# Brief: TrendCarry-OpusHigh (Stage E.13 Task 2)

Read reports/stage_e13_briefs/research_rules.md first and follow it. Your pages folder:
reports/stage_e13_briefs/pages/TrendCarry/.

## Objective (one)
Establish, from published sources, how strong the trend-following (time-series momentum) and futures-carry
premia are after their publication and since 2010, and compute what capital a solo trader needs to run a
diversified trend-and-carry portfolio in micro and small futures, with the income and drawdown to expect,
and whether it survives a prop firm's trailing drawdown.

## Context (read by section)
- docs/DECISIONS.md lines 386-408 (V22: the income path; personal micro account after XFA payouts).
- docs/STAGE_E_ML_V2_DESIGN.md lines 47-131 (V2.0: the economics table, the ruin formula, t ~ S x sqrt(years)).
- docs/STAGE_E_ML_V2_DESIGN.md lines 143-178 (the 28 vehicles, tick values, the frozen cost wall RT_X).
- You may NOT use the program's bars or any figure measured on them. Volatilities come from published sources.

## Part A: evidence (with sources and verbatim quotes)
For each: the published Sharpe ratio (gross/net, and how costs were treated), sample period, number and kind
of markets, holding period / lookbacks, and the performance AFTER publication and SINCE 2010 (from later
papers, index data or fund records):
1. Moskowitz, Ooi and Pedersen (2012, JFE), "Time series momentum".
2. Hurst, Ooi and Pedersen, "A Century of Evidence on Trend-Following Investing" (and any later update).
3. An out-of-sample record: the SG Trend Index (or SG CTA Index, BarclayHedge/BTOP50 if SG is not reachable):
   annual returns 2010-2025, annualized return, volatility, Sharpe and worst drawdown over 2010-2025 and over
   the post-2012 period. Fund-index returns are net of fees: say so.
4. Koijen, Moskowitz, Pedersen and Vrugt (2018, JFE), "Carry": per asset class and diversified.
5. Critiques and post-publication evidence: at least Huang, Li, Wang and Zhou (2020, JFE) "Time series
   momentum: Is it there?", and any study of trend's 2010s weakness and carry's post-publication record.
Give each effect one line: "post-publication strength: <figure>, <period>, <source>".

## Part B: small-account implementation (Robert Carver)
From Carver's books' published excerpts, his blog (qoppac.blogspot.com) and his public code/config
(pysystemtrade on GitHub): minimum capital guidance for retail futures accounts, the minimum-capital formula
(contracts = capital x IDM x weight x vol target / (multiplier x price x FX x annual vol%), or his stated
version), his recommended minimum position (1 or 4 contracts), the volatility targets he uses (e.g. 20% or
25%), position rounding and buffering, dynamic optimisation for small accounts, and his instrument-choice
rules (liquidity, cost per trade in risk units, minimum capital per instrument). Quote him.

## Part C: sizing with numbers
- Instrument list: the program's 28 vehicles (docs/STAGE_E_ML_V2_DESIGN.md lines 143-172) plus the micros the
  evidence calls for: equity micros (MES, MNQ, M2K, MYM), micro treasury yield futures if listed, micro FX,
  micro gold MGC, micro silver SIL, micro crude MCL, micro copper MHG, micro Henry Hub gas if listed, micro
  grains if listed, MBT. For each, establish from a published source: whether it is listed, multiplier, a
  recent price level, and an annualized volatility (a published figure with its period: e.g. an implied-vol
  index such as VIX/OVX/GVZ, a published realized-vol table, a broker's or data site's historical-volatility
  page; use the broker's or exchange's margin as a cross-check only). Record each with its source key.
- Formula: state it (Carver's, Part B) and the vol target you use (justify from Part B; also show 15%).
- For each instrument: the minimum capital to hold one contract at the target, as a lone instrument and inside
  a diversified portfolio (state the IDM and weights you assume).
- At FOUR capital levels, $10K, $25K, $50K and $100K: which instruments can be held (at least one contract
  without exceeding the target by more than a stated tolerance), expected annual return at the post-2010
  Sharpe range from Part A (give low / mid / high; net of the program's cost wall or your stated cost
  assumption), expected monthly income in dollars, and the worst drawdown to expect (an analytic expected
  maximum drawdown for a Brownian motion with drift over 5 and 10 years, e.g. Magdon-Ismail et al. 2004, AND
  the published worst drawdown of the index in Part A). Show the arithmetic in a table, every input sourced.
- Statistical power for the user's own test: t ~ Sharpe x sqrt(years); the years needed to reach t = 2 and
  t = 3 at the post-2010 Sharpe range.

## Part D: prop-firm fit (a grid, not firm names)
Prop firms that allow swing holding use trailing drawdowns of a few thousand dollars. Do NOT wait for the venue
research: tabulate, for drawdown distances D in {$2,000, $2,500, $3,000, $4,000, $4,500, $5,000, $6,000,
$7,500} and for both end-of-day and intraday trailing:
- the daily P&L sigma a diversified trend/carry portfolio runs when it holds the minimum position (1 micro) in
  each instrument it can hold, from Part C's volatilities (state the instrument set);
- the probability of losing D before it locks or within 1 year, at the post-2010 Sharpe range, by the V2.0
  arithmetic (drifting random walk: P(ruin) = exp(-2 mu D / sigma^2) for an infinite horizon; give a finite
  horizon figure too; say that trailing makes ruin likelier and EOD trailing less so than intraday);
- the largest daily sigma that keeps that ruin below 10%, and whether one micro per instrument already exceeds
  it (the granularity problem).
State every assumption (gap risk over weekends, correlation in crises, the trailing rule).

## Output
reports/stage_e13_trend_carry.md: Parts A-D, an evidence table (effect | published Sharpe | sample | markets
| holding | post-publication | since 2010 | source keys), the sizing tables, the prop-fit table, a source list
(key T-01... | URL | fetched | page date | verbatim quote), and a closing "What this means for the program"
paragraph of at most 150 words that sticks to what the numbers show.

## Stopping rule
Done when Parts A-D are complete with sources, or a gap is marked UNSOURCED with the reason. Budget: at most
150 WebSearch calls. Do not search for prop-firm rules (other workers do that).
