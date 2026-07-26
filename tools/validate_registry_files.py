#!/usr/bin/env python3
"""Structural checks on the namespace registry and the resolution policy.

These two files are the parts of the crosswalk that other rules depend on. The
namespace registry decides which acquisition routes are admissible; the
resolution policy decides which of two conflicting claims wins. A malformed or
internally inconsistent entry in either would be enforced silently and wrongly,
so both are checked here before anything is allowed to build on them.

Exits 1 and names every problem. No dependencies outside the standard library.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAMESPACES = ROOT / "schema" / "namespaces.json"
POLICY = ROOT / "policy" / "resolution-policy.json"

REQUIRED_NS_KEYS = {"label", "grain", "id_pattern", "url_template", "posture"}
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def load(path: Path, errors: list[str]) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{path.relative_to(ROOT)}: missing")
    except json.JSONDecodeError as exc:
        errors.append(f"{path.relative_to(ROOT)}:{exc.lineno}: {exc.msg}")
    return None


def check_namespaces(doc: dict, errors: list[str]) -> int:
    postures = set(doc.get("posture_values", {}))
    if not postures:
        errors.append("namespaces.json: posture_values is empty, so posture cannot be checked")
        return 0

    namespaces = doc.get("namespaces", {})
    if not namespaces:
        errors.append("namespaces.json: no namespaces registered")
        return 0

    for name, entry in sorted(namespaces.items()):
        where = f"namespaces.json: {name}"

        missing = REQUIRED_NS_KEYS - set(entry)
        if missing:
            errors.append(f"{where}: missing {', '.join(sorted(missing))}")
            continue

        if entry["posture"] not in postures:
            errors.append(
                f"{where}: posture {entry['posture']!r} is not one of "
                f"{', '.join(sorted(postures))}"
            )

        # A namespace that may only be reached indirectly must say by which
        # routes, or the restriction is unenforceable and therefore decorative.
        if entry["posture"] == "indirect_only" and not entry.get("allowed_routes"):
            errors.append(f"{where}: posture is indirect_only but allowed_routes is absent")

        if entry["posture"] != "indirect_only" and entry.get("allowed_routes"):
            errors.append(
                f"{where}: allowed_routes is only meaningful when posture is indirect_only"
            )

        try:
            re.compile(entry["id_pattern"])
        except re.error as exc:
            errors.append(f"{where}: id_pattern does not compile: {exc}")

        for key in ("url_template", "url_template_film"):
            template = entry.get(key)
            if template is not None and "{id}" not in template:
                errors.append(f"{where}: {key} has no {{id}} placeholder")

    return len(namespaces)


def check_policy(doc: dict, errors: list[str]) -> int:
    version = doc.get("policy_version", "")
    if not SEMVER.match(version):
        errors.append(
            f"resolution-policy.json: policy_version {version!r} is not semver. "
            "Resolutions cite this version, so it has to be comparable."
        )

    precedence = doc.get("precedence", [])
    if not precedence:
        errors.append("resolution-policy.json: precedence is empty")
        return 0

    ranks = [rule.get("rank") for rule in precedence]
    if ranks != sorted(r for r in ranks if isinstance(r, int)):
        errors.append("resolution-policy.json: precedence ranks are not in ascending order")
    if len(set(ranks)) != len(ranks):
        errors.append("resolution-policy.json: duplicate precedence rank")

    for rule in precedence:
        if not rule.get("rule") or not rule.get("applies_when"):
            errors.append(
                f"resolution-policy.json: rank {rule.get('rank')} needs both a rule name "
                "and an applies_when condition"
            )

    publication = doc.get("publication", {})
    accepted = set(publication.get("accepted_artifact_includes", []))
    full = set(publication.get("full_artifact_includes", []))
    if accepted and full and not accepted <= full:
        errors.append(
            "resolution-policy.json: the accepted artifact declares classes the full "
            f"artifact does not: {', '.join(sorted(accepted - full))}"
        )

    default = publication.get("vendoring_default")
    if default and f"{default}_artifact_includes" not in publication:
        errors.append(
            f"resolution-policy.json: vendoring_default is {default!r} but no "
            f"{default}_artifact_includes is declared"
        )

    return len(precedence)


def main() -> int:
    errors: list[str] = []

    ns_doc = load(NAMESPACES, errors)
    ns_count = check_namespaces(ns_doc, errors) if ns_doc else 0

    policy_doc = load(POLICY, errors)
    rule_count = check_policy(policy_doc, errors) if policy_doc else 0

    if errors:
        print(f"{len(errors)} problem(s):\n")
        for err in errors:
            print(f"  {err}")
        return 1

    print(f"registry: {ns_count} namespaces, {rule_count} precedence rules, all consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
