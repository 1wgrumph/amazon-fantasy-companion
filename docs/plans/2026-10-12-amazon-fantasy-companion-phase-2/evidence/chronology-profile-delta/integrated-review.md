# Integrated Phase 2 review package

Outcome: **NEEDS_MORE_EVIDENCE** for full-page browser inspection; the requested
chronology and profile revision is complete and mechanically verified. No owner
approval, product execution, publication or runtime acceptance is claimed.

## Candidate identities

- Package digest: `e02871029b86f8d0f2fdef6617feb989413883cc6bdb70e5dec3a47e64c86da8`.
- Complete frozen profile: `7d501eb8c103831a38c50d237b5d1e2e015a564b9ade8aef09a32dfc39b26ab1`.
- Bearing route/capability digest: `11c4478edb7b0c94da196cdc8be2317f498378724ae041bde0c108832b1e2036`.
- Tracking payload: `f0b8d5bf26d3959948e65960fc2b06525a96f964ab3454633eb6c1aaeab9acdb`.
- Implementation bytes: `ae2b224ceb242d6a45e8d0564feee1c93e79e555e0d4e2ca045b8ed4b3c64c9a`.
- Manifest bytes: `2453404c09efbb82fcaa09c3d2d4baa338c2b12496c16c77b1a8667cb87e8c6f`.
- Authoring baseline: `14120d1d24e71c95e50cbc7a2e4edec1a5d7f5a7`; the pushed PR15 commit records the final Git candidate.

[Open the generated Manifest](../../amazon-fantasy-companion-phase-2-dod-manifest.html).
All individual hashes and command exits: [parent verification](parent-final-verification.json).

## Milestones in order

Milestone numbers organize tracking. Ready work overlaps where its dependencies
and leases permit; they do not replace the five technical waves/releases.

| Milestone | Outcome | Issues in order | Due UTC |
|---|---|---|---|
| M01 | Day one: tracking, verification guidance and product gate | P2-L01, P2-D01, P2-G01 | 2026-10-14T20:00:00Z |
| M02 | Fire TV stick qualified and backend skeleton with device linking | P2-X01, P2-B01 | 2026-10-14T20:00:00Z |
| M03 | Panel spike, TV app scaffold and release v0.1.0 | P2-X04, P2-A01, P2-R1 | 2026-10-14T23:00:00Z |
| M04 | Stick spikes and Thursday Oct 15 live checks | P2-X02, P2-X03, P2-X07, P2-X05 | 2026-10-17T01:00:00Z |
| M05 | Feed ingest, lineup sources and first AWS deploy | P2-B03, P2-L02, P2-B02 | 2026-10-17T01:00:00Z |
| M06 | Profile settings, lineup-source verdict and release v0.2.0 | P2-A02, P2-X06, P2-R2 | 2026-10-17T01:00:00Z |
| M07 | Event matching, alert policy and panel service | P2-B04, P2-B05, P2-B07 | 2026-10-18T09:00:00Z |
| M08 | Provider resolver, TV alerts and Watch | P2-B06, P2-A03, P2-A04 | 2026-10-18T09:00:00Z |
| M09 | TV lineup panel and integrated backend deploy | P2-A05, P2-L03 | 2026-10-18T11:00:00Z |
| M10 | Sunday Oct 18 live end-to-end and release v0.3.0 | P2-X09, P2-R3 | 2026-10-19T12:00:00Z |
| M11 | Monday Oct 19 hardening, conditional Alexa, spec revision and release v0.4.0 | P2-X10, P2-X11, P2-D02, P2-R4 | 2026-10-21T23:00:00Z |
| M12 | Submission documents and developer feedback | P2-D03, P2-D04, P2-D05, P2-SCR1 | 2026-10-22T16:00:00Z |
| M13 | Release candidate v1.0.0, final APK, demo capture and handover | P2-R5, P2-L05, P2-X12 | 2026-10-23T12:00:00Z |

Counts: 3,2,3,4,3,3,3,3,2,2,4,4,3. Every issue is assigned once; 13 TDD pairs
retain shared issues. X05 supplies CP-X05-HIST to R1 in M03 and B02 in M05
before its M04 live-verdict closure. X11 stays conditional.

## Acceptance to evidence

| Objective | Status | Evidence |
|---|---|---|
| 1. Full profile migration; preserve capabilities, holds and budgets | Complete | [full freeze](../profile-migration-041/profile.json), [migration receipt](../profile-migration-041/receipt.json), [review continuity](review-continuity.json); both PI launches carry contributor-mode on |
| 2. 39 issues in 13 chronological milestones, 52 slices and 13 pairs | Complete | [tracking payload](../github-work-items/github-work-items.json), [conservation](conservation.json), [sequence checks](tracking-proposal-checks.json); duplicate/missing/out-of-range negatives reject |
| 3. Full scope, dependencies, assembly and timing preserved | Complete | 268 parent checks; 63 active+3 withdrawn register UIDs, 100 proofs, 70 commands, 121 edges, 44 steps, five waves/releases; [IE32 checks](ie-check.json), [TE22 checks](te-check.json); no dates or scope cut |
| 4. Canonical artifacts, authority, generator, bodies and Manifest reconciled | Complete except browser check | [RE closure](requirements-delta-closure.json), [PI final](../../specialists/pi-chronology-041-final-receipt.md), [final terminology correction](release-condition-label-receipt.json), native schema/freeze/renderer PASS; [visual gap](visual-evidence.json) |
| 5. Push safe delta and present one integrated owner gate | Draft PR15; approval pending | Repository gate and hosted checks must name pushed head; PR15 remains draft. No tracking creation or product execution |

## Verification and limits

- Requirements: four changed local rows closed. MS-01 received its bounded semantic correction; correction_rounds2 stays spent. Full103-row snapshots and native named-change/reference receipts are preserved.
- Parent conservation: 268 checks PASS; duplicate issue, missing issue and invalid milestone-size negatives reject. The final additional check requires generic release dependency labels to say technical wave; all40such labels changed and every other implementation value stayed equal.
- Native1.1.7 schemas and plan-package freeze: PASS, zero findings. Renderer --check: PASS. HTML source inspection confirms13milestones,52slices and7embeddedSVGs.
- Repository gate: `TMPDIR=/var/tmp/az bash tools/ci/gate.sh`; final output is [repository-gate.txt](repository-gate.txt).
- Authorization: native owner-stop negative cases reject unapproved tracking creation, including an effective-bit-only test copy; [boundary receipt](publication-boundary.json).
- Privacy: one absolute home path in a new PI evidence metadata field was normalized before publication; original hash/private-copy provenance retained in [sanitization record](sanitization-provenance.json). No result or verdict was changed.
- Historical review1/1 and repair1/1 remain spent; Opus chronology review is separate and completed. No new independent review or assurance is claimed. The native historical review-continuity check is not a review of current bytes.
- Every runtime proof remains not_run. OCR delegation excludes Markdown; native tools/APK semantic Reverify and external S8 ledger remain future gaps. Dormant fallbacks were not invoked; exact selected profile was preserved, with [parent dispositions](parent-dispositions.json).

## Remaining visual evidence and schedule risk

CUA reported IAB unavailable and an empty browser inventory twice. Full-page
layout, phone width and browser screenshots are NOT_RUN, not PASS, and the
owner has not accepted that gap. The changed wave SVG was rendered with the
installed librsvg decoder and visually inspected without clipping; this is not
a browser screenshot. A browser connection or explicit owner disposition is
still needed for that verification item.

The full24h X04 timebox can overrun R1 at2026-10-14T23:00Z because A01 review
must follow it. Latest X01 start stays2026-10-14T03:15Z; no deadline moved.
Final-ready stays2026-10-23T12:00Z and submission deadline19:00Z.

## One integrated owner gate

Approve this exact planning/tracking package or request changes, with explicit
disposition of the visual gap and the existing timing risk. Approval may permit
PR15 merge and P2-L01 tracking setup after landing; it does not authorize
product execution, credentials, public export or release publication. All
specialist children are finished; resume from the current handoff without
repeating the completed Opus review or changing the frozen routes.
