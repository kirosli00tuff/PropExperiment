# R7 Live audited track records (Stage E.25, reader R7, SourceReader-LiveRecords-OpusHigh)

Started 2026-10-18 01:38 PDT, finished about 02:10 PDT. Research only; no market data opened, nothing computed on data.
Tool notes: OpenAlex returned 429 "Insufficient budget ... resets at midnight UTC" at 08:45Z (the IP's free budget was used up; .env has no OpenAlex key, only OPENALEX_EMAIL). Semantic Scholar keyless returned 429 twice at 08:45Z (logged "throttled"). Firecrawl returned "Insufficient credits" at about 08:46Z. After that, all evidence came through WebSearch (20 calls), curl and scrapling.

## 1. Answer (at most 250 words)

No audited live record of an intraday futures system came up. Every record found falls into one of four groups:

- (a) hypothetical by the platform's own label (Collective2, Futures Truth, the Barclay index);
- (b) a one-year contest result where only the top 5 are published (World Cup Trading Championship, WCC);
- (c) a CTA program that is short-term but not intraday, with average holds of about 1 to 10 days and proprietary rules (Crabel, QIM, Paskewitz, the SG Short-Term Traders Index);
- (d) population data that is negative for retail day traders (Taiwan and Brazil futures).

The strongest single record is the Collective2 strategy "ares", read from its public page:
- MNQ only, long and short, "No overnight. Always with stop", risk 1% of equity per trade.
- Tagged "Trend-following Short Term". Average trade 2.3 hours.
- 767 trades from 2020-09-12 to 2026-10-16 (74 months).
- 35.6% winners, average win $906, average loss $339.
- 32.6% compounded annual return "includes fees/commissions". Max drawdown 14.1%. Sharpe 1.48.

Its winners minus losers come to $79,796, or $104 net per trade, but contracts per trade vary. The 30 trades visible on the page average 5.53 MNQ and together lost $8.23 per contract.

Collective2 labels the whole record hypothetical. The manager does not certify that he trades it himself ("TOS percent 0.0%"). The rules are not public: "For deeper information of the backtest results you can pm me." The style is the opening-range and intraday-momentum family the program already tested on MNQ (K1-cp2-01, K1-vwap-01, E20H6-T1), so it adds a live existence proof, not a new mechanism.

The strongest negative finding is from Bhardwaj, Gorton and Rouwenhorst (NBER w14424). Average CTA returns fall from 9.4% a year with backfill included to 4.9% "in real time". After bias correction, CTAs earned only 85 bp a year over T-bills, net of fees.

## 2. Candidate hypotheses

One candidate. Zero would also be defensible: its rules are unknown and it overlaps tested families. It is listed because it is the only multi-year intraday futures record found with per-trade statistics.

| id | hypothesis | mechanism | instruments | entry window CT | hold | trades/yr | best source | grade | published effect | gross per trade (micro ticks) | gross or net | rules known | owned | research window testable | overlap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R7-C1 | MNQ intraday short-term trend-following: stop on every trade, no overnight, low hit rate (about 35%), payoff about 2.7:1, about one trade every 2 trading days, size 1% equity risk | intraday momentum or breakout (as the manager labels it "Trend-following Short Term"); actual rules proprietary | MNQ | not published (Collective2 shows dates only, no times) | 2.3 h average | about 124 (767 trades / 74 months x 12) | Collective2 strategy page "ares" (id 131145247), manager ares_Systemtrading | live-record-unaudited (C2: "All performance results are hypothetical") | $104.04 net per trade (sum of winners $247,359 minus losers $167,563, over 767 trades), multi-contract; 32.6% compounded annual return, max drawdown 14.1%, Sharpe 1.48 | not computable from the page (contracts per trade over life not published). Inputs for the lead: the 30 visible recent trades average 5.53 MNQ per trade; at a constant 5.53 contracts, $104.04 / 5.53 = $18.81 per contract = 37.6 MNQ ticks net of C2's model commissions (a crude estimate; with 1% risk sizing on growing equity, earlier trades likely had fewer contracts); the 30 visible trades themselves sum to -$1,366 on 166 contracts = -$8.23 per contract (-16.5 ticks) | net of C2 model "fees/commissions" (slippage model not stated) | no | data yes (MNQ 1-min in the research window); rules no | partial: only a generic re-specification is testable, which falls inside tested families | K1-cp2-01, K1-vwap-01, E20H6-T1, B-H1/B-H3/B-H4, RT1-RT4, H1-H5 |

Supporting records of the same style (not separate candidates, both under 2.1 years):
- "ares P2", same manager: 216 trades since 2024-09-21, average 2.2 h, $106.84 net per trade, 16.6% compounded, max drawdown 13.0%.
- "DT LS Mix" (QuantifiedSolutions): "Day Trading with 6 subsystems - both long and short", MNQ, 738 trades since 2025-02-04, average 2.1 h, 30.9% winners, profit factor 1.10, $56.36 net per trade, max drawdown 26.4%, "Trades Own Strategy" with "TOS percent 35.0%".

Bias next to each figure:
- All Collective2 figures are self-selected survivors. "ares" is "Rank at C2 % Top 0.1%", read off a leaderboard sorted by performance.
- They are hypothetical model-account fills.
- The manager can launch many strategies and keep the winners (incubation; the same manager runs "ares P2").
- No backfill: C2 tracks results forward only (secondary quote in section 3, E9).
- Year-by-year YTD returns for "ares": 2021 17.8%, 2022 76.4%, 2023 17.8%, 2024 70.1%, 2025 5.0%, 2026 YTD 13.5%. The research-window year 2025 was its weakest.

## 3. Evidence table

| # | claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|---|
| E1 | "ares" style, instrument, overnight rule | MNQ, 1% risk, no overnight | "System ares trades MNQ Future long and short. Risk per trade is 1% of equity. No overnight. Always with stop. The system is backtested and is 100% automated. For deeper information of the backtest results you can pm me. TOS not possible because of the Tax Regulations for derivatives in Germany. Trend-following Short Term" | "About this strategy" section | Collective2, strategy "ares" by ares_Systemtrading, https://collective2.com/details/131145247, fetched 2026-10-18 | live-record-unaudited | pages/R7/c2_details_131145247_ares.html |
| E2 | "ares" statistics | 767 trades, 35.6% win, 2.3 h, max drawdown 14.1%, 32.6% annual, Sharpe 1.48 | "Strategy began 9/12/2020 Suggested Minimum Capital $90,000 Age 74 months ... # Trades 767 # Profitable 273 % Profitable 35.6% Avg trade duration 2.3 hours Max peak-to-valley drawdown 14.1% drawdown period Oct 05, 2021 - Nov 26, 2021 Annual Return (Compounded) 32.6% Avg win $906 Avg loss $339 ... Sharpe Ratio 1.48" | "Statistics / Overview" | same | live-record-unaudited | same |
| E3 | "ares" winners and losers in dollars | $247,359 / $167,563 | "Sum Trade PL (losers) $167,563 Sum Trade PL (winners) $247,359 Num Months Winners 49 # Losers 494 % Winners 35.6%" | "Win / Loss" | same | live-record-unaudited | same |
| E4 | "ares" costs included; manager does not trade it himself | 32.6% with costs vs 34.7% without fees; TOS 0% | "Ann Return (w trading costs) 32.6% Return Pcnt (Compound or Annual, age-based, NFA compliant) 0.3% Return Pcnt Since TOS Status 0.0% Ann Return (Compnd, No Fees) 34.7%" and "Trades Own System? 0 TOS percent 0.0%" | "Return Statistics", "Trades-Own-System Certification" | same | live-record-unaudited | same |
| E5 | "ares" monthly table is hypothetical and includes fees and commissions | 2025 = 5.0% | "Hypothetical Monthly Returns (includes fees/commissions) ... 2024 5.7 5.3 -0.7 16.1 2.0 2.6 4.5 1.1 1.7 3.1 1.3 12.8 70.1 2025 -2.8 -0.9 -3.3 -0.1 -0.3 -1.9 -1.4 7.5 0.1 0.3 4.1 4.1 5.0" | monthly table | same | live-record-unaudited | same |
| E6 | Collective2 disclaimer on these pages | all hypothetical | "These results are based on simulated or hypothetical performance results that have certain inherent limitations. Unlike the results shown in an actual performance record, these results do not represent actual trading." and on the leader board: "All performance results are hypothetical." | page footer; leader board header | Collective2 strategy page and https://collective2.com/leader-board | firm-page | pages/R7/c2_details_131145247_ares.html, pages/R7/c2_leader_board.html |
| E7 | "ares P2" statistics | 216 trades, 2.2 h, 16.6%, drawdown 13.0%, $106.84 per trade | "Strategy began 9/21/2024 ... # Trades 216 ... Avg trade duration 2.2 hours Max peak-to-valley drawdown 13.0% ... Annual Return (Compounded) 16.6% Avg win $1,082 Avg loss $433" ; "Sum Trade PL (losers) $60,207 Sum Trade PL (winners) $83,285" | Statistics | https://collective2.com/details/149476882 | live-record-unaudited | pages/R7/c2_details_149476882_aresP2.html |
| E8 | "DT LS Mix" statistics | 738 trades, 30.9% win, profit factor 1.10, 22.0%, drawdown 26.4%, $56.36 per trade | "Day Trading with 6 subsystems - both long and short" ; "Strategy began 2/4/2025 ... # Trades 738 # Profitable 228 % Profitable 30.9% Avg trade duration 2.1 hours Max peak-to-valley drawdown 26.4% ... Annual Return (Compounded) 22.0% Avg win $1,419 Avg loss $553" ; "Sum Trade PL (losers) $281,928 Sum Trade PL (winners) $323,524" ; "TOS percent 35.0%" | header, Statistics | https://collective2.com/details/150759166 | live-record-unaudited | pages/R7/c2_details_150759166_dtlsmix.html |
| E9 | C2 records are forward-only and cannot be deleted (search snippet, not read on C2) | n/a | "Performance results are designated as hypothetical by Collective2 (C2), which prohibits the retroactive deletion or modification of trading signals." | search-result snippet of a NinjaTrader Follow mirror page | follow.ninjatrader.com/details/... (via WebSearch) | firm-page [secondary-only] | none |
| E10 | dispersion example: a different C2 futures strategy | max drawdown 83.2%, 3.4-day trades | "TradePathStrategies ... Started Jul 2024 hypothetical · Annual Return (Compounded) 51.0% Max Drawdown 83.2% Trades 552 Win Trades 85.0% Profit Factor 1.30" | header | https://collective2.com/details/148563155 | live-record-unaudited | pages/R7/c2_details_148563155.html |
| E11 | WCC publishes only the top 5 and "net %"; audit at the end of the period | Q3 2026 Futures Day Trading winner 1350.8% in one quarter | "All Standings are subject to final audit at the conclusion of the championship period." ; "2026 3rd Quarter Futures Day Trading Championship RANK NAME NET % COUNTRY 1 David Trullas Vila 1350.8% 2 Gerard Garcia 684.4% 3 Carles Clotet 204.7% 4 Huthayfa Abbaas 151% 5 Zachary Boyajian 116.1% July 1, 2026 – September 30, 2026 – Final Pending Audit" | standings page | World Cup Trading Championships, https://www.worldcupchampionships.com/world-cup-trading-championship-standings | firm-page | pages/R7/wcc_standings.html (do not commit) |
| E12 | WCC annual winners 2025 | 324.7% | "2025 World Cup Championship of Futures Trading® RANK NAME NET % COUNTRY 1 Tirutrade AG 324.7% 2 Marci Silfrain 206.4% 3 Andrea Marenda 155.9% ... January 1, 2025 – December 31, 2025 – Final" | standings page | same | firm-page | same |
| E13 | WCC field size and the 2023 winner | about 5,000 entrants; 491.4% | "which of 5,000 traders can close the year with the largest percentage gain" / "returned 491.4% in 2023" | search-result summary of Bloomberg Línea (2024-01-17) | bloomberglinea.com | pointer [secondary-only] | none |
| E14 | Davey WCC record | 148% / 107% / 112% (2005-2007) | "He finished second in 2005 (+148% return), first in 2006 (+107% return), and second in 2007 (+112% return)" | search snippet | completetradersedge.com, author bios | pointer [secondary-only] | none |
| E15 | Unger style and rules | rules not public | "Request your free copy of the book 'The Unger Method'" ; a podcast summary says 30-40 futures markets, breakout among other types, 5-to-15-minute up to daily bars | search snippets | ungeracademy.com; metacast (Better System Trader ep. 16/45) | pointer [secondary-only] | none |
| E16 | Futures Truth tracks hypothetical results; last issue 2019 | 200+ systems | "This quarterly publication tracks hypothetical performance of 200+ publicly offered trading systems." ; "Futures Truth Magazine, Issue #4/2019 has just been published!" | homepage | https://futurestruth.com/ | vendor | scratch only (homepage text, not saved under pages) |
| E17 | CTA database bias: backfill and survivorship | real time 4.9% vs 9.4% with backfill; net 85 bp over T-bills | "CTA excess returns to investors (i.e., net of fees) averaged 85 basis points per annum over US T-bills, which is insignificantly different from zero. We estimate that CTAs on average earned gross excess returns (i.e., before fees) of 5.4%" ; "the average performance of funds when they report to the database in real time (4.9%) and the average performance of all funds including backfill (9.4%). The former return is lower because the average backfilled return of 11.3% considerably exceeds the 'live' average return of 4.9%." | abstract (pdf p.2); Section on backfill bias (pdf p.9) | Bhardwaj, Gorton, Rouwenhorst (2008) NBER WP 14424; published RFS 2014 (1994-2012 sample, not read) | working-paper | pages/R7/bgr_nber_w14424.pdf |
| E18 | short-term CTAs earned less than longer-horizon CTAs (older literature) | n/a | "Results also indicated that CTAs using long- or medium-run systems had higher returns than CTAs using short-term trading systems and that CTAs with higher historical returns tend to charge higher fees." | Chapter 1 overview, excerpt p.2 | Gregoriou, Karavas, Lhabitant, Rouah (eds., 2004), Commodity Trading Advisors: Risk, Performance Analysis and Selection, Wiley (excerpt PDF) | practitioner-book | pages/R7/gregoriou_2004_cta_excerpt.pdf |
| E19 | SG Short-Term Traders Index definition (holding period under 10 days) | 10 largest | "The SG Short-Term Traders Index is designed to track the daily performance of a group of the largest 10 short-term, diversified CTAs that have a holding period shorter than 10 days, are willing to provide daily returns and are open to new investment." ; "SG Short-Term Traders Index -1.18% 5.47%" (March 2016, YTD) | p.2 and table p.1 | Societe Generale Prime Services, Index Performance Announcement, 5 April 2016 | vendor | pages/R7/sg_cta_indices_2016_03.pdf |
| E20 | STTI 2022 result | +11.3%; best year +11.74% (2008) | "ended the year +11.3%, the second best performance since inception in 2008, beaten only by its first year which was +11.74%" | search snippet | thefullfx.com, "Year-End Drop Fails to Dampen Stellar 2022" | pointer [secondary-only] | none |
| E21 | Crabel Multi-Product (constituent of the SG STTI; Crabel Gemini added for 2026) is short-term and multi-strategy, not intraday | AUM $1.334bn; inception 03/1998 | "The program consists of a highly diversified portfolio of uncorrelated and predominantly short-term, systematic strategies traded across a large number of markets. The majority of the price-driven strategies in the portfolio can be classified as short-term momentum or mean-reversion trades." ; "Assets Under Management (USD) $1,334,000,000 Inception Date 03/01/1998" | Executive Summary | RCM Alternatives program page, https://www.rcmalternatives.com/?p=4510 | vendor | pages/R7/rcm_crabel_multiproduct_1x.html |
| E22 | Crabel performance (aggregator) | 7.59% annualized, Sharpe 0.62, about 10-day average hold | search snippets of AutumnGold reports: "annualized return of +7.59%" ; "Sharpe Ratio of 0.62" ; "approximate 10-day average hold" | search snippets | autumngold.com (profile not public: "This program is not available as a public CTA profile.") | vendor [secondary-only] | none |
| E23 | QIM Global Program (short-term futures, STTI member re-included 2019) | about 6% annualized, Sharpe about 0.55-0.58, drawdown -23.64% (07/2022-04/2025) | search snippets of AutumnGold program statistics | search snippets | autumngold.com | vendor [secondary-only] | none |
| E24 | Paskewitz contrarian S&P program (S&P futures only) | average hold 6 days; 27.4% annualized 12/2003-2008 (manager claim) | search snippets: "averages a holding period of 6 trading days" ; "annualized return of 27.4% since inception" | search snippets | opalesque.com (2009) | pointer [secondary-only] | none |
| E25 | Taiwan futures individual day traders lose after costs | 3,470 traders; NT$61,500 loss after costs vs NT$26,700 before | "the 3,470 individual day traders in the sample incur on average a significant loss of 61,500 (26,700) New Taiwan dollars after (before) transaction costs over October 2007-September 2008" | abstract (search snippet; HKU repository PDF blocked: 403) | Kuo, Lin (2013), Journal of Banking and Finance 37, 3548-3561 | peer-reviewed [secondary-only] | none |
| E26 | Brazil mini-index futures day traders | 19,646 individuals; 97% lost money | "97% of them lost money, only 0.4% earned more than a bank teller" (working paper) ; "only 1.1% earned more than the Brazilian minimum wage" (2020 SSRN version) | search snippets (FGV and USP PDFs not retrievable: HTML stub / connection failure) | Chague, De-Losso, Giovannetti (2019/2020), "Day Trading for a Living?" | working-paper [secondary-only] | none |
| E27 | Social-trading signal providers: chasing top performers loses, no alpha after costs | n/a | "simply investing in those traders with the highest accumulated returns leads to high losses ... no strategy reveals a positive abnormal return after transaction costs in the sense of a Carhart four-factor model" | abstract (RePEc page) | Dorfleitner et al. (2018), Quarterly Review of Economics and Finance 70, 160-171 | peer-reviewed [secondary-only] (abstract only) | pages/R7/repec_dorfleitner_2018_qref.html |
| E28 | Copy-trading popularity is poorly tied to performance | n/a | "people overwhelmingly choose whom to mirror based on social popularity, a signal poorly correlated with actual performance" | arXiv abstract | Joseph, Riedl, Pentland, Moro (2025), arXiv:2507.01817 | working-paper [secondary-only] (abstract only) | pages/R7/arxiv_2507.01817v2_abs.html |
| E29 | CME Trading Challenge (simulated): persistence, but negative excess returns before expenses for most teams | 2014-2018 | "After risk adjustment, most teams are experiencing negative excess returns prior to expenses" | abstract via search snippet | Review of Behavioral Finance (Emerald), doi 10.1108/RBF-09-2019-0122 | peer-reviewed [secondary-only] | none |
| E30 | Barclay CTA Index is hypothetical and requires 4 years of history | n/a | "The Barclay Index does not represent an actual portfolio, which could be invested in, and therefore the index performance results should be deemed to be hypothetical in nature" | search snippet | barclayhedge.com/barclay-cta-index | vendor [secondary-only] | none |
| E31 | S&P 500 Dynamic Intraday TCA Index: published-rule intraday trend index on E-mini, live only since 2023-08-14 | up to 13 rebalances a day (TWAP), 15% volatility target | "all data prior to such date is back-tested hypothetical data" (insurer flyer, launch 2023-08-14) | search snippets | S&P DJI methodology and brochure (spglobal.com; robots.txt returned 403, not fetched) | vendor [secondary-only] | none |

## 4. Negative evidence

- CTA databases overstate live performance (E17). Backfilled months average 11.3% against a 4.9% "live" average. Net of fees, CTAs earned 85 bp a year over T-bills (1994-2007). The RFS 2014 version (1994-2012, not read) says the net excess return is "insignificantly different from zero".
- Short-term CTAs earned less than longer-horizon CTAs in the older literature (E18). The short-term CTA programs with long live records (Crabel since 1998, QIM, Paskewitz) average holds of about 1 to 10 days, not intraday. Their reported long-run results are modest: Crabel about 7.6% a year with Sharpe 0.62, QIM about 6% a year with Sharpe about 0.55 and a 23.6% drawdown in 2022-2025 (E21-E23, secondary-only).
- Collective2 shows only hypothetical results (E6). The board is sorted by performance, so what is visible is the survivors. Records range from a 14% to an 83% maximum drawdown (E2, E10). The 30 recent visible trades of "ares" lost money per contract (-$8.23). Its 2025 return (+5.0%) was the lowest of its full years, and 2025 lies inside the program's research window.
- WCC (E11-E13) publishes the top 5 by net % out of about 5,000 entrants (secondary). Periods are 1 month to 1 year, with no drawdown, size or style published. A quarterly futures day-trading winner at +1350.8% implies leverage no prop account would allow. Winners' methods are sold, not published (Unger, E15).
- Futures Truth (E16) tracks "hypothetical performance" of vendor systems, and its last issue is #4/2019.
- Population studies of real retail futures day traders (E25, E26, exchange-wide, no selection) show losses after costs. Taiwan: average loss after costs, larger than before costs. Brazil: 97% lost money among those who persisted 300+ days.
- Social-trading platforms (E27, E28): following top past returns loses, there is no four-factor alpha after costs, and popularity is not performance.

## 5. Data and cost

- R7-C1 needs MNQ 1-minute OHLCV in the research window, which the program owns (section 4 of the brief). No side data is needed for a generic intraday momentum re-specification. The record's own trade list would need Collective2 per-trade data. robots.txt disallows /strategy/csv/*, the terms forbid scraping "paid strategy content", and only 30 trades are visible on the public page. A subscription is $100/month (quoted: "Subscribe $100/mo"). This reader made no sign-up and no purchase.
- CTA program monthly data (IASG, BarclayHedge, AutumnGold, RCM) sits behind registration, terms forbid harvesting (IASG), or the profiles are not public (AutumnGold).

## 6. Prop compatibility

R7-C1 as described:
- It fits the overnight rule: "No overnight".
- It uses one micro instrument (MNQ) and is "100% automated", which fits TopstepX API automation with no HFT (about 124 trades a year, average 2.3 h).
- Flat by 15:10 CT is unknown: C2 shows dates only, no times.
- News behaviour is unknown (P06).
- Sizing: "1% of equity" on a suggested $90,000 is about $900 of risk per trade. The 14.1% maximum drawdown is about $12.7k on $90k, which would breach a Topstep 50K $2,000 trailing limit unless risk is cut to roughly 1/6 or less. The lead computes the scaling.
- Consistency rule: the monthly table shows lumpy years (2022 +76.4%, 2024 +70.1%, 2025 +5.0%). Whether the best-day share stays under 55% is not knowable from the page.
- WCC winners and the short-term CTAs hold multi-day positions or use leverage outside prop limits.

## 7. Overlap with tested mechanisms

- R7-C1 against K1-cp2-01 (MNQ first close beyond the 08:30-08:45 opening range, momentum, Tier B fail) and B-H1/B-H3/B-H4, RT1-RT4, H1-H5 (MES opening-range breakouts on 1-minute and 5-minute bars, OR30 patterns). Same family, intraday breakout or momentum. The live record adds proprietary filters, stop placement and 1% risk sizing that are not known.
- Against K1-vwap-01 (VWAP stop-and-reverse on MNQ) and E20H6-T1 (rest-of-day momentum on NQ at MNQ cost, gross 1.25 ticks vs 4.08 cost). Same direction-following family. The mechanism index was checked (r0_mechanism_index.md, lines 47-89, 271-282).

## 8. Re-dig verdict checks

Not a re-dig reader. No earlier verdict is overturned. Two weak notes for the lead:
- The ares record is a hypothetical C2 record, and E.13/E.20 never cited it. It neither supports nor weakens K1-cp2-01's Tier B fail, because its rules are unknown.
- E17 supports the program's general stance (V33) that unaudited or backfilled records are not evidence.

## 9. Fetch log

| url | UTC | sha256 | saved path | status | tool |
|---|---|---|---|---|---|
| https://collective2.com/robots.txt | 2026-10-18T08:39:44Z | 45865f1a8a8fa1792c3927d0f95bbefaef75a45411c5096f1b483eca70eafe8e | pages/R7/robots_collective2.com.txt | ok | curl |
| https://www.iasg.com/robots.txt | 2026-10-18T08:39:50Z | d92f413ec9abd6020d136d517a5f7e75c0261e2a27458a65366313d73647d31d | pages/R7/robots_www.iasg.com.txt | ok | curl |
| https://www.barclayhedge.com/robots.txt | 2026-10-18T08:39:55Z | 42f036947e9d0d8625b0afa34ff127ecc1efd9eaca7ab9c103e41e6d6d4cb945 | pages/R7/robots_www.barclayhedge.com.txt | ok (returned ionanalytics.com HTML) | curl |
| https://www.worldcupchampionships.com/robots.txt | 2026-10-18T08:40:01Z | ec280b95b3e73a6b5c875e6617ac49fbeb5fd5a78948e2cd030e5646f5c73721 | pages/R7/robots_www.worldcupchampionships.com.txt | ok | curl |
| https://www.futurestruth.com/robots.txt | 2026-10-18T08:40:12Z | db3682b5afcdaab3982e040989a24cdcd796b1b174ee3fe6fa60a75389660fa2 | pages/R7/robots_www.futurestruth.com.txt | ok | curl |
| https://www.darwinex.com/robots.txt | 2026-10-18T08:40:19Z | 57449cfa162344eed2cd0bb44807becd8ab7538e7ec4428950e6615bfa50f4af | pages/R7/robots_www.darwinex.com.txt | ok; site homepage redirect-loops (302), not read | curl |
| https://collective2.com/terms-of-service | 2026-10-18T08:42:22Z | d6e2d0919ef8eebba73d87dbba4d4e8d80853aaaff53da2ce821cf9f67861bdb | terms/collective2.com_terms.html | ok | curl |
| https://www.iasg.com/terms-of-service | 2026-10-18T08:42:28Z | eeabb180aa8d290899d63b2e5a9daf0a3c7d737992f6b615299ec47854cff708 | terms/www.iasg.com_terms.html | ok; terms forbid harvesting, no content pages fetched | curl |
| https://www.worldcupchampionships.com/disclaimer | 2026-10-18T08:42:33Z | da4fc4123507ddb214fb1a3493d774559b6a6bf5dfc61610f4553c218dff458f | terms/www.worldcupchampionships.com_terms.html | ok | curl |
| https://futurestruth.com/ | 2026-10-18T08:41:09Z | n/a | scratch only | ok (no terms page linked) | curl |
| https://www.nber.org/papers/w14424.pdf | 2026-10-18T08:43:56Z | 7e695ef499cff58480f5cf60dc76545b2199d77797f84326f5e6d14ccef40ab2 | pages/R7/bgr_nber_w14424.pdf | ok | curl |
| https://repositorio.fgv.br/... (Chague et al.) | 2026-10-18T08:44:02Z to 08:46:23Z | n/a | deleted | blocked (JS stub, HTML instead of PDF) | curl |
| http://www.repec.eae.fea.usp.br/documentos/Chague_Losso_Giovannetti_47WP.pdf | 2026-10-18T08:46:02Z and 08:46:40Z | n/a | none | failed (no connection, twice) | curl |
| (same PDF) | about 08:46Z | n/a | none | Firecrawl: "Insufficient credits" | firecrawl_scrape |
| https://api.openalex.org/works?search=... | 2026-10-18T08:45Z | n/a | none | throttled (429, daily IP budget used up) | curl |
| https://api.semanticscholar.org/graph/v1/paper/search (x2) | 2026-10-18T08:45:10Z | n/a | none | throttled (429) | curl |
| https://www.worldcupchampionships.com/world-cup-trading-championship-standings | 2026-10-18T08:47:04Z | d76135a5dc6c523bddda2ef12cbbaf935ad9fc7ed6514b901b696e71ee6c5ef8 | pages/R7/wcc_standings.html | ok (do not commit) | curl |
| https://www.worldcupchampionships.com/enter-now | 2026-10-18T08:47:10Z | 87d72ac62b7786282980940d76cf2cfd69ee4eed89ec5fb339f5ef1351f67fb1 | pages/R7/wcc_enter_now.html | ok (privacy text only; do not commit) | curl |
| https://catalogimages.wiley.com/images/db/pdf/0471681946.excerpt.pdf | 2026-10-18T08:47:53Z | dff8bc149c3f75b36223ebb3a96176f1045b6422f76c2d26d0d3fccc5a584b89 | pages/R7/gregoriou_2004_cta_excerpt.pdf | ok | curl |
| https://www.autumngold.com/Advisor/cta_profile.php?id=113924 | 2026-10-18T08:48:44Z | n/a | scratch | not public ("This program is not available as a public CTA profile.") | curl |
| https://www.societegenerale.asia/uploads/tx_bisgnews/SG_Prime_Services_CTA_Indices_March_2016_final_01.pdf | 2026-10-18T08:49:12Z | d3fab2df3a2eac27cb9029b433244c3de0c2990bb2d0d249521613178e031196 | pages/R7/sg_cta_indices_2016_03.pdf | ok | curl |
| https://www.rcmalternatives.com/disclaimer/ | 2026-10-18T08:50:09Z | 4b332da9e5f22ee12c33578403e491348eec0c9dc5445da9a6b994d2ee767c16 | terms/www.rcmalternatives.com_terms.html | ok | curl |
| https://www.rcmalternatives.com/?p=4510 | 2026-10-18T08:49:51Z | 52010325446e9c87c3fa792eaa509d2253f5add7d0cf3f71e1a1dd8afbc0b307 | pages/R7/rcm_crabel_multiproduct_1x.html | ok | curl |
| https://repository.hku.hk/bitstream/10722/184789/1/content.pdf | 2026-10-18T08:51:13Z | n/a | none | failed (no connection); hub.hku.hk 403 at 08:51:22Z | curl, scrapling get |
| https://collective2.com/details/148563155 | 2026-10-18T08:51:56Z | ce9676ed91f778133312a884ca121013f493b14a75e9ba6b9873ea600a39c40a | pages/R7/c2_details_148563155.html | ok | curl |
| https://collective2.com/leader-board | 2026-10-18T08:52:26Z | e1758c77b9cc13a397935b5eac72c14b2a69a4e87677378c6964d04e82cd0120 | pages/R7/c2_leader_board.html | ok | curl |
| https://collective2.com/details/131145247 | 2026-10-18T08:53:06Z | 6d33d4a3e7c73d6903f124acda7c8df8d80db974cdf6b566144237bbfdcb759a | pages/R7/c2_details_131145247_ares.html | ok | curl |
| https://collective2.com/details/149476882 | 2026-10-18T08:53:39Z | 7d4d8e19604eeb1283ef10b3fd64d9635b4e64568f0ef4a5880e5884108044c9 | pages/R7/c2_details_149476882_aresP2.html | ok | curl |
| https://collective2.com/details/150759166 | 2026-10-18T08:54:08Z | 965c51fff580885ddf0ef76270e9c570706ee9780eb3c025f94cccdd249b0881 | pages/R7/c2_details_150759166_dtlsmix.html | ok | curl |
| https://collective2.com/localize/faq | 2026-10-18T08:54:22Z | 3088230a76ee242610b66ba609e434c99a7e041f6eb930e224682fd235cd1c63 | pages/R7/c2_faq.html | blocked (403) | curl |
| https://wholesale.banking.societegenerale.com/fileadmin/indices_feeds/SG_CTA_Index_Constituents.pdf | 2026-10-18T08:55:44Z | 487046b9927e71388e1d08382d9cbab5f3925835eae403e4d92709bda586e7fa | pages/R7/sg_cta_index_constituents.pdf | ok (SG CTA Index only, not STTI) | curl |
| https://arxiv.org/abs/2507.01817v2 | 2026-10-18T08:56:25Z | a37e39c6bbbbe8bb4e7b1a4a48fbd2b377a07fff428412ae0063e257d9afd4bb | pages/R7/arxiv_2507.01817v2_abs.html | ok | curl |
| https://ideas.repec.org/a/eee/quaeco/v70y2018icp160-171.html | 2026-10-18T08:56:30Z | b5a91fffefa7a35ee4ce281a1cf25e91e42dd9226accf41ce4ef72672e3dc2ec | pages/R7/repec_dorfleitner_2018_qref.html | ok | curl |
| https://www.spglobal.com/robots.txt | 2026-10-18T08:57:14Z | n/a | scratch | blocked (403); no S&P DJI page fetched | curl |
| https://www.ampfutures.com/robots.txt | 2026-10-18T08:55:06Z | e334ed2c4a9539063a522a85e05840fa04539cbc74b93dbaff1a278f0216fd3e | scratch | ok; auto-systems page 301, not followed (time) | curl |

Terms read and logged (terms/terms_log.md, R7 lines):
- collective2.com: named public pages one at a time.
- iasg.com: forbidden; search results only.
- worldcupchampionships.com: named pages one at a time, internal only, do not commit.
- futurestruth.com: no terms page found.
- darwinex.com: not readable.
- barclayhedge.com: moved to ION Analytics; terms not read; search results only.
- rcmalternatives.com: named pages one at a time.

DO_NOT_COMMIT.txt has the IASG terms page and the WCC pages.

Budget notices:
- OpenAlex 429 "Insufficient budget" at 08:45Z.
- Semantic Scholar 429 x2 at 08:45Z.
- Firecrawl "Insufficient credits" at about 08:46Z. The tool's message: "Your Firecrawl credits ran out. Add credits or upgrade to keep going: https://www.firecrawl.dev/billing/bw5epbcjrpzvwg0ds2wf0wh7xf408gb7".
- WebSearch: 20 calls used, no over-budget notice.

## 10. Unfinished and unverified

- Full text not read for Kuo-Lin 2013 (HKU 403), Chague et al. (FGV stub, USP unreachable), Dorfleitner 2018 and Joseph et al. 2025 (abstracts only), the RFS 2014 version of BGR, and the CME Trading Challenge paper (Emerald).
- No STTI constituent list or long-run STTI series was retrieved (only the 2016 announcement and snippets).
- IASG and BarclayHedge program pages were not opened (IASG terms forbid; BarclayHedge terms unread). Search results named no intraday-only CTA program with a public multi-year record. That is a gap in the record, not proof none exists.
- Collective2 was read only from its default leader board (the C2Star list, 38 rows). The "Old-Timers" and "Futures" filters load by script and were not read, and only 3 intraday futures strategies were opened. More long-lived intraday futures records may exist there.
- C2's fill and slippage model is not verified (FAQ 403). "Includes fees/commissions" is C2's own wording.
- Not done: AMP Futures, Striker and iSystems broker-run system records, Darwinex (CFD/FX, cookie wall), NFA BASIC checks of any manager.
- The R7-C1 per-contract figure (37.6 MNQ ticks) is a crude estimate from 30 visible trades, not a published number.
