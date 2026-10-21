# BUG-PROVIDER-ART

## Reproduction

On `0ace67dfc58dfb0bb3e5e891b5b7a9109ab50f4f` (the `origin/main` tip at the
start of this fix), `python3 tools/ci/check_provider_art.py` exits 1.
`red.txt` is that stdout. It names each of the twenty withheld captures
with `PROVIDER-ART-NAME` and `PROVIDER-ART-HASH`, and it names the text
files that still cited them.

## Origin

Spike and device captures for SP-2, SP-3, SP-4, and P2-A04 committed
provider screens before the rule that committed images show companion UI
only. That rule is owner decision OD-AFC-P2-02 = B, recorded by the
Orchestrator on 2026-10-20.

## Escape

Nothing in the hygiene gate rejected provider imagery, so the captures
stayed on the public tip after the rule existed.

## Classification

Compliance and content defect in committed evidence. Not product code.
The pictures are Prime Video and Fire TV screens, team logos, and the
YouTube TV site. Black protected-video frames, Fire OS settings screens,
and companion UI were left in the tree.

## Prevention

`tools/ci/check_provider_art.py` runs from the hygiene area of
`tools/ci/gate.sh`. It fails when a tracked path uses one of the withheld
basenames, when a tracked blob's sha256 is one of the withheld content
hashes, or when any other tracked text file contains those basenames or
hashes. `evidence/visual/PRIVATE-EVIDENCE.md`, the check, and `red.txt`
are the only text records allowed to cite them. Tests cover a clean tree,
a returned basename, the same bytes under another name, a text citation,
and the manifest exception.

History still contains the images. Removing them from history needs a
force-push, which this fix does not do.
