# Stage E ML route v2: a quant-style portfolio model (design draft)

**DRAFT. Nothing in this file is frozen, hashed or registered.** Written by the Stage E.11 lead
(Opus 5.5, xhigh) on 2026-10-03 for the user's review, before any training data is bought and
before any model is fit. A later session freezes it after the user's decisions (V2.12). It
replaces running the frozen ML route (docs/STAGE_E_ML_DESIGN.md, "v1") as designed (V20); v1 stays
frozen and is not edited.

**Written before any market data was read.** No bar, quote, cost sample, Stage E screen or
confirmation figure was read for this draft. The only numbers used come from frozen tables:
- the D8 cost table, reports/stage_e2a_costs.json, through E.10's cost wall
  reports/stage_e10_research/cost_wall.json (sha256 8ef052dc...);
- the frozen design docs/STAGE_E_DESIGN.md (D2 to D9);
- the Topstep facts file reports/stage_e0_topstep_facts.json;
- the XFA rules engine rules/xfa_rules.py;
- docs/DECISIONS.md V10 to V22.

Every rule below is a stated rule or a bounded grid searched only on the training window. Nothing is
"chosen later by looking". Each section ends with **Open** when the user decides something there;
every open point is collected in V2.12.

**Decisions in force.** V20 (ML route v2), V18 (a minimum trade count fixed before data), V19
(account keys and caps), V21 (K9-anncday-01 folded in as a candidate signal; the cost wall, Holm
K = 10, a 30-trade floor), V22 (the income path, more history not finer data, the two-phase
purchase, Gate 0 first, the research findings F1 to F13).

**What v2 keeps from v1, and what it replaces.**

| v1 item | v2 | Where |
|---|---|---|
| M1 data partition | kept: train S_X..2024-02-29, March 2024 embargo, holdout-2 sealed, research window tested once | V2.1 |
| M2 pooling | kept: one pooled model across products, product and cluster identifiers, evidence counted in dates | V2.6 |
| M3 challengers (LightGBM grid, LSTM) | replaced: ridge primary, shallow LightGBM the only challenger, no LSTM (F3) | V2.6 |
| M4 features, targets, 30-minute clock | replaced: 1 to 3 decision times, holds of 60 minutes or more (F6), every K1-K9 family as a feature | V2.2, V2.3, V2.5 |
| M5 distillation | replaced: a deployable frozen model or distilled rules, the user's choice | V2.10 |
| M6 trial accounting | replaced: every configuration and every Gate 0 test counted for DSR (F4) | V2.9 |
| M7 leakage controls | kept in full, plus v2 canaries | V2.9 |
| M8 compute rules | kept (overnight profile, nice 10, resumable ledgers) | V2.11 |

---

## V2.0 Economics and statistical power (F1, F5, F11)

**The binding constraint is the MLL, not the edge alone (F1).** Every dollar figure below is a
model calculation for scale, not a forecast.

**Account parameters.**
- 50K XFA: MLL $2,000 (rules/xfa_rules.py XFA_50K, trailing from -$2,000 up to a $0 lock); optional
  DLL $1,000 (facts F12.2c); payout caps Standard $2,000 and Consistency $3,000, doubled with the
  DLL (F12.2a, F12.2b); scaling plan 2 lots, 3 at $1,500, 5 above $2,000 (xfa_rules).
- 150K XFA: MLL $4,500 (V22; not in the facts file, so the freeze session confirms it); DLL $3,000
  (F12.2c); payout caps Standard $5,000 and Consistency $6,000, doubled with the DLL (F12.2a,
  F12.2b). The 150K scaling schedule is published only as an image (facts F5.2 note); until it is
  read, the simulator uses the 50K tiers, the conservative reading.

**Sizing gives the daily risk (V2.8).** The target daily P&L sigma is 0.10 x D, where D is the
distance to the trailing MLL. At the start of an XFA, D = MLL, so sigma_day is $200 (50K) or $450
(150K). At an annualized net Sharpe S, the mean daily P&L is mu = S x sigma_day / sqrt(252).

| Net Sharpe S | 50K mu/day | 50K /month (21 d) | 150K mu/day | 150K /month | 5 x 150K /month, after the 90/10 split |
|---|---|---|---|---|---|
| 1.0 | $12.60 | $265 | $28.35 | $595 | $2,679 |
| 1.5 | $18.90 | $397 | $42.52 | $893 | $4,018 |
| 2.0 | $25.20 | $529 | $56.70 | $1,191 | $5,358 |
| eps (D3) $85/day at 50K | needs S = 6.75 at sigma_day $200 | | | | |

These figures are before payout caps, the MLL path, resets and sizing changes. The payout
simulator (V2.9) gives the figures that count.

Ruin, shown here for scale only (analytic, fixed size, no trailing): the probability that a
drifting random walk ever loses the MLL is exp(-2 mu MLL / sigma^2) = exp(-2 x 10 x S / sqrt(252)).
That is 0.28 at S = 1.0, 0.15 at 1.5 and 0.08 at 2.0. The trailing floor makes ruin likelier.
Sizing down as D falls makes it less likely.

More views of the same arithmetic (design review D-01; analytic; S = 1.0 / 1.5 / 2.0):
- Within 252 dates at fixed size, ruin is 0.235 / 0.139 / 0.078.
- During the trailing phase, before the floor locks at a $0 balance, the probability of breaching
  is about 0.39 / 0.29 / 0.20. This is F1's "the MLL binds".
- Under V2.8's D-proportional sizing, a breach is structurally rare: size shrinks as D shrinks.
  The event that ends income is D falling to the KS2b halt level, 0.25 x MLL. Its probability is
  about 0.70 / 0.29 / 0.12, from log D as a random walk with drift 0.0063 S - 0.005 and sd 0.10.
- So V2.9's ruin criterion counts reaching the KS2b level as ruin. A 10% bar on it is met only
  from S of about 1.8 upward.

F1's "near 3.5" and the table's 6.75 are not in conflict. F1 lets the daily sigma be chosen freely
at a 10% ruin bound. The table fixes sigma at 0.10 x D, a $200 day. Earning $85 a day with a $200
sigma needs S = 6.75. With sigma free, the ruin bound allows a sigma near $385, and S near 3.5
suffices.

**The realistic target band (F1).** A realistic successful system runs at a net Sharpe of 0.8 to 1.8
(V22). The design's success criteria (V2.9) aim at the band 1.5 to 2.5. They are never a bar only
HFT clears: the eps line is reported as context, not as the pass bar. A nested out-of-sample net
Sharpe above 4.0 is treated as a leakage alarm. The result is held until an independent leakage
audit clears it. Why 4.0: above F1's near-3.5, the figure only HFT reaches on this account, and
above the band's 2.5 ceiling. An intraday system at holds of an hour or more that shows 4.0 is
more likely leaking than skilled.

**Five copied accounts are one bet (F11).** Copy-traded accounts see the same fills, so they breach
together. Every multi-account figure multiplies a single path. It never treats five paths as
independent draws. The monthly column above is 5 x one account, with the same ruin probability as
one account.

**Minimum detectable Sharpe (F5).** For daily P&L, t is about S x sqrt(years). "Detect" means
t >= 3.0; "80% power" means a true S with E[t] = 3.0 + 0.84.

| Data | Years | S for t = 3.0 | S for 80% power |
|---|---|---|---|
| research window 2025-04-01..2026-06-19 (299 dates) | 1.19 | 2.75 | 3.52 |
| research window + holdout-2 | 2.19 | 2.03 | 2.60 |
| phase-1 or full training window, S_X 2019-05-06..2024-02-29 | 4.82 | 1.37 | 1.75 |
| MBT (S_X about 2021-05) | 2.8 | 1.79 | 2.29 |
| 2010 extension, 2010-01..2024-02 (V2.1 phase 2) | 14.2 | 0.80 | 1.02 |

Two consequences:
- The research window cannot confirm a Sharpe near 1.5 (F5). Confirmation therefore rests on the
  pooled training history, through the nested out-of-sample estimate (V2.9). The research-window
  test is a guard against regime break and overfitting, with a bar it can meet (V2.9).
- Phase 1 and the full 28-product set give the same years. More products add breadth, and so more
  achievable Sharpe, but not more detectability per year. Only the 2010 extension buys detectable
  Sharpe below about 1.4.

The DSR at the full trial count (V2.9) raises the bar further. Its haircut depends on the variance of
the trials' Sharpes, which is not known before data.

---

## V2.1 Universe, windows and the purchase plan (V22)

**Universe: the 28 traded exposures** (D2 vehicles with status chosen or undersized; RBOB, ULSD and
silver have no vehicle; MES and ES are not traded, D1.5). Each exposure's price path is the
full-size contract where one is permitted. This is v1's ML-A07 rule: "the longest history", with
ties going to the full-size contract. Bitcoin uses MBT. Trades, fills, costs and tick values are the
vehicle's (D2, D8). RT_X is E.10's cost wall: commission plus 2 x the worst bucket's one-side
slippage, in ticks of the vehicle.

| Cl | Exposure | Vehicle | Price path | Tick $ | RT_X ticks | RT_X $ |
|---|---|---|---|---|---|---|
| K1 | Nasdaq-100 | MNQ | NQ | 0.5 | 5.41 | 2.71 |
| K1 | Russell 2000 | M2K | RTY | 0.5 | 6.35 | 3.17 |
| K1 | Dow | MYM | YM | 0.5 | 7.52 | 3.76 |
| K2 | 2-year | ZT | ZT | 7.8125 | 1.32 | 10.31 |
| K2 | 5-year | ZF | ZF | 7.8125 | 1.31 | 10.23 |
| K2 | 10-year | ZN | ZN | 15.625 | 1.17 | 18.28 |
| K2 | Ultra 10-year | TN | TN | 15.625 | 1.24 | 19.38 |
| K2 | Bond | ZB | ZB | 31.25 | 1.12 | 35.00 |
| K2 | Ultra bond | UB | UB | 31.25 | 1.12 | 35.00 |
| K3 | EUR | 6E | 6E | 6.25 | 2.31 | 14.44 |
| K3 | AUD | 6A | 6A | 5.0 | 2.48 | 12.40 |
| K3 | GBP | 6B | 6B | 6.25 | 2.03 | 12.69 |
| K3 | CAD | 6C | 6C | 5.0 | 2.21 | 11.05 |
| K3 | JPY | 6J | 6J | 6.25 | 2.10 | 13.13 |
| K3 | CHF | 6S | 6S | 6.25 | 3.98 | 24.88 |
| K3 | NZD | 6N | 6N | 5.0 | 2.62 | 13.10 |
| K4 | WTI crude | MCL | CL | 1.0 | 4.35 | 4.35 |
| K4 | Henry Hub gas | NG | NG | 10.0 | 2.41 | 24.10 |
| K5 | gold | MGC | GC | 1.0 | 5.60 | 5.60 |
| K5 | copper | MHG | HG | 1.25 | 5.01 | 6.26 |
| K6 | corn | ZC | ZC | 12.5 | 1.50 | 18.75 |
| K6 | wheat | ZW | ZW | 12.5 | 1.69 | 21.13 |
| K6 | soybeans | ZS | ZS | 12.5 | 1.64 | 20.50 |
| K6 | soybean meal | ZM | ZM | 10.0 | 1.79 | 17.90 |
| K6 | soybean oil | ZL | ZL | 6.0 | 2.67 | 16.02 |
| K6 | lean hogs | HE | HE | 10.0 | 1.97 | 19.70 |
| K6 | live cattle | LE | LE | 10.0 | 2.50 | 25.00 |
| K7 | bitcoin | MBT | MBT | 0.5 | 10.87 | 5.44 |

(Tick values and RT_X are copied from cost_wall.json, the "tick_value_usd" and "rt_wall_ticks"
fields. The table generator is reports/stage_e11_briefs/universe_table.md. The freeze session
regenerates the table from the JSON and checks it.)

**Signal-only roots.** MES is read as a signal leg only, never traded (K8-flight; V16(b)). The
price-path contracts of other clusters are read for cross-product features (V2.3).

**Windows (v1 M1, kept).**
- Training: trade dates S_X..2024-02-29, with S_X from D4's start rule; the earliest is 2019-05-06.
  All fitting, tuning, normalization, selection, Gate 0 and the c/sigma filter use this window only.
- Never touched: March 2024 (embargo); holdout-2 (2024-04-01..2025-03-31, sealed on arrival);
  everything from 2026-06-21 00:00 UTC.
- Research window 2025-04-01..2026-06-19: one test of the frozen model, once (V2.9). The vehicles'
  research-window bars are already owned (E.1).
- Recorded (V20): the training window overlaps the 2019-2024 data already read for K4's and K5's
  confirmations (MCL, NG, MGC, MHG). v2 selects nothing by those results. Every family is a
  feature, and the model chooses on the training window only.

**Purchase plan in two phases (V22).** No tick or order-book data at any phase (F13): one-minute
OHLCV bars suffice for holds of 60 minutes or more.

*Phase 1: the funds already in the two Databento accounts.*
- Budget: acct-1's headroom first (about $28.41), then acct-2 ($125 after the user raises
  ACCOUNT_2_CAP_USD to about $249.67, V19). The purchasing session raises the cap; this draft
  changes nothing.
- Scope per exposure: ohlcv-1m of the price-path contract, training window only (S_X..2024-02-29).
  This departs from V1, under which the route bought the full step 2 range including the holdout-2
  chunks. Holdout-2 for the products the frozen model trades comes in phase 2, sealed on arrival.
  Open.
- The price path is fixed now, once, before Gate 0 (design review D-06): the full-size contract
  of the table above, for every exposure, in every phase.
  - The owned step 2 store of NG (E.5) is the NG price path itself, so it costs $0.
  - The owned MCL, MGC and MHG stores are the micros, whose own S_X starts years after 2019-05.
    They are NOT price paths. CL, GC and HG are bought under the ranking like any other exposure.
  - A price-path switch between phases would change every feature, sigma_X,d and the Gate 0
    result for those pairs, so none is allowed.
- **Ranking rule (stated now, applied at the freeze session to a fresh quote):**
  1. Liquidity screen: an exposure whose vehicle's 2026 January-August ADV (the frozen D1 census,
     reports/stage_e0_liquidity.json) is at or above the median of the 28 is in tier 1; the rest
     are tier 2.
  2. Within a tier, sort by c / sigma_proxy ascending, where c = RT_X in dollars per contract and
     sigma_proxy = the CME maintenance margin per contract of the vehicle's front month, in
     dollars, as published on the freeze date. The margin is the volatility proxy: CME sets it from
     its own risk model, so it reads no market-data window of ours. Open (alternative below).
  3. Cluster round-robin: the first pass takes the best-ranked exposure of each cluster K1..K7 in
     rank order; the second pass takes the rest by rank. Each pass skips an exposure whose fresh
     quote exceeds the remaining budget and goes on to the next.
  4. Stop when no remaining exposure's quote fits. The freeze session quotes the subset fresh
     before buying and logs the quote first (CLAUDE.md).
- Alternative volatility proxy: the frozen E|m_1| of the E.2a epsilon report. It is the vehicle's
  mean absolute day-session move. It is already on disk and closer to intraday volatility, but it
  was measured on research-window bars (level information of the kind v1 M7.9 allows). Open.
- Expected phase-1 size: about 8 products (the runtime probe's second scale, Task 7). The figure
  is a planning guess, not a rule.

*Phase 2: only if Gate 0 passes on phase 1 (V2.2b).*
- The remaining exposures of the 28 (training window).
- The holdout-2 chunks (2024-03..2025-03, sealed on arrival) for every exposure the frozen model
  can trade.
- A free quote for the full-size contracts from 2010-01-04 to 2019-05-03 as price paths before the
  micros existed (the 2010 extension). Buying it needs a start-rule amendment, because D4's
  earliest S_X is 2019-05-06, and the user's decision. Open.

If Gate 0 fails, nothing more is bought and v2 stops (V2.2b).

Gate 0 runs once, on the phase-1 products. Phase-2 products enter V2.6 after the c/sigma filter
(re-applied to them), without a Gate 0 audit of their own. N adds the phase-1 Gate 0 tests only.

---

## V2.2 Decision clock (F6)

**Notation.** b_s is the one-minute bar starting at s; it closes at s + 1 min. The frozen engine
decides at a bar's close and fills a market order at the open of a later bar (api: stage_e_engine
fill_pending_at_open). A decision at clock time t therefore uses only bars b_s with s <= t - 1 min,
which have closed by t, and its entry fills at the open of b_t, or later under the D9.5a fill guard.

**Decision times: three per product per trade date, from D6's session table and D9's flatten F_X.**
With O_X the day-session open and k counting 30-minute steps:
- t1 = O_X + 30 min;
- t3 = the latest O_X + 30k with t3 + 120 min <= F_X, so that both fixed horizons fit;
- t2 = O_X + 30 x floor((1 + k3) / 2) minutes.

| Group (D6) | O_X | F_X | t1 | t2 | t3 |
|---|---|---|---|---|---|
| equity index, crypto (MNQ, M2K, MYM, MBT) | 08:30 | 15:08 | 09:00 | 11:00 | 13:00 |
| rates, FX | 07:20 | 15:08 | 07:50 | 10:20 | 12:50 |
| energy (MCL, NG) | 08:00 | 15:08 | 08:30 | 10:30 | 13:00 |
| gold (MGC) | 07:20 | 15:08 | 07:50 | 10:20 | 12:50 |
| copper (MHG) | 07:10 | 15:08 | 07:40 | 10:10 | 12:40 |
| grains (ZC, ZW, ZS, ZM, ZL) | 08:30 | 13:18 | 09:00 | 10:00 | 11:00 |
| livestock (HE, LE) | 08:30 | 13:03 | 09:00 | 10:00 | 11:00 |

(CT. The clock uses O_X and F_X only and deliberately ignores C_X. On gold, copper, rates and FX,
t3 and the h60/h120 exits can fall after the day-session settlement; D8's buckets price those
hours, and the cost gate decides. The worker code computes the table from the rule, and a test pins
it to this table. On a CME
early-close date the whole date is excluded, as in v1. The flatten table rules/sessions.py governs F_X.)

**Horizons: h in {60 min, 120 min, F}.** "F" exits at the forced flatten: the exit fills at the
engine's flatten fill. Every hold is 60 minutes or longer (F6). A fixed horizon exists at t only if
t + h <= F_X. "F" exists at every t.

**Frequency cap.** At most one open position per product. A decision time is skipped while a
position from an earlier decision of the same product is open (v1 M4). At most 3 entries per
product per trade date, so D9.3's floor of 20 entries and 2-minute holds holds by construction.

**Excluded dates (v1 M4, ML-A09).**
- Roll-blackout dates of the traded product, which exclude its rows.
- A signal leg's roll-blackout date does not drop rows. Every feature that reads that leg (the
  G17 leads, the K8 signal legs) is "not applicable" on that date: 0 plus its flag, the same
  treatment as a lead not yet listed.
- This replaces D4's union for v2. Every product reads all eight leads, so the union would drop
  every lead's roll dates (CL and MBT roll monthly) for every product: a large share of the
  training dates. D4's union stays in force for the frozen K8 members as trials.
- Open.
- Early-halt and early-close dates of its group calendar.
- An entry whose fill would land in the D9.12 CPI window on a mini, which is skipped. No decision
  time here is within [CPI - 5, CPI + 5] with CPI at 07:30 CT, but the engine enforces the rule
  anyway.
- Vendor-degraded dates are kept (NULL_CRITERIA_E 4).

**The c/sigma filter (F6), on the training window.** For each product p and horizon h:
- c(p,h) is the mean D8 round trip in vehicle ticks over p's decision rows. It is the commission
  plus the entry bucket's and exit bucket's one-side slippage at size 1, with D8's event-window
  rule.
- sigma(p,h) is the standard deviation of the gross h-forward return in vehicle ticks over the same
  rows (V2.5).
- The pair (p,h) is admissible iff c(p,h) / sigma(p,h) <= tau = 0.10. A product with no admissible
  horizon is dropped.

Why 0.10: with the predicted return r_hat = IC x sigma x z, a strong intraday information
coefficient (0.10) at its 99th-percentile prediction (|z| about 2.5) predicts 0.25 sigma. The
loosest cost gate (V2.7, k = 1.5) needs a predicted gross of 2.5c. So c/sigma > 0.10 means no
plausible signal clears the gate.

The filter reads volatility only, never a return's sign or mean. It is not a trial and adds nothing
to N. It is applied once, before Gate 0. Open (tau).

---

## V2.2b Gate 0: the pre-cost component audit (F2)

Gate 0 comes first. **If Gate 0 fails, v2 stops: no net modelling, no phase-2 purchase.** It runs on
the phase-1 products' training window, on admissible (p,h) pairs only. It uses gross targets (V2.5).
The pass bar below is fixed now, before any data.

**Test family A: each signal alone.** For each signal s of V2.3 and each horizon h, pooled over
products:
- The statistic is the date-clustered information coefficient. For each row i, compute
  z_s,i x y_i, where z_s,i is the signal's causal z-score (V2.4) and y_i is the gross h-forward
  return divided by sigma_X,d (V2.5). Average within each trade date to get m_d. Then t_A is the
  mean of m_d over its standard error across dates.
- Averaging within the date first means overlapping horizons on one date and same-date
  correlation across products count once ("t-statistics that respect overlap").
- The Spearman rank IC per (s, h), pooled, and the mean gross forward return in ticks of the
  sign(z_s) position are reported beside it. They are descriptive.
- A single signal is not fitted, so it needs no CPCV. Test A is two-sided, since a generic feature
  has no stated sign.

**Test family B: the pooled ridge combination, per product-horizon pair.**
- Fit: ridge at the fixed middle of V2.6's grid (lambda = 0.1; no selection inside Gate 0) on all
  V2.3 features plus product and cluster identifiers, pooled across the phase-1 products, one model
  per horizon.
- Out-of-fold predictions: CPCV as V2.9. Six calendar blocks, two test blocks, 15 splits, with purge
  and a one-trade-date embargo. Each row is out of fold in 5 splits, and its OOF prediction r_hat_i
  is the mean of those 5.
- Trades in Gate 0: for each pair (p,h), the rows whose |r_hat| is in the top 20% of the pair's OOF
  |r_hat|, traded in sign(r_hat). The quantile reads predictions only, no returns.
- Statistic: the gross P&L per trade g_i = sign(r_hat_i) x r_i in vehicle ticks. The mean g over
  the pair's trades is compared with c(p,h). The date-clustered t_B is the mean of the per-date mean
  g over its standard error.

**Pass bar (fixed now).** Gate 0 passes iff at least one pair (p,h) has all of:
1. mean g >= 1.5 x c(p,h);
2. t_B >= 3.0;
3. its p-value is rejected by Holm at family-wise alpha 0.05 across all of Gate 0's tests (families
   A and B together);
4. at least 30 trades (V18, V21).

The pooled result over all pairs is reported beside it.

Gate 0 does not choose products. A pass lets the whole admissible universe go on to V2.6. A
pair's own Gate 0 result never decides whether that product is in the model. Choosing products by
Gate 0 results would select on the same data the model is then tuned on.

**Trial accounting.** Every Gate 0 test counts toward N: |A| = (number of signals) x 3 horizons,
and |B| = the number of admissible pairs (V2.9).

**How a sub-cost edge behaves (canary semantics).**
- An edge smaller than the round-trip cost fails bar 1 here.
- An edge that clears bar 1 (at or above 1.5c on the confident quintile) can still sit below the
  cost gate's lowest hurdle: a predicted gross of 2.5c at k = 1.5 (V2.7). It then passes Gate 0 and
  the cost gate rejects it.
- The canaries test both.

**The operative bar** (design review D-14).
- With families A and B in one Holm family (about 222 tests at 8 products, 282 at 28), the first
  rejection needs p <= 0.05 / 282, a one-sided z of about 3.57.
- So bar 2 (t >= 3) is dominated, and the real bar is about 3.6.
- Without family A in the Holm family, it would be about 3.24.

**Coupled with the cost gate and tau** (V2.7; design review D-05). The Gate 0 multiple, the
cost-gate reading and tau are one decision, collected as V2.12 item 1.

Open: the bar (the 1.5 multiple, t >= 3, the top-20% trade set, Holm at 0.05), and whether family A
counts in the Holm family.

---

## V2.3 Signals: the candidate library

Every K1 to K9 member family's decision variable is a feature, all of them (V20). Generic features
are added. No signal is chosen or dropped by any Stage E result. The inventory of decision variables
is reports/stage_e11_briefs/member_inventory.md and .json: 54 families, 33 non-port and 21 ports,
traced to their member modules and the K9 catalog entry.

**Rule for member variables.**
- A member variable enters at each decision time t as its most recent value available at t on the
  same trade date. It is computed from the member's own frozen definition: bars, calendars, literals.
- An event that has not happened yet that day gives the value 0 plus an applicability flag of 0.
  Example: a WASDE 5-minute move before the release.
- A fixed-clock member (13 of the 54) has no variable. It enters as its event's flags: a same-day
  flag, minutes to the event and minutes since the event, each from a calendar known in advance.
- A family that cannot be computed causally over the training window is logged with its reason and
  enters as no feature. One example is a literal table, such as the VXN closes (K1-vxnband) or the
  Nikkei monthly returns (K3-mehedge), that does not cover 2019-05..2024-02. The SignalCoder's
  coverage log decides, and nothing is guessed.

**Member families (one feature group each, availability per the inventory).**
- Ports, per cluster K1-K7:
  - CP1: sign and size of the early-session return, close(O+29) - open(first bar);
  - CP2: the opening range and the breakout distance beyond it;
  - CP3: the prior day's close-location value.
- K1: vwap side; VXN regime and band breach.
- K2:
  - fixed-clock event flags for the auction pre and post, FOMC post and month-end members;
  - the ISM pre-release drift.
- K3:
  - flags for the ECB fix and the Tokyo pre and post fixes;
  - the London pre-fix trend;
  - the London month-end move;
  - the Nikkei month return (if covered).
- K4:
  - the API Tuesday return;
  - the WPSR post-release move and WPSR-day return;
  - the NG storage-day flag;
  - the hourly return and its trailing percentile position.
- K5:
  - the FOMC 5-minute move;
  - the hourly return percentile;
  - the PM fix move;
  - the pre-auction flag.
- K6:
  - the crush gap (ZM, ZL legs);
  - the limit-close event;
  - the WASDE post-release 5-minute move;
  - the WASDE pre-release drift.
- K7:
  - the expiry flag;
  - the Monday hourly TSMOM;
  - the two-hour return.
- K8:
  - the MES 5-minute return and its tail-quantile position (flight);
  - the MCL 5-minute z-score (oil to CAD);
  - the weekend MBT move.
- K9: the announcement-day flag (EC-K9 calendar: FOMC, payrolls, GDP first or last, ISM
  manufacturing, the earlier of CPI and PPI).

**Generic features (each with its availability).** All are computed from bars closed by t, or from
calendars known in advance:
- G1-G4: returns over the last 30, 60 and 120 minutes, and since the trade date's first bar;
- G5: the overnight gap, the day-session open minus the prior close at C_X;
- G6: realized volatility of one-minute returns over the last 60 minutes, over its 20-date mean;
- G7: the intraday range so far over sigma_X,d;
- G8: the prior complete day's return, over sigma_X,d;
- G9: the trailing 20-date sigma_X,d over its trailing 120-date median;
- G10: the log volume ratio over the last 30 minutes (v1 F10);
- G11: the decision-time index (1, 2, 3); G12: day of week;
- G13-G15: release flags for the product (D8's list): minutes to the next release, minutes since
  the last, and a release-day flag; G16: a month-end flag (last two trade dates of the month);
- G17: cross-product returns: the 60-minute return of each other cluster's lead price path (K1 NQ,
  K2 ZN, K3 6E, K4 CL, K5 GC, K6 ZC, K7 MBT, plus MES), from bars closed by t only (v1 F16). A
  lead not yet listed on a date is "not applicable" (0 plus a flag), never a missing row.
- G18, G19: product and cluster identifiers (one-hot).

**Missing values (v1 ML-A05, kept).**
- "Not applicable" by construction (no event that day, a lead not yet listed) is 0 plus a flag.
- Missing for data reasons excludes the row: an absent bar at t, at the entry or at the exit; a
  lookback not full; a warm-up not complete. There is no imputation.

**Size (as built, Task 2).**
- Signals: 51 of the 54 families are coded. The three CP ports are pooled across products: one
  feature per port variable, since D6 defines each port as one rule ported to every product. There
  are 24 generic signals (G1-G16, and G17's 8 leads).
- Excluded, with reasons (reports/stage_e11_signal_coverage.md):
  - K5-fomc-01: the FOMC move is known at 13:05 CT, after the last metals decision time, 12:50;
  - K6-wasdepost-01: the WASDE move is known at 11:15 CT, after the last grain decision time,
    11:00;
  - K9-anncday-01: its EC-K9 calendar covers only 2025-04..2026-06, and the frozen release calendar
    has no GDP or ISM-manufacturing rows for 2019-2024. Building EC-K9 for the training window
    from official sources is a sourced-data task the freeze session can do. Open.
- Columns: 66 signals, 42 member and 24 generic. Each gives a z-score; 53 applicability flags
  remain after the always-1 flags are dropped; and there are 35 identifier one-hots (28 products, 7
  clusters). That makes 154 model columns against about 90,000 rows on 28 products: easily within
  ridge's and LightGBM's range.
- Family A therefore has 66 x 3 = 198 tests.
- Family A has one test per signal per horizon (V2.2b). The exact counts are in
  reports/stage_e11_signal_coverage.md.

Open: the generic list.

---

## V2.4 Normalization (causal)

- **Features:** a rolling z-score per product and per feature, z = (x - mean) / sd. The mean and sd
  are over the product's rows in the trailing 250 trade dates strictly before the row's trade date,
  with at least 60 dates; with fewer, the row is in warm-up and excluded. The z-score is clipped to
  [-5, 5]. Flags and identifiers are not normalized.
- **Targets:** divided by sigma_X,d, v1's ML-A06 definition: the mean over the 20 complete trade
  dates before d of |close(C_X - 1 min) - open(O_X)| in vehicle ticks.
- **No constant is estimated on or after 2024-03-01.** The only research-window-derived constants
  the training may use are v1 M7.9's (the D8 cost surface, D2's q_c and r_c, S_X) and two more:
  - the D1 ADV census (2026 January-August), used only by the phase-1 ranking;
  - E|m_1|, only if the user picks it as the volatility proxy (V2.1).
  Both are level information used before any training bar is read.
- **Known overlap, as v1 ML-A13 ruled.** The trailing statistics are not embargoed. A training row
  just after a CPCV test block is normalized with feature values from that block. These are
  features only, never labels, and only inside the training window.

Fixed: the windows 250, 60 and 20, and the clip at 5. No grid.

**Warm-up at the research-window test.**
- Trailing windows (z-scores, sigma_X,d, G6, G9, G10) run over the last available trade dates,
  skipping the never-touched gap (March 2024 and holdout-2): the training-window dates, then the
  research-window dates before the row. That is causal (only older data) and costs no
  research-window dates.
- With warm-up from the research window's own bars only (v1's ML-A19 convention), the first 80 to
  140 of its 299 dates would have no rows: sigma_X,d 20 plus the z-score minimum 60, and G9's
  120-date median on top. The window would shrink to 0.63-0.87 years. The power of the t >= 1.0
  screen at S = 1.5 would fall from 0.74 to about 0.58-0.66.
- Open: skip the gap (proposed), or research-window-only warm-up.

---

## V2.5 Targets

For a decision at t with horizon h, in ticks of the vehicle:
- **Gross:** r = open(b_{t+h}) - open(b_t). For h = F, r is the engine's forced-flatten fill price
  minus open(b_t). The fill guard can move the entry; then the entry price is that fill's open.
- **Net:** for a long, r - c; for a short, -r - c. c is that row's D8 round trip at size 1, the
  entry and exit buckets with the event-window rule. The net figures are what the decision layer,
  the selection metric and every evaluation use.
- **Normalized:** r / sigma_X,d, used for fitting and pooling.
- Horizons end at or before F_X by construction (V2.2). Gate 0 uses gross. Everything after Gate 0
  is evaluated net.
- D9.7's price-limit exits and locked markets act through the engine at evaluation and are not
  modelled in the targets (v1 ML-A25).

---

## V2.6 Alpha combination (F3)

- **The model is fit on the normalized gross target.** At decision time the cost c is known exactly,
  so the predicted net edge of either side follows exactly: e_long = r_hat - c and
  e_short = -r_hat - c. Fitting on gross also lets Gate 0 and the net pipeline share the same fit.
- **"The net model"** means the full pipeline: model, then cost gate, then sizing, then net P&L.
  It is selected on net P&L (V2.9).
- **Pooled across products** (v1 M2). One model per horizon over all admissible products, with
  product and cluster identifiers. Evidence is counted in trade dates.
- **Primary: ridge.** Closed form and deterministic. Alpha = lambda x n_train, with lambda in
  {0.01, 0.1, 1.0}. Features are z-scored (V2.4), with an intercept. Elastic net is not used: with
  154 columns and about 10^5 rows, sparsity buys little, and an L1 path adds a parameter.
- **Only challenger: shallow LightGBM**, L2 regression.
  - Its fixed settings are new literals, fixed now and never tuned. They are not v1's: v1 used
    0.03, 400 rounds, 0.8 fractions and an unbounded depth.
  - At phase-1 scale (8 products, about 12,000 rows in an inner-fold training set),
    min_data_in_leaf 2000 allows at most six leaves. So the depth-3 configuration cannot grow its 8
    leaves, and the two LightGBM configurations are near-degenerate until phase 2 (design review
    D-12).
  - Grid: max_depth in {2, 3}, with num_leaves = 2^max_depth.
  - Fixed: min_data_in_leaf 2000, lambda_l2 100, learning_rate 0.02, 300 rounds, no early
    stopping, feature_fraction 0.7, bagging_fraction 0.7, bagging_freq 1, deterministic true,
    force_col_wise true, num_threads 8, every seed 20261003.
- **No LSTM, transformer or other deep sequence model.** ml_route/lstm.py is not reused (F3).
- **Grid size: 5 models x 3 values of k (V2.7) x 3 horizons = 45 configurations.** That is at v1's
  MinBTL bound of about 45 independent configurations for about 5 years (E1-ML-19). The
  configurations are not independent: the values of k share each fit, so the effective count is
  lower.

Open: the grids.

---

## V2.7 Decision layer: the cost gate (F7)

At decision time t, for product p and horizon h of the selected configuration:
- r_hat_ticks = r_hat x sigma_X,d;
- c is the D8 round trip at size 1, with t's entry bucket and the exit bucket at t + h (for F, the
  flatten bucket), applying the event-window rule if the entry or the exit falls in
  [release, release + 30 min);
- the predicted net edge is e = |r_hat_ticks| - c.

Trade sign(r_hat) iff e > k x c, with k in {1.5, 2, 3} chosen by nested CPCV (V2.9). This is the
literal reading of F7: the predicted net edge, after cost, exceeds k round trips, so the gross must
exceed (1 + k) c.

**One coupled decision, with two consistent sets** (design review D-05):

| | Literal reading (built, the default) | Gross reading (|r_hat| > k c) |
|---|---|---|
| hurdles on predicted gross at k = 1.5 / 2 / 3 | 2.5c / 3c / 4c | 1.5c / 2c / 3c |
| tau (V2.2's derivation: 0.25 sigma = the loosest hurdle) | 0.10 | 0.167 |
| Gate 0 cost multiple | 1.5c (1.0c below the loosest hurdle), or 2.5c to align | 1.5c = the loosest hurdle |
| k = 2 and k = 3 configurations at IC 0.10 | often below the 30-trade eligibility when c/sigma > 0.083 or 0.0625 | alive |

The code switches between the readings with one constant (COST_GATE_READING). The lead recommends
the gross reading: it is the usual quant formulation, it aligns Gate 0 with the loosest hurdle, and
it keeps the k = 3 configurations alive. The user decides (V2.12 item 1).

At the same clock time, candidates are ranked by e / c, ties going to the root's alphabetical order,
and taken while V2.8's caps allow.

**Known property (Task 5 canary 8c, finding C-1).**
- The gate acts on the model's predictions, not on the true edge. For a bounded true edge (a
  constant 2c whenever a feature is positive), ridge extrapolates linearly, and its predictions on
  large-|z| rows can pass the 2.5c hurdle although the true edge never does.
- Those trades realize the true edge: positive net, about 1.1c each, in the canary. So the gate
  does not admit negative-net trades there, but it does trade an edge below its own hurdle.
- The canary therefore holds for the planted expected edge (zero trades at every k), and for
  ridge it is kept as a documented expected failure.
- The verdicts read realized net P&L out of sample, so this affects how much the gate filters,
  not the evaluation's honesty.

---

## V2.8 Sizing, portfolio and kill switches (F8, F10, F11)

**Drawdown distance.** D = (account equity, realized plus unrealized) minus the trailing MLL floor in
force (rules/xfa_rules.py). D_open is D at the start of the trade date.

**Sizing (F8).**
- Daily risk target: sigma_target = 0.10 x D_open.
- Per-trade risk budget: b = sigma_target / sqrt(m), with m = 3, the cap on simultaneous positions.
- **Daily risk budget** (design review D-03):
  - The day starts with a variance budget sigma_target^2. Each accepted trade consumes
    (n x sigma(p,h) x tick_value)^2.
  - A trade's n is the largest that fits both b (or the rounding band below) and the remaining
    budget. No entry is accepted once the budget is spent.
  - For about independent trades, the daily sigma is then at most sigma_target by construction.
  - Without the budget, three decision times and short h60/h120 holds allow up to 9 trades a day,
    a daily sigma up to 1.7 x the target.
- Contracts from risk: n_risk = floor(b / (sigma(p,h) x tick_value)), with sigma(p,h) the training
  window's gross h-return sd in ticks (V2.2's filter quantity).
- Rounding band: if n_risk is 0 but one contract's h-sigma in dollars is at most 2 x b, then
  n_risk = 1. This is D2's band upper end (risk ratio 2.0). Without the band, every vehicle whose
  one-contract h-sigma exceeds b would be untradeable at that D, whatever its signal. b is $115.47
  at 50K's starting D ($2,000) and $259.81 at 150K's ($4,500), so many full-size vehicles would be
  out at 50K. The band can lift one trade's sigma to about 1.15 x sigma_target. The loss cap and
  KS1 still bound it. Open.
- Loss cap (F8): n_loss = floor(0.25 x D_now / ((L(p,h) + c) x tick_value)). L(p,h) is the 99th
  percentile of the absolute h-move in ticks on the training window, a constant per pair. The rule
  has no stop orders (D9.4), so "maximum loss on one trade" is this tail quantile, not a guarantee.
- n = min(n_risk, n_loss, the per-product cap, the portfolio capacity left, D9.12's CPI cap), then
  reduced until it fits the day's remaining risk budget. If n < 1, no trade.
- **Cost beyond D2's size** (design review D-08a):
  - D8's slippage, depth term included, is calibrated at q_c. Each contract beyond q_c pays one
    extra tick per side: D8's "one extra tick for the part of the order beyond the top level",
    with the top level taken as q_c, which is conservative.
  - The engine run (a cost override in PortfolioRules, which only adds cost), the selection metric
    and the payout simulator's re-sizing all charge it.
- **After a payout** the XFA's MLL floor resets to a $0 balance (xfa_rules reset_mll_after_payout).
  D drops to the remaining balance, and sizing falls with it (F8 "size down after each payout").
  Nothing else is needed.

**Caps (the frozen rules, at the account level).**
- Per product: at most 1 lot-equivalent (D9.5: minis 1, micros 0.1 each, MBT 1) and D9.11's 50K
  volatility caps (MHG 2, MCL and MGC 10). The 50K figures are used at 150K too, conservatively,
  as D9.11 does.
- Portfolio: open lot-equivalents at most the XFA scaling tier at the prior session's closing
  balance minus 0.1 lot. It is never at full Maximum Position Size, D9.5's purpose (F6.3). At 50K:
  1.9, 2.9 or 4.9 lots by tier; the 150K tiers are open (V2.0).
- Simultaneous positions: at most 3 in all, and at most 1 per cluster (F11: a cluster's products
  are largely one bet, as K2's six rates contracts are).
- Everything is flat by 15:08 CT, or the group's earlier F_X. The engine forces it (D9.1).

**Kill switches (F10), with default thresholds (open):**

| # | Switch | Trigger | Action | In backtest |
|---|---|---|---|---|
| KS1 | daily loss stop | the day's P&L (realized + unrealized) <= -0.30 x D_open, or the DLL if added | flatten all; no entry for the rest of the trade date | simulated |
| KS2 | drawdown-distance stop | D < 0.50 x MLL | size multiplier 0.5 until D >= 0.50 x MLL | simulated |
| KS2b | drawdown-distance halt | D < 0.25 x MLL | no new entries; the account halts pending the user's review | simulated: the path stops trading, reported as "halted", not as ruin |
| KS3 | consecutive-loss stop | 5 consecutive losing trade dates | no entries on the next trade date; the counter resets | simulated |
| KS4 | live-versus-expected drift | the trailing 40-date mean daily P&L < mu_expected - 3 x sd_expected / sqrt(40) (both from the nested OOS estimate) | halt pending review | paper and live only; the backtest reports when it would have fired |
| KS5 | stale data | the product's latest closed bar is older than 2 minutes at t, or any input is missing | no entry; in a position with no bar for 5 minutes, flatten at the next bar | the missing-input rule applies; the 5-minute flatten is live only |

**The simulator (ml_route_v2/simulate.py) runs the portfolio through the frozen engine as one
multi-leg account.**
- Unchanged from the frozen engine: run_engine, the D8 fills and costs, the fill guard, the CPI
  window, the price-limit rules, the flatten, the entry cap, the minimum hold, the XFA scaling gate
  and the real-time and end-of-day trailing MLL.
- The v2 rules object derived from StageERules differs in exactly three ways. None of them changes
  a fill, a cost rate, the flatten, the XFA gate or the MLL:
  1. it drops the catalog's one-position-at-a-time refusal (engine_second_leg_position, a catalog
     rule, K8 rule 5);
  2. it applies the member lot-equivalent cap per product instead of per member;
  3. it checks the roll blackout per product (V2.2): an entry in P is refused on P's own roll
     dates, and no longer on every traded product's.
  It also only ADDS cost: one extra tick per side for contracts beyond q_c (above).
- Each engine path runs in its own process, for memory (V2.11). The portfolio caps above are applied by
  the portfolio before any intent reaches the engine. The engine's own XFA gate still refuses
  anything above the tier.
- Two tests show it is never more generous than the frozen engine:
  - a single-product portfolio reproduces the frozen StageERules run fill for fill;
  - a hand-computed two-product day matches to the cent.
- The frozen account model encodes 50K only. The 150K figures come from the payout simulator
  (V2.9), which re-sizes the engine's per-contract trip records under 150K parameters.
- **Combined MLL audit.** The frozen engine checks each leg's adverse extreme against the floor on
  its own (screening/stage_e_engine.py check_mll). That was exact while the catalog held one
  position at a time, but it understates an account-level breach when several products are open.
  simulate.py therefore audits every minute with two or more open legs. The realized balance plus
  each open leg's adverse-extreme unrealized is compared with the floor in force; the sum of
  per-leg extremes is conservative, because they need not coincide. Any audit hit counts as an
  MLL breach in every verdict and report. The engine itself is not changed.
- Kill switches act in the payout simulator (V2.9), not inside the engine run. The engine run
  supplies exact per-contract fills and costs. The payout simulator applies account mechanics and
  kill switches to re-sized trades.

---

## V2.9 Evaluation (F4, F9)

**Partition of the training window (v1 M7.3's block-cut rule kept; its use changed).**
- The training calendar is every CME trade date S_X..2024-02-29 of at least one group calendar. It
  is cut from calendars alone into 6 contiguous blocks of floor(n/6) dates, the last taking the
  remainder.
- Purge: training rows whose target window overlaps a test date. All holds are intraday, so this
  is every row on a test date.
- Embargo: one full trade date on each side of every test block.
- The change from v1 (design review D-13): v1 ran CPCV on blocks 1-5 (10 splits) and kept block 6
  for M5's pre-test. v2 has no M5 and uses all six blocks (15 splits, 5 paths).

**Nested CPCV (F4).**
- Outer: 6 blocks, 2 test blocks, 15 splits, giving 5 backtest paths.
- Inner, inside each outer split's 4 training blocks: 4 folds, each holding out one block, with the
  same purge and embargo.
- Per outer split:
  1. Every one of the 45 configurations is scored on the inner folds by the selection metric.
  2. The best eligible configuration is refit on the outer training blocks.
  3. That refit predicts the outer test blocks.
- The outer predictions, assembled into the 5 paths, are the **nested out-of-sample** record of the
  whole selection procedure. Every verdict below reads that record.
- The final configuration: chosen by the same metric over the 15 outer splits of the full window,
  then refit once on all 6 blocks. That refit is the frozen model.
- **Aggregation and eligibility, fixed now** (design review D-07):
  - A configuration's score is the mean of its per-fold daily Sharpes (inner) or per-split daily
    Sharpes (final).
  - It is eligible only with at least 30 trades and a finite score on EVERY fold: every inner fold
    of the outer split, and every one of the 15 outer splits for the final model.
  - If no configuration is eligible, the split trades nothing. If none is eligible for the final
    model, the route has no model, and that is a fail.
- **The risk table inside the CPCV** (design review D-04):
  - sigma(p,h) and L(p,h), which size every trade, are computed per outer split from its training
    blocks, and per inner fold from the inner training blocks. A test block's volatility therefore
    never sizes its own trades.
  - The frozen table, for the final model and the research-window test, comes from all six blocks.
  - The admissibility filter (V2.2) stays a single pass on the whole window. It decides only which
    pairs exist, and it reads volatility only.

**Selection metric.**
- The portfolio's daily net P&L in dollars at the 50K constraints is built with V2.7 and V2.8:
  - D is held at the MLL ($2,000), so there is no path dependence and the metric is fast;
  - cost is 1.0 x D8;
  - every cap applies.
- The score is the daily Sharpe, mean over sd across the validation dates, with zero on no-trade
  dates.
- A configuration is eligible on a split only with at least 30 trades in that split's validation
  set (V18).
- Ties go to the smaller model: ridge before LightGBM, then the larger lambda, then the smaller
  depth, then the larger k, then the shorter horizon.
- No eligible configuration: the split trades nothing.

**PBO (CSCV).**
- The matrix is the 45 configurations' CPCV out-of-sample daily net P&L on the full training
  window, averaged per date over the 5 paths.
- It is cut into 16 contiguous date blocks, giving C(16,8) = 12,870 combinations.
- PBO is the share of combinations where the in-sample best ranks below the out-of-sample median.

**Trial count N for the DSR (F4).** N_total = N_program + 45 + |Gate 0 tests|.
- N_program is the program's cumulative N at the freeze: 198 after E.9. E.10 screened nothing
  (V21).
- |Gate 0 tests| = |A| + |B| (V2.2b).
- The DSR's Sharpe variance is taken over the 45 configurations' CPCV out-of-sample daily Sharpes:
  the per-date average over the 5 paths, the same matrix as PBO. Two biases pull in opposite
  directions (design review D-22). The 45 share fits and are highly correlated, so their variance
  understates that of about 525 independent trials (lenient). The nested CV already removes the
  selection bias inside the 45, so counting them in N as well is conservative.
- What v2 adds to the program's carried N (design review D-20): 45 + |A| + |B| from the training
  window (phase-1 Gate 0 only), plus 1 for the research-window test of the frozen model. N_program
  is read from the program's ledger at the freeze.
- N accumulates across runs on real data (code review C-08). A second real-data run under a
  different configuration set or cost-gate reading adds its configurations and Gate 0 tests again.
  Runs on synthetic data add nothing. Each run's ledger counts only itself, so the freeze session
  passes N_program explicitly.
- Every v2 configuration and every Gate 0 test is written to the configuration ledger
  (ml_route_v2/configs.py) before its first fit, and N is read from that ledger.

**Training-window verdict (all must hold; fixed now).**
1. Gate 0 passed (V2.2b).
2. The nested OOS median-path daily t >= 3.0, the median of the 5 paths' t statistics (F4).
3. The DSR of the nested OOS daily series is > 0.95 at N_total.
4. PBO < 0.5.
5. Not a gate (design review D-09): the nested OOS annualized net Sharpe is reported against F1's
   band, 1.5 to 2.5. As a gate it would add only 1.37 -> 1.50 to criterion 2, and would make the
   band's lower edge a coin flip. Above 4.0 is a leakage alarm: the result is held for an
   independent leakage audit.
6. At least 30 completed round trips per product the model trades, out of sample; products below
   that are flagged and stay in.
7. Payout simulation (below) from the nested OOS daily records: the probability of ruin within 252
   trade dates is <= 10% at 50K and at 150K (F1's 10% convention).
   - **Ruin** = the MLL breached, OR D at or below 0.25 x MLL (the KS2b level) at any close (design
     review D-01). Under D-proportional sizing a breach is rare by construction, and the KS2b level
     is what ends the income.
   - It is read with KS1, KS3 and KS4 off. Daily records cannot time a stop's fill, so KS1 on would
     fill exactly at its level.
   - The plain breach probability and the figures with the switches on are reported beside it.

**Power of the training-window verdict** (design review D-09). On 4.82 years:
- at a true S = 1.5, criterion 2 (t >= 3) passes with probability Phi(1.5 x 2.195 - 3) = 0.61; at
  S = 2.0, 0.92;
- the DSR at N_total (about 525) adds a haircut that depends on the trials' Sharpe dispersion.
  With an annualized sd of 0.3 or 0.5, the expected maximum under the null is about 0.92 or 1.53,
  and the pass needs a Sharpe near 1.67 or 2.28 (illustration only);
- criterion 7 at S = 1.5 is about 0.29 analytically (V2.0), so a fixed-size S = 1.5 system fails
  it. A pass at S = 1.5 would come from the sizing-down mechanics.

So a system at the band's lower edge passes the training-window verdict less often than not. The
bar is honest about what a 4.8-year window can show. The 2010 extension (V2.1) is the lever that
raises power.

**Cost sensitivity** (design review D-08b).
- D8 is calibrated on 2025-26 books and understates costs in thinner earlier years. That cuts
  against an edge claim made on 2019-2024 (D8's own early-era note).
- So the nested OOS record is also re-priced at 1.5 x slippage, a stated multiple, not tuned, and
  reported beside every criterion. The registration decides whether a pass must survive it.

**F4's "final configuration"** (design review D-21). Different outer splits may select different
configurations, so the nested record measures the procedure. Beside criterion 2, the final
configuration's own CPCV OOS t and Sharpe (its column of the PBO matrix) are reported.

**The one research-window test (after the freeze, once).**
- The frozen model, the frozen decision layer and the frozen sizing run through the engine on the
  research window at the 50K constraints.
- **The research-window test is a screen, not an edge claim** (design review D-02, option (a)). It
  makes no Holm rejection. The route's confirmatory control is the DSR at N_total on the nested OOS
  record, plus the registered holdout-2 read. The route's slot in V21's Holm K = 10 is unused on
  the research window; the freeze session records that in docs/DECISIONS.md. The alternative,
  (b), is a Holm-level bar on the research window: t >= 2.58 at 0.05 / 10, with power 0.17 at
  S = 1.5 and 0.35 at S = 2.0 (V2.12 item 14).
- Pass needs all of:
  - mean daily net P&L > 0;
  - one-sided daily t >= 1.0 (D5's screen level);
  - at least 30 completed round trips (V18, V21);
  - KS4 does not fire.
- Power at t >= 1.0 on 1.19 years (Phi(S x sqrt(1.19) - 1.0)): about 0.74 at S = 1.5 and 0.88 at
  S = 2.0. The window cannot do more (V2.0). Open: the bar, or t >= 1.645 (power about 0.50 at
  S = 1.5 and 0.70 at S = 2.0).

**Then:**
- a registered holdout-2 read, the user's registration only (REGISTRATION.md), with criteria fixed
  in that registration;
- then paper trading on a TopstepX Practice account (D9.10) for at least 40 trade dates. Pass:
  KS4 does not fire, and realized costs are within 1.25 x the modelled D8 costs. Open.

**Portfolio economics, reported for both account sizes.**
- Daily P&L in dollars at the 50K constraints (the engine) and the 150K constraints (the re-sized
  records), against eps at the portfolio level ($85 a day per 50K account, D3).
- The 150K figures are a LOWER BOUND on income (design review D-10). The trade set is the 50K
  run's: trades that only 150K sizing would take are absent, and the CPI micro cap (3, vs 150K's 9),
  the D9.11 caps and the scaling tiers are 50K's. For ruin they rest on a different trade set
  from a true 150K run.
- F1's Sharpe lines at 1.0, 1.5 and 2.0.

**Payout simulation (F9; ml_route_v2/payout_sim.py).**
- Inputs: per trade date, the list of trades, each with product, horizon, P&L per contract in
  dollars, worst intraday P&L per contract (the adverse excursion), and the risk quantities of V2.8.
- Paths:
  - 10,000 paths of 252 trade dates;
  - a stationary block bootstrap of trade dates, mean block 10, seed 20261003;
  - each path re-sizes every trade with V2.8 from the path's own D;
  - the intraday drawdown is approximated conservatively as the sum of the trades' worst
    excursions.
- Account mechanics, from rules/xfa_rules.py and the facts file:
  - the trailing MLL path, its lock and its post-payout reset;
  - DLL off and DLL on, where the DLL truncates the day at -DLL, triggered by the intraday worst;
  - the Standard path: 5 winning days of $150 or more since the last payout, the request day not
    counting;
  - the Consistency path: 3 days traded, largest winning day <= 40% of net profit in the window;
  - the 50%-of-balance ceiling, the per-account caps, the $125 minimum, the 90/10 split.
- Payout policy (fixed): on the first eligible date, request the largest amount that leaves
  D >= 0.5 x MLL. The amount is min(cap, x 2 with the DLL; 50% of balance; balance - 0.5 x MLL),
  requested only if it is at least the $125 minimum. A payout therefore never triggers KS2 or KS2b
  by itself. The plain "largest allowed amount" policy halted accounts after small early payouts
  (Task 4 finding). Open.
- A breach ends the account. A new XFA would need a new Combine: its cost and delay are parameters
  the freeze session fills from Topstep's pricing page. Open. Reported as the expected resets per
  year and their cost.
- Five copied accounts are one draw (F11): payouts x 5, the same ruin.
- Outputs per account size and path type:
  - monthly net payouts (mean, median, 10th and 90th percentiles);
  - the probability of ruin within 252 dates;
  - the probability of a halt (KS2b);
  - days to the first payout.
- Tests pin a hand-computed payout sequence for each path type.

**Leakage controls (v1 M7, kept in full, plus the v2 canaries in tests/test_ml_v2_leakage.py).**
- The feature-timestamp validator.
- The perturbation test: bars after t are randomized and the features and predictions at t must
  not change.
- The fold test (purge and embargo).
- The window test: no date on or after 2024-03-01 in any fit or normalization.
- The normalization test.
- The model hash chain.
- The planted canaries: a future bar, a future release, a target shuffled across dates that must
  find no edge (a shuffle within a date is not a valid null, because the lagged cross-product
  features legitimately see other products' earlier same-day moves), a
  peeking normalizer, a selection step that sees the test block, a label overlapping the test fold
  (the purge must remove it), a product shifted by one minute, and Gate 0's three (pure noise
  fails; a planted gross edge passes; a sub-hurdle edge passes Gate 0 and is rejected by the cost
  gate, V2.2b). Each must be caught.

---

## V2.10 Deployment (open)

**(a) Frozen model.**
- The selected configuration's weights (ridge coefficients, or the LightGBM model file),
  normalization windows and decision rules are fixed and hashed. They are never retrained live.
- For ridge, the frozen model is one readable linear formula over z-scored features: in effect a
  plain rule with many terms.
- Trade-offs:
  - it is what was tested, with no extra trials;
  - it replaces the "deployed bot runs plain rules" decision of 2026-09-24 (V20);
  - Topstep's "unfair technology ... AI" clause (D9.9) may need a support answer first.

**(b) A distilled rule set, as v1's M5.**
- Depth-2 surrogates of the frozen model's predictions per cluster, at fixed cut points, each leaf
  a plain rule.
- Trade-offs:
  - closest to the plain-rules decision;
  - but it adds trials;
  - it loses the portfolio's combination (the reason v2 exists, V21);
  - and v1's M5 machinery would have to be re-run.

Recommendation (the user decides): (a), a frozen ridge model, if the user accepts V20's open point.

---

## V2.11 Compute (open)

- ThinkPad: 20 threads, 14 GB, RTX 3050 4 GB, the overnight profile. Ridge and shallow LightGBM
  need no GPU.
- **Runtime probe (Task 5, synthetic data at full scale; reports/stage_e11_runtime_probe.md):**
  - 8 products (the phase-1 size), the full grid of 45 configurations, nested CPCV, the engine on 5
    paths and payouts: **20.4 min measured end to end**, peak 3.1 GB, 60 MB on disk.
  - 28 products: **about 46 min extrapolated** from measured stages. The biggest pieces are the
    nested CPCV at about 12 min and the engine at 28 min for 5 paths. The engine stage peaked at
    7.2 GB, 73% of the memory free at launch: over the 70% rule. The pipeline is being changed to
    free the bars before simulating, or to run each engine path in its own process.
  - Both sizes fit one 8-to-10-hour window with room to spare. Checkpoints are at every stage, plus
    one per (configuration, split, fold) unit inside the CPCV.
  - The 2010 extension triples the dates. Scaling linearly, that is about 2.5 h at 28 products,
    still one window. Memory is the binding limit there (design review D-17): about 2.4 GB of the
    7.2 GB is bars, and tripling them breaks the 70% rule. So the extension runs each engine path
    in its own process and builds the panel in date chunks.
  - The ThinkPad is sufficient; the Windows PC is not needed for v2's grid.
- The Windows PC (V10, 32 GB) if the user prefers it (V12). Only training-window data is sent,
  never holdout or research-window data (V10-4).
- Another host the user names.
- The runtime probe (reports/stage_e11_runtime_probe.md, Task 7) gives each host its wall time,
  peak memory and disk, and splits the full grid into 8-to-10-hour windows that pause at
  checkpoints (V12). The CPCV ledgers are resumable per configuration x split, as v1 M8.

---

## V2.12 What the user decides (collected)

Each item gives the built default and the lead's recommendation. Items 1 to 3 are coupled.

1. **The Gate 0 bar, the cost-gate reading and tau: one coupled decision** (V2.2, V2.2b, V2.7;
   design review D-05, D-14).
   - Built default (literal F7):
     - hurdles 2.5c / 3c / 4c;
     - tau 0.10;
     - Gate 0: mean gross >= 1.5 x c on the top-20% confident trades, t >= 3, Holm 0.05 over
       families A and B (operative z about 3.57), >= 30 trades.
   - Alternative (gross): hurdles 1.5c / 2c / 3c, tau 0.167, Gate 0 at 1.5c = the loosest hurdle.
   - Alternative (pre-cost Gate 0, F2's wording): no cost multiple in Gate 0, only the t, Holm and
     trade-count bars. Under it the prompt's canary sentence ("an edge smaller than the cost passes
     Gate 0 and is rejected by the cost gate") holds literally.
   - Also: whether family A counts in the Holm family (z 3.57 with it, 3.24 without).
   - Lead recommends: the gross reading, with Gate 0 at 1.5c and family A in the Holm family.
2. **The phase-1 subset rule** (V2.1): the liquidity tier by median ADV, then c / sigma_proxy, then
   the cluster round-robin, greedy to the budget. Lead recommends: as written.
3. **The volatility proxy**: the CME maintenance margin, or the frozen E|m_1|. Lead recommends: the
   margin (it reads no window of ours); E|m_1| if CME's pages block the fetch.
4. **Phase-1 scope**: the training window only, with holdout-2 deferred to phase 2 (a departure from
   V1), or the full step 2 range per V1. Lead recommends: training window only, so more products
   fit the budget for Gate 0.
5. **The 2010 extension**: a free quote at the freeze. Buying needs a D4 start-rule amendment and
   follows only a Gate 0 pass. Lead recommends: quote it at the freeze. It is the only lever that
   makes a Sharpe near 1 detectable (V2.0).
6. **The decision clock and horizons** (V2.2): three times by rule, h in {60, 120, F}. Lead
   recommends: as written.
7. **The roll-blackout rule** (V2.2): a signal leg's roll date makes the features reading it not
   applicable, replacing D4's union for v2. Lead recommends: as written.
8. **The signal library** (V2.3):
   - all 54 families, ports pooled, and the generic list G1-G19;
   - excluded: K5-fomc and K6-wasdepost, which fall after the last decision time, and K9-anncday,
     whose calendar is uncovered.
   - Lead recommends: as written, and building EC-K9 for 2019-2024 from official pages in the
     freeze session (a sourced-data task) so K9-anncday can enter.
9. **The research-window warm-up** (V2.4): skip the sealed gap, or the window's own bars only (the
   t >= 1.0 screen's power at S = 1.5 drops from 0.74 to 0.58-0.66). Lead recommends: skip the gap.
10. **The grids** (V2.6): ridge lambda in {0.01, 0.1, 1.0}; LightGBM depth in {2, 3}; k in
    {1.5, 2, 3}; 45 configurations. Lead recommends: as written.
11. **Sizing constants** (V2.8):
    - 0.10 x D, 0.25 x D, m = 3, the daily risk budget, the 99th-percentile loss proxy, the
      rounding band (one contract up to 2 x b), one extra tick per side beyond q_c;
    - at most 3 positions and 1 per cluster; the portfolio at the tier minus 0.1 lot.
    - The last is within D9.5's letter (never at full Maximum Position Size). But it keeps a 5%
      margin where D9.5's member rule kept 50% (design review D-11). Alternative: no new entry with
      a fill in [release - 5 min, release + 30 min) while open lot-equivalents exceed half the
      tier.
    - Lead recommends: add that alternative; it costs little.
12. **The 150K parameters**: the MLL $4,500 and the XFA scaling schedule (an image on Topstep's
    page). Until confirmed, the 50K tiers and D9.11's 50K caps apply, and every 150K figure is a
    lower bound on income (D-10). Lead recommends: the freeze session reads both from Topstep.
13. **Kill-switch thresholds**: KS1 -0.30 x D_open; KS2 0.50 x MLL; KS2b 0.25 x MLL; KS3 five
    losing dates; KS4 3 standard errors over 40 dates; KS5 2 and 5 minutes. Lead recommends: as
    written.
14. **The success criteria** (V2.9):
    - Training window: median-path t >= 3, DSR > 0.95 at N_total, PBO < 0.5, ruin <= 10% (breach
      or the KS2b level, switches off), >= 30 trades per product.
      - Sharpe against the band is reported, not gated (alternative: keep Sharpe >= 1.5 as a gate).
      - Eligibility on every split (alternative: a majority of splits).
    - Research window: a screen only (mean > 0, t >= 1.0, >= 30 trips).
      - Alternatives: t >= 1.645, or (b) a Holm-level t >= 2.58.
    - Paper trading: 40 dates; realized costs within 1.25 x D8.
    - The 1.5 x slippage sensitivity is reported beside each criterion. Whether a pass must survive
      it is the registration's choice.
    - Lead recommends: as written, with the sensitivity as a must-survive condition in the holdout-2
      registration.
15. **The payout policy** (V2.9): request at the first eligibility the largest amount leaving
    D >= 0.5 x MLL; the reset cost and delay; Standard versus Consistency; DLL on or off. Lead
    recommends: as written; decide the path type and DLL from the payout simulation's outputs.
16. **Deployment** (V2.10): (a) a frozen model, or (b) distilled rules. Lead recommends: (a).
17. **The compute host** (V2.11): the ThinkPad (the full grid takes under 1 hour at 28 products), or
    the Windows PC. Lead recommends: the ThinkPad.
18. **The Live Funded risk (F12).**
    - Topstep's Live Funded Account does not allow API trading: "Live funded accounts are not
      allowed to trade through the ProjectX API" (facts F12.2g, D9.10). The bot runs on XFAs only.
    - A call-up to Live Funded ends automated trading on that account. Its income stops unless the
      user trades it by hand, and the program already models the call-up as terminal.
    - The income path (V22) plans for this. XFA payouts fund a personal account, where the same
      frozen model can run without an MLL.
    - The user decides whether to accept a call-up, or decline it if Topstep allows, before the
      first funded account.
19. **The purchase**: the phase-1 budget (acct-1 about $28.41 headroom, then acct-2 $125 after the
    cap raise to about $249.67). The purchasing session raises the cap and logs a fresh quote first.

**Lead decisions, not open, shown so nothing is silent** (design review D-16):
- The selection metric: the fixed-D (the 50K MLL) daily Sharpe with zeros on no-trade dates, at
  1.0 x D8.
- The model is fit on the gross normalized target, and the cost gate comes after it.
- The DSR Sharpe variance is taken over the 45 configurations' path-averaged OOS Sharpes.
- The research-window test runs at the 50K constraints only, though the plan is 5 x 150K.
- The tie-break order: ridge, larger lambda, smaller depth, larger k, shorter horizon.
- Ruin is read with the kill switches off.
- The engine and payout figures come from the nested OOS schedule (5 paths), not from the
  in-sample final refit.
- The combined-MLL audit counts as a breach.

**What the freeze session needs:**
- the decisions above;
- the CME margin table, or the E|m_1| choice;
- Topstep's 150K MLL and scaling schedule;
- the reset price;
- a fresh phase-1 quote under the subset rule;
- the EC-K9 calendar for 2019-2024, if item 8 is accepted;
- this file and its build hashed into a v2 freeze manifest;
- the program N at that date, read from the ledger;
- a docs/DECISIONS.md entry for the route's unused research-window Holm slot (V2.9).
