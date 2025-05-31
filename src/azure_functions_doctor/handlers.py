import os
import sys
from typing import Any, Callable, Dict

from packaging.version import Version  # type: ignore
from packaging.version import parse as parse_version


def compare_version(rule: Dict[str, Any], path: str) -> Dict[str, str]:
    """
    Compare the current Python version against the expected version.

    Args:
        rule: Dictionary with 'value' (expected version) and 'operator' (comparison).
        path: Project path (unused).

    Returns:
        A dictionary containing 'status' and 'detail' about the version comparison.
    """
    expected: str = rule["value"]
    operator: str = rule["operator"]
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    # Define operator map with explicit type annotations
    op_map: Dict[str, Callable[[Version, Version], bool]] = {
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b,
        "==": lambda a, b: a == b,
        ">": lambda a, b: a > b,
        "<": lambda a, b: a < b,
    }

    current: Version = parse_version(current_version)
    expected_v: Version = parse_version(expected)

    passed: bool = op_map[operator](current, expected_v)

    return {
        "status": "pass" if passed else "fail",
        "detail": f"Current: {current_version}, Expected: {operator}{expected}",
    }


def env_var_exists(rule: Dict[str, Any], path: str) -> Dict[str, str]:
    """
    Check if a specific environment variable is set.

    Args:
        rule: Dictionary with 'var' key.
        path: Project path (unused).

    Returns:
        A dictionary indicating whether the environment variable is set.
    """
    var: str = rule["var"]
    exists = os.getenv(var) is not None
    return {
        "status": "pass" if exists else "fail",
        "detail": f"{var} is {'set' if exists else 'not set'}",
    }


def path_exists(rule: Dict[str, Any], path: str) -> Dict[str, str]:
    """
    Check if a given path exists on the file system.

    Args:
        rule: Dictionary with 'target' (can be 'sys.executable' or relative path).
        path: Base directory to resolve the target path.

    Returns:
        A dictionary indicating whether the path exists.
    """
    target: str = rule["target"]
    if target == "sys.executable":
        target_path = sys.executable
    else:
        target_path = os.path.join(path, target)

    exists = os.path.exists(target_path)
    return {
        "status": "pass" if exists else "fail",
        "detail": f"{target_path} {'exists' if exists else 'is missing'}",
    }


def file_exists(rule: Dict[str, Any], path: str) -> Dict[str, str]:
    """
    Check if a specific file exists.

    Args:
        rule: Dictionary with 'target' (relative file path).
        path: Base path to check the file existence.

    Returns:
        A dictionary indicating whether the file exists.
    """
    target = os.path.join(path, rule["target"])
    exists = os.path.isfile(target)
    return {
        "status": "pass" if exists else "fail",
        "detail": f"{target} {'exists' if exists else 'is missing'}",
    }


def package_installed(rule: Dict[str, Any], path: str) -> Dict[str, str]:
    """
    Check if a Python package is installed in the current environment.

    Args:
        rule: Dictionary with 'target' as the package name.
        path: Project path (unused).

    Returns:
        A dictionary indicating whether the package is installed.
    """
    package_name: str = rule["target"]
    try:
        __import__(package_name)
        return {
            "status": "pass",
            "detail": f"{package_name} is installed",
        }
    except ImportError:
        return {
            "status": "fail",
            "detail": f"{package_name} is not installed",
        }
