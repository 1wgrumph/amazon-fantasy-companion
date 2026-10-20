# Demo video plan — Amazon Fantasy Companion

Slice P2-D05, issue [#50](https://github.com/1wgrumph/amazon-fantasy-companion/issues/50).
Governing criterion: `AC-AFC-P2-SUB-02` (technical plan §Submission).
Capture itself is P2-X12 (M13, on the final APK from P2-L05); this document
is the plan. M12 documents are due 2026-10-22T16:00:00Z (RISK-AFC-P2-14).
Submission deadline `T_deadline` is 2026-10-23T19:00:00Z; judge access runs
through `T_judge_access` 2026-11-20.

## Duration

Filmable-today shot list: 12 + 22 + 28 + 30 + 32 + 18 + 14 = **156 s**
(2 min 36 s). That is 14 s under the 170 s (2 min 50 s) plan limit and
24 s under the under-3-minute public-video rule. PENDING swap-ins below
reuse the duration of the shot they replace, so the total stays at 156 s
whichever version is filmed. No shot is added beyond this list.

## Rules for every shot

- Source is one of exactly: **on-device capture**, **owner camera capture**,
  or **labeled replay**. A labeled replay is labeled on screen as replay;
  it never stands in for live notification or provider behavior evidence.
- No shot claims behavior with no passing evidence. Where the target
  behavior failed its spike, the shot shows the honest fallback and the
  narration states the limit.
- No live Yahoo API data is shown or implied; the lineup source is manual
  entry, labeled manual (SP-6 FAILS).
- No account details, credentials, or device addresses appear on screen.
- Fire OS on the owner's stick (AFTKM, Fire OS 8.1.8.5 / API 30) is the
  primary target. Vega is a paused stretch compatibility target only
  (owner direction, 2026-10-20; RISK-AFC-P2-14): it is named in the
  closing narration as a paused stretch with stated limits, never shown
  as delivered, and no Vega footage is planned.

## Protected-video limitation (RISK-AFC-P2-09)

Provider video uses secure surfaces. On-device `adb` screencap or
screenrecord of provider playback may return black or blank frames, so
**this plan does not claim capturable provider video**. SP-3 desk
evidence shows exactly this: playback state is evidenced, the picture
itself is a black secure surface (`spikes/sp3-provider-links/VERDICT.md`).

`OD-AFC-P2-02` — owner camera capture (A) versus companion-UI-only
capture (B) — is **not recorded as decided** in the tree (the technical
plan records a recommendation only). This plan does not choose it.
Every shot that would show provider video is written conditionally:

- Under **A**: that shot uses owner camera capture of the TV screen and
  is marked owner-filmed; on-device captures cover the companion UI.
- Under **B**: that shot uses on-device capture of the companion UI
  only; provider video is described in narration, not shown.

The filmable-today list below needs no provider-video shot, so it is
filmable under either disposition. Only PENDING shot P-X09-2 depends on
this decision. The owner checklist records `OD-AFC-P2-02` as a decision
needed before P2-X12 capture.

## Shot list — filmable today (156 s)

| Shot | Duration | What is shown | Source | Register UIDs shown | Evidence |
|---|---|---|---|---|---|
| S1 | 12 s | Problem statement; companion app launches on the Fire TV stick (AFTKM, Fire OS 8.1.8.5 / API 30). Narration: Fire OS is primary; Vega is a paused stretch compatibility target, not delivered. | on-device capture | AFC-PR-052, AFC-PR-053 | SP-1 WORKS, `spikes/sp1-device/VERDICT.md` (PR #89) |
| S2 | 22 s | Lineup setup by labeled manual entry built from ESPN rosters. Narration states the Yahoo route is not approved and no live Yahoo data is used; manual values are never presented as Yahoo values. | on-device capture | AFC-PR-006, AFC-PR-007 | SP-6 FAILS (Yahoo route), `spikes/sp6-yahoo/VERDICT.md` (PR #100); manual is the single active source |
| S3 | 28 s | A replay event involving a followed starter produces an alert, rendered panel-only in the companion app. On-screen label: replay. Narration states there is no heads-up banner over other apps on this device, so panel-only presentation is the selected fallback. | labeled replay | AFC-PR-013, AFC-PR-021, AFC-PR-027 | SP-2 FAILS (heads-up), `spikes/sp2-notify/VERDICT.md` (PR #109); AFC-PR-021 panel-only fallback; replay per AFC-PR-013 |
| S4 | 30 s | **Required moment (a), at proven strength:** alert → D-pad **Watch** → Prime Video opens at its search screen (outcome `searchOpened`). Narration states this honestly: the correct provider opens; a direct-to-game open (`gameOpened`) is not proven for any provider, and no outcome is relabeled. Ends on the search screen — no provider video is shown, so this shot is identical under OD-AFC-P2-02 A or B. | on-device capture | AFC-PR-029, AFC-PR-030, AFC-PR-031, AFC-PR-048 | SP-3 PARTIAL, `spikes/sp3-provider-links/VERDICT.md` (PR #110): Prime Video `searchOpened` is the registered route; `gameOpened` unproven |
| S5 | 32 s | **Required moment (b), at proven strength:** the lineup panel moment — followed team's starters, points, game status, team total and progress, with stale or unavailable values labeled as such, never zero. The panel is full-screen in the companion app. Narration states the panel does not sit beside playing video on this device; full-screen is the selected fallback. | on-device capture | AFC-PR-039, AFC-PR-040, AFC-PR-047 | SP-4 FAILS (panel beside video), `spikes/sp4-panel-video/VERDICT.md` (PR #106); `PanelMode.fullScreen` per AFC-PR-047 |
| S6 | 18 s | Honest unavailable route: for a game carried by a provider whose app is not installed, the outcome is reported as `appAbsent` and unverifiable game access is shown as unknown — never promised from an installed app alone. | on-device capture | AFC-PR-031, AFC-PR-032, AFC-PR-033 | SP-3 PARTIAL: ESPN, DirecTV Stream and YouTube TV are `appAbsent` on the stick; local broadcast has no carrying app (PR #110) |
| S7 | 14 s | Customer control takes effect: an alert-type setting is changed and the changed behavior is stated; closing summary repeats the limits — panel-only alerts, full-screen panel, manual lineup, no voice offer, Vega paused stretch only. | on-device capture | AFC-PR-016, AFC-PR-021 | Alert policy gated by enabled types (PR #85); presentation choice per AFC-PR-021 |

Total: 12 + 22 + 28 + 30 + 32 + 18 + 14 = **156 s** ≤ 170 s.
Margin: 14 s under the plan limit, 24 s under 3 minutes.

Required-moment coverage (issue #1 §Judging alignment):
(a) alert → Watch → correct game or channel is S3 + S4, filmed only up to
the proven `searchOpened` outcome; (b) the lineup panel moment is S5,
filmed as the proven full-screen panel.

## PENDING swap-ins — not filmable today

Each PENDING shot replaces the named filmable shot at the same duration
if and only if its dependency lands passing evidence before P2-X12
capture. Until then the filmable version above is what is shot. Nothing
here is filmed speculatively.

| Shot | Replaces | Dependency (owner) | What would change | Honest fallback filmed today |
|---|---|---|---|---|
| P-X09-1 | S3 | X09/X10 live end-to-end run, C3 window 2026-10-23T00:15Z (Integration Engineer) | Alert produced from a live event instead of a replay fixture, still panel-only. Source becomes on-device capture; the replay label drops only for genuinely live values. | S3 as written: labeled replay, clearly labeled as replay. |
| P-X09-2 | S4 | X09/X10 live run 2026-10-23T00:15Z (Integration Engineer); plus `OD-AFC-P2-02` decision (owner, William) | Watch during a live Prime Video game, to whatever outcome the live evidence proves — `gameOpened` only if actually observed, otherwise the strongest observed outcome. Source: **owner camera capture** under OD-AFC-P2-02 = A (marked owner-filmed), or **on-device capture** of the companion UI only under B, with provider video described not shown. UIDs: AFC-PR-029, AFC-PR-030, AFC-PR-031, AFC-PR-048. | S4 as written: on-device capture ending at the proven Prime Video `searchOpened` screen; no provider video claimed. |
| P-X09-3 | S5 | X09/X10 live run 2026-10-23T00:15Z (Integration Engineer) | Panel values updating from live events, still full-screen. Source stays on-device capture. | S5 as written: full-screen panel on current data, stale or unavailable values labeled. |
| P-X11 | S7 segment | X11 Alexa disposition, still open (owner, William, on P2-X11 evidence) | A verified voice interaction could be shown only if X11 verifies an implemented route on the device (AFC-PR-022, AFC-PR-036 pass by not offering voice without one). | No Alexa or voice offer is shown or implied; S7 narration states voice is not offered. |
| P-M13 | S1–S7 (recapture) | P2-L05 final APK and P2-X12 demo capture, M13 (Implementer / Integration Engineer) | All shots are captured on the final submitted APK; no clip from a differing product candidate is used. Same shots, sources, UIDs, and durations. | This plan; no footage exists yet and none is claimed. |

## Never to be filmed (not pending)

These have failing evidence or no evidence. They are not PENDING and no
future evidence in this Lifecycle is expected to reverse them:

- A heads-up notification banner over third-party playback
  (SP-2 FAILS; AFC-PR-015 positive case not unblocked).
- The lineup panel beside playing provider video, picture-in-picture,
  split, or overlay composition (SP-4 FAILS; AFC-PR-041 positive case
  not unblocked). The panel shown is `fullScreen`.
- Live Yahoo lineup data or a Yahoo account flow (SP-6 FAILS; manual
  entry is the active source).
- Provider video captured on-device as if the secure surface were
  readable (RISK-AFC-P2-09).
- Vega running the companion (paused stretch compatibility target only).
- Hardware performance, latency, or RAM claims (excluded by owner
  direction in issue #1).

## Capture notes for P2-X12

- Capture on the final APK only (P-M13). Clips from a differing product
  candidate fail `SEIT-AFC-P2-SUB-02`.
- Replay shots carry a visible replay label for their full duration.
- Owner-filmed shots under OD-AFC-P2-02 = A are marked owner-filmed.
- Confirm the exported video runtime is under 3 minutes before handover
  to the owner for upload. Upload itself is an owner-only action (see
  the [owner checklist](owner-checklist.md)); no agent uploads or posts.
