# R12: volatility and regime filters for intraday books (Stage E.25, research only)

Reader: SourceReader-RegimeFilters-OpusHigh (R12). Started 2026-10-18 01:38 PDT; this version written
01:53-02:10 PDT. Machine-readable copy: reports/stage_e25_briefs/R12_regime_filters.json.
Price levels used for every conversion: ES (and MES) 6,000; NQ (and MNQ) 23,000. MES and MNQ tick
0.25 index point. Conversion: bp x price / 10,000 = index points; points / 0.25 = ticks. A one-tick
move at ES 6,000 is 0.42 bp. Hurdles (brief section 2): MES about 3.0 ticks, MNQ 6.18 ticks.

## 1. Answer (at most 250 words)

In the published record, volatility filters do raise the gross per trade of intraday momentum. But
every such result conditions on information that is in-sample or not tradeable, or it has decayed,
or it comes from an unreviewed source with heavy search. The clearest case is Gao, Han, Li and Zhou
(2015 WP / JFE 2018), SPY 1993-2013. First-half-hour to last-half-hour momentum earns 2.65 bp per
trade unconditionally (6.4 MES ticks at ES 6,000), 5.85 bp in the high first-half-hour-volatility
tercile (14.0 ticks), 0.21 bp in the low tercile (0.5 ticks), and 7.95 bp on FOMC days (19.1 ticks).
The terciles use full-sample cutoffs. Rosa (2022, abstract only) finds the predictability disappears
out of sample. The program's own NQ test of the same family (E20H6 T1) grossed 1.25 ticks. Lundström
(2013/2017) finds ORB returns rise steeply with same-day volatility. That is look-ahead: GARCH
forecasts of the volatility state "did not improve the results". The overnight-drift "buy the dip"
(Boyarchenko-Larsen-Whelan) is about 3x stronger at high VIX, but its authors report it "flat" for
2021-25. A VIX-term-structure (VIX/VIX3M, VIX9D, VIX1D) filter for intraday ES/NQ trades: no study
found. The strongest candidate is not a filter but a calendar regime: the 3rd-Friday a.m.-settlement
reversal (Baltussen-Terstegge-Whelan 2024). ES futures fall 12.89 bp from 3rd-Friday open to close,
2003-2021 (30.9 MES ticks), and the two-leg trade earns 24.2 bp net. The sample stops in 2021 and no
post-publication test was found. Two arXiv MNQ regime-classifier signals (Mesfin 2026) report an
out-of-sample edge. They are unreviewed and carry admitted selection exposure.

## 2. Candidate hypotheses

Gross per trade in micro ticks uses the price levels above. "Overlap" ids come from
r0_mechanism_index.md.

| id | hypothesis | instruments | entry window CT | hold | trades/yr | best source (grade) | sample / OOS | published effect | gross pts | gross micro ticks | gross/net | dispersion | owned | window testable | overlap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R12-C1 | 3rd-Friday a.m.-settlement reversal, intraday leg: short at the RTH open on the monthly a.m.-settlement Friday (SOQ day), cover by noon ET or at the close | MES (also MNQ, MYM: the paper says the spike is present in Dow and Nasdaq-100 a.m. settlements; their numbers were not read) | 08:30 CT | to 11:00 CT (paper: "fully reverts afterward by about noon") or 15:00 CT (the published figure) | 12 | Baltussen, Terstegge, Whelan, "The Derivative Payoff Bias", Sept 2024 (AEA 2025 program copy) (working-paper) | 2003-2021; no OOS or post-publication test found | ES futures Fr-open to Fr-close mean -12.89 bp (index -16.42 bp) | 7.73 ES pts | 30.9 MES | gross (trade prices) | t -2.40, sd 80.45 bp per event; n about 227 events | yes (1-min bars + third-Friday calendar) | partial: about 15 events in 2025-04..2026-06, fewer after roll blackout | E-H3 (quarterly witching short, 14:30-15:00 CT): different window and monthly not quarterly |
| R12-C2 | 3rd-Friday spike, overnight leg, Topstep-legal form: long at the 17:00 CT Globex reopen on the 3rd Thursday, sell at the 08:30 CT open on the 3rd Friday | MES (MNQ, MYM as above) | 17:00 CT Thu | to 08:30 CT Fri | 12 | same (working-paper) | 2003-2021 | ES futures Th-close to Fr-open mean +14.30 bp (index +18.24 bp, t 4.53). The share earned before 17:00 CT (the Topstep gap) is not given in the text | at most 8.58 ES pts | at most 34.3 MES | gross | t 3.54, sd 60.53 bp | yes | partial (about 15 events) | A-H1 / E-H1 (overnight holds): different calendar trigger |
| R12-C3 | Gao-type intraday momentum filtered on high first-half-hour realized volatility: trade the sign of the first 30-min RTH return over the last 30 min, only when first-30-min 1-min realized volatility is in the top tercile (expanding-window cutoff; the paper used full-sample terciles) | MES, MNQ | 14:30 CT | 30 min, flat 15:00 CT | about 84 (one third of days) | Gao, Han, Li, Zhou, WP Dec 2015 (JFE 129, 2018) (working-paper read; peer-reviewed version not read) | 1993-2013 SPY; recursive OOS timing, but terciles sorted on the full sample | high tercile 14.73% p.a. (x252, one trade a day) = 5.85 bp per trade; unconditional 6.67% p.a. = 2.65 bp; low tercile 0.54% = 0.21 bp | 3.51 ES pts (high tercile) vs 1.59 unconditional | 14.0 MES (high) vs 6.4 (unconditional) | gross | t 3.80 (high tercile), Sharpe 1.63; unconditional Sharpe 1.08 | yes | yes | K1-cp1 (morning sign to last half hour), E20H6 T1/T2 (large-move filter, FAIL), Gate 0 g06_rv60/g09_vol_state as separate linear features (no interaction) |
| R12-C4 | Same momentum, FOMC-announcement days only | MES, MNQ | 14:30 CT | 30 min | about 8 | Gao et al. WP 2015 Table 8 (working-paper) | 1993-2013 | FOMC-day eta(r1) 20.04% p.a. = 7.95 bp per trade | 4.77 ES pts | 19.1 MES | gross | t not read (Table 8 Panel B not extracted) | yes (owned FOMC calendar) | partial (about 10 FOMC days) | K9-anncday-01 (draft), E-H1/E-H2 (FOMC drift and post-release momentum), K1-cp1 |
| R12-C5 | GMM regime-transition long, London session (Mesfin "London Signal B"): long at the next 15-min bar after a clean regime 0 to regime 2 transition, 03:00-08:30 ET | MNQ | 02:00-07:30 CT | 60 min or to 07:30 CT, 20-pt stop | about 80 (247 OOS trades over about 3 years) | Mesfin, arXiv 2605.04004, May 2026 (working-paper; independent, unreviewed) | 2021-2025 5-min bars; walk-forward, GMM refit per fold | OOS net +4.09 pts at 2.0-pt round-trip friction | 6.09 NQ pts (net + friction) | 24.4 MNQ | net (gross derived) | T 4.30, per-trade Sharpe 0.27 (4.09/14.97), N 247 | yes | yes | A-H1 (european-open overnight drift): different trigger (regime classifier) |
| R12-C6 | GMM regime + Markov-gate pullback long in RTH (Mesfin "RTH Confluence") | MNQ | RTH | 13 five-min bars | about 65 | same (working-paper) | 2022-2025; W1 fold contaminated; 53+ combinations searched before locking | OOS mean net +11.82 pts | 13.82 NQ pts | 55.3 MNQ | net (gross derived) | T 3.11, sd 53.8 pts, N 196 | yes | yes | C-H1..C-H4 reversal family, D-H1 vol gate: different (multi-feature regime) |

Why these and no more: the only filters with a published per-trade size are the ones in rows C3 and
C4, and both are pre-2014. The R12-C5/C6 numbers are a single unreviewed author's, net of his own
friction. R12-C1/C2 is the one regime (a calendar regime) with a peer-presented, futures-measured,
after-cost result. Every other filter read is a non-survivor (section 4).

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| 3FPS futures legs | +14.30 bp / -12.89 bp | "Panel (b) Futures ... mean 2.69 0.91 3.60 -2.09 -1.71 14.30 -12.89 ... t-stat 2.75 0.68 2.12 -0.60 -0.28 3.54 -2.40 ... Std 67.47 92.25 117.16 51.96 90.33 60.53 80.45" | Table II, columns Thclose-to-Fropen and Fropen-to-Frclose; "Returns are in basis points. The sample period is 2003 to 2021." | Baltussen, Terstegge, Whelan (Sept 2024), The Derivative Payoff Bias, https://www.aeaweb.org/conference/2025/program/paper/N7rsBN2N | working-paper | pages/R12/aea2025_derivative_payoff_bias.pdf (+ dpb.txt) |
| 3FPS trade after costs | 27.48 gross, 24.20 net bp | "Panel (a): Excluding Trade Costs mean 27.48 0.10 t-stat 3.94 0.06 ... Panel (b): Including Trade Costs mean 24.20 -3.18 t-stat 3.47 -1.90" | Table A.4; strategy "buys S&P 500 E-mini futures at 3rd Thursday close, reverses into a short positions at 3rd Friday open and closes the position at 3rd Friday close" | same | working-paper | same |
| 3FPS timing and persistence | reverts by noon | "a tent-shaped reversal pattern from the close of regular trading on 3rd Thursdays, which peaks exactly when the SOQ is calculated on 3rd Fridays and fully reverts afterward by about noon 3rd Friday ... The 3FPS is present in almost every year since 2003" | Introduction, p. 2 | same | working-paper | same |
| No p.m.-window pattern | none | "Around the p.m. settlement window there is no corresponding pattern, highlighting the specialness of the a.m. settlement window." | p. 3 | same | working-paper | same |
| Intraday momentum, volatility terciles OOS | 0.54% / 4.75% / 14.73% p.a. | "The average return per annum (and its t-statistic) of the η(r1 ) strategy rises substantially from 0.54% (0.43) in the low volatility group, to 4.75% (2.27) in the medium volatility group, and then to 14.73% (3.80) in the high volatility group." | Section 3.1.2; Table 5 Panel A | Gao, Han, Li, Zhou, Market Intraday Momentum, WP Dec 2015 (JFE 129(2) 2018 394-414), c.mql5.com copy | working-paper | reports/stage_e20_briefs/shared/gao_han_li_zhou_wp2015_mql5.pdf.txt (E.20 copy, re-used) |
| Tercile cutoffs are full-sample | in-sample sort | "we first sort all trading days into terciles based on the first half-hour volatility and report the out-of-sample timing results in Panel A of Table 5" | Section 3.1.2 | same | working-paper | same |
| Unconditional and annualization | 6.67% p.a., x252 | "the average return is 6.67% on an annual basis" ; "we still annualize the returns multiplying by a factor of 252 because we only trade once per day" | Section 3.1.1 and footnote 7 | same | working-paper | same |
| FOMC days | 20.04% p.a. | "The greatest economic gains are delivered on the release days of the FOMC minutes. The annualized average return reaches a high level of 20.04%. This is close to four times the level on days without FOMC news." | Section 4, Table 8 Panel B | same | working-paper | same |
| Costs post-2005 | 7.96% gross, 6.52% net p.a. | "The average return of market timing using the first half-hour return is 6.52% after transaction costs compared with 7.96% before transaction costs." | Section 5.2, Table 10 Panel B | same | working-paper | same |
| ORB vs volatility state is look-ahead | in-sample | "these are in-sample results. In actual trading, traders do not a priori know the volatility state" | Section 3.2, p. 16-17 | Lundström, Day trading returns across volatility states, Umeå Economic Studies 861 (rev. 2017) | working-paper | pages/R12/lundstrom_ues861.pdf (+ .txt) |
| GARCH volatility forecasts do not help ORB | none | "We tried various ARCH and GARCH specifications to predict the volatility state, but without improving the results in any significant way. We find that expansion days, which result in high ORB returns, tend to come unexpectedly after a number of contraction days." | footnote 2, p. 17 | same | working-paper | same |
| ORB S&P 500 OOS, no costs | A = 0.0004 (4 bp), rho 0.5% | "S&P 500 0.5 3314 0.49 0.0004 0.0057 ... 1.5 749 0.52 0.0006 0.1755 2.0 368 0.52 0.0006 0.4937" | Table 2 (S&P 500 futures 1991-2010, daily OHLC) | same | working-paper | same |
| Overnight drift x VIX | 2.6 / 6.1 / about 0 bp | "generates a return response of ... 2.6 basis points. With the VIX at its 90th percentile (30%) the return response is 6.1 basis points and with the VIX at its 10th percentile (12 %) there is close to zero effect." | Section IV, eq. 8, p. 24-25 | Boyarchenko, Larsen, Whelan, The Overnight Drift, NY Fed SR 917 (rev. Aug 2022; RFS 36(9) 2023) | working-paper (peer-reviewed version in RFS) | pages/R12/nyfed_sr917_overnight_drift.pdf (+ .txt) |
| Overnight drift double sort, high VIX | 12.66 bp | "Panel B3: OD Average Returns VIX Low VIX Med VIX High ... RSV Low 0.88 4.93 12.66 11.78 0.00" | Table IV | same | working-paper | same |
| Buy-the-dip after costs | 6.07% gross, 4.04% net p.a. | "RSVt−1 close < 0 ... Mean ... 6.07 ... (a) Without Transaction Costs ... 4.04 ... (b) With Transaction Costs" ; "holds the e-mini on ∼ 50% of trading days" | Table IX; Section V | same | working-paper | same |
| Overnight drift gone 2021-25 | flat | "The 2:00–3:00 window—previously responsible for more than 60 percent of the contract’s 5.9 percent annualized close-to-close return—is flat. The same pattern holds in the E-mini Nasdaq-100 (NQ) and E-mini Dow Jones (YM) contracts." | post body | Boyarchenko, Larsen, Whelan, The Disappearing Overnight Drift, Liberty Street Economics, 2026-07-01 | exchange-regulator (Federal Reserve blog) | pages/R12/lse_disappearing_overnight_drift.html (+ .txt) |
| Imbalance-return link broken, VIX unchanged | RSV sd 6.5% to 2.9% | "The Order-Imbalance–Overnight-Return Relationship Has Broken Down" ; "The VIX, a standard proxy for return variance, is little changed: its mean fell only modestly from 20.4 in the original sample to 19.4 in the post-publication period" | post body | same | exchange-regulator | same |
| MNQ OHLCV families below friction | 0.07-1.50 pts | "Eleven signal families fail because their maximum gross return before friction is 0.07 to 1.50 points per trade, below the 2.0-point MNQ friction floor." | Abstract | Mesfin, Structural Limits of OHLCV-Based Intraday Momentum Signals in MNQ Futures, arXiv 2605.04004 (May 2026) | working-paper | pages/R12/arxiv_2605.04004.pdf (+ .txt) |
| London Signal B | net +4.09, T 4.30, N 247 | "London Session Signal B (walk-forward OOS T = 4.30, mean net +4.09 points, N = 247, p = 0.000025)" ; "Per-trade Sharpe = mean net / std = 4.09/14.97 = 0.27" | Abstract; Table 11 note | same | working-paper | same |
| RTH Confluence | net +11.82, T 3.11, N 196 | "Walk-forward OOS T-statistic (net) 3.11 ... Walk-forward OOS mean net return +11.82 pts ... Walk-forward OOS std deviation 53.8 pts ... Walk-forward OOS N 196" | Table 10 | same | working-paper | same |
| RTH Confluence selection exposure | 53+ combinations | "the RTH Confluence Signal specification was selected after evaluating 53 or more parameter combinations across seven parameters" | Section 6 limitations | same | working-paper | same |
| Idealized stops | yes | "Stop 80 × ATR_ratio points below Entry 1. Filled at exact stop price (idealized fill assumption)." | Appendix A, Table A1 (also A2: "20 points fixed. Filled at exact stop price") | same | working-paper | same |

## 4. Negative evidence (nulls, decay, after-cost failures)

Unconditional vs conditional, side by side (gross per trade; MES ticks at ES 6,000 unless stated):

| effect | unconditional | conditional (filter) | filter tradeable ex ante? | holds later? |
|---|---|---|---|---|
| Gao r1 -> last half hour, SPY 1993-2013 | 2.65 bp = 6.4 ticks | high first-30-min vol tercile 5.85 bp = 14.0 ticks; low tercile 0.21 bp = 0.5 ticks; FOMC days 7.95 bp = 19.1 ticks | partly (first-30-min vol is known at 09:00 CT, but the published cutoffs are full-sample) | Rosa 2022 (abstract): "The predictability disappears in the out‐of‐sample period"; program E20H6 T1 (rest-of-day form, NQ) gross 1.25 ticks |
| Overnight drift 02:00-03:00 ET, ES 1998-2020 | 1.5 bp per hour (3.6 ticks); OD strategy Sharpe 1.10 gross, -0.54 net | BtD (negative closing imbalance) 6.07% p.a. over about 126 trades = 4.82 bp = 11.6 ticks gross, 7.7 net; high-VIX x low-RSV cell 12.66 bp | VIX yes; RSV needs signed volume (not owned) | No: "flat" 2021-25 (authors, 2026) |
| ORB S&P 500 futures, daily OHLC 1991-2010 | rho 0.5%: 4 bp per day (9.6 ticks), no costs | top-vs-bottom same-day vol decile: about 150 bp per day difference | No (same-day realized volatility); GARCH forecasts gave no improvement | not tested by the author after 2010 |
| MNQ VVG classifier (big gap + big first 30 min + volume), 2021-25 | n/a | reversal OOS net +13.49 pts (T 1.26, 35 trades); best variant T 1.46, net +7.80 pts, 127 trades | yes (expanding window) | No: "No fixed directional rule survives across all three test years" (arXiv 2605.04004 s4.6); 2605.11423 abstract: "Eight directional configurations were tested. None passed." |
| MNQ gap fill fade, 2021-25 | n/a | net -1.92 / -1.05 / -1.43 pts at 09:30 / 09:45 / 10:00 ET entries | yes | FAIL (Table 6) |
| MNQ gap continuation short (Kalman velocity z > 2.5), 2021-25 | n/a | gross +16.53 pts, net +14.52, T 1.46, 35 OOS trades; 2024 -11.87 | yes | FAIL on year stability and per-fold count |
| MNQ event-day trend (993 ForexFactory high-impact events 2022-25) | n/a | "From bar +6 onward, T-statistics on net returns range from 0.14 to 0.69 across all horizons" | yes | FAIL ("No persistent post-news drift materializes once the initial spike bars are excluded") |
| Index-futures opening-move reversal (Grant, Wolf, Yu, JBF 2005; 1987-2002) | n/a | large opening moves reverse intraday | yes | "the significance of intraday price reversals is sharply reduced when gross trading results are adjusted by a bid-ask proxy for transactions costs" (abstract, Montclair Pure page; [secondary-only]: full text paywalled) |
| Beat the Market (Zarattini, Aziz, Barbon 2024; R10 owns) | Sharpe about 1.5 at VIX > 6 (all days) | Sharpe about 3.5 at VIX > 40 (in-sample bar chart); short trades: "no significant relationship between VIX and short trade profitability" (p 0.91), "limiting short trades to high volatility environments does not benefit overall compounded performance" | yes (VIX at open) | in-sample only; no per-trade figure by VIX bucket in text |

Other nulls:
- VIX term structure (VIX/VIX3M), VIX9D, VIX1D as filters for intraday ES/NQ direction: no study found
  in two WebSearch queries and two Firecrawl paper-index queries. Only practitioner explainers came
  up (pointers). This is a gap in what was found, not evidence that nothing exists. OpenAlex and S2
  were unavailable (section 9).
- Day-of-week filters: no new intraday ES/NQ source with a per-trade size was read. The program
  already tested A-H3 (weekend effect) and Gate 0 g12_dow.
- 3FPS post-2021: no out-of-sample or post-publication test found. The effect was publicised by
  Bloomberg in Sept 2023 (press coverage in search results, pointer). That is a known decay risk.

## 5. Data and cost

| candidate | needs | owned (brief s4) | price / terms |
|---|---|---|---|
| R12-C1, C2 | 1-min MES/MNQ/MYM bars; a monthly a.m.-settlement calendar (3rd Friday; when that Friday is an exchange holiday the SOQ moves to the Thursday, as on 2025-04-17) | yes; the calendar can be computed. The holiday rule must be checked against Cboe pages ([unverified] here) | none |
| R12-C3 | 1-min bars (first-30-min realized volatility, first-30-min return) | yes | none |
| R12-C4 | 1-min bars + FOMC calendar | yes (owned release calendars) | none |
| R12-C5, C6 | 1-min bars aggregated to 5/15 min; volume | yes (OHLCV volume) | none; replication needs the GMM details in Appendix A (some are under-specified: "Two-step heuristic based on vol_zscore and directional consistency") |
| Overnight BtD (non-survivor) | signed volume 15:15-16:15 ET (trade side) | no (OHLCV only) | Databento trades data is not owned; no price quoted here (R4 owns databento.com pricing) |
| VIX filters | Cboe VIX/VXN daily (owned); VIX3M, VIX9D, VIX1D daily CSVs | VIX and VXN yes; the others no | Cboe terms: R2's terms_log line for www.cboe.com (https://www.cboe.com/terms, 2026-10-18T08:39:20Z, "allowed for named pages one at a time"); not re-read by R12. that line quotes 'download one copy of the Materials for your personal non-commercial use', so whether a funded prop account counts as commercial use is a question for the lead (E.13 read the same limit for the Cboe daily CSVs, I-42/I-45) |

## 6. Prop compatibility

- R12-C1 (3rd-Friday intraday short): entry 08:30 CT, exit 11:00 CT or 15:00 CT. Inside the Topstep
  trading day and flat before 15:10 CT. One trade a month. It is not a scheduled major release, so P06
  does not bind (unless CPI or another release falls on that Friday; check per date). Automation is
  allowed (API); not HFT.
- R12-C2 (overnight leg): the published leg starts at the Thursday RTH close (about 15:00-15:15 CT).
  Topstep forces flat at 15:10 CT, and the new trading day starts at 17:00 CT. Only the 17:00 CT to
  08:30 CT part is tradeable, and its share of the +14.30 bp is not stated in the text (Figure 1 only).
  It is an overnight hold within one Topstep trading day, so it is allowed. The DLL is exposed to
  overnight gaps.
- R12-C3/C4: entry 14:30 CT, flat 15:00 CT. Allowed. On FOMC days the entry is 90 min after the
  13:00 CT release, so the position is not taken "into" the release (P06).
- R12-C5: 02:00-07:30 CT, inside the trading day. Unattended automation runs at night. The paper's
  idealized stop fills overstate the edge; a live 20-pt stop on MNQ fills worse in the London session.
- R12-C6: RTH. Allowed.

## 7. Overlap with tested mechanisms

- R12-C1/C2 vs E-H3 (quarterly witching short 14:30-15:00 CT, C5, FAIL): different window (open to
  noon, and overnight) and different calendar (monthly a.m. settlement). The paper's own null for the
  p.m. window agrees with the E-H3 FAIL. vs K7-expiry-01 (MBT expiry): unrelated. R1/R2 (0DTE and
  dealer charm) may also report this paper; the lead should dedup.
- R12-C3 vs K1-cp1 (morning sign to last half hour, MNQ/M2K/MYM, Tier B) and E20H6 T1/T2: same base
  signal. The difference is the conditioning on first-30-min realized volatility (T2 conditioned on
  move size, |r_ROD| above its trailing median). Gate 0 had cp1_ret and g06_rv60/g09_vol_state only as
  separate linear terms, not as an interaction. K1-vxnband-01 is a VXN-banded fade, not a momentum
  filter. D-H1/RT6 (trailing EWMA-vol gate) is a different base signal.
- R12-C4 vs K9-anncday-01 (draft), E-H1, E-H2, Gate 0 k2_fomc_mto: announcement-day effects were
  tested as drift or post-release momentum, not as first-30-min momentum on FOMC days.
- R12-C5 vs A-H1 (european-open drift): same session, different trigger (a regime transition, not
  the clock).
- R12-C6 vs C-H1..C-H4, D-H1..D-H3: a multi-feature regime gate plus a pullback entry; not tested.

## 8. Re-dig section

R12 is a first-wave reader, not a re-dig reader. Verdict checks that the reading bears on are below
(also in the JSON):
- A-H1 FAIL (european-open overnight drift, D.1): SUPPORTS. "Five additional years of data later, that
  pattern appears to have faded: the 2:00–3:00 window that previously generated roughly 3.7 percent per
  annum has averaged close to zero since 2021" (Liberty Street, 2026-07-01).
- E20H6 T1-T3 FAIL and K1-cp1 Tier B: SUPPORTS. Mesfin (2026): "Eleven signal families fail because
  their maximum gross return before friction is 0.07 to 1.50 points per trade, below the 2.0-point MNQ
  friction floor." Rosa 2022 (abstract, via E.20 notes): "The predictability disappears in the
  out‐of‐sample period."
- D-H1/RT6 and Gate 0 g09_vol_state (vol-regime gates) FAIL: SUPPORTS, weakly. Lundström: GARCH
  state forecasts gave no improvement ("without improving the results in any significant way").
- E-H3 FAIL (quarterly witching last half hour): SUPPORTS. "Around the p.m. settlement window there is
  no corresponding pattern".
- K1-cp2 family (opening-range breakout) Tier B: SUPPORTS. Mesfin ORB long at bar+15: "T = 0.88 on 447
  OOS trades, mean net +2.82 points" (FAIL).

## 9. Fetch log

| url | UTC | sha256 | saved path | status | tool |
|---|---|---|---|---|---|
| https://arxiv.org/pdf/2605.04004 | 2026-10-18T08:41:44Z | d0bd26e424a0c81bbca149e35566a3b9929a3cd207934e07638a99e78ca4ca80 | pages/R12/arxiv_2605.04004.pdf (+ .txt) | ok | curl (arXiv terms: terms_log.md arxiv.org line) |
| https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf | 2026-10-18T08:42:40Z | 403276b2ea8227c14ccfb854014af1df6a425430e5f622599640d7c0c16e683a | pages/R12/nyfed_sr917_overnight_drift.pdf (+ .txt) | ok | curl (NY Fed terms read in E.20, reports/stage_e20_briefs/pages/ZT/nyfed_terms.txt) |
| https://doi.org/10.59576/lse.20260701 -> https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/ | 2026-10-18T08:43:41Z | 3af27dbb6b8f3c97d3c4b3f86c3afdfd670263b1c6bca50f20a39f465549318e | pages/R12/lse_disappearing_overnight_drift.html (+ .txt) | ok | curl |
| https://swopec.hhs.se/umnees/abs/umnees0861.htm (also 0948, 0845) | 2026-10-18T08:45:55Z | not hashed (abstract pages) | pages/R12/swopec_umnees0861.htm, _0948.htm, _0845.htm | ok | curl |
| http://www.usbe.umu.se/digitalAssets/194/194520_ues861.pdf | 2026-10-18T08:46:23Z | 7c71f315bd897780eda0c35328eb1cb966974bc929df240b7fb85fd7d7bf631d | pages/R12/lundstrom_ues861.pdf (+ .txt) | ok | curl |
| https://arxiv.org/pdf/2605.11423 | 2026-10-18T08:48:54Z | 70501c60f354060a1ed23f209d82eb7a84482f4372620f0481e18afe894fbe6d | pages/R12/arxiv_2605.11423.pdf (+ .txt) | ok | curl (15 s after the previous arXiv request) |
| https://www.aeaweb.org/conference/2025/program/paper/N7rsBN2N (serves the PDF) | 2026-10-18T08:49:35Z | b98e7372007c43295265ac704ec260541d885653ef6ec415cb74258d8f29adb3 | pages/R12/aea2025_derivative_payoff_bias.pdf (+ dpb.txt) | ok | curl; WebFetch of the same URL confirmed it is a PDF (aeaweb terms: R1's terms_log line) |
| https://ideas.repec.org/a/eee/jbfina/v29y2005i5p1311-1327.html | 2026-10-18T08:51:06Z | 4c4118c061c35b42496c84158b2c478e8ca7f1eb97824cae31bbc2c6a34fe2f7 | pages/R12/ideas_grant_wolf_yu_2005.html | ok (no abstract on page) | curl |
| https://researchwith.montclair.edu/en/publications/intraday-price-reversals-in-the-us-stock-index-futures-market-a-1/ | 2026-10-18T08:51:12Z | a29bfae4484ae1d5038f0e01637374845534b5974cacf9f9c01b1c474a544095 | pages/R12/montclair_grant_wolf_yu_2005.html | ok (abstract only) | curl |
| api.openalex.org (search, works, cites) | 2026-10-18T08:39Z-08:44Z | n/a | scratch only | ok, then budget exhausted | curl |
| api.semanticscholar.org (3 attempts) | 08:44Z, 08:46Z, 08:51Z | n/a | n/a | throttled (429 x3) | curl |

Re-used E.20 copies (not refetched): reports/stage_e20_briefs/shared/gao_han_li_zhou_wp2015_mql5.pdf.txt,
reports/stage_e20_briefs/shared/zarattini_aziz_barbon_beat_the_market.pdf.txt,
reports/stage_e20_briefs/shared/rosa_2022_notes.md, reports/stage_e20_briefs/shared/li_sakkas_urquhart_2022_accepted.pdf.txt.

Terms lines appended to terms/terms_log.md: swopec.hhs.se, www.usbe.umu.se,
libertystreeteconomics.newyorkfed.org, researchwith.montclair.edu. Cited existing lines: arxiv.org,
www.aeaweb.org (R1), ideas.repec.org.

Budget notices (times PDT):
- 01:44 (08:44Z) OpenAlex: "Rate limit exceeded ... Insufficient budget. This request has no API key,
  so it counts against the free daily budget shared by everyone on your network's IP address, and that
  budget is used up". .env has no OpenAlex key (only OPENALEX_EMAIL). Forward-citation searches stopped
  there.
- 01:44, 01:46, 01:51 Semantic Scholar keyless: 429 each time; logged "throttled".
- 01:41 Firecrawl firecrawl_search: "Request failed with status code 429". 01:52 Firecrawl: 402, "The
  connected Firecrawl account is out of credits". Firecrawl paper-index search (research_search_papers)
  worked earlier, at 01:47-01:50.
- WebSearch: 8 calls used of 45; no over-budget notice.

## 10. Unfinished and unverified

- 3FPS: the Nasdaq-100 and Dow numbers were not extracted (the paper says the spike is "present" in
  them). The split of the +14.30 bp overnight leg before and after 17:00 CT is only in Figure 1, not
  in the text. No post-2021 test was found. The September 2024 AEA copy may not be the latest version.
- Gao FOMC-day t-statistic and the Table 8 per-event counts were not extracted. The figures come from
  the 2015 working paper, not the JFE 2018 version.
- Rosa (2022) threshold details: still [unverified] (paywalled; E.20 notes).
- Forward citations of Gao et al. and of Baltussen et al. 2024 (who re-tested, on what data): not
  done. OpenAlex budget was exhausted and S2 throttled. The lead may rerun after 00:00 UTC.
- Two titles found in OpenAlex but not read (SSRN only, blocked): Fetna (2026), "Opening-Range Breakout
  Does Not Survive Trading Costs: A Pre-Registered 225-Cell Study on Sixteen Years of Futures Data",
  doi 10.2139/ssrn.7428398 [unverified]; Delgado (2026), "'Beat the Market' Revisited: An Independent
  Replication and Statistical Audit", doi 10.2139/ssrn.7323419 [unverified] (R10's domain); Elms
  (2026), "From Pinning to Amplification: Evidence of a Regime Shift in S&P 500 Options Expiration
  Dynamics, 2016-2025", doi 10.2139/ssrn.6564078 [unverified] (bears on R12-C1 decay; R1/R2 may have
  it).
- Grant, Wolf, Yu (2005): abstract only [secondary-only].
- Cboe terms: R12 cites R2's line and did not re-read them.
