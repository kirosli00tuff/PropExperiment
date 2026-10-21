# Stage E.26 T1.1 Sweep B: code references to the market-data locations

Worker: DataInvCode-OpusHigh (opus, high). Written 2026-10-21 02:2x PDT. Read-only static sweep.
No market-data file was opened, hashed or listed beyond names (`find`), no pytest was run,
and nothing in the repo or under /mnt/large-storage was written.

## Scope and method

- Python in .venv: **Python 3.12.13** (`.venv/bin/python -V`).
- Files searched: every `*.py`, `*.sh`, `*.toml`, `*.cfg` under the repo, excluding .venv, .git,
  .claude/worktrees, node_modules and the data directories themselves. That is 1,249 files
  (1,160 tracked, 89 untracked). By top-level directory: reports 478, tests 275, strategy 168,
  ml_route_v2 48, data 40, screening 29, base_rules 26, ml_route 25, forward 21, trigger_hold 19,
  pattern_search 17, h6_rod 14, sim 13, compute 13, funnel 12, multiday 11, c1_replication 10,
  prop_econ 9, microbook 9, rules 6, mdio 4, scripts 1, pyproject.toml.
- **Code inside the data directories (not read):** `find` shows 28 untracked `.py` files under
  `data/vendor/release_pages/{commodity_scripts (14), macro_scripts (7), named_scripts (7)}`
  (build.py, fetch.py, finalize.py, verify.py, crawl_*.py, parse_*.py, extra.py,
  recheck_d1f.py; 908 to 22,971 bytes). The brief forbids reading any file under data/vendor, so
  their contents were not grepped. See H13.
- Reference grep (data paths): `DATA_ROOT|VENDOR_ROOT|PROCESSED_ROOT|STEP2_ROOT|HIST_ROOT|SEALED*`,
  string literals `data/vendor`, `data/processed*`, `data/sealed`, `"vendor"`, `"processed*"`,
  `"sealed"`, `release_pages`, `index_history`, `GLBX.MDP3`, `"databento"`, plus joins of the form
  `/ "data" /`. Result: 522 lines in 116 files, all tracked (appendix). None of the 89 untracked
  code files refers to a data path.
- Hazard grep: resolve/realpath/relative_to/is_relative_to, is_symlink/lstat/readlink, os.walk,
  rglob/glob/`**`/recursive=True, copytree/rmtree/move/rename/replace, os.link/hardlink,
  chmod, fsync, flock/fcntl/O_EXCL, st_ino/st_dev/st_nlink/samefile/mtime, tempfile, git
  subprocess calls. 1,057 lines; each one on a data path was read in context.
- Python 3.12 behaviour was checked on a toy tree in the session scratchpad (not the repo):
  - `Path.rglob`/`Path.glob('**')` started ABOVE a symlinked directory list the link but do not
    descend into it.
  - Started AT the symlink, or at a path whose ancestor is the symlink, they descend normally.
  - `glob.glob(..., recursive=True)` DOES descend through the symlink.
  - `os.walk` (followlinks=False) does not descend into a link it finds below the top. It does
    follow the top argument itself.
  - Non-strict `Path.resolve()` of a missing file under a symlinked dir resolves the existing
    prefix through the link.
  - `shutil.rmtree(symlink)` raises OSError.

### What stays fixed

`data/config.py:19` sets `REPO_ROOT = Path(__file__).resolve().parents[1]`. data/config.py is
code and never moves, so REPO_ROOT stays the repo. Every other module-level `REPO_ROOT`/`ROOT`
of the same form (`prop_econ/*.py:36-74`, `funnel/exposure_gate_*.py:65-68`,
`strategy/research/_d1e_power.py:142`, the reports/ scripts' `REPO`) also points at code that
stays. The data roots are lexical joins under REPO_ROOT:
- `DATA_ROOT` (config.py:20)
- `VENDOR_ROOT = data/vendor/databento` (:21)
- `PROCESSED_ROOT` (:22)
- `STEP2_ROOT` (:129)
- `HIST_ROOT` (:205)
- `DATASET = "GLBX.MDP3"` (:229)

Other modules' constants:
- `data/holdout.py:127-136`: `DEFAULT_PATHS` and `HOLDOUT2_PATHS` (sealed roots under
  `DATA_ROOT/sealed`, research/confirmation parquets under PROCESSED_ROOT/MES,
  `vendor_root=VENDOR_ROOT`).
- `data/step2_seal.py:35`: `SEALED_BASE`.
- `data/hist_store.py:92` and `data/step2_store.py:96`: `SEALED_ROOT`.
- `data/build_bars.py:89-90`, `data/step2_store.py:94-95`, `data/pull_hist.py:136-137` and
  `data/build_mes_bars.py:70`: `CONDITION_PATH` / `ROLLS_DIR` / `CONDITION_DIR`.
- `data/research_bars.py:31,56`: `RESEARCH_SERIES_PATH` / `CONFIRMATION_SERIES_PATH`.
- `h6_rod/constants.py:26`: `NQ_STORE_REL`.
- `trigger_hold/events_validate.py:40-41`: cwd-relative `Path("data/processed")` and
  `Path("data/processed_step2")`.
- `sim/eta_probe.py:84`: `PARQUET`.
- `data/tick_crosscheck.py:40`.
- `screening/vehicles_run.py:76` and `prop_econ/returns.py:63`: inline joins.
- `screening/harness_freeze.py:37-38`: `DATA_SUBDIRS`.
- Path strings pinned in member modules:
  - `strategy/members/k1/_vxn.py:21` and `k3/_mehedge_signal.py:28-34`
    (data/vendor/index_history/..., tracked files)
  - `k7/_calendar.py:38-40` (data/vendor/databento/condition/...)

`sim/calibrate_slippage.py:38` and `data/tick_crosscheck.py:37` point at the sibling
MLCryptoEngine checkout (`REPO_ROOT.parent`), which the move does not touch.

Terms used below:
- **(a) top-level symlink**: one of data/processed, data/processed_step2, data/processed_hist,
  data/sealed or data/vendor becomes a symlink.
- **(b) sub-directory symlink**: for example data/vendor/databento or data/processed_step2/NQ
  becomes a symlink.
- **(c) per-file symlink**: each file is a symlink.

## Hazards found (BREAKS or CHANGES BEHAVIOUR)

### H1. ml_route research-store containment guard and its test (BREAKS a test under (a) for data/processed)

`ml_route/store.py:59-65`, in `assert_store_root`:

```python
root = Path(store_root).resolve()
forbidden = Path(forbidden_root).resolve()          # PROCESSED_ROOT
if _inside(root, forbidden) or _inside(forbidden, root):
    raise StoreRefused(... "is, contains or lies inside the research store root" ...)
```

Suppose data/processed becomes a symlink to /mnt/.../data/processed:
- `forbidden` resolves to /mnt/..., but an ancestor such as `data/` or the repo root still
  resolves inside the repo.
- So "contains the research store" is no longer detected.
- `tests/test_ml_route_store.py:53-56` (`test_research_store_root_is_refused_outright`) passes
  `PROCESSED_ROOT.parent` and expects `StoreRefused` matching "research".
- The call now gets past the containment check. It rglob's the real `data/` directory and raises
  the allowlist refusal instead: "REFUSED: __init__.py is not on the step 2 path allowlist" (the
  first sorted entry is data/__init__.py).
- `match="research"` fails, so **the test fails**.

In production the store root is still refused, but by the later allowlist rule, not by the
research-store rule.

- Not triggered by (b) or (c) inside data/processed: data/processed stays a real directory.
- Code fix option: also compare the unresolved `absolute()` spellings, as compute/datarules.py
  already does.

### H2. Holdout-leak test goes vacuous (CHANGES BEHAVIOUR, silent loss of coverage, any granularity at or below data/)

`tests/test_holdout.py:307-313` (`TestRealStore.test_no_plaintext_parquet_under_data_holds_a_holdout_date`)
runs `Path(ho.DATA_ROOT).rglob("*.parquet")` from `data/`:
- rglob does not descend into a symlinked data/processed, processed_step2 or processed_hist (or
  into any symlinked sub-directory).
- So the loop checks zero moved parquets and passes.
- Line 313 (`... / ORIGINAL_FULL_PARQUET_NAME).exists()`) follows the link and is unaffected.
- Fix: iterate each root itself (rglob from the root follows it) or use
  `os.walk(followlinks=True)`.
- No granularity avoids this except leaving the parquets in place.

### H3. Holdout-2 "no plaintext survives anywhere" scan narrows (CHANGES BEHAVIOUR)

`tests/test_d1f_holdout2.py:164-182` (`_files_holding`, called at :264-266 with roots including
`REPO_ROOT`):
- It uses `os.walk(root)` without followlinks and `lstat` with S_ISREG.
- After any symlink under the repo, the moved data is no longer scanned.
- The stub plaintext lives in tmp_path, so pass/fail is unchanged in normal runs. The scan just
  no longer covers the moved stores.
- Existing behaviour worth knowing: today this walk hashes every repo file whose size equals a
  stub chunk size, data included.

### H4. Legacy D.1f freeze/preflight file sets shrink (CHANGES BEHAVIOUR, low)

These walk `data` with rglob:
- `strategy/research/_d1f_preflight.py:124-129` (`python_files_under`, PINNED_PY_DIRS includes
  "data").
- `strategy/research/_d1f_freeze.py:70-74`.

Today they include the 28 untracked data/vendor/release_pages scripts.
`reports/stage_d1f_harness_freeze.json` lists none of them, so `_d1f_preflight.py:164-165`
reports 28 "not in the freeze manifest" problems. After (a) for data/vendor, or (b) for
data/vendor/release_pages, those 28 vanish from `on_disk`.

- `tests/test_d1f_confirmation.py:621-631` builds both sides from the same rglob and stays
  self-consistent (SAFE).
- `tests/test_cross_platform_static.py:152-154,405` `report()` scans fewer files. It is
  informational; the in-scope set is the import closure, which contains none of these.

### H5. New holdout seal records lose their repo-relative path (CHANGES BEHAVIOUR, future seals only)

`data/holdout.py:259-264` (`_relpath_in_repo`) does
`Path(path).resolve().relative_to(REPO_ROOT)` and returns None on ValueError.
- A raw chunk under a symlinked data/vendor or data/vendor/databento resolves to /mnt/... .
- Any seal written after the move therefore records `original_relpath: None` with only the
  absolute /home path. Writers: `holdout.py:478, 667` and `step2_seal.py:145` (for example a
  new step-2 product's holdout-2 chunks bought by data/pull_step2.py).

Existing records are unaffected. Verification and refusal both resolve both sides and stay
correct (S3):
- `holdout.py:267-286`: `_record_paths`, `is_sealed_raw`
- `holdout.py:353-356`: `unseal_raw_file`
- `holdout.py:402-410` and `:744-747`: `verify_seal` / `_verify_holdout2` `plaintext_absent`
- `step2_seal.py:96-99,183-189`

`tests/test_holdout.py:287` asserts holdout 1's records start with "data/vendor". It reads the
existing manifest and passes.

### H6. New purchase records store an absolute /mnt path (CHANGES BEHAVIOUR, future buys only)

`data/pull_hist.py:568-570` and `data/pull_step2.py:823-825` record:

```python
rel = target.resolve().relative_to(REPO_ROOT) if target.resolve().is_relative_to(REPO_ROOT) else target
```

- With data/vendor (or databento) symlinked, `resolve()` lands on /mnt.
- The recorded `"path"` becomes the unresolved absolute /home/... target, not
  "data/vendor/...". (The else-branch returns `target`, which is REPO_ROOT-based and absolute.)
- Readers accept absolute paths: `data/hist_store.py:131-132`, `data/step2_store.py:148-149`,
  and `data/build_bars.py:183` (pathlib `REPO_ROOT / abs` gives abs). It works on this machine
  but is no longer repo-relative.

### H7. Run outputs record resolved store paths (CHANGES BEHAVIOUR of output records; verifiers SAFE)

These write the resolved path when it is in the repo and an absolute path otherwise. After the
move a store is recorded as /mnt/... (or, for `_display`, the unresolved absolute /home/...
path) instead of "data/processed_*/...":

| Recorder | Writes the path into | Unresolved fallback? |
|---|---|---|
| `c1_replication/evaluate.py:113-117` | `:230` (store records) | No |
| `screening/stage_e14_c2.py:119-122` | `:476` ("store") | No |
| `screening/stage_e_start_dates.py:146-150` (`_display`) | `:280` (start-rule file sources) | Yes, the unresolved absolute path |
| `pattern_search/preflight.py:43-45` (`rel`), via `pattern_search/freeze_manifest.py:98-100` | store entries, only if a freeze is rebuilt with stores | No |
| `h6_rod/preflight.py:47-49` | | No |

Checking the EXISTING freezes and manifests is SAFE: each side is resolved before comparison.
- `pattern_search/preflight.py:104-110`: `listed[str(repo_path(e["path"]).resolve())]` against
  `str(Path(p).resolve())`.
- The same pattern in `h6_rod/preflight.py:143-148`, `trigger_hold/freeze_manifest.py:116-135`,
  `multiday/freeze_manifest.py:111-127`, `microbook/data.py:73-77` and
  `base_rules/guards.py:82-94`.

A rebuild of any such freeze after the move would write different path strings, so its sha256
would change.

### H8. Per-file or per-product symlinks are refused by store and compute guards (BREAKS under (c), and under (b) inside data/processed_step2)

- `ml_route/store.py:69-80`:
  - A symlinked product directory under the store root (for example data/processed_step2/NQ ->
    /mnt) is not skipped as a directory. It gives `rel` with one part, which is refused ("not on
    the step 2 path allowlist").
  - Per-file links are accepted only if the target name matches and lies outside PROCESSED_ROOT.
  - A whole data/processed_step2 symlink is SAFE: the root is resolved before the rglob.
- `compute/datarules.py:299-301` (`check_bar_file`) refuses any path whose last component is a
  symlink ("missing, a link or not a file"). It is called on each `sub.data_paths` entry by
  `compute/remote.py:174-175` (local submit) and by `compute/agent.py:137`. Per-file symlinks for
  any store sent to the remote machine therefore BREAK remote job submission.
- Directory-level symlinks are SAFE: `is_symlink()` tests only the last component.
- `compute/files.py:45-61,81` refuses links in export trees. Those trees are not data, but per-file
  links copied into them would be refused.

### H9. A committed symlink breaks the compute code export (BREAKS if ever committed)

`compute/gitbundle.py:107-109` and `:222-223` refuse every tree entry that is not a regular file
(mode 120000 included): "only regular files are exported" and "is not a regular file".

`.gitignore` ignores the data directories with a trailing slash, which does not match a
symlink. So:
- `git add -A` or `git add data` after the move would stage the symlinks.
- For data/vendor it would also stage deletion of the 11 tracked index_history files.
- The next remote export would be refused.

Avoid: never commit the links. Add slash-free ignore lines, or `.git/info/exclude` entries, for
each symlink path. No other code runs git on data paths:
- `_d1f_preflight.py:169-185` runs ls-files and status on manifest paths only.
- `harness_freeze.py:377` runs rev-parse HEAD.
- tests run git only in tmp repos.
- There are no `--porcelain` or untracked cleanliness checks in production code.

### H10. D.1e vendor listing misses files below a deeper symlink (CHANGES BEHAVIOUR under (b) below databento)

`strategy/research/_d1e_quotes.py:172-174` runs `VENDOR_ROOT.rglob("*")` and takes a lexical
`relative_to(REPO_ROOT)`.
- SAFE if the link is at data/vendor or data/vendor/databento: rglob starts below the link and
  descends.
- If GLBX.MDP3, condition, rolls or symbology are linked individually, their files are no longer
  listed.
- This is historical D.1e report code.

### H11. Fail-open when the target is absent (CHANGES BEHAVIOUR only if /mnt/large-storage is not mounted, so the link dangles)

`exists()`/`is_file()` return False through a dangling link:
- `holdout.py:410` and `:746-747`: `plaintext_absent` becomes True. The sealed blobs also
  read as missing, so `all_ok` is False if data/sealed is linked.
- `holdout.py:723-733` (`_confirmation_clean`) returns None, and `step2_seal.py:210` (and
  `holdout.py:768` for MES holdout 2) treat None as passing (`is not False`). If data/processed_step2 dangles while data/sealed stays local, the
  "store has no embargo rows" clause passes silently.
- 15 `skipif(... exists()/is_file())` markers in tests. 8 depend on data files: RESEARCH_SERIES_PATH
  in test_d1f_release_table, test_e2a_exposure_gate, test_leakage_canaries, test_null_generator
  and test_stage_e_mes_regression; test_e2a_bars:506; test_k1_members_tables:52 (VXN, tracked
  file under data/vendor); test_build_release_calendar:29/434 (REAL_PAGES). These turn into
  skips instead of failures.
- Mitigation for the after-checks: assert `mountpoint -q /mnt/large-storage` and `test -e` on
  every link first, and compare the pytest skip count with the pre-move run.

### H12. Naming constraint on the target path (SAFE for the planned root)

- `base_rules/store.py:71-79` lowercases every component of the RESOLVED path. It refuses
  "sealed" and "mes" components (and `is_relative_to` sealed/processed).
- `compute/datarules.py:150-158` refuses "sealed" and "ledger" components in the given and the
  resolved spelling.
- `base_rules/store.py:84` and `base_rules/hist_plan.py:80` check the resolved
  `parent.name == root` (and `parent.parent.name == plan`).

/mnt/large-storage/market_data/PropExperiment/<mirrored repo layout> passes. Any other target
must contain no component named sealed, mes or ledger, and must keep the per-product directory
names.

### H13. Unread scripts inside data/vendor/release_pages (UNVERIFIED)

The 28 untracked scripts listed above are the release sourcers' fetch, build and verify code
(harness_freeze.py:34-36 describes them as data). Under (a) for data/vendor, or (b) for
release_pages, they move with the data.

If any of them finds the repo through `Path(__file__).resolve().parents[N]`, a rerun after the
move would anchor in the /mnt mirror. It would write or read there instead of the repo, for
example reports/ outputs. Their contents were not read because of the brief's no-read rule for
data/vendor. Lead decides: read them (grep for `__file__`, resolve and REPO), or keep
release_pages in the repo.

Nothing in tracked code imports or runs them. The release calendar reads only the saved pages,
through a lexical guard (S9).

### H14. Start checks' `git status --short` output changes (CHANGES BEHAVIOUR of the check output)

`reports/stage_e26_briefs/checks.sh:11`:
- (a) for data/vendor shows `D` for the 11 tracked index_history files, plus `?? data/vendor`.
- A symlink at any trailing-slash-ignored path (data/processed, processed_step2, processed_hist,
  sealed) shows up as `??` untracked.

Earlier checks.sh files use the same command. Sweep C owns the data-reading after-checks.

## SAFE (checked, no change)

- **S1. Harness freeze scan.** `screening/harness_freeze.py:77-89,113-126,132-150,280-293,350-361`
  rglob over HARNESS_DIRS (which include data). rglob does not descend into a symlink found below
  `data/`. The link entry itself has `rel == "data/vendor"` (etc.), and `_in_data_subdir`
  (:73-74) excludes it. `is_file()` is False for a dir link, and a dir link never matches `*.py`.
  SAFE at every granularity inside DATA_SUBDIRS. A link at a NEW name under data/ (not in
  DATA_SUBDIRS) would be scanned like code.
- **S2. Realpath prefix guards.** `pattern_search/guard.py:50-107` (and its audit hook) and
  `h6_rod/guard.py:41-77` realpath both the root and the checked path. Targets stay disjoint and
  `_under` adds os.sep. `tests/test_pattern_search_guard.py:27-80` and
  `tests/test_h6_rod_guard.py:30-65` only build paths ("planted_absent" files are never written),
  and the tmp symlink test at :76-80 still resolves through to HIST_ROOT's real path.
- **S3. Resolve-equality pairs.** Both sides go through the same link:
  - `holdout.py:267-286, 353-356, 618-621, 702`
  - `step2_seal.py:96-99`
  - `build_mes_bars.py:303-313`
  - `pull_mes.py:246`
  - `hist_store.py:146-153`
  - `step2_store.py:167-174`
  - `base_rules/store.py:71-84` (mirrored names)
  - `base_rules/hist_plan.py:80`
  - `trigger_hold/run.py:86-87,118-123`
  - `multiday/run.py:100-107`
- **S4. compute/datarules.** `check_location` (:147-171) checks both spellings.
  `compute/remote.py:177` uploads from the resolved /mnt path, which is fine.
  `check_data_root` (:320-345) runs on the far side's own root.
- **S5. Write paths.** These all link or rename within ONE directory, so the moved tree is
  never crossed and EXDEV cannot occur:
  - `.partial` then `os.link` then `chmod 0444`: `adapter.py:110-127`,
    `pull_universe.py:585-604`, `build_mes_bars.py:458-471` (used by `build_bars.write_parquet`
    :760-767, step2_store and hist_store).
  - Sibling `.tmp` then `replace`: `pull_universe.py:576-579`, `build_bars_run.py:313-317`,
    `build_bars_reports.py:29-33`, `pull_hist.py:528-551`, `pull_step2.py:784-818`,
    `quote_universe.py:368-375`.
  - Durable manifest writes: `holdout._write_manifest` :578-593 (docs/).

  ext4 on /mnt supports hard links and chmod. Other checks:
  - Directory fsync through a link is fine: `holdout._fsync_dir` :570-575, used on `raw.parent`
    and the sealed dirs.
  - No `shutil.move`, `os.rename` or tempfile-to-data move into a data dir, no flock, and no
    st_ino/st_dev/st_nlink/samefile checks on data paths.
  - The only O_EXCL writers are run markers under reports/.
  - The probe's `tempfile.mkdtemp` in `build_bars_run.py:270` writes to /tmp, not data.
- **S6. Lexical relative_to on unresolved REPO_ROOT-based paths.** `build_bars.py:341`,
  `group_session.py:180`, `hist_calendar.py:449`, `build_bars_run.py:200,207`,
  `vehicles_run.py:72`, `_d1f_confirmation.py:207`, `_d1e_quotes.py:157-162`,
  `screening/trial_registry.py:194-196` (reports freeze only), and `funnel/exposure_gate_*.py`
  `rel` (reports files only).
- **S7.** `screening/runner.py:164-169` caches by resolved path, mtime and size within a
  process.
- **S8.** cwd-relative "data/processed" and "data/processed_step2":
  `trigger_hold/events_validate.py:40-59`,
  `reports/stage_e22_briefs/{confirm_run.sh:22-27, power_runs.sh:11}`, and the ml_route CLI
  docstrings.
- **S9.** The release calendar's `Pages` reads data/vendor/release_pages through
  `screening/build_release_calendar_checks.py:106-128`. `_page_path` is a lexical guard (no
  absolute paths, no ".."), so a link is fine.
- **S10. Tests touching the real data dirs.**
  - No test creates, renames, chmods or deletes anything in a real data directory. Every write
    goes to tmp_path or tmp "world" roots; checked by grep for write, mkdir, touch, unlink and
    chmod on the real roots, and for real roots passed as root/base/out arguments.
  - Tests that LIST real data: H2, H3, H4 (`test_holdout.py:309`,
    `test_d1f_holdout2.py:171,264`, `test_d1f_confirmation.py:628-631`).
  - Tests that READ real data through plain opens (SAFE while mounted):
    - TestRealStore in `test_holdout.py:301-313`
    - `test_d1f_holdout2.py:986`
    - `test_stage_e_mes_regression`
    - `test_e2a_bars.py:501-518`
    - `test_leakage_canaries.py:160`
    - `test_null_generator.py:427`
    - `test_k1_members_tables.py:35,52`
    - `test_e4_k3_members_m_signal.py:124-126`
    - `test_k7_members_events.py:69-70`
    - `test_build_release_calendar.py:434`
    - `test_ml_route_e2e.py:87-93` (`--research-root PROCESSED_ROOT`)
- **S11.** No `shutil.rmtree`, `copytree`, `os.walk` or `glob.glob(recursive=True)` call in
  production code targets a data path:
  - rmtree: `compute/remote.py:332-369` (job state) and `base_rules/probe.py:193` (scratch).
  - os.walk: `ml_route_v2/pipeline.py:171` (output size).
  - recursive glob: `reports/stage_e20_briefs/h6_freeze_manifest.py:13` (ml_route_v2 code).
- **pyproject.toml** has `testpaths = ["tests"]` and no package-data or include rules that touch
  data/. There is no setup.cfg, tox.ini, pytest.ini or tests/conftest.py data reference.

## Observation on the lead's draft reports/stage_e26_briefs/move_data.py (out of scope, for the lead)

This file appeared at 02:18 PDT, after the sweep's file list was taken. I read it only for the
hazards above.
- `os.rename(src, aside)` at :179 needs `aside_root` on the repo's filesystem, or it fails
  with EXDEV.
- Do not put `aside_root` under data/ unless the name is in harness_freeze.DATA_SUBDIRS. Nor
  under any other HARNESS_DIR or MEMBERS_DIR.
  - An aside copy of data/vendor carries the 28 release_pages `.py` files.
  - `unlisted_python_files` (harness_freeze.py:77-89) would then report them and fail
    `harness_freeze verify`.
  - `git status` would also show the aside tree.
- A same-filesystem location outside the repo avoids both.
- `cp -a` preserves hard links only within one invocation, so hard-link pairs that span two
  plan sources would split. Sweep A reports hard-link counts.

## Hazard table

| # | Hazard | file:line | Severity | Symlink granularity that avoids it |
|---|---|---|---|---|
| H1 | Resolved containment no longer sees `data/` as containing the research store; test expects "research" | ml_route/store.py:59-65; tests/test_ml_route_store.py:53-56 | BREAKS (test); CHANGES BEHAVIOUR (refusal reason) | Keep data/processed a real dir (link its sub-dirs or files), or fix the guard to compare absolute() too |
| H2 | DATA_ROOT.rglob skips linked stores; holdout-leak test goes vacuous | tests/test_holdout.py:307-313 | CHANGES BEHAVIOUR (silent) | None at or below data/; fix the test (rglob from each root, or os.walk followlinks=True) |
| H3 | os.walk(REPO_ROOT) plaintext scan skips moved data | tests/test_d1f_holdout2.py:164-182,264 | CHANGES BEHAVIOUR (coverage) | None; add followlinks or the targets to the roots |
| H4 | D.1f on-disk *.py set loses the 28 release_pages scripts | strategy/research/_d1f_preflight.py:124-129,164-165; _d1f_freeze.py:70-74; tests/test_cross_platform_static.py:152-154,405 | CHANGES BEHAVIOUR (low) | Leave data/vendor/release_pages in place |
| H5 | New seal records get original_relpath None | data/holdout.py:259-264 (callers :478, :667; step2_seal.py:145) | CHANGES BEHAVIOUR (future seals) | Leave data/vendor/databento/GLBX.MDP3 in place, or fix (relpath from the unresolved path) |
| H6 | New purchase records store the absolute path | data/pull_hist.py:568-570; data/pull_step2.py:823-825 | CHANGES BEHAVIOUR (future buys) | Same as H5 |
| H7 | Outputs and rebuilt freezes record /mnt or absolute store paths | c1_replication/evaluate.py:113-117,230; screening/stage_e14_c2.py:119-122,476; screening/stage_e_start_dates.py:146-150,280; pattern_search/preflight.py:43-45 + freeze_manifest.py:98-100; h6_rod/preflight.py:47-49 | CHANGES BEHAVIOUR (new outputs; verifying existing freezes is SAFE) | None at directory level; per-file links resolve to /mnt too |
| H8 | Linked product dir or linked store file refused | ml_route/store.py:69-80; compute/datarules.py:299-301 (via compute/remote.py:174-175, compute/agent.py:137) | BREAKS under (c), and under (b) inside data/processed_step2 | Whole top-level dir link (a) |
| H9 | Committed symlink (mode 120000) refused by code export; trailing-slash ignore lets `git add` stage links and delete tracked index_history | compute/gitbundle.py:107-109,222-223; .gitignore | BREAKS (only if committed) | Any, as long as the links are never committed; add slash-free ignores or info/exclude |
| H10 | VENDOR_ROOT.rglob misses files under deeper links | strategy/research/_d1e_quotes.py:172-174 | CHANGES BEHAVIOUR (historic) | Link at data/vendor or data/vendor/databento, not below |
| H11 | Dangling link (mount absent) makes exists() False: plaintext_absent True, _confirmation_clean None passes, 8 data skipifs skip | data/holdout.py:410,723-733,746-747,768; data/step2_seal.py:210; 8 test skipif markers | CHANGES BEHAVIOUR (fail-open on mount loss) | None; check the mount and links before every check |
| H12 | Resolved-path component checks (sealed, mes, ledger, parent names) | base_rules/store.py:71-84; base_rules/hist_plan.py:80; compute/datarules.py:150-158 | SAFE for /mnt/large-storage/market_data/PropExperiment (mirrored) | Any; the target path must avoid those component names and keep the mirrored layout |
| H13 | 28 unread scripts under data/vendor/release_pages may anchor on `__file__.resolve()` | data/vendor/release_pages/*_scripts/*.py | UNVERIFIED | Leave release_pages in place, or read them first |
| H14 | `git status --short` start-check output gains D and ?? lines | reports/stage_e26_briefs/checks.sh:11 | CHANGES BEHAVIOUR (check output) | Sub-directory links that leave tracked files' dirs real, plus ignore entries for the links |
| S1 | harness_freeze rglob over data | screening/harness_freeze.py:73-150,280-361 | SAFE | Any link inside DATA_SUBDIRS; not a new name under data/ |
| S2 | realpath prefix guards and audit hooks | pattern_search/guard.py:50-107; h6_rod/guard.py:41-77 | SAFE | Any (targets disjoint) |
| S3 | resolve()-equality checks (holdout, seal, builders, pullers, freeze verifiers) | see S3 | SAFE | Any |
| S5 | .partial/.tmp then os.link/replace in the same dir; fsync dir; chmod 0444 | adapter.py:110-127; pull_universe.py:576-604; build_mes_bars.py:458-471; holdout.py:570-593 | SAFE (no EXDEV) | Any (target fs is ext4) |
| S6-S11 | Lexical relative_to, cwd-relative paths, Pages guard, test reads, no rmtree/copytree on data | see sections | SAFE | Any |

## Appendix: every file with a data-path reference (522 lines, 116 files, all tracked)

Line numbers are matches of the reference grep (comments and docstrings included). A blank
hazard column means the code joins or opens the path plainly, which follows symlinks: SAFE.

| file | git | refs | lines | hazard IDs (blank: path construction or plain open/read, follows symlinks, SAFE) |
|---|---|---|---|---|
| base_rules/store.py | tracked | 4 | 7,39,75,77 | S3, H12 |
| c1_replication/evaluate.py | tracked | 5 | 141,309,332,479,484 | H7 |
| compute/datarules.py | tracked | 10 | 5,37,38,56,84,88,153,155,190,191 | S4, H8, H12 |
| compute/gitbundle.py | tracked | 4 | 27,30,112,115 | H9 |
| data/adapter.py | tracked | 4 | 1,36,65,89 | S5 (os.link same dir) |
| data/build_bars.py | tracked | 5 | 59,89,90,201,213 |  |
| data/build_bars_run.py | tracked | 4 | 56,93,166,308 |  |
| data/build_mes_bars.py | tracked | 9 | 7,43,70,144,145,219,298,303,493 | S5 (os.link same dir) |
| data/config.py | tracked | 7 | 20,21,22,35,129,205,229 |  |
| data/hist_bars.py | tracked | 3 | 7,27,91 |  |
| data/hist_store.py | tracked | 11 | 9,11,39,64,92,106,137,159,238,383,427 | S3 (resolve both sides) |
| data/holdout.py | tracked | 17 | 8,9,10,72,87,119,127,131,135,445,519,641,672,755,766,807,808 | H5, H11 (resolve both sides: SAFE for reads) |
| data/pull_hist.py | tracked | 9 | 8,14,44,45,97,136,137,651,801 | H6 |
| data/pull_mes.py | tracked | 8 | 53,115,228,238,266,275,284,347 | S3 (resolve both sides) |
| data/pull_step2.py | tracked | 17 | 17,124,169,187,224,226,356,372,417,462,486,810,891,903,907,940,1121 | H6 |
| data/pull_universe.py | tracked | 7 | 1,37,80,366,424,671,756 | S5 (os.link same dir) |
| data/quote_universe.py | tracked | 2 | 1,666 |  |
| data/research_bars.py | tracked | 3 | 27,31,56 |  |
| data/step2_seal.py | tracked | 9 | 13,16,32,35,46,50,150,197,208 | H5 (via holdout), resolve both sides SAFE |
| data/step2_store.py | tracked | 17 | 6,12,14,64,91,92,94,95,96,103,113,154,158,180,227,242,485 | S3 (resolve both sides) |
| data/tick_crosscheck.py | tracked | 2 | 37,40 |  |
| h6_rod/constants.py | tracked | 1 | 26 |  |
| h6_rod/guard.py | tracked | 8 | 5,10,11,58,66,69,71,72 | S2 (SAFE) |
| h6_rod/run.py | tracked | 6 | 70,75,77,92,97,98 |  |
| microbook/data.py | tracked | 1 | 103 |  |
| microbook/run.py | tracked | 1 | 9 |  |
| ml_route/__init__.py | tracked | 1 | 12 |  |
| ml_route/store.py | tracked | 8 | 5,6,8,11,14,38,59,143 | H1, H8 |
| ml_route/test.py | tracked | 1 | 6 |  |
| ml_route/train.py | tracked | 1 | 4 |  |
| ml_route_v2/phase1/world.py | tracked | 7 | 39,211,224,525,528,536,539 |  |
| pattern_search/guard.py | tracked | 16 | 8,9,10,11,21,45,46,47,57,60,74,82,83,86,88,89 | S2 (SAFE) |
| pattern_search/world.py | tracked | 2 | 188,194 |  |
| prop_econ/returns.py | tracked | 1 | 63 |  |
| reports/stage_e12_briefs/gate0verifier/mes_mbt_check.py | tracked | 2 | 22,48 |  |
| reports/stage_e12_briefs/gate0verifier/spot_check.py | tracked | 1 | 66 |  |
| reports/stage_e16_briefs/freeze_manifest.py | tracked | 3 | 7,8,97 |  |
| reports/stage_e18_briefs/freeze_manifest.py | tracked | 2 | 97,110 |  |
| reports/stage_e18_diff_review/hist_store_v10.py | tracked | 10 | 9,11,54,82,96,127,149,228,373,417 |  |
| reports/stage_e18_diff_review/pull_hist_v10.py | tracked | 9 | 8,14,44,45,75,114,115,523,654 |  |
| reports/stage_e19_verify/er_returns.py | tracked | 1 | 41 |  |
| reports/stage_e20_briefs/h6_freeze_manifest.py | tracked | 1 | 22 |  |
| reports/stage_e20_briefs/h6_verify_recompute.py | tracked | 1 | 31 |  |
| reports/stage_e22_briefs/confirm_run.sh | tracked | 3 | 22,26,27 |  |
| reports/stage_e22_briefs/power_runs.sh | tracked | 1 | 11 |  |
| reports/stage_e23_briefs/inventory/tmp_K1/K1_build.py | tracked | 5 | 55,62,65,74,271 |  |
| reports/stage_e23_briefs/inventory/tmp_K2/K2_build.py | tracked | 2 | 59,60 |  |
| reports/stage_e23_briefs/inventory/tmp_K3/K3_build.py | tracked | 6 | 55,56,61,96,375,383 |  |
| reports/stage_e23_briefs/inventory/tmp_K5/K5_build.py | tracked | 1 | 326 |  |
| reports/stage_e23_briefs/inventory/tmp_K7/K7_build.py | tracked | 1 | 49 |  |
| reports/stage_e23_briefs/inventory/tmp_K8/K8_build.py | tracked | 10 | 95,96,100,101,154,158,159,208,213,214 |  |
| reports/stage_e3_briefs/audit/csv_availability.py | tracked | 1 | 7 |  |
| reports/stage_e3_briefs/audit/recompute_releases.py | tracked | 1 | 46 |  |
| reports/stage_e3_briefs/audit/replay_predrift.py | tracked | 1 | 51 |  |
| reports/stage_e3_briefs/audit/replay_two.py | tracked | 1 | 27 |  |
| reports/stage_e4_briefs/audit_k3/recompute_tables.py | tracked | 4 | 35,36,37,38 |  |
| reports/stage_e4_briefs/audit_k5/recompute_tables.py | tracked | 3 | 5,52,57 |  |
| reports/stage_e4_briefs/gen_k3_mehedge.py | tracked | 4 | 52,53,54,55 |  |
| reports/stage_e5_briefs/start_checks.sh | tracked | 1 | 51 |  |
| reports/stage_e6_briefs/audit_k7/recompute_tables.py | tracked | 2 | 28,29 |  |
| reports/stage_e6_briefs/gen_k7_calendar.py | tracked | 4 | 11,65,66,322 |  |
| reports/stage_e7_briefs/audit_k1/auditor_recompute_tables.py | tracked | 2 | 34,140 |  |
| reports/stage_e7_briefs/gen_k1_tables.py | tracked | 3 | 15,53,256 |  |
| screening/harness_freeze.py | tracked | 2 | 37,38 | S1 (SAFE) |
| screening/stage_e14_c2.py | tracked | 2 | 59,431 | H7 |
| screening/stage_e_start_dates.py | tracked | 7 | 75,420,421,474,475,727,728 | H7 |
| screening/vehicles_run.py | tracked | 1 | 76 |  |
| sim/calibrate_slippage.py | tracked | 2 | 6,38 |  |
| sim/cost_inputs.py | tracked | 1 | 13 |  |
| sim/eta_probe.py | tracked | 1 | 84 |  |
| strategy/members/k1/_vxn.py | tracked | 2 | 5,21 |  |
| strategy/members/k3/_mehedge_signal.py | tracked | 4 | 28,30,32,34 |  |
| strategy/members/k7/_calendar.py | tracked | 3 | 16,38,40 |  |
| strategy/research/_d1e_quotes.py | tracked | 10 | 34,68,84,100,172,174,422,428,661,947 | H10 |
| strategy/research/_d1f_confirmation.py | tracked | 3 | 68,129,199 |  |
| strategy/research/_d1f_preflight.py | tracked | 1 | 290 |  |
| strategy/stage_e/_template.py | tracked | 1 | 33 |  |
| tests/_compute_fixtures.py | tracked | 2 | 29,100 |  |
| tests/_e14_fixtures.py | tracked | 2 | 180,189 |  |
| tests/test_base_rules_store.py | tracked | 3 | 150,162,165 |  |
| tests/test_build_release_calendar.py | tracked | 2 | 28,29 |  |
| tests/test_compute_datarules.py | tracked | 7 | 16,46,66,70,324,327,342 |  |
| tests/test_compute_remote_e2e.py | tracked | 5 | 85,100,155,217,257 |  |
| tests/test_compute_units.py | tracked | 2 | 321,507 |  |
| tests/test_d1f_calendar_build.py | tracked | 3 | 300,305,427 |  |
| tests/test_d1f_holdout2.py | tracked | 31 | 40,43,64,66,103,119,127,129,132,134,136,199,238,249,301,327,423,463,515,563,565,587,661,686,759,903,907,910,914,970,976 | H3 |
| tests/test_d1f_preflight.py | tracked | 1 | 39 |  |
| tests/test_d1f_runner_hardening.py | tracked | 1 | 121 |  |
| tests/test_e14_config_v10.py | tracked | 3 | 22,54,60 |  |
| tests/test_e14_hist_store.py | tracked | 4 | 92,94,225,228 |  |
| tests/test_e14_pull_hist.py | tracked | 2 | 163,189 |  |
| tests/test_e17_v12_pull_hist.py | tracked | 4 | 209,442,444,453 |  |
| tests/test_e2a_bars.py | tracked | 1 | 501 |  |
| tests/test_e2b_pull_step2.py | tracked | 8 | 55,132,241,281,437,540,622,670 |  |
| tests/test_e2b_pull_step2_e12.py | tracked | 4 | 158,349,434,485 |  |
| tests/test_e2b_step2_store.py | tracked | 7 | 26,60,73,111,113,115,229 |  |
| tests/test_e2b_step2_store_v9.py | tracked | 2 | 71,82 |  |
| tests/test_e2b_trade_date_guard.py | tracked | 1 | 75 |  |
| tests/test_h6_rod_guard.py | tracked | 9 | 30,31,36,37,38,51,52,65,72 |  |
| tests/test_harness_freeze.py | tracked | 2 | 98,99 |  |
| tests/test_holdout.py | tracked | 11 | 49,52,56,67,125,140,265,276,287,308,312 | H2 |
| tests/test_k1_members_tables.py | tracked | 1 | 35 |  |
| tests/test_k7_members_events.py | tracked | 2 | 69,70 |  |
| tests/test_mdio_bounded.py | tracked | 2 | 323,324 |  |
| tests/test_ml_route_e2e.py | tracked | 2 | 87,93 |  |
| tests/test_ml_route_store.py | tracked | 5 | 13,42,54,108,116 | H1 |
| tests/test_pattern_search_guard.py | tracked | 22 | 28,30,33,34,35,40,41,42,45,47,59,60,78,79,104,105,108,111,194,203,204,212 |  |
| tests/test_pattern_search_run.py | tracked | 1 | 117 |  |
| tests/test_pattern_search_world_check.py | tracked | 2 | 166,170 |  |
| tests/test_pull_universe.py | tracked | 15 | 65,140,181,197,216,367,451,489,505,530,547,574,599,601,606 |  |
| tests/test_quote_universe.py | tracked | 3 | 28,293,397 |  |
| tests/test_spend_gate.py | tracked | 4 | 20,125,138,155 |  |
| tests/test_spend_gate_accounts.py | tracked | 1 | 27 |  |
| tests/test_stage_e_loader.py | tracked | 2 | 199,205 |  |
| tests/test_stage_e_mes_regression.py | tracked | 2 | 18,40 |  |
| trigger_hold/events_validate.py | tracked | 4 | 40,41,47,58 |  |
