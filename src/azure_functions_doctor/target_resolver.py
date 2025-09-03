import subprocess
import sys

from azure_functions_doctor.logging_config import get_logger

logger = get_logger(__name__)


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
            output = subprocess.check_output(["func", "--version"], text=True, timeout=10)
            return output.strip()
        except FileNotFoundError:
            logger.debug("Azure Functions Core Tools not found in PATH")
            return "not_installed"
        except subprocess.TimeoutExpired:
            logger.warning("Timeout getting func version")
            return "timeout"
        except TimeoutError:
            logger.warning("Timeout getting func version")
            return "timeout"
        except subprocess.CalledProcessError as e:
            logger.warning(f"func command failed with code {e.returncode}")
            return f"error_{e.returncode}"
        except Exception as exc:
            logger.error(f"Unexpected error getting func version: {exc}")
            return "unknown_error"
    raise ValueError(f"Unknown target: {target}")
