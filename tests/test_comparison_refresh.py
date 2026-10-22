"""Current preparation is distinct from the preserved, unexecuted legacy pilot."""

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from scripts.comparison_bundle import prepare_bundle

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / 'evals/openai-first-implement'
REVISION = '1854315e78454f1f3b98ad9f9ea9ce2217cbf013'


class ComparisonRefreshTests(unittest.TestCase):
    def test_default_prepares_current_baseline_without_retired_plan_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'actor'
            result = prepare_bundle(ROOT, 'baseline', 'small-fix-normal', target)
            self.assertEqual(result['baseline_revision'], REVISION)
            self.assertEqual(result['suite_id'], 'current-v2')
            self.assertFalse(result['comparison_ready'])
            self.assertFalse(result['trial_authorized'])
            self.assertFalse(result['isolation_verified'])
            installed = target / '.agents/skills/implement'
            self.assertEqual((installed / 'SKILL.md').read_bytes(),
                             (SUITE / 'snapshots/current-v2/baseline/implement/SKILL.md').read_bytes())
            self.assertTrue((installed / 'references/planning.md').is_file())
            self.assertFalse((target / '.agents/skills/implementation-plan').exists())
            self.assertFalse(list(target.rglob('cases.v*.json')))
            self.assertFalse(list(target.rglob('provenance.json')))

    def test_current_candidate_fails_before_creating_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'actor'
            with self.assertRaisesRegex(ValueError, 'candidate.*not prepared'):
                prepare_bundle(ROOT, 'candidate', 'small-fix-normal', target)
            self.assertFalse(target.exists())

    def test_legacy_inputs_remain_byte_identical(self):
        inventory = json.loads((SUITE / 'snapshots/legacy-v1.inventory.json').read_text(encoding='utf-8'))
        self.assertEqual(inventory['source_revision'], '98056c63bee21f6170657da244634e0b3961f126')
        for name, digest in inventory['files'].items():
            with self.subTest(path=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)

    def test_current_snapshot_inventory_and_hashes_are_complete(self):
        manifest = json.loads((SUITE / 'snapshots/current-v2/preparation.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['baseline_revision'], REVISION)
        self.assertEqual(set(manifest['conditions']), {'baseline'})
        entries = manifest['conditions']['baseline']
        base = SUITE / 'snapshots/current-v2/baseline'
        actual = {p.relative_to(ROOT).as_posix() for p in base.rglob('*')
                  if p.is_file() and '__pycache__' not in p.parts}
        self.assertEqual(actual, {entry['source'] for entry in entries.values()})
        for spec in entries.values():
            self.assertEqual(hashlib.sha256((ROOT / spec['source']).read_bytes()).hexdigest(), spec['sha256'])

    def test_current_all_cases_and_explicit_legacy_are_separate(self):
        manifest = json.loads((SUITE / 'preparation.v1.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            for case_id in manifest['tasks']:
                result = prepare_bundle(ROOT, 'baseline', case_id, Path(tmp) / case_id)
                self.assertEqual(result['suite_id'], 'current-v2')
            old = prepare_bundle(ROOT, 'candidate', 'small-fix-normal', Path(tmp) / 'legacy',
                                 suite_id='legacy-v1')
            self.assertEqual(old['baseline_revision'], manifest['baseline_revision'])
            self.assertEqual(old['suite_id'], 'legacy-v1')
            self.assertFalse(old['comparison_ready'])

    def test_unknown_suite_and_cli_candidate_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'actor'
            with self.assertRaises(ValueError):
                prepare_bundle(ROOT, 'baseline', 'small-fix-normal', target, suite_id='../legacy-v1')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/comparison_bundle.py'),
                                     'candidate', 'small-fix-normal', str(target)],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 2)
            self.assertIn('not prepared', result.stderr)
            self.assertFalse(target.exists())

    def test_current_hash_and_cross_suite_sources_fail_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            repository = Path(tmp) / 'repository'
            suite = repository / SUITE.relative_to(ROOT)
            shutil.copytree(SUITE, suite)
            manifest_path = suite / 'snapshots/current-v2/preparation.json'
            original = json.loads(manifest_path.read_text(encoding='utf-8'))
            key = '.agents/skills/implement/SKILL.md'
            for source, digest in [
                (original['conditions']['baseline'][key]['source'], '0' * 64),
                ('evals/openai-first-implement/candidate/implement/SKILL.md',
                 hashlib.sha256((SUITE / 'candidate/implement/SKILL.md').read_bytes()).hexdigest()),
            ]:
                with self.subTest(source=source):
                    manifest = json.loads(json.dumps(original))
                    manifest['conditions']['baseline'][key] = {'source': source, 'sha256': digest}
                    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
                    target = Path(tmp) / 'actor'
                    with self.assertRaises(ValueError):
                        prepare_bundle(repository, 'baseline', 'small-fix-normal', target)
                    self.assertFalse(target.exists())

    def test_current_existing_destination_and_repo_destination_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileExistsError):
                prepare_bundle(ROOT, 'baseline', 'small-fix-normal', Path(tmp))
        with self.assertRaisesRegex(ValueError, 'outside'):
            prepare_bundle(ROOT, 'baseline', 'small-fix-normal', ROOT / 'actor-not-created')

    def test_installed_current_relative_links_and_support_entrypoints(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'actor'
            prepare_bundle(ROOT, 'baseline', 'small-fix-normal', target)
            skills = target / '.agents/skills'
            for path in skills.rglob('*.md'):
                for link in re.findall(r"\[[^]]+\]\(([^)]+)\)", path.read_text(encoding='utf-8')):
                    parsed = urlsplit(link)
                    if parsed.scheme or parsed.netloc or not parsed.path:
                        continue
                    dependency = (path.parent / unquote(parsed.path)).resolve()
                    with self.subTest(path=path.relative_to(skills), link=link):
                        self.assertTrue(dependency.is_relative_to(skills.resolve()))
                        self.assertTrue(dependency.is_file())
            self.assertEqual([p.relative_to(skills).as_posix() for p in skills.rglob('SKILL.md')],
                             ['implement/SKILL.md'])
