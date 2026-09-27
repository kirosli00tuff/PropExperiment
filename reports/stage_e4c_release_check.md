# Stage E.4 Part 3 (K3), Task 1b: release check (clocks, calendars, index histories)

Worker ReleaseChecker-OpusMed, 2026-09-27 (PDT). Extraction and checks only; no member event set decided. Full data: reports/stage_e4c_release_check.json. Build script: session scratchpad build_e4c.py (not in repo).

## Counts

- EC-EW (England and Wales) holidays 2019-04-01..2026-06-30: 63
- EC-TGT rows: 54 (6 per year 2019-2026; 2021 listed twice, from two sources that agree)
- EC-JP CAO holidays 2019-2026: 148
- Tokyo business days per year: {'2019': 241, '2020': 243, '2021': 245, '2022': 244, '2023': 246, '2024': 245, '2025': 243, '2026': 242}
- Gotobi dates in 2019-04-01..2026-06-19: 350; Tokyo month-ends 2019-04..2026-06: 87
- ME(m) months 2019-04..2026-06: 87

## Clocks (zoneinfo) and known-answer tests

T_L: CT times seen ['10:00', '11:00']; 145 weekdays at 11:00 CT in 2019-2026. Computed ranges through 2026-06-30 equal C9's list: **True** (diff {'only_computed': [], 'only_c9': []}). After the window: ['2026-10-26..2026-10-30'].

| clock | date | expected | computed | pass |
|---|---|---|---|---|
| T_L | 2025-03-10 | 11:00 | 11:00 | True |
| T_L | 2025-03-31 | 10:00 | 10:00 | True |
| T_L | 2025-10-27 | 11:00 | 11:00 | True |
| T_L | 2025-11-03 | 10:00 | 10:00 | True |
| T_L | 2021-11-01 | 11:00 | 11:00 | True |
| T_L | 2021-11-02 | 11:00 | 11:00 | True |
| T_L | 2021-11-03 | 11:00 | 11:00 | True |
| T_L | 2021-11-04 | 11:00 | 11:00 | True |
| T_L | 2021-11-05 | 11:00 | 11:00 | True |
| T_E | 2025-03-10 | 08:15 | 08:15 | True |
| T_E | 2025-04-01 | 07:15 | 07:15 | True |
| T_T | 2025-11-04 | 2025-11-03 18:55 CT | 2025-11-03 18:55 CST | True |
| T_T | 2025-01-10 | 2025-01-09 18:55 CST | 2025-01-09 18:55 CST | True |
| T_T | 2025-03-10 | 2025-03-09 19:55 CDT | 2025-03-09 19:55 CDT | True |
| T_T | 2025-07-10 | 2025-07-09 19:55 CDT | 2025-07-09 19:55 CDT | True |

T_E: CT times ['07:15', '08:15']; 08:15 weekdays (145) fall in exactly the T_L 11:00 weeks: True. T_T: always on CT day d-1: True; CT times ['18:55', '19:55']. (The last three T_T rows are C9's computed examples.)

T_L 11:00 CT weekday ranges by year:

- 2019: 2019-03-11..2019-03-29, 2019-10-28..2019-11-01
- 2020: 2020-03-09..2020-03-27, 2020-10-26..2020-10-30
- 2021: 2021-03-15..2021-03-26, 2021-11-01..2021-11-05
- 2022: 2022-03-14..2022-03-25, 2022-10-31..2022-11-04
- 2023: 2023-03-13..2023-03-24, 2023-10-30..2023-11-03
- 2024: 2024-03-11..2024-03-29, 2024-10-28..2024-11-01
- 2025: 2025-03-10..2025-03-28, 2025-10-27..2025-10-31
- 2026: 2026-03-09..2026-03-27, 2026-10-26..2026-10-30

## EC-TGT, TARGET closing days

| year | dates | source (capture) |
|---|---|---|
| 2019 | 01-01, 04-19, 04-22, 05-01, 12-25, 12-26 | 20181217075419: https://web.archive.org/web/20181217075419id_/https://www.ecb.europa.eu/paym/target/target2/profuse/calendar/html/index.en.html |
| 2020 | 01-01, 04-10, 04-13, 05-01, 12-25, 12-26 | 20191226084555: https://web.archive.org/web/20191226084555id_/https://www.ecb.europa.eu/paym/target/target2/profuse/calendar/html/index.en.html |
| 2021 | 01-01, 04-02, 04-05, 05-01, 12-25, 12-26 | 20201125150220: https://web.archive.org/web/20201125150220id_/https://www.ecb.europa.eu/paym/target/target2/profuse/calendar/html/index.en.html |
| 2021 | 01-01, 04-02, 04-05, 05-01, 12-25, 12-26 | 20210508192900: https://web.archive.org/web/20210508192900id_/https://www.ecb.europa.eu/services/contacts/working-hours/html/index.en.html |
| 2022 | 01-01, 04-15, 04-18, 05-01, 12-25, 12-26 | 20211214193232: https://web.archive.org/web/20211214193232id_/https://www.ecb.europa.eu/services/contacts/working-hours/html/index.en.html |
| 2023 | 01-01, 04-07, 04-10, 05-01, 12-25, 12-26 | 20221217181447: https://web.archive.org/web/20221217181447id_/https://www.ecb.europa.eu/services/contacts/working-hours/html/index.en.html |
| 2024 | 01-01, 03-29, 04-01, 05-01, 12-25, 12-26 | 20231228195814: https://web.archive.org/web/20231228195814id_/https://www.ecb.europa.eu/services/contacts/working-hours/html/index.en.html |
| 2025 | 01-01, 04-18, 04-21, 05-01, 12-25, 12-26 | 20241230111431: https://web.archive.org/web/20241230111431id_/https://www.ecb.europa.eu/ecb/contacts/working-hours/html/index.en.html |
| 2026 | 01-01, 04-03, 04-06, 05-01, 12-25, 12-26 | 20251218035041: https://web.archive.org/web/20251218035041id_/https://www.ecb.europa.eu/ecb/contacts/working-hours/html/index.en.html |

Notes: 2021: the earliest working-hours capture (2021-05-08) is dated after 1 Jan 2021; the TARGET2-calendar capture of 2020-11-25 (rule text) is dated before it. Both listed. 2026 live page starred set equals 2025-12-18 capture's: True Every parsed capture was compared with the six-day rule (1 Jan, Good Friday, Easter Monday, 1 May, 25 and 26 Dec) for every year it lists: no differences. Captures parsed: 20210508192900, 20211214193232, 20221202003032, 20221208180732, 20221211011442, 20221217181447, 20231228195814, 20241230111431, 20251218035041, live. The page lists more ECB holidays; only starred ones (TARGET closing) are kept.

## Tokyo year-end finding

Checked against MUFG Research and Consulting's yearly TTM files (murc-kawasesouba.jp/fx/xls/murc_YYYY.xls, 2019-2026; USD TTM column). Over 2019-01-01..2026-08-31: 1868 dates carry a USD TTM; the EC-JP rule gives 1868 Tokyo business days. Dates with a TTM that the rule excludes: none. Rule business days without a TTM: none. So the 31 Dec-3 Jan closure rule matches the MUFG publication record exactly for every year-end in the span. MUFG's TTM is the Tokyo bank's own 9:55 rate, a free record of fix days (not the WM/R or any other benchmark).

| year-end | weekdays 28 Dec-6 Jan: TTM published? |
|---|---|
| 2019/2020 | 12-30=1, 12-31=0, 01-01=0, 01-02=0, 01-03=0, 01-06=1 |
| 2020/2021 | 12-28=1, 12-29=1, 12-30=1, 12-31=0, 01-01=0, 01-04=1, 01-05=1, 01-06=1 |
| 2021/2022 | 12-28=1, 12-29=1, 12-30=1, 12-31=0, 01-03=0, 01-04=1, 01-05=1, 01-06=1 |
| 2022/2023 | 12-28=1, 12-29=1, 12-30=1, 01-02=0, 01-03=0, 01-04=1, 01-05=1, 01-06=1 |
| 2023/2024 | 12-28=1, 12-29=1, 01-01=0, 01-02=0, 01-03=0, 01-04=1, 01-05=1 |
| 2024/2025 | 12-30=1, 12-31=0, 01-01=0, 01-02=0, 01-03=0, 01-06=1 |
| 2025/2026 | 12-29=1, 12-30=1, 12-31=0, 01-01=0, 01-02=0, 01-05=1, 01-06=1 |

## ME(m) and the EC-EW drop

Month-ends that are EC-EW bank holidays (C9 drops these):

- 2020-08: ME 2020-08-31
- 2021-05: ME 2021-05-31 (EC-CAL early halt 12:00:00 CT)

In the research window (2025-04..2026-06): 0 dropped, as C9 expects. Month-ends with an EC-CAL early halt (information only): 2019-11-29 (12:15:00), 2021-05-31 (12:00:00), 2024-11-29 (13:45:00), 2025-11-28 (13:45:00). Outside EC-CAL coverage (last weekday listed instead): 2019-04-30, 2026-06-30.

## Index histories (K3-mehedge-01)

**N225: obtained = True.** Publisher Nikkei Inc. https://indexes.nikkei.co.jp/nkave/historical/nikkei_stock_average_daily_en.csv (live) plus 3 Wayback captures of the same file. In 2019-04-01..2026-06-19: n=1761, first 2019-04-01, last 2026-06-19. Checked against EC-JP Tokyo business days: missing dates none; non-trading dates with a value none; overlap conflicts between pieces: 0. FRED NIKKEI225 spot check (15 dates incl. 6 FRED-blank holidays): all equal = True (FRED scrape not saved; see unverified).

| piece | capture | first | last | n | sha256 |
|---|---|---|---|---|---|
| data/vendor/index_history/nikkei_stock_average_daily_en.csv | live 2026-09-27 | 2023-01-04 | 2026-09-25 | 911 | 417292006e50f23a |
| data/vendor/index_history/nikkei_wayback/wb_20200919105418_nikkei_daily_en.csv | 20200919105418 | 2017-01-04 | 2020-09-18 | 907 | 17df976527e693d9 |
| data/vendor/index_history/nikkei_wayback/wb_20230523124334_nikkei_daily_en.csv | 20230523124334 | 2020-01-06 | 2023-05-23 | 826 | c9e29268c8bfbdc3 |
| data/vendor/index_history/nikkei_wayback/wb_20240401064221_nikkei_daily_en.csv | 20240401064221 | 2021-01-04 | 2024-03-29 | 793 | 203e775e94d8c950 |

**SX5E: obtained = False.** the free file h_3msx5e.txt holds a rolling ~3-month window only; the full-history file h_sx5e.txt redirects to a login page (302 -> /c/portal/login); 19 Wayback captures leave gaps. The union of the live file and 17 captures covers 960 dates in the window (2019-07-23..2025-06-17); against weekdays minus EC-TGT days, 889 dates are missing (257 in the research window), non-trading date with a value: ['2025-05-01']. Per the entry's E.2 rule this exposure's trial is to be dropped; that decision is the lead's.

Missing ranges: 2019-04-01..2019-04-18, 2019-04-23..2019-04-30, 2019-05-02..2019-07-22, 2019-12-16..2019-12-24, 2019-12-27..2019-12-31, 2020-01-02..2020-04-09, 2020-04-14..2020-04-30, 2020-05-04..2020-06-19, 2020-11-26..2020-12-01, 2021-10-18..2021-10-19, 2022-01-20..2022-04-01, 2022-07-04..2022-09-01, 2022-12-02..2022-12-16, 2023-03-23..2023-04-06, 2023-04-11..2023-04-28, 2023-05-02..2023-06-21, 2023-09-22..2023-11-30, 2024-03-01..2024-03-28, 2024-04-02..2024-04-30, 2024-05-02..2024-05-02, 2024-08-05..2024-12-24, 2024-12-27..2024-12-31, 2025-01-02..2025-03-17, 2025-06-18..2025-12-24, 2025-12-29..2025-12-31, 2026-01-02..2026-04-02, 2026-04-07..2026-04-30, 2026-05-04..2026-06-19

| piece | capture | first | last | n |
|---|---|---|---|---|
| data/vendor/index_history/stoxx_h_3msx5e.txt | live 2026-09-27 | 2026-06-26 | 2026-09-25 | 66 |
| data/vendor/index_history/stoxx_wayback/wb_20191022234639_h_3msx5e.txt | 20191022234639 | 2019-07-23 | 2019-10-22 | 66 |
| data/vendor/index_history/stoxx_wayback/wb_20191216123719_h_3msx5e.txt | 20191216123719 | 2019-09-16 | 2019-12-13 | 65 |
| data/vendor/index_history/stoxx_wayback/wb_20200922130558_h_3msx5e.txt | 20200922130558 | 2020-06-22 | 2020-09-21 | 66 |
| data/vendor/index_history/stoxx_wayback/wb_20201126090521_h_3msx5e.txt | 20201126090521 | 2020-08-26 | 2020-11-25 | 66 |
| data/vendor/index_history/stoxx_wayback/wb_20210302035628_h_3msx5e.txt | 20210302035628 | 2020-12-02 | 2021-03-01 | 62 |
| data/vendor/index_history/stoxx_wayback/wb_20210508213359_h_3msx5e.txt | 20210508213359 | 2021-02-08 | 2021-05-07 | 63 |
| data/vendor/index_history/stoxx_wayback/wb_20210802142409_h_3msx5e.txt | 20210802142409 | 2021-05-03 | 2021-07-30 | 65 |
| data/vendor/index_history/stoxx_wayback/wb_20211018161016_h_3msx5e.txt | 20211018161016 | 2021-07-16 | 2021-10-15 | 66 |
| data/vendor/index_history/stoxx_wayback/wb_20220120101102_h_3msx5e.txt | 20220120101102 | 2021-10-20 | 2022-01-19 | 66 |
| data/vendor/index_history/stoxx_wayback/wb_20220703170543_h_3msx5e.txt | 20220703170543 | 2022-04-04 | 2022-07-01 | 63 |
| data/vendor/index_history/stoxx_wayback/wb_20221201222410_h_3msx5e.txt | 20221201222410 | 2022-09-02 | 2022-12-01 | 65 |
| data/vendor/index_history/stoxx_wayback/wb_20230320145915_h_3msx5e.txt | 20230320145915 | 2022-12-19 | 2023-03-17 | 64 |
| data/vendor/index_history/stoxx_wayback/wb_20230323180450_h_3msx5e.txt | 20230323180450 | 2022-12-23 | 2023-03-22 | 63 |
| data/vendor/index_history/stoxx_wayback/wb_20230922135959_h_3msx5e.txt | 20230922135959 | 2023-06-22 | 2023-09-21 | 66 |
| data/vendor/index_history/stoxx_wayback/wb_20240301063723_h_3msx5e.txt | 20240301063723 | 2023-12-01 | 2024-02-29 | 62 |
| data/vendor/index_history/stoxx_wayback/wb_20240803103348_h_3msx5e.txt | 20240803103348 | 2024-05-03 | 2024-08-02 | 66 |
| data/vendor/index_history/stoxx_wayback/wb_20250618030042_h_3msx5e.txt | 20250618030042 | 2025-03-18 | 2025-06-17 | 64 |

## Sources

- https://www.gov.uk/bank-holidays.json -> data/vendor/release_pages/e4b/govuk_bank-holidays.json (sha256 538b3482c28b85ec) reused from e4b (fetched 2026-09-27 05:03 PDT)
- https://web.archive.org/web/20181217075419id_/https://www.ecb.europa.eu/paym/target/target2/profuse/calendar/html/index.en.html -> data/vendor/release_pages/e4c/wb_20181217075419_ecb_target2_calendar.html (sha256 38f73bec561f0768) Wayback capture 20181217075419 of the TARGET2 calendar page (rule text, used for 2019)
- https://web.archive.org/web/20191226084555id_/https://www.ecb.europa.eu/paym/target/target2/profuse/calendar/html/index.en.html -> data/vendor/release_pages/e4c/wb_20191226084555_ecb_target2_calendar.html (sha256 48771bb5c81705ca) Wayback capture 20191226084555 of the TARGET2 calendar page (rule text, used for 2020)
- https://web.archive.org/web/20201125150220id_/https://www.ecb.europa.eu/paym/target/target2/profuse/calendar/html/index.en.html -> data/vendor/release_pages/e4c/wb_20201125150220_ecb_target2_calendar.html (sha256 83e75cd969175866) Wayback capture 20201125150220 of the TARGET2 calendar page (rule text, used for 2021)
- https://web.archive.org/web/20210508192900id_/https://www.ecb.europa.eu/services/contacts/working-hours/html/index.en.html -> data/vendor/release_pages/e4c/wb_20210508192900_ecb_working_hours.html (sha256 fee86b8b1f3900b9) Wayback capture 20210508192900 of the ECB working-hours page (used for 2021)
- https://web.archive.org/web/20211214193232id_/https://www.ecb.europa.eu/services/contacts/working-hours/html/index.en.html -> data/vendor/release_pages/e4c/wb_20211214193232_ecb_working_hours.html (sha256 92d93ca5370971f6) Wayback capture 20211214193232 of the ECB working-hours page (used for 2022)
- https://web.archive.org/web/20221217181447id_/https://www.ecb.europa.eu/services/contacts/working-hours/html/index.en.html -> data/vendor/release_pages/e4c/wb_20221217181447_ecb_working_hours.html (sha256 0b8d4769287d98c5) Wayback capture 20221217181447 of the ECB working-hours page (used for 2023)
- https://web.archive.org/web/20231228195814id_/https://www.ecb.europa.eu/services/contacts/working-hours/html/index.en.html -> data/vendor/release_pages/e4c/wb_20231228195814_ecb_working_hours.html (sha256 5098662472af86af) Wayback capture 20231228195814 of the ECB working-hours page (used for 2024)
- https://web.archive.org/web/20241230111431id_/https://www.ecb.europa.eu/ecb/contacts/working-hours/html/index.en.html -> data/vendor/release_pages/e4c/wb_20241230111431_ecb_working_hours.html (sha256 6ef3c4b72c083fd8) Wayback capture 20241230111431 of the ECB working-hours page (used for 2025)
- https://web.archive.org/web/20251218035041id_/https://www.ecb.europa.eu/ecb/contacts/working-hours/html/index.en.html -> data/vendor/release_pages/e4c/wb_20251218035041_ecb_working_hours.html (sha256 050cb23955792d0c) Wayback capture 20251218035041 of the ECB working-hours page (used for 2026)
- https://www.ecb.europa.eu/services/contacts/working-hours/html/index.en.html -> data/vendor/release_pages/e4c/ecb_working_hours_live.html (sha256 535a7c8d44e4ac14) live fetch 2026-09-27; served at /ecb/contacts/working-hours/; lists 2026-2028
- https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv -> data/vendor/release_pages/e4c/cao_syukujitsu.csv (sha256 cec37a743c96995c) Cabinet Office national holidays CSV, Shift_JIS, raw
- https://murc-kawasesouba.jp/fx/xls/murc_2019.xls -> data/vendor/release_pages/e4c/murc/murc_2019.xls (sha256 201152d5fc63b083) MUFG Research (MURC) yearly TTM file 2019
- https://murc-kawasesouba.jp/fx/xls/murc_2020.xls -> data/vendor/release_pages/e4c/murc/murc_2020.xls (sha256 1934b2dd2d0a3786) MUFG Research (MURC) yearly TTM file 2020
- https://murc-kawasesouba.jp/fx/xls/murc_2021.xls -> data/vendor/release_pages/e4c/murc/murc_2021.xls (sha256 0c461ad9164649bd) MUFG Research (MURC) yearly TTM file 2021
- https://murc-kawasesouba.jp/fx/xls/murc_2022.xls -> data/vendor/release_pages/e4c/murc/murc_2022.xls (sha256 22aa7ff8c55322ca) MUFG Research (MURC) yearly TTM file 2022
- https://murc-kawasesouba.jp/fx/xls/murc_2023.xls -> data/vendor/release_pages/e4c/murc/murc_2023.xls (sha256 6d5491ad15ab6d9f) MUFG Research (MURC) yearly TTM file 2023
- https://murc-kawasesouba.jp/fx/xls/murc_2024.xls -> data/vendor/release_pages/e4c/murc/murc_2024.xls (sha256 88bb77513fee350b) MUFG Research (MURC) yearly TTM file 2024
- https://murc-kawasesouba.jp/fx/xls/murc_2025.xls -> data/vendor/release_pages/e4c/murc/murc_2025.xls (sha256 4073727919db52c4) MUFG Research (MURC) yearly TTM file 2025
- https://murc-kawasesouba.jp/fx/xls/murc_2026.xls -> data/vendor/release_pages/e4c/murc/murc_2026.xls (sha256 53ffc4d25d1cf037) MUFG Research (MURC) yearly TTM file 2026
- Index files: data/vendor/index_history/manifest.jsonl (URL requested, URL served, fetch time PDT, sha256). Pages: data/vendor/release_pages/e4c/manifest.jsonl. CDX listings saved as data/vendor/release_pages/e4c/cdx_*.txt.

## Log (fetch failures and notes, PDT)

- EC-EW: gov.uk JSON covers years 2019..2028; 63 E&W holidays in 2019-04-01..2026-06-30
- EC-JP: CAO CSV rows 1067, first 1955-01-01, last 2027-11-23
- EC-CAL fx coverage 2019-05-01..2026-06-19; full closures in coverage: 2019-12-25, 2020-01-01, 2020-04-10, 2020-12-25, 2021-01-01, 2021-12-24, 2022-04-15, 2022-12-26, 2023-01-02, 2023-12-25, 2024-01-01, 2024-03-29, 2024-12-25, 2025-01-01, 2025-04-18, 2025-12-25, 2026-01-01
- 06:14 PDT FRED fredgraph.csv: curl HTTP/2 stream INTERNAL_ERROR; 06:15 retry --http1.1 timed out (90 s); later python urllib timed out; FRED home page returns 200, series paths blocked for this client.
- 06:14 PDT stoxx.com: TLS verify failure (server sends chain to AAA Certificate Services, not in the local store); fixed by adding the AIA intermediate http://cert.ssl.com/SSL.com-TLS-I-RSA-R1.cer (issuer SSL.com TLS RSA Root CA 2022, in store); verification kept on.
- 06:16 PDT stoxx.com h_3msx5e.txt live: 66 rows, 2026-06-26..2026-09-25 (rolling 3 months). h_sx5e.txt: 302 to /c/portal/login (login wall, not used). hbrbcpe.txt: ends 2016.
- 06:18 PDT Wayback refused connections for two STOXX captures (20240803, 20250618); retried 06:22 PDT, both served 200.
- 06:21 PDT mizuhobank.co.jp quote.csv: 403 (also with Referer); Wayback has no capture (404); CDX queries 504. Replaced by MURC (MUFG Research) yearly TTM files.
- Nikkei 225 stitched from Nikkei Inc. live CSV (2023-01-04..2026-09-25) and Wayback captures 20200919 (2017-01-04..2020-09-18), 20230523 (2020-01-06..2023-05-23), 20240401 (2021-01-04..2024-03-29); no value conflicts in overlaps.
- No WebSearch used; no budget or cost notice seen.

## Unverified

- FRED NIKKEI225 spot check: values read from a Firecrawl scrape of https://fred.stlouisfed.org/graph/fredgraph.csv?id=NIKKEI225&cosd=2019-03-01&coed=2026-06-30 (2026-09-27 ~06:16 PDT); the scrape was not saved to disk (direct curl to FRED failed: HTTP/2 INTERNAL_ERROR, then timeouts).
- EC-TGT 2019-2021: the dates are computed from the rule sentence on the TARGET2 calendar page captures (Easter by computus); the page lists no dates for those years.
- SX5E gap check calendar: STOXX index calculation days assumed = weekdays minus EC-TGT closing days; STOXX published a value on 2025-05-01 (a TARGET closing day).
- ME(2019-04) and ME(2026-06) lie outside EC-CAL fx coverage (2019-05-01..2026-06-19): the last weekday is listed, not an EC-CAL trade date.
