from pathlib import Path
from typing import Any, cast

from azure_functions_doctor.handlers import Rule, generic_handler


def run_check(rule: dict[str, Any], base_path: Path) -> dict[str, Any]:
    """
    Wrap the generic_handler to cast a raw rule into a typed Rule.

    Args:
        rule: Dictionary parsed from rules.json
        base_path: Path to Azure Functions app

    Returns:
        Structured result with status, label, value, and optional hint.
    """
    result = generic_handler(cast(Rule, rule), base_path)

    return {
        "status": result["status"],
        "label": rule.get("label", rule.get("id")),
        "value": result["detail"],
        "hint": rule.get("hint"),
    }
