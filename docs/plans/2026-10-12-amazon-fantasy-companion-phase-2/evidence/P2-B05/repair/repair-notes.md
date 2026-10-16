# P2-B05 repair notes (AFC-B05-R01..R06)

Base: c49fb183996a4ab9eccb5ff2b8fe2471a5e4e660. Frozen B05T files untouched
(verify_receipt PASS). AFC-B05-A01 left as remaining risk per packet.

- R01: possession and starter teams canonicalize to ESPN abbreviations at the
  policy boundary (numeric ESPN teamParticipant id map + common aliases).
- R02: a match carrying a cursor revises the stored alert (keeping its type)
  even when the correction removes the original trigger; new-alert gates are
  bypassed for revisions.
- R03: pending returns a revision-aware progress token (cursor, suffixed
  ~r<revision> above revision 1) and re-serves an alert at the progress
  cursor when its stored revision is higher; store.list_alerts gained an
  opt-in include_after bound (default unchanged). Envelope id stays the
  alert cursor.
- R04: pending stops before the serialized body exceeds a 60,000-byte budget
  (API limit 65,536) and resumes from the last served alert; held alerts are
  never passed.
- R05: basis is observed-playback only with opt-in plus observation evidence
  on the match or event; otherwise profile-assumption.
- R06: close-game fires once per entry; an observed Q4/OT exit (or a later
  stored alert with a non-close score) re-arms it. Exit tracking is
  in-process (see shortcut comment in alert_policy).

Red-then-green: the six cases in
backend/tests/unit/alert_policy/test_policy_repair_b05.py failed on base
(6 failed) and pass after the fix; frozen alert_policy suite 76 passed in
total; full gate 740 passed, exit 0. The review reproduce.py cases report
EXPECTATION_MET after the fix (its correction_after_cursor case is
time-of-day sensitive: it seeds a 17:00-23:59 UTC game-day window around the
wall clock, so after 00:00 UTC it cannot create its first alert; R03 was
additionally verified with a time-independent variant of the same flow).
