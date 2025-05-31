from pathlib import Path
from typing import Any, Callable

from azure_functions_doctor import handlers


def run_check(check: dict[str, Any], base_path: Path) -> dict[str, Any]:
    """
    Run a single diagnostic check defined in rules.json.

    Args:
        check (dict[str, Any]): The check configuration, including 'type', 'name', 'hint', etc.
        base_path (Path): The root path of the Azure Functions project.

    Returns:
        dict[str, Any]: A result dictionary containing status, label, value, and optionally hint.
    """
    check_type = check["type"]

    # Dynamically look up the check function by name from handlers module
    func: Callable[..., tuple[str, str]] = getattr(handlers, check_type)

    # Filter out non-parameter fields and prepare arguments for the handler
    kwargs: dict[str, Any] = {k: v for k, v in check.items() if k not in {"id", "name", "type", "hint"}}

    # Allow dynamic base path substitution in parameters
    for key, val in kwargs.items():
        if isinstance(val, str) and "${base}" in val:
            kwargs[key] = val.replace("${base}", str(base_path))

    # Run the check function and collect result
    status, value = func(**kwargs)

    return {
        "status": status,
        "label": check["name"],
        "value": value,
        "hint": check.get("hint"),
    }
