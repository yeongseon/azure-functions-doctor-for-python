import importlib.resources
import json
from collections import defaultdict
from pathlib import Path
from typing import TypedDict

from azure_functions_doctor.handlers import Rule, generic_handler


class CheckResult(TypedDict, total=False):
    label: str
    value: str
    status: str
    hint: str
    hint_url: str


class SectionResult(TypedDict):
    title: str
    category: str
    status: str  # 'pass' or 'fail'
    items: list[CheckResult]


class Doctor:
    """
    Diagnostic runner for Azure Functions apps.
    Loads checks from rules.json and executes them against a target project path.
    """

    def __init__(self, path: str = ".") -> None:
        self.project_path: Path = Path(path).resolve()

    def load_rules(self) -> list[Rule]:
        rules_path = importlib.resources.files("azure_functions_doctor.assets").joinpath("rules.json")
        with rules_path.open(encoding="utf-8") as f:
            rules: list[Rule] = json.load(f)
        return sorted(rules, key=lambda r: r.get("check_order", 999))

    def run_all_checks(self) -> list[SectionResult]:
        rules = self.load_rules()
        grouped: dict[str, list[Rule]] = defaultdict(list)

        for rule in rules:
            grouped[rule["section"]].append(rule)

        results: list[SectionResult] = []

        for section, checks in grouped.items():
            section_result: SectionResult = {
                "title": section.replace("_", " ").title(),
                "category": section,
                "status": "pass",
                "items": [],
            }

            for rule in checks:
                result = generic_handler(rule, self.project_path)

                # If the result is empty, skip this rule
                value_msg = result["detail"]
                if result["status"] != "pass" and not rule.get("required", True):
                    value_msg += " (optional)"

                item: CheckResult = {
                    "label": rule.get("label", rule["id"]),
                    "value": value_msg,
                    "status": result["status"],
                }

                # If the rule is not passing and is required, set section status to fail
                if result["status"] != "pass" and rule.get("required", True):
                    section_result["status"] = "fail"

                if "hint" in rule:
                    item["hint"] = rule["hint"]

                if "hint_url" in rule and rule["hint_url"]:
                    item["hint_url"] = rule["hint_url"]

                section_result["items"].append(item)

            results.append(section_result)

        return results
