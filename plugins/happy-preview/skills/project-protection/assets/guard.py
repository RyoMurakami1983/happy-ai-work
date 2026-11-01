"""Local accident prevention. Requires Python 3 and Gitleaks 8.24+."""
import shutil
import subprocess
import sys


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def scan(args):
    if not shutil.which('gitleaks'):
        raise RuntimeError('Gitleaks unavailable; scan not executed')
    result = subprocess.run(['gitleaks', *args, '--redact', '--no-banner'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode:
        raise RuntimeError('Secret scan failed or found a secret; details suppressed')


def main():
    mode = sys.argv[1]
    if mode == 'pre-commit':
        if git('symbolic-ref', '--quiet', '--short', 'HEAD') == 'main':
            raise RuntimeError('Ordinary commits on main are blocked; create a feature branch')
        scan(['git', '--pre-commit', '--staged'])
    elif mode == 'pre-push':
        updates = [line.split() for line in sys.stdin if line.strip()]
        if any(len(row) != 4 for row in updates):
            raise RuntimeError('Invalid pre-push input')
        # Check every destination before scanning; deletion is also an update to main.
        if any(row[2] == 'refs/heads/main' for row in updates):
            raise RuntimeError('Push destination main is blocked (including deletion)')
        for _, local, _, remote in updates:
            if set(local) == {'0'}:
                continue
            revision = local if set(remote) == {'0'} else f'{remote}..{local}'
            scan(['git', '--log-opts=' + revision])
    else:
        raise RuntimeError('Unknown hook')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        print('project-protection: ' + str(error), file=sys.stderr)
        sys.exit(1)
