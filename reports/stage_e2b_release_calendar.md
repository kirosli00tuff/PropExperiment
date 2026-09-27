# Stage E.2b release calendar (summary)

File: `reports/stage_e2b_release_calendar.json` (schema `stage_e_release_calendar/1`), sha256 `839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8`. Built 2026-09-26 17:08 PDT by `screening/build_release_calendar.py` (`uv run --no-sync python -m screening.build_release_calendar`; `--check` rebuilds in memory and compares byte for byte). Coverage 2019-05-01..2026-06-21. Rulings: OC-J, OC-N and the lead's two commodity rulings (NGS kept as unverified; CROP_ANNUAL kept, instants de-duplicated per product).

## Totals

- Entries: 2609 (macro 227, commodity 921, named 1461); verified 1872, [unverified] 365, announced_schedule 372. All are kept and carry products.
- **NGS (EIA Weekly Natural Gas Storage Report): 365 of 373 entries are [unverified]** (EIA's standing Thursday 10:30 ET rule, and the Wednesday 12:00 ET holiday weeks by EIA's documented practice; the per-week WNGSR pages were unreachable on Wayback). Kept and counted, per the lead's ruling.
- API bulletin: 372 entries dated from API's announced annual schedules (publication not confirmed per week); kept and counted.
- Cancelled (no entry): 14 (CPI 1, CROP 1, CROP_PROGRESS 6, FOMC 1, G17 2, NFP 1, PPI 1, WASDE 1).
- Instants shared by more than one entry: 85 (e.g. CROP, WASDE and the January CROP_ANNUAL at 12:00 ET); the loader keeps one instant per product.

## Entries per release and year

| Release | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | Total | Unverified | Announced | Cancelled |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NFP | 8 | 12 | 12 | 12 | 12 | 12 | 11 | 6 | 85 | 0 | 0 | 1 |
| CPI | 8 | 12 | 12 | 12 | 12 | 12 | 11 | 6 | 85 | 0 | 0 | 1 |
| FOMC | 6 | 7 | 8 | 8 | 8 | 8 | 8 | 4 | 57 | 0 | 0 | 1 |
| WPSR | 35 | 53 | 52 | 51 | 51 | 52 | 53 | 24 | 371 | 0 | 0 | 0 |
| NGS | 35 | 53 | 52 | 52 | 52 | 52 | 53 | 24 | 373 | 365 | 0 | 0 |
| CROP | 8 | 12 | 12 | 12 | 12 | 12 | 11 | 6 | 85 | 0 | 0 | 1 |
| CROP_ANNUAL | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 7 | 0 | 0 | 0 |
| WASDE | 8 | 12 | 12 | 12 | 12 | 12 | 11 | 6 | 85 | 0 | 0 | 1 |
| PPI | 8 | 12 | 12 | 12 | 12 | 12 | 10 | 7 | 85 | 0 | 0 | 1 |
| ISM_SERVICES | 8 | 12 | 12 | 12 | 12 | 12 | 12 | 6 | 86 | 0 | 0 | 0 |
| G17 | 8 | 12 | 12 | 12 | 12 | 12 | 11 | 6 | 85 | 0 | 0 | 2 |
| API_WSB | 35 | 52 | 52 | 52 | 52 | 53 | 52 | 24 | 372 | 0 | 372 | 0 |
| CROP_PROGRESS | 32 | 35 | 35 | 35 | 35 | 35 | 28 | 11 | 246 | 0 | 0 | 6 |
| TREASURY_AUCTION | 48 | 80 | 84 | 84 | 84 | 84 | 84 | 39 | 587 | 0 | 0 | 0 |

## Products per release

F6.4 roots outside rules/products.py (the loader refuses unknown roots) are not written: NFP: 6M GE MET NKD; FOMC: 6M MET NKD PL.

| Release | F6.4 row | F6.4 roots (in table) | Micro siblings | Member-named roots | Products |
|---|---|---|---|---|---|
| NFP | Unemployment Rate | 6A 6B 6C 6E 6J 6N 6S E7 ES GC HG M6A M6E MBT NQ RTY SI TN UB YM ZB ZF ZN ZT | M2K M6B MES MGC MHG MNQ MYM SIL | 6A 6B 6C 6E 6J 6N 6S GC HG MBT MGC MHG SI ZN | 32 |
| CPI | - | - | - | GC HG MBT MGC MHG MNQ NQ SI | 8 |
| FOMC | FOMC Statement | all 46 universe roots | MES | 6A 6B 6C 6E 6J 6N 6S CL GC HE HG HO LE M2K MBT MCL MGC MHG MNQ MYM NG NQ RB RTY SI TN UB YM ZB ZC ZF ZL ZM ZN ZS ZT ZW | 47 |
| WPSR | Crude Oil Inventories (EIA) | CL MCL QM RB | - | 6C CL HO MCL NG RB | 7 |
| NGS | Natural Gas Inventories (EIA) | NG QG | MNG | CL HO MCL NG RB | 7 |
| CROP | Crop Production | ZC ZL ZM ZS ZW | - | HE LE ZC ZL ZM ZS ZW | 7 |
| CROP_ANNUAL | Crop Production | ZC ZL ZM ZS ZW | - | HE LE ZC ZL ZM ZS ZW | 7 |
| WASDE | - | - | - | HE LE ZC ZL ZM ZS ZW | 7 |
| PPI | - | - | - | MBT | 1 |
| ISM_SERVICES | - | - | - | M2K MNQ MYM NQ RTY YM ZB ZN | 8 |
| G17 | - | - | - | GC HG MGC MHG SI | 5 |
| API_WSB | - | - | - | CL MCL | 2 |
| CROP_PROGRESS | - | - | - | ZC | 1 |
| TREASURY_AUCTION | - | - | - | TN UB ZB ZF ZN ZT | 6 |

## Product universe

In the product table (46): 6A 6B 6C 6E 6J 6N 6S CL E7 ES GC HE HG HO LE M2K M6A M6B M6E MBT MCL MGC MHG MNG MNQ MYM NG NQ QG QM RB RTY SI SIL TN UB YM ZB ZC ZF ZL ZM ZN ZS ZT ZW. Not in it, not written: 6M MET NKD PL. MES is added to NFP and FOMC as the micro sibling of ES.

## Distinct release instants per product

| Root | Distinct instants | Releases |
|---|---|---|
| 6A | 142 | NFP FOMC |
| 6B | 142 | NFP FOMC |
| 6C | 513 | NFP FOMC WPSR |
| 6E | 142 | NFP FOMC |
| 6J | 142 | NFP FOMC |
| 6N | 142 | NFP FOMC |
| 6S | 142 | NFP FOMC |
| CL | 1173 | FOMC WPSR NGS API_WSB |
| E7 | 142 | NFP FOMC |
| ES | 142 | NFP FOMC |
| GC | 312 | NFP CPI FOMC G17 |
| HE | 142 | FOMC CROP CROP_ANNUAL WASDE |
| HG | 312 | NFP CPI FOMC G17 |
| HO | 801 | FOMC WPSR NGS |
| LE | 142 | FOMC CROP CROP_ANNUAL WASDE |
| M2K | 228 | NFP FOMC ISM_SERVICES |
| M6A | 142 | NFP FOMC |
| M6B | 142 | NFP FOMC |
| M6E | 142 | NFP FOMC |
| MBT | 312 | NFP CPI FOMC PPI |
| MCL | 1173 | FOMC WPSR NGS API_WSB |
| MES | 142 | NFP FOMC |
| MGC | 312 | NFP CPI FOMC G17 |
| MHG | 312 | NFP CPI FOMC G17 |
| MNG | 430 | FOMC NGS |
| MNQ | 313 | NFP CPI FOMC ISM_SERVICES |
| MYM | 228 | NFP FOMC ISM_SERVICES |
| NG | 801 | FOMC WPSR NGS |
| NQ | 313 | NFP CPI FOMC ISM_SERVICES |
| QG | 430 | FOMC NGS |
| QM | 428 | FOMC WPSR |
| RB | 801 | FOMC WPSR NGS |
| RTY | 228 | NFP FOMC ISM_SERVICES |
| SI | 312 | NFP CPI FOMC G17 |
| SIL | 142 | NFP FOMC |
| TN | 729 | NFP FOMC TREASURY_AUCTION |
| UB | 729 | NFP FOMC TREASURY_AUCTION |
| YM | 228 | NFP FOMC ISM_SERVICES |
| ZB | 815 | NFP FOMC ISM_SERVICES TREASURY_AUCTION |
| ZC | 388 | FOMC CROP CROP_ANNUAL WASDE CROP_PROGRESS |
| ZF | 729 | NFP FOMC TREASURY_AUCTION |
| ZL | 142 | FOMC CROP CROP_ANNUAL WASDE |
| ZM | 142 | FOMC CROP CROP_ANNUAL WASDE |
| ZN | 815 | NFP FOMC ISM_SERVICES TREASURY_AUCTION |
| ZS | 142 | FOMC CROP CROP_ANNUAL WASDE |
| ZT | 729 | NFP FOMC TREASURY_AUCTION |
| ZW | 142 | FOMC CROP CROP_ANNUAL WASDE |

## Word to roots (member-named releases)

A member's traded exposures are its catalog `exposures` words; each maps to the exposure's frozen vehicle root and ML price-path root. Starred products that are neither (SIL, M6E, M6A) are not added by this rule.

| Word | Exposure (stage_e2a_vehicles.json) | Roots |
|---|---|---|
| AUD | AUD | 6A |
| CAD | CAD | 6C |
| CHF | CHF | 6S |
| Dow | Dow | MYM YM |
| EUR | EUR | 6E |
| GBP | GBP | 6B |
| HE | lean hogs | HE |
| JPY | JPY | 6J |
| LE | live cattle | LE |
| NZD | NZD | 6N |
| Nasdaq-100 | Nasdaq-100 | MNQ NQ |
| RBOB | RBOB | RB |
| Russell 2000 | Russell 2000 | M2K RTY |
| TN | Ultra 10-year | TN |
| UB | Ultra bond | UB |
| ULSD | ULSD | HO |
| ZB | Bond | ZB |
| ZC | corn | ZC |
| ZF | 5-year | ZF |
| ZL | soybean oil | ZL |
| ZM | soybean meal | ZM |
| ZN | 10-year | ZN |
| ZS | soybeans | ZS |
| ZT | 2-year | ZT |
| ZW | wheat | ZW |
| bitcoin | bitcoin | MBT |
| copper | copper | HG MHG |
| crude | WTI crude | CL MCL |
| gas | Henry Hub gas | NG |
| gold | gold | GC MGC |
| silver | silver | SI |

## Naming members by status

Every catalog status counts (PPI and Crop Progress are named only by members the ML route superseded, and the lead's list includes them).

| Release | Naming members by catalog status |
|---|---|
| NFP | active: K3-cp3-01, K3-ecbfix-01, K5-cp2-01, K5-cp3-01, K5-ovr-01, K7-expiry-01, K8-flight-01; excluded_superseded_ml_route: K2-ml-01, K3-ml-01, K5-ml-01, K7-ml-01 |
| CPI | active: K5-cp1-01, K5-cp2-01, K5-ovr-01, K8-flight-01, K8-wkndbtc-01; excluded_superseded_ml_route: K1-ml-01, K5-ml-01, K7-ml-01 |
| FOMC | active: K1-cp1-01, K1-cp2-01, K1-cp3-01, K1-vwap-01, K1-vxnband-01, K2-cp1-01, K2-cp3-01, K2-fomcpost-01, K3-cp1-01, K3-cp3-01, K3-ecbfix-01, K4-cp1-01, K4-cp2-01, K4-cp3-01, K5-cp2-01, K5-fomc-01, K5-ovr-01, K6-cp1-01, K6-cp3-01, K7-cp1-01, K7-cp2-01, K7-cp3-01, K7-rev2h-01, K8-flight-01, K8-oilcad-01; excluded_by_lead: K6-ovr-01; excluded_superseded_ml_route: K1-ml-01, K2-ml-01, K3-ml-01, K4-ml-01, K5-ml-01, K6-ml-01, K7-ml-01, K8-ml-01 |
| WPSR | active: K4-apipre-01, K4-cp3-01, K4-eiafade-01, K4-eiamom-01, K4-ovr-01, K8-oilcad-01; excluded_superseded_ml_route: K4-ml-01, K8-ml-01 |
| NGS | active: K4-cp3-01, K4-ngpre-01; excluded_by_lead: K4-ngrev-01; excluded_superseded_ml_route: K4-ml-01 |
| CROP | active: K6-cp2-01, K6-cp3-01, K6-crushgap-01, K6-limitcont-01, K6-wasdepost-01, K6-wasdepre-01; excluded_by_lead: K6-ovr-01; excluded_superseded_ml_route: K6-ml-01 |
| CROP_ANNUAL | active: K6-cp2-01, K6-cp3-01, K6-crushgap-01, K6-limitcont-01, K6-wasdepost-01, K6-wasdepre-01; excluded_by_lead: K6-ovr-01; excluded_superseded_ml_route: K6-ml-01 |
| WASDE | active: K6-cp2-01, K6-cp3-01, K6-crushgap-01, K6-limitcont-01, K6-wasdepost-01, K6-wasdepre-01; excluded_by_lead: K6-ovr-01; excluded_superseded_ml_route: K6-ml-01 |
| PPI | excluded_superseded_ml_route: K7-ml-01 |
| ISM_SERVICES | active: K1-cp1-01, K1-cp2-01, K1-cp3-01, K2-predrift-01; excluded_by_lead: K1-predrift-01; excluded_superseded_ml_route: K1-ml-01, K2-ml-01 |
| G17 | active: K5-cp2-01, K5-cp3-01, K5-ovr-01 |
| API_WSB | active: K4-apipre-01; excluded_superseded_ml_route: K4-ml-01 |
| CROP_PROGRESS | excluded_superseded_ml_route: K6-ml-01 |
| TREASURY_AUCTION | active: K2-aucpost-01, K2-aucpre-01, K2-cp3-01; excluded_superseded_ml_route: K2-ml-01 |

## Local release times

| Release | Local times (America/New_York): count |
|---|---|
| NFP | 08:30: 85 |
| CPI | 08:30: 85 |
| FOMC | 14:00: 57 |
| WPSR | 10:30: 317, 11:00: 43, 12:00: 9, 13:00: 1, 17:00: 1 |
| NGS | 10:30: 358, 12:00: 15 |
| CROP | 12:00: 85 |
| CROP_ANNUAL | 12:00: 7 |
| WASDE | 12:00: 85 |
| PPI | 08:30: 85 |
| ISM_SERVICES | 10:00: 86 |
| G17 | 09:15: 85 |
| API_WSB | 16:30: 372 |
| CROP_PROGRESS | 16:00: 245, 17:00: 1 |
| TREASURY_AUCTION | 10:00: 1, 11:30: 34, 13:00: 552 |

## Excluded by ruling

- CME CF Bitcoin Reference Rate (BRR) final settlement (named by K7-expiry-01, K7-ml-01): lead ruling OC-N: not a release of information, and daily, so already inside E.2a's time-of-day cost buckets.
- ECB reference-rate fix (WM/Reuters) (named by K3-ecbfix-01, K3-ml-01): lead ruling OC-N: not a release of information, and daily, so already inside E.2a's time-of-day cost buckets.
- LBMA gold PM auction (named by K5-cp3-01, K5-ml-01, K5-pmfix-01): lead ruling OC-N: not a release of information, and daily, so already inside E.2a's time-of-day cost buckets.
- LBMA gold/silver AM auction (named by K5-ml-01, K5-preauc-01): lead ruling OC-N: not a release of information, and daily, so already inside E.2a's time-of-day cost buckets.
- London 4pm fix (WM/Reuters) (named by K3-cp3-01, K3-ldnmom-01, K3-ldnrev-01, K3-mehedge-01, K3-ml-01): lead ruling OC-N: not a release of information, and daily, so already inside E.2a's time-of-day cost buckets.
- Tokyo 9:55 fix (gotobi) (named by K3-tkypost-01, K3-tkypre-01): lead ruling OC-N: not a release of information, and daily, so already inside E.2a's time-of-day cost buckets.

## Cancellations (no entry)

| Source | Release | Reference period | Originally scheduled | Reason |
|---|---|---|---|---|
| macro | NFP | October 2025 | 2025-11-07 08:30 America/New_York | 2025 lapse in federal appropriations; not published |
| macro | CPI | October 2025 | 2025-11-13 08:30 America/New_York | 2025 lapse in federal appropriations; not published |
| macro | FOMC | March 17-18, 2020 regularly scheduled meeting | 2020-03-18 14:00 America/New_York | meeting cancelled (the Fed's historical page marks it cancelled); no statement release |
| commodity | CROP | October 2025 | 2025-10-09 12:00 America/New_York | 2025 lapse in federal appropriations; not released |
| commodity | WASDE | October 2025 | 2025-10-09 12:00 America/New_York (the Crop Production date; WASDE is released with Crop Production) | 2025 lapse in federal appropriations; no October 2025 WASDE was published |
| named | PPI | October 2025 | 2025-11-14 08:30 America/New_York | 2025 lapse in federal appropriations; not published |
| named | G17 | 2025-10 release month | [unverified] (no pre-shutdown copy of the release-dates table could be fetched: web.archive.org unreachable during this run) | no G.17 release in this month (2025 federal shutdown delayed source data; September data came out 2025-12-03, October and November data 2025-12-23) |
| named | G17 | 2025-11 release month | [unverified] (no pre-shutdown copy of the release-dates table could be fetched: web.archive.org unreachable during this run) | no G.17 release in this month (2025 federal shutdown delayed source data; September data came out 2025-12-03, October and November data 2025-12-23) |
| named | CROP_PROGRESS | issue due 2025-10-06 | 2025-10-06 16:00 America/New_York (standing Monday 4:00 pm ET; Tuesday after the Columbus Day holiday) | 2025 lapse in federal funding; will not be released |
| named | CROP_PROGRESS | issue due 2025-10-14 | 2025-10-14 16:00 America/New_York (standing Monday 4:00 pm ET; Tuesday after the Columbus Day holiday) | 2025 lapse in federal funding; will not be released |
| named | CROP_PROGRESS | issue due 2025-10-20 | 2025-10-20 16:00 America/New_York (standing Monday 4:00 pm ET; Tuesday after the Columbus Day holiday) | 2025 lapse in federal funding; will not be released |
| named | CROP_PROGRESS | issue due 2025-10-27 | 2025-10-27 16:00 America/New_York (standing Monday 4:00 pm ET; Tuesday after the Columbus Day holiday) | 2025 lapse in federal funding; will not be released |
| named | CROP_PROGRESS | issue due 2025-11-03 | 2025-11-03 16:00 America/New_York (standing Monday 4:00 pm ET; Tuesday after the Columbus Day holiday) | 2025 lapse in federal funding; will not be released |
| named | CROP_PROGRESS | issue due 2025-11-10 | 2025-11-10 16:00 America/New_York (standing Monday 4:00 pm ET; Tuesday after the Columbus Day holiday) | 2025 lapse in federal funding; will not be released |

## Known gaps

- G.17's 2025-11-24 annual revision (a standalone publication quoted on the 2025-12-03 G.17 release page) is not entered (lead list, ruling OC-N); the named source did not audit whether other years' annual revisions were published on separate dates (reports/stage_e2b_release_sources_named_log.md).

## Verification

- Quotes 2609/2609, instants 2609/2609, cancellation and move evidence quotes 53/53.
- Vehicle and price-path roots with equal instant lists: 31 exposures.
- Loader round trip: {"roots": 47, "cpi_instants": 85, "instants_per_root_min": 142, "instants_per_root_max": 1173}.
- Method: quotes: whitespace-normalised substring of the strict-UTF-8 saved page; instants: date + time_local in tz via zoneinfo equals instant_utc; coverage tables recounted from entries and cancellations; loader: screening.stage_e_rules.release_calendar_from_dict on the built dict.
