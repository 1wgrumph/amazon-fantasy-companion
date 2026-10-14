"""Read-only validation of the frozen P2-B03 behavioral-red receipt."""

import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

EVIDENCE = Path("docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B03T")


def validate(receipt_path):
    receipt = json.loads(receipt_path.read_text())
    red = receipt["red"]
    assert red["exit_code"] == 1, "pytest must exit 1 for assertion failures"
    junit = Path(red["junit"])
    assert junit.resolve().is_relative_to(EVIDENCE.resolve()), "JUnit outside P2-B03T evidence"
    cases = ET.parse(junit).getroot().findall(".//testcase")
    assert cases, "no collected test cases"
    failed, skipped = 0, 0
    ids = []
    for case in cases:
        assert case.find("error") is None, "error case present"
        skip = case.find("skipped")
        if skip is not None:
            assert case.get("classname", "").startswith("tests.deployed."), "skip outside deployed scope"
            assert (skip.get("message") or "").startswith("NOT_RUN"), "skip without NOT_RUN signal"
            skipped += 1
        else:
            failure = case.find("failure")
            assert failure is not None, "required red case passed"
            assert failure.get("type") in (None, "AssertionError"), "non-behavioral failure type"
            assert failure.get("message", "").startswith("AssertionError"), "non-assertion failure"
            failed += 1
        ids.append(case.get("classname").replace(".", "/") + ".py::" + case.get("name"))
    assert sorted(ids) == sorted(red["test_ids"]), "test inventory changed"
    assert len(ids) == len(set(ids)), "duplicate test ID"
    frozen = dict(receipt["frozen_test_sha256"])
    frozen.update(receipt.get("frozen_fixture_sha256", {}))
    for name, expected in frozen.items():
        path = Path(name).resolve()
        assert path.is_relative_to(Path("backend/tests").resolve()), "frozen file outside backend/tests"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, f"frozen hash changed: {name}"
    assert failed == red["failed"] and skipped == red["skipped"], "counts changed"
    return {"outcome": "PASS", "failed_cases": failed, "errors": 0, "skipped": skipped,
            "frozen_files": len(frozen)}


if __name__ == "__main__":
    try:
        result = validate(Path(sys.argv[1]))
    except AssertionError as error:
        print(json.dumps({"outcome": "VALIDATION_FAILED", "reason": str(error)}))
        sys.exit(1)
    except (OSError, KeyError, ValueError, ET.ParseError, IndexError):
        print(json.dumps({"outcome": "NEEDS_EVIDENCE", "reason": "missing or invalid receipt/artifact"}))
        sys.exit(2)
    print(json.dumps(result))
