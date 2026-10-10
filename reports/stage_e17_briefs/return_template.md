# Stage E.17 return: C1 STOPPED at C10; the base-rule batch H1-H5 run once, all five FAIL

Prompt docs/prompts/STAGE_E.17.md (V24-V30; V30 amended to a $124.00 budget). Lead Opus 5.5 xhigh, Claude sessions
0dcecb5d (18:34-19:38) and c71b1fb9 (19:41 on; resumed after the first ended), usage logged under 0dcecb5d. All times
PDT, from `date`, file times or logs. Stage start 18:34 on 2026-10-09.

## 1. Verdict summary

**C1: STOPPED.** Its single evaluation stopped at guard C10: g17_mbt applies on 0 NG rows in 2010-2019 (87 and 84
in E.12). MBT did not exist then, and the freeze has no exemption for a leg that is n/a by design. No T1 or T2
statistic exists. Fable verified the stop. The attempt is closed and not rerun.

**E16-H1..H5: all five FAIL** (base case, Holm 0.05, N 478). Fable recomputed every number:
{{H_VERIFY_SUMMARY}}.

| Test | Mean (risk units) | t | p | n |
|---|---|---|---|---|
| H1 | -0.161 | -20.0 | 1.0 | 3,380 |
| H2 | +0.344 | +1.52 | 0.068 | 56 |
| H3 | -0.015 | -0.26 | 0.60 | 405 |
| H4 | -0.048 | -6.7 | 1.0 | 3,381 |
| H5 | -0.149 | -1.46 | 0.93 | 3,400 |

- Holm rejects none, DSR is about 0, and the stress and 1.5 x slippage cases are worse.
- Windows: 2010-07..2024-02, with TN from 2016-01, RTY from 2017-06 and HE from 2017-07.
- Fallback window 2019-05-06..2024-02-29, not funded: YM, HG, 6S, 6J, 6A, 6B, 6N, ZM, ZW, 6C.

**Bought:** C1's six roots for $57.817332 and 11 extension roots for $64.038166, a total of $121.855498 of the
$124.00 budget. About $3.14 is left of $125.

**Harness:** v11 ba1ce99672b7e5bbb33f0cfabb89ba618d207d701348da1b1681ecfa7d932292, v12
ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32. **N = 478.**

**Meaning:**
- C1 says nothing about the NG hypothesis; a rerun needs a new pre-registration.
- No base rule has a net edge at D8 cost. H1's gross is about a quarter of its cost.
- There is no holdout-2 read and no meta-labeling (V28).

## 2. Guardrail evidence

No TopstepX call, credential or file under live/ or ops/ was touched. REGISTRATION.md stayed 0 bytes. Holdout-2, the
embargo, MES's sealed stores, the research window and anything from 2026-06-21 were not read by any test. No key was
printed or logged. Nothing was pushed. Every Databento spend followed a logged quote checked by the guard (the sum of
the run's own ledger lines; never the tool's JSON, never --retry-failed).

**Start checks, 18:37 on 2026-10-09** (reports/stage_e17_briefs/start_checks.txt; harness v10):

```
{{START_CHECKS}}
```

Start suite (18:37:38-18:54:28): `6815 passed, 2 skipped, 3 xfailed, 54 warnings in 1007.46s`, rc=0.

**After C1's purchase, 22:41** (reports/stage_e17_briefs/post_c1_purchase_checks.txt; harness v11). The one freeze
inputs mismatch is the harness manifest itself (v10 -> v11), which C1's freeze section 11 allows:

```
{{POST_C1_CHECKS}}
```

**After the base-rule purchase, 01:27 on 2026-10-10** (reports/stage_e17_briefs/post_h_purchase_checks.txt; harness
v12):

```
{{POST_H_CHECKS}}
```

**End checks** (reports/stage_e17_briefs/end_checks.txt; harness v12):

```
{{END_CHECKS}}
```

End suite: {{END_SUITE}}

**Order of events (PDT):**

| Time | Event |
|---|---|
| 18:34 (10-09) | Prompt read; context files read |
| 18:35-18:38 | Planning chat: budget $122.50, then $126.30, then FINAL $124.00 (commit 8e5707c) |
| 18:37 | Start checks pass; start suite 18:37:38-18:54:28, 6815 passed |
| 18:37:58 | C1's freeze verified by script (ALL_OK: 43 inputs, freeze unchanged since 1680982, E.12 state, model, M1, q, v10) |
| 18:54:50-19:06:57 | Fresh C1 quote under v10: 642 of 642, 0 failed; guard: $57.742330 from the run's own lines |
| 19:07-19:28:52 | v11 (two caps and pinning tests); Fable review APPROVE 19:10-19:25; suite 6815 passed; commit a21d82d |
| 19:29:06 | C1 registered, N 471 -> 473 |
| 19:29:15-22:40:40 | C1 buy, 642 chunks (the first process died with the Claude session at 19:37:46 mid-chunk; resumed 19:42:33) |
| 22:41 | Post-purchase checks pass |
| 22:41:36-22:46:57 | Six ext2010 stores built |
| 22:47 | C1 store and calendar hash files written (sha256 into STATE) |
| 22:47:44 | C1 run-once marker; 22:48:44 verdict STOPPED (C10) |
| 22:51:12 | Commit 558a7ce "E.17 C1 evaluated" |
| 22:51-23:08 | Fable verifies C1's STOP: VERIFIED WITH NOTES |
| 22:51-23:16 | V12Coder writes v12 in a worktree; applied on main 23:16 |
| 23:18-23:35 | Fable v12 review: APPROVE WITH FIXES (F-1 fixed 23:35) |
| 23:36:08-00:01:54 | Fresh ext2010h quote: 1993 of 1993, 0 failed; guard: $153.965349 |
| 00:02-00:03 (10-10) | A3 selection and fallback list written (STATE) |
| 00:04-00:29:51 | Caps into v12; Fable caps follow-up APPROVE (00:07-00:12); suite 6916 passed; commit d30f50c |
| 00:30:15 | E16-H1..H5 registered, N 473 -> 478 |
| 00:30:28-01:26:30 | Base-rule buy, 933 chunks in 4 processes over disjoint roots |
| about 01:21 | The user: "theres 125 total on the account. use all if needed" (no change: ruling B-2) |
| 01:26:58 | Post-purchase checks pass |
| 01:27:13-01:30:28 | Eleven ext2010h stores built |
| 01:31 | Run manifest written (sha256 into STATE); pre-marker dry check clean |
| 01:31:39-01:39:40 | H1, H2, H3, H4, H5 once each (each marker written before any bar is read) |
| 01:39:53 | Verdict written |
| 01:40-{{H_VERIFY_END}} | Fable recomputes every H verdict number |
| {{END_TIME}} | End checks, end suite, final commit |

## 3. Results per step

{{RESULTS_PER_STEP}}

## 4. Delegation record

| # | Agent (description) | File | Model | Effort | Start | End | Tokens | Result |
|---|---|---|---|---|---|---|---|---|
{{DELEGATION_ROWS}}

## 5. Verification

{{VERIFICATION}}

## 6. Open choices (every decision the lead made on its own, with the reason)

{{OPEN_CHOICES}}

## 7. Decisions for the user (the lead's recommendation first)

{{DECISIONS}}

## 8. Session cost

{{SESSION_COST}}
