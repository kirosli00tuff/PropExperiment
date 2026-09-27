# Stage E.2b g2a: InputsCoder-OpusXHigh worker report (start dates S_X, shared loader, Q10)

Worker: InputsCoder-OpusXHigh (worker-xhigh, opus, xhigh). Brief: reports/stage_e2b_briefs/g2a_inputs.md.
Spawned 14:27 PDT; report written 14:50 PDT, 2026-09-26. Follow-up on the lead's rulings applied 16:40-16:47 PDT
(section 0). Sections 1-8 are the original report, with superseded statements marked.

## 0. Follow-up: lead rulings applied (16:47 PDT)

- **OC-S (Q-1): D6's (O_X, C_X) is the day session for every root.**
  - `D1_DAY_SESSION_CT` and `DAY_SESSION_RULINGS` are removed, replaced by the single rule `DAY_SESSION_RULE`, which cites OC-S.
  - `day_session_window(root)` returns E.2a's hashed per-contract (O_X, C_X) as [O_X, C_X). MES stays D.1f's RTH, which equals D6's equity row.
  - None of the 45 contracts in `reports/stage_e2a_vehicle_sizes.json` is refused (tested).
  - Only roots without a record are refused by name: ES has no E.2a record (`DaySessionUndeclared`); NKD, MET, 6M and BTC are not in the product table.
  - Each set file carries the rule text in a top-level `"day_session"` key.
- **Q-2:** kept. Any refused root refuses the whole set, before any bar is read, with every refused root named in one `StartDatesRefusal`.
- **Q-3: an empty window supplies 0 days.**
  - Runner: `confirmation_supply_days` calls the loader with `allow_empty=True`. A leg with `s_x` null supplies 0 days, so `power_check(series, ..., 0)` labels the member "inconclusive by design" (n_b > 0 exceeds 0).
  - The power record carries `empty_window: [roots]`, the provenance with `s_x` null, and the note `EMPTY_WINDOW_NOTE`: D4's full-size price-path fallback is the user's decision.
  - A confirmation run on an empty window is still refused by name (`StartWindowEmpty`).
  - A zero-variance series with an empty window still records "power check undefined": n_b is undefined, so no label can be compared. That combined case is the only one left undecided.
- **Q-4: the loader compares S_X, V_ref and every monthly median of a root across files.**
  - Any difference raises `StartRuleConflict`, naming the fields that differ and the files.
  - The parser now requires `v_ref` (a finite number > 0, not a bool) and a `monthly_medians` mapping of YYYY-MM keys to finite medians >= 0 or null. Anything else is `StartRuleInvalid`.
- **Q-7:** unchanged.
- **Tests after the follow-up:** `tests/test_stage_e_start_dates.py` 62, `tests/test_stage_e_runner.py` 22, all pass.
  - Start-date tests: 18 parametrized D6 windows (silver 12:25, copper 07:10-12:00, grains 13:15, livestock 13:00 included), plus all 45 E.2a contracts accepted with their recorded (O_X, C_X).
  - Set refusal: the whole-set refusal now uses ES and NKD.
  - Loader: conflicts on V_ref alone and on one monthly median alone; identical files accepted; `allow_empty` provenance; 6 more invalid-document cases.
  - Runner: an empty window gives supply 0 and "inconclusive by design", plus the note; an empty window refuses the confirmation run.
- **Other checks:**
  - Neighbouring ML route inputs, alignment, loader and stats_start tests: 64 passed.
  - Coverage: stage_e_start_dates 96%, stage_e_runner 93%.
  - ruff clean.
  - The RuntimeWarning in the power test comes from `screening/stage_e_stats_power.py:218` (ScreenStatsCoder's file), on a zero-supply run.

## 1. Files

Created
- `screening/stage_e_start_dates.py` (new harness file: the S_X builder per set and the one shared loader).
- `tests/test_stage_e_start_dates.py` (56 tests).

Modified (only for the edits the brief names)
- `screening/stage_e_runner.py`:
  - `START_RULE_PATH`, `START_RULE_SCHEMA` and `load_start_rule` are removed, replaced by `_start_dates(roots)`, which calls the shared loader.
  - Three new refusal classes: `StartWindowEmpty(StartRuleMissing)`, `StartRuleConflict(RunnerRefusal)`, `StartRuleInvalid(RunnerRefusal)`.
  - Records carry `"start_rule": {root: {"s_x", "files": [{"path", "sha256"}]}}` in place of `"start_rule_sha256"`.
  - The Q10 ruling is applied (section 4).
  - The unused imports `REPO_ROOT` and `sha256_file` are dropped, and `math` is imported.
- `tests/test_stage_e_runner.py`: 7 tests appended. None of the 14 existing tests was changed: none asserted the old single path, and the one confirmation test (StartRuleMissing matching "S_X") still passes through the new loader.

Not modified
- `screening/stage_e_align.py` needed no edit. S_X is applied by `data.stage_e_bars.load_confirmation_leg`, and alignment only sees the frames.
- No other worker's files were touched: nothing in ml_route/, data/, or `screening/stage_e_stats*.py`.

## 2. Public interface (the names MLTestCoder imports)

```python
# screening/stage_e_start_dates.py
load_start_dates(root=REPO_ROOT) -> Mapping[str, date]        # every reports/stage_e_start_rule_*.json merged
start_date(root_symbol, root=REPO_ROOT) -> date                 # runner's StartRuleMissing / StartWindowEmpty
start_dates_for(root_symbols, root=REPO_ROOT) -> (dict[str, date], provenance)   # what the runner uses
load_start_entries(root=REPO_ROOT) -> Mapping[str, StartDateEntry(root_symbol, s_x|None, sources)]
day_session_window(root_symbol, tables=None) -> (start, end)   # CT, [start, end)
day_session_monthly_medians(frame, window) -> {"YYYY-MM": median}
product_start_rule(root, *, research_path, step2_path, research_sha256, window) -> ProductStart
mes_from_d1f(root=REPO_ROOT) -> ProductStart
set_roots(set_id, root=REPO_ROOT, tables=None) -> (roots, frozen inputs)
build_set(set_id, *, harness_sha256, research_root, step2_root, root) -> dict     # preflight first
write_start_rule(doc, root) -> Path                             # write once, 0444, validated by the loader's parser
run_set(...) -> Path;  main(argv)
StartDatesRefusal(RuntimeError), DaySessionUndeclared(StartDatesRefusal)
python -m screening.stage_e_start_dates --harness-sha256 SHA --set K1..K8|ML [--research-root D] [--step2-root D]
```

Refusal classes:
- The loader's classes live in `screening.stage_e_runner`, so `ml_route.inputs`' `except StartRuleMissing` works unchanged.
- `StartWindowEmpty` is a subclass of `StartRuleMissing`.
- `StartRuleConflict` and `StartRuleInvalid` are RunnerRefusal but not StartRuleMissing, so ml_route lets them propagate, still named.
- The loader imports the runner lazily, and the runner imports the loader at module level, so there is no import cycle. Both import orders were checked.

File `reports/stage_e_start_rule_<SET>.json`:
- Top level: `{"schema": "stage_e_start_rule/2", "set", "rule", "products": {ROOT: {...}}, "inputs": [{"path", "sha256"}], "harness_sha256", "created_pdt"}`.
- Each product entry holds the brief's five keys (`s_x`, `s_x_015`, `s_x_040`, `v_ref`, `monthly_medians`) plus four for audit: `m_star` (per fraction), `first_trade_dates`, `day_session_ct` and `source`.
- `monthly_medians` holds the 14 reference months and the 58 extension months, with null for a month that has no day-session bar.
- `s_x` is null when no month qualifies (an empty window).
- Inputs recorded: research and step 2 parquet paths with their sha256, the E.2a sizes and vehicles table hashes, and the cluster freeze file and sha256 (clusters only).

## 3. How the brief is met, and the readings

- **Set roots.**
  - Cluster K: its traded vehicles (verified `reports/stage_e2a_vehicles.json`, statuses chosen or undersized, `cluster == K`) plus every leg of its frozen members (`reports/stage_e_<k#>_member_freeze.json`; a missing freeze is refused by name).
  - K8 has no own vehicles, so it is legs only.
  - ML: the 31 `ml_route.constants.PRICE_PATH_CONTRACTS`, including RB, HO and SI, which have no vehicle (the brief says all 31).
- **Stores.**
  - Research: `data.build_bars.research_parquet_path`. The sha256 must equal E.2a's recorded value.
  - Step 2: `data.step2_store.step2_parquet_path`. Its sha256 is recorded; there is no frozen value yet (runner Q9).
  - Only `ts_event`, `volume` and `trade_date` are read; a test spies on `read_parquet`.
  - Every row goes through `data.stage_e_bars.check_bookings`, so a holdout-1, holdout-2, embargo or out-of-store row refuses the root, as the runner's loaders do.
- **Rule.**
  - `screening.stage_e_stats_start.start_rule` is imported, not re-implemented.
  - Reference medians come from the research store, restricted to 2025-04..2026-05; June 2026 is dropped. Extension medians come from the step 2 store.
  - First trade dates (any session) come from `first_trade_dates_by_month`.
  - A stats refusal (for example a missing reference month) becomes a `StartDatesRefusal` naming the root.
- **Day session.** [Superseded by OC-S, section 0: D6's (O_X, C_X) for every root.]
  - CT clock minute of `ts_event` in [start, end), the month keyed by the bar's trade date, bars present, no exclusions. This is D.1f's rule; for MES it is RTH 08:30..14:59.
  - The window is D1's declared day-session window of the product's group, accepted only where it equals D6's (O_X, C_X) as E.2a froze it (`FrozenTables.day_session_ct`).
  - Agreement holds for equity (MNQ NQ M2K RTY MYM YM), crypto (MBT), rates, FX, energy and gold (GC, MGC).
  - Where the two frozen texts differ, the product is refused by name (`DaySessionUndeclared`, question Q-1). Every undeclared root of a set is named at once, before any bar is read, and nothing is written.
  - Roots with no Stage E product entry (NKD, 6M, MET, BTC) or no E.2a record (ES) are refused by name.
- **MES as a leg.**
  - MES's bars are not read (common brief). D4 fixes "MES as a leg starts 2020-02-03".
  - The entry comes from D.1f's record `reports/stage_d1f_step5_start_rule.json`:
    - its sha256 is pinned (`4f2870f5...`);
    - the rule is re-run on the recorded medians and first dates and must reproduce the record, including 0.15 and 0.40;
    - S must equal D4's 2020-02-03.
- **Whole-set refusal.** Any refused root refuses the whole set, so no partial frozen file is ever written (question Q-2).
- **Writing.** The file is written once with open mode "x", then chmod 0444. The document must pass the loader's own parser before it is written.
- **Preflight.** `build_set` calls `harness_freeze.preflight(harness_sha256)` before reading anything; `run_set` and the CLI go through it.
- **Loader.**
  - It merges every `reports/stage_e_start_rule_*.json`.
  - These are refused as `StartRuleInvalid`, naming the file:
    - a file name that is not `_K1.._K8` or `_ML`;
    - bad JSON;
    - a wrong schema;
    - a `set` that differs from the file name;
    - no products;
    - a missing `s_x`;
    - an `s_x` outside 2019-05-06..2024-02-29 or not in ISO form.
  - A root with different S_X in two files is refused (`StartRuleConflict`). Only S_X is compared, as the brief says (question Q-5).
  - A null `s_x` raises `StartWindowEmpty`.

## 4. Lead ruling on runner Q10 (mean <= 0 is Tier B)

Finding, stated plainly: the stats module has, since its 13:07 follow-up, returned `passes False, t None` for sd = 0 with mean <= 0. So a member that never trades was already tiered B by the runner's existing path; the runner report's Q10 text described the older behaviour. The runner test `test_a_member_that_never_trades_fails_the_screen_and_is_tier_b` now proves it end to end: tier B, t None, and power "power check undefined" with supply 8.

Added to apply the ruling in full:
- `_screen(series)`: when the stats module raises `ScreenUndefined` but the series is finite with mean <= 0 (n < 2 is the only such case left), the runner builds `ScreenResult(passes=False, t_daily=None)`, so the member is Tier B. The two remaining undefined cases stay named `screen_undefined` and not tiered, as before:
  - sd = 0 with mean > 0;
  - any non-finite value.
- `screen_cluster` output gains `"power_check_undefined": [members]`, which names the members whose power check is undefined as the user's question. They are tiered as usual.
- Docstrings of the module and of `_research_statistics` state the ruling.

## 5. Tests

`tests/test_stage_e_start_dates.py`: 56 tests, all pass.
- Day session:
  - 10 parametrized: D1 = D6 for MNQ, NQ, MBT, ZN, 6E, CL, MCL, GC and MGC, plus MES from D.1f.
  - 11 parametrized: SI, SIL, HG, MHG, ZC, ZW, ZS, ZM, ZL, HE and LE refused by name, citing D1 and D6.
  - 5 parametrized: ES, NKD, MET, 6M and BTC refused by name.
  - Minute boundaries: 08:29 out, 08:30 in, 14:59 in, 15:00 out.
  - Months keyed by trade date: a 2021-05-31 bar booked to 2021-06-01 counts in June.
- Builder:
  - D.1f reproduction. Synthetic research and step 2 stores whose day-session medians are D.1f's recorded MES medians give v_ref 1763.0, S_X 2020-02-03, S at 0.15 = 2020-01-02 and at 0.40 = 2020-03-02, and M* 2020-02, 2020-01 and 2020-03. All 72 monthly medians and 58 first trade dates equal D.1f's.
  - The stores carry 90 pre-open bars of volume 10^7 on each date. 2020-02's first date has pre-open bars only, which proves "first trade date with bars (any session)".
  - The June 2026 research date is excluded.
  - Only three columns are read (spy).
  - A research sha mismatch is refused.
  - A missing step 2 store is refused (ConfirmationStoreMissing).
  - A March 2024 row in the step 2 store and a holdout-2 row in the research store are each refused (HoldoutRowRefused).
  - A missing reference month is refused, naming the root and the month.
  - No qualifying month gives `s_x` null.
  - MES from the pinned D.1f record; a tampered copy is refused on its sha256.
- Sets:
  - ML = the 31 price-path contracts.
  - K2 = its 6 vehicles plus the MES leg from a synthetic freeze, with the freeze's path and sha recorded as an input.
  - A missing freeze and an unknown set are refused.
- Entry:
  - `run_set` writes once, read-only, with schema /2, the PDT stamp and the inputs, and the loader reads it back. A second run is refused.
  - A preflight refusal stops the entry before the set or any store is read, and nothing is written.
  - Undeclared day sessions refuse the whole set before any read.
  - The CLI requires `--harness-sha256` and `--set` and passes the hash to preflight.
- Loader:
  - No file: an empty mapping, and StartRuleMissing by name.
  - Files merged, with provenance paths and sha256.
  - Conflict refused.
  - Empty window: `StartWindowEmpty`, which is a StartRuleMissing.
  - Every missing root is named.
  - 6 parametrized invalid documents.
  - A stray file name and non-JSON are refused.
  - The writer refuses a document the loader would refuse.

`tests/test_stage_e_runner.py`: 21 tests (14 existing, unchanged; 7 new), all pass.
- The runner's `_start_dates` delegates to `stage_e_start_dates.start_dates_for`, and the old names are gone.
- The confirmation run's window starts at the shared S_X, and the record carries `s_x` and both files with their sha256.
- Two files that disagree refuse the confirmation run (`StartRuleConflict`).
- The power-check supply counts step 2 days from the shared S_X, and its meta carries the provenance.
- An empty window is recorded as power `not_run` with "StartWindowEmpty: ZN ...".
- Q10:
  - A never-trading member is Tier B, `t None`, with power undefined listed.
  - n = 1 with mean < 0 goes through the fallback and is Tier B.
  - sd = 0 with mean > 0 stays `screen_undefined`.
  - -inf stays `screen_undefined`.

TDD note: the start-date tests were written first and failed at collection (module absent) before the module existed. The 7 runner tests were written after the runner edits and passed on their first run.

## 6. Commands run (PDT)

| Time | Command | Result |
|---|---|---|
| 14:3x | `uv run --no-sync python -m pytest -q tests/test_stage_e_start_dates.py -x` (before the module) | RED: collection ImportError |
| 14:4x | same, after the module | 56 passed in 1.7 s |
| 14:4x | `pytest -q tests/test_stage_e_runner.py tests/test_ml_route_stage_e_inputs.py tests/test_stage_e_alignment.py tests/test_stage_e_loader.py` | 60 passed |
| 14:4x | `pytest -q tests/test_stage_e_runner.py` (with the 7 new tests) | 21 passed |
| 14:45 | `heavy.sh pytest -q` on stats_start, stats, ml_route stage_e_inputs, ml_route test_entry, ml_route stage_e_adapter, stage_e rules, freeze and frozen | 165 passed in 77 s |
| 14:46 | `coverage run --include=... -m pytest -q` on the 2 test files | stage_e_start_dates 96%, stage_e_runner 93% (77 passed) |
| 14:4x | `ruff check` on the 4 files | all checks passed |
| 14:47 | `heavy.sh` timing probe (SYNTHETIC stores at real scale: 2.54M step 2 rows, 640k research rows) | `product_start_rule` 8.7 s per product, peak RSS 648 MB |
| 14:47 | `python -m screening.stage_e_start_dates --help`; import-order check | OK; the real repo has no start-rule file, so the loader raises StartRuleMissing |

- The probe gives the ETA for the real CLI runs: about 9 s per root, so about 5 min for the 31-root ML set, peak under 1 GB. Run it through heavy.sh.
- `pytest --cov` (the pytest-cov plugin) fails to import numpy in this venv. This is an environment issue, not these files, so coverage was measured with `coverage run`.

## 7. Questions for the lead

Rulings received for these (section 0): Q-1 D6 for all (OC-S); Q-2 kept; Q-3 supply 0 days, "inconclusive by design"; Q-4 compare S_X, V_ref and the medians; Q-7 fine. Q-5 (manifest) and Q-6 (store contents) remain for Task 6 and the step 2 owners.

- **Q-1 (blocks K5, K6 and the ML set until ruled). Day-session window where D1 and D6 differ.**

  | Product | D1 window | D6 (O_X, C_X) |
  |---|---|---|
  | silver (SI, SIL) | 07:20-12:30 | 07:20-12:25 |
  | copper (HG, MHG) | 07:20-12:30 | 07:10-12:00 |
  | grains (ZC, ZW, ZS, ZM, ZL) | 08:30-13:20 | 08:30-13:15 |
  | livestock (HE, LE) | 08:30-13:05 | 08:30-13:00 |

  - These 11 roots are refused by name.
  - My reading, not applied: D1 governs.
    - D1 is the only text that declares "day-session windows".
    - D6's header calls C the "daily settlement time", and D6's own F column gives the session close as 13:20 (grains) and 13:05 (livestock), as D10 does.
    - D.1f's MES window is RTH, a clock window, not the settlement time.
    - Against this, D2 calls (O_X, C_X) the "day-session open and close". E.2a's `day_session_ct` and the ML route also use D6.
  - Copper stays open under either reading: D6's O of 07:10 is the "conventional CME day-session open" (ruling L-1), where D1 says 07:20.
  - Resolving it is a one-line entry per root in `DAY_SESSION_RULINGS` ("D1" or "D6"). The module hash changes, so the manifest must be rebuilt.
- **Q-2.** A set with any refused root is refused whole, so no partial file is written. Keep this, or allow a partial file and let the loader name the missing roots?
- **Q-3.** An empty window (no qualifying month) is recorded as power `not_run: StartWindowEmpty`. Should the power check instead treat it as supply 0, which is "inconclusive by design" under D4?
- **Q-4.** The same root appears in several files (for example a K2 vehicle in the ML set). The loader compares only S_X, as the brief says; it does not compare v_ref or the input hashes. Stricter?
- **Q-5 (for Task 6).** The harness manifest must list `screening/stage_e_start_dates.py` (new) and re-hash `screening/stage_e_runner.py`. Until then, preflight refuses the unlisted module.
- **Q-6 (for PurchaseCoder2 / the cluster sessions).**
  - The step 2 store must hold every root of a set, including cluster signal legs; MES is taken from D.1f's record.
  - The ML set computes RB, HO and SI as well: the brief says all 31, though ML reads only the 28 with a vehicle.
- **Q-7 (for MLTestCoder, via the lead).** `start_date` raises the runner's StartRuleMissing or its subclass StartWindowEmpty. `StartRuleConflict` and `StartRuleInvalid` are RunnerRefusal but not StartRuleMissing, so `ml_route.inputs.load_start_dates` lets them propagate. They are named refusals, not a RouteInputMissing.

## 8. Deviations and anything unfinished

- Boundaries kept:
  - No bar parquet of any product was opened. Reads were synthetic data, the E.2a tables (hash-verified, through `load_frozen_tables`) and D.1f's recorded start-rule JSON (medians, no bars).
  - No git command changed the tree.
  - No holdout path was touched and no purchase was made.
- Extra keys beyond the brief's schema: top-level `schema` and `rule`; per product `m_star`, `first_trade_dates`, `day_session_ct` and `source`. The brief's keys are all present.
- Not done, because there is nothing to read yet: no real `reports/stage_e_start_rule_<SET>.json` was built, since there is no step 2 data. Q-1 no longer blocks any set (OC-S).
- Still open: the harness manifest (Q-5) must list `screening/stage_e_start_dates.py` and re-hash `screening/stage_e_runner.py`.

## Follow-up F-3 (review reports/stage_e2b_harness_review.md F-3, lead ruling: fix; 18:05-18:35 PDT)

Files changed:
- `screening/stage_e_start_dates.py`
- `data/stage_e_bars.py` (for this fix only)
- `screening/stage_e_runner.py` (the confirmation call sites and the new class)
- `tests/test_stage_e_start_dates.py`, `tests/test_stage_e_loader.py`, `tests/test_stage_e_runner.py`

Not touched: `stage_e_freeze.py` and the template (RunnerCoder's).

**(a) Every entry must follow from its own data.**
- On every load, and in `write_start_rule`, the loader parses each entry's `monthly_medians` (reference and extension months only), `first_trade_dates` and `step2_sha256`.
- It re-runs `screening.stage_e_stats_start.start_rule` on them and compares with the recorded values: `s_x`, `v_ref`, `s_x_015`, `s_x_040` and `m_star`.
- Any difference raises `StartRuleInconsistent`, naming the root, the fields, and the recorded and re-run values. It is a new subclass of `StartRuleInvalid` in the runner.
- Medians that cannot re-run the rule (for example a missing reference month) are refused the same way.
- The builder writes entries through the new `entry_from_medians`, so every file it writes passes this check.

**(b) The step 2 store is pinned.**
- Each entry records `step2_sha256`, the store its medians were read from. For MES it is D.1f's confirmation parquet (`82e256b4...`, taken from D.1f's pinned record).
- The cross-file comparison (Q-4) now covers `s_x`, `v_ref`, the medians, the first trade dates and `step2_sha256`.
- `data.stage_e_bars.load_confirmation_leg` and `read_leg_dates` take a required keyword `expected_sha256` and refuse by name:
  - a non-sha256 value: ValueError;
  - a store that hashes differently: `ParquetHashMismatch`.
- `read_leg` now requires a sha256 for both stores; the `None` path is gone.
- The runner passes each leg's recorded `step2_sha256` from the shared loader's provenance.

**(c) Records.** Every confirmation record and every power-check record carries `start_rule: {root: {s_x, step2_sha256, files: [{path, sha256}]}}`; confirmation records also carry the store's sha256 under `bars`. Stating the start-rule sha256s in the cluster prompt is an instruction for later sessions, not code.

**Tests**
- `tests/test_stage_e_start_dates.py`: 72 tests.
  - The review's E1: medians giving S_X = 2019-05-06 with `s_x` written as 2023-06-15. The writer refuses it and writes nothing; a hand-written file is refused by `start_dates_for` and `start_date`.
  - A doctored `v_ref`, `s_x_015`, `s_x_040` or `m_star` (4 parametrized cases) is refused.
  - Medians missing a reference month are refused.
  - Each entry keeps its `step2_sha256`.
  - Two files agreeing on S_X but differing in `v_ref`, one median, or `step2_sha256` are refused.
  - 3 more invalid-document cases.
  - The test entries are built by a helper, `consistent_entry`, that runs D4's rule, so they follow from their own data.
- `tests/test_stage_e_loader.py`: 19 tests.
  - Existing calls now pass the file's sha256.
  - New: a doctored store (volumes changed) is refused by both `load_confirmation_leg` and `read_leg_dates`.
  - New: 4 parametrized non-sha256 expected values are refused.
- `tests/test_stage_e_runner.py`: 25 tests, 2 of them (`test_oct_*`) added by another worker.
  - New: a doctored step 2 store refuses the confirmation run (`ParquetHashMismatch`) and is recorded as the power check's named `not_run` on the research window.
  - The confirmation record's `bars` sha256 equals the recorded `step2_sha256`.

**Runs**
- `heavy.sh pytest -q tests/test_stage_e_*.py tests/test_ml_route_stage_e_inputs.py`: 550 passed in 214 s (18:2x PDT).
- Coverage on the 3 test files (116 passed): stage_e_start_dates 96%, stage_e_runner 94%, stage_e_bars 93%.
- ruff clean on all 6 files.

**Consequences for the lead**
- F3-1, MES as a leg. Its S_X is pinned to D.1f's confirmation parquet, so a confirmation read of `step2_parquet_path("MES", ...)` passes only if that file is byte-identical to D.1f's `ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet`. A step 2 MES store built separately will be refused by name. Which MES store confirmation runs read, and how it is pinned, is your call.
- F3-2. `ml_route`'s own step 2 reads for training (MLTestCoder's) read S_X through `start_date` but are not pinned by this change. Pinning them to `provenance[root]["step2_sha256"]` (`start_dates_for`) would be the parallel fix in ml_route.
- F3-3. The harness manifest must re-hash `screening/stage_e_start_dates.py`, `screening/stage_e_runner.py` and `data/stage_e_bars.py`.
