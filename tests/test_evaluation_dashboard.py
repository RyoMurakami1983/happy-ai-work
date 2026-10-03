"""Behavioral contract for local, sanitized dashboard imports (synthetic fixtures)."""

import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluation_dashboard.py"


class EvaluationDashboardTests(unittest.TestCase):
    def assert_summary_refused_without_changing_bytes(self, kind: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            source_bytes = json.dumps(self.fixture()).encode("utf-8")
            source.write_bytes(source_bytes)
            output = Path(directory) / "summary.json"
            previous_bytes = b"previous immutable summary\n"
            if kind == "input":
                output = source
            elif kind == "prior":
                output.write_bytes(previous_bytes)
            elif kind == "symlink":
                try:
                    output.symlink_to(source)
                except OSError as exc:
                    self.skipTest(f"symlink creation unavailable: {exc}")
            elif kind == "hardlink":
                try:
                    os.link(source, output)
                except OSError as exc:
                    self.skipTest(f"hardlink creation unavailable: {exc}")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--summary", str(output)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("summary", result.stderr)
            self.assertEqual(source.read_bytes(), source_bytes)
            self.assertEqual(output.read_bytes(), previous_bytes if kind == "prior" else source_bytes)

    def test_cli_refuses_input_as_summary_output(self) -> None:
        self.assert_summary_refused_without_changing_bytes("input")

    def test_cli_preserves_existing_summary_bytes(self) -> None:
        self.assert_summary_refused_without_changing_bytes("prior")

    def test_cli_refuses_symlink_output_alias(self) -> None:
        self.assert_summary_refused_without_changing_bytes("symlink")

    def test_cli_refuses_hardlink_output_alias(self) -> None:
        self.assert_summary_refused_without_changing_bytes("hardlink")

    def test_cli_reports_new_output_io_failure_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            source.write_text(json.dumps(self.fixture()), encoding="utf-8")
            output = Path(directory) / "missing-parent" / "summary.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--summary", str(output)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("summary", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(output.exists())

    @staticmethod
    def fixture() -> dict:
        return json.loads((ROOT / "tests/fixtures/dashboard/synthetic.v1.json").read_text(encoding="utf-8"))

    @staticmethod
    def mutate(payload: dict, path: tuple, value: object) -> dict:
        result = copy.deepcopy(payload)
        target = result
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        return result

    def invalid_examples(self) -> list[dict]:
        payload = self.fixture()
        case = ("runs", 0, "cases", 0)
        mutations = [
            (("schema_version",), 2), (("sanitized",), False), (("unexpected",), "no"),
            (("runs", 0, "iteration"), 1.5), (("runs", 0, "iteration"), True),
            (case + ("q",), -1), (case + ("q",), 101), (case + ("q",), True),
            (case + ("b",), 11), (case + ("b",), -0.1),
            (case + ("outcome",), "fail"), (case + ("gates", "safety"), "fail"),
            (case + ("burden_basis",), "estimated"), (case + ("evidence",), []),
            (case + ("burden_details", "raw_burden", "value"), -1),
            (case + ("burden_details", "human_review_time", "basis"), "unavailable"),
            (case + ("burden_details", "event_links", 0, "work_event_ids"), ["same", "same"]),
            (("methods", 0, "preregistration", "locked_at"), "2026-10-01T00:00:00Z"),
            (("methods", 0, "lambda"), None), (("methods", 0, "beta"), -1),
            (("methods", 0, "q_max"), 0), (("methods", 0, "locked"), False),
            (("runs", 0, "started_at"), "2026-02-30T00:00:00Z"),
            (("runs", 0, "method_id"), "missing"),
            (("runs", 0, "assigned_case_ids"), ["demo-case-1"]),
            (("runs", 0, "cases", 1, "id"), payload["runs"][0]["cases"][0]["id"]),
            (("runs", 0, "cases", 1, "case_id"), "demo-case-1"),
            (("runs", 0, "provenance", "harness", "sha256"), "bad"),
            (("export_id",), "bad\n"), (("export_id",), "x" * 129),
            (("runs", 0, "condition_sha256"), "a" * 64 + "\n"),
            (("runs", 0, "cases", 5, "gates", "safety"), "fail"),
            (case + ("summary",), "gh" + "p_" + "synthetic-secret-detection"),
        ]
        return [self.mutate(payload, path, value) for path, value in mutations]

    def test_rejects_malformed_contract_values(self) -> None:
        from scripts import evaluation_dashboard as dashboard
        for index, payload in enumerate(self.invalid_examples()):
            with self.subTest(example=index), self.assertRaises(dashboard.ValidationError):
                dashboard.loads(json.dumps(payload))
        fixture = json.dumps(self.fixture())
        for text in ('{"x":1,"x":2}', '{"q":1,"\\u0071":2}',
                     fixture.replace('"q": 80', '"q": NaN'),
                     fixture.replace('"q": 80', '"q": Infinity'),
                     fixture.replace('"q": 80', '"q": 1e309'),
                     ' ' * (dashboard.MAX_BYTES + 1), '\ufeff' + fixture):
            with self.subTest(text=text[:50]), self.assertRaises(dashboard.ValidationError):
                dashboard.loads(text)

    def test_draft_and_insufficient_evidence_never_receive_s(self) -> None:
        from scripts import evaluation_dashboard as dashboard
        base = self.fixture()
        for path, value in [
            (("independence",), "unknown"), (("contamination",), "contaminated"),
            (("trace",), "insufficient"), (("burden_details", "accounting"), "unverified"),
            (("burden_details", "event_links"), []),
        ]:
            payload = self.mutate(base, ("runs", 0, "cases", 0) + path, value)
            first = dashboard.summarize(dashboard.validate(payload))["runs"][0]
            self.assertEqual(first["assigned"], 6)
            self.assertEqual(first["counts"]["pass"], 1)
            self.assertIsNone(first["s"])
            self.assertEqual(first["s_count"], 0)
        draft = copy.deepcopy(base)
        draft["methods"][0].update(locked=False, preregistration=None, **{"lambda": None, "beta": None})
        self.assertIsNone(dashboard.summarize(dashboard.validate(draft))["runs"][0]["s"])

    def test_cohort_partitions_every_fixed_execution_boundary(self) -> None:
        from scripts import evaluation_dashboard as dashboard
        payload = self.fixture()
        run, method = payload["runs"][0], payload["methods"][0]
        key = dashboard.cohort_key(run, method, "synthetic")
        for path in [
            ("condition_id",), ("condition_sha256",), ("evaluation_mode",),
            ("provenance", "model_id"), ("provenance", "model_snapshot"),
            ("provenance", "reasoning_effort"), ("provenance", "tools", 0, "sha256"),
            ("provenance", "permissions", "sha256"), ("provenance", "execution_profile", "sha256"),
            ("provenance", "fixture", "sha256"), ("provenance", "dataset", "sha256"),
            ("provenance", "harness", "version"), ("provenance", "sources", 0, "sha256"),
            ("cases", 0, "family"), ("cases", 0, "case_id"),
        ]:
            with self.subTest(path=path):
                self.assertNotEqual(key, dashboard.cohort_key(self.mutate(run, path, "changed"), method, "synthetic"))
        for field, value in [("lambda", 0.2), ("q_max", 90), ("burden_basis", "estimated"),
                             ("version", "v-next"), ("burden_unit", "other-units")]:
            self.assertNotEqual(key, dashboard.cohort_key(run, {**method, field: value}, "synthetic"))
        changed_revision = self.mutate(run, ("provenance", "implementation_revision"), "a" * 40)
        self.assertEqual(key, dashboard.cohort_key(changed_revision, method, "synthetic"))
        self.assertNotEqual(key, dashboard.cohort_key(run, method, "real"))
        full = dashboard.summarize(payload)
        filtered = dashboard.summarize(payload, "docs")
        self.assertEqual(full["runs"][0]["cohort"], filtered["runs"][0]["cohort"])
        self.assertEqual(filtered["runs"][0]["assigned"], 3)
        self.assertNotIn("rate", full)
        self.assertNotIn("s", full)

    def test_embedded_schema_and_fixture_match_canonical_files(self) -> None:
        html = (ROOT / "docs/evaluation-dashboard.html").read_text(encoding="utf-8")
        for name, path in [("DASHBOARD_SCHEMA", "evals/schema/dashboard-export.v1.schema.json"),
                           ("SYNTHETIC_FIXTURE", "tests/fixtures/dashboard/synthetic.v1.json")]:
            match = re.search(r"const " + name + r" = (.*?);\n", html)
            assert match is not None
            embedded = match[1]
            self.assertEqual(json.loads(embedded), json.loads((ROOT / path).read_text(encoding="utf-8")))
        schema = json.loads((ROOT / "evals/schema/dashboard-export.v1.schema.json").read_text(encoding="utf-8"))
        pattern = schema["$defs"]["id"]["pattern"]
        for identifier in ("!bad!", "x" * 129, "okay\n", "before okay after"):
            self.assertIsNone(re.search(pattern, identifier))
        self.assertIsNotNone(re.search(pattern, "valid-ID.1"))

    @unittest.skipUnless(shutil.which("node"), "Node runtime is not installed")
    def test_browser_python_parity_and_missing_trend_segments(self) -> None:
        from scripts import evaluation_dashboard as dashboard
        base = self.fixture()
        numeric = self.mutate(base, ("schema_version",), 1.0)
        numeric["runs"][0]["iteration"] = 1.0
        inputs = [json.dumps(base), json.dumps(numeric)] + [json.dumps(p) for p in self.invalid_examples()]
        inputs += ['{"q":1,"q":2}', json.dumps(base).replace('"q": 80', '"q": 1e309')]
        expected = []
        for text in inputs:
            try:
                dashboard.loads(text)
                expected.append(True)
            except dashboard.ValidationError:
                expected.append(False)
        program = r"""
const fs=require('fs');
eval(fs.readFileSync(process.argv[1],'utf8').match(/<script id="dashboard-runtime">([\s\S]*?)<\/script>/)[1]);
const api=module.exports;
const inputs=JSON.parse(fs.readFileSync(0,'utf8'));
const accepted=inputs.map(text=>{try{api.parseImport(text);return true;}catch{return false;}});
const rows=[{id:'1',cohort:'a',iteration:1,s:10},{id:'2',cohort:'a',iteration:2,s:null},
{id:'3',cohort:'a',iteration:3,s:20},{id:'5',cohort:'a',iteration:5,s:30},
{id:'6',cohort:'a',iteration:6,s:40},{id:'7',cohort:'b',iteration:7,s:50}];
process.stdout.write(JSON.stringify({accepted,segments:api.segments(rows,'s').map(pair=>pair.map(r=>r.id))}));
"""
        result = subprocess.run(
            ["node", "-e", program, str(ROOT / "docs/evaluation-dashboard.html")],
            input=json.dumps(inputs), text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        observed = json.loads(result.stdout)
        self.assertEqual(expected, observed["accepted"])
        self.assertEqual(observed["segments"], [["5", "6"]])

    def test_html_exposes_offline_import_clear_and_error_controls(self) -> None:
        html = (ROOT / "docs/evaluation-dashboard.html").read_text(encoding="utf-8")
        for marker in ('id="import-file"', 'id="clear"', 'id="import-error"', "connect-src 'none'"):
            self.assertIn(marker, html)
        self.assertNotIn("localStorage", html)
        self.assertNotIn("fetch(", html)
        self.assertIn("真正性", html)

    @unittest.skipUnless(shutil.which("node"), "Node runtime is not installed")
    def test_browser_engine_matches_python_contract(self) -> None:
        from scripts import evaluation_dashboard as dashboard
        fixture = ROOT / "tests/fixtures/dashboard/synthetic.v1.json"
        program = r"""
const fs = require('fs');
const html = fs.readFileSync(process.argv[1], 'utf8');
const script = html.match(/<script id="dashboard-runtime">([\s\S]*?)<\/script>/)[1];
eval(script);
const payload = module.exports.parseImport(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(module.exports.summarize(payload)));
"""
        result = subprocess.run(
            ["node", "-e", program, str(ROOT / "docs/evaluation-dashboard.html")],
            input=fixture.read_text(encoding="utf-8"), capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        browser = json.loads(result.stdout)
        python = dashboard.summarize(dashboard.load(fixture))
        for collection in (browser, python):
            for row in collection["runs"]:
                row["cohort"] = json.loads(row["cohort"])
        for js_row, py_row in zip(browser["runs"], python["runs"], strict=True):
            for key in ("q", "b", "s", "rate"):
                if py_row[key] is not None:
                    self.assertAlmostEqual(js_row[key], py_row[key], places=10)
                    js_row[key] = py_row[key]
        self.assertEqual(browser, python)

    def test_import_rejects_contradictory_gate_without_writing_summary(self) -> None:
        payload = json.loads((ROOT / "tests/fixtures/dashboard/synthetic.v1.json").read_text(encoding="utf-8"))
        payload["runs"][0]["cases"][0]["gates"]["permission"] = "fail"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            output = Path(directory) / "summary.json"
            source.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--summary", str(output)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())
            self.assertIn("outcome", result.stderr)

    def test_synthetic_run_preserves_all_assignments_and_gate_counts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "summary.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(ROOT / "tests/fixtures/dashboard/synthetic.v1.json"),
                 "--summary", str(output)], capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(len(summary["runs"]), 4)
            first = summary["runs"][0]
            self.assertEqual(first["assigned"], 6)
            self.assertEqual(first["counts"], dict.fromkeys(
                ["pass", "fail", "hard_fail", "incomplete", "indeterminate", "not_run"], 1))
            self.assertAlmostEqual(first["rate"], 100 / 6)
            self.assertEqual(first["s_count"], 1)
            self.assertEqual(summary["runs"][1]["s"], None)

    def test_empty_export_is_valid_but_not_a_zero_score(self) -> None:
        payload = {
            "schema_version": 1,
            "data_kind": "synthetic",
            "sanitized": True,
            "export_id": "empty-synthetic",
            "generated_at": "2026-10-03T00:00:00Z",
            "methods": [],
            "runs": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            output = Path(directory) / "summary.json"
            source.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--summary", str(output)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(summary["runs"], [])
            self.assertEqual(summary["data_kind"], "synthetic")
            self.assertNotIn("rate", summary)


if __name__ == "__main__":
    unittest.main()
