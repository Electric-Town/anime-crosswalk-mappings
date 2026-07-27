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

import copy
import json
import re
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    print("jsonschema is not installed. pip install -r requirements-dev.txt")
    sys.exit(1)

try:
    from .json_input import JsonInputError, load_json_object
except ImportError:
    from json_input import JsonInputError, load_json_object

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schema" / "release.schema.json"
CASES = ROOT / "conformance" / "cases.json"
CAP_MAP = ROOT / "conformance" / "capability-map.json"
FIXTURES = ROOT / "conformance" / "fixtures.json"
README = ROOT / "README.md"
EXAMPLE = ROOT / "examples" / "release.json"


def pointer_tokens(pointer: str) -> list[str] | None:
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        return None
    return [
        raw.replace("~1", "/").replace("~0", "~")
        for raw in pointer.lstrip("/").split("/")
    ]


def resolve_pointer(doc: object, pointer: str) -> tuple[bool, object | None, str]:
    """RFC 6901 JSON Pointer. Returns (found, value, failing_token)."""
    tokens = pointer_tokens(pointer)
    if tokens is None:
        return False, None, pointer
    node = doc
    for token in tokens:
        if isinstance(node, dict):
            if token not in node:
                return False, None, token
            node = node[token]
        elif isinstance(node, list):
            if not token.isdigit() or int(token) >= len(node):
                return False, None, token
            node = node[int(token)]
        else:
            return False, None, token
    return True, node, ""


def replace_pointer(doc: object, pointer: str, replacement: object) -> bool:
    tokens = pointer_tokens(pointer)
    if not tokens:
        return False
    parent_pointer = (
        ""
        if len(tokens) == 1
        else "/" + "/".join(
            token.replace("~", "~0").replace("/", "~1") for token in tokens[:-1]
        )
    )
    found, parent, _ = resolve_pointer(doc, parent_pointer)
    if not found:
        return False
    token = tokens[-1]
    if isinstance(parent, dict) and token in parent:
        parent[token] = replacement
        return True
    if isinstance(parent, list) and token.isdigit() and int(token) < len(parent):
        parent[int(token)] = replacement
        return True
    return False


def json_pointer(parts: object) -> str:
    return "/" + "/".join(
        str(part).replace("~", "~0").replace("/", "~1") for part in parts
    )


def main() -> int:
    errors: list[str] = []

    try:
        schema = load_json_object(SCHEMA, ROOT)
        cases = load_json_object(CASES, ROOT)
        cap_map = load_json_object(CAP_MAP, ROOT)
        fixtures = load_json_object(FIXTURES, ROOT)
        example = load_json_object(EXAMPLE, ROOT)
    except JsonInputError as exc:
        print(exc)
        return 1

    # 1. The schema is a valid schema.
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        print(f"schema/release.schema.json is not valid JSON Schema 2020-12:\n  {exc}")
        return 1
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    # 2. Fixtures. Valid must pass; invalid must fail.
    valid_fixtures = fixtures.get("valid", [])
    invalid_fixtures = fixtures.get("invalid", [])

    fixture_ids: set[str] = set()
    fixture_by_id: dict[str, dict] = {}
    for entry in valid_fixtures + invalid_fixtures:
        fixture_id = entry.get("id")
        if not fixture_id:
            errors.append("fixture has no id")
        elif fixture_id in fixture_ids:
            errors.append(f"fixture id is duplicated: {fixture_id}")
        else:
            fixture_ids.add(fixture_id)
            fixture_by_id[fixture_id] = entry

    for entry in valid_fixtures:
        problems = sorted(validator.iter_errors(entry["record"]), key=lambda e: list(e.path))
        if problems:
            first = problems[0]
            errors.append(
                f"fixture exercising {', '.join(entry['exercises'])} should validate but does not: "
                f"{'/'.join(str(p) for p in first.path) or '<root>'}: {first.message}"
            )

    for entry in invalid_fixtures:
        problems = list(validator.iter_errors(entry["record"]))
        if not problems:
            errors.append(
                f"fixture that must be rejected was accepted: {entry['must_reject']}"
            )
            continue
        expected_validator = entry.get("expected_validator")
        expected_schema_path = entry.get("expected_schema_path")
        if not expected_validator or not expected_schema_path:
            errors.append(f"invalid fixture {entry.get('id', '<unnamed>')} has no expected failure")
            continue
        if not any(
            problem.validator == expected_validator
            and json_pointer(problem.absolute_schema_path) == expected_schema_path
            for problem in problems
        ):
            observed = ", ".join(
                f"{problem.validator}@{json_pointer(problem.absolute_schema_path)}"
                for problem in problems
            )
            errors.append(
                f"invalid fixture {entry['id']} did not fail as intended; "
                f"expected {expected_validator}@{expected_schema_path}, observed {observed}"
            )

    example_problems = list(validator.iter_errors(example))
    if example_problems:
        first = example_problems[0]
        errors.append(
            f"examples/release.json is invalid at "
            f"{json_pointer(first.absolute_path)}: {first.message}"
        )
    marker = "<!-- validated-release-example: examples/release.json -->"
    readme = README.read_text(encoding="utf-8")
    match = re.search(
        re.escape(marker) + r"\s*```json\s*(.*?)\s*```",
        readme,
        re.DOTALL,
    )
    if not match:
        errors.append("README.md has no marked release example")
    else:
        try:
            readme_example = json.loads(match.group(1))
        except ValueError as exc:
            errors.append(f"README.md release example is malformed JSON: {exc}")
        else:
            if readme_example != example:
                errors.append("README.md release example differs from examples/release.json")

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
        found, _, token = resolve_pointer(schema, pointer)
        if not found:
            errors.append(
                f"capability {name}: pointer {pointer} does not resolve in the schema "
                f"(stopped at {token!r})"
            )
        if len(entry.get("note", "")) < 20:
            errors.append(f"capability {name}: note is too thin to explain the construct")

        fixture_id = entry.get("fixture")
        instance_path = entry.get("instance_path")
        fixture = fixture_by_id.get(fixture_id)
        if fixture is None:
            errors.append(f"capability {name}: fixture {fixture_id!r} does not exist")
            continue
        if name not in fixture.get("exercises", []):
            errors.append(f"capability {name}: fixture {fixture_id} does not exercise it")
        if not isinstance(instance_path, str) or not instance_path.startswith("/"):
            errors.append(f"capability {name}: instance_path must be a JSON Pointer")
            continue

        mutated_schema = copy.deepcopy(schema)
        if not replace_pointer(mutated_schema, pointer, False):
            continue
        mutation_errors = list(
            Draft202012Validator(
                mutated_schema, format_checker=FormatChecker()
            ).iter_errors(fixture["record"])
        )
        if not any(
            json_pointer(problem.absolute_path) == instance_path
            for problem in mutation_errors
        ):
            observed = ", ".join(
                json_pointer(problem.absolute_path) for problem in mutation_errors
            ) or "<none>"
            errors.append(
                f"capability {name}: disabling {pointer} did not reject fixture "
                f"{fixture_id} at {instance_path}; observed {observed}"
            )

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
