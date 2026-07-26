#!/usr/bin/env python3
"""Assert that every repository path referenced in Markdown actually exists.

A README that describes files which are not there is the cheapest way to lose a
reader's trust, and it is the failure mode that recurs most often as a project
grows. This is the mechanical enforcement of one rule: nothing is described in
the documentation that is not in the repository.

Exits 1 and lists every unresolved reference. Exits 0 and says nothing useful
when the documentation is honest.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# A backticked span is treated as a path only if it looks like one. Field names,
# enum values and identifiers are also backticked and must not be mistaken for
# files.
PATHISH = re.compile(r"^[\w./-]+$")
EXTENSIONS = {".md", ".json", ".jsonl", ".py", ".yml", ".yaml", ".xml", ".txt", ".zst"}

INLINE_CODE = re.compile(r"`([^`\n]+)`")
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")

SKIP_PREFIXES = ("http://", "https://", "mailto:", "#", "<")


def looks_like_path(token: str) -> bool:
    if not token or token.startswith(SKIP_PREFIXES):
        return False
    if not PATHISH.match(token):
        return False
    if token.endswith("/"):
        return True
    return "/" in token or Path(token).suffix in EXTENSIONS


def references(text: str) -> set[str]:
    found = set()
    for match in INLINE_CODE.findall(text):
        token = match.strip()
        if looks_like_path(token):
            found.add(token)
    for match in MD_LINK.findall(text):
        token = match.split("#", 1)[0].strip()
        if looks_like_path(token):
            found.add(token)
    return found


def main() -> int:
    failures: list[tuple[Path, str]] = []
    checked = 0

    for doc in sorted(ROOT.rglob("*.md")):
        if ".git" in doc.parts:
            continue
        for ref in sorted(references(doc.read_text(encoding="utf-8"))):
            checked += 1
            if not (ROOT / ref).exists():
                failures.append((doc.relative_to(ROOT), ref))

    if failures:
        print(f"{len(failures)} unresolved path reference(s):\n")
        for doc, ref in failures:
            print(f"  {doc}: {ref}")
        print("\nEither create the file or stop describing it.")
        return 1

    print(f"docs: {checked} path reference(s) across the repository, all resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
