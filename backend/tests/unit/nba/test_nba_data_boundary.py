"""Token/data boundary check for the NBA tests and synthetic fixtures (issue #137).

Fails when any NBA test file or fixture carries an OAuth token field, a client
id/secret, a literal bearer token, a high-entropy blob, a home path or an IPv4
address. Patterns are assembled from fragments so this file never matches
itself; a planted-sample self-check proves the scanner is not vacuous.
"""

import re
from pathlib import Path

TESTS = Path(__file__).resolve().parents[2]
SCANNED = sorted([*(TESTS / "fixtures" / "nba").rglob("*.json"),
                  *(TESTS / "unit" / "nba").glob("*.py")])
_U = "_"
PATTERNS = {
    "oauth-field": re.compile("(?i)(access|refresh|id|oauth)" + _U + "token"),
    "client-credential": re.compile("(?i)(client|consumer)" + _U + "(id|key|secret)"),
    "bearer-literal": re.compile("Bearer" + r"\s+[A-Za-z0-9._~+/=-]{16,}"),
    "high-entropy": re.compile(r"(?<![A-Za-z0-9+/])(?=[A-Za-z0-9+/]*\d)(?=[A-Za-z0-9+/]*[a-z])"
                               r"(?=[A-Za-z0-9+/]*[A-Z])[A-Za-z0-9+/]{32,}"),
    "home-path": re.compile("/" + "(home|Users)" + r"/[A-Za-z0-9._-]+"),
    "ipv4": re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])"),
}


def findings(text):
    return sorted({name for name, pattern in PATTERNS.items() if pattern.search(text)})


def test_scanner_detects_each_planted_sample():
    planted = {
        "oauth-field": '{"access' + _U + 'token": "x"}',
        "client-credential": "CLIENT" + _U + "SECRET=x",
        "bearer-literal": "Authorization: Bearer " + "abcDEF0123456789xyz",
        "high-entropy": "k=" + "Zx9" * 12,
        "home-path": "/" + "home/" + "someone/.yahoo",
        "ipv4": "device at " + ".".join(["10", "0", "0", "42"]),
    }
    for name, sample in planted.items():
        assert name in findings(sample), name


def test_scanned_set_includes_the_new_yahoo_fixtures_and_tests():
    names = {p.name for p in SCANNED}
    assert {"leagues.json", "roster_2026-10-21.json", "settings_points.json",
            "test_nba_yahoo.py", "test_nba_manual_lineup.py", Path(__file__).name} <= names


def test_nba_fixtures_and_tests_carry_no_token_or_private_data():
    leaks = {str(p.relative_to(TESTS)): hits for p in SCANNED
             if (hits := findings(p.read_text()))}
    assert leaks == {}
