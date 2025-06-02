# 🛠 Release Process

This document describes how to release a new version of **Azure Functions Doctor** to PyPI and update the changelog.

---

## 🧾 Step 1: Update the Version

Use Hatch to bump the version and generate changelog:

```bash
make release-patch   # or: release-minor, release-major
```

This will:

- Update the version in `pyproject.toml`
- Generate `CHANGELOG.md` via `git-cliff`
- Commit changelog
- Tag the commit (e.g. `v0.2.0`)
- Push the tag to GitHub

---

## 📦 Step 2: Publish to PyPI

Build and upload the package:

```bash
make build
make publish
```

This will upload the package to [PyPI](https://pypi.org/project/azure-functions-doctor/).

> 🔒 Make sure your `~/.pypirc` is correctly configured with PyPI credentials.

---

## ✅ Summary

| Task                  | Command                          |
|-----------------------|----------------------------------|
| Version bump + changelog | `make release-patch`         |
| Build package         | `make build`                     |
| Publish to PyPI       | `make publish`                   |

---

## 🔁 Test on TestPyPI (Optional)

```bash
hatch build
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ azure-functions-doctor
```
