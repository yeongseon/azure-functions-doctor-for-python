# ------------------------------
# 🔧 Environment Setup
# ------------------------------

.PHONY: install
install:
	hatch env create
	hatch run precommit-install

.PHONY: shell
shell:
	hatch shell

.PHONY: hatch-clean
hatch-clean:
	hatch env remove default || true
	rm -rf .hatch

.PHONY: reset
reset: clean-all hatch-clean install
	@echo "🔁 Project reset complete."

# ------------------------------
# 🧹 Code Quality
# ------------------------------

.PHONY: format
format:
	hatch run format

.PHONY: lint
lint:
	hatch run lint

.PHONY: typecheck
typecheck:
	hatch run typecheck

.PHONY: check
check:
	hatch run check

.PHONY: precommit
precommit:
	hatch run precommit

.PHONY: precommit-install
precommit-install:
	hatch run precommit-install

# ------------------------------
# 🧪 Testing & Coverage
# ------------------------------

.PHONY: test
test:
	hatch run test

.PHONY: cov
cov:
	hatch run cov

.PHONY: tox
tox:
	hatch run tox

# ------------------------------
# 📦 Build & Release
# ------------------------------

.PHONY: build
build:
	hatch build

.PHONY: release
release:
	cz bump --changelog

.PHONY: release-patch
release-patch:
	cz bump --increment patch --changelog

.PHONY: release-minor
release-minor:
	cz bump --increment minor --changelog

.PHONY: release-major
release-major:
	cz bump --increment major --changelog

.PHONY: publish
publish:
	hatch publish

# ------------------------------
# 📚 Documentation
# ------------------------------

.PHONY: docs
docs:
	hatch run docs

# ------------------------------
# 🩺 Diagnostic
# ------------------------------

.PHONY: doctor
doctor:
	@echo "🔍 Python version:"
	@python --version
	@echo "🔍 Installed packages:"
	@hatch run pip list
	@echo "🔍 Azure Function Core Tools version:"
	@func --version || echo "⚠️ func not found. Install with: npm i -g azure-functions-core-tools@4"
	@echo "🔍 Pre-commit hook installed:"
	@test -e .git/hooks/pre-commit && echo "✅ Yes" || echo "❌ No"

# ------------------------------
# 🧹 Clean
# ------------------------------

.PHONY: clean
clean:
	rm -rf dist build .mypy_cache .ruff_cache .pytest_cache .coverage coverage.xml htmlcov .DS_Store

.PHONY: clean-all
clean-all: clean
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	rm -rf .hatch .venv .tox

# ------------------------------
# 🆘 Help
# ------------------------------

.PHONY: help
help:
	@echo "📖 Available commands:"
	@grep -E '^\.PHONY: ' Makefile | cut -d ':' -f2 | xargs -n1 echo "  - make"
