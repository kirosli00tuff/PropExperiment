# Stage E.30 request and measure definitions (written before any quote)

Written by the E.30 lead (Opus 5.5) on 2026-10-21 at about 22:05 PDT, before any Databento
call of this stage and before any QM or CL volume was seen. Its sha256 is logged in
reports/stage_e30_STATE.md. Binding source: docs/prompts/STAGE_E.30.md (V1 to V4); this file
copies V1 and fixes the details V3 and V4 leave open.

## V1 request (copied from the prompt)

- dataset `GLBX.MDP3`, schema `ohlcv-1d`, stype_in `parent`
- symbols `QM.FUT`, `CL.FUT` (one request, both symbols)
- start `2023-01-01`; end = the `ohlcv-1d` end from the free
  `metadata.get_dataset_range("GLBX.MDP3")` call made just before the quote (the dataset-wide
  `end` if no per-schema end is returned), passed through unchanged
- nothing else: no MCL, MGC or other program micro, no MES, NG, MHG or holdout-2 root, no
  schema other than ohlcv-1d, no date before 2023-01-01

## V2 spend (copied from the prompt)

- account `acct-2` only; SpendGate (data.pull_mes.RequestCappedGate, a SpendGate with a
  per-request ceiling) with session id `stage-E.30-2026-10-21`, session cap USD 1.00 and
  request cap USD 1.00; key through `data.config.require_databento_key(account="acct-2")`
- a fresh logged quote (`metadata.get_cost` and `get_billable_size`) first; buy only if the
  quote is at most USD 1.00 and at most acct-2's remaining headroom under its gate cap
  (USD 1.924772 at the 22:01 start check). Otherwise buy nothing and record why.
- download to
  `/mnt/large-storage/market_data/PropExperiment/data/vendor/databento/GLBX.MDP3/ohlcv-1d/QM_CL_parent/`
  (reached through the repo symlink data/vendor/databento) via data.pull_universe.download
  (.partial, os.link, read-only), then the record-byte check and settle as data.pull_hist does,
  then a sha256 manifest `manifest.json` beside the file
- no key is read into any log, print or file

## Free metadata used after the purchase

- `symbology.resolve(stype_in="instrument_id", stype_out="raw_symbol")` over the purchased
  span for the instrument ids in the file, to name each instrument (free; no data schema).
  If the DBN metadata already names every instrument with a raw symbol, that is used instead
  and the resolve call is still made as a cross-check.

## V3 measures, fixed details

- Outright filter (the prompt's rule): drop every instrument whose raw symbol contains a
  hyphen. Check line, not a filter: report the count and volume of remaining symbols that do
  not match `^(QM|CL)[FGHJKMNQUVXZ][0-9]{1,2}$`; if their volume is above 1% of QM or CL
  volume, also show the table without them.
- Day universe: the dates (the bar's `ts_event` date, UTC) on which CL has at least one
  outright bar, Monday to Friday only. Weekend-dated bars (ohlcv-1d is UTC-day aligned, so the
  Sunday evening open may appear as a Sunday bar) are excluded and their count and volume
  reported. A day in the universe on which QM has no outright bar counts as QM volume 0.
- Daily volume per root: sum of `volume` over that root's outrights on that date.
- Quarter: calendar quarter of the date. Per quarter: median and 10th percentile (numpy
  `percentile`, linear) of QM daily volume; the median over days of QM/CL daily volume; the
  front-month share = sum over the quarter of front-month QM volume / sum of QM volume.
- Front month (QM): on each date, the QM outright with the earliest delivery month among QM
  outrights with a bar that date. Delivery year from the symbol's digit(s): for one digit d on
  a date in year t, the year is t - (t mod 10) + d, plus 10 if that is below t - 1; two digits
  are read as 20dd.
- The last quarter is marked partial with its day count.
- Prices are not loaded, used or reported (only `ts_event`, `instrument_id`, `volume` are read).

## V4 kill rule (copied from the prompt), window fixed

- Window: the last 12 full calendar months available, i.e. the 12 calendar months ending with
  the latest month whose last day is before the data end (the end is exclusive). With an end of
  2026-10-21 that is 2025-10-01 to 2026-09-30.
- QM median daily volume over that window (same day universe): below 1,000 = FAIL; 1,000 to
  3,000 inclusive = MARGINAL; above 3,000 = PASS.
