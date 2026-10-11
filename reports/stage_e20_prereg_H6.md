# Stage E.20 pre-registration H6: rest-of-day to last-half-hour momentum on NQ at MNQ cost

**Status: FROZEN (lead, 2026-10-11; hashed in reports/stage_e20_h6_freeze.json, commit "E.20 H6 freeze"; review reports/stage_e20_review_h6.md, rulings reports/stage_e20_rulings.md section 2).** Written from docs/prompts/STAGE_E.20.md F5 before any NQ bar was
read for this rule and before Gate 0's NQ rows were read. The only GEX value read before the freeze is
the sign count in section 6, made after T3's status was fixed (review H6R-2). It
becomes binding when hashed in reports/stage_e20_h6_freeze.json and committed ("E.20 H6 freeze"),
before the registration line exists. Nothing in it may change after the freeze; a code error found
later is fixed by finding it, never by a second evaluation.

## 1. Hypothesis (one, with a stated sign)

On NQ, the return from the previous trade date's equity close C to C-30 (r_ROD) predicts the sign of
the paper's last-half-hour return (C-30 to C), traded here from the C-30 open to the open after the
first bar at or after C-2 (Baltussen, Da, Lammers and Martens, "Hedging
demand and market intraday momentum", JFE 142 (2021) 377-403): momentum, traded in sign(r_ROD),
after the paper's sample (which ends in May 2020), at Topstep-feasible cost on MNQ.
- T1: every eligible date.
- T2: eligible dates where |r_ROD| exceeds the median of |r_ROD| over the previous 60 eligible
  trade dates (Rosa, J. Futures Markets 2022, the threshold form).
- T3: eligible dates whose previous trade date's GEX is negative (Baltussen et al.: momentum present
  when NGE is negative). Registered: the GEX source is cleared under its terms (section 7).

## 2. Data and windows

- Store: the E.12 NQ store, data/processed_step2/NQ/ohlcv-1m_NQ_v_0_2019-05-06_2024-02-29_step2.parquet,
  sha256 08fae13f8747883944888f4e7a3dd695c974707df2af59a22ef9036816be30aa (reports/stage_e17_run_manifest.json),
  read through the frozen loader with its booking checks. NQ is the price path; MNQ is the vehicle.
  MNQ and NQ quote the same index, so prices are used as read; ticks and dollars are MNQ's
  (tick 0.25 index points, $0.50).
- Verdict window: trade dates 2020-06-01..2024-02-29 of the frozen equity group calendar.
- T2 warm-up: the 60 equity trade dates before 2020-06-01 (their r_ROD values may feed T2's
  median for verdict dates; nothing else). For a verdict date d, T2's threshold uses only eligible
  dates in [the 60th trade date before 2020-06-01, d). If fewer than 60 eligible dates lie there,
  d has no T2 threshold and no T2 trade (counted "t2_warmup").
- Descriptive overlap window (never in the verdict): 2019-05-06..2020-05-29, the store's dates
  inside the paper's sample, evaluated by the same rules (T2's threshold there from eligible dates
  since 2019-05-06 only; T3 likewise).
- Never read: anything under data/processed_hist/ or data/sealed/, the holdout stores, any other
  root's store, any bar dated 2024-03-01 or later, reports/stage_e12_gate0.md and .json (until this
  evaluation is complete).

## 3. Rule (every parameter fixed)

Clock (CP1's conventions, docs/STAGE_E_DESIGN.md D6 CP1 row and strategy/members/k1/cp1.py): a bar is
named by its CT open minute and closes one minute later; the frozen engine decides at a bar's close
and fills a market intent at the open of the next bar.
- C: the equity group's close on that trade date: 15:00 CT on a normal day; the early close on a
  shortened day (the frozen equity calendar's early-halt time).
- P(C-30): the close of the bar ending at C-30 (the bar opening at C-31; 14:29 on a normal day).
- P(prior C): the close of the bar ending at the previous equity trade date's C (the bar opening at
  that date's C-1; 14:59 on a normal day, the early close minus 1 minute on a shortened day).
- r_ROD = P(C-30) / P(prior C) - 1.
- Eligible date: a trade date of the window on which both bars exist and carry one instrument_id,
  and r_ROD != 0. A date failing any condition has no trade, is not eligible, and is counted by
  reason ("missing_signal_bar", "missing_prior_bar", "instrument_change", "zero_signal").
- Entry: market intent on the bar ending at C-30, in sign(r_ROD) (buy if r_ROD > 0, sell if < 0),
  one MNQ, filling at the next bar's open (C-30).
- Exit: market intent on the first present bar at or after C-2 (opening at or after C-2; 14:58 on a
  normal day), filling at the next bar's open. The engine's forced flatten at F (15:08 CT on a
  normal day) and its D9.7 price-limit exit are backstops.
- Shortened days: the frozen engine's F on an early-close date is the early close minus Topstep's
  lead, 30 minutes for 2019-2025 (rules/sessions.py TOPSTEP_EARLY_CLOSE_LEAD, Rule H-1 derived rows
  for 2019-2023), so F = C-30, the entry fill time. The engine therefore refuses every shortened-day
  entry (engine_flatten_window): such a date can be eligible (its r_ROD feeds T2's median) but
  carries no trade and zero P&L, counted as an engine refusal. (33 of the verdict window's 971
  equity trade dates are shortened, per the build's calendar test; no bar was read for that count.)
- Engine runs: one run per test and per window, each with its own account (T1, T2 and T3 never
  share an MLL path). Each run's frames begin one equity trade date before the window's first date
  (a lead-in date with no entry, which gives the engine its D9.7 prior-settlement reference for the
  first window date); where the store has no earlier date (the overlap window's 2019-05-06), none.
- Through the frozen engine, unchanged: the D8 MNQ costs per 30-minute bucket (commission plus
  the entry and exit buckets' one-side slippage, the event-window rule), the D9.5a fill guard, the
  D9.12 CPI window, D9.7's price-limit rules and locked-market fills, the 2-minute minimum hold,
  the XFA 50K scaling gate, the trailing MLL with restart on a terminal account (a breach does not
  end the sample; breaches are counted and reported), and the refusal of an entry on MNQ's own
  roll-blackout dates (the frozen set the v2 engine stage uses for MNQ: its root's and its price
  path's). Every engine refusal of an eligible date's entry is counted by reason; that date has no
  trade and zero P&L.
- T2's threshold for date d: the median of |r_ROD| over the 60 most recent eligible dates before d
  (within the ranges of section 2); d is a T2 date iff |r_ROD(d)| > that median (strictly).
- T3 (if registered): d is a T3 date iff the GEX value in the row dated the previous equity trade
  date of d is negative (strictly). A previous trade date with no GEX row gives no T3 trade
  (counted "gex_missing"). The row for date x is published after the cash close of x (E.14's
  timing record: Last-Modified 16:57 CT on the row's date), before d's entry. The day after a
  futures-only holiday session (Memorial Day, Labor Day, MLK Day, Presidents' Day, Juneteenth,
  Independence Day, Thanksgiving, Good Friday) has no GEX row for its previous trade date, so it is
  "gex_missing": about 7 to 8 verdict dates a year (review H6R-4); this is the literal reading of
  F5's "previous trade date's GEX", not a data defect.
- Nothing is fitted or tuned. No window, threshold or lookback exists other than those above.

## 4. Statistic (per test)

- Per trade i: gross_i = side_i x (exit fill price - entry fill price) in MNQ ticks; c_i = the D8
  round trip the engine charges that trade, in MNQ ticks; net_i = gross_i - c_i; dollars at $0.50 a
  tick, one MNQ.
- One trade a day at most, so the per-date net P&L is net_i.
- t_B and the one-sided p: ml_route_v2.gate0._b_test (the frozen code C1 used), given the test's
  trades with g_ticks = net_i, cost_ticks = c_i and trade_date; t_B is the date-clustered t over the
  dates with a trade and p its one-sided p-value as _b_test computes it.
- Annualized net Sharpe: the daily net P&L in dollars over every equity trade date of the verdict
  window (zero on a date with no trade), mean over sample standard deviation (ddof 1), times
  sqrt(252).
- Mean gross per trade: the mean of gross_i; the cost bar compares it with 1.5 x the mean of c_i.

## 5. Pass bar (fixed)

A test PASSES iff all hold:
1. its one-sided p is rejected by Holm's step-down at family alpha 0.025 over the registered H6
   tests (m = 2, or 3 if T3 is registered): sort ascending, reject p_(k) <= 0.025 / (m - k + 1) for
   k = 1, 2, ... until the first non-rejection;
2. mean gross per trade >= 1.5 x mean c (c = each trade's D8 round trip);
3. at least 100 trades (30 for T3);
4. annualized net Sharpe >= 0.5.
Otherwise it FAILS. A test whose run cannot complete for a reason this text names (a loader
refusal or an engine invariant error after the marker) is STOPPED, with the rule quoted; a STOPPED
test enters the Holm family with p = 1 and m unchanged.

## 6. Descriptive outputs (never in the verdict)

Per-year results (2020-06..12, 2021, 2022, 2023, 2024-01..02); the 1.5 x slippage stress (each
side's slippage x 1.5, commission unchanged); gross and net per trade in bp of the entry price
(points / entry fill price x 10^4); trade counts by exit type (C-2 exit, forced flatten, D9.7,
MLL breach flatten); refusal and exclusion counts by reason; MLL breach dates; and the
2019-05-06..2020-05-29 overlap with the paper's sample, reported separately. Power for the record:
at the paper's per-day Sharpe of 0.055 to 0.11 on about 930 dates, the expected t is about 1.7 to
3.4 before decay. T3: the GEX CSV holds 148 rows with GEX < 0 dated 2020-05-29..2024-02-28 (a count
of the conditioning variable's sign, made by the lead at 10:56:48 PDT on 2026-10-11, after T3's
status was fixed and before any NQ bar was read; no price was read; the count reads the CSV's date
and gex columns: rows dated 2020-05-29..2024-02-28 with float(gex) < 0, over E.14's file sha256
51bef9ea...; 944 rows in that range; 42 rows with GEX < 0 dated 2019-05-03..2020-05-28), so T3 has at
most about 148 dates and an expected t of about 0.7 to 1.3 at the same per-day Sharpe (higher if the
negative-gamma effect is as much stronger as the paper's S&P result).

## 7. T3 and the GEX source

- Ruling (ProductReader-NQ-OpusHigh, reports/stage_e20_briefs/product_NQ.md section 4c, before any NQ
  bar was read): CLEARED for one registered test. SqueezeMetrics' terms
  (https://squeezemetrics.com/monitor/terms, fetched 2026-10-11T17:34:43Z, sha256
  695c1bbd930b8930777190e1fc966b26f35fa12dcb798ed99977c0cd132c169d, byte-identical to E.14's reading of
  2026-10-05) bar "systematically retrieve data ... to create or compile ... a collection,
  compilation, database, or directory without written permission"; robots.txt is absent (HTTP 404);
  the free DIX page offers the file through its own download button. Using a file the page offers,
  once, for one registered test is not systematic retrieval; nothing is redistributed (the CSV
  stays out of git, DO_NOT_COMMIT.txt). The lead accepts the ruling.
- Copy used: E.14's download, reports/stage_e14_briefs/gex/DIX.csv (fetched 2026-10-05T07:43:01Z,
  sha256 51bef9ea5ee13af2f72b14f4198de57eeb865a36c1d3e244a3f64b3603e9ce62, header
  date,price,dix,gex, 3,880 rows, 2011-05-02..2026-10-02). No new download. Rows dated 2024-03-01 or
  later are cut at load and never used.
- T3 is registered: m = 3 in section 5's Holm family; N 480 -> 483.

## 7a. Differences from the published rules (F5 binds; disclosed, not changed)

From the NQ reader's comparison (product_NQ.md section 4b):
- Exit: the paper's last half hour ends at the 15:00 CT close price; F5's exit fills at the open of
  the bar after the first bar at or after C-2 (about 14:59 CT), so the final one to two minutes of the
  paper's window are not held.
- Early-close days: the paper removes them; F5 sets C at the early close, and the frozen engine's
  flatten falls at C-30 on those days (section 3), so they carry no trade: the outcome matches the
  paper's exclusion, by the engine rather than by the rule.
- T2: Baltussen et al. have no threshold. Rosa (J. Futures Markets 2022) thresholds the overnight
  return, not r_ROD, by a rule whose value and lookback could not be verified (full text closed to
  automated access; abstract only). T2's median over the previous 60 eligible dates is the planning
  brief's variant ("trade only when |r_ROD| is above its trailing median"), fixed by F5; neither the
  median nor the 60-date lookback comes from either paper.
- T3: the paper's gamma result is for S&P 500 futures with NGE (net gamma over market value);
  SqueezeMetrics' GEX is an S&P 500 options construction in dollars, applied to NQ. Both tests use
  only the sign.
- Prices and execution: the paper trades at the signal price with no spread; F5 enters at the next
  bar's open with D8 costs.
- Prior close after an early-close day (review H6R-3): the paper removes early-close days, so its
  prior close for the next day comes from the last retained day (not stated); F5 uses the early
  close as C, so on the day after a shortened day P(prior C) is the close of the bar ending at the
  early close and r_ROD spans the half session (about 33 verdict dates).
- Roll (review H6R-3): the paper rolls on the next contract's volume crossover; the E.12 store
  rolls by its own rule, F5 makes the roll date ineligible (instrument_change), and the engine
  refuses entries on the vehicle's roll-blackout dates; the paper's series has a return there and
  F5's has none.
- Shortened days in T2's median: they are eligible and feed T2's median although their |r_ROD|
  spans a shorter day (on the 08:15 CT Good Friday halts of 2021-04-02 and 2023-04-07 the signal bar
  opens at 07:44 CT); the paper's exclusion avoids this.

## 8. Trial count and registration

Registered after the freeze commit and before the evaluation: N 480 -> 483. The prompt's names
E20-H6-T1, E20-H6-T2, E20-H6-T3 are registered as label E20H6 with ids E20H6-T1, E20H6-T2, E20H6-T3,
because the frozen registry (screening/trial_registry.py) allows no hyphen in a label. The registration carries the
freeze manifest's sha256. The evaluation runs once, behind reports/stage_e20_H6_RUN_ONCE.json. A pass is
a candidate, not a strategy: it leads to the forward research-window read and then holdout-2, each
in its own stage, and to no Combine (docs/DECISIONS.md V33 item 1).

## 9. Guard

Every H6 process imports h6_rod's read guard. It raises on any path under data/processed_hist/,
data/sealed/ or a holdout store, on any store path other than the NQ store above, and on any bar
dated 2024-03-01 or later. Tests plant each case and show it raises.

## 10. Order of events

1. This text and h6_rod/ with its tests (synthetic bars only).
2. H6Reviewer-FableXHigh: the text against F5, the rule against the papers, the code against the
   text; BLOCKING and SHOULD FIX fixed.
3. Section 7 filled from the NQ reader's ruling; T3's status fixed.
4. Freeze manifest reports/stage_e20_h6_freeze.json; commit "E.20 H6 freeze".
5. Registration (N 480 -> 482 or 483).
6. Evaluation once; verdict per section 5; descriptive outputs.
7. VerdictVerifier-FableXHigh recomputes independently.
