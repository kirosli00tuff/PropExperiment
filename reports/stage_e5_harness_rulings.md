# Stage E.5 harness v5 rulings (lead)

Every lead ruling on the harness v5 change set: those made in Task A1 (reports/stage_e5_harness_plan.md section 4), on
HarnessBuilder-OpusXHigh's open points (reports/stage_e5_harness_change.md section 7) and on
HarnessReviewer-FableXHigh's findings (reports/stage_e5_harness_review.md). Times PDT, 2026-09-27.

## Rulings made in Task A1 (12:37; plan section 4)
- L-E5-1: the step 2 gate reads the E.5 block (data/pull_step2.py `step2_gate` and its messages), as part of item (c).
- L-E5-2: the 2019-2023 Topstep lead is 30 minutes, the earliest published lead.
- L-E5-3: PBO with one Tier A member is taken over every run confirmation series of the cluster (Tier A and B),
  aligned on the union of window dates, zeros off each trial's dates.
- L-E5-4: the verdict code restates D.1f's functions on funnel/ and does not import strategy/research/.
- L-E5-5: OC-H-excluded trials are listed, not run, and named in the statement as not covered.

## Rulings on the builder's open points (about 13:02)
- **R-A2-1 (O-1, K3).** v5 flattens 14 FX dates (2022-01-17, 02-21, 05-30, 06-20, 07-04, 09-05, 11-24, 2023-01-16,
  02-20, 05-29, 06-19, 07-04, 09-04, 11-23) at 11:30 CT, which K3's frozen FX_FULL_SESSIONS (generated under v4 per
  K3-L-11) lists as full sessions. K3 member code is frozen and not in this stage's scope (its confirmation is deferred),
  so it is not changed. The three tests of tests/test_e4_k3_members_b.py that pin the v4 table are marked
  xfail(strict=True), with the reason stated, and a new test pins exactly this 14-date difference, so any further drift
  fails. The test file is in neither the K3 cluster freeze (member code only, 16 files) nor the harness manifest. Before
  its confirmation run, K3's session must decide whether to amend the table under K3-L-11 or keep it. This is a
  question for the user. K4 and K5 are not affected: every derived 2019-2023 date already has an entry in the energy
  and metals calendars (lead check, about 13:00), so their frozen full-session tables stay consistent with v5.
- **R-A2-2 (O-9).** No test pins the E.5 cap values. The tests pin behavior: the E.5 session id on acct-2; refusal at
  caps of 0.00; only $0.00 quote lines. So B1's config edit leaves the suite green, and v6 differs from v5 only in
  data/config.py.
- **O-2** accepted: an "(observed)" holiday is ordinary (2022-06-20 Juneteenth observed keeps its derived row, like
  2020-07-03 or 2021-12-24's observed closures).
- **O-3** accepted (plan 3a: July 3 unsettled; 2019-07-03 and 2023-07-03 keep F 15:08 on FX, where the FX calendar has
  no halt).
- **O-4** accepted: the plan's test (iv) formula was wrong. `day_rule` applies the year's lead only where no Topstep row
  exists, as it does in 2024-2026, and the code is unchanged.
- **O-5, O-6, O-7, O-10, O-11** accepted as the builder read them. O-7: the published table has 37 rows; the rule
  reproduces 35 of the 36 in its domain.

## Rulings on HarnessReviewer-FableXHigh's findings (reports/stage_e5_harness_review.md; 0 BLOCKING, 2 SHOULD FIX, 10 NOTE)
| Finding | Ruling | Fix |
|---|---|---|
| SF-1 DSR with a one-series variance set is silently undeflated | Accepted | DSR is undefined, and fails, when the variance set has fewer than 2 series; known-answer test |
| SF-2 the blanket strict xfails on K3's pin tests mask other drift | Accepted (replaces R-A2-1's markers) | Precise assertions: every pinned source sha256 as before, except rules/sessions.py at v5's literal sha256; the generator's output differs from the frozen module exactly by the 14 R-A2-1 dates; the rule test holds except on them |
| N-1 the 2019 lead covers the whole calendar year (equity F on 2019-01-21, 2019-02-18 moves) | Accepted as fact, no code change: no store holds a bar before 2019-05-06 | Docstring states it |
| N-2 2019-07-03 and 2023-07-03 keep F 15:08 in every group | Kept (ruling O-3: the rule cannot settle July 3, so no row is guessed). Two dates in K4/K5's windows; the least restrictive reading, recorded for the user | None |
| N-3 PBO alignment on every run trial's union | Kept (O-5); immaterial with one Tier A trial (K4, K5) | None |
| N-4 an undefined PBO reads as a failed step | Accepted | "no edge (pbo undefined)" / "(dsr undefined)", with the reason carried |
| N-5 unknown vehicle ends in a traceback | Accepted | Named VerdictRefusal |
| N-6 unit string and window bounds unchecked | Accepted | Two refusals in `_series` |
| N-7 ENTRY_MODULES does not name the verdict module | No change (L-E5-4): every import is a listed harness file | None |
| N-8 closed label vocabulary, freeze ordinals | Informational: the list builder uses exactly these | None |
| N-9 a trial can be "null" and "edge candidate, composite pending" at once | The cluster statement stays "null" (eps_X is the bar; NULL_CRITERIA_E 2 allows a real edge below it); the verdict file and the return name any such trial in the same sentence | None |
| N-10, N-11, N-12 | No change | None |
The fixes touch screening/stage_e_verdict.py, rules/sessions.py (docstring), tests/test_stage_e_verdict.py and
tests/test_e4_k3_members_b.py. After them, the manifest is rebuilt (v5), the K4 and K5 replays are rerun under v5
exactly, and the full suite runs before the commit.

## Task A4: the v5 manifest (13:40; re-checked after the 13:50 crash)
- `python -m screening.harness_freeze build` on the fixed tree: reports/stage_e2b_harness_freeze.json, 1,037 files,
  sha256 **ba925a97854efdc61a8a20641af10cc0de0be472a634dcb3b8bd637259bba0cd**; `verify --expected` OK (13:40 and again
  13:53 after the reboot). Against v4 (82ae8536..., HEAD): added screening/stage_e_verdict.py,
  tests/test_stage_e_sessions_holidays.py, tests/test_stage_e_verdict.py; changed data/config.py, data/pull_step2.py,
  rules/sessions.py, tests/test_e2b_pull_step2.py; nothing removed; header fields created_pdt and head_at_creation.
- The K4 and K5 research replays were rerun under v5 exactly (13:42-13:46; reports/stage_e5_replay_k4_v5.md,
  reports/stage_e5_replay_k5_v5.md): 25/25 and 23/23 files equal E.4's apart from harness_sha256, created_utc and the trip
  files' record_sha256. The reviewed replays under the pre-fix tree (b720c5aa...) are reports/stage_e5_replay_k4.md and
  _k5.md; the fixes after the review touched only the verdict module, a docstring and tests, none of which a research run
  executes.
- tests/test_e2a_rules.py and tests/test_e4_k3_members_b.py changed too; neither is a manifest file (not in TEST_PATTERNS).
