#!/usr/bin/env python3
"""Require a DCO sign-off in every commit in a pull-request range."""
from __future__ import annotations

import re
import subprocess
import sys

SIGNOFF = re.compile(r"^Signed-off-by: .+ <.+@.+>$", re.IGNORECASE | re.MULTILINE)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def check_range(base: str, head: str) -> list[str]:
    commits = [sha for sha in git("rev-list", f"{base}..{head}").splitlines() if sha]
    return [
        sha
        for sha in commits
        if not SIGNOFF.search(git("log", "-1", "--format=%B", sha))
    ]


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("usage: check_dco.py BASE HEAD", file=sys.stderr)
        return 2

    try:
        missing = check_range(args[0], args[1])
    except subprocess.CalledProcessError as exc:
        print(exc.stderr.strip() or "git failed while checking the DCO range", file=sys.stderr)
        return 2

    if not missing:
        print("all commits signed off")
        return 0

    for sha in missing:
        print(f"::error::{sha} is not signed off")
        print(git("log", "-1", "--format=  %h %s", sha).rstrip())
    print(
        "\nContributions are dedicated to the public domain under CC0-1.0, and the\n"
        "sign-off is how that is certified. See CONTRIBUTING.md.\n\n"
        "Fix the most recent commit with:  git commit --amend -s\n"
        "Fix a whole branch with:          git rebase --signoff main"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
