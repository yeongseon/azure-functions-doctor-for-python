"""Binding-connection handlers and evaluators (domain module, issue #387).

Split out of handlers/registry.py; registration/dispatch stays there.
"""

from pathlib import Path
from typing import Optional

from azure_functions_doctor.deploy_config import (
    local_settings_values,
)
from azure_functions_doctor.handlers._helpers import (
    HandlerResult,
    Rule,
    RuleContext,
    _collect_binding_connections,
    _create_result,
    _rule_handler,
)


def _evaluate_binding_connection_resolution(
    references: list[tuple[str, str]],
    app_settings: dict[str, str],
) -> HandlerResult:
    """Resolve v2 binding ``connection`` references against configured settings (#352).

    A referenced connection name is satisfied when an app setting matches it exactly
    or when an identity-based setting group is present (any ``<name>__...`` key, e.g.
    ``MyConn__serviceUri`` / ``MyConn__accountName``). References that resolve to no
    configuration are reported as a non-gating WARN so a project cannot silently ship
    a trigger whose connection will fail to bind at runtime. When no binding
    references a named connection, the check PASSes.
    """
    if not references:
        return _create_result(
            "pass",
            "No named binding connections referenced in v2 decorators.",
        )
    setting_names = set(app_settings)
    identity_prefixes = {name.split("__", 1)[0] for name in setting_names if "__" in name}

    def _is_resolved(name: str) -> bool:
        return name in setting_names or name in identity_prefixes

    unresolved: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for name, label in references:
        if _is_resolved(name):
            continue
        key = (name, label)
        if key in seen:
            continue
        seen.add(key)
        unresolved.append((name, label))

    if not unresolved:
        return _create_result(
            "pass",
            "All referenced binding connections resolve to configured settings.",
        )

    lines = ["Binding connections reference unconfigured settings:"]
    lines.extend(f"  - {name} ({label})" for name, label in unresolved)
    lines.append(
        "Add the missing app setting(s), or configure an identity-based connection "
        "group (<name>__serviceUri / <name>__accountName)."
    )
    detail = "\n".join(lines)
    result = _create_result("fail", detail)
    result["severity"] = "warning"
    result["gate"] = False
    result["expected"] = "Every referenced binding connection has a matching app setting"
    result["actual"] = "Unresolved connections: " + ", ".join(
        sorted({name for name, _ in unresolved})
    )
    return result


class BindingHandlers:
    """Binding-connection handlers and evaluators.

    Resolves ``connection=`` references against configured settings.
    """

    @_rule_handler
    def _handle_binding_connection_resolution(
        self, rule: Rule, path: Path, context: Optional[RuleContext] = None
    ) -> HandlerResult:
        """Resolve v2 binding ``connection`` references against configuration (#352).

        Collects ``connection="..."`` references from v2 trigger/binding decorators
        and resolves each against ``local.settings.json`` Values plus the ingested
        deploy-config app settings. Unresolved connections WARN (non-gating);
        identity-based connection groups (``<name>__...``) suppress false positives.
        """
        references = _collect_binding_connections(path)
        settings: dict[str, str] = dict(local_settings_values(path))
        target_config = context.get("target_config") if context is not None else None
        if target_config is not None:
            settings.update(target_config.app_settings)
        return _evaluate_binding_connection_resolution(references, settings)
