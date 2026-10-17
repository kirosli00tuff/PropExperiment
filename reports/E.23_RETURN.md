# Stage E.23 return: the program's intraday triggers at multi-day holds

Prompt: docs/prompts/STAGE_E.23.md. Lead: Opus 5.5 at xhigh, under ultracode. Session 09fe7046-23b3-4a60-9a36-ff97fd7dcbf1,
unattended. Date 2026-10-17; all times are PDT (America/Vancouver).

Key files:
- Prereg: reports/stage_e23_prereg.md. Freeze: reports/stage_e23_freeze.json (sha256 24dcf4dd...). Registry: r008-E23.
- Results: reports/stage_e23_runs/discovery/discovery_result.json and reports/stage_e23_runs/confirmation/confirmation_result.json.
- Markers: reports/stage_e23_RUN_ONCE_discovery.json and reports/stage_e23_RUN_ONCE_confirmation.json.
- Verification: reports/stage_e23_briefs/verify/verdict_verify.md.


## 1. Summary

**Shortlist** (4 triggers, 5 trigger-holds, K = 5):
- K2-monthend-01, long on ZF, ZN and ZB at 5 days (strong: month-end Treasury index-extension demand).
- E20H6-T1, reversal on NQ at 5 and 20 days (hedging pressure reverses; the 20-day evidence is disputed).

**Dropped**, among the other 203 inventoried triggers:
- No owned 2010-2019 data, or too short a store: MES, FX, MBT, VXN and the event calendars; TN, RTY, HE and LE.
- Weak or intraday-only mechanisms.
- Already read: the auction members are E16-H3's long leg; CP1, E16-H1 and E16-H4 are H6 on NQ.
- Always-in-market books: NG before its report, month-end at 20 days.

**Discovery**, W_ext 2011-07-27..2019-04-30, read once, base case. Alpha is over the root's E.21 T1 and T2, NW lags h.

| Trigger-hold | Net Sharpe | Raw t | Alpha t |
|---|---|---|---|
| Month-end ZF, 5 days | 0.21 | 0.62 | 0.55 |
| Month-end ZN, 5 days | 0.14 | 0.40 | 0.38 |
| Month-end ZB, 5 days | 0.02 | 0.05 | 0.10 |
| H6 NQ, 5 days | -0.50 | -1.46 | -1.61 |
| H6 NQ, 20 days | -0.37 | -1.12 | -0.71 |

- Adding the bonds' buy-and-hold return takes the month-end alpha t to 0.12, -0.34 and -0.78: the gain is the bonds' drift.
- Holm's smallest p was 0.309 against 0.01: no survivor.

**Confirmation verdicts:**
- All five NULL (each failed discovery).
- W_cf (2019-05..2024-02) was INCONCLUSIVE BY DESIGN for every row (power 0.18 < 0.2). Nothing was computed on it.
- K8-flight-01 and K1-vxnband-01 are UNCONFIRMABLE ON OWNED DATA.

**Verification:** VerdictVerifier-FableXHigh returned VERIFIED WITH NOTES (no BLOCKING); the books re-simulated exactly.

**N:** 533 -> 538.

**For the user:** close this direction (recommended); keep W_cf and holdout-2 for a stronger prior; buy no data; bound the
multi-day loader next time; E22-F1's settlement source is pending.

## 2. Guardrail evidence

Script: reports/stage_e23_briefs/checks.sh (E.22's checks plus the E.23 freeze and the markers). Every line is quoted
verbatim except the untracked (`??`) lines of `git status --short`, which are omitted: 1029
at the start and 1288 at the end (Open choice 26). The full files are
reports/stage_e23_briefs/start_checks.txt and end_checks.txt.

The five failing earlier-freeze checks are the expected harness-v13 failures:
- the E.14 C1 inputs list;
- E.16 and E.18;
- E.20 H6 and the E.20 search.

Each pinned v12 files that v13 rewrote, and none was edited. The suite's one failure, tests/test_h6_rod_run.py, has the
same cause.

### 2.1 Start checks (02:03:59-02:04:14)

```
$ date
Sat Oct 17 02:03:59 PDT 2026
$ git status --short
$ git log --oneline -3
cb07387 docs: Stage E.23 prompt (triggers at multi-day holds) and V40
7547638 Stage E.22 Tier A confirmations and micro book
ccd7fa7 E.22 confirmation lists
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
$ E.22 confirmation list and E22-F1 registration (pinned 6f2fbf38... and 04ef33a6...)
6f2fbf381c95ee57f05237102c97347c9fe3c343d99b6bc6e6f7e377b8a1a664  reports/stage_e22_confirmation_list.md
tracked, no diff vs HEAD
04ef33a6943004adcd50c542adf719c04ba362f7a7274a140a6293c168d8473b  reports/stage_e22_prereg_F1.md
tracked, no diff vs HEAD
$ E.23 freeze and registration (written during the stage)
reports/stage_e23_freeze.json not yet written
reports/stage_e23_prereg.md not yet written
```

Start suite, `uv run pytest -q -p no:cacheprovider` (detached at nice 10, 02:04:19-02:28:56; reports/stage_e23_briefs/pytest_start.out):

```
FAILED tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha
1 failed, 7634 passed, 3 skipped, 3 xfailed, 54 warnings in 1473.94s (0:24:33)
rc 1 end 02:28:56
```

### 2.2 End checks (05:21:40-05:22:01, after both reads)

```
$ date
Sat Oct 17 05:21:40 PDT 2026
$ git status --short
 M ledger/trial_registrations.jsonl
 M reports/stage_e23_STATE.md
$ git log --oneline -3
75874c4 E.23 freeze (registry ids)
25bc321 E.23 freeze
cb07387 docs: Stage E.23 prompt (triggers at multi-day holds) and V40
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
N = 538 (9 lines)
r001-C1: C1 ['C1-T1', 'C1-T2'] N 471 -> 473 at 2026-10-09T19:29:06-07:00
r002-E16: E16 ['E16-H1', 'E16-H2', 'E16-H3', 'E16-H4', 'E16-H5'] N 473 -> 478 at 2026-10-10T00:30:15-07:00
r003-C1b: C1b ['C1b-T1', 'C1b-T2'] N 478 -> 480 at 2026-10-10T12:17:48-07:00
r004-E20H6: E20H6 ['E20H6-T1', 'E20H6-T2', 'E20H6-T3'] N 480 -> 483 at 2026-10-11T15:36:20-07:00
r005-E20S: E20S ['E20S-01', 'E20S-02', 'E20S-03', 'E20S-04', 'E20S-05', 'E20S-06', 'E20S-07', 'E20S-08', 'E20S-09', 'E20S-10', 'E20S-11', 'E20S-12', 'E20S-13', 'E20S-14', 'E20S-15', 'E20S-16', 'E20S-17', 'E20S-18', 'E20S-19', 'E20S-20', 'E20S-21', 'E20S-22', 'E20S-23', 'E20S-24', 'E20S-25', 'E20S-26', 'E20S-27', 'E20S-28', 'E20S-29', 'E20S-30', 'E20S-31', 'E20S-32', 'E20S-33', 'E20S-34', 'E20S-35', 'E20S-36', 'E20S-37', 'E20S-38', 'E20S-39', 'E20S-40', 'E20S-41', 'E20S-42', 'E20S-43', 'E20S-44', 'E20S-45'] N 483 -> 528 at 2026-10-11T17:43:59-07:00
r006-E21: E21 ['E21-T1', 'E21-T2', 'E21-T3', 'E21-T4'] N 528 -> 532 at 2026-10-14T04:12:12-07:00
r007-E22: E22 ['E22-F1'] N 532 -> 533 at 2026-10-16T02:12:01-07:00
r008-E23: E23 ['E23-MEZFh5', 'E23-MEZNh5', 'E23-MEZBh5', 'E23-H6NQh5', 'E23-H6NQh20'] N 533 -> 538 at 2026-10-17T03:33:45-07:00
$ wc -l ledger/trial_registrations.jsonl; sha256sum
9
25c04088fed9b1a2bd14a79512bedc8ab9764611aa2abd95e2a29829542aa302
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
$ E.22 confirmation list and E22-F1 registration (pinned 6f2fbf38... and 04ef33a6...)
6f2fbf381c95ee57f05237102c97347c9fe3c343d99b6bc6e6f7e377b8a1a664  reports/stage_e22_confirmation_list.md
tracked, no diff vs HEAD
04ef33a6943004adcd50c542adf719c04ba362f7a7274a140a6293c168d8473b  reports/stage_e22_prereg_F1.md
tracked, no diff vs HEAD
$ E.23 freeze and registration (written during the stage)
24dcf4dd671dbada927f548b3aff7a58a89c8fa92a6d43ae498aa69cbb3df5a5  reports/stage_e23_freeze.json
tracked, no diff vs HEAD
db34eac9fd8ef141f7d472a3c72e158ef4354a4ccda41084b828672cc48c0c5c  reports/stage_e23_prereg.md
tracked, no diff vs HEAD
$ E.23 freeze: uv run python -m trigger_hold.freeze_manifest verify --sha256 24dcf4dd671dbada927f548b3aff7a58a89c8fa92a6d43ae498aa69cbb3df5a5
freeze verified: 20 inputs, 5 ids
exit 0
$ markers
-r--r--r-- 1 kiros-li kiros-li 2028 Oct 17 03:35 reports/stage_e23_RUN_ONCE_confirmation.json
-r--r--r-- 1 kiros-li kiros-li 1963 Oct 17 03:33 reports/stage_e23_RUN_ONCE_discovery.json
```

End suite (detached at nice 10, 05:22:14-05:41:25; at least 8 GB free at launch; reports/stage_e23_briefs/pytest_end.out).
The code is identical to the final commit's; the 94 new trigger_hold tests are included.

```
FAILED tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha
1 failed, 7728 passed, 3 skipped, 3 xfailed, 54 warnings in 1148.48s (0:19:08)
rc 1 end 05:41:25
```

### 2.3 Final checks before the commit (reports/stage_e23_briefs/end_checks_final.txt; its difference from the 05:21:40 run, untracked lines omitted: 1292 in the final run)

```
2c2
< Sat Oct 17 05:21:40 PDT 2026
---
> Sat Oct 17 07:29:08 PDT 2026
3a4
>  M docs/STAGES.md
4a6
>  M progress.md
```

Every other tracked line is identical to the 05:21:40 run:
- holdout all_ok with 0 unlocks, REGISTRATION.md 0 bytes;
- harness v13 dd2bcc60... OK;
- spend ledger 36,402 lines, 034a454b...;
- N = 538 (9 lines, 25c04088...);
- the E.23 freeze verified (20 inputs, 5 ids, exit 0), and both markers read-only.


### 2.4 Order of events (PDT, 2026-10-17; from file mtimes, logs, git and the STATE file)

| Time | Event |
|---|---|
| 02:03:59 | Start checks (reports/stage_e23_briefs/start_checks.txt) |
| 02:04:19-02:28:56 | Start suite, detached at nice 10 (1 failed: the known tests/test_h6_rod_run.py since v13) |
| 02:14-02:21 | Inventory and mechanism briefs, lead spec draft (no outcome read) |
| 02:17-02:29 | P1.1: 10 InventoryReader workers (workflow wf_b90fd95b-792) |
| 02:17-02:33 | P1.2: 11 MechanismReader workers (workflow wf_e33ecfd4-8a1) |
| 02:22-02:42 | BookCoder-OpusXHigh: engine, trend regressors (exact vs E.21), T3 reproduction (exact) |
| 02:24-03:08 | TriggerCoder-OpusXHigh: events extraction; W_cf validations identical |
| 02:33-02:37 | Lead: shortlist and data-use map (reports/stage_e23_briefs/shortlist.md), before any outcome read |
| 02:39 | Prereg draft (reports/stage_e23_prereg.md) |
| 02:46-02:58 | TriggerCoder's first-pass events files carried engine exit-side counters (deleted, regenerated; disclosed) |
| 03:09-03:11 | Power table, freeze 3fdd98d7... built |
| 03:11-03:30 | RegReviewer-FableXHigh and CodeReviewer-FableXHigh (APPROVE WITH FIXES each; 0 BLOCKING) |
| 03:25-03:32 | Fixes (R-01..R-04, R-06, C-01, C-04), freeze rebuilt e0d20d0f..., real preconditions dry run passed |
| 03:32:24 | Freeze commit 25bc321 |
| 03:32-03:33 | Registry refused the first id form (nothing written); ids renamed, power rerun, freeze 24dcf4dd..., dry run |
| 03:33:43 | Commit 75874c4 "E.23 freeze (registry ids)" |
| 03:33:45 | Registration r008-E23, N 533 -> 538 |
| 03:33:54-03:34:35 | Discovery read once (marker written 03:33, before any bar; compute 03:33:57-03:34:34) |
| 03:35:27-03:35:29 | Confirmation step once (marker 03:35; 0 survivors; nothing read) |
| 03:36 | VerdictVerifier-FableXHigh spawned |
| 03:38-05:21 | PAUSE: usage limit (the verifier stopped at its start; nothing written) |
| 05:21 | Resumed; verifier resumed by message |
| 05:21:40 | End checks (reports/stage_e23_briefs/end_checks.txt) |
| 05:22:14 | End suite, detached at nice 10 |
| 05:21-05:28 | VerdictVerifier file-based recomputation (recompute_file_based.json 05:28:19); spot_audit.py written 05:37 |
| 05:41:05 | Verifier ends its turn waiting on a background wait for the suite; Verdict line PENDING |
| 05:41:25 | End suite done (1 failed: the known h6 test; 7728 passed) |
| 05:41-07:21 | STALL: the verifier's wait matched its own command line (`pgrep -f`) and never fired; the lead waited idle (context compacted 06:37) |
| 07:21:27 | User resumed the session |
| 07:22 | Lead killed the stuck wait loop; verifier resumed by message |
| 07:22:25-07:22:35 | Spot audit re-simulation from the ext2010 stores (spot_audit.json) |
| 07:24:49 | Verdict set: VERIFIED WITH NOTES, 0 BLOCKING |
| 07:25-about 07:35 | Return, progress entry, STAGES line, final checks, session cost, final commit |

## 3. Results

### 3.1 Inventory (P1.1; full rows in reports/stage_e23_briefs/inventory/*.json)
208 frozen intraday trigger rows: K1 11, K2 44, K3 30, K4 12, K5 11, K6 27, K7 6, K8 4, H6 3 (E20H6-T1..T3), CDE 60
(the D.1-D.1f MES families and E16-H1, E16-H4). 34 items excluded by the readers with reasons: ML models (C1, C1b, every
K*-ml member), drafts never frozen (E.13 C1/C2 drafts, E.14 C2), H2 and H3 (already multi-day; H2 is E.21 T4), H5 and
the cluster books (combinations, not triggers), Stage C (no trading rule), non-directional D.1f statistics, members
never declared (K1-predrift, K3-mehedge 6E, K2 X-01..X-09).

Lead exclusions for data not owned on BOTH windows (P1.1), from the rows' inputs_needed:
- Every rule on a root with no W_ext store: MES (all D.1-D.1f rules), MYM/YM, 6A 6B 6C 6J 6S 6N, ZW, ZM, MHG, MBT (all K7);
  and every multi-leg rule whose signal leg has no W_ext store: K8-flight-01 H30/HEOD (MES leg), K8-oilcad-01 (6C traded),
  K8-wkndbtc-01 (MBT leg), K6-crushgap-01 (ZM leg).
- Rules whose own inputs do not exist for 2010-2019 in the repo: K1-vxnband-01 (VXN table 2019-04-30 on), K2-predrift-01
  (ISM Services dates), K6-wasdepre-01 and K6-wasdepost-01 (WASDE dates), K3-ldnrev/ldnmom/ecbfix 6E (fix clocks, E&W and
  TARGET holiday tables 2019 on), K5-pmfix-01 and K5-preauc-01 (LBMA auction tables 2019 on), K4-apipre-01 (federal
  Monday holidays, API dropped weeks), K4-eiamom-01 (NYSE_NOT_FULL), E20H6-T3 (GEX from 2011-05 only, and its terms ruling
  covers one registered test).
- Roots with W_ext stores too short to read (P2.3, see the power section of the prereg): TN (from 2016-01-11), RTY (from
  2017-07-10), HE (from 2017-07-01), LE (from 2014-12-15): every rule on them (incl. K6-limitcont-01 HE and LE).

### 3.2 Mechanism memo (P1.2; full paragraphs with verbatim quotes in reports/stage_e23_briefs/mech/M1..M11)
| Member(s) | Memo | Strength | Direction (5 / 20 days) | Lead note |
|---|---|---|---|---|
| K6-limitcont-01 HE, LE | M1 | weak | flat after t+1 (the published continuation is at t+1, before the entry) | dropped: weak; roots too short |
| K5-fomc-01 MGC | M2 | weak | continuation by analogy; a source disagrees | dropped: weak |
| K2-fomcpost-01 rates (fixed BUY) | M2 | weak | same side, not significant; disagreement | dropped: weak |
| K2-predrift-01 ZN, ZB (ISM pre-release) | M2 | none: intraday-only | - | dropped: intraday-only; no data |
| K8-flight-01 H30, HEOD MGC | M3 | moderate | reversal (opposite side) at 20 days; flat at 5 | not readable: MES leg not owned on W_ext; W_cf alone is power-gated |
| K8-oilcad-01, K8-wkndbtc-01 | M3 | none (one-step / Monday only) | - | dropped |
| E20H6-T1 NQ (and T2) | M4 | moderate | reversal at 5 (BDLM2021 1-3 days, t -3.16; BvD2019 anti-MAC(5) Sharpe 0.63 after 1999); 20 days disputed | SHORTLISTED (T1) |
| CP1 port, every root | M4 | moderate on equity (reversal at 5); weak to moderate rates and index commodities; weak FX, livestock | as left | not shortlisted: on NQ the same mechanism as H6 (redundant); weaker elsewhere |
| E16-H1 settlement-window momentum (pooled) | M4 | moderate pooled (reversal at 5) | 20 days disputed | not shortlisted: on NQ the same mechanism as H6; pooled multi-root trial |
| CP2 opening-range breakout | M5 | none: intraday-only | - | dropped |
| CP3 prior-close location | M5 | weak, reversal, one day | - | dropped |
| K1-vwap-01 | M5 | none: intraday-only | - | dropped |
| K2-aucpre-01, K2-aucpost-01 | M6 | moderate on ZT, ZF (FNR2024, fading after 2010/2014); weak ZN, TN, ZB, UB | long after the auction at 5 days; 20 days none | dropped: their 5-day post-auction long from the auction day's settlement IS the long leg of E16-H3, already read on 2010-07..2024-02 (E.17 FAIL); the two members are one bet (M6) |
| K2-monthend-01 rates | M7 | strong at 5 days for the N-1 trigger (Hartley-Schwarz 2019 Table 8, futures: 5y +7 bp, 10y +9 bp, 30y +15 bp on day N, se 1-2); N trigger weak/disputed | same side (long) at 5; 20 days only the unconditional premium | SHORTLISTED on ZF, ZN, ZB at 5 days |
| K3-mehedge-01 6J | M7 | none: intraday-only | - | dropped (no W_ext data either) |
| K3 fix members, K5-pmfix, K5-preauc | M8 | none: intraday-only (ldnrev weak, disputed) | - | dropped |
| K4-eiafade, K4-apipre | M9 | none: intraday-only | - | dropped |
| K4-eiamom-01 | M9 | weak, disputed | - | dropped |
| K4-ngpre-01 NG | M9 | moderate as a report-day calendar premium only (Prokopczuk et al., t -2.19, absent 2014-2018) | same side (short) | dropped: weekly events with 5- or 20-day holds keep the book short on almost every day: a buy-and-hold short, not a trigger test |
| K6-wasdepre, K6-wasdepost | M10 | weak | short continuation or null | dropped (no W_ext WASDE table either) |
| K6-crushgap-01 | M10 | weak (single leg) | - | dropped (ZM not owned on W_ext) |
| K4-ovr-01, K5-ovr-01 | M11 | weak, disputed | - | dropped |
| E16-H4 next-day reversal | M11 | moderate (reversal, the member's side; evidence to 3 days) | - | not shortlisted: on NQ the same bet as H6 one day later |
| K1-vxnband-01 | M11 | moderate (reversal at 5) | - | not readable: VXN not owned for 2010-2019 |
| K7 (MBT), D.1-D.1f MES rules | - | not researched | - | excluded for data (no W_ext store) |

### 3.3 Shortlist (P1.3; 4 triggers, 5 trigger-holds of at most 12 and 24)
Rule applied: a trigger is shortlisted if its stated multi-day mechanism is moderate or strong, its data exist on both
windows, its multi-day outcome has not been read before, it is not a duplicate of a shortlisted trigger's mechanism on
the same root, and its book is a trigger test: a FIXED-side book that would be in the market on almost every day is
the root's buy-and-hold, not a trigger test (amended 03:10 PDT from the power table's calendar facts: the H6 books are in
the market on 91-94% of days, but their side follows the trigger, so they remain trigger tests).

| Id (registry) | Trigger (frozen) | Root (price path, vehicle) | m | Hold | Mechanism (memo) | Expected events per year |
|---|---|---|---|---|---|---|
| E23-MEZFh5 | K2-monthend-01 ZF | ZF (ZF) | +1 (same side: long) | 5 | month-end Treasury index-extension demand (M7: HS19 Table 8, ERSV20) | 24 (N-1 and N), 12 non-overlapping |
| E23-MEZNh5 | K2-monthend-01 ZN | ZN (ZN) | +1 | 5 | same | same |
| E23-MEZBh5 | K2-monthend-01 ZB | ZB (ZB) | +1 | 5 | same | same |
| E23-H6NQh5 | E20H6-T1 | NQ (NQ bars, MNQ costs) | -1 (reversal of sign(r_ROD)) | 5 | hedging price pressure reverses; post-2000 index anti-autocorrelation (M4: BDLM2021 Table 11, BvD2019) | about 240 |
| E23-H6NQh20 | E20H6-T1 | NQ | -1 | 20 | same; 20-day evidence disputed (M4) | about 240 |

Lead choices on the shortlist (Open choices in the return): K2-monthend-01's 20-day hold is not registered: with N-1 and N
every month and a 20-trading-day hold the book is long on nearly every day (a buy-and-hold long, not a trigger test);
"two holds each" is read as the default, not an obligation to register a degenerate book. Roots for K2-monthend-01: one per
published futures tenor (HS19 Table 8: 5y ZF, 10y ZN, 30y ZB); ZT has only a cash 2y figure (+3 bp) and TN/UB have no
row (TN is also too short on W_ext). H6: T1 only (T2 is a magnitude-filtered variant of the same rule; T3 is excluded).

Cost feasibility (V31): published gross per event against the D8 round trip of the vehicle (round trips: reports and
base_rules.costs; approximate bp at typical prices): month-end day N +7 / +9 / +15 bp (ZF / ZN / ZB) against about 1 / 2
/ 3 bp; H6 reversal about 6 bp over 2 to 3 days per a 20 bp last half hour (M4, the reader's arithmetic) against MNQ's
about 0.4-0.7 bp. Each clears 1.5 x its cost. The exact round trips go in the prereg table from base_rules.costs.

### 3.4 Data-use map and declared windows (P1.4)
| Trigger | Selected on (screen, discovery) | Confirmed or tested on | Other reads | Discovery window | Confirmation window |
|---|---|---|---|---|---|
| K2-monthend-01 ZF, ZN, ZB | research window 2025-04-01..2026-06-17 (E.3 screen, FAIL, Tier B; E.4 replay) | none (K2's confirmation never ran) | its month-end feature in the ML runs E.12 Gate 0 and E.20 (2019-05..2024-02; ML, no rule read); E.21 T1/T2 read the roots' daily series 2010-07..2024-02; for ZN only, E16-H2 (E.17, 2010-07..2024-02) held ZN from the fifth-last to the last trading day's settlement, long or short by the NQ-vs-ZN month-to-date sign, so ZN's day-N return entered H2's pair P&L with a conditional sign (partial overlap: one day of the 5-day hold, signed differently; not the same book) | W_ext 2011-07-27..2019-04-30 | W_cf 2019-05-06..2024-02-29 (ZF S_X 2020-10-01 per E.12's D4 path table, if declared; else 2019-05-06): inconclusive by design (power below 0.2) |
| E20H6-T1 NQ | none (registered from the literature, V34) | E.20 once on 2020-06-01..2024-02-29 (FAIL); descriptive overlap 2019-05-06..2020-05-29 | E.20 search feature rod_ret on 2019-05..2024-02 (ML); E16-H1 (a related settlement-window rule incl. NQ) tested on 2010-07..2024-02; E.21 T1/T2/T3 read NQ's daily series 2010-07..2024-02 | W_ext 2011-07-27..2019-04-30 | W_cf 2019-05-06..2024-02-29: inconclusive by design |

Stated plainly (P1.4): E.21 read the daily series of 2010-07..2024-02 for the 17 roots, so the aggregate multi-day drift
of both windows is known. The alpha over the same root's E.21 T1 and T2 returns is the registered guard; alpha3 (adding
the root's own buy-and-hold return, descriptive) is reported beside it because the month-end book is long-only.

Residue for the program's record (RegReviewer R-08; it does not touch E.23's outcomes):
- (a) TriggerCoder's W_cf validation ran the Stage E harness once for K2-monthend-01 on ZF, ZN and ZB over 2019-05..2024-02. This is a window K2's confirmation never used. The intraday P&L was computed in memory and discarded.
- (b) From 02:46 to 02:58 PDT the first-pass validation files held that run's engine exit-side counters, including MLL liquidation counts. These are a coarse fact about K2's intraday path on W_cf, not about any multi-day forward return. Nobody opened them, and they were deleted and regenerated.

A later K2 registration should know that W_cf's intraday path was executed once by the engine, unread by any person.

Window reasoning (the full text is in the prereg): the ideal discovery window, the data each trigger was screened on, is
the research window, barred by P2.4. W_cf is at most 4.82 years and cannot reach the bar with power 0.2 in any role; W_ext
(7.76 years on these roots) can. Discovery is therefore W_ext and the declared confirmation window W_cf is inconclusive by
design, leaving every trigger's multi-day outcome on 2019-05..2024-02 uncomputed for a later registered confirmation
(the discovery run computed nothing from any bar after 2019-04-30; the shared frozen E.21 loader did hold the W_cf
store's rows in memory during the read, VerdictVerifier NOTE-2, section 5).

### 3.5 Power table (P2.3; reports/stage_e23_power.json, from events, calendars and bar existence only, before any outcome read)

| Id | Window | Book dates (first) | Events | Units | Non-overlap | In market | E[t] | power_gate | power_holm1 (K 5) | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| E23-MEZFh5 | W_ext | 1939 (2011-07-28) | 137 | 131 | 71 | 0.21 | 1.387 | 0.270 | 0.174 | read |
| E23-MEZFh5 | W_cf | 1170 (2019-06-27) | 79 | 77 | 39 | 0.20 | 1.077 | 0.178 | 0.106 | inconclusive by design |
| E23-MEZNh5 | W_ext | 1939 (2011-07-28) | 143 | 137 | 77 | 0.23 | 1.387 | 0.270 | 0.174 | read |
| E23-MEZNh5 | W_cf | 1170 (2019-06-27) | 77 | 77 | 39 | 0.20 | 1.077 | 0.178 | 0.106 | inconclusive by design |
| E23-MEZBh5 | W_ext | 1939 (2011-07-28) | 142 | 136 | 76 | 0.23 | 1.387 | 0.270 | 0.174 | read |
| E23-MEZBh5 | W_cf | 1170 (2019-06-27) | 79 | 77 | 39 | 0.20 | 1.077 | 0.178 | 0.106 | inconclusive by design |
| E23-H6NQh5 | W_ext | 1934 (2011-07-27) | 1860 | 1727 | 374 | 0.91 | 1.385 | 0.269 | 0.173 | read |
| E23-H6NQh5 | W_cf | 1204 (2019-05-07) | 1147 | 1085 | 233 | 0.93 | 1.093 | 0.182 | 0.109 | inconclusive by design |
| E23-H6NQh20 | W_ext | 1934 (2011-07-27) | 1860 | 1711 | 95 | 0.94 | 1.385 | 0.269 | 0.173 | read |
| E23-H6NQh20 | W_cf | 1204 (2019-05-07) | 1147 | 1070 | 59 | 0.95 | 1.093 | 0.182 | 0.109 | inconclusive by design |

Every W_cf row is inconclusive by design (power_gate 0.178-0.182 < 0.2 at the most lenient hurdle, t >= 2.0); every W_ext row was read (0.269-0.270; at least 71 non-overlapping events).

### 3.6 Discovery (W_ext 2011-07-27..2019-04-30, nothing computed from any later bar; read once 03:33:57-03:34:34 PDT; reports/stage_e23_runs/discovery/discovery_result.json)

Capital units: the book's daily net value as a fraction of capital at 0.40 / sigma per unit (scale-free for every statistic). Alpha: OLS on the same root's E.21 T1 and T2 base daily values, Bartlett HAC lags h; alpha3 (descriptive) adds the root's own buy-and-hold return.

| Id | Root, m, h | Units (events) | Non-overlap | In market | Case | Net Sharpe | Raw t (NW) | Alpha t_NW (plain) | p_alpha | alpha3 t_NW | R^2 | Net (gross, costs) capital units |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E23-MEZFh5 | ZF, +1, 5 | 131 (137) | 71 | 0.21 | base | 0.21 | 0.57 (0.62) | 0.55 (0.50) | 0.309 | 0.12 | 0.008 | 0.309 (0.412, 0.102) |
| | | | | | stress | 0.15 | 0.43 (0.46) | 0.39 (0.35) | 0.363 | -0.06 | 0.008 | 0.230 (0.412, 0.181) |
| E23-MEZNh5 | ZN, +1, 5 | 137 (143) | 77 | 0.23 | base | 0.14 | 0.38 (0.40) | 0.38 (0.36) | 0.360 | -0.34 | 0.012 | 0.217 (0.338, 0.121) |
| | | | | | stress | 0.07 | 0.20 (0.21) | 0.19 (0.17) | 0.431 | -0.56 | 0.011 | 0.114 (0.338, 0.225) |
| E23-MEZBh5 | ZB, +1, 5 | 136 (142) | 76 | 0.23 | base | 0.02 | 0.05 (0.05) | 0.10 (0.10) | 0.461 | -0.78 | 0.032 | 0.026 (0.118, 0.092) |
| | | | | | stress | -0.04 | -0.10 (-0.10) | -0.06 (-0.05) | 0.522 | -0.95 | 0.032 | -0.059 (0.118, 0.177) |
| E23-H6NQh5 | NQ, -1, 5 | 1729 (1860) | 373 | 0.91 | base | -0.50 | -1.39 (-1.46) | -1.61 (-1.63) | 0.949 | -1.63 | 0.013 | -1.520 (-1.291, 0.228) |
| | | | | | stress | -0.54 | -1.48 (-1.55) | -1.70 (-1.72) | 0.957 | -1.72 | 0.013 | -1.616 (-1.291, 0.324) |
| E23-H6NQh20 | NQ, -1, 20 | 1713 (1860) | 95 | 0.94 | base | -0.37 | -1.03 (-1.12) | -0.71 (-0.75) | 0.772 | -0.63 | 0.041 | -1.134 (-1.006, 0.128) |
| | | | | | stress | -0.39 | -1.08 (-1.17) | -0.76 (-0.80) | 0.787 | -0.68 | 0.041 | -1.189 (-1.006, 0.182) |

Screen: K = 5, Holm one-sided 0.05; eligible []; survivors [].
Checks: E23-MEZFh5: Holm False, t>=2 False, Sharpe>=0.3 False; E23-MEZNh5: Holm False, t>=2 False, Sharpe>=0.3 False; E23-MEZBh5: Holm False, t>=2 False, Sharpe>=0.3 False; E23-H6NQh5: Holm False, t>=2 False, Sharpe>=0.3 False; E23-H6NQh20: Holm False, t>=2 False, Sharpe>=0.3 False
DSR at N 538 (variance over 5 discovery Sharpes): E23-MEZFh5 0.0332, E23-MEZNh5 0.0211, E23-MEZBh5 0.0089, E23-H6NQh5 0.0001, E23-H6NQh20 0.0003
CSCV PBO (8 blocks of 242 days, 70 splits, 1940 aligned dates 2011-07-27..2019-04-30): 0.429

Per year, base net Sharpe (n):
- E23-MEZFh5: 2011 2.82, 2012 0.14, 2013 -0.29, 2014 2.00, 2015 -0.10, 2016 1.20, 2017 -0.41, 2018 -1.40, 2019 -1.17
- E23-MEZNh5: 2011 2.39, 2012 -0.03, 2013 -0.67, 2014 2.02, 2015 0.11, 2016 0.81, 2017 0.56, 2018 -1.72, 2019 -0.96
- E23-MEZBh5: 2011 2.55, 2012 -0.48, 2013 -0.85, 2014 1.51, 2015 0.01, 2016 0.56, 2017 0.77, 2018 -1.96, 2019 -0.66
- E23-H6NQh5: 2011 0.23, 2012 0.20, 2013 0.47, 2014 -0.79, 2015 -1.02, 2016 -0.07, 2017 -0.43, 2018 -1.46, 2019 -1.65
- E23-H6NQh20: 2011 -0.97, 2012 -0.21, 2013 -0.08, 2014 0.36, 2015 -0.72, 2016 -0.85, 2017 -1.64, 2018 1.27, 2019 -4.00

Reading: the month-end books earned a small raw gain (ZF net Sharpe 0.21, ZN 0.14, ZB 0.02) with alpha t 0.55, 0.38 and 0.10 over trend; once the bonds' own buy-and-hold return is added (alpha3) the alpha is about zero or negative (t 0.12, -0.34, -0.78): the gain is the long drift of 2011-2019, not the month-end trigger. Costs took 25%, 36% and 78% of gross. The H6 reversal books lost (net Sharpe -0.50 at 5 days, alpha t -1.61; -0.37 at 20 days, alpha t -0.71); the 5-day book's losses came in 2014-2019 (2011-2013 small positive), and the 20-day book was negative in 7 of 9 calendar years. No trigger-hold passed any of the three discovery checks; Holm rejects none (smallest p_alpha 0.309).

### 3.7 Confirmation (W_cf; the step ran once at 03:35:27-03:35:29 PDT; reports/stage_e23_runs/confirmation/confirmation_result.json)

Zero survivors, so nothing was read: S = 0, no trigger-hold, no W_cf series. Had there been survivors, every one would have been INCONCLUSIVE BY DESIGN (power_gate 0.178-0.182 < 0.2).

| Id | Discovery | Confirmation verdict |
|---|---|---|
| E23-MEZFh5 | not a survivor (alpha t 0.55, Sharpe 0.21) | NULL (failed discovery; W_cf inconclusive by design, not read) |
| E23-MEZNh5 | not a survivor (0.38, 0.14) | NULL (same) |
| E23-MEZBh5 | not a survivor (0.10, 0.02) | NULL (same) |
| E23-H6NQh5 | not a survivor (-1.61, -0.50) | NULL (same) |
| E23-H6NQh20 | not a survivor (-0.71, -0.37) | NULL (same) |
| Inventory triggers not registered | - | dropped (mechanism weak or intraday-only, duplicate or spent) or UNCONFIRMABLE ON OWNED DATA / inconclusive by design for data and window length (section 3.1-3.3) |

## 4. Delegation record

The lead was Opus 5.5 at xhigh, under ultracode. It kept the reserved work for itself:
- the decomposition and every brief, and the lead spec (lead_spec.md);
- the shortlist and data-use map (P1.3-P1.4), and the prereg text and power reasoning;
- the rulings on both reviews, the registration, the two run-once reads, the discovery screen judgment, and this synthesis.

Every number entering a verdict was rechecked by a Fable worker that did not produce it. Times are PDT, taken from each agent's first and last transcript message; tokens per spawn are in section 8.

| Spawn (name) | Agent file | Model | Effort | Parallel or serial | Start-end (PDT) | Objective | Output | Status, check |
|---|---|---|---|---|---|---|---|---|
| InventoryReaderK1 .. K8, H6, CDE-OpusHigh (10) | workflow agent (e23-p1-inventory, wf_b90fd95b-792) | opus | high | all 10 at once | 02:16-02:28 | P1.1: one cluster's frozen intraday triggers, with inputs, windows read and data needs | reports/stage_e23_briefs/inventory/{K1..K8,H6,CDE}.json, .md | 10/10 done. The lead checked row counts (208 rows, 34 excluded with reasons) and compiled inventory_compact.txt |
| MechanismReaderM1 .. M11-OpusHigh (11) | workflow agent (e23-p1-mechanisms, wf_e33ecfd4-8a1) | opus | high | all 11 at once, one shared brief, at most 60 searches each, deadline 03:45 | 02:16-02:32 | P1.2: the stated multi-day mechanism per family, with strength and direction at 5 and 20 days and verbatim quotes | reports/stage_e23_briefs/mech/M1..M11.md, raw pages in mech_pages/ | 11/11 done by 02:33. The lead judged strength and direction itself (shortlist.md); RegReviewer re-read the memos the shortlist cites |
| BookCoder-OpusXHigh | worker-xhigh | opus | xhigh | parallel with TriggerCoder | 02:21-02:42 | The unit-book engine, trend regressors, statistics, power, config, run-once runner, freeze manifest and tests | trigger_hold/{types,constants,units,book,stats,power,trend,config,evaluate,run,freeze_manifest}.py; tests; bookcoder_report.md | Done. Per-root trend sums equal E.21's (max diff 0.0); T3 reproduced exactly; reviewed by CodeReviewer; recomputed by VerdictVerifier |
| TriggerCoder-OpusXHigh | worker-xhigh | opus | xhigh | parallel with BookCoder | 02:22-03:08 | Extract each shortlisted frozen trigger's decision events (d0, tau, side) on both windows from the frozen member code, without outcomes | trigger_hold/events*.py; reports/stage_e23_events/*.json (8 files) and validation/; triggercoder_report.md | Done. W_cf validations 0 differences against the harness. Exit-side counters were on disk 02:46-02:58, then scrubbed and disclosed (R-08, C-09) |
| RegReviewer-FableXHigh | worker-xhigh | fable | xhigh | parallel with CodeReviewer | 03:10-03:24 | Adversarial review of the design and registration before any read | reports/stage_e23_briefs/reg_review.md | APPROVE WITH FIXES, 0 BLOCKING (R-01..R-09; section 5) |
| CodeReviewer-FableXHigh | worker-xhigh | fable | xhigh | parallel with RegReviewer | 03:11-03:29 | Line-by-line review of trigger_hold/ against the spec before any read | reports/stage_e23_briefs/code_review.md | APPROVE WITH FIXES, 0 BLOCKING (C-01..C-09; section 5) |
| VerdictVerifier-FableXHigh | worker-xhigh | fable | xhigh | serial, after the confirmation step | 03:35-03:36; 05:21-05:41; 07:22-07:25 | Recompute every verdict number from the written files with its own code; spot-audit the books from the bar stores | reports/stage_e23_briefs/verify/verdict_verify.md, recompute_file_based.json, spot_audit.json, tables.md | Done: VERIFIED WITH NOTES, 0 BLOCKING, 7 NOTEs (section 5.3). The usage limit cut it at its start; it stalled 05:41-07:21 on a wait that matched itself, which the lead killed at 07:22 |

Messages the lead sent to running workers (SendMessage):
- To TriggerCoder: inventory facts (02:29) and the final shortlist (02:35).
- To BookCoder: the shortlist and two spec additions (02:35).
- To VerdictVerifier: resume after the usage limit (05:21), and run the spot audit now (07:22).

Deviations:
- No opening estimate table was printed in chat before the first spawn, against the CLAUDE.md rule. The plan ran against the prompt's clock instead: outcome reads by 10:30, return by 11:30.
- The usage limit (03:38-05:21) cut the verifier at its start.
- From 05:41 to 07:21 the session stalled. The verifier's wait for the end suite matched its own command line in `pgrep -f`, so it never fired, and the lead waited on the verifier instead of checking the wait. Section 8 shows both gaps as their own rows.
- Workers spawned no further workers.
- At most 2 heavy jobs ran at once: the start suite with the coders' tests, the discovery read alone, and the end suite alone.

## 5. Verification (each Fable finding, the ruling and the fix)

Three Fable xhigh workers checked this stage. None of them produced any of the work it checked.

- **RegReviewer** (design and registration) and **CodeReviewer** (trigger_hold/ line by line) worked before any read, on freeze 3fdd98d7... . Both returned APPROVE WITH FIXES with 0 BLOCKING.
- Every fix went into the rebuilt freeze e0d20d0f... . After the registry id rename it became 24dcf4dd..., which is the freeze the reads ran on (rulings: reports/stage_e23_briefs/review_rulings.md).
- **VerdictVerifier** worked after both reads. It used its own code and imported no project module. Its verdict was **VERIFIED WITH NOTES, no BLOCKING** (reports/stage_e23_briefs/verify/verdict_verify.md, set 07:24 PDT).

### 5.1 Registration review (reports/stage_e23_briefs/reg_review.md)
| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| R-01 the prereg's future confirmation window used the research window, which SELECTED K2-monthend-01 | SHOULD FIX | accepted | prereg section 4. K2: a later confirmation is W_cf + holdout-2 (about 5.8 y, power about 0.21). H6: W_cf + holdout-2 + the research window (about 7.0 y, 0.25) |
| R-02 per-root regressors start 2011-07-29; 1-2 book dates had no value, and the frozen text did not say how they are handled | SHOULD FIX | accepted | lead_spec section 1 and prereg section 3: an absent regressor value is zero (E.21's zero-when-flat). The code already did this |
| R-03 two definitions of the power gate | SHOULD FIX | accepted | prereg section 3: the confirmation gate uses b = max(2.0, z(1 - 0.05/S)); every W_cf row fails it at 2.0 already |
| R-04 E.12's ML-panel S_X for ZF | NOTE | accepted | lead_spec section R wording (a panel start, not this trigger's S_X) |
| R-05 the lenient power gate (t >= 2.0; at the Holm step-1 hurdle W_ext power is 0.17) | NOTE | Open choice 3 | none |
| R-06 the H6 20-day direction is not fixed by the mechanism | NOTE | Open choice 11 | prereg section 1 sentence |
| R-07 the H6 cost margin is thin at beta 0.1 (multiple 1.3-2.9) | NOTE | recorded | none |
| R-08 exit-side counters on disk 02:46-02:58 | NOTE | no leak relevant to multi-day outcomes; residue recorded in section 3.4 | none |
| R-09 p_alpha is stricter than the prompt (max of plain and NW p) | NOTE | kept (conservative, pre-registered) | none |

### 5.2 Code review (reports/stage_e23_briefs/code_review.md)
| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| C-01 the test mode with `--input-paths '{}'` reached the real stores without the real marker | SHOULD FIX | accepted | `preconditions` refuses the test mode with the real run manifest; test added (tests/test_trigger_hold_run.py::test_the_test_mode_refuses_the_real_run_manifest) |
| C-02 window membership is tested on d0, not d_e | NOTE | recorded | none. d_e = d0 for every unit (verified on all 3,846), so no number changes |
| C-03 a PASS is impossible on this freeze (every W_cf row gated) | NOTE | recorded | none. The prereg said so before the discovery read (section 4 power table); Open choice 3 |
| C-04 the power table's events and config hashes were not cross-checked | NOTE | adopted | `preconditions` compares them with the frozen files outside the test mode |
| C-05 regressors are projected on the book's dates (a few roll dates per root) | NOTE | recorded | none. This cannot create alpha |
| C-06 exit eligibility uses calendar and bar existence at d_x | NOTE | recorded | none. It is not a price condition (lead ruling R1, as E.21 T3) |
| C-07 the member code is pinned indirectly through the events files' recorded hashes | NOTE | recorded | none |
| C-08 stress rounding is conservative by at most 1 cent per side | NOTE | recorded | none |
| C-09 the TriggerCoder counters incident | NOTE | as R-08 | none |
| (lead) the registry refused ids with two hyphens | n/a | ids renamed (E23-MEZFh5 etc.), power rerun with identical rows, freeze rebuilt 24dcf4dd..., dry run passed | none |

### 5.3 Verdict verification (reports/stage_e23_briefs/verify/verdict_verify.md, tables.md, recompute_file_based.json, spot_audit.json)

**File-based recomputation: 343 rows compared, 339 within 1e-9 relative, 4 DSR rows at 2-3e-9.** It covered:
- n, mean, sd, net Sharpe, raw t, NW t, and the OLS alpha on v_T1 and v_T2 with its Bartlett HAC t, plain t, p_alpha, R^2, betas and correlations, for all five trigger-holds in both cases;
- alpha3 and the in-market fraction;
- Holm (nothing rejected; smallest p_alpha 0.3095 against 0.01) and the survivor rule (none: largest alpha t_NW 0.552, largest Sharpe 0.207);
- DSR at N 538 (all below 0.001) and CSCV PBO 0.428571 (30/70);
- the W_cf gate (below 0.2 at every S from 1 to 4), N 533 -> 538, the freeze and registry hashes (108 frozen files match), and the marker order (each marker written before its computation).

**Spot audit** (re-simulation from the ext2010 stores, 07:22:25-07:22:35 PDT, nice 10, 2010-07-01..2019-04-30 only):
- Every daily base and stress series value matched (max |diff| 0.0 on 9,668 dates). So did unit counts by reason, fills, roll pairs, gross, costs, net and alpha3.
- Each unit enters at the first mark after its decision (d_e = d0 for all 3,846 units) and exits h marks later.
- Size is 0.40/(sigma x notional), with sigma taken strictly before entry.
- Costs per side are D8 base; stress = commission + 2 x slippage. Round trips are $10.14 / $18.26 / $34.04 / $2.10, equal to the prereg's.
- The entry day carries only the fill cost: no trigger-day intraday P&L.

| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| NOTE-1 four DSR values differ at 2-3e-9 relative (the run's Acklam normal quantile) | NOTE | accepted | none (descriptive; every DSR < 0.001) |
| NOTE-2 the frozen E.21 loader (base_rules/context.py -> store.load_product) concatenates both eras, so the step2 store's W_cf rows (2019-05-06..2024-02-29) were in memory during the discovery read. Nothing was computed from them; only the boundary-splice contract comparison and the limit-lock rule construction touch that frame, and neither yields a value in any statistic | NOTE | accepted. The return says "computed nothing from any bar dated after 2019-04-30" (sections 3.4, 3.6, Open choice 4), not "read nothing". The freeze is not changed after the reads | for a later stage: bound the loader by ctx.last before any further discovery on W_ext (decision 5) |
| NOTE-3 the program's CSCV helper drops the last 4 of 1,940 dates (n // 8 blocks); equal blocks give PBO 0.4857 | NOTE | recorded; the program's helper is kept | none (descriptive; both < 0.5) |
| NOTE-4 the calendar-only power table differs from the realized books by up to 6 dates and 2 units | NOTE | recorded | none (realized power 0.2685-0.2694; no gate flag changes) |
| NOTE-5 the discovery output has no per-unit or per-fill records; the audit had to re-simulate | NOTE | accepted for later stages | none now (run-once outputs are not rewritten); later books write unit and fill files, as E.21 did |
| NOTE-6 the prereg says K2 decides "at 07:20 CT"; the events carry 07:21 CT (the 07:20 bar's close) | NOTE | recorded; the frozen prereg is not edited | none (no unit changes) |
| NOTE-7 registry line r008 was in the working copy, not committed | NOTE | accepted | committed in the final commit with the stage's results |

## 6. Open choices (every decision the lead made on its own, with the reason)

1. **A trigger is one frozen member trial** (a member on one root, or one frozen rule test such as E20H6-T1), as the
   program counted trials; the trend regression is then the same root's T1 and T2.
2. **Power convention**: true net Sharpe 0.5 on the book's daily series, zeros on flat days, E[t] = 0.5 x sqrt(years): the
   program's convention (E.21 prereg section 3, E.22 F1). Under it power depends on window length, not on event count.
3. **Power gate at the per-test hurdle alpha t >= 2.0** (the lenient reading of "the power to reach the bar"; R-05).
   Holm's step-1 power at K = 5 (0.17 on W_ext) is reported beside it. Under the strict reading every trigger-hold would be
   inconclusive by design on both windows and nothing would have been read. The discovery read therefore spent W_ext's
   multi-day outcome for these five trigger-holds in a read that could not produce a PASS (every confirmation row was
   gated before the read).
4. **Discovery on W_ext (2011-07-27..2019-04-30), confirmation declared on W_cf (2019-05-06..2024-02-29) and gated.** The
   prompt's ideal discovery window (the data each trigger was screened on) is the research window, which P2.4 bars. W_cf
   (at most 4.82 years) cannot reach power 0.2 in any role; W_ext (7.7 years on the long roots) can. The reverse order
   would have read nothing. This order keeps every trigger's multi-day outcome on 2019-05..2024-02 uncomputed for a
   later registered confirmation (the frozen E.21 loader held the W_cf rows in memory during discovery; nothing was
   computed from them: NOTE-2).
5. **W_ext starts at 2011-07-27**, the first date of the E.21 T1/T2 series, so both regressors are defined; a book's
   series starts at its first unit (amendment 02:36); a regressor value absent on a book date (first per-root values
   2011-07-29) is zero, E.21's own convention (R-02).
6. **Shortlist rule**: moderate or strong stated mechanism; data owned on both windows; multi-day outcome never read; not
   a duplicate of a shortlisted mechanism on the same root; a fixed-side book that would be in the market on almost every
   day is a buy-and-hold, not a trigger test (refined at 03:10 from the power table's calendar facts; H6's books, in the
   market 91-94% of days with a side that follows the trigger, stay trigger tests).
7. **K2-aucpre-01 and K2-aucpost-01 dropped**: their 5-day post-auction long from the auction day's settlement is the long
   leg of E16-H3, already read on 2010-07..2024-02 (E.17, FAIL); the two members are one bet (M6).
8. **K4-ngpre-01 dropped and K2-monthend-01's 20-day hold not registered**: weekly events (ngpre) or N-1 and N each month
   with a 20-day hold keep a fixed-side book in the market on almost every day. "Two holds each" read as the default.
9. **K2-monthend-01 on ZF, ZN and ZB**: one root per futures tenor in Hartley-Schwarz Table 8 (5y, 10y, 30y); ZT has only a
   cash 2y figure; TN and UB have no row (TN is also too short on W_ext).
10. **E20H6-T1 only** (T2 is a magnitude-filtered variant; T3 excluded: GEX from 2011-05 and terms cleared for one test),
    and H6 rather than CP1, E16-H1 or E16-H4 on NQ: the same late-day pressure and reversal mechanism on the same root.
11. **Directions**: K2-monthend-01 m = +1 (the member's long side; M7); E20H6-T1 m = -1 (reversal; M4). The 20-day H6 hold
    keeps the mechanism's direction although the 20-day evidence is disputed (R-06).
12. **FOMC triggers dropped as weak** (M2: K5-fomc-01 and K2-fomcpost-01 weak with disagreement; K2-predrift-01
    intraday-only) although the prompt names post-FOMC drift; **K8-flight-01 (moderate) and K1-vxnband-01 (moderate)
    unreadable** for data (the MES leg and VXN are not owned for 2010-2019; W_cf alone is gated).
13. **TN, RTY, HE and LE excluded** for short W_ext stores (power below 0.2 on both windows), which removed K6-limitcont-01.
14. **Entry rule**: the first settlement mark strictly after the trigger's decision time (the same day for both triggers);
    **position**: clip(sum of units, -1, +1), changing only when that value changes, sized 0.40 / (sigma x notional) at the
    change date and not resized while held.
15. **Descriptive alpha3** (adding the root's own buy-and-hold return) and the in-market fraction, because the month-end
    book is long-only and E.21's regressors are signed trend returns, not the asset's drift.
16. **Two coders** (BookCoder for the engine, TriggerCoder for the event extraction) in parallel instead of one BookCoder
    (V37: independent items); **two Fable reviewers** with distinct lenses (design and registration; code).
17. **BookCoder's thirteen conservative choices accepted** (lead_spec section R): an ineligible exit date excludes the unit
    (E.21 T3's rule; a calendar and bar-existence filter, never a price); the T3 entry eligibility in full, so Treasury
    roll blackouts at quarter month-ends remove about a third of the month-end units; stress = commission + 2 x (base -
    commission); discovery context ends 2019-04-30; Holm counts every registered trigger-hold; ties by id.
18. **TriggerCoder's eight readings accepted** (trigger ids as freeze labels; an event is an accepted entry that filled; D9.7
    price limits not applied on W_ext, where no table exists and W_cf shows no H6 refusal; H6's lead-in clamp not applied
    on W_ext).
19. **s_x null** for every row (W_cf from 2019-05-06); E.12's ML-panel S_X for ZF is not this trigger's (R-04).
20. **Registry ids renamed** E23-MEZFh5 etc. when the registry refused a second hyphen (03:33; nothing written by the
    refusal); power rerun with identical rows; freeze rebuilt.
21. **The confirmation step was run once with zero survivors** (03:35): it wrote its marker and recorded that nothing was
    read, so the order of P2.6 is on record.
22. **C-04 guard added** beyond the SHOULD FIX (the power table's events and config sha256 must equal the frozen files').
23. **Cost feasibility on approximate notionals** (typical prices; the H6 gross is the reader's arithmetic, not a published
    figure; R-07).
24. **Mechanism readers' deadline 03:45 PDT** and 60 searches each; all returned by 02:33.
25. **VerdictVerifier's NOTE-2 (W_cf rows in memory during discovery) was ruled a wording correction**, not a re-read or
    a code change. A second discovery read is barred (run-once), and the frozen loader is not edited after the reads. The
    return says "computed nothing from any bar dated after 2019-04-30"; decision 5 carries the loader bound forward.
26. **The `git status --short` quotes in section 2 omit the untracked (`??`) lines**: 1,029 at the start and 1,288 at the
    end. These are earlier stages' untracked pages plus this stage's new files before the final commit. Every other line is
    verbatim, and the full text is in reports/stage_e23_briefs/start_checks.txt and end_checks.txt.
27. **The end checks are the 05:21:40 run**, taken after both reads and before the end suite. A final rerun just before
    the commit (end_checks_final.txt) is quoted as its difference from the 05:21:40 run.
28. **After the stall, the verifier was resumed by message, not re-spawned.** Its file-based recomputation (343 rows)
    and spot_audit.py were already on disk, and only the run and the verdict line were missing.

## 7. Decisions for the user (the lead's recommendation first)

1. **Close "the program's intraday triggers at multi-day holds" as a direction.** Recommendation: yes. The four triggers
   with a moderate or strong multi-day mechanism and owned 2010-2019 data were read once on 7.7 years of data none of them
   had touched, and none came near the bar (largest alpha t 0.55; Holm smallest p 0.31). The month-end book's small raw
   gain is the bonds' own drift (alpha3 about zero). H6's reversal lost money at both holds. No variant (other roots, the
   20-day month-end hold, the opposite H6 direction, T2) should be tested on these windows: any of them would be chosen from
   this read.
2. **What to do with the multi-day data no E.23 computation used (W_cf 2019-05..2024-02, holdout-2).** Recommendation: keep it for a
   hypothesis with a stronger prior than these. A confirmation of E.23's (absent) survivors is moot. Note the structural
   finding: at a true net Sharpe of 0.5, no window the program owns supports a discovery read AND a confirmation read with
   power 0.2 each (W_cf at most 4.8 years gives 0.18; W_ext 7.7 years gives 0.27); W_cf + holdout-2 (about 5.8 years) gives
   about 0.21 and W_cf + holdout-2 + the research window about 0.25. A future multi-day test can confirm on those blocks
   only once, and only for a trigger the research window did not select.
3. **Data for a properly powered multi-day program.** Recommendation: do not buy data for this line now. Pre-2010 CME minute
   data is not on Databento's GLBX.MDP3 (it starts 2010-06), and a daily-settlement source for longer history would be a
   new vendor and a new design question; the trend evidence (E.21) and E22-F1 already cover the multi-day track's best
   candidate.
4. **Carried over:** E22-F1 still waits for the user's choice of a daily settlement source (recommendation from E.22: a
   fresh Databento statistics-schema quote); the AiTrader readout (2026-10-23) remains the next decision point.
5. **Bound the multi-day loader before the next multi-day discovery read** (VerdictVerifier NOTE-2, NOTE-5).
   Recommendation: yes, in the next multi-day stage's prompt. Load the stores only through ctx.last, so a discovery
   read never holds later bars in memory, and have the book write per-unit and per-fill files as E.21 did. This is a
   code change to base_rules/context.py or multiday/, outside any frozen member, so it needs the user's approval in
   that prompt. The E.23 numbers do not depend on it (the spot audit reproduced every value).

## 8. Session cost

No initial estimate table was printed before the first spawn (a deviation, section 4). The rows are set against the prompt's
clock instead: no outcome read after 10:30, the return by 11:30, the session ended by 12:00.

Sources:
- Times: PDT, from the STATE file, file mtimes, git, and each agent's first and last transcript message.
- Tokens: reports/stage_e23_briefs/ret/make_cost.py, run over the lead's .jsonl and every subagent transcript, counted to
  2026-10-17T14:29:56Z (07:29:56 PDT). The lead's last messages after that (final assembly and commit) are not counted.

### Final ETA table (actuals)

| Task | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Start checks | lead | opus | xhigh | 02:03:59 | 02:04:14 | 15 s | in lead | done; all expected |
| 0 Start suite (detached, nice 10) | lead | - | - | 02:04:19 | 02:28:56 | 24.6 min | in lead | 1 failed (known h6), 7634 passed |
| Context reading, scouting, briefs, lead spec | lead | opus | xhigh | 02:04 | 02:21 | 17 min | in lead | done |
| P1.1 inventory | InventoryReaderK1..K8, H6, CDE-OpusHigh (10, workflow) | opus | high | 02:16:13 | 02:28:24 | 12 min | 71,417,556 | 10/10 done |
| P1.2 mechanisms | MechanismReaderM1..M11-OpusHigh (11, workflow) | opus | high | 02:16:30 | 02:32:13 | 16 min | 94,195,121 | 11/11 done (deadline 03:45) |
| P2 engine | BookCoder-OpusXHigh | opus | xhigh | 02:21:42 | 02:42:24 | 21 min | 13,544,251 | done; E.21 sums and T3 exact |
| P2 events | TriggerCoder-OpusXHigh | opus | xhigh | 02:22:14 | 03:08:16 | 46 min | 44,187,620 | done; counters incident 02:46-02:58 disclosed |
| P1.3-P1.4 shortlist, data-use map | lead | opus | xhigh | 02:33 | 02:37 | 4 min | in lead | done before any outcome read |
| Prereg text, window and power reasoning | lead | opus | xhigh | 02:37 | 03:09 | 32 min (with waits on TriggerCoder) | in lead | done |
| Power table, first freeze | lead | opus | xhigh | 03:09 | 03:11 | 2 min | in lead | 3fdd98d7... |
| Registration review | RegReviewer-FableXHigh | fable | xhigh | 03:10:51 | 03:24:42 | 14 min | 1,768,830 | APPROVE WITH FIXES, 0 BLOCKING |
| Code review | CodeReviewer-FableXHigh | fable | xhigh | 03:11:00 | 03:29:43 | 19 min | 3,723,290 | APPROVE WITH FIXES, 0 BLOCKING |
| Fixes, freeze rebuilds, dry runs, commits, registration | lead | opus | xhigh | 03:25 | 03:33:45 | 9 min | in lead | 25bc321, 75874c4; r008-E23 N 533 -> 538; id rename |
| Discovery read (once) | lead | - | - | 03:33:54 | 03:34:35 | 41 s | in lead | rc 0; no survivor |
| Confirmation step (once) | lead | - | - | 03:35:27 | 03:35:29 | 2 s | in lead | 0 survivors; nothing read |
| Verification, part 1 | VerdictVerifier-FableXHigh | fable | xhigh | 03:35:45 | 03:36:26 | 1 min | (in the verifier's total below) | cut by the usage limit |
| Return tables and drafts | lead | opus | xhigh | 03:36 | 03:38 | 2 min | in lead | done |
| PAUSE: usage limit | - | - | - | 03:38 | 05:21 | 1 h 43 min | - | excluded from work |
| End checks; end suite (detached, nice 10) | lead | - | - | 05:21:40 | 05:41:25 | 20 min | in lead | 1 failed (known h6), 7728 passed |
| Verification, part 2 (file-based, 343 rows) | VerdictVerifier-FableXHigh | fable | xhigh | 05:21 | 05:41:05 | 20 min | (below) | done; then waited on a wait that could not fire |
| Return drafts (sections 2, 3, 6, 7) | lead | opus | xhigh | 05:22 | 05:41:33 | 19 min | in lead | done |
| STALL: the verifier's self-matching wait; the lead idle | - | - | - | 05:41:33 | 07:21:27 | 1 h 40 min | - | excluded from work; the cause is the lead's and the verifier's (section 4) |
| Verification, part 3 (spot audit, verdict) | VerdictVerifier-FableXHigh | fable | xhigh | 07:22 | 07:25:07 | 3 min | 9,542,109 (all parts) | VERIFIED WITH NOTES, 0 BLOCKING |
| Return, progress, STAGES, final checks, cost, commit | lead | opus | xhigh | 07:21:27 | about 07:35 | about 14 min | in lead | done; no push |
| **Stage** | lead and 26 worker spawns | | | 02:02:54 | about 07:35 | **about 2 h 10 min of work** (02:03-03:38, 05:21-05:41, 07:21-07:35); wall clock 5 h 32 min, of which 1 h 43 min pause and 1 h 40 min stall | **323,355,480** (lead 84,976,703; workers 238,378,777) | reads done at 03:35 (deadline 10:30); return written by about 07:35 (deadline 11:30) |

### Tokens per model

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,904 | 235,012 | 13,416,877 | 1,380,436 | 15,034,229 |
| claude-opus-5-5 | 3,498 | 1,449,464 | 300,979,056 | 5,889,233 | 308,321,251 |
| all | 5,402 | 1,684,476 | 314,395,933 | 7,269,669 | 323,355,480 |

Delegation share: the lead 84,976,703 (26.3%), workers 238,378,777 (73.7%). By model: Fable 4.6%, Opus 95.4%.

### Per worker spawn (agent file, model, effort as set, tokens)

| Spawn | Agent file | Model | Effort | Tokens |
|---|---|---|---|---|
| TriggerCoder-OpusXHigh | worker-xhigh | opus | xhigh | 44,187,620 |
| BookCoder-OpusXHigh | worker-xhigh | opus | xhigh | 13,544,251 |
| VerdictVerifier-FableXHigh | worker-xhigh | fable | xhigh | 9,542,109 |
| CodeReviewer-FableXHigh | worker-xhigh | fable | xhigh | 3,723,290 |
| RegReviewer-FableXHigh | worker-xhigh | fable | xhigh | 1,768,830 |
| InventoryReaderCDE-OpusHigh | workflow agent | opus | high | 11,418,905 |
| InventoryReaderK2-OpusHigh | workflow agent | opus | high | 10,543,576 |
| InventoryReaderK3-OpusHigh | workflow agent | opus | high | 9,166,818 |
| InventoryReaderK4-OpusHigh | workflow agent | opus | high | 7,783,905 |
| InventoryReaderK6-OpusHigh | workflow agent | opus | high | 7,575,743 |
| InventoryReaderK5-OpusHigh | workflow agent | opus | high | 7,124,358 |
| InventoryReaderK1-OpusHigh | workflow agent | opus | high | 6,798,447 |
| InventoryReaderK8-OpusHigh | workflow agent | opus | high | 4,417,225 |
| InventoryReaderH6-OpusHigh | workflow agent | opus | high | 4,018,176 |
| InventoryReaderK7-OpusHigh | workflow agent | opus | high | 2,570,403 |
| MechanismReaderM10_USDA-OpusHigh | workflow agent | opus | high | 10,792,595 |
| MechanismReaderM11_OVERNIGHT_REVERSAL_VOL-OpusHigh | workflow agent | opus | high | 10,643,057 |
| MechanismReaderM2_FOMC-OpusHigh | workflow agent | opus | high | 10,306,577 |
| MechanismReaderM5_BREAKOUT_LOCATION-OpusHigh | workflow agent | opus | high | 9,481,681 |
| MechanismReaderM4_INTRADAY_MOM-OpusHigh | workflow agent | opus | high | 8,811,785 |
| MechanismReaderM9_ENERGY_REPORTS-OpusHigh | workflow agent | opus | high | 8,491,619 |
| MechanismReaderM6_AUCTION-OpusHigh | workflow agent | opus | high | 8,455,135 |
| MechanismReaderM3_FLIGHT-OpusHigh | workflow agent | opus | high | 7,882,276 |
| MechanismReaderM8_FIXES-OpusHigh | workflow agent | opus | high | 6,849,121 |
| MechanismReaderM7_MONTHEND-OpusHigh | workflow agent | opus | high | 6,500,415 |
| MechanismReaderM1_LIMIT-OpusHigh | workflow agent | opus | high | 5,980,860 |

These are token counts, not plan-credit percentages; the /usage meter is the user's to read. The 21 readers spent 165.6M
tokens (51% of the stage), most of it cache reads. That is the largest line to trim in a later stage, for example with
fewer, merged inventory readers.
