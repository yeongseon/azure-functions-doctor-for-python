# 🖥️ CLI Usage: Azure Functions Doctor

Azure Functions Doctor provides a CLI to help validate and troubleshoot your Python Azure Functions project.

---

## 🔧 Basic Usage

Run the CLI from your terminal:

```bash
hatch run azfunc-doctor
```

This will display the help menu and available commands.

Or alternatively:

```bash
python -m azure_functions_doctor.cli
```

---

## 🩺 Run Diagnostics

To check your local Azure Functions setup:

```bash
hatch run azfunc-doctor diagnose
```

You can also specify options:

```bash
hatch run azfunc-doctor diagnose --format json --verbose
```

### What It Checks:

- ✅ Python version is ≥ 3.9
- ✅ `.venv` directory exists
- ✅ Azure Functions Core Tools (`func`) is installed
- ✅ `host.json` and `function.json` are valid
- ✅ Expected directory structure is present
- ⚠️ Optional files like `requirements.txt` (future support)

---

## 🆘 Help

To view available options and subcommands:

```bash
hatch run azfunc-doctor --help
hatch run azfunc-doctor diagnose --help
```

---

## 💡 Example Output

```bash
$ azfunc-doctor diagnose

✖ Python Environment
  • Python version: Current: 3.12.3, Expected: >=3.9
  • Virtual environment: VIRTUAL_ENV is set
  • Python executable: /root/.local/share/hatch/env/virtual/azure-function-doctor/qaLwoID5/azure-function-doctor/bin/python exists
  • requirements.txt: /root/Github/azure-functions-doctor/examples/basic-hello/requirements.txt exists
  • azure-functions package: azure_functions is not installed

✖ Project Structure
  • host.json: /root/Github/azure-functions-doctor/examples/basic-hello/host.json exists
  • local.settings.json: /root/Github/azure-functions-doctor/examples/basic-hello/local.settings.json is missing
  • main.py: /root/Github/azure-functions-doctor/examples/basic-hello/main.py is missing

─────────────────────────────────────────────────────────────────────────────── Summary ────────────────────────────────────────────────────────────────────────────────
✔ 0 Passed    ✖ 2 Failed
```
