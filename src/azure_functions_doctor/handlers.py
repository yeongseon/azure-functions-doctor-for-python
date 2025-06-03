import logging
import os
import sys
from pathlib import Path
from typing import Literal, TypedDict, Union

from packaging.version import parse as parse_version

logger = logging.getLogger(__name__)


def _create_result(status: str, detail: str) -> dict[str, str]:
    """Create a standardized result dictionary."""
    return {"status": status, "detail": detail}


def _handle_exception(operation: str, exc: Exception) -> dict[str, str]:
    """Handle exceptions consistently across all handlers."""
    error_msg = f"Error during {operation}: {exc}"
    logger.error(error_msg, exc_info=True)
    return _create_result("error", error_msg)


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
            return _create_result("fail", "Missing condition fields for compare_version")

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
            return _create_result(
                "pass" if passed else "fail",
                f"Python version is {current_version}, expected {operator}{value}",
            )

        return _create_result("fail", f"Unknown target for version comparison: {target}")

    # Check if an environment variable is set
    if check_type == "env_var_exists":
        if not target:
            return _create_result("fail", "Missing environment variable name")

        exists = os.getenv(target) is not None
        return _create_result(
            "pass" if exists else "fail",
            f"{target} is {'set' if exists else 'not set'}",
        )

    # Check if a path exists (including sys.executable)
    if check_type == "path_exists":
        if not target:
            return _create_result("fail", "Missing target path")

        resolved_path = sys.executable if target == "sys.executable" else os.path.join(path, target)
        exists = os.path.exists(resolved_path)

        if exists:
            return _create_result("pass", f"{resolved_path} exists")

        if not rule.get("required", True):
            return _create_result("pass", f"{resolved_path} is missing (optional)")

        return _create_result("fail", f"{resolved_path} is missing")

    # Check if a specific file exists
    if check_type == "file_exists":
        if not target:
            return _create_result("fail", "Missing file path")

        file_path = os.path.join(path, target)
        exists = os.path.isfile(file_path)

        if exists:
            return _create_result("pass", f"{file_path} exists")

        if not rule.get("required", True):
            return _create_result("pass", f"{file_path} not found (optional for local development)")

        return _create_result("fail", f"{file_path} not found")

    # Check if a Python package is importable
    if check_type == "package_installed":
        if not target:
            return _create_result("fail", "Missing package name")

        import_path_str: str = str(target)

        try:
            __import__(import_path_str)
            return _create_result("pass", f"Module '{import_path_str}' is installed")
        except ImportError as exc:
            return _create_result("fail", f"Module '{import_path_str}' is not installed: {exc}")
        except Exception as exc:
            return _handle_exception(f"importing module '{import_path_str}'", exc)

    # Check if a keyword exists in any .py source files
    if check_type == "source_code_contains":
        keyword = condition.get("keyword")
        if not isinstance(keyword, str):
            return _create_result("fail", "Missing or invalid 'keyword' in condition")

        found = False

        for py_file in path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                if keyword in content:
                    found = True
                    break
            except Exception as exc:
                logger.warning(f"Failed to read file {py_file}: {exc}")
                continue

        return _create_result(
            "pass" if found else "fail",
            f"Keyword '{keyword}' {'found' if found else 'not found'} in source code",
        )

    # Unknown check type fallback
    return _create_result("fail", f"Unknown check type: {check_type}")
