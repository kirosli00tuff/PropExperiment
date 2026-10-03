# Phase1Coder-OpusXHigh report (Stage E.12 Task 1b)

Brief: reports/stage_e12_briefs/brief_phase1coder.md. Real-data entry point of ML route v2 phase 1:
`python -m ml_route_v2.phase1 build|register|run`. Built and tested on synthetic fixture stores
only. No bar row of any real store was read. No commit, no key, no network.

## 1. Files

New (all under ml_route_v2/ or tests/test_ml_v2_phase1*.py):

| file | lines | content |
|---|---|---|
| ml_route_v2/phase1/__init__.py | 21 | exports |
| ml_route_v2/phase1/__main__.py | 7 | `python -m ml_route_v2.phase1` |
| ml_route_v2/phase1/world.py | 463 | P-1 coverage, P-3 start dates, bar loading, window guard, `phase1_world` |
| ml_route_v2/phase1/build.py | 271 | build step: panel and filter stage files, bars and c/sigma reports |
| ml_route_v2/phase1/gate0_stage.py | 334 | P-2 list, register, run (run once, resume), Gate 0 JSON and MD |
| ml_route_v2/phase1/freeze.py | 99 | `verify_v2_freeze(path, expected_sha256)` |
| ml_route_v2/phase1/cli.py | 139 | argparse; harness preflight, then freeze check, before anything else |
| ml_route_v2/phase1/_io.py | 76 | atomic JSON writes (NaN to null), sha256, PDT time stamp |
| tests/test_ml_v2_phase1_support.py | 233 | fixture stores in the real formats (holds no tests) |
| tests/test_ml_v2_phase1_world.py | 244 | 17 tests |
| tests/test_ml_v2_phase1_freeze.py | 88 | 10 tests |
| tests/test_ml_v2_phase1_gate0.py | 263 | 11 tests |

Edited (minimal; defaults unchanged):
- ml_route_v2/panel.py (+12/-7): `build_panel(..., signals=None)` (line 107; names at line 114),
  which `_features` passes to `compute_signals(ctx, names)`. None means all of REGISTRY, as before.
- ml_route_v2/pipeline.py (+6/-3): `build_world_panel(world, *, check_grid=True, signals=None)`
  (line 269), passed through to `build_panel` (line 287).
- ml_route_v2/clock.py: not edited. It already applies the real group calendar's early-halt and
  early-close exclusions: `ml_route.inputs.day_times` loads the real calendar and
  `rules.sessions.flatten_time_ct` gives the early close. Pinned by
  `test_clock_excludes_real_early_halt_dates` (HE, MNQ, ZN, every real early halt 2019-05..2024-02).

## 2. Rules (file:line)

- **P-1.** `world.py:113 available_roots` gives the price paths plus MES. `world.py:118
  signal_coverage` marks a signal covered iff `own_path_only`, or every root it reads is
  available; the uncovered ones are recorded with their missing roots. `build.py:150` builds the
  panel with the covered signals only. The micro stores (MCL, MGC, MHG) are never read: a vehicle
  maps to its path (MCL to CL).
- **P-2.** `gate0_stage.py:72 list_tests` runs gate0's own `_register_a`, `_b_pairs` and
  `_register_b` (with `DEFAULT_RULE`) into a recorder, so the ids and specs are gate0's.
  `:86 list_doc` assembles the list. `:141 run_register` writes the list once (0444) and
  registers it in `ConfigLedger`. `:289 run_gate0` checks the sha (`:276`) and the registration
  (`:128`), applies the run-once guard (`:258`) and the pin (`:265`), then calls
  `pipeline._gate0` unchanged (`:306`).
- **P-3.** `world.py:158 root_start` calls `product_start_rule` with E.2a's research sha256 and
  the D6 window. `:181 mes_root_start` calls `mes_from_d1f`, giving 2020-02-03 and the confirmation
  sha. `:429` drops an empty-window root by name. `:256 load_root_leg` uses
  `load_confirmation_leg` (MES: `read_leg` plus the same cut). `:211 refuse_late` refuses any bar
  dated on or after 2024-03-01. `:442` builds the training calendar. No start-rule file is written.
- **Freeze and harness.** `freeze.py:61` and `cli.py:54 _gates` run before any read.

## 3. Assumptions (each one is mine; the lead may veto any before the freeze)

1. The training calendar starts at the earliest S_X of the kept vehicles' price paths. MES is
   signal-only and does not set the start.
2. A vehicle's own roll blackout is its price path's. Its micro store is not read (P-1), and
   `pipeline.own_blackout` is unchanged.
3. MES is loaded through `data.stage_e_bars.read_leg(MES, <confirmation parquet>, STEP2,
   expected_sha256 = D.1f's recorded confirmation sha)`, then cut at S_X exactly as
   `load_confirmation_leg` cuts. The step 2 layout has no MES file, and E.2b review F3-1 left
   that choice open. This path has not been run on the real file, since that would mean reading
   rows. If D.1f's trade_date labels differ from the equity calendar's L-3 booking, build stops by
   name (`TradeDateMismatch`). Its metadata (rolls; trade_date_range 2019-05-06..2024-02-29) is
   compatible.
4. On real data `build_world_panel(check_grid=False)` (`build.py:150`).
   `assert_bars_on_session_grid` books bars without L-3 and would refuse real close-minute
   prints. The frozen loader's L-3 booking check replaces it, and each root's report counts the
   bars outside the open intervals and the close-minute bars.
5. A root with an empty window drops its vehicle and is not available to coverage.
6. If no pair is admissible, the list is empty and the verdict is FAIL, as `pipeline._gate0`
   computes nothing then. P-2's text would still list family A.
7. A step 2 summary whose `parquet.sha256` is not the store's sha is refused. MES has no summary,
   so its degraded dates come from the parquet metadata. Degraded dates are reported and kept.
8. Existing start-rule files (K4 and K5 list NG and others) are only compared. The result
   (`s_x_agrees`, `store_sha256_agrees`) goes into the bars report; a mismatch is never refused.
9. The bars are compacted to 8 columns. Prices stay float64; volume and instrument_id become
   uint32 when they fit.
10. Run once means `state_dir/gate0_DONE.json` exists, or `reports/stage_e12_gate0.json` exists.
    A resume needs the same constants, inputs and list sha (`gate0_run.json`) and passes gate0's
    own B-state check.
11. JSON: NaN is written as null, and ±inf as "inf"/"-inf".

## 4. Tests

- `PYTHONPYCACHEPREFIX=/tmp/claude-1000/pyc_p1t3 nice -n 10 uv run pytest -q -p no:cacheprovider
  tests/test_ml_v2_phase1_*.py` gives **`38 passed in 22.32s`**.
- Phase 1 plus `test_ml_v2_panel.py` and `test_ml_v2_e2e.py`: `63 passed in 130.29s`.
- Whole `tests/test_ml_v2_*.py`: `10 failed, 771 passed, 1 xfailed in 264.84s`. All 10 failures
  are in V23Coder's in-progress files: `decide` wants a `release_window` column, the leakage
  cost-gate counts, the payout 150K figures, and the portfolio tiers (x7). None touches
  panel.py or pipeline.py; my diff there only adds a defaulted `signals=None`.
- What the tests cover:
  - the coverage rule (stub registry and the real registry);
  - S_X cut (LE's low-volume June 2022 gives S_X 2022-07-01);
  - the empty-window root dropped by name (ZC), and the MES date from the real D.1f JSON record;
  - the window guard: `refuse_late`, `assert_window`, and a store with a 2024-03-01 bar refused;
  - sha pins for research, MES and the summary; degraded dates reported and kept;
  - roll-blackout rows dropped, and real-calendar early halts;
  - the freeze check (good manifest, tampered file, missing file, wrong sha, malformed), and the
    CLI refusing before it reads or writes anything;
  - the list (|A| = covered × 3, |B| = admissible pairs, gate0's ids, ledger lines), and
    register being idempotent and refusing a changed list;
  - registration is a no-op for the run (ledger bytes unchanged);
  - refusals: list sha, list content, unregistered tests, run once;
  - resume after a crash in family B after 7 fits: the 7 saved splits are not refit and the
    results are identical;
  - a resume under a changed constant is refused;
  - end to end through the CLI: the planted edge (synthetic.py `sign` plant, 10c, fed through the
    fixture stores) gives **PASS**, noise gives **FAIL**.

## 5. Memory

Measured on the fixture: 856k bars (HE, LE, MES), 1,653 panel rows, 161 columns.
- Baseline after imports is about 250-290 MB RSS. The panel stage peaks at 448-458 MB and the
  filter stage at 378-385 MB.
- Compact bars take 50 B per bar. Five back-to-back MES loads (620k bars each) kept about 1.2x
  that in RSS, after a one-time ~45 MB.
- `read_leg` (full columns plus booking) costs a transient 289 B per bar, which is freed after.
- The panel frame takes 1,440 B per row.

Extrapolation to 25 products:
- The worst case is about 24 h a day for every product (NG's store has 1.535M rows) plus MES
  from 2020-02-03, about 39M bars.
- Bars about 2.3 GB, signal and target day caches about 0.3 GB, panel-phase copies about 0.6 GB
  (86k rows), baseline 0.3 GB. That gives a **peak of about 3.0-3.5 GB**. The load phase is
  about 3.1 GB, with the largest root's transient (at most about 0.5 GB) on top of the bars.
- 10 products come to about 1.5-1.8 GB. The register and run steps hold the panel only: under
  1 GB.
- This is under 4 GB but not well under. The bars (float64 prices) dominate. Storing float32
  would not help: `signals._core.bar_arrays` and the targets cast to float64 copies.
- The world (all bars) is freed when the panel stage returns; register and run never load bars.

## 6. Open items and rulings needed

1. The design text (V2.2b, "The phase-1 test list") names `ml_route_v2/phase1.py`. It is
   implemented as the package `ml_route_v2/phase1/` (the brief allowed this), and the CLI is
   identical. The design line may need `ml_route_v2/phase1/` before the freeze.
2. The memory peak at 25 products is about 3-3.5 GB (section 5). Accept, or cap the subset.
3. Acknowledge assumptions 3 (MES loader; not verifiable without reading rows) and 4
   (`check_grid=False`).
4. P-2 counts covered signals that never apply to the phase-1 vehicles. On the fixture (HE, LE),
   26 of the 48 covered signals are 0 on every row. Their 78 family A tests have p = 1 and
   enlarge the Holm family. The real count depends on the vehicles. Informational only; the rule
   is the lead's.
5. The freeze manifest should list source files only. `ml_route_v2/__pycache__` exists in the
   tree, and every step re-hashes every listed file.
6. P-3 reads research-store volume, while the stage SCOPE says no research-window bar is read.
   P-3 and the design ("never a price") already decide this; noted only.
7. Observation: NG's step 2 summary records `calendar_check.passed: false` (an early-stop
   discrepancy). This is not in my brief.

Invariants: holdout `unlocks_logged` 0, `all_ok` true; REGISTRATION.md 0 bytes; nothing was
written to the real reports/ or ledger/ (all runs used tmp or scratch dirs).

## Follow-up: MES contingency (lead ruling E.12 P-1a)

- **Trigger.** Loading MES's frozen confirmation store raises a
  `data.stage_e_bars.StageEBarRefusal` subclass (`world.py:486`), or D.1f's record check fails
  with `StartDatesRefusal` from `mes_from_d1f` (`world.py:434`). Either makes MES UNAVAILABLE
  instead of stopping the build. That second check covers the record's pinned sha256, and also
  its presence and its re-run.
- **Reason text.** "MES store refused: <exception class>: <message>" (`world.py:442 mes_refused`).
- **Price-path refusals** still stop the build. The code re-raises for any root other than MES
  (`world.py:488`), and `available_roots` refuses to mark a price path unavailable
  (`world.py:131`).
- **Coverage.** P-1 treats MES like any root not owned: `signal_coverage(...,
  unavailable={MES: reason})` (`world.py:143`, called at `world.py:495`). `Coverage.unavailable`
  and `Coverage.reasons()` (`world.py:100-102`) give each uncovered signal its reason.
- **World fields.** `Phase1World.mes_status` ("loaded" | "refused") and `mes_refusal`
  (`world.py:413`, set at `world.py:505`).
- **Bars report.** Records `mes_status`, `mes_refusal`, `signals.uncovered_reasons` and
  `signals.unavailable_roots` (`build.py:136, 146`) and the rule text (`build.py:47 RULE_P1A`).
  The input record and fingerprint pin the MES status (`build.py:95`), and so does the Gate 0
  list (`gate0_stage.py:97`).
- **CLI.** Prints one line, "MES store: loaded" or "MES store: refused, every signal reading
  MES excluded (<text>)" (`build.py:222-225`).
- **Tests** (`tests/test_ml_v2_phase1_world.py`):
  - `:220`: a fixture MES with mislabelled trade dates (`write_mes(mislabel=...)`,
    `tests/test_ml_v2_phase1_support.py:185`) raises `TradeDateMismatch` in the loader, then the
    CLI build completes. Every MES-reading signal is uncovered with the reason, `mes_status` is
    "refused", and exactly one "MES store" line is printed.
  - `:256`: a failing D.1f record check makes MES unavailable.
  - `:214`: only a signal-only root can be unavailable.
  - `:269`: the "loaded" status is recorded.
  - `:201`: the former MES-sha assertion is updated to P-1a. A wrong MES sha now gives
    "refused" (`ParquetHashMismatch`), and a wrong price-path research sha still raises.
- `PYTHONPYCACHEPREFIX=/tmp/claude-1000/pyc_p1a nice -n 10 uv run pytest -q -p no:cacheprovider
  tests/test_ml_v2_phase1*.py` gives **`42 passed in 29.30s`**.
- Line counts now: world.py 514, build.py 286, test_ml_v2_phase1_world.py 307,
  test_ml_v2_phase1_support.py 246.

## Follow-up 2: F-2, F-3, F-8 (freeze review reports/stage_e12_review.md)

This supersedes the CLI usage in sections 1-2. The command line is now
`python -m ml_route_v2.phase1 build|register|run --harness-sha256 SHA --freeze-sha256 SHA`, and
run also takes `--expected-list-sha256 SHA`.

### F-2: canonical paths only

- `--freeze-manifest`, `--reports-dir`, `--ledger`, `--state-dir` and `--vehicles` are removed
  (`ml_route_v2/phase1/cli.py:43-53`).
- The paths live only in module constants (`cli.py:35-40`):
  - `FREEZE_ROOT` = REPO_ROOT; the manifest is always `FREEZE_ROOT / freeze.FREEZE_MANIFEST`,
    verified against `--freeze-sha256` (`cli.py:63`);
  - `REPORTS_DIR` = REPO_ROOT/reports;
  - `LEDGER_PATH` = REPO_ROOT/ledger/ml_v2_config_ledger.jsonl;
  - `STATE_DIR` = `~/.cache/propexp_e12_phase1` (expanduser);
  - `WORLD_KW` = {}: the stores are data.config's.
- `main(argv)` takes no keyword arguments any more.
- Tests reach their tmp paths only by monkeypatching these constants and
  `screening.harness_freeze.preflight` (`tests/test_ml_v2_phase1_gate0.py _cli`;
  `tests/test_ml_v2_phase1_freeze.py _canonical`), or by calling the step functions directly.
- Tests:
  - `test_ml_v2_phase1_gate0.py:199`: every removed flag exits with a usage error;
  - `test_ml_v2_phase1_freeze.py:93`: a valid manifest elsewhere is not used, and the
    canonical one is required;
  - `test_ml_v2_phase1_freeze.py:103`: the canonical constants are pinned.

### F-3: vehicles derived from the ranking

- `world.py:206 phase1_subset` reads the "subset" of `REPORTS_DIR/stage_e12_ranking.json`
  (`RANKING_FILE`, `world.py:172`). It keeps each vehicle whose price-path step 2 store
  (`step2_parquet_path(path)`) and summary `bars_<PATH>.json` both exist.
- A subset vehicle without them is dropped by name with "no step 2 store (purchase incomplete or
  failed)" (`world.py:173, 225`).
- The ranking is refused when:
  - the file is absent;
  - it is not valid JSON or has no subset;
  - an entry is malformed;
  - a vehicle/path pair is not in UNIVERSE (for example MCL with path "MCL");
  - a vehicle is duplicated;
  - no subset vehicle has a store.
- `run_build` derives the vehicles itself (`build.py:276`). The ranking's name, sha256, subset
  and no-store drops go into the input record, and so into the input fingerprint
  (`build.py:94, 103`), and into the bars report (`build.py:155`). The Gate 0 list's
  fingerprints carry the ranking sha (`gate0_stage.py:101`).
- A resume under another ranking file or another derived set is refused as a changed input
  (`build.py:282`).
- Docstrings are updated: world.py module docstring ("Vehicles (freeze review F-3)"),
  `build.py`, `cli.py`, and the package `__init__.py`.
- Tests:
  - `test_ml_v2_phase1_world.py:214`: the derived set, in ranking order, with ZN (no store)
    dropped by name and the sha recorded;
  - `test_ml_v2_phase1_world.py:228`: a missing summary drops that vehicle by name;
  - `test_ml_v2_phase1_world.py:242`: an absent or malformed ranking refuses;
  - `test_ml_v2_phase1_gate0.py:131`: the bars report and the input record carry the ranking
    sha and `dropped_no_store`;
  - `test_ml_v2_phase1_gate0.py:185`: a rebuild after the ranking changed is refused;
  - `test_ml_v2_phase1_gate0.py:193`: no ranking file means build refuses, before any state is
    written.
- **Reading for the lead:** NG is kept iff it is in the ranking's subset; its owned store counts as
  present. NG is not added when the subset omits it, so the ranking should list NG (at $0), as
  the design's "NG included at $0" implies.

### F-8: freeze manifest key check

- `freeze.py:40` is now `not {"path", "sha256", "bytes"} <= set(entry)`.
- Test: `test_ml_v2_phase1_freeze.py:57`, where an entry `{"path", "sha256", "foo"}` raises
  FreezeError "malformed" instead of KeyError.

### Result

- `PYTHONPYCACHEPREFIX=/tmp/claude-1000/pyc_p1f2 nice -n 10 uv run pytest -q -p no:cacheprovider
  tests/test_ml_v2_phase1*.py` gives **`50 passed in 29.44s`**.
- No test wrote to the real reports/, ledger/ or `~/.cache/propexp_e12_phase1`.
