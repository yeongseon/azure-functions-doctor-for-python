import os
import sys
from pathlib import Path
from typing import Literal, TypedDict, Union

from packaging.version import parse as parse_version


class Condition(TypedDict, total=False):
    target: str
    operator: str
    value: Union[str, int, float]
    keyword: str


class Rule(TypedDict, total=False):
    id: str
    type: Literal[
        "compare_version",
        "env_var_exists",
        "path_exists",
        "file_exists",
        "package_installed",
        "source_code_contains",
    ]
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
        rule: The diagnostic rule to execute.

    Returns:
        A dictionary with the status and detail of the check.
    """
    check_type = rule.get("type")
    condition = rule.get("condition", {})

    target = condition.get("target")
    operator = condition.get("operator")
    value = condition.get("value")

    # Compare current Python version with expected version
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

    # Check if an environment variable is set
    if check_type == "env_var_exists":
        if not target:
            return {"status": "fail", "detail": "Missing environment variable name"}

        exists = os.getenv(target) is not None
        return {
            "status": "pass" if exists else "fail",
            "detail": f"{target} is {'set' if exists else 'not set'}",
        }

    # Check if a path exists (including sys.executable)
    if check_type == "path_exists":
        if not target:
            return {"status": "fail", "detail": "Missing target path"}

        resolved_path = sys.executable if target == "sys.executable" else os.path.join(path, target)
        exists = os.path.exists(resolved_path)

        if exists:
            return {"status": "pass", "detail": f"{resolved_path} exists"}

        if not rule.get("required", True):
            return {"status": "pass", "detail": f"{resolved_path} is missing (optional)"}

        return {"status": "fail", "detail": f"{resolved_path} is missing"}

    # Check if a specific file exists
    if check_type == "file_exists":
        if not target:
            return {"status": "fail", "detail": "Missing file path"}

        file_path = os.path.join(path, target)
        exists = os.path.isfile(file_path)

        if exists:
            return {"status": "pass", "detail": f"{file_path} exists"}

        if not rule.get("required", True):
            return {"status": "pass", "detail": f"{file_path} not found (optional for local development)"}

        return {"status": "fail", "detail": f"{file_path} not found"}

    # Check if a Python package is importable
    if check_type == "package_installed":
        if not target:
            return {"status": "fail", "detail": "Missing package name"}

        import_path_str: str = str(target)

        try:
            __import__(import_path_str)
            found = True
            error_msg = ""
        except ImportError as exc:
            found = False
            error_msg = f": {exc}"

        return {
            "status": "pass" if found else "fail",
            "detail": f"Module '{import_path_str}' is {'installed' if found else f'not installed{error_msg}'}",
        }

    # Check if a keyword exists in any .py source files
    if check_type == "source_code_contains":
        keyword = condition.get("keyword")
        if not isinstance(keyword, str):
            return {
                "status": "fail",
                "detail": "Missing or invalid 'keyword' in condition",
            }

        found = False

        for py_file in path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                if keyword in content:
                    found = True
                    break
            except Exception:
                continue

        return {
            "status": "pass" if found else "fail",
            "detail": f"Keyword '{keyword}' {'found' if found else 'not found'} in source code",
        }

    # Unknown check type fallback
    return {"status": "fail", "detail": f"Unknown check type: {check_type}"}
