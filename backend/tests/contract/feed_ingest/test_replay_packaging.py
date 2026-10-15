"""B02-R1: the replay corpus ships inside the IngestFunction CodeUri package.

The SAM Globals CodeUri is backend/src/; the packaged task root has no
repository parent directories, so the fixture locator must resolve inside it.
"""

import importlib
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

BACKEND = Path(__file__).resolve().parents[3]
GAME = "401872981"


@pytest.mark.contract
def test_replay_corpus_loads_from_an_isolated_code_uri_copy(tmp_path):
    module = importlib.import_module("feed_ingest")
    code = tmp_path / "task"
    shutil.copytree(BACKEND / "src", code,
                    ignore=shutil.ignore_patterns("__pycache__"))
    with patch.object(module, "__file__", str(code / "feed_ingest/__init__.py")):
        fixtures = module._fixtures()
    assert fixtures.is_relative_to(code), "locator must not walk above CodeUri"
    assert len(list(fixtures.glob("*/index.json"))) == 14
    events = module.load_events(GAME, fixtures)
    assert events and all(event["source"] == "replay" for event in events)


@pytest.mark.contract
def test_packaged_corpus_matches_the_captured_game_set():
    module = importlib.import_module("feed_ingest")
    packaged = sorted(p.name for p in module._fixtures().iterdir() if p.is_dir())
    captured = sorted(p.name for p in (BACKEND / "fixtures/replay").iterdir()
                      if p.is_dir())
    assert packaged == captured
