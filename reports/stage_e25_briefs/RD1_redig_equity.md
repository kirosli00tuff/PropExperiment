# RD1 re-dig: equity-index intraday momentum sources (Stage E.25)

Reader: RedigReader-EquityIndex-OpusHigh (RD1). Started 2026-10-18 01:38 PDT; this file written 01:57-02:20 PDT.
Scope (spawn message): every source cited in reports/stage_e20_briefs/product_NQ.{json,md} and product_RTY.{json,md},
the equity notes in reports/stage_e20_briefs/shared/, and Baltussen, Da, Lammers, Martens (JFE 2021) intraday-momentum
results (its gamma table belongs to RD5). 0DTE papers (Adams et al. 2026: R1) and Zarattini/Concretum (R10) are cited,
not re-read. Verdicts checked: E20H6 T1-T3, the K1 cluster (E.7), the V38 closure.

Tool state (section 9): Firecrawl was out of credits at 08:43Z (all Firecrawl tools unavailable); the OpenAlex free
IP budget ran out at about 08:51Z (shared IP, no key in .env); Semantic Scholar keyless returned 429 three times. The
forward-citation sets for the four anchor papers had already been downloaded from OpenAlex before the budget ran out.

## 1. Answer (at most 250 words)

Source list ranked by relevance to a prop-compatible sized intraday edge: (1) Baltussen et al. 2021, (2) Gao, Han,
Li, Zhou 2018, (3) Mesfin arXiv 2605.04004 (MNQ 2021-2025), (4) Rosa 2022, (5) Li, Sakkas, Urquhart 2022, (6) Aalto
thesis 2025, (7) firmtape (pointer), (8) Lucca-Moench / Kurov et al. (pre-FOMC drift), (9) Barbon et al. LETF, (10)
Liu-Tse 2017, plus the authors' later work (Baltussen, Da, Soebhag 2025 "End-of-Day Reversal"; Baltussen,
Terstegge, Whelan "Derivative Payoff Bias"; Mesfin's two later MNQ preprints).

Forward citations (OpenAlex, 2026-10-18): Gao 2018 has 228 citing works, Baltussen 2021 94, Rosa 2022 7, Li-Sakkas-
Urquhart 36. No citing work found re-tests rest-of-day (ROD) or first-half-hour momentum on US index FUTURES after 2020
net of costs, other than Mesfin (MNQ, 5-min bars) and the Adams et al. draft (R1). Most replications are Chinese,
APAC, European or commodity markets; several are paywalled on hosts whose terms or blocks stopped retrieval.

Verdicts: the deeper reading SUPPORTS E20H6 T1-T3 FAIL (in-paper decay of the equity coefficient; the authors'
own cost caveat; Rosa's out-of-sample disappearance; Mesfin's 11 of 14 MNQ families grossing 0.07-1.50 NQ points).
It mildly WEAKENS H6 as a replica of the published rule (H6 exits 1-2 minutes early, inside the last ten minutes the
Aalto thesis says carry most of the effect), but not the FAIL. It SUPPORTS the K1 Tier B results and V38. Nothing
OVERTURNS a verdict. One sized pointer-grade candidate: Mesfin's London Session Signal B (gross about 6.09 NQ points =
24.4 MNQ ticks per trade, walk-forward OOS, single unreviewed author, GMM spec not fully reproducible).

## 2. Candidate hypotheses

| id | hypothesis | instruments | entry window CT | hold | published effect | gross per trade | grade | owned | overlap |
|---|---|---|---|---|---|---|---|---|---|
| RD1-C1 | London Session Signal B (Mesfin 2026): long MNQ after a "clean" GMM regime transition from "Bearish Chop" to "Bullish Drift" on 15-minute bars during 03:00-08:30 ET | MNQ (NQ path) | 02:00-07:30 CT (15-min bars) | 60 min or 07:30 CT (08:30 ET), whichever first; 20-point stop | walk-forward OOS net +4.09 NQ pts, sd 14.97, T 4.30, N 247 (OOS 2023-01..2025-08; data 2021-2025), at 2.0-point round-trip friction | gross = 4.09 + 2.0 = 6.09 NQ pts = 24.4 MNQ ticks (0.25-pt tick) | working-paper (arXiv preprint, single independent author, unreviewed; treat as pointer for design) | yes (1-min bars include the overnight session; 2019-05..2024-02 NQ path, research window MNQ) | A-H1 (European-open overnight drift, D.1) is the nearest tested window; different trigger (regime classifier, not time of day) |
| RD1-C2 (unsized, reported for completeness, not proposable under V31/V38) | ROD momentum confined to the last ten minutes of the cash session (Aalto thesis 2025 claim) | MNQ | 14:50 CT | 10 min to 15:00 CT | "most of the predictability in the return of the last half an hour stems from the last ten-minute period" (abstract only; no figures) | not published (abstract only; full text restricted) | thesis [secondary-only: abstract] | yes | E20H6-T1 (same signal, longer window); differs only in entry time |

Zero further candidates: every other re-read source is either already tested (E20H6, K1, D-H4, E-H1), needs data the
program does not own (high-frequency factor returns, option positions, stock-level data), needs an overnight hold
(Derivative Payoff Bias, Thursday close to third-Friday open), or is cross-sectional stocks (End-of-Day Reversal).
RD1-C1 carries heavy caveats (section 4 and section 3 row M3-M6).

## 3. Evidence table

All quotes are from full text saved on disk, with the location. "derived" = this reader's arithmetic.

| # | claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|---|
| B1 | Baltussen equity 1/N ROD strategy (re-checked against the E.20 reading: matches) | 6.86 %/yr, sd 3.96, SR 1.73, success 0.55; derived 2.72 bp/trade at /252 | "\| η(rROD) \| 6.86 \| 3.96 \| 1.73 \| 0.55 \|" | Table 6 Panel A, L1734-L1736 | Baltussen, Da, Lammers, Martens, JFE 142 (2021) 377-403, https://pure.eur.nl/files/58145484/1_s2.0_S0304405X21001598_main.pdf | peer-reviewed | reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md (sha256 18cb436e9d18cb3e...) |
| B2 | In-paper decay of the equity ROD coefficient (matches E.20) and of its middle-of-day component | equity beta_ROD x100 5.96 (t 4.80) in 1974-1999 vs 3.98 (t 6.65) in 2000-2020; beta_M 6.94 vs 2.42 | "\| Equity \| 3.73*** (2.74) \| 0.53 \| 3.81*** (2.70) \| 6.94*** (4.25) \| 9.46*** (4.35) \| 3.74 \| 5.96*** (4.80) \| 3.41 \|" and "\| Equity \| 4.97*** (6.06) \| 1.67 \| 4.83*** (6.02) \| 2.42*** (3.82) \| 8.89*** (4.11) \| 2.73 \| 3.98*** (6.65) \| 2.34 \|" | Table 5 Panels A and B, L1661 and L1666 | same | peer-reviewed | same |
| B3 | Authors' own cost statement | gross only; positive net Sharpe at a 1-tick cost for S&P futures, no number | "Note that we do not consider transaction costs. Given that trading on market intraday momentum requires frequent rebalancing, the strategy as presented might not be exploitable to many investors after accounting for transaction costs." ... "exploiting the effect in the S&P 500 futures yields a positive net Sharpe ratio when we assume transaction cost equal to a tick" | L1687-L1694 | same | peer-reviewed | same |
| B4 | Per-market rows, NQ, ES, ER, YM (ONFH beta, R2, R2_OOS ... ROD beta, R2, R2_OOS) | NQ ROD 6.36 (t 7.97), R2_OOS 3.76; ES ONFH R2_OOS -1.68; YM ROD 5.02 (t 4.12), R2_OOS 2.18 | "\| NQ \| 7.45*** (5.33) \| 2.01 \| 1.83*** \| ... \| 6.36*** (7.97) \| 4.10 \| 3.76*** \|"; "\| ES \| 5.24*** (3.38) \| 0.98 \| -1.68 \| ..."; "\| YM \| 6.07*** (3.28) \| 1.34 \| 1.31*** \| ... \| 5.02*** (4.12) \| 2.20 \| 2.18*** \|" | Table B1 Panel B, L3428-L3431 | same | peer-reviewed | same |
| D1 | Authors' later work: market-level last-half-hour autocovariance still positive in stocks 1993-2019 | autocovariance component +2.98 bp/day (CRSP stocks), cross-covariance -5.97 bp/day | "We find that the auto-covariance component is positive and significant (2.98 basis points per day) as expected based on the market intraday momentum pattern." | Sec. 4, txt L1086-L1088; sample "January 1993 to December 2019" (L473) | Baltussen, Da, Soebhag, "End-of-Day Reversal", WP April 2025 (SSRN 5039009), https://www3.nd.edu/~zda/EOD.pdf | working-paper | pages/RD1/baltussen_da_soebhag_EOD.pdf (+ .txt) |
| D2 | Same paper: stock-level reversal size and cost caveat (single stocks; not a futures strategy) | 3.78 bp/day VW L-S, 6.86 bp/day EW | "The effect is very sizable in gross terms with a 3.78 bps reversal per day, or about 9.5% a year, for the value-weighted L-S portfolio, and 6.86 bps per day, or 17.3% a year, for the equal-weighted L-S portfolio." | txt L772-L775 | same | working-paper | same |
| D3 | Same paper names a further Baltussen co-authored market-level effect around option expiries | none in this source | "Baltussen, Terstegge, and Whelan (2023) document strong overnight and intraday reversals at the market level around option expiries." | footnote 2, txt L477-L478 | same | working-paper (citing source); the cited paper itself [secondary-only: search summary, "The Derivative Payoff Bias", Thursday close to third-Friday open] | same |
| M1 | Mesfin MNQ 2021-2025: most OHLCV intraday families gross below friction | 11 of 14 families gross 0.07-1.50 NQ points (0.3-6.0 MNQ ticks) vs 2.0-point friction | "Eleven families fail because gross return before friction is 0.07-1.50 points, below the 2.0-point friction floor." | abstract; txt L23 | Mesfin, arXiv 2605.04004v3 (May 2026), https://arxiv.org/abs/2605.04004 | working-paper (unreviewed preprint, independent author) | reports/stage_e20_briefs/pages/NQ/arxiv_2605.04004.pdf (+ .txt), sha256 d0bd26e424a0c81b... |
| M2 | Opening range breakout and gap continuation on MNQ, near-misses | ORB long net +2.82 pts, T 0.88; gap continuation short gross +16.53, net +14.52, T 1.46, 35 OOS trades | "the Opening Range Breakout long at a 15-bar hold (net +2.82 points, T = 0.88 on net returns)"; "Gap continuation short is the most credible near-miss in the study. Gross +16.53 points, net +14.52, T = 1.46." | txt L24, L290 | same | working-paper | same |
| M3 | London Session Signal B, walk-forward OOS (candidate RD1-C1) | net +4.09 pts, sd 14.97, T 4.30, N 247, win 61.54 % | "Walk-forward OOS N 247" / "Walk-forward OOS mean net return +4.09 pts" / "Walk-forward OOS std deviation 14.97 pts" / "Walk-forward OOS T-statistic (net) 4.30" | Table 11, txt L470-L483 | same | working-paper | same |
| M4 | London B is fragile to one-bar delay | 15-min delay: T -2.78, net -2.91 pts | "A one-bar (15-minute) delay reverses T from +4.30 to -2.78; a two-bar delay produces T = -2.16." | txt L486-L487, Table 12 | same | working-paper | same |
| M5 | London B spec (session, entry, exit, stop, friction) | 03:00-08:30 ET, long next 15-min open, exit 60 min or 08:30 ET, 20-pt stop at exact price, 2.0-pt RT friction | "Session 03:00–08:30 ET, 15-minute bars." ... "Exit rule 60 minutes after entry or 08:30 ET, whichever first." ... "Stop 20 points fixed. Filled at exact stop price (idealized fill assumption)." | Table A2, txt L700-L725 | same | working-paper | same |
| M6 | RTH Confluence Signal (second positive control): larger but heavily searched | OOS net +11.82 pts, sd 53.8, T 3.11, N 196; "53+ combinations across 7 parameters" | "Walk-forward OOS mean net return +11.82 pts"; "First, 53 or more parameter combinations across seven parameters were evaluated before the final specification was locked" | Table 10 and txt L445-L449 | same | working-paper | same |
| M7 | Mesfin later work (author's own follow-ups, abstracts from the arXiv API) | VVG classifier: best T 1.46, "None passed"; LSTM/GBM: OOS accuracy 50.00-50.89 % vs 51.8 % base | "Eight directional configurations were tested. None passed."; "No configuration produces statistically significant out-of-sample accuracy above the 51.8% base rate." | arXiv 2605.11423v3 and 2605.17724v1 abstracts | Mesfin 2026, https://arxiv.org/abs/2605.11423, https://arxiv.org/abs/2605.17724 | working-paper [secondary-only: abstract] | pages/RD1/arxiv_api_mesfin.xml (sha256 0a2f725f78528f84...) |
| A1 | Aalto thesis (E.20 notes, not refetched): ROD momentum persists 2008-2024; concentrated in last ten minutes; mostly not feasible after costs | no figures | "We first show that the intraday momentum patterns still exist in our dataset spanning January 2008 to October 2024." ... "most of the predictability in the return of the last half an hour stems from the last ten-minute period" ... "most intraday momentum and reversal trading strategies may not be feasible after transactions costs, especially in bond and currency futures" | dc.description.abstract | Majorin, Aalto University master's thesis 2025, https://aaltodoc.aalto.fi/items/1011f043-edd1-4cb2-9694-b1216d77561f | thesis [secondary-only: abstract] | reports/stage_e20_briefs/shared/aalto_thesis_item_api.json |
| R1 | Rosa 2022: out-of-sample disappearance (abstract, re-confirmed; full text still unreachable) | none | "The predictability disappears in the out-of-sample period." ... "A strategy with thresholds delivers higher returns than a strategy that is always active." | abstract (IDEAS record) | Rosa, J. Futures Markets 42(12) (2022) 2218-2234, doi 10.1002/fut.22375 | peer-reviewed [secondary-only: abstract] | reports/stage_e20_briefs/shared/rosa_ideas.html |
| T1 | Two non-US thesis replications found through the citation graph (context only) | none extracted | title pages: "Intraday Momentum and Return Predictability / A High Frequency Analysis of the Swedish OMX30 ... Spring 2024"; "Intraday Momentum ... Klagenfurt, May 2021" (EURO STOXX 50 ETF 2019-2020: "intraday time-series momentum exists on the European stock") | title pages; aau abstract txt L131-L132 | Julin (Örebro 2024), Moser (Klagenfurt 2021) | thesis | pages/RD1/diva_1878991.pdf, pages/RD1/aau_7301728.pdf |

Forward-citation inventory (OpenAlex, saved pages/RD1/openalex/cites_*.json). Gao 2018 (W3123013550): 228 citing
works; Baltussen 2021 (W3106590193): 94; Rosa 2022 (W4294956096): 7; Li-Sakkas-Urquhart (W3121499907): 36. Citing
works most relevant to the verdicts, NOT read in full text (host blocked, paywalled, SSRN-only, or budget ran out):
Aleti, Bollerslev, Siggaard, Management Science 71(9) 2025 (intraday market return predictable from lagged
high-frequency factor returns; "after transaction costs" per a search summary [secondary-only]; needs factor-zoo
stock data, not owned); Iwanaga and Sakemoto, "Intraday Time Series Reversal" (SSRN 5807282, 2025) and NAJEF 2026
(overnight return predicts a first-half-hour REVERSAL in US index ETFs, "weakened after the 2010s" per a search
summary [secondary-only]; overlaps D-H4); Limkriangkrai, Chai, Zheng, PBFJ 2023 (APAC; Monash copy behind login);
Ho, Lv, Schultz, PBFJ 2021 (Australia; request-a-copy only); Huddleston, Liu, Stentoft, JFEc 2020 and Liu and Stentoft
2023 "Intraday Stock Predictability Everywhere" (SSRN only); Willeboordse, "Does gamma survive the close?", FRL 2026
(gamma: RD5); Zhang, Zhang, Pan, Li, IREF 2026 (macro announcements and intraday momentum; ScienceDirect);
Lai, Lin, Eom, Tsai, JRFM 2022 (KOSPI with trading-cost measures; MDPI blocked); Wu and Pinsky, JRFM 2026 (MDPI blocked);
Gava, McNeal, Turc, J. Investing 2021 "The Early Bird Catches the Intraday Trend" (no copy found); Hossain et al.,
E+M 2021 (S&P 500 and CSI300 incl. 2020; repository unreachable).

## 4. Negative evidence

- In-paper decay (B2): equity beta_ROD falls by a third from 1974-1999 to 2000-2020; the middle-of-day component
  (beta_M) falls from 6.94 to 2.42. ES's first-half-hour (ONFH) predictor has negative R2_OOS (-1.68, B4).
- Cost (B3): the authors concede the strategy "might not be exploitable to many investors after accounting for
  transaction costs"; the only net figure is a positive net Sharpe at a one-tick cost for S&P futures, unsized.
- Out of sample (R1): Rosa finds the overnight-return predictor's predictability "disappears in the out-of-sample
  period" (abstract; threshold details still [unverified]).
- MNQ 2021-2025 (M1, M2, M7): 11 of 14 OHLCV families gross 0.07-1.50 NQ points, under a 2.0-point friction; ORB long
  T 0.88; gap continuation short T 1.46 on 35 trades; the author's VVG classifier and ML follow-ups: "None passed" and
  no accuracy above base rate.
- Aalto (A1): momentum "still exist[s]" 2008-2024 but "may not be feasible after transactions costs" for most
  strategies (abstract; no numbers).
- RD1-C1's own caveats (M4-M6): sign flip under a 15-minute delay; idealized stop fills; the regime-mapping
  heuristic for London B is described but not fully specified ("Two-step heuristic based on vol_zscore and directional
  consistency"), so an exact replication is not assured; the companion RTH signal was chosen from 53+ combinations;
  single author, unreviewed, AI-assisted editing disclosed; nothing independent re-tests either control.
- Pointers only (not evidence): firmtape SPX 2022-2026 flat ROD slope (E.20 shared notes S4); a search summary that
  Alpha Architect's in-house backtest did not support Gao et al. (not fetched, [unverified]).

## 5. Data and cost

- RD1-C1: 1-minute OHLCV of NQ/MNQ including the overnight session (aggregated to 15-minute bars; volume z-scores);
  owned for NQ 2019-05..2024-02 and the research window 2025-04..2026-06 (brief section 4). No purchase. The paper
  used MNQ 5- and 15-minute bars 2021-2025 (overlapping the program's NQ path 2021-2024-02). Research window testable:
  yes (about 300 trade dates). Paper rate, derived: 247 OOS trades over the OOS periods 2023, 2024 and 2025
  January-August (Table 2: "3 ... 2022–2024 ... 2025 (partial, January–August)") = about 93 a year; not a program
  figure. Note an internal inconsistency in the paper: Table 2 puts the first OOS fold in 2023, while the RTH
  Confluence text says its W1 fold is "2022 H2".
- RD1-C2: same bars; no extra data.
- Not owned (for completeness): high-frequency factor returns (Aleti et al.), stock-level CRSP/TAQ (End-of-Day
  Reversal), option positions (Adams et al., Baltussen Table 7: RD5/R1).

## 6. Prop compatibility

- RD1-C1: entries 02:00-07:30 CT, inside the Topstep trading day (17:00-15:10 CT), flat by 07:30 CT, so flat before
  the 07:30 CT (08:30 ET) CPI/NFP/PPI/GDP releases: compatible with P06 by construction (exit "at 60 minutes or 08:30
  ET"). One position, 60-minute hold: not HFT. Automation via ProjectX, or semi-manual (15-minute bars, but the
  one-bar delay sensitivity M4 makes manual entry risky). 20-point NQ stop = $40 per MNQ contract: small against any
  DLL. Overnight-hours liquidity in MNQ is thinner than the day session; the program's D8 round trip is a day-session
  figure (brief section 2), so the lead may need an overnight cost bucket.
- RD1-C2: 14:50-15:00 CT, flat before 15:10 CT: compatible.

## 7. Overlap with tested mechanisms

- RD1-C1: A-H1 (European-open overnight drift, 02:00 ET window, D.1, MES) is the closest tested window; RD1-C1 differs
  by its trigger (regime-classifier transition, long only) and vehicle (MNQ). K1 members are all day-session.
- RD1-C2: E20H6-T1 (same r_ROD signal, 14:30-14:58 window). Differs only in entry time.
- Iwanaga-Sakemoto's overnight-to-first-half-hour reversal (not a candidate: unsized here) overlaps D-H4 (overnight
  gap fade, MES first 30 min).

## 8. Verdict checks (re-dig)

| verdict | effect | quote | source |
|---|---|---|---|
| E20H6-T1 (r004; FAIL, gross 1.25 ticks vs 4.08 RT) | SUPPORTS | "Given that trading on market intraday momentum requires frequent rebalancing, the strategy as presented might not be exploitable to many investors after accounting for transaction costs." | Baltussen et al. 2021, L1687-L1690 |
| E20H6-T1 | SUPPORTS | equity beta_ROD "5.96*** (4.80)" in 1974-1999 vs "3.98*** (6.65)" in 2000-2020 | Baltussen et al. 2021, Table 5, L1661/L1666 |
| E20H6-T1 | SUPPORTS | "Eleven families fail because gross return before friction is 0.07-1.50 points, below the 2.0-point friction floor." (MNQ 2021-2025; not a ROD test, but the same instrument, era and bar data) | Mesfin 2026, arXiv 2605.04004v3 abstract |
| E20H6-T1 (as a replica of the published rule) | WEAKENS (mildly; not the FAIL) | "most of the predictability in the return of the last half an hour stems from the last ten-minute period" (H6 exits at 14:58 bar, filling about 14:59 CT, so it drops 1-2 of those ten minutes; E.20 product_NQ.md 4b already flagged this). The thesis also says momentum "still exist[s]" through October 2024. At 1.25 gross ticks vs a 6.18-tick hurdle, a 1-2 minute extension cannot plausibly close the gap; the lead judges. | Aalto thesis 2025 abstract (E.20 shared notes) |
| E20H6-T2 (FAIL; trailing-median |r_ROD| threshold) | SUPPORTS (and confirms T2 is not Rosa's rule) | "This paper studies the out‐of‐sample performance of the intraday momentum strategy where the overnight return predicts the return of the last half‐hour of trading. The predictability disappears in the out‐of-sample period." Rosa's predictor is the overnight return; his threshold rule remains [unverified] (full text still closed: OpenAlex is_oa False; S2 openAccessPdf empty, 2026-10-18). | Rosa 2022 abstract |
| E20H6-T3 (FAIL; GEX < 0) | not assessed here (gamma: RD5, R1). Baltussen's gamma row is S&P-only; no citing work read here tests NQ. | - | - |
| K1-cp1-01 (E.7 Tier B; morning sign to last half hour) | SUPPORTS | ES row "\| ES \| 5.24*** (3.38) \| 0.98 \| -1.68 \|": the first-half-hour (overnight plus first 30 min) predictor has negative out-of-sample R2 on S&P futures; NQ's is 1.83 % against 3.76 % for ROD; Rosa: overnight predictor "disappears in the out-of-sample period" | Baltussen et al. 2021, Table B1 Panel B, L3429-L3430; Rosa 2022 |
| K1-cp2-01 (E.7 Tier B; opening-range breakout) | SUPPORTS | "the Opening Range Breakout long at a 15-bar hold (net +2.82 points, T = 0.88 on net returns)" fails year stability on MNQ 2021-2025 | Mesfin 2026, txt L24 |
| V38 (intraday program on Topstep closed: no published post-2015 intraday effect on the 17 roots exceeds 1.5 x D8) | SUPPORTS, with one exception to weigh | Peer-reviewed and thesis sources found nothing post-2015 on US index futures above the hurdle. The one exception is preprint-grade: "Walk-forward OOS mean net return +4.09 pts" (London Session Signal B, MNQ 2021-2025, net of 2.0 points = 8 MNQ ticks), i.e. gross 24.4 MNQ ticks, about 3.9 x the 6.18-tick MNQ hurdle in inputs (the lead computes the ratio). It is unreviewed, single-author and fragile (a 15-minute delay "reverses T from +4.30 to -2.78"), so it does not overturn V38; it is the one sized item the closure did not see (E.20 read the paper but recorded only its failures). | Mesfin 2026, Table 11, txt L470-L487 |
| V38 / E20H6 (era) | SUPPORTS (weak, context) | "We find that the auto-covariance component is positive and significant (2.98 basis points per day) as expected based on the market intraday momentum pattern." The authors' own later paper still finds market-level end-of-day continuation, but only through 2019 ("sample period runs from January 1993 to December 2019"), so it says nothing about 2020-2024. | Baltussen, Da, Soebhag 2025 WP, L1086-L1088, L473 |

## 9. Fetch log, terms, budget notices

| url | UTC | sha256 (first 16) | saved path | status | tool |
|---|---|---|---|---|---|
| https://api.openalex.org/works?filter=cites:W3123013550 (p1, p2; also W3106590193, W4294956096, W3121499907) | 2026-10-18T08:41Z | see files (e.g. 2e44d1bd1d15c0d6 for Gao p1) | pages/RD1/openalex/cites_*.json | ok | curl (OpenAlex polite pool) |
| https://api.openalex.org/works/{13 ids}?select=locations | 08:42Z | - | scratch only | ok | curl |
| https://api.openalex.org/works?search=... (2 lookups) | 08:51Z | - | - | throttled (IP daily budget used up) | curl |
| https://api.semanticscholar.org/graph/v1/paper/DOI:10.1002/fut.22375 and DOI:10.1016/j.iref.2017.01.005 | 08:50Z | - | scratch only | ok (no OA PDF for Rosa; Liu-Tse only SSRN) | curl keyless |
| https://api.semanticscholar.org/graph/v1/paper/batch (22 DOIs) | 08:51-08:53Z | - | - | throttled (429 x3) | curl keyless |
| https://www3.nd.edu/~zda/EOD.pdf (redirect academicweb.nd.edu) | 08:44:57Z | faa9de99da6579a9 | pages/RD1/baltussen_da_soebhag_EOD.pdf (+ .txt) | ok | curl |
| https://www.diva-portal.org/smash/get/diva2:1878991/FULLTEXT01.pdf | 08:46:34Z | 5428468ae82dd7cf | pages/RD1/diva_1878991.pdf (+ .txt) | ok | curl |
| https://netlibrary.aau.at/obvuklhs/download/pdf/7301728 | 08:46:47Z | 61e66b66b7785b9f | pages/RD1/aau_7301728.pdf (+ .txt) | ok | curl |
| https://assets.super.so/e46b77e7-.../ee7dac49-....pdf (Gao et al. JFE author copy) | 08:46-08:47Z | - | - | blocked (403 curl, WebFetch; scrapling get: S3 AccessDenied) | curl / WebFetch / scrapling |
| https://hull-repository.worktribe.com/OutputFile/3016448 | 08:52Z | - | robots page only | blocked (Cloudflare challenge; WebFetch 403); not pursued (terms unknown) | curl / WebFetch |
| https://www.mdpi.com/robots.txt, /about/terms-and-conditions | 08:48Z | - | - | blocked (403) | curl / WebFetch |
| https://researchmgt.monash.edu (APAC paper) | 08:48Z | - | - | blocked (login redirect) | curl |
| https://dspace5old.zcu.cz/ (Hossain et al. 2021) | 08:54Z | - | - | unreachable (curl 000) | curl |
| https://export.arxiv.org/api/query (2 queries, 16 s apart) | 08:49:51Z | 0a2f725f78528f84 | pages/RD1/arxiv_api_mesfin.xml | ok | curl |
| https://scholars.duke.edu/publication/1585816 | 08:45Z | - | - | ok (no PDF, no abstract) | WebFetch |
| robots.txt: www3.nd.edu (404 after redirect), www.diva-portal.org, netlibrary.aau.at, assets.super.so (403), hull-repository (challenge), www.mdpi.com (403), researchmgt.monash.edu (login) | 08:44-08:48Z | see pages/RD1/*_robots.txt | pages/RD1/ | as noted | curl |

Terms: appended to terms/terms_log.md for www3.nd.edu (www.nd.edu/copyright saved as terms/www.nd.edu_terms.html,
no automated-access clause; allowed for named pages one at a time), www.diva-portal.org and netlibrary.aau.at
(terms pages not located, robots only; allowed for named pages one at a time). arxiv.org: cited R-line already in
terms_log (Crawl-delay 15 observed). Reused E.20/E.13 copies on disk for Baltussen, Mesfin, Aalto, Rosa, Li-Sakkas-
Urquhart, Lucca-Moench, Barbon et al. (not refetched).

Budget notices: 08:43:44Z (01:43 PDT) Firecrawl "Insufficient credits to perform this request" (3 search calls; no
Firecrawl tool used afterwards). 08:51Z (01:51 PDT) OpenAlex "Rate limit exceeded ... Insufficient budget. This
request has no API key ... free daily budget shared by everyone on your network's IP address ... used up". 08:51-08:53Z
Semantic Scholar keyless 429 x3. WebSearch calls used: 11 of 45. A PostToolUse cost notice (informational) appeared
at about 01:55 PDT; it was not a reason to stop.

## 10. Unfinished and unverified

- Rosa (2022) full text: still not retrieved (Wiley terms forbid automation; no OA copy per OpenAlex and S2). The
  threshold variable, value and sample remain [unverified].
- Gao et al. JFE published version: author copy 403; numbers stay as read from the Dec 2015 WP by E.20.
- Liu and Tse (2017): only an SSRN copy exists (SSRN blocks automation): still [unverified].
- Kurov, Wolfe, Gilbert (2021) full text and the post-2015 pre-FOMC drift forward literature: not re-dug (OpenAlex
  budget gone before the Lucca-Moench citer list was pulled).
- Barbon et al. later versions (published form of the LETF paper): not re-dug (budget).
- The citing works listed at the end of section 3 were identified but not read in full text (blocked, paywalled,
  SSRN-only); Aleti et al. (Management Science 2025) and Iwanaga-Sakemoto (2025/2026) are the two most relevant.
- The Aalto thesis full text is still restricted; RD1-C2 has no published size.
- Data or code releases: none found for Baltussen 2021, Gao 2018 or Mesfin (Mesfin gives Appendix A specifications
  only; no code link in the paper).
