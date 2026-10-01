# Stage E.8 Task 4: the lead's rulings on the K6 fidelity audit

Lead: Opus 5.5 xhigh, 2026-10-01 01:57 PDT. Audit: reports/stage_e8_member_audit.md Part 1 (MemberAuditor-K6-FableXHigh,
01:28-01:56 PDT): BLOCKING 0, SHOULD FIX 0, NOTE 11. Every reading in reports/stage_e8_member_specs.md sections 9 and 10
was agreed. No member file and no test file changed after the audit: all 21 files equal
reports/stage_e8_briefs/k6_files_pre_audit.sha256.

| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| N-1 CP1 grain late-open date with a missing 08:30 bar takes 08:31 | NOTE | R-T3-1: the code stands; it is K6-L-01's clause ("the earliest bar of trade date d at or after 19:00 CT on the calendar day before d") applied once more. An exact-08:30 reading would import K6-L-02's livestock text and need a late-open table the member cannot hold. | Specs only: section 1 row and K6-L-01 now say "normally the 08:30 bar of d, and the first later bar of d if it is missing, by the same clause". Flag for the user stays (K6-L-01). |
| N-2 limitcont's event is the proxy's event, not the official settlement's | NOTE | R-T3-2: accepted as a label. | Both K6-limitcont-01 trials carry "settlements by the D9.7 proxy (one bar's close); official settlements not tested" beside section 10's two labels. |
| N-3 cp2.py's F_REGULAR_CT literal (coverage windows only) | NOTE | No action: inert for trading, pinned by tests, the template forbids importing rules.sessions. | none |
| N-4 survivor B-LC-16 (window start not floored) | NOTE | No action: equivalent on every livestock window. | none |
| N-5 the coders' ten surviving mutants | NOTE | No action: each equivalent, checked by the auditor. | none |
| N-6 tests that pin only a literal | NOTE | No action: 16 of 17 pin-first mutants are killed by a trade; the exception is a declaration (CP2's window end). | none |
| N-7 "a contract without a limit on d-1" moot only while the roll keeps the vehicle out of its last two trading days | NOTE | R-T3-3: accepted; the dependence is stated. | Specs section 5 row amended (R-1b-4). |
| N-8 at 1 ZS the D9.7 lower stop lies beyond the $2,000 MLL | NOTE | Recorded for the return (harness and sizing observation, not a member defect). | none |
| N-9 fresh-state starts (limitcont first three livestock dates, crushgap first grain date, CP3 warm-up) | NOTE | Recorded for the return beside the event counts. | none |
| N-10 unreachable ValueError paths on non-integer units | NOTE | No action: unreachable with the frozen tables; a changed table stops the run rather than trading. | none |
| N-11 the auditor's tmpfs incident | NOTE | Recorded (STATE 01:37; return section 4). No repository file was touched; pre-audit hashes verified at the end. | none |

Readings ruled on by the auditor at the lead's request: K6-L-01 (stands, wording per R-T3-1), K6-L-06 (the proxy is the
frozen input by the 01:52 ruling and D9.7 line 542; not unimplementable; label per R-T3-2), K6-L-07 (agreed), K6-L-08
(agreed), K6-L-03 (agreed), R-1b-2 (agreed; SER-9736 quote verified against the saved page).

Nothing is unimplementable as frozen. All 27 declared trials proceed to the freeze.
