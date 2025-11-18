"""Utilities to load blueprint definitions from disk."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_blueprint(path: str | Path) -> Dict[str, Any]:
    """Load a blueprint definition from a JSON file."""
    blueprint_path = Path(path)
    if not blueprint_path.exists():
        raise FileNotFoundError(f"Blueprint file '{blueprint_path}' not found")

    with blueprint_path.open("r", encoding="utf-8") as fp:
        try:
            data = json.load(fp)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in '{blueprint_path}': {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("Blueprint root must be a JSON object")

    required_keys = {"name", "entry_point", "nodes"}
    missing = required_keys - data.keys()
    if missing:
        raise ValueError(f"Blueprint is missing required keys: {sorted(missing)}")

    if not isinstance(data["nodes"], list):
        raise ValueError("'nodes' must be a list")

    return data
