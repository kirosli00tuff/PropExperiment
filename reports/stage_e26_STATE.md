# Stage E.26 STATE (housekeeping: data move, ACCOUNT_3, V45, Topstep rules)

Prompt: docs/prompts/STAGE_E.26.md. Lead: Opus 5.5 xhigh, ultracode on. Session 2819cf4f-44df-4b3e-b6eb-b8d43e270f7a.
Started 2026-10-21 02:06:27 PDT (date). Times PDT, from `date`.

## Data move status (read by E.28)

DATA MOVE: DONE (05:18 PDT). Destination root: /mnt/large-storage/market_data/PropExperiment/
New downloads go straight there (E.28: e.g. /mnt/large-storage/market_data/PropExperiment/<your layout>; it is the
same disk as the four moved stores). Links in the repo: data/sealed, data/processed_hist, data/processed_step2,
data/vendor/databento -> the same paths under the destination root. data/processed, data/vendor/release_pages and
data/vendor/index_history stay in the repo. Before any check that reads data: `mountpoint -q /mnt/large-storage`
(fstab nofail: an unmounted drive leaves dangling links).

## Task status

| Step | Status | Start | End | Artifacts |
|---|---|---|---|---|
| 0 Startup checks | done | 02:06 | 02:11 | reports/stage_e26_briefs/start_checks.txt (all as E.24 end; holdout unlocks 0; N 538; ledger 36402 lines 034a454b...; KEY3 absent from .env) |
| T1.1 inventory (3 sweeps + merge) | done: move 4 links (sealed, processed_hist, processed_step2, vendor/databento); processed, release_pages, index_history stay | 02:14 | 02:36 | reports/stage_e26_inventory.md, .json; reports/stage_e26_briefs/inv_*.md |
| Task 2 code (worktree) | done 05:12 (5-file patch: config.py, pull_step2.py PILOT_ONLY guard, new test file, 2 frozen tests; 48-file rerun 11 old failures + test_harness_freeze) | 02:14 | 05:12 | reports/stage_e26_briefs/task2_config.patch, task2_report.md |
| T1.2 seal check | done: identical on /mnt (seals may move) | 02:16 | 02:17 | reports/stage_e26_briefs/seal_check.py, seal_check.json |
| T1.3 move plan | done (plan, move_data.py tested, loader_reads.py dry run 27 roots 44 stores 0 errors) | 02:17 | 02:40 | reports/stage_e26_move_plan.md, .json; reports/stage_e26_briefs/move_data.py, loader_reads.py |
| Move plan review (Fable) | done: APPROVE AFTER FIXES, 0 BLOCKING, 7 SHOULD FIX, all accepted. Findings 1-4, 6, note 8 FIXED in move_data.py and before_after.sh, retested on a synthetic tree 03:07. Findings 5 and 7 (apply test and .gitignore edits BEFORE the before-checks, with a dangling-link assertion) NOT YET APPLIED | 02:40 | 03:07 | reports/stage_e26_briefs/review_moveplan.md |
| T1.4 before checks | rerun with the step-3 edits in place 05:11-05:14: identical to the first run (holdout JSON byte-equal, loader equal, checks equal; subset 285 passed 0 skipped); first run kept in before0/. sha256 manifest running 05:15 | 02:41 | | reports/stage_e26_briefs/before_*.txt, holdout_before*.json/txt, loader_before.json, find_before_*.txt, pytest_subset_before.out, move_manifest.jsonl |
| T1.5 move | done: 4 sources copied, verified at the destination from disk (4,742 entries), swapped to symlinks; 0 mismatches; asides kept in /home/kiros-li/e26_aside until T1.6 passes | 05:15 | 05:15 | reports/stage_e26_briefs/move_run.log, move_state.json |
| T1.6 after checks | done: link guard OK x4; holdout JSON byte-equal (all True, unlocks 0); loader equal apart from paths_resolved; find listings equal x4; subset 285 passed (= before); checks.sh identical incl. harness v13 and every freeze; git status identical (no data, no link) | 05:15 | 05:18 | reports/stage_e26_briefs/after_*.txt, holdout_after.json, loader_after.json, find_after_*.txt, pytest_subset_after.out |
| T1.7 move done | done: finalize deleted the 4 asides (finalize_run.log times); empty aside root removed; DONE line above; /mnt/large-storage/README.md line added | 05:18 | 05:18 | reports/stage_e26_briefs/finalize_run.log |
| Task 2 review (Fable) | FINAL: APPROVE (after A1/A6/B1/B2 fixes; v14 81121be8 verified); lead then fixed one E501 docstring line in pull_step2.py, v14 rebuilt 2e908c81 (same four entries), preflight OK, 305 tests passed, ruff clean | 05:12 | 05:35 | reports/stage_e26_briefs/review_config.md |
| Task 2 apply + commit with Task 3 | COMMITTED 95df9c6 (05:35): ACCOUNT_3 + PILOT_ONLY guard, harness v14 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1, V45, .gitignore, holdout test edits, key3 helper | 05:19 | 05:35 | commit 95df9c6 |
| Task 4 Topstep rules | done: R040 re-sourced (value false kept), 20 rules R215-R234 added (global.tier1_news_window.*, per-size caps), S42-S44; validate_rules OK; prop_econ tests 148 passed | 02:20 | 02:25 | reports/stage_e19_rules.json (sha256 01155d26... before ebc29f8b...), reports/stage_e26_briefs/refresh_rules.py, topstep_tier1.md, pages/topstep/, stage_e19_rules.before_e26.json |
| Task 3 V45 | committed in 95df9c6 | 05:21 | 05:35 | docs/DECISIONS.md |
| End checks + pytest | done: end checks = start except commit, v14 preflight OK, acct-3 line; suite 1 failed (known h6 v12 pin), 8090 passed, 5 skipped (3 + 2 E.24 broker imports), 3 xfailed, 28:20, min avail 3904 MB | 05:35 | 06:04 | reports/stage_e26_briefs/end_checks.txt, pytest_end.out |
| Return, progress, STAGES, commit | done: reports/E.26_RETURN.md (8 sections), progress entry, STAGES line, session cost; final commit 06:07 | 05:36 | 06:07 | reports/E.26_RETURN.md |

## Notes

- Conflict found 02:10: data/config.py is a frozen member of harness v13 (reports/stage_e2b_harness_freeze.json,
  category harness_code). Task 2 must edit it; Scope forbids changing a harness file. Lead ruling pending (see return
  section 6). Task 2 is coded in an isolated worktree and applied only after the T1.6 after-checks.
- 02:48 ruling: Task 2 needs harness members changed (data/config.py and the frozen tests tests/test_stage_e_config_keys.py,
  tests/test_e2b_pull_step2_e12.py, category stage_e_test). Lead ruling: harness v14 limited to the minimal set, built by the
  lead in the main tree after the T1.6 after-checks (which run on v13), Fable-reviewed before commit. Open choice 1.
- Note for E.28 (from ConfigCoder): pass account="acct-3" explicitly to BOTH SpendGate (its default is acct-1) and
  require_databento_key (its default is ACTIVE_ACCOUNT, acct-2), and use E.28's own session id (session caps sum every
  account's lines). Until the E.26 commit lands, acct-3 does not exist in data/config.py.

## RESUME HERE (usage limit at 03:07 PDT)

Nothing has moved. The destination root is reserved: nothing goes under /mnt/large-storage/market_data/ until DATA MOVE: DONE.
Next steps, in order:
1. Apply plan step 3 now (review finding 5): append the 3 slash-free lines to .gitignore; edit tests/test_holdout.py
   (TestRealStore rglob test) and tests/test_d1f_holdout2.py (test_i_..._survives_anywhere roots) to also scan
   symlinked dirs under data/, each with an assertion that no symlink under data/ is dangling (finding 7).
2. Move the first before-run outputs aside (before_* to before0_*), rerun `bash reports/stage_e26_briefs/before_after.sh before`.
3. `uv run python reports/stage_e26_briefs/move_data.py manifest reports/stage_e26_move_plan.json`.
4. `move_data.py move` (nice 10), then `before_after.sh after`, compare, then `move_data.py finalize`, then T1.7 DONE line.
5. Task 2: ConfigCoder follow-up 2 (PILOT_ONLY_ACCOUNTS guard in pull_step2) may be finished: check
   reports/stage_e26_briefs/task2_report.md "Follow-up 2" and task2_config.patch. Then apply the patch to the main tree,
   rebuild the harness manifest as v14 (only data/config.py, data/pull_step2.py and the two frozen tests may differ),
   and spawn ConfigReviewer-FableXHigh on the diff and the manifest diff.
6. Task 3: V45 from reports/stage_e26_briefs/V45_draft.md (fill MOVE, CAP 125.00, HARNESS v14). Commit Tasks 2+3.
7. End checks, full pytest (run_suite.sh pattern), return document, progress entry, STAGES line, final commit.
Done already: startup checks, T1.1 inventory, T1.2 seal check, T1.3 plan + review, Task 4 (rules record refreshed).

## Resumed 05:11 PDT (usage limit 03:07-05:10, a pause, not work)
- 05:11 step 1 done: .gitignore lines (check-ignore names lines 34-36 for the three links; databento under data/vendor/ line 17);
  test edits in tests/test_holdout.py and tests/test_d1f_holdout2.py (dangling-link assertion). First before-run kept in
  reports/stage_e26_briefs/before0/. Before-checks rerun started 05:11. ConfigCoder resumed for Follow-up 2.
- 05:21 E.28 note: ACCOUNT_3 code is applied in the working tree but NOT committed yet; harness is now v14 6dc0eda9... (any Stage E entry point needs that sha).
- 05:35 FOR E.28: ACCOUNT_3 is COMMITTED (95df9c6). Harness is v14 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1. Pass account="acct-3" to SpendGate AND require_databento_key, own session id and caps; spend bound per V45 item 2.

## STAGE E.26 COMPLETE (06:07 PDT)
Final commit "Stage E.26 data move and housekeeping" after 95df9c6. No push (the planner pushes). No worker or background job left running.
