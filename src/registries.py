"""
    Registries credentials
"""
import re

class Registries:
    def __init__(self):
        self.registries = {}
        self.registries_secrets = {}


    def add_anonymous(self,server):
        """
        Add an anonymous registry with no user credentials.
        
        Parameters:
            server (str): The server address of the registry.
        """
        self.registries[server] = {}
        self.registries_secrets[server] = {}
    

    def add_user_credentials(self, server, username, passoword):
        """
        Add user credentials to a registry.

        Parameters:
            server (str): The server address of the registry.
            username (str): The username for the registry.
            password (str): The password for the registry.
        """
        password_secret_ref = f"registry-{server.replace('.', '-')}-password"
        self.registries[server] = {"server": server, "username": username, "passwordSecretRef": password_secret_ref}
        self.registries_secrets[server] = { "name": password_secret_ref , "value": passoword }

    def get_registries_array(self):
        """
        Get an array of registries with user credentials.
        
        Returns:
            list: An array containing dictionaries representing registries with user credentials.
        """        
        # Filter out empty registries
        filtered_registries = {k: v for k, v in self.registries.items() if v}
        # Construct array with desired content
        return [{"server": registry["server"], "username": registry["username"], "passwordSecretRef": registry["passwordSecretRef"]}
                for registry in filtered_registries.values()]    
    
    def get_registries_secrets_array(self):
        """
        Get an array of registry secrets.
        
        Returns:
            list: An array containing dictionaries representing registry secrets.
        """        
        # Filter out empty registries secrets
        filtered_registries_secrets = {k: v for k, v in self.registries_secrets.items() if v}
        # Construct array with desired content
        return [{"name": registries_secret["name"], "value": registries_secret["value"]}
                for registries_secret in filtered_registries_secrets.values()]
    
    def extract_docker_image_elements(self, image_name):
        """
        Extracts elements from a Docker image name.

        Parameters:
            image_name (str): The Docker image name.

        Returns:
            dict or None: A dictionary containing the extracted elements (server, namespace, repository, tag),
                          or None if no match is found.
        """
        # Regex pattern to match the registry, namespace, repository, and tag
        pattern = r'^(?:(?P<server>[^/]+)/)?(?:(?P<namespace>[^/]+)/)?(?P<repository>[^:]+)(?::(?P<tag>.+))?$'
        match = re.match(pattern, image_name)
        
        if match:
            return match.groupdict()
        return None