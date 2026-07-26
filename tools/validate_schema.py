#!/usr/bin/env python3
"""Validate the schema, and prove it is derived from the conformance corpus.

Three things are checked, and the third is the one that matters:

  1. schema/release.schema.json is itself valid JSON Schema 2020-12.
  2. Every fixture marked valid validates, and every fixture marked invalid is
     rejected. A schema that accepts everything passes check 1 and is useless.
  3. Every capability the conformance corpus declares maps to a construct that
     actually exists in the schema, and is exercised by at least one fixture.

Check 3 is what turns "the schema is derived from the conformance corpus" from a
sentence in a README into something CI can fail on.

Requires jsonschema. Listed in requirements-dev.txt and installed in CI.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    print("jsonschema is not installed. pip install -r requirements-dev.txt")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schema" / "release.schema.json"
CASES = ROOT / "conformance" / "cases.json"
CAP_MAP = ROOT / "conformance" / "capability-map.json"
FIXTURES = ROOT / "conformance" / "fixtures.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_pointer(doc: object, pointer: str) -> tuple[bool, str]:
    """RFC 6901 JSON Pointer. Returns (found, failing_token)."""
    if pointer == "":
        return True, ""
    if not pointer.startswith("/"):
        return False, pointer
    node = doc
    for raw in pointer.lstrip("/").split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict):
            if token not in node:
                return False, token
            node = node[token]
        elif isinstance(node, list):
            try:
                node = node[int(token)]
            except (ValueError, IndexError):
                return False, token
        else:
            return False, token
    return True, ""


def main() -> int:
    errors: list[str] = []

    schema = load(SCHEMA)
    cases = load(CASES)
    cap_map = load(CAP_MAP)
    fixtures = load(FIXTURES)

    # 1. The schema is a valid schema.
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        print(f"schema/release.schema.json is not valid JSON Schema 2020-12:\n  {exc}")
        return 1
    validator = Draft202012Validator(schema)

    # 2. Fixtures. Valid must pass; invalid must fail.
    valid_fixtures = fixtures.get("valid", [])
    invalid_fixtures = fixtures.get("invalid", [])

    for entry in valid_fixtures:
        problems = sorted(validator.iter_errors(entry["record"]), key=lambda e: list(e.path))
        if problems:
            first = problems[0]
            errors.append(
                f"fixture exercising {', '.join(entry['exercises'])} should validate but does not: "
                f"{'/'.join(str(p) for p in first.path) or '<root>'}: {first.message}"
            )

    for entry in invalid_fixtures:
        if validator.is_valid(entry["record"]):
            errors.append(
                f"fixture that must be rejected was accepted: {entry['must_reject']}"
            )

    # 3. Derivation. Every declared capability maps to something real, and is exercised.
    declared = set(cases.get("capabilities", {}))
    mapped = cap_map.get("map", {})

    unmapped = declared - set(mapped)
    if unmapped:
        errors.append(
            f"capabilities with no schema construct: {', '.join(sorted(unmapped))}. "
            "Either the schema is missing something the corpus requires, or the capability "
            "should not be declared."
        )

    stray = set(mapped) - declared
    if stray:
        errors.append(
            f"capability-map entries for capabilities the corpus does not declare: "
            f"{', '.join(sorted(stray))}"
        )

    for name, entry in sorted(mapped.items()):
        pointer = entry.get("pointer", "")
        found, token = resolve_pointer(schema, pointer)
        if not found:
            errors.append(
                f"capability {name}: pointer {pointer} does not resolve in the schema "
                f"(stopped at {token!r})"
            )
        if len(entry.get("note", "")) < 20:
            errors.append(f"capability {name}: note is too thin to explain the construct")

    exercised: set[str] = set()
    for entry in valid_fixtures:
        exercised.update(entry.get("exercises", []))
    unexercised = declared - exercised
    if unexercised:
        errors.append(
            f"capabilities with no fixture exercising them: {', '.join(sorted(unexercised))}. "
            "A mapped capability with no worked record is unproven."
        )

    if errors:
        print(f"{len(errors)} problem(s):\n")
        for err in errors:
            print(f"  {err}")
        return 1

    print(
        f"schema: valid 2020-12 | {len(valid_fixtures)} fixtures accepted, "
        f"{len(invalid_fixtures)} rejected as required | "
        f"{len(declared)} capabilities mapped to real constructs and exercised"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
