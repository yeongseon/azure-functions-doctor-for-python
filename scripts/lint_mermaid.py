#!/usr/bin/env python3
"""Lightweight structural linter for Mermaid code blocks in Markdown docs.

This does not require a headless browser or node toolchain. It catches the
common regressions that break Mermaid rendering on GitHub / MkDocs:

* an empty ```mermaid block,
* a block whose first meaningful line is not a known diagram type,
* unbalanced brackets ``()``, ``[]`` or ``{}`` (a frequent copy/paste error),
* literal ``\\n`` inside node labels (GitHub renders ``<br/>`` reliably but not
  escaped newlines).

Usage:
    python scripts/lint_mermaid.py            # scan tracked docs
    python scripts/lint_mermaid.py README.md  # scan specific files
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent

# Directories we never want to scan.
SKIP_DIRS = {".venv", "node_modules", ".git", "site", "dist", "build"}

# Recognised Mermaid diagram declarations (first meaningful token of a block).
DIAGRAM_TYPES = (
    "flowchart",
    "graph",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "journey",
    "gantt",
    "pie",
    "gitGraph",
    "mindmap",
    "timeline",
    "quadrantChart",
    "requirementDiagram",
    "C4Context",
)

BLOCK_RE = re.compile(r"^```mermaid[^\n]*\n(.*?)^```", re.MULTILINE | re.DOTALL)


def _iter_markdown_files(args: list[str]) -> list[Path]:
    if args:
        return [Path(a) for a in args]
    files: list[Path] = []
    for path in ROOT.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        files.append(path)
    return sorted(files)


def _lint_block(block: str) -> list[str]:
    errors: list[str] = []
    meaningful = [
        line.strip()
        for line in block.splitlines()
        if line.strip() and not line.strip().startswith("%%")
    ]
    if not meaningful:
        return ["empty mermaid block"]

    first = meaningful[0]
    if not first.startswith(DIAGRAM_TYPES):
        errors.append(f"unknown diagram type: {first!r}")

    joined = "\n".join(meaningful)
    for open_ch, close_ch in (("(", ")"), ("[", "]"), ("{", "}")):
        if joined.count(open_ch) != joined.count(close_ch):
            errors.append(
                f"unbalanced '{open_ch}{close_ch}' "
                f"({joined.count(open_ch)} vs {joined.count(close_ch)})"
            )
    if "\\n" in joined:
        errors.append("literal '\\n' in label — use '<br/>' for line breaks")
    return errors


def main(argv: list[str]) -> int:
    failures = 0
    scanned = 0
    for path in _iter_markdown_files(argv):
        text = path.read_text(encoding="utf-8")
        for match in BLOCK_RE.finditer(text):
            scanned += 1
            block = match.group(1)
            line_no = text[: match.start()].count("\n") + 1
            for err in _lint_block(block):
                failures += 1
                rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
                print(f"{rel}:{line_no}: mermaid: {err}")
    if failures:
        print(f"\nMermaid lint FAILED: {failures} problem(s) across {scanned} block(s).")
        return 1
    print(f"Mermaid lint passed ({scanned} block(s) checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
