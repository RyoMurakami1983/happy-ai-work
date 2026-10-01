"""Require a numeric release-version increase for changed plugin distributions."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Existing build metadata is accepted, but changing metadata alone is not a release.
VERSION = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, check=False)
    if result.returncode:
        raise ValueError("Git comparison failed; ensure both commits and their common history were fetched.")
    return result.stdout.decode("utf-8", errors="surrogateescape")


def files_at(root: Path, commit: str, prefix: str) -> set[str]:
    return set(git(root, "ls-tree", "-r", "--name-only", "-z", commit, "--", prefix).split("\0")) - {""}


def version_at(root: Path, commit: str, manifest: str, plugin: str) -> tuple[int, int, int]:
    try:
        data = json.loads(git(root, "show", f"{commit}:{manifest}"))
        value = data.get("version") if isinstance(data, dict) else None
        match = VERSION.fullmatch(value) if isinstance(value, str) else None
        if not match or data.get("name") != plugin:
            raise ValueError
        return int(match[1]), int(match[2]), int(match[3])
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"{manifest}: require matching name and numeric MAJOR.MINOR.PATCH (optional +metadata)."
        ) from exc


def check_versions(root: Path, base: str, head: str) -> list[str]:
    base = git(root, "rev-parse", "--verify", "--end-of-options", f"{base}^{{commit}}").strip()
    head = git(root, "rev-parse", "--verify", "--end-of-options", f"{head}^{{commit}}").strip()
    ancestor = git(root, "merge-base", base, head).strip()
    changed = git(root, "diff", "--no-renames", "--name-only", "-z", ancestor, head, "--", "plugins/")
    plugins = set()
    errors = []
    for path in filter(None, changed.split("\0")):
        parts = path.split("/")
        if len(parts) < 3:
            errors.append(f"{path!r}: distribution files must belong to plugins/<name>/.")
        else:
            plugins.add(parts[1])
    for plugin in sorted(plugins):
        prefix = f"plugins/{plugin}/"
        manifest = f"{prefix}.codex-plugin/plugin.json"
        head_files = files_at(root, head, prefix)
        if not head_files:
            # Full retirement has no surviving release to bump; repo validation checks catalog consistency.
            continue
        if manifest not in head_files:
            errors.append(f"{plugin}: surviving distribution requires {manifest}; do not remove only its manifest.")
            continue
        try:
            current = version_at(root, head, manifest, plugin)
            base_files = files_at(root, base, prefix)
            if base_files:
                if manifest not in base_files:
                    raise ValueError(
                        f"{plugin}: base manifest missing; resolve release history before comparing versions."
                    )
                previous = version_at(root, base, manifest, plugin)
                if current <= previous:
                    errors.append(
                        f"{plugin}: distribution changed but version {'.'.join(map(str, current))} is not greater than "
                        f"PR base {'.'.join(map(str, previous))}; increase {manifest} in this PR."
                    )
        except ValueError as exc:
            errors.append(str(exc))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="PR base commit (fetch full history)")
    parser.add_argument("--head", required=True, help="PR head commit, not GitHub's synthetic merge commit")
    args = parser.parse_args()
    try:
        errors = check_versions(ROOT, args.base, args.head)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    for error in errors:
        print(f"FAIL: {error}", file=sys.stderr)
    if errors:
        return 1
    print("Plugin release-version gate passed (installed content and session load are not checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
