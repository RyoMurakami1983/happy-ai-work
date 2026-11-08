"""Acceptance tests use temporary repositories and a deterministic scanner double."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/happy-preview/skills/project-protection'
spec = importlib.util.spec_from_file_location('project_protection', SKILL / 'scripts/project_protection.py')
assert spec and spec.loader
protection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protection)


class FixtureWindowsError(PermissionError):
    def __init__(self, code, message):
        super().__init__(message)
        self.winerror = code


def load_guard():
    guard_spec = importlib.util.spec_from_file_location('guard_fixture', SKILL / 'assets/guard.py')
    assert guard_spec and guard_spec.loader
    guard = importlib.util.module_from_spec(guard_spec)
    guard_spec.loader.exec_module(guard)
    return guard


def unlink_exited_executable(path, process):
    """Retry only transient Windows access denial, after a waited/closed probe."""
    if process.poll() is None:
        raise RuntimeError('Scanner process has not exited; cleanup not attempted')
    for attempt in range(20):
        try:
            path.unlink()
            return
        except PermissionError as error:
            if getattr(error, 'winerror', None) != 5 or attempt == 19:
                raise
            time.sleep(0.05)



class ProtectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.cleanup_fixture)
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        self.bin = Path(self.temp.name) / 'bin'
        self.bin.mkdir()
        self.scanner = self.bin / ('gitleaks.exe' if sys.platform == 'win32' else 'gitleaks')
        self.base_python = Path(getattr(sys, '_base_executable', sys.executable))
        self.write_scanner('import os, sys\nsys.exit(int(os.environ.get("SCAN_RESULT", "0")))\n')
        overrides = {
            'GIT_CONFIG_GLOBAL': str(Path(self.temp.name) / 'global'),
            'GIT_CONFIG_NOSYSTEM': '1',
            'PROJECT_PROTECTION_SCAN_TIMEOUT': '60',
            'PATH': os.pathsep.join([str(self.bin), str(self.base_python.parent), os.environ['PATH']]),
            'PYTHONHOME': sys.base_prefix,
            'GIT_AUTHOR_NAME': 'Test', 'GIT_AUTHOR_EMAIL': 'test@example.invalid',
            'GIT_COMMITTER_NAME': 'Test', 'GIT_COMMITTER_EMAIL': 'test@example.invalid',
        }
        self.fixture_env = {**os.environ, **overrides}
        self.fake_scanner = self.scanner
        self.env = patch.dict(os.environ, overrides)
        self.env.start()
        self.addCleanup(self.env.stop)

    def cleanup_fixture(self):
        if sys.platform == 'win32' and self.fake_scanner.exists():
            # Hook commands have returned; explicitly wait for a final native
            # scanner probe and close its handle before the narrow cleanup retry.
            with subprocess.Popen([str(self.fake_scanner), '--version'], env=self.fixture_env,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) as probe:
                try:
                    probe.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    probe.kill()
                    probe.wait(timeout=5)
                    raise
            if probe.returncode != 0:
                raise RuntimeError('Fixture probe failed; native executable cleanup unconfirmed')
            unlink_exited_executable(self.fake_scanner, probe)
        self.temp.cleanup()

    def assert_missing_scanner(self):
        empty = Path(self.temp.name) / 'missing-tools'
        empty.mkdir(exist_ok=True)
        guard = load_guard()
        installed_guard = self.bundle() / 'guard.py'
        # Retain Git for the read-only doctor, isolate only its scanner lookup.
        find = shutil.which
        with patch.object(protection.shutil, 'which',
                          side_effect=lambda name: find(name, path=str(empty)) if name == 'gitleaks' else find(name)):
            self.assertFalse(protection.doctor(self.root)['tools']['gitleaks'])
        with patch.dict(os.environ, {'PATH': str(empty)}), patch.object(guard, 'git', return_value='feature'), \
                patch.object(guard.sys, 'argv', ['guard.py', 'pre-commit']):
            self.assertIsNone(shutil.which('gitleaks'))
            with self.assertRaisesRegex(RuntimeError, 'Gitleaks unavailable'):
                guard.main()
            oid = self.git_oid
            result = subprocess.run([sys.executable, str(installed_guard), 'pre-push'],
                                    cwd=self.root, input=f"HEAD {oid} refs/heads/feature {'0' * 40}\n",
                                    text=True, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            self.assertIn('Gitleaks unavailable', result.stderr)

    def write_scanner(self, body):
        # A native Python executable accepts the first Gitleaks argument "git" as
        # its script. This scanner double works without shebang execution on Windows.
        if not self.scanner.exists():
            if sys.platform == 'win32':
                shutil.copy2(self.base_python, self.scanner)
            else:
                self.scanner.symlink_to(self.base_python)
        (self.root / 'git').write_text(body, encoding='utf-8')

    def git(self, *args, expected=0):
        result = subprocess.run(['git', '-C', str(self.root), *args], text=True, capture_output=True)
        self.assertEqual(result.returncode, expected, result.stderr)
        return result.stdout.strip()

    def install(self):
        proposal = protection.plan(self.root, True)
        self.assertEqual(proposal['conflicts'], [])
        return protection.apply(self.root, proposal['plan_hash'], True)

    def bundle(self, root=None):
        return Path(protection.plan(root or self.root)['trusted_bundle'])

    def hook(self, rows, expected=0):
        result = subprocess.run(['sh', str(self.bundle() / 'hooks/pre-push')], cwd=self.root,
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
        self.assertIn('python' if sys.platform == 'win32' else 'python3', report['tools'])
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_commit_main_denied_feature_allowed_tool_missing_and_dummy_detection(self):
        self.install()
        (self.root / 'file').write_text('ordinary content')
        self.git('add', 'file')
        self.git('commit', '-m', 'denied', expected=1)
        self.git('switch', '-c', 'feature')
        self.git_oid = self.commit()
        self.assert_missing_scanner()
        # Synthetic scanner finding, never an actual credential.
        self.write_scanner('import sys\nsys.exit(1)\n')
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
        self.git('init', '-b', 'main')
        with self.assertRaises(RuntimeError):
            protection.apply(self.root, proposal['plan_hash'], True)
        self.install()
        (self.bundle() / 'hooks/pre-push').unlink()
        self.assertEqual(protection.doctor(self.root)['local_configuration'], 'fail')
        proposal = protection.plan(self.root)
        protection.apply(self.root, proposal['plan_hash'])
        (self.bundle() / 'guard.py').write_text('modified')
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
        self.commit()
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

    def legacy_installation(self):
        self.git('init', '--template=', '-b', 'main')
        files = {'.project-protection/guard.py': (ROOT / 'tests/fixtures/project-protection-v1/guard.py').read_bytes()}
        for mode in ('pre-commit', 'pre-push'):
            files['.githooks/' + mode] = (
                '#!/bin/sh\nif [ "${OS-}" = Windows_NT ]; then\n  runtime=python\nelse\n'
                '  runtime=python3\nfi\n'
                f'exec "$runtime" "$(git rev-parse --show-toplevel)/.project-protection/guard.py" {mode} "$@"\n'
            ).encode()
        files['.project-protection/manifest.json'] = json.dumps(protection.LEGACY_DIGESTS, sort_keys=True).encode()
        for name, content in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            if name.startswith('.githooks/'):
                path.chmod(0o755)
        self.git('config', '--local', 'core.hooksPath', '.githooks')
        return files

    def test_legacy_migration_is_explicit_and_preserves_tracked_assets(self):
        files = self.legacy_installation()
        self.assertTrue(protection.plan(self.root)['conflicts'])
        self.assertEqual(protection.doctor(self.root)['local_configuration'], 'fail')
        proposal = protection.plan(self.root, migrate_legacy=True)
        self.assertEqual(proposal['conflicts'], [])
        with self.assertRaises(RuntimeError):
            protection.apply(self.root, proposal['plan_hash'])
        report = protection.apply(self.root, proposal['plan_hash'], migrate_legacy=True)
        self.assertEqual(report['local_configuration'], 'pass')
        self.assertEqual({name: (self.root / name).read_bytes() for name in files}, files)
        self.assertNotEqual(self.git('config', '--get', 'core.hooksPath'), '.githooks')
        self.git('switch', '-c', 'feature')
        self.commit()

    def test_legacy_migration_rejects_forged_manifest_and_extra_hooks(self):
        files = self.legacy_installation()
        config = (self.root / '.git/config').read_bytes()
        guard = self.root / '.project-protection/guard.py'
        guard.write_text('raise SystemExit(0)\n')
        # Forging the manifest cannot authorize different executable bytes.
        manifest = self.root / '.project-protection/manifest.json'
        forged = dict(protection.LEGACY_DIGESTS)
        forged['.project-protection/guard.py'] = protection.hashlib.sha256(guard.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(forged, sort_keys=True))
        proposal = protection.plan(self.root, migrate_legacy=True)
        self.assertTrue(proposal['conflicts'])
        with self.assertRaises(RuntimeError):
            protection.apply(self.root, proposal['plan_hash'], migrate_legacy=True)
        self.assertEqual((self.root / '.git/config').read_bytes(), config)
        for name, content in files.items():
            (self.root / name).write_bytes(content)
        extra = self.root / '.githooks/post-checkout'
        extra.write_text('#!/bin/sh\ntouch PWNED\n')
        extra.chmod(0o755)
        self.assertTrue(protection.plan(self.root, migrate_legacy=True)['conflicts'])
        self.assertFalse((self.root / 'PWNED').exists())
        self.assertEqual((self.root / '.git/config').read_bytes(), config)

    def test_branch_replacements_and_new_post_checkout_never_execute(self):
        self.install()
        trusted = self.bundle()
        self.git('switch', '-c', 'feature')
        baseline = self.commit()
        self.git('branch', 'clean', baseline)
        for mode in ('pre-commit', 'pre-push', 'post-checkout'):
            path = self.root / '.githooks' / mode
            path.parent.mkdir(exist_ok=True)
            path.write_text('#!/bin/sh\necho ran > PWNED\nexit 0\n')
            path.chmod(0o755)
        guard = self.root / '.project-protection/guard.py'
        guard.parent.mkdir()
        guard.write_text('from pathlib import Path\nPath("PWNED").touch()\n')
        self.git('add', '.githooks', '.project-protection')
        self.git('commit', '-m', 'untrusted tracked replacements')
        self.git('switch', 'clean')
        self.git('switch', 'feature')
        self.assertFalse((self.root / 'PWNED').exists())
        self.git('commit', '--allow-empty', '-m', 'still trusted')
        remote = Path(self.temp.name) / 'bare'
        subprocess.run(['git', 'init', '--bare', '--template=', str(remote)], check=True, capture_output=True)
        self.git('remote', 'add', 'origin', str(remote))
        self.git('push', 'origin', 'HEAD:refs/heads/feature')
        self.git('push', 'origin', 'HEAD:refs/heads/main', expected=1)
        self.git('switch', '-c', 'main')
        self.git('commit', '--allow-empty', '-m', 'main denied', expected=1)
        self.assertFalse((self.root / 'PWNED').exists())
        self.assertEqual(self.bundle(), trusted)
        self.assertEqual(protection.doctor(self.root)['local_configuration'], 'pass')

    def test_linked_worktree_without_assets_keeps_protection(self):
        self.install()
        self.git('switch', '-c', 'feature')
        self.commit()
        linked = Path(self.temp.name) / 'linked space 日本語'
        self.git('worktree', 'add', '-b', 'linked', str(linked))
        shutil.copy2(self.root / 'git', linked / 'git')  # Scanner double, not a protection asset.
        self.assertEqual(self.bundle(linked), self.bundle())
        self.assertFalse((linked / '.project-protection').exists())
        self.assertFalse((linked / '.githooks').exists())
        result = subprocess.run(['git', '-C', str(linked), 'commit', '--allow-empty', '-m', 'linked'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.git('config', 'extensions.worktreeConfig', 'true')
        subprocess.run(['git', '-C', str(linked), 'config', '--worktree', 'core.hooksPath', '.githooks'], check=True)
        self.assertEqual(protection.doctor(linked)['local_configuration'], 'fail')

    def test_trusted_bundle_tampering_and_extra_hook_are_rejected(self):
        self.install()
        for name in ('guard.py', 'manifest.json', 'hooks/pre-commit', 'hooks/post-checkout'):
            with self.subTest(name=name):
                path = self.bundle() / name
                original = path.read_bytes() if path.exists() else None
                path.write_text('unmanaged content')
                proposal = protection.plan(self.root)
                self.assertTrue(proposal['conflicts'])
                self.assertEqual(protection.doctor(self.root)['local_configuration'], 'fail')
                with self.assertRaises(RuntimeError):
                    protection.apply(self.root, proposal['plan_hash'])
                if original is None:
                    path.unlink()
                else:
                    path.write_bytes(original)
        self.assertEqual(protection.doctor(self.root)['local_configuration'], 'pass')

    def test_bundle_symlink_and_windows_junction_detection(self):
        self.git('init', '-b', 'main')
        store = self.bundle().parent
        external = Path(self.temp.name) / 'external'
        external.mkdir()
        store.symlink_to(external, target_is_directory=True)
        proposal = protection.plan(self.root)
        self.assertTrue(proposal['conflicts'])
        with self.assertRaises(RuntimeError):
            protection.apply(self.root, proposal['plan_hash'])
        self.assertEqual(list(external.iterdir()), [])
        store.unlink()
        with patch.object(Path, 'is_junction', lambda path: path == store, create=True):
            self.assertTrue(protection.plan(self.root)['conflicts'])

    def test_asset_change_invalidates_approved_plan(self):
        proposal = protection.plan(self.root, True)
        assets = Path(self.temp.name) / 'assets'
        shutil.copytree(SKILL / 'assets', assets)
        (assets / 'guard.py').write_text('raise SystemExit(0)\n')
        with patch.object(protection, 'ASSETS', assets):
            with self.assertRaises(RuntimeError):
                protection.apply(self.root, proposal['plan_hash'], True)
        self.assertFalse((self.root / '.git').exists())

    def test_inactive_conditional_config_include_is_rejected(self):
        self.git('init', '-b', 'main')
        included = self.root / 'branch-config'
        included.write_text('[core]\n hooksPath = .githooks\n')
        self.git('config', 'includeIf.onbranch:untrusted.path', str(included))
        self.assertTrue(protection.plan(self.root)['conflicts'])
        self.assertIn('includes', ' '.join(protection.plan(self.root)['conflicts']))

    def test_external_git_directory_and_paths_with_spaces(self):
        new_root = self.root.with_name('repo space 日本語')
        self.root.rename(new_root)
        self.root = new_root
        common = Path(self.temp.name) / 'git metadata 日本語'
        self.git('init', '--template=', '-b', 'main', '--separate-git-dir', str(common))
        self.assertEqual(self.install()['local_configuration'], 'pass')
        self.assertTrue(self.bundle().is_relative_to(common))
        self.git('switch', '-c', 'feature')
        self.commit()

    def test_git_directory_inside_trackable_worktree_is_rejected(self):
        self.git('init', '--template=', '-b', 'main', '--separate-git-dir', str(self.root / 'tracked-git'))
        proposal = protection.plan(self.root)
        self.assertIn('trackable worktree', ' '.join(proposal['conflicts']))
        with self.assertRaises(RuntimeError):
            protection.apply(self.root, proposal['plan_hash'])

    def test_python_imports_ignore_checkout_and_pythonpath(self):
        self.install()
        self.git('switch', '-c', 'feature')
        marker = Path(self.temp.name) / 'import-marker'
        for name in ('sitecustomize.py', 'shutil.py', 'subprocess.py'):
            (self.root / name).write_text(f'from pathlib import Path\nPath({str(marker)!r}).touch()\n')
        # main is rejected before the scanner double (a separate Python process).
        self.commit()
        self.git('switch', '-c', 'main')
        with patch.dict(os.environ, {'PYTHONPATH': str(self.root)}):
            self.git('commit', '--allow-empty', '-m', 'main denied', expected=1)
        self.assertFalse(marker.exists())

    def test_executable_search_excludes_checkout_and_relative_path_entries(self):
        guard = load_guard()
        before = Path.cwd()
        try:
            os.chdir(self.root)
            with patch.dict(os.environ, {'PATH': os.pathsep.join([
                '', '.', 'relative-tools', str(self.root), str(self.root / 'bin'), str(self.bin)
            ])}):
                self.assertEqual(guard.trusted_path(), str(self.bin))
                self.assertEqual(Path(guard.trusted_executable('gitleaks')), self.scanner)
        finally:
            os.chdir(before)

    def test_scanner_children_get_explicit_path_without_windows_cwd_search(self):
        guard = load_guard()
        process = Mock()
        process.wait.return_value = 0
        process.__enter__ = Mock(return_value=process)
        process.__exit__ = Mock(return_value=False)
        with patch.object(guard, 'trusted_executable', return_value=str(self.scanner)), \
                patch.object(guard, 'trusted_path', return_value=str(self.bin)), \
                patch.object(guard.subprocess, 'Popen', return_value=process) as popen:
            guard.scan(['git', '--staged'])
        self.assertEqual(popen.call_args.args[0][0], str(self.scanner))
        environment = popen.call_args.kwargs['env']
        self.assertEqual(environment['PATH'], str(self.bin))
        self.assertEqual(environment['NoDefaultCurrentDirectoryInExePath'], '1')

    @unittest.skipUnless(sys.platform == 'win32', 'native Windows executable search regression')
    def test_windows_checkout_executables_cannot_shadow_trusted_tools(self):
        self.install()
        self.git('switch', '-c', 'feature')
        marker = self.root / 'EXECUTED_UNTRUSTED_TOOL'
        for name in ('git.exe', 'gitleaks.exe'):
            shutil.copy2(self.base_python, self.root / name)
        (self.root / 'symbolic-ref').write_text(
            f'from pathlib import Path\nPath({str(marker)!r}).touch()\nprint("feature")\n')
        self.write_scanner(
            'import sys\nfrom pathlib import Path\n'
            f'if Path(sys.executable).parent == Path.cwd(): Path({str(marker)!r}).touch()\n')
        self.git('add', 'git.exe', 'gitleaks.exe', 'symbolic-ref')
        self.git('commit', '-m', 'untrusted native executable fixtures')
        oid = self.git('rev-parse', 'HEAD')
        self.hook(f"HEAD {oid} refs/heads/feature {'0' * 40}\n")
        self.assertFalse(marker.exists())
        before = Path.cwd()
        try:
            os.chdir(self.root)
            self.assertEqual(protection.doctor(self.root)['local_configuration'], 'pass')
            self.assertEqual(protection.plan(self.root)['conflicts'], [])
        finally:
            os.chdir(before)
        self.assertFalse(marker.exists())

    def test_installer_git_lookup_excludes_target_and_current_directory(self):
        external = Path(protection.git_executable(self.root)).resolve()
        before = Path.cwd()
        try:
            os.chdir(self.root)
            with patch.dict(os.environ, {'PATH': os.pathsep.join([
                '', '.', str(self.root), str(external.parent)
            ])}):
                self.assertEqual(Path(protection.git_executable(self.root)).resolve(), external)
        finally:
            os.chdir(before)

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
        self.assertEqual(protection.plan(self.root, True)['conflicts'], [])
        template = Path(self.temp.name) / 'template/hooks'
        template.mkdir(parents=True)
        (template / 'pre-commit').write_text('unmanaged template')
        self.git('config', '--global', 'init.templateDir', str(template.parent))
        self.assertEqual(self.install()['local_configuration'], 'pass')
        self.assertFalse((self.root / '.git/hooks/pre-commit').exists())

    @unittest.skipUnless(os.environ.get('GITLEAKS_TEST_BINARY'), 'optional real Gitleaks integration')
    def test_real_scanner_staged_dummy_and_push_history(self):
        real_bin = Path(self.temp.name) / 'real-scanner'
        real_bin.mkdir()
        self.scanner = real_bin / self.scanner.name
        shutil.copy2(os.environ['GITLEAKS_TEST_BINARY'], self.scanner)
        os.environ['PATH'] = str(real_bin) + os.pathsep + os.environ['PATH']
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
        link = self.root / '.git/config-link'
        try:
            link.symlink_to(external)
        except OSError as error:
            if getattr(error, 'winerror', None) == 1314:
                self.assertEqual(config.read_bytes(), original)
                self.fail('UNVERIFIED real Windows symlink: WinError 1314; privilege unavailable. '
                          'Original config preserved; mock coverage is a separate test, not a pass for this case.')
            raise
        config.unlink()
        link.rename(config)
        proposal = protection.plan(self.root)
        self.assertTrue(proposal['conflicts'])
        with self.assertRaises(RuntimeError):
            protection.apply(self.root, proposal['plan_hash'])
        self.assertEqual(external.read_bytes(), original)
        self.assertTrue(config.is_symlink())

    def test_worktree_config_symlink_cannot_enable_future_branch_hooks(self):
        self.git('init', '-b', 'main')
        self.git('config', 'extensions.worktreeConfig', 'true')
        tracked_config = self.root / 'branch-config'
        tracked_config.write_text('[user]\n name = Test\n')
        (self.root / '.git/config.worktree').symlink_to(tracked_config)
        proposal = protection.plan(self.root)
        self.assertIn('config.worktree', ' '.join(proposal['detected']['config_symlinks']))
        self.assertTrue(proposal['conflicts'])
        with self.assertRaises(RuntimeError):
            protection.apply(self.root, proposal['plan_hash'])
        self.assertEqual(tracked_config.read_text(), '[user]\n name = Test\n')
        self.assertFalse(self.bundle().exists())
        (self.root / '.git/config.worktree').unlink()
        self.install()
        self.git('switch', '-c', 'feature')
        self.commit()
        linked = Path(self.temp.name) / 'linked'
        self.git('worktree', 'add', '-b', 'linked', str(linked))
        linked_config = Path(protection.git(linked, 'rev-parse', '--absolute-git-dir')) / 'config.worktree'
        tracked_config = linked / 'branch-config'
        tracked_config.write_text('[user]\n name = Test\n')
        linked_config.symlink_to(tracked_config)
        report = protection.doctor(linked)
        self.assertEqual(report['local_configuration'], 'fail')
        self.assertIn(str(linked_config), report['applicability']['config_symlinks'])
        self.assertEqual(protection.doctor(self.root)['local_configuration'], 'pass')

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
        self.assertEqual(self.git('config', '--get', 'core.hooksPath'), (self.bundle() / 'hooks').as_posix())

    def test_hanging_scanner_times_out_and_normal_retry_succeeds(self):
        self.install()
        self.git('switch', '-c', 'feature')
        oid = self.commit()
        self.write_scanner(
            'import sys, time\n'
            'print("SYNTHETIC_PRIVATE_OUTPUT", flush=True)\n'
            'print("SYNTHETIC_PRIVATE_ERROR", file=sys.stderr, flush=True)\n'
            'time.sleep(30)\n')
        commit = ['git', '-C', str(self.root), 'commit', '--allow-empty', '-m', 'scan retry']
        push = ['sh', str(self.bundle() / 'hooks/pre-push')]
        rows = f"HEAD {oid} refs/heads/feature {'0' * 40}\n"
        with patch.dict(os.environ, {'PROJECT_PROTECTION_SCAN_TIMEOUT': '1'}):
            for command, stdin in ((commit, None), (push, rows)):
                result = subprocess.run(command, cwd=self.root, input=stdin, text=True,
                                        capture_output=True, timeout=8)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn('timed out after 1s', result.stderr)
                self.assertIn('scan incomplete', result.stderr)
                self.assertIn('PROJECT_PROTECTION_SCAN_TIMEOUT=300', result.stderr)
                self.assertNotIn('SYNTHETIC_PRIVATE', result.stdout + result.stderr)
            self.write_scanner('import sys\nsys.exit(0)\n')
            # A successful retry is allowed; timeout does not leave a permanent block.
            self.git('commit', '--allow-empty', '-m', 'successful retry')
            self.hook(rows)

    def test_scan_timeout_default_bounds_and_invalid_values(self):
        guard_spec = importlib.util.spec_from_file_location('protection_guard', SKILL / 'assets/guard.py')
        assert guard_spec and guard_spec.loader
        guard = importlib.util.module_from_spec(guard_spec)
        guard_spec.loader.exec_module(guard)
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(guard.scan_timeout(), 60)
        for raw in ('0', '-1', '601', 'infinite', '0.5', ''):
            with self.subTest(raw=raw), patch.dict(os.environ, {'PROJECT_PROTECTION_SCAN_TIMEOUT': raw}):
                with self.assertRaises(RuntimeError) as error:
                    guard.scan_timeout()
                if raw == 'infinite':
                    self.assertNotIn(raw, str(error.exception))
        with patch.dict(os.environ, {'PROJECT_PROTECTION_SCAN_TIMEOUT': '600'}):
            self.assertEqual(guard.scan_timeout(), 600)

    def test_noncanonical_root_is_normalized_without_allowing_nested_targets(self):
        self.git('init', '-b', 'main')
        holder = self.root.parent / 'holder'
        holder.mkdir()
        alias = holder / '..' / self.root.name
        canonical = self.root.resolve()
        self.assertEqual(protection.plan(alias), protection.plan(canonical))
        proposal = protection.plan(alias)
        self.assertEqual(protection.apply(alias, proposal['plan_hash'])['local_configuration'], 'pass')
        self.assertEqual(protection.doctor(alias)['target'], str(canonical))
        nested = self.root / 'nested'
        nested.mkdir()
        with self.assertRaisesRegex(RuntimeError, 'repository root'):
            protection.plan(nested)

    def test_windows_termination_keeps_timeout_failure_and_uses_fallback(self):
        guard_spec = importlib.util.spec_from_file_location('guard_windows_test', SKILL / 'assets/guard.py')
        assert guard_spec and guard_spec.loader
        guard = importlib.util.module_from_spec(guard_spec)
        guard_spec.loader.exec_module(guard)
        process = Mock()
        process.pid = 12345
        process.poll.return_value = None
        with patch.object(guard.sys, 'platform', 'win32'), patch.object(guard.subprocess, 'run') as run, \
                patch.object(guard, 'trusted_executable', return_value='C:/Windows/System32/taskkill.exe'):
            run.side_effect = subprocess.TimeoutExpired('taskkill', 10)
            guard.stop_scanner(process)
        process.kill.assert_called_once()
        process.wait.assert_called_once_with(timeout=10)
        self.assertEqual(run.call_args.args[0], ['C:/Windows/System32/taskkill.exe', '/PID', '12345', '/T', '/F'])
        self.assertEqual(run.call_args.kwargs['stdout'], subprocess.DEVNULL)
        self.assertEqual(run.call_args.kwargs['stderr'], subprocess.DEVNULL)

    def test_missing_scanner_isolated_even_with_ambient_scanner_on_path(self):
        self.install()
        self.git('switch', '-c', 'feature')
        self.git_oid = self.commit()
        ambient = Path(self.temp.name) / 'ambient-tools'
        ambient.mkdir()
        candidate = ambient / self.scanner.name
        shutil.copy2(self.base_python, candidate)
        with patch.dict(os.environ, {'PATH': str(ambient) + os.pathsep + os.environ['PATH']}):
            found = shutil.which('gitleaks')
            assert found is not None
            self.assertEqual(Path(found).resolve(), candidate.resolve())
            self.assert_missing_scanner()
        self.assertTrue(self.fake_scanner.exists())
        self.assertTrue(candidate.exists())

    def test_config_symlink_detection_mock_without_creation_privilege(self):
        self.git('init', '-b', 'main')
        config = (self.root / '.git/config').resolve()
        original = config.read_bytes()
        real_is_symlink = Path.is_symlink
        with patch.object(Path, 'is_symlink', lambda path: path == config or real_is_symlink(path)):
            proposal = protection.plan(self.root)
            self.assertTrue(any('symlink' in conflict for conflict in proposal['conflicts']))
            with self.assertRaises(RuntimeError):
                protection.apply(self.root, proposal['plan_hash'])
        self.assertEqual(config.read_bytes(), original)
        self.assertFalse(config.is_symlink())

    def test_real_symlink_privilege_failure_is_not_reported_as_pass(self):
        denied = FixtureWindowsError(1314, 'synthetic privilege failure')
        with patch.object(Path, 'symlink_to', side_effect=denied):
            with self.assertRaisesRegex(AssertionError, 'UNVERIFIED real Windows symlink.*1314'):
                self.test_external_config_symlink_is_rejected()
        self.assertTrue((self.root / '.git/config').is_file())
        self.assertFalse((self.root / '.git/config').is_symlink())

    def test_executable_cleanup_retries_only_exited_winerror5_with_short_bound(self):
        exited = Mock()
        exited.poll.return_value = 0
        transient = FixtureWindowsError(5, 'synthetic transient access denial')
        path = Mock()
        path.unlink.side_effect = [transient, None]
        with patch.object(time, 'sleep') as sleep:
            unlink_exited_executable(path, exited)
        self.assertEqual(path.unlink.call_count, 2)
        sleep.assert_called_once_with(0.05)
        path.reset_mock()
        path.unlink.side_effect = transient
        with patch.object(time, 'sleep') as sleep:
            with self.assertRaises(PermissionError):
                unlink_exited_executable(path, exited)
        self.assertEqual(path.unlink.call_count, 20)
        self.assertEqual(sleep.call_count, 19)
        other = FixtureWindowsError(32, 'different failure')
        path.reset_mock()
        path.unlink.side_effect = other
        with patch.object(time, 'sleep') as sleep:
            with self.assertRaises(PermissionError):
                unlink_exited_executable(path, exited)
        self.assertEqual(path.unlink.call_count, 1)
        sleep.assert_not_called()
        path.reset_mock()
        exited.poll.return_value = None
        with self.assertRaisesRegex(RuntimeError, 'has not exited'):
            unlink_exited_executable(path, exited)
        path.unlink.assert_not_called()

    def test_python_does_not_receive_rust_ci(self):
        (self.root / 'pyproject.toml').write_text('[project]\nname="dummy"\n')
        report = self.install()
        self.assertEqual(report['applicability']['technologies'], ['python'])
        self.assertFalse((self.root / '.github').exists())


if __name__ == '__main__':
    unittest.main()
