import json
import os
import sys
from typing import Any, Dict, List


class Doctor:
    """
    A class to perform diagnostics on an Azure Functions application.
    It checks the Python version, host.json configuration, and requirements.txt file.
    """

    def __init__(self, function_app_path: str):
        self.path = function_app_path

    def run_all_checks(self) -> List[Dict[str, Any]]:
        """
        Run all diagnostic checks and return their results.
        :return: A list of dictionaries containing the results of each check.
        """
        return [self.check_python_version(), self.check_host_json(), self.check_requirements_txt()]

    def check_python_version(self) -> Dict[str, Any]:
        """
        Check if the Python version is 3.9 or higher.
        :return: A dictionary with the result of the check.
        """
        version = sys.version_info
        return {
            "check": "Python version",
            "result": "pass" if version >= (3, 9) else "fail",
            "detail": f"{version.major}.{version.minor}.{version.micro}",
        }

    def check_host_json(self) -> Dict[str, Any]:
        """
        Check the host.json file for the correct version.
        :return: A dictionary with the result of the check.
        """
        try:
            with open(os.path.join(self.path, "host.json")) as f:
                config = json.load(f)
            version = config.get("version")
            return {
                "check": "host.json version",
                "result": "pass" if version == "2.0" else "warn",
                "detail": f"version={version}",
            }
        except Exception as e:
            return {"check": "host.json", "result": "fail", "detail": str(e)}

    def check_requirements_txt(self) -> Dict[str, Any]:
        """
        Check if the requirements.txt file exists in the function app path.
        :return: A dictionary with the result of the check.
        """
        exists = os.path.exists(os.path.join(self.path, "requirements.txt"))
        return {
            "check": "requirements.txt",
            "result": "pass" if exists else "fail",
            "detail": "Found" if exists else "Not found",
        }
