# Stage E.5 return: K4 and K5 confirmation (harness v5 and v6, step 2 purchase, K4 confirmed null, K5 stopped before its list)

Lead: Opus 5.5, effort xhigh, 2026-09-27 PDT, three lead transcripts: b56ee083 (12:14-13:50, ended by the machine's crash),
3e169521 (13:52-13:58, paused by the user for usage) and 9e668467 (17:35 on). The prompt is commit ff59c69.

## 1. Verdict summary

**Harness v5** ba925a97854efdc61a8a20641af10cc0de0be472a634dcb3b8bd637259bba0cd, commit 2c0bfe0. It adds the 2019-2023 Topstep holiday rows (Rule H-1,
48 rows, every July 3 unsettled), the confirmation-verdict module, and the E.5 spend block with the gate wiring (L-E5-1). Fable review:
0 blocking, 2 should-fix (fixed), 10 notes. **v6** 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87, commit ce3cb66, differs
only in data/config.py's caps ($21.52 session, $3.00 request).

**Spend** $21.196568 against a fresh quote of $21.196568 (K4 $11.455464, K5 $9.741104). 224 chunks; all 52 holdout-2 chunks sealed on
arrival (13 per root, in order); 0 unlocks. acct-2 has $0.326239 left.

**S_X:** MCL 2021-07-12, NG 2019-05-06, MHG 2022-06-01. **MGC: none (empty window).** Power: all 12 K4 trials sufficient.

**NGS check:** 252 releases, 5 dropped (C9, R-C3-1 and R-C3-2); K4 freeze 7abcde17..., commit 41d6adf. **K4 list** 22388c6b...
(md 8d72edd1...), commit 4161032.

| Cluster | Null statement | Tier A trial | Holm (K = 9) | Composite | DSR | t | PBO | Chain |
|---|---|---|---|---|---|---|---|---|
| K4 | **null**: all 12 trials covered, UCB95 < eps_X, power >= 0.96 | K4-ngpre-01 NG | p 0.5375, no | pending | 3.1e-5 | -0.07 | 0.643 | no edge |
| K5 | none: stopped before its list (R-D-1) | K5-fomc-01 MGC | not run | - | - | - | - | inconclusive by design: supply 0 |

K5's six MGC trials have an empty confirmation window, so K5's single run would test only cp3 MHG and ovr MHG. That would foreclose U8
(GC bars as MGC's price path), so the choice is the user's (section 7). Every K4 verdict figure was recomputed by ConfirmAuditor-K4-FableXHigh: no discrepancy.

## 2. Guardrail evidence

**Start checks, verbatim** (12:25; reports/stage_e5_briefs/start_checks.out; the suite reports/stage_e5_briefs/pytest_start.out):
```
$ date
Sun Sep 27 12:25:30 PM PDT 2026
$ git status --short
?? reports/stage_e5_briefs/
$ git log --oneline -3
ff59c69 docs: Stage E.5 prompt (K4 and K5 confirmation) and V14
7c2cec3 docs: Stage E.4 results, K4 K5 K3 screened, 3 Tier A of 48 screened, N = 150
c5dfd5c feat: K3 member freeze (Stage E.4 Part 3), cluster freeze sha256 c4fb5da4
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m data.holdout status (keys)
holdout_1 all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected 82ae8536738ca43395f43356840c0b799a7925b7b75ddb4fc1353d3ab7491009
preflight OK: 82ae8536738ca43395f43356840c0b799a7925b7b75ddb4fc1353d3ab7491009
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K4 cluster freeze OK cf066cb0507134e2553781f42699165b471be45ebec6b07bfb0d75680e879d1a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
$ ledger
14823 ledger/databento_spend.jsonl
02e7caa257bbee7b84d23a0394c9fae34985e884c1306fb47ea683546f15b1ed
$ acct-2 position (pull_step2.account_position on the step 2 gate; reads the ledger only)
stage-E.2b-2026-09-26 {'account': 'acct-2', 'account_cap_usd': 125.0, 'account_credit_usd': 125.0, 'spent_usd': 103.477194, 'cap_headroom_usd': 21.522806, 'credit_left_usd': 21.522806}
$ python -m data.pull_step2 --status (MCL NG MGC MHG)
roots in status: 45 ; states: ['not_bought']
MCL {"state": "not_bought"}
NG {"state": "not_bought"}
MGC {"state": "not_bought"}
MHG {"state": "not_bought"}
$ ls reports/step2/ data/processed_step2/
ls: cannot access 'reports/step2/': No such file or directory
ls: cannot access 'data/processed_step2/': No such file or directory
$ uv run pytest -q   (start 12:25:21)
4043 passed, 2 skipped, 1 xfailed, 54 warnings in 690.04s (0:11:30)
```
The start suite equals E.4's end result. Scripts ran with a fresh PYTHONPYCACHEPREFIX in the scratchpad (outside the repository);
the suite ran without it, as E.3 established.

**Resume checks after the user's pause, verbatim** (17:36, working tree at v5, before the v5 commit; reports/stage_e5_briefs/resume_checks.out):
```
$ date
Sun Sep 27 05:36:28 PM PDT 2026
$ git status --short
$ git log --oneline -3
ff59c69 docs: Stage E.5 prompt (K4 and K5 confirmation) and V14
7c2cec3 docs: Stage E.4 results, K4 K5 K3 screened, 3 Tier A of 48 screened, N = 150
c5dfd5c feat: K3 member freeze (Stage E.4 Part 3), cluster freeze sha256 c4fb5da4
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m data.holdout status (keys)
holdout_1 all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected ba925a97854efdc61a8a20641af10cc0de0be472a634dcb3b8bd637259bba0cd
preflight OK: ba925a97854efdc61a8a20641af10cc0de0be472a634dcb3b8bd637259bba0cd
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K4 cluster freeze OK cf066cb0507134e2553781f42699165b471be45ebec6b07bfb0d75680e879d1a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
$ ledger
14823 ledger/databento_spend.jsonl
02e7caa257bbee7b84d23a0394c9fae34985e884c1306fb47ea683546f15b1ed
$ acct-2 position (pull_step2.account_position on the step 2 gate; reads the ledger only)
stage-E.5-2026-09-27 {'account': 'acct-2', 'account_cap_usd': 125.0, 'account_credit_usd': 125.0, 'spent_usd': 103.477194, 'cap_headroom_usd': 21.522806, 'credit_left_usd': 21.522806}
$ python -m data.pull_step2 --status (MCL NG MGC MHG)
roots in status: 45 ; states: ['not_bought']
MCL {"state": "not_bought"}
NG {"state": "not_bought"}
MGC {"state": "not_bought"}
MHG {"state": "not_bought"}
$ ls reports/step2/ data/processed_step2/
ls: cannot access 'reports/step2/': No such file or directory
ls: cannot access 'data/processed_step2/': No such file or directory
```

**End checks, verbatim** (19:39:44; reports/stage_e5_briefs/end_checks.out; long `--status` lines cut at 220 characters; the untracked
E.5 report files are left out of `git status --short` here and listed in section 7):
```
$ date
Sun Sep 27 07:39:44 PM PDT 2026
$ git status --short
 M docs/HOLDOUT_UNLOCK_LOG.md
 M docs/STAGES.md
 M ledger/databento_spend.jsonl
 M reports/stage_e5_k4_audit.md
$ git log --oneline -3
4161032 docs: K4 confirmation list (Stage E.5 C4), sha256 22388c6b
41d6adf feat: K4 C9 table amendment (Stage E.5 C3), cluster freeze sha256 7abcde17
ce3cb66 feat: harness v6, E.5 spend caps (sha256 9a8ebe73)
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
$ ledger
17400 ledger/databento_spend.jsonl
0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
$ acct-2 position (pull_step2.account_position on the step 2 gate; reads the ledger only)
stage-E.5-2026-09-27 {'account': 'acct-2', 'account_cap_usd': 125.0, 'account_credit_usd': 125.0, 'spent_usd': 124.673761, 'cap_headroom_usd': 0.326239, 'credit_left_usd': 0.326239}
$ python -m data.pull_step2 --status (MCL NG MGC MHG)
roots in status: 45 ; states: ['not_bought', 'sealed']
MCL {"holdout": "holdout 2", "product": "MCL", "product_matches": true, "state": "sealed", "chunks_expected": 13, "chunks_sealed": 13, "sealed_in_order": true, "raw_files": {"range=2024-03-01_2024-04-01.dbn.zst": {"seale
NG {"holdout": "holdout 2", "product": "NG", "product_matches": true, "state": "sealed", "chunks_expected": 13, "chunks_sealed": 13, "sealed_in_order": true, "raw_files": {"range=2024-03-01_2024-04-01.dbn.zst": {"sealed_
MGC {"holdout": "holdout 2", "product": "MGC", "product_matches": true, "state": "sealed", "chunks_expected": 13, "chunks_sealed": 13, "sealed_in_order": true, "raw_files": {"range=2024-03-01_2024-04-01.dbn.zst": {"seale
MHG {"holdout": "holdout 2", "product": "MHG", "product_matches": true, "state": "sealed", "chunks_expected": 13, "chunks_sealed": 13, "sealed_in_order": true, "raw_files": {"range=2024-03-01_2024-04-01.dbn.zst": {"seale
$ ls reports/step2/ data/processed_step2/
bars_MCL.json
bars_MGC.json
bars_MHG.json
bars_NG.json
purchase_MCL.json
purchase_MGC.json
purchase_MHG.json
purchase_NG.json
MCL
MGC
MHG
NG
$ git diff --stat
 docs/HOLDOUT_UNLOCK_LOG.md   |  416 +++++++
 docs/STAGES.md               |    3 +
 ledger/databento_spend.jsonl | 2577 ++++++++++++++++++++++++++++++++++++++++++
 reports/stage_e5_k4_audit.md |   68 ++
 4 files changed, 3064 insertions(+)
$ git diff --stat -- ledger/
 ledger/databento_spend.jsonl | 2577 ++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 2577 insertions(+)
$ uv run pytest -q   (the session's end suite, start 19:23:39, on the tree at 4161032 plus report files; no code changed after)
4166 passed, 2 skipped, 1 xfailed, 54 warnings in 955.72s (0:15:55)
```
Manifest checks: E.1 and E.2a freezes ALL_OK at start and end; harness v4 OK at start, v5 OK at 13:40, 13:53 and 17:36, v6 OK at the end
(v5 refused after ce3cb66). Cluster freezes K2, K5 and K3 unchanged; K4 cf066cb0 at start, 7abcde17 at the end (the C9 amendment).
Ledger: 14,823 lines at start (02e7caa2...), 17,400 at end (0b5466c4...); +2,577 lines, all stage-E.5-2026-09-27: 2,129 quotes at $0.00, 224
commits ($21.196568) and 224 settles ($0). acct-2: $103.477194 spent at start, $124.673761 at end. docs/HOLDOUT_UNLOCK_LOG.md: +52 "SEALED
holdout 2" entries (13 per root), no unlock. Seals: `--status` 18:50 and at the end, all four roots 13/13 sealed in order, all_ok.
No TopstepX reference, credential or API call; no edit under live/ or ops/; no Databento key printed or logged; no edit to
docs/NULL_CRITERIA.md, docs/NULL_CRITERIA_E.md or any E.3/E.4 record (E.2b's quote files restored to their committed content).
Bars were read only by the runner and the start-rule builder; no session script opened a bar file.

## 3. Results per task

### Task 0: startup (12:23-12:37)
Every start check passed; HEAD ff59c69 held the prompt with a clean tree; the v4 preflight passed; no step 2 chunk existed for any root.

### Task A1: inventory (lead; reports/stage_e5_harness_plan.md)
Of the 16 items of NULL_CRITERIA_E 3 and around it, 6 existed (unit, Holm at K <= 9, t, the power check, OC-H tiers, the D.1f functions
under D.1f's seed). Missing for Stage E: the confirmation bootstrap with seed 20260923 + ordinal, null power at eps_X, the null
statuses, the V14 (c) and PBO switches, the source-overlap gate, the inconclusive-by-design exception, V14 (a)'s wording, the null
statement and its resolution table. The holiday gap: 38 published Topstep rows for 2024-2026 (37 counted by the builder), none before 2024.
The step 2 gate read only E.2b's names (ruling L-E5-1).

### Task A2: the change set (HarnessBuilder-OpusXHigh; reports/stage_e5_harness_change.md)
- rules/sessions.py: Rule H-1 (each weekday the frozen equity calendar lists: full closure -> markets closed; early halt h ->
  close-by h minus the year's lead) reproduces 35 of the 36 published rows in its domain, with the four named exceptions (2024-07-03
  published 11:30, rule 11:45; 2024-01-01, 2025-01-09 and 2025-07-03 not published). 48 derived rows for 2019-05-01..2023-12-31,
  lead 30 minutes (L-E5-2); July 3 (2019, 2020, 2023) unsettled and listed. day_rule unchanged from 2024-01-01 on. 251
  (group, date) flatten times move earlier or close in 2019-2023; 13 of the audit's 15 FX dates now flatten at 11:30.
- screening/stage_e_verdict.py: the verdict module, restating D.1f's pinned functions on funnel/ (equality tests, L-E5-4).
- data/config.py (the E.5 block) and data/pull_step2.py (step2_gate reads the active purchase policy).
- Tests: 119 new or changed; the K3 FX table tests re-pinned to v5 exactly (R-A2-1, SF-2).

### Task A3: replay and review
Replays via python -m under the working tree: K4 25/25 and K5 23/23 files equal E.4's apart from the harness sha256, timestamps and the
trip files' record sha256 (reports/stage_e5_replay_k4.md, _k5.md under b720c5aa; reports/stage_e5_replay_k4_v5.md, _k5_v5.md under v5
exactly). Review: section 5.

### Task A4: v5 (commit 2c0bfe0, 17:53)
Manifest v5 against v4: 3 files added (the verdict module, two test files), 4 changed (data/config.py, data/pull_step2.py,
rules/sessions.py, tests/test_e2b_pull_step2.py), none removed. Suite 17:37-17:53: 4162 passed, 2 skipped, 1 xfailed. The machine
crashed during the first pre-commit suite (13:50) and the user paused the session (13:58-17:35); nothing irreversible was in flight.

### Task B1: quote, caps, v6 (commit ce3cb66, 18:13)
Fresh quote 17:53-18:10 (set clusters-legs, the set `--buy --cluster` buys; 1905 chunks, 0 failed, $0.00 lines under
stage-E.5-2026-09-27): K4 $11.455464, K5 $9.741104, total $21.196568 (the E.2b figures). Session cap = min($23.316225,
headroom $21.522806) = $21.52; request cap $3.00 (D13). E.5's quote record: reports/stage_e5_step2_quotes.json and .md; E.2b's quote files
were restored to their committed content. v6 against v5: only data/config.py.

### Task B2: purchase, seals, bars (reports/stage_e5_purchase.md)
K4 18:13-18:32: 117 chunks, $11.455464. K5 18:32-18:50: 107 chunks, $9.741104 (bought because $10.067342 of headroom was left after K4).
Every settle delta $0. `--status` 18:50: MCL, NG, MGC, MHG each 13/13 sealed in order, all_ok, 0 unlocks, no plaintext. Bars 18:50-18:51:
MCL 894,843 (682 dates from 2021-07-12), NG 1,535,207 (1,246 from 2019-05-06), MGC 1,624,946 (1,246), MHG 361,936 (472 from 2022-05-04).
Calendar checks note early stops only inside each root's span (MCL 12, NG 3, MGC 41, MHG 37): a data-quality note, no refusal.

### Task C1: start rules (reports/stage_e_start_rule_K4.json 523f2e25..., _K5.json d5965f17...)
| Root | S_X (0.25) | 0.15 | 0.40 | V_ref |
|---|---|---|---|---|
| MCL | 2021-07-12 | 2021-07-12 | 2021-07-12 | 54 |
| NG | 2019-05-06 | 2019-05-06 | 2019-05-06 | 127 |
| MGC | **none** (no qualifying month through 2024-02) | 2023-10-02 | none | 299 |
| MHG | 2022-06-01 | 2022-05-04 | none | 11 |

### Task C2: power (reports/stage_e5_k4_start_power.md, reports/stage_e5_k5_start_power.md)
The harness-supported path: research re-runs under v6 (reports/stage_e5_power_k4/, _k5/) that match E.4 in every field but `power`, whose
value is the frozen power_check at the confirmation supply. K4: all 12 "power sufficient" (supply MCL 586, NG 1,070; n_b 1 to 209). K5:
the six MGC trials supply 0, "inconclusive by design" (n_b 1 to 62); cp3 MHG and ovr MHG sufficient (supply 425).

### Task C3: NGS dates (reports/stage_e5_ngs_check.md; reports/stage_e5_k4_table_amendment.md; audit Part 1)
252 releases 2019-05-06..2024-02-29: 247 keep, 5 drop_actual_differs, 0 updated, 0 unverifiable (250 with the time printed on a Wayback
capture of ir.eia.gov/ngs/ngs.html, 1 date from the NGWU). Dropped: 2019-12-26, 2020-01-02, 2020-11-12, 2021-01-21 (EIA released on the
Friday after, as its schedule said; the table's Thursday rows name no release) and 2023-11-09 (no report that week). NGS 372 -> 367 rows;
research-window rows identical. New K4 freeze 7abcde17...; commit 41d6adf with the check and the audit.

### Task C4: the K4 list (commit 4161032)
reports/stage_e5_k4_confirmation_list.json sha256 22388c6b3cbfb2b32809cba1ffbcd6a72ad6ff2b0bff0890474d80a65037d46c; .md
8d72edd1cea4375a9843c6b5b008b4e85bd7d0f24ddf6f7ee0d60668e3dece13. 12 trials, K = 9, N = 150, seeds 20260924..20260935.

### Task C5: the K4 confirmation run (once, 19:15:54-19:22:07) and verdicts (reports/stage_e5_k4_verdicts.md, .json b574b4c1...)
`python -m screening.stage_e_runner --harness-sha256 <v6> --cluster K4 --all --window confirmation ...`: 12 members, 0 refused. Verdict
module 19:22: statement null.

Every trial's confirmation figures (net ticks per contract per day of the vehicle; eps_X in the same unit):

| Cluster | Ord | Trial | Tier | Days | Closed trips | theta_hat | UCB95 | SE_boot | eps_X | Null power | Null verdict | Labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K4 | 1 | K4-cp1-01 MCL | B | 586 | 563 | -6.9332 | -3.9889 | 1.7825 | 21 | 1.0000 | null | source-overlap |
| K4 | 2 | K4-cp1-01 NG | B | 1070 | 1024 | -1.4306 | +0.6634 | 1.2571 | 8 | 1.0000 | null | source-overlap |
| K4 | 3 | K4-cp2-01 MCL | B | 586 | 585 | -2.7009 | +3.0883 | 3.4614 | 21 | 1.0000 | null | source-overlap |
| K4 | 4 | K4-cp2-01 NG | B | 1070 | 1061 | +1.4390 | +5.4655 | 2.3455 | 8 | 0.9613 | null | source-overlap |
| K4 | 5 | K4-cp3-01 MCL | B | 586 | 280 | -1.7862 | +5.3481 | 4.2274 | 21 | 0.9996 | null | source-overlap |
| K4 | 6 | K4-cp3-01 NG | B | 1070 | 455 | -5.4139 | -1.7005 | 2.2949 | 8 | 0.9672 | null | source-overlap |
| K4 | 7 | K4-ngpre-01 NG | A | 1070 | 198 | -0.0823 | +1.7735 | 1.1106 | 8 | 1.0000 | null | calendar partly unverified |
| K4 | 8 | K4-apipre-01 MCL | B | 586 | 93 | -0.4384 | +1.6168 | 1.2389 | 21 | 1.0000 | null | source-overlap |
| K4 | 9 | K4-eiafade-01 MCL | B | 586 | 55 | -2.7267 | -0.7509 | 1.2374 | 21 | 1.0000 | null | source-overlap |
| K4 | 10 | K4-eiamom-01 MCL | B | 586 | 100 | -0.0879 | +0.4682 | 0.3266 | 21 | 1.0000 | null | source-overlap |
| K4 | 11 | K4-ovr-01 MCL | B | 586 | 587 | -5.2969 | -0.1226 | 3.1556 | 21 | 1.0000 | null | source-overlap |
| K4 | 12 | K4-ovr-01 NG | B | 1070 | 1091 | -1.0121 | +1.5175 | 1.5558 | 8 | 0.9998 | null | source-overlap |

| Cluster | Ord | Trial | Tier | Confirmation | D4 power (label) |
|---|---|---|---|---|---|
| K5 | 1 | K5-cp1-01 MGC | B | not run (K5 stopped, R-D-1) | supply 0, n_b 9, inconclusive by design |
| K5 | 2 | K5-cp1-01 MHG | excluded | not run (K5 stopped, R-D-1) | coverage_below_0.95 |
| K5 | 3 | K5-cp2-01 MGC | B | not run (K5 stopped, R-D-1) | supply 0, n_b 44, inconclusive by design |
| K5 | 4 | K5-cp2-01 MHG | excluded | not run (K5 stopped, R-D-1) | coverage_below_0.95 |
| K5 | 5 | K5-cp3-01 MGC | B | not run (K5 stopped, R-D-1) | supply 0, n_b 62, inconclusive by design |
| K5 | 6 | K5-cp3-01 MHG | B | not run (K5 stopped, R-D-1) | supply 425, n_b 52, power sufficient |
| K5 | 7 | K5-preauc-01 MGC | B | not run (K5 stopped, R-D-1) | supply 0, n_b 6, inconclusive by design |
| K5 | 8 | K5-pmfix-01 MGC | excluded | not run (K5 stopped, R-D-1) | supply 0, n_b 11, inconclusive by design |
| K5 | 9 | K5-fomc-01 MGC | A | not run (K5 stopped, R-D-1) | supply 0, n_b 1, inconclusive by design |
| K5 | 10 | K5-ovr-01 MGC | B | not run (K5 stopped, R-D-1) | supply 0, n_b 29, inconclusive by design |
| K5 | 11 | K5-ovr-01 MHG | B | not run (K5 stopped, R-D-1) | supply 425, n_b 18, power sufficient |

K4 per-exposure resolution: MCL eps 21 ticks ($84.00/day at q_c 4), fewest trips K4-eiafade-01 (55), largest per-trade upper bound 11.19 ticks
(K4-cp3-01 MCL); NG eps 8 ticks ($80.00/day at q_c 1), fewest trips K4-ngpre-01 (198), largest per-trade upper bound 9.58 ticks
(K4-ngpre-01). No member null by inactivity; none not covered. K4-ngpre-01's sign check (catalog, descriptive): mean price move T-90 to
T+30 -1.27 ticks, t -0.20.

The K4 null statement, as NULL_CRITERIA_E 1 and 7 allow it: for intraday strategies on CME energy futures in cluster K4, on the
pre-registered confirmation windows (MCL 2021-07-12, NG 2019-05-06, to 2024-02-29), at the modelled retail cost, the risk-matched sizes
and flat by the XFA cutoff, every member's net edge of at least eps_X (MCL 21 ticks/ct/day = $84/day at 4 micros; NG 8 ticks/ct/day =
$80/day at 1 contract) is rejected at one-sided 95% with achieved null power of at least 80%; no member is null by inactivity or
inconclusive by design (lists: reports/stage_e5_k4_confirmation_list.md, sha256 above).

### Task C6: the recomputation (ConfirmAuditor-K4-FableXHigh; reports/stage_e5_k4_audit.md Part 2)
ConfirmAuditor-K4-FableXHigh recomputed every figure in its own code (reports/stage_e5_briefs/audit_k4_part2/):
| Item | Verdict | Evidence |
|---|---|---|
| 0 The run's inputs equal the hashed list | VERIFIED WITH NOTES | list 22388c6b (commit 4161032); all 12 records carry v6, freeze 7abcde17, and the list's member, ordinal, window, S_X, leg roots, frozen-table and calendar hashes; seed = 20260923 + ordinal; record set = the list's run trials. Note: legs are stored as objects in the records, roots in the list; compared on roots |
| 1 Per trial (theta_hat, UCB95, SE_boot, p, power, status) | VERIFIED | every float of all 12 trials reproduced bit-identically; all "null" |
| 2 Holm at K = 9 | VERIFIED | p 0.5375 against 0.005556: not rejected |
| 3 DSR, t, PBO | VERIFIED WITH NOTES | variance 0.0020416 over 12 trials; DSR 3.10e-05 (1.3e-8 relative from the normal-quantile approximation; the program function reproduces it to 1e-9); t -0.06874 exact; PBO 45/70 = 0.642857 exact on 1,154 union dates in blocks of 144 (the last 2 dates fall outside the blocks, as n_days // 8 prescribes) |
| 4 Chain verdict, statement, resolution table | VERIFIED | "no edge", first failing step Holm; cluster "null", 12 covered, none by inactivity; eps_X figures equal the frozen epsilon table |
| 5 Trip rebuild (K4-ngpre-01 NG) | VERIFIED | 198/198 trips exact from gross cents and the cost table; the daily series equal to 2.8e-14 |
| 6 The rendering (.md) | VERIFIED WITH NOTES | every cell matches; the sign-check paragraph is the lead's own descriptive figure from the trip list, not in the JSON (unchecked) |
No DISCREPANCY, so no verdict is marked "unverified". Unchecked: an MCL trip rebuild, the sign-check figures, the runner itself.

### Part D: K5 (stopped after C1 and C2; ruling R-D-1)
K5 was bought, sealed and built, and its start rule and power check are recorded; no K5 list was hashed and K5's confirmation window was
never read. Section 6 gives the reasons; section 7 the decision owed.

## 4. Delegation record

| Agent (description) | Worker file | Model | Effort | Objective | Status | Deviations |
|---|---|---|---|---|---|---|
| HarnessBuilder-OpusXHigh | worker-xhigh | opus | xhigh | A2: the v5 change set (plan section 3), then two follow-ups (R-A2-1/R-A2-2; the review fixes) | done | Stopped on K3's table pins (O-1) as briefed; 11 open points ruled |
| ReleaseChecker-OpusMed | worker-medium | opus | medium | C3: NGS confirmation-window check (started during Part A) | done | none |
| HarnessReviewer-FableXHigh | worker-xhigh | fable | xhigh | A3: independent review of the v5 change | done | none |
| MemberCoder-OpusXHigh | worker-xhigh | opus | xhigh | C3: remove the five NGS rows, update the table test | done | Added a one-off E.5 generator the test loads (committed with the amendment) |
| ConfirmAuditor-K4-FableXHigh | worker-xhigh | fable | xhigh | C3 Part 1: the table audit; C6 Part 2: the recomputation | done (Part 1 and Part 2; no discrepancy) | none |
| ConfirmAuditor-K5-FableXHigh | - | fable | xhigh | Part D recomputation | not spawned (K5 stopped, R-D-1) | - |

## 5. Verification

**Harness review (reports/stage_e5_harness_review.md), rulings in reports/stage_e5_harness_rulings.md:**
| Finding | Class | Ruling | Fix |
|---|---|---|---|
| SF-1 DSR with a one-series variance set silently undeflated | SHOULD FIX | accepted | undefined, and a fail, below 2 series |
| SF-2 blanket strict xfails on K3's pins mask other drift | SHOULD FIX | accepted | exact assertions against v5 (the 14-date difference pinned) |
| N-1 the 2019 lead covers the whole year (2019-01-21, 02-18 move) | NOTE | fact; no store has bars before 2019-05-06 | docstring |
| N-2 July 3 2019 and 2023 keep F 15:08 in every group | NOTE | kept (O-3, unsettled); for the user | none |
| N-3 PBO union over every run trial | NOTE | kept (O-5); immaterial with one Tier A trial | none |
| N-4 undefined PBO reads as a failed step | NOTE | accepted | "no edge (pbo undefined)" |
| N-5 unknown vehicle ends in a traceback | NOTE | accepted | named refusal |
| N-6 unit and window bounds unchecked | NOTE | accepted | two refusals |
| N-7 ENTRY_MODULES does not name the verdict module | NOTE | no change (L-E5-4) | none |
| N-8 closed label vocabulary, freeze ordinals | NOTE | informational | none |
| N-9 a trial can be null and an edge candidate at once | NOTE | the statement stays null; named in the same sentence | none (K4: no such trial) |
| N-10, N-11, N-12 | NOTE | no change | none |

**The builder's open points (O-1..O-11):** O-1 (K3's frozen FX table lists 14 dates v5 flattens at 11:30) ruled R-A2-1 (K3 untouched;
its session decides; question for the user); O-9 ruled R-A2-2 (no test pins the cap values, so v6 differs only in data/config.py);
O-2 (an "(observed)" holiday is ordinary), O-3, O-4 (day_rule governs), O-5, O-6, O-7 accepted.

**Table amendment audit (Part 1):** table diff VERIFIED; drops and keeps VERIFIED WITH NOTES (five drops quoted from the saved captures,
12 keeps checked, 30/30 capture hashes; the note: for the four Friday rows C9's first rule literally compares EIA's actual with its
schedule, which agree, while the table differs: ruling R-C3-2 below); freeze VERIFIED; research series VERIFIED (50 trips identical);
tests VERIFIED.

**Recomputation (Part 2):** items 0 to 6: VERIFIED (1, 2, 4, 5) or VERIFIED WITH NOTES (0, 3, 6); no DISCREPANCY (section 3, Task C6). The lead rules no change on the three notes: none bears on a figure.

## 6. Open choices (each decided by the lead alone, with the reason; each can be overturned)

- **L-E5-1 (gate wiring).** The prompt's A2 (c) names data/config.py only, but data/pull_step2.py's step2_gate read the E.2b names, so an
  E.5 block would never reach the gate. The gate's reading of the active purchase policy was ruled part of (c), reviewed, replayed and
  frozen in v5. A later purchase session now edits only data/config.py (it repoints three names).
- **L-E5-2 (2019-2023 lead).** 30 minutes, the earliest published lead; Topstep's 2019-2023 articles are not held.
- **L-E5-3 (PBO with one Tier A trial).** Over every run trial of the cluster, aligned on the union of window dates (the V14 (c) set).
  Declared in the K4 list before its hash.
- **L-E5-4 (verdict code restated).** D.1f's functions are restated on funnel/ with equality tests, since strategy/research/ is not in
  the harness manifest.
- **L-E5-5 (OC-H-excluded trials).** Listed, not run, not covered; they do not block the statement.
- **Rule H-1's unsettled dates.** Every July 3 (the one date the rule does not reproduce in the published years) gets no row;
  "(observed)" holidays are ordinary (O-2).
- **R-A2-1 / SF-2 (K3).** K3's frozen FX_FULL_SESSIONS lists 14 dates (2022-01-17 .. 2023-11-23) that v5 flattens at 11:30. K3's code
  was not changed; its table tests now pin that exact difference. K4 and K5 are unaffected: every derived date already has an entry in
  the energy and metals calendars.
- **Replays under in-place working-tree manifests** (E.4 H2 precedent). The prompt says every command takes v4 until A4, but v4's
  preflight refuses a changed tree by design; the replay ran under the working-tree manifest (b720c5aa) and again under v5 exactly.
- **C3 started during Part A.** It reads only EIA pages and S_NG can only shorten its window; it saved about an hour.
- **Quote set clusters-legs**, the set the buy path uses; the frozen quote writer updated E.2b's quote files, which were copied to
  reports/stage_e5_step2_quotes.{json,md} and restored to their committed content, so E.2b's record is unchanged.
- **Caps.** Session cap = the headroom in whole cents ($21.52), since quote x 1.10 exceeded it; request cap $3.00 (D13's per-request
  cap; the largest chunk is $0.12).
- **C2's method.** A research re-run under v6 (the runner's own power path), not a direct call, matched to E.4 first.
- **Calendar checks** reporting `passed: false` (early stops inside each root's span) are recorded as data-quality notes: the frozen
  builder wrote every store as "built" and no rule makes them a stop.
- **R-C3-1 / R-C3-2 (NGS drops).** Five rows dropped, none added: for the four Friday weeks, the table's Thursday row names a release
  that did not happen on its date; C9's drop rule is applied to the table E.2 built, and correcting the date is not a drop. The
  auditor calls this an extension of the rule's literal text; the alternative (keeping the rows) would trade four non-release
  Thursdays. The stored reasons keep the checker's words "(lead decides drop vs correction)" verbatim.
- **The K4 freeze rewrite.** The freeze file is write-once, so the old one (cf066cb0..., in git) was removed and a new one written
  with the same declarations; only _releases.py's hash differs.
- **"calendar partly unverified"** stays on K4-ngpre-01 for E.4's three research-window releases; the confirmation window has none.
- **R-D-1 (K5 stopped before its list).** MGC's start rule found no qualifying month, so six of K5's eight tiered trials (the Tier A
  K5-fomc-01 among them) have supply 0 and are inconclusive by design. Running K5 now would spend its one confirmation run on two MHG
  Tier B trials and foreclose U8 (GC bars as MGC's price path, declared before any confirmation read). The v5 verdict module also
  refuses a Tier A or B trial without a record. A decision that cannot be undone and could reasonably go either way: the user's.
- **K5's C1 and C2 ran right after K4's**, not after Part C: both read only volumes and research series.
- **The end suite ran while the auditor's Part 2 ran**; no code changed after it.
- **The pre-commit suite was stopped at the user's pause** (13:58) and rerun on resume.

## 7. What the next session must do first

- **Push (the planning chat).** Local, unpushed: 2c0bfe0 (harness v5), ce3cb66 (harness v6), 41d6adf (K4 C9 table amendment), 4161032
  (K4 confirmation list). Uncommitted for review: this file, reports/stage_e5_STATE.md, the verdicts (reports/stage_e5_k4_verdicts.md and
  .json), the audit's Part 2, the purchase report and quote record (reports/stage_e5_purchase.md, reports/stage_e5_step2_quotes.*), the
  K5 start-rule and power outputs, the builder's report, the runner outputs (reports/stage_e5_k4_confirmation/, _power_k4/, _power_k5/,
  _replay_*), the briefs, the ledger (+2,577 lines), docs/HOLDOUT_UNLOCK_LOG.md (+52 seal entries), docs/ACCESS.md if touched, progress.md
  and docs/STAGES.md.
- **Hashes in force.** Harness v6 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87 (v5 and v4 refused). Cluster freezes: K2
  8815a775..., K4 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a, K5 1d0c974f..., K3 c4fb5da4.... K4 list 22388c6b....
  Start-rule files reports/stage_e_start_rule_K4.json (523f2e25...) and _K5.json (d5965f17...).
- **acct-2:** $124.673761 spent of $125.00; **$0.326239 left**. Any further purchase needs a top-up and a cap raise.
- **K4 is done:** null. Its Tier A trial fails Holm (p 0.54); no composite is built.
- **Questions for the user.**
  1. **K5 (U8):** (a) declare full-size GC bars as MGC's price path (D2, D4, U8). That needs GC's step 2 history ($7.548369 quoted in
     E.2b, $8.30 with +10%), a top-up of about $7.23 ($7.98 with +10%), a higher ACCOUNT_2_CAP_USD, a start rule on GC and a declaration
     before K5's list. Or (b) run K5 now with the MGC trials inconclusive by design, so only cp3 MHG and ovr MHG are tested. That
     forecloses (a) under one confirmation run per cluster, and needs a harness change first: the verdict module must accept a Tier A or
     B trial with no record. MGC's power needs are small (n_b 1 to 62 days), so with a window it would be testable.
  2. **K3's FX table (R-A2-1):** amend K3's FX_FULL_SESSIONS for the 14 dates v5 flattens at 11:30 (K3-L-11's rule), or keep it,
     before K3's confirmation.
  3. **The July 3 dates (N-2):** 2019-07-03 and 2023-07-03 keep the regular flatten in every group; accept, or rule a July 3 row.
  4. **The four NGS Thursdays (R-C3-2):** dropped rather than corrected; accept.
  5. **Data quality:** the frozen release calendar's five wrong NGS rows (2019-12-26, 2020-01-02, 2020-11-12, 2021-01-21, 2023-11-09)
     also drive the engine's D9.5a release guard and event costs on those dates for every NG member; and the step 2 stores' early-stop
     notes (section 3, B2).
  6. Carried: the E.4 questions still open (K4-L-15, the liquidation-dependent tiers, counting N on screened trials, OC-Q's composite
     for a later edge candidate).

## 8. Session cost

**Final ETA table** (PDT; tokens from the transcripts; pauses shown as their own rows and excluded from the work total):

| Task | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Startup, start suite | lead | opus | xhigh | 12:23 | 12:37 | 14 min | in lead | done |
| A1 Inventory, plan, rulings | lead | opus | xhigh | 12:27 | 12:37 | 10 min | in lead | done |
| A2 Change set (+ 2 follow-ups) | HarnessBuilder-OpusXHigh | opus | xhigh | 12:36 | 13:41 | 65 min | 37,076,657 | done; K3 stop point ruled (R-A2-1) |
| C3 NGS check (started during Part A) | ReleaseChecker-OpusMed | opus | medium | 12:36 | 13:26 | 50 min | 8,593,252 | done; moved ahead of B2 |
| A3 Replays (b720c5aa), suite | lead | opus | xhigh | 13:13 | 13:28 | 15 min | in lead | done |
| A3 Review | HarnessReviewer-FableXHigh | fable | xhigh | 13:18 | 13:37 | 19 min | 3,101,653 | done |
| A4 Fixes, v5 manifest, v5 replays | lead | opus | xhigh | 13:33 | 13:50 | 17 min | in lead | done |
| PAUSE: machine crash | - | - | - | 13:50 | 13:53 | 3 min | - | excluded |
| A4 Suite (stopped for the pause) | lead | - | - | 13:54 | 13:58 | 4 min | in lead | stopped, rerun |
| PAUSE: user (usage) | - | - | - | 13:58 | 17:35 | 217 min | - | excluded |
| A4 Resume checks, suite, v5 commit 2c0bfe0 | lead | opus | xhigh | 17:35 | 17:53 | 18 min | in lead | done |
| B1 Quote, caps, v6 commit ce3cb66 | lead | opus | xhigh | 17:53 | 18:13 | 20 min | in lead | done |
| B2 Buy K4, buy K5, status, bars, report | lead | opus | xhigh | 18:13 | 18:52 | 39 min | in lead | done; $21.196568 = quote |
| C1 Start rules K4, K5 | lead | opus | xhigh | 18:52 | 18:53 | 1 min | in lead | done; S_MGC empty |
| C2 Power re-runs K4, K5 | lead | opus | xhigh | 18:54 | 19:00 | 6 min | in lead | done; R-D-1 (K5 stopped) |
| C3 Table amendment | MemberCoder-OpusXHigh | opus | xhigh | 18:59 | 19:07 | 8 min | 4,998,610 | done |
| C3 Freeze, audit Part 1, commit 41d6adf | lead + ConfirmAuditor-K4-FableXHigh | opus / fable | xhigh | 19:05 | 19:14 | 9 min | auditor below | done |
| C4 K4 list, commit 4161032 | lead | opus | xhigh | 19:14 | 19:15 | 1 min | in lead | done |
| C5 K4 run (once), verdicts | lead | opus | xhigh | 19:15 | 19:23 | 8 min | in lead | done: null |
| C6 Recomputation (Part 2) | ConfirmAuditor-K4-FableXHigh | fable | xhigh | 19:23 | 19:31 | 8 min | 4,238,978 (Parts 1 and 2) | done: no discrepancy |
| Part D K5 (C4-C6) | - | - | - | - | - | - | - | not run (R-D-1); ConfirmAuditor-K5 not spawned |
| End suite, end checks, return, cost | lead | opus | xhigh | 19:23 | 19:43 | 20 min | in lead | done |
| **Stage** | | | | 12:23 | 19:43 | **7 h 20 min wall, 3 h 40 min of work excluding the 3 h 40 min of pauses** | **146,528,258** (lead 88,519,108, 60%; workers 58,009,150, 40%) | estimate was about 9 h of work to 21:30 (22:45 with the table amendment); K5 stopped at C2, which removed about 1.5 h |

**Tokens per model** (the lead transcript b56ee083's .jsonl, which also holds the two resumed sessions' messages, plus every worker
transcript under its subagents/ folder, from 12:00 PDT to the end; messages de-duplicated by message and request id;
reports/stage_e5_briefs/cost.out; the lead's last messages after the count are not included):

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,322 | 3,670 | 6,656,181 | 679,458 | 7,340,631 |
| claude-opus-5-5 | 1,090 | 278,565 | 136,021,295 | 2,886,677 | 139,187,627 |
| all | 2,412 | 282,235 | 142,677,476 | 3,566,135 | 146,528,258 |

**Per worker spawn:**
- MemberCoder-OpusXHigh (worker-xhigh, opus, xhigh; C3 table amendment): 4,998,610 tokens, 18:59-19:07
- ConfirmAuditor-K4-FableXHigh (worker-xhigh, fable, xhigh; C3 audit Part 1 + C6 recomputation Part 2): 4,238,978 tokens, 19:08-19:31
- HarnessReviewer-FableXHigh (worker-xhigh, fable, xhigh; A3 review): 3,101,653 tokens, 13:18-13:37
- HarnessBuilder-OpusXHigh (worker-xhigh, opus, xhigh; A2 change set + 2 follow-ups): 37,076,657 tokens, 12:36-13:41
- ReleaseChecker-OpusMed (worker-medium, opus, medium; C3 NGS check): 8,593,252 tokens, 12:36-13:26

**Delegation share:** lead 60.4%, workers 39.6%; by tier opus 95.0%, fable 5.0%. About 97% of all tokens are
cache reads, as in E.0 and E.2a. These are token counts, not plan-credit percentages; the /usage meter is the user's to read.
