"""
This script transforms Kubernetes deployments into Azure Container Apps (ACA) configurations.

It uses the Kubernetes API to retrieve deployment details and convert them into the necessary
format for ACA, outputting the result in YAML, JSON, or Terraform formats.

"""

import os
import argparse

from src import transformer_tf
from src.kube_init import KubeApis
from src.kubernetes_utils import get_deployments
from src.utils import (
    write_to_az_scripts_file,
    write_to_json_file,
    write_to_terraform_file,
    write_to_yaml_file,
)
from src.yaml_transformer import YamlTransformer



def main():
    """
    Main function to transform Kubernetes deployment to ACA deployment.

    Parses command line arguments, retrieves the Kubernetes deployment(s), transforms them
    to ACA configurations, and writes the output to the specified format and path.
    """
    parser = argparse.ArgumentParser(
        description="Transform Kubernetes deployment to ACA deployment"
    )
    parser.add_argument("--kubeconfig", type=str, help="Path to the kubeconfig file")
    parser.add_argument(
        "--context", type=str, required=False, help="kubeconfig context"
    )
    parser.add_argument(
        "--namespace",
        type=str,
        required=True,
        help="Namespace name",
    )
    parser.add_argument(
        "--deployment", type=str, required=False, help="Deployment name"
    )
    parser.add_argument(
        "--aca_resource_group",
        type=str,
        required=False,
        help="Container App Resource Group",
    )
    parser.add_argument(
        "--aca_environment", type=str, required=False, help="Container App environment"
    )
    parser.add_argument(
        "--output",
        type=str,
        required=False,
        default="yaml",
        help="Output file for ACA configuration",
    )
    parser.add_argument(
        "--outputpath",
        type=str,
        required=False,
        default=os.getcwd(),
        help="Output file for ACA configuration",
    )
   
    args = parser.parse_args()

    kube_apis = KubeApis(kubeconfig_path=args.kubeconfig, kubeconf_context=args.context)

    try:

        yaml_transformer = YamlTransformer()
         
        deployments = []
        if args.deployment:
            deployments.append(
                kube_apis.api_instance.read_namespaced_deployment(
                    name=args.deployment, namespace=args.namespace
                )
            )
        else:
            deployments = get_deployments(kube_apis, args.namespace)

        filename = os.path.join(args.outputpath, "yaml", "deployment.sh")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as file:
            file.write("#!/bin/bash\n")

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        for deployment in deployments:
            aca_config = yaml_transformer.transform(kube_apis, deployment)
            if args.output == "yaml":
                write_to_yaml_file(
                    args.outputpath, deployment.metadata.name, aca_config
                )
                write_to_az_scripts_file(
                    args.outputpath,
                    deployment.metadata.name,
                    args.aca_resource_group,
                    args.aca_environment,
                )

            if args.output == "terraform":
                tf = transformer_tf.transform(deployment.metadata.name, aca_config)
                write_to_terraform_file(args.outputpath, deployment.metadata.name, tf)
            if args.output == "json":
                write_to_json_file(
                    args.outputpath, deployment.metadata.name, aca_config
                )

        print(f"ACA configuration has been written to {args.output}")

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
