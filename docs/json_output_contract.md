# JSON Output Contract

`--format json` produces the primary machine-readable output contract for automation.

This page defines field meanings, stability guarantees, and parser examples.

## Emit JSON

```bash
azure-functions-doctor doctor --format json --output doctor.json
```

If `--output` is omitted, JSON is printed to stdout.

## Top-level shape

```json
{
  "metadata": {
    "tool_version": "0.19.1",
    "generated_at": "2026-03-14T10:40:20.731Z",
    "target_path": "/absolute/path/to/project",
    "programming_model": "v2",
    "target_python": null,
    "deployment_mode": "remote-build"
  },
  "results": [
    {
      "title": "Python Env",
      "category": "python_env",
      "status": "fail",
      "items": [
        {
          "label": "Python version",
          "value": "Python 3.9.18 (>=3.10)",
          "status": "fail",
          "hint": "Target a Python version supported by Azure Functions: 3.10, 3.11, 3.12, 3.13, or 3.14.",
          "hint_url": "https://learn.microsoft.com/..."
        }
      ]
    }
  ]
}
```

## Field reference

### `metadata`

| Field | Type | Description |
| --- | --- | --- |
| `tool_version` | string | Installed `azure-functions-doctor` version. |
| `generated_at` | string | UTC timestamp in ISO 8601 format. |
| `target_path` | string | Resolved absolute project path used for checks. |
| `programming_model` | string | Detected Azure Functions programming model (`v2`, `mixed`, `unsupported_v1`, or `unknown`). |
| `target_python` | string \| null | Target Python version requested via `--target-python`, or `null` when not set. |
| `deployment_mode` | string | Deployment mode used for dependency checks: `remote-build` (default) or `local`. |

### `results[]`

| Field | Type | Description |
| --- | --- | --- |
| `title` | string | Human-readable section label (display-oriented). |
| `category` | string | Stable machine-oriented section key. |
| `status` | `pass` \| `fail` | Section-level status (required-check semantics). |
| `items` | array | List of check result objects for that section. |

### `results[].items[]`

| Field | Type | Description |
| --- | --- | --- |
| `label` | string | Check display label. |
| `value` | string | Diagnostic detail text from handler execution. |
| `status` | `pass` \| `warn` \| `fail` | Canonical item-level status. |
| `hint` | string (optional) | Human-readable remediation guidance. |
| `hint_url` | string (optional) | Supporting documentation link. |

## Stability levels

Use the following contract expectations when writing parsers.

| Field | Stability | Guidance |
| --- | --- | --- |
| `metadata.tool_version` | Stable | Safe for telemetry and compatibility checks. |
| `metadata.generated_at` | Stable | Safe for run timestamp tracking. |
| `metadata.target_path` | Stable | Safe for target correlation. |
| `metadata.programming_model` | Stable | Safe for detecting v1/v2/mixed project state. |
| `metadata.target_python` | Stable | Safe for correlating requested target Python version. |
| `results[].category` | Stable | Prefer for machine grouping. |
| `results[].status` | Stable | Safe for section-level logic. |
| `results[].items[].label` | Stable | Safe for human-readable matching. |
| `results[].items[].status` | Stable | Primary gate/filter field. |
| `results[].items[].value` | Stable | Safe for reporting detail text. |
| `results[].title` | Detail | Display-oriented; do not hardcode behavior on casing/format. |
| `results[].items[].hint` | Detail | Helpful for UX, optional in parsers. |
| `results[].items[].hint_url` | Detail | Helpful for UX, optional in parsers. |

!!! note
    Breaking changes to stable fields require a major version bump under project semver policy.

## Status semantics

Item status rules:

- `pass`: check succeeded
- `fail`: required rule failed
- `warn`: optional rule failed

Section status rules:

- `fail` if any required item in section failed
- otherwise `pass`

## Exit code contract

Process exit code aligns with required failures:

- `0` -> no required failures
- `1` -> one or more required failures

Always use exit code for gate truth; use JSON for diagnostics detail.

## Python parsing example

```python
import json
from pathlib import Path


def parse_doctor(path: str) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))

    summary = {"pass": 0, "warn": 0, "fail": 0}
    failures: list[dict[str, str]] = []

    for section in payload["results"]:
        for item in section["items"]:
            status = item["status"]
            summary[status] += 1
            if status == "fail":
                failures.append(
                    {
                        "section": section["category"],
                        "label": item["label"],
                        "value": item["value"],
                        "hint": item.get("hint", ""),
                    }
                )

    return {
        "tool_version": payload["metadata"]["tool_version"],
        "generated_at": payload["metadata"]["generated_at"],
        "target_path": payload["metadata"]["target_path"],
        "summary": summary,
        "failures": failures,
    }
```

## Bash and `jq` parsing examples

Count required failures:

```bash
jq '[.results[].items[] | select(.status=="fail")] | length' doctor.json
```

List failure labels:

```bash
jq -r '.results[].items[] | select(.status=="fail") | .label' doctor.json
```

Group by status:

```bash
jq '[.results[].items[] | .status] | group_by(.) | map({status: .[0], count: length})' doctor.json
```

Extract concise report lines:

```bash
jq -r '.results[] as $s | $s.items[] | "[\($s.category)] \(.status) - \(.label): \(.value)"' doctor.json
```

## CI parser recommendations

- Prefer `results[].items[].status` for gates and counters
- Prefer `results[].category` for section grouping
- Treat `hint` and `hint_url` as optional display enrichments
- Avoid coupling logic to `title` formatting

## Common parser mistakes

- Assuming warnings fail builds
- Treating missing optional fields (`hint`, `hint_url`) as schema errors
- Parsing output from non-JSON format
- Ignoring process exit code and relying only on string matching

## Relationship to other formats

- `sarif` output follows SARIF 2.1.0 conventions
- `junit` output follows JUnit XML conventions
- This contract governs only the doctor JSON format

## Related docs

- [Usage](usage.md)
- [Diagnostics](diagnostics.md)
- [Examples: CI Integration](examples/ci_integration.md)
