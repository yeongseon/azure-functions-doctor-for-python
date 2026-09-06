"""Ecosystem-integration handlers (domain module, issue #387).

Split out of handlers/registry.py; registration/dispatch stays there.
"""

from pathlib import Path
from typing import Optional

from azure_functions_doctor.handlers._helpers import (
    HandlerResult,
    Rule,
    RuleContext,
    _collect_anonymous_auth_routes,
    _collect_openapi_version_mixing,
    _collect_routes_missing_validate_http_locations,
    _collect_scan_before_spec,
    _collect_unsupported_metadata_versions,
    _create_result,
    _project_activates_trace_context,
    _project_declares_opentelemetry,
    _project_declares_validation_dep,
    _project_imports_langgraph,
    _rule_handler,
)


class IntegrationHandlers:
    """Ecosystem-integration handlers.

    Endpoint metadata, OpenAPI versioning, LangGraph auth, metadata versions,
    OTel activation.
    """

    @_rule_handler
    def _handle_endpoint_metadata(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Warn when route handlers lack @validate_http in a validation-enabled project."""
        if not _project_declares_validation_dep(path):
            return _create_result(
                "skip", "azure-functions-validation not declared; endpoint metadata check skipped"
            )
        uncovered = _collect_routes_missing_validate_http_locations(path)
        if not uncovered:
            return _create_result("pass", "All route handlers expose endpoint metadata")
        detail = "\n".join(
            [
                "Route handlers missing @validate_http (no endpoint metadata):",
                *[f"- {label}" for label, _ln, _end, _col in uncovered[:10]],
                "",
                "Fix: add @validate_http so the route emits OpenAPI endpoint metadata.",
            ]
        )
        first_label, first_line, first_end_line, first_column = uncovered[0]
        first_file = first_label.rsplit(":", 1)[0]
        return _create_result(
            "fail",
            detail,
            file=first_file,
            line=first_line,
            end_line=first_end_line,
            column=first_column,
        )

    @_rule_handler
    def _handle_openapi_version_mixing(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Detect when two or more OpenAPI versions (3.0/3.1/3.2) appear together."""
        signals = _collect_openapi_version_mixing(path)
        present = {version: sigs for version, sigs in signals.items() if sigs}
        if len(present) < 2:
            return _create_result("pass", "No OpenAPI version mixing detected")
        detail = "\n".join(
            [
                "Mixed OpenAPI version signals detected:",
                *[
                    f"- {version} signals: {', '.join(sorted(sigs))}"
                    for version, sigs in sorted(present.items())
                ],
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
            return _create_result("skip", "langgraph not imported; anonymous auth check skipped")
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
                "skip", "No supported_versions configured; metadata version check skipped"
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

    @_rule_handler
    def _handle_otel_activation(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Warn when the project opts into logging OTel trace-context activation but
        does not declare an ``opentelemetry`` distribution.

        ``azure-functions-logging`` stays silent at runtime when activation is
        requested without OpenTelemetry installed, so doctor surfaces the mismatch.
        """
        activations = _project_activates_trace_context(path)
        if not activations:
            return _create_result(
                "skip", "No OTel trace-context activation requested; check skipped"
            )
        if _project_declares_opentelemetry(path):
            return _create_result(
                "pass", "Trace-context activation requested and opentelemetry is declared"
            )
        detail = "\n".join(
            [
                "Trace-context activation requested without an opentelemetry dependency:",
                *[f"- {loc}" for loc in activations[:10]],
                "",
                "Fix: install the azure-functions-logging[otel] extra (or an "
                "opentelemetry-* package), or disable activate_trace_context.",
            ]
        )
        return _create_result("fail", detail)
