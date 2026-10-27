## 6. E.31 code that can be reused for directional features and labels, and what is missing

Source: module and function docstrings and signatures of reports/stage_e31_briefs/work/pilot/*.py
(read by `ast`, 2026-10-27), reports/stage_e31_pilot_spec.md section headings, and
README_measure31.md. Test counts are `def test_` lines in pilot/tests/. "Reuse" means import as is
or copy with the same semantics; nothing below was run except `mbo_book31.Book` and
`mbo_book31.time_axis` in section 5.

### 6.1 Reusable as is

| Module | Function / class | What it does (docstring) | Directional use | Tests |
|---|---|---|---|---|
| mbo_book31 | `Book` (`add`, `cancel`, `modify`, `clear`, `on_fill`, `end_snapshot`, `mark_bad`, `best`, `level_total`, `queue`, `is_valid`, `top_at`) | "One instrument's displayed outright book with time priority and TOP state." A modify that raises size or changes price loses priority; R clears; T, F, N do not change the book; F_MAYBE_BAD_BOOK marks the book bad until the next R. | The core of every book feature (best levels, level totals, queue lengths, order counts) for ZM.v.0 and ZM.v.1. Only `best` and `level_total` are O(1)/O(levels); there is no depth-k accessor beyond `prices` (sorted price lists per side) and `levels`. | test_book31.py, 19 |
| mbo_book31 | `time_axis(ts_event, ts_recv, flags)` | "ts_event made non-decreasing in file order. Snapshot records carry the snapshot generation time (ts_recv) instead of an event time, so they enter the running maximum with ts_recv; inversions are counted over the other records only." | The event-time axis for any sampler and label horizon. | test_book31.py |
| mbo_book31 | constants `ACT_*`, `SIDE_*`, `F_*`, `UNDEF_PRICE`, `book_side` | Action, side and flag codes matching Databento's. | Shared decoding constants. | |
| measure31.py | `split_file`, `compact`, `day_bounds`, `MBO_COMPACT`, `MBP_COMPACT` | "Stream one Z1/Z2/Z3 file once into per-trade-date compact arrays (resumable per file)." Trade date D = ts_recv in [D-1 16:00 CT, D 16:00 CT); keeps regular grains trade dates of the file's month. | The per-day store already exists for all 39 months (section 4.3, 47 GB at /mnt/large-storage/market_data/PropExperiment/derived/e31/Z1, Z2, Z3; markers checked against the manifest sha256). MBP_COMPACT keeps only ts_recv, ts_event, instrument_id, flags, bid_px, ask_px, sequence: no sizes, counts, action, side or trade price for ZS/ZL. | test_measure31.py, 45 (whole file) |
| measure31.py | `load_manifest`, `guard_request`, `open_store`, `guard_chunk`, `file_sha256` | Manifest hard-check refusal, sha256 re-check, refusal of any record on or after 2024-03-01, refusal of a request touching a sealed window (`data.holdout.request_touches_sealed_window`). | The data guards a directional pipeline needs, plus the soy test-window seal (2017-05-01..2020-11-30) which E.31's guards do not name: they check data.holdout's windows, so the seal must be added. | |
| measure31.py | `definition_rows`, `read_definitions`, `root_tick`, `checked_tick`, `definitions_summary` | "The last definition of every outright future (instrument_class F) of ZM, ZS and ZL"; tick from Z4 `min_price_increment`, checked against tick value in USD. | Tick sizes for tick-normalised labels. Known issue (README_measure31.md): the USD check stops on ZS and ZL because their prices are in cents; the rule for the check is open. | |
| measure31.py | `merge_mappings`, `instrument_on`, `roll_reasons` | Continuous-symbol mapping intervals (UTC dates, end exclusive) to instrument ids; roll day and the trade date after it flagged. | Front and second-month identity per trade date; roll exclusions for labels that would span a roll. | |
| measure31.py | `grains`, `month_trade_dates`, `calendar_reason` | Grains calendar trade dates; holiday, early close and late-open reasons. | Day universe and exclusions. | |
| measure31.py | `load_usda`, `usda_coverage`, `release_trade_date`; measure31_core `usda_minutes` | USDA release instants per trade date (reports/stage_e31_briefs/research/usda_releases*.csv, covered 2020-12-01..2024-02-29); signed minutes to the nearest release. | Event-time conditioning and exclusion windows around releases. | |
| measure31_core | `regular_sessions`, `Session` | OVERNIGHT 19:00 CT (D-1) to 07:45 CT, DAY 08:30-13:20 CT. `Session.grid` is E.31's 5-minute placement grid (DAY 08:35..13:10, 56 times). | Session masks; the grid is a clock-time sampler template. | |
| measure31_core | `instrument_records`, `has_valid_start`, `max_gap_s`, `symbol_prepass` | Per-instrument records with the time axis; a snapshot clear before the first open; largest gap inside a session; day exclusion reasons. | Day-level data-quality filters. | |
| measure31_core | `InstrumentRun.commit` and `History` (`index`, `mid`) | Appends (t, best bid, best ask, valid) whenever the top of book or its validity changes, at F_LAST boundaries only. `History.index(at)` is an as-of lookup. | An as-of top-of-book series for ZM; usable for mid-based labels at fixed horizons. Tied to `InstrumentRun`, which also runs placements and fill models: it must be lifted out to be used alone. | |
| measure31_core | `CondSeries.of`, `mid_at`, `move` | "A ZS or ZL mbp-1 state series of the trade date (time axis, mid, validity, tick)"; `mid_at` = "Last valid mid at or before ``at`` from a record inside the session". Validity: both sides defined, bid < ask, no F_MAYBE_BAD_BOOK. | A minimal as-of aligner for ZS/ZL mid on the ZM clock (top-of-book mid only). | test_measure31.py |
| measure31_core | `markouts` | "markout_h = s x (mid(t_f + h) - mid0) / tick per horizon", headline (dropped at session end or on any invalid state in the window) and no-drop variants. | The template of a fixed-horizon, tick-normalised mid-change label with drop rules; the horizons are E.31's seconds (`HORIZONS_S`), not minutes. | test_measure31.py |
| canary_check31 | `TFPairing`, `TFRuns` | T and F records per instrument paired in file order (each T opens a group the following F records join). | Aggressor-signed trade volume and trade-event grouping for order-flow features. Info-only class today. | test_canary31.py, 15 |
| stats31_core | `bootstrap_weights`, `ratio_stat`, `interval`, `per_day` | Day-block bootstrap ("W[r, d] = how often trade date d is drawn in replicate r (E.28's construction)"), pooled ratios with percentile intervals. | Day-block intervals for any per-day statistic. | test_stats31.py, 29 |
| stats31_core | `imb_bucket`, `usda_bucket`, `move_bucket`, `joint_bucket` | Fixed buckets: side-adjusted imbalance, minutes from USDA release, sign of ZS/ZL move. | Bucket definitions only; directional features need continuous values. | |
| verify31.py | `Scan`, `verify_file`, `snapshot_table`, `tail_check` | File checks that produced the manifests. | Already run; nothing to redo. | |

### 6.2 Not reusable for this purpose

`kalgo31.py` (CME algorithm K fill allocation; only for passive-fill simulation),
`measure31_core.VOrder`, `Loop`, `Placement`, `InstrumentRun.fill`, `through`, `implied_check`,
`close_event`, `_k_allocation`, `touched`, `is_stale` (virtual passive orders and fill models),
`stats31.py` / `stats31_report.py` (the E.31 kill rule and report), `pull31.py`,
`pilot31_common.py` and `vol_pull.py` (purchase and spend-gate code; must not be run),
`vol_measure.py` (daily volume of QM/ZM fronts from ohlcv-1d).

### 6.3 Missing for a directional search (to be written)

1. A standalone book driver: the book-changing branch of `InstrumentRun._run_chunk` without
   placements, fill models and timers (section 5 used a 40-line replica; it should be a tested
   module) that emits book states at chosen sample times.
2. Book feature extractors on the rebuilt book: depth beyond level 1 (sum of the first k levels
   per side from `Book.prices` and `levels`), order counts per level, queue ages, add/cancel/
   trade flow over trailing windows, aggressor-signed volume (from T records; `TFPairing` covers
   only the pairing). Nothing in E.31 computes a trailing-window statistic.
3. A ZS/ZL MBP-1 aligner beyond the mid: E.31's split arrays (MBP_COMPACT) dropped the MBP-1
   sizes, counts, action, side, trade price and size, so trade flow and top-of-book size for ZS
   and ZL need a new split from the raw Z2/Z3 files (about 4 s per month per series, section 4.4).
   Also needed: as-of joins with an explicit latency (ts_recv of the context record < the ZM
   sample time), and the cross-instrument check that ts_recv clocks are comparable (same
   capture, both GLBX).
4. An event-time sampler: samples by trade count, volume, F_LAST event count or a mid-change
   rule, on the `time_axis` clock, with session masks. E.31 has only the 5-minute clock grid.
5. A label builder for minutes-scale directional targets: forward mid change (and sign, and
   triple-barrier style if Part P chooses it) at minute horizons on the ZM.v.0 as-of history, with
   session-end, invalid-book and roll-day drops, and the label end time stored for purging.
6. Purged and embargoed CV folds by trade date with label end times (V43). Nothing in E.31.
7. A feature store writer (per-day parquet with fixed schema and fingerprint) and resumable
   runner; `measure31.py` main/pool/`run_task`/`write_day_tables` are the pattern to copy.
8. The soy test-window seal guard (2017-05-01..2020-11-30) in the data guards, and the 2024-03-01
   cutoff (present).
