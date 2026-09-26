#!/usr/bin/env python3
"""Safely add or update the Happy AI Work section in Codex home AGENTS.md."""

from __future__ import annotations

import argparse
import difflib
import io
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

START = "<!-- happy-ai-work:start -->"
END = "<!-- happy-ai-work:end -->"
YOHAKU_KEY = "happy-ai-work:yohaku"


def managed_body(text: str, *, required: bool = False) -> str | None:
    if START not in text and END not in text and not required:
        return None
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("incomplete or duplicate managed-section markers")
    start, end = text.index(START), text.index(END)
    if start >= end:
        raise ValueError("managed-section markers are reversed")
    return text[start + len(START):end]


def yohaku_state(body: str | None) -> str | None:
    lines = [line.strip() for line in (body or "").splitlines() if YOHAKU_KEY in line]
    if not lines:
        return None
    if len(lines) == 1:
        for state in ("enabled", "disabled"):
            if lines[0] == f"<!-- {YOHAKU_KEY}={state} -->":
                return state
    raise ValueError("invalid or duplicate Yohaku state; resolve the managed section first")


def compose(existing: str, template: str, choice: str, startup_path: Path) -> str:
    state = yohaku_state(managed_body(existing))
    managed_body(template, required=True)
    if YOHAKU_KEY in template:
        raise ValueError("base template must not contain Yohaku state metadata")
    if choice != "preserve":
        state = {"enable": "enabled", "disable": "disabled"}[choice]
    if state is None:
        return template
    option = f"<!-- {YOHAKU_KEY}={state} -->\n"
    if state == "enabled":
        option += startup_path.read_text(encoding="utf-8").strip() + "\n"
    before, after = template.split(END, 1)
    if not before.endswith("\n"):
        before += "\n"
    return before + option + END + after


def codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def merge(existing: str, managed: str) -> str:
    managed = managed.strip() + "\n"
    managed_body(managed, required=True)
    if managed_body(existing) is not None:
        before, remainder = existing.split(START, 1)
        _, after = remainder.split(END, 1)
        return before + managed.rstrip("\n") + after
    if not existing:
        return managed
    if existing.endswith(("\n\n", "\r\n\r\n")):
        separator = ""
    else:
        separator = "\n" if existing.endswith("\n") else "\n\n"
    return existing + separator + managed


def main() -> int:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="show the diff without writing (default)")
    mode.add_argument("--apply", action="store_true", help="write after creating a backup")
    parser.add_argument("--target", type=Path, help="override the AGENTS.md path for testing")
    parser.add_argument("--template", type=Path, help="override the managed template path")
    parser.add_argument(
        "--yohaku", choices=("preserve", "enable", "disable"), default="preserve",
        help="preserve the saved startup preference (default), or explicitly change it",
    )
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parent.parent
    template_path = args.template or skill_root / "assets" / "AGENTS.md"
    target = args.target or codex_home() / "AGENTS.md"
    try:
        existing = target.read_bytes().decode("utf-8") if target.exists() else ""
        managed = compose(
            existing, template_path.read_text(encoding="utf-8"), args.yohaku,
            skill_root / "assets" / "yohaku-startup.md",
        )
        updated = merge(existing, managed)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

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
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        backup = target.with_name(f"{target.name}.{stamp}.bak")
        backup.write_bytes(existing.encode("utf-8"))
        print(f"backup: {backup}")
    target.write_bytes(updated.encode("utf-8"))
    print("applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
