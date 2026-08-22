import unittest
from datetime import UTC, datetime, timedelta

from scripts import validate_constitution


class ConstitutionValidatorTests(unittest.TestCase):
    def test_drift_stage_boundaries(self) -> None:
        cases = (
            (timedelta(days=2, hours=23), "healthy", 0),
            (timedelta(days=3), "warning", 0),
            (timedelta(days=6, hours=23), "warning", 0),
            (timedelta(days=7), "restricted", 1),
            (timedelta(days=9, hours=23), "restricted", 1),
            (timedelta(days=10), "hard-stop", 1),
        )

        for age, expected_stage, expected_exit in cases:
            with self.subTest(age=age):
                result = validate_constitution.classify_drift(age)
                self.assertEqual(result.stage, expected_stage)
                self.assertEqual(result.exit_code, expected_exit)

    def test_matching_remote_revision_has_no_drift(self) -> None:
        committed_at = datetime(2026, 5, 28, tzinfo=UTC)
        sync = {
            "personal_philosophy": {
                "revision": "a" * 40,
                "committed_at": committed_at.isoformat(),
            },
            "drift_started_at": None,
            "resolution": "reflected",
        }
        remote = validate_constitution.ProfileHistory(
            latest=validate_constitution.ProfileRevision("a" * 40, committed_at),
            oldest_unreconciled=None,
        )

        result = validate_constitution.evaluate_remote_drift(
            sync, remote, datetime(2026, 8, 22, tzinfo=UTC)
        )

        self.assertEqual(result.stage, "healthy")
        self.assertEqual(result.exit_code, 0)

    def test_pending_record_is_not_cleared_by_matching_remote_revision(self) -> None:
        now = datetime(2026, 8, 22, tzinfo=UTC)
        started_at = now - timedelta(days=10)
        sync = {
            "personal_philosophy": {"revision": "a" * 40},
            "resolution": "pending",
            "drift_started_at": started_at.isoformat(),
        }
        remote = validate_constitution.ProfileHistory(
            latest=validate_constitution.ProfileRevision("a" * 40, now - timedelta(days=30)),
            oldest_unreconciled=None,
        )

        result = validate_constitution.evaluate_remote_drift(sync, remote, now)

        self.assertEqual(result.stage, "hard-stop")
        self.assertEqual(result.started_at, started_at)

    def test_unreconciled_remote_revision_uses_remote_commit_time(self) -> None:
        now = datetime(2026, 8, 22, tzinfo=UTC)
        remote_commit = now - timedelta(days=7)
        sync = {
            "personal_philosophy": {
                "revision": "a" * 40,
                "committed_at": "2026-05-28T00:42:29+00:00",
            },
            "drift_started_at": None,
            "resolution": "reflected",
        }
        remote = validate_constitution.ProfileHistory(
            latest=validate_constitution.ProfileRevision("b" * 40, now - timedelta(days=1)),
            oldest_unreconciled=validate_constitution.ProfileRevision("c" * 40, remote_commit),
        )

        result = validate_constitution.evaluate_remote_drift(sync, remote, now)

        self.assertEqual(result.stage, "restricted")
        self.assertEqual(result.started_at, remote_commit)

    def test_profile_history_uses_oldest_commit_after_recorded_revision(self) -> None:
        now = datetime(2026, 8, 22, tzinfo=UTC)
        commits = [
            validate_constitution.ProfileRevision("c" * 40, now - timedelta(days=1)),
            validate_constitution.ProfileRevision("b" * 40, now - timedelta(days=11)),
            validate_constitution.ProfileRevision("a" * 40, now - timedelta(days=30)),
        ]

        history = validate_constitution.profile_history_from_commits(commits, "a" * 40)

        self.assertEqual(history.latest.sha, "c" * 40)
        self.assertEqual(history.oldest_unreconciled.sha, "b" * 40)
        result = validate_constitution.evaluate_remote_drift(
            {
                "personal_philosophy": {"revision": "a" * 40},
                "resolution": "reflected",
                "drift_started_at": None,
            },
            history,
            now,
        )
        self.assertEqual(result.stage, "hard-stop")

    def test_local_validation_rejects_future_drift_start(self) -> None:
        sync = validate_constitution.load_sync()
        sync["resolution"] = "pending"
        sync["drift_source"] = "constitution"
        sync["drift_started_at"] = "2026-08-23T00:00:01+00:00"

        failures = validate_constitution.validate_local(
            sync, now=datetime(2026, 8, 23, tzinfo=UTC)
        )

        self.assertTrue(any("future" in failure for failure in failures))

    def test_remote_failure_is_evaluation_mode_b(self) -> None:
        def unavailable() -> validate_constitution.ProfileRevision:
            raise OSError("network unavailable")

        result = validate_constitution.run_remote_check(
            {}, now=datetime(2026, 8, 22, tzinfo=UTC), fetch=unavailable
        )

        self.assertEqual(result.stage, "undetermined-b")
        self.assertEqual(result.exit_code, 1)
        self.assertIn("network unavailable", result.message)

    def test_future_remote_commit_is_evaluation_mode_b(self) -> None:
        now = datetime(2026, 8, 22, tzinfo=UTC)
        remote = validate_constitution.ProfileHistory(
            latest=validate_constitution.ProfileRevision("b" * 40, now + timedelta(seconds=1)),
            oldest_unreconciled=validate_constitution.ProfileRevision("b" * 40, now + timedelta(seconds=1)),
        )
        result = validate_constitution.run_remote_check(
            {"personal_philosophy": {"revision": "a" * 40}, "resolution": "reflected"},
            now=now,
            fetch=lambda: remote,
        )
        self.assertEqual(result.stage, "undetermined-b")
        self.assertIn("future", result.message)

    def test_constitution_pending_uses_oldest_git_or_record_time(self) -> None:
        now = datetime(2026, 8, 22, tzinfo=UTC)
        sync = {
            "resolution": "pending",
            "drift_source": "constitution",
            "drift_started_at": (now - timedelta(days=4)).isoformat(),
        }
        result = validate_constitution.evaluate_local_drift(
            sync, now=now, unreconciled_start=now - timedelta(days=8)
        )
        self.assertEqual(result.stage, "restricted")
        self.assertEqual(result.source, "constitution")
        self.assertIsNotNone(result.remediation)

    def test_pending_constitution_may_retain_reconciled_hash(self) -> None:
        sync = validate_constitution.load_sync()
        sync["resolution"] = "pending"
        sync["drift_source"] = "constitution"
        sync["drift_started_at"] = "2026-08-22T00:00:00+00:00"
        sync["constitution_sha256"] = "0" * 64
        failures = validate_constitution.validate_local(
            sync, now=datetime(2026, 8, 23, tzinfo=UTC)
        )
        self.assertFalse(any("changed without" in failure for failure in failures))

    def test_local_validation_reports_malformed_schema_without_traceback(self) -> None:
        failures = validate_constitution.validate_local([], now=datetime(2026, 8, 23, tzinfo=UTC))  # type: ignore[arg-type]
        self.assertEqual(failures, ["sync record root must be a JSON object"])

        sync = validate_constitution.load_sync()
        sync["personal_philosophy"] = 42
        failures = validate_constitution.validate_local(
            sync, now=datetime(2026, 8, 23, tzinfo=UTC)
        )
        self.assertTrue(any("personal_philosophy must" in failure for failure in failures))

        for field in ("constitution_sha256", "drift_started_at"):
            with self.subTest(field=field):
                malformed = validate_constitution.load_sync()
                if field == "drift_started_at":
                    malformed["resolution"] = "pending"
                    malformed["drift_source"] = "constitution"
                malformed[field] = 42
                failures = validate_constitution.validate_local(
                    malformed, now=datetime(2026, 8, 23, tzinfo=UTC)
                )
                self.assertTrue(failures)

    def test_constitution_history_keeps_oldest_unreconciled_commit(self) -> None:
        now = datetime(2026, 8, 22, tzinfo=UTC)
        revisions = [
            validate_constitution.ConstitutionRevision("d" * 40, "c" * 64, now - timedelta(days=1)),
            validate_constitution.ConstitutionRevision("c" * 40, "a" * 64, now - timedelta(days=2)),
            validate_constitution.ConstitutionRevision("b" * 40, "b" * 64, now - timedelta(days=11)),
            validate_constitution.ConstitutionRevision("a" * 40, "a" * 64, now - timedelta(days=30)),
        ]
        started_at = validate_constitution.constitution_history_from_revisions(
            revisions, "a" * 40
        )
        self.assertEqual(started_at, now - timedelta(days=11))

        with self.assertRaisesRegex(ValueError, "not found"):
            validate_constitution.constitution_history_from_revisions(revisions, "e" * 40)

    def test_profile_change_during_constitution_pending_marks_both_sources(self) -> None:
        now = datetime(2026, 8, 22, tzinfo=UTC)
        sync = {
            "personal_philosophy": {"revision": "a" * 40},
            "resolution": "pending",
            "drift_source": "constitution",
            "drift_started_at": (now - timedelta(days=1)).isoformat(),
        }
        remote = validate_constitution.ProfileHistory(
            latest=validate_constitution.ProfileRevision("b" * 40, now),
            oldest_unreconciled=validate_constitution.ProfileRevision(
                "b" * 40, now - timedelta(days=2)
            ),
        )
        result = validate_constitution.evaluate_remote_drift(sync, remote, now)
        self.assertEqual(result.source, "both")

    def test_remote_and_local_checks_use_the_older_drift_start(self) -> None:
        now = datetime(2026, 8, 22, tzinfo=UTC)
        remote = validate_constitution.DriftResult(
            "healthy", 0, "remote", now - timedelta(days=1), "personal-philosophy", "sync"
        )
        local = validate_constitution.DriftResult(
            "hard-stop", 1, "local", now - timedelta(days=11), "constitution", "sync"
        )
        result = validate_constitution.stricter_result(remote, local, now=now)
        self.assertEqual(result.stage, "hard-stop")
        self.assertEqual(result.source, "both")

    def test_mode_b_has_source_and_remediation(self) -> None:
        result = validate_constitution.run_remote_check(
            {},
            now=datetime(2026, 8, 22, tzinfo=UTC),
            fetch=lambda: (_ for _ in ()).throw(OSError("offline")),
        )
        self.assertEqual(result.source, "unknown")
        self.assertIsNotNone(result.remediation)


if __name__ == "__main__":
    unittest.main()
