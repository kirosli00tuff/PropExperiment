# Stage E.21 return: multi-day round (TSMOM-12, trend blend, turn of the month, combined book) on 17 roots, 2010-2024; all four FAIL; N = 532

Prompt docs/prompts/STAGE_E.21.md. Lead Opus 5.5 xhigh, ultracode on, session 13fe2d4e-086f-4929-8325-9ef707bdf0cf, 2026-10-14 03:04-04:40 PDT, unattended. All times PDT (America/Vancouver).

## 1. Verdict summary

**All four tests FAIL.** This is the base case, under Holm step-down at family alpha 0.025. Every
number was recomputed independently by VerdictVerifier-FableXHigh (VERIFIED WITH NOTES, 152 numbers
matched, 0 BLOCKING).

| Test | Net Sharpe [95% CI] | t | p | Fills | Costs / gross |
|---|---|---|---|---|---|
| T1 TSMOM-12 | 0.50 [-0.06, 1.05] | 1.78 | 0.042 | 4,081 | 7.2% |
| T2 trend blend | 0.44 [-0.11, 0.98] | 1.56 | 0.064 | 4,081 | 9.8% |
| T3 turn of month | 0.15 [-0.40, 0.71] | 0.53 | 0.30 | 454 | 21.2% |
| T4 combined book | 0.12 [-0.37, 0.60] | 0.43 | 0.34 | n/a | n/a |

- **T1 and T2 clear the 0.3 Sharpe bar but not Holm**, whose first step needs p ≤ 0.00625. Each is
  a FAIL with a positive point estimate: underpowered, not refuted. A Sharpe of 0.5 would need about
  25 years of data to pass.
- **Published comparison, same window:** AQR's TSMOM factor 0.39 gross; SG Trend 0.35 net (0.24 over
  2010-2025). T3 matches the post-2008 decay of the turn-of-month effect.
- **T4's statistic is dominated by three spikes** from H5's scaling.
- **New N = 532.** The holdout is sealed (0 unlocks), nothing was bought, and the ledger is unchanged.
- **Personal account:** holding the 17-root trend book at one contract or more per root needs about
  $415K-$691K (T1) or $323K-$538K (T2). Live cattle is the binding root.
- **PropEd:** no public page grants automation for any plan. The trend books cannot be held there:
  roots are not listed, and 46-100% of 21-day windows breach the drawdown (One Plan 24-57%). Phidias
  Premium 50K matches PropEd's $2,500 plans. No purchase is recommended.

## 2. Guardrail evidence

### Start checks (verbatim; reports/stage_e21_briefs/start_checks.txt)

```
$ date
Wed Oct 14 03:10:05 PDT 2026
$ git status --short
[928 untracked paths (?? lines) omitted here; full list in reports/stage_e21_briefs/start_checks.txt]
$ git log --oneline -3
03cdf50 docs: Stage E.21 prompt (multi-day round, PropEd main venue) and V38
2237731 Stage E.20 pattern search
498fd05 E.20 H6 freeze
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32
preflight OK: ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K6 cluster freeze OK a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 27 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K8 cluster freeze OK 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 4 members
$ ledger
36402 ledger/databento_spend.jsonl
034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 353.455228 cap 355.38 headroom 1.924772
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
$ uv run python -m screening.trial_registry status
N = 528 (6 lines)
r001-C1: C1 ['C1-T1', 'C1-T2'] N 471 -> 473 at 2026-10-09T19:29:06-07:00
r002-E16: E16 ['E16-H1', 'E16-H2', 'E16-H3', 'E16-H4', 'E16-H5'] N 473 -> 478 at 2026-10-10T00:30:15-07:00
r003-C1b: C1b ['C1b-T1', 'C1b-T2'] N 478 -> 480 at 2026-10-10T12:17:48-07:00
r004-E20H6: E20H6 ['E20H6-T1', 'E20H6-T2', 'E20H6-T3'] N 480 -> 483 at 2026-10-11T15:36:20-07:00
r005-E20S: E20S ['E20S-01', 'E20S-02', 'E20S-03', 'E20S-04', 'E20S-05', 'E20S-06', 'E20S-07', 'E20S-08', 'E20S-09', 'E20S-10', 'E20S-11', 'E20S-12', 'E20S-13', 'E20S-14', 'E20S-15', 'E20S-16', 'E20S-17', 'E20S-18', 'E20S-19', 'E20S-20', 'E20S-21', 'E20S-22', 'E20S-23', 'E20S-24', 'E20S-25', 'E20S-26', 'E20S-27', 'E20S-28', 'E20S-29', 'E20S-30', 'E20S-31', 'E20S-32', 'E20S-33', 'E20S-34', 'E20S-35', 'E20S-36', 'E20S-37', 'E20S-38', 'E20S-39', 'E20S-40', 'E20S-41', 'E20S-42', 'E20S-43', 'E20S-44', 'E20S-45'] N 483 -> 528 at 2026-10-11T17:43:59-07:00
$ wc -l ledger/trial_registrations.jsonl; sha256sum
6
2acc993e741fc0745f50947f534d7da753368a2551fb4b705e3c3d583ce11a8d
$ E.14 C1 freeze (reports/stage_e14_prereg_C1.md; pinned afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b): sha256, tracked, no diff vs HEAD, commits touching
afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b
tracked
no diff vs HEAD
1680982 
$ E.14 C1 freeze inputs list (reports/stage_e14_c1_freeze_inputs.json; pinned 3356d676...)
list sha256 3356d67604245db99383215f1fb7f694d25a1beb71b0693a86faeb7243a5140e entries 43 mismatches ['reports/stage_e2b_harness_freeze.json']
$ E.16 freeze: uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4
E.16 freeze OK: 97 files; manifest sha256 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4
exit 0
$ git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md
exit 0
$ E.18 C1b freeze: uv run python reports/stage_e18_briefs/freeze_manifest.py verify --expected 5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03
E.18 C1b freeze OK: 48 files, 10 external; manifest sha256 5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03
exit 0
$ git diff --quiet b714751 -- c1_replication/c1b.py tests/test_c1b.py reports/stage_e18_prereg_C1b.md reports/stage_e18_freeze.json
exit 0
$ git diff --quiet HEAD -- ml_route_v2 rules sim screening data/holdout.py live ops
exit 0
$ E.20 store sha256 (17 roots; step2 search stores and the ext2010/ext2010h backward stores, hashed as bytes, never decoded) vs reports/stage_e17_run_manifest.json
stores checked 34 mismatches []
$ E.20 H6 freeze: PYTHONPATH=. uv run python reports/stage_e20_briefs/h6_freeze_manifest.py verify 22e606f0b74532e267a4155d93e295702ff86f6e8f4143236882f3c2f230e795
manifest 22e606f0b74532e267a4155d93e295702ff86f6e8f4143236882f3c2f230e795 expected 22e606f0b74532e267a4155d93e295702ff86f6e8f4143236882f3c2f230e795 match True files 91 bad []
exit 0
$ E.20 search freeze: uv run python -m pattern_search.freeze_manifest verify --sha256 94ee86b02d1cb644c9307be958b7791587d42c062996a6220dc901d4fe5a0f2f
verified reports/stage_e20_search_freeze.json: 117 files
exit 0
$ E.21 freeze: uv run python -m multiday.freeze_manifest verify (written at Step 3)
not yet written
$ uv run pytest -q -p no:cacheprovider (detached, 03:10-03:31)
7340 passed, 3 skipped, 3 xfailed, 54 warnings in 1222.16s (0:20:22)
rc 0
```

The E.14 inputs-list mismatch on reports/stage_e2b_harness_freeze.json is pre-existing and identical at E.20's start and end (the harness freeze file was rewritten for v12 after E.14).

### End checks (verbatim; reports/stage_e21_briefs/end_checks.txt)

```
$ date
Wed Oct 14 04:35:56 PDT 2026
$ git status --short
 M ledger/trial_registrations.jsonl
 M reports/stage_e21_STATE.md
[1045 untracked paths (?? lines) omitted here; full list in reports/stage_e21_briefs/end_checks.txt]
$ git log --oneline -3
839efc9 E.21 freeze
03cdf50 docs: Stage E.21 prompt (multi-day round, PropEd main venue) and V38
2237731 Stage E.20 pattern search
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32
preflight OK: ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K6 cluster freeze OK a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 27 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K8 cluster freeze OK 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 4 members
$ ledger
36402 ledger/databento_spend.jsonl
034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 353.455228 cap 355.38 headroom 1.924772
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
$ uv run python -m screening.trial_registry status
N = 532 (7 lines)
r001-C1: C1 ['C1-T1', 'C1-T2'] N 471 -> 473 at 2026-10-09T19:29:06-07:00
r002-E16: E16 ['E16-H1', 'E16-H2', 'E16-H3', 'E16-H4', 'E16-H5'] N 473 -> 478 at 2026-10-10T00:30:15-07:00
r003-C1b: C1b ['C1b-T1', 'C1b-T2'] N 478 -> 480 at 2026-10-10T12:17:48-07:00
r004-E20H6: E20H6 ['E20H6-T1', 'E20H6-T2', 'E20H6-T3'] N 480 -> 483 at 2026-10-11T15:36:20-07:00
r005-E20S: E20S ['E20S-01', 'E20S-02', 'E20S-03', 'E20S-04', 'E20S-05', 'E20S-06', 'E20S-07', 'E20S-08', 'E20S-09', 'E20S-10', 'E20S-11', 'E20S-12', 'E20S-13', 'E20S-14', 'E20S-15', 'E20S-16', 'E20S-17', 'E20S-18', 'E20S-19', 'E20S-20', 'E20S-21', 'E20S-22', 'E20S-23', 'E20S-24', 'E20S-25', 'E20S-26', 'E20S-27', 'E20S-28', 'E20S-29', 'E20S-30', 'E20S-31', 'E20S-32', 'E20S-33', 'E20S-34', 'E20S-35', 'E20S-36', 'E20S-37', 'E20S-38', 'E20S-39', 'E20S-40', 'E20S-41', 'E20S-42', 'E20S-43', 'E20S-44', 'E20S-45'] N 483 -> 528 at 2026-10-11T17:43:59-07:00
r006-E21: E21 ['E21-T1', 'E21-T2', 'E21-T3', 'E21-T4'] N 528 -> 532 at 2026-10-14T04:12:12-07:00
$ wc -l ledger/trial_registrations.jsonl; sha256sum
7
085ed33c1d88ad517c8346bde1b71fbd0116c77ed7d28346f0bb7d4ea62e4831
$ E.14 C1 freeze (reports/stage_e14_prereg_C1.md; pinned afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b): sha256, tracked, no diff vs HEAD, commits touching
afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b
tracked
no diff vs HEAD
1680982 
$ E.14 C1 freeze inputs list (reports/stage_e14_c1_freeze_inputs.json; pinned 3356d676...)
list sha256 3356d67604245db99383215f1fb7f694d25a1beb71b0693a86faeb7243a5140e entries 43 mismatches ['reports/stage_e2b_harness_freeze.json']
$ E.16 freeze: uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4
E.16 freeze OK: 97 files; manifest sha256 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4
exit 0
$ git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md
exit 0
$ E.18 C1b freeze: uv run python reports/stage_e18_briefs/freeze_manifest.py verify --expected 5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03
E.18 C1b freeze OK: 48 files, 10 external; manifest sha256 5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03
exit 0
$ git diff --quiet b714751 -- c1_replication/c1b.py tests/test_c1b.py reports/stage_e18_prereg_C1b.md reports/stage_e18_freeze.json
exit 0
$ git diff --quiet HEAD -- ml_route_v2 rules sim screening data/holdout.py live ops
exit 0
$ E.20 store sha256 (17 roots; step2 search stores and the ext2010/ext2010h backward stores, hashed as bytes, never decoded) vs reports/stage_e17_run_manifest.json
stores checked 34 mismatches []
$ E.20 H6 freeze: PYTHONPATH=. uv run python reports/stage_e20_briefs/h6_freeze_manifest.py verify 22e606f0b74532e267a4155d93e295702ff86f6e8f4143236882f3c2f230e795
manifest 22e606f0b74532e267a4155d93e295702ff86f6e8f4143236882f3c2f230e795 expected 22e606f0b74532e267a4155d93e295702ff86f6e8f4143236882f3c2f230e795 match True files 91 bad []
exit 0
$ E.20 search freeze: uv run python -m pattern_search.freeze_manifest verify --sha256 94ee86b02d1cb644c9307be958b7791587d42c062996a6220dc901d4fe5a0f2f
verified reports/stage_e20_search_freeze.json: 117 files
exit 0
$ E.21 freeze: uv run python -m multiday.freeze_manifest verify (written at Step 3)
freeze verified: 18 inputs
exit 0
$ uv run pytest -q -p no:cacheprovider (detached, 04:15-04:35)
7402 passed, 3 skipped, 3 xfailed, 54 warnings in 1233.43s (0:20:33)
rc 0 end 04:35:48
```

Changed between start and end: ledger/trial_registrations.jsonl gained line 7 (r006-E21; 6 -> 7 lines, sha256 2acc993e... -> 085ed33c...); the spend ledger is unchanged (36,402 lines, 034a454b...). Harness v12 is unchanged and was verified at start and end with a fresh PYTHONPYCACHEPREFIX. No file under live/, ops/, screening/, rules/, sim/, data/holdout.py or base_rules/ changed. Nothing dated 2024-03-01 or later was read (the stores end 2024-02-29 and base_rules refuses later dates). No TopstepX call, no Databento call, no push. Peak memory of the evaluation 1.47 GB (nice 10); at most two heavy jobs at once (the verifier and the end pytest).

### Order of events

| Event | Time (PDT) | Evidence |
|---|---|---|
| Prompt commit | 2026-10-14 03:03:14 | 03cdf50 (git) |
| Start checks | 03:10:05 | reports/stage_e21_briefs/start_checks.txt |
| Literature check (4 readers) | 03:13-03:33 | workflow wf_18fed4b8-d89; spec_*.md mtimes 03:19-03:33 |
| Literature rulings A1-A11 | 03:35 | lead_spec section A |
| Calendar-only counts (no bar row); A12 ruling | 03:42-03:50; 03:48 | calendar_counts.json written 03:42:22, re-run 03:50:38 |
| Freeze review | 03:51-04:02; recheck 04:07-04:10 | reports/stage_e21_review_freeze.md (mtime 04:09:54) |
| Freeze manifest | 04:11:30 | reports/stage_e21_freeze.json sha256 0bb899e5... |
| Freeze commit | 04:12:01 | 839efc9 "E.21 freeze" (git) |
| Registration | 04:12:12 | r006-E21, ledger/trial_registrations.jsonl line 7 |
| Run-once marker (before any bar) | 04:12:28 | reports/stage_e21_RUN_ONCE.json |
| Evaluation complete | 04:14:35 | reports/stage_e21_runs/verdict.json |
| Verification | 04:15-04:35 | reports/stage_e21_review_verdict.md (mtime 04:35:29) |
| End checks | 04:35:56 | reports/stage_e21_briefs/end_checks.txt |

## 3. Results

### 3.1 Literature check (Step 1; before any bar)

Each F4 rule was checked against its primary source. The quotes are in the reader reports:
reports/stage_e21_briefs/spec_trend.md, spec_tom.md and spec_post2010.md. The rulings are in
lead_spec section A.

| Item | Primary source | Result | Freeze |
|---|---|---|---|
| T1 signal, hold, 40%/sigma, equal-weight average | MOP 2012, pp.231-236 | MATCH | as F4 |
| T1/T2 lookback across rolls | MOP p.231 (compounds the held contract's daily returns) | MATCH. h2.chained_return splits at every recorded splice; the reader's "MISMATCH risk" was rejected (A1) | lead_spec 1 |
| Volatility: 261, EWMA-mean demeaning, returns strictly before d | MOP eq. 1, p.233 | Prompt SILENT; the paper's terms adopted | lead_spec 2 |
| Warm-up, floor, cap | MOP: none | SILENT; 60 returns [LEAD]; no floor and no cap | A3, A4 |
| T2: 1/3/12 lookbacks, equal weights, monthly | HOP 2017, p.3 | MATCH | as F4 |
| T2 book scaled to a 10% ex-ante volatility (3-year covariance) | HOP 2017, p.3 and endnote 7 | MISMATCH, NOT adopted; declared deviation (A6) | T2 as F4 |
| T3 window: days -1, +1, +2, +3, close to close | McConnell-Xu (WP Table 1); Lakonishok-Smidt via McConnell-Xu | MATCH | day -2 = the month's second-to-last trade date |
| T3 parenthetical "(two trade dates before the month's last)" | as above | MISMATCH: it describes day -3; corrected (A8) | lead_spec 5 |
| T3 day numbering | the papers count NYSE trading days | MISMATCH, found in the calendar-only counts: the futures calendar books US holidays as trade dates; T3 renumbered on NYSE days (A12) | lead_spec 5, A12 |
| T3 volatility scaling | the papers do not scale | the prompt's choice, kept | lead_spec 5 |

Published post-2010 comparison (not part of any verdict):

| Source | Period | Universe | Gross / net | Sharpe | Where |
|---|---|---|---|---|---|
| AQR TSMOM factor (MOP update; computed by SpecReaderPost2010 from AQR's file) | 2010-07..2024-02 (164 months) | AQR's MOP universe | gross (no costs or fees) | 0.389 (t 1.44) | spec_post2010.md P1 |
| Same | 2010-01..2026-05 | same | gross | 0.402 (t 1.63) | P2 |
| SG Trend Index (computed from AQR's fund workbook) | 2010-07..2024-02 | about 10 largest trend CTAs | net of fees and costs | 0.352 (t 1.30) | P4 |
| SG Trend Index (E.13) | 2010-2025 | same | net | 0.24 | P5; stage_e13_trend_carry.md |
| HOP 2017 Exhibit 2: 12-month signal | 2010-2016 | 67 markets | gross | 0.73 | spec_trend.md (read from an exhibit image by eye; not checked by a second reader) |
| HOP 2017 Exhibit 1: the 1/3/12 blend | 2010-2016 | 67 markets | net of costs and 2/20 fees | 0.41 | same caveat |
| Turn of the month, McConnell-Xu | 1987-2005 (after Lakonishok-Smidt) | US cash indexes | gross | 0.15%/day vs -0.00% on other days (t 3.78); weaker in the second half (t 2.00) | spec_tom.md |
| Turn of the month after 2008 | 2010-2018 (Plastun et al., DJIA) and others | cash indexes | gross | mostly decayed (DJIA 0.03%/day on TOM days vs 0.05% on other days) | spec_tom.md |
| Turn of the month in index futures after 2010 | none found | - | - | no peer-reviewed study | spec_post2010.md section 3 |

E.21's T1 (0.50 net) and T2 (0.44 net) sit at or a little above these post-2010 records, after D8
costs, on 17 roots. T3 (0.15) agrees with the decay literature.

### 3.2 PropEd Capital's sourced rules (PropEdReader-OpusHigh)

PropEd's terms (last updated 2026-10-06) forbid "scraping without permission", while robots.txt
allows `/`. The reader therefore made plain one-page fetches only, about 4 s apart, and listed every
saved PropEd page in DO_NOT_COMMIT.txt (kept local, not committed).

**Automation is unresolved.** Terms section 8 says "Copy trading and automated strategies may be used
only where supported and permitted". The FAQ marks "EAs / Bots / Automated" with a red not-allowed
icon. Terms section 5 says the FAQs do not override the plan agreement or the Nexus dashboard, and
neither is public. No public page grants automation for any plan.

**Other rules:**
- Overnight holds are allowed.
- Weekend holds need a paid add-on.
- Listed micros: MES, MNQ, M2K, MGC and MCL. M6E and the micro yield futures are not listed.
- Canada is not on the restricted-countries list.

Ten written questions for PropEd are drafted in reports/stage_e21_proped_rules.md for the user to
send. Nothing was sent.

#### PropEd rule table (generated from reports/stage_e21_proped_rules.json)

Source: reports/stage_e21_proped_rules.md and .json (PropEdReader-OpusHigh; fetched 2026-10-14T03:14:05-07:00/2026-10-14T03:20:24-07:00); every value carries a quote id there. UNSOURCED = no public primary source.

| Plan | Size | Price | Drawdown (type; amount) | Daily loss limit | Overnight | Weekend (add-on price) | Automation | Max contracts |
|---|---|---|---|---|---|---|---|---|
| Standard Eval - 25k | 25000 | 109 | EOD ("(eod)"; whether it trails is not …; 1000 | UNSOURCED | yes (FAQ Q21; terms Q02… | with add-on (Q22,… (16.35) | CONFLICT, not resolved: terms s.8 "… | 3 minis / 30 micros |
| Standard Eval - 50k | 50000 | 175 | EOD ("(eod)"; whether it trails is not …; 2000 | UNSOURCED | yes (FAQ Q21; terms Q02… | with add-on (Q22,… (26.25) | CONFLICT, not resolved: terms s.8 "… | 5 minis / 50 micros |
| Standard Eval - 100k | 100000 | 285 | EOD ("(eod)"; whether it trails is not …; 4000 | UNSOURCED | yes (FAQ Q21; terms Q02… | with add-on (Q22,… (42.75) | CONFLICT, not resolved: terms s.8 "… | 10 minis / 100 micros |
| Standard Eval - 150k | 150000 | 365 | EOD ("(eod)"; whether it trails is not …; 6000 | UNSOURCED | yes (FAQ Q21; terms Q02… | with add-on (Q22,… (54.75) | CONFLICT, not resolved: terms s.8 "… | 15 minis / 150 micros |
| Instant Funding - 50k | 50000 | 599 | EOD ("(eod)"; trailing not stated); 2500 | UNSOURCED | yes (FAQ Q21; terms Q02… | with add-on (Q22,… (89.85) | CONFLICT, not resolved: terms s.8 "… | 3 minis / 30 micros |
| Instant Funding - 100k | 100000 | 949 | EOD ("(eod)"; trailing not stated); 5000 | UNSOURCED | yes (FAQ Q21; terms Q02… | with add-on (Q22,… (142.35) | CONFLICT, not resolved: terms s.8 "… | 6 minis / 60 micros |
| Instant Funding - 150k | 150000 | 1299 | EOD ("(eod)"; trailing not stated); 7500 | UNSOURCED | yes (FAQ Q21; terms Q02… | with add-on (Q22,… (194.85) | CONFLICT, not resolved: terms s.8 "… | 9 minis / 90 micros |
| TrueRisk Eval - 1.25k | 1250 | 249 | CONFLICT: Static (plan page, plan compa…; 1250 | UNSOURCED | yes (FAQ Q21; terms Q02… | with add-on (Q24,… (UNSOURCED ("avail…) | CONFLICT, not resolved: terms s.8 "… | 1 minis / 15 micros |
| TrueRisk Eval - 2.5k | 2500 | 449 | CONFLICT: Static (plan page, plan compa…; 2500 | UNSOURCED | yes (FAQ Q21; terms Q02… | with add-on (Q24,… (UNSOURCED ("avail…) | CONFLICT, not resolved: terms s.8 "… | 3 minis / 30 micros |
| TrueRisk Eval - 5k | 5000 | 899 | CONFLICT: Static (plan page, plan compa…; 5000 | UNSOURCED | yes (FAQ Q21; terms Q02… | with add-on (Q24,… (UNSOURCED ("avail…) | CONFLICT, not resolved: terms s.8 "… | 6 minis / 60 micros |
| TrueRisk Eval - 10k | 10000 | 1499 | CONFLICT: Static (plan page, plan compa…; 10000 | UNSOURCED | yes (FAQ Q21; terms Q02… | with add-on (Q24,… (UNSOURCED ("avail…) | CONFLICT, not resolved: terms s.8 "… | 12 minis / 120 micros |
| TrueRisk - Instant Funded - 2.5k | 2500 | 799 | CONFLICT: Static (plan page, plan compa…; 2500 | UNSOURCED | yes (FAQ Q21; terms Q02… | with add-on (Q26,… (89.85) | CONFLICT, not resolved: terms s.8 "… | 3 minis / 30 micros |
| TrueRisk - Instant Funded - 5k | 5000 | 1199 | CONFLICT: Static (plan page, plan compa…; 5000 | UNSOURCED | yes (FAQ Q21; terms Q02… | with add-on (Q26,… (89.85) | CONFLICT, not resolved: terms s.8 "… | 6 minis / 60 micros |
| TrueRisk - Instant Funded - 7.5k | 7500 | 1599 | CONFLICT: Static (plan page, plan compa…; 7500 | UNSOURCED | yes (FAQ Q21; terms Q02… | with add-on (Q26,… (194.85) | CONFLICT, not resolved: terms s.8 "… | 9 minis / 90 micros |
| TrueRisk - Instant Funded - 10k | 10000 | 1999 | CONFLICT: Static (plan page, plan compa…; 10000 | UNSOURCED | yes (FAQ Q21; terms Q02… | with add-on (Q26,… (194.85) | CONFLICT, not resolved: terms s.8 "… | 9 minis / 90 micros |
| One Plan - 750k | 750000 | 1095 | trailing EOD, locks at starting balance…; 37500 | 11250 | general FAQ statement o… | UNSOURCED (no add… (UNSOURCED) | CONFLICT, not resolved: terms s.8 "… | 75 minis / 750 micros |
| Nexus X5 Evaluation - 50k | 50000 | 10 (launch offer, first… | trailing EOD (Q87); 2500 | UNSOURCED | general FAQ statement o… | UNSOURCED (UNSOURCED) | CONFLICT, not resolved: terms s.8 "… | 5 minis / 50 micros |
| Phidias Premium 50K | 50000 | UNSOURCED (accounts pag… | EOD trailing; on CASH stops trailing at…; 2500 | None | True | True (None) | semi-automated only: "Only semi-aut… | 10 E-mini / 100 micro |

Canada (BC): not excluded by the published list: restricted list is AF, BY, CU, IR, LY, KP, RU, SY, YE and "If your country is not listed, you are welcome to register." (Q120, Q121); terms put the legality check on the customer (Q11). No Canada- or BC-specific statement found: BC eligibility itself UNSOURCED.

Conflicts recorded by the reader: 7
- {"id": "C1", "topic": "automation", "a": ["Q04"], "b": ["Q20"], "also": ["Q08", "Q07"], "text": "Terms s.8 permit automated strategies \"only where supported and permitted\"; the FAQ marks \"EAs / Bots / Automated\" not allowed (red x) while marking copy trading allowed. Terms s.5 says FAQs do not …
- {"id": "C2", "topic": "TrueRisk drawdown type", "a": ["Q48", "Q71"], "b": ["Q72", "Q73"], "text": "Plan pages and Plan Comparison label TrueRisk drawdown \"(Static)\"; FAQ Drawdowns lists type \"Eod\" for the same plans."}
- {"id": "C3", "topic": "activation fee", "a": ["Q110", "Q111"], "b": ["Q58", "Q88"], "text": "FAQ Real-Time Passing says PropEd does not charge an activation fee; One Plan has a $299 activation fee and X5 a $99 pay-after-pass charge."}
- {"id": "C4", "topic": "One Plan payout cap", "a": ["Q76", "Q58"], "b": ["Q56"], "text": "Payouts FAQ and One Plan page: $2,500 per payout; One Plan catalog row on the plan page: \"Not specified\"."}
- {"id": "C5", "topic": "price shown", "a": ["Q75", "Q81", "Q58"], "b": ["Q42", "Q56"], "text": "FAQ tables and the One Plan page show the catalog price ($175; \"$1,095 One-time\"); plan pages show that price struck through beside half of it ($87.50; $547.50). Which one checkout charges, and for how …
- {"id": "C6", "topic": "One Plan rules page missing", "a": ["Q63"], "b": ["Q125"], "text": "One Plan page points to \"Full rules on the One Plan FAQ\"; /faq/one-plan-evaluation returns HTTP 404 (twice) and has no Wayback capture."}
- {"id": "C7", "topic": "weekend add-on table shape", "a": ["Q26"], "b": ["Q30"], "text": "TrueRisk Instant Funded has four sizes but the add-on row gives three prices for \"$2.5k / $5k / $7.5k-$10k\"; the mapping of $194.85 to both 7.5k and 10k is read from the \"$7.5k-$10k\" label, not stated per s…

### 3.3 Per-test results (generated from reports/stage_e21_runs/ by reports/stage_e21_briefs/ret_tables.py)

### Verdict table (base case; Holm step-down at family alpha 0.025; N 532)

| Test | n | mean (capital units/day) | sd | t | t NW | p (t) | p (NW) | p | Sharpe (ann.) | 95% CI | Holm rejects | Sharpe >= 0.3 | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | 3205 | 0.00032871 | 0.0104765 | 1.776 | 1.729 | 0.0379 | 0.0419 | 0.0419 | 0.498 | [-0.063, 1.053] | False | True | FAIL |
| T2 | 3205 | 0.000224288 | 0.00815743 | 1.557 | 1.525 | 0.0598 | 0.0637 | 0.0637 | 0.436 | [-0.109, 0.982] | False | True | FAIL |
| T3 | 3319 | 0.000101562 | 0.0110445 | 0.530 | 0.523 | 0.2982 | 0.3003 | 0.3003 | 0.146 | [-0.399, 0.706] | False | False | FAIL |
| T4 | 3331 | 0.0558588 | 7.58019 | 0.425 | 0.430 | 0.3353 | 0.3335 | 0.3353 | 0.117 | [-0.369, 0.600] | False | False | FAIL |

### Cost cases (reported; the prompt's stress case is 1.5 x slippage)

| Test | Case | t | p | Sharpe | gross | costs | net | costs / gross |
|---|---|---|---|---|---|---|---|---|
| T1 | base (D8) | 1.776 | 0.0419 | 0.498 | 1.1352 | 0.0817 | 1.0535 | 0.072 |
| T1 | D8 + 1 tick/side | 1.614 | 0.0583 | 0.453 | 1.1352 | 0.1778 | 0.9574 | 0.157 |
| T1 | 1.5 x slippage | 1.726 | 0.0465 | 0.484 | 1.1352 | 0.1112 | 1.0240 | 0.098 |
| T2 | base (D8) | 1.557 | 0.0637 | 0.436 | 0.7973 | 0.0785 | 0.7188 | 0.098 |
| T2 | D8 + 1 tick/side | 1.348 | 0.0935 | 0.378 | 0.7973 | 0.1746 | 0.6227 | 0.219 |
| T2 | 1.5 x slippage | 1.495 | 0.0716 | 0.419 | 0.7973 | 0.1069 | 0.6904 | 0.134 |
| T3 | base (D8) | 0.530 | 0.3003 | 0.146 | 0.4279 | 0.0908 | 0.3371 | 0.212 |
| T3 | D8 + 1 tick/side | 0.462 | 0.3239 | 0.127 | 0.4279 | 0.1338 | 0.2941 | 0.313 |
| T3 | 1.5 x slippage | 0.500 | 0.3108 | 0.138 | 0.4279 | 0.1101 | 0.3179 | 0.257 |
| T4 | base (D8) | 0.425 | 0.3353 | 0.117 | n/a | n/a | n/a | n/a |
| T4 | D8 + 1 tick/side | 0.466 | 0.3205 | 0.128 | n/a | n/a | n/a | n/a |
| T4 | 1.5 x slippage | 0.449 | 0.3269 | 0.123 | n/a | n/a | n/a | n/a |

### Per calendar year (base case)

| Year | T1 n | T1 Sharpe | T2 n | T2 Sharpe | T3 n | T3 Sharpe | T4 n | T4 Sharpe |
|---|---|---|---|---|---|---|---|---|
| 2010 |  |  |  |  | 44 | 2.80 |  |  |
| 2011 | 110 | 1.31 | 110 | 1.29 | 251 | 0.42 | 236 | 0.62 |
| 2012 | 255 | -0.16 | 255 | -0.90 | 247 | 1.14 | 255 | 0.02 |
| 2013 | 252 | 1.06 | 252 | -0.12 | 249 | 1.19 | 252 | 0.91 |
| 2014 | 254 | 1.01 | 254 | 0.99 | 243 | -0.61 | 254 | -0.94 |
| 2015 | 254 | 1.22 | 254 | 0.40 | 250 | -0.71 | 254 | -0.78 |
| 2016 | 255 | -1.38 | 255 | -0.83 | 251 | -1.04 | 255 | -1.04 |
| 2017 | 253 | 0.08 | 253 | 0.42 | 249 | 0.79 | 253 | 1.33 |
| 2018 | 254 | -1.17 | 254 | -0.20 | 248 | -0.40 | 254 | -0.00 |
| 2019 | 252 | 0.51 | 252 | 0.08 | 246 | -0.31 | 252 | 0.14 |
| 2020 | 254 | 1.85 | 254 | 1.56 | 251 | 1.34 | 254 | 1.08 |
| 2021 | 254 | -0.19 | 254 | 1.12 | 251 | 0.09 | 254 | 1.08 |
| 2022 | 258 | 2.24 | 258 | 1.90 | 250 | -0.37 | 258 | 1.09 |
| 2023 | 257 | -0.53 | 257 | -0.77 | 248 | 0.81 | 257 | -1.30 |
| 2024 | 43 | 3.22 | 43 | 1.89 | 41 | -3.11 | 43 | 2.53 |

### Per root, T1 (base case)

| Root (T1) | contribution (sum, base) | own t | fills | gross | costs (base) |
|---|---|---|---|---|---|
| ZT | 0.2736 | 2.69 | 252 | 0.2870 | 0.0134 |
| NQ | 0.2654 | 2.67 | 252 | 0.2678 | 0.0024 |
| ZF | 0.1569 | 1.58 | 256 | 0.1625 | 0.0057 |
| NG | 0.1511 | 1.39 | 456 | 0.1586 | 0.0075 |
| ZN | 0.1037 | 1.06 | 252 | 0.1091 | 0.0054 |
| UB | 0.0627 | 0.62 | 252 | 0.0658 | 0.0031 |
| ZL | 0.0627 | 0.75 | 225 | 0.0681 | 0.0054 |
| ZC | 0.0576 | 0.82 | 153 | 0.0624 | 0.0048 |
| CL | 0.0542 | 0.55 | 452 | 0.0627 | 0.0084 |
| 6E | 0.0446 | 0.46 | 252 | 0.0469 | 0.0024 |
| ZB | 0.0401 | 0.40 | 252 | 0.0447 | 0.0046 |
| TN | 0.0372 | 0.55 | 142 | 0.0392 | 0.0020 |
| LE | 0.0201 | 0.33 | 159 | 0.0247 | 0.0046 |
| GC | -0.0394 | -0.42 | 278 | -0.0338 | 0.0055 |
| HE | -0.0638 | -1.36 | 99 | -0.0623 | 0.0015 |
| ZS | -0.0797 | -0.95 | 237 | -0.0758 | 0.0039 |
| RTY | -0.0936 | -1.55 | 112 | -0.0925 | 0.0011 |

### Per root, T2 (base case)

| Root (T2) | contribution (sum, base) | own t | fills | gross | costs (base) |
|---|---|---|---|---|---|
| NG | 0.1506 | 1.73 | 456 | 0.1565 | 0.0059 |
| NQ | 0.1397 | 1.87 | 252 | 0.1425 | 0.0027 |
| UB | 0.1243 | 1.61 | 252 | 0.1274 | 0.0031 |
| ZB | 0.0900 | 1.18 | 252 | 0.0948 | 0.0048 |
| CL | 0.0735 | 0.87 | 452 | 0.0803 | 0.0068 |
| ZN | 0.0539 | 0.73 | 252 | 0.0600 | 0.0061 |
| 6E | 0.0414 | 0.52 | 252 | 0.0438 | 0.0024 |
| TN | 0.0403 | 0.78 | 142 | 0.0424 | 0.0021 |
| LE | 0.0365 | 0.76 | 159 | 0.0403 | 0.0037 |
| ZF | 0.0364 | 0.49 | 256 | 0.0424 | 0.0060 |
| ZT | 0.0284 | 0.37 | 252 | 0.0432 | 0.0149 |
| ZL | 0.0283 | 0.44 | 225 | 0.0330 | 0.0047 |
| ZC | 0.0251 | 0.48 | 153 | 0.0296 | 0.0045 |
| HE | -0.0294 | -0.83 | 99 | -0.0281 | 0.0013 |
| GC | -0.0315 | -0.41 | 278 | -0.0267 | 0.0048 |
| ZS | -0.0385 | -0.65 | 237 | -0.0351 | 0.0034 |
| RTY | -0.0501 | -1.03 | 112 | -0.0490 | 0.0011 |

### Per root, T3 (base case)

| Root (T3) | contribution (sum, base) | own t | fills | gross | costs (base) |
|---|---|---|---|---|---|
| NQ | 0.4317 | 0.87 | 308 | 0.5047 | 0.0730 |
| RTY | -0.0946 | -0.38 | 146 | -0.0768 | 0.0178 |

### Fills by kind

- T1: {"rebalance": {"fills": 2121, "abs_contracts_per_capital": 0.004784476300964327}, "roll_in": {"fills": 980, "abs_contracts_per_capital": 0.006832929382010042}, "roll_out": {"fills": 980, "abs_contracts_per_capital": 0.006832929382010042}}
- T2: {"rebalance": {"fills": 2121, "abs_contracts_per_capital": 0.008584819324259887}, "roll_in": {"fills": 980, "abs_contracts_per_capital": 0.004644594738277805}, "roll_out": {"fills": 980, "abs_contracts_per_capital": 0.004644594738277805}}
- T3: {"entry": {"fills": 227, "abs_contracts_per_capital": 0.04294261376031261}, "exit": {"fills": 227, "abs_contracts_per_capital": 0.04294261376031261}}
- T4: {}

### Exclusions and counters (all reasons, per test)

- T1: return undefined: previous mark missing 1343; rebalance moved: roll blackout 819; rebalance moved earlier 465; no signal (lookback: missing bar) 171; no signal (no reference (no trade date)) 143; UB: return undefined: previous mark missing 113; ZT: return undefined: previous mark missing 111; CL: return undefined: previous mark missing 110; rebalance moved: early halt 106; ZF: return undefined: previous mark missing 104; NQ: return undefined: previous mark missing 103; ZB: return undefined: previous mark missing 103; ZN: return undefined: previous mark missing 103; GC: return undefined: previous mark missing 99; NG: return undefined: previous mark missing 96; 6E: return undefined: previous mark missing 90; TN: return undefined: previous mark missing 71; no signal (no reference (outside window)) 60; RTY: return undefined: previous mark missing 50; LE: return undefined: previous mark missing 43; ZL: return undefined: previous mark missing 40; ZC: return undefined: previous mark missing 39; ZS: return undefined: previous mark missing 38; HE: return undefined: previous mark missing 30; rebalance moved: missing bar 27; series dates added (value booked on a non-series date) 22; flat month 2019-04 (store boundary or window end) 17; flat month 2024-02 (store boundary or window end) 17; return undefined: missing bar 17; hold excluded: contract change 12; ZC: return undefined: missing bar 7; rebalance moved: fill guard 6; closed at the first eligible date after month end 4; no eligible rebalance date 4; LE: return undefined: missing bar 3; ZS: return undefined: missing bar 3; HE: return undefined: missing bar 2; ZL: return undefined: missing bar 2; hold excluded: missing roll bar (fill guard) 1; rebalance moved: unsourced calendar date 1; forced close (backstop) 0
- T2: return undefined: previous mark missing 1343; rebalance moved: roll blackout 819; rebalance moved earlier 465; no signal (lookback: missing bar) 171; no signal (no reference (no trade date)) 117; UB: return undefined: previous mark missing 113; ZT: return undefined: previous mark missing 111; CL: return undefined: previous mark missing 110; rebalance moved: early halt 106; ZF: return undefined: previous mark missing 104; NQ: return undefined: previous mark missing 103; ZB: return undefined: previous mark missing 103; ZN: return undefined: previous mark missing 103; GC: return undefined: previous mark missing 99; NG: return undefined: previous mark missing 96; 6E: return undefined: previous mark missing 90; no signal (no reference (outside window)) 86; TN: return undefined: previous mark missing 71; RTY: return undefined: previous mark missing 50; LE: return undefined: previous mark missing 43; ZL: return undefined: previous mark missing 40; ZC: return undefined: previous mark missing 39; ZS: return undefined: previous mark missing 38; HE: return undefined: previous mark missing 30; rebalance moved: missing bar 27; series dates added (value booked on a non-series date) 22; flat month 2019-04 (store boundary or window end) 17; flat month 2024-02 (store boundary or window end) 17; return undefined: missing bar 17; hold excluded: contract change 12; ZC: return undefined: missing bar 7; rebalance moved: fill guard 6; closed at the first eligible date after month end 4; no eligible rebalance date 4; LE: return undefined: missing bar 3; ZS: return undefined: missing bar 3; HE: return undefined: missing bar 2; ZL: return undefined: missing bar 2; hold excluded: missing roll bar (fill guard) 1; rebalance moved: unsourced calendar date 1; forced close (backstop) 0
- T3: T3 units traded 227; return undefined: previous mark missing 153; NQ: return undefined: previous mark missing 103; RTY: return undefined: previous mark missing 50; T3 unit excluded: sigma warm-up 6; T3 unit excluded: exit: early halt 4; T3 unit excluded: entry: early halt 3; T3 unit excluded: store boundary 2; T3 unit excluded: window end 2; forced close (backstop) 0
- T4: grid dates 3391; series dates 3331; warmup 60

### Fill diagnostics (T1 notes)

```
{
 "fills": 4081,
 "fills in an event window": 14,
 "fills in an uncalibrated bucket (R-B2)": 74,
 "diag: fills the limit-lock test flags (not moved)": 14,
 "diag: 2010-2019 fill bars with high == low": 454,
 "diag: forced fills inside a guard window": 0
}
```

### 3.4 F8 descriptive economics (EconWorker-OpusHigh; reports/stage_e21_economics.md and .json)

- Personal account (capital at which every root holds at least one contract at full signal; E.13 C2 per-contract dollar risk; F8 micros where they exist, full-size flagged): T1 about $691K at 15% and $415K at 25% annual volatility (book volatility 16.6%); T2 $538K and $323K (12.9%); T3 (MNQ, M2K) $57K and $34K (17.5%). Live cattle (full-size LE) binds T1 and T2; at $100K, 4 to 7 of the 17 roots round to zero contracts.
- The integer book at its smallest integer size tracks the fractional book (correlation >= 0.995): daily / 5-day dollar sd T1 $6,540 / $14,520, T2 $5,099 / $10,958, T3 $535 / $1,190.
- No weekend holds (flat every Friday, two extra fills per root per weekend): T1's mean turns negative on costs alone (-$4.9K a year at that size), T2 about -$0.3K, T3 about +$0.4K.
- PropEd (automation UNCONFIRMED on every row): T1 and T2 breach the drawdown in 46-100% of rolling 21-day windows (One Plan 750K 24-57%), exceed the micro-contract caps on 57-99% of days, and hold roots PropEd does not list (M6E, micro yields, TN, UB, HE, LE). T3 fits the $7.5K-$10K-drawdown plans and Standard 150K (breach 0-1.4%), but T3 failed. Phidias Premium 50K ($2,500 EOD trailing, semi-automated only) matches PropEd's $2,500 plans.
- T4 has no contract book; its realized volatility is 120 risk units a year, 13.0 without the 8 days with |value| > 10 (the H5-scaling spikes, section 5 FR-4 and section 7 item 3).

#### T3 against each PropEd plan (from reports/stage_e21_economics.md)

### T3 (daily sd $535, 5-day sd $1,190, max micro-equivalent 32)

| plan | DD type | DD $ | DLL $ | max micros | share days over max | not listed | daily sd / DD | 5-day sd / DD | weekend add-on $ | breach with weekend (trailing / static) | breach no weekend (trailing / static) | 10% scale: m, with wknd tr/st, no wknd tr/st |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Standard Eval - 25k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 1,000 | UNSOURCED | 30 | 0.2% | - | 0.53 | 1.19 | 16.35 | 55.8% / 42.7% | 48.1% / 37.6% | none |
| Standard Eval - 50k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 2,000 | UNSOURCED | 50 | 0.0% | - | 0.27 | 0.60 | 26.25 | 31.3% / 24.8% | 27.2% / 22.8% | none |
| Standard Eval - 100k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 4,000 | UNSOURCED | 100 | 0.0% | - | 0.13 | 0.30 | 42.75 | 6.7% / 5.2% | 4.3% / 4.1% | none |
| Standard Eval - 150k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 6,000 | UNSOURCED | 150 | 0.0% | - | 0.09 | 0.20 | 54.75 | 1.4% / 1.4% | 0.2% / 0.2% | m=1: 1.4% / 1.4%; 0.2% / 0.2% |
| Instant Funding - 50k [automation UNCONFIRMED] | EOD ("(eod)"; trailing not stated) | 2,500 | UNSOURCED | 30 | 0.2% | - | 0.21 | 0.48 | 89.85 | 21.8% / 16.9% | 17.3% / 15.9% | none |
| Instant Funding - 100k [automation UNCONFIRMED] | EOD ("(eod)"; trailing not stated) | 5,000 | UNSOURCED | 60 | 0.0% | - | 0.11 | 0.24 | 142.35 | 2.7% / 2.1% | 1.5% / 1.5% | none |
| Instant Funding - 150k [automation UNCONFIRMED] | EOD ("(eod)"; trailing not stated) | 7,500 | UNSOURCED | 90 | 0.0% | - | 0.07 | 0.16 | 194.85 | 1.2% / 1.2% | 0.0% / 0.0% | m=1: 1.2% / 1.2%; 0.0% / 0.0% |
| TrueRisk Eval - 1.25k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 1,250 | UNSOURCED | 15 | 7.0% | - | 0.43 | 0.95 | UNSOURCED ("available ... | 48.7% / 35.5% | 40.6% / 33.5% | none |
| TrueRisk Eval - 2.5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 2,500 | UNSOURCED | 30 | 0.2% | - | 0.21 | 0.48 | UNSOURCED ("available ... | 21.8% / 16.9% | 17.3% / 15.9% | none |
| TrueRisk Eval - 5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 5,000 | UNSOURCED | 60 | 0.0% | - | 0.11 | 0.24 | UNSOURCED ("available ... | 2.7% / 2.1% | 1.5% / 1.5% | none |
| TrueRisk Eval - 10k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 10,000 | UNSOURCED | 120 | 0.0% | - | 0.05 | 0.12 | UNSOURCED ("available ... | 0.6% / 0.6% | 0.0% / 0.0% | m=1: 0.6% / 0.6%; 0.0% / 0.0% |
| TrueRisk - Instant Funded - 2.5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 2,500 | UNSOURCED | 30 | 0.2% | - | 0.21 | 0.48 | 89.85 | 21.8% / 16.9% | 17.3% / 15.9% | none |
| TrueRisk - Instant Funded - 5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 5,000 | UNSOURCED | 60 | 0.0% | - | 0.11 | 0.24 | 89.85 | 2.7% / 2.1% | 1.5% / 1.5% | none |
| TrueRisk - Instant Funded - 7.5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 7,500 | UNSOURCED | 90 | 0.0% | - | 0.07 | 0.16 | 194.85 | 1.2% / 1.2% | 0.0% / 0.0% | m=1: 1.2% / 1.2%; 0.0% / 0.0% |
| TrueRisk - Instant Funded - 10k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 10,000 | UNSOURCED | 90 | 0.0% | - | 0.05 | 0.12 | 194.85 | 0.6% / 0.6% | 0.0% / 0.0% | m=1: 0.6% / 0.6%; 0.0% / 0.0% |
| One Plan - 750k [automation UNCONFIRMED] | trailing EOD, locks at starting balance on... | 37,500 | 11250 | 750 | 0.0% | - | 0.01 | 0.03 | UNSOURCED | 0.0% / 0.0% | 0.0% / 0.0% | m=6: 20.6% / 20.6%; 16.7% / 16.7% |
| Nexus X5 Evaluation - 50k [automation UNCONFIRMED] | trailing EOD (Q87) | 2,500 | UNSOURCED | 50 | 0.0% | - | 0.21 | 0.48 | UNSOURCED | 21.8% / 16.9% | 17.3% / 15.9% | none |
| Phidias Premium 50K (comparison) [semi-automated only] | EOD trailing; on CASH stops trailing at $5... | 2,500 | none | 100 | 0.0% | UNSOURCED (Phidias instrument list not collected) | 0.21 | 0.48 | not needed / none listed | 21.8% / 16.9% | 17.3% / 15.9% | none |

Overnight: Standard, Instant and TrueRisk plans 'yes' (FAQ Q21, terms Q02); One Plan and Nexus X5: general FAQ statement only, plan not named (FLAG). Weekend holds: add-on for Standard/Instant/TrueRisk (TrueRisk Eval price UNSOURCED, 'available at checkout'); One Plan and Nexus X5 weekend terms UNSOURCED; Phidias allows weekends (JSON weekend_allowed true).

## 4. Delegation record

| Spawn (CLI name) | Agent file | Model | Effort | Start-end (PDT) | Objective | Output | Result |
|---|---|---|---|---|---|---|---|
| SpecReaderTrend-OpusHigh | worker-high (workflow wf_18fed4b8-d89) | opus | high | 03:13-03:19 | T1/T2 and F3 vs MOP 2012, HOP 2017 | reports/stage_e21_briefs/spec_trend.md | done; T2 scaling mismatch, chained-return claim rejected |
| SpecReaderTOM-OpusHigh | worker-high (same workflow) | opus | high | 03:13-03:33 | T3 vs Lakonishok-Smidt, McConnell-Xu; post-2008 | spec_tom.md | done; parenthetical mismatch |
| SpecReaderPost2010-OpusHigh | worker-high (same workflow) | opus | high | 03:13-03:25 | post-2010 trend and TOM-futures evidence | spec_post2010.md | done; AQR 0.389, SG 0.352 |
| PropEdReader-OpusHigh | worker-high (same workflow) | opus | high | 03:13-03:26 | PropEd plans and rules | reports/stage_e21_proped_rules.md/.json | done; automation unresolved |
| MultidayCoder-OpusXHigh | worker-xhigh | opus | xhigh | 03:18-04:11 (build 03:18-03:46; 4 SendMessage rounds) | multiday/ to the lead spec, tests, calendar counts | multiday/, tests/test_multiday_*.py, multiday_build.md | done; 62 tests |
| FreezeReviewer-FableXHigh | worker-xhigh | fable | xhigh | 03:51-04:02; recheck 04:07-04:10 | adversarial freeze review | reports/stage_e21_review_freeze.md | APPROVE WITH FIXES; recheck APPROVE |
| EconWorker-OpusHigh | worker-high | opus | high | 04:15-04:20 | F8 economics | reports/stage_e21_economics.md/.json, briefs/econ/economics.py | done |
| VerdictVerifier-FableXHigh | worker-xhigh | fable | xhigh | 04:15-04:35 | independent recomputation of every verdict number | reports/stage_e21_review_verdict.md | VERIFIED WITH NOTES |

Tokens per spawn are in section 8 (transcripts). Reserved to the lead and not delegated: the decomposition, the lead spec and prereg, every ruling (A1-A12, Q1-Q4, FR-1..FR-9, VV-1..VV-5), the registration, the evaluation command, the verdicts and this synthesis.

## 5. Verification (each Fable finding, the ruling and the fix)

### 5.1 FreezeReviewer-FableXHigh (reports/stage_e21_review_freeze.md)

The review ran before registration, 03:51-04:02 PDT, and returned APPROVE WITH FIXES (0 BLOCKING,
2 SHOULD FIX, 6 NOTE). The recheck, 04:07-04:10, returned APPROVE with one further NOTE (FR-9). The
rulings are in lead_spec section B.

| Id | Severity | Finding | Ruling and fix |
|---|---|---|---|
| FR-1 | SHOULD FIX | The forced close at an era's last mark was untested. It was the only path keeping the "book ends with a position" invariant from raising after the marker. | Fixed. Tests were added at both era ends (2019-04, 2024-02). The end-of-book check became a non-fatal, counted backstop forced close. The run counted 0 backstops. |
| FR-2 | SHOULD FIX | The "missing roll bar" and "missing roll bar (fill guard)" hold exclusions were untested. | Fixed: two synthetic tests. The run counted 1 "missing roll bar (fill guard)" in T1. |
| FR-3 | NOTE | Bar existence at later dates steers rebalance dates and T3 eligibility. This is a data-presence effect, not a price effect. | Declared in the prereg. Reported separately from calendar reasons. |
| FR-4 | NOTE | T4's trailing-sd scaling runs over mostly-zero H2 and early-T2 values, which inflates x/sigma on those dates. | No change, because the prompt prescribes H5's method. After the run, this effect dominates T4's series (section 7, item 3; open choice 28). |
| FR-5 | NOTE | Capital units versus risk units, and "scaled to the hold", do not change the verdict. | Declared in the prereg. |
| FR-6 | NOTE | Sigma skips returns across a missing previous mark. | Counted in the exclusions: 1,343 across the 17 roots. |
| FR-7 | NOTE | multiday/README.md and screening/trial_registry.py were not pinned. | Both added to the freeze. |
| FR-8 | NOTE | The pre-marker order and the O_EXCL marker were confirmed. | None. |
| FR-9 | NOTE (recheck) | A backstop close on a mark dated 2019-05-01..05-05, whose era is None, would raise KeyError after the marker. | Hardened before the freeze: the marks on each side of an era change are precomputed. Test added. |

### 5.2 VerdictVerifier-FableXHigh (reports/stage_e21_review_verdict.md)

The verifier worked 04:15-04:35 PDT and returned VERIFIED WITH NOTES (0 BLOCKING, 0 SHOULD FIX,
5 NOTE).
- **Its own code first:** it built its own series from the real stores with its own code, before
  opening the run's statistics.
- **Statistics:** all 152 verdict numbers matched within 1e-9 (n, mean, sd, t, t_NW, p_t, p_NW, p,
  Sharpe, bootstrap CI, Holm, Sharpe bar and PASS, for every cost case).
- **Series and units:** all 12 daily series (4 tests x 3 cost cases) matched date by date with zero
  difference. All 17 roots matched in T1 and T2 on net, fills, gross and costs, and T3's 227 units
  matched.
- **Order of events:** confirmed, as were N = 532, the freeze and the H2 pin.

| Id | Severity | Finding | Ruling |
|---|---|---|---|
| VV-1 | NOTE | The 171 "no signal (lookback: missing bar)" root-months, concentrated in ZC, ZL, ZS, LE and HE, come from the stores' roll metadata. It records two roll instants on consecutive weekend days (Saturday, then Sunday's session open) with no bar between them. At the second instant, base_rules.h2.chained_return finds i_out < start_i and returns "missing bar". The verifier reproduces all 171, the 17 undefined returns and the 13 hold exclusions. Positions are identical; there is no look-ahead. | Accepted as classification (a): the frozen rule applied as specified to a real store feature. It thins those five roots for about 1-5 years each and does not bias the verdicts. Any future test chaining across these stores should treat consecutive recorded rolls with no bar between them as one splice, defined before data. |
| VV-2 | NOTE | The wording of multiday/README.md coder choice 5 can be misread as cascading backwards. The code zeroes only the order in force at the failed interval, which is the verified reading. The verifier's first pass misread it, and both passes are kept. | No change to the frozen README; noted here. |
| VV-3 | NOTE | Fills by kind: the run labels every non-roll fill "rebalance". The verifier's entry/flip/exit split sums to the same 2,121. | Reporting only. |
| VV-4 | NOTE | The two T3 "window end" units (February 2024) are counted by the run and skipped silently by the verifier. Traded units agree. | Reporting only. |
| VV-5 | NOTE | The two counts label pre-window months differently. No position is affected. | Reporting only. |

Not checked by the verifier: the F8 economics, the DSR block, the limit-lock and high == low
diagnostics, and the stress and 1.5 x per-root rows. F8 is descriptive. EconWorker-OpusHigh
reconstructed each test's base series from the per-root files (maximum absolute error 2e-17), which
cross-checks the per-root files the economics uses.

## 6. Open choices (every decision the lead made on its own, with the reason)

Rulings are in reports/stage_e21_briefs/lead_spec.md ([LEAD] items, section A, section B) and
multiday/README.md (Coder choices, Lead rulings, Freeze review fixes). All were made before any bar
was read (the marker is dated 04:12:28 PDT).

1. **MultidayCoder started in parallel with Step 1**, not after it as the delegation table says (03:18
   vs the readers' 03:33 return). Reason: the five-hour window, and the build reads no data. Reader
   amendments were to go by SendMessage; none changed the code-level spec (A1-A11). A12 came later,
   from the calendar counts.
2. **LE's 2010-06-07..2014-12-14 span (R-S3) is excluded for every test.** LE's first mark is on or
   after 2014-12-15. Reason: the prompt's F1 exclusion, applied to marks, references and S_M alike.
3. **Volatility warm-up: 60 defined daily returns (A3).** MOP gives no rule. T3 needs a defined sigma
   without a 12-month lookback. For T1 and T2 the 12-month lookback binds first.
4. **Daily returns for sigma are undefined across store eras and across a missing previous mark**
   (skipped by the EWMA, counted; FR-6). Reason: same-contract, one-day returns only. This gives no
   look-ahead.
5. **Lookbacks across the 2019-04-30/2019-05-06 store boundary.** They are split as at a splice only
   when the two contracts differ; with the same contract the chain runs through. Reason: never chain
   across two contracts, and never lose a year of signals to the boundary.
6. **The store boundary is a flat month for T1/T2.** The April 2019 rebalance closes everything and the
   May 2019 rebalance reopens. T3's April/May 2019 unit is excluded. Reason: lead_spec section 2 says a
   multi-day hold spanning the boundary is excluded.
7. **Rebalance date.** It is the latest eligible date among the month's last six trade dates. If none
   exists, the position is closed at the first eligible date after month end. Reference dates follow
   the same six-date rule, and roll-blackout dates are allowed for references. Reason: month-end
   semantics under roll blackouts, with calendar-known eligibility.
8. **S_M is calendar-defined:** the roots whose month M-12 lies in the window. A root whose signal or
   sigma is undefined still counts and holds zero. After Q1, the window is the latest of the
   windows-file date, R-S4 and R-S3. Reason: roots rebalance on different dates, so an S_M built from
   realized signals would use other roots' later information.
9. **Holdings are fixed contracts between fills:** n = w / (S_M x V). Reason: this reproduces MOP's
   monthly return exactly between rolls (A5), as a real monthly-rebalanced book would.
10. **The February 2024 rebalance closes every position.** Reason: the next month lies outside the
    window.
11. **T3 sizing.** "Scaled to the hold" is read as a constant 0.40/sigma weight over the hold. S_u
    counts eligible units, and eligibility includes a defined sigma (Q2). Reason: the prompt's
    wording, with verdict invariance shown in FR-5. Both roots enter at the same settlement, so this
    is not look-ahead.
12. **Fill guard.** Rebalance, entry and exit dates must have a fill point outside D9.5a guard
    windows (calendar data). Roll legs move to the nearest usable bar outside them. Reason: release
    times are known in advance.
13. **Limit locks are a counted diagnostic only.** Reason: moving or excluding on the fill bar's own
    high and low would use that bar's prices.
14. **Series dates are calendar-defined, with zeros on flat days.** Reason: no data-dependent series
    length.
15. **The bootstrap uses a fresh default_rng(20261014) per test and circular blocks of 21.** Reason:
    test order cannot change any interval.
16. **HOP's 10% portfolio scaling is not adopted for T2 (A6, a declared deviation).** Reasons: the
    prompt's T2 formula is binding first; the 36-month covariance warm-up costs about two years and
    four roots; a book-level scaler at per-root rebalance dates would need other roots' unknown
    same-month signals.
17. **The T3 parenthetical is corrected (A8):** day -2 is the second-to-last trade date. Reason: the
    papers' four-day window.
18. **T3 days are numbered on NYSE trading days (A12)**, by rule-based NYSE closures plus three
    special closures. Reason: the equity futures calendar books US holidays as early-halt trade dates,
    while the papers count NYSE days. This was found in the calendar-only counts, before any bar.
19. **The trend reader's chained_return "MISMATCH risk" is rejected (A1).** Reason: the function
    splits at every recorded splice (h2.py lines 65-72).
20. **A non-positive price makes a return, lookback or notional undefined, counted (Q3).** Reason:
    CL's April 2020 prices. Fixed-contract P&L is unaffected.
21. **Forced close at an era's last mark (Q4).** The end-of-book check is a counted, non-fatal
    backstop (FR-1), and backstop fill dates are precomputed (FR-9). Reason: no unforeseen data
    condition may STOP the single attempt after its marker (R-B3).
22. **A failed hold (a contract change with no splice, or a missing roll bar) zeroes the order that
    opened it, counted.** Reason: base_rules' unit-exclusion convention. This is a data-presence
    effect, reported (FR-3).
23. **PropEd's F8 table covers every plan allowing overnight holds, each flagged "automation
    UNCONFIRMED" (A11).** Reason: no public page grants automation, and the FAQ marks it not allowed.
24. **F8 method (brief_economics.md):** K_min is the smallest capital at which every root's
    full-signal position is at least one contract, from E.13's C2 per-contract dollar risk. The
    "smallest integer size" is the scale at which the binding root holds one contract. Breaches are
    measured over rolling 21-trade-day EOD windows. In the no-weekend variant, P&L after weekend gaps
    is zeroed and two extra fills are charged per weekend. Reason: the prompt fixes the outputs but
    not the method.
25. **Evidence pages committed:** text, HTML and markdown pages and the fetch logs. Left out: every
    DO_NOT_COMMIT entry (all PropEd pages, whose terms forbid scraping without permission; 10 TOM
    pages) and third-party PDFs and images, whose .txt extractions stay. Reason: site terms and
    copyright; E.13 and E.20 also committed selectively.
26. **The E.21 checks script is E.20's** with this session's scratchpad and an E.21 freeze check
    added.
27. **Commits carry the Co-Authored-By and Claude-Session lines.** Reason: this repository's
    precedent (E.20's commits).
28. **T4 kept H5's trailing-60-grid-date scaling (FR-4, no change at the freeze).** Reason: the prompt
    says "as H5 combines". Consequence, seen after the run (F8): T4's series is dominated by three days
    where H2's first hold dates meet a near-zero trailing sd. T4 is therefore not an informative test
    of the combined book (section 7, item 3).
29. **The verifier was told of the lookback "missing bar" concentration after its own computation**
    (ZC, ZL, ZS, LE, HE runs of about 12 months). Reason: a post-run diagnostic. It changes no rule
    or number; finding in section 5.

## 7. Decisions for the user (the lead's recommendation first)

1. **Trend (T1, T2): FAIL with a positive point estimate. This is underpowered, not refuted. Close
   the test route on owned data.**
   - **The numbers:** T1 nets a Sharpe of 0.50 (95% CI [-0.06, 1.05]) and T2 0.44 ([-0.11, 0.98]).
     Both are above the 0.3 bar and in line with the published post-2010 records (AQR TSMOM 0.39
     gross; SG Trend 0.35 net on the same window).
   - **What more data would need:** passing Holm's first step (z 2.50) at the observed 0.50 needs
     about 25 years of data; at the published 0.39 it needs about 41 years. A single test at 0.025
     needs about 15 years at 0.50. The owned post-2010 history is 12.6 years.
   - **No new data source changes this.** Databento's GLBX.MDP3 has nothing before 2010. Pre-2010
     data lies inside MOP and HOP's own samples, so it is not independent. The research window adds
     about 1.2 years, and forward time adds one year a year.
   - **A longer hold is no remedy:** T1 is already a monthly book, and any new hold or lookback would
     be a variant on data whose per-root results are now known.
   - **Recommendation:** run no further trend variant on 2010-2024 (N stays 532). Record T1/T2 as
     "consistent with the published evidence, not established by this program's bar".
   - **If you later want trend exposure in a personal account,** that is a decision on the published
     1880-2016 evidence plus this estimate, not a pass under V33. Holding every root at one contract
     or more at full signal needs about $415K-$691K (T1) or $323K-$538K (T2); live cattle binds
     (F8). At $100K, 4 to 7 of the 17 roots round to zero.
   - **A forward paper record** of the micro-available book, registered before any of its data
     exists, is the only route to new independent evidence. It accrues about one year of power per
     year.
2. **Turn of the month (T3): close.** Its Sharpe is 0.15, below the bar, with an interval of [-0.40,
   0.71] and costs at 21% of gross. That matches the decay the post-2008 literature reports, and no
   futures study after 2010 supports it. Recommendation: no variant.
3. **The combined book (T4) and H5's combination method: close, and fix the method before any future
   combination.**
   - T4 nets 0.12. Its statistic is dominated by three days where H2's first hold dates meet a
     trailing 60-date standard deviation of near-zeros (FR-4; F8: -299.9 on 2016-06-27, +244.8,
     +190.5). The prompt prescribed H5's method, and the freeze review flagged it as a NOTE.
   - Recommendation: any future combination of sparse components scales each one by its volatility
     on active days, or over a longer window, fixed before data. H2 itself gets no further work.
4. **PropEd Capital: no purchase.**
   - **Automation is not granted publicly for any plan.** Terms section 8 says "only where supported
     and permitted", and the FAQ marks bots not allowed. This weakens V38's premise.
   - **The T1/T2 books cannot be held there.** PropEd lists no M6E, micro yields, TN, UB, HE or LE.
     Rolling 21-day windows breach the drawdown in 46-100% of cases (One Plan 750K: 24-57%), and the
     books exceed the micro caps on 57-99% of days.
   - **T3 fits** the $7.5K-$10K-drawdown plans and Standard 150K, but T3 failed.
   - Recommendation: send the ten drafted questions (reports/stage_e21_proped_rules.md) only if a
     future strategy passes. Phidias Premium 50K ($2,500 EOD trailing, semi-automated) shows the same
     breach profile as PropEd's $2,500 plans.
5. **Program direction.** The intraday program closed in V38. Multi-day trend on owned data is
   underpowered at any feasible bar, and no venue can hold the trend book.
   - Recommendation: pause the futures program until the AiTrader readout (2026-10-23).
   - Then choose between (a) stopping the futures route, and (b) a registered forward paper record
     of a micro-available trend book. Route (b) needs no purchase now; it needs a daily data source
     and a small runner.
   - Weekend holds matter for any prop route: flattening every Friday pushes T1's mean below zero on
     costs alone (F8).

## 8. Session cost

### Final ETA table (actuals; PDT; the initial estimate in brackets)

| Task | Owner | Model | Effort | Mode | Start | End | Time (min) | Tokens | Status and deviations | [Initial estimate] |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 Startup checks | lead | opus | xhigh | first | 03:04 | 03:10 | 6 | in lead | done; all pass | [03:04-03:10] |
| 0b Start pytest (detached) | lead (shell) | - | - | parallel | 03:10 | 03:31 | 21 | - | 7340 passed, 3 skipped, 3 xfailed | [~22 min, ~03:32] |
| 1 SpecReaderTrend | SpecReaderTrend-OpusHigh | opus | high | 4 at once | 03:13 | 03:19 | 6 | 4,250,676 | done | [<=50 min, ~04:05] |
| 1 SpecReaderTOM | SpecReaderTOM-OpusHigh | opus | high | 4 at once | 03:13 | 03:33 | 20 | 14,848,480 | done | [<=50 min, ~04:05] |
| 1 SpecReaderPost2010 | SpecReaderPost2010-OpusHigh | opus | high | 4 at once | 03:13 | 03:25 | 12 | 11,239,686 | done | [<=50 min, ~04:05] |
| 1 PropEdReader | PropEdReader-OpusHigh | opus | high | 4 at once | 03:13 | 03:26 | 13 | 7,206,887 | done; automation unresolved | [<=50 min, ~04:05] |
| 2a Lead spec, prereg draft | lead | opus | xhigh | parallel with 1 | 03:13 | 03:20 | 7 | in lead | done | [~7 min] |
| 2b MultidayCoder (build, then fixes Q1/Q2/A12, FR-1/2/6/7, FR-9 via SendMessage) | MultidayCoder-OpusXHigh | opus | xhigh | parallel with 1 (deviation: the plan said after 1) | 03:18 | 04:11 | 53 | 30,512,915 | done: 62 tests, ruff clean | [~80 min, ~04:45] |
| 2c Literature and calendar rulings A1-A12, Q1-Q4 | lead | opus | xhigh | serial | 03:33 | 03:49 | 16 | in lead | done | [~10 min, ~04:15] |
| 3b FreezeReviewer (review and recheck) | FreezeReviewer-FableXHigh | fable | xhigh | serial | 03:51 | 04:10 | 19 | 2,544,519 | APPROVE WITH FIXES (0 BLOCKING, 2 SHOULD FIX, 6 NOTE); recheck APPROVE (+FR-9 NOTE) | [~25 min, ~05:25] |
| 3g Freeze manifest, commit 839efc9 | lead | opus | xhigh | serial | 04:11 | 04:12 | 1 | in lead | done | [~20 min with fixes, ~05:45] |
| 4a Register r006-E21 (N 528 -> 532) | lead | opus | xhigh | serial | 04:12 | 04:12 | 0 | in lead | done 04:12:12 | [in 3c] |
| 4b Evaluate once (detached) | lead (shell) | - | - | serial | 04:12 | 04:14 | 2 | - | rc 0; 2:11 wall; 1.47 GB peak; all FAIL | [~20 min, ~06:05] |
| 4c F8 economics | EconWorker-OpusHigh | opus | high | parallel with 5 | 04:15 | 04:20 | 5 | 2,619,435 | done | [~25 min, ~06:30] |
| 5 Verdict verification | VerdictVerifier-FableXHigh | fable | xhigh | parallel with 4c | 04:15 | 04:35 | 20 | 7,780,026 | VERIFIED WITH NOTES (152 numbers MATCH) | [~30 min, ~06:35] |
| 6a End pytest (detached) | lead (shell) | - | - | parallel | 04:15 | 04:35 | 20 | - | 7402 passed, 3 skipped, 3 xfailed | [~22 min] |
| 6b End checks | lead | opus | xhigh | serial | 04:35 | 04:36 | 1 | in lead | all pass | [-] |
| 6c Return, progress, STAGES, cost, commit | lead | opus | xhigh | last | 04:36 | 04:40 | 4 | in lead | done | [~35 min, ~07:10] |
| **Stage total** | lead + 8 workers | | | | 03:04 | 04:40 | 96 | 133,371,734 (lead 52,369,110; workers 81,002,624) | no pauses; no outage | [cumulative ETA ~07:10] |

### Tokens per model (transcripts; reports/stage_e21_briefs/make_cost.py over the lead's .jsonl and every subagent transcript, each message's final usage)

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,528 | 130,716 | 9,708,950 | 483,351 | 10,324,545 |
| claude-opus-5-5 | 1,174 | 727,411 | 120,180,685 | 2,137,919 | 123,047,189 |
| all | 2,702 | 858,127 | 129,889,635 | 2,621,270 | 133,371,734 |

Delegation share: lead 52,369,110 (39.3%), workers 81,002,624 (60.7%). By model: claude-fable-5-1 7.7%, claude-opus-5-5 92.3%

| Spawn (name) | Model | Effort | First | Last | Tokens |
|---|---|---|---|---|---|
| lead (Opus 5.5) | claude-opus-5-5 | xhigh | 03:04 PDT | 2026-10-14T11:40:18 | 52,369,110 |
| FreezeReviewer-FableXHigh | claude-fable-5-1 | xhigh | 03:51 PDT | 2026-10-14T11:10:03 | 2,544,519 |
| VerdictVerifier-FableXHigh | claude-fable-5-1 | xhigh | 04:15 PDT | 2026-10-14T11:35:40 | 7,780,026 |
| EconWorker-OpusHigh | claude-opus-5-5 | high | 04:15 PDT | 2026-10-14T11:20:35 | 2,619,435 |
| MultidayCoder-OpusXHigh | claude-opus-5-5 | xhigh | 03:18 PDT | 2026-10-14T11:11:00 | 30,512,915 |
| SpecReaderTrend-OpusHigh | claude-opus-5-5 | high | 03:13 PDT | 2026-10-14T10:19:18 | 4,250,676 |
| SpecReaderTOM-OpusHigh | claude-opus-5-5 | high | 03:13 PDT | 2026-10-14T10:33:18 | 14,848,480 |
| SpecReaderPost2010-OpusHigh | claude-opus-5-5 | high | 03:13 PDT | 2026-10-14T10:25:21 | 11,239,686 |
| PropEdReader-OpusHigh | claude-opus-5-5 | high | 03:13 PDT | 2026-10-14T10:26:13 | 7,206,887 |
