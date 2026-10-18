# R13 cross-market intraday lead-lag (Stage E.25, research only)

Reader: R13-LeadLag-OpusHigh. Started 2026-10-18 01:38 PDT, written 01:55-02:10 PDT. Brief:
reports/stage_e25_briefs/brief_shared.md (read whole). No market data opened, nothing tested.

## 1. Answer (at most 250 words)

What the program has already tested in this direction (from r0_mechanism_index.md, K8.md and
ml_route_v2/signals/generic.py): K8-flight-01 (MES tail move to long MGC, H30 and HEOD), K8-oilcad-01
(MCL 5-min shock to 6C), K8-wkndbtc-01 (MBT weekend move to MNQ; bitcoin closed); E.22 cluster
statement "K8 NULL". Gate 0 (E.12) tested the g17 lead features (60-minute log return of the NQ, ZN,
6E, CL, GC, ZC and MBT lead paths, plus MES where covered) at three decision times per product and
h60/h120/hF: FAIL, no Holm rejection. E.20's ML search kept g17_nq/zn/6e/cl/gc/zc among its 34
features (inferred from backward_swap_table.md row 59): FAIL. Also E16-H2 (NQ vs ZN month-end),
K3-mehedge-01 (Nikkei to 6J), K6-crushgap-01, A-H1 (European-open drift on MES): all failed.

What the literature says about the untested pairs: every cross-market lead with a measured horizon
lives at milliseconds to a few seconds (CAC/SMI futures: correlation under 5% by 30 s; E-mini leads
cash 10-year Treasuries by 5 ms, not the reverse; Chicago-to-New Jersey 4 to 8 ms), and the papers
that cost it find the lead is lost to the spread (Huth-Abergel: +0.4 bp at mid, -2.73 bp after the
spread) or unprofitable after costs (VIX futures to SPX futures). At 1-minute and longer horizons I
found no published dollar-to-gold, crude-to-CAD, crude-to-energy-equity or Treasury-to-equity effect
with a tradeable size. A 2016-2018 one-minute study finds no persistent dollar-index-to-gold or
WTI-to-CAD link. The one sized minutes-to-hours candidate (European-open "overnight drift", conditional
on a US-close sell-off) is re-used from E.10 and its own authors report it faded after 2021.
Candidates proposed: one, weak (R13-C1), flagged with decay.

## 2. Candidate hypotheses

| id | hypothesis | instruments | entry CT / hold | published effect | gross per trade (micro ticks) | grade | decay | owned data | overlap |
|---|---|---|---|---|---|---|---|---|---|
| R13-C1 | "Buy the dip" overnight drift: after a US close with net selling (closing relative signed volume RSV < 0, 15:15-16:15 ET), go long equity index futures 01:30-03:30 ET, when European (and earlier Tokyo) participants arrive and dealers offload inventory | MES (paper: ES); NQ and YM showed the same unconditional pattern | 00:30 CT, hold 120 min, flat 02:30 CT | Table IX: BtD mean 6.07% annualized before costs, 4.04% after bid-ask, Sharpe 1.78 / 1.10, 2004-2020, holds on about 50% of days | about 4.8 bp per trade (derivation in section 5); at ES 6,000 = 2.9 ES points = 11.6 MES ticks; at NQ 21,000 = 10.1 NQ points = 40 MNQ ticks (NQ size not published for BtD) | working-paper (FRBNY SR 917, rev. 2022); published RFS 36(9) 2023 (citation from a fetched reference list) | STRONG: the authors' own 2026 update says the 02:00-03:00 window "has averaged close to zero since 2021" and the imbalance-return spread is "much narrower" (chart title: "The Order-Imbalance-Overnight-Return Relationship Has Broken Down") | partial: MES 1-min bars owned; RSV needs aggressor-signed volume (trades data), not owned | A-H1 (unconditional, MES, D.1 fail); E.10 K9O-001/002 (same source, already read) |

Why only one, and why it is weak: R13-C1 is the only sized cross-session effect at minutes-to-hours
that touches the "Asian or European to US" pair, and it is not new to the program (E.10 read it and its
decay note). Its conditioning variable is not in the owned data, and the post-publication sample
(2021-2025) overlaps the research window and shows decay. I list it so the lead can rule on it, not as
a recommendation. No candidate is proposed for Treasury-to-equity, dollar-to-gold, crude-to-CAD or
crude-to-energy-equity: no source with a tradeable minute-level size was found (section 4).

## 3. Evidence table

| # | claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|---|
| E1 | Cross-country index futures lead-lag dies within seconds | max correlation at 0.2 s; under 5% by 30 s | "For the FCE/FSMI pair (future vs future), the cross-correlation vanishes very quickly, there is less than 5% of correlation at 30 seconds. We observe that there is more correlation on the side where FCE leads with a LLR of 1.26 and a maximum correlation at 0.2 seconds." | section 3.1, p. 8 (txt lines 597-599) | Huth, Abergel, High frequency lead/lag relationships - empirical facts, arXiv 1111.7103 (J. Empirical Finance 2014, venue not verified in a fetched file), https://arxiv.org/pdf/1111.7103 | working-paper | pages/R13/huth_abergel_2014_leadlag.pdf |
| E2 | Lead-lag forecast is right 60% but loses after the spread | +0.4 / +0.54 bp per trade at mid; -2.73 / -3.44 bp after spread | "being able to trade at the mid price yields a profitable strategy with an average return of 0.4 (resp. 0.54) bps per trade." ... "However, all the profit made by the lead/lag strategy is lost when taking into account the bid/ask spread: the average return is -2.73 (resp. -3.44) bps per trade." | section 4, p. 23 (txt 1829-1843) | same | working-paper | same |
| E3 | Sample of E1/E2 | 3 months, European equities and equity futures | "We only consider equities and equity futures." ... "The time period is 2010/03/01-2010/05/31" | section 1 (txt 130-132) | same | working-paper | same |
| E4 | E-mini leads cash 10-year Treasuries by 5 ms, not the reverse | +5 ms | "overall cross-market activity in the ten-year Treasury notes and E-mini S&P 500 futures is much lower (see chart below) and indicates that, to the extent that cross-market activity does occur, the E-mini market leads the cash Treasury market (+5 millisecond offset) but not vice versa." | post body, after the cash-futures chart | Dobrev, Schaumburg, High-Frequency Cross-Market Trading in U.S. Treasury Markets, Liberty Street Economics (FRBNY), Aug 2015, https://libertystreeteconomics.newyorkfed.org/2015/08/high-frequency-cross-market-trading-in-us-treasury-markets/ | exchange-regulator | pages/R13/lse_2015_dobrev_schaumburg_crossmarket.html |
| E5 | Treasury futures and cash lead each other at 5 ms | +/-5 ms | "exhibit very pronounced cross-market trading activity at an offset of +/-5 milliseconds, strikingly consistent with the time it takes to transmit information between the two trading venues using current microwave tower technology." | same post | same | exchange-regulator | same |
| E6 | Chicago futures to NJ equities at single-digit ms | 7.25-7.95 ms (fiber), later about 4.2-5.2 ms | "Chicago futures markets to the New Jersey equity markets was through fiber optic lines that allowed equity prices to respond within 7.25-7.95 ms of a price change in Chicago" | p. 2 (txt 79-81) | Laughlin, Aguirre, Grundfest, Information transmission between financial markets in Chicago and New York, arXiv 1302.5966 (Financial Review 49(2) 2014 per RePEc search result), https://arxiv.org/pdf/1302.5966 | working-paper | pages/R13/laughlin_etal_2014_chicago_ny.pdf |
| E7 | At 1-minute, no persistent dollar-index-to-gold or WTI-to-CAD lead; leaders are equity indexes | lists (no magnitudes) | Table 4 "Persistent statistically significant correlations": leaders AUX/AUD, ETX/EUR, JPX/JPY, SPX/USD, USD/MXN; negatively correlated laggers only "ETX/EUR XAU/AUD", "JPX/JPY XAU/AUD", "SPX/USD XAU/AUD". Table 5 gold link only "XAG/USD XAU/USD"; oil only "BCO/USD WTI/USD" and "WTI/USD BCO/USD" | Tables 4-5, pp. 23-24 | Basnarkov, Stojkoski, Utkovski, Kocarev, Lead-lag relationships in foreign exchange markets, arXiv 1906.10388 (Physica A), https://arxiv.org/pdf/1906.10388 | working-paper | pages/R13/basnarkov_etal_2019_fx_leadlag.pdf |
| E8 | Data and cost caveat of E7 | 2016-01..2018-12, bid quotes only, no costs | "The collected data spans from January 2016 until December 2018." ... "highly frequent one-minute exchange rate values only on the bid quotes" ... "a detailed study involving also data on the transaction costs and ask quotes could reveal whether these lead-lag relationships are indeed profitable." | sections 3.1-3.2 (txt 333-336, 394-396, 423) | same | working-paper | same |
| E9 | 60-minute-chart extrema: DAX leads E-mini, gold vs EUR-USD; lags 5-10 min with +/-30 min uncertainty; no P&L | 5-10 min | "The lead-lag ... is between 5 min and 10 min for the point in time of the extrema for the indexes and foreign exchanges and also for Gold versus Silver." ... "these points in time have an uncertainty of +/-30 min. Therefore we cannot view the value ... as an absolute value but more as a tendency" ... "DAX Futures leads E-mini S&P 500 Futures" | section 4.2 and Remark 6 (txt 645-655) | Maier-Paape, Platen, Lead-lag relationship using a stop-and-reverse-MinMax process, arXiv 1504.06235 (2015), https://arxiv.org/pdf/1504.06235 | working-paper | pages/R13/maier_paape_platen_2015_sar_minmax_leadlag.pdf |
| E10 | VIX futures lead SPX futures in high volatility; not profitable after costs | none | "when volatility is high, their prices are highly negatively correlated, with VIX futures leading SPX futures. However, the tightness of the lead-lag relation prevents the formation of profitable trading strategies in a setup that includes transaction costs." | abstract | Bangsgaard, Kokholm, The lead-lag relation between VIX futures and SPX futures, J. Financial Markets 67 (2024) 100851, https://ideas.repec.org/a/eee/finmar/v67y2024ics1386418123000496.html | peer-reviewed [secondary-only] | pages/R13/repec_bangsgaard_kokholm_2024.html |
| E11 | ES/FTSE/DAX futures lead-lag lasts fractions of a second; claimed profitable after costs, constrained by slippage and infrastructure | sub-second | RePEc page: "No abstract is available for this item."; content known only from a search-engine summary | - | Alsayed, McGroarty, Ultra-high-frequency algorithmic arbitrage across international index futures, J. Forecasting 33(6) 2014, 391-408 | peer-reviewed [secondary-only][unverified] | pages/R13/repec_alsayed_mcgroarty_2014.html (no abstract); Southampton copy blocked by a bot check |
| E12 | European-open drift: size | 1.48 bp per day, 3.7% p.a. | "the largest positive returns are between 2:00 and 3:00 - the opening of European markets in U.S. Eastern Time terms (ET) - averaging 3.7% on an annualized basis (1.48 basis points per day)." | Introduction p. 1 (txt 58-60) | Boyarchenko, Larsen, Whelan, The Overnight Drift, FRBNY Staff Report 917 (Feb 2020, rev. Aug 2022), https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf (same file as E.10's boyarchenko_sr917.pdf, sha256 identical) | working-paper | pages/R13/boyarchenko_larsen_whelan_sr917_overnight_drift.pdf |
| E13 | Conditional BtD rule | 01:30-03:30 ET after RSV < 0 | "We also consider a conditional trading strategy that 'buys-the-dip', denoted BtD, which holds the e-mini during the OD+ period but only on trading days following a negative order flow at market close (RSV close t-1 < 0)." | section V (txt 1191-1194) | same | working-paper | same |
| E14 | BtD sizes before and after spread | 6.07% / 4.04% p.a.; Sharpe 1.78 / 1.10 | Table IX (a) "Mean 8.95 4.62 4.20 3.75 6.21 6.07" ... "Sharpe ratio 0.42 0.34 0.23 1.10 1.30 1.78"; (b) "Mean 8.95 0.38 -0.05 -0.59 1.91 4.04" ... "Sharpe ratio 0.42 -0.04 -0.06 -0.54 0.26 1.10" (columns CTC, CTO, OTC, OD, OD+, BtD) | Table IX, p. 43 (txt 1826-1847) | same | working-paper | same |
| E15 | BtD frequency and cost model | about 50% of days; spread only | "the conditional versions of OD+ which holds the e-mini on ~50% of trading days" ... "Returns excluding transaction cost are computed from mid quotes and returns including transaction costs are computed from the best bid and ask prices quotes. The sample period is 2004.1 - 2020.12." | section V and Table IX note (txt 1210-1211, 1858-1860) | same | working-paper | same |
| E16 | Unconditional OD loses after spread | Sharpe 1.1 to -0.5 | "a trading strategy that goes long the S&P 500 futures between 2:00 and 3:00 earns a Sharpe ratio of 1.1 and accounting for bid-ask spreads this reduces to -0.5." | Introduction p. 4 (txt 195-196) | same | working-paper | same |
| E17 | Tokyo arrival also moves the predictability | qualitative | "return predictability around Tokyo open shifts forward by one hour when moving from winter to summer time" | Introduction p. 4 (txt 188-189) | same | working-paper | same |
| E18 | Decay after publication (authors' update) | about 0 since 2021 | "Five additional years of data later, that pattern appears to have faded: the 2:00-3:00 window that previously generated roughly 3.7 percent per annum has averaged close to zero since 2021." ... "The same pattern holds in the E-mini Nasdaq-100 (NQ) and E-mini Dow Jones (YM) contracts." ... "In 2021-25 (bottom panel), the spread is much narrower, consistent with a weaker predictive link in the post-publication sample." | post body (E.10 file) | Boyarchenko, Larsen, Whelan, The Disappearing Overnight Drift, Liberty Street Economics, 1 July 2026, https://libertystreeteconomics.newyorkfed.org/?p=43261 | exchange-regulator (FRBNY blog by the original authors) | reports/stage_e10_research/overnight/lse_blog_43261.html (E.10 copy, re-used, not refetched) |
| E19 | Published version and an independent critique | RFS 36(9) 3502-3547 | "Boyarchenko, N., L. C. Larsen, and P. Whelan (2023): 'The Overnight Drift,' The Review of Financial Studies, 36(9), 3502-3547." ... "this mechanism cannot account for all aspects of over-intra outperformance and over-intra correlations." | references; section 5.4 (txt 856-865, 1076-1077) | Glasserman, Krstovski, Laliberte, Mamaysky, Does overnight news explain overnight returns?, arXiv 2507.04481 (2025), https://arxiv.org/pdf/2507.04481 | working-paper | pages/R13/arxiv_2507.04481_overnight_news.pdf |
| E20 | US stock open raises price discovery in bond futures (information shares, not return predictability) | qualitative | "We find that price discovery increases in the US, UK, and German futures following the opening of the US stock market, indicating the importance of the US stock market in domestic and international government bond futures." | abstract | Indriawan, Jiao, Tse, The impact of the US stock market opens on price discovery of government bond futures, J. Futures Markets 2019 (accepted manuscript), https://openrepository.aut.ac.nz/bitstreams/e1c7c388-f556-4786-975c-ec486378d282/download | peer-reviewed (accepted manuscript) | pages/R13/aut_2019_us_open_bond_futures.pdf |
| E21 | Oil-currency cojumps are rare; oil and USD/CAD strongly negatively correlated contemporaneously (15-min) | qualitative | "while the probability of cojumps involving oil and currencies is relatively low, currency pairs frequently exhibit simultaneous jumps." ... "a strong negative correlation between oil and USD/CAD, reflecting the Canadian dollar's sensitivity to oil prices." | abstract; section 3 (txt 599-600) | Mensi, El-Khoury, Reboredo, Sensoy, Al-Yahyaee, Modeling intraday jumps and cojumps in oil and currency markets, Rev. Quant. Finance and Accounting 2025, doi 10.1007/s11156-025-01461-x | peer-reviewed (repository copy) | pages/R13/bilkent_2025_oil_currency_cojumps.pdf |
| E22 | Oil to CAD: lagged predictive ability daily only and "ephemeral" | qualitative | search-result text only: "little systematic relation between oil prices and the exchange rate at the monthly and quarterly frequencies" ... daily relationship holds with contemporaneous or lagged oil prices, but with lagged prices "the predictive ability is ephemeral" | abstract (via search result) | Ferraro, Rogoff, Rossi, Can oil prices forecast exchange rates?, J. Int. Money and Finance 54 (2015) 116-141; NBER w17998 | peer-reviewed [secondary-only] (an NBER copy was fetched before its terms were read; it is listed in DO_NOT_COMMIT.txt and not used as retrieved evidence) | none used |
| E23 | Asian/European cash-index patterns forecast close-to-open gaps; tiny sample, cash indexes, no trading test | 35 test days | "The period covered is from 24th September 2007 to 8th May 2008." ... "The testing sample for each specification contains 35 days (curves)." | section 5 (txt 419-421, 449) | De Gooijer, Diks, Gatarek, Information flows around the globe: predicting opening gaps from overnight foreign stock price patterns, Tinbergen Institute DP 2009-107/4, https://repub.eur.nl/pub/17493/20091074.pdf | working-paper | pages/R13/degooijer_diks_gatarek_2009_opening_gaps.pdf |

## 4. Negative evidence

- Speed: every measured cross-market lead between liquid futures is milliseconds to seconds (E1, E4,
  E5, E6, E11). Retail latency (100 ms to seconds) and 1-minute bars cannot capture it; Topstep bans
  HFT (brief section 3).
- After-cost failures: Huth-Abergel lead-lag strategy +0.4 bp at mid becomes -2.73 bp after the spread
  (E2); VIX futures to SPX futures "prevents the formation of profitable trading strategies" with costs
  (E10); the unconditional European-open hour goes from Sharpe 1.1 to -0.5 after the spread (E16).
- Null at 1 minute: no persistent UDX-to-XAU/USD or WTI-to-USD/CAD lagged link in 36 monthly tests,
  2016-2018 (E7, E8). Gold's only persistent leader in that study is silver; oil's only link is
  Brent-WTI.
- Weak and unpriced: the 60-minute-chart extrema study gives 5-10 min "tendencies" with +/-30 min
  timestamp uncertainty and no P&L (E9).
- Decay: the overnight drift, the only sized minutes-to-hours effect in this area, faded after 2021 by
  its authors' own account, in ES, NQ and YM, and the imbalance-conditioned link narrowed (E18).
- Treasury to equity: I found no published intraday study in which Treasury futures returns predict
  equity index futures returns at seconds-to-30-minutes with a size. The only direction measured is
  E-mini leading cash Treasuries by 5 ms (E4). This is an absence in what I could search (OpenAlex,
  Semantic Scholar and Firecrawl went down during the read, section 9), not proof that no such paper
  exists.
- Crude to energy equities: no intraday study with returns found; search results gave only weekly or
  practitioner commentary (pointers, not evidence). Energy-equity futures are not among the owned roots.
- Program's own tests agree: g17 60-min lead returns (NQ, ZN, 6E, CL, GC, ZC, MBT) failed in Gate 0
  and in the E.20 search; K8 NULL in E.22.

## 5. Data and cost

- R13-C1 needs (a) the condition: closing relative signed volume RSV (aggressor-signed volume / gross
  volume, 15:15-16:15 ET), which needs trade-level data with aggressor side (Databento trades or TBBO
  schema, not owned; one-minute OHLCV carries no side). Price: not fetched by R13 (databento.com pages
  belong to R2/R4). (b) The traded window 01:30-03:30 ET on MES/MNQ: owned 1-minute bars cover it.
  A price-only proxy (for example the sign of the last-hour return) is NOT the paper's signal; any
  such proxy would be a new design choice for the lead.
- Per-trade derivation (inputs for the lead, not a ruling): Table IX gives 6.07% annualized (mean of
  daily returns times about 250; the paper's 3.7% p.a. = 1.48 bp/day implies 250 days). Holding on
  about 50% of days gives 6.07% / (0.5 x 250) = 4.86 bp per trade before costs; after the bid-ask
  spread 4.04% / 125 = 3.2 bp. At ES 6,000: 4.86 x 6,000 / 10,000 = 2.92 ES points = 11.7 MES ticks
  (tick 0.25). At NQ 21,000: 10.2 NQ points = 40.8 MNQ ticks, but no NQ figure is published for BtD.
  The "about 50%" is the paper's approximation, so the per-trade figure carries that error. All of it
  is 2004-2020; the authors report decay after 2021 (E18).
- Unconditional OD (A-H1 analogue): 1.48 bp/day = 0.89 ES points at 6,000 = 3.6 MES ticks; already
  tested on MES and failed (A-H1, D.1 and D.1f).
- Every other pair: no candidate, so no data request. For reference, sub-second lead-lag needs
  MBP-1/MBO with exchange timestamps on two venues plus colocation; out of scope for a retail prop
  account.

## 6. Prop compatibility

- R13-C1: 00:30-02:30 CT lies inside the Topstep trading day (17:00-15:10 CT), flat long before 15:10
  CT; one entry, one exit; not near a scheduled US release (P06 not triggered; check ECB or European
  data at 02:00 ET case by case); not HFT; automatable through the TopstepX API, or manual at
  22:30-00:30 PT for a trader in British Columbia. DLL exposure: one 2-hour MES or MNQ hold per
  signal day.
- Millisecond lead-lag (E1-E6, E11): incompatible (HFT ban, no VPS, 1-minute data).

## 7. Overlap with tested mechanisms

| tested id | what it did | how the R13 reading relates |
|---|---|---|
| K8-flight-01 (H30, HEOD) | MES 5-min tail to long MGC | equity-to-gold flight; R13 found no new dollar-to-gold evidence |
| K8-oilcad-01 | MCL 5-min shock to 6C | same pair as the brief's crude-to-CAD; the literature (E7, E21, E22) gives no lagged minute-level effect |
| K8-wkndbtc-01 | MBT weekend to MNQ | bitcoin closed; not revisited |
| Gate 0 g17_* (E.12), E20S-01..45 | 60-min lead returns of NQ, ZN, 6E, CL, GC, ZC (MBT, MES where covered) as features | covers Treasury-to-equity (g17_zn into NQ/RTY), dollar-to-gold (g17_6e into GC), crude-to-CAD (g17_cl into 6C, gate0B) at 60 min; all FAIL |
| E16-H2 | NQ vs ZN month-end pair | multi-day, not intraday lead-lag |
| K3-mehedge-01 | Nikkei month return to 6J | Asian equity to yen, month-end only |
| A-H1 | European-open drift, unconditional, MES | R13-C1 is its conditional (BtD) version; same source as E.10 K9O-001, decay in K9O-002 |

## 8. Re-dig section

Not a re-dig reader. One verdict note from the sources read: E18 SUPPORTS the A-H1 closure (D.1 screen
fail): "the 2:00-3:00 window that previously generated roughly 3.7 percent per annum has averaged
close to zero since 2021." E7 and E21 are consistent with the E.22 "K8 NULL" statement for
K8-oilcad-01 (no lagged WTI-to-CAD link at 1 minute), but they test different instruments (spot FX
quotes), so I mark that SUPPORTS (weak).
E2 (lead-lag profit lost to the spread at second horizons) indirectly SUPPORTS the E.12 Gate 0 and
E.20 FAIL verdicts on the g17 60-minute lead features: the documented leads are over long before 60 min.

## 9. Fetch log, terms, budget notices

| url | UTC | sha256 | saved path | status | tool |
|---|---|---|---|---|---|
| https://arxiv.org/pdf/1111.7103 | 2026-10-18T08:41:12Z | 12df47d24d980ce2839e1b2633d2eea8d6dca88816c02498133eee84dc351857 | pages/R13/huth_abergel_2014_leadlag.pdf | ok | curl |
| https://arxiv.org/pdf/1302.5966 | 2026-10-18T08:41:29Z | 8c1a401e79de194870ebd960ce9ee150648ac58b520fc3f6cdd13594eb3fff2a | pages/R13/laughlin_etal_2014_chicago_ny.pdf | ok | curl |
| https://www.atlantafed.org/-/media/.../dobrev-schaumburg_high-frequency-cross-market-trading.pdf | 2026-10-18T08:41:30Z | cbf610a6673b1dca410900853394378b26ddf415c40977efea606b2537d15fba | deleted (404 page) | blocked (404) | curl |
| https://repub.eur.nl/pub/17493/20091074.pdf | 2026-10-18T08:43:37Z | cc18abd302df0f35f90b0f28c7f64b6ab5fa52f2aeeba1fcc1a08dcb35170392 | pages/R13/degooijer_diks_gatarek_2009_opening_gaps.pdf | ok | curl |
| https://openrepository.aut.ac.nz/bitstreams/e1c7c388-f556-4786-975c-ec486378d282/download | 2026-10-18T08:43:40Z | 43ef0e0833deefd354ebb446bedfc98e2b71b3e366f5433c5dc73d1a1796b47c | pages/R13/aut_2019_us_open_bond_futures.pdf | ok | curl |
| https://www.nber.org/papers/w17998.pdf | 2026-10-18T08:43:41Z | aafedbf1c81f223ec0b1fa88cfed681817fe76b7405d0732ae56308f9a2649c1 | pages/R13/ferraro_rogoff_rossi_nber_w17998.pdf | terms-forbid (read after fetch; DO_NOT_COMMIT) | curl |
| https://repository.bilkent.edu.tr/bitstreams/ac8a69c7-38ac-4fc9-a0e9-3fc94f64b695/download | 2026-10-18T08:43:45Z | f7b3c09814be1e24090b57e765408499c230cc0dbec7f5c1d4da75ed032e61cd | pages/R13/bilkent_2025_oil_currency_cojumps.pdf | ok | curl |
| https://arxiv.org/pdf/1906.10388 | 2026-10-18T08:43:49Z | 205f3e3b753492e28387f0a863d7f88f327cb15b8f6c45a30a3590d381e00c44 | pages/R13/basnarkov_etal_2019_fx_leadlag.pdf | ok | curl |
| https://arxiv.org/pdf/1504.06235 | 2026-10-18T08:45:11Z | f3a0edc7f51c7a19ff3ee9be3d0ff7a2f78e5bbc1ff1e68758fafd1b7f9a02d1 | pages/R13/maier_paape_platen_2015_sar_minmax_leadlag.pdf | ok | curl |
| https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf | 2026-10-18T08:46:17Z | 403276b2ea8227c14ccfb854014af1df6a425430e5f622599640d7c0c16e683a | pages/R13/boyarchenko_larsen_whelan_sr917_overnight_drift.pdf | ok (identical to E.10 copy) | curl |
| https://eprints.soton.ac.uk/341452/ | about 2026-10-18T08:45Z (not logged by script) | n/a | not saved | blocked (bot check) | curl |
| https://libertystreeteconomics.newyorkfed.org/2015/08/high-frequency-cross-market-trading-in-us-treasury-markets/ | 2026-10-18T08:50:26Z | 32cd50bcd4b6bab5a6cf44f8c2f085f05b203dbeb1bb7ba28fd6559c74658d29 | pages/R13/lse_2015_dobrev_schaumburg_crossmarket.html | ok | curl |
| https://ideas.repec.org/a/wly/jforec/v33y2014i6p391-408.html | 2026-10-18T08:50:42Z | c3ca968eabffcb2abcb8da466ff2907988fda24ca4efc39185b516714537fbc8 | pages/R13/repec_alsayed_mcgroarty_2014.html | ok (no abstract) | curl |
| https://ideas.repec.org/a/eee/finmar/v67y2024ics1386418123000496.html | 2026-10-18T08:50:49Z | 750080ccd1fff933163843f8d5f1d57d8998f3ea2c74a13c90ecfad7128c418e | pages/R13/repec_bangsgaard_kokholm_2024.html | ok | curl |
| https://arxiv.org/pdf/2507.04481 | 2026-10-18T08:50:56Z | 9ac5796c29529683383b82c08dfca7e57d1eb7c3e039df1d59a56dd339cc19bd | pages/R13/arxiv_2507.04481_overnight_news.pdf | ok | curl |

Terms: arxiv.org (cited existing terms_log line; crawl-delay 15 s kept between arXiv PDFs except
1906.10388 to 1504.06235 spacing over 80 s); ideas.repec.org (existing line); NY Fed and Liberty
Street (existing line, E.20 ruling); new lines appended for www.atlantafed.org, repub.eur.nl,
openrepository.aut.ac.nz, repository.bilkent.edu.tr, eprints.soton.ac.uk (blocked). www.nber.org:
another reader logged "forbidden" at 08:44:30Z; R13 had fetched w17998 at 08:43:41Z after reading
only robots.txt (my error); the files are listed in DO_NOT_COMMIT.txt and not used as evidence.

Budget notices (UTC):
- 08:42Z Firecrawl: "Rate limit exceeded. Consumed (req/min): 11" (one firecrawl_search not run).
- 08:47:20Z OpenAlex: "Rate limit exceeded ... free daily budget shared by everyone on your network's
  IP address ... used up" (no key in .env; OpenAlex stopped for R13).
- 08:48-08:52Z Semantic Scholar keyless: three "Too Many Requests" with 60 s waits: throttled.
- 08:52:27Z Firecrawl: "Request failed with status code 402 ... out of credits" (two searches not run;
  Firecrawl stopped for R13).
- WebSearch: 16 calls used of 45; no over-budget notice.

## 10. Unfinished and unverified

- Forward citations of Huth-Abergel, Basnarkov et al. and Boyarchenko et al. not pulled (OpenAlex
  budget exhausted, S2 throttled).
- Dobrev-Schaumburg working paper (2018) full text not retrieved (Atlanta Fed URL 404; federalreserve
  .gov copy not tried); only the 2015 Liberty Street post is quoted.
- Alsayed-McGroarty (2014) full text not read (Southampton bot check, RePEc has no abstract):
  [secondary-only][unverified].
- Bangsgaard-Kokholm (2024): abstract only; horizon (seconds vs minutes) not verified.
- Ferraro-Rogoff-Rossi: only search-result text usable (terms issue above).
- No dedicated search for Treasury-to-equity lead-lag in Chinese or European data, or for intraday
  gold vs real yields; the Treasury-to-equity absence is a search gap as much as a finding.
- g17 features kept in E.20's search inferred from reports/stage_e20_briefs/backward_swap_table.md
  line 59, not from the E.20 configs.
