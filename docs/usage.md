# 🖥️ CLI Usage: `func-doctor`

The Azure Functions Doctor CLI helps validate your local Python-based Azure Functions project for common issues using an extensible rules system.

---

## 🚀 Basic Usage

```bash
func-doctor diagnose
```

Run diagnostics in the current or specified folder.

---

## ⚙️ Options

| Option | Description |
|--------|-------------|
| `--path` | Target directory (default: current folder) |
| `--format json` | Output in machine-readable JSON |
| `--verbose` | Show detailed diagnostics and hints |
| `--help` | Show usage for the CLI or subcommand |

Example:

```bash
func-doctor diagnose --path ./my-func-app --format json --verbose
```

---

## ✅ What It Checks

| Category | Description |
|----------|-------------|
| Python Environment | Python version ≥ 3.9, virtualenv activated, executable exists |
| Dependencies | `requirements.txt` present, `azure-functions` installed |
| Project Files | `host.json`, `local.settings.json`, and `main.py` exist |

---

## 🧪 Example Output

```
🩺 Azure Functions Doctor for Python v0.1.0
📁 Path: /root/Github/azure-functions-doctor/examples/basic-hello

✖ Python Env
  • Python version: Python version is 3.12.3, expected >=3.9
  • Virtual environment: VIRTUAL_ENV is set
  • Python executable: .../bin/python exists
  • requirements.txt: exists
  • azure-functions package: Package 'azure_functions' is not installed

✖ Project Structure
  • host.json: exists
  • local.settings.json: is missing
  • main.py: is missing

Summary
✔ 0 Passed    ✖ 2 Failed
```

---

## 🆘 Help

```bash
func-doctor --help
func-doctor diagnose --help
```

For more examples, see the [example project](../examples/basic-hello/README.md).