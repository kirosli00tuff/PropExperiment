# Stage E.2a Task 6: CME Globex calendar, grains group (ZC, ZW, ZS, ZM, ZL)

Built by CalendarBuilder-Grains (Opus 5.5, xhigh), 2026-09-25 01:35 PDT. Module: `data/calendars/grains.py`; tests: `tests/test_e2a_calendar_grains.py`; machine-readable twin: `reports/stage_e2a_calendar_sources_grains.json`. Coverage 2019-05-01..2026-06-19 (design D10). No market data was read.

## Counts

- HOLIDAYS entries: 82 (68 full closures, 14 early halts). LATE_OPENS: 20. NO_ENTRY_FINDINGS: 22.
- Status grades (entries and late opens): {'cme': 101, 'secondary': 1, 'unverified': 0}.
- Time grades (entries and late opens): {'cme': 34, 'secondary': 0, 'inferred': 0, 'unverified': 0, 'n/a': 68}.
- verbatim_check false: 1 (2023-01-16; image source, see gaps 1). Script failures on text sources: 0.
- Bar check codes below: T7 = pending Task 7 (research-window bars); S2 = validated against CME schedules only, bar check pending the step 2 purchase; H2 = validated against CME schedules only; embargo or holdout-2 date, never checked against bars (full strings in the JSON).

## Verbatim check

Document text: .xls = LibreOffice CSV export of every sheet ('|' separated, trailing '|' dropped per line, cells as LibreOffice displays them; zip members read from the zip); .pdf = `pdftotext -layout`; service .json = the raw response; Confluence REST .json = body.storage value with tags stripped; .html = tags stripped (scripts and styles removed), entities unescaped. Normalization of both quote and document: zero-width characters (U+200B-U+200D, U+FEFF) deleted, then every run of whitespace replaced by one space. A quote may elide text with '...': every segment must be a substring of the normalized document, and the segments must occur in the quoted order. Image (.png) sources cannot be checked by script: their quotes are transcriptions and carry verbatim false.

## Entries

| Date | Name | Kind | Halt CT | Status | Time | Verbatim | Source doc | Bar | Next session |
|---|---|---|---|---|---|---|---|---|---|
| 2019-05-27 | Memorial Day | full_closure | - | cme | n/a | True | x19_mem | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2019-05-27 for trade date 2019-05-28. |
| 2019-07-03 | Day before Independence Day | early_halt | 12:05 | cme | cme | True | x19_jul | S2 | No grain evening session (trade date 2019-07-04 is closed). |
| 2019-07-04 | Independence Day | full_closure | - | cme | n/a | True | x19_jul | S2 | No grain evening session on 2019-07-03 or on 2019-07-04; trade date 2019-07-05 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2019-09-02 | Labor Day | full_closure | - | cme | n/a | True | x19_lab | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2019-09-02 for trade date 2019-09-03. |
| 2019-11-28 | Thanksgiving Day | full_closure | - | cme | n/a | True | x19_thx | S2 | No grain evening session on 2019-11-27 or on 2019-11-28; trade date 2019-11-29 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2019-11-29 | Day after Thanksgiving | early_halt | 12:05 | cme | cme | True | x19_thx | S2 | Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not in the schedule). |
| 2019-12-24 | Christmas Eve | early_halt | 12:05 | cme | cme | True | x19_xms | S2 | No grain evening session (trade date 2019-12-25 is closed). |
| 2019-12-25 | Christmas Day | full_closure | - | cme | n/a | True | x19_xms | S2 | No grain evening session on 2019-12-24 or on 2019-12-25; trade date 2019-12-26 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2020-01-01 | New Year's Day | full_closure | - | cme | n/a | True | x19_ny | S2 | No grain evening session on 2019-12-31 or on 2020-01-01; trade date 2020-01-02 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2020-01-20 | Martin Luther King Jr. Day | full_closure | - | cme | n/a | True | x20_mlk | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2020-01-20 for trade date 2020-01-21. |
| 2020-02-17 | Presidents Day | full_closure | - | cme | n/a | True | x20_pres | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2020-02-17 for trade date 2020-02-18. |
| 2020-04-10 | Good Friday | full_closure | - | cme | n/a | True | x20_gf | S2 | No grain evening session on 2020-04-09; grain Globex reopens Sunday 2020-04-12 19:00 CT for trade date 2020-04-13. |
| 2020-05-25 | Memorial Day | full_closure | - | cme | n/a | True | x20_mem | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2020-05-25 for trade date 2020-05-26. |
| 2020-07-02 | Day before Independence Day (observed) | early_halt | 12:05 | cme | cme | True | x20_jul | S2 | No grain evening session (trade date 2020-07-03 is closed). |
| 2020-07-03 | Independence Day (observed) | full_closure | - | cme | n/a | True | x20_jul | S2 | No grain evening session on 2020-07-02; grain Globex reopens Sunday 2020-07-05 19:00 CT for trade date 2020-07-06. |
| 2020-09-07 | Labor Day | full_closure | - | cme | n/a | True | x20_lab | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2020-09-07 for trade date 2020-09-08. |
| 2020-11-26 | Thanksgiving Day | full_closure | - | cme | n/a | True | x20_thx | S2 | No grain evening session on 2020-11-25 or on 2020-11-26; trade date 2020-11-27 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2020-11-27 | Day after Thanksgiving | early_halt | 12:05 | cme | cme | True | x20_thx | S2 | Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not in the schedule). |
| 2020-12-24 | Christmas Eve | early_halt | 12:05 | cme | cme | True | x20_xms | S2 | No grain evening session (trade date 2020-12-25 is closed). |
| 2020-12-25 | Christmas Day | full_closure | - | cme | n/a | True | x20_xms | S2 | No grain evening session on 2020-12-24; grain Globex reopens Sunday 2020-12-27 19:00 CT for trade date 2020-12-28. |
| 2021-01-01 | New Year's Day | full_closure | - | cme | n/a | True | x20_ny | S2 | No grain evening session on 2020-12-31; grain Globex reopens Sunday 2021-01-03 19:00 CT for trade date 2021-01-04. |
| 2021-01-18 | Martin Luther King Jr. Day | full_closure | - | cme | n/a | True | x21_mlk | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2021-01-18 for trade date 2021-01-19. |
| 2021-02-15 | Presidents Day | full_closure | - | cme | n/a | True | x21_pres | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2021-02-15 for trade date 2021-02-16. |
| 2021-04-02 | Good Friday | full_closure | - | cme | n/a | True | x21_gf | S2 | No grain evening session on 2021-04-01; grain Globex reopens Sunday 2021-04-04 19:00 CT for trade date 2021-04-05. |
| 2021-05-31 | Memorial Day | full_closure | - | cme | n/a | True | x21_mem | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2021-05-31 for trade date 2021-06-01. |
| 2021-07-05 | Independence Day (observed) | full_closure | - | cme | n/a | True | x21_julc | S2 | No grain session on Sunday 2021-07-04 or Monday 2021-07-05 ('Markets Closed'); trade date 2021-07-06 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2021-09-06 | Labor Day | full_closure | - | cme | n/a | True | x21_lab | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2021-09-06 for trade date 2021-09-07. |
| 2021-11-25 | Thanksgiving Day | full_closure | - | cme | n/a | True | x21_thx | S2 | No grain evening session on 2021-11-24 or on 2021-11-25; trade date 2021-11-26 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2021-11-26 | Day after Thanksgiving | early_halt | 12:05 | cme | cme | True | x21_thx | S2 | Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not in the schedule). |
| 2021-12-24 | Christmas Day (observed) | full_closure | - | cme | n/a | True | x21_xms | S2 | No grain evening session on 2021-12-23; grain Globex reopens Sunday 2021-12-26 19:00 CT for trade date 2021-12-27. |
| 2022-01-17 | Martin Luther King Jr. Day | full_closure | - | cme | n/a | True | x22_mlk | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2022-01-17 for trade date 2022-01-18. |
| 2022-02-21 | Presidents Day | full_closure | - | cme | n/a | True | x22_pres | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2022-02-21 for trade date 2022-02-22. |
| 2022-04-15 | Good Friday | full_closure | - | cme | n/a | True | x22_gf | S2 | No grain evening session on 2022-04-14; grain Globex reopens Sunday 2022-04-17 19:00 CT for trade date 2022-04-18. |
| 2022-05-30 | Memorial Day | full_closure | - | cme | n/a | True | x22_mem | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2022-05-30 for trade date 2022-05-31. |
| 2022-06-20 | Juneteenth (observed) | full_closure | - | cme | n/a | True | x22_jun | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2022-06-20 for trade date 2022-06-21. |
| 2022-07-04 | Independence Day | full_closure | - | cme | n/a | True | x22_julc | S2 | No grain session on Sunday 2022-07-03 or Monday 2022-07-04 ('Markets Closed'); trade date 2022-07-05 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2022-09-05 | Labor Day | full_closure | - | cme | n/a | True | x22_lab | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2022-09-05 for trade date 2022-09-06. |
| 2022-11-24 | Thanksgiving Day | full_closure | - | cme | n/a | True | x22_thx | S2 | No grain evening session on 2022-11-23 or on 2022-11-24; trade date 2022-11-25 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2022-11-25 | Day after Thanksgiving | early_halt | 12:05 | cme | cme | True | x22_thx | S2 | Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not in the schedule). |
| 2022-12-26 | Christmas Day (observed) | full_closure | - | cme | n/a | True | x22_xms | S2 | No grain session from Friday 2022-12-23 13:20 CT until the Monday 2022-12-26 19:00 CT open (pre-open 16:00 CT) for trade date 2022-12-27, which is therefore regular. |
| 2023-01-02 | New Year's Day (observed) | full_closure | - | cme | n/a | True | x23_ny | S2 | No grain session from Friday 2022-12-30 13:20 CT until the Monday 2023-01-02 19:00 CT open (pre-open 16:00 CT) for trade date 2023-01-03 ('NORMAL SCHEDULE'). |
| 2023-01-16 | Martin Luther King Jr. Day | full_closure | - | secondary | n/a | False | i23_mlk | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2023-01-16 for trade date 2023-01-17. |
| 2023-02-20 | Presidents Day | full_closure | - | cme | n/a | True | p23_pres | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2023-02-20 for trade date 2023-02-21. |
| 2023-04-07 | Good Friday | full_closure | - | cme | n/a | True | p23_gf | S2 | No grain evening session on 2023-04-06; the retrieved document stops before Sunday 2023-04-09: the regular Sunday 19:00 CT reopen for trade date 2023-04-10 is assumed (not in a source). |
| 2023-05-29 | Memorial Day | full_closure | - | cme | n/a | True | p23_mem | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2023-05-29 for trade date 2023-05-30. |
| 2023-06-19 | Juneteenth | full_closure | - | cme | n/a | True | p23_jun | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2023-06-19 for trade date 2023-06-20. |
| 2023-07-04 | Independence Day | full_closure | - | cme | n/a | True | p23_jul | S2 | No grain evening session on 2023-07-03 or on 2023-07-04; trade date 2023-07-05 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2023-09-04 | Labor Day | full_closure | - | cme | n/a | True | p23_lab | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2023-09-04 for trade date 2023-09-05. |
| 2023-11-23 | Thanksgiving Day | full_closure | - | cme | n/a | True | p23_thx | S2 | No grain evening session on 2023-11-22 or on 2023-11-23; trade date 2023-11-24 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2023-11-24 | Day after Thanksgiving | early_halt | 12:05 | cme | cme | True | p23_thx | S2 | Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not in the summary). |
| 2023-12-25 | Christmas Day | full_closure | - | cme | n/a | True | p23_xms | S2 | No grain session on Sunday 2023-12-24 or Monday 2023-12-25; trade date 2023-12-26 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2024-01-01 | New Year's Day | full_closure | - | cme | n/a | True | p24_ny | S2 | No grain session on Sunday 2023-12-31 or Monday 2024-01-01; trade date 2024-01-02 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2024-01-15 | Martin Luther King Jr. Day | full_closure | - | cme | n/a | True | s24_mlk | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2024-01-15 for trade date 2024-01-16. |
| 2024-02-19 | Presidents Day | full_closure | - | cme | n/a | True | s24_pres | S2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2024-02-19 for trade date 2024-02-20. |
| 2024-03-29 | Good Friday | full_closure | - | cme | n/a | True | s24_gf | H2 | No grain evening session on 2024-03-28; the retrieved document stops before Sunday 2024-03-31: the regular Sunday 19:00 CT reopen for trade date 2024-04-01 is assumed (not in a source). |
| 2024-05-27 | Memorial Day | full_closure | - | cme | n/a | True | s24_mem | H2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2024-05-27 for trade date 2024-05-28. |
| 2024-06-19 | Juneteenth | full_closure | - | cme | n/a | True | s24_jun | H2 | No grain evening session on 2024-06-18; grain Globex reopens 19:00 CT on 2024-06-19 for trade date 2024-06-20. |
| 2024-07-04 | Independence Day | full_closure | - | cme | n/a | True | s24_jul | H2 | No grain evening session on 2024-07-03 or on 2024-07-04; trade date 2024-07-05 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2024-09-02 | Labor Day | full_closure | - | cme | n/a | True | s24_lab | H2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2024-09-02 for trade date 2024-09-03. |
| 2024-11-28 | Thanksgiving Day | full_closure | - | cme | n/a | True | s24_thx | H2 | No grain evening session on 2024-11-27 or on 2024-11-28; trade date 2024-11-29 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2024-11-29 | Day after Thanksgiving | early_halt | 12:05 | cme | cme | True | s24_thx | H2 | Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not in the record). |
| 2024-12-24 | Christmas Eve | early_halt | 12:05 | cme | cme | True | s24_xms | H2 | No grain evening session (trade date 2024-12-25 is closed). |
| 2024-12-25 | Christmas Day | full_closure | - | cme | n/a | True | s24_xms | H2 | No grain evening session on 2024-12-24 or on 2024-12-25; trade date 2024-12-26 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2025-01-01 | New Year's Day | full_closure | - | cme | n/a | True | s25_ny | H2 | No grain evening session on 2024-12-31 or on 2025-01-01; trade date 2025-01-02 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2025-01-09 | National Day of Mourning (Carter) | early_halt | 12:15 | cme | cme | True | p25_dom | H2 | The schedule gives only the early close; the regular 19:00 CT reopen for trade date 2025-01-10 is assumed (not in the source). |
| 2025-01-20 | Martin Luther King Jr. Day | full_closure | - | cme | n/a | True | s25_mlk | H2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2025-01-20 for trade date 2025-01-21. |
| 2025-02-17 | Presidents Day | full_closure | - | cme | n/a | True | s25_pres | H2 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2025-02-17 for trade date 2025-02-18. |
| 2025-04-18 | Good Friday | full_closure | - | cme | n/a | True | s25_gf | T7 | No grain evening session on 2025-04-17; the retrieved document stops before Sunday 2025-04-20: the regular Sunday 19:00 CT reopen for trade date 2025-04-21 is assumed (not in a source). |
| 2025-05-26 | Memorial Day | full_closure | - | cme | n/a | True | s25_mem | T7 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2025-05-26 for trade date 2025-05-27. |
| 2025-06-19 | Juneteenth | full_closure | - | cme | n/a | True | s25_jun | T7 | No grain evening session on 2025-06-18; grain Globex reopens 19:00 CT on 2025-06-19 for trade date 2025-06-20. |
| 2025-07-04 | Independence Day | full_closure | - | cme | n/a | True | s25_jul | T7 | No grain evening session on 2025-07-03; the retrieved document stops before Sunday 2025-07-06: the regular Sunday 19:00 CT reopen for trade date 2025-07-07 is assumed (not in a source). |
| 2025-09-01 | Labor Day | full_closure | - | cme | n/a | True | s25_lab | T7 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2025-09-01 for trade date 2025-09-02. |
| 2025-11-27 | Thanksgiving Day | full_closure | - | cme | n/a | True | s25_thx | T7 | No grain evening session on 2025-11-26 or on 2025-11-27; trade date 2025-11-28 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2025-11-28 | Day after Thanksgiving | early_halt | 12:05 | cme | cme | True | s25_thx | T7 | Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not in the record). |
| 2025-12-24 | Christmas Eve | early_halt | 12:05 | cme | cme | True | s25_xms | T7 | No grain evening session (trade date 2025-12-25 is closed). |
| 2025-12-25 | Christmas Day | full_closure | - | cme | n/a | True | s25_xms | T7 | No grain evening session on 2025-12-24 or on 2025-12-25; trade date 2025-12-26 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2026-01-01 | New Year's Day | full_closure | - | cme | n/a | True | s26_ny | T7 | No grain evening session on 2025-12-31 or on 2026-01-01; trade date 2026-01-02 has no overnight segment and opens 08:30 CT (LATE_OPENS). |
| 2026-01-19 | Martin Luther King Jr. Day | full_closure | - | cme | n/a | True | s26_mlk | T7 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2026-01-19 for trade date 2026-01-20. |
| 2026-02-16 | Presidents Day | full_closure | - | cme | n/a | True | s26_pres | T7 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2026-02-16 for trade date 2026-02-17. |
| 2026-04-03 | Good Friday | full_closure | - | cme | n/a | True | s26_gf | T7 | No grain evening session on 2026-04-02; the retrieved document stops before Sunday 2026-04-05: the regular Sunday 19:00 CT reopen for trade date 2026-04-06 is assumed (not in a source). |
| 2026-05-25 | Memorial Day | full_closure | - | cme | n/a | True | s26_mem | T7 | No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2026-05-25 for trade date 2026-05-26. |
| 2026-06-19 | Juneteenth | full_closure | - | cme | n/a | True | s26_jun | T7 | No grain evening session on 2026-06-18; the next session (Sunday 2026-06-21 19:00 CT) lies outside the coverage. |

## Late opens (LATE_OPENS)

Trade dates with no overnight segment: the first trading minute is 08:30 CT on the date. Every one follows a full closure on the previous calendar day.

| Date | Name | Open CT | Status | Time | Verbatim | Source doc | Bar |
|---|---|---|---|---|---|---|---|
| 2019-07-05 | Day after Independence Day | 08:30 | cme | cme | True | x19_jul | S2 |
| 2019-11-29 | Day after Thanksgiving | 08:30 | cme | cme | True | x19_thx | S2 |
| 2019-12-26 | Day after Christmas | 08:30 | cme | cme | True | x19_xms | S2 |
| 2020-01-02 | Day after New Year's Day | 08:30 | cme | cme | True | x19_ny | S2 |
| 2020-11-27 | Day after Thanksgiving | 08:30 | cme | cme | True | x20_thx | S2 |
| 2021-07-06 | Day after Independence Day (observed) | 08:30 | cme | cme | True | x21_julc | S2 |
| 2021-11-26 | Day after Thanksgiving | 08:30 | cme | cme | True | x21_thx | S2 |
| 2022-07-05 | Day after Independence Day | 08:30 | cme | cme | True | x22_julc | S2 |
| 2022-11-25 | Day after Thanksgiving | 08:30 | cme | cme | True | x22_thx | S2 |
| 2023-07-05 | Day after Independence Day | 08:30 | cme | cme | True | p23_jul | S2 |
| 2023-11-24 | Day after Thanksgiving | 08:30 | cme | cme | True | p23_thx | S2 |
| 2023-12-26 | Day after Christmas | 08:30 | cme | cme | True | p23_xms | S2 |
| 2024-01-02 | Day after New Year's Day | 08:30 | cme | cme | True | p24_ny | S2 |
| 2024-07-05 | Day after Independence Day | 08:30 | cme | cme | True | s24_jul | H2 |
| 2024-11-29 | Day after Thanksgiving | 08:30 | cme | cme | True | s24_thx | H2 |
| 2024-12-26 | Day after Christmas | 08:30 | cme | cme | True | s24_xms | H2 |
| 2025-01-02 | Day after New Year's Day | 08:30 | cme | cme | True | s25_ny | H2 |
| 2025-11-28 | Day after Thanksgiving | 08:30 | cme | cme | True | s25_thx | T7 |
| 2025-12-26 | Day after Christmas | 08:30 | cme | cme | True | s25_xms | T7 |
| 2026-01-02 | Day after New Year's Day | 08:30 | cme | cme | True | s26_ny | T7 |

Interface extension: `LATE_OPENS: dict[date, LateOpen]` with `LateOpen(day, name, open_ct, evidence, time_evidence)` and `LATE_OPEN_SOURCES`. The field names match the first five fields of `data.calendars.rates.LateOpen` (rates adds `halt_from_ct` and `halt_from_offset_days` for its unscheduled outage). Additive: `HOLIDAYS` and the `data.cme_calendar` types are unchanged; a Thanksgiving Friday appears in both HOLIDAYS (12:05 CT early halt) and LATE_OPENS (08:30 CT open).

## Session-hour changes found

None found for 2019-05-01..2026-06-19: one regime covers the whole window (SESSIONS has one
SessionSpec). The grain Globex trade date D is 19:00 CT on D-1 to 07:45 CT on D (Sunday 19:00 CT
for Monday), a pause 07:45-08:30 CT (halt at 07:45, pre-open from 08:00, no matching), and the day
session 08:30-13:20 CT; at 13:20 CT the market pauses (no matching) and closes at 13:30 CT, with a
post-close pre-open (PCP) 14:30-16:00 CT and the next pre-open at 16:45 CT (Sunday 16:00 CT).
Pre-open and PCP states carry no trading.

Evidence (session_sources and the per-entry quotes):
- CME contract specifications, 2019 captures of all five products (ZC 2019-04-06, ZW 2019-07-20,
  ZS 2019-03-28, ZM 2019-07-18, ZL 2019-07-21): "Sunday – Friday, 7:00 p.m. – 7:45 a.m. CT and
  Monday – Friday, 8:30 a.m. – 1:20 p.m. CT" (ZW and ZL write "Sunday – Friday:").
- Every CME Globex holiday schedule 2019-2022 shows the regular grain events around each holiday
  (19:00 open, "7:45 (H) 8:00" halt and pre-open, 08:30 open, 13:20 close, PCP 14:30-16:00), and
  CME's 2023 holiday summary PDFs show 07:45 PAUSED, 08:00 PREOPEN, 08:30 OPEN, 13:20 PAUSED, 13:30
  CLOSED, 14:30 PCP, 16:00 CLOSED, 16:45 PREOPEN, 19:00 OPEN.
- CME's ZC trading-hours service records 2023-09..2026-06 show the same regular events (for
  example 2024-11-27 and 2026-04-01 in session_sources).
- CME's client-systems wiki (Grains settlement page, version 2026-08-20) lists "Changes in Trading
  Hours for CBOT Grain and Oilseed and KCBT Markets 04/01/2013" as its latest grain trading-hours
  advisory; nothing after it.
- A Firecrawl web search (2026-09-25, about 01:18 PDT) for later grain-hours changes returned CME's
  current corn page and a CME Globex notice of 2026-07-13 (after the coverage), both with the same
  hours in their search snippets. These snippets were not fetched and are not used as evidence
  ([unverified]).

Two CME context items for the reader (not session changes): the 2025-11-27/28 CME Globex outage
fell while grains were closed for Thanksgiving (entry 2025-11-28 notes); and TopstepX's own grain
hours (reports/stage_e0_topstep_facts.md F4.3) state the overnight session as "Sunday–Monday: 7:00
PM – 7:45 AM CT", which reads as a Topstep wording slip for CME's Sunday-Thursday evenings; that
is the lead's to rule on if it matters (D9).

## D6 confirmation

Design D6 row: grains (ZC, ZW, ZS, ZM, ZL) O 08:30, C 13:15, F 13:18 CT (session close 13:20).
SESSIONS encodes day_session_ct = (08:30, 13:15) for each of the five products, unchanged.

- C = 13:15 CT: CONFIRMED. CME's settlement procedures for each product state that "CME Group
  staff determines the daily settlements in CBOT Corn (ZC) futures on trading activity on CME
  Globex between 13:14:00 and 13:15:00 Central Time (CT), the settlement period" (ZC; the same
  sentence for Wheat (ZW), Soybeans (ZS), Soybean Meal (ZM) and Soybean Oil (ZL);
  session_sources settle_zc, settle_zw, settle_zs, settle_zm, settle_zl), the umbrella Grains page
  names all five in one sentence (settle_grains), and CME's Daily Settlement Time Details table
  reads "Grains/Oilseeds 13:14:00-13:15:00 CT" (settle_times). The settlement period ends at 13:15
  CT, which is C. These are CME's current pages (versions 2025-02-14 to 2026-08-20, fetched
  2026-09-25); their advisory list records "New Settlement Methodology for CBOT Agricultural
  Futures 06/08/2012" and no later methodology change, so the 13:14-13:15 period is taken to hold
  for 2019-2026 (from the list, not from dated copies of the procedure).
- O = 08:30 CT: CONFIRMED as CME's day-session open (2019 contract specifications of all five
  products: "Monday – Friday, 8:30 a.m. – 1:20 p.m. CT"; every holiday schedule and service record
  shows the 08:30 open). CME's settlement procedures do not define an open.
- Session close 13:20 CT: CONFIRMED (contract specifications; service records "13:20 paused",
  "13:30 closed": matching stops at 13:20 CT).
- F = 13:18 CT is not a CME value: design D9 sets it two minutes before the 13:20 CT close
  (Topstep's rule); it is consistent with CME's close.
- Early-close days (for the rules engine; not a D6 value): on every 12:05 CT grain early close
  CME settles agricultural products at 12:00:00 CT (extra_evidence: 2019-07-03, 2019-11-29,
  2019-12-24, 2020-07-02, the Thanksgiving Fridays 2020-2025, 2024-12-24, 2025-12-24): the same
  five minutes between settlement and close as the regular 13:15/13:20.

No discrepancy with D6 was found.

## Entries graded secondary or unverified, and why

- 2023-01-16 Martin Luther King Jr. Day, full closure, status "secondary": see gaps item 1.
  Time grade "n/a" (closure). Next session from the same image: 19:00 CT Monday for trade date
  2023-01-17.
- No entry is graded "unverified". No time is graded "secondary", "inferred" or "unverified":
  every halt and late-open time is stated by a CME document. "empirical" is not used.

## Gaps

1. MLK Day 2023 (2023-01-16): no CME document with grain hours was retrievable. CME's 2023 MLK
   xls (…-compact-mgex-dme.xls) lists only MGEX and DME products, CME's holiday page (capture
   2023-01-16) links the day to its JavaScript trading-hours service, whose Wayback captures hold
   no 2023-01 events, and CME's electronic-trading notices of January 2023 have no holiday table.
   The entry rests on AMP Futures' image of CME's Globex schedule (status "secondary"; the image is
   transcribed, so verbatim_check is false for this one entry) and on the pattern of every other
   year. CME's own MLK 2023 settlement notice (no CBOT settlement prices that day) agrees.
2. Fridays 2023-12-22 and 2023-12-29 (before the Monday Christmas and New Year's Day of 2023-24):
   no CME grain Globex schedule covers these days; CME's settlement notices (captures 2023-02-03,
   ten months before) say only rates settle early. Regular sessions assumed; no entry;
   NO_ENTRY_FINDINGS grade "settlement-only". Both lie in the confirmation window (bar check
   pending the step 2 purchase).
3. The Sunday 19:00 CT reopen after Friday closures in 2023-2026 (Good Friday 2023, 2024, 2025,
   2026; Independence Day 2025) and after the Thanksgiving Fridays, and the evening after the
   2025-01-09 early close, lie outside the date range of the retrieved documents. The regular
   reopen is assumed (next_session says so); in 2020-2022 CME's schedules show the Sunday 19:00 CT
   reopen after every Friday closure.
4. Capture dates: CME's 2022 single-file schedules and the 2023 New Year schedule were captured
   on 2022-07-04 ("Updated 6/29/2022"); for Labor Day, Thanksgiving and Christmas 2022 and New
   Year 2023 that is months before the holiday, and a later revision, if any, was not seen. The
   2019-2021 schedules come from CME's yearly archives. The 2023 summary PDFs for Christmas 2023
   and New Year 2024 are 2026 captures of the files CME still hosts.
5. Juneteenth 2021 (federal observance Friday 2021-06-18): CME's 2021 archive has no Juneteenth
   schedule; CME's first Juneteenth closure is 2022-06-20. Regular session assumed; no entry.
6. Columbus Day and Veterans Day: no grain Globex change in any document (CME's settlement notices
   call them normal settlement days); no entries.
7. Product scope: CME's service records are for Corn (ZC) only; the 2019-2022 schedules give one
   "Grains and Oilseeds" row and the 2023 summaries one "GRAINS" row. ZW, ZS, ZM and ZL are taken to
   share ZC's holiday hours, as they share its regular hours (2019 contract specifications).
8. No year lacks CME documents except as listed above; no entry was filled by pattern alone.

## Superseded CME drafts (for the lead)

CME revised two 2021 settlement notices after first posting them. The shared cache's copies (the
Wayback captures of 2021-01-15, fetched by CalendarBuilder-Rates) are the January 2021 drafts:
- fourth-of-july-settlement-times-2021.pdf, draft: "Friday, July 2, 2021 Settlement Times
  Agricultural Products 12:00:00 CT"; final (capture 2024-07-22): "Agricultural Products (Grains,
  Livestock, Dairy, Commodity Index) Normal Settlement Times" (rates still 12:00 CT).
- christmas-holiday-settlement-times-2021.pdf, draft: "Thursday, 12/23/2021 Agricultural Products
  (Grains, Livestock, Dairy, Commodity Index) 12:00:00 CT" and Equity 12:00 CT; final (capture
  2021-12-22): agricultural and equity products "Normal Settlement Times" (rates and FX 12:00 CT).
CME's Globex schedules for both days show the regular 13:20 CT grain close, matching the finals.
Any other group that reads agricultural or equity early settlements from the January 2021 drafts
should use the finals (the livestock builder in particular).

Side finding for the equity calendar (not acted on; data/cme_calendar.py is not this builder's):
D.1f graded the equity entry 2021-01-01 (New Year's Day) "unverified" because no 2021 document
was fetched. CME's own schedule in the 2020 yearly archive (member 2021-new-years-holiday-
schedule.xls, "Updated 12/09/2020") reads "Equity Products|04:00:00 PM|Globex Closed|04:00:00
PM|05:00:00 PM|||||||04:00:00 PM" under "Calendar Date|Thursday, December 31|Friday, January 1|
Sunday, January 3||||||Monday, January 4": a CME-direct source for that full closure.

## No-entry findings

| Date | Grade | Source doc | Verbatim | Note |
|---|---|---|---|---|
| 2019-12-31 | cme | x19_ny | True | New Year's Eve: CME's schedule gives the grain 'Close 13:20 PCP: 14:30-16:00' (regular); the evening session is absent because 2020-01-01 is closed. |
| 2020-07-06 | cme | x20_jul | True | Monday after the observed Independence Day: grain Globex opens Sunday July 5 at 19:00 CT (regular overnight), not a late open. |
| 2020-12-28 | cme | x20_xms | True | Monday after Christmas: Sunday December 27 19:00 CT open, Monday pre-open 08:00 and open 08:30 (the regular morning pause), not a late open. |
| 2020-12-31 | cme | x20_ny | True | New Year's Eve: regular 13:20 CT grain close. |
| 2021-01-04 | cme | x20_ny | True | Monday after New Year's Day: Sunday January 3 19:00 CT open (regular). |
| 2021-07-02 | cme | x21_jul | True | Friday before the observed Independence Day: 'Regular Close' 13:20 CT. CME's FINAL settlement notice (capture 2024-07-22) says 'Agricultural Products (Grains, Livestock, Dairy, Commodity Index) Normal Settlement Times'; its January 2021 draft (capture 2021-01-15, the copy in the shared cache) had 'Agricultural Products 12:00:00 CT' (superseded; extra_evidence). |
| 2021-12-23 | cme | x21_xms | True | Thursday before the observed Christmas: grain close '13:20 (**PCP 14:30-16:00)'. CME's FINAL settlement notice (capture 2021-12-22) says agricultural products settle at normal times; the January 2021 draft (capture 2021-01-15) had 12:00:00 CT (superseded; extra_evidence). |
| 2021-12-27 | cme | x21_xms | True | Monday after the observed Christmas: Sunday December 26 19:00 CT open (regular). |
| 2021-12-31 | cme | x21_ny | True | New Year's Eve 2021 (New Year's Day fell on a Saturday): Thursday 19:00 CT open, Friday 08:30-13:20 CT; a regular grain day. |
| 2022-01-03 | cme | x21_ny | True | Monday after New Year's Day on a Saturday: Sunday January 2 19:00 CT open, 'NORMAL SCHEDULE' (no closure; the equity D.1f finding agrees). |
| 2022-07-01 | cme | x22_jul | True | Friday before Independence Day: 'Regular Close' 13:20 CT. |
| 2022-12-23 | cme | x22_xms | True | Friday before the observed Christmas: grain close '13:20 (**PCP 14:30-16:00)'. |
| 2022-12-27 | cme | x22_xms | True | Tuesday after the observed Christmas: Monday 19:00 CT open (regular overnight). |
| 2023-01-03 | cme | x23_ny | True | Tuesday after the observed New Year's Day: Monday 19:00 CT open, 'NORMAL SCHEDULE'. |
| 2023-07-03 | cme | p23_jul | True | Monday before Independence Day: the GRAINS Monday column is a regular day (07:45 PAUSED, 08:00 PREOPEN, 08:30 OPEN, 13:20 PAUSED, 13:30 CLOSED, 14:30 PCP, 16:00 CLOSED); unlike 2019-07-03 and 2020-07-02 there is no 12:05 CT early close. |
| 2023-12-22 | settlement-only | n23_xms | True | Friday before Christmas (Monday): SETTLEMENT NOTICE ONLY (capture 2023-02-03): agricultural products settle at their normal time; no CME grain Globex schedule for this day was retrieved. Regular session assumed; listed under gaps. |
| 2023-12-29 | settlement-only | n24_nye | True | Friday before New Year's Day (Monday): SETTLEMENT NOTICE ONLY (capture 2023-02-03): only rates settle early; no CME grain Globex schedule for this day was retrieved. Regular session assumed; listed under gaps. |
| 2024-07-03 | cme | s24_jul | True | Wednesday before Independence Day: regular grain events (07:45 paused, 08:30 open, 13:20 paused, 13:30 closed ...), no 12:05 CT early close; no evening open (2024-07-04 closed). |
| 2024-12-31 | cme | s25_ny | True | New Year's Eve: regular grain day (13:20 CT). |
| 2025-07-03 | cme | s25_jul | True | Thursday before Independence Day: regular grain day (13:20 CT), no early close. |
| 2025-12-31 | cme | s26_ny | True | New Year's Eve: regular grain day (13:20 CT). |
| 2026-04-02 | cme | s26_gf | True | Thursday before Good Friday: regular grain day (13:20 CT); no evening open. |

## Extra evidence (not cited by the module)

| Date | What | Source doc | Verbatim | Quote |
|---|---|---|---|---|
| 2019-07-03 | CME settlement notice (2019 zip) | n19_jul | True | Wednesday, July 3, 2019 Settlement Times ... Agricultural Products 12:00:00 CT |
| 2019-11-29 | CME settlement notice (2019 zip) | n19_thx | True | Friday, 11/29/2019 (the day after Thanksgiving) Settlement Times ... Agricultural Products 12:00:00 CT |
| 2019-12-24 | CME settlement notice (2019 zip) | n19_xms | True | Tuesday, 12/24/2019 ... Agricultural Products (Grains, Livestock, Dairy, Commodity Index) 12:00:00 CT |
| 2020-07-02 | CME settlement notice | n20_jul | True | Thursday, July 2, 2020 Settlement Times ... Agricultural Products 12:00:00 CT |
| 2020-11-27 | CME settlement notice | n20_thx | True | Friday, 11/27/2020 (the day after Thanksgiving) Settlement Times ... Agricultural Products 12:00:00 CT |
| 2021-11-26 | CME settlement notice | n21_thx | True | Friday, 11/26/2021 (the day after Thanksgiving) Settlement Times ... Agricultural Products 12:00:00 CT |
| 2022-11-25 | CME settlement notice | n22_thx | True | Friday, November 25, 2022 (the day after Thanksgiving) Settlement ... Agricultural Products 12:00:00 CT |
| 2023-11-24 | CME settlement notice | n23_thx | True | Friday, November 24, 2023 (the day after Thanksgiving) ... Agricultural Products 12:00:00 CT |
| 2024-11-29 | CME settlement notice | n24_thx | True | Friday, November 29, 2024 (the day after Thanksgiving) ... Agricultural Products Settlement Time: 12:00:00 CT |
| 2024-12-24 | CME settlement notice | n24_xms | True | Tuesday, December 24, 2024 ... Agricultural Products Settlement Time: 12:00:00 CT |
| 2025-11-28 | CME settlement notice | n25_thx | True | Friday, November 28, 2025 (the day after Thanksgiving) ... Agricultural Products Settlement Time: 12:00:00 CT |
| 2025-12-24 | CME settlement notice | n25_xms | True | Wednesday, December 24, 2025 ... Agricultural Products Settlement Time: 12:00:00 CT |
| 2021-07-02 | CME settlement notice, January 2021 draft (superseded) | n21_jul_draft | True | Friday, July 2, 2021 Settlement Times Agricultural Products 12:00:00 CT |
| 2021-07-02 | CME settlement notice, final version | n21_jul_final | True | Friday, July 2, 2021 Settlement Times ... Agricultural Products (Grains, Livestock, Dairy, Commodity Index) Normal Settlement Times |
| 2021-12-23 | CME settlement notice, January 2021 draft (superseded) | n21_xms_draft | True | Thursday, 12/23/2021 Agricultural Products (Grains, Livestock, Dairy, Commodity Index) 12:00:00 CT |
| 2021-12-23 | CME settlement notice, final version | n21_xms_final | True | Thursday, 12/23/2021 ... Agricultural Products (Grains, Livestock, Dairy, Commodity Index) Normal Settlement Times |
| 2023-01-16 | CME settlement notice (MLK Day 2023) | n23_mlk | True | Note: Monday January 16, 2023 CME Group will not derive or disseminate settlement prices (other than the two LIBOR Settlements listed above) for CME, CBOT, NYMEX or COMEX |
| 2023-04-07 | AMP Futures image of CME's Good Friday 2023 Globex schedule (secondary) | i23_gf | False | CME Group Globex - Good Friday Holiday Schedule 6 - 7 April 2023 ... Grains \| 13:30 CST \| Closed for Good Friday |
| 2023-09-04 | CME ZC service record (capture 2024-07-08) | s23_lab | True | "globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2023-09-03","events":[{"tradingDate":"2023-09-05","eventTime":"16:00","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2023-09-04","events":[{"tradingDate":"2023-09-05","eventTime":"19:00","marketEventType":"open"}]} |
| 2023-11-23 | CME ZC service record (capture 2024-07-08) | s23_thx | True | "globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2023-11-22","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2023-11-24","eventTime":"16:45","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2023-11-23","events":[]},{"groupCode":"ZC","eventDate":"2023-11-24","events":[{"tradingDate":"2023-11-24","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2023-11-24","eventTime":"12:05","marketEventType":"closed"}]} |
| 2023-12-25 | CME ZC service record (capture 2024-07-08) | s23_xms | True | "globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2023-12-24","events":[]},{"groupCode":"ZC","eventDate":"2023-12-25","events":[]},{"groupCode":"ZC","eventDate":"2023-12-26","events":[{"tradingDate":"2023-12-26","eventTime":"06:00","marketEventType":"preopen"},{"tradingDate":"2023-12-26","eventTime":"08:30","marketEventType":"open"} |
| 2024-01-01 | CME ZC service record (capture 2024-07-08) | s24_ny | True | "globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2023-12-31","events":[]},{"groupCode":"ZC","eventDate":"2024-01-01","events":[]},{"groupCode":"ZC","eventDate":"2024-01-02","events":[{"tradingDate":"2024-01-02","eventTime":"06:00","marketEventType":"preopen"},{"tradingDate":"2024-01-02","eventTime":"08:30","marketEventType":"open"} |
| 2025-11-28 | CME ZC service record, pre-event capture 2024-12-20 (planned schedule) | s25_thx_plan | True | "globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"12:05","marketEventType":"closed"}]} |

## Session sources

| Key | URL | Verbatim | Quote | Note |
|---|---|---|---|---|
| cme_grain_hours | https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/corn_contract_specifications.html | True | Trading Hours Sunday – Friday, 7:00 p.m. – 7:45 a.m. CT and Monday – Friday, 8:30 a.m. – 1:20 p.m. CT ... CME Globex: ZC | Primary citation of SESSIONS: CME contract specifications, Corn (capture 2019-04-06). The same hours for ZW, ZS, ZM, ZL: hours_2019_zw..hours_2019_zl; unchanged in CME's ZC service records 2024 and 2026: hours_2024_zc, hours_2026_zc; no later change in CME's grain advisory list: hours_history. |
| hours_2019_zc | https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/corn_contract_specifications.html | True | Trading Hours Sunday – Friday, 7:00 p.m. – 7:45 a.m. CT and Monday – Friday, 8:30 a.m. – 1:20 p.m. CT ... CME Globex: ZC | CME contract specifications, Corn (capture 2019-04-06). |
| hours_2019_zw | https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/wheat_contract_specifications.html | True | Trading Hours Sunday – Friday: 7:00 p.m. – 7:45 a.m. CT and Monday – Friday: 8:30 a.m. – 1:20 p.m. CT ... CME Globex: ZW | CME contract specifications, Chicago SRW Wheat (capture 2019-07-20). |
| hours_2019_zs | https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/soybean_contract_specifications.html | True | Trading Hours Sunday – Friday, 7:00 p.m. – 7:45 a.m. CT and Monday – Friday, 8:30 a.m. – 1:20 p.m. CT ... CME Globex: ZS | CME contract specifications, Soybean (capture 2019-03-28). |
| hours_2019_zm | https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/soybean-meal_contract_specifications.html | True | Trading Hours Sunday – Friday, 7:00 p.m. – 7:45 a.m. CT and Monday – Friday, 8:30 a.m. – 1:20 p.m. CT ... CME Globex: ZM | CME contract specifications, Soybean Meal (capture 2019-07-18). |
| hours_2019_zl | https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/soybean-oil_contract_specifications.html | True | Trading Hours Sunday – Friday: 7:00 p.m. – 7:45 a.m. CT and Monday – Friday: 8:30 a.m. – 1:20 p.m. CT ... CME Globex: ZL | CME contract specifications, Soybean Oil (capture 2019-07-21). |
| hours_2024_zc | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535 | True | "globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2024-11-27","events":[{"tradingDate":"2024-11-27","eventTime":"07:45","marketEventType":"paused"},{"tradingDate":"2024-11-27","eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-11-27","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-11-27","eventTime":"13:20","marketEventType":"paused"},{"tradingDate":"2024-11-27","eventTime":"13:30","marketEventType":"closed"},{"tradingDate":"2024-11-27","eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-11-27","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-11-29","eventTime":"16:45","marketEventType":"preopen"}]} | A regular grain day in CME's ZC service record (2024-11-27): 07:45 paused, 08:00 preopen, 08:30 open, 13:20 paused, 13:30 closed; the regular day also carries a 19:00 CT open for the next trade date (for example 2024-01-16 in the MLK record). |
| hours_2026_zc | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1743113432016 | True | "globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2026-04-01","events":[{"tradingDate":"2026-04-01","eventTime":"07:45","marketEventType":"paused"},{"tradingDate":"2026-04-01","eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2026-04-01","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2026-04-01","eventTime":"13:20","marketEventType":"paused"},{"tradingDate":"2026-04-01","eventTime":"13:30","marketEventType":"closed"},{"tradingDate":"2026-04-01","eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2026-04-01","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-04-02","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2026-04-02","eventTime":"19:00","marketEventType":"open"}]} | A regular grain day in CME's ZC service record (2026-04-01): the same events, and the 16:45 preopen and 19:00 open for trade date 2026-04-02. |
| hours_history | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457414829/Grains | True | Agriculture Advisories Changes in Trading Hours for CBOT Grain and Oilseed and KCBT Markets 04/01/2013 | CME client-systems wiki, Grains settlement page (version 2026-08-20): its advisory list names no grain trading-hours change after 04/01/2013. |
| settle_grains | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457414829/Grains | True | CME Group staff determines the daily settlements in CBOT Corn (ZC), Wheat (ZW), Rice (ZR), Oats (ZO), Soybean (ZS), Soybean Meal (ZM), Soybean Oil (ZL) and KC HRW Wheat (KE) futures based on trading activity on CME Globex between 13:14:00 and 13:15:00 Central Time (CT), the settlement period. | CME client-systems wiki, Grains (page 457414829, version 2026-08-20). |
| settle_zc | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457090243/Corn | True | CME Group staff determines the daily settlements in CBOT Corn (ZC) futures on trading activity on CME Globex between 13:14:00 and 13:15:00 Central Time (CT), the settlement period. | CME client-systems wiki, Corn (page 457090243, version 2025-02-14). |
| settle_zw | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457321091/Wheat | True | CME Group staff determines the daily settlements in CBOT Wheat (ZW) futures based on trading activity on CME Globex between 13:14:00 and 13:15:00 Central Time (CT), the settlement period. | CME client-systems wiki, Wheat (page 457321091, version 2025-12-31). |
| settle_zs | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457090434/Soybeans | True | CME Group staff determines the daily settlements in CBOT Soybeans (ZS) futures based on trading activity on CME Globex between 13:14:00 and 13:15:00 Central Time (CT), the settlement period. | CME client-systems wiki, Soybeans (page 457090434, version 2025-12-31). |
| settle_zm | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457321181/Soybean+Meal | True | CME Group staff determines the daily settlements in CBOT Soybean Meal (ZM) futures on trading activity on CME Globex between 13:14:00 and 13:15:00 Central Time (CT), the settlement period. | CME client-systems wiki, Soybean Meal (page 457321181, version 2025-12-31). |
| settle_zl | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457090469/Soybean+Oil | True | CME Group staff determines the daily settlements in CBOT Soybean Oil (ZL) futures based on trading activity on CME Globex between 13:14:00 and 13:15:00 Central Time (CT), the settlement period. | CME client-systems wiki, Soybean Oil (page 457090469, version 2025-12-31). |
| settle_times | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457085528/Daily+Settlement+Time+Details | True | Grains/Oilseeds 13:14:00-13:15:00 CT | CME client-systems wiki, Daily Settlement Time Details (fetched by CalendarBuilder-Energy). |

## Documents used

Original URL, the copy actually read (Wayback capture or direct), and which builder fetched it into the shared cache (times PDT).

| Key | Original URL | Fetched via | Fetched by | Fetched (PDT) |
|---|---|---|---|---|
| c19_corn | https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/corn_contract_specifications.html | https://web.archive.org/web/20190406072006id_/https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/corn_contract_specifications.html | CalendarBuilder-Grains | 2026-09-25 01:15:45 PDT |
| c19_meal | https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/soybean-meal_contract_specifications.html | https://web.archive.org/web/20190718130507id_/https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/soybean-meal_contract_specifications.html | CalendarBuilder-Grains | 2026-09-25 01:16:28 PDT |
| c19_oil | https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/soybean-oil_contract_specifications.html | https://web.archive.org/web/20190721123701id_/https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/soybean-oil_contract_specifications.html | CalendarBuilder-Grains | 2026-09-25 01:16:33 PDT |
| c19_soy | https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/soybean_contract_specifications.html | https://web.archive.org/web/20190328181851id_/https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/soybean_contract_specifications.html | CalendarBuilder-Grains | 2026-09-25 01:16:20 PDT |
| c19_wheat | https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/wheat_contract_specifications.html | https://web.archive.org/web/20190720235912id_/https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/wheat_contract_specifications.html | CalendarBuilder-Grains | 2026-09-25 01:16:11 PDT |
| i23_gf | https://www.ampfutures.com/hubfs/CME%20Group%20Globex%20-%20Good%20Friday%20Holiday%20Schedule%206%20-%207%20April%202023.png | https://www.ampfutures.com/hubfs/CME%20Group%20Globex%20-%20Good%20Friday%20Holiday%20Schedule%206%20-%207%20April%202023.png | CalendarBuilder-Rates | 2026-09-25 00:45:12 PDT |
| i23_mlk | https://www.ampfutures.com/hubfs/CME%20Holiday%20Trading%20Schedule%20-%20Dr.%20Martin%20Luther%20King%2c%20Jr.%20(2023).png | https://www.ampfutures.com/hubfs/CME%20Holiday%20Trading%20Schedule%20-%20Dr.%20Martin%20Luther%20King%2c%20Jr.%20(2023).png | CalendarBuilder-Rates | 2026-09-25 00:45:12 PDT |
| n19_jul | https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:37 PDT |
| n19_thx | https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:37 PDT |
| n19_xms | https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:37 PDT |
| n20_jul | https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2020.pdf | https://web.archive.org/web/20260715054102id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2020.pdf | CalendarBuilder-Rates | 2026-09-25 00:53:28 PDT |
| n20_thx | https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2020.pdf | https://web.archive.org/web/20210126094832id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2020.pdf | CalendarBuilder-Rates | 2026-09-25 00:54:00 PDT |
| n21_jul_draft | https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2021.pdf | https://web.archive.org/web/20210115184643id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2021.pdf | CalendarBuilder-Rates | 2026-09-25 00:53:39 PDT |
| n21_jul_final | https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2021.pdf | https://web.archive.org/web/20240722180647id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2021.pdf | CalendarBuilder-Grains | 2026-09-25 01:14:01 PDT |
| n21_thx | https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2021.pdf | https://web.archive.org/web/20210115184603id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2021.pdf | CalendarBuilder-Rates | 2026-09-25 00:54:11 PDT |
| n21_xms_draft | https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2021.pdf | https://web.archive.org/web/20210115184900id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2021.pdf | CalendarBuilder-Rates | 2026-09-25 00:54:45 PDT |
| n21_xms_final | https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2021.pdf | https://web.archive.org/web/20211222214822id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2021.pdf | CalendarBuilder-Grains | 2026-09-25 01:14:02 PDT |
| n22_thx | https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2022.pdf | https://web.archive.org/web/20220128023650id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2022.pdf | CalendarBuilder-Rates | 2026-09-25 00:54:21 PDT |
| n23_mlk | https://www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2023.pdf | https://web.archive.org/web/20230203073653id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/mlk-day-holiday-settlement-times-2023.pdf | CalendarBuilder-FX | 2026-09-25 00:43:55 PDT |
| n23_thx | https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2023.pdf | https://web.archive.org/web/20230203063905id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2023.pdf | CalendarBuilder-Energy | 2026-09-25 00:51:26 PDT |
| n23_xms | https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2023.pdf | https://web.archive.org/web/20230203075043id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2023.pdf | CalendarBuilder-FX | 2026-09-25 00:44:44 PDT |
| n24_nye | https://www.cmegroup.com/tools-information/holiday-calendar/files/new-years-eve-holiday-settlement-times-2024.pdf | https://web.archive.org/web/20230203062741id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/new-years-eve-holiday-settlement-times-2024.pdf | CalendarBuilder-Energy | 2026-09-25 00:51:16 PDT |
| n24_thx | https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2024.pdf | https://web.archive.org/web/20231209141725id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/thanksgiving-holiday-settlement-times-2024.pdf | CalendarBuilder-Energy | 2026-09-25 00:51:30 PDT |
| n24_xms | https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2024.pdf | https://web.archive.org/web/20231121134649id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2024.pdf | CalendarBuilder-Energy | 2026-09-25 00:50:34 PDT |
| n25_thx | https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/thanksgiving-holiday-settlement-times-2025.pdf | https://web.archive.org/web/20241214004507id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/thanksgiving-holiday-settlement-times-2025.pdf | CalendarBuilder-FX | 2026-09-25 00:43:57 PDT |
| n25_xms | https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/christmas-holiday-settlement-times-2025.pdf | https://web.archive.org/web/20241214020338id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2025/christmas-holiday-settlement-times-2025.pdf | CalendarBuilder-FX | 2026-09-25 00:43:57 PDT |
| p23_gf | https://www.cmegroup.com/files/good-friday.pdf | https://web.archive.org/web/20240708160009id_/https://www.cmegroup.com/files/good-friday.pdf | CalendarBuilder-Energy | 2026-09-25 00:45:55 PDT |
| p23_jul | https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf | https://web.archive.org/web/20230627125057id_/https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf | CalendarBuilder-Energy | 2026-09-25 00:30:08 PDT |
| p23_jun | https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf | https://web.archive.org/web/20230613185949id_/https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf | CalendarBuilder-Energy | 2026-09-25 00:30:20 PDT |
| p23_lab | https://www.cmegroup.com/trading-hours/files/labor-day-2023.pdf | https://web.archive.org/web/20230802192446id_/https://www.cmegroup.com/trading-hours/files/labor-day-2023.pdf | CalendarBuilder-Energy | 2026-09-25 00:30:24 PDT |
| p23_mem | https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf | https://web.archive.org/web/20230420224018id_/https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf | CalendarBuilder-FX | 2026-09-25 00:31:47 PDT |
| p23_pres | https://www.cmegroup.com/files/presidents-day.pdf | https://web.archive.org/web/20230329115747id_/https://www.cmegroup.com/files/presidents-day.pdf | CalendarBuilder-Energy | 2026-09-25 00:45:58 PDT |
| p23_thx | https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf | https://web.archive.org/web/20231203205929id_/https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf | CalendarBuilder-Energy | 2026-09-25 00:32:06 PDT |
| p23_xms | https://www.cmegroup.com/trading-hours/files/christmas-day-2023.pdf | https://web.archive.org/web/20260719095248id_/https://www.cmegroup.com/trading-hours/files/christmas-day-2023.pdf | CalendarBuilder-Energy | 2026-09-25 00:30:12 PDT |
| p24_ny | https://www.cmegroup.com/trading-hours/files/new-years-day-2024.pdf | https://web.archive.org/web/20260811165716id_/https://www.cmegroup.com/trading-hours/files/new-years-day-2024.pdf | CalendarBuilder-Energy | 2026-09-25 00:32:02 PDT |
| p25_dom | https://www.cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf | https://web.archive.org/web/20250218194143id_/https://www.cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf | CalendarBuilder-Energy | 2026-09-25 00:30:17 PDT |
| s23_lab | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-09-03&toEventDate=2023-09-05&isProtected&_t=1720455278654 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-09-03&toEventDate=2023-09-05&isProtected&_t=1720455278654 | CalendarBuilder-FX | 2026-09-25 00:35:12 PDT |
| s23_thx | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-11-22&toEventDate=2023-11-24&isProtected&_t=1720455278656 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-11-22&toEventDate=2023-11-24&isProtected&_t=1720455278656 | CalendarBuilder-FX | 2026-09-25 00:35:28 PDT |
| s23_xms | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-24&toEventDate=2023-12-26&isProtected&_t=1720455278659 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-24&toEventDate=2023-12-26&isProtected&_t=1720455278659 | CalendarBuilder-FX | 2026-09-25 00:35:28 PDT |
| s24_gf | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-03-28&toEventDate=2024-03-30&isProtected&_t=1720455278672 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-03-28&toEventDate=2024-03-30&isProtected&_t=1720455278672 | CalendarBuilder-FX | 2026-09-25 00:36:31 PDT |
| s24_jul | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680 | CalendarBuilder-FX | 2026-09-25 00:33:26 PDT |
| s24_jun | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677 | CalendarBuilder-FX | 2026-09-25 00:36:32 PDT |
| s24_lab | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1734710019534 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1734710019534 | CalendarBuilder-Energy | 2026-09-25 00:36:47 PDT |
| s24_mem | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675 | CalendarBuilder-FX | 2026-09-25 00:36:32 PDT |
| s24_mlk | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663 | CalendarBuilder-FX | 2026-09-25 00:35:45 PDT |
| s24_ny | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-31&toEventDate=2024-01-02&isProtected&_t=1720455278661 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2023-12-31&toEventDate=2024-01-02&isProtected&_t=1720455278661 | CalendarBuilder-Rates | 2026-09-25 00:35:41 PDT |
| s24_pres | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669 | https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669 | CalendarBuilder-FX | 2026-09-25 00:36:31 PDT |
| s24_thx | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535 | CalendarBuilder-Energy | 2026-09-25 00:37:50 PDT |
| s24_xms | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537 | CalendarBuilder-Energy | 2026-09-25 00:38:24 PDT |
| s25_gf | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-04-17&toEventDate=2025-04-19&isProtected&_t=1734710019542 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-04-17&toEventDate=2025-04-19&isProtected&_t=1734710019542 | CalendarBuilder-FX | 2026-09-25 00:36:37 PDT |
| s25_jul | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545 | CalendarBuilder-Rates | 2026-09-25 00:38:43 PDT |
| s25_jun | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544 | CalendarBuilder-Rates | 2026-09-25 00:37:42 PDT |
| s25_lab | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546 | CalendarBuilder-Energy | 2026-09-25 00:38:45 PDT |
| s25_mem | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543 | CalendarBuilder-Rates | 2026-09-25 00:36:46 PDT |
| s25_mlk | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539 | CalendarBuilder-FX | 2026-09-25 00:36:35 PDT |
| s25_ny | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1734710019538 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1734710019538 | CalendarBuilder-Energy | 2026-09-25 00:38:37 PDT |
| s25_pres | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540 | CalendarBuilder-FX | 2026-09-25 00:36:37 PDT |
| s25_thx | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060 | CalendarBuilder-Energy | 2026-09-25 00:39:22 PDT |
| s25_thx_plan | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1734710019547 | https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1734710019547 | CalendarBuilder-Energy | 2026-09-25 00:38:49 PDT |
| s25_xms | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064 | CalendarBuilder-Energy | 2026-09-25 00:39:39 PDT |
| s26_gf | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1743113432016 | https://web.archive.org/web/20260610104510id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1743113432016 | CalendarBuilder-Energy | 2026-09-25 00:40:11 PDT |
| s26_jun | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-18&toEventDate=2026-06-20&isProtected&_t=1784720540600 | https://web.archive.org/web/20260722114220id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-18&toEventDate=2026-06-20&isProtected&_t=1784720540600 | CalendarBuilder-Energy | 2026-09-25 00:41:29 PDT |
| s26_mem | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1749141516014 | https://web.archive.org/web/20260619114105id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1749141516014 | CalendarBuilder-Energy | 2026-09-25 00:40:48 PDT |
| s26_mlk | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068 | CalendarBuilder-Rates | 2026-09-25 00:39:49 PDT |
| s26_ny | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066 | https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066 | CalendarBuilder-Energy | 2026-09-25 00:39:46 PDT |
| s26_pres | https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1743113432015 | https://web.archive.org/web/20260610104510id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1743113432015 | CalendarBuilder-Energy | 2026-09-25 00:39:54 PDT |
| w_corn | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457090243/Corn | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457090243?expand=body.storage,version,history | CalendarBuilder-Grains | 2026-09-25 01:15:30 PDT |
| w_grains | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457414829/Grains | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457414829?expand=body.storage,version,history | CalendarBuilder-Grains | 2026-09-25 01:15:09 PDT |
| w_meal | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457321181/Soybean+Meal | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457321181?expand=body.storage,version,history | CalendarBuilder-Grains | 2026-09-25 01:15:31 PDT |
| w_oil | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457090469/Soybean+Oil | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457090469?expand=body.storage,version,history | CalendarBuilder-Grains | 2026-09-25 01:15:32 PDT |
| w_soy | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457090434/Soybeans | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457090434?expand=body.storage,version,history | CalendarBuilder-Grains | 2026-09-25 01:15:31 PDT |
| w_times | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457085528/Daily+Settlement+Time+Details | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457085528/Daily+Settlement+Time+Details | CalendarBuilder-Energy | 2026-09-25 00:48:06 PDT |
| w_wheat | https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457321091/Wheat | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457321091?expand=body.storage,version,history | CalendarBuilder-Grains | 2026-09-25 01:15:30 PDT |
| x19_jul | https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:37 PDT |
| x19_lab | https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:37 PDT |
| x19_mem | https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:37 PDT |
| x19_ny | https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:37 PDT |
| x19_thx | https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:37 PDT |
| x19_xms | https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:37 PDT |
| x20_gf | https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x20_jul | https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x20_lab | https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x20_mem | https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x20_mlk | https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x20_ny | https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x20_pres | https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x20_thx | https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x20_xms | https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x21_gf | https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x21_jul | https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x21_julc | https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x21_lab | https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x21_mem | https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x21_mlk | https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x21_ny | https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x21_pres | https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x21_thx | https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x21_xms | https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip | CalendarBuilder-Rates | 2026-09-25 00:25:38 PDT |
| x22_gf | https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule.xls | https://web.archive.org/web/20220704065501id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule.xls | CalendarBuilder-Energy | 2026-09-25 00:27:32 PDT |
| x22_jul | https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls | https://web.archive.org/web/20220704065450id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls | CalendarBuilder-Energy | 2026-09-25 00:27:34 PDT |
| x22_julc | https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls | https://web.archive.org/web/20220704065431id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls | CalendarBuilder-Energy | 2026-09-25 00:27:34 PDT |
| x22_jun | https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls | https://web.archive.org/web/20220620200210id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls | CalendarBuilder-Energy | 2026-09-25 00:27:35 PDT |
| x22_lab | https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule.xls | https://web.archive.org/web/20220704065441id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule.xls | CalendarBuilder-Energy | 2026-09-25 00:27:56 PDT |
| x22_mem | https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule.xls | https://web.archive.org/web/20220704065438id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule.xls | CalendarBuilder-Energy | 2026-09-25 00:28:35 PDT |
| x22_mlk | https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule.xls | https://web.archive.org/web/20220117212230id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule.xls | CalendarBuilder-Energy | 2026-09-25 00:28:43 PDT |
| x22_pres | https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule.xls | https://web.archive.org/web/20220704073810id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule.xls | CalendarBuilder-Energy | 2026-09-25 00:29:01 PDT |
| x22_thx | https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls | https://web.archive.org/web/20220704065423id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls | CalendarBuilder-FX | 2026-09-25 00:29:13 PDT |
| x22_xms | https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls | https://web.archive.org/web/20220704065430id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls | CalendarBuilder-Energy | 2026-09-25 00:27:31 PDT |
| x23_ny | https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule.xls | https://web.archive.org/web/20220704065501id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule.xls | CalendarBuilder-Energy | 2026-09-25 00:27:39 PDT |

## Fetch log (CalendarBuilder-Grains)

New fetches and listings by this builder (everything else was reused from the shared cache, see Documents used). No WebSearch was used; two Firecrawl searches were run (2026-09-25, about 01:12 and 01:18 PDT), no budget notice was seen.

| Time (PDT) | URL | Result |
|---|---|---|
| 2026-09-25 01:10:07 PDT | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/files/*&output=json&fl=original,timestamp,statuscode&filter=statuscode:200&collapse=urlkey&limit=5000 | OK CDX listing, 186 rows; holiday PDFs: files/good-friday.pdf, files/presidents-day.pdf (both already cached by CalendarBuilder-FX) |
| 2026-09-25 01:11:07 PDT | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar.html&from=20221201&to=20230301 | OK CDX listing (captures of the holiday-calendar page, Dec 2022-Feb 2023) |
| 2026-09-25 01:11:12 PDT | https://web.archive.org/web/20230116032437id_/https://www.cmegroup.com/tools-information/holiday-calendar.html | OK 200 text/html; charset=UTF-8 138297B sha256=2917984167c50c02 -> grains_20230116032437_holiday-calendar.html |
| 2026-09-25 01:11:28 PDT | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/notices/electronic-trading/2023/01/* | OK CDX listing of CME electronic-trading notices, Jan 2023 |
| 2026-09-25 01:11:34 PDT | https://web.archive.org/web/20260210150235id_/https://www.cmegroup.com/notices/electronic-trading/2023/01/20230109.html | OK 200 text/html; charset=UTF-8 199691B sha256=4b6b10327fb1b2bc -> grains_20260210150235_et-notice-20230109.html |
| 2026-09-25 01:11:35 PDT | https://web.archive.org/web/20260207072119id_/https://www.cmegroup.com/notices/electronic-trading/2023/01/20230102.html | OK 200 text/html; charset=UTF-8 198129B sha256=70b8ad3d7fec6f32 -> grains_20260207072119_et-notice-20230102.html |
| 2026-09-25 01:13:55 PDT | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2021.pdf | OK CDX listing of captures |
| 2026-09-25 01:13:55 PDT | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2021.pdf | OK CDX listing of captures |
| 2026-09-25 01:14:01 PDT | https://web.archive.org/web/20240722180647id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/fourth-of-july-settlement-times-2021.pdf | OK 200 application/pdf 144474B sha256=accd93ac7b42be76 -> grains_20240722180647_fourth-of-july-settlement-times-2021.pdf |
| 2026-09-25 01:14:02 PDT | https://web.archive.org/web/20211222214822id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/christmas-holiday-settlement-times-2021.pdf | OK 200 application/pdf 46865B sha256=3dc22dc4df2e2b77 -> grains_20211222214822_christmas-holiday-settlement-times-2021.pdf |
| 2026-09-25 01:14:52 PDT | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457085558?expand=body.storage,version,history | OK 200 application/json 3826B sha256=eefb640671806901 -> grains_epic_457085558_Agriculture.json |
| 2026-09-25 01:15:00 PDT | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457085558/child/page?limit=100 | OK child-page listing of the CME wiki Agriculture settlement page |
| 2026-09-25 01:15:09 PDT | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457414829/child/page?limit=100 | OK child-page listing of the CME wiki Grains settlement page |
| 2026-09-25 01:15:09 PDT | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457414829?expand=body.storage,version,history | OK 200 application/json 15405B sha256=6a2a7aee50d7a686 -> grains_epic_457414829_Grains.json |
| 2026-09-25 01:15:30 PDT | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457090243?expand=body.storage,version,history | OK 200 application/json 10478B sha256=dff0fc40da85584a -> grains_epic_457090243_Corn.json |
| 2026-09-25 01:15:30 PDT | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457321091?expand=body.storage,version,history | OK 200 application/json 12845B sha256=278f68cd14e806ab -> grains_epic_457321091_Wheat.json |
| 2026-09-25 01:15:31 PDT | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457090434?expand=body.storage,version,history | OK 200 application/json 12936B sha256=dabf7eaef2057526 -> grains_epic_457090434_Soybeans.json |
| 2026-09-25 01:15:31 PDT | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457321181?expand=body.storage,version,history | OK 200 application/json 10823B sha256=ffd614a4e0f48990 -> grains_epic_457321181_Soybean_Meal.json |
| 2026-09-25 01:15:32 PDT | https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457090469?expand=body.storage,version,history | OK 200 application/json 11671B sha256=5a0bef186c6e3790 -> grains_epic_457090469_Soybean_Oil.json |
| 2026-09-25 01:15:45 PDT | https://web.archive.org/web/20190406072006id_/https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/corn_contract_specifications.html | OK 200 text/html; charset=UTF-8 128729B sha256=02255bc2d62c482a -> grains_20190501_corn_contract_specifications.html |
| 2026-09-25 01:15:46 PDT | https://web.archive.org/web/20260417215649id_/https://www.cmegroup.com/markets/agriculture/grains/corn.contractSpecs.html | OK 200 text/html; charset=UTF-8 264328B sha256=5d619dca1bb33f85 -> grains_20260601_corn.contractSpecs.html |
| 2026-09-25 01:16:07 PDT | https://web.archive.org/web/20190501id_/https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/corn_contract_specifications.html | reused cache grains_20190501_corn_contract_specifications.html (by CalendarBuilder-Grains) |
| 2026-09-25 01:16:09 PDT | https://web.archive.org/web/20230505074233id_/https://www.cmegroup.com/markets/agriculture/grains/corn.contractSpecs.html | OK 200 text/html; charset=UTF-8 37754B sha256=8c2a679a556753db -> grains_20221231_corn_contract_specifications.html |
| 2026-09-25 01:16:11 PDT | https://web.archive.org/web/20190720235912id_/https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/wheat_contract_specifications.html | OK 200 text/html; charset=UTF-8 134910B sha256=9e090fcdd42da12a -> grains_20190501_wheat_contract_specifications.html |
| 2026-09-25 01:16:19 PDT | https://web.archive.org/web/20220311222226id_/https://www.cmegroup.com/markets/agriculture/grains/wheat.contractSpecs.html | OK 200 text/html; charset=UTF-8 207488B sha256=d684951f554c2d61 -> grains_20221231_wheat_contract_specifications.html |
| 2026-09-25 01:16:20 PDT | https://web.archive.org/web/20190328181851id_/https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/soybean_contract_specifications.html | OK 200 text/html; charset=UTF-8 126060B sha256=bbc0c4493802fa1a -> grains_20190501_soybean_contract_specifications.html |
| 2026-09-25 01:16:27 PDT | https://web.archive.org/web/20221210030020id_/https://www.cmegroup.com/markets/agriculture/oilseeds/soybean.contractSpecs.html | OK 200 text/html; charset=UTF-8 235288B sha256=eec65577897082c5 -> grains_20221231_soybean_contract_specifications.html |
| 2026-09-25 01:16:28 PDT | https://web.archive.org/web/20190718130507id_/https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/soybean-meal_contract_specifications.html | OK 200 text/html; charset=UTF-8 140968B sha256=6420824fd0830838 -> grains_20190501_soybean-meal_contract_specifications.html |
| 2026-09-25 01:16:30 PDT | https://web.archive.org/web/20230324160855id_/https://www.cmegroup.com/markets/agriculture/oilseeds/soybean-meal.contractSpecs.html | OK 200 text/html; charset=UTF-8 218238B sha256=1655c9997a425d8a -> grains_20221231_soybean-meal_contract_specifications.html |
| 2026-09-25 01:16:33 PDT | https://web.archive.org/web/20190721123701id_/https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/soybean-oil_contract_specifications.html | OK 200 text/html; charset=UTF-8 134966B sha256=703f16bbe95d35f8 -> grains_20190501_soybean-oil_contract_specifications.html |
| 2026-09-25 01:16:40 PDT | https://web.archive.org/web/20240225214953id_/https://www.cmegroup.com/markets/agriculture/oilseeds/soybean-oil.contractSpecs.html | OK 200 text/html; charset=UTF-8 222421B sha256=f2ca56916d366d1e -> grains_20221231_soybean-oil_contract_specifications.html |
| 2026-09-25 01:17:46 PDT | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/trading/agricultural/grain-and-oilseed/corn_contract_specifications.html&from=2020&to=2023 | OK CDX listing of corn old-URL spec captures 2020-2023 |
| 2026-09-25 01:17:52 PDT | https://web.archive.org/web/20210513024735id_/https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/corn_contract_specifications.html | OK 200 text/html; charset=UTF-8 79464B sha256=084909e16ef00c38 -> grains_20210513024735_corn_contract_specifications.html |
| 2026-09-25 01:12 PDT (approx., between the 01:11:35 and 01:13:55 entries) | firecrawl_search: "Martin Luther King" 2023 CBOT grains closed Monday January 16 2023 reopen 7:00 p.m. | OK 8 results, no CME grain-hours text for MLK 2023 (AMP page, CME trading-hours page, market-clock); 2 credits; no budget notice |
| 2026-09-25 01:18 PDT (approx., after the 01:17:52 entry) | firecrawl_search: CME Group CBOT grain oilseed futures trading hours change Globex ... | OK 10 results; snippets of CME's corn page and CME Globex Notice 2026-07-13 give the same hours (not fetched, [unverified]); CME wiki Grains page lists the 04/01/2013 hours change; 2 credits; no budget notice |
| 2026-09-25 01:19 PDT | note on index.jsonl | Five records appended at 01:16 carry an old contract-spec URL (…/grain-and-oilseed/<product>_contract_specifications.html) but hold the JavaScript-only new-site page Wayback redirected to (fetched_via shows markets/agriculture/...contractSpecs.html); they contain no hours text and are not cited. The 2019 captures (fetched_via …/grain-and-oilseed/…) are the cited ones. |

## Quotes per entry

### 2019-05-27 Memorial Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-memorial-day-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Updated 4/29/2019|CME Group Globex Memorial Day Holiday Schedule: May 24, 2019 - May 28, 2019 ... Trade Date|Friday, May 24||Tuesday, May 28 ... Calendar Date|Friday, May 24||Sunday, May 26|||||Monday, May 27|||||||Tuesday, May 28 ... All times are Central Time ET +1 UTC +5|Regular Fri. Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening **|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2019-05-27 for trade date 2019-05-28.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2019-07-03 Day before Independence Day (early_halt, 12:05)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-independence-day-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Updated 6/6/2019|CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019 ... Trade Date|Wednesday, July 3||Friday, July 5 ... Calendar Date|Wednesday, July 3||||||||Thursday, July 4||||||||Friday, July 5 ... All times are Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|||| ... Grains and Oilseeds ||12:05:00 PM|12:30 - 16:00| |||||Markets Closed||||||||06:00:00 AM|08:30:00 AM`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-independence-day-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Calendar Date|Wednesday, July 3||||||||Thursday, July 4||||||||Friday, July 5 ... All times are Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|||| ... Grains and Oilseeds ||12:05:00 PM|12:30 - 16:00| |||||Markets Closed||||||||06:00:00 AM|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session (trade date 2019-07-04 is closed).
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). Early Close 12:05 CT; CME's 2019 notice settles agricultural products at 12:00 CT (extra_evidence).

### 2019-07-04 Independence Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-independence-day-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Updated 6/6/2019|CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019 ... Trade Date|Wednesday, July 3||Friday, July 5 ... Calendar Date|Wednesday, July 3||||||||Thursday, July 4||||||||Friday, July 5 ... All times are Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|||| ... Grains and Oilseeds ||12:05:00 PM|12:30 - 16:00| |||||Markets Closed||||||||06:00:00 AM|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2019-07-03 or on 2019-07-04; trade date 2019-07-05 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2019-09-02 Labor Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-labor-day-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Updated 8/14/2019|CME Group Globex Labor Day Holiday Schedule: August 30, 2019 - September 3, 2019 ... Trade Date|Friday, August 30||Tuesday, September 3 ... Calendar Date|Friday, August 30||Sunday, September 1|||||Monday, September 2|||||||Tuesday, September 3 ... All times are Central Time ET +1 UTC +5|Regular Fri. Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2019-09-02 for trade date 2019-09-03.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2019-11-28 Thanksgiving Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-thanksgiving-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Updated 10/07/2019|CME Group Globex Thanksgiving Holiday Schedule: November 27, 2019 - November 29, 2019 ... Trade Date|Wednesday, November 27||Friday, November 29 ... Calendar Date|Wednesday, November 27|||||||Thursday, November 28|||||||||Friday, November 29 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2019-11-27 or on 2019-11-28; trade date 2019-11-29 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). Wednesday 2019-11-27 closes at the regular 13:20 CT; its 16:45 CT pre-open is for trade date Friday.

### 2019-11-29 Day after Thanksgiving (early_halt, 12:05)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-thanksgiving-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Updated 10/07/2019|CME Group Globex Thanksgiving Holiday Schedule: November 27, 2019 - November 29, 2019 ... Trade Date|Wednesday, November 27||Friday, November 29 ... Calendar Date|Wednesday, November 27|||||||Thursday, November 28|||||||||Friday, November 29 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-thanksgiving-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Calendar Date|Wednesday, November 27|||||||Thursday, November 28|||||||||Friday, November 29 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not in the schedule).
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). The Friday session is the day session only: no Thursday-evening session, open 08:30 CT, close 12:05 CT (CME settles agricultural products at 12:00 CT that day).

### 2019-12-24 Christmas Eve (early_halt, 12:05)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-christmas-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Updated 10/01/2019|CME Group Globex Christmas Holiday Schedule: December 24, 2019 - December 26, 2019 ... Trade Date|Tuesday, December 24|Globex Closed|Thursday, December 26 ... Calendar Date|Tuesday, December 24|Wednesday, December 25|Wednesday, December 25||||||Thursday, December 26 ... All times are Central Time ET +1 UTC +6|Close|| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|||||||06:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-christmas-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Calendar Date|Tuesday, December 24|Wednesday, December 25|Wednesday, December 25||||||Thursday, December 26 ... All times are Central Time ET +1 UTC +6|Close|| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|||||||06:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session (trade date 2019-12-25 is closed).
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2019-12-25 Christmas Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-christmas-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Updated 10/01/2019|CME Group Globex Christmas Holiday Schedule: December 24, 2019 - December 26, 2019 ... Trade Date|Tuesday, December 24|Globex Closed|Thursday, December 26 ... Calendar Date|Tuesday, December 24|Wednesday, December 25|Wednesday, December 25||||||Thursday, December 26 ... All times are Central Time ET +1 UTC +6|Close|| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|||||||06:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2019-12-24 or on 2019-12-25; trade date 2019-12-26 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2020-01-01 New Year's Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-2020-new-years-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Updated 10/01/2019|CME Group Globex New Years Holiday Schedule: December 31, 2019 - January 2, 2020 ... Trade Date|Tuesday, December 31||Thursday, January 2 ... Calendar Date|Tuesday, December 31|Wednesday, January 1|Wednesday, January 1||||||Thursday, Jan 2 ... All times are Central Time ET +1 UTC +6| Close|| Pre-opening**|Open|Pre-opening**|halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP*|||||| ... Grains and Oilseeds |13:20 PCP: 14:30-16:00|Globex Closed|||||||06:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2019-12-31 or on 2020-01-01; trade date 2020-01-02 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). New Year's Eve 2019-12-31 closes at the regular 13:20 CT (NO_ENTRY_FINDINGS).

### 2020-01-20 Martin Luther King Jr. Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-mlk-day-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Updated 4/6/2020|CME Group Globex Martin Luther King Day Holiday Schedule: January 17, 2020 - January 21, 2020 ... Trade Date|Friday, January 17||Tuesday, January 21 ... Calendar Date|Friday, January 17||Sunday, January 19|||||Monday, January 20|||||||Tuesday, January 21 ... All times are Central Time ET +1 UTC +6|Regular Fri. Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2020-01-20 for trade date 2020-01-21.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). Equities trade to a 12:00 CT halt that day (data/cme_calendar.py); grains close.

### 2020-02-17 Presidents Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-presidents-day-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Updated 4/6/2020|CME Group Globex Presidents Day Holiday Schedule: February 14, 2020 - February 18, 2020 ... Trade Date|Friday, February 14||Tuesday, February 18 ... Calendar Date|Friday, February 14||Sunday, February 16|||||Monday, February 17|||||||Tuesday, February 18 ... All times are Central Time ET +1 UTC +6|Regular Fri. Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2020-02-17 for trade date 2020-02-18.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2020-04-10 Good Friday (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-good-friday-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Updated 4/6/2020|CME Group Globex Good Friday Holiday Schedule: April 9, 2020 to April 13, 2020 ... Trade Date|Thursday, April 9|||Friday, April 10||||||Monday, April 13 ... Calendar Date|Thursday, April 9||||||Friday, April 10|||Sunday, April 12|||||Monday, April 13 ... All times are Central Time ET +1 UTC +5|Regular Close|Early Thur. Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Close|Pre-opening**|Open| ... Grains and Oilseeds |01:20:00 PM||14:30-16:00||||Globex Closed|||04:00:00 PM|07:00:00 PM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2020-04-09; grain Globex reopens Sunday 2020-04-12 19:00 CT for trade date 2020-04-13.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2020-05-25 Memorial Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-memorial-day-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Updated 4/21/2020|CME Group Globex Memorial Day Holiday Schedule: May 22, 2020 - May 26, 2020 ... Trade Date|Friday, May 22||Tuesday, May 26 ... Calendar Date|Friday, May 22||Sunday, May 24|||||Monday, May 25|||||||Tuesday, May 26 ... All times are Central Time ET +1 UTC +5|Regular Fri. Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening **|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2020-05-25 for trade date 2020-05-26.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2020-07-02 Day before Independence Day (observed) (early_halt, 12:05)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-independence-day-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Updated 6/26/2020|CME Group Globex Independence Day Holiday Schedule: July 2, 2020 to July 6, 2020 ... Trade Date|Thursday, July 2||Monday, July 6 ... Calendar Date|Thursday, July 2||||||||Friday, July 3|||Sunday, July 5|||||Monday, July 6 ... All times are Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|||||| ... Grains and Oilseeds ||12:05:00 PM|12:30 - 16:00| |||||Markets Closed|||04:00:00 PM|07:00:00 PM||||08:00:00 AM|08:30:00 AM`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-independence-day-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Calendar Date|Thursday, July 2||||||||Friday, July 3|||Sunday, July 5|||||Monday, July 6 ... All times are Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|||||| ... Grains and Oilseeds ||12:05:00 PM|12:30 - 16:00| |||||Markets Closed|||04:00:00 PM|07:00:00 PM||||08:00:00 AM|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session (trade date 2020-07-03 is closed).
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). Grains close early although equities settled normally that day (data/cme_calendar.py NO_ENTRY_FINDINGS_2019_2024 has 2020-07-02 as a normal equity day); CME's 2020 notice settles agricultural products at 12:00 CT (extra_evidence).

### 2020-07-03 Independence Day (observed) (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-independence-day-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Updated 6/26/2020|CME Group Globex Independence Day Holiday Schedule: July 2, 2020 to July 6, 2020 ... Trade Date|Thursday, July 2||Monday, July 6 ... Calendar Date|Thursday, July 2||||||||Friday, July 3|||Sunday, July 5|||||Monday, July 6 ... All times are Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|||||| ... Grains and Oilseeds ||12:05:00 PM|12:30 - 16:00| |||||Markets Closed|||04:00:00 PM|07:00:00 PM||||08:00:00 AM|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2020-07-02; grain Globex reopens Sunday 2020-07-05 19:00 CT for trade date 2020-07-06.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2020-09-07 Labor Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-labor-day-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Updated 8/28/2020|CME Group Globex Labor Day Holiday Schedule: September 4, 2020 - September 8, 2020 ... Trade Date|Friday, September 4||Tuesday, September 8 ... Calendar Date|Friday, September 4||Sunday, September 6|||||Monday, September 7|||||||Tuesday, September 8 ... All times are Central Time ET +1 UTC +5|Regular Fri. Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2020-09-07 for trade date 2020-09-08.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2020-11-26 Thanksgiving Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-thanksgiving-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Updated 10/13/2020|CME Group Globex Thanksgiving Holiday Schedule: November 25, 2020 - November 27, 2020 ... Trade Date|Wednesday, November 25||Friday, November 27 ... Calendar Date|Wednesday, November 25|||||||Thursday, November 26|||||||||Friday, November 27 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2020-11-25 or on 2020-11-26; trade date 2020-11-27 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2020-11-27 Day after Thanksgiving (early_halt, 12:05)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-thanksgiving-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Updated 10/13/2020|CME Group Globex Thanksgiving Holiday Schedule: November 25, 2020 - November 27, 2020 ... Trade Date|Wednesday, November 25||Friday, November 27 ... Calendar Date|Wednesday, November 25|||||||Thursday, November 26|||||||||Friday, November 27 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-thanksgiving-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Calendar Date|Wednesday, November 25|||||||Thursday, November 26|||||||||Friday, November 27 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not in the schedule).
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). The Friday session is the day session only: no Thursday-evening session, open 08:30 CT, close 12:05 CT (CME settles agricultural products at 12:00 CT that day).

### 2020-12-24 Christmas Eve (early_halt, 12:05)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-christmas-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Updated 11/17/2020|CME Group Globex Christmas Holiday Schedule: December 24, 2020 - December 28, 2020 ... Trade Date|Thursday, December 24|Globex Closed|Monday, December 28 ... Calendar Date|Thursday, December 24|Friday, December 25|Sunday, December 27||||||Monday, December 28 ... All times are Central Time ET +1 UTC +6|Close|| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|04:00:00 PM|07:00:00 PM|||||08:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-christmas-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Calendar Date|Thursday, December 24|Friday, December 25|Sunday, December 27||||||Monday, December 28 ... All times are Central Time ET +1 UTC +6|Close|| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|04:00:00 PM|07:00:00 PM|||||08:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session (trade date 2020-12-25 is closed).
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2020-12-25 Christmas Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-christmas-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Updated 11/17/2020|CME Group Globex Christmas Holiday Schedule: December 24, 2020 - December 28, 2020 ... Trade Date|Thursday, December 24|Globex Closed|Monday, December 28 ... Calendar Date|Thursday, December 24|Friday, December 25|Sunday, December 27||||||Monday, December 28 ... All times are Central Time ET +1 UTC +6|Close|| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|04:00:00 PM|07:00:00 PM|||||08:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2020-12-24; grain Globex reopens Sunday 2020-12-27 19:00 CT for trade date 2020-12-28.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). Monday 2020-12-28 keeps its Sunday 19:00 CT overnight (not a late open).

### 2021-01-01 New Year's Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2021-new-years-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Updated 12/09/2020|CME Group Globex New Years Holiday Schedule: December 31, 2020 - January 4, 2021 ... Trade Date|Thursday, December 31||Monday, January 4 ... Calendar Date|Thursday, December 31|Friday, January 1|Sunday, January 3||||||Monday, January 4 ... All times are Central Time ET +1 UTC +6| Close|| Pre-opening**|Open|Pre-opening**|halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP*|||||| ... Grains and Oilseeds |13:20 PCP: 14:30-16:00|Globex Closed|04:00:00 PM|07:00:00 PM|||||8:00|08:30:00 AM|01:20:00 PM|14:30-16:00`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2020-12-31; grain Globex reopens Sunday 2021-01-03 19:00 CT for trade date 2021-01-04.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). New Year's Eve 2020-12-31 closes at the regular 13:20 CT. D.1f graded the equity entry for this date unverified (not fetched); for grains CME's own schedule states it.

### 2021-01-18 Martin Luther King Jr. Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip (member 2021-mlk-day-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip; sha256 0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59
  - quote: `Updated 12/23/2020|CME Group Globex Martin Luther King Day Holiday Schedule: January 15, 2021 - January 19, 2021 ... Trade Date|Friday, January 15||Tuesday, January 19 ... Calendar Date|Friday, January 15||Sunday, January 17|||||Monday, January 18|||||||Tuesday, January 19 ... All times are Central Time ET +1 UTC +6|Regular Fri. Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2021-01-18 for trade date 2021-01-19.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2021-02-15 Presidents Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip (member 2021-presidents-day-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip; sha256 0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59
  - quote: `Updated 2/11/2021|CME Group Globex Presidents Day Holiday Schedule: February 12, 2021 - February 16, 2021 ... Trade Date|Friday, February 12||Tuesday, February 16 ... Calendar Date|Friday, February 12||Sunday, February 14|||||Monday, February 15|||||||Tuesday, February 16 ... All times are Central Time ET +1 UTC +6|Regular Fri. Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2021-02-15 for trade date 2021-02-16.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2021-04-02 Good Friday (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip (member 2021-good-friday-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip; sha256 0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59
  - quote: `Updated 3/31/2021|CME Group Globex Good Friday Holiday Schedule: April 1, 2021 to April 5, 2021 ... Trade Date|Thursday, April 1|||Friday, April 2||||||Monday, April 5 ... Calendar Date|Thursday, April 1||||||Friday, April 2|||Sunday, April 4|||||Monday, April 5 ... All times are Central Time ET +1 UTC +5|Regular Close|Early Thur. Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Close|Pre-opening**|Open| ... Grains and Oilseeds |01:20:00 PM||14:30-16:00||||Globex Closed|||04:00:00 PM|07:00:00 PM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2021-04-01; grain Globex reopens Sunday 2021-04-04 19:00 CT for trade date 2021-04-05.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). Jobs-report Good Friday: equities, rates and FX traded abbreviated sessions; grains stayed closed ('Globex Closed').

### 2021-05-31 Memorial Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip (member 2021-memorial-day-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip; sha256 0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59
  - quote: `Updated 5/25/2021|CME Group Globex Memorial Day Holiday Schedule: May 28, 2021 - Jun 1, 2021 ... Trade Date|Friday, May 28||Tuesday, Jun 1 ... Calendar Date|Friday, May 28||Sunday, May 30|||||Monday, May 31|||||||Tuesday, Jun 1 ... All times are Central Time ET +1 UTC +5|Regular Fri. Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening **|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2021-05-31 for trade date 2021-06-01.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2021-07-05 Independence Day (observed) (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip (member 2021-independence-day-holiday-schedule-compact.xls)
  - fetched via https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip; sha256 0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59
  - quote: `|CME Group Globex Independence Day Holiday Schedule: July 2, 2021 to July 6, 2021 ... Trade Date|Friday, July 2|Tuesday, July 6 ... Calendar Date|Friday July 2|Sunday July 4|Monday July 5|Monday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... Grain & Oilseed |Regular Per Product|Markets Closed|Markets Closed|Tuesday July 6 Regular @ 0830 CT / 1330 UTC`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on Sunday 2021-07-04 or Monday 2021-07-05 ('Markets Closed'); trade date 2021-07-06 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME Globex compact holiday schedule, row 'Grain & Oilseed' (the full schedule's grain row leaves the Sunday and Monday cells empty). Friday 2021-07-02 closes at the regular 13:20 CT (NO_ENTRY_FINDINGS).

### 2021-09-06 Labor Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip (member 2021-labor-day-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip; sha256 0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59
  - quote: `Updated 8/12/2021|CME Group Globex Labor Day Holiday Schedule: September 3, 2021 - September 7, 2021 ... Trade Date|Friday, September 3||Tuesday, September 7 ... Calendar Date|Friday, September 3||Sunday, September 5|||||Monday, September 6|||||||Tuesday, September 7 ... All times are Central Time ET +1 UTC +5|Regular Fri. Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2021-09-06 for trade date 2021-09-07.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2021-11-25 Thanksgiving Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip (member 2021-thanksgiving-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip; sha256 0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59
  - quote: `Updated 11/23/2021|CME Group Globex Thanksgiving Holiday Schedule: November 24, 2021 - November 26, 2021 ... Trade Date|Wednesday, November 24||Friday, November 26 ... Calendar Date|Wednesday, November 24|||||||Thursday, November 25|||||||||Friday, November 26 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2021-11-24 or on 2021-11-25; trade date 2021-11-26 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2021-11-26 Day after Thanksgiving (early_halt, 12:05)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip (member 2021-thanksgiving-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip; sha256 0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59
  - quote: `Updated 11/23/2021|CME Group Globex Thanksgiving Holiday Schedule: November 24, 2021 - November 26, 2021 ... Trade Date|Wednesday, November 24||Friday, November 26 ... Calendar Date|Wednesday, November 24|||||||Thursday, November 25|||||||||Friday, November 26 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip (member 2021-thanksgiving-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip; sha256 0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59
  - quote: `Calendar Date|Wednesday, November 24|||||||Thursday, November 25|||||||||Friday, November 26 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not in the schedule).
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). The Friday session is the day session only: no Thursday-evening session, open 08:30 CT, close 12:05 CT (CME settles agricultural products at 12:00 CT that day).

### 2021-12-24 Christmas Day (observed) (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip (member 2021-christmas-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip; sha256 0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59
  - quote: `Updated 12/01/2021|CME Group Globex Christmas Holiday Schedule: December 24, 2021 - December 27, 2021 ... Trade Date|Thursday, December 23||||||||||Monday, December 27 ... Calendar Date|Thursday, December 23|||||||||||||Friday, December 24||||||||||Sunday, December 26||||||Monday, Dec 27 ... All times are Central Time ET +1 UTC +6|Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close||Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Close| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |13:20 (**PCP 14:30-16:00)|||||||||||||Globex Closed||||||||||04:00:00 PM|07:00:00 PM|||||08:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2021-12-23; grain Globex reopens Sunday 2021-12-26 19:00 CT for trade date 2021-12-27.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). Thursday 2021-12-23 closes at the regular 13:20 CT (NO_ENTRY_FINDINGS).

### 2022-01-17 Martin Luther King Jr. Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule.xls
  - fetched via https://web.archive.org/web/20220117212230id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-mlk-day-holiday-schedule.xls; sha256 896944fa701062e2e1ee305f8adb696ba8ab03655a96874c7885f2328177626e
  - quote: `Updated 12/14/2021|CME Group Globex Martin Luther King Day Holiday Schedule: January 14, 2022 - January 18, 2022 ... Trade Date|Friday, January 14||Tuesday, January 18 ... Calendar Date|Friday, January 14|||||Sunday, January 16|||||Monday, January 17|||||||||Tuesday, January 18 ... All times are Central Time ET +1 UTC +6|Regular Fri. Close|PCP*|Pre-opening|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening|Open|Halt|Pre-opening|Open|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00||||04:00:00 PM||||||||||07:00:00 PM||||7:45 (H) 8:00|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2022-01-17 for trade date 2022-01-18.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2022-02-21 Presidents Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule.xls
  - fetched via https://web.archive.org/web/20220704073810id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-presidents-day-holiday-schedule.xls; sha256 07932975d04ccabad0fb53f33f946f1a6fd8a696bafdb21f95f030ede9a84516
  - quote: `Updated 1/24/2022|CME Group Globex Presidents Day Holiday Schedule: February 18, 2022 - February 22, 2022 ... Trade Date|Friday, February 18||Tuesday, February 22 ... Calendar Date|Friday, February 18|||||Sunday, February 20|||||Monday, February 21||||||||||||Tuesday, February 22 ... All times are Central Time ET +1 UTC +6|Regular Fri. Close|PCP*|Pre-opening|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening|Open|Halt|Pre-opening|Open|Halt|Pre-opening|Open|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00||||04:00:00 PM|||||||||||||07:00:00 PM||||7:45 (H) 8:00|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2022-02-21 for trade date 2022-02-22.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2022-04-15 Good Friday (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule.xls
  - fetched via https://web.archive.org/web/20220704065501id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-good-friday-holiday-schedule.xls; sha256 a82936ab14d1b1f7041583123289c4de401c66ace4eea7e90fa9f60c1a3f3b7e
  - quote: `Updated 3/17/2022|CME Group Globex Good Friday Holiday Schedule: April 14, 2022 to April 18, 2022 ... Trade Date|Thursday, April 14||||||Monday, April 18 ... Calendar Date|Thursday, April 14|||||||||Friday, April 15|||Sunday, April 17|||||Monday, April 18 ... All times are Central Time ET +1 UTC +5|Regular Close|Early Thur. Close|PCP*|Pre-opening**|Open|Halt/Close|Pre-opening**|Open|Halt/Close|Pre-opening**|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Close|Pre-opening**|Open| ... Grains and Oilseeds |01:20:00 PM||14:30-16:00|||||||Globex Closed|||04:00:00 PM|07:00:00 PM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2022-04-14; grain Globex reopens Sunday 2022-04-17 19:00 CT for trade date 2022-04-18.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2022-05-30 Memorial Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule.xls
  - fetched via https://web.archive.org/web/20220704065438id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-memorial-day-holiday-schedule.xls; sha256 0d1b1f89a315cae22a5857a7027a514e3086c1cccfee42fddddff3caba0c2230
  - quote: `Updated 5/18/2022|CME Group Globex Memorial Day Holiday Schedule: May 27, 2022 - May 31, 2022 ... Trade Date|Friday, May 27||Tuesday, May 31 ... Calendar Date|Friday, May 27|||||Sunday, May 29|||||Monday, May 30||||||||||Tuesday, May 31 ... All times are Central Time ET +1 UTC +5|Regular Fri. Close|PCP*|Pre-opening|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening **|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00||||04:00:00 PM|||||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2022-05-30 for trade date 2022-05-31.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2022-06-20 Juneteenth (observed) (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls
  - fetched via https://web.archive.org/web/20220620200210id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-juneteenth-holiday-schedule.xls; sha256 bc9f2caf26a73a13029f177fcc6468bdc8662899ff935f44329ee1a95c8b667b
  - quote: `Updated 5/18/2022|CME Group Globex Juneteenth Holiday Schedule: June 17, 2022 - Jun 21, 2022 ... Trade Date|Friday, June 17||Tuesday, Jun 21 ... Calendar Date|Friday, June 17|||||Sunday, June 19|||||Monday, June 20||||||||||Tuesday, Jun 21 ... All times are Central Time ET +1 UTC +5|Regular Fri. Close|PCP*| Pre-opening**|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening **|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00||||04:00:00 PM|||||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2022-06-20 for trade date 2022-06-21.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). First Juneteenth closure: CME's 2021 schedules include no Juneteenth file.

### 2022-07-04 Independence Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls
  - fetched via https://web.archive.org/web/20220704065431id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls; sha256 11925e2a7c434e05e2e3b74df1e677cd0657629370e735a11f821871e0e91e06
  - quote: `|CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022 ... Trade Date|Friday, July 1|Tuesday, July 5 ... Calendar Date|Friday July 1|Sunday July 3|Monday July 4|Monday July 4 ... Product|CLOSE|OPEN|HALT|OPEN ... Grain & Oilseed |Regular Per Product|Markets Closed|Markets Closed|Tuesday July 5 Regular @ 0830 CT / 1330 UTC`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on Sunday 2022-07-03 or Monday 2022-07-04 ('Markets Closed'); trade date 2022-07-05 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME Globex compact holiday schedule, row 'Grain & Oilseed' (the full schedule's grain row leaves the Sunday and Monday cells empty). Friday 2022-07-01 closes at the regular 13:20 CT.

### 2022-09-05 Labor Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule.xls
  - fetched via https://web.archive.org/web/20220704065441id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-labor-day-holiday-schedule.xls; sha256 28d533f25d1af74af043e411635f1933fd4ff6359c80c049f87f019d2f1d57d0
  - quote: `Updated 6/29/2022|CME Group Globex Labor Day Holiday Schedule: September 2, 2022 - September 6, 2022 ... Trade Date|Friday, September 2||Tuesday, September 6 ... Calendar Date|Friday, September 2|||||Sunday, September 4|||||Monday, September 5||||||||||Tuesday, Sept. 6 ... All times are Central Time ET +1 UTC +5|Regular Fri. Close|PCP*| Pre-opening**|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00||||04:00:00 PM|||||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2022-09-05 for trade date 2022-09-06.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2022-11-24 Thanksgiving Day (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls
  - fetched via https://web.archive.org/web/20220704065423id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls; sha256 767da53e71854a3b293b613d256642f8155cd04997fa0825a35825440448126c
  - quote: `Updated 6/29/2022|CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, 2022 ... Trade Date|Wednesday, November 23|||||Friday, November 25 ... Calendar Date|Wednesday, November 23||||||||||Thursday, November 24||||||||||||Friday, November 25 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00||||04:45:00 PM||||||||||||||||||08:30:00 AM|12:05:00 PM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2022-11-23 or on 2022-11-24; trade date 2022-11-25 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2022-11-25 Day after Thanksgiving (early_halt, 12:05)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls
  - fetched via https://web.archive.org/web/20220704065423id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls; sha256 767da53e71854a3b293b613d256642f8155cd04997fa0825a35825440448126c
  - quote: `Updated 6/29/2022|CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, 2022 ... Trade Date|Wednesday, November 23|||||Friday, November 25 ... Calendar Date|Wednesday, November 23||||||||||Thursday, November 24||||||||||||Friday, November 25 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00||||04:45:00 PM||||||||||||||||||08:30:00 AM|12:05:00 PM`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls
  - fetched via https://web.archive.org/web/20220704065423id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls; sha256 767da53e71854a3b293b613d256642f8155cd04997fa0825a35825440448126c
  - quote: `Calendar Date|Wednesday, November 23||||||||||Thursday, November 24||||||||||||Friday, November 25 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00||||04:45:00 PM||||||||||||||||||08:30:00 AM|12:05:00 PM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not in the schedule).
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). The Friday session is the day session only: no Thursday-evening session, open 08:30 CT, close 12:05 CT (CME settles agricultural products at 12:00 CT that day).

### 2022-12-26 Christmas Day (observed) (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls
  - fetched via https://web.archive.org/web/20220704065430id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-christmas-holiday-schedule.xls; sha256 2dd1d531514989845dcb6ce6d767db5dd3f956ac6777ab1cfe36d6843f3762e7
  - quote: `Updated 6/29/2022|CME Group Globex Christmas Holiday Schedule: December 23, 2022 - December 27, 2022 ... Trade Date|Friday, December 23|||||Tuesday, December 27 ... Calendar Date|Friday, December 23||||||||Monday, December 26||||||||||||||||Tuesday, December 27 ... All times are Central Time ET +1 UTC +6|Close|PCP*|Pre-opening**|Open|Halt| Pre-opening**|Open|Close||Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Close| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |13:20 (**PCP 14:30-16:00)||||||||Globex Closed||||||||||04:00:00 PM|07:00:00 PM|||||08:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session from Friday 2022-12-23 13:20 CT until the Monday 2022-12-26 19:00 CT open (pre-open 16:00 CT) for trade date 2022-12-27, which is therefore regular.
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). The capture (2022-07-04) is CME's schedule 'Updated 6/29/2022', six months before the holiday; no later version was retrieved.

### 2023-01-02 New Year's Day (observed) (full_closure, -)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule.xls
  - fetched via https://web.archive.org/web/20220704065501id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-holiday-schedule.xls; sha256 eefafd1066f406edbe6167ddf8ad13c0697b124a337c0893ce5a5da200c783d3
  - quote: `Updated 6/29/22|CME Group Globex New Year's Holiday Schedule: December 30, 2022 - January 3, 2023 ... Trade Date|Friday, December 30|Tuesday, January 3 ... Calendar Date|Friday, December 30||||Monday, January 2|Monday, January 2||||||Tuesday, January 3 ... All times are Central Time ET +1 UTC +6| Close| Pre-opening**|Open|Close|| Pre-opening**|Open|Pre-opening**|halt| Pre-opening**|Open|Close|Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |13:20 PCP: 14:30-16:00||||Globex Closed|04:00:00 PM|07:00:00 PM|NORMAL|||||SCHEDULE`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session from Friday 2022-12-30 13:20 CT until the Monday 2023-01-02 19:00 CT open (pre-open 16:00 CT) for trade date 2023-01-03 ('NORMAL SCHEDULE').
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). The capture (2022-07-04) is CME's schedule 'Updated 6/29/22'; no later version was retrieved.

### 2023-01-16 Martin Luther King Jr. Day (full_closure, -)

- status: https://www.ampfutures.com/hubfs/CME%20Holiday%20Trading%20Schedule%20-%20Dr.%20Martin%20Luther%20King%2c%20Jr.%20(2023).png
  - fetched via https://www.ampfutures.com/hubfs/CME%20Holiday%20Trading%20Schedule%20-%20Dr.%20Martin%20Luther%20King%2c%20Jr.%20(2023).png; sha256 09e7f123df0f99e6a2d75defe15427500e2219341d507fc7b7a128e06bff857f
  - quote: `CME Group Globex Dr. Martin Luther King, Jr. Holiday Schedule: 13 - 17 January 2023 ... Calendar Trade | Friday, Jan 13 | Sunday, Jan 15 | Monday, Jan 16 | Monday, Jan 16 | Tuesday, Jan 17 ... | CLOSE | OPEN | HALT | OPEN | CLOSE ... Grains | Regular per Product | Extended Pre Open @ 16:00 CST | > | 19:00 CST | Regular per Product`
- verbatim_check: False; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2023-01-16 for trade date 2023-01-17.
- notes: SECONDARY: no CME grain-hours document for MLK Day 2023 was retrievable (CME's 2023 MLK xls covers only MGEX and DME products; CME's page linked the day to its trading-hours service, whose captures hold no 2023-01 events). AMP Futures' image of 'CME Group Globex Dr. Martin Luther King, Jr. Holiday Schedule' is transcribed; the image cannot be checked by script. CME's own MLK 2023 settlement notice says no CBOT settlement prices that day, and every other year (2020-2022, 2024-2026) CME's schedule closes grains on MLK Day.

### 2023-02-20 Presidents Day (full_closure, -)

- status: https://www.cmegroup.com/files/presidents-day.pdf
  - fetched via https://web.archive.org/web/20230329115747id_/https://www.cmegroup.com/files/presidents-day.pdf; sha256 63c9f17b5dd285a522cccb6d75ac014f299d6a25defab6fd182e6ec7300d4a80
  - quote: `PRODUCT NAME Cleared As SUNDAY, 19 FEB 2023 MONDAY, 20 FEB 2023 TUESDAY, 21 FEB 2023 ... 07:45 (PAUSED) 08:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) TRADE DATE: TUES 21 FEB TRADE DATE: TUES 21 FEB 13:30 (CLOSED) GRAINS 16:00 (PREOPEN) 19:00 (OPEN) 14:30 (PCP) 16:00 (CLOSED) TRADE DATE: WED 22 FEB 16:45 (PREOPEN) 19:00 (OPEN)`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2023-02-20 for trade date 2023-02-21.
- notes: CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of each asset class); the table's column for each calendar day was read from the pdftotext -layout column positions. Sunday column: 16:00 PREOPEN; Monday column: 19:00 OPEN, both for trade date Tuesday 21 Feb.

### 2023-04-07 Good Friday (full_closure, -)

- status: https://www.cmegroup.com/files/good-friday.pdf
  - fetched via https://web.archive.org/web/20240708160009id_/https://www.cmegroup.com/files/good-friday.pdf; sha256 7c598e4e4853335eec65283677349985aaac9fff8d95cb248510bc6fac981189
  - quote: `PRODUCT NAME THURSDAY, 6 APR 2023 FRIDAY, 7 APR 2023 ... TRADE DATE: THURS 6 APR 07:45 (PAUSED) Holiday hours outlined in yellow. 08:00 (PREOPEN) GRAINS 08:30 (OPEN) 13:20 (PAUSED) 13:30 (CLOSED) 14:30 (PCP) 16:00 (CLOSED)`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2023-04-06; the retrieved document stops before Sunday 2023-04-09: the regular Sunday 19:00 CT reopen for trade date 2023-04-10 is assumed (not in a source).
- notes: CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of each asset class); the table's column for each calendar day was read from the pdftotext -layout column positions. The GRAINS row has events only in the Thursday column (regular session ending 16:00 CLOSED, no 19:00 open) and none in the Friday column, while equities, rates and FX show Friday abbreviated sessions (jobs-report Good Friday). AMP Futures' image of CME's schedule shows Grains 'Closed for Good Friday' (extra_evidence).

### 2023-05-29 Memorial Day (full_closure, -)

- status: https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf
  - fetched via https://web.archive.org/web/20230420224018id_/https://www.cmegroup.com/trading-hours/files/memorial-day-2023.pdf; sha256 7657bc8089ca669cfd244c2e3e697b47a7e650f5d957efe5b32da001622acb35
  - quote: `PRODUCT NAME SUNDAY, 28 MAY 2023 MONDAY, 29 MAY 2023 TUESDAY, 30 MAY 2023 ... TRADE DATE: TUES 30 MAY 07:45 (PAUSED) 08:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) TRADE DATE: TUES 30 MAY TRADE DATE: TUES 30 MAY 13:30 (CLOSED) GRAINS 16:00 (PREOPEN) 19:00 (OPEN) 14:30 (PCP) 16:00 (CLOSED) TRADE DATE: WED 31 MAY 16:45 (PREOPEN) 19:00 (OPEN)`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2023-05-29 for trade date 2023-05-30.
- notes: CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of each asset class); the table's column for each calendar day was read from the pdftotext -layout column positions.

### 2023-06-19 Juneteenth (full_closure, -)

- status: https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf
  - fetched via https://web.archive.org/web/20230613185949id_/https://www.cmegroup.com/trading-hours/files/juneteenth-2023.pdf; sha256 831f7f63e197ce58436780830aa515cb08dcf92bdf82a540265c2d21a4bffa43
  - quote: `PRODUCT NAME SUNDAY, 18 JUNE 2023 MONDAY, 19 JUNE 2023 TUESDAY, 20 JUNE 2023 ... TRADE DATE: TUES 20 JUNE 07:45 (PAUSED) 08:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) TRADE DATE: TUES 20 JUNE TRADE DATE: TUES 20 JUNE 13:30 (CLOSED) GRAINS 16:00 (PREOPEN) 19:00 (OPEN) 14:30 (PCP) 16:00 (CLOSED) TRADE DATE: WED 21 JUNE 16:45 (PREOPEN) 19:00 (OPEN)`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2023-06-19 for trade date 2023-06-20.
- notes: CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of each asset class); the table's column for each calendar day was read from the pdftotext -layout column positions.

### 2023-07-04 Independence Day (full_closure, -)

- status: https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf
  - fetched via https://web.archive.org/web/20230627125057id_/https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf; sha256 ccbc1f1fc39ba2219fd748372faa985798fee7eaffabf69f08956f5465a769e3
  - quote: `PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... TRADE DATE: WED 5 JULY TRADE DATE: MON 3 JULY 06:00 (PREOPEN) 07:45 (PAUSED) 08:30 (OPEN) 08:00 (PREOPEN) 13:20 (PAUSED) 08:30 (OPEN) 13:30 (CLOSED) GRAINS 14:30 (PCP) 13:20 (PAUSED) 13:30 (CLOSED) 16:00 (CLOSED) 14:30 (PCP) TRADE DATE: THUR 6 JULY 16:00 (CLOSED) 16:45 (PREOPEN) 19:00 (OPEN)`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2023-07-03 or on 2023-07-04; trade date 2023-07-05 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of each asset class); the table's column for each calendar day was read from the pdftotext -layout column positions. Two columns interleave in the text: Monday 3 July (trade date MON 3 JULY: 07:45 PAUSED, 08:00 PREOPEN, 08:30 OPEN, 13:20 PAUSED, 13:30 CLOSED, 14:30 PCP, 16:00 CLOSED, a regular day with no evening open) and Wednesday 5 July (trade date WED 5 JULY: 06:00 PREOPEN, 08:30 OPEN, ...; then TRADE DATE THUR 6 JULY 16:45 PREOPEN, 19:00 OPEN); the Tuesday 4 July column is empty for GRAINS.

### 2023-09-04 Labor Day (full_closure, -)

- status: https://www.cmegroup.com/trading-hours/files/labor-day-2023.pdf
  - fetched via https://web.archive.org/web/20230802192446id_/https://www.cmegroup.com/trading-hours/files/labor-day-2023.pdf; sha256 39a4c075437fdc7134166328eca730e3cabf3bea00ab369466dff63c99f8e948
  - quote: `PRODUCT NAME SUNDAY, 3 SEPTEMBER 2023 MONDAY, 4 SEPTEMBER 2023 TUESDAY, 5 SEPTEMBER 2023 ... TRADE DATE: TUES 5 SEP 07:45 (PAUSED) 08:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) TRADE DATE: TUES 5 SEP TRADE DATE: TUES 5 SEP 13:30 (CLOSED) GRAINS 16:00 (PREOPEN) 19:00 (OPEN) 14:30 (PCP) 16:00 (CLOSED) TRADE DATE: WED 6 SEP 16:45 (PREOPEN) 19:00 (OPEN)`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2023-09-04 for trade date 2023-09-05.
- notes: CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of each asset class); the table's column for each calendar day was read from the pdftotext -layout column positions. CME's ZC service record (captured 2024-07-08) agrees (extra_evidence).

### 2023-11-23 Thanksgiving Day (full_closure, -)

- status: https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf
  - fetched via https://web.archive.org/web/20231203205929id_/https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf; sha256 99e187b3f3899e1062d662e148d5978e0cd075b961e6fc79550d4393812307e8
  - quote: `PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 NOVEMBER 2023 ... TRADE DATE: WED 22 NOV 07:45 (PAUSED) 08:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) TRADE DATE: FRI 24 NOV GRAINS 13:30 (CLOSED) 08:30 (OPEN) 14:30 (PCP) 12:05 (CLOSED) 16:00 (CLOSED) TRADE DATE: FRI 24 NOV 16:45 (PREOPEN)`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain evening session on 2023-11-22 or on 2023-11-23; trade date 2023-11-24 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of each asset class); the table's column for each calendar day was read from the pdftotext -layout column positions. Wednesday column: regular day, then 16:45 PREOPEN for trade date FRI 24 NOV; Thursday column empty; Friday column: 08:30 OPEN, 12:05 CLOSED.

### 2023-11-24 Day after Thanksgiving (early_halt, 12:05)

- status: https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf
  - fetched via https://web.archive.org/web/20231203205929id_/https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf; sha256 99e187b3f3899e1062d662e148d5978e0cd075b961e6fc79550d4393812307e8
  - quote: `PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 NOVEMBER 2023 ... TRADE DATE: FRI 24 NOV GRAINS 13:30 (CLOSED) 08:30 (OPEN) 14:30 (PCP) 12:05 (CLOSED)`
- time: https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf
  - fetched via https://web.archive.org/web/20231203205929id_/https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf; sha256 99e187b3f3899e1062d662e148d5978e0cd075b961e6fc79550d4393812307e8
  - quote: `TRADE DATE: FRI 24 NOV GRAINS 13:30 (CLOSED) 08:30 (OPEN) 14:30 (PCP) 12:05 (CLOSED)`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not in the summary).
- notes: CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of each asset class); the table's column for each calendar day was read from the pdftotext -layout column positions. The Friday session is the day session only: no Thursday-evening session, open 08:30 CT, close 12:05 CT (CME settles agricultural products at 12:00 CT that day).

### 2023-12-25 Christmas Day (full_closure, -)

- status: https://www.cmegroup.com/trading-hours/files/christmas-day-2023.pdf
  - fetched via https://web.archive.org/web/20260719095248id_/https://www.cmegroup.com/trading-hours/files/christmas-day-2023.pdf; sha256 edcde0fcf61d3414cee2a332453db861e0e2d7edf81d89a5f379c44b2e72d5cf
  - quote: `PRODUCT NAME MONDAY, 25 DECEMBER 2023 TUESDAY, 26 DECEMBER 2023 ... TRADE DATE: TUES 26 DEC 06:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) 13:30 (CLOSED) GRAINS 14:30 (PCP) 16:00 (CLOSED) TRADE DATE: WED 27 DEC 16:45 (PREOPEN) 19:00 (OPEN)`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on Sunday 2023-12-24 or Monday 2023-12-25; trade date 2023-12-26 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of each asset class); the table's column for each calendar day was read from the pdftotext -layout column positions. The Monday column is empty for GRAINS; CME's ZC service record (captured 2024-07-08) shows no events on 2023-12-24 or 2023-12-25 (extra_evidence). Friday 2023-12-22 has no grain Globex document (gaps; CME's settlement notice says only rates settle early).

### 2024-01-01 New Year's Day (full_closure, -)

- status: https://www.cmegroup.com/trading-hours/files/new-years-day-2024.pdf
  - fetched via https://web.archive.org/web/20260811165716id_/https://www.cmegroup.com/trading-hours/files/new-years-day-2024.pdf; sha256 34e60f8c97623df30e00f0ad8e4eeda20b99001b6c35d64f735828fecec5b9b8
  - quote: `PRODUCT NAME MONDAY, 1 JANUARY 2024 TUESDAY, 2 JANUARY 2024 ... TRADE DATE: TUES 2 JAN 06:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) 13:30 (CLOSED) GRAINS 14:30 (PCP) 16:00 (CLOSED) TRADE DATE: WED 3 JAN 16:45 (PREOPEN) 19:00 (OPEN)`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on Sunday 2023-12-31 or Monday 2024-01-01; trade date 2024-01-02 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of each asset class); the table's column for each calendar day was read from the pdftotext -layout column positions. CME's ZC service record (captured 2024-07-08) shows no events on 2023-12-31 or 2024-01-01 (extra_evidence). Friday 2023-12-29 has no grain Globex document (gaps).

### 2024-01-15 Martin Luther King Jr. Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663
  - fetched via https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-01-14&toEventDate=2024-01-16&isProtected&_t=1720455278663; sha256 e7c5cee8b81efb4ec34a66e9295bb977cc6cd876007689b55a18be0485134fff
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2024-01-14","events":[{"tradingDate":"2024-01-16","eventTime":"16:00","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2024-01-15","events":[{"tradingDate":"2024-01-16","eventTime":"19:00","marketEventType":"open"}]}`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2024-01-15 for trade date 2024-01-16.
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2024-02-19 Presidents Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669
  - fetched via https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-02-18&toEventDate=2024-02-20&isProtected&_t=1720455278669; sha256 07613c57b79dac5dc38a06c88cdaf01eb8182d3b88af8b9c7aa386a0e32b81d9
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2024-02-18","events":[{"tradingDate":"2024-02-20","eventTime":"16:00","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2024-02-19","events":[{"tradingDate":"2024-02-20","eventTime":"19:00","marketEventType":"open"}]}`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2024-02-19 for trade date 2024-02-20.
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2024-03-29 Good Friday (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-03-28&toEventDate=2024-03-30&isProtected&_t=1720455278672
  - fetched via https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-03-28&toEventDate=2024-03-30&isProtected&_t=1720455278672; sha256 451df5abdd31106dcb258fe973e7353928dc44d8009f18b9bc9ed9795241cba7
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2024-03-28","eventTime":"16:00","marketEventType":"closed"}]},{"groupCode":"ZC","eventDate":"2024-03-29","events":[]},{"groupCode":"ZC","eventDate":"2024-03-30","events":[]}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- next session: No grain evening session on 2024-03-28; the retrieved document stops before Sunday 2024-03-31: the regular Sunday 19:00 CT reopen for trade date 2024-04-01 is assumed (not in a source).
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2024-05-27 Memorial Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675
  - fetched via https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-05-26&toEventDate=2024-05-28&isProtected&_t=1720455278675; sha256 842d4a8bd9fced2fe5ff15912d732016bb47b7a2113ede518d5d721ff428cb2d
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2024-05-26","events":[{"tradingDate":"2024-05-28","eventTime":"16:00","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2024-05-27","events":[{"tradingDate":"2024-05-28","eventTime":"19:00","marketEventType":"open"}]}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2024-05-27 for trade date 2024-05-28.
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2024-06-19 Juneteenth (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677
  - fetched via https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-06-18&toEventDate=2024-06-20&isProtected&_t=1720455278677; sha256 a48d61ca544ca2620f2cdc4a3d2232b2c9ff236282879cd4f7d86d66b1adef17
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2024-06-18","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-06-20","eventTime":"16:45","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2024-06-19","events":[{"tradingDate":"2024-06-20","eventTime":"19:00","marketEventType":"open"}]}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- next session: No grain evening session on 2024-06-18; grain Globex reopens 19:00 CT on 2024-06-19 for trade date 2024-06-20.
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2024-07-04 Independence Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680
  - fetched via https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680; sha256 54de3d48c849891d7f37ec1afa38d3e10103c7d606b141a91ad8dec9349e529a
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2024-07-03","eventTime":"16:00","marketEventType":"closed"}]},{"groupCode":"ZC","eventDate":"2024-07-04","events":[]}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- next session: No grain evening session on 2024-07-03 or on 2024-07-04; trade date 2024-07-05 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules). Wednesday 2024-07-03 is a regular grain day (13:20 CT; NO_ENTRY_FINDINGS). data/cme_calendar.py carries 2024-07-04 as an equity full closure that design D10 says must be corrected to a 12:00 CT halt; for grains the full closure is right.

### 2024-09-02 Labor Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1734710019534
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-09-01&toEventDate=2024-09-03&isProtected&_t=1734710019534; sha256 bbe6c78555cba0437fe4b9c6eac0063983ecae49056877db618ed2b29c109546
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2024-09-01","events":[{"tradingDate":"2024-09-03","eventTime":"16:00","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2024-09-02","events":[{"tradingDate":"2024-09-03","eventTime":"19:00","marketEventType":"open"}]}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2024-09-02 for trade date 2024-09-03.
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2024-11-28 Thanksgiving Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535; sha256 e59cbaab0a0a4e62b57226147edd4a5bd8bfee86911eb3a2b4e98b1b0bb12517
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2024-11-27","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-11-29","eventTime":"16:45","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2024-11-28","events":[]}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- next session: No grain evening session on 2024-11-27 or on 2024-11-28; trade date 2024-11-29 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2024-11-29 Day after Thanksgiving (early_halt, 12:05)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535; sha256 e59cbaab0a0a4e62b57226147edd4a5bd8bfee86911eb3a2b4e98b1b0bb12517
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2024-11-28","events":[]},{"groupCode":"ZC","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-11-29","eventTime":"12:05","marketEventType":"closed"}]}`
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535; sha256 e59cbaab0a0a4e62b57226147edd4a5bd8bfee86911eb3a2b4e98b1b0bb12517
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-11-29","eventTime":"12:05","marketEventType":"closed"}]}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- next session: Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not in the record).
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules). The Friday session is the day session only: no Thursday-evening session, open 08:30 CT, close 12:05 CT (CME settles agricultural products at 12:00 CT that day).

### 2024-12-24 Christmas Eve (early_halt, 12:05)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537; sha256 183c85160e31d53fde30c422048b8e778937d8866f3ea1c45e2dd570ea9db1c8
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eventTime":"07:45","marketEventType":"paused"},{"tradingDate":"2024-12-24","eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-12-24","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-12-24","eventTime":"12:05","marketEventType":"closed"}]}`
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537; sha256 183c85160e31d53fde30c422048b8e778937d8866f3ea1c45e2dd570ea9db1c8
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2024-12-24","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-12-24","eventTime":"12:05","marketEventType":"closed"}]}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- next session: No grain evening session (trade date 2024-12-25 is closed).
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules). CME's notice settles agricultural products at 12:00 CT (extra_evidence).

### 2024-12-25 Christmas Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537; sha256 183c85160e31d53fde30c422048b8e778937d8866f3ea1c45e2dd570ea9db1c8
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2024-12-24","eventTime":"12:05","marketEventType":"closed"}]},{"groupCode":"ZC","eventDate":"2024-12-25","events":[]}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- next session: No grain evening session on 2024-12-24 or on 2024-12-25; trade date 2024-12-26 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2025-01-01 New Year's Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1734710019538
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1734710019538; sha256 6b6399a1de34bbc9eea0a135691dfed90edee2a0c705162b1840e214256e4c46
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2024-12-31","eventTime":"16:00","marketEventType":"closed"}]},{"groupCode":"ZC","eventDate":"2025-01-01","events":[]}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- next session: No grain evening session on 2024-12-31 or on 2025-01-01; trade date 2025-01-02 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2025-01-09 National Day of Mourning (Carter) (early_halt, 12:15)

- status: https://www.cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf
  - fetched via https://web.archive.org/web/20250218194143id_/https://www.cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf; sha256 f169d709420a24ebe7f0ab4466ecd8961ea677cb56e9a8fc60fc43dcc9a70ac2
  - quote: `U.S. National Day of Mourning Trading Schedule for Globex, BrokerTec, EBS and Trading Floor ... PRODUCT NAME JANUARY 9, 2025 TRADING FLOOR CLEARPORT ... CME AND CBOT AGS* EARLY CLOSE – 12:15 PM CT N/A NORMAL HOURS`
- time: https://www.cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf
  - fetched via https://web.archive.org/web/20250218194143id_/https://www.cmegroup.com/trading-hours/files/day-of-mourning-january-9-2024.pdf; sha256 f169d709420a24ebe7f0ab4466ecd8961ea677cb56e9a8fc60fc43dcc9a70ac2
  - quote: `CME AND CBOT AGS* EARLY CLOSE – 12:15 PM CT N/A NORMAL HOURS ... *There is no change for products that have an earlier close than 12 PM CT`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- next session: The schedule gives only the early close; the regular 19:00 CT reopen for trade date 2025-01-10 is assumed (not in the source).
- notes: CME's U.S. National Day of Mourning trading schedule (the file name says 2024; the content is dated January 9, 2025). The overnight session of 2025-01-09 (from 19:00 CT on 2025-01-08) is not affected by the schedule's wording. Grains close at 13:20 CT normally, so the footnote's exemption does not apply.

### 2025-01-20 Martin Luther King Jr. Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-01-19&toEventDate=2025-01-21&isProtected&_t=1734710019539; sha256 2cdfb6d5a2bbc1b6b159f5c980d2bf70350c5b181c8d91c3c1023d1eb6a26175
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2025-01-19","events":[{"tradingDate":"2025-01-21","eventTime":"16:00","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2025-01-20","events":[{"tradingDate":"2025-01-21","eventTime":"19:00","marketEventType":"open"}]}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2025-01-20 for trade date 2025-01-21.
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2025-02-17 Presidents Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-02-16&toEventDate=2025-02-18&isProtected&_t=1734710019540; sha256 46119e9af5875c05dee480d7465b431344d0c5bf55492ca1ebb92024a77b5f72
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2025-02-16","events":[{"tradingDate":"2025-02-18","eventTime":"16:00","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2025-02-17","events":[{"tradingDate":"2025-02-18","eventTime":"19:00","marketEventType":"open"}]}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2025-02-17 for trade date 2025-02-18.
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2025-04-18 Good Friday (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-04-17&toEventDate=2025-04-19&isProtected&_t=1734710019542
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-04-17&toEventDate=2025-04-19&isProtected&_t=1734710019542; sha256 c067674b1c10456f5fd86da6db1438b54fa3e352a44662674eb9a9411332edd3
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2025-04-17","eventTime":"16:00","marketEventType":"closed"}]},{"groupCode":"ZC","eventDate":"2025-04-18","events":[]},{"groupCode":"ZC","eventDate":"2025-04-19","events":[]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- next session: No grain evening session on 2025-04-17; the retrieved document stops before Sunday 2025-04-20: the regular Sunday 19:00 CT reopen for trade date 2025-04-21 is assumed (not in a source).
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2025-05-26 Memorial Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-05-25&toEventDate=2025-05-27&isProtected&_t=1734710019543; sha256 73d01c7c3c0cd47c4fb9d6cf14a7c60a1f80d2c81e6a26d42e4c7a1367c94c35
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2025-05-25","events":[{"tradingDate":"2025-05-27","eventTime":"16:00","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2025-05-26","events":[{"tradingDate":"2025-05-27","eventTime":"19:00","marketEventType":"open"}]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2025-05-26 for trade date 2025-05-27.
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2025-06-19 Juneteenth (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-06-18&toEventDate=2025-06-20&isProtected&_t=1734710019544; sha256 7dcceaa759e9888568093eb258a67be0513b443b72acd07dc873a75115854bee
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2025-06-18","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-06-20","eventTime":"16:45","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2025-06-19","events":[{"tradingDate":"2025-06-20","eventTime":"19:00","marketEventType":"open"}]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- next session: No grain evening session on 2025-06-18; grain Globex reopens 19:00 CT on 2025-06-19 for trade date 2025-06-20.
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2025-07-04 Independence Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-07-03&toEventDate=2025-07-05&isProtected&_t=1734710019545; sha256 cd4008266d4387521824839b0b1858ac33bc2326fe3ade74f5f2d756b5d3026f
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2025-07-03","eventTime":"16:00","marketEventType":"closed"}]},{"groupCode":"ZC","eventDate":"2025-07-04","events":[]},{"groupCode":"ZC","eventDate":"2025-07-05","events":[]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- next session: No grain evening session on 2025-07-03; the retrieved document stops before Sunday 2025-07-06: the regular Sunday 19:00 CT reopen for trade date 2025-07-07 is assumed (not in a source).
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules). Thursday 2025-07-03 is a regular grain day (13:20 CT; NO_ENTRY_FINDINGS).

### 2025-09-01 Labor Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-08-31&toEventDate=2025-09-02&isProtected&_t=1734710019546; sha256 dff4ccaf3b18531b37b4ee789d2ca5e686a3c04f6dd1aa5c720b732a6832eeb0
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2025-08-31","events":[{"tradingDate":"2025-09-02","eventTime":"16:00","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2025-09-01","events":[{"tradingDate":"2025-09-02","eventTime":"19:00","marketEventType":"open"}]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2025-09-01 for trade date 2025-09-02.
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2025-11-27 Thanksgiving Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
  - fetched via https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060; sha256 ab8342bd5dbc6dd78f4f6efe599b6448d47a0adffe1bd8baafa5337d49c08062
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2025-11-26","eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-11-28","eventTime":"16:45","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2025-11-27","events":[]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- next session: No grain evening session on 2025-11-26 or on 2025-11-27; trade date 2025-11-28 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2025-11-28 Day after Thanksgiving (early_halt, 12:05)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
  - fetched via https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060; sha256 ab8342bd5dbc6dd78f4f6efe599b6448d47a0adffe1bd8baafa5337d49c08062
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2025-11-27","events":[]},{"groupCode":"ZC","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"12:05","marketEventType":"closed"}]}`
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
  - fetched via https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060; sha256 ab8342bd5dbc6dd78f4f6efe599b6448d47a0adffe1bd8baafa5337d49c08062
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"12:05","marketEventType":"closed"}]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- next session: Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not in the record).
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules). The Friday session is the day session only: no Thursday-evening session, open 08:30 CT, close 12:05 CT (CME settles agricultural products at 12:00 CT that day). The CME Globex outage of 2025-11-27/28 (data-center cooling failure; data/calendars/rates.py LATE_OPENS) fell while grains were already closed: this post-event capture (2026-01-29) adds a 07:00 CT pre-open before the scheduled 08:30 CT open and keeps the 12:05 CT close; the pre-event capture (2024-12-20) has 08:30 open and 12:05 closed only (extra_evidence). No grain entry changes.

### 2025-12-24 Christmas Eve (early_halt, 12:05)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
  - fetched via https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064; sha256 6944a2dd28359cea6a47194c6e74ef9f8808229fd1411482025b962f87290cb2
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eventTime":"07:45","marketEventType":"paused"},{"tradingDate":"2025-12-24","eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-12-24","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-12-24","eventTime":"12:05","marketEventType":"closed"}]}`
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
  - fetched via https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064; sha256 6944a2dd28359cea6a47194c6e74ef9f8808229fd1411482025b962f87290cb2
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2025-12-24","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-12-24","eventTime":"12:05","marketEventType":"closed"}]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- next session: No grain evening session (trade date 2025-12-25 is closed).
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules). CME's notice settles agricultural products at 12:00 CT (extra_evidence).

### 2025-12-25 Christmas Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
  - fetched via https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064; sha256 6944a2dd28359cea6a47194c6e74ef9f8808229fd1411482025b962f87290cb2
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2025-12-24","eventTime":"12:05","marketEventType":"closed"}]},{"groupCode":"ZC","eventDate":"2025-12-25","events":[]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- next session: No grain evening session on 2025-12-24 or on 2025-12-25; trade date 2025-12-26 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2026-01-01 New Year's Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066
  - fetched via https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066; sha256 9eb4ca23526ff7086662f547be2a5702d40f67d7ab21024ff7b3bac9e17e0d19
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2025-12-31","eventTime":"16:00","marketEventType":"closed"}]},{"groupCode":"ZC","eventDate":"2026-01-01","events":[]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- next session: No grain evening session on 2025-12-31 or on 2026-01-01; trade date 2026-01-02 has no overnight segment and opens 08:30 CT (LATE_OPENS).
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2026-01-19 Martin Luther King Jr. Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068
  - fetched via https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20&isProtected&_t=1769649703068; sha256 f8b1f22d11e3465a8b81b94e4f33a9e7cde1b32e35c11ee35965b219c2a55e1d
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2026-01-18","events":[{"tradingDate":"2026-01-20","eventTime":"16:00","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2026-01-19","events":[{"tradingDate":"2026-01-20","eventTime":"19:00","marketEventType":"open"}]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2026-01-19 for trade date 2026-01-20.
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2026-02-16 Presidents Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1743113432015
  - fetched via https://web.archive.org/web/20260610104510id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-02-15&toEventDate=2026-02-17&isProtected&_t=1743113432015; sha256 c1ddc73e2c8af4e695c5f35a49f30c988694d09f31e659f98ca2d232ee942543
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2026-02-15","events":[{"tradingDate":"2026-02-17","eventTime":"16:00","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2026-02-16","events":[{"tradingDate":"2026-02-17","eventTime":"19:00","marketEventType":"open"}]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2026-02-16 for trade date 2026-02-17.
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2026-04-03 Good Friday (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1743113432016
  - fetched via https://web.archive.org/web/20260610104510id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-04-01&toEventDate=2026-04-03&isProtected&_t=1743113432016; sha256 cdba0a6550c433978ef2818881d3f80efd34a5f8b1746bb764457d7c7bb3e5da
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2026-04-02","eventTime":"16:00","marketEventType":"closed"}]},{"groupCode":"ZC","eventDate":"2026-04-03","events":[]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- next session: No grain evening session on 2026-04-02; the retrieved document stops before Sunday 2026-04-05: the regular Sunday 19:00 CT reopen for trade date 2026-04-06 is assumed (not in a source).
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules). Jobs-report Good Friday: equities traded an abbreviated session; grains closed.

### 2026-05-25 Memorial Day (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1749141516014
  - fetched via https://web.archive.org/web/20260619114105id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-05-24&toEventDate=2026-05-26&isProtected&_t=1749141516014; sha256 0abe70f6b4cb1a6ad8022d71993016b4219333a2b6a4fbc44c3a8cdbb4cffdf9
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2026-05-24","events":[{"tradingDate":"2026-05-26","eventTime":"16:00","marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2026-05-25","events":[{"tradingDate":"2026-05-26","eventTime":"19:00","marketEventType":"open"}]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- next session: No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex reopens 19:00 CT on 2026-05-25 for trade date 2026-05-26.
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2026-06-19 Juneteenth (full_closure, -)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-18&toEventDate=2026-06-20&isProtected&_t=1784720540600
  - fetched via https://web.archive.org/web/20260722114220id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2026-06-18&toEventDate=2026-06-20&isProtected&_t=1784720540600; sha256 8443ca95be51e95f953be29b713a9b996f298015f692e3d6706be8201f430bb2
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"tradingDate":"2026-06-18","eventTime":"16:00","marketEventType":"closed"}]},{"groupCode":"ZC","eventDate":"2026-06-19","events":[]},{"groupCode":"ZC","eventDate":"2026-06-20","events":[]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- next session: No grain evening session on 2026-06-18; the next session (Sunday 2026-06-21 19:00 CT) lies outside the coverage.
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2019-07-05 Day after Independence Day (late_open, 08:30)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-independence-day-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Updated 6/6/2019|CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019 ... Trade Date|Wednesday, July 3||Friday, July 5 ... Calendar Date|Wednesday, July 3||||||||Thursday, July 4||||||||Friday, July 5 ... All times are Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|||| ... Grains and Oilseeds ||12:05:00 PM|12:30 - 16:00| |||||Markets Closed||||||||06:00:00 AM|08:30:00 AM`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-independence-day-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Calendar Date|Wednesday, July 3||||||||Thursday, July 4||||||||Friday, July 5 ... All times are Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|||| ... Grains and Oilseeds ||12:05:00 PM|12:30 - 16:00| |||||Markets Closed||||||||06:00:00 AM|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). Friday July 5: Pre-opening 06:00, Open 08:30 (no Thursday-evening session).

### 2019-11-29 Day after Thanksgiving (late_open, 08:30)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-thanksgiving-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Updated 10/07/2019|CME Group Globex Thanksgiving Holiday Schedule: November 27, 2019 - November 29, 2019 ... Trade Date|Wednesday, November 27||Friday, November 29 ... Calendar Date|Wednesday, November 27|||||||Thursday, November 28|||||||||Friday, November 29 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-thanksgiving-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Calendar Date|Wednesday, November 27|||||||Thursday, November 28|||||||||Friday, November 29 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). Pre-opening 16:45 on Wednesday for trade date Friday; Friday Open 08:30.

### 2019-12-26 Day after Christmas (late_open, 08:30)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-christmas-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Updated 10/01/2019|CME Group Globex Christmas Holiday Schedule: December 24, 2019 - December 26, 2019 ... Trade Date|Tuesday, December 24|Globex Closed|Thursday, December 26 ... Calendar Date|Tuesday, December 24|Wednesday, December 25|Wednesday, December 25||||||Thursday, December 26 ... All times are Central Time ET +1 UTC +6|Close|| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|||||||06:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-christmas-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Calendar Date|Tuesday, December 24|Wednesday, December 25|Wednesday, December 25||||||Thursday, December 26 ... All times are Central Time ET +1 UTC +6|Close|| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|||||||06:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). Thursday December 26: Pre-opening 06:00, Open 08:30.

### 2020-01-02 Day after New Year's Day (late_open, 08:30)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-2020-new-years-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Updated 10/01/2019|CME Group Globex New Years Holiday Schedule: December 31, 2019 - January 2, 2020 ... Trade Date|Tuesday, December 31||Thursday, January 2 ... Calendar Date|Tuesday, December 31|Wednesday, January 1|Wednesday, January 1||||||Thursday, Jan 2 ... All times are Central Time ET +1 UTC +6| Close|| Pre-opening**|Open|Pre-opening**|halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP*|||||| ... Grains and Oilseeds |13:20 PCP: 14:30-16:00|Globex Closed|||||||06:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip (member globex-trading-schedules/2019-2020-new-years-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20210126094837id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip; sha256 1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05
  - quote: `Calendar Date|Tuesday, December 31|Wednesday, January 1|Wednesday, January 1||||||Thursday, Jan 2 ... All times are Central Time ET +1 UTC +6| Close|| Pre-opening**|Open|Pre-opening**|halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP*|||||| ... Grains and Oilseeds |13:20 PCP: 14:30-16:00|Globex Closed|||||||06:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). Thursday January 2: Pre-opening 06:00, Open 08:30.

### 2020-11-27 Day after Thanksgiving (late_open, 08:30)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-thanksgiving-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Updated 10/13/2020|CME Group Globex Thanksgiving Holiday Schedule: November 25, 2020 - November 27, 2020 ... Trade Date|Wednesday, November 25||Friday, November 27 ... Calendar Date|Wednesday, November 25|||||||Thursday, November 26|||||||||Friday, November 27 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip (member 2020-thanksgiving-schedule.xls)
  - fetched via https://web.archive.org/web/20260730111834id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-holiday-calendars.zip; sha256 5263a4a5e9076bc0e69c7cd0e3fd9f82dc4d80b66f1b56f14070f08c1d762b59
  - quote: `Calendar Date|Wednesday, November 25|||||||Thursday, November 26|||||||||Friday, November 27 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2021-07-06 Day after Independence Day (observed) (late_open, 08:30)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip (member 2021-independence-day-holiday-schedule-compact.xls)
  - fetched via https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip; sha256 0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59
  - quote: `|CME Group Globex Independence Day Holiday Schedule: July 2, 2021 to July 6, 2021 ... Trade Date|Friday, July 2|Tuesday, July 6 ... Calendar Date|Friday July 2|Sunday July 4|Monday July 5|Monday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... Grain & Oilseed |Regular Per Product|Markets Closed|Markets Closed|Tuesday July 6 Regular @ 0830 CT / 1330 UTC`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip (member 2021-independence-day-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip; sha256 0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59
  - quote: `Calendar Date|Friday, July 2||Sunday, July 4|||||Monday, July 5||||||Tuesday, July 6 ... All times are Central Time ET +1 UTC +5|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|||||| ... Grains and Oilseeds |01:20:00 PM|14:30 - 16:00| |||||||||||06:00:00 AM|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- notes: Compact schedule: 'Tuesday July 6 Regular @ 0830 CT'; full schedule: Tuesday Pre-opening 06:00, Open 08:30.

### 2021-11-26 Day after Thanksgiving (late_open, 08:30)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip (member 2021-thanksgiving-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip; sha256 0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59
  - quote: `Updated 11/23/2021|CME Group Globex Thanksgiving Holiday Schedule: November 24, 2021 - November 26, 2021 ... Trade Date|Wednesday, November 24||Friday, November 26 ... Calendar Date|Wednesday, November 24|||||||Thursday, November 25|||||||||Friday, November 26 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip (member 2021-thanksgiving-holiday-schedule.xls)
  - fetched via https://web.archive.org/web/20260830100327id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-holiday-calendars.zip; sha256 0ee0860a3a0e035eb9d079419aca3cafcc4256d296fa916647987c396dda8c59
  - quote: `Calendar Date|Wednesday, November 24|||||||Thursday, November 25|||||||||Friday, November 26 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2022-07-05 Day after Independence Day (late_open, 08:30)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls
  - fetched via https://web.archive.org/web/20220704065431id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls; sha256 11925e2a7c434e05e2e3b74df1e677cd0657629370e735a11f821871e0e91e06
  - quote: `|CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022 ... Trade Date|Friday, July 1|Tuesday, July 5 ... Calendar Date|Friday July 1|Sunday July 3|Monday July 4|Monday July 4 ... Product|CLOSE|OPEN|HALT|OPEN ... Grain & Oilseed |Regular Per Product|Markets Closed|Markets Closed|Tuesday July 5 Regular @ 0830 CT / 1330 UTC`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls
  - fetched via https://web.archive.org/web/20220704065450id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls; sha256 1ea0459d8aa0fd7ec5147614855f6d0d43607efefdc3aa9c6b1e18ddbfd54fde
  - quote: `Calendar Date|Friday, July 1|||||Sunday, July 3|||||Monday, July 4|||||||||||Tuesday, July 5 ... All times are Central Time ET +1 UTC +5|Regular Close|PCP*| Pre-opening**|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|||||| ... Grains and Oilseeds |01:20:00 PM|14:30 - 16:00|||| ||||||||||||||||06:00:00 AM|08:30:00 AM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- notes: Compact schedule: 'Tuesday July 5 Regular @ 0830 CT'; full schedule: Tuesday Pre-opening 06:00, Open 08:30.

### 2022-11-25 Day after Thanksgiving (late_open, 08:30)

- status: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls
  - fetched via https://web.archive.org/web/20220704065423id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls; sha256 767da53e71854a3b293b613d256642f8155cd04997fa0825a35825440448126c
  - quote: `Updated 6/29/2022|CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, 2022 ... Trade Date|Wednesday, November 23|||||Friday, November 25 ... Calendar Date|Wednesday, November 23||||||||||Thursday, November 24||||||||||||Friday, November 25 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00||||04:45:00 PM||||||||||||||||||08:30:00 AM|12:05:00 PM`
- time: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls
  - fetched via https://web.archive.org/web/20220704065423id_/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-thanksgiving-holiday-schedule.xls; sha256 767da53e71854a3b293b613d256642f8155cd04997fa0825a35825440448126c
  - quote: `Calendar Date|Wednesday, November 23||||||||||Thursday, November 24||||||||||||Friday, November 25 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|14:30-16:00||||04:45:00 PM||||||||||||||||||08:30:00 AM|12:05:00 PM`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- notes: CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it).

### 2023-07-05 Day after Independence Day (late_open, 08:30)

- status: https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf
  - fetched via https://web.archive.org/web/20230627125057id_/https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf; sha256 ccbc1f1fc39ba2219fd748372faa985798fee7eaffabf69f08956f5465a769e3
  - quote: `PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... TRADE DATE: WED 5 JULY TRADE DATE: MON 3 JULY 06:00 (PREOPEN) 07:45 (PAUSED) 08:30 (OPEN)`
- time: https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf
  - fetched via https://web.archive.org/web/20230627125057id_/https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf; sha256 ccbc1f1fc39ba2219fd748372faa985798fee7eaffabf69f08956f5465a769e3
  - quote: `TRADE DATE: WED 5 JULY TRADE DATE: MON 3 JULY 06:00 (PREOPEN) 07:45 (PAUSED) 08:30 (OPEN)`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- notes: CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of each asset class); the table's column for each calendar day was read from the pdftotext -layout column positions. Wednesday column: TRADE DATE WED 5 JULY 06:00 PREOPEN, 08:30 OPEN (the 07:45 PAUSED between them belongs to the Monday column).

### 2023-11-24 Day after Thanksgiving (late_open, 08:30)

- status: https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf
  - fetched via https://web.archive.org/web/20231203205929id_/https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf; sha256 99e187b3f3899e1062d662e148d5978e0cd075b961e6fc79550d4393812307e8
  - quote: `PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 NOVEMBER 2023 ... TRADE DATE: FRI 24 NOV GRAINS 13:30 (CLOSED) 08:30 (OPEN)`
- time: https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf
  - fetched via https://web.archive.org/web/20231203205929id_/https://www.cmegroup.com/trading-hours/files/thanksgiving-day-2023.pdf; sha256 99e187b3f3899e1062d662e148d5978e0cd075b961e6fc79550d4393812307e8
  - quote: `TRADE DATE: FRI 24 NOV GRAINS 13:30 (CLOSED) 08:30 (OPEN)`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- notes: CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of each asset class); the table's column for each calendar day was read from the pdftotext -layout column positions.

### 2023-12-26 Day after Christmas (late_open, 08:30)

- status: https://www.cmegroup.com/trading-hours/files/christmas-day-2023.pdf
  - fetched via https://web.archive.org/web/20260719095248id_/https://www.cmegroup.com/trading-hours/files/christmas-day-2023.pdf; sha256 edcde0fcf61d3414cee2a332453db861e0e2d7edf81d89a5f379c44b2e72d5cf
  - quote: `PRODUCT NAME MONDAY, 25 DECEMBER 2023 TUESDAY, 26 DECEMBER 2023 ... TRADE DATE: TUES 26 DEC 06:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) 13:30 (CLOSED) GRAINS`
- time: https://www.cmegroup.com/trading-hours/files/christmas-day-2023.pdf
  - fetched via https://web.archive.org/web/20260719095248id_/https://www.cmegroup.com/trading-hours/files/christmas-day-2023.pdf; sha256 edcde0fcf61d3414cee2a332453db861e0e2d7edf81d89a5f379c44b2e72d5cf
  - quote: `TRADE DATE: TUES 26 DEC 06:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) 13:30 (CLOSED) GRAINS`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- notes: CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of each asset class); the table's column for each calendar day was read from the pdftotext -layout column positions.

### 2024-01-02 Day after New Year's Day (late_open, 08:30)

- status: https://www.cmegroup.com/trading-hours/files/new-years-day-2024.pdf
  - fetched via https://web.archive.org/web/20260811165716id_/https://www.cmegroup.com/trading-hours/files/new-years-day-2024.pdf; sha256 34e60f8c97623df30e00f0ad8e4eeda20b99001b6c35d64f735828fecec5b9b8
  - quote: `PRODUCT NAME MONDAY, 1 JANUARY 2024 TUESDAY, 2 JANUARY 2024 ... TRADE DATE: TUES 2 JAN 06:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) 13:30 (CLOSED) GRAINS`
- time: https://www.cmegroup.com/trading-hours/files/new-years-day-2024.pdf
  - fetched via https://web.archive.org/web/20260811165716id_/https://www.cmegroup.com/trading-hours/files/new-years-day-2024.pdf; sha256 34e60f8c97623df30e00f0ad8e4eeda20b99001b6c35d64f735828fecec5b9b8
  - quote: `TRADE DATE: TUES 2 JAN 06:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) 13:30 (CLOSED) GRAINS`
- verbatim_check: True; bar_check_status: validated against CME schedules only, bar check pending the step 2 purchase
- notes: CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of each asset class); the table's column for each calendar day was read from the pdftotext -layout column positions.

### 2024-07-05 Day after Independence Day (late_open, 08:30)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680
  - fetched via https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680; sha256 54de3d48c849891d7f37ec1afa38d3e10103c7d606b141a91ad8dec9349e529a
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2024-07-04","events":[]},{"groupCode":"ZC","eventDate":"2024-07-05","events":[{"tradingDate":"2024-07-05","eventTime":"06:00","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"08:30","marketEventType":"open"}`
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680
  - fetched via https://web.archive.org/web/20240708161439id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680; sha256 54de3d48c849891d7f37ec1afa38d3e10103c7d606b141a91ad8dec9349e529a
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2024-07-05","events":[{"tradingDate":"2024-07-05","eventTime":"06:00","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"08:30","marketEventType":"open"}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2024-11-29 Day after Thanksgiving (late_open, 08:30)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535; sha256 e59cbaab0a0a4e62b57226147edd4a5bd8bfee86911eb3a2b4e98b1b0bb12517
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2024-11-28","events":[]},{"groupCode":"ZC","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-11-29","eventTime":"12:05","marketEventType":"closed"}]}`
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-11-27&toEventDate=2024-11-29&isProtected&_t=1734710019535; sha256 e59cbaab0a0a4e62b57226147edd4a5bd8bfee86911eb3a2b4e98b1b0bb12517
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-11-29","eventTime":"12:05","marketEventType":"closed"}]}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2024-12-26 Day after Christmas (late_open, 08:30)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537; sha256 183c85160e31d53fde30c422048b8e778937d8866f3ea1c45e2dd570ea9db1c8
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2024-12-25","events":[]},{"groupCode":"ZC","eventDate":"2024-12-26","events":[{"tradingDate":"2024-12-26","eventTime":"06:00","marketEventType":"preopen"},{"tradingDate":"2024-12-26","eventTime":"08:30","marketEventType":"open"}`
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-24&toEventDate=2024-12-26&isProtected&_t=1734710019537; sha256 183c85160e31d53fde30c422048b8e778937d8866f3ea1c45e2dd570ea9db1c8
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2024-12-26","events":[{"tradingDate":"2024-12-26","eventTime":"06:00","marketEventType":"preopen"},{"tradingDate":"2024-12-26","eventTime":"08:30","marketEventType":"open"}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2025-01-02 Day after New Year's Day (late_open, 08:30)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1734710019538
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1734710019538; sha256 6b6399a1de34bbc9eea0a135691dfed90edee2a0c705162b1840e214256e4c46
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2025-01-01","events":[]},{"groupCode":"ZC","eventDate":"2025-01-02","events":[{"tradingDate":"2025-01-02","eventTime":"06:00","marketEventType":"preopen"},{"tradingDate":"2025-01-02","eventTime":"08:30","marketEventType":"open"}`
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1734710019538
  - fetched via https://web.archive.org/web/20241220155340id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-12-31&toEventDate=2025-01-02&isProtected&_t=1734710019538; sha256 6b6399a1de34bbc9eea0a135691dfed90edee2a0c705162b1840e214256e4c46
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2025-01-02","events":[{"tradingDate":"2025-01-02","eventTime":"06:00","marketEventType":"preopen"},{"tradingDate":"2025-01-02","eventTime":"08:30","marketEventType":"open"}`
- verbatim_check: True; bar_check_status: validated against CME schedules only; embargo or holdout-2 date, never checked against bars
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2025-11-28 Day after Thanksgiving (late_open, 08:30)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
  - fetched via https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060; sha256 ab8342bd5dbc6dd78f4f6efe599b6448d47a0adffe1bd8baafa5337d49c08062
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2025-11-27","events":[]},{"groupCode":"ZC","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"12:05","marketEventType":"closed"}]}`
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060
  - fetched via https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060; sha256 ab8342bd5dbc6dd78f4f6efe599b6448d47a0adffe1bd8baafa5337d49c08062
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"12:05","marketEventType":"closed"}]}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules). The 07:00 CT pre-open in this post-event record follows the 2025-11-27/28 CME Globex outage; the 08:30 CT open is the scheduled one.

### 2025-12-26 Day after Christmas (late_open, 08:30)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
  - fetched via https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064; sha256 6944a2dd28359cea6a47194c6e74ef9f8808229fd1411482025b962f87290cb2
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2025-12-25","events":[]},{"groupCode":"ZC","eventDate":"2025-12-26","events":[{"tradingDate":"2025-12-26","eventTime":"06:00","marketEventType":"preopen"},{"tradingDate":"2025-12-26","eventTime":"08:30","marketEventType":"open"}`
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064
  - fetched via https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-24&toEventDate=2025-12-26&isProtected&_t=1769649703064; sha256 6944a2dd28359cea6a47194c6e74ef9f8808229fd1411482025b962f87290cb2
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2025-12-26","events":[{"tradingDate":"2025-12-26","eventTime":"06:00","marketEventType":"preopen"},{"tradingDate":"2025-12-26","eventTime":"08:30","marketEventType":"open"}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).

### 2026-01-02 Day after New Year's Day (late_open, 08:30)

- status: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066
  - fetched via https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066; sha256 9eb4ca23526ff7086662f547be2a5702d40f67d7ab21024ff7b3bac9e17e0d19
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2026-01-01","events":[]},{"groupCode":"ZC","eventDate":"2026-01-02","events":[{"tradingDate":"2026-01-02","eventTime":"06:00","marketEventType":"preopen"},{"tradingDate":"2026-01-02","eventTime":"08:30","marketEventType":"open"}`
- time: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066
  - fetched via https://web.archive.org/web/20260129012143id_/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-12-31&toEventDate=2026-01-02&isProtected&_t=1769649703066; sha256 9eb4ca23526ff7086662f547be2a5702d40f67d7ab21024ff7b3bac9e17e0d19
  - quote: `"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC","eventDate":"2026-01-02","events":[{"tradingDate":"2026-01-02","eventTime":"06:00","marketEventType":"preopen"},{"tradingDate":"2026-01-02","eventTime":"08:30","marketEventType":"open"}`
- verbatim_check: True; bar_check_status: pending Task 7 (research-window bars)
- notes: CME's trading-hours service record for Corn (ZC, product id 300), the most active grain contract; CME states the grain holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules).
