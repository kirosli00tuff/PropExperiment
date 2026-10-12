# Stage E.20 return: pattern search with per-product research (Part A, H6, ML search)

Lead Opus 5.5 xhigh, ultracode on; session 2b0cd60b-1622-462e-8c67-e6ae076a3acb; 2026-10-11 10:21-20:25 PDT. All times PDT.

## 1. Verdict summary

**H6 (rest-of-day to last-half-hour momentum on NQ at MNQ cost, 2020-06-01..2024-02-29): FAIL on all three tests.**
- T1 (every eligible date): FAIL. 893 trades; mean gross 1.25 ticks (0.38 bp), net -2.83 ticks (-0.39 bp) against a
  4.08-tick round trip; t_B -0.53, one-sided p 0.70; net Sharpe -0.27.
- T2 (|r_ROD| above its 60-date median): FAIL. 446 trades; gross -3.27 ticks (-0.35 bp), net -7.35 (-1.11 bp); t_B
  -0.95, p 0.83; Sharpe -0.48.
- T3 (previous day's GEX negative; ran, the source cleared under its terms): FAIL. 134 trades; gross -3.52 ticks
  (-0.52 bp), net -7.60 (-1.33 bp); t_B -0.38, p 0.65; Sharpe -0.19.
- No Holm rejection (m = 3, 0.025). Fable reproduced every number independently.

**Search screen: FAIL.** Median-path daily t -1.33 (bar 2.0), PBO 0.60 (bar < 0.5), annualized net Sharpe at 50K -0.83
(bar 0.5); DSR at N = 528 about 0. All 45 configurations were negative out of sample (best -0.33). The final
configuration would have been ridge, lambda 0.1, k 2, h60. A failed screen ends Part C: no freeze, no backward read,
E20-B1 not run.

**N: 480 -> 483 (H6) -> 528 (45 configurations).**

**Features:** 33 of the 67-signal library dropped by F6 (legs outside the 17 roots, or calendars absent in 2010-2019,
including k2_fomc_mto after the plan review); 34 kept; 2 added (rod_ret, rod_absratio); 0 Part A features accepted (7
proposed, none with a published post-2015 size above 1.5 x the D8 round trip for the hold it would serve).

**What it means.** The one published intraday effect whose historical size cleared the cost wall, Baltussen et al.'s
rest-of-day momentum, is absent on NQ after the paper's sample at retail cost: gross 1.25 ticks against 4.08, and the
gamma and magnitude subsets are negative. The ML route's net pipeline, run on 17 roots with late-session features,
found nothing either; the r_ROD features reduced its losses but did not make it profitable. Across 528 registered
trials nothing has passed, and E.19 showed the Topstep funnel loses money without an edge. Both lines tested here are
closed (section 7).

## 2. Guardrail evidence

### Start checks (10:24)

```
$ date
Sun Oct 11 10:24:11 PDT 2026
$ git status --short
[642 untracked paths (?? lines) omitted here; full list in reports/stage_e20_briefs/start_checks.txt]
$ git log --oneline -3
abfdeb8 chore: parallel-reader refinements (shared sources, per-domain spacing); E.20 updated
c9ae83d chore: maximum-parallelism standing rule (V37); settings cap 20
7366b56 E.20: run the 17 product readers at once; settings cap 17 (V36)
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
N = 480 (4 lines)
r001-C1: C1 ['C1-T1', 'C1-T2'] N 471 -> 473 at 2026-10-09T19:29:06-07:00
r002-E16: E16 ['E16-H1', 'E16-H2', 'E16-H3', 'E16-H4', 'E16-H5'] N 473 -> 478 at 2026-10-10T00:30:15-07:00
r003-C1b: C1b ['C1b-T1', 'C1b-T2'] N 478 -> 480 at 2026-10-10T12:17:48-07:00
$ wc -l ledger/trial_registrations.jsonl; sha256sum
4
55b1d24c65d484186c4494294fdae03e374141eba5c3f210800d77e56e95289d
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
```

Start suite: `7138 passed, 3 skipped, 3 xfailed, 54 warnings in 1319.55s (0:21:59)` (rc 0)

### End checks (20:12)

```
$ date
Sun Oct 11 20:12:16 PDT 2026
$ git status --short
[970 untracked paths (?? lines) omitted here; full list in reports/stage_e20_briefs/end_checks.txt]
 M ledger/trial_registrations.jsonl
 M reports/stage_e20_STATE.md
 M reports/stage_e20_briefs/brief_search_code.md
 M reports/stage_e20_briefs/checks.sh
 M reports/stage_e20_briefs/partA_returns.log
 M reports/stage_e20_briefs/rulings_partA.md
 M reports/stage_e20_product_summary.md
 M reports/stage_e20_rulings.md
$ git log --oneline -3
498fd05 E.20 H6 freeze
abfdeb8 chore: parallel-reader refinements (shared sources, per-domain spacing); E.20 updated
c9ae83d chore: maximum-parallelism standing rule (V37); settings cap 20
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
```

End suite: `7340 passed, 3 skipped, 3 xfailed, 54 warnings in 1108.23s (0:18:28)` (rc 0)

### Order of events (2026-10-11, PDT; from date, file mtimes, git, the registry and the logs)

| Time | Event | Source |
|---|---|---|
| 10:21-10:24 | Start checks (all pass; N 480; holdout 0 unlocks) | reports/stage_e20_briefs/start_checks.txt |
| 10:24-10:46 | Start test suite: 7138 passed, 3 skipped, 3 xfailed | pytest_start.out |
| 10:33-10:58 | Part A: 17 product readers at once | partA_returns.log, product_<ROOT>.json mtimes |
| 10:58-11:01 | Part A consolidation; GEX source cleared (T3 registered) | reports/stage_e20_product_summary.md |
| 10:56:48 | GEX sign count (148 rows < 0) after T3's status was fixed | transcript; prereg section 6 |
| 10:40-11:10 | h6_rod built (synthetic only) | h6_build.md |
| 11:12-11:21 | H6Reviewer (1st) stopped on the usage limit, no output | transcript mtime |
| 11:21-15:10 | PAUSE: usage limit | - |
| 15:12-15:30 | H6 review (APPROVE WITH FIXES) | reports/stage_e20_review_h6.md |
| 15:33:45 | H6 prereg last written | mtime (verifier) |
| 15:35:17 | H6 freeze manifest written (22e606f0...) | reports/stage_e20_h6_freeze.json |
| 15:35:53 | Commit 498fd05 "E.20 H6 freeze" | git |
| 15:36:20 | Registration r004-E20H6 (N 480 -> 483) | ledger/trial_registrations.jsonl |
| 15:36:38 | H6 run-once marker | reports/stage_e20_H6_RUN_ONCE.json |
| 15:38:15 | H6 result written (T1, T2, T3 FAIL) | reports/stage_e20_H6_result.json |
| 15:39-15:55 | H6 verification (VERIFIED WITH NOTES) | reports/stage_e20_review.md |
| 15:56-16:18 | Search plan review (BLOCK on PR-1) | reports/stage_e20_review_plan.md |
| 16:19-16:40 | 2010-2019 swap table (PR-1) | backward_swap_table.md |
| 16:21-17:13 | pattern_search built; Step 6 dry check passed | search_build.md, stage_e20_dry_check_step6.md |
| 16:42-16:47 | Plan recheck (BLOCK lifted) | review_plan.md "Recheck" |
| 17:12-17:29 | Search code review (APPROVE WITH FIXES) | reports/stage_e20_review_search_code.md |
| 17:35:42 | First search freeze manifest (66436234...); check --world refused (grid assertion); manifest deleted unregistered | search_check_world.log; rulings section 7 |
| 17:42-17:43 | Search freeze manifest 94ee86b0...; check --world passed | world_check.json |
| 17:43:59 | Registration r005-E20S (E20S-01..45; N 483 -> 528) | ledger/trial_registrations.jsonl |
| 17:44:15-17:52:20 | Search run: panel, nested CPCV, final selection, screen FAIL | search_run.log; reports/stage_e20_search.json |
| 17:53-18:12 | End test suite: 7340 passed, 3 skipped, 3 xfailed | pytest_end.out |
| 17:53-17:54 | ScreenVerifier (1st) stopped on the usage limit, no output | transcript |
| 17:54-20:10 | PAUSE: usage limit | - |
| 20:12 | ScreenVerifier re-spawned; end checks (all pass; N 528) | end_checks.txt |

No 2010-2019 bar was decoded (E20-B1 never registered); no NQ bar was read before 15:36:38; Gate 0's NQ rows were not
read; nothing dated 2024-03-01 or later was read (GEX rows after 2024-02-29 cut at load).

## 3. Results per part

### Part A: 17 product readers (consolidation: reports/stage_e20_product_summary.md)

17 ProductReader-<ROOT>-OpusHigh ran at once (10:33-10:58 PDT), from one shared brief with one assigned reader per
cross-root source. 157 evidence rows. Only H6's equity figure clears 1.5 x a root's D8 round trip on its own window
(Baltussen et al. equity portfolio about 2.7 bp per trade, 2.64 x the MNQ wall at search-window prices). Feature
availability: 35 of the 67-signal library passed F6 at consolidation, then 34 after the plan review (k2_fomc_mto
dropped, PR-2); 33 dropped with reasons (product summary 1.3 and 1.6). Part A features proposed: 7; accepted: 0 (every
one fails rule (c), two also (b); product summary 1.4). GEX ruling: cleared (E.14's copy; terms byte-identical).

| Root | Evidence rows | Proposals (reader ratio to D8) | Accepted |
|---|---|---|---|
| NQ | 10 | none | - |
| RTY | 15 | fomc_r1 (2.51) | no: (c) |
| ZT | 7 | zt_cpnauc (0.75) | no: (c) |
| ZF | 6 | zf_auc10y (0.76 post-2014; 1.53 full sample) | no: (c) |
| ZN | 13 | none | - |
| TN | 6 | none | - |
| ZB | 8 | k2_auc10_mto_zb (0.79) | no: (c) |
| UB | 6 | none | - |
| 6E | 9 | p6e_mehedge_nq (1.14), p6e_post_ldnfix (0.66) | no: (c); (b) |
| CL | 12 | none | - |
| NG | 10 | none | - |
| GC | 14 | none | - |
| ZC | 10 | none | - |
| ZS | 9 | zs_wasde_post_t4 (2.31 upper bound) | no: (b), (c) |
| ZL | 6 | none | - |
| HE | 8 | none | - |
| LE | 8 | none | - |

### Part B: H6 (reports/stage_e20_H6_result.json/.md; prereg reports/stage_e20_prereg_H6.md; freeze 22e606f0...)

Registered 15:36:20 as r004-E20H6 (N 480 -> 483); evaluated once 15:36:34-15:38:15 (marker 15:36:38); verified by
VerdictVerifier-FableXHigh (VERIFIED WITH NOTES; every trade matched to the cent except two MLL liquidations).
c = 4.08 MNQ ticks ($2.04) on every trade; 1.5c = 6.12 ticks; verdict window 971 equity trade dates.

| Test | Verdict | Trades | Mean gross ticks (bp) | Mean net ticks (bp) | t_B | p (one-sided) | Holm (m = 3, 0.025) | Net Sharpe |
|---|---|---|---|---|---|---|---|---|
| E20-H6-T1 (E20H6-T1) | FAIL | 893 | 1.25 (0.38) | -2.83 (-0.39) | -0.528 | 0.701 | not rejected | -0.27 |
| E20-H6-T2 (E20H6-T2) | FAIL | 446 | -3.27 (-0.35) | -7.35 (-1.11) | -0.948 | 0.828 | not rejected | -0.48 |
| E20-H6-T3 (E20H6-T3) | FAIL | 134 | -3.52 (-0.52) | -7.60 (-1.33) | -0.380 | 0.648 | not rejected | -0.19 |

Every test fails all four bars except the trade floor. Descriptive only:
- Per year (T1 trades, mean gross ticks, t, Sharpe): 2020-06..12 139, 0.27, -0.29, -0.37; 2021 239, 1.20, -0.33,
  -0.33; 2022 238, 17.39, 0.97, 0.96; 2023 236, -9.03, -1.61, -1.59; 2024-01..02 41, -29.63, -1.46, -3.53. T2: 2022 the
  only positive year (30.4 ticks, t 1.39); 2021 -21.9 (t -2.25).
- 1.5 x slippage: c 4.92 ticks; T1 Sharpe -0.35, T2 -0.54, T3 -0.22.
- Overlap with the paper's sample, 2019-05-06..2020-05-29 (never in the verdict): T1 254 trades, mean net 13.4 ticks,
  t 1.16, Sharpe 1.11; T2 104, 17.8, t 0.67, Sharpe 0.64; T3 39, 71.9, t 1.19, Sharpe 1.13.
- Eligibility (verdict window): 956 eligible of 971; 15 instrument_change; shortened days carry no trade (engine F = C-30).
  T2 warm-up: 59 of the 60 warm-up dates eligible (one instrument change), so T2's first threshold came one date late.
- MLL: one liquidation each in T1 (2023-11-30) and T2 (2021-10-07); the result's breach_dates field is empty because
  report.py reads DayClose events only (H6V-2; the dates are mll_liquidation_fill_dates).
- Exit types: T1 892 C-2 exits + 1 MLL flatten; T2 445 + 1; T3 134 + 0. No D9.7 exit, no D9.5a deferral, no locked fill.
- T3 power: 148 GEX < 0 rows in the window (count made before the freeze, after T3's status was fixed).

Reading: the rest-of-day to last-half-hour effect, strong in the paper's 1996-2020 NQ sample and positive in the
2019-05..2020-05 overlap here, is absent in 2020-06..2024-02 at MNQ cost: the unconditional gross is 1.25 ticks against
a 4.08-tick round trip; the magnitude-threshold and negative-gamma subsets are negative gross. This matches the
post-2020 decay evidence the readers found (the unreviewed SPX retest, Adams et al.'s draft).

### Part C: the search (reports/stage_e20_search.json/.md; plan reports/stage_e20_plan.md, FROZEN; freeze 94ee86b0...)

Plan reviewed by PlanReviewer-FableXHigh (BLOCK on PR-1, then APPROVE WITH FIXES on recheck), code reviewed by
SearchReviewer-FableXHigh (APPROVE WITH FIXES, no leak found). Step 6 dry check passed before the freeze: all 36 features
compute and are applicable on their event rows under the 2010-2019 swaps; removing any leg stops the build; the declared
row losses reproduced (reports/stage_e20_dry_check_step6.md). check --world on the real stores passed after one correction
(the grid assertion on real bars, removed per V2.2b; rulings section 7). Registered 17:43:59 as r005-E20S (N 483 -> 528),
before any panel or fit; run 17:44:15-17:52:20 (8:05 wall, 1.88 GB peak).

- Panel: 57,775 decision rows (13,587 at t4) on 17 vehicles over 1,248 training-calendar dates; usable rows h60 57,377,
  h120 43,988, hF 56,783; 36 features (34 frozen + rod_ret, rod_absratio), 94 feature columns with flags and identifiers.
  Closure bars counted and kept: 30 in all (NQ 7, RTY 6, LE 3, ZS 3, ZL 3, ZC 2, HE 2, ZT 1, ZF 1, 6E 1).
- Admissibility (tau 0.167, one pass): 51 of 51 (vehicle, horizon) pairs admissible.
- Nested CPCV: 15 outer splits, 4 inner folds, 45 configurations; selected per split: ridge in 14 of 15 (lambda 0.01 in 7,
  0.1 in 6, 1.0 in 1), LightGBM depth 2 in 1; horizons h60 in 8, hF in 6, h120 in 1.

SCREEN (F7): FAIL on all three items.

| Item | Value | Bar | Passes |
|---|---|---|---|
| 1. Median-path daily t (paths -1.33, -0.78, -0.87, -1.40, -1.57) | -1.334 | >= 2.0 | no |
| 2. PBO (CSCV, 16 blocks, 12,870 combinations, not degenerate) | 0.596 | < 0.5 | no |
| 3. Annualized net Sharpe at 50K (path average) | -0.826 | >= 0.5 and <= 4.0 | no |
| final_selection returns a configuration | ridge_l0.1_k2_h60 (E20-S13) | a configuration | yes |

Reported, not gating:
- DSR at N = 528: 0.00001 (observed daily Sharpe -0.052, expected maximum under the null 0.068; 1,248 dates).
- Daily mean of the nested record: -$5.55 at 50K (daily sd $106.6).
- 1.5 x slippage: median-path t -1.479, Sharpe -1.018.
- Every one of the 45 configurations has a negative CPCV OOS daily t (best: E20-S13 ridge_l0.1_k2_h60, -0.33, Sharpe
  -0.15; worst: E20-S30 lgbm_d2_k1.5_hF, -3.24). The final configuration's own CPCV record: daily t -0.327, Sharpe
  -0.147, 8,356 outer trades.
- t4 share of the final configuration's CPCV OOS net P&L: -0.079 (t4 trades +$597 of a -$7,544 total over 15 splits);
  1,398 of 9,822 trades at t4.
- r_ROD share: -1.309. With the rod_* z columns set to 0 at prediction, the final configuration's P&L falls from -$7,544
  to -$17,419: the two r_ROD features reduced losses but did not make the model profitable. The planning brief's
  expectation that a surviving late-session signal would be H6 found again does not arise: nothing survived.
- Per-product OOS round trips (median over the 5 paths; the lead's reading of V2.9 criterion 6): MNQ 779, M2K 532,
  MCL 422, MGC 232; below 30 and flagged: ZF 17, ZT 16, ZC 11, ZN 1, 6E 0; the other eight vehicles (NG, TN, ZB, UB, ZS,
  ZL, HE, LE) never traded.
- Ruin probability: not computed (the screen failed; no real-data engine path exists; plan section 9, review PR-6).

A failed screen ends Part C (F7): no B1 freeze, no dry check against a frozen model, no backward read; E20-B1 is not
registered; Steps 8 and 9 did not run. The 2010-2019 stores were hashed as bytes at start and end and never decoded.

Per-configuration table (the 45 registered configurations; ids E20-S01..S45 = registry E20S-01..45):

| Id | Configuration | Inner mean score | Outer mean score | Outer trades | CPCV OOS daily t | CPCV OOS net Sharpe | Splits selected |
|---|---|---|---|---|---|---|---|
| E20S-01 | ridge_l0.01_k1.5_h60 | -0.0255 | -0.0350 | 13579 | -1.50 | -0.67 | 4 |
| E20S-02 | ridge_l0.01_k1.5_h120 | -0.0553 | -0.0445 | 13241 | -2.06 | -0.92 | 0 |
| E20S-03 | ridge_l0.01_k1.5_hF | -0.0140 | -0.0524 | 10603 | -2.24 | -1.01 | 2 |
| E20S-04 | ridge_l0.01_k2_h60 | -0.0283 | -0.0174 | 10570 | -0.81 | -0.36 | 1 |
| E20S-05 | ridge_l0.01_k2_h120 | -0.0305 | -0.0384 | 9541 | -1.97 | -0.88 | 0 |
| E20S-06 | ridge_l0.01_k2_hF | -0.0158 | -0.0341 | 8414 | -1.64 | -0.74 | 0 |
| E20S-07 | ridge_l0.01_k3_h60 | -0.0247 | -0.0117 | 6816 | -0.65 | -0.29 | 0 |
| E20S-08 | ridge_l0.01_k3_h120 | -0.0216 | -0.0285 | 5408 | -1.69 | -0.76 | 0 |
| E20S-09 | ridge_l0.01_k3_hF | -0.0154 | -0.0255 | 5355 | -1.56 | -0.70 | 0 |
| E20S-10 | ridge_l0.1_k1.5_h60 | 0.0007 | -0.0112 | 11068 | -0.64 | -0.29 | 1 |
| E20S-11 | ridge_l0.1_k1.5_h120 | -0.0345 | -0.0502 | 9844 | -1.83 | -0.82 | 0 |
| E20S-12 | ridge_l0.1_k1.5_hF | 0.0007 | -0.0325 | 9050 | -1.62 | -0.73 | 1 |
| E20S-13 | ridge_l0.1_k2_h60 | -0.0045 | -0.0082 | 8356 | -0.33 | -0.15 | 1 |
| E20S-14 | ridge_l0.1_k2_h120 | -0.0286 | -0.0292 | 6560 | -0.98 | -0.44 | 0 |
| E20S-15 | ridge_l0.1_k2_hF | 0.0097 | -0.0217 | 6739 | -1.15 | -0.52 | 2 |
| E20S-16 | ridge_l0.1_k3_h60 | -0.0133 | -0.0178 | 4953 | -0.97 | -0.43 | 0 |
| E20S-17 | ridge_l0.1_k3_h120 | -0.0230 | -0.0189 | 3539 | -0.79 | -0.35 | 1 |
| E20S-18 | ridge_l0.1_k3_hF | -0.0232 | -0.0303 | 3764 | -1.52 | -0.68 | 0 |
| E20S-19 | ridge_l1_k1.5_h60 | -0.0051 | -0.0089 | 5702 | -0.34 | -0.15 | 1 |
| E20S-20 | ridge_l1_k1.5_h120 | -0.0311 | -0.0330 | 3928 | -0.98 | -0.44 | 0 |
| E20S-21 | ridge_l1_k1.5_hF | -0.0114 | -0.0271 | 4255 | -1.32 | -0.59 | 0 |
| E20S-22 | ridge_l1_k2_h60 | -0.0143 | -0.0289 | 3591 | -1.12 | -0.50 | 0 |
| E20S-23 | ridge_l1_k2_h120 | -0.0314 | -0.0126 | 2472 | -0.52 | -0.24 | 0 |
| E20S-24 | ridge_l1_k2_hF | -0.0410 | -0.0271 | 2554 | -1.05 | -0.47 | 0 |
| E20S-25 | ridge_l1_k3_h60 | -0.0303 | -0.0289 | 1393 | -1.27 | -0.57 | 0 |
| E20S-26 | ridge_l1_k3_h120 | n/a | 0.0002 | 1287 | -0.78 | -0.35 | 0 |
| E20S-27 | ridge_l1_k3_hF | -0.0008 | -0.0194 | 987 | -0.82 | -0.37 | 0 |
| E20S-28 | lgbm_d2_k1.5_h60 | -0.0352 | -0.0264 | 10622 | -0.98 | -0.44 | 0 |
| E20S-29 | lgbm_d2_k1.5_h120 | -0.0584 | -0.0619 | 10029 | -2.57 | -1.15 | 0 |
| E20S-30 | lgbm_d2_k1.5_hF | -0.0393 | -0.0756 | 8325 | -3.24 | -1.45 | 1 |
| E20S-31 | lgbm_d2_k2_h60 | -0.0382 | -0.0166 | 7879 | -0.75 | -0.34 | 0 |
| E20S-32 | lgbm_d2_k2_h120 | -0.0439 | -0.0663 | 6621 | -2.84 | -1.28 | 0 |
| E20S-33 | lgbm_d2_k2_hF | -0.0462 | -0.0678 | 6035 | -2.79 | -1.26 | 0 |
| E20S-34 | lgbm_d2_k3_h60 | -0.0224 | -0.0187 | 4410 | -1.03 | -0.46 | 0 |
| E20S-35 | lgbm_d2_k3_h120 | -0.0424 | -0.0482 | 3394 | -2.11 | -0.95 | 0 |
| E20S-36 | lgbm_d2_k3_hF | -0.0449 | -0.0431 | 3031 | -1.85 | -0.83 | 0 |
| E20S-37 | lgbm_d3_k1.5_h60 | -0.0339 | -0.0297 | 12328 | -1.01 | -0.45 | 0 |
| E20S-38 | lgbm_d3_k1.5_h120 | -0.0570 | -0.0754 | 12093 | -3.07 | -1.38 | 0 |
| E20S-39 | lgbm_d3_k1.5_hF | -0.0320 | -0.0720 | 9403 | -2.99 | -1.34 | 0 |
| E20S-40 | lgbm_d3_k2_h60 | -0.0301 | -0.0144 | 9416 | -0.56 | -0.25 | 0 |
| E20S-41 | lgbm_d3_k2_h120 | -0.0587 | -0.0625 | 8192 | -2.76 | -1.24 | 0 |
| E20S-42 | lgbm_d3_k2_hF | -0.0412 | -0.0592 | 7158 | -2.39 | -1.07 | 0 |
| E20S-43 | lgbm_d3_k3_h60 | -0.0315 | -0.0124 | 5672 | -0.82 | -0.37 | 0 |
| E20S-44 | lgbm_d3_k3_h120 | -0.0430 | -0.0524 | 4319 | -1.99 | -0.90 | 0 |
| E20S-45 | lgbm_d3_k3_hF | -0.0409 | -0.0453 | 4039 | -1.83 | -0.82 | 0 |

## 4. Delegation record (one row per spawn; tokens from the transcripts)

| Spawn (name) | Model | Effort | First (PDT) | Last (PDT) | Tokens |
|---|---|---|---|---|---|
| lead (Opus 5.5) | claude-opus-5-5 | xhigh | 10:21 | 20:25 | 159,332,242 |
| ProductReader-GC-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:53 | 24,482,063 |
| ProductReader-ZT-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:47 | 13,051,890 |
| ProductReader-ZS-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:48 | 13,648,311 |
| ProductReader-6E-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:51 | 16,531,694 |
| ProductReader-CL-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:54 | 22,900,247 |
| ProductReader-UB-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:45 | 10,529,386 |
| ProductReader-TN-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:44 | 9,575,403 |
| ProductReader-ZC-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:56 | 23,882,817 |
| H6Reviewer-FableXHigh | claude-fable-5-1 | xhigh | 15:12 | 15:30 | 2,865,540 |
| ProductReader-ZN-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:57 | 18,955,473 |
| ProductReader-HE-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:50 | 16,924,223 |
| BackwardTables-OpusXHigh | claude-opus-5-5 | xhigh | 16:19 | 16:39 | 19,665,357 |
| ProductReader-ZF-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:50 | 14,707,873 |
| SearchReviewer-FableXHigh | claude-fable-5-1 | xhigh | 17:12 | 17:28 | 2,774,580 |
| H6Coder-OpusXHigh | claude-opus-5-5 | xhigh | 10:40 | 15:33 | 31,068,850 |
| H6Reviewer-FableXHigh | claude-fable-5-1 | xhigh | 11:12 | 11:20 | 982,316 |
| ProductReader-ZL-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:47 | 12,659,465 |
| ScreenVerifier-FableXHigh | claude-fable-5-1 | xhigh | 17:53 | 17:56 | 990,468 |
| VerdictVerifier-FableXHigh | claude-fable-5-1 | xhigh | 15:38 | 15:55 | 3,351,142 |
| ScreenVerifier-FableXHigh | claude-fable-5-1 | xhigh | 20:12 | 20:24 | 3,349,887 |
| SearchCoder-OpusXHigh | claude-opus-5-5 | xhigh | 16:21 | 17:42 | 73,838,678 |
| ProductReader-ZB-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:48 | 14,509,703 |
| PlanReviewer-FableXHigh | claude-fable-5-1 | xhigh | 15:56 | 16:46 | 3,872,464 |
| ProductReader-RTY-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:55 | 22,003,014 |
| ProductReader-NG-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:52 | 17,217,404 |
| ProductReader-NQ-OpusHigh | claude-opus-5-5 | high | 10:32 | 10:54 | 17,508,680 |
| ProductReader-LE-OpusHigh | claude-opus-5-5 | high | 10:33 | 10:57 | 25,682,521 |
| CodeMapper-clock-panel-signals-OpusHigh | claude-opus-5-5 | high | 10:42 | 10:47 | 3,601,316 |
| CodeMapper-leakage-tests-OpusHigh | claude-opus-5-5 | high | 10:42 | 10:48 | 4,562,069 |
| CodeMapper-models-cpcv-selection-OpusHigh | claude-opus-5-5 | high | 10:42 | 10:47 | 3,255,001 |
| CodeMapper-sizing-sim-engine-OpusHigh | claude-opus-5-5 | high | 10:42 | 10:48 | 6,028,124 |
| CodeMapper-phase1-world-OpusHigh | claude-opus-5-5 | high | 10:42 | 10:47 | 4,929,967 |

## 5. Verification (each Fable finding, the ruling and the fix; full text in the review files, rulings in reports/stage_e20_rulings.md)

| Review | Verdict | Findings | Rulings (section) |
|---|---|---|---|
| H6Reviewer-FableXHigh (reports/stage_e20_review_h6.md) | APPROVE WITH FIXES | 0 BLOCKING, 3 SHOULD FIX, 7 NOTE | 2 |
| VerdictVerifier-FableXHigh, H6 (reports/stage_e20_review.md "H6 verification") | VERIFIED WITH NOTES | 0 BLOCKING, 1 SHOULD FIX, 5 NOTE | 3 |
| PlanReviewer-FableXHigh (reports/stage_e20_review_plan.md) | BLOCK, then APPROVE WITH FIXES on recheck | 1 BLOCKING, 6 SHOULD FIX, 8 NOTE; recheck +1 SHOULD FIX, 2 NOTE | 4, 4b |
| SearchReviewer-FableXHigh (reports/stage_e20_review_search_code.md) | APPROVE WITH FIXES | 0 BLOCKING, 1 SHOULD FIX, 8 NOTE | 6 |
| ScreenVerifier-FableXHigh (reports/stage_e20_review.md "Search screen verification") | VERIFIED | 0 BLOCKING, 0 SHOULD FIX, 3 NOTE | 8 |

Every BLOCKING and SHOULD FIX finding, with its fix:
- H6R-1 (code): a post-marker catch-all writes every test STOPPED with the traceback and the result file; test added.
- H6R-2 (text): the prereg header discloses the GEX sign count; section 6 records who, when and what was read.
- H6R-3 (text): section 7a adds the prior close after an early-close day, the roll difference, shortened days in T2.
- H6V-2 (descriptive): breach dates are the result's mll_liquidation_fill_dates (T1 2023-11-30, T2 2021-10-07); reading note.
- PR-1 (BLOCKING): the 2010-2019 swap table (backward_swap_table.md; plan 10.1) and the Step 6 sentinel dry check before the
  freeze; no feature NO-SOURCE; the dry check passed with no feature dropped.
- PR-2: k2_fomc_mto dropped (13:00 CT event minute wrong before 2013-03-20).
- PR-3: above-4.0 Sharpe fails the screen (reading (a)), fixed before the fit.
- PR-4: the composed builder re-applies the frozen checks by name (the grid assertion later limited to synthetic worlds per
  V2.2b, rulings 7).
- PR-5: B1's fixed-D construction declared, with E.16 F-07's single-price-bar diagnostic.
- PR-6: ruin not computed on a fail; on a pass, an engine adapter hashed before B1's registration.
- PR-7: acceptance rule (c) written as applied; RTY's ground (d) withdrawn.
- PR-16: the daily cost fallback's reach quantified (25.0% of entries for 15 vehicles; grains and livestock exits 13-18%).
- SC-1: check --world before the registration.
The verifier of H6 reproduced every verdict number independently (bar-level reconstruction, no h6_rod import): all
trades matched to the cent except the two MLL liquidations, which explain the small t differences.

## 6. Open choices (every decision the lead made on its own, with the reason)

Part A
1. **The 17 readers were spawned with the Agent tool, all at once, not inside a workflow.** The workflow runtime caps
   concurrent agents at 16; V36 and the prompt say all 17 at once with the same instructions and effort.
2. **Shared sources by assignment, not by a pre-fetch wave.** Baltussen et al. was already on disk (E.13's copy of the
   version of record), so every reader could grep it; each other cross-root source went to one class reader (NQ:
   Baltussen and Rosa; RTY: equity class and the macro calendars; ZN: rates class and the Aalto thesis; CL, ZC, LE:
   their classes). A pre-fetch wave would have added about 45 minutes of serial time.
3. **Feature-cut readings** (product summary 1.3): a table that a frozen rule derives from a calendar existing over
   both windows counts as existing (k1_vwap_dist, k5_ovr_*); partial availability from a window start, the warm-up or
   a session structure whose bars do not exist (rows then "missing", never "not applicable") does not drop a feature;
   undetermined calendars drop (k4_apipre_ret); a table not derivable from the program's calendars drops
   (k4_eiamom_r3's NYSE list); one pooled release column cannot be made product-specific, so g13-g15 drop as a group.
4. **RTY's fomc_r1 rejected** under rule (c): its published size is for SPY's 15:30-16:00 ET hold in 1993-2013, not for
   the t4-to-F hold on Russell; the plan review (PR-7) asked the written rule to state this refinement, which it now does.
5. **Excluded v2 families not re-admitted at t4** (K5-fomc-01, K6-wasdepost-01, k2_fomc_msince's reach): not in the
   frozen library's code, and F6 allows no added features; no reader proposed them with a published size.

Part B (H6)
6. **The H6 code was written by H6Coder-OpusXHigh, not by the lead.** The prompt's Step 2 says the lead writes the
   code; CLAUDE.md says the lead does not write bulk code. The lead wrote the text, ruled on every stop item and read
   the code paths the verdict rests on.
7. **T2's warm-up, the literal reading:** only eligible dates among the 60 trade dates before 2020-06-01 feed the first
   verdict thresholds; fewer than 60 means no threshold (59 were eligible, so T2 started a date late).
8. **T3, the literal reading of "previous trade date's GEX":** the row dated the equity calendar's previous trade
   date; after a futures-only holiday session there is no row, so no T3 trade (about 7 to 8 dates a year).
9. **GEX copy:** E.14's download reused (the NQ reader's reading of the terms), no new retrieval; rows on or after
   2024-03-01 cut at load.
10. **A sign count of GEX < 0 rows (148) was made before the freeze**, after T3's status was fixed, for the power
    record; disclosed in the prereg header and section 6 (review H6R-2).
11. **Registry names without hyphens** (the frozen registry's regex): E20H6-T1..T3 for E20-H6-T1..T3, E20S-01..45 for
    E20-S01..S45, E20B1-T1 for E20-B1.
12. **ENGINE_LEAD_IN_DATES = 1:** each engine run starts one trade date before its window with no entry, so the first
    window date has the D9.7 reference like every other date.
13. **The rulings file stays appendable:** the H6 freeze hashes a snapshot (reports/stage_e20_briefs/h6_rulings_at_freeze.md),
    because Steps 4, 5 and 9 append to reports/stage_e20_rulings.md.
14. **The first H6Reviewer stopped on the session usage limit** (11:21, no output); it was re-spawned fresh after the
    reset (15:12) rather than resumed, since it had written nothing.
15. **H6 evaluate ran detached** (setsid nohup), because a run-once evaluation that died with the session would leave
    the marker and no permitted rerun.

Part C (plan and search)
16. **E.12's recorded S_X** (ZF 2020-10-01, ZT 2021-10-01, the others 2019-05-06) instead of rerunning D4's rule, which
    reads research-window store bytes (F2 forbids them).
17. **MES is never loaded** (its features are cut by F6's leg rule; phase1_world would read its store by default).
18. **Four decision times allow four entries per product per date** (the v2 cap of 3 followed from three decision
    times and is read by no frozen module).
19. **rod_absratio's median is per vehicle and per t_index** (|r_ROD| grows with the time since the prior close).
20. **Composition, no v2 amendment:** pattern_search composes the frozen functions (the frozen run_pipeline cannot
    take t4 rows or skip Gate 0).
21. **Above-4.0 Sharpe fails the screen** (review PR-3, reading (a)); a clean leakage audit cannot convert it.
22. **B1 uses the fixed-D score_split construction** (review PR-5), the one behind the screen's record; the engine's
    path-dependent mechanics are excluded and named.
23. **The ruin probability is computed only after a passed screen** (review PR-6; no real-data engine path exists).
24. **The seven backward rulings of plan 10.1** (metals map and livestock calendar; LE 08:00-era t1 rows excluded;
    grains R-B1 exit; the daily cost fallback for release types without 2010-2019 rows; WPSR 2012-11-01 excluded;
    unsourced livestock dates excluded; frozen reopening labels).
25. **SearchCoder started before the PR-1 swap table existed** (16:21), building the parts already fixed; no fit before
    the reviewer's recheck and the Step 6 dry check.
26. **An independent SearchReviewer-FableXHigh** was added before the 45 registrations (CLAUDE.md: a Fable check of
    harness code a verdict rests on); the prompt names no code review for pattern_search.

Process
27. **Raw third-party pages stay uncommitted** (reports/stage_e20_briefs/pages/ and shared/ raw files;
    DO_NOT_COMMIT.txt), as E.13 and E.14 did; the fetch logs and notes are committed.
28. **A five-agent read-only code-map workflow** (opus high) mapped ml_route_v2 before the plan was written.
29. **check --world before the registration** (review SC-1): the real world was loaded once through the frozen loaders
    before the registry line, with no row, feature or fit, so a loader failure could be fixed without a post-registration
    change (F9 requires registration before any fit).
30. **The grid assertion on real bars was removed** (rulings section 7): the lead had added it at PR-4; the first real
    check --world refused on 7 NQ closure bars; the frozen V2.2b text replaces it with the L-3 booking check on real
    bars, and E.12 kept and counted closure bars (30 here). The first search manifest (66436234...) was deleted unregistered.
31. **Criterion 6's reading**: per-product round trips per path on the nested record, flagged when the median over the 5
    paths is below 30 (the median path, as criterion 2); the other readings are reported (rulings section 5).
32. **No commit before the search registration**: the prompt asks for commits only at the H6 and B1 freezes and at the
    end; the search registration carries the freeze manifest's sha256, and the end commit holds the manifest.
33. **The screen numbers got an independent Fable check** (CLAUDE.md), although the prompt's verifiers cover H6 and B1
    only; its first spawn stopped on the usage limit and it was re-spawned fresh at 20:12.
34. **The rulings and reviews are not in the search freeze manifest** (only the plan, code, tests and inputs), so the
    rulings file could take later sections; the plan pins the swap table by sha256 in its text.
35. **The cost table counts the workflow agents' transcripts** (subagents/workflows/), which reports/stage_e10_briefs/cost.py
    does not glob; reports/stage_e20_briefs/make_cost.py reuses cost.py's scan on all of them.

## 7. Decisions for the user (each with a recommendation)

Nothing passed, so no forward research-window read and no holdout-2 read is proposed (V33 item 1: no Combine either).

1. **What is closed.** H6, rest-of-day to last-half-hour momentum on NQ at MNQ cost (T1, T2, T3), on 2020-06..2024-02,
   and the ML route's net pipeline on the 17 roots with t4 and the r_ROD features, on 2019-05..2024-02. Recommendation:
   treat both as closed; no variant of either on these windows (another threshold, another gamma source, another
   decision time, more configurations) without a new pre-registration that counts the full N (now 528), and none is
   recommended: H6's gross was 1.25 ticks against a 4.08-tick round trip, and all 45 search configurations were
   negative out of sample.
2. **The backward stores.** The 2010-2019 stores stay owned and unread by any model (E20-B1 never registered). They
   remain usable for a future registered backward test of a candidate that passes elsewhere. Recommendation: keep them
   sealed by process as now; no exploratory use.
3. **The cost wall.** H6's result repeats E.17's pattern: a published effect that is sized gross in history is below the
   round trip at retail cost in recent data. Every Part A reader found the same for its root (only H6's historical
   equity figure cleared 1.5 x). Recommendation: no new intraday hypothesis on these 17 roots unless a primary source
   gives a post-2015 per-trade size above 1.5 x the D8 round trip (V31), which none of the 157 evidence rows did.
4. **The program's next step.** E.19 showed the Topstep funnel loses money without an edge (net Sharpe about 0.5 needed
   at 50K), and none of the 528 registered trials has passed. Recommendation: pause new Topstep-oriented searches and
   decide between (a) the AiTrader options readout (V33 item 3, a separate track), (b) the personal-account path for H2
   (V33 item 4, noted only), or (c) stopping the futures intraday program. The lead recommends (a) first, since it is
   the one track with a readout pending, and recording (c) as the default if it does not pass.
5. **Housekeeping.** The E.20 raw pages (about 103 MB) stay on disk uncommitted (DO_NOT_COMMIT.txt); the user may delete
   them later. The H6 result's `mll.breach_dates` field is empty by a reporting quirk (the dates are in
   `mll_liquidation_fill_dates`; H6V-2); no change is proposed to the frozen code.

## 8. Session cost

### Final ETA table

| Task | Owner | Model | Effort | Start | End | Time (min) | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Start checks + start suite | lead | opus | xhigh | 10:21 | 10:46 | 25 |  | done; suite 7138 passed |
| 1 Part A readers x17 | ProductReader-<ROOT>-OpusHigh | opus | high | 10:33 | 10:58 | 25 | 294,770,167 | done (all 17 at once) |
| 5a Code map (workflow, 5 agents) | CodeMapper-*-OpusHigh | opus | high | 10:42 | 10:49 | 7 | 22,376,477 | done (lead's addition) |
| 1c Consolidation | lead | opus | xhigh | 10:58 | 11:01 | 3 |  | done |
| 2 H6 code | H6Coder-OpusXHigh | opus | xhigh | 10:40 | 11:10 | 30 | 31,068,850 | done; follow-up 15:31-15:33 |
| 2 H6 review (1st) | H6Reviewer-FableXHigh | fable | xhigh | 11:12 | 11:21 | 9 | 3,847,856 (both spawns) | stopped: usage limit |
| PAUSE usage limit | - | - | - | 11:21 | 15:10 | 229 |  | excluded from work time |
| 2 H6 review (2nd) + fixes | H6Reviewer-FableXHigh | fable | xhigh | 15:12 | 15:34 | 22 | in the row above | APPROVE WITH FIXES; fixed |
| 3 H6 freeze, commit, register, evaluate | lead | opus | xhigh | 15:34 | 15:38 | 4 |  | done; T1-T3 FAIL |
| 4 H6 verify | VerdictVerifier-FableXHigh | fable | xhigh | 15:39 | 15:55 | 16 | 3,351,142 | VERIFIED WITH NOTES |
| 5 Plan review | PlanReviewer-FableXHigh | fable | xhigh | 15:56 | 16:18 | 22 | 3,872,464 | BLOCK on PR-1; recheck 16:42-16:47 lifted it |
| 5 Swap table (PR-1) | BackwardTables-OpusXHigh | opus | xhigh | 16:19 | 16:40 | 21 | 19,665,357 | done (lead's addition) |
| 6 Build pattern_search + dry check | SearchCoder-OpusXHigh | opus | xhigh | 16:21 | 17:13 | 52 | 73,838,678 | done; fixes 17:29-17:42 |
| 6b Code review | SearchReviewer-FableXHigh | fable | xhigh | 17:12 | 17:29 | 17 | 2,774,580 | APPROVE WITH FIXES (lead's addition) |
| 7 Freeze, check --world, register, search, screen | lead | opus | xhigh | 17:34 | 17:52 | 18 |  | SCREEN FAIL |
| 7 Screen verify (1st) | ScreenVerifier-FableXHigh | fable | xhigh | 17:53 | 17:54 | 1 | 4,340,355 (both spawns) | stopped: usage limit |
| 10 End suite (detached) | - | - | - | 17:53 | 18:12 | 19 |  | 7340 passed |
| PAUSE usage limit | - | - | - | 17:54 | 20:10 | 136 |  | excluded from work time |
| 7 Screen verify (2nd) | ScreenVerifier-FableXHigh | fable | xhigh | 20:12 | 20:25 | 13 | in the row above | see section 5 |
| 8-9 B1 freeze, register, evaluate, verify | - | - | - |  |  |  |  | not run: screen failed |
| 10 End checks, cost, return, progress, commit | lead | opus | xhigh | 20:12 | 20:25 | 13 |  | done |
| Whole stage | lead + workers | | | 10:21 | 20:25 | 239 work (+365 paused; wall 604) | 619,238,168 | initial estimate: about 12 h 40 min to 23:00 on a fail; actual work 3 h 59 min |

### Tokens per model (transcripts; reports/stage_e20_briefs/make_cost.py)

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 3,700 | 395,813 | 15,995,270 | 1,791,614 | 18,186,397 |
| claude-opus-5-5 | 5,286 | 2,366,659 | 588,839,967 | 9,839,859 | 601,051,771 |
| all | 8,986 | 2,762,472 | 604,835,237 | 11,631,473 | 619,238,168 |

Delegation share: lead 159,332,242 (25.7%), workers 459,905,926 (74.3%). By model: claude-fable-5-1 2.9%, claude-opus-5-5 97.1%

These are token counts, not plan-credit percentages; the /usage meter is the user's to read.
