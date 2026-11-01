"""Acceptance tests use temporary repositories and a deterministic scanner double."""
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/happy-preview/skills/project-protection'
spec = importlib.util.spec_from_file_location('project_protection', SKILL / 'scripts/project_protection.py')
assert spec and spec.loader
protection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protection)


class ProtectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        self.bin = Path(self.temp.name) / 'bin'
        self.bin.mkdir()
        self.scanner = self.bin / 'gitleaks'
        self.scanner.write_text('#!/bin/sh\ncat >/dev/null\nexit "${SCAN_RESULT:-0}"\n')
        self.scanner.chmod(0o755)
        self.env = patch.dict(os.environ, {
            'GIT_CONFIG_GLOBAL': str(Path(self.temp.name) / 'global'),
            'GIT_CONFIG_NOSYSTEM': '1',
            'PATH': str(self.bin) + os.pathsep + os.environ['PATH'],
            'GIT_AUTHOR_NAME': 'Test', 'GIT_AUTHOR_EMAIL': 'test@example.invalid',
            'GIT_COMMITTER_NAME': 'Test', 'GIT_COMMITTER_EMAIL': 'test@example.invalid',
        })
        self.env.start()
        self.addCleanup(self.env.stop)

    def git(self, *args, expected=0):
        result = subprocess.run(['git', '-C', str(self.root), *args], text=True, capture_output=True)
        self.assertEqual(result.returncode, expected, result.stderr)
        return result.stdout.strip()

    def install(self):
        proposal = protection.plan(self.root, True)
        self.assertEqual(proposal['conflicts'], [])
        return protection.apply(self.root, proposal['plan_hash'], True)

    def hook(self, rows, expected=0):
        result = subprocess.run([str(self.root / '.githooks/pre-push')], cwd=self.root,
                                input=rows, text=True, capture_output=True)
        self.assertEqual(result.returncode, expected, result.stderr)

    def commit(self):
        (self.root / 'file').write_text('ordinary content')
        self.git('add', 'file')
        self.git('commit', '-m', 'test')
        return self.git('rev-parse', 'HEAD')

    def test_new_folder_replay_and_read_only_doctor(self):
        self.assertTrue(protection.plan(self.root)['conflicts'])
        self.assertEqual(self.install()['local_configuration'], 'pass')
        self.assertEqual(protection.plan(self.root)['changes'], [])
        before = {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        report = protection.doctor(self.root)
        self.assertEqual(report['remote_protection'], 'remote_not_created')
        self.assertEqual(report['secret_scan'], 'not_run')
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_commit_main_denied_feature_allowed_tool_missing_and_dummy_detection(self):
        self.install()
        (self.root / 'file').write_text('ordinary content')
        self.git('add', 'file')
        self.git('commit', '-m', 'denied', expected=1)
        self.git('switch', '-c', 'feature')
        self.commit()
        self.scanner.unlink()
        self.assertFalse(protection.doctor(self.root)['tools']['gitleaks'])
        self.git('commit', '--allow-empty', '-m', 'missing', expected=1)
        # Synthetic scanner finding, never an actual credential.
        self.scanner.write_text('#!/bin/sh\nexit 1\n')
        self.scanner.chmod(0o755)
        self.git('commit', '--allow-empty', '-m', 'dummy finding', expected=1)

    def test_all_push_destinations_and_deletion(self):
        self.install()
        self.git('switch', '-c', 'feature')
        oid = self.commit()
        zero = '0' * 40
        allowed = f'refs/heads/feature {oid} refs/heads/feature {zero}\n'
        for source in ('refs/heads/feature', 'HEAD', '(delete)'):
            local = zero if source == '(delete)' else oid
            self.hook(f'{source} {local} refs/heads/main {oid}\n', 1)
        self.hook(allowed + f'HEAD {oid} refs/heads/main {zero}\n', 1)
        self.hook(allowed)
        self.hook(f'(delete) {zero} refs/heads/feature {oid}\n')
        self.git('branch', 'main', oid)
        self.git('switch', 'main')
        self.hook(f'HEAD {oid} refs/heads/other {zero}\n')
        with patch.dict(os.environ, {'SCAN_RESULT': '1'}):
            self.hook(allowed, 1)

    def test_conflicts_stale_plan_and_partial(self):
        proposal = protection.plan(self.root, True)
        (self.root / '.githooks').mkdir()
        (self.root / '.githooks/pre-commit').write_text('existing')
        with self.assertRaises(RuntimeError):
            protection.apply(self.root, proposal['plan_hash'], True)
        self.assertFalse((self.root / '.git').exists())
        (self.root / '.githooks/pre-commit').unlink()
        self.install()
        (self.root / '.githooks/pre-push').unlink()
        self.assertEqual(protection.doctor(self.root)['local_configuration'], 'fail')
        proposal = protection.plan(self.root)
        protection.apply(self.root, proposal['plan_hash'])
        (self.root / '.project-protection/guard.py').write_text('modified')
        self.assertTrue(protection.plan(self.root)['conflicts'])

    def test_global_hooks_and_existing_hooks_are_preserved(self):
        self.git('init', '-b', 'main')
        self.git('config', '--global', 'core.hooksPath', '/unmanaged/hooks')
        self.assertTrue(protection.plan(self.root)['conflicts'])
        self.assertEqual(self.git('config', '--global', '--get', 'core.hooksPath'), '/unmanaged/hooks')
        self.git('config', '--global', '--unset', 'core.hooksPath')
        hook = self.root / '.git/hooks/pre-commit'
        hook.write_text('existing')
        self.assertTrue(protection.plan(self.root)['conflicts'])
        self.assertEqual(hook.read_text(), 'existing')

    def test_worktree_clone_and_remote_are_not_assumed_protected(self):
        self.install()
        self.git('switch', '-c', 'feature')
        for name in protection.desired():
            self.git('add', name)
        self.git('commit', '-m', 'assets')
        worktree = Path(self.temp.name) / 'worktree'
        self.git('worktree', 'add', '-b', 'other', str(worktree))
        self.assertEqual(protection.plan(worktree)['conflicts'], [])
        self.assertEqual(protection.doctor(worktree)['local_configuration'], 'pass')
        clone = Path(self.temp.name) / 'clone'
        subprocess.run(['git', 'clone', str(self.root), str(clone)], check=True, capture_output=True)
        self.assertEqual(protection.doctor(clone)['local_configuration'], 'fail')
        proposal = protection.plan(clone)
        protection.apply(clone, proposal['plan_hash'])
        self.assertEqual(protection.doctor(clone)['remote_protection'], 'unverified')

    def test_timeout_is_not_pass(self):
        with patch.object(protection.subprocess, 'run', side_effect=subprocess.TimeoutExpired('git', 10)):
            with self.assertRaises(subprocess.TimeoutExpired):
                protection.doctor(self.root)

    def test_extra_hooks_and_initialization_templates(self):
        hooks = self.root / '.githooks'
        hooks.mkdir()
        extra = hooks / 'post-checkout'
        extra.write_text('#!/bin/sh\nexit 1\n')
        extra.chmod(0o755)
        self.assertTrue(protection.plan(self.root, True)['conflicts'])
        extra.unlink()
        template = Path(self.temp.name) / 'template/hooks'
        template.mkdir(parents=True)
        (template / 'pre-commit').write_text('unmanaged template')
        self.git('config', '--global', 'init.templateDir', str(template.parent))
        self.assertEqual(self.install()['local_configuration'], 'pass')
        self.assertFalse((self.root / '.git/hooks/pre-commit').exists())

    @unittest.skipUnless(os.environ.get('GITLEAKS_TEST_BINARY'), 'optional real Gitleaks integration')
    def test_real_scanner_staged_dummy_and_push_history(self):
        self.scanner.unlink()
        self.scanner.symlink_to(os.environ['GITLEAKS_TEST_BINARY'])
        self.install()
        self.git('switch', '-c', 'feature')
        (self.root / '.gitleaks.toml').write_text(
            "[[rules]]\nid = 'synthetic-test'\ndescription = 'not a real secret'\n"
            "regex = '''PROTECTION_TEST_DUMMY'''\n")
        self.git('add', '.gitleaks.toml')
        self.git('-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'test config')
        baseline = self.commit()
        dummy = self.root / 'dummy'
        dummy.write_text('clean content')
        self.git('add', 'dummy')
        self.git('commit', '-m', 'clean baseline')
        # Worktree-only dummy must not be mistaken for staged content.
        dummy.write_text('PROTECTION_TEST_' + 'DUMMY')
        self.git('commit', '--allow-empty', '-m', 'unstaged dummy allowed')
        self.git('add', 'dummy')
        dummy.write_text('clean content')
        # Staged dummy must be rejected even when the worktree is clean.
        self.git('commit', '-m', 'reject staged dummy', expected=1)
        self.git('-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'dummy middle commit')
        self.git('add', 'dummy')
        self.git('commit', '-m', 'remove dummy from tip')
        oid = self.git('rev-parse', 'HEAD')
        self.hook(f"HEAD {oid} refs/heads/feature {'0' * 40}\n", 1)
        self.hook(f"HEAD {oid} refs/heads/feature {baseline}\n", 1)
        # Scanner configuration errors must fail closed as well.
        (self.root / '.gitleaks.toml').write_text('invalid TOML [')
        self.git('commit', '--allow-empty', '-m', 'scanner error', expected=1)
        self.hook(f"HEAD {oid} refs/heads/feature {baseline}\n", 1)

    def test_remote_url_is_not_printed(self):
        self.install()
        self.git('remote', 'add', 'origin', 'https://dummy-user:synthetic-value@example.invalid/repo')
        report = json.dumps(protection.doctor(self.root))
        self.assertNotIn('synthetic-value', report)
        self.assertNotIn('dummy-user', report)

    def test_first_install_with_multiple_worktrees_stops(self):
        self.git('init', '-b', 'main')
        self.commit()
        linked = Path(self.temp.name) / 'linked'
        self.git('worktree', 'add', '-b', 'linked', str(linked))
        for root in (self.root, linked):
            proposal = protection.plan(root)
            self.assertEqual(len(proposal['detected']['worktrees']), 2)
            self.assertTrue(proposal['conflicts'])
            with self.assertRaises(RuntimeError):
                protection.apply(root, proposal['plan_hash'])
        result = subprocess.run(['git', '-C', str(self.root), 'config', '--get', 'core.hooksPath'])
        self.assertEqual(result.returncode, 1)

    def test_upstream_only_remote_is_unverified(self):
        self.install()
        self.git('remote', 'add', 'upstream', 'https://example.invalid/repo')
        self.assertEqual(protection.doctor(self.root)['remote_protection'], 'unverified')

    def test_external_config_symlink_is_rejected(self):
        self.git('init', '-b', 'main')
        config = self.root / '.git/config'
        external = Path(self.temp.name) / 'external-config'
        original = config.read_bytes()
        external.write_bytes(original)
        config.unlink()
        config.symlink_to(external)
        proposal = protection.plan(self.root)
        self.assertTrue(proposal['conflicts'])
        with self.assertRaises(RuntimeError):
            protection.apply(self.root, proposal['plan_hash'])
        self.assertEqual(external.read_bytes(), original)
        self.assertTrue(config.is_symlink())

    def test_concurrent_config_before_activation_is_preserved(self):
        self.git('init', '-b', 'main')
        proposal = protection.plan(self.root)
        original_open = Path.open
        root = self.root

        def interleaved_open(path, *args, **kwargs):
            if path.name == 'manifest.json' and args == ('xb',):
                subprocess.run(['git', '-C', str(root), 'config', '--local',
                                'core.hooksPath', '/concurrent-hooks'], check=True)
            return original_open(path, *args, **kwargs)

        with patch.object(Path, 'open', interleaved_open):
            with self.assertRaises(RuntimeError):
                protection.apply(self.root, proposal['plan_hash'])
        self.assertEqual(self.git('config', '--get', 'core.hooksPath'), '/concurrent-hooks')
        self.assertFalse((self.root / '.git/config.lock').exists())

    def test_existing_git_config_lock_is_preserved(self):
        self.git('init', '-b', 'main')
        proposal = protection.plan(self.root)
        lock = self.root / '.git/config.lock'
        lock.write_text('another writer')
        original = (self.root / '.git/config').read_bytes()
        with self.assertRaises(FileExistsError):
            protection.apply(self.root, proposal['plan_hash'])
        self.assertEqual(lock.read_text(), 'another writer')
        self.assertEqual((self.root / '.git/config').read_bytes(), original)

    def test_next_git_writer_lock_is_preserved_after_activation(self):
        self.git('init', '-b', 'main')
        proposal = protection.plan(self.root)
        original_replace = os.replace
        lock = self.root / '.git/config.lock'

        def interleaved_replace(source, destination):
            original_replace(source, destination)
            lock.write_text('next writer owns this lock')

        with patch.object(protection.os, 'replace', interleaved_replace):
            protection.apply(self.root, proposal['plan_hash'])
        self.assertEqual(lock.read_text(), 'next writer owns this lock')
        self.assertEqual(self.git('config', '--get', 'core.hooksPath'), '.githooks')

    def test_python_does_not_receive_rust_ci(self):
        (self.root / 'pyproject.toml').write_text('[project]\nname="dummy"\n')
        report = self.install()
        self.assertEqual(report['applicability']['technologies'], ['python'])
        self.assertFalse((self.root / '.github').exists())


if __name__ == '__main__':
    unittest.main()
