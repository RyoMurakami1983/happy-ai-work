"""Run the production hook logic with a test script launched by its own interpreter."""
import importlib.util
import subprocess
import sys
from unittest.mock import patch


def run_fixture(guard_path, scanner_script):
    spec = importlib.util.spec_from_file_location('guard', guard_path)
    assert spec and spec.loader
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    scan = guard.scan
    lookup = guard.trusted_executable

    def scan_with_python(args):
        def fixture_tool(name):
            return sys.executable if name == 'gitleaks' else lookup(name)

        with patch.object(guard, 'trusted_executable', side_effect=fixture_tool):
            scan(['-I', scanner_script, *args])

    with patch.object(guard, 'scan', side_effect=scan_with_python):
        return guard.main()


if __name__ == '__main__':
    try:
        sys.exit(run_fixture(globals()['guard_path'], globals()['scanner_script']))
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        print('project-protection: ' + str(error), file=sys.stderr)
        sys.exit(1)
