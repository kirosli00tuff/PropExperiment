# RD7 re-dig: trend and carry (E.13 trend/carry sources, E.21 test sources)

Reader: RedigReader-TrendCarry-OpusHigh (RD7), Stage E.25, research only. Started 2026-10-18 01:39 PDT,
written 01:39-01:56 PDT. No market data read, nothing tested, no purchase.

Sources re-dug, ranked by relevance to a prop-compatible intraday edge (method step 2):
1. Lou, Polk, Skouras, "A Tug of War: Overnight versus Intraday Expected Returns" (JFE 2019; read as the Feb 2018
   LSE version): the only study found that splits MOP time-series momentum into day and night (a forward citation
   of MOP 2012; new to the program).
2. Safari and Schmidhuber (2025, Physica A; arXiv 2501.16772): trend strength from 2 minutes to 1 day on 16 futures,
   2010-2023 (cited in E.20 as TN E3; read here for its trend content).
3. Kurth, Eisler, Rej, Bouchaud (arXiv 2607.01550, 2 Jul 2026): post-2008 decay of fast trend by tick size,
   about 100 futures 1995-2025 (a forward citation of MOP and HOP; new).
4. Hurst, Ooi, Pedersen (JPM Fall 2017) Exhibits 1 and 2 (E.13 T-03, E.21 spec_trend): re-read from the rendered page.
5. Baltas and Kosowski (2011 WP, E.10 copy): daily, weekly and monthly TSMOM by subperiod.
6. Babu, Levine, Ooi, Schroeder, Stamelos (JPM 2020; E.13 T-04): attribution of the 2010s weakness.
7. MOP 2012 (T-01), HLWZ 2020 (T-12), KMPV carry (T-10), Magdon-Ismail (T-31): E.13 quotes re-checked on the on-disk text.
8. Hutchinson, Kyziropoulos, O'Brien, O'Reilly, Sharma (IRFA 2022): out-of-sample replication of FX carry, TSMOM,
   momentum and value (a forward citation of MOP and KMPV; new).
9. Forward citations of MOP 2012 (Semantic Scholar, 1,000 of about 1,500 citing works; OpenAlex intraday/overnight
   subsets): Xu et al. (2025) cross-market overnight TSMOM; two 2026 MDPI papers (overlapping-returns bias;
   commodity ETF day/night ML).

## 1. Answer (at most 250 words)

The deeper reading supports every earlier trend and carry verdict. It adds one direct reason why trend cannot be
made prop-compatible by holding it only intraday.

- Lou-Polk-Skouras split MOP's TSMOM on 22 equity-index futures (1996-2016) into night and day. The CAPM alpha is
  1.40% a month overnight (t 3.24) and -0.10% intraday (t -0.24). All of the intraday leg's negative skew sits there
  (-2.77). A flat-by-15:10 version of the trend book would drop the part that earns, at least on the equity roots.
- Fast trend decayed most after 2009:
  - HOP's own 1-month signal: gross Sharpe 0.06 for 2010-2016, against 0.70 for 2000-2009.
  - Kurth et al.: EWM-5-20 fell from 0.84 to 0.12. Slow trend held 0.40 ± 0.26.
  - Baltas-Kosowski's daily (1,1) rule fell from 2.63 (1978-94) to 0.37 (1995-2012, t 1.07).
  - Safari-Schmidhuber find hour-scale trends too weak to trade after costs.
- Kurth et al. find the decay only on small-tick contracts: equity indices, FX and the smaller-tick commodities.
  Large-tick contracts kept fast-trend Sharpe of 1.0-1.2 (gross; cost treatment not stated). This weakens
  E22-F1's equal weight on fast speeds for MNQ, M2K and M6E. It supports E22-F1's yield and grain micros.
- Carry: Hutchinson et al. replicate FX carry out of sample (Oct 2012-Apr 2020) at Sharpe -0.10, gross and net.
  This supports E.13's carry closure for FX. I found no new futures-wide carry replication.

Candidates: two. Neither is a sized intraday edge; no published gross per trade exists for either.

## 2. Candidate hypotheses

| id | hypothesis | instruments | window / hold | published effect | gross per trade (micro ticks) | grade | owned | overlap |
|---|---|---|---|---|---|---|---|---|
| RD7-C1 | Fast/medium EWMA trend (EWM-tau-4tau, tau 5-50 days) restricted to large-tick contracts (vol-normalised tick in the top half) | rates (ZT, ZF, ZN, TN, ZB, UB; micro yields), larger-tick grains/livestock (ZC, ZS, ZL, HE, LE); not equity index, not FX | daily settlement signal, multi-day hold (NOT Topstep-compatible) | LT-tier Sharpe "remain in the range 1.0-1.2" post-break vs about 1.4 pre-break; ST tier about 0 (cost treatment not stated) | not computable: the paper reports Sharpe only, no per-trade P&L | working-paper | yes (17 roots 2010-2024; research window) | E21-T1, E21-T2, E22-F1; V39 "no further trend variant on 2010-2024" |
| RD7-C2 | Cross-market overnight TSMOM: US last-half-hour return predicts the next day's first half-hour return of international equity markets | CME-listed Nikkei futures would be the only Topstep-eligible vehicle (eligibility unverified); the paper studies "international stock markets" | entry at the foreign open (Tokyo 09:00 JST = 19:00 CT in US summer), 30 min | sign and significance only; "remains profitable with the consideration of transaction costs"; no size in the abstract | unknown (full text embargoed to 2027-10-21) | peer-reviewed [secondary-only] | partial or no (no Nikkei root among the 17; research-window list not checked) | K8 cross-market; E.20 RTY E7 (Li-Sakkas-Urquhart); R13's topic |

Not proposed (non-survivors):
- Trend held day-session only (flat by 15:10). Lou-Polk-Skouras's intraday leg is -0.29% a month raw (t -0.78) on
  equity-index futures. No day/night split was found for rates or commodity trend; that is a gap, not a null.
- Hour-scale intraday trend (Safari-Schmidhuber 2025). The regression R^2 is 0.012 to 0.027 bp, and the authors
  write that the patterns are "difficult to profitably exploit ... in the face of trading costs".
- Daily (1,1) TSMOM, i.e. yesterday's sign held one day (Baltas-Kosowski). It decayed to Sharpe 0.37 (t 1.07) by
  1995-2012.

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| TSMOM on equity-index futures earns only overnight | overnight CAPM alpha 1.40%/month (t 3.24); intraday -0.10% (t -0.24) | "the monthly overnight CAPM alpha associated with time-series momentum is 1.40% with a t-statistic of 3.24. The corresponding intraday alpha is negative, economically negligible, and statistically indistinguishable from zero." | Sec. on momentum strategies, text lines 627-630 of the .txt | Lou, Polk, Skouras, A Tug of War (Feb 2018 version of JFE 134 (2019)), https://personal.lse.ac.uk/loud/ATugofWar.pdf | working-paper (version of peer-reviewed) | pages/RD7/lps_tug_of_war.pdf |
| Same, raw returns and skew | close-to-close 0.81% (t 1.39), overnight 1.10% (t 2.67), intraday -0.29% (t -0.78); skew -0.491 / 0.178 / -2.767 | Table III Panel A rows "Close-to-close 0.81% 1.29% 1.31% 1.50% 7.30% -0.491"; "Overnight 1.10% 1.40% 1.42% 1.54% 4.24% 0.178"; "Intraday -0.29% -0.10% -0.10% -0.04% 4.85% -2.767" | Table III | same | same | same |
| Sample and intraday definition | 22 equity-index futures, 1996-2016; S&P 500 mini from 1997-09-10 | "for the period 1996 to 2016, for 22 equity index futures"; "from the 30 minute VWAP centered on the 'open' (defined as the minute before noon with the largest number of trades ...)" | Table III note | same | same | same |
| Intraday trend 2010-2023 too weak to trade | R^2 0.012-0.027 bp at hour horizons | "it would be difficult to profitably exploit these weak patterns in the face of trading costs, beyond earning a fair risk premium" | Sec. 3.2; Table 12 | Safari, Schmidhuber (2025), Physica A, doi 10.1016/j.physa.2025.130796; arXiv 2501.16772v2 | peer-reviewed (arXiv full text) | pages/RD7/safari_schmidhuber_2025_passages.md |
| Daily trend coefficient decaying | b -> 0 between 2010 and 2030 | "estimates that b→0 somewhere between 2010 and 2030. This has a natural interpretation: so much money has flown into trend-following that it does not work as well any more" | end of Sec. 2 | same | same | same |
| Hour-scale trends exist but are small | weak trends persist from a few hours to days | "Time horizons from a few hours to several days: small trends tend to persist (b>0), while strong trends tend to revert (c<0). In this range, b and c are small." | Sec. 5 | same | same | same |
| Fast trend collapsed after 2008, slow survived | Sharpe tau=5: 0.84 -> 0.12; tau=50: 0.70 -> 0.40 (1995-2009 vs 2009-2025) | "post-2008 the ordering reverses, with the fastest signal collapsing to 0.12 and the slowest still delivering 0.40" | Sec. 3.2, Table 1 | Kurth, Eisler, Rej, Bouchaud (2026), arXiv 2607.01550v1 | working-paper | pages/RD7/kurth_eisler_rej_bouchaud_2026_passages.md |
| Decay only on small-tick contracts | LT tier 1.0-1.2 post-break; ST tier about 0 | "Post-break, ST Sharpes collapse to essentially zero (mildly negative for the fastest signals), while LT Sharpes remain in the range 1.0–1.2." | Sec. 5.2 | same | same | same |
| Asset classes | IDX and FXR gone; YLD and CMD intact | "Trend has effectively vanished for IDX and FXR, while YLD and CMD show no appreciable degradation." | Sec. 3.3 | same | same | same |
| Signal decay, not cost | flat even at zero lag without costs | "produces equally flat post-2008 returns, even without costs" | Sec. 4.1 | same | same | same |
| No intraday-localised trend flow effect | n/a | "The volume-clock decomposition therefore does not reveal an intra-day-localised effect that the daily aggregation had been underestimating." | App. C | same | same | same |
| HOP 2010-2016 by signal (gross Sharpe) | 1-month 0.06, 3-month 0.30, 12-month 0.73 (2000-09: 0.70, 0.67, 1.10) | Exhibit 2 row "Jan 2010–Dec 2016 0.06 0.13 0.30 0.33 0.73 0.70"; note: "annualized gross Sharpe ratio (i.e., excess return before simulated transaction costs and fees divided by volatility)" | JPM Fall 2017 p.5 Exhibit 2 (image; read from rendered page) | Hurst, Ooi, Pedersen (2017), https://fairmodel.econ.yale.edu/ec439/hurst.pdf (E.13 copy) | peer-reviewed | ../stage_e13_briefs/pages/TrendCarry/hop_century_jpm.pdf |
| HOP 2010-2016 blend, net | 7.6% gross, 6.2% net of cost, 3.3% net of 2/20, vol 8.1%, Sharpe 0.41 | Exhibit 1 row "Jan 2010–Dec 2016 7.6% 6.2% 3.3% 8.1% 0.41 -0.15 0.28" | p.4 Exhibit 1 (image) | same | peer-reviewed | same |
| Daily TSMOM decayed after 1994 | (1,1): Sharpe 2.63 (t 11.91) -> 0.37 (t 1.07) | "the t-statistic drops dramatically to the insignificant value of 1.07 and the Sharpe ratio to the unattractive value of 0.37" | p.12 (text line ~617) | Baltas, Kosowski (2011 WP, first version Dec 10, 2011) | working-paper | ../stage_e10_research/overnight/baltas_kosowski_momf.txt |
| AQR attributes the 2010s weakness to small moves | n/a | "the primary explanatory factor is (1), namely, that the average size of global market moves has been more muted than usual" | abstract | Babu et al. (2020) JPM (E.13 T-04) | peer-reviewed | ../stage_e13_briefs/pages/TrendCarry/aqr_cant_always_trend_jpm.txt |
| FX carry / TSMOM out of sample | carry OOS Sharpe -0.10 gross and net (Oct 2012-Apr 2020); FX TSMOM OOS -0.16 gross, -0.18 net (2010-Apr 2020); in-sample 0.47 / 0.45 | Table 2 Panel C "Sharpe ratio − 0.10 − 0.68** − 0.16 0.30 − 0.10 − 0.77** − 0.18 0.28"; abstract: "the average out-of-sample Sharpe ratio decreases from +0.39 to − 0.32" | Table 2; abstract | Hutchinson et al., IRFA 83 (2022) 102245 | peer-reviewed | pages/RD7/hutchinson_etal_2022_fx_cmv.pdf |
| Overlapping returns inflate measured TSMOM | n/a | "the widespread use of overlapping returns in time series momentum (TSM) research, which can materially overstate the strength of TSM signals" | abstract | "How Overlapping Returns Inflate Measured Time Series Momentum", JRFM 19(1) 46 (2026) | peer-reviewed (MDPI) | pages/RD7/mdpi_overlapping_tsmom_2026.md |
| Cross-market overnight TSMOM | sign only | "the US stock market's last half-hour return predicts the next day's first half-hour stock returns in international markets"; "The COTSM strategy remains profitable with the consideration of transaction costs" | Griffith repository abstract | Xu, Li, Singh, Chen, Li, JIFMIM 105 (2025) 102239 | peer-reviewed [secondary-only] | pages/RD7/griffith_cotsm_item.html |
| E.13 quotes re-checked | match | "a Sharpe ratio greater than one on an annual basis, or"; "level, 47 of the 55 assets have a t-statistic of less than 1.65,"; "remarkable Sharpe ratio of 1.10 per annum."; "logarithmic (µ > 0), square root (µ = 0), or linear (µ < 0)." | mop2012.txt l.175; hlwz_w717.txt l.106; kmpv_carry_nber.txt l.1010; magdon_ismail_mdd.txt l.31 | E.13 T-01, T-12, T-10, T-31 | as E.13 | ../stage_e13_briefs/pages/TrendCarry/ |
| MOP deducts no costs | n/a | grep of mop2012.txt for "transaction cost" finds only a literature citation (l.133) and a reference title (l.1659) | full text | MOP 2012 | peer-reviewed | same |

Conversion note: none of these sources gives a per-trade gross in points, so no tick conversion is possible. The
Lou-Polk-Skouras monthly figures are portfolio returns of a vol-scaled long/short book across 22 indices, not
per-trade P&L on one contract.

## 4. Negative evidence

- Trend held intraday only: LPS Table III. The intraday leg's raw return is -0.29% a month (t -0.78), with skew
  -2.767. ("all of this strategy's negative return skewness comes from its intraday component").
- Fast trend after 2009:
  - HOP 1-month signal gross Sharpe 0.06 (2010-2016).
  - Kurth EWM-5-20 Sharpe 0.12 ± 0.24 (2009-2025). The rolling Sharpe "collapses from a historical range of 1–2.5
    to a level statistically indistinguishable from zero post-2010".
  - Baltas-Kosowski daily (1,1) Sharpe 0.37 (t 1.07) for 1995-2012.
- Hour-scale trends: Safari-Schmidhuber find reversion below about 30 minutes. Above that, trends are weak and
  "difficult to profitably exploit ... in the face of trading costs".
- FX: Hutchinson et al. report out-of-sample FX carry Sharpe -0.10, FX TSMOM -0.16 and FX cross-sectional momentum
  -0.68 (t -2.20), all gross. Kurth: FX trend "effectively vanished".
- Equity-index trend: Kurth reports the IDX sector "effectively vanished" for fast signals. LPS shows its profits
  are overnight only.
- Disagreement in the literature. Babu et al. (AQR 2020) say trend "continued to profit from market moves". Kurth et
  al. (CFM 2026) say "the signal itself has degraded" for fast trend on small-tick contracts. Both may hold: AQR's
  1/3/12-month blend is dominated by slow signals, which Kurth also finds intact (tau = 50: 0.40).
- ML trend overlays: forward citers such as DeePM (arXiv 2601.05975, abstract only) claim net gains of about twice
  classical trend, 2010-2025. That is an abstract claim, not read in full; see verdict check 8.
- Forward citations, 2022-2026: no direct re-test of the HLWZ critique was found. "Endogeneity and moments in time
  series momentum's predictability test" (Annals of Applied Statistics, 2025) was listed by Semantic Scholar and not
  read. The 2026 overlapping-returns paper adds a measurement critique (cash S&P 500 and ASX 200 only).

## 5. Data and cost

- RD7-C1 needs daily settlement or close prices for rates, grain and livestock roots, plus tick sizes.
  - Owned: 1-minute bars for ZT, ZF, ZN, TN, ZB, UB, ZC, ZS, ZL, HE, LE (2010-07..2024-02), and the research
    window. No purchase needed.
  - The tick-to-vol tiering is computable from owned bars and the published tick sizes.
  - Kurth et al. use daily settlement data for 101 contracts and proprietary CFM 5-minute bars (not needed for the
    trend P&L).
- RD7-C2 needs CME Nikkei futures 1-minute bars (none of the 17 roots) and US index futures last-half-hour returns
  (owned: NQ, RTY, MES).
  - No Databento price was looked up (no spend in this stage).
  - The paper's full text is embargoed until 2027-10-21.
- Terms on use: LSE allows personal download ("You may download information from the Website for your own personal
  use only"). MDPI articles are under CC BY. arXiv 2607.01550 is CC BY 4.0.

## 6. Prop compatibility

- RD7-C1: multi-day holds, so it is not Topstep-compatible (flat by 15:10 CT).
  - LPS gives no evidence that a day-only version keeps the premium; for equity-index futures it suggests the
    opposite.
  - It fits only the multi-day track: personal IBKR micro account, or a firm allowing overnight holds (V38/V39:
    PropEd cannot hold the book; R9 owns the current landscape).
  - Micro yield contracts (2YY, 10Y, 30Y), micro grains (MZC, MZS, MZL) and full-size rates fall in the large-tick
    group, as Kurth's sector result implies. Per-contract tiering was not published in the passages read.
- RD7-C2: a 30-minute hold at the Tokyo open (19:00 CT in US daylight time; 18:00 CT in standard time) sits inside
  Topstep's 17:00-15:10 CT trading day.
  - It is a single trade per day, not HFT, and needs no news exposure.
  - Whether Topstep lists a Nikkei contract is UNVERIFIED here.

## 7. Overlap with tested mechanisms

- RD7-C1 overlaps E21-T1 (TSMOM-12), E21-T2 (1/3/12 blend) and E22-F1 (Carver EWMAC 8/32..64/256, the same
  fast-minus-slow EWMA family).
  - It differs in two ways: it restricts the universe to large-tick contracts, and it reweights toward fast speeds
    there.
  - V39 says "no further trend variant on 2010-2024". Re-proposing it conflicts with that line, and the lead decides.
- RD7-C2 overlaps the K8 cross-market family (K8-flight-01, K8-wkndbtc-01) and E.20's RTY E7 (intraday TSMOM
  international, first half-hour to last half-hour).
  - This direction is the reverse: US close to the foreign open, overnight.
  - It overlaps R13's assignment (cross-market lead-lag), and R13 may hold more.

## 8. Verdict checks (re-dig readers)

| # | verdict | effect | quote | source |
|---|---|---|---|---|
| 1 | V39: trend "consistent with the published evidence, not established" | SUPPORTS | "post-2008 the ordering reverses, with the fastest signal collapsing to 0.12 and the slowest still delivering 0.40" (bootstrap SE about 0.26, so t < 2 over 16 years) | Kurth et al. 2026, Table 1 |
| 2 | E.21 T1-T4 FAIL on Holm (T1 0.50 net, T2 0.44 net) | SUPPORTS | HOP Exhibit 2, 2010-2016, 12-month gross Sharpe "0.73" and Exhibit 1 blend net "0.41"; Kurth tau=50 post-2008 "0.40 ± 0.26". E.21's figures sit inside this range, and a Sharpe near 0.4-0.5 over 14 years gives t about 1.5-1.9, short of Holm's first step | HOP 2017 p.4-5; Kurth 2026 |
| 3 | E.21 spec_trend: HOP 2010-2016 values "read from an exhibit image by eye; not checked by a second reader" | SUPPORTS (second read matches) | Exhibit 2 row "Jan 2010–Dec 2016 0.06 0.13 0.30 0.33 0.73 0.70"; Exhibit 1 row "Jan 2010–Dec 2016 7.6% 6.2% 3.3% 8.1% 0.41" | HOP 2017, rendered pp.4-5 |
| 4 | V38/V39: trend is not prop-compatible (PropEd cannot hold the trend book; Topstep flat by 15:10) | SUPPORTS | "time-series momentum occurs entirely overnight ... The corresponding intraday alpha is negative, economically negligible, and statistically indistinguishable from zero" | Lou, Polk, Skouras (2018/2019) |
| 5 | E.13 Part D drawdown arithmetic (10% ruin bound s_max = D/121.8, D/60.9, D/36.6) | SUPPORTS (re-derived) | Re-derivation: P = exp(-2 mu D / s^2) with mu = S s / sqrt(252) gives s_max = 2 S D / (ln 10 x sqrt(252)) = D x S / 18.28, i.e. D/121.8 (S 0.15), D/60.9 (0.30), D/36.6 (0.50). Matches E.13 lines 389-391. Magdon-Ismail quote matches its source (l.31) | own arithmetic; E.13 T-31 |
| 6 | E22-F1 design: equal weights on EWMAC 8/32, 16/64, 32/128, 64/256 across 12 micros incl. MNQ, M2K, M6E | WEAKENS (fast speeds on small-tick micros); SUPPORTS (yield and grain micros) | "Trend has effectively vanished for IDX and FXR, while YLD and CMD show no appreciable degradation."; "Post-break, ST Sharpes collapse to essentially zero ... while LT Sharpes remain in the range 1.0–1.2." | Kurth et al. 2026 Sec. 3.3, 5.2 |
| 7 | E.13 A2/A5: 2010s weakness attributed to "smaller market moves, not to lost trend efficacy" (Babu et al.) | WEAKENS for fast signals | "If capacity were the cause, removing execution costs should restore profitability, which it does not. This means the signal itself has degraded" | Kurth et al. 2026 Sec. 4.1 |
| 8 | V39: ML overlay on trend not built ("published gains vanish at 2-3 bp of cost") | WEAKENS (weak; abstract only) | "In large-scale backtests from 2010-2025 on 50 diversified futures with highly realistic transaction costs, DeePM attains net risk-adjusted returns that are roughly twice those of classical trend-following strategies" | arXiv 2601.05975 abstract [secondary-only]; full text not read |
| 9 | E.13 A4 carry closure (cross-sectional carry about zero since 2013) | SUPPORTS for FX; no new futures-wide evidence | "For CAR the in-sample period is November 1983 to September 2012"; Panel C carry "Sharpe ratio − 0.10" (gross) and "− 0.10" (net) | Hutchinson et al. 2022, Table 2 |
| 10 | V38: no published post-2015 intraday effect on the 17 roots clears 1.5 x D8 (trend at intraday horizons) | SUPPORTS | "Again, it would be difficult to profitably exploit these weak patterns in the face of trading costs, beyond earning a fair risk premium." | Safari, Schmidhuber 2025 Sec. 3.2 |
| 11 | E.13 A1 MOP "gross" label (no costs) | SUPPORTS | MOP text has no cost deduction; the only "transaction cost" hits are a literature citation and a reference title | mop2012.txt grep |

Mixed note on check 9: E.13's own AQR FX-carry column for 2013-2025 is +0.15. Hutchinson's out-of-sample FX
carry (2012-10..2020-04) is -0.10. They differ in window and construction; neither is significant.

## 9. Fetch log

| url | UTC | sha256 | saved path | status | tool |
|---|---|---|---|---|---|
| https://personal.lse.ac.uk/robots.txt | 2026-10-18T08:42Z | (404 page) | pages/RD7/lse_personal_robots.txt | ok (no robots file, 404) | curl |
| https://www.lse.ac.uk/lse-information/terms-of-use | 2026-10-18T08:42Z | 5c60834b653edef277ce51711ab1a9d84d2baec68f587cfc4e394e7d3e807e7a | terms/www.lse.ac.uk_terms.html | ok | curl |
| https://personal.lse.ac.uk/loud/ATugofWar.pdf | 2026-10-18T08:42:36Z | 013d4133e759d4cb65c6e2135917001ae26a67b7061860e141a61f2e6d3c306a | pages/RD7/lps_tug_of_war.pdf (.txt 88f7edb31b6b0e625a17d830f3314be5577663249b81faed93ff18c36b317737) | ok | curl + pdftotext |
| arxiv:2501.16772 (Firecrawl paper index) | 2026-10-18T08:42Z | 3ce553b8a1a6f61b3d3af1afc109e2517326408e96627fafcfe5624b04633a7b | pages/RD7/safari_schmidhuber_2025_passages.md | ok | firecrawl_research_read_paper |
| arxiv:2607.01550 (Firecrawl paper index, 3 reads) | 2026-10-18T08:43Z | 1fbe1aedb344e79379f5c8228283c767c5b0c2396ae5a5920b44e143c3f813b7 | pages/RD7/kurth_eisler_rej_bouchaud_2026_passages.md | ok | firecrawl_research_read_paper |
| api.openalex.org (works, cites: filters; 10 calls) | 2026-10-18T08:40-08:45Z | n/a | scratch only | ok, then rate-limited | curl |
| api.semanticscholar.org (KMPV citations, search) | 2026-10-18T08:46-08:47Z | n/a | n/a | throttled (429 x2; KMPV DOI "not found") | curl |
| api.semanticscholar.org (MOP citations, limit 1000) | 2026-10-18T08:50:53Z | n/a | scratch s2_mop.json | ok | curl |
| firecrawl_search (2 calls) | 2026-10-18T08:47:43Z | n/a | n/a | failed: out of credits | Firecrawl |
| https://research-repository.griffith.edu.au/robots.txt | 2026-10-18T08:48Z | afbc0f2f7fa9d12870378901b0871a9344fb514b648c22c799064948442298d7 | pages/RD7/griffith_robots.txt | ok | curl |
| https://www.griffith.edu.au/copyright | 2026-10-18T08:48Z | n/a | terms/www.griffith.edu.au_terms.html (403 body) | blocked (403) | curl |
| https://research-repository.griffith.edu.au/items/77d29c70-c6f9-426e-a28a-fca4c540dedd | 2026-10-18T08:48:24Z | 784cd68327c37a376a79c5a3748a8c0f2ccffd504118ae73e0921e4507e5fefd | pages/RD7/griffith_cotsm_item.html | ok (abstract; PDF embargoed) | curl |
| https://repository.adu.ac.ae/robots.txt | 2026-10-18T08:50Z | (see terms_log) | pages/RD7/adu_robots.txt | ok | curl |
| https://repository.adu.ac.ae/bitstreams/4912355c-88d1-434c-a489-e44e6ba6494b/download | 2026-10-18T08:50:32Z | 17bc83399eff9763a28cbf4f5b3075e19074ed531eaac000d46f429c533149d7 | pages/RD7/hutchinson_etal_2022_fx_cmv.pdf (.txt 76265bb8...) | ok | curl + pdftotext |
| https://www.mdpi.com/robots.txt | 2026-10-18T08:51Z | n/a | n/a | blocked (403) | curl |
| https://www.mdpi.com/about/terms-and-conditions | 2026-10-18T08:51Z | (see terms_log) | terms/www.mdpi.com_terms.md | ok (WebFetch 403; scrapling get ok) | scrapling get |
| https://www.mdpi.com/1911-8074/19/1/46 | 2026-10-18T08:51:49Z | c8ae2a49e0ab187c213e4805abdbf9f904a7beecd4106dc3e42070a24db846b4 | pages/RD7/mdpi_overlapping_tsmom_2026.md | ok (get returned empty; fetch ok) | scrapling fetch |
| https://www.mdpi.com/2813-2432/5/3/16 | 2026-10-18T08:52:10Z | 827d2df1a6361cba6a3e5c04f82b1ceb177997b6929164e329685be42851777c | pages/RD7/mdpi_commodity_etf_overnight_2026.md | ok | scrapling fetch |
| On-disk prior copies (no refetch) | n/a | baltas_kosowski_momf.txt 36807a56...; aqr_cant_always_trend_jpm.txt 3871dfd8...; mop2012.txt 6fdd9073...; hlwz_w717.txt 8d6934e6...; kmpv_carry_nber.txt 42fd4572...; magdon_ismail_mdd.txt 19c4aecf... | reports/stage_e10_research/overnight/, reports/stage_e13_briefs/pages/TrendCarry/ | read | grep, pdftoppm (HOP pp.4-5) |

Terms lines appended to terms/terms_log.md: www.lse.ac.uk, research-repository.griffith.edu.au (robots only; terms
page 403), repository.adu.ac.ae (robots only), www.mdpi.com. Memory checks before scrapling fetch: 2,512 MB and
2,865 MB available (both above 2,000).

WebSearch calls used: 10 of 45.

Budget notices:
- OpenAlex, 2026-10-18T08:45Z: "Rate limit exceeded ... Insufficient budget. This request has no API key, so it
  counts against the free daily budget shared by everyone on your network's IP address, and that budget is used up
  ($0 remaining; resets at midnight UTC)".
  - .env holds no OpenAlex key, only OPENALEX_EMAIL.
  - OpenAlex was used no further.
- Semantic Scholar, 08:46Z and 08:47Z: HTTP 429 twice with a 60 s backoff. It worked at 08:50:53Z.
- Firecrawl, 2026-10-18T08:47:43Z: "Insufficient credits to perform this request". No further Firecrawl calls were
  made. The three firecrawl_research_read_paper calls before it had succeeded.

## 10. Unfinished and unverified

- The forward-citation sweep of MOP is partial. Semantic Scholar returned 1,000 citing works (MOP has about 1,500 in
  OpenAlex). OpenAlex then hit its IP budget, and no KMPV, HOP or HLWZ citer lists were pulled.
- No futures-wide carry replication after 2013 was found. The E.13 AQR carry computation was not re-run: openpyxl
  is not installed and was not added.
- Kurth et al.: the cost treatment of the Sharpe tables is not stated in the passages read. Their per-contract tier
  membership (which CME roots fall in the large-tick half) was not published in those passages. Figures 10, 11 and 21
  are images and were not read.
- Lou-Polk-Skouras cover equity-index futures only. No day/night split of trend returns was found for rates,
  commodities or FX futures: a gap, not a null.
- Xu et al. (2025): abstract only; full text embargoed to 2027-10-21. No effect size.
- Unread forward citers: DeePM (arXiv 2601.05975), "Endogeneity and moments ..." (AoAS 2025) and "Speculators and
  time series momentum in commodity futures markets" (RFE 2025).
- Not cross-checked: SG Trend 2025-2026 figures from SG's own source (they are sold through LSEG).
- Data and code releases: AQR's TSMOM and Century-of-Factor-Premia files, already used by E.13 and E.21. Kurth et al.
  use proprietary CFM bars. No code release was found for any re-dug paper.
