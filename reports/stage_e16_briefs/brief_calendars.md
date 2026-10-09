# Task 3b brief: CalendarBuilder-OpusHigh (worker-high, opus). Read brief_common.md first.

Two calendars the 2010-2024 window needs that do not exist yet. E.14's six hist group calendars (energy, equity,
rates, fx, metals, grains; data/calendars/hist2010/*.json) are reused as frozen: do not edit them.

(a) The LIVESTOCK group calendar for trade dates 2010-06-01..2019-05-31 (LE, HE; CME livestock), in E.14's hist
calendar format and grading: the JSON schema data/hist_calendar.py loads (read that module and one existing file,
for example data/calendars/hist2010/grains.json, by section), with full closures, early closes (halt minute), halts,
scheduled late opens, the session specs (segments and day_session_ct: the livestock day session open and close and
every change in 2010-2019 with its date), each date's status graded and cited per E.14's rules
(reports/stage_e14_briefs/calendar_rules.md, brief_cal_equity.md, brief_cal_commod.md; the hist2010 files' own
grading and "unsourced" fields), and the 2% check: the share of window weekdays whose status is unsourced, which must
be at most 2% (report the share and list the dates). Write it to reports/stage_e16_calendars/hist2010_livestock.json
(NOT under data/: data/ is harness code; E.17's later harness will copy it in). Prove it loads: call
data.hist_calendar's parser on the file (or on a copy in a scratch directory outside the repo) without writing into
data/, and report what data.hist_calendar would need to accept a "livestock" group (for example a hardcoded group
list), as a note for E.17; do not edit it. Also cross-check your 2019-05 dates against the frozen
data/calendars/livestock.py (the 2019 on calendar): the overlap must agree.
Sources: no CME pages, live or archived (brief_common.md). Permitted examples: cftc.gov, the Federal Register, USDA
pages (AMS market news schedules note livestock market closures), broker or vendor holiday-schedule pages and PDFs
whose terms allow access, news reports of exchange closures, published papers. E.14's grains calendar evidence may be
reused for livestock only where the source explicitly covers livestock (CME agricultural) hours.

(b) The EC-AUC Treasury auction calendar for auction dates 2010-01-01..2019-06-30, from FiscalData's public
auctions_query API (https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query;
read FiscalData's terms/API documentation page first and save it), with E.0's rule (reports/stage_e0_catalog.md lines
1350-1365: fields security_type, original_security_term, floating_rate, inflation_index_security, auction_date,
announcemt_date, closing_time_comp; a record counts only if announcemt_date is strictly before auction_date; Note or
Bond, floating_rate No, inflation_index_security No). Read metadata fields only (plus security_term and cusip for
identity); no result field (no yield, no bid-to-cover, no price). Output rows in the FROZEN format of the
TREASURY_AUCTION rows of reports/stage_e2b_release_calendar.json (same keys, same time and tenor conventions; read its
schema and a few rows by script) to reports/stage_e16_calendars/ec_auc_2010_2019.json, with a header block (source
URL, query parameters, fetch times, response sha256s, counts by tenor and year, same-day-announcement exclusions,
records missing a required field). Save the raw API responses under reports/stage_e16_briefs/pages/fiscaldata/ with
a fetch log. Overlap check: your rows for 2019-05-01..2019-06-30 must equal the frozen file's rows exactly (report
the comparison). The 2% check for EC-AUC: the share of 2-, 5-, 10- and 30-year nominal fixed-rate records in
2010-06..2019-04 that are dropped for a missing field or a same-day announcement (report counts; above 2% is reported,
not hidden).

Also write reports/stage_e16_calendars.md: method, sources with grades, counts per year, the 2% checks, deviations,
and the notes for E.17. Boundaries: no market data, no Databento, no edits outside reports/stage_e16_calendars/,
reports/stage_e16_calendars.md and reports/stage_e16_briefs/pages/{livestock,fiscaldata}/. Other workers own the
settlement table, the overlap audit and base_rules/.
