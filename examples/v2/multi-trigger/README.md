# Multi Trigger Sample (Programming Model v2)

Single project demonstrating multiple triggers (start with HTTP; extend with Timer, Queue, etc.).

## Structure
```
v2/multi-trigger/
├── function_app.py
├── host.json
├── requirements.txt
└── README.md
```

## Run
```bash
cd examples/v2/multi-trigger
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
func start
```

## Diagnostics
```bash
azure-functions doctor --path .
```

Add more triggers by decorating functions in `function_app.py`.
