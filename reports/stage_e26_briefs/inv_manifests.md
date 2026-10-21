# Stage E.26 T1.1 Sweep C: manifests and verifiers (DataInvManifests-OpusHigh)

Written 2026-10-21 02:23 PDT. Brief: reports/stage_e26_briefs/brief_inventory.md, section "Sweep C".
Read-only sweep. No market-data file was opened, read or hashed. I read only JSON/JSONL records under
reports/ and docs/, key names and path-like fields of the manifest JSONL files under data/vendor, code
(grep and line ranges), and metadata (find, ls, stat, `test -e`, git ls-files, git check-ignore).
Python in .venv: 3.12.13.

Path forms used below:
- **rel**: repo-relative (`data/...`), opened against REPO_ROOT or against the CWD. Where it is the CWD
  (noted), the command must run from the repo root. checks.sh does `cd` there itself.
- **abs**: `/home/kiros-li/Documents/GitHub/PropExperiment/data/...`.
- **store-rel**: relative to a store or sealed root.
- **name**: a bare file name relative to the manifest's own directory.

"Symlink OK" means the verifier still passes when the old path is a symlink to an intact copy on
/mnt/large-storage. It assumes the mirrored layout from the brief (each target sits at
`/mnt/large-storage/market_data/PropExperiment/<same repo-relative path>`).

## 1. Records with a verifier (these give the before and after checks)

| # | Record (tracked?) | Data it names | Path form | Verifier: exact command | How the verifier opens it | Symlink OK? |
|---|---|---|---|---|---|---|
| V1 | docs/HOLDOUT_MANIFEST.json (T) | 4 sealed MES raw chunks (`raw_files[].original_path` abs + `original_relpath` rel), `sealed_relpath` store-rel under data/sealed/MES_holdout_v1, `research.path` abs + `research.relpath` rel = data/processed/MES/ohlcv-1m_MES_v_0_2025-04-01_2026-06-19_research.parquet, holdout blob `holdout_bars.sealed` | abs + rel + store-rel | `uv run python -m data.holdout status` (data.holdout.status_report, then verify_seal(DEFAULT_PATHS)) | sealed blobs: `Path.read_bytes` sha256 (follows symlinks). research parquet: `exists()` + sha256 + `pq.read_table(columns=["trade_date"])`. Plaintext absence: `_record_paths` builds the abs and REPO_ROOT/relpath spellings, `.resolve()`s both, then calls `exists()` | Yes. Both sides resolve the same way. Silent-pass risk: H1 |
| V2 | docs/HOLDOUT2_MANIFEST.json (T) | 13 sealed MES raw chunks (abs + rel), data/sealed/MES_holdout_v2; guards the confirmation parquet data/processed/MES/ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet; unsealed-chunk check on data/vendor/databento/GLBX.MDP3/ohlcv-1m/MES_v_0/range=... and their `.partial` names | abs + rel + store-rel | same command (`holdout_2` section; data.holdout._verify_holdout2) | sealed sha256 via read_bytes. `exists()` on resolved record paths and on `.partial` siblings. Confirmation parquet: `exists()` then `pq.read_table(trade_date)` | Yes. Silent-pass risks: H1, H2 |
| V3 | docs/holdout2/{MCL,MGC,MHG,NG}_HOLDOUT2_MANIFEST.json (T), 13 records each | sealed raws under data/sealed/<R>_holdout_v2; each product's step 2 store data/processed_step2/<R>/ohlcv-1m_<R>_v_0_2019-05-06_2024-02-29_step2.parquet (rows checked) | abs + rel + store-rel | same command (`holdout_2.products`; data.step2_seal.verify_all, which globs `docs/holdout2/*_HOLDOUT2_MANIFEST.json`) | as V2. The store is read with `pq.read_table(trade_date)` | Yes. Silent-pass risks: H1, H2 |
| V4 | reports/stage_e17_run_manifest.json (T), schema stage_e16_run_manifest/1: 27 roots, 27 `step2` entries, 17 `ext2010` entries (6 under data/processed_hist/ext2010, 11 under ext2010h), 10 `ext2010` null | 44 store parquets: data/processed_step2/<R>/... and data/processed_hist/{ext2010,ext2010h}/<R>/... | rel, resolved against the **CWD** | (a) checks.sh block "E.20 store sha256": inline python, plain `open(e["path"],"rb")`, 34 stores. (b) base_rules.store.load_manifest, then `preflight` / `_checked_input`: `Path(ref.path).is_file()`, sha256 via data.stage_e_bars._check_hash, and `refuse_path`, which uses `resolve()` and is_relative_to(data/sealed resolved, PROCESSED_ROOT resolved) plus name tests. Used by the E.17 base rules, multiday (E.21), trigger_hold (E.23) and microbook (E.22) runners, not by checks.sh. (c) pattern_search.preflight.check_stores (E.20 search runner) | plain open and is_file follow symlinks. refuse_path compares two resolved paths | Yes, if the target path has no component named `sealed` or `mes` (any case) and no store root is nested inside another (see section 7) |
| V5 | reports/stage_e20_search_freeze.json (T), 117 entries, 17 of them step 2 stores | data/processed_step2/<R>/... for the 17 search roots | rel (repo_path joins REPO_ROOT) | `uv run python -m pattern_search.freeze_manifest verify --sha256 94ee86b02d1cb644c9307be958b7791587d42c062996a6220dc901d4fe5a0f2f` (pattern_search.preflight.check_freeze) | `is_file`, `st_size`, sha256 via `guarded_sha256`. The guard is `os.path.realpath` on both the candidate and the allowlist (`_real`). Listed-versus-required compares `str(p.resolve())` on both sides | Yes. Every comparison goes through realpath or resolve on both sides |
| V6 | reports/stage_e20_h6_freeze.json (T), 91 entries | data/processed_step2/NQ/ohlcv-1m_NQ_v_0_2019-05-06_2024-02-29_step2.parquet (28,880,316 bytes). Also reports/stage_e14_briefs/gex/DIX.csv (untracked, **git-ignored** by .gitignore:25), an external-data file outside data/ | rel, against the **CWD** | `PYTHONPATH=. uv run python reports/stage_e20_briefs/h6_freeze_manifest.py verify 22e606f0b74532e267a4155d93e295702ff86f6e8f4143236882f3c2f230e795` | `Path(p).is_file()` + `read_bytes()` sha256 | Yes |
| V7 | reports/stage_e18_freeze.json (T): `external[]` 6 ext2010 stores, path recorded abs; pinned to reports/stage_e17_c1_store_hashes.json (T; `stores` = {root: sha256}, no paths) | data/processed_hist/ext2010/{6E,GC,NG,NQ,ZC,ZN}/... | path recomputed by `hist_parquet_path(root,"ext2010",HIST_ROOT)`, unresolved. The recorded abs string is **not compared**; only the sha256 list is | `uv run python reports/stage_e18_briefs/freeze_manifest.py verify --expected 5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03` | `is_file()` + open/read sha256. A missing file yields sha None, so the check fails loudly | Yes. Also checks ~/.cache/propexp_e14_c1 (outside the repo, not moving) |
| V8 | data/vendor/release_pages pages, through reports/stage_e2b_release_sources_{macro,commodity,named}.json (T; `raw`/`txt`/`saved_path` rel) | ~1,370 saved release pages | rel, joined to REPO_ROOT (`_page_path` refuses absolute paths and `..`) | `uv run --no-sync python -m screening.build_release_calendar --check` (rebuilds in memory and compares byte for byte to reports/stage_e2b_release_calendar.json). **Not in checks.sh** | `read_bytes()` (follows symlinks) | Yes. A useful extra after-check for release_pages |
| V9 | strategy/members/k1/_vxn.py `VXN_SOURCE_SHA256` + tests/test_k1_members_tables.py; strategy/members/k3/_mehedge_signal.py + tests/test_e4_k3_members_m_signal.py (via reports/stage_e4c_release_check.json `index.N225.saved_path`/`sha256`) | data/vendor/index_history/vxn/VXN_History.csv; data/vendor/index_history/nikkei_stock_average_daily_en.csv + 3 nikkei_wayback CSVs (all **git-tracked**) | rel, joined to REPO | pytest only (the lead runs it; I did not) | `read_bytes()` sha256. **The K1 tests are `skipif(not is_file())`**: H3 | Yes when the target is intact; a dangling link silently skips |

Not data-bearing (they never open market data), checked so they can be ruled out:
- check_frozen.py: E.1 and E.2a freezes, the E.2a tables.
- harness_freeze verify. It walks data/ with rglob but skips DATA_SUBDIRS by prefix. In Python 3.12 rglob does
  not descend into a directory symlink, and the symlink entry itself matches a DATA_SUBDIRS prefix, so the
  output does not change. The walk only gets faster.
- cluster freezes K1..K8 (files under strategy/ only).
- the v2 freeze (ml_route_v2, docs, reports, tests).
- E.14 C1 freeze inputs (43 entries; under data/ only data/calendars/hist2010/*.json, which never move).
- E.16 freeze. Its writer refuses data/processed*, data/vendor and data/sealed, and its globs hold none.
- E.21 and E.23 freezes. Their files and input roles are code and reports/ JSON only.
- E22-F1 sha256 list (forward/, tests/, reports/).
- trial_registry and the ledgers.
- reports/stage_e24_f2_files.sha256 does not exist, so checks.sh skips it.
- The verify step of every freeze above reads no store.

## 2. Records that name data paths but have no verifier (provenance only)

From a scan of reports/**.json, docs/**.json and *.sha256/*.txt (212 files match a data-path pattern;
208 tracked, 4 untracked under reports/stage_e25_briefs/pages). Re-verifying any of these is not
needed. They only matter if something regenerates them and compares strings.

| Family | Files | Path form | Notes |
|---|---|---|---|
| reports/step2/purchase_<R>.json, bars_<R>.json | 31 + 31 | rel | `files[].path`/`input_files[].path` (vendor raws), `rolls.rolls_file`, `degraded.condition_file`, `parquet.path` (data/processed_step2). Read by data.step2_store.input_files (REPO_ROOT join) only on a rebuild |
| reports/hist/purchase_<R>_ext2010{,h}.json, bars_... | 17 + 17 | rel | same plus `metadata_files.{condition,symbology}.path`. Read by data.hist_store on a rebuild |
| reports/stage_e1_purchase.json | 1 (904 file records) | rel | vendor raws with sha256 |
| reports/stage_e2a_bars.json | 1 (675 inputs, 45 parquets, 45 rolls, 45 condition) | rel | E.2a research stores data/processed/<R>. The research sha256 the loaders check comes from reports/stage_e2a_vehicle_sizes.json via screening.stage_e_frozen (sha only, no path) |
| reports/stage_e12_phase1_bars.json | 1 | **abs** (28 `store_path` data/processed_step2, 28 `research_path` data/processed) | pattern_search reads only `roots.*.s_x`/`store_sha256` from it, never the paths |
| reports/stage_d1f_confirmation_build{,_step4b_failed}.json | 2 | **abs** (`inputs.rolls/condition/symbology` in data/vendor) | provenance |
| reports/stage_e14_c1_result.json, stage_e18_c1b_result.json, stage_e18_verify/{compare,recompute}.json | 4 | rel (`inputs.stores.*.path`) and **abs** (`world.roots.*.path`, compare rows) | provenance. A re-run would record /mnt paths in `inputs.stores` (H4) |
| reports/stage_e14_c1_RUN_ONCE.json, stage_e18_c1b_RUN_ONCE.json, stage_e17_c1_verify/hashes.json | 3 | rel | 6 ext2010 stores each |
| reports/stage_e20_H6_RUN_ONCE.json, stage_e20_H6_result.json | 2 | rel | NQ step 2 store |
| reports/stage_e23_events/*.json and *.meta.json | 20 | rel | `inputs.store:*`/`store_checked:*`. These files are hashed as bytes by the E.23 freeze; their contents are never re-checked against disk |
| reports/stage_e_start_rule_K{3,4,5,6,8}.json | 5 | rel | `inputs[].path`. Written through screening.stage_e_start_dates._display (resolve + relative_to, falling back to the unresolved string) |
| reports/stage_e22_mes_closure_rulings.json | 1 | rel | `store.path` data/processed/MES. The file is pinned by sha; the path is never re-checked |
| reports/tick_crosscheck_summary.json | 1 | abs (4) | provenance |
| quote, release-check and inventory JSONs (stage_d1e/e0/e12/e14/e15/e17 quotes, stage_e2b/e3..e9 release checks, stage_e2a_costs/vehicles/sizes, stage_e11 member_inventory, stage_e23 inventory K*.json, stage_e20 product_*.json, stage_e25 R3, stage_e24 loader/replay_compare) | ~45 | rel or in-text | provenance. The E.2a tables are byte-hashed by check_frozen and stage_e_frozen, whose content is unchanged by a move |
| reports/stage_e7_briefs/k1_files_pre_audit.sha256, audit_k1/auditor_sha256_at_start.txt | 2 | rel (sha256sum format) | each lists data/vendor/index_history/vxn/VXN_History.csv (tracked). Historical audit snapshots, not in checks.sh |
| ledger/*.jsonl | 3 files, 36,684 lines | none | **0 lines record any data path** (databento_spend 36,402, ml_v2_config 273, trial_registrations 9). data/config.py EXTERNAL_LEDGER_PATHS already reads /mnt/large-storage/Archive/GitHub/MLCryptoEngine/data/vendor/spend_ledger.jsonl, so the checks already depend on that mount |

## 3. Manifests and index files inside the data directories (names and sizes; keys and path fields only)

- data/processed, data/processed_step2, data/processed_hist, data/sealed: **no JSON, JSONL, manifest or index
  file**. They hold 48 + 31 + 17 parquet and 70 `.sealed` files (69 raw chunks + 1 holdout_bars.sealed).
  There is one odd file: data/processed/NG/superseded/ohlcv-1m_NG_v_0_2025-04-01_2026-06-19_research.parquet.outright-pattern-bug
  (921,327 B; the superseded NG build named in stage_e2a_bars.json notes).
- data/vendor/databento: 98 json + 97 jsonl. These are vendor metadata (condition/GLBX.MDP3_*.json ×4,
  rolls/<R>_v_0_*.jsonl and *_symbology.json, symbology/), not manifests. Only their names were listed.
- Manifest JSONL in data/vendor (none records an absolute path):

| File | Bytes | Lines | Keys | Path field form |
|---|---|---|---|---|
| data/vendor/release_pages/commodity_manifest.jsonl | 503,416 | 977 | bytes, fetched_pdt, fetched_url, raw, tried, txt, url, via | `raw`/`txt` rel (data/vendor/release_pages/...) |
| data/vendor/release_pages/named_manifest.jsonl | 149,009 | 312 | same | rel |
| data/vendor/release_pages/macro_manifest.jsonl | 40,437 | 83 | same | rel |
| data/vendor/release_pages/e4/manifest.jsonl | 114,383 | 187 | effective_url, fetched_pdt, note, saved_path, sha256, url | `saved_path` rel |
| data/vendor/release_pages/e5/manifest.jsonl | 99,236 | 297 | effective_capture, fetched_pdt, saved_path, sha256, url | `saved_path` rel |
| data/vendor/release_pages/e4b/manifest.jsonl | 9,498 | 24 | fetched_pdt, file, note, sha256, url_requested, url_served | `file` name |
| data/vendor/release_pages/e4c/manifest.jsonl | 12,956 | 29 | bytes, fetched_pdt, file, http, note, sha256, url_requested, url_served | `file` name |
| data/vendor/index_history/manifest.jsonl (**tracked**) | 14,632 | 29 | bytes, fetched_pdt, file, http, note, sha256, url_requested, url_served | `file` name |
| data/vendor/index_history/vxn/manifest.jsonl (**tracked**) | 4,458 | 7 | adds fetched_utc, http_status, last_modified | `file` rel (5) |

- **Code inside a data directory**: data/vendor/release_pages/{commodity,macro,named}_scripts/*.py, 28 files.
  Several hard-code `REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")`. The three `verify.py`
  scripts **rewrite** reports/stage_e2b_release_sources_*.json, so never use them as after-checks.
  named_scripts/build.py derives "fetched" times from `st_mtime`, so a copy that does not keep mtimes would
  change any rebuild. harness_freeze does not freeze these scripts (they sit under data/vendor). They move
  with release_pages and are untracked or ignored there; Sweep A has the git status.
- Name-based manifest fields do not all resolve at `<manifest dir>/<file>`. From my join of 4,461 vendor and
  processed files against all recorded hashes: 19 index_history names and 12 e4c names are not found there
  (the files sit in sub-folders or are absent), and 3 index_history names carry two different sha256 values
  (re-fetches). This predates the move. Use existence and sha comparisons of these manifests only
  before-versus-after, not against the recorded value.

## 4. checks.sh commands that read data through these paths (reports/stage_e26_briefs/checks.sh)

checks.sh runs from the repo root (line 6).

| checks.sh line | Command | Data paths it exercises |
|---|---|---|
| 13-22 | `uv run python -m data.holdout status` | data/sealed/* (all 70 blobs hashed); data/processed/MES research + confirmation parquets (sha256 and trade_date column); data/processed_step2/{MCL,MGC,MHG,NG} stores (trade_date column); existence of the 69 sealed-raw original paths and their `.partial` names under data/vendor/databento/GLBX.MDP3/ohlcv-1m/{MES,MCL,MGC,MHG,NG}_v_0/ |
| 26-27 | `screening.harness_freeze verify` | walks data/ but skips every data subdir; reads no data |
| 86-102 | E.20 store sha256 block (inline python) | 34 stores: data/processed_step2/<17 roots> + data/processed_hist/{ext2010,ext2010h}/<17 roots>, plain open, CWD-relative |
| 103-104 | E.20 H6 freeze verify | data/processed_step2/NQ store (plus reports/.../DIX.csv) |
| 105-106 | pattern_search.freeze_manifest verify | the 17 step 2 search stores (data/processed_step2), through realpath |
| 79-81 | E.18 C1b freeze verify | 6 data/processed_hist/ext2010 stores (plus ~/.cache) |
| all others | E.16, E.21, E.23, v2, cluster, E.14 C1 inputs, E22-F1, check_frozen, ledger, trial registry | no market data |

None of checks.sh touches data/vendor/databento/GLBX.MDP3 raw contents, rolls, condition, symbology,
release_pages, index_history, data/processed/<R> other than MES, or data/processed/NG/superseded.

## 5. Recommended before and after commands

Run every command from the repo root, before the move and again after it. Compare full outputs, not just
exit codes.

1. `bash reports/stage_e26_briefs/checks.sh <harness sha256>` (as now). In the holdout block, also compare
   these fields (H1, H2), not only `all_ok`:
   `uv run python -m data.holdout status | python3 -c 'import json,sys;d=json.load(sys.stdin);h=d["holdout_2"];print(d["all_ok"],d["research_parquet_ok"],d["research_has_no_holdout_rows"],h["confirmation_has_no_holdout2_rows"],h["unsealed_plaintext_present"],{r:(p["all_ok"],p["store_has_no_embargo_or_holdout2_rows"],p["unsealed_plaintext_present"]) for r,p in h["products"].items()})'`
   Before the move, expect True for every flag and `[]` for every list. After the move they must be the
   same, with **True, not None**.
2. Release pages (not covered by checks.sh): `uv run --no-sync python -m screening.build_release_calendar --check`.
3. Symlink-resolution guard, to run before trusting any existence-based pass: for each moved path P,
   `test -e P && test "$(readlink -f P)" = /mnt/large-storage/market_data/PropExperiment/P`. Also
   `test -d data/vendor/databento/GLBX.MDP3/ohlcv-1m/MES_v_0`, so the holdout plaintext-absence
   checks are not vacuous.
4. Recorded-hash index (for T1.4, the lead's hashing). I wrote a JSON-only collector:
   `python3 -I /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/2819cf4f-44df-4b3e-b6eb-b8d43e270f7a/scratchpad/recorded_hashes.py "$PWD" <out.json>`.
   It opens no data file. Its output, already written to
   /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/2819cf4f-44df-4b3e-b6eb-b8d43e270f7a/scratchpad/recorded_hashes.json,
   covers 5,007 data paths with a recorded sha256: 4,263 GLBX.MDP3 raws, 18 rolls, 3 condition, 1 symbology,
   45 data/processed/<R> research stores, 2 data/processed/MES files, all 31 step 2 stores, all 17 hist
   stores, and 579 release-page and 48 index_history entries (mostly from the in-dir manifests). Across the reports/docs
   records, no path carries conflicting sha256 values. 69 recorded paths are absent, and all 69 are the
   sealed holdout raws (expected). 247 data files on disk have no recorded hash: 172 rolls, 72 GLBX
   raws, 1 MES file, 1 NG file and 1 condition file. The lead's T1.4 hash covers those.
5. pytest (lead, separately): compare the **skip count** before and after, not only pass/fail (H3).

## 6. Hazards from manifests and verifiers (for the merge's hazard list)

| ID | Hazard | Where | Severity | Avoided by |
|---|---|---|---|---|
| H1 | The plaintext-absence checks (`plaintext_absent`, `unsealed_plaintext_present`) are `exists()` tests. If the data/vendor link is dangling (mount absent, wrong target), they pass vacuously and the seal reads as intact | data/holdout.py `_record_paths`, verify_seal, _verify_holdout2; data/step2_seal.py verify | CHANGES BEHAVIOUR (silent pass) | after-check 3 (link resolves) before trusting status |
| H2 | `confirmation_has_no_holdout2_rows` and per-product `store_has_no_embargo_or_holdout2_rows` return **None** when the parquet is missing, and `all_ok` accepts None (`is not False`). So holdout 2 and the four product seals stay `all_ok: True` if data/processed or data/processed_step2 is unreachable. Holdout 1's `research_parquet_ok` would catch data/processed but not processed_step2 | data/holdout.py `_confirmation_clean`, lines 723-770; data/step2_seal.py 203-212 | CHANGES BEHAVIOUR (silent pass) | compare the field values (after-check 1), not only all_ok |
| H3 | K1 VXN tests are `skipif(not (REPO/VXN_FILE).is_file())`. A dangling link turns a hash check into a skip. tests/test_build_release_calendar.py gates on `is_dir()` of release_pages in the same way | tests/test_k1_members_tables.py:52-53, 89; tests/test_build_release_calendar.py:29 | CHANGES BEHAVIOUR (silent skip) | compare pytest skip counts; index_history is tracked and should stay in place anyway |
| H4 | Path recorders that `resolve()` and then `relative_to(REPO_ROOT)` will write `/mnt/large-storage/...` absolute paths (or None) into any **new** record. Existing records are unaffected, and every verifier above compares by resolve/realpath on both sides or by sha only, so verification still passes. Affected: pattern_search.preflight.rel (a rebuilt search freeze would list /mnt paths); base_rules.guards.rel; c1_replication.evaluate._rel (`inputs.stores.*.path`); data.holdout._relpath_in_repo (a future seal would record `original_relpath: null`); screening.stage_e_start_dates._display | as listed | CHANGES BEHAVIOUR (new records only) | no rebuilds of freezes or seals planned; note it for any future seal or freeze |
| H5 | Several verifiers resolve manifest paths against the **CWD**, not REPO_ROOT: the E.20 store block, h6_freeze_manifest.py, base_rules.store StoreRef (from stage_e17_run_manifest.json), trigger_hold EB.RUN_MANIFEST_PATH | as listed | SAFE when run from the repo root (checks.sh cds there) | run the after-checks from the repo root |
| H6 | `ml_route.store.assert_store_root` rglobs from the resolved step 2 root and refuses any entry that is not `<R>/<file>`. A **per-product-directory** symlink (data/processed_step2/NQ -> ...) appears as a one-part symlink and is refused. A whole-directory symlink of data/processed_step2, or per-file links, pass | ml_route/store.py:59-82 | BREAKS at the sub-directory granularity | symlink data/processed_step2 as a whole (cross-reference for Sweep B) |
| H7 | base_rules.store.refuse_path refuses a resolved store path with any component equal to `sealed` or `mes` (case-insensitive), or one lying under resolved PROCESSED_ROOT. ml_route refuses a step 2 root inside or containing PROCESSED_ROOT | base_rules/store.py:68-87; ml_route/store.py:59-64 | BREAKS if the target layout nests one store root inside another or names a directory `sealed`/`MES` above the stores | the mirrored sibling layout from the brief is safe: /mnt/large-storage/market_data/PropExperiment/data/{processed,processed_step2,processed_hist} are siblings |
| H8 | The holdout seal and step2_seal write the manifest with tmp + `os.link` + `os.replace` in docs/, and the adapter downloads `.partial` then `os.link`s it in the same vendor directory. Both stay on one filesystem whatever the granularity, as long as `.partial` and its target share a directory | data/holdout.py:578-592; data/adapter.py:122 | SAFE | — |
| H9 | named_scripts/build.py takes "fetched" from `st_mtime`. A copy that does not keep mtimes changes any rebuild of named_manifest-derived records | data/vendor/release_pages/named_scripts/build.py:231 | CHANGES BEHAVIOUR (rebuild only) | copy with mtimes kept (rsync -a / cp -a) |
| H10 | screening/runner.py caches the confirmation frame keyed by (resolved path, mtime_ns, size). After the move the key changes, which only costs a cache miss in-process | screening/runner.py:169 | SAFE | — |

## 7. Constraints these records put on the move

- Keep every stored path string valid. All existing records are either rel (`data/...`) or abs under
  /home/kiros-li/Documents/GitHub/PropExperiment/data/.... Both stay valid only if a symlink exists at
  each old path. Never symlink `data/` itself: data/config.py computes REPO_ROOT from
  `Path(__file__).resolve().parents[1]`, and data/ holds the code.
- Keep the target names as a mirror (`.../PropExperiment/data/processed_step2/...` and so on). No
  `sealed` or `MES` directory above the stores, and no store root nested inside another (H6, H7).
- The holdout guards resolve paths, so the 69 sealed-raw originals keep resolving consistently through
  a symlinked data/vendor. `is_sealed_raw` and step2_store.refuse_inputs stay correct while the link
  exists.
- index_history (11 tracked files incl. manifest.jsonl, vxn/manifest.jsonl, VXN_History.csv, the Nikkei
  CSVs) holds hash-pinned inputs of the K1 and K3 member code and tests. Leaving it in place avoids H3
  and keeps git clean.
- The external DIX.csv (reports/stage_e14_briefs/gex/DIX.csv, git-ignored) is frozen by the H6 freeze
  at its reports/ path. The microbook cache (reports/stage_e22_microbook/cache/, 14 parquet + 14 json,
  725,494 B, untracked and not ignored; its json `stores` records hold sha256 only, no paths) also sits
  outside data/. Sweep A decides whether either counts as market data. Moving DIX.csv would need a symlink
  for the H6 verify to pass.

## 8. Unfinished and uncertain

- I traced only the verifiers above. I did not trace every runner that consumes a manifest (for example
  each multiday, trigger_hold or ml_route_v2 loader); Sweep B covers code paths. H6 and H7 are
  cross-references, found while reading the store verifiers.
- I did not run any verifier (the boundary is read-only, and the holdout status and freeze verifies hash
  data). The "Symlink OK" calls come from reading the code, not from running the checks.
- The recorded-hash collector is heuristic: a dict with `path`/`original_relpath`/`saved_path`/`file`
  next to `sha256`/`sha256_plaintext`. Records with other key names (for example `parquet_sha256` keyed
  by root in stage_e2a_vehicle_sizes.json, or `stores` maps without paths) are not in its path index.
  This affects coverage counts only, not any verdict above.
- 4 untracked page captures under reports/stage_e25_briefs/pages mention GLBX.MDP3 in text. They are
  not records and were ignored.
