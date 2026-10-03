# Stage E.10 research log: Reader 4, commodity term structure, carry, inventory and seasonal regimes (topics M1, M2)

- Reader: LitReader-Commodity-OpusHigh (model claude-opus-5-5, effort high)
- Start: 2026-10-02 22:33 PDT. End: 2026-10-02 22:55 PDT (stopped on saturation, not on budget).
- Records screened: about 520 (262 OpenAlex records from 14 queries, saved under
  reports/stage_e10_research/commodity/api/; about 255 WebSearch result links from 28 calls, many duplicates;
  6 single-DOI OpenAlex lookups).
- Sources logged: 22 (K9M-001 to K9M-022). Full text: 20 (19 studies plus K9M-018, a data-publication page,
  not a study). Abstract only: 2 (K9M-012, K9M-021). Blocked or not retrievable: 6 (WTI term-structure 2021,
  Szymanowska et al. 2014, Shao-Bhar-Colwell 2015, Martinez-Torro 2016, Mu 2004/2007, the CEPR copy of the
  Overnight Drift); see the rejection table.
- WebSearch calls used: 28 of 120. No over-budget notice was seen.
- Firecrawl: used once (2026-10-03T05:47:30Z approx., ageconsearch PDF aaea-1981-147 after curl returned an
  empty file and `scrapling extract fetch` returned a JavaScript challenge). The document turned out to be
  irrelevant (cross-hedging pork products, no return evidence); it was not saved and is listed under rejections.
- Semantic Scholar: NOT USED. The `.env` line `SEMANTIC_SCHOLAR_API_KEY=` holds a one-character value (line
  length 26 = 25-character name plus 1), so every keyed request returned `{"message":"Forbidden"}` (403) and an
  unkeyed probe returned 429. The key itself was never printed. OpenAlex plus WebSearch replaced it. The lead
  may want to fix the key for other readers.
- Stop reason per topic:
  - M1 (term structure, basis, carry; FX carry; rates curve; session split): saturation. The last 15+ records
    screened (OpenAlex m1e-m1g, WebSearch on Treasury session splits, three calls) added no new mechanism. Daily-
    horizon and session-split evidence for commodity carry and for Treasury carry was NOT found (a finding, below).
  - M2 (inventory, weather, harvest, livestock, heating season): saturation. The last 15+ records (livestock
    seasonals, crude inventory level, NG storage-level searches) added no new mechanism; livestock evidence is
    practitioner-only beyond the roll-return evidence in K9M-004.

Units used in reader's notes: sources report % per year or per month. A per-trade-date figure is the annual
figure / 252. Tick conversions are illustrative only, at assumed price levels stated in each note (MCL 70 $/bbl,
tick 0.01; NG 3.00 $/MMBtu, tick 0.001; MGC 2500 $/oz, tick 0.10; MHG 4.50 $/lb, tick 0.0005; ZC 450 c/bu,
tick 0.25 c; 6E 1.10, tick 0.00005; 6A 0.65, tick 0.00005). No program data was read.

---

## M1: term structure, basis, carry

### K9M-001 The Fundamentals of Commodity Futures Returns (theory of storage, inventories and risk premiums)
- Citation: Gorton, G. B., Hayashi, F., Rouwenhorst, K. G. (2007 working paper; published 2013). "The
  Fundamentals of Commodity Futures Returns." NBER Working Paper 13249 (DOI 10.3386/w13249); Review of Finance
  17(1), DOI 10.1093/rof/rfs019 (DOI from OpenAlex).
- Retrieval: curl of NBER PDF; reports/stage_e10_research/commodity/ghr_w13249.pdf (+ .txt). Full text.
- Mechanism: Low physical inventories raise the convenience yield (backwardation) and the required futures
  risk premium (theory of storage); the basis, prior returns and spot changes are price proxies for that state.
- Products and horizon: 31 commodities (energy, metals, grains, livestock, softs); monthly holding periods.
- Sample window: December 1969 (or later contract start) to December 2006; subsample December 1990 to
  December 2006.
- Market and frequency: US/UK futures; monthly returns and inventories.
- Cost assumptions: none stated in the passages read (gross returns).
- Quality tells: long sample, physical inventory data, nonparametric portfolio sorts, published in a top field
  journal; cross-sectional sorts relative to an equal-weighted index, not a single-product timing rule.
- Verified passages:
  - P-K9M-001-a (abstract): "Commodity futures risk premiums vary across commodities and over time depending on
    the level of physical inventories, as predicted by the Theory of Storage."
  - P-K9M-001-b (abstract): "Price measures, such as the futures basis, prior futures returns, and spot returns
    reflect the state of inventories and are informative about commodity futures risk premiums."
  - P-K9M-001-c (p. 17): "the Low Inventory portfolio has outperformed the High Inventory portfolios in 56% of
    the months between 1969 and 2006. The annualized average out-performance was 8.06 % (t = 3.19)."
  - P-K9M-001-d (Table 6 text): "the High Basis portfolio outperformed the equally-weighted index by 5.42%
    annualized (t = 3.98) while the Low Basis portfolio underperformed the average commodity by 4.82% (t =
    −3.44). The difference between the High and Low Basis portfolio was positive in 58% of the months and
    averaged 10.23% annualized (t = 3.73)."
  - P-K9M-001-e (Table 5 text): "The Low Inventory portfolio selects commodities with a high basis: the
    difference between the basis of the Low and High Inventory portfolios exceeds 12% (t = 14.51)."
- Numeric claims: low-minus-high inventory 8.06%/yr, t = 3.19, 56% of months (P-K9M-001-c); high-minus-low
  basis 10.23%/yr, t = 3.73, 58% of months (P-K9M-001-d).
- Conflicting evidence: K9M-003 (more frequent rebalancing lowers term-structure returns, P-K9M-003-c); K9M-002
  (commodity carry predicts negative price changes, coefficient below one, P-K9M-002-c).
- Reader's note: Fits K9 only as a state condition: "backwardation (or low inventory) in the top quintile of the
  product's trailing 250-date distribution" fires on about 20% of dates by D-pct and persists for weeks, so the
  weekly cap binds and the trip count can reach 40. Sign long; hold a full trade date (17:00 CT reopen to F;
  grains 19:00-07:43 or 08:30-13:18; livestock 08:30-13:03). Data items: the second-nearby contract's daily
  settlement (deferred-contract bars, flagged), or a public inventory series with a documented publication time
  (NG: K9M-018). No X matches (it is not roll- or expiry-keyed, so not X13, provided the slope is read on a
  constant-maturity basis and never across the program's roll dates). Magnitude: the 8-10% per year spreads are
  long-short across commodities; a single-leg excess return in the favourable state of roughly half that, 4-5%
  per year, is about 2 bp per trade date. At illustrative prices that is about 1.4 ticks MCL (M_X 13.0, G(0.4)
  56.8), 0.6 tick NG (M_X 7.2), 0.4 tick ZC (M_X 4.5). Far below M_X; the premium is a slow monthly drift, not
  a session move.

### K9M-002 Carry (cross-asset carry including commodities, currencies and Treasuries)
- Citation: Koijen, R. S. J., Moskowitz, T. J., Pedersen, L. H., Vrugt, E. B. (2013 working paper; published
  2018). "Carry." NBER Working Paper 19325 (DOI 10.3386/w19325). Journal of Financial Economics 127(2), 2018
  (journal DOI not verified in this session).
- Retrieval: curl of NBER PDF; reports/stage_e10_research/commodity/kmpv_carry_w19325.pdf (+ .txt). Full text.
- Mechanism: Carry (expected return if prices are unchanged; for commodities the front-to-next futures slope)
  predicts returns in the time series and cross section of every asset class.
- Products and horizon: global equities, bonds, currencies, commodities (24), US Treasuries (slope), credit,
  options; monthly.
- Sample window: commodities January 1980 to September 2012; other classes from August 1971 or later to
  September 2012.
- Market and frequency: futures and forwards; monthly.
- Cost assumptions: gross; not examined in the passages read.
- Quality tells: very broad, published, carry measured ex ante without a model; monthly only; commodity carry
  contaminated by seasonality (authors' own caveat).
- Verified passages:
  - P-K9M-002-a (abstract): "We find that carry predicts returns both in the cross section and time series for a
    variety of different asset classes that include global equities, global bonds, currencies, commodities, US
    Treasuries, credit, and equity index options."
  - P-K9M-002-b (Section on Table VI): "carry is a strong predictor of expected returns, with consistently positive
    and statistically significant coefficients on carry, save for the commodity strategy, which may be tainted by
    strong seasonal effects in carry for commodities. The carry1-12 strategy in Appendix C, which mitigates seasonal
    effects, is a ubiquitously positive and significant predictor of returns, even for commodities."
  - P-K9M-002-c (same section): "For commodities, the predictive coefficient is significantly less than one, so
    that when a commodity has a high spot price relative to its futures price, implying a high carry, the spot
    price tends to depreciate on average, thus lowering the realized return on average below the carry."
  - P-K9M-002-d (introduction): "a zero-cost carry trade portfolio, which goes long high carry securities and short
    low ones within each asset class earns an annualized Sharpe ratio of 0.7 on average"
  - P-K9M-002-e (data section): "The commodities sample covers 24 commodities futures dating as far back as January
    1980 (through September 2012)."
- Numeric claims: average within-class carry Sharpe 0.7 (P-K9M-002-d).
- Conflicting evidence: within the source, commodity carry is not significant in the pooled time-series test
  until seasonality is removed (P-K9M-002-b); realized return falls short of carry (P-K9M-002-c).
- Reader's note: The cleanest statement that carry is a daily accrual: under a coefficient of one an investor
  "earns the full carry", which for a futures contract is the curve slope accrued day by day. That makes the
  per-session expected move = annualized carry / 252 (or / 365 including weekends). A top-quintile carry of 20%
  per year is about 8 bp per trade date: about 6 ticks MCL at 70 $/bbl (M_X 13.0), 2.4 ticks NG (M_X 7.2),
  1.4 ticks ZC (M_X 4.5). Below M_X even in extreme states, and P-K9M-002-c says commodity carry is only
  partly earned. For Treasuries (slope carry) and FX (rate differential), carry per day is smaller still. No
  session split is given. Data items: second-nearby futures settles (curve), or for FX a policy-rate or deposit-
  rate series (public). X: none.

### K9M-003 Tactical allocation with momentum and term-structure signals (rebalancing-frequency test)
- Citation: Fuertes, A.-M., Miffre, J., Rallis, G. (2010). "Tactical allocation in commodity futures markets:
  Combining momentum and term structure signals." Journal of Banking and Finance 34(10) (DOI not verified in
  this session).
- Retrieval: curl from City, University of London open-access repository;
  reports/stage_e10_research/commodity/fmr_jbf2010.pdf (+ .txt). Full text (accepted manuscript).
- Mechanism: Long the most backwardated, short the most contangoed commodities (roll-yield sort); combined with
  12-month momentum.
- Products and horizon: 37 commodities; monthly holding; test of 2, 4, 7 and 10 rebalancings a month.
- Sample window: January 1, 1979 to January 31, 2007 (daily closing prices of nearby, second-nearby and distant
  contracts).
- Market and frequency: daily data, monthly portfolios.
- Cost assumptions: transaction-cost-adjusted for the rebalancing test.
- Quality tells: peer-reviewed; explicit test of shorter holding periods, which is the K9-relevant part.
- Verified passages:
  - P-K9M-003-a (abstract): "With significant annualized alphas of 10.14% and 12.66% respectively, the momentum
    and term structure strategies appear profitable when implemented individually."
  - P-K9M-003-b (Section 2): "The dataset from Datastream International and Bloomberg spans the period January, 1
    1979 to January, 31 2007. It consists of the daily closing prices on the nearby, second- nearby and distant
    contracts of 37 commodities"
  - P-K9M-003-c (rebalancing results): "A comparison across TS3,i with i=2, 4, 7 and 10 indicates that the more
    frequent the rebalancing, the lower the returns. This result is reinforced by the fact that larger transaction
    costs are incurred with more regular rebalancing which exacerbates the difference in net returns between TS1
    and TS3,i."
- Numeric claims: term-structure alpha 12.66% per year (P-K9M-003-a).
- Conflicting evidence: this source is itself the main conflict for a daily-horizon carry trade
  (P-K9M-003-c): refreshing the term-structure signal more often than monthly lowers returns.
- Reader's note: Direct evidence against using the curve signal at a short horizon: the value of the signal is
  slow. A K9 member keyed to a curve state can still be built (the state persists), but the expected session
  move is the slow drift of K9M-001/002, about 2-5 bp per trade date. X: none. Data item: second-nearby settles.

### K9M-004 The Strategic and Tactical Value of Commodity Futures (roll returns)
- Citation: Erb, C. B., Harvey, C. R. (2006). "The Strategic and Tactical Value of Commodity Futures." Financial
  Analysts Journal 62(2) (DOI 10.2469/faj.v62.n2.4084, seen in a search-result URL); NBER Working Paper 11222.
- Retrieval: curl of NBER PDF; reports/stage_e10_research/commodity/erbharvey_w11222.pdf (+ .txt). Full text.
- Mechanism: The cross-section of commodity futures excess returns is explained mostly by the roll return
  (term-structure shape), not by spot returns.
- Products and horizon: individual commodity futures including copper, heating oil, live cattle, corn, wheat,
  gold; long-run averages.
- Sample window: tables run from December 1969 (index) to May 2004; Figure 6's exact window was not located by
  grep.
- Market and frequency: monthly.
- Cost assumptions: none.
- Quality tells: widely cited practitioner-academic paper; descriptive cross-section of long-run averages.
- Verified passages:
  - P-K9M-004-a (Section 3.4.3): "Three commodities (copper, heating oil, and live cattle) had, on average,
    positive roll returns and positive excess returns. Corn, wheat, silver, gold and coffee had, on average,
    negative roll returns and negative excess returns."
  - P-K9M-004-b (same): "The almost 9% excess return difference between the positive roll return portfolio and the
    negative roll return portfolios consists of a 7.5% difference in roll returns and a 1.4% difference in spot
    returns. Roll returns explain 91% of the cross-sectional variation of commodity futures returns in Figure 6."
    (the source has a footnote marker "xix" after "returns" that is omitted here)
  - P-K9M-004-c (Section 3.4.3): "it is not surprising that the term structure of futures prices is a significant
    driver of the cross-section of commodity futures returns."
- Numeric claims: 9% per year spread, 7.5% from roll (P-K9M-004-b).
- Conflicting evidence: the same paper finds an equal-weighted long-only portfolio earned about zero excess return
  over 25 years (abstract; not quoted as a passage here).
- Reader's note: Context for livestock (live cattle positive roll) and grains/gold (negative roll). The 7.5% per
  year roll difference is about 3 bp per trade date, spread over the full 24-hour trade date with no session
  split. Below M_X on every exposure. X: none.

### K9M-005 Basis-momentum
- Citation: Boons, M., Porras Prado, M. (2019). "Basis-Momentum." Journal of Finance 74(1), 239-279. DOI
  10.1111/jofi.12738. Working-paper title: "Basis-momentum in the futures curve and volatility risk."
- Retrieval: curl of NBER conference PDF (conference.nber.org/conf_papers/f89296/f89296.pdf);
  reports/stage_e10_research/commodity/boons_prado_bm.pdf (+ .txt). Full text (working paper).
- Mechanism: The difference between 12-month momentum in first-nearby and second-nearby futures (average
  curvature plus slope changes of the curve) predicts nearby (spot-premium) and spreading (term-premium) returns;
  explained as maturity-specific price pressure and volatility risk.
- Products and horizon: 21 commodities (32 in the appendix); also currencies; monthly.
- Sample window: July 1959 to February 2014 (portfolio results August 1960 to February 2014).
- Market and frequency: monthly.
- Cost assumptions: "These returns survive estimates of transaction costs based on the evidence in Marshall et
  al. (2012)." (introduction).
- Quality tells: top journal; pre-registered nothing; signal built from two contract maturities.
- Verified passages:
  - P-K9M-005-a (abstract): "We propose a new commodity-return predictor related to the slope and curvature of the
    futures curve: basis-momentum. Basis-momentum strongly outperforms benchmark characteristics, such as basis and
    momentum, in predicting commodity spot and term premiums in the time series and cross section."
  - P-K9M-005-b (introduction): "sorting commodities on basis-momentum leads to an economically and statistically
    large average annualized difference between the high and low portfolio of 18.38% (t-statistic of 6.73) in
    nearby returns and 4.08% (t-statistic of 6.43) in spreading returns."
  - P-K9M-005-c (introduction): "a standard deviation increase in basis-momentum predicts a large and significant
    increase in monthly nearby (spreading) return of 0.85% (0.2%)."
  - P-K9M-005-d (introduction): "Basis-momentum is measured as the difference between momentum in first- and
    second- nearby futures strategies."
- Numeric claims: 18.38%/yr HML nearby, t = 6.73 (P-K9M-005-b); +0.85% per month per SD (P-K9M-005-c).
- Conflicting evidence: none inside the source; K9M-003's frequency result applies by analogy.
- Reader's note: Condition: basis-momentum of the product in its top (bottom) quintile of the trailing 250 dates
  (D-pct), long (short); fires about 20% of dates and persists. One SD gives +0.85% per month, about 4 bp per
  trade date: about 3 ticks MCL (M_X 13.0), 1.3 ticks NG (M_X 7.2), 0.7 tick ZC (M_X 4.5). Below M_X. Data
  item: 12 months of first- and second-nearby settlement returns (deferred-contract bars, flagged). Overlaps
  O2's TSMOM (12-month momentum) in its inputs but differs in mechanism (curve shape, not trend). X: none; note
  the borderline "daily-scale TSMOM" ruling in the design target if the lead treats it as momentum.

### K9M-006 Exploiting the dynamics of commodity futures curves (daily-rebalanced slope strategy)
- Citation: Bianchi, R. J., Fan, J. H., Miffre, J., Zhang, T. (2023). "Exploiting the dynamics of commodity
  futures curves." arXiv:2308.00383, version July 16, 2023 (journal version not verified in this session).
- Retrieval: curl of arXiv PDF; reports/stage_e10_research/commodity/arxiv_2308.00383.pdf (+ .txt). Full text.
- Mechanism: Nelson-Siegel level, slope and curvature estimated daily on each curve; strategies bet on one-day
  continuation of recent slope or curvature changes (long-short across and within curves).
- Products and horizon: commodity futures panel following Szymanowska et al.; one-day holding, daily rebalancing.
- Sample window: January 1992 to June (year in the grepped line cut off; paper version July 2023).
- Market and frequency: daily settlement prices.
- Cost assumptions: transaction costs estimated (TC1, TC3, following Szakmary et al. and Paschke et al.); daily
  turnover 1.17 for S.
- Quality tells: one of the few genuinely daily-horizon curve papers; strategy is a spread (long-short legs on
  curve positions), not an outright directional bet.
- Verified passages:
  - P-K9M-006-a (Section 3): "Irrespective of the strategy considered, the NS model is estimated daily. The
    strategies are set up at the end of day t and implemented for one day."
  - P-K9M-006-b (results): "the S strategy based on the change in the slope beta delivers an annualized mean excess
    return of 1.77% that is highly significant (t-statistic=7.23) and a Sharpe ratio of 1.41."
  - P-K9M-006-c (results): "The annualized standard deviation of the C strategy equals 0.55% versus 1.25% for the
    S strategy and 6.30% for the L strategy."
  - P-K9M-006-d (Section 4.3): "Our NS strategies are trading intensive since they assume daily rebalancing."
- Numeric claims: 1.77%/yr, t = 7.23, Sharpe 1.41 (P-K9M-006-b); volatility 1.25%/yr (P-K9M-006-c).
- Conflicting evidence: the parallel-shift (L) strategy, the outright-like one, is not reported as significant in
  the lines read ("surprising given our previous conclusion" context); not quoted beyond P-K9M-006-c.
- Reader's note: Daily-horizon curve information exists but is tiny: 1.77% per year is under 1 bp per trade date,
  and it is a within-curve spread (two positions), which breaks (b)2 (one position). Not a K9 shape. Useful only as
  evidence that curve-shape signals carry daily information in spreads, not in outright session moves. X: none.

### K9M-007 Relative Basis and the Expected Returns of Commodity Futures
- Citation: Gu, M., Kang, W., Lou, D., Tang, K. (draft July 2024; FMG Discussion Paper 942, November 2025).
  "Relative Basis and the Expected Returns of Commodity Futures." LSE Financial Markets Group.
- Retrieval: curl; reports/stage_e10_research/commodity/fmg_dp942.pdf (+ .txt). Full text.
- Mechanism: Near-term basis minus distant basis purges persistent storage and financing costs and tracks
  inventory changes better than the basis; predicts commodity futures returns.
- Products and horizon: 24 commodities; next month and next quarter.
- Sample window: January 1979 to December 2019 (Table text).
- Market and frequency: monthly.
- Cost assumptions: not examined.
- Quality tells: recent, strong authors; monthly only; needs three contract maturities.
- Verified passages:
  - P-K9M-007-a (abstract): "Our measure is the difference between the traditional near-term basis and a similarly
    defined distant basis."
  - P-K9M-007-b (abstract): "Relative basis is closely tied to changes in physical inventories and dominates
    traditional basis in forecasting commodity futures returns."
  - P-K9M-007-c (table note): "We report the returns of these three portfolios, as well as the return difference
    between the portfolios with the highest and lowest ranking variables (P3-P1), in the next month and one
    quarter. The sample period is January 1979 to December 2019."
- Numeric claims: none extracted (portfolio magnitudes are in tables not grepped).
- Conflicting evidence: none located.
- Reader's note: A better state variable for C-STORAGE (below), but monthly. Data item: three contract
  maturities' settles (deferred-contract bars, flagged). X: none.

### K9M-008 Convenience Yield Risk
- Citation: Prokopczuk, M., Symeonidis, L., Wese Simen, C., Wichmann, R. (January 29, 2023). "Convenience Yield
  Risk." Energy Economics, forthcoming at that date (DOI not verified).
- Retrieval: curl from University of Essex repository; reports/stage_e10_research/commodity/essex_cyr.pdf
  (+ .txt). Full text.
- Mechanism: Commodities whose convenience yield is more volatile (higher convenience-yield risk) earn higher
  subsequent returns.
- Products and horizon: 27 commodities; monthly signals built from daily data.
- Sample window: July 1959 to December 2018 (some variables from 1986).
- Market and frequency: monthly.
- Cost assumptions: not examined.
- Verified passages:
  - P-K9M-008-a (abstract): "a strategy that opens long positions in commodity markets with a higher than median
    CYR signal and sells the remaining commodities yields an average return of 6.93% per year."
  - P-K9M-008-b (data): "We use a cross-section of 27 commodities spanning the period from July 1959"
  - P-K9M-008-c (table note): "The sample period is from July 1959 to December 2018."
- Numeric claims: 6.93% per year long-short (P-K9M-008-a).
- Reader's note: Cross-sectional, monthly, median split (fires 50% of the time). Not a K9 shape; context for the
  storage state family. About 3 bp per trade date long-short. X: none.

### K9M-009 Futures basis, inventory and commodity price volatility
- Citation: Symeonidis, L., Prokopczuk, M., Brooks, C., Lazar, E. (2012). "Futures basis, inventory and commodity
  price volatility: An empirical analysis." MPRA Paper 39903 (July 4, 2012); Economic Modelling 2012, DOI
  10.1016/j.econmod.2012.07.016 (DOI from OpenAlex).
- Retrieval: curl from MPRA; reports/stage_e10_research/commodity/mpra_39903.pdf (+ .txt). Full text.
- Mechanism: Low inventory goes with backwardated curves and with higher price volatility.
- Products and horizon: 21 commodities including NYMEX natural gas; inventory at weekly or monthly frequency
  (EIA for energy).
- Sample window: 1993-2011.
- Verified passages:
  - P-K9M-009-a (abstract): "Low (high) inventory is associated with forward curves in backwardation (contango),
    as the theory of storage predicts. Second, we show that price volatility is a decreasing function of inventory
    for the majority of commodities in our sample. This effect is more pronounced in backwardated markets."
  - P-K9M-009-b (Section 3): "The annualized daily volatility of 47.39% for natural gas is the highest among"
- Numeric claims: NG annualized daily volatility 47.39% (P-K9M-009-b).
- Reader's note: Not directional. It says the storage state raises the size of session moves, which raises the
  noise a K9 storage member must overcome; the volatility side belongs to the Regime reader. Context only.

### K9M-010 FX Premia Around the Clock (carry and dollar carry earned in U.S. hours)
- Citation: Krohn, I., Mueller, P., Whelan, P. (December 2018 version, first draft February 2018). "FX Premia
  Around the Clock." Preliminary paper on the 2019 AEA (ASSA) programme
  (topcat.aeaweb.org/conference/2019/preliminary/paper/QQ73KSH8).
- Retrieval: curl of the AEA URL (served a PDF with an HTML name; renamed);
  reports/stage_e10_research/commodity/kmw_fxpremia_aea2019.pdf (+ .txt). Full text. An AUT-hosted copy was
  behind a Cloudflare challenge (scrapling get failed).
- Mechanism: Long-foreign-currency, carry (HML) and dollar-carry returns accrue mainly during New York hours
  (08:00-17:00 ET); the overnight window is flat or negative.
- Products and horizon: G10 currencies vs USD, spot quotes and CME futures; intraday vs overnight split of daily
  returns; carry portfolios formed monthly.
- Sample window: January 1994 to December 2017 (spot); futures check 2005-2017 per the text.
- Market and frequency: tick/5-minute spot (TRTH), CME front-month futures.
- Cost assumptions: the abstract says the result "may be exploitable by investors that are able to benefit from
  lower than average transaction costs."
- Quality tells: high-frequency data, futures robustness check, later published in a different framing (K9M-011);
  preliminary version, "please do not cite or circulate without permission" on the title page.
- Verified passages:
  - P-K9M-010-a (abstract): "we document that 75% of the HML portfolio returns from a standard carry trade
    strategy and almost 80% of dollar carry returns are generated during the U.S. trading day."
  - P-K9M-010-b (Section on decomposition): "we define the beginning and ending of the intraday period as 8:00
    a.m. and 5:00 p.m. (EST), respectively."
  - P-K9M-010-c (same): "the overnight window is defined as the remaining period between 5:00 p.m. on day d and
    8:00 a.m. on day d + 1."
  - P-K9M-010-d (Carry Trade Revisited): "For our sample, 75% of the total carry return or 3.25% per year are earned
    during the intraday period. The remaining 25% or 1.12% per year are earned during the overnight period although
    the return by itself is not statistically significant."
  - P-K9M-010-e (same): "For the high interest rate currency portfolios, the returns range between 6% for the
    intraday and −3.05% for the overnight period, whereas the spread is slightly smaller for the low interest rate
    currency portfolios with 2.74% and −4.17, respectively."
  - P-K9M-010-f (Dollar Carry Decomposition): "Table IV shows that intraday dollar carry trade return is 2.86%
    (t-stat: 2.42). This is equivalent to almost 80% of the dollar carry trade strategy based on close-to-close
    returns."
  - P-K9M-010-g (Futures Returns): "The 'W' shaped return pattern in the unconditional dollar portfolio is clearly
    visible." (the source uses typographic quotes around W)
  - P-K9M-010-h (data): "Our sample period spans January 1994 to December 2017"
- Numeric claims: carry intraday 3.25%/yr vs overnight 1.12%/yr (P-K9M-010-d); high-yield portfolio +6% intraday,
  -3.05% overnight (P-K9M-010-e); dollar carry intraday 2.86%, t = 2.42 (P-K9M-010-f).
- Conflicting evidence: K9M-011 (published version reframes the intraday pattern around benchmark fixes, X9);
  K9M-012 (UIP holds over short intraday windows away from the rollover).
- Reader's note: The only located source that splits a carry premium by session, and it says the premium is a
  day-session (07:00-16:00 CT) phenomenon. As a K9 rule: long the high-rate currency futures (for example 6A, 6N)
  or short low-rate (6J, 6S) in the US session only. But the condition is the sign of a monthly rate differential,
  which holds on almost every date, so it trades daily unless a rarity condition is added (none in the source; the
  lead could pair it with a D-pct extreme of the differential, which the source does not test). Magnitude: high-
  yield intraday 6% per year is about 2.4 bp per trade date, about 3 ticks of 6A at 0.65 (M_X 7.4, G(0.4) 30.0);
  HML intraday 3.25% per year is about 1.3 bp, about 3 ticks of 6E-equivalent at 1.10 (M_X 6.9). Below M_X.
  Data item: a public daily interest-rate differential series with documented publication time (or the implied
  differential from two FX futures maturities). Closest X: X9 (the intraday U.S.-hours appreciation sits after the
  London 4 p.m. fix, see K9M-011) and the Overnight reader's session-drift topic (O1). Route a copy to the lead
  for the X9 borderline call.

### K9M-011 Foreign Exchange Fixings and Returns around the Clock (published version)
- Citation: Krohn, I., Mueller, P., Whelan, P. (2024). "Foreign Exchange Fixings and Returns around the Clock."
  Journal of Finance 79(1). DOI 10.1111/jofi.13306 (from OpenAlex).
- Retrieval: Warwick WRAP accepted manuscript via OpenAlex location;
  reports/stage_e10_research/commodity/kmw_fixings_2024.pdf (+ .txt). Full text.
- Mechanism: The dollar appreciates ahead of the Tokyo, ECB and London fixes and reverts afterward; across the day
  foreign currencies appreciate in U.S. hours and depreciate overnight.
- Sample window: January 1999 to December 2019.
- Verified passages:
  - P-K9M-011-a (introduction): "the U.S. dollar gradually appreciates against all currencies ahead of the three
    major currency fixes in Tokyo, Frankfurt (the ECB fix) and London, and reverts thereafter."
  - P-K9M-011-b (Section B): "Overall, all currencies apart from the yen appreciate during the U.S. intraday period
    and depreciate overnight."
  - P-K9M-011-c (Section B): "We begin our analysis by plotting the average cumulative 5-minute log returns from
    17:00 ET on one day until 17:00 ET on the next day for the sample period January 1999 to December 2019."
  - P-K9M-011-d (carry comparison): "While carry trades are profitable but have fat tails and are heavily exposed
    to crash risk, our reversal port- folios generate positive returns with fat tails but generally positive
    skewness."
- Conflicting evidence: relative to K9M-010, the published framing attributes the intraday pattern to fixes
  (X9) and no longer reports the carry-by-session table in the lines grepped.
- Reader's note: The session asymmetry survives publication (P-K9M-011-b) but its mechanism is fix-related, which
  is X9 territory. A K9 FX-carry member would have to show its sign comes from the rate differential, not the fix
  cycle. Unconditional session drift belongs to the Overnight reader. X9 borderline.

### K9M-012 Uncovered interest parity: it works, but not for long (abstract only)
- Citation: Chaboud, A. P., Wright, J. H. (2005). "Uncovered interest parity: it works, but not for long."
  Journal of International Economics 66(2), 349-362; Federal Reserve Board International Finance Discussion Paper
  752.
- Retrieval: EconPapers abstract page (curl); reports/stage_e10_research/commodity/cw_econpapers.html (+ .txt).
  Abstract only. Federal Reserve PDF URLs returned "Page not Found"; NBER w11077 (tried first) is a different
  paper (Chinn-Meredith) and was discarded.
- Mechanism: Interest accrues discretely at the daily rollover; over intraday windows that span the rollover, UIP
  holds; the carry risk premium shrinks over short intervals.
- Verified passages:
  - P-K9M-012-a (abstract): "because no interest is paid on intradaily positions and interest is instead paid
    discretely at the point when a position is rolled over from one day to the next, the size of the interest
    differential remains fixed over any interval that covers the time of the discrete interest payment."
  - P-K9M-012-b (abstract): "We replicate the rejection of the uncovered interest parity hypothesis with daily data,
    but find results that are consistently much more supportive of the uncovered interest parity hypothesis over
    short windows of intradaily data that span the time of the discrete interest payment."
- Conflicting evidence: this is the conflict for K9M-010 at the sub-daily scale: in spot FX, the differential is
  paid at the rollover and offset by the spot move around it; the carry premium is a daily-and-longer phenomenon.
- Reader's note: In futures the differential is built into the futures price, so the rollover point does not
  exist; the session question reduces to where the spot risk premium accrues (K9M-010). Context; abstract only.

No Treasury session-split source was found; see "Gaps" below.

---

## M2: inventory, weather, harvest and seasonal regimes

### K9M-013 Common Factors in Return Seasonalities (commodity same-calendar-month seasonality)
- Citation: Keloharju, M., Linnainmaa, J. T., Nyberg, P. (2014). "Common Factors in Return Seasonalities." NBER
  Working Paper 20815 (published 2016 as "Return Seasonalities," Journal of Finance; journal DOI not verified).
- Retrieval: curl of NBER PDF; reports/stage_e10_research/commodity/kln_seasonal_w20815.pdf (+ .txt). Full text.
- Mechanism: Assets with high historical returns in a given calendar month earn high returns in the same month
  later; applied to 24 commodity futures.
- Products and horizon: 24 commodity futures; monthly, cross-sectional (2-3 long, 2-3 short).
- Sample window: January 1970 to July 2011 (commodities).
- Verified passages:
  - P-K9M-013-a (Section on other asset classes): "Our commodity- return data consist of 24 commodity futures
    assembled from a variety of sources and markets and cover the period January 1970 through July 2011."
  - P-K9M-013-b (same): "the average return on a long-short strategy that trades on seasonalities in commodity
    returns is 0.93% per month (t-value = 1.93). The average return is −0.22% (t-value = −0.58) when the
    long-short strategy instead chooses commodities based on their historical other- calendar-month returns."
  - P-K9M-013-c (same): "Panel C shows that seasonalities in both commodity returns and country indexes exist also
    in non-January data."
- Numeric claims: 0.93% per month, t = 1.93 (P-K9M-013-b).
- Conflicting evidence: K9M-014 (no robust out-of-sample seasonal gains 2016-2024).
- Reader's note: Weak (t below 2), cross-sectional and monthly. A K9 version (long a product during its
  historically strongest calendar month) would trade every date of that month, so it needs the weekly cap and
  fires about 8% of dates per product-month. 0.93% per month long-short is about 4.4 bp per trade date. Below
  M_X. Closest X: none (X12 is turn-of-month, a different mechanism), but the Calendar reader owns calendar effects;
  the lead may route it there.

### K9M-014 Seasonal Trading in Commodity Futures (out-of-sample test, conflicting)
- Citation: Kosch, R., Forsberg, R. (September 2026). "Seasonal Trading in Commodity Futures: Evidence from
  Regression and Singular Spectrum Signals." arXiv:2609.12227v1.
- Retrieval: curl of arXiv PDF; reports/stage_e10_research/commodity/arxiv_2609.12227.pdf (+ .txt). Full text.
- Mechanism tested: dummy-variable regression and SSA seasonal signals on monthly returns of 15 liquid commodity
  futures; rolling 10-year estimation; out-of-sample 2016-2024 with costs.
- Verified passages:
  - P-K9M-014-a (abstract): "Using monthly delivery- avoidance returns for 15 liquid commodity futures, the models
    are estimated on rolling ten-year windows and evaluated from 2016 to 2024 with transaction costs, an
    equal-weight long benchmark, and Maximum Entropy Bootstrap (MEB) assessment."
  - P-K9M-014-b (abstract): "None of the 18 approximate paired MEB Sharpe tests rejects after within- family Holm
    adjustment."
  - P-K9M-014-c (abstract): "The evidence does not establish robust benchmark outperformance and shows that model
    performance varies materially across market subperiods."
- Reader's note: Strong conflicting evidence for any calendar-month commodity seasonal member: out of sample with
  costs, no seasonal model beats a long benchmark. New preprint (not peer-reviewed). X: none.

### K9M-015 Seasonality in Agricultural Commodity Futures (seasonality priced into the curve)
- Citation: Sørensen, C. (1999; published 2002 in the Journal of Futures Markets, not verified here).
  "Seasonality in Agricultural Commodity Futures." Copenhagen Business School, Department of Finance Working Paper
  1999-14.
- Retrieval: curl from CBS research portal; reports/stage_e10_research/commodity/sorensen_cbs.pdf (+ .txt). Full
  text.
- Mechanism: Deterministic seasonality in corn, soybean and wheat spot prices shows up in the term structure of
  futures prices; risk premia modelled as constant.
- Sample window: weekly CBOT data 1972-1997.
- Verified passages:
  - P-K9M-015-a (abstract): "The continuous time dynamics of (log-) commodity prices are modeled as a sum of a
    deterministic sea- sonal component, a non-stationary state-variable, and a stationary state-variable."
  - P-K9M-015-b (abstract): "the Kalman lter methodology is used to estimate the model parameters for corn futures,
    soy- bean futures, and wheat futures based on weekly data from the Chicago Board of Trade for the period
    1972-1997." (ligature "fi" lost in extraction)
  - P-K9M-015-c (introduction): "at a given date the corn futures prices will usually be higher for delivery in May
    and July than for delivery in March, September, or December."
- Reader's note: Conflicting in principle: predictable seasonality in spot prices is already in the futures curve,
  so a single futures contract need not drift seasonally; a seasonal futures drift requires a seasonal risk
  premium (K9M-019, K9M-016). X: none. Context.

### K9M-016 Risk premia and seasonality in commodity futures (heating oil)
- Citation: Hevia, C., Petrella, I., Sola, M. (April 2016). "Risk premia and seasonality in commodity futures."
  Bank of England Staff Working Paper 591.
- Retrieval: curl from bankofengland.co.uk; reports/stage_e10_research/commodity/boe_seasonality_2016.pdf (+
  .txt). Full text.
- Verified passages:
  - P-K9M-016-a (abstract): "We estimate the model using heating oil futures prices over the period 1984–2012. We
    find strong evidence of stochastic seasonality in the data."
  - P-K9M-016-b (abstract): "We analyse risk premia in futures markets and discuss two traditional theories of
    commodity futures: the theory of storage and the theory of normal backwardation. The data strongly supports the
    theory of storage."
  - P-K9M-016-c (introduction): "the contribution of seasonal shocks to risk premia is relatively small."
- Reader's note: Heating oil is not a traded exposure; logged as evidence that seasonal shocks contribute little
  to risk premia (P-K9M-016-c), which weighs against heating-season members on NG by analogy. Context only.

### K9M-017 Extreme weather forecasts and a natural gas futures risk premium
- Citation: Monteux, M., Arcuri, M. C., Gandolfi, G., Caselli, S. (2025). "Can extreme weather forecasts lead to
  a risk premium? Evidence of a non-linear response in U.S. natural gas futures." North American Journal of
  Economics and Finance 80, 102494 (DOI not verified).
- Retrieval: curl from Bocconi IRIS repository; reports/stage_e10_research/commodity/caselli_ng_weather.pdf (+
  .txt). Full text.
- Mechanism: Colder-than-normal NOAA GEFS 1-2 week temperature forecasts (bottom decile or quintile of the
  forecast deviation from seasonal norms) are followed by a premium in the front NG contract relative to the second,
  captured by long NG1 / short NG2 held 5 business days; observed (realized) temperatures carry no premium.
- Products and horizon: NYMEX Henry Hub NG1 and NG2; settlement-to-settlement daily returns; 5-business-day holds.
- Sample window: daily data April 4, 1990 to July 31, 2019 (forecast dataset from 1 January 1987).
- Market and frequency: daily settlements (14:30 EST), NOAA forecasts released 00:00 UTC.
- Cost assumptions: not found in the grepped lines.
- Quality tells: explicit look-ahead discussion with forecast release times; spread strategy, not outright; many
  thresholds and horizons shown (monotone pattern claimed); CAGR compared with the S&P 500 rather than a
  risk model.
- Verified passages:
  - P-K9M-017-a (abstract): "Using data on hourly frequency observed temperature and daily forecasted temperatures
    across major U.S. metropolitan areas over a 30-year period, we analyze the relationship between the daily
    returns of the NYMEX Henry Hub Natural Gas futures and U.S. weather fluctuations."
  - P-K9M-017-b (summary bullets): "Extreme weather events are classified as those within the bottom 10 % of
    temperature forecast deviations from seasonal norms, a threshold shown in Section 4 to be flexible without loss
    of statistical significance;"
  - P-K9M-017-c (Section 4.3): "We evaluate the effectiveness of a spreading strategy that involves taking a short
    NG2 position along with a long NG1 position every business day when the "event" temperature differentials
    (actual/observed and forecasted) from seasonal norms fall below a certain decile threshold. The short NG2 and
    long NG1 positions are held for a period of 5 business days following the occurrence of the weather event"
    (source uses typographic quotes)
  - P-K9M-017-d (Section 4.3): "Table 5 shows that a spreading strategy based on actual (observed) U.S.
    temperatures does not produce any abnormal return, even for extreme cold conditions (<10 % percentile)."
  - P-K9M-017-e (Section 3.4): "NOAA weather forecasts in our dataset are released at 00:00 Coordinated Universal
    Time (UTC)."
  - P-K9M-017-f (Section 3.4): "we computed returns from settlement price to settlement price, which is set at 14:30
    EST. To compute the spreading strategy returns described in the next section, we use t + 1 returns, meaning that
    we leave a 19 ½ hours of time between the weather forecast signal and the start of the computation of the
    return of the trades that compose the spreading strategy."
  - P-K9M-017-g (Section 3.3): "the analysis shows that NG1 returns are linearly dependent on 1-week ahead U.S.
    forecasted temperatures, but they do not appear to be dependent on U.S. realized temperatures levels (at 14:00
    EST)."
  - P-K9M-017-h (Section 3.3): "Although statistically significant, the regression shows low predictive power with
    an R2 of 4.7 %"
  - P-K9M-017-i (results): "the risk premia strategies (which utilize only forecasted U.S. temperatures as a trading
    signal) for "extreme events" (10th percentile) had a Sharpe ratio of 1.3"
  - P-K9M-017-j (results): "the CAGR of the spreading strategy based on 2-week forecasted temperatures was 12 % over
    the period"
- Numeric claims: spread CAGR 12% (P-K9M-017-j), Sharpe 1.3 at the 10th percentile (P-K9M-017-i); outright NG1
  regression R2 4.7% (P-K9M-017-h).
- Conflicting evidence: realized temperatures carry no premium (P-K9M-017-d); the outright regression explains
  little (P-K9M-017-h). The annual return table shows activity concentrated in a few winter months (not quoted).
- Reader's note: The most K9-like M2 candidate found, but not as published. Published form: a two-leg calendar
  spread held 5 days, which breaks (b)2 (one position) and the inside-one-trade-date rule. A K9 adaptation: long NG
  (outright, front) for one trade date from the 17:00 CT reopen to 15:08 CT after a bottom-quintile 1-2 week
  forecast deviation. Look-ahead: the 00:00 UTC run is 18:00 CT in winter (19:00 EST, P-K9M-017-e), after the
  17:00 CT reopen, so the entry is the first bar after the forecast is public (plus a dissemination lag the lead
  must fix) on that trade date, or the following trade date's 17:00 CT reopen; never the 17:00 CT bar of the same
  evening. Frequency: bottom quintile of trailing deviations fires about 20% of dates (D-pct), winter-
  heavy. Magnitude: not available for an outright one-day hold; the spread's 12% per year over a fraction of dates
  is not convertible to NG ticks from the passages read. Data item: NOAA GEFS forecast series (public, free, with
  the 00Z release time documented) that the program does not hold: flag for E.11/E.12. X: none (weather forecast
  state, not keyed to the EIA Thursday release, so not X7; keep entry off Thursday 09:30 CT windows to stay clear).

### K9M-018 EIA Weekly Natural Gas Storage Report schedule (publication time of an inventory state variable)
- Citation: U.S. Energy Information Administration. "Weekly Natural Gas Storage Report Schedule."
  https://ir.eia.gov/ngs/schedule.html (fetched 2026-10-03).
- Retrieval: curl; reports/stage_e10_research/commodity/eia_wngsr_schedule.html (+ .txt). Full page.
- Verified passages:
  - P-K9M-018-a: "The standard release time and day of the week will be at 10:30 a.m. eastern time on Thursdays
    with the following exceptions. All times are eastern."
- Reader's note: Documents the publication time needed for an NG storage-level state (for example storage below
  its 5-year average). Look-ahead rule: the level of week w is usable from the first bar after Thursday 09:30 CT;
  a K9 member using it must enter on a later trade date (for example the Sunday or Monday 17:00 CT reopen), never
  in the Thursday release window, or it becomes X7. No academic source located that shows the storage-level state
  signs a session drift (searches K9M-related, see rejections); only K9M-001's monthly cross-section and K9M-009's
  curve/volatility link.

### K9M-019 The Weather Risk Premium in New-Crop Corn Futures Prices
- Citation: Janzen, J. (June 2, 2021). "The Weather Risk Premium in New-Crop Corn Futures Prices." farmdoc daily
  (11):88, University of Illinois at Urbana-Champaign.
- Retrieval: curl of farmdoc PDF; reports/stage_e10_research/commodity/fdd_corn_weather.pdf (+ .txt). Full text.
- Mechanism: New-crop December corn futures carry a growing-season weather risk premium that decays into
  harvest when no major weather event occurs.
- Products and horizon: CBOT December corn; first week of June to week of December 1.
- Sample window: 2000-2020.
- Quality tells: extension article by an academic (university series, stated sample and method), descriptive
  averages, no significance test in the lines read.
- Verified passages:
  - P-K9M-019-a: "December corn futures prices were on average 12% higher in the first week of June than in the
    week of December 1 during the period 2000-2020. This behavior is consistent with (but not definitive evidence
    for) a weather risk premium in new-crop corn futures prices."
  - P-K9M-019-b: "If the growing season progresses without a major weather event, new-crop prices are expected to
    fall."
  - P-K9M-019-c: "Much higher prices may be necessary to ration scarce supply, especially when existing inventories
    are not available to buffer the price impact of lower production."
- Numeric claims: 12% average decline June to December, 2000-2020 (P-K9M-019-a).
- Conflicting evidence: K9M-020 (no premium in soybeans); K9M-021 (passive short not attractive risk-adjusted).
- Reader's note: Condition = season (early June to harvest) for new-crop December corn (a deferred contract in
  June-August while July/September are nearby: data item, the December contract's bars). Sign short. Hold one
  grain session (08:30-13:18 CT or 19:00-07:43 CT). Frequency: the season alone covers about 25 weeks a year, so
  the weekly cap gives up to about 50 trips a year; a rarer version keys on low carryout (K9M-022). Magnitude: 12%
  over about 125 trade dates is about 10 bp per trade date (24-hour), about 1.8 ticks ZC at 450 c (M_X 4.5,
  G(0.4) 11.5). Below M_X; and the decline is front-loaded (peak in early June) only on average. Closest X: X8 if
  entries cluster on WASDE or Crop Progress days; the member must exclude those (release-timed is X8).

### K9M-020 The (Absence of a) Weather Risk Premium in New-Crop Soybean Futures Prices
- Citation: Janzen, J. (June 23, 2021). farmdoc daily, University of Illinois.
- Retrieval: curl; reports/stage_e10_research/commodity/fdd_soy_weather.pdf (+ .txt). Full text.
- Verified passages:
  - P-K9M-020-a: "In contrast to corn, I show that new-crop soybean futures prices are not on average substantially
    higher during the growing season than at harvest. Between 2000 and 2020, November soybean futures prices were
    on average neither higher or lower than the price at harvest."
  - P-K9M-020-b: "At their seasonal maximum in mid-July, new-crop soybean futures are on average just 4% higher than
    in the week of November 1. This is inconsistent with the presence of a weather risk premium."
- Reader's note: Conflicting evidence: the weather-premium season does not carry over to ZS (and by extension to
  ZM, ZL). A corn member must not be extended to the soy complex. X: none.

### K9M-021 The weather premium in the U.S. corn market (abstract only)
- Citation: Li, Z., Hayes, D. J., Jacobs, K. L. (2018). "The weather premium in the U.S. corn market." Journal of
  Futures Markets 38(3), 359-372. DOI 10.1002/fut.21884.
- Retrieval: IDEAS/RePEc abstract page (curl); reports/stage_e10_research/commodity/lhj_ideas.html (+ .txt).
  Abstract only (Wiley full text not open).
- Verified passages:
  - P-K9M-021-a (abstract): "We further show that the magnitude of the weather premium depends on the carryout and
    expected yield at harvest."
  - P-K9M-021-b (abstract): "We use data from 1968 to 2015 to evaluate the accuracy of the December futures price as
    a forecast of the harvest price. A predictable component in the forecast error is consistent with the existence
    of a time‐varying weather premium."
  - P-K9M-021-c (abstract): "We demonstrate that a passive strategy of routinely shorting the corn December futures
    does not provide an attractive risk‐adjusted return."
- Reader's note: Supports a state-dependent (carryout-dependent) premium rather than an unconditional season;
  conflicts with an unconditional seasonal short (P-K9M-021-c). Carryout is a USDA WASDE number: usable as a level
  only, read after publication and never traded in the release window (X8). Abstract only.

### K9M-022 Pre-harvest corn pricing and the post-short-crop pattern
- Citation: Blue, E. N., Wisner, R. N., Baldwin, E. D. (2004). "Performance of Selected Pre-harvest and Post-harvest
  Corn and Soybean Marketing Strategies vs. Alternative Market Benchmarks." Proceedings of the NCR-134 Conference
  on Applied Commodity Price Analysis, Forecasting, and Market Risk Management, St. Louis, April 19-20, 2004.
- Retrieval: curl from farmdoc NCCC-134 archive; reports/stage_e10_research/commodity/nccc2004_confp22.pdf (+
  .txt). Full text.
- Mechanism: New-crop December corn is high early in the year and declines into harvest; after a weather-induced
  short crop the decline appeared in every such year.
- Sample window: 1975-2003 (29 years); 1985-2003 subperiod.
- Quality tells: conference paper, marketing-strategy focus, small number of state years (8), farm-income metric
  not a futures return statistic.
- Verified passages:
  - P-K9M-022-a: "in 29 years of data, the weekly average December futures price is relatively high from the start
    of the year until June, and then declines into the harvest season."
  - P-K9M-022-b: "Figure 2 shows the pattern of December corn futures for all years following a weather-induced
    short crop from 1975 through 2003."
  - P-K9M-022-c: "For the eight such years since 1975, that pattern emerged each year."
  - P-K9M-022-d: "Six out of the 29 years showed lower prices in the pre-harvest period than at harvest. Five of these
    years reflected severe drought in the Corn Belt, and the remaining year was a time of widespread excessive
    rains."
- Numeric claims: 8 of 8 post-short-crop years declined (P-K9M-022-c); 6 of 29 years rose into harvest
  (P-K9M-022-d).
- Conflicting evidence: K9M-021 (passive short not attractive risk-adjusted); 6/29 adverse years are weather
  disasters, so the short has severe left-tail risk in exactly the years that matter.
- Reader's note: A rare state (post-short-crop year, about 8 in 29) times a season. As a K9 member it would fire
  only in qualifying years: at two entries a week over about 25 weeks, about 50 trips in a qualifying year and
  zero otherwise, so the 299-date window may hold no qualifying year at all (trip floor risk). Data item: a public
  "short crop" definition (USDA final yield below trend, or ending stocks-to-use below a percentile), level read
  after publication. Short ZC December, one grain session per trip. X8 risk if keyed to report days.

---

## Gaps (searched, not found)
- No source found that splits commodity carry, basis or term-structure premia into overnight vs day-session parts
  for CME energy, metals, grains or livestock (WebSearch calls on commodity overnight/intraday decompositions
  returned equity papers or Chinese night-session papers, routed).
- No source found that splits Treasury futures returns or the curve (slope) carry by session (three WebSearch
  calls; results were equity overnight-drift papers, Treasury price-discovery papers, and practitioner pages).
- Daily-horizon outright evidence for curve signals: only K9M-006 (daily, but a spread, under 1 bp a day). All
  outright curve-state evidence is monthly (K9M-001 to -005, -007, -008), with K9M-003 showing that faster
  rebalancing lowers returns.
- Livestock seasonals: only practitioner seasonal charts (rejected as blogs) and K9M-004's roll-return line.
- NG storage-level state signing a drift: no academic source located beyond the monthly cross-section.

## Fetch log

All times UTC. Tool "curl" = `curl -sL -A "Mozilla/5.0 ..."`, then `pdftotext -layout` for PDFs; HTML pages
converted to .txt by a tag-stripping Python one-liner.

| File | URL | UTC fetch time | sha256 | bytes | tool |
|---|---|---|---|---|---|
| commodity/ghr_w13249.pdf | https://www.nber.org/system/files/working_papers/w13249/w13249.pdf | 2026-10-03T05:36:27Z | e0533a62d4ccdd2b18d4b39d7fdec0c7f26367fb94ec8a877b927bfa16abf0ed | 427352 | curl |
| commodity/kmpv_carry_w19325.pdf | https://www.nber.org/system/files/working_papers/w19325/w19325.pdf | 2026-10-03T05:36:28Z | 6daaa0a9552e0552f94cfea778ff841f4497fa602c218f9410518fe5dc6b6612 | 342308 | curl |
| commodity/fmr_jbf2010.pdf | https://openaccess.city.ac.uk/id/eprint/6416/1/Fuertes_Miffre_Rallis_JBF2010(CRO).pdf | 2026-10-03T05:36:29Z | a1ef8516f80785735dfb3413029eeb00e7940c3a877874422d60446e129f34bb | 290630 | curl |
| commodity/erbharvey_w11222.pdf | https://www.nber.org/system/files/working_papers/w11222/w11222.pdf | 2026-10-03T05:36:31Z | 35f34d652a0d40726ddf7102e07b86e3c2900fee1eeed3d984147b832fd4437e | 328029 | curl |
| commodity/kln_seasonal_w20815.pdf | https://www.nber.org/system/files/working_papers/w20815/w20815.pdf | 2026-10-03T05:36:32Z | a273963eeaf32b3acdd15bb0ddfd9d74cc91c7138f8f81956a7d9072d518fc65 | 363131 | curl |
| commodity/boons_prado_bm.pdf | https://conference.nber.org/conf_papers/f89296/f89296.pdf | 2026-10-03T05:39:27Z | b62be3db128ad32ec3736f4b3775630afbb2d9002787d7364f917a537f4413e3 | 631318 | curl |
| commodity/arxiv_2308.00383.pdf | https://arxiv.org/pdf/2308.00383 | 2026-10-03T05:39:59Z | d244f3b2fbc0ab91f955087ab7c87f5d417319115e79371b3c594870ca0b5150 | 1072718 | curl |
| commodity/fmg_dp942.pdf | https://www.fmg.ac.uk/sites/default/files/2026-01/DP942.pdf | 2026-10-03T05:40:01Z | 89878613fba40febb9054cfbb27761eefc63cfad87005fa57077b69958417c44 | 840670 | curl |
| commodity/essex_cyr.pdf | https://repository.essex.ac.uk/34736/1/Convenience%20yield%20risk.pdf | 2026-10-03T05:40:04Z | 85f206e649cd7f76c6a4a4810f2171ab08ea13894a8d9a88b4e009038287e799 | 515602 | curl |
| commodity/mpra_39903.pdf | https://mpra.ub.uni-muenchen.de/39903/1/MPRA_paper_39903.pdf | 2026-10-03T05:46:57Z | d1046025ab1f99a82232eb7d44f71047193fe2f1d4aaa8b8738414c12bfec2c9 | 314764 | curl |
| commodity/kmw_fxpremia_aea2019.pdf | https://topcat.aeaweb.org/conference/2019/preliminary/paper/QQ73KSH8 | 2026-10-03T05:35:51Z | d795e33d357b071b394d7be4aeb5ee4b057528bbcea983f4cc4515eed27e64c8 | 2625049 | curl (served PDF under .html name; renamed) |
| commodity/kmw_fixings_2024.pdf | https://wrap.warwick.ac.uk/177333/1/WRAP-foreign-exchange-fixings-returns-around-clock-Mueller-2023.pdf | 2026-10-03T05:35:39Z | a7975f26f9b42b837a0b2a6c1474a63e448fff5a0fa7957bc2233b1c0302e6a3 | 1265557 | curl |
| commodity/cw_econpapers.html | https://econpapers.repec.org/RePEc:fip:fedgif:752 | 2026-10-03T05:46:35Z | 976928d79604b622e2cb55bf6ef2e4daea827e5c8ecdecb5924b568769d11edb | 13835 | curl |
| commodity/arxiv_2609.12227.pdf | https://arxiv.org/pdf/2609.12227 | 2026-10-03T05:39:09Z | f45d74fadda3caa5b1a4cb51a29185f67a8c9a249621624bc2cfffa9253557ab | 2402390 | curl |
| commodity/sorensen_cbs.pdf | https://research-api.cbs.dk/ws/files/59044569/7146.pdf | 2026-10-03T05:45:01Z | 933e88735f7de82c34e379a78ae5fbe80444b7f5b078fd9dc277602367a9dd4e | 817514 | curl |
| commodity/boe_seasonality_2016.pdf | https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2016/risk-premia-and-seasonality-in-commodity-futures.pdf | 2026-10-03T05:38:01Z | 1c02088c5828d1e4cb1f277532b57d1a9fea291df09ba7b00f525977e1dd0192 | 802157 | curl |
| commodity/caselli_ng_weather.pdf | https://iris.unibocconi.it/retrieve/80f68941-b412-43f3-992a-2a2a701b0398/Caselli%20Gandolfi%20et%20al.pdf | 2026-10-03T05:38:04Z | 49e740eb84a0efdffea5dda139459a94d57fabd00d9fbb1d8dded3eb9c3e0382 | 7400739 | curl |
| commodity/eia_wngsr_schedule.html | https://ir.eia.gov/ngs/schedule.html | 2026-10-03T05:48:33Z | b54595ec6784c11c95ab448fa21d3f115b03a2bcc02960cab589fb0ad4cc1e04 | 8105 | curl |
| commodity/fdd_corn_weather.pdf | https://farmdocdaily.illinois.edu/wp-content/uploads/2021/06/fdd020621.pdf | 2026-10-03T05:38:05Z | 8d33707c122ee63bf18de71479ee9cd52db3bc4292c14d776418d9aef20c306e | 336804 | curl |
| commodity/fdd_soy_weather.pdf | https://farmdocdaily.illinois.edu/wp-content/uploads/2021/06/fdd230621.pdf | 2026-10-03T05:38:06Z | a0c2ecf0ad20e2c92dc6c186b06142dd7e164c6b6212b7505a8e18674ee08cdb | 278055 | curl |
| commodity/lhj_ideas.html | https://ideas.repec.org/a/wly/jfutmk/v38y2018i3p359-372.html | 2026-10-03T05:46:12Z | 324945061fb087670c43856a4e86452b16291da8ae15316f8d41da78029ef6af | 53887 | curl |
| commodity/nccc2004_confp22.pdf | https://farmdoc.illinois.edu/assets/meetings/nccc134/conf_2004/pdf/confp22-04.pdf | 2026-10-03T05:43:22Z | 7919372b5c3e53e438fca1d8f82ccb1f2216c6e06436eb16ce5f1d5995750656 | 402169 | curl |

API search records (not evidence): reports/stage_e10_research/commodity/api/ (14 OpenAlex query files oa_m*.json,
7 single-work lookups, 2 Semantic Scholar 403 responses ss_m1a.json and ss_m1b.json).

## Rejection table (screened and not logged)

| Record | Reason |
|---|---|
| He, S. (2026) "Interpretable Systematic Risk around the Clock", arXiv:2604.13458 (fetched, deleted) | Equity market only (S&P 500 E-mini, TAQ); no commodity, FX or rates content |
| Hayenga, M. L., DiPietre, D. D. (1981) "Hedging Pork Products Using Live Hog Futures", ageconsearch 279413 (Firecrawl, not saved) | Cross-hedging regressions of cash pork cuts on live hog futures; no futures return or seasonal premium evidence. The search snippet claiming livestock futures "tended to rise ... about 30 cents per hundredweight per month" was not found in it |
| Zanini, F. C., Garcia, P. (1997) "Did Producer Hedging Opportunities in the Live Hog Contract Decline?", EconWPA 9712005 (fetched, deleted) | Hedging effectiveness, not a return premium; no "30 cents" claim inside |
| Colling, Irwin, Zulauf (1992) "Response of Wheat, Corn and Soybeans Futures Prices to the USDA Export Inspection Report", NCCC-134 (fetched, deleted) | Release-timed (USDA report): X8-type, outside M2's level-or-season rule |
| Forecasting WTI crude oil futures returns: Does the term structure help? (Energy Economics 2021, DOI 10.1016/j.eneco.2021.105350) | ScienceDirect PDF returned a captcha page (blocked); no open copy found; abstract not retrieved |
| Szymanowska, de Roon, Nijman, van den Goorbergh (2014) "An Anatomy of Commodity Futures Risk Premia", JF (DOI 10.1111/jofi.12096) | Wiley 403; SSRN copy not attempted (SSRN blocks); no OA location in OpenAlex. Its spot/term premium decomposition is described inside K9M-005 |
| Shao, Bhar, Colwell (2015) "A multi-factor model with time-varying and seasonal risk premiums for the natural gas market", Energy Economics (DOI 10.1016/j.eneco.2015.04.013) | No OA copy; OpenAlex has no abstract; not retrievable |
| Martinez, Torró (2016) UK natural gas risk premium and seasonality (roderic.uv.es bitstream) | Repository returned an HTML page, not the PDF; UK NBP is not a traded exposure anyway |
| Mu, X. (2004/2007) "Weather, storage, and natural gas price dynamics" (iaee.org PDF) | Returned HTML (blocked); the snippet is about volatility (Mondays, storage-report days): volatility belongs to the Regime reader, release days to X7/Calendar |
| Boyarchenko, Larsen, Whelan "The Overnight Drift" (CEPR DP14462 blocked; NY Fed SR917 fetched, grepped, deleted) | Equity overnight drift; no Treasury-futures session split in the grepped text; routed to the Overnight reader |
| Bakshi, Gao, Rossi; Daskalaki et al.; Bhardwaj-Gorton-Rouwenhorst (2015) "Facts and Fantasies ... Ten Years Later" (NBER w21243); Fernandez-Perez et al. (2017) "The skewness of commodity futures returns" | Monthly cross-sectional factor papers duplicating K9M-001/-002/-005; not fetched for depth reasons |
| Symeonidis et al. companion: "Index Funds, Financialization..." (Irwin-Sanders 2011), "Index Investment and Financialization" (Tang-Xiong) | Financialization topic; index-roll effects are X13 |
| Columbia CGEP "Low US Storage Levels" (policy brief); EIA cash-and-carry arbitrage working paper (eia.gov cc_arbitrage_full.pdf) | Not return-predictability studies (inventory response to spreads; policy commentary) |
| Practitioner pages: equityclock seasonal charts (live cattle, lean hogs, TY), aegis-hedging, RBN Energy, S&P Global news, DTN, Barchart, profarmer, National Hog Farmer, Quantpedia, Alpha Architect, WisdomTree, Macrosynergy, harbourfrontquant | Blogs or news without a stated sample and method; pointers only |
| arXiv 1802.01393 seasonal stochastic volatility (Samuelson effect); JARE Aug 2010 grain volatility components (ageconsearch 93205) | Volatility seasonality, not a signed drift (Regime reader) |
| CARD Ag Policy Review (2014) "Is there an Optimal Month to Forward Contract?"; farmweeknow, manitobacooperator, hoosieragtoday | Extension and news commentary; not fetched |
| Kogan-Livdan-Yaron, Routledge-Seppi-Spatt "Equilibrium Forward Curves for Commodities" (JF 2000) | Theory/pricing models; no tradable return condition |
| Iowa State "Three essays on commodity futures and options markets" (livestock risk premium) | Snippet says no time-varying risk premium in hogs and cattle; dissertation full text not fetched (time); noted as possible conflicting evidence for livestock, unverified |

## Routed (belong to other readers; not read)
- Lou, Polk, Skouras, "A Tug of War: Overnight versus Intraday Expected Returns" (JFE 2019) and "The Day Destroys
  the Night, Night Extends the Day" (2022): Overnight reader (O1).
- Boyarchenko, Larsen, Whelan, "The Overnight Drift" (RFS 2023): Overnight reader (O1).
- "Empirical differences between the overnight and day trading hour returns: Evidence from the Chinese commodity
  futures" (China Finance Review International 8(3)): Overnight reader (O1).
- Ewald, Haugom, Lien, Størdal, Wu (2022) "Trading time seasonality in commodity futures: An opportunity for
  arbitrage in the natural gas and crude oil markets?" Energy Economics 115, 106324 (title page only seen):
  Calendar reader (C1, time-of-day/day-of-week).
- Moskowitz, Ooi, Pedersen (2012) "Time series momentum": Overnight reader (O2, TSMOM).
- Brunnermeier, Nagel, Pedersen (2009) "Carry trades and currency crashes" / NBER w15062 "Crash Risk in Currency
  Markets": Regime reader (volatility-state conditioning of carry).
- Mu (2004/2007) NG volatility on Mondays and storage-report days: Calendar reader (day-of-week) and Regime reader.
- The fix-timed portion of K9M-011: Calendar reader / X9 (logged here only for the carry-session question).

## Candidate mechanisms (what the log supports; the lead decides)

1. C-STORAGE: scarcity-state carry (theory of storage). Sources K9M-001 (P-K9M-001-a, -b, -c, -d), K9M-002
   (P-K9M-002-a, -b), K9M-004 (P-K9M-004-b), K9M-005 (P-K9M-005-a, -c), K9M-007 (P-K9M-007-b), K9M-008
   (P-K9M-008-a). Condition: the product's annualized front-to-second basis (or relative basis, or basis-momentum)
   in the top 20% of its trailing 250 completed trade dates (D-pct). Sign: long (short in the bottom 20%,
   contango). Hold: full trade date, 17:00 CT reopen to 15:08 CT (grains 19:00-07:43 or 08:30-13:18; livestock
   08:30-13:03). Products: MCL, NG, MHG, ZC, ZW, ZS, ZM, ZL, HE, LE (MGC excluded: negligible convenience yield,
   negative roll in P-K9M-004-a). Data items: second-nearby (and for relative basis a third) contract daily
   settles: deferred-contract bars, flagged for E.11/E.12; or NG storage level vs 5-year average with publication
   Thursday 10:30 ET (K9M-018). Closest X: none; keep the slope read away from roll windows (X13). Conflicts:
   P-K9M-003-c (faster rebalancing lowers returns), P-K9M-002-c (commodity carry only partly earned). Documented
   size about 2-8 bp per trade date, below M_X on every commodity exposure.
2. C-FXCARRY-DAY: FX carry earned in the U.S. session. Source K9M-010 (P-K9M-010-a, -d, -e, -f, -g), K9M-011
   (P-K9M-011-b). Condition as published: sign of the rate differential (monthly), which fires daily; a rarity
   condition is not in the source. Sign: long high-rate (6A, 6N), short low-rate (6J, 6S, 6E) futures. Hold: 07:00
   to 15:08 CT (the source's 08:00-17:00 ET window truncated at F). Data item: public policy or deposit rate
   series with publication times. Closest X: X9 (K9M-011 ties the session pattern to fixes); overlaps O1. Conflict:
   K9M-012 (short-window UIP). Size about 1-2.4 bp per trade date, below M_X.
3. C-NGCOLD: extreme cold-forecast premium in NG. Source K9M-017 (P-K9M-017-b, -c, -e, -f, -g, -i). Condition:
   NOAA GEFS 1-2 week U.S. temperature forecast deviation from seasonal norms in its bottom 10-20% (about 10-20%
   of dates, winter-heavy). Sign: long front NG. Hold: next full trade date after the forecast is public (00:00 UTC
   run; entry at the first bar after publication or the next 17:00 CT reopen) to 15:08 CT. Data item: NOAA GEFS
   forecasts (not held; flag). Closest X: none (not EIA-timed; avoid Thursday release windows, X7). Published
   evidence is for a 5-day NG1-NG2 spread, not an outright one-day hold; realized temperatures carry no premium
   (P-K9M-017-d).
4. C-CORNWX: new-crop corn weather-premium decay, conditioned on carryout. Sources K9M-019 (P-K9M-019-a), K9M-021
   (P-K9M-021-a, -b), K9M-022 (P-K9M-022-b, -c). Condition: June through August (season), optionally only in
   post-short-crop or high-carryout years per K9M-021's carryout dependence. Sign: short December corn. Hold: one
   grain session, 08:30-13:18 CT (or 19:00-07:43 CT). Products: ZC only (K9M-020 shows no premium in soybeans).
   Data item: December contract bars while it is deferred; USDA carryout level read after publication. Closest X:
   X8 if any entry is keyed to WASDE or Crop Progress days. Conflicts: P-K9M-021-c (passive short not attractive),
   P-K9M-022-d (drought years are large losses). Size about 10 bp per trade date (about 1.8 ZC ticks), below M_X
   (4.5); state version may not reach the 40-trip floor in the 299-date window.
5. C-SEASON (weak): same-calendar-month commodity seasonality. Source K9M-013 (P-K9M-013-b). Condition: product's
   historically strongest (weakest) calendar month from prior years only. Sign: long (short). Hold: full trade
   date. Data: own history. Closest X: none (Calendar reader may own it). Conflict: K9M-014 (P-K9M-014-b, -c), t =
   1.93 in-sample. Not recommended on this evidence.
