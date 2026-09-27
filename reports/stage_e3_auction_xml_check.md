# Stage E.3 Task 1b: EC-AUC announcement XML check (AuctionXmlChecker-OpusMed)

Started 2026-09-26 23:45 PDT. Ended 2026-09-27 00:03 PDT. FiscalData query fetched 2026-09-27T06:46:12Z.
Machine-readable output: reports/stage_e3_auction_xml_check.json (340 records).

## Method

1. Scope: rows of data/vendor/release_pages/treasury/auctions_query_notes_bonds_20190501_20260621.csv
   (763 rows) with security_type Note/Bond, floating_rate "No", inflation_index_security "No",
   announcemt_date < auction_date, original_security_term in {2,5,10,30}-Year, auction_date in
   [2019-05-06, 2026-06-19]. Tenor = original_security_term.
2. XML names: FiscalData auctions_query, same filter/sort/page size as the saved CSV, fields limited to
   cusip, auction_date, security_type, original_security_term, floating_rate, inflation_index_security,
   announcemt_date, closing_time_comp, xml_filenm_announcemt (no results fields). Raw response saved to
   data/vendor/release_pages/treasury/e3_auctions_xml_names.csv (763 rows, HTTP 200). Joined on
   (cusip, auction_date): every in-scope row matched exactly one row; closing_time_comp and
   announcemt_date identical in both downloads for all 340.
3. Fetched https://www.treasurydirect.gov/xml/<xml_filenm_announcemt> with plain curl, about 0.6 s
   between requests, saved to data/vendor/release_pages/treasury/e3_announcement_xml/ (340 files).
   Only A_*.xml announcement files were requested; no results file was requested or read.
4. Parsed the competitive close element, normalized both sides to HH:MM 24-hour ET, compared.
   Also compared the XML `<CUSIP>` and `<AuctionDate>` with the query row (identity check, extra).

XML tag, quoted from A_20190501_2.xml (10-Year, CUSIP 9128286T2, auction 2019-05-08):

    <CompetitiveClosingTime>13:00
    </CompetitiveClosingTime>

(NonCompetitiveClosingTime is the sibling element, value 12:00 in that file; not used.)

## Counts

| Tenor | In scope | Release calendar TREASURY_AUCTION rows | agree | disagree | xml_unavailable |
|---|---|---|---|---|---|
| 2Y | 84 | 84 | 84 | 0 | 0 |
| 5Y | 83 | 83 | 83 | 0 | 0 |
| 10Y | 87 | 87 | 87 | 0 | 0 |
| 30Y | 86 | 86 | 86 | 0 | 0 |
| Total | 340 | 340 | 340 | 0 | 0 |

The calendar counts come from reports/stage_e2b_release_calendar.json, `releases` entries whose id starts
TREASURY_AUCTION- and ends -2Y/-5Y/-10Y/-30Y with date in range. Beyond counts, the (date, tenor) sets
are identical (0 in either set only).

All 340 files came from treasurydirect.gov on the first try (HTTP 200). Wayback: 0 used.
Value pairs (query, XML): ("01:00 PM","13:00") 317; ("11:30 AM","11:30") 22; ("10:00 AM","10:00") 1
(2019-12-24 5Y 912828YY0, A_20191219_4.xml).

## Disagreements

None on closing_time_comp.

## Unavailable files

None.

## Identity flag (not a closing-time disagreement; for the lead)

Two in-scope records name an announcement file whose XML describes a different security. The
closing time in that file (13:00) equals the query (01:00 PM), so status is "agree" by the brief's
rule, and xml_identity_matches is false in the JSON. I did not decide what this means.

1. Saved CSV line 51: `"2019-11-05","Note","3-Year","10-Year","912828TY6","Yes","No","No","2019-10-30","01:00 PM","12:00 PM"`
   Names CSV line 51: `"912828TY6","2019-11-05","Note","10-Year","No","No","2019-10-30","01:00 PM","A_20191030_1.xml"`
   A_20191030_1.xml: `<SecurityTermWeekYear>3-YEAR`, `<SecurityType>NOTE`, `<CUSIP>912828YR5`,
   `<AnnouncementDate>2019-10-30`, `<AuctionDate>2019-11-05`, `<CompetitiveClosingTime>13:00`,
   `<ReOpeningIndicator>N`.
2. Saved CSV line 720: `"2026-01-26","Note","2-Year","5-Year","91282CGH8","Yes","No","No","2026-01-22","01:00 PM","12:00 PM"`
   Names CSV line 720: `"91282CGH8","2026-01-26","Note","5-Year","No","No","2026-01-22","01:00 PM","A_20260122_2.xml"`
   A_20260122_2.xml: `<SecurityTermWeekYear>2-YEAR`, `<SecurityType>NOTE`, `<CUSIP>91282CPV7`,
   `<AnnouncementDate>2026-01-22`, `<AuctionDate>2026-01-26`, `<CompetitiveClosingTime>13:00`,
   `<ReOpeningIndicator>N`.

Observed facts only: in both rows security_term (3-Year, 2-Year) differs from original_security_term
(10-Year, 5-Year) and reopening is "Yes"; the scope filter keys on original_security_term, so these
two enter the 10Y and 5Y counts, and the release calendar carries TREASURY_AUCTION-2019-11-05-10Y and
TREASURY_AUCTION-2026-01-26-5Y. In the in-scope set, 117 rows have security_term different from
original_security_term; 115 of them are the usual 9-Year 10/11-Month and 29-Year 10/11-Month reopenings,
and these two (3-Year of a 10-Year, 2-Year of a 5-Year) are the only others. All 338 other XML files
match the query row on both CUSIP and auction date.

## Boundaries kept

No results fields requested, no R_*.xml or results file fetched. No existing file edited. No git
changes. No WebSearch/WebFetch used; no budget notice seen.
