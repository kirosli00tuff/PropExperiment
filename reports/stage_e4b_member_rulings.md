# Stage E.4 Part 2 (K5), Task 4: the lead's rulings on the K5 fidelity audit

Lead: Opus 5.5 (xhigh), 2026-09-27. Audit: reports/stage_e4b_member_audit.md Part 1 (MemberAuditor-K5-FableXHigh,
fable xhigh, 05:23-05:43, which wrote none of the code, specs or tests): BLOCKING 0, SHOULD FIX 1, NOTE 9. All seven
members implement their frozen entries and nothing more; every table recomputes exactly from its sources (AM 1,802,
PM 1,788, no-auction 14 PM-only, FOMC 57 = E.3's table, full sessions 1,784); C10's 5-hour-week table matches zoneinfo
in all eight years; every no-auction day rests on a dated advance notice read from the capture actually served; F-7
holds (k5/ovr.py differs from the audited k4/ovr.py only in the derived clock, the calendar table and the derived value
floor); the auditor agrees with every lead reading; 52 of 56 mutants killed (2 equivalent, S-1, and one probe that only
added an unused constant).

## SHOULD FIX

**S-1. The CP2 opening-range test does not pin the range's end** (tests/test_e4_k5_members_a.py:587-599; the mutant
RANGE_MINUTES = 14 survived). Ruling R-K5-1: accepted, test-only. MemberCoder-A-OpusXHigh (resumed) added a sell-side
pair and an assertion `cp2.RANGE_MINUTES == 15`; no member module changed (section below). The K4 twin test
(tests/test_e4_k4_members_a.py, committed with the K4 freeze e0ccf63) likely shares the gap. K4's cp2.py is correct
(both audits; its rule body equals K5's); the committed K4 test is left as it is and the gap is reported in the returns
for the user.

## NOTE

| Note | Finding | Ruling |
|---|---|---|
| N-1 | cp2's resend of a refused 75-bar exit untested | as K4 N-4: unreachable in practice. No change |
| N-2 | D9.7 tests use a test-only rules class (MGC, MHG have no hard limit) | as K4 N-3: adequate. No change |
| N-3 | confirmation-window evidence for the IBA calendars rests on PDF metadata, one 2019 capture served from 2020, start times 2020-2025 not checked page by page | K5-L-01: a Tier A preauc or pmfix confirmation session re-checks 2019-2024 first. No change |
| N-4 | two equivalent mutants survive (cp1 Globex-bar date half-check; ovr is_flat vs position) | not defects. No change |
| N-5 | METALS_FULL_SESSIONS equals K4's energy table | expected (the two calendars coincide). No change |
| N-6 | Task 6 event-set arithmetic (preauc 307 AM days less halts and blackouts; pmfix 305 PM days ...) | passed to Task 6 |
| N-7 | _event_common.py:86: no exit sent for a position on a date without a plan | unreachable; the engine's flatten covers it. No change |
| N-8 | CP2's "75 minutes after the fill" vs "75th bar after the entry-intent bar" differ when D9.5a defers a fill | the code counts from the fill, as D6 governs (E.3-L-07). No change |
| N-9 | the 2019 IBA calendar is a 2020 capture | the 2019 half days rest on LBMA's dated 2019-12-13 notice; the calendar is corroboration. No change |

## The fix (R-K5-1)

MemberCoder-A-OpusXHigh (resumed) added a sell-side pair on both roots to test_cp2_the_opening_range_is_o_to_o_plus_15
(a close of B-7 at O+15 sells, B-6 does not) and an assertion `cp2.RANGE_MINUTES == 15` beside the buffer literal. The
mutant RANGE_MINUTES = 14 now fails the range test on both roots and the literal check (in memory, restored). Its
reference command ended `238 passed in 3.12s`. Against reports/stage_e4_briefs/k5_files_pre_audit.sha256 exactly one
file differs: tests/test_e4_k5_members_a.py (now 73636c9555d9c97bef589316c7d24295d0c48af885f033932c04f9879a7226cb);
every member module equals the audited hash.

Cluster freeze (write_cluster_freeze): reports/stage_e_k5_member_freeze.json, sha256
1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655, 11 members; load_cluster_freeze + verify_cluster_code OK.
