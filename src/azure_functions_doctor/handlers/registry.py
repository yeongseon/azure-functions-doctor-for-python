from datetime import date
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
from typing import Callable, Dict, List, Optional

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion
from packaging.version import parse as parse_version

from azure_functions_doctor.compatibility import Catalog, Fact, load_catalog
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
    _collect_routes_missing_validate_http_locations,
    _collect_scan_before_spec,
    _collect_unregistered_blueprint_aliases,
    _collect_unsupported_metadata_versions,
    _create_result,
    _detect_native_dependency_risks,
    _handle_specific_exceptions,
    _iter_project_py_contents,
    _parse_requirements_names,
    _project_activates_trace_context,
    _project_declares_opentelemetry,
    _project_declares_validation_dep,
    _project_imports_langgraph,
    _read_project_python_file,
    _resolve_host_json_path,
    _resolve_host_json_pointer,
    _rule_handler,
    _source_contains_ast,
    is_local_prebuilt_deployment,
    logger,
    parse_compare_version,
    parse_package,
    parse_source_code,
    parse_target,
    pyproject_declares_dependencies,
    pyproject_dependency_names,
)
from azure_functions_doctor.target_resolver import (
    PYTHON_HOSTING_PLAN_MATRIX,
    SUPPORTED_PYTHON_VERSIONS,
    is_supported_python_for_plan,
is_supported_python_target,
    resolve_python_target,
    resolve_target_value,
)

# Issue #343: a Python runtime is flagged "retiring soon" (WARN) when its
# published Azure Functions end-of-support date falls within this many days of
# today. Beyond the window the runtime is "supported" (PASS); once the date has
# passed it is "unsupported" (FAIL). Comparison uses the last calendar day the
# source guarantees (month/year precision is widened, never narrowed), so the
# tool never asserts a finer date than Microsoft publishes.
PYTHON_RETIRING_SOON_WINDOW_DAYS = 180


def _evaluate_python_lifecycle(
    version: str,
    *,
    today: date,
    catalog: Optional[Catalog] = None,
) -> HandlerResult:
    """Classify a Python ``version`` against its catalog end-of-support date.

    Returns a :class:`HandlerResult` whose ``status``/``severity``/``gate`` encode
    one of three deterministic states:

    * **supported** -> ``pass``
    * **retiring soon** (within :data:`PYTHON_RETIRING_SOON_WINDOW_DAYS`) ->
      failing status refined to ``warning`` severity, non-gating
    * **unsupported** (past end-of-support) -> failing status refined to
      ``error`` severity, gating

    Dates are rendered at the precision the catalog publishes (e.g.
    ``"October 2026"``); no day-level countdown is synthesized. Auditable
    evidence (source URL, ``last_verified``, ``catalog_version``) is attached so
    the finding is offline-verifiable per the Finding Contract v2 (issue #348).
    """
    cat = load_catalog() if catalog is None else catalog
    fact = cat.python_lifecycle_fact(version)
    if fact is None or fact.support_end is None:
        # No lifecycle data for this version (e.g. a version outside the
        # supported band); check_python_version owns that failure, so stay quiet.
        return _create_result("pass", f"Python {version}: no catalog lifecycle data")

    eos = fact.support_end
    rendered = eos.render()
    end = eos.end_date()
    last_verified = fact.last_verified or cat.last_verified

    if end is not None and today > end:
        status, severity, gate = "fail", "error", True
        detail = (
            f"Python {version} is past Azure Functions end-of-support "
            f"(ended {rendered}); upgrade to a supported Python (3.12+)."
        )
    elif end is not None and (end - today).days <= PYTHON_RETIRING_SOON_WINDOW_DAYS:
        status, severity, gate = "fail", "warning", False
        detail = (
            f"Python {version} support is expected to end in {rendered}; "
            f"plan an upgrade to a newer Python (3.12+) before then."
        )
    else:
        status, severity, gate = "pass", "info", False
        detail = (
            f"Python {version} is supported; Azure Functions support is "
            f"expected to end in {rendered}."
        )

    result = _create_result(status, detail)
    result["severity"] = severity
    result["gate"] = gate
    result["evidence"] = detail
    result["expected"] = "A supported Azure Functions Python runtime (3.12+)"
    result["actual"] = f"Python {version} (support ends {rendered})"
    if fact.source_url:
        result["source_url"] = fact.source_url
    if last_verified:
        result["last_verified"] = last_verified
    if cat.catalog_version:
        result["catalog_version"] = cat.catalog_version
    return result


# Issue #344: the only GA Azure Functions runtime major version. v1 is a legacy
# runtime (C#/.NET Framework only, incompatible with Python) and v2/v3 are out of
# support.
FUNCTIONS_RUNTIME_CURRENT = "4.x"

# Hosting-plan retirement reuses the Python runtime "retiring soon" window: a
# scheduled retirement WARNs inside the window, is an informational note beyond
# it, and FAILs once the date has passed.
HOSTING_PLAN_RETIRING_SOON_WINDOW_DAYS = 180


def _normalize_functions_runtime(ext_version: Optional[str]) -> Optional[str]:
    """Map a ``FUNCTIONS_EXTENSION_VERSION`` value to a ``"N.x"`` runtime key.

    Accepts the pinned forms Azure uses (``"~4"``, ``"4"``, ``"4.0.1"``) and
    returns ``"4.x"``. Returns ``None`` when no major version can be parsed.
    """
    if not ext_version:
        return None
    cleaned = ext_version.strip().lstrip("~")
    match = re.match(r"(\d+)", cleaned)
    if match is None:
        return None
    return f"{int(match.group(1))}.x"


def _attach_catalog_evidence(
    result: HandlerResult,
    fact: Fact,
    catalog: Catalog,
    *,
    detail: str,
    expected: str,
    actual: str,
) -> None:
    """Attach Finding Contract v2 evidence (issue #348) sourced from a catalog fact."""
    result["evidence"] = detail
    result["expected"] = expected
    result["actual"] = actual
    if fact.source_url:
        result["source_url"] = fact.source_url
    last_verified = fact.last_verified or catalog.last_verified
    if last_verified:
        result["last_verified"] = last_verified
    if catalog.catalog_version:
        result["catalog_version"] = catalog.catalog_version


def _evaluate_functions_runtime_lifecycle(
    runtime_version: Optional[str],
    hosting_plan: Optional[str],
    *,
    today: date,
    catalog: Optional[Catalog] = None,
) -> HandlerResult:
    """Classify the Azure Functions runtime major version for a Python app.

    Compatibility is judged first (issue #344): runtime v1 is a legacy runtime
    for C#/.NET Framework apps and is incompatible with a Python target
    regardless of its end-of-support date, so it FAILs on a compatibility basis
    with an added lifecycle note. v2/v3 are out of support (FAIL); v3 on Linux
    Consumption stops running on a published date (emphasised FAIL). v4 is the
    current GA runtime (PASS). An undeterminable runtime SKIPs.

    ``today`` is accepted for deterministic testing though the current states are
    compatibility-driven rather than window-driven.
    """
    cat = load_catalog() if catalog is None else catalog
    runtime = _normalize_functions_runtime(runtime_version)
    if runtime is None:
        return _create_result(
            "skip",
            "Azure Functions runtime version could not be determined from infra "
            "or app settings; check skipped.",
        )

    if runtime == FUNCTIONS_RUNTIME_CURRENT:
        detail = "Azure Functions runtime v4 is the current GA runtime."
        result = _create_result("pass", detail)
        result["severity"] = "info"
        result["gate"] = False
        fact = cat.functions_runtime_fact(runtime)
        if fact is not None:
            _attach_catalog_evidence(
                result,
                fact,
                cat,
                detail=detail,
                expected="Azure Functions runtime v4 (~4)",
                actual="Azure Functions runtime v4",
            )
        return result

    if runtime == "1.x":
        fact = cat.functions_runtime_fact(runtime)
        note = ""
        if fact is not None and fact.support_end is not None:
            note = f" Runtime v1 support ends {fact.support_end.render()}."
        detail = (
            "Azure Functions runtime v1 is not compatible with Python "
            "(v1 supports only C#/.NET Framework apps); migrate to runtime v4." + note
        )
        result = _create_result("fail", detail)
        result["severity"] = "error"
        result["gate"] = True
        if fact is not None:
            _attach_catalog_evidence(
                result,
                fact,
                cat,
                detail=detail,
                expected="Azure Functions runtime v4 (~4) for a Python app",
                actual="Azure Functions runtime v1 (incompatible with Python)",
            )
        return result

    if runtime == "3.x" and hosting_plan == "linux-consumption":
        fact = cat.functions_runtime_plan_fact(runtime, hosting_plan)
        if fact is not None:
            stop = (
                fact.support_end.render()
                if fact.support_end is not None
                else "the published date"
            )
            detail = (
                "Azure Functions runtime v3 apps on Linux Consumption stop "
                f"running after {stop}; migrate to runtime v4."
            )
            result = _create_result("fail", detail)
            result["severity"] = "error"
            result["gate"] = True
            _attach_catalog_evidence(
                result,
                fact,
                cat,
                detail=detail,
                expected="Azure Functions runtime v4 (~4)",
                actual="Azure Functions runtime v3 on Linux Consumption",
            )
            return result

    fact = cat.functions_runtime_fact(runtime)
    ended = ""
    if fact is not None and fact.support_end is not None:
        ended = f" (ended {fact.support_end.render()})"
    major = runtime.split(".")[0]
    detail = (
        f"Azure Functions runtime v{major} is out of support{ended}; "
        "migrate to runtime v4."
    )
    result = _create_result("fail", detail)
    result["severity"] = "error"
    result["gate"] = True
    if fact is not None:
        _attach_catalog_evidence(
            result,
            fact,
            cat,
            detail=detail,
            expected="Azure Functions runtime v4 (~4)",
            actual=f"Azure Functions runtime v{major}",
        )
    return result


def _evaluate_hosting_plan_lifecycle(
    hosting_plan: Optional[str],
    *,
    today: date,
    catalog: Optional[Catalog] = None,
) -> HandlerResult:
    """Classify a hosting plan against its published retirement date (issue #344).

    Linux Consumption is retiring on a published date: informational while the
    date is far off, a WARN inside the retiring-soon window, and a FAIL once the
    date has passed. Plans with no published retirement PASS. An undeterminable
    plan SKIPs.
    """
    cat = load_catalog() if catalog is None else catalog
    if not hosting_plan:
        return _create_result(
            "skip",
            "Hosting plan could not be determined from infra config; check skipped.",
        )

    fact = cat.hosting_plan_lifecycle_fact(hosting_plan)
    if fact is None or fact.support_end is None:
        return _create_result(
            "pass",
            f"Hosting plan '{hosting_plan}' has no published retirement date.",
        )

    rendered = fact.support_end.render()
    end = fact.support_end.end_date()
    if end is not None and today > end:
        status, severity, gate = "fail", "error", True
        detail = (
            f"The '{hosting_plan}' hosting plan retired on {rendered}; "
            "migrate to Flex Consumption."
        )
    elif end is not None and (end - today).days <= HOSTING_PLAN_RETIRING_SOON_WINDOW_DAYS:
        status, severity, gate = "fail", "warning", False
        detail = (
            f"The '{hosting_plan}' hosting plan is retiring on {rendered}; "
            "migrate to Flex Consumption before then."
        )
    else:
        status, severity, gate = "pass", "info", False
        detail = (
            f"The '{hosting_plan}' hosting plan is supported; it retires on "
            f"{rendered}. Consider Flex Consumption for new workloads."
        )

    result = _create_result(status, detail)
    result["severity"] = severity
    result["gate"] = gate
    _attach_catalog_evidence(
        result,
        fact,
        cat,
        detail=detail,
        expected="A hosting plan with no near-term retirement (e.g. Flex Consumption)",
        actual=f"{hosting_plan} (retires {rendered})",
    )
    return result


# Issue #345: Flex Consumption declares its runtime under
# ``functionAppConfig.runtime`` (name/version) and ignores ``linuxFxVersion``.
# The canonical plan name matches deploy_config.PLAN_FLEX_CONSUMPTION.
FLEX_CONSUMPTION_PLAN = "flex-consumption"

_LINUX_FX_KEY_RE = re.compile(r"linuxFxVersion", re.IGNORECASE)


def _infra_declares_linux_fx_version(path: Path) -> bool:
    """Return ``True`` when any infra file declares a ``linuxFxVersion`` key.

    Flex Consumption ignores ``linuxFxVersion``; its presence on a Flex app is a
    misconfiguration worth surfacing. ``local.settings.json`` is a local signal,
    not deployable infrastructure, so it is excluded.
    """
    for pattern in ("*.bicep", "*.json"):
        for infra in sorted(path.rglob(pattern)):
            if infra.name == "local.settings.json":
                continue
            try:
                text = infra.read_text(encoding="utf-8")
            except OSError:
                continue
            if _LINUX_FX_KEY_RE.search(text):
                return True
    return False


def _evaluate_flex_runtime_config(
    hosting_plan: Optional[str],
    runtime_name: Optional[str],
    runtime_version: Optional[str],
    *,
    linux_fx_present: bool,
) -> HandlerResult:
    """Validate a Flex Consumption app's ``functionAppConfig.runtime`` (issue #345).

    Only Flex apps are in scope (others SKIP). A ``linuxFxVersion`` declaration on
    a Flex app is a misconfiguration (WARN) because Flex ignores it. Otherwise the
    declared Python runtime version is validated against the Flex hosting-plan
    matrix (Flex supports through 3.14); an undeclared or non-Python runtime SKIPs.
    """
    if hosting_plan != FLEX_CONSUMPTION_PLAN:
        return _create_result(
            "skip",
            "Not a Flex Consumption app; functionAppConfig.runtime check skipped.",
        )

    if linux_fx_present:
        detail = (
            "linuxFxVersion is declared on a Flex Consumption app, which ignores "
            "it; declare the runtime under functionAppConfig.runtime (name/version) "
            "instead."
        )
        result = _create_result("fail", detail)
        result["severity"] = "warning"
        result["gate"] = False
        result["expected"] = "Runtime declared under functionAppConfig.runtime"
        result["actual"] = "linuxFxVersion declared on a Flex Consumption app"
        return result

    if runtime_name is None or runtime_version is None:
        return _create_result(
            "skip",
            "Flex Consumption app declares no functionAppConfig.runtime "
            "name/version; check skipped.",
        )

    if runtime_name != "python":
        return _create_result(
            "skip",
            f"Flex Consumption runtime is '{runtime_name}', not Python; "
            "Python runtime check skipped.",
        )

    if is_supported_python_for_plan(runtime_version, FLEX_CONSUMPTION_PLAN):
        return _create_result(
            "pass",
            f"Flex Consumption runtime Python {runtime_version} is supported.",
        )

    allowed = PYTHON_HOSTING_PLAN_MATRIX.get(FLEX_CONSUMPTION_PLAN, SUPPORTED_PYTHON_VERSIONS)
    supported_range = f"{allowed[0]}\u2013{allowed[-1]}" if allowed else "the supported set"
    detail = (
        f"Flex Consumption runtime Python {runtime_version} is not supported; "
        f"target a supported Python runtime ({supported_range})."
    )
    result = _create_result("fail", detail)
    result["severity"] = "error"
    result["gate"] = True
    result["expected"] = f"A supported Flex Consumption Python runtime ({supported_range})"
    result["actual"] = f"functionAppConfig.runtime = python {runtime_version}"
    return result


def _evaluate_flex_extension_version(ext_value: Optional[str]) -> HandlerResult:
    """Classify FUNCTIONS_EXTENSION_VERSION for a Flex Consumption app (issue #346).

    Flex Consumption does not support the ``FUNCTIONS_EXTENSION_VERSION`` app
    setting: it only runs on runtime v4 and the value is backend-managed. A
    missing value is therefore correct (SKIP), while an explicit value is a
    deprecated/unsupported setting worth surfacing (WARN).
    """
    if ext_value is None:
        return _create_result(
            "skip",
            "FUNCTIONS_EXTENSION_VERSION is not required on Flex Consumption "
            "(the runtime is v4 and backend-managed); check skipped.",
        )
    detail = (
        f"FUNCTIONS_EXTENSION_VERSION is set to '{ext_value}' but is not supported "
        "on Flex Consumption; the runtime is v4 and backend-managed. Remove the setting."
    )
    result = _create_result("fail", detail)
    result["severity"] = "warning"
    result["gate"] = False
    result["expected"] = "No FUNCTIONS_EXTENSION_VERSION on Flex Consumption"
    result["actual"] = f"FUNCTIONS_EXTENSION_VERSION = {ext_value}"
    return result


class HandlerRegistry:
    """Registry for diagnostic check handlers with individual handler methods."""

    def __init__(self) -> None:
        self._handlers: Dict[str, Callable[[Rule, Path, Optional[RuleContext]], HandlerResult]] = {
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
            current_version, source = resolve_python_target(path, override=target_python)
            tool_runtime = (
                f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            )
            current = parse_version(current_version)
            expected = parse_version(str(value))
            operator_passed = {
                ">=": current >= expected,
                "<=": current <= expected,
                "==": current == expected,
                ">": current > expected,
                "<": current < expected,
            }.get(operator, False)
            supported = is_supported_python_target(current_version)
            passed = operator_passed and supported
            supported_range = f"{SUPPORTED_PYTHON_VERSIONS[0]}\u2013{SUPPORTED_PYTHON_VERSIONS[-1]}"
            if source == "override":
                detail = (
                    f"Target Python: {current_version} (override) "
                    f"\u2014 Tool runtime: {tool_runtime}"
                )
            elif source == "tool-runtime":
                detail = f"Python {current_version} (tool runtime, {operator}{value})"
            else:
                detail = (
                    f"Target Python: {current_version} ({source}, {operator}{value}) "
                    f"\u2014 Tool runtime: {tool_runtime}"
                )
            if not supported:
                detail += (
                    f" \u2014 unsupported target; Azure Functions supports Python {supported_range}"
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
    def _handle_python_runtime_lifecycle(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Flag a target Python runtime that is retiring soon or unsupported.

        Reads end-of-support dates from the compatibility catalog (never
        hardcoded) and renders them at the catalog's published precision, so a
        month-precision source yields e.g. "October 2026" with no invented day
        or countdown.
        """
        target_python = context.get("target_python") if context is not None else None
        version, _source = resolve_python_target(path, override=target_python)
        return _evaluate_python_lifecycle(version, today=date.today())

    @_rule_handler
    def _handle_functions_runtime_lifecycle(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Check the Azure Functions runtime major version for a Python app.

        The runtime major version is read from the resolved target config's
        ``FUNCTIONS_EXTENSION_VERSION`` (e.g. ``~4``); v1 is judged incompatible
        with Python first, with lifecycle dates sourced from the catalog.
        """
        target_config = context.get("target_config") if context is not None else None
        runtime_version: Optional[str] = None
        hosting_plan: Optional[str] = None
        if target_config is not None:
            runtime_version = target_config.extension_version.value
            hosting_plan = target_config.hosting_plan.value
        return _evaluate_functions_runtime_lifecycle(
            runtime_version, hosting_plan, today=date.today()
        )

    @_rule_handler
    def _handle_hosting_plan_lifecycle(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Check the resolved hosting plan against its published retirement date."""
        target_config = context.get("target_config") if context is not None else None
        hosting_plan = (
            target_config.hosting_plan.value if target_config is not None else None
        )
        return _evaluate_hosting_plan_lifecycle(hosting_plan, today=date.today())

    @_rule_handler
    def _handle_flex_runtime_config(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Validate a Flex Consumption app's ``functionAppConfig.runtime`` (issue #345).

        Flex Consumption declares its runtime under ``functionAppConfig.runtime``
        (name/version) rather than ``linuxFxVersion``. This check is scoped to Flex
        apps: it WARNs when a legacy ``linuxFxVersion`` is present (Flex ignores it)
        and otherwise validates the declared Python runtime against the Flex
        hosting-plan matrix.
        """
        target_config = context.get("target_config") if context is not None else None
        hosting_plan: Optional[str] = None
        runtime_name: Optional[str] = None
        runtime_version: Optional[str] = None
        if target_config is not None:
            hosting_plan = target_config.hosting_plan.value
            runtime_name = target_config.runtime_name.value
            runtime_version = target_config.runtime_version.value
        linux_fx_present = (
            hosting_plan == FLEX_CONSUMPTION_PLAN
            and _infra_declares_linux_fx_version(path)
        )
        return _evaluate_flex_runtime_config(
            hosting_plan,
            runtime_name,
            runtime_version,
            linux_fx_present=linux_fx_present,
        )

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
        rel_target = target.replace("\\", "/")
        exists = file_path.is_file()
        detail = f"{file_path} {'exists' if exists else 'not found'}"
        if not exists and not rule.get("required", True):
            detail += " (optional)"
        return _create_result("pass" if exists else "fail", detail, file=rel_target)

    @_rule_handler
    def _handle_dependency_manifest(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Validate the dependency manifest against the deployment mode.

        Azure Functions performs a *remote build* by default, installing
        dependencies from ``requirements.txt`` on the server. A pyproject-only
        project therefore passes only for a local/prebuilt deployment; under
        remote build a missing ``requirements.txt`` is flagged because the
        server never reads ``pyproject.toml``.
        """
        condition = rule.get("condition", {}) or {}
        target = parse_target(condition) or "requirements.txt"
        req_path = path / target
        if req_path.is_file():
            return _create_result("pass", f"{req_path} exists")
        if pyproject_declares_dependencies(path):
            if is_local_prebuilt_deployment(path, context):
                return _create_result(
                    "pass",
                    f"{req_path} not found; dependencies declared in pyproject.toml "
                    "(local/prebuilt deployment)",
                )
            detail = (
                f"{req_path} not found; dependencies are only declared in "
                "pyproject.toml. Azure remote build installs from requirements.txt, "
                "so generate one (e.g. 'pip freeze > requirements.txt') or deploy "
                "with a local/prebuilt build (--deployment-mode local)."
            )
            if not rule.get("required", True):
                detail += " (optional)"
            return _create_result("fail", detail)
        detail = f"{req_path} not found and pyproject.toml declares no dependencies"
        if not rule.get("required", True):
            detail += " (optional)"
        return _create_result("fail", detail)

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
        normalized_target = canonicalize_name(package_name)
        req_path = path / Path(req_file)
        if not req_path.exists():
            # No requirements.txt: fall back to pyproject.toml. This is valid
            # only for a local/prebuilt deployment; remote build reads
            # requirements.txt, never pyproject.toml.
            if normalized_target in pyproject_dependency_names(path):
                if is_local_prebuilt_deployment(path, context):
                    return _create_result(
                        "pass",
                        f"Package '{package_name}' declared in pyproject.toml "
                        "(local/prebuilt deployment)",
                    )
                return _create_result(
                    "fail",
                    f"Package '{package_name}' is only declared in pyproject.toml; "
                    "Azure remote build installs from requirements.txt. Add it there "
                    "or deploy with a local/prebuilt build (--deployment-mode local).",
                )
            return _create_result(
                "fail",
                f"{req_path} not found and '{package_name}' not declared in pyproject.toml",
            )
        try:
            content = req_path.read_text(encoding="utf-8")
        except Exception as exc:
            return _handle_specific_exceptions(f"reading {req_file}", exc)
        normalized = _parse_requirements_names(content)
        declared = normalized_target in normalized
        if not declared and normalized_target in pyproject_dependency_names(path):
            if is_local_prebuilt_deployment(path, context):
                return _create_result(
                    "pass",
                    f"Package '{package_name}' declared in pyproject.toml "
                    "(local/prebuilt deployment)",
                )
            return _create_result(
                "fail",
                f"Package '{package_name}' is only declared in pyproject.toml; "
                "Azure remote build installs from requirements.txt. Add it there "
                "or deploy with a local/prebuilt build (--deployment-mode local).",
            )
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
            return _create_result("skip", f"{req_file} not found; check skipped")
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
            return _create_result("skip", "No Durable Functions usage detected; check skipped")

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
        """Detect ASGI/WSGI callable exposure in source files (basic heuristics).

        A plain decorator-based ``FunctionApp`` project has no ASGI/WSGI app and
        should not be warned, so the check **skips** when there is no framework
        signal at all. When a framework is present but its callable is not wired
        into Azure Functions it returns ``fail`` (surfaced as a warning by the
        doctor only because this rule is optional); a correctly exposed callable
        passes.
        """
        # Azure Functions wiring that actually exposes an ASGI/WSGI callable.
        exposure_patterns = [
            r"\bAsgiFunctionApp\s*\(",
            r"\bWsgiFunctionApp\s*\(",
            r"\bAsgiMiddleware\s*\(",
            r"\bWsgiMiddleware\s*\(",
        ]
        # Presence of an ASGI/WSGI framework (import or instantiation).
        framework_patterns = [
            r"\bFastAPI\s*\(|\bStarlette\s*\(|\bFlask\s*\(|\bQuart\s*\(",
            r"\b(?:import|from)\s+(?:fastapi|starlette|flask|quart)\b",
            r"ASGIApp|WSGIApp|asgi_app|wsgi_app",
        ]

        exposure_hits: List[str] = []
        framework_hits: List[str] = []
        try:
            for py_file in path.rglob("*.py"):
                content = _read_project_python_file(py_file)
                if content is None:
                    continue
                rel = py_file.relative_to(path)
                for pat in exposure_patterns:
                    if re.search(pat, content):
                        exposure_hits.append(f"{rel}:{pat}")
                        break
                for pat in framework_patterns:
                    if re.search(pat, content):
                        framework_hits.append(f"{rel}:{pat}")
                        break
        except Exception as exc:
            return _handle_specific_exceptions("scanning for ASGI/WSGI callables", exc)

        if exposure_hits:
            return _create_result(
                "pass", f"Detected ASGI/WSGI callable exposure: {exposure_hits[:3]}"
            )

        if framework_hits:
            return _create_result(
                "fail",
                "ASGI/WSGI framework detected but no callable is exposed via "
                "AsgiFunctionApp/WsgiFunctionApp (or AsgiMiddleware/WsgiMiddleware); "
                f"wire it into Azure Functions: {framework_hits[:3]}",
            )

        return _create_result(
            "skip",
            "No ASGI/WSGI framework detected; plain FunctionApp project.",
        )

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
    def _handle_app_insights_connection(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Validate Application Insights connection configuration.

        Instrumentation-key ingestion ended 2025-03-31, so a connection string
        (``APPLICATIONINSIGHTS_CONNECTION_STRING``) is now required. A legacy
        instrumentation key (``APPINSIGHTS_INSTRUMENTATIONKEY`` or
        ``host.json:instrumentationKey``) is treated as stale, and
        ``APPLICATIONINSIGHTS_AUTHENTICATION_STRING`` is recognised for Entra
        (AAD) authentication.
        """
        conn = (os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING") or "").strip()
        auth = (os.getenv("APPLICATIONINSIGHTS_AUTHENTICATION_STRING") or "").strip()
        ik_env = (os.getenv("APPINSIGHTS_INSTRUMENTATIONKEY") or "").strip()

        ik_host = False
        host_path = path / "host.json"
        if host_path.exists():
            try:
                data = json.loads(host_path.read_text(encoding="utf-8"))
                node = _resolve_host_json_pointer(data, ["instrumentationKey"])
                ik_host = node is not _HOST_JSON_MISSING and node is not None
            except json.JSONDecodeError as exc:
                logger.debug(f"Skip invalid host.json while checking App Insights: {exc}")

        has_ik = bool(ik_env) or ik_host
        auth_note = (
            " Entra auth via APPLICATIONINSIGHTS_AUTHENTICATION_STRING is configured."
            if auth
            else ""
        )

        if conn:
            if has_ik:
                return _create_result(
                    "fail",
                    "Connection string is set, but a legacy instrumentation key is "
                    "also configured; remove it (instrumentation-key ingestion ended "
                    "2025-03-31)." + auth_note,
                )
            return _create_result(
                "pass",
                "Application Insights connection string configured." + auth_note,
            )

        if has_ik:
            return _create_result(
                "fail",
                "Only a legacy Application Insights instrumentation key is configured; "
                "instrumentation-key ingestion ended 2025-03-31. Set "
                "APPLICATIONINSIGHTS_CONNECTION_STRING instead." + auth_note,
            )

        if auth:
            return _create_result(
                "fail",
                "Application Insights Entra authentication "
                "(APPLICATIONINSIGHTS_AUTHENTICATION_STRING) is configured, but "
                "APPLICATIONINSIGHTS_CONNECTION_STRING is missing; set the connection "
                "string to enable telemetry.",
            )

        return _create_result(
            "fail",
            "Application Insights is not configured; set "
            "APPLICATIONINSIGHTS_CONNECTION_STRING to enable telemetry.",
        )

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
            return _create_result("skip", "local.settings.json not present; check skipped")

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
                "skip",
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

        version_str = str(bundle_version).strip()
        # Parse a NuGet-style range: [lower, upper) with */numeric version parts.
        range_match = re.match(
            r"^([\[(])\s*"
            r"(\d+)(?:\.(\d+|\*))?(?:\.(\d+|\*))?\s*,\s*"
            r"(\d+)(?:\.(\d+|\*))?(?:\.(\d+|\*))?\s*"
            r"([\])])$",
            version_str,
        )
        if range_match is None:
            return _create_result(
                "fail",
                f"extensionBundle version '{version_str}' is not a valid range;"
                " use the recommended [4.0.0, 5.0.0)",
            )

        lower_bracket = range_match.group(1)
        lower_major = int(range_match.group(2))
        upper_major = int(range_match.group(5))
        upper_minor_raw = range_match.group(6)
        upper_patch_raw = range_match.group(7)
        upper_bracket = range_match.group(8)

        if lower_major < 4:
            return _create_result(
                "fail",
                f"extensionBundle version '{version_str}' is below"
                " recommended v4 range — upgrade to [4.0.0, 5.0.0)",
            )

        # Valid v4: lower bound inclusive starting at major 4, upper bound
        # exclusive at exactly major 5 (i.e. [4.x, 5.0.0)).
        # The exclusive upper bound must be exactly 5.0.0. An absent minor/patch
        # component defaults to 0; a wildcard ('*') or non-zero component (e.g.
        # 5.1.0) widens the range beyond the recommended bound and must fail.
        upper_minor_zero = upper_minor_raw in (None, "0")
        upper_patch_zero = upper_patch_raw in (None, "0")
        is_valid_v4 = (
            lower_bracket == "["
            and lower_major == 4
            and upper_major == 5
            and upper_minor_zero
            and upper_patch_zero
            and upper_bracket == ")"
        )
        if is_valid_v4:
            return _create_result(
                "pass",
                f"extensionBundle uses recommended v4 range: {version_str}",
            )

        return _create_result(
            "fail",
            f"extensionBundle version '{version_str}' does not match the"
            " recommended v4 range [4.0.0, 5.0.0); the upper bound must be an"
            " exclusive 5.0.0",
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
            condition.get("decorator_names") or ["orchestration_trigger", "entity_trigger"]
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

    @_rule_handler
    def _handle_functions_extension_version(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Flag a missing, legacy, or non-v4 FUNCTIONS_EXTENSION_VERSION setting.

        The v1/v2/v3 runtimes are retired, so ``local.settings.json`` should pin
        the extension version to the current runtime (``~4`` by default). The
        expected value is overridable via ``condition.value``.

        Flex Consumption is special-cased (issue #346): it does not support this
        app setting at all, so a missing value SKIPs and an explicit value WARNs
        instead of following the legacy-runtime logic.
        """
        target_config = context.get("target_config") if context is not None else None
        if (
            target_config is not None
            and target_config.hosting_plan.value == FLEX_CONSUMPTION_PLAN
        ):
            return _evaluate_flex_extension_version(target_config.extension_version.value)
        condition = rule.get("condition", {}) or {}
        expected = str(condition.get("value") or "~4")
        settings_path = path / "local.settings.json"
        if not settings_path.exists():
            return _create_result(
                "skip",
                "local.settings.json not present; FUNCTIONS_EXTENSION_VERSION check skipped",
            )
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return _handle_specific_exceptions("reading local.settings.json", exc)
        values = data.get("Values") if isinstance(data, dict) else None
        current = values.get("FUNCTIONS_EXTENSION_VERSION") if isinstance(values, dict) else None
        if current is None:
            return _create_result(
                "fail",
                "FUNCTIONS_EXTENSION_VERSION is not set in local.settings.json; "
                f"pin it to '{expected}' for the current Azure Functions runtime.",
            )
        if str(current).strip() != expected:
            return _create_result(
                "fail",
                f"FUNCTIONS_EXTENSION_VERSION is '{current}', expected '{expected}'. "
                "Legacy runtimes (~1/~2/~3) are retired; target the v4 runtime.",
            )
        return _create_result("pass", f"FUNCTIONS_EXTENSION_VERSION is '{expected}'")

    @_rule_handler
    def _handle_linux_fx_version(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Validate any Python ``linuxFxVersion`` declared in infra (bicep) config.

        Scoped to legacy Linux / Premium / Dedicated / classic Consumption apps.
        Flex Consumption declares its runtime under ``functionAppConfig.runtime``
        and ignores ``linuxFxVersion``, so Flex apps SKIP here and are handled by
        ``check_flex_runtime_config`` (issue #345). When such a declaration targets
        a Python version outside the supported set it is flagged; when no Python
        ``linuxFxVersion`` is determinable the check is skipped.
        """
        target_config = context.get("target_config") if context is not None else None
        if (
            target_config is not None
            and target_config.hosting_plan.value == FLEX_CONSUMPTION_PLAN
        ):
            return _create_result(
                "skip",
                "Flex Consumption app; linuxFxVersion is not used "
                "(see check_flex_runtime_config).",
            )
        findings: list[tuple[str, str]] = []
        pattern = re.compile(r"linuxFxVersion['\"]?\s*[:=]\s*['\"]?[Pp]ython\|(\d+\.\d+)")
        for bicep in sorted(path.rglob("*.bicep")):
            try:
                text = bicep.read_text(encoding="utf-8")
            except OSError:
                continue
            for match in pattern.finditer(text):
                findings.append((str(bicep.relative_to(path)), match.group(1)))
        if not findings:
            return _create_result(
                "skip", "No Python linuxFxVersion found in infra config; check skipped"
            )
        unsupported = [(loc, ver) for loc, ver in findings if not is_supported_python_target(ver)]
        if not unsupported:
            return _create_result(
                "pass", "linuxFxVersion Python runtime(s) target a supported version"
            )
        supported_range = f"{SUPPORTED_PYTHON_VERSIONS[0]}\u2013{SUPPORTED_PYTHON_VERSIONS[-1]}"
        detail = "\n".join(
            [
                "Unsupported Python linuxFxVersion runtime(s) in infra config:",
                *[f"- {loc}: Python|{ver}" for loc, ver in unsupported[:10]],
                "",
                f"Fix: target a supported Python runtime ({supported_range}).",
            ]
        )
        return _create_result("fail", detail)

    @_rule_handler
    def _handle_host_json_log_level_conflict(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Flag host.json logLevel entries that conflict with the default level.

        ``logging.logLevel`` category overrides win over ``default``. When a
        category is configured *more verbose* than ``default`` it silently
        overrides the intended-restrictive default, producing more logs (and
        cost/PII exposure) than expected — a common misconfiguration.
        """
        host_path = path / "host.json"
        if not host_path.exists():
            return _create_result("skip", "host.json not found; logLevel check skipped")
        try:
            host_data = json.loads(host_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return _handle_specific_exceptions("reading host.json", exc)
        logging_cfg = host_data.get("logging") if isinstance(host_data, dict) else None
        log_level = logging_cfg.get("logLevel") if isinstance(logging_cfg, dict) else None
        if not isinstance(log_level, dict) or "default" not in log_level:
            return _create_result(
                "skip", "host.json has no logging.logLevel.default; conflict check skipped"
            )
        rank = {
            "trace": 0,
            "debug": 1,
            "information": 2,
            "warning": 3,
            "error": 4,
            "critical": 5,
            "none": 6,
        }
        default_rank = rank.get(str(log_level["default"]).strip().lower())
        if default_rank is None:
            return _create_result(
                "fail",
                f"host.json logging.logLevel.default '{log_level['default']}' "
                "is not a recognized log level.",
            )
        conflicts: list[str] = []
        for category, level in log_level.items():
            if category == "default":
                continue
            category_rank = rank.get(str(level).strip().lower())
            if category_rank is not None and category_rank < default_rank:
                conflicts.append(
                    f"- {category}={level} is more verbose than default={log_level['default']}"
                )
        if not conflicts:
            return _create_result(
                "pass", "host.json logLevel categories are consistent with default"
            )
        detail = "\n".join(
            [
                "host.json logLevel category overrides conflict with the default level:",
                *conflicts[:10],
                "",
                "Fix: lower the category level(s) to match the intended default, or "
                "raise the default deliberately.",
            ]
        )
        return _create_result("fail", detail)

    @_rule_handler
    def _handle_dev_storage_connection(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Flag the Azurite/dev-storage emulator connection in deployable config.

        ``AzureWebJobsStorage=UseDevelopmentStorage=true`` targets the local
        Azurite emulator and must never reach a deployed app. It is expected in
        ``local.settings.json`` (which is not deployed) but is a deploy-risk when
        present in infra templates (bicep/ARM) that provision app settings.
        """
        emulator = "UseDevelopmentStorage=true"
        findings: list[str] = []
        candidates = list(path.rglob("*.bicep")) + [
            p
            for p in path.rglob("*.json")
            if p.name not in ("local.settings.json",) and ".venv" not in p.parts
        ]
        for candidate in sorted(candidates):
            try:
                text = candidate.read_text(encoding="utf-8")
            except OSError:
                continue
            if "AzureWebJobsStorage" in text and emulator in text:
                findings.append(str(candidate.relative_to(path)))
        if not findings:
            return _create_result(
                "pass", "No dev-storage emulator connection found in deployable config"
            )
        detail = "\n".join(
            [
                "Dev-storage emulator connection in deployable config (ships to production):",
                *[f"- {loc}" for loc in findings[:10]],
                "",
                "Fix: provision a real storage account connection for AzureWebJobsStorage "
                "in deployment templates; keep UseDevelopmentStorage=true only in "
                "local.settings.json.",
            ]
        )
        return _create_result("fail", detail)

    @_rule_handler
    def _handle_unpinned_requirements(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Warn when ``requirements.txt`` declares unpinned/unbounded dependencies.

        Azure remote build resolves ``requirements.txt`` at deploy time, so
        unpinned dependencies (no version specifier, or an open ``>=`` lower
        bound with no upper bound) make deployments non-reproducible and prone to
        surprise breakage.
        """
        condition = rule.get("condition", {}) or {}
        target = parse_target(condition) or "requirements.txt"
        req_path = path / target
        if not req_path.is_file():
            return _create_result("skip", f"{target} not found; unpinned check skipped")
        try:
            content = req_path.read_text(encoding="utf-8")
        except OSError as exc:
            return _handle_specific_exceptions(f"reading {target}", exc)
        unpinned: list[str] = []
        for raw in content.splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            try:
                requirement = Requirement(line)
            except InvalidRequirement:
                continue
            if requirement.url is not None:
                continue
            specifiers = list(requirement.specifier)
            if not specifiers:
                unpinned.append(f"- {requirement.name} (no version specifier)")
                continue
            has_upper_bound = any(
                spec.operator in ("==", "===", "~=", "<", "<=") for spec in specifiers
            )
            if not has_upper_bound:
                bounds = ",".join(str(spec) for spec in specifiers)
                unpinned.append(f"- {requirement.name} ({bounds}; no upper bound)")
        if not unpinned:
            return _create_result("pass", f"{target} dependencies are pinned/bounded")
        detail = "\n".join(
            [
                f"Unpinned or unbounded dependencies in {target}:",
                *unpinned[:10],
                "",
                "Fix: pin versions (e.g. 'package==1.2.3') or add an upper bound to "
                "keep deployments reproducible.",
            ]
        )
        return _create_result("fail", detail)


# Global registry instance
_registry = HandlerRegistry()


def generic_handler(rule: Rule, path: Path, context: Optional[RuleContext] = None) -> HandlerResult:
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
