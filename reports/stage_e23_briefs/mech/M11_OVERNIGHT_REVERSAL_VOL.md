# M11_OVERNIGHT_REVERSAL_VOL: mechanism memo (Stage E.23 P1.2)

Worker: MechanismReaderM11_OVERNIGHT_REVERSAL_VOL-OpusHigh. Brief: reports/stage_e23_briefs/brief_mechanism.md.
Started 02:16:35 PDT 2026-10-17 (date). Pages and the fetch log: reports/stage_e23_briefs/mech_pages/M11_OVERNIGHT_REVERSAL_VOL/
(fetch_log.md, query_log.md). Every time below is PDT. Line numbers (Lnnn) refer to the saved text file named in the
evidence table. Figures marked "derived" are my arithmetic on printed numbers, not printed results.

The question for every member: does the trigger's event predict the 5 or 20 trading days after the trigger day's
settlement (entry at the trigger day's settlement, intraday P&L not counted)?

Members and triggers, from their docstrings:
- K4-ovr-01 (MCL, NG) and K5-ovr-01 (MGC, MHG): the 60-minute return at an hourly decision time is at or beyond the
  10th/90th percentile of the same-clock values on the prior 20 sessions. Side: fade (buy after an extreme fall, sell
  after an extreme rise). The member's own source (K5-029) is intraday (1-minute to 1-hour overreactions, about six
  months of 2019-11..2020-06 data; reports/stage_e0_catalog_K4.md lines 723-793).
- E.16 H4: d-1's settlement-window move m (S-30 to S). Side on d: -sign(m) (reports/stage_e16_prereg_H4.md section 1-2).
  The sign rests on Baltussen et al. 2021 "reverts over the next days" (ibid. section 4).
- K1-vxnband-01 (MNQ): an intraday breach of +/- VXN/16 (a one-sigma daily move implied by the prior day's VXN) around the
  prior close, only when VXN < 20 or VXN >= 30. Side: fade. The member's own source (Seeck 2026, abstract only) is a
  30-minute exit (reports/stage_e0_catalog_K1.md lines 403-416).

## 1. Evidence table

| Key | Citation | URL | Saved path | sha256 | Verbatim quote (location) | Claim supported (horizon, direction, magnitude, sample, instrument) |
|---|---|---|---|---|---|---|
| BDLM2021 | Baltussen, G., Da, Z., Lammers, S., Martens, M. (2021). Hedging demand and market intraday momentum. JFE 142, 377-403. doi 10.1016/j.jfineco.2021.04.029 | https://pure.eur.nl/files/58145484/1_s2.0_S0304405X21001598_main.pdf | reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md (program copy, reused) | 18cb436e9d18cb3eff3565cddfe85b35fa1c5d5d8bf2afb85df42b6ab49e0465 | (a) L2715-L2720: "In case the market intraday momentum is caused by price pressure from hedging demands, the price should revert back after the hedging activity has ceased. ... under the hedging explanation, we expect meanreversion in the near future". (b) Table 11 caption L2844-L2846: "regressing the next day return (r_cc,t+1), the next two days return (r_cc,t+2), and the next three days return (r_cc,t+3) on a constant and today's last half-hour return (r_LH,t)" ... "Adjusted R2 and regression coefficients are multiplied by 100." (c) L3140-L3141: "In all four markets, we observe reversals, although this effect is not significant in currency futures." (d) Table 11 cells (L2880-L2907, PDF-to-markdown conversion): Panel A equity, r_LH coefficient: t+1 "-14.51* (-1.70)", t+2 "-29.05*** (-3.16)", t+3 "-27.98***(-2.61)"; Panel C commodity: "-0.82 (-0.25)", "-8.56 (-1.61)", "-12.22**(-2.17)"; Panel B bonds t+2 "-10.68(-1.60)", t+3 "-19.64**(-2.21)"; Panel D currency t+2 "-8.64(-1.14)", t+3 "-6.98(-0.84)". (e) Fig. 5 caption L2826-L2830: "Samples range from December 1974 to May 2020." | H4: horizon 1 to 3 days after the last-half-hour move (not 5, not 20). Direction: reversal of the last-half-hour move. Magnitude (slope x100 per unit r_LH): equity -29 by t+2 (t -3.16); commodity -12 by t+3 (t -2.17); bonds -20 by t+3 (t -2.21); currency n.s. Pooled futures by class, Dec 1974 - May 2020, gross. The bond t+1 and currency t+1 cells (1.77 (0.41); -8.06 (-1.32)) are placed by the converter's layout only: check against the printed PDF before using them |
| BvD2019 | Baltussen, G., van Bekkum, S., Da, Z. (2019). Indexing and stock market serial dependence around the world. JFE 132(1), 26-48. doi 10.1016/j.jfineco.2018.07.016 | https://www3.nd.edu/~zda/Indexing.pdf | mech_pages/M11_OVERNIGHT_REVERSAL_VOL/bvd_indexing_2019.pdf (+ .txt) | pdf 05333bbdbe54c931... (full in fetch_log); txt d7baad18f9598ebad8b9d9286e26cf8b854a1d325595a33dee0253058f858352 | (a) Abstract (p. 1, L30-L36): "While many studies find serial dependence to be positive until the 1990s, it switches to negative since the 2000s. This change happens in most stock markets around the world and is both statistically significant and economically meaningful." (b) Table 1 Nasdaq 100 row (L383-L384): Daily AR(1) before "0.071**", after "-0.065***" (t "(-2.79)"), t(diff.) "-3.45***"; Weekly AR(1) before "-0.001", after "-0.074" (t "(-1.63)"). Before/after = "before and after March 3, 1999". (c) p. 8, L515-L519: "Fig. 3 plots daily pth-order autocorrelations ... for p up to 21. The plot shows that serial dependence has declined across most lags and has turned significantly negative for p equal to one, two, three, and five." (d) p. 13, L808-L812: "a strategy that trades against the negative MAC(5) using all indexes (the S&P 500 alone) in our sample would result in an annualized Sharpe ratio of 0.63 (0.67) after March 2, 1999." (e) L288-L289: "up to December 31, 2016". | K1-vxnband (and H4 on equity roots): horizon 1 to 5 days (daily lags 1-5, weekly AR(1)); not 20. Direction: reversal of the prior day's (and week's) index move. Magnitude: Nasdaq 100 next-day slope -0.065 (t -2.79), weekly -0.074 (t -1.63, n.s.), 1999-03..2016-12, cash index returns. Not conditioned on VXN or on move size. Sign changed after 1999 (a documented regime change, linked to indexing) |
| Giot2002 | Giot, P. (2002/2005). Implied volatility indices as leading indicators of stock index returns? CORE DP 2002/50; publ. as "Relationships between implied volatility indexes and stock index returns", J. Portfolio Management (2005) | (E.10 copy) | reports/stage_e10_research/regime/giot_uclouvain.txt (program copy, reused) | dd3a717c208a23e13d6a601b69730f5effb49ec148995f0df505842a8f8b2e19 | (a) L98-L100: "the whole dataset (which ranges from 3/1/1995 - 2/8/2002) into a bull market period (3/1/1995 - 10/3/2000) and a bear market period". (b) p. 11-12, L403-L410: "For 1- and 5-day-ahead returns, their average and standard deviation are still increasing functions of the VXN level: traders making short-term buy trades in the NASDAQ100 index when the VXN index is high do achieve (on average) large positive returns ... this is true both for the bull and bear market periods." (c) L415-L418: "For 20- and 60-day-ahead returns, the bull and bear markets do not deliver the same results. During the bull market, 20- and 60-day-ahead returns present very nice risk-return properties ... when the VXN index is low. However results are poor when the VXN level is high". (d) L348-L350 (1-day regression): "the econometric analysis does not show a strong relationship between VIX or VXN levels and 1-day ahead returns". | K1-vxnband: horizon 5 days (and 20 mixed). Direction: unconditional long drift after high VXN (favours the BUY side of a fade at VXN >= 30, works against the SELL side); at low VXN, 20-day long returns good in the bull market (favours BUY regardless of the breach side). Magnitude: no t-statistics for the n-day tables; sample 1995-2002, NDX cash, no overlap with 2010-2024 |
| Nagel2012 | Nagel, S. (2012). Evaporating liquidity. RFS 25(7), 2005-2039; NBER WP 17653 (Dec 2011) | https://www.nber.org/papers/w17653.pdf | mech_pages/M11_OVERNIGHT_REVERSAL_VOL/nber_w17653_nagel.pdf (+ .txt) | txt 1088bd72ddc3d57ebc1adb9407acec12df79a7f8ae03fe0ab0a860f25c8e55b7 | (a) Abstract L46-L49: "the expected return from liquidity provision is strongly time-varying and highly predictable with the VIX index. Expected returns and conditional Sharpe Ratios increase enormously along with the VIX during times of financial market turmoil". (b) Section 4, L1283-L1288: "reversal strategies constructed from individual stocks have returns that are strongly predictable with the VIX. The magnitude of the coefficient (0.22) is big relative to the standard error shown in parenthesis (0.02). An increase of one percentage point in the normalized VIX (corresponding to an increase of sqrt(250) ~ 16 percentage points in the annualized VIX) is associated with an increase of 0.22 percentage points in the daily returns of the return-reversal strategy." (c) L1169-L1170: "The sample period runs from January 1998 to December 2010." | K1-vxnband VXN >= 30 bucket (analog): direction reversal, stronger at high implied vol. Cross-sectional US stocks and industry portfolios, 1998-2010, short-horizon (5-day formation, daily) reversal. Not an index-level test |
| BCR2008 | Bianco, S., Corsi, F., Reno, R. (2008). Serial correlation and heterogeneous volatility in financial markets: beyond the LeBaron effect. arXiv 0810.4912 | https://arxiv.org/pdf/0810.4912 | mech_pages/M11_OVERNIGHT_REVERSAL_VOL/bcr_arxiv_0810_4912.pdf (+ .txt) | txt 441aea63ecd5f3adfc1f162bdb244ff1983e8645c9f13e40781b721fbf0df125 | Abstract L8-L11: "At daily and weekly level, serial correlation and volatility are known to be negatively correlated (LeBaron effect). While confirming that the LeBaron effect holds also at intraday level ... We show that unexpected volatility is instead positively correlated with intraday serial correlation." | K1-vxnband: secondary statement of the LeBaron (1992) effect: daily/weekly autocorrelation is lower when (expected) volatility is high, i.e. reversal is more likely in the VXN >= 30 bucket than the VXN < 20 bucket. LeBaron 1992 itself not fetched: [unverified] beyond this secondary sentence. S&P 500 |
| BK2025 | Bangsgaard, C. D., Kokholm, T. (2025). The stock market impact of volatility hedging: evidence from end-of-day trading by VIX ETPs. J. Banking & Finance 180, 107556 | https://ideas.repec.org/a/eee/jbfina/v180y2025ics0378426625001761.html | mech_pages/M11_OVERNIGHT_REVERSAL_VOL/ideas_bangsgaard_kokholm_2025.html | e31bf26177205352473c48c411b716503cb7efdd0c0ebfe2ff053b80f7e05b02 | Abstract only: "The VIX ETP demand is a strong predictor of the end-of-day SPX futures return in-sample and out-of-sample. We find evidence of a subsequent reversal, suggesting that VIX futures hedging activities can move the SPX futures market for reasons unrelated to price discovery." | H4 (equity roots): mechanism support, end-of-day flow pressure in index futures reverses. Horizon of the reversal not in the abstract [unverified]. Abstract only |
| KRT2016 | Kang, W., Rouwenhorst, K. G., Tang, K. (2020). A tale of two premiums: the role of hedgers and speculators in commodity futures markets. JF 75(1), 377-417. Version read: WP of 4 Dec 2016 | https://www7.uc.cl/economia/finance_uc/docs/conferences/11th/Rouwenhorst-Tale%20of%20two%20premiums.pdf | mech_pages/M11_OVERNIGHT_REVERSAL_VOL/krt_tale_two_premiums_2016wp.pdf (+ .txt) | txt ad0cb5ba652e6f5136e9df9bf01fef9fa30667e94220346c16abaec10591da35 | (a) p. 14, L642-L657: "hedgers, who most intensively buy commodities that have fallen in price during the prior two weeks (prior return of -3.09%), and most intensively sell winners (prior return of 3.68%). ... during the 4 days after portfolio formation, commodities in the top quintile (largest Q) earn on average 0.20% compared to -0.01 % for commodities in the bottom quintile ... The return difference of 0.21% is significant, with a t-statistic of 3.04. ... a positive excess return spread persists during days 5-20 following the release of the CFTC report: 0.30% during days 5-10 (t = 3.62) and 0.15% (t = 1.23) during days 11-20. ... a spread of 67 basis points during the four weeks (1-20 days) following a position change". (b) p. 16, L760-L766: "underperform the quintile that are sold most heavily by hedgers by 6.77% during the two weeks prior to the positions report, followed by a partial reversal of 0.61% during the next 40 trading days, leaving (on net) a permanent component to the price change of 6.16%." (c) Table caption L2147-L2148: "from 1994/1/2 to 2003/12/31, and from 2004/1/2 to 2014/11/1". | K4/K5-ovr (analog only): horizon 1-20 days. Direction: partial reversal of liquidity-demand-driven moves (impatient speculators), but small relative to the move (0.61% of 6.77%). Cross-sectional quintile spread on CFTC position changes, 26 commodities (incl. oil, copper), 1994-2014. Not conditioned on an intraday price move |
| CP2020 | Caporale, G. M., Plastun, A. (2020). Gold and oil prices: abnormal returns, momentum and contrarian effects. Brunel Economics and Finance WP 2015 (July 2020); CESifo WP 8445 | https://www.brunel.ac.uk/economics-finance-and-accounting/research/pdf/2015-Jul-GMC-Commodities.pdf | mech_pages/M11_OVERNIGHT_REVERSAL_VOL/brunel_2015_gmc_commodities.pdf (+ .txt) | txt 68898632039ce441aaea22ea125a27c19e1e7f516e2ce1ef2a2dac9a164b0f76 | (a) Abstract L49-L62: "using daily Gold and Oil price data over the period 01.01.2009-31.03.2020 ... Prices tend to move in the direction of abnormal returns till the end of the day when these occur. ... On the following day two different price patterns are detected: a momentum effect for Oil prices and a contrarian effect for Gold prices respectively." (b) L195-L196: "Daily and hourly data for Gold and Oil over the period 01.01.2009-31.03.2020 (GMT +3 time zone) are used. The data source is MetaQuotes Software Corp." (c) L224-L226: "k is the number of standard deviations used to identify the abnormal returns (k=2 ...)". (d) L174-L177 (secondary citation): "Wang and Yu (2004) found strong evidence of weekly return reversals in futures prices; they also showed that futures market overreactions exist". | K4-ovr MCL: next day (1 day only) continuation of a 2-sigma daily move; K5-ovr MGC: next day reversal. Horizon 1 day, neither 5 nor 20. No t-statistics on the next-day effect in the quoted text; MetaQuotes (retail CFD/spot feed), 2009-2020; daily abnormal returns, not hourly deciles |
| MW2014 | Mazouz, K., Wang, J. (2014). Commodity futures price behaviour following large one-day price changes. Applied Financial Economics 24(14), 939-948. doi 10.1080/09603107.2014.914140 | https://orca.cardiff.ac.uk/id/eprint/61689/ | mech_pages/M11_OVERNIGHT_REVERSAL_VOL/orca_mazouz_61689_fetch.md | babbf8559aca4b193f00403898fcc2282f34aab7dbf88663312548aa149551f9 | Abstract only: "the mean-adjusted abnormal return model suggests that investors in 6 of the 18 commodity futures examined in this study either underreact or overreact to positive surprises. It also detects underreaction patterns in eight commodity future prices following negative surprises. However, after making appropriate systematic risk and conditional heteroscedasticity adjustments, we show that almost all commodity futures react efficiently to shocks." | K4/K5-ovr: null after risk adjustment, multi-day post-shock (window not in the abstract [unverified]). 18 commodity futures; sample [unverified]. Abstract only (full text behind Cloudflare) |
| Hua2012 | Hua, W. (2012). International Financial Markets (PhD dissertation, essay 2: large one-day price changes in 26 commodity futures). University of New Orleans, td/1443. Published version: Hua and Wei (2014), Int. J. Business Development (Inderscience) | https://scholarworks.uno.edu/td/1443 | mech_pages/M11_OVERNIGHT_REVERSAL_VOL/uno_hua_td1443.html | 71cffc4e8448dd29f41028be6e56b25d428da9015406f18bb16ee4a5fc7ff8d2 | Abstract only: "Without controlling for other factors, I find some support for the overreaction theory, especially following negative large price changes in closing. However, controlling for macro factors or market conditions, there is no support for overreactions." | K4/K5-ovr: null after controls. 26 commodity futures; horizon and sample [unverified]. Abstract only |
| DKW2015 | Della Corte, P., Kosowski, R., Wang, T. (2015). Market closure and short-term reversal. SSRN 2730304 | (E.10 copy of the EPFL seminar page) | reports/stage_e10_research/overnight/dellacorte_epfl_memento.html (program copy, reused) | f33a2ad4a0fd59f80572ed60bc50d0ef579a546d769be96e66b7a9a0186f956f | Abstract only: "A strategy that buys securities with low past overnight returns and sell securities with high past overnight returns generates sizeable out-of-sample excess returns and Sharpe ratios. This strategy { labelled as overnight-intraday reversal strategy { outperforms the conventional short-term reversal strategy for major international equity markets and futures written on equity indices, interest rates, commodities, and currencies." | Family background (overnight vs intraday): reversal of the overnight move during the next intraday session, cross-sectional. Intraday horizon; says nothing about 5-20 days. No member of this family uses the overnight return |
| MOP2012 | Moskowitz, T., Ooi, Y. H., Pedersen, L. H. (2012). Time series momentum. JFE 104, 228-250 | (E.10 copy) | reports/stage_e10_research/overnight/mop_tsmom.txt (program copy, reused) | 6fdd907354d8347c0731e9a9a8f7f244dec75d2c2beed26ebc18bb63ec65647b | Section 1 (L186-L188, right column): "Section 3 documents time series momentum at horizons less than a year and reversals beyond that." | Counter-evidence at the 20-day (one-month) horizon: futures returns over the past month(s) continue. Monthly lookbacks; an hourly or half-hour move is a tiny part of a monthly return, so the link to these triggers is indirect |
| CKX2015 | Cheng, I.-H., Kirilenko, A., Xiong, W. (2015). Convective risk flows in commodity futures markets. Review of Finance 19(5); NBER WP 17921 | https://www.nber.org/papers/w17921.pdf | mech_pages/M11_OVERNIGHT_REVERSAL_VOL/nber_w17921_ckx.pdf (+ .txt) | txt db48d1cb5e026b27695acbac9f0793f140878533a46165fe248dd91a183535b3 | L971-L975: "no commodities show significant reversal, and in fact grains show continuation. ... the commercial hedgers also show little sign of reversals to movements in the VIX, suggesting the risk convection was a re-allocation of risk that does not reverse over a 13-week horizon." | Read, not used for a direction: about positions after VIX changes (2000-2011), not about prices after a price trigger |

## 2. Per-member paragraphs

### E.16 H4 (next-day reversal of the settlement-window move; all H4 products)

- Strength: moderate (published multi-day evidence on the same event, the last-half-hour return, pooled futures by
  asset class, t >= 2 at 2 to 3 days for equity, commodity and bond futures, sample 1974-2020 overlapping 2010-2024; but
  the horizon stops at 3 days, the magnitude per event is a small fraction of the trigger move, and nothing speaks to 5
  or 20 days).
- Direction: reversal of the trigger move m (d-1's settlement-window move), which is the member's own side (-sign(m)).
- Reason: Under the hedging (gamma) explanation, the last half hour carries transitory price pressure from market makers'
  rebalancing, so "the price should revert back after the hedging activity has ceased" (BDLM2021 (a)). The paper finds
  "reversals" in "all four markets", insignificant only in currencies (BDLM2021 (c)), and frames the alternative
  (informed trading) as predicting no reversal. A separate end-of-day flow channel in index futures (VIX ETP hedging)
  also shows "a subsequent reversal" (BK2025, abstract only), and post-1999 index returns reverse at daily lags 1-5
  (BvD2019 (a), (c)), which supports the equity roots.
- Horizon: neither 5 nor 20 directly; the evidence covers 1, 2 and 3 days after the event day. For E.23 the entry is at
  d's settlement, one day after the event (t = d-1), so only the increment from close t+1 to close t+3 is available to
  the multi-day hold.
- Magnitude: BDLM2021 Table 11 (slope x100 on r_LH; t in parentheses): equity -14.51 (-1.70) by t+1, -29.05 (-3.16) by
  t+2, -27.98 (-2.61) by t+3; commodity -0.82 (-0.25), -8.56 (-1.61), -12.22 (-2.17); bonds -10.68 (-1.60) by t+2,
  -19.64 (-2.21) by t+3; currency not significant. Derived: the part after a d-settlement entry (t+3 slope minus t+1
  slope) is about -0.13 x m for equity and about -0.11 x m for commodities, so a 20 bp settlement-window move would
  imply about 2 to 3 bp gross over the next two days (illustrative arithmetic on an assumed m, no standard error for the
  difference is printed). Gross; no costs in the paper; sample ends May 2020. Decay: the paper's subsample table shows
  the intraday-momentum slope smaller in 2000-2020 for every class (reports/stage_e20_briefs/shared/baltussen_notes.md,
  Table 5); no subsample is printed for the reversal. Program context, not literature: the E.16 overlap note records
  reversal-leaning, unrejected Gate 0 ICs (stage_e16_prereg_H4.md section 4).

### K4-ovr-01 (MCL, NG) and K5-ovr-01 (MGC, MHG) (hourly overreaction fade)

- Strength: weak. The member's own mechanism (K5-029) is intraday-only (minute-to-hour overreaction and snap-back); for
  the 5-20 days after the trigger day there is no published test on this event, and the closest analogs are a
  one-day study on retail-feed data, a cross-sectional liquidity-provision analog, and two abstract-only nulls.
- Direction: the literature disagrees, and it differs by root:
  - Continuation: oil next day (CP2020 (a): "a momentum effect for Oil prices"); futures time-series momentum at one
    month (MOP2012).
  - Reversal: gold next day (CP2020 (a): "a contrarian effect for Gold prices"); partial reversal of liquidity-driven
    commodity moves over 1-20 days (KRT2016 (a), (b)); "weekly return reversals in futures prices" (Wang and Yu 2004,
    cited inside CP2020 (d); the original was not reached: [unverified]).
  - No effect after risk or macro controls (MW2014, Hua2012, both abstract only).
  - NG and MHG: no root-specific multi-day evidence found (KRT2016 includes copper among its 26 commodities only in the
    pooled cross-section).
- Reason: The only multi-day mechanism with full-text support is liquidity provision. Impatient speculators push
  prices, and liquidity providers (hedgers) are paid through a later, partial reversal (KRT2016 (a); Grossman-Miller via
  KRT). If an extreme hourly move reflects liquidity demand rather than news, part of it should revert over days. But
  KRT measure the demand with CFTC position changes, not with price moves, and the reversal is small: 0.61% of a 6.77%
  move over 40 days (KRT2016 (b)). CP2020 report that a 2-sigma daily move continues to the close of its own day, then
  continues the next day in oil and reverses the next day in gold. Nothing found conditions on an hourly decile move,
  and nothing measures 5 or 20 days after such a move.
- Horizon: 1 day (CP2020); 1-20 days for the cross-sectional analog (KRT2016); 20 days continuation via monthly TSMOM
  (MOP2012, indirect). Neither 5 nor 20 is tested on this event.
- Magnitude: KRT2016 quintile spread (cross-sectional, hedger-bought minus hedger-sold): 0.21% in days 1-4 (t 3.04),
  0.30% in days 5-10 (t 3.62), 0.15% in days 11-20 (t 1.23), 67 bp over days 1-20, 26 commodities, 1994-2014; a
  long-short spread, not a one-contract per-event return. CP2020 print no next-day t-statistic in the quoted text;
  sample 2009-2020 on a MetaQuotes feed. No published per-event figure exists for MCL, NG, MGC or MHG after an hourly
  trigger. Decay: not documented.

### K1-vxnband-01 (MNQ) (fade of a one-sigma VXN band breach, VXN < 20 or >= 30)

- Strength: moderate (index-level evidence on the Nasdaq 100 itself: post-1999 next-day reversal, t -2.79, sample
  1999-2016 overlapping 2010-2024; but it is not conditioned on the band breach or the VXN bucket, the weekly figure is
  not significant, and the volatility-bucket evidence is an analog (cross-sectional stocks) or old (1995-2002)).
- Direction: reversal of the trigger-day move (the member's own fade side), more likely in the VXN >= 30 bucket than in
  the VXN < 20 bucket. For VXN >= 30, Giot2002 adds an unconditional positive drift over 1 and 5 days, which supports the
  fade only when it is a BUY (after a down-breach) and works against a SELL. For VXN < 20 the literature gives no
  reversal case: the LeBaron effect (BCR2008, secondary) implies weaker reversal at low volatility, and Giot2002 finds
  good 20- and 60-day long returns at low VXN in the bull market.
- Reason: Since index products became widespread, index returns reverse at short lags (BvD2019 (a)-(c)); the paper
  links this to the arbitrage between index products and the underlying stocks (BvD2019 abstract), that is, transitory
  price pressure that is undone over the next days. Reversal profits are the pay to liquidity providers, and they rise
  sharply with the VIX as constrained intermediaries withdraw (Nagel2012 (a), (b)). Serial correlation is lower when
  volatility is high (LeBaron effect, BCR2008). Together these predict that a large intraday move at VXN >= 30 is
  partly undone over the next 1-5 days. At VXN < 20 the case is weak.
- Horizon: 5 days (daily lags 1-5 and weekly AR(1) in BvD2019; 1- and 5-day forward returns in Giot2002). 20 days: no
  reversal evidence; Giot2002's 20-day results are mixed by regime.
- Magnitude: BvD2019 Nasdaq 100 daily AR(1) after March 1999 -0.065 (t -2.79); weekly AR(1) -0.074 (t -1.63);
  1999-03..2016-12; Sharpe 0.63 for a strategy against the negative MAC(5) across all indexes after 1999 (0.67 for the
  S&P 500 alone). Derived: a breach is at least VXN/16 percent (about 1.9% at VXN 30, 1.25% at VXN 20); at slope -0.065
  the implied next-day reversal of a 1.9% move is about 12 bp, before any VXN conditioning (the band breach is an
  intraday crossing, so the day's close-to-close move can be smaller). Nagel2012: +0.22 percentage points of daily
  reversal return per +16 points of annualized VIX (s.e. 0.02), US stocks, 1998-2010. Giot2002: no t-statistics for the
  n-day tables, 1995-2002. Decay: BvD2019 document a sign change around 1999 (positive before, negative after), so the
  sign is regime-dependent; nothing after 2016 is covered.

## 3. Query log

The full log with time bounds is mech_pages/M11_OVERNIGHT_REVERSAL_VOL/query_log.md (17 entries: 16 WebSearch calls, 1
OpenAlex API batch). The last two WebSearches (16, 17) added no new relevant source.

| # | Query (short) | Tool | Time (PDT) | Kept |
|---|---|---|---|---|
| 1 | Kang Rouwenhorst Tang Tale of Two Premiums reversal pdf | WebSearch | before 02:19:26 | KRT2016 |
| 2 | Baltussen van Bekkum Da Indexing serial dependence pdf | WebSearch | before 02:19:26 | BvD2019 |
| 3 | energy futures large daily price changes overreaction mean reversion | WebSearch | before 02:19:26 | MW2014 |
| 4 | "large price changes" commodity futures reversal "market factor" 26 | WebSearch | 02:19:30-02:21:27 | Hua2012 |
| 5 | index return autocorrelation conditional on VIX, reversal | WebSearch | 02:19:30-02:21:27 | none |
| 6 | Nasdaq-100 large daily moves, VXN, 5-day 20-day | WebSearch | 02:19:30-02:21:27 | none |
| 7 | Caporale Plastun one-day abnormal returns gold oil | WebSearch | 02:21:40-02:22:21 | CP2020 |
| 8 | Nagel Evaporating Liquidity VIX reversal pdf | WebSearch | 02:21:40-02:22:21 | Nagel2012 |
| 9 | intraday extreme returns commodity futures next-day multi-day | WebSearch | 02:21:40-02:22:21 | (CP2020 again) |
| 10 | Wang Yu 2004 trading activity price reversals futures pdf | WebSearch | 02:22:30-02:23:37 | Wang-Yu (not reached) |
| 11 | Overnight-Intraday Reversal Everywhere Kosowski pdf | WebSearch | 02:22:30-02:23:37 | none new (DKW2015 saved at E.10) |
| 12 | LeBaron 1992 volatility serial correlation | WebSearch | 02:22:30-02:23:37 | BCR2008 |
| 13 | extreme daily index futures returns, 5/20-day, VIX conditional | WebSearch | 02:23:40-02:24:12 | BK2025 |
| 14 | Cheng Kirilenko Xiong convective risk flows pdf | WebSearch | 02:23:40-02:24:12 | CKX2015 |
| 15 | OpenAlex title search (Wang-Yu, Mazouz-Wang, Hua-Wei) | curl API | 02:24:20-02:24:51 | OA lead (blocked) |
| 16 | settlement-period closing pressure reverses next days, commodity | WebSearch | 02:25:10-02:26:30 | none |
| 17 | gold copper futures weekly reversal after large intraday moves | WebSearch | 02:25:10-02:26:30 | none |

## 4. Not verified or not reached

- Wang and Yu (2004), JBF 28(6), 1337-1361 (weekly reversals in 24 US futures): no full text. A tcnh.ntt.edu.vn link
  returned a proxy page. Its claim appears here only as cited inside CP2020: [unverified].
- Mazouz and Wang (2014) full text: curl 403, Scrapling get and fetch hit Cloudflare (ORCA and Hull repository). Abstract only.
  Firecrawl was not tried: an abstract is enough for a null claim, and time was short.
- Hua (2012) dissertation PDF and Hua and Wei (2014): Cloudflare on UNO; no OA copy (OpenAlex). Abstract only.
- AgEcon record 169763: empty 202 by curl, 181 bytes by Scrapling, 403 by WebFetch. Not identified.
- CESifo WP 8445: client-challenge page (deleted); the same paper was read as the Brunel WP.
- LeBaron (1992), J. Business 65(2): not fetched; used only through BCR2008's abstract sentence.
- Bangsgaard and Kokholm (2025): abstract only; the horizon of the "subsequent reversal" is not stated there.
- BDLM2021 Table 11: the bond t+1 and currency t+1 cells come from a garbled PDF-to-markdown layout; the equity and
  commodity rows and the bond and currency t+2/t+3 cells follow the panel labels. Check them against the printed PDF
  (doi 10.1016/j.jfineco.2021.04.029) before any number goes into a verdict.
- No source tests the 5- or 20-day return after an hourly decile move (K4/K5), after a last-half-hour move beyond 3 days
  (H4), or after a VXN-band breach conditioned on the VXN bucket (K1). These gaps are absences in what I found, not
  findings of no effect.
- No over-budget WebSearch notice was seen (16 WebSearch calls used of the family's 60).
