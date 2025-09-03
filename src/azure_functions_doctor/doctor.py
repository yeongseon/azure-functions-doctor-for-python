import importlib.resources
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import TypedDict

from azure_functions_doctor.handlers import Rule, generic_handler
from azure_functions_doctor.logging_config import get_logger, log_rule_execution

logger = get_logger(__name__)


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
        self._check_compatibility()

    def _check_compatibility(self) -> None:
        """Check if the project is compatible with this tool (currently v2 only)."""
        # Check for v1 function.json files
        function_json_files = list(self.project_path.rglob("function.json"))
        if function_json_files:
            print("❌ Incompatible project detected!")
            print("This tool currently supports Azure Functions Python Programming Model v2 only.")
            print("Your project appears to use v1 (function.json based).")
            print("\nTo use this tool:")
            print("1. Migrate your project to v2 using decorators (@app.route, @app.schedule, etc.)")
            print("2. Or use a different diagnostic tool that supports v1")
            print("\nLearn more: https://learn.microsoft.com/azure/azure-functions/functions-python-develop-v2")
            sys.exit(1)

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
                # Time rule execution for logging
                rule_start = time.time()
                result = generic_handler(rule, self.project_path)
                rule_duration_ms = (time.time() - rule_start) * 1000

                # Log rule execution
                log_rule_execution(rule["id"], rule["type"], result["status"], rule_duration_ms)

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
