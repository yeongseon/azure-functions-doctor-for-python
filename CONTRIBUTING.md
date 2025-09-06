# Contributing to Azure Functions Doctor

**Thank you for your interest in contributing to Azure Functions Doctor!**

We welcome all kinds of contributions:
- Bug reports and fixes
- New features and enhancements  
- Documentation improvements
- Tests and quality improvements
- Ideas and suggestions
- Translations and accessibility

This guide will help you get started as a contributor to our open source community.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Adding New Features](#adding-new-features)
- [Testing](#testing)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

---

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## Getting Started

### First Time Contributors

New to open source? Here are some good first issues to get started:
- Look for issues labeled `good first issue` or `help wanted`
- Check our [documentation](docs/) for areas that need improvement
- Fix typos or improve code comments
- Add tests for existing functionality

### Ways to Contribute

1. **Report Bugs**: Found a bug? [Create an issue](https://github.com/yeongseon/azure-functions-doctor-for-python/issues/new/choose)
2. **Suggest Features**: Have an idea? [Start a discussion](https://github.com/yeongseon/azure-functions-doctor-for-python/discussions)
3. **Improve Docs**: Documentation can always be better
4. **Write Code**: Pick an issue and submit a PR
5. **Review PRs**: Help review other contributors' work

---

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Instructions

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/azure-functions-doctor-for-python.git
   cd azure-functions-doctor-for-python
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/yeongseon/azure-functions-doctor-for-python.git
   ```

4. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

5. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

6. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

7. **Verify setup**:
   ```bash
   make check-all
   python -m azure_functions_doctor.cli diagnose --help
   ```

---

## Code Style

We maintain high code quality standards:

### Tools We Use
* **Formatter:** `black` - Consistent code formatting
* **Linter:** `ruff` - Fast Python linter
* **Type checker:** `mypy` - Static type checking
* **Import sorting:** `isort` - Consistent import ordering

### Code Standards
* Follow PEP 8 Python style guide
* Use type hints for all function signatures
* Write descriptive variable and function names
* Add docstrings for public functions and classes
* Keep functions focused and small
* Use meaningful commit messages (Conventional Commits)

### Before Submitting
```bash
make format      # Format code with black
make lint        # Lint with ruff
make typecheck   # Type check with mypy
make test        # Run tests
make check-all   # Run all checks
```

---

## Adding New Features

### Adding New Diagnostic Rules

Our diagnostic system is designed to be easily extensible:

1. **Define the rule** in `src/azure_functions_doctor/assets/rules/v2.json` (and/or `v1.json` for v1 projects):
   ```json
   {
     "id": "check_my_feature",
     "type": "my_check_type",
     "label": "My Feature Check",
     "description": "Checks if my feature is properly configured",
     "section": "my_section",
     "required": true,
     "severity": "error",
     "condition": {
       "target": "my_target"
     },
     "hint": "How to fix this issue",
     "hint_url": "https://docs.example.com/fix-guide"
   }
   ```

2. **Implement the handler** in `src/azure_functions_doctor/handlers.py`:
   ```python
   def my_check_handler(rule: Rule, path: Path) -> dict[str, str]:
       # Implementation here
       return _create_result("pass", "Check passed")
   ```

3. **Add handler to dispatcher** in `generic_handler` function

4. **Write tests** in `tests/test_handler.py`

5. **Update documentation** if needed

### Architecture Overview

```
src/azure_functions_doctor/
├── cli.py           # CLI interface and logging setup
├── doctor.py        # Core diagnostic engine
├── handlers.py      # Individual check implementations
├── logging_config.py # Centralized logging system
├── target_resolver.py # Version resolution utilities
└── assets/
   └── rules/
      ├── v1.json
      └── v2.json
```

### Handler Guidelines

- Always return `{"status": str, "detail": str}`
- Use `_create_result()` for consistent responses
- Handle exceptions with `_handle_exception()`
- Add appropriate logging with `logger.debug()` or `logger.warning()`
- Keep handlers focused on a single responsibility
- Add comprehensive error handling

---

## Pull Request Process

### Before Creating a PR

1. **Sync with upstream**:
   ```bash
   git checkout main
   git pull upstream main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```

3. **Make your changes** and test thoroughly

4. **Run all checks**:
   ```bash
   make check-all
   ```

5. **Commit with conventional commits**:
   ```bash
   git commit -m "feat(handlers): add new diagnostic rule for X"
   ```

### PR Requirements

- Branch from `main`
- Use [Conventional Commits](https://www.conventionalcommits.org/) format
- Include tests for new functionality
- Update documentation if needed
- Keep PRs focused and atomic
- Ensure all CI checks pass
- Add screenshots for UI changes
- Link related issues with `Fixes #123`

### PR Template

When creating a PR, please include:
- **Description**: What does this PR do?
- **Motivation**: Why is this change needed?
- **Testing**: How was this tested?
- **Screenshots**: For visual changes
- **Checklist**: Confirm all requirements met

### Review Process

1. Automated CI checks must pass
2. At least one maintainer review required
3. Address review feedback promptly
4. Keep discussions respectful and constructive
5. PRs are typically reviewed within 2-3 business days

---

## Testing Guidelines

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make cov

# Run specific test file
python -m pytest tests/test_handlers.py -v

# Run tests with debugging
python -m pytest tests/ -v -s
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names: `test_handler_returns_fail_when_package_missing`
- Mock external dependencies
- Test both success and failure cases
- Keep tests focused and independent

---

## Community

### Getting Help

- [GitHub Discussions](https://github.com/yeongseon/azure-functions-doctor-for-python/discussions) - General questions and ideas
- [GitHub Issues](https://github.com/yeongseon/azure-functions-doctor-for-python/issues) - Bug reports and feature requests
- [Documentation](docs/) - Comprehensive guides and API reference

### Stay Connected

- Star the repository to show support
- Watch for updates and releases
- Fork to experiment with your own changes
- Share the project with others who might find it useful

### Recognition

All contributors are recognized in our:
- [Contributors section](https://github.com/yeongseon/azure-functions-doctor-for-python/graphs/contributors)
- Release notes for significant contributions
- Special thanks in documentation

---

## Contribution Checklist

Before submitting your contribution:

- [ ] I have read and agree to the [Code of Conduct](CODE_OF_CONDUCT.md)
- [ ] I have searched existing issues and PRs
- [ ] I have tested my changes thoroughly
- [ ] I have added/updated tests as needed
- [ ] I have updated documentation as needed
- [ ] My code follows the project's style guidelines
- [ ] All CI checks pass
- [ ] I have used descriptive commit messages

---

## Thank You!

Your contributions make this project better for everyone. Whether you're fixing a typo, adding a feature, or helping other users - every contribution matters!

Welcome to the Azure Functions Doctor community!