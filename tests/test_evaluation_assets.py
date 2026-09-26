import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import validate_eval_manifest_links, validate_evals

ROOT = Path(__file__).resolve().parents[1]


class EvaluationAssetTests(unittest.TestCase):
    def test_public_suites_are_versioned_and_never_holdouts(self) -> None:
        suites = sorted((ROOT / "evals").glob("*/cases.v*.json"))
        self.assertEqual(
            {path.parent.name for path in suites},
            {
                "skill-eval",
                "improvement-loop",
                "instruction-finalization",
                "interactive-review-loop",
                "ui-design",
                "to-prd-purpose",
                "technical-design-review",
                "consultation-start",
                "workflow-entry",
                "workflow-startup",
            },
        )
        for path in suites:
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(payload["visibility"], "public")
            self.assertIn(payload["case_kind"], {"upstream-eval", "common-safety-eval"})
            self.assertTrue(all(case["holdout"] is False for case in payload["cases"]))
            self.assertEqual(
                {case["type"] for case in payload["cases"]},
                {"happy-path", "near-miss", "failure-missing-context"},
            )

    def test_policy_rejects_forbidden_fields_and_public_holdout(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            path = Path(directory) / "cases.v1.json"
            payload = {
                "schema_version": 1,
                "suite_version": "1.0.0",
                "target": Path(directory).name,
                "case_kind": "upstream-eval",
                "visibility": "public",
                "constitution_version": "1.0.0",
                "evaluation_criteria_version": "1.0.0",
                "raw_transcript": "must not be tracked",
                "cases": [
                    {"id": f"case-{index}", "type": case_type, "holdout": index == 0,
                     "prompt": "prompt", "critical": ["c"], "normal": ["n"], "prohibited": ["p"]}
                    for index, case_type in enumerate(
                        ("happy-path", "near-miss", "failure-missing-context")
                    )
                ],
            }
            path.write_text(json.dumps(payload), encoding="utf-8")
            failures: list[str] = []
            schema = json.loads(
                (ROOT / "evals" / "schema" / "case.schema.json").read_text(encoding="utf-8")
            )
            validate_evals.validate_case_suite(path, failures, schema)
        self.assertTrue(any("holdout false" in failure for failure in failures))
        self.assertTrue(any("forbidden field raw_transcript" in failure for failure in failures))

    def test_append_only_policy_rejects_modified_or_deleted_records(self) -> None:
        completed = subprocess.CompletedProcess(
            [],
            0,
            stdout=(
                " M evals/records/old.json\n"
                "D  evals/schema/case.schema.json\n"
                " R evals/skill-eval/cases.v1.json\n"
            ),
        )
        with (
            mock.patch.object(validate_evals.subprocess, "run", return_value=completed),
            mock.patch.dict(validate_evals.os.environ, {"GITHUB_ACTIONS": "false"}),
        ):
            failures: list[str] = []
            validate_evals.validate_append_only(failures)
        self.assertEqual(len(failures), 3)

    def test_append_only_policy_rejects_committed_changes_in_ci(self) -> None:
        clean = subprocess.CompletedProcess([], 0, stdout="")
        committed = subprocess.CompletedProcess(
            [],
            0,
            stdout="M\tevals/records/old.json\nA\tevals/records/new.json\n",
        )
        with (
            mock.patch.object(validate_evals.subprocess, "run", side_effect=[clean, committed]),
            mock.patch.dict(
                validate_evals.os.environ,
                {"GITHUB_ACTIONS": "true", "GITHUB_BASE_REF": "main"},
            ),
        ):
            failures: list[str] = []
            validate_evals.validate_append_only(failures)
        self.assertEqual(len(failures), 1)
        self.assertIn("origin/main...HEAD", failures[0])

    def test_append_only_push_uses_event_before_sha_and_rejects_type_change(self) -> None:
        before = "a" * 40
        clean = subprocess.CompletedProcess([], 0, stdout="")
        committed = subprocess.CompletedProcess(
            [],
            0,
            stdout="T\tevals/schema/record.schema.json\n",
        )
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            event = Path(directory) / "event.json"
            event.write_text(json.dumps({"before": before}), encoding="utf-8")
            with (
                mock.patch.object(
                    validate_evals.subprocess,
                    "run",
                    side_effect=[clean, committed],
                ) as run,
                mock.patch.dict(
                    validate_evals.os.environ,
                    {
                        "GITHUB_ACTIONS": "true",
                        "GITHUB_BASE_REF": "",
                        "GITHUB_EVENT_PATH": str(event),
                    },
                ),
            ):
                failures: list[str] = []
                validate_evals.validate_append_only(failures)
        self.assertEqual(len(failures), 1)
        self.assertIn(f"{before}...HEAD", failures[0])
        self.assertIn(f"{before}...HEAD", run.call_args_list[1].args[0])

    def test_policy_inspects_unknown_json_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            evals_dir = Path(directory) / "evals"
            path = evals_dir / "pilot" / "context.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"private_code": "not allowed"}), encoding="utf-8")
            failures: list[str] = []
            validate_evals.validate_tracking_policy(failures, evals_dir=evals_dir)
        self.assertTrue(any("forbidden field private_code" in failure for failure in failures))

    def test_policy_rejects_hyphenated_sealed_and_holdout_filenames(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            evals_dir = Path(directory) / "evals"
            pilot = evals_dir / "pilot"
            pilot.mkdir(parents=True)
            (pilot / "sealed-prompt.json").write_text("{}", encoding="utf-8")
            (pilot / "private-holdout.json").write_text("{}", encoding="utf-8")
            failures: list[str] = []
            validate_evals.validate_tracking_policy(failures, evals_dir=evals_dir)
        self.assertEqual(sum("forbidden evaluation artifact" in item for item in failures), 2)

    def test_case_schema_rejects_invalid_case_items(self) -> None:
        schema = json.loads(
            (ROOT / "evals" / "schema" / "case.schema.json").read_text(encoding="utf-8")
        )
        payload = json.loads(
            (ROOT / "evals" / "skill-eval" / "cases.v3.json").read_text(encoding="utf-8")
        )
        payload["cases"][0]["critical"] = "not-an-array"
        failures: list[str] = []
        validate_evals.validate_against_schema(payload, schema, location="fixture", failures=failures)
        self.assertTrue(any("expected array" in failure for failure in failures))

    def test_retired_case_requires_replacement_and_reason(self) -> None:
        schema = json.loads(
            (ROOT / "evals" / "schema" / "case.schema.json").read_text(encoding="utf-8")
        )
        payload = json.loads(
            (ROOT / "evals" / "skill-eval" / "cases.v3.json").read_text(encoding="utf-8")
        )
        payload["cases"][0]["status"] = "retired"
        failures: list[str] = []
        path = ROOT / "evals" / "skill-eval" / "cases.v3.json"
        with mock.patch.object(validate_evals, "load_json", return_value=payload):
            validate_evals.validate_case_suite(path, failures, schema)
        self.assertTrue(any("requires replaced_by" in failure for failure in failures))
        self.assertTrue(any("requires retirement_reason" in failure for failure in failures))

    def test_adopted_record_requires_complete_decision_evidence(self) -> None:
        schema = json.loads(
            (ROOT / "evals" / "schema" / "record.schema.json").read_text(encoding="utf-8")
        )
        path = ROOT / "evals" / "records" / "evaluation-assets-adoption-001.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload.pop("artifact_hashes")
        payload["roles"]["independence"]["status"] = "invalid"
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            fixture = Path(directory) / path.name
            fixture.write_text(json.dumps(payload), encoding="utf-8")
            failures: list[str] = []
            validate_evals.validate_record(fixture, failures, schema)
        self.assertTrue(any("missing required property artifact_hashes" in item for item in failures))
        self.assertTrue(any("adopted record requires valid independence" in item for item in failures))

    def test_record_artifact_hashes_must_be_sha256_and_match_files(self) -> None:
        schema = json.loads(
            (ROOT / "evals" / "schema" / "record.schema.json").read_text(encoding="utf-8")
        )
        path = ROOT / "evals" / "records" / "evaluation-assets-adoption-001.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        artifact = next(iter(payload["artifact_hashes"]))
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            fixture = Path(directory) / path.name
            payload["artifact_hashes"][artifact] = "garbage"
            fixture.write_text(json.dumps(payload), encoding="utf-8")
            malformed: list[str] = []
            validate_evals.validate_record(fixture, malformed, schema)
            payload["artifact_hashes"][artifact] = "0" * 64
            fixture.write_text(json.dumps(payload), encoding="utf-8")
            stale: list[str] = []
            validate_evals.validate_record(fixture, stale, schema)
        self.assertTrue(any("string does not match pattern" in item for item in malformed))
        self.assertTrue(any("artifact hash mismatch" in item for item in stale))

    def test_record_hashes_must_match_the_frozen_artifact_manifest(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            fixture_root = Path(directory)
            manifest_path = fixture_root / "evals" / "pilot" / "001" / "TARGET.json"
            manifest_path.parent.mkdir(parents=True)
            manifest = {"conditions": {"current": {"artifacts": {"artifact.md": "a" * 64}}}}
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            record_path = fixture_root / "evals" / "records" / "test-record.json"
            record_path.parent.mkdir(parents=True)
            record = {
                "conditions": {
                    "evaluation_context": {"artifact_manifest": "evals/pilot/001/TARGET.json"}
                },
                "artifact_hashes": {
                    "evals/pilot/001/TARGET.json": validate_eval_manifest_links.hashlib.sha256(
                        manifest_path.read_bytes()
                    ).hexdigest(),
                    "artifact.md": "b" * 64,
                },
            }
            record_path.write_text(json.dumps(record), encoding="utf-8")
            failures = validate_eval_manifest_links.validate_records(fixture_root)
        self.assertTrue(any("record hash differs from artifact manifest" in item for item in failures))

    def test_target_rejects_conflicting_duplicate_artifact_hashes(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            fixture_root = Path(directory)
            manifest_path = fixture_root / "evals" / "pilot" / "001" / "TARGET.json"
            manifest_path.parent.mkdir(parents=True)
            manifest = {
                "artifact_hashes": {"artifact.md": "a" * 64},
                "conditions": {"current": {"artifacts": {"artifact.md": "b" * 64}}},
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            record_path = fixture_root / "evals" / "records" / "test-record.json"
            record_path.parent.mkdir(parents=True)
            record = {
                "conditions": {
                    "evaluation_context": {"artifact_manifest": "evals/pilot/001/TARGET.json"}
                },
                "artifact_hashes": {
                    "evals/pilot/001/TARGET.json": validate_eval_manifest_links.hashlib.sha256(
                        manifest_path.read_bytes()
                    ).hexdigest(),
                    "artifact.md": "b" * 64,
                },
            }
            record_path.write_text(json.dumps(record), encoding="utf-8")
            failures = validate_eval_manifest_links.validate_records(fixture_root)
        self.assertTrue(any("conflicting frozen hashes" in item for item in failures))

    def test_docs_define_public_private_and_role_boundaries(self) -> None:
        text = (ROOT / "docs" / "EVALUATION_ASSETS.md").read_text(encoding="utf-8")
        for required in (
            "upstream eval",
            "共通安全eval",
            "private eval",
            "未見hold-outとして再利用しない",
            "AI grader／comparator",
            "raw run",
            "append-only",
            "downstream",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_skill_eval_requires_high_risk_decision_checkpoint(self) -> None:
        skill = (
            ROOT / "plugins" / "happy-core" / "skills" / "skill-eval" / "SKILL.md"
        ).read_text(encoding="utf-8")
        governance = (
            ROOT
            / "plugins"
            / "happy-core"
            / "skills"
            / "skill-eval"
            / "references"
            / "evaluation-governance.md"
        ).read_text(encoding="utf-8")
        self.assertIn("採用可否、独立再評価", skill)
        for required in (
            "採用・独立再評価checkpoint",
            "`hold-out`",
            "`independence`",
            "`prior record`",
            "`new record`",
            "`public artifact`",
            "`decision`",
            "通常のユーザー向け回答",
            "固定templateと構造fieldへ二重に書かない",
            "decision invariants",
            "response quality",
            "棄却やFAILであることを理由にCを選ばない",
            "hold-outの汚染だけを根拠にしない",
            "必ず`new record: required`",
        ):
            with self.subTest(required=required):
                self.assertIn(required, governance)

    def test_v3_cases_separate_decision_invariants_from_response_quality(self) -> None:
        payload = json.loads(
            (ROOT / "evals" / "skill-eval" / "cases.v3.json").read_text(encoding="utf-8")
        )
        derived = next(
            case for case in payload["cases"] if case["id"] == "skill-eval-derived-public-case-003"
        )
        self.assertTrue(any("採用判定を止める" in item for item in derived["critical"]))
        self.assertTrue(any("新規sealed" in item for item in derived["normal"]))
        final_record = next(
            case for case in payload["cases"] if case["id"] == "skill-eval-final-record-003"
        )
        self.assertTrue(any("構造field" in item for item in final_record["critical"]))

    def test_packaged_evaluation_reference_is_self_contained(self) -> None:
        text = (
            ROOT
            / "plugins"
            / "happy-core"
            / "skills"
            / "skill-eval"
            / "references"
            / "evaluation-assets.md"
        ).read_text(encoding="utf-8")
        self.assertIn("配布plugin内で自己完結", text)
        self.assertNotIn("../../../../../docs/", text)


if __name__ == "__main__":
    unittest.main()
