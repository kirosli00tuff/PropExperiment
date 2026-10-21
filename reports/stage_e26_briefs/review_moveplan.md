# Stage E.26 T1.3: adversarial review of the move plan (MovePlanReviewer-FableXHigh)

Reviewer: Fable 5.1, xhigh, 2026-10-21 (about 02:45-03:25 PDT). Read-only on the repo and on
/mnt/large-storage; no market-data file content was read (metadata only: stat, find, lsattr, git).
Inputs reviewed in the brief's order: reports/stage_e26_move_plan.md and .json;
reports/stage_e26_briefs/move_data.py; loader_reads.py and checks.sh; stage_e26_inventory.md
sections 2-5; inv_disk.md sections 3-6, inv_code.md (H11, SAFE list, move_data observation),
inv_manifests.md sections 3 and 6-8; seal_check.py and seal_check.json. Code paths read myself:
data/config.py, data/holdout.py (paths, _record_paths, is_sealed_raw, verify_seal, _verify_holdout2,
status_report, _write_manifest, seal writer), data/step2_seal.py (verify, verify_all), data/hist_store.py
and data/step2_store.py (sealed_roots checks), base_rules/store.py (refuse_path, preflight),
pattern_search/guard.py and preflight.py, h6_rod/guard.py, ml_route/store.py, compute/datarules.py,
compute/files.py, compute/gitbundle.py, screening/harness_freeze.py, data/adapter.py, the
multiday/trigger_hold/pattern_search freeze verifiers, tests/test_holdout.py:301-313,
tests/test_d1f_holdout2.py:164-182 and 257-275 and 983-990.

move_data.py was exercised on synthetic trees under /home/kiros-li/e26_review_scratch (repo
filesystem, st_dev 64513) and /mnt/large-storage/_e26_review_scratch (ext4, the real destination
device), with the script copied to `<scratch>/reports/stage_e26_briefs/move_data.py` so that its
`REPO = parents[2]` pointed at the scratch tree. Eleven scenarios (A happy path, rollback, re-move,
finalize; B1-B10 crash and misuse states); scripts and raw output in this session's scratchpad
(`scripts/mdtest.sh`, `mdtest.out`, `mdtest2.sh`, `mdtest2.out`). Both scratch trees were deleted
before this review was returned.

## Findings

Labels: BLOCKING (must fix before any move), SHOULD FIX (fix before the move), NOTE.

### 1. SHOULD FIX: after `rollback`, `move` re-swaps the destination copy without re-verifying it, and `finalize` then deletes the only verified copy

Evidence: move_data.py:170 sets `state[s] = "verified"` once, after the only `compare()` call;
:221 `rollback` returns the state to `"verified"`; :173-185 the `"verified"` branch renames and
links with no `compare()`. Reproduced (scenario A): move, rollback, flip one byte in
`<dest>/data/sealed/S1/holdout_bars.sealed`, move again: every source "swapped" (rc 0); the sha256
read through the new link differed from the aside copy; `finalize` then deleted the aside (rc 0),
leaving only the altered copy.

Failure scenario in the real plan: step 4 finds an unexpected difference, step 6 rolls back ("the
destination copy is kept for inspection"), the cause is judged benign, step 2 is rerun. Anything
that changed the destination copy between the first copy and the rerun (inspection, a bad block,
an early E.28 write under the destination root) is swapped in unverified. The after-checks hash
the 34 + 6 + 17 stores and the 70 sealed blobs again, but not the 4,461 vendor files (step 4
compares only a `find` listing of name, mode, size and mtime for those), so a changed vendor file
would reach finalize unseen.

Fix: make rollback leave the source in a state that forces re-verification. For example
`rollback` sets `state[s] = "copied"`, and `cmd_move` handles `"copied"` as "dest exists, run
`compare(rows[s], dest, s)`, then continue as verified" (no second copy; the 8.6 GB is re-read,
not re-written). Equivalent: rollback deletes the state entry and the operator removes the
destination copy before the rerun; the first form is cheaper and keeps the tool's own guarantee
("every manifest entry re-checked at the destination" before every swap).

### 2. SHOULD FIX: `rollback` does not cover the two half-swapped states the plan worries about (crash or mount loss between `os.rename` and `os.symlink`)

Evidence: move_data.py:179-182. After `os.rename(src, aside)` the state is still `"verified"`;
`"swapped"` is written only at :183 after the symlink check. `cmd_rollback` (:215) handles
`"swapped"` only. Reproduced: (B2) src absent, aside full, state verified: `move` stops with
"`<aside> exists; inspect`", `rollback` prints nothing for that source and the repo path stays
ABSENT. (B3) a dangling link at src (mount gone before `os.symlink`, or `dest.is_dir()` False):
`move` stops with "already a symlink but state says verified; inspect", `rollback` skips it, the
dangling link stays and the data sits in the aside.

Both are safe (nothing lost) but the plan's step 6 ("rollback removes each link and renames the
aside copy back") is not true for them, and the operator has to repair by hand under time
pressure. Fix: in `cmd_rollback`, also treat `state == "verified" and aside.exists()` as a
rollback case (unlink `src` if it is a symlink, `os.rename(aside, src)`); and in `cmd_move`
write `state[s] = "swapped"` right after `os.symlink` succeeds, before the resolve check, so a
failed check leaves a state rollback understands. Keep the EXDEV behaviour (B7: a cross-device
aside root raises OSError before anything is renamed; state stays verified, source untouched).

### 3. SHOULD FIX: `finalize` deletes the aside when the link exists but points at the wrong target

Evidence: move_data.py:197 checks only `src.is_symlink() and src.exists()`. Reproduced (B6): link
`data/processed_hist -> <dest>/data/processed_step2` (an existing, complete, wrong directory):
`finalize` printed "aside deleted" (rc 0). B5 (dangling link) is refused correctly.

Step 4's link guard (`readlink -f P` equals the destination) runs before finalize, so the window
is between that guard and step 5; the tool is the last line and the check is one expression.
Fix: `if not (src.is_symlink() and src.exists() and src.resolve() == dest.resolve())` with
`dest = Path(plan["dest_root"]) / s`.

### 4. SHOULD FIX: a `finalize` interrupted inside `shutil.rmtree` followed by `rollback` puts a partial tree back at the repo path and reports success

Evidence: move_data.py:203 `shutil.rmtree(aside)` runs while the state is still `"swapped"`;
`"finalized"` is written at :206 afterwards. Reproduced (B4): one file removed from the aside to
stand for an interrupted rmtree of the 4,461-file vendor tree, then `rollback`: every source
"rolled back" (rc 0); the repo path became a real directory holding 1 of 2 files while the
complete copy sat unlinked on /mnt. Fix: write `state[s] = "finalizing"` before the chmod loop and
rmtree, and have `rollback` refuse a `"finalizing"` source ("aside is partly deleted; the
destination copy is the complete one, relink it") instead of renaming it back.

### 5. SHOULD FIX: apply the two test edits and the .gitignore lines before step 1, not after step 2

Evidence: plan step 3 edits tests/test_holdout.py and tests/test_d1f_holdout2.py after the move,
so the "before" pytest run (step 1 item 6) runs the unedited tests and the "after" run (step 4)
runs the edited ones, and the plan's acceptance rule ("the test subset has the same pass/fail/skip
counts") compares two different test programs. The same holds for `git status --short` in
checks.sh: after step 3 it gains ` M .gitignore`, ` M tests/test_holdout.py`,
` M tests/test_d1f_holdout2.py`, which the plan's expected-difference list ("the git status lines
of this stage's own new files") does not name; by the plan's rule an unlisted difference means
rollback.

Both edits are backward compatible with the current layout: with no symlink under data/,
`linked` is empty and the tests read exactly what they read today (verified on Python 3.12.13:
`rglob("*")` lists a symlink entry but does not descend into it; `os.walk(top=symlink)` and
`Path(symlink).rglob()` do enumerate the target), and the slash-free .gitignore lines match
nothing while the directories are real (`git check-ignore -v` today names lines 17-23). Fix:
make the edits before step 1, run the before-checks with them in place, and list the three ` M`
lines as expected in step 4 either way. Neither file is in any freeze: checked the harness manifest
(1065 files; test_holdout.py, test_d1f_holdout2.py and .gitignore absent, test_ml_route_store.py
present), reports/*.json, reports/*.sha256, docs/*.json (only stage_e26_inventory.json names them).

### 6. SHOULD FIX: the step 1/4 `find -printf '%P %m %s %T@'` listings will differ on directory sizes, a spurious failure that the plan's rule turns into a rollback

Evidence: `%s` on a directory is its on-disk size, which on ext4 depends on history (deleted
`.partial` names keep their blocks). Today 18 directories under data/vendor/databento are over one
block: rolls 20480 B with 190 entries; ZC/GC/6E/NQ/ZN/NG_v_0 16384 B with 180 entries;
ZL/LE/ZS/ZB/UB/CL/ZF/ZT_v_0 12288 B with 179 entries; HE_v_0 12288 B with 95 entries, RTY_v_0
12288 B with 96, TN_v_0 12288 B with 113, while every ~60-entry directory is 4096 B. A fresh
`cp -a` writes the minimum (HE_v_0 with 95 entries lands in 8192 B, 180-entry dirs likely in
12288), so the after listing differs from the before listing on several lines although every file
is identical. move_data.py itself is right not to compare directory size (:141-142). Fix: print
`%s` for files only, for example
`find <root> \( -type f -printf '%P f %m %s %T@\n' \) -o \( -type d -printf '%P d %m %T@\n' \) | sort`,
or diff the before/after listings with directory lines excluded.

### 7. SHOULD FIX (lead's call on the form): the two edited tests still pass vacuously on a dangling link

Evidence: plan step 3 builds `linked` with `p.is_symlink() and p.is_dir()`; `Path.is_dir()` is
False through a dangling link (verified), so a lost mount or a wrong target silently removes the
moved stores from both scans again, which is the H-03/H-04 coverage loss the edit exists to
prevent. Not a new false pass (today a deleted store directory passes the same way) but the move
makes the state reachable by a `nofail` boot. Fix: one assertion in each test before the scan,
e.g. `dangling = [p for p in root.rglob("*") if p.is_symlink() and not p.exists()]` /
`assert not dangling, dangling`; the test then fails closed when LARGE STORAGE is absent.

### 8. NOTE: resume paths that need manual repair, and the error messages that should say so

- B1 (crash during `cp -a`, or after the copy but before the state write): the rerun refuses
  "`<dest> exists before copy; inspect it (no overwrite)`" and the only way forward is to delete
  the partial destination by hand and copy again (8.6 GB for databento). A `verify` subcommand
  (compare an existing destination against the manifest, then mark verified) would make the
  "copied but state not written" case resumable without the recopy; the finding-1 `"copied"`
  state gives the same thing. Not required for safety.
- B7 (aside root on another device): an unhandled `OSError: [Errno 18] Invalid cross-device link`
  traceback, source untouched, state verified. A `os.stat(REPO).st_dev == os.stat(aside_root).st_dev`
  precheck (and `os.path.ismount("/mnt/large-storage")`, and a free-space check) in `cmd_move`
  would turn the plan's step 0 into code. If /mnt/large-storage is not mounted,
  `dest.parent.mkdir(parents=True)` fails with EACCES because the mount point is a root-owned 755
  directory; safe by accident, not by design.
- B9 (rollback when someone recreated a non-empty directory at the source path): unhandled
  `OSError: Directory not empty`, state stays swapped. Safe; message could say what to do.
- `move_problems.txt` is overwritten on each mismatch; keep the first (append or name it per source).

### 9. NOTE: what the tool verifies, and what it does not

- Compared field set (:141-142): kind, mode, uid, gid for every entry; size, mtime_ns, sha256 for
  files; target for symlinks; nothing extra for directories (mtime is recorded, not compared; cp -a
  does preserve it, and the find listing compares it). The root entry is included (scenario A:
  6 entries for a 2-file sealed tree = root, 2 subdirs, 1 empty dir, 2 files). Empty directories
  and dotfiles are covered. `nlink` is recorded, not compared (correct: a link to a file outside
  the tree would have nlink 1 at the destination; there are 0 such files, `find -links +1` on all
  four sources). The four sources hold 0 symlinks, 0 special files, 0 immutable or append-only
  attributes (lsattr), directories all 775, files 444 or 664, owner kiros-li:kiros-li only, so
  the cp -a / rename / rmtree paths are exercised only in their simple branches; B10 confirmed
  cp -a keeps a 555 directory and finalize's chmod loop still removes it.
- "From disk" (:45-46): `os.sync()` makes the copy's pages clean, `POSIX_FADV_DONTNEED` over the
  whole file evicts clean, unmapped pages; pages mapped or under I/O by another process are kept.
  Best effort, the standard trick without root (no `drop_caches`); adequate here. B8 (a byte
  flipped at the destination between cp and verify through a monkeypatched `subprocess.run`) was
  caught as both an mtime_ns and a sha256 mismatch, source untouched, state empty.
- The swap window (:179-180) is one `rename` and one `symlink`; a reader in it gets ENOENT, never
  wrong data, and a `data.holdout status` in it reports `holdout_blob_ok` False (a false alarm,
  not a false pass). A reader that opened a file before the swap keeps reading the aside inode
  until finalize, and an open handle survives finalize's unlink. Acceptable with step 0.
- The manifest is computed from the page cache (correct for the source) and refused on rerun
  (:109-110); if any source changes between the manifest and the copy, `compare` fails closed.

### 10. NOTE: the symlink layout and the code paths (the brief's first question)

Checked myself; the inventory's H-00..H-14 hold, with one correction below.
- Realpath/resolve guards resolve both sides: pattern_search/guard.py:52,80-107 and
  h6_rod/guard.py:49,64-90 (`_real` = realpath of root and path); base_rules/store.py:68-84 (the
  resolved parts of `/mnt/large-storage/market_data/PropExperiment/data/processed_step2/<R>/...`
  contain no `sealed` or `mes`, `resolved.parent.name == root`, and the sealed/research prefixes
  are resolved too); data/hist_store.py:150-152 and step2_store.py:171-173
  (`resolved.is_relative_to(Path(s).resolve())`); compute/datarules.py:147-171 (both spellings,
  no `sealed`/`ledger` component in the destination path) and :300 (final-component symlink only,
  so whole-directory links pass); ml_route/store.py:59-65 (`assert_store_root(STEP2_ROOT)` resolves
  to /mnt, PROCESSED_ROOT stays real, neither contains the other; the research-root test at
  tests/test_ml_route_store.py:53-56 keeps passing because data/processed stays).
- Holdout: `_record_paths` (holdout.py:267-273) and `is_sealed_raw` (:285) resolve both the
  absolute `original_path` and `REPO_ROOT / original_relpath` through the same link (seal_check.json
  `is_sealed_raw_same` true); `sealed_relpath` is joined to `sealed_root`, which is the link.
  Writers stay inside one directory (`.partial` + `os.link` in adapter.py:114-127; manifests in
  docs/ via holdout.py:578-593; no `os.replace`/`shutil.move` across data/ in production code:
  grep of compute, data, funnel, prop_econ, c1_replication).
- harness_freeze.py:37-38,73-89,113-126,132-150: rglob does not descend into links on 3.12,
  `_in_data_subdir` excludes the link entries, no `.py`/`.pyc`/`.sh` exists in any of the four
  sources (find: 0; suffixes zst 4266, json 98, jsonl 97, sealed 70, parquet 48). Unchanged output.
- Freeze verifiers (E.20 search, E.21, E.23) compare `str(p.resolve())` on both sides
  (pattern_search/preflight.py:104-110, multiday/freeze_manifest.py:111-127,
  trigger_hold/freeze_manifest.py:116-135); `rel()` appears only in messages. The E.17 run
  manifest's 44 store paths are all repo-relative (`data/processed_step2/...`), read through the
  links from the repo root. checks.sh `cd`s to the repo root.
- Unguarded `resolve().relative_to(ROOT)`: funnel/exposure_gate_mes.py:100 and
  exposure_gate_run.py:113 are applied to reports/ files only (call sites :453-455); the rest are
  guarded (`is_relative_to`) or wrapped in try (holdout.py:259-264), so they change spellings in
  new records only (H-05), never raise.
- Correction to H-03 / inv_manifests H1-H2: the holdout status is not fail-open on a lost mount.
  `verify_seal(DEFAULT_PATHS)` sets `holdout_blob_ok = paths.holdout_blob.exists() and ...`
  (holdout.py:400-401) and `all_ok` requires it (:419-422); the per-product reports require
  `sealed_ok` (step2_seal.py:186,211). Since all four links point at one mount, a `nofail` boot
  without the drive flips `all_ok` False at the next session-start check. The vacuous passes
  (`plaintext_absent`, `unsealed_plaintext_present`, the `is not False` clauses, the two scans)
  remain and matter only for a single wrong or missing destination directory; finding 7 and the
  step 4 link guard cover that.
- Nothing found that the inventory missed in the code paths named by the brief. Two small
  additions: `c1_replication/guards.py:146` copies a store with `shutil.copyfile` (through the link,
  fine) and `screening/stage_e_start_dates._display` (:146-150) is guarded by try (display only).

### 11. NOTE: keeping data/processed, data/vendor/release_pages and data/vendor/index_history is correct and sufficient

data/processed must stay for H-01 (ml_route/store.py:59-65 and its test) and holds the holdout
research and confirmation parquets whose `exists()` checks feed `all_ok`; release_pages holds 28
scripts hard-coding the repo path plus the D.1f `*.py` sets (strategy/research/_d1f_preflight.py,
_d1f_freeze.py; tests/test_d1f_confirmation.py:628-631 rglobs `data` for `*.py`); index_history
holds 11 tracked files (`git ls-files`), and a link above them would show them deleted. With
data/vendor real, the link at data/vendor/databento is ignored by `.gitignore:17 data/vendor/`
(reproduced in a scratch git repo, git 2.53.0: a symlink child of an ignored real directory stays
clean; a symlink at a trailing-slash-ignored top-level path shows `??` and `git add -A` would stage
it; the slash-free lines `/data/processed_step2`, `/data/processed_hist`, `/data/sealed` fix that and
`git check-ignore -v` names them). The four sources hold 0 tracked files. 3% of the bytes staying
is the right trade.

### 12. NOTE: concurrency with Stage E.28

- E.28's prompt makes Part B wait for E.26's STATE line and download "straight to
  /mnt/large-storage/market_data/PropExperiment/" (STAGE_E.28.md:159-161, 204-208); its end
  checks run the holdout status (:236), which reads data/sealed and exists-checks data/vendor. In
  the swap window that yields a false alarm (finding 9), never a false pass. The lsof precondition
  is a snapshot; after the first swap, `lsof | grep 'PropExperiment/data/...'` no longer sees
  readers of already-moved stores (their paths print as /mnt/...), which does not matter for the
  next swap.
- If E.28 pre-creates any directory under the destination root before the STATE line (for its
  own download target), `cmd_move` refuses that source ("exists before copy") and the lead must
  check nothing of E.28's is deleted. Worth one line in reports/stage_e26_STATE.md now: "destination
  root reserved; nothing under it until DATA MOVE: DONE".
- Step 0's "no pytest or uv job whose cwd is the main repo" will be false whenever an E.28 worker
  runs `uv run` on reports files; the condition that matters is 0 open handles under the four
  sources (lsof) plus no pytest. Phrase it that way or the lead will be blocked or tempted to skip
  the check.
- E.28's download, after DONE, writes through the data/vendor/databento link into the moved store
  (new paths recorded as /mnt or absolute, H-05); the step 4 `find_after` listings are a snapshot
  of that moment, not a lasting manifest. E.28 must not `git add -A` or `git stash` while E.26's
  .gitignore and test edits are uncommitted (its prompt already forbids staging E.26 files).
- The unexplained /mnt/large-storage mtime change at 02:19:14 (inv_disk section 5) matches the
  plan header's "tested 02:17-02:19 on a synthetic tree"; it is almost certainly the lead's own
  move_data.py test, and the top level is clean now (ls -A: Archive, Games, Installers, README.md,
  lost+found, .Trash-1000; market_data absent; /home/kiros-li/e26_aside absent).

### 13. NOTE: smaller points on the plan text and the after-check expectations

- Byte counts and file counts agree with my own `find` (70 / 17 / 31 / 4,461 files); the aside root
  and the repo are both st_dev 64513; /mnt/large-storage is /dev/nvme1n1p2 ext4 (`defaults,nofail`),
  769 GiB available (825 GB, the plan's figure), mount point mode 700 kiros-li.
- `holdout_after.json` byte-for-byte equal to `holdout_before.json` is a sound expectation: the
  report holds booleans, counts, chunk names and `Path(original_path).name` keys, no timestamps and
  no resolved paths (holdout.py:396-423, 739-770, step2_seal.py:177-213; `json.dumps(indent=1)` at
  holdout.py:801). `loader_after.json` differs from `loader_before.json` only in `paths_resolved`
  (dbn_header.path is the unresolved `raw_path` string; preflight records carry root, era, plan,
  sha256, splices; errors are 0 before, so any error line after is a real difference).
- The pytest subset: only tests/test_holdout.py (TestRealStore, after the edit also the step2/hist
  parquets) and tests/test_d1f_holdout2.py (TestRealStores, the scan) read any moved path; the other
  six files read data/processed, index_history, release_pages or nothing (grep of the eight files
  for the moved roots). So "any new skip means a dangling link" applies to none of the moved paths
  (their reads fail, not skip); the statement is harmless but the real after-check of the moved
  data is checks.sh (E.18 C1b, E.20 store block, E.20 search, E.21/E.23 verifiers over the stores,
  holdout status over the 70 blobs) plus loader_reads.py and the link guard.
- `cp -a --no-target-directory` creates the destination directory itself (scenario A); `cp -a`
  across ext4 to ext4 preserved 444/664/555 modes, uid/gid and nanosecond mtimes (scenario A and
  seal_check.json). `--preserve=all` treats xattr failures as warnings, not errors, so `check=True`
  cannot fail on them.
- `load_plan` validates `sources` but not `dest_root`/`aside_root` (absolute, outside the repo, on
  the right devices). The plan JSON is fixed, so this is a hardening note.
- The plan says "Nothing is deleted" during step 2; true. Step 5 deletes the aside per source and
  stops at the first problem after deleting earlier sources' asides (B5: sealed's aside gone, hist's
  kept); correct, since each deleted aside had its own passing link check.

## Answers to the brief's questions, in one line each

- Freeze, seal, harness, run-manifest and guard checks: none breaks, none silently passes, and the
  only behaviour change is spellings in new records (H-05), provided the links sit exactly at the
  four roots (finding 10). The holdout status fails closed on a lost mount (finding 10, correction).
- data/processed, release_pages, index_history staying: correct and sufficient (finding 11).
- move_data.py: cp -a, the field set, dir and root entries, empty dirs, dotfiles, the from-disk read
  and the first-pass verify are right (finding 9); the state machine has four holes (findings 1-4),
  all small to fix; EXDEV and a recreated source fail loudly and safely (finding 8).
- Test edits and .gitignore lines: correct and sufficient; they read the same files as before; the
  tests stay vacuous on a dangling link (finding 7); apply them before the before-checks (finding 5).
- After-check expectations detect a dangling link (link guard, `exists()`-based sealed checks, test
  failures), a partial copy (the tool's compare; after the move the sha blocks over the stores and
  blobs), a wrong target (`readlink -f` guard; add it to finalize, finding 3) and a mount loss
  (step 0, link guard, `holdout_blob_ok`); the `find` listing will raise a false alarm on directory
  sizes (finding 6).
- E.28: no data risk while it waits for the STATE line; false alarms and a blocked copy are the
  realistic interactions (finding 12).

## Not done or not verifiable here

- No real data file was hashed or opened; the tool was tested on synthetic trees only, so copy time
  and the page-cache eviction on an 8.6 GB tree are untested.
- `uv run python -m data.holdout status` and the pytest subset were not run (the lead's T1.4 does
  both; the start-check output of 02:11 was not re-derived).
- E.28's actual code and STATE polling were not read, only its prompt.
- lsof ran as uid 1000 and is a snapshot (every project process is uid 1000).

VERDICT: APPROVE AFTER FIXES (findings 1, 2, 3, 4 in move_data.py; 5 and 6 in the plan's order and
after-check commands; 7 in the two test edits, form at the lead's discretion).
