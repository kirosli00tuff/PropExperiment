# Stage E.26 T1.1 brief: market-data inventory before the move (shared by the three sweeps and the merge)

Lead: Opus 5.5 (E.26). Stage prompt: docs/prompts/STAGE_E.26.md, Task 1 (read T1.1-T1.7 there).

## Context

The program's market data will move from the repo folder to /mnt/large-storage/market_data/PropExperiment/
(ext4, same machine, mirroring the repo-relative layout), with a symlink left at every old path. Before
any file moves, the lead needs a complete inventory: what is market data, where, how big, how it is
tracked by git, and every manifest, freeze, holdout record, script or test that refers to it or would
behave differently once the old path is a symlink to another filesystem. A missed reference can
silently break a freeze, a holdout seal or a harness check, so completeness matters more than speed.

Known so far (lead, 02:10 PDT; verify, do not trust):
- data/vendor (8.2G: databento/{GLBX.MDP3,condition,rolls,symbology} 8.1G, release_pages 155M,
  index_history 1.2M), data/processed (290M), data/processed_step2 (566M), data/processed_hist (443M),
  data/sealed (28M; six holdout stores, encrypted blobs, mode 664; checked by sha256 against
  docs/HOLDOUT_MANIFEST.json, docs/HOLDOUT2_MANIFEST.json and per-product holdout-2 manifests).
- .gitignore ignores data/vendor/, data/processed/, data/processed_step2/, data/processed_hist/,
  data/sealed/ WITH a trailing slash (git does not apply a trailing-slash pattern to a symlink).
- 11 files under data/vendor/index_history/ ARE tracked by git despite the ignore rule.
- data/calendars/ is tracked code and JSON (calendar tables), not market data: it never moves.
- Code under data/ (the Python package) is NOT data and never moves. .env, keys and secrets never move.
- Python is 3.12 (pyproject requires >=3.12,<3.13): Path.glob/rglob with ** does not descend into a
  symlinked directory found below the starting directory; os.walk does not follow symlinks by default.
- screening/harness_freeze.py scans HARNESS_DIRS (which include data) with rglob and skips
  DATA_SUBDIRS (data/processed, data/processed_step2, data/vendor, data/sealed, data/processed_hist).
- data/holdout.py resolves both sides when it compares paths (_record_paths, is_sealed_raw) and
  records original_relpath via Path.resolve().relative_to(REPO_ROOT).

## Hard boundaries (all workers)

- READ-ONLY. Move, copy, delete, rename, chmod or touch nothing under the repo or /mnt/large-storage.
  Write only your own output files named below.
- Never read the contents of any market-data file: no head, cat, less, tail, od, xxd, strings,
  python open() or pandas/pyarrow/databento reads of any file under data/vendor, data/processed*,
  data/sealed, or any parquet, dbn, zst, csv or npz of bars anywhere. Metadata only: find, stat, du,
  ls, git ls-files, git check-ignore, lsof, file counts. Do not hash data files either (the lead
  hashes in T1.4). JSON manifests and freeze files under reports/ and docs/ ARE readable, by section
  (grep, jq with field selection, short python that prints only the fields needed); never load a
  large file into context.
- Do not import modules that load bars or outcome data. Static reading of code (grep, ast) is fine.
- No network, no Databento, no TopstepX. Never open .env or print any secret.
- Do not run pytest. Do not spawn further workers.
- Keep command output short (counts and summaries, logs to files under your output folder).

## Sweep A: disk (DataInvDisk-OpusHigh). Output: reports/stage_e26_briefs/inv_disk.md

1. Every directory and file under the repo that holds market data, at the granularity that matters
   for a symlink plan: for each of data/vendor/* (one level down, and data/vendor/databento/* one more),
   data/processed, data/processed_step2, data/processed_hist, data/sealed/*: size (du -sb), file count,
   dir count, git status of its contents (tracked count via git ls-files, ignored via git check-ignore,
   untracked-not-ignored count), existing symlinks inside (find -type l), hard links (find -links +1
   -type f), file modes and owners (distinct values with counts), any sparse or special files, newest
   and oldest mtime.
2. Market data OUTSIDE data/: search the whole repo (excluding .venv, .git, node_modules) for *.dbn,
   *.dbn.zst, *.zst, *.parquet, *.feather, *.arrow, *.npz, *.npy, *.h5, *.pkl, bar or tick CSVs,
   cache directories (names containing cache, bars, ticks, store), and large files (> 20 MB). For each
   hit, say whether it is market data, a run output, or something else, and whether it is tracked.
   Include balt_full.json and ni_full.json at the repo root (metadata and git status only; you may read
   the first 300 bytes of these two JSON files to classify them, nothing more). Include .claude/worktrees/
   (do worktrees hold data copies or symlinks?).
3. Which directories mix tracked files with ignored data (so a whole-directory symlink would make git
   report the tracked files as deleted), with the exact tracked paths.
4. Open handles: lsof +D on each data directory (or lsof | grep the paths) to see whether any running
   process (E.28 in the parallel session, the AiTrader collector, anything) holds a data file open now.
5. Free space on /mnt/large-storage and whether /mnt/large-storage/market_data exists already and
   what is in it (ls, du; nothing written).

## Sweep B: code references (DataInvCode-OpusHigh). Output: reports/stage_e26_briefs/inv_code.md

Search every tracked and untracked *.py, *.sh, *.toml and *.cfg in the repo (exclude .venv, .git,
.claude/worktrees) for references to the data locations: data/config.py constants (DATA_ROOT,
PROCESSED_ROOT, VENDOR_ROOT and the rest), other modules' path constants, string literals naming
data/vendor, data/processed*, data/sealed, release_pages, index_history, GLBX.MDP3, and paths built by
joining those constants. For each reference, record file:line, what the code does with the path, and
whether it would break or change behaviour if (a) the top-level data directory (for example
data/processed_step2) became a symlink to /mnt/large-storage/..., or (b) a sub-directory (for example
data/vendor/databento) did. Look specifically for:
- Path.resolve(), os.path.realpath, relative_to(REPO_ROOT) or is_relative_to guards (a resolved path
  now lands outside the repo), and equality comparisons between a resolved path and a recorded one.
- is_symlink, lstat, os.walk (followlinks default False), Path.glob/rglob with ** starting ABOVE a
  symlinked directory, glob.glob(recursive=True), shutil.copytree, shutil.rmtree (refuses a symlink).
- os.rename, os.replace, Path.rename, Path.replace, shutil.move and atomic-write helpers where the
  temporary file and the destination may now sit on different filesystems (EXDEV); tempfile with dir=.
- os.link (hard links), chmod on targets, fsync of a directory, file locks, inode or st_dev checks.
- git commands run on data paths (git ls-files, check-ignore, status) by code or tests.
- Tests under tests/ that create, list or delete files in the REAL data directories (not tmp_path).
Report the Python version in .venv (`.venv/bin/python -V`). End with a table: hazard, file:line,
severity (BREAKS / CHANGES BEHAVIOUR / SAFE), the symlink granularity that avoids it.

## Sweep C: manifests and verifiers (DataInvManifests-OpusHigh). Output: reports/stage_e26_briefs/inv_manifests.md

Every record that names a data path or hashes a data file: reports/*freeze*.json, reports/*.sha256,
reports/stage_e17_run_manifest.json and other run manifests, docs/HOLDOUT_MANIFEST.json,
docs/HOLDOUT2_MANIFEST.json and the per-product holdout-2 manifests (find where step2_seal keeps them),
manifests or index files that live INSIDE the data directories (store manifests in data/processed_*/,
data/vendor/**/manifest*.json*; list their names and sizes only, do not read inside data dirs beyond
JSON/JSONL manifest files, and for those print only key names and path-like fields), E.2a hashed
tables, base_rules/store.py's store manifest, microbook manifests, ledger lines that record paths
(count only). For each: the path form recorded (absolute /home/..., repo-relative, or relative to a
store root), the verifier and its exact command (module and function, for the lead's before and after
checks), how the verifier opens the path (plain open follows symlinks; resolve()-equality; is_file;
lstat; st_size; mtime; st_nlink; st_ino), and whether a symlinked old path keeps it passing. Also list
every verification command the start checks run (reports/stage_e26_briefs/checks.sh) that reads data
through these paths (for example the E.20 store sha256 block), so the lead knows which after-checks
exercise the symlinks.

## Merge (DataInvMerge-OpusHigh). Output: reports/stage_e26_inventory.md and reports/stage_e26_inventory.json

Read the three sweep files. Produce one inventory: (1) a table of every market-data source path with
size in bytes, file count, git status (tracked / ignored / mixed), and the references (manifests,
scripts, tests) to it; (2) the hazard list from B and C, deduplicated, with severity; (3) a
recommended symlink granularity per source (whole directory, sub-directory, or per file) with the
reason, which keeps every tracked file in place and in git; (4) the before and after check commands
from C; (5) a completeness critic section: what none of the sweeps covered, contradictions between
sweeps (resolve them by re-checking the evidence yourself with metadata-only commands), and anything
the lead must decide. The JSON holds the source table only: [{"path", "bytes", "files", "git",
"granularity", "references": [...]}]. Same boundaries as the sweeps.

## Return (every worker)

The output path, a summary of at most 200 words, and anything you could not finish. Report failures
and uncertainties, not only clean results.
