# multi-trigger (Programming Model v1)

Multiple triggers in a single v1 (function.json-based) Functions app: HTTP, Timer, Queue.
Designed to compare against the v2 `examples/v2/multi-trigger` sample and to exercise azure-functions-doctor checks.

## Structure
```
v1/multi-trigger/
├── http_trigger_function/
│   ├── __init__.py
│   └── function.json
├── timer_trigger_function/
│   ├── __init__.py
│   └── function.json
├── queue_trigger_function/
│   ├── __init__.py
│   └── function.json
├── host.json
├── requirements.txt
├── local.settings.sample.json
└── README.md
```

## Run Locally
```bash
cd examples/v1/multi-trigger
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp local.settings.sample.json local.settings.json
func start
```

## Triggers
- HTTP: GET/POST name echo at /api/http_trigger_function
- Timer: Every 5 minutes (`0 */5 * * * *`)
- Queue: Listens on `samples-in` queue (use Azurite or real storage)

## Diagnostics
```bash
azure-functions doctor --path .
```

Compare with v2 sample in `examples/v2/multi-trigger`.
