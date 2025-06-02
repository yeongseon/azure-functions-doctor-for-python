# 🖥️ CLI Usage: Azure Functions Doctor

**Azure Functions Doctor** provides a command-line interface (CLI) to validate and troubleshoot your Python Azure Functions project setup.

---

## 🔧 Basic Usage

Run the CLI from your terminal using:

```bash
azfunc-doctor diagnose
```

You can also specify options:

```bash
azfunc-doctor diagnose --format json --verbose
```

---

## 🩺 What It Checks

* ✅ Python version is ≥ 3.9
* ✅ Virtual environment is activated (VIRTUAL\_ENV)
* ✅ Python executable path is resolvable
* ✅ `requirements.txt` file exists
* ✅ `azure-functions` package is installed
* ✅ Project files like `host.json`, `local.settings.json`, and `main.py` exist

---

## 💡 Example Output

```bash
🩺 Azure Functions Doctor for Python v0.1.0
📁 Path: /root/Github/azure-functions-doctor/examples/basic-hello

✖ Python Env
  • Python version: Python version is 3.12.3, expected >=3.9
  • Virtual environment: VIRTUAL_ENV is set
  • Python executable: /root/.local/share/hatch/env/virtual/azure-functions-doctor/qaLwoID5/azure-functions-doctor/bin/python exists
  • requirements.txt: /root/Github/azure-functions-doctor/examples/basic-hello/requirements.txt exists
  • azure-functions package: Package 'azure_functions' is not installed

✖ Project Structure
  • host.json: /root/Github/azure-functions-doctor/examples/basic-hello/host.json exists
  • local.settings.json: /root/Github/azure-functions-doctor/examples/basic-hello/local.settings.json is missing
  • main.py: /root/Github/azure-functions-doctor/examples/basic-hello/main.py is missing

Summary
✔ 0 Passed    ✖ 2 Failed
```

---

## 🆘 Help

To view available options and subcommands:

```bash
azfunc-doctor --help
azfunc-doctor diagnose --help
```
