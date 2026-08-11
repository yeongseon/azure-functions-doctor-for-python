# Migrating off deprecated command aliases

`azure-functions-doctor` is the **canonical** command. Two legacy console-script
aliases — `azure-functions` and `fdoctor` — still work but are **deprecated** and
print a warning to stderr when invoked. Both are scheduled for removal in
**v1.0.0**.

This guide explains what changes, why, and exactly how to migrate scripts and CI
pipelines before the aliases are removed.

## What is deprecated

| Command | Status | Action |
| --- | --- | --- |
| `azure-functions-doctor` | Canonical | Use this. No change needed. |
| `azure-functions` | Deprecated (removal in v1.0.0) | Replace with `azure-functions-doctor`. |
| `fdoctor` | Deprecated (removal in v1.0.0) | Replace with `azure-functions-doctor`. |

The deprecated aliases are thin wrappers. They emit a one-line deprecation notice
to stderr and then delegate to the exact same diagnostics engine as
`azure-functions-doctor`, so **behavior and exit codes are identical** during the
deprecation window. Only the invocation name changes.

## Why the change

Multiple entry points for one tool cause avoidable friction:

- **Discoverability** — `azure-functions` collides conceptually with the
  `azure-functions` PyPI SDK package, and `fdoctor` is not self-describing.
- **Documentation drift** — every example, CI snippet, and troubleshooting note
  has to be kept correct for three names instead of one.
- **Predictable tooling** — a single canonical command is easier to pin, cache,
  and reason about in automation.

Consolidating on `azure-functions-doctor` removes that ambiguity.

## How to migrate

### 1. Shell scripts and local usage

Replace the alias with the canonical command:

```bash
# Before
fdoctor --path .
azure-functions doctor --path .

# After
azure-functions-doctor doctor --path .
```

### 2. GitHub Actions

```yaml
# Before
- run: |
    pip install azure-functions-doctor
    fdoctor doctor --profile minimal --format json --output doctor.json

# After
- run: |
    pip install azure-functions-doctor
    azure-functions-doctor doctor --profile minimal --format json --output doctor.json
```

### 3. Makefiles and task runners

```makefile
# Before
doctor:
	fdoctor doctor --path .

# After
doctor:
	azure-functions-doctor doctor --path .
```

### 4. pre-commit hooks

```yaml
# Before
- id: azure-functions-doctor
  entry: fdoctor doctor
# After
- id: azure-functions-doctor
  entry: azure-functions-doctor doctor
```

## Finding remaining usages

Search your repository for the deprecated names before v1.0.0:

```bash
grep -rnE '\b(fdoctor|azure-functions doctor)\b' \
  --include='*.sh' --include='*.yml' --include='*.yaml' \
  --include='Makefile' --include='*.mk' .
```

Anything the search returns should be updated to `azure-functions-doctor`.

## Timeline

- **Now** — Aliases work and print a deprecation warning on stderr. No breakage.
- **v1.0.0** — Aliases are removed. `fdoctor` and `azure-functions` will no longer
  resolve; only `azure-functions-doctor` remains.

Migrate before upgrading to v1.0.0 to avoid `command not found` failures in CI.
