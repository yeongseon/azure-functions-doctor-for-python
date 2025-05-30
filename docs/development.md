# 🛠️ Development Guide (Hatch-based)

This project uses [Hatch](https://hatch.pypa.io/) as its build and environment manager.

## ✅ Requirements

- Python 3.9+
- Git
- Recommended: [`uv`](https://github.com/astral-sh/uv) for fast dependency management

## 🚀 Setup

```bash
make venv               # Create virtual environment
make install            # Install dependencies using Hatch
make precommit-install  # Install pre-commit hooks
```

## 🧪 Local Testing

```bash
make check         # Format, lint, typecheck, test
make test          # Run unit tests
make cov           # Generate test coverage report
```

## 🚢 Release Workflow

```bash
make release-patch   # Patch version bump + changelog update
make release-minor   # Minor version bump + changelog update
make release-major   # Major version bump + changelog update
make publish         # Publish to PyPI (requires credentials)
```

## 🧹 Code Quality Commands

```bash
make format      # Format code with Black + Ruff
make lint        # Run Ruff + Mypy
make typecheck   # Run static type checks
make docs        # Serve local MkDocs site
```
