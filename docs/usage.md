# CLI Usage: Azure Functions Doctor

Azure Functions Doctor provides a CLI to help validate and troubleshoot your Python Azure Functions project.

---

## 🔧 Basic Usage

To run the CLI from your terminal:

```bash
azfunc-doctor
```

This will display the help menu and available commands.

---

## 🩺 Run Diagnostics

Check your local Azure Functions setup:

```bash
azfunc-doctor doctor
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
azfunc-doctor --help
```

You can also run:

```bash
azfunc-doctor doctor --help
```

To get help for the `doctor` subcommand.

---

## 💡 Example Output

```bash
$ azfunc-doctor doctor
✅ Python version: 3.10.12
✅ Virtual environment detected
✅ host.json found and valid
✅ function.json present in functions
⚠️ Azure Functions Core Tools not installed
```
