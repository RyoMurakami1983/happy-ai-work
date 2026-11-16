import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WorkspaceBootstrapReviewRulesTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_repo_onboarding_routes_missing_agents_without_writing(self) -> None:
        skill = self.read("plugins/happy-coding/skills/repo-onboarding/SKILL.md")

        self.assertIn("親／home指示があっても", skill)
        self.assertIn(
            "各directoryのinstruction chainは`AGENTS.override.md`→`AGENTS.md`→"
            "`project_doc_fallback_filenames`の設定済みfallbackの順で解決する",
            skill,
        )
        self.assertIn("repo内にrepo管理の有効な`AGENTS.override.md`・`AGENTS.md`・設定済みfallbackがなければ", skill)
        self.assertIn("導入価値があり`workspace-bootstrap`が使えればhandoff候補にし", skill)
        self.assertIn("使えなければ必要性と専用機能の利用不可を伝える", skill)
        self.assertIn("handoff候補にし", skill)
        self.assertIn("どちらでもonboarding中は作成しない", skill)

    def test_workspace_bootstrap_preserves_and_deduplicates_instructions(self) -> None:
        skill = self.read("plugins/happy-coding/skills/workspace-bootstrap/SKILL.md")

        for expected in (
            "`.github/copilot-instructions.md`",
            "`.github/instructions/*.instructions.md`",
            "instruction chainを`AGENTS.override.md`→`AGENTS.md`→設定済み`project_doc_fallback_filenames`で解決する",
            "overrideが有効なら隠れるAGENTSを新設提案しない",
            "override廃止",
            "通常AGENTS移行",
            "fallbackが有効なら新AGENTSのshadow影響",
            "fallback制約を保つ統合差分",
            "fallback移行は別変更として明示承認を得る",
            "`applyTo`の範囲をrootへ一般化せず",
            "最寄りAGENTSまたはscope明示指示で保つ",
            "`AGENTS.fragment.md`",
            "有効な既存指示の構造・管理内容を保ち、全文置換しない",
            "Copilot指示は全文複製せず",
            "重複させず",
            "矛盾は優先順位・scopeを確認して解消する",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, skill)

    def test_review_rules_are_optional_and_limited_to_high_impact_constraints(self) -> None:
        skill = self.read("plugins/happy-coding/skills/workspace-bootstrap/SKILL.md")
        template = self.read("plugins/happy-coding/skills/workspace-bootstrap/assets/AGENTS.md")

        for expected in (
            "## Code Review Rules",
            "採用済みAcceptance Criteria",
            "外部contract",
            "安全invariant",
            "重大誤動作",
            "data損失",
            "誤正常終了",
            "実装・CI・事故記録は必要性とscopeの証拠",
            "一時workaround・検討過程・非採用挙動を恒久化しない",
            "一般lint／style／test推奨は入れない",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, skill if expected != "## Code Review Rules" else template)
        self.assertIn("該当がなければsectionごと省く", template)
        self.assertIn("権限／security境界の破れ", template)


if __name__ == "__main__":
    unittest.main()
