import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ConstitutionContractTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_canonical_documents_publish_distinct_responsibilities(self) -> None:
        constitution = self.read("CONSTITUTION.md")
        summary = self.read("docs/CONSTITUTION_SUMMARY.md")
        profile = self.read("docs/governance/UPSTREAM_DECISION_PROFILE.md")

        for required in (
            "Version: 1.0.0",
            "個人philosophy",
            "通常の運用改善",
            "Constitution amendment",
            "安全・評価整合性",
            "downstream Constitution",
            "3日",
            "7日",
            "10日",
        ):
            with self.subTest(required=required):
                self.assertIn(required, constitution)

        for required in ("通常評価（A）", "判定不能（B）", "緊急例外（C）"):
            with self.subTest(required=required):
                self.assertIn(required, summary)

        for required in ("人→AI", "AI→AI", "人→人", "anchor", "最小差分", "再利用性"):
            with self.subTest(required=required):
                self.assertIn(required, profile)

    def test_sync_record_is_machine_readable_and_reconciled(self) -> None:
        sync_path = ROOT / "docs/governance/constitution-sync.json"
        sync = json.loads(sync_path.read_text(encoding="utf-8"))

        self.assertEqual(sync["schema_version"], 1)
        self.assertEqual(sync["constitution_version"], "1.0.0")
        self.assertRegex(sync["constitution_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(sync["constitution_revision"], r"^[0-9a-f]{40}$")
        self.assertRegex(sync["personal_philosophy"]["revision"], r"^[0-9a-f]{40}$")
        self.assertTrue(sync["personal_philosophy"]["url"].startswith("https://github.com/"))
        self.assertIn(sync["resolution"], {"reflected", "not-applicable", "pending"})
        if sync["resolution"] == "pending":
            self.assertIsNotNone(sync["drift_started_at"])
            self.assertIn(sync["drift_source"], {"personal-philosophy", "constitution", "both"})
        else:
            self.assertIsNone(sync["drift_started_at"])
            self.assertIsNone(sync["drift_source"])
        self.assertTrue(sync["reason"].strip())

    def test_navigation_points_to_the_canonical_constitution(self) -> None:
        for relative_path in ("README.md", "AGENTS.md", "docs/ARCHITECTURE.md"):
            with self.subTest(path=relative_path):
                text = self.read(relative_path)
                self.assertIn("CONSTITUTION.md", text)
                self.assertIn("CONSTITUTION_SUMMARY.md", text)

    def test_behavior_changing_skills_route_to_governance_references(self) -> None:
        skill_eval = self.read("plugins/happy-core/skills/skill-eval/SKILL.md")
        eval_governance = self.read(
            "plugins/happy-core/skills/skill-eval/references/evaluation-governance.md"
        )
        improvement_loop = self.read("plugins/happy-core/skills/improvement-loop/SKILL.md")
        constitution_governance = self.read(
            "plugins/happy-core/skills/improvement-loop/references/constitution-governance.md"
        )

        self.assertIn("evaluation-governance.md", skill_eval)
        for required in (
            "downstream Constitution",
            "通常評価（A）",
            "判定不能（B）",
            "緊急例外（C）",
            "過去record",
            "vNext",
        ):
            with self.subTest(eval_required=required):
                self.assertIn(required, eval_governance)

        self.assertIn("constitution-governance.md", improvement_loop)
        for required in (
            "通常の運用改善",
            "Constitution amendment",
            "3日",
            "7日",
            "10日",
            "remediation",
        ):
            with self.subTest(improvement_required=required):
                self.assertIn(required, constitution_governance)


if __name__ == "__main__":
    unittest.main()
