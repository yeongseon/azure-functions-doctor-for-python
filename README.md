# Azure Function Doctor 🩺

A Python-based diagnostic CLI tool for Azure Function Apps.

## Features

- Diagnose common issues in Azure Functions (`host.json`, `function.json`, etc.)
- Check Python environment and Azure Function Core Tools installation
- Validate best practices
- Developer-friendly CLI interface

## Installation

```bash
git clone https://github.com/yeongseon/azure-functions-doctor.git
cd azure-functions-doctor
make venv
make install
```

## Usage

```bash
azfunc-doctor run
```

## Development

### Format, Lint, Test

```bash
make format
make lint
make test
```

### Clean

```bash
make clean       # Keep .venv
make clean-all   # Remove .venv and all cache
```

### Documentation

```bash
make docs
```

Browse at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## License

MIT License
