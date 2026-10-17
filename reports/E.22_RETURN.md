# Stage E.22 return: the five Tier A members confirmed once each (no edge; K8 null, K3/K5/K6 no cluster statement), the micro trend book designed, E22-F1 registered; N = 533

Lead: Opus 5.5, effort xhigh, ultracode on, session 1414530f, unattended. Prompt docs/prompts/STAGE_E.22.md (commit 5a5674b,
V39). Run 2026-10-16 00:46-02:43 PDT, paused (usage limit 02:43, then the user's pause at 07:57 and a laptop restart), resumed
18:26 PDT under a user-approved window (no confirmation read after 02:00 PDT 2026-10-17, return by 03:00 PDT). Times PDT,
from `date`, file mtimes and git.

## 1. Summary

**Part A** (one confirmation run per cluster on S_X..2024-02-29 under harness v13, Holm K = 5 at alpha 0.01, N = 533; every
figure recomputed by Fable):
- **K5-fomc-01 MGC** (on GC bars, U8): **NULL**, no edge. UCB95 +0.09 against eps 71 ticks; Holm p 0.894. Cluster K5:
  no statement (two MHG Tier B trials excluded at confirmation, coverage 0.77).
- **K3-ldnrev-01 6E: NULL**, no edge. UCB95 +0.10 against 12; Holm p 0.797. K3: no statement (6S, 6N Tier B, coverage 0.93-0.94).
- **K6-limitcont-01 HE: NULL BY INACTIVITY** (10 trips < 30), no edge. UCB95 +0.39 against 7; Holm p 0.409. K6: no
  statement (limitcont LE, 0 trips; ruled R-E22-A16 before the read).
- **K8-flight-01 HEOD MGC** (on GC bars): **NULL**, no edge. UCB95 +2.25 against 71; Holm p 0.574. **K8: NULL.**
- **K8-wkndbtc-01 MNQ: INCONCLUSIVE BY DESIGN** (D4: MBT-limited window 34 days < n_b 43; BTC not owned); not run.
No Tier A member passes Holm; no edge candidate; N unchanged.

**Part B** (design study on data E.21 already read; not evidence of edge). Net Sharpe, unrounded / simple / greedy: $10K
0.47 / 0.47 / 0.07; $25K 0.47 / 0.41 / 0.29; $50K 0.47 / 0.46 / 0.31. At $25K, simple rounding: costs $572 a year,
expected 1-year max drawdown 22% of capital (95th percentile 39%), realized max drawdown 63.5% (2015-2017), IBKR margin
52% of capital on average and 104% at the 95th percentile (12 of 21 micros modelled).

**E22-F1** registered (r007-E22, **N 532 -> 533**): the $25K simple-rounded book, 36 months from its first ledger record,
PASS iff one-sided p <= 0.05 and net Sharpe >= 0.3; power about 0.22 at a true Sharpe of 0.5.

**For the user:** approve a daily settlement source (recommendation: a fresh Databento statistics-schema quote); E22-F1's
clock starts only then.

## 2. Guardrail evidence

### Start checks (verbatim; reports/stage_e22_briefs/start_checks.txt; 1,027 untracked paths omitted)

```
$ date
Fri Oct 16 00:47:41 PDT 2026
$ git status --short
$ git log --oneline -3
5a5674b docs: Stage E.22 prompt (Tier A confirmations, micro book) and V39
90e41b0 Stage E.21 multi-day round
839efc9 E.21 freeze
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
$ E.21 freeze: uv run python -m multiday.freeze_manifest verify --sha256 0bb899e56729d84075f43d72ae7e4207a026a955f1b39b39b490330a2e03bb1e
freeze verified: 18 inputs
exit 0
$ E.22 confirmation list and E22-F1 registration (written during the stage)
reports/stage_e22_confirmation_list.md not yet written
reports/stage_e22_prereg_F1.md not yet written
$ uv run pytest -q -p no:cacheprovider (detached, 00:48:05-01:09:26)
7402 passed, 3 skipped, 3 xfailed, 54 warnings in 1276.46s (0:21:16)
rc 0
```

### Resume checks after the pause (reports/stage_e22_briefs/resume_checks.txt, 18:26:48)

No run-once marker, no confirmation output, no runner or pytest process existed. Harness v13 dd2bcc60 preflight OK; holdout
all_ok True, unlocks_logged 0; REGISTRATION.md 0 bytes; spend ledger 36,402 lines 034a454b...; trial registry 8 lines
df7b662d..., N = 533; git: only ` M ledger/trial_registrations.jsonl` (r007) plus untracked files.

### End checks (verbatim; reports/stage_e22_briefs/end_checks.txt; untracked paths omitted)

```
$ date
Fri Oct 16 19:00:01 PDT 2026
$ git status --short
$ git log --oneline -3
ccd7fa7 E.22 confirmation lists
2a2bdd8 E.22 E22-F1 freeze
e40ca85 feat: harness v13 (Stage E.22 Part A), sha256 dd2bcc60
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
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4
preflight OK: dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4
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
N = 533 (8 lines)
r001-C1: C1 ['C1-T1', 'C1-T2'] N 471 -> 473 at 2026-10-09T19:29:06-07:00
r002-E16: E16 ['E16-H1', 'E16-H2', 'E16-H3', 'E16-H4', 'E16-H5'] N 473 -> 478 at 2026-10-10T00:30:15-07:00
r003-C1b: C1b ['C1b-T1', 'C1b-T2'] N 478 -> 480 at 2026-10-10T12:17:48-07:00
r004-E20H6: E20H6 ['E20H6-T1', 'E20H6-T2', 'E20H6-T3'] N 480 -> 483 at 2026-10-11T15:36:20-07:00
r005-E20S: E20S ['E20S-01', 'E20S-02', 'E20S-03', 'E20S-04', 'E20S-05', 'E20S-06', 'E20S-07', 'E20S-08', 'E20S-09', 'E20S-10', 'E20S-11', 'E20S-12', 'E20S-13', 'E20S-14', 'E20S-15', 'E20S-16', 'E20S-17', 'E20S-18', 'E20S-19', 'E20S-20', 'E20S-21', 'E20S-22', 'E20S-23', 'E20S-24', 'E20S-25', 'E20S-26', 'E20S-27', 'E20S-28', 'E20S-29', 'E20S-30', 'E20S-31', 'E20S-32', 'E20S-33', 'E20S-34', 'E20S-35', 'E20S-36', 'E20S-37', 'E20S-38', 'E20S-39', 'E20S-40', 'E20S-41', 'E20S-42', 'E20S-43', 'E20S-44', 'E20S-45'] N 483 -> 528 at 2026-10-11T17:43:59-07:00
r006-E21: E21 ['E21-T1', 'E21-T2', 'E21-T3', 'E21-T4'] N 528 -> 532 at 2026-10-14T04:12:12-07:00
r007-E22: E22 ['E22-F1'] N 532 -> 533 at 2026-10-16T02:12:01-07:00
$ wc -l ledger/trial_registrations.jsonl; sha256sum
8
df7b662db1a2d2453f6800bcd545ed196e8cdee16429285918bfbbc2e3f21301
$ E.14 C1 freeze (reports/stage_e14_prereg_C1.md; pinned afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b): sha256, tracked, no diff vs HEAD, commits touching
afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b
tracked
no diff vs HEAD
1680982 
$ E.14 C1 freeze inputs list (reports/stage_e14_c1_freeze_inputs.json; pinned 3356d676...)
list sha256 3356d67604245db99383215f1fb7f694d25a1beb71b0693a86faeb7243a5140e entries 43 mismatches ['reports/stage_e2b_harness_freeze.json']
$ E.16 freeze: uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4
changed: screening/stage_e_verdict.py
changed: data/stage_e_bars.py
exit 1
$ git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md
exit 0
$ E.18 C1b freeze: uv run python reports/stage_e18_briefs/freeze_manifest.py verify --expected 5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03
changed: reports/stage_e2b_harness_freeze.json
pin mismatch: reports/stage_e2b_harness_freeze.json
exit 1
$ git diff --quiet b714751 -- c1_replication/c1b.py tests/test_c1b.py reports/stage_e18_prereg_C1b.md reports/stage_e18_freeze.json
exit 0
$ git diff --quiet HEAD -- ml_route_v2 rules sim screening data/holdout.py live ops
exit 0
$ E.20 store sha256 (17 roots; step2 search stores and the ext2010/ext2010h backward stores, hashed as bytes, never decoded) vs reports/stage_e17_run_manifest.json
stores checked 34 mismatches []
$ E.20 H6 freeze: PYTHONPATH=. uv run python reports/stage_e20_briefs/h6_freeze_manifest.py verify 22e606f0b74532e267a4155d93e295702ff86f6e8f4143236882f3c2f230e795
manifest 22e606f0b74532e267a4155d93e295702ff86f6e8f4143236882f3c2f230e795 expected 22e606f0b74532e267a4155d93e295702ff86f6e8f4143236882f3c2f230e795 match True files 91 bad ['data/stage_e_bars.py']
exit 1
$ E.20 search freeze: uv run python -m pattern_search.freeze_manifest verify --sha256 94ee86b02d1cb644c9307be958b7791587d42c062996a6220dc901d4fe5a0f2f
REFUSED (Refused): frozen file reports/stage_e2b_harness_freeze.json is missing or changed
exit 2
$ E.21 freeze: uv run python -m multiday.freeze_manifest verify --sha256 0bb899e56729d84075f43d72ae7e4207a026a955f1b39b39b490330a2e03bb1e
freeze verified: 18 inputs
exit 0
$ E.22 confirmation list and E22-F1 registration (written during the stage)
6f2fbf381c95ee57f05237102c97347c9fe3c343d99b6bc6e6f7e377b8a1a664  reports/stage_e22_confirmation_list.md
tracked, no diff vs HEAD
04ef33a6943004adcd50c542adf719c04ba362f7a7274a140a6293c168d8473b  reports/stage_e22_prereg_F1.md
tracked, no diff vs HEAD
$ uv run pytest -q -p no:cacheprovider (detached, 02:20:36-02:40:13)
FAILED tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha
1 failed, 7634 passed, 3 skipped, 3 xfailed, 54 warnings in 1174.20s (0:19:34)
rc 1 end 02:40:13
```

The quoted end suite ran 02:20-02:40 on the final code (v13 and E22-F1 committed). A second run after the confirmations
(18:59:54) was stopped at 81% at 19:14:51 when free memory fell to 1.5 GB (pytest at 6.85 GB beside the user's other
applications); no tested code changed after 2a2bdd8 (git: no .py change outside reports/), so the 02:20 result stands.

Changed between start and end: the trial registry gained line 8 (r007-E22; 7 -> 8 lines, 085ed33c... -> df7b662d...);
the spend ledger is unchanged (36,402 lines, 034a454b...); the harness moved from v12 ece91ae8... to **v13 dd2bcc60...**
(commit e40ca85, Fable-reviewed, before any confirmation read), as the prompt's guardrail allows. **Four earlier freezes
no longer verify under v13** (E.16: screening/stage_e_verdict.py and data/stage_e_bars.py; E.18 C1b and the E.20 search
freeze: the harness manifest; E.20 H6: data/stage_e_bars.py): every file named is one the sanctioned v13 change rewrote;
those freezes pinned v12 for their own completed runs and were not edited (the same class as the E.14 inputs-list note after
v12). The end suite's single failure (tests/test_h6_rod_run.py) is the same cause: h6_rod pins the v12 harness inside the E.20
H6 freeze. Nothing dated 2024-03-01 or later was read; the March 2024 embargo and holdout-2 were never read; no Databento or
TopstepX call; no purchase; no push; no edit under live/ or ops/; no key printed.

### Order of events

| Event | Time (PDT) | Evidence |
|---|---|---|
| Prompt commit | 2026-10-16 00:45:57 | 5a5674b (git) |
| Start checks; start suite | 00:47:41; 00:48-01:09 | start_checks.txt; pytest_start.out |
| Part A facts (4 agents); rulings | 00:53-01:11; 01:03-01:05 | reports/stage_e22_briefs/partA_*.md |
| K3, K6 start rules (v12) | 01:12:47-01:13:47 | reports/stage_e_start_rule_K3.json, _K6.json |
| Price-path declaration (before any read) | 01:14:03 | reports/stage_e22_price_paths.json 860f4b11... |
| Harness v13 built; Fable review; fixes; recheck | 01:15-01:40; 01:40-01:58; 01:59-02:07; ~02:10 | reports/stage_e22_harness_change.md, _review.md |
| K8 start rule; power re-runs (working tree W1) | 01:41; 01:41-01:54 | reports/stage_e22_briefs/power_w1/ |
| v13 commit | 02:10:40 | e40ca85 |
| E22-F1 freeze commit; registration | 02:11:33; 02:12:01 | 2a2bdd8; r007-E22 (N 532 -> 533) |
| Power re-runs under v13 (identical to W1) | 02:08:38-02:19:52 | reports/stage_e22_power_k*/ |
| Lists; ListReviewer; fixes; recheck | 02:20:10; 02:20-02:37; 02:40:12; ~02:43 | reports/stage_e22_list_review.md |
| PAUSE (usage limit; user pause at 07:57; laptop restart) | 02:43-18:26 | STATE file |
| Resume checks; list commit | 18:26:48; 18:27:48 | resume_checks.txt; ccd7fa7 |
| K5 marker; run; verdict | 18:28:16; -18:31:46; 18:31:49 | reports/stage_e22_K5_RUN_ONCE.json; k5_verdict.json |
| K8 marker; run; verdict | 18:32:35; -18:34:42; 18:34:43 | K8 marker; k8_verdict.json |
| K3 marker; run; verdict | 18:36:23; -18:48:46; 18:48:54 | K3 marker; k3_verdict.json |
| K6 marker; run; verdict | 18:50:00; -18:59:17; 18:59:25 | K6 marker; k6_verdict.json |
| Verifiers K5, K8, K3, K6 | 18:32-19:12 | reports/stage_e22_verify_k*.md |
| End checks; end suite (quoted) | 19:00:01; 02:20:36-02:40:13 | end_checks.txt; pytest_end.out |
| Second end suite after the confirmations | 18:59:54-19:14:51, stopped at 81% (free memory 1.5 GB, pytest 6.85 GB) | pytest_end_1859_stopped.out |

## 3. Results

### 3.1 Part A: the list (A1)

The prompt's five Tier A members match the screening returns exactly (E.4b:13, E.4c:14, E.8:12-15 and 274, E.9:15-18 and
262-263); K5 has no other Tier A trial. As in E.5, each cluster's single run covers every runnable frozen trial (Tier A and
Tier B), so V14 (c) and L-E5-3 can use the one run (R-E22-A1). Lists (commit ccd7fa7): K5 d2a230f3..., K3 43456def...,
K6 ebb3d034..., K8 28ad6f63...; combined reports/stage_e22_confirmation_list.md 6f2fbf38....

| Cluster | Trials listed / run | Roots and S_X (D4 start rule; price path) | Power (D4) |
|---|---|---|---|
| K5 | 11 / 8 (3 OC-H-excluded) | MGC on **GC** 2019-05-06 (MGC's own window empty: U8 via V39); MHG 2022-06-01 | all sufficient (MGC supply 1,174; fomc n_b 1) |
| K3 | 30 / 27 (3 coverage-excluded) | 6A 6B 6C 6E 6J 6N 6S 2019-05-06 | all sufficient (supply 1,191; ldnrev n_b 1) |
| K6 | 27 / 27 | HE LE ZC ZL ZM ZS ZW 2019-05-06 | sufficient; limitcont LE undefined (0 research trips; R-E22-A16) |
| K8 | 4 / 3 | MGC on GC 2019-05-06, MES 2020-02-03 (D.1f), 6C 2019-05-06, MCL 2021-07-12, MBT 2024-01-02, MNQ on NQ 2019-05-06 | flight H30/HEOD supply 944, oilcad 569; **wkndbtc supply 34 < n_b 43: inconclusive by design, not run** |

Power re-runs (research window, E.5's method) under v13 matched the screening records in every field but `power`
(K5 23/23 files, K3 61/61, K6 54/55 where the one difference is the cluster record's power-undefined list, K8 9/9).

### 3.2 Part A: verdicts (D5; Holm K = 5, alpha_k 0.01; DSR at N = 533; t > 3.0; PBO < 0.5)

| Cluster | Statement | Tier A trial | Status | theta_hat | UCB95 | eps_X | Trips | Holm p (K = 5; alpha 0.01) | t | DSR (N 533) | PBO | Chain |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K5 | no statement | K5-fomc-01 MGC | null | -0.3129 | +0.0930 | +71 | 34 | 0.8938 (not rejected) | -1.253 | 5.43e-12 | +0.043 | no edge (first failing: holm) |
| K8 | null | K8-flight-01 HEOD MGC | null | -0.3075 | +2.2464 | +71 | 231 | 0.5738 (not rejected) | -0.201 | 0.00e+00 | +0.971 | no edge (first failing: holm) |
| K8 | null | K8-wkndbtc-01 MNQ | not run | - | - | - | - | 1.0000 (not rejected) | - | no series | +0.971 | no edge (first failing: holm) |
| K3 | no statement | K3-ldnrev-01 6E | null | -0.1071 | +0.1032 | +12 | 55 | 0.7974 (not rejected) | -0.844 | 3.04e-10 | +0.543 | no edge (first failing: holm) |
| K6 | no statement | K6-limitcont-01 HE | null by inactivity | +0.0495 | +0.3869 | +7 | 10 | 0.4088 (not rejected) | +0.237 | 5.77e-09 | +0.557 | no edge (first failing: holm) |

#### K5 (verdict sha256 51061000f6b0...; statement: no statement)

| Ord | Trial | Tier | Status | Days | Trips | theta_hat | UCB95 | SE_boot | eps_X | Null power | p_upper |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K5-cp1-01 MGC | B | null | 1174 | 1132 | -3.2051 | -2.1072 | +0.6593 | 71.0 | +1.000 | +1.0000 |
| 2 | K5-cp1-01 MHG | excluded | not run | - | - | - | - | - | - | - | - |
| 3 | K5-cp2-01 MGC | B | null | 1174 | 1166 | -3.8527 | -0.3417 | +2.1091 | 71.0 | +1.000 | +0.9692 |
| 4 | K5-cp2-01 MHG | excluded | not run | - | - | - | - | - | - | - | - |
| 5 | K5-cp3-01 MGC | B | null | 1174 | 489 | -5.1667 | -1.5998 | +2.1632 | 71.0 | +1.000 | +0.9916 |
| 6 | K5-cp3-01 MHG | B | inconclusive | - | - | - | - | - | - | - | - |
| 7 | K5-preauc-01 MGC | B | null | 1174 | 1115 | -4.0368 | -3.0145 | +0.6180 | 71.0 | +1.000 | +1.0000 |
| 8 | K5-pmfix-01 MGC | excluded | not run | - | - | - | - | - | - | - | - |
| 9 | K5-fomc-01 MGC | A | null | 1174 | 34 | -0.3129 | +0.0930 | +0.2505 | 71.0 | +1.000 | +0.8938 |
| 10 | K5-ovr-01 MGC | B | null | 1174 | 1221 | -5.5728 | -2.8922 | +1.6550 | 71.0 | +1.000 | +0.9992 |
| 11 | K5-ovr-01 MHG | B | inconclusive | - | - | - | - | - | - | - | - |

Covered: 8; not covered: K5-cp1-01 MHG (not run: excluded (not Tier A or B)); K5-cp2-01 MHG (not run: excluded (not Tier A or B)); K5-pmfix-01 MGC (not run: excluded (not Tier A or B)); blocking: K5-cp3-01 MHG (inconclusive: record status 'excluded_before_screening': no series); K5-ovr-01 MHG (inconclusive: record status 'excluded_before_screening': no series); null by inactivity: none.
Edge chain: Holm K = 5 (m = 1); descriptive K = 9: K5-fomc-01 MGC p 0.8938 vs 0.00556; DSR variance 0.00269005 over 6 series; PBO +0.0429 over 6 series.

#### K8 (verdict sha256 0a2a820b2210...; statement: null)

| Ord | Trial | Tier | Status | Days | Trips | theta_hat | UCB95 | SE_boot | eps_X | Null power | p_upper |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K8-flight-01 H30 MGC | B | null | 944 | 231 | -0.2280 | +1.2278 | +0.8700 | 71.0 | +1.000 | +0.5969 |
| 2 | K8-flight-01 HEOD MGC | A | null | 944 | 231 | -0.3075 | +2.2464 | +1.5217 | 71.0 | +1.000 | +0.5738 |
| 3 | K8-oilcad-01 6C | B | null | 569 | 1438 | -4.1124 | -2.6674 | +0.8864 | 9.0 | +1.000 | +1.0000 |
| 4 | K8-wkndbtc-01 MNQ | A | not run | - | - | - | - | - | - | - | - |

Covered: 3; not covered: K8-wkndbtc-01 MNQ (not run: inconclusive by design); blocking: none; null by inactivity: none.
Edge chain: Holm K = 5 (m = 2); descriptive K = 9: K8-flight-01 HEOD MGC p 0.5738 vs 0.00278, K8-wkndbtc-01 MNQ p 1.0000 vs 0.00556; DSR variance 0.00937685 over 3 series; PBO +0.9714 over 3 series.

#### K3 (verdict sha256 9f6e74c8605f...; statement: no statement)

| Ord | Trial | Tier | Status | Days | Trips | theta_hat | UCB95 | SE_boot | eps_X | Null power | p_upper |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K3-cp1-01 6E | B | null | 1191 | 1134 | -0.4478 | +0.3306 | +0.4680 | 12.0 | +1.000 | +0.8279 |
| 2 | K3-cp1-01 6A | B | null | 1191 | 1100 | -1.6585 | -0.9911 | +0.4024 | 11.0 | +1.000 | +1.0000 |
| 3 | K3-cp1-01 6B | B | null | 1191 | 1107 | -0.3684 | +0.1347 | +0.3064 | 8.0 | +1.000 | +0.8849 |
| 4 | K3-cp1-01 6C | B | null | 1191 | 1131 | -1.3204 | -0.7847 | +0.3239 | 9.0 | +1.000 | +1.0000 |
| 5 | K3-cp1-01 6J | B | null | 1191 | 1118 | -1.2085 | -0.6233 | +0.3462 | 10.0 | +1.000 | +0.9998 |
| 6 | K3-cp1-01 6S | excluded | not run | - | - | - | - | - | - | - | - |
| 7 | K3-cp1-01 6N | excluded | not run | - | - | - | - | - | - | - | - |
| 8 | K3-cp2-01 6E | B | null | 1191 | 1183 | -3.4087 | -1.6286 | +1.0651 | 12.0 | +1.000 | +0.9993 |
| 9 | K3-cp2-01 6A | B | null | 1191 | 1184 | -1.5796 | +0.0108 | +0.9438 | 11.0 | +1.000 | +0.9565 |
| 10 | K3-cp2-01 6B | B | null | 1191 | 1186 | -1.7056 | -0.5354 | +0.7028 | 8.0 | +1.000 | +0.9920 |
| 11 | K3-cp2-01 6C | B | null | 1191 | 1182 | -1.3914 | -0.1754 | +0.7275 | 9.0 | +1.000 | +0.9711 |
| 12 | K3-cp2-01 6J | B | null | 1191 | 1173 | -1.3200 | -0.0282 | +0.7783 | 10.0 | +1.000 | +0.9571 |
| 13 | K3-cp2-01 6S | B | inconclusive | - | - | - | - | - | - | - | - |
| 14 | K3-cp2-01 6N | excluded | not run | - | - | - | - | - | - | - | - |
| 15 | K3-cp3-01 6E | B | null | 1191 | 513 | +0.2227 | +2.2949 | +1.2761 | 12.0 | +1.000 | +0.4292 |
| 16 | K3-cp3-01 6A | B | null | 1191 | 544 | -1.0236 | +1.0324 | +1.2198 | 11.0 | +1.000 | +0.8050 |
| 17 | K3-cp3-01 6B | B | null | 1191 | 548 | +0.2622 | +2.0640 | +1.0557 | 8.0 | +1.000 | +0.3997 |
| 18 | K3-cp3-01 6C | B | null | 1191 | 538 | -2.3067 | -0.6401 | +1.0086 | 9.0 | +1.000 | +0.9892 |
| 19 | K3-cp3-01 6J | B | null | 1191 | 543 | -0.2039 | +1.6850 | +1.1603 | 10.0 | +1.000 | +0.5728 |
| 20 | K3-cp3-01 6S | B | null | 1191 | 497 | -0.5882 | +1.5190 | +1.2898 | 13.0 | +1.000 | +0.6775 |
| 21 | K3-cp3-01 6N | B | inconclusive | - | - | - | - | - | - | - | - |
| 22 | K3-ldnrev-01 6E | A | null | 1191 | 55 | -0.1071 | +0.1032 | +0.1287 | 12.0 | +1.000 | +0.7974 |
| 23 | K3-ldnrev-01 6J | B | null | 1191 | 53 | -0.1314 | +0.0203 | +0.0961 | 10.0 | +1.000 | +0.9069 |
| 24 | K3-ldnrev-01 6S | B | null | 1191 | 55 | -0.0320 | +0.2120 | +0.1483 | 13.0 | +1.000 | +0.5863 |
| 25 | K3-ldnmom-01 6E | B | null | 1191 | 1063 | -1.5901 | -0.7328 | +0.5113 | 12.0 | +1.000 | +0.9986 |
| 26 | K3-ldnmom-01 6J | B | null | 1191 | 1033 | -2.1492 | -1.5410 | +0.3734 | 10.0 | +1.000 | +1.0000 |
| 27 | K3-mehedge-01 6J | B | null | 1191 | 55 | -0.1134 | +0.2476 | +0.2204 | 10.0 | +1.000 | +0.6955 |
| 28 | K3-ecbfix-01 6E | B | null | 1191 | 2301 | -1.2285 | +3.3484 | +2.6948 | 12.0 | +0.998 | +0.6753 |
| 29 | K3-tkypre-01 6J | B | null | 1191 | 224 | +0.7285 | +1.3478 | +0.3684 | 10.0 | +1.000 | +0.0271 |
| 30 | K3-tkypost-01 6J | B | null | 1191 | 1091 | -1.0613 | +0.6714 | +1.0283 | 10.0 | +1.000 | +0.8550 |

Covered: 27; not covered: K3-cp1-01 6S (not run: excluded (not Tier A or B)); K3-cp1-01 6N (not run: excluded (not Tier A or B)); K3-cp2-01 6N (not run: excluded (not Tier A or B)); blocking: K3-cp2-01 6S (inconclusive: record status 'excluded_before_screening': no series); K3-cp3-01 6N (inconclusive: record status 'excluded_before_screening': no series); null by inactivity: none.
Edge chain: Holm K = 5 (m = 1); descriptive K = 9: K3-ldnrev-01 6E p 0.7974 vs 0.00556; DSR variance 0.00241732 over 25 series; PBO +0.5429 over 25 series.

#### K6 (verdict sha256 265d9ec018f2...; statement: no statement)

| Ord | Trial | Tier | Status | Days | Trips | theta_hat | UCB95 | SE_boot | eps_X | Null power | p_upper |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K6-cp1-01 ZC | B | null | 1130 | 1060 | -1.5630 | -1.2071 | +0.2182 | 4.0 | +1.000 | +1.0000 |
| 2 | K6-cp1-01 ZW | B | null | 1129 | 1075 | -1.1743 | -0.6529 | +0.3159 | 4.0 | +1.000 | +0.9998 |
| 3 | K6-cp1-01 ZS | B | null | 1136 | 1109 | -1.7015 | -1.1732 | +0.3261 | 5.0 | +1.000 | +1.0000 |
| 4 | K6-cp1-01 ZM | B | null | 1106 | 1075 | -1.2097 | -0.6902 | +0.3119 | 5.0 | +1.000 | +0.9999 |
| 5 | K6-cp1-01 ZL | B | null | 1129 | 1076 | -2.4878 | -1.6296 | +0.5172 | 11.0 | +1.000 | +1.0000 |
| 6 | K6-cp1-01 HE | B | null | 1104 | 833 | -1.0354 | -0.4729 | +0.3433 | 7.0 | +1.000 | +0.9986 |
| 7 | K6-cp1-01 LE | B | null | 1109 | 915 | -2.0954 | -1.6102 | +0.3000 | 8.0 | +1.000 | +1.0000 |
| 8 | K6-cp2-01 ZC | B | null | 1130 | 1008 | -1.6711 | -1.0677 | +0.3695 | 4.0 | +1.000 | +1.0000 |
| 9 | K6-cp2-01 ZW | B | null | 1129 | 1070 | -0.8385 | +0.3623 | +0.7176 | 4.0 | +1.000 | +0.8807 |
| 10 | K6-cp2-01 ZS | B | null | 1136 | 1077 | -1.7164 | -0.4434 | +0.7787 | 5.0 | +1.000 | +0.9845 |
| 11 | K6-cp2-01 ZM | B | null | 1106 | 1033 | -1.3235 | -0.1204 | +0.7288 | 5.0 | +1.000 | +0.9666 |
| 12 | K6-cp2-01 ZL | B | null | 1129 | 1081 | -2.0867 | -0.1249 | +1.2129 | 11.0 | +1.000 | +0.9531 |
| 13 | K6-cp2-01 HE | B | null | 1104 | 906 | -1.0058 | +0.3860 | +0.8592 | 7.0 | +1.000 | +0.8747 |
| 14 | K6-cp2-01 LE | B | null | 1109 | 973 | -2.9227 | -1.8320 | +0.6727 | 8.0 | +1.000 | +1.0000 |
| 15 | K6-cp3-01 ZC | B | null | 1130 | 501 | -1.1126 | -0.2403 | +0.5310 | 4.0 | +1.000 | +0.9810 |
| 16 | K6-cp3-01 ZW | B | null | 1129 | 472 | -1.5916 | -0.0890 | +0.8982 | 4.0 | +0.998 | +0.9643 |
| 17 | K6-cp3-01 ZS | B | null | 1136 | 511 | -1.9350 | -0.3332 | +0.9650 | 5.0 | +1.000 | +0.9770 |
| 18 | K6-cp3-01 ZM | B | null | 1106 | 515 | -1.4151 | +0.0896 | +0.8933 | 5.0 | +1.000 | +0.9452 |
| 19 | K6-cp3-01 ZL | B | null | 1129 | 482 | -1.1039 | +1.3205 | +1.4759 | 11.0 | +1.000 | +0.7683 |
| 20 | K6-cp3-01 HE | B | null | 1104 | 480 | -1.6296 | +0.1612 | +1.1061 | 7.0 | +1.000 | +0.9268 |
| 21 | K6-cp3-01 LE | B | null | 1109 | 487 | -1.8153 | -0.5006 | +0.7969 | 8.0 | +1.000 | +0.9875 |
| 22 | K6-crushgap-01 ZS | B | null | 1028 | 516 | -2.5773 | -0.6257 | +1.1941 | 5.0 | +0.994 | +0.9822 |
| 23 | K6-limitcont-01 HE | A | null by inactivity | 1104 | 10 | +0.0495 | +0.3869 | +0.2068 | 7.0 | +1.000 | +0.4088 |
| 24 | K6-limitcont-01 LE | B | inconclusive | 1109 | 0 | +0.0000 | +0.0000 | +0.0000 | 8.0 | +0.000 | +1.0000 |
| 25 | K6-wasdepre-01 ZC | B | null | 1130 | 55 | -0.2534 | +0.0387 | +0.1776 | 4.0 | +1.000 | +0.9264 |
| 26 | K6-wasdepre-01 ZS | B | null | 1136 | 57 | -0.4458 | +0.1724 | +0.3788 | 5.0 | +1.000 | +0.8782 |
| 27 | K6-wasdepost-01 ZC | B | null | 1130 | 54 | -0.0691 | +0.1482 | +0.1351 | 4.0 | +1.000 | +0.7068 |

Covered: 27; not covered: ; blocking: K6-limitcont-01 LE (inconclusive: zero trips, SE_boot = 0, null power < 0.80); null by inactivity: K6-limitcont-01 HE.
Edge chain: Holm K = 5 (m = 1); descriptive K = 9: K6-limitcont-01 HE p 0.4088 vs 0.00556; DSR variance 0.0035193 over 27 series; PBO +0.5571 over 27 series.

Reading. Every Tier A member's own null status is null (or null by inactivity) at power 1.0, and none comes near Holm, so
the edge chain stops at its first step for all five. K8's statement is **null**. K3, K5 and K6 get **no cluster statement**
under NULL_CRITERIA_E 1 and 6: in K3 and K5, Tier B trials on the thinnest products (6S, 6N; MHG) failed D9's member-level
coverage check on their confirmation windows (0.93-0.94; 0.77), so the frozen runner excluded them before screening and the
frozen verdict classes them inconclusive (VerdictVerifier-K5 confirmed this is the required reading); in K6, limitcont LE had
no trip (the outcome R-E22-A16 accepted before the read). The descriptive Holm at K = 9 (V14 b) gives the same decisions.
Program-level family-wise error: K4 was tested at 0.05/9 = 0.0056 in E.5 and the four E.22 clusters at 0.01, total at most
0.0456 < 0.05.

### 3.3 Part B: the micro trend book (design study; reports/stage_e22_microbook.md, .json)

These figures re-use data E.21 already read (2010-07..2024-02); they are a design study and not evidence of edge. No p-value,
no verdict, nothing added to N. Rule: Carver's EWMAC 8/32, 16/64, 32/128, 64/256 (his production scalars 5.95/4.10/2.79/1.91,
cap 20), FDM 1.1314 and IDM 2.3518 from his formulas (cited in reports/stage_e22_briefs/carver_sources.md), 20% vol target,
equal weights, next-settlement fills, D8 costs (D8 extension for 8 micros, flagged). Rounding: (a) Carver's rounded and
buffered baseline; (b) his November 2021 greedy minimum-tracking-error optimiser (shadow cost 250, buffer 0.0125, correlation
shrink 0.5).

#### 1. Universe (S1)
| Micro | Exposure | Owned path | Multiplier | Tick | Costs | Data | Status |
|---|---|---|---|---|---|---|---|
| MNQ | Nasdaq-100 | NQ | 2 USD per price unit | 0.25 / $0.50 | frozen | 2010-07-01..2024-02-29 | modelled |
| M2K | Russell 2000 | RTY | 5 USD per price unit | 0.1 / $0.50 | frozen | 2017-07-10..2024-02-29 | modelled |
| MGC | Gold | GC | 10 USD per price unit | 0.1 / $1.00 | frozen | 2010-07-01..2024-02-29 | modelled |
| MCL | WTI crude | CL | 100 USD per price unit | 0.01 / $1.00 | frozen | 2010-07-01..2024-02-29 | modelled |
| MNG | Henry Hub gas | NG | 1000 USD per price unit | 0.001 / $1.00 | extension | 2010-07-01..2024-02-29 | modelled |
| M6E | EUR/USD | 6E | 12500 USD per price unit | 0.0001 / $1.25 | extension | 2010-07-01..2024-02-29 | modelled |
| 2YY | 2-year yield | ZT (yield proxy, D 1.9, declared approximation, UNSOURCED (lead_spec_B S3.6)) | 10 USD per bp | 0.1 / $1.00 | extension | 2010-07-01..2024-02-29 | modelled |
| 10Y | 10-year yield | ZN (yield proxy, D 6.5, declared approximation, UNSOURCED (lead_spec_B S3.6)) | 10 USD per bp | 0.1 / $1.00 | extension | 2010-07-01..2024-02-29 | modelled |
| 30Y | 30-year yield | ZB (yield proxy, D 15.0, declared approximation, UNSOURCED (lead_spec_B S3.6)) | 10 USD per bp | 0.1 / $1.00 | extension | 2010-07-01..2024-02-29 | modelled |
| MZC | Corn | ZC | 500 USD per price unit | 0.005 / $2.50 | extension | 2010-07-01..2024-02-29 | modelled |
| MZS | Soybeans | ZS | 500 USD per price unit | 0.005 / $2.50 | extension | 2010-07-01..2024-02-29 | modelled |
| MZL | Soybean oil | ZL | 6000 USD per price unit | 0.0002 / $1.20 | extension | 2010-07-01..2024-02-29 | modelled |
| SIL |  |  |  |  |  |  | not modelled: no owned silver path (SI not owned) |
| MHG |  |  |  |  |  |  | not modelled: only owned path HG/MHG step 2 2019-05..2024-02, never read by E.21; Part A K5 confirmation data |
| M6A |  |  |  |  |  |  | not modelled: only owned path 6A step 2, never read by E.21; Part A K3 confirmation data |
| M6B |  |  |  |  |  |  | not modelled: only owned path 6B step 2, never read by E.21; Part A K3 confirmation data |
| MCD |  |  |  |  |  |  | not modelled: only owned path 6C step 2, never read by E.21; Part A K3 confirmation data |
| MJY |  |  |  |  |  |  | not modelled: only owned path 6J step 2, never read by E.21; Part A K3 confirmation data |
| MZW |  |  |  |  |  |  | not modelled: only owned path ZW step 2, never read by E.21; Part A K6 confirmation data |
| MZM |  |  |  |  |  |  | not modelled: only owned path ZM step 2, never read by E.21; Part A K6 confirmation data |
| MES |  |  |  |  |  |  | not modelled: no owned 2010-2024 path (only MES's Stage D 2019-2024 store, a Part A leg) |
| MTN | Ultra 10-year (micro) | TN | 100 | 0.0078125 / $1.562 | extension |  | sensitivity only ($25K, in place of 10Y/30Y) |
| MWN | Ultra bond (micro) | UB | 100 | 0.03125 / $3.125 | extension |  | sensitivity only ($25K, in place of 10Y/30Y) |

Specs: E.13 T-28 (AMP contract specifications; quotes per row in forward/config_f1.json and microbook/universe.py). Costs 'frozen' = base_rules' D8 vehicle tables (settlement bucket, base); 'extension' = FLAGGED S6 D8 extension (commission per side + 1 tick per side). Yield-micro and micro-grain commissions are UNSOURCED (declared $1.92 RT, the largest frozen micro figure). Yield-proxy durations ZT 1.9, ZN 6.5, ZB 15.0 are a declared approximation, UNSOURCED.

#### 4. Returns by capital and method (S5)
Daily net $ P&L series from the first fill of the unrounded book (2011-07-08) to 2024-02-29; annualised x252 (mean) and x sqrt(252) (sd, Sharpe). Fixed capital, no compounding. Stress = 2 x slippage (S6).

| Book | Mean $/yr | Sd $/yr | Mean % | Sd % (target 20) | SR gross | SR net | SR net stress | Net SR loss vs unrounded | Corr with unrounded |
|---|---|---|---|---|---|---|---|---|---|
| $10,000 unrounded (reference) | 1,047 | 2,208 | 10.5 | 22.1 | 0.61 | 0.47 | 0.40 | 0.00 | 1.00 |
| $10,000 simple (rounded + buffered) | 945 | 2,010 | 9.5 | 20.1 | 0.57 | 0.47 | 0.41 | 0.00 | 0.84 |
| $10,000 greedy (Nov 2021, shrink 0.5) | 80 | 1,089 | 0.8 | 10.9 | 0.09 | 0.07 | 0.07 | 0.40 | 0.48 |
| $25,000 unrounded (reference) | 2,619 | 5,519 | 10.5 | 22.1 | 0.61 | 0.47 | 0.40 | 0.00 | 1.00 |
| $25,000 simple (rounded + buffered) | 2,219 | 5,461 | 8.9 | 21.8 | 0.51 | 0.41 | 0.34 | 0.07 | 0.95 |
| $25,000 greedy (Nov 2021, shrink 0.5) | 1,150 | 4,033 | 4.6 | 16.1 | 0.31 | 0.29 | 0.27 | 0.19 | 0.75 |
| $25,000 WITHOUT yield proxies, unrounded (reference) | 2,144 | 5,325 | 8.6 | 21.3 | 0.52 | 0.40 | 0.33 | 0.00 | 1.00 |
| $25,000 WITHOUT yield proxies, simple (rounded + buffered) | 1,878 | 5,388 | 7.5 | 21.6 | 0.44 | 0.35 | 0.29 | 0.05 | 0.95 |
| $25,000 WITHOUT yield proxies, greedy (Nov 2021, shrink 0.5) | 1,033 | 4,334 | 4.1 | 17.3 | 0.27 | 0.24 | 0.22 | 0.16 | 0.78 |
| $50,000 unrounded (reference) | 5,237 | 11,039 | 10.5 | 22.1 | 0.61 | 0.47 | 0.40 | 0.00 | 1.00 |
| $50,000 simple (rounded + buffered) | 5,048 | 10,968 | 10.1 | 21.9 | 0.57 | 0.46 | 0.40 | 0.01 | 0.99 |
| $50,000 greedy (Nov 2021, shrink 0.5) | 2,521 | 8,023 | 5.0 | 16.0 | 0.35 | 0.31 | 0.30 | 0.16 | 0.81 |

#### 5. Turnover and costs (S5, S6)
| Book | Contracts traded/yr | Roll fills/yr | Round turns/yr | Cost $/yr | Cost % of capital | Cost (SR units) | Cost $/yr stress |
|---|---|---|---|---|---|---|---|
| $10,000 unrounded (reference) | 81 | 53 | 67 | 296 | 2.96 | 0.134 | 471 |
| $10,000 simple (rounded + buffered) | 51 | 40 | 46 | 206 | 2.06 | 0.102 | 328 |
| $10,000 greedy (Nov 2021, shrink 0.5) | 5 | 5 | 5 | 15 | 0.15 | 0.014 | 23 |
| $25,000 unrounded (reference) | 202 | 133 | 168 | 741 | 2.96 | 0.134 | 1,178 |
| $25,000 simple (rounded + buffered) | 131 | 127 | 129 | 572 | 2.29 | 0.104 | 910 |
| $25,000 greedy (Nov 2021, shrink 0.5) | 23 | 44 | 33 | 120 | 0.48 | 0.030 | 185 |
| $25,000 WITHOUT yield proxies, unrounded (reference) | 157 | 119 | 138 | 648 | 2.59 | 0.121 | 1,055 |
| $25,000 WITHOUT yield proxies, simple (rounded + buffered) | 102 | 111 | 107 | 502 | 2.01 | 0.093 | 818 |
| $25,000 WITHOUT yield proxies, greedy (Nov 2021, shrink 0.5) | 28 | 48 | 38 | 137 | 0.55 | 0.031 | 213 |
| $50,000 unrounded (reference) | 404 | 266 | 335 | 1,481 | 2.96 | 0.134 | 2,357 |
| $50,000 simple (rounded + buffered) | 262 | 259 | 260 | 1,154 | 2.31 | 0.105 | 1,837 |
| $50,000 greedy (Nov 2021, shrink 0.5) | 53 | 98 | 75 | 273 | 0.55 | 0.034 | 420 |

#### 6. Drawdowns (S5)
Bootstrap: circular blocks of 21 days, 10,000 resamples of 252 days, seed 20261016 (a fresh generator per series); expected = mean, worst = 95th percentile, also the 99th.

| Book | Realized max DD $ | % of capital | Peak .. trough | Exp. 1y max DD $ | p95 $ | p99 $ | Exp. % | p95 % | p99 % |
|---|---|---|---|---|---|---|---|---|---|
| $10,000 unrounded (reference) | 5,471 | 54.7 | 2015-01-30 .. 2017-09-27 | 2,088 | 3,771 | 4,678 | 20.9 | 37.7 | 46.8 |
| $10,000 simple (rounded + buffered) | 3,342 | 33.4 | 2015-01-30 .. 2017-09-29 | 1,927 | 3,491 | 4,413 | 19.3 | 34.9 | 44.1 |
| $10,000 greedy (Nov 2021, shrink 0.5) | 3,340 | 33.4 | 2012-02-28 .. 2017-02-07 | 1,101 | 2,080 | 2,633 | 11.0 | 20.8 | 26.3 |
| $25,000 unrounded (reference) | 13,677 | 54.7 | 2015-01-30 .. 2017-09-27 | 5,221 | 9,428 | 11,695 | 20.9 | 37.7 | 46.8 |
| $25,000 simple (rounded + buffered) | 15,874 | 63.5 | 2015-01-30 .. 2017-09-28 | 5,501 | 9,851 | 12,348 | 22.0 | 39.4 | 49.4 |
| $25,000 greedy (Nov 2021, shrink 0.5) | 9,064 | 36.3 | 2022-05-05 .. 2024-01-12 | 4,040 | 7,614 | 9,872 | 16.2 | 30.5 | 39.5 |
| $25,000 WITHOUT yield proxies, unrounded (reference) | 13,951 | 55.8 | 2015-03-17 .. 2019-12-03 | 5,083 | 8,962 | 11,187 | 20.3 | 35.8 | 44.7 |
| $25,000 WITHOUT yield proxies, simple (rounded + buffered) | 14,949 | 59.8 | 2022-05-05 .. 2024-01-31 | 5,232 | 9,481 | 11,848 | 20.9 | 37.9 | 47.4 |
| $25,000 WITHOUT yield proxies, greedy (Nov 2021, shrink 0.5) | 10,781 | 43.1 | 2022-05-05 .. 2024-01-05 | 4,373 | 8,045 | 10,232 | 17.5 | 32.2 | 40.9 |
| $50,000 unrounded (reference) | 27,354 | 54.7 | 2015-01-30 .. 2017-09-27 | 10,441 | 18,856 | 23,389 | 20.9 | 37.7 | 46.8 |
| $50,000 simple (rounded + buffered) | 22,896 | 45.8 | 2015-01-30 .. 2017-09-27 | 10,342 | 18,622 | 23,360 | 20.7 | 37.2 | 46.7 |
| $50,000 greedy (Nov 2021, shrink 0.5) | 14,340 | 28.7 | 2022-10-20 .. 2024-01-05 | 7,650 | 14,068 | 17,837 | 15.3 | 28.1 | 35.7 |

#### 7. Instruments at zero and margin (S5)
Margin: /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e22_briefs/ibkr_margins.json (IBKR overnight initial per contract, as fetched in 2026, applied to every date: a present-day rate on historical positions; since sizing gives more contracts when prices are lower, the early years' margin is biased upward, notably for MNQ and MGC). The unrounded book's margin uses fractional contracts.

| Book | Mean share of live instruments at 0 | Margin mean $ | p95 $ | max $ | % of capital (mean/p95/max) | Margin not sourced |
|---|---|---|---|---|---|---|
| $10,000 unrounded (reference) | 0.00 | 5,749 | 10,615 | 13,671 | 57.5 / 106.2 / 136.7 | none |
| $10,000 simple (rounded + buffered) | 0.70 | 3,994 | 9,715 | 14,625 | 39.9 / 97.2 / 146.2 | none |
| $10,000 greedy (Nov 2021, shrink 0.5) | 0.95 | 1,673 | 6,632 | 10,350 | 16.7 / 66.3 / 103.5 | none |
| $25,000 unrounded (reference) | 0.00 | 14,373 | 26,538 | 34,178 | 57.5 / 106.2 / 136.7 | none |
| $25,000 simple (rounded + buffered) | 0.40 | 12,990 | 26,021 | 34,835 | 52.0 / 104.1 / 139.3 | none |
| $25,000 greedy (Nov 2021, shrink 0.5) | 0.71 | 7,828 | 16,982 | 24,850 | 31.3 / 67.9 / 99.4 | none |
| $25,000 WITHOUT yield proxies, unrounded (reference) | 0.00 | 12,601 | 28,617 | 36,153 | 50.4 / 114.5 / 144.6 | none |
| $25,000 WITHOUT yield proxies, simple (rounded + buffered) | 0.39 | 11,505 | 28,675 | 36,827 | 46.0 / 114.7 / 147.3 | none |
| $25,000 WITHOUT yield proxies, greedy (Nov 2021, shrink 0.5) | 0.66 | 9,415 | 22,796 | 30,200 | 37.7 / 91.2 / 120.8 | none |
| $50,000 unrounded (reference) | 0.00 | 28,745 | 53,076 | 68,356 | 57.5 / 106.2 / 136.7 | none |
| $50,000 simple (rounded + buffered) | 0.22 | 27,654 | 52,010 | 67,071 | 55.3 / 104.0 / 134.1 | none |
| $50,000 greedy (Nov 2021, shrink 0.5) | 0.57 | 16,561 | 33,288 | 46,421 | 33.1 / 66.6 / 92.8 | none |

#### 8. Capital sweep: Sharpe loss against unrounded (S5)
| Capital | SR net unrounded | SR net simple | SR net greedy | Loss simple | Loss greedy | Zero share simple | Zero share greedy |
|---|---|---|---|---|---|---|---|
| $10,000 | 0.47 | 0.47 | 0.07 | 0.00 | 0.40 | 0.70 | 0.95 |
| $15,000 | 0.47 | 0.79 | 0.39 | -0.31 | 0.09 | 0.56 | 0.87 |
| $25,000 | 0.47 | 0.41 | 0.29 | 0.07 | 0.19 | 0.40 | 0.71 |
| $35,000 | 0.47 | 0.43 | 0.15 | 0.04 | 0.33 | 0.31 | 0.64 |
| $50,000 | 0.47 | 0.46 | 0.31 | 0.01 | 0.16 | 0.22 | 0.57 |
| $75,000 | 0.47 | 0.46 | 0.31 | 0.01 | 0.17 | 0.15 | 0.51 |
| $100,000 | 0.47 | 0.48 | 0.30 | -0.01 | 0.18 | 0.11 | 0.49 |
| $250,000 | 0.47 | 0.48 | 0.29 | -0.01 | 0.19 | 0.04 | 0.40 |

Reading. Simple rounding tracks the unrounded book closely from $25K up (correlation 0.95 at $25K, 0.99 at $50K); at $10K
the correlation is 0.84 and 70% of live instruments sit at zero on an average day. Carver's greedy, at the November 2021
post's parameters, holds most instruments at zero and loses 0.16-0.40 of net Sharpe at every capital level in this 12-micro
universe; its own tracking error is worse than plain rounding on most dates from $50K up (section 10b of the report). The
two figures that matter most for a real account: at the 20% target the realized maximum drawdown was 55-64% of capital
(2015-2017), and IBKR's 2026 overnight margins exceed 100% of a $25K account on about one day in twenty (2026 rates on
historical positions, biased upward in the early years).

### 3.4 Part B: E22-F1 and the paper runner

reports/stage_e22_prereg_F1.md (FROZEN 02:11:20, sha256 04ef33a6...; frozen file set reports/stage_e22_f1_files.sha256,
30 files; commit 2a2bdd8; registered r007-E22 at 02:12:01, test group E22, id E22-F1). forward/ (core, strategy, runner,
ledger, sources, rolls, history, evaluate, report; config_f1.json, tables_f1.json, rolls_f1.json): 142 tests on synthetic data.
The rounding method was changed from the greedy (draft 1, preserved) to simple rounding before the freeze, on the design
study (R-B7); RegReviewer judged this legitimate because the forward test never reads historical data.

### 3.5 Part B: the data-source memo (reports/stage_e22_data_source_memo.md; DataSourceReader-OpusHigh, 14 searches)

| Source | Cost per year for this use | Settlement price | Micros covered | Main caveat |
|---|---|---|---|---|
| Databento GLBX.MDP3 usage-based, `statistics` schema | unknown until a fresh quote (none obtained tonight) | yes (final/preliminary flag) | all CME futures since 2010 | quote needed; same-day availability of the final settlement not stated |
| Databento Standard plan | USD 2,388 | yes | same | live-licence conditions |
| IBKR paper (shares live subscriptions) | USD 74.40 (waived with USD 20/month commission per exchange) or USD 120 bundle | not established | all 21 have margin rows | API settlement field unverified; funded account needed |
| Norgate Data Futures | USD 270 | yes (close = official settlement) | 3 of 21 (all 12 full-size parents) | most micros absent; Windows updater |
| CSI Data (Unfair Advantage) | USD 458 in year 1 | partly (settlement semantics unverified) | 21 of 21 | one device, personal use |
| Massive (Polygon) futures | USD 0-348 | yes (`settlement_price`) | per-symbol unverified | short history on low tiers |
| Barchart, Nasdaq Data Link, AMP, NinjaTrader, CME DataMine | unpublished or unverified | various | - | see the memo; CME's site never fetched |

`ohlcv-1d` is not a settlement series (daily bars built from trades on UTC dates); the settlement lives in the
`statistics` schema.

## 4. Delegation record

| Agent (description) | Worker file | Model | Effort | Objective | Status | Deviations |
|---|---|---|---|---|---|---|
| HarnessGapAudit-OpusXHigh | workflow agent | opus | xhigh | v12 audit for one run per cluster | done | added (the prompt's plan had no audit; needed to scope v13) |
| TierAFactsK5K3-SonnetMed | workflow agent | sonnet | medium | extraction: K5, K3 trials and open issues | done | added |
| TierAFactsK6K8-SonnetMed | workflow agent | sonnet | medium | extraction: K6, K8 | done | added |
| DecisionsScan-SonnetMed | workflow agent | sonnet | medium | rulings bearing on Part A | done | added |
| CarverReader-OpusHigh | worker-high | opus | high | Carver's constants and the Nov 2021 greedy, quoted | done | added (research on opus) |
| DataSourceReader-OpusHigh | worker-high | opus | high | data-source memo, IBKR margins | done | added |
| MicroBookCoder-OpusXHigh | worker-xhigh | opus | xhigh | rule core, study, tables, strategy wiring | done (two follow-ups) | as planned |
| ForwardRunnerCoder-OpusXHigh | worker-xhigh | opus | xhigh | paper runner, ledger, rolls, evaluate | done | added (split from the coder) |
| HarnessBuilder-OpusXHigh | worker-xhigh | opus | xhigh | harness v13 (N1-N5, R1-R3) and review fixes | done | added (the guardrail's v13 path) |
| HarnessReviewer-FableXHigh | worker-xhigh | fable | xhigh | independent review of v13; recheck | done | added (guardrail: Fable-reviewed) |
| RegReviewer-FableXHigh | worker-xhigh | fable | xhigh | E22-F1 review; recheck | done | as planned |
| F1FixApplier-SonnetMed | worker-medium | sonnet | medium | pin test, status strings | done | added |
| ListReviewer-FableXHigh | worker-xhigh | fable | xhigh | the four lists before any read; recheck | done | as planned |
| VerdictVerifier-K5/K8/K3/K6-FableXHigh | worker-xhigh | fable | xhigh | recompute every verdict figure, one cluster each | done; no DISCREPANCY in any cluster | one per cluster (planned as one), started as each verdict landed |

## 5. Verification (each Fable finding, the ruling and the fix)

**HarnessReviewer-FableXHigh** (reports/stage_e22_harness_review.md): 0 BLOCKING, 2 SHOULD FIX, 14 NOTE. SF-1 (the marker
path did not check the out-dir for stale records) and SF-2 (`--list` sealed into the marker after checking only cluster and
harness): fixed in code with tests. N-2 (declaration mode 0444), N-3 (descriptive Holm at K = 9), N-4, N-11, N-12: fixed.
N-8 (MES closure prints visible to the member) kept as the declared keep-and-flag reading; N-9 (h6 test) recorded as an
expected failure; others no change. Recheck: 7/7 RESOLVED, 0 new blocking; residual R-1 (the list guard does not compare the
freeze sha or vehicles) covered by reports/stage_e22_briefs/prerun_check.py before each run (ALL PASS for all four) and by
ListReviewer.

**RegReviewer-FableXHigh** (reports/stage_e22_reg_review.md): 2 BLOCKING, 8 SHOULD FIX, 10 NOTE, all accepted. B1 (the
runner's tables_f1.json was not named or hashed): named and hashed, with a pin test. B2 (an ambiguous start date and a
post-hoc `--clock-start`): start = the first ledger record; evaluate/report run without `--clock-start`. S1 (warm-up rule),
S2 (pre-clock roll correction; stuck roll -> abandoned), S3 (back-fill), S4 (power 0.13/0.22/0.53), S5-S8: fixed in the
text. Recheck: 19/20 resolved, N2 by agreement; NEW-1 (the abandonment trigger named the wrong flag) and NEW-2 fixed. R-B7
judged legitimate.

**ListReviewer-FableXHigh** (reports/stage_e22_list_review.md): 0 BLOCKING, 5 SHOULD FIX, 7 NOTE. F1 (start-rule files not
hashed: build_list.py read the wrong provenance key): fixed, lists rebuilt. F2 (limitcont LE's undefined power): ruling
R-E22-A16 before the read. F3 (wkndbtc labelled from two readings): consistent labelling, inconclusive by design only, a
reason-only not-run declaration; the strict reading recorded as an open choice. F4/F5 (the ledger line and the inputs
untracked): carried in the list commit ccd7fa7. N-1 (by-design trials always not run): applied. Recheck: 0 blocking, 1,743
field checks pass, K8 dry run rc 0.

**VerdictVerifiers** (reports/stage_e22_verify_k5.md, _k8.md, _k3.md, _k6.md):
| Cluster | Items (0-6) | Main evidence | Notes | Result |
|---|---|---|---|---|
| K5 | 1-6 VERIFIED; 0 WITH NOTES | own bootstrap and DSR/t/PBO to 1e-9; fomc series rebuilt from 34 trips with MGC's $1.92 commission and $1.00 tick (not GC's) | pmfix (excluded) executed by `--all`, present and not used; the coverage-excluded MHG trials classed inconclusive and blocking is the required reading of NULL_CRITERIA_E 1, 6 and the frozen code | no DISCREPANCY |
| K8 | 1-3, 5 VERIFIED; 0, 4, 6 WITH NOTES | 126 checks, 0 FAIL; HEOD 231/231 trips and 944/944 days exact with MGC's costs on GC bars; MES s_x 2020-02-03 | flight window starts 2020-02-04 (S_X date is a leg roll blackout); fewest-trips tie 231/231; PBO mixes MGC and 6C tick units by L-E5-3 | no DISCREPANCY |
| K3 | 1-3, 5 VERIFIED; 0, 4, 6 WITH NOTES | 25 run trials within 1e-9; ldnrev 6E/6J/6S rebuilt exactly; all 20,611 trips match the frozen cost table | no ldnrev trip on the 14 kept FX dates (cp3, ecbfix and one cp2 6J trip were force-flattened at 11:30 on them); the classification of coverage-excluded run trials as blocking follows NULL_CRITERIA_E 6 literally (decision 3) | no DISCREPANCY |
| K6 | 0-2, 4-6 VERIFIED; 3 WITH NOTES | all 27 trials bit-identical; limitcont HE 10 trips rebuilt exactly (series to 1e-14) | DSR differs from an exact inverse normal by 1.9e-8 relative (the program's Acklam approximation); PBO floor blocks drop 6 trailing dates (array_split sensitivity 0.586, also fails) | no DISCREPANCY |

No verdict figure was marked unverified; no second run was made.

## 6. Open choices (every decision the lead made on its own, with the reason)

**Window (user-approved, not the lead's).** The user paused the stage at 07:57 PDT and approved a new window (planner
message 2026-10-16 18:27 PDT): no confirmation read after 02:00 PDT on 2026-10-17, the return by 03:00 PDT; this replaced the
prompt's 06:30/07:30 times and nothing else. Logged here as a user-approved window change. The stage itself stopped at 02:43
PDT on a usage limit with no confirmation read started; after the laptop restart every earlier worker was treated as gone and
the disk state re-verified (section 2).

**Part A (reports/stage_e22_briefs/partA_rulings.md, written and hashed into the lists before any read):**
1. R-E22-A1: each cluster's single run covers every runnable frozen trial, Tier A and Tier B (E.5's K4 precedent), so V14 (c)
   and L-E5-3 have their series; OC-H-excluded trials listed, not run, not covered. `--all` still executes them (pmfix MGC,
   K3's three coverage exclusions); their records are present and not used (VerdictVerifier-K5 note).
2. R-E22-A2: K6 confirmed despite V18 ("not planned"), since V39 and the prompt name K6-limitcont-01.
3. R-E22-A3: owned data only (step 2 stores of E.5 and E.12; MES's Stage D store); MNQ step 2 and BTC not owned.
4. R-E22-A4: GC bars as MGC's price path for every MGC-vehicle trial (K5's six, K8's flight H30 and HEOD), MGC's costs, tick
   value and q_c: MGC's own window is empty, so D4's power check fails; U8 met by V39's delegation; declared before any read
   (reports/stage_e22_price_paths.json, pinned in v13).
5. R-E22-A5: NQ bars as MNQ's price path (MNQ's history not owned, so its owned supply is 0). Declared, but not exercised: the
   only MNQ trial (wkndbtc) is not run. ListReviewer preferred the strict reading (no NQ path; wkndbtc "untestable on owned
   data, missing MNQ"); verdict-neutral either way. Left in v13's declaration (see decision 6).
6. R-E22-A6 (revised after the list review): wkndbtc "inconclusive by design" only (MBT window 34 days < n_b 43; BTC not
   owned, not bought), declared not run by a reason-only entry; an earlier "untestable (missing MBT)" declaration was withdrawn
   before any commit.
7. R-E22-A7, A8: MES from its Stage D store at S = 2020-02-03; D4's start rule for every other root, run on its owned store
   (GC and NQ on their own research volumes).
8. R-E22-A9: by-design trials are never run (applied in the list builder after list-review N-1).
9. R-E22-A10: Holm K = 5 (K3, K4, K5, K6, K8), not V14 (b)'s 9, since every cluster and the ML route have now been screened;
   the K = 9 Holm reported descriptively; family-wise error with K4 at 0.0056 is at most 0.0456.
10. R-E22-A11: N = 533 for DSR (532 + E22-F1, registered at 02:12 before the lists at 02:20), the conservative value.
11. R-E22-A12: operative eps_X (min of translated and funnel), as E.5.
12. R-E22-A13: a Tier A trial with no record enters Holm at p = 1 with the screened family size.
13. R-E22-A14: K8's DSR variance over Tier A when two series exist, else every run trial (here the three run trials).
14. R-E22-A15: open issues carried as frozen (K3's 14 FX dates, July 3 dates, K6 limit tables and D9.7 proxy, wkndbtc regime);
    tick history over the confirmation window taken from the step 2 bar reports (off_tick_prices 0).
15. R-E22-A16: K6-limitcont-01 LE (power undefined, 0 research trips) run and covered; a zero-trip confirmation outcome reads
    inconclusive and costs K6 its statement; accepted before the read (and it happened).

**Harness and process:**
16. Harness v13 built rather than an E.5-style stop: the prompt's guardrail anticipated it; Fable-reviewed and committed
    (e40ca85) before any read. Review SHOULD FIX items fixed in code (not procedure); residual R-1 covered by a pre-run script.
17. A speculative working-tree manifest (W1, 8cd39432) was used to build K8's start rule and a first power run during the
    review; the power was re-run under committed v13 (identical); K8's start-rule file was kept (W1 -> v13 changed only the
    runner and verdict modules and tests; list-review N-2).
18. K3 and K6 start rules built under v12 before any harness edit (the loader does not check a file's harness).
19. The four earlier freezes broken by v13 (E.16, E.18, E.20 H6, E.20 search) and the h6 test were left as they are
    (frozen records of completed stages).
20. One Fable verifier per cluster, started as each verdict landed (the prompt planned one VerdictVerifier).
21. Confirmation order K5, K8, K3, K6, one at a time, detached with setsid so a dropped shell could not consume a marker.
22. The end suite ran at 02:20 on the final code and is the one quoted; a second run after the confirmations (18:59:54) was
    stopped at 81% (19:14:51) because free memory fell to 1.5 GB (stability over speed); no tested code changed after 2a2bdd8.

**Part B (reports/stage_e22_briefs/lead_spec_B.md S1-S8):**
23. Universe: 12 micros on E.21's owned paths; SIL (no owned path), MES (no 2010-2024 path) and MHG, M6A, M6B, MCD, MJY, MZW,
    MZM (their only owned paths are Part A confirmation-window data E.21 never read) not modelled.
24. Yield micros in the study: a proxy from ZT/ZN/ZB with declared modified durations 1.9/6.5/15.0 (UNSOURCED); in the
    forward test they trade their own yield-quoted contracts.
25. Sizing vol as price-difference vol (sigma(dP)/P), so the yield instruments are well defined.
26. B-R1: Carver's production forecast scalars (5.95/4.10/2.79/1.91), not the book set (shown as a sensitivity).
27. B-R2 to B-R5: the blended vol as the EWMAC denominator; the rounded-and-buffered baseline as "simple"; the November 2021
    post's greedy parameters unchanged (250, 0.0125, not rescaled to 20%); no end-of-sample look-ahead.
28. B-R6: the 0.5 correlation shrink in the main greedy rows (the post states shrinking without a value).
29. B-R7: E22-F1's rounding changed from the greedy (draft 1) to simple rounding after the design study, before the freeze.
30. D8 extension costs for MNG, M6E, 2YY, 10Y, 30Y, MZC, MZS, MZL (commission plus one tick; the $1.92 round-turn commission for
    yields and grains UNSOURCED); 2026 IBKR margins applied to historical positions.
31. E22-F1: frozen by a separate freeze commit (2a2bdd8, E.21's precedent) before registration; registered under test group
    "E22" with id E22-F1 because the registry refuses the "E22F1" group form the frozen text's example command used.
32. E22-F1 text decisions: start = the first ledger record; warm-up = the source's own back history (no splice); a missing
    weekday counts as 0; pre-clock roll correction allowed; stuck roll -> abandoned; abandonment reported, never restarted
    under the same ID.
33. The study's cache (daily price series) and per-book series are not committed (derived market data; size).

## 7. Decisions for the user (the lead's recommendation first)

1. **E22-F1's daily data source.** Recommend: authorize a fresh Databento quote for the GLBX.MDP3 `statistics` schema
   (official settlement, every micro, 2010 on) covering the 12 micros' warm-up history and daily updates, then approve the
   spend if it is small; the usage-based price is unpublished, so the quote decides. Fallback: CSI Data (USD 458 in year 1,
   all 21 micros; settlement semantics to confirm). Not recommended: Norgate (3 of the 12 micros), IBKR paper alone
   (settlement field unverified). The clock starts on the first ledger record after approval; before it, check
   forward/rolls_f1.json against the exchange's published roll schedule (logged; not a new registration).
2. **Size and risk of any live version.** Recommend: run E22-F1 as registered (paper, $25K notional) and do not trade the
   book live at $25K at a 20% vol target: the design study shows a 55-64% historical maximum drawdown and IBKR margin above
   the account on about 5% of days. A live book would need $50K or more, or a lower target (a new registration).
3. **Stage E's intraday clusters.** Recommend: close them. Every Tier A member of K3, K4, K5, K6 and K8 is null or untestable
   with no Holm rejection; no holdout read is warranted. Accept "no statement" for K3, K5 and K6 as final (thin-product
   coverage at confirmation, one zero-trip LE member). The frozen rule classes a run-listed trial that the confirmation-window
   coverage check excludes as blocking (VerdictVerifier-K3's note); whether such exclusions deserve a "not covered" class
   instead is a criteria question for any future program, not a reason to re-read.
4. **The four pre-E.22 freezes that no longer verify under v13** (E.16, E.18, E.20 H6, E.20 search). Recommend: accept and
   carry a note in future check scripts (they pinned v12 for completed runs); re-pinning them would rewrite frozen records.
5. **Push** the E.22 commits (e40ca85, 2a2bdd8, ccd7fa7 and the final commit); not pushed, as the prompt says.
6. **The MNQ -> NQ entry in v13's price-path declaration** applies by vehicle: if K1 (MNQ) were ever confirmed it would read
   NQ. No K1 confirmation is planned; remove or keep at the next harness change.

## 8. Session cost

### Final ETA table (actuals; PDT; the initial estimate in brackets)

| Task | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Start checks; start suite | lead | opus | xhigh | 00:47 | 01:09 | 22 min | in lead | done; 7402 passed [1 min + 20 min] |
| A0 Part A facts (workflow, 4 agents) | HarnessGapAudit-OpusXHigh; TierAFactsK5K3-, TierAFactsK6K8-, DecisionsScan-SonnetMed | opus / sonnet | xhigh / medium | 00:53 | 01:11 | 18 min | 23,719,572 + 3,488,024 + 2,400,102 + 4,805,088 | done [40 min] |
| B1 Carver sources | CarverReader-OpusHigh | opus | high | 00:59 | 01:08 | 9 min | 10,371,337 | done [35 min] |
| B2 Data-source memo, IBKR margins | DataSourceReader-OpusHigh | opus | high | 00:59 | 01:19 | 20 min | 21,314,667 | done; 14 searches [60 min] |
| B3 Rule core, study, tables, wiring | MicroBookCoder-OpusXHigh | opus | xhigh | 00:59 | 01:36 | 37 min | 31,993,960 | done; two follow-ups [3 h] |
| B4 Paper runner | ForwardRunnerCoder-OpusXHigh | opus | xhigh | 00:59 | 01:19 | 20 min | 8,799,199 | done; 88 tests [2 h] |
| A1 Rulings, K3/K6 start rules, declaration | lead | opus | xhigh | 01:03 | 01:14 | 11 min | in lead | done [20 min] |
| A2 Harness v13 and review fixes | HarnessBuilder-OpusXHigh | opus | xhigh | 01:15 | 02:07 | 33 min of work | 36,721,085 | done [65 min] |
| A2b v13 review and recheck | HarnessReviewer-FableXHigh | fable | xhigh | 01:40 | 02:10 | 19 min of work | 7,287,736 | done; 0 blocking [20 min] |
| B6 E22-F1 review and recheck | RegReviewer-FableXHigh | fable | xhigh | 01:36 | 01:55 | 16 min of work | 3,943,562 | done; 2 blocking fixed [25 min] |
| B7 Pin test, status strings | F1FixApplier-SonnetMed | sonnet | medium | 01:49 | 01:50 | 1 min | 377,319 | done |
| A3 W1 manifest, K8 start rule, power (W1) | lead | opus | xhigh | 01:40 | 01:55 | 15 min | in lead | done (power redone under v13) |
| A4/A5 v13 commit; power under v13 | lead | opus | xhigh | 02:08 | 02:20 | 12 min | in lead | done [40 + 25 min] |
| B10/B11 F1 freeze commit; registration | lead | opus | xhigh | 02:11 | 02:12 | 1 min | in lead | done; N 532 -> 533 |
| A6/A7 Lists; list review and recheck | lead; ListReviewer-FableXHigh | opus / fable | xhigh | 02:20 | 02:43 | 23 min | 4,371,839 | done; 0 blocking [60 min] |
| E1 End suite (quoted) | lead | - | - | 02:20 | 02:40 | 20 min | in lead | 1 failed (h6, expected), 7634 passed |
| PAUSE: usage limit, user pause 07:57, laptop restart | - | - | - | 02:43 | 18:26 | 15 h 43 min | - | excluded from work |
| R0/R1 Resume checks; list commit | lead | opus | xhigh | 18:26 | 18:28 | 2 min | in lead | done; ccd7fa7 |
| A8 Confirmations K5, K8, K3, K6 (once each) | lead | - | - | 18:28 | 18:59 | 31 min | in lead | done [30 min] |
| A10 Verifiers K5, K8, K3, K6 | VerdictVerifier-K5/K8/K3/K6-FableXHigh | fable | xhigh | 18:32 | 19:12 | 40 min (overlapping) | 2,471,132 + 3,098,209 + 2,424,785 + 2,435,262 | done; no discrepancy [35 min] |
| E1b End checks; suite rerun | lead | - | - | 18:59 | 19:15 | 16 min | in lead | checks done; rerun stopped at 81% (memory) |
| E2 Return, progress, STAGES, cost, commit | lead | opus | xhigh | 19:01 | ~19:20 | ~19 min | in lead | done [35 min] |
| **Stage** | | | | 00:46 | ~19:20 | **about 2 h 55 min of work (00:46-02:43 and 18:26-~19:20), excluding the 15 h 43 min pause** | **308,963,957** (lead and workers; split below) | initial estimate: about 7 h 5 min of work to ~07:55; the build and review steps ran much faster than estimated |

### Tokens per model (transcripts; reports/stage_e22_briefs/make_cost.py over the lead's .jsonl and every subagent transcript, each message's final usage; to 2026-10-17T02:15:19Z; the lead's last few messages after the count are not included)

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 4,034 | 474,495 | 23,583,225 | 1,970,771 | 26,032,525 |
| claude-opus-5-5 | 1,898 | 1,044,899 | 266,933,115 | 3,880,987 | 271,860,899 |
| claude-sonnet-5-5 | 182 | 80,926 | 10,447,508 | 541,917 | 11,070,533 |
| all | 6,114 | 1,600,320 | 300,963,848 | 6,393,675 | 308,963,957 |

Delegation share: lead 138,941,079 (45.0%), workers 170,022,878 (55.0%). By model: claude-fable-5-1 8.4%, claude-opus-5-5 88.0%, claude-sonnet-5-5 3.6%.

Per worker spawn (agent, model, effort as set, tokens): HarnessGapAudit-OpusXHigh (opus, xhigh) 23,719,572; TierAFactsK5K3-SonnetMed (sonnet, medium) 3,488,024; TierAFactsK6K8-SonnetMed (sonnet, medium) 2,400,102; DecisionsScan-SonnetMed (sonnet, medium) 4,805,088; CarverReader-OpusHigh (opus, high) 10,371,337; DataSourceReader-OpusHigh (opus, high) 21,314,667; MicroBookCoder-OpusXHigh (opus, xhigh) 31,993,960; ForwardRunnerCoder-OpusXHigh (opus, xhigh) 8,799,199; HarnessBuilder-OpusXHigh (opus, xhigh) 36,721,085; HarnessReviewer-FableXHigh (fable, xhigh) 7,287,736; RegReviewer-FableXHigh (fable, xhigh) 3,943,562; F1FixApplier-SonnetMed (sonnet, medium) 377,319; ListReviewer-FableXHigh (fable, xhigh) 4,371,839; VerdictVerifier-K5-FableXHigh (fable, xhigh) 2,471,132; VerdictVerifier-K8-FableXHigh (fable, xhigh) 3,098,209; VerdictVerifier-K3-FableXHigh (fable, xhigh) 2,424,785; VerdictVerifier-K6-FableXHigh (fable, xhigh) 2,435,262.
(The script's effort column reads workflow agents as 'high'; the efforts above are those set in the workflow script.)

These are token counts, not plan-credit percentages; the /usage meter is the user's to read.
