# RD6 re-dig: E.13's non-gamma information sources (RedigReader-InfoSources-OpusHigh)

Reader RD6, Stage E.25 (research only). Second run, started 06:21 PDT 2026-10-18 (the wave-1 run, 01:38-02:00 PDT,
was cut by a usage limit; its saved pages and its OpenAlex and Semantic Scholar pulls in pages/RD6/ are reused and
logged in section 9). Third pass (this one) 11:16-11:50 PDT finished the file. No market data was read. There was no
purchase, quote or sign-up. Times are PDT unless marked UTC. Dealer gamma (E.13 row 7) belongs to RD5. Volatility filters (E.13 row 5) belong to R12. The FOMC
pre-announcement reversal belongs to R6 (R6-C3). Treasury auctions belong to RD2. This file cites those readers and does not redo their work.

STATUS: COMPLETE (with the gaps listed in section 10).

## 1. Answer (at most 250 words)

On these sources the deeper reading mostly supports E.13. It weakens two of E.13's factual statements.

- **NG storage (E.13 row 2a; it sits behind K4-ngpre-01, C1 and C1b).** The literature shows decay and latency capture:
  - the announcement-day premium is "not present" in 2014-2018;
  - the pre-release drift fell to -0.15% per event after 2014. That is about 5.3 MNG ticks at $3.50, below the 8.03-tick hurdle;
  - HFTs in the first 50 ms "earn the majority of profits".
  The C1/C1b FAIL fits this record. No forward citation replicates an NG intraday edge.
- **Weather (row 3, C4).**
  - The mechanism is real but contemporaneous. Hsu-Park-Zhu (2026) find that forecast revisions, not realized
    weather, move NG prices (abstract only).
  - The only tradable published form is still a 5-day NG1/NG2 spread, gross and overnight. Its single forward citer is
    a coffee paper.
  - E.13's "no archive before 2021" is too strong. Monteux used the free NOAA GEFS Reforecast V2 (1984 onward, a fixed
    2012 model, so not the vintages the market saw). Operational GEFS on AWS starts 2017-01-01. ECMWF has been fully open
    (CC-BY-4.0) since 2025-10-01.
  - C4 still has no published intraday gross, so it fails the V31 gate as stated.
- **COT (row 1).** The only direct test (Dreesmann et al. 2023) fails at portfolio level. No study of the Friday
  14:30 CT release window was found. This supports "not pursued".
- **Overturned closure: FOMC text (row 8b).** E.13 set the thesis aside on timing. Its full text trades 12:50-14:50 CT,
  which is flat before 15:10 CT. The figures are 23.34 bp per event net of spread, 2011-2020, n 71, about 56 MES ticks
  at ES 6,000. That candidate is R6-C3. RD6 adds one point: OpenCitations shows zero citers of the SSRN version.
- **E.13 ranking (C1 > C2 > C3).** RD5, RD7 and this file support the low odds behind all three. None reverses the
  order.

New sized candidates: none. One unsized pointer (RD6-C1).

## 2. Candidate hypotheses

Zero sized candidates. The reason: none of the sources re-read here publishes a gross per trade for an intraday,
flat-by-15:10 trade, except the FOMC reversal. That one is owned by R6 (R6-C3) and is not duplicated here, so N is not
counted twice. One unsized pointer is listed so the lead can see why it fails the V31 gate.

| id | hypothesis | mechanism | instruments | entry (CT) | hold | trades/yr | best source | grade | published effect | gross/trade (micro ticks) | gross/net | owned data | research-window testable | overlap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RD6-C1 (pointer, unsized) | Sign of the change in gas-weighted HDD/CDD between consecutive NOAA GEFS 00Z runs predicts the NG return from the open to the forced flatten | Slow diffusion of forecast revisions into NG prices (if any; the published evidence is contemporaneous) | NG / MNG | 08:30 (after the 00Z run; the 12Z run completes about 11:15-12:15 CT per E.13 I-31) | to 15:08 | about 150-250 (E.13, UNSOURCED) | Hsu, Park, Zhu (2026) SSRN 10.2139/ssrn.6985300 (abstract); Monteux et al. (2025) NAJEF (full text, daily, 5-day) | working-paper [secondary-only]; peer-reviewed (daily) | contemporaneous effect only; Monteux: 5-day spread, gross, CAR/Sharpe tables, no per-trade figure | null (none published) | unknown | no (GEFS GRIB is free, not owned; NG bars are owned only for the stores bought) | partial: AWS GEFS 2017-01-01 onward, mostly inside V24-read windows; Reforecast V2 1984 onward is not real-time vintage | K4-ngwx-01 (excluded X-13), K9M-017 (excluded); E.13 C4 |

Cross-reference (not an RD6 candidate): R6-C3, the FOMC pre-announcement reversal on the E-mini, 12:50-14:50 CT. Section 8 gives
the RD6 verdict check on E.13's row-8b treatment, and section 3 rows E15-E17 give the full-text figures.

## 3. Evidence table

| # | Claim | Number | Verbatim quote | Location | Source | Grade | Saved path |
|---|---|---|---|---|---|---|---|
| E1 | NG EIA-storage announcement-day premium decayed; absent 2014-2018 | effect absent 2014-2018 | "the effect is not present in the most recent period (2014–2018), which saw a sharp decline in energy prices" | p. 7 fn (Table A.3 note) | Prokopczuk, Wese Simen, Wichmann (2021), Energy Journal 42(2), doi:10.5547/01956574.42.2.mpro, https://centaur.reading.ac.uk/90003/ | peer-reviewed (accepted version) | reports/stage_e13_briefs/pages/InfoSource/reading_ng_paper_final_round.pdf.txt (E.13 copy, sha256 0c6bdb1e97a0...) |
| E2 | Same: pre-announcement part halved after 2014 | -0.38%, -0.47%, then -0.15% per event | "the preannouncement effect has been even stronger in the past with average values of −0.38% and −0.47% for the first and second period, respectively. However, it has more than halved to only −0.15% in the most recent period after 2014." | Section IV, Table 7 Panel B | same | peer-reviewed | same |
| E3 | Same: strategy net of costs no longer pays | 3% p.a., Sharpe 0.5 recent | "In the more recent period, this has declined to only 3% and a Sharpe ratio of 0.5, which do not withstand transaction and funding costs." | Section V, Table 8 Panels B-C | same | peer-reviewed | same |
| E4 | Same: the whole day effect sits in the 2-hour window around the release | 99% | "the entire effect (99%) stems from the two hour window surrounding the announcement" | Section IV, Table 5 Panel A | same | peer-reviewed | same |
| E5 | Weather-forecast NG premium is a 5-day NG1/NG2 spread, gross | no costs | "Simulation based on daily NYMEX futures settlement prices, 4 April 1990 to 31 July 2019, without considering transaction costs and market slippage." | Table 5 note | Monteux, Arcuri, Gandolfi, Caselli (2025), NAJEF 80, 102494, doi:10.1016/j.najef.2025.102494 | peer-reviewed | reports/stage_e10_research/commodity/caselli_ng_weather.txt (E.10 copy, sha256 ddfea619f509...) |
| E6 | Same: realized-weather surprise is absorbed intraday the next day (contemporaneous, no lead) | qualitative | "when these forecasts are wrong, the market updates NG1 prices in the intraday trading session the following day" | Conclusions | same | peer-reviewed | same |
| E6b | Same: the forecast archive used is the free NOAA GEFS Reforecast V2 (fixed 2012 model), from Dec 1984 | 1984 onward | "The forecast data used in this study corresponds to the Reforecast V2 dataset, which consists of an 11-member ensemble of forecasts, produced every day from 00:00 UTC initial conditions from Dec 1984 to the present." | Section 3 (data), lines 355-358 of the text copy | same | peer-reviewed | same |
| E7 | Newest weather paper: NG prices move with forecast revisions (contemporaneous price discovery), asymmetric | qualitative | "weather forecasts and forecast revisions, rather than realized weather conditions, exert significant effects on natural gas prices. We further document a pronounced asymmetry in market responses" | abstract (Crossref record) | Hsu, Park, Zhu (2026), "Weather Forecasts, Forecast Revisions, and Natural Gas Price Discovery", SSRN wp, doi:10.2139/ssrn.6985300 (also 10.2139/ssrn.7411255) | working-paper [secondary-only] | pages/RD6/cr/10.2139_ssrn.6985300.json |
| E8 | WPSR-day third half-hour predicts last half-hour in crude (USO) | slope 0.038, t 2.12 (E.0 K4 quotes) | "returns on the third half-hour on EIA announcement days can significantly and positively predict the returns in the last half-hour" | abstract | Wen, Indriawan, Lien, Xu (2023), Energy Journal 44(4), doi:10.5547/01956574.44.4.zwen | peer-reviewed [secondary-only for this run: abstract via Crossref] | pages/RD6/cr/10.5547_01956574.44.4.zwen.json |
| E9 | NG pre-release informed trading driven by forecasting skill; strategy Sharpe 1.26 | Sharpe 1.26 | "A simple trading strategy conditioned on the predictor would have generated an annualized Sharpe ratio of 1.26." | abstract | Gu, Kurov (2018), J. Futures Markets 38(9), doi:10.1002/fut.21926 | peer-reviewed [secondary-only] | pages/RD6/cr/10.1002_fut.21926.json |
| E10 | Sequential API->EIA announcements: crude inefficiency; predictor of surprises and pre-announcement returns in and out of sample | qualitative | "We also construct a predictor that can predict inventory surprises and preannouncement returns in‐sample and out‐of‐sample." | abstract | Alturki, Kurov (2021), J. Futures Markets, doi:10.1002/fut.22264 | peer-reviewed [secondary-only] | pages/RD6/cr/10.1002_fut.22264.json |
| E11 | HFTs in first 50 ms earn most NG storage-report profits; no pre-release informed trading found | 50 ms | "those who trade within the first 50 ms accurately incorporate the information contained in the storage report into prices, and earn the majority of profits" | abstract | Brigida, Pratt (2019), Studies in Economics and Finance, doi:10.1108/sef-03-2018-0092 | peer-reviewed [secondary-only] | pages/RD6/cr/10.1108_sef-03-2018-0092.json |
| E12 | Crowd (free) NG storage forecasts add nothing beyond the professional consensus | qualitative | "crowdsourced consensus forecast does not influence the market’s expectation of gas storage changes beyond what is already contained in professional consensus forecast" | abstract | Fernandez-Perez, Garel, Indriawan (2020), Energy Journal 41(5), doi:10.5547/01956574.41.5.afer | peer-reviewed [secondary-only] | pages/RD6/cr/10.5547_01956574.41.5.afer.json |
| E13 | Market impounds analyst storage forecasts before the EIA release; storage surprises partly reverse next week | qualitative | "the market promptly incorporates analyst forecasts into oil and gas prices prior to the EIA announcements" | abstract | Ederington, Lin, Linn, Yang (2019), Energy Journal 40(5), doi:10.5547/01956574.40.5.lede | peer-reviewed [secondary-only] | pages/RD6/cr/10.5547_01956574.40.5.lede.json |
| E14 | USDA releases: low-latency traders earn excess profits; lockup change did not remove them | qualitative | "excess profits can be earned quickly in agricultural commodity futures markets around United States Department of Agriculture (USDA) statistical releases" | abstract | Huang, Serra, Garcia (2022), AJAE, doi:10.1111/ajae.12356 | peer-reviewed [secondary-only] | pages/RD6/cr/10.1111_ajae.12356.json |
| E15 | FOMC pre-announcement reversal on the E-mini, net of spread, full sample | 17.86 bp per event, 180 events, annualized SR 1.02, 1997-2020 | "Reversal From 1:50 p.m. FOMCt to 3:50 p.m. FOMCt 180 17.86∗∗∗ 1.02" | Table 1.2 Panel A, p. 14 | Baglioni (2023), Essays in Financial Economics, PhD thesis, Insper, ch. 1 with R. M. Ribeiro, https://repositorio.insper.edu.br/handle/11224/7532; SSRN version doi:10.2139/ssrn.4182628 (2022) | thesis | pages/RD6/baglioni_2023_insper_thesis.txt (sha256 bd046c7e5e3f...; PDF 865a0c404e05...) |
| E16 | Same, post-Lucca-Moench subsample | 23.34 bp, 71 events, SR 1.60, 03/2011-01/2020 | "Reversal From 1:50 p.m. FOMCt to 3:50 p.m. FOMCt 71 23.34∗∗∗ 1.60" | Table 1.9 Panel A | same | thesis | same |
| E17 | Same: returns are net of the bid-ask; Sharpe annualization stated as multiplied by 8 | n/a | "Each strategy is implemented buying at the ask price and selling at the bid price" ... "in Panel A the daily Sharpe ratio is annualized (multiplied by 8)" | Table 1.2 note | same | thesis | same |
| E18 | COT short-term reversal strategy fails at portfolio level | qualitative | "a scenario analysis indicated underperformance of the CoT strategy when traded in a portfolio, confirming that the chosen strategy parameters could not generate excess Sharpe ratios" | abstract | Dreesmann, Herberger, Charifzadeh (2023), Int. J. Financial Markets and Derivatives 9(1/2) 76-113, doi:10.1504/ijfmd.2023.129093, https://ideas.repec.org/a/ids/ijfmkd/v9y2023i1-2p76-113.html | peer-reviewed [secondary-only] | pages/RD6/repec_dreesmann_2023_cot.html (sha256 38a52b9821c7...) |
| E19 | Macro surprises in energy: speculators damp the post-surprise drift (contemporaneous, not a lead) | qualitative | "We find that increased speculative trading lessens the impact of macroeconomic surprises on futures markets, as measured by price drift, volatility, and bid-ask spreads." | abstract | Boucher, Gagnon, Power (2025), The Energy Journal, doi:10.1177/01956574251369707 | peer-reviewed [secondary-only] | pages/RD6/cr/10.1177_01956574251369707.json |
| E20 | Temperature effects on NG are modelled daily from hourly realized temperatures (no forecast lead) | qualitative | "Hourly temperatures also allow us to construct measures of extreme temperatures that better match the timing of release of other market information." | abstract | Chen, Hartley, Lan (2023), J. Futures Markets, doi:10.1002/fut.22402 | peer-reviewed [secondary-only] | pages/RD6/cr/10.1002_fut.22402.json |
| E21 | NOAA GEFS on AWS: free, four runs a day; S3 listing starts 2017-01-01 | 2017-01-01 | "NOAA data disseminated through NODD are open to the public and can be used as desired." / S3 first prefix "gefs.20170101/" with cycles 00, 06, 12, 18 | License section; S3 ListObjectsV2 | AWS Open Data Registry, https://registry.opendata.aws/noaa-gefs/; https://noaa-gefs-pds.s3.amazonaws.com/ | exchange-regulator (official data page) | pages/RD6/aws_registry_noaa_gefs.html (68b5b534...); pages/RD6/s3_noaa_gefs_first.xml, s3_noaa_gefs_20170101.xml |
| E22 | NOAA GFS on AWS: listing starts 2021-01-01 (matches E.13's NCEI 2021 start) | 2021-01-01 | S3 first prefixes "gfs.20210101/", "gfs.20210102/" | S3 ListObjectsV2 | https://noaa-gfs-bdp-pds.s3.amazonaws.com/ | exchange-regulator | pages/RD6/s3_noaa_gfs_first_gfs.xml |
| E23 | ECMWF real-time products fully open since 2025-10-01 | CC-BY-4.0, no information cost | "ECMWF achieved a fully open data status on 01 October 2025. All products in the ECMWF Real-time Catalogue are now under a CC-BY-4.0 licence with no Information Cost." | page description | ECMWF, "Open Data Roadmap", https://www.ecmwf.int/node/29013 | exchange-regulator (official agency page) | pages/RD6/ecmwf_open_data_roadmap.html (016d30fe...) |
| E24 | Forward citations of the weather paper: one citer, unrelated (coffee) | 1 citer | title "Wavelet Decomposition of Coffee Price Dynamics - The Role of Temperature Shocks" (2025) | OpenCitations + Crossref | OpenCitations doi:10.1016/j.najef.2025.102494; Crossref 10.2139/ssrn.5975814 | exchange-regulator (index metadata) | pages/RD6/oc/10.1016_j.najef.2025.102494.json; pages/RD6/cr/10.2139_ssrn.5975814.json |
| E25 | Forward citations of Prokopczuk et al. (2021): 5 citers, none an NG intraday replication | 5 | citers: Bunek-Janzen 2024 (USDA RV), Bajatovic et al. 2024 (NG forecasting, x2), Cao et al. 2023 (USDA ML), Chen-Hartley-Lan 2023 (temperature) | OpenCitations | doi:10.5547/01956574.42.2.mpro | index metadata | pages/RD6/oc/10.5547_01956574.42.2.mpro.json; pages/RD6/citing_titles.tsv |
| E26 | Forward citations of the FOMC reversal SSRN paper: none in OpenCitations | 0 | "[]" (empty citation list) | OpenCitations v2 | doi:10.2139/ssrn.4182628 | index metadata | pages/RD6/oc/10.2139_ssrn.4182628.json |

Conversions (section 2 of the shared brief):
- E2 (post-2014 NG pre-announcement drift, -0.15% per event, gross): at NG $3.50/MMBtu, 0.0015 x 3.50 = $0.00525 = 5.25
  ticks of 0.001. The MNG tick is also 0.001, so this is 5.25 MNG ticks against the MNG hurdle of 8.03. On NG (full size) it is 5.25 ticks
  of $10, against an NG round trip the brief's table does not list. Price-level assumption: $3.50, stated, not read from data.
- E16 (FOMC reversal 2011-2020, 23.34 bp per event net of spread): at ES 6,000, 0.002334 x 6,000 = 14.0 ES points = 56
  ticks of 0.25, which is 56 MES ticks ($70 per MES) against the MES hurdle of about 3.0 ticks. At ES 5,500 it is 51 ticks. E15 (17.86 bp)
  at 6,000 is 10.7 points, or 43 ticks. The paper's returns already deduct the spread, so the gross is larger. The lead computes ratios
  and power. Note that n is about 8 a year, and the Sharpe annualization ("multiplied by 8") is ambiguous between x8 and x sqrt(8).

## 4. Negative evidence

- NG storage day premium decayed and is absent 2014-2018 (E1). The pre-release part fell to -0.15% after 2014 (E2). The
  strategy's 3% a year at Sharpe 0.5 "do not withstand transaction and funding costs" (E3).
- NG storage profits go to the first 50 ms (E11); USDA release profits go to low-latency traders (E14). Neither is available
  at retail latency or under Topstep's HFT ban.
- Free crowd forecasts add nothing beyond the paid consensus (E12). This supports E.13's point that the surprise needs a
  proprietary consensus.
- Weather: the published tradable form is daily and multi-day and gross (E5). Realized weather is absorbed the next day
  intraday (E6), and the newest paper is about contemporaneous price discovery (E7). There is no forward replication (E24).
- COT: the only direct strategy test fails at portfolio level (E18). Two WebSearch queries and two Crossref queries found
  no study of the Friday 14:30 CT release window (section 9). This is a search null, not evidence of absence.
- FOMC reversal (R6-C3): no forward citation (E26). The sample ends 2020-01. The companion pre-FOMC drift disappeared
  after 2015 (R6 quotes Kurov-Wolfe-Gilbert 2021). The program's own FOMC members K2-fomcpost-01 (Tier B) and
  K5-fomc-01 (NULL) are different rules, but they show no FOMC edge on the program's data.
- Macro surprises in energy: the drift is damped by speculative trading (E19). This is a contemporaneous effect.

## 5. Data and cost

- RD6-C1 (pointer): NOAA GEFS GRIB2 on AWS, free: "NOAA data disseminated through NODD are open to the public and can be
  used as desired" (E21, registry page fetched 2026-10-18T13:31:53Z). The listing starts 2017-01-01. GFS on AWS starts 2021-01-01
  (E22). The free GEFS Reforecast V2 (NOAA PSL) runs from Dec 1984, but it is a fixed 2012 model, not the operational vintage the
  market saw (E6b). Building gas-weighted HDD needs population or gas-demand weights; their source and cost are UNSOURCED here.
  ECMWF real-time products are free under CC-BY-4.0 since 2025-10-01 (E23), which corrects E.13's "ECMWF paid (UNSOURCED)" for
  real-time data. The ECMWF archive price was not read. NG/MNG bars: owned only for the stores bought (shared brief section 4;
  not read here).
- NG storage consensus (row 2a): proprietary (Bloomberg/WSJ), and the free crowd consensus is uninformative (E12). Unchanged
  from E.13.
- COT: CFTC, free, public domain (E.13 I-01). Release Friday 15:30 ET = 14:30 CT (search-result pointer, consistent with
  E.13). Not re-fetched.
- FOMC reversal: owned by R6 (E-mini 1-min bars; the program holds MES/ES stores for some windows; S&P exposure closed by
  STAGE_E_DESIGN D1 rule 5, as E.13 noted for C2).

## 6. Prop compatibility

- RD6-C1: entry after the 00Z run (before 08:30 CT), exit by 15:08 CT. Flat by 15:10. No scheduled-release P06 issue except on
  EIA Thursdays (09:30 CT storage), where size into the release must stay below maximum. Automation of GRIB download and
  parsing is the user's own, which is allowed. Order entry through the TopstepX API is allowed, with no HFT. MNG round trip
  5.35 ticks, hurdle 8.03.
- FOMC reversal (R6-C3): entry 12:50 CT, exit 14:50 CT, inside the session. P06 ("not at full maximum position size into a
  scheduled major release"): the entry is 10 minutes before the FOMC statement, so size must be below maximum. The DLL
  sizing is in R6.
- COT window (Friday 14:30-15:10 CT): 40 minutes inside the session. E.13's "arrives after Friday's last decision" reflects the
  program's decision times (t3 13:00), not a prop rule. No evidence exists to size it.
- Other firms: not assessed (R9).

## 7. Overlap with tested mechanisms

- RD6-C1: K4-ngwx-01 (excluded X-13, never tested) and K9M-017 (excluded, a 5-day spread). Gate-0 ML (gate0A, E.12/E.20) used no weather
  feature (the index lists none). So it is untested, but it shares the NG vehicle with K4-ngpre-01 (NULL), C1 and C1b (FAIL).
- NG storage literature (E1-E4, E9, E11-E13): K4-ngpre-01 (sell 90 min before, exit 30 min after; Tier A, E.5 NULL) is the same
  window as Gu-Kurov and Prokopczuk's pre-announcement drift. The NULL fits the post-2014 decay.
- WPSR third-half-hour (E8): already tested as K4-eiamom-01 (Tier B), MCL 14:30-14:59.
- FOMC reversal: R6-C3. Program relatives K2-fomcpost-01 (BUY 13:29, exit 15:04, momentum-free long; Tier B), K5-fomc-01
  (gold momentum, NULL), E-H1 and E-H2 (macro drift and post-release momentum). None fades the pre-announcement 24-hour return.
- COT: K3-cot-01 (excluded X-16). Never tested with content.

## 8. Verdicts supported, weakened or overturned

| Verdict | Effect | Quote | Source |
|---|---|---|---|
| E.18 / V32: C1b FAIL, NG near-miss closed (and E.17/V31 C1 stop) | SUPPORTS | "it has more than halved to only −0.15% in the most recent period after 2014" (E2); "those who trade within the first 50 ms ... earn the majority of profits" (E11) | Prokopczuk et al. 2021; Brigida-Pratt 2019. The external NG record shows decay and latency capture. Nothing published predicts that E.12's 2019-2024 NG h60 row would recur in 2010-2019. |
| E.13 ranking v3 (C1 > C2 > C3) | SUPPORTS (the low odds), no evidence to reorder | C1: as above. C2: RD5 finds GEX and NGE "virtually identical" and the paper's 48% negative share impossible in 2011-2019. C3: RD7 finds intraday TSMOM alpha "-0.10% intraday (t -0.24)" | RD6 (this file); RD5_redig_gamma.md; RD7_redig_trend_carry.md. All three ranked candidates are now closed or failed, as their low central odds (at most about 7%) implied. RD5's finding weakens the C2 rationale's "power is no longer the weak point" (RD5's verdict, cited). |
| E.13 C4 / row 3: "no forecast-vintage archive before 2021 was found" | WEAKENS (factual) | "Reforecast V2 dataset ... produced every day from 00:00 UTC initial conditions from Dec 1984 to the present" (E6b); S3 "gefs.20170101/" (E21) | Monteux et al. 2025; AWS NODD. Reforecasts are not vintages, so the clean-test problem stays: 2017-2018 is the only operational pre-2019 span. |
| E.13 row 3: "ECMWF paid (UNSOURCED)" | OVERTURNS (for real-time products, since 2025-10-01) | "ECMWF achieved a fully open data status on 01 October 2025 ... CC-BY-4.0 licence with no Information Cost." | ECMWF Open Data Roadmap (E23) |
| E.13 C4 ranked 4th: weak evidence | SUPPORTS | "weather forecasts and forecast revisions, rather than realized weather conditions, exert significant effects on natural gas prices" (E7, contemporaneous); "without considering transaction costs and market slippage" (E5) | Hsu-Park-Zhu 2026 [secondary-only]; Monteux 2025 |
| E.13 row 1 / K3-cot-01 excluded: COT not pursued | SUPPORTS | "the chosen strategy parameters could not generate excess Sharpe ratios" (E18) | Dreesmann et al. 2023 [secondary-only] |
| E.13 row 2a/2b/4 and ranking section 2: surprise-against-consensus sources not carried | SUPPORTS | "crowdsourced consensus forecast does not influence the market’s expectation ... beyond what is already contained in professional consensus forecast" (E12); USDA "excess profits can be earned quickly" by low-latency traders (E14) | Fernandez-Perez et al. 2020; Huang et al. 2022 [secondary-only] |
| E.13 row 8b: FOMC reversal thesis set aside ("13:00 is after every t3 except equity's 13:00 bar close") | WEAKENS/OVERTURNS the timing dismissal | "buying (selling) E-Mini S&P 500 at 1:50 p.m. EST of scheduled FOMC days, if the pre-announcement return is negative (positive), and closing the position two hours later" (thesis p. 4); "Reversal ... 71 23.34∗∗∗ 1.60" (Table 1.9) | Baglioni 2023 (E15-E17). The trade is 12:50-14:50 CT, inside 15:10, and its published net figure is far above the MES hurdle (section 3 conversion). The candidate is R6-C3. It is unreplicated (E26), the sample ends 2020, and n is 8 a year. |
| E.13 row 6: economic-surprise indices, evidence none/weak | SUPPORTS | "increased speculative trading lessens the impact of macroeconomic surprises on futures markets, as measured by price drift" (E19) | Boucher et al. 2025 [secondary-only] |

## 9. Fetch log

Machine log: reports/stage_e25_briefs/pages/RD6/_fetchlog.tsv. Columns: url, UTC, sha256, path, status, tool, bytes. It has 76 rows
after this pass. Its status column holds an HTTP code for the earlier rows and ok/httpNNN for the rows this pass added. The
OpenAlex and S2 pulls of the wave-1 run are in pages/RD6/openalex/_log.tsv and pages/RD6/s2/_log.tsv.

Rows added this pass (UTC 2026-10-18):
- https://api.crossref.org/works/10.2139/ssrn.5975814 | ok | pages/RD6/cr/10.2139_ssrn.5975814.json | curl
- https://api.crossref.org/works?query.bibliographic=FOMC announcement reversal Baglioni Ribeiro | ok | pages/RD6/cr/q_fomc_reversal.json | curl
- https://api.crossref.org/works?query.bibliographic=Commitment of Traders report trading signal ... | ok | pages/RD6/cr/q_cot_reversal.json | curl
- https://api.opencitations.net/index/v2/citations/doi:10.2139/ssrn.4182628 | ok (empty list) | pages/RD6/oc/10.2139_ssrn.4182628.json | curl

Blocked or forbidden:
- dataspace.princeton.edu: the 2022 senior thesis "Weather Forecasts and Natural Gas Futures Price Dynamics" is blocked
  (WebFetch 401; scrapling get hit a "Verification required" wall, 13:31Z).
- iaee.org (Hsu, Zhu, Petty, Zhang conference abstract, forecasts 2014-2016): terms forbid ("No content ... may be
  downloaded"; terms_log line 15). Not fetched; known only from a search result.

Terms: all hosts used are already in terms/terms_log.md: api.crossref.org (lines 128-129, 146), api.opencitations.net
(127, 130, 147), ideas.repec.org (59, 152), registry.opendata.aws and the NOAA S3 buckets (155), www.ecmwf.int (159),
repositorio.insper.edu.br (94), iaee.org (15, forbidden). No new terms lines this pass.

Budget notices:
- 2026-10-18T08:44:33Z: Firecrawl "Insufficient credits", with a per-minute limit hit at 08:42Z.
- 2026-10-18T08:47:22Z: OpenAlex HTTP 429 "Insufficient budget". Not called again (lead: exhausted until 17:00 PDT).
- WebSearch: 4 calls this pass (cap 15). The topics were the GFS 12z intraday reaction, a COT release-day event study, the Hsu-Park-Zhu full
  text, and the Kurov-Sancetta-Wolfe abstract. They are pointers only and none is used as evidence. No over-budget notice.

## 10. Unfinished and unverified

- Full texts not read (abstract only, [secondary-only]): Hsu-Park-Zhu 2026 (SSRN), Gu-Kurov 2018, Alturki-Kurov 2021,
  Brigida-Pratt 2019, Fernandez-Perez et al. 2020, Ederington et al. 2019, Huang et al. 2022, Dreesmann et al. 2023,
  Boucher et al. 2025, and Kurov-Sancetta-Wolfe 2022 (no abstract in Crossref; a search snippet says it covers UK macro
  releases and FX futures, which is outside this file's sources [unverified]).
- Princeton senior thesis (2022) on intraday NG response to consecutive temperature-forecast changes: blocked. It is
  [unverified] and the most direct intraday weather source found.
- No intraday event study of GFS/GEFS run releases was found. A USPTO patent (US 7844427) describes traders reacting to the 12Z run
  around 11:00-12:00 ET. It is a pointer only and was not fetched.
- Forward citations rely on OpenCitations and Crossref only. Coverage of SSRN and theses is thin, so zero citers can be an index gap.
- The NOAA GFS archive at NCEI before 2021 and the TIGGE archive (ECMWF research ensemble) were not checked: [unverified].
- VIX/Cboe (row 5) and Treasury auctions (row 8a) were not re-read here; they belong to R12 and RD2.
