# Examples

| Model | Path | Description |
|-------|------|-------------|
| v1 (function.json) | `examples/v1/http-trigger` | Legacy single HTTP trigger function folder. |
| v2 (decorators) | `examples/v2/http-trigger` | Minimal single HTTP trigger using decorator API. |
| v2 (multi) | `examples/v2/multi-trigger` | Multiple triggers (HTTP, timer, queue placeholder). |

## Install (one time)
```bash
pip install azure-functions-doctor
# or from source
pip install -e .
```

## Run Diagnostics (examples)

v1:
```bash
azure-functions doctor --path examples/v1/http-trigger
```

v2 (single):
```bash
azure-functions doctor --path examples/v2/http-trigger
```

v2 (multi):
```bash
azure-functions doctor --path examples/v2/multi-trigger
```
