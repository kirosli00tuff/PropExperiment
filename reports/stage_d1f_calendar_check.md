# Stage D.1f calendar check: CME Globex equity hours around Independence Day, 2019-2024

Source lookup only (CalendarChecker-OpusXHigh). The lead decides whether `data/cme_calendar.py` changes; this file records what CME's own documents say. Full records: `reports/stage_d1f_calendar_check.json`.

**Result.** Every date in the brief has at least one CME-primary document, fetched in full (cmegroup.com returns HTTP 403 to automated clients, so every CME file was read from a Wayback Machine copy). None of these documents describes a full Globex closure for equity products on any of the Independence Day dates. They give a 12:00 CT halt with a 17:00 CT reopen (2020: a 12:00 CT close on Friday with a Sunday 17:00 CT reopen). The eve dates show a 12:15 CT early close with a 17:00 CT reopen the same day. These times coincide with the bar pattern given in the brief (last bar 11:59 CT, next bar 17:00 CT). No secondary source was needed for any date.

**Scope caveat.** The 2019-2023 documents give hours per product group ('Equity', 'Equity Products', 'EQUITIES'), not per contract. ES and MES are not named, and they are not among the listed Equity exceptions (those are BTIC and TACO instruments only). The 2023 summary PDF says its rows use 'the most actively traded instruments for each asset class'. The 2024 JSON names ES ('E-mini S&P 500 Futures', id 133) and does not include MES.

**Quote conventions.** Spreadsheet quotes are the cell text as displayed (LibreOffice CSV export, cells separated by `|`, trailing empty cells dropped, a leading `...` marks a line cut before its first `|`, which drops only the long column-A header text). Which date a spreadsheet column belongs to was read from the merged header cells with xlrd (see notes). PDF table-cell lines are kept one per line, and PDF prose that wraps across lines is joined with a single space. A build script asserted every quote as a verbatim substring of the fetched text.

## Summary table

| Group | Date | Weekday | Calendar now | Finding (CME source) | Halt CT | Reopen CT | Sources (grade) |
|---|---|---|---|---|---|---|---|
| B | 2019-07-03 | Wednesday | EARLY_HALT 12:15 (time inferred) | halt_1215_ct | 12:15 | 2019-07-03 17:00 | 2019 Globex schedule, compact (cme_primary); 2019 Globex schedule, full (zip) (cme_primary) |
| A | 2019-07-04 | Thursday | FULL_CLOSURE | halt_1200_ct | 12:00 | 2019-07-04 17:00 | 2019 Globex schedule, compact (cme_primary); 2019 Globex schedule, full (zip) (cme_primary); 2019 clearing advisory (cme_primary) |
| A | 2020-07-03 | Friday | FULL_CLOSURE | halt_1200_ct | 12:00 | 2020-07-05 17:00 | 2020 Globex schedule, full (cme_primary); 2020 clearing advisory (cme_primary) |
| A | 2021-07-05 | Monday | FULL_CLOSURE | halt_1200_ct | 12:00 | 2021-07-05 17:00 | 2021 Globex schedule, compact (cme_primary); 2021 clearing advisory (cme_primary) |
| A | 2022-07-04 | Monday | FULL_CLOSURE | halt_1200_ct | 12:00 | 2022-07-04 17:00 | 2022 Globex schedule, compact (cme_primary); 2022 Globex schedule, full (cme_primary) |
| B | 2023-07-03 | Monday | EARLY_HALT 12:15 (time inferred) | halt_1215_ct | 12:15 | 2023-07-03 17:00 | 2023 holiday summary PDF (cme_primary); 2023 trading-hours page (cme_primary) |
| A | 2023-07-04 | Tuesday | FULL_CLOSURE | halt_1200_ct | 12:00 | 2023-07-04 17:00 | 2023 holiday summary PDF (cme_primary); 2023 trading-hours page (cme_primary) |
| C | 2024-07-03 | Wednesday | EARLY_HALT 12:15 (time inferred) | halt_1215_ct | 12:15 | 2024-07-03 17:00 | 2024 trading-hours JSON (ES) (cme_primary) |
| C | 2024-07-04 | Thursday | FULL_CLOSURE | halt_1200_ct | 12:00 | 2024-07-04 17:00 | 2024 trading-hours JSON (ES) (cme_primary) |

## Per date, with verbatim quotes

### 2019-07-03 (Wednesday), group B: halt_1215_ct

Question: Did CME Globex equity index futures (ES/MES) halt (early close) at 12:15 CT this day and reopen at 17:00 CT the same day?

Group label in the sources is 'Equity' / 'Equity Products'; ES and MES are not named individually and are not in the listed Equity exceptions (BTIC and TACO instruments only). Compact sheet: Calendar Date 'Wednesday July 3' -> CLOSE 'Early @ 1215 CT', OPEN 'Regular @ 1700 CT'. Full sheet (merged header ranges read with xlrd): Equity Products 'Early Close' 12:15 and 'Pre-opening**' 16:45 / 'Open' 17:00 all sit under Calendar Date 'Wednesday, July 3'; the 17:00 open belongs to Trade Date 'Friday, July 5'. The compact file in the zip is byte-identical (sha256 8546b2a9...) to the standalone copy captured 2022-09-20; zip entry dated 2019-10-23. Current calendar entry (early halt 12:15 CT, time_evidence 'inferred') agrees with this CME source.

- **CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019 (compact spreadsheet, sheet 'Independence Day 2019')**, CME Group (Globex holiday trading schedule), grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019/2019-4th-of-july-holiday-schedule-compact.xls  
  Archive: https://web.archive.org/web/20220920142350/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019/2019-4th-of-july-holiday-schedule-compact.xls

```text
|CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019
Trade Date|Wednesday July 3 |    Friday July 5
Calendar Date|Wednesday July 3 |Wednesday,July 3|Thursday July 4 |Thursday July 4 into  Friday July 5
Product|CLOSE|OPEN|HALT|OPEN
Equity |Early  @ 1215 CT / 1715 UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC
```

- **globex-trading-schedules/2019-independence-day-schedule.xls inside CME's 2019-holiday-calendars.zip: 'CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019' (Updated 6/6/2019)**, CME Group (Globex holiday trading schedule), grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip  
  Archive: https://web.archive.org/web/20210126094837/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip

```text
Updated 6/6/2019|CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019
Trade Date|Wednesday, July 3||Friday, July 5
Calendar Date|Wednesday, July 3||||||||Thursday, July 4||||||||Friday, July 5
...|Regular Close|Early Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open
Equity Products||12:15||16:45|17:00||||||12:00|12:00|17:00
```

### 2019-07-04 (Thursday), group A: halt_1200_ct

Question: Did CME Globex equity index futures (ES/MES) trade this day with a trading halt at 12:00 CT and a 17:00 CT reopen, or was Globex fully closed?

Compact sheet: Calendar Date 'Thursday July 4' -> HALT '1200 CT / 1700 UTC'; 'Thursday July 4 into  Friday July 5' -> OPEN 'Regular @ 1700 CT / 2200 UTC'. Full sheet: Equity Products 'Halt' 12:00, 'Pre-opening**' 12:00, 'Open' 17:00 in columns 11-13, all under merged Calendar Date 'Thursday, July 4' (cols 9-16); Trade Date 'Friday, July 5' spans cols 3-18, i.e. the Wed 17:00 -> Thu 12:00 session belongs to trade date Friday July 5. The clearing advisory confirms Globex trades on July 4 carried trade date July 5. Current calendar entry is FULL_CLOSURE; this CME source describes a 12:00 CT halt, not a full closure.

- **CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019 (compact spreadsheet, sheet 'Independence Day 2019')**, CME Group (Globex holiday trading schedule), grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019/2019-4th-of-july-holiday-schedule-compact.xls  
  Archive: https://web.archive.org/web/20220920142350/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019/2019-4th-of-july-holiday-schedule-compact.xls

```text
|CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019
Trade Date|Wednesday July 3 |    Friday July 5
Calendar Date|Wednesday July 3 |Wednesday,July 3|Thursday July 4 |Thursday July 4 into  Friday July 5
Product|CLOSE|OPEN|HALT|OPEN
Equity |Early  @ 1215 CT / 1715 UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC
```

- **globex-trading-schedules/2019-independence-day-schedule.xls inside CME's 2019-holiday-calendars.zip: 'CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019' (Updated 6/6/2019)**, CME Group (Globex holiday trading schedule), grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip  
  Archive: https://web.archive.org/web/20210126094837/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-holiday-calendars.zip

```text
Updated 6/6/2019|CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019
Trade Date|Wednesday, July 3||Friday, July 5
Calendar Date|Wednesday, July 3||||||||Thursday, July 4||||||||Friday, July 5
...|Regular Close|Early Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open
Equity Products||12:15||16:45|17:00||||||12:00|12:00|17:00
```

- **IMPORTANT MEMORANDUM, SUBJECT: HOLIDAY SCHEDULE – Thursday, July 4, 2019 Independence Day**, CME Group Clearing, grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-4th-of-july-advisory.pdf  
  Archive: https://web.archive.org/web/20240628032233/https://www.cmegroup.com/tools-information/holiday-calendar/files/2019-4th-of-july-advisory.pdf

```text
Please Note: Trades executed on GLOBEX or ClearPort on Thursday July 4, 2019 will be for trade date Friday, July 5th, 2019.
```

### 2020-07-03 (Friday), group A: halt_1200_ct

Question: Did CME Globex equity index futures (ES/MES) trade this day with a trading halt at 12:00 CT and a reopen on Sunday 2020-07-05 17:00 CT, or was Globex fully closed?

CME labels the Friday 12:00 event 'Close' (not 'Halt'); the next open in the sheet is Sunday July 5 17:00. Merged header ranges (xlrd): Calendar Date 'Thursday, July 2' cols 1-8, 'Friday, July 3' cols 9-11, 'Sunday, July 5' cols 12-16; Trade Date 'Monday, July 6' cols 3-18. Equity Products row: col 1 'Regular Close' 16:00 (Thu Jul 2), col 4-5 Pre-opening 16:45 / Open 17:00 (Thu Jul 2 evening), col 11 'Close' 12:00 (Fri Jul 3), col 12-13 Pre-opening 16:00 / Open 17:00 (Sun Jul 5). So Globex equity traded Thu 17:00 -> Fri 12:00 CT for trade date Monday July 6, closed at 12:00 CT, reopened Sunday 17:00 CT. Advisory confirms Globex trades on Friday July 3, 2020 carried trade date Monday July 6. Sheet times are Excel time values; quoted as displayed by LibreOffice. Current calendar entry is FULL_CLOSURE; this CME source describes a 12:00 CT close with a Sunday reopen.

- **CME Group Globex Independence Day Holiday Schedule: July 2, 2020 to July 6, 2020 (Updated 6/26/2020, sheet 'Independence')**, CME Group (Globex holiday trading schedule), grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-independence-day-schedule.xls  
  Archive: https://web.archive.org/web/20220707015539/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-independence-day-schedule.xls

```text
Updated 6/26/2020|CME Group Globex Independence Day Holiday Schedule: July 2, 2020 to July 6, 2020
Trade Date|Thursday, July 2||Monday, July 6
Calendar Date|Thursday, July 2||||||||Friday, July 3|||Sunday, July 5|||||Monday, July 6
...|Regular Close|Early Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open
Equity Products|16:00|||16:45|17:00||||||12:00|16:00|17:00
* Day Orders entered for Friday's trading session will be eliminated at 12:00 CT
```

- **IMPORTANT MEMORANDUM, SUBJECT: HOLIDAY SCHEDULE – Friday, July 3, 2020 Independence Day (Observed)**, CME Group Clearing, grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-4th-of-july-advisory.pdf  
  Archive: https://web.archive.org/web/20210126094839/https://www.cmegroup.com/tools-information/holiday-calendar/files/2020-4th-of-july-advisory.pdf

```text
Please Note: Trades executed on GLOBEX or ClearPort on Friday July 3rd, 2020 will be for trade date Monday, July 6th, 2020.
```

### 2021-07-05 (Monday), group A: halt_1200_ct

Question: Did CME Globex equity index futures (ES/MES) trade this day with a trading halt at 12:00 CT and a 17:00 CT reopen, or was Globex fully closed?

Compact sheet captured 2021-07-02 05:15 UTC, before the holiday. Equity: Friday July 2 CLOSE 'Regular @ 1600 CT'; Sunday July 4 OPEN 'Regular @ 1700 CT'; Monday July 5 HALT '1200 CT / 1700 UTC'; Monday July 5 OPEN 'Regular @ 1700 CT / 2200 UTC'. Sheet note: day orders entered after Sunday July 4 pre-open are for trade date Tuesday July 6. The advisory line is verbatim including its own typo ('Tuesday, July 5th, 2020'). Current calendar entry is FULL_CLOSURE; this CME source describes a 12:00 CT halt.

- **CME Group Globex Independence Day Holiday Schedule: July 2, 2021 to July 6, 2021 (compact spreadsheet)**, CME Group (Globex holiday trading schedule), grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-independence-day-holiday-schedule-compact.xls  
  Archive: https://web.archive.org/web/20210702051538/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-independence-day-holiday-schedule-compact.xls

```text
|CME Group Globex Independence Day Holiday Schedule: July 2, 2021 to July 6, 2021
Trade Date|Friday, July 2|Tuesday, July 6
Calendar Date|Friday July 2|Sunday July 4|Monday July 5|Monday July 5
Product|CLOSE|OPEN|HALT|OPEN
Equity |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC
Day orders entered after a product’s Pre-opening(s) on Sunday, July 4 are for trade date Tuesday, July 6 and can continue working until their Tuesday, July 6 Globex close.
```

- **IMPORTANT MEMORANDUM, SUBJECT: HOLIDAY SCHEDULE – Monday, July 5th, 2021 Independence Day (Observed)**, CME Group Clearing, grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-4th-of-july-advisory.pdf  
  Archive: https://web.archive.org/web/20210115184655/https://www.cmegroup.com/tools-information/holiday-calendar/files/2021-4th-of-july-advisory.pdf

```text
Please Note: Trades executed on GLOBEX or ClearPort on Monday July 5th, 2021 will be for trade date Tuesday, July 5th, 2020.
```

### 2022-07-04 (Monday), group A: halt_1200_ct

Question: Did CME Globex equity index futures (ES/MES) trade this day with a trading halt at 12:00 CT and a 17:00 CT reopen, or was Globex fully closed?

Both files captured 2022-07-04 06:54 UTC; full sheet 'Updated 6/29/2022'. Compact: Equity Monday July 4 HALT '1200 CT / 1700 UTC', OPEN 'Regular @ 1700 CT / 2200 UTC'. Full sheet merged ranges: Calendar Date 'Monday, July 4' cols 11-21; Equity Products col 13 'Halt' 12:00, col 17 'Pre-opening**' 12:00, col 18 'Open' 17:00. Trade Date 'Tuesday, July 5' cols 3-23. The CME 2022 clearing advisory (fetched in full) gives no Globex hours; it points to the holiday calendar. Current calendar entry is FULL_CLOSURE; this CME source describes a 12:00 CT halt.

- **CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022 (compact spreadsheet, sheet 'Independence Day 2022')**, CME Group (Globex holiday trading schedule), grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls  
  Archive: https://web.archive.org/web/20220704065431/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls

```text
|CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022
Trade Date|Friday, July 1|Tuesday, July 5
Calendar Date|Friday July 1|Sunday July 3|Monday July 4|Monday July 4
Product|CLOSE|OPEN|HALT|OPEN
Equity |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC
Day orders entered after a product’s Pre-opening(s) on Sunday, July 3 are for trade date Tuesday, July 5 and can continue working until their Tuesday, July 5 Globex close.
```

- **CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022 (Updated 6/29/2022, full spreadsheet, sheet 'Independence')**, CME Group (Globex holiday trading schedule), grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls  
  Archive: https://web.archive.org/web/20220704065450/https://www.cmegroup.com/tools-information/holiday-calendar/files/2022-independence-day-holiday-schedule.xls

```text
Updated 6/29/2022|CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022
Trade Date|Friday, July 1||Tuesday, July 5
Calendar Date|Friday, July 1|||||Sunday, July 3|||||Monday, July 4|||||||||||Tuesday, July 5
...|Regular Close|PCP*| Pre-opening**|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open
Equity Products|16:00|||||16:00|17:00||||||12:00||||12:00|17:00
```

### 2023-07-03 (Monday), group B: halt_1215_ct

Question: Did CME Globex equity index futures (ES/MES) halt (early close) at 12:15 CT this day and reopen at 17:00 CT the same day?

From 2023 CME stopped publishing Globex holiday spreadsheets (page statement quoted) and published a one-page summary PDF per holiday; this one was captured 2023-06-27, before the holiday (PDF creation date 2023-03-23). The PDF says its rows use 'the most actively traded instruments for each asset class' and points to the online Trading Calendar for individual products; the EQUITIES row therefore reflects the most active equity instrument, and neither ES nor MES is named. In the layout text the Monday 3 July column of the EQUITIES row holds 'TRADE DATE: MON 3 JULY 12:15 (CLOSED)' then 'TRADE DATE: WED 5 JULY 16:45 (PREOPEN) 17:00 (OPEN)'. Current calendar entry (early halt 12:15 CT, time_evidence 'inferred') agrees.

- **Holiday Schedule (4th of July 2023 summary view; linked from cmegroup.com/trading-hours.html as 'Download a summary view of the 4th of July Holiday Hours')**, CME Group (trading-hours holiday summary), grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf  
  Archive: https://web.archive.org/web/20230627125057/https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf

```text
The table below provides a general overview of holiday trading hours by using the most actively traded instruments for each asset class. To see detailed holiday trading hours for individual products, refer to the CME Group Trading Calendar online, which offers quick and easy product lookup.
Trading hours are subject to change and are in U.S. Central Time unless otherwise stated.
PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023
EQUITIES
TRADE DATE: MON 3 JULY
12:15 (CLOSED)
TRADE DATE: WED 5 JULY
16:45 (PREOPEN)
17:00 (OPEN)
TRADE DATE: WED 5 JULY
12:00 (PREOPEN) HALT
17:00 (OPEN)
TRADE DATE: WED 5 JULY
16:00 (CLOSED)
TRADE DATE: THUR 6 JULY
16:45 (PREOPEN)
17:00 (OPEN)
PREOPEN (HALT): Order Entry, modification, and cancel are allowed. No order matching.
```

- **Trading Hours - Globex Trading Hours and Holiday Schedules (page snapshot 2023-06-27)**, CME Group (trading-hours web page), grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/trading-hours.html  
  Archive: https://web.archive.org/web/20230627124824/https://www.cmegroup.com/trading-hours.html

```text
Please note that with the 2023 calendar year the CME Group will be transitioning from downloadable holiday calendars for Globex and incorporating the holiday hours into our trading hours page. ... Download a summary view of the 4th of July Holiday Hours
```

### 2023-07-04 (Tuesday), group A: halt_1200_ct

Question: Did CME Globex equity index futures (ES/MES) trade this day with a trading halt at 12:00 CT and a 17:00 CT reopen, or was Globex fully closed?

EQUITIES row, Tuesday 4 July column: 'TRADE DATE: WED 5 JULY 12:00 (PREOPEN) HALT 17:00 (OPEN)'. The PDF legend defines PREOPEN (HALT) as order entry allowed with no order matching, i.e. no trading 12:00-17:00 CT. The session up to 12:00 and the 17:00 reopen both belong to trade date Wed 5 July. CME's trading-hours JSON for 2023-07-03..05 (Wayback capture 2024-07-08) returned empty event lists, so it adds nothing. Current calendar entry is FULL_CLOSURE; this CME source describes a 12:00 CT halt.

- **Holiday Schedule (4th of July 2023 summary view; linked from cmegroup.com/trading-hours.html as 'Download a summary view of the 4th of July Holiday Hours')**, CME Group (trading-hours holiday summary), grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf  
  Archive: https://web.archive.org/web/20230627125057/https://www.cmegroup.com/trading-hours/files/4th-of-july-2023.pdf

```text
The table below provides a general overview of holiday trading hours by using the most actively traded instruments for each asset class. To see detailed holiday trading hours for individual products, refer to the CME Group Trading Calendar online, which offers quick and easy product lookup.
Trading hours are subject to change and are in U.S. Central Time unless otherwise stated.
PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023
EQUITIES
TRADE DATE: MON 3 JULY
12:15 (CLOSED)
TRADE DATE: WED 5 JULY
16:45 (PREOPEN)
17:00 (OPEN)
TRADE DATE: WED 5 JULY
12:00 (PREOPEN) HALT
17:00 (OPEN)
TRADE DATE: WED 5 JULY
16:00 (CLOSED)
TRADE DATE: THUR 6 JULY
16:45 (PREOPEN)
17:00 (OPEN)
PREOPEN (HALT): Order Entry, modification, and cancel are allowed. No order matching.
```

- **Trading Hours - Globex Trading Hours and Holiday Schedules (page snapshot 2023-06-27)**, CME Group (trading-hours web page), grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/trading-hours.html  
  Archive: https://web.archive.org/web/20230627124824/https://www.cmegroup.com/trading-hours.html

```text
Please note that with the 2023 calendar year the CME Group will be transitioning from downloadable holiday calendars for Globex and incorporating the holiday hours into our trading hours page. ... Download a summary view of the 4th of July Holiday Hours
```

### 2024-07-03 (Wednesday), group C: halt_1215_ct

Question: Did CME Globex equity index futures (ES/MES) halt (early close) at 12:15 CT this day and reopen at 17:00 CT the same day? (information only; no bars in this stage)

Only CME source found for 2024 hours: the JSON web service behind cmegroup.com/trading-hours.html, captured 2024-07-08 (after the holiday). It names ES ('E-mini S&P 500 Futures', id 133); MES was not in the captured product set. eventDate 2024-07-03: closed 12:15 (tradingDate 2024-07-03), preopen 16:45 and open 17:00 (tradingDate 2024-07-05). The 2024 summary PDF (4th-of-july-2024.pdf / independence-day-2024.pdf) has only 404 captures. Current calendar entry: early halt 12:15 CT, inferred.

- **trading-hours-by-product JSON, fromEventDate=2024-07-03 toEventDate=2024-07-05, product 133 'E-mini S&P 500 Futures' (capture 2024-07-08 16:14:39 UTC)**, CME Group (trading-hours-by-product web service behind cmegroup.com/trading-hours.html), grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680  
  Archive: https://web.archive.org/web/20240708161439/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680

```text
"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures","id":133,"url":"/trading/equity-index/us-index/e-mini-sandp500_contract_specifications.html","tradingHours":{"schedules":[{"groupCode":"ES","eventDate":"2024-07-03","events":[{"tradingDate":"2024-07-03","eventTime":"12:15","marketEventType":"closed"},{"tradingDate":"2024-07-05","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","marketEventType":"open"}]},{"groupCode":"ES","eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","marketEventType":"open"}]},{"groupCode":"ES","eventDate":"2024-07-05","events":[{"tradingDate":"2024-07-05","eventTime":"16:00","marketEventType":"closed"}]}],"eventCount":3}
```

### 2024-07-04 (Thursday), group C: halt_1200_ct

Question: Did CME Globex equity index futures (ES/MES) trade this day with a trading halt at 12:00 CT and a 17:00 CT reopen, or was Globex fully closed? (information only; no bars in this stage)

Same JSON: ES eventDate 2024-07-04 events are preopen 12:00 and open 17:00, both tradingDate 2024-07-05. The service uses 'preopen' for the holiday halt, as the 2023 PDF does ('12:00 (PREOPEN) HALT'). Current calendar entry is FULL_CLOSURE; this CME source describes a 12:00 CT halt.

- **trading-hours-by-product JSON, fromEventDate=2024-07-03 toEventDate=2024-07-05, product 133 'E-mini S&P 500 Futures' (capture 2024-07-08 16:14:39 UTC)**, CME Group (trading-hours-by-product web service behind cmegroup.com/trading-hours.html), grade `cme_primary`, fetched in full: True.  
  Original: https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680  
  Archive: https://web.archive.org/web/20240708161439/https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected&_t=1720455278680

```text
"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures","id":133,"url":"/trading/equity-index/us-index/e-mini-sandp500_contract_specifications.html","tradingHours":{"schedules":[{"groupCode":"ES","eventDate":"2024-07-03","events":[{"tradingDate":"2024-07-03","eventTime":"12:15","marketEventType":"closed"},{"tradingDate":"2024-07-05","eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","marketEventType":"open"}]},{"groupCode":"ES","eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05","eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","marketEventType":"open"}]},{"groupCode":"ES","eventDate":"2024-07-05","events":[{"tradingDate":"2024-07-05","eventTime":"16:00","marketEventType":"closed"}]}],"eventCount":3}
```

## Searched and not found, or found and not used

- **CME clearing advisories 2022, 2023, 2024** (`20XX-4th-of-july-advisory.pdf`, fetched in full): no Globex clock times. The 'Trading:' line only points to the holiday calendar (2022) or to 'CME Group Trading Hours - CME Group' (2023, 2024). Not used as time evidence.
- **Globex holiday spreadsheets for 2023 and 2024**: none in the Wayback index under `/tools-information/holiday-calendar/files/`. The 2023 files there cover only partner exchanges (`...-compact-mgex-dme.xls`). The 2023-06-27 trading-hours page says CME moved Globex holiday hours onto that page from calendar year 2023 (quoted under 2023-07-03/04).
- **`trading-hours/files/4th-of-july-2024.pdf` and `independence-day-2024.pdf`**: only 404 captures (from 2026). No 2024 summary PDF was found; the 2024 dates rest on the JSON service capture alone.
- **CME trading-hours-by-product JSON for 2023-07-03..05** (Wayback capture 2024-07-08, fetched and decompressed): every product's `events` list is empty, so it says nothing about 2023.
- **CME investor press releases 'CME Announces Independence Day Holiday Hours'** (fetched in full): dated 2007-06-21 and 2009-06-19, so they do not apply. The 2007 release describes a '10:30 a.m. to 5:00 p.m.' equity halt on July 4, 2007. The WebSearch tool's own summary misattributed that 2007 text to 2019; it was not used.
- **2024 trading-hours page, table 'DATE AND TIME ON WHICH CME GROUP TRADING FLOOR CLOSES EARLY'** ('Wednesday, July 3, 2024 Close at 12:00 CT'): this is the Chicago trading-floor schedule, not Globex. Not used.
- **CME Globex Notices archive** (cmegroup.com/notices/electronic-trading/...): not searched, because CME's own schedule documents were found for every date.
- **Live cmegroup.com**: three original file URLs returned HTTP 403 (application/json) to curl on 2026-09-23, so no CME document was read from the live site.
- **Settlement-time PDFs** already cited in `data/cme_calendar.py`: not re-fetched. They concern settlement prices, not Globex hours.
- A first Wayback index query for the `/content/dam/...` path timed out (HTTP 504). A narrower 2024 query later succeeded and listed only advisories, no schedules.

## Fetched files (scratch copies, sha256)

Scratch directory: `/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/c39a9cf3-de81-44e4-96f7-c074621e99f7/scratchpad/calendar_check`

| File | What | sha256 |
|---|---|---|
| `sched_2019_compact.xls` | 2019 compact Globex schedule (Wayback 2022-09-20) | `8546b2a9e42c92a4bcf2d2e8209906f482467aeb549ed2a02eb95690954ddd16` |
| `zip2019/2019-independence-day-schedule.xls` | 2019 full Globex schedule, from 2019-holiday-calendars.zip | `6d8534e146a744f21f2970172ebd00ff9977ab905c6292cf1b206a4ca0a5a0fc` |
| `hc_2019.zip` | CME 2019-holiday-calendars.zip (Wayback 2021-01-26) | `1e861e355238903b013c1288f4eb9e8026e6ddd5fc1001dfd2acdbfcc1832e05` |
| `adv_2019.pdf` | 2019 clearing advisory | `8d0ccdbcfe3f8f1dd3212211fabacbd607e6a7ed77ef507690b9f643105489f9` |
| `sched_2020.xls` | 2020 full Globex schedule (Wayback 2022-07-07) | `4c107d4efaa2a97552b2f5b61bc22cf77b961a779ed92e4ad86c22238f5fdef4` |
| `adv_2020.pdf` | 2020 clearing advisory | `fedd5ef54f7fd584754b6a5154a714eaf51dbe33f492425776b12ec5d7a403b5` |
| `sched_2021_compact.xls` | 2021 compact Globex schedule (Wayback 2021-07-02) | `6444dd5b3513a79c4bce6b9db0746c969e432a3c2cdb5bb918c80ad44bf8fe9b` |
| `adv_2021.pdf` | 2021 clearing advisory | `8f8a2d1e584eb1ce61b212ccf847b556be848076a0672aa25aa556d5987c8572` |
| `sched_2022_compact.xls` | 2022 compact Globex schedule (Wayback 2022-07-04) | `11925e2a7c434e05e2e3b74df1e677cd0657629370e735a11f821871e0e91e06` |
| `sched_2022_full.xls` | 2022 full Globex schedule (Wayback 2022-07-04) | `1ea0459d8aa0fd7ec5147614855f6d0d43607efefdc3aa9c6b1e18ddbfd54fde` |
| `adv_2022.pdf` | 2022 clearing advisory (no Globex hours) | `ef0d9a25c548e803ab0b029a8194b180d0e0adc8c9d284cae6dd3188503d34d2` |
| `th_20230627.html` | cmegroup.com/trading-hours.html snapshot 2023-06-27 | `5befb1de75e7d97ba57d9e5d2b2b67e091506d40c9bc44e8e97f81e7e20d6244` |
| `th_4th_2023.pdf` | 4th-of-july-2023.pdf holiday summary (Wayback 2023-06-27) | `ccbc1f1fc39ba2219fd748372faa985798fee7eaffabf69f08956f5465a769e3` |
| `adv_2023.pdf` | 2023 clearing advisory (no Globex hours) | `342a543a690be2dac764a33f3638b579952d41ea411086b126c91a905dc89edb` |
| `thbp_2023_dec.json` | trading-hours-by-product JSON 2023-07-03..05 (empty events) | `c1ebf1a7033d79a2a0375db3eff1f495db4b1d4e76ca0ae3e63bd1255d1d9d43` |
| `thbp_2024_dec.json` | trading-hours-by-product JSON 2024-07-03..05 | `6ef0e2b055c349249f5cc7ea7c98132a31111a01ce7af028e13584c0f82d4d38` |
| `adv_2024.pdf` | 2024 clearing advisory (no Globex hours) | `827447954fc3e59c0bc597786dbc775f804ff6611ce89c0497c841b846a429d1` |

