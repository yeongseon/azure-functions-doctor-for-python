import sys

from azure_functions_doctor.result import DiagnosticResult


def check_python_version() -> DiagnosticResult:
    """
    Check the Python version to ensure it meets the minimum requirement for Azure Functions.
    :return: A DiagnosticResult indicating the status of the Python version.
    """
    version = sys.version_info
    if version >= (3, 9):
        return DiagnosticResult(
            check="Python version",
            result="pass",
            detail=f"{version.major}.{version.minor}.{version.micro}",
            recommendation="None needed.",
            docs_url="https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices?tabs=python",
        )
    else:
        return DiagnosticResult(
            check="Python version",
            result="fail",
            detail=f"{version.major}.{version.minor}.{version.micro} (requires ≥ 3.9)",
            recommendation="Upgrade to Python 3.9 or higher.",
            docs_url="https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices?tabs=python",
        )
