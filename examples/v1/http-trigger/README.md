# http-trigger (Programming Model v1)

Legacy v1 function folder illustrating an HTTP trigger via function.json.

## Structure
```
v1/http-trigger/
├── http_trigger_function/
│   ├── __init__.py
│   └── function.json
├── host.json
├── requirements.txt
├── local.settings.sample.json
└── README.md
```

## Run
```bash
cd examples/v1/http-trigger
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

Compare with the v2 single example in `examples/v2/http-trigger` or multi trigger sample in `examples/v2/multi-trigger`.
