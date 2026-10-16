# microbook: Stage E.22 Part B, the micro trend book (design study) and its forward rule core

Code of reports/stage_e22_briefs/lead_spec_B.md (S0-S8) and the lead's messages of 2026-10-16
(the sigma ruling, the forward instruments, R-B6 and R-B7). A design and feasibility study: no p-value,
no verdict. **These figures re-use data E.21 already read (2010-07..2024-02); they are a design
study and not evidence of edge.**

## Modules

| Module | What it does |
|---|---|
| microbook/universe.py | The 12 modelled micros (path, multiplier, tick, cost basis, commission, sources), the not-modelled list with reasons, the MTN/MWN sensitivity micros. |
| microbook/data.py | E.21's run context from E.21's own frozen input files (re-hashed), one root at a time through base_rules' loader and preflight, multiday.daily's marks and per-contract path (imported, not edited), reduced to one frame per root; cache in reports/stage_e22_microbook/cache/. |
| microbook/config_build.py | Every constant with its value and source; writes forward/config_f1.json and forward/tables_f1.json. |
| microbook/book.py | Per-instrument series (signal, vol, $ vol, live flag, forecasts, costs), FDM and IDM estimates, the union-date grid, the daily simulation per capital and method, P&L and costs. |
| microbook/stats.py | Sharpe, annual figures, max drawdown, circular block bootstrap of the 1-year max drawdown. |
| microbook/study.py | Estimates, books (saved with a fingerprint, rerun skips them), statistics, sensitivities, diagnostics, the JSON. |
| microbook/report.py | reports/stage_e22_microbook.md. |
| microbook/run.py | The CLI. |
| forward/core.py | The rule core (pure, numpy/pandas): mixed vol, EWMAC, caps, forecast combination, diversification multipliers, positions, buffered rounding, the greedy optimiser and the November 2021 buffer, the greedy's correlation, the yield proxy. |
| forward/strategy.py | `target_positions(history, prev_positions, config)` for forward.runner, on forward.core. |
| forward/config_f1.json, forward/tables_f1.json | E22-F1's constants (DRAFT; the lead freezes them). tables_f1.json is the runner's `--tables` file (multipliers in the CSV's quote units, per-side costs, sources). |

## Commands

1. `nice -n 10 uv run python -m microbook.run load` builds the cache (the 12 roots plus TN and UB for the
   sensitivity; about 2 minutes, peak RSS 1.4 GB, one root at a time). Cached roots are skipped.
2. `nice -n 10 uv run python -m microbook.run study` writes forward/config_f1.json, forward/tables_f1.json,
   reports/stage_e22_microbook.json and .md, books under reports/stage_e22_microbook/books/ (about 25 s
   cold, 3 s from saved books). `--no-sensitivity` skips the book-scalar and MTN/MWN rows.
3. `uv run python -m microbook.run margins` re-renders everything with the margin columns from
   reports/stage_e22_briefs/ibkr_margins.json (no bar read, books reused). The study run already
   reads that file when it exists.

Tests: `nice -n 10 uv run python -m pytest -q -p no:cacheprovider tests/test_forward_core_*.py tests/test_microbook_*.py`.

## Study versus forward (lead ruling (2))

- Study: the yield micros 2YY, 10Y and 30Y run on a proxy yield series built from the ZT/ZN/ZB
  futures paths (S3.6, durations 1.9 / 6.5 / 15.0, declared, UNSOURCED), in bp, $10 per bp. Forward:
  each yield micro trades its own yield-quoted contract (price = yield in percent, multiplier 1,000
  per 1.000 = $10 per bp) and its forecast runs on its own settlement series. EWMAC, the vol and the $
  vol per contract are the same functions in both (forecasts are scale-free; $ vol = multiplier x 16 x
  daily vol of the price differences).
- Study: every micro on its full-size owned path (prices of the full-size contract, rolls at the
  owned stores' splices). Forward: the micro's own settlements, rolled by forward/rolls_f1.json.
- Study: correlation, FDM and IDM from 13 years of data. Forward: FDM and IDM frozen in
  config_f1.json; the greedy's correlation and the slow vol are estimated from whatever history the
  runner supplies (warm-up rows plus ledger rows). The strategy needs at least `warmup_diffs` (256)
  daily differences per instrument before it holds that instrument.
- tests/test_forward_core_strategy.py shows that forward.strategy reproduces the study book's integer
  targets exactly (greedy and simple) on synthetic data, and runs forward.runner for 300 synthetic days
  with the real strategy (integer positions, fills at the next settlement, a verifying ledger).

## Choices where the spec was silent (conservative option; numbered)

1. Context: E.21's input files are read from reports/stage_e21_freeze.json and each is re-hashed against
   the freeze (the same calendars, settlement table, windows, release rows and run manifest E.21 read).
   Window starts come from multiday.run.e21_starts, so M2K starts on 2017-07-10 (R-S4) rather than
   2017-06-01.
2. Marks: E.21's MK (multiday.daily.marks_of). Listed window dates without a mark (for example equity
   holidays booked as trade dates) are dropped and counted (41 to 130 per root).
3. Back-adjusted series: the cumulative per-contract path move (multiday.daily._interval, imported):
   rolled at the open of the last usable bar before each splice and the first usable bar at or after
   it, as E.21 and base_rules.sim do. Increments inside an interval are summed onto its mark date.
4. Splices with no usable bar between them form one group that keeps only its last splice. When the
   contract before and after the group is the same (a roll away and back), the group is dropped:
   no roll took place. This removed 13 (ZC), 6 (ZS), 4 (ZL) and 6 (TN) recorded splices, and left
   no failed interval in any root. (A first build that kept the later splice left 10 "contract change"
   failures in ZC/ZS/ZL.)
5. Store boundary (2019-04-30 to 2019-05-06): chained like a splice. multiday.daily.with_boundary_splice
   adds a splice when the contract changes; then daily._interval is called with the previous mark's
   day replaced by the later date, which bypasses only its era check. Positions are held across the
   boundary, and the 2019-05-01..03 move falls in the 05-06 interval. E.21 instead closed positions
   at the era end.
6. A failed interval would book P&L 0 and a signal change of 0 (counted; none remain).
7. Grid: the union of the 12 paths' mark dates (3,453 dates, 252.7 per calendar year). An instrument without
   a mark on a date carries its position and target (no fill, no order). Annualisation uses 252 (the S7
   convention).
8. Fills: the target decided at an instrument's mark t fills at its next mark (S3.7). The P&L of the
   interval to a mark is earned by the position filled at the previous mark.
9. Costs. Frozen micros (MNQ, M2K, MGC, MCL): base_rules' D8 base case at the mark bar (VehicleCost
   at the settlement bucket, event flag as base_rules sets it). Roll legs are costed at their own bars,
   as E.21 does: a long rolls by selling the old contract and buying the new one. Extension micros:
   commission/2 + 1 tick per side. The commission is the frozen cost-table figure for MNG ($1.92) and
   M6E ($1.00). The yield and grain micros have no Topstep or D8 figure, so they get $1.92 round
   turn, the largest frozen micro figure (UNSOURCED, flagged). Stress (S6, 2 x slippage): frozen =
   commission + 2 x (base - commission); extension = commission + 2 ticks.
10. Greedy cost input: the mean of the buy and sell per-side base cost at the decision mark, in USD,
    undeflated. It is the cost the backtest then charges, so there is no look-ahead (B-R4).
11. Warm-up: an instrument is live once it has 256 defined daily differences (the slowest EWMAC span).
    pysystemtrade starts at once, with min_periods 1 for the EWMAs and 10 for the vol. A later start
    avoids trading on immature estimates. The cost: each path's first year (for M2K, 2017-07..2018-07)
    is not traded.
12. Vol (B-R2): the mixed vol on the instrument's own defined differences (NaN dropped, then carried
    to its mark dates). The same estimate is the EWMAC denominator and the sizing vol.
13. FDM: weekly (W-FRI, last) scaled capped forecasts on live dates, stacked over the 12 instruments,
    Pearson over the full span, floored at 0, w = 1/4, cap 2.5. Carver's estimate is exponentially
    weighted and expanding; the spec asks for one full-span estimate.
14. IDM: the subsystem return is F/10 / ($ vol) decided at t, held over the interval after the next
    mark, x multiplier x dP. Weekly (W-FRI) sums on weeks with the instrument live. Pairwise Pearson
    needs at least 52 common weeks (else 0). Floored at 0, w = 1/12, cap 2.5. On dates with fewer live
    instruments the live sub-matrix is used (S3.5).
15. Greedy correlation (B-R5 values): returns are dP/P of the held contract (pysystemtrade's
    percentage returns; yield changes for the yield micros). Cumulated, then sampled every 7 calendar
    days in windows ending on the decision date, over 5 years (261 windows). Exponentially weighted,
    span 75, pairwise-complete, min 10, clip 0.99, missing pairs 0, then shrunk 50% toward a zero
    off-diagonal (R-B6). Re-estimated on every decision date.
16. Greedy scope: each date it optimises over the instruments that have a mark that day and are live.
    The others are carried and left out of the tracking error. An all-zero greedy result is accepted;
    the code's fallback to the prior (C-OPT:164-170, D7) is code-only, and its count is reported.
17. Halves round away from zero everywhere (B-R3), including the greedy's adjusted trades.
18. Simple rounding: the buffer is 10% of the position at forecast +10, using the same date's IDM,
    weight and $ vol.
19. The unrounded reference has no buffer; its costs are charged pro rata on fractional trades and
    rolls.
20. Series span: from the first fill of the unrounded book (2011-07-08) to 2024-02-29. All methods at a
    capital level use the same span.
21. Statistics: annual mean = daily mean x 252, sd = daily sd x sqrt(252), Sharpe = mean/sd x sqrt(252).
    Cost in Sharpe units = gross Sharpe - net Sharpe. Turnover counts trade contracts per year
    (excluding rolls), roll fills (2 x |held| per roll) and round turns ((trades + roll fills) / 2).
22. Drawdowns: realized max drawdown of the cumulative net series, with the start counted as a peak.
    Bootstrap: block starts uniform over the series with circular wrap, 12 blocks of 21 days cut to
    252, and a fresh default_rng(20261016) for each series (so every series uses the same block
    starts).
23. Share at zero: the position held after the fills, over live instruments, on series dates.
24. Margin: IBKR overnight initial (the 2026 rate) x |held| per day (fractional for the unrounded book).
    It is not rescaled to historical prices, which biases early years upward.
25. Per instrument: cost per round turn in Sharpe units = cost per round turn / median annual $ vol per
    contract. Carver's minimum capital uses the median $ vol: with ours (tau 0.20, the study IDM,
    w = 1/12) and with his report's assumptions (0.25, 2.5, 0.04).
26. Yield proxy: P_t is the held contract's mark on the same date as dP_t.
27. Book-scalar sensitivity: FDM and IDM held at the main estimates.
28. MTN/MWN sensitivity: TN/UB price paths, extension costs with the UNSOURCED $1.92 commission, IDM
    re-estimated on that set, FDM held.
29. Forward quote units (tables_f1.json "quote_units"): grains in USD per bushel or pound. CME quotes
    cents, so the operator enters cents / 100; yields in percent; the rest in the contract's quote.
30. Forward costs: frozen micros at their latest owned mark's settlement bucket (2024-02-29, mean of buy
    and sell, base). The other micros use the extension formula.
31. Forward strategy: the decision date is the latest date in the history. An instrument without a
    settlement on it keeps its position (prereg section 6). The live set for the weights and the IDM
    includes carried instruments. E22-F1 rounds with the simple method (R-B7). The greedy, kept as
    the study's comparison method, would run over today's live instruments.

## Lead rulings after the first return (2026-10-16)

- R-B6: the November 2021 post states shrinking the correlation matrix (P-NOV21 .txt:153), with no
  value. Under B-R5 the main greedy rows therefore use the code's 0.5 shrink toward a zero
  off-diagonal (config_f1.json greedy.correlation.shrinkage = 0.5). The no-shrink greedy is a
  sensitivity row.
- R-B7: E22-F1 rounds with the SIMPLE method (Carver's rounded-and-buffered baseline):
  config_f1.json rounding_method = "simple", and greedy.used_by_e22_f1 = false. The greedy code and
  its parameters stay in forward/core.py as the study's comparison method. The runner integration
  test runs with simple rounding.
- Unit check (requested with R-B6/R-B7): step 3's x and the buffer b = 0.0125 are in the same units,
  so there was nothing to fix. Both are an annualised tracking-error standard deviation as a
  fraction of capital: sqrt(dn' D rho D dn) / C, with D = multiplier x 16 x daily price-difference
  vol, equals the post's sqrt(dw' Sigma% dw) with dw = contracts x multiplier x price / capital.
  tests/test_forward_core_rounding.py pins this with a hand-computed two-instrument case.
  **Why most dates adjust to 0:** on those dates the greedy's integer optimum equals the current
  positions (x = 0; at $25K 2,882 of 3,197 dates, and 0 < x <= b on only 11). At small capital one
  contract is several % of tracking error (median 4% at $25K), so step 1 (inside the buffer)
  rarely holds, and the shadow-cost term (250 x per-side cost / capital per contract) outweighs most
  one-contract tracking-error gains.

## Open items for the lead

A. (Resolved by R-B6.) With the 0.5 shrink, the greedy's net Sharpe at $10K/$25K/$50K is
   0.07 / 0.29 / 0.31; without it, 0.25 / 0.20 / 0.37 (sensitivity rows).
B. Greedy diagnostic (report section 10b, now with the 0.5 shrink). With shadow cost 0 and no
   buffer, the greedy's tracking error to the unrounded book exceeds plain rounding's on 4% to 52%
   of sampled dates ($10K to $250K), with a median ratio of 0.97 to 1.01. Without the shrink it was
   95% and 3.55 at $250K. Cause: the one-direction greedy overshoots one of a highly correlated
   pair (10Y/30Y about 0.9 to 0.95) and cannot step back; the shrink damps this. It is the
   published algorithm, not a coding error; tests pin its steps.
C. UNSOURCED inputs: the yield and grain micro commissions ($1.92 round turn declared) and the
   yield-proxy durations.
D. The forward warm-up history (at least 256 settlements per micro; the slow vol uses up to 10
   years) has no source yet. The runner accepts warm-up rows.
