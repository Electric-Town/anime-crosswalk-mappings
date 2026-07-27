from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from tools import check_docs, validate_conformance, validate_registry_files


class ValidatorMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_json(self, name: str, value: object) -> Path:
        path = self.root / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def capture(self, function) -> tuple[int, str]:
        output = StringIO()
        with redirect_stdout(output):
            result = function()
        return result, output.getvalue()

    def test_conformance_reports_structural_mutations(self) -> None:
        doc = {
            "capabilities": {"unused": "defined but unused"},
            "cases": [
                {
                    "id": "Bad_ID",
                    "title": "Bad",
                    "breaks": "short",
                    "capabilities": ["missing"],
                    "shape": {},
                    "loss_if_unsupported": "short",
                    "observed_in": [],
                },
                {
                    "id": "Bad_ID",
                    "title": "Leak",
                    "breaks": "x" * 40,
                    "capabilities": [],
                    "shape": {"source": "x", "target": "x", "relationship": "tt1234567"},
                    "loss_if_unsupported": "x" * 40,
                    "observed_in": ["example"],
                },
            ],
        }
        path = self.write_json("cases.json", doc)
        with patch.object(validate_conformance, "ROOT", self.root), patch.object(
            validate_conformance, "CASES", path
        ):
            result, output = self.capture(validate_conformance.main)
        self.assertEqual(1, result)
        for message in (
            "id is not kebab-case",
            "duplicate id",
            "undefined capability",
            "shape missing",
            "too thin",
            "observed_in is empty",
            "provider identifier",
            "declares no capabilities",
            "exercised by no case",
        ):
            self.assertIn(message, output)

    def test_registry_reports_invalid_contracts(self) -> None:
        namespace_errors: list[str] = []
        validate_registry_files.check_namespaces(
            {
                "posture_values": {"direct": "", "indirect_only": ""},
                "namespaces": {
                    "bad": {
                        "label": "Bad",
                        "grain": "series",
                        "id_pattern": "[",
                        "url_template": "https://example.invalid/",
                        "posture": "unknown",
                        "allowed_routes": ["x"],
                    },
                    "indirect": {
                        "label": "Indirect",
                        "grain": "series",
                        "id_pattern": "x",
                        "url_template": "https://example.invalid/{id}",
                        "posture": "indirect_only",
                    },
                },
            },
            namespace_errors,
        )
        joined = "\n".join(namespace_errors)
        for message in (
            "is not one of",
            "allowed_routes is only meaningful",
            "id_pattern does not compile",
            "has no {id} placeholder",
            "allowed_routes is absent",
        ):
            self.assertIn(message, joined)

        authority_errors: list[str] = []
        validate_registry_files.check_authorities(
            {
                "roles": {"studio": ""},
                "scope_kinds": {"own_catalogue": ""},
                "verification_methods": {"domain": ""},
                "namespace_grant": {"form": "authority:<slug>"},
                "authorities": [
                    {
                        "id": "Bad_ID",
                        "label": "Bad",
                        "role": "unknown",
                        "scopes": [{"kind": "own_catalogue"}],
                        "verification": {"method": "unknown"},
                        "licence": "MIT",
                        "namespace": "wrong",
                    }
                ],
            },
            authority_errors,
        )
        joined = "\n".join(authority_errors)
        for message in (
            "id is not kebab-case",
            "role",
            "must name the namespace",
            "verification method",
            "CC0-1.0",
            "granted namespace should be",
        ):
            self.assertIn(message, joined)

        policy_errors: list[str] = []
        validate_registry_files.check_policy(
            {
                "policy_version": "latest",
                "precedence": [
                    {"rank": 2, "rule": "", "applies_when": ""},
                    {"rank": 2, "rule": "x", "applies_when": "y"},
                ],
                "publication": {
                    "accepted_artifact_includes": ["verified"],
                    "full_artifact_includes": [],
                    "vendoring_default": "accepted",
                },
            },
            policy_errors,
        )
        joined = "\n".join(policy_errors)
        for message in ("not semver", "duplicate precedence rank", "needs both"):
            self.assertIn(message, joined)

    def test_docs_report_unresolved_reference(self) -> None:
        (self.root / "README.md").write_text("[missing](missing.json)", encoding="utf-8")
        with patch.object(check_docs, "ROOT", self.root):
            result, output = self.capture(check_docs.main)
        self.assertEqual(1, result)
        self.assertIn("missing.json", output)

    def test_each_json_validator_rejects_wrong_root_type(self) -> None:
        path = self.root / "wrong.json"
        path.write_text("[]", encoding="utf-8")
        with patch.object(validate_conformance, "ROOT", self.root), patch.object(
            validate_conformance, "CASES", path
        ):
            result, output = self.capture(validate_conformance.main)
        self.assertEqual(1, result)
        self.assertIn("expected a JSON object", output)
