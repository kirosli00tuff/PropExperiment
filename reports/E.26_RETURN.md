# Stage E.26 return: market data to LARGE STORAGE, ACCOUNT_3, V45, the Topstep rules record

Prompt: docs/prompts/STAGE_E.26.md. Lead: Opus 5.5 (claude-opus-5-5), effort xhigh, ultracode on, session
2819cf4f-44df-4b3e-b6eb-b8d43e270f7a. 2026-10-21, times PDT from `date`, file times and logs. Work 02:06-03:07 and
05:10-06:07; a usage-limit pause 03:07-05:10 is not work. STATE: reports/stage_e26_STATE.md.

## 1. Summary

- **Data moved.** data/sealed, data/processed_hist, data/processed_step2 and data/vendor/databento now live under
  /mnt/large-storage/market_data/PropExperiment/: 4,579 files, 9,693,260,747 bytes, mirrored paths, absolute
  symlinks at the old paths. Every file's sha256, mode, owner and mtime were verified at the destination, read from
  disk, before each swap. The originals were deleted only after the after-checks passed.
- **What stayed in the repo, and why.**
  - data/processed (303 MB): a link there changes a harness guard and fails a harness test.
  - data/vendor/release_pages: web pages plus scripts the D.1f preflight scans.
  - data/vendor/index_history: 11 tracked files.
- **Checks before and after the move were identical:**
  - the holdout status, byte for byte (unlocks 0);
  - harness v13 and every freeze verification;
  - the E.20 store hashes (34 stores);
  - a row-free loader preflight over 44 stores;
  - a 285-test data subset.
- **ACCOUNT_3.** acct-3 (DATABENTO_API_KEY3, cap $125, pilot-only: step-2 buys refuse it) is committed in 95df9c6
  with harness v14 (2e908c81...). Only data/config.py, data/pull_step2.py and two frozen tests differ from v13.
- **V45** records the move, ACCOUNT_3, the V34 correction and the V38 amendment.
- **Topstep.** reports/stage_e19_rules.json carries the Tier 1 news window from today's pages (PPI added
  2026-10-20); R040 holds.
- **Unchanged:** N 538; nothing bought or registered.

## 2. Guardrail evidence

### 2.1 Start checks (02:06-02:11; reports/stage_e26_briefs/start_checks.txt, sha256 26c117622bfac65f...)

```
$ uv run python -m data.holdout status (session start, tail)
    "unsealed_plaintext_present": [],
    "unlock_log_ok": true,
    "store_has_no_embargo_or_holdout2_rows": true,
    "unlocks_logged": 0,
    "all_ok": true
$ git status --short
(1,409 lines, every one "?? " untracked: no tracked file modified, nothing staged; full list in the file)
$ git log --oneline -3
71d667f docs: Stage E.26 (housekeeping) and E.28 (methods brief, ranking, pilot) prompts, V44
80c8f3c docs: V43 (V28 amended for order-book ML strategies; paper trading parked; pilot cap)
8da6bec Stage E.24 forward plumbing and E22-F2
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
$ wc -l ledger/trial_registrations.jsonl; sha256sum
9
25c04088fed9b1a2bd14a79512bedc8ab9764611aa2abd95e2a29829542aa302
$ E.14 C1 freeze inputs list (reports/stage_e14_c1_freeze_inputs.json; pinned 3356d676...)
list sha256 3356d67604245db99383215f1fb7f694d25a1beb71b0693a86faeb7243a5140e entries 43 mismatches ['reports/stage_e2b_harness_freeze.json']
$ E.16 freeze: ... verify --expected 5274aa97...
changed: screening/stage_e_verdict.py
changed: data/stage_e_bars.py
exit 1
$ E.18 C1b freeze: ... verify --expected 5ed208a2...
changed: reports/stage_e2b_harness_freeze.json
pin mismatch: reports/stage_e2b_harness_freeze.json
exit 1
$ E.20 store sha256 (17 roots ...) vs reports/stage_e17_run_manifest.json
stores checked 34 mismatches []
$ E.20 H6 freeze: ... verify 22e606f0...
manifest 22e606f0b74532e267a4155d93e295702ff86f6e8f4143236882f3c2f230e795 expected 22e606f0b74532e267a4155d93e295702ff86f6e8f4143236882f3c2f230e795 match True files 91 bad ['data/stage_e_bars.py']
exit 1
$ E.20 search freeze: ... verify --sha256 94ee86b0...
REFUSED (Refused): frozen file reports/stage_e2b_harness_freeze.json is missing or changed
exit 2
$ E.21 freeze: ... verify --sha256 0bb899e5...
freeze verified: 18 inputs
exit 0
$ E.23 freeze: ... verify --sha256 24dcf4dd...
freeze verified: 20 inputs, 5 ids
exit 0
$ E22-F1 frozen file set: sha256sum -c reports/stage_e22_f1_files.sha256 (list pinned bb3bf3b3...)
all 30 files OK
exit 0
$ .env variable names (status only; values never read)
DATABENTO_API_KEY1 empty
DATABENTO_API_KEY2 non-empty
```

The E.14 inputs list, E.16, E.18, E.20 H6 and E.20 search lines fail as they have since harness v13 (memory note
"v13 breaks earlier freezes"; identical in E.24's checks). DATABENTO_API_KEY3 was absent from .env at the start
(name check only).

### 2.2 End checks (05:35:38-05:35:59; reports/stage_e26_briefs/end_checks.txt, sha256 23c0803b4d73c034...)

Run with the v14 sha (`bash reports/stage_e26_briefs/checks.sh 2e908c81...`). Every line equals the start block in
2.1, holdout keys (unlocks_logged 0 everywhere), REGISTRATION.md 0 bytes, ledger 36402 lines sha256 034a454b...,
N = 538 (9 lines, 25c04088...), every freeze line and `stores checked 34 mismatches []` included, except these,
verbatim from `diff` (git status lines compared separately):
```
>  M reports/stage_e19_rules.json
> 95df9c6 feat: Stage E.26 ACCOUNT_3 (harness v14), V45, data-move git and test hygiene
< 8da6bec Stage E.24 forward plumbing and E22-F2
< $ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4
< preflight OK: dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4
> $ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
> preflight OK: 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
> acct-3: spent 0.000000 cap 125.00 headroom 125.000000
```
`git status --short` at the end: 1,469 untracked lines (the stage's own new files under reports/ added to the
1,409 of the start, plus E.28's) and one tracked modification, ` M reports/stage_e19_rules.json` (Task 4, committed
in the final commit). No data path and no link appears. DATABENTO_API_KEY3 is still absent from .env (name check
only): E.28 or the user adds it with scripts/set_databento_key3.sh. The full holdout status JSON after the move:
reports/stage_e26_briefs/holdout_after.json (byte-equal to the before copy).

pytest (`uv run pytest -q -p no:cacheprovider`, nice 10, memory watchdog at 2 GB; reports/stage_e26_briefs/run_suite.sh,
output reports/stage_e26_briefs/pytest_end.out), on the final code except the uncommitted Task 4 record, verbatim:
```
start 05:35:59 avail_mb 9244
FAILED tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha
1 failed, 8090 passed, 5 skipped, 3 xfailed, 54 warnings in 1700.96s (0:28:20)
min_avail_mb 3904
rc 1 end 06:04:27
```
The one failure is the known one (it pins harness v12 and has failed by design since v13; E.23's end run and E.24's
start run show the same line). Skips: 3 as in E.24's start run, plus 2 from E.24's forward tests, verified with
`-rs`: `SKIPPED [1] tests/test_forward_ibkr_vendor_contract.py:14: could not import 'ib_async'` and
`SKIPPED [1] tests/test_forward_alpaca_contract.py:16: could not import 'alpaca'`. No skip comes from a dangling
link (the data-path subset had 0 skips after the move, and the two edited holdout tests fail rather than skip on one).

### 2.3 Order of events (PDT)

| Time | Event |
|---|---|
| 02:06 | start; holdout status (unlocks 0); prompt read |
| 02:06-02:11 | start checks |
| 02:10 | conflict found: data/config.py is a v13 harness member (Task 2 vs scope); STATE noted |
| 02:14 | inventory workflow (3 sweeps + merge) and ConfigCoder (worktree) spawned |
| 02:16 | T1.2 seal check on /mnt (synthetic): identical; cleaned up |
| 02:17-02:19 | move tool written and tested on a synthetic tree |
| 02:20-02:22 | TopstepRulesReader fetched 3 Topstep pages |
| 02:22-02:25 | Task 4: rules record refreshed (lead), 148 prop_econ tests passed |
| 02:27-02:36 | inventory merged |
| 02:38 | loader check dry run (27 roots, 44 stores, 0 errors) |
| 02:40 | move plan written; MovePlanReviewer spawned |
| 02:41-02:43 | first before-checks (kept in before0/) |
| ~02:58 | ConfigCoder: 4 new failures, 3 in frozen harness tests; lead ruling: v14 minimal set |
| ~03:05 | move plan review: APPROVE AFTER FIXES (7 SHOULD FIX); fixes 1-4, 6 applied and retested |
| 03:07-05:10 | **usage-limit pause** (ConfigCoder cut mid-follow-up; resumed 05:11) |
| 05:11 | step-3 edits (.gitignore, two holdout tests) applied before the before-checks |
| 05:11-05:14 | before-checks rerun: identical to the first run |
| 05:12 | ConfigCoder follow-up 2 done (pilot-only guard); ConfigReviewer spawned |
| 05:14:24-05:14:43 | sha256 manifest (4,579 files) |
| 05:15:19-05:15:45 | move: copy, verify from disk, swap, x4 |
| 05:15:54-05:18:17 | after-checks: all identical |
| 05:18:35 | finalize: originals deleted; DATA MOVE: DONE in STATE |
| 05:19 | Task 2 patch applied in the main tree; harness v14 built |
| 05:21-05:22 | V45 written |
| ~05:26-05:30 | ConfigReviewer: APPROVE AFTER FIXES, fixes applied, FINAL: APPROVE |
| 05:35 | commit 95df9c6 (Tasks 2 and 3) |
| 05:35-06:04 | end checks; full suite |

## 3. Results

### 3.1 Inventory (reports/stage_e26_inventory.md, .json; sweeps reports/stage_e26_briefs/inv_disk.md, inv_code.md, inv_manifests.md)

| Source | Bytes | Files | Git | Decision |
|---|---:|---:|---|---|
| data/vendor/databento | 8,608,399,283 | 4,461 | ignored | moved (one link: VENDOR_ROOT) |
| data/processed_step2 | 592,497,579 | 31 | ignored | moved (STEP2_ROOT) |
| data/processed_hist | 464,057,539 | 17 | ignored | moved (HIST_ROOT) |
| data/sealed | 28,306,346 | 70 | ignored | moved (SEALED_BASE) |
| data/processed | 303,035,283 | 49 | ignored | stays (H-01: ml_route/store.py:59-65 guard and a harness test) |
| data/vendor/release_pages | 153,575,775 | 4,263 | ignored | stays (D.1f preflight scans its 28 scripts; mtimes read) |
| data/vendor/index_history | 1,101,859 | 29 | mixed (11 tracked) | stays (a link would show tracked files deleted) |
| reports/stage_e22_microbook/cache, gex/DIX.csv, ~/.cache/propexp_e14_c1 | small | | | stay (outside scope; DIX.csv path-frozen) |

Hazards found (14, inventory section 2) and how each was handled: reports/stage_e26_move_plan.md section 3. The
decisive ones: realpath-prefix guards fail open if a link sits below a guarded root (H-00), so links sit exactly at
the four roots; ml_route refuses per-product links (H-02); git ignores a trailing-slash pattern for a symlink
(H-06); scans that start above a link narrow (H-04); a `nofail` mount loss leaves dangling links (H-03).

### 3.2 Seal check (T1.2; reports/stage_e26_briefs/seal_check.py, seal_check.json)

A synthetic holdout-1 store (random blobs, a 3-row parquet, a manifest with the real field names) verified with
data.holdout.verify_seal on the repo's ext4, on /mnt/large-storage after `cp -a`, and through a symlink:
`{"all_ok": {"verify_control": true, "verify_large": true, "verify_via_symlink": true}, "reports_equal": true,
"cp_a_preserves_stat": true, "ro_scheme_same": true, "is_sealed_raw_same": true, "symlink_detects_plaintext": true}
cleaned_up True`. So the sealed stores moved too.

### 3.3 Move plan (reports/stage_e26_move_plan.md, .json) and tool (reports/stage_e26_briefs/move_data.py)

Order: data/sealed, data/processed_hist, data/processed_step2, data/vendor/databento (smallest first). Per source:
`cp -a --no-target-directory` to /mnt/large-storage/market_data/PropExperiment/<path>; `sync`; every manifest entry
re-checked at the destination (path set, kind, mode, uid, gid; files: size, mtime_ns, sha256 after
POSIX_FADV_DONTNEED so the bytes are read from disk); `os.rename` to /home/kiros-li/e26_aside (same filesystem);
`os.symlink`; link check. Originals deleted only by `finalize` after the after-checks, and only for a link that
resolves to its own destination. Resumable states pending/copied/verified/swapped/finalizing/finalized; rollback
re-verifies before any re-swap (review fixes). Repo edits required by the links, made before the before-checks:
.gitignore lines `/data/processed_step2`, `/data/processed_hist`, `/data/sealed`; tests/test_holdout.py and
tests/test_d1f_holdout2.py scan through symlinked stores and fail on a dangling link.

### 3.4 Checksum manifest (T1.4; reports/stage_e26_briefs/move_manifest.jsonl, sha256 778ec6218cdf5ed6...)

```
data/sealed {'entries': 83, 'files': 70, 'bytes': 28306346, 'symlinks': 0, 'hardlinked_files': 0}
data/processed_hist {'entries': 37, 'files': 17, 'bytes': 464057539, 'symlinks': 0, 'hardlinked_files': 0}
data/processed_step2 {'entries': 63, 'files': 31, 'bytes': 592497579, 'symlinks': 0, 'hardlinked_files': 0}
data/vendor/databento {'entries': 4559, 'files': 4461, 'bytes': 8608399283, 'symlinks': 0, 'hardlinked_files': 0}
manifest 778ec6218cdf5ed6f899f4aaf2571237cb7138545d44013985dc00cdd8f14486 files 4579 bytes 9693260747
```
Move log (reports/stage_e26_briefs/move_run.log), verbatim:
```
start 05:15:19
data/sealed copied and verified 83 entries
data/sealed swapped: symlink -> /mnt/large-storage/market_data/PropExperiment/data/sealed
data/processed_hist copied and verified 37 entries
data/processed_hist swapped: symlink -> /mnt/large-storage/market_data/PropExperiment/data/processed_hist
data/processed_step2 copied and verified 63 entries
data/processed_step2 swapped: symlink -> /mnt/large-storage/market_data/PropExperiment/data/processed_step2
data/vendor/databento copied and verified 4559 entries
data/vendor/databento swapped: symlink -> /mnt/large-storage/market_data/PropExperiment/data/vendor/databento
move complete: {'data/sealed': 'swapped', 'data/processed_hist': 'swapped', 'data/processed_step2': 'swapped', 'data/vendor/databento': 'swapped'}
rc 0 end 05:15:45
```

### 3.5 Before and after checks (T1.4, T1.6; reports/stage_e26_briefs/before_*, after_*, holdout_*, loader_*, find_*, pytest_subset_*)

Before (05:11-05:14, with the step-3 edits in place) and after (05:15:54-05:18:17), verbatim:
```
$ step 0 preconditions (after)
/mnt/large-storage is a mountpoint
open data handles: 0
$ link guard
OK   data/sealed -> /mnt/large-storage/market_data/PropExperiment/data/sealed
OK   data/processed_hist -> /mnt/large-storage/market_data/PropExperiment/data/processed_hist
OK   data/processed_step2 -> /mnt/large-storage/market_data/PropExperiment/data/processed_step2
OK   data/vendor/databento -> /mnt/large-storage/market_data/PropExperiment/data/vendor/databento
OK   MES_v_0 reachable
$ holdout field values, before and after (identical)
True 0 True True 0 True [] {'MCL': (True, True, []), 'MGC': (True, True, []), 'MHG': (True, True, []), 'NG': (True, True, [])}
$ cmp holdout_before.json holdout_after.json
holdout JSON byte-equal (sha256 44364c3828557e48... both)
$ loader_reads.py (base_rules.store.preflight, row-free; DBN header), before and after
roots 27 stores 44 errors 0 dbn ohlcv-1m ['MES.v.0']
loader equal apart from paths_resolved: True
$ find listings (files: mode, size, mtime; dirs: mode, mtime), before vs after
same find_after_data_processed_hist.txt
same find_after_data_processed_step2.txt
same find_after_data_sealed.txt
same find_after_data_vendor_databento.txt
$ pytest subset (8 data-path files), before and after
285 passed in 110.73s (0:01:50)
285 passed in 109.53s (0:01:49)
$ checks.sh before vs after (date and git status lines excluded)
checks identical
$ git status lines before vs after
(no difference: no data path and no link appears)
```
The checks.sh output in both runs contains, among the lines quoted in 2.1: `preflight OK: dd2bcc60...` (harness
v13), the K1-K8, E.1, E.2a, v2, E.21, E.23 and F1 verifications, and `stores checked 34 mismatches []`. Finalize
(05:18:35) deleted the four originals; `git status --short | grep -cE '^\?\? data/|^ M data/|^ D data/'` = 0.

### 3.6 Config diff and tests (Task 2; commit 95df9c6)

- data/config.py: ACCOUNT_3_ID "acct-3"; ACCOUNT_3_CAP_USD 125.00 (sourced comment: V44, U5); the registry entry
  (no external ledger; "the temporary E.28 pilot account (V44), wiped by the user after the download is verified");
  DATABENTO_API_KEY3 in DATABENTO_KEY_ENV_BY_ACCOUNT; PILOT_ONLY_ACCOUNTS = frozenset({ACCOUNT_3_ID}). acct-1,
  acct-2, LEGACY_ACCOUNT_ID and ACTIVE_ACCOUNT unchanged.
- data/pull_step2.py: require_buy_caps refuses a pilot-only account (Step2Error) before any key load or vendor
  call; docstrings and the --buy usage message updated (review A1, A6). pull_hist already refused acct-3.
- tests/test_e26_account3.py (new, fake keys only); minimal edits to the frozen tests/test_stage_e_config_keys.py
  (the key map includes acct-3; the "unregistered" example is now acct-9) and tests/test_e2b_pull_step2_e12.py
  (the quote summary lists acct-3).
- Harness v14: reports/stage_e2b_harness_freeze.json sha256
  2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1; against v13 (kept at
  reports/stage_e26_briefs/harness_v13_manifest.json): files added none, removed none, changed exactly
  data/config.py, data/pull_step2.py, tests/test_e2b_pull_step2_e12.py, tests/test_stage_e_config_keys.py;
  categories unchanged (1,065 files). `preflight OK: 2e908c81...`; v13 now refused.
- scripts/set_databento_key3.sh: committed after the review fixes (EXIT trap removes the temp file; dedupe of
  export/indented forms; CR stripped; refuses a .env directory; mv -T).
- Tests in the main tree (05:31-05:35): the Task 2 set and the two holdout files, 305 passed; ruff clean on the
  edited files (data/config.py's 7 E501 lines predate the stage). Worker runs in its worktree (48 files): 12
  failed, 1,443 passed, 1 skipped, the 12 being the 11 failures that also fail at HEAD in a worktree (9
  test_compute_remote_e2e, 1 test_d1f_holdout2 real stores, 1 test_h6_rod_run pinning v12) plus
  test_harness_freeze before the v14 rebuild.
- DATABENTO_API_KEY3: absent from .env at start (name check only; the value was never read); end: see 2.2.

### 3.7 Topstep rules record (Task 4)

reports/stage_e19_rules.json (sha256 ebc29f8b... -> 01155d26...; the old file kept at
reports/stage_e26_briefs/stage_e19_rules.before_e26.json; script reports/stage_e26_briefs/refresh_rules.py).
Source, fetched 2026-10-21 02:20:34 PDT, help.topstep.com/en/articles/13613539 (dateModified 2026-10-20T19:42:21Z),
quoted: "Ahead of Tier 1 News Events (for example, CPI, FOMC, NFP, PPI), Topstep temporarily restricts new opening
positions on equity index products and metals in SIM to protect Traders from extreme volatility." ; "Minis (ES,
RTY, YM, NQ, NKD, GC, SI, HG, PL): No new opening transactions permitted during the 10-minute window surrounding
the release (5 minutes before, 5 minutes after)." ; "Micros (MES, M2K, MYM, MNQ, MGC): Opening transactions limited
to 1, 3, 6, 9, and 15 contracts for the $25K, $50K, $100K, $150K, and $250K account sizes, respectively, during
the window (see table below)" ; "Existing Positions: Traders holding existing positions in equity index products
and metals prior to 5 minutes before the news event may keep them open and manage them through the Tier 1 News
Events window." Page 8284211 (dateModified 2026-10-15) no longer has E.19's sentence "Topstep doesn't require you
to flatten positions during economic releases"; page 10305426 (P06) unchanged (2026-06-10). Changes: R040
(global.news_flatten_required = false) keeps its value with source S42 and the "Existing Positions" quote; 20
rules R215-R234 add global.tier1_news_window.* (window, products, pending orders, events in CT, enforcement) and
per-size Combine caps (micros 3/6/9, MHG/SIL 2/5/7) and XFA caps by balance; sources S42-S44; a "refreshes" record.
validate_rules passes (214 -> 234 rules); prop_econ tests 148 passed. E.19's simulator was not rerun. Since E.25:
PPI was added to the window on 2026-10-20 and the existing-positions sentence now names equity index products and
metals (reports/stage_e26_briefs/topstep_tier1.md).

### 3.8 V45 (Task 3)

docs/DECISIONS.md, last entry, five records: the data move; ACCOUNT_3 with the harness v14 consequence and the
pilot's spend bound (V44's "all of its funds", superseding V43's USD 100 for acct-3); V34's "unsized" reason
corrected with E.25's post-publication evidence; V38's sentence amended to name the three working-paper effects
(pre-refunding ZN, pre-FOMC ZN, the ES 3rd-Friday reversal) as exceptions that cannot be tested with adequate
power, the closure standing; the Topstep record.

## 4. Delegation record

Routing per CLAUDE.md; the agent file sets effort, the model is passed per call. Times from the transcripts (first
and last message, PDT); tokens summed per message from the transcripts (reports/stage_e26_briefs/cost.py, final
usage per message), never estimated. At most 5 workers ran at once (cap 6).

| Agent (description) | Agent file / route | Model | Effort | Task | Start | End | Tokens (total; output) | Status |
|---|---|---|---|---|---|---|---|---|
| DataInvDisk-OpusHigh | workflow agent | opus | high | T1.1 sweep A (disk) | 02:14 | 02:20 | 4,038,814; 33,141 | done |
| DataInvCode-OpusHigh | workflow agent | opus | high | T1.1 sweep B (code references) | 02:14 | 02:27 | 19,011,261; 72,429 | done |
| DataInvManifests-OpusHigh | workflow agent | opus | high | T1.1 sweep C (manifests, verifiers) | 02:14 | 02:25 | 15,498,880; 63,041 | done |
| DataInvMerge-OpusHigh | workflow agent | opus | high | T1.1 merge + completeness critic | 02:27 | 02:36 | 4,460,364; 45,313 | done |
| ConfigCoder-OpusXHigh | worker-xhigh, isolated worktree | opus | xhigh | Task 2 code and tests; follow-ups 1 (frozen tests) and 2 (pilot-only guard) | 02:14 | 05:12 | 28,122,365; 121,125 | done (cut by the usage limit at 03:07 mid follow-up 2, resumed 05:11 with SendMessage) |
| TopstepRulesReader-OpusMed | worker-medium | opus | medium | Task 4: fetch 3 Topstep pages, quotes, diff vs E.25 | 02:20 | 02:22 | 1,086,590; 10,611 | done |
| MovePlanReviewer-FableXHigh | worker-xhigh | fable | xhigh | T1.3 independent review of the move plan and tool | 02:40 | 03:05 | 7,782,928; 93,793 | done: APPROVE AFTER FIXES |
| ConfigReviewer-FableXHigh | worker-xhigh | fable | xhigh | Task 2 review, v14 diff, final confirmation | 05:13 | 05:30 | 3,433,527; 65,110 | done: FINAL APPROVE |
| lead | main session | opus | xhigh | startup, T1.2-T1.7, Tasks 3-4, rulings, synthesis | 02:06 | 06:07 | see section 8 | |

Deviations from the prompt's delegation plan: T1.1 used four agents (three sweeps and a merge) instead of one
DataInventory worker (ultracode; open choice 7); a TopstepRulesReader was added for a fresh fetch (open choice 7);
ConfigCoder needed two follow-ups (frozen tests; the pilot-only guard), sent with SendMessage as small briefs.

## 5. Verification

### MovePlanReviewer-FableXHigh (reports/stage_e26_briefs/review_moveplan.md): APPROVE AFTER FIXES, 0 BLOCKING

| # | Finding | Ruling | Fix |
|---|---|---|---|
| 1 | SHOULD FIX: after rollback, move re-swaps the destination without re-verifying; finalize then deletes the only verified copy (reproduced) | accepted | rollback sets state "copied"; move re-verifies a "copied" destination before any swap (retested: a flipped byte after rollback is caught) |
| 2 | SHOULD FIX: rollback misses half-swapped states (crash between rename and symlink) | accepted | "swapped" written right after os.symlink; rollback also handles verified + aside present (retested) |
| 3 | SHOULD FIX: finalize deletes the aside when the link points at a wrong existing target (reproduced) | accepted | finalize requires src.resolve() == its own destination (retested: refused) |
| 4 | SHOULD FIX: interrupted finalize + rollback restores a partial tree (reproduced) | accepted | "finalizing" state before rmtree; rollback refuses up front if any source is finalizing (retested) |
| 5 | SHOULD FIX: apply test and .gitignore edits before the before-checks | accepted | applied at 05:11; before-checks rerun (identical to the first run) |
| 6 | SHOULD FIX: find %s on directories differs after cp -a (spurious rollback) | accepted | listing prints sizes for files only |
| 7 | SHOULD FIX: edited tests pass vacuously on a dangling link | accepted | both tests assert no dangling link under data/ |
| 8 | NOTE: resume and precondition messages | accepted in part | mount, same-device and free-space preconditions in code; problems file appended |
| 9-13 | NOTEs: what is verified; layout safe; what stays is right; E.28 concurrency; plan text | noted | STATE line "destination root reserved" written before the move; holdout status is fail-closed on a lost mount via holdout_blob_ok (a correction to the inventory's H-03) |

### ConfigReviewer-FableXHigh (reports/stage_e26_briefs/review_config.md): APPROVE AFTER FIXES, then FINAL: APPROVE

| # | Finding | Ruling | Fix |
|---|---|---|---|
| A1 | SHOULD FIX: the step-2 quote summary's combined headroom includes acct-3's $125 that step 2 may not spend | accepted, option (a) | accounts_summary docstring states pilot-only accounts are listed but not spendable by step 2 |
| A2-A3 | NOTE: acct-1/acct-2 unchanged; acct-3 selectable; E.28 needs no config edit (SpendGate or pull_mes.RequestCappedGate with account="acct-3", own session id and caps) | confirmed | none |
| A4 | NOTE: say in V45 whether V43's USD 100 or V44's "all funds" governs the pilot | accepted | V45 item 2: V44's "all of its funds" governs acct-3 |
| A5 | NOTE: the pilot-only guard covers every buy path in data/ and refuses before any key or client use | confirmed | none |
| A6 | NOTE: stale --account text in pull_step2.py | accepted | docstring line and the --buy message list non-pilot accounts only |
| A7-A8 | NOTE: tests fake-key only, frozen-test edits minimal; harness impact | confirmed | none |
| B1 | SHOULD FIX: the key helper leaves a .env.XXXXXX copy of the key if it fails between mktemp and mv (reproduced) | accepted | EXIT trap |
| B2 | NOTE: dedupe of export/indented forms, CR, .env as a directory | accepted | the reviewer's validated replacement, verbatim |
| C | v14 verified independently: only the four expected entries changed; breaks only trigger_hold's v13 pin and before_after.sh's v13 constant | accepted | trigger_hold left pinned (E.23 freeze member; decision 2); end checks run with the v14 sha |
| D | final: the fixes match, v14 81121be8 verified, V45 item 2 accurate; non-blocking: an E501 line and V45 not naming trigger_hold's pin | accepted | the lead fixed the E501 line (pull_step2.py docstring) and rebuilt v14 once more (2e908c81, the same four entries, preflight OK, 305 tests passed); V45 names the trigger_hold pin |

Numbers entering a verdict: none (no screen, no DSR/PBO, N unchanged). The checksum comparisons were done by the
tool and repeated by the independent find listings and the holdout/freeze verifiers.

## 6. Open choices (decided by the lead, with the reason)

1. **Task 2 as a harness v14, against the prompt's scope line "does NOT change any freeze, harness file or frozen
   member".**
   - Why it was unavoidable: data/config.py is a v13 harness member, and Task 2 orders it changed. The registry,
     the key map and pull_step2's account summary all iterate the same table, so two frozen tests that pinned a
     two-account registry fail with any third account.
   - Why it was done fully: half-applying (config changed, manifest at v13) would leave every Stage E entry point
     refusing and four failing tests. The harness manifest's own notes prescribe a rebuild for a spend-policy
     change in data/config.py, and E.28's purchase today depends on ACCOUNT_3.
   - How it was limited: v14 changes exactly four entries. It was built after the move's after-checks, so those
     ran on v13. It was Fable-reviewed, independently verified, and approved.
2. **ACCOUNT_3_CAP_USD = 125.00.**
   - Where the figure comes from: the credit a new Databento account opens with (U5: acct-2 opened with $125.00).
     It is an upper bound; the balance at purchase governs.
   - Why it is set here: E.28 may not edit data/config.py.
   - V45 states that V44's "all of its funds" bounds the pilot, superseding V43's USD 100 for acct-3 (review A4).
3. **A pilot-only guard in code** (PILOT_ONLY_ACCOUNTS; pull_step2 refuses acct-3). V44 limits acct-3 to the pilot,
   and the worker found that pull_step2 --buy --account acct-3 could otherwise spend about $4 on training-window
   data once v14 existed. It is one more harness file, inside the same v14.
4. **Moved:** data/sealed, data/processed_hist, data/processed_step2 and data/vendor/databento, each as one link
   exactly at its guarded root (inventory H-00, H-02).
   **Stayed:**
   - data/processed: H-01, a harness guard and test.
   - data/vendor/release_pages: preflight scripts and mtimes.
   - data/vendor/index_history: tracked files. Because of these, data/ and data/vendor stay real directories.
   - The sealed stores moved because T1.2 found no difference.
5. **Repo edits the links require**, made before the before-checks (review 5):
   - .gitignore gets slash-free entries (tracked; chosen over .git/info/exclude so a clone or bundle never stages
     the links).
   - tests/test_holdout.py and tests/test_d1f_holdout2.py scan through the links and fail on a dangling one.
     Neither file is in any freeze.
6. **Move mechanics.**
   - Originals go to an aside root outside the repo, on the same filesystem (so neither git nor the harness scan
     sees them).
   - They were deleted only after the after-checks, which is stricter than the prompt's "after its copy is
     verified and its symlink is in place".
   - Verification reads from disk (POSIX_FADV_DONTNEED after sync), not from the page cache.
7. **Extra delegation for completeness (ultracode).**
   - T1.1 ran as three independent sweeps (disk, code, manifests) plus a merge with a completeness critic,
     instead of one DataInventory worker.
   - TopstepRulesReader-OpusMed re-fetched the three Topstep pages today rather than reusing E.25's copies. The
     page had changed on 2026-10-20 (PPI added).
8. **Task 4 ran early (02:20-02:25)**, while the inventory ran: independent of Tasks 1-2, and E.28's ranking reuses
   the refreshed record. The Tier 1 window went into new schema leaves, each with one sourced rule. The schema
   version is unchanged and validate_rules accepts extra leaves. R040 keeps value false: flattening is still not
   required.
9. **Two commits.** 95df9c6 (Tasks 2 and 3, plus the move's .gitignore and test edits) was made as soon as the
   config review approved, so E.28 could use ACCOUNT_3. The final commit carries the rest.
10. **trigger_hold/events.py keeps its v13 pin.** It is a member of the E.23 freeze, so E.23's runners refuse under
    v14 until the user decides (decision 2).
11. **The final v14 (2e908c81) differs from the Fable-confirmed v14 (81121be8)** only by a one-line docstring wrap
    (an E501 the reviewer flagged as non-blocking). The lead verified it: same four entries, preflight OK, 305
    tests passed, ruff clean. It was not sent back for a third review.
12. **V45 has a fifth record** (the Topstep refresh) and the pilot spend-bound sentence; the prompt listed three
    topics.
13. **The start and end `git status --short` blocks are summarized by count** (1,409 untracked lines, mostly earlier
    stages' saved pages). The full lists are in start_checks.txt and end_checks.txt.
14. **A line was added to /mnt/large-storage/README.md** (outside the repo) naming market_data/PropExperiment and
    repeating that no secret goes on that drive.
15. **The T1.2 probe and the move-tool tests** ran in scratch directories at the top of /mnt/large-storage
    (_e26_sealcheck, _e26_movetest, _e26_mt2) and under /home/kiros-li. All were deleted and checked gone.
16. **ConfigCoder ran in an isolated git worktree**, so the main tree stayed on v13 until the after-checks were
    done.

## 7. Decisions for the user (each with a recommendation)

1. **Keep harness v14 (2e908c81...) or revert Task 2.**
   - **Recommendation:** keep v14. It is the minimal consequence of the account you asked for: four files, all
     reviewed.
   - From now on, every Stage E entry point (`--harness-sha256`) takes the v14 sha.
   - To revert instead: revert commit 95df9c6. That removes ACCOUNT_3, which E.28's purchase needs.
2. **E.23's trigger_hold v13 pin** (trigger_hold/events.py:69, a member of the E.23 freeze).
   - **Recommendation:** leave it. E.23 is closed and its verdict recorded.
   - If its runners must ever run again, do it as a registered amendment that bumps the pin to v14 and records
     the freeze change.
3. **A fail-closed mount check.** The drive is mounted `nofail`, so after a boot without it the four links dangle.
   - Today the holdout status fails closed (holdout_blob_ok), and so do the two edited tests.
   - Other checks fail on missing files rather than passing, but a few `skipif` tests would skip.
   - **Recommendation:**
     - Add `mountpoint -q /mnt/large-storage` to the session-start invariants in CLAUDE.md now.
     - At the next harness bump, add a guard in data/config.py that refuses to resolve a data root whose link
       dangles.
4. **data/processed stays in the repo (303 MB).**
   - **Recommendation:** keep it there. Moving it needs ml_route/store.py's research-root guard to compare
     unresolved paths, which is a harness change for a later stage.
5. **The pilot's spend bound.** V45 says V44's "all of acct-3's funds" (balance less a few dollars of margin, under
   the $125 account cap) governs, superseding V43's USD 100 for this account.
   - **Recommendation:** confirm. If you want USD 100 to bind instead, tell E.28 to set its session cap to 100.
6. **After E.28 writes "ACCOUNT_3 SAFE TO WIPE".** Wipe the Databento account, then delete the
   DATABENTO_API_KEY3 line from .env yourself.
   - **Recommendation:** yes, in that order. The acct-3 registry entry can stay, since its cap and the pilot-only
     guard keep it inert, or a later stage can remove it.
7. **Paths in records written from now on.**
   - New holdout seals, purchases and run outputs may record /mnt/... absolute paths (inventory H-05).
   - Existing records and every verifier are unaffected.
   - **Recommendation:** accept. When a later stage rebuilds a freeze, prefer repo-relative paths where its code
     allows.
8. **Push.** Per the prompt, the planner pushes 95df9c6 and the final commit. Nothing was pushed here.

## 8. Session cost

Wall clock 02:06-06:07 PDT = 4 h 01 min, of which the usage-limit pause 03:07-05:10 (2 h 03 min) is not work: work
time about 1 h 58 min (02:06-03:07 and 05:10-06:07). Tokens from this session's transcripts (main .jsonl plus
subagents/**, including the four workflow agents), per message at its final usage (reports/stage_e26_briefs/cost.py,
a copy of reports/stage_e10_briefs/cost.py that also globs the workflow agents; output cost_out.txt), through
06:06 PDT (the final commit's few messages after that are not counted). Never estimated.

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---:|---:|---:|---:|---:|
| claude-opus-5-5 | 1,384 | 619,133 | 151,390,494 | 3,015,397 | 155,026,408 |
| claude-fable-5-1 | 1,932 | 158,903 | 10,571,879 | 483,741 | 11,216,455 |
| all | 3,316 | 778,036 | 161,962,373 | 3,499,138 | 166,242,863 |

Per worker spawn: DataInvDisk-OpusHigh (workflow, opus high) 4,038,814; DataInvCode-OpusHigh (workflow, opus high)
19,011,261; DataInvManifests-OpusHigh (workflow, opus high) 15,498,880; DataInvMerge-OpusHigh (workflow, opus
high) 4,460,364; ConfigCoder-OpusXHigh (worker-xhigh, opus) 28,122,365; TopstepRulesReader-OpusMed (worker-medium,
opus) 1,086,590; MovePlanReviewer-FableXHigh (worker-xhigh, fable) 7,782,928; ConfigReviewer-FableXHigh
(worker-xhigh, fable) 3,433,527. Workers 83,434,729 (the sum of the eight rows); lead 82,808,134.

Delegation share: lead 49.8%, workers 50.2%. By tier: Opus 93.3% (lead 49.8%, Opus workers 43.4%), Fable 6.7%.
97.4% of all tokens are cache reads.

### Final ETA table (actuals; the initial estimate in the last column)

| # | Task | Owner | Model | Effort | Start | End | Time | Tokens | Status, deviations | Initial ETA |
|---|---|---|---|---|---|---|---|---:|---|---|
| 0 | Startup checks | lead | opus | xhigh | 02:06 | 02:11 | 5 min | lead | done | 15 min |
| 1a | T1.1 sweep A, disk | DataInvDisk-OpusHigh | opus | high | 02:14 | 02:20 | 6 min | 4,038,814 | done | 25 min |
| 1b | T1.1 sweep B, code | DataInvCode-OpusHigh | opus | high | 02:14 | 02:27 | 13 min | 19,011,261 | done | 25 min |
| 1c | T1.1 sweep C, manifests | DataInvManifests-OpusHigh | opus | high | 02:14 | 02:25 | 11 min | 15,498,880 | done | 25 min |
| 1d | T1.1 merge, critic | DataInvMerge-OpusHigh | opus | high | 02:27 | 02:36 | 9 min | 4,460,364 | done | 15 min |
| 2 | Task 2 code + 2 follow-ups | ConfigCoder-OpusXHigh | opus | xhigh | 02:14 | 05:12 | about 55 min of work | 28,122,365 | done; cut at 03:07 by the limit, resumed 05:11 | 45 min |
| 3 | T1.2 seal check | lead | opus | xhigh | 02:16 | 02:16 | 1 min | lead | done | 15 min |
| 4 | Move tool + test; plan; loader check | lead | opus | xhigh | 02:17 | 02:40 | 23 min | lead | done | 30 min |
| 4b | Task 4 fetch | TopstepRulesReader-OpusMed | opus | medium | 02:20 | 02:22 | 2 min | 1,086,590 | done (row added) | (in 12) |
| 5 | Move plan review | MovePlanReviewer-FableXHigh | fable | xhigh | 02:40 | 03:05 | 25 min | 7,782,928 | APPROVE AFTER FIXES | 25 min |
| 6 | Review fixes, move tool | lead | opus | xhigh | 03:05 | 03:07 | 2 min | lead | done (retest 05:10s) | 15 min |
| P | **usage-limit pause** | | | | 03:07 | 05:10 | 2 h 03 min | | excluded from work | |
| 7 | Step-3 edits; before-checks rerun; manifest | lead | opus | xhigh | 05:11 | 05:14 | 4 min | lead | done (first run 02:41-02:43 kept) | 10 min |
| 8 | T1.5 move | lead | opus | xhigh | 05:15:19 | 05:15:45 | 26 s | lead | done, 0 mismatches | 15 min |
| 9 | T1.6 after-checks, T1.7 finalize, DONE | lead | opus | xhigh | 05:15 | 05:18 | 3 min | lead | done, all identical | 15 min |
| 10 | Task 2 apply, v14, tests | lead | opus | xhigh | 05:19 | 05:35 | 16 min | lead | done (v14 rebuilt twice for review fixes) | 10 min |
| 11 | Task 2 review | ConfigReviewer-FableXHigh | fable | xhigh | 05:13 | 05:30 | 17 min | 3,433,527 | APPROVE AFTER FIXES, FINAL APPROVE | 25 min |
| 12 | Task 4 rules record | lead | opus | xhigh | 02:22 | 02:25 | 3 min | lead | done (moved early) | 30 min |
| 13 | Task 3 V45 | lead | opus | xhigh | 05:21 | 05:22 | 1 min (draft 02:26) | lead | done | 20 min |
| 14 | Commit Tasks 2+3 (95df9c6) | lead | opus | xhigh | 05:35 | 05:35 | 1 min | lead | done | 10 min |
| 15 | End checks; full suite | lead (background) | n/a | n/a | 05:35 | 06:04 | 29 min | | done | 35 min |
| 16 | Return, progress, STAGES, cost, final commit | lead | opus | xhigh | 05:36 | 06:07 | 31 min | lead | done | 45 min |
| | **Cumulative** | | | | 02:06 | 06:07 | **work 1 h 58 min** (wall 4 h 01 min incl. the pause) | **166,242,863** (lead 82,808,134; workers 83,434,729) | | initial estimate: end 07:40, about 5 h 34 min |

