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

import re
import sys
from pathlib import Path

try:
    from .json_input import JsonInputError, load_json_object
except ImportError:
    from json_input import JsonInputError, load_json_object

ROOT = Path(__file__).resolve().parent.parent
NAMESPACES = ROOT / "schema" / "namespaces.json"
AUTHORITIES = ROOT / "schema" / "authorities.json"
POLICY = ROOT / "policy" / "resolution-policy.json"

REQUIRED_NS_KEYS = {"label", "grain", "id_pattern", "url_template", "posture"}
REQUIRED_AUTH_KEYS = {"id", "label", "role", "scopes", "verification", "licence"}
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
KEBAB = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


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


def check_authorities(doc: dict, errors: list[str]) -> int:
    """The authority registry is what makes rank-1 precedence operable.

    An unverifiable or unbounded authority entry is worse than none, because the
    resolution policy would grant it precedence over everything else.
    """
    roles = set(doc.get("roles", {}))
    scope_kinds = set(doc.get("scope_kinds", {}))
    methods = set(doc.get("verification_methods", {}))

    for name, values in (("roles", roles), ("scope_kinds", scope_kinds),
                         ("verification_methods", methods)):
        if not values:
            errors.append(f"authorities.json: {name} is empty, so entries cannot be checked")

    grant_form = doc.get("namespace_grant", {}).get("form", "")
    if "<slug>" not in grant_form:
        errors.append("authorities.json: namespace_grant.form has no <slug> placeholder")

    authorities = doc.get("authorities")
    if authorities is None:
        errors.append("authorities.json: no authorities key")
        return 0

    seen: set[str] = set()
    for entry in authorities:
        aid = entry.get("id", "<unnamed>")
        where = f"authorities.json: {aid}"

        missing = REQUIRED_AUTH_KEYS - set(entry)
        if missing:
            errors.append(f"{where}: missing {', '.join(sorted(missing))}")
            continue

        if not KEBAB.match(entry["id"]):
            errors.append(f"{where}: id is not kebab-case")
        if entry["id"] in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(entry["id"])

        if entry["role"] not in roles:
            errors.append(f"{where}: role {entry['role']!r} is not one of {', '.join(sorted(roles))}")

        if not entry["scopes"]:
            errors.append(
                f"{where}: no scopes declared. An authority with unbounded scope would "
                "outrank every other source everywhere, which is the thing this registry exists to prevent."
            )
        for scope in entry["scopes"]:
            kind = scope.get("kind")
            if kind not in scope_kinds:
                errors.append(f"{where}: scope kind {kind!r} is not one of {', '.join(sorted(scope_kinds))}")
            if kind == "own_catalogue" and not scope.get("namespace"):
                errors.append(f"{where}: an own_catalogue scope must name the namespace it covers")

        if entry["verification"].get("method") not in methods:
            errors.append(
                f"{where}: verification method {entry['verification'].get('method')!r} is not "
                f"one of {', '.join(sorted(methods))}. An unverified authority carries no precedence."
            )

        if entry["licence"] != "CC0-1.0":
            errors.append(
                f"{where}: contributions must be CC0-1.0. An organisation that cannot "
                "contribute on those terms can be cited but does not enter the dataset."
            )

        granted = entry.get("namespace")
        if granted:
            expected = grant_form.replace("<slug>", entry["id"])
            if granted != expected:
                errors.append(f"{where}: granted namespace should be {expected!r}, found {granted!r}")

    return len(authorities)


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

    try:
        ns_doc = load_json_object(NAMESPACES, ROOT)
        auth_doc = load_json_object(AUTHORITIES, ROOT)
        policy_doc = load_json_object(POLICY, ROOT)
    except JsonInputError as exc:
        print(exc)
        return 1

    ns_count = check_namespaces(ns_doc, errors)
    auth_count = check_authorities(auth_doc, errors)
    rule_count = check_policy(policy_doc, errors)

    if errors:
        print(f"{len(errors)} problem(s):\n")
        for err in errors:
            print(f"  {err}")
        return 1

    print(
        f"registry: {ns_count} namespaces, {auth_count} authorities, "
        f"{rule_count} precedence rules, all consistent"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
