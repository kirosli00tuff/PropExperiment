# Stage E.2a Task 6: CME Globex calendar, energy group (CL, MCL, QM, NG, MNG, QG, RB, HO)

Worker CalendarBuilder-Energy-OpusXHigh, written 2026-09-25 01:14 PDT. Sourcing, code and synthetic tests only: no market data was opened. Module `data/calendars/energy.py` (sha256 `ef90ef8d19df6e2d...`), tests `tests/test_e2a_calendar_energy.py`, full records in `reports/stage_e2a_calendar_sources_energy.json`.

## Summary

- Coverage 2019-05-01..2026-06-19: 79 entries, 20 full closures and 59 early halts or early closes; 1 late open (LATE_OPENS, additive extension); 19 CME-stated normal days recorded as NO_ENTRY_FINDINGS.
- Status grades: {'cme': 79}. Time grades: {'cme': 58, 'n/a': 20, 'inferred': 1}. No entry is graded secondary or unverified; one time is inferred (2023-01-16).
- Verbatim check: 0 failures over 110 cited rows (entries, late open, normal days, session sources).
- Bar-check status: {'validated against CME schedules only, bar check pending the step 2 purchase': 52, 'validated against CME schedules only; embargo or holdout-2 date, never checked against bars': 12, 'pending Task 7 (research-window bars)': 15}.

Halt times by period (CT):

| Day type | 2019-2021 | 2022-2023 | 2024-2026-06 |
|---|---|---|---|
| Holiday halt, Monday-Thursday (MLK, Presidents, Memorial, Juneteenth, July 4, Labor, Thanksgiving) | 12:00 | 13:30 | 13:30 |
| Holiday on a Friday (2020-07-03, 2025-07-04, 2026-06-19) | 12:00 close | none | 12:00 close |
| Day after Thanksgiving | 12:45 | 12:45 | 13:45 |
| Christmas Eve (weekday, not the observed holiday) | 12:45 | none in 2022-2023 | 12:45 |
| Good Friday, Christmas, New Year (observed days included) | closed | closed | closed |
| Eve of July 4, New Year's Eve, day before an observed Christmas / New Year, 2025-01-09 | regular | regular | regular |

## Method

CME Group documents only, every cmegroup.com file read from a Wayback Machine capture (cmegroup.com refuses this machine), the CME client wiki on atlassian.net read directly. Sources by period: 2019-2021 CME's yearly `holiday-calendars.zip` (Globex holiday schedules, compact sheets, row 'Energy, Metals & DME'); 2022 and New Year 2023 CME's per-holiday .xls schedules; 2023 CME's holiday summary PDFs (row 'ENERGY'); 2023-09 to 2026-06 CME's `trading-hours-by-product` service (the data behind cmegroup.com/trading-hours.html), product 425 'Crude Oil Futures' (CL). CME's settlement notices and clearing advisories corroborate status and the early-close settlement times.

Verbatim check (run by `/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/ee707266-bbda-4ccb-84dc-81ce0d628d05/scratchpad/energy/gen_report.py (with docs.py, spec.py, gen_module.py)`, outside the repo): Each quote is split on ' ... ' into fragments; every fragment must be a substring of the cited document's text after normalization: Unicode format characters (category Cf) removed and every run of whitespace (including line breaks and NBSP) replaced by one space, the same normalization applied to the fragment. Document text: .xls = LibreOffice CSV export with '|' between cells (all sheets); .pdf = pdftotext -layout; service JSON = response body (gunzipped when stored gzip-encoded); .html = scripts and styles removed, tags replaced by a space, entities unescaped. For a zip the text is that of the named member; the hash is the zip's.

Scope caveat: CME states holiday hours per asset class ('Energy, Metals & DME', 'ENERGY') or for CL. MCL, QM, NG, MNG, QG, RB and HO are taken to share them; the full 2019-2022 schedules list no exception row for any of them (their energy exceptions are DME Oman Crude TAM, Singapore TAM, EUA Daily Futures and TAS/TAM notes).

## Entries

| Date | Name | Kind | Halt CT | Status | Time | Verbatim | Bar check | Status source |
|---|---|---|---|---|---|---|---|---|
| 2019-05-27 | Memorial Day | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2019-holiday-calendars.zip :: 2019-memorial-day-holiday-schedule-compact.xls |
| 2019-07-04 | Independence Day | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2019-holiday-calendars.zip :: 2019-4th-of-july-holiday-schedule-compact.xls |
| 2019-09-02 | Labor Day | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2019-holiday-calendars.zip :: 2019-labor-day-holiday-schedule-compact.xls |
| 2019-11-28 | Thanksgiving Day | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2019-holiday-calendars.zip :: 2019-thanksgiving-holiday-schedule-compact.xls |
| 2019-11-29 | Day after Thanksgiving | early_halt | 12:45 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2019-holiday-calendars.zip :: 2019-thanksgiving-holiday-schedule-compact.xls |
| 2019-12-24 | Christmas Eve | early_halt | 12:45 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2019-holiday-calendars.zip :: 2019-christmas-holiday-schedule-compact.xls |
| 2019-12-25 | Christmas Day | full_closure | - | cme | n/a | True | validated against CME schedules only, bar check pending the step 2 purchase | 2019-holiday-calendars.zip :: 2019-christmas-holiday-schedule-compact.xls |
| 2020-01-01 | New Year's Day | full_closure | - | cme | n/a | True | validated against CME schedules only, bar check pending the step 2 purchase | 2019-holiday-calendars.zip :: 2019-new-years-holiday-schedule-compact.xls |
| 2020-01-20 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2020-holiday-calendars.zip :: 2020-martin-luther-king-holiday-schedule-compact.xls |
| 2020-02-17 | Presidents Day | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2020-holiday-calendars.zip :: 2020-presidents-day-holiday-schedule-compact.xls |
| 2020-04-10 | Good Friday | full_closure | - | cme | n/a | True | validated against CME schedules only, bar check pending the step 2 purchase | 2020-holiday-calendars.zip :: 2020-good-friday-holiday-compact.xls |
| 2020-05-25 | Memorial Day | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2020-holiday-calendars.zip :: 2020-memorial-day-holiday-schedule-compact.xls |
| 2020-07-03 | Independence Day (observed) | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2020-holiday-calendars.zip :: 2020-4th-of-july-holiday-schedule-compact.xls |
| 2020-09-07 | Labor Day | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2020-holiday-calendars.zip :: 2020-labor-day-holiday-schedule-compact.xls |
| 2020-11-26 | Thanksgiving Day | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2020-holiday-calendars.zip :: 2020-thanksgiving-holiday-schedule-compact.xls |
| 2020-11-27 | Day after Thanksgiving | early_halt | 12:45 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2020-holiday-calendars.zip :: 2020-thanksgiving-holiday-schedule-compact.xls |
| 2020-12-24 | Christmas Eve | early_halt | 12:45 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2020-holiday-calendars.zip :: 2020-christmas-holiday-schedule-compact.xls |
| 2020-12-25 | Christmas Day | full_closure | - | cme | n/a | True | validated against CME schedules only, bar check pending the step 2 purchase | 2020-holiday-calendars.zip :: 2020-christmas-holiday-schedule-compact.xls |
| 2021-01-01 | New Year's Day | full_closure | - | cme | n/a | True | validated against CME schedules only, bar check pending the step 2 purchase | 2020-holiday-calendars.zip :: 2021-new-years-holiday-schedule-compact.xls |
| 2021-01-18 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2021-holiday-calendars.zip :: 2021-mlk-day-schedule-compact.xls |
| 2021-02-15 | Presidents Day | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2021-holiday-calendars.zip :: 2021-presidents-day-holiday-schedule-compact.xls |
| 2021-04-02 | Good Friday | full_closure | - | cme | n/a | True | validated against CME schedules only, bar check pending the step 2 purchase | 2021-holiday-calendars.zip :: 2021-good-friday-holiday-schedule-compact.xls |
| 2021-05-31 | Memorial Day | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2021-holiday-calendars.zip :: 2021-memorial-day-holiday-schedule-compact.xls |
| 2021-07-05 | Independence Day (observed) | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2021-holiday-calendars.zip :: 2021-independence-day-holiday-schedule-compact.xls |
| 2021-09-06 | Labor Day | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2021-holiday-calendars.zip :: 2021-labor-day-holiday-schedule-compact.xls |
| 2021-11-25 | Thanksgiving Day | early_halt | 12:00 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2021-holiday-calendars.zip :: 2021-thanksgiving-holiday-schedule-compact.xls |
| 2021-11-26 | Day after Thanksgiving | early_halt | 12:45 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2021-holiday-calendars.zip :: 2021-thanksgiving-holiday-schedule-compact.xls |
| 2021-12-24 | Christmas Day (observed) | full_closure | - | cme | n/a | True | validated against CME schedules only, bar check pending the step 2 purchase | 2021-holiday-calendars.zip :: 2021-christmas-holiday-schedule-compact.xls |
| 2022-01-17 | Martin Luther King Jr. Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2022-mlk-day-holiday-schedule-compact.xls |
| 2022-02-21 | Presidents Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2022-presidents-day-holiday-schedule-compact.xls |
| 2022-04-15 | Good Friday | full_closure | - | cme | n/a | True | validated against CME schedules only, bar check pending the step 2 purchase | 2022-good-friday-holiday-schedule-compact.xls |
| 2022-05-30 | Memorial Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2022-memorial-day-holiday-schedule-compact.xls |
| 2022-06-20 | Juneteenth (observed) | early_halt | 13:30 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2022-juneteenth-holiday-schedule.xls |
| 2022-07-04 | Independence Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2022-independence-day-holiday-schedule-compact.xls |
| 2022-09-05 | Labor Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2022-labor-day-holiday-schedule-compact.xls |
| 2022-11-24 | Thanksgiving Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2022-thanksgiving-holiday-schedule-compact.xls |
| 2022-11-25 | Day after Thanksgiving | early_halt | 12:45 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 2022-thanksgiving-holiday-schedule-compact.xls |
| 2022-12-26 | Christmas Day (observed) | full_closure | - | cme | n/a | True | validated against CME schedules only, bar check pending the step 2 purchase | 2022-christmas-holiday-schedule.xls |
| 2023-01-02 | New Year's Day (observed) | full_closure | - | cme | n/a | True | validated against CME schedules only, bar check pending the step 2 purchase | 2023-new-years-holiday-schedule-compact.xls |
| 2023-01-16 | Martin Luther King Jr. Day | early_halt | 13:30 | cme | inferred | True | validated against CME schedules only, bar check pending the step 2 purchase | mlk-day-holiday-settlement-times-2023.pdf |
| 2023-02-20 | Presidents Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | presidents-day.pdf |
| 2023-04-07 | Good Friday | full_closure | - | cme | n/a | True | validated against CME schedules only, bar check pending the step 2 purchase | good-friday.pdf |
| 2023-05-29 | Memorial Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | memorial-day-2023.pdf |
| 2023-06-19 | Juneteenth | early_halt | 13:30 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | juneteenth-2023.pdf |
| 2023-07-04 | Independence Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | 4th-of-july-2023.pdf |
| 2023-09-04 | Labor Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | labor-day-2023.pdf |
| 2023-11-23 | Thanksgiving Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | thanksgiving-day-2023.pdf |
| 2023-11-24 | Day after Thanksgiving | early_halt | 12:45 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | thanksgiving-day-2023.pdf |
| 2023-12-25 | Christmas Day | full_closure | - | cme | n/a | True | validated against CME schedules only, bar check pending the step 2 purchase | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2024-01-01 | New Year's Day (observed) | full_closure | - | cme | n/a | True | validated against CME schedules only, bar check pending the step 2 purchase | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2024-01-15 | Martin Luther King Jr. Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2024-02-19 | Presidents Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only, bar check pending the step 2 purchase | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2024-03-29 | Good Friday | full_closure | - | cme | n/a | True | validated against CME schedules only; embargo or holdout-2 date, never checked against bars | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2024-05-27 | Memorial Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only; embargo or holdout-2 date, never checked against bars | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2024-06-19 | Juneteenth | early_halt | 13:30 | cme | cme | True | validated against CME schedules only; embargo or holdout-2 date, never checked against bars | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2024-07-04 | Independence Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only; embargo or holdout-2 date, never checked against bars | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2024-09-02 | Labor Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only; embargo or holdout-2 date, never checked against bars | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2024-11-28 | Thanksgiving Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only; embargo or holdout-2 date, never checked against bars | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2024-11-29 | Day after Thanksgiving | early_halt | 13:45 | cme | cme | True | validated against CME schedules only; embargo or holdout-2 date, never checked against bars | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2024-12-24 | Christmas Eve | early_halt | 12:45 | cme | cme | True | validated against CME schedules only; embargo or holdout-2 date, never checked against bars | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2024-12-25 | Christmas Day | full_closure | - | cme | n/a | True | validated against CME schedules only; embargo or holdout-2 date, never checked against bars | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2025-01-01 | New Year's Day | full_closure | - | cme | n/a | True | validated against CME schedules only; embargo or holdout-2 date, never checked against bars | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2025-01-20 | Martin Luther King Jr. Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only; embargo or holdout-2 date, never checked against bars | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2025-02-17 | Presidents Day | early_halt | 13:30 | cme | cme | True | validated against CME schedules only; embargo or holdout-2 date, never checked against bars | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2025-04-18 | Good Friday | full_closure | - | cme | n/a | True | pending Task 7 (research-window bars) | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2025-05-26 | Memorial Day | early_halt | 13:30 | cme | cme | True | pending Task 7 (research-window bars) | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2025-06-19 | Juneteenth | early_halt | 13:30 | cme | cme | True | pending Task 7 (research-window bars) | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2025-07-04 | Independence Day | early_halt | 12:00 | cme | cme | True | pending Task 7 (research-window bars) | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2025-09-01 | Labor Day | early_halt | 13:30 | cme | cme | True | pending Task 7 (research-window bars) | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2025-11-27 | Thanksgiving Day | early_halt | 13:30 | cme | cme | True | pending Task 7 (research-window bars) | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2025-11-28 | Day after Thanksgiving | early_halt | 13:45 | cme | cme | True | pending Task 7 (research-window bars) | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2025-12-24 | Christmas Eve | early_halt | 12:45 | cme | cme | True | pending Task 7 (research-window bars) | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2025-12-25 | Christmas Day | full_closure | - | cme | n/a | True | pending Task 7 (research-window bars) | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2026-01-01 | New Year's Day | full_closure | - | cme | n/a | True | pending Task 7 (research-window bars) | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2026-01-19 | Martin Luther King Jr. Day | early_halt | 13:30 | cme | cme | True | pending Task 7 (research-window bars) | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2026-02-16 | Presidents Day | early_halt | 13:30 | cme | cme | True | pending Task 7 (research-window bars) | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2026-04-03 | Good Friday | full_closure | - | cme | n/a | True | pending Task 7 (research-window bars) | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2026-05-25 | Memorial Day | early_halt | 13:30 | cme | cme | True | pending Task 7 (research-window bars) | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |
| 2026-06-19 | Juneteenth | early_halt | 12:00 | cme | cme | True | pending Task 7 (research-window bars) | trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5 |

## Per-entry records

### 2019-05-27 Memorial Day

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_doc_sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05` (zip member `globex-trading-schedules/2019-memorial-day-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Memorial Day Holiday Schedule: May 24, 2019 - May 28, 2019 ... Calendar Date|Friday,May 24|Sunday,May 26 into Monday,May 27|Monday, May 27|Mon,May 27 into Tues,May 28 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- time_doc_sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05` (zip member `globex-trading-schedules/2019-memorial-day-holiday-schedule-compact.xls`)
- time_quote: "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- notes: Zip member globex-trading-schedules/2019-memorial-day-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2019-07-04 Independence Day

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_doc_sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05` (zip member `globex-trading-schedules/2019-4th-of-july-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019 ... Calendar Date|Wednesday July 3 |Wednesday,July 3|Thursday July 4 |Thursday July 4 into Friday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- time_doc_sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05` (zip member `globex-trading-schedules/2019-4th-of-july-holiday-schedule-compact.xls`)
- time_quote: "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- notes: Zip member globex-trading-schedules/2019-4th-of-july-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2019-09-02 Labor Day

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_doc_sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05` (zip member `globex-trading-schedules/2019-labor-day-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Labor Day Holiday Schedule: August 30, 2019 - September 3, 2019 ... Calendar Date|Friday,August 30|Sunday,Sept 1 into Monday,Sept 2|Monday, Sept 2|Monday, Sept 2 into Tuesday, Sept 3 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- time_doc_sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05` (zip member `globex-trading-schedules/2019-labor-day-holiday-schedule-compact.xls`)
- time_quote: "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- notes: Zip member globex-trading-schedules/2019-labor-day-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2019-11-28 Thanksgiving Day

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_doc_sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05` (zip member `globex-trading-schedules/2019-thanksgiving-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Thanksgiving Holiday Schedule: November 27, 2019 - November 29, 2019 ... Products|Wednesday ,November 27|Wednesday, November 27|Thursday ,November 28|Thursday , November 28|Friday November 29|Friday November 29 ... |CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- time_doc_sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05` (zip member `globex-trading-schedules/2019-thanksgiving-holiday-schedule-compact.xls`)
- time_quote: "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- notes: Zip member globex-trading-schedules/2019-thanksgiving-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2019-11-29 Day after Thanksgiving

- kind early_halt, halt_ct 12:45; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_doc_sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05` (zip member `globex-trading-schedules/2019-thanksgiving-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Thanksgiving Holiday Schedule: November 27, 2019 - November 29, 2019 ... Products|Wednesday ,November 27|Wednesday, November 27|Thursday ,November 28|Thursday , November 28|Friday November 29|Friday November 29 ... |CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- time_doc_sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05` (zip member `globex-trading-schedules/2019-thanksgiving-holiday-schedule-compact.xls`)
- time_quote: "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- notes: Zip member globex-trading-schedules/2019-thanksgiving-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2019-12-24 Christmas Eve

- kind early_halt, halt_ct 12:45; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_doc_sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05` (zip member `globex-trading-schedules/2019-christmas-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Christmas Holiday Schedule: December 24, 2019 - December 26, 2019 ... Trade Date|Tuesday,December 24|Globex Closed|Thursday December 26 ... Products|Tuesday, Dec 24|Wednesday,Dec 25|Wednesday December 25|Thursday,Dec 26|Thursday, Dec 26 ... Energy, Metals & DME |Early @ 1245 CT / 1845 UTC|Closed for Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- time_doc_sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05` (zip member `globex-trading-schedules/2019-christmas-holiday-schedule-compact.xls`)
- time_quote: "Products|Tuesday, Dec 24|Wednesday,Dec 25|Wednesday December 25|Thursday,Dec 26|Thursday, Dec 26 ... Energy, Metals & DME |Early @ 1245 CT / 1845 UTC|Closed for Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
- notes: Zip member globex-trading-schedules/2019-christmas-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2019-12-25 Christmas Day

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_doc_sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05` (zip member `globex-trading-schedules/2019-christmas-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Christmas Holiday Schedule: December 24, 2019 - December 26, 2019 ... Trade Date|Tuesday,December 24|Globex Closed|Thursday December 26 ... Products|Tuesday, Dec 24|Wednesday,Dec 25|Wednesday December 25|Thursday,Dec 26|Thursday, Dec 26 ... Energy, Metals & DME |Early @ 1245 CT / 1845 UTC|Closed for Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
- notes: Zip member globex-trading-schedules/2019-christmas-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2020-01-01 New Year's Day

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
- status_doc_sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05` (zip member `globex-trading-schedules/2019-new-years-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex New Years Holiday Schedule: December 31, 2019 - January 2, 2020 ... Trade Date|Tuesday,Dec 31|Globex Closed|Thursday, January 2 ... Calendar Trade|Tuesday, Dec 31|Wednessday, Jan 1 |Wednesday, Jan 1|Thursday, Jan 2|Thursday, Jan 2 ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Closed for New Year's|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
- notes: Zip member globex-trading-schedules/2019-new-years-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). The member file is named 2019-new-years but its title covers 2019-12-31 to 2020-01-02.

### 2020-01-20 Martin Luther King Jr. Day

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-martin-luther-king-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Martin Luther King Day Holiday Schedule: January 17, 2020 - January 21, 2020 ... Calendar Date|Friday, Jan 17|Sunday, Jan 19 into Monday, Jan 20|Monday, Jan 20|Monday, Jan 20 into Tuesday, Jan 21 ... Products|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-martin-luther-king-holiday-schedule-compact.xls`)
- time_quote: "Products|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
- notes: Zip member 2020-martin-luther-king-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2020-02-17 Presidents Day

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-presidents-day-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Presidents Day Holiday Schedule: February 14, 2020 - February 18, 2020 ... Calendar Date|Friday, Feb 14|Sunday, Feb 16 into Monday, Feb 17|Monday,Feb 17|Monday, Feb 17 into Tuesday, Feb 18 ... Products|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-presidents-day-holiday-schedule-compact.xls`)
- time_quote: "Products|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
- notes: Zip member 2020-presidents-day-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2020-04-10 Good Friday

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-good-friday-holiday-compact.xls`)
- status_quote: "CME Group Globex Good Friday Holiday Schedule: April 9,2020 to April 13, 2020 ... Calendar Date|Thursday April 9|Friday April 10|Sunday, April 12 into Monday, April 13 ... Product|CLOSE|CLOSED|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Closed for Good Friday|Regular @ 1700 CT / 2200 UTC"
- notes: Zip member 2020-good-friday-holiday-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2020-05-25 Memorial Day

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-memorial-day-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Memorial Day Holiday Schedule: May 22, 2020 - May 26, 2020 ... Calendar Date|Friday,May 22|Sunday,May 24 into Monday,May 25|Monday, May 25|Mon,May 25 into Tues,May 26 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-memorial-day-holiday-schedule-compact.xls`)
- time_quote: "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- notes: Zip member 2020-memorial-day-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2020-07-03 Independence Day (observed)

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-4th-of-july-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Independence Day Holiday Schedule: July 2, 2020 to July 6, 2020 ... Calendar Date|Thursday July 2|Thursday , July 2|Friday July 3|Sunday July 5 into Monday July 6 ... Product|CLOSE|OPEN|ClOSE|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-4th-of-july-holiday-schedule-compact.xls`)
- time_quote: "Product|CLOSE|OPEN|ClOSE|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- notes: Zip member 2020-4th-of-july-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). Friday holiday: CME labels the 12:00 CT event a close (header 'ClOSE'), and the next open is Sunday July 5 at 17:00 CT.

### 2020-09-07 Labor Day

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-labor-day-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Labor Day Holiday Schedule: September 4, 2020 - September 8, 2020 ... Calendar Date|Friday,September 4|Sunday,Sept 6 into Monday,Sept 7|Monday, Sept 7|Monday, Sept 7 into Tuesday, Sept 8 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-labor-day-holiday-schedule-compact.xls`)
- time_quote: "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- notes: Zip member 2020-labor-day-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2020-11-26 Thanksgiving Day

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-thanksgiving-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Thanksgiving Holiday Schedule: November 25, 2020 - November 27, 2020 ... Products|Wednesday ,November 25|Wednesday, November 25|Thursday ,November 26|Thursday , November 26|Friday November 27|Friday November 27 ... |CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-thanksgiving-holiday-schedule-compact.xls`)
- time_quote: "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- notes: Zip member 2020-thanksgiving-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2020-11-27 Day after Thanksgiving

- kind early_halt, halt_ct 12:45; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-thanksgiving-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Thanksgiving Holiday Schedule: November 25, 2020 - November 27, 2020 ... Products|Wednesday ,November 25|Wednesday, November 25|Thursday ,November 26|Thursday , November 26|Friday November 27|Friday November 27 ... |CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-thanksgiving-holiday-schedule-compact.xls`)
- time_quote: "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- notes: Zip member 2020-thanksgiving-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2020-12-24 Christmas Eve

- kind early_halt, halt_ct 12:45; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-christmas-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Christmas Holiday Schedule: December 24, 2020 - December 28, 2020 ... Trade Date|Thursday,December 24|Globex Closed|Monday December 28 ... Products|Thursday, Dec 24|Friday,Dec 25|Sunday 27|Monday,Dec 28|Monday, Dec 28 ... Energy, Metals & DME |Early @ 1245 CT / 1845 UTC|Closed for Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- time_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-christmas-holiday-schedule-compact.xls`)
- time_quote: "Products|Thursday, Dec 24|Friday,Dec 25|Sunday 27|Monday,Dec 28|Monday, Dec 28 ... Energy, Metals & DME |Early @ 1245 CT / 1845 UTC|Closed for Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
- notes: Zip member 2020-christmas-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2020-12-25 Christmas Day

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2020-christmas-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Christmas Holiday Schedule: December 24, 2020 - December 28, 2020 ... Trade Date|Thursday,December 24|Globex Closed|Monday December 28 ... Products|Thursday, Dec 24|Friday,Dec 25|Sunday 27|Monday,Dec 28|Monday, Dec 28 ... Energy, Metals & DME |Early @ 1245 CT / 1845 UTC|Closed for Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
- notes: Zip member 2020-christmas-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2021-01-01 New Year's Day

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
- status_doc_sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59` (zip member `2021-new-years-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex New Years Holiday Schedule: December 31, 2020 - January 4, 2021 ... Trade Date|Thursday,Dec 31|Globex Closed|Monday, January 4 ... Calendar Trade|Thursday,Dec 31|Friday,Jan 1|Sunday,Jan 3|Monday, Jan 4|Monday, Jan 4 ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Closed for New Year's|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
- notes: Zip member 2021-new-years-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). CME filed the 2021 New Year schedule in its 2020 zip.

### 2021-01-18 Martin Luther King Jr. Day

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-mlk-day-schedule-compact.xls`)
- status_quote: "CME Group Globex Martin Luther King Day Holiday Schedule: January 15, 2021 - January 19, 2021 ... Calendar Date|Friday, Jan 15|Sunday, Jan 17 into Monday, Jan 18|Monday, Jan 18|Monday, Jan 18 into Tuesday, Jan 19 ... Products|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- time_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-mlk-day-schedule-compact.xls`)
- time_quote: "Products|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
- notes: Zip member 2021-mlk-day-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2021-02-15 Presidents Day

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-presidents-day-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Presidents Day Holiday Schedule: February 12, 2021 - February 16, 2021 ... Calendar Date|Friday, Feb 12|Sunday, Feb 14 into Monday, Feb 15|Monday,Feb 15|Monday, Feb 15 into Tuesday, Feb 16 ... Products|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- time_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-presidents-day-holiday-schedule-compact.xls`)
- time_quote: "Products|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
- notes: Zip member 2021-presidents-day-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2021-04-02 Good Friday

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-good-friday-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Good Friday Holiday Schedule: April 1,2021 to April 5, 2021 ... Calendar Date|Thursday April 1|Thursday,April 1|Friday April 2|Sunday, April 4 into Monday, April 5 ... Product|CLOSE|OPEN|CLOSED|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Closed for Good Friday|Closed for Good Friday|Regular @ 1700 CT / 2200 UTC"
- notes: Zip member 2021-good-friday-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). Jobs-report Good Friday: equities and rates traded an abbreviated session (equity calendar), energy did not open.

### 2021-05-31 Memorial Day

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-memorial-day-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Memorial Day Holiday Schedule: May 28, 2021 - June 1st, 2021 ... Calendar Date|Friday,May 28|Sunday,May 30|Monday, May 31|Monday, May 31 into Tues, June 1 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- time_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-memorial-day-holiday-schedule-compact.xls`)
- time_quote: "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- notes: Zip member 2021-memorial-day-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2021-07-05 Independence Day (observed)

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-independence-day-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Independence Day Holiday Schedule: July 2, 2021 to July 6, 2021 ... Calendar Date|Friday July 2|Sunday July 4|Monday July 5|Monday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- time_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-independence-day-holiday-schedule-compact.xls`)
- time_quote: "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- notes: Zip member 2021-independence-day-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2021-09-06 Labor Day

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-labor-day-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Labor Day Holiday Schedule: September 3, 2021 - September 7, 2021 ... Calendar Date|Friday,September 3|Sunday,Sept 5 into Monday,Sept 6|Monday, Sept 6|Monday, Sept 6 into Tuesday, Sept 7 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- time_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-labor-day-holiday-schedule-compact.xls`)
- time_quote: "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
- notes: Zip member 2021-labor-day-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2021-11-25 Thanksgiving Day

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-thanksgiving-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Thanksgiving Holiday Schedule: November 24, 2021 - November 26, 2021 ... Products|Wednesday ,November 24|Wednesday, November 24|Thursday ,November 25|Thursday , November 25|Friday November 26|Friday November 26 ... |CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- time_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-thanksgiving-holiday-schedule-compact.xls`)
- time_quote: "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- notes: Zip member 2021-thanksgiving-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2021-11-26 Day after Thanksgiving

- kind early_halt, halt_ct 12:45; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-thanksgiving-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Thanksgiving Holiday Schedule: November 24, 2021 - November 26, 2021 ... Products|Wednesday ,November 24|Wednesday, November 24|Thursday ,November 25|Thursday , November 25|Friday November 26|Friday November 26 ... |CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- time_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- time_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-thanksgiving-holiday-schedule-compact.xls`)
- time_quote: "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- notes: Zip member 2021-thanksgiving-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2021-12-24 Christmas Day (observed)

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_fetched_via: https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
- status_doc_sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59` (zip member `2021-christmas-holiday-schedule-compact.xls`)
- status_quote: "CME Group Globex Christmas Holiday Schedule: December 23, 2021 - December 27, 2021 ... Trade Date|Thursday,December 23|Globex Closed|Monday December 27 ... Products|Thursday, Dec 23|Friday,Dec 24|Sunday 26|Monday,Dec 27 ... Energy, Metals & DME |Regular per Product|Closed for Christmas|Regular @ 1700 CT / 2300 UTC|Regular @ 1600 CT / 2200 UTC"
- notes: Zip member 2021-christmas-holiday-schedule-compact.xls; the zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2022-01-17 Martin Luther King Jr. Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule-compact.xls
- status_fetched_via: https://web.archive.org/web/20220704065433id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule-compact.xls
- status_doc_sha256: `efeb807e9cec93a018ebeaa1e8a59e902a316a7ddc7a1e9d85850345c9b125ad`
- status_quote: "CME Group Globex Martin Luther King Day Holiday Schedule: January 14, 2022 - January 18, 2022 ... Calendar Date|Friday, Jan 14|Sunday, Jan 16 into Monday, Jan 17|Monday, Jan 17|Monday, Jan 17 into Tuesday, Jan 18 ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule-compact.xls
- time_fetched_via: https://web.archive.org/web/20220704065433id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule-compact.xls
- time_doc_sha256: `efeb807e9cec93a018ebeaa1e8a59e902a316a7ddc7a1e9d85850345c9b125ad`
- time_quote: "Calendar Date|Friday, Jan 14|Sunday, Jan 16 into Monday, Jan 17|Monday, Jan 17|Monday, Jan 17 into Tuesday, Jan 18 ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC"
- notes: CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). First 13:30 CT energy holiday halt found (2019-2021: 12:00 CT).

### 2022-02-21 Presidents Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule-compact.xls
- status_fetched_via: https://web.archive.org/web/20220217175219id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule-compact.xls
- status_doc_sha256: `418f38b72b2bad9011d31dc189637ba1f5cd6617745f21b9f5bcfcd0eeea962d`
- status_quote: "CME Group Globex Presidents Day Holiday Schedule: February 18, 2022 - February 22, 2022 ... Calendar Date|Friday, Feb 18|Sunday, Feb 20 into Monday, Feb 21|Monday,Feb 21|Monday, Feb 21 into Tuesday, Feb 22 ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule-compact.xls
- time_fetched_via: https://web.archive.org/web/20220217175219id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule-compact.xls
- time_doc_sha256: `418f38b72b2bad9011d31dc189637ba1f5cd6617745f21b9f5bcfcd0eeea962d`
- time_quote: "Calendar Date|Friday, Feb 18|Sunday, Feb 20 into Monday, Feb 21|Monday,Feb 21|Monday, Feb 21 into Tuesday, Feb 22 ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC"
- notes: CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2022-04-15 Good Friday

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule-compact.xls
- status_fetched_via: https://web.archive.org/web/20220412171426id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule-compact.xls
- status_doc_sha256: `cb83640e4daa9c27d4d79a7d27bbc97ceb15a6b2e41cdace7b5e368d268e43dd`
- status_quote: "CME Group Globex Good Friday Holiday Schedule: April 14,2022 to April 18, 2022 ... Calendar Date|Thursday April 14|Friday April 15|Sunday, April 17 into Monday, April 18 ... Product|CLOSE|CLOSED|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Closed for Good Friday|Regular @ 1700 CT / 2200 UTC"
- notes: CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2022-05-30 Memorial Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule-compact.xls
- status_fetched_via: https://web.archive.org/web/20220704094237id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule-compact.xls
- status_doc_sha256: `fe52d4b95edc9e9cee9037486a63c70c6d403f03bdbbbe3f29cbd57ffcfb06bb`
- status_quote: "CME Group Globex Memorial Day Holiday Schedule: May 27, 2022 - May 31 , 2022 ... Calendar Date|Friday,May 27|Sunday,May 29|Monday, May 30|Monday, May 30 into Tues, May31 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1330 CT / 1830 UTC|Regular @ 1700 CT / 2200 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule-compact.xls
- time_fetched_via: https://web.archive.org/web/20220704094237id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule-compact.xls
- time_doc_sha256: `fe52d4b95edc9e9cee9037486a63c70c6d403f03bdbbbe3f29cbd57ffcfb06bb`
- time_quote: "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1330 CT / 1830 UTC|Regular @ 1700 CT / 2200 UTC"
- notes: CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2022-06-20 Juneteenth (observed)

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls
- status_fetched_via: https://web.archive.org/web/20220620200210id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls
- status_doc_sha256: `bc9f2caf26a73a13029f177fcc6468bdc8662899ff935f44329ee1a95c8b667b`
- status_quote: "CME Group Globex Juneteenth Holiday Schedule: June 17, 2022 - Jun 21, 2022 ... Calendar Date|Friday, June 17|||||Sunday, June 19|||||Monday, June 20||||||||||Tuesday, Jun 21 ... Energy, Metals & DME Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||01:30:00 PM||||01:30:00 PM|05:00:00 PM"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls
- time_fetched_via: https://web.archive.org/web/20220620200210id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls
- time_doc_sha256: `bc9f2caf26a73a13029f177fcc6468bdc8662899ff935f44329ee1a95c8b667b`
- time_quote: "Energy, Metals & DME Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||01:30:00 PM||||01:30:00 PM|05:00:00 PM"
- notes: CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). Full schedule (no compact file captured). Column mapping read from the merged header cells with xlrd: Calendar Date 'Monday, June 20' spans columns 11-20; the energy row's 13:30 cells are columns 14 ('Halt') and 18, and 17:00 is column 19 ('Open').

### 2022-07-04 Independence Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls
- status_fetched_via: https://web.archive.org/web/20220704065431id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls
- status_doc_sha256: `11925e2a7c434e05e2e3b74df1e677cd0657629370e735a11f821871e0e91e06`
- status_quote: "CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022 ... Calendar Date|Friday July 1|Sunday July 3|Monday July 4|Monday July 4 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1330 CT / 1830 UTC|Regular @ 1700 CT / 2200 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls
- time_fetched_via: https://web.archive.org/web/20220704065431id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls
- time_doc_sha256: `11925e2a7c434e05e2e3b74df1e677cd0657629370e735a11f821871e0e91e06`
- time_quote: "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1330 CT / 1830 UTC|Regular @ 1700 CT / 2200 UTC"
- notes: CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2022-09-05 Labor Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule-compact.xls
- status_fetched_via: https://web.archive.org/web/20220704072842id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule-compact.xls
- status_doc_sha256: `c0fc7d1a13d8b7b220dbd7fbc933e282961eaec46e899ae50c0be297a0bbf51e`
- status_quote: "CME Group Globex Labor Day Holiday Schedule: September 2, 2022 - September 6, 2022 ... Calendar Date|Friday, September 2|Sunday,Sept 4 into Monday, Sept 5|Monday, Sept 5|Monday, Sept 5 into Tuesday, Sept 6 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1330 CT / 1830 UTC|Regular @ 1700 CT / 2200 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule-compact.xls
- time_fetched_via: https://web.archive.org/web/20220704072842id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule-compact.xls
- time_doc_sha256: `c0fc7d1a13d8b7b220dbd7fbc933e282961eaec46e899ae50c0be297a0bbf51e`
- time_quote: "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1330 CT / 1830 UTC|Regular @ 1700 CT / 2200 UTC"
- notes: CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2022-11-24 Thanksgiving Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule-compact.xls
- status_fetched_via: https://web.archive.org/web/20220704073046id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule-compact.xls
- status_doc_sha256: `f6de3c7cd0bcff067fd5b548daa211e2ee7075b9781daa06bbc3532c5aee2600`
- status_quote: "CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, 2022 ... Products|Wednesday ,November 23|Wednesday, November 23|Thursday ,November 24|Thursday , November 24|Friday November 25|Friday November 25 ... |CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule-compact.xls
- time_fetched_via: https://web.archive.org/web/20220704073046id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule-compact.xls
- time_doc_sha256: `f6de3c7cd0bcff067fd5b548daa211e2ee7075b9781daa06bbc3532c5aee2600`
- time_quote: "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- notes: CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2022-11-25 Day after Thanksgiving

- kind early_halt, halt_ct 12:45; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule-compact.xls
- status_fetched_via: https://web.archive.org/web/20220704073046id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule-compact.xls
- status_doc_sha256: `f6de3c7cd0bcff067fd5b548daa211e2ee7075b9781daa06bbc3532c5aee2600`
- status_quote: "CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, 2022 ... Products|Wednesday ,November 23|Wednesday, November 23|Thursday ,November 24|Thursday , November 24|Friday November 25|Friday November 25 ... |CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule-compact.xls
- time_fetched_via: https://web.archive.org/web/20220704073046id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule-compact.xls
- time_doc_sha256: `f6de3c7cd0bcff067fd5b548daa211e2ee7075b9781daa06bbc3532c5aee2600`
- time_quote: "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 CT/ 1845 UTC"
- notes: CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET').

### 2022-12-26 Christmas Day (observed)

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls
- status_fetched_via: https://web.archive.org/web/20220704065430id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls
- status_doc_sha256: `2dd1d531514989845dcb6ce6d767db5dd3f956ac6777ab1cfe36d6843f3762e7`
- status_quote: "CME Group Globex Christmas Holiday Schedule: December 23, 2022 - December 27, 2022 ... Calendar Date|Friday, December 23||||||||Monday, December 26||||||||||||||||Tuesday, December 27 ... Energy, Metals & DME products (see notes below)|04:00:00 PM||||||||Globex Closed||||||||||04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
- notes: CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). Full schedule, 'Updated 6/29/2022' (captured 2022-07-04, before the holiday). Merged header cells (xlrd): 'Globex Closed' spans columns 9-18 under Calendar Date 'Monday, December 26' (columns 9-24); pre-open 16:00 and open 17:00 follow on the Monday. CME's 2022 Christmas settlement notice agrees: 'Note: Monday December 26, 2022 CME Group will not derive or disseminate settlement prices'.

### 2023-01-02 New Year's Day (observed)

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule-compact.xls
- status_fetched_via: https://web.archive.org/web/20220704065450id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule-compact.xls
- status_doc_sha256: `9c7937fbe705b906edcc5e31d0a7d44edb19d99e2341406c419a0e03eca8c5f4`
- status_quote: "CME Group Globex New Years Holiday Schedule: December 30, 2022 - January 3, 2023 ... Calendar Trade|Friday,Dec 30|Sunday, Jan 1 and Monday, Jan 2|Monday,Jan 2|Tuesday, Jan 3|Tuesday, Jan 3 ... |CLOSE|Closed|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Globex Closed|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
- notes: CME's compact Globex holiday schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). Captured 2022-07-04, before the holiday (CME published it in advance).

### 2023-01-16 Martin Luther King Jr. Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence inferred; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2023.pdf
- status_fetched_via: https://web.archive.org/web/20230203073653id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2023.pdf
- status_doc_sha256: `051f2a2136e27daecf8ed717983787fc8aacd62b83418cbecca1a44937e9e4cb`
- status_quote: "Note: Monday January 16, 2023 CME Group will not derive or disseminate settlement prices (other than the two LIBOR Settlements listed above) for CME, CBOT, NYMEX or COMEX"
- time_url: https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-mlk-day-holiday-schedule-compact-mgex-dme.xls
- time_fetched_via: https://web.archive.org/web/20230313181421id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-mlk-day-holiday-schedule-compact-mgex-dme.xls
- time_doc_sha256: `895304a765a7000c53d81ae991b8e2b5855bb1730a6c2ee3ff1ace38a793d259`
- time_quote: "CME Group Globex Martin Luther King Day Holiday Schedule: January 13, 2023 - January 17, 2023 ... Calendar Date|Friday, Jan 13|Sunday, Jan 15 into Monday, Jan 16|Monday, Jan 16|Monday, Jan 16 into Tuesday, Jan 17 ... Products|CLOSE|OPEN|HALT|OPEN ... DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC"
- notes: Time inferred, not cme: no CME Globex schedule with a NYMEX energy row was retrievable for MLK Day 2023 (the 2023 summary PDF was not archived; the service capture of 2024-07-08 has no events for that window). The CME Globex MLK 2023 schedule retrieved covers MGEX and DME only; its DME row (Dubai Mercantile Exchange crude on CME Globex, grouped with NYMEX energy as 'Energy, Metals & DME' in CME's 2019-2022 schedules) halts at 13:30 CT. Consistent with every NYMEX energy holiday halt from 2022-01-17 to 2026-05-25 (13:30 CT). Secondary corroboration, not machine-checkable: AMP Futures' image of CME's table 'CME Group Globex Dr. Martin Luther King, Jr. Holiday Schedule: 13 - 17 January 2023' shows 'Energies' HALT '13:30 CST' on Monday Jan 16 (https://www.ampfutures.com/hubfs/CME%20Holiday%20Trading%20Schedule%20-%20Dr.%20Martin%20Luther%20King%2c%20Jr.%20(2023).png, cached by CalendarBuilder-Rates, read as an image).

### 2023-02-20 Presidents Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/files/presidents-day.pdf
- status_fetched_via: https://web.archive.org/web/20230329115747id_/https://www.cmegroup.com/files/presidents-day.pdf
- status_doc_sha256: `63c9f17b5dd285a522cccb6d75ac014f299d6a25defab6fd182e6ec7300d4a80`
- status_quote: "PRODUCT NAME Cleared As SUNDAY, 19 FEB 2023 MONDAY, 20 FEB 2023 TUESDAY, 21 FEB 2023 ... ENERGY 16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
- time_url: https://www.cmegroup.com/files/presidents-day.pdf
- time_fetched_via: https://web.archive.org/web/20230329115747id_/https://www.cmegroup.com/files/presidents-day.pdf
- time_doc_sha256: `63c9f17b5dd285a522cccb6d75ac014f299d6a25defab6fd182e6ec7300d4a80`
- time_quote: "ENERGY 16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
- notes: CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most actively traded instruments for each asset class', ENERGY row; text read with pdftotext -layout, so the ENERGY line carries the day columns left to right. cmegroup.com/files/presidents-day.pdf is the fixed name CME's trading-hours page linked as 'Download a summary view of the President's Day Holiday Hours' (page capture 2023-02-19); this capture (2023-03-29) holds the 2023 version.

### 2023-04-07 Good Friday

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/files/good-friday.pdf
- status_fetched_via: https://web.archive.org/web/20240708160009id_/https://www.cmegroup.com/files/good-friday.pdf
- status_doc_sha256: `7c598e4e4853335eec65283677349985aaac9fff8d95cb248510bc6fac981189`
- status_quote: "PRODUCT NAME THURSDAY, 6 APR 2023 FRIDAY, 7 APR 2023 ... ENERGY 16:00 ( CLOSED)"
- notes: CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most actively traded instruments for each asset class', ENERGY row; text read with pdftotext -layout, so the ENERGY line carries the day columns left to right. The 2024-07-08 capture of the fixed name cmegroup.com/files/good-friday.pdf still holds the 2023 version (6-7 APR 2023). The ENERGY row has only Thursday's 16:00 close and no Friday event, while INTEREST RATE, EQUITIES, FX and CRYPTOCURRENCIES carry Friday sessions. CME's 2023 Good Friday clearing advisory names only equities as open for an abbreviated session and FX and interest-rate markets as settled.

### 2023-05-29 Memorial Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf
- status_fetched_via: https://web.archive.org/web/20230420224018id_/https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf
- status_doc_sha256: `7657bc8089ca669cfd244c2e3e697b47a7e650f5d957efe5b32da001622acb35`
- status_quote: "PRODUCT NAME SUNDAY, 28 MAY 2023 MONDAY, 29 MAY 2023 TUESDAY, 30 MAY 2023 ... ENERGY 16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
- time_url: https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf
- time_fetched_via: https://web.archive.org/web/20230420224018id_/https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf
- time_doc_sha256: `7657bc8089ca669cfd244c2e3e697b47a7e650f5d957efe5b32da001622acb35`
- time_quote: "ENERGY 16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
- notes: CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most actively traded instruments for each asset class', ENERGY row; text read with pdftotext -layout, so the ENERGY line carries the day columns left to right.

### 2023-06-19 Juneteenth

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf
- status_fetched_via: https://web.archive.org/web/20230613185949id_/https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf
- status_doc_sha256: `831f7f63e197ce58436780830aa515cb08dcf92bdf82a540265c2d21a4bffa43`
- status_quote: "PRODUCT NAME SUNDAY, 18 JUNE 2023 MONDAY, 19 JUNE 2023 TUESDAY, 20 JUNE 2023 ... ENERGY 16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
- time_url: https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf
- time_fetched_via: https://web.archive.org/web/20230613185949id_/https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf
- time_doc_sha256: `831f7f63e197ce58436780830aa515cb08dcf92bdf82a540265c2d21a4bffa43`
- time_quote: "ENERGY 16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
- notes: CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most actively traded instruments for each asset class', ENERGY row; text read with pdftotext -layout, so the ENERGY line carries the day columns left to right.

### 2023-07-04 Independence Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf
- status_fetched_via: https://web.archive.org/web/20230627125057id_/https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf
- status_doc_sha256: `ccbc1f1fc39ba2219fd748372faa985798fee7eaffabf69f08956f5465a769e3`
- status_quote: "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... ENERGY TRADE DATE: WED 5 JULY 13:30 (PREOPEN) HALT"
- time_url: https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf
- time_fetched_via: https://web.archive.org/web/20230627125057id_/https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf
- time_doc_sha256: `ccbc1f1fc39ba2219fd748372faa985798fee7eaffabf69f08956f5465a769e3`
- time_quote: "ENERGY TRADE DATE: WED 5 JULY 13:30 (PREOPEN) HALT"
- notes: CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most actively traded instruments for each asset class', ENERGY row; text read with pdftotext -layout, so the ENERGY line carries the day columns left to right.

### 2023-09-04 Labor Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/trading-hours/files/labor-day-2023.pdf
- status_fetched_via: https://web.archive.org/web/20230802192446id_/https://www.cmegroup.com/trading-hours/files/labor-day-2023.pdf
- status_doc_sha256: `39a4c075437fdc7134166328eca730e3cabf3bea00ab369466dff63c99f8e948`
- status_quote: "PRODUCT NAME SUNDAY, 3 SEPTEMBER 2023 MONDAY, 4 SEPTEMBER 2023 TUESDAY, 5 SEPTEMBER 2023 ... ENERGY 16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-09-03&toEventDate=2023-09-05&isProtected&_t=1720455278654
- time_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-09-03&toEventDate=2023-09-05&isProtected&_t=1720455278654
- time_doc_sha256: `214f0f8f9dab7c04ff8b0277a6c70137b0399d0bb677bb8953dc87581e9ddb57`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2023-09-04","events":[{"tradingDate":"2023-09-05","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2023-09-05","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most actively traded instruments for each asset class', ENERGY row; text read with pdftotext -layout, so the ENERGY line carries the day columns left to right. CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2023-11-23 Thanksgiving Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf
- status_fetched_via: https://web.archive.org/web/20231203205929id_/https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf
- status_doc_sha256: `99e187b3f3899e1062d662e148d5978e0cd075b961e6fc79550d4393812307e8`
- status_quote: "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 NOVEMBER 2023 ... ENERGY TRADE DATE: FRI 24 NOV 13:30 (PREOPEN) HALT 12:45 (CLOSED)"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-11-22&toEventDate=2023-11-24&isProtected&_t=1720455278656
- time_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-11-22&toEventDate=2023-11-24&isProtected&_t=1720455278656
- time_doc_sha256: `d1e371e76342de901d4b0ee26a2eb8d64c8df8fb2c488c961ed7d9f23282fa8f`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2023-11-23","events":[{"tradingDate":"2023-11-24","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2023-11-24","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most actively traded instruments for each asset class', ENERGY row; text read with pdftotext -layout, so the ENERGY line carries the day columns left to right. CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2023-11-24 Day after Thanksgiving

- kind early_halt, halt_ct 12:45; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf
- status_fetched_via: https://web.archive.org/web/20231203205929id_/https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf
- status_doc_sha256: `99e187b3f3899e1062d662e148d5978e0cd075b961e6fc79550d4393812307e8`
- status_quote: "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 NOVEMBER 2023 ... ENERGY TRADE DATE: FRI 24 NOV 13:30 (PREOPEN) HALT 12:45 (CLOSED)"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-11-22&toEventDate=2023-11-24&isProtected&_t=1720455278656
- time_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-11-22&toEventDate=2023-11-24&isProtected&_t=1720455278656
- time_doc_sha256: `d1e371e76342de901d4b0ee26a2eb8d64c8df8fb2c488c961ed7d9f23282fa8f`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2023-11-24","events":[{"tradingDate":"2023-11-24","eventTime":"12:45","marketEventType":"closed"}]}"
- notes: CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most actively traded instruments for each asset class', ENERGY row; text read with pdftotext -layout, so the ENERGY line carries the day columns left to right. CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. CME's 2023 Thanksgiving settlement notice: 'Energy Products 13:30:00 ET' (12:30 CT) on Friday November 24.

### 2023-12-25 Christmas Day

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-24&toEventDate=2023-12-26&isProtected&_t=1720455278659
- status_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-24&toEventDate=2023-12-26&isProtected&_t=1720455278659
- status_doc_sha256: `c7d59dc8371c5d03d2ddfe42ed8f9f65faf9729bd23b1a83a23bd8a6f175e2e2`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2023-12-24","events":[]} ... {"groupCode":"CL","eventDate":"2023-12-25","events":[{"tradingDate":"2023-12-26","eventTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2023-12-26","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. No event on Sunday 12-24 (no 17:00 CT reopen) and only the 16:00 pre-open and 17:00 open for trade date 12-26 on Monday 12-25. CME's summary PDF christmas-day-2023.pdf (ENERGY row, Monday 25 December: 16:00 PREOPEN, 17:00 OPEN) and its settlement notice ('Note: Monday December 25, 2023 CME Group will not derive or disseminate settlement prices') agree.

### 2024-01-01 New Year's Day (observed)

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-31&toEventDate=2024-01-02&isProtected&_t=1720455278661
- status_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-31&toEventDate=2024-01-02&isProtected&_t=1720455278661
- status_doc_sha256: `fdf3a5d8938743d59e7ab55cd4f482c5d0a6433fde353a943c3a2aeacbc7eea2`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2023-12-31","events":[]} ... {"groupCode":"CL","eventDate":"2024-01-01","events":[{"tradingDate":"2024-01-02","eventTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-01-02","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. CME's summary PDF new-years-day-2024.pdf (ENERGY, Monday 1 January 2024: 16:00 PREOPEN, 17:00 OPEN) agrees.

### 2024-01-15 Martin Luther King Jr. Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663
- status_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663
- status_doc_sha256: `e7c5cee8b81efb4ec34a66e9295bb977cc6cd876007689b55a18be0485134fff`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-01-15","events":[{"tradingDate":"2024-01-16","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-01-16","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663
- time_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663
- time_doc_sha256: `e7c5cee8b81efb4ec34a66e9295bb977cc6cd876007689b55a18be0485134fff`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-01-15","events":[{"tradingDate":"2024-01-16","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-01-16","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2024-02-19 Presidents Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669
- status_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669
- status_doc_sha256: `07613c57b79dac5dc38a06c88cdaf01eb8182d3b88af8b9c7aa386a0e32b81d9`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-02-19","events":[{"tradingDate":"2024-02-20","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-02-20","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669
- time_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669
- time_doc_sha256: `07613c57b79dac5dc38a06c88cdaf01eb8182d3b88af8b9c7aa386a0e32b81d9`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-02-19","events":[{"tradingDate":"2024-02-20","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-02-20","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2024-03-29 Good Friday

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-03-28&toEventDate=2024-03-30&isProtected&_t=1720455278672
- status_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-03-28&toEventDate=2024-03-30&isProtected&_t=1720455278672
- status_doc_sha256: `451df5abdd31106dcb258fe973e7353928dc44d8009f18b9bc9ed9795241cba7`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-03-28","events":[{"tradingDate":"2024-03-28","eventTime":"16:00","marketEventType":"closed"}]} ... {"groupCode":"CL","eventDate":"2024-03-29","events":[]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2024-05-27 Memorial Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675
- status_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675
- status_doc_sha256: `842d4a8bd9fced2fe5ff15912d732016bb47b7a2113ede518d5d721ff428cb2d`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-05-27","events":[{"tradingDate":"2024-05-28","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-05-28","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675
- time_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675
- time_doc_sha256: `842d4a8bd9fced2fe5ff15912d732016bb47b7a2113ede518d5d721ff428cb2d`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-05-27","events":[{"tradingDate":"2024-05-28","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-05-28","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2024-06-19 Juneteenth

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677
- status_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677
- status_doc_sha256: `a48d61ca544ca2620f2cdc4a3d2232b2c9ff236282879cd4f7d86d66b1adef17`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-06-19","events":[{"tradingDate":"2024-06-20","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-06-20","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677
- time_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677
- time_doc_sha256: `a48d61ca544ca2620f2cdc4a3d2232b2c9ff236282879cd4f7d86d66b1adef17`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-06-19","events":[{"tradingDate":"2024-06-20","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-06-20","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2024-07-04 Independence Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680
- status_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680
- status_doc_sha256: `54de3d48c849891d7f37ec1afa38d3e10103c7d606b141a91ad8dec9349e529a`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680
- time_fetched_via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680
- time_doc_sha256: `54de3d48c849891d7f37ec1afa38d3e10103c7d606b141a91ad8dec9349e529a`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2024-09-02 Labor Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1734710019534
- status_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1734710019534
- status_doc_sha256: `bbe6c78555cba0437fe4b9c6eac0063983ecae49056877db618ed2b29c109546`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-09-02","events":[{"tradingDate":"2024-09-03","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-09-03","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1734710019534
- time_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1734710019534
- time_doc_sha256: `bbe6c78555cba0437fe4b9c6eac0063983ecae49056877db618ed2b29c109546`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-09-02","events":[{"tradingDate":"2024-09-03","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-09-03","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2024-11-28 Thanksgiving Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535
- status_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535
- status_doc_sha256: `e59cbaab0a0a4e62b57226147edd4a5bd8bfee86911eb3a2b4e98b1b0bb12517`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-11-28","events":[{"tradingDate":"2024-11-29","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-11-29","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535
- time_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535
- time_doc_sha256: `e59cbaab0a0a4e62b57226147edd4a5bd8bfee86911eb3a2b4e98b1b0bb12517`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-11-28","events":[{"tradingDate":"2024-11-29","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-11-29","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2024-11-29 Day after Thanksgiving

- kind early_halt, halt_ct 13:45; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535
- status_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535
- status_doc_sha256: `e59cbaab0a0a4e62b57226147edd4a5bd8bfee86911eb3a2b4e98b1b0bb12517`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","eventTime":"13:45","marketEventType":"closed"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535
- time_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535
- time_doc_sha256: `e59cbaab0a0a4e62b57226147edd4a5bd8bfee86911eb3a2b4e98b1b0bb12517`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","eventTime":"13:45","marketEventType":"closed"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. Close moved from 12:45 CT (2019-2023) to 13:45 CT: CME's 2024 Thanksgiving settlement notice gives 'Energy Products Normal Settlement Schedule' for Friday November 29 (the 2023 notice had 'Energy Products 13:30:00 ET'). The 2024-07-08 capture also gives 13:45.

### 2024-12-24 Christmas Eve

- kind early_halt, halt_ct 12:45; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537
- status_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537
- status_doc_sha256: `183c85160e31d53fde30c422048b8e778937d8866f3ea1c45e2dd570ea9db1c8`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eventTime":"12:45","marketEventType":"closed"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537
- time_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537
- time_doc_sha256: `183c85160e31d53fde30c422048b8e778937d8866f3ea1c45e2dd570ea9db1c8`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eventTime":"12:45","marketEventType":"closed"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. Capture 2024-12-20, before the day (the 2024-07-08 capture agrees). CME's 2024 Christmas settlement notice: 'Energy Products Settlement Time: 13:30:00 ET' (12:30 CT).

### 2024-12-25 Christmas Day

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537
- status_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537
- status_doc_sha256: `183c85160e31d53fde30c422048b8e778937d8866f3ea1c45e2dd570ea9db1c8`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eventTime":"12:45","marketEventType":"closed"}]} ... {"groupCode":"CL","eventDate":"2024-12-25","events":[{"tradingDate":"2024-12-26","eventTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-12-26","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2025-01-01 New Year's Day

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1734710019538
- status_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1734710019538
- status_doc_sha256: `6b6399a1de34bbc9eea0a135691dfed90edee2a0c705162b1840e214256e4c46`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31","eventTime":"16:00","marketEventType":"closed"}]} ... {"groupCode":"CL","eventDate":"2025-01-01","events":[{"tradingDate":"2025-01-02","eventTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-01-02","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. Capture 2024-12-20, before the holiday.

### 2025-01-20 Martin Luther King Jr. Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539
- status_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539
- status_doc_sha256: `2cdfb6d5a2bbc1b6b159f5c980d2bf70350c5b181c8d91c3c1023d1eb6a26175`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-01-20","events":[{"tradingDate":"2025-01-21","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-01-21","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539
- time_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539
- time_doc_sha256: `2cdfb6d5a2bbc1b6b159f5c980d2bf70350c5b181c8d91c3c1023d1eb6a26175`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-01-20","events":[{"tradingDate":"2025-01-21","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-01-21","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. Capture 2024-12-20, the only one of this window: CME's schedule as planned.

### 2025-02-17 Presidents Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540
- status_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540
- status_doc_sha256: `46119e9af5875c05dee480d7465b431344d0c5bf55492ca1ebb92024a77b5f72`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-02-17","events":[{"tradingDate":"2025-02-18","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-02-18","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540
- time_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540
- time_doc_sha256: `46119e9af5875c05dee480d7465b431344d0c5bf55492ca1ebb92024a77b5f72`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-02-17","events":[{"tradingDate":"2025-02-18","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-02-18","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. Capture 2024-12-20, the only one of this window: CME's schedule as planned.

### 2025-04-18 Good Friday

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-04-17&toEventDate=2025-04-19&isProtected&_t=1734710019542
- status_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-04-17&toEventDate=2025-04-19&isProtected&_t=1734710019542
- status_doc_sha256: `c067674b1c10456f5fd86da6db1438b54fa3e352a44662674eb9a9411332edd3`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-04-17","events":[{"tradingDate":"2025-04-17","eventTime":"16:00","marketEventType":"closed"}]} ... {"groupCode":"CL","eventDate":"2025-04-18","events":[]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. Capture 2024-12-20, the only one of this window: CME's schedule as planned.

### 2025-05-26 Memorial Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543
- status_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543
- status_doc_sha256: `73d01c7c3c0cd47c4fb9d6cf14a7c60a1f80d2c81e6a26d42e4c7a1367c94c35`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-05-26","events":[{"tradingDate":"2025-05-27","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-05-27","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543
- time_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543
- time_doc_sha256: `73d01c7c3c0cd47c4fb9d6cf14a7c60a1f80d2c81e6a26d42e4c7a1367c94c35`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-05-26","events":[{"tradingDate":"2025-05-27","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-05-27","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. Capture 2024-12-20, the only one of this window: CME's schedule as planned.

### 2025-06-19 Juneteenth

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544
- status_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544
- status_doc_sha256: `7dcceaa759e9888568093eb258a67be0513b443b72acd07dc873a75115854bee`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-06-19","events":[{"tradingDate":"2025-06-20","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-06-20","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544
- time_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544
- time_doc_sha256: `7dcceaa759e9888568093eb258a67be0513b443b72acd07dc873a75115854bee`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-06-19","events":[{"tradingDate":"2025-06-20","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-06-20","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. Capture 2024-12-20, the only one of this window: CME's schedule as planned.

### 2025-07-04 Independence Day

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545
- status_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545
- status_doc_sha256: `cd4008266d4387521824839b0b1858ac33bc2326fe3ade74f5f2d756b5d3026f`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-07-04","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2025-07-04","eventTime":"17:00","marketEventType":"open"}]} ... {"groupCode":"CL","eventDate":"2025-07-04","events":[{"tradingDate":"2025-07-04","eventTime":"12:00","marketEventType":"closed"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545
- time_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545
- time_doc_sha256: `cd4008266d4387521824839b0b1858ac33bc2326fe3ade74f5f2d756b5d3026f`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-07-04","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2025-07-04","eventTime":"17:00","marketEventType":"open"}]} ... {"groupCode":"CL","eventDate":"2025-07-04","events":[{"tradingDate":"2025-07-04","eventTime":"12:00","marketEventType":"closed"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. Capture 2024-12-20, the only one of this window: CME's schedule as planned. Friday holiday: 12:00 CT 'closed' (not the 13:30 CT halt of Monday-Thursday holidays), next open Sunday 17:00 CT; the same pattern as Juneteenth 2026-06-19 (captures before and after the day). The equity calendar's bars confirmed a 12:00 CT stop for ES on this day; energy bars are checked in Task 7.

### 2025-09-01 Labor Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546
- status_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546
- status_doc_sha256: `dff4ccaf3b18531b37b4ee789d2ca5e686a3c04f6dd1aa5c720b732a6832eeb0`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-09-01","events":[{"tradingDate":"2025-09-02","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-09-02","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546
- time_fetched_via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546
- time_doc_sha256: `dff4ccaf3b18531b37b4ee789d2ca5e686a3c04f6dd1aa5c720b732a6832eeb0`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-09-01","events":[{"tradingDate":"2025-09-02","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-09-02","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. Capture 2024-12-20, the only one of this window: CME's schedule as planned.

### 2025-11-27 Thanksgiving Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
- status_fetched_via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
- status_doc_sha256: `ab8342bd5dbc6dd78f4f6efe599b6448d47a0adffe1bd8baafa5337d49c08062`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-11-27","events":[{"tradingDate":"2025-11-28","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
- time_fetched_via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
- time_doc_sha256: `ab8342bd5dbc6dd78f4f6efe599b6448d47a0adffe1bd8baafa5337d49c08062`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-11-27","events":[{"tradingDate":"2025-11-28","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20260129012143. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2025-11-28 Day after Thanksgiving

- kind early_halt, halt_ct 13:45; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
- status_fetched_via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
- status_doc_sha256: `ab8342bd5dbc6dd78f4f6efe599b6448d47a0adffe1bd8baafa5337d49c08062`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"07:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45","marketEventType":"closed"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
- time_fetched_via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
- time_doc_sha256: `ab8342bd5dbc6dd78f4f6efe599b6448d47a0adffe1bd8baafa5337d49c08062`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"07:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45","marketEventType":"closed"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20260129012143. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. The 13:45 CT close is the schedule (the 2024-12-20 capture has only '13:45 closed'); this later capture also records the delayed 07:30 CT open after the CME outage: LATE_OPENS. CME's 2025 Thanksgiving settlement notice: 'Energy Products Settlement Times: Normal Settlement Schedule'.

### 2025-12-24 Christmas Eve

- kind early_halt, halt_ct 12:45; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
- status_fetched_via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
- status_doc_sha256: `6944a2dd28359cea6a47194c6e74ef9f8808229fd1411482025b962f87290cb2`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eventTime":"12:45","marketEventType":"closed"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
- time_fetched_via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
- time_doc_sha256: `6944a2dd28359cea6a47194c6e74ef9f8808229fd1411482025b962f87290cb2`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eventTime":"12:45","marketEventType":"closed"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20260129012143. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. CME's 2025 Christmas settlement notice: 'Energy Products Settlement Time: 13:30:00 ET' (12:30 CT).

### 2025-12-25 Christmas Day

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
- status_fetched_via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
- status_doc_sha256: `6944a2dd28359cea6a47194c6e74ef9f8808229fd1411482025b962f87290cb2`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eventTime":"12:45","marketEventType":"closed"}]} ... {"groupCode":"CL","eventDate":"2025-12-25","events":[{"tradingDate":"2025-12-26","eventTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-12-26","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20260129012143. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2026-01-01 New Year's Day

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066
- status_fetched_via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066
- status_doc_sha256: `9eb4ca23526ff7086662f547be2a5702d40f67d7ab21024ff7b3bac9e17e0d19`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31","eventTime":"16:00","marketEventType":"closed"}]} ... {"groupCode":"CL","eventDate":"2026-01-01","events":[{"tradingDate":"2026-01-02","eventTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2026-01-02","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20260129012143. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2026-01-19 Martin Luther King Jr. Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068
- status_fetched_via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068
- status_doc_sha256: `f8b1f22d11e3465a8b81b94e4f33a9e7cde1b32e35c11ee35965b219c2a55e1d`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2026-01-19","events":[{"tradingDate":"2026-01-20","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2026-01-20","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068
- time_fetched_via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068
- time_doc_sha256: `f8b1f22d11e3465a8b81b94e4f33a9e7cde1b32e35c11ee35965b219c2a55e1d`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2026-01-19","events":[{"tradingDate":"2026-01-20","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2026-01-20","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20260129012143. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2026-02-16 Presidents Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1743113432015
- status_fetched_via: https://web.archive.org/web/20260610104510id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1743113432015
- status_doc_sha256: `c1ddc73e2c8af4e695c5f35a49f30c988694d09f31e659f98ca2d232ee942543`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2026-02-16","events":[{"tradingDate":"2026-02-17","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2026-02-17","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1743113432015
- time_fetched_via: https://web.archive.org/web/20260610104510id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1743113432015
- time_doc_sha256: `c1ddc73e2c8af4e695c5f35a49f30c988694d09f31e659f98ca2d232ee942543`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2026-02-16","events":[{"tradingDate":"2026-02-17","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2026-02-17","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20260610104510. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2026-04-03 Good Friday

- kind full_closure, halt_ct -; evidence cme, time_evidence n/a; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1743113432016
- status_fetched_via: https://web.archive.org/web/20260610104510id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1743113432016
- status_doc_sha256: `cdba0a6550c433978ef2818881d3f80efd34a5f8b1746bb764457d7c7bb3e5da`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02","eventTime":"16:00","marketEventType":"closed"}]} ... {"groupCode":"CL","eventDate":"2026-04-03","events":[]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20260610104510. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. Jobs-report Good Friday: equities, rates and FX traded (CME 2026 Good Friday clearing advisory); energy has no event on 04-03.

### 2026-05-25 Memorial Day

- kind early_halt, halt_ct 13:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1749141516014
- status_fetched_via: https://web.archive.org/web/20260619114105id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1749141516014
- status_doc_sha256: `0abe70f6b4cb1a6ad8022d71993016b4219333a2b6a4fbc44c3a8cdbb4cffdf9`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2026-05-25","events":[{"tradingDate":"2026-05-26","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2026-05-26","eventTime":"17:00","marketEventType":"open"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1749141516014
- time_fetched_via: https://web.archive.org/web/20260619114105id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1749141516014
- time_doc_sha256: `0abe70f6b4cb1a6ad8022d71993016b4219333a2b6a4fbc44c3a8cdbb4cffdf9`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2026-05-25","events":[{"tradingDate":"2026-05-26","eventTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2026-05-26","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20260619114105. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date.

### 2026-06-19 Juneteenth

- kind early_halt, halt_ct 12:00; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-18&toEventDate=2026-06-20&isProtected&_t=1784720540600
- status_fetched_via: https://web.archive.org/web/20260722114220id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-18&toEventDate=2026-06-20&isProtected&_t=1784720540600
- status_doc_sha256: `8443ca95be51e95f953be29b713a9b996f298015f692e3d6706be8201f430bb2`
- status_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-06-22","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2026-06-22","eventTime":"17:00","marketEventType":"open"}]} ... {"groupCode":"CL","eventDate":"2026-06-19","events":[{"tradingDate":"2026-06-22","eventTime":"12:00","marketEventType":"closed"}]}"
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-18&toEventDate=2026-06-20&isProtected&_t=1784720540600
- time_fetched_via: https://web.archive.org/web/20260722114220id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-18&toEventDate=2026-06-20&isProtected&_t=1784720540600
- time_doc_sha256: `8443ca95be51e95f953be29b713a9b996f298015f692e3d6706be8201f430bb2`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-06-22","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2026-06-22","eventTime":"17:00","marketEventType":"open"}]} ... {"groupCode":"CL","eventDate":"2026-06-19","events":[{"tradingDate":"2026-06-22","eventTime":"12:00","marketEventType":"closed"}]}"
- notes: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback capture 20260722114220. CL stands for the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a time = trading halts (order entry only) until the next 'open'; 'closed' = final close of the trade date. Friday holiday: 12:00 CT 'closed', next open Sunday 17:00 CT (trade date 06-22). The 2026-01-29 and 2026-06-19 captures agree. The same capture shows Saturday 06-20 events ('05:00 open', '17:00 closed', trade date 06-22) for CL, ES and GC alike; 06-20 is outside the coverage and is not an entry.

### 2025-11-28 Globex outage (data-center cooling failure)

- kind late_open, halt_ct -, open_ct 07:30; evidence cme, time_evidence cme; verbatim_check True; bar_check_status: pending Task 7 (research-window bars)
- status_url: https://www.sec.gov/Archives/edgar/data/1156375/000115637526000009/cme-20251231.htm
- status_fetched_via: https://web.archive.org/web/20260226224856id_/https://www.sec.gov/Archives/edgar/data/1156375/000115637526000009/cme-20251231.htm
- status_doc_sha256: `57b0d2709e1032a568dd5ce23b211a4df357da99a0f30b14d2f9005dc63b08dd`
- status_quote: "On November 27, 2025, our largest data center owned and operated by CyrusOne experienced a critical cooling failure caused by human error. In response to the critical cooling failure, we made the decision to temporarily halt our markets. Our markets opened the following day on a delayed basis."
- time_url: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
- time_fetched_via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
- time_doc_sha256: `ab8342bd5dbc6dd78f4f6efe599b6448d47a0adffe1bd8baafa5337d49c08062`
- time_quote: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"07:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45","marketEventType":"closed"}]}"
- notes: Unscheduled. Status: CME Group's 2025 Form 10-K (SEC EDGAR, read from its Wayback capture; sec.gov refused the direct fetch). Open time: CME's CL service record for eventDate 2025-11-28 in the 2026-01-29 capture adds '07:00 preopen' and '07:30 open' before the scheduled 13:45 close; the 2024-12-20 capture (the plan) has only the 13:45 close. The time trading stopped on the evening of 2025-11-27 is in no CME document retrieved (halt_from_ct None). The outage hit every CME Globex group; data/cme_calendar.py does not record it.

## CME-stated normal days (NO_ENTRY_FINDINGS)

| Date | Finding | Verbatim | Source | Quote |
|---|---|---|---|---|
| 2019-07-03 | Day before Independence Day: regular close | True | https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | Calendar Date\|Wednesday July 3 \|Wednesday,July 3\|Thursday July 4 \|Thursday July 4 into Friday July 5 ... Product\|CLOSE\|OPEN\|HALT\|OPEN ... Energy, Metals & DME \|Regular @ 1600 CT / 2100 UTC\|Regular @ 1700 CT/ 2200 UTC\|1200 CT / 1700 UTC\|Regular @ 1700 CT / 2200 UTC |
| 2019-10-14 | Columbus Day: normal | True | https://web.archive.org/web/20241212022305id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-columbus-day-holiday-settlement-times.pdf | All products will settle at their normal times for the Columbus Day Holiday |
| 2019-12-31 | New Year's Eve: regular close | True | https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | Calendar Trade\|Tuesday, Dec 31\|Wednessday, Jan 1 \|Wednesday, Jan 1\|Thursday, Jan 2\|Thursday, Jan 2 ... Energy, Metals & DME \|Regular @ 1600 CT / 2200 UTC\|Closed for New Year's\|Regular @ 1700 CT / 2300 UTC\|\|Regular @ 1600 CT / 2200 UTC |
| 2020-07-02 | Day before Independence Day (observed): regular close | True | https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | Calendar Date\|Thursday July 2\|Thursday , July 2\|Friday July 3\|Sunday July 5 into Monday July 6 ... Energy, Metals & DME \|Regular @ 1600 CT / 2100 UTC\|Regular @ 1700 CT/ 2200 UTC\|1200 CT / 1700 UTC\|Regular @ 1700 CT / 2200 UTC |
| 2020-12-31 | New Year's Eve: regular close | True | https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | Calendar Trade\|Thursday,Dec 31\|Friday,Jan 1\|Sunday,Jan 3\|Monday, Jan 4\|Monday, Jan 4 ... Energy, Metals & DME \|Regular @ 1600 CT / 2200 UTC\|Closed for New Year's\|Regular @ 1700 CT / 2300 UTC\|\|Regular @ 1600 CT / 2200 UTC |
| 2021-12-23 | Day before Christmas (observed): regular close | True | https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | Products\|Thursday, Dec 23\|Friday,Dec 24\|Sunday 26\|Monday,Dec 27 ... Energy, Metals & DME \|Regular per Product\|Closed for Christmas |
| 2021-12-31 | New Year's Eve (New Year's Day on Saturday): regular | True | https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | CME Group Globex New Years Holiday Schedule: December 30, 2021 - January 3, 2022 ... Calendar Trade\|Thursday,Dec 30\|Thursday,Dec 30\|Friday,Dec 31\|Friday,Dec 31\|Sunday,Jan 2\|Monday, Jan 3 ... Energy, Metals & DME \|Regular @ 1600 CT / 2200 UTC\|Regular @ 1700 CT / 2300 UTC\|\|Regular @ 1600 CT / 2200 UTC\|Regular @ 1700 CT / 2300 UTC |
| 2022-07-01 | Friday before Independence Day: regular close | True | https://web.archive.org/web/20220704065431id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls | Calendar Date\|Friday July 1\|Sunday July 3\|Monday July 4\|Monday July 4 ... Energy, Metals & DME \|Regular @ 1600 CT / 2100 UTC |
| 2022-12-23 | Friday before Christmas (observed): regular close | True | https://web.archive.org/web/20220704065430id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls | Calendar Date\|Friday, December 23\|\|\|\|\|\|\|\|Monday, December 26 ... Energy, Metals & DME products (see notes below)\|04:00:00 PM\|\|\|\|\|\|\|\|Globex Closed |
| 2022-12-30 | Friday before New Year's Day (observed): regular close | True | https://web.archive.org/web/20220704065450id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule-compact.xls | Calendar Trade\|Friday,Dec 30\|Sunday, Jan 1 and Monday, Jan 2 ... Energy, Metals & DME \|Regular @ 1600 CT / 2200 UTC\|Globex Closed |
| 2023-07-03 | Day before Independence Day: regular | True | https://web.archive.org/web/20230203064221id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2023.pdf | Monday, July 3, 2023 ... All other products will settle at their normal times on Monday July 3rd |
| 2023-12-22 | Friday before Christmas: regular | True | https://web.archive.org/web/20230203075043id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2023.pdf | Friday, December 22, 2023 ... Interest Rate Products ... All other products will settle at their normal times |
| 2024-07-03 | Day before Independence Day: regular close | True | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680 | "globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-07-03","events":[{"tradingDate":"2024-07-03","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-07-05","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","marketEventType":"open"}]} |
| 2024-12-31 | New Year's Eve: regular close | True | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1734710019538 | "globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31","eventTime":"16:00","marketEventType":"closed"}]} |
| 2025-01-09 | National Day of Mourning (Carter): energy normal hours | True | https://web.archive.org/web/20250218194143id_/https://www.cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf | PRODUCT NAME JANUARY 9, 2025 ... CME GROUP ENERGY NORMAL HOURS |
| 2025-07-03 | Day before Independence Day: regular close | True | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545 | "globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-07-04","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2025-07-04","eventTime":"17:00","marketEventType":"open"}]} |
| 2025-12-31 | New Year's Eve: regular close | True | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066 | "globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31","eventTime":"16:00","marketEventType":"closed"}]} |
| 2026-04-02 | Thursday before Good Friday: regular close | True | https://web.archive.org/web/20260610104510id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1743113432016 | "globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02","eventTime":"16:00","marketEventType":"closed"}]} |
| 2026-06-18 | Thursday before Juneteenth: regular close | True | https://web.archive.org/web/20260722114220id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-18&toEventDate=2026-06-20&isProtected&_t=1784720540600 | "globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-06-22","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2026-06-22","eventTime":"17:00","marketEventType":"open"}]} |

## Session-hour changes found

- Regular session: none. NYMEX energy traded Sunday-Friday 17:00-16:00 CT with the daily 16:00-17:00 CT halt throughout 2019-05-01..2026-06-19 (CME contract specifications for CL, NG, RB, HO in 2019, the MCL/QM fact card of 2021, the MNG FAQ of 2025, CME's 2026 CL trading-hours record). No CME notice of a change was found. SESSIONS is one regime.
- Holiday-schedule conventions (holiday entries, not regular-session changes): (1) the energy holiday halt moved from 12:00 CT (last: 2021-11-25) to 13:30 CT (first: 2022-01-17); (2) the day-after-Thanksgiving close moved from 12:45 CT (last: 2023-11-24, energy settled 13:30 ET that day) to 13:45 CT (first: 2024-11-29, energy on its normal settlement schedule); (3) a holiday that falls on a Friday closes at 12:00 CT in both periods (2020-07-03, 2025-07-04, 2026-06-19).
- Unscheduled: the 2025-11-27/28 CME Globex outage (CyrusOne data-center cooling failure). CME's service record shows the 2025-11-28 session reopening at 07:30 CT (pre-open 07:00); CME's 2025 10-K states the markets were halted and 'opened the following day on a delayed basis'. The time trading stopped on 2025-11-27 is in no CME document retrieved. Recorded as LATE_OPENS[2025-11-28] (additive extension, same fields as the rates group's LateOpen). Interface extension: `LateOpen` dataclass, `LATE_OPENS` and `LATE_OPEN_SOURCES` in data/calendars/energy.py; HOLIDAYS keeps the data.cme_calendar type, so existing callers are unaffected. The lead rules whether the bar builder applies LATE_OPENS.

## D6 confirmation

D6 energy row: O 08:00, C 13:30, F 15:08 CT. Encoded unchanged in SESSIONS.day_session_ct for all eight products.

- C 13:30 CT: CONFIRMED. CME's daily settlement time range for 'Energy Products' is '14:28:00-14:30:00 ET' (13:28-13:30 CT; CME client wiki 'Daily Settlement Time Details', updated 2025-01-03). By sub-group: CL 'The settlement period is defined as: 14:28:00 to 14:30:00 ET for the Active Month' (wiki 'NYMEX Crude Oil', 2025, and the same text on the cmegroup.com page last modified 2019-05-08, captured 2021-12-02); QM 'derived directly from the settlements of the regular sized Crude Oil (CL) futures'; NG '14:28:00 to 14:30:00 ET'; QG 'derived directly from the settlements of the regular sized Natural Gas (NG) contracts'; HO and RB '14:28:00 to 14:30:00 ET for the Active Month'. MCL and MNG have no product page of their own; the 'Energy Products' line covers them. On holiday early-close days CME moves the energy settlement (12:30 CT on Christmas Eve and, to 2023, the day after Thanksgiving): the rules engine's early-close F handles those days.
- O 08:00 CT: NOT CONFIRMABLE from CME. No CME settlement procedure, contract specification or holiday schedule retrieved defines a day-session open for NYMEX energy; the only CME session boundaries are the Globex 17:00 CT open and 16:00 CT close. D6's value is encoded unchanged and flagged for the lead's ruling.
- F 15:08 CT: from Topstep (D9.1), not CME; it lies inside the energy Globex session (ends 16:00 CT), and every energy holiday halt or early close precedes it, so early-close F (halt minus 15 minutes) applies on all 59 early-halt entries.

## Entries graded unverified or secondary, and why

- None graded secondary or unverified (status or time).
- One time graded inferred: 2023-01-16 (MLK Day) 13:30 CT. No CME Globex schedule with a NYMEX energy row for that day was retrievable: the 2023 MLK summary PDF was not archived, the service capture of 2024-07-08 returns no events for the 2023-01-15..17 window, and the CME MLK 2023 compact schedule captured covers only MGEX and DME. The time is inferred from that CME schedule's DME row (13:30 CT halt; CME grouped DME with NYMEX energy in its 2019-2022 schedules) and matches every other 2022-2026 energy holiday halt; AMP Futures' image of CME's table (secondary, not machine-checkable) shows 'Energies' 13:30 CST. Status is CME-direct (settlement notice naming NYMEX).

## Gaps

- No year is filled by pattern: every entry cites a document for its own date.
- Pre-event captures only (CME's schedule as planned; no capture after the day): 2024-12-24, 2025-01-01 (capture 2024-12-20), and 2025-01-20, 2025-02-17, 2025-04-18, 2025-05-26, 2025-06-19, 2025-07-04, 2025-09-01 (capture 2024-12-20). 2022 Christmas (2022-12-26) and New Year 2023 (2023-01-02) rest on schedules captured 2022-07-04, also before the day; CME's settlement notices agree on the status of both.
- 2025-07-04 12:00 CT (Friday close) rests on one pre-event capture; the 12:00 Friday pattern is confirmed after the fact for 2026-06-19 (capture 2026-07-22). Task 7's bars check it.
- 2023-01-16 time (above). 2023-02-20 and 2023-04-07 come from reused-name CME PDFs (cmegroup.com/files/presidents-day.pdf captured 2023-03-29, good-friday.pdf captured 2024-07-08) whose content is dated 2023 inside the document.
- Product scope: CME names CL in the 2023-09+ service records and gives asset-class rows elsewhere; MCL, QM, NG, MNG, QG, RB and HO are assumed to share the group hours (no exception row found). Task 7's bar check per product tests this.
- The 2025-11-27 halt start time is unsourced (LateOpen.halt_from_ct None).
- Not searched: unscheduled intraday Globex interruptions other than 2025-11-28 (no CME incident list was found); they are not calendar entries unless the lead rules otherwise.

## Session sources

- `cme_energy_hours` (verbatim True): https://web.archive.org/web/20190806095424id_/https://www.cmegroup.com/trading/energy/crude-oil/light-sweet-crude_contract_specifications.html (sha256 `6c8f316498d6a696...`): "Trading Hours Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. CT) with a 60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)"; time: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068: ""globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... {"groupCode":"CL","eventDate":"2026-01-20","events":[{"tradingDate":"2026-01-20","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-01-21","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2026-01-21","eventTime":"17:00","marketEventType":"open"}]}". Regular NYMEX energy Globex session, Sunday-Friday 17:00-16:00 CT with the daily 16:00-17:00 CT halt: CME's CL contract specifications (capture 2019-08-06) and CME's 2026 CL trading-hours record (16:00 closed, 16:45 pre-open, 17:00 open). The other SESSION_SOURCES keys give the same hours for NG, RB, HO (2019), MCL and QM (2021 fact card) and MNG (2025 FAQ). No CME notice of a change to NYMEX energy Globex hours in 2019-2026 was found.
- `cme_ng_hours` (verbatim True): https://web.archive.org/web/20190915224001id_/https://www.cmegroup.com/trading/energy/natural-gas/natural-gas_contract_specifications.html (sha256 `1bcbefcb4f928fdd...`): "Trading Hours Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. /CT) with a 60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)". NG contract specifications, capture 2019-09-15.
- `cme_rb_hours` (verbatim True): https://web.archive.org/web/20190915222104id_/https://www.cmegroup.com/trading/energy/refined-products/rbob-gasoline_contract_specifications.html (sha256 `7f269fe3a6252537...`): "Trading Hours Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. CT) with a 60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)". RB contract specifications, capture 2019-09-15.
- `cme_ho_hours` (verbatim True): https://web.archive.org/web/20190919124625id_/https://www.cmegroup.com/trading/energy/refined-products/heating-oil_contract_specifications.html (sha256 `3b0e71d8785ebb2e...`): "Trading Hours CME Globex: Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. Chicago Time/CT) with a 60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)". HO contract specifications, capture 2019-09-19.
- `cme_mcl_qm_hours` (verbatim True): https://web.archive.org/web/20211016122244id_/https://www.cmegroup.com/trading/energy/files/micro-wti-crude-oil-futures-fact-card.pdf (sha256 `ddb7a8cd67d90946...`): "PRODUCT CODE MCL QM CL ... CME Globex: Sunday – Friday: 5:00 p.m. to 4:00 p.m. Central Time (CT) ... Monday – Friday: 60-minute daily trading halt beginning at 4:00 p.m. CT". Micro WTI fact card (capture 2021-10-16): one trading-hours line for MCL, QM and CL.
- `cme_mng_hours` (verbatim True): https://web.archive.org/web/20250114125534id_/https://www.cmegroup.com/articles/faqs/micro-henry-hub-natural-gas-futures-and-options-frequently-asked-questions.html (sha256 `3268418a30803b36...`): "PRODUCT CODE MNG QG MNO ... TRADING SCHEDULE CME Globex: Sunday – Friday: 5:00 p.m. to 4:00 p.m. Central Time (CT) ... Monday – Friday: 60-minute daily trading halt beginning at 4:00 p.m. CT". Micro Henry Hub FAQ (capture 2025-01-14): MNG, QG and NG share the Globex schedule. The FAQ dates MNG's launch to November 2023.
- `cme_energy_settlement` (verbatim True): https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457085528/Daily+Settlement+Time+Details (sha256 `725eb929d3d91045...`): "Energy Products 14:28:00-14:30:00 ET"; time: https://web.archive.org/web/20211022221401id_/https://www.cmegroup.com/confluence/display/EPICSANDBOX/NYMEX+Crude+Oil: "last modified by Confluence Admin on May 08, 2019 ... The settlement period is defined as: 14:28:00 to 14:30:00 ET for the Active Month and 14:28:00 to 14:30:00 ET for calendar spreads.". D6 confirmation of C: CME's daily settlement time range for 'Energy Products' is 14:28:00-14:30:00 ET = 13:28:00-13:30:00 CT (CME client wiki 'Daily Settlement Time Details', updated 2025-01-03, read directly). The CL procedure page as captured 2021-12-02 (last modified 2019-05-08) gives the same period, so C = 13:30 CT held for the whole 2019-2026 window. MCL and MNG have no product page of their own; the 'Energy Products' line covers them.
- `cme_cl_qm_settlement` (verbatim True): https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457218849/NYMEX+Crude+Oil (sha256 `327dd521900168d9...`): "NYMEX Light Sweet Crude Oil (CL) futures are settled by CME Group staff based on trading activity on CME Globex during the settlement period. The settlement period is defined as: 14:28:00 to 14:30:00 ET for the Active Month ... The settlements in the E-mini Crude Oil (QM) futures contracts are derived directly from the settlements of the regular sized Crude Oil (CL) futures contracts". CME client wiki 'NYMEX Crude Oil' (updated 2025-08-27, read directly).
- `cme_ng_qg_settlement` (verbatim True): https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457415061/Natural+Gas (sha256 `b3c56a3296706e34...`): "NYMEX Natural Gas (NG) futures are settled by CME Group staff based on trading activity on CME Globex during the settlement period. The settlement period is defined as: 14:28:00 to 14:30:00 ET ... The settlements in the E-Mini Natural Gas (QG) futures contracts are derived directly from the settlements of the regular sized Natural Gas (NG) contracts". CME client wiki 'Natural Gas' (updated 2025-08-27, read directly).
- `cme_ho_settlement` (verbatim True): https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457415161/NYMEX+Heating+Oil (sha256 `c3ac26d5c7fcaa0e...`): "NYMEX NY Harbor ULSD (HO) futures are settled by CME Group staff based on trading activity on CME Globex during the settlement period. The settlement period is defined as: 14:28:00 to 14:30:00 ET for the Active Month". CME client wiki 'NYMEX Heating Oil' (updated 2025-08-27, read directly).
- `cme_rb_settlement` (verbatim True): https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457088078/NYMEX+RBOB+Gasoline (sha256 `82eaa5b9b674c263...`): "NYMEX RBOB Gasoline (RB) futures are settled by CME Group staff based on trading activity on CME Globex during the settlement period. The settlement period is defined as: 14:28:00 to 14:30:00 ET for the Active Month". CME client wiki 'NYMEX RBOB Gasoline' (updated 2025-08-27, read directly).

## Fetch log

Times PDT (America/Vancouver), 2026-09-25. 'cache hit' = a file another CalendarBuilder had already fetched into the shared cache (reused, not re-fetched). FAIL rows: 20 Wayback connection refusals under load (curl exit 7, HTTP 000), each retried successfully; 2 HTTP 404 for the standalone 2022-new-years compact capture listed by CDX (not served; the identical-name member of CME's 2021 zip was used instead); 1 HTTP 403 from sec.gov (the 10-K was read from its Wayback capture). Every cited document was fetched.

- Wayback CDX listings (not individually timestamped; all between 00:25 and 01:05 PDT): cmegroup.com/tools-information/holiday-calendar/files/ (prefix), cmegroup.com/trading-hours/ (prefix), cmegroup.com/services/trading-hours (prefix), cmegroup.com/trading-hours.html (2022-2026), cmegroup.com/files/ (prefix), the CL contract-spec pages, cmegroup.com/confluence/display/EPICSANDBOX/NYMEX+Crude+Oil, the sec.gov 10-K, cmegroup.com/media-room/press-releases/2025/11/ (no outage release captured). CDX requests that failed (timeout or refusal) and were not retried: the cmegroup.com/market-data/settlements/ and cmegroup.com/confluence/display/EPICSANDBOX/ prefixes, and the EPICSANDBOX Daily+Settlement+Time+Details and Natural+Gas pages (the current versions were read directly on atlassian.net instead). The first holiday-calendar CDX request returned HTTP 504 and was retried successfully.
- WebSearch (4 queries, no budget notice received): the NYMEX energy daily settlement procedure; the 2025-11-27/28 CME Globex outage; changes to NYMEX energy Globex hours 2019-2025 (none found); MCL/MNG settlement. Search results were used only to locate documents; every cited text was fetched.

| Time PDT | URL | Result |
|---|---|---|
| 00:25:11 | CDX cmegroup.com/tools-information/holiday-calendar/files/* | OK |
| 00:25:40 | CDX cmegroup.com/trading-hours/ prefix | OK |
| 00:25:45 | https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | cache hit |
| 00:25:45 | https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | OK 200 https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-inform |
| 00:25:46 | https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | OK 200 https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-inform |
| 00:25:47 | https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2018-holiday-calendars.zip | OK 200 https://web.archive.org/web/20260830100225id_/https://www.cmegroup.com/tools-inform |
| 00:27:31 | https://web.archive.org/web/20220704065430id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls | OK 200 https://web.archive.org/web/20220704065430id_/https://www.cmegroup.com/tools-inform |
| 00:27:32 | https://web.archive.org/web/20220412171426id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule-compact.xls | OK 200 https://web.archive.org/web/20220412171426id_/https://www.cmegroup.com/tools-inform |
| 00:27:32 | https://web.archive.org/web/20220704065501id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule.xls | OK 200 https://web.archive.org/web/20220704065501id_/https://www.cmegroup.com/tools-inform |
| 00:27:34 | https://web.archive.org/web/20220704065431id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls | OK 200 https://web.archive.org/web/20220704065431id_/https://www.cmegroup.com/tools-inform |
| 00:27:34 | https://web.archive.org/web/20220704065450id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls | OK 200 https://web.archive.org/web/20220704065450id_/https://www.cmegroup.com/tools-inform |
| 00:27:35 | https://web.archive.org/web/20220620200210id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls | OK 200 https://web.archive.org/web/20220620200210id_/https://www.cmegroup.com/tools-inform |
| 00:27:35 | https://web.archive.org/web/20220704072842id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule-compact.xls | FAIL 000 https://web.archive.org/web/20220704072842id_/https://www.cmegroup.com/tools-info |
| 00:27:36 | https://web.archive.org/web/20220704065441id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule.xls | FAIL 000 https://web.archive.org/web/20220704065441id_/https://www.cmegroup.com/tools-info |
| 00:27:36 | https://web.archive.org/web/20220704094237id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule-compact.xls | FAIL 000 https://web.archive.org/web/20220704094237id_/https://www.cmegroup.com/tools-info |
| 00:27:36 | https://web.archive.org/web/20220704065438id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule.xls | FAIL 000 https://web.archive.org/web/20220704065438id_/https://www.cmegroup.com/tools-info |
| 00:27:36 | https://web.archive.org/web/20220704065433id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule-compact.xls | FAIL 000 https://web.archive.org/web/20220704065433id_/https://www.cmegroup.com/tools-info |
| 00:27:36 | https://web.archive.org/web/20220117212230id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule.xls | FAIL 000 https://web.archive.org/web/20220117212230id_/https://www.cmegroup.com/tools-info |
| 00:27:37 | https://web.archive.org/web/20211230185015id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-new-years-holiday-schedule-compact.xls | FAIL 000 https://web.archive.org/web/20211230185015id_/https://www.cmegroup.com/tools-info |
| 00:27:37 | https://web.archive.org/web/20220102130655id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-new-years-holiday-schedule.xls | FAIL 000 https://web.archive.org/web/20220102130655id_/https://www.cmegroup.com/tools-info |
| 00:27:37 | https://web.archive.org/web/20220217175219id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule-compact.xls | FAIL 000 https://web.archive.org/web/20220217175219id_/https://www.cmegroup.com/tools-info |
| 00:27:38 | https://web.archive.org/web/20220704073810id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule.xls | FAIL 000 https://web.archive.org/web/20220704073810id_/https://www.cmegroup.com/tools-info |
| 00:27:38 | https://web.archive.org/web/20220704073046id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule-compact.xls | FAIL 000 https://web.archive.org/web/20220704073046id_/https://www.cmegroup.com/tools-info |
| 00:27:38 | https://web.archive.org/web/20220704065423id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls | FAIL 000 https://web.archive.org/web/20220704065423id_/https://www.cmegroup.com/tools-info |
| 00:27:38 | https://web.archive.org/web/20230313161640id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-good-friday-holiday-schedule-compact-mgex-dme.xls | FAIL 000 https://web.archive.org/web/20230313161640id_/https://www.cmegroup.com/tools-info |
| 00:27:39 | https://web.archive.org/web/20230313162054id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-juneteenth-holiday-schedule-compact-mgex-dme.xls | FAIL 000 https://web.archive.org/web/20230313162054id_/https://www.cmegroup.com/tools-info |
| 00:27:39 | https://web.archive.org/web/20230313162721id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-memorial-day-holiday-schedule-compact-mgex-dme.xls | FAIL 000 https://web.archive.org/web/20230313162721id_/https://www.cmegroup.com/tools-info |
| 00:27:39 | https://web.archive.org/web/20230313181421id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-mlk-day-holiday-schedule-compact-mgex-dme.xls | FAIL 000 https://web.archive.org/web/20230313181421id_/https://www.cmegroup.com/tools-info |
| 00:27:39 | https://web.archive.org/web/20220704065450id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule-compact.xls | FAIL 000 https://web.archive.org/web/20220704065450id_/https://www.cmegroup.com/tools-info |
| 00:27:39 | https://web.archive.org/web/20220704065501id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule.xls | OK 200 https://web.archive.org/web/20220704065501id_/https://www.cmegroup.com/tools-inform |
| 00:27:40 | https://web.archive.org/web/20230313161514id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-pesidents-day-holiday-schedule-compact-mgex-dme.xls | FAIL 000 https://web.archive.org/web/20230313161514id_/https://www.cmegroup.com/tools-info |
| 00:27:51 | https://web.archive.org/web/20220704065430id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls | cache hit |
| 00:27:51 | https://web.archive.org/web/20220412171426id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule-compact.xls | cache hit |
| 00:27:51 | https://web.archive.org/web/20220704065501id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule.xls | cache hit |
| 00:27:51 | https://web.archive.org/web/20220704065431id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls | cache hit |
| 00:27:51 | https://web.archive.org/web/20220704065450id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls | cache hit |
| 00:27:52 | https://web.archive.org/web/20220620200210id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls | cache hit |
| 00:27:52 | https://web.archive.org/web/20220704072842id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule-compact.xls | OK 200 https://web.archive.org/web/20220704072842id_/https://www.cmegroup.com/tools-inform |
| 00:27:56 | https://web.archive.org/web/20220704065441id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule.xls | OK 200 https://web.archive.org/web/20220704065441id_/https://www.cmegroup.com/tools-inform |
| 00:28:30 | https://web.archive.org/web/20220704094237id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule-compact.xls | OK 200 https://web.archive.org/web/20220704094237id_/https://www.cmegroup.com/tools-inform |
| 00:28:35 | https://web.archive.org/web/20220704065438id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule.xls | OK 200 https://web.archive.org/web/20220704065438id_/https://www.cmegroup.com/tools-inform |
| 00:28:39 | https://web.archive.org/web/20220704065433id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule-compact.xls | OK 200 https://web.archive.org/web/20220704065433id_/https://www.cmegroup.com/tools-inform |
| 00:28:43 | https://web.archive.org/web/20220117212230id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule.xls | OK 200 https://web.archive.org/web/20220117212230id_/https://www.cmegroup.com/tools-inform |
| 00:28:47 | https://web.archive.org/web/20211230185015id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-new-years-holiday-schedule-compact.xls | FAIL 404 https://web.archive.org/web/20211230185015id_/https://www.cmegroup.com/tools-info |
| 00:28:54 | https://web.archive.org/web/20220102130655id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-new-years-holiday-schedule.xls | OK 200 https://web.archive.org/web/20220102130655id_/https://www.cmegroup.com/tools-inform |
| 00:28:57 | https://web.archive.org/web/20220217175219id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule-compact.xls | OK 200 https://web.archive.org/web/20220217175219id_/https://www.cmegroup.com/tools-inform |
| 00:29:01 | https://web.archive.org/web/20220704073810id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule.xls | OK 200 https://web.archive.org/web/20220704073810id_/https://www.cmegroup.com/tools-inform |
| 00:29:05 | https://web.archive.org/web/20220704073046id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule-compact.xls | OK 200 https://web.archive.org/web/20220704073046id_/https://www.cmegroup.com/tools-inform |
| 00:29:08 | https://web.archive.org/web/20220704065423id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls | OK 200 https://web.archive.org/web/20220704065423id_/https://www.cmegroup.com/tools-inform |
| 00:29:13 | https://web.archive.org/web/20230313161640id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-good-friday-holiday-schedule-compact-mgex-dme.xls | OK 200 https://web.archive.org/web/20230313161640id_/https://www.cmegroup.com/tools-inform |
| 00:29:16 | https://web.archive.org/web/20230313162054id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-juneteenth-holiday-schedule-compact-mgex-dme.xls | OK 200 https://web.archive.org/web/20230313162054id_/https://www.cmegroup.com/tools-inform |
| 00:29:20 | https://web.archive.org/web/20230313162721id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-memorial-day-holiday-schedule-compact-mgex-dme.xls | OK 200 https://web.archive.org/web/20230313162721id_/https://www.cmegroup.com/tools-inform |
| 00:29:23 | https://web.archive.org/web/20230313181421id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-mlk-day-holiday-schedule-compact-mgex-dme.xls | OK 200 https://web.archive.org/web/20230313181421id_/https://www.cmegroup.com/tools-inform |
| 00:29:27 | https://web.archive.org/web/20220704065450id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule-compact.xls | cache hit |
| 00:29:27 | https://web.archive.org/web/20220704065501id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule.xls | cache hit |
| 00:29:27 | https://web.archive.org/web/20230313161514id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-pesidents-day-holiday-schedule-compact-mgex-dme.xls | OK 200 https://web.archive.org/web/20230313161514id_/https://www.cmegroup.com/tools-inform |
| 00:29:40 | https://web.archive.org/web/20211230185015id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-new-years-holiday-schedule-compact.xls | FAIL 404 https://web.archive.org/web/20211230185015id_/https://www.cmegroup.com/tools-info |
| 00:30:08 | https://web.archive.org/web/20230627125057id_/https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf | OK 200 https://web.archive.org/web/20230627125057id_/https://www.cmegroup.com/trading-hour |
| 00:30:12 | https://web.archive.org/web/20260719095248id_/https://www.cmegroup.com/trading-hours/files/christmas-day-2023.pdf | OK 200 https://web.archive.org/web/20260719095248id_/https://www.cmegroup.com/trading-hour |
| 00:30:17 | https://web.archive.org/web/20250218194143id_/https://www.cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf | OK 200 https://web.archive.org/web/20250218194143id_/https://www.cmegroup.com/trading-hour |
| 00:30:20 | https://web.archive.org/web/20230613185949id_/https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf | OK 200 https://web.archive.org/web/20230613185949id_/https://www.cmegroup.com/trading-hour |
| 00:30:24 | https://web.archive.org/web/20230802192446id_/https://www.cmegroup.com/trading-hours/files/labor-day-2023.pdf | OK 200 https://web.archive.org/web/20230802192446id_/https://www.cmegroup.com/trading-hour |
| 00:30:58 | https://web.archive.org/web/20230420224018id_/https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf | OK 200 https://web.archive.org/web/20230420224018id_/https://www.cmegroup.com/trading-hour |
| 00:32:02 | https://web.archive.org/web/20260811165716id_/https://www.cmegroup.com/trading-hours/files/new-years-day-2024.pdf | OK 200 https://web.archive.org/web/20260811165716id_/https://www.cmegroup.com/trading-hour |
| 00:32:06 | https://web.archive.org/web/20231203205929id_/https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf | OK 200 https://web.archive.org/web/20231209053815id_/https://www.cmegroup.com/trading-hour |
| 00:32:36 | https://web.archive.org/web/20241220155339id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1734710019526 | OK 200 https://web.archive.org/web/20241220155339id_/https://www.cmegroup.com/services/tra |
| 00:33:18 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2022-12-31&toEventDate=2023-01-02&isProtected&_t=1720455278630 | OK 200 https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/tra |
| 00:33:22 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-01-15&toEventDate=2023-01-17&isProtected&_t=1720455278636 | OK 200 https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/tra |
| 00:33:25 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-02-19&toEventDate=2023-02-21&isProtected&_t=1720455278640 | OK 200 https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/tra |
| 00:33:29 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-04-06&toEventDate=2023-04-08&isProtected&_t=1720455278642 | OK 200 https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/tra |
| 00:33:32 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-05-28&toEventDate=2023-05-30&isProtected&_t=1720455278644 | OK 200 https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/tra |
| 00:33:36 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-06-18&toEventDate=2023-06-20&isProtected&_t=1720455278646 | OK 200 https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/tra |
| 00:33:39 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-07-03&toEventDate=2023-07-05&isProtected&_t=1720455278650 | OK 200 https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/tra |
| 00:34:13 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-09-03&toEventDate=2023-09-05&isProtected&_t=1720455278654 | FAIL 000 https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/t |
| 00:36:47 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-11-22&toEventDate=2023-11-24&isProtected&_t=1720455278656 | cache hit |
| 00:36:47 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-24&toEventDate=2023-12-26&isProtected&_t=1720455278659 | cache hit |
| 00:36:47 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-31&toEventDate=2024-01-02&isProtected&_t=1720455278661 | cache hit |
| 00:36:47 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663 | cache hit |
| 00:36:47 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669 | cache hit |
| 00:36:47 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-03-28&toEventDate=2024-03-30&isProtected&_t=1720455278672 | cache hit |
| 00:36:47 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675 | cache hit |
| 00:36:47 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677 | cache hit |
| 00:36:47 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680 | cache hit |
| 00:36:47 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1720455278683 | cache hit |
| 00:36:47 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1734710019534 | OK 200 https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/tra |
| 00:37:50 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1720455278685 | cache hit |
| 00:37:50 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535 | OK 200 https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/tra |
| 00:38:24 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537 | OK 200 https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/tra |
| 00:38:37 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1734710019538 | OK 200 https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/tra |
| 00:38:41 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539 | cache hit |
| 00:38:41 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540 | cache hit |
| 00:38:41 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-04-17&toEventDate=2025-04-19&isProtected&_t=1734710019542 | cache hit |
| 00:38:41 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543 | cache hit |
| 00:38:41 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544 | cache hit |
| 00:38:41 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545 | OK 200 https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/tra |
| 00:38:45 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546 | OK 200 https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/tra |
| 00:38:49 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1734710019547 | OK 200 https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/tra |
| 00:39:22 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060 | OK 200 https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/tra |
| 00:39:36 | https://web.archive.org/web/20241220155341id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1734710019548 | OK 200 https://web.archive.org/web/20241220155341id_/https://www.cmegroup.com/services/tra |
| 00:39:39 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064 | OK 200 https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/tra |
| 00:39:43 | https://web.archive.org/web/20241220155341id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1734710019549 | OK 200 https://web.archive.org/web/20241220155341id_/https://www.cmegroup.com/services/tra |
| 00:39:46 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066 | OK 200 https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/tra |
| 00:39:49 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068 | cache hit |
| 00:39:49 | https://web.archive.org/web/20260129012309id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1769649789745 | OK 200 https://web.archive.org/web/20260129012309id_/https://www.cmegroup.com/services/tra |
| 00:39:54 | https://web.archive.org/web/20260610104510id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1743113432015 | OK 200 https://web.archive.org/web/20260610104510id_/https://www.cmegroup.com/services/tra |
| 00:39:58 | https://web.archive.org/web/20260129012309id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1769649789746 | OK 200 https://web.archive.org/web/20260129012309id_/https://www.cmegroup.com/services/tra |
| 00:40:11 | https://web.archive.org/web/20260610104510id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1743113432016 | OK 200 https://web.archive.org/web/20260610104510id_/https://www.cmegroup.com/services/tra |
| 00:40:15 | https://web.archive.org/web/20260129012310id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1769649789747 | OK 200 https://web.archive.org/web/20260129012310id_/https://www.cmegroup.com/services/tra |
| 00:40:48 | https://web.archive.org/web/20260619114105id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1749141516014 | OK 200 https://web.archive.org/web/20260619114105id_/https://www.cmegroup.com/services/tra |
| 00:40:52 | https://web.archive.org/web/20260129012310id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-17&toEventDate=2026-06-19&isProtected&_t=1769649789748 | OK 200 https://web.archive.org/web/20260129012310id_/https://www.cmegroup.com/services/tra |
| 00:40:55 | https://web.archive.org/web/20260619113404id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-18&toEventDate=2026-06-20&isProtected&_t=1749141523693 | OK 200 https://web.archive.org/web/20260619113404id_/https://www.cmegroup.com/services/tra |
| 00:41:29 | https://web.archive.org/web/20260722114220id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-18&toEventDate=2026-06-20&isProtected&_t=1784720540600 | OK 200 https://web.archive.org/web/20260722114220id_/https://www.cmegroup.com/services/tra |
| 00:41:48 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-09-03&toEventDate=2023-09-05&isProtected&_t=1720455278654 | cache hit |
| 00:44:05 | https://web.archive.org/web/20221221043007id_/https://www.cmegroup.com/trading-hours.html | OK 200 https://web.archive.org/web/20221221043007id_/https://www.cmegroup.com/trading-hour |
| 00:44:38 | https://web.archive.org/web/20230219233358id_/https://www.cmegroup.com/trading-hours.html | OK 200 https://web.archive.org/web/20230219233358id_/https://www.cmegroup.com/trading-hour |
| 00:44:54 | https://web.archive.org/web/20230406195707id_/https://www.cmegroup.com/trading-hours.html | OK 200 https://web.archive.org/web/20230406195707id_/https://www.cmegroup.com/trading-hour |
| 00:45:55 | https://web.archive.org/web/20240708160009id_/https://www.cmegroup.com/files/good-friday.pdf | OK 200 https://web.archive.org/web/20240708160009id_/https://www.cmegroup.com/files/good-f |
| 00:45:58 | https://web.archive.org/web/20230329115747id_/https://www.cmegroup.com/files/presidents-day.pdf | OK 200 https://web.archive.org/web/20230329115747id_/https://www.cmegroup.com/files/presid |
| 00:46:12 | https://web.archive.org/web/20230203065333id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-good-friday-advisory.pdf | cache hit |
| 00:46:12 | https://web.archive.org/web/20230203071256id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-mlk-day-advisory.pdf | cache hit |
| 00:46:12 | https://web.archive.org/web/20220128031643id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-advisory.pdf | OK 200 https://web.archive.org/web/20220128031643id_/https://www.cmegroup.com/tools-inform |
| 00:46:16 | https://web.archive.org/web/20230203064614id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/good-friday-holiday-settlement-times-2023.pdf | cache hit |
| 00:46:16 | https://web.archive.org/web/20230203073653id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2023.pdf | cache hit |
| 00:46:31 | https://web.archive.org/web/20180508164650id_/http://www.cmegroup.com:80/tools-information/holiday-calendar/files/2019-new-years-advisory.pdf | OK 200 https://web.archive.org/web/20180508164650id_/http://www.cmegroup.com:80/tools-info |
| 00:46:39 | https://web.archive.org/web/20240628032233id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-4th-of-july-advisory.pdf | OK 200 https://web.archive.org/web/20240628032233id_/https://www.cmegroup.com/tools-inform |
| 00:47:12 | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457218849/NYMEX+Crude+Oil | OK 200 https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457218849/NY |
| 00:46:43 | https://web.archive.org/web/20240628152521id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-christmas-advisory.pdf | OK 200 https://web.archive.org/web/20240628152521id_/https://www.cmegroup.com/tools-inform |
| 00:47:17 | https://web.archive.org/web/20241212022103id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-christmas-holiday-settlement-times.pdf | OK 200 https://web.archive.org/web/20241212022103id_/https://www.cmegroup.com/tools-inform |
| 00:47:22 | https://web.archive.org/web/20240628034800id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-columbus-day-advisory.pdf | OK 200 https://web.archive.org/web/20240628034800id_/https://www.cmegroup.com/tools-inform |
| 00:47:26 | https://web.archive.org/web/20241212022305id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-columbus-day-holiday-settlement-times.pdf | OK 200 https://web.archive.org/web/20241212022305id_/https://www.cmegroup.com/tools-inform |
| 00:47:33 | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457415061/Natural+Gas | OK 200 https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457415061/Na |
| 00:47:37 | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457415161/NYMEX+Heating+Oil | OK 200 https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457415161/NY |
| 00:47:29 | https://web.archive.org/web/20240627181023id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-fourth-of-july-holiday-settlement-times.pdf | OK 200 https://web.archive.org/web/20240627181023id_/https://www.cmegroup.com/tools-inform |
| 00:47:41 | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457088078/NYMEX+RBOB+Gasoline | OK 200 https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457088078/NY |
| 00:47:45 | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457412940/Energy | OK 200 https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457412940/En |
| 00:48:06 | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457085528/Daily+Settlement+Time+Details | OK 200 https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457085528/Da |
| 00:47:43 | https://web.archive.org/web/20240627190501id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-good-friday-advisory.pdf | OK 200 https://web.archive.org/web/20240627190501id_/https://www.cmegroup.com/tools-inform |
| 00:48:47 | https://web.archive.org/web/20230203061740id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2024-new-years-advisory.pdf | OK 200 https://web.archive.org/web/20230203061740id_/https://www.cmegroup.com/tools-inform |
| 00:48:51 | https://web.archive.org/web/20241212010848id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025-new-years-advisory.pdf | OK 200 https://web.archive.org/web/20241212010848id_/https://www.cmegroup.com/tools-inform |
| 00:49:05 | https://web.archive.org/web/20241214001222id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/2025-4th-of-july-clearing-advisory.pdf | OK 200 https://web.archive.org/web/20241214001222id_/https://www.cmegroup.com/tools-inform |
| 00:49:08 | https://web.archive.org/web/20241214005158id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/2025-thanksgiving-clearing-advisory.pdf | OK 200 https://web.archive.org/web/20241214005158id_/https://www.cmegroup.com/tools-inform |
| 00:49:12 | https://web.archive.org/web/20241212004643id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/juneteenth-day-settlement-times-2025.pdf | OK 200 https://web.archive.org/web/20241212004643id_/https://www.cmegroup.com/tools-inform |
| 00:49:46 | https://web.archive.org/web/20241212000623id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/new-years-eve-holiday-settlement-times-2026.pdf | OK 200 https://web.archive.org/web/20241212000623id_/https://www.cmegroup.com/tools-inform |
| 00:49:49 | https://web.archive.org/web/20241212004808id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/us-independence-day-settlement-times-2025.pdf | OK 200 https://web.archive.org/web/20241212004808id_/https://www.cmegroup.com/tools-inform |
| 00:49:53 | https://web.archive.org/web/20260205021135id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2026/2026-juneteenth-clearing-advisory.pdf | OK 200 https://web.archive.org/web/20260205021135id_/https://www.cmegroup.com/tools-inform |
| 00:49:56 | https://web.archive.org/web/20251013214651id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2026/juneteenth-day-settlement-times-2026.pdf | OK 200 https://web.archive.org/web/20251013214651id_/https://www.cmegroup.com/tools-inform |
| 00:50:31 | https://web.archive.org/web/20220128031516id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2022.pdf | OK 200 https://web.archive.org/web/20220128031516id_/https://www.cmegroup.com/tools-inform |
| 00:50:34 | https://web.archive.org/web/20231121134649id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2024.pdf | OK 200 https://web.archive.org/web/20231121134649id_/https://www.cmegroup.com/tools-inform |
| 00:50:38 | https://web.archive.org/web/20230203064221id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2023.pdf | OK 200 https://web.archive.org/web/20230203064221id_/https://www.cmegroup.com/tools-inform |
| 00:48:18 | https://web.archive.org/web/20240626053134id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-good-friday-holiday-settlement-times.pdf | FAIL 000 https://web.archive.org/web/20240626053134id_/https://www.cmegroup.com/tools-info |
| 00:50:42 | https://web.archive.org/web/20220128021542id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/new-years-eve-holiday-settlement-times-2023.pdf | OK 200 https://web.archive.org/web/20220128021542id_/https://www.cmegroup.com/tools-inform |
| 00:51:16 | https://web.archive.org/web/20230203062741id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/new-years-eve-holiday-settlement-times-2024.pdf | OK 200 https://web.archive.org/web/20230203062741id_/https://www.cmegroup.com/tools-inform |
| 00:51:20 | https://web.archive.org/web/20231121113308id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/new-years-eve-holiday-settlement-times-2025.pdf | OK 200 https://web.archive.org/web/20231121113308id_/https://www.cmegroup.com/tools-inform |
| 00:51:26 | https://web.archive.org/web/20230203063905id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2023.pdf | OK 200 https://web.archive.org/web/20230203063905id_/https://www.cmegroup.com/tools-inform |
| 00:51:30 | https://web.archive.org/web/20231209141725id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2024.pdf | OK 200 https://web.archive.org/web/20231209141725id_/https://www.cmegroup.com/tools-inform |
| 00:51:33 | https://web.archive.org/web/20231122090808id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/us-independence-day-settlement-times-2024.pdf | OK 200 https://web.archive.org/web/20231122090808id_/https://www.cmegroup.com/tools-inform |
| 00:52:35 | https://www.sec.gov/Archives/edgar/data/1156375/000115637526000009/cme-20251231.htm | FAIL 403 https://www.sec.gov/Archives/edgar/data/1156375/000115637526000009/cme-20251231.h |
| 00:55:25 | https://web.archive.org/web/20260226224856id_/https://www.sec.gov/Archives/edgar/data/1156375/000115637526000009/cme-20251231.htm | OK 200 https://web.archive.org/web/20260226224856id_/https://www.sec.gov/Archives/edgar/da |
| 00:58:03 | https://web.archive.org/web/20190806095424id_/https://www.cmegroup.com/trading/energy/crude-oil/light-sweet-crude_contract_specifications.html | OK 200 https://web.archive.org/web/20190806095424id_/https://www.cmegroup.com/trading/ener |
| 00:58:08 | https://web.archive.org/web/20260511161031id_/https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.contractSpecs.html | OK 200 https://web.archive.org/web/20260511161031id_/https://www.cmegroup.com/markets/ener |
| 00:58:22 | https://web.archive.org/web/20190901000000id_/https://www.cmegroup.com/trading/energy/natural-gas/natural-gas_contract_specifications.html | OK 200 https://web.archive.org/web/20190915224001id_/https://www.cmegroup.com/trading/ener |
| 00:58:30 | https://web.archive.org/web/20190901000000id_/https://www.cmegroup.com/trading/energy/refined-products/rbob-gasoline_contract_specifications.html | OK 200 https://web.archive.org/web/20190915222104id_/https://www.cmegroup.com/trading/ener |
| 00:58:34 | https://web.archive.org/web/20190901000000id_/https://www.cmegroup.com/trading/energy/refined-products/heating-oil_contract_specifications.html | OK 200 https://web.archive.org/web/20190919124625id_/https://www.cmegroup.com/trading/ener |
| 00:59:14 | https://web.archive.org/web/20211202191714id_/https://www.cmegroup.com/confluence/display/EPICSANDBOX/NYMEX+Crude+Oil | OK 200 https://web.archive.org/web/20211022221401id_/https://www.cmegroup.com/confluence/d |
| 01:01:46 | https://web.archive.org/web/2024id_/https://www.cmegroup.com/trading/energy/files/micro-wti-crude-oil-futures-fact-card.pdf | OK 200 https://web.archive.org/web/20211016122244id_/https://www.cmegroup.com/trading/ener |
| 01:01:50 | https://web.archive.org/web/2024id_/https://www.cmegroup.com/articles/faqs/micro-henry-hub-natural-gas-futures-and-options-frequently-asked-questions.html | OK 200 https://web.archive.org/web/20250114125534id_/https://www.cmegroup.com/articles/faq |
