# Stage E.6 Task 4: lead rulings on the K7 fidelity audit

Lead: Opus 5.5 (xhigh), 2026-09-27 22:45-22:50 PDT. Audit: reports/stage_e6_member_audit.md Part 1
(MemberAuditor-K7-FableXHigh, 22:15-22:43 PDT): BLOCKING 0, SHOULD FIX 1, NOTE 8; 104 of 105 mutants killed;
every table recomputed equal (CRYPTO_FULL_SESSIONS 1782, VENDOR_DEGRADED 11, MBTX 60); the 17 files matched their
pre-audit hashes (reports/stage_e6_briefs/k7_files_pre_audit.sha256) at the audit's start and end.
Earlier rulings in this stage: R-1b-1..R-1b-4 (reports/stage_e6_member_specs.md section 9) and the coders' questions
(reports/stage_e6_STATE.md, Task 2 lines).

| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| F-1 no event test tells the t-1 bar's close from its open; mutant `ec-end-close` survives | SHOULD FIX | R-T3-1: accepted; the code is right (_event_common.py:203), the tests do not pin what they claim | test-only: MemberCoder-B gives the end bars in rev2h's B1_UP and b2() and montrend's FIRST_UP an open of the opposite sign to their close, and confirms `ec-end-close` is killed; no file under strategy/ changes |
| F-2 the entry-bar instrument gate is a K7 narrowing, and the rev2h spec rows named the entry bar among the target's bars | NOTE | accepted: the code's behaviour (entry bar gates the entry only) is the reading; wording corrected | specs S0.9, section 5 rows "Decision 10:30" and "Decision 12:30", section 8's adoption line and K7-L-06 amended (22:47); no code change |
| F-3 under the per-bar flag, confirmation Mondays 2021-12-06 and 2022-01-03 would trade on flagged Sunday-evening bars | NOTE | K7-L-03's same-date mapping stands (the program's defined term; the auditor agrees); the two Mondays are named to the user | reports/E.6_RETURN.md sections 6 and 7 |
| F-4 K7-L-12 did not name section 7 item 13 (b), (c), (d), (h) | NOTE | accepted | K7-L-12 amended: (b) moot, (c) a confirmation-session check, (d) MBT is DCB_ONLY in rules/price_limits.py (default NO_LOCK_LIMIT), so D9.7 does not fire, (h) moot |
| F-5 K7-L-05 should state its consequence | NOTE | accepted | K7-L-05 amended: the trial adds 1 to N with a certain screen fail, conservative for the other five |
| F-6 literal windows (expiry 05:00 / 11:00; CP2's F 15:08) duplicate derived values | NOTE | no change: both match S0.12 and are pinned by tests; rules.sessions is not an allowed member import (K4 precedent) | none |
| F-7 2024-07-03: data/calendars/crypto.py has no early halt, rules.sessions flattens MBT at 11:30 | NOTE | no change here (holdout-2, outside every K7 window this stage reads); CRYPTO_FULL_SESSIONS already removes it (K3-L-11) | flagged for the confirmation and holdout sessions (return section 7) |
| F-8 (a) a montrend booked-forward test passes on the weekday check alone; (b) no port test feeds a weekday 16:00-16:59 CT bar of d-1 | NOTE | no change: (a) the table fact is pinned separately (events.py:297); (b) the code path is exercised by the Friday 16:02 weekend bars | none |
| F-9 coverage windows are measured on every research date (E.3-L-17) | NOTE | expected; the interface has no per-date condition; a coverage failure can only exclude a member before screening | read the runner's coverage output with it in mind |

No member module changes after the audit, so the frozen member files equal the audited ones.
