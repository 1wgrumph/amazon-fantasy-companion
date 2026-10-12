# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml==6.0.3"]
# ///
"""Render and lint specification figures; exit 3 for missing Graphviz."""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from azdiagram.__main__ import main

if __name__ == "__main__":
    if shutil.which("dot") is None:
        print("TOOL_MISSING: Graphviz dot is required", file=sys.stderr)
        sys.exit(3)
    sys.exit(main())
