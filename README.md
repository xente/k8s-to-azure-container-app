# K8sToAzureContainerApp

**Overview**

K8sToAca is a Python tool designed to streamline the process of transitioning Kubernetes namespaces into Azure Container App environments. Leveraging the Kubernetes API, this tool retrieves all deployment objects within the specified namespace and generates Azure Container Apps deployment in YAMLs, JSON or Terraform(in Beta). Additionally, it provides a shell script containing commands necessary for deploying the generated deployment files using the Azure CLI.


## Parameters

| Parameter | Mandatory | Description |
|-|-|-|
| `namespace`           | True      | The Kubernetes namespace to be migrated.                 |
| `context`             | True      | The name of the Kubernetes config context for the cluster. |
| `aca_resource_group`  | True      | The Azure Resource Group where the Container App Environment exists. |
| `aca_environment`     | True      | The name of the Azure Container App Environment.         |
| `output`              | False     | Output format values (yaml, json, terraform). Terraform output is in preview. Default value: yaml |
| `outputpath`          | False     | Output folder. Default value: current path               |



## Features
K8sToAzureContainerApp can generate deployment scripts in YAML format from a specified Kubernetes namespace. Currently, it supports migrating the following objects:

- **POD**:
  - Deployment
  - Pod
  - Horizontal Pod Autoscaler
- **Configuration**:
  - Secrets
- **Storage**:
  - Volumes
- **Network/Exposure**:
  - Ingress
  - Service
  - Endpoint

## Installation
You can install K8sToAca using pip:

1. **pip install**: Run the following command:
    ```bash
    pip3 install k8s-to-azure-container-app
    ```

1. **Generate a package**:
    
    Alternatively, you can download the source code and follow these steps for a manual installation:
   
    ```bash
    pip install -e .
    ```

## Usage

Run K8sToAca using the following command:

```bash
K8sToAca --namespace my_name_space --context cluster_context --aca_resource_group target_resource_group --aca_environment target_container_app_environment_name
```
Replace the placeholders with your actual values.

Deploy to Azure deployment script:

```cmd
./deployment.sh 
```

## Recomendation

Install Azure CLI using https://learn.microsoft.com/en-us/cli/azure/install-azure-cli

Ensure your Azure CLI and the Azure Container Apps extension are up to date by executing the following commands:

```bash
az upgrade
az extension add -n containerapp --upgrade
```

## License
This tool is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
