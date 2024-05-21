"""
    Transform a Kubernetes deployment to an Azure Container Apps (ACA) deployment.
"""
from src.registries import Registries
from .extractor import (
    extract_mounts,
    extract_scale,
    extract_resources,
    extract_readiness_probes,
    extract_secrets_ref_from_env_from,
    extract_volumes,
    extract_ingress,
    extract_envs,
    extract_env_from,
    normalize_secrets,
)

class YamlTransformer:
    def __init__(self):
        self.registries = Registries()

    def transform(self, kube_apis, deployment):
        """
        Transform a Kubernetes deployment to an Azure Container Apps (ACA) deployment.

        Args:
            kube_apis: KubeApis object for interacting with the Kubernetes API.
            deployment: Kubernetes deployment object.

        Returns:
            dict: ACA configuration based on the Kubernetes deployment.
        """

        deployment_namespace = deployment.metadata.namespace
        volumes = extract_volumes(kube_apis, deployment)

        containers = []
        secrets = []

        for container in deployment.spec.template.spec.containers:

            secrets = extract_env_from(kube_apis, container, deployment_namespace)

            aca_container = {
                "image": container.image,
                "name": container.name,
                "resources": extract_resources(container),
                "command": container.command,
                "probes": extract_readiness_probes(container),
                "env": extract_envs(container) + extract_secrets_ref_from_env_from(secrets),
                "volumeMounts": extract_mounts(container)
            }
            registry= self.registries.extract_docker_image_elements(container.image)
            
            registry_exists = False
            if  registry.get('server') in self.registries.registries:
              registry_exists = True
            
            if not registry_exists:
                has_registry_credentials = input(f"This registry  {registry.get('server')} reqquired credentials [Y/N]: ") or "N"

                if has_registry_credentials.upper() == "Y":
                    registry_username = input(f"Registry username for {registry.get('server')}: ")
                    registry_passoword = input(f"Registry password for {registry.get('server')}: ")
                    
                    self.registries.add_user_credentials(registry.get('server'),registry_username, registry_passoword)
                else:
                    self.registries.add_anonymous(registry.get('server'))
            containers.append(aca_container)
    

        aca_config = {
            "properties": {
                "configuration": {
                    "registries": self.registries.get_registries_array(),
                    "ingress": extract_ingress(kube_apis, deployment),
                    "secrets": self.registries.get_registries_secrets_array()  + normalize_secrets(secrets) + volumes["secrets"]
                },
                "template": {
                    "containers": containers,
                    "scale": extract_scale(kube_apis, deployment),
                    "volumes": volumes["volumes"],
                },
            }
        }

        return aca_config