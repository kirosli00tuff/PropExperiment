# Stage E.20 Part A: product reader ZS (CBOT soybeans; vehicle ZS)

Reader: ProductReader-ZS-OpusHigh. Brief: `reports/stage_e20_briefs/brief_partA_shared.md` (section 7: root-specific
evidence only; class evidence is the ZC reader's, `shared/grains_class_notes.md`). Raw pages:
`reports/stage_e20_briefs/pages/ZS/` (fetch log `pages/ZS/fetch_log.tsv`). No data store was opened; no bar was read.

Vehicle facts used (root table): ZS, tick 0.25 cents/bu = $12.50; D8 round-trip wall 1.644 ticks = $20.55; grains
O 08:30, C 13:15, F 13:18 CT; decision times t1 09:00, t2 10:00, t3 11:00, t4 12:18.

## 1. Evidence

No study since 2015 gives a sized, intraday, directional, bar-only rule on CBOT soybeans that clears the D8 wall.
The rows below include the nulls.

| ID | Effect | Rule (as published) | Hold | Gross per trade | Gross/net | Sample | Decay evidence | Source | Grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Market intraday momentum (ROD -> LH) on soybeans: **null**. First half-hour -> last half-hour: **reversal**, but OOS R2 negative | r_LH on r_ROD (return from prior close to 30 min before close); also r_LH on r_ONFH. SY trading hours 08:30-13:20 | last 30 min (12:50-13:20 CT) | beta_ROD = -0.05 x 1e-2 (t -0.13): ~0 bp per 1% r_ROD. beta_ONFH = -1.17 x 1e-2 (t -2.17): -1.17 bp per 1% r_ONFH; R2_OOS -0.04% | gross | SY (CBOT soybeans), Tick Data, 1-min, 1982-07-06..2020-05-01 (Table B3: Apr 1981..May 2020 for the panel) | negative OOS R2 for both slopes on SY | Baltussen, Da, Lammers, Martens (2021), JFE 142, Table B3 Panel B (on-disk copy) | primary |
| E2 | WASDE (world ending stocks) news -> soybean price reaction **keeps growing after 30 min** | event regression of ln(P_end/P_start) on news = mean ln(WASDE/analyst forecast); windows from release (or the open if released pre-open) to +10 min, +30 min, day close | 10 min / 30 min / to close | soy beta: 10 min -0.028 (0.027), 30 min -0.061** (0.031), day -0.124** (0.049). Upper bound for the 30 min -> close leg with perfect news sign: 14.6 bp (see derivation in section 3) | gross | CME nearby corn and soybean futures, 2010-2021, 122 WASDE events (26% "early release", i.e. pre-2013 07:30 CT releases) | none (single sample, conference paper, no OOS) | Anderson, McKenzie, Noyes (2024), NCCC-134 proceedings, farmdoc | primary (conference paper, not peer reviewed) |
| E3 | USDA report windows in ZS: volatility spike, **no systematic under- or overreaction** in returns | 15-second returns, 15 min before to 60 min after WASDE, CP, GS, AC, PP releases; trading-hour vs non-trading-hour releases | up to 60 min | none (no directional effect found) | n/a | ZS nearby, CME Globex time and sales, June 2010-May 2014; 30 non-trading-hour and 29 trading-hour releases | n/a | Joseph and Garcia (2016), AAEA selected paper, AgEcon 10.22004/ag.econ.235772 | primary |
| E4 | Crush-spread intraday deviations from the USDA-implied processing relationship mean-revert; "profitable after transaction costs" | not stated in the abstract; full text paywalled | not stated | not stated | net (claimed) | 8,650 trading days, Sep 1990-May 2021 | not stated | Abdoh and Chitavi (2025), Int. Rev. Econ. Finance 101, 104186 | secondary-only (abstract) |
| E5 | Soybean-complex intraday cointegration depends on liquidity and time of day | VECM on 1-min LOB snapshots of ZS, ZL, ZM | n/a | none (no trading rule) | n/a | CME, all of 2015 (243 trading days); session 2 = 08:30-13:20 | n/a | Zhou, Bagnarosa, Gohin, Pennings, Debie (2023), J. Commodity Markets 30, 100314 (CC BY) | primary |
| E6 | Crop Progress "good+excellent" rating vs next-day November soybean price: -0.45% per +1% rating | log price level at the next day's 13:30 close regressed on log condition and a trend (levels, not returns) | next day close (report at 4 p.m. ET Monday, after the close) | not a per-trade figure; needs the released CPR value | n/a | November ZS, weeks 25-40, 1995-2018, 448 reports | none | Bethlem, Lima, Lima (2023), RESR 61(2) | primary (SciELO full text) |
| E7 | Dalian soybean (No.1): first 30 min -> last 30 min **momentum** (opposite sign to E1's CBOT SY row) | r_last30 on r_first30 (excluding overnight) | last 30 min | slope 0.073: 7.3 bp per 1% first-30 return; insignificant once the overnight return is included | gross | DCE soybean No.1, 2002-07-01..2013-06-27, 2,245 days | n/a | Jin, Kearney, Li, Yang (2020), J. Futures Markets 40(4) 632-650; read as MPRA WP 97134 | primary (WP copy); not the vehicle |
| E8 | Chinese soybean complex reacts to USDA reports at the Dalian open; WASDE alone minimal | event study, intraday | minutes | none | n/a | Dalian, Jan 2011-Apr 2021 | n/a | Hu and Mallory (2025), JFM 45(11) 2109-2127 | secondary-only (abstract); not the vehicle |
| E9 | CBOT corn: real-time USDA releases give wider ranges, spikes moderate quickly; media-lockup removal (2018) adds no volatility | daily and intraday volatility | n/a | none | n/a | CBOT corn | n/a | Adjemian and Irwin (2020), J. Commodity Markets 19, 100110 | secondary-only (abstract); corn: class row, see ZC |

Verbatim quotes (location; file under `pages/ZS/` unless stated):
- E1, Table B3 Panel B, SY row (`reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md` line 3776,
  sha256 18cb436e...0465): "| SY | -1.17**(-2.17) | 0.06 | -0.04** | -1.23**(-2.26) | 1.68**(2.01) | 3.11(1.19) | 0.15 | -0.45 | -0.05(-0.13) | -0.01 | -0.07 |";
  column header (line 3762): "| βONFH | R2(%) | R2OOS(%) | βTONFH | βM | βSLH | R2(%) | R2OOS(%) | βROD | R2(%) | R2OOS(%) |";
  caption: "Adjusted R2, R2OOS, and slope coefficients are multiplied by 100."; Table A3 (line 3301): "| Soybean futures | SY | 1982-07-06 | 2020-05-01 | 9462 | 08:30-13:20 | Softs |".
  The pooled "Softs" row (line 3715): "| Softs | 0.25 (0.70) | ... | 0.65** (2.16) | 0.04 | -0.01 |" (R2_OOS of ROD -0.01).
  The NQ reader holds the full Baltussen read ([shared, see shared/baltussen_notes.md]).
- E2 (`anderson_mckenzie_noyes_2024.txt`): line 197 "Soy News -0.028 -0.061** -0.124**"; line 154 "Soybean News 122 0.001 0.029 -0.070 0.110";
  line 156 "Early Release 122 0.262 0.442 0 1"; lines 190-191 "By the end of the release day, the corn reaction doesn't change much but the soybean price reaction grows after 30 minutes.";
  line 149 "The data in out study spans from 2010 to 2021."; methods: "The time window began when the WASDE report was released or the opening price if the report was released before the market opened. For this paper we chose time windows of 10 minutes, 30 minutes, and the report day close."
- E3 (`joseph_garcia_2016_aaea.txt` lines 55-61, abstract): "releases during trading hours result in a smaller volatility spike which extends for five to six minutes at a higher magnitude. ... Return correlations provide little evidence to support systematic under- or overreaction in prices regardless of when the report is released, reflecting the efficiency of the market."
  Release times (lines 70-72): "In January 2013, USDA officially shifted these reports releases to 11:00 a.m., formalizing trading hour re- leases." Sample (lines 145-146): "The announcement data reflect WASDE, CP, GS, AC, and PP reports from June 2010-May 2014."
- E4 (`ideas_abdoh_chitavi_2025.html`, abstract): "no study has examined how intraday deviations of soybean products from the processing relationship reflected in USDA estimates affect the soybean crush spread. ... Our simulations demonstrate that trading strategies based on these findings would have been profitable, even after accounting for transaction costs. This analysis is based on 8650 trading days from September 1990 to May 2021." Full text: "Full text for ScienceDirect subscribers only" (not fetched).
- E5 (`zhou_etal_2023_jcm.txt` lines 42-44): "Our analysis further suggests that the presence of cointegration among assets is related to the time of day and the contract maturities traded at a given time."; line 587: "The high-frequency data used in this study covers the total trading activity of 2015, amounting to 243 trading days."
- E6 (`bethlem_etal_2023_resr.txt`, abstract): "a 1% increase in soybean crop area evaluated as “good” and “excellent” (Condition variable) in the weekly CPR reduced soybean futures contract prices by 0.45% the day following the report’s release"; method: "the CPR’s impact on prices was determined using the natural logarithm of soybean futures prices at the 1:30 p.m. CBOT closing on the day following the report’s release as the model’s dependent variable."
- E7 (`jin_etal_mpra_97134.txt` lines 621-623): "first 30-minute returns positively predict the last 30-minute returns for all four contracts with a slope of 0.073 for soybean"; line 748: "the result for soybean is rendered insignificant if we include the overnight return into the first 30-minute return."
- E8 (`ideas_jfm_2025_v45i11.html`): "The results show that the strongest price and volume reactions occur immediately after the market opens. On average, price reactions dissipate within a few minutes".
- E9 (`ideas_jocoma_v19_2020.html`): "these volatility spikes moderate fairly quickly, and that the CBOT corn market has a more difficult time distinguishing important news events."

Reading of decay and costs.
- The one class-wide intraday-momentum source with a soybean row (E1) finds no ROD -> LH effect on soybeans and a
  first-half-hour reversal that fails out of sample. The pooled "Softs" ROD slope is significant in sample (t 2.16) but
  its OOS R2 is negative. No post-2020 soybean figure exists in any source read.
- The Aalto thesis has no commodities ([shared, see shared/aalto_thesis_notes.md], lines 16-18): it is not soybean evidence.
- Report windows (E2, E3, E9): volatility is well documented; direction is not, except E2's conditional result, which
  needs the analyst-survey surprise (not a bar, not a calendar). E3 finds no systematic return pattern after releases.
- The crush-spread literature since 2015 (E4, E5) gives no open, sized intraday rule. The program's crush member
  (K6-crushgap-01) rests on Rechner and Poitras (1993), pit-era 1978-1991 data, outside this brief's window.
- Costs: ZS's D8 wall is 1.644 ticks. At an assumed $12.00/bu that is 0.41 cents/bu, about 3.4 bp of notional
  ([unverified assumption]: the $12.00 level is a round figure, not read from a fetched page; at $9 it is 4.6 bp,
  at $15 it is 2.7 bp). A 1.5x hurdle needs about 5 bp gross per trade.

## 2. Feature availability (V2.3 features reading ZS bars or applying on ZS rows)

Calendars used for the facts (dates and source grades from the files; no bar read):
- Grains group calendar 2010-2019: `data/calendars/hist2010/grains.json` (= `reports/stage_e14_cal_grains.json`),
  coverage 2010-06-01..2019-05-31, 128 entries all evidence "cme", 0 unsourced, verbatim check 201/0 failures,
  every year 2010-2019 "complete_exception_list": true. Session eras (ZS): 2010-06-01..2012-05-18 Globex 18:00-07:15
  plus day 09:30-13:15; 2012-05-21..2013-04-05 Globex 17:00-14:00 (day 09:30-14:00); 2013-04-08..2015-07-03
  19:00-07:45 plus 08:30-13:15; 2015-07-06..2019-05-31 19:00-07:45 plus 08:30-13:20.
- Grains group calendar 2019-2026: `data/calendars/grains.py`, CALENDAR_COVERAGE 2019-05-01..2026-06-19, every status
  "cme" except MLK 2023 "secondary".
- K6 member tables: `strategy/members/k6/_calendar.py` (GRAIN_FULL_SESSIONS, GRAIN_TRADE_DATES) TABLE_RANGE
  2019-05-01..2026-06-19; `strategy/members/k6/_wasde.py` WASDE_RANGE 2019-05-01..2026-06-19 (58 dates in the
  search window), generated from `reports/stage_e2b_release_calendar.json`.
- Release calendars: frozen `reports/stage_e2b_release_calendar.json` (2019-05-01..2026-06-21) lists ZS on WASDE,
  CROP, CROP_ANNUAL (12:00 ET) and FOMC rows: 158 ZS rows in 2019-05-06..2024-02-29. E.14's
  `reports/stage_e14_cal_releases.json` (2010-06-01..2019-05-31) holds NGS, WPSR and FOMC only (FOMC 72 rows, ZS
  listed); **no WASDE, Crop Production or other USDA row exists for 2010-2019 anywhere in the repo** (grep of
  `reports/`, `data/calendars/`, `screening/`).
- E.16 settlement table (`reports/stage_e16_settlement.md` rows 50-53): grains S 13:15, except 14:00 on
  2012-06-25..2013-04-07; O 09:30 until 2013-04-07, 08:30 from 2013-04-08.
- Listing/windows: `reports/stage_e16_windows.json`: ZS, ZM, ZL all start 2010-07 (ZM's 2010-2019 bars are in the
  E.17 21-root purchase plan).

Clock fact that bounds every row: in 2010-07-01..2012-05-18 the 09:00 t1 lies in the Globex pause (07:15-09:30), so no
t1 entry bar exists; t2, t3, t4 exist. In 2012-05-21..2013-04-05 08:30-09:30 is Globex-only trading (pit opened 09:30).

| Feature | Legs | Calendars / literals | 2010-2019 | 2019-2024 | Dates / basis |
|---|---|---|---|---|---|
| cp1_ret | ZS | group calendar; D6 O 08:30; grain first bar >= 19:00 CT d-1 | partial | yes | close(08:59) absent 2010-07-01..2012-05-18 (pause 07:15-09:30); exists from 2012-05-21 |
| cp2_range, cp2_brk | ZS | group calendar; OR [08:30, 08:45) | partial | yes | OR bars absent 2010-07-01..2012-05-18; exist from 2012-05-21 |
| cp3_clv | ZS | group calendar (port-complete days) | yes | yes | day H/L/C exist in every era; era session edges differ (C 14:00 in 2012-05-21..2013-04-05) |
| k6_crushgap_gap | ZS, **ZM**, ZL | k6 GRAIN_FULL_SESSIONS, GRAIN_TRADE_DATES (2019-05-01..2026-06-19 only); 08:30 opens of d, 13:14 closes of d-1; GPM = 0.022 P_ZM + 11 P_ZL - P_ZS | partial | yes | ZM is not one of the 17 roots (fails the F6 leg rule regardless). k6 literal tables do not extend before 2019-05-01 (derivable from hist2010 grains, not built). 08:30 bars absent 2010-07-01..2012-05-18. 13:14 bar exists in all eras |
| k6_wasdepre_drift | ZS (also ZC rows) | WASDE_DATES (2019-05-10..2026-06-11); GRAIN_FULL_SESSIONS; drift 08:30 open -> 10:29 close | no | yes | no WASDE calendar for 2010-2019 on disk; and before Jan 2013 WASDE came at 07:30 CT, pre-open (E3 quote), so the 11:00 pre-release window did not exist 2010-07..2012-12 |
| k6_wasdepost (EXCLUDED; ZC rows only) | ZC | WASDE_DATES | no | n/a now | not on ZS rows. Fact for the lead: its exclusion reason (known 11:15 CT, after the last grain decision 11:00) no longer holds at t4 = 12:18; same 2010-2019 calendar gap |
| g01_ret30, g02_ret60, g03_ret120, g04_ret_day | ZS | group session intervals (SG-3) | yes | yes | lookbacks crossing the pause are "not applicable" by SG-3 (07:15-09:30 in 2010-07..2012-05; 07:45-08:30 from 2013-04) |
| g05_gap | ZS | C 13:15 (D6), group early halts | yes | yes | 13:14 bar exists in every era; not applicable after early-halt dates (SG-4) |
| g06_rv60, g07_range, g08_prev_ret, g09_vol_state, g10_logvol30 | ZS | none beyond the group calendar | yes | yes | bars only |
| g11_t_index, g12_dow | none | clock | yes | yes | t1 rows absent 2010-07-01..2012-05-18 |
| g13_min_to_rel, g14_min_since_rel, g15_rel_day | ZS rows | ZS's D8 release list: WASDE, CROP, CROP_ANNUAL, FOMC | partial | yes | 2019-2024: frozen calendar. 2010-2019: FOMC only (E.14); USDA rows absent. FOMC coverage: [shared, see shared/macro_calendars.md] |
| g16_month_end | ZS rows | grain trade dates | yes | yes | hist2010 grains + grains.py |
| g17_nq, g17_zn, g17_6e, g17_cl, g17_gc | NQ, ZN, 6E, CL, GC | lead listings | [shared] | [shared] | see product_NQ/ZN/6E/CL/GC.json (lead readers own them) |
| g17_zc | ZC | n/a | n/a | n/a | not applicable on ZS rows: ZC is K6's own cluster lead (SG-2) |
| g17_mbt | MBT | listing | no | partial | MBT listed 2021; not one of the 17 roots |
| g17_mes | MES | listing | no | partial | MES listed 2019-05; not one of the 17; "uncovered" in reports/stage_e12_gate0_list.json |

## 3. Proposed features

One proposal, offered with its weaknesses; the evidence does not establish that it clears 1.5x.

**P1 `zs_wasde_post_t4`** (WASDE post-release continuation, soybeans).
- Source: Anderson, McKenzie, Noyes (2024), quotes under E2: the soybean reaction to WASDE news grows from
  -0.061 at 30 minutes to -0.124 at the day close; corn does not.
- Formula: on a WASDE date d (release 11:00 CT) at t4 = 12:18: x = (close of the ZS 12:17 bar - close of the ZS
  10:59 bar) / tick, in vehicle ticks (both bars of d, one instrument_id). Other dates: 0 with applicability flag 0.
  Optional sign form sign(x). Uses only bars closed by t4 and the WASDE date calendar.
- Decision times and horizons: t4 only; h60 and F (12:18 -> 13:18).
- Legs: ZS. Calendars: WASDE dates; grains group calendar.
- Availability: 2019-2024 yes (k6/_wasde.py, 58 dates in the window). 2010-2019 **no**: no WASDE calendar on disk.
  If the lead built one from USDA's archive, the 11:00 CT release exists only from January 2013 (07:30 CT before).
  Under the F6 rule as written, it fails unless that calendar is built.
- Expected gross per trade (derivation): with the news sign known exactly, the 30 min -> close increment is
  |beta_day - beta_30| x E|news| = 0.063 x (0.798 x 0.029) = 14.6 bp over about 11:30-13:15 (105 min). Pro-rated to the
  t4 window (12:18-13:15, 57 of 105 min; linear drift assumed, not published) that is 7.9 bp. At $12.00/bu
  ([unverified assumption]) that is 0.95 cents = 3.80 ticks ($47.5), so 2.31x the 1.644-tick D8 wall ($9: 1.73x;
  $15: 2.89x). That is an **upper bound**: a bar-only proxy matches the news sign with an unknown probability p, and the
  gross scales by about (2p - 1). Clearing 1.5x (2.47 ticks) needs p >= 0.82. Nothing published gives p.
  Further weaknesses: conference paper, 122 events, 2010-2021 including 26% pre-2013 pre-open releases, no OOS
  test, normality assumed for E|news|.
- Clears 1.5x: not established (upper bound 2.31x; realistic value unknown).

No second proposal. Rejected candidates:
- Baltussen's SY first-half-hour reversal (E1): negative OOS R2, and its 12:50 decision minute is not a V2.2 or t4 time.
- The crush gap or crush mean-reversion (E4, Rechner-Poitras 1993): needs ZM (not one of the 17 roots) and has no open,
  sized post-2015 rule.
- Crop-condition response (E6): needs the released CPR value (not a bar or calendar), is a levels regression, and the
  report lands after the close.
- Dalian intraday momentum (E7, E8): not the vehicle, and the opposite sign to the CBOT row.

## 4. NQ only

n/a.

## 5. Fetch log, terms read, budget notices

Fetch log (UTC; full sha256 in `pages/ZS/fetch_log.tsv` and in product_ZS.json):

| UTC | Status | File | URL |
|---|---|---|---|
| 17:37:01 | ok | ideas_robots.txt | https://ideas.repec.org/robots.txt |
| 17:37:05 | ok | ideas_abdoh_chitavi_2025.html | https://ideas.repec.org/a/eee/reveco/v101y2025ics1059056025003491.html |
| 17:37:08 | ok | ideas_nccc24_379012.html (Wu, Huang, Serra 2024: hedging, not used) | https://ideas.repec.org/p/ags/nccc24/379012.html |
| 17:37:52 | ok | archive_org_robots.txt | https://archive.org/robots.txt |
| 17:37:55 | superseded (Wayback wrapper HTML, overwritten) | joseph_garcia_2016_aaea.pdf | web.archive.org/web/20241117204227/... |
| 17:38:06 | ok | joseph_garcia_2016_aaea.pdf (+ .txt) | https://web.archive.org/web/20241117204227id_/https://ageconsearch.umn.edu/nanna/record/235772/files/AAEA2016_USDA%20Report%20Effects.pdf |
| 17:38:22 | ok | farmdoc_robots.txt | https://farmdoc.illinois.edu/robots.txt |
| 17:38:25 | blocked (403; no Wayback snapshot) | Adjemian-Irwin 2018 WP | http://farmdoc.illinois.edu/irwin/research/USDA_Announcement_Effects_in_Real_Time.pdf |
| 17:38:53 / 17:39:00 | 403 by curl; scrapling get ok | irwin_pubs.md (paper not listed) | https://scotthirwin.com/pubs/ |
| 17:39:29 | ok | edepot_robots.txt (Crawl-delay 600; one request made after it) | https://edepot.wur.nl/robots.txt |
| 17:39:30 | blocked (403, Cloudflare) | hull robots | https://hull-repository.worktribe.com/robots.txt |
| 17:39:32 | ok | zhou_etal_2023_jcm.pdf (+ .txt) | https://edepot.wur.nl/629433 |
| 17:39:38 | blocked (403, Cloudflare challenge) | Jin et al. JFM accepted MS | https://hull-repository.worktribe.com/OutputFile/3303156 |
| 17:40:04 | ok | mpra_robots.txt | https://mpra.ub.uni-muenchen.de/robots.txt |
| 17:40:07 | ok | mpra_97134.html | https://mpra.ub.uni-muenchen.de/97134/ |
| 17:40:18 | ok | jin_etal_mpra_97134.pdf (+ .txt) | https://mpra.ub.uni-muenchen.de/97134/1/MPRA_paper_97134.pdf |
| 17:40:57 | ok | ideas_revi24_340926.html | https://ideas.repec.org/a/ags/revi24/340926.html |
| 17:41:01 | ok | ideas_jocoma_v19_2020.html | https://ideas.repec.org/a/eee/jocoma/v19y2020ics2405851319300753.html |
| 17:41:06 | ok | ideas_jfm_2025_v45i11.html | https://ideas.repec.org/a/wly/jfutmk/v45y2025i11p2109-2127.html |
| 17:41:30 | ok | scielo_robots.txt | https://www.scielo.br/robots.txt |
| 17:41:34 | ok | bethlem_etal_2023_resr.html (+ .txt) | https://www.scielo.br/j/resr/a/vcxYjcBRQYWDd6HL6Vq85WF/?lang=en |
| 17:42:29 | ok | anderson_mckenzie_noyes_2024.pdf (+ .txt) | https://farmdoc.illinois.edu/assets/meetings/nccc134/conf_2024/pdf/Anderson_McKenzie_Noyes_NCCC-134_2024.pdf |
| 17:44:35-43 | terms pages: RePEc 404, MPRA policies ok, SciELO about ok, farmdoc 404 | terms_*.html | see fetch_log.tsv |

Terms read: robots.txt read before fetching from each host (IDEAS: disallows only /cgi-bin/; archive.org: /control/,
/report/; farmdoc: /lucee, /wp-admin; scotthirwin.com: /wp-admin/; edepot.wur.nl: Disallow /WebQuery, Crawl-delay 600;
MPRA: /cgi/; SciELO: /admin only). No dedicated terms page restricting automated access was found: RePEc and farmdoc
terms URLs return 404; the MPRA policies and SciELO about pages contain no automated-access clause found by grep. The
papers carry their own permissions: Zhou et al. "open access article under the CC BY license"; Anderson et al. "Readers
may make verbatim copies of this document for non-commercial purposes". No cmegroup.com page was fetched.

Budget notices: none. WebSearch calls used: 11 of about 50. Firecrawl not used.

Overlap for the lead: the ZL reader also fetched Zhou et al. (2023) and the Abdoh-Chitavi IDEAS page
(`pages/ZL/`), and the ZC reader also fetched Joseph and Garcia (2016) (`pages/ZC/aaea2016_usda_report_effects.md`).
Anderson et al. (2024) covers corn too: the ZC reader may cite `pages/ZS/anderson_mckenzie_noyes_2024.txt`.

## 6. Unfinished and unverified items

- Adjemian and Irwin (2018, AJAE 100(4)): full text blocked (farmdoc 403, no Wayback copy); its 2009-2014 intraday grain
  results were not read. [unverified]
- Abdoh and Chitavi (2025): paywalled; rule, hold and per-trade size unknown. [secondary-only]
- Jin et al. (2020): read as the MPRA working paper, not the JFM version (Hull repository blocked by Cloudflare).
- Grains class evidence and release-time history: [shared, see shared/grains_class_notes.md] (not on disk when this
  file was written). FOMC coverage for g13-g15: [shared, see shared/macro_calendars.md] (not on disk when written).
- Price level for the bp/tick conversion ($12.00/bu) is an assumption, not read from a fetched page.
- No study found on NOPA crush-report (mid-month) intraday reactions in ZS: trade press only, not read, not evidence.
- A 2010-2019 WASDE / Crop Production calendar does not exist in the repo; building one is the lead's call.
