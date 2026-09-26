#!/usr/bin/env python3
"""Validate public evaluation cases, sanitized records, and tracking policy."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
EVALS = ROOT / "evals"
CASE_GLOB = "*/cases.v*.json"
RECORDS = EVALS / "records"
SECRET_RE = re.compile(
    r"(?:gh" + r"p_|github_" + r"pat_|s" + r"k-[A-Za-z0-9_-]{20,}|AK" + r"IA[0-9A-Z]{16})"
)
FORBIDDEN_PATH_MARKERS = {"runs", "sealed", "holdout", "raw", "transcript", "viewer"}
FORBIDDEN_NAME_FRAGMENTS = {"sealed", "holdout", "raw", "transcript", "viewer"}
FORBIDDEN_FIELDS = {
    "raw_response",
    "raw_run",
    "raw_transcript",
    "transcript",
    "tool_output",
    "secret",
    "pii",
    "private_code",
    "sealed_prompt",
}
CASE_TYPES = {"happy-path", "near-miss", "failure-missing-context"}


def load_json(path: Path, failures: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return None


def display_path(path: Path) -> Path:
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def walk_fields(value: Any, *, path: Path, failures: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_FIELDS:
                failures.append(f"{display_path(path)}: forbidden field {key}")
            walk_fields(child, path=path, failures=failures)
    elif isinstance(value, list):
        for child in value:
            walk_fields(child, path=path, failures=failures)


def validate_tracking_policy(failures: list[str], *, evals_dir: Path = EVALS) -> None:
    for path in evals_dir.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(evals_dir)
        lowered_parts = {part.lower() for part in relative.parts}
        path_tokens = {
            token
            for part in relative.parts
            for token in re.split(r"[^a-z0-9]+", part.lower())
            if token
        }
        lowered_name = path.name.lower()
        forbidden_path = bool((lowered_parts | path_tokens) & FORBIDDEN_PATH_MARKERS)
        forbidden_name = any(fragment in lowered_name for fragment in FORBIDDEN_NAME_FRAGMENTS)
        if forbidden_path or forbidden_name:
            failures.append(f"{relative}: forbidden evaluation artifact path or filename")
        if path.suffix.lower() in {".json", ".jsonl", ".md"}:
            text = path.read_text(encoding="utf-8")
            if SECRET_RE.search(text):
                failures.append(f"{relative}: possible secret")
        if path.suffix.lower() == ".json":
            payload = load_json(path, failures)
            if payload is not None:
                walk_fields(payload, path=path, failures=failures)
        elif path.suffix.lower() == ".jsonl":
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as exc:
                    failures.append(f"{relative}:{line_number}: invalid JSON line: {exc}")
                    continue
                walk_fields(payload, path=path, failures=failures)


def matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def validate_against_schema(
    value: Any, schema: dict[str, Any], *, location: str, failures: list[str]
) -> None:
    expected_type = schema.get("type")
    if expected_type and not matches_type(value, expected_type):
        failures.append(f"{location}: expected {expected_type}")
        return
    if "const" in schema and value != schema["const"]:
        failures.append(f"{location}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        failures.append(f"{location}: value is not in enum")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            failures.append(f"{location}: string is too short")
        pattern = schema.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            failures.append(f"{location}: string does not match pattern")
    if isinstance(value, dict):
        required = set(schema.get("required", []))
        for key in sorted(required - value.keys()):
            failures.append(f"{location}: missing required property {key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in sorted(value.keys() - properties.keys()):
                failures.append(f"{location}: unexpected property {key}")
        elif isinstance(schema.get("additionalProperties"), dict):
            additional_schema = schema["additionalProperties"]
            for key in sorted(value.keys() - properties.keys()):
                validate_against_schema(
                    value[key], additional_schema, location=f"{location}.{key}", failures=failures
                )
        if len(value) < schema.get("minProperties", 0):
            failures.append(f"{location}: too few properties")
        for key, child_schema in properties.items():
            if key in value:
                validate_against_schema(
                    value[key], child_schema, location=f"{location}.{key}", failures=failures
                )
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            failures.append(f"{location}: too few items")
        if schema.get("uniqueItems"):
            serialized = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value]
            if len(serialized) != len(set(serialized)):
                failures.append(f"{location}: items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, child in enumerate(value):
                validate_against_schema(
                    child, item_schema, location=f"{location}[{index}]", failures=failures
                )


def validate_case_suite(path: Path, failures: list[str], schema: dict[str, Any]) -> None:
    payload = load_json(path, failures)
    if not isinstance(payload, dict):
        return
    validate_against_schema(payload, schema, location=str(display_path(path)), failures=failures)
    expected = {
        "schema_version": 1,
        "visibility": "public",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            failures.append(f"{path.relative_to(ROOT)}: {key} must be {value!r}")
    if payload.get("case_kind") not in {"upstream-eval", "common-safety-eval"}:
        failures.append(f"{path.relative_to(ROOT)}: invalid case_kind")
    target = payload.get("target")
    if not isinstance(target, str) or path.parent.name != target:
        failures.append(f"{path.relative_to(ROOT)}: target must match parent directory")
    for key in ("suite_version", "constitution_version", "evaluation_criteria_version"):
        if not isinstance(payload.get(key), str) or not payload[key]:
            failures.append(f"{path.relative_to(ROOT)}: {key} is required")
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) < 3:
        failures.append(f"{path.relative_to(ROOT)}: at least three cases are required")
        return
    ids: set[str] = set()
    found_types: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            failures.append(f"{path.relative_to(ROOT)}: every case must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            failures.append(f"{path.relative_to(ROOT)}: case id is required")
        elif case_id in ids:
            failures.append(f"{path.relative_to(ROOT)}: duplicate case id {case_id}")
        else:
            ids.add(case_id)
        case_type = case.get("type")
        if case_type in CASE_TYPES:
            found_types.add(case_type)
        else:
            failures.append(f"{path.relative_to(ROOT)}: invalid case type {case_type!r}")
        if case.get("holdout") is not False:
            failures.append(f"{path.relative_to(ROOT)}: public case {case_id} must set holdout false")
        status = case.get("status", "active")
        if status == "retired":
            for key in ("replaced_by", "retirement_reason"):
                if not case.get(key):
                    failures.append(f"{path.relative_to(ROOT)}: retired case {case_id} requires {key}")
        elif "replaced_by" in case or "retirement_reason" in case:
            failures.append(
                f"{path.relative_to(ROOT)}: active case {case_id} cannot define retirement metadata"
            )
        for key in ("prompt", "critical", "normal", "prohibited"):
            value = case.get(key)
            if key == "prompt" and (not isinstance(value, str) or not value.strip()):
                failures.append(f"{path.relative_to(ROOT)}: {case_id} prompt is required")
            if key != "prompt" and (not isinstance(value, list) or not value):
                failures.append(f"{path.relative_to(ROOT)}: {case_id} {key} must be non-empty")
    if found_types != CASE_TYPES:
        failures.append(f"{path.relative_to(ROOT)}: happy, near-miss, and missing-context are required")
    walk_fields(payload, path=path, failures=failures)


def validate_record(path: Path, failures: list[str], schema: dict[str, Any]) -> None:
    payload = load_json(path, failures)
    if not isinstance(payload, dict):
        return
    validate_against_schema(payload, schema, location=str(display_path(path)), failures=failures)
    required = {
        "schema_version",
        "record_id",
        "target_revision",
        "constitution_version",
        "criteria_version",
        "decision_profile_version",
        "case_schema_version",
        "record_schema_version",
        "mode",
        "verdict",
        "evaluated_at",
        "roles",
        "conditions",
        "case_results",
        "holdout",
        "previous_record",
        "artifact_hashes",
        "retention_decision",
    }
    missing = sorted(required - payload.keys())
    if missing:
        failures.append(f"{path.relative_to(ROOT)}: missing fields {missing}")
    if payload.get("schema_version") != 1:
        failures.append(f"{path.relative_to(ROOT)}: schema_version must be 1")
    if payload.get("mode") not in {"A", "B", "C"}:
        failures.append(f"{path.relative_to(ROOT)}: mode must be A, B, or C")
    if payload.get("verdict") not in {"adopted", "continued", "rejected"}:
        failures.append(f"{path.relative_to(ROOT)}: invalid verdict")
    if payload.get("record_id") != path.stem:
        failures.append(f"{path.relative_to(ROOT)}: record_id must match filename")
    holdout = payload.get("holdout")
    roles = payload.get("roles")
    independence = roles.get("independence") if isinstance(roles, dict) else None
    prior = payload.get("previous_record")
    retention = payload.get("retention_decision")
    public_status = retention.get("public_artifact") if isinstance(retention, dict) else None
    artifact_hashes = payload.get("artifact_hashes")
    if payload.get("verdict") == "adopted":
        if isinstance(holdout, dict) and holdout.get("status") in {"contaminated", "missing"}:
            failures.append(f"{path.relative_to(ROOT)}: adopted record cannot use missing/contaminated holdout")
        if isinstance(independence, dict) and independence.get("status") != "valid":
            failures.append(f"{path.relative_to(ROOT)}: adopted record requires valid independence")
        if payload.get("mode") == "C":
            failures.append(f"{path.relative_to(ROOT)}: emergency mode C cannot be adopted")
    if isinstance(prior, dict) and prior.get("status") == "preserved" and not prior.get("record_id"):
        failures.append(f"{path.relative_to(ROOT)}: preserved prior record requires record_id")
    if public_status != "sanitized-only":
        failures.append(f"{path.relative_to(ROOT)}: public artifact must be sanitized-only")
    if isinstance(artifact_hashes, dict):
        root = ROOT.resolve()
        for artifact_path, expected_hash in artifact_hashes.items():
            relative = Path(artifact_path)
            candidate = (ROOT / relative).resolve()
            if relative.is_absolute() or root not in candidate.parents:
                failures.append(f"{path.relative_to(ROOT)}: artifact path escapes repository: {artifact_path}")
                continue
            if not candidate.is_file():
                failures.append(f"{path.relative_to(ROOT)}: hashed artifact is missing: {artifact_path}")
                continue
            actual_hash = hashlib.sha256(candidate.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                failures.append(f"{path.relative_to(ROOT)}: artifact hash mismatch: {artifact_path}")
    walk_fields(payload, path=path, failures=failures)


def immutable_eval_path(changed_path: str) -> bool:
    normalized = changed_path.replace("\\", "/")
    return (
        normalized.startswith("evals/records/")
        or normalized.startswith("evals/schema/")
        or re.fullmatch(r"evals/[^/]+/cases\.v[0-9]+\.json", normalized) is not None
    )


def inspect_append_only_status(output: str, failures: list[str], *, source: str) -> None:
    for line in output.splitlines():
        fields = line.split("\t")
        if len(fields) >= 2 and fields[0] and fields[0][0] in {"A", "M", "D", "R", "T"}:
            status = fields[0]
            paths = fields[1:]
        else:
            status = line[:2]
            paths = [line[3:]] if len(line) > 3 else []
        if not any(marker in status for marker in ("M", "D", "R", "T")):
            continue
        for changed_path in paths:
            normalized = changed_path.replace("\\", "/")
            if immutable_eval_path(changed_path):
                failures.append(
                    "versioned eval assets are immutable; "
                    f"existing file changed in {source}: {normalized}"
                )


def validate_append_only(failures: list[str]) -> None:
    worktree = subprocess.run(
        ["git", "status", "--porcelain=v1", "--", "evals"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if worktree.returncode != 0:
        failures.append("could not inspect append-only record status")
        return
    inspect_append_only_status(worktree.stdout, failures, source="worktree")

    if os.environ.get("GITHUB_ACTIONS") != "true":
        return
    base_ref = os.environ.get("GITHUB_BASE_REF")
    comparison = f"origin/{base_ref}...HEAD" if base_ref else github_push_comparison(failures)
    if comparison is None:
        return
    committed = subprocess.run(
        ["git", "diff", "--name-status", "--find-renames", comparison, "--", "evals"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if committed.returncode != 0:
        failures.append(f"could not compare append-only assets against {comparison}")
        return
    inspect_append_only_status(committed.stdout, failures, source=comparison)


def github_push_comparison(failures: list[str]) -> str | None:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        failures.append("GITHUB_EVENT_PATH is required for append-only validation on push")
        return None
    try:
        payload = json.loads(Path(event_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"could not read GitHub push event: {exc}")
        return None
    before = payload.get("before") if isinstance(payload, dict) else None
    if not isinstance(before, str) or not re.fullmatch(r"[0-9a-f]{40}", before):
        failures.append("GitHub push event requires a valid before SHA")
        return None
    if before == "0" * 40:
        failures.append("GitHub push event has no comparable before SHA")
        return None
    return f"{before}...HEAD"


def main() -> int:
    failures: list[str] = []
    schemas: dict[str, dict[str, Any]] = {}
    for schema_name in ("case.schema.json", "record.schema.json"):
        schema_path = EVALS / "schema" / schema_name
        if not schema_path.is_file():
            failures.append(f"evals/schema/{schema_name}: required schema is missing")
            continue
        payload = load_json(schema_path, failures)
        if isinstance(payload, dict):
            schemas[schema_name] = payload
    suites = sorted(EVALS.glob(CASE_GLOB))
    if not suites:
        failures.append("no public evaluation case suites found")
    for path in suites:
        if "case.schema.json" in schemas:
            validate_case_suite(path, failures, schemas["case.schema.json"])
    if RECORDS.exists():
        for path in sorted(RECORDS.glob("*.json")):
            if "record.schema.json" in schemas:
                validate_record(path, failures, schemas["record.schema.json"])
    validate_tracking_policy(failures)
    validate_append_only(failures)
    if failures:
        print("evaluation validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("evaluation validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
