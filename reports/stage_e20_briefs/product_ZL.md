# Stage E.20 Part A: product reader ZL (CBOT soybean oil; vehicle ZL)

Reader: ProductReader-ZL-OpusHigh, 2026-10-11 (all times UTC in this file, as the fetch log requires; 17:36Z to 17:50Z = 10:36 to 10:50 PDT).
Machine-readable copy: `reports/stage_e20_briefs/product_ZL.json`. Raw pages: `reports/stage_e20_briefs/pages/ZL/`.
Root facts (root table): tick $6.00 (0.01 c/lb x 60,000 lb); D8 RT wall 2.675 ticks = $16.05; 1.5x hurdle 4.01 ticks = $24.08;
grains group O 08:30, C 13:15, F 13:18 CT; t1 09:00, t2 10:00, t3 11:00, t4 12:18.

bp conversion used throughout: 1 tick = 0.01 c/lb, so bp per tick = 100 / P (P in c/lb). Public price level: IMF global
soybean-oil price via FRED `PSOILUSDM` (saved `fred_PSOILUSDM.csv`), mean 39.52 c/lb over 2010-07..2019-04 (2.53 bp per tick)
and 50.75 c/lb over 2019-05..2024-02 (1.97 bp per tick). This is a proxy for the price level, not the CBOT ZL price. The D8 wall is
therefore about 6.8 bp (backward window) and 5.3 bp (search window); the 1.5x hurdle about 10.1 bp and 7.9 bp.

## 1. Evidence

| ID | Effect | Rule | Hold | Gross per trade | Gross/net | Sample | Decay evidence | Source | Grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Market intraday momentum, soybean oil's own row (BO) | r_LH on r_ROD (prior close to close-30; last half hour of 08:30-13:20 CT) | last 30 min | none: slope 0.03 (x100), t 0.08, no effect to size | gross | BO 1982-07-06..2020-05-01, 9,458 days, 1-min | in-sample null: R2 -0.01%, R2_OOS -0.06%. Pooled "Softs" (12 ags incl. BO): b_ROD 0.65 (t 2.16), R2_OOS -0.01% | Baltussen, Da, Lammers, Martens, JFE 142 (2021), Table B3 Panel B, on-disk copy | primary |
| E2 | Intraday crush cointegration (ZS, ZL, ZM) in the day session, stronger on USDA days | none (econometric, no trading rule) | n/a | not published | unknown | ZS/ZL/ZM CME MBO, all of 2015 (243 days), 1-min | one year; no OOS | Zhou, Bagnarosa, Gohin, Pennings, Debie, J. Commodity Markets 30 (2023) 100314, CC BY, https://edepot.wur.nl/629433 | primary |
| E3 | Biofuel-policy events (EPA RVO, CARB quarterly, Reuters "sources" leaks) raise soybean oil absolute daily returns, event day +0.59%, next day +0.62%, 1.21% over two days | none tradable: unsigned close-to-close; EPA events and leaks unscheduled | 1 day | none: changes in absolute return, no direction | gross | daily Bloomberg nearby, 2019..2025-02; 36 events 2021-2025 | none; 2021-2025 only | Avileis and Swanson, NCCC-134 2025, farmdoc PDF | primary |
| E4 | Crush-spread mean reversion from intraday deviations vs the USDA-implied processing relationship; profitable after costs | unknown (abstract only) | unknown | not sized | net | 8,650 days 1990-09..2021-05 | unknown | Abdoh and Chitavi, Int. Rev. Econ. & Finance 101 (2025), paywalled | secondary-only |
| E5 | USDA reports and Dalian soybean oil (not CBOT): minute volatility/volume react at the DCE open; price reactions fade within minutes; weaker for soybean oil in the trade war | none (vol/volume) | n/a | no signed effect | unknown | DCE soybean complex 2011-01..2021-04, minute | trade-war weakening | Hu and Mallory, NCCC-134 2022 / J. Futures Markets 45(11) 2025 | secondary-only (abstract for the numbers; full NCCC text read for scope) |
| E6 | Intraday momentum and reversal on 31 Chinese commodity futures (minute data): intraday versions fail to cover costs | various (abstract only) | intraday | not sized | net | 31 Chinese commodities, minute | after-cost failure | Yang, Goncu, Pantelous, IRFA 60 (2018) 177-196 | secondary-only |

Verbatim quotes (location; saved file and sha256 in the JSON):
- E1 (Table B3 Panel B, row BO; columns bONFH, R2, R2OOS, bTONFH, bM, bSLH, R2, R2OOS, bROD, R2, R2OOS, x100):
  "| BO | -0.80(-1.40) | 0.02 | -0.06 | -0.86(-1.48) | 1.02(1.20) | 2.80(1.22) | 0.06 | -0.36 | 0.03(0.08) | -0.01 | -0.06 |".
  Panel A: "| Softs | 0.25 (0.70) | 0.00 | -0.06 | 0.19 (0.57) | 0.61* (1.70) | 3.50*** (2.62) | 0.09 | -0.14 | 0.65** (2.16) | 0.04 | -0.01 |".
  Sample (Table A, commodities): "| Soybean oil futures | BO | 1982-07-06 | 2020-05-01 | 9458 | 08:30-13:20 | Softs |".
  The paper files BO under "Softs" with all 12 ags. Its Fig. 4(c) OCR gives "| BO | 5.0 | -1.7 |" (LETF size, t), low confidence; not used.
- E2 (Section 5.1, PDF p. 10): "A high level of cointegration is indeed observed during session 2 trading hours, which fades away
  during session 1. Another interesting result is the stronger intraday cointegration observed on average on USDA announcement
  days, although the number of observations available is limited." (Section 4, PDF p. 8): "The high-frequency data used in this
  study covers the total trading activity of 2015, amounting to 243 trading days."
- E3 (Section 3, p. 10-11): "We calculate absolute returns for all commodities and the crush as the difference between market
  open (i.e., market close of the previous trading day) and market close for a single day." Abstract: "soybean oil futures returns
  increase significantly on announcement days (0.59%) and continue rising the following day (0.62%)". Section 1: "EPA
  announcements are when the EPA proposed or finalized new biofuel mandated volumes. These are unscheduled. CARB reports are
  quarterly reports published every last day of the quarter." (The pdftotext ligature reads "di!erence"; quoted as printed text.)
- E4 (IDEAS abstract): "Our simulations demonstrate that trading strategies based on these findings would have been profitable,
  even after accounting for transaction costs. This analysis is based on 8650 trading days from September 1990 to May 2021."
- E5 (JFM 2025 abstract, IDEAS): "On average, price reactions dissipate within a few minutes, while increased trading volume can
  last up to an hour. ... During the trade war period, USDA reports had reduced impact on soybean no. 1 and soybean oil futures but
  remained influential on soybean no. 2 and soybean meal futures."
- E6 (IDEAS abstract): "the intra-day strategies used cannot generate sufficiently enough high excess returns to cover the
  excessive costs due to the higher frequency of trading."

Reading of decay and costs.
- The one sized, ZL-specific intraday return test since 2015 is Baltussen et al.'s BO row, and it is a null. ROD -> LH has no
  predictive power for soybean oil (t 0.08, negative OOS R2) over 1982-2020. The class effect for ags is weak (Softs t 2.16,
  OOS R2 below zero). The planning brief puts the commodity portfolio at about 1.7 bp per trade (its own derivation;
  [shared, see shared/baltussen_notes.md]). That is 0.67 ticks at 39.5 c/lb and 0.86 ticks at 50.75 c/lb, 0.25x to 0.32x the
  2.675-tick D8 wall, so the class figure would not clear the cost wall on ZL even if it held there.
- The other root-specific work is about volatility, cointegration or daily moves, not signed intraday returns:
  - E2 is one year of crush cointegration with no rule;
  - E3 is unsigned and daily, and its events are unscheduled;
  - E5 and E6 are Chinese-venue results, and E6 is an after-cost failure.
- E4 is the only after-cost profitability claim. It needs ZM and is unread beyond the abstract.
- No published, sized, post-2015 intraday direction effect for CBOT soybean oil was found.

## 2. Feature availability (ZL's rows, and ZL as a leg)

Calendars used for the decision:
- `data/calendars/hist2010/grains.json`: 2010-06-01..2019-05-31; 2,269 trade dates; 0 unsourced; CME evidence; 201 verbatim
  checks, 0 failures; sha256 1197496f...
- `data/calendars/grains.py`: 2019-05-01..2026-06-19; sha256 a685731b...
- The frozen release calendar `reports/stage_e2b_release_calendar.json` (sha256 839f2437...).
- E.14's `reports/stage_e14_cal_releases.json` (sha256 9a051211...).

Grain session eras (hist2010/grains.json `sessions`):
- 2010-06-01..2012-05-18: Globex 18:00 (d-1) to 07:15, then 09:30 to 13:15. No bars from 07:15 to 09:30.
- 2012-05-21..2013-04-05: Globex 17:00 (d-1) to 14:00.
- 2013-04-08..2015-07-03: 19:00 to 07:45, then 08:30 to 13:15.
- From 2015-07-06: 08:30 to 13:20.

Two clock facts follow for every grain root:
- (a) Under the frozen O = 08:30, there is no bar at t1 = 09:00 or at 08:30 from 2010-07-01 to 2012-05-18.
- (b) F = 13:18 lies after the 13:15 Globex close in 2010-07-01..2012-05-18 and in 2013-04-08..2015-07-03.

The E.16 settlement table also records the 09:30 open until 2013-04-07 (R-S5 analogue; `reports/stage_e16_calendars.md` rows 50-53).

| Feature | Legs | Calendars | 2010-2019 | 2019-2024 | Dates / basis |
|---|---|---|---|---|---|
| cp1_ret | ZL | grain calendar | partial | yes | no 08:59 bar under O=08:30 before 2012-05-21; computable from 2012-05-21; day open 08:30 only from 2013-04-08. First-bar rule (>= 19:00 CT d-1) met in every era |
| cp2_range, cp2_brk | ZL | grain calendar | partial | yes | no bars in [08:30, 08:45) before 2012-05-21 |
| cp3_clv | ZL | grain calendar | partial | yes | needs the 08:30 O bar and a complete [O, C) day: from 2012-05-21 under O=08:30; every era with an era O of 09:30 |
| g01_ret30, g02_ret60, g03_ret120, g04_ret_day, g06_rv60, g07_range, g10_logvol30 | ZL | grain calendar | partial | yes | bars exist at t2, t3, t4 in every era. t1 has no bar 2010-07-01..2012-05-18; g02/g03 at t2 reach back into the break in that era. Normal warm-up at 2010-07 |
| g05_gap | ZL | grain calendar | partial | yes | needs the 08:30 bar of d (absent 2010-07-01..2012-05-18); the 13:14 bar of d-1 exists in every era |
| g08_prev_ret | ZL | grain calendar | partial | yes | close(C-1) - open(O) of the last complete day: same O caveat |
| g09_vol_state | ZL | grain calendar | partial | yes | sigma_X,d from daily [O, C) bars: same O caveat; 120-date warm-up |
| g11_t_index, g12_dow | none | none | yes | yes | no data dependence |
| g13_min_to_rel, g14_min_since_rel, g15_rel_day | none | ZL's D8 list: FOMC, WASDE, CROP, CROP_ANNUAL | partial (FOMC only) | yes | See the note after this table. FOMC part: [shared, see shared/macro_calendars.md] |
| g16_month_end | none | grain calendar | yes | yes | both group calendars cover their windows (hist2010 0 unsourced) |
| g17_nq, g17_zn, g17_6e, g17_cl, g17_gc | the lead | the lead's calendar | undetermined here | undetermined here | apply on ZL rows; audited by product_NQ/ZN/6E/CL/GC |
| g17_zc | ZC | grain calendar | n/a | n/a | ZL's own cluster lead: not applicable on ZL rows by construction (`ml_route_v2/signals/generic.py` `_lead`) |
| g17_mbt, g17_mes | MBT, MES | | no | yes (MBT from 2021, MES from 2019) | legs outside the 17 roots (brief section 7) |
| k6_crushgap_gap (ZL as leg) | ZS, ZM, ZL | GRAIN_FULL_SESSIONS, GRAIN_TRADE_DATES (k6/_calendar.py, 2019-05-01..2026-06-18) | partial | yes | See the note after this table |
| r_ROD, ratio (prompt additions, reference only) | ZL | grain calendar, C 13:15 | yes | yes | the prior close at C exists in every era |

Note on g13 to g15 (release features):
- 2019-2024: the frozen calendar has ZL rows for CROP 85, WASDE 85, FOMC 57 and CROP_ANNUAL 7 (2019-05..2026-06).
- 2010-2019: E.14's calendar holds NGS, WPSR and FOMC only (FOMC: 72 rows, 2010-06-23..2019-05-01). It has no WASDE or Crop
  Production rows. E.16 review F-11 says the same ("CROP, WASDE, CROP_PROGRESS" have no 2010-2019 rows).
- If those rows are ever built, the USDA notice of 2012-09-19 gives the time regime (Wayback copy, quoted): "will begin issuing
  several major USDA statistical reports at 12:00 noon EDT beginning in January 2013. The current USDA release time of 8:30 a.m.
  EDT will remain in effect until January 1, 2013. USDA statistical reports affected are: World Agricultural Supply and Demand
  Estimates, Acreage, Crop Production, Grain Stocks, Prospective Plantings, and Small Grains Summary."
- So the releases came at 07:30 CT until 2012, which falls inside the 07:15-09:30 Globex break before 2012-05-21, and at 11:00 CT
  from 2013-01-11.

Note on k6_crushgap_gap:
- It applies on ZS rows, not ZL rows.
- Its leg ZM is not one of the 17 roots, which fails the F6 leg rule regardless of calendars.
- The member's calendar tables start 2019-05-01. A 2010-2019 version would have to come from hist2010/grains.json.
- The 08:30 open bars it reads are absent 2010-07-01..2012-05-18.
- ZL and ZM bars exist from 2010-07 (E.16 windows: 106 chunks each, from the E.17 purchase).

Listing: CBOT soybean oil traded throughout both windows. Its window starts 2010-07-01 (`reports/stage_e16_windows.json`), and
no R-S4 restriction applies.

## 3. Proposed features

None. Reasons, candidate by candidate:
- ROD -> LH on ZL: the published BO row is a null (E1). r_ROD and its ratio are already added by the prompt.
- Intraday crush reversion (E2, E4; Rechner-Poitras 1993 is the K6-crushgap source and predates 2015): every published form
  needs ZM. ZM is outside the 17 roots, so it fails the leg rule. A ZS-ZL-only variant is not published, and building one would
  mean designing a rule without a source.
- Biofuel-policy events (E3): EPA decisions and press leaks are unscheduled, so no calendar exists in advance. The published
  effect is unsigned and daily. CARB quarter-end dates are known in advance, but the paper gives no separate signed CARB effect.
- Crude oil to soybean oil lead-lag: no intraday, sized source was found (CME commentary on cmegroup.com describes yearly or daily
  co-movement; not fetched, [unverified]). The CL 60-minute return already enters ZL rows as `g17_cl`.
- WASDE or Crop Production windows for ZL: no ZL-sized published effect was found. The 2010-2019 grain-report calendar does not
  exist on disk, so the availability rule fails today.

## 4. NQ only

n/a.

## 5. Fetch log, terms read, budget notices

Fetch log (UTC; sha256 of every saved file is in the JSON `fetch_log`):

| UTC | URL | Saved as | Status |
|---|---|---|---|
| 17:37:05 | farmdoc.illinois.edu/robots.txt; ageconsearch.umn.edu/robots.txt | `farmdoc.illinois.edu_robots.txt`, `ageconsearch.umn.edu_robots.txt` | ok |
| 17:37:13 | farmdoc .../conf_2025/pdf/Aveleis_Swanson_NCCC134_2025.pdf | `aveleis_swanson_nccc134_2025.pdf` (sha256 a44fbcff...) | ok |
| 17:37:19, 17:37:26, 17:37:59 | ageconsearch.umn.edu records 329790 and 235772 (curl, then scrapling get and fetch) | none | blocked (AWS WAF, HTTP 202) |
| 17:38:12 | farmdoc .../conf_2022/pdf/Hu_Mallory_NCCC-134_2022.pdf | `hu_mallory_nccc134_2022.pdf` (00743c4e...) | ok |
| 17:38:54 | ideas.repec.org robots; Abdoh-Chitavi record | `ideas_robots.txt`, `ideas_abdoh_chitavi_2025.html` (9204c6f2...) | ok |
| 17:40:32 | doaj.org robots; Energy Reports 2022 article | `doaj_robots.txt` | article blocked (Cloudflare 403) |
| 17:40:47 | edepot.wur.nl robots; https://edepot.wur.nl/629433 | `edepot_robots.txt`, `zhou_etal_2023_jcm.pdf` (908bb3f4...) | ok |
| 17:41:21 to 17:41:30 | three IDEAS records (riibaf 2020, finana 2018, jfutmk 2025) | `ideas_*.html` | ok |
| 17:41:53 | usda.gov release-time PDF and robots.txt | none | blocked (Akamai 403) |
| 17:41:53 to 17:42:27, not stamped | archive.org availability API | none | throttled (429) |
| 17:42:27 | web.archive.org/web/20201018081741id_/...USDA_Release_time_change_9_19_12.pdf | `usda_release_time_change_2012-09-19.pdf` (f1b8003f...) | ok |
| 17:42:51 to 17:43:11 | fred robots; fredgraph.csv?id=PSOILUSDM | `fred_robots.txt`, `fred_PSOILUSDM.csv` (d05d8678...) | ok |
| 17:44:30 | fred.stlouisfed.org/legal/; farmdoc home (terms links) | `fred_legal.html`, `farmdoc_home.html` | ok |
| local | Baltussen on-disk copy (grep only) | `reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md` (18cb436e...) | ok |

Terms read:
- farmdoc: robots Crawl-delay 10, only /lucee disallowed. The site links the University of Illinois copyright page (not fetched).
  Requests were spaced more than 10 s apart. The Hu & Mallory PDF states "Readers may make verbatim copies of this document for
  non-commercial purposes".
- AgEcon Search: robots allow /record/. The WAF blocks automated reads; stealthy-fetch was not used. The same papers were taken
  from farmdoc's NCCC-134 archive.
- IDEAS: robots disallow /cgi-bin/ only.
- DOAJ: robots allow /article/; Cloudflare blocked the read.
- WUR edepot: Crawl-delay 600, so one request was made. The article is CC BY.
- usda.gov: Akamai denies even robots.txt. The notice was read from Wayback, which is permitted (not cmegroup.com).
- FRED: legal page, "may be used without permission, provided you do not engage in any prohibited use", with citation.
- No cmegroup.com page was fetched.

Budget notices: none. 22 WebSearch calls were used of about 50. No Firecrawl call was made. No usage or over-budget notice
appeared.

## 6. Unfinished and unverified items

- Abdoh and Chitavi (2025): full text unread (paywall; no preprint found). The rule, bar size and per-trade size are unknown
  [secondary-only].
- Energy Reports (2022), information flow between palm oil, soybean oil and crude oil: blocked. Its data frequency is unknown
  [unverified].
- Crude-to-soybean-oil lead-lag: only CME commentary (not fetched; cmegroup.com is barred) [unverified].
- Hu & Mallory and Yang et al. numbers come from abstracts; both concern Dalian or other Chinese venues, not CBOT ZL.
- Grains-class evidence (WASDE windows, Adjemian-Irwin, Anderson-McKenzie-Noyes 2024, Joseph-Garcia, Janardanan et al. limit
  days) is left to ZC (`shared/grains_class_notes.md`), and the Aalto per-class notes to ZN (`shared/aalto_thesis_notes.md`).
  The macro calendars are left to RTY (`shared/macro_calendars.md`). None of these files was on disk when I wrote this, so
  each is cited by path only.
- G17 rows are left undetermined here by design.
- The FRED IMF series is a proxy for the price level, used only for the bp conversion. CBOT ZL settlement prices were not used
  (no data store opened).
