"""Mechanical AC/RISK statement checks reusing lint-sdoc.py rule constants.

Usage: python3 specialists/ac_mechanical_lint.py <lint-sdoc.py> <technical-plan.md>
"""
import importlib.util, re, sys

spec = importlib.util.spec_from_file_location("lint_sdoc", sys.argv[1])
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
rows = flagged = 0
for line in open(sys.argv[2], encoding="utf-8"):
    if line.startswith("## Exclusions"):
        break  # rows after this point (Deferred to Phase 2) are not register rows
    m = re.match(r"\| ((?:AC|RISK)-AFC-[A-Z0-9-]+)(?: \*\((?:amended|new)\)\*)? \| (.+?) \| ", line)
    if not m:
        continue
    rows += 1
    uid, text = m.groups()
    issues = []
    prefix = next((p for p in mod.EARS_PREFIXES if text.startswith(p[0])), None)
    if not prefix:
        issues.append("no EARS prefix")
    elif prefix[1] and prefix[1] not in text:
        issues.append("If-clause without ', then '")
    if " shall " not in text:
        issues.append("no 'shall'")
    for modal in (" should ", " may "):
        if modal in text:
            issues.append("weak modal" + modal.rstrip())
    low = text.lower()
    issues += ["banned term: " + t for t in mod.BANNED_TERMS if re.search(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])", low)]
    issues += ["agnostic term: " + t for t in mod.AGNOSTIC_TERMS if re.search(r"\b" + re.escape(t) + r"\b", low)]
    flagged += bool(issues)
    print(uid, "OK" if not issues else "; ".join(issues))
print(f"rows={rows} flagged={flagged}")
