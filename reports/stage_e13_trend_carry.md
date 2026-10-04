# Stage E.13 Task 2: trend and carry after publication, small-account sizing, prop-firm fit

Worker: TrendCarry-OpusHigh. Written 2026-10-03 (PDT). Evidence pages: reports/stage_e13_briefs/pages/TrendCarry/
(fetch_log.md lists every fetch, failures included). Helper scripts: the worker's scratchpad folder
(instruments.py, sizing.py, emdd.py, ruin.py, partd.py, sgstats.py, tsstats.py, carrystats.py).

No program bars, cost samples or Gate 0 figures were read. Volatilities, prices and multipliers come from published
sources (Carver's published minimum-capital report, Huang et al. 2020 Table 1, a broker's spec table, US Treasury par
yields). The only program inputs are design-doc figures: the RT_X cost wall per vehicle and the V2.0 arithmetic.
Statistics marked "computed" are this worker's arithmetic on a published series. A second worker has not checked them.

## Summary

- Trend after publication is weak. The SG Trend Index (net of fees) ran a Sharpe ratio of 0.24 over 2010-2025 and 0.30
  over 2013-2025, with a worst monthly drawdown of -20.6%. AQR's updated MOP factor (gross) ran 0.34 over 2010-2025 and
  0.31 over 2012-2025 (t = 1.18), against 1.41 over 1985-2009.
- Cross-sectional carry after publication is gone in AQR's own updated factors (gross): -0.19 over 2013-2025, against
  0.92 over 1972-2012.
- Carver's sizing formula and his small-account rules are quoted from his public code and blog. At $10K to $100K a
  diversified micro portfolio is feasible, but it fills up with the lowest-risk micros (FX, yields, micro grains).
- At a mid post-2010 Sharpe the expected income is about $40 a month at $10K and about $430 a month at $100K (25% vol
  target, after costs). The expected 10-year maximum drawdown is 76% to 103% of capital at a 25% target, and 46% to 56%
  at 15%.
- Prop fit: one micro in each instrument a diversified portfolio would hold already runs $169 to $2,432 a day of P&L
  sigma. A 10% one-year trailing-ruin bound allows only D/25 to D/29 a day ($69 to $295 across the D grid). Only the 10
  smallest micros fit, and only at D >= $5,000.

## Part A: evidence

### A1. Moskowitz, Ooi and Pedersen (2012, JFE), "Time series momentum" [T-01; update T-09]
- Markets and sample: 58 liquid futures and forwards (24 commodities, 12 cross-currency pairs, 9 equity indices, 13
  government bonds). Data run January 1965 to December 2009, and the main results use 1985-2009.
- Construction: sign of the past 12-month excess return, held 1 month. Each position is sized to 40% ex-ante annual
  volatility, and the equal-weighted factor runs at about 12% a year.
- Published Sharpe ratio: "a Sharpe ratio greater than one on an annual basis". This is gross: the per-instrument
  figures are labelled "gross Sharpe ratio", and no transaction costs or fees are deducted.
- After publication (computed from AQR's monthly-updated factor file, T-09, which extends the paper's factor; the file
  states no cost or fee deduction):

| Period | Months | Mean (ann.) | Vol (ann.) | Sharpe | t | Worst DD | Commodities / Equities / Bonds / FX Sharpe |
|---|---|---|---|---|---|---|---|
| 1985-01..2009-12 (in-sample) | 300 | 16.84% | 11.93% | 1.41 | 7.06 | -15.1% | 1.01 / 0.83 / 0.71 / 0.78 |
| 2010-01..2025-12 | 192 | 4.48% | 13.11% | 0.34 | 1.37 | -27.9% | 0.11 / 0.07 / 0.45 / 0.15 |
| 2012-01..2025-12 (post-publication) | 168 | 4.17% | 13.23% | 0.31 | 1.18 | -27.9% | 0.12 / 0.15 / 0.33 / 0.17 |
| 2010-01..2019-12 | 120 | 5.91% | 12.96% | 0.46 | 1.44 | -22.9% | -0.04 / 0.26 / 0.65 / 0.31 |
| 2020-01..2025-12 | 72 | 2.08% | 13.42% | 0.16 | 0.38 | -24.6% | 0.36 / -0.19 / 0.14 / -0.11 |

Post-publication strength: Sharpe 0.31 (gross, t = 1.18), 2012-01..2025-12, T-09.

### A2. Hurst, Ooi and Pedersen, "A Century of Evidence on Trend-Following Investing" [T-02 (2014 white paper), T-03 (JPM Fall 2017)]
- Sample: 67 markets (29 commodities, 11 equity indices, 15 bonds, 12 currency pairs). The white paper runs January 1880
  to December 2013; the JPM version runs to the end of 2016.
- Construction: equal-weighted 1-, 3- and 12-month signals, each position vol-targeted, portfolio at 10% ex-ante vol.
- Costs and fees: net of simulated transaction costs (time-varying, higher historically). Fees are simulated as 2/20:
  "To simulate fees, we apply a 2% management fee".
- Results (2014 white paper, Exhibit 1): 1880-2013 net-of-fee Sharpe 0.77 (gross-of-fee return 14.9%, net 11.2%,
  volatility 9.7%). The latest window, Jan 2000-Dec 2013, has a net-of-fee Sharpe of 0.62.
- The authors illustrate a lower future Sharpe with: "only realizes a Sharpe ratio of 0.4 net of fees and"
  (transaction costs).
- The JPM 2017 decade table (Exhibit 1) is an image in the saved PDF, so its 2014-2016 numbers are not extractable.
  Those are UNSOURCED here.
- After publication: AQR's follow-up (Babu et al. 2020, JPM; T-04) reports that "From January 1, 2010, through" /
  "December 31, 2018, the SG Trend Index realized an annualized" / "Sharpe ratio of 0.05, versus a Sharpe ratio of 0.28
  from the incep-" (tion of the index in 2000 through 2018). The quote is split at PDF line breaks. It attributes the gap mainly to smaller market moves, not to lost
  trend efficacy.

Post-publication strength: SG Trend Sharpe 0.05, 2010-2018, T-04 (and 0.30 for 2013-2025, A3).

### A3. Out-of-sample record: SG Trend Index, 2010-2025 [T-05 data file; T-07 index definition; T-08 cross-check]
Source of the series: AQR publishes, in its AQR Managed Futures Strategy Fund track-record workbook (T-05), monthly
returns for the fund, the ICE BofA 3M T-bill index and the SG Trend Index from January 2010 to September 2026. SG's own
history is sold through LSEG and was not fetched.

The SG Trend Index "calculates the net daily rate of return for a pool of trend following based hedge fund managers"
(T-07), so its returns are net of fees and costs.

Cross-checks:
- SG's February 2015 release (T-08) gives the then-named Newedge Trend Index at -0.14% for February and +4.94% YTD.
  The AQR file gives -0.26% and +4.80%, a small mismatch that is recorded rather than resolved.
- The AQR file's 2010-2018 monthly Sharpe of 0.08 is consistent with T-04's 0.05 (computed on a different frequency).

Annual returns (computed by compounding the monthly figures):

| Year | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SG Trend % | 10.64 | -7.93 | -3.52 | 2.67 | 19.70 | 0.04 | -6.16 | 2.23 | -8.11 | 9.23 | 6.28 | 9.09 | 27.29 | -4.08 | 2.63 | 2.56 |
| AQMIX % (live fund, net) | 5.41 | -6.37 | 2.99 | 9.40 | 9.69 | 2.00 | -8.43 | -0.97 | -8.88 | 1.93 | -0.41 | -1.06 | 35.38 | 1.80 | 8.41 | 14.63 |

The AQMIX 2017-2025 figures match the June 2026 factsheet's calendar-year row exactly (T-06).

| Series (monthly, computed) | Window | Ann. return | Ann. vol | Sharpe (excess of 3M T-bill) | Worst DD (trough) |
|---|---|---|---|---|---|
| SG Trend Index | 2010-2025 | 3.50% | 11.33% | 0.24 | -20.62% (2019-01) |
| SG Trend Index | 2013-2025 (post-2012) | 4.46% | 11.17% | 0.30 | -20.62% (2019-01) |
| SG Trend Index | 2010-2019 | 1.52% | 11.45% | 0.14 | -20.62% |
| SG Trend Index | 2020-2025 | 6.87% | 11.16% | 0.40 | -20.06% (2025-05) |
| AQMIX (fund, net) | 2010-2025 | 3.63% | 10.01% | 0.27 | -24.40% (2019-02) |
| AQMIX (fund, net) | 2013-2025 | 4.35% | 10.25% | 0.30 | -24.40% |

The AQMIX factsheet reports a "Realized Since Inception Sharpe Ratio" of 0.26 (T-06). Monthly drawdowns understate
daily ones.

### A4. Koijen, Moskowitz, Pedersen and Vrugt, "Carry" (JFE 2018; read from NBER WP 19325, August 2013) [T-10; update T-11]
- Construction: carry is the futures return if prices stay constant. Strategies go long high-carry and short low-carry
  assets within each asset class; the global factor is inverse-vol weighted across classes. Results are gross.
- The authors note: "the carry strategy faces larger transaction costs, greater funding issues, and" limits to
  arbitrage.
- Samples end in September 2012: currencies from November 1983, bonds from August 1971, commodities from 1980.
- Sharpe by asset class (Table II, Panel A): global equities 0.88; 10Y global bonds 0.52; 10Y-2Y slope 0.66; US
  Treasuries 0.68; commodities 0.60; currencies 0.68; credit 0.47; index calls 0.37; puts 1.80. The average is 0.74.
  The diversified "global carry factor" has a "remarkable Sharpe ratio of 1.10 per annum" (mean 6.75%, vol 6.12%).
- After publication: AQR's monthly-updated cross-sectional carry factors (Century of Factor Premia, T-11). The file
  says "returns are presented gross of trading costs and fees" (computed):

| Window | Equity-index carry | Bond carry | FX carry | Commodity carry | All macro carry (diversified) |
|---|---|---|---|---|---|
| 1972-01..2012-09 | 0.33 | 0.51 | 0.50 | 0.64 | 0.92 (t 5.90, vol 3.7%) |
| 2010-01..2025-12 | -0.47 | -0.06 | 0.21 | 0.27 | -0.02 (t -0.08) |
| 2013-01..2025-12 (post-publication) | -0.74 | -0.07 | 0.15 | 0.20 | -0.19 (t -0.68), worst DD -15.3% |
| 2019-01..2025-12 (after JFE print) | -0.19 | -0.43 | 0.29 | 0.30 | -0.12 |

Caveat: these are AQR's simplest cross-sectional (long/short) carry factors, not the time-series carry rule Carver
trades. No published post-2012 record of time-series futures carry was found; that gap is UNSOURCED.

Post-publication strength: diversified cross-sectional carry Sharpe -0.19 (gross), 2013-2025, T-11.

### A5. Critiques and other post-publication evidence
- Huang, Li, Wang and Zhou (2020, JFE), "Time series momentum: Is it there?" [T-12]. 55 assets, 1985:01-2015:12.
  - Asset-by-asset: "47 of the 55 assets have a t-statistic of less than 1.65".
  - The pooled t-statistic is below bootstrap critical values.
  - "From an investment perspective, the TSM strategy is proﬁtable, but its perfor-" /
    "mance is virtually the same as that of a similar strategy that is based on historical sample" (mean); split at
    PDF line breaks. In other words, much of TSMOM's profit is a long-the-assets-that-drifted-up
    effect, not predictability.
- Baltussen, Swinkels and van Vliet, "Global Factor Premiums" (Jan 2019 version; JFE 2021) [T-13].
  - In the "new sample" (1800-1980 plus post-sample 2012-2016), gross multi-asset Sharpe ratios are 0.98 for trend
    and 0.91 for carry.
  - This shows little decay, but the new sample is overwhelmingly pre-1980. Only five of its years are
    post-publication.
- Falck, Rej and Thesmar (2021) [T-14]. On published equity anomalies (context, not futures): "the Sharpe ratio drops
  by 43%" after publication.
- Babu et al. (2020) [T-04]. Trend's 2010s weakness is attributed to smaller market moves (A2).

### Evidence table

| Effect | Published Sharpe | Sample | Markets | Holding | Post-publication | Since 2010 | Source keys |
|---|---|---|---|---|---|---|---|
| TSMOM (MOP 2012) | >1, gross | 1965/1985-2009 | 58 futures, 4 classes | 12m signal, 1m hold | 0.31 gross, 2012-2025 (t 1.18) | 0.34 gross, 2010-2025 | T-01, T-09 |
| Century trend (HOP) | 0.77 net of 2/20 and costs; 0.62 for 2000-2013 | 1880-2013 (2016 in JPM) | 67 | 1/3/12m blend | SG Trend 0.05 for 2010-2018 | SG Trend 0.24 net, 2010-2025 | T-02, T-03, T-04, T-05 |
| CTA index (SG Trend) | n/a (live record, net) | 2000- | ~10 largest trend CTAs | multi-speed | 0.30 net, 2013-2025; worst DD -20.6% | 0.24 net, 2010-2025 | T-05, T-07 |
| Carry (KMPV) | 1.10 diversified, 0.74 average by class, gross | ~1972/1983-2012-09 | equities, bonds, FX, commodities, credit, options | monthly | -0.19 gross, 2013-2025 (AQR cross-sectional) | -0.02 gross, 2010-2025 | T-10, T-11 |
| TSMOM critique (HLWZ) | TSM roughly equal to sample-mean strategy | 1985-2015 | 55 | 12m/1m | n/a | n/a | T-12 |
| Global factors (BSV) | trend 0.98, carry 0.91 (new sample), gross | 1800-1980 and 2012-2016 | 4 classes | monthly | 2012-2016 not separated | n/a | T-13 |

## Part B: Robert Carver's small-account guidance (quoted)

- Minimum-capital formula (his code, T-25; his report, T-22). Minimum capital = minimum position x multiplier x price
  x FX x annual vol% / (risk target x IDM x instrument weight). In code:
  "min_contracts_held * single_contract_min_capital / (idm * instrument_weight)", where single-contract capital is
  "base_multiplier * price * ann_perc_stdev / (risk_target)". The report header states the same as "E * F / ( G * H)".
- Assumptions in his published report (T-24):
  - "RISK_TARGET_ASSUMED = 25", INSTRUMENT_WEIGHT_ASSUMED = 0.04, IDM_ASSUMED = 2.5, MIN_CONTRACTS_HELD = 4.0.
  - His backtest default vol target is "percentage_vol_target: 16.0" (T-26).
- Recommended minimum position:
  - "In fact I recommend that you are holding at least 4 contracts at the maximum forecast." (2016, T-15)
  - Later: "if we can't hold at least three contracts with a maximum forecast of 20 (twice the average forecast)"
    (2021, T-19).
  - Penalty for small positions: "a Sharpe ratio penalty of around 20% if you can only hold one contract or 5% if you
    can only hold two." (T-15)
- Risk target: "your optimal risk target would be 50%. ... A better rule of thumb is to use half the optimal risk
  target. In this case we'd use a risk target of 25%." That is for a Sharpe of 0.5 (T-17). On the same rule, the
  post-2010 Sharpe of 0.3 gives 15%, and 0.15 gives 7.5%.
- Capital guidance:
  - "at least until you have $100K or so" use binary or thresholded forecasts across as many instruments as possible
    (T-15).
  - Systematic Trading systems "require large amounts of money (at least £100,000; around $130,000). The Starter
    System in LT needs just £1,100 or $1,500." (T-16)
  - His 2016 ladder holds 3 instruments at $10,000, 6 at $50,000 and 8 at $100,000 (T-15). His current static
    selection report lists 8 instruments at 10,000, 13 at 25,000, 19 at 50,000 and 28 at 100,000 (T-23; GBP base,
    many non-US markets).
- Rounding, buffering and dynamic optimisation:
  - Positions are buffered ("buffer_size: 0.10", T-26; "this is done using buffering to reduce trading costs", T-21).
  - At $50K (in a 45-instrument test also run at $100K), dynamic optimisation beats simple rounding: "So the
    optimised version is still better than the rounded (SR improvement around 0.1), but nowhere near as good as the
    unrounded (SR penalty around 0.2)." (T-20)
- Instrument choice (T-18, T-24):
  - "As a rule of thumb anything with a cost above 0.01SR is going to be too expensive" (per trade, in Sharpe units).
  - Markets are rejected if they fail "the maximum cost test (0.01SR), maximum risk per contract ($125,000) or minimum
    volume ($1.25 million per day in risk units, and 100 contracts per day)".
  - The code constants match: "MAX_SR_COST = 0.01", MIN_VOLUME_CONTRACTS_DAILY = 100.
- Vol estimate in his report: 70% of a 35-day EWMA plus 30% of a 10-year vol ("proportion_of_slow_vol: 0.3", T-26).
  The report's vols are a blend of the recent and the long run as of 2026-10-02.
- Not sourced: the exact text of his books (AFTS, Leveraged Trading). Book-only figures, such as a printed IDM-by-count
  table, are not used. IDM here comes from his code's definition, "1 / [ ( W x H x WT ) 1/2 ]", capped at 2.5 (T-27).

## Part C: sizing

### C1. Formula and assumptions
- Annual $ risk of one contract = multiplier x price x annual vol (FX = 1, all USD).
- Single-contract capital at vol target tau = $risk / tau. In a portfolio with weight w and IDM, divide by (w x IDM);
  Carver's minimum multiplies by 4 contracts.
- Vol target: 25% is Carver's reporting assumption and his half-Kelly at Sharpe 0.5. 15% is shown because it is
  half-Kelly at the post-2010 mid Sharpe of 0.3. The evidence in Part A argues for 15% or less.
- Volatilities: Carver's published report of 2026-10-02 (T-22). His "point_size_base" is in GBP; the USD-to-GBP rate
  0.75719 is backed out of CAD_micro's 7,571.9 for 10,000 CAD. The $ risk uses the report's unrounded single-contract
  capital x 0.25 / 0.75719 and matches multiplier x price x vol within 1% (6J within 6%, from price rounding).
- Micro yield futures: realized 252-day vol of Treasury par yields to 2026-10-02 (T-30), times the $10 DV01 (T-28).
- Long-run cross-check: Huang et al. 2020 Table 1, 1985-2015 (T-12).
- The FX vols in T-22 (4-7%) are about half their 1985-2015 levels (7-12%). A long-run rerun is in C3.
- No micro NZD contract appears in T-28's table, so 6N is full-size (UNSOURCED whether a micro exists).
- Lean hogs and live cattle have no micro in T-28; they are full-size.
- Margins were not used (cross-check not done).

### C2. Per-instrument table (all USD; "Cl" is the program's cluster)
| Code | Exposure | Cl | Listed (src) | Size | Price 2026-10-02 (T-22) | Ann. vol % (T-22) | Long-run vol % 1985-2015 (T-12) | $ risk / contract / yr | $ risk / day | Lone, 1 contract, tau 25% | Lone, tau 15% | In portfolio, 1 contract (w 0.04, IDM 2.5, tau 25%) | Carver 4-contract minimum (w 0.04, IDM 2.5, tau 25%) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MES | S&P 500 | K1 | T-28 | $5 x index | 7775.5 | 10.7 | 15.2 | 4,176 | 263 | 16,703 | 27,838 | 167,025 | 668,102 |
| MNQ | Nasdaq-100 | K1 | yes; program vehicle + T-28 | $2 x index | 31039.8 | 15.7 | - | 9,743 | 614 | 38,973 | 64,955 | 389,730 | 1,558,922 |
| M2K | Russell 2000 | K1 | yes; program vehicle + T-28 | $5 x index | 2851.7 | 14.1 | - | 2,014 | 127 | 8,057 | 13,429 | 80,574 | 322,297 |
| MYM | Dow | K1 | yes; program vehicle + T-28 | $0.50 x index | 51441 | 11.3 | - | 2,915 | 184 | 11,660 | 19,434 | 116,602 | 466,409 |
| ZT | 2-year | K2 | yes; program vehicle | $2,000/pt | 101.754 | 1.5 | 1.67 | 3,116 | 196 | 12,465 | 20,774 | 124,645 | 498,580 |
| ZF | 5-year | K2 | yes; program vehicle | $1,000/pt | 103.43 | 3.5 | 4.3 | 3,581 | 226 | 14,325 | 23,876 | 143,253 | 573,013 |
| ZN | 10-year | K2 | yes; program vehicle | $1,000/pt | 104.344 | 5.0 | 7.6 | 5,186 | 327 | 20,742 | 34,571 | 207,425 | 829,699 |
| TN | Ultra 10-year | K2 | yes; program vehicle | $1,000/pt | 105.094 | 6.1 | - | 6,453 | 407 | 25,814 | 43,023 | 258,139 | 1,032,555 |
| ZB | Bond | K2 | yes; program vehicle | $1,000/pt | 102.688 | 9.4 | 16.44 | 9,703 | 611 | 38,812 | 64,687 | 388,119 | 1,552,477 |
| UB | Ultra bond | K2 | yes; program vehicle | $1,000/pt | 103.625 | 11.0 | - | 11,366 | 716 | 45,464 | 75,774 | 454,642 | 1,818,566 |
| MTN | Micro Ultra 10-year | K2 | T-28 | $10K note ($100/pt) | 105.094 | 6.1 | 7.6 | 645 | 41 | 2,581 | 4,302 | 25,814 | 103,255 |
| MWN | Micro Ultra bond | K2 | T-28 | $10K bond ($100/pt) | 103.625 | 11.0 | 16.44 | 1,137 | 72 | 4,546 | 7,577 | 45,464 | 181,857 |
| 6E | EUR | K3 | yes; program vehicle | EUR 125,000 | 1.128 | 5.6 | 11.02 | 7,859 | 495 | 31,435 | 52,391 | 314,346 | 1,257,386 |
| 6A | AUD | K3 | yes; program vehicle | AUD 100,000 | 0.695 | 7.2 | 12.03 | 5,028 | 317 | 20,113 | 33,521 | 201,125 | 804,501 |
| 6B | GBP | K3 | yes; program vehicle | GBP 62,500 | 1.324 | 5.7 | 10.14 | 4,747 | 299 | 18,989 | 31,648 | 189,886 | 759,545 |
| 6C | CAD | K3 | yes; program vehicle | CAD 100,000 | 0.704 | 4.3 | 7.44 | 3,028 | 191 | 12,111 | 20,184 | 121,106 | 484,423 |
| 6J | JPY | K3 | yes; program vehicle | JPY 12.5M | 0.00635 (backed out) | 9.1 | 11.12 | 7,220 | 455 | 28,880 | 48,134 | 288,805 | 1,155,219 |
| 6S | CHF | K3 | yes; program vehicle | CHF 125,000 | 1.217 | 7.0 | 11.77 | 10,666 | 672 | 42,664 | 71,107 | 426,643 | 1,706,573 |
| 6N | NZD | K3 | yes; program vehicle | NZD 100,000 | 0.563 | 7.8 | 12.31 | 4,408 | 278 | 17,632 | 29,387 | 176,323 | 705,292 |
| M6E | Micro EUR | K3 | T-28 | EUR 12,500 | 1.128 | 5.6 | 11.02 | 787 | 50 | 3,150 | 5,250 | 31,498 | 125,992 |
| M6A | Micro AUD | K3 | T-28 | AUD 10,000 | 0.695 | 7.3 | 12.03 | 504 | 32 | 2,018 | 3,363 | 20,180 | 80,720 |
| M6B | Micro GBP | K3 | T-28 | GBP 6,250 | 1.324 | 5.7 | 10.14 | 473 | 30 | 1,893 | 3,154 | 18,925 | 75,701 |
| MCD | Micro CAD | K3 | T-28 | CAD 10,000 | 0.704 | 4.3 | 7.44 | 304 | 19 | 1,218 | 2,029 | 12,177 | 48,706 |
| MJY | Micro JPY | K3 | T-28 | JPY 1.25M | 0.00635 (backed out) | 9.1 | 11.12 | 722 | 45 | 2,888 | 4,813 | 28,880 | 115,522 |
| MSF | Micro CHF | K3 | T-28 | CHF 12,500 | 1.216 | 7.0 | 11.77 | 1,064 | 67 | 4,258 | 7,096 | 42,578 | 170,314 |
| MCL | WTI crude (micro) | K4 | yes; program vehicle + T-28 | 100 bbl | 87.7 | 31.7 | 34.98 | 2,777 | 175 | 11,107 | 18,511 | 111,069 | 444,274 |
| NG | Henry Hub gas | K4 | yes; program vehicle | 10,000 MMBtu | 3.706 | 35.6 | 50.79 | 13,183 | 830 | 52,732 | 87,886 | 527,318 | 2,109,272 |
| MNG | Micro Henry Hub | K4 | T-28 | 1,000 MMBtu | 3.706 | 35.6 | 50.79 | 1,318 | 83 | 5,273 | 8,789 | 52,732 | 210,927 |
| MGC | Gold (micro) | K5 | yes; program vehicle + T-28 | 10 oz | 4175.2 | 22.2 | 15.65 | 9,254 | 583 | 37,016 | 61,693 | 370,158 | 1,480,632 |
| MHG | Copper (micro) | K5 | yes; program vehicle + T-28 | 2,500 lb | 6.568 | 23.1 | 26.8 | 3,785 | 238 | 15,140 | 25,234 | 151,402 | 605,608 |
| SIL | Silver (1,000 oz) | K5 | T-28 | 1,000 oz | 60.735 | 41.0 | 27.73 | 24,874 | 1,567 | 99,496 | 165,826 | 994,955 | 3,979,820 |
| ZC | Corn | K6 | yes; program vehicle | 5,000 bu | 516.25 | 14.8 | 26.65 | 3,817 | 240 | 15,268 | 25,447 | 152,683 | 610,732 |
| ZW | Wheat | K6 | yes; program vehicle | 5,000 bu | 683 | 25.7 | 26.68 | 8,789 | 554 | 35,158 | 58,596 | 351,576 | 1,406,305 |
| ZS | Soybeans | K6 | yes; program vehicle | 5,000 bu | 1252 | 12.6 | 23.17 | 7,914 | 499 | 31,655 | 52,759 | 316,552 | 1,266,208 |
| ZM | Soybean meal | K6 | yes; program vehicle | 100 short tons | 347.1 | 20.9 | 28.75 | 7,255 | 457 | 29,019 | 48,365 | 290,191 | 1,160,765 |
| ZL | Soybean oil | K6 | yes; program vehicle | 60,000 lb | 68.89 | 21.7 | 26.12 | 8,971 | 565 | 35,884 | 59,807 | 358,840 | 1,435,360 |
| HE | Lean hogs | K6 | yes; program vehicle + T-28 | 40,000 lb | 76.25 | 21.6 | 24.23 | 6,586 | 415 | 26,342 | 43,904 | 263,421 | 1,053,685 |
| LE | Live cattle | K6 | yes; program vehicle + T-28 | 40,000 lb | 223.2 | 16.4 | 13.56 | 14,666 | 924 | 58,663 | 97,772 | 586,630 | 2,346,518 |
| MZC | Micro corn | K6 | T-28 | 500 bu | 516.25 | 14.8 | 26.65 | 382 | 24 | 1,527 | 2,545 | 15,268 | 61,073 |
| MZW | Micro wheat | K6 | T-28 | 500 bu | 683 | 25.7 | 26.68 | 879 | 55 | 3,516 | 5,860 | 35,158 | 140,630 |
| MZS | Micro soybeans | K6 | T-28 | 500 bu | 1252 | 12.6 | 23.17 | 791 | 50 | 3,166 | 5,276 | 31,655 | 126,621 |
| MZM | Micro soybean meal | K6 | T-28 | 10 short tons | 347.1 | 20.9 | 28.75 | 725 | 46 | 2,902 | 4,837 | 29,019 | 116,077 |
| MZL | Micro soybean oil | K6 | T-28 | 6,000 lb | 68.89 | 21.7 | 26.12 | 897 | 57 | 3,588 | 5,981 | 35,884 | 143,536 |
| MBT | Bitcoin (micro) | K7 | yes; program vehicle + T-28 | 0.1 BTC | 84800 | 39.0 | - | 3,309 | 208 | 13,237 | 22,062 | 132,371 | 529,484 |
| 2YY | Micro 2 Treasury yield | K2 | T-28 | $10 DV01 | n/a | 74.5 bp/yr (T-30) | - | 745 | 47 | 2,980 | 4,967 | 29,800 | 119,200 |
| 5YY | Micro 5 Treasury yield | K2 | T-28 | $10 DV01 | n/a | 75.2 bp/yr (T-30) | - | 752 | 47 | 3,008 | 5,013 | 30,080 | 120,320 |
| 10YY | Micro 10 Treasury yield | K2 | T-28 | $10 DV01 | n/a | 67.0 bp/yr (T-30) | - | 670 | 42 | 2,680 | 4,467 | 26,800 | 107,200 |
| 30YY | Micro 30 Treasury yield | K2 | T-28 | $10 DV01 | n/a | 58.7 bp/yr (T-30) | - | 587 | 37 | 2,348 | 3,913 | 23,480 | 93,920 |

Reading the table:
- "Lone, 1 contract" is the capital at which one contract is exactly the vol target as the only holding.
- "In portfolio, 1 contract" uses Carver's reporting weights (w = 0.04, IDM = 2.5, so w x IDM = 0.10).
- The last column is Carver's own minimum (4 contracts). For example, MES needs $16.7K alone at 25%, $167K as one
  contract in a 25-instrument portfolio, and $668K by Carver's 4-contract rule.

### C3. What $10K, $25K, $50K and $100K can hold, and what they earn

Rule:
- Candidates are the smallest listed contract per exposure (30 instruments): 4 equity micros; 2YY/5YY/10YY/30YY;
  MTN; MWN; 6 FX micros plus full-size 6N; MCL; MNG; MGC; MHG; SIL; 5 micro grains plus full-size HE and LE; MBT.
- At capital K with N instruments held equally (w = 1/N), each instrument's target annual $ risk is
  K x tau x IDM(N) / N.
- IDM(N) = sqrt(N / (1 + (N-1) x 0.125)), capped at 2.5. The rho of 0.125 is the average correlation implied by
  Carver's IDM 2.5 at w = 0.04.
- An instrument is held if one contract's annual $ risk is at most 1.5x its target (the stated tolerance). The
  largest N for which the N lowest-risk instruments all pass is chosen.
- Position = max(1, round(target / $ risk)).

Return and drawdown assumptions:
- Index Sharpe range from Part A: low 0.15 (TSMOM 2020-2025 0.16; SG Trend 2010-2019 0.14), mid 0.30 (SG Trend
  2013-2025; TSMOM 2012-2025), high 0.50 (AQMIX 2020-2025 0.59; SG Trend 2020-2025 0.40).
- Carry adds nothing on the post-2012 evidence (A4), so no carry uplift is applied.
- Net S = index S x (1 - size penalty) - cost / portfolio sigma.
  - Size penalty: Carver's 20% if the maximum position is about 1 contract, 5% at 2, 0 at 3+, averaged over held
    instruments, with maximum = 2x the target position.
  - Cost: 10 round trips per contract per year (Carver's "6 trades per year" plus quarterly rolls, T-18), at the
    program's RT_X $ where the program has the vehicle (design doc lines 143-172).
  - For micros the program does not trade, $3.00 per round trip is assumed (UNSOURCED assumption, set near the
    program's MNQ/M2K/MYM RT_X of $2.71-$3.76).
- Using an index Sharpe that is net of CTA fees as the pre-cost Sharpe of a retail book is a stated approximation. Fee
  savings push one way; CTAs' cheaper execution and 100+ markets push the other.
- E[$/yr] = net S x portfolio sigma.
- E[MDD]: the expected maximum drawdown of Brownian motion with drift (Magdon-Ismail et al. 2004, T-31), computed by
  daily Monte Carlo (20,000 paths, emdd.py). At S = 0 it gives 2.74 sigma over 5 years, against the paper's
  continuous-time 2 x sqrt(pi/8) x sqrt(5) = 2.80.
- Index worst drawdowns scaled to the account's sigma: SG Trend -20.6% at 11.33% vol (1.82 sigma); TSMOM -27.9% at
  13.11% vol (2.13 sigma).
- The portfolio sigma uses rho = 0.125. The held sets are concentrated in rates and FX micros, whose true
  within-cluster correlation is much higher, so these sigmas and the diversification are optimistic.

#### Sizing table (base vols, T-22)


| Capital | tau | N held | Held (contracts) | IDM | Target $/instr/yr | Portfolio sigma $/yr (% of K) | Cost $/yr (10 RT/contract) | Size penalty | Case | Index S | Net S | E[$/yr] | E[$/month] | E[MDD] 5y | E[MDD] 10y | SG Trend worst DD scaled | TSMOM worst DD scaled |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| $10,000 | 25% | 11 | MCDx2 MZCx1 M6Bx1 M6Ax1 30YYx1 MTNx1 10YYx1 MJYx1 MZMx1 2YYx1 5YYx1 | 2.21 | 503 | 3,104 (31%) | 360 | 0.10 | low | 0.15 | 0.02 | 61 (0.6%) | 5 | 8,370 (84%) | 11,820 (118%) | 5,648 (56%) | 6,605 (66%) |
| $10,000 | 25% | 11 | (same) | 2.21 | 503 | 3,104 (31%) | 360 | 0.10 | mid | 0.30 | 0.16 | 482 (4.8%) | 40 | 7,529 (75%) | 10,303 (103%) | 5,648 (56%) | 6,605 (66%) |
| $10,000 | 25% | 11 | (same) | 2.21 | 503 | 3,104 (31%) | 360 | 0.10 | high | 0.50 | 0.34 | 1,044 (10.4%) | 87 | 6,653 (67%) | 8,696 (87%) | 5,648 (56%) | 6,605 (66%) |
| $25,000 | 25% | 17 | MCDx3 MZCx2 M6Bx2 M6Ax2 30YYx1 MTNx1 10YYx1 MJYx1 MZMx1 2YYx1 5YYx1 M6Ex1 MZSx1 MZWx1 MZLx1 MSFx1 MWNx1 | 2.38 | 875 | 5,923 (24%) | 660 | 0.03 | low | 0.15 | 0.03 | 202 (0.8%) | 17 | 15,807 (63%) | 22,237 (89%) | 10,780 (43%) | 12,605 (50%) |
| $25,000 | 25% | 17 | (same) | 2.38 | 875 | 5,923 (24%) | 660 | 0.03 | mid | 0.30 | 0.18 | 1,065 (4.3%) | 89 | 14,121 (56%) | 19,239 (77%) | 10,780 (43%) | 12,605 (50%) |
| $25,000 | 25% | 17 | (same) | 2.38 | 875 | 5,923 (24%) | 660 | 0.03 | high | 0.50 | 0.37 | 2,214 (8.9%) | 185 | 12,392 (50%) | 16,039 (64%) | 10,780 (43%) | 12,605 (50%) |
| $50,000 | 25% | 19 | MCDx5 MZCx4 M6Bx3 M6Ax3 30YYx3 MTNx2 10YYx2 MJYx2 MZMx2 2YYx2 5YYx2 M6Ex2 MZSx2 MZWx2 MZLx2 MSFx1 MWNx1 MNGx1 M2Kx1 | 2.42 | 1,591 | 11,824 (24%) | 1,262 | 0.01 | low | 0.15 | 0.04 | 503 (1.0%) | 42 | 31,362 (63%) | 44,021 (88%) | 21,520 (43%) | 25,164 (50%) |
| $50,000 | 25% | 19 | (same) | 2.42 | 1,591 | 11,824 (24%) | 1,262 | 0.01 | mid | 0.30 | 0.19 | 2,267 (4.5%) | 189 | 27,946 (56%) | 37,990 (76%) | 21,520 (43%) | 25,164 (50%) |
| $50,000 | 25% | 19 | (same) | 2.42 | 1,591 | 11,824 (24%) | 1,262 | 0.01 | high | 0.50 | 0.39 | 4,619 (9.2%) | 385 | 24,466 (49%) | 31,520 (63%) | 21,520 (43%) | 25,164 (50%) |
| $100,000 | 25% | 23 | MCDx9 MZCx7 M6Bx6 M6Ax5 30YYx5 MTNx4 10YYx4 MJYx4 MZMx4 2YYx4 5YYx4 M6Ex3 MZSx3 MZWx3 MZLx3 MSFx3 MWNx2 MNGx2 M2Kx1 MCLx1 MYMx1 MBTx1 MHGx1 | 2.48 | 2,692 | 25,778 (26%) | 2,480 | 0.02 | low | 0.15 | 0.05 | 1,328 (1.3%) | 111 | 67,918 (68%) | 95,101 (95%) | 46,915 (47%) | 54,860 (55%) |
| $100,000 | 25% | 23 | (same) | 2.48 | 2,692 | 25,778 (26%) | 2,480 | 0.02 | mid | 0.30 | 0.20 | 5,136 (5.1%) | 428 | 60,592 (61%) | 82,250 (82%) | 46,915 (47%) | 54,860 (55%) |
| $100,000 | 25% | 23 | (same) | 2.48 | 2,692 | 25,778 (26%) | 2,480 | 0.02 | high | 0.50 | 0.40 | 10,213 (10.2%) | 851 | 53,142 (53%) | 68,359 (68%) | 46,915 (47%) | 54,860 (55%) |
| $10,000 | 15% | 6 | MCDx2 MZCx1 M6Bx1 M6Ax1 30YYx1 MTNx1 | 1.92 | 480 | 1,678 (17%) | 210 | 0.06 | low | 0.15 | 0.02 | 27 (0.3%) | 2 | 4,538 (45%) | 6,414 (64%) | 3,054 (31%) | 3,572 (36%) |
| $10,000 | 15% | 6 | (same) | 1.92 | 480 | 1,678 (17%) | 210 | 0.06 | mid | 0.30 | 0.16 | 264 (2.6%) | 22 | 4,066 (41%) | 5,562 (56%) | 3,054 (31%) | 3,572 (36%) |
| $10,000 | 15% | 6 | (same) | 1.92 | 480 | 1,678 (17%) | 210 | 0.06 | high | 0.50 | 0.35 | 580 (5.8%) | 48 | 3,576 (36%) | 4,663 (47%) | 3,054 (31%) | 3,572 (36%) |
| $25,000 | 15% | 14 | MCDx2 MZCx2 M6Bx1 M6Ax1 30YYx1 MTNx1 10YYx1 MJYx1 MZMx1 2YYx1 5YYx1 M6Ex1 MZSx1 MZWx1 | 2.31 | 619 | 4,198 (17%) | 480 | 0.05 | low | 0.15 | 0.03 | 118 (0.5%) | 10 | 11,254 (45%) | 15,856 (63%) | 7,641 (31%) | 8,935 (36%) |
| $25,000 | 15% | 14 | (same) | 2.31 | 619 | 4,198 (17%) | 480 | 0.05 | mid | 0.30 | 0.17 | 717 (2.9%) | 60 | 10,075 (40%) | 13,749 (55%) | 7,641 (31%) | 8,935 (36%) |
| $25,000 | 15% | 14 | (same) | 2.31 | 619 | 4,198 (17%) | 480 | 0.05 | high | 0.50 | 0.36 | 1,514 (6.1%) | 126 | 8,860 (35%) | 11,507 (46%) | 7,641 (31%) | 8,935 (36%) |
| $50,000 | 15% | 18 | MCDx3 MZCx3 M6Bx2 M6Ax2 30YYx2 MTNx2 10YYx1 MJYx1 MZMx1 2YYx1 5YYx1 M6Ex1 MZSx1 MZWx1 MZLx1 MSFx1 MWNx1 MNGx1 | 2.40 | 1,000 | 7,114 (14%) | 780 | 0.01 | low | 0.15 | 0.04 | 272 (0.5%) | 23 | 18,927 (38%) | 26,597 (53%) | 12,946 (26%) | 15,139 (30%) |
| $50,000 | 15% | 18 | (same) | 2.40 | 1,000 | 7,114 (14%) | 780 | 0.01 | mid | 0.30 | 0.19 | 1,324 (2.6%) | 110 | 16,880 (34%) | 22,971 (46%) | 12,946 (26%) | 15,139 (30%) |
| $50,000 | 15% | 18 | (same) | 2.40 | 1,000 | 7,114 (14%) | 780 | 0.01 | high | 0.50 | 0.38 | 2,727 (5.5%) | 227 | 14,789 (30%) | 19,092 (38%) | 12,946 (26%) | 15,139 (30%) |
| $100,000 | 15% | 19 | MCDx6 MZCx5 M6Bx4 M6Ax4 30YYx3 MTNx3 10YYx3 MJYx3 MZMx3 2YYx3 5YYx3 M6Ex2 MZSx2 MZWx2 MZLx2 MSFx2 MWNx2 MNGx1 M2Kx1 | 2.42 | 1,909 | 15,185 (15%) | 1,622 | 0.00 | low | 0.15 | 0.04 | 650 (0.6%) | 54 | 40,266 (40%) | 56,515 (57%) | 27,635 (28%) | 32,315 (32%) |
| $100,000 | 15% | 19 | (same) | 2.42 | 1,909 | 15,185 (15%) | 1,622 | 0.00 | mid | 0.30 | 0.19 | 2,922 (2.9%) | 243 | 35,870 (36%) | 48,755 (49%) | 27,635 (28%) | 32,315 (32%) |
| $100,000 | 15% | 19 | (same) | 2.42 | 1,909 | 15,185 (15%) | 1,622 | 0.00 | high | 0.50 | 0.39 | 5,951 (6.0%) | 496 | 31,393 (31%) | 40,431 (40%) | 27,635 (28%) | 32,315 (32%) |


Reading the base table:
- At 25%, the mid case earns about $40 a month at $10K, $89 at $25K, $189 at $50K and $428 at $100K. The high case
  roughly doubles that; the low case is near zero after costs.
- The held sets have no equity index until $50K (M2K) and no gold or MES even at $100K. At $10K and $25K they are 3
  clusters (rates, FX, grains).
- At 25% the expected 10-year maximum drawdown is 76-103% of capital. At 15% it is 46-56%, with about 55-60% of the
  income ($22, $60, $110 and $243 a month).
- At $10K the 25% book runs 31% realized vol because of the 1-contract floor.

#### Long-run vol sensitivity (vols replaced by the 1985-2015 figures in T-12 where available; mid case only)

| Capital | tau | N held | Held (contracts) | Portfolio sigma $/yr | Cost $/yr | Net S (mid case, index S 0.30) | E[$/month] mid | E[MDD] 10y mid |
|---|---|---|---|---|---|---|---|---|
| $10,000 | 25% | 9 | MCDx1 30YYx1 10YYx1 MZCx1 2YYx1 5YYx1 MTNx1 M6Ax1 M6Bx1 | 3,052 | 270 | 0.18 | 46 | 9,897 (99%) |
| $25,000 | 25% | 14 | MCDx2 30YYx2 10YYx2 MZCx1 2YYx1 5YYx1 MTNx1 M6Ax1 M6Bx1 MJYx1 MZWx1 MZMx1 MZLx1 MZSx1 | 5,921 | 510 | 0.20 | 100 | 18,824 (75%) |
| $50,000 | 25% | 19 | MCDx3 30YYx3 10YYx2 MZCx2 2YYx2 5YYx2 MTNx2 M6Ax2 M6Bx2 MJYx2 MZWx2 MZMx2 MZLx1 MZSx1 M6Ex1 MWNx1 MSFx1 MNGx1 M2Kx1 | 12,878 | 992 | 0.22 | 234 | 40,367 (81%) |
| $100,000 | 25% | 22 | MCDx5 30YYx5 10YYx4 MZCx4 2YYx4 5YYx4 MTNx3 M6Ax3 M6Bx3 MJYx3 MZWx3 MZMx3 MZLx3 MZSx2 M6Ex2 MWNx2 MSFx2 MNGx1 M2Kx1 MYMx1 MCLx1 MBTx1 | 25,312 | 1,847 | 0.22 | 475 | 78,839 (79%) |
| $10,000 | 15% | 5 | MCDx1 30YYx1 10YYx1 MZCx1 2YYx1 | 1,769 | 150 | 0.19 | 28 | 5,686 (57%) |
| $25,000 | 15% | 12 | MCDx1 30YYx1 10YYx1 MZCx1 2YYx1 5YYx1 MTNx1 M6Ax1 M6Bx1 MJYx1 MZWx1 MZMx1 | 4,132 | 360 | 0.20 | 67 | 13,230 (53%) |
| $50,000 | 15% | 15 | MCDx2 30YYx2 10YYx2 MZCx2 2YYx2 5YYx2 MTNx1 M6Ax1 M6Bx1 MJYx1 MZWx1 MZMx1 MZLx1 MZSx1 M6Ex1 | 7,466 | 630 | 0.21 | 132 | 23,548 (47%) |
| $100,000 | 15% | 19 | MCDx4 30YYx3 10YYx3 MZCx3 2YYx3 5YYx3 MTNx2 M6Ax2 M6Bx2 MJYx2 MZWx2 MZMx2 MZLx2 MZSx1 M6Ex1 MWNx1 MSFx1 MNGx1 M2Kx1 | 14,720 | 1,172 | 0.22 | 266 | 46,217 (46%) |

Long-run vols raise the FX and grain micros' risk. The selections shrink slightly (9 instead of 11 at $10K/25%) and the
income changes little, because the vol target rescales positions. A drawdown above 100% of capital in the tables means
the arithmetic Brownian model would have wiped the account inside the horizon.

### C4. Statistical power for the user's own test (t ~ S x sqrt(years))

| Sharpe S | Years to t = 2 | Years to t = 3 |
|---|---|---|
| 0.15 (low; TSMOM 2020-2025) | 178 | 400 |
| 0.18 (net, $25K mid case after costs) | 123 | 278 |
| 0.24 (SG Trend 2010-2025, net of fees) | 69 | 156 |
| 0.30 (mid) | 44 | 100 |
| 0.40 | 25 | 56 |
| 0.50 (high) | 16 | 36 |

A personal trend/carry account cannot confirm its own edge in any useful time. Its case rests on the published record
in Part A.

## Part D: prop-firm fit (drawdown grid, no firm names)

Model and assumptions:
- Daily P&L is Gaussian with daily sigma s and drift mu = S x s / sqrt(252) at fixed size (no D-proportional sizing).
  S is the index Sharpe: 0.15, 0.30, 0.50; costs would lower it further.
- Infinite-horizon fixed floor: P = exp(-2 mu D / s^2) (the V2.0 formula).
- One-year fixed floor: the closed-form first-passage probability. A Monte Carlo check matches it: 0.428 vs 0.430 at
  S = 0.3, D = 10s; and 0.224 vs 0.234 at S = 1.0, D = 10s, the design doc's 0.235.
- Trailing floors by Monte Carlo (20,000 paths, 252 days, 16 intraday steps a day; ruin.py):
  - Floor = high-water balance - D, and it locks at the starting balance once the high reaches start + D (assumed lock
    rule).
  - End-of-day (EOD) trailing raises the high only on daily closes but checks the breach intraday.
  - Intraday trailing raises the high continuously.
  - Horizon 1 year, reported as total ruin and, in parentheses, ruin before the lock.
- Ruin depends only on D / s and S, so the 10%-ruin bound is a ratio:
  - infinite fixed: s_max = D / 121.8 (S 0.15), D / 60.9 (S 0.30), D / 36.6 (S 0.50);
  - 1-year EOD trailing: D / 29.0, D / 27.2, D / 25.5;
  - intraday: D / 29.2, D / 27.6, D / 25.8.
- Trailing makes ruin likelier than a fixed floor. For the 10-micro set at D = $2,000 and S = 0.3, the 1-year ruin is
  0.36 with a fixed floor and 0.63 trailing EOD. EOD trailing is slightly less likely to breach than intraday (0.63 vs
  0.64 here, up to 0.03 apart in the grid).
- Gap risk: weekend and overnight gaps are inside the daily Gaussian step. Fat tails and limit moves are not modelled,
  so real ruin is higher.
- Crisis correlation (rho 0.30 instead of 0.125) raises each set's sigma by 26-38% (shown below).
- Instrument sets hold one micro each, sigmas from C2:


- A: all 30 smallest contracts (incl. full-size 6N, HE, LE): daily sigma $3,024 (rho 0.125), $3,944 (rho 0.30). Members: MCD MZC M6B M6A 30YY MTN 10YY MJY MZM 2YY 5YY M6E MZS MZW MZL MSF MWN MNG M2K MCL MYM MBT MHG MES 6N HE MGC MNQ LE SIL
- B: 27 micros (all micro-listed exposures): daily sigma $2,432 (rho 0.125), $3,057 (rho 0.30). Members: MCD MZC M6B M6A 30YY MTN 10YY MJY MZM 2YY 5YY M6E MZS MZW MZL MSF MWN MNG M2K MCL MYM MBT MHG MES MGC MNQ SIL
- C: 17 lowest-risk micros (the $25K/25% held set): daily sigma $324 (rho 0.125), $446 (rho 0.30). Members: MCD MZC M6B M6A 30YY MTN 10YY MJY MZM 2YY 5YY M6E MZS MZW MZL MSF MWN
- D: 10 lowest-risk micros: daily sigma $169 (rho 0.125), $222 (rho 0.30). Members: MCD MZC M6B M6A 30YY MTN 10YY MJY MZM 2YY
- E: MES alone: daily sigma $263 (rho 0.125), $263 (rho 0.30). Members: MES


#### Ruin grid (S = index Sharpe; sigma values per day; 'EXCEEDS' means set D's sigma is above the 1-year EOD 10%-ruin bound)


| S | D | Max daily sigma for ruin < 10%: infinite horizon, fixed floor | 1 year, EOD trailing | 1 year, intraday trailing | Set D (10 micros) sigma/day | Set D: P ruin infinite fixed | Set D: P 1y fixed | Set D: P 1y EOD trailing (before lock) | Set D: P 1y intraday trailing (before lock) | Set C (17 micros) sigma/day: P 1y EOD / intraday | Set B (27 micros) sigma/day: P 1y EOD / intraday |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.15 | $2,000 | $16 | $69 | $68 | $169 EXCEEDS | 0.80 | 0.41 | 0.68 (0.57) | 0.69 (0.57) | $324: 0.84 / 0.85 | $2,432: 0.95 / 0.96 |
| 0.15 | $2,500 | $21 | $86 | $86 | $169 EXCEEDS | 0.76 | 0.30 | 0.56 (0.51) | 0.56 (0.50) | $324: 0.80 / 0.81 | $2,432: 0.95 / 0.96 |
| 0.15 | $3,000 | $25 | $104 | $103 | $169 EXCEEDS | 0.72 | 0.22 | 0.43 (0.41) | 0.43 (0.41) | $324: 0.76 / 0.77 | $2,432: 0.95 / 0.96 |
| 0.15 | $4,000 | $33 | $138 | $137 | $169 EXCEEDS | 0.64 | 0.11 | 0.22 (0.21) | 0.22 (0.22) | $324: 0.66 / 0.66 | $2,432: 0.94 / 0.95 |
| 0.15 | $4,500 | $37 | $155 | $154 | $169 EXCEEDS | 0.61 | 0.07 | 0.14 (0.14) | 0.15 (0.15) | $324: 0.59 / 0.60 | $2,432: 0.94 / 0.95 |
| 0.15 | $5,000 | $41 | $173 | $171 | $169 ok | 0.57 | 0.05 | 0.09 (0.09) | 0.10 (0.10) | $324: 0.53 / 0.53 | $2,432: 0.94 / 0.94 |
| 0.15 | $6,000 | $49 | $207 | $205 | $169 ok | 0.51 | 0.02 | 0.03 (0.03) | 0.04 (0.04) | $324: 0.39 / 0.40 | $2,432: 0.93 / 0.93 |
| 0.15 | $7,500 | $62 | $259 | $257 | $169 ok | 0.43 | 0.00 | 0.01 (0.01) | 0.01 (0.01) | $324: 0.23 / 0.23 | $2,432: 0.91 / 0.92 |
| 0.30 | $2,000 | $33 | $73 | $72 | $169 EXCEEDS | 0.64 | 0.36 | 0.63 (0.52) | 0.64 (0.53) | $324: 0.82 / 0.82 | $2,432: 0.94 / 0.94 |
| 0.30 | $2,500 | $41 | $92 | $90 | $169 EXCEEDS | 0.57 | 0.26 | 0.50 (0.45) | 0.52 (0.46) | $324: 0.77 / 0.78 | $2,432: 0.94 / 0.94 |
| 0.30 | $3,000 | $49 | $110 | $109 | $169 EXCEEDS | 0.51 | 0.18 | 0.37 (0.35) | 0.39 (0.36) | $324: 0.72 / 0.73 | $2,432: 0.94 / 0.94 |
| 0.30 | $4,000 | $66 | $147 | $145 | $169 EXCEEDS | 0.41 | 0.09 | 0.17 (0.17) | 0.19 (0.18) | $324: 0.60 / 0.62 | $2,432: 0.94 / 0.94 |
| 0.30 | $4,500 | $74 | $165 | $163 | $169 EXCEEDS | 0.37 | 0.06 | 0.11 (0.11) | 0.12 (0.12) | $324: 0.54 / 0.56 | $2,432: 0.93 / 0.94 |
| 0.30 | $5,000 | $82 | $184 | $181 | $169 ok | 0.33 | 0.03 | 0.07 (0.07) | 0.08 (0.08) | $324: 0.47 / 0.49 | $2,432: 0.93 / 0.93 |
| 0.30 | $6,000 | $98 | $220 | $217 | $169 ok | 0.26 | 0.01 | 0.02 (0.02) | 0.03 (0.03) | $324: 0.33 / 0.35 | $2,432: 0.92 / 0.92 |
| 0.30 | $7,500 | $123 | $276 | $271 | $169 ok | 0.19 | 0.00 | 0.00 (0.00) | 0.01 (0.01) | $324: 0.19 / 0.20 | $2,432: 0.90 / 0.90 |
| 0.50 | $2,000 | $55 | $79 | $77 | $169 EXCEEDS | 0.48 | 0.30 | 0.57 (0.47) | 0.59 (0.48) | $324: 0.77 / 0.79 | $2,432: 0.93 / 0.94 |
| 0.50 | $2,500 | $68 | $98 | $97 | $169 EXCEEDS | 0.39 | 0.21 | 0.43 (0.39) | 0.46 (0.41) | $324: 0.72 / 0.74 | $2,432: 0.93 / 0.94 |
| 0.50 | $3,000 | $82 | $118 | $116 | $169 EXCEEDS | 0.33 | 0.14 | 0.31 (0.29) | 0.33 (0.31) | $324: 0.67 / 0.69 | $2,432: 0.93 / 0.94 |
| 0.50 | $4,000 | $109 | $157 | $155 | $169 EXCEEDS | 0.23 | 0.06 | 0.14 (0.13) | 0.15 (0.14) | $324: 0.54 / 0.57 | $2,432: 0.92 / 0.93 |
| 0.50 | $4,500 | $123 | $177 | $174 | $169 ok | 0.19 | 0.04 | 0.08 (0.08) | 0.09 (0.09) | $324: 0.47 / 0.50 | $2,432: 0.91 / 0.93 |
| 0.50 | $5,000 | $137 | $196 | $193 | $169 ok | 0.16 | 0.02 | 0.05 (0.05) | 0.05 (0.05) | $324: 0.40 / 0.43 | $2,432: 0.91 / 0.92 |
| 0.50 | $6,000 | $164 | $236 | $232 | $169 ok | 0.11 | 0.01 | 0.02 (0.02) | 0.02 (0.02) | $324: 0.28 / 0.30 | $2,432: 0.89 / 0.91 |
| 0.50 | $7,500 | $205 | $295 | $290 | $169 ok | 0.06 | 0.00 | 0.00 (0.00) | 0.00 (0.00) | $324: 0.15 / 0.16 | $2,432: 0.87 / 0.89 |

The granularity problem:
- The 10%-ruin bounds allow a daily sigma of only about $69-$295 over the D grid (one year, trailing). The bounds are
  $16-$205 for an infinite horizon.
- One micro in every exposure (set B) runs about $2,400 a day, 8 to 35 times the bound. Even the 17 lowest-risk micros
  run $324 a day, above every bound in the grid.
- Only the 10 lowest-risk micros ($169 a day: CAD, GBP, AUD, JPY FX micros; 2Y, 10Y and 30Y yield micros; MTN; micro
  corn and micro meal) fit, and only at D >= $5,000 (S 0.15-0.30) or D >= $4,500 (S 0.50). That set has three
  clusters and no equity, energy or metal exposure.
- MES alone ($263 a day) exceeds the 1-year bound for every D up to $7,500 at S 0.15, and fits only at about
  D >= $7,200 at S 0.30.
- A swing trend/carry book at minimum micro size is therefore too large for trailing drawdowns of $2,000-$4,500 unless
  it trades a handful of low-vol micros.
- At the evidence-based Sharpe, the infinite-horizon fixed-floor ruin of even that handful is 0.06-0.80 across the
  grid (0.19-0.64 at S 0.30).

## Source list

Fetch times are UTC from fetch_log.md; page dates are as shown on the page.

| Key | URL | Fetched (UTC) | Page date | Verbatim quote |
|---|---|---|---|---|
| T-01 | https://pages.stern.nyu.edu/~lpederse/papers/TimeSeriesMomentum.pdf | 2026-10-03 (F01) | JFE 104 (2012) | "a Sharpe ratio greater than one on an annual basis, or"; "contract as described above. The choice of 40% is incon-"; "period 1985–2009, which is roughly the level of volatility" |
| T-02 | https://www.TrendFollowing.com/whitepaper/Century_Evidence_Trend_Following.pdf | 2026-10-03 (F05) | Fall 2014 | "To simulate fees, we apply a 2% management fee"; "Jan 2000-Dec 2013 11.3% 7.9% 9.6% 0.62" (table row, spacing compressed); "only realizes a Sharpe ratio of 0.4 net of fees and" |
| T-03 | https://fairmodel.econ.yale.edu/ec439/hurst.pdf | 2026-10-03 (F06) | JPM Fall 2017 | "1880 to the end of 2016. We do not have data on each of" |
| T-04 | https://www.aqr.com/-/media/AQR/Documents/Journal-Articles/JPM-You-Cant-Always-Trend-When-You-Want.pdf | 2026-10-03 (F22) | 2020 | "December 31, 2018, the SG Trend Index realized an annualized" / "Sharpe ratio of 0.05, versus a Sharpe ratio of 0.28 from the incep-" |
| T-05 | https://funds.aqr.com/-/media/Files/Fund-Documents/TrackRecords/MFMF.xls | 2026-10-03 (F14) | data to 2026-09-30 | header cells: "Class N", "Class I", "Class R6", "ICE BofA US 3M T-Bill Index", "SG Trend Index" |
| T-06 | https://funds.aqr.com/-/media/Files/Fund-Documents/Fact-Sheet/MFMF.pdf | 2026-10-03 (F15) | as of 06/30/2026 | "Realized Since Inception Sharpe Ratio" (0.26); "AQMIX -0.97 -8.88 1.93 -0.41 -1.06 35.38 1.80 8.41 14.63" (spacing compressed) |
| T-07 | https://wholesale.banking.societegenerale.com/en/prime-services-indices/ | 2026-10-03 (F08) | no date shown | "Trend Index is equal-weighted and reconstituted annually. The index calculates the net daily rate of return for a pool of trend following based hedge fund managers." |
| T-08 | https://wholesale.banking.societegenerale.com/uploads/tx_bisgnews/CTA_Indices_February_2015_05.pdf | 2026-10-03 (F11) | February 2015 | "Newedge Trend Index -0.14% +4.94%" (spacing compressed) |
| T-09 | https://www.aqr.com/-/media/AQR/Documents/Insights/Data-Sets/Time-Series-Momentum-Factors-Monthly.xlsx (page: https://www.aqr.com/Insights/Datasets/Time-Series-Momentum-Factors-Monthly) | 2026-10-03 (F39, F38) | data 1985-01..2026-05 | "The TSMOM factor here is a 12-month time series momentum strategy with a 1-month holding period." |
| T-10 | https://www.nber.org/system/files/working_papers/w19325/w19325.pdf | 2026-10-03 (F03) | August 2013 | "remarkable Sharpe ratio of 1.10 per annum. A diversified passive long position in all"; "other hand, the carry strategy faces larger transaction costs, greater funding issues, and" |
| T-11 | https://www.aqr.com/-/media/AQR/Documents/Insights/Data-Sets/Century-of-Factor-Premia-Monthly.xlsx (page: https://www.aqr.com/Insights/Datasets/Century-of-Factor-Premia-Monthly) | 2026-10-03 (F44, F43) | data 1926-07..2026-02 | "As in most academic studies, returns are presented gross of trading costs and fees." |
| T-12 | https://down.aefweb.net/WorkingPapers/w717.pdf (via https://econpapers.repec.org/RePEc:cuf:wpaper:717) | 2026-10-03 (F19) | JFE 135 (2020) | "level, 47 of the 55 assets have a t-statistic of less than 1.65,"; "refers to the average value within asset class. The sample period is 1985:01–2015:12." |
| T-13 | https://www.institutional-investment.de/uploads/media/Robeco_Study_Global-Factor-Premiums.pdf | 2026-10-03 (F42) | January 2019 version | "from 2012-2016, such that we have an extensive new sample to conduct further analyses." |
| T-14 | https://arxiv.org/pdf/2105.01380 | 2026-10-03 (F40) | May 5, 2021 | "the Sharpe ratio drops by 43%. This drop is slightly smaller than McLean and Pontiff (2016), who" |
| T-15 | https://qoppac.blogspot.com/2016/03/diversification-and-small-account-size.html | 2026-10-03 (F24) | 9 March 2016 | "In fact I recommend that you are holding at least 4 contracts at the maximum forecast."; "you're probably better off using a binary or thresholded forecast filter with as wide a range of instruments as you can manage, at least until you have $100K or so." |
| T-16 | https://qoppac.blogspot.com/2019/10/new-book-leveraged-trading.html | 2026-10-03 (F29) | 2 October 2019 | "The trading systems in ST require large amounts of money (at least £100,000; around $130,000). The Starter System in LT needs just £1,100 or $1,500." |
| T-17 | https://qoppac.blogspot.com/2020/03/how-much-risk-should-we-take.html | 2026-10-03 (F28) | 5 March 2020 | "If for example your Sharpe Ratio was 0.5, then your optimal risk target would be 50%. Most people think the Kelly formula is too aggressive. A better rule of thumb is to use half the optimal risk target. In this case we'd use a risk target of 25%." |
| T-18 | https://qoppac.blogspot.com/2021/05/adding-new-instruments-or-how-i-learned.html | 2026-10-03 (F30) | 7 May 2021 | "As a rule of thumb anything with a cost above 0.01SR is going to be too expensive"; "Add later: Markets which fail eithier the maximum cost test (0.01SR), maximum risk per contract ($125,000) or minimum volume ($1.25 million per day in risk units, and 100 contracts per day)" |
| T-19 | https://qoppac.blogspot.com/2021/06/static-optimisation-of-best-set-of.html | 2026-10-03 (F32) | 29 June 2021 | "Instruments should be not too large. In particular (as discussed here ) if we can't hold at least three contracts with a maximum forecast of 20 (twice the average forecast)" |
| T-20 | https://qoppac.blogspot.com/2021/10/mr-greedy-and-tale-of-minimum-tracking.html | 2026-10-03 (F25) | 1 October 2021 | "So the optimised version is still better than the rounded (SR improvement around 0.1), but nowhere near as good as the unrounded (SR penalty around 0.2)." |
| T-21 | https://qoppac.blogspot.com/2021/12/my-trading-system.html | 2026-10-03 (F27) | 2 December 2021 | "this is done using buffering to reduce trading costs." |
| T-22 | https://github.com/robcarver17/reports/blob/c955c34ecbc5001ac81be86ead28ac65b3a4e56e/Minimum_capital_report | 2026-10-03 (F33) | report produced 02/10/2026 | "Minimum capital report produced on 02/10/2026 23:00"; "I- minimum_capital: Minimum capital within a portfolio, allowing for minimum position = E * F / ( G * H)" |
| T-23 | https://github.com/robcarver17/reports/blob/c955c34ecbc5001ac81be86ead28ac65b3a4e56e/Static_selection_of_instruments | 2026-10-03 (F34) | commit 2026-10-02 | "For capital of 10000, 8 instruments" |
| T-24 | https://github.com/robcarver17/pysystemtrade/blob/326b5d402c2825cc8561cabb899d1454e593bda9/sysproduction/reporting/data/constants.py | 2026-10-03 (F35) | commit 2026-09-30 | "RISK_TARGET_ASSUMED = 25  ## 20 = 20%"; "MAX_SR_COST = 0.01" |
| T-25 | https://github.com/robcarver17/pysystemtrade/blob/326b5d402c2825cc8561cabb899d1454e593bda9/sysproduction/reporting/data/risk.py | 2026-10-03 (F36) | commit 2026-09-30 | "min_contracts_held * single_contract_min_capital / (idm * instrument_weight)" |
| T-26 | https://github.com/robcarver17/pysystemtrade/blob/326b5d402c2825cc8561cabb899d1454e593bda9/sysdata/config/defaults.yaml | 2026-10-03 (F37) | commit 2026-09-30 | "percentage_vol_target: 16.0"; "buffer_size: 0.10"; "proportion_of_slow_vol: 0.3" |
| T-27 | https://github.com/robcarver17/pysystemtrade/blob/326b5d402c2825cc8561cabb899d1454e593bda9/sysquant/estimators/diversification_multipliers.py | 2026-10-03 (F72) | commit 2026-09-30 | "the diversification multiplier will be 1 / [ ( W x H x WT ) 1/2 ]" |
| T-28 | https://www.ampfutures.com/trading-info/contract-specifications | 2026-10-03 (F46) | no date shown | adjacent cells of one row: "Micro 10-Year Yield" / "10YY" / "CBOT/CME" / "$10.00 DV01" / "1/10 of 1bp / $1.00"; and "Micro Corn" / "MZC" / "CBOT/CME" / "500 bushels" |
| T-29 | https://www.ironbeam.com/knowledge-base/micro-bitcoin-futures-mbt-contract-specifications/ | 2026-10-03 (F47) | datePublished 2024-12-04 | "0.1 Bitcoin (1/10th of a Bitcoin)" |
| T-30 | https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_yield_curve&field_tdr_date_value=2026&page&_format=csv (and the 2025 file) | 2026-10-03 (F71, F70) | data to 2026-10-02 | "10/02/2026,4.04,4.09,4.11,4.19,4.26,4.27,4.46,4.83,4.96,5.06,5.17,5.28,5.67,5.63" |
| T-31 | https://www.cs.rpi.edu/~magdon/ps/journal/drawdown_journal.pdf | 2026-10-03 (F73) | September 1, 2003 preprint | "logarithmic (µ > 0), square root (µ = 0), or linear (µ < 0)." |

Internal inputs (not web): docs/STAGE_E_ML_V2_DESIGN.md lines 47-131 (V2.0 ruin arithmetic, t ~ S x sqrt(years)) and
lines 143-172 (vehicle list, tick values, RT_X $). docs/DECISIONS.md lines 386-408 (V22).

Failures and non-survivors:
- AQR's original century-paper URL returned 404 (F02).
- The SMU repository is behind an Incapsula wall, for both curl and scrapling fetch (F07, F17).
- BarclayHedge BTOP50 now redirects to ION Analytics with no index data (F09). Wayback has no post-2014 capture.
- CEPR's "Out-of-Sample Performance of Carry Trades" returned 403 (F20); it is FX-only and was not used.
- FRED CSV downloads failed with HTTP/2 stream errors and then hung (F48-F59); Treasury.gov was used instead.
- The CME micro-yield page via Wayback holds no spec values (JS page; F45; listed in DO_NOT_COMMIT.txt).
- SG's own index history is sold through LSEG (not fetched).

## What this means for the program

The published record after 2010 puts diversified trend at a Sharpe of about 0.25-0.35 (net of CTA fees, or gross for
AQR's factor). Cross-sectional carry is about zero since 2013. At those Sharpes:
- a $10K-$100K micro portfolio at a 25% target earns about $40-$430 a month in the mid case, after costs;
- its expected 10-year drawdown is 76-103% of capital (46-56% at 15%);
- confirming the edge from its own record takes 44-100+ years.

A trailing drawdown of $2,000-$7,500 allows a daily sigma of only about D/27. One micro in each diversifying market
runs 8 to 35 times that. Only about ten low-vol FX, yield and grain micros fit, and only at D >= $5,000.
Trend/carry at minimum micro size does not fit the prop-firm drawdown grid. As a personal-account income path at these
capital levels, it yields hundreds of dollars a month at best, with deep drawdowns.
