#!/usr/bin/env python3
"""Validate consistency between sanitized records and their frozen TARGET manifests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def load_object(path: Path, failures: list[str], *, label: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"{label}: invalid JSON: {exc}")
        return None
    if not isinstance(payload, dict):
        failures.append(f"{label}: expected object")
        return None
    return payload


def validate_records(root: Path) -> list[str]:
    failures: list[str] = []
    resolved_root = root.resolve()
    records = root / "evals" / "records"
    for record_path in sorted(records.glob("*.json")):
        label = record_path.relative_to(root).as_posix()
        record = load_object(record_path, failures, label=label)
        if record is None:
            continue
        conditions = record.get("conditions")
        evaluation_context = (
            conditions.get("evaluation_context") if isinstance(conditions, dict) else None
        )
        manifest_name = (
            evaluation_context.get("artifact_manifest")
            if isinstance(evaluation_context, dict)
            else None
        )
        if not isinstance(manifest_name, str):
            continue
        manifest_path = (root / manifest_name).resolve()
        if resolved_root not in manifest_path.parents or not manifest_path.is_file():
            failures.append(f"{label}: artifact manifest is missing or escapes repository")
            continue
        manifest = load_object(manifest_path, failures, label=manifest_name)
        if manifest is None:
            continue
        record_hashes = record.get("artifact_hashes")
        if not isinstance(record_hashes, dict):
            continue
        actual_manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        if record_hashes.get(manifest_name) != actual_manifest_hash:
            failures.append(f"{label}: artifact manifest hash is missing or stale: {manifest_name}")
        frozen_hashes: dict[str, Any] = {}
        manifest_hashes = manifest.get("artifact_hashes")
        if isinstance(manifest_hashes, dict):
            frozen_hashes.update(manifest_hashes)
        manifest_conditions = manifest.get("conditions")
        current = (
            manifest_conditions.get("current")
            if isinstance(manifest_conditions, dict)
            else None
        )
        current_artifacts = current.get("artifacts") if isinstance(current, dict) else None
        if isinstance(current_artifacts, dict):
            for artifact_name, current_hash in current_artifacts.items():
                frozen_hash = frozen_hashes.get(artifact_name)
                if frozen_hash is not None and frozen_hash != current_hash:
                    failures.append(
                        f"{manifest_name}: conflicting frozen hashes: {artifact_name}"
                    )
                    continue
                frozen_hashes[artifact_name] = current_hash
        for artifact_name, record_hash in record_hashes.items():
            frozen_hash = frozen_hashes.get(artifact_name)
            if frozen_hash is not None and frozen_hash != record_hash:
                failures.append(
                    f"{label}: record hash differs from artifact manifest: {artifact_name}"
                )
    return failures
