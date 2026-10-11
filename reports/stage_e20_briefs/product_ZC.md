# Stage E.20 Part A: product reader ZC (CBOT corn; vehicle ZC)

Reader: ProductReader-ZC-OpusHigh. Written 2026-10-11 (PDT). Shared class notes (also cited by ZS and ZL):
`reports/stage_e20_briefs/shared/grains_class_notes.md`. Raw pages: `reports/stage_e20_briefs/pages/ZC/`.
Machine-readable copy: `reports/stage_e20_briefs/product_ZC.json`.

ZC facts used below (root table): tick $12.50 = 0.25 cents/bu; D8 RT wall 1.496 ticks = $18.70; day-session
RT mean 1.425 ticks; grains group O 08:30, C 13:15, F 13:18 CT; decision times t1 09:00, t2 10:00, t3 11:00,
t4 12:18 (h60 and F only at t4). Conversion: 1 tick = 0.0025/P of notional = 25/P bp, with P in $/bu.
**No public price level was saved** (see section 6). The figures below use P = $4.50/bu (5.56 bp per
tick), marked [assumed], and give P = $6.50 (3.85 bp per tick) as a second case.

## 1. Evidence (intraday, since 2015, ZC or the grains class)

| ID | Effect | Rule (as published) | Hold | Gross per trade | Gross/net | Sample | Decay / OOS | Source | Grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | ROD -> last half-hour momentum, corn | r_LH = a + b r_ROD; r_ROD = close 30 min before the close / prior close - 1; long if r_ROD > 0 | last 30 min of 08:30-13:20 CT (12:50-13:20) | about 1.4 bp, about 0.26 ticks at $4.50 (0.37 at $6.50); derivation below | gross | CN 1982-07-06..2020-05-01, 1-min, 9,462 days | full-sample R2_OOS -0.01% (negative); 2006-06..2020-05 t 2.8 (Fig. 4c, in-sample) | Baltussen, Da, Lammers, Martens, JFE 142 (2021) 377-403; on-disk copy L3774, L3299, L2463 | primary |
| E2 | Same, "Softs" pool (grains, livestock, softs) | same | same | not sized | gross | 1981-04..2020-05 | R2_OOS -0.01% | same, L3715 | primary |
| E3 | Commodity class eta(r_ROD) portfolio | 1/N of commodity futures | last 30 min | 4.34%/yr, SR 1.42, hit 0.56; about 1.72 bp per trade (NQ reader's derivation) | gross | to 2020-05 | class beta 1.59 (t 3.92) in 1974-1999 vs 1.04 (t 2.86) in 2000-2020 | [shared, see shared/baltussen_notes.md] | shared |
| E4 | WASDE surprise response, corn | return over w after release = b0 + b1 News (News from a Bloomberg poll of world ending stocks) | 10 min, 30 min, to the day's close | corn b1: -0.023 (10 min, n.s.), -0.041** (30 min), -0.044* (day); gain from 30 min to close about 0 | gross | 122 WASDE releases, 2010-2021 | corn "adjusts very little past the initial 30-minute time window" | Anderson, McKenzie, Noyes, NCCC-134 2024 | primary (WP) |
| E5 | WASDE-day volatility curve, corn and soybeans | none (volatility) | n/a | no direction | n/a | 2013-01..2023-04, 08:30-14:00 CT | n/a | Lee and Park (2024), summarized by co-author Park (Southern Ag Today) | secondary |
| E6 | Jumps around USDA reports, corn | none | n/a | no direction | n/a | 2008-2015 | n/a | Couleau, Serra, Garcia (NCCC-134 2018; AJAE 2020) | primary (WP) |
| E7 | Corn-soy volatility and spillover, USDA days | none | n/a | no direction; elevated over 1 hour after release | n/a | 11:00 releases | n/a | Bian, Serra, Garcia, NCCC-134 2018 | primary (WP) |
| E8 | Speed of adjustment after the 2013 move to in-session releases | none | n/a | differences "persist only for a handful of trading minutes" | n/a | 2009-2014 | n/a | Adjemian and Irwin, AJAE 2018, p. 1169 (quoted by Isengildina-Massa, VT) | secondary-only |
| E9 | Trend in USDA announcement effects | none (daily volatility) | daily | no direction | n/a | corn, soybeans, multi-decade | "generally increasing trend", with some reports declining | Ying, Chen, Dorfman, NCCC-134 2017 | primary (WP), daily |
| E10 | Limit-day continuation (class: 9 commodities incl. corn) | after a limit-up (limit-down) close, long (short) the next day | next-day close-to-close | pooled: +40 to +62 bp after limit up, -38 to -63 bp after limit down (close-to-close, includes the overnight gap); **corn-specific row not retained** (see section 5); day-session share not published | gross | 1991-01-07..2016-05-23, daily open/close | 90%-of-limit moves: "returns are small" | Janardanan, Qiao, Rouwenhorst, JFM 39(8) 2019 (WP Feb 2017); quotes from E.0 on disk (`reports/stage_e0_research_K6.md` K6-002) | secondary (E.0 on-disk quotes of the WP); not intraday |

Verbatim quotes (location in the saved text):
- E1: Table B3 row `| CN | -0.13(-0.26) | -0.01 | -0.05 | -0.21(-0.41) | 2.89***(3.54) | 0.79(0.42) | 0.21 | 0.03*** | 0.82**(2.09) | 0.05 | -0.01 |`
  (L3774). Columns per the header (L3759 onward): beta_ONFH, R2, R2_OOS, beta_TONFH, beta_M, beta_SLH, R2, R2_OOS,
  **beta_ROD, R2, R2_OOS**. Caption (L3673 onward): "Adjusted R2, R2OOS, and slope coefficients are multiplied by
  100." Sample row: `| Corn futures | CN | 1982-07-06 | 2020-05-01 | 9462 | 08:30-13:20 | Softs |` (L3299).
  Fig. 4(c): `| CN | 10.0 | 2.8 |` (L2463); caption: "Samples range from June 2006 to May 2020."
- E2: `| Softs | 0.25 (0.70) | 0.00 | -0.06 | 0.19 (0.57) | 0.61* (1.70) | 3.50*** (2.62) | 0.09 | -0.14 | 0.65** (2.16) | 0.04 | -0.01 |` (L3715).
- E4: Table 2, "Corn News -0.023 -0.041** -0.044*", "Soy News -0.028 -0.061** -0.124**"; "This figure makes it
  clear that corn adjusts very little past the initial 30-minute time window"; data "spans from 2010 to 2021";
  N = 122 (`anderson_mckenzie_noyes_2024.pdf.txt` lines 149-202). The News variable needs "Bloomberg reports
  on private analyst projections", so it is not causal from bars or calendars.
- E5: "On WASDE days, volatility is comparatively calm into late morning, jumps right after the 11:00 a.m.
  Central Time (CT) release, and then eases within about an hour"; "We study corn and soybean futures from
  January 2013 through April 2023" (`tamu_afpc_wasde_days.txt`).
- E6: "Our results suggest that the real-time trading of major USDA reports has substantially increased the
  frequency and the magnitude of jump risk" (`couleau_serra_garcia_2018.pdf.txt` lines 38-40).
- E7: "The elevated level of volatilities would not settle down within the first hour after announcements"
  (`bian_serra_garcia_2018.pdf.txt` lines 60-61).
- E8: "these differences persist only for a handful of trading minutes. After that, announcement shocks at
  major agricultural markets resemble those that were observed when (trading) timeouts were in effect.
  (p. 1169)" (`vt_isengildina_insights.txt`; secondary quotation of the AJAE paper).
- E9: "USDA reports are still informative and influential in commodity futures markets, with a generally
  increasing trend in the impact of announcement effects, while there are some reports whose impact show a
  declining potential" (`ying_chen_dorfman_2017.pdf.txt` lines 56-58).
- E10 (E.0 on-disk quotes, `reports/stage_e0_research_K6.md` lines 155-158): "For limit up days, the average return
  on the following day is 40 to 62 basis points, and for limit down days, the average return on the following day is
  -38 to -63 basis points" (P-K6-002-b); "a 1% increase in the return calculated from limit day close to
  options-implied prices is associated with a 0.76% increase in the close-to-open futures returns, and 0.15% increase
  in the close-to-close futures returns" (P-K6-002-d). Corn-specific Table 1 and 2 entries were read in a fetch that
  turned out to be disallowed by ou.edu's robots.txt; the file was deleted and those numbers are not used.

**E1 derivation (sizing only; r_ROD is already in the E.20 prompt and is not proposed here).** The expected
last-half-hour move from trading the sign of r_ROD is about b x E|r_ROD|, with b = 0.82/100. The paper
gives no corn r_ROD dispersion. As a stand-in I use the standard deviation of corn's report-day return in
Anderson et al., Table 1: 0.022 ("Day Returns Corn ... 0.022"). It is measured on WASDE days, so it is
likely an upper bound for ordinary days. With E|r| = 0.022 x sqrt(2/pi) = 1.76%, the expected move is
0.0082 x 1.76% = 0.0144% = 1.44 bp. That is 0.26 ticks at $4.50 [assumed], or 0.37 ticks at $6.50. Against
the D8 RT of 1.496 ticks the ratio is 0.17 to 0.25: far under the 1.5x hurdle. The paper's window is also
12:50-13:20 CT, which ends after ZC's F = 13:18 CT.

**Reading of decay and costs.**
- No grains-specific intraday directional rule published since 2015, with a per-trade size, was found.
- The only sized rule is Baltussen et al.'s corn ROD row. It is weak in sample (t 2.09) and has a negative
  out-of-sample R2 over 1982-2020. Its implied gross is about a fifth of ZC's D8 round trip.
- The USDA-window literature (E4 to E9) is about volatility, jumps and adjustment speed. Where direction is
  measured (E4), it needs a proprietary survey. Corn's response is complete by about 30 minutes after the
  11:00 CT release, which leaves nothing for a t4 (12:18) entry to collect.
- Limit continuation (E10) is large close-to-close, but limit days are rare. The paper's own options evidence points to the open gap as the main
  channel. Neither the day-session share nor any post-2014 (variable-limit) figure was found.
- Null and failure results recorded: Lehecka et al. (2014) found no systematic over- or under-reaction
  after reports [secondary-only, pre-2015]. The Aalto thesis has no commodities (ZN reader). The E.13 review
  found no tradable in-session post-release drift (`reports/stage_e13_info_sources.md` 2.4).

## 2. Feature availability (ZC rows, and features reading ZC bars)

Session and calendar basis: `data/calendars/hist2010/grains.json` (E.14; coverage 2010-06-01..2019-05-31; 2,269
trade dates; 0 unsourced) and `data/calendars/grains.py` (2019-05-01..2026-06-19). The grain eras
(sessions, settlement, USDA release times) are in `shared/grains_class_notes.md`. Three facts drive most
"partial" verdicts:
- (a) 2010-06-01..2012-05-18: no ZC bars between 07:15 and 09:30 CT, so no 08:30 bar and no 08:59 bar.
  The decision time t1 (09:00) has no bar at t, so ZC's t1 rows are missing for data reasons in
  2010-07-01..2012-05-18.
- (b) 2012-05-21..2013-04-05: Globex ran continuously from 17:00 to 14:00, so the 08:30 bars exist. The
  calendar's day session was 09:30-14:00, and settlement was 14:00 from 2012-06-25.
- (c) USDA grain reports came out at 07:30 CT before 2013 (markets closed until 2012-05-18) and at 11:00
  CT from January 2013.

| Feature | Legs | Calendars / literals | 2010-2019 (ZC 2010-07-01..2019-05-05) | 2019-2024 | Dates and basis |
|---|---|---|---|---|---|
| `cp1_ret` | ZC (every vehicle; pooled) | grains group calendar; first bar of d at or after 19:00 CT d-1; close(O+29 = 08:59) | partial | yes | 2010-07-01..2012-05-18: no 08:59 bar (fact a), so missing. 2012-05-21..2013-04-05: computable, but the bar is pre-open by the calendar (O 09:30). 2013-04-08 onward: as defined. Evening open 18:00 (to 2012-05-18), 17:00, then 19:00 (from 2013-04-08). |
| `cp2_range`, `cp2_brk` | ZC | bars of d opening in [08:30, 08:45) | partial | yes | Same eras as cp1: missing to 2012-05-18; pre-open by the calendar 2012-05-21..2013-04-05; as defined from 2013-04-08. |
| `cp3_clv` | ZC | previous port-complete day's H, L, C under D6 O 08:30 / C 13:15 (signals._daily, family H) | partial / undetermined | yes | From 2013-04-08 the eras match D6. Before that, the O bar does not exist (to 2012-05-18) and C was 14:00 (2012-06-25..2013-04-05). Whether family H's port-complete test drops those days could not be decided from the calendar files; it is a code question. |
| `k6_wasdepre_drift` (ZC, ZS) | ZC | WASDE dates (k6/_wasde.py), close(10:29) - open(08:30), 11:00 CT release | **no** (calendar absent) | yes | 2019-2024: WASDE_DATES 2019-05-10..2026-06-11, 58 in the window, from the frozen release calendar (sha256 839f2437...). 2010-2019: no WASDE calendar on disk (E.14 releases JSON holds NGS, WPSR and FOMC only). If one were built from ESMIS (dated list back to 1973), the rule's meaning (a pre-release drift) holds only from the first noon-ET WASDE in January 2013. Before that the report came out at 07:30 CT, before the 08:30 bar. Before 2012-05-21 the 08:30 bar does not exist (fact a). |
| `g01_ret30`..`g03_ret120` (G1-G3) | ZC | group calendar; SG-3 lookback must be in-session | partial | yes | Computable at t2, t3 and t4 in every era. At t1, 2010-07-01..2012-05-18 has no bar at t (row missing). From 2013-04-08 the 07:45-08:30 pause makes g01 at 09:00 "not applicable" (SG-3, as in 2019-2024). |
| `g04` (since first bar) | ZC | first bar of the trade date (evening session) | yes | yes | Evening-session bars exist in every era (fact a affects t1 rows only). |
| `g05` overnight gap | ZC | open(O_X 08:30 bar) - close(C_X - 1 = 13:14 bar of the previous trade date) | partial | yes | No 08:30 bar to 2012-05-18 (missing). 2012-05-21..2013-04-05: computable, but 13:14 was not the settlement close from 2012-06-25 (settlement 14:00). As defined from 2013-04-08. |
| `g06`, `g07`, `g09`, `g10` | ZC | bars by t; 20- and 120-date windows | yes (t2-t4); t1 missing to 2012-05-18 | yes | Bars only; fact (a) for t1. |
| `g08` prev-day return | ZC | close(C-1) - open(O) of the previous complete day | partial | yes | As g05: no O bar to 2012-05-18. |
| `g11`, `g12`, `g16` | none | clock; group calendar (month end) | yes | yes | Both group calendars cover their windows (hist2010 grains 2010-06-01..2019-05-31; grains.py 2019-05-01..2026-06-19). |
| `g13_min_to_rel`, `g14_min_since_rel`, `g15_rel_day` | none | ZC's D8 release list: CROP_PROGRESS (Mon 16:00 ET), CROP and WASDE (12:00 ET), CROP_ANNUAL (Jan), FOMC | **partial** (FOMC only) | yes | 2019-2024: frozen release calendar 2019-05-01..2026-06-21, 267 ZC releases in the window. 2010-2019: only FOMC exists (E.14 releases JSON, 72 rows, 2010-06-01..2019-05-31; [shared, see shared/macro_calendars.md]). No 2010-2019 USDA rows exist on disk. Grain Stocks, Acreage and Prospective Plantings are in neither window's ZC list. |
| `g17_nq`, `g17_zn`, `g17_6e`, `g17_cl`, `g17_gc` on ZC rows | NQ, ZN, 6E, CL, GC | each lead's listing and session | per lead reader | per lead reader | [shared: product_NQ/ZN/6E/CL/GC.md]. On ZC rows the decision times are 09:00-12:18 CT, inside every lead's session. |
| `g17_mbt` on ZC rows | MBT | listed 2021 | no | partial (from 2021-05) | Leg outside the 17 roots (brief section 7). |
| `g17_mes` on ZC rows | MES | listed 2019 | no | yes (from 2019-05-06) | Leg outside the 17 roots. |
| `g17_zc` (ZC as G17 lead) on other roots' rows | ZC | ZC listing; ZC session segments; ZC roll-blackout dates | yes (listed), staleness noted | yes | Listing: Globex segments in hist2010 grains.json from 2010-06-01 and grains.py from 2019-05-01; side-by-side electronic since 2006-08-01 [secondary-only]. Not applicable on K6 rows (ZC, ZS, ZL, HE, LE; SG-2 own-cluster rule), so it applies on the other 12 roots. It is as-of (latest ZC bar closed by t), so it is computed but stale when ZC is shut: rates/FX/gold t1 07:50 reads ZC to 07:44 (from 2013-04-08); equity t1 09:00 reads ZC to 07:14 in 2010-07..2012-05-18; every t4 = 14:08 row reads ZC's last bar before 13:15/13:20 (14:00 in 2012-05-21..2013-04-05). ZC roll-blackout dates make it not applicable (V2.2). |
| r_ROD and \|r_ROD\| / median60 (prompt-added; not proposed) | ZC | group C = 13:15 prior close | yes, with an era note | yes | The 13:14 bar exists in every era. Its meaning as "the prior close" differs 2012-06-25..2013-04-05 (settlement 14:00), and hist2010's C is 13:20 from 2015-07-06 (the settlement window stays 13:14-13:15). |
| `k6_crushgap_gap` | ZS (reads ZM, ZL) | | n/a for ZC rows | n/a | ZS rows only (ZS reader). |
| `k6_limitcont_dir` | HE, LE | | n/a | n/a | HE and LE rows only. |
| `k9_anncday` | | | n/a | n/a | Equity vehicles only. |

Fact for the lead: K6-wasdepost-01 (R = close 11:14 - close 10:59 on WASDE days, ZC, known 11:15 CT) is
excluded in V2.3 because the last grain decision time was 11:00 CT. E.20's t4 = 12:18 CT comes after
11:15, so the member's value would be known at t4. Its 2010-2019 calendar has the same gap as
`k6_wasdepre_drift`, and its meaning holds only from January 2013. Literature E4 and E8 say corn's
response is complete within about 30 minutes or less. Whether to include it is the lead's call.

## 3. Proposed features

**None.** Reasons:
1. The only sized intraday directional result for corn is Baltussen et al.'s ROD -> last half-hour row.
   r_ROD is already added by the prompt. Its implied gross (about 0.26-0.37 ticks) is under 0.25x ZC's D8
   RT (1.496 ticks), and its out-of-sample R2 is negative.
2. The USDA-window literature gives direction only through survey surprises (Bloomberg/Reuters polls).
   These are not computable from bars of the 17 roots or from calendars known in advance. The price-only
   results are about volatility. Corn's response is complete within about 30 minutes (E4), so no
   post-release drift is published for a t4 entry.
3. Limit continuation (E10) is sized only close-to-close. The publication points to the next open as the
   main channel and gives no day-session share. Corn limit days are rare, and no figure after 2014's
   variable limits was found. A ZC limit flag therefore cannot be given an expected gross per trade from
   the evidence.
4. The pre-WASDE drift (K6-wasdepre-01's source, Aitkulova et al. 2026) is abstract-only and already a
   member. No new proposal follows from it.

## 4. NQ only

n/a.

## 5. Fetch log, terms read, budget notices

Fetch log (UTC; full sha256 in `product_ZC.json` and `pages/ZC/fetch_log.tsv`):

| URL | UTC | sha256 (first 16) | Path (pages/ZC/) | Status |
|---|---|---|---|---|
| ageconsearch.umn.edu/record/235772/files/AAEA2016_USDA%20Report%20Effects.pdf | 17:37:05Z | a54720d65ef322e6 | (challenge page, deleted) | blocked (AWS WAF, HTTP 202 challenge) |
| ageconsearch.umn.edu/record/285838/files/Bunek_Janzen_NCCC_134_2015.pdf | 17:37:11Z | e57495e855f81e3d | (deleted) | blocked |
| ageconsearch.umn.edu/record/343571/files/27969.pdf | 17:37:18Z | bba181395d3757e7 | (deleted) | blocked |
| same AAEA2016 PDF via `scrapling extract get`; record 235772 via `scrapling extract fetch` | 17:38:14Z, 17:38:23Z | 940a6dc1bbdda082 | aaea2016_usda_report_effects.md, aaea2016_record.md | blocked ("verify that you're not a robot"); stealthy-fetch not used |
| farmdoc.illinois.edu/.../conf_2018/pdf/Bian_Serra_Garcia_NCCC-134_2018.pdf | 17:37:30Z | b162e8b704e5267a | bian_serra_garcia_2018.pdf | ok |
| farmdoc.illinois.edu/.../conf_2018/pdf/Couleau_Serra_Garcia_NCCC-134_2018.pdf | 17:39:52Z | 82de7a764b0ce18e | couleau_serra_garcia_2018.pdf | ok |
| farmdoc.illinois.edu/.../conf_2017/pdf/Ying_Chen_Dorfman_NCCC-134_2017.pdf | 17:40:04Z | 29adee4cc23a5af1 | ying_chen_dorfman_2017.pdf | ok |
| farmdoc.illinois.edu/.../conf_2024/pdf/Yang_McKenzie_NCCC-134_2024.pdf | 17:40:16Z | a4c9fad7c114a9c9 | yang_mckenzie_2024.pdf | ok (not used) |
| farmdoc.illinois.edu/.../conf_2019/pdf/Janzen_Legrand_NCCC-134_2019.pdf | 17:40:28Z | 599ebf53c6a2ea2b | janzen_legrand_2019.pdf | ok (not used) |
| aaec.vt.edu/people/faculty/Isengildina_Olga/report/insights.html | 17:41:11Z | ea535d57f556cf45 | vt_isengildina_insights.html | ok |
| www.k-state.edu/riskmanagement/documents/agcon/Jones.pdf | 17:41:16Z | 27142177879e5599 | kstate_jones_hft.pdf | ok (not used) |
| www.usda.gov/sites/default/files/documents/USDA_Release_time_change_9_19_12.pdf | 17:42:04Z | 8e479d7b2a04d657 | usda_release_time_change_2012-09-19.pdf (403 page) | blocked (Akamai 403; scrapling get/fetch also failed; no Wayback capture) |
| www.govinfo.gov/content/pkg/FR-2012-06-08/pdf/2012-13951.pdf | 17:42:10Z | c4fd596b35cbb0b7 | fr_2012-06-08_nass_release_times.pdf | ok |
| www.nass.usda.gov/Newsroom/printable/2012/08_03_12.pdf | 17:42:19Z | 64329b41a8aa4b72 | nass_newsroom_2012-08-03.pdf | ok |
| www.nass.usda.gov/Newsroom/printable/2012/09_19_12.pdf | 17:42:33Z | 80c3fe2ae1062abf | (deleted) | 404 |
| sat-wp.afpc.tamu.edu/?p=42948 | 17:43:17Z | ec0432ae47cf4fb6 | tamu_afpc_wasde_days.html | ok |
| farmdoc.illinois.edu/.../conf_2024/pdf/Anderson_McKenzie_Noyes_NCCC-134_2024.pdf | 17:43:44Z | e9df84b1f3fdad98 | anderson_mckenzie_noyes_2024.pdf | ok |
| esmis.nal.usda.gov/publication/world-agricultural-supply-and-demand-estimates (+ ?date=2013-01, ?date=2012-12) | 17:44:59Z, 17:45:33Z, 17:45:41Z | 841f5fba837158e1, 573e0704c7cbcc3b, 3ae499e961f6bdb2 | esmis_wasde_*.html | ok |
| www.sec.gov/Archives/edgar/data/1161448/000119312506088998/dex992.htm | 17:46:49Z | b53af5ae543436e6 | sec_cbot_2006_dex992.htm (error page) | blocked (403; SEC requires a declared contact, not supplied) |
| www.ou.edu/.../Janardanan-et-al-Limits%20Paper.pdf | 17:47:15Z | f8a3ed6596667a3d | (deleted) | terms-forbid: fetched before robots.txt was read; robots.txt (after its 301) disallows /content; file deleted at about 17:58Z, numbers not used |
| www.ers.usda.gov/amber-waves/2021/december/usda-s-corn-output-projections-inform-futures-price-movements | 17:48:46Z | 80585ced43681719 | ers_amberwaves_2021_corn_projections.html | ok (not intraday; not used) |
| primary.ers.usda.gov/webdocs/publications/101815/err-293_summary.pdf | 17:48:46Z | none | none | failed (no response) |
| farmdocdaily.illinois.edu/wp-content/uploads/2025/09/fdd091525.pdf | 17:49:23Z | f3302cffd6eb39ac | farmdocdaily_2025-09-15.pdf | ok (no price level found; not used) |
| www.efmaefm.org/.../EndofDayReversal_withnames.pdf | 17:50:40Z | 4a16b6ed72b3404c | baltussen_da_soebhag_eod_reversal_2024.pdf | ok (stocks only; not used) |

On-disk sources used without fetching: `reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md`
(L2463, L3299, L3673, L3715, L3759, L3774); `shared/baltussen_notes.md`; `shared/aalto_thesis_notes.md`;
`reports/stage_e0_research_K6.md` (abstract quotes K6-027, K6-043).

Terms read (robots.txt; a site-terms page was read where noted):
- ageconsearch.umn.edu: robots.txt allows `/record/*/files` (Crawl-Delay 5; disallows /rss, /search). Saved
  `ageconsearch_robots.txt`. Blocked in practice by an AWS WAF bot challenge, so recorded as a gap, not bypassed.
- farmdoc.illinois.edu and farmdocdaily.illinois.edu: robots.txt Crawl-delay 10, no relevant disallow. The first farmdoc PDF (Bian et al., 17:37:30Z) was fetched before farmdoc's robots.txt was read (17:39Z), a slip with no rule broken. Each NCCC-134
  paper carries "Readers may make verbatim copies of this document for non-commercial purposes". Fetches were
  spaced at least 11 s apart.
- aaec.vt.edu: robots.txt first redirected (301) and was not followed before the fetch (a slip). Followed later: `User-agent: * / Disallow:` (all allowed).
- k-state.edu: robots.txt disallows only /KSU_resources/.
- usda.gov: robots.txt returned Akamai 403 ("Access Denied"); no page obtained.
- nass.usda.gov: robots.txt (read 14 s after the 08_03_12 fetch, a slip) disallows /Quick_Stats/CDQT/ only.
- esmis.nal.usda.gov: robots.txt (Drupal default) disallows admin, search and user paths only; the publication page is allowed.
- sat-wp.afpc.tamu.edu: Yoast robots, `Disallow:` empty (all allowed).
- ou.edu: robots.txt first returned a 301 that was not followed, so the PDF was fetched before the rules were read (a process slip). Followed later: `Disallow: /content`. The PDF was deleted and its corn-specific figures are not used; E.0's on-disk quotes of the same paper are cited instead.
- govinfo.gov: US government public document (Federal Register); robots.txt has no rule on /content.
- sec.gov: robots.txt page itself returned "Request Rate Threshold Exceeded"; no content used.
- efmaefm.org: robots.txt returned 404 (none).
- ers.usda.gov: robots.txt (Drupal default) disallows /core/ and /profiles/ only.

Budget notices: none. WebSearch calls used: about 22 of the 90 budget. No Firecrawl calls.

Process incident (reported, not hidden): the session scratchpad is shared by all readers, and another reader
overwrote my first fetch helper (`scratchpad/fetch.sh`). My first four fetches (17:37:05Z-17:37:30Z) were therefore
written into `pages/LE/` and logged in `pages/LE/fetch_log.tsv`. I moved those files to `pages/ZC/` and removed only
those four lines from the LE log (the LE reader's own lines, its robots.txt fetches at 17:36Z, were left as they
were). All later fetches used `scratchpad/zc_reader/zcfetch.sh`. The LE reader may want to check its log.

## 6. Unfinished and unverified items

- **Public price level for the bp-to-tick conversion not saved.** E1 uses P = $4.50/bu [assumed] and
  $6.50/bu. The formula (1 tick = 25/P bp) is exact. Neither conclusion changes for any P between $3 and $8.
- **E1's r_ROD dispersion is a stand-in**: Anderson et al.'s WASDE-day corn day-return sd (0.022), not the paper's own figure.
- **USDA's 2012-09-19 release-time decision** (usda.gov) is blocked (403). The January 2013 noon-ET switch is verified
  only through two academic papers (Couleau et al.; Bian et al.). The pre-change 8:30 ET time is verified through USDA's
  own FR notice and NASS news release.
- **Adjemian and Irwin (AJAE 2018)**: [secondary-only] (VT quotation). AgEcon Search blocks every paper hosted only there
  (AAEA 2016 Joseph-Garcia, Bunek-Janzen 2015, Aitkulova et al. 2026, Zhu et al. 2026).
- **2006-08-01 side-by-side electronic listing of corn**: [secondary-only] (cmegroup press-release snippets; SEC copy blocked).
- **ESMIS completeness 2010-2019**: dated entries confirmed for 2012-12; the 2013-01 filter returned no dated entry. Month-by-month
  completeness was not audited (a calendar build would need that).
- **cp3_clv 2010-2013**: whether family H's port-complete test excludes days without an 08:30 O bar is a code question,
  left undetermined.
- **Post-2014 limit-move evidence for corn** (variable limits from 2014-05-01): not found; the 2014 rule change itself is a
  search snippet only [unverified].
- No grains-specific intraday momentum, reversal, settlement-window or lunchtime study since 2015 was found. That is a gap
  in what was found, not evidence that such an effect is absent.
