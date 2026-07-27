from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.json_input import JsonInputError, load_json_object


class JsonInputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_missing_file_is_structured(self) -> None:
        with self.assertRaisesRegex(JsonInputError, r"missing\.json: missing"):
            load_json_object(self.root / "missing.json", self.root)

    def test_malformed_json_is_structured(self) -> None:
        path = self.root / "broken.json"
        path.write_text("{", encoding="utf-8")
        with self.assertRaisesRegex(JsonInputError, r"broken\.json:1:2:"):
            load_json_object(path, self.root)

    def test_wrong_root_type_is_rejected(self) -> None:
        path = self.root / "list.json"
        path.write_text("[]", encoding="utf-8")
        with self.assertRaisesRegex(JsonInputError, r"expected a JSON object.*found list"):
            load_json_object(path, self.root)

    def test_object_is_returned(self) -> None:
        path = self.root / "object.json"
        path.write_text('{"ok": true}', encoding="utf-8")
        self.assertEqual({"ok": True}, load_json_object(path, self.root))
