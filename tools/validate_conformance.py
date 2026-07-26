#!/usr/bin/env python3
"""Check the conformance corpus is well formed.

The corpus is the specification the schema is derived from, so a malformed or
vacuous case is worse than a missing one: it looks like coverage and is not.

Enforced here:
  - identifiers are unique and kebab-case
  - every declared capability is defined, and every defined capability is used
  - every case says what breaks and what is lost, in more than a phrase
  - no case carries a provider identifier, because the corpus asserts structure

Exits 1 and names every problem. Standard library only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "conformance" / "cases.json"

REQUIRED = {"id", "title", "breaks", "capabilities", "shape", "loss_if_unsupported", "observed_in"}
SHAPE_KEYS = {"source", "target", "relationship"}
KEBAB = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

# The corpus tests expressiveness, not correctness of a row, so it must stay free of
# provider identifiers. Anything matching these is a data leak into a specification.
ID_LEAK = re.compile(
    r"\b(tt\d{7,8}"                      # IMDb
    r"|myanimelist\.net/anime/\d+"
    r"|anilist\.co/anime/\d+"
    r"|anidb\.net/anime/\d+"
    r"|thetvdb\.com/\S*\d"
    r"|themoviedb\.org/\S*\d"
    r"|10\.5240/[0-9A-Z-]+)",             # EIDR
    re.IGNORECASE,
)

# A meaningful explanation, not a shrug.
MIN_PROSE = 40


def main() -> int:
    errors: list[str] = []

    try:
        doc = json.loads(CASES.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"{CASES.relative_to(ROOT)}: missing")
        return 1
    except json.JSONDecodeError as exc:
        print(f"{CASES.relative_to(ROOT)}:{exc.lineno}: {exc.msg}")
        return 1

    defined = set(doc.get("capabilities", {}))
    if not defined:
        errors.append("no capabilities defined")

    cases = doc.get("cases", [])
    if not cases:
        errors.append("no cases")

    seen_ids: set[str] = set()
    used: set[str] = set()

    for index, case in enumerate(cases):
        cid = case.get("id", f"<case {index}>")
        where = f"case {cid}"

        missing = REQUIRED - set(case)
        if missing:
            errors.append(f"{where}: missing {', '.join(sorted(missing))}")
            continue

        if not KEBAB.match(case["id"]):
            errors.append(f"{where}: id is not kebab-case")
        if case["id"] in seen_ids:
            errors.append(f"{where}: duplicate id")
        seen_ids.add(case["id"])

        caps = case["capabilities"]
        if not caps:
            errors.append(f"{where}: declares no capabilities, so it tests nothing")
        for cap in caps:
            if cap not in defined:
                errors.append(f"{where}: undefined capability {cap!r}")
        used.update(caps)

        missing_shape = SHAPE_KEYS - set(case["shape"])
        if missing_shape:
            errors.append(f"{where}: shape missing {', '.join(sorted(missing_shape))}")

        for field in ("breaks", "loss_if_unsupported"):
            if len(case[field].strip()) < MIN_PROSE:
                errors.append(
                    f"{where}: {field} is too thin to be useful. A case that cannot say "
                    "what goes wrong is a preference, not a case."
                )

        if not case["observed_in"]:
            errors.append(f"{where}: observed_in is empty. Cases describe real families of works.")

        leak = ID_LEAK.search(json.dumps(case))
        if leak:
            errors.append(
                f"{where}: contains what looks like a provider identifier ({leak.group(0)!r}). "
                "The corpus asserts structure and stays identifier-free."
            )

    unused = defined - used
    if unused:
        errors.append(
            f"capabilities defined but exercised by no case: {', '.join(sorted(unused))}. "
            "Either write the case or drop the capability."
        )

    if errors:
        print(f"{len(errors)} problem(s):\n")
        for err in errors:
            print(f"  {err}")
        return 1

    print(
        f"conformance: {len(cases)} cases, {len(defined)} capabilities, "
        f"all exercised, no identifiers"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
