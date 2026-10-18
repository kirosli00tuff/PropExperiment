# R4: volume and trade-side features (Stage E.25, research only)

Reader: R4-VolumeTradeSide-OpusHigh. Started 2026-10-18 01:38 PDT; this version written 02:05 PDT.
Sources already on disk that were re-used, not refetched: Gao, Han, Li, Zhou WP 2015
(reports/stage_e20_briefs/shared/gao_han_li_zhou_wp2015_mql5.pdf.txt, E.20 copy); Zarattini and Aziz 2023
VWAP paper (ZA23; R10 owns it; E.23 copy reports/stage_e23_briefs/mech_pages/M5_BREAKOUT_LOCATION/zarattini_aziz_2023_vwap.txt,
same PDF sha256 47137abd... as R10's pages/R10/concretum_Volume-Weighted-Average-Price.pdf); E.7 result
table (reports/E.7_RETURN.md); E.0 Databento quote log (reports/stage_e0_quotes.md); R3's Databento pricing
excerpt (pages/R3/databento_pricing_excerpt.md).

## 1. Answer (at most 250 words)

Peer-reviewed evidence that volume or trade-side features give a directional intraday edge on futures above
retail costs is thin. Trade-sign and order-flow work shows impact is real but transient: price impact of
imbalance is absorbed in about one second in the E-mini (Takahashi 2025), liquidity co-moves with signed flow
and cancels its predictability (Farmer, Gerig, Lillo, Mike 2006), and extreme imbalance coincides with pinned,
not moving, prices (Patzelt and Bouchaud 2018). No peer-reviewed test of volume profile, point of control,
value area, anchored VWAP or cumulative-delta divergence was found; two 2026 SSRN value-area papers on NQ/ES
exist but could not be read (SSRN blocks automation; OpenAlex has no abstract) [unverified].
The usable positives are conditional: (a) Gao et al. (JFE 2018): first-half-hour momentum on SPY is strongest on
high first-half-hour-volume days, 11.87% a year from one last-half-hour trade a day (about 4.7 bp a trade, gross,
1993-2013), but the program's own Baltussen-style test (E20H6-T1) found 1.25 ticks gross on NQ, so the
unconditional effect has decayed; (b) one independent author's MNQ walk-forward studies (arXiv 2026, not
peer-reviewed) where a 50-bar volume z-score gate is part of a regime signal: about 55 MNQ ticks gross a trade
OOS (N 196), after a 53+ combination search. The VWAP stop-and-reverse rule (ZA23) is already K1-vwap-01 and
failed in E.7. Volume spikes and dry-ups alone fail even before costs on MNQ (Mesfin 2026, gross about 0 pts).
Trades with aggressor side are cheap at Databento (TBBO 5 days: NQ $3.58, MNQ $8.62 in the E.0 log).

## 2. Candidate hypotheses

Gross per trade in MNQ ticks uses NQ at 21,000 (low end of the brief's range) and MES ticks use ES at 6,000;
conversions in section 3. The lead ranks; I give inputs.

| id | hypothesis | instruments | entry window CT | hold | trades/yr | best source (grade) | published effect | gross/trade (points; micro ticks) | dispersion | owned | testable on research window | overlap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R4-C1 | Volume-conditioned intraday momentum: trade the sign of the first 30-min return into the last 30 min only on days whose first-30-min volume is in the top within-year tercile | MNQ (also MES) | decision 09:00 (after 08:30-09:00), entry 14:30 | 30 min (to 15:00) | about 84 (one tercile of about 252 days) | Gao, Han, Li, Zhou, JFE 2018 (peer-reviewed; read as 2015 WP) | high-volume tercile: 11.87% a year, t 3.23, Sharpe 1.38; medium 6.46% (t 3.03); low 1.67% (t 0.98); annualised x 252, one trade a day; SPY 1993-2013 | 4.71 bp; NQ 9.89 pts = 39.6 MNQ ticks; ES 2.83 pts = 11.3 MES ticks (gross, no costs) | t 3.23; sd 8.60% a year | yes (1-min volume) | yes | K1-cp1-01; E20H6-T1/T2; Gate 0 g10 logvol30 and cp1_ret; E.20 ML (volume feature) |
| R4-C2 | Volume-gated regime pullback (RTH Confluence): long when a 3-state GMM labels the 5-min bar "Active Flow", the 200-bar Markov P(1->2) > 0.15 and the 50-bar volume z-score > 0.5; enter on a 25 x ATR-ratio pullback; exit at bar 13 | MNQ | 08:30-15:00 (RTH) | 65 min (13 x 5-min bars) or RTH end | about 65 OOS (196 over about 3 years), about 180 in sample | Mesfin 2026, arXiv 2605.04004 (working-paper; single independent author) | walk-forward OOS mean net +11.82 pts after 2.0 pts friction, sd 53.8, N 196, T 3.11; in sample +15.77 pts, T 5.83, N 538 | net + friction = 13.82 pts = 55.3 MNQ ticks gross | sd 53.8 pts; T 3.11 | yes (1-min OHLCV) | yes | none found for the regime gate; volume-spike family (C-H2) differs |
| R4-C3 | London-session regime transition long (Signal B): 15-min bars, long after a clean GMM transition R0 -> R2 (volume z-score is one of five features), exit 60 min or 07:30 CT | MNQ | 02:00-07:30 | 60 min | about 80 OOS (247 over about 3 years) | Mesfin 2026, arXiv 2605.04004 (working-paper) | walk-forward OOS net +4.09 pts, N 247, T 4.30, p 0.000025 (2.0 pts friction) | 6.09 pts = 24.4 MNQ ticks gross | T 4.30 | yes (1-min OHLCV; overnight bars) | yes | K-series overnight members (K1-cp2 opening range not overnight); volume is a minor feature here |
| R4-C4 | Volatility-Volume-Gap day classifier (first-bar volume z vs 20-day baseline, overnight gap, first-30-min move all in expanding top tercile), reversal entry with OLS filter | MNQ | after 09:00 | to close (15:00) | about 10 classifier days a year (127 OOS trades) | Mesfin 2026, arXiv 2605.11423 (working-paper) | best of 8 configurations: mean net +7.80 pts, T 1.46, N 127; author verdict FAIL (2024 year failure) | 9.80 pts = 39.2 MNQ ticks gross | T 1.46; win 52.0% | yes | yes | K1-cp2-01 (opening range), gap D-H4, C-H2 |

Not proposed (already tested or no sized evidence): price vs session VWAP stop-and-reverse (ZA23 = K1-vwap-01,
FAIL); volume profile / POC / value area, anchored VWAP, cumulative-delta divergence (no sized evidence found);
volume spike or dry-up alone (fails before costs, section 4); VPIN (volatility, not direction).

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| Intraday momentum stronger on high first-half-hour volume days | 1.67% (t 0.98) / 6.46% (t 3.03) / 11.87% (t 3.23) a year by volume tercile | "The average return per annum (and its t-statistic) of the η(r1 ) strategy increases from 1.67% (0.98) on low volume days to 6.46% (3.03) on medium volume days, and then further to a much higher level of 11.87% (3.23) on high volume days." | WP txt L536-538 (Sec 3.1.2; Table 5 Panel B) | Gao, Han, Li, Zhou, "Market intraday momentum", JFE 129 (2018) 394-414; WP Dec 2015 copy https://c.mql5.com/forextsd/forum/173/intraday_momentum_-_the_first_half-hour_return_predicts_the_last_half-hour_return.pdf | peer-reviewed (read as WP) | reports/stage_e20_briefs/shared/gao_han_li_zhou_wp2015_mql5.pdf.txt (sha256 3e2926...e067, txt) |
| Annualisation convention (needed for per-trade conversion) | x 252, one trade a day | "Even though we are only in the market for the last half-hour, we still annualize the returns multiplying by a factor of 252 because we only trade once per day." | WP txt L458-459 (footnote 7) | same | peer-reviewed | same |
| Volume terciles are formed within year | - | "we first sort all trading days within each year into terciles based on the first half-hour trading volume, and then combine each volume tercile across all years" | WP txt L362-364 | same | peer-reviewed | same |
| Sample | 1993-2013 SPY | "The sample period is from February 1, 1993, through December 31, 2013, excluding days with fewer than 500 trades." | Table 5 note, txt L1455-1456 | same | peer-reviewed | same |
| Conversion C1 | 11.87%/252 = 0.0471% = 4.71 bp; x 21,000 / 10,000 = 9.89 NQ pts / 0.25 = 39.6 MNQ ticks (at 25,000: 11.78 pts = 47.1 ticks); x 6,000 = 2.83 ES pts = 11.3 MES ticks. Medium tercile 2.56 bp = 5.38 NQ pts = 21.5 MNQ ticks. | - | R4 arithmetic | - | - | - |
| RTH Confluence signal, OOS | net +11.82 pts, sd 53.8, N 196, T 3.11 | "Walk-forward OOS T-statistic (net) 3.11 / Walk-forward OOS mean net return +11.82 pts / Walk-forward OOS std deviation 53.8 pts / Walk-forward OOS N 196" | Table 10, txt L424-431 | Mesfin, M. (2026), "Structural Limits of OHLCV-Based Intraday Momentum Signals in MNQ Futures: A Systematic Falsification Study", arXiv 2605.04004 https://arxiv.org/pdf/2605.04004 | working-paper | pages/R4/arxiv_2605.04004_mnq_falsification.pdf (sha256 d0bd26e4...a80) |
| Volume gate in that signal | z > 0.5 | "the GMM (Gaussian Mixture Model) regime label equals Regime 1 (Active Flow), the rolling 200-bar Markov transition probability from Regime 1 to Regime 2 exceeds 0.15, and the rolling 50-bar volume z-score exceeds 0.5" | Sec 5.1, txt L411-413 | same | working-paper | same |
| Search breadth and contamination (selection) | 53+ combinations | "53+ combinations across 7 parameters evaluated before locking. Walk-forward OOS run once on locked specification." and "Fit once on 2022 data only. Applied forward, no per-fold refitting. Contaminates W1 OOS (2022 H2)." | Table A1, txt L686-689, L678-679 | same | working-paper | same |
| Friction assumed | 2.0 MNQ pts RT | "For MNQ: 2.0 points ($4.00 per micro contract), covering bid-ask spread, NinjaTrader exchange fees, and conservative slippage." | Sec 2, txt L122-123 | same | working-paper | same |
| Idealised stop fills | - | "80 × ATR_ratio points below Entry 1. Filled at exact stop price (idealized fill assumption)." | Table A1, txt L683-684 | same | working-paper | same |
| London Signal B, OOS | net +4.09 pts, N 247, T 4.30 | "Walk-forward OOS (N=247, T=4.30, net +4.09 pts, p=0.000025): primary result." | Table A2, txt L725-726 | same | working-paper | same |
| VVG best configuration | net +7.80 pts, T 1.46, N 127 | "N (OOS trades) 127 / Mean net return +7.80 pts / T-statistic +1.46" ... "Verdict FAIL — T = 1.46; 2024 year failure" | Table 8, txt L305-318 | Mesfin, M. (2026b), "A Validated Volatility-Volume-Gap Classifier for Regime Identification in MNQ Intraday Data", arXiv 2605.11423 https://arxiv.org/pdf/2605.11423 | working-paper | pages/R4/arxiv_2605.11423_mnq_vvg.pdf (sha256 70501c60...fe6d) |
| VVG volume feature | first-bar volume z vs 20-day | "Feature 3 is the first-bar volume deviation: (first_bar_volume − rolling_mean_20) / rolling_std_20." | Sec 2.2, txt L111 | same | working-paper | same |
| ZA23 VWAP rule (owned by R10; source of K1-vwap-01) | $25,000 to $192,656 net, 21,967 trades, 2018-01-02..2023-09-28, QQQ | "VWAP TT (QQQ) $25,000 $192,656 13,094,444 6,547 21,967" (Table 3) and "we assumed no slippage in our order fills" (Sec 3.4) and "a commission rate of $0.0005 per share" | E.23 copy txt L626-634, L346-347, L364 | Zarattini, Aziz (2023), SSRN 4631351; https://concretumgroup.com/wp-content/uploads/2026/02/Volume-Weighted-Average-Price.pdf | working-paper | E.23 copy (pdf sha256 47137abd...05c8); R10 copy pages/R10/concretum_Volume-Weighted-Average-Price.pdf |
| ZA23 per trade (derived, not published) | geometric mean ln(192,656/25,000)/21,967 = 0.93 bp a trade net of commission, zero slippage; at NQ 21,000 = 1.95 pts = 7.8 MNQ ticks | - | R4 arithmetic | - | - | - |
| ZA23 hit ratio | 17.0%, gain:loss 5.67 | "VWAP TT (QQQ) 17.0% 5.67 6.5% -1.4%" | Table 4, txt L644-645 | same | working-paper | same |
| K1-vwap-01 (the ZA23 rule on MNQ, research window) | 3,502 trips, net -$8,428.18, daily t -1.115 | "11 \| K1-vwap-01 MNQ \| 3,502 \| -56.3758 \| 874.31 \| -1.115 \| -8,428.18" and "its gross could not be separated from costs here (no prices in the records)" | reports/E.7_RETURN.md L221, L225-226 | program record | program | reports/E.7_RETURN.md |
| K1-vwap-01 per trip (derived) | -8,428.18 / 3,502 = -$2.41 net = -4.81 MNQ ticks; plus D8 RT 4.119 ticks = about -0.69 ticks gross if every trip paid the day-session RT (lead to verify; E.7 says gross not separable) | - | R4 arithmetic | - | - | - |
| Trades schema carries aggressor side | A/B/N | "The side that initiates the trade. Can be **A**sk for a sell aggressor in a trade, **B**id for a buy aggressor in a trade, or **N**one where no side is specified." | TradeMsg doc comment, record.rs L247 | Databento DBN source, https://raw.githubusercontent.com/databento/dbn/main/rust/dbn/src/record.rs | vendor | pages/R4/github_dbn_record.rs (sha256 2617f6db...f660) |
| Block trades in ES are informative asymmetrically by regime | no size | "block purchases are relatively more informed in bear markets and block sales are relatively more informed in bull markets. Using a sample of large trades executed in the E‐mini S&P 500 index futures and SPDR S&P 500 exchange traded fund, we find evidence consistent with our theoretical model." | abstract | Frino, Mollica, Romano, Zhou, J. Futures Markets 37 (2017) 359-373, https://ideas.repec.org/a/wly/jfutmk/v37y2017i4p359-373.html | peer-reviewed [secondary-only] | pages/R4/repec_frino_2017_jfm_blocks.html (sha256 87ee214b...7532) |

## 4. Negative evidence

| finding | quote | location | source | grade |
|---|---|---|---|---|
| Volume spike and volume dry-up on MNQ 5-min bars: all four FAIL; net -1.92, -2.45, -2.42, -1.99 pts at 2.0 pts friction, so gross +0.08, -0.45, -0.42, +0.01 pts | "Volume Spike Up 2,122 −1.92 −2.21 39.9 ... FAIL" (and three similar rows); "At sample sizes of 723 to 2,412, a near-zero T-statistic is a precise estimate, not an underpowered one. The null is real." | Table 7, txt L304-319 | Mesfin 2026, arXiv 2605.04004 | working-paper |
| Eleven of fourteen OHLCV families have gross 0.07-1.50 MNQ pts | "Eleven signal families fail because their maximum gross return before friction is 0.07 to 1.50 points per trade, below the 2.0-point MNQ friction floor." | abstract, txt L22-23 | same | working-paper |
| VVG reversal fails year stability; 2024 negative | "2024 net points −26.75" | Table 8, txt L313 | Mesfin 2026b, arXiv 2605.11423 | working-paper |
| Order-flow shocks in the E-mini dissipate in about one second (BBO-based OFI; R3's domain, cited for the trade-side horizon) | "Impulse responses indicate that shocks dissipate almost entirely within a second." | abstract, txt L23; sample "1,490 trading days from January 2, 2008 to December 31, 2013" txt L118 | Takahashi (2025), "Returns and Order Flow Imbalances: Intraday Dynamics and Macroeconomic News Effects", arXiv 2508.06788v4 | working-paper |
| Signed-trade imbalance is offset by liquidity imbalance (no exploitable drift) | "efficiency is maintained by a liquidity imbalance that co-moves with the imbalance of buyer vs. seller initiated transactions ... after a small number of time steps it cancels all the inefficiency caused by the transaction sign imbalance, bounding the price impact." | abstract | Farmer, Gerig, Lillo, Mike (2006), arXiv physics/0602015 | working-paper |
| Extreme order-sign imbalance coincides with pinned prices (includes EUREX DAX, BUND futures) | "We further show that extreme order flow imbalance is not associated with large returns. To the contrary, it is observed when the price is “pinned” to a particular level." | abstract, txt L15-16; instruments txt L79 | Patzelt, Bouchaud (2018), arXiv 1706.04163 (Phys. Rev. E 97, 012304) | peer-reviewed |
| Gao low-volume tercile not significant | "1.67% (0.98) on low volume days" | WP txt L537 | Gao et al. | peer-reviewed |
| The unconditional Gao/Baltussen effect on NQ at program cost failed | E20H6-T1 "gross 1.25 ticks vs 4.08 cost" | brief_shared.md section 5 | program record | program |
| ZA23 VWAP rule failed on MNQ in the research window | K1-vwap-01, daily t -1.115, net -$8,428 | reports/E.7_RETURN.md L221 | program record | program |
| ZA23 relies on zero slippage and $0.0005/share | "we assumed no slippage in our order fills"; footnote: "We observed that significantly higher commission rates can affect the strategy’s effectiveness." | Sec 3.4, footnote 6 | ZA23 | working-paper |
| On-balance volume (OBV) cross-sectional, monthly, Russell 3000: REFUTED (stocks, monthly; out of scope, noted for completeness) | "Volume (OBV) [−0.193, 0.175] REFUTED (material exclusion: US < δS )" | Table, txt L244 | "Retail Trader's Ruin: An Anatomy of Popular Signal Failure", arXiv 2607.20093 | working-paper |
| Volume profile / POC / value area / cumulative-delta divergence / VWAP-band fade: search returned only vendor and education pages; no tested evidence. A vendor blog DAX VWAP-band fade backtest (-98.6%, 2016-2026) appeared in search results only | (search results; not fetched) | WebSearch 08:4x-08:5x UTC | backtrex.com, luxalgo.com, nexusfi.com | pointer [unverified] |
| VPIN predicts volatility (not direction) and its predictive content is disputed | (not fetched: SSRN blocks automation; NBER terms forbid robots) | - | Andersen, Bondarenko (2014) J. Financial Markets "VPIN and the flash crash"; Easley, López de Prado, O'Hara rejoinder | peer-reviewed [unverified] |
| Pre-FOMC embargo-window order imbalance in ES predicted the surprise, but the lockup was tightened in 2014 (decay by rule change) | (not fetched: SMU repository Incapsula block) | - | Bernile, Hu, Tang (2016) JFE 121(3) 496-520 | peer-reviewed [unverified] |

## 5. Data and cost

- Owned (section 4 of the brief): ohlcv-1m bars carry volume, so R4-C1..C4, session VWAP (typical price x volume,
  as K1-vwap-01 does), relative volume, opening-volume surprise and volume z-scores are all computable now. A
  1-minute "volume profile" can only spread each bar's volume over its high-low range: an approximation of
  volume at price, not the real profile.
- Not owned: true volume at price (POC, value area at tick resolution) and cumulative volume delta need trade
  prints with aggressor side: Databento `trades` (aggressor side field quoted in section 3) or `tbbo`
  (trades plus the BBO at each trade).
- Published / logged prices (no new quote requested):
  - E.0 logged quotes (reports/stage_e0_quotes.md, free metadata endpoint, 2026-09-23), 5 sample days
    (2025-05-14, 2025-08-13, 2025-11-12, 2026-02-11, 2026-04-15): TBBO ES $4.41, NQ $3.58, MNQ $8.62; mbp-1
    ES $5.44, NQ $5.92, MNQ $13.46 (rows L28, L29, L32). A linear extrapolation (not a quote) is about $0.72
    a trade date for NQ TBBO, so about $180 for 250 dates; MNQ about $430. `trades` is smaller than `tbbo`.
  - databento.com/pricing (R3's Firecrawl excerpt, about 08:47Z): "$125 in free credits"; example
    "CME Globex MDP 3.0 / 1 product(ES) / MBO 14 months / MBP-1 12 months / TBBO 15 months / Trades 16 months";
    Standard plan "$199 per month ... 1 year of L1 history" (L1 = MBP-1, TBBO, Trades). Terms: databento.com
    ToU forbids redistribution of Materials (R3's terms line); saved pages stay local.
  - Live aggressor-side data through TopstepX/ProjectX for a live CVD signal: not checked (no API calls allowed).

## 6. Prop compatibility

- R4-C1: one entry at 14:30 CT, flat by 15:00 CT (before 15:10); 1 trade a day; no release in the window except
  rare 13:00/13:30 CT FOMC days (already ended by 14:30; D9.5a guard applies). Automatable on 1-min bars.
- R4-C2: RTH entries, 65-min hold, exit at bar 13 or RTH end (15:00 CT): compatible. Entries near 07:30 CT
  releases do not occur (RTH starts 08:30 CT), but 09:00 CT ISM releases fall inside the window (P06: not at
  full size into a scheduled major release). The author's stop is an idealised fill; DLL sizing must assume worse.
- R4-C3: 02:00-07:30 CT lies inside Topstep's trading day (17:00-15:10 CT), so allowed; the exit "at 08:30 ET"
  is exactly 07:30 CT, the CPI/NFP/PPI release minute: P06 risk and a fill at the release; the lead should
  require exit before 07:29 CT on release days. Overnight spreads are wider than the D8 day-session RT.
- R4-C4: about 10 days a year, too few for a Combine on its own.
- None needs HFT; all fit 1-min bar automation. CVD/footprint variants would need a live trade feed.

## 7. Overlap with tested mechanisms

Grepped reports/stage_e25_briefs/r0_mechanism_index.md (rows 52, 89, 195, 277) and
reports/stage_e23_briefs/inventory/K1.md (rows 11, 50-54, 59-60).
- K1-vwap-01 (index row 89; K1.md row 11): "sign of bar close vs session VWAP from 08:30; stop-and-reverse,
  <= 20 entries/day" on MNQ: this is the ZA23 rule (E.23 M5 file: "The published source of the K1-vwap-01 rule
  (QQQ, 1-minute bars)"). Tested in E.7 (FAIL), as a Gate 0 feature k1_vwap_dist (FAIL) and in the E.20 ML
  search (FAIL). ZA23 is therefore not a new candidate; any VWAP-band, anchored-VWAP or VWAP-reversion variant
  would be a new trial on the same variable.
- ZA23: appears only in reports/stage_e23_briefs/mech/M5_BREAKOUT_LOCATION.md (row 22) and the E.25 prompt; R10
  owns the Zarattini/Concretum papers.
- C-H2 (index row 52): "post-spike exhaustion fade: bar with volume z > 3.0 or range ratio > 3.0" (D.1, MES):
  FAIL; the Mesfin volume-spike null agrees.
- Gate 0 (row 195) included g10 logvol30 and cp1_ret as ML features (FAIL); E.20 ML search also. R4-C1 differs:
  a pre-declared single conditional rule (tercile of first-30-min volume within year) on the cp1 / E20H6
  mechanism, not a pooled ML feature. It is the same mechanism as K1-cp1-01 and E20H6-T1/T2, so it adds to N
  inside that family.
- R4-C2/C3: no index member uses a GMM regime label with a volume z gate; nearest are the D-H1..D-H3 volatility
  gates and RT6/RT7 sizing. R10 also holds a copy of arXiv 2605.04004 (pages/R10/arxiv_2605.04004.pdf); the
  lead should merge any R10 row on the same paper.
- R4-C4: overlaps K1-cp2-01 (opening range), D-H4 (overnight gap), Gate 0 g05_gap.

## 8. Re-dig verdict checks

Not a re-dig reader (R4 is first wave); verdict_checks left empty. One observation for the lead, not a verdict
check: the ZA23 figures assume zero slippage, which is consistent with the E.7 K1-vwap-01 failure at program costs.

## 9. Fetch log

| url | UTC | sha256 | saved path | status | tool |
|---|---|---|---|---|---|
| https://arxiv.org/pdf/2605.04004 | 2026-10-18T08:41:23Z | d0bd26e424a0c81bbca149e35566a3b9929a3cd207934e07638a99e78ca4ca80 | pages/R4/arxiv_2605.04004_mnq_falsification.pdf | ok | curl |
| https://arxiv.org/pdf/2605.11423 | 2026-10-18T08:41:43Z | 70501c60f354060a1ed23f209d82eb7a84482f4372620f0481e18afe894fbe6d | pages/R4/arxiv_2605.11423_mnq_vvg.pdf | ok | curl |
| https://api.openalex.org/works/W7215069909, W7214779915, W7171720672 | 2026-10-18T08:43:2xZ | 904a24ca..., 23f685fa..., c7095a78... | pages/R4/openalex_W*.json | ok (metadata; no abstracts) | curl |
| https://api.semanticscholar.org/graph/v1/paper/search (two title queries) | 2026-10-18T08:44Z | 65ab993d... | pages/R4/s2_value_area_*.json | throttled (429) | curl |
| https://ink.library.smu.edu.sg/lkcsb_research/4482 | 2026-10-18T08:45:11Z / 08:45:29Z | d0203228... / 8fb62efa... | pages/R4/smu_*.html | blocked (Incapsula bot wall; curl and scrapling get) | curl, scrapling |
| https://databento.com/docs/schemas-and-data-formats/trades | 2026-10-18T08:46:04Z | ea3c0d4d... | pages/R4/databento_docs_trades.html | ok but JavaScript shell, no content (not used) | curl |
| https://raw.githubusercontent.com/databento/dbn/main/rust/dbn/src/record.rs | 2026-10-18T08:46:24Z | 2617f6db93abb318a0a9e0ecabdd08876ca8c969e82d5341f102cbc58106f660 | pages/R4/github_dbn_record.rs | ok | curl |
| https://arxiv.org/pdf/2508.06788 | 2026-10-18T08:46:43Z | 79bb14f8e7d8d859e971187825433511c6d0ce00f1ff267be24887a48bbb95b2 | pages/R4/arxiv_2508.06788_takahashi_emini_ofi_var.pdf | ok | curl |
| https://arxiv.org/pdf/2607.20093 | 2026-10-18T08:47:03Z | 14f6a756437d0a6306d8ff09bb00dfbd3fcf0f32171e498dda5e09d0bddd1cae | pages/R4/arxiv_2607.20093_retail_traders_ruin.pdf | ok | curl |
| https://arxiv.org/pdf/1706.04163 | 2026-10-18T08:47:24Z | e1143e710d1401b4837e41075bdb3f0090d69a8a08b9c0ca62b1333a42070fb6 | pages/R4/arxiv_1706.04163_patzelt_bouchaud_aggregate_impact.pdf | ok | curl |
| https://arxiv.org/pdf/2101.07410 | 2026-10-18T08:47:44Z | 7876a7bb72804b041fc3aff49851795a71afd7e2643f1a51708dd573430930bc | pages/R4/arxiv_2101.07410_chung_bellotti_sr_levels.pdf | ok (price-based S/R; not used as evidence) | curl |
| https://centaur.reading.ac.uk/95566/1/Accepted-Version.pdf | 2026-10-18T08:55:14Z | 39add97e355b49c01ac9d5f0ba76a584fb593e8ec293545127e5c60ca2830bee | pages/R4/li_sakkas_urquhart_2022_itsm_accepted.pdf | ok after two transient http000 | curl |
| https://arxiv.org/pdf/physics/0602015 | 2026-10-18T08:55:57Z | 238f2b1e04d500bf9af9d097c1a6bb5b483478261f1c961e5819698fe809c35a | pages/R4/arxiv_physics0602015_farmer_lillo_comment.pdf | ok | curl |
| https://ideas.repec.org/a/wly/jfutmk/v37y2017i4p359-373.html | 2026-10-18T08:56:04Z | 87ee214b3bd5890dca19835ef63491cb8659d0e1012736ebdaab064c65137532 | pages/R4/repec_frino_2017_jfm_blocks.html | ok | curl |

Terms read: arxiv.org (R3's line in terms_log.md; R4's duplicate removed), databento.com (R3's line),
ideas.repec.org (existing line), centaur.reading.ac.uk (R4 appended), github.com / raw.githubusercontent.com
(R4 appended), ink.library.smu.edu.sg (robots saved terms/ink.library.smu.edu.sg_robots.txt; blocked anyway),
www.nber.org (another reader's line: forbidden; conference.nber.org not fetched), SSRN (brief: no automation).

Budget notices (UTC):
- 08:42:52 Firecrawl firecrawl_search: "Rate limit exceeded. Consumed (req/min): 20" (twice).
- 08:44 Semantic Scholar keyless: HTTP 429 on two queries; not retried (OpenAlex fallback also failed).
- 08:44 OpenAlex: HTTP 429, polite-pool daily budget exhausted ("creditsRemaining":9, "retryAfter":54930); no
  OpenAlex key in .env; OpenAlex unusable for the rest of the run.
- 08:45 Firecrawl firecrawl_search: "Insufficient credits" (account out of credits). Firecrawl paper search
  (firecrawl_research_search_papers) still answered at 08:49Z and 08:57Z.
- WebSearch calls used by R4: 15 of 45 (no over-budget notice).

## 10. Unfinished and unverified

- Alqaydi (2026), "Harvesting the Value Area: Auction Geometry as a Durable Intraday Edge in Nasdaq-100 Futures",
  SSRN 7546200 / 7529379, and Howard (2026), "Stop Distance, Exit Methodology, and Signal Preservation in
  Intraday Value Area Breakouts: Evidence from E-mini S&P 500 Futures", SSRN 6350238: titles from OpenAlex
  metadata only; no abstract or numbers [unverified]. These are the only value-area tests found; the lead may
  want them read by a human through SSRN.
- Andersen-Bondarenko VPIN critique, Easley-López de Prado-O'Hara-Zhang "Microstructure in the Machine Age"
  (RFS 2021, 87 futures), Chordia-Green-Kottimukkalur (RFS 2018, ES order flow at milliseconds after releases;
  R6's territory) and Bernile-Hu-Tang (JFE 2016): not fetched (SSRN, NBER terms, Incapsula) [unverified].
- Forward citations and replications of Gao et al. on volume terciles after 2013: not searched (OpenAlex out of
  budget, S2 throttled).
- No independent replication of any Mesfin signal was found; the author mentions external replication
  attempts but publishes none.
