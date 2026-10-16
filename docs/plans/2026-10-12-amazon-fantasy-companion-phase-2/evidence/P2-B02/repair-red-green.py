"""Reproduce the repair regressions on the pinned baseline and working candidate."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[5]
out = Path(__file__).resolve().parent
record = json.loads((out / "repair-red-green.json").read_text())
tests = record["test_selectors"]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
with tempfile.TemporaryDirectory(prefix="afc-b02-red-") as work:
    archive = subprocess.Popen(["git", "archive", record["baseline"], "backend"],
                               cwd=root, stdout=subprocess.PIPE)
    subprocess.run(["tar", "-x", "-C", work], stdin=archive.stdout, check=True)
    archive.stdout.close()
    assert archive.wait() == 0
    for name in {test.split("::")[0] for test in tests}:
        shutil.copyfile(root / name, Path(work) / name)
    with (out / record["red"]["output"]).open("w") as log:
        red = subprocess.run(["python3.12", "-m", "pytest", *tests, "-q", "--tb=short"],
                             cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT)
with (out / record["green"]["output"]).open("w") as log:
    green = subprocess.run(["python3.12", "-m", "pytest", *tests, "-q", "--tb=short"],
                           cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
record["red"]["exit_code"] = red.returncode
record["green"]["exit_code"] = green.returncode
record["test_file_sha256"] = {}
import hashlib
for name in sorted({test.split("::")[0] for test in tests}):
    record["test_file_sha256"][name] = hashlib.sha256((root / name).read_bytes()).hexdigest()
(out / "repair-red-green.json").write_text(json.dumps(record, indent=2) + "\n")
print(f"red exit: {red.returncode}; green exit: {green.returncode}")
assert red.returncode == 1 and green.returncode == 0
