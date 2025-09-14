# http-trigger (Programming Model v2)

Minimal single HTTP trigger for the Python v2 programming model.

## Structure
```
v2/http-trigger/
├── function_app.py
├── host.json
├── requirements.txt
├── local.settings.sample.json
└── README.md
```

## Key Points
- Uses the decorator-based programming model.
- Single HTTP route returning a greeting.
- Mirrors the v1 example structure for comparison (see `examples/v1/http-trigger`).

## Run
```bash
cd examples/v2/http-trigger
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp local.settings.sample.json local.settings.json
func start
```

## Diagnostics
```bash
azure-functions doctor --path .
```

* Compare with the v1 example in `examples/v1/http-trigger` for structural differences.
