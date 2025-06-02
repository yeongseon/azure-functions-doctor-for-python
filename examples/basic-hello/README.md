# 🔪 Basic Hello Function

This is a minimal Azure Function example using the **Python Programming Model v2** with an HTTP trigger.

---

## 📁 Structure

```
basic-hello/
├── function_app.py
├── host.json
├── requirements.txt
└── README.md
```

---

## 🚀 Run Locally

1. Navigate to the example directory and create a virtual environment:

```bash
cd examples/basic-hello
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
pip install azure-functions-doctor  # Local testing
```

3. Start the Azure Function runtime:

```bash
func start
```

> Make sure Azure Functions Core Tools (v4) is installed:
> `npm i -g azure-functions-core-tools@4 --unsafe-perm true`

---

## 🩺 Run Diagnostics

You can validate your setup using the Azure Functions Doctor CLI:

```bash
func-doctor diagnose --path .
```

Example output:

```bash
$ func-doctor diagnose
🩺 Azure Functions Doctor for Python v0.1.0
📁 Path: /root/Github/azure-functions-doctor/examples/basic-hello

✖ Python Env
  • Python version: Python version is 3.12.3, expected >=3.9
  • Virtual environment: VIRTUAL_ENV is set
  • Python executable: /root/.local/share/hatch/env/virtual/azure-functions-doctor/.../bin/python exists
  • requirements.txt: /root/Github/azure-functions-doctor/examples/basic-hello/requirements.txt exists
  • azure-functions package: Package 'azure_functions' is not installed

✖ Project Structure
  • host.json: exists
  • local.settings.json: is missing
  • main.py: is missing

Summary
✔ 0 Passed    ✖ 2 Failed
---

## 📌 Notes

* This example uses the [Python Programming Model v2](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Cbash&pivots=python-mode-v2).
* There is no `function.json` or `__init__.py` file; routing is handled in `function_app.py`.