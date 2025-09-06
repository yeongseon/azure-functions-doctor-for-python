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
🩺 Azure Functions Doctor for Python v0.5.1
📁 Path: /path/to/v2-project
🐍 Python Programming Model: v2

✖ Python Env
  • Python version: Python version is 3.12.3, expected >=3.9
  • Virtual environment: VIRTUAL_ENV is set
  • Python executable: .../bin/python exists
  • requirements.txt: exists
  • azure-functions-python-library package: Package 'azure.functions' is not installed

✔ Project Structure
  • host.json: exists
  • local.settings.json: is missing (optional for local development)

Summary
✔ 1 Passed    ✖ 1 Failed
```

### v1 Project (function.json-based)
```
🩺 Azure Functions Doctor for Python v0.5.1
📁 Path: /path/to/v1-project
🐍 Python Programming Model: v1 (limited support)

✖ Python Env
  • Python version: Python version is 3.12.3, expected >=3.6
  • Virtual environment: VIRTUAL_ENV is set
  • Python executable: .../bin/python exists
  • requirements.txt: exists
  • azure-functions-worker package: Package 'azure.functions_worker' is not installed

✖ Project Structure
  • host.json: is missing
  • local.settings.json: is missing (optional for local development)

Summary
✔ 0 Passed    ✖ 2 Failed
```

---

## 🆘 Help

```bash
azure-functions --help
azure-functions doctor --help
```

For more examples, see the [example project](../examples/basic-hello/README.md).