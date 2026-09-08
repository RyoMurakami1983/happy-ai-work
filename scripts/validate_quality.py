#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = ["PyYAML==6.0.3"]
# ///
"""Run the repository's reproducible quality checks."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON_VERSION = "3.14"
PYYAML_VERSION = "6.0.3"
RUFF_VERSION = "0.16.3"
TY_VERSION = "0.0.74"


def build_uvx_command(
    tool: str,
    version: str,
    arguments: list[str],
    *,
    offline: bool = False,
    with_packages: tuple[str, ...] = (),
) -> list[str]:
    command = ["uvx"]
    if offline:
        command.append("--offline")
    for package in with_packages:
        command.extend(["--with", package])
    command.extend([f"{tool}@{version}", *arguments])
    return command


def run_step(label: str, command: list[str]) -> bool:
    print(f"\n== {label} ==")
    print(subprocess.list2cmdline(command))
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode:
        print(f"FAILED ({result.returncode}): {label}", file=sys.stderr)
        return False
    return True


def worktree_status() -> str:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate this repository with Python 3.14 and pinned temporary tools."
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Require Ruff and ty to resolve from the existing uv cache.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if shutil.which("uvx") is None:
        print(
            "uvx was not found. Install uv or run this command in an environment where uv is on PATH.",
            file=sys.stderr,
        )
        return 2

    before = worktree_status()
    passed = True

    passed &= run_step(
        "repository validator", [sys.executable, str(ROOT / "scripts" / "validate_repo.py")]
    )
    passed &= run_step(
        "unit tests",
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
    )
    passed &= run_step(
        "Ruff",
        build_uvx_command("ruff", RUFF_VERSION, ["check", "."], offline=args.offline),
    )
    passed &= run_step(
        "ty",
        build_uvx_command(
            "ty",
            TY_VERSION,
            [
                "check",
                "--python-version",
                PYTHON_VERSION,
                "scripts",
                "tests",
                "plugins",
            ],
            offline=args.offline,
            with_packages=(f"PyYAML=={PYYAML_VERSION}",),
        ),
    )
    passed &= run_step("git diff check", ["git", "diff", "--check"])

    after = worktree_status()
    if after != before:
        print(
            "FAILED: validation changed the worktree. Review generated files before continuing.",
            file=sys.stderr,
        )
        passed = False

    if passed:
        print("\nQuality validation passed.")
        return 0
    print("\nQuality validation failed.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
