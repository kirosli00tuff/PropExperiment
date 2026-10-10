# Stage E.17 return: C1 STOPPED at C10; the base-rule batch H1-H5 run once, all five FAIL

Prompt docs/prompts/STAGE_E.17.md (V24-V30; V30 amended to a $124.00 budget). Lead Opus 5.5 xhigh, Claude sessions
0dcecb5d (18:34-19:38) and c71b1fb9 (19:41 on; resumed after the first ended), usage logged under 0dcecb5d. All times
PDT, from `date`, file times or logs. Stage start 18:34 on 2026-10-09.

## 1. Verdict summary

**C1: STOPPED.** Its single evaluation stopped at guard C10: g17_mbt applies on 0 NG rows in 2010-2019 (87 and 84
in E.12). MBT did not exist then, and the freeze has no exemption for a leg that is n/a by design. No T1 or T2
statistic exists. Fable verified the stop. The attempt is closed and not rerun.

**E16-H1..H5: all five FAIL** (base case, Holm 0.05, N 478). Fable recomputed every number:
H1-H4 VERIFIED, H5 VERIFIED WITH NOTES, no BLOCKING finding.

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
$ date
Fri Oct  9 18:37:04 PDT 2026
$ git status --short
?? .claude/worktrees/
?? reports/stage_e12/e13/e14/e16_briefs page files: 639 lines (collapsed; full text in reports/stage_e17_briefs/start_checks.txt)
?? reports/stage_e17_briefs/
$ git log --oneline -3
7447677 docs: V30 amendment corrected, E.17 budget $126.30 (balance $130.23)
5f9671d docs: V30 amended, E.17 budget $122.50 (balance $126.25)
d6b869a docs: Stage E.17 prompt (C1 and base-rule batch, $97 budget) and V30
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
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b
preflight OK: fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b
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
29040 ledger/databento_spend.jsonl
a9ad6ab59b94818407042d4faf1ccaaa3bab72447376dcce631f3312cc12b2de
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 231.599730 cap 249.67 headroom 18.070270
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
$ uv run python -m screening.trial_registry status
N = 471 (1 lines)
$ wc -l ledger/trial_registrations.jsonl; sha256sum
1
a73b4de878caa75066a8c24513e354de0a07d34f15d53407c4450e6f0135de0d
$ E.14 C1 freeze (reports/stage_e14_prereg_C1.md; pinned afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b): sha256, tracked, no diff vs HEAD, commits touching
afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b
tracked
no diff vs HEAD
1680982 
$ E.14 C1 freeze inputs list (reports/stage_e14_c1_freeze_inputs.json; pinned 3356d676...)
list sha256 3356d67604245db99383215f1fb7f694d25a1beb71b0693a86faeb7243a5140e entries 43 mismatches []
$ E.16 freeze: uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4
E.16 freeze OK: 97 files; manifest sha256 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4
exit 0
$ git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md
exit 0
```

Start suite (18:37:38-18:54:28): `6815 passed, 2 skipped, 3 xfailed, 54 warnings in 1007.46s`, rc=0.

**After C1's purchase, 22:41** (reports/stage_e17_briefs/post_c1_purchase_checks.txt; harness v11). The one freeze
inputs mismatch is the harness manifest itself (v10 -> v11), which C1's freeze section 11 allows:

```
$ date
Fri Oct  9 10:41:08 PM PDT 2026
$ git status --short
 M ledger/databento_spend.jsonl
 M ledger/trial_registrations.jsonl
?? ..env.swp
?? .claude/worktrees/
?? reports/hist/
?? reports/stage_e12/e13/e14/e16_briefs page files: 639 lines (collapsed; full text in reports/stage_e17_briefs/post_c1_purchase_checks.txt)
?? reports/stage_e17_STATE.md
?? reports/stage_e17_briefs/
?? reports/stage_e17_c1_calendar_hashes.json
?? reports/stage_e17_review.md
?? reports/stage_e17_rulings.md
$ git log --oneline -3
a21d82d harness v11, acct-2 cap for C1
8e5707c docs: V30 amendment, E.17 budget $124.00 (user choice)
7447677 docs: V30 amendment corrected, E.17 budget $126.30 (balance $130.23)
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
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected ba1ce99672b7e5bbb33f0cfabb89ba618d207d701348da1b1681ecfa7d932292
preflight OK: ba1ce99672b7e5bbb33f0cfabb89ba618d207d701348da1b1681ecfa7d932292
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
31610 ledger/databento_spend.jsonl
ba22273fbfe658d9a0bfc75f0deaa6e1c0a1ba2ff9328bc0fadcb309621a4864
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 289.417062 cap 291.08 headroom 1.662938
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
$ uv run python -m screening.trial_registry status
N = 473 (2 lines)
r001-C1: C1 ['C1-T1', 'C1-T2'] N 471 -> 473 at 2026-10-09T19:29:06-07:00
$ wc -l ledger/trial_registrations.jsonl; sha256sum
2
4b1bf93d86a2b65b66e52c32aee927641b0d2fb1e5581a1fddbe54a4b521e585
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
```

**After the base-rule purchase, 01:27 on 2026-10-10** (reports/stage_e17_briefs/post_h_purchase_checks.txt; harness
v12):

```
$ date
Sat Oct 10 01:26:58 AM PDT 2026
$ git status --short
 M ledger/databento_spend.jsonl
 M ledger/trial_registrations.jsonl
 M reports/stage_e17_STATE.md
 M reports/stage_e17_review.md
 M reports/stage_e17_rulings.md
?? ..env.swp
?? .claude/worktrees/
?? reports/hist/purchase_CL_ext2010h.json
?? reports/hist/purchase_HE_ext2010h.json
?? reports/hist/purchase_LE_ext2010h.json
?? reports/hist/purchase_RTY_ext2010h.json
?? reports/hist/purchase_TN_ext2010h.json
?? reports/hist/purchase_UB_ext2010h.json
?? reports/hist/purchase_ZB_ext2010h.json
?? reports/hist/purchase_ZF_ext2010h.json
?? reports/hist/purchase_ZL_ext2010h.json
?? reports/hist/purchase_ZS_ext2010h.json
?? reports/hist/purchase_ZT_ext2010h.json
?? reports/stage_e12/e13/e14/e16_briefs page files: 639 lines (collapsed; full text in reports/stage_e17_briefs/post_h_purchase_checks.txt)
?? reports/stage_e17_a3_selection.json
?? reports/stage_e17_briefs/a3_select.out
?? reports/stage_e17_briefs/brief_h_verify.md
?? reports/stage_e17_briefs/brief_v12_review.md
?? reports/stage_e17_briefs/fresh_quote_ext2010h.json
?? reports/stage_e17_briefs/fresh_quote_ext2010h.out
?? reports/stage_e17_briefs/h_buy_p1.log
?? reports/stage_e17_briefs/h_buy_p2.log
?? reports/stage_e17_briefs/h_buy_p3.log
?? reports/stage_e17_briefs/h_buy_p4.log
?? reports/stage_e17_briefs/h_buy_start.txt
?? reports/stage_e17_briefs/h_register.log
?? reports/stage_e17_briefs/post_h_purchase_checks.txt
?? reports/stage_e17_briefs/pytest_v12.out
?? reports/stage_e17_briefs/quote_ext2010h.log
?? reports/stage_e17_briefs/quotes_ext2010h.json
?? reports/stage_e17_briefs/quotes_ext2010h.md
?? reports/stage_e17_briefs/v12.diff
?? reports/stage_e17_briefs/v12_report.md
?? reports/stage_e17_c1_verify/
?? reports/stage_e17_fallback.json
$ git log --oneline -3
d30f50c harness v12, ext2010h plan
558a7ce E.17 C1 evaluated
a21d82d harness v11, acct-2 cap for C1
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
N = 478 (3 lines)
r001-C1: C1 ['C1-T1', 'C1-T2'] N 471 -> 473 at 2026-10-09T19:29:06-07:00
r002-E16: E16 ['E16-H1', 'E16-H2', 'E16-H3', 'E16-H4', 'E16-H5'] N 473 -> 478 at 2026-10-10T00:30:15-07:00
$ wc -l ledger/trial_registrations.jsonl; sha256sum
3
851f18218bc22d76ae16b9c8ceee49cbe764af6e3c4e19de3b66b0abd0210e9f
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
```

**End checks** (reports/stage_e17_briefs/end_checks.txt; harness v12):

```
$ date
Sat Oct 10 02:04:22 AM PDT 2026
$ git status --short
 M ledger/databento_spend.jsonl
 M ledger/trial_registrations.jsonl
 M reports/stage_e17_STATE.md
 M reports/stage_e17_review.md
 M reports/stage_e17_rulings.md
?? ..env.swp
?? .claude/worktrees/
?? reports/hist/bars_CL_ext2010h.json
?? reports/hist/bars_HE_ext2010h.json
?? reports/hist/bars_LE_ext2010h.json
?? reports/hist/bars_RTY_ext2010h.json
?? reports/hist/bars_TN_ext2010h.json
?? reports/hist/bars_UB_ext2010h.json
?? reports/hist/bars_ZB_ext2010h.json
?? reports/hist/bars_ZF_ext2010h.json
?? reports/hist/bars_ZL_ext2010h.json
?? reports/hist/bars_ZS_ext2010h.json
?? reports/hist/bars_ZT_ext2010h.json
?? reports/hist/purchase_CL_ext2010h.json
?? reports/hist/purchase_HE_ext2010h.json
?? reports/hist/purchase_LE_ext2010h.json
?? reports/hist/purchase_RTY_ext2010h.json
?? reports/hist/purchase_TN_ext2010h.json
?? reports/hist/purchase_UB_ext2010h.json
?? reports/hist/purchase_ZB_ext2010h.json
?? reports/hist/purchase_ZF_ext2010h.json
?? reports/hist/purchase_ZL_ext2010h.json
?? reports/hist/purchase_ZS_ext2010h.json
?? reports/hist/purchase_ZT_ext2010h.json
?? reports/stage_e12/e13/e14/e16_briefs page files: 639 lines (collapsed; full text in reports/stage_e17_briefs/end_checks.txt)
?? reports/stage_e17_a3_selection.json
?? reports/stage_e17_briefs/a3_select.out
?? reports/stage_e17_briefs/brief_h_verify.md
?? reports/stage_e17_briefs/brief_v12_review.md
?? reports/stage_e17_briefs/collapse_checks.py
?? reports/stage_e17_briefs/end_checks.txt
?? reports/stage_e17_briefs/fresh_quote_ext2010h.json
?? reports/stage_e17_briefs/fresh_quote_ext2010h.out
?? reports/stage_e17_briefs/h_buy_p1.log
?? reports/stage_e17_briefs/h_buy_p2.log
?? reports/stage_e17_briefs/h_buy_p3.log
?? reports/stage_e17_briefs/h_buy_p4.log
?? reports/stage_e17_briefs/h_buy_start.txt
?? reports/stage_e17_briefs/h_register.log
?? reports/stage_e17_briefs/h_store_build.log
?? reports/stage_e17_briefs/post_h_purchase_checks.txt
?? reports/stage_e17_briefs/pytest_v12.out
?? reports/stage_e17_briefs/quote_ext2010h.log
?? reports/stage_e17_briefs/quotes_ext2010h.json
?? reports/stage_e17_briefs/quotes_ext2010h.md
?? reports/stage_e17_briefs/ret_decisions.md
?? reports/stage_e17_briefs/ret_open_choices.md
?? reports/stage_e17_briefs/ret_results.md
?? reports/stage_e17_briefs/ret_verification.md
?? reports/stage_e17_briefs/return_template.md
?? reports/stage_e17_briefs/run_H1.log
?? reports/stage_e17_briefs/run_H2.log
?? reports/stage_e17_briefs/run_H3.log
?? reports/stage_e17_briefs/run_H4.log
?? reports/stage_e17_briefs/run_H5.log
?? reports/stage_e17_briefs/run_h.sh
?? reports/stage_e17_briefs/v12.diff
?? reports/stage_e17_briefs/v12_report.md
?? reports/stage_e17_briefs/verdict.log
?? reports/stage_e17_c1_verify/
?? reports/stage_e17_fallback.json
?? reports/stage_e17_h_verify/
?? reports/stage_e17_run_manifest.json
?? reports/stage_e17_runs/
$ git log --oneline -3
d30f50c harness v12, ext2010h plan
558a7ce E.17 C1 evaluated
a21d82d harness v11, acct-2 cap for C1
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
N = 478 (3 lines)
r001-C1: C1 ['C1-T1', 'C1-T2'] N 471 -> 473 at 2026-10-09T19:29:06-07:00
r002-E16: E16 ['E16-H1', 'E16-H2', 'E16-H3', 'E16-H4', 'E16-H5'] N 473 -> 478 at 2026-10-10T00:30:15-07:00
$ wc -l ledger/trial_registrations.jsonl; sha256sum
3
851f18218bc22d76ae16b9c8ceee49cbe764af6e3c4e19de3b66b0abd0210e9f
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
```

End suite: 02:04:34-02:20:59, `6916 passed, 3 skipped, 3 xfailed, 54 warnings in 982.33s (0:16:22)`, rc=0 (reports/stage_e17_briefs/pytest_end.out)

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
| 01:40-02:03 | Fable recomputes every H verdict number |
| 02:22 | End checks, end suite, final commit |

## 3. Results per step

### Part 1: C1 (hand-off steps 1-7)

1. **Start checks and suite (step 1).** All pass at harness v10: holdout all_ok with 0 unlocks, REGISTRATION.md
   0 bytes, check_frozen ALL_OK, cluster freezes K1-K8, v2 freeze (91 files), N = 471, the ledger 29,040 lines.
   acct-2 had spent 231.599730 against a 249.67 cap. Suite: 6815 passed.
2. **C1's freeze verified by script (step 2).** reports/stage_e17_briefs/verify_freeze.py (E.15's, output path changed)
   gave ALL_OK; verify_freeze.json sha256 5029b5c7... It checked:
   - the 43 inputs of reports/stage_e14_c1_freeze_inputs.json (list sha256 3356d676...);
   - the freeze file afc5c10f..., tracked, with no diff and touched only by 1680982;
   - the E.12 state copy (51 files);
   - the model JSON c6075306..., both M1 payloads and q;
   - the v10 preflight.
3. **E.16 freeze verified (step 3).** freeze_manifest.py verify OK (97 files, 5274aa97...), and
   `git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md` exited 0.
4. **Fresh quote, which was also the access check (steps 4-5; A2).** acct-2 was unlocked.
   - 642 of 642 chunks were quoted with 0 failed, 18:54:50-19:06:57, under session stage-E.14-2026-10-05.
   - The guard (reports/stage_e17_briefs/fresh_quote_guard.py: E.15's, generalized and dry-run against E.15's failed
     lines, which it refused) summed the run's own 642 ledger lines: $57.742330.
   - Per root: NG 8.570392, NQ 10.625886, ZN 10.106134, 6E 11.072096, GC 11.182294, ZC 6.185528. That equals E.14's
     quote and the tool's JSON.
   - x 1.03 = $59.474600, within the $124.00 budget; the session cap of $59.47 is within V27's $60.00.
5. **Harness v11 (step 6).**
   - The diff: ACCOUNT_2_CAP_USD 249.67 -> 291.08 (231.599730 + 59.474600, rounded up) and E14_EXT2010_SESSION_CAP_USD
     0.00 -> 59.47 (rounded down), each with a comment.
   - The pinning assertions changed: test_e14_config_v10.py:20,32-33; test_e14_pull_hist.py:300, and :196, which
     also pins the cap (V11-R1); test_stage_e_config_v8.py:64-65, cited 62-64.
   - Manifest ba1ce996... Only those four file entries changed, plus the creation time and head fields.
   - Fable APPROVE (0 BLOCKING, 0 SHOULD FIX, 4 NOTE). Suite 6815 passed. Commit a21d82d.
6. **Registration, buy, stores and evaluation (step 7).**
   - Registered r001-C1 at 19:29:06 (N 471 -> 473).
   - Bought all 642 chunks: $57.817332 billed, i.e. the quote plus one orphan commit of $0.075002. The first buy process
     died with the Claude session at 19:37:46, during NG 2013-03's download; that chunk was committed but not settled,
     with no file. The identical command resumed at 19:42:33, skipped the 33 settled chunks and finished at 22:40:40
     with no chunk billed above its quote.
   - Built six ext2010 stores, 2010-06-07..2019-04-30, 2,241-2,287 trade dates each, 0 unsourced rows.
   - Hash files: stores b77bfc18..., calendars d5e48579... (byte-identical to E.15's).
   - Evaluated once: marker 22:47:44, STOPPED at C10 at 22:48:44 (exit 1; 1:05 wall; 2.06 GB peak). Result
     reports/stage_e14_c1_result.json, sha256 e5bbcaeb...
   - NG ok rows were h60 5,120 and hF 4,538. The only feature that was live on NG rows in E.12 and dead now is
     g17_mbt (E.12 87 and 84; now 0).
   - Rulings C1-R1..R5; Fable verification C1-V1..V4.

### Part 2: the base-rule batch (hand-off steps 8-15)

7. **Harness v12 (step 8).**
   - V12Coder-OpusXHigh wrote the diff in an isolated worktree, and the lead applied it on main. It covers:
     - plan "ext2010h" (label E16, ids E16-H1..H5, the 21 roots with per-root chunk lists, 1,993 chunks, store trade
       dates 2010-07-01..2019-04-30);
     - its own quote and buy session stage-E.17-ext2010h;
     - `--roots` (A4), which the lead made required for an ext2010h buy (review F-1);
     - the livestock hist calendar, a byte copy (802a4dd9...);
     - the ext2010h store builder;
     - tests.
   - No file of the E.16 freeze changed.
   - Fable: APPROVE WITH FIXES (F-1, F-2 fixed), then caps follow-up APPROVE.
   - Caps: ACCOUNT_2_CAP_USD 355.38; E17_EXT2010H_SESSION_CAP_USD 65.82 (V12-R3).
   - Manifest ece91ae8... Suite 6916 passed. Commit d30f50c.
8. **Fresh ext2010h quote (step 9).**
   - 1993 of 1993 chunks quoted with 0 failed, 23:36:08-00:01:54, under the new session.
   - The guard summed the run's own 1,993 lines: $153.965349, equal per root to E.12's quote.
9. **A3 selection (fixed before any quote).**
   - B = $124.00 - $57.817332 = $66.182668.
   - Order: ZT, ZF, ZB, then E.12's ranking mapped to price-path roots, skipping C1's six. Greedy on each root's fresh
     quote x 1.03, with the budget left falling by each taken root's quote x 1.03.

| Priority | Root | Quote x 1.03 ($) | Budget left before ($) | Taken? |
|---|---|---|---|---|
| 1 | ZT | 6.222467 | 66.182668 | taken |
| 2 | ZF | 9.364551 | 59.960200 | taken |
| 3 | ZB | 9.509736 | 50.595650 | taken |
| 4 | CL | 11.353945 | 41.085913 | taken |
| 5 | ZL | 6.409844 | 29.731968 | taken |
| 6 | ZS | 7.139396 | 23.322124 | taken |
| 7 | UB | 7.435118 | 16.182728 | taken |
| 8 | TN | 2.875335 | 8.747611 | taken |
| 9 | YM | 10.817687 | 5.872276 | skipped |
| 10 | RTY | 1.959305 | 5.872276 | taken |
| 11 | LE | 3.221091 | 3.912971 | taken |
| 12 | HG | 10.386760 | 0.691880 | skipped |
| 13 | 6S | 8.929036 | 0.691880 | skipped |
| 14 | HE | 0.468523 | 0.691880 | taken |
| 15-21 | 6J, 6A, 6B, 6N, ZM, ZW, 6C | 5.83-11.19 | 0.223357 | skipped |

   - Selected: 11 roots, 933 chunks, quote $64.038166 (x 1.03 $65.959311), with $0.223357 left. Selection
     reports/stage_e17_a3_selection.json, sha256 488b58f9...
10. **Fallback list and registration (step 10).**
    - reports/stage_e17_fallback.json (sha256 1acf1d96...): the 10 skipped roots, "not funded", window
      2019-05-06..2024-02-29. It was in STATE before any Part 2 purchase.
    - Registered r002-E16 at 00:30:15 (E16-H1..H5 against the E.16 freeze under v12; N 473 -> 478). The note records
      both sha256s.
11. **Buy (step 11).** Four detached processes over disjoint roots (CL ZT HE; ZB ZF RTY; UB ZS TN; ZL LE), 00:30:28 to
    01:26:30, all rc=0.
    - 933 chunks for $64.038166, equal to the quote, with no billed-above-quote stop.
    - Symbology was fetched for all 11 roots, including TN, RTY and HE. The condition file was written once.
    - acct-2 has now spent $353.455228; the stage total is $121.855498.
12. **Stores and run manifest (step 12).**
    - Eleven ext2010h stores built (3:15; 1.37 GB). LE and HE dropped 6,081 and 1,084 rows booked to unsourced
      livestock dates (R-C3). No purchase or build failed, so the fallback list is unchanged.
    - Run manifest reports/stage_e17_run_manifest.json, sha256 256a5410...: 6 ext2010 stores, 11 ext2010h and
      10 fallback.
    - Pre-marker dry check on it: context OK, 0 preflight refusals.
13. **The five runs, once each (step 13).**
    - H1 complete in 3:02 (1.58 GB). H2 in 0:24. H3 in 0:35. H4 in 2:59. H5 in 0:03 (no bar read).
    - Every marker was written before any bar was read, and every result records the registry path and sha256 (R-2).
14. **Verdict (step 14).** reports/stage_e17_runs/verdict.json, sha256 0c1777da..., N 478. Base case, Holm 0.05 over
    the five, with the stress and 1.5 x slippage cases reported.

| Test | Base n | mean | t | p | Holm | mean > 0 | n >= 30 | Years (qualifying / positive) | Pass | Stress mean / p | 1.5x slip mean / p |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 | 3,380 | -0.161 | -20.01 | 1.0 | no | no | yes | 15 / 0 | FAIL | -0.424 / 1.0 | -0.236 / 1.0 |
| H2 | 56 | +0.344 | +1.52 | 0.0677 | no | yes | yes | 6 / 5 (passes) | FAIL | +0.287 / 0.105 | +0.329 / 0.076 |
| H3 | 405 | -0.015 | -0.26 | 0.604 | no | no | yes | 12 / 5 | FAIL | -0.084 / 0.926 | -0.033 / 0.712 |
| H4 | 3,381 | -0.048 | -6.72 | 1.0 | no | no | yes | 15 / 0 | FAIL | -0.112 / 1.0 | -0.067 / 1.0 |
| H5 | 3,400 | -0.149 | -1.46 | 0.929 | no | no | yes | 15 / 2 | FAIL | -0.373 / 1.0 | -0.213 / 0.998 |

    - DSR at N = 478: H1 0.0, H2 0.0064, H3 0.0, H4 0.0, H5 0.0.
    - Descriptive only (the lead's sum over H1's 55,070 traded units with a sigma, after its run; adds nothing to N):
      mean gross_cents/sigma 5.22 against mean base costs_cents/sigma 20.83. The mean gross per traded unit is
      positive but about a quarter of the mean base cost.
15. **Fable recomputation (step 15).** See section 5.

## 4. Delegation record

| # | Agent (description) | File | Model | Effort | Start | End | Tokens | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | HarnessReviewer-FableXHigh (v11 diff) | worker-xhigh | fable | xhigh | 19:10 | 19:26 | 1,548,942 | APPROVE (0 BLOCKING, 0 SHOULD FIX, 4 NOTE) |
| 2 | VerdictVerifier-FableXHigh (C1's STOPPED verdict) | worker-xhigh | fable | xhigh | 22:51 | 23:08 | 4,489,321 | VERIFIED WITH NOTES (F-1 to the user) |
| 3 | V12Coder-OpusXHigh (v12 diff, isolated worktree) | worker-xhigh | opus | xhigh | 22:51 | 23:16 | 21,387,333 | done; diff applied by the lead, worktree removed |
| 4 | HarnessReviewer-FableXHigh (v12 diff; caps follow-up 00:07-00:12 by SendMessage) | worker-xhigh | fable | xhigh | 23:18 | 00:12 | 3,477,338 | APPROVE WITH FIXES (F-1, F-2 fixed), then APPROVE |
| 5 | VerdictVerifier-FableXHigh (H1-H5 verdict numbers) | worker-xhigh | fable | xhigh | 01:40 | 02:03 | 7,223,323 | H1-H4 VERIFIED, H5 VERIFIED WITH NOTES, 0 BLOCKING |

## 5. Verification

Four Fable checks ran, each worker-xhigh on fable, as the prompt names them. Every finding and its ruling is in
reports/stage_e17_review.md and reports/stage_e17_rulings.md.

| Check | When | Verdict | Findings | Rulings and fixes |
|---|---|---|---|---|
| v11 diff (HarnessReviewer) | 19:10-19:25 | APPROVE | 0 BLOCKING, 0 SHOULD FIX, 4 NOTE | V11-R1 line 196 within the freeze's words; R2 the dropped `funds >= cap` assertion (the invariant holds); R3 older sessions' room (pre-existing, no session ran); R4 stale names left (the freeze allows only assertions) |
| C1's verdict (VerdictVerifier) | 22:51-23:08 | VERIFIED WITH NOTES | 0 BLOCKING, 1 SHOULD FIX (F-1), 4 NOTE | C1-V1: F-1, the freeze contradiction (C10 vs section 2 for g17_mbt), decidable since 2026-10-05, goes to the user (section 7); V2-V4 recorded. The STOP stands, verified: reference 87/84 recomputed, run 0 of 5,137 NG rows, c10_check is the freeze's sentence, order and leakage 11/11, hashes 12/12 |
| v12 diff (HarnessReviewer) | 23:18-23:35; caps follow-up 00:07-00:12 | APPROVE WITH FIXES, then APPROVE | 0 BLOCKING, 2 SHOULD FIX (F-1, F-2), NOTEs N-1..N-8 | V12-R1 F-1 FIXED: an ext2010h buy needs --roots. V12-R2 F-2 FIXED: cap and session pins in the hashed test_e14_config_v10.py. V12-R3 the concurrency bound sets the session cap at 65.82. V12-R4/R5 the coder's points and the quote on the reviewed tree. V12-R6 the caps follow-up verified the selection, both caps (worst case $123.99), F-1 and manifest ece91ae8 |
| H1-H5 verdicts (VerdictVerifier) | 01:40-02:03 | H1-H4 VERIFIED, H5 VERIFIED WITH NOTES | 0 BLOCKING, 4 NOTE | H-V1 every verdict number verified (series to <= 2.8e-14; 714 units spot-checked against the stores, 0 mismatches); H-V2 H5's sd comes from four sparse-component dates (literal frozen wording; the verdict is unaffected; any reuse must guard sigma); H-V3 H3's flip cost accepted; H-V4 the unverifiable counters recorded; H-V5 the brief's focus points disclosed |

No BLOCKING finding arose on any verdict, so no verdict is reported as unverified. No fix touched a frozen file or a
registered parameter. The two code fixes (v12 F-1 and F-2) were made before v12's first use and before its commit.

## 6. Open choices (every decision the lead made on its own, with the reason)

1. **Budget.** Three planning-chat messages before any quote set the budget at $122.50, then $126.30, then FINAL
   $124.00 (commits 5f9671d, 7447677, 8e5707c). The last one governed (ruling B-1). At about 01:21 the user wrote
   "theres 125 total on the account. use all if needed". A3 rerun at $125.00 selects the same 11 roots, and the
   selection and fallback list were already registered, so nothing changed (B-2).
2. **Order: quote, v11, register, buy.** The hand-off's steps 5-7 and C1's freeze section 11 put the fresh quote first.
   The prompt summary lists "harness v11, fresh quote". The quote ran first under v10, as E.15 did, because v11's caps
   need the fresh total.
3. **E.17's own scripts.** The scripts are copies of E.15's with output paths changed, so no earlier stage's file
   was overwritten:
   - check script (adds the E.14 inputs check and the E.16 freeze verification);
   - freeze verifier;
   - hash-file writer.
   The calendar hash file is byte-identical to E.15's.
4. **The guard was generalized** to both plans and A1's budget. It was dry-run on E.15's failed lines, which it
   refused. The A3 selection script was written before any quote (18:43-18:45) and reads no market data.
5. **v11's test assertions.**
   - tests/test_e14_pull_hist.py:196 also pins E14_EXT2010_SESSION_CAP_USD and failed on v11. The freeze's citation
     list omits it, so it was changed under the freeze's governing words "the test assertions that pin those two
     values" (V11-R1; Fable agreed).
   - test_stage_e_config_v8.py's pinning assertions are lines 64-65, not 62-64 (E.15 item 14). The dropped
     `funds >= cap` (V11-R2) became a value pin.
6. **Commits hold only what they name.** The v11 and v12 commits hold only harness files; the ledger's quote and buy
   lines went into "E.17 C1 evaluated" and the final commit. The commit "E.17 C1 evaluated" uses the prompt's name:
   C1 was evaluated once, and its verdict is STOPPED.
7. **The C1 buy interrupted by the session end.**
   - The first Claude session ended at about 19:38 and its background shell took the buy with it, after 33 settled
     chunks. NG 2013-03 had been committed ($0.075002) without a settle, and it left no file.
   - The identical command resumed at 19:42:33; the tool skips settled chunks.
   - The orphan commit stays in the ledger and is counted as spend (conservative): $57.817332 against the
     $57.742330 quote.
   - Every long job after that ran detached (setsid nohup) with an rc line in its log.
8. **C1 STOPPED, not rerun.** The C10 stop is the freeze's rule applied as written; the freeze says a C10 stop closes
   the attempt, and the prompt forbids a second run (C1-R1, C1-R2). The Fable check after step 7 verified the STOP
   (C1-R5), because no verdict statistic existed to recompute. A6 did not apply (NQ and ZN were bought), so H2 stayed.
9. **v12 in a worktree; the quote before the commit.**
   - The coder worked in an isolated git worktree. The lead applied its diff (sha256 5f68cc84...) on main.
   - The ext2010h quote ran on the uncommitted, Fable-reviewed v12 with the caps at 0.00. Quote-only takes no
     harness sha; E.12's open choice 7 is the precedent. This put the caps into the single v12 commit the prompt
     names.
   - The coder's worktree (.claude/worktrees/agent-a463ba71418f7066b) was removed at the end.
10. **F-1 made `--roots` mandatory for an ext2010h buy** (Fable SHOULD FIX). It is a tightening inside
    data/pull_hist.py, a file v12 changes anyway.
11. **v12's caps.**
    - ACCOUNT_2_CAP_USD = acct-2's spend after C1 + the A3 selection's quote x 1.03, rounded up: 355.38. That is the
      hand-off's formula with the selection's total in place of the 21-root total, as A1 and A3 require.
    - The session cap is $65.82, not the formula's $65.95. That tightening lets 4 concurrent buy processes (each able
      to overshoot by one in-flight chunk, the largest $0.115211) stay within $124.00 (V12-R3; Fable checked: worst
      case $123.99).
12. **Four buy processes over disjoint roots** (E.12's precedent). This cut the base-rule buy to 56 minutes. The C1 buy
    had run serially at about 17 s a chunk.
13. **A3's "budget left" falls by each taken root's quote x 1.03**, not by the bare quote (conservative, consistent
    with the caps).
14. **Step-2 stores in the run manifest.** They were taken from reports/step2/bars_<ROOT>.json, E.12's store
    summaries. The hand-off calls it "E.12's start-rule file", but no file by that name exists. Each sha256 was
    checked on disk.
15. **A pre-marker dry check before the H registration** (lesson from C1). It ran on a scratch manifest at 22:52 and
    again on the real one at 01:31: base_rules' freeze check, context build and store preflight, with no bar read
    and no marker. It is not part of the frozen procedure and changed nothing.
16. **A descriptive look at H1's units** right after H1's run (gross versus cost). H2-H4 were frozen and could not be
    affected. It is reported as descriptive and adds nothing to N.
17. **The H-verification brief carried three run numbers.** After the runs the lead appended "focus points" quoting
    H1's mean and t and H5's per-case sd, to direct Fable's checks to costs and H5's scaling. The prompt asks Fable to
    work "without reading the lead's statistics first". Fable still recomputed every number from the units and stores,
    but this is a departure, and it is recorded here.
18. **Times.** Several STATE entries were first written with estimated times and corrected the same minute from
    `date` and file times (memory rule). The user's 01:21 message was first logged as 00:33 and corrected.
19. **No Firecrawl, web search or other network use** besides Databento's quote, buy and free metadata calls.
20. **The untracked ..env.swp** at the repo root (an editor swap file) was never opened, read, staged or committed
    (section 7).

## 7. Decisions for the user (the lead's recommendation first)

1. **C1: rerun under a corrected freeze, or close it.**
   - Recommended: a new pre-registration "C1b". It is identical to C1 except that C10 names the legs that are n/a by
     design (MBT; CL is already 0 in E.12) as exempt. Before registering, a frozen dry check should run c10_check on
     the frozen reference against the sentinel frames (Fable F-1).
   - Costs: N + 2 (478 -> 480) and no purchase. The six 2010-2019 stores are bought and the model, q and calendars are
     frozen, so it is one short session.
   - Why: C1 never produced an answer. With the data owned, the only cost is N.
   - The alternative is to close the NG near-miss as unresolved: the freeze contradicted itself and nothing was learned.
2. **The base-rule batch: close it.**
   - All five registered tests fail on the base case: Holm rejects none, DSR is about 0 at N = 478, and the stress
     and 1.5 x slippage cases are worse. Per the common file (section 10), there is no holdout-2 read and no
     meta-labeling design (V28) for any of H1-H5. Holdout-2 stays sealed.
   - H2's positive mean (+0.344, p 0.068, 5 of 6 years positive) is not a pass. Any H2 variant would be a new
     pre-registration counted from N = 478.
   - H1's gross momentum is positive but about a quarter of D8 costs, so it is not a cost-feasible rule at these
     horizons.
   - Recommended: no rerun or variant of H1-H5 on these windows.
3. **What the next search should cost-check first.** H1 and H4 show that 30-minute and next-day horizons at D8 costs
   leave little room: costs are about 4x H1's gross. Recommended: any new hypothesis states its expected gross per
   trade against the D8 cost of its vehicle before pre-registration (a cost-feasibility gate), so a decade of data is
   not bought to learn the cost arithmetic.
4. **Funds.** acct-2 has about $3.14 left against the user's $125 figure; the ledger total for E.17 is $121.855498.
   No further purchase is possible without a top-up. The 10 fallback roots (YM, HG, 6S, 6J, 6A, 6B, 6N, ZM, ZW, 6C)
   would need $92.62 (x 1.03) for their 2010-2019 extension. Recommended: do not buy them for the base-rule batch;
   its verdict is final.
5. **The quote tool's ledger fallback (E.15)** is still unfixed for plans es2011 and ext2010. ext2010h sidesteps it
   with its own session id. Recommended: fix it in the next harness change (use only the current run's lines).
6. **The untracked ..env.swp** at the repo root is an editor swap file of .env and may hold the Databento keys. It was
   not read or committed. Recommended: delete it, or add `*.swp` to .gitignore, before any commit with `git add -A`.

## 8. Session cost

Wall clock 18:34 (2026-10-09) to 02:22 (2026-10-10) PDT. One break, not counted as work: the first Claude
session ended at about 19:38, taking the C1 buy process with it, and the next started at 19:41 (about 0:04, its own
row). No usage-limit pause.

### Final ETA table (actuals; PDT; the initial estimate in brackets)

| # | Task / spawn | Owner | Model | Effort | Start | End | Time [estimate] | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|---|
| 0-3 | Prompt and context, start checks, start suite, C1 and E.16 freeze verification, guard/A3/hash prep | lead | opus | xhigh | 18:34 | 18:54 | 0:20 [0:34] | lead | done; suite 6815 passed |
| 5 | Fresh C1 quote and guard | lead | opus | xhigh | 18:54 | 19:07 | 0:13 [0:08] | lead | done; $57.742330 |
| 6 | v11 edit, manifest, suite, commit a21d82d | lead | opus | xhigh | 19:07 | 19:29 | 0:22 [0:40] | lead | done; +line 196 (V11-R1) |
| 6r | HarnessReviewer-FableXHigh (v11) | worker-xhigh | fable | xhigh | 19:10 | 19:26 | 0:16 [0:25] | 1,548,942 | APPROVE |
| 7a | Register C1, buy 642 chunks | lead | opus | xhigh | 19:29 | 22:41 | 3:12 incl. the break [1:00-1:40] | lead | done; 17 s a chunk (estimate 10 s); resumed after the session end |
| - | Break: the Claude session ended; the next session resumed the buy | | | | 19:38 | 19:42 | 0:04 (not work) | | the orphan commit $0.075002 |
| 7b | Post-purchase checks, six stores, hash files, evaluation, commit 558a7ce | lead | opus | xhigh | 22:41 | 22:51 | 0:10 [1:10] | lead | STOPPED at C10 |
| 7v | VerdictVerifier-FableXHigh (C1's STOP) | worker-xhigh | fable | xhigh | 22:51 | 23:08 | 0:17 [0:45] | 4,489,321 | VERIFIED WITH NOTES |
| 8a | V12Coder-OpusXHigh | worker-xhigh | opus | xhigh | 22:51 | 23:16 | 0:25 [1:15] | 21,387,333 | done |
| 8b | HarnessReviewer-FableXHigh (v12; caps follow-up 00:07-00:12) | worker-xhigh | fable | xhigh | 23:18 | 00:12 | 0:17 + 0:05 [0:45] | 3,477,338 | APPROVE WITH FIXES, then APPROVE |
| 9 | ext2010h quote, guard, A3 selection, fallback list | lead | opus | xhigh | 23:36 | 00:03 | 0:27 [0:20] | lead | done; 11 roots |
| 8c | Caps, manifest, suite, commit d30f50c | lead | opus | xhigh | 00:04 | 00:30 | 0:26 [0:40] | lead | done; suite 6916 passed |
| 10 | Register E16-H1..H5 | lead | opus | xhigh | 00:30 | 00:30 | 0:01 [0:10] | lead | N 478 |
| 11 | Buy 933 chunks in 4 processes | lead | opus | xhigh | 00:30 | 01:27 | 0:56 [0:45] | lead | done; $64.038166 |
| 12 | Post-purchase checks, 11 stores, run manifest, dry check | lead | opus | xhigh | 01:27 | 01:31 | 0:04 [0:35] | lead | done |
| 13-14 | H1-H5 once each, verdict | lead | opus | xhigh | 01:31 | 01:40 | 0:09 [0:45] | lead | all five FAIL |
| 15 | VerdictVerifier-FableXHigh (H1-H5) | worker-xhigh | fable | xhigh | 01:40 | 02:03 | 0:23 [1:00] | 7,223,323 | H1-H4 VERIFIED, H5 WITH NOTES |
| 16 | Return drafts (parallel with 15), rulings, end checks, end suite, cost, progress, STAGES, final commit | lead | opus | xhigh | 01:41 | 02:22 | 0:41 [0:45] | lead | done |
| Total | Stage E.17 | lead + 5 spawns | | | 18:34 | 02:22 | 7:44 work, break excluded [about 11:00] | 163,370,316 | C1 STOPPED; H1-H5 FAIL |

### Tokens per model (session 0dcecb5d's transcript and its 5 subagent transcripts, 2026-10-10 01:30Z on; reports/stage_e10_briefs/cost.py)

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 3,022 | 288,913 | 15,329,973 | 1,117,016 | 16,738,924 |
| claude-opus-5-5 | 876 | 438,993 | 144,885,165 | 1,306,358 | 146,631,392 |
| all | 3,898 | 727,906 | 160,215,138 | 2,423,374 | 163,370,316 |

Delegation share: lead 125,244,059 (76.7%), workers 38,126,257 (23.3%); by model claude-fable-5-1 16,738,924 (10.2%), claude-opus-5-5 146,631,392 (89.8%).

Per transcript (model, messages, first and last UTC, input, output, cache read, cache creation, total):

    lead claude-opus-5-5 msgs=314 first=2026-10-10T01:34:08.287Z last=2026-10-10T09:21:23.106Z in=666 out=313985 cread=123945574 ccreate=983834 total=125244059
    agent-a092f29e8ebc7951d claude-fable-5-1 msgs=12 first=2026-10-10T02:10:49.954Z last=2026-10-10T02:26:19.186Z in=354 out=44850 cread=1334816 ccreate=168922 total=1548942
    agent-a3f9947473bd4761c claude-fable-5-1 msgs=34 first=2026-10-10T08:40:22.699Z last=2026-10-10T09:03:41.201Z in=1028 out=95212 cread=6838850 ccreate=288233 total=7223323
    agent-a463ba71418f7066b claude-opus-5-5 msgs=105 first=2026-10-10T05:51:32.236Z last=2026-10-10T06:16:19.631Z in=210 out=125008 cread=20939591 ccreate=322524 total=21387333
    agent-a6de7832a8ed6d053 claude-fable-5-1 msgs=34 first=2026-10-10T05:51:29.920Z last=2026-10-10T06:08:27.369Z in=1058 out=61010 cread=4230286 ccreate=196967 total=4489321
    agent-ab2dedb725a4e6538 claude-fable-5-1 msgs=21 first=2026-10-10T06:18:06.225Z last=2026-10-10T07:12:06.529Z in=582 out=87841 cread=2926021 ccreate=462894 total=3477338

These are token counts from the transcripts, not plan-credit percentages; the session cannot read the /usage meter.
