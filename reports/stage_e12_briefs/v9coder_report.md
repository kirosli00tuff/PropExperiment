# V9Coder-OpusXHigh report: harness v9, the L-3 closure-bar ruling path (Stage E.12)

Worktree: /home/kiros-li/Documents/GitHub/PropExperiment-e12-v9 (detached at deccd17, harness v8).
No commits, no Databento call, no key, no network. No real store's bar rows were read (fixtures
only). The real summaries reports/step2/bars_NQ.json and bars_6A.json were read for their
"closure_bars" key only. Times PDT, 2026-10-03.

## 1. Loader check (done first): PASS, the frozen loader does not refuse a ruled closure bar

Quick probe first (before any code change): data.stage_e_bars.book_trade_dates on the real group
calendars books all 7 held instants to exactly the trade dates the summaries show:
NQ (equity) 2020-03-30 Mon 15:29 -> 2020-03-30, 2020-03-31 Tue 15:29 -> 2020-03-31,
2020-03-31 Tue 16:59 -> 2020-04-01, 2020-04-01 Wed 15:29 -> 2020-04-01,
2020-06-30 Tue 15:29 -> 2020-06-30, 2020-06-30 Tue 16:59 -> 2020-07-01;
6A (fx) 2020-06-30 Tue 16:59 -> 2020-07-01. None unbookable, none forbidden.

Then the full check, as tests in tests/test_e2b_step2_store_v9.py (both pass):
- `test_the_loader_reads_a_v9_equity_store_with_ruled_halt_and_break_bars` (line 340): an NQ
  fixture store built end to end by `run_product` (the v9 path) under the REAL equity calendar
  (`group_of("NQ") == product("NQ").group == "equity"`, summary calendar_modules include
  data/calendars/equity.py), with ruled bars at 2020-03-30 Mon 15:29 (equity-halt minute),
  2020-03-31 Tue 16:59 and 2020-06-30 Tue 16:59 (daily-break minutes). `read_leg`,
  `load_confirmation_leg` (S_X 2019-05-06) and `read_leg_dates` all load it with no
  TradeDateUnbookable / TradeDateMismatch / HoldoutRowRefused (or any other refusal); each
  ruled bar is present once, in_scheduled_closure True, with trade_date equal to the summary's
  closure_bars trade date (2020-03-30, 2020-04-01, 2020-07-01); the loader's own re-booking of
  every row equals its label. A cut at S_X 2020-04-01 keeps the 03-31 16:59 bar (it is 04-01's)
  and drops the 03-30 15:29 bar.
- `test_the_loader_reads_a_v9_fx_store_with_a_ruled_break_bar` (line 358): the same for a 6A
  fixture store under the REAL FX calendar (data/calendars/fx.py), ruled bar 2020-06-30 Tue
  16:59 -> trade date 2020-07-01.

## 2. Changes (worktree)

`git -C /home/kiros-li/Documents/GitHub/PropExperiment-e12-v9 diff --stat`:
```
 data/step2_store.py         | 119 ++++++++++++++++++++++++++++++++++++++++----
 screening/harness_freeze.py |   1 +
 2 files changed, 110 insertions(+), 10 deletions(-)
```
Untracked (new): tests/test_e2b_step2_store_v9.py (367 lines), reports/stage_e12_closure_rulings.json.

sha256 now: data/step2_store.py 637787e0b65875e28a6fb7314c40b4f7a5525c399f7c12ea2d1e756f32d33c49;
screening/harness_freeze.py 9cb2779aec2b6177ae4bf6a7b5bfbd8c090018021e95df353d0cd0612e6136f1;
tests/test_e2b_step2_store_v9.py c6b323b78f5a2eccd4e9a6002af760dc6f76cfdae033ab07194bae7e476d6ebe;
reports/stage_e12_closure_rulings.json 155f0b2d7e27a2f99ff00cd8f8b348dbbdfa212d9fd64037d3b4b0c4f77fd5e0.

data/step2_store.py:
- :33-40 docstring item 4 (the v9 rule). :47, :50 imports hashlib, collections.Counter.
- :98-102 `CLOSURE_RULINGS_PATH = REPO_ROOT / "reports" / "stage_e12_closure_rulings.json"`,
  `CLOSURE_RULINGS_SCHEMA = "closure_rulings/1"`, `KEEP_AND_FLAG`, `RULING_ENTRY_KEYS`.
- :228, :255 `build_step2_product(..., closure_rulings: Path = CLOSURE_RULINGS_PATH)` passes it
  to `_build_window` (:285). :490, :506 `run_product(..., closure_rulings=...)` passes it through.
- :308-321 `_build_window`: after the existing hard-failure return (unchanged), the deep bars go
  to `_closure_ruling`; refusal causes -> status "refused"; deep bars not all ruled ->
  "held_for_lead" with the v8 message unchanged as cause [0] plus the reason (unlisted bars
  named, or "no closure ruling file at ..."); fully ruled -> `summary["closure_ruling"]` and on
  to `_flag` (unchanged).
- :325 `load_closure_rulings(path) -> (entries, sha256 of the bytes parsed)`: refuses (Step2StoreRefused)
  non-JSON, schema != closure_rulings/1, missing/blank "ruling" text, non-list entries, an entry
  without exactly {root, ct, trade_date, ruling} as strings, a ruling other than keep_and_flag,
  a repeated (root, ct, trade_date).
- :360 `_closure_ruling(root, deep, path)`: missing file rules nothing; the root's entries are
  matched to deep bars by (ct, trade_date) (ct exactly as `bb._ct_str` writes it). Built only if
  every deep bar is listed AND every listed entry of the root is a deep bar. Unlisted bar -> held
  (named). Listed entry with no matching deep bar (including a close-minute bar, or the right
  minute under the wrong trade date) -> refused, naming it and the file's sha256. A (ct,
  trade_date) key naming two bars (DST fall-back) -> held. Record:
  `{"path": bb._rel(path), "sha256", "bars_ruled": n, "entries": [the root's entries]}`.
- :480 `_metadata`: `closure_ruling` copied into the parquet metadata when the summary has it
  (absent otherwise, so a v9 store without deep bars carries no new key).
- Unchanged: step2_parquet_path, summary_path, the store layout, every existing guard, every
  other module (stage_e_bars.py, group_session.py, build_bars.py untouched).

screening/harness_freeze.py:257: one line appended to `FROZEN_INPUTS`:
`"reports/stage_e12_closure_rulings.json",  # harness v9: data.step2_store's closure ruling`.
Needed: the file is outside HARNESS_DIRS and the import closure, so without it the manifest
would not hash it and preflight would not check it.

reports/stage_e12_closure_rulings.json (worktree, DRAFT for the lead): written by script from
the "closure_bars" rows with close_minute false of reports/step2/bars_NQ.json (6) and
bars_6A.json (1), the exact 7 bars the brief lists, each "keep_and_flag"; the top-level
"ruling" text paraphrases the brief's user decision of 2026-10-03. The lead should read and
confirm (or rewrite) it before building the v9 manifest; `harness_freeze build` refuses while
it is missing ("listed files missing").

## 3. Tests

Command (from the worktree): `nice -n 10 /home/kiros-li/Documents/GitHub/PropExperiment/.venv/bin/python -m pytest -q -p no:cacheprovider <files>`
- tests/test_e2b_step2_store_v9.py: 22 passed (held without a ruling; held with an extra unlisted
  deep bar, named; refused for a listed bar that does not exist, two forms; refused for a listed
  entry when the build has no deep bar; refused for a malformed file; 8 malformed-file unit
  cases; built with the exact ruling: ruled bars present, in_scheduled_closure True,
  open/high/low/close/volume equal to the planted values, trade dates as the summary, other
  roots' entries ignored, "closure_ruling" with the file's sha256 in the summary, in bars_NQ.json
  and in the parquet metadata; no ruling recorded without deep bars; a close-minute bar (16:00 CT)
  builds as before and cannot be ruled; the two loader checks; the frozen-input listing; the
  drafted real ruling file parses).
- With tests/test_e2b_step2_store.py and tests/test_stage_e_loader.py: `53 passed in 8.44s`.
- Wider set (tests/test_e2b_*.py, every test importing step2_store or stage_e_bars, test_ml_v2_phase1_*,
  test_stage_e_runner/verdict/alignment/start_dates/loader, test_cross_platform_static,
  test_compute_datarules, test_harness_freeze, test_e2a_bars), 10:49-10:54 PDT:
  `1 failed, 632 passed, 2 skipped, 1 warning in 285.10s`. The failure is
  `test_harness_freeze.py::test_the_real_tree_matches_the_committed_manifest_when_it_exists`:
  data/step2_store.py and screening/harness_freeze.py differ from the committed v8 manifest, as
  any harness change does until the lead rebuilds it. The 2 skips are test_e2a_bars.py:506/518
  (MES research files not on disk in the worktree). The full 6,400-test suite was not run.
- ruff clean on data/step2_store.py and the new test; screening/harness_freeze.py's two E501
  (lines 157, 254) are pre-existing at deccd17.
- Manifest dry run in the worktree (`build_manifest()` called, nothing written): 1,042 files;
  reports/stage_e12_closure_rulings.json -> frozen_input, tests/test_e2b_step2_store_v9.py ->
  stage_e_test (matches TEST_PATTERNS "test_e2b_*.py"), data/step2_store.py -> harness_code.

## 4. Manifest commands (lead, in the tree that will run v9, after the ruling file is final)

```
cd <tree> && uv run --no-sync python -m screening.harness_freeze build
cd <tree> && uv run --no-sync python -m screening.harness_freeze verify --expected <sha256 printed by build>
```
(in the worktree, which has no .venv: `/home/kiros-li/Documents/GitHub/PropExperiment/.venv/bin/python -m screening.harness_freeze build|verify --expected <sha256>` from the worktree directory). Then the NQ and 6A builds:
`python -m data.step2_store --products NQ 6A --harness-sha256 <v9 sha256>` (the existing v8
summaries bars_NQ.json / bars_6A.json are overwritten by the run; no parquet exists for them).

## 5. Open items and choices for the lead

- The ruling file is a worker DRAFT (section 2): confirm its contents and text.
- Stricter than the brief, by choice: when the ruling file exists, it is parsed for EVERY
  product build, so a malformed file, or entries for a root whose build has no matching deep
  bar, refuse that build even when the root has no deep bars at all (the brief scoped the check
  to "when deep closure bars exist"). Existing ZN tests now read the real drafted file by
  default and pass (no ZN entries). Say if you want the check limited to roots with deep bars.
- Entries must hold exactly the four keys (no "note" field); any ruling value other than
  keep_and_flag refuses rather than holds.
- Downstream readers of the store beyond data.stage_e_bars (ML v2 features, the screening
  engine) were not audited for how they treat in_scheduled_closure rows deep in a closure; the
  research stores already carry such rows flagged (build_bars._keep_and_flag), so this is not new.
- The committed-manifest test fails in the worktree until the v9 manifest is built (expected).
