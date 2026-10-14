"""Read-only validation of a frozen AFC behavioral-red receipt."""

import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def validate(receipt_path):
    receipt = json.loads(receipt_path.read_text())
    red = receipt["red"]
    assert red["exit_code"] == 1, "pytest must exit 1 for assertion failures"
    assert Path(red["junit"]).resolve().is_relative_to(receipt_path.resolve().parent), "JUnit outside receipt evidence directory"
    cases = ET.parse(red["junit"]).getroot().findall(".//testcase")
    assert cases, "no collected test cases"
    ids = []
    for case in cases:
        assert case.find("error") is None and case.find("skipped") is None, "error or skipped case"
        failure = case.find("failure")
        assert failure is not None, "required red case passed"
        assert failure.get("type") in (None, "AssertionError"), "non-behavioral failure type"
        assert failure.get("message", "").startswith("AssertionError:"), "non-assertion failure message"
        ids.append(case.get("classname").replace(".", "/") + ".py::" + case.get("name"))
    assert sorted(ids) == sorted(red["test_ids"]), "test inventory changed"
    assert len(ids) == len(set(ids)), "duplicate test ID"
    for name, expected in receipt["frozen_test_sha256"].items():
        path = Path(name).resolve()
        assert path.is_relative_to(Path("backend/tests").resolve()), "test file outside allowed inventory"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, "frozen test hash changed"
    return {"outcome": "PASS", "failed_cases": len(cases), "errors": 0, "skips": 0,
            "frozen_files": len(receipt["frozen_test_sha256"])}


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
