# Brief: DataCoder-OpusXHigh (Stage E.33, pipeline A data layer)

You are a worker (Opus 5.5, xhigh) for the E.33 lead. Do not spawn workers. Do not use AskUserQuestion: decide
conservatively, log it, continue.

## Objective
Write and test the data layer of pipeline A: guard33.py, data33.py, cal33.py; run the ZS/ZL full re-split; check
E.31's ZM split store; write the G6 clock report. Five other coders start at the same time and code against the API
below, so deliver in this order and announce each in reports/stage_e33_briefs/work/DataCoder_progress.md (one line
per milestone with `date` time): (1) guard33 + its dry-check CLI (target 30 minutes), (2) data33 loaders, (3) cal33,
(4) the split (run), (5) the G6 report.

## Read first (by section; context hygiene)
- reports/stage_e33_briefs/INTERFACE.md (all; its section 2 rules bind you)
- Protocol reports/stage_e32_discovery_protocol.md: 0.3, P1.1, P1.2, P1.4, P3.6 rules 3-5, P4 G2 and G6, P4 C.7,
  C.10, C.15, P4.1 LT4 and LT6 (grep -n headings, read ranges)
- reports/stage_e32_data_facts.md sections 1, 2, 4.3, 4.4, 6 (grep -n "^#" for line ranges)
- reports/stage_e31_briefs/work/pilot/README_measure31.md and measure31.py: split_file, compact, day_bounds,
  MBO_COMPACT, MBP_COMPACT, load_manifest, guard_request, open_store, guard_chunk, read_definitions, root_tick,
  checked_tick (and the known ZS/ZL USD-check issue), merge_mappings, instrument_on, roll_reasons, grains,
  month_trade_dates, calendar_reason, load_usda
- data/calendars (grains), data/cme_calendar.py, data/hist_calendar.py (program calendars; read only)
- reports/stage_e32_briefs/seal/soy_test_seal.py (window, paths), docs/soy_test/SOY_TEST_MANIFEST.json (keys only),
  reports/stage_e32_briefs/seal/derived_unsealed_files.tsv

## Deliverables (all under reports/stage_e33_briefs/work/pipeline/, tests in pipeline/tests/)
1. guard33.py. Every E.33 real-data read goes through it. It raises on everything P1.2 refuses: any path under
   data/sealed/SOY_test_v1 (resolve symlinks); any ZM, ZS or ZL data dated 2017-05-01..2020-11-30 (by requested trade
   date and by any date span readable from a file name); any date on or after 2024-03-01; any path listed in
   derived_unsealed_files.tsv; any market data other than the 156 discovery files of manifest 09396842..., E.31's
   per-day split store /mnt/large-storage/market_data/PropExperiment/derived/e31/Z1 (ZM MBO) and the E.33 DERIVED
   tree; anything under reports/stage_e31_briefs/work/pilot/runs/. API: check_path(path), check_date(D),
   check_request(path, first_date, last_date). A CLI `uv run python reports/stage_e33_briefs/work/pipeline/guard33.py
   dry-check` that tries one sealed test-window path, one test-window date (e.g. 2019-03-05), one 2024-03-01 date and
   one E.31 runs/ path and prints each refusal verbatim (the lead quotes it at the A1 gate), then exits 0 only if all
   four were refused. LT6 tests (pipeline/tests/test_guard33.py): one test per refused class, plus allowed cases.
2. data33.py (all loaders call guard33 and take cutoff_ns=None, truncating at ts_recv <= cutoff_ns):
   - load_zm(D, cutoff_ns=None): the E.31 Z1 per-day split records of D (MBO_COMPACT fields, all ZM instruments).
     Before relying on the store, check it against the raw Z1 files on 3 dates (equal record counts per date, P1.1)
     and record the result in your progress file.
   - load_mbp1(root, D, cutoff_ns=None), root in {"ZS", "ZL"}: from the E.33 split (deliverable 3).
   - definitions(cutoff_ns=None): all Z4 definition records in ts_recv order with the fields the features and labels
     need (instrument_id, raw_symbol, expiration, high_limit_price, low_limit_price, min_price_increment, ts_recv,
     ts_event, and any others you judge useful).
   - Document whether records come back in ts_recv order; count ts_recv decreases in file order per feed on 3 dates
     and report (P0.3, LT4: ordering uses ts_recv). If files are not in ts_recv order, the loader returns a stable
     ts_recv sort and says so.
3. The ZS/ZL split: per trade date, every MBP-1 field of every record (ts_recv, ts_event, rtype, publisher_id,
   instrument_id, action, side, depth, price, size, flags, ts_in_delta, sequence, bid_px_00, ask_px_00, bid_sz_00,
   ask_sz_00, bid_ct_00, ask_ct_00) to DERIVED/split/{ZS,ZL}/<YYYY-MM-DD>.npy, window [D-1 16:00 CT, D 16:00 CT)
   (measure31.day_bounds), the 816 dates, a DONE marker per date, a manifest (source file sha256 from the manifest,
   per-date record counts). Resumable, nice 10, at most 3 processes, `free -m` checked first. Not between 15:30 and
   16:00 PDT: if it cannot finish by 15:28, start it at 16:00 or later. Check per-date counts against an independent
   raw count on 3 dates.
4. cal33.py: the calendar API. Other coders already code against these names; you may add functions, never rename:
   trade_dates(), burn_in(), oof_dates() (P1.4: 816, 20, 796); day_bounds(D); ct_ns(D, "HH:MM:SS") (CT wall time on
   D to UTC ns, DST-aware); fronts(D) -> {"ZM", "ZS", "ZL": instrument_id} (P0.3: ZM.v.0, ZS.v.0, ZL.v.0 on UTC date D
   via measure31.instrument_on and the manifests' symbology); excluded(D) -> (bool, reasons) (P1.4: ZM roll date and
   the trade date after it; early close and scheduled late open via measure31.calendar_reason; print the counts by
   reason, computed by the rule); segment_id(D) (P4 G2: maximal runs of trade dates with the ZM, ZS and ZL fronts
   unchanged); releases(D) -> sorted list of release instants R in UTC ns (P3.6 rule 3 with its parse rule; assert
   39 WASDE, 39 Crop Production, 4 Crop Production Annual, 13 Grain Stocks, 3 Prospective Plantings, 3 Acreage,
   37 NOPA rows plus 2 NOPA rule dates, print them, raise on any other count); limits(D) -> (HL, LL) or None (P3.6
   rule 5: the front's last definition record with ts_recv <= 08:30:00 CT on D, one as-of pass over the Z4 files in
   ts_recv order with state carried across files and dates; UNDEF_PRICE (2^63 - 1) or 0 in either field -> None;
   count the None dates); expiry_trade_dates(D) (for C.7: trade dates from D to the expiration of the ZM front of
   D per its last definition with ts_recv <= 08:30:00 CT on D; document the counting convention as a READING);
   monday_or_after_closure(D) (C.10); jja(D) (C.15); tick(root) (P0.3, checked_tick with E.31's ZS/ZL fix as
   README_measure31.md describes). Prices stay Databento fixed-point int64 (1e-9 units) unless the docstring says
   otherwise. Unit tests for each function in pipeline/tests/test_cal33.py.
5. G6 clock report: per month, the median, p1 and p99 of ts_recv - ts_event for ZM, ZS and ZL side by side; flag any
   month whose medians differ by more than 100 ms; write reports/stage_e33_briefs/work/G6_clock_report.md (a data
   check; no outcome is involved).

## Boundaries
No features, labels or models (other workers'). Do not read reports/stage_e33_briefs/work/implB/. INTERFACE.md
section 2 rules apply (no Databento call, no edits under data/ screening/ etc., no package installs, no git writes).

## Return
The paths written, a summary of at most 200 words (include the guard dry-check output lines, the ZM split check, the
split's record totals, the asserted release counts, the P1.4 exclusion counts, the None-limit date count), what is
unfinished, and reports/stage_e33_briefs/work/DataCoder_readings.md.
