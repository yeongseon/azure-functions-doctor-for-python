# Detect Python command
ifeq ($(OS),Windows_NT)
    PYTHON := $(shell where python)
    VENV_PYTHON := .venv/Scripts/python.exe
else
    PYTHON := $(shell which python3)
    VENV_PYTHON := .venv/bin/python
endif

.PHONY: check-python
check-python:
	@$(PYTHON) -c "import sys; assert sys.version_info >= (3,9), '❌ Python 3.9+ is required'" || exit 1

.PHONY: venv
venv: check-python
	@$(PYTHON) -m venv .venv
	@echo "✅ Virtual environment created at .venv"

.PHONY: install
install:
	@$(VENV_PYTHON) -m pip install --upgrade pip
	@$(VENV_PYTHON) -m pip install -e .
	@$(VENV_PYTHON) -m pip install -e ".[dev]"

.PHONY: format
format:
	@$(VENV_PYTHON) -m ruff format src tests
	@$(VENV_PYTHON) -m black src tests

.PHONY: lint
lint:
	@$(VENV_PYTHON) -m ruff check src tests

.PHONY: test
test:
	@$(VENV_PYTHON) -m pytest tests

.PHONY: clean
ifeq ($(OS),Windows_NT)
clean:
	@for /d %%D in (*.egg-info dist build __pycache__ .pytest_cache) do if exist %%D rmdir /s /q %%D
else
clean:
	rm -rf *.egg-info dist build __pycache__ .pytest_cache
endif

.PHONY: clean-all
clean-all: clean
ifeq ($(OS),Windows_NT)
	@if exist .venv rmdir /s /q .venv
	@for /r %%D in (__pycache__) do if exist %%D rmdir /s /q %%D
	@for /r %%F in (*.pyc *.pyo) do if exist %%F del /q %%F
	@if exist .mypy_cache rmdir /s /q .mypy_cache
	@if exist .ruff_cache rmdir /s /q .ruff_cache
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist .coverage del /q .coverage
	@if exist coverage.xml del /q coverage.xml
	@if exist .DS_Store del /q .DS_Store
else
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	rm -rf .mypy_cache .ruff_cache .pytest_cache .coverage coverage.xml .DS_Store
endif

.PHONY: doctor
doctor:
	@echo "🔍 Python version:"
	@$(VENV_PYTHON) --version
	@echo "🔍 Installed packages:"
	@$(VENV_PYTHON) -m pip list
	@echo "🔍 Azure Function Core Tools version:"
	@func --version || echo "⚠️ func not found. Install with: npm i -g azure-functions-core-tools@4"

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

.PHONY: docs
docs:
	@$(VENV_PYTHON) -m mkdocs serve
