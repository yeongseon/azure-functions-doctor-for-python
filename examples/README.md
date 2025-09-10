# Examples

Collection of sample Azure Functions projects demonstrating both Python programming models.

| Model | Path | Description |
|-------|------|-------------|
| v2 (Decorator) | `examples/v2/multi-trigger` | Modern model, multiple triggers in one project. |
| v1 (function.json) | `examples/v1/HttpExample` | Legacy single HTTP trigger function folder. |

## Common Operations
Create environment & install:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run host:
```bash
func start
```

Run diagnostics:
```bash
azure-functions doctor --path .
```

Compare structures to understand rule differences detected by the Doctor.
