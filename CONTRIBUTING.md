# Contributing to Azure Functions Doctor

Thanks for your interest in contributing! Whether it's bug reports, feature requests, code contributions, or documentation — we appreciate your support.

---

## 🧰 Development Setup

1. Clone the repository:

```bash
git clone https://github.com/yeongseon/azure-functions-doctor.git
cd azure-functions-doctor
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -e ".[dev]"
```

4. Run checks before committing:

```bash
make check-all
```

---

## 📐 Code Style

We follow these conventions:

* **Formatter:** `black`
* **Linter:** `ruff`
* **Type checker:** `mypy`

Use `make format lint typecheck` before submitting.

---

## 🧪 Running Tests

To run unit tests:

```bash
make test
```

To view coverage:

```bash
make cov
```

---

## ✍️ Adding New Checks

New rule logic should be defined declaratively in `rules.json`.

Each rule in `rules.json` is associated with a `type` field that determines which handler function will be used to process it.

You can add or modify handlers in:

```
src/azure_functions_doctor/handlers.py
```

The core logic that loads rules and dispatches handlers is in:

```
src/azure_functions_doctor/doctor.py
```

To create a new check type:

* Add a new entry to `rules.json` with a unique `type`
* Implement a corresponding handler function in `handlers.py`
* Ensure it follows the expected input/output pattern

---

## ✅ Pull Request Guidelines

* Branch from `main`
* Use Conventional Commits (e.g. `feat:`, `fix:`, `docs:`)
* Include or update tests where applicable
* Keep PRs focused and minimal
* Add/update documentation when relevant

---

## 🗣 Feedback & Suggestions

If you're not ready to contribute code, feel free to open:

* GitHub **Discussions** for ideas
* GitHub **Issues** for bugs or requests

We love hearing from users and contributors alike!

---

Thanks again for contributing 💙
