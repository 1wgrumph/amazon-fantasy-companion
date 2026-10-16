"""Reproduce F2/F3 survivors in memory from 20a570a; never edit product files."""

import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[5]
TEST = "backend/tests/unit/lineup/test_review_regressions.py"
CASES = {
    "F2-roster-size": ("manual", " or len(espn_roster) > _max_entries()", "",
                       "test_manual_oversize_espn_roster_is_rejected_without_duplicates"),
    "F3-week-one": ("yahoo", "week < 1", "week <= 1", "test_yahoo_week_one_is_accepted"),
    "F3-leagues-url": ("yahoo", "game_keys=nfl/leagues", "game_keys=nf/leagues",
                       "test_yahoo_leagues_url_is_exact"),
    "F3-modifiers-bound": ("yahoo", "len(modifiers) > _max_items()",
                           "len(modifiers) >= _max_items()",
                           "test_yahoo_settings_at_size_limit_is_accepted[stat_modifiers]"),
    "F3-slots-bound": ("yahoo", "len(slots) > _max_items()",
                       "len(slots) >= _max_items()",
                       "test_yahoo_settings_at_size_limit_is_accepted[roster_slots]"),
}


if len(sys.argv) == 2:
    import pytest
    name = sys.argv[1]
    module_name, before, after, test = CASES[name]
    source_path = f"backend/src/lineup/{module_name}.py"
    source = subprocess.check_output(["git", "show", f"20a570a:{source_path}"], text=True)
    assert source.count(before) == 1
    sys.path.insert(0, str(ROOT / "backend/src"))
    module = importlib.import_module("lineup." + module_name)
    exec(compile(source.replace(before, after), source_path, "exec"), module.__dict__)

    class Failures:
        failed = []

        def pytest_runtest_logreport(self, report):
            if report.failed:
                self.failed.append({"test": report.nodeid, "phase": report.when})

    failures = Failures()
    rc = pytest.main([TEST + "::" + test, "-q", "-p", "no:cacheprovider", "--tb=short"],
                     plugins=[failures])
    print("MUTANT_PROOF " + json.dumps({"case": name, "baseline": "20a570a",
          "baseline_source_sha256": hashlib.sha256(source.encode()).hexdigest(),
          "test_sha256": hashlib.sha256((ROOT / TEST).read_bytes()).hexdigest(),
          "replacement": [before, after], "exit_code": rc, "failures": failures.failed}))
    assert rc == 1 and failures.failed == [{"test": "tests/unit/lineup/" +
                                           Path(TEST).name + "::" + test, "phase": "call"}]
else:
    os.chdir(ROOT)
    results = []
    for name in CASES:
        child = subprocess.run([sys.executable, __file__, name], capture_output=True, text=True,
                               env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), timeout=120)
        print(child.stdout)
        print(child.stderr)
        assert child.returncode == 0, (name, child.returncode)
        results.append(json.loads(next(line.removeprefix("MUTANT_PROOF ")
                            for line in child.stdout.splitlines() if line.startswith("MUTANT_PROOF "))))
    Path(__file__).with_name("review-boundary-proof.json").write_text(
        json.dumps({"status": "PASS", "mutants": results}, indent=2) + "\n")
