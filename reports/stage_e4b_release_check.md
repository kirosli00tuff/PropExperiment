# Stage E.4 Part 2, Task 1b: K5 release check (LBMA gold auctions, UK bank holidays, FOMC)

Built by ReleaseChecker-OpusMed, 2026-09-27 05:03-05:15 PDT. Full data: reports/stage_e4b_release_check.json. Pages: data/vendor/release_pages/e4b/ (manifest.jsonl lists URL requested, URL served, sha256). Extraction and checks only; no member event set is decided here.

## Counts (2019-05-01..2026-06-19)

| Item | Count |
|---|---|
| weekdays_2019-05-01_2026-06-19 | 1863 |
| uk_bank_holidays_in_range | 61 |
| uk_bank_holidays_on_weekdays | 61 |
| scheduled_auction_days | 1802 |
| days_pm_not_held | 14 |
| five_hour_week_days | 124 |
| window_weekdays | 319 |
| window_bank_holidays | 12 |
| window_auction_days | 307 |
| window_pm_not_held | 2 |
| window_five_hour_days | 20 |

CT start times over all scheduled days (zoneinfo, C10 rule): 04:30/09:00/five=False: 1678; 05:30/10:00/five=True: 124. Only two AM/PM pairs occur: 04:30/09:00 CT (6-hour offset) and 05:30/10:00 CT (5-hour weeks).

Research window 2025-04-01..2026-06-19: 319 weekdays, 12 E&W bank holidays, 307 scheduled auction days, 2 of them with no PM auction (2025-12-24, 2025-12-31), 20 days in 5-hour weeks. Matches catalog C12 (319 weekdays, 12 bank holidays, 20 five-hour weekdays).

## EC-UKBH

gov.uk bank-holidays.json (live, England and Wales, lists 2019-01-01..2028-12-26), so no Wayback capture was needed. 61 bank holidays in range, all on weekdays. Cross-check against the IBA gold holiday calendars 2019-2026: every E&W weekday bank holiday is an IBA full no-auction day and every IBA full no-auction day is an E&W bank holiday (issues: none). Includes 2020-05-08 (VE Day), 2022-06-03 (Jubilee), 2022-09-19 (State Funeral), 2023-05-08 (Coronation).

## No-auction days announced in advance (other than bank holidays)

All 14 are UK Christmas/New Year half days: AM gold auction held, PM (15:00) not held. Each is also marked AM "Auction Unaffected" / PM "No Auction" in that year's IBA LBMA Gold Price Holiday Calendar.

| Date | AM held | PM held | Notice date | Notice source | IBA calendar dating |
|---|---|---|---|---|---|
| 2019-12-24 | True | False | 2019-12-13 | https://www.lbma.org.uk/_blog/lbma_media_centre/post/lbma-prices-and-lpmcl-clearing-over-the-2019-festive-period/ (Wayback 20191218064424) | linked from IBA page capture 2019-06-08 |
| 2019-12-31 | True | False | 2019-12-13 | https://www.lbma.org.uk/_blog/lbma_media_centre/post/lbma-prices-and-lpmcl-clearing-over-the-2019-festive-period/ (Wayback 20191218064424) | linked from IBA page capture 2019-06-08 |
| 2020-12-24 | True | False | 2020-12-15 | https://www.lbma.org.uk/articles/2020-2021-lpmcl-closing-times-and-dates-when-prices-will-not-be-published | PDF CreationDate 2019-10-21 |
| 2020-12-31 | True | False | 2020-12-15 | https://www.lbma.org.uk/articles/2020-2021-lpmcl-closing-times-and-dates-when-prices-will-not-be-published | PDF CreationDate 2019-10-21 |
| 2021-12-24 | True | False | 2021-11-23 | https://www.lbma.org.uk/articles/lbma-precious-metals-auctions | PDF CreationDate 2020-12-10 |
| 2021-12-31 | True | False | 2021-12-07 | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times | PDF CreationDate 2020-12-10 |
| 2022-12-23 | True | False | 2022-12-07 | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2022 | PDF CreationDate 2022-09-12 (revision) |
| 2022-12-30 | True | False | 2022-12-07 | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2022 | PDF CreationDate 2022-09-12 (revision) |
| 2023-12-22 | True | False | 2023-12-14 | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2023 | PDF CreationDate 2023-05-15 (revision) |
| 2023-12-29 | True | False | 2023-12-14 | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2023 | PDF CreationDate 2023-05-15 (revision) |
| 2024-12-24 | True | False | 2024-12-17 | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2024 | PDF CreationDate 2023-11-20 |
| 2024-12-31 | True | False | 2024-12-17 | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2024 | PDF CreationDate 2023-11-20 |
| 2025-12-24 | True | False | 2025-12-15 | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2025 | PDF CreationDate 2024-10-17; Wayback first capture 2025-05-22 |
| 2025-12-31 | True | False | 2025-12-15 | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2025 | PDF CreationDate 2024-10-17; Wayback first capture 2025-05-22 |

Note: in 2022 and 2023 the half days were the Fridays before Christmas Eve / New Year's Eve (2022-12-23, 2022-12-30, 2023-12-22, 2023-12-29), not 24 and 31 December. Every notice date predates its day. No other advance-announced cancellation was found in the IBA calendars or LBMA notices.

## 5-hour weeks (London minus Chicago = 5 h), weekdays, zoneinfo

| Year | Spring | Autumn | Matches C10 table |
|---|---|---|---|
| 2019 | 2019-03-11..2019-03-29 (15) | 2019-10-28..2019-11-01 (5) | True |
| 2020 | 2020-03-09..2020-03-27 (15) | 2020-10-26..2020-10-30 (5) | True |
| 2021 | 2021-03-15..2021-03-26 (10) | 2021-11-01..2021-11-05 (5) | True |
| 2022 | 2022-03-14..2022-03-25 (10) | 2022-10-31..2022-11-04 (5) | True |
| 2023 | 2023-03-13..2023-03-24 (10) | 2023-10-30..2023-11-03 (5) | True |
| 2024 | 2024-03-11..2024-03-29 (15) | 2024-10-28..2024-11-01 (5) | True |
| 2025 | 2025-03-10..2025-03-28 (15) | 2025-10-27..2025-10-31 (5) | True |
| 2026 | 2026-03-09..2026-03-27 (15) | 2026-10-26..2026-10-30 (5) | True |

All eight rows equal C10 (catalog lines 206-219). Published start times: IBA page capture 2019-06-08 "The auctions are run at 10:30am and 3:00pm London time for gold"; current IBA page "The auctions are run at 10:30 and 15:00 London time for gold"; all IBA calendars 2019-2026 head the columns "Auction (1030)" and "Auction (1500)". No published change to the gold start times found.

## EC-FOMC

reports/stage_e2b_release_calendar.json release==FOMC: 57 rows, all time_local 14:00 America/New_York = 13:00 America/Chicago (converted from instant_utc with zoneinfo). strategy/members/k2/_releases.py FOMC_STATEMENT_DATES: 57 dates. Equal, same order: **True**; differences: none. 2020-03-18 is in the calendar's cancellations list (meeting cancelled).

Research-window statement days (10): 2025-05-07, 2025-06-18, 2025-07-30, 2025-09-17, 2025-10-29, 2025-12-10, 2026-01-28, 2026-03-18, 2026-04-29, 2026-06-17 — equal to catalog C12 lines 256-257.

## Sources

| File | URL requested | URL served | Fetched (PDT) | sha256 |
|---|---|---|---|---|
| govuk_bank-holidays.json | https://www.gov.uk/bank-holidays.json | https://www.gov.uk/bank-holidays.json | 2026-09-27T05:03-07:00 | 538b3482c28b85ec… |
| iba_lbma-precious-metals.html | https://www.ice.com/iba/lbma-precious-metals | https://www.ice.com/iba/lbma-precious-metals | 2026-09-27T05:03-07:00 | df9cbce4aaeb9445… |
| lbma_closing_times_base.html | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times | 2026-09-27T05:03-07:00 | cf00f993dacc26c7… |
| lbma_closing_times-2022.html | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2022 | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2022 | 2026-09-27T05:03-07:00 | f70a37fef9830af1… |
| lbma_closing_times-2023.html | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2023 | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2023 | 2026-09-27T05:03-07:00 | cd1c1d80c7e2f705… |
| lbma_closing_times-2024.html | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2024 | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2024 | 2026-09-27T05:03-07:00 | e6b27f945adeacf3… |
| lbma_closing_times-2025.html | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2025 | https://www.lbma.org.uk/articles/market-and-lbma-price-auction-closing-times-2025 | 2026-09-27T05:03-07:00 | 02e8088154ccd18a… |
| lbma_2020-2021-lpmcl-closing-times-and-dates-when-prices-will-not-be-published.html | https://www.lbma.org.uk/articles/2020-2021-lpmcl-closing-times-and-dates-when-prices-will-not-be-published | https://www.lbma.org.uk/articles/2020-2021-lpmcl-closing-times-and-dates-when-prices-will-not-be-published | 2026-09-27T05:04-07:00 | f837742fe82f1aa5… |
| lbma_lbma-precious-metals-auctions.html | https://www.lbma.org.uk/articles/lbma-precious-metals-auctions | https://www.lbma.org.uk/articles/lbma-precious-metals-auctions | 2026-09-27T05:04-07:00 | bbd210d504ab6c51… |
| wb_20191218064424_lbma-prices-and-lpmcl-clearing-over-the-2019-festive-period.html | https://web.archive.org/web/20191218064424/http://www.lbma.org.uk:80/_blog/lbma_media_centre/post/lbma-prices-and-lpmcl-clearing-over-the-2019-festive-period/ | https://web.archive.org/web/20191218064424/http://www.lbma.org.uk:80/_blog/lbma_media_centre/post/lbma-prices-and-lpmcl-clearing-over-the-2019-festive-period/ | 2026-09-27T05:04-07:00 | 9c85e2529c91ba4c… |
| wb_20201216163829_market-closing-times-and-price-publication-dates-over-the-2020-21-festive-period.html | https://web.archive.org/web/20201216163829/http://www.lbma.org.uk/_blog/lbma_media_centre/post/market-closing-times-and-price-publication-dates-over-the-2020-21-festive-period/ | https://web.archive.org/web/20201216163829/http://www.lbma.org.uk/_blog/lbma_media_centre/post/market-closing-times-and-price-publication-dates-over-the-2020-21-festive-period/ | 2026-09-27T05:04-07:00 | 9e8d4e75737627e9… |
| wb_20190608104336_iba_lbma-gold-silver-price.html | https://web.archive.org/web/20190608104336/https://www.theice.com/iba/lbma-gold-silver-price | https://web.archive.org/web/20190608104336/https://www.theice.com/iba/lbma-gold-silver-price | 2026-09-27T05:09-07:00 | c7c1cc5256dfca18… |
| wb_iba_LBMA_Gold_Price_Holiday_Calendar_2019.pdf | https://web.archive.org/web/20190608104336if_/https://www.theice.com/publicdocs/LBMA_Gold_Price_Holiday_Calendar_2019.pdf | https://web.archive.org/web/20201202011450if_/https://www.theice.com/publicdocs/LBMA_Gold_Price_Holiday_Calendar_2019.pdf | 2026-09-27T05:09-07:00 | 46d0ae24ad3f8ce5… |
| iba_Gold_Holiday_Calendar_2020.pdf | https://www.ice.com/publicdocs/Gold_Holiday_Calendar_2020.pdf | https://www.ice.com/publicdocs/Gold_Holiday_Calendar_2020.pdf | 2026-09-27T05:05-07:00 | a91bd02d018b7add… |
| iba_Gold_Holiday_Calendar_2021.pdf | https://www.ice.com/publicdocs/Gold_Holiday_Calendar_2021.pdf | https://www.ice.com/publicdocs/Gold_Holiday_Calendar_2021.pdf | 2026-09-27T05:05-07:00 | c6eaa601ae788ba2… |
| iba_Gold_Holiday_Calendar_2022.pdf | https://www.ice.com/publicdocs/Gold_Holiday_Calendar_2022.pdf | https://www.ice.com/publicdocs/Gold_Holiday_Calendar_2022.pdf | 2026-09-27T05:05-07:00 | 995dc0239c40d726… |
| iba_Gold_Holiday_Calendar_2023.pdf | https://www.ice.com/publicdocs/Gold_Holiday_Calendar_2023.pdf | https://www.ice.com/publicdocs/Gold_Holiday_Calendar_2023.pdf | 2026-09-27T05:05-07:00 | f0e3da337c665d90… |
| iba_Gold_Holiday_Calendar_2024.pdf | https://www.ice.com/publicdocs/Gold_Holiday_Calendar_2024.pdf | https://www.ice.com/publicdocs/Gold_Holiday_Calendar_2024.pdf | 2026-09-27T05:05-07:00 | 94c205c28462b036… |
| iba_Gold_Holiday_Calendar_2025.pdf | https://www.ice.com/publicdocs/Gold_Holiday_Calendar_2025.pdf | https://www.ice.com/publicdocs/Gold_Holiday_Calendar_2025.pdf | 2026-09-27T05:05-07:00 | 4f5ab78dcc514cbc… |
| iba_Gold_Holiday_Calendar_2026.pdf | https://www.ice.com/publicdocs/Gold_Holiday_Calendar_2026.pdf | https://www.ice.com/publicdocs/Gold_Holiday_Calendar_2026.pdf | 2026-09-27T05:05-07:00 | dbfaa795cc3154e7… |
| cdx_lbma_lbma.org.uk_articles__.txt | Wayback CDX API query | n/a | 2026-09-27T05:04-07:00 | 0c6d57d10fd0fc8f… |
| cdx_lbma_www.lbma.org.uk__.txt | Wayback CDX API query | n/a | 2026-09-27T05:04-07:00 | 471da1de051c79b3… |
| cdx_ice_publicdocs_holiday.txt | Wayback CDX API query | n/a | 2026-09-27T05:04-07:00 | d03aed88789e8a28… |
| cdx_iba_goldsilver_2019_2020.txt | Wayback CDX API query | n/a | 2026-09-27T05:04-07:00 | b099e3f5c21061ef… |

## Log (failed fetches and events, PDT)

- 05:03 PDT gov.uk bank-holidays.json fetched live (200); England-and-Wales covers 2019-01-01..2028-12-26, so no Wayback capture needed.
- 05:03 PDT LBMA closing-times articles: base (2021), -2022..-2025 200; -2019, -2020, -2021, -2026 slugs 404 (not saved).
- 05:04 PDT live /articles/lbma-prices-and-lpmcl-clearing-over-the-2019-festive-period 404; used Wayback capture 20191218064424 of the old blog URL instead.
- 05:05 PDT IBA Gold_Holiday_Calendar_2019.pdf live 404; 2020..2026 200.
- 05:06-05:08 PDT Wayback CDX for ice.com/publicdocs/Gold_Holiday_Calendar_2019.pdf and _2026.pdf returned 504 Gateway Time-out.
- 05:09 PDT Wayback: 2019 IBA gold page capture 20190608104336 served as requested; its linked 2019 holiday calendar PDF was served from capture 20201202011450 (different day than requested).
- A PostToolUse session-cost notice appeared (informational, not a WebSearch budget notice); no WebSearch was used (Firecrawl search used 3 times).

## Unverified / caveats

- Advance-publication dates for IBA holiday calendars are PDF CreationDate metadata (and Wayback first captures), not published notice dates; the dated LBMA notices are the primary advance evidence for half days.
- No IBA/LBMA notice found for non-auction days other than bank holidays and the Christmas/New Year half days; absence of other advance-announced cancellations is from the IBA calendars only (2019 via Wayback, 2020-2026 live). Unscheduled disruptions were not searched (they would not be announced in advance).
- Start-time change check: IBA page 2019-06-08 capture says 10:30am and 3:00pm; current IBA page says 10:30 and 15:00; every IBA calendar 2019-2026 heads its columns Auction (1030)/(1500). No published change found; intermediate years not checked page by page.
- Glyph mapping in IBA calendar PDFs: pdftotext renders the symbols as O (key: No Auction) and P (key: Auction Unaffected); the mapping is read from each PDF key.
