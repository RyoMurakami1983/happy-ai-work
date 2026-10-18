"""
Contract Verification Checkpoint for implement.

Validates that all required artifacts from dependent repos are present
and verifies checksums match between upstream provides and local requires.

This checkpoint runs during contract verification in the implement workflow,
before execution starts for repos that depend on upstream artifacts.

On first run (checksum is null in plan_dict), calculates and updates the checksum.
On subsequent runs, verifies checksum matches.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class CheckpointResult:
    """Result of checkpoint verification."""

    status: str  # "PASS" or "FAIL"
    reason: str


class ContractMismatchError(Exception):
    """Raised when contract verification fails."""

    pass


def verify_contracts(plan_dict: dict[str, Any], repo_root: Path) -> CheckpointResult:
    """
    Verify all required contracts in the plan.

    On first run (checksum is null), calculates actual checksum from file and updates plan_dict.
    On subsequent runs (checksum exists), validates that actual checksum matches.

    Args:
        plan_dict: Plan YAML front-matter as dict, containing dependencies.contracts.requires
                   Schema: requires[*] = {source_repo, artifact, path, checksum (null | hex)}
        repo_root: Path to the repository root

    Returns:
        CheckpointResult with status and reason
        Updates plan_dict[dependencies][contracts][requires][idx][checksum] on first run

    Raises:
        None (returns FAIL status instead of raising)
    """
    # Handle missing dependencies section
    if not plan_dict:
        return CheckpointResult(
            status="PASS", reason="No plan dictionary provided: 0 contracts verified"
        )

    dependencies = plan_dict.get("dependencies", {})
    contracts = dependencies.get("contracts", {})
    requires = contracts.get("requires", [])

    # No required contracts
    if not requires:
        return CheckpointResult(
            status="PASS", reason="No required contracts: 0 artifacts to verify"
        )

    # Verify each required artifact
    failed_artifacts = []
    verified_count = 0

    for idx, require in enumerate(requires):
        artifact_name = require.get("artifact", "unknown")
        artifact_path_str = require.get("path", "")
        checksum_value = require.get("checksum")  # Can be None, hex string

        artifact_path = repo_root / artifact_path_str

        # Check if artifact exists
        if not artifact_path.exists():
            failed_artifacts.append(
                {
                    "artifact": artifact_name,
                    "path": artifact_path_str,
                    "reason": "missing",
                }
            )
            continue

        # Calculate actual checksum from file
        actual_content = artifact_path.read_bytes()
        actual_checksum = hashlib.sha256(actual_content).hexdigest()

        # Handle first run: checksum is null, calculate and update plan_dict
        if checksum_value is None:
            # Update plan_dict with calculated checksum
            plan_dict["dependencies"]["contracts"]["requires"][idx]["checksum"] = (
                actual_checksum
            )
            verified_count += 1
            continue

        # Verify checksum matches (subsequent runs)
        if actual_checksum != checksum_value:
            failed_artifacts.append(
                {
                    "artifact": artifact_name,
                    "path": artifact_path_str,
                    "reason": "checksum_mismatch",
                    "expected": checksum_value,
                    "actual": actual_checksum,
                }
            )
            continue

        # Artifact verified
        verified_count += 1

    # Return failure if any artifact failed
    if failed_artifacts:
        return _build_failure_result(failed_artifacts, verified_count, requires)

    # All contracts verified; persist updated checksums to plan.md if it exists
    plan_file = repo_root / "plan.md"
    if plan_file.exists():
        save_plan_with_updated_checksums(plan_file, plan_dict)

    # All contracts verified
    return CheckpointResult(
        status="PASS",
        reason=f"Contract verified: {len(requires)} artifacts, {verified_count} checksums validated",
    )


def _build_failure_result(
    failed_artifacts: list[dict[str, Any]], verified_count: int, requires: list[Any]
) -> CheckpointResult:
    """Build a detailed failure result with actionable error message."""
    error_parts = [
        "Contract verification failed:",
    ]

    for failed in failed_artifacts:
        artifact = failed["artifact"]
        path = failed["path"]
        reason = failed["reason"]

        if reason == "missing":
            error_parts.append(
                f"\n  - Missing artifact: {artifact}"
                f"\n    Path: {path}"
                f"\n    Action: Check if upstream repo merged PR with this artifact"
                f"\n    Remediation: Wait for upstream implement to complete, or verify path is correct"
            )
        elif reason == "checksum_mismatch":
            expected = failed.get("expected", "unknown")
            actual = failed.get("actual", "unknown")
            error_parts.append(
                f"\n  - Checksum mismatch: {artifact}"
                f"\n    Path: {path}"
                f"\n    Expected: {expected}"
                f"\n    Actual:   {actual}"
                f"\n    Action: Upstream artifact changed since design handoff"
                f"\n    Remediation: Revisit technical-design or the planning phase of implement"
            )

    if verified_count > 0:
        error_parts.append(f"\n  ({verified_count}/{len(requires)} artifacts verified)")

    reason = "".join(error_parts)

    return CheckpointResult(status="FAIL", reason=reason)


def save_plan_with_updated_checksums(plan_path: Path, plan_dict: dict[str, Any]) -> None:
    """Save plan.md with updated checksums in YAML front-matter.

    Treat the on-disk front-matter as authoritative for every field except the
    verified requires checksums. Leave the file untouched when none changed.
    """
    if not plan_path.exists():
        return  # Nothing to save if no file

    # Keep line endings and the Markdown body byte-for-byte, including EOF.
    original_content = plan_path.read_bytes().decode("utf-8")
    lines = original_content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return

    # Find YAML front-matter boundaries
    yaml_end_idx = None
    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            yaml_end_idx = idx
            break

    if yaml_end_idx is None:
        return  # No YAML front-matter found, can't update

    front_matter = yaml.safe_load("".join(lines[1:yaml_end_idx]))
    if not isinstance(front_matter, dict):
        return

    # Match contracts by identity rather than overwriting metadata or relying on
    # list positions: the caller can hold a partial or differently ordered plan.
    identity_fields = ("source_repo", "artifact", "path", "version")
    updated_requires = plan_dict.get("dependencies", {}).get("contracts", {}).get("requires", [])
    updated_checksums = {
        tuple(require.get(field) for field in identity_fields): require["checksum"]
        for require in updated_requires
        if require.get("checksum") is not None
    }
    saved_dependencies = front_matter.get("dependencies", {})
    saved_contracts = saved_dependencies.get("contracts", {})
    saved_requires = saved_contracts.get("requires", [])
    merged_requires = []
    changed = False
    for require in saved_requires:
        identity = tuple(require.get(field) for field in identity_fields)
        checksum = updated_checksums.get(identity)
        if checksum is not None and require.get("checksum") != checksum:
            require = {**require, "checksum": checksum}
            changed = True
        merged_requires.append(require)

    if not changed:
        return

    # Copy only the updated path so YAML aliases in other metadata keep their values.
    front_matter["dependencies"] = {
        **saved_dependencies,
        "contracts": {**saved_contracts, "requires": merged_requires},
    }
    newline = "\r\n" if lines[0].endswith("\r\n") else "\n"
    yaml_str = yaml.safe_dump(
        front_matter, default_flow_style=False, sort_keys=False, allow_unicode=True, line_break=newline
    )
    updated_content = lines[0] + yaml_str + "".join(lines[yaml_end_idx:])

    plan_path.write_bytes(updated_content.encode("utf-8"))
