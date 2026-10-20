# P2-D03 fresh-host dependency download (2026-10-20)

Closes the typed gap `FRESH_HOST_DOWNLOAD_NOT_PROVEN` recorded in
`fresh-setup-receipt.json`: the walkthrough host's documented venv
already existed, so its hash-pinned installs downloaded nothing.
This run creates two brand-new venvs under a private scratchpad
(`<scratchpad>/d03-fresh-host/`), each with an empty per-install
`PIP_CACHE_DIR` and `--no-cache-dir`, and runs the README
hash-pinned installs otherwise unchanged. The pre-existing
afc-tools environments were not used or modified. Machine-readable
record, including each venv's full `pip freeze`:
`fresh-host-download.json` (same directory).

Environment: `python3.12` 3.12.3, pip 25.1.1 (venv-bundled).

## Backend closure (`backend/requirements-dev.txt`)

```bash
python3.12 -m venv <scratchpad>/d03-fresh-host/backend-tests
PIP_CACHE_DIR=<scratchpad>/d03-fresh-host/cache-backend \
  <scratchpad>/d03-fresh-host/backend-tests/bin/python3.12 \
  -m pip install --no-cache-dir --require-hashes \
  -r backend/requirements-dev.txt
```

Result: venv exit 0, install exit 0, 42 `Downloading` lines, no
hash-mismatch output; `Successfully installed` lists the 42 pinned
packages and `pip freeze` returns the same 42 pins. The only
differences from the README command are the venv location,
`--no-cache-dir`, and the empty `PIP_CACHE_DIR`. Requirements file
sha256 `d95d58b060eebce85295993c92c84523944cc993414d216742341e051cc68250`.

## Hygiene closure (`tools/ci/requirements-hygiene.txt`)

```bash
python3.12 -m venv <scratchpad>/d03-fresh-host/hygiene
PIP_CACHE_DIR=<scratchpad>/d03-fresh-host/cache-hygiene \
  <scratchpad>/d03-fresh-host/hygiene/bin/python3.12 \
  -m pip install --no-cache-dir --require-hashes \
  -r tools/ci/requirements-hygiene.txt
<scratchpad>/d03-fresh-host/hygiene/bin/python3.12 -c 'import yaml'
```

Result: venv exit 0, install exit 0, 23 `Downloading` lines, no
hash-mismatch output; `import yaml` exit 0 (PyYAML 6.0.3); `pip
freeze` returns the 23 pins. The README hygiene command installs
into the `python3` that runs the gate; here that interpreter is
the brand-new venv `python3.12` (the README's PEP 668 route), so
the closure itself is what downloads. Requirements file sha256
`459ed1e12426d507bf0ec98b023e9c888809459045965841218a10017f7a065f`.

## Verdict

PASS. Both README hash-pinned installs download and install from
an empty pip cache into brand-new venvs, with pip's hash checking
passing. Captured logs stay in the private scratchpad (trailing
whitespace stripped before the gates ran); the counts, exit codes,
requirements digests, and freeze lists above and in the JSON are
the committed evidence.
