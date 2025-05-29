from typing import Any, Dict, List

from azure_functions_doctor.doctor import Doctor


def run_diagnostics(path: str) -> List[Dict[str, Any]]:
    """
    Run diagnostics on the Azure Functions application at the specified path.
    :param path: The file system path to the Azure Functions application.
    :return: A list of dictionaries containing the results of each diagnostic check.
    """
    return Doctor(path).run_all_checks()
