# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml==6.0.3"]
# ///
"""Lint specification section sources.

A section source is YAML front matter with a ``requirements`` list, exactly one
heading, an opening prose paragraph without printed writer labels,
and a captioned table or figure whenever the structural trigger fires.

Usage: ``python tools/spec_lint.py <section dir>``; exits 1 on any finding.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

MAX_REQUIREMENTS = 5
WRITER_LABEL = re.compile(
    r"\*\*(?:BLUF|Frame)\b|\*\*(?:Who|What|Why|How|When|Where):?\*\*"
)
TABLE_CLASSES = {f"T{n}" for n in range(1, 9)}
FIGURE_CLASSES = {f"F{n}" for n in range(1, 9)}
SECTION_FILE = re.compile(r"^(\d+(?:\.\d+)*)-.+\.md$")
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
CAPTION = re.compile(r"^(Table|Figure) \(([A-Z]+\d+)\): (\S.*)$")
HEADING = re.compile(r"^(#{1,6}) (\S.*)$")
BULLET = re.compile(r"^[-*] (.*)$")
ORDERED = re.compile(r"^\d+\. ")
ATTRIBUTE = re.compile(r"^\s*(?:\*\*)?([A-Za-z][\w ]*?):(?:\*\*)?\s*\S")
ISSUE_REF = re.compile(r"(?<![\w])(?:[\w.-]+/[\w.-]+)?#\d+\b|\b(?:issue|PR|pull request)\s+#?\d+\b", re.I)
SECTION_REF = re.compile(r"\bsections?\s+\d+(?:\.\d+)*\b|\bsee\s+\d+(?:\.\d+)+\b", re.I)
FILE_REF = re.compile(r"(?<![\w])(?:[\w.-]+/)*[\w.-]+\.(?:md|markdown|sdoc|pdf|docx?|xlsx?|csv|ya?ml|json|toml|txt|html?|py|sh|js|ts|tsx|rs|svg|drawio)\b", re.I)
URL_REF = re.compile(r"https?://[^\s<>]+", re.I)
INLINE_CODE = re.compile(r"(`+)(?!`).*?(?<!`)\1(?!`)", re.DOTALL)
LINK = re.compile(r"!?\[([^\]\n]+)\](?:\(([^\s()]+(?:\([^()]*\)[^\s()]*)*)(?:\s+\"[^\"]*\")?\)|\[([^\]\n]*)\])")


def split_front_matter(text: str) -> tuple[dict | None, str]:
    match = FRONT_MATTER.match(text)
    if not match:
        return None, text
    data = yaml.safe_load(match.group(1))
    return (data if isinstance(data, dict) else {}), text[match.end() :]


def section_files(src_dir: Path) -> list[Path]:
    """Section sources in document order: numeric prefixes such as 04.1.2 sort naturally."""
    files = [f for f in Path(src_dir).iterdir() if SECTION_FILE.match(f.name)]
    return sorted(
        files,
        key=lambda f: tuple(int(n) for n in SECTION_FILE.match(f.name)[1].split(".")),
    )


def prose_lines(body: str) -> list[str]:
    """Preserve line positions while excluding Markdown backtick/tilde fences."""
    lines, fence = [], None
    for line in body.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            lines.append("")
        elif marker:
            fence = marker[1]
            lines.append("")
        else:
            lines.append(line)
    return lines


def reference_findings(body: str) -> list[str]:
    text = INLINE_CODE.sub("code", "\n".join(prose_lines(body)))
    definitions = dict(re.findall(r"^ {0,3}\[([^\]]+)\]:\s*(\S+).*$", text, re.M))
    definitions = {key.lower(): value.strip("<>") for key, value in definitions.items()}
    text = re.sub(r"^ {0,3}\[[^\]]+\]:.*$", "", text, flags=re.M)

    def linked(label, target):
        return bool(target) and (not SECTION_REF.search(label) or target.startswith("#"))

    def unlink(match):
        label, target, key = match.groups()
        target = target or definitions.get((key or label).lower())
        if not linked(label, target):
            return label
        return ""

    text = LINK.sub(unlink, text)
    # Shortcut reference links are clickable only with a matching definition.
    text = re.sub(r"\[([^\]\n]+)\]", lambda m: "" if linked(m[1], definitions.get(m[1].lower())) else m[0], text)
    text = re.sub(r"<https?://[^\s<>]+>", "", text)
    return [f"unlinked {kind} reference: {match[0]}"
            for kind, pattern in (("issue/PR", ISSUE_REF), ("section", SECTION_REF), ("document/file", FILE_REF), ("document/file", URL_REF))
            for match in pattern.finditer(text)]


def revision_findings(meta: dict) -> list[str]:
    revisions = meta.get("revisions")
    if not isinstance(revisions, list) or not revisions:
        return ["revisions must be a non-empty list"]
    findings = []
    for index, revision in enumerate(revisions):
        if not isinstance(revision, dict) or not revision.get("rev"):
            findings.append(f"revision entry {index + 1}: rev is required")
            continue
        prefix = f"revision {revision['rev']}: "
        changes, links = revision.get("changes", []), revision.get("links", {})
        if not isinstance(changes, list) or any(not isinstance(s, str) or not s.strip() for s in changes) or (index and not changes):
            findings.append(prefix + "changes must list changed sections")
        if not isinstance(links, dict):
            findings.append(prefix + "links must map pr and diff URLs")
            continue
        if (index or links.get("pr")) and not re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+/pull/\d+", str(links.get("pr", ""))):
            findings.append(prefix + "links.pr must be a PR URL")
        if (index or links.get("diff")) and not re.fullmatch(r"https://[^\s<>]+/(?:compare/[^\s<>]+|pull/\d+/files)", str(links.get("diff", ""))):
            findings.append(prefix + "links.diff must be a diff/compare URL")
    return findings


def list_blocks(lines: list[str], pattern: re.Pattern) -> list[list[str]]:
    blocks, current = [], []
    for line in lines + [""]:
        if pattern.match(line):
            current.append(line)
        elif current:
            blocks.append(current)
            current = []
    return blocks


def _next_content(lines: list[str], index: int) -> str:
    return next((line for line in lines[index + 1 :] if line.strip()), "")


def lint_section(text: str) -> list[str]:
    findings = []
    meta, body = split_front_matter(text)
    findings.extend(reference_findings(body))
    if meta is None:
        findings.append("missing YAML front matter with a requirements list")
    else:
        requirements = meta.get("requirements")
        if not isinstance(requirements, list):
            findings.append("front matter requirements is not a list")
        elif len(requirements) > MAX_REQUIREMENTS:
            findings.append(
                f"binds {len(requirements)} requirements; at most {MAX_REQUIREMENTS} per section"
            )

    lines = prose_lines(body)
    headings = [line for line in lines if HEADING.match(line)]
    if len(headings) != 1:
        findings.append(
            f"has {len(headings)} headings; a section source has exactly one"
        )
    if WRITER_LABEL.search(body):
        findings.append("printed writer label; use ordinary specification prose")
    opening_lines = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).splitlines()
    heading_index = next(
        (i for i, line in enumerate(opening_lines) if HEADING.match(line)), -1
    )
    opening = _next_content(opening_lines, heading_index).strip()
    if not opening or re.match(
        r"^(?:#|[-*+] |\d+[.)] |[|>]|!\[|```|~~~|(?:Table|Figure) \()", opening
    ):
        findings.append("missing opening paragraph after the section heading")

    has_table = has_figure = False
    for i, line in enumerate(lines):
        match = CAPTION.match(line)
        if not match:
            continue
        kind, cls, _ = match.groups()
        valid = TABLE_CLASSES if kind == "Table" else FIGURE_CLASSES
        if cls not in valid:
            findings.append(
                f"{kind} class {cls} is outside {'T1-T8' if kind == 'Table' else 'F1-F8'}"
            )
        follow = _next_content(lines, i)
        if kind == "Table":
            has_table = True
            if not follow.startswith("|"):
                findings.append(
                    f"Table ({cls}) caption is not followed by a Markdown table"
                )
        else:
            has_figure = True
            if not follow.startswith("!["):
                findings.append(f"Figure ({cls}) caption is not followed by an image")

    bullets = list_blocks(lines, BULLET)
    if not has_table:
        for block in bullets:
            keys = [
                {
                    m[1].lower()
                    for part in re.split(r"[;,—]", item)
                    if (m := ATTRIBUTE.match(part))
                }
                for item in (BULLET.match(line)[1] for line in block)
            ]
            shared = {
                k for k in set().union(*keys) if sum(k in item for item in keys) >= 3
            }
            if len(shared) >= 2:
                findings.append(
                    "list of 3+ items sharing 2+ attributes needs a table (Table (Tn): caption)"
                )
                break
    if not has_figure:
        related = any(
            len(
                {e.strip() for line in block for e in BULLET.match(line)[1].split("->")}
            )
            >= 3
            for block in bullets
            if all("->" in line for line in block)
        )
        ordered = any(len(block) >= 3 for block in list_blocks(lines, ORDERED))
        if related or ordered:
            findings.append(
                "3+ related entities (-> list or ordered steps) need a figure "
                "(Figure (Fn): caption)"
            )
    return findings


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: spec_lint.py <section dir>", file=sys.stderr)
        return 2
    files = section_files(Path(argv[0]))
    if not files:
        print(f"{argv[0]}: no section sources (NN-*.md)")
        return 1
    failed = False
    metadata = Path(argv[0]) / "spec.yaml"
    if metadata.exists():
        for finding in revision_findings(yaml.safe_load(metadata.read_text()) or {}):
            print(f"{metadata}: {finding}")
            failed = True
    for path in files:
        for finding in lint_section(path.read_text()):
            print(f"{path}: {finding}")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
