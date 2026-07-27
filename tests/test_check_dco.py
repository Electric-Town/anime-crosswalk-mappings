from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from tools import check_dco


class DcoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        self.old_cwd = Path.cwd()
        subprocess.run(["git", "init", "-q", self.repo], check=True)
        subprocess.run(["git", "-C", self.repo, "config", "user.name", "Test"], check=True)
        subprocess.run(
            ["git", "-C", self.repo, "config", "user.email", "test@example.com"],
            check=True,
        )
        self.commit("base", signed=True)
        self.base = self.rev()
        os.chdir(self.repo)

    def tearDown(self) -> None:
        os.chdir(self.old_cwd)
        self.temp.cleanup()

    def commit(self, subject: str, *, signed: bool) -> None:
        message = [subject]
        if signed:
            message += ["-m", "Signed-off-by: Test <test@example.com>"]
        subprocess.run(
            ["git", "-C", self.repo, "commit", "--allow-empty", "-q", "-m", *message],
            check=True,
        )

    def rev(self) -> str:
        return subprocess.run(
            ["git", "-C", self.repo, "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def run_check(self, base: str, head: str) -> tuple[int, str]:
        output = StringIO()
        with redirect_stdout(output):
            result = check_dco.main([base, head])
        return result, output.getvalue()

    def test_empty_range_passes(self) -> None:
        result, output = self.run_check(self.base, self.base)
        self.assertEqual(0, result)
        self.assertIn("all commits signed off", output)

    def test_signed_range_passes(self) -> None:
        self.commit("signed", signed=True)
        result, _ = self.run_check(self.base, self.rev())
        self.assertEqual(0, result)

    def test_unsigned_range_fails(self) -> None:
        self.commit("unsigned", signed=False)
        result, output = self.run_check(self.base, self.rev())
        self.assertEqual(1, result)
        self.assertIn("is not signed off", output)

    def test_mixed_range_fails(self) -> None:
        self.commit("signed", signed=True)
        self.commit("unsigned", signed=False)
        result, output = self.run_check(self.base, self.rev())
        self.assertEqual(1, result)
        self.assertIn("unsigned", output)
