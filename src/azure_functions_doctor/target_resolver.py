from pathlib import Path
import re
import shutil
import subprocess  # nosec B404
import sys
from typing import Callable, Dict, Optional, Tuple

from azure_functions_doctor.logging_config import get_logger

logger = get_logger(__name__)


def _resolve_python(override: Optional[str] = None) -> str:
    """Resolve the running Python interpreter version."""
    return override if override is not None else sys.version.split()[0]


_PYTHON_VERSION_RE = re.compile(r"(\d+\.\d+(?:\.\d+)?)")


def _requires_python_floor(pyproject: Path) -> Optional[str]:
    """Extract the lower version bound from ``[project] requires-python``."""
    try:
        text = pyproject.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', text)
    if not match:
        return None
    version_match = _PYTHON_VERSION_RE.search(match.group(1))
    return version_match.group(1) if version_match else None


def resolve_python_target(
    project_path: Optional[Path] = None, override: Optional[str] = None
) -> Tuple[str, str]:
    """Resolve the Python version to diagnose against, with provenance.

    Precedence (first match wins):

    1. Explicit ``override`` (e.g. ``--target-python``) -> source ``"override"``.
    2. ``pyproject.toml`` ``[project] requires-python`` floor ->
       source ``"pyproject:requires-python"``.
    3. ``.python-version`` file -> source ``".python-version"``.
    4. The running interpreter -> source ``"tool-runtime"`` (always resolves).

    Args:
        project_path: Root of the project under diagnosis. When ``None`` or when
            no project signal is found, the running interpreter is used.
        override: Explicit target that short-circuits project detection.

    Returns:
        A ``(version, source)`` tuple where ``source`` records provenance.
    """
    if override is not None:
        return override, "override"

    if project_path is not None:
        pyproject = project_path / "pyproject.toml"
        if pyproject.is_file():
            version = _requires_python_floor(pyproject)
            if version is not None:
                return version, "pyproject:requires-python"

        python_version_file = project_path / ".python-version"
        if python_version_file.is_file():
            try:
                content = python_version_file.read_text(encoding="utf-8").strip()
            except OSError:
                content = ""
            match = _PYTHON_VERSION_RE.search(content)
            if match:
                return match.group(1), ".python-version"

    return sys.version.split()[0], "tool-runtime"


def _resolve_func_core_tools(override: Optional[str] = None) -> str:
    """Resolve the installed Azure Functions Core Tools version."""
    func_path = shutil.which("func")
    if not func_path:
        logger.debug("Azure Functions Core Tools not found in PATH")
        return "not_installed"
    try:
        output = subprocess.check_output([func_path, "--version"], text=True, timeout=10)  # nosec B603
        return output.strip()
    except FileNotFoundError:
        logger.debug("Azure Functions Core Tools executable disappeared before execution")
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


# Registry mapping a target name to its resolver callable.
_TARGET_RESOLVERS: Dict[str, Callable[[Optional[str]], str]] = {
    "python": _resolve_python,
    "func_core_tools": _resolve_func_core_tools,
}


def resolve_target_value(target: str, override: Optional[str] = None) -> str:
    """
    Resolve the current value of a target used in version comparison or diagnostics.

    Args:
        target: The name of the target to resolve. Examples include "python" or "func_core_tools".

    Returns:
        A string representing the resolved version or value.

    Raises:
        ValueError: If the target is not recognized.
    """
    resolver = _TARGET_RESOLVERS.get(target)
    if resolver is None:
        raise ValueError(f"Unknown target: {target}")
    return resolver(override)
