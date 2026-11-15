"""Placement and optional developer tooling contracts, without semantic evaluation claims."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SkillPlacementTests(unittest.TestCase):
    def test_inventory_has_one_owner(self):
        owners = {}
        for p in ROOT.glob('plugins/*/skills/*/SKILL.md'):
            self.assertNotIn(p.parent.name, owners)
            owners[p.parent.name] = p.parts[-4]
        for name in ('happy-add-issue', 'improvement-loop', 'skill-eval', 'furikaeri'):
            self.assertEqual(owners[name], 'happy-improvement')
        self.assertEqual(owners['workspace-bootstrap'], 'happy-coding')
        self.assertEqual(owners['github-issue'], 'happy-coding')
        for name in ('home-bootstrap', 'yohaku', 'kime-zanshin', 'iwakan-to-omoi',
                     'mokuteki-to-michi', 'sennosen-to-gonosen'):
            self.assertEqual(owners[name], 'happy-core')

    def test_developer_plugin_is_opt_in_not_normal_install(self):
        entries = json.loads((ROOT / '.agents/plugins/marketplace.json').read_text(encoding="utf-8"))['plugins']
        entry = next(e for e in entries if e['name'] == 'happy-improvement')
        self.assertEqual(entry['policy']['installation'], 'AVAILABLE')
        readme = (ROOT / 'README.md').read_text(encoding="utf-8")
        normal = readme.split('### happy-core')[0]
        self.assertNotIn('codex plugin add happy-improvement', normal)

    def test_coding_without_developer_plugin_has_no_install_wait(self):
        # Static availability contract, not an installed Codex execution test.
        for name in ('implement', 'technical-design'):
            body = (ROOT / 'plugins/happy-coding/skills' / name / 'SKILL.md').read_text(encoding="utf-8")
            self.assertIn('`happy-improvement`の`happy-add-issue`', body)
            self.assertIn('`happy-add-issue`が未導入', body)
            self.assertIn('追加確認・導入待ちを増やさず元の作業を閉じる', body)

    def test_sennosen_identifier_migration(self):
        old = 'sen-no-sen-to-go-no-sen'
        new = 'sennosen-to-gonosen'
        for plugin in (ROOT / 'plugins').iterdir():
            self.assertFalse((plugin / 'skills' / old).exists())
        skill = ROOT / 'plugins/happy-core/skills' / new
        self.assertIn(f'name: {new}', (skill / 'SKILL.md').read_text(encoding="utf-8"))
        self.assertIn(f'${new}', (skill / 'agents/openai.yaml').read_text(encoding="utf-8"))
        for path in (ROOT / 'plugins').rglob('*'):
            if path.suffix in ('.md', '.yaml', '.json'):
                self.assertNotIn(old, path.read_text(encoding="utf-8"), str(path))
        self.assertNotIn(old, (ROOT / 'README.md').read_text(encoding="utf-8"))
