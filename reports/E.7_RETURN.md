# Stage E.7 return: K1 equity index coded, audited, frozen and screened on the research window (no purchase)

Lead Opus 5.5 xhigh, session 99bb7678-38d8-413c-82c8-d103cf2d3163, 2026-09-28 00:48-03:32 PDT. Prompt
docs/prompts/STAGE_E.7.md (commit c865a87). State file reports/stage_e7_STATE.md. All times PDT.

## 1. Verdict summary

Five K1 members, **11 trials** (the three core ports on MNQ q_c 1, M2K q_c 3 and MYM q_c 3; K1-vxnband-01 and K1-vwap-01
on MNQ), were coded from the frozen entries, audited by Fable (0 blocking, 1 should-fix fixed in the tests, 9 notes),
**frozen in commit 9113abd (cluster freeze cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2)** and run
once on the research window (299 dates). The Fable recomputation found no discrepancy.

| Tier | Trials | Screen (mean net ticks/contract/day, daily t) |
|---|---|---|
| A | none | - |
| B | all 11 | best cp3 MNQ +10.31 (t 0.29); worst vwap MNQ -56.38 (t -1.12) |

None unimplementable, refused or untraded. Labels: K1-vxnband-01 "VXN not point-in-time checked; availability
observational"; the three CP2 trials "tick history not source-verified". No window event item dropped; three
confirmation-window VXN rows dropped. K1-cp3-01 MNQ's Tier B rests on four MLL-liquidated days (flagged). **Program N =
156 + 11 = 167.** A K1 confirmation would need MNQ, M2K and MYM step 2 ($22.11 quoted) and a top-up of about $21.78
($23.99 with 10%).

## 2. Guardrail evidence

**Start checks** (reports/stage_e7_briefs/start_checks.out, verbatim):

```
$ date
Mon Sep 28 12:48:29 AM PDT 2026
$ git status --short
?? reports/stage_e7_briefs/
$ git log --oneline -3
c865a87 docs: swap E.7 and E.8, K1 now (E.7), K6 after the weekly reset (E.8)
6dc521e docs: Stage E.6 results, K7 screened, all 6 trials Tier B, N = 156
d661eb6 feat: K7 member freeze (Stage E.6), cluster freeze sha256 46cae308
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m data.holdout status (keys)
holdout_1 all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87
preflight OK: 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K1 no freeze: ClusterFreezeError
$ ledger
17400 ledger/databento_spend.jsonl
0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
$ acct-2 position (pull_step2.account_position on the step 2 gate; reads the ledger only)
stage-E.5-2026-09-27 {'account': 'acct-2', 'account_cap_usd': 125.0, 'account_credit_usd': 125.0, 'spent_usd': 124.673761, 'cap_headroom_usd': 0.326239, 'credit_left_usd': 0.326239}
$ python -m data.pull_step2 --status (MNQ M2K MYM)
roots in status: 45 ; states: ['not_bought', 'sealed']
MNQ {"state": "not_bought"}
M2K {"state": "not_bought"}
MYM {"state": "not_bought"}
```

Start suite (reports/stage_e7_briefs/pytest_start.out, run with a PYTHONPYCACHEPREFIX set):
`3 failed, 4369 passed, 2 skipped, 1 xfailed, 54 warnings in 1031.07s (0:17:11)`; the 3 are
tests/test_harness_freeze.py's bytecode tests, which fail under a pycache prefix (E.3). Re-run without the prefix
(pytest_start_bytecode_rerun.out): `17 passed in 2.61s`. Start baseline 4372 passed, 2 skipped, 1 xfailed = E.6's end
result. Later suites ran without the prefix, as E.6's did.

**End checks** (reports/stage_e7_briefs/end_checks.out, verbatim):

```
$ date
Mon Sep 28 03:24:22 AM PDT 2026
$ git status --short
 M docs/STAGES.md
 M reports/stage_e7_member_audit.md
?? reports/E.7_RETURN.md
?? reports/stage_e7_STATE.md
?? reports/stage_e7_briefs/
?? reports/stage_e7_coder_A.md
?? reports/stage_e7_coder_B.md
?? reports/stage_e7_k1_screen/
$ git log --oneline -3
9113abd feat: K1 member freeze (Stage E.7), cluster freeze sha256 cf48f514
c865a87 docs: swap E.7 and E.8, K1 now (E.7), K6 after the weekly reset (E.8)
6dc521e docs: Stage E.6 results, K7 screened, all 6 trials Tier B, N = 156
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m data.holdout status (keys)
holdout_1 all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87
preflight OK: 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
$ ledger
17400 ledger/databento_spend.jsonl
0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
$ acct-2 position (pull_step2.account_position on the step 2 gate; reads the ledger only)
stage-E.5-2026-09-27 {'account': 'acct-2', 'account_cap_usd': 125.0, 'account_credit_usd': 125.0, 'spent_usd': 124.673761, 'cap_headroom_usd': 0.326239, 'credit_left_usd': 0.326239}
$ python -m data.pull_step2 --status (MNQ M2K MYM)
roots in status: 45 ; states: ['not_bought', 'sealed']
MNQ {"state": "not_bought"}
M2K {"state": "not_bought"}
MYM {"state": "not_bought"}
```

Suites: gate (02:08:53-02:25:09) `4739 passed, 2 skipped, 1 xfailed`; Task 4 (02:48-03:04:15) `4743 passed, 2 skipped, 1
xfailed`; end (03:08:00-03:24:18, `4743 passed, 2 skipped, 1 xfailed, 54 warnings in 975.99s (0:16:15)`, on 9113abd with no code or test change after it).

Manifests and freezes: E.1 manifest 96166eb3... 32/32 and E.2a ML 077a57e1... 4/4 match at start and end; harness v6
preflight OK at start and end and before the run; K2, K4, K5, K3, K7 cluster freezes verify at start and end; K1's new
freeze verifies at end. Ledger: 17400 lines, sha256 0b5466c4... at start and end (diff empty); acct-2 spent 124.673761,
left 0.326239, unchanged. REGISTRATION.md 0 bytes. Holdout status all_ok, unlocks_logged 0 (both holdouts) at start and
end. No TopstepX reference, no credential, no edit under live/ or ops/, no Databento call, no push.

`git status --short` and `git diff --stat` at the end:

```
 M docs/STAGES.md
 M progress.md
 M reports/stage_e7_member_audit.md
?? reports/E.7_RETURN.md
?? reports/stage_e7_STATE.md
?? reports/stage_e7_briefs/
?? reports/stage_e7_coder_A.md
?? reports/stage_e7_coder_B.md
?? reports/stage_e7_k1_screen/

 docs/STAGES.md                   |   3 +
 progress.md                      |  55 +++++++++++++++
 reports/stage_e7_member_audit.md | 142 +++++++++++++++++++++++++++++++++++++++
 3 files changed, 200 insertions(+)
```

## 3. Results per task

**Task 0.** Start checks pass (section 2). HEAD c865a87 (the commit holding the prompt), clean tree; v6 preflight accepted.

**Task 1: specs** (reports/stage_e7_member_specs.md). Every field with a catalog or design line reference. Adopted readings:
E.3-L-01/03/04/05/06/07/08/09/10/11/12/13/17/19/22, K4-L-01/05/06/13, K3-L-11, K7-L-01/07; K7-L-03 not adopted (K1's C4 has
no vendor-degraded clause). New readings K1-L-01..K1-L-16 (all in section 6 below). The ordinal table:

| Ordinal | Trial | q_c | Ordinal | Trial | q_c |
|---|---|---|---|---|---|
| 1 | K1-cp1-01 MNQ | 1 | 7 | K1-cp3-01 MNQ | 1 |
| 2 | K1-cp1-01 M2K | 3 | 8 | K1-cp3-01 M2K | 3 |
| 3 | K1-cp1-01 MYM | 3 | 9 | K1-cp3-01 MYM | 3 |
| 4 | K1-cp2-01 MNQ | 1 | 10 | K1-vxnband-01 MNQ | 1 |
| 5 | K1-cp2-01 M2K | 3 | 11 | K1-vwap-01 MNQ | 1 |
| 6 | K1-cp2-01 MYM | 3 | | | |

The count, 11, equals the prompt's expectation and the freeze declarations; no difference to log.

**Task 1b: event check and free series** (reports/stage_e7_release_check.md/.json; specs section 9, R-1b-1..R-1b-8).
- VXN: Cboe's free daily file fetched 00:55:48 (sha256 f1b00135c4922ea7..., 4,287 rows 2009-09-14..2026-09-25), saved
  with a new manifest under data/vendor/index_history/vxn/ with three Wayback copies and a FRED copy. 1,797 rows in
  2019-04-30..2026-06-19; the 67 weekdays without a row are all NYSE closures (no gap on an open day). Research-window
  values equal FRED's current copy (0 differences); no 2025-2026 capture exists, so they are **kept and labelled "not
  point-in-time checked"**. Publication before 08:30 CT on D+1 in every informative observation (file Last-Modified
  17:01 CDT on D; captures at 08:05 CST and 04:12 CDT on D+1), no Cboe statement: observational.
- **Dropped (confirmation window only):** 2024-02-01 (revised 11.20 in the 2024-04-19 capture to 17.33 now; R-1b-2);
  2021-04-02 and 2021-12-24 (carry-forward rows on NYSE closures; R-1b-3). Effect: 2024-02-02 and 2021-04-05 have no V.
- Nine research dates have no V because trade date d-1 was an exchange holiday with a CME early halt (K1-L-02): 2025-05-27,
  06-20, 07-07, 09-02, 11-28, 2026-01-20, 02-17, 04-06, 05-26.
- CPI: all 14 research instants kept (BLS schedules; the delayed 2025-10-24 and 2025-12-18 releases and the cancelled
  October 2025 CPI confirmed); D9.12 never binds on K1 (no fill before 08:31, q_c <= 3).
- Equity calendar: all 16 research dates the members meet (3 closures, 13 early halts or early F) cited and equal across
  MNQ, M2K, MYM; keep. No member reads a release (FOMC 10, NFP 14, ISM_SERVICES 15 rows per root are harness inputs).

**Task 2: modules and tests.** strategy/members/k1/: cp1.py, cp2.py, cp3.py, _port_common.py (MemberCoder-A);
vxnband.py, vwap.py, _event_common.py, _calendar.py (EQUITY_TRADE_DATES 1,846, EQUITY_FULL_SESSIONS 1,779), _vxn.py
(VXN_CLOSE 1,794 = 1,797 - 3 drops; CLOSE as exact strings) (MemberCoder-B, generator reports/stage_e7_briefs/
gen_k1_tables.py); __init__.py 0 bytes. Tests: tests/test_k1_members_ports.py, _ports_cp2.py, _ports_cp3.py,
_ports_events.py (268 cases, all through the real engine), tests/test_k1_members_tables.py, _vxnband.py, _vwap.py (99 +
4 after R-T3-1/R-T3-4). Coders' mutants: A 178/182 killed (4 equivalent), B 82/84 (2 equivalent). Coder reports
reports/stage_e7_coder_A.md (saved by the lead from the coder's final message: the harness refused the subagent's .md
write) and reports/stage_e7_coder_B.md.

**Task 3: fidelity audit** (reports/stage_e7_member_audit.md Part 1, MemberAuditor-K1-FableXHigh 02:09-02:45): 0
BLOCKING, 1 SHOULD FIX, 9 NOTE; the ports' rule bodies byte-identical to the audited K7 ports; tables recomputed equal;
exact-rational oracles (100k band, 50k CLV, 3k VWAP days) 0 mismatches; 113 auditor mutants, 106 killed, 4 equivalent,
2 survivors (VB-26, VW-28) = the SHOULD FIX; every lead reading stands. Section 5 has each finding and ruling.

**Task 4: freeze.** Rulings reports/stage_e7_member_rulings.md; R-T3-1/R-T3-4 test-only fix (member files unchanged
against the pre-audit hashes); cluster freeze reports/stage_e_k1_member_freeze.json written 02:47:46, sha256
cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2, 11 members, 11 files, verified; commit **9113abd**
03:04:26 "feat: K1 member freeze (Stage E.7), cluster freeze sha256 cf48f514" (29 files: modules, tests, specs, release
check, the VXN files force-added past .gitignore, audit Part 1, rulings, freeze).

**Task 5: the screen** (03:04:36-03:07:26, exit 0, "K1 research: 11 members, 0 refused"; reports/stage_e7_k1_screen/, 11
records, 11 trip lists, the cluster file; log reports/stage_e7_briefs/t5_run.log). Window 299 trade dates
2025-04-01..2026-06-12 (316 less 15 roll-blackout dates and 2 UR-1 dates). Power `not_run` (StartRuleMissing) on every
record. eps (net ticks/contract/day): MNQ 170, M2K 56, MYM 56.

| # | Trial | Trips | Mean net ticks | sd | Daily t | Net USD | Coverage | Labels | MLL | Tier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K1-cp1-01 MNQ | 284 | +4.4725 | 232.10 | +0.333 | +668.64 | 0.9998 | none | 1 | B |
| 2 | K1-cp1-01 M2K | 285 | -2.9538 | 52.37 | -0.975 | -1,324.80 | 0.9998 | none | 1 | B |
| 3 | K1-cp1-01 MYM | 286 | -8.2648 | 78.45 | -1.822 | -3,706.78 | 0.9999 | none | 2 | B |
| 4 | K1-cp2-01 MNQ | 296 | -8.4855 | 500.75 | -0.293 | -1,268.58 | 1.0000 | none | 2 | B |
| 5 | K1-cp2-01 M2K | 297 | +2.8543 | 134.85 | +0.366 | +1,280.15 | 0.9996 | none | 0 | B |
| 6 | K1-cp2-01 MYM | 295 | -10.7871 | 174.20 | -1.071 | -4,838.03 | 0.9998 | none | 5 | B |
| 7 | K1-cp3-01 MNQ | 118 | +10.3082 | 625.67 | +0.285 | +1,541.08 | 1.0000 | none | 4 | B |
| 8 | K1-cp3-01 M2K | 140 | -14.1300 | 189.81 | -1.287 | -6,337.29 | 0.9996 | none | 6 | B |
| 9 | K1-cp3-01 MYM | 131 | -16.1497 | 229.30 | -1.218 | -7,243.12 | 0.9998 | none | 8 | B |
| 10 | K1-vxnband-01 MNQ | 25 | -11.5237 | 257.25 | -0.775 | -1,722.79 | 1.0000 | none | 1 | B |
| 11 | K1-vwap-01 MNQ | 3,502 | -56.3758 | 874.31 | -1.115 | -8,428.18 | 1.0000 | none | 8 | B |

Labels: no D9 floor label on any trial (max entries a day 1, vwap 20; 0 entry-cap and 0 min-hold refusals; mean holds
28.9, 74.1-74.8, 369.8-374.4, 29.6 and 28.9 minutes); source-overlap on all five members (confirmation only); the
session labels in section 1. vwap traded 286 dates, about 12 trips a day, 61 dates at the cap of 20; its gross could
not be separated from costs here (no prices in the records). vxnband: 97 of 287 full-session window dates had V in regime
(V < 20 or V >= 30), 25 traded (13 at V >= 30, 12 at V < 20). Engine notes: the first window date 2025-04-01 is
untradeable for CP2 and vwap (no prior-settlement proxy for D9.7; harness behaviour, 1 date of 299); the D9.5a guard
moved 23 vwap reversal pairs and some CP2 fills to 09:02 or 13:02.

**Task 6: recomputation** (Part 2, 03:08-03:17): no discrepancy (section 5). **Tiers final and verified.**

**Task 7: the read.** Tier A is empty, so K1 has no Holm family and no edge candidate. **Program N = 156 + 11 = 167**
(every trial has a screen record, as E.4 counted; K1-L-16). The three positive-mean trials (cp1 MNQ, cp2 M2K, cp3 MNQ) have
daily t 0.29-0.37, far from D5's 1.0. **K1-cp3-01 MNQ:** its four MLL-closed trips (2025-04-07, 04-09, 04-14, 09-05)
total -$5,443.56; with them zeroed its series would pass the screen (mean 46.72, t 1.56). The lead's reading: the tier
stands. The MLL floor is the frozen XFA account model applied to the member as deployed, the screen is D5's on the
recorded series, and zeroing is a bound, not an estimate (held to 14:59 those trips could have lost more or less). Even
the zeroed t would be far below the edge chain's 3.0. Flagged for the user. K1-vxnband-01's one MLL trip (-$1,802.56 on
2025-04-09) carries most of its loss; zeroed it still fails (t 0.06).
**What K1's confirmation would need:** MNQ, M2K and MYM step 2 history, quoted $22.11 on 2026-09-26 (MNQ $7.59, M2K $7.15,
MYM $7.37; $24.32 with D13's 10%; reports/stage_e2b_step2_quotes.md line 72). acct-2 holds $0.326239, so a top-up of
about $21.78 at the quote or $23.99 with 10%, and ACCOUNT_2_CAP_USD raised to at least $146.78 ($148.99). A fresh quote is
logged before any spend. With Tier A empty, only a null-side confirmation is possible (as K7's).

## 4. Delegation record

| Agent (description) | Worker file | Model | Effort | Objective | Status and deviations |
|---|---|---|---|---|---|
| ReleaseChecker-OpusMed | worker-medium | opus | medium | Task 1b: VXN file, CPI instants, equity calendar, other inputs | done 00:52-01:08; no WebSearch used; its leftover FRED download timed out without changing a file |
| MemberCoder-A-OpusXHigh | worker-xhigh | opus | xhigh | Task 2: the three ports on three roots, tests, mutants | done 01:03-02:06 (63 min against 40 estimated); the harness refused its .md report write, and the lead saved the text; its scratch mutant script was overwritten by coder B at 01:21 and rebuilt |
| MemberCoder-B-OpusXHigh | worker-xhigh | opus | xhigh | Task 2: vxnband, vwap, the tables; resumed for R-T3-1/R-T3-4 | done 01:03-01:38, resumed 02:46-02:47 (tests only); started before 1b finished (the VXN rulings followed by message at 01:13); overwrote coder A's scratch file (a shared scratchpad name) and reported it |
| MemberAuditor-K1-FableXHigh | worker-xhigh | fable | xhigh | Task 3 fidelity audit; resumed for Task 6 recomputation | Part 1 02:09-02:45, Part 2 03:08-03:17; no deviation |

At most three workers ran at once. No worker spawned another.

## 5. Verification

**Part 1 (fidelity audit)**, rulings in reports/stage_e7_member_rulings.md:

| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| 1. vxnband and vwap engine tests never feed the previous evening's bars; "only bars of CT date d" had no failing mutant (VB-26, VW-28) | SHOULD FIX | R-T3-1 accepted, test-only | coder B added per-member evening tests (vxnband with the real post-Memorial-Day layout; Tuesday stays Wednesday's C_prev); each kills its mutant; member files unchanged |
| 2. C7's tick history not confirmed before bars | NOTE | R-T3-2: E.2a's raw checks show 0 off-tick prices on the frozen grid; only CP2's buffer depends on tick size | label on the three CP2 trials; specs K1-L-14 amended; confirmation session confirms (C7) |
| 3. Cboe publication time observational | NOTE | R-T3-3: label carried | none |
| 4. No synthetic-F flatten test for vxnband and vwap | NOTE | R-T3-4 adopted | coder B added one per member |
| 5. K1-L-08 counts sent intents (vs fills) | NOTE | R-T3-5: stands, the conservative reading; alternative recorded | none |
| 6. vxnband's hold is 28 min under a D9.5a-deferred entry | NOTE | as K1-L-05 | none |
| 7. _calendar.py starts 2019-05-01 | NOTE | no trade date affected | none |
| 8. cp2.py's F literal in trading_windows | NOTE | equals D line 391 and the audited K7 port | none |
| 9. two behaviours reachable only by direct calls | NOTE | follow the specs | none |
| 10. nine research dates without V | NOTE | reported with the trial (section 3) | none |

The auditor also found a line drift in the specs' C9 citations (150-151 instead of 154); corrected, no reading changed.

**Part 2 (recomputation):** item 0 VERIFIED (every file equals the freeze; only the two coder-B test files differ from
Part 1's hashes); 1 VERIFIED (11 screens to 1e-9; 299 dates = 316 - 15 - 2); 2 VERIFIED (all Tier B, no label, no OC-H
exclusion); 3 VERIFIED (cp2 MNQ's 296 and vwap's 3,502 trips' net_cents rebuilt exactly from the frozen cost table and
release calendar, event-window cost on 52 trips, both series day by day; gross not checkable without prices); 4 VERIFIED
WITH NOTES (every trip on an eligible date at the rule's minutes or a documented deviation: MLL, D9.7, D9.5a, CP2's
present-bar count on thin holiday sessions; 72 eligible vxnband dates without a trip cannot be attributed without bars;
first window date untradeable for CP2 and vwap); 5 VERIFIED (N = 167); 6 VERIFIED WITH NOTES (MLL counts match; only
K1-cp3-01 MNQ's tier would flip with its MLL days zeroed; the lead's reading in section 3). No DISCREPANCY, so no tier is
"unverified".

## 6. Open choices (each decided by the lead alone, with the reason; each can be overturned)

- **K1-L-01 VXN is used from 08:30 CT on d**, as the vxnband entry (C line 458) and C9 (C line 154) state. The prompt's
  test note cites "the catalog KF1 row: from 08:35 CT on d"; KF1 is K1-ml-01's feature row (excluded, U6), whose 08:35 is
  the ML decision window's start. Using 08:35 would drop breaches on the 08:30-08:33 bars and change the frozen rule.
  The auditor agreed. **Flagged for the user.**
- **K1-L-02** V is the VXN close of the EC-CAL trade date before d; after an exchange holiday that is a CME early-halt
  trade date, Cboe has no close, so the next date is not traded (9 research dates). Not adopted: pairing V with C_prev's
  date (9 more research dates would be eligible).
- **K1-L-03** C_prev by Family H completeness, as CP3's d-1; **K1-L-04** vxnband's exact band, clock scan, and a gap or an
  instrument change before the first breach ends the day's search; the first breach uses the day's entry; **K1-L-05**
  vxnband's exit by clock at entry-intent + 30 min.
- **K1-L-06** VWAP over present bars, exact integer sign; **K1-L-07** a gap ends vwap's new entries for the day (the open
  position keeps the rule's exits); the instrument-change exit as the entry states; **K1-L-08** entries counted as sent
  intents (R-T3-5; the alternative counts fills); **K1-L-09** vwap's fill bar is the bar at which the position is first
  seen, and no intent while an order is pending.
- **K1-L-10** C4's early close by EQUITY_FULL_SESSIONS (the halt and F tests agree on every date); **K1-L-11**
  trading_windows; **K1-L-12** 11 declarations in catalog order then MNQ, M2K, MYM; **K1-L-13** two coders, seven test
  files; **K1-L-14** catalog section 7 settled by the frozen text (item 10(c) amended, R-T3-2); **K1-L-15** D9.12 never
  binds; **K1-L-16** the N rule (a trial counts when the runner writes its screen record).
- **R-1b-1** research VXN rows kept with the label "not point-in-time checked"; **R-1b-2** 2024-02-01 dropped rather
  than taking either value (**flagged**: the confirmation's 2024-02-02 is not traded); **R-1b-3** the two carry-forward
  rows dropped (2021-04-05 not traded).
- **R-T3-2** the tick-history gap handled by a label on the three CP2 trials, not the nine ports (only CP2's buffer is
  tick-dependent), because web access is limited to Task 1b.
- **K1-cp3-01 MNQ's tier stands** although its four MLL-closed days decide it (section 3). **Flagged for the user.**
- **The VXN evidence files were committed** (the file, the new manifest, three Wayback copies and the FRED copy, force-added
  past .gitignore): the prompt names "any free series file", and the Wayback copy is the evidence for R-1b-2. The pages
  under reports/stage_e7_briefs/pages/ stay uncommitted.
- **Coder A's report was saved by the lead** from the coder's final message (the harness refused the subagent's .md
  write), unchanged except a one-line provenance comment.
- **Coder B started before Task 1b finished** (only the VXN table depended on it; the rulings followed by message).
- **The start suite ran with a PYTHONPYCACHEPREFIX**, which fails three bytecode tests; they passed on a re-run without it,
  and every later suite ran without the prefix (the prompt's prefix rule is read as applying to Stage E commands).
- **The session cost counts output tokens from each message's last usage record** (reports/stage_e7_briefs/cost.py).
  E.4-E.6 used reports/stage_e4_briefs/cost.py, which keeps the first record of a streamed message and so understated
  output tokens (here: 165,965 against the final count); cache reads, about 95% of every total, are unaffected.
- The one-off generator, the lead's scripts, the coder reports, the STATE file, the screen records and the audit's Part 2
  stay uncommitted, as in E.3-E.6. The end suite ran fresh on 9113abd while Part 2 was written (no code or test changed
  after the commit).

## 7. What the next session must do first

- **The push the planning chat owes:** 9113abd (K1 member freeze) is on main, not pushed. The session made exactly that one
  commit. Uncommitted by design: reports/E.7_RETURN.md, reports/stage_e7_STATE.md, reports/stage_e7_briefs/,
  reports/stage_e7_coder_A.md, _coder_B.md, reports/stage_e7_k1_screen/, the audit's Part 2 (reports/stage_e7_member_audit.md
  modified), and the progress.md and docs/STAGES.md lines.
- **Frozen hashes in force:** harness v6 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87; E.1 manifest
  96166eb3...; E.2a ML 077a57e1...; cluster freezes K2 8815a775..., K4 7abcde17..., K5 1d0c974f..., K3 c4fb5da4..., K7
  46cae308..., **K1 cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2** (11 members). VXN file sha256
  f1b00135c4922ea756cd22cfeaa1d483700a6aed580f8da562f61574b5e1cdcc.
- **Funding for a K1 confirmation:** step 2 for MNQ, M2K, MYM quoted $22.11 (2026-09-26); acct-2 has $0.326239; top-up about
  $21.78 at the quote, $23.99 with 10%; the account cap must rise to at least $146.78 ($148.99). A fresh quote first.
- **Questions for the user:** (1) whether to run K1's null-side confirmation at all, with Tier A empty; (2) K1-L-01's 08:30
  against the prompt's 08:35 note; (3) K1-cp3-01 MNQ's MLL-decided Tier B; (4) R-1b-2's drop of 2024-02-01 (confirmation
  window); (5) the tick-history confirmation (C7) owed before any K1 confirmation bar is read; (6) whether E.4-E.6's
  session-cost output counts should be restated with the last-record method.
- **Next stage:** E.8 (K6) after the weekly reset, per V15 as amended.

## 8. Session cost

**Wall clock** 00:48-03:32 PDT (2 h 44 min), all of it work: no pause, no usage-limit wait, no crash. First estimate
3 h 12 min (to about 04:00; the prompt expected about 1.5 h); the cumulative ETA moved about +15 min at 02:06 (coder A's 63
minutes against 40) and back as the audit, run and recomputation came in shorter. The four full suites (16-17 minutes each)
are about 66 minutes of the wall clock, three of them overlapping worker time.

**Final ETA table** (PDT; tokens from the transcripts; no pause rows, since none occurred):

| Task | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Startup checks (start suite in background to 01:06) | lead | opus | xhigh | 00:48 | 00:52 | 4 min | in lead | done; suite = E.6's end result after the bytecode re-run |
| 1 Member specs (section 9 at 01:12) | lead | opus | xhigh | 00:50 | 01:00 | 10 min | in lead | done |
| 1b Event checks, free series | ReleaseChecker-OpusMed | opus | medium | 00:52 | 01:08 | 16 min | 9,055,436 | done; 3 confirmation-window VXN drops |
| 2A Ports | MemberCoder-A-OpusXHigh | opus | xhigh | 01:03 | 02:06 | 63 min | 23,182,817 | done; .md write refused, saved by the lead |
| 2B New members, tables (+ R-T3-1/R-T3-4 02:46-02:47) | MemberCoder-B-OpusXHigh | opus | xhigh | 01:03 | 02:47 | 37 min | 27,445,017 | done; started before 1b finished (logged) |
| 2g Gate suite | lead | - | - | 02:09 | 02:25 | 16 min | in lead | 4739 passed |
| 3 Fidelity audit | MemberAuditor-K1-FableXHigh | fable | xhigh | 02:09 | 02:45 | 36 min | 14,969,310 (Parts 1 and 2) | 0 blocking, 1 should-fix, 9 notes |
| 4 Rulings, fix, freeze, suite, commit 9113abd | lead | opus | xhigh | 02:45 | 03:04 | 19 min | in lead | done |
| 5 Screening run | lead | opus | xhigh | 03:04 | 03:07 | 3 min | in lead | 11 members, 0 refused |
| 6 Recomputation | MemberAuditor-K1-FableXHigh (resumed) | fable | xhigh | 03:08 | 03:17 | 9 min | above | no discrepancy |
| 7 Result, return, end suite (03:08-03:24), end checks, cost, progress | lead | opus | xhigh | 03:07 | 03:32 | 25 min | in lead | done |
| **Stage** | | | | 00:48 | 03:32 | **2 h 44 min wall and work** | **115,063,741** (lead 40,411,161, 35.1%; workers 74,652,580, 64.9%) | first estimate 3 h 12 min; the prompt expected about 1.5 h |

**Tokens per model** (the lead transcript 99bb7678's .jsonl plus every worker transcript under its subagents/ folder;
each assistant message counted once by message id, from its LAST usage record, so output tokens are final counts;
reports/stage_e7_briefs/cost.py, cost.out; the lead's last messages after the count, about 03:25-03:32, are not included):

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,228 | 179,275 | 13,434,512 | 1,354,295 | 14,969,310 |
| claude-opus-5-5 | 892 | 540,396 | 96,296,997 | 3,256,146 | 100,094,431 |
| all | 2,120 | 719,671 | 109,731,509 | 4,610,441 | 115,063,741 |

Per worker spawn: ReleaseChecker-OpusMed (worker-medium, opus, medium) 9,055,436; MemberCoder-A-OpusXHigh (worker-xhigh,
opus, xhigh) 23,182,817; MemberCoder-B-OpusXHigh (worker-xhigh, opus, xhigh, incl. its resumption) 27,445,017;
MemberAuditor-K1-FableXHigh (worker-xhigh, fable, xhigh, Parts 1 and 2) 14,969,310.

Delegation share: lead 35.1%, workers 64.9%; by model opus 87.0%, fable 13.0%. Cache reads are 95.4% of all tokens. Method
note: E.4-E.6 kept each message's first usage record, which understates output tokens; with that method this session's
output would read about 166k instead of 720k (cache reads unchanged). These are token counts, not plan-credit percentages;
the /usage meter is the user's to record.
