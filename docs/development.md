# Development Guide

## Requirements

- Python 3.9+
- Git
- Recommended: `uv` for dependency management

## Setup

```bash
make venv
make install
make precommit-install
```

## Local Testing

```bash
make check         # Format, lint, typecheck, test
make test          # Run unit tests
make coverage      # View test coverage
```

## Release

```bash
make release-patch   # Patch version bump + changelog
make publish         # Publish to PyPI (requires config)
```
