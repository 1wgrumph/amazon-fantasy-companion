"""Render the Phase 2 planning views (use cases, alert->Watch flow, program waves) as
plain SVG from the Mermaid sources in design.md / the technical plan. Deterministic;
standard library only. Run from the plan directory: python3 evidence/P2-6/render_views.py
"""
import pathlib
from xml.sax.saxutils import escape

OUT = pathlib.Path("views")
OUT.mkdir(exist_ok=True)
FONT = 'font-family="sans-serif"'


def svg(w, h, title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">\n'
            f'<title>{escape(title)}</title>\n'
            '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#333"/></marker></defs>\n'
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>\n' + body + '</svg>\n')


def box(x, y, w, h, text, fill="#eef3fb"):
    lines = text.split("\n")
    t = "".join(f'<text x="{x + w / 2}" y="{y + h / 2 + (i - (len(lines) - 1) / 2) * 15 + 5}" text-anchor="middle" font-size="12" {FONT}>{escape(s)}</text>' for i, s in enumerate(lines))
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="#335" stroke-width="1"/>{t}\n'


def arrow(x1, y1, x2, y2, label=""):
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#333" stroke-width="1.2" marker-end="url(#a)"/>'
    if label:
        s += f'<text x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 - 4}" text-anchor="middle" font-size="10" {FONT}>{escape(label)}</text>'
    return s + "\n"


# V-P2-1 use cases
b = box(20, 120, 110, 40, "Customer", "#fdf3e1") + box(20, 330, 110, 40, "Owner", "#fdf3e1")
cases = ["Link TV by device code", "Set lineup source, preset, controls", "Receive alert over provider playback",
         "Watch: open provider game or channel", "Follow lineup panel"]
for i, c in enumerate(cases):
    y = 20 + i * 60
    b += box(260, y, 300, 40, c) + arrow(130, 140, 260, y + 20)
b += box(260, 330, 300, 40, "Approve, publish, submit") + arrow(130, 350, 260, 350)
b += arrow(410, 160, 410, 200, "then")
(OUT / "p2-use-cases.svg").write_text(svg(600, 390, "Phase 2 use cases (outcome view)", b))

# V-P2-2 alert -> Watch sequence
parts = ["ESPN JSON", "backend.ingest", "matcher+policy", "backend.api", "tvApp.alertSvc", "tvApp.notifier", "tvApp.launcher", "Provider app"]
W = 120
b = ""
for i, p in enumerate(parts):
    x = 10 + i * W
    b += box(x, 10, W - 10, 34, p) + f'<line x1="{x + (W - 10) / 2}" y1="44" x2="{x + (W - 10) / 2}" y2="470" stroke="#999" stroke-dasharray="4,3"/>\n'
cx = lambda i: 10 + i * W + (W - 10) / 2
msgs = [(1, 0, "poll (feed_poll_interval)"), (0, 1, "summary JSON"), (1, 1, "schema check, store revision"),
        (1, 2, "GameEvent"), (2, 2, "relevance, types, periods, quiet, frequency, spoiler"), (2, 3, "Alert + route + access basis"),
        (4, 3, "GET /v1/alerts (long poll)"), (3, 4, "Alert"), (4, 5, "present (heads-up or panel-only)"), (5, 6, "Watch"),
        (6, 7, "registry intent/URI (after confirmation)"), (6, 3, "POST /v1/routing-outcome")]
for k, (s, d, label) in enumerate(msgs):
    y = 70 + k * 33
    if s == d:
        b += f'<text x="{cx(s) + 6}" y="{y}" font-size="10" {FONT}>{escape(label)}</text>\n'
    else:
        b += arrow(cx(s), y, cx(d), y, label)
(OUT / "p2-alert-watch-flow.svg").write_text(svg(10 + len(parts) * W, 480, "Phase 2 operational flow: alert to Watch", b))

# V-P2-3 program waves / release checkpoints
waves = [("W1 Foundations (due 10-14 23:00Z)", "L01 X01 X05 D01 G01T/G01 A01T/A01 B01T/B01 R1"),
         ("W2 Spike verdicts (due 10-17 01:00Z = T_yahoo + 6 h)", "X04 X02 X03 X07 X06 B02T/B02 B03T/B03 A02T/A02 L02 R2"),
         ("W3 End-to-end on the stick (due 10-19 12:00Z)", "B04..B07 pairs A03..A05 pairs L03 X09 (Sun 10-18) R3"),
         ("W4 Feature complete (due 10-21 23:00Z)", "X10 (Mon 10-19) D02 X11 (conditional) R4 + bug-triager defects"),
         ("W5 Submission ready (due 10-23 12:00Z)", "D03 D04 D05 SCR1 -> R5 (v1.0.0 candidate) -> L05 (APK + Reverify) -> X12 (Thu 10-22)")]
b = ""
for i, (m, s) in enumerate(waves):
    y = 15 + i * 62
    b += box(15, y, 330, 46, m, "#e8f5e9") + box(365, y, 520, 46, s)
    if i:
        b += arrow(180, y - 16, 180, y)
b += f'<text x="15" y="335" font-size="11" {FONT}>Stick lease: X01 -> X04 (within 24 h of first install) -> A01 review -> X02 -> X03 desk -> X07; X03 live = TNF 10-15. Cap: 5.</text>\n'
(OUT / "p2-program-waves.svg").write_text(svg(900, 345, "Phase 2 waves and release checkpoints", b))
print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
