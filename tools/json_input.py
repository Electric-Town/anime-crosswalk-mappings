"""Strict, user-facing JSON input handling for repository validators."""
from __future__ import annotations

import json
from pathlib import Path


class JsonInputError(ValueError):
    """A JSON file could not be loaded as the object a validator expects."""


def load_json_object(path: Path, root: Path) -> dict:
    try:
        label = path.relative_to(root)
    except ValueError:
        label = path

    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise JsonInputError(f"{label}: missing") from exc
    except OSError as exc:
        raise JsonInputError(f"{label}: cannot read: {exc.strerror or exc}") from exc

    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise JsonInputError(f"{label}:{exc.lineno}:{exc.colno}: {exc.msg}") from exc

    if not isinstance(value, dict):
        raise JsonInputError(
            f"{label}: expected a JSON object at the document root, "
            f"found {type(value).__name__}"
        )
    return value
