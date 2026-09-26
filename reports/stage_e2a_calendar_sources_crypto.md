# Stage E.2a Task 6: CME calendar sources, crypto group (MBT)

Built 2026-09-25 02:14 PDT by CalendarBuilder-Crypto (opus xhigh). Module: `data/calendars/crypto.py`. Tests: `tests/test_e2a_calendar_crypto.py`. Full rows with verbatim quotes, capture URLs and file hashes: `reports/stage_e2a_calendar_sources_crypto.json`. Coverage 2019-05-01..2026-06-19. No purchased market data was read.

## Summary

- HOLIDAYS: 49 entries: 17 full closures, 32 early halts or early closes. Grades (status, time): cme/cme 32, cme/n/a 17.
- LATE_OPENS: 1 (2025-11-28 CME outage, 07:30 CT open). EXTENDED_MAINTENANCE: 1 (2026-06-01, the first 24/7 trade date, opened Friday 2026-05-29 16:30 CT after the day-one extended maintenance, not 16:02 CT).
- BOOKED_FORWARD: 31 US holidays on which crypto traded its regular hours while CME booked the day to the next business day (not HOLIDAYS entries); 30 graded cme, 1 unverified (MLK Day 2023).
- NO_ENTRY_FINDINGS: 16 CME-stated normal days next to holidays.
- SESSIONS: 2 specs, 2019-05-01..2026-05-29 (5-day week) and 2026-06-01..2026-06-19 (24/7); 10 SESSION_SOURCES citations.
- Verbatim check: 107/107 cited rows pass (every status and time quote). Mutation control: 107/107 one-character mutations rejected. The one row with no document (2023-01-16, unverified) has verbatim_check false by construction.

Verbatim-check normalization: Each quote is split on ' ... ' into fragments; every fragment must be a substring of the cited document's text after normalization: Unicode format characters (category Cf, e.g. zero-width spaces) removed and every run of whitespace (including line breaks and NBSP) replaced by one space, the same normalization applied to the fragment. Document text: .xls = LibreOffice CSV export with '|' between cells (all sheets); .pdf = pdftotext -layout; service JSON = response body (gunzipped when stored gzip-encoded); .html = scripts and styles removed, tags replaced by a space, entities unescaped; CME client wiki REST JSON = page title, a space, then body.storage.value with tags replaced by a space and entities unescaped. For a zip the text is that of the named member; the hash is the zip's.

## HOLIDAYS

| date | name | kind | halt CT | status | time | status source | fetched | verbatim | bar check |
|---|---|---|---|---|---|---|---|---|---|
| 2019-05-27 | Memorial Day | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip :: 2019-memorial-day-holiday-schedule-compact.xls | Wayback 20210126094837 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2019-07-03 | Day before Independence Day | EARLY_HALT | 12:15 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip :: 2019-4th-of-july-holiday-schedule-compact.xls | Wayback 20210126094837 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2019-07-04 | Independence Day | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip :: 2019-4th-of-july-holiday-schedule-compact.xls | Wayback 20210126094837 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2019-09-02 | Labor Day | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip :: 2019-labor-day-holiday-schedule-compact.xls | Wayback 20210126094837 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2019-11-28 | Thanksgiving Day | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip :: 2019-thanksgiving-holiday-schedule-compact.xls | Wayback 20210126094837 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2019-11-29 | Day after Thanksgiving | EARLY_HALT | 12:15 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip :: 2019-thanksgiving-holiday-schedule-compact.xls | Wayback 20210126094837 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2019-12-24 | Christmas Eve | EARLY_HALT | 12:15 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip :: 2019-christmas-holiday-schedule-compact.xls | Wayback 20210126094837 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2019-12-25 | Christmas Day | FULL_CLOSURE |  | cme | n/a | cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip :: 2019-christmas-holiday-schedule-compact.xls | Wayback 20210126094837 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2020-01-01 | New Year's Day | FULL_CLOSURE |  | cme | n/a | cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip :: 2019-new-years-holiday-schedule-compact.xls | Wayback 20210126094837 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2020-01-20 | Martin Luther King Jr. Day | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip :: 2020-martin-luther-king-holiday-schedule-compact.xls | Wayback 20260730111834 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2020-02-17 | Presidents Day | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip :: 2020-presidents-day-holiday-schedule-compact.xls | Wayback 20260730111834 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2020-04-10 | Good Friday | FULL_CLOSURE |  | cme | n/a | cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip :: 2020-good-friday-holiday-compact.xls | Wayback 20260730111834 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2020-05-25 | Memorial Day | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip :: 2020-memorial-day-holiday-schedule-compact.xls | Wayback 20260730111834 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2020-07-03 | Independence Day (observed) | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip :: 2020-4th-of-july-holiday-schedule-compact.xls | Wayback 20260730111834 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2020-09-07 | Labor Day | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip :: 2020-labor-day-holiday-schedule-compact.xls | Wayback 20260730111834 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2020-11-26 | Thanksgiving Day | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip :: 2020-thanksgiving-holiday-schedule-compact.xls | Wayback 20260730111834 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2020-11-27 | Day after Thanksgiving | EARLY_HALT | 12:15 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip :: 2020-thanksgiving-holiday-schedule-compact.xls | Wayback 20260730111834 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2020-12-24 | Christmas Eve | EARLY_HALT | 12:15 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip :: 2020-christmas-holiday-schedule-compact.xls | Wayback 20260730111834 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2020-12-25 | Christmas Day | FULL_CLOSURE |  | cme | n/a | cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip :: 2020-christmas-holiday-schedule-compact.xls | Wayback 20260730111834 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2021-01-01 | New Year's Day | FULL_CLOSURE |  | cme | n/a | cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip :: 2021-new-years-holiday-schedule-compact.xls | Wayback 20260730111834 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2021-01-18 | Martin Luther King Jr. Day | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip :: 2021-mlk-day-schedule-compact.xls | Wayback 20260830100327 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2021-02-15 | Presidents Day | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip :: 2021-presidents-day-holiday-schedule-compact.xls | Wayback 20260830100327 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2021-04-02 | Good Friday (abbreviated, jobs report) | EARLY_HALT | 08:15 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip :: 2021-good-friday-holiday-schedule-compact.xls | Wayback 20260830100327 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2021-05-31 | Memorial Day | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip :: 2021-memorial-day-holiday-schedule-compact.xls | Wayback 20260830100327 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2021-07-05 | Independence Day (observed) | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip :: 2021-independence-day-holiday-schedule-compact.xls | Wayback 20260830100327 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2021-09-06 | Labor Day | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip :: 2021-labor-day-holiday-schedule-compact.xls | Wayback 20260830100327 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2021-11-25 | Thanksgiving Day | EARLY_HALT | 12:00 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip :: 2021-thanksgiving-holiday-schedule-compact.xls | Wayback 20260830100327 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2021-11-26 | Day after Thanksgiving | EARLY_HALT | 12:45 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip :: 2021-thanksgiving-holiday-schedule-compact.xls | Wayback 20260830100327 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2021-12-24 | Christmas Day (observed) | FULL_CLOSURE |  | cme | n/a | cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip :: 2021-christmas-holiday-schedule-compact.xls | Wayback 20260830100327 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2022-04-15 | Good Friday | FULL_CLOSURE |  | cme | n/a | cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule-compact.xls | Wayback 20220412171426 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2022-11-25 | Day after Thanksgiving | EARLY_HALT | 12:45 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule-compact.xls | Wayback 20220704073046 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2022-12-26 | Christmas Day (observed) | FULL_CLOSURE |  | cme | n/a | cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls | Wayback 20220704065430 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2023-01-02 | New Year's Day (observed) | FULL_CLOSURE |  | cme | n/a | cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule-compact.xls | Wayback 20220704065450 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2023-04-07 | Good Friday (abbreviated, jobs report) | EARLY_HALT | 10:15 | cme | cme | cmegroup.com/files/good-friday.pdf | Wayback 20240708160009 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2023-11-24 | Day after Thanksgiving | EARLY_HALT | 12:45 | cme | cme | cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf | Wayback 20231209053815 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2023-12-25 | Christmas Day | FULL_CLOSURE |  | cme | n/a | trading-hours service (BTC) 2023-12-24..2023-12-26 | Wayback 20240708161439 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2024-01-01 | New Year's Day | FULL_CLOSURE |  | cme | n/a | trading-hours service (BTC) 2023-12-31..2024-01-02 | Wayback 20240708161439 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2024-03-29 | Good Friday | FULL_CLOSURE |  | cme | n/a | trading-hours service (BTC) 2024-03-28..2024-03-30 | Wayback 20240708161439 | pass | validated against CME schedules only; embargo or holdout-2 date, never checked against bars |
| 2024-11-29 | Day after Thanksgiving | EARLY_HALT | 13:45 | cme | cme | trading-hours service (BTC) 2024-11-27..2024-11-29 | Wayback 20241220155340 | pass | validated against CME schedules only; embargo or holdout-2 date, never checked against bars |
| 2024-12-24 | Christmas Eve | EARLY_HALT | 12:45 | cme | cme | trading-hours service (BTC) 2024-12-24..2024-12-26 | Wayback 20241220155340 | pass | validated against CME schedules only; embargo or holdout-2 date, never checked against bars |
| 2024-12-25 | Christmas Day | FULL_CLOSURE |  | cme | n/a | trading-hours service (BTC) 2024-12-24..2024-12-26 | Wayback 20241220155340 | pass | validated against CME schedules only; embargo or holdout-2 date, never checked against bars |
| 2025-01-01 | New Year's Day | FULL_CLOSURE |  | cme | n/a | trading-hours service (BTC) 2024-12-31..2025-01-02 | Wayback 20241220155340 | pass | validated against CME schedules only; embargo or holdout-2 date, never checked against bars |
| 2025-04-18 | Good Friday | FULL_CLOSURE |  | cme | n/a | trading-hours service (BTC) 2025-04-17..2025-04-19 | Wayback 20241220155340 | pass | pending Task 7 (research-window bars) |
| 2025-07-04 | Independence Day | EARLY_HALT | 12:00 | cme | cme | trading-hours service (BTC) 2025-07-03..2025-07-05 | Wayback 20241220155340 | pass | pending Task 7 (research-window bars) |
| 2025-11-28 | Day after Thanksgiving | EARLY_HALT | 13:45 | cme | cme | trading-hours service (BTC) 2025-11-26..2025-11-28 | Wayback 20260129012143 | pass | pending Task 7 (research-window bars) |
| 2025-12-24 | Christmas Eve | EARLY_HALT | 12:45 | cme | cme | trading-hours service (BTC) 2025-12-24..2025-12-26 | Wayback 20260129012143 | pass | pending Task 7 (research-window bars) |
| 2025-12-25 | Christmas Day | FULL_CLOSURE |  | cme | n/a | trading-hours service (BTC) 2025-12-24..2025-12-26 | Wayback 20260129012143 | pass | pending Task 7 (research-window bars) |
| 2026-01-01 | New Year's Day | FULL_CLOSURE |  | cme | n/a | trading-hours service (BTC) 2025-12-31..2026-01-02 | Wayback 20260129012143 | pass | pending Task 7 (research-window bars) |
| 2026-04-03 | Good Friday (abbreviated, jobs report) | EARLY_HALT | 10:15 | cme | cme | cmegroup.com/tools-information/holiday-calendar/files/2026/2026-good-friday-clearing-advisory.pdf | Wayback 20260202002306 | pass | pending Task 7 (research-window bars) |

## LATE_OPENS and EXTENDED_MAINTENANCE

| table | date (trade date) | name | open CT | open offset days | stopped CT | status | time | status source | time source | verbatim | bar check |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LATE_OPENS | 2025-11-28 | Globex outage (data-center cooling failure) | 07:30 | 0 |  | cme | cme | https://www.sec.gov/Archives/edgar/data/1156375/000115637526000009/cme-20251231.htm | trading-hours service (BTC) 2025-11-26..2025-11-28 | pass | pending Task 7 (research-window bars) |
| EXTENDED_MAINTENANCE | 2026-06-01 | First 24/7 session: day-one extended maintenance | 16:30 | -3 | 16:00 | cme | cme | CME client wiki 1283194884/Cryptocurrency+Futures+and+Options+Migration+to+24-7+Trading | CME client wiki 1283194884/Cryptocurrency+Futures+and+Options+Migration+to+24-7+Trading | pass | pending Task 7 (research-window bars) |

## BOOKED_FORWARD (regular hours, no CME trade date that day)

| date | name | CME trade date | status | source | fetched | verbatim | bar check |
|---|---|---|---|---|---|---|---|
| 2022-01-17 | Martin Luther King Jr. Day | 2022-01-18 | cme | cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule-compact.xls | Wayback 20220704065433 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2022-02-21 | Presidents Day | 2022-02-22 | cme | cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule-compact.xls | Wayback 20220217175219 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2022-05-30 | Memorial Day | 2022-05-31 | cme | cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule.xls | Wayback 20220704065438 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2022-06-20 | Juneteenth (observed) | 2022-06-21 | cme | cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls | Wayback 20220620200210 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2022-07-04 | Independence Day | 2022-07-05 | cme | cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls | Wayback 20220704065431 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2022-09-05 | Labor Day | 2022-09-06 | cme | cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule-compact.xls | Wayback 20220704072842 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2022-11-24 | Thanksgiving Day | 2022-11-25 | cme | cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule-compact.xls | Wayback 20220704073046 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2023-01-16 | Martin Luther King Jr. Day | 2023-01-17 | unverified | none |  | FAIL/none | not validated: no CME schedule found (unverified); bar check pending the step 2 purchase |
| 2023-02-20 | Presidents Day | 2023-02-21 | cme | cmegroup.com/files/presidents-day.pdf | Wayback 20230329115747 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2023-05-29 | Memorial Day | 2023-05-30 | cme | cmegroup.com/trading-hours/files/memorial-day-2023.pdf | Wayback 20230420224018 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2023-06-19 | Juneteenth | 2023-06-20 | cme | cmegroup.com/trading-hours/files/juneteenth-2023.pdf | Wayback 20230613185949 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2023-07-04 | Independence Day | 2023-07-05 | cme | cmegroup.com/trading-hours/files/4th-of-july-2023.pdf | Wayback 20230627125057 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2023-09-04 | Labor Day | 2023-09-05 | cme | cmegroup.com/trading-hours/files/labor-day-2023.pdf | Wayback 20230802192446 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2023-11-23 | Thanksgiving Day | 2023-11-24 | cme | cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf | Wayback 20231209053815 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2024-01-15 | Martin Luther King Jr. Day | 2024-01-16 | cme | trading-hours service (BTC) 2024-01-14..2024-01-16 | Wayback 20241220155339 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2024-02-19 | Presidents Day | 2024-02-20 | cme | trading-hours service (BTC) 2024-02-18..2024-02-20 | Wayback 20240708161439 | pass | validated against CME schedules only, bar check pending the step 2 purchase |
| 2024-05-27 | Memorial Day | 2024-05-28 | cme | trading-hours service (BTC) 2024-05-26..2024-05-28 | Wayback 20240708161439 | pass | validated against CME schedules only; embargo or holdout-2 date, never checked against bars |
| 2024-06-19 | Juneteenth | 2024-06-20 | cme | trading-hours service (BTC) 2024-06-18..2024-06-20 | Wayback 20240708161439 | pass | validated against CME schedules only; embargo or holdout-2 date, never checked against bars |
| 2024-07-04 | Independence Day | 2024-07-05 | cme | trading-hours service (BTC) 2024-07-03..2024-07-05 | Wayback 20240708161439 | pass | validated against CME schedules only; embargo or holdout-2 date, never checked against bars |
| 2024-09-02 | Labor Day | 2024-09-03 | cme | trading-hours service (BTC) 2024-09-01..2024-09-03 | Wayback 20241220155340 | pass | validated against CME schedules only; embargo or holdout-2 date, never checked against bars |
| 2024-11-28 | Thanksgiving Day | 2024-11-29 | cme | trading-hours service (BTC) 2024-11-27..2024-11-29 | Wayback 20241220155340 | pass | validated against CME schedules only; embargo or holdout-2 date, never checked against bars |
| 2025-01-20 | Martin Luther King Jr. Day | 2025-01-21 | cme | trading-hours service (BTC) 2025-01-19..2025-01-21 | Wayback 20241220155340 | pass | validated against CME schedules only; embargo or holdout-2 date, never checked against bars |
| 2025-02-17 | Presidents Day | 2025-02-18 | cme | trading-hours service (BTC) 2025-02-16..2025-02-18 | Wayback 20241220155340 | pass | validated against CME schedules only; embargo or holdout-2 date, never checked against bars |
| 2025-05-26 | Memorial Day | 2025-05-27 | cme | trading-hours service (BTC) 2025-05-25..2025-05-27 | Wayback 20241220155340 | pass | pending Task 7 (research-window bars) |
| 2025-06-19 | Juneteenth | 2025-06-20 | cme | trading-hours service (BTC) 2025-06-18..2025-06-20 | Wayback 20241220155340 | pass | pending Task 7 (research-window bars) |
| 2025-09-01 | Labor Day | 2025-09-02 | cme | trading-hours service (BTC) 2025-08-31..2025-09-02 | Wayback 20241220155340 | pass | pending Task 7 (research-window bars) |
| 2025-11-27 | Thanksgiving Day | 2025-11-28 | cme | trading-hours service (BTC) 2025-11-26..2025-11-28 | Wayback 20260129012143 | pass | pending Task 7 (research-window bars) |
| 2026-01-19 | Martin Luther King Jr. Day | 2026-01-20 | cme | trading-hours service (BTC) 2026-01-18..2026-01-20 | Wayback 20260129012143 | pass | pending Task 7 (research-window bars) |
| 2026-02-16 | Presidents Day | 2026-02-17 | cme | trading-hours service (BTC) 2026-02-15..2026-02-17 | Wayback 20260129012143 | pass | pending Task 7 (research-window bars) |
| 2026-05-25 | Memorial Day | 2026-05-26 | cme | trading-hours service (BTC) 2026-05-24..2026-05-26 | Wayback 20260619114105 | pass | pending Task 7 (research-window bars) |
| 2026-06-19 | Juneteenth (24/7 regime) | 2026-06-22 | cme | trading-hours service (BTC) 2026-06-18..2026-06-20 | Wayback 20260619113404 | pass | pending Task 7 (research-window bars) |

## NO_ENTRY_FINDINGS

| date | source | fetched | verbatim | note |
|---|---|---|---|---|
| 2019-12-31 | cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip :: 2019-new-years-holiday-schedule-compact.xls | Wayback 20210126094837 | pass | CME's compact Globex holiday schedule, member globex-trading-schedules/2019-new-years-holiday-schedule-compact.xls of CME's 2019 holiday-calendars.zip (the hash is the zip's). The schedule gives hours per asset-class row; the crypto row is 'Bitcoin'. NORMAL: regular 16:00 CT close on New Year's Eve (Tuesday Dec 31, 2019). |
| 2020-07-02 | cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip :: 2020-4th-of-july-holiday-schedule-compact.xls | Wayback 20260730111834 | pass | CME's compact Globex holiday schedule, member 2020-4th-of-july-holiday-schedule-compact.xls of CME's 2020 holiday-calendars.zip (the hash is the zip's). The schedule gives hours per asset-class row; the crypto row is 'Bitcoin'. NORMAL: Thursday July 2, 2020 closes at the regular 16:00 CT (no early close before the observed holiday). |
| 2020-12-31 | cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip :: 2021-new-years-holiday-schedule-compact.xls | Wayback 20260730111834 | pass | CME's compact Globex holiday schedule, member 2021-new-years-holiday-schedule-compact.xls of CME's 2020 holiday-calendars.zip (the hash is the zip's). The schedule gives hours per asset-class row; the crypto row is 'Bitcoin'. NORMAL: regular 16:00 CT close on Thursday Dec 31, 2020. |
| 2021-07-02 | cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip :: 2021-independence-day-holiday-schedule-compact.xls | Wayback 20260830100327 | pass | CME's compact Globex holiday schedule, member 2021-independence-day-holiday-schedule-compact.xls of CME's 2021 holiday-calendars.zip (the hash is the zip's). The schedule gives hours per asset-class row; the crypto row is 'Bitcoin'. NORMAL: Friday July 2, 2021 closes at the regular 16:00 CT. |
| 2021-12-23 | cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip :: 2021-christmas-holiday-schedule-compact.xls | Wayback 20260830100327 | pass | CME's compact Globex holiday schedule, member 2021-christmas-holiday-schedule-compact.xls of CME's 2021 holiday-calendars.zip (the hash is the zip's). The schedule gives hours per asset-class row; the crypto row is 'Bitcoin'. NORMAL: Thursday Dec 23, 2021 'Regular per Product' close before the observed Christmas closure of Friday Dec 24. |
| 2021-12-31 | cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip :: 2022-new-years-holiday-schedule-compact.xls | Wayback 20260830100327 | pass | CME's compact Globex holiday schedule, member 2022-new-years-holiday-schedule-compact.xls of CME's 2021 holiday-calendars.zip (the hash is the zip's). The schedule gives hours per asset-class row; the crypto row is 'Bitcoin'. NORMAL: January 1, 2022 fell on a Saturday and CME observed no crypto closure: Friday Dec 31, 2021 trades Thursday 17:00 to the regular Friday 16:00 CT close, and Globex reopens Sunday Jan 2 17:00 CT for trade date Monday Jan 3 (also normal). |
| 2022-07-01 | cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls | Wayback 20220704065431 | pass | CME's compact Globex holiday schedule (.xls). The schedule gives hours per asset-class row; the crypto row is 'Cryptocurrency'. NORMAL: Friday July 1, 2022 closes at the regular 16:00 CT. |
| 2022-12-23 | cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls | Wayback 20220704065430 | pass | CME's full Globex holiday schedule (.xls). The schedule gives hours per asset-class row; the crypto row is 'Cryptocurrency'. NORMAL: Friday Dec 23, 2022 closes 04:00:00 PM (16:00 CT, regular) before the observed Christmas closure of Monday Dec 26. |
| 2022-12-30 | cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule-compact.xls | Wayback 20220704065450 | pass | CME's compact Globex holiday schedule (.xls). The schedule gives hours per asset-class row; the crypto row is 'Cryptocurrency'. NORMAL: Friday Dec 30, 2022 closes at the regular 16:00 CT. |
| 2023-07-03 | cmegroup.com/trading-hours/files/4th-of-july-2023.pdf | Wayback 20230627125057 | pass | CME's holiday trading-hours summary PDF, row CRYPTOCURRENCIES ('the most actively traded instruments for each asset class'); pdftotext -layout interleaves the table columns, so each quoted run mixes cells of adjacent columns. NORMAL: the Monday 3 July column of the CRYPTOCURRENCIES row reads 'TRADE DATE: MON 3 JULY 16:00 (CLOSED)' then '16:45 (PREOPEN) 17:00 (OPEN)' for trade date Wed 5 July: a regular 16:00 CT close (the Equities row closes 12:15 CT that day). |
| 2024-07-03 | trading-hours service (BTC) 2024-07-03..2024-07-05 | Wayback 20240708161439 | pass | CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20240708. BTC stands for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list one crypto row. 'preopen' at a time = trading stops (order entry only) until the next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. NORMAL: Wednesday July 3, 2024 closes 16:00 CT (regular; ES closes 12:15 CT). |
| 2024-12-31 | trading-hours service (BTC) 2024-12-31..2025-01-02 | Wayback 20241220155340 | pass | CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list one crypto row. 'preopen' at a time = trading stops (order entry only) until the next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. NORMAL: New Year's Eve 2024 closes at the regular 16:00 CT. |
| 2025-07-03 | trading-hours service (BTC) 2025-07-03..2025-07-05 | Wayback 20241220155340 | pass | CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list one crypto row. 'preopen' at a time = trading stops (order entry only) until the next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. NORMAL: Thursday July 3, 2025 closes 16:00 CT (regular; ES closes 12:15 CT). |
| 2025-12-31 | trading-hours service (BTC) 2025-12-31..2026-01-02 | Wayback 20260129012143 | pass | CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20260129. BTC stands for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list one crypto row. 'preopen' at a time = trading stops (order entry only) until the next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. NORMAL: New Year's Eve 2025 closes at the regular 16:00 CT. |
| 2025-01-09 | cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf | Wayback 20250218194143 | pass | CME's trading-hours summary for the National Day of Mourning (President Carter), file trading-hours/files/day-of-mourning-january-9-2024.pdf (the file name says 2024; the document is for January 9, 2025). NORMAL: CRYPTO 'NORMAL HOURS' while US equities close at 8:30 AM CT (data.cme_calendar's 08:30 halt for MES does not apply to crypto). |
| 2026-05-29 | CME client wiki 1283194884/Cryptocurrency+Futures+and+Options+Migration+to+24-7+Trading | direct | pass | CME client systems wiki page 1283194884. NORMAL: trade date Friday 2026-05-29 is the last trade date of the 5-day regime (Thursday 17:00 CT to Friday 16:00 CT); 24/7 trading starts after its 16:00 CT close. SESSIONS splits here. |

## SESSION_SOURCES

| key | status source | fetched | time source | verbatim |
|---|---|---|---|---|
| cme_crypto_hours_5day | cmegroup.com/trading/equity-index/us-index/bitcoin_contract_specifications.html | Wayback 20190603151021 | cmegroup.com/education/articles-and-reports/micro-bitcoin-futures-frequently-asked-questions.html | pass |
| cme_crypto_hours_5day_2026 | CME client wiki 1283194884/Cryptocurrency+Futures+and+Options+Migration+to+24-7+Trading | direct |  | pass |
| cme_crypto_24_7_launch | cmegroup.com/media-room/press-releases/2026/2/19/cme_group_to_launch247cryptocurrencyfuturesandoptionstradingonma.html | Wayback 20260219141120 | cmegroup.com/media-room/press-releases/2026/6/01/cme_group_announceslaunchof247cryptocurrencyfuturesandoptionstra.html | pass |
| cme_crypto_24_7_article_k7_036 | cmegroup.com/articles/2026/aligning-cryptocurrency-derivatives-with-spot-markets-measuring-the-247-trading-opportunity.html | Wayback 20260513095936 |  | pass |
| cme_crypto_24_7_hours | cmegroup.com/articles/faqs/frequently-asked-questions-cryptocurrency-futures.html | Wayback 20260820062923 | cmegroup.com/articles/faqs/frequently-asked-questions-cryptocurrency-futures.html | pass |
| cme_crypto_24_7_wiki | CME client wiki 1283194884/Cryptocurrency+Futures+and+Options+Migration+to+24-7+Trading | direct | CME client wiki 1283194884/Cryptocurrency+Futures+and+Options+Migration+to+24-7+Trading | pass |
| cme_btc_settlement_2026 | CME client wiki 457318016/Bitcoin | direct | CME client wiki 457318016/Bitcoin | pass |
| cme_settlement_time_details | CME client wiki 457085528/Daily+Settlement+Time+Details | direct |  | pass |
| cme_btc_settlement_2020 | cmegroup.com/confluence/display/EPICSANDBOX/Bitcoin | Wayback 20200809023134 |  | pass |
| cme_mbt_settlement_2021 | cmegroup.com/education/articles-and-reports/micro-bitcoin-futures-frequently-asked-questions.html | Wayback 20210330123221 |  | pass |

## Session-hour changes found

1. **2026-05-29 16:00 CT: 5-day week to 24/7 trading** (the only change to crypto's regular Globex
   hours in 2019-05..2026-06). CME press release of 2026-02-19: "Beginning Friday, May 29 at 4:00
   p.m. CT , CME Group Cryptocurrency futures and options will trade continuously on CME Globex
   with at least a two-hour weekly maintenance period over the weekend. All holiday or weekend
   trading from Friday evening through Sunday evening will have a trade date of the following
   business day, with clearing, settlement and regulatory reporting processed the following
   business day as well." CME press release of 2026-06-01: "today announced it launched 24/7
   trading for Cryptocurrency futures and options. The expanded trading hours, which went live on
   Friday, May 29, mark a significant milestone". Maintenance windows (CME FAQ, Wayback
   2026-08-20): "Monday through Friday: 4:00 p.m. to 4:02 p.m. CT (pre-open: 4:01 p.m. to 4:02
   p.m. CT) Saturday: 2:00 a.m. to 4:00 a.m. CT (pre-open: 3:45 a.m. to 4:00 a.m. CT)". The CME
   client wiki (page 1283194884, version 2026-08-14) gives the same windows to the second
   (daily close 16:00:00-16:01:00, pre-open to 16:01:30, no-cancel to 16:02:00, open 16:02:00;
   Saturday close 02:00-03:45, pre-open to 04:00, open 04:00) and a day-one extended maintenance:
   Friday 2026-05-29 close 16:00, open 16:30 CT (EXTENDED_MAINTENANCE 2026-06-01). CME's service records
   of 2026-06-18..20 show exactly these events (16:00 closed, 16:01 preopen, 16:02 open; Saturday
   02:00 closed, 03:45 preopen, 04:00 open). The first 24/7 trade date is Monday 2026-06-01; the
   trade date 2026-05-29 (Thursday 17:00 to Friday 16:00 CT) is still 5-day shaped. Encoded as two
   SessionSpecs; the Monday shape is SEGMENTS_AFTER_WEEKEND_24_7.
   - CME Clearing's "Summary of Requirements and Guidelines for Cryptocurrency Trading and 24x7
     Clearing" (the January 2026 version, Wayback 2026-03-13; pdftotext drops most spaces in it)
     describes a one-minute daily close, 16:00 to 16:01 CT, at the trade-date switch; the later
     FAQ, wiki and service records give no matching from 16:00 to 16:02 CT (close 16:00-16:01,
     pre-open and no-cancel to 16:02). Encoded 16:02; the PDF is logged, not cited.
   - Frozen design D10 calls the source "CME's own release of 2026-06-01, K7-036". K7-036 in the
     E.0 registry is CME's article "Aligning Cryptocurrency Derivatives with Spot Markets:
     Measuring the 24/7 Trading Opportunity" ("Starting on May 29, 2026, pending regulatory review,
     we are transitioning ..."), written before the launch; the release dated 2026-06-01 is a
     separate CME press release, which confirms the launch. Both are quoted (SESSION_SOURCES
     'cme_crypto_24_7_article_k7_036', 'cme_crypto_24_7_launch').
2. **No other regular-hours change 2019-05-01..2026-05-29.** CME's BTC contract specifications
   (Wayback 2019-06-03): "Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m/ CT) with a
   60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)"; MBT FAQ (Wayback 2021-03-30):
   the same hours; CME wiki's pre-24/7 "Current Cryptocurrency Futures and Options Schedule"
   (2026): Sunday startup 16:00-17:00 CT, daily maintenance 16:00-16:45 close, 16:45-17:00
   pre-open. Every 2019-2022 compact holiday schedule's crypto row closes "Regular @ 1600 CT" and
   opens "Regular @ 1700 CT", and the 2023 summary PDFs and 2023-2026 service records show the
   same 16:00 close and 17:00 open around each holiday.
3. **Holiday-hours policy changes (not regular-session changes), all dated from CME schedules:**
   crypto halts with equities at 12:00 CT on US holidays through 2021, and trades its regular
   hours on them from MLK Day 2022-01-17 (first CME schedule with a "Cryptocurrency" row and a
   "1600 CT" HALT cell); the day-after-Thanksgiving close moves 12:15 CT (2019-2020) to 12:45 CT
   (2021-2023) to 13:45 CT (2024-2025); jobs-report Good Friday closes are 08:15 CT (2021) and
   10:15 CT (2023, 2026).

## D6 confirmation

Design D6's crypto row: O 08:30, C 15:00, F 15:08 CT. Encoded unchanged in both SessionSpecs
(`day_session_ct={"MBT": (08:30, 15:00)}`).

- **C 15:00 CT: confirmed.** CME client wiki, Bitcoin settlement procedures (page 457318016,
  version 2026-02-12, current when read 2026-09-25, i.e. after the 24/7 launch): "CME Group
  determines the daily settlements for Bitcoin (BTC) futures based on CME Globex trading activity
  between 14:59:00 and 15:00:00 Central Time (CT), the settlement period." and "The daily
  settlements in the Micro Bitcoin (MBT) futures contracts are derived directly from settlements
  in the Bitcoin (BTC) futures contracts. Daily settlements derived from the BTC will be copied
  directly to the MBT for each contract listing." CME wiki Daily Settlement Time Details: "Bitcoin
  14:59:00-15:00:00 CT". The same period in the Wayback capture of 2020-08-09 ("CME Group staff
  determines the daily settlements for Bitcoin futures based on trading activity on CME Globex
  between 14:59:00 and 15:00:00 Central Time, the settlement period.") and in the MBT FAQ of
  2021-03-30 ("between 3:59:00 p.m. and 4:00:00 p.m. Eastern Time"). No change 2019-2026 found.
  Holiday settlement exceptions (not a D6 value): CME's notices give "Equity & Crypto Products"
  12:00:00 CT on early-close days (2023-2025) and "CME Group FX and Cryptocurrency Products 10:00
  am CT" on Good Friday 2023.
- **O 08:30 CT: not a CME-published boundary.** CME's crypto futures trade a 17:00-16:00 CT Globex
  session (24/7 from 2026-05-29); no CME settlement procedure, contract specification, FAQ or
  schedule retrieved defines a crypto day-session open. 08:30 CT is the US equity cash open.
  Encoded as D6 states; the lead rules.
- **F 15:08 CT:** a Topstep constant (D9.1), not a CME time; it falls after C and inside the
  trading segment in both regimes (5-day: until 16:00 CT; 24/7: until 16:00 CT).
- Discrepancies: none for C. O has no CME counterpart (reported, not changed).

## Entries graded unverified or secondary, and why

- HOLIDAYS: none. All 49 entries are status "cme"; every early halt's time is "cme" (the CME
  schedule, summary PDF or service record states the crypto clock time).
- BOOKED_FORWARD 2023-01-16 (MLK Day 2023): **unverified**, pattern-assumed. No CME document with
  a crypto row was retrieved: the only MLK 2023 Globex schedule on Wayback is the MGEX/DME sheet;
  Wayback has 404s for every guessed MLK 2023 summary PDF name; the service captures carry no
  events before 2023-09 for any product; AMP Futures' image of CME's MLK 2023 schedule lists
  Equity, Interest Rate, FX, Energies, Metals, Grains, Dairy, Lumber and Livestock but no crypto
  row; CME's settlement notice and clearing advisory give no hours. Assumed regular hours from
  CME's crypto rows for MLK 2022 (1600 CT) and Presidents Day 2023 (16:00 PREOPEN HALT). If wrong,
  HOLIDAYS lacks a 12:00 CT EARLY_HALT on 2023-01-16 (confirmation window; the bar check after
  the step 2 purchase settles it).
- Conflict (graded cme, flagged): 2024-11-29 close. CME's service capture of 2024-07-08 gave
  12:45 CT for BTC; the capture of 2024-12-20 (after the date) gives 13:45 CT, and CL, GC and 6E
  moved to 13:45 between the two captures. 13:45 is encoded. CME's settlement notice for that day
  gives "Equity & Crypto Products Settlement Time: 12:00:00 CT". Holdout-2 date, never checkable
  against bars; the same 13:45 on 2025-11-28 is in the research window and Task 7 checks it.

## Gaps

- **MLK Day 2023**: no CME document with crypto hours (above).
- **2023-09..2024**: CME published no holiday summary PDFs for 2024-2025 (Wayback 404s, per the
  energy builder's CDX listing); these years rest on the trading-hours-by-product service
  captures, which exist for every holiday in the window from 2023-09 on. Captures from before the
  event (2024-07-08, 2024-12-20, 2026-01-29) are CME's published plan; later ones (2024-12-20 for
  2024 dates, 2026-01-29, 2026-06-10, 2026-06-19, 2026-07-22) show the record after the date.
  Entries whose only capture predates the date: 2025-01-20, 2025-02-17, 2025-04-18, 2025-05-26,
  2025-06-19, 2025-07-04, 2025-09-01 (Dec 2024 plan), 2026-01-19, 2026-02-16 (Jan 2026 plan);
  all in the research window, so Task 7 checks them against bars.
- **MBT itself**: CME states holiday hours per asset-class row ("Bitcoin", "Cryptocurrency",
  "CRYPTOCURRENCIES") or for BTC (service product 8478). MBT-specific holiday hours are not
  published separately; MBT is taken to trade BTC's hours (same Globex session; MBT's daily
  settlement is copied from BTC).
- **Years before MBT listed (2019-05..2021-04)**: covered from the Bitcoin row, as the brief asks.
- **2026-06-19 (24/7 regime)**: the clock is regular, but CME books it to trade date 2026-06-22;
  the treatment is the lead's ruling (flag 1).
- **2025-11-28 outage stop time**: when trading stopped on the evening of 2025-11-27 is in no CME
  document retrieved (LATE_OPENS halt_from_ct None).
- No year is filled by pattern except the one MLK 2023 record.

Holiday coverage by year (crypto treatment; C = FULL_CLOSURE, H = EARLY_HALT with CT time, R =
regular hours booked forward, n = normal):

| holiday | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| New Year's Day | before coverage | C 01-01 | C 01-01 | n (Sat; 12-31 n) | C 01-02 | C 01-01 | C 01-01 | C 01-01 |
| MLK Day | before | H 12:00 | H 12:00 | R | R (unverified) | R | R | R |
| Presidents Day | before | H 12:00 | H 12:00 | R | R | R | R | R |
| Good Friday | before | C | H 08:15 | C | H 10:15 | C | C | H 10:15 |
| Memorial Day | H 12:00 | H 12:00 | H 12:00 | R | R | R | R | R |
| Juneteenth | not a holiday | not a holiday | not a holiday | R (06-20) | R | R | R | R (24/7) |
| Eve of Independence Day | H 12:15 (07-03) | n (07-02) | n (07-02) | n (07-01) | n (07-03) | n (07-03) | n (07-03) | after coverage |
| Independence Day | H 12:00 | H 12:00 (07-03) | H 12:00 (07-05) | R | R | R | H 12:00 | after coverage |
| Labor Day | H 12:00 | H 12:00 | H 12:00 | R | R | R | R | after coverage |
| Thanksgiving Day | H 12:00 | H 12:00 | H 12:00 | R | R | R | R | after coverage |
| Day after Thanksgiving | H 12:15 | H 12:15 | H 12:45 | H 12:45 | H 12:45 | H 13:45 | H 13:45 + late open 07:30 | after coverage |
| Christmas Eve | H 12:15 | H 12:15 | n (12-23) | n (12-23 Fri) | Sunday | H 12:45 | H 12:45 | after coverage |
| Christmas Day | C | C | C (12-24 obs.) | C (12-26 obs.) | C | C | C | after coverage |
| Day of Mourning | | | | | | | n (01-09) | |

## Flags for the lead

1. **Trade-date treatment of BOOKED_FORWARD days.** From 2022 crypto trades regular hours on US
   holidays while CME books those hours to the next business day. Under the program's convention
   (data/session.py, data.cme_calendar: each calendar day its own trade date, as Topstep's XFA
   treats holidays) these are ordinary trade dates, so no HOLIDAYS entry is needed. **2026-06-19
   (24/7 regime) is the case that matters**: the 02:10 PDT ruling says the bar builder follows
   CME's weekend assignment in the 24/7 regime; CME's rule covers "holiday or weekend trading",
   so under that ruling 2026-06-19 has no crypto trade date and Thursday 16:02 CT onward belongs
   to 2026-06-22, outside the coverage and the research window. Under the data.session convention
   it is a regular 24/7 weekday. Not encoded either way beyond the BOOKED_FORWARD record.
2. **24/7 Monday shape.** SessionSpec carries one segments tuple; the Tuesday-Friday shape is
   encoded there and the Monday shape (Friday 16:02 to Monday 16:00 less Saturday 02:00-04:00 CT)
   in SEGMENTS_AFTER_WEEKEND_24_7. Whoever builds crypto bars for 2026-06 must read both.
3. **D6's O 08:30 CT** has no CME counterpart for crypto (D6 confirmation).
4. **Interface extensions** (additive, backward compatible): LateOpen gains `open_offset_days`
   (default 0 = the rates/energy meaning); new BookedForward/BOOKED_FORWARD(_SOURCES),
   EXTENDED_MAINTENANCE(_SOURCES) and SEGMENTS_AFTER_WEEKEND_24_7. Two attributes that the
   lead's data/group_session.py reads with getattr: WEEKEND_TO_NEXT_TRADE_DATE_FROM =
   2026-06-01 (CME's weekend/holiday assignment from the first 24/7 trade date) and
   GLOBEX_HOURS_UNDOCUMENTED = {2023-01-16} (the rates group's watch-day attribute). HOLIDAYS,
   SOURCES, NO_ENTRY_FINDINGS, CALENDAR_COVERAGE, assert_calendar_coverage and SESSIONS follow
   data.cme_calendar / data.calendars exactly. The day-one 24/7 delay is NOT in LATE_OPENS:
   data.group_session.is_scheduled_late_open refuses a LateOpen that has `halt_from_ct` and no
   "outage"/"unscheduled" in its name, and session_intervals applies a scheduled open time on
   the trade date itself (it would have emptied Monday 2026-06-01). `load_group_calendar
   ("crypto")` was run against the module and loads (outage classed unscheduled).
5. **group_session's weekend rule vs CME's 24/7 windows.** With WEEKEND_TO_NEXT_TRADE_DATE_FROM
   set, data.group_session opens a Monday trade date at the previous trade date's end (Friday
   16:00 CT), so the Friday 16:00-16:02 CT pause (16:00-16:30 on 2026-05-29) and the Saturday
   02:00-04:00 CT maintenance count as open (bars simply absent there, not bars in a closed
   window). The exact shape is SEGMENTS_AFTER_WEEKEND_24_7 plus EXTENDED_MAINTENANCE.
6. **For the equity group (not edited here):** the 2021 CME compact schedules read for crypto also
   carry the Equity row and resolve two entries data/cme_calendar.py grades unverified:
   2021-01-01 ("Equity |Regular @ 1600 CT / 2200 UTC|Closed for New Year's|Regular @ 1700 CT /
   2300 UTC||Regular @ 1600 CT / 2200 UTC", member 2021-new-years-holiday-schedule-compact.xls of
   the 2020 zip) and the 2021-04-02 close time ("Equity |Regular @ 1600 CT / 2100 UTC|Regular @
   1700 CT / 2200 UTC|Closed @ 0815 CT / 1315 UTC|Regular @ 1700 CT / 2200 UTC", member
   2021-good-friday-holiday-schedule-compact.xls of the 2021 zip). Both quotes pass the same
   verbatim check (normalized text).
7. **2024-11-29** 12:45 vs 13:45 conflict between two CME captures (above).

## Fetch log (times PDT, 2026-09-25)

WebSearch: not used (0 calls). Firecrawl: 1 search, between 01:45 and 01:53 PDT (query 'CME Group 24/7 cryptocurrency futures weekly maintenance window Saturday trade date FAQ', 2 credits), used only to discover URLs; every quoted page was then fetched with curl and hashed. Wayback CDX listings (curl, no files saved; exact times not logged, all between 01:43 and 01:57 PDT; 01:43:52 and 01:45:24 are shell-clock readings): press-releases 2026/2-6 (found the 2026-02-19 and 2026-06-01 releases); notices/electronic-trading/2026, articles/faqs, markets/cryptocurrencies, notices/clearing/2026, articles/2026 (the prefix queries except articles/faqs returned nothing); files/mlk*, files/martin*, trading-hours/files/m* and files/<holiday>* (MLK 2023: 404s only); confluence/display/EPICSANDBOX/Bitcoin; the crypto FAQ, clearing guidelines, K7-036 article, MBT FAQ, BTC and MBT specification pages. Shortly before 01:56 web.archive.org briefly refused connections (curl exit 7); retried successfully.

Files fetched by this builder (saved in the shared cache as crypto_*; index.jsonl lines by CalendarBuilder-Crypto):

| time PDT | URL | fetched via | result |
|---|---|---|---|
| 01:42:40 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457316087/child/page?limit=200 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457316087/child/page?limit=200 | HTTP 200, 9956 bytes |
| 01:42:41 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457316087?expand=body.storage,version,history | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457316087?expand=body.storage,version,history | HTTP 200, 3747 bytes |
| 01:42:50 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457318016?expand=body.storage,version,history | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457318016?expand=body.storage,version,history | HTTP 200, 17639 bytes |
| 01:42:51 | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457318016/Bitcoin | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457318016/Bitcoin | HTTP 200, 1466101 bytes |
| 01:44:00 | https://www.cmegroup.com/media-room/press-releases/2026/6/01/cme_group_announceslaunchof247cryptocurrencyfuturesandoptionstra.html | https://web.archive.org/web/20260602010915id_/https://www.cmegroup.com/media-room/press-releases/2026/6/01/cme_group_announceslaunchof247cryptocurrencyfuturesandoptionstra.html | HTTP 200, 137122 bytes |
| 01:44:01 | https://www.cmegroup.com/media-room/press-releases/2026/2/19/cme_group_to_launch247cryptocurrencyfuturesandoptionstradingonma.html | https://web.archive.org/web/20260219141120id_/https://www.cmegroup.com/media-room/press-releases/2026/2/19/cme_group_to_launch247cryptocurrencyfuturesandoptionstradingonma.html | HTTP 200, 135684 bytes |
| 01:52:18 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/Bitcoin | https://web.archive.org/web/20200809023134id_/https://www.cmegroup.com/confluence/display/EPICSANDBOX/Bitcoin | HTTP 200, 50576 bytes |
| 01:52:18 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/Bitcoin | https://web.archive.org/web/20210613044557id_/https://www.cmegroup.com/confluence/display/EPICSANDBOX/Bitcoin | failed (curl code 000, no file kept) |
| 01:52:25 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/Bitcoin | https://web.archive.org/web/20211021043830id_/https://www.cmegroup.com/confluence/display/EPICSANDBOX/Bitcoin | failed (curl code 000, no file kept) |
| 01:52:32 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/Bitcoin | https://web.archive.org/web/20220128191225id_/https://www.cmegroup.com/confluence/display/EPICSANDBOX/Bitcoin | failed (curl code 000, no file kept) |
| 01:52:53 | https://www.cmegroup.com/articles/faqs/frequently-asked-questions-cryptocurrency-futures.html | https://web.archive.org/web/20260820062923id_/https://www.cmegroup.com/articles/faqs/frequently-asked-questions-cryptocurrency-futures.html | HTTP 200, 199151 bytes |
| 01:52:53 | https://www.cmegroup.com/clearing/files/cryptocurrency-guidelines.pdf | https://web.archive.org/web/20260313115223id_/https://www.cmegroup.com/clearing/files/cryptocurrency-guidelines.pdf | HTTP 200, 270181 bytes |
| 01:52:54 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/1283194884?expand=body.storage,version,history | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/1283194884?expand=body.storage,version,history | HTTP 200, 162082 bytes |
| 01:56:41 | https://www.cmegroup.com/trading/equity-index/us-index/bitcoin_contract_specifications.html | https://web.archive.org/web/20190603151021id_/https://www.cmegroup.com/trading/equity-index/us-index/bitcoin_contract_specifications.html | HTTP 200, 126645 bytes |
| 01:56:42 | https://www.cmegroup.com/markets/cryptocurrencies/bitcoin/micro-bitcoin.contractSpecs.html | https://web.archive.org/web/20260411030127id_/https://www.cmegroup.com/markets/cryptocurrencies/bitcoin/micro-bitcoin.contractSpecs.html | HTTP 200, 255089 bytes |
| 01:56:43 | https://www.cmegroup.com/education/articles-and-reports/micro-bitcoin-futures-frequently-asked-questions.html | https://web.archive.org/web/20210330123221id_/https://www.cmegroup.com/education/articles-and-reports/micro-bitcoin-futures-frequently-asked-questions.html | HTTP 200, 117377 bytes |
| 01:56:43 | https://www.cmegroup.com/articles/2026/aligning-cryptocurrency-derivatives-with-spot-markets-measuring-the-247-trading-opportunity.html | https://web.archive.org/web/20260513095936id_/https://www.cmegroup.com/articles/2026/aligning-cryptocurrency-derivatives-with-spot-markets-measuring-the-247-trading-opportunity.html | HTTP 200, 153224 bytes |

Files reused from the shared cache (fetched earlier by other CalendarBuilders; hash re-verified against index.jsonl before use):

| document | fetched via | fetched (PDT) | by |
|---|---|---|---|
| cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | 2026-09-25 00:25:37 PDT | CalendarBuilder-Rates |
| cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | 2026-09-25 00:25:38 PDT | CalendarBuilder-Rates |
| cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | 2026-09-25 00:25:38 PDT | CalendarBuilder-Rates |
| cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule-compact.xls | https://web.archive.org/web/20220704065433id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule-compact.xls | 2026-09-25 00:28:39 PDT | CalendarBuilder-Energy |
| cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule-compact.xls | https://web.archive.org/web/20220217175219id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule-compact.xls | 2026-09-25 00:28:57 PDT | CalendarBuilder-Energy |
| cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule-compact.xls | https://web.archive.org/web/20220412171426id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule-compact.xls | 2026-09-25 00:27:32 PDT | CalendarBuilder-Energy |
| cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule.xls | https://web.archive.org/web/20220704065438id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule.xls | 2026-09-25 00:28:35 PDT | CalendarBuilder-Energy |
| cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls | https://web.archive.org/web/20220620200210id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls | 2026-09-25 00:27:35 PDT | CalendarBuilder-Energy |
| cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls | https://web.archive.org/web/20220704065431id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls | 2026-09-25 00:27:34 PDT | CalendarBuilder-Energy |
| cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule-compact.xls | https://web.archive.org/web/20220704072842id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule-compact.xls | 2026-09-25 00:27:52 PDT | CalendarBuilder-Energy |
| cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule-compact.xls | https://web.archive.org/web/20220704073046id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule-compact.xls | 2026-09-25 00:29:05 PDT | CalendarBuilder-Energy |
| cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls | https://web.archive.org/web/20220704065430id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls | 2026-09-25 00:27:31 PDT | CalendarBuilder-Energy |
| cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule-compact.xls | https://web.archive.org/web/20220704065450id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule-compact.xls | 2026-09-25 00:29:13 PDT | CalendarBuilder-FX |
| cmegroup.com/files/presidents-day.pdf | https://web.archive.org/web/20230329115747id_/https://www.cmegroup.com/files/presidents-day.pdf | 2026-09-25 00:45:58 PDT | CalendarBuilder-Energy |
| cmegroup.com/files/good-friday.pdf | https://web.archive.org/web/20240708160009id_/https://www.cmegroup.com/files/good-friday.pdf | 2026-09-25 00:45:55 PDT | CalendarBuilder-Energy |
| cmegroup.com/trading-hours/files/memorial-day-2023.pdf | https://web.archive.org/web/20230420224018id_/https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf | 2026-09-25 00:30:58 PDT | CalendarBuilder-Energy |
| cmegroup.com/trading-hours/files/juneteenth-2023.pdf | https://web.archive.org/web/20230613185949id_/https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf | 2026-09-25 00:30:20 PDT | CalendarBuilder-Energy |
| cmegroup.com/trading-hours/files/4th-of-july-2023.pdf | https://web.archive.org/web/20230627125057id_/https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf | 2026-09-25 00:30:08 PDT | CalendarBuilder-Energy |
| cmegroup.com/trading-hours/files/labor-day-2023.pdf | https://web.archive.org/web/20230802192446id_/https://www.cmegroup.com/trading-hours/files/labor-day-2023.pdf | 2026-09-25 00:30:24 PDT | CalendarBuilder-Energy |
| cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf | https://web.archive.org/web/20231209053815id_/https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf | 2026-09-25 00:32:06 PDT | CalendarBuilder-Energy |
| cmegroup.com/trading-hours/files/christmas-day-2023.pdf | https://web.archive.org/web/20260719095248id_/https://www.cmegroup.com/trading-hours/files/christmas-day-2023.pdf | 2026-09-25 00:30:12 PDT | CalendarBuilder-Energy |
| cmegroup.com/trading-hours/files/new-years-day-2024.pdf | https://web.archive.org/web/20260811165716id_/https://www.cmegroup.com/trading-hours/files/new-years-day-2024.pdf | 2026-09-25 00:32:02 PDT | CalendarBuilder-Energy |
| cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf | https://web.archive.org/web/20250218194143id_/https://www.cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf | 2026-09-25 00:30:17 PDT | CalendarBuilder-Energy |
| cmegroup.com/tools-information/holiday-calendar/files/2021-good-friday-advisory.pdf | https://web.archive.org/web/20210517110023id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-good-friday-advisory.pdf | 2026-09-25 00:42:46 PDT | CalendarBuilder-Rates |
| cmegroup.com/tools-information/holiday-calendar/files/2023-good-friday-advisory.pdf | https://web.archive.org/web/20230203065333id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-good-friday-advisory.pdf | 2026-09-25 00:42:56 PDT | CalendarBuilder-Rates |
| cmegroup.com/tools-information/holiday-calendar/files/2026/2026-good-friday-clearing-advisory.pdf | https://web.archive.org/web/20260202002306id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2026/2026-good-friday-clearing-advisory.pdf | 2026-09-25 00:43:07 PDT | CalendarBuilder-Rates |
| https://www.sec.gov/Archives/edgar/data/1156375/000115637526000009/cme-20251231.htm | https://web.archive.org/web/20260226224856id_/https://www.sec.gov/Archives/edgar/data/1156375/000115637526000009/cme-20251231.htm | 2026-09-25 00:55:25 PDT | CalendarBuilder-Energy |
| trading-hours service (BTC) 2023-09-03..2023-09-05 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-09-03&toEventDate=2023-09-05&isProtected&_t=1720455278654 | 2026-09-25 00:35:12 PDT | CalendarBuilder-FX |
| trading-hours service (BTC) 2023-11-22..2023-11-24 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-11-22&toEventDate=2023-11-24&isProtected&_t=1720455278656 | 2026-09-25 00:35:28 PDT | CalendarBuilder-FX |
| trading-hours service (BTC) 2023-12-24..2023-12-26 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-24&toEventDate=2023-12-26&isProtected&_t=1720455278659 | 2026-09-25 00:35:28 PDT | CalendarBuilder-FX |
| trading-hours service (BTC) 2023-12-31..2024-01-02 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-31&toEventDate=2024-01-02&isProtected&_t=1720455278661 | 2026-09-25 00:35:41 PDT | CalendarBuilder-Rates |
| trading-hours service (BTC) 2024-01-14..2024-01-16 | https://web.archive.org/web/20241220155339id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1734710019526 | 2026-09-25 00:32:36 PDT | CalendarBuilder-Energy |
| trading-hours service (BTC) 2024-02-18..2024-02-20 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669 | 2026-09-25 00:36:31 PDT | CalendarBuilder-FX |
| trading-hours service (BTC) 2024-03-28..2024-03-30 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-03-28&toEventDate=2024-03-30&isProtected&_t=1720455278672 | 2026-09-25 00:36:31 PDT | CalendarBuilder-FX |
| trading-hours service (BTC) 2024-05-26..2024-05-28 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675 | 2026-09-25 00:36:32 PDT | CalendarBuilder-FX |
| trading-hours service (BTC) 2024-06-18..2024-06-20 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677 | 2026-09-25 00:36:32 PDT | CalendarBuilder-FX |
| trading-hours service (BTC) 2024-07-03..2024-07-05 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680 | 2026-09-25 00:33:26 PDT | CalendarBuilder-FX |
| trading-hours service (BTC) 2024-09-01..2024-09-03 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1734710019534 | 2026-09-25 00:36:47 PDT | CalendarBuilder-Energy |
| trading-hours service (BTC) 2024-11-27..2024-11-29 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535 | 2026-09-25 00:37:50 PDT | CalendarBuilder-Energy |
| trading-hours service (BTC) 2024-11-27..2024-11-29 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1720455278685 | 2026-09-25 00:36:33 PDT | CalendarBuilder-FX |
| trading-hours service (BTC) 2024-12-24..2024-12-26 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537 | 2026-09-25 00:38:24 PDT | CalendarBuilder-Energy |
| trading-hours service (BTC) 2024-12-31..2025-01-02 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1734710019538 | 2026-09-25 00:38:37 PDT | CalendarBuilder-Energy |
| trading-hours service (BTC) 2025-01-19..2025-01-21 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539 | 2026-09-25 00:36:35 PDT | CalendarBuilder-FX |
| trading-hours service (BTC) 2025-02-16..2025-02-18 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540 | 2026-09-25 00:36:37 PDT | CalendarBuilder-FX |
| trading-hours service (BTC) 2025-04-17..2025-04-19 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-04-17&toEventDate=2025-04-19&isProtected&_t=1734710019542 | 2026-09-25 00:36:37 PDT | CalendarBuilder-FX |
| trading-hours service (BTC) 2025-05-25..2025-05-27 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543 | 2026-09-25 00:36:46 PDT | CalendarBuilder-Rates |
| trading-hours service (BTC) 2025-06-18..2025-06-20 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544 | 2026-09-25 00:37:42 PDT | CalendarBuilder-Rates |
| trading-hours service (BTC) 2025-07-03..2025-07-05 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545 | 2026-09-25 00:38:43 PDT | CalendarBuilder-Rates |
| trading-hours service (BTC) 2025-08-31..2025-09-02 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546 | 2026-09-25 00:38:45 PDT | CalendarBuilder-Energy |
| trading-hours service (BTC) 2025-11-26..2025-11-28 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060 | 2026-09-25 00:39:22 PDT | CalendarBuilder-Energy |
| trading-hours service (BTC) 2025-12-24..2025-12-26 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064 | 2026-09-25 00:39:39 PDT | CalendarBuilder-Energy |
| trading-hours service (BTC) 2025-12-31..2026-01-02 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066 | 2026-09-25 00:39:46 PDT | CalendarBuilder-Energy |
| trading-hours service (BTC) 2026-01-18..2026-01-20 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068 | 2026-09-25 00:39:49 PDT | CalendarBuilder-Rates |
| trading-hours service (BTC) 2026-02-15..2026-02-17 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1769649703070 | 2026-09-25 00:40:23 PDT | CalendarBuilder-FX |
| trading-hours service (BTC) 2026-04-01..2026-04-03 | https://web.archive.org/web/20260610104510id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1743113432016 | 2026-09-25 00:40:11 PDT | CalendarBuilder-Energy |
| trading-hours service (BTC) 2026-05-24..2026-05-26 | https://web.archive.org/web/20260619114105id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1749141516014 | 2026-09-25 00:40:48 PDT | CalendarBuilder-Energy |
| trading-hours service (BTC) 2026-06-17..2026-06-19 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-17&toEventDate=2026-06-19&isProtected&_t=1769649703075 | 2026-09-25 00:41:54 PDT | CalendarBuilder-FX |
| trading-hours service (BTC) 2026-06-18..2026-06-20 | https://web.archive.org/web/20260619113404id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-18&toEventDate=2026-06-20&isProtected&_t=1749141523693 | 2026-09-25 00:40:55 PDT | CalendarBuilder-Energy |
| trading-hours service (BTC) 2026-06-18..2026-06-20 | https://web.archive.org/web/20260722114220id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-18&toEventDate=2026-06-20&isProtected&_t=1784720540600 | 2026-09-25 00:41:29 PDT | CalendarBuilder-Energy |
| CME client wiki 457085528/Daily+Settlement+Time+Details | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457085528/Daily+Settlement+Time+Details | 2026-09-25 00:48:06 PDT | CalendarBuilder-Energy |
| cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | 2026-09-25 00:25:37 PDT | CalendarBuilder-Rates |
| cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | 2026-09-25 00:25:38 PDT | CalendarBuilder-Rates |
| cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | 2026-09-25 00:25:38 PDT | CalendarBuilder-Rates |

