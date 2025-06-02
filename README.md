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

# 🚑 Azure Functions Doctor for Python

A fast and extensible diagnostic CLI for Python-based Azure Functions projects.

---

## 🤔 Why Azure Functions Doctor?

- Getting random 500 errors and suspect misconfiguration?
- Need to verify your dev environment before CI/CD deployment?
- Want a quick health check without digging through docs?

**Azure Functions Doctor** helps save time by automating common environment diagnostics.

---

## ✨ Key Features

- Diagnose Python version, venv, `azure-functions` package
- Validate `host.json`, `local.settings.json`, function structure
- Fully customizable via `rules.json`
- Output: colorized CLI or machine-readable JSON
- Built-in rule engine, easily extensible

---

## 🪠 Requirements

- Python 3.9+
- Git
- (Optional) Azure Functions Core Tools v4+ (`npm i -g azure-functions-core-tools@4`)
- (Recommended) Unix-like shell or PowerShell for Makefile support

---

## 📦 Installation

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

## 🩺 Usage

### Run the Doctor

```bash
func-doctor diagnose
```

<img src="docs/assets/func-doctor-example.png" alt="Sample output" width="100%" />

### Show Help

```bash
func-doctor --help
```

📌 Sample: [examples/basic-hello/diagnose-output.md](examples/basic-hello/diagnose-output.md)

---

## 📋 Example

See [`examples/basic-hello`](examples/basic-hello) for:

- Minimal Azure Functions structure setup
- Running the CLI and inspecting results

---

## 📘 Documentation

- Getting Started: [docs/index.md](https://yeongseon.github.io/azure-functions-doctor-for-python/)
- Custom Rules: [docs/rules.md](https://yeongseon.github.io/azure-functions-doctor-for-python/rules/)
- Developer Guide: [docs/development.md](https://yeongseon.github.io/azure-functions-doctor-for-python/development/)

---

## 🤝 Contributing

We welcome issues and PRs!

Please see [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution guidelines.

If you find this useful, please ⭐️ the repo!

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).