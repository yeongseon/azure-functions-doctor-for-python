# 🖥️ CLI Usage: `azure-functions doctor`

The Azure Functions Doctor CLI helps validate your local Python-based Azure Functions project for common issues using an extensible rules system. It supports both **Programming Model v1** (function.json-based) and **Programming Model v2** (decorator-based) projects.

---

## Basic Usage

```bash
azure-functions doctor
```

Run diagnostics in the current or specified folder.

---

## Options

| Option | Description |
|--------|-------------|
| `--path` | Target directory (default: current folder) |
| `--format json` | Output in machine-readable JSON |
| `--verbose` | Show detailed diagnostics and hints |
| `--help` | Show usage for the CLI or subcommand |

Example:

```bash
azure-functions doctor --path ./my-func-app --format json --verbose
```

---

## ✅ What It Checks

### Programming Model Detection
The tool automatically detects your project's programming model:

- **v2 (Decorator-based)**: Uses `@app.route`, `@app.schedule` decorators
- **v1 (function.json-based)**: Uses `function.json` files for configuration

### Diagnostic Categories

| Category | v2 Checks | v1 Checks |
|----------|-----------|-----------|
| Python Environment | Python ≥ 3.9, virtualenv, executable | Python ≥ 3.6, virtualenv, executable |
| Dependencies | `azure-functions-python-library` | `azure-functions-worker` |
| Project Files | `host.json`, `local.settings.json` | `host.json`, `local.settings.json`, `function.json` |

---

## Example Output

### v2 Project (Decorator-based)
```
Azure Functions Doctor

Programming Model
[✓] Programming model v2: @app decorator detected

Python Env
[✓] Python version: Python 3.12.3 (>=3.9)
[✓] Virtual environment: VIRTUAL_ENV set
[✓] Python executable: /path/to/.venv/bin/python3
[✓] requirements.txt: present
[✗] azure-functions-python-library package: Module 'azure.functions' not installed

Project Structure
[✓] host.json: present
[!] local.settings.json: missing (optional)

Tooling
[✓] Azure Functions Core Tools (func): func detected

Summary: 1 error, 1 warning, 12 passed
```

### v1 Project (function.json-based)
```
Azure Functions Doctor

Programming Model
[✓] Programming model v1: function.json detected

Python Env
[✓] Python version: Python 3.11.9 (>=3.6)
[✓] Virtual environment: VIRTUAL_ENV set
[✓] Python executable: /path/to/.venv/bin/python
[✓] requirements.txt: present
[✗] azure-functions-worker package: Module 'azure.functions_worker' not installed

Project Structure
[✗] host.json: missing
[!] local.settings.json: missing (optional)

Summary: 2 errors, 1 warning, 8 passed
```

---

## 🆘 Help

```bash
azure-functions --help
azure-functions doctor --help
```

For more examples, see the [example project](../examples/basic-hello/README.md).