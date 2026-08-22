#!/usr/bin/env python3
"""Validate Constitution metadata and optionally check profile governance drift."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
CONSTITUTION_PATH = ROOT / "CONSTITUTION.md"
CONSTITUTION_GIT_PATH = "CONSTITUTION.md"
SYNC_PATH = ROOT / "docs" / "governance" / "constitution-sync.json"
VERSION_RE = re.compile(r"^Version: ([0-9]+\.[0-9]+\.[0-9]+)\s*$", re.MULTILINE)
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class ProfileRevision:
    sha: str
    committed_at: datetime


@dataclass(frozen=True)
class ProfileHistory:
    latest: ProfileRevision
    oldest_unreconciled: ProfileRevision | None


@dataclass(frozen=True)
class ConstitutionRevision:
    commit_sha: str
    sha256: str
    committed_at: datetime


@dataclass(frozen=True)
class DriftResult:
    stage: str
    exit_code: int
    message: str
    started_at: datetime | None = None
    source: str | None = None
    remediation: str | None = None


def parse_datetime(value: str) -> datetime:
    if not isinstance(value, str):
        raise TypeError("datetime must be a string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("datetime must include a timezone")
    return parsed.astimezone(UTC)


def classify_drift(age: timedelta) -> DriftResult:
    if age < timedelta(days=3):
        return DriftResult("healthy", 0, "governance drift is within the 3-day grace period")
    if age < timedelta(days=7):
        return DriftResult("warning", 0, "governance drift is at least 3 days old")
    if age < timedelta(days=10):
        return DriftResult("restricted", 1, "behavior-changing skill/plugin release and merge are restricted")
    return DriftResult(
        "hard-stop",
        1,
        "only investigation, synchronization, remediation, rollback, and safety work may continue",
    )


def evaluate_remote_drift(
    sync: dict[str, Any], remote: ProfileHistory, now: datetime
) -> DriftResult:
    checked_at = now.astimezone(UTC)
    revisions = [remote.latest]
    if remote.oldest_unreconciled:
        revisions.append(remote.oldest_unreconciled)
    if any(revision.committed_at.astimezone(UTC) > checked_at for revision in revisions):
        raise ValueError("remote profile commit time must not be in the future")
    recorded = sync.get("personal_philosophy", {}).get("revision")
    recorded_start = sync.get("drift_started_at")
    if sync.get("resolution") == "pending":
        started_at = parse_datetime(recorded_start)
        if remote.oldest_unreconciled:
            started_at = min(started_at, remote.oldest_unreconciled.committed_at)
        source = sync.get("drift_source")
        if remote.oldest_unreconciled and source == "constitution":
            source = "both"
        result = classify_drift(checked_at - started_at)
        return DriftResult(
            result.stage,
            result.exit_code,
            result.message,
            started_at,
            source,
            "compare both sources, record reflected/not-applicable, then clear drift fields",
        )

    if recorded == remote.latest.sha:
        return DriftResult("healthy", 0, "personal philosophy revision is reconciled")

    if not remote.oldest_unreconciled:
        raise ValueError("remote history does not contain an unreconciled profile revision")
    started_at = remote.oldest_unreconciled.committed_at
    age = checked_at - started_at.astimezone(UTC)
    result = classify_drift(age)
    return DriftResult(
        result.stage,
        result.exit_code,
        result.message,
        started_at,
        "personal-philosophy",
        "compare the new profile revision with the current Constitution and update the sync record",
    )


def run_remote_check(
    sync: dict[str, Any], *, now: datetime, fetch: Callable[[], ProfileHistory]
) -> DriftResult:
    try:
        remote = fetch()
        return evaluate_remote_drift(sync, remote, now)
    except Exception as exc:  # noqa: BLE001 - system-boundary failures become mode B
        return DriftResult(
            "undetermined-b",
            1,
            f"remote governance drift is undetermined (evaluation mode B): {exc}",
            source="unknown",
            remediation="retry the read-only check and inspect the sync record; do not release while undetermined",
        )


def profile_api_url(profile_url: str) -> str:
    parsed = urlparse(profile_url)
    parts = [part for part in parsed.path.split("/") if part]
    if parsed.netloc != "github.com" or len(parts) < 5 or parts[2] != "blob":
        raise ValueError("personal philosophy URL must be a GitHub blob URL")
    owner, repository = parts[0], parts[1]
    file_path = "/".join(parts[4:])
    return f"https://api.github.com/repos/{owner}/{repository}/commits?path={file_path}&per_page=100"


def profile_history_from_commits(
    commits: list[ProfileRevision], recorded_revision: str
) -> ProfileHistory:
    if not commits:
        raise ValueError("profile README commit history is empty")
    if commits[0].sha == recorded_revision:
        return ProfileHistory(commits[0], None)
    for index, commit in enumerate(commits):
        if commit.sha == recorded_revision:
            return ProfileHistory(commits[0], commits[index - 1])
    raise ValueError("recorded profile revision was not found in README history")


def fetch_profile_history(sync: dict[str, Any]) -> ProfileHistory:
    base_url = profile_api_url(sync["personal_philosophy"]["url"])
    recorded_revision = sync["personal_philosophy"]["revision"]
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "happy-ai-work-constitution-validator",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    commits: list[ProfileRevision] = []
    for page in range(1, 11):
        request = urllib.request.Request(f"{base_url}&page={page}", headers=headers)
        with urllib.request.urlopen(request, timeout=15) as response:  # noqa: S310 - GitHub host validated above
            payload = json.load(response)
        commits.extend(
            ProfileRevision(
                sha=item["sha"],
                committed_at=parse_datetime(item["commit"]["committer"]["date"]),
            )
            for item in payload
        )
        if any(commit.sha == recorded_revision for commit in commits) or len(payload) < 100:
            return profile_history_from_commits(commits, recorded_revision)
    raise ValueError("recorded profile revision was not found within 1000 README commits")


def constitution_sha256() -> str:
    return hashlib.sha256(CONSTITUTION_PATH.read_bytes()).hexdigest()


def load_sync() -> dict[str, Any]:
    payload = json.loads(SYNC_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("sync record root must be a JSON object")
    return payload


def constitution_commit_time() -> datetime | None:
    """Return the latest committed Constitution timestamp, or None before its first commit."""
    completed = subprocess.run(
        ["git", "log", "-1", "--format=%cI", "--", CONSTITUTION_GIT_PATH],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = completed.stdout.strip()
    return parse_datetime(value) if completed.returncode == 0 and value else None


def constitution_history_from_revisions(
    revisions: list[ConstitutionRevision], recorded_revision: str
) -> datetime | None:
    """Find the oldest Constitution commit after the exact reconciled commit."""
    if not revisions or revisions[0].commit_sha == recorded_revision:
        return None
    for index, revision in enumerate(revisions):
        if revision.commit_sha == recorded_revision:
            return revisions[index - 1].committed_at
    raise ValueError("reconciled Constitution commit was not found in Git history")


def constitution_unreconciled_start(recorded_revision: str) -> datetime | None:
    completed = subprocess.run(
        ["git", "log", "--format=%H%x09%cI", "--", CONSTITUTION_GIT_PATH],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise OSError(completed.stderr.strip() or "could not read Constitution Git history")
    revisions: list[ConstitutionRevision] = []
    for line in completed.stdout.splitlines():
        commit_sha, committed_at = line.split("\t", 1)
        shown = subprocess.run(
            ["git", "show", f"{commit_sha}:CONSTITUTION.md"],
            cwd=ROOT,
            check=False,
            capture_output=True,
        )
        if shown.returncode != 0:
            raise OSError("could not read Constitution content from Git history")
        revisions.append(
            ConstitutionRevision(
                commit_sha,
                hashlib.sha256(shown.stdout).hexdigest(),
                parse_datetime(committed_at),
            )
        )
    return constitution_history_from_revisions(revisions, recorded_revision)


def evaluate_local_drift(
    sync: dict[str, Any], *, now: datetime, unreconciled_start: datetime | None
) -> DriftResult:
    started_at = parse_datetime(sync["drift_started_at"])
    if sync.get("drift_source") in {"constitution", "both"} and unreconciled_start:
        if unreconciled_start.astimezone(UTC) > now.astimezone(UTC):
            raise ValueError("Constitution commit time must not be in the future")
        started_at = min(started_at, unreconciled_start.astimezone(UTC))
    result = classify_drift(now.astimezone(UTC) - started_at)
    return DriftResult(
        result.stage,
        result.exit_code,
        result.message,
        started_at,
        sync.get("drift_source"),
        "compare both sources, record reflected/not-applicable, then clear drift fields",
    )


def run_local_drift_check(sync: dict[str, Any], *, now: datetime) -> DriftResult:
    try:
        history_start = None
        if sync.get("drift_source") in {"constitution", "both"}:
            history_start = constitution_unreconciled_start(sync["constitution_revision"])
        return evaluate_local_drift(sync, now=now, unreconciled_start=history_start)
    except Exception as exc:  # noqa: BLE001 - local system boundary becomes mode B
        return DriftResult(
            "undetermined-b",
            1,
            f"local governance drift is undetermined (evaluation mode B): {exc}",
            source=sync.get("drift_source", "unknown"),
            remediation="inspect Constitution Git history and the sync record; do not release while undetermined",
        )


def stricter_result(first: DriftResult, second: DriftResult, *, now: datetime) -> DriftResult:
    if first.stage == "undetermined-b":
        return first
    if second.stage == "undetermined-b":
        return second
    starts = [value for value in (first.started_at, second.started_at) if value is not None]
    if not starts:
        return first if first.exit_code >= second.exit_code else second
    started_at = min(starts)
    classified = classify_drift(now.astimezone(UTC) - started_at.astimezone(UTC))
    sources = {value for value in (first.source, second.source) if value}
    source = "both" if len(sources) > 1 else next(iter(sources), None)
    return DriftResult(
        classified.stage,
        classified.exit_code,
        classified.message,
        started_at,
        source,
        first.remediation or second.remediation,
    )


def validate_local(sync: dict[str, Any], *, now: datetime | None = None) -> list[str]:
    failures: list[str] = []
    checked_at = (now or datetime.now(UTC)).astimezone(UTC)
    if not isinstance(sync, dict):
        return ["sync record root must be a JSON object"]
    if sync.get("schema_version") != 1:
        failures.append("schema_version must be 1")

    constitution = CONSTITUTION_PATH.read_text(encoding="utf-8")
    match = VERSION_RE.search(constitution)
    if not match:
        failures.append("CONSTITUTION.md must declare a semantic Version")
    elif sync.get("constitution_version") != match.group(1):
        failures.append("sync constitution_version does not match CONSTITUTION.md")

    recorded_hash = sync.get("constitution_sha256", "")
    if not isinstance(recorded_hash, str) or not SHA256_RE.fullmatch(recorded_hash):
        failures.append("constitution_sha256 must be a lowercase SHA-256")
    elif recorded_hash != constitution_sha256() and not (
        sync.get("resolution") == "pending"
        and sync.get("drift_source") in {"constitution", "both"}
    ):
        failures.append("CONSTITUTION.md changed without a reconciled sync record")

    constitution_revision = sync.get("constitution_revision")
    if not isinstance(constitution_revision, str) or not SHA_RE.fullmatch(constitution_revision):
        failures.append("constitution_revision must be a lowercase Git SHA")

    philosophy = sync.get("personal_philosophy", {})
    if not isinstance(philosophy, dict):
        failures.append("personal_philosophy must be a JSON object")
        philosophy = {}
    revision = philosophy.get("revision", "")
    if not isinstance(revision, str) or not SHA_RE.fullmatch(revision):
        failures.append("personal_philosophy.revision must be a lowercase Git SHA")
    committed_at: datetime | None = None
    reconciled_at: datetime | None = None
    try:
        committed_at = parse_datetime(philosophy.get("committed_at", ""))
        reconciled_at = parse_datetime(sync.get("reconciled_at", ""))
    except (TypeError, ValueError) as exc:
        failures.append(f"sync timestamps must be timezone-aware ISO-8601: {exc}")

    resolution = sync.get("resolution")
    if resolution not in {"reflected", "not-applicable", "pending"}:
        failures.append("resolution must be reflected, not-applicable, or pending")
    drift_started_at = sync.get("drift_started_at")
    drift_source = sync.get("drift_source")
    if resolution == "pending":
        if drift_source not in {"personal-philosophy", "constitution", "both"}:
            failures.append("pending resolution requires a valid drift_source")
        try:
            started_at = parse_datetime(drift_started_at)
            if started_at > checked_at:
                failures.append("drift_started_at must not be in the future")
            if reconciled_at and started_at < reconciled_at:
                failures.append("drift_started_at must not precede reconciled_at")
        except (TypeError, ValueError) as exc:
            failures.append(f"pending resolution requires a valid drift_started_at: {exc}")
    elif drift_started_at is not None or drift_source is not None:
        failures.append("resolved sync state must clear drift_started_at and drift_source")

    if committed_at and committed_at > checked_at:
        failures.append("personal philosophy committed_at must not be in the future")
    if reconciled_at and reconciled_at > checked_at:
        failures.append("reconciled_at must not be in the future")
    reason = sync.get("reason", "")
    if not isinstance(reason, str) or not reason.strip():
        failures.append("sync reason is required")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-remote", action="store_true")
    args = parser.parse_args(argv)

    try:
        sync = load_sync()
        failures = validate_local(sync)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"constitution validation failed: {exc}")
        return 1

    if failures:
        print("constitution validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    if args.check_remote:
        now = datetime.now(UTC)
        result = run_remote_check(
            sync,
            now=now,
            fetch=lambda: fetch_profile_history(sync),
        )
        if sync.get("resolution") == "pending":
            result = stricter_result(result, run_local_drift_check(sync, now=now), now=now)
        prefix = "warning" if result.stage == "warning" else result.stage
        print(f"constitution remote check: {prefix}: {result.message}")
        if result.started_at:
            print(f"drift started at: {result.started_at.isoformat()}")
        if result.source:
            print(f"drift source: {result.source}")
        if result.remediation:
            print(f"remediation: {result.remediation}")
        return result.exit_code

    if sync.get("resolution") == "pending":
        result = run_local_drift_check(sync, now=datetime.now(UTC))
        print(f"constitution local drift: {result.stage}: {result.message}")
        print(f"drift source: {result.source}")
        print(f"remediation: {result.remediation}")
        return result.exit_code

    print("constitution validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
