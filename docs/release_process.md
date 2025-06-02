# 🛠️ Release Process

This document outlines the steps to release a new version of **Azure Functions Doctor** to PyPI and update the changelog, using the existing Makefile and Hatch-based workflows.

---

## 🧾 Step 1: Bump Version and Generate Changelog

Use the Makefile targets to bump the version and update the changelog:

```bash
# Patch release (e.g., v0.1.0 → v0.1.1)
make release-patch

# Minor release (e.g., v0.1.1 → v0.2.0)
make release-minor

# Major release (e.g., v0.2.0 → v1.0.0)
make release-major
```

Each command will:
- Update the version in `pyproject.toml` and `src/azure_functions_doctor/__init__.py`
- Generate or update `CHANGELOG.md` based on Git commit history (`git-cliff`)
- Commit the updated changelog and version bump
- Create a Git tag (e.g., `v0.2.0`)
- Push commits and tags to the `main` branch

> **Tip**: Ensure your local branch is up-to-date with `main` before running these commands.

---

## 📦 Step 2: Build and Test the Package

Before publishing, build and verify locally:

```bash
# Create source and wheel distributions
make build

# (Optional) Install from the local distribution to test
pip install dist/azure_functions_doctor-<version>-py3-none-any.whl
```

Verify installation:

```bash
func-doctor --version
```

---

## 🚀 Step 3: Publish to PyPI

Once the build artifacts are validated, upload the package to PyPI:

```bash
make publish
```

This runs:
- `hatch release` under the hood (builds, signs if configured, and uploads)
- Uses credentials from `~/.pypirc` or environment variables (`PYPI_USERNAME`/`PYPI_PASSWORD`)
- Verifies successful upload by checking PyPI listing

> **Security**: Ensure that your PyPI API token or credentials are stored securely and not committed to source control.

---

## 🔁 Step 4: Test on TestPyPI (Optional)

If you want to verify the upload workflow without affecting production releases:

1. Build the package:

   ```bash
   make build
   ```

2. Upload to TestPyPI:

   ```bash
   twine upload --repository testpypi dist/*
   ```

3. Install from TestPyPI:

   ```bash
   pip install --index-url https://test.pypi.org/simple/ azure-functions-doctor
   ```

4. Verify version:

   ```bash
   func-doctor --version
   ```

---

## ✅ Summary of Release Commands

| Task                          | Command                          |
|-------------------------------|----------------------------------|
| Version bump + changelog      | `make release-patch`             |
| Build distributions           | `make build`                     |
| Publish to PyPI               | `make publish`                   |
| Test on TestPyPI (optional)   | `twine upload --repository testpypi dist/*` |

---

## 🔗 Related Documentation

- [CHANGELOG.md](CHANGELOG.md)
- [Development Guide](development.md)
- [Makefile Targets](development.md#%EB%AC%B8%EC%84%9C)
- [PyPI Publishing with Hatch](https://hatch.pypa.io/latest/publishing/)