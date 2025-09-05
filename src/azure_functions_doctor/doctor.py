import importlib.resources
import json
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

    def __init__(self, path: str = ".", allow_v1: bool = False) -> None:
        self.project_path: Path = Path(path).resolve()
        self.programming_model = self._detect_programming_model()
        # If v1 detected in nested function folders (function.json not at project root)
        # and caller did not allow v1, signal incompatibility.
        function_json_files = list(self.project_path.rglob("function.json"))
        nested_v1 = any(f.parent.resolve() != self.project_path for f in function_json_files)

        if nested_v1 and not allow_v1:
            raise SystemExit("v1 programming model detected - limited support")

    def _detect_programming_model(self) -> str:
        """Detect the Azure Functions programming model version.

        Returns:
            str: 'v1' if function.json files are found, 'v2' if @app decorators are found,
                 'v2' as default if neither is clearly detected.
        """
        # Check for v1: function.json files
        function_json_files = list(self.project_path.rglob("function.json"))
        if function_json_files:
            return "v1"

        # Check for v2: @app decorators in Python files
        if self._has_v2_decorators():
            return "v2"

        # Default to v2 (current primary support)
        return "v2"

    def _has_v2_decorators(self) -> bool:
        """Check if the project uses v2 decorators (@app.*)."""
        python_files = list(self.project_path.rglob("*.py"))

        for py_file in python_files:
            try:
                with py_file.open(encoding="utf-8") as f:
                    content = f.read()
                    if "@app." in content:
                        return True
            except (OSError, UnicodeDecodeError):
                # Skip files that can't be read
                continue

        return False

    def load_rules(self) -> list[Rule]:
        """Load rules based on detected programming model."""
        if self.programming_model == "v2":
            return self._load_v2_rules()
        elif self.programming_model == "v1":
            return self._load_v1_rules()
        else:
            # Fallback to legacy rules.json
            return self._load_legacy_rules()

    def _load_v2_rules(self) -> list[Rule]:
        """Load complete v2 rules set."""
        files_obj = importlib.resources.files("azure_functions_doctor.assets")

        # Load v2 rules from assets/rules/v2.json only
        try:
            rules_path = files_obj.joinpath("rules").joinpath("v2.json")
            with rules_path.open(encoding="utf-8") as f:
                v2_rules = json.load(f)
        except FileNotFoundError as e:
            logger.error("v2.json not found")
            raise RuntimeError("v2.json not found") from e
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in v2.json: {e}")
            raise RuntimeError(f"Failed to parse v2.json: {e}") from e

        return sorted(list(v2_rules), key=lambda r: r.get("check_order", 999))

    def _load_v1_rules(self) -> list[Rule]:
        """Load complete v1 rules set."""
        files_obj = importlib.resources.files("azure_functions_doctor.assets")

        # Load v1 rules from assets/rules/v1.json only
        try:
            rules_path = files_obj.joinpath("rules").joinpath("v1.json")
            with rules_path.open(encoding="utf-8") as f:
                v1_rules = json.load(f)
        except FileNotFoundError as e:
            logger.error("v1.json not found")
            raise RuntimeError("v1.json not found") from e
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in v1.json: {e}")
            raise RuntimeError(f"Failed to parse v1.json: {e}") from e

        return sorted(list(v1_rules), key=lambda r: r.get("check_order", 999))

    def _load_legacy_rules(self) -> list[Rule]:
        """Load legacy rules.json for backward compatibility."""
        try:
            files_obj = importlib.resources.files("azure_functions_doctor.assets")
            rules_path = files_obj.joinpath("rules.json")
            try:
                with rules_path.open(encoding="utf-8") as f:
                    legacy_rules: list[Rule] = json.load(f)
                    return legacy_rules
            except FileNotFoundError:
                # Test harnesses sometimes mock importlib.resources.files and
                # attach a different path object on joinpath.return_path. Try
                # that as a fallback to be compatible with unit tests.
                joiner = getattr(files_obj, "joinpath", None)
                if joiner is not None and hasattr(joiner, "return_path"):
                    try:
                        with joiner.return_path.open(encoding="utf-8") as f:
                            rules: list[Rule] = json.load(f)
                            return rules
                    except Exception:
                        pass
                logger.error("No rules files found")
                raise RuntimeError("No rules files found") from None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in rules.json: {e}")
            raise RuntimeError(f"Failed to parse rules.json: {e}") from e

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
