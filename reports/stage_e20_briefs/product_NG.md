# Stage E.20 Part A: product file for NG (Henry Hub natural gas, vehicle NG)

Reader: ProductReader-NG-OpusHigh, 2026-10-11 (started 10:33 PDT, written 10:52 PDT). JSON:
`reports/stage_e20_briefs/product_NG.json`. Raw pages: `reports/stage_e20_briefs/pages/NG/`
(fetch log `fetch_log.tsv`). No data store, no E.14/E.15/E.17/E.18 result on NG and no Gate 0 result
was opened. C1 code and calendars were read; their outcomes were not.

Conversion used throughout: NG tick = 0.001 $/MMBtu x 10,000 MMBtu = $10. Price level $3.00/MMBtu,
from EIA's Henry Hub spot annual averages (2010-2023: 4.37, 4.00, 2.75, [2013 cell not parsed], 4.37,
2.62, 2.52, 2.99, 3.15, 2.56, 2.03, 3.89, 6.45, 2.53; `pages/NG/eia_henryhub_annual.htm`). At $3.00,
1 tick = 3.33 bp, and 1 bp = $3.00 on a $30,000 notional. D8 round-trip wall from the root table:
2.408 ticks ($24.08). The 1.5x hurdle is 3.61 ticks ($36.12), about 12.0 bp at $3.00. The day-session
mean round trip is 1.672 ticks.

## 1. Evidence

| id | Effect | Rule | Hold | Gross per trade | Gross/net | Sample | Decay | Source | Grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Storage-day short across the WNGSR release, full sample | Sell the first-nearby NG future 90 min before the EIA release (10:30 ET standard, so entry at 09:00 ET) and buy back 30 min after. Unconditional. | 120 min | 34.3 bp = 10.3 ticks (17.86%/yr / 52) | gross (mid prices); 23.5 bp after bid-ask (12.21/52) | NG, 2003-03..2018-12, 699 announcements, 5-min TRTH | see E2 | Prokopczuk, Wese Simen, Wichmann (2021), Energy J. 42(2), Table 8 | primary |
| E2 | The same, after 2011 | As E1 | 120 min | **5.6 bp = 1.68 ticks** (2.91%/52), p = 0.558. Net -1.7 bp | gross | 2011..2018-12 | before 2011: 63.2 bp/event, Sharpe 4.22. After 2011: Sharpe 0.50, net negative | same, Table 8 Panel C and section V.C | primary |
| E3 | Decomposition of the announcement-day return | Descriptive | windows | (-90,+30) mean -0.37% (37 bp, 11.1 ticks), 99% of the day's return; pre (-90,-5) -0.18%, post (-5,+30) -0.19% | gross | as E1 | pre-window effect "steadily decreases" for 60- and 30-min windows (fn 20) | same, Table 5 | primary |
| E4 | Pre-release drift traded on an analyst-forecast predictor | Buy (sell) 90 min before the release if the predictor (accurate-analyst median minus Bloomberg consensus) is negative (positive); exit 5 min before | 85 min | not reported (Sharpe 0.84; 1.26 on large predictor values) | unknown | NG, 2008-07..2016-01, 334 announcements (WPSR same-day weeks dropped) | 24-month moving average positive to 2016-01; nothing after | Gu and Kurov (2018) JFM 38(9), read in Gu's 2018 WVU dissertation, ch. 1, Table 13 | primary (author's version) |
| E5 | ROD -> LH intraday momentum, NG's own row | Regress r_LH (14:00-14:30 ET = 13:00-13:30 CT) on r_ROD (previous 14:30 ET close to 14:00 ET); trade in the sign of r_ROD | 30 min | slope 3.02 (x100), so 3.02 bp of LH per 1% of r_ROD = 0.906 ticks per 1% at $3.00. The unconditional per-trade figure is not published for NG | gross | NG, 1993-01-06..2020-05-01, 6,824 days, 1-min | per-market decay not reported (class: shared notes) | Baltussen, Da, Lammers, Martens (2021) JFE, Table B3 Panel B | primary (on-disk copy) |
| E6 | Week-to-week storage-surprise reversal; prices absorb analyst forecasts before the release | Needs analyst forecasts | n/a | no size | unknown | not read | none | Ederington, Lin, Linn, Yang (2019) Energy J. 40(5) | secondary-only |
| E7 | Pressure from leveraged-ETF rebalancing in NG, VIX, oil and metals | Needs ETF holdings; daily horizon | daily | no NG size retrieved | unknown | not read | none | Todorov (2021) BIS WP 952 | secondary-only |
| E8 | Intraday NG moves on weather-forecast revisions (00 and 18 UTC runs) | Conditional on forecast changes | n/a | none | unknown | 2022 senior thesis, not retrieved | none | Princeton dataspace 88435/dsp01r781wk215 | unverified |
| E9 | NG settlement window (13:28-13:30 CT), post-release reversal, time of day, NG intraday TSMOM other than E5 | none | n/a | none | n/a | n/a | **null search**: 6 WebSearch queries plus OpenAlex (1,927 hits since 2015, top 50 titles screened) found no post-2015 study | - | unverified |
| E10 | NG intraday patterns from HFT data | not read | n/a | none | n/a | not read | not read | Song, Lopez de Prado, Simon, Wu (2015) SSRN 2657224 | unverified |

Verbatim quotes (locations refer to the saved files):

- E1 (`prokopczuk_wesesimen_wichmann_2021_ej_accepted.pdf`, Table 8, accepted version p. 33, txt
  lines 1222-1258): "The strategy opens a short position 90 minutes before the EIA storage report
  announcement, usually Thursdays at 10:30 AM ET, and closes the position 30 minutes after the
  announcement." / "Raw (-90,30) 17.86 (0.000) 2.57 / Raw + TC 12.21 (0.003) 1.79 / Raw + TC + FC
  12.01 (0.003) 1.76". Footnote 24 (p. 16): "returns are annualized using a multiplier of 52 to
  represent the realisable return within a year". The Table 8 caption says the raw row is "based on
  mid prices", while the text (p. 15) says "this is based on returns from the settlement prices".
  The paper is inconsistent on this point.
- E2 (Table 8 Panel C): "Panel C: After 2011 / Raw (-90,30) 2.91 (0.558) 0.50 / Raw + TC -0.90
  (0.854) -0.16". Section V.C: "In the more recent period, this has declined to only 3% and a Sharpe
  ratio of 0.5, which do not withstand transaction and funding costs." Also: "gradually decreasing
  to become insignificantly different from zero in the most recent period."
- E3 (Table 5, p. 30): "Average Return -0.37 -0.37 -0.00 ... % of Daily Return 100% 99.0% 1.0%";
  Panel B: "(-90, -5) ... -0.18 ... (-5, 30) -0.19 ... 49.4% 50.6%". Table 7 Panel B: "2014-2018
  -0.02 -0.15 (0.070) 0.08 (0.147)" (pre-announcement mean, split by the sign of the ex-post surprise).
- E4 (`gu_2016_wvu_dissertation_firecrawl.md`, section 1.5.3): "a simple trading strategy that
  consists of buying (selling) a futures contract 90 minutes before the release time if the predictor
  is negative (positive), and closing the position 5 minutes ahead of the announcement would have
  earned an annualized Sharpe ratio of 0.84." Table 13: "Full Sample (N=271) ... Sharpe Ratio 0.84 ...
  Large Values of Predictor (N=153) 1.26". Sample (section 1.2.2): "Our sample period is from July 2008
  through January 2016 ... The final sample contains 334 observations." This also verifies the Sharpe
  of 1.26 that the E.0 catalog (K4-012) carried as [unverified], on the dissertation version.
- E5 (`reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md`, line 3771): "| NG |
  3.89***(5.49) | 0.68 | 0.61***(5.21) | 3.74***(5.21) | 1.80***(2.58) | 9.20***(3.44) | 1.34 |
  0.94*** | 3.02***(6.15) | 1.04 | 0.92*** |". The columns are beta_ONFH, R2, R2OOS, beta_rONFH,
  beta_M, beta_SLH, R2, R2OOS, **beta_ROD 3.02 (t 6.15), R2 1.04%, R2OOS 0.92%**. Caption: "Adjusted
  R2, R2OOS, and slope coefficients are multiplied by 100." Table 1 (line 900): "Natural gas futures
  NYMEX | NG | 9:00 - 14:30", with "U.S.-listed futures are expressed in Eastern Standard Time".
- E6: abstract only, as quoted in the E.0 catalog (K4-006) and the E.0 review row 25: "Storage flows
  higher or lower than analysts had expected one week tend to be partially reversed the following
  week"; "Analyst's natural gas forecasts efficiently impound the available time-series information".
  The saved Montana State research-brief page contains neither sentence.
- E7 (`bis_wp952_landing_scrapling.txt` line 419): "Leverage rebalancing has the largest effects. It
  amplifies price changes and exposes ETF counterparties negatively to variance."

**Reading of decay and costs.**
- The one unconditional, NG-specific, sized intraday rule published since 2015 is the storage-day short
  (E1). It is the source of member K4-ngpre-01, and its authors report that it died after 2011. The
  post-2011 gross of 5.6 bp is 1.68 ticks at $3.00, which is 0.70x the D8 wall and below both the 1x
  and the 1.5x hurdles. The sign of the pre-2011 effect is not significant after 2011 (p = 0.558).
- Its pre-release half depends on the ex-post surprise sign (Table 7). It shrank from -0.47% (2007-14)
  to -0.15% (2014-18, p = 0.070) on positive-surprise days. No public rule picks those days ex ante
  except analyst forecasts (E4), which are not available here.
- NG's ROD->LH slope (E5) is among the strongest commodity rows (t 6.15, OOS R2 0.92%). At 0.906 ticks
  per 1% of |r_ROD|, a trade needs |r_ROD| >= 2.66% to cover the wall and >= 3.99% to clear 1.5x.
- Timing facts for the lead on E5:
  - NG's LH is 13:00-13:30 CT.
  - The energy t3 = 13:00 CT matches its start.
  - h60 exits at 14:00 CT, 30 minutes after NG's day close C = 13:30 CT (the settlement window is
    13:28-13:30 CT, `reports/stage_e16_settlement.md`).
  - t4 = 14:08 CT is after C, so r_ROD at t4 spans past the published LH window for NG.
  - The published hold (30 min) is under V2.2's 60-min minimum.
- No sized NG evidence was found for the settlement window, post-release reversal, time of day or
  weather timing (E8, E9). That is an absence in what was searched, not a rejection.

## 2. Feature availability (NG rows; NG bars are read by no other root's features)

Backward window 2010-07-01..2019-05-05; search window 2019-05-06..2024-02-29. Basis: listing and
calendar files only.

Calendar files:
- **H10**: `data/calendars/hist2010/energy.json`, 2010-06-01..2019-05-31, sha256 c7a58e90..., grade cme,
  0 unsourced. Two Globex eras: 17:00-16:15 CT to 2015-09-18, then 17:00-16:00 CT. Day session
  08:00-13:30 CT. O = 08:00 is marked UNVERIFIED for 2015-09-21..2019-05-31; E.16 grades it
  secondary (S40).
- **E19**: `data/calendars/energy.py`, 2019-05-01..2026-06-19.
- **REL14**: `reports/stage_e14_cal_releases.json`, 2010-06-01..2019-05-31, sha256 9a051211...:
  - NGS 470, all official, 0 drop_actual_differs, 28 schedule-only weeks;
  - WPSR 470, with the 2012-11-01 time unsourced;
  - FOMC 72, with 14 times inferred at 14:15 ET.
- **REL19**: `reports/stage_e2b_release_calendar.json`, 2019-05-01..2026-06-21. NG's D8 list is NGS,
  WPSR and FOMC. In the search window:
  - NGS 252 (evidence field: 251 "unverified", 1 "verified");
  - WPSR 250 verified;
  - FOMC 37 verified.
- **NGS19**: `strategy/members/k4/_releases.py` NGS, 247 rows in the window (239 at 09:30 CT, 8 at
  11:00 CT). It drops the 5 rows the E.5 check found misdated: 2019-12-26, 2020-01-02, 2020-11-12,
  2021-01-21 and 2023-11-09.
- **FS14**: `reports/stage_e14_cal_energy_full_sessions.json`, 2,250 dates 2010-06-01..2019-05-31.
- **FS19**: `strategy/members/k4/_calendar.py` ENERGY_FULL_SESSIONS, 2019-05-01..2026-06-18.

Code wiring fact: `ml_route_v2` reads only the 2019+ tables (NGS19, FS19, REL19, E19). The 2010-2019
loaders exist in `c1_replication/tables.py` (load_releases, load_full_sessions; NG's D8 list) and
`base_rules/calendars.py` (hist2010), but they are not wired into `ml_route_v2`.

| Feature | Legs | Calendars | 2010-2019 | 2019-2024 | Basis / dates |
|---|---|---|---|---|---|
| cp1_ret | NG | H10, E19, D6 O | yes | yes | close(O+29) - open of the 17:00 CT bar of d-1. Globex reopened at 17:00 CT in both eras (cme). |
| cp2_range | NG | H10, E19 | yes | yes | OR over [08:00, 08:15) CT. O is a D6 convention, UNVERIFIED as a CME-stated open for 2015-09..2019-05. |
| cp2_brk | NG | H10, E19 | yes | yes | Bars in [08:15, 13:30) CT. |
| cp3_clv | NG | H10, E19 | yes | yes | Prior port-complete day. |
| k4_ngpre_mto | NG | REL14 (via the C1 NGS table, 0 C13 drops), NGS19 | yes | yes | T = 09:30 CT (11:00 exceptions). 2010-19 times: 457 at 10:30 ET, 13 at 12:00 ET (Thu 444, Wed 13, Fri 12, Tue 1). Applies at t1 = 08:30 on NGS days (mto = 60). |
| k4_ngpre_msince | NG | REL14, NGS19 | yes | yes | Applies at t2 = 10:30 (60 min after) and t3 = 13:00. |
| k4_ovr_ret | NG | FS14, FS19, H10, E19 | yes | yes | Slots 09:00-13:00 CT; applies at t2/t3. |
| k4_ovr_pct | NG | FS14, FS19 | yes | yes | Needs 20 prior full sessions (>= 80 values); warm-up to about 2010-08. |
| g01_ret30, g02_ret60, g03_ret120, g04_ret_day | NG | H10, E19 | yes | yes | Own path; sigma_X,d warm-up of 20 dates. |
| g05_gap | NG | H10, E19 | yes | yes | Not applicable after early-halt dates (H10: 73 early halts, 26 closures). |
| g06_rv60, g07_range, g08_prev_ret, g10_logvol30 | NG | H10, E19 | yes | yes | 20-date warm-ups. |
| g09_vol_state | NG | H10, E19 | yes | yes | 120 + 20 date warm-up: about 2010-07..2011-01 is missing for data reasons, not causally unavailable. |
| g11_t_index, g12_dow | none | V2.2 clock | yes | yes | Clock and date only. |
| g13_min_to_rel, g14_min_since_rel, g15_rel_day | none | REL14, REL19 | yes | yes | NGS/WPSR/FOMC. 2019-24 caveat: G13-G15 read ReleaseCalendar.by_root, so they keep the 5 misdated NGS rows and miss the actual Friday releases (the k4 table drops the rows but does not add the Fridays). 2010-19 caveats: WPSR 2012-11-01 time unsourced; 14 inferred FOMC times. FOMC part: [shared, see `shared/macro_calendars.md`]. |
| g16_month_end | none | H10, E19 | yes | yes | Energy group calendar. |
| g17_nq, g17_zn, g17_6e, g17_gc, g17_zc | NQ, ZN, 6E, GC, ZC | none | yes | yes | Each leg's window starts 2010-07 (`stage_e16_windows.json`). Listing: [shared, see `product_<lead>.md`]. |
| g17_cl | CL | none | yes | yes | **Not applicable on NG rows by construction**: CL is K4's own cluster lead (generic.py: "the row's own cluster lead is not applicable"). |
| g17_mbt | MBT (not one of the 17) | none | no | partial | MBT listed 2021 (brief section 7). |
| g17_mes | MES (not one of the 17) | none | no | yes | MES listed 2019-05-06, after the backward window ends (2019-05-05). |

Not V2.3 but added by the prompt: r_ROD and |r_ROD| over its 60-date median on NG rows use C = 13:30 CT.
t4 = 14:08 CT falls after C (see section 1).

## 3. Proposed features

None. Reasons:
1. The only unconditional NG-specific rule with a published per-trade size (E1/E2) is already in the
   library as `k4_ngpre_mto` and `k4_ngpre_msince`. Its post-2011 gross is 1.68 ticks, 0.70x the D8
   wall, so it fails 1.5x.
2. NG's ROD->LH (E5) is r_ROD, which the prompt already adds.
3. Every other NG effect found either needs data outside bars and calendars (analyst forecasts in E4
   and E6, ETF holdings in E7, weather forecasts in E8) or has no published size (E9, E10).

## 4. NQ only

n/a

## 5. Fetch log, terms read, budget notices

Fetch log: all times UTC 2026-10-11, sha256 in `pages/NG/fetch_log.tsv` and the JSON.

| UTC | Status | File | URL |
|---|---|---|---|
| 17:37:20 | 200 | centaur_robots.txt | https://centaur.reading.ac.uk/robots.txt |
| 17:37:28 | 200 | centaur_90003.html | https://centaur.reading.ac.uk/90003/ |
| 17:37:40 | 200 | centaur_end_user_agreement.pdf | https://centaur.reading.ac.uk/1492/1/End_User_Agreement_version_C1%2000.pdf |
| 17:37:46 | 200 | prokopczuk_wesesimen_wichmann_2021_ej_accepted.pdf (sha256 4ffdbf72...) | https://centaur.reading.ac.uk/90003/1/NG_paper_final_round.pdf |
| 17:38:38 | 200 | wvu_robots.txt | https://researchrepository.wvu.edu/robots.txt |
| 17:38:42 | 200 | wvu_etd_8184.html | https://researchrepository.wvu.edu/etd/8184/ |
| 17:38:51 | 403 blocked (Cloudflare) | gu_2016_wvu_dissertation_403_cloudflare.html | viewcontent.cgi?article=9192&context=etd |
| 17:38:57 | 403 (scrapling get) | not kept | same |
| 17:39:08 | 200 but empty (scrapling fetch) | not kept | same |
| 17:40:54 | 200 (Firecrawl, pages 1-60 of 132) | gu_2016_wvu_dissertation_firecrawl.md (sha256 08c3c50d...) | same |
| 17:43:16 | 200 | bis_robots.txt | https://www.bis.org/robots.txt |
| 17:43:20 | 200 | bis_terms.htm | https://www.bis.org/terms_conditions.htm |
| 17:43:31 | 200 HTML, not the PDF | todorov_bis_wp952_landing.html | https://www.bis.org/publ/work952.pdf |
| 17:43:45 | 200 (scrapling get; redirected to the landing page) | bis_wp952_landing_scrapling.txt | same |
| 17:44:22 | 200 | openalex_ng_intraday.json | api.openalex.org search "natural gas futures intraday", 2015+ |
| 17:44:33 | 200 | openalex_ng_detail.json | api.openalex.org, 4 DOIs |
| 17:44:50 | 200 | osti_robots.txt | https://www.osti.gov/robots.txt |
| 17:45:31 | timeout | none | osti.gov API query |
| 17:47:12 | 200 | montana_robots.txt | https://www.montana.edu/robots.txt |
| 17:47:14 | 200 | montana_ederington2019.html | montana.edu research brief (no abstract text) |
| 17:47:48 | 200 | eia_henryhub_annual.htm | https://www.eia.gov/dnav/ng/hist/rngwhhda.htm |

Terms read:
- **CentAUR (Reading).**
  - robots allows everything except /cgi/.
  - End User Agreement cl. 2: "single copies ... for personal research, study, educational,
    non-commercial or not-for-profit purposes".
  - cl. 8: "Whole items must not be harvested by robots except transiently for full-text indexing or
    citation analysis".
  - The agreement was fetched just before the paper in the same command and read after it: one item,
    one request. Flagged for the lead under cl. 8.
- **WVU Research Repository.**
  - robots does not disallow viewcontent.
  - Rights statement on the PDF: "You are free to use this Dissertation in any way that is permitted
    by the copyright and related rights legislation that applies to your use."
  - Cloudflare blocked curl and Scrapling. The brief's fallback order was followed to Firecrawl.
- **BIS.** robots allows. Terms: "Users may reproduce a limited extract of BIS Material ... provided
  the BIS is cited as the source."
- **OpenAlex.** Terms were NOT read before two metadata queries (metadata only).
- **OSTI.** robots allows; the API query timed out.
- **montana.edu.** robots allows.
- **eia.gov.** Public domain, per E.14's reading (`reports/stage_e14_briefs/pages/terms_checks.md`).

WebSearch queries (10 used of about 50):
1. NG futures intraday response to the EIA storage report
2. NG intraday momentum, last half-hour
3. NG storage pre-announcement drift
4. Henry Hub intraday TSMOM
5. Gu and Kurov pdf
6. Ederington 2019 / Bjursell 2015
7. "intraday momentum" "natural gas" in the journals
8. weather-forecast revisions intraday
9. NG settlement window
10. Todorov ETF rebalancing; plus NG post-release reversal and NG time-of-day seasonality

Queries 1, 2, 4, 7, 9 and the reversal and seasonality queries returned no NG intraday study since
2015 beyond E1 to E5.

Budget notices: no over-budget WebSearch notice and no Firecrawl credit notice. A "COST CRITICAL"
session-cost hook message appeared; it is informational, and work continued.

## 6. Unfinished and unverified items

- Gu and Kurov (2018): the published JFM version was not retrieved. The dissertation chapter was read
  (Firecrawl pages 1-60 of 132; chapter 1 is complete in them).
- Ederington et al. (2019): abstract-level only (secondary-only). The Montana State page has no
  abstract text.
- Todorov (BIS WP 952): the PDF was not obtained, so there is no NG size.
- Song et al. (2015) and the Princeton 2022 thesis were not retrieved (unverified).
- Not read here; cite the shared notes instead:
  - energy-class evidence: `reports/stage_e20_briefs/shared/energy_class_notes.md` (CL reader);
  - the Aalto thesis NG and energy rows: `shared/aalto_thesis_notes.md` (ZN reader);
  - post-2020 ROD->LH decay: `shared/baltussen_notes.md` (NQ reader).
  None of these files existed at 10:52 PDT.
- No unconditional per-trade gross of ROD->LH is published for NG alone. The thresholds in E5 come
  from the slope only.
- Shared scratch-path collision:
  - Other readers' scripts named `fetch.sh` sit at the shared scratchpad path. My first call ran one
    of them, which wrote my CentAUR robots fetch into `reports/stage_e20_briefs/pages/LE/`
    (`centaur_robots.txt`) and added two lines to `pages/LE/fetch_log.tsv` (17:36:53 and 17:36:54Z).
    I left these untouched.
  - `pages/NG/wrap_robots.txt` is not mine; it appears in the 6E reader's log.
  - From then on I used my own script, `ng_reader_fetch.sh`.
