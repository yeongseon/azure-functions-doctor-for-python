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

### Install Azure Functions Doctor

You can install the CLI either from PyPI or from the repository source.

From PyPI (recommended):

```bash
pip install azure-functions-doctor
```

From source (developer):

```bash
git clone https://github.com/yeongseon/azure-functions-doctor-for-python.git
cd azure-functions-doctor-for-python
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
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

## Using the CLI

Each example includes a small project you can run the diagnostic against. Typical usage from the repo root:

```bash
# run in a virtualenv from the repo root
source .venv/bin/activate
azure-functions doctor --path examples/v2/multi-trigger
azure-functions doctor --path examples/v1/HttpExample
```

For full help and output formatting options:

```bash
azure-functions --help
azure-functions doctor --help
```
