import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import List, Literal, TypedDict, Union

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
            "error",
            (f"File encoding error in {operation}: {exc}. " "Please check file encoding (UTF-8 recommended)."),
        )
    elif isinstance(exc, (ValueError, TypeError)):
        return _create_result(
            "fail",
            f"Configuration error in {operation}: {exc}. Please check your rule configuration.",
        )
    elif isinstance(exc, (OSError, PermissionError)):
        return _create_result(
            "error",
            f"File system error in {operation}: {exc}. Please check file permissions and paths.",
        )
    elif isinstance(exc, ImportError):
        return _create_result(
            "fail",
            f"Missing dependency in {operation}: {exc}. Please install required packages.",
        )
    elif isinstance(exc, MemoryError):
        return _create_result(
            "error",
            f"Memory error in {operation}: File too large to process. Consider using smaller files.",
        )
    elif isinstance(exc, KeyboardInterrupt):
        # Re-raise keyboard interrupt to allow proper cleanup
        raise exc
    elif isinstance(exc, SystemExit):
        # Re-raise system exit to allow proper cleanup
        raise exc
    else:
        logger.error(f"Unexpected error in {operation}: {exc}", exc_info=True)
        return _create_result("error", f"Unexpected error in {operation}. Please check the logs for more details.")


class Condition(TypedDict, total=False):
    target: str
    operator: str
    value: Union[str, int, float]
    keyword: str
    jsonpath: str
    targets: list[str]
    patterns: list[str]
    pypi: str


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
        "executable_exists",
        "any_of_exists",
        "file_glob_check",
        "host_json_property",
        "binding_validation",
        "cron_validation",
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
            "executable_exists": self._handle_executable_exists,
            "any_of_exists": self._handle_any_of_exists,
            "file_glob_check": self._handle_file_glob_check,
            "host_json_property": self._handle_host_json_property,
            "binding_validation": self._handle_binding_validation,
            "cron_validation": self._handle_cron_validation,
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
        condition = rule.get("condition", {}) or {}
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
        condition = rule.get("condition", {}) or {}
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
        condition = rule.get("condition", {}) or {}
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
        condition = rule.get("condition", {}) or {}
        target = condition.get("target")

        if not target:
            return _create_result("fail", "Missing file path")

        file_path = os.path.join(path, target)
        exists = os.path.isfile(file_path)

        if exists:
            return _create_result("pass", f"{file_path} exists")

        if not rule.get("required", True):
            return _create_result(
                "pass",
                f"{file_path} not found (optional for local development)",
            )

        return _create_result("fail", f"{file_path} not found")

    def _handle_package_installed(self, rule: Rule, path: Path) -> dict[str, str]:
        """Handle Python package installation checks."""
        condition = rule.get("condition", {}) or {}
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
        condition = rule.get("condition", {}) or {}
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
        durable_keywords = [
            "durable",
            "DurableOrchestrationContext",
            "durable_functions",
            "orchestrator",
        ]
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

        if not uses_durable:
            return _create_result("pass", "No Durable Functions usage detected; check skipped")

        condition = rule.get("condition", {}) or {}
        jsonpath = condition.get("jsonpath")

        if not jsonpath:
            return _create_result(
                "fail",
                "Missing jsonpath in condition for conditional_exists check",
            )

        if not isinstance(jsonpath, str):
            return _create_result("fail", "jsonpath must be a string for conditional_exists check")

        host_path = path / "host.json"
        if not host_path.exists():
            return _create_result("fail", "host.json not found but Durable Functions detected")

        try:
            host_data = json.loads(host_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return _handle_specific_exceptions("reading host.json", exc)

        pointer = jsonpath.lstrip("$.")
        parts = pointer.split(".") if pointer else []
        node = host_data
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                return _create_result(
                    "fail",
                    f"Required host.json property '{jsonpath}' not found",
                )

        return _create_result("pass", f"host.json contains '{jsonpath}'")

    def _handle_callable_detection(self, rule: Rule, path: Path) -> dict[str, str]:
        """Detect ASGI/WSGI callable exposure in source files (basic heuristics)."""
        patterns = [
            r"\bFastAPI\s*\(|\bStarlette\s*\(|\bFlask\s*\(|\bQuart\s*\(",
            r"\bapp\s*=",
            r"ASGIApp|WSGIApp|asgi_app|wsgi_app",
        ]

        found_items: List[str] = []
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

    # --- adapters / additional handlers ---

    def _handle_executable_exists(self, rule: Rule, path: Path) -> dict[str, str]:
        """Check if an executable is available on PATH."""
        condition = rule.get("condition", {}) or {}
        target = condition.get("target")
        if not target:
            return _create_result("fail", "Missing 'target' for executable_exists")
        found = shutil.which(target) is not None
        return _create_result(
            "pass" if found else "fail",
            f"Executable '{target}' {'found' if found else 'not found'} in PATH",
        )

    def _handle_any_of_exists(self, rule: Rule, path: Path) -> dict[str, str]:
        """Check if any of a list of targets exist (env vars, host.json keys, files)."""
        condition = rule.get("condition", {}) or {}
        targets = condition.get("targets", [])
        if not targets or not isinstance(targets, list):
            return _create_result("fail", "Missing 'targets' list for any_of_exists")

        for t in targets:
            if isinstance(t, str) and t.startswith("host.json:"):
                key = t.split("host.json:", 1)[1].lstrip(".")
                host_path = path / "host.json"
                if host_path.exists():
                    try:
                        data = json.loads(host_path.read_text(encoding="utf-8"))
                        node = data
                        for p in key.split("."):
                            if isinstance(node, dict) and p in node:
                                node = node[p]
                            else:
                                node = None
                                break
                        if node is not None:
                            return _create_result("pass", f"Found host.json:{key}")
                    except Exception:
                        continue
            else:
                # env var
                if os.getenv(str(t)) is not None:
                    return _create_result("pass", f"Environment variable '{t}' is set")
                # file path
                candidate = path / str(t)
                if candidate.exists():
                    return _create_result("pass", f"Found file/path '{candidate}'")
        return _create_result("fail", "None of the targets in 'targets' were found")

    def _handle_file_glob_check(self, rule: Rule, path: Path) -> dict[str, str]:
        """Detect unwanted files by glob patterns."""
        condition = rule.get("condition", {}) or {}
        patterns = condition.get("patterns", [])
        if not patterns or not isinstance(patterns, list):
            return _create_result("fail", "Missing 'patterns' list for file_glob_check")
        matches: List[str] = []
        try:
            for pat in patterns:
                for p in path.rglob(pat):
                    matches.append(str(p.relative_to(path)))
                    if len(matches) >= 5:
                        break
                if len(matches) >= 5:
                    break
        except Exception as exc:
            return _handle_specific_exceptions("checking file globs", exc)
        if matches:
            return _create_result("fail", f"Found unwanted files: {matches[:5]}")
        return _create_result("pass", "No unwanted files detected")

    def _handle_host_json_property(self, rule: Rule, path: Path) -> dict[str, str]:
        """Check a property exists in host.json using simple jsonpath-like pointer."""
        condition = rule.get("condition", {}) or {}
        jsonpath = condition.get("jsonpath")
        if not jsonpath or not isinstance(jsonpath, str):
            return _create_result("fail", "Missing or invalid 'jsonpath' in condition")
        host_path = path / "host.json"
        if not host_path.exists():
            return _create_result("fail", "host.json not found")
        try:
            host_data = json.loads(host_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return _handle_specific_exceptions("reading host.json", exc)
        pointer = jsonpath.lstrip("$.")
        parts = pointer.split(".") if pointer else []
        node = host_data
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                return _create_result("fail", f"host.json property '{jsonpath}' not found")
        return _create_result("pass", f"host.json contains '{jsonpath}'")

    def _handle_binding_validation(self, rule: Rule, path: Path) -> dict[str, str]:
        """
        Basic HTTP trigger binding validation:
        - look for function.json files and validate httpTrigger bindings have authLevel/methods where applicable.
        This is a lightweight heuristic to catch common misconfigurations.
        """
        try:
            issues = []
            for func_file in path.rglob("function.json"):
                try:
                    data = json.loads(func_file.read_text(encoding="utf-8"))
                except Exception:
                    continue
                bindings = data.get("bindings", [])
                for b in bindings:
                    if b.get("type") == "httpTrigger":
                        if "authLevel" not in b:
                            issues.append(f"{func_file.relative_to(path)}: missing authLevel")
                        if "methods" in b and not b.get("methods"):
                            issues.append(f"{func_file.relative_to(path)}: empty methods in httpTrigger")
            if issues:
                return _create_result("fail", f"HTTP trigger binding issues: {issues[:5]}")
            return _create_result("pass", "HTTP trigger bindings appear valid or not present")
        except Exception as exc:
            return _handle_specific_exceptions("validating httpTrigger bindings", exc)

    def _handle_cron_validation(self, rule: Rule, path: Path) -> dict[str, str]:
        """
        Simple CRON validation for timerTrigger schedules found in function.json files.
        Accepts 5- or 6-field cron-like expressions as a heuristic.
        """
        cron_regex = re.compile(r"^([\S]+\s+){4,5}[\S]+$")
        try:
            found_cron = False
            invalid = []
            for func_file in path.rglob("function.json"):
                try:
                    data = json.loads(func_file.read_text(encoding="utf-8"))
                except Exception:
                    continue
                bindings = data.get("bindings", [])
                for b in bindings:
                    if b.get("type") == "timerTrigger":
                        schedule = b.get("schedule", "")
                        found_cron = True
                        if not isinstance(schedule, str) or not cron_regex.match(schedule.strip()):
                            invalid.append(f"{func_file.relative_to(path)}: invalid schedule '{schedule}'")
            if invalid:
                return _create_result("fail", f"Invalid CRON expressions: {invalid[:5]}")
            if not found_cron:
                return _create_result("pass", "No timerTrigger schedules found")
            return _create_result("pass", "Timer trigger schedules appear valid")
        except Exception as exc:
            return _handle_specific_exceptions("validating cron expressions", exc)


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
