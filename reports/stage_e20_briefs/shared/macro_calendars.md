# Macro release calendars behind g13-g15 and k9_anncday: causal coverage over both windows

Reader: ProductReader-RTY-OpusHigh (Stage E.20 Part A, shared assignment). Written 2026-10-11.
Other readers cite this file as `reports/stage_e20_briefs/shared/macro_calendars.md` for
`g13_min_to_rel`, `g14_min_since_rel`, `g15_rel_day` and `k9_anncday`.
Basis: the calendar files and their source notes only (dates, counts, grades). No bar was read.
The coverage ruling (the F6 cut) is the lead's; this file gives facts.

Windows: backward = each root's 2010-2019 window (root table; ends 2019-05-05); search =
2019-05-06..2024-02-29.

## 1. What the features read (code)

- `g13_min_to_rel`, `g14_min_since_rel`, `g15_rel_day` (`ml_route_v2/signals/generic.py` lines 19-20,
  277-312): minutes to the next release at or after t, minutes since the last before t, and a
  release-day flag, from "the vehicle's D8 list", via `release_times(ctx.releases, v)`; rows outside
  `release_coverage(ctx.releases)` are not applicable. The release source is the frozen calendar
  `reports/stage_e2b_release_calendar.json` (schema `stage_e_release_calendar/1`, loaded by
  `screening.stage_e_rules.load_release_calendar`, `RELEASE_CALENDAR_PATH`, line 98).
- `k9_anncday` (`ml_route_v2/signals/k9.py`): 1 on an EC-K9 trade date on MNQ, M2K and MYM rows
  (VEHICLES, line 60); training-window set from `reports/stage_e12_ec_k9_2019_2024.json`
  (TRAIN_WINDOW 2019-05-01..2024-02-29), research-window set from the K9 catalog. EC-K9 = FOMC
  statement days, NFP, GDP first and last estimates, ISM manufacturing, the earlier of CPI and PPI
  per reference month.

## 2. Files on disk (every macro release file found)

| File | sha256 (prefix) | Releases | Coverage (file's own field) | Grade notes |
|---|---|---|---|---|
| `reports/stage_e2b_release_calendar.json` (frozen; D8 list per product) | 839f2437bedbeb7b | 14 types, 2,609 rows | 2019-05-01..2026-06-21 | evidence "verified" for FOMC 57, NFP 85, ISM_SERVICES 86, CPI 85, PPI 85, G17 85 (all rows); NGS 365 of 373 "unverified" (EIA standing rule, lead-ruled kept); API_WSB "announced_schedule"; 1 known gap (G.17 2025-11-24 revision, outside both windows) |
| `reports/stage_e12_ec_k9_2019_2024.json` (EC-K9, training window) | b9297ae81a2f08df | FOMC 38, NFP 58, GDP_first_last 38, ISM_manufacturing_scheduled 58, inflation (earlier of CPI/PPI) 58; union 240 dates | window 2019-05-01..2024-02-29, `uncovered_spans` [] | official Fed, BLS, BEA, ISM pages (ISM via Wayback); ex-ante check "minimum lead over all 250 component dates is 4 days"; FOMC, NFP, CPI, PPI agree with the frozen calendar (cross_check) |
| `reports/stage_e14_cal_releases.json` (E.14, 2010-2019) | 9a051211fe381cd2 | NGS 470, WPSR 470, FOMC 72 | 2010-06-01..2019-05-31 | FOMC: 58 official times, 14 inferred (all 2010-06-23..2013-01-30, 14:15 ET for non-press-conference meetings); dates all official |
| `reports/stage_e16_calendars/ec_auc_2010_2019.json` (E.16) | e3b5f4522dad8e8d | TREASURY_AUCTION | 2010-01-01..2019-06-30 | FiscalData; sha256 matches the E.16 F-04 rebuild note (stage_e16_calendars.md line 274), not the line-11 original (0c21ce85...) |
| `reports/stage_d1f_release_sources.md/.json` (D.1f) | (not hashed) | FOMC 38, CPI 58, NFP 58, ... | 2019-05-01..2024-02-29 | primary Fed/BLS pages; corroboration only, not loaded by the code |

No file on disk covers NFP, CPI, PPI, GDP, ISM services or ISM manufacturing before 2019-05-01
(searched: `reports/`, `data/calendars/`, `data/calendars/hist2010/`, E.14, E.16, E.18, E.19 briefs,
by file name and by grep for "nonfarm", "NFP", "ISM", "CPI").
The frozen calendar has no GDP and no ISM-manufacturing rows at all (those exist only in EC-K9);
PPI rows list only MBT.

## 3. Coverage by release type

| Release (time ET) | 2010-07..2019-05-05 | 2019-05-06..2024-02-29 |
|---|---|---|
| FOMC statement (14:00; 14:15 or 12:30-12:35 before 2013) | yes: E.14, 72 statements 2010-06-23..2019-05-01; 71 inside 2010-07-01..2019-05-05; 15 inside 2017-07-10..2019-05-05, all 14:00 official | yes: frozen calendar 37 in window (57 over 2019-05-01..2026-06-17); EC-K9 FOMC 38 (incl. 2019-05-01) |
| NFP (08:30) | no file | yes: frozen 57 in window; EC-K9 58 |
| CPI (08:30) | no file | yes: frozen 58 in window; inside EC-K9 inflation set |
| PPI (08:30) | no file | yes: frozen 58 in window (MBT only); inside EC-K9 inflation set |
| GDP first and last (08:30) | no file | EC-K9 only: 38 (2019-06-27..2024-01-25); not in the frozen calendar |
| ISM services (10:00) | no file | yes: frozen 57 in window |
| ISM manufacturing (10:00) | no file | EC-K9 only: 58 (2019-05-01..2024-02-01); not in the frozen calendar |
| EC-K9 union (k9_anncday) | no file (FOMC component only exists) | yes: 240 dates, no uncovered span |

Non-macro D8 types for context (class readers own them): WPSR and NGS 2010-2019 exist (E.14);
TREASURY_AUCTION 2010-2019 exists (E.16); WASDE, CROP, CROP_ANNUAL, CROP_PROGRESS, G17, API_WSB:
no 2010-2019 file found by this reader (grains, metals and energy readers to confirm).

## 4. Per-root D8 list (frozen calendar `release_products`) and what that implies

Counts are release rows in 2019-05-06..2024-02-29 on the root's vehicle (not de-duplicated
instants; CROP and WASDE share instants, so E.11's ZC figure of 267 instants differs from 330 rows).

| Root (vehicle) | D8 list | Rows in search window | 2010-2019 types with a file | 2010-2019 types without a file |
|---|---|---|---|---|
| NQ (MNQ) | NFP, CPI, FOMC, ISM_SERVICES | 209 | FOMC | NFP, CPI, ISM_SERVICES |
| RTY (M2K) | NFP, FOMC, ISM_SERVICES | 151 | FOMC | NFP, ISM_SERVICES |
| ZT, ZF, TN, UB | NFP, FOMC, TREASURY_AUCTION | 488 each | FOMC, TREASURY_AUCTION | NFP |
| ZN, ZB | NFP, FOMC, ISM_SERVICES, TREASURY_AUCTION | 545 each | FOMC, TREASURY_AUCTION | NFP, ISM_SERVICES |
| 6E | NFP, FOMC | 94 | FOMC | NFP |
| GC (MGC) | NFP, CPI, FOMC, G17 | 210 | FOMC | NFP, CPI, G17 |
| CL (MCL) | FOMC, WPSR, NGS, API_WSB | 791 | FOMC, WPSR, NGS | API_WSB |
| NG | FOMC, WPSR, NGS | 539 | FOMC, WPSR, NGS | none |
| ZC | FOMC, CROP, CROP_ANNUAL, WASDE, CROP_PROGRESS | 330 | FOMC | CROP, CROP_ANNUAL, WASDE, CROP_PROGRESS (unless the grains reader finds one) |
| ZS, ZL, HE, LE | FOMC, CROP, CROP_ANNUAL, WASDE | 158 each | FOMC | CROP, CROP_ANNUAL, WASDE (unless found) |

Facts for the lead's cut:
- `g13`/`g14`/`g15` exist causally over the search window for all 17 roots (frozen calendar,
  2019-05-01..2026-06-21, every root listed).
- Over 2010-2019 they are complete only for NG (FOMC, WPSR, NGS all on file). For every other root,
  only part of the D8 list has a 2010-2019 file: computing g13-g15 from that part would give a
  different variable (for example, minutes to the next FOMC only, instead of to the next of NFP,
  FOMC and ISM services). Status: partial (2010-2019), with the missing types listed above.
- `k9_anncday` (MNQ, M2K, MYM rows; of the 17 roots only NQ and RTY): yes 2019-05-01..2024-02-29;
  no 2010-2019 (no NFP, GDP, ISM manufacturing, CPI or PPI file; FOMC alone exists).
- The FOMC statement calendar is the one macro calendar on file for both windows: 2010-06-01..
  2019-05-31 (E.14) and 2019-05-01..2026-06-21 (frozen), overlapping in May 2019. A feature built on
  FOMC alone would meet the both-windows calendar condition.
- Unscheduled FOMC actions: excluded from EC-K9 by lead ruling (2019-10-11, 2020-03-03, 2020-03-15,
  notation votes; and 2020-03-18, the cancelled scheduled statement); the frozen calendar lists the
  2020-03-17/18 meeting under `cancellations`. E.14 lists scheduled meetings and conference calls
  (stage_e14_cal_releases.md, Method); whether its 72 rows include any unscheduled call statement was
  not checked here (no row id mentions "unscheduled").

## 5. If a 2010-2019 macro calendar were built (not done here; for the lead)
- Sources named in the existing builders' notes: Fed FOMC historical pages (E.14), BLS schedule and
  archive pages, BEA release schedule, ISM calendar via Wayback (E.12 method). The E.12 builder used
  Wayback captures to show each date was announced in advance; the same ex-ante test would apply.
- Hazard to check in any build [unverified here]: delayed or rescheduled federal releases in
  2010-2019 (for example during federal funding lapses) would need the actual and the pre-announced
  dates; the frozen calendar's `cancellations` field shows how 2025's lapse was handled.
