# Stage E.20 Part A: product file for CL (WTI crude; vehicle MCL, price path CL)

Reader: ProductReader-CL-OpusHigh (opus, high). Started 2026-10-11 10:33 PDT, finished
10:55 PDT (from date). Brief: `reports/stage_e20_briefs/brief_partA_shared.md`. Shared class notes written:
`reports/stage_e20_briefs/shared/energy_class_notes.md` (the NG reader cites it). Raw pages, fetch
log and search log: `reports/stage_e20_briefs/pages/CL/`. No data store, no E.15/E.17/E.18 or Gate 0
result was opened. Facts only: the F6 feature cut, acceptance and every registration choice belong to
the lead.

Conversion used everywhere: 1 bp of notional = P/100 MCL ticks ($1.00 per tick, $0.01/bbl x 100 bbl).
P_s = $67.35 (mean of EIA annual WTI spot 2019-2023: 56.99, 39.16, 68.13, 94.90, 77.58; saved
`pages/CL/eia_rwtc_annual.html`), so 0.674 ticks per bp; P_b = $74.17 (2010-2018 mean), 0.742 ticks
per bp. MCL D8 round trip (root table): 4.346 ticks = $4.35 = 6.45 bp at P_s. 1.5x hurdle: 6.52 ticks.

## 1. Evidence

| ID | Effect | Rule (as coded by the source) | Hold | Gross per trade (bp; MCL ticks at P_s) | Gross/net | Sample | Decay evidence | Source | Grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | ROD -> LH momentum, CL | regress r_LH (14:00-14:30 ET) on r_ROD (prior close to 14:00 ET), CL day 09:00-14:30 ET | 30 min | none: beta_ROD 0.67 (x100), t 0.25; R2 0.03%; R2_OOS -1.04% | gross | CL tickdata 1987-01-06..2020-05-01, 8,336 days, 1-min | OOS R2 negative over the full sample (a null, not a decay) | Baltussen, Da, Lammers, Martens, JFE 142 (2021), Table B3 row CL, Table A3; on-disk copy `reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md` lines 3294, 3673-3680, 3769 | primary |
| E2 | EIA-day third half-hour -> last half-hour | on Wednesday 10:30 ET WPSR days: r3 = log(p(11:00)/p(10:30)) ET; long if r3 >= 0, short if < 0, at the start of the last half-hour (15:30 ET), exit 16:00 ET | 30 min | Table 6 Panel E: 4.14% "per annum", t 1.88. Per trade: 1.64 bp if annualised x252 (1.11 ticks), 9.32 bp if summed over 44.4 EIA days a year (6.28 ticks). The paper does not say which. | gross (no cost in the paper) | USO ETF 1-min, 2006-04-10..2019-07-31; 591 EIA Wednesdays | rolling 5-year coefficient "declining trend"; "not observed" in 2014-2016 | Wen, Indriawan, Lien, Xu, Energy Journal 44(5) 2023, 149-171; accepted version https://hdl.handle.net/2440/141224 | primary |
| E3 | Non-EIA first half-hour -> last half-hour | r1 = log(p(10:00 ET)/p(prior 16:00 close)); same timing as E2 | 30 min | Table 6 Panel B: 1.88% p.a., t 2.10; 0.75 bp (x252) or 0.94 bp (per non-EIA day, 199 a year); 0.5-0.6 ticks | gross | as E2, 2,649 non-EIA days | its source is the overnight component (Table 2) | same | primary |
| E4 | Overnight component -> last half-hour | r_overnight = prior 16:00 close to the 09:30 open | 30 min | Panel C: 2.39% p.a., t 2.45 | gross | as E3 | n/a; overnight effects are a V34 drop category | same | primary |
| E5 | r3 on non-EIA days (placebo) | as E2 on non-EIA days | 30 min | Panel D: -0.36% p.a., t -0.37 | gross | as E3 | n/a | same | primary (null) |
| E6 | Pre-EIA buyer-initiated flow, price -0.25% before the release | conditional on the inventory surprise sign (known only after the release) | about 2 h | not codeable from bars and calendars | unknown | WTI futures (years not verified) | n/a | Rousse and Sevi, Energy Journal 40(2) 2019, 139-160 | secondary-only |
| E7 | API and EIA inventory surprises, 5-min returns | surprise vs consensus (API) and vs API (EIA) | minutes | unsized in what was read; needs released values | unknown | CL futures about 2013-2014 (search summary) | n/a | Ye and Karali, Energy Economics 59 (2016) 349-364 | secondary-only |
| E8 | Post-WPSR reversion | price "reverts quickly after the initial reaction", effects last about 25 min | minutes | unsized | unknown | WTI around EIA reports | n/a | Geman and Li, J. Energy Markets 11(2) 2018 | secondary-only |
| E9 | Intraday overreaction then reversal, energy most | 1-min to 1-h overreactions | <= 1 h | unsized | gross | 20 commodity futures 2019-11-20..2020-06-03 | 6.5-month sample | Borgards, Czudaj, Van Hoang, Resources Policy (ISSN 0301-4207); LMU record 97149 | secondary-only |
| E10 | Brent time-of-day long-short | long/short at particular times of day | intraday | unsized; "some" strategies have positive CAPM alphas after costs and margin | net (as claimed) | ICE Brent tick 2010-01..2021-10 | n/a | Haugom, Ouyang, Smith-Meyer, Stordal et al., Quantitative Finance 2025; Glasgow eprint 363707 | secondary-only (not CL) |
| E11 | Settlement window 13:28-13:30 CT | no systematic post-2015 study found; one-event study of 2020-04-20 (closing pressure about $7/bbl, TAS predation for the rest) | n/a | n/a | n/a | one event | n/a | Ge, Kang, Tang, Yang, AEA 2023 session paper | secondary-only; a null |
| E12 | Passive-fill adverse selection (execution) | resting 1-lot limit orders, TT simulator | n/a | 518/625 CL fills adverse (82.9%) | n/a | CL Jun24, 2024-04-23, one day | n/a | Lalor and Swishchuk, arXiv 2409.12721, Table 2 | primary |

Verbatim quotes and locations for E1-E5 and E12 are in `shared/energy_class_notes.md` ("Quotes").
Key ones:
- E1 (Table B3 row CL): "| CL | 2.00(0.72) | 0.17 | -0.48 | 2.40(1.12) | -0.06(-0.03) | -13.95(-0.99)
  | 1.25 | -1.77 | 0.67(0.25) | 0.03 | -1.04 |"; caption: "Adjusted R2, R2OOS, and slope coefficients
  are multiplied by 100."
- E2 (Table 6): "Panel E: using r3 as a trading signal on EIA days ... 4.14* [1.88] 0.21 19.54 0.66
  10.09 58"; text: "an even higher average return of 4.14% per annum and a Sharpe ratio of 19.54."
  Data: "We collect USO ETF data at a one-minute frequency from Refinitv Tick History. The sample
  period is from April 10, 2006, when the ETF started trading, to July 31, 2019." Decay: "strong and
  statistically significant over our sample period, albeit with a declining trend. ... during the
  crude oil price plunge between 2014 and 2016, the intraday return predictability is not observed."
- E12: "2024/04/23 CL Jun24 625 518 107".

**Reading of decay and costs.** The one primary result on CL futures themselves (E1) is a null:
crude is the energy contract without ROD -> LH momentum (HO, NG show it; XB weakly). The only sized
post-2015 crude result (E2) is on USO, gross, significant at 10% in its strategy table, declining
over 2006-2019 and absent in 2014-2016; its exit window (14:30-15:00 CT) lies after CL's 13:30 CT
settlement. Its rule is the source of the library's K4-eiamom-01, so it is already in v2 as
`k4_eiamom_r3`. Under the generous per-trade reading (9.32 bp = 6.28 MCL ticks) it is 1.44x the MCL
D8 round trip, under the 1.5x hurdle; under the x252 reading it is 0.26x. E3/E4 are a fraction of a
tick. The minute-scale reversal results (E8, E9) are unsized and shorter than v2's 60-minute minimum
hold. No settlement-window or API-window study sized for trading was found. Passive entry would add
adverse selection (E12). On published evidence, no CL intraday effect clears the cost wall.

## 2. Feature availability (CL legs and MCL rows)

Calendar files read for dates and source notes only:
- energy group 2019-2024: `data/calendars/energy.py`, CALENDAR_COVERAGE 2019-05-01..2026-06-19 (CME,
  graded cme/secondary/unverified per row); 2010-2019: `data/calendars/hist2010/energy.json` (= E.14
  `reports/stage_e14_cal_energy.json`, sha256 c7a58e90...), coverage 2010-06-01..2019-05-31, 2,323
  trade dates, 0 unsourced, every status "cme"; session row 2010-06-01..2015-09-18 "Globex 17:00-16:15
  CT", day session CL 08:00-13:30 CT.
- ENERGY_FULL_SESSIONS: 2019-2026 `strategy/members/k4/_calendar.py` (2019-05-01..2026-06-18 dates
  used); 2010-2019 `reports/stage_e14_cal_energy_full_sessions.json` (2010-06-01..2019-05-31, 2,250
  dates, same rule).
- WPSR: 2019-2026 `strategy/members/k4/_releases.py` (369 rows, 317 standard, 2019-05-01..2026-06-17,
  from the frozen release calendar `reports/stage_e2b_release_calendar.json`); 2010-2019 E.14
  `reports/stage_e14_cal_releases.json` (470 WPSR rows 2010-06-03..2019-05-30; 469 official/official, 1
  time unverified: 2012-11-01; 398 Wednesday 10:30 ET, 64 Thursday 11:00, 6 Friday 11:00, 1 Monday
  10:30).
- API_WSB release rows: 2019-2026 frozen release calendar (372 rows, all 16:30 ET, products CL MCL);
  2010-2019: none on disk. E.16's review (F-11) lists API_WSB among types "without 2010-2019 rows".
  API's own page, Wayback 2016-04-10: "every Tuesday afternoon at 4:30 pm Eastern. If Monday is a
  Federal holiday, the reports are scheduled for release on Wednesday afternoon"; the 2014-04-06
  capture: "Published weekly every Tuesday afternoon (published Wednesday afternoon in the event of a
  Monday holiday)" (no time).
- FEDERAL_MONDAY_HOLIDAYS and NYSE_NOT_FULL: 2019-05-27..2026-05-25 and 2019-05-27..2026-06-19 in
  `strategy/members/k4/_releases.py`; no 2010-2019 table on disk (searched reports/ and data/).
- OILCAD_DATES (k8): 2019-05-01..2026-06-18 (`strategy/members/k8/_calendar.py`, energy and FX full
  sessions); 2010-2019: no table, derivable from `data/calendars/hist2010/energy.json` and `fx.json`
  (both 2010-06-01..2019-05-31, 0 unsourced) by the same full-session rule.
- Listing: CL in Baltussen Table A3 from 1987-01-06; `reports/stage_e16_windows.json` CL window
  2010-07-01..2024-02-29, 2010-2019 bars from the E.17 21-root purchase. MCL (the vehicle) is not
  read: v2 maps MCL rows to the CL price path in both windows.

| Feature | Rows | Legs | Calendars / literals | 2010-2019 | 2019-2024 | Basis and dates | Shared ref |
|---|---|---|---|---|---|---|---|
| `cp1_ret` | all; here MCL | CL | energy group calendar; D6 O 08:00, first bar 17:00 CT d-1 | yes | yes | hist2010/energy.json 2010-06-01..2019-05-31 (Globex from 17:00 CT d-1, cme); energy.py 2019-05-01.. | |
| `cp2_range`, `cp2_brk` | all; MCL | CL | energy calendar; O 08:00, C 13:30 | yes | yes | as above; D6 O after 2015-09 is the design constant (E.14 limit 2; E.16 marks hist O 2015-09-21..2019-05-31 secondary/unverified, S40) | |
| `cp3_clv` | all; MCL | CL | energy calendar (previous port-complete day) | yes | yes | as above | |
| `k4_apipre_ret` | MCL | CL | WPSR standard Wednesdays; ENERGY_FULL_SESSIONS; FEDERAL_MONDAY_HOLIDAYS; API_DROPPED_WEEKS; API time premise Tuesday 15:30 CT (K4-L-04) | partial / undetermined | yes | 2010-2019: WPSR yes (E.14), full sessions yes (E.14), FEDERAL_MONDAY_HOLIDAYS no file (rule-derivable from 5 U.S.C. 6103 / OPM lists, not built), API_DROPPED_WEEKS undetermined (no 2010-2019 API calendar to check), API 4:30 pm ET verified from 2016-04 (API page), 2010-2015 time [secondary-only] | |
| `k4_eiafade_move` | MCL | CL | WPSR rows with T_W (CT), T_W+15 <= 13:13 | partial | yes | 2010-2019 E.14 WPSR: 469 of 470 times official; 2012-11-01 time unverified (that date cannot be computed) | |
| `k4_eiamom_r3` | MCL | CL | WPSR standard rows; NYSE_NOT_FULL | partial | yes | 2010-2019: WPSR standard rows yes (398 Wednesday 10:30 ET); NYSE_NOT_FULL no 2010-2019 table on disk (E.16 saved NYSE holiday captures for 2015-2016 only, in its livestock pages) | |
| `k4_ovr_ret`, `k4_ovr_pct` | MCL, NG | CL (MCL rows); NG (NG rows) | ENERGY_FULL_SESSIONS (20 prior dates, >= 80 values) | yes | yes | E.14 energy full sessions 2010-06-01..2019-05-31; k4/_calendar 2019-05-01..2026-06-18 | |
| `g01_ret30`, `g02_ret60`, `g03_ret120`, `g04_ret_day` (G1-G4) | MCL | CL | energy calendar (trade date, first bar) | yes | yes | group calendars above | |
| `g05_gap` (G5) | MCL | CL | energy calendar: previous trade date's C_X - 1 bar (13:29), early halts (SG-4) | yes | yes | group calendars above (73 early halts 2010-2019) | |
| `g06_rv60`, `g07_range`, `g08_prev_ret`, `g09_vol_state`, `g10_logvol30` (G6-G10) | MCL | CL | energy calendar; 20/120-date lookbacks | yes | yes | group calendars above | |
| `g11_t_index`, `g12_dow` | MCL | none (clock) | V2.2 table | yes | yes | constants | |
| `g13_min_to_rel`, `g14_min_since_rel`, `g15_rel_day` | MCL | none (calendar) | MCL's D8 list = FOMC, WPSR, NGS, API_WSB (frozen calendar) | partial | yes | 2019-2024: frozen calendar 2019-05-01..2026-06-21. 2010-2019: E.14 has WPSR, NGS, FOMC (2010-06-01..2019-05-31); API_WSB absent. FOMC coverage: see RTY's macro file | `shared/macro_calendars.md` (RTY), FOMC |
| `g16_month_end` | MCL | none | energy calendar | yes | yes | group calendars above | |
| `g17_cl` | every row except K4's own cluster (MCL, NG) | CL | CL roll dates (not-applicable flag); trade date | yes | yes | CL listed and trading throughout both windows (Baltussen Table A3 from 1987-01-06; E.16 windows 2010-07-01..2024-02-29). Roll dates come from the store build's symbology, not a calendar. CL rolls monthly, so g17_cl is "not applicable" on CL roll-blackout dates (V2.2) | |
| `k8_oilcad_ret`, `k8_oilcad_z` | 6C only | CL | OILCAD_DATES (energy and FX full sessions), 20 prior dates, >= 1,000 values | partial (no table; derivable) | yes | 2010-2019 derivable from hist2010 energy.json and fx.json; 6C is not one of the 17 roots (applies on 6C rows only) | |
| r_ROD, its magnitude ratio | MCL | CL | group close C 13:30 | (added by the prompt; not audited here) | | | |

## 3. Proposed features

None. Reasons:
1. The two codeable crude rules with a published size are already in v2: E2 (EIA third half-hour ->
   last half-hour) is the K4-eiamom-01 port (`k4_eiamom_r3`), and E1/E3 (rest-of-day or first
   half-hour -> last half-hour) are covered by r_ROD (added by the prompt) and `cp1_ret`.
2. None clears the cost wall on the published numbers: E2 at most 6.28 MCL ticks per trade under the
   generous reading (ratio 1.44 to the 4.346-tick D8 round trip, under 1.5x) and 1.11 ticks (0.26x)
   under the x252 reading; E3 0.5-0.6 ticks; E1 is a null on CL futures.
3. The API-window, settlement-window, overreaction and Brent time-of-day studies are unsized in what
   could be read (secondary-only), minute-scale (below the 60-minute hold), or need released values
   (API, EIA surprises), which no feature may read.

## 4. NQ only

n/a

## 5. Fetch log, terms read, budget notices

Fetch log (UTC; full lines in `pages/CL/fetch_log.md`):

| URL | UTC | sha256 | Path | Status |
|---|---|---|---|---|
| https://digital.library.adelaide.edu.au/server/api/core/bitstreams/aee73b81-111e-4bef-9e0e-7b1164f368a1/content | 2026-10-11T17:37:20Z | 110ec616bcded7c190e7840235375552813e7b8ad8271e5703f5b1c1723e9a24 | pages/CL/wen_etal_2023_ej_adelaide.pdf | ok |
| https://hull-repository.worktribe.com/OutputFile/3303156 | 2026-10-11T17:38:27Z | - | - | blocked (Cloudflare) |
| https://hal.science/hal-02024317 | 2026-10-11T17:38:51Z | - | - | blocked (Anubis anti-AI-scraping page; not bypassed) |
| https://services.bepress.com/feem/paper1157 | 2026-10-11T17:39:08Z | ad44c1707e81b4a2781828937a3169a570fa4feafa2eaeecd0978791e05073ce | pages/CL/feem_paper1157.html | ok (landing) |
| https://services.bepress.com/cgi/viewcontent.cgi?article=2172&context=feem | 2026-10-11T17:39:38Z | - | - | blocked (405, CAPTCHA) |
| https://ageconsearch.umn.edu/record/205595/files/AAEA_Ye_Karali-2015.pdf | 2026-10-11T17:40:25Z | - | - | blocked (bot check) |
| https://openscholar.uga.edu/record/7887/files/ye_shiyu_201612_phd.pdf | 2026-10-11T17:40Z (approx.) | - | - | blocked (bot check) |
| https://www.ecb.europa.eu/pub/pdf/scpwps/ecbwp1901.en.pdf | 2026-10-11T17:41:15Z | 6bec58a8c4c296fc29ac49998ae1c3aa373b38701b5ad901b6ce948355887d67 | pages/CL/kurov_etal_ecbwp1901.pdf | ok |
| https://web.archive.org/web/20160410024743id_/http://www.api.org:80/products-and-services/statistics/api-weekly-statistical-bulletin | 2026-10-11T17:43:00Z | 0ba4588103e2775d8911c8932c30bc6c1e49bda50bd87d0ae13497c5827d787b | pages/CL/api_wsb_wb20160410.html | ok |
| https://www.api.org/products-and-services/statistics/api-weekly-statistical-bulletin | 2026-10-11T17:43:00Z | b361365937a275f8e4b0f8c006c6d678a8b8b599b375c6d149126ca240e6a5c9 | pages/CL/api_wsb_live.html | ok (no time text in static HTML) |
| https://web.archive.org/web/20140406093608id_/http://www.api.org:80/publications-standards-and-statistics/statistics/api-weekly-statistical-bulletin | 2026-10-11T17:43:48Z | 1c29dac3a4182e743a8412ca0c47722c425a9c047f1547f50b73d263f54851ca | pages/CL/api_wsb_wb20140406.html | ok |
| https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=RWTC&f=A | 2026-10-11T17:44:37Z | dac81c9e17c45108fa88cf3758d2787684773498c4abbdcda526d0ed8d900429 | pages/CL/eia_rwtc_annual.html | ok |
| https://epub.ub.uni-muenchen.de/97149/ | 2026-10-11T17:45:18Z | a657a3a8eda7da3bdf15e8faf99dfaf79c083cd52dc90e264a1c93a76d62af5d | pages/CL/lmu_97149.html | ok (abstract only) |
| https://export.arxiv.org/pdf/2409.12721 | 2026-10-11T17:46:09Z | 09d9d43308f08e7944d133e578721d0beaad65a2b666cb6563c80de38f551b09 | pages/CL/lalor_swishchuk_2409.12721.pdf | ok |
| https://eprints.gla.ac.uk/363707/ | 2026-10-11T17:49:55Z | f8ab6d6550350debf2da3c8ab4f05a37a5ed339f71d8a500a0973f0cc3985a3e | pages/CL/gla_363707.html | ok (abstract) |
| https://eprints.gla.ac.uk/363707/1/363707.pdf | 2026-10-11T17:49:55Z | - | - | blocked (HTTP 401) |

Terms and robots read (UTC 2026-10-11, before each site's first content fetch unless noted):

| Site | What was read | Ruling |
|---|---|---|
| digital.library.adelaide.edu.au | robots.txt (17:36Z): disallows /search, /admin, /submit etc., not /server/api or bitstreams; the PDF's own cover: SAGE green OA, "Users may also download and save a local copy of an article accessed in an institutional repository for the user's personal reference" | allowed; saved for reference |
| hal.science | robots (17:38Z) returned the Anubis page; the page says it protects "against the scourge of AI companies aggressively scraping websites" | not fetched further |
| services.bepress.com | robots.txt (17:39Z): `User-agent: *` disallows /cgi/areyousure.cgi, author dashboards; viewcontent allowed | allowed; blocked in practice by CAPTCHA |
| iaee.org | robots.txt: `Disallow: /cpresources/` | allowed; executive summaries 404 |
| ageconsearch.umn.edu, openscholar.uga.edu | robots.txt: `Disallow: /rss`, `/search`, `/record/*/export/*$` | allowed; bot check blocked |
| ecb.europa.eu | robots.txt `User-agent: *` (no relevant disallow); the WP's notice: reproduction "is permitted only with the explicit written authorisation of the ECB or the authors" | private research copy only; not reproduced |
| api.org | robots.txt: "Policy: Permit all AI and search crawlers", `Allow: /` | allowed |
| web.archive.org | E.14 reading, `reports/stage_e14_briefs/pages/terms_checks.md` rows 5-6 (2026-10-05) | allowed (not cmegroup) |
| eia.gov | E.13/E.14 reading, terms_checks.md row 7 (EIA copyright and reuse page) | allowed |
| epub.ub.uni-muenchen.de, mpra.ub.uni-muenchen.de | robots.txt: `User-agent: *` `Disallow: /cgi/` | allowed |
| eprints.gla.ac.uk | robots.txt: `Disallow: /cgi/`, `/view/subjects` | allowed; PDF restricted |
| export.arxiv.org | robots.txt returned "Rate exceeded" when read at 17:48Z, after the single PDF download at 17:46Z | logged as a lapse: robots read after the fetch |
| hull-repository.worktribe.com | robots behind a Cloudflare challenge | not fetched |

Budget notices: none. WebSearch calls: 25 of about 90 (queries in `pages/CL/search_log.md`).
Firecrawl not used. Cost-hook notices seen (informational only).

## 6. Unfinished and unverified

- Full texts blocked: Rousse and Sevi 2019 (E6), Ye and Karali 2016 (E7), Geman and Li 2018 (E8),
  Borgards et al. 2021 (E9), Haugom et al. 2025 (E10), Wen, Gong, Ma, Xu 2021 Economic Modelling (USO
  first half-hour, not fetched: paywalled), Hull repository item 3303156 (title unknown). All
  secondary-only or gaps; no number from them is used.
- E2's per-trade size is ambiguous: the paper does not state how its "per annum" means are formed;
  both readings are given. Its Sharpe column (19.54 with mean 4.14 and sd 0.21) is internally
  inconsistent with a standard annualised Sharpe; not used.
- API release time 2010-2015: 4:30 pm ET verified only from the 2016-04-10 API page; the 2014 capture
  gives "Tuesday afternoon" without a time; earlier years [secondary-only]. API_DROPPED_WEEKS for
  2010-2019 undetermined (no API calendar for that window).
- FEDERAL_MONDAY_HOLIDAYS and NYSE_NOT_FULL for 2010-2019: no file on disk; derivable, not built.
- OILCAD_DATES 2010-2019: not built; derivable from the E.14 group calendars.
- The arXiv robots.txt was read after the download (rate-limited); logged.
- Two blocked-fetch times were logged after the fact: the UGA thesis (17:40Z, approximate) and the
  FEEM landing page (taken from the saved file's mtime).
- The macro calendar coverage behind g13-g15's FOMC rows is cited to RTY's `shared/macro_calendars.md`,
  which did not exist yet when this file was written.
