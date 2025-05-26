# Azure Function Doctor 🩺

**Azure Function Doctor** is a Python-based CLI tool designed to diagnose, validate, and assist in debugging [Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/) environments. It helps developers identify misconfigurations, missing dependencies, or best practice violations in their local or deployed Azure Function Apps.

---

## 🚀 Features

- ✅ Diagnose common issues in Azure Functions (`host.json`, `function.json`, directory structure, etc.)
- ✅ Check Python version compatibility and venv usage
- ✅ Validate if Azure Function Core Tools are installed and correctly configured
- ✅ Ensure best practice configurations for Python-based Azure Functions
- ✅ Developer-friendly CLI interface with rich terminal output
- ✅ Built-in linting, type-checking, coverage, and release automation tools

---

## 🧰 Requirements

- Python 3.9+
- Git
- Optional: Azure Function Core Tools v4 (`npm i -g azure-functions-core-tools@4`)
- Recommended: Unix-like shell or PowerShell for Makefile support

---

## 📦 Installation

```bash
git clone https://github.com/yeongseon/azure-functions-doctor.git
cd azure-functions-doctor

make venv        # Create a virtual environment
make install     # Install main and development dependencies
make precommit-install  # Install Git hook for pre-commit
```

---

## 🧪 Usage

```bash
azfunc-doctor run
```

This command will execute a full diagnostic scan and print results in your terminal.

---

## 🛠 Development Workflow

### 🔍 Format, Lint, Type Check, Test

```bash
make format        # Format code using ruff & black
make lint          # Lint using ruff
make typecheck     # Type checking using mypy
make test          # Run all tests using pytest
make check         # Run lint + typecheck + test
```

---

### 🧼 Cleaning

```bash
make clean         # Remove build artifacts but keep .venv
make clean-all     # Remove .venv and all caches
```

---

### 🧪 Code Coverage

```bash
make coverage
```

Generates an HTML report in `htmlcov/index.html`.

---

### 🔁 Reset Environment

```bash
make reset
```

Performs: `clean-all → venv → install`

---

## 📚 Documentation (Live Preview)

```bash
make docs
```

Visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🧹 Git Hooks & Pre-commit

```bash
make precommit-install  # Install pre-commit hook
make precommit          # Run all hooks manually (black, ruff, mypy)
```

---

## 🚀 Release & Publishing (with hatch)

```bash
make release-patch   # bump patch version, tag, push
make release-minor   # bump minor version, tag, push
make release-major   # bump major version, tag, push
make publish         # build and publish to PyPI using hatch
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
