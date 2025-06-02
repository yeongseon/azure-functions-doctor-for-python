# 🛠️ Development Guide (Hatch-based)

This guide covers how to set up a local development environment, run tests, and manage code quality for **Azure Functions Doctor**, using Hatch and a Makefile for workflow automation.

---

## 📦 Prerequisites

- **Python 3.9+** installed on your system
- **Git** for version control
- **Hatch** as the build and environment manager (installed via `pip install hatch`)
- **Make** (for running the provided Makefile targets)
- (Optional) **uv** for fast dependency installation (`pip install uv`)

---

## 🛠️ Project Structure Overview

```text
azure-functions-doctor-for-python/
├── Makefile
├── pyproject.toml
├── hatch.toml
├── src/
│   └── azure_functions_doctor/
│       ├── __init__.py
│       ├── cli.py
│       ├── doctor.py
│       ├── handlers.py
│       ├── utils.py
│       ├── assets/
│       │   └── rules.json
│       └── checks/
├── tests/
│   ├── test_cli.py
│   ├── test_handler.py
│   └── test_*.py
├── docs/
│   ├── index.md
│   ├── usage.md
│   ├── rules.md
│   ├── diagnostics.md
│   └── development.md
├── examples/
│   └── basic-hello/
│       └── diagnose-output.md
└── ...
```

- **`Makefile`**: Defines common commands for creating the environment, running tests, linting, formatting, and publishing.
- **`pyproject.toml`** and **`hatch.toml`**: Configuration for Hatch environments and project metadata.
- **`src/azure_functions_doctor/`**: Core application code, including CLI entrypoint, diagnostic logic, and rule assets.
- **`tests/`**: Unit and integration tests for the project.
- **`docs/`**: Documentation files used by MkDocs (if enabled) or GitHub pages.
- **`examples/`**: Contains sample Azure Functions projects and expected outputs.

---

## 🚀 Initial Setup

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yeongseon/azure-functions-doctor-for-python.git
    cd azure-functions-doctor-for-python
    ```

2. **Create and activate a virtual environment** using the Makefile:
    ```bash
    make venv
    source .venv/bin/activate      # On Windows (PowerShell): .venv\Scripts\Activate.ps1
    ```

3. **Install project dependencies** via Hatch (or using `uv` if preferred):
    ```bash
    make install
    # or, if using uv: uv install
    ```

4. **Install pre-commit hooks** for code formatting and linting:
    ```bash
    make precommit-install
    ```

> **Note**: The Makefile ensures Hatch commands run inside the appropriate environment. If you bypass Makefile, you can manually do:
> ```bash
> hatch env create default
> hatch run pip install -r requirements-dev.txt
> hatch run pre-commit install
> ```

---

## 🧪 Running Tests and Quality Checks

### 1. Format Code
Use **Black** and **Ruff** via Makefile to enforce consistent styling:
```bash
make format
```

### 2. Lint Code
Run **Ruff** and **Mypy** for linting and type checks:
```bash
make lint
```

### 3. Type Checking
Perform static type analysis with **Mypy**:
```bash
make typecheck
```

### 4. Run Unit Tests
Execute all tests using **pytest**:
```bash
make test
```

### 5. Combined Quality Checks
Run formatting, linting, type checking, and tests in one command:
```bash
make check
```

### 6. Generate Coverage Report
Produce a coverage report (HTML + XML):
```bash
make cov
```
- Opens `htmlcov/index.html` for browser viewing
- Generates `coverage.xml` for CI integrations (e.g., Codecov)

---

## 🎯 Development Workflow

1. **Create a feature branch**:
    ```bash
    git checkout -b feature/your-description
    ```

2. **Implement changes** in `src/azure_functions_doctor/` and/or update `rules.json` under `src/azure_functions_doctor/assets/`.

3. **Add new tests** in the `tests/` directory to cover your changes.

4. **Run quality checks** locally:
    ```bash
    make check
    ```

5. **Commit changes** with Conventional Commits format:
    ```
    git commit -m "feat: add new check for custom config file"
    ```

6. **Push and open a Pull Request** to `main`.

---

## 📝 Makefile Targets Reference

| Target                 | Description                                                       |
|------------------------|-------------------------------------------------------------------|
| `make venv`            | Create a Python virtual environment at `.venv/`                    |
| `make install`         | Install runtime and dev dependencies via Hatch (`hatch install`)  |
| `make precommit-install` | Install pre-commit hooks (Black, Ruff, etc.)                    |
| `make format`          | Format code with Black and apply Ruff fixes                         |
| `make lint`            | Run Ruff and Mypy checks                                           |
| `make typecheck`       | Perform static type checking with Mypy                             |
| `make test`            | Run pytest                                                       |
| `make check`           | Run formatting, linting, typechecking, and tests in sequence       |
| `make cov`             | Generate coverage report and open HTML index                       |
| `make docs`            | Serve MkDocs locally (if MkDocs configured)                        |
| `make release-patch`   | Bump patch version, update changelog                               |
| `make release-minor`   | Bump minor version, update changelog                               |
| `make release-major`   | Bump major version, update changelog                               |
| `make publish`         | Publish package to PyPI (requires credentials in environment)      |

> For detailed release workflow, refer to [`release_process.md`](release_process.md).

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository and create a new branch.
2. Follow the **Development Workflow** above.
3. Ensure tests pass and code quality checks succeed.
4. Submit a Pull Request with a clear description of your changes.

Thank you for helping improve Azure Functions Doctor!

---

## 📄 License

This project is licensed under the [MIT License](../LICENSE).