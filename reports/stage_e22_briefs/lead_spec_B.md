# Stage E.22 Part B lead spec: the micro trend book (design study) and its forward rule

Written by the E.22 lead (Opus 5.5, xhigh), 2026-10-16 ~01:15 PDT, against docs/prompts/STAGE_E.22.md
Part B (B1-B5). This is a DESIGN AND FEASIBILITY study, not an edge test: no p-value, no verdict, nothing
added to N by the historical figures. The only N change in Part B is the E22-F1 forward registration
(N 532 -> 533), written by the lead after the code exists.

## S0. Hard boundaries (every Part B worker)

- Data: only owned stores, only trade dates 2010-07-01..2024-02-29, only through base_rules' loader
  (base_rules.store.load_product and its preflight; it refuses dates after 2024-02-29). Never read
  data/processed/ (the research window 2025-04-01..2026-06-19 is out of bounds for Part B), never any
  sealed store, never anything dated 2024-03-01 or later. No Databento call, no web market data, no
  purchase. CME's website is never fetched by automation.
- Roots read (all are E.21 roots whose step 2 and ext2010/ext2010h stores E.21 already read, verified
  in reports/stage_e17_run_manifest.json): NQ, RTY, GC, CL, NG, 6E, ZT, ZN, ZB, ZC, ZS, ZL. Optional
  sensitivity only: TN, UB (also E.21 roots). NO other root is read in Part B (in particular not 6A,
  6B, 6C, 6J, 6N, 6S, HG, MHG, MGC, MBT, ZW, ZM, YM, MES: some are Part A confirmation-window data that
  E.21 never read; see S1).
- Do not edit base_rules/, multiday/, screening/, sim/, rules/, data/, live/, ops/, any freeze, any
  ledger, REGISTRATION.md. New code only in microbook/ (the historical study) and forward/ (the rule
  core and the paper runner), tests in tests/test_microbook_*.py and tests/test_forward_*.py.
- Compute: nice -n 10, check `free -m` first, at most one heavy job per worker, resumable outputs.

## S1. Universe (B2) and price paths

Modelled (12): each micro on an owned E.21 price path, with the micro's own multiplier, tick and cost.

| Micro | Exposure | Owned price path | Notes |
|---|---|---|---|
| MNQ | Nasdaq-100 | NQ | "MES or MNQ": MNQ, since ES/MES has no owned 2010-2024 path |
| M2K | Russell 2000 | RTY | path starts 2017-06-01 (base_rules START_EXCEPTIONS) |
| MGC | Gold | GC | |
| MCL | WTI crude | CL | |
| MNG | Henry Hub gas | NG | MNG (1,000 MMBtu, E.13 C2/T-28); QG not used |
| M6E | EUR/USD | 6E | |
| 2YY | 2-year yield | ZT | yield proxy (S3.6) |
| 10Y | 10-year yield | ZN | yield proxy (S3.6) |
| 30Y | 30-year yield | ZB | yield proxy (S3.6) |
| MZC | Corn | ZC | micro grain specs from E.13 C2 (T-28); if absent there, flagged UNSOURCED |
| MZS | Soybeans | ZS | as above |
| MZL | Soybean oil | ZL | as above |

Not modelled (listed in every table as "not modelled", with the reason):
- SIL (silver): no owned silver path (SI not owned).
- MHG (copper), M6A, M6B, MCD, MJY, MZW, MZM: their only owned paths (HG/MHG, 6A, 6B, 6C, 6J, ZW, ZM
  step 2 stores, 2019-05..2024-02) were never read by E.21 and are confirmation-window data of Part A's
  clusters (K3 FX, K5 metals, K6 grains); this design study does not touch them before those
  confirmations. A later supplement may add them from 2019-05 (lead's open choice; not tonight's
  main tables).
- MES: no owned 2010-2024 path (only MES's Stage D 2019-2024 store, a Part A leg).
Multipliers, tick sizes and tick values come from E.13's sourced C2 table (reports/stage_e13_trend_carry.md
lines 214-271, source T-28) or the program's frozen vehicle constants; each row cites its source; an
unsourced figure is flagged UNSOURCED, never invented.

## S2. Prices

- Daily mark: base_rules' settlement mark (common.settle_point), as E.21's daily.py builds it (MK).
- Signal series: a back-adjusted (chained) price series built from the per-contract path, rolled at
  each store splice exactly as E.21/base_rules roll (reuse multiday.daily / base_rules functions; do not
  copy-edit them). Known quirks (memory, E.21): the equity calendar books US holidays as trade dates
  (drop dates with no new mark); ZC/ZL/ZS/LE/HE have consecutive-weekend-day roll pairs with no bar
  between them; handle so no NaN propagates and log the count of affected dates.
- Sizing price: the held contract's own mark (not back-adjusted).

## S3. The rule (B1), from Carver's published method; every constant cited

1. Price volatility for the EWMAC denominator: EWMA standard deviation of daily price differences of
   the back-adjusted series, Carver's span (pysystemtrade defaults; cite the file and line).
2. EWMAC(f, s) for (8,32), (16,64), (32,128), (64,256): raw = (EWMA_span=f(P) - EWMA_span=s(P)) /
   sigma_price; scaled = raw x forecast scalar (Carver's published scalars for these four speeds;
   cite); capped at +-20. Report the realized pooled mean |scaled forecast| per speed against 10.
3. Combined forecast = equal-weight mean of the four capped forecasts x FDM, capped at +-20.
   FDM = 1 / sqrt(w' H w), H = correlation matrix of the four scaled forecasts pooled across the 12
   instruments over the full study span, negative correlations floored at 0, capped at 2.5 (Carver's
   formula; cite). Computed once, reported, and frozen as a constant for E22-F1.
4. Instrument risk: annualized percentage volatility sigma_% = 16 x daily % return std, Carver's blend
   of a recent EWMA and a long-run average (the 0.7/0.3 "proportion_of_slow_vol" and spans as his
   defaults give them; cite). Use only data up to and including the decision date.
5. Unrounded position (contracts) on date t, instrument i:
   N_i = (F_i / 10) x C x tau x IDM x w_i / (M_i x P_i x sigma_%,i), tau = 0.20 (the prompt),
   C = capital (fixed, no compounding), w_i = 1/n over the instruments live on date t, M_i = micro
   multiplier, P_i = held contract's price. IDM = 1 / sqrt(w' H w) on the correlation of instrument
   subsystem returns (unit-risk positions), floored at 0, capped at 2.5 (Carver's formula; cite);
   full-span estimate frozen as a constant for E22-F1; for dates with fewer live instruments use the
   same formula on the live sub-matrix.
6. Yield proxies (2YY, 10Y, 30Y): build a proxy yield series y_t (bp) from the note/bond futures
   path: dy_t = -dP_t / PVBP_t, PVBP_t = P_t x D_i / 10,000 in price points per bp, with a declared
   modified duration D_i per tenor (ZT 1.9, ZN 6.5, ZB 15.0; flagged "declared approximation, UNSOURCED").
   EWMAC runs on y; one micro contract moves $10 per bp (E.13 T-28, "$10 DV01"); sizing uses the $ vol
   per contract = 10 x 16 x std(dy in bp). Every table shows the book with and without the three
   proxies at $25K.
7. Positions are computed from data through settle(t) and traded at settle(t+1) (the next settlement),
   for every method; P&L from t+1 on. Rolls: at each store splice the held position rolls (two fills
   per contract, D8 costs).

## S4. Rounding (B2)

- Reference: the unrounded (fractional) book, traded at settle(t+1) with the same fill and cost rules
  (costs on fractional contracts, pro rata).
- (a) Simple rounding: Carver's rounded baseline as his October/November 2021 posts define it
  (reports/stage_e22_briefs/carver_sources.md, written by CarverReader tonight; if he applies his
  position buffer to the rounded baseline, do the same; if the posts are silent, round half away from
  zero with no buffer, and say so).
- (b) Carver's greedy minimum-tracking-error dynamic optimisation, the November 2021 version (with
  costs and the tracking-error buffer), implemented from his published description as quoted in
  carver_sources.md; every parameter (shadow cost, buffer, covariance estimate) as he states it,
  cited. Where his description and pysystemtrade's code differ, follow the post and note the
  difference.

## S5. Capital levels and outputs (B3), all descriptive

Capital levels $10,000, $25,000, $50,000 (main) and a sweep $10K, 15K, 25K, 35K, 50K, 75K, 100K,
250K (Sharpe loss vs unrounded per method: "the capital each size needs").
Per capital level x method (unrounded, simple, optimised), on the daily net $ P&L series:
- annual mean $, annual sd $ and as % of capital (against the 20% target), Sharpe gross and net,
  net Sharpe loss against unrounded, correlation of daily net P&L with the unrounded book;
- turnover (contracts per year, round turns per year), cost $ per year, cost as % of capital and in
  Sharpe units, at D8 (S6);
- realized max drawdown ($, % of capital) and its date range; expected and worst 1-year max drawdown
  from a circular block bootstrap of the daily net series (block 21 days, 10,000 resamples of 252
  days, seed 20261016; expected = mean, worst = 95th percentile; also report the 99th);
- share of instruments held at zero (mean over days of the fraction of live instruments with 0
  contracts; per instrument % of days at 0);
- margin: daily sum of IBKR initial margin x |contracts| (mean, 95th percentile, max, as % of capital)
  where reports/stage_e22_briefs/ibkr_margins.json (DataSourceReader, tonight) has a sourced rate;
  instruments without one are listed "margin not sourced".
Per instrument: path, span used, multiplier and source, cost per round turn ($ and in Sharpe units,
Carver's 0.01 SR test reported, not applied), Carver's minimum capital (his published formula,
E.13 Part B), mean |forecast|, % days at zero per capital level and method.
Sensitivities at $25K only: without yield proxies; and, if time permits, with MTN/MWN on TN/UB
paths in place of 10Y/30Y.
Every output states: "These figures re-use data E.21 already read (2010-07..2024-02); they are a
design study and not evidence of edge." No p-value anywhere.

## S6. Costs (D8)

Per contract per side: the frozen D8 tables through base_rules.costs where the micro is a frozen
vehicle there (MNQ, M2K, MGC, MCL): the settlement-time bucket's base case. For micros without a
frozen D8 table (MNG, M6E, 2YY, 10Y, 30Y, MZC, MZS, MZL): a declared "D8 extension": D8's commission
for a micro (cite the figure from docs/STAGE_E_DESIGN.md D8 or the frozen cost inputs) plus one tick
of slippage per side; flagged in every table. Also report a stress case at 2x slippage.

## S7. The forward rule core and paper runner (B5)

forward/ holds the rule core used by both the historical study and the paper runner, so E22-F1
freezes one implementation:
- forward/core.py (MicroBookCoder): vol, EWMAC, forecast combination, sizing, simple rounding,
  greedy optimiser, the frozen constants (FDM, IDM, scalars, spans, durations, multipliers) loaded
  from forward/config_f1.json (written by MicroBookCoder from the study; the lead freezes it).
- forward/runner.py, forward/ledger.py, forward/sources.py, forward/rolls.py, forward/evaluate.py,
  forward/report.py (ForwardRunnerCoder): pluggable daily settlement source (a protocol; a CSV
  source for manual entry; a test source), state rebuilt from the ledger, paper fills at the next
  settlement with D8 costs, rolls by each micro's roll schedule (a declared per-instrument rule in a
  config file, flagged "to be checked against the exchange's published roll schedule before the
  clock starts"; CME's site is never fetched by automation), an append-only JSONL ledger with a
  sha256 chain that refuses rewrites and out-of-order dates, the E22-F1 evaluation (forward/evaluate.py:
  one-sided Newey-West t on the daily net series, lag 10, p from the normal; annualized net Sharpe
  = mean/sd x sqrt(252)) and the 6-monthly descriptive report (no p-value). Tests on synthetic data
  only; no network.
- The runner calls the strategy through one function, forward.strategy.target_positions(history,
  prev_positions, config) -> {instrument: int}, which MicroBookCoder wires to forward.core.

## S8. Lead rulings after CarverReader (2026-10-16 ~01:15 PDT; reports/stage_e22_briefs/carver_sources.md)

Made before any study figure existed; each is an Open choice in the return.
- B-R1 Forecast scalars: Carver's estimated production values for the four speeds as quoted in
  carver_sources.md (ewmac8_32 5.95, 16_64 4.10, 32_128 2.79, 64_256 1.91), not the book config set
  (5.3/3.75/2.65/1.87): they are his estimate of the scalar that gives an average absolute forecast of
  10, which is what B1 asks for. The realized mean |forecast| on our data is reported; the book set is
  shown as a one-row sensitivity at $25K if cheap.
- B-R2 EWMAC denominator: the blended volatility of his configured systems (recent 35-span mixed with
  the slow average as configured), as quoted; same estimate as sizing (S3.4), price-difference form.
- B-R3 Simple rounding (a): Carver's rounded baseline as his posts define it: rounded AND buffered
  (buffer 10% of the average absolute position, trade to the buffer edge). Halves round away from zero
  (immaterial: the posts are silent; pysystemtrade rounds half to even).
- B-R4 Greedy (b): the November 2021 post's parameters unchanged: shadow cost 250 and tracking-error
  buffer 0.0125 as published (derived by Carver at a 25% risk target; NOT rescaled to 20%, since the post
  gives no rescaling rule and a rescale would be the lead's invention; this makes the buffer relatively
  wider at 20%, the conservative direction: less trading). Correlation shrinkage only if the post
  states it (the code's 50% shrink is a code-only difference: not applied, noted). Cost deflation uses
  only data up to the decision date (the code's end-of-sample volatility is look-ahead: not used).
- B-R5 Where the post leaves a parameter unstated (for example the covariance lookback), take
  pysystemtrade's value as quoted, without look-ahead, and list it.
- B-R6 (~01:29-01:31 PDT, after MicroBookCoder's first return): the November 2021 post states correlation
  shrinking (carver_pages P-NOV21 .txt:153, "What eventually came to the rescue ... was shrinking the
  correlation matrix") without a value, so B-R5 applies: the main greedy rows use pysystemtrade's 0.5 shrink;
  the no-shrink greedy is a sensitivity row. This supersedes B-R4's "not applied" for the shrink.
- B-R7 (~01:32 PDT): E22-F1's rounding method is simple rounding (B-R3's rounded-and-buffered baseline), not
  the greedy chosen in the 01:05 draft of reports/stage_e22_prereg_F1.md (preserved as
  reports/stage_e22_briefs/prereg_F1_draft_0105.md): the historical design study showed the greedy, at the
  post's parameters, losing 0.19-0.28 of net Sharpe at $25K against 0.07 for simple rounding. A design choice
  on historical data the forward test never reads; made before the freeze and before any forward data.
