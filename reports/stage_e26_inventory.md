# Stage E.26 T1.1: market-data inventory before the move (merge)

Worker: DataInvMerge-OpusHigh (opus, high). Written 2026-10-21 02:27 to 02:36 PDT. Brief:
reports/stage_e26_briefs/brief_inventory.md, section "Merge". Inputs: the three sweeps,
reports/stage_e26_briefs/inv_disk.md (A), inv_code.md (B) and inv_manifests.md (C). Machine-readable
source table: reports/stage_e26_inventory.json.

Method and boundaries: the merge read the sweep files and code (sed/grep line ranges). It re-checked
facts with metadata-only commands (du -sb, find counts and names, git ls-files/check-ignore, stat,
lsof, df, mountpoint). No market-data file was opened, read or hashed. Section 5 notes one
interpretation call: a names-only grep (`grep -l`, `grep -c`) over the 28 `.py` scripts under
data/vendor/release_pages. Nothing was moved or written outside the two output files and one
scratchpad list (`new_code.txt`).

## 1. Source table

Sizes from `du -sb` and `find -type f`, re-run by the merge at 02:31 PDT. They match Sweep A to the
byte. Git: tracked = `git ls-files`; ignored = the trailing-slash patterns .gitignore:17-20 and 23.
No symlinks and no hard links exist in any unit (A, re-checked: `find -type l` = 0 in each unit).

| Source | bytes | files | git | Recommended granularity | Main references (full lists in the JSON) |
|---|---:|---:|---|---|---|
| data/vendor/databento (GLBX.MDP3 8,605,473,695 B / 4,266; condition 761,530 / 4; rolls 2,147,559 / 190; symbology 16,499 / 1) | 8,608,399,283 | 4,461 | ignored | **sub-directory link at data/vendor/databento** | holdout manifests (69 sealed-raw originals, abs + rel), purchase/bars reports, stage_e1_purchase, stage_e2a_bars; VENDOR_ROOT in data/config.py:21 and the pullers/builders; the realpath guards pattern_search/guard.py:89, h6_rod/guard.py:71-72; k7/_calendar.py:38-40; checks.sh:13-22 |
| data/vendor/release_pages | 153,575,775 | 4,263 | ignored | **lead decides**; default keep in place. If moved: a sub-directory link at data/vendor/release_pages, copied with mtimes kept | stage_e2b_release_sources_*.json, stage_e2b_release_calendar.json (screening.build_release_calendar --check), 7 in-dir manifests, 28 in-dir scripts, tests/test_build_release_calendar.py, the D.1f preflight rglob |
| data/vendor/index_history | 1,101,859 | 29 | **mixed** (11 tracked, 18 ignored) | **stays real, nothing moves** | K1 _vxn.py:21 and K3 _mehedge_signal.py:28-34 (sha-pinned tracked CSVs), their tests (skipif), stage_e4c_release_check.json, stage_e7 sha256 snapshots |
| data/processed (46 product dirs; 48 parquet + 1 `.outright-pattern-bug`) | 303,035,283 | 49 | ignored | **whole-directory link** (= PROCESSED_ROOT); needs the H-01 decision | HOLDOUT_MANIFEST research path, HOLDOUT2 confirmation, stage_e2a_bars, stage_e12_phase1_bars (abs); ml_route/store.py:59-65, base_rules/store.py:77, pattern_search/h6_rod realpath guards; data.holdout status |
| data/processed_step2 (31 products) | 592,497,579 | 31 | ignored | **whole-directory link** (= STEP2_ROOT) | holdout2 product manifests, stage_e17_run_manifest, E.20 search and H6 freezes, step2 bars reports; ml_route/store.py, compute/datarules.py, base_rules/store.py, guards; checks.sh:86-106 |
| data/processed_hist (ext2010 6 roots 224,596,181 B; ext2010h 11 roots 239,461,358 B) | 464,057,539 | 17 | ignored | **whole-directory link** (= HIST_ROOT) | stage_e17_run_manifest, stage_e18_freeze + e17_c1_store_hashes, hist bars reports, C1 results; base_rules/hist_plan.py:80, guards; checks.sh:79-81, 86-102 |
| data/sealed (6 stores; 69 `.dbn.zst.sealed` + 1 holdout_bars.sealed, all mode 664) | 28,306,346 | 70 | ignored | **whole-directory link** (= SEALED_BASE) | the 6 holdout manifests (sha256 of every blob), data/holdout.py, step2_seal.py, hist/step2_store sealed_roots, base_rules/store.py:75, compute/datarules.py:150-158, guards; checks.sh:13-22 |
| reports/stage_e22_microbook/cache | 725,494 | 28 | untracked, not ignored | stays (outside scope) | microbook/data.py (sha only) |
| reports/stage_e14_briefs/gex/DIX.csv | 222,563 | 1 | ignored | stays (frozen at this path) | stage_e20_h6_freeze.json |

Totals:
- The recommended move (databento + processed + processed_step2 + processed_hist + sealed) is
  **9,996,296,030 B in 4,628 files**.
- Moving release_pages as well gives 10,149,871,805 B in 8,891 files.
- Sweep A's grand total of 10,150,973,664 B adds index_history, which stays.

Never a symlink:
- **data/**: it holds the code; REPO_ROOT is `Path(data/config.py).resolve().parents[1]`.
- **data/vendor**: it holds the 11 tracked index_history files. A link there shows them as ` D` and
  makes `git add` fail with "beyond a symbolic link" (A, scratch git demo).
- **data/calendars**: tracked code and JSON.

Not market data and not moved:
- reports/stage_e19_runs/*.npz (ignored), the E.2a npy (tracked) and other run outputs (A section 2).
- ~/.cache/propexp_e14_c1 (111,453,378 B, outside the repo). The E.18 freeze verify checks it.
- balt_full.json and ni_full.json are OpenAlex records, untracked.

Target filesystem (A, re-checked 02:30 PDT):
- /mnt/large-storage is a mountpoint: ext4, st_dev 66310 against the repo's 64513, about 768 GiB
  free, mode 700, fstab `nofail`.
- **market_data does not exist yet.**
- The aside root planned in move_data.py (/home/kiros-li/e26_aside) is on st_dev 64513, the repo's
  filesystem, so the planned `os.rename` cannot hit EXDEV. It does not exist yet.

## 2. Hazard list (B and C deduplicated, plus one found in the merge)

Severity: BREAKS / CHANGES BEHAVIOUR / SAFE. The source IDs are given (A-, B-H, C-H) so the
evidence can be traced.

| ID | Hazard | Where | Severity | Granularity or step that avoids it | Sources |
|---|---|---|---|---|---|
| **H-00** | **Realpath-prefix guards fail open below their root (new in the merge).** The guards compute `realpath(ROOT)` once and refuse paths under it. If the link sits *below* the root (per product, per era, per store, or below databento), the root still resolves into the repo while the files resolve to /mnt, so they fall outside every prefix and are **allowed**. Affected: (1) the pattern_search and h6_rod forbidden prefixes (PROCESSED_ROOT, STEP2_ROOT, HIST_ROOT, VENDOR_ROOT, SEALED_BASE); for example per-store links of MCL/MGC/MHG/NG_holdout_v2 are covered only by SEALED_BASE. (2) base_rules refuse_path's research rule (backstopped only by the `"research" in name` test). (3) The hist/step2_store `sealed_roots` input check (backstopped by is_sealed_raw and parent-name checks). | pattern_search/guard.py:80-107; h6_rod/guard.py:64-90; base_rules/store.py:75-77; data/hist_store.py:150-152; data/step2_store.py:171-173; ml_route/store.py:59-65 | **BREAKS** (silent guard fail-open) at sub-directory granularity; SAFE when each link sits exactly at its root | Link exactly at PROCESSED_ROOT, STEP2_ROOT, HIST_ROOT, SEALED_BASE (data/sealed) and VENDOR_ROOT (data/vendor/databento). Never below them | merge (B S2 called these SAFE, assuming root-level links) |
| H-01 | `ml_route.store.assert_store_root(PROCESSED_ROOT.parent)` no longer detects that data/ contains the research root once data/processed resolves to /mnt. It is refused later by the allowlist rule ("__init__.py is not on the step 2 path allowlist"), so `test_research_store_root_is_refused_outright` (`match="research"`) **fails**. The production refusal still happens, with a different reason | ml_route/store.py:59-65; tests/test_ml_route_store.py:53-56 | BREAKS (1 test); CHANGES BEHAVIOUR (refusal reason) | None that is also H-00-safe. **Lead decides:** a code fix (also compare unresolved `absolute()` spellings, as compute/datarules.py:164 does; ml_route is harness code) or a recorded known failure | B-H1 (merge re-read the code and confirms it) |
| H-02 | Per-product or per-file links are refused. assert_store_root treats a linked product dir as a one-part entry; compute/datarules.check_bar_file refuses a final-component symlink | ml_route/store.py:69-80; compute/datarules.py:299-301 (via compute/remote.py:174-175, compute/agent.py:137) | BREAKS under per-file links, and per-product links in processed_step2 | Whole-directory links | B-H8, C-H6 |
| H-03 | Mount loss fails open (fstab `nofail`). A dangling link makes `exists()` False: holdout `plaintext_absent` / `unsealed_plaintext_present` pass vacuously; `_confirmation_clean` returns None and `all_ok` accepts None (`is not False`, holdout.py:768, step2_seal.py:210); 8 data-dependent test `skipif`s turn checks into skips (K1 VXN, release calendar, research-series tests) | data/holdout.py:402-410,723-770; data/step2_seal.py:203-212; tests skipif markers | CHANGES BEHAVIOUR (silent pass or skip) | None. Before every check: `mountpoint -q /mnt/large-storage` and `test -e` on every link. Compare field values and pytest skip counts, not only all_ok/pass | B-H11, C-H1, C-H2, C-H3 |
| H-04 | Scans that start above a link stop covering the moved data: `DATA_ROOT.rglob("*.parquet")` in the holdout-leak test (reads 0 moved parquets and passes); `os.walk(REPO_ROOT)` in the holdout-2 plaintext scan; the D.1f preflight/freeze `*.py` sets (lose the 28 release_pages scripts, only if release_pages moves); `VENDOR_ROOT.rglob` in _d1e_quotes (only if linked below databento) | tests/test_holdout.py:307-313; tests/test_d1f_holdout2.py:164-182,264; strategy/research/_d1f_preflight.py:124-129,164-165, _d1f_freeze.py:70-74; strategy/research/_d1e_quotes.py:172-174 | CHANGES BEHAVIOUR (silent coverage loss) | No granularity fixes the first two. Lead decides on a test fix (rglob from each root, or `os.walk(followlinks=True)`). The D.1f item is avoided by keeping release_pages; _d1e by linking at databento | B-H2, B-H3, B-H4, B-H10 |
| H-05 | New records written after the move carry /mnt or absolute paths. `_relpath_in_repo` gives `original_relpath: None` for future seals; pull_hist/pull_step2 record absolute targets; c1_replication, stage_e14_c2, stage_e_start_dates._display, pattern_search/h6_rod preflight `rel` write resolved paths. A rebuilt freeze would change its sha256. Existing records and every existing verifier are unaffected (both sides resolved, or sha only) | data/holdout.py:259-264 (callers :478,:667; step2_seal.py:145); data/pull_hist.py:568-570; data/pull_step2.py:823-825; c1_replication/evaluate.py:113-117; screening/stage_e14_c2.py:119-122; screening/stage_e_start_dates.py:146-150; pattern_search/preflight.py:43-45; h6_rod/preflight.py:47-49 | CHANGES BEHAVIOUR (future seals, buys, freezes only) | None at directory level. No seal or freeze rebuild is planned; note it for future stages | B-H5, B-H6, B-H7, C-H4 |
| H-06 | Git sees links. A link at a trailing-slash-ignored path (data/processed, processed_step2, processed_hist, sealed) shows `?? data/<x>`. `git add -A` would stage mode-120000 entries, which compute/gitbundle.py refuses on export. checks.sh:11 output changes. Links inside the real, ignored data/vendor/ (databento, release_pages) stay clean | .gitignore:17-23; compute/gitbundle.py:107-109,222-223; checks.sh:11 | BREAKS only if committed; CHANGES BEHAVIOUR of `git status` | Never commit the links. **Lead decides:** slash-free entries (`/data/processed`, `/data/processed_step2`, `/data/processed_hist`, `/data/sealed`) in .gitignore (tracked, in no freeze; checked by grep) or in .git/info/exclude (local, currently empty of rules) | A-3, B-H9, B-H14 |
| H-07 | Target naming. Resolved-path component checks refuse `sealed`, `mes` and `ledger` components and check `parent.name == root`; ml_route refuses nested store roots | base_rules/store.py:71-84; base_rules/hist_plan.py:80; compute/datarules.py:150-158; ml_route/store.py:59-64 | SAFE for /mnt/large-storage/market_data/PropExperiment/<mirrored layout> | Keep the mirror. No `sealed`/`MES`/`ledger` component above the stores; sibling roots | B-H12, C-H7 |
| H-08 | mtime preservation. named_scripts/build.py takes "fetched" from `st_mtime`; screening/runner caches by (resolved path, mtime_ns, size) | data/vendor/release_pages/named_scripts/build.py:231; screening/runner.py:164-169 | CHANGES BEHAVIOUR (rebuild only); cache SAFE | `cp -a` / `rsync -a` (modes 444/664 kept as well) | C-H9, C-H10, B-S7 |
| H-09 | Scripts inside release_pages travel with it. Names-only grep (section 5): **all 28 hard-code `/home/kiros-li/Documents/GitHub/PropExperiment`**, none calls `resolve()` or `realpath`, and 2 (macro_scripts/build.py, finalize.py) use `__file__`, which is lexical without resolve. The verify.py scripts **rewrite** reports/stage_e2b_release_sources_*.json, so they are never after-checks | data/vendor/release_pages/*_scripts/*.py | SAFE (low residual: `__file__` use not read line by line) | Never run them as checks | B-H13 (was UNVERIFIED), C-3 |
| H-10 | CWD-relative verifiers: the E.20 store sha256 block, h6_freeze_manifest.py, base_rules StoreRef, trigger_hold EB.RUN_MANIFEST_PATH, trigger_hold/events_validate.py | as listed | SAFE when run from the repo root | Run every check from the repo root (checks.sh does cd) | C-H5, B-S8 |
| H-11 | Same-directory write patterns (`.partial`/`.tmp`, then `os.link`/`replace`, chmod 0444, dir fsync) stay inside one directory, so there is no EXDEV. ext4 on /mnt supports hard links and chmod | data/adapter.py:110-127; data/pull_universe.py:576-604; data/build_mes_bars.py:458-471; data/holdout.py:570-593 | SAFE | Any | B-S5, C-H8 |
| H-12 | harness_freeze rglob over data/: rglob does not descend into a link and the link entry matches a DATA_SUBDIRS prefix, so the output is unchanged. A link at a NEW name under data/ would be scanned as code | screening/harness_freeze.py:37-38,73-150 | SAFE at every recommended link | Links only at existing DATA_SUBDIRS paths; move_data.py's aside root is outside the repo | B-S1, C-1 |
| H-13 | Resolve-equality pairs: holdout `_record_paths`, `is_sealed_raw`, `unseal_raw_file`, step2_seal, the builders' input checks, and freeze verifiers comparing resolved paths on both sides | B-S3 list; pattern_search/preflight.py:104-110 | SAFE | Any | B-S3, C-V1..V5 |
| H-14 | Swap window and concurrent users. Between `os.rename` to the aside and `os.symlink`, the path is missing. At 02:30 PDT a `pytest -q` (pid 351234, from this session's scratchpad) was running, and so was the E.28 session (A: pid 129448/129449). Open data handles: 0 at 02:16, 02:18 (A) and 02:30 (merge) | system | CHANGES BEHAVIOUR (a reader in the window sees missing data and fails, or skips under H-03) | Move only with no pytest or `uv run` job and 0 handles; repeat the lsof check right before each swap | A-4, merge |

## 3. Recommended granularity, with reasons

The rule that satisfies H-00, H-02 and H-06 together: **one link exactly at each guarded root, and
never above a tracked file.**

1. **data/vendor/databento → one sub-directory link.**
   - It is VENDOR_ROOT, so the realpath guards stay consistent (H-00), and _d1e_quotes still
     descends (H-04).
   - Git stays clean because the real parent data/vendor/ is ignored (A demo).
   - data/vendor itself cannot be a link: index_history is tracked.
   - Not below databento: per-child links would put GLBX.MDP3 outside VENDOR_ROOT's prefix (H-00).
2. **data/processed, data/processed_step2, data/processed_hist, data/sealed → four whole-directory
   links.**
   - Each is a guarded root (PROCESSED_ROOT, STEP2_ROOT, HIST_ROOT, SEALED_BASE), and each holds 0
     tracked files.
   - The whole-directory link is what ml_route accepts (H-02) and keeps every realpath guard
     consistent (H-00).
   - Costs:
     - H-01: one test fails. Lead decision.
     - H-06: `??` lines appear unless ignore entries are added. Lead decision.
   - Sweep B's H1 advice (keep data/processed real and link its sub-directories) is **rejected**: it
     would trade a test failure for silent guard fail-open (H-00).
3. **data/vendor/index_history → stays.**
   - It holds 11 tracked, hash-pinned K1/K3 inputs.
   - A link would show them as deleted and turn the K1 tests into skips (H-03).
   - The 18 ignored stoxx files (no code reference) are not worth moving.
4. **data/vendor/release_pages → lead decides; the default is keep.**
   - These are saved web pages, not exchange data (153.6 MB, 1.5% of the bytes).
   - Keeping them avoids H-04 (D.1f preflight set change) and H-08 (mtime).
   - If moved: one link at data/vendor/release_pages, copied with `cp -a`, then
     `screening.build_release_calendar --check` before and after. Git stays clean.
5. **Outside data/** (microbook cache, DIX.csv, ~/.cache/propexp_e14_c1): stay. They are small or
   outside the repo, and DIX.csv is path-frozen.

Copy method: `cp -a` or `rsync -a` (modes 444/664/775 and mtimes kept). There are no hard links to
split (A). Mirror layout: `/mnt/large-storage/market_data/PropExperiment/<repo-relative path>` (H-07).

## 4. Before and after checks (from C, with the merge's additions)

Run every command from the repo root, before the move and again after it. Diff the full outputs.

0. **Preconditions (merge, from H-03 and H-14).**
   - `mountpoint -q /mnt/large-storage`
   - `lsof -nP | grep -cE 'PropExperiment/data/(vendor|processed|sealed)'` = 0
   - `pgrep -af 'pytest|uv run'` is empty of project jobs
1. **Start checks.** `bash reports/stage_e26_briefs/checks.sh <harness sha256>`. It exercises the
   data in these blocks:
   - holdout status (lines 13-22): all 70 sealed blobs, MES research and confirmation, step 2
     products, and the existence checks on raws
   - E.18 C1b freeze (79-81): 6 ext2010 stores
   - E.20 store sha256 (86-102): 34 stores, plain open, CWD-relative
   - E.20 H6 freeze (103-104): NQ step 2 store and DIX.csv
   - E.20 search freeze (105-106): 17 step 2 stores, through realpath

   harness_freeze verify (26-27) must print the same result. `git status --short` (11) changes as
   H-06 describes.
2. **Holdout field values** (C §5.1). Every flag must be True, not None, and every list `[]`:
   ```
   uv run python -m data.holdout status | python3 -c 'import json,sys;d=json.load(sys.stdin);h=d["holdout_2"];print(d["all_ok"],d["research_parquet_ok"],d["research_has_no_holdout_rows"],h["confirmation_has_no_holdout2_rows"],h["unsealed_plaintext_present"],{r:(p["all_ok"],p["store_has_no_embargo_or_holdout2_rows"],p["unsealed_plaintext_present"]) for r,p in h["products"].items()})'
   ```
   Also report `unlocks_logged` (CLAUDE.md invariant).
3. **Link resolution guard** (C §5.3). For each moved path P:
   - `test -L P && test -e P && test "$(readlink -f P)" = /mnt/large-storage/market_data/PropExperiment/P`
   - also `test -d data/vendor/databento/GLBX.MDP3/ohlcv-1m/MES_v_0`, so the plaintext-absence
     checks are not vacuous
4. **Release pages.** Only if release_pages moves; harmless either way:
   `uv run --no-sync python -m screening.build_release_calendar --check`.
5. **Content identity** (lead, T1.4).
   - The sha256 of every moved file at the source equals the sha256 at the target. C's recorded-hash
     index covers 5,007 paths; 247 files have no recorded hash (172 rolls, 72 GLBX raws, 1 MES,
     1 NG, 1 condition).
   - `find <unit> -printf '%P %m %s %T@\n' | sort` before, against the same command on the target
     after, gives equal modes, sizes and mtimes.
6. **pytest** (lead, separately, with ≥ 8 GB free; memory note). Compare pass, fail **and skip**
   counts.
   - Expected differences: `tests/test_ml_route_store.py::test_research_store_root_is_refused_outright`
     fails (H-01) unless fixed.
   - test_holdout's rglob test passes vacuously (H-04).
   - Any new skip means a dangling link (H-03).
7. **Never** use as checks: release_pages `*_scripts/verify.py` (they rewrite reports), or any freeze
   rebuild (H-05).

## 5. Completeness critic

Gaps in the sweeps, covered here with metadata-only commands:
- **Worktree and sibling-checkout code (A and B both flagged this).**
  - A grep of `*.py/*.sh/*.toml/*.cfg` in the 3 .claude/worktrees and the 2 sibling checkouts
    (PropExperiment-e12-v8, -v9), outside .venv/.git, finds **0 files** naming
    `PropExperiment/data/(vendor|processed|sealed)`.
  - They do hard-code the repo root `/home/kiros-li/Documents/GitHub/PropExperiment` (27, 27, 70,
    22 and 22 files, all reports/ scripts, the same as the main repo's 215 reports/ hits). That path
    reaches the data lexically through the links, so plain opens follow them: SAFE.
  - No worktree holds data copies or links (A).
  - Outside the repo: no crontab entry, no systemd unit, and no code in other ~/Documents/GitHub
    checkouts names the data paths.
- **Code created after Sweep B's file list (02:18).**
  - 21 code files changed since 02:10 (list in the scratchpad file `new_code.txt`): the E.26 briefs
    and E.28 work scripts. None references a data path.
  - The exceptions are the lead's own seal_check.py (/mnt/large-storage/_e26_sealcheck probe) and
    move_data.py. Its aside root /home/kiros-li/e26_aside is outside the repo on the repo's
    filesystem, which satisfies B's EXDEV and harness-freeze concerns.
- **H13 (release_pages scripts).** Covered by a names-only grep (file names and match counts, no
  lines printed). **Interpretation call for the lead:** the brief forbids reading file contents
  under data/vendor. These are code, not market data, and Sweep C had already read some of them. I
  kept to names and counts.

Contradictions between the sweeps, resolved:
1. **The /mnt/large-storage change at 02:16:16 (A: unexplained).**
   - Explained: reports/stage_e26_briefs/seal_check.json has mtime 2026-10-21 02:16:16.685691799
     PDT, the same instant to the millisecond.
   - seal_check.py creates and cleans up /mnt/large-storage/_e26_sealcheck (lines 30, 82-88,
     134-135). It is the lead's T1.2 probe.
   - A **second** change happened at 02:19:14.80 PDT, after A's look. It left no residue
     (`ls -A`: Archive, Games, Installers, README.md, lost+found, .Trash-1000). Its source is not
     identified. The lead may know (a probe rerun?).
2. **The superseded files under data/processed.**
   - A says NG/superseded holds 2 files. In fact NG/superseded holds 1 file (the 921,327-byte
     `.outright-pattern-bug`), and **MES/superseded** holds
     `ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.step4b_failed_build.parquet`
     (26,213,714 B).
   - Counts reconcile: 47 depth-2 files (45 roots + 2 MES) + 2 superseded = 49 files, 48 of them
     named `*.parquet` (C's figure).
   - The MES superseded file covers the holdout-2 confirmation window. It moves with data/processed
     and stays under PROCESSED_ROOT's guards only with a whole-directory link (H-00).
   - A's directory counts exclude the root directory (e.g. 48 vs 49). Cosmetic.
3. **Granularity for data/processed.** B advises sub-directory links to save H-01; the realpath
   guards (H-00) need the whole directory. Resolved for the whole directory (section 3). B's S2
   "SAFE" holds only at root-level links.
4. **release_pages scripts.** B left them unread (H13); C quoted their content. Both are now
   consistent with the names-only grep: all 28 hard-code the repo path and none resolves.
5. **Agreements.** A, C and the merge's re-count agree on every size and file count.
   - C-H6 = B-H8 (per-product refusal) and C-H7 = B-H12 (naming).
   - C-H1/H2/H3 = B-H11 (fail-open).
   - C-H4 = B-H5/H6/H7 (new records).

Not covered by any sweep or by the merge:
- Runner-level loaders were traced only through the verifiers and guards above. That includes
  multiday, trigger_hold, microbook and ml_route_v2 world loading (C-8), though B's grep found their
  data references, and all are plain opens or resolve-both-sides.
- The 28 release_pages scripts were not read line by line (`__file__` use in 2 of them).
- lsof ran without root (every project process is uid 1000).
- The handle check is a snapshot.
- No market-data file was hashed. Integrity is T1.4.
- C's recorded-hash index is heuristic (`parquet_sha256`-by-root records are not path-indexed).
  Name-based manifest fields under index_history (19 not found, 3 with two hashes) and e4c (12 not
  found) predate the move. Compare them only before versus after.

Decisions for the lead:
1. **H-01**: fix ml_route/store.py (a harness change; the harness sha moves) or record the one
   expected test failure.
2. **H-06**: slash-free ignore lines in .gitignore (tracked) or .git/info/exclude (local) for the
   four whole-directory links, or accept `??` lines.
3. **release_pages**: keep (default) or move as one link.
4. **H-04**: whether to fix the two vacuous holdout scans (tests/test_holdout.py:307-313,
   tests/test_d1f_holdout2.py:164-182) now or record the coverage loss.
5. **H-03 / nofail**: whether to add a mount guard anywhere beyond the check preconditions.
   At minimum, every future start check should run step 0.
6. **Timing (H-14)**: a pytest run was live at 02:30 and E.28 runs in parallel. Swap only when
   step 0 passes.
7. The unexplained 02:19:14 change on /mnt/large-storage.
