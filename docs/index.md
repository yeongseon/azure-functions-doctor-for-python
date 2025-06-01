# Azure Functions Doctor 🩺⚡

**Azure Functions Doctor** is a Python-based CLI tool that diagnoses and validates your local Azure Functions environment.
It helps identify common issues such as missing files, version mismatches, or misconfigurations in your project setup.

---

## 🔍 Why Use This Tool?

* ✅ You're getting random 500 errors and suspect a misconfigured environment?
* ✅ You want to sanity-check your project before deploying to Azure?
* ✅ You prefer structured output over guesswork?

Let Azure Functions Doctor help you save time and debug faster.

---

## 🚀 Key Features

* 🐍 Diagnose Python version, virtual environment, and dependencies
* 📁 Validate Azure Functions project structure (`host.json`, `function.json`, `main.py`, etc.)
* 📦 Check if required packages (like `azure-functions`) are installed
* 📄 Validate presence of config files like `requirements.txt` and `local.settings.json`
* 💡 Developer-friendly output with emoji indicators and summary section
* 🛠 Easily extendable via `rules.json` and handler functions
