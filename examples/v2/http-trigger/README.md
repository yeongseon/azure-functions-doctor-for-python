# HTTP Trigger Function (Programming Model v2)

Minimal Azure Functions example using the **Python Programming Model v2** with an HTTP trigger.

---

## Structure

```
v2/http-trigger/
├── function_app.py
├── host.json
├── requirements.txt
└── README.md
```

---

## Run Locally

1. Create a virtual environment:

```bash
cd examples/v2/http-trigger
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
pip install azure-functions-doctor  # optional: ensure latest doctor locally
```

3. Start the Azure Functions host:

```bash
func start
```

> Ensure Azure Functions Core Tools (v4) is installed: `npm i -g azure-functions-core-tools@4 --unsafe-perm true`

---

## Run Diagnostics

```bash
azure-functions doctor --path .
```

Example output path references will now show `examples/v2/http-trigger`.

---

## Notes

* Programming Model v2 uses decorators (`@app.route`, etc.) instead of `function.json`.
* Compare with the v1 example in `examples/v1/HttpExample` for structural differences.
