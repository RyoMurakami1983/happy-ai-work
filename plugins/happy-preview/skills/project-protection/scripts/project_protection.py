"""Detect, plan, explicitly apply, and diagnose local project protection."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / 'assets'


def git(root: Path, *args: str) -> str:
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True,
                            text=True, timeout=10)
    if result.returncode:
        raise RuntimeError('Git inspection failed: ' + ' '.join(args))
    return result.stdout.strip()


def inventory(root: Path) -> dict:
    repository = subprocess.run(['git', '-C', str(root), 'rev-parse', '--show-toplevel'],
                                capture_output=True, text=True, timeout=10)
    is_repo = repository.returncode == 0
    if is_repo and Path(repository.stdout.strip()).resolve() != root:
        raise RuntimeError('Target must be the repository root, not a nested folder')
    config = subprocess.run(['git', '-C', str(root), 'config', '--show-origin', '--get-all',
                             'core.hooksPath'], capture_output=True, text=True, timeout=10)
    if config.returncode not in (0, 1):
        raise RuntimeError('Cannot inspect hooksPath')
    result = {'repository': is_repo, 'hooks_config': config.stdout.strip(),
              'hooks_path': git(root, 'config', '--get', 'core.hooksPath') if config.returncode == 0 else None,
              'remotes': git(root, 'remote').splitlines() if is_repo else [],
              'technologies': [label for file, label in [('package.json', 'typescript'),
                               ('Cargo.toml', 'rust'), ('pyproject.toml', 'python')]
                               if (root / file).exists()]}
    result['legacy_hooks'] = []
    result['worktrees'] = []
    result['common_directory'] = None
    result['config_symlinks'] = []
    if is_repo:
        common = git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir')
        result['common_directory'] = common
        config_path = Path(common) / 'config'
        result['config_symlinks'] = [str(p) for p in (config_path, *config_path.parents) if p.is_symlink()]
        result['worktrees'] = [entry.removeprefix('worktree ') for entry in
                               git(root, 'worktree', 'list', '--porcelain', '-z').split('\0')
                               if entry.startswith('worktree ')]
        directory = Path(common) / 'hooks'
        result['legacy_hooks'] = sorted(
            p.name for p in directory.iterdir()
            if (p.is_file() or p.is_symlink()) and not p.name.endswith('.sample')
        ) if directory.exists() else []
    return result


def desired() -> dict[str, bytes]:
    files = {'.project-protection/guard.py': (ASSETS / 'guard.py').read_bytes(),
            '.githooks/pre-commit': (ASSETS / 'hooks/pre-commit').read_bytes(),
            '.githooks/pre-push': (ASSETS / 'hooks/pre-push').read_bytes()}
    files['.project-protection/manifest.json'] = json.dumps(
        {name: hashlib.sha256(content).hexdigest() for name, content in files.items()},
        sort_keys=True).encode()
    return files


def plan(root: Path, initialize: bool = False) -> dict:
    state = inventory(root)
    conflicts = []
    changes = []
    if not state['repository'] and not initialize:
        conflicts.append('not a repository: explicit --init required')
    if state['config_symlinks']:
        conflicts.append('Git config or ancestor is a symlink: reconcile manually')
    config = state['hooks_config']
    if not config and len(state['worktrees']) > 1:
        conflicts.append('first installation would change shared worktree configuration: reconcile manually')
    local_config = subprocess.run(
        ['git', '-C', str(root), 'config', '--local', '--show-origin', '--get-all', 'core.hooksPath'],
        capture_output=True, text=True, timeout=10).stdout.strip() if state['repository'] else ''
    owned = (root / '.project-protection/manifest.json').is_file()
    if not owned and any((root / name).exists() for name in desired()):
        conflicts.append('partial or unmanaged installation: manifest missing')
    # A managed local setting is the only permitted existing override. Global or
    # worktree settings (even equal values) require manual reconciliation.
    if config and (state['hooks_path'] != '.githooks' or len(config.splitlines()) != 1
                   or config != local_config or not owned):
        conflicts.append('existing hooksPath: reconcile manually')
    if state['legacy_hooks']:
        conflicts.append('existing Git hooks: reconcile manually')
    hooks = root / '.githooks'
    if hooks.is_dir():
        extras = sorted(p.name for p in hooks.iterdir() if p.name not in ('pre-commit', 'pre-push'))
        if extras:
            conflicts.append('unmanaged destination hooks: ' + ', '.join(extras))
    for name, content in desired().items():
        path = root / name
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != root.parent):
            conflicts.append(name + ': symlink')
        elif path.exists():
            if not path.is_file() or path.read_bytes() != content:
                conflicts.append(name + ': unmanaged or modified content')
            elif name.startswith('.githooks/') and not os.access(path, os.X_OK):
                conflicts.append(name + ': not executable')
        else:
            changes.append({'path': name, 'content': content.decode()})
    if not state['repository']:
        changes.insert(0, {'operation': 'git init --template= -b main (do not copy template hooks)'})
    if not config:
        changes.append({'operation': 'git config --local core.hooksPath .githooks'})
    body = {'target': str(root), 'detected': state, 'changes': changes, 'conflicts': conflicts}
    body['plan_hash'] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    return body


def activate_hooks(root: Path, expected: dict) -> None:
    """Use Git's config lock protocol; never replace a concurrent setting."""
    config = Path(expected['common_directory']) / 'config'
    lock = config.with_name('config.lock')
    if any(p.is_symlink() for p in (config, *config.parents)):
        raise RuntimeError('Git config or ancestor became a symlink')
    # Exclusive creation also rejects an existing symlink or another Git writer.
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    owned_identity = (os.fstat(descriptor).st_dev, os.fstat(descriptor).st_ino)
    consumed = False
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            original = config.read_bytes()
            stream.write(original)
        current = inventory(root)
        if current != expected:
            raise RuntimeError('Git state changed during apply; configuration preserved')
        remaining = plan(root)
        if remaining['conflicts'] or any('path' in change for change in remaining['changes']):
            raise RuntimeError('Assets changed during apply; configuration preserved')
        git(root, 'config', '--file', str(lock), 'core.hooksPath', '.githooks')
        owned_identity = (lock.lstat().st_dev, lock.lstat().st_ino)
        if any(p.is_symlink() for p in (config, *config.parents)) or config.read_bytes() != original:
            raise RuntimeError('Git config changed during apply; configuration preserved')
        lock.chmod(config.stat().st_mode & 0o777)
        os.replace(lock, config)
        consumed = True
    finally:
        if not consumed:
            try:
                remaining = lock.lstat()
            except FileNotFoundError:
                pass
            else:
                if (remaining.st_dev, remaining.st_ino) == owned_identity:
                    lock.unlink()


def apply(root: Path, approved_hash: str, initialize: bool = False) -> dict:
    proposal = plan(root, initialize)
    if proposal['conflicts'] or proposal['plan_hash'] != approved_hash:
        raise RuntimeError('Conflicting or changed plan; inspect and approve a fresh plan')
    if not proposal['detected']['repository']:
        git(root, 'init', '--template=', '-b', 'main')
    expected = inventory(root) if not proposal['detected']['repository'] else proposal['detected']
    for change in proposal['changes']:
        if 'path' in change:
            path = root / change['path']
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(change['content'].encode())
            if change['path'].startswith('.githooks/'):
                path.chmod(0o755)
    if not proposal['detected']['hooks_config']:
        activate_hooks(root, expected)
    return doctor(root)


def doctor(root: Path) -> dict:
    proposal = plan(root)
    tools = {'python3': bool(shutil.which('python3')), 'gitleaks': bool(shutil.which('gitleaks'))}
    return {'target': str(root), 'applicability': proposal['detected'],
            'local_configuration': 'pass' if not proposal['changes'] and not proposal['conflicts'] else 'fail',
            'conflicts': proposal['conflicts'],
            'missing_files': [x['path'] for x in proposal['changes'] if 'path' in x],
            'tools': tools, 'secret_scan': 'not_run',
            'local_validation': 'not_run',
            'remote_protection': 'unverified' if proposal['detected']['remotes'] else 'remote_not_created'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan', 'bootstrap', 'doctor'])
    parser.add_argument('target', type=Path)
    parser.add_argument('--init', action='store_true', help='Include git init for a local folder')
    parser.add_argument('--apply', metavar='PLAN_HASH', help='Apply this reviewed plan only')
    args = parser.parse_args()
    root = args.target.resolve()
    try:
        if args.command == 'doctor':
            if args.apply or args.init:
                parser.error('doctor is read-only')
            result = doctor(root)
        elif args.apply:
            result = apply(root, args.apply, args.init)
        else:
            result = plan(root, args.init)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as error:
        print(json.dumps({'status': 'unverified', 'reason': str(error)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
