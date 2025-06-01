import importlib.util
import os
import sys
from pathlib import Path
from typing import Literal, TypedDict, Union

from packaging.version import parse as parse_version


class Condition(TypedDict, total=False):
    target: str
    operator: str
    value: Union[str, int, float]


class Rule(TypedDict, total=False):
    id: str
    type: Literal["compare_version", "env_var_exists", "path_exists", "file_exists", "package_installed"]
    label: str
    category: str
    section: str
    description: str
    required: bool
    severity: Literal["error", "warning", "info"]
    condition: Condition
    hint: str
    fix: str
    fix_command: str
    hint_url: str
    check_order: int


def generic_handler(rule: Rule, path: Path) -> dict[str, str]:
    """
    Execute a diagnostic rule based on its type and condition.

    Args:
        rule: The rule dictionary.
        path: Path to the Azure Functions project.

    Returns:
        A result dict with status ('pass' or 'fail') and detail message.
    """
    check_type = rule.get("type")
    condition = rule.get("condition", {})

    target = condition.get("target")
    operator = condition.get("operator")
    value = condition.get("value")

    if check_type == "compare_version":
        if not (target and operator and value):
            return {"status": "fail", "detail": "Missing condition fields for compare_version"}

        if target == "python":
            current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            current = parse_version(current_version)
            expected = parse_version(str(value))

            passed = {
                ">=": current >= expected,
                "<=": current <= expected,
                "==": current == expected,
                ">": current > expected,
                "<": current < expected,
            }.get(operator, False)

            return {
                "status": "pass" if passed else "fail",
                "detail": f"Python version is {current_version}, expected {operator}{value}",
            }

        return {"status": "fail", "detail": f"Unknown target for version comparison: {target}"}

    elif check_type == "env_var_exists":
        if not target:
            return {"status": "fail", "detail": "Missing environment variable name"}
        exists = os.getenv(target) is not None
        return {
            "status": "pass" if exists else "fail",
            "detail": f"{target} is {'set' if exists else 'not set'}",
        }

    elif check_type == "path_exists":
        if not target:
            return {"status": "fail", "detail": "Missing target path"}
        resolved_path = sys.executable if target == "sys.executable" else os.path.join(path, target)
        exists = os.path.exists(resolved_path)
        return {
            "status": "pass" if exists else "fail",
            "detail": f"{resolved_path} {'exists' if exists else 'is missing'}",
        }

    elif check_type == "file_exists":
        if not target:
            return {"status": "fail", "detail": "Missing file path"}
        file_path = os.path.join(path, target)
        exists = os.path.isfile(file_path)
        return {
            "status": "pass" if exists else "fail",
            "detail": f"{file_path} {'exists' if exists else 'is missing'}",
        }

    elif check_type == "package_installed":
        if not target:
            return {"status": "fail", "detail": "Missing package name"}
        found = importlib.util.find_spec(target) is not None
        return {
            "status": "pass" if found else "fail",
            "detail": f"Package '{target}' is {'installed' if found else 'not installed'}",
        }

    return {
        "status": "fail",
        "detail": f"Unsupported check type: {check_type}",
    }
