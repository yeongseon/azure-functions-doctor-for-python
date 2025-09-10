<p align="center">
  <img
    src="https://raw.githubusercontent.com/yeongseon/azure-functions-doctor-for-python/main/logo_assets/logo_full.png"
    alt="Azure Functions Doctor Logo"
    width="320"
  />
</p>

<p align="center">
  <a href="https://github.com/yeongseon/azure-functions-doctor-for-python/actions/workflows/test.yml">
    <img src="https://github.com/yeongseon/azure-functions-doctor-for-python/actions/workflows/test.yml/badge.svg" alt="Test Status" />
  </a>
  <a href="https://github.com/yeongseon/azure-functions-doctor-for-python/actions/workflows/release.yml">
    <img src="https://github.com/yeongseon/azure-functions-doctor-for-python/actions/workflows/release.yml/badge.svg" alt="Release Status" />
  </a>
  <a href="https://pypi.org/project/azure-functions-doctor/">
    <img src="https://img.shields.io/pypi/v/azure-functions-doctor.svg" alt="PyPI Version" />
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/github/license/yeongseon/azure-functions-doctor-for-python.svg" alt="License" />
  </a>
  <a href="https://codecov.io/gh/yeongseon/azure-functions-doctor-for-python">
    <img src="https://codecov.io/gh/yeongseon/azure-functions-doctor-for-python/branch/main/graph/badge.svg" alt="Codecov Coverage" />
  </a>
  <a href="https://pypi.org/project/azure-functions-doctor/">
    <img src="https://img.shields.io/pypi/pyversions/azure-functions-doctor.svg" alt="Python Versions" />
  </a>
</p>

---

# Azure Functions Doctor for Python

A fast and extensible diagnostic CLI for Python-based Azure Functions projects. Supports both **Programming Model v1** (function.json-based) and **Programming Model v2** (decorator-based) projects.

---

## Why Azure Functions Doctor?

- Getting random 500 errors and suspect misconfiguration?
- Need to verify your dev environment before CI/CD deployment?
- Want a quick health check without digging through docs?

**Azure Functions Doctor** helps save time by automating common environment diagnostics.

---

## Key Features

- **Multi-Model Support**: Works with both v1 (function.json) and v2 (decorator) projects
- **Automatic Detection**: Automatically detects your project's programming model
- **Model-Specific Checks**: Different requirements for v1 vs v2 (Python version, packages, etc.)
- **Rich Diagnostics**: Python version, venv, required packages, project files
- **Extensible Rules**: Customizable rules system for both programming models
- **Rich Console Output**: Clear formatting with hints and suggestions
- **CI/CD Ready**: JSON output for automated environments

---

## Architecture

Azure Functions Doctor uses a modular, rule-based architecture for extensibility and maintainability:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Interface │    │  Core Diagnostic │    │   Rule System   │
│    (cli.py)     │───▶│    Engine        │───▶│  (assets/rules/v2.json or v1.json)   │
│                 │    │   (doctor.py)    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         │                        ▼                       ▼
         │               ┌──────────────────┐    ┌─────────────────┐
         │               │     Handler      │    │  Target/Version │
         │               │    Dispatcher    │    │    Resolver     │
         │               │  (handlers.py)   │    │ (target_resolver │
         │               └──────────────────┘    │      .py)       │
         │                        │              └─────────────────┘
         │                        ▼
         │               ┌──────────────────┐
         │               │   Individual     │
         │               │    Handlers      │
         │               │ • file_exists    │
         │               │ • compare_version│
         │               │ • check_package  │
         │               │ • validate_json  │
         │               └──────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌──────────────────┐
│ Output Formatter│    │     Results      │
│   JSON / CLI    │◀───│   Aggregator     │
│                 │    │                  │
└─────────────────┘    └──────────────────┘
```

### Key Components

- **CLI Interface**: Entry point handling commands, flags, and output formatting
- **Diagnostic Engine**: Core orchestration logic loading rules and coordinating execution  
- **Rule System**: Declarative JSON-based rule definitions for extensibility
- **Handler Dispatcher**: Routes rule types to appropriate handler functions
- **Individual Handlers**: Specific diagnostic implementations (file checks, version validation, etc.)
  - New adapter-style checks: `executable_exists`, `any_of_exists`, `file_glob_check`, `host_json_property`,
    and lightweight validators `binding_validation` and `cron_validation` (see `docs/rules.md`).
- **Results Aggregator**: Collects and structures all diagnostic outcomes
- **Output Formatter**: Renders results as colorized CLI output or machine-readable JSON

This design allows easy extension by adding new rules to `src/azure_functions_doctor/assets/rules/v2.json` (and `v1.json` for v1 projects) and implementing corresponding handlers, without modifying core engine logic.

---

## Requirements

- Python 3.9+
- Git
- (Optional) Azure Functions Core Tools v4+ (`npm i -g azure-functions-core-tools@4`)
- (Recommended) Unix-like shell or PowerShell for Makefile support

---

## Installation

From PyPI:

```bash
pip install azure-functions-doctor
```

Or from source:

```bash
git clone https://github.com/yeongseon/azure-functions-doctor-for-python.git
cd azure-functions-doctor-for-python
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

---

## Usage

### Run the Doctor

```bash
azure-functions doctor
```

<img src="docs/assets/azure-functions-doctor-example.png" alt="Sample output" width="100%" />

### Show Help

```bash
azure-functions --help
```

Sample (v2): [examples/v2/multi-trigger](examples/v2/multi-trigger)

### Icons & Status

| Icon | Status | Meaning |
|------|--------|---------|

### 메시지 간결화 (최근 변경)

일부 출력 문구가 더 짧고 스캔하기 쉽게 다음과 같이 정리되었습니다:

| 이전 | 변경 후 |
|------|---------|
| `Executable 'func' found in PATH` | `func detected` |
| `host.json: /path/.../host.json exists` | `host.json: present` |
| `requirements.txt: /path/.../requirements.txt exists` | `requirements.txt: present` |
| `No Durable Functions usage detected; check skipped` | (향후 예정: `No durable usage`) |

문구 축약은 단계적으로 진행 중이며, 추가 축약은 추후 릴리스 노트에 반영됩니다.
| ✔ | pass | 검사 통과 |
| ⚠ | warn | 경고 (선택적/권장 구성 누락: 예 `local.settings.json` 등) |
| ✖ | fail | 오류 (배포 차단 가능 / 필수 구성 문제) |

CLI 출력에서 `warn` 은 즉각적인 실패는 아니지만 품질이나 향후 배포 안정성을 위해 개선이 권장되는 항목입니다.

---

## Example

See examples for:

- Programming Model v2: [`examples/v2/multi-trigger`](examples/v2/multi-trigger)
- Programming Model v1: [`examples/v1/HttpExample`](examples/v1/HttpExample)

- Minimal Azure Functions structure setup
- Running the CLI and inspecting results

---

## Documentation

- Getting Started: [docs/index.md](https://yeongseon.github.io/azure-functions-doctor-for-python/)
- Custom Rules: [docs/rules.md](https://yeongseon.github.io/azure-functions-doctor-for-python/rules/)
- Developer Guide: [docs/development.md](https://yeongseon.github.io/azure-functions-doctor-for-python/development/)

---

## Contributing

We welcome issues and PRs!

Please see [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution guidelines.

If you find this useful, please star the repo!

---

## License

This project is licensed under the [MIT License](LICENSE).