#!/usr/bin/env python3
"""Safely add or update the Happy AI Work section in Codex home AGENTS.md."""

from __future__ import annotations

import argparse
import difflib
import os
from datetime import UTC, datetime
from pathlib import Path

START = "<!-- happy-ai-work:start -->"
END = "<!-- happy-ai-work:end -->"


def codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def merge(existing: str, managed: str) -> str:
    managed = managed.strip() + "\n"
    if START not in managed or END not in managed:
        raise ValueError("template is missing managed-section markers")
    if START in existing or END in existing:
        if existing.count(START) != 1 or existing.count(END) != 1:
            raise ValueError("existing AGENTS.md has incomplete or duplicate markers")
        before, remainder = existing.split(START, 1)
        _, after = remainder.split(END, 1)
        return before.rstrip() + "\n\n" + managed + after.lstrip("\r\n")
    if not existing.strip():
        return managed
    return existing.rstrip() + "\n\n" + managed


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="show the diff without writing (default)")
    mode.add_argument("--apply", action="store_true", help="write after creating a backup")
    parser.add_argument("--target", type=Path, help="override the AGENTS.md path for testing")
    parser.add_argument("--template", type=Path, help="override the managed template path")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parent.parent
    template_path = args.template or skill_root / "assets" / "AGENTS.md"
    target = args.target or codex_home() / "AGENTS.md"
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    updated = merge(existing, template_path.read_text(encoding="utf-8"))

    print(f"target: {target}")
    print("".join(difflib.unified_diff(
        existing.splitlines(keepends=True),
        updated.splitlines(keepends=True),
        fromfile=str(target),
        tofile=str(target),
    )), end="")

    if not args.apply:
        print("dry-run: no files changed")
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and updated != existing:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        backup = target.with_name(f"{target.name}.{stamp}.bak")
        backup.write_text(existing, encoding="utf-8")
        print(f"backup: {backup}")
    target.write_text(updated, encoding="utf-8")
    print("applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
