import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WorkArtifactPolicyTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_work_artifacts_define_saved_by_default_policy(self) -> None:
        policy = self.read(
            "plugins/happy-coding/skills/implementation-plan/references/WORK_ARTIFACTS.md"
        )

        self.assertIn("saved-by-default", policy)
        self.assertIn("conversation-only exceptions", policy)
        self.assertIn("small one-slice", policy)
        self.assertIn("multi-repo", policy)
        self.assertIn("public contract", policy)
        self.assertIn("migration / operations", policy)
        self.assertIn("exception reason", policy)

    def test_each_artifact_skill_requires_its_canonical_path(self) -> None:
        required_paths = {
            "plugins/happy-coding/skills/interview-with-docs/SKILL.md": (
                "docs/grill_results/NNN_GRILL_WITH_DOCS_RESULT.md"
            ),
            "plugins/happy-coding/skills/to-prd/SKILL.md": "docs/prd/NNN_PRD.md",
            "plugins/happy-coding/skills/technical-design/SKILL.md": (
                "docs/design/NNN_TECHNICAL_DESIGN.md"
            ),
            "plugins/happy-coding/skills/implementation-plan/SKILL.md": (
                "docs/plan/NNN_PLAN.md"
            ),
        }

        for skill_path, artifact_path in required_paths.items():
            with self.subTest(skill=skill_path):
                skill = self.read(skill_path)
                self.assertIn(artifact_path, skill)
                self.assertIn("saved-by-default", skill)

    def test_design_skills_define_adr_decision_conditions(self) -> None:
        for skill_path in (
            "plugins/happy-coding/skills/domain-modeling/SKILL.md",
            "plugins/happy-coding/skills/technical-design/SKILL.md",
        ):
            with self.subTest(skill=skill_path):
                skill = self.read(skill_path)
                self.assertIn("long-lived structure", skill)
                self.assertIn("compatibility", skill)
                self.assertIn("migration", skill)
                self.assertIn("operations", skill)
                self.assertIn("ADR", skill)

    def test_skill_eval_covers_exception_and_required_save_cases(self) -> None:
        scenarios = self.read(
            "plugins/happy-core/skills/skill-eval/references/prompt-evaluation.md"
        )

        self.assertIn("small one-slice", scenarios)
        self.assertIn("artifact save required", scenarios)
        self.assertIn("conversation-only", scenarios)


if __name__ == "__main__":
    unittest.main()
