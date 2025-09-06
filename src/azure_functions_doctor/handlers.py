import json
import os
import re
import sys
from pathlib import Path
from typing import Literal, TypedDict, Union

from packaging.version import parse as parse_version

from azure_functions_doctor.logging_config import get_logger

logger = get_logger(__name__)


def _create_result(status: str, detail: str) -> dict[str, str]:
    """Create a standardized result dictionary."""
    return {"status": status, "detail": detail}


def _handle_exception(operation: str, exc: Exception) -> dict[str, str]:
    """Handle exceptions consistently across all handlers."""
    error_msg = f"Error during {operation}: {exc}"
    logger.error(error_msg, exc_info=True)
    return _create_result("error", error_msg)


def _handle_specific_exceptions(operation: str, exc: Exception) -> dict[str, str]:
    """Handle specific exception types with user-friendly messages."""
    if isinstance(exc, UnicodeDecodeError):
        return _create_result(
            "error", f"File encoding error in {operation}: {exc}. Please check file encoding (UTF-8 recommended)."
        )
    elif isinstance(exc, (ValueError, TypeError)):
        return _create_result(
            "fail", f"Configuration error in {operation}: {exc}. Please check your rule configuration."
        )
    elif isinstance(exc, (OSError, PermissionError)):
        return _create_result(
            "error", f"File system error in {operation}: {exc}. Please check file permissions and paths."
        )
    elif isinstance(exc, ImportError):
        return _create_result("fail", f"Missing dependency in {operation}: {exc}. Please install required packages.")
    elif isinstance(exc, MemoryError):
        return _create_result(
            "error", f"Memory error in {operation}: File too large to process. Consider using smaller files."
        )
    elif isinstance(exc, KeyboardInterrupt):
        # Re-raise keyboard interrupt to allow proper cleanup
        raise exc
    elif isinstance(exc, SystemExit):
        # Re-raise system exit to allow proper cleanup
        raise exc
    else:
        # For unknown exceptions, provide generic error message
        logger.error(f"Unexpected error in {operation}: {exc}", exc_info=True)
        return _create_result("error", f"Unexpected error in {operation}. Please check the logs for more details.")


class Condition(TypedDict, total=False):
    target: str
    operator: str
    value: Union[str, int, float]
    keyword: str
    jsonpath: str


class Rule(TypedDict, total=False):
    id: str
    type: Literal[
        "compare_version",
        "env_var_exists",
        "path_exists",
        "file_exists",
        "package_installed",
        "source_code_contains",
        "conditional_exists",
        "callable_detection",
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


class HandlerRegistry:
    """Registry for diagnostic check handlers with individual handler methods."""

    def __init__(self) -> None:
        self._handlers = {
            "compare_version": self._handle_compare_version,
            "env_var_exists": self._handle_env_var_exists,
            "path_exists": self._handle_path_exists,
            "file_exists": self._handle_file_exists,
            "package_installed": self._handle_package_installed,
            "source_code_contains": self._handle_source_code_contains,
            "conditional_exists": self._handle_conditional_exists,
            "callable_detection": self._handle_callable_detection,
        }

    def handle(self, rule: Rule, path: Path) -> dict[str, str]:
        """Route rule execution to appropriate handler."""
        check_type = rule.get("type")
        if check_type is None:
            return _create_result("fail", "Missing check type in rule")
        handler = self._handlers.get(check_type)

        if not handler:
            return _create_result("fail", f"Unknown check type: {check_type}")

        try:
            return handler(rule, path)
        except Exception as exc:
            return _handle_specific_exceptions(f"executing {check_type} check", exc)

    def _handle_compare_version(self, rule: Rule, path: Path) -> dict[str, str]:
        """Handle version comparison checks."""
        condition = rule.get("condition", {})
        target = condition.get("target")
        operator = condition.get("operator")
        value = condition.get("value")

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

    def _handle_env_var_exists(self, rule: Rule, path: Path) -> dict[str, str]:
        """Handle environment variable existence checks."""
        condition = rule.get("condition", {})
        target = condition.get("target")

        if not target:
            return _create_result("fail", "Missing environment variable name")

        exists = os.getenv(target) is not None
        return _create_result(
            "pass" if exists else "fail",
            f"{target} is {'set' if exists else 'not set'}",
        )

    def _handle_path_exists(self, rule: Rule, path: Path) -> dict[str, str]:
        """Handle path existence checks."""
        condition = rule.get("condition", {})
        target = condition.get("target")

        if not target:
            return _create_result("fail", "Missing target path")

        resolved_path = sys.executable if target == "sys.executable" else os.path.join(path, target)
        exists = os.path.exists(resolved_path)

        if exists:
            return _create_result("pass", f"{resolved_path} exists")

        if not rule.get("required", True):
            return _create_result("pass", f"{resolved_path} is missing (optional)")

        return _create_result("fail", f"{resolved_path} is missing")

    def _handle_file_exists(self, rule: Rule, path: Path) -> dict[str, str]:
        """Handle file existence checks."""
        condition = rule.get("condition", {})
        target = condition.get("target")

        if not target:
            return _create_result("fail", "Missing file path")

        file_path = os.path.join(path, target)
        exists = os.path.isfile(file_path)

        if exists:
            return _create_result("pass", f"{file_path} exists")

        if not rule.get("required", True):
            return _create_result("pass", f"{file_path} not found (optional for local development)")

        return _create_result("fail", f"{file_path} not found")

    def _handle_package_installed(self, rule: Rule, path: Path) -> dict[str, str]:
        """Handle Python package installation checks."""
        condition = rule.get("condition", {})
        target = condition.get("target")

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

    def _handle_source_code_contains(self, rule: Rule, path: Path) -> dict[str, str]:
        """Handle source code keyword search checks."""
        condition = rule.get("condition", {})
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
            except PermissionError:
                logger.warning(f"Permission denied reading {py_file}")
                continue
            except UnicodeDecodeError:
                logger.warning(f"Encoding error in {py_file}, trying with errors='ignore'")
                try:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")
                    if keyword in content:
                        found = True
                        break
                except Exception:
                    logger.warning(f"Failed to read {py_file} even with error handling")
                    continue
            except MemoryError:
                logger.error(f"File too large to process: {py_file}")
                continue
            except Exception as exc:
                logger.error(f"Unexpected error reading {py_file}: {exc}")
                continue

        return _create_result(
            "pass" if found else "fail",
            f"Keyword '{keyword}' {'found' if found else 'not found'} in source code",
        )

    def _handle_conditional_exists(self, rule: Rule, path: Path) -> dict[str, str]:
        """Handle conditional existence checks such as durableTask in host.json when durable usage exists."""
        # Determine if project uses Durable Functions by scanning for common imports/keywords
        durable_keywords = ["durable", "DurableOrchestrationContext", "durable_functions", "orchestrator"]
        uses_durable = False

        try:
            for py_file in path.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                lowered = content.lower()
                if any(k in lowered for k in durable_keywords):
                    uses_durable = True
                    break
        except Exception as exc:
            return _handle_specific_exceptions("scanning for durable usage", exc)

        # If no durable usage detected, skip/soft-pass the check
        if not uses_durable:
            return _create_result("pass", "No Durable Functions usage detected; check skipped")

        # Load host.json and verify jsonpath-style key presence
        condition = rule.get("condition", {})
        jsonpath = condition.get("jsonpath")

        if not jsonpath:
            return _create_result("fail", "Missing jsonpath in condition for conditional_exists check")

        # Ensure jsonpath is a str for type-checkers and safe operations
        if not isinstance(jsonpath, str):
            return _create_result("fail", "jsonpath must be a string for conditional_exists check")

        host_path = path / "host.json"
        if not host_path.exists():
            return _create_result("fail", "host.json not found but Durable Functions detected")

        try:
            host_data = json.loads(host_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return _handle_specific_exceptions("reading host.json", exc)

        # Support simple jsonpath like $.extensions.durableTask or $.extensionBundle
        pointer = jsonpath.lstrip("$.")
        parts = pointer.split(".") if pointer else []
        node = host_data
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                return _create_result("fail", f"Required host.json property '{jsonpath}' not found")

        return _create_result("pass", f"host.json contains '{jsonpath}'")

    def _handle_callable_detection(self, rule: Rule, path: Path) -> dict[str, str]:
        """Detect ASGI/WSGI callable exposure in source files (basic heuristics)."""
        patterns = [
            r"\bFastAPI\s*\(|\bStarlette\s*\(|\bFlask\s*\(|\bQuart\s*\(",
            r"\bapp\s*=",
            r"ASGIApp|WSGIApp|asgi_app|wsgi_app",
        ]

        found_items: list[str] = []
        try:
            for py_file in path.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                for pat in patterns:
                    if re.search(pat, content):
                        found_items.append(f"{py_file.relative_to(path)}:{pat}")
                        break
        except Exception as exc:
            return _handle_specific_exceptions("scanning for ASGI/WSGI callables", exc)

        if found_items:
            return _create_result("pass", f"Detected ASGI/WSGI-related patterns: {found_items[:3]}")

        return _create_result("fail", "No ASGI/WSGI callable detected in project source")


# Global registry instance
_registry = HandlerRegistry()


def generic_handler(rule: Rule, path: Path) -> dict[str, str]:
    """
    Execute a diagnostic rule based on its type and condition.

    This function maintains backward compatibility while delegating to the registry.

    Args:
        rule: The diagnostic rule to execute.
        path: Path to the Azure Functions project.

    Returns:
        A dictionary with the status and detail of the check.
    """
    return _registry.handle(rule, path)
