# Stage E.20 Part A: product reader LE (CME live cattle, vehicle LE)

Reader: ProductReader-LE-OpusHigh. Started 2026-10-11T17:35:50Z, finished 2026-10-11T17:57:00Z (10:36 to 10:57 PDT).
Brief: `reports/stage_e20_briefs/brief_partA_shared.md`. Shared assignment: the livestock class (section 7).
The class notes are in `reports/stage_e20_briefs/shared/livestock_class_notes.md`.
No data store, result file or Gate 0 result was opened. Calendars and code were read for dates and rules only.

Conversion used throughout (public price level). CME's own lookback table in its CFTC-hosted Submission
20-352 (Aug 2020, Exhibit 4) gives the average June live cattle settle over 2015-2020 as "ALL $117.08"
(USD per cwt), i.e. $1.1708/lb. One LE contract is 40,000 lb, so notional is about $46,832. One tick
($0.00025/lb = $10) is 2.135 bp. The D8 round-trip wall (root table) is 2.498 ticks ($24.98), or 5.33 bp. The
1.5x hurdle is 3.75 ticks ($37.47), or 8.0 bp.

## 1. Evidence

| ID | Effect | Rule | Hold | Gross per trade | Gross/net | Sample | Decay evidence | Source | Grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | LC: rest-of-day (ROD) predicts the last half hour (LH). **Null for live cattle** | r_LH on r_ROD, where r_ROD = previous close to 30 min before the close, and LH = the last 30 min (LC day 08:30-13:05) | 30 min | not sized: slope 0.42 (x100), t 1.03, R2 0.00, R2_OOS -0.05 (insignificant) | gross | LC 1984-08-14..2020-05-01, 8,797 days, 1-min (Tickdata) | Fig. 4(c) (2006-06..2020-05): LC NW t = 0.3, LH -0.6, FC -1.6 | Baltussen, Da, Lammers, Martens, JFE 142 (2021) 377-403. On-disk copy `reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md` (sha256 18cb436e...), Table B3 Panel B line 3783; Fig. 4(c) line 2456 | primary (grep of the on-disk copy; Fig. 4 values are a figure transcription in that copy) |
| E2 | LC: the second-to-last half hour (SLH) predicts the last half hour (LH) | r_LH on r_ONFH, r_M and r_SLH jointly; for LC, SLH = 12:05-12:35 and LH = 12:35-13:05 | 30 min | slope 6.14 (x100), t 2.77, R2 0.19%, R2_OOS 0.01%. My derivation: if E\|r_SLH\| is at most about 0.25% (daily SD 0.95% from E5's Table 1, split evenly over 9 half hours), the expected \|r_LH\| is at most 0.0614 x 0.25% = 1.5 bp = 0.72 ticks | gross | as E1 | none reported per contract | Baltussen et al. 2021, Table B3 Panel B, line 3783 | primary (the size is my derivation) |
| E3 | Commodity class: ROD to LH momentum | long if r_ROD > 0, else short, over the last half hour; 1/N portfolio of 21 commodities. Live cattle sits in "Softs" | 30 min | Table 6: 4.34%/yr, SR 1.42, success 0.56. About 1.7 bp per trade at the portfolio level (planning brief's derivation, 4.34%/252). Softs group: slope 0.65 (t 2.16), R2_OOS -0.01 | gross | 21 commodity futures, 1974-2020 | Table 5: commodity slope 1.59 (t 3.92) in 1974-1999, then 1.04 (t 2.86) in 2000-2020 | Baltussen et al. 2021, Table 2 line 983, Table 5 line 1668, Table 6 line 1742, Table B3 line 3715 | primary |
| E4 | Price-limit continuation, next day (LC) | after a close at the daily limit, hold the next day in the limit direction. "No consecutive limit days" variant | 1 day, close to close (includes the overnight gap) | LC limit-up: +0.57% (t 4.07) over all limits; +0.36% (t 2.41) without consecutive limits. LC limit-down: -0.41% (t -1.99); -0.08% (t -0.50). +0.36% = 16.9 ticks close to close, but the intraday share (08:45 to F) is **unknown** | gross | 9 to 12 ag and livestock futures, Bloomberg daily open and close, 1991-01-07..2016-05-23. LC: 535 limits (236 up, 299 down) | No out-of-sample or post-2016 test. Table 3: for LC, the options-implied limit-day price forecasts the close-to-open return (b 0.39, R2 49.2%) better than the close-to-close return (b 0.34, R2 19.9%). That suggests most of the forecastable move is in the price by the next open (my reading) | Janardanan, Qiao, Rouwenhorst, working paper Feb 2017, Table 2 (p. 13) and Table 3 (p. 16), `pages/LE/janardanan_etal_2017_wp_ou.pdf(.txt)`. Published version JFM 39(8) 2019, pooled: +56/+29 bp and -53/-27 bp (`pages/LE/janardanan_qiao_rouwenhorst_2019_jfm_quotes.md`) | primary (WP full text; JFM via Firecrawl quotes) |
| E5 | Cattle on Feed (COF) surprises, next-day reaction | price reaction per 1% marketings surprise (USDA minus analysts) | 1 day, close to close; after-hours reports dated to the next trading day | marketed: +0.102 pp per 1% surprise post-2000 (se 0.049). Mean \|surprise\| post-2000 is 1.10%, so about 11 bp per report (my derivation). On-feed and placed are insignificant post-2000. Needs analyst-survey data (not an input) | gross | LC 1977-2016, AR(5)-GARCH(1,1) | Report-day variance ratio 1.08 (p 0.43) in 2000-2016, against 1.62 (p 0.00) in 1977-1999: the volatility impact is gone | Karali, Isengildina-Massa, Irwin, JARE 44(3) 2019 591-604, `pages/LE/karali_isengildina_irwin_2019_jare_quotes.md` | primary (Firecrawl quotes; raw PDF behind AWS WAF) |
| E6 | USDA livestock reports and report-day volatility | conditional-volatility dummies on report days | 1 day, close to close | none (volatility only) | n/a | 1970-2016 | COF effect on cattle volatility: 0.205 in 1985-1994, falling to 0.097 in 2007-2016. Hogs and Pigs "not significantly different from zero" in 2007-2016 | Isengildina-Massa, Karali, Irwin, Adjemian, NCCC-134 2016, `pages/LE/isengildina_karali_irwin_adjemian_2016_nccc134_quotes.md` | primary (Firecrawl quotes) |
| E7 | Intraday behaviour around LE/HE limit moves | event study of limit moves | intraday | none on returns: "higher volatility and lower liquidity when trading resumes" | n/a | LE, HE intraday futures and options, 2014-2019 | n/a | He and Serra, AJAE 104(5) 2022 1724-1746 (closed access) | secondary-only (abstract via the OpenAlex API, `pages/LE/openalex_abstracts.txt`) |
| E8 | Lean hog limit-up: price trades past the limit within 3 days | (trade press) | 3 days | "853 of 1,039" | unknown | unknown | unknown | Technical Traders article citing Moore Research (Cloudflare 403 to curl and Scrapling) | unverified (search summary only) |

Checked and not usable for LE (reported so they are not re-searched):
- The Aalto thesis (2008-2024) has no commodities. See `shared/aalto_thesis_notes.md` (ZN reader), line 16: "equity, bond and currency futures only (20 futures)".
- Borgards, Czudaj, Hoang (Resources Policy 2021): intraday overreaction in 20 commodities, 2019-11..2020-06, with no livestock in the list. Grep of the full text (`pages/LE/borgards_czudaj_hoang_2021_pmc9759686.txt`) finds no "cattle" or "hog".
- K. Joseph's dissertation, "Three essays in commodity futures markets" (Illinois, IDEALS item 73133). The cattle essay is a daily boxed-beef lead-lag study ("the futures price leads boxed beef price"). The intraday announcement essay is about soybeans.
- He, Serra, Garcia (AJAE 2021): resilience of liquidity in lean hog flash events. Liquidity only, not open access.
- Couleau, Serra, Garcia (2017/2018): LC realized volatility, 2011-2015. Abstract only: noise matters "below 4-minute time intervals", and the 2015 volatility was "strongly driven by market fundamentals".
- Gousgounis and Onur (2017, 2020): the livestock pit closure, a liquidity study. Title only.

None of the following turned up in E.0's K6 log (`reports/stage_e0_research_K6.md`) or in this search: a post-2015 study sizing intraday livestock returns around report windows, at the settlement window (12:59:30-13:00), or at the open. Nor did a study of the intraday lead-lag from corn to live cattle.

Reading (decay and costs):
- Live cattle shows no rest-of-day momentum into the close (E1: t 1.03, R2_OOS negative), even though the commodity class does (E3). The class effect decays (slope 1.59, then 1.04) and is about 1.7 bp per trade at the portfolio level. One LE tick is 2.1 bp, and D8's wall is 5.3 bp.
- The only significant LC intraday predictor in Baltussen, SLH (E2), implies at most about 1.5 bp (0.7 ticks), against a 1.5x hurdle of 3.75 ticks.
- The main USDA livestock reports (COF, Hogs and Pigs) come out after the livestock close. Karali et al. date them to the next trading day (footnote 9), so their reaction is an overnight gap, which is out of scope. Their report-day volatility effect has disappeared since 2000 (E5, E6). The 14:00 CT release time is [secondary-only] (trade press).
- The limit-continuation evidence (E4) is daily and close to close, and its sample ends in 2016. For LC, the options test suggests the predictable part is in the price by the next open. The share left for an 08:45-to-F intraday hold (K6-limitcont's design) is unknown.
- Limit days are rare. LC hit a limit on 1.76% (up) and 1.60% (down) of days in 1991-2016 (Janardanan et al. 2019, Table 1 share; the share is over contracts and days).

## 2. Feature availability (V2.3 features on LE rows)

The windows for LE:
- Backward window: 2010-07-01..2019-05-05. LE rows are effectively 2014-12-15..2019-05-05 only, because 2010-06-07..2014-12-14 is excluded by E.16 R-S3 (the settlement time is unsourced there).
- Search window: 2019-05-06..2024-02-29.

The session eras come from the calendar file `data/calendars/hist2010/livestock.json` (sha256 802a4dd9..., the same file as `reports/stage_e16_calendars/hist2010_livestock.json`; coverage 2010-06-01..2019-05-31; E.16 R-C3 and R-S5):

| Era | Dates | Session | Source |
|---|---|---|---|
| 1 | to 2014-10-24 | Sunday-to-Friday Globex, 17:00 to 16:00, Monday open 09:05 | f14_408 (secondary) |
| 2 | 2014-10-27..2016-02-26 | 08:00-16:00 Tue-Thu, 08:00-13:55 Fri, Monday (or the first business day of the week) open 09:05 | f14_408 (cme) |
| 3 | from 2016-02-29 | 08:30-13:05 | CME 16-064 (cme) |

Settlement in the effective window is 13:00 CT. The window is 12:59:30-13:00:00 from 2014-12-15 (E.16 settlement table, S27, S33, S30).
- In era 2, therefore, F_X = 13:03 falls mid-session (trading ran to 16:00).
- On the 62 era-2 late-open dates, no bar exists at 08:30 or at t1 = 09:00.
- In the effective backward window, the calendar has 14 unsourced trade dates (excluded as action dates), 39 full closures and 13 early halts.

From the frozen release calendar (`reports/stage_e2b_release_calendar.json`, sha256 839f2437..., 2019-05-01..2026-06-21), LE's D8 release list is:
- WASDE: 85 rows, 12:00 ET;
- CROP (Crop Production): 85 rows, 12:00 ET;
- CROP_ANNUAL: 7 rows, 12:00 ET;
- FOMC: 57 rows, 14:00 ET.

That is 158 rows in the search window, or 95 distinct instants. The 2010-2019 release calendar (`reports/stage_e14_cal_releases.json`, sha256 9a051211..., 2010-06-01..2019-05-31) holds only NGS (470), WPSR (470) and FOMC (72).

| Feature | Legs | Calendars / literal tables | Exists 2010-2019 (LE backward) | Exists 2019-2024 | Dates and basis |
|---|---|---|---|---|---|
| cp1_ret | LE | D6 O = 08:30 literal; livestock group calendar (livestock.py 2019+, hist2010 livestock.json) | partial | yes | No LE rows before 2014-12-15 (R-S3). In era 2 (2014-12-15..2016-02-26), the 62 Monday or first-of-week late opens at 09:05 have no 08:30 bar, so the value is missing. On era-2 Tue-Fri the 08:30 bar is 30 min after the 08:00 open, so the value is computable but measures 08:30-08:59, not the session's first half hour. Era 3 (2016-02-29..2019-05-05) matches 2019-2024. |
| cp2_range, cp2_brk | LE | as cp1 | partial | yes | Same dates as cp1. In era 2 the "opening range" [08:30, 08:45) is not the session's opening range. |
| cp3_clv | LE | as cp1 (port-complete day) | partial | yes | From 2014-12-15. Era-2 Mondays are not port-complete (no bars 08:30-09:04), so the next date uses the latest complete day. Undetermined: whether the 2014-12-15 start may use d-1 = 2014-12-12 (inside the excluded span); that is the lead's call. |
| k6_limitcont_dir | LE | LIVESTOCK_FULL_SESSIONS and LIVESTOCK_TRADE_DATES (strategy/members/k6/_calendar.py, 2019-05-01..2026-06-19); LIMIT_PERIODS and DROPPED_LIMIT_DATES (k6/_limits.py, LIMIT_RANGE 2019-05-01..2026-06-19; generated from rules/price_limits.py); SETTLEMENT_WINDOW_LIVESTOCK 12:59:30-13:00 | **no** | yes | (a) 2019-2024: every LE period of LIMIT_PERIODS inside 2019-05-06..2024-02-29 is "sourced" (0.03 to 2020-10-04; 0.04; 0.05; 0.0575; 0.0675 to 2024-06-02). The bracketed LE periods lie after 2024-10. (b) 2010-2019: no limit table exists on disk (limit_ticks returns None, so the feature is never applicable), and the k6 calendars start 2019-05-01. (c) A table is sourceable for the effective window from CFTC-hosted CME filings (`pages/LE/cftc_*.pdf`): CME 14-575 (filed 12/18/14) shows the rule text "no trading at a price more than $.030 per pound above or below the previous day's settlement price", and CME 20-352 (Aug 2020) moves "the current, initial daily price limit for Live Cattle futures from $0.03 to $0.04 per pound" effective trade date 2020-10-05. No filing for 2015-2019 was read, so continuity in between is unverified. CME 14-109 (effective 2014-09-08) sets $0.050 for the expiring month's last two days; the member encodes the initial limit only (R-L2). Expanded $0.045 limits date from 14-575. (d) The settlement window 12:59:30-13:00 holds from 2014-12-15 (S27). |
| g01_ret30 | LE | livestock calendar (open intervals) | partial | yes | At t1 = 09:00 the bar closing at 08:30 is outside the session in era 3 and 2019-2024, so the value is not applicable there (SG-3). In era 2 (open 08:00) that bar exists Tue-Fri, so the value is applicable at t1. The availability pattern therefore differs by era. t2-t4 are as in 2019-2024. |
| g02_ret60, g03_ret120 | LE | as g01 | partial (from 2014-12-15) | yes | At t1 (and at t2 for g03) the lookback bar closes at or before 08:00, which is outside the session in every era. Otherwise as 2019-2024. |
| g04_ret_day | LE | as g01 | partial | yes | The first bar of the trade date is 08:00 in era 2 (09:05 Mondays), against 08:30 later. Same definition, shifted meaning. |
| g05_gap | LE | livestock calendar (C_X - 1 bar of the previous trade date; early-halt rule SG-4) | partial | yes | Era 2: the "gap" from 12:59 on d-1 to 08:30 on d spans 13:00-16:00 and 08:00-08:30 of live trading, and is missing on the 62 late-open dates. Not applicable after the 13 early-halt dates. |
| g06_rv60, g07_range, g08_prev_ret, g10_logvol30 | LE | livestock calendar | partial (from 2014-12-15) | yes | Bars only. g07 includes 08:00-08:30 in era 2. g06 and g10 need 20 previous row dates. |
| g09_vol_state | LE | livestock calendar | partial | yes | The warm-up is 20 + 120 dates. If the warm-up may not read bars before 2014-12-15, about the first 140 dates (to about mid-2015) are lost. Whether pre-2014-12-15 bars may feed the warm-up is undetermined (lead). |
| g11_t_index, g12_dow | none | trade dates | yes (from 2014-12-15) | yes | Clock and weekday only. |
| g13_min_to_rel, g14_min_since_rel, g15_rel_day | none (calendar) | LE's D8 list: WASDE, CROP, CROP_ANNUAL, FOMC | **partial** | yes | 2019-2024: frozen calendar, all rows "verified". 2010-2019: E.14 calendar has FOMC only. No WASDE, Crop Production or Crop Annual rows exist on disk for 2010-2019 (E.16 review F-11 says the same: "CROP, WASDE, CROP_PROGRESS grains and livestock" types have no 2010-2019 rows). FOMC coverage: [shared, see shared/macro_calendars.md] (RTY reader). WASDE/Crop history: ZC reader (product_ZC.md). |
| g16_month_end | none | group calendar trade dates | yes (from 2014-12-15) | yes | hist2010 livestock.json covers 2010-06-01..2019-05-31. 14 unsourced dates in the effective window: 2014-12-24, 12-25, 12-26 and 12-31, and 2015-01-01 and 01-02, among them. They are excluded as action dates and may touch the month-end flag for 2014-12. |
| g17_nq, g17_zn, g17_6e, g17_cl, g17_gc | NQ, ZN, 6E, CL, GC | the leads' group calendars (hist2010 equity, rates, fx, energy, metals: 2010-06-01..2019-05-31; 2019+ data/calendars/*.py) and the leads' roll tables | yes (subject to the lead readers) | yes | On LE rows the 60-min lead return at t1 = 09:00 reads lead bars 08:00-09:00, inside every lead's session. Listing: [shared, see product_NQ/ZN/6E/CL/GC.md]. |
| g17_zc | ZC | n/a | not applicable by design | not applicable by design | ZC is the row's own cluster lead (K6), so the feature is not applicable on LE rows in both windows (SG-2). |
| g17_mbt | MBT | n/a | no | partial (from 2021-05) | MBT was listed in 2021 and is not one of the 17 roots (brief section 7). |
| g17_mes | MES | n/a | no | yes (from 2019-05-06) | MES was listed in 2019 and is not one of the 17 roots. |
| k9_anncday | none | EC-K9 | does not apply | does not apply | Applies on MNQ, M2K and MYM rows only (V2.3). |

Not read and not needed: K8 signals and other K6 members (crushgap, wasdepre) read no LE bars and do not apply on LE rows.

## 3. Proposed features

None. The reasons:
1. The only live-cattle-specific intraday predictor in a primary source, Baltussen et al.'s SLH (E2), is 30 min that ends 30 min before a 13:05 close. Its decision point (12:35) is not t1-t4. At t4 = 12:03 (h = F, exit 13:03) the window differs. Its implied size (about 0.7 ticks gross at most) is about 0.29x D8's 2.498-tick wall, far below 1.5x.
2. ROD momentum on LC is null (E1), and r_ROD is already added by the prompt.
3. Limit continuation (E4) is already a member feature (`k6_limitcont_dir`). Its published size is daily and close to close (+36 bp without consecutive limits = 16.9 ticks, but the intraday share is unknown and the options test points to the open). No published intraday figure exists to size a new variant, and a variant's 2010-2019 limit table is absent on disk.
4. COF and Hogs and Pigs effects are overnight (reports after the close) and need analyst-survey surprises, which are not an input. Their volatility effect has decayed (E5, E6).

## 4. NQ only

n/a

## 5. Fetch log, terms read, budget notices

Fetch log (raw files under `reports/stage_e20_briefs/pages/LE/`; machine log `LE_fetch_log.tsv`):

| URL | UTC | sha256 | Path | Status |
|---|---|---|---|---|
| https://ageconsearch.umn.edu/robots.txt | 17:39:33Z | 76ce0beb53cc0c83ac20f38864831433c85371c17bdd582c822505c465cd369a | ageconsearch_robots.txt | ok |
| https://ageconsearch.umn.edu/pages/about | 17:39:40Z | e3b0c442... (empty) | ageconsearch_about.html | blocked (202, x-amzn-waf-action: challenge) |
| https://ageconsearch.umn.edu/record/292333/files/JARE%2C44.3%2CSept2019%2C%238%2CKarali%2C591-604.pdf | 17:39:53Z | e3b0c442... (empty) | karali_etal_2019_jare.pdf | blocked (AWS WAF 202). scrapling fetch 202 at 17:40:12Z. Then Firecrawl, see the quotes file |
| https://farmdoc.illinois.edu/robots.txt | 17:40:34Z | 8219ec175e69f4216c1c6462f625ab06abd02b04e2a26272d45c96d4be2f31c1 | farmdoc_robots.txt | ok (not used further) |
| https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/fut.21999 | 17:41:05Z | n/a | none | blocked (Cloudflare 403, curl and scrapling get); Firecrawl ok, 17:42:05Z |
| (Firecrawl) the same JFM PDF, two directQuote queries | 17:42:05Z | quotes file 3a2a55ba893717ff2b10fe3f4073783c278f06351564fb35d23a4cb3a8afa592 | janardanan_qiao_rouwenhorst_2019_jfm_quotes.md | ok (raw PDF not saved) |
| (Firecrawl) https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/ajae.12146 | about 17:43Z | n/a | none | redirected to the abstract page (not open access); not used |
| OpenAlex API abstracts (10 + 4 works) | 17:43:38Z | 9997c52dab8a22599c6e8a59bde014eb4a32ee3bb10498946f1514eb5b1f1e11 | openalex_abstracts.txt | ok (secondary: abstracts only) |
| https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9759686/fullTextXML | 17:45:06Z | 98fd726eba6419bce35481ea51a336efb2033e867120947a38b44275630e49bc | borgards_czudaj_hoang_2021_pmc9759686.xml (+ .txt) | ok (no livestock) |
| (Firecrawl) https://ageconsearch.umn.edu/record/285854/files/Isengildina_Karali_Irwin_Adjemian_NCCC-134_2016.pdf | 17:45:06-17:47:21Z | quotes file b1427e074234533647de25c94c715b3e5509a2174fd14cec2a814d2aa3b56f8a | isengildina_karali_irwin_adjemian_2016_nccc134_quotes.md | ok (raw PDF not saved) |
| (Firecrawl) the Karali JARE PDF above | 17:45:06-17:47:21Z | quotes file dedc30e24dead60bc3a06edfbd31586b07a546550225b5d99c0b83691a6f4896 | karali_isengildina_irwin_2019_jare_quotes.md | ok (raw PDF not saved) |
| https://technical.traders.com/robots.txt | 17:47:03Z | 11a07014e0b6186d79707b32bc949d34775bf4d98be8d8f5c6aa70a70e9800c4 | traders_com_robots.txt | ok |
| https://technical.traders.com/tradersonline/display.asp?art=402 | 17:47:09Z | be261be497d6855fd7cb74861644fb0e6d078c9c19b0ad19c747d4381d3956c7 | traders_com_art402.html (challenge page) | blocked (Cloudflare 403; scrapling get 403, scrapling fetch 403) |
| https://www.cftc.gov/robots.txt | 17:48:59Z | 1d500ec03ef610b457287a8e55e6ad2f83a7bb888a630325c23573dccdcd81bb | cftc_robots.txt | ok |
| https://www.cftc.gov/filings/orgrules/rule122214cmedcm002.pdf | 17:49:03Z | 6cc9b6acf138ef9a5c249bec676808dea8f328520d325b5a8937186d8c851634 | cftc_rule122214cmedcm002.pdf (+ .txt) | ok |
| https://www.cftc.gov/filings/ptc/ptc082020cmedcm001.pdf | 17:49:08Z | 74d09fdfa238ed0698d273763c76a9f1f3782ff0dcb22d71b3983ca392990d68 | cftc_ptc082020cmedcm001.pdf (+ .txt) | ok |
| https://www.cftc.gov/filings/ptc/ptc072814cmedcm002.pdf | 17:49:14Z | 4e700154d95945792b70094a806cc7f872e0bb1a7a7b4ae6a833fb913b986c50 | cftc_ptc072814cmedcm002.pdf (+ .txt) | ok |
| https://www.ideals.illinois.edu/robots.txt | 17:50:20Z | 2ac02f038caa0320c19646a32dabdea7b14b9ab8683655be7cb26a8548465091 | ideals_robots.txt | ok |
| https://www.ideals.illinois.edu/items/73133 | 17:50:23Z | 2307937e3c0ddc95c466eb8c581a0cf176e00c902ff456eeae6cab37bbf54af2 | ideals_item73133.html | ok |
| https://www.ou.edu/robots.txt | 17:50:49Z | c2bef0a00987245e3ef9662b2ac63ceb5b7fda9cf1ef9872a16204885ab42bb1 | ou_robots.txt | ok |
| https://www.ou.edu/content/dam/price/Finance/energyfinanceconference/papers/Janardanan-et-al-Limits%20Paper.pdf | 17:50:52Z | f8a3ed6596667a3d37fd17cc879f7b594bd91242b743a34829f602a3d1ec28fc | janardanan_etal_2017_wp_ou.pdf (+ .txt) | ok |

Terms and robots read (all on 2026-10-11):
- ageconsearch.umn.edu robots (17:39Z): Crawl-Delay 5; disallows /rss and /search only. The site's about/terms page sits behind the same WAF and could not be read. Ruling: an open repository, record files allowed. Automated access was refused by the WAF, so Firecrawl was used as the brief's last fallback.
- onlinelibrary.wiley.com robots (17:40Z, read inline, not saved): /doi/pdfdirect is not disallowed. Ruling: bronze open-access PDF, Firecrawl fallback.
- cftc.gov robots (17:48:59Z): "User-agent: * / Content-Signal: search=yes,ai-train=no,use=reference / Allow: /". Ruling: allowed for reference.
- ou.edu robots (17:50:49Z): "Allow: /content/dam". Ruling: allowed.
- ideals.illinois.edu robots (17:50:20Z): disallows admin and auth paths only. Ruling: allowed.
- technical.traders.com robots (17:47:03Z): no rule for /tradersonline. Ruling: allowed by robots, but blocked by Cloudflare. Recorded as a gap.
- farmdoc.illinois.edu robots (17:40:34Z): Crawl-delay 10. Not used further.
- Europe PMC REST API (17:45Z): a public programmatic API. Not saved separately.
- cmegroup.com: never fetched. CME text is quoted only from CFTC-hosted filings.

Budget: 10 WebSearch calls used (cap about 90). No over-budget notice. Firecrawl: 5 scrapes, no credit notice. The tools reported cost notices (informational).

Incident (shared scratchpad collision, for the lead). At 17:36-17:37Z the 6E reader ran my first helper script (scratchpad `fetch.sh`, whose output dir was pages/LE), and the GC reader then overwrote that script with its own.
- Result 1: three 6E files sit in `pages/LE/` (boc_robots.txt, mpra_robots.txt, centaur_robots.txt), with 4 log lines in `pages/LE/fetch_log.tsv`. They are not mine and are not used here.
- Result 2: my first ageconsearch robots fetch landed in pages/GC (GC's `_fetch_log.tsv`).
- I then moved to a private script (`scratchpad/le_reader_private/le_fetch.sh`, log `pages/LE/LE_fetch_log.tsv`).
- The other readers' later calls through `fetch.sh` go to pages/GC. Their leads should check their logs.

## 6. Unfinished and unverified

- E4's intraday share is unverified. No source splits the next-day LC return into open-to-close. The reading that "most is in by the open" is mine, from Table 3's R2 (49.2% close-to-open against 19.9% close-to-close).
- E2's per-trade size is my derivation. It assumes an even spread of daily variance (from E5's Table 1 SD of 0.95%) over 9 half hours, not a published LC half-hour SD.
- E7 (He and Serra 2022) is abstract-only. E8 (Moore Research figure) is unverified (page blocked).
- The COF and Hogs and Pigs release time (14:00 CT) is secondary-only. No USDA page was fetched for it.
- LE limit continuity 2014-12..2020-10 at $0.030 is bracketed by CME 14-575 and 20-352. No 2015-2019 filing was read to rule out an intermediate change.
- Not done: a 2010-2019 WASDE, Crop Production or Crop Annual calendar check beyond the files on disk (the ZC reader's area). The lead decides whether rows before 2014-12-15 may feed warm-ups (g09, cp3).
- The Firecrawl-sourced quotes (E1-E3 excluded) come from Firecrawl's text extraction. Raw PDFs were not saved for the JFM, JARE and NCCC papers.
