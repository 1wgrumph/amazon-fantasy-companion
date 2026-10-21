# Owner checklist — submission

Slice P2-D05, issue [#50](https://github.com/1wgrumph/amazon-fantasy-companion/issues/50).
Governing criterion: `AC-AFC-P2-SUB-04` (technical plan §Submission).
Submission deadline `T_deadline` is 2026-10-23T19:00:00Z; judge access must
be kept through `T_judge_access` 2026-11-20. The accountable owner for
every row is **William**.

**Agents performed none of these owner actions.** Agent work prepared
material only. No row is marked completed without landed evidence named
in its state cell, and agent preparation is not a legal determination
and does not supply owner approval for any row.

State vocabulary: **Completed** (landed evidence), **Outstanding**
(owner action still to do), **PENDING evidence** (waiting on a named
run or decision).

## Owner-only actions from the technical plan

| ID | Accountable owner | Exact action | Due (before 2026-10-23T19:00:00Z) | Blocks | Current state (evidence) |
|---|---|---|---|---|---|
| OA-1 | William | Q6: stick located, ADB debugging enabled on the local network, model and Fire OS version recorded; P2-X01 reads `getprop` and the owner confirms. | Before P2-X01 dispatch (W1) — met | Every stick slice; RISK-AFC-P2-01 | **Completed.** SP-1 verdict WORKS: AFTKM, Fire OS 8.1.8.5 / API 30, starter installed and launched (`spikes/sp1-device/VERDICT.md`, PR #89). |
| OA-2 | William | Q7: Yahoo application submitted now; if approved, store the client id and secret as SSM SecureString parameters in the dev AWS account and complete the OAuth consent in a browser; after P2-L02 reports the stack ApiUrl, register the deployed /link callback as the Yahoo app redirect URI. | By `T_yahoo` 2026-10-16T19:00:00Z — date passed | Yahoo path only; manual path proceeds (C6) | **Outstanding (approval).** Application submitted 2026-10-16; approval has not arrived and unapproved apps receive 403 from the Fantasy API (`spikes/sp6-yahoo/VERDICT.md`, SP-6 FAILS, PR #100). Manual lineup entry is the single active source. No live Yahoo data is used. |
| OA-3 | William | Q8: AWS Free-plan account created and the named CLI profile `afc-dev` configured on the development host. | Before P2-L02 (W2) — met | Deployed-API cases; local backend work proceeds without it | **Completed.** Backend deployed to the dev account and repeatedly redeployed from `main` with passing deployed smoke (P2-L03 deploys, PR #96; redeploy records PR #104 and PR #107). |
| OA-4 | William | Provider apps installed and signed in on the stick: Prime Video; ESPN; DirecTV Stream (current subscription); YouTube TV if a subscription exists. | Prime Video before P2-X01 first install; others before P2-X03 — past; any addition needed for live runs before 2026-10-23T00:15:00Z | Provider routes without a session are recorded as `accessUnknown` or `appAbsent` | **Completed for Prime Video only; outstanding for the rest.** Prime Video is present and signed in (owner-reported sign-in; SP-3 observed the signed-in home). ESPN, DirecTV Stream and YouTube TV are not installed and are observed `appAbsent`; local broadcast has no carrying app (`spikes/sp3-provider-links/VERDICT.md`, SP-3 PARTIAL, PR #110). Owner decides whether any are installed before the live window; absent apps stay honest `appAbsent` outcomes. |
| OA-5 | William | Authorize the exact public export and visibility change after the W5 history/content review. Apache-2.0 is already selected; its standard LICENSE file is prepared as ordinary agent work (P2-D03), not an unresolved license choice. A secret/path scan alone does not authorize exporting private prompts or profile routes; if the existing history cannot be shared, decide the bounded clean-export/history question first. | W5; prepared for 2026-10-22, before judge access is needed | Public judge access; no public flip without this approval | **Outstanding.** Repository is private. No visibility change, export, or publication has been authorized or performed. |
| OA-6 | William | Review the ESPN unofficial JSON terms for public submission (C3). | Before P2-D04 write-up final; M12 documents due 2026-10-22T16:00:00Z | Final write-up wording (P2-D04) | **Outstanding.** No owner terms determination is recorded in the tree. The write-up must not finalize ESPN wording ahead of this review. |
| OA-7 | William | Create the Devpost project draft, upload the public demo video (YouTube or Vimeo), and submit with the Fire TV track and AWS Builder fields before the deadline; keep judge access through 2026-11-20. | Before 2026-10-23T19:00:00Z; judge access through 2026-11-20 | The submission itself | **Outstanding.** The Devpost draft is NOT STARTED (issue #1 readiness table: empty project list). No video exists yet; capture is P2-X12 on the final APK. No agent creates, uploads, or submits anything. |
| OA-8 | William | Authorize each release publication (P2-R1 through P2-R5) and any external feedback sending. | At each technical-wave release checkpoint; final release authorization before 2026-10-23T19:00:00Z | Each release stays a prepared draft until authorized | **Outstanding.** No owner release-publication or external-feedback authorization is recorded in the tree. Agents prepare drafts only; nothing is published or sent. |
| OA-9 — not needed | William | Camera capture of the TV screen for protected-video demo shots (RISK-AFC-P2-09). | — | — | **Does not apply.** `OD-AFC-P2-02` resolved to option B on 2026-10-20 (DEC-AFC-OD-P2-02-B-20261020): the demo uses companion-UI captures only. Provider video is not shown in the demo, to respect copyright. |
| OA-10 | William | Device linking in its settled form (DEC-AFC-SD-048, TV code only): **no passphrase is stored anywhere.** When a linked device is needed — P2-L02 link smoke, the X09/X10 live runs, or a data-clearing rollback — confirm the code shown on the TV on the `/link` page from a phone or browser. Confirm only a code shown on your own TV. | On demand; next expected for the live runs starting 2026-10-23T00:15:00Z, if linking is needed there | Deployed link confirmation; linked-device live runs | **Settled form; confirmation outstanding on demand.** The code-only form is decided and implemented (short code expiry, one-time confirmation; PR #68). Owner confirmation is performed when a linked device is needed; agents cannot confirm codes. |
| OA-11 — optional | William | Optionally supply a release signing keystore for the submitted APK. | Before P2-L05 final APK build (W5, M13) | Nothing hard: without it, the debug signing configuration is used | **Outstanding (optional).** No keystore has been supplied. P2-L05 proceeds with debug signing unless the owner supplies one; the APK sha256 and Reverify record are P2-L05 evidence either way (AC-AFC-P2-APK-01). |

## Owner-only actions from the plan §Exclusions

These restate the owner boundary from the technical plan §Exclusions
(C9). Several are the same duties as rows above, seen from the exclusion
side; they are listed so none is missed. Agents perform none of them.

| ID | Accountable owner | Exact action | Due | Blocks | Current state |
|---|---|---|---|---|---|
| EX-1 | William | Credential creation or retrieval (any service). | Whenever a slice needs credentials, and in any case before 2026-10-23T19:00:00Z where needed for submission; none may be created by agents | The dependent slice only | **Outstanding as a standing boundary.** Agents hold no credentials and create none. The Yahoo credential step is covered in the table above. |
| EX-2 | William | AWS plan changes. If any AWS action would require a Paid plan, a paid service, or a payment-method change, work stops for an owner decision (RISK-AFC-P2-07). | Before any such action could proceed, and in any case before 2026-10-23T19:00:00Z where needed for submission | The dependent AWS action | **Outstanding as a standing boundary.** No plan change has been requested or made; the dev account work to date ran on the existing plan. |
| EX-3 | William | Repository visibility flip — the decision side of the exact-surface public export approval in the table above. | W5, before judge access | Public judge access | **Outstanding.** The repository remains private. History is not rewritten and private material is not published by agents under any scan result. |
| EX-4 | William | License choice. | Settled | Nothing | **Completed as a decision.** Apache-2.0 is already selected. Preparing the standard LICENSE file is agent work (P2-D03); it is not an open owner choice. |
| EX-5 | William | Release publication (same duty as the per-wave release authorization above). | Each release checkpoint | Each release stays a draft | **Outstanding.** No publication performed by agents. |
| EX-6 | William | Video upload (same duty as the demo-video part of the Devpost row above). | Before 2026-10-23T19:00:00Z | The public-video requirement | **Outstanding.** No video exists yet (P2-X12, M13); no upload performed by agents. |
| EX-7 | William | External feedback sending (to Amazon, Yahoo, the NFL, or anyone else), including the Scribe's prepared feedback and friction log. | Before any sending, and in any case before 2026-10-23T19:00:00Z where the sending is needed for submission; separately authorized each time | Feedback stays prepared, unsent | **Outstanding.** Feedback material is prepared in-repo only (P2-SCR1); nothing has been sent. |
| EX-8 | William | Devpost submission (same duty as the submission part of the Devpost row above). | Before 2026-10-23T19:00:00Z | The entry itself | **Outstanding.** Draft NOT STARTED (issue #1). No submission action performed by agents. |

## Owner decisions this checklist needs

- **`OD-AFC-P2-02` (protected provider video capture): decided, option
  B** (owner, 2026-10-20, DEC-AFC-OD-P2-02-B-20261020). The demo and
  evidence use companion-UI captures only, with provider video
  described, not shown, to respect copyright. Option A (owner filming
  the TV) was declined, so the OA-9 camera row does not arise.
- **Alexa disposition (X11)** remains open. Until a voice route is
  implemented and verified on the device, voice is not offered
  (AFC-PR-022, AFC-PR-036) and the demo shows no voice interaction.

## Hackathon-admin items — unresolved, owner only

Each item below is **unresolved / outstanding**. Nothing in this
repository, and no agent preparation, is a legal determination, and
none of it supplies owner approval. William decides each item; the
current facts are recorded only as issue #1 states them.

| Item | What William must settle | Current state |
|---|---|---|
| Eligibility and participation terms, including affiliation and conflict clauses | Confirm full eligibility under the event's current official rules — participation terms and every affiliation/conflict clause. | **Unresolved.** Issue #1 records: Devpost registration confirmed, adult U.S. residence owner-confirmed, employer corrected to AMD (the earlier Amazon-employment statement is retracted and is not a disqualification). No organizer eligibility ruling exists; registration is not one. The remaining affiliation/conflict clauses are unexamined by any determination. |
| Ownership and third-party rights, including any applicable employment/IP agreement | Confirm project ownership and third-party rights; review any applicable employment or IP agreement for its effect on the entry and its license. | **Unresolved.** Issue #1 records that no employment/IP agreement has been reviewed. No rights determination is claimed. |
| Individual or team participation, and authorized representative | Choose individual or team entry, and name the authorized representative if the chosen form requires one. | **Unresolved.** Issue #1 lists this choice as an open checklist item; no choice is recorded. |
| Devpost draft URL | Create the project draft and record its URL for the submission record. | **Unresolved — NOT STARTED.** Issue #1 records an empty project list; no draft URL exists to record. Creation is part of the Devpost row above and is owner-only. |

## Live-window dependencies affecting states above

- The X09/X10 live end-to-end run is scheduled in the C3 window
  starting 2026-10-23T00:15:00Z. Live `gameOpened`, live alert
  delivery, and live panel updates have no passing evidence until
  that run lands; demo shots depending on them are PENDING in the
  demo plan. Device-link confirmation may be needed on demand there.
- The final APK (P2-L05) and demo capture (P2-X12) are M13. The
  optional signing row above is due
  around those slices, before the owner's upload and submission.
- Vega is PAUSED by owner direction (2026-10-20). It appears in
  submission material only as a paused stretch compatibility target
  with stated limits, never as delivered (RISK-AFC-P2-14), and no
  owner action in this checklist depends on it.
