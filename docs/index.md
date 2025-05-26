# Azure Functions Doctor

🩺 A Python-based diagnostic tool for Azure Function Apps.

## Features

- Diagnose common issues in `host.json`, `function.json`, or `local.settings.json`
- Check Python environment and Azure Functions Core Tools installation
- Provide suggestions based on best practices

## Get Started

```bash
make venv
make install
azfunc-doctor run
```

## Commands

| Command         | Description                                      |
|-----------------|--------------------------------------------------|
| `make venv`     | Create a virtual environment                     |
| `make install`  | Install package and dev dependencies             |
| `make format`   | Format code using Ruff and Black                 |
| `make lint`     | Run linter using Ruff                            |
| `make test`     | Run unit tests                                   |
| `make clean`    | Remove build artifacts (preserve `.venv`)       |
| `make clean-all`| Remove all dev artifacts including `.venv`       |
| `make docs`     | Start local MkDocs documentation server          |

## License

MIT License. Created by Yeongseon Choe.
