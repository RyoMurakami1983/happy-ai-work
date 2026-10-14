#!/usr/bin/env python3
"""Prepare one allowlisted development input; this is NOT an isolated model runner."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SUITE = Path("evals/openai-first-implement")


def _portable_path(name: str) -> None:
    reserved = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)),
                *(f"lpt{i}" for i in range(1, 10))}
    parts = name.split("/")
    if not name or any(char in name for char in "\\:*?\"<>|"):
        raise ValueError("unsafe portable path")
    if any(not part or part in {".", ".."} or part.endswith((".", " "))
           or part.split(".")[0].casefold() in reserved for part in parts):
        raise ValueError("unsafe portable path")


def _safe_file(root: Path, name: str) -> Path:
    _portable_path(name)
    path = root / name
    if any(part.is_symlink() for part in [path, *path.parents] if part != root.parent):
        raise ValueError("symlink sources are forbidden")
    if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("source is absent or outside repository")
    return path


def prepare_bundle(root: Path, condition: str, case_id: str, destination: Path) -> dict[str, Any]:
    """Copy only frozen actor inputs; keep grading/other conditions outside the bundle."""
    if condition not in {"baseline", "candidate"}:
        raise ValueError("unknown condition")
    root = root.resolve()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    if destination.resolve().is_relative_to(root):
        raise ValueError("actor input destination must be outside this repository")
    manifest = json.loads((root / SUITE / "preparation.v1.json").read_text(encoding="utf-8"))
    if case_id not in manifest["tasks"]:
        raise ValueError("unknown development case")
    task = manifest["tasks"][case_id]
    entries = list(manifest["conditions"][condition].items()) + list(task["files"].items())
    canonical: set[str] = {"source.json"}
    for output, _ in entries:
        _portable_path(output)
        key = output.casefold()
        if any(key == old or key.startswith(old + "/") or old.startswith(key + "/") for old in canonical):
            raise ValueError("colliding or reserved output path")
        canonical.add(key)
    ready: dict[str, bytes] = {}
    for output, spec in entries:
        source = spec["source"]
        allowed_prefixes = (
            f"{SUITE.as_posix()}/{condition}/implement/",
            f"{SUITE.as_posix()}/{condition}/implementation-plan/",
            f"{SUITE.as_posix()}/fixtures/{task['family']}/",
        )
        if source != f"{SUITE.as_posix()}/tasks/{case_id}.md" and not source.startswith(allowed_prefixes):
            raise ValueError("source is not an actor input")
        content = _safe_file(root, source).read_bytes()
        if hashlib.sha256(content).hexdigest() != spec["sha256"]:
            raise ValueError("frozen source hash mismatch")
        ready[output] = content
    provenance = {
        "schema_version": 1,
        "kind": "public-development-input-only",
        "case_id": case_id,
        "condition": condition,
        "baseline_revision": manifest["baseline_revision"],
        "isolation_verified": False,
        "trial_authorized": False,
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in ready.items()},
    }
    destination.mkdir()  # exclusive creation; never overwrite a previous preparation
    try:
        for name, data in ready.items():
            output = destination / name
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(data)
        (destination / "SOURCE.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    except Exception:
        shutil.rmtree(destination)  # only the directory exclusively created above
        raise
    return provenance


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("condition", choices=["baseline", "candidate"])
    parser.add_argument("case_id")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        result = prepare_bundle(ROOT, args.condition, args.case_id, args.destination)
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(2, f"Preparation failed: {exc}\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
