# Stage E.26 T1.1 Sweep A: disk inventory (DataInvDisk-OpusHigh)

Worker: DataInvDisk-OpusHigh (opus, high). Run 2026-10-21 02:14 to 02:20 PDT. Brief:
reports/stage_e26_briefs/brief_inventory.md, section "Sweep A: disk".

Method: metadata only (find, stat, du, lsattr, getfacl, git ls-files, git check-ignore, lsof, df,
findmnt). No market-data file was opened, read or hashed. The only file contents read were the first
300 bytes of balt_full.json and ni_full.json (allowed by the brief), the docstring of microbook/data.py
(code), and two fields (`store`, `condition_file`) of two bar-build report JSONs under reports/.
Raw logs: reports/stage_e26_briefs/inv_disk_logs/ (units.log, outside_data_ext.log,
outside_data_ext_grouped.log, outside_csv.log, lsof.log).

## 0. Verdict on the lead's "known so far" list

| Lead claim | Check | Result |
|---|---|---|
| data/vendor 8.2G, databento 8.1G, release_pages 155M, index_history 1.2M | du -sb | Confirmed (8.16 GiB, 8.02 GiB, 146.5 MiB apparent / 155 MiB allocated, 1.05 MiB apparent / 1.13 MiB allocated). |
| processed 290M, step2 566M, hist 443M, sealed 28M | du -sb | Confirmed in MiB (289.0, 565.0, 442.6, 27.0 MiB). |
| sealed: six holdout stores, mode 664 | find -printf %m | Confirmed: 6 stores, 70 files, all 664, dirs 775. |
| .gitignore ignores the five dirs with a trailing slash | grep .gitignore | Confirmed, lines 17-20 and 23. No .gitattributes, no nested .gitignore under data/, no info/exclude entries, no git-lfs. |
| 11 files under data/vendor/index_history tracked despite the ignore | git ls-files | Confirmed (list in section 3). |
| data/calendars is tracked code and JSON | git ls-files | Confirmed: 16 tracked files; its 20 other files are __pycache__ (ignored by `__pycache__/`). Not market data. |

## 1. Market data inside data/ (per unit)

All units: on the root filesystem (/dev/mapper/ubuntu--vg-ubuntu--lv, ext4, st_dev 64513), owner
kiros-li:kiros-li throughout. No symlinks, no hard links (find -type f -links +1 = 0), no sparse files
(allocated blocks >= size for every file), no special files (fifo, socket, device), no extended
attributes beyond the ext4 `e` (extents) flag, no immutable or append-only flag (lsattr), no ACLs
(getfacl -s: 0), no mtime in the future. Git columns: tracked = `git ls-files`, ignored =
`git ls-files -o -i --exclude-standard`, untracked-not-ignored = `git ls-files -o --exclude-standard`.

| Unit | bytes (du -sb) | files | dirs | tracked | ignored | untracked | file modes | oldest mtime (PDT) | newest mtime (PDT) |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| data/vendor (total) | 8,763,076,917 | 8,753 | 132 | 11 | 8,742 | 0 | 444: 4,456; 664: 4,297 | 2026-09-16 21:58 | 2026-10-10 01:30 |
| data/vendor/databento (total) | 8,608,399,283 | 4,461 | 97 | 0 | 4,461 | 0 | 444: 4,456; 664: 5 | 2026-09-16 21:58 | 2026-10-10 01:30 |
| data/vendor/databento/GLBX.MDP3 | 8,605,473,695 | 4,266 | 93 | 0 | 4,266 | 0 | 444: 4,266 | 2026-09-16 21:59 | 2026-10-10 01:26 |
| . GLBX.MDP3/mbp-1 (45 symbol dirs) | 7,404,915,927 | 229 | 45 | 0 | 229 | 0 | 444 | | |
| . GLBX.MDP3/ohlcv-1m (46 symbol dirs) | 1,200,557,768 | 4,037 | 46 | 0 | 4,037 | 0 | 444 | | |
| data/vendor/databento/condition | 761,530 | 4 | 0 | 0 | 4 | 0 | 444: 3; 664: 1 | 2026-09-16 22:10 | 2026-10-10 01:19 |
| data/vendor/databento/rolls | 2,147,559 | 190 | 0 | 0 | 190 | 0 | 444: 186; 664: 4 | 2026-09-16 21:58 | 2026-10-10 01:30 |
| data/vendor/databento/symbology | 16,499 | 1 | 0 | 0 | 1 | 0 | 444: 1 | 2026-09-23 16:57 | 2026-09-23 16:57 |
| data/vendor/index_history | 1,101,859 | 29 | 4 | **11** | 18 | 0 | 664: 29 | 2026-09-27 06:16 | 2026-09-28 01:03 |
| data/vendor/release_pages | 153,575,775 | 4,263 | 28 | 0 | 4,263 | 0 | 664: 4,263 | 2026-09-26 13:36 | 2026-09-27 13:24 |
| data/processed | 303,035,283 | 49 | 48 | 0 | 49 | 0 | 444: 49 | 2026-09-17 07:47 | 2026-09-25 02:21 |
| data/processed_step2 | 592,497,579 | 31 | 31 | 0 | 31 | 0 | 444: 31 | 2026-09-27 18:50 | 2026-10-03 12:09 |
| data/processed_hist | 464,057,539 | 17 | 19 | 0 | 17 | 0 | 444: 17 | 2026-10-09 22:42 | 2026-10-10 01:30 |
| data/sealed (total) | 28,306,346 | 70 | 12 | 0 | 70 | 0 | 664: 70 | 2026-09-17 07:47 | 2026-09-27 18:49 |
| data/sealed/MES_holdout_v1 | 3,138,538 | 5 | 1 | 0 | 5 | 0 | 664 | 2026-09-17 07:47 | 2026-09-17 07:47 |
| data/sealed/MES_holdout_v2 | 5,790,645 | 13 | 1 | 0 | 13 | 0 | 664 | 2026-09-23 16:52 | 2026-09-23 16:55 |
| data/sealed/MCL_holdout_v2 | 5,089,875 | 13 | 1 | 0 | 13 | 0 | 664 | 2026-09-27 18:19 | 2026-09-27 18:20 |
| data/sealed/MGC_holdout_v2 | 5,849,414 | 13 | 1 | 0 | 13 | 0 | 664 | 2026-09-27 18:41 | 2026-09-27 18:43 |
| data/sealed/MHG_holdout_v2 | 3,912,600 | 13 | 1 | 0 | 13 | 0 | 664 | 2026-09-27 18:47 | 2026-09-27 18:49 |
| data/sealed/NG_holdout_v2 | 4,525,274 | 13 | 1 | 0 | 13 | 0 | 664 | 2026-09-27 18:30 | 2026-09-27 18:31 |

Directory modes: 775 everywhere. Grand total of the five top-level sources (vendor, processed,
processed_step2, processed_hist, sealed): **10,150,973,664 bytes, 8,920 files, 247 directories**.
The 119 files over 20 MB inside data/ hold 7,117,921,223 bytes; the largest is a 347,584,849-byte
mbp-1 file under data/vendor/databento/GLBX.MDP3/mbp-1/MNQ_v_0/. mbp-1 symbol dirs by size: MNQ
2.09 GB, NQ 0.97 GB, MYM 0.40 GB, MGC 0.37 GB.

Layout notes (names and metadata only):
- GLBX.MDP3: every file is `*.dbn.zst` at depth 3 (`<schema>/<SYM>_v_0/range=....dbn.zst`). There are
  no index, manifest or sidecar files inside GLBX.MDP3. mbp-1 has 45 roots; ohlcv-1m has 46 (the
  same 45 plus MES_v_0).
- condition: 4 JSON files (`GLBX.MDP3_<start>_<end>.json`); the one in mode 664 is
  `GLBX.MDP3_2025-04-01_2026-09-16.json`. Bar-build reports record this path repo-relatively, for
  example reports/hist/bars_NQ_ext2010.json has `condition_file:
  data/vendor/databento/condition/GLBX.MDP3_2010-06-06_2019-05-01.json`.
- rolls: 93 `.json` and 97 `.jsonl` files. The 4 files in mode 664 are the MES `_v_0`/`_c_0` rolls
  for 2019-04-01_2024-03-01 and 2025-04-01_2026-09-16.
- release_pages: 14 subdirs (eia 78 MB/1,578 files, usda 19.5 MB/975, e4 15 MB/396, bls, fed, e5,
  e4c, e4b, ism, commodity_scripts, treasury, api, named_scripts, macro_scripts) plus 3 top-level
  manifests (commodity_manifest.jsonl 503,416 B, named_manifest.jsonl 149,009 B,
  macro_manifest.jsonl 40,437 B). All are ignored and none is tracked. These are saved third-party
  web pages, not exchange market data, but they live under data/vendor and are in the move scope.
- index_history: daily index-level files (Nikkei, VXN, STOXX) and their Wayback copies, plus two
  manifest.jsonl files. It mixes tracked and ignored files (see section 3).
- data/processed: 46 product dirs, 1 parquet each at depth 2. NG also has `NG/superseded/` holding
  one research parquet and one file ending `.parquet.outright-pattern-bug`; these are the 2 files at
  depth 3. There are no manifest files at the top level.
- data/processed_step2: 31 product dirs, 1 parquet each; no top-level files.
- data/processed_hist: `ext2010/` (6 roots, 224,596,181 B) and `ext2010h/` (11 roots, 239,461,358 B),
  one parquet per root; no top-level files.
- data/sealed: 69 `range=*.dbn.zst.sealed` files plus `MES_holdout_v1/holdout_bars.sealed`. Each
  store is `<store>/raw/` (MES_holdout_v1 also has the bars blob at its root).
- Read-only modes: 4,456 vendor files and all 97 processed* parquets are mode 444. A move must
  preserve modes (rsync -a / cp -a). Neither the sealed blobs (664) nor the 444 files carry
  immutable flags, so a privileged process is not needed.

## 2. Market data and data-like files outside data/

Search scope: the whole repo minus .venv, .git and node_modules, with the five data dirs pruned.
Extensions searched: dbn, dbn.zst, zst, parquet, feather, arrow, npz, npy, h5/hdf5, pkl/pickle,
joblib, sealed. Also searched: CSV/TSV, directory names containing cache/bars/tick/store, files
over 20 MB, and file names containing bars/tick/ohlcv/mbp/store. There are **no dbn, zst, sealed,
feather, arrow, h5 or pkl files anywhere outside data/**, and **no bar or tick CSVs outside data/**.

| Path | Size / count | What it is (classification) | Git |
|---|---|---|---|
| reports/stage_e2a_funnel/**/*.npy | 43,094,016 B, 672 files | Run output (E.2a null/sample arrays per root). Not market data. | tracked (672) |
| reports/stage_e19_runs/*.npz | 100,543,276 B, 336 files | Run output (bootstrap results). Not market data. | ignored (.gitignore:30 `reports/stage_e19_runs/*.npz`) |
| reports/stage_e19_verify/er_returns.npz | 130,905 B | Run output (verifier returns). | ignored (.gitignore:31) |
| reports/stage_e22_microbook/cache/{ROOT}.parquet + .json | 725,494 B, 14 parquet + 14 json | **Derived market data cache**: per microbook/data.py docstring, one small daily-mark frame per root (price, chained dp, roll legs) reduced from the E.21 price paths and rebuilt from bars when absent. Run output, but it is the one derived price cache outside data/. | **untracked, not ignored** |
| reports/stage_e22_microbook/books/*.npz, *.npy | 19.6 MB npz (42) + 18.1 MB npy (5) | Run output (book scalars, correlation matrices). | **untracked, not ignored** |
| reports/stage_e12_briefs/gate0verifier/ (3 npy, 1 parquet, 8 csv) | 1.6 MB npy, 716,432 B parquet | Verifier run output (OOF predictions, trades). | tracked (4 array files) |
| reports/stage_d1e_gate_extension_samples.npz, reports/power_gate_samples.npz | 3,095,629 B, 2,440,198 B | Run output (gate samples). | tracked |
| reports/stage_e17_runs/H1_units.jsonl, H4_units.jsonl | 31,424,928 B, 29,873,016 B | Run output (the only non-data files > 20 MB in the repo). | tracked (stage_e17_runs: 16/16) |
| ledger/databento_spend.jsonl | 20,762,985 B | Spend ledger. Not market data, never moves. | tracked |
| reports/hist/bars_*.json (34), reports/step2/bars_*.json (62), reports/stage_e2a_bars.json, reports/stage_e12_phase1_bars.json | 0.1 to 1.1 MB each | Bar-build **reports** (JSON metadata whose keys include store, condition_file, harness_sha256), not bars. They hold data paths (Sweep C). | tracked |
| reports/stage_e14_briefs/gex/DIX.csv + pages/gex/wayback/DIX_*.csv (8) | ~0.2 MB each | Third-party daily index data set (SqueezeMetrics DIX/GEX), kept on disk only by the E.14 rule. Daily, not exchange bars; outside the move scope unless the lead decides otherwise. | ignored (.gitignore:25-27) |
| reports/stage_e20_search/config_daily.csv, path_daily*.csv | 0.83 MB, 0.11 MB x2 | Run output (search P&L paths). | see Sweep C if referenced |
| reports/stage_e12_briefs/margin_pages/wb_*_outright_*.csv (10 csv) | up to 0.7 MB | Saved margin pages (research evidence). | **untracked** (directory shows `??` in git status) |
| reports/stage_e14_briefs/pages/cme_holiday/extracted/** (~130 csv) | small | Extracted CME holiday calendars (research evidence). | per git status |
| reports/stage_e23_briefs/tmp_bookcoder/pycache | 32,513,635 B, 1,232 files | Bytecode cache, not data. | ignored |
| .pytest_cache, .ruff_cache | 0.69 MB, 0.06 MB | Tool caches. | ignored |
| balt_full.json (repo root) | 18,408 B, mode 664, mtime 2026-10-18 01:44:37 PDT, 1 link | **Not market data.** The first 300 bytes show an OpenAlex work record (W3106590193, doi 10.1016/j.jfineco.2021.04.029, "Hedging demand and market intraday momentum", 2021): literature metadata, apparently a stray research fetch. | **untracked, not ignored** |
| ni_full.json (repo root) | 16,984 B, mode 664, mtime 2026-10-18 01:44:35 PDT, 1 link | **Not market data.** OpenAlex work record W3122647810 (doi 10.1093/rfs/hhaa082, "Does Option Trading Have a Pervasive Impact on Underlying Stock Prices?"). | **untracked, not ignored** |

There are no other symlinks anywhere in the repo outside .venv/.git (`find -type l`: 0).

### .claude/worktrees (1,395,139,511 B total, not ignored, shows as `?? .claude/worktrees/`)

`git worktree list` shows 5 linked worktrees: 3 under .claude/worktrees/ and 2 siblings outside the
repo.

| Worktree | bytes | files | branch / HEAD | market data? |
|---|---:|---:|---|---|
| .claude/worktrees/agent-a87e3dc1a4f58c0e5 | 393,016,203 | 4,358 | worktree-agent-a87e3dc1a4f58c0e5 @ 5c4a1cd (2026-10-05) | No data copies. data/ holds only calendars/ and vendor/index_history/ (the 11 tracked files, 1,072,327 B, checked out by git). No processed*, no sealed, no databento, no symlinks. The npy/npz/parquet inside are checked-out copies of tracked reports files (e2a_funnel, gate0verifier, the two top-level npz). |
| .claude/worktrees/agent-a94b80ceda0f5c25b | 407,468,769 | 4,645 | worktree-agent-a94b80ceda0f5c25b @ e577d55 (2026-10-05) | Same as above. Its 4 symlinks are all inside its own .venv (lib64 -> lib; bin/python -> uv cpython 3.12). None points at data. |
| .claude/worktrees/agent-aeca900d4301d6fb8 | 594,654,539 | 6,948 | worktree-agent-aeca900d4301d6fb8 @ 71d667f, **locked** ("claude agent agent-aeca900d4301d6fb8 (pid 129448 ...)"), created 2026-10-21 02:14 PDT | Same: only the 11 tracked index_history files and tracked reports outputs; it also holds tracked copies of stage_e17_runs/H1,H4_units.jsonl. **Live**: pid 129448 is a running `claude --model opus --effort xhigh` session (cwd = repo root, tmux session stage-e26). |
| /home/kiros-li/Documents/GitHub/PropExperiment-e12-v8 (outside repo) | 286,269,924 | | e12-v8 @ 8b93e98 | Only data/vendor/index_history; no data dirs, no symlinks (maxdepth 4, outside .venv). |
| /home/kiros-li/Documents/GitHub/PropExperiment-e12-v9 (outside repo) | 294,093,073 | | detached @ deccd17 | Same. |

Consequence: no worktree holds a copy of, or a symlink to, vendor/processed/sealed data. Code run
inside a worktree with REPO_ROOT set to the worktree would find no data dirs at all. Whether any
worktree code reaches the main repo's data through an absolute path is a code question (Sweep B
excludes .claude/worktrees, so the merge should note this as uncovered).

## 3. Directories that mix tracked files with ignored data

Only two directories in the move scope mix tracked and ignored content:

1. **data/vendor/** (11 tracked, 8,742 ignored), through its child index_history.
2. **data/vendor/index_history/** (11 tracked, 18 ignored). The exact tracked paths
   (`git ls-files -s`, all mode 100644, and `git status` shows them clean):
   - data/vendor/index_history/manifest.jsonl
   - data/vendor/index_history/nikkei_stock_average_daily_en.csv
   - data/vendor/index_history/nikkei_wayback/wb_20200919105418_nikkei_daily_en.csv
   - data/vendor/index_history/nikkei_wayback/wb_20230523124334_nikkei_daily_en.csv
   - data/vendor/index_history/nikkei_wayback/wb_20240401064221_nikkei_daily_en.csv
   - data/vendor/index_history/vxn/VXN_History.csv
   - data/vendor/index_history/vxn/fred_VXNCLS.csv
   - data/vendor/index_history/vxn/manifest.jsonl
   - data/vendor/index_history/vxn/wayback/VXN_History_wb_20220714220323.csv
   - data/vendor/index_history/vxn/wayback/VXN_History_wb_20221230140502.csv
   - data/vendor/index_history/vxn/wayback/VXN_History_wb_20240419091234.csv

   The ignored files are data/vendor/index_history/stoxx_h_3msx5e.txt and the 17 files in
   data/vendor/index_history/stoxx_wayback/. By subdirectory: nikkei_wayback/ and vxn/ (with
   vxn/wayback/) are fully tracked; stoxx_wayback/ is fully ignored; the index_history root mixes the
   two tracked files (manifest.jsonl, nikkei csv) with the ignored stoxx_h_3msx5e.txt. Every one of
   these files matches `.gitignore:17 data/vendor/`. The tracked ones were force-added.

All other units have 0 tracked files: data/vendor/databento (and its 4 children),
data/vendor/release_pages, data/processed, data/processed_step2, data/processed_hist, data/sealed and
its 6 stores. data/ itself mixes tracked Python code and data/calendars with the data dirs, so
data/ as a whole can never be one symlink.

Git behaviour, demonstrated in a throwaway repo in the scratchpad
(/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/2819cf4f-44df-4b3e-b6eb-b8d43e270f7a/scratchpad/gitdemo,
git 2.x, with the same `data/processed/` and `data/vendor/` ignore lines):
- A symlink at **data/processed** (top-level ignored dir): `git status` shows `?? data/processed`.
  The trailing-slash pattern does not match a symlink, so each top-level symlink appears as
  untracked unless the lead adds a no-slash pattern (e.g. `/data/processed`).
- A symlink at **data/vendor**, which holds a tracked file: `git status` shows
  ` D data/vendor/index_history/m.jsonl` plus `?? data/vendor`, and
  `git add data/vendor/index_history/...` fails with
  `fatal: pathspec ... is beyond a symbolic link`. A whole-directory symlink of data/vendor (or of
  data/vendor/index_history) would therefore show the 11 tracked files as deleted.
- A symlink at **data/vendor/databento**, a child of the real, ignored directory data/vendor/:
  `git status` stays clean, because the parent pattern `data/vendor/` still matches the real
  directory and ignores everything below it, symlinks included. The same holds for symlinks at
  data/vendor/release_pages and data/sealed/<store>, inside real ignored parents.

Granularity this implies (for the merge to confirm against B and C): data/vendor/databento and
data/vendor/release_pages can each be one sub-directory symlink with git clean. index_history must
stay a real directory (1.1 MB; moving its 18 ignored stoxx files is optional, per file or as
stoxx_wayback/). The top-level dirs processed, processed_step2, processed_hist and sealed have no
tracked files and can each be a whole-directory symlink, but each would then appear as `??` unless
.gitignore gains slash-less entries. A symlink one level down (per product or store, inside a real
ignored dir) keeps git clean with no .gitignore change.

## 4. Open handles

At 2026-10-21 02:16:58 PDT, `lsof +D` on each of the five data dirs (absolute paths) returned no
holder (rc=1 for all five). A full `lsof | grep PropExperiment/data/(vendor|processed|sealed)`
found 0 handles then and again at 02:18:25 PDT. Caveat: lsof ran as uid 1000 without root, so it
sees only this user's processes. Every project process is this user's.

Processes with cwd in the repo at 02:17: tmux session `stage-e26` and its bash shells; two `claude`
sessions (pid 129448 and 129449, both `--model opus --effort xhigh`, presumably this E.26 lead and
the parallel E.28 session), each with an auto-retry monitor; MCP helper processes (context7,
playwright, chrome-devtools). No python or `uv run` job was running (the only python processes are
the system networkd-dispatcher and unattended-upgrades). No AiTrader collector was running: neither
`systemctl --user list-timers --all` nor the system timers list a news-collect timer (only
motd-news and sysstat-collect). The collector window (about 15:30 to 16:00 PT) is far from the
current time. The handle check is a point-in-time snapshot; E.28 could open data later, so the lead
should repeat it immediately before the move.

## 5. Target filesystem /mnt/large-storage

- Device /dev/nvme1n1p2, ext4, mounted rw,relatime (st_dev 66310, unlike the repo's 64513, so a
  move between them is a cross-filesystem copy, and rename() would raise EXDEV).
- Size 1,005,867,986,944 B; used 129,606,852,608 B (14%); **available 825,090,363,392 B (~768 GiB)**,
  about 81 times the 10.15 GB to move. Inodes: 62,303,952 free (8,920 files and 247 dirs needed).
- Persisted in /etc/fstab line 15: `UUID=14b9488c-... /mnt/large-storage ext4 defaults,nofail 0 2`.
  systemd unit mnt-large\x2dstorage.mount is active. **`nofail` matters**: if that disk fails to
  mount at boot, the system still boots, and every symlink into /mnt/large-storage dangles with no
  error until code opens a path.
- /mnt/large-storage is mode 700, owner kiros-li:kiros-li, so only this user can traverse it. That
  is fine for the project and is consistent with the sealed data.
- **/mnt/large-storage/market_data does not exist.** Top-level entries: Archive (40.1 GB), Games
  (88.5 GB), Installers (0.6 GB), README.md, lost+found, .Trash-1000. Nothing was written.
- Observation: the mtime and ctime of /mnt/large-storage changed at **2026-10-21 02:16:16.685 PDT**,
  so an entry was created and removed at its top level then, leaving no residue. This worker wrote
  nothing there (its only access was `test -w` at about 02:17, which does not modify). Another
  process (a parallel worker's write probe, or the parallel session) touched it. The lead may want
  to identify which.

## 6. Uncertainties and gaps

- lsof without root sees only uid 1000's processes (all project processes run as that user).
- The /mnt/large-storage 02:16:16 modification is unexplained (see section 5).
- Classifying the e22 microbook cache as derived price data rests on microbook/data.py's docstring,
  not on its contents (not read, per the boundary).
- I did not check whether code anywhere (including worktree code and the sibling worktrees) uses
  absolute paths into the main repo's data. That is Sweep B, which excludes .claude/worktrees.
- Cross-reference for Sweep C (count only): 20 JSON files under reports/ and docs/ contain the
  absolute prefix `/home/kiros-li/Documents/GitHub/PropExperiment/data/`, including
  docs/HOLDOUT_MANIFEST.json, docs/HOLDOUT2_MANIFEST.json, the 4 docs/holdout2/*_HOLDOUT2_MANIFEST.json,
  reports/stage_e18_freeze.json, reports/stage_e12_phase1_bars.json and
  reports/stage_e23_events/*__cf.json.
- No market-data file was hashed or read, so whether files are intact is not established here
  (that is the lead's T1.4).
