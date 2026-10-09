# Stage E.16 Task 3b: calendars for 2010-2019 (livestock group, EC-AUC)

Worker: CalendarBuilder-OpusHigh (opus, worker-high). Built 2026-10-09 00:16-01:06 PDT.
Brief: reports/stage_e16_briefs/brief_calendars.md. No market data read. No Databento call.
No cmegroup.com page fetched, live or archived. Nothing written under data/. No commit.

Outputs:
- reports/stage_e16_calendars/hist2010_livestock.json (schema e14_hist_calendar/1, group "livestock"),
  sha256 802a4dd98a71776af58748c43c2a70772a966a2e37dd08e32fef1ebfe023ba5d
- reports/stage_e16_calendars/ec_auc_2010_2019.json (header + TREASURY_AUCTION rows in the frozen format),
  sha256 0c21ce8554698c51868451ca596549bc2940e3271dca47b2f5802ba5e54a7047
- reports/stage_e16_calendars/scripts/ (build_ec_auc.py, build_livestock.py, post_livestock.py: the scripts
  that produced both files; they read only the saved pages)
- Evidence: reports/stage_e16_briefs/pages/livestock/ (fetch_log.md) and pages/fiscaldata/ (fetch_log.md)

## (b) EC-AUC, Treasury auctions 2010-01-01..2019-06-30

Method. I read FiscalData's API documentation first and saved it. Its License and Authorization
section says: "The data is offered free, without restriction, and available to copy, adapt,
redistribute, or otherwise use for non-commercial or commercial purposes." One query, sent in JSON
and in CSV, to auctions_query with these settings:
- metadata fields only: auction_date, security_type, security_term, original_security_term, cusip,
  reopening, floating_rate, inflation_index_security, announcemt_date, closing_time_comp,
  closing_time_noncomp
- filter: auction_date 2010-01-01..2019-06-30, security_type in (Note, Bond)

The query returned 862 records. The two formats are identical record for record. I read no result
field: no yield, no bid-to-cover, no price.

Rule (E.0 C9, lines 1350-1365):
- security_type Note or Bond, floating_rate No, inflation_index_security No;
- announcemt_date strictly before auction_date;
- tenor from original_security_term;
- time_local = closing_time_comp (ET), with instant_utc computed in America/New_York.

The rows use the frozen TREASURY_AUCTION format: the same keys in the same order, the id pattern
TREASURY_AUCTION-<date>-<tenor>, and the same products, cpi and evidence values. Like the frozen
file, they include every nominal coupon tenor, reopenings included. H3 subsets them to 2, 5, 10 and
30 years.

Counts:
- 684 rows: 2Y 105, 3Y 114, 5Y 114, 7Y 123, 10Y 114, 30Y 114. No 20-year bond was auctioned in
  this period.
- Skipped: 66 FRN and 111 TIPS records.
- Excluded for a same-day announcement: 1 (the 2019-06-21 10-year reopening, 11:00 ET). It is the
  same record the frozen file excludes.
- Records with a missing required field: 0.

Per year, by tenor:

| year | 2Y | 3Y | 5Y | 7Y | 10Y | 30Y |
|---|---|---|---|---|---|---|
| 2010-2012 | 12/yr | 12/yr | 12/yr | 12/yr | 12/yr | 12/yr |
| 2013 | 12 | 12 | 10 | 14 | 12 | 12 |
| 2014 | 12 | 12 | 12 | 12 | 12 | 12 |
| 2015 | 8 | 12 | 16 | 12 | 12 | 12 |
| 2016 | 11 | 12 | 13 | 12 | 12 | 12 |
| 2017 | 10 | 12 | 11 | 15 | 12 | 12 |
| 2018 | 12 | 12 | 12 | 12 | 12 | 12 |
| 2019 (to 06-30) | 4 | 6 | 4 | 10 | 6 | 6 |

The year-to-year gaps come from keying the tenor on original_security_term. Treasury sometimes sold
a 2-year note as a reopening of an older 5-year note (9 months in 2015-2019), or a 5-year note as a
reopening of a 7-year note (6 months in 2013-2019). Those auctions carry the original term ("5Y" or "7Y"), as in the frozen
convention (L-23; the frozen 2019-05-28-7Y row is a 5-year sale of a 7-year note). So H3 maps those
2-year sales to ZF, not ZT. **This is for the lead to note, not a defect.**

Two rows share an instant: 2016-09-12, 3Y and 10Y, both with a 13:00 ET close as FiscalData
records them. They are kept as separate rows, as in the frozen file.

**2% check:** 420 records are 2-, 5-, 10- and 30-year nominal fixed-rate auctions dated
2010-06..2019-04 (2Y 98, 5Y 108, 10Y 107, 30Y 107). None was dropped for a missing field or a
same-day announcement. **Share 0.0%.**

**Overlap check, 2019-05-01..2019-06-30, against reports/stage_e2b_release_calendar.json**
(frozen sha256 839f2437...): 12 frozen rows and 12 of mine. They have the same ids, and every
field except `source` is equal, with keys in the same order. `source` differs by construction,
because each row cites its own query. **Result: exact match excluding source.**

## (a) Livestock group calendar 2010-06-01..2019-05-31 (LE, HE)

### Sources and grades

The brief forbids CME pages, live or archived. So the CME documents used here are copies hosted by
third parties: the CFTC, and the brokers Dorman Trading and Cannon Trading. Grades:

- **"cme"**: CME self-certifications fetched from cftc.gov. These are Submission 14-408 (Oct 2014
  hours cut), Submission 16-064 (Feb 2016 hours), the June 2015 livestock-options floor-hours filing
  and Submission 08-159 (Friday close 1:55 p.m. from 2008-10-24).
- **"secondary"**: one of the following.
  - CME holiday schedules and floor holiday cards re-hosted by Dorman Trading (2010-2014; 41 PDFs).
  - Cannon Trading posts: text in 2011-2016, schedule-table images in 2016-2019 that I read
    visually (no OCR tool is installed).
  - FIA's and AMP Futures' notices for 2018-12-05.
  - NYSE holiday lists, from Wayback captures, used for 2015-2019 as the universe of holidays.

  The precedent for this grade is data/calendars/livestock.py, which grades an AMP Futures image of
  a CME schedule "secondary".
- **"unverified"**: the QuantConnect LEAN vendor table. I used it only as a cross-check. It
  disagrees with the documents several times; for example, it gives 12:15 for 2011-11-25, where two
  documents say 12:00.

Every text quote in the file is extracted from the saved page text by regex, so it is verbatim.
Image quotes are marked "[transcribed from image]".

### Sessions (three eras)

**Era 1, 2010-06-01..2014-10-24, graded secondary.**
- Segment: 17:00 CT on the prior day to 16:00. This follows Submission 14-408's "current" hours:
  "Monday 9:05 a.m. ... Opening", "Daily trading halts 4:00 p.m. - 5:00 p.m. CT", "Friday 1:55 p.m.
  CT- Close".
- No CME filing dates this structure to 2010. The 2010-2013 schedules corroborate it (evening
  reopenings at 1700 CT; livestock "closed until their regularly scheduled open on Monday").
- day_session_ct is (09:05, 13:00): the open-outcry open and the end of the settlement period.

**Era 2, 2014-10-27..2016-02-26, graded cme.**
- 14-408 hours "as of Monday, October 27": Monday 09:05-16:00, Tuesday-Thursday 08:00-16:00, Friday
  08:00-13:55. Submission 16-064 confirms them as "current" in Feb 2016.
- day_session_ct is (08:00, 13:00).
- In June 2015 CME filed: "The opening at 9:05 a.m. CT on the first business day of the week
  (usually Monday but Monday holidays will change this to Tuesday) shall remain unchanged."

**Era 3, 2016-02-29..2019-05-31, graded cme.**
- 16-064: CME Globex "Mon – Fri: 8:30 am – 1:05 pm", effective 2016-02-29.
- day_session_ct is (08:30, 13:00), which equals the frozen livestock.py.
- 16-064 says "The daily settlement period and procedures for the Contracts shall remain unchanged."

Weekday-dependent hours do not fit SessionSpec:
- **Mondays (eras 1-2):** 268 regular Mondays are late_open entries at 09:05. In era 1 they are
  status secondary and time inferred; in era 2 both grades are cme.
- **Post-holiday 09:05 opens:** 27 more late_open entries, each sourced. One of them, 2017-01-17,
  has time unverified (see the judgment calls).
- **Friday 13:55 closes and the era-1 Sunday gap:** not entries. They are left to E.17.

### Counts (from data.hist_calendar.parse_hist_calendar on a scratch copy)

2349 weekdays and 2274 trade dates. There are 75 full closures, 26 early halts and 295 late opens.
3 entries have time unverified, and 25 dates are unsourced.

| year | trade dates | closures | early halts | late opens | unsourced |
|---|---|---|---|---|---|
| 2010 (Jun-Dec) | 150 | 4 | 2 | 28 | 0 |
| 2011 | 252 | 8 | 1 | 49 | 0 |
| 2012 | 252 | 9 | 3 | 54 | 0 |
| 2013 | 253 | 8 | 4 | 54 | 3 |
| 2014 | 255 | 6 | 3 | 50 | 12 |
| 2015 | 253 | 8 | 5 | 51 | 4 |
| 2016 | 252 | 9 | 2 | 8 | 2 |
| 2017 | 251 | 9 | 3 | 1 | 2 |
| 2018 | 252 | 9 | 3 | 0 | 2 |
| 2019 (Jan-May) | 104 | 5 | 0 | 0 | 0 |

Unsourced trade dates are counted as trade dates in this table, because the loader excludes them.
That is also why 2013 and 2014 show fewer closures: their unsourced holidays are not recorded as
closures.

### 2% check (unsourced share)

| window | weekdays | unsourced | share of weekdays | share of trade dates |
|---|---|---|---|---|
| coverage 2010-06-01..2019-05-31 | 2349 | 25 | **1.06%** | 1.10% |
| E.14 window 2010-06-07..2019-04-30 | 2322 | 25 | 1.08% | 1.11% |
| LE window (U2) 2010-07-01..2019-04-30 | 2304 | 25 | 1.09% | 1.12% |
| HE window (U2) 2017-07-03..2019-04-30 | 477 | 4 | 0.84% | 0.87% |

**All four windows pass the 2% rule as built.** The 25 unsourced dates are:

| year | dates | what is missing |
|---|---|---|
| 2013 | 01-21, 01-22 | MLK Day and the day after |
| 2013 | 10-14 | Columbus Day |
| 2014 | 04-08 | Globex agricultural outage: an early halt at 12:38 CT, status unverified (see the judgment calls) |
| 2014 | 08-25 | Monday after the Sunday-evening Globex outage |
| 2014 | 09-01, 09-02 | Labor Day and the day after |
| 2014 | 10-13, 11-11 | Columbus and Veterans Days |
| 2014 | 11-27, 11-28 | Thanksgiving and the day after |
| 2014 | 12-24, 12-25, 12-26, 12-31 | Christmas and New Year's Eve |
| 2015 | 01-01, 01-02 | New Year |
| 2015-2018 | 2015-10-12, 2015-11-11, 2016-10-10, 2016-11-11, 2017-10-09, 2017-11-10, 2018-10-08, 2018-11-12 | Columbus and Veterans Days. Livestock traded normally on these days in 2010-2013, but no saved source covers these years. |

Sensitivity (reported, not hidden):
- **If the lead rules that the Dorman-hosted CME PDFs are "mirrors" under brief_common.md:** 722
  dates are unsourced (30.7%), because 2010-2012 lose their year lists. **This fails the 2% rule.**
- **If the image transcriptions are not accepted:** 61 dates are unsourced (2.60%). **This fails the
  2% rule.**

### 2019-05 overlap with the frozen data/calendars/livestock.py

The frozen module's sha256 is 57727e68.... Its May 2019 entries are 2019-05-27 FULL_CLOSURE, and
mine are the same. Neither has a late open in May 2019. Segments are equal (08:30-13:05), and
day_session_ct is equal ((08:30, 13:00)). **Result: they agree.**

### Unscheduled-event check

- **Hurricane Sandy, 2012-10-29/30:** livestock regular. Cannon's posts say the closures were limited
  to stock index and interest-rate products. Graded secondary, but the evidence is implicit.
- **2018-12-05, national day of mourning:** regular. FIA: "All other US futures markets will open as
  usual". AMP: "All other markets on CME Globex ... will remain open for regular trading hours".
- **2014-04-08 Globex agricultural outage:** recorded as an early halt at 12:38 CT, status
  unverified, so the date is unsourced. Details are in the judgment calls.
- **2014-08-24/25 Sunday Globex outage:** 08-25 is listed unsourced.

I ran WebSearch for other livestock halts in 2010-2019 and found none.

## Deviations and judgment calls (for the lead)

1. **Grades.** Grades follow the scheme under "Sources and grades". The two sensitivity results
   above show what changes if the lead does not accept that scheme.
2. **Year coverage for 2013 and 2014.** I found no full-year holiday list outside CME's site. I
   assumed the standard holiday set that every other year's list shows. Every candidate date that
   has no sourced statement is listed unsourced.
3. **Thursday 13:55 closes are early halts.** The 13:55 closes before Good Friday (2012-2015) and on
   2015-12-31 are recorded as early halts, because CME calls them "Early Close". They are after the
   13:00 settlement, but lead spec section 2 still excludes them.
4. **2012-07-03 is recorded as a regular Globex day.** CME's Globex schedule (updated 6/18/2012) says
   regular close. The 2012 floor card (late 2011) says commodities closed at 12:00 on the floor. The
   settlement minute that day may have followed the floor.
5. **Early-close minutes for 2010-12-31 and 2012-12-24.** Both statuses come from floor cards, which
   give 12:00 on the floor. For 2010-12-31 I used 12:00, time unverified; the LEAN table has 12:15.
   For 2012-12-24 I used 12:15, time inferred from the 2012 Thanksgiving Globex schedule.
6. **2011-09-06: two sources disagree.** Cannon's text lists livestock as reopening at 5:00 pm
   Monday. CME's schedule says 0905 CT Tuesday. I followed CME's schedule.
7. **2017-01-17 late open at 09:05.** Cannon's MLK 2017 table shows a 09:05 Tuesday open, which
   conflicts with the 08:30 open in force. I kept it with time unverified (conservative).
8. **H4's O_p in era 2 is a lead call.** day_session_ct uses 08:00 (the Globex open), but the futures
   pit opened at 09:05 until 2015-07-02.
9. **The 2014-04-08 outage is recorded on unsaved reports.** Reuters and Bloomberg (seen only in
   search results) say livestock was halted from about 12:38 CT and restarted about 14:30 CT. The
   only saved source is the CFTC-hosted Nadex filing, which covers corn only. I recorded an early
   halt at 12:38 with status unverified.
10. **Process slips (logged in fetch_log.md):**
    - One Farm Media page (agcanada.com) was fetched before I read its terms. The terms forbid
      automated copying, so the page was deleted and not used.
    - The FIA and AMP pages were fetched seconds before their terms pages were read. Neither terms
      page forbids automated access.

## Notes for E.17

- **Loading the livestock file.** data.hist_calendar.parse_hist_calendar(raw, "livestock", path)
  accepts the file as is. load_hist_group_calendar("livestock") refuses, because HIST_GROUPS is
  hardcoded to six groups and hist_calendar_path checks it. E.17 must add "livestock" to HIST_GROUPS
  and copy the file to data/calendars/hist2010/livestock.json. GROUP_OF_PRODUCT already maps HE and
  LE to livestock.
- **Weekday-dependent hours in eras 1-2.** Bar checks must allow:
  - no bars from 13:55 to 16:00 CT on Fridays;
  - no Sunday-evening session in era 1;
  - Monday 09:05 opens, which are already late_open entries.
- **H4's entry minute.** H4 should take max(O_p, open_ct) on late-open dates. Late opens are not
  exclusions under lead spec section 2.
- **EC-AUC same-instant rows.** Two rows share an instant (2016-09-12). Handle them as the frozen
  file's same-instant convention does.

## Anything not finished

- **Unsourced livestock dates.** 25 remain, listed above. Their sources are on CME's own site, or on
  sites whose terms forbid copying (Farm Media, thepigsite) or whose robots.txt blocks Claude
  (kyfb.com).
- **The Labor Day 2014 image is unreachable.** Cannon's Labor Day 2014 schedule image no longer
  loads, and Wayback returns a 404.
- **Columbus and Veterans Days 2013-2018 have no saved statement.** One exception: Veterans Day
  2013, from Dorman.

## F-04 announcement dates (lead follow-up, 2026-10-09 01:4x PDT)

What was done:
- **New fields on the 2010-2019 rows.** Every row of ec_auc_2010_2019.json now carries announcemt_date,
  original_security_term, security_term, security_type, floating_rate, inflation_index_security and
  cusip. The values come from the saved CSV (F5); there was no new fetch.
- **Existing content unchanged.** The new fields are appended after `source`. Every existing key and
  value is unchanged: checked against the previous file, 684 of 684 rows. The header gains
  `f04_fields`, and all 684 rows have all 7 fields.
- **Overlap check still passes.** It now compares the frozen keys only; the result is still an exact
  match excluding `source`.
- **Reproducible.** Re-running scripts/build_ec_auc.py writes the identical file (sha256 e3b5f452...,
  rerun checked).
- **New fetch for 2019-2024.** I fetched FiscalData auctions_query for auction dates 2019-05-01..2024-03-31
  with the same 11 metadata fields (2026-10-09T08:49:19-20Z UTC). It returned 524 records, identical
  in JSON and CSV. Both are saved under pages/fiscaldata/ and logged in fetch_log.md (F7, F8).
- **The announcements file.** reports/stage_e16_calendars/ec_auc_announcements_2019_2024.json (sha256
  78e68a58...) holds one row per frozen TREASURY_AUCTION row of 2019-05-01..2024-02-29 with tenor
  2/5/10/30Y: 231 rows (2Y 58, 5Y 56, 10Y 59, 30Y 58).
- **Match rule.** Frozen id `TREASURY_AUCTION-<YYYY-MM-DD>-<N>Y`, with N taken from
  original_security_term, matched to the FiscalData record that has the same auction_date and
  original term after the E.0 filter.
- **Match result.** No frozen row is unmatched and no match is ambiguous. One FiscalData record in
  the window has no frozen row: the same-day-announced 2019-06-21 10Y reopening, which the frozen
  file excludes.
- **Scripts.** scripts/build_ec_auc_announcements.py builds the file and the counts below
  (f04_t3_counts.json, sha256 76be916d...), including every after-t-3 id.

How t-3 is defined:
- t-3 is the third rates-group trade date before the auction date t.
- A trade date is a weekday that is not a FULL_CLOSURE.
- Up to 2019-04-30 the calendar is data/calendars/hist2010/rates.json (sha256 099ac84e..., 0 unsourced
  dates). From 2019-05-01 it is data/calendars/rates.py (sha256 449c1529...). The two agree on the
  May 2019 closures.
- Every auction date is a rates trade date.

Counts are for 2-, 5-, 10- and 30-year rows after the E.0 filter. "After" means announcemt_date > t-3.

| period | tenor | after t-3 | on t-3 | before t-3 | n |
|---|---|---|---|---|---|
| 2010-06..2019-04 | 2Y | 37 | 59 | 2 | 98 |
| | 5Y | 6 | 37 | 65 | 108 |
| | 10Y | 6 | 9 | 92 | 107 |
| | 30Y | 0 | 6 | 101 | 107 |
| | **all** | **49** | **111** | **260** | **420** |
| 2019-05..2024-02 | 2Y | 26 | 32 | 0 | 58 |
| | 5Y | 14 | 12 | 30 | 56 |
| | 10Y | 6 | 8 | 45 | 59 |
| | 30Y | 0 | 6 | 52 | 58 |
| | **all** | **46** | **58** | **127** | **231** |

Under the amended H3 rule (announced on or before t-3), the following would be dropped:
- 2010-06..2019-04: 49 of 420 auctions (11.7%).
- 2019-05..2024-02: 46 of 231 auctions (19.9%).

The drops are mostly 2-year auctions. A typical case is a Monday auction announced the Thursday
before, which is t-2 (for example 2019-11-25, announced 2019-11-21, with t-3 = 2019-11-20).

Paths note: this follow-up arrived with a session working directory in a stale git worktree
(.claude/worktrees/agent-ae6594a41ca6ced74, at commit be01890), which does not contain this stage's
untracked outputs. I therefore read and wrote the main checkout's reports/ paths named in the
request, using absolute paths. Nothing was written to the worktree or under data/.
