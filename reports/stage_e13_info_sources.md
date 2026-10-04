# Stage E.13 Task 3: new information sources for intraday signals (InfoSource-OpusHigh)

Worker: InfoSource-OpusHigh (opus, high). Written 2026-10-03. Research and scoping only: no market data
of this program was read, no Databento call, no account, no key. Evidence pages and the fetch log are in
reports/stage_e13_briefs/pages/InfoSource/ (fetch_log.md; restricted pages listed in DO_NOT_COMMIT.txt).
Source keys: I-xx are pages fetched in this task (section 4); P-xx are this program's own records (section 4b).

Path note for the lead: the brief points to docs/stage_e0_catalog_K1.md ... K8.md; the catalogs are in
reports/ (reports/stage_e0_catalog_K1.md ... K8.md). They were read there.

Times: release and decision times are CT (the program's clock); the CT figure is the ET figure minus one
hour, which holds all year because both zones change clocks together (P-06).

---

## 1. Summary table

Verdicts are given separately for evidence (E) and fit (F): strong / moderate / weak / none.

| # | Candidate | Measures | Available at (CT) | Source and cost | History | Evidence (post-publication) | Used by program | Fit | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | CFTC COT (legacy, disaggregated, TFF) | Tuesday positions by trader class | Fri 14:30 (data as of Tue) | CFTC, free, public domain (I-01, I-04b) | legacy 1986; disaggregated and TFF 2006 (I-05) | Weekly only; little or no forecasting power for futures (I-06c 1995-2006; I-08 1993-2006); hedging pressure priced at weekly-plus horizons (I-09, abstract) | Never with content; K3-cot-01 excluded X-16 (P-03) | Arrives after Friday's last decision; weekly signal; no intraday record | E: weak (daily: none) / F: none |
| 2a | EIA natural gas storage surprise vs consensus | Storage change minus analyst median | Thu 09:30 | EIA free (I-10, I-12); consensus Bloomberg/WSJ, proprietary (I-19, I-21b) | EIA weekly; Bloomberg survey from about 2003 (I-21b) | Contemporaneous response strong; no tradable post-release drift (P-01 X-02); announcement-day premium decayed after 2011 and absent 2014-2018 (I-21b) | Day flag and the (-90, +30) window as K4-ngpre-01; reversal K4-ngrev-01 (excluded R-06); surprise excluded X-01, X-02, X-03 (P-01) | Release before energy t2 10:30; 52 a year | E: weak / F: moderate |
| 2b | EIA WPSR crude and product surprise | Inventory change minus consensus | Wed 09:30 (tables 1-14) | EIA free (I-11); consensus Bloomberg or WSJ, proprietary (I-19) | EIA weekly; consensus history proprietary | Contemporaneous response and pre-release anticipation (I-19, 2018); post-release continuation not documented (P-01 X-02) | WPSR post-release move, WPSR-day return, K4-eiafade-01, K4-eiamom-01 (P-01, P-02) | Before energy t2; 52 a year | E: weak / F: moderate |
| 2c | API Weekly Statistical Bulletin | Industry inventory survey | Tue about 15:30 | Paid, via LSEG or ICE only (I-14b) | UNSOURCED | Program record only (K4-apipre-01) | K4-apipre-01 uses the price response (P-01) | After Tuesday's last decision; content paid | E: weak / F: weak |
| 3 | Weather forecast revisions (GFS/GEFS, CPC 6-10/8-14) | Gas-weighted HDD/CDD forecast changes | GFS 12Z out about 10:30-12:15 CDT; 00Z overnight; CPC 6-10 issued 14:00-15:00 CDT (I-26, I-31) | NOAA free, public domain (I-28); ECMWF paid (UNSOURCED) | NCEI GFS 0.25 deg forecasts listed from 2021-02-26 (I-30); longer forecast archive UNSOURCED here | One finance paper: cold GEFS forecasts precede a 5-day NG1/NG2 spread premium, 1990-2019, daily (P-05; published 2025, no post-publication record); realized temperature is contemporaneous only (I-25) | Never; K4-ngwx-01 excluded X-13, K9M-017 excluded (P-01, P-04) | 12Z run lands before energy t3 13:00; daily in heating and cooling seasons | E: weak / F: moderate (NG); weak (grains) |
| 4 | USDA report surprises (WASDE, Crop Progress, Grain Stocks, Plantings, Acreage, Hogs and Pigs, Cattle on Feed) | Report minus trade estimate | WASDE, Grain Stocks, Plantings, Acreage 11:00; Crop Progress Mon 15:00; livestock 14:00 (P-02, P-06) | USDA free; trade estimates from Dow Jones/Reuters/private analysts, proprietary (I-35) | Reports decades; expectations 1984+ in the papers, proprietary | Strong same-day price impact, 1985-2018 (I-34, I-35), impact grew after 2007 for some reports (I-35); no tradable post-release drift within the day documented; Crop Progress next-day null (P-02 X-07) | WASDE pre-drift, usda_resp, cp_ge_chg; surprise excluded X-04, X-05, livestock X-08 (P-02) | 11:00 release = last grain decision; others after the close: next day only | E: weak (for the tradable window) / F: weak |
| 5 | Implied-volatility indices (VIX, VIX9D, VIX3M, VXN, OVX, GVZ, VVIX; CME CVOL) | 30-day (or 9-day, 3-month) implied vol | Prior close known before t1; intraday values real time but intraday history not free (P-04 Q18) | Cboe daily CSVs free for personal non-commercial use (I-42, I-45); CVOL via CME, which bars automated access (research rules) | VIX from 1990 (I-42); OVX, GVZ CSVs listed (I-42) | Volatility forecasting, not direction (S22, S23 found only vol results); VIX-slope result is for variance assets (search snippet only, UNSOURCED); no intraday direction evidence retrieved | VXN with content (K1-vxnband-01, P-07); VIX drafts withdrawn, VIX backwardation routed to ML v2 but not in V2.3 (P-04) | Known before t1; useful as a conditioning or sizing variable | E: weak / F: moderate |
| 6 | Economic-surprise indices (Citi ESI, Scotti, free rebuild) | Aggregate actual-minus-consensus macro surprises | After each release | Citi/Bloomberg proprietary; Scotti index built on Bloomberg expectations (I-50) | Bloomberg expectations from 2003 (I-50) | Practitioner blogs only, multi-week to one-year horizons (S25); individual-release responses contemporaneous (P-01, P-03) | Never; per-release surprise excluded under rule 3 in K1 X-18, K2 X-08, K3 X-05, K5 X-03 | No free consensus history; no intraday record | E: none / F: weak |
| 7 | Options positioning: put/call, SKEW, dealer gamma (GEX/NGE) | Option volume and open-interest positioning | Prior-day GEX known before t1 (CSV daily) | SqueezeMetrics DIX/GEX CSV free (I-40; header verified, starts 2011-05-02, I-47); put/call and SKEW from Cboe (terms I-45) | GEX 2011+ (I-47); NGE from OptionMetrics 1996-2017 (I-37b, paid) | Gamma: intraday momentum present when NGE negative and stronger as it becomes more negative, 1974-2020, no costs (I-37b); intraday momentum predictability declined after 2013 (Rosa 2022, cited in I-39). Public put/call: predictability from non-public volume (I-51). SKEW: up to one-year tail risk (I-52) | Never for gamma, put/call or SKEW. Unconditional intraday momentum is used: CP1 port in K1-K7 and D.1 F3.3 null on MES 2020-02..2024-02 (P-07, P-08) | Gamma: known before t1; late-session hold; about 250 days a year | E: moderate (gamma) / weak (put/call, SKEW); F: moderate (gamma) |
| 8a | Treasury auction results (tail, bid-to-cover, indirect share) | Auction demand vs when-issued yield | Coupon auctions close 12:00; results timestamp UNSOURCED (P-03 X-07) | FiscalData free (P-03); when-issued yield proprietary (I-53) | Decades (UNSOURCED start) | Tail defined and used as a demand-shock gauge (I-53); no intraday post-result drift found (S29-S31) | Calendar flags K2-aucpre-01 and K2-aucpost-01; bid-to-cover excluded X-07 (P-03) | Results before rates t3 12:50; about 7 coupon auctions a month (UNSOURCED count) | E: none / F: moderate |
| 8b | Fed communications text (statements, minutes, speeches) | Text tone or policy surprise | Statement and minutes 13:00 | Fed free | Statements since 1994 (UNSOURCED) | Speeches: no significant equity effect on average (I-54); FOMC pre-to-post reversal, 1997-2020, unpublished thesis (I-56b) | FOMC flags K2, K5, K9; K5-fomc-01 excluded (13:05 is after metals' t3) | 13:00 is after every t3 except equity's 13:00 bar close | E: weak / F: weak |
| 8c | News sentiment | — | — | — | — | Note only: the sibling AiTrader project tests news judgment; not researched (brief) | — | — | not assessed |
| 8d | Order flow from one-minute OHLCV | Volume imbalance proxies | — | — | — | Note only (brief); the K9 catalog records that the bars lack signed volume (P-04) | G10 log volume ratio | — | not assessed |

---

## 2. Per-candidate blocks

### 2.1 CFTC Commitments of Traders (legacy, disaggregated, TFF)
- **Measures:** open interest held by commercial, non-commercial and non-reportable traders (legacy), and by
  producer, swap dealer, managed money and other reportables (disaggregated), or dealer, asset manager,
  leveraged funds (TFF).
- **Release and availability:** "generally published each Friday at 3:30 pm Eastern Time (US), using the data
  from the immediately preceding Tuesday" (I-01), that is Friday 14:30 CT, a three-day lag on Tuesday's
  positions. Holidays move it (I-02).
- **Source, cost, terms:** CFTC website, free. "Government information at the CFTC website is in the public
  domain" (I-04b). The site's robots.txt sets Content-Signal "ai-train=no" and disallows ClaudeBot and
  Claude-Web as training crawlers (I-03b); this task used plain single-page fetches only and lists the CFTC
  files in DO_NOT_COMMIT.txt as a precaution. Files are text and Excel by year (I-05).
- **History:** "Commitments of Traders Futures Only reports file from 1986" (I-05); disaggregated and TFF
  files from 2006 ("2006-2016", I-05). No consensus series is needed (positions are the data).
- **Evidence:**
  - Sanders, Irwin and Merrin (2009), 10 grain and livestock futures, weekly, "1995 through 2006": "very
    little evidence that traders' positions are useful in forecasting (leading) returns" (I-06c).
  - Bank of England Quarterly Bulletin (2006), currencies, oil, rates, equities, January 1993 to January
    2006: "There is little evidence that changes in non-commercial positions have significant predictive
    power regarding asset prices" (I-08).
  - Kang, Rouwenhorst and Tang (JF 2020), abstract only (OpenAlex record): "Short-term position changes are
    driven mainly by the liquidity demands of noncommercial traders ... These two components influence
    expected futures returns with opposite signs" (I-09). Horizon is weekly and longer; the full text
    was not retrieved (Wiley; SSRN blocks).
  - Later evidence found (S36): managed-money positions predict commodity producers' stock returns in the
    next week (search result only, not retrieved; not futures).
  - No study of an intraday or one-day futures response to the Friday release was found (S01, S04).
  - Evidence is weekly only, and the weekly record is mostly null for futures.
- **Used by program:** never with content. K3-cot-01 was excluded: "Weekly signals and multi-week
  horizons" (P-03, K3 X-16).
- **Fit:** the release (Friday 14:30 CT) falls after Friday's last decision time for every group, so the
  earliest use is Monday t1. A weekly signal held for at most one session: 52 events a year. At a per-event
  Sharpe of 0.1, t = 3 needs 9 / (0.01 x 52) = 17 years. The literature gives no per-event figure to plug in.
- **Verdict:** evidence weak (weekly), none for intraday; fit none.

### 2.2 EIA weekly storage and inventory reports, and the API bulletin

**(a) Natural gas storage surprise against consensus**
- **Measures:** the weekly working-gas storage change minus the analysts' median forecast.
- **Release:** "10:30 a.m. eastern time on Thursdays", with holiday exceptions (I-10): Thursday 09:30 CT.
- **Source, cost, terms:** EIA, free. "U.S. government publications are in the public domain and are not
  subject to copyright protection" (I-12).
- **Consensus:** proprietary. Prokopczuk, Simen and Wichmann use "the Bloomberg median survey forecast"
  (I-21b). Search S08 found news-article polls (WSJ, S&P Global, NGI) but no free downloadable history; the
  program's K4 reader reached the same conclusion: "Consensus surveys (Bloomberg, Reuters) are proprietary,
  with no named obtainable history" (P-01, X-02).
- **History:** sample March 2003 to December 2018 in I-21b; "The start of the sample is motivated by the
  inception of the Bloomberg forecast for the EIA report" (I-21b).
- **Evidence:**
  - The response to the surprise is contemporaneous. For gas the program's K4 record quotes "No evidence ...
    of economically meaningful reactions to the surprise other than on the date the storage news is
    released" (P-01, P-K4-028-b).
  - The announcement-day puzzle (Prokopczuk et al., Energy Journal 2021): "More than 50% of the annual return
    is earned on these days ... which cannot be explained by the announcement surprise" (I-16b abstract).
    The short (-90, +30) strategy: whole sample "12.01% with a Sharpe ratio of 1.76" after costs, but "In
    the more recent period, this has declined to only 3% and a Sharpe ratio of 0.5, which do not withstand
    transaction and funding costs" (I-21b), and "the effect is not present in the most recent period
    (2014–2018)" (I-21b). The record after the paper's own split is negative.
  - No later replication was found (S10, S12).
- **Used by program:** the day flag and the (-90, +30) window are K4-ngpre-01 (P-01, source K4-001 = this
  paper); the week-to-week reversal K4-ngrev-01 (excluded on review R-06); the surprise, the accurate-analyst
  predictor and the disagreement versions are excluded X-01, X-02, X-03 under rule 3 (P-01). Only the
  consensus content is new, and it is not obtainable free.
- **Fit:** 09:30 CT release, before energy t2 (10:30) and t3 (13:00); a post-release hold of 60 minutes or
  more fits. 52 events a year: per-event Sharpe 0.1 needs 17 years for t = 3; 0.2 needs 4.3 years.
- **Verdict:** evidence weak (contemporaneous only; the day premium decayed); fit moderate, blocked by data.

**(b) WPSR crude and product inventory surprise**
- **Release:** "Tables 1-14 in CSV and XLS formats, are released to the web site after 10:30 a.m. eastern
  time on Wednesday" (I-11): Wednesday 09:30 CT.
- **Consensus:** Miao et al. (JFM 2018): "Consensus forecasts of the inventories in the weekly storage report
  are obtained from Bloomberg's survey of analysts" (I-19); the paper's example cites a WSJ survey. No free
  history found.
- **Evidence:** "a strong announcement day effect ... prices to move in anticipation of the inventory
  surprise. Futures returns significantly decrease with positive surprises and increase with negative
  surprises" (I-19). This is a same-day response plus anticipation; no post-release continuation over an
  hour or more is documented (S09, S11; P-01 X-02 "what is documented is contemporaneous").
- **Used by program:** WPSR post-release move and WPSR-day return (V2.3 K4 features), K4-eiafade-01,
  K4-eiamom-01 (P-01, P-02 design list). The surprise is excluded X-02.
- **Fit and verdict:** same timing class as (a), 52 a year. Evidence weak; fit moderate, blocked by data.

**(c) API Weekly Statistical Bulletin**
- **Release:** "every Tuesday afternoon at approximately 4:30 pm Eastern" (I-14b): about 15:30 CT, after
  every Tuesday decision time.
- **Cost:** paid: "Contact one of the two certified distributors below to purchase access to the WSB LSEG
  Data & Analytics ... " and ICE (I-14b). Price UNSOURCED (not shown on the page).
- **Used by program:** K4-apipre-01 trades the API-to-EIA price continuation from bars only (P-01).
- **Verdict:** evidence weak; fit weak (next day only; EIA supersedes it on Wednesday morning).

### 2.3 Weather forecast revisions
- **Measures:** changes between successive model runs in population- or gas-weighted heating and cooling
  degree days (NG), and in precipitation and temperature over the Corn Belt (grains).
- **Release and availability:**
  - NOAA CPC 6-10 and 8-14 day outlooks: "issued daily between 3pm & 4pm Eastern Time" (I-26), that is
    14:00-15:00 CT, after the last decision; the 2026-10-03 discussion is stamped "300 PM EDT" (I-27).
  - GFS: four cycles a day, "4/day: 00, 06, 12, 18UTC" (I-30). On NCEP's production status page the 12 UTC
    "FORECAST F000-F384" step runs "15:29:20 17:13:54" (I-31), times taken as UTC (inferred from the cycle
    labels): the 16-day forecast is complete by about 12:15 CDT (11:15 CST), before energy t3 (13:00). The
    00 UTC run completes overnight, before t1.
- **Source, cost, terms:** NOAA/NWS, free: "in the public domain, unless specifically noted otherwise, and
  may be used without charge for any lawful purpose" (I-28). ECMWF (the market's other reference model) is
  licensed; its cost and terms are UNSOURCED here.
- **History:** NCEI lists GFS 0.25 and 0.5 degree forecasts "26Feb2021-Present" and GFS analysis from
  "01Jan2007" (I-30); analysis is not forecast, so a forecast-vintage history before 2021 is UNSOURCED in
  this task. The one finance paper used NOAA GEFS forecasts with a "forecast dataset from 1 January 1987"
  (P-05, the E.10 log's summary; the archive used is not named there). The CPC archive page returned 403
  (I-29).
- **Evidence:**
  - Monteux, Arcuri, Gandolfi, Caselli (North American Journal of Economics and Finance 2025): NG1 returns
    "are linearly dependent on 1-week ahead U.S. forecasted temperatures, but they do not appear to be
    dependent on U.S. realized temperatures levels" (P-05, P-K9M-017-g). The tradable form is a
    long NG1 / short NG2 spread "held for a period of 5 business days" after a bottom-decile cold forecast,
    daily settlement data 1990-2019 (P-05). Costs were not found in E.10's grepped lines. Published 2025:
    no post-publication record yet.
  - Hartley and Lan (JFM 2023) model daily NG price changes on realized hourly temperatures (I-25,
    abstract): contemporaneous, not forecast revisions.
  - Intraday response to model runs: news reports only (S13, S14); no academic study found.
  - Grains: no academic study of a price response to forecast updates found (S16); practitioner and news
    pages only.
- **Used by program:** never. K4-ngwx-01 excluded X-13 ("Model-update times and an obtainable record of
  historical forecast vintages are [unverified]"; P-01), and K9's "NG long after an extreme cold forecast"
  excluded as "a 5-day NG1/NG2 spread, not an outright session hold. Needs NOAA GEFS forecast history"
  (P-04). The E.0 K4 reader's dedicated weather search did not complete (P-01, line 1074).
- **Fit:** NG only. The 00Z revision is known before t1 (08:30 CT) and the 12Z revision before t3 (13:00 CT);
  holds to F (15:08) fit. Events: every trade date in the heating and cooling seasons, about 150 to 250 a
  year (UNSOURCED count; depends on the season definition); an extreme-revision subset is smaller. At 150
  events and a per-event Sharpe of 0.1, t = 3 needs 9 / (0.01 x 150) = 6 years; at 0.05, 24 years.
- **Verdict:** evidence weak (one daily, spread-based, 2025 paper; no intraday or post-publication
  record); fit moderate for NG, weak for grains.

### 2.4 USDA report surprises
- **Release times:** WASDE, Crop Production, Grain Stocks, Prospective Plantings and Acreage at "11:00 a.m.
  CT (12:00 p.m. ET)" since January 2013; Crop Progress Mondays "3:00 p.m. CT (4:00 p.m. ET) ... April
  through November"; Cattle on Feed, Hogs and Pigs and Cold Storage at 14:00 CT (P-02, verified by the K6
  reader from USDA and NASS pages).
- **Source and expectations:** reports free (USDA/NASS). Expectations are proprietary polls: "expectations
  ... are obtained from Knight Ridder/Dow Jones through 2015; 2016 expectations are from Thomson Reuters.
  Private analysts' estimates for corn and soybean Crop Production reports use an average of forecasts by
  Conrad Leslie and Informa Economics" (I-35).
- **History:** "1984/85–2016/17 marketing years for corn and soybeans" (I-35); 1985-2018 in I-34.
- **Evidence:**
  - Karali et al. (Food Policy 2019): own-surprise impact of Prospective Plantings "has increased almost
    two-fold in corn and soybeans" after 2007 (I-35); measured on close-to-close returns, a same-day
    response.
  - Isengildina-Massa et al. (J. Commodity Markets 2020): market reactions "over 1985 through 2018" (I-34),
    same-day.
  - Intraday: Lehecka, Wang and Garcia (AEPP 2014) "Gone in Ten Minutes" (title via OpenAlex; full text not
    retrieved); the program's K6 record: WASDE's post-release move is known at 11:15 CT (P-02).
  - No tradable post-release drift within the session, and no after-cost strategy, was found (S17, S19;
    the one strategy result found assumes advance access to the report, which is look-ahead).
  - Crop Progress next session: "Significant results could not be found for the open-to-close return"
    (P-02, X-07).
- **Used by program:** heavily: K6-wasdepre-01, usda_resp, cp_ge_chg and the EC-USDA calendar; the surprise
  versions are excluded X-04, X-05 (rule 3), livestock X-08 (P-02).
- **Fit:** the 11:00 CT releases coincide with the last grain decision time (11:00), so the content can only
  be used the next day; Crop Progress and livestock reports come after the close. Events: WASDE 12 a year,
  Grain Stocks 4, Hogs and Pigs 4, Cattle on Feed 12. At 12 events and a per-event Sharpe of 0.3, t = 3 needs
  9 / (0.09 x 12) = 8 years.
- **Verdict:** evidence weak for any window this program can trade; fit weak.

### 2.5 Implied-volatility indices
- **Measures:** VIX (30-day S&P 500 implied vol), VIX9D, VIX3M (term structure), VXN (Nasdaq-100), OVX
  (crude via USO options), GVZ (gold), VVIX; CME CVOL for futures options.
- **Availability:** daily closes known before the next session's t1. Intraday values are disseminated in
  real time, but a free intraday history is [unverified] (P-04, routed item Q18).
- **Source, cost, terms:** Cboe publishes "VIX Index data for 1990 to present (Updated Daily)" (I-42) and
  daily CSVs including GVZ_History.csv, OVX_History.csv, VIX9D_History.csv, VVIX_History.csv (I-42 links).
  Cboe's terms: "You may view, print and download one copy of the Materials for your personal non-commercial
  use" (I-45). CME CVOL: cmegroup.com forbids automated access (research rules, E.12 case); not fetched;
  history and cost UNSOURCED.
- **Evidence:**
  - Direction: no study retrieved shows that an implied-vol index or its change predicts the direction of
    the program's futures over the next hour to session (S20, S22, S23). Results found concern
    volatility forecasting (OVX for oil volatility) or variance-asset returns (VIX slope, Johnson JFQA 2017,
    search snippet only: UNSOURCED).
  - Conditioning: market intraday momentum is "stronger on high-volatility days" per a search summary of
    Gao, Han, Li, Zhou (JFE 2018) (S21 snippet; full text not retrieved: UNSOURCED).
  - The program's K9 round examined two VIX members and withdrew both: VIX backwardation (shape and
    horizon) and the VIX spike (fails the X10 test) (P-04).
- **Used by program:** VXN prior close with content (K1-vxnband-01: regime and band breach; coded in E.11,
  P-07). VIX: withdrawn drafts; K9-vixback-01 routed to ML v2 as a candidate feature but absent from the V2.3
  list (P-04, P-02 design). OVX, GVZ, VIX3M, VVIX, CVOL: never.
- **Fit:** good timing (prior close before t1), daily, every product group has a matching index (VIX/VXN
  for K1; OVX for CL; GVZ for gold). But it is a state variable, not an event: about 250 rows a year per
  product, and its use would be as a conditioning or sizing input to some other signal.
- **Verdict:** evidence weak (for direction); fit moderate.

### 2.6 Economic-surprise indices
- **Measures:** a running aggregate of actual-minus-consensus macro surprises (Citi ESI; Scotti's index).
- **Source:** Citi ESI is distributed through Bloomberg (proprietary; cost UNSOURCED). Scotti (Fed IFDP 1093,
  revised 2016) builds hers from Bloomberg expectations: "Expectation data are available from Bloomberg for
  all countries since 2003" (I-50). Whether the Fed posts the index series was not found (S24).
- **Free reconstruction:** needs a free consensus history for each release; none was found in this task or
  in the program's catalogs (the rule-3 exclusions K1 X-18, K2 X-08, K3 X-05, K5 X-03 all rest on that).
- **Evidence:** practitioner blogs describing multi-week to one-year horizons (S25); no academic intraday or
  one-day test found (S25, OpenAlex queries). Per-release responses are contemporaneous (P-01, P-03).
- **Used by program:** never; the K9 announcement-day flag uses the release calendar only (P-02 design).
- **Verdict:** evidence none; fit weak (no data).

### 2.7 Options-market positioning
**(a) Dealer gamma exposure (NGE / GEX)**
- **Measures:** the dollar gamma that option market makers must hedge, estimated from S&P 500 index option
  open interest under assumptions about who is short.
- **Source and data:** Baltussen, Da, Lammers and Martens built it "based on all the open interest in S&P 500
  index options using OptionMetrics data ... from 1996 until the end of 2017. We use data from SqueezeMetrics
  to extend the sample until May 2020" (I-37b). SqueezeMetrics publishes a daily CSV of date, price, DIX and
  GEX starting 2011-05-02 (I-47, header rows only; file not saved). Its page defines "Gamma Exposure (GEX)
  is a dollar-denominated measure of option market-makers' hedging obligations" (I-40). Its platform terms
  bar "creating user accounts by automated means" (I-48); no clause on the public CSV was found. OptionMetrics
  is paid (cost UNSOURCED). The CSV covers S&P only; no free Nasdaq-100 or Russell gamma series was found.
- **Availability:** the prior day's GEX is known before t1; its intraday update is not free (UNSOURCED).
- **Evidence:**
  - Baltussen et al. (JFE 2021), 60+ futures, "December 1974 to May 2020": the last half-hour return is
    predicted by the rest-of-day return in every asset class, with timing-strategy "Sharpe ratios between
    0.87 and 1.73 at the asset class level"; for the S&P, "market intraday momentum is present for the index
    when NGE is negative and becomes stronger when NGE becomes more negative" (I-37b). Costs: "Note that we
    do not consider transaction costs", though in S&P futures a one-tick cost still leaves "a positive net
    Sharpe ratio" (I-37b).
  - After publication: Zarattini, Aziz and Barbon (2024 working paper) report that "Rosa [7] analyzes
    additional data post2013, noting a decline in predictability" (I-39), citing Rosa, "Understanding
    intraday momentum strategies", Journal of Futures Markets (I-39 reference list). Rosa's paper itself was
    not retrieved. The 0DTE options boom since 2022 changes dealer gamma; no academic test of the gamma
    conditioning after 2020 was retrieved (S28, S37).
- **Used by program:** gamma never. The unconditional effect is used: the CP1 port is "the
  Gao-Han-Li-Zhou / Baltussen form" ported to K1-K7 (P-07), and D.1's F3.3 (the 08:30-09:00 and first-bar-to-09:00
  forms against 14:30-15:00) belongs to "MES classes C1-C5 and C7 null on 2020-02-03..2024-02-29" (P-07,
  P-08). The rest-of-day form (open to 14:30) and its gamma conditioning were not screened. The E.0 K1 log
  rejected a 2026 paper on free GEX reconstruction for S&P and gold as off-product (P-09).
- **Fit:** gamma is known before t1. The documented hold is the last 30 minutes (14:30-15:00 CT), below
  the 60-minute floor of ML route v2; a 14:00 CT decision held to F (15:08, 68 minutes) fits the floor but
  is not the paper's window. About 250 trade dates a year; a negative-gamma subset is smaller (share
  UNSOURCED). Converting the paper's 0.87-1.73 annual Sharpe at 252 days: per-day 0.055-0.11; t = 3 needs
  (3 / SR)^2 = 3.0 to 11.9 years before costs and before any post-2013 decline.
- **Verdict:** evidence moderate (peer-reviewed, 45 years, intraday, on-instrument; decline reported after
  2013; costs not tested for micros); fit moderate.

**(b) Put/call ratios**
- **Evidence:** Pan and Poteshman (NBER w10925): stock-level next-day predictability, but "the economic
  source of this predictability is non-public information possessed by option traders rather than market
  inefficiency" (I-51); the volume "initiated by buyers to open new positions – is not publicly observable"
  (I-51). Index put/call evidence found is practitioner-level and mostly null (S26 search summary only).
- **Source:** Cboe daily market statistics; Cboe's robots.txt disallows "/*market_statistics/volume_reports/"
  (I-43), so history files were not fetched; their availability is UNSOURCED.
- **Used by program:** never. **Verdict:** evidence weak; fit weak.

**(c) CBOE SKEW**
- **Evidence:** Bevilacqua and Tunaru (J. Financial Stability 2021): the negative-SKEW component "is found to
  be able to predict recessions, market downturns, and uncertainty indicators up to one year in advance"
  (I-52). Horizon months to a year.
- **Used by program:** never. **Verdict:** evidence weak (no intraday or one-day record); fit weak.

### 2.8 Others
**(a) Treasury auction results**
- **Measures:** the tail, "the highest yield accepted at auction less the security's when-issued yield
  immediately before the auction's conclusion" (I-53); bid-to-cover; bidder shares.
- **Availability and source:** coupon auctions close 13:00 ET (12:00 CT; the program's K2 calendar), before
  rates t3 (12:50 CT is the last decision; results published at about 12:00 CT would be in time). The program
  found "No confirmed source gives a per-auction results publication time (FiscalData carries results with
  no release timestamp)" (P-03, X-07). The when-issued yield needed for the tail is a dealer quote,
  proprietary (cost UNSOURCED).
- **Evidence:** none for intraday or next-hours drift after results (S29, S30, S31: news reports only). The
  Dallas Fed note defines the tail as a gauge of "unanticipated shifts in demand" (I-53).
- **Used by program:** auction pre and post flags (K2-aucpre-01, K2-aucpost-01) with calendar content;
  bid-to-cover excluded X-07 (P-03).
- **Verdict:** evidence none; fit moderate (timing works on rates if a timestamp is sourced).

**(b) Fed communications text**
- **Timing:** FOMC statements and minutes at 14:00 ET (13:00 CT): after the last decision for rates, FX,
  metals and energy, and at equity's 13:00 decision bar, so same-day use needs a new decision time. Speeches
  happen through the day.
- **Evidence:** a Chicago Fed working paper on 481 FOMC-member speeches since 2007: "these monetary policy
  speech surprises have no significant effects on inflation expectations or equity prices" on average
  (I-54). A doctoral thesis (Insper, unpublished) reports a pre-FOMC to post-FOMC reversal in E-mini S&P
  from the announcement to the day's end: "Over the period 1997 – 2020, considering 180 scheduled FOMC
  announcements, this strategy generates Sharpe ratios about 2.5 times greater than the pre-FOMC
  announcement drift puzzle" (I-56b). FOMC tone studies found concern network structure, not returns
  (I-55). FOMC minutes raise volatility (S38 search summary only).
- **Fit:** 8 events a year: at a per-event Sharpe of 0.3, t = 3 needs 9 / (0.09 x 8) = 12.5 years.
- **Used by program:** FOMC calendar flags in K2, K5, K9; K5-fomc-01 excluded on timing; pre-FOMC drift
  excluded in K9 on frequency (P-04).
- **Verdict:** evidence weak; fit weak.

**(c) Considered and dropped:** Baker Hughes rig count (Friday 12:00 CT; S35 found news only, no study).

**(d) Notes only (per brief):** news sentiment (AiTrader's territory, not researched); order flow from
one-minute OHLCV (the bars carry no signed volume; the program already has G10, the log volume ratio).

---

## 3. Gaps
- **Free consensus histories** for EIA storage, WPSR, USDA and macro releases: none found. Every surprise
  candidate (2a, 2b, 4, 6) is blocked by this, as in the program's rule-3 exclusions. Investing.com and
  similar calendars show forecasts, but their terms were not checked and they were not fetched.
- **Weather forecast vintages before 2021-02-26:** NCEI's page lists GFS 0.25 degree forecasts only from then
  (I-30). GEFS reforecasts and older GFS archives exist per general knowledge but are UNSOURCED here. The
  CPC archive page returned 403 (I-29).
- **Full texts not retrieved:** Kang-Rouwenhorst-Tang 2020 (abstract only); Rosa (JFM) on post-2013 intraday
  momentum (secondary citation only); Gao-Han-Li-Zhou 2018; Johnson 2017; Lehecka-Wang-Garcia 2014; the
  0DTE gamma paper (Dim, Eraker, Vilkov, SSRN; OpenAlex had no abstract); Sen 2026 free GEX reconstruction
  (P-09); Hong-Luo crude inventory intraday paper (403).
- **Release timestamps:** Treasury auction result publication time; USDA times are taken from the program's
  verified K6 record rather than re-fetched (the USDA pages fetched here did not show times in grepped text).
- **Costs:** API WSB price, ECMWF licence, OptionMetrics, Bloomberg consensus: not shown on any fetched page.
- **CME CVOL:** not researched (cmegroup.com forbids automated access).
- **Counts in fit lines** (weather-season days, negative-gamma share, auctions per month) are UNSOURCED and
  marked so; the t-arithmetic is t ~ s x sqrt(N x years), years = 9 / (s^2 N).

---

## 4. Source list (fetched in this task)

Full fetch log with UTC times, methods, sha256 and terms: pages/InfoSource/fetch_log.md.

| Key | URL | Fetched (UTC) | Page date | Verbatim quote |
|---|---|---|---|---|
| I-01 | https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm | 2026-10-03 | no date shown | "The COT Report is generally published each Friday at 3:30 pm Eastern Time (US), using the data from the immediately preceding Tuesday of that week." |
| I-02 | https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm | 2026-10-03 | no date shown | "The Commitments of Traders reports are released at 3:30 p.m. Eastern time." |
| I-03b | https://www.cftc.gov/robots.txt | 2026-10-03 | no date shown | "Content-Signal: search=yes,ai-train=no,use=reference" |
| I-04b | https://www.cftc.gov/webpolicy/index.htm | 2026-10-03 | no date shown | "Government information at the CFTC website is in the public domain." |
| I-05 | https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm | 2026-10-03 | no date shown | "The complete Commitments of Traders Futures Only reports file from 1986 is included by year." |
| I-06c | https://ageconsearch.umn.edu/record/54547/files/JARE_Aug09__04R_pp276-296.pdf (Firecrawl) | 2026-10-03 | 2009 | "Bivariate Granger causality tests show very little evidence that traders' positions are useful in forecasting (leading) returns in 10 agricultural futures markets." |
| I-08 | https://www.bankofengland.co.uk/-/media/boe/files/quarterly-bulletin/2006/the-information-content-of-aggregate-data-on-financial-futures-positions.pdf | 2026-10-03 | Spring 2006 | "There is little evidence that changes in non-commercial positions have significant predictive power regarding asset prices." |
| I-09 | https://api.openalex.org/works/https://doi.org/10.1111/jofi.12845 | 2026-10-03 | 2019/2020 | "These two components influence expected futures returns with opposite signs." (abstract) |
| I-10 | https://ir.eia.gov/ngs/schedule.html | 2026-10-03 | no date shown | "The standard release time and day of the week will be at 10:30 a.m. eastern time on Thursdays" |
| I-11 | https://www.eia.gov/petroleum/supply/weekly/schedule.php | 2026-10-03 | no date shown | "Tables 1-14 in CSV and XLS formats, are released to the web site after 10:30 a.m. eastern time on Wednesday" |
| I-12 | https://www.eia.gov/about/copyrights_reuse.php | 2026-10-03 | no date shown | "U.S. government publications are in the public domain and are not subject to copyright protection." |
| I-14b | https://www.api.org/energy-insights/statistics/wsb | 2026-10-03 | no date shown | "the weekly reports are scheduled for release every Tuesday afternoon at approximately 4:30 pm Eastern." |
| I-16b | https://livrepository.liverpool.ac.uk/3083246/ (Scrapling get) | 2026-10-03 | Last Modified 24 Jan 2026 | "More than 50% of the annual return is earned on these days." |
| I-19 | https://api.mountainscholar.org/server/api/core/bitstreams/9938aa1b-96a3-466b-ac76-7710737b5b72/content | 2026-10-03 | 2018 | "Consensus forecasts of the inventories in the weekly storage report are obtained from Bloomberg's survey of analysts." |
| I-21b | https://centaur.reading.ac.uk/90003/1/NG_paper_final_round.pdf | 2026-10-03 | 2021 (accepted version) | "In the more recent period, this has declined to only 3% and a Sharpe ratio of 0.5, which do not withstand transaction and funding costs." |
| I-25 | https://research-repository.uwa.edu.au/en/publications/c9d03fdb-8ca3-492e-92ee-1a262e0d6d7b | 2026-10-03 | 2023 | "daily changes in US natural gas (NG) futures prices and their variance can be explained by changes in oil futures prices and volatilities, storage announcements, and temperature shocks." |
| I-26 | https://www.cpc.ncep.noaa.gov/products/predictions/610day/ | 2026-10-03 | no date shown | "6-10 Day outlooks are issued daily between 3pm & 4pm Eastern Time." |
| I-27 | https://www.cpc.ncep.noaa.gov/products/predictions/610day/fxus06.html | 2026-10-03 | 2026-10-03 | "300 PM EDT Sat October 03 2026" |
| I-28 | https://www.weather.gov/disclaimer | 2026-10-03 | no date shown | "may be used without charge for any lawful purpose" |
| I-30 | https://www.ncei.noaa.gov/products/weather-climate-models/global-forecast | 2026-10-03 | no date shown | "0.25° 26Feb2021-Present 4/day: 00, 06, 12, 18UTC" |
| I-31 | https://www.nco.ncep.noaa.gov/pmb/nwprod/prodstat/ | 2026-10-03 | no date shown | "12 UTC GFS EVENT ... FORECAST F000-F384 15:29:20 17:13:54" |
| I-34 | https://vtechworks.lib.vt.edu/bitstreams/25def527-0597-478a-821f-c18b709cfdc7/download | 2026-10-03 | 2020 | "examine when various USDA information releases cause the largest market reactions in crop and livestock markets over 1985 through 2018." |
| I-35 | https://vtechworks.lib.vt.edu/bitstreams/fa60c40a-70c1-4520-a7e2-13131ec3cdfb/download | 2026-10-03 | 2019 | "expectations for corn, soybeans, and wheat are obtained from Knight Ridder/Dow Jones through 2015; 2016 expectations are from Thomson Reuters." |
| I-37b | https://pure.eur.nl/files/58145484/1_s2.0_S0304405X21001598_main.pdf (Firecrawl) | 2026-10-03 | 2021 | "market intraday momentum is present for the index when NGE is negative and becomes stronger when NGE becomes more negative." |
| I-39 | https://alexandria.unisg.ch/server/api/core/bitstreams/a99aba00-f967-49b3-aceb-f544dc386e0b/content | 2026-10-03 | 2024 (working paper) | "Rosa [7] analyzes additional data post2013, noting a decline in predictability" |
| I-40 | https://squeezemetrics.com/monitor/dix | 2026-10-03 | no date shown | "Gamma Exposure (GEX) is a dollar-denominated measure of option market-makers' hedging obligations." |
| I-42 | https://www.cboe.com/tradable_products/vix/vix_historical_data/ | 2026-10-03 | no date shown | "VIX Index data for 1990 to present (Updated Daily)" |
| I-43 | https://www.cboe.com/robots.txt | 2026-10-03 | no date shown | "Disallow: /*market_statistics/volume_reports/" |
| I-45 | https://www.cboe.com/terms | 2026-10-03 | no date shown | "You may view, print and download one copy of the Materials for your personal non-commercial use" |
| I-47 | https://squeezemetrics.com/monitor/static/DIX.csv (first 160 bytes, not saved) | 2026-10-03 | first row 2011-05-02 | "date,price,dix,gex 2011-05-02,1361.219971,..." |
| I-48 | https://squeezemetrics.com/monitor/terms | 2026-10-03 | no date shown | "creating user accounts by automated means or under false pretenses" |
| I-50 | https://www.federalreserve.gov/econresdata/ifdp/2013/files/ifdp1093r.pdf | 2026-10-03 | Nov 2013, rev. May 2016 | "Expectation data are available from Bloomberg for all countries since 2003." |
| I-51 | https://www.nber.org/system/files/working_papers/w10925/w10925.pdf | 2026-10-03 | 2004 | "the economic source of this predictability is non-public information possessed by option traders rather than market inefficiency." |
| I-52 | https://researchonline.lse.ac.uk/id/eprint/108198 | 2026-10-03 | 2021 | "it is found to be able to predict recessions, market downturns, and uncertainty indicators up to one year in advance." |
| I-53 | https://www.dallasfed.org/research/economics/2021/0831 | 2026-10-03 | 2021-08-31 | "The tail is the highest yield accepted at auction less the security's when-issued yield immediately before the auction's conclusion." |
| I-54 | https://www.chicagofed.org/-/media/publications/working-papers/2025/wp2025-23.pdf | 2026-10-03 | March 27, 2026 | "On average, these monetary policy speech surprises have no significant effects on inflation expectations or equity prices." |
| I-55 | https://arxiv.org/pdf/2510.02705 | 2026-10-03 | 3 Oct 2025 | "Dovish tone effects are not statistically significant for all time window k." |
| I-56b | https://repositorio.insper.edu.br/handle/11224/7532 (Scrapling get) | 2026-10-03 | no date shown | "Over the period 1997 – 2020, considering 180 scheduled FOMC announcements, this strategy generates Sharpe ratios about 2.5 times greater than the pre-FOMC announcement drift puzzle of Lucca and Moench." |

### 4b. Program records cited (repository documents, read by line range)
| Key | File | What it supplies |
|---|---|---|
| P-01 | reports/stage_e0_catalog_K4.md (members lines 384-794; excluded X-01..X-19 lines 884-902; log 961-991; 1074) | K4-ngpre-01, K4-ngrev-01, K4-apipre-01, K4-eiafade-01, K4-eiamom-01; surprise, weather exclusions; P-K4-028-b quote |
| P-02 | reports/stage_e0_catalog_K6.md (C9 calendar text; X-04..X-17 lines 919-932; log 992-1027) and docs/STAGE_E_ML_V2_DESIGN.md lines 435-550 | USDA release times, K6 members, exclusions; the V2.3 feature list |
| P-03 | reports/stage_e0_catalog_K2.md (X-03..X-08 lines 676-681), K3 (X-04..X-16 lines 954-966), K1 (X-17..X-19 lines 808-810), K5 (X-03 line 911) | auction and surprise exclusions; K3-cot-01 exclusion |
| P-04 | reports/stage_e10_catalog_K9.md sections 2-4 (lines 388-444) and Appendices A-B | VIX drafts withdrawn, routing, NG cold-forecast exclusion, Q18 |
| P-05 | reports/stage_e10_research_commodity.md lines 487-525 (K9M-017, Monteux et al. 2025, full text verified in E.10) | weather-forecast NG evidence and quotes P-K9M-017-a..g |
| P-06 | reports/stage_e0_catalog_K6.md ("USDA releases published at "12:00pm ET" are 11:00 CT all year") | ET to CT conversion |
| P-07 | reports/stage_e0_catalog_K1.md lines 218-245 (K1-cp1-01) and 403-409 (K1-vxnband-01); reports/stage_e11_signal_coverage.md lines 44, 112, 152 | intraday momentum port; VXN coded with content |
| P-08 | reports/stage_d1b_family_f_declaration.md lines 68-73 (F3.3) | the D.1 intraday momentum statistics screened on MES |
| P-09 | reports/stage_e0_research_K1.md line 116 (R-K1-072) | Sen 2026 GEX reconstruction rejected as off-product |
| P-10 | reports/E.12_RETURN.md lines 7-32; docs/DECISIONS.md lines 446-467 (V24) | Gate 0 failed; re-mining the 2019-2024 stores ruled out; MES excluded by P-1a |

---

## 5. The best two or three (ranking: post-publication evidence, then fit, then cost)

1. **Dealer gamma exposure (GEX) conditioning late-session momentum.** The only new source with a
   peer-reviewed intraday effect on the program's instruments over decades (I-37b). Against it: a reported
   post-2013 decline (I-39), no cost test for micros, and the unconditional form already failed on MES
   (P-07, P-08). Free daily data from 2011 (I-47). Sketch: MES (S&P data; P-1a excluded it from E.12), with
   MNQ, MYM, M2K as secondary trials; signal = sign of the return from the prior settlement to 14:00 CT,
   traded only when the prior day's GEX is in the lowest third of its trailing one-year range; decision
   14:00 CT, hold to F (68 minutes); about 80 events a year. At a per-event Sharpe of 0.1, t = 3 needs 11
   years. V24 rules out re-mining 2019-2024, so the test needs 2011-2019 or post-2024 data.
2. **NOAA GFS forecast revisions for natural gas.** Never used; timing fits (00Z before t1, 12Z before t3);
   free public-domain data (I-28, I-30, I-31). Evidence is one 2025 paper on daily spreads, with no
   post-publication record (P-05). Sketch: NG; signal = change in next-14-day gas-weighted HDD (CDD in
   summer) between today's and yesterday's 00Z runs; decision t1 08:30 CT, hold 120 minutes or to F; about
   150 events a year (UNSOURCED). A sourced forecast-vintage archive is needed first (NCEI lists 2021+,
   I-30). At a per-event Sharpe of 0.1, t = 3 needs 6 years.
3. **No third source meets the bar.** Nearest: the EIA storage surprise (2a). Its fit is moderate, but the
   consensus is proprietary, the related day premium decayed after 2011 (I-21b), and K4-ngpre-01 already
   covers that window. Implied-volatility indices (5) are free and well timed but show no directional
   evidence. They could only condition (1), and each extra condition adds trials to N.

## Lead note (2026-10-04, Fable R-11 and R-02)

- Fetch-order deviation: the Baltussen et al. PDF (I-37b) was fetched by Firecrawl directly after a curl 403,
  skipping the Scrapling step that research_rules.md step 4 requires before Firecrawl. The text is the published
  paper and is used as evidence. The deviation is recorded here.
- The negative-gamma share: the saved paper states "In the period from 1996 until May 2020 there have been 2930
  days with a negative NGE and 3158 with a positive one" (48%). This replaces "share UNSOURCED" in section 2.7(a)
  for the paper's NGE measure. SqueezeMetrics' GEX column is a different construction, so its own share remains to
  be counted (reports/stage_e13_prereg_gexmom.md section 9 step 3).

