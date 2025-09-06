# Release Process

This document outlines the steps to release a new version of **Azure Functions Doctor** to PyPI and update the changelog using the existing Makefile and Hatch-based workflows.

---

## 🧾 Step 1: Bump Version and Generate Changelog

Use Makefile targets to bump the version and update the changelog:

```bash
make release-patch     # Patch release (e.g., v0.1.0 → v0.1.1)
make release-minor     # Minor release (e.g., v0.1.1 → v0.2.0)
make release-major     # Major release (e.g., v0.2.0 → v1.0.0)
```

Each command will:
- Update the version in `src/azure_functions_doctor/__init__.py`
- Generate or update `CHANGELOG.md` via `git-cliff`
- Commit the version bump and changelog
- Create a Git tag (e.g., `v0.2.0`) and push to `main`

> Make sure your `main` branch is up-to-date before running these commands.

---

## Step 2: Build and Test the Package

```bash
make build
```

To test the local build:

```bash
pip install dist/azure_functions_doctor-<version>-py3-none-any.whl
azure-functions --version
```


## Step 3: Publish to PyPI

```bash
make publish-pypi
```

- Uses `hatch publish` under the hood
- Relies on `.pypirc` for authentication (`~/.pypirc` must contain PyPI token)
- No need for `twine`

---

## 🔁 Step 4: (Optional) Publish to TestPyPI

```bash
make publish-test
```

To install from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ azure-functions-doctor
```

---

## ✅ Summary of Makefile Commands

| Task                          | Command             |
|-------------------------------|---------------------|
| Version bump + changelog      | `make release-patch`|
| Build distributions           | `make build`        |
| Publish to PyPI               | `make publish-pypi` |
| Publish to TestPyPI           | `make publish-test` |

---

## 🔗 Related Documentation

- [CHANGELOG.md](CHANGELOG.md)
- [Development Guide](docs/development.md)
- [Makefile Targets](Makefile)
- [PyPI Publishing with Hatch](https://hatch.pypa.io/latest/publishing/)
