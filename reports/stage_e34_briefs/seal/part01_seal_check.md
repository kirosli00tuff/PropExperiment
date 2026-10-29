# Stage E.34 Part 0.1: the E.32 test seal against every ZL, ZS and ZM file (lead, Opus 5.5 max)

Done 2026-10-29 11:54:58-12:03 PDT (this file's mtime 12:03:49), before any worker was spawned or any other source was read for design. Names and
file metadata only: no data file was opened, decoded or hashed (the census reads directory listings and os.stat).

## Checks (verbatim key fields; reports/stage_e34_briefs/checks_start.txt)

```
soy_test_seal.py status: state sealed, files_expected 114, files_sealed 114, files_ok 114,
                         plaintext_in_window_present [], unclassified_files [], unlock_log_ok True,
                         unlocks_logged 0, all_ok True
guard33.py dry-check:    dry-check: 4 of 4 refused (rc=0)
data.holdout status:     top, holdout_2, MCL, MGC, MHG, NG: all_ok True, unlocks_logged 0, unlock_log_ok True
```

## Why a wider census, and what it found

soy_test_seal.py's scan (lines 164-203) sees only `GLBX.MDP3/<schema>/<dataset with a ZM/ZS/ZL token>/<file>`, the
three bar-store globs (data/processed, data/processed_step2, data/processed_hist/*) and the two E.22 caches. Files made
elsewhere after the seal (2026-10-26 22:55:11 PDT) by E.33, E.33b, E.33c and E.32b would not appear in its status.

reports/stage_e34_briefs/seal/census34.py (sha256 d5ab3832...) walked the repo (no symlink following; .git, .venv and
caches skipped), /mnt/large-storage (market_data, Archive and the rest), ~/.cache and /tmp/claude-1000. It kept every
file with a soy token (ZL, ZS, ZM, MZL, MZS, MZM, soy*) in its last four path parts, and every data-like file
(dbn, zst, parquet, npy, npz, csv, feather, arrow, pkl, h5, jsonl, gz, sealed) modified after the seal. Output:
reports/stage_e34_briefs/seal/census34.tsv (143,390 rows, sha256 8d903791...), summary census34_out.txt (rc 0, run
12:00:10-12:00:33).

| class | rows | reading |
|---|---|---|
| PROBLEM (an in-window name span, or a manifest original back in plaintext) | 0 | none |
| sealed blobs (data/sealed/SOY_test_v1) | 114 | the 114 sealed files |
| name span outside the window | 4,467 | for example E.31's first chunks `range=2020-11-30T220000Z_2020-12-31T220000Z` (Z1-Z4), which start at 16:00 CT after trade date 2020-11-30 closed (seal section 1 item 6) |
| roll symbology (data/vendor/databento/rolls/) | 16 | E.32 OC-0.4: dates to instrument ids and raw symbols, no prices or volumes; kept |
| derived records of earlier trials, listed by E.32 (derived_unsealed_files.tsv) | 24 of the 206 | E.32 OC-0.5: audit trail of registered trials; refused by the protocol's allowlist, never re-read |
| soy token, no span in the name | 679 | all judged by provenance below |
| data-like, modified after the seal, no soy token | 138,090 | 136,738 under derived/e33 (E.33, inputs held to guard33's 156 discovery files), E.33 review and scratch files, E.32b work files, CLI logs, the two ledgers |

The 679 no-span files: 223 agent-worktree report JSONs (2026-10-05..10-21), trial records and literature pages of
earlier stages (E.2a, E.8, E.10, E.20, E.22, E.23, E.28, E.29, E.31, E.32; all before the seal or E.32's own seal
files), E.32b's F3 sigma parts (window 2022-11..2023-10) and economics parts (no market data), E.33's logs and G6 probes
(named by discovery month 2020-12..2024-02), E.31's five purchase manifests, one E.33 scratch script, and three
groups outside the program (another project's crypto funding pages under /mnt/large-storage/Archive/GitHub/
NPLExperiment, named vntl_SOY and xyz_ZM; game files; a uv archive). A last pass over the full path of every row (not
only the name), excluding the sealed, roll and listed-derived classes, found 4 paths with an in-window date or
nanosecond stamp: the four E.31 first chunks above, outside the window by the seal's UTC rule. No file holding the
window's data was made after the seal: the post-seal scratch and derived data names carry dates 2020-12-30..2022-09-29
only.

## Verdict

The E.32 test seal covers every ZL, ZS and ZM data file on disk that touches 2017-05-01..2020-11-30, in every schema
the program owns (raw ohlcv-1m for ZS and ZL from 2017-04 and ZM from 2019-05; the step 2 and ext2010h bar stores; the
E.22 caches). No order-book data for the window was ever owned. No ZL file needed sealing, and none was sealed: no
guard changed, so the end-of-stage pytest rule of the prompt (2 GB rule, "if Part 0 changed a guard") is not
triggered.

Two plaintext items touch the window by content and stay as E.32 classified them, with the reason restated for the
ZL program (open choice OC-1):
- reports/stage_e20_briefs/pages/ZL/fred_PSOILUSDM.csv (12,163 bytes, untracked, sha256 d05d8678...): FRED's monthly
  IMF global soybean-oil price, not CME ZL data; E.32 section 3 kept it ("not CME data; not used by this program").
  It is monthly, so it carries nothing about 15-60 minute order-book or lead-lag structure; it is not sealed because
  the seal's fixed 114-file plan cannot be extended without changing E.32's sealed manifest, which E.33's guard reads.
  The ZL protocol's P1.2 refuses it by path, and no E.34 worker is allowed to open it.
- The 16 roll symbology files (OC-0.4): needed to map instrument ids; no prices or volumes. The protocol's data facts
  take roll dates from the discovery files' own instrument ids and definitions instead, so no E.34 worker opens them.
