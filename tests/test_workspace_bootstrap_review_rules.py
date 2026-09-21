import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WorkspaceBootstrapReviewRulesTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_repo_onboarding_routes_missing_agents_without_writing(self) -> None:
        skill = self.read("plugins/happy-coding/skills/repo-onboarding/SKILL.md")

        self.assertIn("親directoryやhomeの共通指示", skill)
        self.assertIn("対象repo内にrepo管理の`AGENTS.md`がない場合", skill)
        self.assertIn("`workspace-bootstrap`を明示的なhandoff候補", skill)
        self.assertIn("onboarding中には作成しない", skill)

    def test_workspace_bootstrap_preserves_and_deduplicates_instructions(self) -> None:
        skill = self.read("plugins/happy-core/skills/workspace-bootstrap/SKILL.md")

        for expected in (
            "`.github/copilot-instructions.md`",
            "`AGENTS.fragment.md`",
            "全文置換せず",
            "全文を複製せず",
            "重複させず",
            "優先順位と適用範囲",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, skill)

    def test_review_rules_are_optional_and_limited_to_high_impact_constraints(self) -> None:
        skill = self.read("plugins/happy-core/skills/workspace-bootstrap/SKILL.md")
        template = self.read("plugins/happy-core/skills/workspace-bootstrap/assets/AGENTS.md")

        for expected in (
            "## Code Review Rules",
            "重大な誤動作",
            "データ損失",
            "誤った正常終了",
            "一般的なlint／style／テスト推奨は入れない",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, skill if expected != "## Code Review Rules" else template)
        self.assertIn("該当がなければsectionごと省く", template)
        self.assertIn("権限／security境界の破れ", template)


if __name__ == "__main__":
    unittest.main()
