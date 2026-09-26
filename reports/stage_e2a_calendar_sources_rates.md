# Stage E.2a Task 6: CME Globex calendar, rates group (ZT, ZF, ZN, TN, ZB, UB)

CalendarBuilder-Rates (Opus 5.5, xhigh), 2026-09-25 PDT. Sourcing, code and synthetic tests only: no purchased market data was read. Module: `data/calendars/rates.py`; tests: `tests/test_e2a_calendar_rates.py`; full records: `reports/stage_e2a_calendar_sources_rates.json`.

## Summary

- Window 2019-05-01..2026-06-19: 80 entries: 63 early halts or early closes, 17 full closures; plus 1 late open (the unscheduled CME outage of 2025-11-28), 29 CME-stated regular days near holidays (NO_ENTRY_FINDINGS), 41 CME-published rates settlement times other than 14:00 CT, and 6 days with an early settlement but no CME Globex-hours document.
- Grades (status, time): cme/cme: 60; cme/inferred: 1; cme/n/a: 17; cme/secondary: 2.
- Verbatim check: 80/80 entries pass; failures anywhere: none.
- Session hours: one regime, Sunday-Friday 17:00-16:00 CT, no change found in 2019-2026.
- D6: C 14:00 CT confirmed by CME's Treasury settlement procedure; O 07:20 CT is not a CME-published time (see D6 confirmation); D6 values encoded unchanged.

## Method

CME Group's own documents, read through Wayback Machine copies (`id_` raw captures) because cmegroup.com refuses this machine, except the CME client-wiki page (Confluence REST API, direct). Every fetched file sits in the shared cache `scratchpad/e2a_cal_cache/` with its sha256 in `index.jsonl`; files another CalendarBuilder had already fetched were reused.

- 2019-2021: CME's yearly `YYYY-holiday-calendars.zip` (Globex trading schedules and settlement notices); 2022: one Globex schedule `.xls` per holiday. Row used: 'Interest Rate Products'. The date of each cell was read from the merged 'Calendar Date' and 'Trade Date' header cells with xlrd (recorded in each row's notes).
- 2023: CME's one-page holiday summary PDFs (`cmegroup.com/trading-hours/files/`), row 'INTEREST RATE' ('the most actively traded instruments for each asset class').
- 2023-09..2026-06: CME's `trading-hours-by-product` JSON service behind cmegroup.com/trading-hours.html, product id 316 = ZN '10-Year T-Note Futures', Wayback captures 2024-07-08, 2024-12-20, 2026-01-29 (and 2026-06-19). The 2024-07-08 capture returns empty event lists for 2023-01..07 ranges, as D.1f also found.
- Settlement notices and clearing advisories under `tools-information/holiday-calendar/files/` for status and settlement times; CME contract specifications and the CME client wiki 'Treasuries' page for the session and settlement time.
- Secondary sources only where no CME Globex-hours document exists: AMP Futures (2023-01-16, 2023-02-20, 2023-04-07 corroboration) and CNBC (2025-11-28 outage status).

Verbatim check (build script, not the test suite): Doc text conventions (the verbatim check normalizes whitespace on both sides): - .xls (Globex holiday schedules): LibreOffice CSV export of every sheet, '|' separated,   trailing '|' dropped per line; cells as LibreOffice displays them. - .pdf: `pdftotext -layout` output. - .json (trading-hours-by-product service): the raw response text (gunzipped if needed). - .html: tags stripped (scripts/styles removed), entities unescaped. - Confluence REST JSON: the page body (body.storage.value), then as .html. Normalization: zero-width characters (U+200B-U+200D, U+FEFF) are deleted, then every run of whitespace (spaces, tabs, newlines) becomes one space. A quote may elide text with '...'; each elided segment must be a substring on its own.

Scope caveat: CME states these hours for its interest-rate asset class ('Interest Rate Products', 'INTEREST RATE') or for ZN only (JSON service). ZT, ZF, TN, ZB and UB are taken to share them; the only rates exception row in the schedules read is 'Treasuries TAS' (its early TAS closes mark the early settlements below).

## Entries

| Date | Name | Kind | Halt CT | Status | Time | Status source | Time source | Verbatim | Bar check |
|---|---|---|---|---|---|---|---|---|---|
| 2019-05-27 | Memorial Day | early_halt | 12:00 | cme | cme | cme hc/2019-holiday-calendars.zip (Wayback 20210126094837) | cme hc/2019-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2019-07-04 | Independence Day | early_halt | 12:00 | cme | cme | cme hc/2019-holiday-calendars.zip (Wayback 20210126094837) | cme hc/2019-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2019-09-02 | Labor Day | early_halt | 12:00 | cme | cme | cme hc/2019-holiday-calendars.zip (Wayback 20210126094837) | cme hc/2019-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2019-11-28 | Thanksgiving Day | early_halt | 12:00 | cme | cme | cme hc/2019-holiday-calendars.zip (Wayback 20210126094837) | cme hc/2019-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2019-11-29 | Day after Thanksgiving | early_halt | 12:15 | cme | cme | cme hc/2019-holiday-calendars.zip (Wayback 20210126094837) | cme hc/2019-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2019-12-24 | Christmas Eve | early_halt | 12:15 | cme | cme | cme hc/2019-holiday-calendars.zip (Wayback 20210126094837) | cme hc/2019-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2019-12-25 | Christmas Day | full_closure | - | cme | n/a | cme hc/2019-holiday-calendars.zip (Wayback 20210126094837) | - | True | CME only, bar check pending the step 2 purchase |
| 2020-01-01 | New Year's Day | full_closure | - | cme | n/a | cme hc/2019-holiday-calendars.zip (Wayback 20210126094837) | - | True | CME only, bar check pending the step 2 purchase |
| 2020-01-20 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | cme | cme hc/2020-holiday-calendars.zip (Wayback 20260730000000) | cme hc/2020-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2020-02-17 | Presidents Day | early_halt | 12:00 | cme | cme | cme hc/2020-holiday-calendars.zip (Wayback 20260730000000) | cme hc/2020-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2020-04-10 | Good Friday | full_closure | - | cme | n/a | cme hc/2020-holiday-calendars.zip (Wayback 20260730000000) | - | True | CME only, bar check pending the step 2 purchase |
| 2020-05-25 | Memorial Day | early_halt | 12:00 | cme | cme | cme hc/2020-holiday-calendars.zip (Wayback 20260730000000) | cme hc/2020-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2020-07-03 | Independence Day (observed) | early_halt | 12:00 | cme | cme | cme hc/2020-holiday-calendars.zip (Wayback 20260730000000) | cme hc/2020-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2020-09-07 | Labor Day | early_halt | 12:00 | cme | cme | cme hc/2020-holiday-calendars.zip (Wayback 20260730000000) | cme hc/2020-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2020-11-26 | Thanksgiving Day | early_halt | 12:00 | cme | cme | cme hc/2020-holiday-calendars.zip (Wayback 20260730000000) | cme hc/2020-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2020-11-27 | Day after Thanksgiving | early_halt | 12:15 | cme | cme | cme hc/2020-holiday-calendars.zip (Wayback 20260730000000) | cme hc/2020-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2020-12-24 | Christmas Eve | early_halt | 12:15 | cme | cme | cme hc/2020-holiday-calendars.zip (Wayback 20260730000000) | cme hc/2020-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2020-12-25 | Christmas Day | full_closure | - | cme | n/a | cme hc/2020-holiday-calendars.zip (Wayback 20260730000000) | - | True | CME only, bar check pending the step 2 purchase |
| 2021-01-01 | New Year's Day | full_closure | - | cme | n/a | cme hc/2020-holiday-calendars.zip (Wayback 20260730000000) | - | True | CME only, bar check pending the step 2 purchase |
| 2021-01-18 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | cme | cme hc/2021-holiday-calendars.zip (Wayback 20260830000000) | cme hc/2021-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2021-02-15 | Presidents Day | early_halt | 12:00 | cme | cme | cme hc/2021-holiday-calendars.zip (Wayback 20260830000000) | cme hc/2021-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2021-04-02 | Good Friday (abbreviated, jobs report) | early_halt | 10:15 | cme | cme | cme hc/2021-holiday-calendars.zip (Wayback 20260830000000) | cme hc/2021-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2021-05-31 | Memorial Day | early_halt | 12:00 | cme | cme | cme hc/2021-holiday-calendars.zip (Wayback 20260830000000) | cme hc/2021-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2021-07-05 | Independence Day (observed) | early_halt | 12:00 | cme | cme | cme hc/2021-holiday-calendars.zip (Wayback 20260830000000) | cme hc/2021-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2021-09-06 | Labor Day | early_halt | 12:00 | cme | cme | cme hc/2021-holiday-calendars.zip (Wayback 20260830000000) | cme hc/2021-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2021-11-25 | Thanksgiving Day | early_halt | 12:00 | cme | cme | cme hc/2021-holiday-calendars.zip (Wayback 20260830000000) | cme hc/2021-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2021-11-26 | Day after Thanksgiving | early_halt | 12:15 | cme | cme | cme hc/2021-holiday-calendars.zip (Wayback 20260830000000) | cme hc/2021-holiday-calendars.zip | True | CME only, bar check pending the step 2 purchase |
| 2021-12-24 | Christmas Day (observed) | full_closure | - | cme | n/a | cme hc/2021-holiday-calendars.zip (Wayback 20260830000000) | - | True | CME only, bar check pending the step 2 purchase |
| 2022-01-17 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | cme | cme hc/2022-mlk-day-holiday-schedule.xls (Wayback 20220117212230) | cme hc/2022-mlk-day-holiday-schedule.xls | True | CME only, bar check pending the step 2 purchase |
| 2022-02-21 | Presidents Day | early_halt | 12:00 | cme | cme | cme hc/2022-presidents-day-holiday-schedule.xls (Wayback 20220704073810) | cme hc/2022-presidents-day-holiday-schedule.xls | True | CME only, bar check pending the step 2 purchase |
| 2022-04-15 | Good Friday | full_closure | - | cme | n/a | cme hc/2022-good-friday-holiday-schedule.xls (Wayback 20220704065501) | - | True | CME only, bar check pending the step 2 purchase |
| 2022-05-30 | Memorial Day | early_halt | 12:00 | cme | cme | cme hc/2022-memorial-day-holiday-schedule.xls (Wayback 20220704065438) | cme hc/2022-memorial-day-holiday-schedule.xls | True | CME only, bar check pending the step 2 purchase |
| 2022-06-20 | Juneteenth (observed) | early_halt | 12:00 | cme | cme | cme hc/2022-juneteenth-holiday-schedule.xls (Wayback 20220620200210) | cme hc/2022-juneteenth-holiday-schedule.xls | True | CME only, bar check pending the step 2 purchase |
| 2022-07-04 | Independence Day | early_halt | 12:00 | cme | cme | cme hc/2022-independence-day-holiday-schedule.xls (Wayback 20220704065450) | cme hc/2022-independence-day-holiday-schedule.xls | True | CME only, bar check pending the step 2 purchase |
| 2022-09-05 | Labor Day | early_halt | 12:00 | cme | cme | cme hc/2022-labor-day-holiday-schedule.xls (Wayback 20220704065441) | cme hc/2022-labor-day-holiday-schedule.xls | True | CME only, bar check pending the step 2 purchase |
| 2022-11-24 | Thanksgiving Day | early_halt | 12:00 | cme | cme | cme hc/2022-thanksgiving-holiday-schedule.xls (Wayback 20220704065423) | cme hc/2022-thanksgiving-holiday-schedule.xls | True | CME only, bar check pending the step 2 purchase |
| 2022-11-25 | Day after Thanksgiving | early_halt | 12:15 | cme | cme | cme hc/2022-thanksgiving-holiday-schedule.xls (Wayback 20220704065423) | cme hc/2022-thanksgiving-holiday-schedule.xls | True | CME only, bar check pending the step 2 purchase |
| 2022-12-26 | Christmas Day (observed) | full_closure | - | cme | n/a | cme hc/2022-christmas-holiday-schedule.xls (Wayback 20220704065430) | - | True | CME only, bar check pending the step 2 purchase |
| 2023-01-02 | New Year's Day (observed) | full_closure | - | cme | n/a | cme hc/2023-new-years-holiday-schedule.xls (Wayback 20220704065501) | - | True | CME only, bar check pending the step 2 purchase |
| 2023-01-16 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | secondary | cme hc/mlk-day-holiday-settlement-times-2023.pdf (Wayback 20230203073653) | https://www.ampfutures.com/news/holiday-trading-schedule-martin-luther-king-day-2023 | True | CME only, bar check pending the step 2 purchase |
| 2023-02-20 | Presidents Day | early_halt | 12:00 | cme | secondary | cme hc/presidents-day-holiday-settlement-times-2023.pdf (Wayback 20230203065411) | https://www.ampfutures.com/news/holiday-trading-schedule-presidents-day-2023 | True | CME only, bar check pending the step 2 purchase |
| 2023-04-07 | Good Friday (abbreviated, jobs report) | early_halt | 10:15 | cme | inferred | cme hc/good-friday-holiday-settlement-times-2023.pdf (Wayback 20230203064614) | cme hc/good-friday-holiday-settlement-times-2023.pdf | True | CME only, bar check pending the step 2 purchase |
| 2023-05-29 | Memorial Day | early_halt | 12:00 | cme | cme | cme th/memorial-day-2023.pdf (Wayback 20230420224018) | cme th/memorial-day-2023.pdf | True | CME only, bar check pending the step 2 purchase |
| 2023-06-19 | Juneteenth | early_halt | 12:00 | cme | cme | cme th/juneteenth-2023.pdf (Wayback 20230613185949) | cme th/juneteenth-2023.pdf | True | CME only, bar check pending the step 2 purchase |
| 2023-07-04 | Independence Day | early_halt | 12:00 | cme | cme | cme th/4th-of-july-2023.pdf (Wayback 20230627125057) | cme th/4th-of-july-2023.pdf | True | CME only, bar check pending the step 2 purchase |
| 2023-09-04 | Labor Day | early_halt | 12:00 | cme | cme | cme th/labor-day-2023.pdf (Wayback 20230802192446) | cme svc ZN 2023-09-03..023-09-05& | True | CME only, bar check pending the step 2 purchase |
| 2023-11-23 | Thanksgiving Day | early_halt | 12:00 | cme | cme | cme th/thanksgiving-day-2023.pdf (Wayback 20231203205929) | cme svc ZN 2023-11-22..023-11-24& | True | CME only, bar check pending the step 2 purchase |
| 2023-11-24 | Day after Thanksgiving | early_halt | 12:15 | cme | cme | cme th/thanksgiving-day-2023.pdf (Wayback 20231203205929) | cme svc ZN 2023-11-22..023-11-24& | True | CME only, bar check pending the step 2 purchase |
| 2023-12-25 | Christmas Day | full_closure | - | cme | n/a | cme th/christmas-day-2023.pdf (Wayback 20260719095248) | - | True | CME only, bar check pending the step 2 purchase |
| 2024-01-01 | New Year's Day | full_closure | - | cme | n/a | cme th/new-years-day-2024.pdf (Wayback 20260811165716) | - | True | CME only, bar check pending the step 2 purchase |
| 2024-01-15 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | cme | cme svc ZN 2024-01-14..024-01-16& (Wayback 20240708161439) | cme svc ZN 2024-01-14..024-01-16& | True | CME only, bar check pending the step 2 purchase |
| 2024-02-19 | Presidents Day | early_halt | 12:00 | cme | cme | cme svc ZN 2024-02-18..024-02-20& (Wayback 20240708161439) | cme svc ZN 2024-02-18..024-02-20& | True | CME only, bar check pending the step 2 purchase |
| 2024-03-29 | Good Friday | full_closure | - | cme | n/a | cme svc ZN 2024-03-28..024-03-30& (Wayback 20240708161439) | - | True | CME only; embargo or holdout-2 date, never checked against bars |
| 2024-05-27 | Memorial Day | early_halt | 12:00 | cme | cme | cme svc ZN 2024-05-26..024-05-28& (Wayback 20240708161439) | cme svc ZN 2024-05-26..024-05-28& | True | CME only; embargo or holdout-2 date, never checked against bars |
| 2024-06-19 | Juneteenth | early_halt | 12:00 | cme | cme | cme svc ZN 2024-06-18..024-06-20& (Wayback 20240708161439) | cme svc ZN 2024-06-18..024-06-20& | True | CME only; embargo or holdout-2 date, never checked against bars |
| 2024-07-04 | Independence Day | early_halt | 12:00 | cme | cme | cme svc ZN 2024-07-03..024-07-05& (Wayback 20240708161439) | cme svc ZN 2024-07-03..024-07-05& | True | CME only; embargo or holdout-2 date, never checked against bars |
| 2024-09-02 | Labor Day | early_halt | 12:00 | cme | cme | cme svc ZN 2024-09-01..024-09-03& (Wayback 20240708161439) | cme svc ZN 2024-09-01..024-09-03& | True | CME only; embargo or holdout-2 date, never checked against bars |
| 2024-11-28 | Thanksgiving Day | early_halt | 12:00 | cme | cme | cme svc ZN 2024-11-27..024-11-29& (Wayback 20240708161439) | cme svc ZN 2024-11-27..024-11-29& | True | CME only; embargo or holdout-2 date, never checked against bars |
| 2024-11-29 | Day after Thanksgiving | early_halt | 12:15 | cme | cme | cme svc ZN 2024-11-27..024-11-29& (Wayback 20240708161439) | cme svc ZN 2024-11-27..024-11-29& | True | CME only; embargo or holdout-2 date, never checked against bars |
| 2024-12-24 | Christmas Eve | early_halt | 12:15 | cme | cme | cme svc ZN 2024-12-24..024-12-26& (Wayback 20240708161439) | cme svc ZN 2024-12-24..024-12-26& | True | CME only; embargo or holdout-2 date, never checked against bars |
| 2024-12-25 | Christmas Day | full_closure | - | cme | n/a | cme svc ZN 2024-12-24..024-12-26& (Wayback 20240708161439) | - | True | CME only; embargo or holdout-2 date, never checked against bars |
| 2025-01-01 | New Year's Day | full_closure | - | cme | n/a | cme svc ZN 2024-12-31..025-01-02& (Wayback 20240708161439) | - | True | CME only; embargo or holdout-2 date, never checked against bars |
| 2025-01-09 | National Day of Mourning (Carter) | early_halt | 12:15 | cme | cme | cme th/day-of-mourning-january-9-2024.pdf (Wayback 20250218194143) | cme th/day-of-mourning-january-9-2024.pdf | True | CME only; embargo or holdout-2 date, never checked against bars |
| 2025-01-20 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | cme | cme svc ZN 2025-01-19..025-01-21& (Wayback 20241220155340) | cme svc ZN 2025-01-19..025-01-21& | True | CME only; embargo or holdout-2 date, never checked against bars |
| 2025-02-17 | Presidents Day | early_halt | 12:00 | cme | cme | cme svc ZN 2025-02-16..025-02-18& (Wayback 20241220155340) | cme svc ZN 2025-02-16..025-02-18& | True | CME only; embargo or holdout-2 date, never checked against bars |
| 2025-04-18 | Good Friday | full_closure | - | cme | n/a | cme svc ZN 2025-04-17..025-04-19& (Wayback 20241220155340) | - | True | pending Task 7 (research-window bars) |
| 2025-05-26 | Memorial Day | early_halt | 12:00 | cme | cme | cme svc ZN 2025-05-25..025-05-27& (Wayback 20241220155340) | cme svc ZN 2025-05-25..025-05-27& | True | pending Task 7 (research-window bars) |
| 2025-06-19 | Juneteenth | early_halt | 12:00 | cme | cme | cme svc ZN 2025-06-18..025-06-20& (Wayback 20241220155340) | cme svc ZN 2025-06-18..025-06-20& | True | pending Task 7 (research-window bars) |
| 2025-07-04 | Independence Day | early_halt | 12:00 | cme | cme | cme svc ZN 2025-07-03..025-07-05& (Wayback 20241220155340) | cme svc ZN 2025-07-03..025-07-05& | True | pending Task 7 (research-window bars) |
| 2025-09-01 | Labor Day | early_halt | 12:00 | cme | cme | cme svc ZN 2025-08-31..025-09-02& (Wayback 20241220155340) | cme svc ZN 2025-08-31..025-09-02& | True | pending Task 7 (research-window bars) |
| 2025-11-27 | Thanksgiving Day | early_halt | 12:00 | cme | cme | cme svc ZN 2025-11-26..025-11-28& (Wayback 20241220155340) | cme svc ZN 2025-11-26..025-11-28& | True | pending Task 7 (research-window bars) |
| 2025-11-28 | Day after Thanksgiving | early_halt | 12:15 | cme | cme | cme svc ZN 2025-11-26..025-11-28& (Wayback 20241220155340) | cme svc ZN 2025-11-26..025-11-28& | True | pending Task 7 (research-window bars) |
| 2025-12-24 | Christmas Eve | early_halt | 12:15 | cme | cme | cme svc ZN 2025-12-24..025-12-26& (Wayback 20260129012143) | cme svc ZN 2025-12-24..025-12-26& | True | pending Task 7 (research-window bars) |
| 2025-12-25 | Christmas Day | full_closure | - | cme | n/a | cme svc ZN 2025-12-24..025-12-26& (Wayback 20260129012143) | - | True | pending Task 7 (research-window bars) |
| 2026-01-01 | New Year's Day | full_closure | - | cme | n/a | cme svc ZN 2025-12-31..026-01-02& (Wayback 20260129012143) | - | True | pending Task 7 (research-window bars) |
| 2026-01-19 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | cme | cme svc ZN 2026-01-18..026-01-20& (Wayback 20260129012143) | cme svc ZN 2026-01-18..026-01-20& | True | pending Task 7 (research-window bars) |
| 2026-02-16 | Presidents Day | early_halt | 12:00 | cme | cme | cme svc ZN 2026-02-15..026-02-17& (Wayback 20260129012143) | cme svc ZN 2026-02-15..026-02-17& | True | pending Task 7 (research-window bars) |
| 2026-04-03 | Good Friday (abbreviated, jobs report) | early_halt | 10:15 | cme | cme | cme svc ZN 2026-04-01..026-04-03& (Wayback 20260129012143) | cme svc ZN 2026-04-01..026-04-03& | True | pending Task 7 (research-window bars) |
| 2026-05-25 | Memorial Day | early_halt | 12:00 | cme | cme | cme svc ZN 2026-05-24..026-05-26& (Wayback 20260129012143) | cme svc ZN 2026-05-24..026-05-26& | True | pending Task 7 (research-window bars) |
| 2026-06-19 | Juneteenth | early_halt | 12:00 | cme | cme | cme svc ZN 2026-06-17..026-06-19& (Wayback 20260129012143) | cme svc ZN 2026-06-17..026-06-19& | True | pending Task 7 (research-window bars) |

### Per-entry sources (URL, capture, sha256, verbatim quote, notes)

**2019-05-27 Memorial Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip [member globex-trading-schedules/2019-memorial-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
  - sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05`; verbatim: True
  - quote: "Updated 4/29/2019|CME Group Globex Memorial Day Holiday Schedule: May 24, 2019 - May 28, 2019 ... Calendar Date|Friday, May 24||Sunday, May 26|||||Monday, May 27|||||||Tuesday, May 28 ... Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip [member globex-trading-schedules/2019-memorial-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
  - sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, May 24] Regular Fri. Close 16:00 (trade date Friday, May 24); [Sunday, May 26] Pre-opening** 16:00 (trade date Tuesday, May 28); [Sunday, May 26] Open 17:00 (trade date Tuesday, May 28); [Monday, May 27] Halt 12:00 (trade date Tuesday, May 28); [Monday, May 27] Pre-opening ** 12:00 (trade date Tuesday, May 28); [Monday, May 27] Open 17:00 (trade date Tuesday, May 28)

**2019-07-04 Independence Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip [member globex-trading-schedules/2019-independence-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
  - sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05`; verbatim: True
  - quote: "Updated 6/6/2019|CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019 ... Calendar Date|Wednesday, July 3||||||||Thursday, July 4||||||||Friday, July 5 ... Interest Rate Products|04:00:00 PM|||04:45:00 PM|05:00:00 PM||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip [member globex-trading-schedules/2019-independence-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
  - sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM|||04:45:00 PM|05:00:00 PM||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Wednesday, July 3] Regular Close 16:00 (trade date Wednesday, July 3); [Wednesday, July 3] Pre-opening** 16:45 (trade date Friday, July 5); [Wednesday, July 3] Open 17:00 (trade date Friday, July 5); [Thursday, July 4] Halt 12:00 (trade date Friday, July 5); [Thursday, July 4] Pre-opening** 12:00 (trade date Friday, July 5); [Thursday, July 4] Open 17:00 (trade date Friday, July 5)

**2019-09-02 Labor Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip [member globex-trading-schedules/2019-labor-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
  - sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05`; verbatim: True
  - quote: "Updated 8/14/2019|CME Group Globex Labor Day Holiday Schedule: August 30, 2019 - September 3, 2019 ... Calendar Date|Friday, August 30||Sunday, September 1|||||Monday, September 2|||||||Tuesday, September 3 ... Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip [member globex-trading-schedules/2019-labor-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
  - sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, August 30] Regular Fri. Close 16:00 (trade date Friday, August 30); [Sunday, September 1] Pre-opening** 16:00 (trade date Tuesday, September 3); [Sunday, September 1] Open 17:00 (trade date Tuesday, September 3); [Monday, September 2] Halt 12:00 (trade date Tuesday, September 3); [Monday, September 2] Pre-opening** 12:00 (trade date Tuesday, September 3); [Monday, September 2] Open 17:00 (trade date Tuesday, September 3)

**2019-11-28 Thanksgiving Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip [member globex-trading-schedules/2019-thanksgiving-schedule.xls]
  - fetched via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
  - sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05`; verbatim: True
  - quote: "Updated 10/07/2019|CME Group Globex Thanksgiving Holiday Schedule: November 27, 2019 - November 29, 2019 ... Calendar Date|Wednesday, November 27|||||||Thursday, November 28|||||||||Friday, November 29 ... Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip [member globex-trading-schedules/2019-thanksgiving-schedule.xls]
  - fetched via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
  - sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Wednesday, November 27] Regular Close 16:00 (trade date Wednesday, November 27); [Wednesday, November 27] Pre-opening** 16:45 (trade date Friday, November 29); [Wednesday, November 27] Open 17:00 (trade date Friday, November 29); [Thursday, November 28] Halt 12:00 (trade date Friday, November 29); [Thursday, November 28] Pre-opening** 12:00 (trade date Friday, November 29); [Thursday, November 28] Open 17:00 (trade date Friday, November 29); [Friday, November 29] Close 12:15 (trade date Friday, November 29)

**2019-11-29 Day after Thanksgiving** (early_halt, halt 12:15, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip [member globex-trading-schedules/2019-thanksgiving-schedule.xls]
  - fetched via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
  - sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05`; verbatim: True
  - quote: "Updated 10/07/2019|CME Group Globex Thanksgiving Holiday Schedule: November 27, 2019 - November 29, 2019 ... Calendar Date|Wednesday, November 27|||||||Thursday, November 28|||||||||Friday, November 29 ... Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip [member globex-trading-schedules/2019-thanksgiving-schedule.xls]
  - fetched via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
  - sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- notes: xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Wednesday, November 27] Regular Close 16:00 (trade date Wednesday, November 27); [Wednesday, November 27] Pre-opening** 16:45 (trade date Friday, November 29); [Wednesday, November 27] Open 17:00 (trade date Friday, November 29); [Thursday, November 28] Halt 12:00 (trade date Friday, November 29); [Thursday, November 28] Pre-opening** 12:00 (trade date Friday, November 29); [Thursday, November 28] Open 17:00 (trade date Friday, November 29); [Friday, November 29] Close 12:15 (trade date Friday, November 29)

**2019-12-24 Christmas Eve** (early_halt, halt 12:15, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip [member globex-trading-schedules/2019-christmas-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
  - sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05`; verbatim: True
  - quote: "Updated 10/01/2019|CME Group Globex Christmas Holiday Schedule: December 24, 2019 - December 26, 2019 ... Calendar Date|Tuesday, December 24|Wednesday, December 25|Wednesday, December 25||||||Thursday, December 26 ... Interest Rate Products|12:15:00 PM|Globex Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip [member globex-trading-schedules/2019-christmas-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
  - sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05`; verbatim: True
  - quote: "Interest Rate Products|12:15:00 PM|Globex Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
- notes: xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Tuesday, December 24] Close 12:15 (trade date Tuesday, December 24); [Wednesday, December 25] - Globex Closed (trade date Globex Closed); [Wednesday, December 25] Pre-opening** 16:00 (trade date Thursday, December 26); [Wednesday, December 25] Open 17:00 (trade date Thursday, December 26); [Thursday, December 26] Close 16:00 (trade date Thursday, December 26)

**2019-12-25 Christmas Day** (full_closure, halt -, status cme, time n/a; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip [member globex-trading-schedules/2019-christmas-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
  - sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05`; verbatim: True
  - quote: "Updated 10/01/2019|CME Group Globex Christmas Holiday Schedule: December 24, 2019 - December 26, 2019 ... Calendar Date|Tuesday, December 24|Wednesday, December 25|Wednesday, December 25||||||Thursday, December 26 ... Interest Rate Products|12:15:00 PM|Globex Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
- time: none (time n/a)
- notes: xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Tuesday, December 24] Close 12:15 (trade date Tuesday, December 24); [Wednesday, December 25] - Globex Closed (trade date Globex Closed); [Wednesday, December 25] Pre-opening** 16:00 (trade date Thursday, December 26); [Wednesday, December 25] Open 17:00 (trade date Thursday, December 26); [Thursday, December 26] Close 16:00 (trade date Thursday, December 26)

**2020-01-01 New Year's Day** (full_closure, halt -, status cme, time n/a; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip [member globex-trading-schedules/2019-2020-new-years-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip
  - sha256: `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05`; verbatim: True
  - quote: "Updated 10/01/2019|CME Group Globex New Years Holiday Schedule: December 31, 2019 - January 2, 2020 ... Calendar Date|Tuesday, December 31|Wednesday, January 1|Wednesday, January 1||||||Thursday, Jan 2 ... Interest Rate Products|04:00:00 PM|Globex Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
- time: none (time n/a)
- notes: xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Tuesday, December 31] Close 16:00 (trade date Tuesday, December 31); [Wednesday, January 1] - Globex Closed (trade date -); [Wednesday, January 1] Pre-opening** 16:00 (trade date Thursday,  January 2); [Wednesday, January 1] Open 17:00 (trade date Thursday,  January 2); [Thursday, Jan 2] Close 16:00 (trade date Thursday,  January 2)

**2020-01-20 Martin Luther King Jr. Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-mlk-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Updated 4/6/2020|CME Group Globex Martin Luther King Day Holiday Schedule: January 17, 2020 - January 21, 2020 ... Calendar Date|Friday, January 17||Sunday, January 19|||||Monday, January 20|||||||Tuesday, January 21 ... Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-mlk-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, January 17] Regular Fri. Close 16:00 (trade date Friday, January 17); [Sunday, January 19] Pre-opening** 16:00 (trade date Tuesday, January 21); [Sunday, January 19] Open 17:00 (trade date Tuesday, January 21); [Monday, January 20] Halt 12:00 (trade date Tuesday, January 21); [Monday, January 20] Pre-opening 12:00 (trade date Tuesday, January 21); [Monday, January 20] Open 17:00 (trade date Tuesday, January 21)

**2020-02-17 Presidents Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-presidents-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Updated 4/6/2020|CME Group Globex Presidents Day Holiday Schedule: February 14, 2020 - February 18, 2020 ... Calendar Date|Friday, February 14||Sunday, February 16|||||Monday, February 17|||||||Tuesday, February 18 ... Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-presidents-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, February 14] Regular Fri. Close 16:00 (trade date Friday, February 14); [Sunday, February 16] Pre-opening** 16:00 (trade date Tuesday, February 18); [Sunday, February 16] Open 17:00 (trade date Tuesday, February 18); [Monday, February 17] Halt 12:00 (trade date Tuesday, February 18); [Monday, February 17] Pre-opening 12:00 (trade date Tuesday, February 18); [Monday, February 17] Open 17:00 (trade date Tuesday, February 18)

**2020-04-10 Good Friday** (full_closure, halt -, status cme, time n/a; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-good-friday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Updated 4/6/2020|CME Group Globex Good Friday Holiday Schedule: April 9, 2020 to April 13, 2020 ... Calendar Date|Thursday, April 9||||||Friday, April 10|||Sunday, April 12|||||Monday, April 13 ... Interest Rate Products|04:00:00 PM||||||Globex Closed|||04:00:00 PM|05:00:00 PM"
- time: none (time n/a)
- notes: xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Thursday, April 9] Regular Close 16:00 (trade date Thursday, April 9); [Friday, April 10] Pre-opening** Globex Closed (trade date Friday, April 10); [Sunday, April 12] Pre-opening** 16:00 (trade date Monday, April 13); [Sunday, April 12] Open 17:00 (trade date Monday, April 13)

**2020-05-25 Memorial Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-memorial-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Updated 4/21/2020|CME Group Globex Memorial Day Holiday Schedule: May 22, 2020 - May 26, 2020 ... Calendar Date|Friday, May 22||Sunday, May 24|||||Monday, May 25|||||||Tuesday, May 26 ... Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-memorial-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, May 22] Regular Fri. Close 16:00 (trade date Friday, May 22); [Sunday, May 24] Pre-opening** 16:00 (trade date Tuesday, May 26); [Sunday, May 24] Open 17:00 (trade date Tuesday, May 26); [Monday, May 25] Halt 12:00 (trade date Tuesday, May 26); [Monday, May 25] Pre-opening ** 12:00 (trade date Tuesday, May 26); [Monday, May 25] Open 17:00 (trade date Tuesday, May 26)

**2020-07-03 Independence Day (observed)** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-independence-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Updated 6/26/2020|CME Group Globex Independence Day Holiday Schedule: July 2, 2020 to July 6, 2020 ... Calendar Date|Thursday, July 2||||||||Friday, July 3|||Sunday, July 5|||||Monday, July 6 ... Interest Rate Products|04:00:00 PM|||04:45:00 PM|05:00:00 PM||||||12:00:00 PM|04:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-independence-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM|||04:45:00 PM|05:00:00 PM||||||12:00:00 PM|04:00:00 PM|05:00:00 PM"
- notes: CME labels the Friday 12:00 event 'Close'; the next open is Sunday July 5 17:00. CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Thursday, July 2] Regular Close 16:00 (trade date Thursday, July 2); [Thursday, July 2] Pre-opening** 16:45 (trade date Monday, July 6); [Thursday, July 2] Open 17:00 (trade date Monday, July 6); [Friday, July 3] Close 12:00 (trade date Monday, July 6); [Sunday, July 5] Pre-opening** 16:00 (trade date Monday, July 6); [Sunday, July 5] Open 17:00 (trade date Monday, July 6)

**2020-09-07 Labor Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-labor-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Updated 8/28/2020|CME Group Globex Labor Day Holiday Schedule: September 4, 2020 - September 8, 2020 ... Calendar Date|Friday, September 4||Sunday, September 6|||||Monday, September 7|||||||Tuesday, September 8 ... Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-labor-day-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, September 4] Regular Fri. Close 16:00 (trade date Friday, September 4); [Sunday, September 6] Pre-opening** 16:00 (trade date Tuesday, September 8); [Sunday, September 6] Open 17:00 (trade date Tuesday, September 8); [Monday, September 7] Halt 12:00 (trade date Tuesday, September 8); [Monday, September 7] Pre-opening** 12:00 (trade date Tuesday, September 8); [Monday, September 7] Open 17:00 (trade date Tuesday, September 8)

**2020-11-26 Thanksgiving Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-thanksgiving-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Updated 10/13/2020|CME Group Globex Thanksgiving Holiday Schedule: November 25, 2020 - November 27, 2020 ... Calendar Date|Wednesday, November 25|||||||Thursday, November 26|||||||||Friday, November 27 ... Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-thanksgiving-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Wednesday, November 25] Regular Close 16:00 (trade date Wednesday, November 25); [Wednesday, November 25] Pre-opening** 16:45 (trade date Friday, November 27); [Wednesday, November 25] Open 17:00 (trade date Friday, November 27); [Thursday, November 26] Halt 12:00 (trade date Friday, November 27); [Thursday, November 26] Pre-opening** 12:00 (trade date Friday, November 27); [Thursday, November 26] Open 17:00 (trade date Friday, November 27); [Friday, November 27] Close 12:15 (trade date Friday, November 27)

**2020-11-27 Day after Thanksgiving** (early_halt, halt 12:15, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-thanksgiving-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Updated 10/13/2020|CME Group Globex Thanksgiving Holiday Schedule: November 25, 2020 - November 27, 2020 ... Calendar Date|Wednesday, November 25|||||||Thursday, November 26|||||||||Friday, November 27 ... Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-thanksgiving-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- notes: xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Wednesday, November 25] Regular Close 16:00 (trade date Wednesday, November 25); [Wednesday, November 25] Pre-opening** 16:45 (trade date Friday, November 27); [Wednesday, November 25] Open 17:00 (trade date Friday, November 27); [Thursday, November 26] Halt 12:00 (trade date Friday, November 27); [Thursday, November 26] Pre-opening** 12:00 (trade date Friday, November 27); [Thursday, November 26] Open 17:00 (trade date Friday, November 27); [Friday, November 27] Close 12:15 (trade date Friday, November 27)

**2020-12-24 Christmas Eve** (early_halt, halt 12:15, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-christmas-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Updated 11/17/2020|CME Group Globex Christmas Holiday Schedule: December 24, 2020 - December 28, 2020 ... Calendar Date|Thursday, December 24|Friday, December 25|Sunday, December 27||||||Monday, December 28 ... Interest Rate Products|12:15:00 PM|Globex Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-christmas-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Interest Rate Products|12:15:00 PM|Globex Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
- notes: xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Thursday, December 24] Close 12:15 (trade date Thursday, December 24); [Friday, December 25] - Globex Closed (trade date Globex Closed); [Sunday, December 27] Pre-opening** 16:00 (trade date Monday, December 28); [Sunday, December 27] Open 17:00 (trade date Monday, December 28); [Monday, December 28] Close 16:00 (trade date Monday, December 28)

**2020-12-25 Christmas Day** (full_closure, halt -, status cme, time n/a; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2020-christmas-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Updated 11/17/2020|CME Group Globex Christmas Holiday Schedule: December 24, 2020 - December 28, 2020 ... Calendar Date|Thursday, December 24|Friday, December 25|Sunday, December 27||||||Monday, December 28 ... Interest Rate Products|12:15:00 PM|Globex Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
- time: none (time n/a)
- notes: xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Thursday, December 24] Close 12:15 (trade date Thursday, December 24); [Friday, December 25] - Globex Closed (trade date Globex Closed); [Sunday, December 27] Pre-opening** 16:00 (trade date Monday, December 28); [Sunday, December 27] Open 17:00 (trade date Monday, December 28); [Monday, December 28] Close 16:00 (trade date Monday, December 28)

**2021-01-01 New Year's Day** (full_closure, halt -, status cme, time n/a; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip [member 2021-new-years-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260730000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip
  - sha256: `5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59`; verbatim: True
  - quote: "Updated 12/09/2020|CME Group Globex New Years Holiday Schedule: December 31, 2020 - January 4, 2021 ... Calendar Date|Thursday, December 31|Friday, January 1|Sunday, January 3||||||Monday, January 4 ... Interest Rate Products|04:00:00 PM|Globex Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
- time: none (time n/a)
- notes: xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Thursday, December 31] Close 16:00 (trade date Thursday, December 31); [Friday, January 1] - Globex Closed (trade date -); [Sunday, January 3] Pre-opening** 16:00 (trade date Monday,  January 4); [Sunday, January 3] Open 17:00 (trade date Monday,  January 4); [Monday, January 4] Close 16:00 (trade date Monday,  January 4)

**2021-01-18 Martin Luther King Jr. Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-mlk-day-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Updated 12/23/2020|CME Group Globex Martin Luther King Day Holiday Schedule: January 15, 2021 - January 19, 2021 ... Calendar Date|Friday, January 15||Sunday, January 17|||||Monday, January 18|||||||Tuesday, January 19 ... Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-mlk-day-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, January 15] Regular Fri. Close 16:00 (trade date Friday, January 15); [Sunday, January 17] Pre-opening** 16:00 (trade date Tuesday, January 19); [Sunday, January 17] Open 17:00 (trade date Tuesday, January 19); [Monday, January 18] Halt 12:00 (trade date Tuesday, January 19); [Monday, January 18] Pre-opening 12:00 (trade date Tuesday, January 19); [Monday, January 18] Open 17:00 (trade date Tuesday, January 19)

**2021-02-15 Presidents Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-presidents-day-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Updated 2/11/2021|CME Group Globex Presidents Day Holiday Schedule: February 12, 2021 - February 16, 2021 ... Calendar Date|Friday, February 12||Sunday, February 14|||||Monday, February 15|||||||Tuesday, February 16 ... Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-presidents-day-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, February 12] Regular Fri. Close 16:00 (trade date Friday, February 12); [Sunday, February 14] Pre-opening** 16:00 (trade date Tuesday, February 16); [Sunday, February 14] Open 17:00 (trade date Tuesday, February 16); [Monday, February 15] Halt 12:00 (trade date Tuesday, February 16); [Monday, February 15] Pre-opening 12:00 (trade date Tuesday, February 16); [Monday, February 15] Open 17:00 (trade date Tuesday, February 16)

**2021-04-02 Good Friday (abbreviated, jobs report)** (early_halt, halt 10:15, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-good-friday-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Updated 3/31/2021|CME Group Globex Good Friday Holiday Schedule: April 1, 2021 to April 5, 2021 ... Calendar Date|Thursday, April 1||||||Friday, April 2|||Sunday, April 4|||||Monday, April 5 ... Interest Rate Products|04:00:00 PM|||04:45:00 PM|05:00:00 PM||||10:15:00 AM|04:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-good-friday-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM|||04:45:00 PM|05:00:00 PM||||10:15:00 AM|04:00:00 PM|05:00:00 PM"
- notes: Globex reopened Thursday April 1 17:00 for trade date Friday April 2 and closed at 10:15 CT; next open Sunday April 4 17:00. xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Thursday, April 1] Regular Close 16:00 (trade date Thursday, April 1); [Thursday, April 1] Pre-opening** 16:45 (trade date Friday, April 2); [Thursday, April 1] Open 17:00 (trade date Friday, April 2); [Friday, April 2] Close 10:15 (trade date Friday, April 2); [Sunday, April 4] Pre-opening** 16:00 (trade date Monday, April 5); [Sunday, April 4] Open 17:00 (trade date Monday, April 5)

**2021-05-31 Memorial Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-memorial-day-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Updated 5/25/2021|CME Group Globex Memorial Day Holiday Schedule: May 28, 2021 - Jun 1, 2021 ... Calendar Date|Friday, May 28||Sunday, May 30|||||Monday, May 31|||||||Tuesday, Jun 1 ... Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-memorial-day-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, May 28] Regular Fri. Close 16:00 (trade date Friday, May 28); [Sunday, May 30] Pre-opening** 16:00 (trade date Tuesday, Jun 1); [Sunday, May 30] Open 17:00 (trade date Tuesday, Jun 1); [Monday, May 31] Halt 12:00 (trade date Tuesday, Jun 1); [Monday, May 31] Pre-opening ** 12:00 (trade date Tuesday, Jun 1); [Monday, May 31] Open 17:00 (trade date Tuesday, Jun 1)

**2021-07-05 Independence Day (observed)** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-independence-day-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Updated 7/1/2021|CME Group Globex Independence Day Holiday Schedule: July 2, 2021 to July 6, 2021 ... Calendar Date|Friday, July 2||Sunday, July 4|||||Monday, July 5||||||Tuesday, July 6 ... Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-independence-day-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, July 2] Regular Close 16:00 (trade date Friday, July 2); [Sunday, July 4] Pre-opening** 16:00 (trade date Tuesday, July 6); [Sunday, July 4] Open 17:00 (trade date Tuesday, July 6); [Monday, July 5] Halt 12:00 (trade date Tuesday, July 6); [Monday, July 5] Pre-opening** 12:00 (trade date Tuesday, July 6); [Monday, July 5] Open 17:00 (trade date Tuesday, July 6)

**2021-09-06 Labor Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-labor-day-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Updated 8/12/2021|CME Group Globex Labor Day Holiday Schedule: September 3, 2021 - September 7, 2021 ... Calendar Date|Friday, September 3||Sunday, September 5|||||Monday, September 6|||||||Tuesday, September 7 ... Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-labor-day-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, September 3] Regular Fri. Close 16:00 (trade date Friday, September 3); [Sunday, September 5] Pre-opening** 16:00 (trade date Tuesday, September 7); [Sunday, September 5] Open 17:00 (trade date Tuesday, September 7); [Monday, September 6] Halt 12:00 (trade date Tuesday, September 7); [Monday, September 6] Pre-opening** 12:00 (trade date Tuesday, September 7); [Monday, September 6] Open 17:00 (trade date Tuesday, September 7)

**2021-11-25 Thanksgiving Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-thanksgiving-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Updated 11/23/2021|CME Group Globex Thanksgiving Holiday Schedule: November 24, 2021 - November 26, 2021 ... Calendar Date|Wednesday, November 24|||||||Thursday, November 25|||||||||Friday, November 26 ... Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-thanksgiving-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Wednesday, November 24] Regular Close 16:00 (trade date Wednesday, November 24); [Wednesday, November 24] Pre-opening** 16:45 (trade date Friday, November 26); [Wednesday, November 24] Open 17:00 (trade date Friday, November 26); [Thursday, November 25] Halt 12:00 (trade date Friday, November 26); [Thursday, November 25] Pre-opening** 12:00 (trade date Friday, November 26); [Thursday, November 25] Open 17:00 (trade date Friday, November 26); [Friday, November 26] Close 12:15 (trade date Friday, November 26)

**2021-11-26 Day after Thanksgiving** (early_halt, halt 12:15, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-thanksgiving-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Updated 11/23/2021|CME Group Globex Thanksgiving Holiday Schedule: November 24, 2021 - November 26, 2021 ... Calendar Date|Wednesday, November 24|||||||Thursday, November 25|||||||||Friday, November 26 ... Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-thanksgiving-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- notes: xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Wednesday, November 24] Regular Close 16:00 (trade date Wednesday, November 24); [Wednesday, November 24] Pre-opening** 16:45 (trade date Friday, November 26); [Wednesday, November 24] Open 17:00 (trade date Friday, November 26); [Thursday, November 25] Halt 12:00 (trade date Friday, November 26); [Thursday, November 25] Pre-opening** 12:00 (trade date Friday, November 26); [Thursday, November 25] Open 17:00 (trade date Friday, November 26); [Friday, November 26] Close 12:15 (trade date Friday, November 26)

**2021-12-24 Christmas Day (observed)** (full_closure, halt -, status cme, time n/a; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip [member 2021-christmas-holiday-schedule.xls]
  - fetched via: https://web.archive.org/web/20260830000000id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip
  - sha256: `0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59`; verbatim: True
  - quote: "Updated 12/01/2021|CME Group Globex Christmas Holiday Schedule: December 24, 2021 - December 27, 2021 ... Calendar Date|Thursday, December 23|||||||||||||Friday, December 24||||||||||Sunday, December 26||||||Monday, Dec 27 ... Interest Rate Products|04:00:00 PM|||||||||||||Globex Closed||||||||||04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
- time: none (time n/a)
- notes: xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Thursday, December 23] Close 16:00 (trade date Thursday, December 23); [Friday, December 24] - Globex Closed (trade date Monday, December 27); [Sunday, December 26] Pre-opening** 16:00 (trade date Monday, December 27); [Sunday, December 26] Open 17:00 (trade date Monday, December 27); [Monday, Dec 27] Close 16:00 (trade date Monday, December 27)

**2022-01-17 Martin Luther King Jr. Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220117212230id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule.xls
  - sha256: `896944fa701062e2e1ee305f8adb696ba8ab03655a96874c7885f2328177626e`; verbatim: True
  - quote: "Updated 12/14/2021|CME Group Globex Martin Luther King Day Holiday Schedule: January 14, 2022 - January 18, 2022 ... Calendar Date|Friday, January 14|||||Sunday, January 16|||||Monday, January 17|||||||||Tuesday, January 18 ... Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220117212230id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule.xls
  - sha256: `896944fa701062e2e1ee305f8adb696ba8ab03655a96874c7885f2328177626e`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, January 14] Regular Fri. Close 16:00 (trade date Friday, January 14); [Sunday, January 16] Pre-opening** 16:00 (trade date Tuesday, January 18); [Sunday, January 16] Open 17:00 (trade date Tuesday, January 18); [Monday, January 17] Halt 12:00 (trade date Tuesday, January 18); [Monday, January 17] Pre-opening 12:00 (trade date Tuesday, January 18); [Monday, January 17] Open 17:00 (trade date Tuesday, January 18)

**2022-02-21 Presidents Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220704073810id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule.xls
  - sha256: `07932975d04ccabad0fb53f33f946f1a6fd8a696bafdb21f95f030ede9a84516`; verbatim: True
  - quote: "Updated 1/24/2022|CME Group Globex Presidents Day Holiday Schedule: February 18, 2022 - February 22, 2022 ... Calendar Date|Friday, February 18|||||Sunday, February 20|||||Monday, February 21||||||||||||Tuesday, February 22 ... Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220704073810id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule.xls
  - sha256: `07932975d04ccabad0fb53f33f946f1a6fd8a696bafdb21f95f030ede9a84516`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, February 18] Regular Fri. Close 16:00 (trade date Friday, February 18); [Sunday, February 20] Pre-opening** 16:00 (trade date Tuesday, February 22); [Sunday, February 20] Open 17:00 (trade date Tuesday, February 22); [Monday, February 21] Halt 12:00 (trade date Tuesday, February 22); [Monday, February 21] Pre-opening 12:00 (trade date Tuesday, February 22); [Monday, February 21] Open 17:00 (trade date Tuesday, February 22)

**2022-04-15 Good Friday** (full_closure, halt -, status cme, time n/a; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220704065501id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule.xls
  - sha256: `a82936ab14d1b1f7041583123289c4de401c66ace4eea7e90fa9f60c1a3f3b7e`; verbatim: True
  - quote: "Updated 3/17/2022|CME Group Globex Good Friday Holiday Schedule: April 14, 2022 to April 18, 2022 ... Calendar Date|Thursday, April 14|||||||||Friday, April 15|||Sunday, April 17|||||Monday, April 18 ... Interest Rate Products|04:00:00 PM|||||||||Globex Closed|||04:00:00 PM|05:00:00 PM"
- time: none (time n/a)
- notes: xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Thursday, April 14] Regular Close 16:00 (trade date Thursday, April 14); [Friday, April 15] Pre-opening** Globex Closed (trade date Monday, April 18); [Sunday, April 17] Pre-opening** 16:00 (trade date Monday, April 18); [Sunday, April 17] Open 17:00 (trade date Monday, April 18)

**2022-05-30 Memorial Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220704065438id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule.xls
  - sha256: `0d1b1f89a315cae22a5857a7027a514e3086c1cccfee42fddddff3caba0c2230`; verbatim: True
  - quote: "Updated 5/18/2022|CME Group Globex Memorial Day Holiday Schedule: May 27, 2022 - May 31, 2022 ... Calendar Date|Friday, May 27|||||Sunday, May 29|||||Monday, May 30||||||||||Tuesday, May 31 ... Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220704065438id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule.xls
  - sha256: `0d1b1f89a315cae22a5857a7027a514e3086c1cccfee42fddddff3caba0c2230`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, May 27] Regular Fri. Close 16:00 (trade date Friday, May 27); [Sunday, May 29] Pre-opening** 16:00 (trade date Tuesday, May 31); [Sunday, May 29] Open 17:00 (trade date Tuesday, May 31); [Monday, May 30] Halt 12:00 (trade date Tuesday, May 31); [Monday, May 30] Pre-opening ** 12:00 (trade date Tuesday, May 31); [Monday, May 30] Open 17:00 (trade date Tuesday, May 31)

**2022-06-20 Juneteenth (observed)** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220620200210id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls
  - sha256: `bc9f2caf26a73a13029f177fcc6468bdc8662899ff935f44329ee1a95c8b667b`; verbatim: True
  - quote: "Updated 5/18/2022|CME Group Globex Juneteenth Holiday Schedule: June 17, 2022 - Jun 21, 2022 ... Calendar Date|Friday, June 17|||||Sunday, June 19|||||Monday, June 20||||||||||Tuesday, Jun 21 ... Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220620200210id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls
  - sha256: `bc9f2caf26a73a13029f177fcc6468bdc8662899ff935f44329ee1a95c8b667b`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, June 17] Regular Fri. Close 16:00 (trade date Friday, June 17); [Sunday, June 19] Pre-opening** 16:00 (trade date Tuesday, Jun 21); [Sunday, June 19] Open 17:00 (trade date Tuesday, Jun 21); [Monday, June 20] Halt 12:00 (trade date Tuesday, Jun 21); [Monday, June 20] Pre-opening ** 12:00 (trade date Tuesday, Jun 21); [Monday, June 20] Open 17:00 (trade date Tuesday, Jun 21)

**2022-07-04 Independence Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220704065450id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls
  - sha256: `1ea0459d8aa0fd7ec5147614855f6d0d43607efefdc3aa9c6b1e18ddbfd54fde`; verbatim: True
  - quote: "Updated 6/29/2022|CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022 ... Calendar Date|Friday, July 1|||||Sunday, July 3|||||Monday, July 4|||||||||||Tuesday, July 5 ... Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220704065450id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls
  - sha256: `1ea0459d8aa0fd7ec5147614855f6d0d43607efefdc3aa9c6b1e18ddbfd54fde`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, July 1] Regular Close 16:00 (trade date Friday, July 1); [Sunday, July 3] Pre-opening** 16:00 (trade date Tuesday, July 5); [Sunday, July 3] Open 17:00 (trade date Tuesday, July 5); [Monday, July 4] Halt 12:00 (trade date Tuesday, July 5); [Monday, July 4] Pre-opening** 12:00 (trade date Tuesday, July 5); [Monday, July 4] Open 17:00 (trade date Tuesday, July 5)

**2022-09-05 Labor Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220704065441id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule.xls
  - sha256: `28d533f25d1af74af043e411635f1933fd4ff6359c80c049f87f019d2f1d57d0`; verbatim: True
  - quote: "Updated 6/29/2022|CME Group Globex Labor Day Holiday Schedule: September 2, 2022 - September 6, 2022 ... Calendar Date|Friday, September 2|||||Sunday, September 4|||||Monday, September 5||||||||||Tuesday, Sept. 6 ... Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220704065441id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule.xls
  - sha256: `28d533f25d1af74af043e411635f1933fd4ff6359c80c049f87f019d2f1d57d0`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). Schedule sheet 'Updated 6/29/2022', Wayback capture 2022-07-04, months before the holiday; no later capture was retrieved, so a later CME revision cannot be excluded. xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, September 2] Regular Fri. Close 16:00 (trade date Friday, September 2); [Sunday, September 4] Pre-opening** 16:00 (trade date Tuesday, September 6); [Sunday, September 4] Open 17:00 (trade date Tuesday, September 6); [Monday, September 5] Halt 12:00 (trade date Tuesday, September 6); [Monday, September 5] Pre-opening** 12:00 (trade date Tuesday, September 6); [Monday, September 5] Open 17:00 (trade date Tuesday, September 6)

**2022-11-24 Thanksgiving Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220704065423id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls
  - sha256: `767da53e71854a3b293b613d256642f8155cd04997fa0825a35825440448126c`; verbatim: True
  - quote: "Updated 6/29/2022|CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, 2022 ... Calendar Date|Wednesday, November 23||||||||||Thursday, November 24||||||||||||Friday, November 25 ... Interest Rate Products|04:00:00 PM|||||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220704065423id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls
  - sha256: `767da53e71854a3b293b613d256642f8155cd04997fa0825a35825440448126c`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM|||||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention). Schedule sheet 'Updated 6/29/2022', Wayback capture 2022-07-04, months before the holiday; no later capture was retrieved, so a later CME revision cannot be excluded. xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Wednesday, November 23] Regular Close 16:00 (trade date Wednesday, November 23); [Wednesday, November 23] Pre-opening** 16:45 (trade date Friday, November 25); [Wednesday, November 23] Open 17:00 (trade date Friday, November 25); [Thursday, November 24] Halt 12:00 (trade date Friday, November 25); [Thursday, November 24] Pre-opening** 12:00 (trade date Friday, November 25); [Thursday, November 24] Open 17:00 (trade date Friday, November 25); [Friday, November 25] Close 12:15 (trade date Friday, November 25)

**2022-11-25 Day after Thanksgiving** (early_halt, halt 12:15, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220704065423id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls
  - sha256: `767da53e71854a3b293b613d256642f8155cd04997fa0825a35825440448126c`; verbatim: True
  - quote: "Updated 6/29/2022|CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, 2022 ... Calendar Date|Wednesday, November 23||||||||||Thursday, November 24||||||||||||Friday, November 25 ... Interest Rate Products|04:00:00 PM|||||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220704065423id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls
  - sha256: `767da53e71854a3b293b613d256642f8155cd04997fa0825a35825440448126c`; verbatim: True
  - quote: "Interest Rate Products|04:00:00 PM|||||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
- notes: Schedule sheet 'Updated 6/29/2022', Wayback capture 2022-07-04, months before the holiday; no later capture was retrieved, so a later CME revision cannot be excluded. xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Wednesday, November 23] Regular Close 16:00 (trade date Wednesday, November 23); [Wednesday, November 23] Pre-opening** 16:45 (trade date Friday, November 25); [Wednesday, November 23] Open 17:00 (trade date Friday, November 25); [Thursday, November 24] Halt 12:00 (trade date Friday, November 25); [Thursday, November 24] Pre-opening** 12:00 (trade date Friday, November 25); [Thursday, November 24] Open 17:00 (trade date Friday, November 25); [Friday, November 25] Close 12:15 (trade date Friday, November 25)

**2022-12-26 Christmas Day (observed)** (full_closure, halt -, status cme, time n/a; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220704065430id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls
  - sha256: `2dd1d531514989845dcb6ce6d767db5dd3f956ac6777ab1cfe36d6843f3762e7`; verbatim: True
  - quote: "Updated 6/29/2022|CME Group Globex Christmas Holiday Schedule: December 23, 2022 - December 27, 2022 ... Calendar Date|Friday, December 23||||||||Monday, December 26||||||||||||||||Tuesday, December 27 ... Interest Rate Products|04:00:00 PM||||||||Globex Closed||||||||||04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
- time: none (time n/a)
- notes: Schedule sheet 'Updated 6/29/2022', Wayback capture 2022-07-04, months before the holiday; no later capture was retrieved, so a later CME revision cannot be excluded. xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, December 23] Close 16:00 (trade date Friday, December 23); [Monday, December 26] - Globex Closed (trade date Tuesday, December 27); [Monday, December 26] Pre-opening** 16:00 (trade date Tuesday, December 27); [Monday, December 26] Open 17:00 (trade date Tuesday, December 27); [Tuesday, December 27] Close 16:00 (trade date Tuesday, December 27)

**2023-01-02 New Year's Day (observed)** (full_closure, halt -, status cme, time n/a; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule.xls
  - fetched via: https://web.archive.org/web/20220704065501id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule.xls
  - sha256: `eefafd1066f406edbe6167ddf8ad13c0697b124a337c0893ce5a5da200c783d3`; verbatim: True
  - quote: "Updated 6/29/22|CME Group Globex New Year's Holiday Schedule: December 30, 2022 - January 3, 2023 ... Calendar Date|Friday, December 30||||Monday, January 2|Monday, January 2||||||Tuesday, January 3 ... Interest Rate Products|04:00:00 PM||||Globex Closed|04:00:00 PM|05:00:00 PM"
- time: none (time n/a)
- notes: Schedule sheet 'Updated 6/29/22', Wayback capture 2022-07-04, months before the holiday; no later capture was retrieved, so a later CME revision cannot be excluded. xlrd read of the 'Interest Rate Products' row (merged Calendar Date headers): [Friday, December 30] Close 16:00 (trade date Friday, December 30); [Monday, January 2] - Globex Closed (trade date Tuesday,  January 3); [Monday, January 2] Pre-opening** 16:00 (trade date Tuesday,  January 3); [Monday, January 2] Open 17:00 (trade date Tuesday,  January 3)

**2023-01-16 Martin Luther King Jr. Day** (early_halt, halt 12:00, status cme, time secondary; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2023.pdf
  - fetched via: https://web.archive.org/web/20230203073653id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2023.pdf
  - sha256: `051f2a2136e27daecf8ed717983787fc8aacd62b83418cbecca1a44937e9e4cb`; verbatim: True
  - quote: "Martin Luther King Holiday 1/16/2023 Settlement Times ... Monday, January 16, 2023 Holiday ... Note: Monday January 16, 2023 CME Group will not derive or disseminate settlement prices (other than the two LIBOR Settlements listed above) for CME, CBOT, NYMEX or COMEX"
- time: https://www.ampfutures.com/news/holiday-trading-schedule-martin-luther-king-day-2023
  - fetched via: https://www.ampfutures.com/news/holiday-trading-schedule-martin-luther-king-day-2023
  - sha256: `b8f1b2ddd823cc5c3669e32eb742537140e2abd6eb8a2a17853ac0dcbeaa2e70`; verbatim: True
  - quote: "Monday, January 16, 2023 - Early Market "HALT" - Noon CST (Chicago) > then reopens normal times."
- notes: Status: CME settlement notice (a holiday with no settlement); the halt-versus-closure distinction rests on AMP (secondary). Time secondary: no CME Globex-hours document for this 2023 date was retrieved (CME's 2023 summary PDF for it has only 404 captures, and the ZN service capture of 2024-07-08 returns empty event lists for 2023-01..07). AMP Futures' page quotes the CME Globex Control Center's generic 'Early Market HALT - Noon' line; its embedded CME schedule image (AMP-made table) shows the 'Interest Rate' row with HALT 12:00 CST and OPEN 17:00 CST (read visually, not script-checkable; see extra_evidence). Every CME-documented MLK and Presidents Day in 2019-2026 has the same 12:00 CT rates halt.

**2023-02-20 Presidents Day** (early_halt, halt 12:00, status cme, time secondary; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2023.pdf
  - fetched via: https://web.archive.org/web/20230203065411id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2023.pdf
  - sha256: `477fcee315e34a3a2556b2ffb3367a6047ca62c5ae909a0adb6a607548e2921c`; verbatim: True
  - quote: "Presidents’ Day Holiday 2/20/2023 Settlement Times ... Note: Monday February 20, 2023 CME Group will not derive or disseminate settlement prices for CME, CBOT, NYMEX or COMEX"
- time: https://www.ampfutures.com/news/holiday-trading-schedule-presidents-day-2023
  - fetched via: https://www.ampfutures.com/news/holiday-trading-schedule-presidents-day-2023
  - sha256: `3d4b417e42dd382e3c76b0db726998d7ff57cc8e351e899d919fba7728aafb37`; verbatim: True
  - quote: "Monday, February 20, 2023 - Early Market "HALT" - Noon CST (Chicago) > then reopens normal times."
- notes: Status: CME settlement notice (a holiday with no settlement); the halt-versus-closure distinction rests on AMP (secondary). Time secondary: no CME Globex-hours document for this 2023 date was retrieved (CME's 2023 summary PDF for it has only 404 captures, and the ZN service capture of 2024-07-08 returns empty event lists for 2023-01..07). AMP Futures' page quotes the CME Globex Control Center's generic 'Early Market HALT - Noon' line; its embedded CME schedule image (AMP-made table) shows the 'Interest Rate' row with HALT 12:00 CST and OPEN 17:00 CST (read visually, not script-checkable; see extra_evidence). Every CME-documented MLK and Presidents Day in 2019-2026 has the same 12:00 CT rates halt.

**2023-04-07 Good Friday (abbreviated, jobs report)** (early_halt, halt 10:15, status cme, time inferred; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/good-friday-holiday-settlement-times-2023.pdf
  - fetched via: https://web.archive.org/web/20230203064614id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/good-friday-holiday-settlement-times-2023.pdf
  - sha256: `908dbebd752477d61deccc8198f5b77f361db3931e6f95895a8646092c9fe22f`; verbatim: True
  - quote: "Good Friday 4/7/2023 Settlement Times Friday, April 7, 2023 ... CME Group Interest Rate Products 10:00 am CT Good Friday, 4/7/2023 Due to the BLS Employment Situation Release on April 7, 2023 CME Group FX, Cryptocurrency and Interest rate products will have unique settlements for trade date April 7th."
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/good-friday-holiday-settlement-times-2023.pdf
  - fetched via: https://web.archive.org/web/20230203064614id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/good-friday-holiday-settlement-times-2023.pdf
  - sha256: `908dbebd752477d61deccc8198f5b77f361db3931e6f95895a8646092c9fe22f`; verbatim: True
  - quote: "CME Group Interest Rate Products 10:00 am CT"
- notes: Status: CME settlement notice (interest rate products settled at 10:00 CT for trade date April 7) and the CME clearing advisory ('FX & Interest Rate markets will be settled on April 7th'). Close 10:15 CT inferred from the 10:00 CT settlement, the pattern of CME's own schedules for the other jobs-report Good Fridays (2021-04-02 spreadsheet and 2026-04-03 ZN service: settle/close 10:15), and AMP's image of the CME schedule ('Interest Rate' CLOSE 10:15 CST, secondary, read visually). No CME Globex-hours document for 2023-04-07 was retrieved.

**2023-05-29 Memorial Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf
  - fetched via: https://web.archive.org/web/20230420224018id_/https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf
  - sha256: `7657bc8089ca669cfd244c2e3e697b47a7e650f5d957efe5b32da001622acb35`; verbatim: True
  - quote: "PRODUCT NAME SUNDAY, 28 MAY 2023 MONDAY, 29 MAY 2023 TUESDAY, 30 MAY 2023 ... TRADE DATE: TUES 30 MAY TRADE DATE: TUES 30 MAY INTEREST RATE 16:00 (PREOPEN) 12:00 (PREOPEN) HALT TRADE DATE: WED 31 MAY"
- time: https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf
  - fetched via: https://web.archive.org/web/20230420224018id_/https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf
  - sha256: `7657bc8089ca669cfd244c2e3e697b47a7e650f5d957efe5b32da001622acb35`; verbatim: True
  - quote: "INTEREST RATE 16:00 (PREOPEN) 12:00 (PREOPEN) HALT TRADE DATE: WED 31 MAY ... OPEN: Start of continuous trading 17:00 (OPEN) 17:00 (OPEN) 16:45 (PREOPEN)"
- notes: CME holiday summary PDF (row 'INTEREST RATE', the most actively traded rates instrument); Monday 29 May column: '12:00 (PREOPEN) HALT' then '17:00 (OPEN)', trade date Tue 30 May. The legend defines PREOPEN (HALT) as order entry with no order matching. CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2023-06-19 Juneteenth** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf
  - fetched via: https://web.archive.org/web/20230613185949id_/https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf
  - sha256: `831f7f63e197ce58436780830aa515cb08dcf92bdf82a540265c2d21a4bffa43`; verbatim: True
  - quote: "PRODUCT NAME SUNDAY, 18 JUNE 2023 MONDAY, 19 JUNE 2023 TUESDAY, 20 JUNE 2023 ... TRADE DATE: TUES 20 JUNE TRADE DATE: TUES 20 JUNE INTEREST RATE 16:00 (PREOPEN) 12:00 (PREOPEN) HALT TRADE DATE: WED 21 JUNE"
- time: https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf
  - fetched via: https://web.archive.org/web/20230613185949id_/https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf
  - sha256: `831f7f63e197ce58436780830aa515cb08dcf92bdf82a540265c2d21a4bffa43`; verbatim: True
  - quote: "INTEREST RATE 16:00 (PREOPEN) 12:00 (PREOPEN) HALT TRADE DATE: WED 21 JUNE ... OPEN: Start of continuous trading 17:00 (OPEN) 17:00 (OPEN) 16:45 (PREOPEN)"
- notes: CME holiday summary PDF, row 'INTEREST RATE'; Monday 19 June column: '12:00 (PREOPEN) HALT' then '17:00 (OPEN)', trade date Tue 20 June. CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2023-07-04 Independence Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf
  - fetched via: https://web.archive.org/web/20230627125057id_/https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf
  - sha256: `ccbc1f1fc39ba2219fd748372faa985798fee7eaffabf69f08956f5465a769e3`; verbatim: True
  - quote: "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... TRADE DATE: WED 5 JULY INTEREST RATE TRADE DATE: WED 5 JULY 12:00 (PREOPEN) HALT TRADE DATE: THUR 6 JULY"
- time: https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf
  - fetched via: https://web.archive.org/web/20230627125057id_/https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf
  - sha256: `ccbc1f1fc39ba2219fd748372faa985798fee7eaffabf69f08956f5465a769e3`; verbatim: True
  - quote: "INTEREST RATE TRADE DATE: WED 5 JULY 12:00 (PREOPEN) HALT TRADE DATE: THUR 6 JULY ... OPEN: Start of continuous trading 16:45 (PREOPEN) 17:00 (OPEN)"
- notes: CME holiday summary PDF, row 'INTEREST RATE'; Tuesday 4 July column (layout read): 'TRADE DATE: WED 5 JULY 12:00 (PREOPEN) HALT 17:00 (OPEN)'. The same PDF (read by D.1f for equities) is linked from cmegroup.com/trading-hours.html. CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2023-09-04 Labor Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/trading-hours/files/labor-day-2023.pdf
  - fetched via: https://web.archive.org/web/20230802192446id_/https://www.cmegroup.com/trading-hours/files/labor-day-2023.pdf
  - sha256: `39a4c075437fdc7134166328eca730e3cabf3bea00ab369466dff63c99f8e948`; verbatim: True
  - quote: "PRODUCT NAME SUNDAY, 3 SEPTEMBER 2023 MONDAY, 4 SEPTEMBER 2023 TUESDAY, 5 SEPTEMBER 2023 ... TRADE DATE: TUES 5 SEP TRADE DATE: TUES 5 SEP INTEREST RATE 16:00 (PREOPEN) 12:00 (PREOPEN) HALT TRADE DATE: WED 6 SEP"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-09-03&toEventDate=2023-09-05&isProtected&_t=1720455278654
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-09-03&toEventDate=2023-09-05&isProtected&_t=1720455278654
  - sha256: `214f0f8f9dab7c04ff8b0277a6c70137b0399d0bb677bb8953dc87581e9ddb57`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2023-09-04","events":[{"tradingDate":"2023-09-05","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2023-09-05","eventTime":"17:00","marketEventType":"open"}]}"
- notes: Status: CME holiday summary PDF, row 'INTEREST RATE', Monday 4 September column '12:00 (PREOPEN) HALT', '17:00 (OPEN)'. Time: CME trading-hours service, ZN (id 316): eventDate 2023-09-04 preopen 12:00 and open 17:00, both trading date 2023-09-05. CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2023-11-23 Thanksgiving Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf
  - fetched via: https://web.archive.org/web/20231203205929id_/https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf
  - sha256: `99e187b3f3899e1062d662e148d5978e0cd075b961e6fc79550d4393812307e8`; verbatim: True
  - quote: "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 NOVEMBER 2023 ... INTEREST RATE TRADE DATE: FRI 24 NOV 12:00 (PREOPEN) HALT 12:15 (CLOSED)"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-11-22&toEventDate=2023-11-24&isProtected&_t=1720455278656
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-11-22&toEventDate=2023-11-24&isProtected&_t=1720455278656
  - sha256: `d1e371e76342de901d4b0ee26a2eb8d64c8df8fb2c488c961ed7d9f23282fa8f`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2023-11-23","events":[{"tradingDate":"2023-11-24","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2023-11-24","eventTime":"17:00","marketEventType":"open"}]}"
- notes: PDF layout: Thursday 23 Nov column 'TRADE DATE: FRI 24 NOV 12:00 (PREOPEN) HALT 17:00 (OPEN)'. ZN service: eventDate 2023-11-23 preopen 12:00, open 17:00 (trading date 2023-11-24). CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2023-11-24 Day after Thanksgiving** (early_halt, halt 12:15, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf
  - fetched via: https://web.archive.org/web/20231203205929id_/https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf
  - sha256: `99e187b3f3899e1062d662e148d5978e0cd075b961e6fc79550d4393812307e8`; verbatim: True
  - quote: "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 NOVEMBER 2023 ... INTEREST RATE TRADE DATE: FRI 24 NOV 12:00 (PREOPEN) HALT 12:15 (CLOSED)"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-11-22&toEventDate=2023-11-24&isProtected&_t=1720455278656
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-11-22&toEventDate=2023-11-24&isProtected&_t=1720455278656
  - sha256: `d1e371e76342de901d4b0ee26a2eb8d64c8df8fb2c488c961ed7d9f23282fa8f`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2023-11-24","events":[{"tradingDate":"2023-11-24","eventTime":"12:15","marketEventType":"closed"}]}"
- notes: PDF layout: Friday 24 Nov column 'TRADE DATE: FRI 24 NOV 12:15 (CLOSED)'. ZN service: eventDate 2023-11-24 closed 12:15.

**2023-12-25 Christmas Day** (full_closure, halt -, status cme, time n/a; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/trading-hours/files/christmas-day-2023.pdf
  - fetched via: https://web.archive.org/web/20260719095248id_/https://www.cmegroup.com/trading-hours/files/christmas-day-2023.pdf
  - sha256: `edcde0fcf61d3414cee2a332453db861e0e2d7edf81d89a5f379c44b2e72d5cf`; verbatim: True
  - quote: "PRODUCT NAME MONDAY, 25 DECEMBER 2023 TUESDAY, 26 DECEMBER 2023 TRADE DATE: TUES 26 DEC TRADE DATE: TUES 26 DEC 16:00 (CLOSED) INTEREST RATE 16:00 (PREOPEN) TRADE DATE: WED 27 DEC 17:00 (OPEN)"
- time: none (time n/a)
- notes: CME holiday summary PDF (Wayback capture 2026-07-19 of the CME file): Monday 25 Dec, row 'INTEREST RATE': no trading until '16:00 (PREOPEN) 17:00 (OPEN)' for trade date Tue 26 Dec. ZN service (capture 2024-07-08) agrees: eventDate 2023-12-25 preopen 16:00, open 17:00. The Friday 22 Dec close is not in either document (see gaps).

**2024-01-01 New Year's Day** (full_closure, halt -, status cme, time n/a; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/trading-hours/files/new-years-day-2024.pdf
  - fetched via: https://web.archive.org/web/20260811165716id_/https://www.cmegroup.com/trading-hours/files/new-years-day-2024.pdf
  - sha256: `34e60f8c97623df30e00f0ad8e4eeda20b99001b6c35d64f735828fecec5b9b8`; verbatim: True
  - quote: "PRODUCT NAME MONDAY, 1 JANUARY 2024 TUESDAY, 2 JANUARY 2024 TRADE DATE: TUES 2 JAN TRADE DATE: TUES 2 JAN 16:00 (CLOSED) INTEREST RATE 16:00 (PREOPEN) TRADE DATE: WED 3 JAN 17:00 (OPEN)"
- time: none (time n/a)
- notes: CME holiday summary PDF (Wayback capture 2026-08-11 of the CME file), row 'INTEREST RATE': Monday 1 Jan closed until 16:00 preopen / 17:00 open for Tue 2 Jan. ZN service (capture 2024-07-08) agrees. The Friday 29 Dec 2023 close is not in either document.

**2024-01-15 Martin Luther King Jr. Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663
  - sha256: `e7c5cee8b81efb4ec34a66e9295bb977cc6cd876007689b55a18be0485134fff`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2024-01-15","events":[{"tradingDate":"2024-01-16","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-01-16","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663
  - sha256: `e7c5cee8b81efb4ec34a66e9295bb977cc6cd876007689b55a18be0485134fff`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2024-01-15","events":[{"tradingDate":"2024-01-16","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-01-16","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME trading-hours service, ZN (10-Year T-Note, id 316), Wayback capture 2024-07-08. CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2024-02-19 Presidents Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only, bar check pending the step 2 purchase)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669
  - sha256: `07613c57b79dac5dc38a06c88cdaf01eb8182d3b88af8b9c7aa386a0e32b81d9`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2024-02-19","events":[{"tradingDate":"2024-02-20","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-02-20","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669
  - sha256: `07613c57b79dac5dc38a06c88cdaf01eb8182d3b88af8b9c7aa386a0e32b81d9`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2024-02-19","events":[{"tradingDate":"2024-02-20","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-02-20","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME trading-hours service, ZN, capture 2024-07-08. CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2024-03-29 Good Friday** (full_closure, halt -, status cme, time n/a; bar check: validated against CME schedules only; embargo or holdout-2 date, never checked against bars)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-03-28&toEventDate=2024-03-30&isProtected&_t=1720455278672
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-03-28&toEventDate=2024-03-30&isProtected&_t=1720455278672
  - sha256: `451df5abdd31106dcb258fe973e7353928dc44d8009f18b9bc9ed9795241cba7`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2024-03-28","events":[{"tradingDate":"2024-03-28","eventTime":"16:00","marketEventType":"closed"}]} ... {"groupCode":"ZN","eventDate":"2024-03-29","events":[]}"
- time: none (time n/a)
- notes: ZN service: eventDate 2024-03-28 has only 'closed' 16:00 (no evening reopen) and 2024-03-29 has no events; the next open is Sunday. Not a jobs-report Good Friday.

**2024-05-27 Memorial Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only; embargo or holdout-2 date, never checked against bars)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675
  - sha256: `842d4a8bd9fced2fe5ff15912d732016bb47b7a2113ede518d5d721ff428cb2d`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2024-05-27","events":[{"tradingDate":"2024-05-28","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-05-28","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675
  - sha256: `842d4a8bd9fced2fe5ff15912d732016bb47b7a2113ede518d5d721ff428cb2d`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2024-05-27","events":[{"tradingDate":"2024-05-28","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-05-28","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2024-06-19 Juneteenth** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only; embargo or holdout-2 date, never checked against bars)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677
  - sha256: `a48d61ca544ca2620f2cdc4a3d2232b2c9ff236282879cd4f7d86d66b1adef17`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2024-06-19","events":[{"tradingDate":"2024-06-20","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-06-20","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677
  - sha256: `a48d61ca544ca2620f2cdc4a3d2232b2c9ff236282879cd4f7d86d66b1adef17`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2024-06-19","events":[{"tradingDate":"2024-06-20","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-06-20","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2024-07-04 Independence Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only; embargo or holdout-2 date, never checked against bars)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680
  - sha256: `54de3d48c849891d7f37ec1afa38d3e10103c7d606b141a91ad8dec9349e529a`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680
  - sha256: `54de3d48c849891d7f37ec1afa38d3e10103c7d606b141a91ad8dec9349e529a`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2024-09-02 Labor Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only; embargo or holdout-2 date, never checked against bars)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1720455278683
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1720455278683
  - sha256: `bbe6c78555cba0437fe4b9c6eac0063983ecae49056877db618ed2b29c109546`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2024-09-02","events":[{"tradingDate":"2024-09-03","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-09-03","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1720455278683
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1720455278683
  - sha256: `bbe6c78555cba0437fe4b9c6eac0063983ecae49056877db618ed2b29c109546`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2024-09-02","events":[{"tradingDate":"2024-09-03","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-09-03","eventTime":"17:00","marketEventType":"open"}]}"
- notes: ZN service capture 2024-07-08, before the holiday. CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2024-11-28 Thanksgiving Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only; embargo or holdout-2 date, never checked against bars)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1720455278685
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1720455278685
  - sha256: `f6a15f26991d25f8c6821fa6c967d0e76b2ad3f775bed62a2a001ec2fd7e389a`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2024-11-28","events":[{"tradingDate":"2024-11-29","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-11-29","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1720455278685
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1720455278685
  - sha256: `f6a15f26991d25f8c6821fa6c967d0e76b2ad3f775bed62a2a001ec2fd7e389a`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2024-11-28","events":[{"tradingDate":"2024-11-29","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-11-29","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2024-11-29 Day after Thanksgiving** (early_halt, halt 12:15, status cme, time cme; bar check: validated against CME schedules only; embargo or holdout-2 date, never checked against bars)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1720455278685
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1720455278685
  - sha256: `f6a15f26991d25f8c6821fa6c967d0e76b2ad3f775bed62a2a001ec2fd7e389a`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","eventTime":"12:15","marketEventType":"closed"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1720455278685
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1720455278685
  - sha256: `f6a15f26991d25f8c6821fa6c967d0e76b2ad3f775bed62a2a001ec2fd7e389a`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","eventTime":"12:15","marketEventType":"closed"}]}"
- notes: 

**2024-12-24 Christmas Eve** (early_halt, halt 12:15, status cme, time cme; bar check: validated against CME schedules only; embargo or holdout-2 date, never checked against bars)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1720455278686
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1720455278686
  - sha256: `5a3e1c994f9e22f7797bb9d49e78984f5e28ef185ad0c657eeae1a32fa851202`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eventTime":"12:15","marketEventType":"closed"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1720455278686
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1720455278686
  - sha256: `5a3e1c994f9e22f7797bb9d49e78984f5e28ef185ad0c657eeae1a32fa851202`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eventTime":"12:15","marketEventType":"closed"}]}"
- notes: 

**2024-12-25 Christmas Day** (full_closure, halt -, status cme, time n/a; bar check: validated against CME schedules only; embargo or holdout-2 date, never checked against bars)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1720455278686
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1720455278686
  - sha256: `5a3e1c994f9e22f7797bb9d49e78984f5e28ef185ad0c657eeae1a32fa851202`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eventTime":"12:15","marketEventType":"closed"}]} ... {"groupCode":"ZN","eventDate":"2024-12-25","events":[{"tradingDate":"2024-12-26","eventTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-12-26","eventTime":"17:00","marketEventType":"open"}]}"
- time: none (time n/a)
- notes: ZN service: eventDate 2024-12-24 closed 12:15 with no evening reopen; 2024-12-25 preopen 16:00, open 17:00 for trading date 2024-12-26.

**2025-01-01 New Year's Day** (full_closure, halt -, status cme, time n/a; bar check: validated against CME schedules only; embargo or holdout-2 date, never checked against bars)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1720455278688
  - fetched via: https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1720455278688
  - sha256: `6b6399a1de34bbc9eea0a135691dfed90edee2a0c705162b1840e214256e4c46`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31","eventTime":"16:00","marketEventType":"closed"}]} ... {"groupCode":"ZN","eventDate":"2025-01-01","events":[{"tradingDate":"2025-01-02","eventTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-01-02","eventTime":"17:00","marketEventType":"open"}]}"
- time: none (time n/a)
- notes: ZN service: eventDate 2024-12-31 closed 16:00 (regular) with no evening reopen; 2025-01-01 preopen 16:00, open 17:00 for trading date 2025-01-02.

**2025-01-09 National Day of Mourning (Carter)** (early_halt, halt 12:15, status cme, time cme; bar check: validated against CME schedules only; embargo or holdout-2 date, never checked against bars)

- status: https://www.cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf
  - fetched via: https://web.archive.org/web/20250218194143id_/https://www.cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf
  - sha256: `f169d709420a24ebe7f0ab4466ecd8961ea677cb56e9a8fc60fc43dcc9a70ac2`; verbatim: True
  - quote: "U.S. National Day of Mourning Trading Schedule for Globex, BrokerTec, EBS and Trading Floor ... PRODUCT NAME JANUARY 9, 2025 TRADING FLOOR CLEARPORT ... CME GROUP INTEREST RATE EARLY CLOSE – 12:15 PM CT EARLY CLOSE – 12:00 PM CT NORMAL HOURS"
- time: https://www.cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf
  - fetched via: https://web.archive.org/web/20250218194143id_/https://www.cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf
  - sha256: `f169d709420a24ebe7f0ab4466ecd8961ea677cb56e9a8fc60fc43dcc9a70ac2`; verbatim: True
  - quote: "CME GROUP INTEREST RATE EARLY CLOSE – 12:15 PM CT EARLY CLOSE – 12:00 PM CT NORMAL HOURS"
- notes: CME's day-of-mourning schedule (file named day-of-mourning-january-9-2024.pdf, dated January 9, 2025 inside): Globex column 'EARLY CLOSE – 12:15 PM CT' for CME Group Interest Rate; the 12:00 PM CT early close is the TRADING FLOOR column. Same PDF: 'All other CME/CBOT/NYMEX/COMEX Futures & Options WILL derive settlements on the National DOM trade date.' The 17:00 CT reopen is not stated in the PDF (regular reopen assumed, as in data.cme_calendar).

**2025-01-20 Martin Luther King Jr. Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only; embargo or holdout-2 date, never checked against bars)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539
  - sha256: `2cdfb6d5a2bbc1b6b159f5c980d2bf70350c5b181c8d91c3c1023d1eb6a26175`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2025-01-20","events":[{"tradingDate":"2025-01-21","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-01-21","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539
  - sha256: `2cdfb6d5a2bbc1b6b159f5c980d2bf70350c5b181c8d91c3c1023d1eb6a26175`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2025-01-20","events":[{"tradingDate":"2025-01-21","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-01-21","eventTime":"17:00","marketEventType":"open"}]}"
- notes: ZN service capture 2024-12-20, before the holiday. CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2025-02-17 Presidents Day** (early_halt, halt 12:00, status cme, time cme; bar check: validated against CME schedules only; embargo or holdout-2 date, never checked against bars)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540
  - sha256: `46119e9af5875c05dee480d7465b431344d0c5bf55492ca1ebb92024a77b5f72`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2025-02-17","events":[{"tradingDate":"2025-02-18","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-02-18","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540
  - sha256: `46119e9af5875c05dee480d7465b431344d0c5bf55492ca1ebb92024a77b5f72`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2025-02-17","events":[{"tradingDate":"2025-02-18","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-02-18","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2025-04-18 Good Friday** (full_closure, halt -, status cme, time n/a; bar check: pending Task 7 (research-window bars))

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-04-17&toEventDate=2025-04-19&isProtected&_t=1734710019542
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-04-17&toEventDate=2025-04-19&isProtected&_t=1734710019542
  - sha256: `c067674b1c10456f5fd86da6db1438b54fa3e352a44662674eb9a9411332edd3`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2025-04-17","events":[{"tradingDate":"2025-04-17","eventTime":"16:00","marketEventType":"closed"}]} ... {"groupCode":"ZN","eventDate":"2025-04-18","events":[]}"
- time: none (time n/a)
- notes: ZN service: eventDate 2025-04-17 closed 16:00 with no evening reopen; 2025-04-18 no events. Not a jobs-report Good Friday.

**2025-05-26 Memorial Day** (early_halt, halt 12:00, status cme, time cme; bar check: pending Task 7 (research-window bars))

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543
  - sha256: `73d01c7c3c0cd47c4fb9d6cf14a7c60a1f80d2c81e6a26d42e4c7a1367c94c35`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2025-05-26","events":[{"tradingDate":"2025-05-27","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-05-27","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543
  - sha256: `73d01c7c3c0cd47c4fb9d6cf14a7c60a1f80d2c81e6a26d42e4c7a1367c94c35`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2025-05-26","events":[{"tradingDate":"2025-05-27","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-05-27","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2025-06-19 Juneteenth** (early_halt, halt 12:00, status cme, time cme; bar check: pending Task 7 (research-window bars))

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544
  - sha256: `7dcceaa759e9888568093eb258a67be0513b443b72acd07dc873a75115854bee`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2025-06-19","events":[{"tradingDate":"2025-06-20","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-06-20","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544
  - sha256: `7dcceaa759e9888568093eb258a67be0513b443b72acd07dc873a75115854bee`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2025-06-19","events":[{"tradingDate":"2025-06-20","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-06-20","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2025-07-04 Independence Day** (early_halt, halt 12:00, status cme, time cme; bar check: pending Task 7 (research-window bars))

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545
  - sha256: `cd4008266d4387521824839b0b1858ac33bc2326fe3ade74f5f2d756b5d3026f`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-07-04","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2025-07-04","eventTime":"17:00","marketEventType":"open"}]} ... {"groupCode":"ZN","eventDate":"2025-07-04","events":[{"tradingDate":"2025-07-04","eventTime":"12:00","marketEventType":"closed"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545
  - sha256: `cd4008266d4387521824839b0b1858ac33bc2326fe3ade74f5f2d756b5d3026f`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2025-07-04","events":[{"tradingDate":"2025-07-04","eventTime":"12:00","marketEventType":"closed"}]}"
- notes: ZN service: eventDate 2025-07-03 closed 16:00 then preopen 16:45 / open 17:00 for trading date 2025-07-04; eventDate 2025-07-04 'closed' 12:00 (a Friday: next open Sunday).

**2025-09-01 Labor Day** (early_halt, halt 12:00, status cme, time cme; bar check: pending Task 7 (research-window bars))

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546
  - sha256: `dff4ccaf3b18531b37b4ee789d2ca5e686a3c04f6dd1aa5c720b732a6832eeb0`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2025-09-01","events":[{"tradingDate":"2025-09-02","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-09-02","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546
  - sha256: `dff4ccaf3b18531b37b4ee789d2ca5e686a3c04f6dd1aa5c720b732a6832eeb0`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2025-09-01","events":[{"tradingDate":"2025-09-02","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-09-02","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2025-11-27 Thanksgiving Day** (early_halt, halt 12:00, status cme, time cme; bar check: pending Task 7 (research-window bars))

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1734710019547
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1734710019547
  - sha256: `c3aa44bf0cb487f45adbb9a9f6f7c8a79a6214aca71f1317057e579212b6a6d9`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2025-11-27","events":[{"tradingDate":"2025-11-28","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1734710019547
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1734710019547
  - sha256: `c3aa44bf0cb487f45adbb9a9f6f7c8a79a6214aca71f1317057e579212b6a6d9`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2025-11-27","events":[{"tradingDate":"2025-11-28","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2025-11-28 Day after Thanksgiving** (early_halt, halt 12:15, status cme, time cme; bar check: pending Task 7 (research-window bars))

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1734710019547
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1734710019547
  - sha256: `c3aa44bf0cb487f45adbb9a9f6f7c8a79a6214aca71f1317057e579212b6a6d9`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"12:15","marketEventType":"closed"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1734710019547
  - fetched via: https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1734710019547
  - sha256: `c3aa44bf0cb487f45adbb9a9f6f7c8a79a6214aca71f1317057e579212b6a6d9`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"12:15","marketEventType":"closed"}]}"
- notes: 

**2025-12-24 Christmas Eve** (early_halt, halt 12:15, status cme, time cme; bar check: pending Task 7 (research-window bars))

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
  - fetched via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
  - sha256: `6944a2dd28359cea6a47194c6e74ef9f8808229fd1411482025b962f87290cb2`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eventTime":"12:15","marketEventType":"closed"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
  - fetched via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
  - sha256: `6944a2dd28359cea6a47194c6e74ef9f8808229fd1411482025b962f87290cb2`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eventTime":"12:15","marketEventType":"closed"}]}"
- notes: ZN service capture 2026-01-29 (after the date); the 2024-12-20 capture of the same range returned no events yet.

**2025-12-25 Christmas Day** (full_closure, halt -, status cme, time n/a; bar check: pending Task 7 (research-window bars))

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
  - fetched via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
  - sha256: `6944a2dd28359cea6a47194c6e74ef9f8808229fd1411482025b962f87290cb2`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eventTime":"12:15","marketEventType":"closed"}]} ... {"groupCode":"ZN","eventDate":"2025-12-25","events":[{"tradingDate":"2025-12-26","eventTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-12-26","eventTime":"17:00","marketEventType":"open"}]}"
- time: none (time n/a)
- notes: ZN service: eventDate 2025-12-24 closed 12:15 with no evening reopen; 2025-12-25 preopen 16:00, open 17:00 for trading date 2025-12-26. ZN service capture 2026-01-29 (after the date); the 2024-12-20 capture of the same range returned no events yet.

**2026-01-01 New Year's Day** (full_closure, halt -, status cme, time n/a; bar check: pending Task 7 (research-window bars))

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066
  - fetched via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066
  - sha256: `9eb4ca23526ff7086662f547be2a5702d40f67d7ab21024ff7b3bac9e17e0d19`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31","eventTime":"16:00","marketEventType":"closed"}]} ... {"groupCode":"ZN","eventDate":"2026-01-01","events":[{"tradingDate":"2026-01-02","eventTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2026-01-02","eventTime":"17:00","marketEventType":"open"}]}"
- time: none (time n/a)
- notes: ZN service: eventDate 2025-12-31 closed 16:00 (regular) with no evening reopen; 2026-01-01 preopen 16:00, open 17:00 for trading date 2026-01-02. ZN service capture 2026-01-29 (after the date); the 2024-12-20 capture of the same range returned no events yet.

**2026-01-19 Martin Luther King Jr. Day** (early_halt, halt 12:00, status cme, time cme; bar check: pending Task 7 (research-window bars))

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068
  - fetched via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068
  - sha256: `f8b1f22d11e3465a8b81b94e4f33a9e7cde1b32e35c11ee35965b219c2a55e1d`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2026-01-19","events":[{"tradingDate":"2026-01-20","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2026-01-20","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068
  - fetched via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068
  - sha256: `f8b1f22d11e3465a8b81b94e4f33a9e7cde1b32e35c11ee35965b219c2a55e1d`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2026-01-19","events":[{"tradingDate":"2026-01-20","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2026-01-20","eventTime":"17:00","marketEventType":"open"}]}"
- notes: ZN service capture 2026-01-29. CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2026-02-16 Presidents Day** (early_halt, halt 12:00, status cme, time cme; bar check: pending Task 7 (research-window bars))

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1769649703070
  - fetched via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1769649703070
  - sha256: `92a39359c8f386fbe5f367391a6a870cebcea33c6fb6b373171e65fa7ee57f3a`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2026-02-16","events":[{"tradingDate":"2026-02-17","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2026-02-17","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1769649703070
  - fetched via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1769649703070
  - sha256: `92a39359c8f386fbe5f367391a6a870cebcea33c6fb6b373171e65fa7ee57f3a`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2026-02-16","events":[{"tradingDate":"2026-02-17","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2026-02-17","eventTime":"17:00","marketEventType":"open"}]}"
- notes: ZN service capture 2026-01-29, before the holiday. CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2026-04-03 Good Friday (abbreviated, jobs report)** (early_halt, halt 10:15, status cme, time cme; bar check: pending Task 7 (research-window bars))

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1769649703072
  - fetched via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1769649703072
  - sha256: `054e91e27350e39e4491a3d5f46f0c628a08a7e04274eea27af3f0621b519613`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-04-03","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2026-04-03","eventTime":"17:00","marketEventType":"open"}]} ... {"groupCode":"ZN","eventDate":"2026-04-03","events":[{"tradingDate":"2026-04-03","eventTime":"10:15","marketEventType":"closed"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1769649703072
  - fetched via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1769649703072
  - sha256: `054e91e27350e39e4491a3d5f46f0c628a08a7e04274eea27af3f0621b519613`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2026-04-03","events":[{"tradingDate":"2026-04-03","eventTime":"10:15","marketEventType":"closed"}]}"
- notes: ZN service capture 2026-01-29: eventDate 2026-04-02 closed 16:00 then preopen 16:45 / open 17:00 for trading date 2026-04-03; eventDate 2026-04-03 'closed' 10:15.

**2026-05-25 Memorial Day** (early_halt, halt 12:00, status cme, time cme; bar check: pending Task 7 (research-window bars))

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1769649703074
  - fetched via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1769649703074
  - sha256: `5f08ca1972caf9d075744f359cff3bb86de91a57ebed7d3550886a2fc736a9f2`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2026-05-25","events":[{"tradingDate":"2026-05-26","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2026-05-26","eventTime":"17:00","marketEventType":"open"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1769649703074
  - fetched via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1769649703074
  - sha256: `5f08ca1972caf9d075744f359cff3bb86de91a57ebed7d3550886a2fc736a9f2`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2026-05-25","events":[{"tradingDate":"2026-05-26","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2026-05-26","eventTime":"17:00","marketEventType":"open"}]}"
- notes: CME books the Globex session that ends at the holiday halt to the next trade date; this module models the halt day as its own short trade date (the data.cme_calendar convention).

**2026-06-19 Juneteenth** (early_halt, halt 12:00, status cme, time cme; bar check: pending Task 7 (research-window bars))

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-17&toEventDate=2026-06-19&isProtected&_t=1769649703075
  - fetched via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-17&toEventDate=2026-06-19&isProtected&_t=1769649703075
  - sha256: `267c1ae4f275cc3d23a41a202cadaa54c5adcfbdb109c10143ba06326b5b2d68`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-06-22","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2026-06-22","eventTime":"17:00","marketEventType":"open"}]} ... {"groupCode":"ZN","eventDate":"2026-06-19","events":[{"tradingDate":"2026-06-22","eventTime":"12:00","marketEventType":"closed"}]}"
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-17&toEventDate=2026-06-19&isProtected&_t=1769649703075
  - fetched via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-17&toEventDate=2026-06-19&isProtected&_t=1769649703075
  - sha256: `267c1ae4f275cc3d23a41a202cadaa54c5adcfbdb109c10143ba06326b5b2d68`; verbatim: True
  - quote: "{"groupCode":"ZN","eventDate":"2026-06-19","events":[{"tradingDate":"2026-06-22","eventTime":"12:00","marketEventType":"closed"}]}"
- notes: ZN service capture 2026-01-29 (the 2026-06-19 capture agrees): eventDate 2026-06-18 closed 16:00, reopen 17:00 for trading date 2026-06-22; eventDate 2026-06-19 'closed' 12:00 (trading date 2026-06-22). CME books the Thursday-evening-to-Friday-noon session to Monday 2026-06-22; this module keeps 2026-06-19 as its own short trade date (the data.cme_calendar convention).

## Late open (interface extension)

`data.cme_calendar.Holiday` has no field for a late start, so the module adds `LateOpen` and `LATE_OPENS` / `LATE_OPEN_SOURCES` beside `HOLIDAYS` (additive; `HOLIDAYS` keeps the planned 2025-11-28 early close at 12:15 CT).

**2025-11-28**, trading resumed 07:30 CT

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
  - fetched via: https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
  - sha256: `ab8342bd5dbc6dd78f4f6efe599b6448d47a0adffe1bd8baafa5337d49c08062`; verbatim: True
  - quote: ""globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"07:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"12:15","marketEventType":"closed"}]}"
- notes: Unscheduled: CME Globex outage (data-center cooling failure at CyrusOne) after the Thursday 2025-11-27 17:00 CT reopen. CME's ZN service record for eventDate 2025-11-28 in the 2026-01-29 capture adds 'preopen' 07:00 and 'open' 07:30 before the scheduled 12:15 close; the 2024-12-20 capture (the planned schedule, used for the HOLIDAYS entry) has only the 12:15 close. The halt start is not in any CME document retrieved: CNBC reports CME saying markets 'were halted due to a cooling issue' (secondary, see extra_evidence). The same outage hit every CME Globex group, including equities (data/cme_calendar.py does not record it).

## CME-stated regular days near holidays (NO_ENTRY_FINDINGS)

| Date | Source | Capture | Verbatim | Notes |
|---|---|---|---|---|
| 2019-05-24 | cme hc/2019-holiday-calendars.zip | Wayback 20210126094837 | True | Interest Rate Products 'Regular Fri. Close' 16:00 on Friday May 24. CME's settlement notice gives 'CME Group Interest Rate Products 12:00:00 CT' that day (see EARLY_SETTLEMENT_CT). |
| 2019-07-03 | cme hc/2019-holiday-calendars.zip | Wayback 20210126094837 | True | Interest Rate Products 'Regular Close' 16:00 on Wednesday July 3 (equities closed early at 12:15). CME's settlement notice for the day gives 'Interest Rate Products 12:00:00 CT' (see EARLY_SETTLEMENT_CT). |
| 2019-10-14 | cme hc/2019-holiday-calendars.zip | Wayback 20210126094837 | True | Columbus Day is a bond-market (SIFMA) holiday but not a CME holiday: CME settles every product at its normal time and published no Globex holiday schedule for it. Later years not re-fetched. |
| 2019-11-11 | cme hc/2019-holiday-calendars.zip | Wayback 20210126094837 | True | Veterans Day is a bond-market (SIFMA) holiday but not a CME holiday: CME settles every product at its normal time and published no Globex holiday schedule for it. Later years not re-fetched. |
| 2019-12-31 | cme hc/2019-holiday-calendars.zip | Wayback 20210126094837 | True | Interest Rate Products 'Close' 16:00 on Tuesday December 31. CME's settlement notice gives 'CME Group Interest Rate Products 12:00:00 CT' (see EARLY_SETTLEMENT_CT). |
| 2020-04-09 | cme hc/2020-holiday-calendars.zip | Wayback 20260730000000 | True | Interest Rate Products 'Regular Close' 16:00 on Thursday April 9, before the Good Friday closure. |
| 2020-05-22 | cme hc/2020-holiday-calendars.zip | Wayback 20260730000000 | True | Interest Rate Products 'Regular Fri. Close' 16:00 on Friday May 22. |
| 2020-07-02 | cme hc/2020-holiday-calendars.zip | Wayback 20260730000000 | True | Interest Rate Products 'Regular Close' 16:00 on Thursday July 2. |
| 2020-12-31 | cme hc/2020-holiday-calendars.zip | Wayback 20260730000000 | True | Interest Rate Products 'Close' 16:00 on Thursday December 31. |
| 2021-04-01 | cme hc/2021-holiday-calendars.zip | Wayback 20260830000000 | True | Interest Rate Products 'Regular Close' 16:00 on Thursday April 1 (then reopen 17:00 for the abbreviated Friday April 2 session). |
| 2021-05-28 | cme hc/2021-holiday-calendars.zip | Wayback 20260830000000 | True | Interest Rate Products 'Regular Fri. Close' 16:00 on Friday May 28. |
| 2021-07-02 | cme hc/2021-holiday-calendars.zip | Wayback 20260830000000 | True | Interest Rate Products 'Regular Close' 16:00 on Friday July 2. |
| 2021-12-23 | cme hc/2021-holiday-calendars.zip | Wayback 20260830000000 | True | Globex 'Interest Rate Products' regular close 16:00; the sheet's 'Treasuries TAS' exception closes at 12:00, i.e. CME's Treasury settlement was early that day. |
| 2021-12-31 | cme hc/2021-holiday-calendars.zip | Wayback 20260830000000 | True | Globex 'Interest Rate Products' regular close 16:00; the sheet's 'Treasuries TAS' exception closes at 12:00, i.e. CME's Treasury settlement was early that day. |
| 2022-01-03 | cme hc/2021-holiday-calendars.zip | Wayback 20260830000000 | True | January 1, 2022 fell on a Saturday; the sheet shows 'NORMAL' 'SCHEDULE' for Monday January 3 (no weekday closure). |
| 2022-04-14 | cme hc/2022-good-friday-holiday-schedule.xls | Wayback 20220704065501 | True | Globex 'Interest Rate Products' regular close 16:00; the sheet's 'Treasuries TAS' exception closes at 12:00, i.e. CME's Treasury settlement was early that day. |
| 2022-05-27 | cme hc/2022-memorial-day-holiday-schedule.xls | Wayback 20220704065438 | True | Globex 'Interest Rate Products' regular close 16:00; the sheet's 'Treasuries TAS' exception closes at 12:00, i.e. CME's Treasury settlement was early that day. |
| 2022-07-01 | cme hc/2022-independence-day-holiday-schedule.xls | Wayback 20220704065450 | True | Globex 'Interest Rate Products' regular close 16:00; the sheet's 'Treasuries TAS' exception closes at 12:00, i.e. CME's Treasury settlement was early that day. |
| 2022-12-23 | cme hc/2022-christmas-holiday-schedule.xls | Wayback 20220704065430 | True | Globex 'Interest Rate Products' regular close 16:00; the sheet's 'Treasuries TAS' exception closes at 12:00, i.e. CME's Treasury settlement was early that day. Schedule sheet 'Updated 6/29/2022', Wayback capture 2022-07-04, months before the holiday; no later capture was retrieved, so a later CME revision cannot be excluded. |
| 2022-12-30 | cme hc/2023-new-years-holiday-schedule.xls | Wayback 20220704065501 | True | Globex 'Interest Rate Products' regular close 16:00; the sheet's 'Treasuries TAS' exception closes at 12:00, i.e. CME's Treasury settlement was early that day. Schedule sheet 'Updated 6/29/22', Wayback capture 2022-07-04, months before the holiday; no later capture was retrieved, so a later CME revision cannot be excluded. |
| 2023-07-03 | cme th/4th-of-july-2023.pdf | Wayback 20230627125057 | True | Layout read: the INTEREST RATE row's Monday 3 July cell is 'TRADE DATE: MON 3 JULY 16:00 (CLOSED)', then 'TRADE DATE: WED 5 JULY 16:45 (PREOPEN) 17:00 (OPEN)'; the EQUITIES row's Monday cell is '12:15 (CLOSED)'. Interest rates closed at their regular 16:00. |
| 2024-03-28 | cme svc ZN 2024-03-28..024-03-30& | Wayback 20240708161439 | True | ZN closed 16:00 (regular) on Thursday March 28, before the Good Friday closure. |
| 2024-07-03 | cme svc ZN 2024-07-03..024-07-05& | Wayback 20240708161439 | True | ZN closed 16:00 (regular) on Wednesday July 3 and reopened 17:00 for trade date July 5 (equities closed early at 12:15). |
| 2024-12-31 | cme svc ZN 2024-12-31..025-01-02& | Wayback 20240708161439 | True | ZN closed 16:00 (regular) on Tuesday December 31. |
| 2025-04-17 | cme svc ZN 2025-04-17..025-04-19& | Wayback 20241220155340 | True | ZN closed 16:00 (regular) on Thursday April 17, before the Good Friday closure. |
| 2025-07-03 | cme svc ZN 2025-07-03..025-07-05& | Wayback 20241220155340 | True | ZN closed 16:00 (regular) on Thursday July 3 and reopened 17:00 for trade date July 4. |
| 2025-12-31 | cme svc ZN 2025-12-31..026-01-02& | Wayback 20260129012143 | True | ZN closed 16:00 (regular) on Wednesday December 31. ZN service capture 2026-01-29 (after the date); the 2024-12-20 capture of the same range returned no events yet. |
| 2026-04-02 | cme svc ZN 2026-04-01..026-04-03& | Wayback 20260129012143 | True | ZN closed 16:00 (regular) on Thursday April 2 and reopened 17:00 for the abbreviated Good Friday session. |
| 2026-06-18 | cme svc ZN 2026-06-17..026-06-19& | Wayback 20260129012143 | True | ZN closed 16:00 (regular) on Thursday June 18 and reopened 17:00 (trading date 2026-06-22). |

Quotes, hashes and xlrd readings for these rows are in the JSON (`no_entry_findings`).

## Rates settlement times other than 14:00 CT (EARLY_SETTLEMENT_CT)

| Date | Settle CT | Source | Verbatim | Globex that day |
|---|---|---|---|---|
| 2019-05-24 | 12:00 | cme hc/2019-holiday-calendars.zip | True | Globex regular close 16:00 (no entry). |
| 2019-07-03 | 12:00 | cme hc/2019-holiday-calendars.zip | True | Globex regular close 16:00 (no entry). |
| 2019-11-29 | 12:00 | cme hc/2019-holiday-calendars.zip | True | Early close 12:15 (HOLIDAYS). |
| 2019-12-24 | 12:00 | cme hc/2019-holiday-calendars.zip | True | Early close 12:15 (HOLIDAYS). |
| 2019-12-31 | 12:00 | cme hc/2019-holiday-calendars.zip | True | Globex regular close 16:00 (no entry). The same notice gives 12:01 CT for the expiring December 2-year and 5-year contracts. |
| 2020-04-09 | 12:00 | cme hc/good-friday-holiday-settlement-times-2020.pdf | True | Globex regular close 16:00 (no entry). |
| 2020-05-22 | 12:00 | cme hc/memorial-day-holiday-settlement-times-2020.pdf | True | Globex regular close 16:00 (no entry). |
| 2020-07-02 | 12:00 | cme hc/fourth-of-july-settlement-times-2020.pdf | True | Globex regular close 16:00 (no entry). |
| 2020-11-27 | 12:00 | cme hc/thanksgiving-holiday-settlement-times-2020.pdf | True | Early close 12:15 (HOLIDAYS). |
| 2020-12-31 | 12:00 | cme hc/new-years-eve-holiday-settlement-times-2020.pdf | True | Globex regular close 16:00 (no entry). |
| 2021-04-02 | 10:00 | cme hc/good-friday-holiday-settlement-times-2021.pdf | True | Jobs-report Good Friday, close 10:15 (HOLIDAYS). |
| 2021-05-28 | 12:00 | cme hc/memorial-day-holiday-settlement-times-2021.pdf | True | Globex regular close 16:00 (no entry). |
| 2021-07-02 | 12:00 | cme hc/fourth-of-july-settlement-times-2021.pdf | True | Globex regular close 16:00 (no entry). |
| 2021-11-26 | 12:00 | cme hc/thanksgiving-holiday-settlement-times-2021.pdf | True | Early close 12:15 (HOLIDAYS). |
| 2021-12-23 | 12:00 | cme hc/christmas-holiday-settlement-times-2021.pdf | True | Globex regular close 16:00 (no entry). |
| 2021-12-31 | 12:00 | cme hc/new-years-eve-holiday-settlement-times-2022.pdf | True | Globex regular close 16:00 (no entry). |
| 2022-04-14 | 12:00 | cme hc/good-friday-holiday-settlement-times-2022.pdf | True | Globex regular close 16:00 (no entry). |
| 2022-05-27 | 12:00 | cme hc/memorial-day-holiday-settlement-times-2022.pdf | True | Globex regular close 16:00 (no entry). |
| 2022-07-01 | 12:00 | cme hc/fourth-of-july-settlement-times-2022.pdf | True | Globex regular close 16:00 (no entry). |
| 2022-11-25 | 12:00 | cme hc/thanksgiving-holiday-settlement-times-2022.pdf | True | Early close 12:15 (HOLIDAYS). |
| 2022-12-23 | 12:00 | cme hc/christmas-holiday-settlement-times-2022.pdf | True | Globex regular close 16:00 (no entry). |
| 2022-12-30 | 12:00 | cme hc/new-years-eve-holiday-settlement-times-2023.pdf | True | Globex regular close 16:00 (no entry). |
| 2023-04-07 | 10:00 | cme hc/good-friday-holiday-settlement-times-2023.pdf | True | Abbreviated jobs-report Good Friday (HOLIDAYS, close 10:15 inferred). |
| 2023-05-26 | 12:00 | cme hc/memorial-day-holiday-settlement-times-2023.pdf | True | Globex hours not in any CME document retrieved (GLOBEX_HOURS_UNDOCUMENTED). |
| 2023-07-03 | 12:00 | cme hc/fourth-of-july-settlement-times-2023.pdf | True | Globex regular close 16:00 (no entry). |
| 2023-11-24 | 12:00 | cme hc/thanksgiving-holiday-settlement-times-2023.pdf | True | Early close 12:15 (HOLIDAYS). |
| 2023-12-22 | 12:00 | cme hc/christmas-holiday-settlement-times-2023.pdf | True | Globex hours not in any CME document retrieved (GLOBEX_HOURS_UNDOCUMENTED). |
| 2023-12-29 | 12:00 | cme hc/new-years-eve-holiday-settlement-times-2024.pdf | True | Globex hours not in any CME document retrieved (GLOBEX_HOURS_UNDOCUMENTED). |
| 2024-03-28 | 12:00 | cme hc/good-friday-holiday-settlement-times-2024.pdf | True | Globex regular close 16:00 (no entry). |
| 2024-05-24 | 12:00 | cme hc/memorial-day-holiday-settlement-times-2024.pdf | True | Globex hours not in any CME document retrieved (GLOBEX_HOURS_UNDOCUMENTED). |
| 2024-07-03 | 12:00 | cme hc/us-independence-day-settlement-times-2024.pdf | True | Globex regular close 16:00 (no entry). |
| 2024-11-29 | 12:00 | cme hc/thanksgiving-holiday-settlement-times-2024.pdf | True | Early close 12:15 (HOLIDAYS). |
| 2024-12-24 | 12:00 | cme hc/christmas-holiday-settlement-times-2024.pdf | True | Early close 12:15 (HOLIDAYS). |
| 2024-12-31 | 12:00 | cme hc/new-years-eve-holiday-settlement-times-2025.pdf | True | Globex regular close 16:00 (no entry). |
| 2025-04-17 | 12:00 | cme hc/2025/good-friday-holiday-settlement-times-2025.pdf | True | Globex regular close 16:00 (no entry). |
| 2025-05-23 | 12:00 | cme hc/2025/memorial-day-holiday-settlement-times-2025.pdf | True | Globex hours not in any CME document retrieved (GLOBEX_HOURS_UNDOCUMENTED). |
| 2025-07-03 | 12:00 | cme hc/2025/us-independence-day-settlement-times-2025.pdf | True | Globex regular close 16:00 (no entry). |
| 2025-11-28 | 12:00 | cme hc/2025/thanksgiving-holiday-settlement-times-2025.pdf | True | Early close 12:15 (HOLIDAYS). |
| 2025-12-24 | 12:00 | cme hc/2025/christmas-holiday-settlement-times-2025.pdf | True | Early close 12:15 (HOLIDAYS). |
| 2025-12-31 | 12:00 | cme hc/2025/new-years-eve-holiday-settlement-times-2026.pdf | True | Globex regular close 16:00 (no entry). |
| 2026-05-22 | 12:00 | cme hc/2026/memorial-day-holiday-settlement-times-2026.pdf | True | Globex hours not in any CME document retrieved (GLOBEX_HOURS_UNDOCUMENTED). |

## Days with an early settlement but no CME Globex-hours document (GLOBEX_HOURS_UNDOCUMENTED)

- 2023-05-26: Friday before Memorial Day: CME settled rates at 12:00 CT (EARLY_SETTLEMENT_CT); CME's summary PDF and the ZN service range for the holiday start on the Sunday. In 2019-2022 CME's schedules show the regular 16:00 CT rates close on this Friday. Bar check: validated against CME schedules only, bar check pending the step 2 purchase.
- 2023-12-22: Friday before Christmas 2023: CME settled rates at 12:00 CT (EARLY_SETTLEMENT_CT). CME's Christmas 2023 summary PDF and the ZN service range start on Monday 2023-12-25. In 2021 and 2022 the same day kept the regular 16:00 CT rates close. Bar check: validated against CME schedules only, bar check pending the step 2 purchase.
- 2023-12-29: Friday before New Year's Day 2024: CME settled rates at 12:00 CT (EARLY_SETTLEMENT_CT). CME's New Year 2024 summary PDF and the ZN service range start on 2023-12-31/2024-01-01. In 2019-2022 and 2024-2025 New Year's Eve kept the regular 16:00 CT rates close. Bar check: validated against CME schedules only, bar check pending the step 2 purchase.
- 2024-05-24: Friday before Memorial Day: CME settled rates at 12:00 CT (EARLY_SETTLEMENT_CT); CME's summary PDF and the ZN service range for the holiday start on the Sunday. In 2019-2022 CME's schedules show the regular 16:00 CT rates close on this Friday. Bar check: validated against CME schedules only; embargo or holdout-2 date, never checked against bars.
- 2025-05-23: Friday before Memorial Day: CME settled rates at 12:00 CT (EARLY_SETTLEMENT_CT); CME's summary PDF and the ZN service range for the holiday start on the Sunday. In 2019-2022 CME's schedules show the regular 16:00 CT rates close on this Friday. Bar check: pending Task 7 (research-window bars).
- 2026-05-22: Friday before Memorial Day: CME settled rates at 12:00 CT (EARLY_SETTLEMENT_CT); CME's summary PDF and the ZN service range for the holiday start on the Sunday. In 2019-2022 CME's schedules show the regular 16:00 CT rates close on this Friday. Bar check: pending Task 7 (research-window bars).

## Session-hour changes found

None. One `SessionSpec` covers 2019-05-01..2026-06-19: Sunday-Friday 17:00-16:00 CT with the
16:00-17:00 CT daily break (segment: prior day 17:00 CT to trade date 16:00 CT).

- CME's ZN contract specifications, Wayback capture 2019-07-19: "Trading Hours Sunday - Friday
  6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. CT) with a 60-minute break each day beginning at
  5:00 p.m. (4:00 p.m. CT)". Capture 2026-04-12: "Trading Hours CME Globex: Sunday - Friday
  6:00 p.m. - 5:00 p.m.ET".
- CME's own holiday documents show the same regular close and reopen at both ends of the window
  (2019 Globex schedules: 'Regular Fri. Close' 16:00, Sunday 'Open' 17:00; 2026 ZN service record
  for a regular day: closed 16:00, preopen 16:45, open 17:00).
- Firecrawl searches of cmegroup.com (Globex notices, SERs) for a Treasury-futures hours change in
  2019-2026 returned nothing relevant. This is a search-based negative, not an exhaustive read of
  CME's notice archive.
- CME's 2019 contract specifications of the other five products state the same hours (ZT, ZF, ZB:
  "Trading Hours SUN - FRI: 5:00 p.m. - 4:00 p.m."; UB: "Sunday - Friday 5:00 p.m. - 4:00 p.m. CT
  with a 60-minute break each day beginning at 4:00 p.m."; TN: "Sunday - Friday 6:00 p.m. - 5:00
  p.m. New York time/ET (5:00 p.m. - 4:00 p.m. Chicago Time/CT)"). Every CME holiday document read
  treats interest-rate products as one row.

## D6 confirmation (rates: O 07:20, C 14:00, F 15:08 CT)

- **C 14:00 CT: confirmed.** CME's settlement procedure for Treasury futures, on its client wiki
  page 'Treasuries' (Wayback capture 2019-10-19 of the version last modified 2018-08-02, and the
  current version 6 of 2025-10-21 read through the Confluence REST API), names ZT, ZF, ZN, TN, ZB
  and UB (plus Z3N, and TWE in 2025) and states: "If the lead month contract trades on Globex
  between 13:59:30 and 14:00:00 Central Time (CT), the settlement period, then the lead month
  settles to the volume-weighted average price (VWAP) of those trade(s)." One procedure covers
  all six products, so no sub-group differs.
- **O 07:20 CT: not confirmable, flagged for the lead.** No CME document retrieved publishes
  07:20 CT for Treasury futures. The 2019 and 2026 ZN contract specifications list Globex hours
  only (17:00-16:00 CT), with no open-outcry session, and CME's settlement procedure defines only
  the 13:59:30-14:00:00 CT window, not an open. 07:20 CT is the conventional (former CBOT pit)
  Treasury day-session open; that history was not verified from a retrieved document here
  [unverified]. D6's value is encoded unchanged (`day_session_ct` = (07:20, 14:00) for every rates
  product), and the discrepancy is recorded in the SessionSpec note. The lead rules.
- **F 15:08 CT:** Topstep's flatten time (D9.1), not a CME time; rates trade until 16:00 CT, so
  the 15:10 CT TopstepX cutoff binds. On early-close days D9.1 gives F = early close minus 15 min
  (12:15 CT closes give 12:00 CT; the 10:15 CT Good Friday closes give 10:00 CT).
- **Settlement moves on pre-holiday days (for the lead).** CME published a rates settlement time
  other than 14:00 CT on every pre-holiday day its notices cover (table EARLY_SETTLEMENT_CT above):
  12:00 CT on the eve of Independence Day, Christmas Eve or the last business day before
  Christmas, New Year's Eve, the Thursday before Good Friday, the Friday before Memorial Day
  (where fetched) and the day after Thanksgiving; 10:00 CT on the jobs-report Good Fridays. On most
  of these days Globex rates traded their regular hours to 16:00 CT (no calendar entry). D6's C is
  the settlement time, so a port using C = 14:00 CT on those days sits two hours after CME's
  settlement. Whether C moves on those days is a design decision; the module only records the
  dates and times, and nothing reads them.

## Entries not graded cme/cme, and why

No entry is graded "unverified". Status is "cme" for every entry.

- 2023-01-16 Martin Luther King Jr. Day and 2023-02-20 Presidents Day: time "secondary". CME's
  settlement notices state the holiday (no settlement), but no CME Globex-hours document for these
  dates was retrievable: CME's 2023 summary PDFs for them have only 404 captures, and the ZN
  service capture of 2024-07-08 returns empty event lists for 2023-01..07. The 12:00 CT halt comes
  from AMP Futures (quoting CME's Globex Control Center; its embedded image of CME's schedule shows
  the 'Interest Rate' row HALT 12:00 CST, OPEN 17:00 CST, read visually and not
  script-checkable). The halt-versus-closure distinction also rests on AMP. Every CME-documented
  MLK Day and Presidents Day in 2019-2026 has the same 12:00 CT rates halt.
- 2023-04-07 Good Friday (abbreviated, jobs report): time "inferred". CME's settlement notice
  gives "CME Group Interest Rate Products 10:00 am CT" with unique settlements for trade date
  April 7, and CME's clearing advisory says rates were settled that day. The 10:15 CT close is
  inferred from the 10:00 CT settlement, from the same settle-10:00 / close-10:15 pattern in CME's
  own 2021 Globex schedule and 2026 ZN record, and from AMP's image of the CME schedule (Interest
  Rate CLOSE 10:15 CST, secondary).

## Gaps

- **2023-12-22 and 2023-12-29** (the Fridays before Christmas 2023 and New Year's Day 2024): CME
  settled rates at 12:00 CT, but no CME Globex-hours document covers these days (the summary PDFs
  and service ranges start the following Sunday or Monday). In 2021 and 2022 the same days kept the
  regular 16:00 CT rates close. No entry; listed in GLOBEX_HOURS_UNDOCUMENTED for the bar check
  (both fall in the 2019-05..2024-02 window).
- **Friday before Memorial Day 2023-2026** (2023-05-26, 2024-05-24, 2025-05-23, 2026-05-22): CME
  settled rates at 12:00 CT, but no CME Globex-hours document covers these Fridays (the holiday
  summary PDF and service ranges start on the Sunday). 2019-2022 CME schedules show the regular
  16:00 CT rates close on this Friday. No entry; listed in GLOBEX_HOURS_UNDOCUMENTED for the bar
  check (2024-05-24 is a holdout-2 date and can never be checked; 2025-05-23 and 2026-05-22 fall in
  the research window, Task 7).
- **Thursday 2023-04-06** (before the 2023 Good Friday): no CME Globex-hours document and no CME
  settlement notice for the Thursday were retrieved; AMP's image of the CME schedule shows 'Regular
  @ 16:00 CST' (secondary). No entry, not listed.
- **2022 H2 schedules are CME's preliminary sheets**: Labor Day, Thanksgiving and Christmas 2022
  and New Year 2023 say 'Updated 6/29/2022' (or 6/29/22) and were captured 2022-07-04; no later
  capture was retrieved (the CDX listing requests were refused), so a later CME revision cannot be
  excluded. Their times match every other year.
- **2023 January-August**: only CME's summary PDFs (Memorial Day, Juneteenth, Independence Day)
  and settlement notices exist in the archive; MLK Day, Presidents Day and Good Friday 2023 are the
  three graded entries above.
- **Columbus Day and Veterans Day**: bond-market (SIFMA) holidays, not CME holidays. CME's 2019
  notices say every product settles at its normal time; 2020-2025 notices were not re-fetched.
- **Juneteenth 2021** (federal holiday observed Friday 2021-06-18): no CME holiday schedule for it
  exists in the 2021 archive; no entry, and no CME statement for that day was retrieved.
- **2020-12-24 settlement notice**: its only capture is a 404; that day's Globex hours come from
  the 2020 schedule regardless.
- **Unscheduled outages**: only the 2025-11-28 outage was found, because the ZN service record for
  that holiday range was re-captured after it. Outages outside the holiday windows read here were
  not searched for systematically; the bar check will show any as unlisted closures.
- **Product coverage**: 2023-09..2026-06 entries rest on the ZN record, earlier ones on CME's
  asset-class rows; ZT, ZF, TN, ZB and UB are assumed to share them.
- **Outside the window**: the 2026-06-19 capture of the ZN record shows an odd event for Saturday
  2026-06-20 (open 05:00 and closed 17:00, trading date 2026-06-22); not used.

## Items for the lead

1. D6's O = 07:20 CT is not a CME-published time; D6's C = 14:00 CT is confirmed; C on
   early-settlement days is open (section D6 confirmation).
2. The 2025-11-28 CME Globex outage (no rates trading until 07:30 CT; stop time unknown) affects
   every group. `data/cme_calendar.py` does not record it. The interface extension here is
   `LateOpen` / `LATE_OPENS`.
3. `SessionSpec.day_session_ct` is keyed by product code here ('ZT', ..., 'UB'); other builders may
   key by sub-group name. The convention needs aligning across modules.
4. Juneteenth 2026-06-19 (a Friday): CME's ZN record books the Thursday 17:00 to Friday 12:00
   session to trade date Monday 2026-06-22. The module keeps 2026-06-19 as its own short trade date
   (the data.cme_calendar convention). A Firecrawl search result listed a CME Globex notice of
   June 1, 2026 on aligning Globex and Clearing trade dates when the Globex trade date falls on a
   Friday US holiday; it was not fetched or read [unverified].
5. Rates differ from equities on eve days: the day after Thanksgiving and Christmas Eve close at
   12:15 CT (not 12:00), and rates keep the regular 16:00 CT close on the eve of Independence Day,
   New Year's Eve and the Thursday before Good Friday, where equities close early.
6. `data/calendars/rates.py` is about 2,200 lines, mostly verbatim quotes in its citation tables:
   over the repository's 800-line file guideline, but the brief allows only this one module file.

## Corroborating evidence (not the cited source of an entry)

- 2021-04-02 CME clearing advisory: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-good-friday-advisory.pdf (Wayback 20210517110023, sha256 `255d42a95643303a...`, verbatim True): "FX & Interest Rate markets will be settled on April 2nd". Interest rates traded and settled on the jobs-report Good Friday.
- 2023-04-07 CME clearing advisory: https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-good-friday-advisory.pdf (Wayback 20230203065333, sha256 `2faa51cf54f97c30...`, verbatim True): "FX & Interest Rate markets will be settled on April 7th". Interest rates traded and settled on the jobs-report Good Friday.
- 2026-04-03 CME clearing advisory: https://www.cmegroup.com/tools-information/holiday-calendar/files/2026/2026-good-friday-clearing-advisory.pdf (Wayback 20260202002306, sha256 `0600518164173820...`, verbatim True): "FX & Interest Rate markets will be settled on April 3rd". Interest rates traded and settled on the jobs-report Good Friday (the PDF carries zero-width characters, removed by the normalization).
- 2023-01-16 CME clearing advisory: https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-mlk-day-advisory.pdf (Wayback 20230203071256, sha256 `2338a383ea4d4324...`, verbatim True): "SUBJECT: HOLIDAY SCHEDULE – Dr. Martin Luther King, Jr., January 16, 2023". Holiday processing (no intraday cycle, prices carried forward from Friday); no Globex hours.
- 2023-01-16 AMP image of the CME schedule (secondary): https://www.ampfutures.com/hubfs/CME%20Holiday%20Trading%20Schedule%20-%20Dr.%20Martin%20Luther%20King%2c%20Jr.%20(2023).png (direct, sha256 `09e7f123df0f99e6...`, verbatim False): "Interest Rate | Regular @ 16:00 CST | Regular @ 17:00 CST | 12:00 CST | 17:00 CST | Regular @ 16:00 CST". Image read visually by the builder, not script-checkable. Columns: Friday Jan 13 CLOSE, Sunday Jan 15 OPEN, Monday Jan 16 HALT, Monday Jan 16 OPEN, Tuesday Jan 17 CLOSE.
- 2023-02-20 AMP image of the CME schedule (secondary): https://www.ampfutures.com/hubfs/CME%20Holiday%20Schedule%20-%20Presidents%20Day%20-%202023.png (direct, sha256 `3e96095996fe3847...`, verbatim False): "Interest Rate | Regular @ 17:00 CST | 12:00 CST | 17:00 CST | Regular @ 16:00 CST". Image read visually, not script-checkable. Columns: Sunday Feb 19 OPEN, Monday Feb 20 HALT, Monday Feb 20 OPEN, Tuesday Feb 21 CLOSE.
- 2023-04-07 AMP image of the CME schedule (secondary): https://www.ampfutures.com/hubfs/CME%20Group%20Globex%20-%20Good%20Friday%20Holiday%20Schedule%206%20-%207%20April%202023.png (direct, sha256 `ca781a391045087d...`, verbatim False): "Interest Rate | Regular @ 16:00 CST | 10:15 CST". Image read visually, not script-checkable. Columns: Thursday 6 Apr CLOSE, Friday 7 Apr 2023 CLOSE.
- 2025-11-28 CNBC (secondary): https://www.cnbc.com/2025/11/28/cme-halts-fx-commodities-futures-trading-after-data-center-issue.html (direct, sha256 `00b16be6d7ea16c6...`, verbatim True): "Earlier, representatives for CME Group had told CNBC markets were halted due to a cooling issue at CyrusOne data centers". Outage status; no halt start time. The same article: 'Bonds and metals resumed trading after a pause, according to FactSet data'.

## Session sources

- settlement_2019: https://www.cmegroup.com/confluence/display/EPICSANDBOX/Treasuries (Wayback 20191019155644, verbatim True): "last modified by Confluence Admin on Aug 02, 2018 ... Daily settlement of 2-Year U.S. Treasury Note futures (ZT), 3-Year U.S. Treasury Note futures (Z3N), 5-Year U.S. Treasury Note futures (ZF), 10-Year U.S. Treasury Note futures (ZN), U.S. Treasury Bond futures (ZB), Ultra 10-Year U.S. Treasury Note futures (TN) and Ultra T-Bond futures (UB) is determined by CME Group staff based on trading activity on CME Globex. ... Tier 1: If the lead month contract trades on Globex between 13:59:30 and 14:00:00 Central Time (CT), the settlement period, then the lead month settles to the volume-weighted average price (VWAP) of those trade(s).". CME Group Client Systems Wiki page 'Treasuries' (CME's settlement procedures), Wayback capture 2019-10-19 of the page last modified 2018-08-02.
- settlement_2025: https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457219006?expand=body.storage,version,history (direct, verbatim True): "Daily settlement of 2-Year U.S. Treasury Note futures (ZT), 3-Year U.S. Treasury Note futures (Z3N), 5-Year U.S. Treasury Note futures (ZF), 10-Year U.S. Treasury Note futures (ZN), U.S. Treasury Bond futures (ZB), Ultra 10-Year U.S. Treasury Note futures (TN) 20-Year U.S. Treasury Bond futures (TWE) and Ultra T-Bond futures (UB) is determined by CME Group staff based on trading activity on CME Globex. ... If the lead month contract trades on Globex between 13:59:30 and 14:00:00 Central Time (CT), the settlement period". Same page on CME's client wiki (cmegroupclientsite.atlassian.net, page 457219006, created 2024-12-21, version 6 of 2025-10-21), read directly through the Confluence REST API on 2026-09-25.
- hours_2019: https://www.cmegroup.com/trading/interest-rates/us-treasury/10-year-us-treasury-note_contract_specifications.html (Wayback 20190719191052, verbatim True): "Trading Hours Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. CT) with a 60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)". CME contract specifications for 10-Year T-Note futures (ZN), Wayback capture 2019-07-19. The page lists Globex hours only (no open-outcry session).
- hours_2026: https://www.cmegroup.com/markets/interest-rates/us-treasury/10-year-us-treasury-note.contractSpecs.html (Wayback 20260412090601, verbatim True): "Trading Hours CME Globex: Sunday - Friday 6:00 p.m. - 5:00 p.m.ET". CME contract specifications for ZN, Wayback capture 2026-04-12 (hours in ET: 17:00-16:00 CT).
- hours_2019_schedule: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (Wayback 20210126094837, verbatim True): "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM". CME 2019 Globex holiday schedule: the rates Friday close 16:00 ('Regular Fri. Close') and Sunday 17:00 open.
- hours_2026_service: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068 (Wayback 20260129012143, verbatim True): "{"groupCode":"ZN","eventDate":"2026-01-20","events":[{"tradingDate":"2026-01-20","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-01-21","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2026-01-21","eventTime":"17:00","marketEventType":"open"}]}". CME trading-hours service, ZN, a regular day in 2026: close 16:00, preopen 16:45, open 17:00 CT.
- hours_2019_zt: https://www.cmegroup.com/trading/interest-rates/us-treasury/2-year-us-treasury-note_contract_specifications.html (Wayback 20190806094839, verbatim True): "Trading Hours SUN - FRI: 5:00 p.m. - 4:00 p.m.". CME contract specifications for 2-Year T-Note futures (ZT), Wayback capture 2019-08-06.
- hours_2019_zf: https://www.cmegroup.com/trading/interest-rates/us-treasury/5-year-us-treasury-note_contract_specifications.html (Wayback 20190719015531, verbatim True): "Trading Hours SUN - FRI: 5:00 p.m. - 4:00 p.m.". CME contract specifications for 5-Year T-Note futures (ZF), Wayback capture 2019-07-19.
- hours_2019_zb: https://www.cmegroup.com/trading/interest-rates/us-treasury/30-year-us-treasury-bond_contract_specifications.html (Wayback 20190806095430, verbatim True): "Trading Hours SUN - FRI: 5:00 p.m. - 4:00 p.m.". CME contract specifications for U.S. Treasury Bond futures (ZB), Wayback capture 2019-08-06.
- hours_2019_ub: https://www.cmegroup.com/trading/interest-rates/us-treasury/ultra-t-bond_contract_specifications.html (Wayback 20190923135706, verbatim True): "Trading Hours Sunday - Friday 5:00 p.m. - 4:00 p.m. CT with a 60-minute break each day beginning at 4:00 p.m.". CME contract specifications for Ultra U.S. Treasury Bond futures (UB), Wayback capture 2019-09-23.
- hours_2019_tn: https://www.cmegroup.com/trading/interest-rates/us-treasury/ultra-10-year-us-treasury-note_contract_specifications.html (Wayback 20190721144945, verbatim True): "Trading Hours Sunday - Friday 6:00 p.m. - 5:00 p.m. New York time/ET (5:00 p.m. - 4:00 p.m. Chicago Time/CT).". CME contract specifications for Ultra 10-Year T-Note futures (TN), Wayback capture 2019-07-21.

## Fetch log (PDT)

Every fetch attempt by CalendarBuilder-Rates, including cache reuses and refused connections (Wayback refused this IP or returned 503 repeatedly while several builders fetched in parallel; each refusal was retried after 45-135 s). WebSearch was not used (no budget notice seen). Firecrawl search (not a fetch; no times logged individually, all between 00:30 and 01:00 PDT) was used eight times to locate URLs: CME Treasury settlement procedure (two queries), Treasury Globex hours changes (two), Good Friday 2023 schedule, AMP 2023 MLK/Presidents pages, and the 2025-11-28 outage (two, including one restricted to cmegroup.com notices).

| Time (PDT) | URL | Result |
|---|---|---|
| 00:25:37 | https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | OK 200 application/zip 742628 sha256=1e861e355238903b -> rates_2019-holiday-calendars.zip |
| 00:25:38 | https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | OK 200 application/zip 305220 sha256=5263a4a5e9076bc0 -> rates_2020-holiday-calendars.zip |
| 00:25:38 | https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | OK 200 application/zip 302047 sha256=0ee0860a3a0e035e -> rates_2021-holiday-calendars.zip |
| 00:29:17 | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule.xls&output=json&fl=timestamp,statuscode,digest,length&filter=statuscode:200 | cdx attempt 0 http 503; backing off |
| 00:29:47 | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule.xls&output=json&fl=timestamp,statuscode,digest,length&filter=statuscode:200 | cdx attempt 1 http 503; backing off |
| 00:30:47 | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule.xls&output=json&fl=timestamp,statuscode,digest,length&filter=statuscode:200 | cdx attempt 2 http 000; backing off |
| 00:32:54 | https://web.archive.org/web/20220117212230id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule.xls | OK 200 application/vnd.ms-excel 102912B sha256=896944fa701062e2 -> rates_2022-mlk-day-holiday-schedule.xls |
| 00:33:03 | https://web.archive.org/web/20220704073810id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule.xls | OK 200 application/vnd.ms-excel 105472B sha256=07932975d04ccaba -> rates_2022-presidents-day-holiday-schedule.xls |
| 00:33:12 | https://web.archive.org/web/20220704065501id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule.xls | OK 200 application/vnd.ms-excel 78848B sha256=a82936ab14d1b1f7 -> rates_2022-good-friday-holiday-schedule.xls |
| 00:33:17 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457219006?expand=body.storage,version,history | OK 200 application/json 13780B sha256=2186c51f9818b438 -> rates_cmewiki_treasuries_457219006.json |
| 00:33:22 | https://web.archive.org/web/20220704065438id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule.xls | OK 200 application/vnd.ms-excel 108032B sha256=0d1b1f89a315cae2 -> rates_2022-memorial-day-holiday-schedule.xls |
| 00:33:30 | https://web.archive.org/web/20220620200210id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls | OK 200 application/vnd.ms-excel 124928B sha256=bc9f2caf26a73a13 -> rates_2022-juneteenth-holiday-schedule.xls |
| 00:33:39 | https://web.archive.org/web/20220630id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls | FAILED http 000  |
| 00:34:24 | https://web.archive.org/web/20220630id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls | FAILED http 000  |
| 00:35:31 | https://web.archive.org/web/20220630id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls | reused cache web.archive.org_web_20220704065450id__https_www.cmegroup.com_tools-information_holiday-calendar_files_2022-independence-day-holiday-schedule.xls (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20220630id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls | reused cache web.archive.org_web_20220704065450id__https_www.cmegroup.com_tools-information_holiday-calendar_files_2022-independence-day-holiday-schedule.xls (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20220901id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule.xls | reused cache web.archive.org_web_20220704065441id__https_www.cmegroup.com_tools-information_holiday-calendar_files_2022-labor-day-holiday-schedule.xls (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20221121id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls | reused cache web.archive.org_web_20220704065423id__https_www.cmegroup.com_tools-information_holiday-calendar_files_2022-thanksgiving-holiday-schedule.xls (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20221220id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls | reused cache web.archive.org_web_20220704065430id__https_www.cmegroup.com_tools-information_holiday-calendar_files_2022-christmas-holiday-schedule.xls (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20221228id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule.xls | reused cache web.archive.org_web_20220704065501id__https_www.cmegroup.com_tools-information_holiday-calendar_files_2023-new-years-holiday-schedule.xls (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20230420224018id_/https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf | reused cache web.archive.org_web_20230420224018id__https_www.cmegroup.com_trading-hours_files_memorial-day-2023.pdf (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20230613185949id_/https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf | reused cache web.archive.org_web_20230613185949id__https_www.cmegroup.com_trading-hours_files_juneteenth-2023.pdf (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20230627125057id_/https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf | reused cache web.archive.org_web_20230627125057id__https_www.cmegroup.com_trading-hours_files_4th-of-july-2023.pdf (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20230802192446id_/https://www.cmegroup.com/trading-hours/files/labor-day-2023.pdf | reused cache web.archive.org_web_20230802192446id__https_www.cmegroup.com_trading-hours_files_labor-day-2023.pdf (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20231203205929id_/https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf | reused cache fx_20231203205929_thanksgiving-day-2023.pdf (by CalendarBuilder-FX) |
| 00:35:40 | https://web.archive.org/web/20260719095248id_/https://www.cmegroup.com/trading-hours/files/christmas-day-2023.pdf | reused cache web.archive.org_web_20260719095248id__https_www.cmegroup.com_trading-hours_files_christmas-day-2023.pdf (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20260811165716id_/https://www.cmegroup.com/trading-hours/files/new-years-day-2024.pdf | reused cache web.archive.org_web_20260811165716id__https_www.cmegroup.com_trading-hours_files_new-years-day-2024.pdf (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20250218194143id_/https://www.cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf | reused cache web.archive.org_web_20250218194143id__https_www.cmegroup.com_trading-hours_files_day-of-mourning-january-9-2024.pdf (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-01-15&toEventDate=2023-01-17&isProtected&_t=1720455278636 | reused cache web.archive.org_web_20240708161438id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__7c71810086e57_isProtected__t_1720455278636 (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-02-19&toEventDate=2023-02-21&isProtected&_t=1720455278640 | reused cache web.archive.org_web_20240708161438id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__5046f265ed801_isProtected__t_1720455278640 (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-04-06&toEventDate=2023-04-08&isProtected&_t=1720455278642 | reused cache web.archive.org_web_20240708161438id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__e020ebe4561c8_isProtected__t_1720455278642 (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-05-28&toEventDate=2023-05-30&isProtected&_t=1720455278644 | reused cache web.archive.org_web_20240708161438id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__e8c3b8b6fce60_isProtected__t_1720455278644 (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-06-18&toEventDate=2023-06-20&isProtected&_t=1720455278646 | reused cache fx_20240708161438_trading-hours-by-product_7a80c989b1 (by CalendarBuilder-FX) |
| 00:35:40 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-07-03&toEventDate=2023-07-05&isProtected&_t=1720455278650 | reused cache web.archive.org_web_20240708161438id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__227d55ea3f575_isProtected__t_1720455278650 (by CalendarBuilder-Energy) |
| 00:35:40 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-09-03&toEventDate=2023-09-05&isProtected&_t=1720455278654 | reused cache fx_20240708161439_trading-hours-by-product_9b2a67ddaf (by CalendarBuilder-FX) |
| 00:35:40 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-11-22&toEventDate=2023-11-24&isProtected&_t=1720455278656 | reused cache fx_20240708161439_trading-hours-by-product_602f419fc0 (by CalendarBuilder-FX) |
| 00:35:40 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-24&toEventDate=2023-12-26&isProtected&_t=1720455278659 | reused cache fx_20240708161439_trading-hours-by-product_0ed27ee990 (by CalendarBuilder-FX) |
| 00:35:41 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-31&toEventDate=2024-01-02&isProtected&_t=1720455278661 | OK 200 application/json 945B sha256=fdf3a5d8938743d5 -> rates_thbp_2023-12-31_20240708.json |
| 00:35:51 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663 | reused cache fx_20240708161439_trading-hours-by-product_04a907ec69 (by CalendarBuilder-FX) |
| 00:35:51 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669 | FAILED http 000  |
| 00:36:36 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669 | reused cache fx_20240708161439_trading-hours-by-product_8a620697b6 (by CalendarBuilder-FX) |
| 00:36:46 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-03-28&toEventDate=2024-03-30&isProtected&_t=1720455278672 | reused cache fx_20240708161439_trading-hours-by-product_5b48ce4e20 (by CalendarBuilder-FX) |
| 00:36:46 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675 | reused cache fx_20240708161439_trading-hours-by-product_e5cdda2a10 (by CalendarBuilder-FX) |
| 00:36:46 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677 | reused cache fx_20240708161439_trading-hours-by-product_432f73e829 (by CalendarBuilder-FX) |
| 00:36:46 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680 | reused cache fx_20240708161439_trading-hours-by-product_f7f641838f (by CalendarBuilder-FX) |
| 00:36:46 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1720455278683 | reused cache fx_20240708161439_trading-hours-by-product_864da3e9b3 (by CalendarBuilder-FX) |
| 00:36:46 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1720455278685 | reused cache fx_20240708161439_trading-hours-by-product_616ec0c44f (by CalendarBuilder-FX) |
| 00:36:46 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1720455278686 | reused cache fx_20240708161439_trading-hours-by-product_45e1192226 (by CalendarBuilder-FX) |
| 00:36:46 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1720455278688 | reused cache fx_20240708161439_trading-hours-by-product_d2ef5fa1ac (by CalendarBuilder-FX) |
| 00:36:46 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539 | reused cache fx_20241220155340_trading-hours-by-product_7ef709d3da (by CalendarBuilder-FX) |
| 00:36:46 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540 | reused cache fx_20241220155340_trading-hours-by-product_8e5d7c14f8 (by CalendarBuilder-FX) |
| 00:36:46 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-04-17&toEventDate=2025-04-19&isProtected&_t=1734710019542 | reused cache fx_20241220155340_trading-hours-by-product_5a3b303832 (by CalendarBuilder-FX) |
| 00:36:46 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543 | OK 200 application/json 973B sha256=73d01c7c3c0cd47c -> rates_thbp_2025-05-25_20241220.json |
| 00:36:56 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544 | FAILED http 000  |
| 00:37:42 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544 | OK 200 application/json 1039B sha256=7dcceaa759e98885 -> rates_thbp_2025-06-18_20241220.json |
| 00:37:52 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545 | FAILED http 000  |
| 00:38:08 | https://www.ampfutures.com/news/holiday-trading-schedule-good-friday-2023 | OK 200 text/html; charset=UTF-8 92579B sha256=afb303ac9b65272b -> rates_amp_good_friday_2023.html |
| 00:38:09 | https://www.ampfutures.com/news/holiday-trading-schedule-good-friday-2021 | OK 200 text/html; charset=UTF-8 92517B sha256=4bff76c538773296 -> rates_amp_good_friday_2021.html |
| 00:38:42 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-01-15&toEventDate=2023-01-17&isProtected&_t=1720455278636 | reused cache web.archive.org_web_20240708161438id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__7c71810086e57_isProtected__t_1720455278636 (by CalendarBuilder-Energy) |
| 00:38:42 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-02-19&toEventDate=2023-02-21&isProtected&_t=1720455278640 | reused cache web.archive.org_web_20240708161438id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__5046f265ed801_isProtected__t_1720455278640 (by CalendarBuilder-Energy) |
| 00:38:42 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-04-06&toEventDate=2023-04-08&isProtected&_t=1720455278642 | reused cache web.archive.org_web_20240708161438id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__e020ebe4561c8_isProtected__t_1720455278642 (by CalendarBuilder-Energy) |
| 00:38:42 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-05-28&toEventDate=2023-05-30&isProtected&_t=1720455278644 | reused cache web.archive.org_web_20240708161438id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__e8c3b8b6fce60_isProtected__t_1720455278644 (by CalendarBuilder-Energy) |
| 00:38:42 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-06-18&toEventDate=2023-06-20&isProtected&_t=1720455278646 | reused cache fx_20240708161438_trading-hours-by-product_7a80c989b1 (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-07-03&toEventDate=2023-07-05&isProtected&_t=1720455278650 | reused cache web.archive.org_web_20240708161438id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__227d55ea3f575_isProtected__t_1720455278650 (by CalendarBuilder-Energy) |
| 00:38:42 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-09-03&toEventDate=2023-09-05&isProtected&_t=1720455278654 | reused cache fx_20240708161439_trading-hours-by-product_9b2a67ddaf (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-11-22&toEventDate=2023-11-24&isProtected&_t=1720455278656 | reused cache fx_20240708161439_trading-hours-by-product_602f419fc0 (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-24&toEventDate=2023-12-26&isProtected&_t=1720455278659 | reused cache fx_20240708161439_trading-hours-by-product_0ed27ee990 (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-31&toEventDate=2024-01-02&isProtected&_t=1720455278661 | reused cache fx_20240708161439_trading-hours-by-product_ce6eed9111 (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663 | reused cache fx_20240708161439_trading-hours-by-product_04a907ec69 (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669 | reused cache fx_20240708161439_trading-hours-by-product_8a620697b6 (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-03-28&toEventDate=2024-03-30&isProtected&_t=1720455278672 | reused cache fx_20240708161439_trading-hours-by-product_5b48ce4e20 (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675 | reused cache fx_20240708161439_trading-hours-by-product_e5cdda2a10 (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677 | reused cache fx_20240708161439_trading-hours-by-product_432f73e829 (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680 | reused cache fx_20240708161439_trading-hours-by-product_f7f641838f (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1720455278683 | reused cache fx_20240708161439_trading-hours-by-product_864da3e9b3 (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1720455278685 | reused cache fx_20240708161439_trading-hours-by-product_616ec0c44f (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1720455278686 | reused cache fx_20240708161439_trading-hours-by-product_45e1192226 (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1720455278688 | reused cache fx_20240708161439_trading-hours-by-product_d2ef5fa1ac (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539 | reused cache fx_20241220155340_trading-hours-by-product_7ef709d3da (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540 | reused cache fx_20241220155340_trading-hours-by-product_8e5d7c14f8 (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-04-17&toEventDate=2025-04-19&isProtected&_t=1734710019542 | reused cache fx_20241220155340_trading-hours-by-product_5a3b303832 (by CalendarBuilder-FX) |
| 00:38:42 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543 | reused cache rates_thbp_2025-05-25_20241220.json (by CalendarBuilder-Rates) |
| 00:38:42 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544 | reused cache rates_thbp_2025-06-18_20241220.json (by CalendarBuilder-Rates) |
| 00:38:43 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545 | OK 200 application/json 965B sha256=cd4008266d438752 -> rates_thbp_2025-07-03_20241220.json |
| 00:38:53 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546 | reused cache web.archive.org_web_20241220155340id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__2b6c12db2b162_isProtected__t_1734710019546 (by CalendarBuilder-Energy) |
| 00:38:53 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1734710019547 | FAILED http 000  |
| 00:39:38 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1734710019547 | reused cache web.archive.org_web_20241220155340id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__6771bf99e47a8_isProtected__t_1734710019547 (by CalendarBuilder-Energy) |
| 00:39:48 | https://web.archive.org/web/20241220155341id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1734710019548 | reused cache web.archive.org_web_20241220155341id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__008a50c3b82e6_isProtected__t_1734710019548 (by CalendarBuilder-Energy) |
| 00:39:48 | https://web.archive.org/web/20241220155341id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1734710019549 | reused cache web.archive.org_web_20241220155341id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__d1d64fcb803c2_isProtected__t_1734710019549 (by CalendarBuilder-Energy) |
| 00:39:49 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068 | OK 200 application/json 969B sha256=f8b1f22d11e3465a -> rates_thbp_2026-01-18_20260129.json |
| 00:39:59 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1769649703070 | FAILED http 000  |
| 00:40:44 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1769649703070 | reused cache fx_20260129012143_trading-hours-by-product_dc8d032b21 (by CalendarBuilder-FX) |
| 00:40:54 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1769649703072 | FAILED http 000  |
| 00:41:40 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1769649703072 | OK 200 application/json 1039B sha256=054e91e27350e39e -> rates_thbp_2026-04-01_20260129.json |
| 00:41:50 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1769649703074 | OK 200 application/json 968B sha256=5f08ca1972caf9d0 -> rates_thbp_2026-05-24_20260129.json |
| 00:42:00 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-17&toEventDate=2026-06-19&isProtected&_t=1769649703075 | reused cache fx_20260129012143_trading-hours-by-product_dee33d4dd4 (by CalendarBuilder-FX) |
| 00:42:00 | https://web.archive.org/web/20260619113404id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-18&toEventDate=2026-06-20&isProtected&_t=1749141523693 | reused cache web.archive.org_web_20260619113404id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__ef9068ebc4cb0_isProtected__t_1749141523693 (by CalendarBuilder-Energy) |
| 00:42:00 | https://web.archive.org/web/20210517110023id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-good-friday-advisory.pdf | FAILED http 000  |
| 00:42:46 | https://web.archive.org/web/20210517110023id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-good-friday-advisory.pdf | OK 200 application/pdf 190540B sha256=255d42a95643303a -> rates_hc_2021-good-friday-advisory.pdf |
| 00:42:56 | https://web.archive.org/web/20230203065333id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-good-friday-advisory.pdf | OK 200 application/pdf 173297B sha256=2faa51cf54f97c30 -> rates_hc_2023-good-friday-advisory.pdf |
| 00:43:07 | https://web.archive.org/web/20260202002306id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2026/2026-good-friday-clearing-advisory.pdf | OK 200 application/pdf 90883B sha256=0600518164173820 -> rates_hc_2026_2026-good-friday-clearing-advisory.pdf |
| 00:43:17 | https://web.archive.org/web/20241214010205id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/2025-good-friday-clearing-advisory.pdf | OK 200 application/pdf 99538B sha256=d0baf71a409670a1 -> rates_hc_2025_2025-good-friday-clearing-advisory.pdf |
| 00:43:28 | https://web.archive.org/web/20191019155644id_/https://www.cmegroup.com/confluence/display/EPICSANDBOX/Treasuries | OK 200 text/html;charset=UTF-8 59509B sha256=bb444a865e595deb -> rates_cmewiki_treasuries_2020.html |
| 00:43:38 | https://web.archive.org/web/20190601id_/https://www.cmegroup.com/trading/interest-rates/us-treasury/10-year-us-treasury-note_contract_specifications.html | FAILED http 000  |
| 00:44:08 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060 | reused cache web.archive.org_web_20260129012143id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__5e4055cdf9878_isProtected__t_1769649703060 (by CalendarBuilder-Energy) |
| 00:44:08 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064 | reused cache web.archive.org_web_20260129012143id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__9167c92219a66_isProtected__t_1769649703064 (by CalendarBuilder-Energy) |
| 00:44:08 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066 | reused cache web.archive.org_web_20260129012143id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__9c24401604d32_isProtected__t_1769649703066 (by CalendarBuilder-Energy) |
| 00:44:08 | https://web.archive.org/web/20230203073653id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2023.pdf | reused cache fx_20230203073653_mlk-day-holiday-settlement-times-2023.pdf (by CalendarBuilder-FX) |
| 00:44:08 | https://web.archive.org/web/20230203065411id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2023.pdf | reused cache fx_20230203065411_presidents-day-holiday-settlement-times-2023.pdf (by CalendarBuilder-FX) |
| 00:44:08 | https://web.archive.org/web/20230203071256id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-mlk-day-advisory.pdf | reused cache fx_20230203071256_2023-mlk-day-advisory.pdf (by CalendarBuilder-FX) |
| 00:44:08 | https://web.archive.org/web/20230203070709id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-presidents-day-advisory.pdf | reused cache fx_20230203070709_2023-presidents-day-advisory.pdf (by CalendarBuilder-FX) |
| 00:44:08 | https://web.archive.org/web/20230203064614id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/good-friday-holiday-settlement-times-2023.pdf | reused cache fx_20230203064614_good-friday-holiday-settlement-times-2023.pdf (by CalendarBuilder-FX) |
| 00:44:08 | https://web.archive.org/web/20210115184936id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/good-friday-holiday-settlement-times-2021.pdf | FAILED http 000  |
| 00:44:53 | https://web.archive.org/web/20210115184936id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/good-friday-holiday-settlement-times-2021.pdf | OK 200 application/pdf 87787B sha256=626662654758c287 -> rates_hc_good-friday-holiday-settlement-times-2021.pdf |
| 00:45:01 | https://www.ampfutures.com/news/holiday-trading-schedule-martin-luther-king-day-2023 | OK 200 text/html; charset=UTF-8 92833B sha256=b8f1b2ddd823cc5c -> rates_amp_mlk_2023.html |
| 00:45:01 | https://www.ampfutures.com/news/holiday-trading-schedule-presidents-day-2023 | OK 200 text/html; charset=UTF-8 92190B sha256=3d4b417e42dd382e -> rates_amp_presidents_2023.html |
| 00:45:03 | https://web.archive.org/web/20251013214632id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2026/good-friday-holiday-settlement-times-2026.pdf | reused cache fx_20251013214632_good-friday-holiday-settlement-times-2026.pdf (by CalendarBuilder-FX) |
| 00:45:04 | https://web.archive.org/web/20221221043007id_/https://www.cmegroup.com/trading-hours.html | OK 200 text/html; charset=UTF-8 18612B sha256=9519505135d389ef -> rates_trading-hours_20230110.html |
| 00:45:12 | https://www.ampfutures.com/hubfs/CME%20Holiday%20Trading%20Schedule%20-%20Dr.%20Martin%20Luther%20King%2c%20Jr.%20(2023).png | OK 200 image/png 117822B sha256=09e7f123df0f99e6 -> rates_amp_mlk_2023.png |
| 00:45:12 | https://www.ampfutures.com/hubfs/CME%20Holiday%20Schedule%20-%20Presidents%20Day%20-%202023.png | OK 200 image/png 110714B sha256=3e96095996fe3847 -> rates_amp_presidents_2023.png |
| 00:45:12 | https://www.ampfutures.com/hubfs/CME%20Group%20Globex%20-%20Good%20Friday%20Holiday%20Schedule%206%20-%207%20April%202023.png | OK 200 image/png 106870B sha256=ca781a391045087d -> rates_amp_good_friday_2023.png |
| 00:45:14 | https://web.archive.org/web/20230215id_/https://www.cmegroup.com/trading-hours.html | FAILED http 000  |
| 00:45:59 | https://web.archive.org/web/20230215id_/https://www.cmegroup.com/trading-hours.html | FAILED http 000  |
| 00:47:01 | https://www.cnbc.com/2025/11/28/cme-halts-fx-commodities-futures-trading-after-data-center-issue.html | OK 200 text/html; charset=utf-8 803439B sha256=00b16be6d7ea16c6 -> rates_cnbc_cme_outage_20251128.html |
| 00:47:30 | https://web.archive.org/web/20230219233358id_/https://www.cmegroup.com/trading-hours.html | OK 200 text/html; charset=UTF-8 142757B sha256=396955aae818135d -> rates_trading-hours_20230215.html |
| 00:47:40 | https://web.archive.org/web/20230403id_/https://www.cmegroup.com/trading-hours.html | FAILED http 000  |
| 00:48:25 | https://web.archive.org/web/20230406195707id_/https://www.cmegroup.com/trading-hours.html | OK 200 text/html; charset=UTF-8 150156B sha256=e623a1fa10192cea -> rates_trading-hours_20230403.html |
| 00:48:35 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-01-15&toEventDate=2023-01-17&isProtected&_t=1720455278636 | reused cache web.archive.org_web_20240708161438id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__7c71810086e57_isProtected__t_1720455278636 (by CalendarBuilder-Energy) |
| 00:48:35 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-02-19&toEventDate=2023-02-21&isProtected&_t=1720455278640 | reused cache web.archive.org_web_20240708161438id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__5046f265ed801_isProtected__t_1720455278640 (by CalendarBuilder-Energy) |
| 00:48:35 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-04-06&toEventDate=2023-04-08&isProtected&_t=1720455278642 | reused cache web.archive.org_web_20240708161438id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__e020ebe4561c8_isProtected__t_1720455278642 (by CalendarBuilder-Energy) |
| 00:48:35 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-05-28&toEventDate=2023-05-30&isProtected&_t=1720455278644 | reused cache web.archive.org_web_20240708161438id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__e8c3b8b6fce60_isProtected__t_1720455278644 (by CalendarBuilder-Energy) |
| 00:48:35 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-06-18&toEventDate=2023-06-20&isProtected&_t=1720455278646 | reused cache fx_20240708161438_trading-hours-by-product_7a80c989b1 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20240708161438id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-07-03&toEventDate=2023-07-05&isProtected&_t=1720455278650 | reused cache web.archive.org_web_20240708161438id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__227d55ea3f575_isProtected__t_1720455278650 (by CalendarBuilder-Energy) |
| 00:48:35 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-09-03&toEventDate=2023-09-05&isProtected&_t=1720455278654 | reused cache fx_20240708161439_trading-hours-by-product_9b2a67ddaf (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-11-22&toEventDate=2023-11-24&isProtected&_t=1720455278656 | reused cache fx_20240708161439_trading-hours-by-product_602f419fc0 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-24&toEventDate=2023-12-26&isProtected&_t=1720455278659 | reused cache fx_20240708161439_trading-hours-by-product_0ed27ee990 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-31&toEventDate=2024-01-02&isProtected&_t=1720455278661 | reused cache fx_20240708161439_trading-hours-by-product_ce6eed9111 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663 | reused cache fx_20240708161439_trading-hours-by-product_04a907ec69 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669 | reused cache fx_20240708161439_trading-hours-by-product_8a620697b6 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-03-28&toEventDate=2024-03-30&isProtected&_t=1720455278672 | reused cache fx_20240708161439_trading-hours-by-product_5b48ce4e20 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675 | reused cache fx_20240708161439_trading-hours-by-product_e5cdda2a10 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677 | reused cache fx_20240708161439_trading-hours-by-product_432f73e829 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680 | reused cache fx_20240708161439_trading-hours-by-product_f7f641838f (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1720455278683 | reused cache fx_20240708161439_trading-hours-by-product_864da3e9b3 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1720455278685 | reused cache fx_20240708161439_trading-hours-by-product_616ec0c44f (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1720455278686 | reused cache fx_20240708161439_trading-hours-by-product_45e1192226 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1720455278688 | reused cache fx_20240708161439_trading-hours-by-product_d2ef5fa1ac (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539 | reused cache fx_20241220155340_trading-hours-by-product_7ef709d3da (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540 | reused cache fx_20241220155340_trading-hours-by-product_8e5d7c14f8 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-04-17&toEventDate=2025-04-19&isProtected&_t=1734710019542 | reused cache fx_20241220155340_trading-hours-by-product_5a3b303832 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543 | reused cache rates_thbp_2025-05-25_20241220.json (by CalendarBuilder-Rates) |
| 00:48:35 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544 | reused cache rates_thbp_2025-06-18_20241220.json (by CalendarBuilder-Rates) |
| 00:48:35 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545 | reused cache web.archive.org_web_20241220155340id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__97e8756208275_isProtected__t_1734710019545 (by CalendarBuilder-Energy) |
| 00:48:35 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546 | reused cache web.archive.org_web_20241220155340id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__2b6c12db2b162_isProtected__t_1734710019546 (by CalendarBuilder-Energy) |
| 00:48:35 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1734710019547 | reused cache web.archive.org_web_20241220155340id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__6771bf99e47a8_isProtected__t_1734710019547 (by CalendarBuilder-Energy) |
| 00:48:35 | https://web.archive.org/web/20241220155341id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1734710019548 | reused cache web.archive.org_web_20241220155341id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__008a50c3b82e6_isProtected__t_1734710019548 (by CalendarBuilder-Energy) |
| 00:48:35 | https://web.archive.org/web/20241220155341id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1734710019549 | reused cache web.archive.org_web_20241220155341id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__d1d64fcb803c2_isProtected__t_1734710019549 (by CalendarBuilder-Energy) |
| 00:48:35 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068 | reused cache rates_thbp_2026-01-18_20260129.json (by CalendarBuilder-Rates) |
| 00:48:35 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1769649703070 | reused cache fx_20260129012143_trading-hours-by-product_dc8d032b21 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1769649703072 | reused cache fx_20260129012143_trading-hours-by-product_f1683e8e37 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1769649703074 | reused cache rates_thbp_2026-05-24_20260129.json (by CalendarBuilder-Rates) |
| 00:48:35 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-17&toEventDate=2026-06-19&isProtected&_t=1769649703075 | reused cache fx_20260129012143_trading-hours-by-product_dee33d4dd4 (by CalendarBuilder-FX) |
| 00:48:35 | https://web.archive.org/web/20260619113404id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-18&toEventDate=2026-06-20&isProtected&_t=1749141523693 | reused cache web.archive.org_web_20260619113404id__https_www.cmegroup.com_services_trading-hours-by-product_id_316_133_425_300_58_437_22_8478_5201_10191__ef9068ebc4cb0_isProtected__t_1749141523693 (by CalendarBuilder-Energy) |
| 00:48:35 | https://web.archive.org/web/20210517110023id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-good-friday-advisory.pdf | reused cache rates_hc_2021-good-friday-advisory.pdf (by CalendarBuilder-Rates) |
| 00:48:35 | https://web.archive.org/web/20230203065333id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-good-friday-advisory.pdf | reused cache rates_hc_2023-good-friday-advisory.pdf (by CalendarBuilder-Rates) |
| 00:48:35 | https://web.archive.org/web/20260202002306id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2026/2026-good-friday-clearing-advisory.pdf | reused cache rates_hc_2026_2026-good-friday-clearing-advisory.pdf (by CalendarBuilder-Rates) |
| 00:48:35 | https://web.archive.org/web/20241214010205id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/2025-good-friday-clearing-advisory.pdf | reused cache rates_hc_2025_2025-good-friday-clearing-advisory.pdf (by CalendarBuilder-Rates) |
| 00:48:35 | https://web.archive.org/web/20200101id_/https://www.cmegroup.com/confluence/display/EPICSANDBOX/Treasuries | reused cache rates_cmewiki_treasuries_2020.html (by CalendarBuilder-Rates) |
| 00:48:35 | https://web.archive.org/web/20190601id_/https://www.cmegroup.com/trading/interest-rates/us-treasury/10-year-us-treasury-note_contract_specifications.html | FAILED http 000  |
| 00:49:20 | https://web.archive.org/web/20190601id_/https://www.cmegroup.com/trading/interest-rates/us-treasury/10-year-us-treasury-note_contract_specifications.html | FAILED http 000  |
| 00:50:50 | https://web.archive.org/web/20190601id_/https://www.cmegroup.com/trading/interest-rates/us-treasury/10-year-us-treasury-note_contract_specifications.html | FAILED http 000  |
| 00:53:07 | https://web.archive.org/web/20190719191052id_/https://www.cmegroup.com/trading/interest-rates/us-treasury/10-year-us-treasury-note_contract_specifications.html | OK 200 text/html; charset=UTF-8 131528B sha256=5b533a05a68d7341 -> rates_spec_zn_2019.html |
| 00:53:18 | https://web.archive.org/web/20260412090601id_/https://www.cmegroup.com/markets/interest-rates/us-treasury/10-year-us-treasury-note.contractSpecs.html | OK 200 text/html; charset=UTF-8 279851B sha256=5f5152e3e67f98e0 -> rates_spec_zn_2026.html |
| 00:53:28 | https://web.archive.org/web/20220630id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls | reused cache web.archive.org_web_20220704065450id__https_www.cmegroup.com_tools-information_holiday-calendar_files_2022-independence-day-holiday-schedule.xls (by CalendarBuilder-Energy) |
| 00:53:28 | https://web.archive.org/web/20220901id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule.xls | reused cache web.archive.org_web_20220704065441id__https_www.cmegroup.com_tools-information_holiday-calendar_files_2022-labor-day-holiday-schedule.xls (by CalendarBuilder-Energy) |
| 00:53:28 | https://web.archive.org/web/20221121id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls | reused cache web.archive.org_web_20220704065423id__https_www.cmegroup.com_tools-information_holiday-calendar_files_2022-thanksgiving-holiday-schedule.xls (by CalendarBuilder-Energy) |
| 00:53:28 | https://web.archive.org/web/20221220id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls | reused cache web.archive.org_web_20220704065430id__https_www.cmegroup.com_tools-information_holiday-calendar_files_2022-christmas-holiday-schedule.xls (by CalendarBuilder-Energy) |
| 00:53:28 | https://web.archive.org/web/20221228id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule.xls | reused cache web.archive.org_web_20220704065501id__https_www.cmegroup.com_tools-information_holiday-calendar_files_2023-new-years-holiday-schedule.xls (by CalendarBuilder-Energy) |
| 00:53:28 | https://web.archive.org/web/20230420224018id_/https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf | reused cache web.archive.org_web_20230420224018id__https_www.cmegroup.com_trading-hours_files_memorial-day-2023.pdf (by CalendarBuilder-Energy) |
| 00:53:28 | https://web.archive.org/web/20230613185949id_/https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf | reused cache web.archive.org_web_20230613185949id__https_www.cmegroup.com_trading-hours_files_juneteenth-2023.pdf (by CalendarBuilder-Energy) |
| 00:53:28 | https://web.archive.org/web/20230627125057id_/https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf | reused cache web.archive.org_web_20230627125057id__https_www.cmegroup.com_trading-hours_files_4th-of-july-2023.pdf (by CalendarBuilder-Energy) |
| 00:53:28 | https://web.archive.org/web/20230802192446id_/https://www.cmegroup.com/trading-hours/files/labor-day-2023.pdf | reused cache web.archive.org_web_20230802192446id__https_www.cmegroup.com_trading-hours_files_labor-day-2023.pdf (by CalendarBuilder-Energy) |
| 00:53:28 | https://web.archive.org/web/20231203205929id_/https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf | reused cache fx_20231203205929_thanksgiving-day-2023.pdf (by CalendarBuilder-FX) |
| 00:53:28 | https://web.archive.org/web/20260719095248id_/https://www.cmegroup.com/trading-hours/files/christmas-day-2023.pdf | reused cache web.archive.org_web_20260719095248id__https_www.cmegroup.com_trading-hours_files_christmas-day-2023.pdf (by CalendarBuilder-Energy) |
| 00:53:28 | https://web.archive.org/web/20260811165716id_/https://www.cmegroup.com/trading-hours/files/new-years-day-2024.pdf | reused cache web.archive.org_web_20260811165716id__https_www.cmegroup.com_trading-hours_files_new-years-day-2024.pdf (by CalendarBuilder-Energy) |
| 00:53:28 | https://web.archive.org/web/20250218194143id_/https://www.cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf | reused cache web.archive.org_web_20250218194143id__https_www.cmegroup.com_trading-hours_files_day-of-mourning-january-9-2024.pdf (by CalendarBuilder-Energy) |
| 00:53:28 | https://web.archive.org/web/20260715054102id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2020.pdf | OK 200 application/pdf 40584B sha256=67b1f845180d1c58 -> rates_hc_fourth-of-july-settlement-times-2020.pdf |
| 00:53:39 | https://web.archive.org/web/20210115184643id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2021.pdf | OK 200 application/pdf 145023B sha256=00e5ea24db3a850c -> rates_hc_fourth-of-july-settlement-times-2021.pdf |
| 00:53:50 | https://web.archive.org/web/20220128024119id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2022.pdf | OK 200 application/pdf 46055B sha256=0b9ad3d58b6b61a7 -> rates_hc_fourth-of-july-settlement-times-2022.pdf |
| 00:54:00 | https://web.archive.org/web/20230203064221id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2023.pdf | reused cache web.archive.org_web_20230203064221id__https_www.cmegroup.com_tools-information_holiday-calendar_files_fourth-of-july-settlement-times-2023.pdf (by CalendarBuilder-Energy) |
| 00:54:00 | https://web.archive.org/web/20231122090808id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/us-independence-day-settlement-times-2024.pdf | reused cache web.archive.org_web_20231122090808id__https_www.cmegroup.com_tools-information_holiday-calendar_files_us-independence-day-settlement-times-2024.pdf (by CalendarBuilder-Energy) |
| 00:54:00 | https://web.archive.org/web/20241212004808id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/us-independence-day-settlement-times-2025.pdf | reused cache web.archive.org_web_20241212004808id__https_www.cmegroup.com_tools-information_holiday-calendar_files_2025_us-independence-day-settlement-times-2025.pdf (by CalendarBuilder-Energy) |
| 00:54:00 | https://web.archive.org/web/20210126094832id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2020.pdf | OK 200 application/pdf 148831B sha256=013fbdd845bbd52a -> rates_hc_thanksgiving-holiday-settlement-times-2020.pdf |
| 00:54:11 | https://web.archive.org/web/20210115184603id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2021.pdf | OK 200 application/pdf 145741B sha256=c834eae8ac3a698c -> rates_hc_thanksgiving-holiday-settlement-times-2021.pdf |
| 00:54:21 | https://web.archive.org/web/20220128023650id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2022.pdf | OK 200 application/pdf 50704B sha256=915d34f0023364fc -> rates_hc_thanksgiving-holiday-settlement-times-2022.pdf |
| 00:54:31 | https://web.archive.org/web/20230203063905id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2023.pdf | reused cache web.archive.org_web_20230203063905id__https_www.cmegroup.com_tools-information_holiday-calendar_files_thanksgiving-holiday-settlement-times-2023.pdf (by CalendarBuilder-Energy) |
| 00:54:31 | https://web.archive.org/web/20231209141725id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2024.pdf | reused cache web.archive.org_web_20231209141725id__https_www.cmegroup.com_tools-information_holiday-calendar_files_thanksgiving-holiday-settlement-times-2024.pdf (by CalendarBuilder-Energy) |
| 00:54:31 | https://web.archive.org/web/20241214004507id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/thanksgiving-holiday-settlement-times-2025.pdf | reused cache fx_20241214004507_thanksgiving-holiday-settlement-times-2025.pdf (by CalendarBuilder-FX) |
| 00:54:34 | https://web.archive.org/web/20210126003901id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2020.pdf | FAILED http 404  |
| 00:54:45 | https://web.archive.org/web/20210115184900id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2021.pdf | OK 200 application/pdf 107581B sha256=178ab6d736518211 -> rates_hc_christmas-holiday-settlement-times-2021.pdf |
| 00:54:55 | https://web.archive.org/web/20220128031516id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2022.pdf | reused cache web.archive.org_web_20220128031516id__https_www.cmegroup.com_tools-information_holiday-calendar_files_christmas-holiday-settlement-times-2022.pdf (by CalendarBuilder-Energy) |
| 00:54:55 | https://web.archive.org/web/20230203075043id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2023.pdf | reused cache fx_20230203075043_christmas-holiday-settlement-times-2023.pdf (by CalendarBuilder-FX) |
| 00:54:55 | https://web.archive.org/web/20231121134649id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2024.pdf | reused cache web.archive.org_web_20231121134649id__https_www.cmegroup.com_tools-information_holiday-calendar_files_christmas-holiday-settlement-times-2024.pdf (by CalendarBuilder-Energy) |
| 00:54:55 | https://web.archive.org/web/20241214020338id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/christmas-holiday-settlement-times-2025.pdf | reused cache fx_20241214020338_christmas-holiday-settlement-times-2025.pdf (by CalendarBuilder-FX) |
| 00:54:57 | https://web.archive.org/web/20260715054802id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/new-years-eve-holiday-settlement-times-2020.pdf | OK 200 application/pdf 100326B sha256=3a6629e87538e5f7 -> rates_hc_new-years-eve-holiday-settlement-times-2020.pdf |
| 00:55:07 | https://web.archive.org/web/20210115181558id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/new-years-eve-holiday-settlement-times-2022.pdf | OK 200 application/pdf 104717B sha256=1b1b6688043dffbe -> rates_hc_new-years-eve-holiday-settlement-times-2022.pdf |
| 00:55:17 | https://web.archive.org/web/20220128021542id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/new-years-eve-holiday-settlement-times-2023.pdf | reused cache web.archive.org_web_20220128021542id__https_www.cmegroup.com_tools-information_holiday-calendar_files_new-years-eve-holiday-settlement-times-2023.pdf (by CalendarBuilder-Energy) |
| 00:55:17 | https://web.archive.org/web/20230203062741id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/new-years-eve-holiday-settlement-times-2024.pdf | reused cache web.archive.org_web_20230203062741id__https_www.cmegroup.com_tools-information_holiday-calendar_files_new-years-eve-holiday-settlement-times-2024.pdf (by CalendarBuilder-Energy) |
| 00:55:17 | https://web.archive.org/web/20231121113308id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/new-years-eve-holiday-settlement-times-2025.pdf | reused cache web.archive.org_web_20231121113308id__https_www.cmegroup.com_tools-information_holiday-calendar_files_new-years-eve-holiday-settlement-times-2025.pdf (by CalendarBuilder-Energy) |
| 00:55:17 | https://web.archive.org/web/20241212000623id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/new-years-eve-holiday-settlement-times-2026.pdf | reused cache web.archive.org_web_20241212000623id__https_www.cmegroup.com_tools-information_holiday-calendar_files_2025_new-years-eve-holiday-settlement-times-2026.pdf (by CalendarBuilder-Energy) |
| 00:55:18 | https://web.archive.org/web/20260715054007id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/good-friday-holiday-settlement-times-2020.pdf | OK 200 application/pdf 31767B sha256=cb5cd68b487bfed0 -> rates_hc_good-friday-holiday-settlement-times-2020.pdf |
| 00:55:28 | https://web.archive.org/web/20210115184936id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/good-friday-holiday-settlement-times-2021.pdf | reused cache rates_hc_good-friday-holiday-settlement-times-2021.pdf (by CalendarBuilder-Rates) |
| 00:55:28 | https://web.archive.org/web/20220128015535id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/good-friday-holiday-settlement-times-2022.pdf | OK 200 application/pdf 30474B sha256=92bc724c6dfa842d -> rates_hc_good-friday-holiday-settlement-times-2022.pdf |
| 00:55:38 | https://web.archive.org/web/20230203064614id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/good-friday-holiday-settlement-times-2023.pdf | reused cache fx_20230203064614_good-friday-holiday-settlement-times-2023.pdf (by CalendarBuilder-FX) |
| 00:55:39 | https://web.archive.org/web/20231209153555id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/good-friday-holiday-settlement-times-2024.pdf | OK 200 application/pdf 50411B sha256=68f0ec268f00d7e6 -> rates_hc_good-friday-holiday-settlement-times-2024.pdf |
| 00:55:49 | https://web.archive.org/web/20241212020646id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/good-friday-holiday-settlement-times-2025.pdf | FAILED http 000  |
| 00:56:38 | https://web.archive.org/web/20241212020646id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/good-friday-holiday-settlement-times-2025.pdf | OK 200 application/pdf 66441B sha256=e27cf24d0775d3d1 -> rates_hc_2025_good-friday-holiday-settlement-times-2025.pdf |
| 00:56:48 | https://web.archive.org/web/20251013214632id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2026/good-friday-holiday-settlement-times-2026.pdf | reused cache fx_20251013214632_good-friday-holiday-settlement-times-2026.pdf (by CalendarBuilder-FX) |
| 00:56:48 | https://web.archive.org/web/20260715054011id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/memorial-day-holiday-settlement-times-2020.pdf | OK 200 application/pdf 39690B sha256=0d95bd526e18c296 -> rates_hc_memorial-day-holiday-settlement-times-2020.pdf |
| 00:56:58 | https://web.archive.org/web/20210115184954id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/memorial-day-holiday-settlement-times-2021.pdf | FAILED http 000  |
| 00:57:44 | https://web.archive.org/web/20210115184954id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/memorial-day-holiday-settlement-times-2021.pdf | OK 200 application/pdf 118814B sha256=c3466a2070230149 -> rates_hc_memorial-day-holiday-settlement-times-2021.pdf |
| 00:57:54 | https://web.archive.org/web/20220128025118id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/memorial-day-holiday-settlement-times-2022.pdf | FAILED http 000  |
| 00:58:39 | https://web.archive.org/web/20220128025118id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/memorial-day-holiday-settlement-times-2022.pdf | OK 200 application/pdf 45573B sha256=f68be1ecd183104f -> rates_hc_memorial-day-holiday-settlement-times-2022.pdf |
| 00:58:50 | https://web.archive.org/web/20230203070002id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/memorial-day-holiday-settlement-times-2023.pdf | OK 200 application/pdf 43997B sha256=9520a08c1b39d59a -> rates_hc_memorial-day-holiday-settlement-times-2023.pdf |
| 00:59:03 | https://web.archive.org/web/20231121220955id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/memorial-day-holiday-settlement-times-2024.pdf | OK 200 application/pdf 69585B sha256=cddb904f50e6233e -> rates_hc_memorial-day-holiday-settlement-times-2024.pdf |
| 00:59:13 | https://web.archive.org/web/20241214020513id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/memorial-day-holiday-settlement-times-2025.pdf | FAILED http 000  |
| 00:59:59 | https://web.archive.org/web/20241214020513id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/memorial-day-holiday-settlement-times-2025.pdf | OK 200 application/pdf 85234B sha256=304e2542d3c8c299 -> rates_hc_2025_memorial-day-holiday-settlement-times-2025.pdf |
| 01:00:10 | https://web.archive.org/web/20251013214653id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2026/memorial-day-holiday-settlement-times-2026.pdf | OK 200 application/pdf 82894B sha256=3d19708e3b0ea8ec -> rates_hc_2026_memorial-day-holiday-settlement-times-2026.pdf |
| 01:00:22 | https://web.archive.org/web/20190806094839id_/https://www.cmegroup.com/trading/interest-rates/us-treasury/2-year-us-treasury-note_contract_specifications.html | OK 200 text/html; charset=UTF-8 132116B sha256=089a06bf2172b1e1 -> rates_spec_zt_2019.html |
| 01:00:35 | https://web.archive.org/web/20190719015531id_/https://www.cmegroup.com/trading/interest-rates/us-treasury/5-year-us-treasury-note_contract_specifications.html | OK 200 text/html; charset=UTF-8 131416B sha256=70147a5d75cf4988 -> rates_spec_zf_2019.html |
| 01:00:50 | https://web.archive.org/web/20190806095430id_/https://www.cmegroup.com/trading/interest-rates/us-treasury/30-year-us-treasury-bond_contract_specifications.html | OK 200 text/html; charset=UTF-8 131734B sha256=53def1c420b9eb53 -> rates_spec_zb_2019.html |
| 01:01:01 | https://web.archive.org/web/20190923135706id_/https://www.cmegroup.com/trading/interest-rates/us-treasury/ultra-t-bond_contract_specifications.html | OK 200 text/html;charset=utf-8 77704B sha256=20fd4b2e31e3d107 -> rates_spec_ub_2019.html |
| 01:01:11 | https://web.archive.org/web/20190721144945id_/https://www.cmegroup.com/trading/interest-rates/us-treasury/ultra-10-year-us-treasury-note_contract_specifications.html | OK 200 text/html; charset=UTF-8 131698B sha256=d4741b2b3a4f3443 -> rates_spec_tn_2019.html |

