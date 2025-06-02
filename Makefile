# ------------------------------
# 🧰 Hatch Environment Management
# ------------------------------

.PHONY: install
install:
	@hatch env create
	@make precommit-install

.PHONY: shell
shell:
	@hatch shell

.PHONY: reset
reset: clean-all install
	@echo "🔁 Project reset complete."

.PHONY: hatch-clean
hatch-clean:
	@hatch env remove || echo "⚠️ No hatch environment to remove"

# ------------------------------
# 🧹 Code Quality
# ------------------------------

.PHONY: format
format:
	@hatch run format

.PHONY: style
style:
	@hatch run style

.PHONY: typecheck
typecheck:
	@hatch run typecheck

.PHONY: lint
lint:
	@hatch run lint

.PHONY: check
check:
	@make lint
	@make typecheck
	@echo "✅ Lint & type check passed!"

.PHONY: check-all
check-all:
	@make check
	@make test
	@echo "✅ All checks passed including tests!"

.PHONY: precommit
precommit:
	@hatch run precommit

.PHONY: precommit-install
precommit-install:
	@hatch run precommit-install

# ------------------------------
# 🧪 Testing & Coverage
# ------------------------------

.PHONY: test
test:
	@echo "🔬 Running tests..."
	@hatch run test

.PHONY: cov
cov:
	@hatch run cov
	@hatch run coverage xml
	@echo "📂 Open htmlcov/index.html in your browser to view the coverage report"
	@echo "📝 coverage.xml generated for Codecov upload"

# ------------------------------
# 📦 Build & Release
# ------------------------------

.PHONY: build
build:
	@hatch build

.PHONY: changelog
changelog:
	@git-cliff -o CHANGELOG.md
	@echo "📝 Changelog generated."

.PHONY: commit-changelog
commit-changelog:
	@git add CHANGELOG.md
	@git commit -m "docs: update changelog" || echo "⚠️ No changes to commit"

.PHONY: tag-release
tag-release:
ifndef VERSION
	$(error VERSION is not set. Usage: make tag-release VERSION=1.0.1)
endif
	@git tag -a v$(VERSION) -m "Release v$(VERSION)"
	@git push origin v$(VERSION)
	@echo "🚀 Tagged release v$(VERSION)"

.PHONY: release
release:
ifndef VERSION
	$(error VERSION is not set. Usage: make release VERSION=1.0.1)
endif
	@hatch version $(VERSION)
	@$(MAKE) release-core VERSION=$(VERSION)

.PHONY: release-core
release-core:
ifndef VERSION
	$(error VERSION is not set. Usage: make release-core VERSION=1.0.1)
endif
	@$(MAKE) changelog
	@$(MAKE) commit-changelog
	@$(MAKE) tag-release VERSION=$(VERSION)

.PHONY: release-patch
release-patch:
	@hatch version patch
	@VERSION=$$(hatch version | tail -n1); \
	 git add src/azure_functions_doctor/__init__.py && \
	 git commit -m "build: bump version to $$VERSION" && \
	 $(MAKE) release-core VERSION=$$VERSION

.PHONY: release-minor
release-minor:
	@hatch version minor
	@VERSION=$$(hatch version | tail -n1); \
	 git add src/azure_functions_doctor/__init__.py && \
	 git commit -m "build: bump version to $$VERSION" && \
	 $(MAKE) release-core VERSION=$$VERSION

.PHONY: release-major
release-major:
	@hatch version major
	@VERSION=$$(hatch version | tail -n1); \
	 git add src/azure_functions_doctor/__init__.py && \
	 git commit -m "build: bump version to $$VERSION" && \
	 $(MAKE) release-core VERSION=$$VERSION

.PHONY: publish
publish:
	@hatch publish

# ------------------------------
# 📚 Documentation
# ------------------------------

.PHONY: docs
docs:
	@hatch run mkdocs build

.PHONY: docs-serve
docs-serve:
	@hatch run mkdocs serve

# ------------------------------
# 🩺 Diagnostic
# ------------------------------

.PHONY: doctor
doctor:
	@echo "🔍 Python version:" && python --version
	@echo "🔍 Installed packages:" && hatch env run pip list || echo "⚠️ No hatch env found"
	@echo "🔍 Azure Function Core Tools version:" && func --version || echo "⚠️ func not found. Install with: npm i -g azure-functions-core-tools@4"
	@echo "🔍 Pre-commit hook installed:"
	@if [ -f .git/hooks/pre-commit ]; then echo ✅ Yes; else echo ❌ No; fi

# ------------------------------
# 🧹 Clean
# ------------------------------

.PHONY: clean
clean:
	@rm -rf *.egg-info dist build __pycache__ .pytest_cache

.PHONY: clean-all
clean-all: clean
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
	@rm -rf .mypy_cache .ruff_cache .pytest_cache .coverage coverage.xml htmlcov .DS_Store

# ------------------------------
# 🆘 Help
# ------------------------------

.PHONY: help
help:
	@echo "📖 Available commands:" && \
	grep -E '^\.PHONY: ' Makefile | cut -d ':' -f2 | xargs -n1 echo "  - make"
