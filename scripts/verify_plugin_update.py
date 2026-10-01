"""Read-only comparison of selected public distribution files (not a load test)."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SAMPLES = {
    "happy-core": (
        ".codex-plugin/plugin.json",
        "skills/home-bootstrap/SKILL.md",
        "skills/home-bootstrap/assets/AGENTS.md",
    ),
    "happy-coding": (
        ".codex-plugin/plugin.json",
        "skills/implement/SKILL.md",
        "skills/implement/references/verification-communication.md",
        "skills/debug-and-fix/SKILL.md",
        "skills/dotnet/SKILL.md",
    ),
    "happy-preview": (
        ".codex-plugin/plugin.json",
        "skills/pr-delivery/SKILL.md",
        "skills/pr-delivery/agents/openai.yaml",
    ),
}


def fingerprint(root: Path, relative: str) -> dict[str, str]:
    """Do not traverse symlinks outside the explicitly selected plugin root."""
    try:
        path = root / relative
        if not path.resolve().is_relative_to(root.resolve()):
            return {"state": "outside_root"}
        content = path.read_bytes()
    except FileNotFoundError:
        return {"state": "missing"}
    except (OSError, RuntimeError):
        return {"state": "unreadable"}
    return {"state": "present", "sha256": hashlib.sha256(content).hexdigest()}


def compare(plugin: str, source: Path, installed: Path | None) -> dict[str, object]:
    files = []
    matched = installed is not None
    for relative in SAMPLES[plugin]:
        expected = fingerprint(source, relative)
        actual = fingerprint(installed, relative) if installed is not None else {"state": "not_checked"}
        matches = expected["state"] == "present" and expected == actual
        matched &= matches
        files.append({"file": relative, "source": expected, "installed": actual, "matches": matches})
    status = "samples_match" if matched else "mismatch"
    if installed is None:
        status = "not_checked"
    return {"plugin": plugin, "status": status, "files": files, "session_load": "not_checked"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin", choices=SAMPLES, required=True)
    parser.add_argument("--source", type=Path, required=True, help="Plugin root in the verified source checkout")
    parser.add_argument("--installed", type=Path, help="Actual installedPath confirmed by Codex; never guess it")
    args = parser.parse_args()
    report = compare(args.plugin, args.source, args.installed)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "samples_match" else 1


if __name__ == "__main__":
    raise SystemExit(main())
