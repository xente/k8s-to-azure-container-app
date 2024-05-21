
"""
This module provides functions to extract information from a Kubernetes cluster
and generate the necessary configurations for migrating to Azure Container Apps.
"""
import base64
from .kubernetes_utils import (
    read_horizontal_pod_autoscaler_for_deployment,
    read_ingress_for_service,
    read_service,
)
from .utils import (
    transform_string,
    parse_memory_string
)


def extract_scale(kube_apis, deployment):
    """
    Extracts the scale (min and max replicas) of a deployment.

    Args:
        kube_apis: Kubernetes API instances.
        deployment: The Kubernetes deployment object.

    Returns:
        dict: A dictionary containing the min and max replicas.
    """
    k8_min_replicas = deployment.spec.replicas
    k8_max_replicas = deployment.spec.replicas

    hpa = read_horizontal_pod_autoscaler_for_deployment(
        kube_apis, deployment.metadata.name, deployment.metadata.namespace
    )
    if hpa:
        k8_min_replicas = hpa.spec.min_replicas
        k8_max_replicas = hpa.spec.max_replicas

    return {"minReplicas": k8_min_replicas, "maxReplicas": k8_max_replicas}


def extract_resources(container):
    """
    Extracts the resources (CPU and memory) of a container.

    Args:
        container: The Kubernetes container object.

    Returns:
        dict: A dictionary containing the CPU and memory resources.
    """
    
    k8_memory_limit = "0.5Gi"
    k8_memory_request = "0.5Gi"
    k8_cpu_limit = "0.25"
    k8_cpu_request = "0.25"

    if container.resources and container.resources.limits:
        k8_memory_limit = container.resources.limits.get("memory", "0.25Gi")
        k8_cpu_limit = container.resources.limits.get("cpu", "0.25")

    if container.resources and container.resources.requests:
        k8_memory_request = container.resources.requests.get("memory", "0.25Gi")
        k8_cpu_request = container.resources.requests.get("cpu", "0.25")

    aca_container_memory_bytes = max(
        parse_memory_string(k8_memory_limit), parse_memory_string(k8_memory_request)
    )
    aca_container_memory = get_aca_memory_from_k8_memory(aca_container_memory_bytes)
    aca_container_cpu = get_cpu_for_memory(aca_container_memory)

    aca_resources = {"cpu": aca_container_cpu, "memory": aca_container_memory}
    return aca_resources


def extract_readiness_probes(container):
    """
    Extracts readiness probes from a container.

    Args:
        container: The Kubernetes container object.

    Returns:
        list: A list of readiness probe dictionaries.
    """
    k8_readiness_probe = container.readiness_probe
    aca_readiness_probes = []

    if k8_readiness_probe and k8_readiness_probe.http_get:
        aca_readiness_probe = {
            "type": "Readiness",
            "httpGet": {
                "host": k8_readiness_probe.http_get.host,
                "path": k8_readiness_probe.http_get.path,
                "port": find_container_port(
                    container.ports, k8_readiness_probe.http_get.port
                ),
                "httpHeaders": k8_readiness_probe.http_get.http_headers,
                "schema": k8_readiness_probe.http_get.scheme,
            },
            "tcpSocket": k8_readiness_probe.tcp_socket,
            "periodSeconds": k8_readiness_probe.period_seconds,
            "initialDelaySeconds": k8_readiness_probe.initial_delay_seconds,
            "failureThreshold": k8_readiness_probe.failure_threshold,
        }
        aca_readiness_probes.append(aca_readiness_probe)

    return aca_readiness_probes


def find_container_port(ports, port_name):
    """
    Finds a container port by its name.

    Args:
        ports: A list of container ports.
        port_name: The name of the port to find.

    Returns:
        int or None: The container port number or None if not found.
    """
    for port in ports:
        if port.name == port_name:
            return port.container_port
        if port.container_port == port_name:
            return port.container_port
    return None


def extract_volumes(kube_apis, deployment):
    """
    Extracts volumes from a deployment.

    Args:
        kube_apis: Kubernetes API instances.
        deployment: The Kubernetes deployment object.

    Returns:
        dict: A dictionary containing volumes and secrets.
    """
    secrets = []
    volumes = []

    k8_volumes = deployment.spec.template.spec.volumes
    if k8_volumes:
        for volume in k8_volumes:
            if volume.secret:
                k8_secret = kube_apis.api_v1.read_namespaced_secret(
                    volume.secret.secret_name, deployment.metadata.namespace
                )
                aca_volumes = {"name": volume.name, "storageType": "Secret"}
                if k8_secret and k8_secret.data:
                    aca_volumes_secrets = []
                    for key, value in k8_secret.data.items():
                        aca_volumes_secret = {
                            "secretRef": transform_string(key),
                            "path": key,
                        }
                        aca_volumes_secrets.append(aca_volumes_secret)

                        aca_secrets = {
                            "name": transform_string(key),
                            "value": base64.b64decode(value).decode("utf-8"),
                        }
                        secrets.append(aca_secrets)
                    aca_volumes["secrets"] = aca_volumes_secrets
            volumes.append(aca_volumes)

    return {"volumes": volumes, "secrets": secrets}

def extract_mounts(container):
    """
    Extracts volume mounts from a Kubernetes container and converts them into ACA format.

    Args:
        container: Kubernetes container object.

    Returns:
        list: List of volume mounts in ACA format, containing dictionaries with 'mountPath' and 'volumeName'.
    """
    aca_mounts = []
    k8_mounts = container.volume_mounts
    if k8_mounts:
        for k8_mount in k8_mounts:
            aca_mount = {
                "mountPath" : k8_mount.mount_path,
                "volumeName": k8_mount.name
            }
            aca_mounts.append(aca_mount)
        
    return aca_mounts

def extract_ingress(kube_apis, deployment):
    """
    Extracts ingress information from a deployment.

    Args:
        kube_apis: Kubernetes API instances.
        deployment: The Kubernetes deployment object.

    Returns:
        dict: A dictionary containing ingress information.
    """
    service = read_service(
        kube_apis, deployment.metadata.name, deployment.metadata.namespace
    )
    aca_ingress = None
    if service:
        aca_ingress = {
            "external": False,
            "allowInsecure": False,
            "targetPort": service.spec.ports[0].target_port,
            "traffic": [{"weight": 100, "latestRevision": True}],
        }

        ingress = read_ingress_for_service(
            kube_apis, service.metadata.name, deployment.metadata.namespace
        )
        if ingress:
            for tls in ingress.spec.tls:
                print(f"CUSTOM_DOMAIN: required for {tls.hosts}")
            for rule in ingress.spec.rules:
                for path in rule.http.paths:
                    if (
                        path.backend.service.name == service.metadata.name
                        and path.backend.service.port.number
                        == service.spec.ports[0].port
                    ):
                        aca_ingress["external"] = True
    return aca_ingress


def extract_envs(container):
    """
    Extracts environment variables from a container.

    Args:
        container: The Kubernetes container object.

    Returns:
        list: A list of environment variable dictionaries.
    """

    k8_envs = container.env
    aca_envs = []
    if k8_envs:
        for k8_env in k8_envs:
            aca_env = {"name": k8_env.name, "value": k8_env.value}
            aca_envs.append(aca_env)
    return aca_envs


def extract_env_from(kube_apis, container, namespace):
    """
    Extracts environment variables from secrets.

    Args:
        kube_apis: Kubernetes API instances.
        container: The Kubernetes container object.
        namespace: The namespace of the container.

    Returns:
        list: A list of secret environment variable dictionaries.
    """
    k8_envs_from = container.env_from
    aca_secrets = []
    if k8_envs_from:
        for env_from in k8_envs_from:
            k8_secret_name = env_from.secret_ref.name
            k8_secret = kube_apis.api_v1.read_namespaced_secret(
                k8_secret_name, namespace
            )
            if k8_secret and k8_secret.data:
                for key, value in k8_secret.data.items():
                    aca_secret = {
                        "name": key,
                        "value": base64.b64decode(value).decode("utf-8"),
                    }
                    aca_secrets.append(aca_secret)
    return aca_secrets


def extract_secrets_ref_from_env_from(secrests):
    """
    Extracts secret references from environment variables.

    Args:
        secrests: A list of secrets.

    Returns:
        list: A list of secret reference dictionaries.
    """
    aca_env_secrets_ref = []
    if secrests:
        for secret in secrests:
            aca_env_secret_ref = {
                "name": secret["name"],
                "secretRef": transform_string(secret["name"]),
            }
            aca_env_secrets_ref.append(aca_env_secret_ref)

    return aca_env_secrets_ref


def normalize_secrets(secrets):
    for secret in secrets:
        secret['name'] = transform_string(secret['name'])
    
    return secrets

memory_mapping = {
    "0.5Gi": 512 * 1024 * 1024,
    "1.0Gi": 1024 * 1024 * 1024,
    "1.5Gi": 1.5 * 1024 * 1024 * 1024,
    "2.0Gi": 2 * 1024 * 1024 * 1024,
    "2.5Gi": 2.5 * 1024 * 1024 * 1024,
    "3.0Gi": 3 * 1024 * 1024 * 1024,
    "3.5Gi": 3.5 * 1024 * 1024 * 1024,
    "4.0Gi": 4 * 1024 * 1024 * 1024,
}


def get_aca_memory_from_k8_memory(k8_memory):
    closest_match = None
    for aca_memory, k8_memory_bytes in memory_mapping.items():
        if k8_memory_bytes >= k8_memory:
            closest_match = aca_memory
            break
    return closest_match


def get_cpu_for_memory(memory):
    memory_to_cpu_map = {
        "0.5Gi": 0.25,
        "1.0Gi": 0.5,
        "1.5Gi": 0.75,
        "2.0Gi": 1.0,
        "2.5Gi": 1.25,
        "3.0Gi": 1.5,
        "3.5Gi": 1.75,
        "4.0Gi": 2.0,
    }
    return memory_to_cpu_map.get(memory, 0.25)
