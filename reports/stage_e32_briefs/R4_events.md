# R4: Event structure in the soybean complex at minutes-to-hours horizons

Stage E.32, worker EventStructure-OpusHigh (root R4_events). Started 2026-10-26 23:03 PDT (first spawn: fetches only,
no output), resumed 2026-10-27 00:16 PDT (this output). Evidence pages and log:
reports/stage_e32_briefs/pages/R4_events/ (log.tsv). Helper scripts: reports/stage_e32_briefs/work/R4_events/.
No market data was read, no statistic was computed from data, no cmegroup.com page or archived copy of one was fetched.

Source labels: [A] academic (paper, thesis, conference paper), [R] regulator (CFTC staff paper, CFTC-hosted
filing), [X] exchange rule text as filed with the CFTC (CFTC-hosted, so secondary for CME), [G] government agency
(USDA), [F] firm or trade association, [P] pointer only (trade press, extension blog): never evidence.

Unit conversions used throughout. ZM tick = 0.10 USD per short ton = 10.00 USD per contract (E.32 brief table).
Percent moves are turned into ZM ticks with an ILLUSTRATIVE price P = 400 USD/short ton. This is an assumption for
scale, not a data read: 1% of 400 USD = 4.00 USD/ton = 4.00 / 0.10 = 40 ticks. At P = 350 the same 1% is 35 ticks,
at P = 450 it is 45 ticks. Random-walk scaling (an assumption) from the brief's sigma_1m = 3.15 ticks:
sigma_15m = 3.15 x sqrt(15) = 3.15 x 3.873 = 12.2 ticks; sigma_60m = 3.15 x sqrt(60) = 3.15 x 7.746 = 24.4 ticks.

---

## 1. USDA and industry release times against the CBOT sessions (topic a)

### 1.1 Current session grid (CT) and how it came about

| Date (trade date) | Globex hours for CBOT grains and oilseeds (CT) | Settlement | Source |
|---|---|---|---|
| before May 2012 | overnight Globex plus a day session opening 9:30; USDA reports at 7:30 fell in the pre-open halt and batch auction | floor, 1:14-1:15 p.m. | Huang 2022 [A]; Onur and Reiffen 2018 [R] |
| May 21, 2012 (Couleau et al.; the CFTC-hosted CBOT filing of 2012-05-16, version 002, names "June 3, 2012, for trade date June 4, 2012", and version 003 asks for "as soon as possible": the exact first date is not settled by the filings read) | from "Sunday to Friday, 6:00 p.m. to 7:15 a.m. CT and 9:30 a.m. to 1:15 p.m. CT" to "Sunday to Friday, 5:00 p.m. to 2:00 p.m. CT"; USDA 7:30 a.m. releases now hit live trading | moved to 2:00 p.m. (June 25, 2012), VWAP of all trades (floor and Globex) in the settlement minute | CBOT filings 2012-05-16 (R4_cftc_cbot_2012-05-16_002.txt, _003.txt) and 2013-03-13 [X]; Onur and Reiffen [R]; Couleau et al. 2018 [A] |
| January 2013 | unchanged | unchanged | USDA moves WASDE, Crop Production, Grain Stocks, Acreage, Prospective Plantings to 12:00 noon ET = 11:00 CT, still inside the day session (Huang 2022 [A]; Farm Progress 2012 [P]) |
| April 8, 2013 | Sun-Fri 7:00 p.m. - 7:45 a.m. and Mon-Fri 8:30 a.m. - 1:15 p.m. | close and settlement both 1:15 p.m. | CBOT filing 2013-03-13 [X] |
| June 8, 2015 | unchanged | TAS (Rule 524) allowed in corn, soybeans, soybean oil, soybean meal, wheat: first three listed months, settlement price +- 4 ticks | CBOT/CME Submission 15-148 [X] |
| July 6, 2015 | Mon-Fri day session extended to 8:30 a.m. - 1:20 p.m. (overnight still 7:00 p.m. - 7:45 a.m.) | settlement window kept at 1:14-1:15 p.m. CT; Globex keeps trading 5 minutes after it | CBOT Submission 15-204 [X] |

Consequence for the owned window (2020-12-01..2024-02-29) and the sealed test window (2017-05-01..2020-11-30): both
lie entirely in the post-July-2015 grid (overnight 19:00-07:45, pause 07:45-08:30, day 08:30-13:20, settlement
13:14-13:15, TAS available). There is no session-grid break inside either window [inference from the filings above;
holidays and early closes are not covered here].

### 1.2 Release calendar per event type

| Event | Publisher | Schedule | Release time | In CT | Session it lands in | Per year | Source |
|---|---|---|---|---|---|---|---|
| WASDE (with Crop Production in the months it is issued) | USDA WAOB (NASS for Crop Production) | monthly, pre-announced (2026: Jan 12, Feb 10, Mar 10, Apr 9, May 12, Jun 11, Jul 10, Aug 12, Sep 11, Oct 9, Nov 10, Dec 10) | 12:00 p.m. ET | 11:00 | day session, 2 h 30 min after the 08:30 open and 2 h 14 min before settlement | 12 | USDA WASDE page [G] |
| Grain Stocks | USDA NASS | quarterly: January, March, June, September | 12:00 p.m. ET (since Jan 2013) | 11:00 | day session | 4 (Jan with the annual Crop Production and WASDE; end-March with Prospective Plantings; end-June with Acreage) | Joseph and Garcia 2016 fn 1 [A]; Farm Progress [P] |
| Prospective Plantings | USDA NASS | annual, end of March | 12:00 p.m. ET | 11:00 | day session | 1 | Joseph and Garcia 2016 fn 1 [A] |
| Acreage | USDA NASS | annual, end of June | 12:00 p.m. ET | 11:00 | day session | 1 | Joseph and Garcia 2016 fn 1 [A] |
| Crop Progress | USDA NASS | weekly (Mondays) April to November; monthly "State Stories" December to March | 4:00 PM (ESMIS lists no zone; NASS times are Eastern [unverified from the page]) | 15:00 if ET | CLOSED: after the 13:20 close and before the 19:00 overnight open; absorbed at the 19:00 open | about 30-35 weekly issues [count is an estimate from "April to November", not a listed number] | ESMIS Crop Progress page [G] |
| U.S. Export Sales (weekly) | USDA FAS | every Thursday | 8:30 a.m. ET | 07:30 | OVERNIGHT session, 15 minutes before the 07:45 pause; the day session opens 08:30 on it | about 52 | FAS fact sheet (updated 2019-05-08) [G] |
| Daily export sales ("flash" sales) | USDA FAS | any business day a large sale is reported | 9:00 a.m. (zone not stated in the fact sheet; ET assumed [unverified]) | 08:00 if ET | inside the 07:45-08:30 PAUSE, so it is absorbed at the 08:30 open | irregular | FAS fact sheet [G] |
| NOPA monthly crush | NOPA (trade association), distributed by Refinitiv/LSEG to subscribers | monthly, dates published by NOPA (commonly mid-month; the exact day rule is [unverified]) | 12:00 noon "EST" | 11:00 | day session | 12 | NOPA crush report page [F] |

Notes on the table:
- The 2026 NOPA page states the 12:00 noon time for 2026 only. That NOPA used the same 11:00 CT time throughout
  2017-2024 is [unverified] here (no archived NOPA calendar was fetched).
- Grain Stocks, Acreage and Prospective Plantings stack on one release minute with each other or with WASDE, so a
  per-report-type effect cannot be separated on those days; this is a design fact for any event study.
- The March and June report days are also near the roll and first-notice windows of the May and July contracts
  (roll calendars are R-other workers' topic; flagged here only as a confound).

### 1.3 History of the move to releases during trading hours (verbatim)

- [A] Huang (2022, Illinois PhD thesis, ch. 3, saved R4_ideals_usda_release_policy_2022.txt): "World Agricultural
  Outlook Board reports were released on pre-announced dates at 7:30 AM (Central Time). The release coincided with a
  regular pre-open batch auction that took place during a trading halt for the CME electronic trading platform.
  After the end of the batch auction at 9:30 AM, regular trading hours started on Globex. In May 2012 the CME
  extended the trading hours to cover the early morning USDA release because of the concern of competition from
  another exchange (Arasu & Saphir, 2012). Since then, market participants can trade on the reports in real-time."
  and "In January 2013, the USDA changed the release time to 11:00 AM but the release was still during trading
  hours."
- [A] Couleau, Serra and Garcia (NCCC-134 2018, saved R4_couleau_serra_garcia_nccc2018.txt): "Since May 21, 2012,
  all sensitive USDA reports are released during trading hours (at 7:30:00 am CT until December 2012 and at
  11:00:00 am CT since January 2013)."
- [A] Joseph and Garcia (AAEA 2016, saved R4_joseph_garcia_aaea2016.txt): "In May 2012, the Chicago Mercantile
  Exchange (CME) extended its electronic trading hours. As a result, major United Stated Department of Agriculture
  (USDA) reports released at 7:30 a.m. central time, including World Agricultural Supply and Demand Estimates
  (WASDE), Crop Production (CP), Grain Stocks (GS), Acreage (AC), and Prospective Planting and Small Grains Summary
  (PP), coincided with real-time trading hours. In January 2013, USDA officially shifted these reports releases to
  11:00 a.m., formalizing trading hour releases."
- [P] Farm Progress, 2012-12-19 (saved R4_farmprogress_2012_release_times.html; trade press, pointer only; its
  content matches the [A] sources): "USDA statistical reports affected are: World Agricultural Supply and Demand
  Estimates, Acreage, Crop Production, Grain Stocks, Prospective Plantings, and Small Grains Summary."
- [A] Huang (2022) on the media lockup: "Prior to August 2018, USDA released its reports after an internal lockup
  procedure involving news media to assist with information dissemination. [...] prompted USDA to end news media
  access to the lockup." and "it coincided with more pervasive delays in the release of market information likely
  caused by server congestion or related accessibility issues." The sealed test window (2017-05..2020-11) therefore
  straddles the August 2018 lockup change; the discovery window (2020-12..2024-02) is entirely after it.
- [X] CBOT filing of 2013-03-13 (CFTC-hosted, saved R4_cftc_cbot_2013-03-13.txt): current hours "Sunday to Friday,
  5:00 p.m. to 2:00 p.m. CT", proposed "Sunday to Friday, 7:00 p.m. to 7:45 a.m. CT" and "Monday to Friday, 8:30
  a.m. to 1:15 p.m. CT", effective "Sunday, April 7, 2013 for the Monday, April 8, 2013 trading date"; "In June 2012,
  the Exchange extended afternoon floor hours for these products and moved settlement to 2:00 p.m. CT".
- [X] CBOT Submission 15-204 (CFTC-hosted, saved R4_cftc_cbot_2015_hours_1320.txt): "effective on Sunday, July 5,
  2015 for trade date Monday, July 6, 2015", new hours "Sunday - Friday, 7:00 p.m. - 7:45 a.m. CT and Monday -
  Friday, 8:30 a.m. - 1:20 p.m. CT"; "A continuation of trading would allow TAS liquidity providers to hedge or
  trade as needed after 1:15 p.m./CT and not impact or influence the 1:14-1:15 p.m. CT settlement window."

Verdict on the planner pointer "11:00 CT releases have been made into live trading since 2012": PARTLY VERIFIED.
Releases have hit live trading since May 21, 2012, but at 7:30 CT until December 2012; the 11:00 CT time dates from
January 2013.

---

## 2. Price discovery after USDA releases: jump, drift or reversal, settling horizon (topic b)

### 2.1 What is published, per study (full text read unless marked)

| Study | Market, sample | Events | Price result | Volatility result | Direction after the jump |
|---|---|---|---|---|---|
| Huang (2022) ch. 3 [A] | corn nearby, real-time era June 2012 - Aug 2019 | 104 real-time events (WASDE/NASS) | 40% of the 1-hour price change in the first minute, about 75% by 10 minutes, 90-100% by 35-45 minutes | spike in first minutes | conditional on knowing the 60-minute direction: big events keep drifting that way to about 40-49 min; small events overshoot (negative ITR from 40 min) |
| Joseph and Garcia (2016) [A] | soybean nearby (ZS), June 2010 - May 2014, 15-second returns | 29 trading-hour releases (June 2012 - May 2014) vs non-trading-hour releases | not measured as a level | trading-hour releases: smaller first spike, elevated 5-6 min, report-day variance above control for 30-40 min, intermittently to about 60 min | Spearman correlations of first return with later returns: few significant, mostly negative in the first minute, "difficult to establish a solid pattern" |
| Lehecka, Wang and Garcia (2014) [A, abstract only] | corn, July 2009 - May 2012 (pre-real-time) | major USDA reports | "market reactions persist for approximately ten minutes" | - | "little evidence exists to support systematic under- or overreactions" |
| Adjemian and Irwin (2018) [A, abstract only] | grain futures, 2009-2014 | USDA crop reports | - | "heightened volatility dissipates within the space of a few trading minutes" | not stated in the abstract |
| Kauffman (2013) [A] | corn, 2012 WASDE releases | WASDE | - | "excessive for 30 consecutive minutes"; "84 percent of the time" in the 30-60 min window; "only slight evidence" beyond 2.5 h | not studied |
| Couleau, Serra and Garcia (2018) [A] | corn nearby, 2008-2015, tick data | announcement vs other days | announcement-day jumps in period 3 (real-time): +4.1 / -3.8 cents/bu average | jumps on 100% of real-time announcement days, 83% with a cluster inside 2 minutes | not studied |
| Bian, Serra and Garcia (NCCC-134 2018) [A] | corn and soybeans, January 2014 - May 2017 (11:00 CT releases) | USDA announcement days | - | "volatilities in both corn and soybean would response to USDA announcements immediately after the news being published. The elevated level of volatilities would not settle down within the first hour after announcements." (R4_bian_serra_garcia_nccc2018.txt) | not studied |
| Karali (2012), as summarised by Bian et al. [A, secondary; original not read] | daily corn, lean hogs, soybeans, SOYBEAN MEAL, soybean oil, 1995-2009 | Crop Progress, Feed Outlook, Grain Stocks, Hogs and Pigs, others | - | daily: "Crop Progress, Grain stocks, and Hogs and Pigs also increase variances of both corn and soybean meal" | not studied (daily) |
| Hu and Mallory (NCCC-134 2022; JFM 2025 45(11)) [A] | Dalian soybean complex incl. soybean meal, 2010/2011 - 2020/2021 | major USDA reports (released while Dalian is closed) | JFM abstract: "On average, price reactions dissipate within a few minutes, while increased trading volume can last up to an hour"; during the trade war USDA reports "remained influential on soybean no. 2 and soybean meal futures" (R4_hu_mallory_nccc2022.txt; R4_ideas_jfm2025_45_11.html, abstract) | NCCC abstract: reactions "can persist for as long as an hour, depending on the size of the information shock and market liquidity" | not studied in the abstract |
| Shubitidze, Adjemian and Dorfman (AAEA 2026) [A, abstract only] | corn, soybeans, wheat, DAILY prices | WASDE ending stocks, Grain Stocks, with analyst forecast distributions | responses depend on forecast dispersion and "pre-report market tightness"; "the direction of the effect varies across markets and report types" (R4_ideas_shubitidze2026.html) | - | daily only; relevant for building an ex-ante surprise measure, which needs analyst surveys the project does not own |
| Janzen, farmdoc daily 2025-09-15 [P] | corn and soybean new crop, May-Sep 2025 | 5 WASDE + June 30 Acreage | Sep 12 2025: soybeans fell up to 13 c/bu in 11:00-11:15, closed up 13 c | - | pointer: 1 large reversal, and 2 small mismatches, in 6 events |

No study found that tests the sign of the 15-90 minute post-release path against the sign of the initial jump in a
form a trader could use (that is, conditioning only on information available at the entry time). No study of CBOT
soybean MEAL (ZM) or soybean oil (ZL) announcement effects at the intraday level was found; the only intraday
soybean-meal announcement study found is on Dalian (Hu and Mallory), where USDA news lands while that market is
closed, and the only CBOT meal evidence is daily (Karali 2012, via Bian et al.). No intraday study of the NOPA crush
release was found (one WebSearch aimed at it returned none). Discovery status in section 9.

### 2.2 Verbatim evidence and equations

Huang (2022), complete price change (CPC), eq. (3.1), saved R4_ideals_usda_release_policy_2022.txt:

    CPC_{t,i} = sign(P_{T,i} - P_{c,i}) * (P_{t,i} - P_{c,i})        (3.1)

Symbols: P_{c,i} = log VWAP of the last five trading minutes before announcement i; P_{T,i} = log VWAP of minutes
61-65 after the announcement (real-time era); P_{t,i} = log one-minute VWAP at minute t after the release; CPC in
percent. Quote: "In the real-time era P_{T,i} is the VWAP for the 61-65 minutes after the announcement takes place.
[...] For P_{c,i}, we use the VWAP of the last five trading minutes before announcement in both eras."

Informed trader return (ITR), same section: "ITR_{t,i} = sign(P_{T,i} - P_{c,i}) * (P_{T,i} - P_{t,i})". Quote:
"Our trader is assumed to be informed (i.e., to correctly interpret the implications of the reports to the market)
and to trade in the correct direction".

Results (verbatim): "in the real-time era, price changes necessary to reflect the USDA information are 1.63% for all
events (2.6% and 0.6% for big and small events) [...] it takes only one minute for the price to reflect 40% of the
USDA information. After the first 10 minutes the price reflects about 75% of the information and then moves to a
phase of much slower price discovery. Overall, it takes around 35-45 minutes to reflect 90%-100% of the new
information."

Table 3.1 Panel B (corn, real-time era June 2012 - August 2019, ITR in percent, exit at 60 minutes):

| Entry after release | All | Big | Small |
|---|---|---|---|
| 0-2 s | 1.33*** | 2.14*** | 0.54*** |
| 1 min | 0.72*** | 1.13*** | 0.33*** |
| 2-5 min | 0.61*** | 0.91*** | 0.31*** |
| 6-9 min | 0.47*** | 0.78*** | 0.18** |
| 10-19 min | 0.31*** | 0.65*** | -0.01 |
| 20-29 min | 0.24*** | 0.55*** | -0.06 |
| 30-39 min | 0.15*** | 0.36*** | -0.06 |
| 40-49 min | 0.04 | 0.18*** | -0.10** |
| 50-59 min | -0.02 | 0.04 | -0.07** |

Huang on small events: "Notice that during small events the price initially moves in the opposite direction of the
final price." and on risk: "except for small events during the real-time release era, where ITRs become negative
after 10 minutes following the release."

Critical reading for a directional label (my analysis, not Huang's claim):
- ITR conditions on sign(P_T - P_c), the 60-minute outcome. It is therefore NOT a tradable return: it is the drift
  that remains toward the eventual 60-minute level. It equals the directional label of family 2 only on events where
  the early jump and the 60-minute move share a sign.
- What it does say: for big events, about 0.65% of corn price is still to come after minute 10, in the direction of
  the eventual 60-minute move. Translated to ZM scale (assumption: the same percent applies to ZM; P = 400 USD/t):
  0.65% x 400 = 2.60 USD/t = 26 ticks between minute 10-19 and minute 60. Check: 26 ticks is about 1.07 sigma_60m
  (26 / 24.4), so it is the size of one ordinary hour of ZM noise, and only for big events, and only if the
  direction were known.
- For small events the sign flips after minute 40 (-0.10%; 0.10% x 400 USD = 0.40 USD/t = 4 ticks on the same
  conversion), an overshoot-then-correction pattern. Even direction-known, 4 ticks gross against the 1.59-tick
  Topstep market-order break-even (reports/stage_e28_ranking.md row "| 6 | topstep | ZM |", column mu*_mkt = 1.59)
  leaves about 2.4 ticks, and 4 ticks is 0.16 sigma_60m (4 / 24.4), so it would be invisible in 39 months of events.
- A tradable family-2 label must replace sign(P_T - P_c) by an entry-time quantity (sign of P_{t0} - P_c at
  t0 = 5-15 minutes). No paper read reports that conditional.

Joseph and Garcia (2016), saved R4_joseph_garcia_aaea2016.txt. Returns, eq. (1): "r_{i,t} = ln(P_{i,t}/P_{i,t-1})
x 100, with P_{i,t} being the last price of the nearby soybean futures contract in each 15-second interval i, on
trading day t." Verbatim results: "releases during trading hours result in a smaller volatility spike which extends
for five to six minutes at a higher magnitude"; "the volatility during the first 15-seconds for trading hour release
peaks at lower magnitude (.51) following report release, but persists at a higher level of .15 for the first 2
minutes and .10 for the next 5 to 6 minutes before dropping to a stable .05 level"; "it is significant in the second
period for 30 to 40 minutes after the release and appears to persist intermittently for nearly 60 minutes";
sample: "the second period is June 2012-May 2014 where 29 reports were released during trading" hours; on direction:
"For both periods, the first significant interval correlation is negative which raises the possibility that the
market overreacts to news within the first minute and then corrects quickly in later periods. A clearly persistent,
but not significant pattern of negative cumulative correlation emerges for both periods. [...] Nevertheless, it is
difficult to establish a solid pattern from the results." and caveats "1) the correlations are based on small sample
sizes; 2) only a few intervals reflect significant correlations with the first return; and 3) the magnitude of these
correlations are not large." The units of the ".51" and ".05" volatility figures are average normalized 15-second
return variances as defined in the paper; I do not convert them to ticks because the normalization is not fully
recoverable from the lines read.

Kauffman (2013, NCCC-134 version of the KC Fed Economic Review article), saved R4_kauffman_nccc2013.txt: "trading
during the information releases in 2012 has led to brief periods of excessive volatility immediately after the
reports were released, but the higher volatility did not persist much beyond 60 minutes."; "In 2012, volatility was
excessive for 30 consecutive minutes following WASDE releases. In the 30-to-60-minute window after WASDE releases,
excess volatility was evident 84 percent of the time."; "There was only slight evidence that excess volatility
persisted more than 2.5 hours after WASDE releases." Scope: corn only, and 2012 only, which is when releases were at
7:30 CT (before the January 2013 move to 11:00).

Couleau, Serra and Garcia (2018), saved R4_couleau_serra_garcia_nccc2018.txt: "By turning to announcement days, jumps
occur 100% of the time in period 3 and 83% of those days have a jump cluster within 2 minutes after the announcement
time"; "For announcement days, average positive (negative) jump size has increased from 1.6 (-2.8) cents per bushel
in period 1, to 4.6 (-6) cents per bushel in period 2, and to 4.1 (-3.8) cents per bushel in period 3"; and outside
announcements: "Non-announcement days register efficient price jumps of smaller size [...] 1.1 (-1.2) cents/bu in
period 3". Scope: corn only.

Lehecka, Wang and Garcia (2014) and Adjemian and Irwin (2018): full text not obtained (publisher-restricted; IDEAS
abstract pages saved, R4_ideas_lehecka2014.html, R4_ideas_adjemian_irwin2018.html). Quotes from the abstracts only:
Lehecka et al.: "Strongest price reactions to the releases are found immediately after the market opens, and market
reactions persist for approximately ten minutes. [...] little evidence exists to support systematic under- or
overreactions in prices. Other more subtle reactions occur in the last trading session before USDA announcements as
traders adjust their market exposure in anticipation of the release." (corn, July 2009 - May 2012, i.e. the HALT era:
"after the market opens" means the 9:30 open after a 7:30 release). Adjemian and Irwin: "without a trading halt,
ensuing real-time trading on USDA crop announcements exhibits noticeable volatility spikes in agricultural futures
markets, but that this heightened volatility dissipates within the space of a few trading minutes. [...] continuously
traded crop markets take nearly the same time to fully absorb these shocks, following a very similar time path."
Which markets and the minute counts in the body are [unverified].

### 2.3 E.31 context (not new evidence)

E.31 measured passive ZM fills 0-5 minutes after a USDA release at an average -8.98 ticks per fill (68 fills;
reports/E.31_RETURN.md, as stated in the R4 brief). That is a markout of a resting order, consistent with the
literature's picture of a fast one-sided repricing in the first minutes (Couleau et al.: jump clusters inside 2
minutes; Huang: 40% of the hour's move in minute 1). It says nothing about the 15-90 minute direction.

### 2.4 What this means for family 2 (post-USDA path, entry 5-15 minutes after)

- Mechanism worth testing: big-surprise events where price discovery is still incomplete at minute 10 (Huang: ~75%
  done for corn), so continuation toward the 60-minute level is plausible; and small events where the first move is
  wrong-signed or overshoots (Huang small events; Joseph and Garcia negative first-minute correlations; the farmdoc
  2025 anecdote as a pointer). The two give OPPOSITE signs, so the label must be conditioned on jump size (big vs
  small), which Huang splits at the median absolute CPC, an ex-post quantity. An ex-ante proxy is needed: the
  absolute return from P_c to minute 5, scaled by the pre-event sigma.
- Sample size is the binding problem. Distinct "major" 11:00 CT USDA days per year: 12 WASDE days (January also
  carries Grain Stocks) + end-March (Grain Stocks with Prospective Plantings) + end-June (Grain Stocks with Acreage)
  + end-September (Grain Stocks alone) = 15. Over the 39-month discovery window: 15 x 39 / 12 = 48.75, about 49
  (the planner's "about 40" is the same order; government shutdowns, e.g. the cancelled October 2013 WASDE noted by
  Joseph and Garcia, can remove some). NOPA adds 12 per year, 39 in the window, if they never share a day with a
  USDA release [unverified]. A median split of 49 leaves about 24 big events. With a per-event 60-minute noise of
  sigma_60m = 24.4 ticks (random-walk assumption; event days are noisier, so this is optimistic), the standard error
  of a mean over 24 events is 24.4 / sqrt(24) = 24.4 / 4.90 = 4.98 ticks, so only a mean effect of about 10 ticks
  (2 SE) or more would show at the 5% level before any multiple-testing correction. Check: 10 ticks = 0.25% of
  400 USD/t, below Huang's direction-known big-event drift after minute 10 (0.65%, 26 ticks), so the test has power
  only if a tradable signal keeps at least about 40% (10 / 26) of the direction-known drift.
- Drop: anything in minutes 0-2 (fast traders, E.31's -8.98 tick markout).

---

## 3. Daily price limits and limit-expansion days for ZM, ZS and ZL (topic c)

Sources: CBOT Submission 23-083 (filed 2023-03-31, CFTC-hosted, saved R4_cftc_cbot_2023_daily_limit_amend.txt) [X];
CME Submission of 2020-02-27 on lean hogs, which describes the CBOT 2014 grain mechanism (CFTC-hosted, saved
R4_cftc_cme_sub_2020_leanhog_varlimit.txt) [X]. No cmegroup.com page was used.

### 3.1 Rule text (ZM, CBOT Rule 13102.D, as shown in the 2023 blackline)

Reset formula (verbatim): "Initial and expanded daily price limits for Soybean Meal futures are reset every six
months. The first reset date would be the first trading day in May based on the following: Daily settlement prices
are collected for the nearest July contract over 45 consecutive trading days before and on the business day prior to
April 16th. The average price is calculated based on the collected settlement prices and then multiplied by seven
percent. The resulting number, rounded to the nearest 5 dollars per ton, or 20 dollars per ton, whichever is higher,
will be the new initial price limits for Soybean Meal futures. The new expanded price limit shall be the new initial
price limit multiplied by 1.5 and rounded up to the nearest 5 dollars per ton." The November reset uses "the nearest
December contract over 45 consecutive trading days before and on the business day prior to October 16th".

Soybean-complex linkage (verbatim; the blackline's insertions and deletions are not distinguishable in the text
extraction, so the exact final wording is uncertain): "Should any futures component of the Soybean Complex (Soybean,
Soybean Meal, and Soybean Oil) settle at the initial price limit, the daily price limits for the other futures
components shall increase to the expanded price limit [...] Price limits will remain at the expanded price limit
until all futures component contract months settle at a price change less than the initial price limit at which
point daily price limits for all futures components of the Soybean Complex shall revert back to their respective
initial price limits the following business day."

Spot month: "There are no price limits on spot-month contracts. Contract expirations become the spot-month on the
second Business Day preceding the first day of the delivery month, which is also first position day." (footnote 1).

Changes effective trade date May 16, 2023 (verbatim, Submission 23-083): (1) trigger: "expanded price limits are
triggered when one contract within the first five (5) through eight (8), depending on the Contract, non-spot
contract months settles at the initial price limit rather than two (2) contract months"; (2) staying expanded: "at
least one (1) contract month must settle at a price change equal to or greater than the initial price limit for
expanded price limits to remain in effect on the next Business Day"; (3) ratchet: "After two (2) consecutive Business
Days of at least one (1) contract month settling at the expanded price limit, the initial price limit is updated to
become the expanded price limit and the expanded price limit will be increased by 50 percent."

History (verbatim, 2020 CME submission): "To avoid frequency in limit settlements, CBOT implemented a variable price
limit mechanism in its grain and oilseeds markets in 2014. Since its implementation in the CBOT grain and oilseed
markets, there has been a significant reduction of the number of days those markets have settled at the limit
price." (its Exhibit 1 with the counts is an image; no count was extracted).

### 3.2 Worked example (ZM)

Assume the 45-day average July settlement before April 16 is 400.0 USD/short ton (illustrative, not a data read).
- 7% x 400.0 = 28.0 USD/ton. Rounded to the nearest 5 USD = 30 USD (28 is nearer 30 than 25). Max(30, 20) = 30 USD.
  Initial limit = 30 USD/ton = 30 / 0.10 = 300 ticks = 300 x 10.00 = 3,000 USD per contract.
- Expanded = 30 x 1.5 = 45 USD, already a multiple of 5, so 45 USD/ton = 450 ticks.
- Ratchet after two consecutive expanded-limit settlements: initial becomes 45, expanded 45 x 1.5 = 67.5, rounded up
  to 70 USD/ton = 700 ticks.
- Check against the brief's median daily range for ZM, 96 ticks: the initial limit is 300 / 96 = 3.1 median daily
  ranges away from the prior settlement, so limit-bound days are rare tail events. Under the random-walk assumption
  the 1-day sigma over the day session (290 minutes from 08:30 to 13:20) is 3.15 x sqrt(290) = 3.15 x 17.03 = 53.6
  ticks, and 300 ticks is 5.6 of those sigmas (overnight adds variance, so the true distance in sigmas is smaller,
  and limit moves cluster on USDA days and on large weather shifts).

### 3.3 What this means for a ZM directional search

- Limits bite on large USDA days (June 30 Acreage/Grain Stocks is the classic case) and on ZS- or ZL-driven days,
  because a limit settlement in any one of the three legs expands the other two. A directional label that crosses a
  limit-locked interval has no tradable exit price: E.33 must flag minutes where the best bid or ask sits at the
  limit and drop or censor labels that cross them (the Databento definitions schema carries daily limit prices per
  instrument [field names are DataFacts' topic; not verified here]).
- Limit-day counts for ZM in 2020-12..2024-02 are not published in any source read; they are a DataFacts count
  (settlements against definition limits), not a literature fact.
- Huang (2022, footnote 19) on why limit days distort microstructure measures: "When the price hits one side of the
  limit, one side of the book is restricted from trading and the other side accumulates a large number of contracts.
  This results in misleading BAS and depth measures."

---

## 4. Overnight gaps, weather and the Sunday-night open (topic d)

### 4.1 Structure of the gaps (from the session grid in section 1.1)

| Gap | Clock time (CT) | Length | Scheduled information inside it | Where it is priced |
|---|---|---|---|---|
| Daily close to overnight open | 13:20 -> 19:00 (Mon-Thu) | 5 h 40 min | Crop Progress, Mondays 15:00 if ET (April-November); afternoon weather-model updates [timing of model runs unverified] | 19:00 overnight open |
| Weekend | Fri 13:20 -> Sun 19:00 | 53 h 40 min (13:20 Fri to 13:20 Sun is 48 h, plus 5 h 40 min) | weekend weather; any weekend policy news | Sunday 19:00 open |
| Morning pause | 07:45 -> 08:30 | 45 min | daily flash export sales (09:00, zone assumed ET = 08:00 CT [unverified]) | 08:30 day open |
| Inside the overnight session | 19:00 -> 07:45 | 12 h 45 min | weekly Export Sales Thursday 07:30 (8:30 a.m. ET, FAS fact sheet) | continuously, on thin overnight volume |

The "overnight gap at 08:30" of the planner's family 4 therefore covers only a 45-minute pause; the large
information gaps are at 19:00 (daily) and at the Sunday 19:00 open (weekly). For ZM, E.28's table gives a day-session
volume share of 0.83, so about 17% (1 - 0.83) of volume trades in the 12 h 45 min overnight session. A family-4
label at 08:30 should define its "gap" as P(08:30 first trade or mid) minus P(13:15 settlement of the prior day),
which bundles the 19:00 open jump and the whole overnight drift; the two components need separate features.

### 4.2 Evidence found

- [A] Jin, Kearney, Li and Yang (MPRA 97134, 2019; Dalian Commodity Exchange soybean meal, June 2, 2008 - June 28,
  2013, 1,093 trading days, day session 9:00-11:30 and 13:30-15:00 in that sample, so no night session; saved
  R4_mpra_97134.txt), Table 3: the overnight return r0 (previous close to today's open) predicts the last half-hour
  return of Dalian soybean meal: beta_r0 = 28.895 (t = 2.96) alone, 29.518 (t = 3.05) jointly with r1, R2 0.97% and
  1.91%. For Dalian soybeans the overnight return does not predict (beta = -7.780, t = -0.82). Caption verbatim:
  "r0 is the return from the previous day's close until today's open (overnight return), and r1 represents the return
  during the first half-hour trading session (excluding the overnight return)."
- [A] Baltussen, Da, Lammers and Martens (JFE 2021; CBOT soybean meal "SM", 1982-07-06 to 2020-05-01, 9,458 days,
  hours 08:30-13:20 at the end of the sample; saved R4_baltussen_jfe2021_firecrawl.md), Table B3: the return from the
  previous close to 30 minutes after today's open, r_ONFH, does NOT predict the last half-hour for CBOT soybean meal:
  beta_ONFH = -0.95 (t = -1.58), R2 0.03%, out-of-sample R2 -0.04%. Section 5.3 discusses this paper fully.
- [P] Trade commentary only, no measurement: DTN 2017-06-19 ("selling interest tied to weekend weather had subsided by
  early Monday" per the search summary), Barchart ("weather derivatives at heart"), Pro Farmer "Ahead of the Open"
  notes. These are pointers: they say weekend and overnight weather shifts move the Sunday open and the overnight
  session, and that some of those moves reverse by the morning, but give no sample, no magnitude and no test.
- Discovery leads not read (titles only, Crossref, [unverified]): Stevens (1991, Journal of Futures Markets 11(1),
  doi 10.1002/fut.3990110108), "Evidence for a weather persistence effect on the corn, wheat, and soybean growing
  season price dynamics" (daily data); Singal and Tayal (2019, Journal of Futures Markets, doi 10.1002/fut.22069),
  weekend effect in futures (daily data).

Stopping rule for topic d: four discovery queries (two WebSearch on overnight and weekend weather effects, one on
crop-condition reactions, three Crossref title queries) surfaced no intraday study of CBOT soybean-complex overnight
gaps, Sunday opens or Crop Progress reactions after 2013. The literature gap is real as far as these queries reach;
it is not proof that no such study exists (Google Scholar was not queried directly; AgEconSearch full-text search
was not run).

### 4.3 What this means for family 4 (gap continuation or reversal)

- Worth testing as a FEATURE inside families 1 and 3 rather than as its own family: the only direct soybean-meal
  evidence is Dalian (a different market with no night session in that sample) and points to overnight-return
  CONTINUATION into the last half-hour (t about 3), while the CBOT soybean meal evidence over 38 years (Baltussen) is
  a NEGATIVE, insignificant slope for the overnight-plus-first-half-hour return. The two disagree in sign.
- Strata that must be separate: Sunday-open days (weekend weather, 53 h 40 min gap) vs Monday-Thursday 19:00 opens;
  growing season (roughly May-August, when weather drives the overnight) vs the rest; Crop Progress Mondays
  (April-November) vs other days; Thursday (Export Sales at 07:30 inside the overnight session).
- Magnitude check under the random-walk assumption: a 45-minute pause carries no ZM trading, so the 08:30 "gap" is
  mostly the overnight session's 12 h 45 min = 765 minutes of drift: 3.15 x sqrt(765) = 3.15 x 27.66 = 87.1 ticks if
  the overnight had the same per-minute sigma as the day (it is quieter, so the true figure is lower). A
  continuation or reversal edge of 2-3 ticks is 2-3% of that noise, which needs hundreds of independent days; 39
  months give about 39 x 21 = 819 trading days, about 160 of them Sunday opens.

---

## 5. Settlement mechanics, pre-close behaviour and intraday momentum (topic e)

### 5.1 Settlement window and TAS

- [X] 2008 (CBOT Market Regulation Advisory RA0815-1, CFTC-hosted, saved R4_cftc_cbot_2008-09-08.txt): the Globex
  Control Center "will settle the futures contracts based upon Globex activity occurring from 1:14:00 to 1:15:00 p.m.
  rather than on trading activity occurring in the pit" (then for rough rice, as part of a pilot "presently operating
  in Wheat futures").
- [R] Onur and Reiffen (CFTC, 2018, saved R4_onur_reiffen_cftc.txt): "The settlement price procedure for several grain
  contracts changed on June 25, 2012. Prior to that date, the settlement price was based on trades made during the
  final minute of trading on the CBT trading floor; equal to the weighted average price of trades made on the floor
  during that minute. After that date, the settlement price was based on the weighted average of all trades made in
  that minute, whether on the floor, or through electronic trading." Footnote 11: "Prior to June 25, 2012, the
  settlement period minute was from 1:14 p.m. - 1:15 p.m. and after the change it became 1:59 p.m. - 2:00 p.m."
- [X] Since April 8, 2013 settlement moved back with the close to 1:15 p.m. (CBOT 2013-03-13 filing: "the Exchange
  plans to determine settlement prices consistent with the new market close time of 1:15 p.m."), and since July 6,
  2015 Globex trades until 13:20 while the "1:14-1:15 p.m. CT settlement window" stays (Submission 15-204).
- The exact current ZM settlement algorithm (VWAP over 13:14:00-13:15:00 on Globex, and the tie-break rules when
  volume is thin) is [unverified]: the only full statements read are from 2008 and 2012, and CME's own settlement
  pages are out of bounds for this stage.
- [X] TAS (Submission 15-148, CFTC-hosted, saved R4_cftc_cbot_2015_tas_rule524.txt): Rule 524 "effective on Sunday,
  June 7, 2015 for trade date Monday, June 8, 2015"; "CBOT will begin to permit orders for the first three listed
  contract months and certain spreads in Corn, Soybean, Soybean Oil, Soybean Meal, Wheat and KC HRW Wheat futures to
  be entered into CME Globex for pricing at the settlement price or any valid price increment four ticks higher or
  lower than the settlement price." For ZM, four ticks = 4 x 0.10 = 0.40 USD/ton = 40 USD per contract. The 2015
  hours filing gives the purpose of the 13:15-13:20 extension: "allow TAS liquidity providers to hedge or trade as
  needed after 1:15 p.m./CT".

### 5.2 Pre-close to settlement reversals (Onur and Reiffen)

Test (verbatim): "we define a binomial variable which is equal to one if (P_{c,t} - P_5) and (P_{o,t+1} - P_{c,t})
have opposite signs and zero if they have the same sign", where "P_{c,t} is the closing price on day t, P_{5,t} is the
volume weighted average price in the 5 minutes before the settlement period on day t, and P_{o,t+1} is the opening
price on day t+1." Result: "We find that the percentage of reversals falls from 57.3% under the old regime to 48.7%
under the new, a decline which is statistically significant at the 1% level." Scope: CBOT corn lead month,
proprietary CFTC trade data, pre- and post-June-2012.

Reading for ZM: the measured reversal is from the last 5 minutes before settlement to the NEXT DAY's open, not an
intraday move. Under the electronic settlement regime the reversal share (48.7%) is at or below a coin flip, i.e.
no evidence of a pre-close move that reverts overnight. Worked number: 48.7% vs 50% on N days has standard error
sqrt(0.25 / N); the share of N needed for 1.3 points to be 2 SE is N = 0.25 x (2 / 0.013)^2 = 0.25 x 23,669 = 5,917
days, far more than any sample, so 48.7% is best read as "no reversal", not as "momentum". The number of days in the
Onur and Reiffen post-period is not in the lines read.

### 5.3 Intraday momentum: first half-hour (or rest of day) predicting the last half-hour

| Study | Market | Sample | Result for the first-half-hour predictor | Other predictors |
|---|---|---|---|---|
| Gao, Han, Li and Zhou (Dec 2015 draft read; cited as "Gao et al. (2018)" by Jin et al.; published version not read) [A] | S&P 500 ETF (SPY), 10 other ETFs, FTSE and Euro Stoxx futures; crude oil and gold futures; currencies | 1993-2013 (SPY) | SPY: R2 1.6% in sample, OOS R2 1.2%; "the intraday momentum does not show up in major currency pairs or commodity futures" | twelfth half-hour adds; R2 2.6% combined, OOS 1.8% |
| Jin, Kearney, Li and Yang (MPRA 2019) [A] | Shanghai copper and rebar, Dalian soybean and soybean meal | soybean meal 2008-06-02 to 2013-06-28 | soybean meal: beta 51.997 (x10^-3 scale), t = 2.60, R2 0.90%; sign version t = 2.89 | second-to-last half-hour t = 2.48; overnight return t = 2.96 |
| Baltussen, Da, Lammers and Martens (JFE 2021) [A] | 60+ futures incl. CBOT soybean meal (SM), soybeans (SY), soybean oil (BO), corn (CN) | SM 1982-07-06 to 2020-05-01 | SM: beta_ONFH = -0.95 (t = -1.58), OOS R2 -0.04%; SY -1.17 (t = -2.17); BO -0.80 (t = -1.40); CN -0.13 (t = -0.26) | SM: r_M (end of first half-hour to the last hour) beta 2.49 (t = 3.22) in a joint regression with OOS R2 -0.27%; r_ROD beta 0.18 (t = 0.42) |

Verbatim, Gao et al. (saved R4_gao_han_li_zhou_mql5.txt): "For out-of-sample (OOS) predictability, the R2 is 1.2%
using the first half-hour return as the only predictor, and 1.8% when this predictor is combined with the twelfth
half-hour return predictor." and "However, the intraday momentum does not show up in major currency pairs or
commodity futures. This is perhaps expected because, unlike the stock market, the daily open and close for currency
and commodity futures are unclear because they are traded globally around the clock." The commodity futures tested
are "crude oil and gold" (Appendix table note); grains were not tested.

Verbatim, Jin et al.: "We observe that the first 30-minute returns positively predict the last 30-minute returns for
all four contracts with a slope of 0.073 for soybean, 0.052 for soybean meal, 0.067 for copper, and 0.103 for steel.
All of these are significant at a 5% level. Furthermore, the R2 for these four contracts are 1.80%, 0.90% 1.36% and
3.32%, respectively." (Table 2 prints the soybean meal slope as 51.997 on a x10^-3 scale with t = 2.60; the text's
0.052 is the same number.) No t-statistic of 3.07 appears in the Jin et al. tables read; the nearest soybean-meal
values are 3.05 (overnight return, joint regression) and 2.96 (overnight alone).

Verbatim, Baltussen et al. (abstract): "Using intraday returns on over 60 futures on equities, bonds, commodities, and
currencies between 1974 and 2020, we find strong market intraday momentum everywhere. The return during the last 30
minutes before the market close is positively predicted by the return during the rest of the day (from previous
market close to the last 30 minutes). [...] and reverts over the next days." And on commodities: "The results are
slightly weaker for commodity futures (Table B3) and currency futures (Table B4). Still, for about 40% to 50% of the
contracts, r_ROD has a positive and significant R2_OOS." Pooled softs (their label for grains and softs): beta_ONFH
0.25 (t = 0.70), beta_ROD 0.65 (t = 2.16), OOS R2 -0.01%. Equations: eq. (1) "r_{ONFH,t} = P_{o+30,t} / P_{c,t-1} -
1" and eq. (2) "r_{ROD,t} = P_{c-30,t} / P_{c,t-1} - 1", P_c the close, P_o the open, t the day. The Table B3 row for
SM was read from a Firecrawl PDF-to-markdown conversion; the column alignment should be rechecked against the PDF
before any number is used in a decision (the table header has 11 numeric columns and the SM row has 11 values, so
the alignment is plausible).

Caveat for the lead (not a decision): Baltussen et al.'s SM sample ends 2020-05-01 and so includes most of the sealed
test window (2017-05-01..2020-11-30). Using its SM row to choose or drop a family lets published results from the
test period inform selection. The effect is small (3 of 38 years) but it is the lead's call.

Worked example on ZM scale (assumptions stated): suppose a first-half-hour slope of the Jin et al. size, beta =
0.052, applied to ZM. With sigma_30m = 3.15 x sqrt(30) = 3.15 x 5.477 = 17.3 ticks for the first half-hour, a
one-sigma first half-hour (17.3 ticks) predicts 0.052 x 17.3 = 0.90 ticks for the last half-hour. Check: R2 =
beta^2 x var(r1) / var(r13); with equal variances R2 = 0.052^2 = 0.27%, below the 0.90% reported, which says Dalian's
last half-hour is quieter than its first (var ratio 0.0027 / 0.0090 = 0.30). Either way, 0.9 ticks expected per
one-sigma day is below the 1.59-tick market-order break-even (Topstep row of reports/stage_e28_ranking.md), so even
the Dalian effect size does not pay at 1 lot on ZM unless conditioned on large first half-hours (a 3-sigma day
predicts 2.7 ticks).

### 5.4 What this means for family 3 (late-session momentum or reversal into the 13:15 settlement)

- The only direct CBOT soybean-meal test (Baltussen, 1982-2020) finds no first-half-hour momentum (slope negative,
  insignificant, OOS R2 negative), and the rest-of-day predictor is insignificant for SM. Gao et al. found no
  momentum in the two commodity futures they tested. The positive Dalian result is a different market, an older
  sample, and a day-only session. Prior for family 3 on ZM: weak. If kept, the predictor should be r_M (mid-day
  return), the one SM coefficient that is significant in-sample (t = 3.22), with the warning that its OOS R2 is
  negative.
- Settlement mechanics give a concrete hypothesis that is not the momentum one: TAS liquidity providers and index or
  hedge flows trade in the 13:14-13:15 window, and Globex trades on to 13:20. A 13:00-13:14 label would sit just
  before that flow; a 13:15-13:20 label would sit just after it. Onur and Reiffen's corn evidence says the electronic
  settlement removed the pre-close-to-next-open reversal, so a reversal into the next day is not expected.
- Exclusions: limit-locked closes (section 3), first notice and roll days, and report days whose 11:00 move is still
  settling (Huang: 35-45 minutes, so to about 11:45 in corn).

---

## 6. Planner pointers owned by R4: verification table

| # | Planner claim | Status | What the full text says (source, saved file) |
|---|---|---|---|
| 1 | Lehecka, Wang and Garcia (2014): price and volatility effect gone within minutes | PARTLY VERIFIED (abstract only) | IDEAS abstract: "market reactions persist for approximately ten minutes"; corn only; July 2009 - May 2012, i.e. releases in the trading HALT, reaction measured "immediately after the market opens" (R4_ideas_lehecka2014.html). Full text not obtained (publisher-restricted). Not a real-time-release study. |
| 2 | Adjemian and Irwin (AJAE 2018): effect gone within minutes | PARTLY VERIFIED (abstract only) | IDEAS abstract: "heightened volatility dissipates within the space of a few trading minutes"; 2009-2014 grain futures (R4_ideas_adjemian_irwin2018.html). The abstract speaks of volatility, not of the price level or direction. Full text not obtained. |
| 3 | Kauffman (2013): volatility elevated up to about 60 minutes | VERIFIED, with scope limits | "the higher volatility did not persist much beyond 60 minutes"; "excessive for 30 consecutive minutes"; 84% of the time in 30-60 min (R4_kauffman_nccc2013.txt). Corn only, 2012 only (7:30 CT releases). Consistent later evidence at 11:00 CT for corn AND soybeans: Bian, Serra and Garcia (2014-2017): volatility "would not settle down within the first hour"; Joseph and Garcia (soybeans): above control for 30-40 minutes, intermittently to about 60. Note the tension with rows 1-2 ("minutes"): the price level settles within minutes to tens of minutes, volatility within about an hour. |
| 4 | "11:00 CT releases have been made into live trading since 2012" | PARTLY VERIFIED | Live-trading releases since May 2012 at 7:30 CT; 11:00 CT since January 2013 (Huang 2022; Couleau et al. 2018; Joseph and Garcia 2016). |
| 5 | "The DIRECTION of the 15-90 minute path after the jump is untested" | PARTLY VERIFIED | No tradable-direction test found. Closest: Joseph and Garcia (soybeans, 29 trading-hour releases) test first-return vs later-return correlations over 15 minutes and find "difficult to establish a solid pattern" with mostly negative signs; Huang (corn) reports direction-conditional drift (ITR) to 60 minutes, positive for big events, negative after 40 min for small events. So the path is partly characterised, but not with an ex-ante direction signal and not beyond 60 minutes, and not for ZM or ZL. |
| 6 | farmdoc daily 2025-09-12 WASDE anecdote (pointer only) | VERIFIED as a pointer | Janzen, farmdoc daily 15:168, 2025-09-15: soybeans fell "as much as [...] 13 cents per bushel" in 11:00-11:15 and November soybeans closed "up 13 cents"; of 6 2025 report days, the author finds two other mismatches (June WASDE tiny moves; June Acreage soybeans) (R4_farmdocdaily_2025-09_wasde.html). Extension blog, 2025, outside all owned windows: pointer only. |
| 7 | Closing range 13:14-13:15 CT | VERIFIED (as the settlement window, CFTC-hosted filing) | "not impact or influence the 1:14-1:15 p.m. CT settlement window" (Submission 15-204, R4_cftc_cbot_2015_hours_1320.txt). The exact current algorithm within the window is [unverified]. |
| 8 | TAS since 2015-06-15 | PARTLY VERIFIED (date differs) | Rule 524 "effective on Sunday, June 7, 2015 for trade date Monday, June 8, 2015", covering "Corn, Soybean, Soybean Oil, Soybean Meal, Wheat and KC HRW Wheat" (Submission 15-148, R4_cftc_cbot_2015_tas_rule524.txt). No source read gives June 15; a later launch date for grains is possible but not seen. |
| 9 | Onur and Reiffen (CFTC 2018): pre-close to settlement reversals declined after 2012 electronic settlement | VERIFIED, with a correction of what is measured | Reversal = sign of (settlement - 5-minute pre-settlement VWAP) opposite to sign of (next-day open - settlement); "falls from 57.3% under the old regime to 48.7% under the new" (R4_onur_reiffen_cftc.txt). Corn only. It is a pre-close to NEXT-OPEN reversal, not a reversal into the settlement. |
| 10 | Gao, Han, Li and Zhou: US ETFs, R2 about 1.2-1.7% out of sample | PARTLY VERIFIED | SPY: in-sample R2 1.6%, OOS R2 1.2% (first half-hour alone), OOS 1.8% with the twelfth half-hour (R4_gao_han_li_zhou_mql5.txt, Dec 2015 draft). "1.7%" does not appear for SPY OOS; the range should read 1.2-1.8% OOS. Same paper: no intraday momentum in commodity futures (crude oil, gold). |
| 11 | Chinese commodities incl. Dalian soybean meal, t about 3.07 | PARTLY VERIFIED (paper found; 3.07 not found) | Paper: Jin, Kearney, Li and Yang, "Intraday Time-series Momentum: Evidence from China" (MPRA 97134, 2019; Hull repository lists a Journal of Futures Markets accepted manuscript, not read: Cloudflare and content-signal block). Dalian soybean meal, 2008-2013: first half-hour t = 2.60 (R2 0.90%), sign version t = 2.89, second-to-last half-hour t = 2.48, overnight return t = 2.96 alone and 3.05 joint. No 3.07 in the tables read; the published JFM version may differ. |
| 12 | Couleau, Serra and Garcia (NCCC-134 2018) | VERIFIED (what it is) | "Are corn futures prices getting 'Jumpy'?": corn nearby 2008-2015; real-time releases raised announcement-day jump frequency (100% of days, 83% with a cluster inside 2 minutes) and size (+4.1/-3.8 c/bu), while non-announcement jumps shrank (R4_couleau_serra_garcia_nccc2018.txt). |
| 13 | Li, Wang and Diersen (NCCC-134 2024): find what it is | FOUND | "Do Agricultural Commodity Price Spikes Always Stem from News?" (South Dakota State). Corn futures, 5-minute prices, 2013-2022, day session 8:30-13:20 only; 3,094 jump clusters on 2,403 days, "994 news-related clusters of jumps on 494 days, which occupy 32.13% of all clusters"; Hawkes fit: "exogenous events exhibit a faster decay in their relaxation exponent [...] in contrast to the more prolonged impact of endogenous events" (R4_li_wang_diersen_nccc2024.txt). Corn only; news matched by date, not time. Relevant to family 5 (non-news jumps), not to USDA paths. |
| 14 | Ranked family 2 (post-USDA path, 15-90 min) | SUPPORTED AS A GAP, WEAK PRIOR | Sections 2.4 and 7: about 49 major USDA days in 39 months; direction-known drift exists in corn after minute 10 for big events; no ex-ante test published; power only for mean effects of about 10 ticks or more. |
| 15 | Ranked family 3 (late-session momentum or reversal into settlement) | EVIDENCE AGAINST on CBOT soybean meal | Baltussen et al. (JFE 2021) Table B3, SM 1982-2020: first-half-hour slope -0.95 (t = -1.58), OOS R2 negative; rest-of-day slope insignificant; Gao et al.: no commodity momentum. The planner's "unpublished for ZM" is REFUTED: it was published (as a null) inside Baltussen et al.'s 60-futures panel. |
| 16 | Ranked family 4 (overnight-gap continuation or reversal at 08:30) | UNTESTED for CBOT; mixed indirect evidence | Dalian soybean meal overnight return predicts the last half-hour (t = 2.96); CBOT SM overnight-plus-first-half-hour does not (Baltussen). No study of the 08:30 or Sunday 19:00 opens found. |

---

## 7. Per-event-type table (the R4 deliverable)

Counts per year are calendar counts from the USDA, FAS and NOPA pages (section 1.2). "Window" counts are for the
39-month discovery window (x 39 / 12 = x 3.25). Tick conversions use the illustrative 400 USD/ton and are
assumptions, not data reads.

| Event | Schedule and time (CT) | Session it lands in | Per year (window) | Published jump evidence (horizon, size) | Published drift or reversal evidence | Implication for a ZM directional label |
|---|---|---|---|---|---|---|
| WASDE (+ Crop Production Aug-Nov, Jan) | monthly, pre-announced, 11:00 | day session (2 h 30 min after open, 2 h 14 min before settlement) | 12 (39) | corn: 40% of the 60-min move in minute 1, ~75% by minute 10, 90-100% by 35-45 min; complete move 1.63% average, 2.6% big, 0.6% small (Huang 2022). On ZM scale, 1.63% x 400 = 6.52 USD = 65 ticks [assumption that corn's % move transfers]. Soybeans: 15-s variance spike elevated 5-6 min, above control 30-40 min, to ~60 min (Joseph and Garcia 2016). Corn jumps: 100% of real-time report days, 83% clustered within 2 min (Couleau et al.) | direction-known drift after min 10: big +0.65% (~26 ticks), small -0.01% then -0.10% at 40-49 min (Huang, corn); soybeans: first-minute overreaction hint, no solid pattern (Joseph and Garcia); farmdoc 2025-09 full reversal [pointer] | Exclude minutes 0-5 (fast traders; E.31 passive fills -8.98 ticks). Candidate label: 15, 30, 60 min returns from an entry at 11:10-11:15, conditioned on the jump size P(11:05) - P(pre) scaled by pre-event sigma; expect continuation on big jumps and reversal on small ones; power only for |mean| >= ~10 ticks. |
| Grain Stocks | quarterly (Jan, end-Mar, end-Jun, end-Sep), 11:00 | day session | 4 (13), 3 of 4 stacked with WASDE, PP or Acreage | pooled into the "big" USDA events in Joseph and Garcia's soybean sample; WASDE-only days showed a lower first-interval spike (1.24 vs pooled 1.43 in the halt period; .47 vs .51 in the trading-hour period) | none separately | Treat as stacked days; only end-September is a clean Grain Stocks event (about 3 in the window). No separate family. |
| Prospective Plantings | annual, end of March, 11:00 (with Grain Stocks) | day session | 1 (3) | in pooled samples only | none | Too few for its own label; include as a "major USDA day" in family 2 and as a stratum. |
| Acreage | annual, end of June, 11:00 (with Grain Stocks) | day session | 1 (3) | in pooled samples; June Acreage 2025 soybeans: fell "more than a dime" immediately, up slightly on the day [pointer] | pointer only | As above; limit-move risk highest on this day (section 3). |
| NOPA crush | monthly (date set by NOPA), 12:00 noon ET = 11:00 | day session | 12 (39) | NONE found: no intraday study of NOPA releases in any source read | none | Directly relevant to ZM (meal production, exports, crush pace) and the one ZM-specific scheduled event. Unstudied: a genuine gap. Separate stratum in family 2, with the warning that release dates and the 11:00 time before 2026 are [unverified] and must be fixed from a dated source before E.33. |
| Crop Progress | weekly Monday (Apr-Nov), 16:00 ET = 15:00 if ET [zone unverified] | CLOSED (13:20-19:00); priced at the 19:00 Monday open | about 30-35 (about 100) | none found (discovery null, section 4.2) | none found | Feature for family 4 (Monday-evening open gap) and a growing-season stratum; no label of its own. |
| Export Sales (weekly) | Thursday 8:30 ET = 07:30 | OVERNIGHT session, 15 min before the 07:45 pause | about 52 (about 169) | none found | none found | Thin overnight book (ZM day-session volume share 0.83); the move is carried into the 08:30 open. Thursday flag for family 4. |
| Daily (flash) export sales | ad hoc, 9:00 a.m. (zone not stated; 08:00 CT if ET) | PAUSE 07:45-08:30 [if ET] | irregular | none found | none found | Flag only. |
| Weekend weather / Sunday open | Sunday 19:00 open after a 53 h 40 min gap | overnight open | about 52 (about 169) | none found (practitioner commentary only) | Dalian SM overnight-return continuation into the last half-hour (t 2.96, different market, no night session); CBOT SM overnight+first half-hour: no prediction (Baltussen) | Family 4 stratum. Growing season separately. Weak prior. |
| Daily settlement | 13:14-13:15 window; Globex to 13:20; TAS at settlement +- 4 ticks | day session close | about 250 (about 819) | n/a | corn: pre-settlement-to-next-open reversals 48.7% after 2012 (no reversal) (Onur and Reiffen); CBOT SM first-half-hour -> last half-hour slope -0.95 (t -1.58), OOS R2 < 0 (Baltussen) | Family 3 prior is weak and partly REFUTED for SM. If kept: predictor r_M (mid-day, SM t 3.22 in-sample, OOS negative); separate 13:00-13:14 and 13:15-13:20 labels around the TAS-driven settlement minute. |
| Limit days | limits reset May 1 and Nov 1 (7% of 45-day average, nearest 5 USD, min 20 USD; expanded x 1.5); soybean-complex linked | any | rare (no count read; DataFacts item) | n/a | n/a | Censor labels that cross a limit-locked interval; flag expanded-limit days, which follow limit settlements in ZS or ZL too. |

---

## 8. Summary of what this means for a ZM directional search

Mechanisms worth testing:
1. Post-USDA path (family 2), entry 10-15 minutes after 11:00, with the sign of the early move and its size as
   conditioners. Big events: continuation is plausible (Huang, corn, direction-known drift +0.65% after minute 10).
   Small events: overshoot then correction (Huang; Joseph and Garcia). About 49 major USDA days plus 39 NOPA days in
   the window. Power suffices only for mean effects around 10 ticks or more.
2. NOPA crush days as a ZM-specific event stratum: no published intraday study exists in the sources read.

Mechanisms to drop or demote:
1. Minutes 0-5 after any release (fast traders; E.31).
2. Late-session momentum from the first half-hour (family 3) as a standalone family: the CBOT soybean-meal null in
   Baltussen et al. (1982-2020) and the commodity null in Gao et al. If kept, use r_M and treat it as low prior.
3. Pre-close-to-next-open reversal: corn evidence says it disappeared after 2012.

Open items that need dated, non-CME sources before E.33 freezes anything: the NOPA release calendar and time for
2020-2024; the Crop Progress time zone; the current settlement algorithm inside 13:14-13:15; the TAS start date for
grains (June 8 vs June 15, 2015); ZM limit levels and limit-day counts in 2020-12..2024-02 (DataFacts can count these
from definitions and settlements).

---

## 9. Discovery and fetch log summary

- Pages saved and logged: see pages/R4_events/log.tsv (49+ entries). Failures: Cao and Robe (JFM 2022, Wiley
  pdfdirect: Cloudflare page, not read), Kansas City Fed Economic Review 2013 (two URLs, no file; the NCCC-134
  version was used), USDA node 13204 (Access Denied), FAS export-sales HTML pages (empty responses; the FAS fact sheet
  PDF was used), Hull repository Jin et al. AAM (Cloudflare; robots.txt carries content signals; not retried),
  Baltussen et al. EUR PDF by curl and by Scrapling get and fetch (Cloudflare 403; stealthy-fetch NOT used because it
  would defeat a bot check), then read through Firecrawl (route 4), logged. ScienceDirect HTML for Baltussen et al.
  carried no article text.
- WebSearch calls in the resumed run: 7 (this worker's budget is 80; the first spawn's count is not in the log).
  Crossref API: 3 title queries. No budget notice was seen. One WebSearch for an author or AgEconSearch copy of
  Adjemian and Irwin (2018) found none (it surfaced Shubitidze et al. 2026 instead).
- Stopping rule, topic b: seven full-text sources read (Huang, Joseph and Garcia, Kauffman, Couleau et al., Bian et
  al., Hu and Mallory NCCC version, Li et al.); the last searches added Bian et al. and Hu and Mallory, so the topic
  was not saturated at the stop; a further sweep (Google Scholar citations of Adjemian and Irwin 2018) is the next
  step if the lead wants more.
- Not done: full texts of Lehecka et al. (2014) and Adjemian and Irwin (2018) (publisher-restricted; no author copy
  found in the queries run); the published JFM version of Jin et al.; any Google Scholar sweep for soybean meal or
  soybean oil USDA intraday studies beyond the queries above.
