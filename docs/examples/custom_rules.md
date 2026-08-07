# Example: Custom Rules

This example shows how to provide a custom rules file with `--rules` and validate project-specific policy.

## When to use custom rules

Use custom rules when built-in checks are not enough for your team policy, for example:

- requiring additional files at project root
- enforcing specific host.json keys
- requiring environment variables in local workflows
- tightening version baselines

## Command shape

```bash
azure-functions-doctor doctor --rules ./rules/custom-rules.json
```

You can combine with profile and output flags:

```bash
azure-functions-doctor doctor --rules ./rules/custom-rules.json --profile minimal --format json --output doctor-custom.json
```

## Minimal custom rules file

Create `rules/custom-rules.json`:

```json
[
  {
    "id": "check_python_version_custom",
    "category": "environment",
    "section": "python_env",
    "label": "Python version >= 3.11",
    "description": "Require Python 3.11 or higher in this repository.",
    "type": "compare_version",
    "required": true,
    "condition": {
      "target": "python",
      "operator": ">=",
      "value": "3.11"
    },
    "hint": "Use Python 3.11+ in your local and CI environments.",
    "check_order": 1
  },
  {
    "id": "check_host_json_exists_custom",
    "category": "structure",
    "section": "project_structure",
    "label": "host.json",
    "description": "Ensure host.json exists.",
    "type": "file_exists",
    "required": true,
    "condition": {
      "target": "host.json"
    },
    "hint": "Add host.json to project root.",
    "check_order": 2
  },
  {
    "id": "check_extension_bundle_custom",
    "category": "configuration",
    "section": "extensions",
    "label": "extensionBundle",
    "description": "Recommend extension bundle configuration.",
    "type": "host_json_property",
    "required": false,
    "condition": {
      "jsonpath": "$.extensionBundle"
    },
    "hint": "Configure extensionBundle in host.json.",
    "check_order": 3
  }
]
```

## Run with the custom file

```bash
azure-functions-doctor doctor --rules ./rules/custom-rules.json --verbose
```

Expected behavior:

- rules are loaded from your file instead of built-in `v2.json`
- schema validation runs before checks execute
- optional failures are still reported as `warn`

## Rule fields that matter most

Required for execution:

- `id`
- `category`
- `section`
- `label`
- `description`
- `type`
- `required`
- `condition`
- `check_order`

Helpful but optional:

- `hint`
- `hint_url`
- `fix`
- `fix_command`

Reference schema:

`src/azure_functions_doctor/schemas/rules.schema.json`

## Supported handler `type` values

Current built-ins:

- `compare_version`
- `env_var_exists`
- `path_exists`
- `file_exists`
- `package_installed`
- `package_declared`
- `source_code_contains`
- `conditional_exists`
- `callable_detection`
- `executable_exists`
- `any_of_exists`
- `file_glob_check`
- `host_json_property`

## Pattern: organization-specific baseline

Many teams keep a repository-local baseline rule file and run:

```bash
azure-functions-doctor doctor --rules ./rules/org-baseline.json --profile minimal --format json --output doctor-org.json
```

This provides consistent policy in local and CI environments.

## Programmatic custom rules usage

```python
from pathlib import Path

from azure_functions_doctor.doctor import Doctor


def run_custom(path: str, rules_file: str) -> list[dict]:
    doctor = Doctor(path=path, profile="full", rules_path=Path(rules_file))
    rules = doctor.load_rules()
    return doctor.run_all_checks(rules=rules)
```

## Common validation errors

### Unknown `type`

If `type` is not one of supported handlers, the run fails for that rule.

### Missing required fields

Schema validation fails before execution.

### Invalid condition shape

A handler may report configuration errors when required condition keys are missing.

## Safe rollout strategy

1. Start with optional (`required: false`) rules
2. Observe behavior in CI reports
3. Promote to required only when false positives are understood
4. Version-control your custom rules file with review

!!! warning
    Only run trusted custom rule files in CI. Rules may inspect local environment and source code.

## Related docs

- [Rules](../rules.md)
- [Diagnostics](../diagnostics.md)
- [Minimal Profile](../minimal_profile.md)
- [API Reference](../api.md)
