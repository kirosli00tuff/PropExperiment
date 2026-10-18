# R5 News and headline-driven intraday futures moves (SourceReader-News-OpusHigh, rerun)

Stage E.25, reader R5. First run started 2026-10-18 01:38 PDT and was cut by a usage limit about 01:58 PDT.
Rerun 06:13-06:36 PDT (hard deadline), built on the first run's saved pages; no new web searches were made in the rerun.
Status: COMPLETE within the deadline, with the gaps listed in section 10.

## 1. Answer

The literature says that headline news reaches liquid index futures, Treasuries and crude in seconds. A retail trader who acts seconds to minutes after the headline captures nothing that clears cost. Scheduled macro surprises are absorbed "within a tenth of a second" and "fully within five seconds" (E1). Even the fastest E-mini traders earned about 2 bp of the notional they traded, and those profits fell from $165,000 to $9,000 per event between 2011 and 2014. Presidential posts about the Fed moved SPY by 0.28 bp (t = 1.40) in a 5-minute window (E2), about 0.7 MES ticks at ES 6,600, which is below the roughly 3-tick hurdle. Geopolitical news enters oil prices "at once without follow-on momentum" (E7). For single stocks, the move associated with news concentrates before and at publication (E10). LLM-scored headlines earned 34 bp a day on single stocks, but their Sharpe ratio fell from 6.54 to 1.22 by 2024, and the authors say only low-cost market makers could use the signal (E6). Backtests of LLM scoring inside the model's training window are biased by look-ahead and memorization (E11, E12). Fed Chair speeches move ES as much as FOMC statements but have a mean near zero (E5): their direction cannot be read without the content. The one sized intraday news effect that leaves minutes to act is scheduled: the FOMC press conference continues the statement move (E3). R6 owns that candidate. R5 lists it once as R5-C1, a cross-reference with the size conversion, the Tier 1 window and contrary evidence. I propose no unscheduled-headline candidate. Evidence on V39: it SUPPORTS the closure of commodity event drift (E7, E10).

## 2. Candidate hypotheses

| id | hypothesis | instruments | entry (CT) | hold | trades/yr | published effect | price used | gross pts | gross micro ticks | grade | owned | testable in research window | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R5-C1 (cross-reference to R6, not a new trial) | FOMC press-conference continuation: trade in the sign of the statement-window move, from the start of the press conference to its end | MES (also MNQ, ZN per R6) | 13:30 published; 13:35 under the Topstep Tier 1 window (13:25-13:35 CT); micros capped and minis blocked inside it | about 55 min (mean 54 min 47 s), exit by about 14:25-14:30 CT | about 8 | alpha 12.66 bp per press conference, t = 2.30, n = 41 (Apr 2011 - Jan 2020), stock portfolio | ES 6,600 | 12.66 x 6,600 / 10,000 = 8.36 ES pts | 8.36 / 0.25 = 33.4 MES ticks (gross, at the published 13:30 entry) | peer-reviewed (JFE 2022, read as WP) | partial: GLBX bars owned; FOMC dates owned (release table C5) | yes (2011-2020 overlaps the research window; the lead checks it against holdout dates) | Same mechanism as R6's lines 38-59. R6 cites a post-COVID reversal under Powell (Narain and Sangani, slope -0.694, N 73). The 5-minute shift forced by Tier 1 and the post-2020 sign reversal both lower the effect. Low power at n of about 8 a year. |

No unscheduled-headline candidate survives. Reasons, row by row:
- Presidential posts (Fed criticism): +0.28 bp immediate (t 1.40) = 0.18 ES pts = 0.74 MES ticks. Below the hurdle, and not significant.
- Unscheduled macro and geopolitical headlines on CL: the move comes "at once without follow-on momentum" (daily data). There is nothing left for a trader who arrives late.
- LLM-scored headlines: the published effects are for single stocks over a day. I found no published futures intraday per-trade size. Any backtest before an LLM's cutoff is biased (E11, E12), so the research window cannot test the idea cleanly. Only a forward test after the cutoff could.
- Fed Chair speeches: SD 60 log-bp, but the mean is +5.0 log-bp over the 90-minute window. The mean is not a directional rule, and reading the sign needs real-time text scoring, which no published futures result supports.
- Tariff headlines (April 2025): only daily Treasury and convenience-yield effects (E13); no intraday published size.

## 3. Evidence table

| # | claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|---|
| E1 | Index futures and SPY absorb scheduled macro surprises within seconds; fast-trader profits small and falling | reaction within 0.1 s, full within 5 s; E-mini profits about $50,000 per event = about 2 bp of the notional traded; E-mini per-event profits $165,000 (2011), $62,000, $21,000, $9,000 (2014) | "Prices react to announcement surprises within a tenth of a second and respond fully within five seconds." / "Profits are larger for index futures, roughly $50,000 per event, yet this dollar amount translates to just two basis points of return relative to the $80 million of notional value traded in the direction of the surprise, and our measured profits do not account for commissions" / "The corresponding profits in the E-mini futures are $165,000, $62,000, $21,000 and $9,000, respectively." | WP Jan 2016, Introduction pp. 2-4 (txt lines 159-176, 243-247) | Chordia, Green, Kottimukkalur (2018), RFS 31(12) 4650-4687; WP "Low Latency Trading on Macroeconomic Announcements" (Jan 2016), https://www.unsw.edu.au/content/dam/pdfs/business/banking-finance/events/news-events/2021-10-busines-banking-finance-news-events-Low-Latency-Trading-on-Macroeconomic-Announcements.pdf | peer-reviewed (read as working-paper version) | pages/R5/chordia_green_kott_2016.pdf |
| E2 | Trump tweets criticising the Fed moved SPY by a fraction of a basis point in the narrow window | +0.28 bp immediate (t = 1.40); +1.71 bp daily (t = 1.92); FFR expectations -0.26 bp per tweet | "We find that the average immediate impact on the level of the stock market index is 0.28 bps (t-statistic = 1.40). The second column shows the average effect at the daily frequency. ... the estimated effect of 1.71 bps is larger in magnitude with increased statistical significance (t-statistic = 1.92)" | NBER w26308 rev. Sept 2022, Sec. on Table 4 Panel C (txt lines 1020-1027); window "0.1 minutes before the tweet and five minutes after" (Table 1 note, line 620) | Bianchi, Kind, Kung (2019, rev. 2022), NBER WP 26308; published as Bianchi, Gómez Cram, Kind, Kung (2023), J. Monetary Economics; https://www.nber.org/system/files/working_papers/w26308/w26308.pdf | working-paper (published version peer-reviewed, not read) | pages/R5/nber_w26308.pdf |
| E3 | FOMC statement-window move predicts same-sign move during the Chair's press conference (information rigidity) | correlation 44% for SPY, 33% average across stock portfolios; sign-following strategy alpha 12.66 bp per press conference for the stock bucket (t = 2.30); 41 press conferences Apr 2011 - Jan 2020; mean press-conference length 54 min 47 s | "The correlation between the two price changes is large and positive, e.g. 58% for 60-month Eurodollar futures, and 44% for the S&P 500 index." / "we take a long position at the beginning of the press conference if its price went up when the statement was released and a short position otherwise. We close the position at the end of the press conference." / Table 4: "Stocks ... α ... 12.66 [2.30]" / "we considered all 41 press conferences, covering a sample period from April 2011 to January 2020" | WP Nov 2020: Introduction (lines 155-163), Sec. 3.4 and Table 4 (lines 727-792), data section | Gómez Cram, Grotteria (2022), "Real-time price discovery via verbal communication: Method and application to Fedspeak", JFE 143(3) 993-1025; WP https://www.hec.edu/sites/default/files/2020-12/Fedspeak_gg.pdf | peer-reviewed (read as working-paper version) | pages/R5/gomezcram_grotteria_fedspeak_2020.pdf |
| E4 | Placebo: no autocorrelation on FOMC days without a press conference | null | "We don't find any evidence of a positive autocorrelation of price changes in days without a press conference." | WP Nov 2020, Sec. 3.3 (line 722) | same as E3 | peer-reviewed (WP version) | same |
| E5 | Fed Chair speeches move ES as much as FOMC statements, but the mean is near zero (no direction without reading content) | 411 Chair speeches 1988-2023; ES 90-min-window SD 60.0 log-bp, mean +5.0; FOMC SD 65.9; press conferences SD 78.2 (n 73) | "We find that speeches and press conferences by the Fed Chair are more important than FOMC announcements for stock prices, Treasury yields, and all but the shortest-maturity interest rate futures." Table 1: "Number 360 411 73 216 123 ... S&P 500 65.9 60.0 78.2 37.3 33.8" ; "For these speeches, we use a 90-minute window from 15 minutes before the" | 2025 version, Abstract; Table 1 (lines 674-704); Sec. 3 window (line 585) | Swanson, Jayawickrema (2025 draft), "Speeches by the Fed Chair Are More Important Than FOMC Announcements"; https://www.tse-fr.eu/sites/default/files/TSE/documents/sem2025/bdf/2025-11-18_swanson.pdf | working-paper | pages/R5/swanson_jayawickrema_2025.pdf |
| E6 | LLM-scored firm headlines predict next-day single-stock drift, decaying fast as LLM adoption rose | 34 bp/day long-short before costs; Sharpe 6.54 (2021Q4) -> 3.68 (2022) -> 2.33 (2023) -> 1.22 (Jan-May 2024); "only feasible for ... market makers" | "A long-short daily-rebalanced strategy based on GPT-4's assessments of overnight news generates average returns of 34 basis points (bps) per day before transaction costs." / "exploiting these patterns in practice is only feasible for market participants whose transaction costs are sufficiently low, such as market makers." / "its annualized Sharpe ratio drops from 6.54 in 2021Q4 to 3.68 in 2022, 2.33 in 2023, and to 1.22 over January-May 2024." | arXiv v6 (28 Oct 2025), Introduction pp. 2-5 (lines 84-90, 185-188) | Lopez-Lira, Tang (2023/2026), "Can ChatGPT forecast stock price movements?", JFE (2026); arXiv 2304.07619 | peer-reviewed (read as arXiv v6) | pages/R5/lopezlira_tang_2304.07619.pdf |
| E7 | Geopolitical news hits crude at once with no follow-on drift; macro news drifts (daily, RavenPack, 2000-2013) | 1 SD drop in war-and-conflict score -> +14.41 bp daily oil return | "The response of oil prices to geopolitical events is even stronger and immediate. News is incorporated into the oil price at once without follow-on momentum, consistent with informational efficiency." / "Geopolitical news have a much stronger immediate impact but exhibit not predictability." | NBER conf. draft Aug 2016, Abstract; Introduction p. 1 (lines 64-66); Sec. 4 (lines 307-311); sample "January 1, 2000 through March 31, 2013" (line 157) | Brandt, Gao (2019), J. Empirical Finance 51, 64-94; draft https://conference.nber.org/conf_papers/f89483/f89483.pdf | peer-reviewed (read as 2016 draft) | pages/R5/brandt_gao_2016_nberconf.pdf |
| E8 | Most news leads quickly to price jumps; most jumps have no identifiable news (DJIA stocks, TRNA) | qualitative | "We find that most relevant news, both idiosyncratic and systematic, lead quickly to price jumps, as market efficiency suggests they should. However, in the reverse direction, the vast majority of price jumps do not have identifiable public news that can explain them" | NBER w32746, Abstract | Aït-Sahalia, Li, Li (2024), "So Many Jumps, So Few News", NBER WP 32746 | working-paper | pages/R5/nber_w32746.pdf |
| E9 | Oil-market sentiment from LLMs helps only at the weekly horizon (classification, no per-trade size) | weekly WTI, 2020-2025 news | "This paper examines whether multi-dimensional sentiment signals extracted by large language models improve the prediction of weekly wti crude oil futures returns." | arXiv v2 16 Mar 2026, Abstract (txt lines 23-41) | Dai, Ma, Liu, Geng, Wang (2026), arXiv 2603.11408 | preprint | pages/R5/arxiv_2603.11408_wti_llm.pdf |
| E10 | News moves are priced before and at publication; stories overreact, numbers underreact (single stocks, daily) | close-of-day move 2.8x its value 20 days later; 4.57 M articles, 1.68 M stock-day events, 2023-2026 | "the price move associated with news concentrates before and at publication: pooled across all signed events, the cumulative move in the news direction by the close of publication day is 2.8 times its value twenty days later, and for rumor-flagged events the rumor day captures the entire move while the subsequent confirmation contributes nothing" | Abstract (txt lines 12-40) | Kargarzadeh, Khaledian, Parvini, Ghatak, Khaledian (2026), "Buy the Rumor, Sell the News: When Is News Priced In?", arXiv 2608.14014 | preprint | pages/R5/arxiv_2608.14014.pdf |
| E11 | LLM headline backtests inside the model's training window are biased | qualitative | "backtesting produces biased results ... This bias can take two forms: a look-ahead" [bias and] "a distraction effect" (abstract, line-wrapped in the extracted text) | Abstract (txt lines 14-30) | Glasserman, Lin (2023), arXiv 2309.17322 | preprint | pages/R5/arxiv_2309.17322_glasserman_lin.pdf |
| E12 | LLMs memorize economic and financial data before their cutoff; masking fails | qualitative | "Large language models (LLMs) cannot be trusted for economic forecasts during periods covered by their training data." / "masking fails as LLMs reconstruct entities and dates from minimal context" | Abstract (txt lines 13-21) | arXiv 2504.14765 (authors not re-read in this rerun) | preprint | pages/R5/arxiv_2504.14765_memorization.pdf |
| E13 | The April 2025 tariff shock moved Treasury convenience yields (daily data, not intraday) | about 12 bp drop in convenience yield | "bond can account for an approximately 12 bps drop in convenience yields in April 2025" | txt line 127 | Acharya, Laarits (2026), "Tariff War Shock and the Convenience Yield of US Treasuries", NBER WP 34640 | working-paper | pages/R5/nber_w34640.pdf |
| E14 | GDELT updates every 15 minutes and is free | 15-min cadence; free | "100% free and open and you can download the raw datafiles" / "every 15 minutes" | gdelt_data.html (grep) | GDELT Project, https://www.gdeltproject.org/data.html | vendor/project page | pages/R5/gdelt_data.html |


## 4. Negative evidence

- Speed: "Prices react to announcement surprises within a tenth of a second and respond fully within five seconds." Fast-trader E-mini profits fell from $165,000 (2011) to $9,000 (2014) per event and "do not account for commissions" (E1, Chordia, Green, Kottimukkalur 2018).
- Presidential posts: the immediate impact was 0.28 bp, t = 1.40 (E2, Bianchi, Kind, Kung). It is not significant and is far below cost.
- Oil geopolitics: "News is incorporated into the oil price at once without follow-on momentum, consistent with informational efficiency." / "Geopolitical news have a much stronger immediate impact but exhibit not predictability." (E7, Brandt and Gao)
- Decay of LLM signals: "its annualized Sharpe ratio drops from 6.54 in 2021Q4 to 3.68 in 2022, 2.33 in 2023, and to 1.22 over January-May 2024." and "only feasible for market participants whose transaction costs are sufficiently low, such as market makers." (E6, Lopez-Lira and Tang)
- Bias in LLM backtests: the look-ahead and distraction effects (E11), and "Large language models (LLMs) cannot be trusted for economic forecasts during periods covered by their training data." (E12)
- Priced before publication: "the cumulative move in the news direction by the close of publication day is 2.8 times its value twenty days later, and for rumor-flagged events the rumor day captures the entire move while the subsequent confirmation contributes nothing" (E10, single stocks).
- Jumps without news: "the vast majority of price jumps do not have identifiable public news that can explain them" (E8). A headline filter would miss most large moves.
- Press-conference placebo: "We don't find any evidence of a positive autocorrelation of price changes in days without a press conference." (E4) This supports C1's mechanism, but it also bounds it to about 8 events a year.
- Contrary evidence on C1 itself (from R6, not re-read by R5): post-COVID Powell press conferences reverse the statement move (slope -0.694, N 73, Narain and Sangani). See R6_sched_events.md lines 38-59 and 222.

## 5. Data and cost

The program owns GLBX.MDP3 bars and the release table (C5). It owns no timestamped news archive. Published prices are from pages saved 2026-10-18 by the first R5 run, read in this rerun:
- GDELT: free. Quote: "100% free and open and you can download the raw datafiles"; updates "every 15 minutes" (https://www.gdeltproject.org/data.html, pages/R5/gdelt_data.html). The 15-minute cadence is too coarse for headline timing within seconds or minutes.
- Tiingo: "It is simply $30/month (or $300/year) for individuals and $50/month (or $499/year) for internal commercial use." Free tier "$0/month" (pages/R5/tiingo_pricing_rendered.md). Not checked in the rerun: news-API depth, the historical archive and timestamp resolution.
- Benzinga Pro: Basic "$37 /monthly", Streamlined "$147 /monthly", Essential "$197 /monthly", Squawk "($99/mo Add-On)" (pages/R5/benzinga_pro_pricing.html). These prices are for the retail terminal. API pricing on benzinga_apis.html was not extracted in the rerun.
- Newsquawk: Basic (one squawk channel) "$199 ... /month", Pro "$399 ... /month", "Go live — 7 days for $29.99" (pages/R5/newsquawk_pricing.html). This is a live audio and text squawk with no historical archive, so it supports forward use only.
- RavenPack (the source behind E7): home page saved, no published price found (pages/R5/ravenpack_home.html).
- Fed feeds and the disclaimer, EIA copyright, OPEC press room, BLS link policy: saved (pages/R5/fed_*.htm*, eia_copyright.html, opec_press_room.html, bls_linksite.htm). These are free official sources. Their terms were not re-read in the rerun.
- R5-C1 needs no news data: it uses FOMC dates, owned bars and the press-conference start and end times (Fed calendar; start 13:30 CT).

## 6. Prop compatibility

- Topstep Tier 1 window (R9 E01, E02): windows are 7:25-7:35 CT (CPI, NFP), 12:55-13:05 CT (FOMC decision) and 13:25-13:35 CT (FOMC press conference). New mini positions are blocked, index and metals micros are capped (50K: 3 micros) and pending orders do not fill. Effect on C1: the published 13:30 entry falls inside the window, so the earliest full-size entry is 13:35 CT, and any resting entry or stop order placed for 13:30 would not fill. The exit at about 14:25 CT is outside every window and before the 15:10 CT flatten.
- P06 (R9 E07): no full maximum position size into a scheduled major event. C1 entered at 13:35, after the window, is arguably not "into" the event, but the press conference is still running. Size it below the maximum.
- Unscheduled headlines fall outside the Tier 1 list, so Topstep allows them. MFFU bans "strategies that exploit immediate news bursts, such as straddles or strangles" (R9 E32) and blocks T1 news trading on sim-funded accounts (E31). Alpha has no restrictions (E28). The5ers and DayTraders allow news trading (E19, E24).
- HFT ban: the only profitable headline window is under 5 seconds (E1), which needs HFT. That is excluded on every firm.
- Automation: C1 is a 1-minute decision with one order and is feasible manually (V39).

## 7. Overlap with tested mechanisms

- R5-C1 overlaps K2-fomcpost-01 (BUY 13:29 on FOMC dates, exit 15:04, unconditional long, Tier B). C1 is sign-conditional on the statement move. It also overlaps E-H2 (post-release momentum at 10 minutes, conditional on the range) and K5-fomc-01 (MGC momentum 13:04 to 13:15, NULL). C1 differs in its window (the press conference) and its conditioning (statement sign). It duplicates R6's candidate (R6_sched_events.md lines 38-59 and 69-89); the lead dedupes.
- E.12 and E.20 ML (FAIL) used no text features, so an LLM-news feature would be new. It is untestable in the research window because of look-ahead and memorization (E11, E12).
- Closed by V39-V41: commodity event drift as a standalone stage (see section 8).

## 8. Verdict check (R5 is not a re-dig reader; V39 only, as the spawn message asked)

- V39 closure of commodity event drift as a standalone stage: SUPPORTS. Brandt and Gao find geopolitical news enters oil "at once without follow-on momentum, consistent with informational efficiency" (E7). Daily macro-news drift in oil exists in their data, but it is daily, ran from 2000 to 2013, and needs RavenPack. The weekly LLM WTI paper gives classification accuracy only, with no tradable size (E9). The single-stock news-timing result places the move before and at publication (E10).

## 9. Fetch log

All pages were fetched by the first R5 run between 08:40 and 08:57 UTC (01:40-01:57 PDT) on 2026-10-18; the times are file mtimes. The tool was not recorded per file (WebFetch, curl or arXiv/NBER direct). The sha256 values below are 16-hex prefixes; the full hashes are in R5_news.json. The rerun made no new fetches. Status is ok unless marked.

| file | UTC | sha256 (prefix) | status |
|---|---|---|---|
| arxiv_2012.06573_curti_kazinnik.pdf | 2026-10-18T08:57Z | 6e131f75932e80f7 | ok |
| arxiv_2012.06573_curti_kazinnik.txt | 2026-10-18T08:57Z | 2c301f502b40d29b | ok (local text extraction) |
| arxiv_2304.07619_abs.html | 2026-10-18T08:40Z | a8030068d866ee10 | ok |
| arxiv_2309.17322_glasserman_lin.pdf | 2026-10-18T08:55Z | dfc8bb5981886467 | ok |
| arxiv_2309.17322_glasserman_lin.txt | 2026-10-18T08:55Z | f858e3ba40219a6f | ok (local text extraction) |
| arxiv_2504.14765_memorization.pdf | 2026-10-18T08:47Z | ce31fa9f08999452 | ok |
| arxiv_2504.14765_memorization.txt | 2026-10-18T08:47Z | 7ca5ca526986600c | ok (local text extraction) |
| arxiv_2603.11408_wti_llm.pdf | 2026-10-18T08:56Z | 286a516f79f547d9 | ok |
| arxiv_2603.11408_wti_llm.txt | 2026-10-18T08:56Z | a4ca72ef5d58e2e2 | ok (local text extraction) |
| arxiv_2608.14014.pdf | 2026-10-18T08:47Z | 9a8836fb060d77d7 | ok |
| arxiv_2608.14014.txt | 2026-10-18T08:47Z | 9f197d60919a0a04 | ok (local text extraction) |
| arxiv_api_tou.html | 2026-10-18T08:40Z | badbec1e87aa3170 | ok |
| benzinga_apis.html | 2026-10-18T08:49Z | b72b322d9fd0fdb7 | ok |
| benzinga_pro_pricing.html | 2026-10-18T08:51Z | 23ead178626f2a15 | ok |
| bls_linksite.htm | 2026-10-18T08:49Z | 406ca8dddcbef006 | ok |
| brandt_gao_2016_nberconf.pdf | 2026-10-18T08:47Z | 721e92109bde23b4 | ok |
| brandt_gao_2016_nberconf.txt | 2026-10-18T08:47Z | 8900461c1d80b48f | ok (local text extraction) |
| chordia_green_kott_2016.pdf | 2026-10-18T08:44Z | ecd0e1c1e7c6eae0 | ok |
| chordia_green_kott_2016.txt | 2026-10-18T08:44Z | 6ff44220035ee0c6 | ok (local text extraction) |
| eia_copyright.html | 2026-10-18T08:49Z | 821ec2732035327f | ok |
| fed_disclaimer.htm | 2026-10-18T08:48Z | c9d47356c9df1c86 | ok |
| fed_feeds.html | 2026-10-18T08:48Z | 07cf981d70bb2635 | ok |
| gdelt_about.html | 2026-10-18T08:48Z | 384754b514042255 | ok |
| gdelt_data.html | 2026-10-18T08:48Z | dc2e607696f7cc09 | ok |
| gomezcram_grotteria_fedspeak_2020.pdf | 2026-10-18T08:44Z | 66455c1fe2418e24 | ok |
| gomezcram_grotteria_fedspeak_2020.txt | 2026-10-18T08:44Z | 8b108f801fbbe326 | ok (local text extraction) |
| lopezlira_tang_2304.07619.pdf | 2026-10-18T08:41Z | a410e809cfffc39b | ok |
| lopezlira_tang_2304.07619.txt | 2026-10-18T08:41Z | dedd0c6c0ba0f13e | ok (local text extraction) |
| massive_pricing.html | 2026-10-18T08:49Z | 4f325847c51c01a9 | ok |
| nber_w26308.pdf | 2026-10-18T08:43Z | b2705f0a4367ec70 | ok |
| nber_w26308.txt | 2026-10-18T08:43Z | 283a24c2054ae34a | ok (local text extraction) |
| nber_w32746.pdf | 2026-10-18T08:43Z | 9bc4386391f52a87 | ok |
| nber_w32746.txt | 2026-10-18T08:43Z | 6e79c16529817010 | ok (local text extraction) |
| nber_w34640.pdf | 2026-10-18T08:43Z | ca8348ba57ce39df | ok |
| nber_w34640.txt | 2026-10-18T08:43Z | c1c24ec021960708 | ok (local text extraction) |
| newsquawk_pricing.html | 2026-10-18T08:51Z | e4c0a3dbb640d68f | ok |
| opec_press_room.html | 2026-10-18T08:49Z | 64ebcd8b8f5ba7c1 | ok |
| ravenpack_home.html | 2026-10-18T08:49Z | 12625c05d326a7d6 | ok |
| repec_burggraf_2020.html | 2026-10-18T08:54Z | 7f15cb934e7c8ed2 | ok |
| repec_busse_green_2002.html | 2026-10-18T08:54Z | 6893db556f27e9b9 | ok |
| repec_machus_mestel_theissen_2022.html | 2026-10-18T08:54Z | 580dfa3dab6cd5b4 | ok |
| scharnowski_2026_jfr_ANUBIS_BLOCK.html | 2026-10-18T08:46Z | 609a04a7a0f2de64 | blocked |
| smales_gold_asym_vol.pdf | 2026-10-18T08:55Z | e3b0c44298fc1c14 | failed (0 bytes) |
| swanson_jayawickrema_2025.pdf | 2026-10-18T08:44Z | 8cdea6ff67a591aa | ok |
| swanson_jayawickrema_2025.txt | 2026-10-18T08:44Z | db2e61c530cd5aa0 | ok (local text extraction) |
| swanson_jayawickrema_nber_f189220.pdf | 2026-10-18T08:44Z | 5320cb1e424a57d5 | ok |
| swanson_jayawickrema_nber_f189220.txt | 2026-10-18T08:44Z | 5fcf1712947615c1 | ok (local text extraction) |
| tiingo_pricing.html | 2026-10-18T08:49Z | 9f184aa5fd7be38c | ok |
| tiingo_pricing_rendered.md | 2026-10-18T08:50Z | 430595ec45a3d53c | ok (local text extraction) |

Budget notices: none were seen in the rerun. The first run's notices, if it had any, were not recorded in its partial file. Blocked: scharnowski_2026_jfr_ANUBIS_BLOCK.html (an anti-bot page; the paper was not read). Empty: smales_gold_asym_vol.pdf (0 bytes, failed fetch; not used). Terms: arXiv API terms of use saved (arxiv_api_tou.html) but not re-read.

## 10. Unfinished and unverified

- The rerun made no WebSearch calls: there was too little time before the 06:36 deadline. The intraday sizes of oil-headline moves (CL in minutes after OPEC or geopolitical headlines), GC headline moves and ZN reactions to Fed speakers were not searched beyond the saved papers.
- Saved but not read: Marchal (2021), FOMC press conferences through computer vision (arxiv_2012.06573); RePEc pages for Burggraf (2020), Busse and Green (2002), and Machus, Mestel and Theissen (2022). The last two are likely sizes for CNBC or TV news on single stocks; not used.
- Swanson and Jayawickrema NBER version (f189220) saved; only the 2025 TSE version was quoted.
- The authors of arXiv 2504.14765 were not re-read. E11's quote is line-wrapped in the PDF text extraction, and the bracketed word is mine.
- The C1 conversion uses the stock-portfolio alpha (12.66 bp), not an ES-specific number. The SPY correlation is 44%. The effect at a 13:35 entry is unknown.
- Tiingo news-API depth and the Benzinga API price were not extracted. URLs for most saved pages were not recorded by the first run; the JSON gives the URLs I know.
- Overlap ids were checked against r0_mechanism_index.md by grep only.
