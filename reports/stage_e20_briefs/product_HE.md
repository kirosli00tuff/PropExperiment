# Stage E.20 Part A: product reader HE (CME lean hogs; vehicle HE)

Reader: ProductReader-HE-OpusHigh. Written 2026-10-11, finished 17:50 UTC (10:50 PDT). JSON:
`reports/stage_e20_briefs/product_HE.json`. Raw pages: `reports/stage_e20_briefs/pages/HE/`.
Assignment: root-specific evidence only (lean hog intraday studies since 2015, hog report windows).
Livestock-class evidence belongs to the LE reader (`shared/livestock_class_notes.md`); the Aalto thesis
to the ZN reader (`shared/aalto_thesis_notes.md`). Neither file was on disk when this was written.

HE facts used below (root table): tick $10 (0.025 c/lb x 40,000 lb), D8 RT wall 1.965 ticks = $19.65,
livestock O 08:30, C 13:00, F 13:03 CT, backward window 2017-07-01..2019-05-05, search window
2019-05-06..2024-02-29. Price level for the bp conversions: 80 c/lb, the level the He (2022) source
itself uses ("for a lean hog contract with a unit price of 80 cents/pound", p.16). At 80 c/lb,
1 tick = 3.125 bp, the D8 RT = 6.1 bp, and the 1.5x hurdle = 2.95 ticks = $29.48 = 9.2 bp.

## 1. Evidence

| ID | Effect | Rule | Hold | Gross per trade | Sample | Decay / OOS | Source | Grade |
|---|---|---|---|---|---|---|---|---|
| E1 | ROD -> LH intraday momentum, lean hogs alone | r_LH on r_ROD = P(C-30)/P(prior close)-1; paper's LH hours 08:30-13:05 | 30 min (12:35-13:05) | slope 0.03 (x100): a 1% r_ROD predicts 0.03 bp = 0.01 tick. Gross. | LH 1981-04-03..2020-05-01, 9,499 days, 1-min | t 0.06; adj. R2 -0.01%; R2_OOS -0.06%: **null** | Baltussen, Da, Lammers, Martens, JFE 142 (2021), Table B3 Panel B | primary (on-disk copy) |
| E2 | SLH -> LH, lean hogs | r_LH on r_SLH (12:05-12:35) jointly with r_ONFH, r_M | 30 min | slope 3.30 (x100): a 1% r_SLH predicts 3.3 bp = 1.06 ticks; half-hour moves are usually far below 1% | as E1 | t 1.76 (10% level); joint R2_OOS -0.06%: no OOS value | same, LH row | primary |
| E3 | Next-day direction after a locked-limit day (under-reaction) | logit of 1[settle(d) > settle(d-1)] on SignedLimit(d-1) | settle to settle (includes the overnight gap) | direction only, not sized: beta 1.006 (SE 0.181), odds ratio about 2.7 | first five nearby, 2014-2019, daily, 7,264 obs.; 172 locked-limit events (39 in the first nearby) | none (one sample; limit days cluster in 2014) | He (2022) dissertation, App. B.4, Table B.5 (working version of He and Serra, AJAE 2022) | primary |
| E4 | Price path after limit moves | 5-min median distance to the limit, pre/post window | locked: next open to +1 h; temporary: same day | locked: next day at 0.3-0.4 c/lb beyond the old limit = 12-16 ticks ($120-160), reached at the **open** (overnight gap, not capturable from t1 = 09:00); later drift not sized ("remains persistently far"). Temporary: about 0.5 c/lb (20 ticks) back inside the range, but "temporary" is defined by the close (hindsight). Gross; pooled HE and LE in the text. | HE and LE, 2014-2019, intraday | none | He (2022), ch.3, Fig. 3.1 text p.69 | primary |
| E5 | Flash events (moves of 2.4 c/lb or more within an hour, at 80 c/lb) | liquidity study, USDA days excluded | n/a | no return pattern sized; events last about 50 min and are read as fundamental | HE and corn, 2014-2019, LOB | n/a | He (2022) ch.2 (= He, Serra, Garcia, AJAE 2021) | primary |
| E6 | Hog report window: Quarterly Hogs and Pigs | normally 3:00 pm ET (14:00 CT, after the 13:05 close: the reaction is overnight, out of scope); a Friday noon-ET release (11:00 CT) falls inside the session | n/a | no intraday study found | n/a | n/a | USDA NASS notice, Dec. 10, 2018 | primary (timing) |
| E7 | Hog report window: USDA LMR swine reports | statutory deadlines: prior-day purchased by 08:00 CT, slaughtered by 10:00 CT, morning report by 11:00 CT, afternoon by 15:00 CT (after the close). Deadlines, not fixed instants | n/a | no published intraday futures response found | n/a | n/a | 7 U.S.C. 1635j (2024 ed., govinfo) | primary (timing) |
| E8 | Limit events lead to persistent price changes (multi-commodity) | not read | | | | | Janardanan, Qiao, Rouwenhorst, JFM 2019 (class-level: LE's) | secondary-only (abstract via OpenAlex) |

Verbatim quotes (each re-found by script in the saved file, whitespace normalized):
- E1/E2, Baltussen Table B3 (on-disk copy lines 3759-3784): "| LH | 0.56(0.87) | 0.00 | -0.04 | 0.58(0.89) | -0.98(-1.18) | 3.30*(1.76) | 0.08 | -0.06 | 0.03(0.06) | -0.01 | -0.06 |". Columns: βONFH, R2, R2OOS, βTONFH, βM, βSLH, R2, R2OOS, βROD, R2, R2OOS. Caption (lines 3673-3684, markdown emphasis removed): "Panel B: Newey and West (1986) robust t-statistics in parentheses. Samples range from April 1981 to May 2020. ... Adjusted R2, R2OOS, and slope coefficients are multiplied by 100." Sample row (line 3309): "| Lean hogs futures | LH | 1981-04-03 | 2020-05-01 | 9499 | 08:30-13:05 | Softs |".
- E3 (pp.179-180, 200): "SignedLimit d−1,c 1.006*** 0.181" (Lean Hog column; Obs 7,264); "The exponential of the coefficient β1 is around 2.7, suggesting that on average the price is 1.7 times more likely to move in the same direction following a locked-limit day than following a non-limit day."
- E4 (p.69): "On the next trading day following a locked-limit day, the price jumps to a new level that is 0.3 to 0.4 cents/lb. outside the previous day's limit. The price level remains persistently far from the previous limit after one hour of trading ... In contrast, temporary-limit moves are followed by a price reversal resulting in a post-limit price level around 0.5 cents/lb. inside the trading range". Table 3.1 (p.87): lean hog first nearby, 39 locked-limit days (2.6% of trading days) in 2014-2019.
- E5 (pp.16, 36-37): "the revised threshold requires the price to change by at least 2.4 cents/pound ($960 per contract) within an hour"; "The temporal duration of the events (around 50 minutes in both markets) corresponds closely to the recent findings which show that it takes about an hour for low latency agricultural markets to absorb fully fundamental information from USDA releases".
- E6: "has rescheduled release of the December Cattle on Feed and Hogs and Pigs reports to Thursday, Dec. 20 at 3:00 pm ET. They were previously scheduled for release on Friday, Dec. 21 at Noon ET."
- E7: "The Secretary shall publish the information obtained under this paragraph in the morning report as soon as practicable, but not later than 11:00 a.m. Central Time, on each reporting day." Also "not later than 8:00 a.m. Central Time", "not later than 10:00 a.m. Central Time" (prior-day reports), "in the afternoon report as soon as practicable, but not later than 3:00 p.m. Central Time".

Reading of decay and costs.
- The one sized intraday test on lean hogs alone, E1, is a clean null over 39 years, out of sample as well. H6 (ROD -> LH) has no support on HE. The SLH slope (E2) is significant only at 10% in sample and has negative R2_OOS.
- The limit result (E3, E4) is real but sits in the wrong place for an intraday book. The continuation after a locked-limit day shows up mostly as the next day's gap at the open (12-16 ticks). After the open the price "remains persistently far" from the old limit, i.e. no further drift is shown. A t1 (09:00) entry would come after the gap. The published logit is settle to settle and unsized. The idea is already in the library as `k6_limitcont_dir` (K6-limitcont-01).
- Locked-limit events are rare: 39 front-month days in 2014-2019, most of them in 2014. That is a power problem for any limit-conditioned test on HE.
- Hog reports: Hogs and Pigs and the LMR afternoon report land after the close, so the response is overnight. The in-session LMR morning report (by 11:00 CT, = t3) has a statutory deadline, not an instant. No post-2015 study of an intraday futures response to it was found.
- Older daily event studies (Colling and Irwin 1990; Isengildina, Irwin, Good 2006; Frank, Garcia, Irwin 2015) were seen only in search snippets. They are daily or close-to-open, pre-2015 or overnight, so out of scope. Not used.

## 2. Feature availability (HE rows)

Sources: HE bars priced from 2017-07 (`reports/stage_e16_windows.json`; last unpriced month 2017-06,
E.16 U2). Livestock calendar 2010-2019: `data/calendars/hist2010/livestock.json` (2010-06-01..2019-05-31,
E.16 Task 3b, "secondary", sha256 802a4dd9...; HE window 2017-07-03..2019-04-30: 460 trade dates,
4 unsourced: 2017-10-09, 2017-11-10, 2018-10-08, 2018-11-12; session era 3, 08:30-13:05, from
2016-02-29, "cme" per CME 16-064). Livestock calendar 2019-2026: `data/calendars/livestock.py`
(2019-05-01..2026-06-19, "cme"). Loader: `data/hist_calendar.py` HIST_GROUPS now includes "livestock".

| Feature | Legs | Calendars / tables | 2010-2019 (HE 2017-07..2019-05) | 2019-2024 | Dates and basis |
|---|---|---|---|---|---|
| cp1_ret, cp2_range, cp2_brk, cp3_clv | HE | livestock sessions (O 08:30, C 13:00) and trade dates | yes | yes | from 2017-07-03 (cp3 from the 2nd trade date); livestock first bar = 08:30 bar of d |
| k6_limitcont_dir | HE | livestock calendar; settlement window 12:59:30-13:00:00 CT; LIMIT_PERIODS | **no** (no limit table on disk) | yes | LIMIT_PERIODS (`strategy/members/k6/_limits.py`) and `rules/price_limits.py` HE periods start 2019-05-01; E.16 review F-07: "for 2010-2019, where no limit table exists". Settlement window: `reports/stage_e16_settlement.md`, HE 2014-12-15..2024-02-29, primary direct to 2018-10, inferred after. Public facts below. |
| g01_ret30, g02_ret60, g03_ret120, g04_ret_day, g07_range, g08_prev_ret | HE | livestock sessions | partial | yes | backward: from about the 21st trade date (2017-08-01), once sigma_X,d's 20 dates are full; G1-G3 at t1 not applicable for livestock by design (SG-3) |
| g05_gap | HE | previous trade date, C_X, early halts | partial | yes | sigma warm-up as above; not applicable after the 6 early-halt dates in the window (2017-07-03, 2017-11-24, 2017-12-22, 2018-07-03, 2018-11-23, 2018-12-24) |
| g06_rv60, g10_logvol30 | HE | livestock sessions | partial | yes | from the 21st row date (about 2017-08-01) |
| g09_vol_state | HE | livestock trade dates | partial | yes | from about the 141st trade date (2018-01-23): 20 dates + 120-date median |
| g11_t_index, g12_dow | none | V2.2 clock only | yes | yes | O 08:30, F 13:03 in both windows |
| g13_min_to_rel, g14_min_since_rel, g15_rel_day | none | HE's D8 list: FOMC, WASDE, CROP, CROP_ANNUAL | **partial** (FOMC only) | yes | `reports/stage_e2b_release_calendar.json` (2019-05-01..2026-06-21; 95 HE instants in the search window, E.11). 2010-2019: `reports/stage_e14_cal_releases.json` holds FOMC, NGS and WPSR only (2010-06-01..2019-05-31). No 2010-2019 WASDE or Crop Production calendar was found on disk. [shared, see shared/macro_calendars.md and shared/grains_class_notes.md] |
| g16_month_end | none | livestock trade dates | yes | yes | both calendars |
| g17_nq, g17_zn, g17_6e, g17_cl, g17_gc, g17_mbt, g17_mes on HE rows (g17_zc is K6's own lead: not applicable on HE rows) | NQ ZN 6E CL GC MBT MES | each lead's calendar | undetermined here | undetermined here | audited by the lead-root readers; MBT and MES are outside the 17 roots |
| id_root_HE, id_cluster_K6 | none | none | yes | yes | constants |
| k9_anncday | none | EC-K9 | n/a | n/a | MNQ, M2K, MYM rows only |

Public limit facts for k6_limitcont_dir's backward window (for the lead; not a ruling):
- CME Submission 15-306 (cftc.gov, effective 2015-08-31), Rule 15202.D: "There shall be no trading at a price more than $.030 per pound above or below the previous day's settlement price ... In the event that any of the first three listed contract months settle at limit, the daily price limits for all contract months shall expand to $0.045 per pound on the next Business Day."
- CME Submission 20-112 (cftc.gov, filed 2020-02-27) quotes the same text as "15202. TRADING SPECIFICATIONS (up to and including April 10, 2020)".
- So both filings that bracket 2017-07..2019-04 state an initial limit of $0.030, i.e. 120 ticks. One search found no 2016-2019 amendment; that check was not exhaustive. A backward table could be built from these two primary filings. Whether to build it is the lead's decision.
- Flag for the frozen 2019-2024 table: 20-112 asks to "adjust the current daily price limits of the Contract to $3.75/cwt." from trade date 2020-04-13 ("commencing April 13, 2020"). The frozen LIMIT_PERIODS encodes $0.03 for 2020-04-02..04-21 ("bracketed") and $0.0375 from 04-22. If CFTC approved 20-112 as filed, then 2020-04-13..04-21 carries the wrong L. The member's exact-L test would then miss a $0.0375 limit settle and could mis-flag a $0.03 move. The approval date was not verified.
- Note: Hogs and Pigs, Cold Storage and the LMR reports are not on HE's D8 release list, so g13-g15 on HE rows never mark them.

## 3. Proposed features

None. The reasons:
- E1 (ROD -> LH) is null on lean hogs, in and out of sample.
- E2 (SLH -> LH) has negative R2_OOS. Its rule (entry 12:35, exit 13:05) also differs from t4 = 12:03 with exit at F = 13:03.
- E3 is unsized and settle-to-settle. E4's continuation is realized at the next open, and its intraday reversal leg is defined with hindsight. The limit idea is already in the library as k6_limitcont_dir.
- E5-E7 carry no sized return effect.
- No published rule therefore gives an expected gross per trade from an entry at t1-t4 that can be set against the 2.95-tick (1.5x of 1.965) hurdle.

## 4. NQ only

n/a

## 5. Fetch log, terms read, budget notices

Fetch log (UTC; sha256 in the JSON):

| UTC | URL | Saved | Status |
|---|---|---|---|
| 17:38:35 | https://www.cftc.gov/robots.txt | pages/HE/cftc_robots.txt | ok |
| 17:38:54 | https://www.cftc.gov/filings/ptc/ptc030220cmedcm002.pdf (CME 20-112) | ptc030220cmedcm002.pdf (+ .txt) | ok, sha256 eaf18961... |
| 17:38:58 | https://www.cftc.gov/filings/ptc/ptc071715cmedcm001.pdf (CME 15-306) | ptc071715cmedcm001.pdf (+ .txt) | ok, sha256 41aed870... |
| 17:39:53-17:40:21 | api.openalex.org (5 searches from 2015, 5 DOI records) | openalex/*.json | ok (metadata only) |
| 17:41:06 | https://onlinelibrary.wiley.com/robots.txt | wiley_robots.txt | ok |
| 17:41:12-17:41:28 | https://onlinelibrary.wiley.com/terms-and-conditions (curl 403; scrapling get challenge; scrapling fetch ok) | wiley_terms.html, wiley_terms.md | read terms only |
| n/a | Wiley PDFs for AJAE 2021, AJAE 2022, JFM 2019 | not fetched | terms-forbid |
| 17:41:52-17:42:36 | ideals.illinois.edu robots, item 125160, about; guides.library.illinois.edu IDEALS guide and Access and Use Policy | ideals_*.html | ok |
| 17:42:46 | https://www.ideals.illinois.edu/items/125160/bitstreams/411014/data.pdf | he_2022_dissertation_ideals.pdf (+ .txt) | ok, sha256 e0624529... |
| 17:44:04-17:44:07 | esmis.nal.usda.gov robots; NASS Dec. 2018 notice (.txt) | esmis_robots.txt, nass_dec2018_hogs_reschedule.txt | ok, sha256 ddb80a1f... |
| 17:44:20-17:44:23 | uscode.house.gov robots; section 1635j | uscode_robots.txt (page: server error, deleted) | blocked |
| 17:44:30 | law.cornell.edu robots | law_cornell_robots.txt | not used further |
| 17:44:40-17:45:06 | govinfo.gov robots; USCODE-2024 title 7 sec. 1635j | govinfo_robots.txt, usc_7_1635j.htm | ok, sha256 9208a0fb... |

On-disk sources grepped, not fetched: Baltussen et al. (`reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md`, sha256 18cb436e...) and the E.13 CFTC web policy copy.

Terms read:
- cftc.gov: robots "Allow: /" for all, with "Content-Signal: search=yes,ai-train=no,use=reference" (no ai-input signal). Web policy: "Government information at the CFTC website is in the public domain." Allowed; this is the E.14/E.16 precedent for CME filings.
- Wiley Online Library: "Users shall not: * Use any scraper, crawler, spider, robot or other automated means of any kind to access or copy this site ..." and no AI ingestion. Terms forbid; no article fetched.
- IDEALS: robots does not disallow /items. Access and Use Policy: "A primary mission of IDEALS is to provide access ... IDEALS disseminates its contents through as many means possible". Allowed; used for quotation.
- ESMIS (USDA), govinfo.gov, uscode.house.gov: robots allow the paths used; these are federal works.
- OpenAlex: CC0 metadata, used for discovery only.

Budget notices: 17 WebSearch calls used (budget about 50); no over-budget notice. One hook cost notice ("COST CRITICAL ... Informational only", about 17:45 UTC) was treated as informational. Firecrawl was not used.

## 6. Unfinished and unverified

- Janardanan, Qiao, Rouwenhorst (JFM 2019) [secondary-only] and the published AJAE versions of He and Serra (2022) and He, Serra, Garcia (2021) were not read, because Wiley's terms forbid it. E3-E5 come from the IDEALS dissertation (working versions); the published numbers may differ. The dissertation's chapter 3 also holds the live cattle rows (Tables 3.1, B.5, B.6); the LE reader can grep `pages/HE/he_2022_dissertation_ideals.txt` instead of re-fetching it.
- Aalto thesis lean-hog rows and livestock-class notes: cited only, not read ([shared, see shared/aalto_thesis_notes.md]; [shared, see shared/livestock_class_notes.md]).
- WASDE and Crop Production calendars 2017-07..2019-04: none on disk, so g13-g15 are partial in the backward window unless the ZC or RTY reader finds one.
- HE limit history 2015-2020: only one search for an intermediate amendment. The approval and effective date of CME 20-112 were not verified, so the frozen-table flag for 2020-04-13..04-21 is open.
- Undetermined: whether any Hogs and Pigs release fell at noon ET (inside the session) in either window. NASS calendars were not read; the 2015 noon practice was seen only in a search snippet [unverified].
- No post-2015 intraday study of lean-hog responses to LMR or Hogs and Pigs reports was found (6 searches and OpenAlex). That is unknown, not rejected.
- Deviation: one `grep -l` over `data/` for "wasde" printed four script file names under `data/vendor/release_pages/commodity_scripts/`. Only the names were shown; no contents and no data store were opened.
