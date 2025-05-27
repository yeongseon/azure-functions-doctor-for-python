# Detect Python command
ifeq ($(OS),Windows_NT)
	PYTHON := $(shell where python)
	VENV_PYTHON := .venv/Scripts/python.exe
	UV_EXISTS := $(shell where uv >NUL 2>&1 && echo yes || echo no)
else
	PYTHON := $(shell which python3)
	VENV_PYTHON := .venv/bin/python
	UV_EXISTS := $(shell command -v uv >/dev/null 2>&1 && echo yes || echo no)
endif

# ------------------------------
# 🔧 Environment Setup
# ------------------------------
.PHONY: venv
venv:
ifeq ($(UV_EXISTS),yes)
	@uv venv
else
	@$(PYTHON) -m venv .venv
endif
	@echo "✅ Virtual environment created at .venv"

.PHONY: install
install:
ifeq ($(UV_EXISTS),yes)
	@uv pip install -e ".[dev]"
else
	@echo "⚠️ uv not found, using pip"
	@$(VENV_PYTHON) -m pip install --upgrade pip
	@$(VENV_PYTHON) -m pip install -e ".[dev]"
endif

.PHONY: reset
reset: clean-all venv install
	@echo "🔁 Project reset complete."

# ------------------------------
# 🧹 Code Quality
# ------------------------------
.PHONY: format
format:
	@$(VENV_PYTHON) -m ruff format src tests
	@$(VENV_PYTHON) -m black src tests

.PHONY: lint
lint:
	@$(VENV_PYTHON) -m ruff check src tests

.PHONY: typecheck
typecheck:
	@$(VENV_PYTHON) -m mypy src tests

.PHONY: check
check: format lint typecheck test
	@echo "✅ All checks passed!"

.PHONY: precommit
precommit:
	@$(VENV_PYTHON) -m pre_commit run --all-files

.PHONY: precommit-install
precommit-install:
	@$(VENV_PYTHON) -m pre_commit install

# ------------------------------
# 🧪 Testing & Coverage
# ------------------------------
.PHONY: test
test:
	@$(VENV_PYTHON) -m pytest tests

.PHONY: coverage
coverage:
	@$(VENV_PYTHON) -m coverage run -m pytest
	@$(VENV_PYTHON) -m coverage report
	@$(VENV_PYTHON) -m coverage html
	@echo "📂 Open htmlcov/index.html in your browser to view the coverage report"

# ------------------------------
# 🧪 Multi-Version Test with tox
# ------------------------------
.PHONY: tox
tox:
	@$(VENV_PYTHON) -m tox

# ------------------------------
# 📦 Build & Release
# ------------------------------
.PHONY: build
build:
	@$(VENV_PYTHON) -m build

.PHONY: release
release:
ifndef VERSION
	$(error VERSION is not set. Usage: make release VERSION=0.1.0)
endif
	@git tag -a v$(VERSION) -m "Release v$(VERSION)"
	@git push origin v$(VERSION)

.PHONY: release-patch
release-patch:
	@hatch version patch
	@make release VERSION=$(shell hatch version)

.PHONY: release-minor
release-minor:
	@hatch version minor
	@make release VERSION=$(shell hatch version)

.PHONY: release-major
release-major:
	@hatch version major
	@make release VERSION=$(shell hatch version)

.PHONY: publish
publish:
	@hatch publish

# ------------------------------
# 📚 Documentation
# ------------------------------
.PHONY: docs
docs:
	@$(VENV_PYTHON) -m mkdocs serve

# ------------------------------
# 🩺 Diagnostic
# ------------------------------
.PHONY: doctor
doctor:
	@echo "🔍 Python version:"
	@$(VENV_PYTHON) --version
	@echo "🔍 Installed packages:"
	@$(VENV_PYTHON) -m pip list
	@echo "🔍 Azure Function Core Tools version:"
	@func --version || echo "⚠️ func not found. Install with: npm i -g azure-functions-core-tools@4"
	@echo "🔍 Pre-commit hook installed:"
	@$(VENV_PYTHON) -c "import os; print('✅ Yes' if os.path.exists('.git/hooks/pre-commit') else '❌ No')"

# ------------------------------
# 🧹 Clean
# ------------------------------
.PHONY: clean
ifeq ($(OS),Windows_NT)
clean:
	@cmd /c scripts\clean-win.bat
else
clean:
	@rm -rf *.egg-info dist build __pycache__ .pytest_cache
endif

.PHONY: clean-all
ifeq ($(OS),Windows_NT)
clean-all: clean
	@cmd /c scripts\clean-all-win.bat
else
clean-all: clean
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	rm -rf .mypy_cache .ruff_cache .pytest_cache .coverage coverage.xml .DS_Store
endif

# ------------------------------
# 🆘 Help
# ------------------------------
.PHONY: help
help:
	@echo "📖 Available commands:" && \
	grep -E '^\.PHONY: ' Makefile | cut -d ':' -f2 | xargs -n1 echo "  - make"
