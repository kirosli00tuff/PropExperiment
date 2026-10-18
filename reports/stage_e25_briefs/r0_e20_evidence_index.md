# Stage E.25 R0: E.20 evidence index (extraction)

Total evidence rows: 157 across 17 product files (reports/stage_e20_briefs/product_<ROOT>.json, key `evidence`).
Rows per root: 6E 9, CL 12, GC 14, HE 8, LE 8, NG 10, NQ 10, RTY 15, TN 6, UB 6, ZB 8, ZC 10, ZF 6, ZL 6, ZN 13, ZS 9, ZT 7

Extraction rules: fields copied from the JSON; effect truncated to 90 characters, source to 80 ("..." marks truncation); `|` in a cell replaced by `/`. "not stated" means the field is absent or empty in the JSON.

D8 round trip in vehicle ticks: not stated per root in reports/stage_e20_product_summary.md (grep for D8 finds only prose mentions and the Part A proposal table). No value is entered here.

Ratio as stated: the evidence JSON rows carry no ratio field. The summary states ratios to D8 only for Part A proposal features (section 1.4), not for evidence rows, so the last column reads "not stated" for every row. No ratio was computed.

| root | id | effect | hold | gross ticks | gross/net | grade | source | ratio as stated |
|---|---|---|---|---|---|---|---|---|
| 6E | E1 | Market intraday momentum ROD->LH, currency futures (Baltussen et al.) | 30 min (last half hour) | 0.75 | gross | primary | Baltussen, Da, Lammers, Martens (2021), Hedging demand and market intraday mo... | not stated |
| 6E | E2 | Post-London-fix U.S. dollar depreciation (EUR appreciates after the 16:00 London fix) | 6 h (10:00-16:00 CT); inside the 6E day session up to F 1... | 6.06 | gross | primary | Krohn, Mueller, Whelan (2024), Foreign Exchange Fixings and Returns Around th... | not stated |
| 6E | E3 | Pre-ECB-fix U.S. dollar appreciation (EUR depreciates 02:00-08:15 ET) | 6.25 h, entirely before t1 (07:50 CT); reachable only by ... | 7.84 | gross | primary | Krohn, Mueller, Whelan (2024), JF | not stated |
| 6E | E4 | ECB-fix 15-minute reversal and its move after July 2016 | 15 min (below the v2 60-min minimum) | 2.13 | gross | primary | Krohn, Mueller, Whelan (2024), JF | not stated |
| 6E | E5 | End-of-month WMR fix reversal (contrarian after the 4 pm fix) | 1-15 min (below the v2 60-min minimum) | not stated | net | primary | Evans (2018), Forex trading and the WMR Fix, J. Banking & Finance 87, 233-247... | not stated |
| 6E | E6 | Month-end equity-hedge rebalancing before the 4 pm fix (Melvin and Prins) | 60 min (15:00-16:00 London = 09:00-10:00 CT standard weeks) | 3.15 | gross | primary | Melvin, Prins (2015), Equity hedging and exchange rates at the London 4 p.m. ... | not stated |
| 6E | E7 | FOMC-day currency drift and reversal (foreign currencies appreciate before and at the a... | 12-hour half-day windows (overlaps the 6E day session onl... | not stated | gross | primary | Wang (2018), Essays on currency markets, PhD dissertation, Georgia Institute ... | not stated |
| 6E | E8 | ECB communication outside meeting days: no EUR/USD drift (null) | up to 20 min | not stated | gross | primary | Fanta (2025), ECB monetary policy communication: an event study on intraday r... | not stated |
| 6E | E9 | Intraday momentum and reversal in currency futures 2008-2024: not feasible after costs ... | last half hour | not stated | net | secondary-only | Aalto University master's thesis (2025), read by ProductReader-ZN | not stated |
| CL | E1 | ROD -> LH momentum in CL futures | 30 min | not stated | gross | primary | Baltussen, Da, Lammers, Martens (JFE 142, 2021), Table B3 and Table A3 | not stated |
| CL | E2 | EIA-day third half-hour -> last half-hour (USO) | 30 min | 6.28 | gross | primary | Wen, Indriawan, Lien, Xu, Energy Journal 44(5) 2023 149-171 (accepted version) | not stated |
| CL | E3 | Non-EIA-day first half-hour -> last half-hour (USO) | 30 min | 0.63 | gross | primary | Wen, Indriawan, Lien, Xu 2023 | not stated |
| CL | E4 | Overnight component -> last half-hour (USO) | 30 min | not stated | gross | primary | Wen, Indriawan, Lien, Xu 2023 | not stated |
| CL | E5 | r3 on non-EIA days (placebo null) | 30 min | not stated | gross | primary | Wen, Indriawan, Lien, Xu 2023 | not stated |
| CL | E6 | Pre-EIA buyer-initiated flow; price -0.25% before the release | about 2 h | not stated | unknown | secondary-only | Rousse and Sevi, Energy Journal 40(2) 2019 139-160 | not stated |
| CL | E7 | API and EIA inventory surprises move 5-min CL returns | minutes | not stated | unknown | secondary-only | Ye and Karali, Energy Economics 59 (2016) 349-364 | not stated |
| CL | E8 | Post-WPSR reversion within about 25 minutes | minutes | not stated | unknown | secondary-only | Geman and Li, Journal of Energy Markets 11(2) 2018 | not stated |
| CL | E9 | Intraday overreactions then reversals, energy most | <= 1 h | not stated | gross | secondary-only | Borgards, Czudaj, Van Hoang, Resources Policy (ISSN 0301-4207) | not stated |
| CL | E10 | Brent time-of-day long-short (not CL) | intraday | not stated | net | secondary-only | Haugom, Ouyang, Smith-Meyer, Stordal et al., Quantitative Finance 2025 | not stated |
| CL | E11 | Settlement window 13:28-13:30 CT: no systematic study found | n/a | not stated | unknown | secondary-only | Ge, Kang, Tang, Yang (AEA 2023 session paper) | not stated |
| CL | E12 | Passive-fill adverse selection in CL (execution) | n/a | not stated | n/a | primary | Lalor and Swishchuk, arXiv 2409.12721 | not stated |
| GC | E1 | ROD->LH market intraday momentum (GC row; commodity portfolio) | 30 min ending 12:30 CT | 3.1 | gross | primary | Baltussen, Da, Lammers, Martens, JFE 142 (2021) 377-403 | not stated |
| GC | E2 | London fix window in GC before/after 2015 auction reform | 10/30/60 min | 6.7 | gross | primary | Aspris, Foley, Gratton, O'Neill (2017) Transparency in Commodities Markets, E... | not stated |
| GC | E3 | PM fix leakage under the pre-2015 telephone fixing (context; published 2014) | 4 min after fix start | not stated | gross | primary | Caminschi & Heaney, J. Futures Markets 34(11) 2014 1003-1039 (UWA AAM) | not stated |
| GC | E4 | Hat-shaped 24h gold pattern; drop into AM/PM London fix | 30 min | -3.0 | gross | primary | Donati & Jung, Gold Price Dynamics Around the Clock, CBS MSc thesis 2019 | not stated |
| GC | E5 | Abnormal-return-day momentum (S1, look-ahead) and next-day contrarian for gold (S2) | to day end (GMT+3) | 12.6 | gross | primary | Caporale & Plastun, Financial Markets and Portfolio Management 35 (2021) 353-368 | not stated |
| GC | E6 | FOMC surprise response in gold futures | 5-10 min | not stated | gross | primary | Awartani, Hussain, Virk, IRFA 103486 (2024), AAM | not stated |
| GC | E7 | Intraday overreaction-reversal (turning points, ex post) | to next turning point | not stated | gross | primary | Borgards, Czudaj, Hoang, Resources Policy 71 (2021) 101966 | not stated |
| GC | E8 | Negative day (open-to-close) returns in COMEX gold | day session | not stated | unknown | secondary-only | Blose, Gondhalekar, Kort, J. Econ. Finance 42(3) 2018; Blose & Gondhalekar AE... | not stated |
| GC | E9 | Flight to gold after extreme negative 5-min S&P 500 returns (K8-flight source) | minutes | not stated | unknown | secondary-only | Baur & Kuck, Finance Research Letters 33 (2020) | not stated |
| GC | E10 | Fix reform, daily gold futures (not intraday) | daily | not stated | unknown | primary | Crain, Hoelscher, Jones, ACRN JoFRP 9 (2020) 177-197 | not stated |
| GC | E11 | First half-hour momentum in SHFE gold; disappears after night trading | 30 min | not stated | unknown | secondary-only | Zhou (Ivy) et al., Night trading momentum..., ACFR conference paper | not stated |
| GC | E12 | Macro announcement response in gold futures complete within 90 s | 90 s | not stated | unknown | secondary-only | Smales & Yang, IRFA 41 (2015) 292-302 | not stated |
| GC | E13 | Fix reform improved spreads and depth in exchange products | n/a | not stated | unknown | secondary-only | Aspris, Foley, O'Neill, JFM 40(11) 2020 | not stated |
| GC | E14 | COMEX settlement window (12:29-12:30 CT) effects | not stated | not stated | unknown | unverified | not stated | not stated |
| HE | E1 | Market intraday momentum ROD -> LH (rest-of-day return predicts last half hour), lean h... | 30 min (last half hour, 12:35-13:05 CT) | not stated | gross | primary | Baltussen, Da, Lammers, Martens (2021), Hedging demand and market intraday mo... | not stated |
| HE | E2 | Second-to-last half hour -> last half hour (SLH -> LH), lean hogs alone | 30 min (12:35-13:05 CT) | not stated | gross | primary | Baltussen et al. (2021), Table B3 Panel B, LH row | not stated |
| HE | E3 | Next-day direction after a locked-limit day (limit-induced under-reaction), lean hogs | settlement to settlement (includes the overnight gap) | not stated | unknown | primary | He, X. (2022), Essays on extreme events in agricultural futures markets, PhD ... | not stated |
| HE | E4 | Price path after limit moves: locked-limit days gap beyond the limit next day and stay;... | next-day open to +1 hour (locked); same-day after the tou... | not stated | gross | primary | He (2022) dissertation, ch.3 section on Figure 3.1 | not stated |
| HE | E5 | Flash events (large intraday moves) in lean hogs: no reversal documented; moves read as... | n/a (liquidity study) | not stated | unknown | primary | He (2022) dissertation ch.2 (= He, Serra, Garcia, AJAE 103(2) 2021, 743-764, ... | not stated |
| HE | E6 | Hog report window: NASS Quarterly Hogs and Pigs release time (after HE's 13:05 CT close... | n/a | not stated | unknown | primary | USDA NASS notice, Dec. 10, 2018 (ESMIS) | not stated |
| HE | E7 | Hog report window: USDA LMR swine report statutory deadlines inside the HE session | n/a | not stated | unknown | primary | 7 U.S.C. 1635j (US Code 2024 edition, govinfo) | not stated |
| HE | E8 | Limit events lead to persistent price changes (commodity futures, multi-market) | not stated | not stated | unknown | secondary-only | Janardanan, Qiao, Rouwenhorst (2019), On commodity price limits, J. Futures M... | not stated |
| LE | E1 | LC rest-of-day -> last half-hour momentum (null) | 30 min (12:35-13:05) | not stated | gross | primary | Baltussen, Da, Lammers, Martens (2021) JFE 142:377-403, Table B3 Panel B | not stated |
| LE | E2 | LC second-to-last half hour (SLH) -> last half hour | 30 min | 0.72 | gross | primary | Baltussen et al. (2021) Table B3 Panel B | not stated |
| LE | E3 | Commodity-class ROD -> LH momentum (LC in 'Softs') | 30 min | 0.8 | gross | primary | Baltussen et al. (2021) Tables 2, 5, 6, B3 | not stated |
| LE | E4 | Price-limit continuation next day (LC) | 1 day close-to-close (includes overnight gap) | 16.9 | gross | primary | Janardanan, Qiao, Rouwenhorst, 'On commodity price limits', WP Feb 2017 (Tabl... | not stated |
| LE | E5 | Cattle on Feed surprise reaction (next trading day) | 1 day close-to-close | 5.2 | gross | primary | Karali, Isengildina-Massa, Irwin (2019) JARE 44(3):591-604 | not stated |
| LE | E6 | USDA livestock report-day volatility (decay) | 1 day close-to-close | not stated | unknown | primary | Isengildina-Massa, Karali, Irwin, Adjemian (2016) NCCC-134 | not stated |
| LE | E7 | Intraday behaviour around LE/HE limit moves | intraday | not stated | unknown | secondary-only | He and Serra (2022) AJAE 104(5):1724-1746 (closed) | not stated |
| LE | E8 | Lean hog limit-up: price exceeds limit within 3 days (trade press) | 3 days | not stated | unknown | unverified | Technical Traders article citing Moore Research | not stated |
| NG | E1 | EIA storage-day short around the WNGSR release (pre- plus post-announcement), whole sample | 120 min (09:00-11:00 ET standard) | 10.3 | gross | primary | Prokopczuk, Wese Simen, Wichmann (2021), The Natural Gas Announcement Day Puz... | not stated |
| NG | E2 | Same storage-day short, after 2011 (the decay result) | 120 min | 1.68 | gross | primary | Prokopczuk, Wese Simen, Wichmann (2021), Energy Journal 42(2) | not stated |
| NG | E3 | Decomposition of the storage-day return: 99% inside (-90,+30); half pre (-90,-5), half ... | n/a (windows of 85 and 35 min) | 11.1 | gross | primary | Prokopczuk, Wese Simen, Wichmann (2021) | not stated |
| NG | E4 | Pre-announcement drift traded on an analyst-forecast predictor (informed-trading signal) | 85 min | not stated | unknown | primary | Gu and Kurov (2018), J. Futures Markets 38(9) 1079-1096, doi 10.1002/fut.2192... | not stated |
| NG | E5 | Market intraday momentum ROD -> LH, NG's own regression row | 30 min (13:00-13:30 CT) | not stated | gross | primary | Baltussen, Da, Lammers, Martens (2021), JFE 142, 377-403, Table B3 Panel B (o... | not stated |
| NG | E6 | Week-to-week reversal of NG storage surprises; prices impound analyst forecasts before ... | n/a | not stated | unknown | secondary-only | Ederington, Lin, Linn, Yang (2019), EIA Storage Announcements, Analyst Storag... | not stated |
| NG | E7 | Leveraged/futures-ETF rebalancing pressure in NG (and VIX, oil, gold, silver) | daily (open to close per a search summary; [unverified]) | not stated | unknown | secondary-only | Todorov (2021), Passive funds affect prices: evidence from the most ETF-domin... | not stated |
| NG | E8 | Weather-forecast revisions and intraday NG futures moves (00 and 18 UTC runs) | n/a | not stated | unknown | unverified | Princeton senior thesis 'Weather Forecasts and Natural Gas Futures Price Dyna... | not stated |
| NG | E9 | NG settlement window (13:28-13:30 CT), NG post-release reversal, NG time-of-day seasona... | n/a | not stated | unknown | unverified | searches logged in md section 5 | not stated |
| NG | E10 | Intraday patterns in NG futures from HFT data (VPIN/ML signals) | n/a | not stated | unknown | unverified | Song, Lopez de Prado, Simon, Wu (2015), Intraday Patterns in Natural Gas Futu... | not stated |
| NQ | E1 | Market intraday momentum, NQ regression | 30 min (14:30-15:00 CT) | not stated | gross | primary | Baltussen, Da, Lammers, Martens, Hedging demand and market intraday momentum,... | not stated |
| NQ | E2 | Equity 1/N portfolio eta(r_ROD) | 30 min | 14.31 | gross | primary | Baltussen, Da, Lammers, Martens, Hedging demand and market intraday momentum,... | not stated |
| NQ | E3 | Subsample stability, pooled equity | 30 min | not stated | gross | primary | Baltussen, Da, Lammers, Martens, Hedging demand and market intraday momentum,... | not stated |
| NQ | E4 | Gamma conditioning (S&P 500 futures only) | 30 min | not stated | gross | primary | Baltussen, Da, Lammers, Martens, Hedging demand and market intraday momentum,... | not stated |
| NQ | E5 | First-half-hour predictor and agreement filter | 30 min | 8.78 | gross | primary | Baltussen, Da, Lammers, Martens, Hedging demand and market intraday momentum,... | not stated |
| NQ | E6 | Overnight return -> last half hour; threshold form | 30 min | not stated | unknown | unverified | Rosa, Understanding intraday momentum strategies, J. Futures Markets 42(12) (... | not stated |
| NQ | E7 | Post-2020 SPX retest (unreviewed blog) | 30 min | not stated | gross | secondary-only | firmtape via dev.to [shared, see shared/equity_class_notes.md] | not stated |
| NQ | E8 | Persistence 2008-2024 (Aalto thesis) | 30 min | not stated | unknown | primary | Aalto master's thesis [shared, see shared/aalto_thesis_notes.md] | not stated |
| NQ | E9 | Gamma and intraday momentum after 0DTE | not stated | not stated | unknown | unverified | Adams, Dim, Eraker, Fontaine, Ornthanalai, Vilkov (2026 draft) [shared, see s... | not stated |
| NQ | E10 | MNQ OHLCV intraday signal falsification (preprint, not a ROD test) | various | not stated | net | primary | Mesfin, arXiv 2605.04004 (2026) | not stated |
| RTY | E1 | Rest-of-day to last half-hour momentum (ROD -> LH), Russell 2000 futures | 30 min (14:30-15:00 CT) | not stated | gross | primary | Baltussen, Da, Lammers, Martens, J. Financial Economics 142 (2021) 377-403, T... | not stated |
| RTY | E2 | Overnight-plus-first-half-hour to last half-hour (ONFH -> LH), Russell 2000 futures | 30 min (14:30-15:00 CT) | not stated | gross | primary | Baltussen et al. (2021) Table B1 Panel B | not stated |
| RTY | E3 | First half-hour (ONFH) sign -> last half-hour, SPY | 30 min | 5.3 | gross | primary | Gao, Han, Li, Zhou, J. Financial Economics 129 (2018) 394-414; read as workin... | not stated |
| RTY | E4 | E3 after bid-ask spread costs | 30 min | 6.32 | net | primary | Gao et al. (2015 WP) Table 10 | not stated |
| RTY | E5 | First half-hour -> last half-hour, IWM (Russell 2000 ETF), mean-variance form | 30 min | not stated | gross | primary | Gao et al. (2015 WP) Table 12 Panel A | not stated |
| RTY | E6 | First half-hour sign -> last half-hour on FOMC statement days, SPY | 30 min | 15.9 | gross | primary | Gao et al. (2015 WP) Table 8 Panel B | not stated |
| RTY | E7 | Intraday time-series momentum, US (S&P 500 cash index) | 30 min | 5.22 | gross | primary | Li, Sakkas, Urquhart, J. Financial Markets 57 (2022) 100619 (accepted manuscr... | not stated |
| RTY | E8 | Hourly momentum vs market-maker net gamma, E-mini S&P | 10-120 min | not stated | gross | primary | Adams, Dim, Eraker, Fontaine, Ornthanalai, Vilkov, 'Do S&P 500 Options Increa... | not stated |
| RTY | E9 | ROD -> LH retest on SPX in the 0DTE era (UNREVIEWED) | 30 min | not stated | gross | unverified | firmtape, dev.to blog post, 2026-08-27 (unreviewed practitioner) | not stated |
| RTY | E10 | Pre-FOMC announcement drift, S&P 500 | 24 h (includes overnight); intraday portion on the FOMC m... | not stated | gross | primary | Lucca and Moench, NY Fed Staff Report 512 (rev. 2013); J. Finance 70 (2015) | not stated |
| RTY | E11 | Pre-FOMC drift after 2015 (decay) | 24 h | not stated | unknown | secondary-only | Kurov, Wolfe, Gilbert, Finance Research Letters 40 (2021) | not stated |
| RTY | E12 | End-of-day momentum/reversal from LETF rebalancing and option gamma imbalance (single s... | to the close | not stated | gross | primary | Barbon, Beckmeyer, Buraschi, Moerke, S/BF-HSG WP 2021/14 | not stated |
| RTY | E13 | Noise-area intraday momentum, SPY (V34 dropped as unsized) | intraday, variable | not stated | net | primary | Zarattini, Aziz, Barbon, 'Beat the Market', WP (2024-05-10; 2025-02-03 version) | not stated |
| RTY | E14 | Overnight return -> last half-hour; first half-hour not predictive (ETFs, 12 index futu... | 30 min | not stated | unknown | unverified | Liu and Tse, Int. Rev. Economics and Finance 48 (2017) | not stated |
| RTY | E15 | Intraday momentum and reversal in 20 equity, bond and FX futures, 2008-01..2024-10 (Aal... | n/a | not stated | unknown | secondary-only | Majorin (Aalto University thesis, 2025); shared, see shared/aalto_thesis_note... | not stated |
| TN | E1 | (absence) TN not in the Baltussen et al. ROD->LH sample | last 30 min | not stated | gross | primary | Baltussen, Da, Lammers, Martens, J. Financial Economics 142 (2021) 377-403 | not stated |
| TN | E2 | (context, no return effect) TN is one of six CBOT futures buckets in a DV01-volume liqu... | n/a | not stated | unknown | primary | Baker, McPhail, Tuckman, CFTC staff note, 2018-12-03 | not stated |
| TN | E3 | (class pointer, not TN) minute-scale reversion and hours-scale weak trending, pooled ov... | 1 minute | not stated | gross | primary | Safari, Schmidhuber, arXiv 2501.16772v2 (2025) | not stated |
| TN | E4 | (class pointer) rates-class ROD->LH and other Treasury-futures intraday effects | not stated | not stated | gross | unverified | [shared, see shared/rates_class_notes.md]; planning brief line 27-29 | not stated |
| TN | E5 | (class pointer) 10-year auction-day intraday price pressure | hours | not stated | gross | secondary-only | Robeco quant chart 2025-03; Fleming, Liu, Nguyen, NY Fed Staff Report 1188 (2... | not stated |
| TN | E6 | (class pointer) post-FOMC drift in long-term US bond futures (multi-day, out of scope) | ~15 days | not stated | unknown | secondary-only | Indriawan, Jiao, Tse, J. Banking and Finance (2021) | not stated |
| UB | E1 | ROD->LH intraday momentum, UB's own regression row | 30 min | 1.01 | gross | primary | Baltussen, Da, Lammers, Martens (JFE 142, 2021) Table B2 Panel B, Table A2 | not stated |
| UB | E2 | Pre-auction concession, 30-year bond (UB's auction tenor) | 180 min | 5.8 | gross | primary | Fleming, Liu, Nguyen, FRBNY Staff Report 1188 (March 2026, revised July 2026)... | not stated |
| UB | E3 | Post-auction reversal, 30-year bond | 180 min | 2.41 | gross | primary | Fleming, Liu, Nguyen (2026) Table 3, p.19 | not stated |
| UB | E4 | FOMC and employment windows: no auction-style V-shape | - | not stated | unknown | primary | Fleming, Liu, Nguyen (2026) p.4 | not stated |
| UB | E5 | Post-FOMC drift in long-term US bond futures | days (persists 15 days) | not stated | unknown | secondary-only | Indriawan, Jiao, Tse (J. Banking & Finance 123, 2021), doi 10.1016/j.jbankfin... | not stated |
| UB | E6 | Leveraged-ETF share (mechanism of E1): UB largest among bond futures | - | not stated | unknown | primary | Baltussen et al. (2021) Fig. 4 panel (b) | not stated |
| ZB | E1 | Pre-auction price pressure, 30-year bond, own auction (inverted-V yields around the auc... | 180 min (pre); 180 min (post) | 3.41 | gross | primary | Fleming, Liu, Nguyen (2026), 'Intraday Price Pressure and Order Flow Around U... | not stated |
| ZB | E2 | Cross-tenor spillover: 10-year (and 5-, 7-year) auctions put yield pressure on the 30-y... | 180 min (pre) | 3.83 | gross | primary | Fleming, Liu, Nguyen (2026), FRBNY SR 1188 | not stated |
| ZB | E3 | Post-FOMC yield decline (unconditional) and nulls before FOMC / around payrolls | up to 180 min after the statement | not stated | gross | primary | Fleming, Liu, Nguyen (2026), FRBNY SR 1188 | not stated |
| ZB | E4 | Market intraday momentum ROD -> LH, US 30-year T-bond futures row | 30 min | 0.95 | gross | primary | Baltussen, Da, Lammers, Martens (2021), JFE 142, 377-403 (on-disk copy) | not stated |
| ZB | E5 | End-of-month Treasury returns (daily, not intraday), 30-year futures | 1 to 6 trading days (includes overnight) | 6.72 | gross | primary | Hartley, Schwarz (2019), 'Predictable End-of-Month Treasury Returns', Rodney ... | not stated |
| ZB | E6 | Pre-release drift before ISM Non-Manufacturing (Services); 30-year bond futures in robu... | ~30 min | not stated | unknown | secondary-only | Kurov, Sancetta, Strasser, Wolfe (2019), JFQA (as logged by Stage E.0, item K... | not stated |
| ZB | E7 | Post-FOMC drift in long-term US bond futures, signed by the policy surprise; no pre-FOM... | multi-day | not stated | unknown | secondary-only | Indriawan, Jiao, Tse (2021), J. Banking & Finance 123, 106027 | not stated |
| ZB | E8 | Intraday momentum/reversal in bond futures 2008-2024: persists but mostly not after cos... | intraday | not stated | net | secondary-only | Aalto master's thesis (2025) [shared, see reports/stage_e20_briefs/shared/aal... | not stated |
| ZC | E1 | ROD -> last half-hour momentum, corn (CN) | 30 min | 0.26 | gross | primary | Baltussen, Da, Lammers, Martens (2021) JFE 142:377-403, Table B3 Panel B | not stated |
| ZC | E2 | ROD -> LH, 'Softs' pool (grains, livestock, softs) | 30 min | not stated | gross | primary | Baltussen et al. (2021) Table B3 Panel A | not stated |
| ZC | E3 | Commodity class eta(r_ROD) portfolio | 30 min | not stated | gross | primary | [shared, see shared/baltussen_notes.md] | not stated |
| ZC | E4 | WASDE surprise response, corn and soybeans | 10 min / 30 min / to close | not stated | gross | primary | Anderson, McKenzie, Noyes (2024) NCCC-134 working paper | not stated |
| ZC | E5 | WASDE-day intraday volatility curve, corn and soybeans | n/a | not stated | unknown | secondary-only | Lee and Park (2024), summarized by co-author E. Park, Southern Ag Today | not stated |
| ZC | E6 | Intraday jumps around USDA reports, corn | n/a | not stated | unknown | primary | Couleau, Serra, Garcia (2018) NCCC-134; AJAE 2020 | not stated |
| ZC | E7 | Corn-soy volatility and spillover on USDA days | n/a | not stated | unknown | primary | Bian, Serra, Garcia (2018) NCCC-134 | not stated |
| ZC | E8 | Adjustment speed after in-session releases | n/a | not stated | unknown | secondary-only | Adjemian and Irwin (2018) AJAE 100(4), p.1169, quoted by Isengildina-Massa (V... | not stated |
| ZC | E9 | Trend of USDA announcement effects (daily volatility) | daily | not stated | unknown | primary | Ying, Chen, Dorfman (2017) NCCC-134 | not stated |
| ZC | E10 | Limit-day continuation (9 commodities incl. corn) | next-day close-to-close (includes overnight) | not stated | gross | secondary-only | Janardanan, Qiao, Rouwenhorst, JFM 39(8) 2019 (WP Feb 2017) | not stated |
| ZF | E1 | Market intraday momentum ROD->last half hour, FV alone | 30 min | 0.62 | gross | primary | Baltussen, Da, Lammers, Martens (2021), Hedging demand and market intraday mo... | not stated |
| ZF | E1b | Same, government bond 1/N portfolio (class) | 30 min | 1.29 | gross | primary | Baltussen, Da, Lammers, Martens (2021), Hedging demand and market intraday mo... | not stated |
| ZF | E2 | 5-year auction pre-auction price pressure (short leg) | 180 min (clock: t2 10:20 CT h60 = close-100..close-40) | 1.19 | gross | primary | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | not stated |
| ZF | E3 | 5-year auction post-auction reversal (long leg) | 180 min (clock: t3 12:50 CT = release+47 to F 15:08 = rel... | 1.66 | gross | primary | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | not stated |
| ZF | E4 | Cross-tenor auction spillover onto the 5-year (10Y and 7Y auctions) | 2 x 180 min (clock legs as E2/E3) | 2.01 | gross | primary | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | not stated |
| ZF | E5 | FOMC and payrolls 3-hour windows: null pre-FOMC and NFP; post-FOMC yield decline (after... | 180 min | not stated | gross | primary | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | not stated |
| ZL | E1 | Market intraday momentum (r_ROD -> r_LH), soybean oil's own row | last 30 min of the day session | not stated | gross | primary | Baltussen, Da, Lammers, Martens (2021), JFE 142, 377-403, Table B3 Panel B (o... | not stated |
| ZL | E2 | Intraday cointegration of the soybean crush (ZS, ZL, ZM) in the day session; stronger o... | n/a | not stated | unknown | primary | Zhou, Bagnarosa, Gohin, Pennings, Debie (2023), 'Microstructure and high freq... | not stated |
| ZL | E3 | Biofuel-policy events (EPA RVO announcements, CARB quarterly reports, Reuters 'sources'... | 1 day (close to close) | not stated | gross | primary | Avileis and Swanson (2025), 'Drivers of Commodity Volatility in the Biofuel E... | not stated |
| ZL | E4 | Crush-spread mean reversion driven by intraday deviations from the USDA-implied process... | unknown | not stated | net | secondary-only | Abdoh and Chitavi (2025), 'Mean reversion of the soybean crush spread: A new ... | not stated |
| ZL | E5 | USDA reports and Dalian (DCE) soybean oil futures: minute volatility and volume react a... | n/a | not stated | unknown | secondary-only | Hu and Mallory (2022 NCCC-134; published J. Futures Markets 45(11), 2025) | not stated |
| ZL | E6 | Intraday momentum/reversal on 31 Chinese commodity futures (minute data, includes the D... | intraday | not stated | net | secondary-only | Yang, Goncu, Pantelous (2018), Int. Review of Financial Analysis 60, 177-196 | not stated |
| ZN | E1 | Market intraday momentum ROD->LH, bond futures | 30 min | 0.6 | gross | primary | Baltussen, Da, Lammers, Martens (2021), Hedging demand and market intraday mo... | not stated |
| ZN | E2 | Intraday momentum and reversal, 20 equity/bond/FX futures 2008-2024 | 30 min | not stated | net | unverified | Majorin (2025), Intraday momentum in futures markets, Aalto University MSc th... | not stated |
| ZN | E3 | 10-year auction day, pre-auction price decline | 180 min | 1.86 | gross | primary | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | not stated |
| ZN | E4 | 10-year auction day, post-auction price recovery | 180 min | 2.96 | gross | primary | Fleming, Liu, Nguyen (2026), FRBNY SR 1188 | not stated |
| ZN | E5 | Cross-tenor auction spillover into the 10-year | 2 x 180 min | 1.55 | gross | primary | Fleming, Liu, Nguyen (2026), FRBNY SR 1188 | not stated |
| ZN | E6 | 10-year auction day, ZN futures decline ahead of the auction | unstated | 4.2 | gross | primary | Houweling, Penninga, Martinetti (Robeco), Quant chart: US Treasuries up for a... | not stated |
| ZN | E7 | Pre-announcement drift (macro releases) | 30 min | not stated | gross | primary | Kurov, Sancetta, Strasser, Wolfe, ECB WP 1901 (2016); JFQA 54 (2019) | not stated |
| ZN | E8 | Pre-FOMC drift in Treasuries (null) | 24 h (2pm-2pm) | 0.0 | gross | primary | Lucca and Moench, The Pre-FOMC Announcement Drift, FRBNY SR 512 (rev. 2013); ... | not stated |
| ZN | E9 | Post-FOMC drift in long bond futures | up to 15 days | not stated | gross | secondary-only | Indriawan, Jiao, Tse (2021), J. Banking & Finance 123, 106027 | not stated |
| ZN | E10 | End-of-month Treasury futures returns (close-to-close, not intraday) | 1 to 5 days incl. overnight | 6.3 | gross | primary | Hartley and Schwarz (2019), Predictable End-of-Month Treasury Returns, Wharto... | not stated |
| ZN | E11 | Month-end index strike time (activity, no returns) | n/a | not stated | unknown | primary | Dyer, Fleming, Shachar, Treasury Trading at the Close, Liberty Street Economi... | not stated |
| ZN | E12 | First-15 to last-15 minute momentum, Chinese Treasury bond futures | 15 min | not stated | unknown | secondary-only | Zhang, Wang, Li (2021), Bond intraday momentum, J. Behavioral and Experimenta... | not stated |
| ZN | E13 | Intraday trend (>=1 h) and reversion (<=16 min), pooled incl. US 10-year futures | 1 h+ | not stated | gross | primary | Safari and Schmidhuber (2025), Trends and Reversion in Financial Markets on T... | not stated |
| ZS | E1 | ROD->LH market intraday momentum on soybeans: null; ONFH->LH reversal, negative OOS R2 | last 30 min (12:50-13:20 CT) | not stated | gross | primary | Baltussen, Da, Lammers, Martens (2021), J. Financial Economics 142, 377-403, ... | not stated |
| ZS | E2 | WASDE news -> soybean price reaction grows after 30 minutes (to the day close) | 10 min / 30 min / to close | not stated | gross | primary | Anderson, McKenzie, Noyes (2024), NCCC-134 proceedings | not stated |
| ZS | E3 | USDA report windows in ZS: volatility spike, no systematic under/overreaction | up to 60 min | not stated | unknown | primary | Joseph and Garcia (2016), AAEA selected paper, AgEcon 10.22004/ag.econ.235772 | not stated |
| ZS | E4 | Crush-spread intraday deviations from USDA-implied processing relationship mean-revert;... | not stated | not stated | net | secondary-only | Abdoh and Chitavi (2025), Int. Rev. Econ. Finance 101, 104186 | not stated |
| ZS | E5 | Soybean-complex intraday cointegration depends on liquidity and time of day (no trading... | n/a | not stated | unknown | primary | Zhou, Bagnarosa, Gohin, Pennings, Debie (2023), J. Commodity Markets 30, 1003... | not stated |
| ZS | E6 | Crop Progress good+excellent rating vs next-day November soybean price level | next day (report after the close) | not stated | unknown | primary | Bethlem, Lima, Lima (2023), Revista de Economia e Sociologia Rural 61(2) | not stated |
| ZS | E7 | Dalian soybean first-30-min -> last-30-min momentum (not the vehicle) | last 30 min | not stated | gross | primary | Jin, Kearney, Li, Yang (2020), J. Futures Markets 40(4) 632-650 (MPRA WP 9713... | not stated |
| ZS | E8 | Chinese soybean complex reacts to USDA reports at the Dalian open (not the vehicle) | minutes | not stated | unknown | secondary-only | Hu and Mallory (2025), J. Futures Markets 45(11) 2109-2127 | not stated |
| ZS | E9 | CBOT corn real-time USDA release volatility moderates quickly (class row; see ZC) | n/a | not stated | unknown | secondary-only | Adjemian and Irwin (2020), J. Commodity Markets 19, 100110 | not stated |
| ZT | E1 | 2Y auction pre-auction price decline (supply pressure), own tenor | 180 min (intraday) | 1.97 | gross | primary | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | not stated |
| ZT | E2 | 2Y auction post-auction price recovery, own tenor | 180 min (intraday) | 1.62 | gross | primary | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | not stated |
| ZT | E3 | Auction spillover to the 2Y note from 3Y, 5Y, 10Y auctions (yield pressure, both legs) | two 180-min legs (intraday) | 2.56 | gross | primary | Fleming, Liu, Nguyen (2026), Intraday Price Pressure and Order Flow Around U.... | not stated |
| ZT | E4 | Market intraday momentum ROD -> last half hour, US 2-year T-note futures (TU) | 30 min | 0.36 | gross | primary | Baltussen, Da, Lammers, Martens (2021), JFE 142, 377-403, Table B2 Panel B (d... | not stated |
| ZT | E5 | End-of-month 2Y Treasury excess return (last trading days of the month) | daily close-to-close over 1-2 days (includes overnight; N... | 6.7 | gross | primary | Hartley and Schwarz (2019), Predictable End-of-Month Treasury Returns, Rodney... | not stated |
| ZT | E6 | Pre-FOMC (day -1) drift at the short end: null for the 2Y | daily (not intraday) | 1.26 | gross | primary | Pan and Peng (2026 draft), The Pre-FOMC Drift in Long-Term Treasury Bonds (SAIF) | not stated |
| ZT | E7 | Pre-FOMC 24h window (2pm to 2pm) in the 2Y Treasury: null | 24 h (includes overnight) | not stated | gross | primary | Lucca and Moench, The Pre-FOMC Announcement Drift, FRBNY SR 512 (rev. Aug 201... | not stated |
