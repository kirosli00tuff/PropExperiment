# F2 grains: family reader facts (Stage E.32b, step F2)

Worker GrainsReader-OpusHigh; started 2026-10-28T22:48:36-07:00, finished 2026-10-28T23:08:48-0700. WebSearch calls 29 of 80; T6 full-text reads 2 of 12. Items 52 in F2_grains.json (ids GRAINS-n). Facts only, no scores. Pages and log: pages/GRAINS/ (log.tsv). Reused E.28 facts cite reports/stage_e28_briefs/A1_grains.json by index and field.

Shared sources not read here: CFTC automated-trading reports (F2_shared_cftc_automation.json, RatesReader) and Baltussen et al. 2021 (F2_shared_baltussen.json, EquityReader). E.28's CFTC figures for ZC/ZS/ZW remain in A1_grains.json hft_automated_share.

## Per code

| Code | Leader | Spread (ticks; item) | Touch (item) | Settlement (item) |
|---|---|---|---|---|
| ZC | ZC | 1.1 (mean; GRAINS-2) | GRAINS-5 | physical delivery (GRAINS-10) |
| XC | ZC | not found | not found | physical delivery; daily and final settlement derived directly from ZC settlement (GRAINS-27) |
| MZC | ZC | not found | not found | financial, settled daily and finally to the ZC settlement (GRAINS-8) |
| ZS | ZS | 1.04 (mean; GRAINS-33) | GRAINS-34; GRAINS-7 | physical delivery (GRAINS-10) |
| XK | ZS | not found | not found | physical delivery; daily and final settlement derived directly from ZS settlement (GRAINS-27) |
| MZS | ZS | not found | not found | financial, settled daily and finally to the ZS settlement (GRAINS-8) |
| ZW | ZW | 1.1 (mean; GRAINS-2) | GRAINS-6 | physical delivery (GRAINS-10) |
| XW | ZW | not found | not found | physical delivery; daily and final settlement derived directly from ZW settlement (GRAINS-27) |
| MZW | ZW | not found | not found | financial, settled daily and finally to the ZW settlement (GRAINS-8) |
| ZL | ZL | not found | not found | physical delivery (GRAINS-10) |
| MZL | ZL | not found | not found | financial, settled daily and finally to the ZL settlement (GRAINS-8) |
| ZM | ZM | not found | not found | physical delivery (GRAINS-10) |
| MZM | ZM | not found | not found | financial, settled daily and finally to the ZM settlement (GRAINS-8) |

No MEDIAN spread or touch size was found for any code; every figure is a mean. Notes per code:

- ZC: Spread figures are MEANS, not medians: 1.1 ticks pooled grains 2015-16 (GRAINS-2), 1.26 ticks 2008-10 (GRAINS-1), about 1 tick 2008-11 (GRAINS-4); 1.12 ticks 2022 snippet only (GRAINS-51). Settlement period 13:14-13:15 CT (GRAINS-28). MM programs 2021-2024: ETH MM program and deferred-month MM program (GRAINS-30, -32). Best directional evidence: Anderson et al. 2024 WP (WASDE, corn mostly absorbed by 30 min, GRAINS-18); null/negative: Lehecka 2014 (abstract), Couleau jumps.
- ZS: Spread MEANS: 1.04 ticks all hours about 2020 (CME article, GRAINS-33); 1.118 ticks day session H1 2019, night 1.22 (GRAINS-3); 1.1 pooled 2015-16 (GRAINS-2). Touch figures are means with differing side conventions. Crush intraday cointegration (GRAINS-15/16). WASDE soybean reaction keeps growing 30 min to close (GRAINS-18, WP full text, in sample). Other-venue DCE soybean intraday momentum (GRAINS-25, full text, in sample, gross). Null: Joseph-Garcia (GRAINS-21).
- ZW: Spread is a pooled grains MEAN 2015-16. No wheat-specific directional study found; only generic USDA absorption (Adjemian-Irwin, abstract) and weekly corn-soy-wheat cointegration (GRAINS-47).
- ZL: No full-text spread: snippet only, 2.06 ticks US hours / 3.07 Asia hours 2022 (GRAINS-35, -51, unverified). No touch size found. Crush member (GRAINS-15). Biofuel policy news pointer (GRAINS-48). In the ETH and deferred MM programs.
- ZM: No spread or touch size published; E.31 RETURN has passive markouts, not a spread (GRAINS-50). Crush member; leadership varies with volume (GRAINS-38). Program's own directional search negative (GRAINS-49). DCE soybean meal intraday momentum, other venue (GRAINS-25). ZM directional route closed (E.33c).
- XC: No spread or touch found for minis. Satellite facts from ZC.
- XK: No spread or touch found. Satellite facts from ZS.
- XW: No spread or touch found. Satellite facts from ZW.
- MZC: Launched 2025-02-24. No spread/touch found.
- MZS: No spread/touch found.
- MZW: No spread/touch found.
- MZL: No spread/touch found.
- MZM: No spread/touch found.

## Facts by topic (one line each; detail, quote and source in the JSON)

### T1 Spread and touch

- GRAINS-1 [T1, reused; codes ZC]: 1.26. Window: 2008-01-14..2010-01-29, last 40 trading days before the expiration month, day session (BBO).
- GRAINS-2 [T1, reused; codes ZC,ZW,ZS]: 1.1. Window: nearby contracts, 2015-11-23..2016-03-31 (Arzandeh and Frank 2017/2019 AJAE).
- GRAINS-3 [T1, reused; codes ZS]: 1.118. Window: H1 2019, day session 08:30-13:20 CT, top-5 contracts volume-weighted (Peng 2022 dissertation); H1 2020 day 0.2775 c/bu = 1.11 ticks.
- GRAINS-4 [T1, reused; codes ZC]: about 1. Window: 2008-01-14..2011-10-31, Globex, incl. USDA and index-roll days (Shang, Mallory, Garcia 2016).
- GRAINS-5 [T1, reused; codes ZC]: {"bid_mean": 377.69, "ask_mean": 375.27}. Window: nearby, 2015-11-23..2016-03-31.
- GRAINS-6 [T1, reused; codes ZW]: {"bid_mean": 45.26, "ask_mean": 43.92}. Window: nearby, 2015-11-23..2016-03-31.
- GRAINS-7 [T1, reused; codes ZS]: {"bid_mean": 62.45, "ask_mean": 64.0, "top_depth_bid_plus_ask_day_2019": 103, "top_depth_bid_plus_ask_night_2019": 43}. Window: 2015-11-23..2016-03-31 (per side); H1 2019 and H1 2020 (both sides summed; 2020 day 109, night 48).
- GRAINS-33 [T1, full_text; codes ZS]: 1.04. Window: CME Group data, period not stated (article written with Jan-Nov 2020 data; published about Dec 2020/early 2021); all hours average; Asian hours (08:00-20:00 Singapore) 1.06.
- GRAINS-34 [T1, full_text; codes ZS]: {"all_hours_avg_level1_lots": 26.32, "asian_hours_avg_level1_lots": 19.81}. Window: as GRAINS-33 (about 2020).
- GRAINS-35 [T1, snippet; codes ZL,MZL]: US hours 2.06 ticks; Asia hours 3.07 ticks (top of book, hourly, first three quarters of 2022). Window: Q1-Q3 2022 (per search snippet).
- GRAINS-50 [T1, full_text; codes ZM,MZM]: null. Window: E.31 pilot, ZM front month DAY session, 2020-12..2024-02.
- GRAINS-51 [T1, snippet; codes ZC,ZS,ZW,ZL,ZM]: ZC about 1.12 ticks whole-day average (2022); ZL widest of the CBOT ag contracts measured (US hours 2.06, Asia hours 3.07 ticks); ZM between ZS and ZL. Window: first three quarters of 2022 (per snippet).

### T2a Automated share

- None recorded from new sources (see searched-not-found).
- E.28 reuse (not re-fetched; CFTC source owned by RatesReader): A1_grains.json [0..4].hft_automated_share; Grain and Oilseed group ATS share 39.0% (2012-14) and 49.0% (2014-16).

### T2b Market-maker and incentive programs

- GRAINS-11 [T2b, reused; codes ZC,ZS,ZW,XC,XK,XW,MZC,MZS,MZW]: none in force 2021-2026 found; historical: CBOT overnight Corn/Wheat/Soybean futures MM program 2009-11-01..2010-12-31; ETH fee incentive 2011-10-17..2011-12-31. Window: checked 2026-10-21 (E.28); 2026-10-01 fee schedule.
- GRAINS-12 [T2b, reused; codes ZL,ZM,MZL,MZM]: none in force 2021-2026 found; historical ETH fee incentive 2011 covered ZL and ZM. Window: checked 2026-10-21 (E.28).
- GRAINS-13 [T2b, reused; codes XC,XK,XW]: mini-sized grains MM program 2007-11-01..2009-12-31 (expired); none 2021-2026 found. Window: 2007-11-01..2009-12-31.
- GRAINS-30 [T2b, full_text; codes ZC,ZS,ZW,ZL,ZM,XC,XK,XW,MZC,MZS,MZW,MZL,MZM]: CBOT Grain & Oilseed Futures ETH Market Maker Program (overnight session 19:00-08:30 CT; outright futures ZC, ZS, ZM, ZL, ZW, KE): in force 2017-01-01 onward, term extended to at least 2024-07-31. Window: start 2017-01-01; modifications effective 2017-11-01, 2021-02-01 (end date moved from 2021-01-31 to 2022-01-31), 2023-08-01 (end date moved from 2023-07-31 to 2024-07-31); in force at least 2021-02..2024-07.
- GRAINS-32 [T2b, full_text; codes ZC,ZS,ZW,ZL,ZM,XC,XK,XW,MZC,MZS,MZW,MZL,MZM]: CBOT Grain & Oilseed Deferred Futures Contract Market Maker Program (Volume Incentive Program): deferred (non-lead) futures months of ZC, ZS, ZM, ZL, ZW, KE; start 2017-01-10, term extended to 2025-07-31. Window: 2017-01-10 .. at least 2025-07-31 (modification effective 2024-08-01).

### T2c Retail share

- None recorded from new sources (see searched-not-found).
- No retail share found. E.28: Haynes-Roberts 'small traders' share is not a retail share (A1_grains.json retail_share).

### T3 Structural relationships

- GRAINS-15 [T3, full_text; codes ZS,ZM,ZL,XK,MZS,MZM,MZL]: soybean crush (ZS vs ZM and ZL): intraday cointegration at 1-minute sampling in the day session. Window: calendar 2015, 243 trading days, CME LOB data.
- GRAINS-16 [T3, full_text; codes ZS,ZM,ZL,XK,MZS,MZM,MZL]: soybean crush: overnight session cointegration on 52 days vs 180 in the day session (1-minute, 2015). Window: 2015.
- GRAINS-24 [T3, abstract; codes ZS,ZM,ZL,XK,MZS,MZM,MZL]: soybean complex liquidity: persistence and positive cross-market spillovers mainly within 30 s; negative at longer horizons. Window: CME soybean complex LOB (2015 per planner pointer, unverified).
- GRAINS-44 [T3, full_text; codes ZC,ZS,ZW,ZL,ZM,XC,XK,XW,MZC,MZS,MZW,MZL,MZM]: calendar spreads with implied-in/implied-out orders linking the spread book and the outright book (CBOT grains). Window: CME Globex, described for 2018-2020 samples (Peng 2022).
- GRAINS-45 [T3, full_text; codes MZC,ZC,MZS,ZS,MZW,ZW,MZL,ZL,MZM,ZM,XC,XK,XW]: micro/full and mini/full pairs: micros cash-settled to the full-size settlement (1/10 size); minis' daily and final settlement equal to the full-size settlement (1/5 size). Window: micros since 2025-02-24; minis per 2024 settlement pages.
- GRAINS-46 [T3, full_text; codes ZC,XC,MZC]: corn nearby vs deferred futures (calendar): intraday cointegration on about 70% of days; nearby price-discovery share 52% vs first deferred, 78% vs fourth deferred. Window: 2008-2015, CME Top-of-Book transactions time-stamped to the second, daily estimation.
- GRAINS-47 [T3, full_text; codes ZC,ZS,ZW,XC,XK,XW,MZC,MZS,MZW]: corn, soybean and wheat futures cointegrated at weekly frequency (two cointegrating vectors); trading rules with significant risk-adjusted returns. Window: weekly prices (period in paper, not extracted); working paper 2012.

### T4 Scheduled events and absorption

- GRAINS-18 [T4, full_text; codes ZS,XK,MZS,ZC,XC,MZC]: WASDE (monthly, 12:00 ET since 2013): price effect not significant at 10 min, significant at 30 min; soybean reaction keeps growing from 30 min to the day close. Window: 2010-2021, 122 WASDE reports, CME nearby corn and soybean futures.
- GRAINS-19 [T4, abstract, negative; codes ZC,XC,MZC]: major USDA reports: reactions persist about ten minutes; no systematic under- or overreaction. Window: July 2009 - May 2012, CBOT corn electronic (Globex).
- GRAINS-20 [T4, abstract; codes ZC,ZS,ZW,XC,XK,XW,MZC,MZS,MZW]: USDA crop reports in real-time trading (since 2012): volatility spike dissipates within a few trading minutes. Window: 2009-2014 intraday grain futures.
- GRAINS-21 [T4, full_text, negative; codes ZS,XK,MZS]: USDA reports during trading hours: volatility spike lasts five to six minutes; return correlations show no systematic under- or overreaction. Window: June 2010 - May 2014 (two periods: pre- and post-2012 trading-hours release), CBOT soybean futures intraday.
- GRAINS-22 [T4, reused; codes MZC,MZS,MZW,MZL,MZM,XC,XK,XW,ZC,ZS,ZW,ZL,ZM]: USDA schedule: WASDE and Crop Production 12:00 ET (11:00 CT, in the day session); Grain Stocks, Prospective Plantings, Acreage at 12:00 ET; Crop Progress Mondays 16:00 ET (after the 13:20 CT close, before the 19:00 CT reopen); Export Sales Thursdays 08:30 ET (07:30 CT, overnight session, 15 min before the pause). Window: 2026 calendars; noon release since January 2013.
- GRAINS-23 [T4, reused; codes ZC,XC,MZC]: USDA report days: jumps cluster within 2 minutes after release (2.30 jumps per announcement day since 2013 vs 0.26 otherwise). Window: 2008-2015 nearby corn transactions.
- GRAINS-40 [T4, abstract; codes ZC,ZS,XC,XK,MZC,MZS]: USDA Crop Progress and Condition (Mondays 16:00 ET, after the close): moves the next session's opening (close-to-open) return variability; reactions rapid and rational; strongest July-August. Window: 1986-2012, daily close-to-open returns.
- GRAINS-48 [T4, snippet, pointer; codes ZL,MZL,ZM,MZM,ZS]: pointer: EPA Renewable Fuel Standard / RVO announcements move ZL sharply (limit moves reported; 2022-12-01 spot ZL -9% on the day and further declines in later sessions); NOPA monthly crush report moves ZM/ZL modestly. Window: news reports 2014-2025.
- GRAINS-52 [T4, full_text, pointer; codes ZC,ZS,XC,XK,MZC,MZS]: pointer (single episode): 2025-09-12 WASDE: bearish report, negative immediate reaction, then corn and soybean new-crop futures closed higher on the day (intraday reversal). Window: one report day, 2025-09-12.

### T5 Settlement and price discovery

- GRAINS-8 [T5, reused; codes MZC,MZS,MZW,MZL,MZM]: financial, daily and final settlement to the standard-size contract's settlement price. Window: since launch 2025-02-24 (SER 9512).
- GRAINS-9 [T5, reused; codes XC,XK,XW]: physical delivery (mini-sized certificates). Window: CBOT rulebook chapters 10B, 11B, 14B.
- GRAINS-10 [T5, reused; codes ZC,ZS,ZW,ZL,ZM]: physical delivery. Window: CBOT rulebook chapters 10-14.
- GRAINS-27 [T5, full_text; codes XC,XK,XW]: daily and final settlement derived directly from the full-size contract's settlement (XC from ZC, XK from ZS, XW from ZW); physically delivered at expiry. Window: CME Globex settlement pages, Wayback captures 2024-04/05.
- GRAINS-38 [T5, full_text; codes ZS,ZM,ZL,XK,MZS,MZM,MZL]: within the crush (ZS, ZM, ZL): relative information shares vary day to day with relative traded volumes; no fixed leader reported. Window: 2015, day session 1-minute data.
- GRAINS-39 [T5, abstract; codes ZS,XK,MZS]: DCE and CBOT soybean futures: information transfer in both directions at similar magnitude (CBOT not dominant). Window: not stated in abstract (daily trading/non-trading-hour returns).

### T6 Intraday directional evidence

- GRAINS-25 [T6, full_text; codes ZS,XK,MZS,ZM,MZM]: first half-hour return positively predicts last half-hour return: DCE soybean slope 0.073 (R2 1.80%), soybean meal slope 0.052 (R2 0.90%), significant at 5%. Window: DCE soybean 2002-07-01..2013-06-27 (2,245 days); soybean meal 2008-06-02..2013-06-28 (1,093 days).
- GRAINS-26 [T6, full_text; codes ZC,ZS,ZM,XC,XK,MZC,MZS,MZM]: excluded: daily-horizon time-series momentum/reversal (intraday semivariance used to predict daily returns), Chinese venue. Window: DCE corn, soybean No.1, soybean meal from Jan 2007 (Table 1).
- GRAINS-41 [T6, abstract; codes ZC,ZS,ZW,XC,XK,XW,MZC,MZS,MZW]: lagged order imbalance predicts returns for some contracts (corn, wheat, soybeans, cattle, hogs). Window: March 2008 and March 2016, CME BBO.
- GRAINS-42 [T6, abstract, negative; codes ZS,ZC,XK,XC,MZS,MZC]: NEGATIVE after night trading: Chinese soybean and corn futures overreacted to US overnight returns (reversal strategy profitable), but the strategy stopped working after DCE introduced night trading. Window: not stated in abstract (DCE before and after night-trading introduction, about 2019).
- GRAINS-43 [T6, abstract, pointer; codes MZC,MZS,MZW,MZL,MZM,XC,XK,XW,ZC,ZS,ZW,ZL,ZM]: low intraday predictability in opening and closing hours for futures incl. commodities; 'some potential economic significance' out of sample. Window: not stated.
- GRAINS-49 [T6, full_text, negative; codes ZM,MZM]: program's own pre-registered ZM directional search (300 configurations, horizons 5-60 min and triple barrier 15/30): no configuration passes; G1-qualifying configurations lose more than 1.0 tick a trade after costs. Window: 796 out-of-fold ZM dates, 2020-12-30..2024-02-29 (owned ZM MBO, ZS/ZL MBP-1).

### T7 Session structure and handoffs

- GRAINS-14 [T7, reused; codes MZC,MZS,MZW,MZL,MZM,XC,XK,XW,ZC,ZS,ZW,ZL,ZM]: Globex Sun-Fri 19:00-07:45 CT and Mon-Fri 08:30-13:20 CT. Window: current (2025 SER; same for all grain classes).
- GRAINS-17 [T7, full_text; codes ZC,XC,MZC]: settlement-window reversals: pre-close to settlement price moves reversed at next open less often after the 2012 settlement-rule change. Window: CBOT corn, March-June 2012 (before/after 2012-06-25).
- GRAINS-28 [T7, full_text; codes ZC,ZS,ZW,XC,XK,XW,MZC,MZS,MZW]: daily settlement period 13:14:00-13:15:00 CT (lead-month VWAP of Globex outright trades; deferred months from calendar-spread VWAP); day session closes 13:20 CT. Window: CME settlement pages, Wayback 2024-04/05 (ZC, ZS, ZW); close 13:20 CT per 2025 SER (GRAINS-14).
- GRAINS-29 [T7, full_text; codes MZC,MZS,MZW,MZL,MZM,XC,XK,XW,ZC,ZS,ZW,ZL,ZM]: 2013 hours: overnight 19:00-07:45 CT, pause 07:45-08:30 CT, day 08:30-13:15 CT; settlement at or around 13:15 CT. Window: effective 2013-04-07 (SER 6617); later the day close moved to 13:20 CT (GRAINS-14).
- GRAINS-36 [T7, full_text; codes ZC,ZS,XC,XK,MZC,MZS]: volatility-only: U-shaped intraday volatility in the day session (open and close dummies), USDA reports raise high-low range. Window: 2015-12..2017-05, day session 08:30-13:20 CT (corn, soybeans, live cattle).
- GRAINS-37 [T7, abstract; codes ZC,XC,MZC]: strongest USDA price reactions immediately after the market opens (when reports came out before the open), lasting about ten minutes. Window: July 2009 - May 2012.

### F1 Changed E.28 facts

- GRAINS-31 [F1, full_text; codes ZC,ZS,ZW,ZL,ZM,XC,XK,XW,MZC,MZS,MZW,MZL,MZM]: market_maker_program: Grain & Oilseed Futures ETH Market Maker Program in force 2017-01..at least 2024-07 for ZC, ZS, ZW, ZL, ZM (see GRAINS-30). Window: 2021-2026 scope of D2 b.

## Key readings for the lead (facts, not ratings)

- D2 b: E.28 found no current program; CFTC filings show the CBOT Grain & Oilseed Futures ETH Market Maker Program (ZC, ZS, ZM, ZL, ZW outrights, overnight session) in force from 2017 through at least 2024-07-31, and a deferred-month market-maker program through at least 2025-07-31 (GRAINS-30, -32, F1 GRAINS-31). Minis and micros are not named.
- D3 s1: the soybean crush has peer-reviewed full-text evidence of intraday cointegration at 1-minute sampling in the day session (180 of 243 days, 2015), much weaker overnight (52 days) (GRAINS-15, -16). No half-life or trading test is reported. Corn nearby/deferred calendar intraday cointegration about 70% of days (GRAINS-46, working paper). Corn-soy-wheat only weekly (GRAINS-47).
- D3 s2: conflicting. Anderson, McKenzie, Noyes 2024 (NCCC-134 working paper, full text, 2010-2021) find the WASDE soybean reaction grows from 30 min to the close; corn mostly done by 30 min (GRAINS-18). Lehecka et al. 2014 (abstract) and Joseph-Garcia (full text) find about 10 min / 5-6 min and no under- or overreaction; Adjemian-Irwin 2018 (abstract) is volatility-only (GRAINS-19 to -21).
- D3 s3: settlement period 13:14-13:15 CT verified for ZC, ZS, ZW (GRAINS-28); daily pause 07:45-08:30 CT (GRAINS-14, -29); U-shaped day-session volatility (volatility-only, GRAINS-36); pre-2012 settlement-window reversals declined after the rule change (GRAINS-17).
- D4 Sat (ii): micros are financially settled to the full-size settlement (GRAINS-8). Minis are physically delivered, but their daily and final settlement price is derived directly from the full-size settlement (GRAINS-27); this changes E.28's plain 'physical delivery' reading.
- D6: no CBOT-grain product-level study of intraday directional predictability found. Other venue: DCE soybean and soybean meal first-half-hour momentum (full text, in sample, gross, 2002-2013 and 2008-2013; GRAINS-25); DCE overreaction to US overnight moves stopped working after night trading (abstract, negative; GRAINS-42). The program's own ZM search is negative net of costs but explicitly not a proof of absence (GRAINS-49).

## Searched, not found

- T1 (ZL,ZM,XC,XK,XW,MZC,MZS,MZW,MZL,MZM): No full-text spread or touch size for ZL, ZM, minis or micros. The 2022 CME article (ZL/ZC figures) has no Wayback capture; cmegroup.com not fetched by rule. de Boer et al. 2022 (ZS/ZL/ZM liquidity cost) full text not retrieved (Wiley paywall; AgEcon 2019 version behind a bot check). Queries: soybean oil futures bid-ask spread ticks CBOT soybean meal futures quoted spread liquidity study intraday; CME micro grain futures one year liquidity bid-ask spread top of book micro corn micro soybean 2025 2026; "Asia agricultural markets turn to regional liquidity" soybean oil 2.06 ticks.
- T2a (MZC,MZS,MZW,MZL,MZM,XC,XK,XW,ZC,ZS,ZW,ZL,ZM): Only CFTC OCE automated-trading figures found (owned by RatesReader: reports/stage_e32b_briefs/F2_shared_cftc_automation.json; E.28 reused values in A1_grains.json hft_automated_share). Non-CFTC: Manitoba thesis (umanitoba_algo_ag_thesis.html) studies AT effects 2015-16 without a share figure in its abstract; Irwin 2013 slides chart only electronic share. Queries: high-frequency trading share of volume agricultural futures corn soybeans percent algorithmic trading grain markets study; "agricultural" futures "algorithmic" OR "automated" share of volume percent CME grains 2019..2022.
- T2b (MZC,MZS,MZW,MZL,MZM,XC,XK,XW): No program naming micros or minis in 2021-2026 found. Leaders' programs: GRAINS-30, -32. Queries: cftc.gov CBOT micro agricultural futures incentive program 2025 market maker micro corn soybean wheat; "Micro" "Grain and Oilseed" futures "Market Maker Program" OR "Incentive Program" CBOT submission 2025.
- T2b (ZC,ZS,ZW,ZL,ZM): No ETH MM program filing after the 2023-08-01 modification found; status after 2024-07-31 unknown. Deferred-month program runs to at least 2025-07-31; later status unknown. Queries: cftc.gov/filings/orgrules CBOT "ETH Market Maker Program" grain oilseed 2024 OR 2025 modifications.
- T6 (ZC,ZS,ZW,XC,XK,XW,MZC,MZS,MZW): No product-level study of intraday directional predictability (5 min to session) on CBOT grain futures found; only other-venue (DCE) studies, multi-asset work (Baltussen, shared file) and announcement-absorption studies. Stopped after consecutive empty queries. Queries: intraday momentum agricultural commodity futures corn soybean wheat first half-hour return predicts last half-hour; intraday return predictability CBOT grain futures corn soybeans out-of-sample trading strategy minutes; "intraday momentum" OR "intraday time-series momentum" commodity futures United States corn soybeans wheat journal; overnight session return predicts day session return CBOT soybean corn futures; corn soybean futures night session versus day session returns pattern study; "intraday momentum" commodity futures international evidence CME agricultural ....
- T5 (MZC,MZS,MZW,MZL,MZM,XC,XK,XW): No information-share study for mini or micro grains. Queries: mini-sized corn soybean futures price discovery relative to full-size CBOT contracts study OR micro grain futures price discovery.
- T4 (ZC,ZS,ZW): No event study of the weekly Export Sales release found (news recaps only). Queries: "Export Sales" report USDA intraday price response corn soybean wheat futures Thursday 7:30 study announcement effect.
- T4 (ZL,ZM): No intraday event study for EPA RFS/RVO or NOPA crush releases; news pointers only (GRAINS-48). Queries: soybean oil futures price reaction EPA Renewable Fuel Standard announcement intraday OR NOPA crush report soybean meal futures announcement effect study.
- T3 (ZC,ZS,ZW): No minute-level cross-grain (corn-wheat, corn-soy) relationship study; only weekly cointegration (GRAINS-47) and corn calendar intraday cointegration (GRAINS-46). Queries: corn wheat futures spread cointegration intraday high-frequency lead-lag CBOT corn wheat soybeans minute data.

## Gaps

- Spreads: only MEANS found (no median) for ZC, ZS, ZW; nothing full-text for ZL, ZM, minis, micros.
- Touch sizes: means only, conventions differ (per side vs both sides); none for ZL, ZM, minis, micros.
- Lehecka-Wang-Garcia 2014 and Adjemian-Irwin 2018 full texts not retrieved (paywalled); abstract level only.
- Volkenand et al. 2018 (lagged order imbalance) horizon unknown: full text 403.
- Jin et al. JFM version not read (MPRA working-paper version read in full instead).
- de Boer et al. 2022 full text (ZL/ZM liquidity costs) not retrieved: Wiley paywall; the AgEcon 2019 record is a slide deck (read via Firecrawl after curl, Scrapling and WebFetch were blocked) with unlabelled chart values and no spread figure.
- ZL and ZM settlement-window pages not found in Wayback; 13:14-13:15 CT verified for ZC, ZS, ZW only.
- ETH MM program status after 2024-07-31 and deferred program after 2025-07-31 not established.
- 2022 CME regional-liquidity article (ZL spread above 2 ticks) only as snippets; no archive copy; cmegroup.com not fetched by rule.
- Kauffman (2013) KC Fed (post-report volatility up to about 60 min) not fetched: volatility-only and low priority.
- Leader column = the full-size sibling per the brief's pointer; not checked against USD-notional ADV here (the spec's c and Sat (i) use E.28 ADV via script).

## Notices

- No WebSearch budget notice was received.
