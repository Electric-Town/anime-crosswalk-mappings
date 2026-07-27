from __future__ import annotations

import copy
import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator, FormatChecker

from tools import validate_schema

ROOT = Path(__file__).resolve().parent.parent


class SchemaValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schema/release.schema.json").read_text())
        cls.base = json.loads(
            (ROOT / "conformance/fixtures.json").read_text()
        )["valid"][0]["record"]
        cls.validator = Draft202012Validator(
            cls.schema, format_checker=FormatChecker()
        )

    def errors_after(self, mutate) -> list:
        record = copy.deepcopy(self.base)
        mutate(record)
        return list(self.validator.iter_errors(record))

    def test_current_repository_contract_passes(self) -> None:
        self.assertEqual(0, validate_schema.main())

    def test_impossible_dates_are_rejected(self) -> None:
        for value in ("2026-99-99", "2026-02-30"):
            with self.subTest(value=value):
                errors = self.errors_after(lambda record: record.__setitem__("updated", value))
                self.assertTrue(any(error.validator == "format" for error in errors))

    def test_other_schema_versions_are_rejected(self) -> None:
        errors = self.errors_after(
            lambda record: record.__setitem__("schema_version", "2.0.0")
        )
        self.assertTrue(any(error.validator == "const" for error in errors))

    def test_verified_requires_human_reviewer(self) -> None:
        def mutate(record: dict) -> None:
            record["mappings"][0]["evidence_class"] = "verified"

        self.assertTrue(any(error.validator == "contains" for error in self.errors_after(mutate)))

    def test_corroborated_requires_multiple_records(self) -> None:
        def mutate(record: dict) -> None:
            record["mappings"][0]["evidence_class"] = "corroborated"

        self.assertTrue(any(error.validator == "minItems" for error in self.errors_after(mutate)))

    def test_asserted_requires_rightsholder_evidence(self) -> None:
        def mutate(record: dict) -> None:
            record["mappings"][0].update(
                evidence_class="asserted",
                authority="example",
            )

        self.assertTrue(any(error.validator == "contains" for error in self.errors_after(mutate)))

    def test_negative_array_pointer_is_rejected(self) -> None:
        found, _, token = validate_schema.resolve_pointer([1], "/-1")
        self.assertFalse(found)
        self.assertEqual("-1", token)

    def test_unrelated_capability_pointer_fails_mutation_proof(self) -> None:
        cap_map = json.loads((ROOT / "conformance/capability-map.json").read_text())
        cap_map["map"]["cardinality_expand"]["pointer"] = "/properties/id"
        with patch.object(validate_schema, "load_json_object") as load:
            load.side_effect = [
                self.schema,
                json.loads((ROOT / "conformance/cases.json").read_text()),
                cap_map,
                json.loads((ROOT / "conformance/fixtures.json").read_text()),
                json.loads((ROOT / "examples/release.json").read_text()),
            ]
            output = StringIO()
            with redirect_stdout(output):
                result = validate_schema.main()
        self.assertEqual(1, result)
        self.assertIn("cardinality_expand", output.getvalue())
        self.assertIn("did not reject fixture", output.getvalue())
