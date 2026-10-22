# Stage E.29: measured reference correlations, CL / ZM / GC / NQ front contracts

Reference only, never a model input (reports/stage_e29_model.md section 8). Facts only: no placement on the
model's rho grid here (the lead does that). Worker CorrMeasurer-OpusHigh, run 2026-10-21 19:27:49-19:27:53 PDT
(times from `date`). Script: reports/stage_e29_briefs/work/corr/corr_stats.py (nice 10, one process, 1.7 s);
tables rendered from E29_correlations.json by work/corr/write_md.py. Per-date daily series (front id, close,
high, low, main-session open/close, roll flag) are in work/corr/daily_<ROOT>.csv.

ZM is owned (data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0), so no soybean-complex substitute was used.

## Data rule and guards, as applied

- Files chosen by name only: <ROOT>_v_0/range=<a>_<b>.dbn.zst with a >= 2022-10-01 and b <= 2023-11-01
  (A0's rule: range=2023-10-01_2023-11-01 is the last file that may be opened; the 2022-10 file is opened only
  for the 2022-10-31 prior close and for trade date 2022-11-01's Sunday-evening bars). 13 files per root, 52 in
  all. No file dated 2023-11-01 or later was opened (the 2023-11 and 2023-12 files exist on disk and were
  skipped by name; the 2024-03+ gap is absent from the folders).
- open_store (copied from A0, extended) refuses before opening: a name outside that range, a root other than
  CL/ZM/GC/NQ, and any resolved path containing mbp-1, sealed, processed, holdout, embargo, research or /MES, or
  not under /ohlcv-1m/. Paths resolve to /mnt/large-storage/market_data/PropExperiment/... (the E.26 data move).
  None was refused; the 60-second missing-file retry never fired.
- Nothing written under data/. No network, no Databento API, no keys. Holdout status checked immediately before
  and after the run (bottom of this file): all_ok true and unlocks_logged 0 for holdout 1 (printed as `<top>`,
  the report's top-level keys) and for holdout_2 and each of its products, both times.

## Method

- Trade date (A0 copy): bar start in America/Chicago; at or after 17:00 CT it belongs to the next day; Saturday
  and Sunday roll to Monday. Window: trade dates 2022-11-01..2023-10-31.
- Front contract per trade date: within the v_0 series (Databento's volume-ranked continuous front), the
  instrument_id with the largest summed one-minute volume on that trade date (ties broken to the lower id).
  Only that instrument's bars are used for the day. The v_0 file holds one instrument per bar,
  so this is the highest-volume outright among the instruments the v_0 series carried that day, not a scan of
  every listed expiry. A roll date is a trade date whose front id differs from the previous owned trade
  date's; roll dates are dropped from returns, ranges and main-session returns.
- Daily close: close of the front contract's last bar of the trade date (not the CME settlement). Daily return:
  ln(close_t / close_prev) where prev is the previous kept trade date of that root, computed only when both days
  have the same front id (no return across a roll). The day after a roll uses the roll day's close of the same
  new contract. The return on 2022-11-01 uses the 2022-10-31 close.
- Daily range: (high - low) / close x 100 over all front-contract bars of the trade date (Globex day).
- Main-session return: ln(close of the last front bar starting before 13:00 PT / open of the first front bar
  starting at or after 06:30 PT) on the trade date. For ZM the session closes 11:20 PT, so its main session is
  06:30-11:20 PT (median 290 bars vs 390 for CL, GC, NQ).
- Calendars (A0 convention): primary tables exclude each root's EARLY_HALT dates (data/calendars/energy.py,
  grains.py, metals.py; data/cme_calendar.py for NQ) because the trade-date rule books holiday sessions on the
  holiday's own date. With a date excluded, the next day's return runs from the previous kept date. A variant
  with all trade dates kept is also given.
- Pairs: inner join on common trade dates with a value for both roots. Pearson (with a Fisher-z 95% interval,
  descriptive), and Spearman (Pearson of ranks). Six pairs.

## Notes of fact

- ZM's v_0 front id changed three times in December 2022 (2022-12-12, 12-14, 12-19), each dropped as a roll date.
- CL roll dates 2023-02-20 and 2023-06-19 are also early-halt dates (excluded in the primary tables either way).
- Dates with two or more instrument ids in the v_0 bars: CL 7, GC 5, NQ 4, ZM 0; on those days only the
  higher-volume id's bars are used.

