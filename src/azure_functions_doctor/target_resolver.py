import subprocess
import sys


def resolve_target_value(target: str) -> str:
    """
    Resolve the current value of a target used in version comparison or diagnostics.

    Args:
        target: The name of the target to resolve. Examples include "python" or "func_core_tools".

    Returns:
        A string representing the resolved version or value.

    Raises:
        ValueError: If the target is not recognized.
    """
    if target == "python":
        return sys.version.split()[0]
    if target == "func_core_tools":
        try:
            output = subprocess.check_output(["func", "--version"], text=True)
            return output.strip()
        except Exception:
            return "0.0.0"  # Return a fallback version if resolution fails
    raise ValueError(f"Unknown target: {target}")
