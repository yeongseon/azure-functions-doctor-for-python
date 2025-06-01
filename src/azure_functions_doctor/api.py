from typing import List

from azure_functions_doctor.doctor import Doctor, SectionResult


def run_diagnostics(path: str) -> List[SectionResult]:
    """
    Run diagnostics on the Azure Functions application at the specified path.

    Args:
        path: The file system path to the Azure Functions application.

    Returns:
        A list of SectionResult containing the results of each diagnostic check.
    """
    return Doctor(path).run_all_checks()
