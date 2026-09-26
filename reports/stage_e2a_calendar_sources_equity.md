# Stage E.2a Task 6: the equity calendar (ES/MES, NQ/MNQ, RTY/M2K, YM/MYM), sources and checks

CalendarBuilder-Equity-OpusXHigh, written 2026-09-25 02:41 PDT. Source lookup, code and synthetic tests only: no purchased market data was opened (nothing under data/vendor/, data/sealed/, data/processed/ or any bar parquet was read). Full records: `reports/stage_e2a_calendar_sources_equity.json`.

## Summary

- 84 calendar entries lie in 2019-05-01..2026-06-19: 67 early_halt, 17 full_closure. Grades (status/time): cme/cme 9, cme/empirical 2, cme/inferred 13, cme/n/a 16, cme/secondary 39, cme/unverified 1, secondary/secondary 3, unverified/n/a 1.
- Verbatim check: 79 of 84 entry rows pass (both quotes found in the fetched CME or cited document). The 5 failures are pre-existing D.1f citations: 2021-01-01 has no source (graded unverified), and four D.1f quotes are not verbatim as fetched (section 'Pre-existing D.1f citation defects'). Every citation written in E.2a passes: the three fixed entries, all 20 citations of 2025-01-01..2026-06-19, 13 no-entry findings, the session, product and late-open sources.
- Carried fixes done: 2024-07-04 is now a 12:00 CT early halt (cme/cme, CME trading-hours record for ES); 2019-07-03 and 2023-07-03 are 12:15 CT closes graded cme/cme (CME Globex schedules). The 2025-2026 block is byte-identical (ENTRIES_2025_2026_SHA256 still matches).
- MES holdout-2 calendar trade dates: 258 -> 259. `uv run python -m data.holdout status`: "all_ok": true, "unlocks_logged": 0 (top level and holdout-2 section; "unsealed_plaintext_present": [], "confirmation_has_no_holdout2_rows": true), run at 02:39 PDT after all edits; the same result right after the calendar edit.
- Session-hour change found and dated: the 15:15-15:30 CT equity halt was removed from trade date 2021-06-28 (CME Globex notice of 2021-06-21; CME/CBOT CFTC submission of 2021-06-11), all eight products.
- D6 confirmation: C 15:00 CT confirmed from trade date 2020-10-26. Before that (2019-05-01..2020-10-23) CME settled all eight products at 15:14:30-15:15:00 CT (SER-8591): a discrepancy for the lead; D6's 15:00 is encoded unchanged. O 08:30 CT is not a settlement boundary.
- The eight products share one CME Globex schedule on every date checked; no product differs on any 2019-2026 date found.
- Tests: `uv run pytest -q tests/test_e2a_calendar_equity.py`: 19 passed. Full suite (`nice -n 10 uv run pytest -q -p no:cacheprovider`): 1773 passed, 2 skipped, 1 xfailed, 49 warnings in 290.15s (0:04:50), run 02:34-02:39 PDT. `uv run ruff check` on the four files: all checks passed.

## What changed

- `data/cme_calendar.py`: sha256 before `3dc4d8527d8c5bd06cb3f51533ed6597a2928b82caf7f60870bed95882ad661a`, after `61218c13635ca73558fcf6ff73884e7cd6f09d5f5f5ceb0d7d7abd28ad968c89`. Changed: the three entries (2019-07-03 time grade inferred -> cme; 2023-07-03 likewise; 2024-07-04 FULL_CLOSURE -> EARLY_HALT 12:00 CT, cme/cme), their three citations, one URL constant `_ES_HOURS_2024_07` for the 2024-07-04 citation, and one comment line per entry. Nothing else (no docstring, no other entry). 2025-2026 block hash: 8752f8370c90a5d6a105fdf9929af880355150a54f7e7196a7fa035b067b9538 (unchanged, checked).
- `data/calendars/equity.py` (new, sha256 `3315e81225400add3ba2cc949117c090db0806d495879382d5f3ad02b59e041c`): re-exports HOLIDAYS, CALENDAR_COVERAGE, assert_calendar_coverage, CalendarCoverageError and the D.1f sources from data.cme_calendar (no copied entries); adds SOURCES_2025_2026 (CME citations for the 20 entries of 2025-01-01..2026-06-19, which the pinned block lacks), SOURCES, NO_ENTRY_FINDINGS_E2A (10 CME-stated regular days) and NO_ENTRY_FINDINGS, SESSIONS (3 specs) with SESSION_SOURCES, PRODUCT_SOURCES, and LATE_OPENS with LATE_OPEN_SOURCES (additive interface extension, the rates module's LateOpen shape, for the 2025-11-28 outage). data.group_session uses equity.py's SESSIONS whenever the file exists, so the equity group's bar builds now use these three regimes instead of the MES fallback session; it does not read LATE_OPENS for equity.
- `tests/test_e2a_calendar_equity.py` (new, sha256 `8137b2351ce7faf58d2a14fa7edcdef045a95f638e602df3858e3da7d2bd47c5`, 19 tests).
- `tests/test_d1f_calendar_build.py::test_judgment_calls_are_the_documented_ones`, expected value corrected (design D14 row 4: the two grades the test pinned as 'inferred' are now 'cme'; the halt time is still asserted for both, and the grade is asserted at its new value (same strength). The other hunks in `git diff` of this file are TestFixer-SonnetMed's D14 edits, not this worker's.)

  Old:
  ```python
      for day in (date(2019, 7, 3), date(2019, 11, 29), date(2019, 12, 24), date(2020, 11, 27),
                  date(2020, 12, 24), date(2021, 11, 26), date(2022, 11, 25), date(2023, 7, 3),
                  date(2023, 11, 24), date(2024, 7, 3), date(2024, 11, 29), date(2024, 12, 24)):
          assert HOLIDAYS[day].halt_ct == time(12, 15), day
          assert HOLIDAYS[day].time_evidence == "inferred", day
  ```
  New:
  ```python
      for day in (date(2019, 11, 29), date(2019, 12, 24), date(2020, 11, 27),
                  date(2020, 12, 24), date(2021, 11, 26), date(2022, 11, 25),
                  date(2023, 11, 24), date(2024, 7, 3), date(2024, 11, 29), date(2024, 12, 24)):
          assert HOLIDAYS[day].halt_ct == time(12, 15), day
          assert HOLIDAYS[day].time_evidence == "inferred", day
      # Stage E.2a (design D14): CME's own Globex schedules confirm these two 12:15 CT closes.
      for day in (date(2019, 7, 3), date(2023, 7, 3)):
          assert HOLIDAYS[day].halt_ct == time(12, 15), day
          assert HOLIDAYS[day].time_evidence == "cme", day
  ```

## Entries in the window (84)

Bar check codes: T7 = pending Task 7 (research-window bars); S2 = validated against CME schedules only, bar check pending the step 2 purchase (MES: these entries passed D.1f step 4b on the MES confirmation bars); H2 = validated against CME schedules only; embargo or holdout-2 date, never checked against bars. Quotes, capture URLs and document hashes per row are in the JSON.

| Date | Name | Kind | Halt CT | Status | Time | Verbatim | Bar | Status source | Time source |
|---|---|---|---|---|---|---|---|---|---|
| 2019-05-27 | Memorial Day | early_halt | 12:00 | cme | secondary | yes | S2 | 2019-memorial-day-holiday-settlement-times.pdf | crosstrade.io (secondary) |
| 2019-07-03 | Day before Independence Day | early_halt | 12:15 | cme | cme | yes | S2 | 2019-fourth-of-july-holiday-settlement-times.pdf | 2019-4th-of-july-holiday-schedule-compact.xls |
| 2019-07-04 | Independence Day | early_halt | 12:00 | cme | cme | yes | S2 | 2019-fourth-of-july-holiday-settlement-times.pdf | 2019-4th-of-july-holiday-schedule-compact.xls |
| 2019-09-02 | Labor Day | early_halt | 12:00 | cme | secondary | yes | S2 | 2019-labor-day-holiday-settlement-times.pdf | crosstrade.io (secondary) |
| 2019-11-28 | Thanksgiving Day | early_halt | 12:00 | secondary | secondary | yes | S2 | crosstrade.io (secondary) | crosstrade.io (secondary) |
| 2019-11-29 | Day after Thanksgiving | early_halt | 12:15 | cme | inferred | yes | S2 | 2019-thanksgiving-holiday-settlement-times.pdf | 2019-thanksgiving-holiday-settlement-times.pdf |
| 2019-12-24 | Christmas Eve | early_halt | 12:15 | cme | inferred | yes | S2 | 2019-christmas-holiday-settlement-times.pdf | 2019-christmas-holiday-settlement-times.pdf |
| 2019-12-25 | Christmas Day | full_closure | - | cme | n/a | yes | S2 | 2019-christmas-holiday-settlement-times.pdf | - |
| 2020-01-01 | New Year's Day | full_closure | - | cme | n/a | yes | S2 | 2020-new-years-advisory.pdf | - |
| 2020-01-20 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | secondary | yes | S2 | mlk-day-holiday-settlement-times-2020.pdf | crosstrade.io (secondary) |
| 2020-02-17 | Presidents Day | early_halt | 12:00 | cme | secondary | yes | S2 | presidents-day-holiday-settlement-times-2020.pdf | crosstrade.io (secondary) |
| 2020-04-10 | Good Friday | full_closure | - | cme | n/a | yes | S2 | good-friday-holiday-settlement-times-2020.pdf | - |
| 2020-05-25 | Memorial Day | early_halt | 12:00 | cme | secondary | yes | S2 | memorial-day-holiday-settlement-times-2020.pdf | crosstrade.io (secondary) |
| 2020-07-03 | Independence Day (observed) | early_halt | 12:00 | cme | cme | NO | S2 | fourth-of-july-settlement-times-2020.pdf | 2020-independence-day-schedule.xls |
| 2020-09-07 | Labor Day | early_halt | 12:00 | cme | secondary | yes | S2 | labor-day-holiday-settlement-times-2020.pdf | crosstrade.io (secondary) |
| 2020-11-26 | Thanksgiving Day | early_halt | 12:00 | secondary | secondary | yes | S2 | crosstrade.io (secondary) | crosstrade.io (secondary) |
| 2020-11-27 | Day after Thanksgiving | early_halt | 12:15 | cme | inferred | yes | S2 | thanksgiving-holiday-settlement-times-2020.pdf | thanksgiving-holiday-settlement-times-2020.pdf |
| 2020-12-24 | Christmas Eve | early_halt | 12:15 | cme | inferred | yes | S2 | christmas-holiday-settlement-times-2020.pdf | christmas-holiday-settlement-times-2020.pdf |
| 2020-12-25 | Christmas Day | full_closure | - | cme | n/a | yes | S2 | christmas-holiday-settlement-times-2020.pdf | - |
| 2021-01-01 | New Year's Day | full_closure | - | unverified | n/a | NO | S2 | - | - |
| 2021-01-18 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | secondary | yes | S2 | mlk-day-holiday-settlement-times-2021.pdf | crosstrade.io (secondary) |
| 2021-02-15 | Presidents Day | early_halt | 12:00 | cme | secondary | yes | S2 | presidents-day-holiday-settlement-times-2021.pdf | crosstrade.io (secondary) |
| 2021-04-02 | Good Friday (abbreviated, jobs report) | early_halt | 08:15 | cme | unverified | NO | S2 | 2021-good-friday-advisory.pdf | AMP Futures (secondary) |
| 2021-05-31 | Memorial Day | early_halt | 12:00 | cme | secondary | yes | S2 | memorial-day-holiday-settlement-times-2021.pdf | crosstrade.io (secondary) |
| 2021-07-05 | Independence Day (observed) | early_halt | 12:00 | cme | cme | NO | S2 | fourth-of-july-settlement-times-2021.pdf | 2021-independence-day-holiday-schedule-compact.xls |
| 2021-09-06 | Labor Day | early_halt | 12:00 | cme | secondary | yes | S2 | labor-day-holiday-settlement-times-2021.pdf | crosstrade.io (secondary) |
| 2021-11-25 | Thanksgiving Day | early_halt | 12:00 | secondary | secondary | yes | S2 | crosstrade.io (secondary) | crosstrade.io (secondary) |
| 2021-11-26 | Day after Thanksgiving | early_halt | 12:15 | cme | inferred | yes | S2 | thanksgiving-holiday-settlement-times-2021.pdf | thanksgiving-holiday-settlement-times-2021.pdf |
| 2021-12-24 | Christmas Day (observed) | full_closure | - | cme | n/a | yes | S2 | christmas-holiday-settlement-times-2021.pdf | - |
| 2022-01-17 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | secondary | yes | S2 | mlk-day-holiday-settlement-times-2022.pdf | crosstrade.io (secondary) |
| 2022-02-21 | Presidents Day | early_halt | 12:00 | cme | secondary | yes | S2 | presidents-day-holiday-settlement-times-2022.pdf | crosstrade.io (secondary) |
| 2022-04-15 | Good Friday | full_closure | - | cme | n/a | yes | S2 | good-friday-holiday-settlement-times-2022.pdf | - |
| 2022-05-30 | Memorial Day | early_halt | 12:00 | cme | secondary | yes | S2 | memorial-day-holiday-settlement-times-2022.pdf | crosstrade.io (secondary) |
| 2022-06-20 | Juneteenth (observed) | early_halt | 12:00 | cme | secondary | yes | S2 | juneteenth-day-holiday-settlement-times-2022.pdf | crosstrade.io (secondary) |
| 2022-07-04 | Independence Day | early_halt | 12:00 | cme | cme | yes | S2 | fourth-of-july-settlement-times-2022.pdf | 2022-independence-day-holiday-schedule-compact.xls |
| 2022-09-05 | Labor Day | early_halt | 12:00 | cme | secondary | yes | S2 | labor-day-holiday-settlement-times-2022.pdf | crosstrade.io (secondary) |
| 2022-11-24 | Thanksgiving Day | early_halt | 12:00 | cme | secondary | yes | S2 | thanksgiving-holiday-settlement-times-2022.pdf | crosstrade.io (secondary) |
| 2022-11-25 | Day after Thanksgiving | early_halt | 12:15 | cme | inferred | yes | S2 | thanksgiving-holiday-settlement-times-2022.pdf | thanksgiving-holiday-settlement-times-2022.pdf |
| 2022-12-26 | Christmas Day (observed) | full_closure | - | cme | n/a | yes | S2 | christmas-holiday-settlement-times-2022.pdf | - |
| 2023-01-02 | New Year's Day (observed) | full_closure | - | cme | n/a | yes | S2 | 2023-new-years-advisory.pdf | - |
| 2023-01-16 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | secondary | yes | S2 | mlk-day-holiday-settlement-times-2023.pdf | crosstrade.io (secondary) |
| 2023-02-20 | Presidents Day | early_halt | 12:00 | cme | secondary | yes | S2 | presidents-day-holiday-settlement-times-2023.pdf | crosstrade.io (secondary) |
| 2023-04-07 | Good Friday (abbreviated, jobs report) | early_halt | 08:15 | cme | secondary | NO | S2 | 2023-good-friday-advisory.pdf | AMP Futures (secondary) |
| 2023-05-29 | Memorial Day | early_halt | 12:00 | cme | secondary | yes | S2 | memorial-day-holiday-settlement-times-2023.pdf | crosstrade.io (secondary) |
| 2023-06-19 | Juneteenth | early_halt | 12:00 | cme | secondary | yes | S2 | juneteenth-day-holiday-settlement-times-2023.pdf | crosstrade.io (secondary) |
| 2023-07-03 | Day before Independence Day | early_halt | 12:15 | cme | cme | yes | S2 | fourth-of-july-settlement-times-2023.pdf | 4th-of-july-2023.pdf |
| 2023-07-04 | Independence Day | early_halt | 12:00 | cme | cme | yes | S2 | fourth-of-july-settlement-times-2023.pdf | 4th-of-july-2023.pdf |
| 2023-09-04 | Labor Day | early_halt | 12:00 | cme | secondary | yes | S2 | labor-day-holiday-settlement-times-2023.pdf | crosstrade.io (secondary) |
| 2023-11-23 | Thanksgiving Day | early_halt | 12:00 | cme | secondary | yes | S2 | thanksgiving-holiday-settlement-times-2023.pdf | crosstrade.io (secondary) |
| 2023-11-24 | Day after Thanksgiving | early_halt | 12:15 | cme | inferred | yes | S2 | thanksgiving-holiday-settlement-times-2023.pdf | thanksgiving-holiday-settlement-times-2023.pdf |
| 2023-12-25 | Christmas Day | full_closure | - | cme | n/a | yes | S2 | christmas-holiday-settlement-times-2023.pdf | - |
| 2024-01-01 | New Year's Day (observed) | full_closure | - | cme | n/a | yes | S2 | 2024-new-years-advisory.pdf | - |
| 2024-01-15 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | secondary | yes | S2 | mlk-day-holiday-settlement-times-2024.pdf | crosstrade.io (secondary) |
| 2024-02-19 | Presidents Day | early_halt | 12:00 | cme | secondary | yes | S2 | presidents-day-holiday-settlement-times-2024.pdf | crosstrade.io (secondary) |
| 2024-03-29 | Good Friday | full_closure | - | cme | n/a | yes | H2 | good-friday-holiday-settlement-times-2024.pdf | - |
| 2024-05-27 | Memorial Day | early_halt | 12:00 | cme | secondary | yes | H2 | memorial-day-holiday-settlement-times-2024.pdf | crosstrade.io (secondary) |
| 2024-06-19 | Juneteenth | early_halt | 12:00 | cme | secondary | yes | H2 | juneteenth-day-settlement-times-2024.pdf | crosstrade.io (secondary) |
| 2024-07-03 | Day before Independence Day | early_halt | 12:15 | cme | inferred | yes | H2 | us-independence-day-settlement-times-2024.pdf | us-independence-day-settlement-times-2024.pdf |
| 2024-07-04 | Independence Day | early_halt | 12:00 | cme | cme | yes | H2 | CME trading-hours service (2024-07-03) | CME trading-hours service (2024-07-03) |
| 2024-09-02 | Labor Day | early_halt | 12:00 | cme | secondary | yes | H2 | labor-day-holiday-settlement-times-2024.pdf | crosstrade.io (secondary) |
| 2024-11-28 | Thanksgiving Day | early_halt | 12:00 | cme | secondary | yes | H2 | thanksgiving-holiday-settlement-times-2024.pdf | crosstrade.io (secondary) |
| 2024-11-29 | Day after Thanksgiving | early_halt | 12:15 | cme | inferred | yes | H2 | thanksgiving-holiday-settlement-times-2024.pdf | thanksgiving-holiday-settlement-times-2024.pdf |
| 2024-12-24 | Christmas Eve | early_halt | 12:15 | cme | inferred | yes | H2 | christmas-holiday-settlement-times-2024.pdf | christmas-holiday-settlement-times-2024.pdf |
| 2024-12-25 | Christmas Day | full_closure | - | cme | n/a | yes | H2 | christmas-holiday-settlement-times-2024.pdf | - |
| 2025-01-01 | New Year's Day | full_closure | - | cme | n/a | yes | H2 | CME trading-hours service (2024-12-31) | CME trading-hours service (2024-12-31) |
| 2025-01-09 | National Day of Mourning (Carter) | early_halt | 08:30 | cme | cme | yes | H2 | day-of-mourning-january-9-2024.pdf | day-of-mourning-january-9-2024.pdf |
| 2025-01-20 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | secondary | yes | H2 | CME trading-hours service (2025-01-19) | CME trading-hours service (2025-01-19) |
| 2025-02-17 | Presidents Day | early_halt | 12:00 | cme | secondary | yes | H2 | CME trading-hours service (2025-02-16) | CME trading-hours service (2025-02-16) |
| 2025-04-18 | Good Friday | full_closure | - | cme | n/a | yes | T7 | CME trading-hours service (2025-04-17) | CME trading-hours service (2025-04-17) |
| 2025-05-26 | Memorial Day | early_halt | 12:00 | cme | secondary | yes | T7 | CME trading-hours service (2025-05-25) | CME trading-hours service (2025-05-25) |
| 2025-06-19 | Juneteenth | early_halt | 12:00 | cme | secondary | yes | T7 | CME trading-hours service (2025-06-18) | CME trading-hours service (2025-06-18) |
| 2025-07-03 | Day before Independence Day | early_halt | 12:15 | cme | inferred | yes | T7 | CME trading-hours service (2025-07-03) | CME trading-hours service (2025-07-03) |
| 2025-07-04 | Independence Day | early_halt | 12:00 | cme | empirical | yes | T7 | CME trading-hours service (2025-07-03) | CME trading-hours service (2025-07-03) |
| 2025-09-01 | Labor Day | early_halt | 12:00 | cme | secondary | yes | T7 | CME trading-hours service (2025-08-31) | CME trading-hours service (2025-08-31) |
| 2025-11-27 | Thanksgiving | early_halt | 12:00 | cme | secondary | yes | T7 | CME trading-hours service (2025-11-26) | CME trading-hours service (2025-11-26) |
| 2025-11-28 | Day after Thanksgiving | early_halt | 12:15 | cme | inferred | yes | T7 | CME trading-hours service (2025-11-26) | CME trading-hours service (2025-11-26) |
| 2025-12-24 | Christmas Eve | early_halt | 12:15 | cme | inferred | yes | T7 | CME trading-hours service (2025-12-24) | CME trading-hours service (2025-12-24) |
| 2025-12-25 | Christmas Day | full_closure | - | cme | n/a | yes | T7 | CME trading-hours service (2025-12-24) | CME trading-hours service (2025-12-24) |
| 2026-01-01 | New Year's Day | full_closure | - | cme | n/a | yes | T7 | CME trading-hours service (2025-12-31) | CME trading-hours service (2025-12-31) |
| 2026-01-19 | Martin Luther King Jr. Day | early_halt | 12:00 | cme | secondary | yes | T7 | CME trading-hours service (2026-01-18) | CME trading-hours service (2026-01-18) |
| 2026-02-16 | Presidents Day | early_halt | 12:00 | cme | secondary | yes | T7 | CME trading-hours service (2026-02-15) | CME trading-hours service (2026-02-15) |
| 2026-04-03 | Good Friday (abbreviated, jobs report) | early_halt | 08:15 | cme | empirical | yes | T7 | CME trading-hours service (2026-04-01) | CME trading-hours service (2026-04-01) |
| 2026-05-25 | Memorial Day | early_halt | 12:00 | cme | secondary | yes | T7 | CME trading-hours service (2026-05-24) | CME trading-hours service (2026-05-24) |
| 2026-06-19 | Juneteenth | early_halt | 12:00 | cme | secondary | yes | T7 | CME trading-hours service (2026-06-17) | CME trading-hours service (2026-06-17) |

## The three fixed entries, with their quotes

### 2019-07-03 Day before Independence Day: early_halt 12:15, cme/cme

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-fourth-of-july-holiday-settlement-times.pdf (fetched via https://web.archive.org/web/20240627181023id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-fourth-of-july-holiday-settlement-times.pdf, sha256 de730cf103b3a1c155f5c6ab5549e81b882f11670bb1f07c142f347cfe08de00, ws_collapsed)
  > Wednesday, July 3, 2019 Settlement Times ... Equity Products 12:00:00 CT (for futures that currently settle at 15:00 CT) 12:15:00 CT (for futures that currently settle at 15:15 CT)
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019/2019-4th-of-july-holiday-schedule-compact.xls (fetched via https://web.archive.org/web/20220920142350id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019/2019-4th-of-july-holiday-schedule-compact.xls, sha256 8546b2a9e42c92a4bcf2d2e8209906f482467aeb549ed2a02eb95690954ddd16, ws_collapsed)
  > Calendar Date|Wednesday July 3 |Wednesday,July 3|Thursday July 4 |Thursday July 4 into  Friday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... Equity |Early  @ 1215 CT / 1715 UTC|Regular @ 1700 CT/ 2200 UTC

### 2023-07-03 Day before Independence Day: early_halt 12:15, cme/cme

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2023.pdf (fetched via https://web.archive.org/web/20230203064221id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2023.pdf, sha256 e5d23dde6527e1f3576d791e385207ba64108b791e450cf4ea09326d70c5f31a, ws_collapsed)
  > Monday, July 3, 2023 ... Equity Index Products 12:00:00 CT
- time: https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf (fetched via https://web.archive.org/web/20230627125057id_/https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf, sha256 ccbc1f1fc39ba2219fd748372faa985798fee7eaffabf69f08956f5465a769e3, ws_collapsed)
  > PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... EQUITIES ... TRADE DATE: MON 3 JULY ... 12:15 (CLOSED) ... TRADE DATE: WED 5 JULY ... 16:45 (PREOPEN) ... 17:00 (OPEN)

### 2024-07-04 Independence Day: early_halt 12:00, cme/cme

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680 (fetched via https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680, sha256 54de3d48c849891d7f37ec1afa38d3e10103c7d606b141a91ad8dec9349e529a, ws_collapsed)
  > "globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures","id":133 ... {"groupCode":"ES","eventDate":"2024-07-03","events":[{"tradingDate":"2024-07-03","eventTime":"12:15","marketEventType":"closed"},{"tradingDate":"2024-07-05","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","marketEventType":"open"}]},{"groupCode":"ES","eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05","eventTime":"12:00","marketEventType":"preopen"}
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680 (fetched via https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680, sha256 54de3d48c849891d7f37ec1afa38d3e10103c7d606b141a91ad8dec9349e529a, ws_collapsed)
  > {"groupCode":"ES","eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","marketEventType":"open"}]}

## Session-hour changes found (CME, dated)

- 2019-05-01..2020-10-25: [-1d 17:00 .. +0d 15:15]; [+0d 15:30 .. +0d 16:00]; day_session_ct {'equity': ['08:30', '15:00']}; source 'cme_hours_with_halt'. Globex 17:00 CT (prior day) to 16:00 CT with the 15:15-15:30 CT halt, all eight products (SESSION_SOURCES 'cme_hours_with_halt', 'cme_halt_removal_notice'). D6 confirmation: DISCREPANCY. CME's daily settlement period for ES, MES, NQ, MNQ, RTY, M2K, YM and MYM in this span was 15:14:30-15:15:00 CT, so CME's C was 15:15 CT (SESSION_SOURCES 'cme_settlement_1515', 'cme_settlement_moved_to_1500'); D6's C 15:00 CT is encoded unchanged and the lead rules. O 08:30 CT: no CME settlement procedure defines it; CME's price limits used 8:30 a.m.-3:00 p.m. CT as the day regime ('cme_price_limit_day_regime'). MES's first trade date in the D.1f confirmation build is 2019-05-06 (a listing date, not a session change).
- 2020-10-26..2021-06-27: [-1d 17:00 .. +0d 15:15]; [+0d 15:30 .. +0d 16:00]; day_session_ct {'equity': ['08:30', '15:00']}; source 'cme_hours_with_halt'. Same Globex hours as before (15:15-15:30 CT halt). From trade date 2020-10-26 CME's daily settlement period for all eight products is 14:59:30-15:00:00 CT (SER-8591, 'cme_settlement_moved_to_1500'): D6's C 15:00 CT is confirmed; O 08:30 CT as in the previous spec. The last trade date of this regime is Friday 2021-06-25.
- 2021-06-28..2026-06-19: [-1d 17:00 .. +0d 16:00]; day_session_ct {'equity': ['08:30', '15:00']}; source 'cme_halt_removal_notice'. CME eliminated the 15:15-15:30 CT halt from trade date 2021-06-28: 'the affected equity futures and options products will trade from Sunday-Friday, 5pm-4pm CT, daily, with a 4pm-5pm CT maintenance period' (all eight listed). No later CME change to these hours was found; CME's trading-hours service shows the regular 16:00 CT close and 17:00 CT open around every holiday of 2023-2026. D6 confirmation: C 15:00 CT matches the settlement period 14:59:30-15:00:00 CT ('cme_settlement_1500'); O 08:30 CT is not a CME settlement boundary ('cme_price_limit_day_regime'). Outside this window: CME captures of 2026-06-19 show Saturday '05:00 open' / '17:00 closed' events on 2026-06-20 and 2026-07-04 for ES; unexplained, not encoded.

Dated changes, each cited in SESSION_SOURCES:

1. Trade date 2021-06-28 (effective Sunday 2021-06-27 evening): the 15:15-15:30 CT Globex halt is eliminated for ES, MES, NQ, MNQ, RTY, M2K (CME) and YM, MYM (CBOT); from then 'Sunday-Friday, 5pm-4pm CT, daily, with a 4pm-5pm CT maintenance period' (CME Globex notice 2021-06-21; CFTC submission 2021-06-11 with Exhibit A). Before it, CME's contract specifications read 'Sunday - Friday 6:00 p.m. - 5:00 p.m. Eastern Time (ET) with trading halt 4:15 p.m. - 4:30 p.m.' for all eight (captures 2019), i.e. 17:00-16:00 CT with the 15:15-15:30 CT halt. Note: the regular close was 16:00 CT before the change as well; tests/test_d1f_calendar_build.py and data/validate.py describe the pre-2021 session as 'traded to 16:15 CT' ([unverified] in reports/stage_d1f_build_STATE.md); CME's own specification pages and holiday schedules (regular close 16:00, e.g. Christmas 2019/2020 rows '15:15|15:30|16:00') say 16:00. data/validate.py's tolerance is wider, so nothing breaks; the lead may want the comment corrected.
2. Trade date 2020-10-26: CME moved the daily settlement period of all eight products from 15:14:30-15:15:00 CT to 14:59:30-15:00:00 CT (SER-8591, 2020-09-22). Not a Globex-hours change; SESSIONS splits there only to date the D6 discrepancy.
3. Trade date 2019-05-06: MES's first trade date in the D.1f confirmation build; the micro contracts' listing is a product event, not a session change (the other micros' listing dates were not checked here).
4. Outside the window: CME captures of 2026-06-19 and 2026-07-22 show Saturday events ('05:00 open', '17:00 closed', trade date the next Monday) on 2026-06-20 and 2026-07-04 for ES (and ZN, CL, 6E, GC); the 2026-01-29 capture of 2026-07-04 had none. Unexplained, after 2026-06-19, not encoded; the FX builder noted the same.

No other CME change to the equity Globex hours in 2019-05..2026-06 was found: CME's trading-hours service shows ES's regular 16:00 CT close and 17:00 CT open around every holiday captured from 2023-09 to 2026-06.

## D6 confirmation

D6 row: equity index (MNQ, M2K, MYM, NQ, RTY, YM): O 08:30, C 15:00, F 15:08 CT. Encoded unchanged in every SessionSpec (`{'equity': (08:30, 15:00)}`).

| Sub-group | CME settlement period, 2019-05-01..2020-10-23 | from 2020-10-26 | Source |
|---|---|---|---|
| ES, MES | 15:14:30-15:15:00 CT (SER-8591 Exhibit B blackline, struck) | 14:59:30-15:00:00 CT | SER-8591; CME wiki 'E-Mini Standard and Poors 500 Futures' (REST, v4 2026-08-20) |
| NQ, MNQ | 15:14:30-15:15:00 CT (wiki Nasdaq-100, capture 2019-11-20) | 14:59:30-15:00:00 CT | SER-8591; wiki Nasdaq-100 (capture 2021-09-23; REST v5 2026-08-20) |
| RTY, M2K | 15:14:30-15:15:00 CT (wiki Dow Jones Futures page, capture 2019-08-24, 'These include: RTY, NQ, YM ...') | 14:59:30-15:00:00 CT | SER-8591; wiki Nasdaq-100 / E-mini Russell 2000 (REST) |
| YM, MYM | 15:14:30-15:15:00 CT (same 2019-08-24 page) | 14:59:30-15:00:00 CT | SER-8591; wiki Dow Jones Futures (capture 2021-12-02; REST v5 2025-11-11) |

- **C 15:00 CT: confirmed from trade date 2020-10-26; DIFFERS before it.** For 2019-05-01..2020-10-23 CME's settlement time, and so the C D6 defines ('daily settlement time'), was 15:15 CT for all eight products. Affected: the part of any confirmation window before 2020-10-26. Encoded value unchanged (15:00); the discrepancy is in SESSIONS[0].note. The lead rules.
- **O 08:30 CT:** no CME settlement procedure defines an open. CME's price-limits page uses 8:30 a.m. CT as the start of the equity day regime in every capture read ('effective from 8:30 a.m. CT – 3:00 p.m. CT', 2019-08-23; '8:30 a.m. CT – 2:25 p.m. CT ... to 3:00 p.m. CT', 2023-06-04), which supports 08:30. No discrepancy found.
- F 15:08 CT is D9.1's Topstep rule, not a CME value; not part of this check.

## Products: does the equity schedule apply to NQ, MNQ, RTY, M2K, YM and MYM? (task e)

Yes on every date checked; no product was found to differ on any 2019-2026 date. Evidence (PRODUCT_SOURCES, SESSION_SOURCES; quotes in the JSON):

- 2019-2022 Globex holiday schedules give one 'Equity Products' (full sheet) / 'Equity' (compact) row; the listed exceptions are BTIC, TACO, FTSE and Nikkei/TOPIX instruments (2019 also 'Big Equities', by its name the full-size contracts); none of the eight products is an exception.
- 2023: CME's holiday summary PDFs give an 'EQUITIES' row using 'the most actively traded instruments for each asset class' (ES). 2023-09..2026-06: CME's trading-hours service names ES (product 133); for YM (product 318, CBOT) one capture exists, MLK Day 2026, with the same 12:00 CT halt and 17:00 CT reopen as ES.
- The 2021 halt removal lists all eight (notice product list and CFTC Exhibit A: ES, MES, NQ, MNQ, RTY, M2K under CME; YM, MYM under CBOT), and the 2019 contract specifications of all eight state the same Globex hours.
- The settlement procedures (SER-8591 and the CME wiki pages) treat all eight alike.
- Caveat: no CME document read states a holiday schedule for NQ, MNQ, RTY, M2K or MYM by name; for 2023-2026 the per-product statement is ES's (and YM's once). Proposal: none needed unless the lead wants per-product captures; the Task 7 bar check on each product's research bars is the direct test.

## Entries graded unverified, secondary or inferred, and why

The file's grades are unchanged except the three carried fixes. For every lower-graded 2019-2024 entry E.2a looked for a CME-direct Globex-hours document; each one found was quoted and verbatim-checked (JSON `proposals_lower_graded_2019_2024`). Proposed grade upgrades are for the lead; they are not encoded.

| Date | Name | Grades now | Why (D.1f) | CME-direct source found (E.2a) | Proposal |
|---|---|---|---|---|---|
| 2019-05-27 | Memorial Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2019-holiday-calendars.zip (ws_collapsed) | time cme |
| 2019-09-02 | Labor Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2019-holiday-calendars.zip (ws_collapsed) | time cme |
| 2019-11-28 | Thanksgiving Day | secondary/secondary | status and time from a generic 2026 broker page | 2019-holiday-calendars.zip (ws_collapsed) | status cme, time cme |
| 2019-11-29 | Day after Thanksgiving | cme/inferred | 12:15 close inferred from CME's 12:00 CT settlement line | 2019-holiday-calendars.zip (ws_collapsed) | time cme |
| 2019-12-24 | Christmas Eve | cme/inferred | 12:15 close inferred from CME's 12:00 CT settlement line | 2019-holiday-calendars.zip (ws_collapsed) | time cme |
| 2020-01-20 | Martin Luther King Jr. Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2020-holiday-calendars.zip (ws_collapsed) | time cme |
| 2020-02-17 | Presidents Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2020-holiday-calendars.zip (ws_collapsed) | time cme |
| 2020-05-25 | Memorial Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2020-holiday-calendars.zip (ws_collapsed) | time cme |
| 2020-09-07 | Labor Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2020-holiday-calendars.zip (ws_collapsed) | time cme |
| 2020-11-26 | Thanksgiving Day | secondary/secondary | status and time from a generic 2026 broker page | 2020-holiday-calendars.zip (ws_collapsed) | status cme, time cme |
| 2020-11-27 | Day after Thanksgiving | cme/inferred | 12:15 close inferred from CME's 12:00 CT settlement line | 2020-holiday-calendars.zip (ws_collapsed) | time cme |
| 2020-12-24 | Christmas Eve | cme/inferred | 12:15 close inferred from CME's 12:00 CT settlement line | 2020-holiday-calendars.zip (ws_collapsed) | time cme |
| 2021-01-01 | New Year's Day | unverified/n/a | status not fetched, assumed from the pattern | 2020-holiday-calendars.zip (ws_collapsed) | status cme |
| 2021-01-18 | Martin Luther King Jr. Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2021-holiday-calendars.zip (ws_collapsed) | time cme |
| 2021-02-15 | Presidents Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2021-holiday-calendars.zip (ws_collapsed) | time cme |
| 2021-04-02 | Good Friday (abbreviated, jobs report) | cme/unverified | not fetched / no year-specific source | 2021-holiday-calendars.zip (ws_collapsed) | time cme |
| 2021-05-31 | Memorial Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2021-holiday-calendars.zip (ws_collapsed) | time cme |
| 2021-09-06 | Labor Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2021-holiday-calendars.zip (ws_collapsed) | time cme |
| 2021-11-25 | Thanksgiving Day | secondary/secondary | status and time from a generic 2026 broker page | 2021-holiday-calendars.zip (ws_collapsed) | status cme, time cme |
| 2021-11-26 | Day after Thanksgiving | cme/inferred | 12:15 close inferred from CME's 12:00 CT settlement line | 2021-holiday-calendars.zip (ws_collapsed) | time cme |
| 2022-01-17 | Martin Luther King Jr. Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2022-mlk-day-holiday-schedule-compact.xls (ws_collapsed) | time cme |
| 2022-02-21 | Presidents Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2022-presidents-day-holiday-schedule-compact.xls (ws_collapsed) | time cme |
| 2022-05-30 | Memorial Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2022-memorial-day-holiday-schedule-compact.xls (ws_collapsed) | time cme |
| 2022-06-20 | Juneteenth (observed) | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2022-juneteenth-holiday-schedule.xls (ws_collapsed) | time cme |
| 2022-09-05 | Labor Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2022-labor-day-holiday-schedule-compact.xls (ws_collapsed) | time cme |
| 2022-11-24 | Thanksgiving Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | 2022-thanksgiving-holiday-schedule-compact.xls (ws_collapsed) | time cme |
| 2022-11-25 | Day after Thanksgiving | cme/inferred | 12:15 close inferred from CME's 12:00 CT settlement line | 2022-thanksgiving-holiday-schedule-compact.xls (ws_collapsed) | time cme |
| 2023-01-16 | Martin Luther King Jr. Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | none found | keep |
| 2023-02-20 | Presidents Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | presidents-day.pdf (ws_collapsed) | time cme |
| 2023-04-07 | Good Friday (abbreviated, jobs report) | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | good-friday.pdf (ws_collapsed) | time cme |
| 2023-05-29 | Memorial Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | memorial-day-2023.pdf (ws_collapsed) | time cme |
| 2023-06-19 | Juneteenth | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | juneteenth-2023.pdf (ws_collapsed) | time cme |
| 2023-09-04 | Labor Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | labor-day-2023.pdf (ws_collapsed) | time cme |
| 2023-11-23 | Thanksgiving Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | thanksgiving-day-2023.pdf (ws_collapsed) | time cme |
| 2023-11-24 | Day after Thanksgiving | cme/inferred | 12:15 close inferred from CME's 12:00 CT settlement line | thanksgiving-day-2023.pdf (ws_collapsed) | time cme |
| 2024-01-15 | Martin Luther King Jr. Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | CME trading-hours service (2024-01-14) (ws_collapsed) | time cme |
| 2024-02-19 | Presidents Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | CME trading-hours service (2024-02-18) (ws_collapsed) | time cme |
| 2024-05-27 | Memorial Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | CME trading-hours service (2024-05-26) (ws_collapsed) | time cme |
| 2024-06-19 | Juneteenth | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | CME trading-hours service (2024-06-18) (ws_collapsed) | time cme |
| 2024-07-03 | Day before Independence Day | cme/inferred | 12:15 close inferred from CME's 12:00 CT settlement line | CME trading-hours service (2024-07-03) (ws_collapsed) | time cme |
| 2024-09-02 | Labor Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | CME trading-hours service (2024-09-01) (ws_collapsed) | time cme |
| 2024-11-28 | Thanksgiving Day | cme/secondary | time from a generic 2026 broker page (crosstrade.io) or AMP | CME trading-hours service (2024-11-27) (ws_collapsed) | time cme |
| 2024-11-29 | Day after Thanksgiving | cme/inferred | 12:15 close inferred from CME's 12:00 CT settlement line | CME trading-hours service (2024-11-27) (ws_collapsed) | time cme |
| 2024-12-24 | Christmas Eve | cme/inferred | 12:15 close inferred from CME's 12:00 CT settlement line | CME trading-hours service (2024-12-24) (ws_collapsed) | time cme |

2025-2026 block (pinned, grades not changeable): every entry's time is now CME-direct from the trading-hours service (SOURCES_2025_2026); the notes propose time 'cme' for the 'secondary', 'inferred' and 'empirical' grades (15 entries). 2023-01-16 (MLK Day 2023) is the one entry with no CME Globex-hours document found (CME's 2023 MLK advisory and settlement notice give no hours; the only 2023 MLK schedule file is the MGEX/DME one): time stays secondary.

## Proposals and findings for the lead

1. **2025-11-28 CME Globex outage (unscheduled, research window).** CME's ES record for eventDate 2025-11-28 in the 2026-01-29 capture adds '07:00 preopen' and '07:30 open' before the scheduled 12:15 CT close; trading stopped at an unknown time after the 2025-11-27 17:00 CT reopen. Recorded in data/calendars/equity.py LATE_OPENS (open 07:30 CT, halt_from_ct None) with LATE_OPEN_SOURCES; not in data.cme_calendar (pinned block), and data.group_session does not read LATE_OPENS for the equity group. Rates, energy and metals record the same outage. Task 7's bar check will see a gap there.
2. **Grade upgrades** listed above (2019-2024: 43 of the 44 lower-graded entries have a CME-direct source, including the two unverified ones: 2021-01-01 status (CME 2021 New Year's schedule: 'Closed for New Year's') and 2021-04-02 time (CME 2021 Good Friday schedule: 'Closed @ 0815 CT'); 2025-2026: 15 time grades).
3. **D6 C before 2020-10-26** (section D6 confirmation).
4. **Stale text in data/cme_calendar.py that this worker may not edit** (write list: the three entries and their citations only): the module docstring still says every 12:15 CT close is 'inferred' and lists 2024-07-04 nowhere; the Citation docstring names 'the five 2019-2023 Independence Day entries' as the only check-sourced time quotes (now eight dates); `_NOTE_SETTLE_SPLIT` says 'ES/MES settle at 15:00 CT' for 2019-2020 dates, but ES/MES settled at 15:15 CT until 2020-10-23 (SER-8591), so their 2019 and 2020 early settlement was the 12:15 line; the 12:15 CT closes themselves are confirmed by CME's Globex schedules.
5. **Pre-2021 regular close:** 16:00 CT per CME (not 16:15 as tests/test_d1f_calendar_build.py's comment and data/validate.py's docstring say).

## Pre-existing D.1f citation defects (not edited)

- 2020-07-03: D.1f status quote reads 'NOTE: Friday, July 3, 2020 CME Group ...'; every copy read (Wayback 2026-07-15 and a live Firecrawl fetch) says 'NOTE: Note: Friday, July 3,2020 CME Group ...' (the quote drops 'Note:'). The status is unaffected; the D.1f citation is not verbatim.
- 2021-07-05: D.1f status quote reads 'NOTE: Monday, July 5, 2021 ...'; the document says 'NOTE: Note: Monday, July 5, 2021 ...' (the quote drops 'Note:').
- 2021-04-02: D.1f status quote joins superscript ordinals ('April 1st'); every copy read is the 2021-03-05 'SECOND CORRECTION' version, whose extracted text places the superscripts on their own line ('...will not be settled and / st / will use the April 1 end of day...'). Same words; not verbatim as extracted.
- 2023-04-07: D.1f status quote reads 'April 7th but ... April 6th end of day'; the document ('SECOND CORRECTION' version) extracts as 'April 7 but ... April 6 end of day' with the superscripts on the previous line. Same words.
- 2021-01-01: no source (status_url None, '[unverified]'); CME's 2021 New Year's Globex schedule (2020 zip) says 'Closed for New Year's' / 'Globex Closed' (proposal above).

## MES holdout-2 trade-date count (task d)

With the fix, data/cme_calendar.py gives 261 weekdays in 2024-04-01..2025-03-31 minus the full closures 2024-12-25 and 2025-01-01 = **259** trade dates (11 early halts, 2024-07-04 now among them). The embargo month (March 2024) still holds 20. Where 258 or 259 is recorded (none edited):

- `progress.md:2135`: D.1f run entry, Task 1: '258 = 261 weekdays 2024-04-01..2025-03-31 minus the listed full closures 2024-07-04, 2024-12-25 and 2025-01-01. Ten early halts count as trade dates ... would make the count 259.' -> historical record of the count at sealing (build choice 2.1); after the fix the calendar gives 259 = 261 - 2 (2024-12-25, 2025-01-01), with eleven early halts (2024-07-04 added). Not edited (outside the write list).
- `progress.md:2299`: 'With it corrected, holdout-2 has 259 calendar trade dates, not 258.' -> now true of the calendar.
- `progress.md:2314`: 'R.9 The holdout-2 count is recorded as 258 from the calendar as it stands (build choice 2.1), with the 2024-07-04 caveat.' -> historical; superseded by 259.
- `reports/stage_d1f_run_STATE.md:18`: task 1b row: 'holdout-2 trade dates by the calendar (choice 2.1): 258 (261 weekdays ...' -> historical; superseded by 259. Not edited.
- `docs/STAGE_E_DESIGN.md:640`: 'MES's holdout-2 has 259 calendar trade dates, not 258.' (frozen) -> now true of the calendar.
- `docs/prompts/STAGE_E.2a.md:345`: 'MES's holdout-2 count moves from 258 to 259 with the 2024-07-04 fix.' -> done.
- `reports/stage_d1f_confirmation_list.md:113`: 'about 259 calendar trade dates before exclusions, about 239 after the roll blackout and vendor-degraded dates' -> an estimate; consistent with 259.
- `reports/stage_d1e_power_verification.md:636 and :652`: holdout-2 weekday-open count 252 by the D.1e stated rule, 259 under the 'pipeline closures' convention (only Good Friday, Christmas, New Year's closed) -> 259 now also equals data/cme_calendar.py's count; the D.1e figures come from strategy/research/_d1e_calendar.py's own holiday rule and do not change.
- `progress.md:1707`: '239 CME trade dates by the calendar estimate; the exact count is recorded at sealing' -> 239 is after roll blackout and degraded dates; unaffected.
- Computed, not stored: every consumer of data.cme_calendar.HOLIDAYS counts 2024-07-04 as a trade date from now on: data/session.py (trade_date, closed windows), sim/engine.py:145 (is a trading day), data/splits.py:111-121, data/validate.py (step-4b rules), data/group_session.py (trade_dates_between, via data/calendars/equity.py), strategy/research/e_calendar_event/h4_turn_of_month.py:100.
- data/holdout.py:497 counts holdout trade dates from unlocked bars (a D.2 read), not from the calendar; strategy/research/_d1e_power.py:686 (holdout2_days = 239) uses strategy/research/_d1e_calendar.py's own holiday rule: neither changes.
- No test and no code in the repo pins the number 258 (grep over data/, docs/, reports/, tests/, strategy/, sim/, rules/, screening/, progress.md; data/vendor, data/sealed and data/processed excluded). docs/HOLDOUT2_MANIFEST.json holds bytes and sha256 only (no count), and was not modified.
- reports/stage_e2a_bars.json records data/cme_calendar.py at sha256 3dc4d852... (the pre-fix file) and the equity calendar modules without data/calendars/equity.py; any Task 7 rebuild or re-check will record the new hashes.

Sealed holdout after the edit (`uv run python -m data.holdout status`): "all_ok": true, "unlocks_logged": 0 (top level and holdout-2 section; "unsealed_plaintext_present": [], "confirmation_has_no_holdout2_rows": true), run at 02:39 PDT after all edits; the same result right after the calendar edit. Nothing under data/sealed/ was touched and nothing was decrypted; docs/HOLDOUT_MANIFEST.json, docs/HOLDOUT2_MANIFEST.json and docs/HOLDOUT_UNLOCK_LOG.md were not modified.

## Gaps

- No CME Globex-hours document for 2023-01-16 (MLK Day 2023): time stays secondary.
- No usable Wayback copy of the cited version of eleven CME documents: the 2020 MLK, Presidents' Day, Labor Day and Christmas settlement notices, the 2020 and 2021 Fourth of July settlement notices, and five clearing advisories (Good Friday 2021 and 2023, New Year's 2021, 2023 and 2024). They were read live through Firecrawl (markdown transcribed into the cache, excerpts marked; fetched_via says so).
- 2019-2022 holiday hours are stated per product group ('Equity Products'), 2023 per asset class (most active instrument), 2024-2026 for ES (and YM once): see the products section.
- The halt start of the 2025-11-28 outage is in no CME document retrieved.
- Entries after 2026-06-19 (in data.cme_calendar's coverage to 2026-12-31) were not re-sourced: outside this stage's window.
- CME's 2026 contract-specification pages are rendered by script; their hours text was not in the captured HTML, so the post-2021 hours rest on the 2021 notice and the trading-hours service.

## Verbatim-check normalization

Quotes are split at ' ... ' and every fragment must occur in the document text in order. Levels: 'ws_collapsed' = every whitespace run (incl. newlines, NBSP) collapsed to one space on both sides; 'ws_removed' = all whitespace removed on both sides (PDF/HTML text whose word spacing is lost in extraction); 'ws_removed+typography' = also curly apostrophes/quotes to straight and en/em dashes to '-'. Document text: PDF via pdftotext (default, -raw, -layout; any mode may match); XLS via LibreOffice CSV export ('|' between cells, all sheets, cells as displayed, trailing empty cells dropped per line); ZIP = all members converted and concatenated; JSON as returned (gzip-decompressed), CME client-wiki REST pages = the page body with tags removed; HTML with tags removed and entities unescaped; Firecrawl markdown with '**', '__', tags and heading '#' removed. verbatim_check is true when both quotes of the row pass at some level.

## Fetch log (PDT)

Network requests by this worker, in order. Files reused from the shared cache (fetched by the other CalendarBuilders) appear in the JSON rows' fetched_via fields and are not repeated here. WebSearch was not used. Firecrawl: 2 searches (about 01:44 and 01:48 PDT; 4 credits) and 11 scrapes of cmegroup.com PDFs (one about 02:05 PDT, ten about 02:17-02:20 PDT; 14 credits), saved to the cache at 02:21 PDT. Wayback CDX returned empty bodies for a stretch around 02:03 PDT (rate limiting); those lookups were repeated slowly at 02:10-02:17 PDT.

| Time | URL | Via | Result |
|---|---|---|---|
| 01:43:15 | www.cmegroup.com/trading/equity-index/us-index/e-mini-sandp500_contract_specifications.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/trading/equity-index/us-index/ | cdx 5832 B |
| 01:43:22 | https://www.cmegroup.com/trading/equity-index/us-index/e-mini-sandp500_contract_specifications.html | https://web.archive.org/web/20190607125912id_/https://www.cmegroup.com/trading/equity-inde | ok http 200 128223 B -> equity_es_specs_20190607125912.html |
| 01:43:23 | https://www.cmegroup.com/trading/equity-index/us-index/e-mini-sandp500_contract_specifications.html | https://web.archive.org/web/20210610062512id_/https://www.cmegroup.com/trading/equity-inde | ok http 200 14322 B -> equity_es_specs_20210610062512.html |
| 01:43:57 | www.cmegroup.com/notices/electronic-trading/2021/06/20210621.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/notices/electronic-trading/202 | cdx 744 B |
| 01:44:11 | www.cmegroup.com/content/dam/cmegroup/notices/electronic-trading/2021/06/cme-equity-index-futures-options.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/content/dam/cmegroup/notices/e | cdx 394 B |
| 01:44:30 | www.cftc.gov/sites/default/files/filings/orgrules/21/06/rule061421cmedcm001.pdf | https://web.archive.org/cdx/search/cdx?url=www.cftc.gov/sites/default/files/filings/orgrul | cdx 335 B |
| 01:44:31 | www.cmegroup.com/trading/equity-index/fairvaluefaq.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/trading/equity-index/fairvalue | cdx 16316 B |
| 01:44:44 | www.cmegroup.com/notices/electronic-trading/2021/06/20210614.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/notices/electronic-trading/202 | cdx 2964 B |
| 01:44:46 | www.cmegroup.com/notices/electronic-trading/2021/06/20210607.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/notices/electronic-trading/202 | cdx 744 B |
| 01:44:55 | https://www.cmegroup.com/notices/electronic-trading/2021/06/20210621.html | https://web.archive.org/web/20260208051545id_/https://www.cmegroup.com/notices/electronic- | ok http 200 188041 B -> equity_notice_20210621.html |
| 01:44:56 | https://www.cmegroup.com/content/dam/cmegroup/notices/electronic-trading/2021/06/cme-equity-index-futures-opti | https://web.archive.org/web/20260310213155id_/https://www.cmegroup.com/content/dam/cmegrou | ok http 200 95886 B -> equity_notice_20210621_products.pdf |
| 01:44:57 | https://www.cftc.gov/sites/default/files/filings/orgrules/21/06/rule061421cmedcm001.pdf | https://web.archive.org/web/20220118235156id_/https://www.cftc.gov/sites/default/files/fil | ok http 200 344016 B -> equity_cftc_rule061421cmedcm001.pdf |
| 01:45:21 | https://www.cmegroup.com/notices/electronic-trading/2021/06/20210614.html | https://web.archive.org/web/20210926100002id_/https://www.cmegroup.com/notices/electronic- | FAILED http 000 curl: (7) Failed to connect to web.archive.org port 443 after 37 |
| 01:45:45 | https://www.cmegroup.com/notices/electronic-trading/2021/06/20210607.html | https://web.archive.org/web/20210615053300id_/https://www.cmegroup.com/notices/electronic- | FAILED http 000 curl: (7) Failed to connect to web.archive.org port 443 after 34 |
| 01:46:36 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457412988/child/page?limit=200 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457412988/child/page?limit= | ok http 200 16992 B -> equity_epic_equity_indices_children.json |
| 01:46:36 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457412988?expand=body.storage,version,history | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457412988?expand=body.stora | ok http 200 3706 B -> equity_epic_equity_indices_457412988.json |
| 01:46:42 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457318203?expand=body.storage,version,history | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457318203?expand=body.stora | ok http 200 10745 B -> equity_epic_equity_Dow_457318203.json |
| 01:46:43 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457087994?expand=body.storage,version,history | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457087994?expand=body.stora | ok http 200 3462 B -> equity_epic_equity_Nasdaq_457087994.json |
| 01:46:43 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457218971?expand=body.storage,version,history | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457218971?expand=body.stora | ok http 200 3386 B -> equity_epic_equity_Russell_457218971.json |
| 01:46:43 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457318586?expand=body.storage,version,history | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457318586?expand=body.stora | ok http 200 3693 B -> equity_epic_equity_SP_457318586.json |
| 01:46:49 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457087994/child/page?limit=200 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457087994/child/page?limit= | ok http 200 5922 B -> equity_epic_equity_Nasdaq_children.json |
| 01:46:49 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457218971/child/page?limit=200 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457218971/child/page?limit= | ok http 200 9102 B -> equity_epic_equity_Russell_children.json |
| 01:46:49 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457318586/child/page?limit=200 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457318586/child/page?limit= | ok http 200 18517 B -> equity_epic_equity_SP_children.json |
| 01:46:55 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457418067?expand=body.storage,version,history | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457418067?expand=body.stora | ok http 200 14147 B -> equity_epic_equity_ES_457418067.json |
| 01:46:55 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457222172?expand=body.storage,version,history | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457222172?expand=body.stora | ok http 200 12646 B -> equity_epic_equity_NQ_457222172.json |
| 01:46:56 | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457222305?expand=body.storage,version,history | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457222305?expand=body.stora | ok http 200 8789 B -> equity_epic_equity_RTY_457222305.json |
| 01:47:07 | www.cmegroup.com/confluence/display/EPICSANDBOX/* | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/confluence/display/EPICSANDBOX | cdx 17460 B |
| 01:48:01 | www.cmegroup.com/confluence/display/EPICSANDBOX/E-Mini+Standard+and+Poors+500+Futures | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/confluence/display/EPICSANDBOX | cdx 3 B |
| 01:48:06 | www.cmegroup.com/confluence/display/EPICSANDBOX/Standard+and+Poors+500+Futures | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/confluence/display/EPICSANDBOX | cdx 3 B |
| 01:48:09 | www.cmegroup.com/confluence/display/EPICSANDBOX/Nasdaq-100 | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/confluence/display/EPICSANDBOX | cdx 910 B |
| 01:48:16 | www.cmegroup.com/confluence/display/EPICSANDBOX/E-mini+Russell+2000 | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/confluence/display/EPICSANDBOX | cdx 3 B |
| 01:48:19 | www.cmegroup.com/confluence/display/EPICSANDBOX/Dow+Jones+Futures | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/confluence/display/EPICSANDBOX | cdx 998 B |
| 01:48:30 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/Nasdaq-100 | https://web.archive.org/web/20191120id_/https://www.cmegroup.com/confluence/display/EPICSA | ok http 200 57676 B -> equity_wiki_Nasdaq-100_20191120.html |
| 01:48:31 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/Nasdaq-100 | https://web.archive.org/web/20210923id_/https://www.cmegroup.com/confluence/display/EPICSA | ok http 200 53410 B -> equity_wiki_Nasdaq-100_20210923.html |
| 01:48:35 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/Dow+Jones+Futures | https://web.archive.org/web/20190824id_/https://www.cmegroup.com/confluence/display/EPICSA | ok http 200 55228 B -> equity_wiki_Dow_Jones_Futures_20190824.html |
| 01:48:36 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/Dow+Jones+Futures | https://web.archive.org/web/20211202id_/https://www.cmegroup.com/confluence/display/EPICSA | ok http 200 51333 B -> equity_wiki_Dow_Jones_Futures_20211202.html |
| 01:48:37 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/E-Mini+Standard+and+Poors+500+Futures | https://web.archive.org/web/2021id_/https://www.cmegroup.com/confluence/display/EPICSANDBO | ok http 200 54679 B -> equity_wiki_E-Mini_Standard_and_Poors_500_Futures_2021.ht |
| 01:48:37 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/E-mini+Russell+2000 | https://web.archive.org/web/2020id_/https://www.cmegroup.com/confluence/display/EPICSANDBO | ok http 200 50508 B -> equity_wiki_E-mini_Russell_2000_2020.html |
| 01:49:03 | www.cmegroup.com/notices/ser/2020/09/SER-8591.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/notices/ser/2020/09/SER-8591.p | cdx 274 B |
| 01:49:08 | https://www.cmegroup.com/notices/ser/2020/09/SER-8591.pdf | https://web.archive.org/web/20241220125115id_/https://www.cmegroup.com/notices/ser/2020/09 | ok http 200 108884 B -> equity_SER-8591.pdf |
| 01:49:49 | https://www.cmegroup.com/trading/equity-index/us-index/e-mini-nasdaq-100_contract_specifications.html | https://web.archive.org/web/20191015id_/https://www.cmegroup.com/trading/equity-index/us-i | ok http 200 88381 B -> equity_specs_NQ_2019.html |
| 01:50:14 | https://www.cmegroup.com/trading/equity-index/us-index/e-mini-russell-2000_contract_specifications.html | https://web.archive.org/web/20191015id_/https://www.cmegroup.com/trading/equity-index/us-i | FAILED http 000 curl: (7) Failed to connect to web.archive.org port 443 after 31 |
| 01:50:15 | https://www.cmegroup.com/trading/equity-index/us-index/e-mini-dow_contract_specifications.html | https://web.archive.org/web/20191015id_/https://www.cmegroup.com/trading/equity-index/us-i | ok http 200 78798 B -> equity_specs_YM_2019.html |
| 01:50:15 | https://www.cmegroup.com/trading/equity-index/us-index/micro-e-mini-sandp-500_contract_specifications.html | https://web.archive.org/web/20191015id_/https://www.cmegroup.com/trading/equity-index/us-i | ok http 200 79280 B -> equity_specs_MES_2019.html |
| 01:50:27 | https://www.cmegroup.com/trading/equity-index/us-index/micro-e-mini-nasdaq-100_contract_specifications.html | https://web.archive.org/web/20191015id_/https://www.cmegroup.com/trading/equity-index/us-i | ok http 200 79222 B -> equity_specs_MNQ_2019.html |
| 01:50:51 | https://www.cmegroup.com/trading/equity-index/us-index/micro-e-mini-russell-2000_contract_specifications.html | https://web.archive.org/web/20191015id_/https://www.cmegroup.com/trading/equity-index/us-i | FAILED http 000 curl: (7) Failed to connect to web.archive.org port 443 after 41 |
| 01:51:05 | https://www.cmegroup.com/trading/equity-index/us-index/micro-e-mini-dow_contract_specifications.html | https://web.archive.org/web/20191015id_/https://www.cmegroup.com/trading/equity-index/us-i | ok http 200 79132 B -> equity_specs_MYM_2019.html |
| 01:51:13 | www.cmegroup.com/trading/equity-index/us-index/* | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/trading/equity-index/us-index/ | cdx 10908 B |
| 01:51:23 | https://www.cmegroup.com/trading/equity-index/us-index/e-mini-russell-2000_contract_specifications.html | https://web.archive.org/web/20190720175051id_/https://www.cmegroup.com/trading/equity-inde | ok http 200 132003 B -> equity_specs_RTY_2019.html |
| 01:51:26 | https://www.cmegroup.com/trading/equity-index/us-index/micro-e-mini-russell-2000_contract_specifications.html | https://web.archive.org/web/20190720032725id_/https://www.cmegroup.com/trading/equity-inde | ok http 200 131972 B -> equity_specs_M2K_2019.html |
| 01:51:35 | www.cmegroup.com/markets/equities/sp/e-mini-sandp500.contractSpecs.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/markets/equities/sp/e-mini-san | cdx 1014 B |
| 01:51:35 | https://www.cmegroup.com/markets/equities/sp/e-mini-sandp500.contractSpecs.html | https://web.archive.org/web/20260517030259id_/https://www.cmegroup.com/markets/equities/sp | ok http 200 291183 B -> equity_specs_ES_20260517.html |
| 01:51:56 | www.cmegroup.com/markets/equities/sp/micro-e-mini-sandp-500.contractSpecs.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/markets/equities/sp/micro-e-mi | cdx 822 B |
| 01:51:58 | https://www.cmegroup.com/markets/equities/sp/micro-e-mini-sandp-500.contractSpecs.html | https://web.archive.org/web/20260907022619id_/https://www.cmegroup.com/markets/equities/sp | ok http 200 205698 B -> equity_specs_MES_20260907.html |
| 01:52:10 | www.cmegroup.com/markets/equities/nasdaq/e-mini-nasdaq-100.contractSpecs.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/markets/equities/nasdaq/e-mini | cdx 816 B |
| 01:52:10 | https://www.cmegroup.com/markets/equities/nasdaq/e-mini-nasdaq-100.contractSpecs.html | https://web.archive.org/web/20260510110334id_/https://www.cmegroup.com/markets/equities/na | ok http 200 262944 B -> equity_specs_NQ_20260510.html |
| 01:52:10 | www.cmegroup.com/markets/equities/nasdaq/micro-e-mini-nasdaq-100.contractSpecs.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/markets/equities/nasdaq/micro- | cdx 0 B |
| 01:52:10 | www.cmegroup.com/markets/equities/nasdaq/micro-e-mini-nasdaq-100.contractSpecs.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/markets/equities/nasdaq/micro- | cdx 0 B |
| 01:52:10 | www.cmegroup.com/markets/equities/russell/e-mini-russell-2000.contractSpecs.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/markets/equities/russell/e-min | cdx 0 B |
| 01:52:10 | www.cmegroup.com/markets/equities/russell/e-mini-russell-2000.contractSpecs.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/markets/equities/russell/e-min | cdx 0 B |
| 01:52:11 | www.cmegroup.com/markets/equities/russell/micro-e-mini-russell-2000.contractSpecs.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/markets/equities/russell/micro | cdx 0 B |
| 01:52:11 | www.cmegroup.com/markets/equities/russell/micro-e-mini-russell-2000.contractSpecs.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/markets/equities/russell/micro | cdx 0 B |
| 01:52:11 | www.cmegroup.com/markets/equities/dow-jones/e-mini-dow.contractSpecs.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/markets/equities/dow-jones/e-m | cdx 0 B |
| 01:52:11 | www.cmegroup.com/markets/equities/dow-jones/e-mini-dow.contractSpecs.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/markets/equities/dow-jones/e-m | cdx 0 B |
| 01:52:11 | www.cmegroup.com/markets/equities/dow-jones/micro-e-mini-dow.contractSpecs.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/markets/equities/dow-jones/mic | cdx 0 B |
| 01:52:11 | www.cmegroup.com/markets/equities/dow-jones/micro-e-mini-dow.contractSpecs.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/markets/equities/dow-jones/mic | cdx 0 B |
| 01:52:28 | www.cmegroup.com/trading/equity-index/fairvaluefaq.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/trading/equity-index/fairvalue | cdx 0 B |
| 01:53:07 | www.cmegroup.com/trading/price-limits.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/trading/price-limits.html&outp | cdx 12469 B |
| 01:53:24 | https://www.cmegroup.com/trading/price-limits.html | https://web.archive.org/web/20201226061711id_/https://www.cmegroup.com/trading/price-limit | ok http 200 316685 B -> equity_price_limits_20201226061711.html |
| 01:53:25 | https://www.cmegroup.com/trading/price-limits.html | https://web.archive.org/web/20210615145720id_/https://www.cmegroup.com/trading/price-limit | ok http 200 374298 B -> equity_price_limits_20210615145720.html |
| 01:53:28 | https://www.cmegroup.com/trading/price-limits.html | https://web.archive.org/web/20230604080601id_/https://www.cmegroup.com/trading/price-limit | ok http 200 410659 B -> equity_price_limits_20230604080601.html |
| 01:53:49 | https://www.cmegroup.com/trading/price-limits.html | https://web.archive.org/web/20190823id_/https://www.cmegroup.com/trading/price-limits.html | ok http 200 342452 B -> equity_price_limits_20190823.html |
| 01:53:53 | https://www.cmegroup.com/trading/price-limits.html | https://web.archive.org/web/20201005id_/https://www.cmegroup.com/trading/price-limits.html | ok http 200 306676 B -> equity_price_limits_20201005.html |
| 01:55:25 | www.cmegroup.com/files/* | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/files/*&output=json&filter=sta | cdx 40780 B |
| 01:55:31 | www.cmegroup.com/trading-hours/files/* | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/trading-hours/files/*&output=j | cdx 2437 B |
| 01:55:32 | www.cmegroup.com/tools-information/holiday-calendar/files/2023* | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 8622 B |
| 01:56:51 | www.cmegroup.com/services/trading-hours* | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/services/trading-hours*&output | cdx 387464 B |
| 01:56:59 | www.cmegroup.com/services/trading-hours* | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/services/trading-hours*&output | cdx 387464 B |
| 01:57:13 | https://www.cmegroup.com/services/trading-hours-by-product?id=318&pageNumber=1&pageSize=999&sortAsc=true&fromE | https://web.archive.org/web/20260714154118id_/https://www.cmegroup.com/services/trading-ho | ok http 200 370 B -> equity_thbp_id318_2026-01-18.json |
| 01:57:14 | https://www.cmegroup.com/services/trading-hours-by-product?pageNumber=1&pageSize=7&exch=&cleared=Futures&group | https://web.archive.org/web/20260622192727id_/https://www.cmegroup.com/services/trading-ho | ok http 200 651 B -> equity_thbp_mostactive_2025-12-31.json |
| 01:57:14 | https://www.cmegroup.com/services/trading-hours-by-product?pageNumber=1&pageSize=7&exch=&cleared=Futures&group | https://web.archive.org/web/20260310033910id_/https://www.cmegroup.com/services/trading-ho | ok http 200 576 B -> equity_thbp_mostactive_2025-02-14.json |
| 01:57:15 | https://www.cmegroup.com/services/trading-hours-by-product?pageNumber=1&pageSize=7&exch=&cleared=Futures&group | https://web.archive.org/web/20260622193137id_/https://www.cmegroup.com/services/trading-ho | ok http 200 582 B -> equity_thbp_mostactive_2023-05-26.json |
| 01:57:15 | https://www.cmegroup.com/services/trading-hours-by-product?id=133,219&pageNumber=1&pageSize=999&sortAsc=true&f | https://web.archive.org/web/20260913150612id_/https://www.cmegroup.com/services/trading-ho | ok http 200 346 B -> equity_thbp_id133_219_2026-09-06.json |
| 02:01:12 | www.cmegroup.com/tools-information/holiday-calendar/files/2019-memorial-day-holiday-settlement-times.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 690 B |
| 02:01:14 | https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-memorial-day-holiday-settlement-times.p | https://web.archive.org/web/20241212005508id_/https://www.cmegroup.com/tools-information/h | ok http 200 45431 B -> equity_https_www.cmegroup.com_tools-information_holiday-c |
| 02:01:14 | https://crosstrade.io/blog/cme-trading-hours-2026 | https://crosstrade.io/blog/cme-trading-hours-2026 | ok http 200 45031 B -> equity_cme-trading-hours-2026 |
| 02:01:16 | https://www.cmegroup.com/tools-information/holiday-calendar/files/2019/2019-4th-of-july-holiday-schedule-compa | https://web.archive.org/web/20220920142350id_/https://www.cmegroup.com/tools-information/h | ok http 200 31232 B -> equity_https_www.cmegroup.com_tools-information_holiday-c |
| 02:01:31 | www.cmegroup.com/tools-information/holiday-calendar/files/2019-labor-day-holiday-settlement-times.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 978 B |
| 02:01:32 | https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-labor-day-holiday-settlement-times.pdf | https://web.archive.org/web/20240628133718id_/https://www.cmegroup.com/tools-information/h | ok http 200 45064 B -> equity_https_www.cmegroup.com_tools-information_holiday-c |
| 02:01:36 | www.cmegroup.com/tools-information/holiday-calendar/files/2019-thanksgiving-holiday-settlement-times.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 690 B |
| 02:01:37 | https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-thanksgiving-holiday-settlement-times.p | https://web.archive.org/web/20241212020001id_/https://www.cmegroup.com/tools-information/h | ok http 200 49153 B -> equity_https_www.cmegroup.com_tools-information_holiday-c |
| 02:01:39 | www.cmegroup.com/tools-information/holiday-calendar/files/2020-new-years-advisory.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 616 B |
| 02:01:40 | https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-new-years-advisory.pdf | https://web.archive.org/web/20241212005141id_/https://www.cmegroup.com/tools-information/h | ok http 200 194300 B -> equity_https_www.cmegroup.com_tools-information_holiday- |
| 02:01:43 | www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 3 B |
| 02:01:43 | cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 3 B |
| 02:01:46 | www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 3 B |
| 02:01:49 | cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 3 B |
| 02:01:50 | https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-independence-day-schedule.xls | https://web.archive.org/web/20220707015539id_/https://www.cmegroup.com/tools-information/h | ok http 200 82944 B -> equity_https_www.cmegroup.com_tools-information_holiday-c |
| 02:01:55 | www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 3 B |
| 02:02:11 | cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 3 B |
| 02:02:34 | www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 378 B |
| 02:03:06 | https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2020.pdf | https://web.archive.org/web/20210126003901id_/https://www.cmegroup.com/tools-information/h | FAILED http 404  |
| 02:03:29 | www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2021.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 672 B |
| 02:03:29 | https://www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2021.pdf | https://web.archive.org/web/20210115175300id_/https://www.cmegroup.com/tools-information/h | ok http 200 115226 B -> equity_https_www.cmegroup.com_tools-information_holiday- |
| 02:03:29 | www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2021.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 0 B |
| 02:03:29 | cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2021.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 0 B |
| 02:03:54 | https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-independence-day-holiday-schedule-compa | https://web.archive.org/web/20210702051538id_/https://www.cmegroup.com/tools-information/h | FAILED http 000 curl: (7) Failed to connect to web.archive.org port 443 after 14 |
| 02:03:54 | www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2021.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 0 B |
| 02:03:54 | cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2021.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 0 B |
| 02:03:54 | www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2022.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 0 B |
| 02:03:54 | cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2022.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 0 B |
| 02:03:54 | www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2022.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 0 B |
| 02:03:54 | cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2022.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 0 B |
| 02:03:55 | www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2022.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 0 B |
| 02:03:55 | cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2022.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 0 B |
| 02:03:56 | www.cmegroup.com/tools-information/holiday-calendar/files/juneteenth-day-holiday-settlement-times-2023.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 0 B |
| 02:03:56 | cmegroup.com/tools-information/holiday-calendar/files/juneteenth-day-holiday-settlement-times-2023.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 0 B |
| 02:03:56 | www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2023.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 0 B |
| 02:03:56 | cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2023.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 0 B |
| 02:03:56 | www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2024.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 0 B |
| 02:03:56 | cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2024.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 0 B |
| 02:03:56 | www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2024.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 0 B |
| 02:03:56 | cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2024.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 0 B |
| 02:03:56 | www.cmegroup.com/tools-information/holiday-calendar/files/juneteenth-day-settlement-times-2024.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 0 B |
| 02:03:57 | cmegroup.com/tools-information/holiday-calendar/files/juneteenth-day-settlement-times-2024.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 0 B |
| 02:03:57 | www.cmegroup.com/content/dam/cmegroup/tools-information/holiday-calendar/files/us-independence-day-settlement- | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/content/dam/cmegroup/tools-inf | cdx 0 B |
| 02:03:57 | cmegroup.com/content/dam/cmegroup/tools-information/holiday-calendar/files/us-independence-day-settlement-time | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/content/dam/cmegroup/tools-informa | cdx 0 B |
| 02:03:57 | www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2024.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 0 B |
| 02:03:57 | cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2024.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 0 B |
| 02:03:57 | www.cmegroup.com/tools-information/holiday-calendar/files/2021-new-years-advisory.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 0 B |
| 02:03:57 | cmegroup.com/tools-information/holiday-calendar/files/2021-new-years-advisory.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 0 B |
| 02:06:09 | www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 3 B |
| 02:06:23 | www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 3 B |
| 02:06:31 | www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 3 B |
| 02:06:40 | cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 3 B |
| 02:06:58 | www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 3 B |
| 02:07:05 | www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 3 B |
| 02:08:09 | www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 153 B |
| 02:08:30 | cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 3 B |
| 02:08:37 | www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 3 B |
| 02:09:07 | www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 3 B |
| 02:09:16 | www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 3 B |
| 02:09:27 | cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 3 B |
| 02:09:35 | www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 378 B |
| 02:10:19 | www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2021.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 1011 B |
| 02:10:59 | web.archive.org/web/20210702051538/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-inde | https://web.archive.org/cdx/search/cdx?url=web.archive.org/web/20210702051538/https://www. | cdx 3 B |
| 02:11:12 | web.archive.org/web/20210702051538/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-inde | https://web.archive.org/cdx/search/cdx?url=web.archive.org/web/20210702051538/https://www. | cdx 3 B |
| 02:12:11 | web.archive.org/web/20210702051538/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-inde | https://web.archive.org/cdx/search/cdx?url=web.archive.org/web/20210702051538/https://www. | cdx 3 B |
| 02:13:10 | web.archive.org/web/20210702051538/https://cmegroup.com/tools-information/holiday-calendar/files/2021-independ | https://web.archive.org/cdx/search/cdx?url=web.archive.org/web/20210702051538/https://cmeg | cdx 3 B |
| 02:13:23 | www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2021.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 680 B |
| 02:13:36 | www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2022.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 670 B |
| 02:13:48 | www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2022.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 388 B |
| 02:13:53 | www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2022.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 678 B |
| 02:13:59 | www.cmegroup.com/tools-information/holiday-calendar/files/juneteenth-day-holiday-settlement-times-2023.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 698 B |
| 02:14:17 | www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2023.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 678 B |
| 02:14:22 | www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2024.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 670 B |
| 02:14:46 | www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2024.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 698 B |
| 02:15:00 | www.cmegroup.com/tools-information/holiday-calendar/files/juneteenth-day-settlement-times-2024.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 666 B |
| 02:15:31 | www.cmegroup.com/content/dam/cmegroup/tools-information/holiday-calendar/files/us-independence-day-settlement- | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/content/dam/cmegroup/tools-inf | cdx 424 B |
| 02:15:54 | www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2024.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 678 B |
| 02:16:18 | www.cmegroup.com/tools-information/holiday-calendar/files/2021-new-years-advisory.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 347 B |
| 02:17:08 | https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2020.pdf | https://web.archive.org/web/20210126003901id_/https://www.cmegroup.com/tools-information/h | FAILED http 404  |
| 02:17:08 | https://www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2021 | https://web.archive.org/web/20210115185017id_/https://www.cmegroup.com/tools-information/h | ok http 200 113974 B -> equity_20210115185017_presidents-day-holiday-settlement- |
| 02:17:09 | https://www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2021.pdf | https://web.archive.org/web/20210115184551id_/https://www.cmegroup.com/tools-information/h | ok http 200 117314 B -> equity_20210115184551_labor-day-holiday-settlement-times |
| 02:17:09 | https://www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2022.pdf | https://web.archive.org/web/20220128023537id_/https://www.cmegroup.com/tools-information/h | ok http 200 44718 B -> equity_20220128023537_mlk-day-holiday-settlement-times-20 |
| 02:17:12 | https://www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2022 | https://web.archive.org/web/20220128015837id_/https://www.cmegroup.com/tools-information/h | ok http 200 74639 B -> equity_20220128015837_presidents-day-holiday-settlement-t |
| 02:17:13 | https://www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2022.pdf | https://web.archive.org/web/20220128030303id_/https://www.cmegroup.com/tools-information/h | ok http 200 45290 B -> equity_20220128030303_labor-day-holiday-settlement-times- |
| 02:17:13 | https://www.cmegroup.com/tools-information/holiday-calendar/files/juneteenth-day-holiday-settlement-times-2023 | https://web.archive.org/web/20230203075330id_/https://www.cmegroup.com/tools-information/h | ok http 200 45081 B -> equity_20230203075330_juneteenth-day-holiday-settlement-t |
| 02:17:14 | https://www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2023.pdf | https://web.archive.org/web/20230203073730id_/https://www.cmegroup.com/tools-information/h | ok http 200 43664 B -> equity_20230203073730_labor-day-holiday-settlement-times- |
| 02:17:17 | https://www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2024.pdf | https://web.archive.org/web/20231121093217id_/https://www.cmegroup.com/tools-information/h | ok http 200 69130 B -> equity_20231121093217_mlk-day-holiday-settlement-times-20 |
| 02:17:18 | https://www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2024 | https://web.archive.org/web/20231121175213id_/https://www.cmegroup.com/tools-information/h | ok http 200 69415 B -> equity_20231121175213_presidents-day-holiday-settlement-t |
| 02:17:19 | https://www.cmegroup.com/tools-information/holiday-calendar/files/juneteenth-day-settlement-times-2024.pdf | https://web.archive.org/web/20231121100846id_/https://www.cmegroup.com/tools-information/h | ok http 200 69251 B -> equity_20231121100846_juneteenth-day-settlement-times-202 |
| 02:17:19 | https://www.cmegroup.com/content/dam/cmegroup/tools-information/holiday-calendar/files/us-independence-day-set | https://web.archive.org/web/20240414203534id_/https://www.cmegroup.com/content/dam/cmegrou | ok http 200 70638 B -> equity_20240414203534_us-independence-day-settlement-time |
| 02:17:20 | https://www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2024.pdf | https://web.archive.org/web/20231121102422id_/https://www.cmegroup.com/tools-information/h | ok http 200 69053 B -> equity_20231121102422_labor-day-holiday-settlement-times- |
| 02:17:21 | https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-new-years-advisory.pdf | https://web.archive.org/web/20240711215207id_/https://www.cmegroup.com/tools-information/h | ok http 200 170065 B -> equity_20240711215207_2021-new-years-advisory.pdf |
| 02:17:22 | https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-independence-day-holiday-schedule-compa | https://web.archive.org/web/20210702051538id_/https://www.cmegroup.com/tools-information/h | ok http 200 48640 B -> equity_20210702051538_2021-independence-day-holiday-sched |
| 02:17:37 | www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 3 B |
| 02:17:44 | cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 3 B |
| 02:18:17 | www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 3 B |
| 02:18:22 | cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 3 B |
| 02:18:32 | www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 3 B |
| 02:18:40 | cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar | cdx 3 B |
| 02:18:53 | www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2020.pdf | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/tools-information/holiday-cale | cdx 378 B |
| 02:19:23 | https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2020.pdf | https://web.archive.org/web/20210126003901id_/https://www.cmegroup.com/tools-information/h | FAILED http 404  |
| 02:21:02 | https://www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2020.pdf | firecrawl_scrape (live fetch of https://www.cmegroup.com/tools-information/holiday-calenda | firecrawl ok 362 chars |
| 02:21:02 | https://www.cmegroup.com/tools-information/holiday-calendar/files/presidents-day-holiday-settlement-times-2020 | firecrawl_scrape (live fetch of https://www.cmegroup.com/tools-information/holiday-calenda | firecrawl ok 437 chars |
| 02:21:02 | https://www.cmegroup.com/tools-information/holiday-calendar/files/labor-day-holiday-settlement-times-2020.pdf | firecrawl_scrape (live fetch of https://www.cmegroup.com/tools-information/holiday-calenda | firecrawl ok 613 chars |
| 02:21:02 | https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2020.pdf | firecrawl_scrape (live fetch of https://www.cmegroup.com/tools-information/holiday-calenda | firecrawl ok 838 chars |
| 02:21:02 | https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2020.pdf | firecrawl_scrape (live fetch of https://www.cmegroup.com/tools-information/holiday-calenda | firecrawl ok 802 chars |
| 02:21:02 | https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2021.pdf | firecrawl_scrape (live fetch of https://www.cmegroup.com/tools-information/holiday-calenda | firecrawl ok 882 chars |
| 02:21:02 | https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-good-friday-advisory.pdf | firecrawl_scrape (live fetch of https://www.cmegroup.com/tools-information/holiday-calenda | firecrawl ok 605 chars |
| 02:21:02 | https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-good-friday-advisory.pdf | firecrawl_scrape (live fetch of https://www.cmegroup.com/tools-information/holiday-calenda | firecrawl ok 452 chars |
| 02:21:02 | https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-advisory.pdf | firecrawl_scrape (live fetch of https://www.cmegroup.com/tools-information/holiday-calenda | firecrawl ok 885 chars |
| 02:21:02 | https://www.cmegroup.com/tools-information/holiday-calendar/files/2024-new-years-advisory.pdf | firecrawl_scrape (live fetch of https://www.cmegroup.com/tools-information/holiday-calenda | firecrawl ok 989 chars |
| 02:21:02 | https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-new-years-advisory.pdf | firecrawl_scrape (live fetch of https://www.cmegroup.com/tools-information/holiday-calenda | firecrawl ok 909 chars |
| 02:26:12 | www.cmegroup.com/confluence/display/EPICSANDBOX/Dow+Jones+Futures | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/confluence/display/EPICSANDBOX | cdx 768 B |
| 02:26:19 | www.cmegroup.com/confluence/display/EPICSANDBOX/Nasdaq-100 | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/confluence/display/EPICSANDBOX | cdx 910 B |
| 02:26:25 | www.cmegroup.com/trading/price-limits.html | https://web.archive.org/cdx/search/cdx?url=www.cmegroup.com/trading/price-limits.html&outp | cdx 19513 B |
| 02:26:39 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/Dow+Jones+Futures | https://web.archive.org/web/20190824091841id_/https://www.cmegroup.com/confluence/display/ | ok http 200 55228 B -> equity_wiki_Dow_Jones_Futures_20190824091841.html |
| 02:26:39 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/Nasdaq-100 | https://web.archive.org/web/20191120084353id_/https://www.cmegroup.com/confluence/display/ | ok http 200 57676 B -> equity_wiki_Nasdaq-100_20191120084353.html |
| 02:26:40 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/Nasdaq-100 | https://web.archive.org/web/20210923141411id_/https://www.cmegroup.com/confluence/display/ | ok http 200 53410 B -> equity_wiki_Nasdaq-100_20210923141411.html |
| 02:26:41 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/Dow+Jones+Futures | https://web.archive.org/web/20211202180631id_/https://www.cmegroup.com/confluence/display/ | ok http 200 51333 B -> equity_wiki_Dow_Jones_Futures_20211202180631.html |
| 02:26:41 | https://www.cmegroup.com/trading/price-limits.html | https://web.archive.org/web/20190823172618id_/https://www.cmegroup.com/trading/price-limit | ok http 200 342452 B -> equity_price_limits_20190823172618.html |
| 02:27:33 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/Dow+Jones+Futures | https://web.archive.org/web/20190824091841id_/https://www.cmegroup.com/confluence/display/ | cache hit equity_wiki_Dow_Jones_Futures_20190824091841.html |
| 02:41:04 | https://www.cmegroup.com/confluence/display/EPICSANDBOX/Dow+Jones+Futures | https://web.archive.org/web/20190824091841id_/https://www.cmegroup.com/confluence/display/ | cache hit equity_wiki_Dow_Jones_Futures_20190824091841.html |
