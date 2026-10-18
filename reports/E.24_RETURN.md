# Stage E.24 return: forward plumbing (the loader fix, the IBKR and Alpaca paper adapters, the E22-F2 registration)

Prompt: docs/prompts/STAGE_E.24.md. Lead: Opus 5.5, effort xhigh, ultracode on; session
c2dca792-060d-4694-91ef-4a6f3f808f1d, 2026-10-18 (all times PDT, America/Vancouver, from `date`, file mtimes, git or
the transcripts). A build stage: no outcome read, no market data read, no broker or data endpoint contacted (V41, V42).
Windows: the prompt's 07:00/07:30 were replaced twice by planner messages (06:18: 09:00/09:30; 11:16: 15:00/15:30)
after two usage-limit pauses (about 02:00-06:10 and 06:35-11:10) and a reboot at 10:49.

## 1. Summary

- **Part A (loader fix): done.** The bound and the per-unit/per-fill files live in a new package, mdio/, because
  base_rules/, multiday/ and trigger_hold/ are frozen. No existing file changed. The E.23 discovery replay matched
  exactly (79,207 values, 0 mismatches; nothing after 2019-04-30 loaded). LoaderReviewer-FableXHigh approved with 2
  fixes; LoaderRecheck-FableXHigh approved them. No harness v14.
- **Part B (IBKR adapter): built and fixed; final Fable recheck pending.** Settlement finding: IBKR documents the
  daily TRADES close as the "Last traded price". Its legacy docs say it only "can be the settlement price if provided
  by the exchange". So it is **not reliably the settlement**. Nothing was registered and E22-F1 is unchanged; decision
  1 in section 7. AdapterReviewer-FableXHigh blocked (1 BLOCKING, 5 SHOULD FIX); IBKRFixer fixed all six. The recheck
  was cut by a usage limit.
- **Part C (Alpaca adapter, E22-F2): adapter built and fixed (recheck pending); E22-F2 NOT frozen and NOT
  registered.** The E22-F2 text is complete and was revised for RegReviewer-FableXHigh's 2 BLOCKING and 8 SHOULD FIX.
  The code fixer for those items (F2Fixer2) was cut by the usage limit before reporting, and the recheck never ran.
  The prompt's rule "BLOCKING and SHOULD FIX fixed first" is therefore not met. **N stays 538.**
- **Part D: done.** Warm-up declarations and the user checklist.
- Tests: forward and mdio 468 passed, 2 skipped; the E22-F1 frozen files are unchanged. The full end suite was not
  re-run: the user asked to finish within a credit limit. The start suite was 7,728 passed with 1 known failure.
- **What the user does next:** decide E22-F1's settlement source (decision 1); approve a short session that finishes
  E22-F2 (code against the text, three Fable rechecks, freeze, register N 538 -> 539; decision 2); then the account
  steps in reports/stage_e24_user_checklist.md.

## 2. Guardrail evidence

### 2.1 Start checks (01:28:39; reports/stage_e24_briefs/start_checks.txt, script reports/stage_e24_briefs/checks.sh)

```
$ date
Sun Oct 18 01:28:39 PDT 2026
$ git status --short
$ git log --oneline -3
0023572 docs: Stage E.24 (forward plumbing) and E.25 (untapped sources) prompts, V42
f36a33a docs: V41 (E.23 accepted, direction closed, loader fix approved)
ef2902d Stage E.23 triggers at multi-day holds
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
$ E22-F1 frozen file set: sha256sum -c reports/stage_e22_f1_files.sha256 (list pinned bb3bf3b3...)
bb3bf3b3c6df28ac203905b53317b1835d447d6b2bba2ec88be929dd2a0fb8af
all 30 files OK
exit 0
$ E.24 E22-F2 freeze and registration (written during the stage)
reports/stage_e24_prereg_F2.md not yet written
reports/stage_e24_f2_files.sha256 not yet written
$ .env variable names (status only; values never read)
(untracked lines omitted: 1272)
```

Start suite, `uv run pytest -q -p no:cacheprovider` (detached at nice 10 with a 2 GB memory watchdog, 01:29:13-01:59:56;
reports/stage_e24_briefs/pytest_start.out; minimum available memory 2,069 MB):

```
FAILED tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha
1 failed, 7728 passed, 3 skipped, 3 xfailed, 54 warnings in 1836.64s (0:30:36)
rc 1 end 01:59:56
```

The one failure is the known v13-era test (the same line as E.23's start and end suites). The known v13-era mismatches
in the freeze lines (E.14 inputs list, E.16 manifest, E.18, E.20 H6, E.20 search) are the same as in E.23's checks.

### 2.2 End checks

End checks 16:00:29 (reports/stage_e24_briefs/end_checks.txt). Every line equals the start block except the date, the git log (Stage E.25's parallel commit 715ae8e) and the E22-F2 draft now present but untracked and unfrozen:

```
$ date
Sun Oct 18 04:00:29 PM PDT 2026
$ git status --short
$ git log --oneline -3
715ae8e Stage E.25 untapped sources research
0023572 docs: Stage E.24 (forward plumbing) and E.25 (untapped sources) prompts, V42
f36a33a docs: V41 (E.23 accepted, direction closed, loader fix approved)
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
$ E22-F1 frozen file set: sha256sum -c reports/stage_e22_f1_files.sha256 (list pinned bb3bf3b3...)
bb3bf3b3c6df28ac203905b53317b1835d447d6b2bba2ec88be929dd2a0fb8af
all 30 files OK
exit 0
$ E.24 E22-F2 freeze and registration (written during the stage)
3d4cae83878cb99d41338147e059f313d1b0d332a10b228307364d28d9d0c0e3  reports/stage_e24_prereg_F2.md
untracked
reports/stage_e24_f2_files.sha256 not yet written
$ .env variable names (status only; values never read)
(untracked lines omitted: 1449)
```

Forward and mdio tests at 15:59:44: `468 passed, 2 skipped in 24.25s`; `sha256sum -c --quiet reports/stage_e22_f1_files.sha256` OK. Full end suite not run (user instruction to finish within a credit limit); the last full run is the start suite above, and E.24 changed only new files outside the harness directories. No worker or background shell is running: the last workflow ended, and the start suite's detached shell ended at 01:59:56.

### 2.3 Order of events

| Time | Event |
|---|---|
| 01:27-01:34 | Start checks; start suite launched (01:29:13); broker libraries pinned in forward/requirements_broker.txt |
| 01:35-01:45 | LoaderCoder, facts workflow (IBKRReader, AlpacaReader), IBKRCoder, AlpacaCoder, FeeReader, F2BookCoder spawned; E22-F2 draft 1 (01:41-01:43) |
| 01:59:56 | Start suite done: 1 failed (known), 7,728 passed |
| ~02:00-06:10 | PAUSE 1: usage limit |
| 06:11-06:33 | Workers resumed; fact checks (I4, A7 overstated); key IBKR finding; D1 and D2 written; lead rulings Q1-Q20; Alpaca switched to raw bars plus corporate actions |
| 06:18 | Planner: window to 09:00/09:30 |
| 06:32 | LoaderReviewer: APPROVE WITH FIXES |
| ~06:35-11:10 | PAUSE 2: usage limit; reboot 10:49 |
| 11:16 | Planner: window to 15:00/15:30, at most 6 workers |
| 11:17-11:49 | Wave 2: loader fixes and recheck (APPROVE); F2 Q21-Q23; RegReviewer BLOCK; AdapterReviewer BLOCK; AlpacaReviewer APPROVE WITH FIXES |
| 11:50-11:56 | Lead rulings (review_rulings.md); E22-F2 text revised |
| 11:54-~12:15 | Wave 3: IBKRFixer and AlpacaFixer done; F2Fixer2 and the three rechecks cut by a usage limit |
| ~12:15-15:59 | PAUSE 3: usage limit |
| 15:59-16:10 | User: finish within a credit limit. Tests, end checks, return, progress, STAGES, commit |

## 3. Results

### 3.1 Part A: the loader fix (V41; E.23 VerdictVerifier NOTE-2, NOTE-5)

- Pins first (reports/stage_e24_briefs/loader/pins.md, pin_inventory.py): base_rules/*.py is pinned by the E.16 freeze
  (its `git diff --quiet 8f388c8 -- base_rules ...` guardrail line), multiday/*.py by the E.21 freeze and
  trigger_hold/*.py by the E.23 freeze, whose verify steps refuse even a new file in those directories. Part A could
  not change base_rules/context.py or multiday/ without changing a frozen file; it did not stop, because the fix fits
  in a NEW package, **mdio/**, that changes no existing file (OC-14).
- The change (reports/stage_e24_briefs/loader/loader_report.md section 2 and "Wave 2 fixes"): mdio/bounded.py
  (BoundedLoader, bound_context, check_bounded: a store whose name starts after the window's last bar is never opened;
  Parquet row groups wholly after it are never decoded; every decoded batch is filtered before pandas; a breach raises
  BoundBreached), mdio/book_files.py and mdio/trigger_books.py (per-unit and per-fill files in E.21's per-root layout),
  tests/test_mdio_bounded.py and tests/test_mdio_book_files.py (23 tests, written first; mutations caught).
- Limit, stated plainly: the bound holds at row-group granularity. When a future window's last bar falls inside a
  Parquet row group (about 1M rows, about 3 years, in the ext2010 stores), the later rows of that group are decoded into
  Arrow buffers and dropped before any pandas frame or computation. E.23's windows produced no such straddle (the
  recheck read the four ext2010 footers: no straddling group). Decision 4 in section 7.
- Proofs: (a) the E.21, E.23 and base_rules suites unchanged and passing, 231 passed (also after the wave 2 fixes);
  every freeze line of the start checks re-run unchanged, the E.16 guardrail rc 0, harness v13 preflight OK with mdio/
  present; (b) the replay of E.23's discovery books in a scratch directory (test mode, no marker, only E.23's ext2010
  discovery stores) matched discovery_result.json exactly, 79,207 values, 0 mismatches, max loaded date 2019-04-30 in
  every store, the step2 stores never opened (strace); LoaderReviewer-FableXHigh's independent replay: 39,624 leaves,
  0 mismatches, its per-root files byte-identical to the coder's.
- Not wired into the frozen runners: multiday/run.py and trigger_hold/run.py stay unbounded if rerun (they are frozen);
  a future multi-day stage must build its context with mdio.bounded.bound_context, read through BoundedLoader, and
  list mdio/*.py in its freeze. No harness v14: mdio/ is outside screening.harness_freeze.HARNESS_DIRS and no pinned
  file changed (LoaderReviewer item 6).

### 3.2 Part B: the IBKR paper adapter for E22-F1

- Facts (reports/stage_e24_briefs/facts/ibkr_facts.md; fact check ibkr_factcheck.md: 8 OK, I4 OVERSTATED):
  - I6, settlement: the TRADES close is the "Last traded price"; the legacy docs say "can be the settlement price if
    provided by the exchange"; no settlement field was found in the pages read.
  - I4/I8, data access: historical bars probably need Level 1 subscriptions (four at USD 1.55 a month, USD 6.20) on a
    funded IBKR Pro account (USD 500). The fact check found a possible delayed path.
  - I5: expired contracts are served for 2 years. I1: IBC 3.24.2 is retired but maintained; paper port 4002.
- Code: forward/ibkr_gateway.py (lazy ib_async 2.1.0, connection from env NAMES), forward/sources_ibkr.py,
  forward/orders_ibkr.py, forward/shadow_f1.json ("enabled": false), forward/daily_f1.py, tests/_forward_ibkr_mock.py,
  tests/test_forward_ibkr_*.py (97 passed, 1 skipped; 4 vendor contract tests pass offline against the real ib_async).
  Report: reports/stage_e24_briefs/ibkr/ibkr_report.md (wave 3 section included).
  - sources_ibkr.py is a SettlementSource for the frozen runner, labelled close_last_trade. It also writes the warm-up
    as HistoryRow JSONL across rolls (both prices on switch dates), and a CSV export that replays byte-identically
    through the unchanged frozen runner.
  - orders_ibkr.py is the shadow route with its own ledger. It never writes the E22-F1 ledger; the byte-identical
    test passes with the shadow route on and off.
- Behaviour after wave 3:
  - a timed-out request raises SourceUnavailable (no record);
  - a missing day is confirmed only by a finished later bar;
  - subscription refusals raise SubscriptionNeeded;
  - `run` needs --date or --holidays, and refuses a whole exchange missing unless --accept-exchange-gap is passed;
  - `probe --log` records the same bar at different ages;
  - late shadow fills are recovered.
- Not fixed: the N3 catch-up loop. A run after several missed dates stops at exit 2 for the operator.

### 3.3 Part C: the Alpaca paper adapter and E22-F2

- Facts (alpaca_facts.md; fact check 9 OK, A7 OVERSTATED; fees_facts.md):
  - the paper account is free; the free plan is IEX real time, and whether SIP history is available is in conflict;
  - the daily close is the last eligible trade, not the official close;
  - the "all" adjustment method is undocumented;
  - fractional orders are day-only and long-only; MOC is whole-share only;
  - Reg T is 2x overnight;
  - fees: SEC $0.0000206 x value on sells, TAF $0 as printed, CAT $0.000003/share; margin 6.50%; ETB borrow $0;
  - paper simulates neither fees, borrow fees nor dividends.
- Adapter: forward/etf_bars.py, forward/sources_alpaca.py, forward/orders_alpaca.py, forward/shadow_f2.json, and
  tests/test_forward_alpaca_*.py plus tests/test_forward_etf_bars.py (123 passed, 1 skipped; 10 contract tests pass
  offline against the real alpaca-py 0.44.0). Report: reports/stage_e24_briefs/alpaca/alpaca_report.md.
  - Returns come from raw bars plus /v1/corporate-actions: k x (close + D)/prev - 1.
  - Capital gains are long_term_rate + short_term_rate. Queries are padded ±60 days on process_date and filtered on
    ex_date. Actions are returned for any span.
  - The shadow route uses whole-share MOC by default.
- E22-F2 design (reports/stage_e24_prereg_F2.md, DRAFT, not frozen; draft 1 preserved at reports/stage_e24_briefs/f2/
  prereg_F2_draft1.md):

| Item | Declared |
|---|---|
| Rule | E22-F1's frozen code: speeds, scalars, caps, FDM 1.1313802916085167, 20% target, $25,000 fixed |
| Universe | QQQ IWM GLD USO UNG FXE SHY IEF TLT CORN SOYB (soybean oil not modelled); BIL as cash benchmark, never traded |
| IDM | 2.3293791420997985: F1's frozen correlation without MZL, live sub-matrix |
| Prices | Alpaca daily bars, feed sip (iex if refused, fixed before the clock), raw closes plus corporate actions |
| Positions | Cap B = $50,000 (Reg T 2x) on unrounded targets with carried notional held fixed; Carver 10% buffer; longs 0.001 share; shorts whole shares toward zero; second cap check on longs and shorts |
| Fills | Next session's daily-bar close, paper |
| P&L | In excess of BIL; shorts earn no credit plus b 1.0%; debit above capital pays s 2.50%; half-spread 1 or 3 cents; SEC and CAT fees rounded up daily; late corporate actions booked in the next record |
| Data rules | Missing-day and ledger rules mirror F1 sections 6-7; prev close = recorded close; suspect-split guard; delisting after 10 sessions; SGOV replaces BIL after 10 sessions |
| Warm-up, horizon, bar | 2024-03-01 to the start; 36 months; F1's bar (NW lag 10 one-sided p <= 0.05 and Sharpe >= 0.3) with its power statement and stated drags |
| Registry | Test E24, id E24-F2 ("E22" is E22-F1's label) |
| Pre-clock correction | sources_alpaca.py and daily_f2.py may be corrected before the first record, logged |

- Book code: forward/strategy_f2.py, runner_f2.py, evaluate_f2.py, daily_f2.py, config_f2.json, tables_f2.json,
  tests/test_forward_f2_*.py. Report: reports/stage_e24_briefs/f2/f2book_report.md; rulings Q1-Q23 applied by wave 2.
  The wave 3 fixes for RegReviewer's B1, B2, S1, S2, S4, S6, S7 and S8 were started by F2Fixer2, which was cut before
  reporting. The tests pass, but which of those items the code now implements is NOT verified. That gap is why
  nothing was frozen.

### 3.4 Part D: warm-up declarations and the user checklist

- reports/stage_e24_warmup_declaration.md (D1): E22-F1 reads the 12 micros' daily IBKR TRADES bars (labelled last
  trade, not declared settlement) from 2024-03-01 to the trade date before the start, only after the user's
  settlement-source decision; it spends holdout-2 for MGC, MCL and MNG and the research window for the 12 micros, for
  trend-type and multi-day hypotheses only (V42), the 2024-03 embargo month included in V42's range; IBKR's 2-year
  expired-contract depth means the obtainable warm-up starts later for a late-2026 start (the spend is declared for the
  whole range regardless). E22-F2 reads raw daily bars and corporate actions of the 11 ETFs and BIL from 2024-03-01
  (never sealed; spends nothing). The files the session writes (ledger/forward/...), their sha256 records and the order
  of events (start checks, pre-clock roll check, connection checks without prices, E22-F2's warm-up first, records,
  first ledger records, end checks) are declared. No read happened in this stage.
- reports/stage_e24_user_checklist.md (D2): the settlement decision first; the IBKR Pro account, futures permissions,
  funding (USD 500 plus subscriptions, likely needed; the next session probes IBKR's delayed path first), the cheapest
  coverage (four L1 feeds at USD 1.55 a month each, USD 6.20, or the USD 10 bundle), market data sharing to the paper
  user; IB Gateway (stable, offline) and IBC 3.24.2 with the paper login in IBC's own config.ini; the Alpaca paper-only
  account and keys; the .env names (IBKR_GATEWAY_HOST, IBKR_GATEWAY_PORT, IBKR_CLIENT_ID, IBKR_ACCOUNT_ID,
  IBKR_PAPER_USERNAME and IBKR_PAPER_PASSWORD for IBC only, ALPACA_PAPER_KEY_ID, ALPACA_PAPER_SECRET_KEY), which no
  session reads or prints; and the approval the first connection session needs.

## 4. Delegation record

Tokens are from reports/stage_e10_briefs/cost.py over the transcripts it reads (the lead and the Agent-tool
subagents). The three workflows' agents are under subagents/workflows/, which the script does not glob. For those,
the harness's reported subagent_tokens are shown instead; they are not split by model and are not comparable with
the per-transcript totals.

| Agent | Model | Effort | Status | Tokens (cost.py) |
|---|---|---|---|---|
| lead | opus | xhigh | - | 49,222,441 |
| LoaderCoder-OpusXHigh | opus | xhigh | done | 19,819,200 |
| IBKRCoder-OpusXHigh | opus | xhigh | done | 26,413,610 |
| AlpacaCoder-OpusXHigh | opus | xhigh | done | 20,860,603 |
| F2BookCoder-OpusXHigh | opus | xhigh | done | 29,017,210 |
| FeeReader-OpusMed | opus | medium | done | 3,404,830 |
| IBKRFactChecker-FableXHigh | fable | xhigh | done | 2,375,080 |
| AlpacaFactChecker-FableXHigh | fable | xhigh | done | 2,642,401 |
| LoaderReviewer-FableXHigh | fable | xhigh | done | 2,835,297 |
| AlpacaReviewer-FableXHigh (1st, cut) | fable | xhigh | no output | 2,370,582 |
| AdapterReviewer-FableXHigh (1st, cut) | fable | xhigh | no output | 901,660 |
| Workflow wf_a244ece8-d25: IBKRReader-OpusHigh, AlpacaReader-OpusHigh, AlpacaFactChecker (cut) | opus, fable | high, xhigh | readers done | harness 590,226 |
| Workflow wf_a5926b6e-692: LoaderFixer, F2Fixer (opus xhigh); LoaderRecheck, RegReviewer, AdapterReviewer, AlpacaReviewer (fable xhigh) | opus, fable | xhigh | all done | harness 1,224,163 |
| Workflow wf_82df3661-9de: IBKRFixer, AlpacaFixer (done), F2Fixer2 (cut) (opus xhigh); 3 rechecks (cut) (fable xhigh) | opus, fable | xhigh | partial | harness 1,067,883 |

## 5. Verification (each Fable finding, the ruling and the fix)

Full rulings: reports/stage_e24_briefs/review_rulings.md. Fact checks: reports/stage_e24_briefs/facts/
ibkr_factcheck.md (8 OK, I4 OVERSTATED: two official pages describe a delayed historical path; the checklist and the
adapter were corrected) and alpaca_factcheck.md (9 OK, A7 OVERSTATED: Alpaca's PDT status in an interim period;
A5 upgraded: "We do not support short sales in fractional orders").

| Review | Verdict | Findings | Ruling and fix |
|---|---|---|---|
| A2 LoaderReviewer (loader_review.md) | APPROVE WITH FIXES | 0 B, 2 SF, 9 N | SF-1 null trade_date refused as the frozen path does; SF-2 bound mandatory in read_root_books. Fixed by LoaderFixer; LoaderRecheck APPROVE (0/0/3) |
| B5 AdapterReviewer (ibkr/adapter_review.md) | BLOCK | 1 B, 5 SF, 8 N | All fixed by IBKRFixer (section 3.2). S3 and S4 ruled by the lead. Recheck NOT run (usage limit) |
| C4a AlpacaReviewer (alpaca/adapter_review.md) | APPROVE WITH FIXES | 0 B, 3 SF, 9 N | S1 any-span corporate actions and t's close; S2 shadow order pagination; S3 empty response raises. Fixed by AlpacaFixer; recheck NOT run |
| C4b RegReviewer (f2/reg_review.md) | BLOCK | 2 B, 8 SF, 14 N | Text revised for B1, B2, S1-S7. Code fix (F2Fixer2) cut, unverified. Recheck NOT run. **No freeze** |

Every number entering a verdict: none in this stage. No registration happened, and the loader replay figures were
checked independently by LoaderReviewer's own replay.

## 6. Open choices (every decision the lead made on its own, with the reason)

- OC-1 Broker libraries pinned in forward/requirements_broker.txt (a uv overlay with hashes), not in pyproject.toml
  or uv.lock. Harness v13 pins both files, and a v14 would make E.23's v13 preflight refuse.
- OC-2 Start suite run at 7.5 GB available, with a 2 GB watchdog.
- OC-3 E22-F2 P&L in excess of BIL. A total-return ETF book could pass the bar on the cash rate and carry alone; a
  flat book must earn 0.
- OC-4 IDM from F1's frozen correlation without MZL; FDM is F1's.
- OC-5 Soybean oil not modelled; BIL as the cash benchmark.
- OC-6 Cap on unrounded targets before the buffer; shorts rounded toward zero (extended by the C4b rulings).
- OC-7 Warm-up from 2024-03-01, for parity with E22-F1.
- OC-8 Share update reinvests distributions at the close. Later based on raw closes plus corporate actions (OC-12).
- OC-9 Two finra.org pages were fetched before FINRA's terms were read (the terms bar scraping); they are not cited.
  TAF follows Alpaca's printed $0.
- OC-10 The NYSE calendar was not fetched (ICE's terms bar robots); the operator checks it in a browser.
- OC-11 s 2.50% (6.50% minus the FOMC upper bound 4.00%); b 1.0%; half-spreads of 1 or 3 cents declared without
  quotes.
- OC-12 Returns from raw closes plus corporate actions, not Alpaca's undocumented "all" adjustment; late actions
  booked in the next record.
- OC-13 Alpaca shadow route uses whole-share MOC by default.
- OC-14 Loader fix in a new package, mdio/. The frozen runners stay unbounded if rerun.
- OC-15 Planner window change 06:18 (09:00/09:30).
- OC-16 Rulings Q1-Q23 on the F2 coder's ambiguities (f2book_report.md).
- OC-17 IBKR cutoff 18:00 CT on the trade date; the price is labelled close_last_trade.
- OC-18 Planner window change 11:16 (15:00/15:30, at most 6 workers).
- OC-19 After the reboot, fresh narrow workers instead of resuming large transcripts.
- OC-20 IBKR S3: `run` needs --date or --holidays and refuses an exchange gap. S4 left to the user, with a probe.
- OC-21 E22-F2 suspect-split guard, delisting rule, SGOV substitute.
- OC-22 Registry id E24-F2 under test E24: the registry needs ids prefixed by a label used once, and E22 is taken.
- OC-23 Pre-clock correction clause for sources_alpaca.py and daily_f2.py.
- OC-24 E22-F2 not frozen and not registered: the BLOCKING and SHOULD FIX code fixes are unverified and no Fable
  recheck ran.
- OC-25 Full end suite not re-run, on the user's instruction to finish within a credit limit. The forward and mdio
  tests and every guardrail check were run.
- OC-26 IBKR warm-up depth: IBKR serves expired contracts for 2 years only, so the declared spend covers the full V42
  range even though less can be read.

## 7. Decisions for the user (the lead's recommendation first)

1. **E22-F1's settlement source (IBKR's close is not reliably the settlement).** Options:
   - (a) a pre-clock amendment, E22-F1b, with N + 1. Same rule on IBKR's daily TRADES close, fetched at a frozen time
     set from the probe's bar-age evidence. E22-F1 ends "abandoned, no verdict" before its clock, having seen no data.
   - (b) a second source for settlements only (for example a fresh Databento statistics-schema quote).

   Recommendation: (a). At daily frequency the rule is insensitive to last-trade versus settlement, (a) needs one
   vendor and no new spend beyond IBKR's L1 data, and the price definition is then frozen explicitly.
2. **Finish E22-F2 in a short session.** Steps: verify and finish the code against the revised text (C4b B1, B2,
   S1-S8), run the three Fable rechecks (registration, IBKR, Alpaca), then freeze, commit and register (test E24, id
   E24-F2, N 538 -> 539). Recommendation: yes, before any account is opened.
3. **Broker libraries.** Recommendation: keep the pinned uv overlay. Move them into pyproject.toml (harness v14)
   only when a harness change is needed anyway.
4. **The loader's row-group limit.** A future window ending inside a row group decodes that group's later rows into
   Arrow and drops them before any computation. Recommendation: accept it, and list mdio/*.py in the next multi-day
   stage's freeze. The alternative is re-chunking the stores, a data rewrite.
5. **Shadow routes.** Recommendation: keep them off for the first two weeks of each ledger.
6. **Carried:** the AiTrader readout (2026-10-23) remains the next decision point.

## 8. Session cost

Wall-clock 01:27-16:10 PDT. Pauses are not work: about 02:00-06:10 and 06:35-11:10 (usage limits; reboot 10:49),
then about 12:15-15:59 (usage limit). Work periods: 01:27-02:00, 06:10-06:35, 11:15-12:15, 15:59-16:10, about 2 h 10
min in total.

Final ETA table (actuals; the estimate was 06:55 for the whole stage):

| Task | Owner | Model | Effort | Start-end | Status |
|---|---|---|---|---|---|
| Startup, deps, briefs | lead | opus | xhigh | 01:27-01:45 | done |
| A1 loader | LoaderCoder | opus | xhigh | 01:35-06:16 (paused) | done |
| A2 review, fix, recheck | LoaderReviewer, LoaderFixer, LoaderRecheck | fable, opus | xhigh | 06:16-11:35 (paused) | APPROVE |
| B1, C1 facts | IBKRReader, AlpacaReader | opus | high | 01:35-01:59 | done |
| Fact checks | IBKRFactChecker, AlpacaFactChecker | fable | xhigh | 06:13-06:27 | done |
| B2-B4 | IBKRCoder, IBKRFixer | opus | xhigh | 01:40-12:13 (paused) | done; recheck pending |
| C2 design | lead | opus | xhigh | 01:41-11:56 (revisions) | draft, not frozen |
| C3 adapter | AlpacaCoder, AlpacaFixer | opus | xhigh | 01:40-12:08 (paused) | done; recheck pending |
| C3 book | F2BookCoder, F2Fixer, F2Fixer2 | opus | xhigh | 01:44-~12:15 (paused) | wave 3 fixes unverified |
| B5, C4a, C4b reviews | Fable reviewers | fable | xhigh | 11:17-11:49 | BLOCK / AWF / BLOCK |
| D1, D2 | lead | opus | xhigh | 01:50-06:30 | done |
| End checks, return, commit | lead | opus | xhigh | 15:59-16:10 | done |

Tokens per model (cost.py; the lead plus the Agent-tool subagents):

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 2,354 | 229,760 | 9,972,735 | 920,171 | 11,125,020 |
| claude-opus-5-5 | 1,238 | 948,975 | 143,187,914 | 4,599,767 | 148,737,894 |
| all | 3,592 | 1,178,735 | 153,160,649 | 5,519,938 | 159,862,914 |

Delegation share over these transcripts: lead 49.2M (30.8%), workers 110.6M (69.2%); by tier, opus 93.0%, fable
7.0%. Workflow agents are not included: harness-reported 590,226 + 1,224,163 + 1,067,883 subagent tokens, a different
measure. Per spawn: section 4. These are token counts, not plan-credit percentages.
