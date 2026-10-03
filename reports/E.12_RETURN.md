# Stage E.12 return: ML route v2 frozen, phase 1 bought, Gate 0 run once: FAIL

Lead Opus 5.5 xhigh, 2026-10-03 07:51 to 13:19 PDT. Prompt docs/prompts/STAGE_E.12.md. Times
are America/Vancouver. One mid-stage question to the user (the held stores, section 3, Task 6); the
user chose harness v9.

## 1. Verdict summary

**Gate 0: FAIL.** No product-horizon pair passes; v2 stops (V2.2b): no phase-2 purchase, no model.
- Best pair NG h60: mean gross 5.57 ticks against c 1.71 (3.25c, bar 1 met), t_B 2.51 (bar 2,
  t >= 3, fails), p 0.0062 against the Holm threshold 0.000183 (rank 1 of 273, not rejected),
  518 trades. NG hF: 7.9c, t 2.33. No pair reaches t >= 3.
- Pooled family B: mean gross -0.72 ticks against 2.26 ticks of cost, t 0.28, 39,997 trades.
  Family A: the smallest p is 0.015 (g07_range hF).
- Fable recomputed all 273 tests independently: agreement to about 1e-13, the same Holm
  decisions, VERIFIED WITH NOTES (no blocking or should-fix finding).

**Phase 1.** The frozen subset rule selected all 28 exposures (the planning guess was 8): 1,543
training-window chunks (2019-05..2024-02) for **$133.723742** (acct-1 $26.797773, acct-2
$106.925969; NG already owned). Billed equalled quoted on every chunk. MBT has no Gate 0 row (D4
start 2024-01-02, all 41 dates lost to warm-up); MES was excluded by the pre-registered P-1a.

**Funds left:** acct-1 $1.61 of headroom, acct-2 $18.07.

**Hashes:** v2 freeze commit 9466f2e, manifest a647cd06...; harness v8 452c4a51... (deccd17); harness
v9 7fd757f6... (4b1e81e, the user's mid-stage decision on 24 held closure bars).

**New program N: 198 + 273 = 471.**

**Phase 2** is not bought (Gate 0 failed). Quotes for the record: holdout-2 for the 28 price paths
$31.98; the 2010 extension $213.94. Top-up needed for both: $226.25.

## 2. Guardrail evidence

### Start (07:52 PDT), quoted verbatim (reports/stage_e12_briefs/start_checks.txt)

```
$ date
Sat Oct  3 07:52:17 PDT 2026
$ git status --short
?? reports/stage_e12_briefs/
$ git log --oneline -3
8b93e98 docs: Stage E.12 prompt (v2 freeze, phase 1, Gate 0) and V23
fbb4202 docs: Stage E.11 briefs, state, key-fix and signal-coverage reports
39738c3 Stage E.11 ML route v2 design draft and build
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
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected eee8a8b92a0210b245429135cf08b42f739b9328fa4eb49bf9034e5b387853d4
preflight OK: eee8a8b92a0210b245429135cf08b42f739b9328fa4eb49bf9034e5b387853d4
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
17400 ledger/databento_spend.jsonl
0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 91.592247 cap 120.00 headroom 28.407753
acct-2: spent 124.673761 cap 125.00 headroom 0.326239
```

Start pytest (07:52-08:13, run with PYTHONPYCACHEPREFIX): `3 failed, 6317 passed, 2 skipped, 2 xfailed`.
The 3 are test_harness_freeze bytecode tests that fail only under PYTHONPYCACHEPREFIX (E.11 saw the
same); rerun without it: `17 passed`. The start state is E.11's 6320 passing.

### After the purchase (11:58 PDT, harness v8), quoted verbatim (reports/stage_e12_briefs/postpurchase_checks.txt)

```
$ date
Sat Oct  3 11:58:47 PDT 2026
$ git status --short
 M ledger/databento_spend.jsonl
?? reports/stage_e12_STATE.md
?? reports/stage_e12_briefs/brief_calendarbuilder.md
?? reports/stage_e12_briefs/brief_freezereviewer.md
?? reports/stage_e12_briefs/brief_gate0verifier.md
?? reports/stage_e12_briefs/brief_keycapfix.md
?? reports/stage_e12_briefs/brief_marginfetch.md
?? reports/stage_e12_briefs/brief_phase1coder.md
?? reports/stage_e12_briefs/brief_topstepfacts.md
?? reports/stage_e12_briefs/brief_v23coder.md
?? reports/stage_e12_briefs/brief_v9coder.md
?? reports/stage_e12_briefs/build_ready_stores.py
?? reports/stage_e12_briefs/buy_acct1.log
?? reports/stage_e12_briefs/buy_acct2_g1.log
?? reports/stage_e12_briefs/buy_acct2_g2.log
?? reports/stage_e12_briefs/buy_acct2_g3.log
?? reports/stage_e12_briefs/calendar_pages/
?? reports/stage_e12_briefs/calendarbuilder_fetches.tsv
?? reports/stage_e12_briefs/calendarbuilder_log.md
?? reports/stage_e12_briefs/calendarbuilder_notes.txt
?? reports/stage_e12_briefs/checks.sh
?? reports/stage_e12_briefs/keycapfix_report.md
?? reports/stage_e12_briefs/margin_pages/
?? reports/stage_e12_briefs/marginfetch_log.md
?? reports/stage_e12_briefs/phase1_quotes_by_root.json
?? reports/stage_e12_briefs/phase1coder_report.md
?? reports/stage_e12_briefs/postpurchase_checks.txt
?? reports/stage_e12_briefs/pytest_mlv2_final.out
?? reports/stage_e12_briefs/pytest_mlv2_final.start
?? reports/stage_e12_briefs/pytest_mlv2_prefreeze.out
?? reports/stage_e12_briefs/pytest_mlv2_prefreeze.start
?? reports/stage_e12_briefs/pytest_prefreeze_full.out
?? reports/stage_e12_briefs/pytest_prefreeze_full.start
?? reports/stage_e12_briefs/pytest_start.out
?? reports/stage_e12_briefs/pytest_start.start
?? reports/stage_e12_briefs/pytest_start_harness_rerun.out
?? reports/stage_e12_briefs/pytest_v8.out
?? reports/stage_e12_briefs/quote_phase1.log
?? reports/stage_e12_briefs/start_checks.txt
?? reports/stage_e12_briefs/store_UB.log
?? reports/stage_e12_briefs/store_builds.log
?? reports/stage_e12_briefs/topstep_pages/
?? reports/stage_e12_briefs/topstepfacts_log.md
?? reports/stage_e12_briefs/v23coder_report.md
?? reports/stage_e12_briefs/v9coder_report.md
?? reports/stage_e12_quotes_phase1.json
?? reports/stage_e12_quotes_phase1.md
?? reports/stage_e12_ranking.json
?? reports/stage_e12_review.md
?? reports/stage_e12_rulings.md
?? reports/step2/bars_6A.json
?? reports/step2/bars_6B.json
?? reports/step2/bars_6C.json
?? reports/step2/bars_6E.json
?? reports/step2/bars_6J.json
?? reports/step2/bars_6N.json
?? reports/step2/bars_6S.json
?? reports/step2/bars_CL.json
?? reports/step2/bars_GC.json
?? reports/step2/bars_HE.json
?? reports/step2/bars_HG.json
?? reports/step2/bars_LE.json
?? reports/step2/bars_MBT.json
?? reports/step2/bars_NQ.json
?? reports/step2/bars_RTY.json
?? reports/step2/bars_TN.json
?? reports/step2/bars_UB.json
?? reports/step2/bars_YM.json
?? reports/step2/bars_ZB.json
?? reports/step2/bars_ZC.json
?? reports/step2/bars_ZF.json
?? reports/step2/bars_ZL.json
?? reports/step2/bars_ZM.json
?? reports/step2/bars_ZN.json
?? reports/step2/bars_ZS.json
?? reports/step2/bars_ZT.json
?? reports/step2/bars_ZW.json
?? reports/step2/purchase_6A.json
?? reports/step2/purchase_6B.json
?? reports/step2/purchase_6C.json
?? reports/step2/purchase_6E.json
?? reports/step2/purchase_6J.json
?? reports/step2/purchase_6N.json
?? reports/step2/purchase_6S.json
?? reports/step2/purchase_CL.json
?? reports/step2/purchase_GC.json
?? reports/step2/purchase_HE.json
?? reports/step2/purchase_HG.json
?? reports/step2/purchase_LE.json
?? reports/step2/purchase_MBT.json
?? reports/step2/purchase_NQ.json
?? reports/step2/purchase_RTY.json
?? reports/step2/purchase_TN.json
?? reports/step2/purchase_UB.json
?? reports/step2/purchase_YM.json
?? reports/step2/purchase_ZB.json
?? reports/step2/purchase_ZC.json
?? reports/step2/purchase_ZF.json
?? reports/step2/purchase_ZL.json
?? reports/step2/purchase_ZM.json
?? reports/step2/purchase_ZN.json
?? reports/step2/purchase_ZS.json
?? reports/step2/purchase_ZT.json
?? reports/step2/purchase_ZW.json
$ git log --oneline -3
deccd17 harness v8, acct-2 cap, key strip, training-window purchase
9466f2e ML route v2 freeze
8b93e98 docs: Stage E.12 prompt (v2 freeze, phase 1, Gate 0) and V23
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
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected 452c4a51ebfae33f6f18822c9b754634f1ce3ab879b88abe416633c75965a426
preflight OK: 452c4a51ebfae33f6f18822c9b754634f1ce3ab879b88abe416633c75965a426
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
23630 ledger/databento_spend.jsonl
e5862e3dd70ee0316ff1233359adfa7fe71f4415f61c85c31c6ad837f9c93976
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 231.599730 cap 249.67 headroom 18.070270
```

Training-window chunks on disk for the 27 bought roots: 1,543 (26 x 58 + MBT 35); chunks starting
in 2024-03..2025-03 (embargo and holdout-2): **0**; every purchase manifest ends at
range=2024-02-01_2024-03-01.

### End (13:19 PDT, harness v9), quoted verbatim (reports/stage_e12_briefs/end_checks.txt)

```
$ date
Sat Oct  3 13:19:03 PDT 2026
$ git status --short
 M ledger/databento_spend.jsonl
?? ledger/ml_v2_config_ledger.jsonl
?? reports/stage_e12_STATE.md
?? reports/stage_e12_briefs/assemble_return.py
?? reports/stage_e12_briefs/brief_calendarbuilder.md
?? reports/stage_e12_briefs/brief_freezereviewer.md
?? reports/stage_e12_briefs/brief_gate0verifier.md
?? reports/stage_e12_briefs/brief_keycapfix.md
?? reports/stage_e12_briefs/brief_marginfetch.md
?? reports/stage_e12_briefs/brief_phase1coder.md
?? reports/stage_e12_briefs/brief_topstepfacts.md
?? reports/stage_e12_briefs/brief_v23coder.md
?? reports/stage_e12_briefs/brief_v9coder.md
?? reports/stage_e12_briefs/build_ready_stores.py
?? reports/stage_e12_briefs/buy_acct1.log
?? reports/stage_e12_briefs/buy_acct2_g1.log
?? reports/stage_e12_briefs/buy_acct2_g2.log
?? reports/stage_e12_briefs/buy_acct2_g3.log
?? reports/stage_e12_briefs/calendar_pages/
?? reports/stage_e12_briefs/calendarbuilder_fetches.tsv
?? reports/stage_e12_briefs/calendarbuilder_log.md
?? reports/stage_e12_briefs/calendarbuilder_notes.txt
?? reports/stage_e12_briefs/checks.sh
?? reports/stage_e12_briefs/end_checks.txt
?? reports/stage_e12_briefs/gate0_run.log
?? reports/stage_e12_briefs/gate0_run.start
?? reports/stage_e12_briefs/gate0verifier/
?? reports/stage_e12_briefs/keycapfix_report.md
?? reports/stage_e12_briefs/margin_pages/
?? reports/stage_e12_briefs/marginfetch_log.md
?? reports/stage_e12_briefs/phase1_build.log
?? reports/stage_e12_briefs/phase1_build.start
?? reports/stage_e12_briefs/phase1_quotes_by_root.json
?? reports/stage_e12_briefs/phase1_register.log
?? reports/stage_e12_briefs/phase1coder_report.md
?? reports/stage_e12_briefs/postpurchase_checks.txt
?? reports/stage_e12_briefs/progress_entry.md
?? reports/stage_e12_briefs/pytest_end.out
?? reports/stage_e12_briefs/pytest_end.start
?? reports/stage_e12_briefs/pytest_end_rerun.out
?? reports/stage_e12_briefs/pytest_mlv2_final.out
?? reports/stage_e12_briefs/pytest_mlv2_final.start
?? reports/stage_e12_briefs/pytest_mlv2_prefreeze.out
?? reports/stage_e12_briefs/pytest_mlv2_prefreeze.start
?? reports/stage_e12_briefs/pytest_prefreeze_full.out
?? reports/stage_e12_briefs/pytest_prefreeze_full.start
?? reports/stage_e12_briefs/pytest_start.out
?? reports/stage_e12_briefs/pytest_start.start
?? reports/stage_e12_briefs/pytest_start_harness_rerun.out
?? reports/stage_e12_briefs/pytest_v8.out
?? reports/stage_e12_briefs/pytest_v9.out
?? reports/stage_e12_briefs/quote_ext2010.log
?? reports/stage_e12_briefs/quote_holdout2.log
?? reports/stage_e12_briefs/quote_phase1.log
?? reports/stage_e12_briefs/ret_delegation.md
?? reports/stage_e12_briefs/ret_open_choices.md
?? reports/stage_e12_briefs/return_draft.md
?? reports/stage_e12_briefs/start_checks.txt
?? reports/stage_e12_briefs/store_UB.log
?? reports/stage_e12_briefs/store_builds.log
?? reports/stage_e12_briefs/store_builds_v9.log
?? reports/stage_e12_briefs/topstep_pages/
?? reports/stage_e12_briefs/topstepfacts_log.md
?? reports/stage_e12_briefs/v23coder_report.md
?? reports/stage_e12_briefs/v9coder_report.md
?? reports/stage_e12_c_sigma.json
?? reports/stage_e12_gate0.json
?? reports/stage_e12_gate0.md
?? reports/stage_e12_gate0_list.json
?? reports/stage_e12_phase1_bars.json
?? reports/stage_e12_quotes_ext2010.json
?? reports/stage_e12_quotes_ext2010.md
?? reports/stage_e12_quotes_holdout2.json
?? reports/stage_e12_quotes_holdout2.md
?? reports/stage_e12_quotes_phase1.json
?? reports/stage_e12_quotes_phase1.md
?? reports/stage_e12_ranking.json
?? reports/stage_e12_review.md
?? reports/stage_e12_rulings.md
?? reports/step2/bars_6A.json
?? reports/step2/bars_6B.json
?? reports/step2/bars_6C.json
?? reports/step2/bars_6E.json
?? reports/step2/bars_6J.json
?? reports/step2/bars_6N.json
?? reports/step2/bars_6S.json
?? reports/step2/bars_CL.json
?? reports/step2/bars_GC.json
?? reports/step2/bars_HE.json
?? reports/step2/bars_HG.json
?? reports/step2/bars_LE.json
?? reports/step2/bars_MBT.json
?? reports/step2/bars_NQ.json
?? reports/step2/bars_RTY.json
?? reports/step2/bars_TN.json
?? reports/step2/bars_UB.json
?? reports/step2/bars_YM.json
?? reports/step2/bars_ZB.json
?? reports/step2/bars_ZC.json
?? reports/step2/bars_ZF.json
?? reports/step2/bars_ZL.json
?? reports/step2/bars_ZM.json
?? reports/step2/bars_ZN.json
?? reports/step2/bars_ZS.json
?? reports/step2/bars_ZT.json
?? reports/step2/bars_ZW.json
?? reports/step2/purchase_6A.json
?? reports/step2/purchase_6B.json
?? reports/step2/purchase_6C.json
?? reports/step2/purchase_6E.json
?? reports/step2/purchase_6J.json
?? reports/step2/purchase_6N.json
?? reports/step2/purchase_6S.json
?? reports/step2/purchase_CL.json
?? reports/step2/purchase_GC.json
?? reports/step2/purchase_HE.json
?? reports/step2/purchase_HG.json
?? reports/step2/purchase_LE.json
?? reports/step2/purchase_MBT.json
?? reports/step2/purchase_NQ.json
?? reports/step2/purchase_RTY.json
?? reports/step2/purchase_TN.json
?? reports/step2/purchase_UB.json
?? reports/step2/purchase_YM.json
?? reports/step2/purchase_ZB.json
?? reports/step2/purchase_ZC.json
?? reports/step2/purchase_ZF.json
?? reports/step2/purchase_ZL.json
?? reports/step2/purchase_ZM.json
?? reports/step2/purchase_ZN.json
?? reports/step2/purchase_ZS.json
?? reports/step2/purchase_ZT.json
?? reports/step2/purchase_ZW.json
$ git log --oneline -3
4b1e81e harness v9, L-3 closure-bar ruling path (user decision)
deccd17 harness v8, acct-2 cap, key strip, training-window purchase
9466f2e ML route v2 freeze
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
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected 7fd757f6d7c3990c2d20756c501f68b0541aa89851dcca9236badabd4f4a9bd9
preflight OK: 7fd757f6d7c3990c2d20756c501f68b0541aa89851dcca9236badabd4f4a9bd9
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
27018 ledger/databento_spend.jsonl
6a074c143670e241b0a383b2778661bbc60e39ec96c501000a4413176efeda4c
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 231.599730 cap 249.67 headroom 18.070270
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
```

End pytest (without PYTHONPYCACHEPREFIX): `6 failed, 6499 passed, 2 skipped, 3 xfailed in 1314.74s (12:17-12:39); the 6 are the real-ledger guard (tests/test_e2b_pull_step2.py x4, test_e2b_pull_step2_e12.py x1, test_pull_universe.py x1), tripped by the concurrent Task 7 quote run appending to ledger/databento_spend.jsonl; the three files rerun after the quotes finished: 155 passed (pytest_end_rerun.out). End state: 6,505 passing`.

## 3. Results per task

### Task 0: startup
All start checks passed (above). HEAD 8b93e98 (the prompt commit), clean tree, v7 preflight OK.

### Task 1: V23 applied (design: lead; code: V23Coder, Phase1Coder)
- Design (docs/STAGE_E_ML_V2_DESIGN.md): every V2.12 item marked decided with V23 cited; only item
  18 open. Gross reading the built default (hurdles 1.5c/2c/3c), tau 0.167 with its derivation,
  Gate 0 at 1.5c with family A in the Holm family, the canary semantics rewritten for the gross
  reading; the release-window rule in V2.8 (lead rule P-5: counted with the entry, refused above
  half the tier); the 1.5 x slippage must-survive in the holdout-2 registration; deployment (a);
  the unused research-window Holm slot with V23 cited; the phase-1 test list (P-1 to P-3).
- Code (V23Coder): COST_GATE_READING "gross", C_SIGMA_TAU 0.167, N_PROGRAM_AT_FREEZE 198, the
  release-window rule in the portfolio, selection metric, engine portfolio and both payout
  re-sizing paths, the K9-anncday-01 flag k9_anncday, the Gate 0 canaries under the new defaults
  (noise fails, a planted gross edge passes, 1.0c-1.5c fails, [1.5c, 2.5c) passes; the literal
  reading's case kept with the reading pinned). ml_v2 suite 704 -> 791 passed.
- Real-data entry point (Phase1Coder; not named in the prompt, needed so Gate 0 code was frozen
  before any data): ml_route_v2/phase1 (build, register, run): the frozen store loaders, D4 S_X per
  price path, coverage rule P-1, MES contingency P-1a, the P-2 list, the run-once guard, the
  list-hash check, the v2 freeze check and the harness preflight before every step. 50 tests.
- Lead edits: ACCOUNT_150K's 150K scaling plan and MLL comment, PAYOUT_RESET_DELAY_DATES = 2.
- Final ml_v2 suite before the freeze: `803 passed, 2 xfailed`.

### Task 2: freeze inputs
- 2a CME margins (MarginFetch): live CME refused automated access (HTTP 403 citing its terms); only
  stale Wayback figures for 25 of 34 symbols; 5 vehicles (MNQ, M2K, MYM, MCL, NG) had none. More
  than a few, so the whole ranking used the frozen E|m_1| (V23 item 3's fallback; design V2.1
  step 6). reports/stage_e12_cme_margins.json kept as the record; its figures are unused.
- 2b Topstep 150K (TopstepFacts): MLL $4,500 confirmed; scaling plan from the page image: 3 lots
  below $1,500, 4 from $1,500, 5 above $2,000, 10 above $3,000, 15 above $4,500 (a balance exactly
  on a boundary takes the lower tier); Combine $199/month (Standard) or $229 (No Activation Fee),
  reset the same, activation $149 (Standard); Back2Funded $829; "as few as two days" to pass.
  reports/stage_e12_topstep_150k.md.
- 2c EC-K9 2019-2024 (CalendarBuilder): 240 dates (FOMC 38, NFP 58, GDP 38, ISM 58, inflation
  58), 884 CAL-E12 source rows from the Fed, BLS, BEA and ISM pages, no uncovered span; FOMC, NFP,
  CPI and PPI match the frozen release calendar exactly; the method reproduces the frozen
  research-window rows exactly. Unscheduled FOMC actions and the cancelled 2020-03-18 statement day
  excluded (not known at the entry intent). reports/stage_e12_ec_k9_2019_2024.json/.md.

### Task 3: the v2 freeze
- Fable reviewed the uncommitted freeze (0 blocking, 4 should-fix, 9 notes); all accepted fixes
  were applied before the commit and the manifest rebuilt once (the first was never committed).
- Commit **9466f2e "ML route v2 freeze"** (09:25:53): the design marked FROZEN, the manifest
  reports/stage_e12_ml_v2_freeze.json (91 files: the design, every ml_route_v2 file, the ml_v2 tests
  and fixtures, the cost wall, the margin attempt, the Topstep file, the EC-K9 files and the other
  frozen inputs; sha256 **a647cd06c8f71f9549c0afa1c740bc32bad05e8f83ed57c87642a1586a0cad5b**), the
  Task 1 code and tests, the Task 2 files, the ranking script and the manifest builder.
- Universe table regenerated from cost_wall.json: all 28 rows match (clusters, paths, tick values
  and ticks exactly; the RT_X $ display to the cent).
- Program N read at the freeze: 198 (E.9; E.10 and E.11 added nothing); no machine-readable N
  ledger exists, so it was read from the stage records, cited in the manifest.

### Task 4: harness v8 (KeyCapFix prepared it in a worktree; lead committed)
- ACCOUNT_2_CAP_USD 125.00 -> **249.67** (acct-2 ledger spend 124.673761 + the $125.00 top-up,
  rounded down to the cent); C-10: the key is returned stripped, docs/ACCESS.md names
  DATABENTO_API_KEY1 and DATABENTO_API_KEY2; the E.12 spend block (session cap $137.73 = the fresh
  quote of the subset $133.723742 x 1.03, under the combined headroom $153.403992; request cap
  $3.00); pull_step2 --account, --roots, --training-window (ends at range=2024-02-01_2024-03-01,
  refuses later chunks, required for --buy), quote-only --holdout2-only and --extension-2010.
- v8 sha256 **452c4a51ebfae33f6f18822c9b754634f1ce3ab879b88abe416633c75965a426**; diff against v7:
  data/config.py, data/pull_step2.py, tests/test_e2b_pull_step2.py changed, two test files added.
  No data/config.py name the phase-1 path imports changed (review F-4). Harness tests 241 passed.
  Commit **deccd17** (10:02:53).

### Task 5: quote, rank and buy
- Fresh quote (09:27-09:58, ledgered at $0.00 under stage-E.12-2026-10-03): 1,601 chunks, 0 failed,
  $139.340240 for the 28 price paths' training windows (reports/stage_e12_quotes_phase1.json).
- Ranking (reports/stage_e12_ranking.json, sha256 43f80e90...; lead rule P-4, E|m_1| proxy):

Median vehicle ADV (YTD 2026): 199,052; headroom at start acct-1 $28.407753, acct-2 $124.996239.

| Rank | Vehicle | Path | Cl | Tier | c $ | E\|m_1\| $ | c/proxy | Quote $ | Pass | Account | acct-1 / acct-2 left after (3% reserved) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | MNQ | NQ | K1 | 1 | 2.71 | 363.5 | 0.0074 | 6.225245 | 1 | acct-1 | 21.995751 / 124.996239 |
| 2 | MGC | GC | K5 | 1 | 5.60 | 258.6 | 0.0216 | 6.165708 | 1 | acct-1 | 15.645072 / 124.996239 |
| 3 | NG | NG | K4 | 1 | 24.08 | 639.3 | 0.0377 | 0.000000 | 1 | acct-1 | 15.645072 / 124.996239 |
| 4 | 6E | 6E | K3 | 1 | 14.41 | 319.5 | 0.0451 | 6.133537 | 1 | acct-1 | 9.327529 / 124.996239 |
| 5 | MCL | CL | K4 | 1 | 4.35 | 91.6 | 0.0475 | 6.195907 | 2 | acct-2 | 3.283495 / 112.822647 |
| 6 | ZL | ZL | K6 | 1 | 16.05 | 304.8 | 0.0527 | 3.971287 | 1 | acct-1 | 5.237103 / 124.996239 |
| 7 | ZS | ZS | K6 | 1 | 20.55 | 304.4 | 0.0675 | 4.183993 | 2 | acct-2 | 3.283495 / 108.513135 |
| 8 | UB | UB | K2 | 1 | 35.03 | 501.4 | 0.0699 | 5.623114 | 1 | acct-2 | 5.237103 / 119.204432 |
| 9 | TN | TN | K2 | 1 | 19.30 | 259.9 | 0.0742 | 5.381340 | 2 | acct-2 | 3.283495 / 102.970355 |
| 10 | ZF | ZF | K2 | 1 | 10.26 | 135.5 | 0.0757 | 5.723536 | 2 | acct-2 | 3.283495 / 97.075113 |
| 11 | ZB | ZB | K2 | 1 | 35.06 | 402.1 | 0.0872 | 5.605258 | 2 | acct-2 | 3.283495 / 91.301698 |
| 12 | ZN | ZN | K2 | 1 | 18.28 | 204.9 | 0.0892 | 5.924931 | 2 | acct-2 | 3.283495 / 85.199019 |
| 13 | ZT | ZT | K2 | 1 | 10.34 | 112.7 | 0.0917 | 4.848968 | 2 | acct-2 | 3.283495 / 80.204581 |
| 14 | ZC | ZC | K6 | 1 | 18.70 | 158.2 | 0.1182 | 3.876783 | 2 | acct-2 | 3.283495 / 76.211495 |
| 15 | MYM | YM | K1 | 2 | 3.76 | 131.1 | 0.0287 | 6.195283 | 2 | acct-2 | 3.283495 / 69.830354 |
| 16 | M2K | RTY | K1 | 2 | 3.17 | 106.1 | 0.0299 | 6.009162 | 2 | acct-2 | 3.283495 / 63.640917 |
| 17 | LE | LE | K6 | 2 | 24.98 | 707.2 | 0.0353 | 1.207669 | 2 | acct-1 | 2.039597 / 63.640917 |
| 18 | MBT | MBT | K7 | 2 | 5.43 | 120.6 | 0.0450 | 1.896707 | 1 | acct-1 | 3.283495 / 119.204432 |
| 19 | MHG | HG | K5 | 2 | 6.27 | 110.2 | 0.0569 | 5.989430 | 2 | acct-2 | 2.039597 / 57.471804 |
| 20 | 6S | 6S | K3 | 2 | 24.89 | 410.8 | 0.0606 | 4.998019 | 2 | acct-2 | 2.039597 / 52.323845 |
| 21 | HE | HE | K6 | 2 | 19.65 | 323.0 | 0.0608 | 1.197622 | 2 | acct-1 | 0.806047 / 52.323845 |
| 22 | 6J | 6J | K3 | 2 | 13.14 | 204.8 | 0.0641 | 6.093240 | 2 | acct-2 | 0.806047 / 46.047808 |
| 23 | 6A | 6A | K3 | 2 | 12.38 | 183.7 | 0.0674 | 6.026233 | 2 | acct-2 | 0.806047 / 39.840788 |
| 24 | 6B | 6B | K3 | 2 | 12.69 | 186.2 | 0.0681 | 5.821807 | 2 | acct-2 | 0.806047 / 33.844326 |
| 25 | 6N | 6N | K3 | 2 | 13.10 | 156.5 | 0.0837 | 5.366412 | 2 | acct-2 | 0.806047 / 28.316922 |
| 26 | ZM | ZM | K6 | 2 | 17.91 | 212.6 | 0.0842 | 3.568317 | 2 | acct-2 | 0.806047 / 24.641555 |
| 27 | ZW | ZW | K6 | 2 | 21.18 | 234.7 | 0.0902 | 3.711048 | 2 | acct-2 | 0.806047 / 20.819176 |
| 28 | 6C | 6C | K3 | 2 | 11.07 | 120.3 | 0.0920 | 5.783189 | 2 | acct-2 | 0.806047 / 14.862491 |

Subset: all 28; total $133.723742 (acct-1 $26.797773, acct-2 $106.925969); no skips. (Pass 1 = the seven cluster-best in rank order; pass 2 = the rest.)

- Every pick fitted (3% reserved per pick): the subset is all 28.
- Buy (10:03-11:57): four processes over disjoint roots (acct-1: NQ GC 6E ZL MBT LE HE; acct-2 in
  three groups), each through data.pull_step2 --buy --training-window with the v8 sha256. 1,543
  commits, 1,543 settles, **every settle delta $0.00** (billed = quoted), 0 refusals. Spend:
  acct-1 $26.797773 (now 118.390020 of 120.00), acct-2 $106.925969 (now 231.599730 of 249.67);
  session $133.723742 under its $137.73 cap.

### Task 6: bars, filter and Gate 0
- Stores: 15 built under v8. The v8 builder held 12 roots "for the lead (ruling L-3)": 24 bars
  inside a scheduled closure beyond the close minute, each the last minute before a 15:30, 17:00 or
  08:30 CT reopen on a 2020 quarter- or month-end date (NQ 6, RTY 5, YM 4; 6E 6S 6J 6A 6B 6N 6C 1
  each; LE, HE 1 each). The builder has no path to apply a ruling, so the choice (harness v9, or
  drop the roots under F-3, or wait) was a guardrail conflict and an irreversible either-way
  decision: the lead asked the user, who chose **harness v9: keep and flag**. V9Coder built the
  enumerated ruling path (reports/stage_e12_closure_rulings.json, 24 entries) and proved the frozen
  loader reads such stores; v9 sha256 **7fd757f6d7c3990c2d20756c501f68b0541aa89851dcca9236badabd4f4a9bd9**,
  commit **4b1e81e** (12:05:01); the 12 stores built under v9. All 28 stores exist.
- Build (12:09-12:14, v9 + the freeze manifest): 28 vehicles; MES store refused by the frozen loader
  (TradeDateMismatch, 3 rows labelled 2020-03-30, booked 2020-03-31), so P-1a excluded g17_mes,
  k8_flight_ret and k8_flight_tail: 64 signals; calendar 1,248 trade dates; 68,138 panel rows; D4
  S_X: 2019-05-06 for 25 paths, ZF 2020-10-01, ZT 2021-10-01, MBT 2024-01-02 (41 dates, no row after
  warm-up). Vendor-degraded dates flagged and kept (5 per path).
- c/sigma filter (tau 0.167, volatility only): 81 pairs, **81 admissible, 0 dropped**; ratios
  0.009 to 0.140 (largest ZN h60). reports/stage_e12_c_sigma.json.
- List registered **12:15:25** before any statistic: reports/stage_e12_gate0_list.json sha256
  **53e7ef576feba9959360b52a633b793175bce98d62a839fefa0f41baf19fa8ea**, |A| 192, |B| 81, 273
  entries in ledger/ml_v2_config_ledger.jsonl; the hash written to the STATE file first.
- Gate 0 ran **once**, 12:15:41-12:15:54. Verdict **FAIL**. reports/stage_e12_gate0.json (sha256
  c0af61c2...) and .md (363c5676...). Family B, the eight pairs with the largest t_B:

| Pair | Mean gross (ticks) | c (ticks) | Mean / c | t_B | p (one-sided) | Trades | Holm rank | Holm threshold | Rejected |
|---|---|---|---|---|---|---|---|---|---|
| NG h60 | 5.569 | 1.713 | 3.25 | 2.51 | 6.20e-03 | 518 | 1 | 1.83e-04 | False |
| NG hF | 13.921 | 1.766 | 7.88 | 2.33 | 1.03e-02 | 494 | 2 | 1.84e-04 | False |
| ZN hF | 1.039 | 1.168 | 0.89 | 1.41 | 7.90e-02 | 571 | 18 | 1.95e-04 | False |
| 6J hF | 3.494 | 1.944 | 1.80 | 1.40 | 8.19e-02 | 490 | 19 | 1.96e-04 | False |
| ZC h60 | 1.138 | 1.427 | 0.80 | 1.39 | 8.30e-02 | 558 | 20 | 1.97e-04 | False |
| ZF h120 | 1.113 | 1.299 | 0.86 | 1.23 | 1.10e-01 | 379 | 27 | 2.02e-04 | False |
| ZF hF | 0.963 | 1.298 | 0.74 | 1.18 | 1.20e-01 | 374 | 29 | 2.04e-04 | False |
| LE h120 | 1.727 | 2.366 | 0.73 | 1.07 | 1.42e-01 | 520 | 32 | 2.07e-04 | False |

  Eight pairs clear 1.5c (6J hF, HE hF, NG h60/h120/hF, UB h60, ZS hF, ZT hF), all with t_B <= 2.51.
  Pooled B: mean gross -0.717 ticks, cost 2.260, t 0.28, 39,997 trades on 1,067 dates. Family A:
  no test near Holm (smallest p 0.015, g07_range hF, t -2.43); the descriptive rank ICs are in the
  JSON beside each test.
- **New program N = 198 + 273 = 471.**

### Task 7: free quotes for later phases (ledgered at $0.00, nothing bought)

| Item | Chunks | Quoted | Notes |
|---|---|---|---|
| Phase 2, training window of exposures not bought in phase 1 | 0 | $0.00 | none: phase 1 bought all 28 |
| Holdout-2 chunks 2024-03..2025-03, 28 price paths | 364 (0 failed) | $31.984359 | NG's are owned and sealed (E.5); sealed on arrival if ever bought |
| Research-window bars of price-path contracts not owned | 0 | $0.00 | all 28 owned since E.1 |
| 2010 extension 2010-01..2019-04, 27 price paths (MBT skipped) | 3024 (292 unpriced, before listing) | $213.942963 | roots with unpriced months: {'NQ': 6, 'RTY': 89, 'YM': 6, 'ZT': 6, 'ZF': 6, 'ZN': 6, 'TN': 52, 'ZB': 6, 'UB': 6, '6E': 6, '6A': 6, '6B': 6, '6C': 6, '6J': 6, '6S': 6, '6N': 6, 'CL': 6, 'NG': 6, 'GC': 6, 'HG': 6, 'ZC': 6, 'ZW': 6, 'ZS': 6, 'ZM': 6, 'ZL': 6, 'HE': 7, 'LE': 6} |

Funds left: acct-1 $1.609980, acct-2 $18.070270 (combined $19.680250). Top-up needed: holdout-2 $12.30; 2010 extension $194.26; both $226.25 (each before the 3% margin). None is planned: Gate 0 failed.

## 4. Delegation record

One row per spawn (times PDT from the transcripts; tokens = input + output + cache read + cache creation,
from reports/stage_e10_briefs/cost.py over this session's subagent transcripts; never estimated).

| Agent (description) | Agent file | Model | Effort | Start-end | Wall | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|
| Phase1Coder-OpusXHigh | worker-xhigh | opus | xhigh | 08:07-09:20 | 73 min span (3 rounds) | 40,564,718 | done: ml_route_v2/phase1, 50 tests; not in the prompt's plan (the real-data entry point Gate 0 needed before the freeze); follow-up 1 (MES contingency P-1a, 08:42-08:45) and follow-up 2 (review F-2, F-3, F-8, 09:16-09:20) by SendMessage |
| V23Coder-OpusXHigh | worker-xhigh | opus | xhigh | 08:07-08:44 | 37 min | 31,107,511 | done: V23 defaults, release-window rule, K9 signal, canaries; ml_v2 704 -> 791; edited targets.py, simulate.py, test_ml_v2_cpcv.py outside its list (ruled) |
| MarginFetch-OpusHigh | worker-high | opus | high | 08:07-08:26 | 19 min | 5,975,264 | done: live CME 403 per its terms; stale Wayback for 25/34; ranking switched to E\|m_1\| |
| CalendarBuilder-OpusHigh | worker-high | opus | high | 08:07-08:56 | 48 min | 25,275,373 | done: EC-K9 2019-2024, 240 dates, 884 source rows, cross-checks exact |
| TopstepFacts-OpusMedium | worker-medium | opus | medium | 08:26-08:29 | 3 min | 2,130,037 | done: 150K MLL, scaling plan from the image, prices |
| KeyCapFix-OpusXHigh | worker-xhigh | opus | xhigh | 08:30-09:02 | 33 min | 20,723,465 | done in a git worktree in parallel with the freeze (the prompt had Task 4 after Task 3; the commit order was kept) |
| FreezeReviewer-FableXHigh | worker-xhigh | fable | xhigh | 08:57-09:15 | 18 min | 1,899,346 | done before the freeze commit: 0 blocking, 4 should fix, 9 notes; its commit-order check moved to Gate0Verifier |
| V9Coder-OpusXHigh | worker-xhigh | opus | xhigh | 10:41-10:55 | 14 min | 8,016,802 | done in a second worktree: the v9 closure-ruling path after the user's decision (not in the prompt's plan); loader check passed |
| Gate0Verifier-FableXHigh | worker-xhigh | fable | xhigh | 12:17-12:37 | 20 min | 4,383,294 | done: VERIFIED WITH NOTES (273 tests to 1e-13), plus the v9, MES, MBT and order-of-events checks |

Fable ran two checks, as the prompt's usage note asks (the v9 review was folded into the Gate 0
verification rather than a third Fable spawn). At most four workers ran at once.

## 5. Verification

Freeze review (FreezeReviewer-FableXHigh, before the commit; reports/stage_e12_review.md Part 1): 0
BLOCKING, 4 SHOULD FIX, 9 NOTE. Gate 0 verification (Gate0Verifier-FableXHigh; Part 2): VERIFIED
WITH NOTES, 0 BLOCKING, 0 SHOULD FIX, 5 NOTE. Rulings in reports/stage_e12_rulings.md.

| Id | Grade | Finding (short) | Ruling and fix |
|---|---|---|---|
| F-1 | SHOULD FIX | ranking reserved the quote, not quote x 1.03 | fixed before the commit |
| F-2 | SHOULD FIX | phase-1 CLI took operator paths for its checks | canonical paths only (Phase1Coder) |
| F-3 | SHOULD FIX | build --vehicles a free input | vehicles derived from the ranking and the stores |
| F-4 | SHOULD FIX | v8 must not change config names on the phase-1 path | verified from the v8 diff |
| F-5..F-13 | NOTE | counts, fixtures hash, phase-2 code items, freeze.py check, manifest wording, inputs not yet existing, proxy record, reset lower bound, K9 R-12 | applied or noted before the commit |
| N-1 | NOTE | c(p,h) built as the mean of max(long, short), design says "the mean round trip" | documentation; no admissibility change either way; next design edit |
| N-2 | NOTE | CPCV blocks cut on the calendar from 2019-05-06 | V2.9 as written |
| N-3 | NOTE | the verifier saw the lead's headline numbers (STATE grep) before finishing | disclosed; all 273 tests recomputed by its own code, agreement 1e-13 |
| N-4 | NOTE | v9 did change data/step2_store.py, imported on the read path (build side only) | wording corrected in the rulings |
| N-5 | NOTE | MBT's V_ref comes from research-window medians the verifier may not read | noted |

Key numbers, Fable vs lead: admissible 81 | 81; NG h60 mean g 5.56950 | 5.56950, c 1.71288 |
1.71288, t_B 2.51434 | 2.51434, p 0.006201 | 0.006201, 518 | 518 trades, Holm rank 1/273 not
rejected | same; pooled t 0.2807 | 0.2807; three seeded family A tests to 3e-13; 20/20 targets from
the bars exact. Order of events confirmed strictly increasing: freeze 09:25:53 < v8 10:02:53 < first
purchase commit 10:03:54 < v9 12:05:01 < last list registration 12:15:25 < Gate 0 result 12:15:54.

## 6. Open choices (decisions the lead made on its own, with the reason)

1. **Built a real-data entry point (ml_route_v2/phase1) and froze it before any data.** The prompt
   assumed the pipeline could run Gate 0 on real bars; it ran on synthetic worlds only. Writing the
   loader after the purchase would have meant code written after data.
2. **Lead rules fixed before any spawn (P-1 to P-6)**: coverage (a signal whose leg is not owned is
   no feature), the Gate 0 list (A = every computed signal x 3, dead tests kept and counted: the
   conservative choice for Holm and N), S_X by D4's frozen rule (it reads research-store volume only,
   never a price), the subset rule's application (pass 1 = exactly the seven cluster-best, the
   literal reading; acct-1 first; 3% reserved per pick), the release-window rule counting the entry
   (it refuses every case the plain wording refuses and keeps D9.5's purpose), N_program 198 read
   from the stage records (no machine-readable N ledger exists).
3. **MES contingency P-1a**, added before the freeze because no Stage E loader had read MES's
   confirmation store. It fired: MES was refused (3 mislabelled rows), and 3 signals left the panel.
4. **The whole ranking on E|m_1|.** Live CME refused automated access, citing its terms, and 5
   vehicles had no 2026 figure anywhere; the prompt's failure path. The margin file is kept as the
   record only (its figures are unused; CME's terms argue against using even archived copies).
5. **150K tier boundaries** at exactly $2,000, $3,000 and $4,500 take the lower tier (the page is
   silent; conservative); $1,500 opens the 4-lot tier as XFA_50K encodes the same label. **Reset
   delay 2 trade dates** (Topstep's stated minimum; a lower bound); reset cost reported at both
   paths; Back2Funded not modelled.
6. **EC-K9**: unscheduled FOMC actions and the cancelled 2020-03-18 statement day excluded (not
   known at the member's entry intent, catalog R-07).
7. **Freeze review before the freeze commit**, so its fixes could not be a Gate 0 rule change after
   the commit; the first manifest (never committed) was deleted and rebuilt once. The review's
   commit-order item went to Gate0Verifier.
8. **v8 prepared in a git worktree in parallel** with the freeze, and the fresh quote run (which
   needs no harness preflight) before the v8 commit, so the session cap could be written into v8 as
   the prompt asks. Commit order kept: freeze, then v8, then the purchase.
9. **The freeze commit also holds** reports/stage_e12_briefs/rank_phase1.py (hashed by the manifest)
   and build_v2_freeze.py (the manifest's builder).
10. **Tests run without PYTHONPYCACHEPREFIX** (three harness bytecode tests fail under it, as in
    E.11). The end suite's 6 failures were all the real-ledger guard, tripped by the Task 7 quote run
    appending to the ledger during the suite; those files were rerun after the quotes finished.
11. **The purchase in four parallel processes** over disjoint roots (E.5's 9.6 s per chunk x 1,543
    chunks would have taken about 4 h serially); each process's quote, authorize and commit go
    through the gate; the caps could not be crossed (planned $133.72 against a $137.73 session cap).
12. **The subset is all 28** because the frozen rule found every exposure fitted the funds (about $6
    per full-size root); no phase-2 training-window item remains.
13. **The held stores went to the user** (AskUserQuestion), not decided by the lead: applying L-3
    needed a harness change beyond v8 (a guardrail) and dropping the roots would have been
    irreversible for the single Gate 0 run. The ruling file was written from the builder's own held
    summaries (24 bars, exactly), after every root had been attempted.
14. **Stores built as purchases completed** (build_ready_stores.py), 15 under v8 and 12 under v9;
    the phase-1 build reads both (their summaries carry their own harness sha256).
15. **Destructive git commands avoided**: a second worktree was added for v9 instead of resetting
    the first (the hook refused the reset). Both worktrees (../PropExperiment-e12-v8, -v9) are left
    for the user to remove (`git worktree remove`); nothing in them is needed.
16. **STATE times before 08:53 were lead guesses**, corrected from file times and transcripts.
17. **A context-hygiene slip**: one directory listing printed about 400 file names into the lead's
    context; no data rows were read.
18. **The raw CME margin captures (reports/stage_e12_briefs/margin_pages/, 14 MB) are not committed**:
    CME's terms forbid scraping and AI use of its website data; the figures are unused, and the log
    (marginfetch_log.md, with each page's URL and sha256) and reports/stage_e12_cme_margins.json are
    committed as the record. The pages stay on disk.

## 7. Decisions for the user (Gate 0 FAILED)

**What v2's stop means.** Under the frozen V2.2b, a Gate 0 fail ends ML route v2: no phase-2
purchase (holdout-2, 2010 extension), no V2.6 selection, no model, no holdout-2 registration, no
paper trading. The 273 tests stay in N (471). The bought training stores remain on disk; reusing them
for a new hypothesis would need a new pre-registration that counts N = 471. V2.12 item 18 becomes
moot until there is a model.

1. **Accept the stop (recommended).** Gate 0 asked the cheapest question (is there any gross edge
   at 1.5x cost, t >= 3, after Holm, on 27 products and 64 signals over 4.8 years), and the answer
   is no. The best pair (NG h60, t 2.51) is not evidence after Holm, and choosing NG now would be
   selection on the same data. Do not re-run Gate 0, relax its bar, or buy phase 2.
2. **V22's personal-account path.** It moves a working model from XFAs to a personal account. With
   no model there is nothing to move, and funding a personal micro account now would trade without
   an edge. Recommendation: do not fund it on v2; revisit only if another route produces an edge
   that clears a pre-registered bar.
3. **The AiTrader readout** (the sibling project's Stage C: a one-shot, pre-registered evaluation of
   its news-judgment signal, not started, gated on its collection's Stage B exit). It is a different
   information source from price-based signals, so v2's null does not predict it. Recommendation:
   make it the program's next live question, run when its exit gate is met; keep PropExperiment
   paused rather than open a new price-based search, since 471 trials and 9 screened clusters plus
   v2 have found nothing that survives.
4. **The unspent funds** (acct-1 $1.61, acct-2 $18.07): no use under v2; leave them.
5. **Harness v9** (the user's decision): stays in force; the ruling file is a frozen input. No
   action, recorded for completeness.

## 8. Session cost

### Final ETA table (actuals; PDT)

| # | Task or spawn | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Startup checks, reading, plan, briefs | lead | opus | xhigh | 07:51 | 08:06 | 0:15 | (lead) | done; estimate 0:35 |
| 1a | V23 design text | lead | opus | xhigh | 08:10 | 08:56 | 0:46 | (lead) | done |
| 1b | Phase1Coder-OpusXHigh | worker-xhigh | opus | xhigh | 08:07 | 09:20 | 1:13 span | 40,564,718 | done (3 rounds); unplanned task |
| 1c | V23Coder-OpusXHigh | worker-xhigh | opus | xhigh | 08:07 | 08:44 | 0:37 | 31,107,511 | done |
| 2a | MarginFetch-OpusHigh | worker-high | opus | high | 08:07 | 08:26 | 0:19 | 5,975,264 | done; CME blocked |
| 2c | CalendarBuilder-OpusHigh | worker-high | opus | high | 08:07 | 08:56 | 0:49 | 25,275,373 | done |
| 2b | TopstepFacts-OpusMedium | worker-medium | opus | medium | 08:26 | 08:29 | 0:03 | 2,130,037 | done |
| 4p | KeyCapFix-OpusXHigh (worktree) | worker-xhigh | opus | xhigh | 08:30 | 09:02 | 0:32 | 20,723,465 | done |
| 3 | Freeze manifest, review fixes, commit 9466f2e | lead | opus | xhigh | 08:56 | 09:26 | 0:30 | (lead) | done |
| 8a | FreezeReviewer-FableXHigh (before the commit) | worker-xhigh | fable | xhigh | 08:57 | 09:15 | 0:18 | 1,899,346 | done |
| 4 | v8 merge, fresh quote, ranking, caps, commit deccd17 | lead | opus | xhigh | 09:27 | 10:03 | 0:36 | (lead) | done |
| 5 | Buy 1,543 chunks (4 processes) | lead | opus | xhigh | 10:03 | 11:57 | 1:54 | (lead) | done; estimate 1:00 |
| 6a | Stores (v8), the held-store question, ruling file, v9 commit 4b1e81e, stores (v9) | lead | opus | xhigh | 10:21 | 12:08 | overlaps 5 | (lead) | done; user decision |
| 6v | V9Coder-OpusXHigh (worktree) | worker-xhigh | opus | xhigh | 10:41 | 10:55 | 0:14 | 8,016,802 | done; unplanned |
| 6b | Build, register, Gate 0 once | lead | opus | xhigh | 12:09 | 12:16 | 0:07 | (lead) | done: FAIL |
| 8b | Gate0Verifier-FableXHigh | worker-xhigh | fable | xhigh | 12:17 | 12:37 | 0:20 | 4,383,294 | done: VERIFIED WITH NOTES |
| 7 | Later-phase quotes (holdout-2, 2010 extension) | lead | opus | xhigh | 12:15 | 13:16 | 1:01 background | (lead) | done |
| 9 | Rulings, return, end checks, progress, commit | lead | opus | xhigh | 12:37 | 13:19 | | (lead) | done |
| | **Stage total** | | | | 07:51 | 13:19 | about 5:30 work | 288,183,688 (to 13:19) | initial estimate: end 16:40 (8:50) |

Pauses: none. The question to the user (about 10:41) was answered at once; there was no usage-limit
wait. The purchase (1:54) and the extension quote (1:01) were the long waits; the 1,543-chunk buy ran
in four processes to stay near 2 h instead of about 4 h.

### Tokens per model (this session's transcript and its 9 subagent transcripts, 07:51 to 13:19 PDT)

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-opus-5-5 | 2,046 | 1,086,322 | 277,732,573 | 3,080,107 | 281,901,048 |
| claude-fable-5-1 | 1,222 | 146,103 | 5,632,322 | 502,993 | 6,282,640 |
| all | 3,268 | 1,232,425 | 283,364,895 | 3,583,100 | 288,183,688 |

Per spawn (agent file, model, effort, tokens): Phase1Coder worker-xhigh opus xhigh 40,564,718;
V23Coder worker-xhigh opus xhigh 31,107,511; CalendarBuilder worker-high opus high 25,275,373;
KeyCapFix worker-xhigh opus xhigh 20,723,465; V9Coder worker-xhigh opus xhigh 8,016,802;
MarginFetch worker-high opus high 5,975,264; Gate0Verifier worker-xhigh fable xhigh 4,383,294;
TopstepFacts worker-medium opus medium 2,130,037; FreezeReviewer worker-xhigh fable xhigh 1,899,346.

Delegation share: lead 148,107,878 (51.4%), workers 140,075,810 (48.6%); by tier, Opus 97.8% (lead
51.4%, Opus workers 46.4%) and Fable 2.2%. Cache reads are 98.3% of all tokens. The closing steps after
13:19 (assembly and the commit) add a little to the lead and are not in these sums. Counts from
reports/stage_e10_briefs/cost.py (raw output reports/stage_e12_briefs/cost_raw.txt); the /usage meter
is not readable from the session.
