"""
This module provides functions to interact with a Kubernetes cluster and extract
necessary configurations for migrating to Azure Container Apps.
"""

from kubernetes.client.rest import ApiException


def get_deployments(kube_apis, namespace):
    """
    Retrieves deployments from a namespace.

    Args:
        kube_apis: Kubernetes API instances.
        namespace: The Kubernetes namespace to list deployments from.

    Returns:
        list: A list of deployment objects or an empty list if an error occurs.
    """
    try:
        # List deployments in the namespace
        api_response = kube_apis.api_instance.list_namespaced_deployment(
            namespace=namespace
        )
        return api_response.items
    except ApiException as e:
        print(f"Error fetching deployments: {e}")
        return []


def parse_kubernetes_objects_from_deployments(kube_apis, deployments):
    """
    Parses Kubernetes objects from deployment YAMLs.

    Args:
        kube_apis: Kubernetes API instances.
        deployments: A list of deployment objects.

    Returns:
        list: A list of deployment YAML objects.
    """
    # Parse Kubernetes objects from deployment YAMLs
    kubernetes_objects = []
    for deployment in deployments:
        namespace = deployment.metadata.namespace
        deployment_name = deployment.metadata.name
        deployment_yaml = kube_apis.api_instance.read_namespaced_deployment(
            deployment_name, namespace
        )
        kubernetes_objects.append(deployment_yaml)
    return kubernetes_objects


def read_horizontal_pod_autoscaler_for_deployment(
    kube_apis, deployment_name, namespace="default"
):
    """
    Reads the HPA for a given deployment.

    Args:
        kube_apis: Kubernetes API instances.
        deployment_name: The name of the deployment.
        namespace: The namespace of the deployment.

    Returns:
        object: The HPA object or None if not found or an error occurs.
    """
    try:
        hpa = kube_apis.hpa_api_instance.read_namespaced_horizontal_pod_autoscaler(
            deployment_name, namespace
        )
        return hpa
    except ApiException as e:
        if e.status == 404:
            return None
        else:
            print(
                f"Exception when calling AutoscalingV1Api->read_namespaced_horizontal_pod_autoscaler: {e}"
            )
            return None


def read_ingress_for_service(kube_apis, service_name, namespace="default"):
    """
    Reads the ingress for a given service.

    Args:
        kube_apis: Kubernetes API instances.
        service_name: The name of the service.
        namespace: The namespace of the service.

    Returns:
        object: The ingress object or None if not found or an error occurs.
    """
    try:
        ingress = kube_apis.api_network.read_namespaced_ingress(service_name, namespace)
        return ingress
    except ApiException as e:
        if e.status == 404:
            return None
        else:
            print(
                f"Exception when calling NetworkingV1Api->read_namespaced_ingress: {e}"
            )
            return None


def read_service(kube_apis, service_name, namespace="default"):
    """
    Reads a service by name.

    Args:
        kube_apis: Kubernetes API instances.
        service_name: The name of the service.
        namespace: The namespace of the service.

    Returns:
        object: The service object or None if not found or an error occurs.
    """
    try:
        service = kube_apis.api_v1.read_namespaced_service(service_name, namespace)
        return service
    except ApiException as e:
        if e.status == 404:
            return None
        else:
            print(f"Exception when calling CoreV1Api->read_namespaced_service: {e}")
            return None
