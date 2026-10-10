# Stage E.18 return: C1b (C1 re-registered with the C10 fix) evaluated once: FAIL; N = 480

Prompt docs/prompts/STAGE_E.18.md (V24-V31). Lead Opus 5.5 xhigh, session a6f2d97b-f5fc-4d95-a054-c5010e1ff6d0, 2026-10-10. All times PDT (America/Vancouver), from `date`, file mtimes, git and the registry. STATE: reports/stage_e18_STATE.md.

## 1. Verdict summary

**C1b: FAIL.** Neither registered test passes its bar (freeze section 5; each meets only n >= 30):

| Test | Trades / dates | Mean gross (ticks) | 1.5c bar | t_B | one-sided p |
|---|---|---|---|---|---|
| C1b-T1, NG h60 | 814 / 557 | +0.585 per trade (-0.914 per date) | 2.562 | -0.83 | 0.80 |
| C1b-T2, NG hF | 627 / 386 | -0.113 per trade | 2.649 | -0.41 | 0.66 |

VerdictVerifier-FableXHigh recomputed every number independently (66 items, 0 unequal at 1e-9): VERIFIED WITH
NOTES, no BLOCKING finding. The verdict holds whether criterion 1 reads the
per-trade or the per-date mean.

**N = 480** (r003-C1b, N 478 -> 480, 12:17:48 PDT).

**The one fix held.** C10 exempted only g17_mbt (MBT unlisted until 2021) and g17_cl (NG's own cluster lead,
reference 0). Every other feature live in E.12 applied, so the run did not stop. The exempt list follows from
listing dates and section 2 alone, not from the C10 counts E.17's stopped run printed. Before the freeze, Fable
approved the diff (one SHOULD FIX, fixed), and the dry check passed on E.12's frozen reference.

**Meaning (freeze section 8, Fail):** the NG near-miss is closed. Gate 0's reading stands, nothing more is built on
v2's model, and N is 480. E.12's 2019-2024 h60 row (5.57 ticks, t_B 2.51) did not recur in 2010-2019. A fail cannot
separate "never real" from "real only in the 2019-2024 LNG-era regime".

## 2. Guardrail evidence

Start and end checks, verbatim (reports/stage_e18_briefs/checks.sh: E.17's script with E.18's paths). Only the
earlier stages' untracked evidence-page lines are collapsed into one line with their count.

### Start checks (11:47)

```
$ date
Sat Oct 10 11:47:18 AM PDT 2026
$ git status --short
?? .claude/worktrees/
?? reports/stage_e12/e13/e14/e16_briefs page files: 639 lines (collapsed; full text in reports/stage_e18_briefs/start_checks.txt)
?? reports/stage_e18_briefs/
$ git log --oneline -3
0436ff2 docs: Stage E.18 prompt (C1b) and V31
8342b6a chore: ignore editor swap and lock files
6a38c4d Stage E.17 C1 and base-rule batch evaluated
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

Start suite, `uv run pytest -q -p no:cacheprovider` (run with PYTHONPYCACHEPREFIX set; see section 6 item 9):

```
FAILED tests/test_harness_freeze.py::test_an_unchecked_hash_pyc_beside_an_unchanged_source_is_refused
FAILED tests/test_harness_freeze.py::test_a_timestamp_pyc_forged_to_match_its_source_is_refused
FAILED tests/test_harness_freeze.py::test_honest_and_stale_bytecode_pass - Fi...
3 failed, 6913 passed, 3 skipped, 3 xfailed, 54 warnings in 1080.40s (0:18:00)
rc=1
Sat Oct 10 12:05:36 PM PDT 2026
```

Rerun of the failing file without the prefix:

```
17 passed in 1.77s
rc=0
12:16:28
```

### End checks (12:29), with the C1b freeze verification and the run-once listing appended

```
$ date
Sat Oct 10 12:29:55 PM PDT 2026
$ git status --short
 M ledger/trial_registrations.jsonl
 M reports/stage_e18_STATE.md
 M reports/stage_e18_briefs/brief_verdict_verify.md
 M reports/stage_e18_review.md
 M reports/stage_e18_rulings.md
?? .claude/worktrees/
?? reports/stage_e12/e13/e14/e16_briefs page files: 639 lines (collapsed; full text in reports/stage_e18_briefs/end_checks.txt)
?? reports/stage_e18_briefs/c1b_evaluate.log
?? reports/stage_e18_briefs/c1b_register.log
?? reports/stage_e18_briefs/end_checks.txt
?? reports/stage_e18_briefs/ret_decisions.md
?? reports/stage_e18_briefs/ret_open_choices.md
?? reports/stage_e18_briefs/ret_results.md
?? reports/stage_e18_c1b_RUN_ONCE.json
?? reports/stage_e18_c1b_result.json
?? reports/stage_e18_verify/
$ git log --oneline -3
b714751 C1b freeze
0436ff2 docs: Stage E.18 prompt (C1b) and V31
8342b6a chore: ignore editor swap and lock files
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
$ git diff --quiet b714751 -- <C1b frozen paths>
exit 0
$ ls reports/*c1b* (run once: one marker, one result)
stage_e18_c1b_RUN_ONCE.json
stage_e18_c1b_diff.md
stage_e18_c1b_result.json
stage_e18_prereg_C1b.md
```

End suite, `uv run pytest -q -p no:cacheprovider` (at nice 10, no prefix):

```
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
6990 passed, 3 skipped, 3 xfailed, 54 warnings in 980.64s (0:16:20)
rc=0
Sat Oct 10 12:46:32 PM PDT 2026
```

Summary: holdout all_ok with 0 unlocks at start and end; REGISTRATION.md 0 bytes; the spend ledger unchanged
(36,402 lines, 034a454b..., at start and end); N 478 at start, 480 at end (one registration, r003-C1b); harness
v12 unchanged; every freeze verified (E.1/E.2a, K1-K8, v2, C1's E.14 freeze and its inputs except the replaced harness
manifest, E.16, C1b). No TopstepX call, no credential, no edit under live/ or ops/, no push. No worker or background
shell was running at the end (`pgrep` before the final commit).

### Order of events

| Event | Evidence | Time (PDT) |
|---|---|---|
| Start checks | reports/stage_e18_briefs/start_checks.txt | 11:47:18 |
| Start suite | reports/stage_e18_briefs/pytest_start.out | 11:47:32-12:05:36 |
| C1b text, code, test written | file mtimes (c1b.py 11:52:07, prereg first version 11:56:07) | 11:48-11:57 |
| Diff review (DiffReviewer-FableXHigh) | reports/stage_e18_review.md lines 5-6; transcript | 11:58:43-12:14:08 |
| Rulings R-1..R-5 applied, text regenerated | reports/stage_e18_prereg_C1b.md mtime | 12:14:38 |
| Dry check | reports/stage_e18_dry_check.json started/finished | 12:16:02-12:16:05 |
| Freeze manifest written / verified | reports/stage_e18_freeze.json mtime; verify run | 12:17:07 / 12:17:22 |
| Freeze commit b714751 "C1b freeze" | git log | 12:17:35 |
| Registration r003-C1b (N 478 -> 480) | ledger/trial_registrations.jsonl time_local | 12:17:48 |
| Evaluation launched (detached) | reports/stage_e18_briefs/c1b_evaluate.log line 1 | 12:18:03 |
| Run-once marker | reports/stage_e18_c1b_RUN_ONCE.json started_local | 12:18:05 |
| Result (verdict FAIL) | reports/stage_e18_c1b_result.json finished_local | 12:18:38 |
| Verdict verification (VerdictVerifier-FableXHigh) | reports/stage_e18_review.md lines 245-366; recompute on disk 12:23:48 | 12:19:13-12:29:08 |
| End checks | reports/stage_e18_briefs/end_checks.txt | 12:29:55 |
| End suite | reports/stage_e18_briefs/pytest_end.out | 12:30:09-12:46:32 |
| Final commit "Stage E.18 C1b evaluated" | git log | 219a0ae's amended successor (git log) |


## 3. Results per step

### Step 0: startup (11:41-11:48)

- Start checks (reports/stage_e18_briefs/start_checks.txt; section 2 quotes them): holdout all_ok, 0 unlocks;
  REGISTRATION.md 0 bytes; check_frozen ALL_OK; harness v12 preflight OK; cluster freezes K1-K8 OK; v2 freeze 91 files;
  N = 478; the spend ledger 36,402 lines (034a454b...); E.14's C1 freeze-inputs list: 43 entries, one mismatch, the
  harness manifest (replaced by v11 and v12 in E.17, the exception C1b's section 11 names); E.16 freeze OK.
- Start suite: 6913 passed, 3 failed, 3 skipped, 3 xfailed (11:47:32-12:05:36). The three failures
  (tests/test_harness_freeze.py, bytecode tests) came from the lead's invocation, not the code: PYTHONPYCACHEPREFIX was
  set for the suite, so bytecode left the tmp_path the tests inspect. The file rerun without it: 17 passed (12:16).
  The end suite used the prompt's exact command.

### Step 1: C1b's text and code (11:48-11:57)

- Text: reports/stage_e18_prereg_C1b.md, written by reports/stage_e18_briefs/make_c1b_text.py as 15 exact
  replacements on C1's freeze (each must match once; the script checks C1's sha256 first) plus a new section 13 listing
  every change. Final sha256 35b936fb33c32f29365cdd77ce1f8642330270a827795dac4059403d78075dcd (after the Step 2 fixes).
- Diff: reports/stage_e18_c1b_diff.md (generator make_diff_doc.py): the 16 changes classified by THE ONE FIX's items,
  the input-by-input table behind the exempt list, the code change, and the full `diff -u`.
  - Item 2 (C10's clause): "unless the feature is on the exempt list below"; the list is exactly g17_mbt (leg MBT:
    no contract listed on any date of the window; CME Micro Bitcoin futures launched 2021-05-03; BTC, listed from the
    trade date 2017-12-18, is not a leg of the model) and g17_cl (leg CL: listed, but NG's own cluster lead, never
    applicable on NG rows; E.12 reference 0, so a no-op). Decided from listing dates and section 2 only.
  - Item 3: "Every other feature keeps C10 exactly as C1 had it."
  - Item 1 and the bookkeeping it forces: ids C1b-T1/T2, N 478 -> 480 (sections 5, 6, 8), the closed attempt cited,
    C1b's steps without purchase (section 9), V31 (section 10), and two statements of C1 that E.17 made false:
    section 2's "no program file has read NG or any leg before 2019-05" (E.17's store builds, C1's stopped run and the
    base-rule batch read these stores) and section 11's "the harness differs from v10 only in data/config.py" (the
    prompt fixes v12, which also changes data/pull_hist.py, hist_store.py and hist_calendar.py).
  - The design change does not depend on the applicable-row counts E.17's stopped run printed (counts only, known to
    the lead): the exempt list follows from listing dates and section 2, and would be the same whatever they were.
- Listing evidence (reports/stage_e18_briefs/pages/LOG.md): two CME press releases saved raw (scrapling; curl got 403),
  verbatim: "today launched Micro Bitcoin futures" (May 3, 2021) and "effective on Sunday, December 17, 2017 for a trade
  date of December 18" (BTC). The older contracts' launch dates are marked [unverified].
- Code: new c1_replication/c1b.py (sha256 4f8ce49b...). It runs the frozen c1_replication.evaluate.run inside
  c1b_profile(), which swaps five evaluate attributes (TEST, TEST_IDS, HORIZON_OF, c10_check, preconditions) and
  restores them on exit or error. Its c10_check calls C1's function on the reference less the two exempt signals; its
  preconditions adds the C1b record (ids, exempt list) to the marker and result. Every C1 file is byte-identical.
  New tests/test_c1b.py (sha256 4d9394fb...): 74 tests, including every one of the 62 non-exempt covered signals
  still stopping, both exempt signals never stopping, C1's frozen rule stopping on the same reference, the profile
  restored after a run and after an exception, C1's registration not admitting C1b, and the CLI paths. 74 passed.

### Step 2: review (DiffReviewer-FableXHigh, 11:58-12:14)

- APPROVE WITH FIXES: 0 BLOCKING, 1 SHOULD FIX, 9 NOTE; all six checks PASS (scope of the diff; exempt list from
  listing dates and section 2; all 30 live signals' inputs traced, no third feature can meet the contradiction;
  the code does exactly clause 2; v12 changes nothing on the ext2010 evaluation path, get_plan("ext2010") equal on
  every v10 field; 101 tests passed).
- S-1 fixed (the criterion no longer says "as in training"); N-1, N-2, N-3, N-6 taken as text precision; N-4, N-5,
  N-7, N-8, N-9 no action (rulings R-1..R-5, reports/stage_e18_rulings.md). Text and diff regenerated 12:14-12:15.

### Step 3: dry check (12:16:02-12:16:05)

- reports/stage_e18_dry_check.md and .json (8b98a628...). The amended check on E.12's frozen reference against a
  synthetic world (synthetic bars for NG and the five legs over 2010-06-07..2011-09-30; CL and MBT as C1's sentinel
  frames; the pinned official 2010-2019 calendars; no store opened). Expected outcome written into STATE at 12:00:19.
- PASS, every case as expected: with every leg present C1b's check returns nothing while C1's frozen check returns
  g17_mbt (both horizons), reproducing E.17's contradiction; with NQ, ZN, 6E, GC or ZC removed, C1b's check stops on
  exactly that leg's g17 feature. All 28 non-exempt live features applied (smallest: k4_ngpre_mto, 39 rows).

### Step 4: freeze (12:17:07-12:17:35)

- reports/stage_e18_freeze.json, sha256 5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03: 13 C1b files;
  35 C1 inputs re-hashed against nine pins (C1's freeze, its inputs list, the E.12 state manifest, the model JSON, the
  v2 freeze, the Gate 0 list, the calendar and store hash files, the v12 harness manifest) plus the eight calendar
  files; 10 external items (both M1 payloads, the six ext2010 stores, the E.12 state copy of 51 files, q h60
  0.033735277284776724 and hF 0.0831931045522869). Verify mode OK at 12:17:22.
- Commit b714751 "C1b freeze" at 12:17:35 (37 files, explicit paths). Both freeze files tracked, no diff vs HEAD.

### Step 5: registration and the single evaluation (12:17:46-12:18:38)

- Harness v12 preflight OK; registered r003-C1b at 12:17:48: C1b ['C1b-T1', 'C1b-T2'], N 478 -> 480, freeze
  sha256 35b936fb... (reports/stage_e18_briefs/c1b_register.log; registry sha256 55b1d24c...).
- `python -m c1_replication.c1b` launched detached at 12:18:03 (nice 10); marker reports/stage_e18_c1b_RUN_ONCE.json at
  12:18:05; result reports/stage_e18_c1b_result.json at 12:18:38 (sha256 0b82091933a2b2b40e6cf52461437f7b8e4a6872f4444b8067fae993aebd6466;
  34.7 s wall, 2.05 GB peak, exit 0). Log reports/stage_e18_briefs/c1b_evaluate.log.
- C10 (amended): NG ok rows h60 5,120, hF 4,538; every non-exempt feature live in E.12 applies (g17 legs 4,231-4,858
  rows; k4_ngpre_mto 347/307 the smallest); g17_mbt and g17_cl 0, exempt. No stop. C11: feature_cols equal E.12's.

| Test | n trades | n dates | mean gross (per trade, ticks) | c (ticks) | bar 1.5c | t_B (per-date) | one-sided p | criteria met | decision |
|---|---|---|---|---|---|---|---|---|---|
| C1b-T1 (NG h60) | 814 | 557 | 0.585 | 1.708 | 2.562 | -0.831 | 0.797 | n >= 30 only | FAIL |
| C1b-T2 (NG hF) | 627 | 386 | -0.113 | 1.766 | 2.649 | -0.410 | 0.659 | n >= 30 only | FAIL |

- Verdict: FAIL (no test passes). For comparison, E.12's 2019-2024 Gate 0 rows were h60 mean 5.569 ticks, t_B 2.51,
  518 trades; hF 13.921 ticks, t_B 2.33, 494 trades.
- Descriptive (after the verdict; add nothing to N): share of ok rows at or above q: T1 0.159 (814 of 5,120), T2 0.138
  (627 of 4,538). Long/short: T1 121 long (mean +0.430 ticks) / 693 short (+0.612); T2 117 long (-4.436) / 510 short
  (+0.878). Trades per year (T1): 2010 1, 2011 101, 2012 99, 2013 94, 2014 85, 2015 90, 2016 98, 2017 96, 2018 127, 2019
  23. C14 (1.5x slippage): bars 3.527 (T1) and 3.657 (T2) ticks, not met.
- Note on the statistic: gate0._b_test's `mean` is the mean over trades, while t_B and p use per-date means (T1's
  per-date mean is negative while its per-trade mean is +0.585). The freeze's section 5 calls the statistic a per-date
  mean and criterion 1 "mean gross g". The verdict does not depend on the reading: both means are below 1.5c and
  p > 0.025 in both tests.

## 4. Delegation record (one row per spawn)

| Agent (description) | subagent_type | Model | Effort | Start-end (PDT, transcript) | Tokens (transcript) | Status | Output |
|---|---|---|---|---|---|---|---|
| DiffReviewer-FableXHigh | worker-xhigh | fable (claude-fable-5-1) | xhigh | 11:58:44-12:14:08 | 2,484,866 | done: APPROVE WITH FIXES (0 BLOCKING, 1 SHOULD FIX, 9 NOTE) | reports/stage_e18_review.md lines 3-243; reports/stage_e18_diff_review/ |
| VerdictVerifier-FableXHigh | worker-xhigh | fable (claude-fable-5-1) | xhigh | 12:19:11-12:29:26 | 2,897,434 | done: VERIFIED WITH NOTES (0 BLOCKING, 0 SHOULD FIX, 2 NOTE) | reports/stage_e18_review.md lines 245-366; reports/stage_e18_verify/ |

Both as the prompt's delegation plan routes them (fable xhigh for the independent review and the verdict
recomputation). Everything else was the lead's (opus xhigh): the C1b text, code and test, the listing lookup (two
pages, inline), the dry check, the freeze, the registration, the single run, the rulings and this synthesis. No worker
spawned another; at most one worker ran at a time.

## 5. Verification (each Fable finding, the ruling and the fix; rulings in reports/stage_e18_rulings.md)

**Step 2, DiffReviewer-FableXHigh (11:58-12:14): APPROVE WITH FIXES.** All six checks PASS (reports/stage_e18_review.md
lines 3-243).

| Finding | What | Ruling | Fix |
|---|---|---|---|
| S-1 SHOULD FIX | section 3's criterion said "as in training", false read literally for g17_mbt (87/84 training rows) | R-1 accepted | reworded via the generator; text and diff regenerated before the freeze |
| N-1 | the prompt's criterion sentence does not fit CL (listed), though the prompt names CL | R-2 accepted | one clause: for CL the operative test is section 2's "not applicable by design" |
| N-2 | section 2 named H1 and H4; the composite H5 also covers NG | R-3 accepted | H5 named |
| N-3 | section 11 omitted E.17's ext2010h session constants in data/config.py | R-3 accepted | named |
| N-4 | the result's code_sha256 lists c1b.py beside C1's ten files | R-5 no action | expected; pins c1b.py |
| N-5 | C1's log and schema strings carry into C1b's files | R-5 no action | the "test": "C1b" field distinguishes them |
| N-6 | --out stays free; the result path is not fixed | R-4 text only | section 9 step 7 names the path; the fixed marker is the run-once guard |
| N-7 | test-coverage misses | R-5 no action | none weakens clause 2's coverage |
| N-8 | text fixes must go through the generator and the diff | R-5 followed | done |
| N-9 | older launch dates [unverified] | R-5 no action | the two decisive dates are verified verbatim |

**Step 6, VerdictVerifier-FableXHigh (12:19-12:29): VERIFIED WITH NOTES** (reports/stage_e18_review.md lines 245-366;
scripts reports/stage_e18_verify/). Own recompute on disk at 12:23:48, before the result, marker or log was opened;
66 compared items, 0 unequal at 1e-9; trades_sha256 equal; amended C10: nothing dead; order of events as the freeze's
section 9; one marker, one result; 105 input items, 1 unequal (NOTE 2); spend ledger unchanged.

| Finding | What | Ruling | Fix |
|---|---|---|---|
| NOTE 1 | criterion 1 in code reads the trade-level mean, the freeze text says per-date; T1 +0.585 vs -0.914 | V-1 recorded | none: both below 2.562 and p 0.797, FAIL under either reading; carried to section 7 as a lesson |
| NOTE 2 | C1's freeze-inputs list holds the v10 harness manifest; the run used v12 | V-2 no action | declared in C1b's section 11 |

## 6. Open choices (every decision the lead made on its own, with the reason)

1. **C1b's code is a new module, not an edit of C1's files** (D-1). The prompt allowed the change "in
   c1_replication/guards.py (or wherever c10_check lives)"; c10_check lives in c1_replication/evaluate.py. The lead
   wrote c1_replication/c1b.py, which runs the frozen evaluate.run with five attributes swapped and restored, the
   pattern c1_replication.context.hist_tables already uses. Reason: an edit of evaluate.py or constants.py would have
   changed C1's frozen code (hashed in E.14's freeze-inputs list and in C1's result), broken C1's own tests (they pin
   C1's ids and marker) and left C1's closed attempt irreproducible from its files. Every C1 file is byte-identical;
   C1b's difference is one file. Fable checked the swap (Step 2, check 4).
2. **g17_cl is on the exempt list, with its true reason** (D-2). V31 and the prompt name CL; the prompt's criterion
   sentence ("no listed contract on any date of the test window") does not fit CL, which was listed throughout. The
   text exempts CL under section 2's "CL is never live on NG rows" (NG's own cluster lead, never applicable on its
   cluster's rows) and says that the exemption is a no-op (E.12 reference 0). Reason: follow the user's list without
   writing a false listing claim into a freeze (Fable N-1 agreed; the clarifying sentence was added, R-2).
3. **C1's section 2 "never read" sentence was corrected** (D-3). After E.17 it was false: the store builds, C1's
   stopped run (C10 counts) and the base-rule batch H1-H5 (whose H1, H4 and composite H5 results include NG's
   2010-07..2019-04 bars) read these six stores. C1b's text says so and why it changes nothing (every parameter was
   frozen on 2026-10-05, before any purchase; the one change uses listing dates and section 2 only). The lead did not
   open the H1/H4 per-product values. Reason: a freeze must not assert something false; this is bookkeeping of item 1.
4. **C1's section 11 harness clause was replaced by v12** (D-4). C1 required the evaluating harness to differ from v10
   only in data/config.py; the prompt fixes v12, which also changes data/pull_hist.py, hist_store.py, hist_calendar.py
   and adds the livestock calendar. C1b's section 11 names v12 and lists the differences; Fable confirmed none touches
   the ext2010 evaluation path (get_plan("ext2010") equal on every v10 field). Reason: otherwise C1b's own text would
   contradict the prompt's harness, a second contradiction of the kind this stage guards against.
5. **The C1b record in the marker and result** (part of D-1). c1b wraps C1's preconditions to add the ids and the
   exempt list to the records written before any bar is read. Reason: the result shows g17_mbt at 0 applicable rows;
   the record makes the exemption in force visible in the same file. Not required by the fix; one dataclass replace.
6. **The dry check's design** (D-5): synthetic bars (tests._c1_fixtures, seed 11) over the sub-window
   2010-06-07..2011-09-30 on the pinned official 2010-2019 calendars, so every calendar-driven feature (NGS release
   times, overnight sessions) is exercised as in the run; each of the five non-exempt legs removed in turn rather than
   one (the prompt asked for one). A smoke run on SYNTHETIC calendars (scratch output) tested the script's mechanics
   before the review; the real dry check ran after the review, as the prompt orders. The expected outcome was written
   into STATE before the real run.
7. **Listing evidence** (D-6): only the two dates the exemption turns on (MBT 2021-05-03, BTC trade date 2017-12-18)
   were fetched and quoted verbatim; the long-established contracts' launch dates are marked [unverified]. Reason: the
   prompt's rule (a quote or [unverified]); no doubt exists for NQ, ZN, 6E, GC, ZC, CL, NG (Fable N-9 agreed).
8. **Review fixes in the text only** (R-1..R-5): S-1 and four notes taken as text precision; N-6 (a fixed result
   path) answered in the text, with no code change, because the fixed marker path is already the run-once guard.
9. **The start suite's three failures were treated as an invocation artifact** (D-7): the lead had set
   PYTHONPYCACHEPREFIX for the suite (the prompt's fresh-prefix rule is for harness commands; its suite command has
   none); the three bytecode tests in tests/test_harness_freeze.py then fail by construction. The file rerun without
   the prefix passed 17/17, and the end suite ran the prompt's exact command. The full start suite was not rerun.
10. **The statistic's two means** (D-8): gate0._b_test's `mean` (criterion 1) is the trade-level mean, its t_B the
    per-date mean; the freeze's wording ("per-date mean") fits t_B. The lead applied the frozen code as C1 and E.12
    did, and had Fable compute both readings; the verdict is FAIL under either.
11. **Times corrected from `date`** (process): three times in this stage the lead typed estimated times that ran ahead
    of the clock (12:24 for 11:57; 12:03-12:04 for 12:00; an end of "about 12:55" for 12:48:04); each was replaced
    from `date`, file mtimes or git.
12. **Commit scope**: both commits staged explicit paths (E.18's files, the two Fable scratch folders); the
    untracked pages of earlier stages, .claude/worktrees/ and other untracked files were left alone.

## 7. Decisions for the user (the lead's recommendation first)

1. **The NG near-miss: accept the closure.** C1b FAILED on its registered bar (section 1). Per the freeze's section 8,
   the NG near-miss is closed, Gate 0's reading stands, nothing more is built on v2's model, and N is 480.
   - Recommended: no further NG variant on the v2 model, horizon or threshold. A different NG hypothesis would be a new
     pre-registration counted from N = 480, and must first pass V31's cost-feasibility gate.
   - What it cannot say: a fail does not separate "never real" from "real only in the 2019-2024 LNG-era regime"
     (section 8). The 2010-2019 sign is not even positive on the per-date mean in either test.
2. **What comes next: wait for the AiTrader readout, as V31 says.** Nothing in E.18 changes that. The data owned
   (2010-2019 stores for 17 roots, 2019-2024 for 27) stay on disk; any reuse needs a new pre-registration.
3. **Freeze-writing lessons, for every future pre-registration.** Recommended as standing rules (the lead can add
   them to docs/ORCHESTRATION.md's stage template if the user agrees):
   - Define each statistic's "mean" explicitly (per trade or per date) in the pass bar. C1's section 5 says "per-date
     mean" while the frozen code's criterion 1 uses the per-trade mean; it did not matter here, but it could at a
     boundary.
   - Dry-run every frozen guard on the frozen reference against the expected data state before registering (E.17's
     F-1; done here, and already a memory rule).
   - When a later stage re-registers an old freeze, re-read every factual sentence of the old text against what has
     happened since (here: "never read" and the harness clause).
4. **Housekeeping (no urgency).** Untracked files from earlier stages remain (the reports/stage_e12 and stage_e13
   evidence pages, .claude/worktrees/). Recommended: commit the evidence pages in a separate "evidence pages" commit or
   add their folders to .gitignore, and remove stale worktrees that hold no unmerged work.

## 8. Session cost

Wall clock 11:41 to 12:48 PDT, 2026-10-10 (final commit 12:48:04) (one session, no pause, no usage-limit wait, no outage). Tokens are
summed from this session's transcript and its two subagent transcripts (reports/stage_e10_briefs/cost.py, per-field
final usage per message) up to 12:46:58 PDT; the lead's last steps after that (writing this return, the progress
entry and the final commit) are not in the count.

### Final ETA table (actuals; PDT; the initial estimate in brackets)

| # | Task | Owner | Model | Effort | Parallel or serial | Start-end | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Read prompt and context | lead | opus | xhigh | serial | 11:41-11:47 | 0:06 | in lead | done [with checks 0:10] |
| 0 | Start checks | lead | opus | xhigh | serial | 11:47:18-11:47:30 | 0:00 | in lead | done |
| 0 | Start suite (detached) | lead | opus | xhigh | parallel with 1-2 | 11:47:32-12:05:36 | 0:18 | in lead | 6913 passed, 3 failed (invocation artifact, file rerun 17/17) [0:17] |
| 1 | C1b text, diff, c1b.py, test, listing evidence | lead | opus | xhigh | serial | 11:48-11:57 | 0:09 | in lead | done [1:00] |
| 1b | Review brief, dry-check and freeze scripts | lead | opus | xhigh | parallel with 2 | 11:57-12:02 | 0:05 | in lead | done (not in the estimate) |
| 2 | Diff review | DiffReviewer-FableXHigh | fable | xhigh | after 1 | 11:58:44-12:14:08 | 0:15 | 2,484,866 | APPROVE WITH FIXES [0:30] |
| 2b | Fixes (R-1..R-5), text and diff regenerated | lead | opus | xhigh | serial | 12:14-12:15 | 0:01 | in lead | done [0:10] |
| 3 | Dry check | lead | opus | xhigh | serial | 12:16:02-12:16:05 | 0:00 | in lead | PASS [0:15] |
| 4 | Freeze manifest, commit b714751 | lead | opus | xhigh | serial | 12:17:07-12:17:35 | 0:00 | in lead | done [0:15] |
| 5 | Register (N 478 -> 480), evaluate once | lead | opus | xhigh | serial | 12:17:46-12:18:38 | 0:01 | in lead | FAIL; 34.7 s run [0:10] |
| 6 | Verdict recomputation | VerdictVerifier-FableXHigh | fable | xhigh | after 5 | 12:19:11-12:29:26 | 0:10 | 2,897,434 | VERIFIED WITH NOTES [0:30] |
| 7a | Return parts drafted | lead | opus | xhigh | parallel with 6 | 12:19-12:29 | 0:10 | in lead | done |
| 7b | End checks | lead | opus | xhigh | serial | 12:29:55-12:30:05 | 0:00 | in lead | all pass |
| 7c | End suite (detached) | lead | opus | xhigh | parallel with 7d | 12:30:09-12:46:32 | 0:16 | in lead | 6990 passed, rc 0 |
| 7d | STAGES, memory, cost, progress, return, commit | lead | opus | xhigh | serial | 12:30-12:48 | 0:18 | in lead (to 12:46:58) | done [7 total 0:50] |
| | **Stage total** | | | | | 11:41-12:48 | **1:07 work** | **45,253,221** | estimate [3:50]; no pause |

Lead versus workers: lead 39,870,921 tokens (88.1%), workers 5,382,300 (11.9%). By tier: opus 88.1%, fable 11.9%.
The estimate's guesses were long: step 1 took 9 minutes, not 60, and each Fable spawn 10-15 minutes, not 30.

### Tokens per model (session a6f2d97b's transcript and its 2 subagent transcripts, 2026-10-10 18:35Z to 19:46:58Z)

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,316 | 120,728 | 4,870,416 | 389,840 | 5,382,300 |
| claude-opus-5-5 | 288 | 213,963 | 39,236,246 | 420,424 | 39,870,921 |
| all | 1,604 | 334,691 | 44,106,662 | 810,264 | 45,253,221 |

Per spawn: DiffReviewer-FableXHigh (worker-xhigh, fable, xhigh) 2,484,866; VerdictVerifier-FableXHigh (worker-xhigh,
fable, xhigh) 2,897,434. Raw lines: reports/stage_e18_briefs/cost_raw.txt.

These are token counts from the transcripts, not plan-credit percentages; the session cannot read the /usage meter.
