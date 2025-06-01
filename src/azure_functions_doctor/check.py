from pathlib import Path
from typing import Any, TypedDict, cast

from azure_functions_doctor.handlers import Rule, generic_handler


class CheckResult(TypedDict, total=False):
    status: str
    label: str
    value: str
    hint: str


def run_check(rule: dict[str, Any], base_path: Path) -> CheckResult:
    """
    Wrap the generic_handler to cast a raw rule into a typed Rule.

    Args:
        rule: Dictionary parsed from rules.json
        base_path: Path to Azure Functions app

    Returns:
        Structured result with status, label, value, and optional hint.
    """
    typed_rule = cast(Rule, rule)
    result = generic_handler(typed_rule, base_path)

    output: CheckResult = {
        "status": result["status"],
        "label": typed_rule.get("label", typed_rule["id"]),
        "value": result["detail"],
    }

    if "hint" in typed_rule:
        output["hint"] = typed_rule["hint"]

    return output
