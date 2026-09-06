"""Diagnostic check handlers for Azure Functions Doctor.

This package was split from a single ``handlers.py`` module. The public API
is preserved: import from ``azure_functions_doctor.handlers`` exactly as
before. Implementation lives in :mod:`._helpers` (pure helpers and types) and
:mod:`.registry` (the ``HandlerRegistry`` dispatch class).
"""

from azure_functions_doctor.deploy_config import (
    ResolvedField,
    TargetConfig,
    resolve_target_config,
)
from azure_functions_doctor.handlers._helpers import (
    _HOST_JSON_MISSING,
    _PYTHON_CANDIDATES,
    _RULE_DISPATCH,
    EXCLUDED_PROJECT_DIRS,
    NATIVE_DEPENDENCY_PACKAGES,
    Condition,
    HandlerResult,
    Rule,
    RuleContext,
    _collect_blueprint_aliases,
    _collect_register_functions_args,
    _collect_unregistered_blueprint_aliases,
    _create_result,
    _detect_native_dependency_risks,
    _discover_functionapp_aliases,
    _handle_exception,
    _handle_specific_exceptions,
    _iter_project_py_contents,
    _parse_requirements_names,
    _read_project_python_file,
    _resolve_host_json_pointer,
    _rule_handler,
    _source_contains_ast,
    _source_contains_blueprint_decorator,
)
from azure_functions_doctor.handlers.registry import (
    HandlerRegistry,
    generic_handler,
)
from azure_functions_doctor.target_resolver import resolve_target_value

__all__ = [
    "EXCLUDED_PROJECT_DIRS",
    "NATIVE_DEPENDENCY_PACKAGES",
    "Condition",
    "HandlerRegistry",
    "HandlerResult",
    "Rule",
    "RuleContext",
    "generic_handler",
    "resolve_target_value",
    "ResolvedField",
    "TargetConfig",
    "resolve_target_config",
    "_collect_blueprint_aliases",
    "_collect_register_functions_args",
    "_collect_unregistered_blueprint_aliases",
    "_create_result",
    "_detect_native_dependency_risks",
    "_discover_functionapp_aliases",
    "_handle_exception",
    "_handle_specific_exceptions",
    "_HOST_JSON_MISSING",
    "_iter_project_py_contents",
    "_parse_requirements_names",
    "_PYTHON_CANDIDATES",
    "_read_project_python_file",
    "_resolve_host_json_pointer",
    "_RULE_DISPATCH",
    "_rule_handler",
    "_source_contains_ast",
    "_source_contains_blueprint_decorator",
]
