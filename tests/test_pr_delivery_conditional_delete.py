"""Exercise the documented Git deletion shape only against disposable bare remotes.

These tests establish transport/ref guarantees, not agent authorization or GitHub support.
"""

import os
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path


class ConditionalDeleteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="pr-delivery-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.remote = self.root / "remote.git"
        self.env = {
            key: value for key, value in os.environ.items()
            if not key.startswith("GIT_")
        }
        self.env.update({
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_ALLOW_PROTOCOL": "file",
            "GIT_AUTHOR_NAME": "Synthetic Evaluator",
            "GIT_AUTHOR_EMAIL": "synthetic@example.invalid",
            "GIT_COMMITTER_NAME": "Synthetic Evaluator",
            "GIT_COMMITTER_EMAIL": "synthetic@example.invalid",
        })
        self.git(self.root, "init", "--bare", str(self.remote))
        self.git(self.root, "init", "-b", "main", str(self.repo))
        (self.repo / "data.txt").write_text("base\n", encoding="utf-8")
        self.git(self.repo, "add", ".")
        self.git(self.repo, "commit", "-m", "base")
        self.expected = self.git(self.repo, "rev-parse", "HEAD").stdout.strip()
        self.ref = "refs/heads/delivery"
        self.git(self.repo, "remote", "add", "origin", str(self.remote))
        self.git(self.repo, "push", "origin", "HEAD:refs/heads/main",
                 f"HEAD:{self.ref}", "HEAD:refs/heads/keep")
        self.git(self.repo, "fetch", "origin")

    def git(self, at: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(at), *args], env=self.env,
            text=True, capture_output=True, check=check,
        )

    def refs(self) -> dict[str, str]:
        lines = self.git(self.remote, "for-each-ref", "--format=%(refname) %(objectname)").stdout
        return dict(line.split() for line in lines.splitlines())

    def delete(self) -> subprocess.CompletedProcess[str]:
        # Same command shape as references/conditional-delete.md, with fixed fixture values.
        return self.git(
            self.repo, "push", "--no-follow-tags", "--recurse-submodules=no",
            f"--force-with-lease={self.ref}:{self.expected}", "--",
            str(self.remote), f":{self.ref}", check=False,
        )

    def advance_remote(self) -> str:
        self.git(self.repo, "switch", "-c", "writer")
        (self.repo / "extra.txt").write_text("keep this new work\n", encoding="utf-8")
        self.git(self.repo, "add", "extra.txt")
        self.git(self.repo, "commit", "-m", "concurrent work")
        tip = self.git(self.repo, "rev-parse", "HEAD").stdout.strip()
        self.git(self.repo, "push", "origin", f"HEAD:{self.ref}")
        return tip

    def test_matching_tip_deletes_only_target_even_with_push_defaults(self) -> None:
        before = self.refs()
        self.git(self.repo, "config", "push.default", "matching")
        self.git(self.repo, "config", "push.followTags", "true")
        self.git(self.repo, "config", "remote.origin.mirror", "true")
        self.git(self.repo, "tag", "-a", "local-only", "-m", "never publish")
        result = self.delete()
        self.assertEqual(result.returncode, 0, result.stderr)
        del before[self.ref]
        self.assertEqual(self.refs(), before)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD").stdout.strip(), self.expected)

    def test_changed_tip_rejected_even_after_tracking_ref_refresh(self) -> None:
        new_tip = self.advance_remote()
        self.git(self.repo, "fetch", "origin")
        self.assertEqual(
            self.git(self.repo, "rev-parse", "refs/remotes/origin/delivery").stdout.strip(),
            new_tip,
        )
        before = self.refs()
        result = self.delete()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.refs(), before)
        self.assertEqual(self.refs()[self.ref], new_tip)
        self.assertEqual(
            self.git(self.remote, "show", f"{self.ref}:extra.txt").stdout,
            "keep this new work\n",
        )

    def test_tip_changed_after_advertisement_is_preserved(self) -> None:
        new_tip = self.advance_remote()
        self.git(self.remote, "update-ref", self.ref, self.expected, new_tip)
        before = self.refs()
        # pre-push runs after Git reads advertised refs, immediately before sending.
        hook = self.repo / ".git" / "hooks" / "pre-push"
        hook.write_text(
            "#!/bin/sh\n" + shlex.join([
                "git", "-C", str(self.remote), "update-ref", self.ref, new_tip, self.expected,
            ]) + "\n", encoding="utf-8",
        )
        hook.chmod(0o755)
        result = self.delete()
        self.assertNotEqual(result.returncode, 0)
        before[self.ref] = new_tip
        self.assertEqual(self.refs(), before)
        self.assertEqual(
            self.git(self.remote, "show", f"{self.ref}:extra.txt").stdout,
            "keep this new work\n",
        )

    def test_server_rejects_deletion_without_fallback(self) -> None:
        before = self.refs()
        self.git(self.remote, "config", "receive.denyDeletes", "true")
        result = self.delete()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.refs(), before)


if __name__ == "__main__":
    unittest.main()
