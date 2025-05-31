import json
from collections import defaultdict
from pathlib import Path
from typing import Any, cast

from azure_functions_doctor.handlers import Rule, generic_handler


class Doctor:
    """
    Diagnostic runner for Azure Functions apps.
    Loads checks from rules.json and executes them against a target project path.
    """

    def __init__(self, path: str = ".") -> None:
        self.project_path: Path = Path(path).resolve()
        self.rules_path: Path = Path(__file__).parent / "rules.json"

    def run_all_checks(self) -> list[dict[str, Any]]:
        """
        Load rules from rules.json, group them by section,
        and run each rule through the generic handler.

        Returns:
            A list of section results with grouped check outcomes.
        """
        with self.rules_path.open(encoding="utf-8") as f:
            rules: list[dict[str, Any]] = json.load(f)

        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for rule in rules:
            grouped[rule["section"]].append(rule)

        results = []

        for section, checks in grouped.items():
            section_result: dict[str, Any] = {
                "title": section.replace("_", " ").title(),
                "category": section,
                "status": "pass",
                "items": [],
            }

            for rule in checks:
                # Cast rule to TypedDict to satisfy mypy
                typed_rule = cast(Rule, rule)
                result = generic_handler(typed_rule, self.project_path)

                item = {
                    "label": typed_rule.get("label", typed_rule["id"]),
                    "value": result["detail"],
                    "status": result["status"],
                }

                if result["status"] != "pass":
                    section_result["status"] = "fail"

                if "hint" in typed_rule:
                    item["hint"] = typed_rule["hint"]

                section_result["items"].append(item)

            results.append(section_result)

        return results
