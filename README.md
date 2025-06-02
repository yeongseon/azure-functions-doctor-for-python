<p align="center">
  <img
    src="https://raw.githubusercontent.com/yeongseon/azure-functions-doctor-for-python/main/logo_assets/logo_full.png"
    alt="Azure Functions Doctor Logo"
    width="320"
  />
</p>

<p align="center">
    <!-- Test workflow status badge -->
  <a href="https://github.com/yeongseon/azure-functions-doctor-for-python/actions/workflows/test.yml">
    <img
      src="https://github.com/yeongseon/azure-functions-doctor-for-python/actions/workflows/test.yml/badge.svg"
      alt="Test Workflow Status"
    />
  </a>
  <!-- Release workflow status badge -->
  <a href="https://github.com/yeongseon/azure-functions-doctor-for-python/actions/workflows/release.yml">
    <img
      src="https://github.com/yeongseon/azure-functions-doctor-for-python/actions/workflows/release.yml/badge.svg"
      alt="Release Workflow Status"
    />
  </a>
  <!-- PyPI version badge -->
  <a href="https://pypi.org/project/azure-functions-doctor/">
    <img
      src="https://img.shields.io/pypi/v/azure-functions-doctor.svg"
      alt="PyPI Version"
    />
  </a>
  <!-- License badge -->
  <a href="LICENSE">
    <img
      src="https://img.shields.io/github/license/yeongseon/azure-functions-doctor-for-python.svg"
      alt="License"
    />
  </a>
  <!-- Coverage status badge (Codecov) -->
  <a href="https://codecov.io/gh/yeongseon/azure-functions-doctor-for-python">
    <img
      src="https://codecov.io/gh/yeongseon/azure-functions-doctor-for-python/branch/main/graph/badge.svg"
      alt="Codecov Coverage"
    />
  </a>
  <!-- Supported Python versions badge -->
  <a href="https://pypi.org/project/azure-functions-doctor/">
    <img
      src="https://img.shields.io/pypi/pyversions/azure-functions-doctor.svg"
      alt="Python Versions"
    />
  </a>
  <!-- Download count badge (Pepy)
  <a href="https://pepy.tech/project/azure-functions-doctor">
    <img
      src="https://pepy.tech/badge/azure-functions-doctor"
      alt="Downloads"
    />
  </a>
  -->
</p>

---

## 🤔 Why Azure Functions Doctor?

* You're getting random 500 errors and suspect misconfiguration?
* Need to verify your dev environment before CI/CD deployment?
* Want a quick health check without digging through docs?

This tool saves time by automating common Azure Functions environment diagnostics.

### 🚀 Key Features

* Diagnose Python version, venv, azure-functions package
* Validate host.json, local.settings.json, and function structure
* Fully customizable via `rules.json` (see [docs](https://yeongseon.github.io/azure-functions-doctor-for-python/rules/))

---

## 🩺 Overview

**Azure Functions Doctor** is a Python-based CLI tool designed to diagnose and validate your local Azure Functions environment.
This tool helps identify configuration issues, missing dependencies, or version mismatches commonly found in Python-based Azure Functions.

The behavior and rules for each check are defined declaratively in the `rules.json` file located in the project root. This file allows users and developers to customize or extend validation logic without modifying Python code directly.
📘 Learn more: [rules.json documentation](https://yeongseon.github.io/azure-functions-doctor-for-python/rules/)

---

## 🪠 Requirements

* Python 3.9+
* Git
* Optional: Azure Function Core Tools v4 (`npm i -g azure-functions-core-tools@4`)
* Recommended: Unix-like shell or PowerShell for Makefile support

---

## 📦 Installation

1. Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/yeongseon/azure-functions-doctor.git
cd azure-functions-doctor
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the tool:

```bash
pip install -e .
```

Alternatively, install from PyPI (when published):

```bash
pip install azure-functions-doctor
```

---

## 🩺 Usage

Navigate to your Azure Functions project directory, then run:

```bash
azfunc-doctor diagnose
```

To see all available commands:

```bash
azfunc-doctor --help
```

### ✅ Sample Output

```bash
azfunc-doctor diagnose
🩺 Azure Functions Doctor for Python v0.1.0
📁 Path: /root/Github/azure-functions-doctor/examples/basic-hello

✖ Python Env
  • Python version: Python version is 3.12.3, expected >=3.9
  • Virtual environment: VIRTUAL_ENV is set
  • Python executable: /root/.local/share/hatch/env/virtual/azure-functions-doctor/.../bin/python exists
  • requirements.txt: /root/Github/azure-functions-doctor/examples/basic-hello/requirements.txt exists
  • azure-functions package: Package 'azure_functions' is not installed

✖ Project Structure
  • host.json: exists
  • local.settings.json: is missing
  • main.py: is missing

Summary
✔ 0 Passed    ✖ 2 Failed
```

📌 Full output: [examples/basic-hello/diagnose-output.md](examples/basic-hello/diagnose-output.md)

---

## 💡 Example

A full example is available under [`examples/basic-hello`](examples/basic-hello), showing how to:

* Prepare a minimal Azure Functions app structure with only `host.json` and `requirements.txt`
* Run `azfunc-doctor` to simulate and inspect diagnosis results

---

## 📋 Documentation

For advanced usage and developer guides, visit the [project site](https://yeongseon.github.io/azure-functions-doctor-for-python/) or [GitHub repository](https://github.com/yeongseon/azure-functions-doctor-for-python).

---

## 🤝 Contributing

We welcome issues and pull requests!
See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines.

If you’ve found this tool helpful, please ⭐ the repo!

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
