# Stage E.31 Part 1: request and measure definitions (written before any quote)

Written by the E.31 lead (Opus 5.5, xhigh) on 2026-10-22 at about 08:20 PDT, before any Databento
call of this stage and before any QM or ZM volume figure of this stage was seen. Its sha256 is
logged in reports/stage_e31_STATE.md. Binding source: docs/prompts/STAGE_E.31.md (Part 1, V1 to
V3 and the kill rules). This file copies them and fixes the details they leave open. It adapts
reports/stage_e30_request.md (E.30 was superseded before any quote, V48 item 1).

## V1 request (copied from the prompt)

- dataset `GLBX.MDP3`, schema `ohlcv-1d`, stype_in `parent`
- symbols `QM.FUT`, `ZM.FUT` (one request, both symbols)
- start `2023-01-01`; end = the `ohlcv-1d` end from the free
  `metadata.get_dataset_range("GLBX.MDP3")` call made just before the quote (the dataset-wide
  `end` if no per-schema end is returned), passed through unchanged
- nothing else: no other root, no schema other than ohlcv-1d, no date before 2023-01-01
- QM and ZM daily volume is not a sealed series. ZM's owned one-minute bars are not opened.

## V2 spend (copied from the prompt, routed through the pilot path)

- account `acct-3` only, key through `data.config.require_databento_key(account="acct-3")`;
  checked by name only, never read into a log, print or file
- acct-3's pilot-only guard (data.config.PILOT_ONLY_ACCOUNTS; data.pull_step2 and data.pull_hist
  refuse acct-3) is not changed. The purchase goes through this stage's own pilot-path script,
  reports/stage_e31_briefs/work/pilot/vol_pull.py, which uses SpendGate directly on acct-3, as
  E.28's pilot_pull.py does. No existing puller is used.
- SpendGate (data.pull_mes.RequestCappedGate) with session id `stage-E.31-2026-10-22-volume`,
  session cap USD 1.00 and request cap USD 1.00
- a fresh logged quote (`metadata.get_cost` and `get_billable_size`) first; buy only if the
  quote is at most USD 1.00 (V2) and at most acct-3's headroom. Otherwise buy nothing and record
  why.
- download to
  `/mnt/large-storage/market_data/PropExperiment/data/vendor/databento/GLBX.MDP3/ohlcv-1d/QM_ZM_parent/`
  (reached through the repo symlink data/vendor/databento) via data.pull_universe.download
  (.partial, os.link, read-only), then the record-byte check and settle as data.pull_hist does,
  then a sha256 manifest `manifest.json` beside the file

## Free metadata used after the purchase

- The DBN metadata's symbol mappings name each instrument_id's raw symbol. If any instrument in
  the file is not named there, one free `symbology.resolve(stype_in="instrument_id",
  stype_out="raw_symbol")` call over the purchased span names it.

## V3 measures, fixed details

- Root: an instrument belongs to QM or ZM by its raw symbol's leading root letters.
- Outright filter (the prompt's rule): drop every instrument whose raw symbol contains a hyphen.
  Check line, not a filter: report the count and volume of remaining symbols that do not match
  `^(QM|ZM)[FGHJKMNQUVXZ][0-9]{1,2}$`; if their volume is above 1% of a root's volume, also show
  that root's table without them.
- Day: the bar's `ts_event` date in UTC (ohlcv-1d is UTC-day aligned). Bars dated Saturday or
  Sunday are excluded, and their count and volume are reported.
- Day universe (primary, used by the kill rules): the Monday-to-Friday dates on which QM or ZM
  has at least one outright bar. A root with no outright bar on a universe date counts as volume
  0 that date (conservative: it can only lower a median). Secondary, shown beside: each root's
  own universe (only dates with its own outright bar). If the two give different verdicts, the
  primary governs and the difference is flagged.
- Daily volume per root: the sum of `volume` over that root's outrights on that date.
- Quarter: the calendar quarter of the date. Per root and quarter: day count, median and 10th
  percentile (numpy `percentile`, linear interpolation) of daily volume, and the front-month
  share = sum over the quarter of front-month volume / sum of the root's volume.
- Front month: on each date, the root's outright with the earliest delivery month among its
  outrights with a bar that date. Delivery year from the symbol's digit(s): for one digit d on a
  date in year t, the year is t - (t mod 10) + d, plus 10 if that is below t - 1; two digits are
  read as 20dd. Beside it, for information only: the share of the day's highest-volume outright.
- The last quarter is marked partial with its day count.
- Prices are not loaded, used or reported. Only `ts_event`, `instrument_id` and `volume` are
  read, plus the symbol mappings.

## Kill rules (copied from the prompt), window fixed

- Window: the last 12 full calendar months available, meaning the 12 calendar months ending with
  the latest month whose last day is before the data end (the end is exclusive). With an end of
  2026-10-21 or 2026-10-22 that is 2025-10-01 to 2026-09-30.
- QM: median daily volume over the window (primary universe) below 1,000 contracts = FAIL. If QM
  fails, the frozen E.28 QM pilot (reports/stage_e28_pilot_spec.md) is closed for good.
- ZM: median daily volume over the window below 5,000 contracts = FAIL. If ZM fails, the stage
  stops before Part 4, buys nothing more, and reports.
- The medians use numpy `median` over the window's universe dates. Nothing else enters a verdict.
