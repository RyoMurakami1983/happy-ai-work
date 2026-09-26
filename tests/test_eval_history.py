import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import validate_evals


class EvaluationHistoryTests(unittest.TestCase):
    def check_record(self, *, change: str = "") -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            record_path = root / "evals/records/example.json"
            record_path.parent.mkdir(parents=True)
            artifact = root / "skill.md"
            artifact.write_text("new instructions", encoding="utf-8")
            snapshot = root / "evals/example/snapshots/v1/skill.md"
            snapshot.parent.mkdir(parents=True)
            snapshot.write_text("old instructions", encoding="utf-8")
            payload = json.loads(
                (validate_evals.ROOT / "evals/records/technical-design-review-preview-001.json")
                .read_text(encoding="utf-8")
            )
            payload["record_id"] = "example"
            payload["artifact_hashes"] = {
                "skill.md": hashlib.sha256(snapshot.read_bytes()).hexdigest()
            }
            record_path.write_text(json.dumps(payload), encoding="utf-8")
            history = root / "evals/history/example.json"
            history.parent.mkdir(parents=True)
            mapping = {
                "record_sha256": hashlib.sha256(record_path.read_bytes()).hexdigest(),
                "artifacts": {"skill.md": "evals/example/snapshots/v1/skill.md"},
            }
            if change == "snapshot":
                snapshot.write_text("tampered", encoding="utf-8")
            elif change == "record":
                payload["decision_summary"] = "modified record"
                record_path.write_text(json.dumps(payload), encoding="utf-8")
            elif change == "escape":
                mapping["artifacts"]["skill.md"] = "../outside.md"
            elif change == "unmapped":
                mapping["artifacts"] = {"other.md": "evals/example/snapshots/v1/skill.md"}
            history.write_text(json.dumps(mapping), encoding="utf-8")
            if change == "no-history":
                history.unlink()
            failures: list[str] = []
            with mock.patch.object(validate_evals, "ROOT", root):
                validate_evals.validate_record(record_path, failures, {})
            return failures

    def test_archived_record_matches_snapshot_after_skill_changes(self) -> None:
        self.assertEqual(self.check_record(), [])

    def test_snapshot_tampering_is_rejected(self) -> None:
        self.assertTrue(any("hash mismatch" in x for x in self.check_record(change="snapshot")))

    def test_record_tampering_cannot_reuse_history(self) -> None:
        self.assertTrue(any("record hash" in x for x in self.check_record(change="record")))

    def test_history_cannot_escape_repository(self) -> None:
        self.assertTrue(any("snapshot" in x for x in self.check_record(change="escape")))

    def test_history_cannot_map_unknown_artifacts(self) -> None:
        self.assertTrue(any("unknown artifact" in x for x in self.check_record(change="unmapped")))

    def test_current_record_still_rejects_stale_hash(self) -> None:
        self.assertTrue(any("hash mismatch" in x for x in self.check_record(change="no-history")))

    def test_history_and_snapshots_are_append_only(self) -> None:
        failures: list[str] = []
        validate_evals.inspect_append_only_status(
            "M\tevals/history/example.json\nD\tevals/example/snapshots/v1/skill.md\n",
            failures,
            source="test",
        )
        self.assertEqual(len(failures), 2)


if __name__ == "__main__":
    unittest.main()
