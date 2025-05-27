# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CLI entrypoint with `Click`
- Python version and virtual environment detection
- Validation of `host.json` and `function.json` existence and structure
- Azure Functions directory layout validation
- Diagnostic summary with emoji indicators (✅, ❌, ⚠️)
- Linting, type-checking, and test suite setup (`ruff`, `mypy`, `pytest`)
- `Makefile` with `check`, `install`, `clean`, and virtualenv helpers
- Pre-commit hook configuration
- GitHub repository initialization
