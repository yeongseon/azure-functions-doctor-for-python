from typing import List

from azure_functions_doctor.checks.config_files import check_host_json, check_requirements_txt
from azure_functions_doctor.checks.python_env import check_python_version
from azure_functions_doctor.result import DiagnosticResult


class Doctor:
    def __init__(self, function_app_path: str):
        """
        Initialize the Doctor with the path to the Azure Functions application.
        :param function_app_path: The file system path to the Azure Functions application.
        """
        self.path = function_app_path

    def run_all_checks(self) -> List[DiagnosticResult]:
        return [
            check_python_version(),
            check_host_json(self.path),
            check_requirements_txt(self.path),
        ]

    def display_results(self) -> None:
        results = self.run_all_checks()
        for r in results:
            print(
                "\n".join(
                    [
                        f"🔍 Check        : {r.check}",
                        f"✅ Result       : {r.result.upper()}",
                        f"📋 Detail       : {r.detail}",
                        f"💡 Recommendation: {r.recommendation}",
                        f"📚 Docs         : {r.docs_url}",
                        "",
                    ]
                )
            )
