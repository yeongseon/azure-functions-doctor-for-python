import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
from typing import Callable, Dict, List, Optional

from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion
from packaging.version import parse as parse_version

from azure_functions_doctor.handlers._helpers import (
    _HOST_JSON_MISSING,
    _PYTHON_CANDIDATES,
    _RULE_DISPATCH,
    HandlerResult,
    Rule,
    RuleContext,
    _collect_anonymous_auth_routes,
    _collect_inverted_decorator_order,
    _collect_openapi_version_mixing,
    _collect_orchestrator_nondeterminism,
    _collect_routes_missing_validate_http,
    _collect_scan_before_spec,
    _collect_unregistered_blueprint_aliases,
    _collect_unsupported_metadata_versions,
    _create_result,
    _detect_native_dependency_risks,
    _handle_specific_exceptions,
    _iter_project_py_contents,
    _parse_requirements_names,
    _project_declares_validation_dep,
    _project_imports_langgraph,
    _read_project_python_file,
    _resolve_host_json_path,
    _resolve_host_json_pointer,
    _rule_handler,
    _source_contains_ast,
    logger,
    parse_compare_version,
    parse_package,
    parse_source_code,
    parse_target,
)
from azure_functions_doctor.target_resolver import resolve_target_value


class HandlerRegistry:
    """Registry for diagnostic check handlers with individual handler methods."""

    def __init__(self) -> None:
        self._handlers: Dict[
            str, Callable[[Rule, Path, Optional[RuleContext]], HandlerResult]
        ] = {
            check_type: getattr(self, method_name)
            for check_type, method_name in _RULE_DISPATCH.items()
        }

    def handle(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Route rule execution to appropriate handler."""
        check_type = rule.get("type")
        if check_type is None:
            return _create_result("fail", "Missing check type in rule")
        handler = self._handlers.get(check_type)

        if not handler:
            return _create_result("fail", f"Unknown check type: {check_type}")

        try:
            return handler(rule, path, context)
        except Exception as exc:
            return _handle_specific_exceptions(f"executing {check_type} check", exc)

    @_rule_handler
    def _handle_compare_version(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Handle version comparison checks."""
        condition = rule.get("condition", {}) or {}
        params = parse_compare_version(condition)
        if params is None:
            return _create_result("fail", "Missing condition fields for compare_version")
        target, operator, value = params

        if target == "python":
            target_python = context.get("target_python") if context is not None else None
            current_version = resolve_target_value("python", override=target_python)
            tool_runtime = (
                f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            )
            current = parse_version(current_version)
            expected = parse_version(str(value))
            passed = {
                ">=": current >= expected,
                "<=": current <= expected,
                "==": current == expected,
                ">": current > expected,
                "<": current < expected,
            }.get(operator, False)
            detail = (
                f"Target Python: {current_version} (override) — Tool runtime: {tool_runtime}"
                if target_python is not None
                else f"Python {current_version} (tool runtime, {operator}{value})"
            )
            return _create_result(
                "pass" if passed else "fail",
                detail,
            )

        if target == "func_core_tools":
            raw = resolve_target_value("func_core_tools")
            if raw in ("not_installed", "timeout", "unknown_error") or raw.startswith("error_"):
                return _create_result("fail", f"func: {raw}")
            try:
                current = parse_version(raw)
            except InvalidVersion:
                return _create_result("fail", f"func version unparseable: {raw}")
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
                f"func {raw} ({operator}{value})",
            )

        return _create_result("fail", f"Unknown target for version comparison: {target}")

    @_rule_handler
    def _handle_env_var_exists(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Handle environment variable existence checks."""
        condition = rule.get("condition", {}) or {}
        target = parse_target(condition)

        if not target:
            return _create_result("fail", "Missing environment variable name")

        exists = os.getenv(target) is not None
        return _create_result(
            "pass" if exists else "fail",
            f"{target} is {'set' if exists else 'not set'}",
        )

    @_rule_handler
    def _handle_path_exists(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Handle path existence checks."""
        condition = rule.get("condition", {}) or {}
        target = parse_target(condition)

        if not target:
            return _create_result("fail", "Missing target path")

        if target == "sys.executable":
            if not sys.executable:
                return _create_result("fail", "sys.executable is empty")
            resolved_path = Path(sys.executable)
        else:
            resolved_path = path / target

        exists = resolved_path.exists()
        detail = f"{resolved_path} {'exists' if exists else 'missing'}"
        if not exists and not rule.get("required", True):
            detail += " (optional)"
        return _create_result("pass" if exists else "fail", detail)

    @_rule_handler
    def _handle_file_exists(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Handle file existence checks."""
        condition = rule.get("condition", {}) or {}
        target = parse_target(condition)

        if not target:
            return _create_result("fail", "Missing file path")
        file_path = path / target
        exists = file_path.is_file()
        detail = f"{file_path} {'exists' if exists else 'not found'}"
        if not exists and not rule.get("required", True):
            detail += " (optional)"
        return _create_result("pass" if exists else "fail", detail)

    @_rule_handler
    def _handle_package_installed(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Handle Python package installation checks."""
        condition = rule.get("condition", {}) or {}
        target = parse_target(condition)

        if not target:
            return _create_result("fail", "Missing package name")

        import_path_str: str = str(target)
        spec = importlib.util.find_spec(import_path_str)
        if spec is not None:
            return _create_result("pass", f"Module '{import_path_str}' is installed")
        return _create_result("fail", f"Module '{import_path_str}' is not installed")

    @_rule_handler
    def _handle_source_code_contains(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Handle source code keyword search checks (string or AST mode)."""
        condition = rule.get("condition", {}) or {}
        params = parse_source_code(condition)
        if params is None:
            return _create_result("fail", "Missing or invalid 'keyword' in condition")
        keyword, mode = params

        found = False
        if mode == "ast":
            # Support pipe-separated identifiers like "@app.|@bp." so that both
            # standard (@app.route) and Blueprint-style (@bp.route) are recognised.
            raw_parts = keyword.strip().split("|")
            ast_identifier = "|".join(p.strip().lstrip("@").rstrip(".") for p in raw_parts)
            if not ast_identifier:
                return _create_result("fail", "Invalid 'keyword' for AST mode")
            for _py_file, content in _iter_project_py_contents(path):
                if _source_contains_ast(content, ast_identifier):
                    found = True
                    break
        else:
            for _py_file, content in _iter_project_py_contents(path):
                if keyword in content:
                    found = True
                    break

        detail_suffix = " (AST)" if mode == "ast" else ""
        return _create_result(
            "pass" if found else "fail",
            (
                f"Keyword '{keyword}' {'found' if found else 'not found'} "
                f"in source code{detail_suffix}"
            ),
        )

    @_rule_handler
    def _handle_package_declared(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Check that a package name appears in requirements.txt (declaration-level)."""
        condition = rule.get("condition", {}) or {}
        params = parse_package(condition)
        if params is None:
            return _create_result("fail", "Missing 'package' in condition")
        package_name, req_file = params
        req_path = path / Path(req_file)
        if not req_path.exists():
            return _create_result("fail", f"{req_path} not found")
        try:
            content = req_path.read_text(encoding="utf-8")
        except Exception as exc:
            return _handle_specific_exceptions(f"reading {req_file}", exc)
        normalized = _parse_requirements_names(content)
        declared = canonicalize_name(package_name) in normalized
        return _create_result(
            "pass" if declared else "fail",
            f"Package '{package_name}' {'declared' if declared else 'not declared'} in {req_file}",
        )

    @_rule_handler
    def _handle_package_forbidden(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Warn when a package that should NOT be pinned appears in requirements.txt."""
        condition = rule.get("condition", {}) or {}
        params = parse_package(condition)
        if params is None:
            return _create_result("fail", "Missing 'package' in condition")
        package_name, req_file = params
        req_path = path / Path(req_file)
        if not req_path.exists():
            return _create_result("fail", f"{req_path} not found")
        try:
            content = req_path.read_text(encoding="utf-8")
        except Exception as exc:
            return _handle_specific_exceptions(f"reading {req_file}", exc)
        normalized = _parse_requirements_names(content)
        declared = canonicalize_name(package_name) in normalized
        if declared:
            return _create_result(
                "fail",
                f"Package '{package_name}' should not be declared in {req_file} "
                "(managed by the platform)",
            )
        return _create_result("pass", f"Package '{package_name}' not declared in {req_file}")

    @_rule_handler
    def _handle_native_dependency_risk(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Warn when requirements.txt includes packages with native extension risk."""
        condition = rule.get("condition", {}) or {}
        req_file_obj = condition.get("file", "requirements.txt")
        req_file = str(req_file_obj)
        req_path = path / Path(req_file)
        if not req_path.exists():
            return _create_result("pass", f"{req_file} not found; check skipped")
        try:
            content = req_path.read_text(encoding="utf-8")
        except Exception as exc:
            return _handle_specific_exceptions(f"reading {req_file}", exc)

        matches = _detect_native_dependency_risks(content)
        if not matches:
            return _create_result("pass", "No native dependency risk packages declared")

        matched_packages = ", ".join(package for package, _hint in matches)
        detail_lines = [
            f"Native dependencies detected: {matched_packages}",
            "These packages depend on platform-specific native libraries.",
            "Ensure your build environment matches the Azure Functions Linux runtime.",
            "Recommended: use remote build (`func azure functionapp publish --build remote`).",
        ]
        for package, hint in matches:
            if hint:
                detail_lines.append(f"- {package}: {hint}")
        return _create_result("fail", "\n".join(detail_lines))

    @_rule_handler
    def _handle_conditional_exists(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Handle host.json checks that only matter when a related feature is detected."""
        durable_keywords = [
            "durable",
            "DurableOrchestrationContext",
            "durable_functions",
            "orchestrator",
        ]
        uses_durable = False

        try:
            for py_file in path.rglob("*.py"):
                content = _read_project_python_file(py_file)
                if content is None:
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
            return _create_result("fail", "host.json missing (durable usage)")

        try:
            host_data = json.loads(host_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return _handle_specific_exceptions("reading host.json", exc)

        if _resolve_host_json_path(host_data, jsonpath) is _HOST_JSON_MISSING:
            return _create_result(
                "fail",
                f"Required host.json property '{jsonpath}' not found",
            )

        return _create_result("pass", f"host.json contains '{jsonpath}'")

    @_rule_handler
    def _handle_callable_detection(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Detect ASGI/WSGI callable exposure in source files (basic heuristics)."""
        patterns = [
            r"\bAsgiMiddleware\s*\(|\bWsgiMiddleware\s*\(",
            r"\bAsgiFunctionApp\s*\(|\bWsgiFunctionApp\s*\(",
            r"\bFastAPI\s*\(|\bStarlette\s*\(|\bFlask\s*\(|\bQuart\s*\(",
            r"ASGIApp|WSGIApp|asgi_app|wsgi_app",
        ]

        found_items: List[str] = []
        try:
            for py_file in path.rglob("*.py"):
                content = _read_project_python_file(py_file)
                if content is None:
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

    @_rule_handler
    def _handle_executable_exists(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Check if an executable is available on PATH."""
        condition = rule.get("condition", {}) or {}
        target = parse_target(condition)
        if not target:
            return _create_result("fail", "Missing 'target' for executable_exists")
        # Use candidate map for symmetric fallback
        candidates = _PYTHON_CANDIDATES.get(target, [target])
        found = any(shutil.which(c) is not None for c in candidates)
        if found:
            # Concise style: "<name> detected"
            return _create_result("pass", f"{target} detected")
        return _create_result("fail", f"{target} not found")

    @_rule_handler
    def _handle_any_of_exists(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
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
                        node = _resolve_host_json_pointer(data, key.split("."))
                        if node is not _HOST_JSON_MISSING and node is not None:
                            return _create_result("pass", f"host.json:{key} present")
                    except json.JSONDecodeError as exc:
                        logger.debug(f"Skip invalid host.json while checking {key}: {exc}")
            else:
                # env var
                if os.getenv(str(t)) is not None:
                    return _create_result("pass", f"env:{t} set")
                # file path
                candidate = path / str(t)
                if candidate.exists():
                    return _create_result("pass", f"path:{candidate.name} present")
        # Shorter failure detail for concise output integration
        return _create_result("fail", "Targets not found")

    @_rule_handler
    def _handle_file_glob_check(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
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

    @_rule_handler
    def _handle_host_json_property(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
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
        if _resolve_host_json_path(host_data, jsonpath) is _HOST_JSON_MISSING:
            return _create_result("fail", f"host.json property '{jsonpath}' not found")
        return _create_result("pass", f"host.json contains '{jsonpath}'")

    @_rule_handler
    def _handle_host_json_version(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Check that host.json declares \"version\": \"2.0\"."""
        host_path = path / "host.json"
        if not host_path.exists():
            return _create_result("fail", "host.json not found")
        try:
            host_data = json.loads(host_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            msg = f"host.json is not valid JSON: {exc}"
            return _create_result("fail", msg, internal_error=True)
        except Exception as exc:
            return _handle_specific_exceptions("reading host.json", exc)
        version = host_data.get("version") if isinstance(host_data, dict) else None
        if version == "2.0":
            return _create_result("pass", 'host.json version is "2.0"')
        return _create_result(
            "fail",
            f'host.json version is {version!r}, expected "2.0"',
        )

    @_rule_handler
    def _handle_local_settings_security(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Check that local.settings.json is not tracked by git (security risk)."""
        import subprocess  # nosec B404

        settings_path = path / "local.settings.json"
        if not settings_path.exists():
            return _create_result("pass", "local.settings.json not present; check skipped")

        # Check if the file is tracked by git
        try:
            result = subprocess.run(  # nosec B603 B607
                ["git", "-C", str(path), "ls-files", "--error-unmatch", str(settings_path)],
                capture_output=True,
                timeout=10,
            )
            tracked = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            # git not available or not a git repo — skip check
            return _create_result(
                "pass",
                "git not available; local.settings.json git-tracking check skipped",
            )

        if tracked:
            return _create_result(
                "fail",
                "local.settings.json is tracked by git and may expose secrets"
                " — add it to .gitignore",
            )
        return _create_result("pass", "local.settings.json is not tracked by git")

    @_rule_handler
    def _handle_host_json_extension_bundle_version(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Check that extensionBundle in host.json uses the recommended v4 range."""
        host_path = path / "host.json"
        if not host_path.exists():
            return _create_result("fail", "host.json not found")
        try:
            host_data = json.loads(host_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return _handle_specific_exceptions("reading host.json", exc)

        if not isinstance(host_data, dict):
            return _create_result("fail", "host.json is not a JSON object")

        bundle = host_data.get("extensionBundle")
        if bundle is None:
            return _create_result("fail", "extensionBundle not configured in host.json")

        if not isinstance(bundle, dict):
            return _create_result("fail", "extensionBundle in host.json is not an object")

        bundle_id = bundle.get("id", "")
        bundle_version = bundle.get("version", "")

        # Recommended bundle: id=Microsoft.Azure.Functions.ExtensionBundle, version=[4.*, 5.0.0)
        recommended_id = "Microsoft.Azure.Functions.ExtensionBundle"
        if bundle_id != recommended_id:
            return _create_result(
                "fail",
                f"extensionBundle id '{bundle_id}' is not the recommended '{recommended_id}'",
            )

        # Check that the version range starts with [4.
        version_str = str(bundle_version)
        if version_str.startswith("[4."):
            return _create_result(
                "pass",
                f"extensionBundle uses recommended v4 range: {version_str}",
            )

        # Detect older major versions
        import re as _re

        major_match = _re.search(r"\[(\d+)\.", version_str)
        if major_match:
            major = int(major_match.group(1))
            if major < 4:
                return _create_result(
                    "fail",
                    f"extensionBundle version '{version_str}' is below"
                    " recommended v4 range — upgrade to [4.*, 5.0.0)",
                )

        return _create_result(
            "fail",
            f"extensionBundle version '{version_str}' does not match"
            " recommended v4 range [4.*, 5.0.0)",
        )

    @_rule_handler
    def _handle_blueprint_registration(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Warn when decorated Blueprint aliases are never registered."""
        unregistered_aliases = sorted(_collect_unregistered_blueprint_aliases(path))
        if not unregistered_aliases:
            return _create_result("pass", "All detected Blueprint aliases are registered")

        detail = "\n".join(
            [
                "Detected:",
                *[f"- {alias} = func.Blueprint()" for alias in unregistered_aliases],
                *[f"- @{alias}.route(...)" for alias in unregistered_aliases],
                "",
                "Missing:",
                *[f"- app.register_functions({alias})" for alias in unregistered_aliases],
                "",
                "Fix: add the missing `app.register_functions(<alias>)` call(s)"
                " in function_app.py.",
            ]
        )
        return _create_result("fail", detail)


    @_rule_handler
    def _handle_decorator_order(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Warn when decorators are stacked outside their expected inner order."""
        condition = rule.get("condition", {})
        # ``decorators`` lists the expected order outermost-first. Only the first
        # and last entries are surfaced in the fix message below, which is exact
        # for the shipped two-element pairing.
        expected_order = condition.get("decorators") or ["with_context", "validate_http"]
        inverted = _collect_inverted_decorator_order(path, expected_order)

        if not inverted:
            return _create_result("pass", "No inverted decorator order detected")
        detail = "\n".join(
            [
                "Inverted decorator order detected:",
                *[
                    f"- {fn}: @{expected_order[-1]} is outside @{expected_order[0]}"
                    for fn in inverted[:10]
                ],
                "",
                "Fix: reorder to @app.route -> "
                + " -> ".join(f"@{name}" for name in expected_order)
                + f" ({expected_order[-1]} innermost).",

            ]
        )
        return _create_result("fail", detail)

    @_rule_handler
    def _handle_endpoint_metadata(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Warn when route handlers lack @validate_http in a validation-enabled project."""
        if not _project_declares_validation_dep(path):
            return _create_result(
                "pass", "azure-functions-validation not declared; endpoint metadata check skipped"
            )
        uncovered = _collect_routes_missing_validate_http(path)
        if not uncovered:
            return _create_result("pass", "All route handlers expose endpoint metadata")
        detail = "\n".join(
            [
                "Route handlers missing @validate_http (no endpoint metadata):",
                *[f"- {fn}" for fn in uncovered[:10]],
                "",
                "Fix: add @validate_http so the route emits OpenAPI endpoint metadata.",
            ]
        )
        return _create_result("fail", detail)

    @_rule_handler
    def _handle_openapi_version_mixing(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Detect when both OpenAPI 3.0 and 3.1 signals appear in one project."""
        v30, v31 = _collect_openapi_version_mixing(path)
        if not (v30 and v31):
            return _create_result("pass", "No OpenAPI version mixing detected")
        detail = "\n".join(
            [
                "Mixed OpenAPI version signals detected:",
                f"- 3.0 signals: {', '.join(sorted(v30))}",
                f"- 3.1 signals: {', '.join(sorted(v31))}",
                "",
                "Fix: standardise on a single OpenAPI version across the project.",
            ]
        )
        return _create_result("fail", detail)

    @_rule_handler
    def _handle_scan_before_spec(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Detect when the OpenAPI spec is built before endpoints are scanned."""
        condition = rule.get("condition", {}) or {}
        scan_names = set(
            condition.get("scan_names")
or [
"scan",
                "scan_endpoints",
                "scan_endpoint_metadata",
"discover_endpoints",
"register_functions",
"register_blueprints",
]
)
        spec_names = set(
            condition.get("spec_names")
or [
"build_spec",
"build",
                "get_openapi_spec",
                "get_openapi_json",
                "get_openapi_yaml",
                "generate_openapi_spec",
                "generate_openapi_report",
"generate_spec",
"create_spec",
]
)
        violations = _collect_scan_before_spec(path, scan_names, spec_names)
        if not violations:
            return _create_result("pass", "No spec-before-scan ordering issues detected")
        detail = "\n".join(
            [
                "OpenAPI spec built before endpoints were scanned:",
                *[f"- {loc}" for loc in violations[:10]],
                "",
                "Fix: call the endpoint scan/registration before building the spec.",
            ]
        )
        return _create_result("fail", detail)

    @_rule_handler
    def _handle_langgraph_anonymous_auth(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Detect when a LangGraph project exposes routes with anonymous auth."""
        if not _project_imports_langgraph(path):
            return _create_result("pass", "langgraph not imported; anonymous auth check skipped")
        condition = rule.get("condition", {}) or {}
        flag_missing = bool(condition.get("flag_missing_auth_level", False))
        flagged = _collect_anonymous_auth_routes(path, flag_missing)
        if not flagged:
            return _create_result("pass", "No anonymous-auth routes detected in LangGraph project")
        detail = "\n".join(
            [
                "Anonymous-auth routes detected in a LangGraph project:",
                *[f"- {loc}" for loc in flagged[:10]],
                "",
                "Fix: require authentication (e.g. AuthLevel.FUNCTION) for LangGraph routes.",
            ]
        )
        return _create_result("fail", detail)

    @_rule_handler
    def _handle_durable_nondeterminism(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Fail when orchestrator functions call nondeterministic APIs."""
        condition = rule.get("condition", {}) or {}
        blocklist = set(
            condition.get("blocklist")
            or [
                "datetime.now",
                "datetime.utcnow",
                "datetime.today",
                "time.time",
                "time.monotonic",
                "time.perf_counter",
                "random.random",
                "random.randint",
                "random.uniform",
                "random.choice",
                "random.randrange",
                "random.getrandbits",
                "uuid.uuid4",
                "uuid.uuid1",
                "requests.get",
                "requests.post",
                "requests.put",
                "requests.delete",
                "requests.patch",
                "requests.head",
                "open",
                "os.getenv",
                "os.environ.get",
            ]
        )
        decorator_names = set(
            condition.get("decorator_names")
            or ["orchestration_trigger", "entity_trigger"]
        )
        flagged = _collect_orchestrator_nondeterminism(path, blocklist, decorator_names)
        if not flagged:
            return _create_result("pass", "No nondeterministic calls detected in orchestrators")
        detail = "\n".join(
            [
                "Nondeterministic calls detected in orchestrator/entity functions:",
                *[f"- {loc}" for loc in flagged[:10]],
                "",
                "Fix: move nondeterministic work into activity functions.",
            ]
        )
        return _create_result("fail", detail)

    @_rule_handler
    def _handle_unsupported_metadata_version(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Detect when metadata declares an unsupported version."""
        condition = rule.get("condition", {}) or {}
        files = list(condition.get("files") or ["*.meta.json", "extensions.json"])
        fields = list(condition.get("fields") or ["metadataVersion", "metadata_version"])
        supported = list(condition.get("supported_versions") or [])
        if not supported:
            return _create_result(
                "pass", "No supported_versions configured; metadata version check skipped"
            )
        found = _collect_unsupported_metadata_versions(path, files, fields, supported)
        if not found:
            return _create_result("pass", "No unsupported metadata versions detected")
        detail = "\n".join(
            [
                "Unsupported metadata versions detected:",
                *[f"- {src} = {ver}" for src, ver in found[:10]],
                "",
                f"Fix: use a supported version ({', '.join(supported) or 'see docs'}).",
            ]
        )
        return _create_result("fail", detail)


# Global registry instance
_registry = HandlerRegistry()


def generic_handler(
    rule: Rule, path: Path, context: Optional[RuleContext] = None
) -> HandlerResult:
    """
    Execute a diagnostic rule based on its type and condition.

    This function maintains backward compatibility while delegating to the registry.

    Args:
        rule: The diagnostic rule to execute.
        path: Path to the Azure Functions project.

    Returns:
        A dictionary with the status and detail of the check.
    """
    return _registry.handle(rule, path, context)
