"""
    Transform a Kubernetes deployment to an Azure Container Apps (ACA) Terraform Script.
"""
import json

def transform(name, yaml_data):
    """
    Transform ACA configuration to Terraform configuration.

    Args:
        name (str): Name of the ACA resource.
        yaml_data (dict): ACA configuration in YAML format.

    Returns:
        str: Terraform configuration.
    """
    terraform_code = ""
    # Map to Terraform Container App resource
    terraform_code += f'resource "azurerm_container_app" "{name}" {{\n'
    terraform_code += f'  name                         = "{name}"\n'
    terraform_code += '  container_app_environment_id = ""\n'
    terraform_code += '  resource_group_name          = ""\n'
    terraform_code += '  revision_mode                = "Single"\n\n'
    terraform_code += "  template {{\n\n"
    template = yaml_data.get("properties").get("template")

    terraform_code += (
        f'    max_replicas      = "{template.get("scale").get("maxReplicas", 1)}"\n'
    )
    terraform_code += (
        f'    min_replicas      = "{template.get("scale").get("mainReplicas", 0)}"\n'
    )
    terraform_code += "\n"

    for container in template.get("containers"):
        terraform_code += "    container {{\n"
        terraform_code += f'        name      = "{container.get("name")}"\n'
        terraform_code += f'        image     = "{container.get("image")}"\n'
        terraform_code += (
            f'        memory    = "{container.get("resources").get("memory")}"\n'
        )
        terraform_code += (
            f'        cpu       = "{container.get("resources").get("cpu")}"\n'
        )

        if container.get("command"):
            command_fmt = f'        command   = {container.get("command")}\n'
            terraform_code += command_fmt.replace("'", '"')

        terraform_code += "\n"

        for env in container.get("env"):
            terraform_code += "env {{\n"
            for key, value in env.items():
                terraform_code += f'    { key if key != "secretRef" else "secret_name" }       = "{value}"\n'
            terraform_code += "}}\n"

        readiness_probes = container.get("probes", [])
        for readiness_probe in readiness_probes:
            terraform_code += "\n"
            terraform_code += "        readiness_probe {{\n"
            terraform_code += (
                f'            path   = "{readiness_probe.get("httpGet").get("path")}"\n'
            )
            terraform_code += (
                f'            port   = "{readiness_probe.get("httpGet").get("port")}"\n'
            )
            terraform_code += (
                f'            timeout   = "{readiness_probe.get("periodSeconds")}"\n'
            )
            terraform_code += f'            transport   = "{readiness_probe.get("httpGet").get("schema")}"\n'
            terraform_code += f'            failure_count_threshold   = "{readiness_probe.get("failureThreshold")}"\n'
            terraform_code += "         }\n"
        terraform_code += "     }\n"
    terraform_code += "   }\n\n"

    if yaml_data.get("properties").get("template").get("secrets"):

        for secret in yaml_data.get("properties").get("template").get("secrets"):
            terraform_code += "   secret {\n"
            terraform_code += f'    name    = "{secret.get("name")}"\n'
            terraform_code += f'    value   = {json.dumps(secret.get("value"))}\n'
            terraform_code += " }\n"

    ingress = yaml_data.get("properties").get("configuration").get("ingress")
    if ingress:
        terraform_code += f"  ingress {{\n"
        terraform_code += f'    external_enabled = "{ingress.get("external")}"\n'
        terraform_code += f'    target_port = "{ingress.get("targetPort")}"\n'
        for traffic in ingress.get("traffic"):
            terraform_code += f"    traffic_weight {{\n"
            terraform_code += f'        percentage = "{traffic.get("weight")}"\n'
            terraform_code += (
                f'        latest_revision = "{traffic.get("latestRevision")}"\n'
            )
            terraform_code += "    }\n"
        terraform_code += "   }\n"

    terraform_code += "}\n\n"
    return terraform_code
