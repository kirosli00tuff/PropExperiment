# Stage E.23 P1.2 mechanism memo: M4_INTRADAY_MOM (intraday and rest-of-day momentum)

Worker: MechanismReaderM4_INTRADAY_MOM-OpusHigh (opus, high). Brief: reports/stage_e23_briefs/brief_mechanism.md.
Written 2026-10-17, 02:16 to about 02:35 PDT. Pages and fetch log: reports/stage_e23_briefs/mech_pages/M4_INTRADAY_MOM/
(fetch_log.md). The lead fixes the final directions; this memo gives the evidence only.

The E.23 question for this family: the trigger's side is the sign of an intraday price move (H6: previous close to C-30;
CP1: trade-date open, overnight included, to O+29; H1: prior settlement to S-31). E.23 enters at the trigger day's
settlement, after that move and after the last half hour, and holds 5 or 20 trading days. So the relevant evidence is
what happens to returns from today's close over the next days, after a day whose intraday move had a given sign.
"Continuation" below means the next-days return has the trigger's sign; "reversal" means the opposite sign.

## 1. Evidence table

All quotes are verbatim from saved full text unless marked. Line numbers refer to the saved text file named.

| key | full citation | URL | saved path | sha256 | verbatim quote (location) | claim it supports |
|---|---|---|---|---|---|---|
| BDLM2021-a | Baltussen, G., Da, Z., Lammers, S., Martens, M. (2021), "Hedging demand and market intraday momentum", Journal of Financial Economics 142, 377-403 | https://doi.org/10.1016/j.jfineco.2021.04.029 (EUR portal copy saved in E.13) | reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md | 18cb436e9d18cb3eff3565cddfe85b35fa1c5d5d8bf2afb85df42b6ab49e0465 | "Using intraday returns on over 60 futures on equities, bonds, commodities, and currencies between 1974 and 2020, we find strong market intraday momentum everywhere. ... The predictive power is economically and statistically highly significant, and reverts over the next days." (abstract, md lines 85-88) | Same event as H6 (r_ROD predicts r_LH); reversal over the next days, all four asset classes |
| BDLM2021-b | same | same | same | same | "Empirically, in all four asset classes, returns in the next three days are opposite to those of r_LH. For equities, bonds, and commodities, there is a highly significant mean-reversion, consistent with transitory price pressure, which arises from hedging." (Section 1 introduction, md lines 356-360) | Direction: reversal; horizon 1 to 3 days |
| BDLM2021-c | same | same | reports/stage_e10_research/overnight/baltussen_intramom.txt (clean JFE text; pdf alongside, sha256 623ba82490acd01546f568cf582de5a9b45dfbd97731cd548cb119d7a0acec57) | 2f4381fb36833b7406d899c4961b31accac53387991f67cf326b74416c3527c4 | Table 11 (p. 393; txt lines 1217-1250): "regressing the next day return (r_c,t^c,t+1), the next two days return (r_c,t^c,t+2), and the next three days return (r_c,t^c,t+3) on a constant and today's last half-hour return (r_LH,t) ... Samples range from December 1974 to May 2020 ... Adjusted R2 and regression coefficients are multiplied by 100." Coefficients on r_LH,t (t-stats): Equity -14.51 (-1.70), -29.05 (-3.16), -27.98 (-2.61); Bond 1.77 (0.41), -10.68 (-1.60), -19.64 (-2.21); Commodity -0.82 (-0.25), -8.56 (-1.61), -12.22 (-2.17); Currency -8.06 (-1.32), -8.64 (-1.14), -6.98 (-0.84). Text (p. 393): "In all four markets, we observe reversals, although this effect is not significant in currency futures." | Magnitude: next 1/2/3-day close-to-close return = beta x r_LH with beta = -0.15/-0.29/-0.28 (equity), -0.20 at 3 days (bonds), -0.12 at 3 days (commodities), insignificant (FX). Entry at the close, as in E.23. Equity sample includes NQ (txt line 1375: "NASDAQ 100 futures ... NQ 1996-04-12 2020-05-01") |
| BDLM2021-d | same | same | baltussen_etal_2021_jfe.md; figure read from rendered page 393 (mech_pages/M4_INTRADAY_MOM/tmp/M4_INTRADAY_MOM_bdlm_p17-17.png) | as above | "Fig. 5 clearly shows that the market intraday momentum does not persist for long. The predictive power of r_ROD reverts to zero in the next day in the currency futures market (Fig. 4D), in two days in the equity and commodity futures markets (Figs. 4A and C), and in three days in the government bond futures markets (Fig. 4B)." (Section 4.4, md lines 2747-2750). Figure reading (visual, not text): the equity panel's cumulative coefficient from C-30 on day t falls from about 4 at r_LH to about -1.5 by the close of t+3, confidence band about -6.7 to +3.7. The figure stops at t+3 in every panel. | Horizon: evidence ends at 3 days; nothing at 5 or 20 days |
| BDLM2021-e | same | same | baltussen_etal_2021_jfe.md | as above | "Heston et al. (2010) find evidence of intraday return seasonality in the cross-section of stocks: returns continue during the same half-hour intervals as in previous trading days, lasting from 1 to up to 40 trading days. ... We also find market intraday momentum to be distinct from intraday return seasonality" (Section 2, md lines 459-464) | The only documented multi-week persistence near this family is same-interval intraday seasonality (stocks), an intraday-only effect, not a close-to-close return |
| GHLZ2015 | Gao, L., Han, Y., Li, S. Z., Zhou, G., "Intraday Momentum: The First Half-Hour Return Predicts the Last Half-Hour Return", working paper, version December 2015 (published as "Market intraday momentum", JFE 129 (2018) 394-414) | https://c.mql5.com/forextsd/forum/173/intraday_momentum_-_the_first_half-hour_return_predicts_the_last_half-hour_return.pdf (third-party host of the authors' working paper) | mech_pages/M4_INTRADAY_MOM/ghlz_2015_wp_mql5.pdf (+ .pdf.txt) | 050d5680d1424a5f53aeb175de283bc796b130be3874abf319aa1980941cc374 | "On a day when the first half-hour return is up substantially, the twelfth half-hour return is on average positive, making those who procrastinate have to unwind in the last half-hour. This also helps to understand the fact that the opening price on the following day is on average lower, which suggests that there is an adjustment of the price from the previous day's buying pressure in the last half-hour." (Introduction, txt lines 128-134; repeated txt lines 380-382) | CP1's source paper: the late-day pressure partly reverses by the next open (SPY, 1993-2013). No multi-day statistic given |
| BBBM2021 | Barbon, A., Beckmeyer, H., Buraschi, A., Moerke, M. (2021), "The Role of Leveraged ETFs and Option Market Imbalances on End-of-Day Price Dynamics", Swiss Institute of Banking and Finance WP 2021/14 | (saved in E.20) | reports/stage_e20_briefs/shared/barbon_beckmeyer_buraschi_moerke_letf.pdf.txt | c3a725db9e1fd4a4268af8742e46cc422de2b34a65e960988f285c2198f1fd01 | "Consistent with the notion of temporary price pressure, the documented effects quickly revert at the next day's open." (abstract, lines 35-37); "we find that on average 82% of the impact of delta-hedging and 32% of the impact of leveraged ETF rebalancing is reversed at the next open." (lines 1886-1888) | Hedging-driven end-of-day momentum is transitory; reversal is overnight (stocks). Horizon: next open only |
| BvD2019 | Baltussen, G., van Bekkum, S., Da, Z. (2019), "Indexing and stock market serial dependence around the world", Journal of Financial Economics 132(1), 26-48 | https://www3.nd.edu/~zda/Indexing.pdf (author's page) | mech_pages/M4_INTRADAY_MOM/bvd_2019_jfe_indexing.pdf (+ .pdf.txt) | 05333bbdbe54c931c52338680255de171edbe86f76129201bce041b3637c6010 | "While many studies find serial dependence to be positive until the 1990s, it switches to negative since the 2000s. ... the decline in serial dependence links to the increasing popularity of index products (e.g., futures, exchange-traded funds, and index mutual funds)" (abstract, txt lines 30-41). "a strategy that trades against MAC(5) using all indexes in our sample [or the Standard & Poor's (S&P) 500 index alone] would result in an annual Sharpe ratio of 0.63 (0.67) after March 2, 1999 ... In addition, serial dependence in the futures and exchange-traded funds (ETFs) covering our equity indexes is negative ever since their inception." (Section 1, txt lines 112-119). "MAC(5) is also significantly negative in futures returns and ETFs returns since the introduction of futures and ETFs, respectively." (txt lines 612-615). Table 1 (txt lines 338, 398), after March 3, 1999: S&P 500 daily AR(1) -0.076***, weekly AR(1) -0.077 (not starred); panel of 20 indexes daily AR(1) -0.026*, weekly AR(1) -0.082**. | Equity-index analog: a day's (or week's) index return predicts a reversal next day and next week, since about 2000, including in index futures. Sample to December 2016 (txt line 289). Close analog for 5-day horizon |
| NBIM2014 | Norges Bank Investment Management (2014), "Momentum in Futures Market", NBIM Discussion Note 1-2014 | https://www.nbim.no/globalassets/documents/dicussion-paper/2014/discussionnote_time_series_momentum_latest.pdf | mech_pages/M4_INTRADAY_MOM/nbim_2014_tsmom_note.pdf (+ .pdf.txt) | 1ab4e7bfc49b8211dd71a3bd909da7770291373d6c183b1b8fa6c158067d061a | "First, return autocorrelation is generally much weaker at one week lags for all asset classes. In particular, we find significant short-term price reversal in equity futures (t-statistic of almost -5 at one week lag). Second, the periods between 2 and 16 weeks, and between 36 and 52 weeks, appear to exhibit significant return continuation." (Section 3.1, p. 8, txt lines 635-639). Chart 2 title: "Time series predictability across all assets based on weekly returns (Sample period is January 1990 to May 2013)". Figure reading (visual, rendered page 8): at the one-week lag, equity about -5, commodity and bond near 0, currency about +2; lags 2-3 weeks positive in all four classes. | Weekly-return analog: equity futures reverse at 1 week (5-day hold); 2+ weeks continuation (relevant to the back part of a 20-day hold). 47 futures, 20 commodities, 9 equity, 11 bond, 7 FX (txt lines 83-84) |
| BK2012 | Baltas, A.-N., Kosowski, R. (2012), "Momentum Strategies in Futures Markets and Trend-following Funds", working paper (first version December 2011) | (saved in E.10) | reports/stage_e10_research/overnight/baltas_kosowski_momf.txt (pdf sha256 f48c15bba94e7105939ddd86c33831078c778c3fb7d77bb2cafa3d8cd0449a5a) | 36807a569a69dde96834e8e97cdf3620c502de968a6701bf74b2a247732d1936 | "Lastly, Panel C documents similarly two important regions of past return predictability. The first period extends roughly from the 9th to the 15th lagged daily returns ... Panel C also reports a relatively large t-statistic for the last day's return, which is in turn directly related to the serial correlation measure. However, as we later see in the subsection 4.3, this effect is largely due to the early sample behaviour and does not represent a stable-over-time significant momentum effect." (Section 4.1, lines 490-496). "the weekly and daily strategies have become less profitable during the second sub-sample period (post-1995)." (lines 97-98) | Daily-return analog across 71 futures (1974-2012): a single day's return has no stable next-day effect; it positively predicts returns about 9 to 15 days later (continuation inside a 20-day hold). Documented decay post-1995 for daily strategies |
| DTTY2024 | Da, Z., Tang, K., Tao, Y., Yang, L. (2024), "Financialization and Commodity Markets Serial Dependence", Management Science 70(4), 2122-2143 | https://www3.nd.edu/~zda/commodity.pdf (author's page) | mech_pages/M4_INTRADAY_MOM/dtty_2024_commodity_serial.pdf (+ .pdf.txt) | 1677446a35f31ca247e8d23f0f4f319dc7a25223b5fb402e67141a5a1fcc36ae | "daily exposure to such index trading results in price overshoots and reversals, as reflected in negative daily return autocorrelations, only among commodities in that index." (abstract, txt lines 33-36). "the daily autocorrelations in two popular commodity indices, S&P Goldman Sachs Commodity Index (GSCI) and the Bloomberg Commodity Index (BCOM), have steadily declined since 2004 when financialization began. They entered negative territory around 2005 and became significantly negative" (txt lines 70-74). "we find that the negative daily autocorrelation among indexed commodities goes beyond one day and becomes stronger during the high index exposure period" (txt lines 144-146). "Our paper speaks to price inefficiency at high frequency (daily to weekly)" (txt lines 335-336). Fig. 1 notes: "we take heating oil and reformulated blendstock for oxygenated blending and lean hogs as nonindexed commodities because of their small weights in the index. The sample period is from 1980 to 2018." (txt lines 111-113) | Commodity analog: reversal after a day's move, daily to weekly, for index constituents (energy, metals, grains), since about 2005; not for non-indexed contracts |
| Mesfin2026 | "The Bounce Has No Direction: Sign, Magnitude, and the Microstructure of Equity Return Predictability", arXiv 2606.29591 (2026 preprint, not peer reviewed) | https://arxiv.org/abs/2606.29591 | mech_pages/M4_INTRADAY_MOM/arxiv_2606.29591_abs.html | 6ac40ab7fc3b35ba414e4ba745a9296bbe571878aa26d1cd831a225e4c82ddb2 | ABSTRACT ONLY: "The lag-1 autocorrelation in SPY is driven entirely by magnitude: the FRI sign test is insignificant (p=0.11) ... At lag 3, a significant directional reversal (p=0.02) ... The cross-asset panel shows mean reversion confined to exchange-traded equities and sovereign bonds; credit ETFs, commodities, FX, and crypto are indistinguishable from random walks." | Counter-evidence (abstract only): the equity daily AR(1) may not be a directional (sign-tradable) reversal; no reversal in commodities or FX, 1993-2026 |
| Coffee2025 | "Intraday market momentum in coffee futures: Dynamics and drivers", Journal of Commodity Markets (2025), doi 10.1016/j.jcomm.2025.100537 | https://verso.uidaho.edu/esploro/outputs/journalArticle/Intraday-market-momentum-in-coffee-futures/996867269001851 | not retrievable (fetch_log.md) | n/a | [unverified]: a search summary said early-day (overnight and morning) momentum "tends to carry over across days" while late-day momentum dissipates quickly. Not read; not used for any direction. | Possible continuation for the CP1-type early-day signal in one commodity; unverified |

## 2. Per-member paragraphs

### E.20 H6: rest-of-day to last-half-hour momentum on NQ (reports/stage_e20_prereg_H6.md)

- Strength: moderate (strong at 1 to 3 days on this exact event and instrument class, BDLM2021 Table 11 with t = -3.16 at
  2 days and NQ in the sample to May 2020; at 5 days only close analogs; at 20 days mixed analogs).
- Direction: reversal of the trigger-day move (sign(r_ROD)) for the 5-day hold; for the 20-day hold the literature
  disagrees (reversal over the first days, continuation at 2+ weeks), see below.
- Reason: BDLM2021 attribute market intraday momentum to gamma hedging by short-gamma option dealers and leveraged ETF
  rebalancing near the close; this is price pressure without news, so it should revert once the hedging stops, and it
  does: "returns in the next three days are opposite to those of r_LH", significantly for equity index futures
  (BDLM2021-b, -c). BBBM2021 find the same transitory end-of-day pressure in stocks, mostly reversed at the next open.
  Beyond 3 days the reason is the indexing/arbitrage channel of BvD2019: since about 2000 index returns, including
  index futures, show negative daily and weekly serial dependence (S&P 500 daily AR(1) -0.076 after 1999), and NBIM2014
  find a one-week-lag reversal in equity futures with t of almost -5 (1990-2013). Against this: BK2012 and NBIM2014
  find continuation at lags of about 9 to 15 days and 2 to 16 weeks across futures (all classes pooled), which would
  act on the back half of a 20-day hold; and Mesfin2026 (abstract only) argues the SPY daily autocorrelation is a
  magnitude effect, not a sign effect.
- Horizon: 1 to 3 days directly (BDLM2021). 5 days: analog only (BvD2019 weekly AR(1); NBIM2014 one-week lag). 20 days:
  no direct evidence; analogs point both ways.
- Magnitude: BDLM2021 Table 11, equity index futures, 1974-2020 (NQ from 1996): next 2-day close-to-close return =
  -0.2905 x r_LH (t -3.16); 3-day -0.2798 x r_LH (t -2.61); R2 0.27% and 0.17%. The expected reversal per event is a
  fraction (about 0.28) of that day's last-half-hour return, which is itself the small predicted part of the day; by
  my arithmetic (not a published number) a 20 bp last half hour implies about 6 bp over 2 to 3 days. BvD2019 report no
  per-event bp; their anti-MAC(5) strategy has an annual Sharpe of 0.63 (0.67 on the S&P 500) after March 1999, sample
  to December 2016. Decay: BDLM2021's sample ends May 2020, before the H6 verdict window (2020-06 to 2024-02); no
  post-publication test of the multi-day reversal was found. BvD2019 document a sign change around 2000 (positive
  before, negative after).

### CP1 port (D6; strategy/members/k1..k6/cp1.py): sign of the overnight plus first half hour, on every root

- Strength: equity roots (K1: MNQ, M2K, MYM) moderate; rates (K2) weak to moderate; energy, metals, grains (K4, K5, K6
  indexed contracts) weak to moderate; FX (K3) and livestock (HE, LE) weak.
- Direction: reversal for the 5-day hold on equity, rates and indexed commodity roots; no evidence of a direction on FX
  and livestock; 20-day hold: the literature disagrees (as for H6).
- Reason: CP1's source paper (GHLZ, the published form of GHLZ2015) explains the first-to-last half-hour link by
  infrequent rebalancing and late-informed trading, and in the working paper by day traders unwinding in the last half
  hour; it states that "the opening price on the following day is on average lower", an adjustment of the previous
  day's last-half-hour buying pressure (GHLZ2015). BDLM2021 treat the overnight plus first half hour as one component
  of r_ROD and show the predicted last-half-hour move reverses over 1 to 3 days in equity, bond and commodity futures
  (t -2.61, -2.21, -2.17 at 3 days) and not significantly in currency futures (t -0.84). Because the CP1 signal is
  positively correlated with the whole day's move, the daily and weekly serial-dependence analogs apply: equity index
  reversal since 2000 (BvD2019; NBIM2014 one-week t of almost -5); indexed commodities reverse at daily-to-weekly
  frequency since about 2005, non-indexed ones (the paper names lean hogs) do not (DTTY2024); bonds and currencies show
  no one-week-lag effect in NBIM2014 (visual reading of Chart 2: bond about 0, currency about +2). Continuation at
  lags of about 9 to 15 days (BK2012) and 2 to 16 weeks (NBIM2014) pulls the other way over 20 days. One unverified
  commodity study (Coffee2025) reports that early-day momentum carries over across days; it was not read and is not
  used.
- Horizon: 1 to 3 days (BDLM2021, all classes; GHLZ2015 next open). 5 days: analogs for equity (BvD2019, NBIM2014) and
  indexed commodities (DTTY2024). 20 days: no direct evidence.
- Magnitude: per class, next 3-day close-to-close beta on r_LH (BDLM2021 Table 11, 1974-2020): equity -0.28 (t
  -2.61), bonds -0.20 (t -2.21), commodities -0.12 (t -2.17), currencies -0.07 (t -0.84). These are betas on the
  last half hour, not on the CP1 signal, so the per-event return on a CP1 trigger is smaller still. No published
  per-event bp for a CP1-signed multi-day hold was found. GHLZ2015 give only the intraday timing return (6.67% a year,
  txt lines 90-91) and no multi-day number. Decay: BK2012 report daily-frequency futures strategies less profitable
  after 1995; DTTY2024 show the commodity reversal is a post-2005 development.

### E.16 H1: settlement-window momentum, pooled over 27 products (reports/stage_e16_prereg_H1.md, base_rules/)

- Strength: moderate for a short reversal on the pooled equity, rates and commodity products; weak for FX and
  livestock; at 20 days mixed.
- Direction: reversal of the trigger-day move (sign of S-31 price minus prior settlement) for the 5-day hold, pooled;
  20-day hold: the literature disagrees.
- Reason: H1's signal is the day's return from the prior settlement to 31 minutes before settlement, which is BDLM's
  r_ROD with the close set at each product's settlement, and the E.23 entry at settlement is the start of BDLM's
  next-days returns. The hedging-pressure reason therefore carries over: transitory end-of-day pressure that reverts
  over the next 1 to 3 days in equity, bond and commodity futures but not significantly in currencies (BDLM2021-b, -c,
  -d). For energy, metals and grain components the index-trading channel adds a daily-to-weekly reversal after about
  2005 (DTTY2024); for livestock (non-indexed in DTTY2024's sense for lean hogs) it does not. Equity products carry the
  BvD2019 / NBIM2014 one-day and one-week reversal. Against: continuation at 9 to 15 daily lags (BK2012) and 2 to 16
  weekly lags (NBIM2014) in pooled futures, and the Mesfin2026 abstract (no reversal in commodities or FX, 1993-2026).
  No paper tests settlement-window momentum, or a settlement-signed trigger, over 5 or 20 days.
- Horizon: 1 to 3 days (BDLM2021); 5 days by analog (NBIM2014, BvD2019, DTTY2024); 20 days none direct.
- Magnitude: as for CP1 (BDLM2021 Table 11 betas on r_LH by class; R2 at most 0.27%). Pooled with equal risk across 27
  products, the class mix (FX insignificant, livestock no reason) dilutes the per-event expectation; no published
  per-event bp exists for this trigger. Decay: as above (BK2012 post-1995; BDLM2021 sample ends May 2020; H1's window
  starts 2010).

### Family-level notes for the lead (evidence, not a direction choice)

- No source found tests any intraday-momentum trigger over a 5 or 20 trading-day hold. The direct multi-day evidence
  (BDLM2021) stops at 3 days and says reversal. The 5-day reading rests on daily and weekly serial-dependence analogs
  (equity: reversal; indexed commodities: reversal; bonds, FX: no effect at one week). The 20-day reading is split:
  reversal at the front, continuation from about the second week (BK2012, NBIM2014).
- Every published multi-day magnitude here is a fraction of a small intraday move (betas 0.1 to 0.3 on r_LH, R2 under
  0.3%), which is relevant to the V31 cost-feasibility rule.

## 3. Query log

Full log with times and outcomes: reports/stage_e23_briefs/mech_pages/M4_INTRADAY_MOM/fetch_log.md. Summary:

| # | time (PDT) | tool | query | kept |
|---|---|---|---|---|
| 1 | 02:18 | WebSearch | Baltussen van Bekkum Da "Indexing and stock market serial dependence around the world" pdf | BvD2019 |
| 2 | 02:19 | WebSearch | Gao Han Li Zhou "market intraday momentum" next day reversal last half-hour return subsequent days | none |
| 3 | 02:20 | WebSearch | "Market intraday momentum" Gao Han Li Zhou pdf olin.wustl.edu | GHLZ2015 |
| 4 | 02:20 | WebSearch | Barbon Buraschi "gamma fragility" daily autocorrelation index returns dealer gamma pdf | none (stock-level, intraday) |
| 5 | 02:20 | WebSearch | commodity futures daily return autocorrelation short-term reversal one-day lagged return predicts next week returns time series | DTTY2024 |
| 6 | 02:22 | WebSearch | intraday momentum futures persistence over following days weekly horizon ... | Coffee2025 (unreachable) |
| 7 | 02:22 | WebSearch | short-term trend following futures lookback one week decay after 2010 ... | NBIM2014 |
| 8 | 02:23 | WebSearch | E-mini S&P 500 futures daily return negative autocorrelation 2010-2023 ... | Mesfin2026 (abstract) |
| 9 | 02:24 | WebSearch | "last half-hour" OR "end-of-day" futures return predicts next week returns ... 5-day 20-day horizon | none new |
| 10 | 02:25 | WebSearch | futures "daily" time-series momentum one-day lookback ... next 5 to 20 days ... post-2010 | none new |

Queries 9 and 10 added no new relevant source (stopping rule (b)). 10 of 60 WebSearch calls used; no over-budget
notice. Local reuse: BDLM2021 (two saved copies), BK2012, BBBM2021 found by grep of reports/stage_e10_research/,
reports/stage_e13_briefs/pages/, reports/stage_e20_briefs/; BDS2024 (Baltussen, Da, Soebhag, "End-of-Day Reversal",
reports/stage_e20_briefs/pages/ZC/baltussen_da_soebhag_eod_reversal_2024.pdf.txt, sha256 64b43ec6...585) was checked
and not used: it is a stock cross-section result whose reversal is within the next day.

## 4. Not verified or not reached

- Coffee2025 (J. Commodity Markets, doi 10.1016/j.jcomm.2025.100537): landing page is JavaScript-only (curl and
  scrapling fetch returned no text), OpenAlex has no abstract, the publisher answered 403. Its "carry over across days"
  claim is [unverified] and not used.
- Mesfin2026: abstract only; full text not read.
- GHLZ published JFE version not read; the December 2015 working paper (third-party host) was used. The next-open
  claim may be worded differently in the published version.
- Figure values (BDLM2021 Fig. 5; NBIM2014 Chart 2) are my visual readings of rendered pages, not tabulated numbers.
- Not searched further: Barbon and Buraschi "Gamma Fragility" and Ni, Pearson, Poteshman and White (stock-level gamma
  and daily autocorrelation); Heston, Korajczyk and Sadka (2010) read only through BDLM2021's citation.
- No source gives a per-event bp for a 5- or 20-day hold after any member's trigger; the bp figure in the H6 paragraph
  is my arithmetic illustration, not published.
