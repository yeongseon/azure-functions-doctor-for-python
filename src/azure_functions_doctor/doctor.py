import json
from pathlib import Path
from typing import Any

from .registry import get_checker


class Doctor:
    """
    Diagnostic runner for Azure Functions apps.
    Loads checks from rules.json and executes them against a target project path.
    """

    def __init__(self, path: str = ".") -> None:
        """
        Initialize the Doctor.

        Args:
            path (str): Path to the Azure Functions project directory.
        """
        self.project_path: Path = Path(path).resolve()
        self.rules_path: Path = Path(__file__).parent / "rules.json"

    def run_all_checks(self) -> list[dict[str, Any]]:
        """
        Run all diagnostic checks defined in rules.json.

        Returns:
            list[dict[str, Any]]: List of section results containing individual check results.
        """
        with self.rules_path.open(encoding="utf-8") as f:
            rule_sections: list[dict[str, Any]] = json.load(f)

        results: list[dict[str, Any]] = []

        for section in rule_sections:
            section_result: dict[str, Any] = {
                "title": section["title"],
                "category": section["category"],
                "status": "pass",
                "items": [],
            }

            for check in section["checks"]:
                checker = get_checker(check["type"])
                result = checker(check, str(self.project_path))

                item: dict[str, Any] = {
                    "label": check["name"],
                    "value": result.get("detail", ""),
                    "status": result["status"],
                }

                if result["status"] != "pass":
                    section_result["status"] = "fail"

                if "hint" in check:
                    item["hint"] = check["hint"]

                section_result["items"].append(item)

            results.append(section_result)

        return results
