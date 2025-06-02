# 🩺 Azure Functions Doctor

Welcome to **Azure Functions Doctor** — a powerful diagnostic CLI tool built with Python to help you validate and troubleshoot your local Azure Functions environment.

---

## ⚡ What Is It?

**Azure Functions Doctor** analyzes your project folder and environment to detect:

- Missing configuration files (e.g., `host.json`, `requirements.txt`)
- Unsupported Python versions
- Missing dependencies (e.g., `azure-functions`)
- Broken or misnamed function folders
- Other common issues that break Azure Functions locally or in CI/CD

It provides **clear emoji-based output**, **rule-based extensibility**, and **optional JSON formatting**.

---

## 🚀 When Should You Use This?

| Scenario | Usefulness |
|----------|------------|
| 🧪 Developing locally | Quickly catch broken setup before you run `func start` |
| 🚢 Before deployment | Prevent silent 500 errors caused by bad config |
| 🔁 In CI pipeline | Automate validation across repos and branches |
| 🛠 Debugging errors | Eliminate basic mistakes before diving into logs |

---

## 🧰 Quick Start

```bash
pip install azure-functions-doctor
func-doctor diagnose
```

View [Usage Guide](usage.md) →  
See [Example Project](../examples/basic-hello/README.md) →

---

## 📘 Documentation Overview

| Topic | Description |
|-------|-------------|
| [Usage Guide](usage.md) | How to run and interpret results |
| [Rule System](rules.md) | Understand and customize `rules.json` |
| [Diagnostics Reference](diagnostics.md) | Full list of built-in checks |
| [Developer Guide](development.md) | Contribute and extend the CLI |
| [Release Process](release_process.md) | Versioning and PyPI publishing |

---

## 💬 Need Help?

Feel free to [open an issue](https://github.com/yeongseon/azure-functions-doctor-for-python/issues) or check out our [GitHub Discussions](https://github.com/yeongseon/azure-functions-doctor-for-python/discussions).

---

## 🧪 Example Output

![CLI output](assets/func-doctor-example.png)

---

## 📄 License

This project is licensed under the [MIT License](../LICENSE).