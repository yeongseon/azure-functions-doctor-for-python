from collections.abc import Callable
from typing import Any

from .handlers import (
    compare_version,
    env_var_exists,
    file_exists,
    package_installed,
    path_exists,
)

# Registry mapping check types to their corresponding handler functions
CHECK_REGISTRY: dict[str, Callable[[dict[str, Any], str], dict[str, str]]] = {
    "compare_version": compare_version,
    "env_var_exists": env_var_exists,
    "path_exists": path_exists,
    "file_exists": file_exists,
    "package_installed": package_installed,
}


def get_checker(check_type: str) -> Callable[[dict[str, Any], str], dict[str, str]]:
    """
    Return the checker function associated with a given check type.

    Args:
        check_type: A string representing the type of check (e.g. 'file_exists').

    Returns:
        The corresponding checker function.

    Raises:
        ValueError: If the check type is not registered.
    """
    if check_type not in CHECK_REGISTRY:
        raise ValueError(f"Unknown check type: {check_type}")
    return CHECK_REGISTRY[check_type]
