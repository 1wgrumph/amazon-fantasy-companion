"""Pinned-schema validation of untrusted ESPN bodies before any store write (AFC-PR-064)."""

import functools
import json
from pathlib import Path

import jsonschema


@functools.cache
def _validator(name):
    schema = json.loads((Path(__file__).parent / "schema" / f"{name}.json").read_text())
    return jsonschema.Draft202012Validator(schema)


def _check(name, payload):
    error = jsonschema.exceptions.best_match(_validator(name).iter_errors(payload))
    if error is not None:
        raise ValueError(f"ESPN {name} fails the pinned schema: {error.message}")


def validate_summary(payload, game_id):
    """None when `payload` is a schema-valid summary for `game_id`; ValueError otherwise."""
    _check("summary", payload)
    if payload["header"]["id"] != game_id:
        raise ValueError("ESPN summary is for another game")


def validate_scoreboard(payload):
    """None when `payload` is a schema-valid scoreboard; ValueError otherwise."""
    _check("scoreboard", payload)
