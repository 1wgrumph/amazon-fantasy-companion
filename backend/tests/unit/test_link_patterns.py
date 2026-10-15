"""Compile the shipped HTML patterns with the browser's Unicode Sets rules."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess


class PatternParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.patterns = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "pattern" in attrs:
            self.patterns.append(attrs)


def test_link_patterns_compile_in_v_mode_and_preserve_profile_ids():
    parser = PatternParser()
    parser.feed((Path(__file__).resolve().parents[2] / "src/api/link.html").read_text())
    assert parser.patterns, "The link page must declare its input patterns"
    [profile] = [attrs["pattern"] for attrs in parser.patterns if attrs.get("id") == "profileId"]
    samples = [chr(code) for code in range(128)]
    samples += ["", "a" * 64, "a" * 65, "A_z-09", "a/b", "owner\n", "é", "😀"]
    result = subprocess.run(
        ["node", "-e", r"""
const input = JSON.parse(require("node:fs").readFileSync(0, "utf8"));
for (const pattern of input.patterns) new RegExp(pattern, "v");
const profile = new RegExp("^(?:" + input.profile + ")$", "v");
process.stdout.write(JSON.stringify(input.samples.map(value => {
  const match = profile.exec(value);
  return match !== null && match[0] === value;
})));
"""],
        input=json.dumps({"patterns": [attrs["pattern"] for attrs in parser.patterns],
                          "profile": profile, "samples": samples}),
        text=True, capture_output=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [
        re.fullmatch(r"[A-Za-z0-9_-]{1,64}", value) is not None for value in samples
    ]
