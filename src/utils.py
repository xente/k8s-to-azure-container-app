import os
import re
import json
import yaml


def transform_string(input_string):
    """
    Transform string to lower case, replace invalid characters, and ensure valid Kubernetes naming.

    Args:
        input_string (str): The input string to transform.

    Returns:
        str: The transformed string.
    """
    result = input_string.lower()
    result = re.sub(r"[^a-z0-9-]", "-", result)
    result = re.sub(r"^[^a-z0-9]+", "", result)
    result = re.sub(r"[^a-z0-9]+$", "", result)
    return result


def write_to_az_scripts_file(
    file_path, deployment, resource_group, container_environment
):
    """
    Write an Azure CLI script to a shell (.sh) file for creating a container app.

    Args:
        file_path (str): The directory path to save the file.
        deployment (str): The name of the deployment.
        resource_group (str): The resource group name.
        container_environment (str): The container environment name.
    """
    filename = os.path.join(file_path, "yaml", "deployment.sh")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "a", encoding="utf-8") as file:
        file.write(
            f"az containerapp create -n {deployment} -g  {resource_group} --environment {container_environment} --yaml {deployment}.yaml\n"
        )


def write_to_yaml_file(file_path, file_name, content):
    """
    Write content to a YAML file.

    Args:
        file_path (str): The directory path to save the file.
        file_name (str): The name of the YAML file.
        content (dict): The content to write to the YAML file.
    """
    filename = os.path.join(file_path, "yaml", f"{file_name}.yaml")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as file:
        yaml.dump(content, file, sort_keys=False)


def write_to_json_file(file_path, file_name, content):
    """
    Write content to a JSON file.

    Args:
        file_path (str): The directory path to save the file.
        file_name (str): The name of the JSON file.
        content (dict): The content to write to the JSON file.
    """
    filename = os.path.join(file_path, "json", f"{file_name}.json")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(content, file, sort_keys=True)


def write_to_terraform_file(file_path, file_name, content):
    """
    Write content to a Terraform (.tf) file.

    Args:
        file_path (str): The directory path to save the file.
        file_name (str): The name of the Terraform file.
        content (str): The content to write to the Terraform file.
    """
    filename = os.path.join(file_path, "tf", f"{file_name}.tf")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)


def parse_memory_string(memory_str):
    """
    Parse a Kubernetes memory string and convert it to bytes.

    Args:
        memory_str (str): The Kubernetes memory string.

    Returns:
        float: The memory value in bytes.

    Raises:
        ValueError: If the memory string format is invalid or contains an unknown suffix.
    """
    memory_str = memory_str.strip()
    patterns = {
        "E": 1e18,
        "P": 1e15,
        "T": 1e12,
        "G": 1e9,
        "M": 1e6,
        "k": 1e3,
        "Ei": 2**60,
        "Pi": 2**50,
        "Ti": 2**40,
        "Gi": 2**30,
        "Mi": 2**20,
        "Ki": 2**10,
        "": 1,
        "m": 1e-3,
    }
    match = re.match(r"(\d+(?:\.\d+)?)([a-zA-Z]*)", memory_str)
    if not match:
        raise ValueError("Invalid memory format")
    value, suffix = match.groups()
    value = float(value)
    if suffix not in patterns:
        raise ValueError(f"Unknown memory suffix '{suffix}'")
    bytes_value = value * patterns[suffix]
    return bytes_value


def convert_to_bytes(memory_str):
    """
    Convert a Kubernetes memory string to bytes.

    Args:
        memory_str (str): The Kubernetes memory string.

    Returns:
        int: The memory value in bytes.
    """
    memory_str = memory_str.lower()
    if memory_str.endswith("ki"):
        return float(memory_str[:-2]) * 1024
    elif memory_str.endswith("mi"):
        return float(memory_str[:-2]) * 1024 * 1024
    elif memory_str.endswith("gi"):
        return float(memory_str[:-2]) * 1024 * 1024 * 1024
    else:
        return int(memory_str)


def transform_bytes_to_gigabytes(memory_bytes):
    """
    Transform bytes to a string representation in GiB, rounded to the nearest 0.5.

    Args:
        memory_bytes (int): The memory value in bytes.

    Returns:
        str: The memory value in GiB as a string.
    """
    gigabytes = memory_bytes / (1024 * 1024 * 1024)
    rounded_gigabytes = round(gigabytes * 2) / 2
    if rounded_gigabytes == 0:
        return "0.25Gi"
    else:
        return f"{rounded_gigabytes}Gi"
