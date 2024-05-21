"""
This module initializes the Kubernetes API clients and provides access
to various Kubernetes resources.

"""

from kubernetes import client, config


class KubeApis:
    """
    A class to initialize and provide access to different Kubernetes API clients.
    """

    def __init__(self, kubeconfig_path=None, kubeconf_context=None):
        """
        Initializes the KubeApis class and loads the Kubernetes configuration.

        Args:
            kubeconfig_path (str, optional): The path to the kubeconfig file. Defaults to None.
            kubeconf_context (str, optional): The context to use from the kubeconfig file. Defaults to None.
        """
        self.load_kube_config(kubeconfig_path, kubeconf_context)
        self.api_v1 = client.CoreV1Api()
        self.api_instance = client.AppsV1Api()
        self.api_network = client.NetworkingV1Api()
        self.hpa_api_instance = client.AutoscalingV1Api()

    def load_kube_config(self, kubeconfig_path=None, kubeconf_context=None):
        """
        Load the Kubernetes configuration.

        Args:
            kubeconfig_path (str, optional): The path to the kubeconfig file. Defaults to None.
            kubeconf_context (str, optional): The context to use from the kubeconfig file. Defaults to None.
        """
        config.load_kube_config(config_file=kubeconfig_path, context=kubeconf_context)
