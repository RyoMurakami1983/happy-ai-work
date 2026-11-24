"""Structural migration checks; these do not claim model behavioral compliance."""

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class IntegratedPlanningDistributionTests(unittest.TestCase):
    def test_retired_skill_is_outside_plugin_discovery(self) -> None:
        active = list((ROOT / "plugins").glob("*/skills/implementation-plan/SKILL.md"))
        self.assertEqual(active, [])
        archive = ROOT / "archive/implementation-plan"
        self.assertFalse((archive / "SKILL.md").exists())
        manifest = json.loads((archive / "snapshot.json").read_text(encoding="utf-8"))
        for relative, expected in manifest["sha256"].items():
            with self.subTest(artifact=relative):
                self.assertEqual(hashlib.sha256((archive / relative).read_bytes()).hexdigest(), expected)

    def test_renderer_and_template_match_relocated_assets(self) -> None:
        archive = ROOT / "archive/implementation-plan"
        current = ROOT / "plugins/happy-coding/skills/implement"
        for relative in ("scripts/render_plan.py", "assets/plan.html"):
            with self.subTest(artifact=relative):
                self.assertEqual((current / relative).read_bytes(), (archive / relative).read_bytes())

    def test_distributed_plan_example_matches_its_sources(self) -> None:
        current = ROOT / "plugins/happy-coding/skills/implement"
        example = current / "assets/example"
        result = subprocess.run(
            [
                sys.executable,
                str(current / "scripts/render_plan.py"),
                str(example / "003_presentation.json"),
                "--output",
                str(example / "003_plan/003_PLAN.html"),
                "--check",
            ],
            capture_output=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
