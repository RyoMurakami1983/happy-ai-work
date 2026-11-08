"""Detect, plan, explicitly apply, and diagnose local project protection."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
# Pinned to the shipped v1 assets (PR #67); a checkout's manifest is not authority.
LEGACY_DIGESTS = {
    '.project-protection/guard.py': '0ed835a84f1b26fd292a91b933d0af838402dde046a71a657fdaf8953fe5db41',
    '.githooks/pre-commit': '31e30f88c46a47c6cae48af643f78cc25031f87b3ca3873bf34bcc86159b7a0a',
    '.githooks/pre-push': '411de5bf810cbc5b7561a5bc2326e8d3bc064dad17f1d8daf05aa9d4f4780fe7',
}


def linked(path: Path) -> bool:
    return path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction())


def linked_ancestor(path: Path) -> bool:
    return any(linked(p) for p in (path, *path.parents))


def git_executable(root: Path) -> str:
    """Keep even read-only diagnosis from executing a checkout's Windows git.exe."""
    excluded = (root.resolve(), Path.cwd().resolve())
    suffixes = ('.exe', '.com') if sys.platform == 'win32' else ('',)
    for entry in os.get_exec_path():
        directory = Path(entry)
        if not directory.is_absolute() or any(directory.resolve().is_relative_to(path) for path in excluded):
            continue
        for suffix in suffixes:
            candidate = directory / ('git' + suffix)
            if candidate.is_file() and os.access(candidate, os.X_OK):
                if not any(candidate.resolve().is_relative_to(path) for path in excluded):
                    return str(candidate)
    raise RuntimeError('Git unavailable on trusted PATH outside the target checkout')


def git(root: Path, *args: str) -> str:
    result = subprocess.run([git_executable(root), '-C', str(root), *args], capture_output=True,
                            text=True, encoding='utf-8', timeout=10)
    if result.returncode:
        raise RuntimeError('Git inspection failed: ' + ' '.join(args))
    return result.stdout.strip()


def inventory(root: Path) -> dict:
    root = root.resolve()
    repository = subprocess.run([git_executable(root), '-C', str(root), 'rev-parse', '--show-toplevel'],
                                capture_output=True, text=True, encoding='utf-8', timeout=10)
    is_repo = repository.returncode == 0
    if is_repo and Path(repository.stdout.strip()).resolve() != root:
        raise RuntimeError('Target must be the repository root, not a nested folder')
    config = subprocess.run([git_executable(root), '-C', str(root), 'config', '--show-origin', '--get-all',
                             'core.hooksPath'], capture_output=True, text=True, encoding='utf-8', timeout=10)
    if config.returncode not in (0, 1):
        raise RuntimeError('Cannot inspect hooksPath')
    result = {'repository': is_repo, 'hooks_config': config.stdout.strip(),
              'hooks_path': git(root, 'config', '--get', 'core.hooksPath') if config.returncode == 0 else None,
              'remotes': git(root, 'remote').splitlines() if is_repo else [],
              'technologies': [label for file, label in [('package.json', 'typescript'),
                               ('Cargo.toml', 'rust'), ('pyproject.toml', 'python')]
                               if (root / file).exists()]}
    includes = subprocess.run(
        [git_executable(root), '-C', str(root), 'config', '--show-origin', '--get-regexp',
         r'^(include|includeif\..*)\.path$'],
        capture_output=True, text=True, encoding='utf-8', timeout=10)
    if includes.returncode not in (0, 1):
        raise RuntimeError('Cannot inspect Git config includes')
    result['config_includes'] = includes.stdout.strip()
    result['legacy_hooks'] = []
    result['worktrees'] = []
    result['common_directory'] = None
    result['config_symlinks'] = []
    if is_repo:
        common = git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir')
        result['common_directory'] = common
        git_directory = Path(git(root, 'rev-parse', '--absolute-git-dir'))
        configs = (Path(common) / 'config', git_directory / 'config.worktree')
        result['config_symlinks'] = sorted({str(p) for config in configs
                                            for p in (config, *config.parents) if linked(p)})
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
    """Only these trusted package assets are installed, never target checkout code."""
    files = {'guard.py': (ASSETS / 'guard.py').read_bytes(),
             'hooks/pre-commit': (ASSETS / 'hooks/pre-commit').read_bytes(),
             'hooks/pre-push': (ASSETS / 'hooks/pre-push').read_bytes()}
    files['manifest.json'] = json.dumps(
        {name: hashlib.sha256(content).hexdigest() for name, content in files.items()},
        sort_keys=True).encode()
    return files


def bundle_directory(root: Path, state: dict) -> Path:
    common = Path(state['common_directory']) if state['repository'] else root / '.git'
    version = hashlib.sha256(desired()['manifest.json']).hexdigest()
    return common / 'project-protection' / version


def legacy_conflicts(root: Path) -> list[str]:
    """Allow explicit migration only of byte-for-byte known v1 installations."""
    conflicts = []
    digests = {**LEGACY_DIGESTS, '.project-protection/manifest.json': hashlib.sha256(
        json.dumps(LEGACY_DIGESTS, sort_keys=True).encode()).hexdigest()}
    for name, digest in digests.items():
        path = root / name
        if linked_ancestor(path) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            conflicts.append(name + ': unknown legacy content; reconcile manually without executing it')
    for directory, allowed in (('.githooks', {'pre-commit', 'pre-push'}),
                               ('.project-protection', {'guard.py', 'manifest.json'})):
        path = root / directory
        if path.is_dir() and not linked_ancestor(path):
            if any(p.name not in allowed for p in path.iterdir()):
                conflicts.append(directory + ': additional legacy files; reconcile manually')
    return conflicts


def plan(root: Path, initialize: bool = False, migrate_legacy: bool = False) -> dict:
    root = root.resolve()
    state = inventory(root)
    conflicts = []
    changes = []
    if not state['repository'] and not initialize:
        conflicts.append('not a repository: explicit --init required')
    if state['config_includes']:
        conflicts.append('Git config includes may activate branch/worktree hooksPath overrides: reconcile manually')
    if state['config_symlinks']:
        conflicts.append('Git config or ancestor is a symlink/junction: reconcile manually')
    bundle = bundle_directory(root, state)
    hooks_path = (bundle / 'hooks').as_posix()
    config = state['hooks_config']
    local_config = subprocess.run(
        [git_executable(root), '-C', str(root), 'config', '--local', '--show-origin', '--get-all', 'core.hooksPath'],
        capture_output=True, text=True, encoding='utf-8', timeout=10).stdout.strip() if state['repository'] else ''
    local_only = bool(config) and len(config.splitlines()) == 1 and config == local_config
    legacy = state['hooks_path'] == '.githooks' and local_only
    if migrate_legacy and not legacy:
        conflicts.append('--migrate-legacy requires the single local v1 .githooks setting')
    if legacy and migrate_legacy:
        conflicts.extend(legacy_conflicts(root))
    elif config and (not local_only or state['hooks_path'] != hooks_path):
        conflicts.append('existing hooksPath: reconcile manually; v1 requires explicit --migrate-legacy')
    activation = state['hooks_path'] != hooks_path
    if activation and len(state['worktrees']) > 1:
        conflicts.append('activation would change shared worktree configuration: reconcile manually')
    if state['legacy_hooks']:
        conflicts.append('existing Git hooks: reconcile manually')
    # A separate Git directory inside a trackable checkout is not a trusted store.
    common = bundle.parent.parent
    # Git may list the metadata path as the primary worktree for --separate-git-dir.
    worktrees = {root, *(Path(path) for path in state['worktrees'] if Path(path) != common)}
    for worktree in worktrees:
        relative = common.relative_to(worktree) if common.is_relative_to(worktree) else None
        if relative is not None and (not relative.parts or relative.parts[0].lower() != '.git'):
            conflicts.append('Git common directory is inside a trackable worktree: reconcile manually')
    files = desired()
    if linked_ancestor(bundle):
        conflicts.append('trusted bundle or ancestor is a symlink/junction')
    else:
        if bundle.exists():
            if not bundle.is_dir():
                conflicts.append('trusted bundle is not a directory')
            else:
                allowed = set(files) | {'hooks'}
                for path in bundle.rglob('*'):
                    if path.relative_to(bundle).as_posix() not in allowed:
                        conflicts.append('unmanaged trusted bundle entry: ' + str(path))
        for name, content in files.items():
            path = bundle / name
            if linked_ancestor(path):
                conflicts.append(name + ': symlink/junction')
            elif path.exists():
                if not path.is_file() or path.read_bytes() != content:
                    conflicts.append(name + ': unmanaged or modified trusted content')
                elif name.startswith('hooks/') and not os.access(path, os.X_OK):
                    conflicts.append(name + ': not executable')
            else:
                changes.append({'path': str(path), 'content': content.decode()})
    if not state['repository']:
        changes.insert(0, {'operation': 'git init --template= -b main (do not copy template hooks)'})
    if activation:
        changes.append({'operation': 'git config --local core.hooksPath', 'value': hooks_path})
    body = {'target': str(root), 'detected': state, 'trusted_bundle': str(bundle),
            'migrate_legacy': migrate_legacy, 'changes': changes, 'conflicts': conflicts}
    if legacy and migrate_legacy:
        body['legacy_files'] = 'preserved, not executed or chained; remove separately after review'
    body['plan_hash'] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    return body


def activate_hooks(root: Path, expected: dict, migrate_legacy: bool = False) -> None:
    """Use Git's config lock protocol; never replace a concurrent setting."""
    config = Path(expected['common_directory']) / 'config'
    lock = config.with_name('config.lock')
    if linked_ancestor(config):
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
        remaining = plan(root, migrate_legacy=migrate_legacy)
        if remaining['conflicts'] or any('path' in change for change in remaining['changes']):
            raise RuntimeError('Assets changed during apply; configuration preserved')
        git(root, 'config', '--file', str(lock), 'core.hooksPath',
            (Path(remaining['trusted_bundle']) / 'hooks').as_posix())
        owned_identity = (lock.lstat().st_dev, lock.lstat().st_ino)
        if linked_ancestor(config) or config.read_bytes() != original:
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


def apply(root: Path, approved_hash: str, initialize: bool = False, migrate_legacy: bool = False) -> dict:
    root = root.resolve()
    proposal = plan(root, initialize, migrate_legacy)
    if proposal['conflicts'] or proposal['plan_hash'] != approved_hash:
        raise RuntimeError('Conflicting or changed plan; inspect and approve a fresh plan')
    if not proposal['detected']['repository']:
        git(root, 'init', '--template=', '-b', 'main')
    expected = inventory(root) if not proposal['detected']['repository'] else proposal['detected']
    for change in proposal['changes']:
        if 'path' in change:
            path = Path(change['path'])
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(change['content'].encode())
            if path.parent.name == 'hooks':
                path.chmod(0o755)
    if proposal['detected']['hooks_path'] != (Path(proposal['trusted_bundle']) / 'hooks').as_posix():
        activate_hooks(root, expected, migrate_legacy)
    return doctor(root)


def doctor(root: Path) -> dict:
    root = root.resolve()
    proposal = plan(root)
    runtime = 'python' if sys.platform == 'win32' else 'python3'
    tools = {runtime: bool(shutil.which(runtime)), 'gitleaks': bool(shutil.which('gitleaks'))}
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
    parser.add_argument('--migrate-legacy', action='store_true', help='Explicitly replace the known v1 local setting')
    parser.add_argument('--apply', metavar='PLAN_HASH', help='Apply this reviewed plan only')
    args = parser.parse_args()
    root = args.target.resolve()
    try:
        if args.command == 'doctor':
            if args.apply or args.init or args.migrate_legacy:
                parser.error('doctor is read-only')
            result = doctor(root)
        elif args.apply:
            result = apply(root, args.apply, args.init, args.migrate_legacy)
        else:
            result = plan(root, args.init, args.migrate_legacy)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as error:
        print(json.dumps({'status': 'unverified', 'reason': str(error)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
