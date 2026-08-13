# Rule Stability and Semver Policy

This document defines how built-in rules evolve over time so that users can rely on Azure Functions Doctor in both local and CI workflows.

## Rule States

Every built-in rule has one of three stability states:

| State | Meaning |
| --- | --- |
| **Stable** | Fully supported. False positives are treated as bugs. |
| **Experimental** | Under evaluation. May change behavior or be removed in a minor release. False positives are documented as known limitations. |
| **Deprecated** | Scheduled for removal. Announced in the changelog and removed in the next major release. |

All 29 current built-in rules are **stable**.

## State Transitions

- **Experimental to Stable**: Requires test coverage and at least one minor release cycle without breaking changes.
- **Stable to Deprecated**: Announced in the changelog. The rule continues to run until the next major release.
- **Deprecated to Removed**: Occurs only in a major release.

## Versioning Impact

| Change | Version Bump |
| --- | --- |
| Add an optional rule to the `full` profile | Minor |
| Add a required rule to the `minimal` profile | **Major** (breaking) |
| Change the meaning of a required rule | **Major** (breaking) |
| Change the meaning of an optional rule | Minor |
| Remove a deprecated rule | **Major** |
| Fix a false positive in a stable rule | Patch |
| Add an experimental rule | Minor |
| Change or remove an experimental rule | Minor |

## Profile Change Policy

The `minimal` profile runs only rules marked `required: true`. Because CI pipelines depend on minimal producing a stable, predictable set of checks:

- Adding a rule to `minimal` (marking it `required: true`) is a **breaking change** and requires a major version bump.
- Adding optional rules to `full` is a minor change.
- Removing an optional rule from `full` follows the deprecation path above.

## False-positive Handling

- **Stable rules**: False positives are bugs. They are fixed in patch releases.
- **Experimental rules**: False positives are documented as known limitations in the rule description or changelog.
- **Deprecated rules**: False positives are not fixed; users should migrate away.

## Current Rule Status

All 29 rules in `v2.json` are **stable**. See the [Rule Inventory](rule_inventory.md) for the complete list.
