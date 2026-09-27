# Brief: AuctionXmlChecker-OpusMed (Stage E.3, Task 1b)

Worker file: worker-medium. Model: opus. Effort: medium (a narrow, bounded lookup: one site, one fact list).
Written by the Stage E.3 lead, 2026-09-26 23:50 PDT.

## Objective (one)

Run the EC-AUC check that the frozen K2 catalog assigned to E.2 and that no earlier stage ran
(reports/stage_e0_catalog_K2.md lines 91-92): "if the announcement XML (xml_filenm_announcemt) and the
query disagree on closing_time_comp for any auction, that auction is dropped and logged." You only
check and report. The lead decides what is dropped.

## Records in scope

From data/vendor/release_pages/treasury/auctions_query_notes_bonds_20190501_20260621.csv (763 rows,
header: auction_date, security_type, security_term, original_security_term, cusip, reopening,
floating_rate, inflation_index_security, announcemt_date, closing_time_comp, closing_time_noncomp),
keep the rows with:
- security_type "Note" or "Bond";
- floating_rate "No" and inflation_index_security "No";
- announcemt_date strictly before auction_date;
- original_security_term one of "2-Year", "5-Year", "10-Year", "30-Year";
- auction_date in [2019-05-06, 2026-06-19].
Report the count per tenor, and say whether it matches the frozen release calendar's TREASURY_AUCTION rows for
2Y/5Y/10Y/30Y in that date range (reports/stage_e2b_release_calendar.json; ids end in -2Y, -5Y, -10Y, -30Y;
read it with a short python script that prints counts only, never the whole file).

## Steps

1. Get each record's announcement XML file name. Query the FiscalData auctions_query endpoint
   (https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query)
   with `fields=` limited to: cusip, auction_date, security_type, original_security_term, floating_rate,
   inflation_index_security, announcemt_date, closing_time_comp, xml_filenm_announcemt. The same
   filter and date range as the saved CSV, csv format, page size 10000. Never request any results field
   (high_yield, bid_to_cover_ratio, offering amounts accepted, allotments, and so on). Save the raw
   response to data/vendor/release_pages/treasury/e3_auctions_xml_names.csv before parsing it.
2. For each in-scope record, fetch the announcement XML at https://www.treasurydirect.gov/xml/<xml_filenm_announcemt>
   with curl (a browser User-Agent header if the plain request is refused; at most 2 requests a second).
   Save each file under data/vendor/release_pages/treasury/e3_announcement_xml/ before parsing.
   Fetch ONLY announcement files (the xml_filenm_announcemt name). Never fetch a results file
   (xml_filenm_comp_results or any R_*.xml).
3. From each XML, read the competitive tender closing time element. Look at one file first to find its
   exact tag name, and quote it in your log. Normalize both times to HH:MM 24-hour ET, then compare with
   closing_time_comp from the CSV.
4. If treasurydirect.gov refuses a file after two tries, try the Wayback Machine copy
   (https://web.archive.org/web/2026id_/<url>). Mark every item gathered that way. An item you cannot get
   is "xml_unavailable" and [unverified]. Never fill it from memory or inference.

## Output

- reports/stage_e3_auction_xml_check.json: {"schema": "stage_e3_auction_xml_check/1", "fetched_utc":
  ..., "counts": {...}, "records": [{"auction_date", "cusip", "tenor", "query_closing_time_comp",
  "xml_file", "xml_closing_time_comp", "via": "treasurydirect"|"wayback", "status":
  "agree"|"disagree"|"xml_unavailable"}]} with every in-scope record.
- reports/stage_e3_auction_xml_check.md: method, the XML tag quoted from one file, per-tenor counts,
  the match against the release calendar counts, every disagreement with both values quoted verbatim
  (the XML element text and the CSV row), every unavailable file, and the times you started and ended
  (PDT).
- Return to the lead: the two paths, a summary of at most 200 words, and anything you could not
  finish.

## Allowed tools and boundaries

- Bash (curl, python3 or `uv run python` for parsing), WebFetch only as a fallback. Pages go to disk
  first, then you grep or parse them. Only short extracts enter your context.
- Do not edit any existing file. Do not read any bar or price file, and do not touch data/processed*,
  ledger/, live/, ops/ or REGISTRATION.md. No Databento, no TopstepX, no credentials. No git commands
  that change anything.
- If a WebSearch or WebFetch budget notice appears, write it into your log with the time and return. Do
  not continue from memory.
- Other workers are coding strategy/members/k2/ in parallel. Do not touch that directory or tests/.
