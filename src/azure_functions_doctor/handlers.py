import importlib.util
import os
import sys
from pathlib import Path
from typing import Literal, TypedDict

from packaging.version import parse as parse_version


class Rule(TypedDict, total=False):
    """
    A typed dictionary representing a diagnostic rule from rules.json.
    Each field is optional and depends on the check type.
    """

    type: Literal[
        "compare_version", "env_var_exists", "path_exists", "file_exists", "package_installed"
    ]  # Type of the check to perform
    label: str  # Human-readable label (optional)
    target: str  # Target file path, package name, or value
    operator: str  # Comparison operator (e.g., >=, ==)
    value: str  # Expected value for comparison
    var: str  # Environment variable to check
    id: str  # Unique identifier for the rule
    hint: str  # Optional hint or recommendation for the user


def generic_handler(rule: Rule, path: Path) -> dict[str, str]:
    """
    Dispatch and execute a generic diagnostic rule.

    Args:
        rule: A Rule dictionary containing check type and parameters.
        path: Base path of the Azure Functions project.

    Returns:
        A dictionary with:
            - 'status': 'pass' or 'fail'
            - 'detail': explanation of the result
    """
    check_type = rule.get("type", "")

    if check_type == "compare_version":
        # Compare system Python version to expected
        expected = rule["value"]
        operator = rule["operator"]
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        current = parse_version(current_version)
        expected_v = parse_version(expected)

        passed = {
            ">=": current >= expected_v,
            "<=": current <= expected_v,
            "==": current == expected_v,
            ">": current > expected_v,
            "<": current < expected_v,
        }.get(operator, False)

        return {
            "status": "pass" if passed else "fail",
            "detail": f"Current: {current_version}, Expected: {operator}{expected}",
        }

    if check_type == "env_var_exists":
        # Check if environment variable is set
        var = rule["var"]
        exists = os.getenv(var) is not None
        return {
            "status": "pass" if exists else "fail",
            "detail": f"{var} is {'set' if exists else 'not set'}",
        }

    if check_type == "path_exists":
        # Check if a specific path exists (can be sys.executable or relative)
        target = rule["target"]
        target_path = sys.executable if target == "sys.executable" else os.path.join(path, target)
        exists = os.path.exists(target_path)
        return {
            "status": "pass" if exists else "fail",
            "detail": f"{target_path} {'exists' if exists else 'is missing'}",
        }

    if check_type == "file_exists":
        # Check if a file exists relative to the base path
        target = os.path.join(path, rule["target"])
        exists = os.path.isfile(target)
        return {
            "status": "pass" if exists else "fail",
            "detail": f"{target} {'exists' if exists else 'is missing'}",
        }

    if check_type == "package_installed":
        # Check if a Python package is importable
        package_name = rule["target"]
        found = importlib.util.find_spec(package_name) is not None
        return {
            "status": "pass" if found else "fail",
            "detail": f"{package_name} is {'installed' if found else 'not installed'}",
        }

    return {
        "status": "fail",
        "detail": f"Unsupported check type: {check_type}",
    }
