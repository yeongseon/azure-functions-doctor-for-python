import json
import os

from azure_functions_doctor.result import DiagnosticResult


def check_host_json(path: str) -> DiagnosticResult:
    """
    Check the host.json file for version compatibility.
    :param path: The file system path to the Azure Functions application.
    :return: A DiagnosticResult indicating the status of the host.json file.
    """
    try:
        with open(os.path.join(path, "host.json")) as f:
            config = json.load(f)
        version = config.get("version")
        if version == "2.0":
            return DiagnosticResult(
                check="host.json version",
                result="pass",
                detail=f"version={version}",
                recommendation="None needed.",
                docs_url="https://learn.microsoft.com/en-us/azure/azure-functions/functions-host-json",
            )
        else:
            return DiagnosticResult(
                check="host.json version",
                result="warn",
                detail=f"version={version}",
                recommendation="Use version: '2.0' for best compatibility.",
                docs_url="https://learn.microsoft.com/en-us/azure/azure-functions/functions-host-json",
            )
    except Exception as e:
        return DiagnosticResult(
            check="host.json",
            result="fail",
            detail=str(e),
            recommendation="Ensure host.json is present and correctly formatted.",
            docs_url="https://learn.microsoft.com/en-us/azure/azure-functions/functions-host-json",
        )


def check_requirements_txt(path: str) -> DiagnosticResult:
    """
    Check for the presence of requirements.txt to declare dependencies.
    :param path: The file system path to the Azure Functions application.
    :return: A DiagnosticResult indicating the status of the requirements.txt file.
    """
    req_path = os.path.join(path, "requirements.txt")
    if os.path.exists(req_path):
        return DiagnosticResult(
            check="requirements.txt",
            result="pass",
            detail="Found",
            recommendation="None needed.",
            docs_url="https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python#python-version",
        )
    else:
        return DiagnosticResult(
            check="requirements.txt",
            result="fail",
            detail="Not found",
            recommendation="Add a requirements.txt to declare dependencies.",
            docs_url="https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python#python-version",
        )
