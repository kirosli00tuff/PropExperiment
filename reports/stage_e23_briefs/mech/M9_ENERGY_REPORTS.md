# M9_ENERGY_REPORTS: multi-day evidence after energy inventory reports (Stage E.23 P1.2)

Worker: MechanismReaderM9_ENERGY_REPORTS-OpusHigh. Brief: reports/stage_e23_briefs/brief_mechanism.md.
Written 2026-10-17, 02:16 to 02:28 PDT (times from `date`). Pages and fetch log:
reports/stage_e23_briefs/mech_pages/M9_ENERGY_REPORTS/ (`fetch_log.md`). Reused from E.20, not refetched:
reports/stage_e20_briefs/pages/NG/ and pages/CL/, and reports/stage_e20_briefs/shared/energy_class_notes.md.
Line numbers ("L") are lines of the saved pdftotext `.txt` next to each PDF.

Members: K4-eiafade-01 MCL (fade a >= 0.5% move over the first 15 minutes after the WPSR release),
K4-eiamom-01 MCL (the WPSR-day release half-hour 09:30-10:00 CT, traded with its sign in 14:30-14:59 CT),
K4-apipre-01 MCL (the sign of the post-API move 15:24-15:39 CT on Tuesday, traded Wednesday 07:30-09:29 CT,
before the EIA release), K4-ngpre-01 NG (fixed SELL 08:00-10:00 CT on every EIA storage-report day).
Docstrings read: strategy/members/k4/{eiafade,eiamom,apipre,ngpre}.py.

## Headline

No paper retrieved measures returns 5 or 20 trading days after an EIA petroleum, API or EIA gas storage
release. The published post-event evidence stops at days +1 and +2. Over those days it finds no relation
between the surprise and the price change, for crude oil and for natural gas (Miao et al. 2018; Linn et al.
2017 slides; Chebbi 2019, abstract only). The price impact is described as "immediate" and
"permanent" (Halova, Kurov and Kucher 2014). The only reversal on record is within hours (E.20 rows EN7 and
EN8, secondary only). The one multi-day mechanism in the family is a calendar one, for NG: a 5- or
20-day hold from a storage-report settlement contains the next 1 or 4 report days. Those days carry a
documented negative return premium (Prokopczuk, Wese Simen and Wichmann 2021), but the paper says the effect is
"not present" in 2014-2018.

## (1) Evidence table

| Key | Full citation | URL | Saved path | sha256 | Verbatim quote (location) | Claim supported: horizon / direction / magnitude / sample / instrument |
|---|---|---|---|---|---|---|
| MIAO18 | Miao, H., Ramchander, S., Wang, T., Yang, J., "The Impact of Crude Oil Inventory Announcements on Prices: Evidence from Derivatives Markets", version of February 3, 2017 (published in the Journal of Futures Markets, 2018 per search results; volume and pages [unverified]) | https://api.mountainscholar.org/server/api/core/bitstreams/9938aa1b-96a3-466b-ac76-7710737b5b72/content | mech_pages/M9_ENERGY_REPORTS/miao_etal_2018_mountainscholar.pdf | 1ecfa0baf499a1d4d6023a738ec7a8845ae3a6fd050df264e8266beb69653415 | (a) L929-935 (Table 12 discussion): "the coefficients for SUR_{t-1} and SUR_{t-2} are insignificant for all the 6 contracts with/without news-related control variables. That is, we do not find any persistence of the impact of inventory news announcements on the returns of futures." (b) L925-927: "γ0 is -0.482 for the nearest futures contract with t-statistics of -3.77". (c) L260-262: "The sample period of our study is June 16, 2003 to December 30, 2011, which includes 446 EIA inventory news". (d) Table 6, CL1 row, mean daily returns (%) on days -2..+2: positive shocks "0.21 -0.48 -0.17 0.19 0.14", negative shocks "-0.43 0.14 0.56 0.09 0.18" (no t-statistics given) | Days +1 and +2 only. The surprise does not predict next-day or day-after returns, in either direction. Day-0 response: -0.48% per 1-SD surprise (t -3.77). Days +1 and +2 average positive after both surprise signs (no t), consistent with the sample's upward drift, not with the surprise. NYMEX CL1-CL6 daily, 2003-06 to 2011-12, 446 releases |
| LINN17 | Linn, S. C., Ederington, L. H., Fernando, C. S., Guernsey, S. B., "Information, Price Levels and Price Volatility of Petroleum Product Futures Price", EIA Workshop on Financial and Physical Oil Market Linkages, September 19, 2017 (slides) | https://www.eia.gov/finance/markets/reports_presentations/2017/linn.pdf | mech_pages/M9_ENERGY_REPORTS/linn_2017_eia_slides.pdf | 747c0db28c493207e3a3f82cdd0156882f9f7fcaa38d9aa357bcba727a2872b0 | (a) slide 11 "Additional Results", L157-160: "No relation between surprises and prices changes on the two days following the release". (b) slide 5, L63: "Immediate response that does not revert (Halova et al. ,2014; this study)". (c) slide 6, L90: "Sample period: 7/16/2003 – 6/30/2017". (d) L150-151: "the response became more muted for Oil, Gasoline and Distillate but was intensified for Natural Gas." | Days +1 and +2. No surprise-driven continuation or reversal. Front-month oil, gasoline, distillate and natural gas, 2003-2017. Slides, not a paper: the tables behind the claim were not seen |
| HKK14 | Halova, M. W., Kurov, A., Kucher, O., "Noisy Inventory Announcements and Energy Prices", June 2013 version (forthcoming in the Journal of Futures Markets 34(10), 911-933, 2014) | https://web.archive.org/web/20260521011904id_/https://www.skidmore.edu/economics/documents/NoisyInventoryAnnouncementsAndEnergyPrices.pdf (the live Skidmore URL returned 404) | mech_pages/M9_ENERGY_REPORTS/halova_kurov_kucher_2014_wayback.pdf | fb443d48263fa90c930973765c08d95a30c06729b1056581af6d7f71685422e1 | (a) L642-664: "Figure 2 shows cumulative average returns (CARs) for crude oil and natural gas futures around the inventory announcements. ... Overall, the figure shows that the price impact of the news is immediate and appears to be permanent." (b) L527: "Our sample period extends from July 16, 2003 through June 27, 2012." (c) Table I, Panel B (L1380-1400), 15-minute window returns (%): "Natural Gas Storage Report / Natural Gas -0.26 -0.32 2.02 -0.03 0 0.55" (announcement mean, median, sd; non-announcement mean, median, sd) | No reversal of the release reaction. The CAR figure's horizon is not stated in the text read; the paper's event window is 10:25-10:40 ET (L597), so "permanent" is an intraday-scale judgment [horizon of Figure 2 unverified]. NG: mean -0.26% in the 15-min storage-report window against -0.03% on control days, 2003-2012 |
| CHEB19 | Chebbi, T., "The inventory change surprise's role in energy price behaviour", International Journal of Global Energy Issues 42(1-2), 1-20, 2019 | https://ideas.repec.org/a/ids/ijgeni/v42y2019i1-2p1-20.html | mech_pages/M9_ENERGY_REPORTS/chebbi_2019_repec.html | 5261692ed10b2709f0e6a2ad9beb620dcc4a88035d464208d63f0523d1fbbb67 | ABSTRACT ONLY (RePEc page; full text paywalled at Inderscience): "using a daily data from 9 November 2010 to 24 September 2013. The data set covers 150 inventory news ... we find strong evidence for the negative effect of inventory surprises on energy commodity futures returns on the day of the announcement. In contrast, the effect after the announcement day becomes insignificant." | After day 0: insignificant (the number of days is not stated in the abstract). Energy futures (crude and NG among them), 2010-2013, 150 releases |
| ANAT18 | Anatolyev, S., Seleznev, S., Selezneva, V., "Formation of Market Beliefs in the Oil Market", CERGE-EI Working Paper 619, June 2018 | https://cz.cerge-ei.cz/pdf/wp/Wp619.pdf | mech_pages/M9_ENERGY_REPORTS/anatolyev_etal_cerge_wp619.pdf | ef9817a4fdd50143d0ca62aa637ee6831985532b3ee3bb26318559585e886b20 | (a) L167-170: "expectations of future oil prices are revised uniformly, and by the same amount irrespective of maturity, which implies that the traders view inventory changes as mostly reflecting permanent or long lasting shocks". (b) L1511-1512: "Our results provide evidence in support of Hamilton's (2009) conjecture that, in the presence of inventories, all oil price movements have to be permanent and unpredictable." (c) L369: "our sample covers 7 years, from 2010 to 2016." | Theory plus an intraday term-structure test: no predictable reversal of the inventory-news move. Not a test of 5- or 20-day returns. Crude oil futures, many maturities, high-frequency data, 2010-2016 |
| LUO14 | Luo, H., Kang, S. B., "How does the Crude Oil Market Impound Inventory News Information? A Closer Look at High-frequency Prices and Trading Activities", working paper, July 22, 2014 | https://acfr.aut.ac.nz/__data/assets/pdf_file/0003/29946/Hong-Luo-CLInventoryNews.pdf | mech_pages/M9_ENERGY_REPORTS/luo_clinventorynews_aut.pdf | efa668a376155fa1941c8e0e92e0d1e5476be10cd8bb45cb7ba0c9439088984b | (a) L893-897: "inventory shock does not predict intraday crude oil futures returns after announcement. However, we find evidence for information leakage because the inventory shock predicts intraday and over-night returns before the announcement." (b) L73-74: "spanning the period July 1, 2003 through Dec 31, 2011". (c) L182: "period after the announcement (10:35AM to 11:00AM on Wednesday)" | Intraday only (to 11:00 ET): no post-release predictability. Pre-release leakage (overnight and intraday), which bears on the API-to-EIA window. CL nearby, 5-minute data, 2003-2011 |
| PWW21 | Prokopczuk, M., Wese Simen, C., Wichmann, R., "The natural gas announcement day puzzle", Energy Journal 42(2), 2021, accepted version (CentAUR 90003) | https://centaur.reading.ac.uk/90003/ (E.20 fetch) | reports/stage_e20_briefs/pages/NG/prokopczuk_wesesimen_wichmann_2021_ej_accepted.pdf (.txt beside it) | 4ffdbf721d5e0ef348b8477b863c77abe659fda1b839401d77ae6baf9c719c43 | (a) L288-292: "For the first nearby contract, the mean daily return on EIA announcement days is −0.37%, while it is only −0.09% on the remaining days. The difference is statistically significant at the 5% level." (b) Table 3, L1062: "1 -0.37 -0.09 -2.19 (0.029)"; L1054: "The sample includes 3982 daily returns from March 2003 to December 2018." (c) footnote 7, L310-311: "the effect is not present in the most recent period (2014–2018), which saw a sharp decline in energy prices." (d) L723-725: "In the more recent period, this has declined to only 3% and a Sharpe ratio of 0.5, which do not withstand transaction and funding costs." (e) L454-458: "we account for reversal or momentum effects by including the lagged return ... We find a reversal effect within the natural gas markets" (daily lag, Online Appendix Table A.8, not seen) | Day-level calendar premium on each report day: NG first nearby -0.37% against -0.09% per day, t -2.19, 2003-2018, absent in 2014-2018. No post-event horizon is studied. The lagged-return result is a one-day reversal in NG daily returns in general, not a post-event finding [size unverified: appendix not retrieved] |
| EDER19 | Ederington, L., Lin, F., Linn, S., Yang, L. (Z.), "EIA Storage Announcements, Analyst Storage Forecasts, and Energy Prices", Energy Journal 40(5), 121-142, 2019 | https://www.montana.edu/regecon/publications/energyinformationannouncement/index.html (E.20 fetch) | reports/stage_e20_briefs/pages/NG/montana_ederington2019.html | 423297319ac6f53c2349e3a4adb5149bdd5b101860f9be38e08ded52e70775e5 | RESEARCH BRIEF ONLY (not full text): "announced storage figures greater or less than analysts expected tend to partially reverse the following week." | The storage figure surprise (a fundamental, not a price) partly reverses the following week. Whether prices reverse with it is not stated in what was read [price implication unverified]. NG storage |
| CP20 | Caporale, G. M., Plastun, A., "Gold and Oil Prices: Abnormal Returns, Momentum and Contrarian Effects", Brunel University Economics and Finance Working Paper 2015, July 2020 | https://www.brunel.ac.uk/economics-finance-and-accounting/research/pdf/2015-Jul-GMC-Commodities.pdf | mech_pages/M9_ENERGY_REPORTS/brunel_2015jul_gmc_commodities.pdf | 7b97d441c087b159f4373769fcc568f4c4c393bb9cf5827f1c9ab9941b2c60f1 | (a) L58-60: "On the following day two different price patterns are detected: a momentum effect for Oil prices and a contrarian effect for Gold prices respectively." (b) L342-344: "The CAR analysis shows that the momentum effect is temporary (Figures D.1 and D.2): usually it lasts for a few hours". (c) L195-196: "Daily and hourly data for Gold and Oil over the period 01.01.2009-31.03.2020 (GMT +3 time zone) are used. The data source is MetaQuotes Software Corp." | Analog, not the event: after any day with an abnormal oil return, a continuation that lasts a few hours into the next day. Next day only. Oil prices from a retail CFD feed, not exchange futures, 2009-2020 |
| KKY20 | Kwon, K. Y., Kang, J., Yun, J., "Weekly Momentum in the Commodity Futures Market", Finance Research Letters (accepted version, Strathprints 70084) | https://strathprints.strath.ac.uk/70084/1/Kwon_etal_FRL_2019_Weekly_momentum_in_the_commodity_futures_market.pdf | mech_pages/M9_ENERGY_REPORTS/kwon_kang_yun_2020_frl_weekly_momentum.pdf | d768279a0b0f601216fffa5c48a534939822e7c29b039169adf0ca817b222f2c | (a) L4-5 (abstract): "Unlike in equity markets, strong short-term momentum, instead of short-term reversal, is observed in commodity futures markets." (b) L165-167: "weekly momentum generates a large average return, which is 0.20% (t = 4.49)". (c) L133: "Our sample spans the period from January 1979 to June 2015." | Analog: a cross-sectional long-short sort on the past week's return (not a single instrument, not an event) earns 0.20% per week (t 4.49) in the following week. Futures on 27 commodities (7 energy), 1979-2015. One-week horizon, in the continuation direction |
| WEN23 | Wen, Z., Indriawan, I., Lien, D., Xu, Y., Energy Journal 44(5), 2023 (accepted version) | E.20 fetch (Adelaide repository) | reports/stage_e20_briefs/pages/CL/wen_etal_2023_ej_adelaide.pdf; quotes in reports/stage_e20_briefs/shared/energy_class_notes.md row EN2 | 110ec616bcded7c190e7840235375552813e7b8ad8271e5703f5b1c1723e9a24 | (energy_class_notes.md, EN2) "This can be interpreted as a 1% increase in the third half-hour return leads to a 0.038% increase in returns by the end of the trading day." | Same-day only (the published rule behind K4-eiamom-01). No multi-day result. USO ETF, 2006-2019 |
| YANG17 | Yang, J. (with Miao, Ramchander, Wang), "The Impact of Crude Oil Inventory Announcements on Prices: Evidence from Derivatives Markets", EIA 2017 workshop slides | https://www.eia.gov/finance/markets/reports_presentations/2017/yang.pdf | mech_pages/M9_ENERGY_REPORTS/yang_2017_eia.pdf | 3e17b8bbed54ed6b243ec1a601d44d69f15f5eec1dc9280415fda7b6ba1968ac | slide 2: "the effect is more persistent than its effect on futures"; "Oil futures and options prices respond in a manner that seem to “correctly” anticipate changes in oil inventory levels! (anticipatory trading apparently prevails)" | Persistence appears in options, not futures. Anticipation is a pre-release effect. Companion to MIAO18 |

## (2) Per member

### K4-eiafade-01 (MCL): fade the first 15 minutes after the WPSR release

- Strength: none: intraday-only.
- Direction: "reversal" (the member's side) has no multi-day support. The literature on the same event finds
  neither reversal nor continuation after the release day: the surprise's effect on days +1 and +2 is nil
  (MIAO18, LINN17; CHEB19 abstract). The reaction is described as immediate, not reverting and permanent
  (HKK14, LINN17 slide 5, ANAT18). Analogs not tied to the event lean the other way, towards continuation
  for one day or one week (CP20 next-day oil momentum lasting "a few hours"; KKY20 weekly cross-sectional momentum).
- Horizon: the published post-event evidence covers days +1 and +2 only. Nothing at 5 or 20 trading days.
- Magnitude: post-event surprise coefficients are insignificant at days +1 and +2 (MIAO18, CL1-CL6,
  2003-2011, 446 releases; LINN17, 2003-2017). No published per-event return in the reversal direction beyond
  the release day. Against the MCL D8 round trip (4.346 ticks = 6.45 bp at $67.35, energy_class_notes.md), the
  published expected gross is zero.
- Reason: The fade rests on overreaction in the minutes after the release. The only records of a reversal
  (Rousse and Sevi 2019; Geman and Li 2018; Borgards et al.) are within hours and secondary only (E.20 rows
  EN5, EN7, EN8). By the release day's settlement, which is the E.23 entry, the papers that track later days
  find the surprise fully impounded: "we do not find any persistence of the impact of inventory news
  announcements on the returns of futures" (MIAO18 L933-935), and "No relation between surprises and prices
  changes on the two days following the release" (LINN17). Storage theory backs permanence: inventory
  arbitrage turns shocks into "small but permanent ones" (ANAT18 L177-178), and price moves are "permanent
  and unpredictable" (ANAT18 L1511-1512). Caveat: these papers condition on the surprise, while the member
  conditions on the 15-minute price move. A move larger than the surprise justifies (noise, liquidity) is
  not studied beyond hours in anything retrieved.

### K4-eiamom-01 (MCL): WPSR-day release half-hour, continued into the last half-hour

- Strength: weak.
- Direction: the evidence disagrees, and neither side is on this event. For "continuation": analogs only
  (KKY20: past-week returns predict next-week returns, cross-sectionally, 1979-2015; CP20: oil continuation
  into the next day after abnormal-return days, a few hours, CFD data). For "neither": the event studies
  find no post-release-day effect of the surprise (MIAO18, LINN17, CHEB19 abstract). No source supports
  multi-day reversal.
- Horizon: days +1 and +2 (event studies, a null) and one week (KKY20 analog). Nothing on this event at 5
  or 20 days.
- Magnitude: KKY20 reports 0.20% per week (t 4.49) for an equal-weight long-short portfolio of commodity
  futures. That is not a per-event number for MCL, and it is not transferable without a test. The event
  studies give zero at days +1 and +2. WEN23 (the source rule) is same-day only, with a "declining trend"
  and no effect in 2014-2016 (energy_class_notes.md, EN2).
- Reason: WEN23's mechanism for this rule is same-day intraday momentum: late-day traders act on the
  release-window information. The multi-day form would need underreaction to the WPSR information carrying
  past the settlement. The papers that test this find none for the surprise component (MIAO18 L929-935;
  LINN17 slide 11). The only continuation evidence is generic short-horizon commodity momentum, which KKY20
  ties to speculative positioning, not to inventory news (abstract, L15: "the weekly momentum is closely
  related to the speculative activity").

### K4-apipre-01 (MCL): post-API move (Tuesday) traded before the EIA release (Wednesday)

- Strength: none: intraday-only.
- Direction: no multi-day source. The mechanism is the overnight bridge from the API bulletin to the EIA
  release. It ends at the 09:30 CT EIA release, before the E.23 entry at Wednesday's settlement. No paper
  retrieved studies returns after Wednesday conditional on the API move, in either direction.
- Horizon: neither 5 nor 20 days.
- Magnitude: none published. Ye and Karali (2016) is the API-specific source and was not reached (AgEcon and
  UGA bot checks, as in E.20). Per E.20's search summary, the EIA effect is "larger and longer" than the API
  effect [secondary only].
- Reason: Pre-release information flow is documented: the inventory shock "predicts intraday and over-night
  returns before the announcement" (LUO14 L895-897), and prices "seem to “correctly” anticipate changes in
  oil inventory levels" (YANG17 slide 2). All of it resolves by the EIA release, and after the release the
  same papers find no persistence (MIAO18, LINN17). Nothing carries the API move into the 5 to 20 days
  after Wednesday's settlement.

### K4-ngpre-01 (NG): fixed SELL on every EIA storage-report day

- Strength: moderate (as a calendar premium on the report days that a multi-day hold contains). As
  post-event drift from the trigger day: none.
- Direction: "same side as the member" (SELL), on PWW21's announcement-day premium. No post-event drift
  source exists either way. Against it: CHEB19 (abstract) and LINN17 find nothing after the report day, and
  EDER19 (brief only) says storage surprises partly reverse the following week. That is a statement about
  the storage figure; the price effect is [unverified] and in any case conditions on the surprise sign,
  which a fixed-SELL member does not use.
- Horizon: both, mechanically. A 5-trading-day hold from a report-day settlement normally contains the next
  report day. A 20-day hold contains about 4. The source measures day-level returns, not holds.
- Magnitude: NG first nearby, March 2003 to December 2018: -0.37% mean on report days against -0.09% on
  other days, a difference with t -2.19 (p 0.029), from 3,982 daily returns (PWW21 Table 3). Decay: "the
  effect is not present in the most recent period (2014–2018)" (PWW21 fn 7), and the intraday strategy
  fell to "only 3%" per year, which does "not withstand transaction and funding costs" (PWW21 L723-725).
  Worker arithmetic, not a published number: a 5-day hold at the full-sample means is about -0.37 +
  4 x (-0.09) = -0.73% (about 22 NG ticks at $3.00, 1 tick = 3.33 bp, against the D8 wall of 2.408 ticks;
  product_NG.md). Most of the non-report-day part is NG's general negative futures return over 2003-2018,
  not this trigger. The figure assumes the full-sample means, and PWW21's own subsample result says they
  do not hold after 2013.
- Reason: PWW21 find the report-day return "cannot be explained by the announcement surprise or other
  control variables". Half of it falls before the release, and only on above-expectation days (PWW21
  abstract, L46-51). That makes it a recurring calendar premium, not information that drifts on after the
  event. In a multi-day hold, the member's side earns it again on each later report day in the window, and
  also earns or loses NG's unconditional drift on the other days. HKK14 confirms the report-window sign for
  2003-2012: a -0.26% mean in the 15-minute window against -0.03% on control days. PWW21 also report a
  daily-lag "reversal effect within the natural gas markets" (L458). Applied to the trigger day's own move,
  that would mean a partial one-day rebound after a down report day, against a SELL entered at that day's
  settlement. Its size is in Online Appendix Table A.8, which was not retrieved [unverified].

## (3) Query log

Times are PDT, 2026-10-17. Each search's time is bracketed by the logged fetch times around it (fetch_log.md);
exact search times were not stamped. Tool: WebSearch (standard) unless noted. 17 WebSearch calls in total,
under the cap of 60.

| # | Query | Time (bracket) | Results kept |
|---|---|---|---|
| 1 | crude oil futures inventory announcement surprise post-announcement drift subsequent days underreaction | 02:17:53-02:18:20 | CHEB19 (RePEc), LUO14, ANAT18, MIAO18 (metatoc), Rousse-Sevi (FEEM/HAL) |
| 2 | EIA weekly petroleum status report surprise crude oil returns following week predictability | same | none (news pages) |
| 3 | natural gas storage report surprise futures price response days after announcement reversal continuation | same | Chiou-Wei, Linn and Zhu (IMF 2012 seminar PDF; fetch failed) |
| 4 | "inventory" announcement crude oil futures cumulative abnormal returns event window days [+1,+5] OR "five days" EIA | 02:18:35-02:19:15 | YANG17 (eia.gov), HKK14 (Skidmore), Ye 2016 PhD (UGA) |
| 5 | Halova Kurov Kucher "Noisy inventory announcements and energy prices" Journal of Futures Markets pdf | same | HKK14 RePEc record |
| 6 | Chebbi "inventory change surprise" energy price behaviour post-announcement days insignificant | same | CHEB19 abstract; MIAO18 repository bitstream |
| 7 | crude oil futures overreaction after large daily price changes subsequent days abnormal returns Caporale Plastun | 02:20:06-02:21:21 | CP20 (Brunel), Mazouz-Wang (Hull, 403) |
| 8 | Gay Simkins Turac analyst forecasts price discovery natural gas storage futures pdf | same | EDER19 (Montana brief, already on disk from E.20) |
| 9 | natural gas futures storage announcement news momentum weekly returns predictability "storage surprise" lagged | same | PWW21 (already on disk), Mu (IAEE; not fetched) |
| 10 | crude oil futures underreaction to news sentiment predicts returns over following week Borovkova OR Smales | 02:21:26-02:22:27 | none relevant (LLM-sentiment forecasting) |
| 11 | API weekly statistical bulletin crude oil price reaction overnight next day EIA Ye Karali API surprise duration | same | none (news pages) |
| 12 | Ederington Lin Linn Yang "EIA Storage Announcements, Analyst Storage Forecasts, and Energy Prices" pdf working paper | same | IAEE executive summary (404) |
| 13 | natural gas futures day-of-the-week effect Thursday storage report negative return weekly seasonality | same | none (market commentary) |
| 14 | persistence of oil price response to weekly inventory announcements multi-day horizon Bjursell Gentle Wang OR Kilian | 02:22:27-02:23:00 | LINN17 (eia.gov slides), Hmedat IJFE (paywalled) |
| 15 | short-term return autocorrelation crude oil futures weekly reversal momentum 1-week 1-month horizon commodity futures evidence | same | KKY20 (Strathprints) |
| 16 | "Noisy inventory announcements and energy prices" Halova Kurov Kucher full text wvu OR skidmore OR researchgate | 02:23:23-02:23:49 | none new (led to the Wayback copy of HKK14) |
| 17 | oil inventory surprise next-week futures return regression "weekly" crude "inventory surprise" predict returns subsequent week drift energy journal | 02:25:11-02:26 | none new (AAEA Ye-Karali 2015 on AgEcon, a known bot-check site) |
| 18 | natural gas futures returns after EIA storage announcement multi-day event study cumulative return days +1 to +10 | same | none new (PWW21 copies) |

Stopping rule: the last two queries (17, 18) added no new relevant source. Key papers read in full text:
MIAO18, HKK14, PWW21, ANAT18 and LUO14 (by grep of saved full text), plus the LINN17 slides.

## (4) Not verified or not reached

- Chiou-Wei, Linn and Zhu (IMF 2012 seminar paper on NG storage surprises, with possible post-day results):
  curl 403 twice. The scrapling copy is a mangled PDF that pdftotext cannot read
  (`chiouwei_linn_zhu_imf2012_scrapling_corrupt.bin`). Firecrawl was not tried. Gap.
- Rousse and Sevi (Energy Journal 2019): the HAL copy is behind an Anubis bot check, not circumvented
  (`rousse_sevi_hal02024317_anubis_block.html`). Its "partly compensated in the hours following" claim is
  from search results only [secondary].
- Ye and Karali (2016, and the 2016 UGA PhD): UGA returned an empty 202 (bot check); AgEcon was not tried
  (known bot checks). The API-specific evidence is therefore secondary only.
- Chebbi (2019): abstract only. The number of post-announcement days tested is not stated.
- Ederington, Lin, Linn, Yang (2019): research brief only. The IAEE executive summary returned 404, and
  SSRN is not fetched (403). Whether prices reverse with the storage figure is [unverified].
- PWW21 Online Appendix (Tables A.3 subsamples, A.8 lagged-return reversal): not retrieved. Sizes
  [unverified].
- HKK14 Figure 2 (CARs): its time axis was not in the extracted text, so "permanent" is not tied to a
  stated horizon.
- Mazouz and Wang (commodity futures after large one-day shocks; Hull repository): 403. Hmedat (IJFE,
  2012-2018 weekly surprises): paywalled. Bjursell, Gentle and Wang (2015): citation only.
- No source anywhere measures 5- or 20-trading-day returns after a WPSR, API or NGS release. That absence
  is a gap in what was found, not a tested null.
