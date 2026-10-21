# Stage E.26 T1.3: move plan (market data to LARGE STORAGE)

Lead: Opus 5.5 (E.26), written 2026-10-21 02:40 PDT. Inputs: reports/stage_e26_inventory.md (+ .json; sweeps
reports/stage_e26_briefs/inv_disk.md, inv_code.md, inv_manifests.md), the T1.2 seal check
(reports/stage_e26_briefs/seal_check.py, seal_check.json: verify_seal identical on the repo disk, on
/mnt/large-storage and through a symlink; cp -a keeps mode, uid, gid and mtime_ns; the 444 scheme refuses
writes on both; plaintext behind a symlink is still detected). Tool: reports/stage_e26_briefs/move_data.py
(tested 02:17-02:19 on a synthetic tree: copy, from-disk sha256 verify, symlink, rollback, re-move,
finalize, a one-byte flip at the destination detected). Machine plan: reports/stage_e26_move_plan.json.

## 1. What moves, what stays

Destination root: `/mnt/large-storage/market_data/PropExperiment/` (ext4, its own device, 825 GB free,
does not exist yet). Each source keeps its repo-relative path under it (inventory H-07: no `sealed`, `mes`
or `ledger` component above the stores).

| Order | Source (repo-relative) | Bytes | Files | Destination | Old path becomes |
|---|---|---:|---:|---|---|
| 1 | data/sealed | 28,306,346 | 70 | /mnt/large-storage/market_data/PropExperiment/data/sealed | symlink (absolute target) |
| 2 | data/processed_hist | 464,057,539 | 17 | .../PropExperiment/data/processed_hist | symlink |
| 3 | data/processed_step2 | 592,497,579 | 31 | .../PropExperiment/data/processed_step2 | symlink |
| 4 | data/vendor/databento | 8,608,399,283 | 4,461 | .../PropExperiment/data/vendor/databento | symlink |
| | **Total** | **9,693,260,747** | **4,579** | | |

Smallest first, so a problem shows on the 28 MB store before the 8.6 GB one. Each link sits exactly at a
guarded root (SEALED_BASE, HIST_ROOT, STEP2_ROOT, VENDOR_ROOT), which keeps every realpath-prefix guard
consistent (inventory H-00) and is what ml_route and compute/datarules accept (H-02).

Stays in the repo, with the reason:
- **data/processed** (303,035,283 B, 49 files; PROCESSED_ROOT, MES's Stage D store and the holdout research
  and confirmation parquets). A link there changes the refusal reason of
  `ml_route.store.assert_store_root(PROCESSED_ROOT.parent)` (ml_route/store.py:59-65) and fails
  tests/test_ml_route_store.py::test_research_store_root_is_refused_outright (H-01). The fix is a harness
  code change, outside this stage's scope. 3% of the bytes; it stays.
- **data/vendor/release_pages** (153,575,775 B, 4,263 files): saved web pages and 28 scripts, not exchange
  data; the D.1f preflight's `*.py` scan would lose the scripts (H-04) and its builder reads st_mtime (H-08).
- **data/vendor/index_history** (29 files, 11 of them tracked and sha-pinned by K1/K3) and therefore
  **data/vendor** itself: a link would make git report the tracked files as deleted.
- **data/** (the Python package), data/calendars (tracked), .env and every secret: never move.
- Outside data/: reports/stage_e22_microbook/cache, reports/stage_e14_briefs/gex/DIX.csv (path-frozen by
  the E.20 H6 freeze), ~/.cache/propexp_e14_c1: small or outside the repo; they stay.

The sealed stores move because T1.2 found no difference on /mnt (README of /mnt/large-storage: the drive
is not encrypted and holds no secrets; the seals are a commitment device keyed by a sentence that is in
the code, and market data is not a secret, so nothing secret goes there).

## 2. Order of operations

Every command runs from the repo root, at nice 10, one heavy job at a time.

**Step 0, preconditions (before step 1 and again right before step 2):**
`mountpoint -q /mnt/large-storage`; `lsof -nP 2>/dev/null | grep -cE 'PropExperiment/data/(vendor|processed|sealed)'`
= 0; no pytest or uv job whose cwd is the main repo (`for p in $(pgrep -f pytest); do readlink /proc/$p/cwd; done`);
`free -m` (at least 2 GB available); destination root absent; aside root /home/kiros-li/e26_aside absent and on
the repo's filesystem (st_dev 64513).

**Step 1, T1.4 before checks (outputs under reports/stage_e26_briefs/, quoted in the return):**
1. `bash reports/stage_e26_briefs/checks.sh dd2bcc60...` -> before_checks.txt (git status, git log, holdout
   status keys, REGISTRATION.md bytes, E.1/E.2a freezes, harness v13 preflight, K1-K8 cluster freezes, ledger
   lines and sha256, per-account spend, v2 freeze, N, E.14/E.16/E.18/E.20 H6/E.20 search/E.21/E.22/E.23/F1
   freezes, the E.20 store sha256 block over 34 stores).
2. `uv run python -m data.holdout status` full JSON -> holdout_before.json, plus the field-value line
   (inventory section 4 item 2: all_ok, research_parquet_ok, research_has_no_holdout_rows,
   confirmation_has_no_holdout2_rows, unsealed_plaintext_present, each product's all_ok,
   store_has_no_embargo_or_holdout2_rows and unsealed_plaintext_present).
3. `PYTHONPATH=. uv run python reports/stage_e26_briefs/loader_reads.py loader_before.json`: base_rules.store.preflight
   over the 27 roots / 44 stores of E.21's run manifest (row-free: sha256, metadata, rolls on the calendar)
   and the DBN header of the first MES chunk (dry run at 02:38: 27 roots, 44 stores, 0 errors).
4. `uv run python reports/stage_e26_briefs/move_data.py manifest reports/stage_e26_move_plan.json`:
   move_manifest.jsonl (one line per dir, file and symlink: mode, uid, gid, mtime_ns, size, nlink, sha256)
   and move_manifest_summary.json (counts, bytes, the manifest's own sha256).
5. `find <each source> -printf '%P %m %s %T@\n' | sort` -> find_before_<n>.txt (an independent listing).
6. The data-path test subset with skips listed:
   `nice -n 10 uv run pytest -q -p no:cacheprovider -rs tests/test_holdout.py tests/test_d1f_holdout2.py
   tests/test_ml_route_store.py tests/test_base_rules_store.py tests/test_k1_members_tables.py
   tests/test_build_release_calendar.py tests/test_d1f_confirmation_window.py tests/test_leakage_canaries.py`
   -> pytest_subset_before.out (pass, fail and skip counts and the skip reasons).

**Step 2, T1.5 move:** `uv run python reports/stage_e26_briefs/move_data.py move reports/stage_e26_move_plan.json`.
Per source, in order: `cp -a --no-target-directory` to the destination; `sync`; every manifest entry
re-checked at the destination (same path set; kind, mode, uid, gid; files: size, mtime_ns and sha256
recomputed after POSIX_FADV_DONTNEED so the bytes come from the disk, not the page cache; symlinks: target);
then `os.rename(source, /home/kiros-li/e26_aside/<source>)` (same filesystem, atomic) and
`os.symlink(<destination>, <source>)`, then a check that the source is a link resolving to the
destination. A mismatch stops the run with the source untouched in place. State per source in
move_state.json (pending, verified, swapped, finalized); the run resumes from it. Nothing is deleted.

**Step 3, two repo edits that the links require (no freeze, harness file or frozen member touched;
checked by grep: neither file is listed in any reports/*freeze*.json or reports/*.sha256):**
- .gitignore, appended (H-06: git never applies a trailing-slash pattern to a symlink, so the three
  top-level links would show as `??` and could be staged as mode-120000 entries, which compute/gitbundle.py
  refuses; data/vendor/databento sits inside the real, ignored data/vendor/ and stays clean):
  ```
  # Stage E.26 (V45): these are symlinks to /mnt/large-storage/market_data/PropExperiment/; git does not
  # apply a trailing-slash pattern to a symlink, so each is also listed without one
  /data/processed_step2
  /data/processed_hist
  /data/sealed
  ```
- Two holdout tests whose scans start above a link and would silently stop covering the moved data (H-04):
  tests/test_holdout.py::TestRealStore::test_no_plaintext_parquet_under_data_holds_a_holdout_date
  (`root.rglob("*.parquet")`) and tests/test_d1f_holdout2.py::...::test_i_no_plaintext_of_a_sealed_chunk_survives_anywhere
  (`os.walk` over REPO_ROOT). Each also scans the symlinked directories under data/:
  ```python
  # test_holdout.py
          root = Path(ho.DATA_ROOT)
          # Stage E.26: data stores are symlinks to LARGE STORAGE; rglob does not descend into a link
          linked = [p for p in root.rglob("*") if p.is_symlink() and p.is_dir()]
          for parquet in [p for base in (root, *linked) for p in base.rglob("*.parquet")]:
  # test_d1f_holdout2.py
          roots = [world.root, Path("/tmp"), Path(tempfile.gettempdir()), REPO_ROOT,
                   *CLIENT_CACHE_CANDIDATES,
                   # Stage E.26: data stores are symlinks to LARGE STORAGE; os.walk does not follow them
                   *(p for p in (REPO_ROOT / "data").rglob("*") if p.is_symlink() and p.is_dir())]
  ```
  Before the move these tests read the same files (the stores were under data/); the edit restores that
  coverage and reads nothing new.

**Step 4, T1.6 after checks:** step 0 again; the link guard for each moved path P:
`test -L P && test -e P && test "$(readlink -f P)" = /mnt/large-storage/market_data/PropExperiment/P`, and
`test -d data/vendor/databento/GLBX.MDP3/ohlcv-1m/MES_v_0` (so plaintext-absence checks are not vacuous,
H-03); then items 1-3, 5 and 6 of step 1 again (after_checks.txt, holdout_after.json, loader_after.json,
find_after_<n>.txt on the destinations, pytest_subset_after.out). Expected: after_checks.txt equals
before_checks.txt apart from the date line and the git status lines of this stage's own new files;
holdout_after.json equals holdout_before.json byte for byte; loader_after.json equals loader_before.json
apart from "paths_resolved"; find listings equal; the test subset has the same pass/fail/skip counts (any
new skip means a dangling link). `git status --short` shows no data path and no link; `git check-ignore -v`
names the .gitignore line for each link. Any difference that is not expected: rollback (step 6).

**Step 5, finalize (only when step 4 passes):** `move_data.py finalize` deletes /home/kiros-li/e26_aside/<source>
for each swapped source (the source "is deleted only after its copy is verified and its symlink is in
place"; here also only after the after-checks), then `rmdir` of the empty aside tree. T1.7: the STATE file
gets "DATA MOVE: DONE" with the destination root, so E.28 downloads there. A line naming
market_data/PropExperiment is added to /mnt/large-storage/README.md (outside the repo).

**Step 6, rollback (any time before step 5):** `move_data.py rollback` removes each link and renames the
aside copy back (the destination copy is kept for inspection); the .gitignore and test edits are reverted
with `git checkout -- .gitignore` and the two test files' edits undone.

## 3. Hazards (inventory section 2) and how the plan handles each

| ID | Handling |
|---|---|
| H-00 realpath guards fail open below their root | links only at the guarded roots themselves |
| H-01 ml_route research-root test | data/processed stays |
| H-02 per-product / per-file links refused | whole-directory links only |
| H-03 mount loss fails open (`nofail`) | step 0 and the link guard before every check; compared field values and skip counts. Recorded for the user: a fail-closed mount check at session start (decision in the return) |
| H-04 scans above a link narrow | the two test edits (step 3); D.1f preflight unaffected (release_pages stays) |
| H-05 records written after the move carry /mnt paths | no freeze or manifest is rebuilt here; recorded in V45 for later stages |
| H-06 git sees links | .gitignore lines (step 3); links never committed |
| H-07 naming | mirrored layout |
| H-08 mtime | cp -a; mtime_ns compared per file |
| H-09 release_pages scripts | release_pages stays |
| H-10 CWD-relative verifiers | all checks from the repo root |
| H-11 same-directory writes, EXDEV | unaffected (writers keep temp and target in one directory); the aside root is on the repo's filesystem |
| H-12 harness rglob | links only at existing DATA_SUBDIRS paths (data/vendor/databento is under data/vendor, data/sealed, data/processed_step2, data/processed_hist are DATA_SUBDIRS) |
| H-13 resolve-equality pairs | safe (both sides resolve through the same link; T1.2 is_sealed_raw test) |
| H-14 swap window, concurrent readers | step 0 right before the move; E.28 reads no market data in its Parts C and A and waits for the STATE line before its download |

## 4. Not done here

No freeze, run manifest, holdout manifest or harness manifest is rebuilt or edited; no market data is read
beyond checksums, the holdout tool's own checks, base_rules' row-free preflight and one DBN header; no file
is deleted before step 5.
