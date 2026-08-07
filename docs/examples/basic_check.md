# Example: Basic Check

This example shows a full local loop:

1. Run `azure-functions-doctor doctor`
2. Read failures and warnings
3. Apply fixes
4. Re-run until required failures are zero

## Scenario

Assume this project has common setup gaps:

- missing `requirements.txt`
- missing `host.json`
- no active virtual environment
- no `azure-functions` dependency declaration

## Step 1: Run the doctor

```bash
azure-functions-doctor doctor
```

You can also target another folder:

```bash
azure-functions-doctor doctor --path ./examples/v2/http-trigger
```

## Step 2: Read status correctly

Status model:

- `pass`: condition satisfied
- `warn`: optional rule failed
- `fail`: required rule failed

Exit codes:

- `0` when no required failures exist
- `1` when at least one required failure exists

!!! tip
    Fix `fail` items first. Warnings are useful but non-blocking.

## Step 3: Use verbose hints

Verbose mode prints `fix:` hints for non-passing checks.

```bash
azure-functions-doctor doctor --verbose
```

This is the fastest way to map output directly to remediation.

## Step 4: Fix required blockers

### Create `requirements.txt`

```bash
touch requirements.txt
```

### Add `azure-functions`

```text
azure-functions
```

### Create minimal `host.json`

```json
{
  "version": "2.0"
}
```

### Activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Confirm v2 decorator usage

```python
import azure.functions as func

app = func.FunctionApp()


@app.route(route="health")
def health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("ok")
```

## Step 5: Re-run

```bash
azure-functions-doctor doctor
```

Desired summary shape:

```text
Doctor summary (to see all details, run azure-functions-doctor doctor -v):
  0 fails, 2 warnings, 13 passed
Exit code: 0
```

Warnings can remain while required baseline is clean.

## Step 6: Export JSON report

```bash
azure-functions-doctor doctor --format json --output doctor-report.json
```

The output file includes `metadata` and `results` fields.

See [JSON Output Contract](../json_output_contract.md).

## Step 7: Parse key findings in Python

```python
import json
from pathlib import Path


def summarize(path: str) -> dict[str, int]:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    counts = {"pass": 0, "warn": 0, "fail": 0}
    for section in doc["results"]:
        for item in section["items"]:
            counts[item["status"]] += 1
    return counts
```

## Step 8: Parse key findings in shell

```bash
jq '[.results[].items[] | select(.status=="fail")] | length' doctor-report.json
```

If this returns `0`, required blockers are resolved.

## Optional: Generate SARIF for code scanning tools

```bash
azure-functions-doctor doctor --format sarif --output doctor.sarif
```

## Optional: Generate JUnit for CI test views

```bash
azure-functions-doctor doctor --format junit --output doctor-junit.xml
```

## What this example validates

- Local command execution and output understanding
- Required versus optional semantics
- Repeatable remediation loop
- Artifact generation for automation

## Related docs

- [CLI Usage](../usage.md)
- [Diagnostics](../diagnostics.md)
- [Rules](../rules.md)
- [Troubleshooting](../troubleshooting.md)
