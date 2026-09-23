"""Scheduled macro releases 2019-05-01..2024-02-29 for E-H1 and E-H2 (Stage D.1f, list 5.7).

``RELEASE_TABLE_2019_2024`` has the same shape as
``strategy.research.e_calendar_event.h1_scheduled_macro_drift.RELEASE_TABLE_ET``: one entry
per release trade date, mapped to its tz-aware America/New_York release datetime. The D.1f
confirmation factories (list 2.1 A1, NEW-1) pass
``RELEASE_TABLE_ET | RELEASE_TABLE_2019_2024``; the two tables share no key.

Contents, following the hashed module's own conventions:
- Regularly scheduled FOMC statement releases at 2:00pm ET, from the Federal Reserve's
  historical FOMC pages (fomchistorical2019.htm, fomchistorical2020.htm) and, for 2021-2024,
  fomccalendars.htm. Unscheduled actions are excluded (the hashed module's "regularly
  scheduled" convention): the 2019-10-04 unscheduled call, the 2020-03-02 and 2020-03-15
  unscheduled meetings, and the 2020-03-19, 2020-03-23, 2020-03-31 and 2020-08-27 notation
  votes. The regularly scheduled 2020-03-17/18 meeting was cancelled, so it has no entry.
- CPI and Employment Situation (NFP) releases at 8:30am ET, from the BLS schedule pages
  (bls.gov/schedule/<year>/home.htm for 2019-2023; the 2024 January and February month views).
  Where a release moved, the date actually published is used (NFP 2020-07-02, moved earlier
  for the July 4 holiday).

Every entry cites its source: ``SOURCES[d]`` holds the URL and the verbatim quote that
reports/stage_d1f_release_sources.json (the verified extraction) records for it. The
extraction marked no entry unverified; an entry without a quote would carry "[unverified]".

Collision ruling (the Stage D.1f lead): two dates carry both an FOMC statement and a CPI
release. The table holds one release per trade date, and E-H1's pre-announcement window
ends at the day's first release, so the EARLIEST release (CPI, 08:30 ET) is kept on both.
The dropped FOMC entries are listed in ``DROPPED_RELEASES``:
- 2019-12-11 FOMC 14:00 ET (December 10-11, 2019 meeting), dropped for CPI 08:30 ET.
- 2020-06-10 FOMC 14:00 ET (June 9-10, 2020 meeting), dropped for CPI 08:30 ET.
Any other duplicate date raises, as the hashed builder's does.

Counts: 37 FOMC statements in the extraction (reports/stage_d1f_release_sources.md prints
38 in its heading, but its own 2020 row holds 6 in-window dates; the JSON has 37), less the
2 dropped = 35; 58 CPI; 58 NFP; 151 entries in total.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from types import MappingProxyType
from zoneinfo import ZoneInfo

ET_TZ = ZoneInfo("America/New_York")
WINDOW_FIRST = date(2019, 5, 1)
WINDOW_LAST = date(2024, 2, 29)

FOMC = "FOMC"
CPI = "CPI"
NFP = "NFP"
RELEASE_TIME_ET: dict[str, time] = {FOMC: time(14, 0), CPI: time(8, 30), NFP: time(8, 30)}

# The lead's ruling: on these dates the kept release is the one of this kind (the earliest).
RULED_COLLISIONS: dict[date, str] = {date(2019, 12, 11): CPI, date(2020, 6, 10): CPI}

_FED_2019 = "https://www.federalreserve.gov/monetarypolicy/fomchistorical2019.htm"
_FED_2020 = "https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm"
_FED_CALENDARS = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
_BLS_2019 = "https://www.bls.gov/schedule/2019/home.htm"
_BLS_2020 = "https://www.bls.gov/schedule/2020/home.htm"
_BLS_2021 = "https://www.bls.gov/schedule/2021/home.htm"
_BLS_2022 = "https://www.bls.gov/schedule/2022/home.htm"
_BLS_2023 = "https://www.bls.gov/schedule/2023/home.htm"
_BLS_2024_01 = "https://www.bls.gov/schedule/2024/01_sched.htm"
_BLS_2024_02 = "https://www.bls.gov/schedule/2024/02_sched.htm"


@dataclass(frozen=True)
class ReleaseSource:
    """One release as the extraction records it: date, kind, source URL, verbatim quote."""

    release_date: date
    kind: str
    url: str
    quote: str
    note: str = ""

    @property
    def release_et(self) -> datetime:
        return datetime.combine(self.release_date, RELEASE_TIME_ET[self.kind], tzinfo=ET_TZ)


_Src = ReleaseSource

# Every release of reports/stage_d1f_release_sources.json, in date order.
_RELEASES: tuple[ReleaseSource, ...] = (
    _Src(date(2019, 5, 1), FOMC, _FED_2019,
        '##### April/May 30-1 Meeting - 2019 ... '
        '[Statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary2019'
        '0501a.htm)',
        note='second day of two-day meeting; also carries an NFP release the same window (May '
        '3) but not same-day'),
    _Src(date(2019, 5, 3), NFP, _BLS_2019,
        '| Friday, May 03, 2019 | 08:30 AM | **Employment Situation** for April 2019 |'),
    _Src(date(2019, 5, 10), CPI, _BLS_2019,
        '| Friday, May 10, 2019 | 08:30 AM | **Consumer Price Index** for April 2019 |'),
    _Src(date(2019, 6, 7), NFP, _BLS_2019,
        '| Friday, June 07, 2019 | 08:30 AM | **Employment Situation** for May 2019 |'),
    _Src(date(2019, 6, 12), CPI, _BLS_2019,
        '| Wednesday, June 12, 2019 | 08:30 AM | **Consumer Price Index** for May 2019 |'),
    _Src(date(2019, 6, 19), FOMC, _FED_2019,
        '##### June 18-19 Meeting - 2019 ... '
        '[Statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary2019'
        '0619a.htm)'),
    _Src(date(2019, 7, 5), NFP, _BLS_2019,
        '| Friday, July 05, 2019 | 08:30 AM | **Employment Situation** for June 2019 |'),
    _Src(date(2019, 7, 11), CPI, _BLS_2019,
        '| Thursday, July 11, 2019 | 08:30 AM | **Consumer Price Index** for June 2019 |'),
    _Src(date(2019, 7, 31), FOMC, _FED_2019,
        '##### July 30-31 Meeting - 2019 ... '
        '[Statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary2019'
        '0731a.htm)'),
    _Src(date(2019, 8, 2), NFP, _BLS_2019,
        '| Friday, August 02, 2019 | 08:30 AM | **Employment Situation** for July 2019 |'),
    _Src(date(2019, 8, 13), CPI, _BLS_2019,
        '| Tuesday, August 13, 2019 | 08:30 AM | **Consumer Price Index** for July 2019 |'),
    _Src(date(2019, 9, 6), NFP, _BLS_2019,
        '| Friday, September 06, 2019 | 08:30 AM | **Employment Situation** for August '
        '2019 |'),
    _Src(date(2019, 9, 12), CPI, _BLS_2019,
        '| Thursday, September 12, 2019 | 08:30 AM | **Consumer Price Index** for August '
        '2019 |'),
    _Src(date(2019, 9, 18), FOMC, _FED_2019,
        '##### September 17-18 Meeting - 2019 ... '
        '[Statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary2019'
        '0918a.htm)'),
    _Src(date(2019, 10, 4), NFP, _BLS_2019,
        '| Friday, October 04, 2019 | 08:30 AM | **Employment Situation** for September '
        '2019 |'),
    _Src(date(2019, 10, 10), CPI, _BLS_2019,
        '| Thursday, October 10, 2019 | 08:30 AM | **Consumer Price Index** for '
        'September 2019 |'),
    _Src(date(2019, 10, 30), FOMC, _FED_2019,
        '##### October 29-30 Meeting - 2019 ... '
        '[Statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary2019'
        '1030a.htm)'),
    _Src(date(2019, 11, 1), NFP, _BLS_2019,
        '| Friday, November 01, 2019 | 08:30 AM | **Employment Situation** for October '
        '2019 |'),
    _Src(date(2019, 11, 13), CPI, _BLS_2019,
        '| Wednesday, November 13, 2019 | 08:30 AM | **Consumer Price Index** for '
        'October 2019 |'),
    _Src(date(2019, 12, 6), NFP, _BLS_2019,
        '| Friday, December 06, 2019 | 08:30 AM | **Employment Situation** for November '
        '2019 |'),
    _Src(date(2019, 12, 11), CPI, _BLS_2019,
        '| Wednesday, December 11, 2019 | 08:30 AM | **Consumer Price Index** for '
        'November 2019 |',
        note='COLLISION: same date as FOMC statement release'),
    _Src(date(2019, 12, 11), FOMC, _FED_2019,
        '##### December 10-11 Meeting - 2019 ... '
        '[Statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary2019'
        '1211a.htm)',
        note='COLLISION: same date as CPI release for November 2019 data'),
    _Src(date(2020, 1, 10), NFP, _BLS_2020,
        '| Friday, January 10, 2020 | 08:30 AM | **Employment Situation** for December '
        '2019 |'),
    _Src(date(2020, 1, 14), CPI, _BLS_2020,
        '| Tuesday, January 14, 2020 | 08:30 AM | **Consumer Price Index** for December '
        '2019 |'),
    _Src(date(2020, 2, 7), NFP, _BLS_2020,
        '| Friday, February 07, 2020 | 08:30 AM | **Employment Situation** for January '
        '2020 |'),
    _Src(date(2020, 2, 13), CPI, _BLS_2020,
        '| Thursday, February 13, 2020 | 08:30 AM | **Consumer Price Index** for January '
        '2020 |'),
    _Src(date(2020, 3, 6), NFP, _BLS_2020,
        '| Friday, March 06, 2020 | 08:30 AM | **Employment Situation** for February '
        '2020 |'),
    _Src(date(2020, 3, 11), CPI, _BLS_2020,
        '| Wednesday, March 11, 2020 | 08:30 AM | **Consumer Price Index** for February '
        '2020 |'),
    _Src(date(2020, 4, 3), NFP, _BLS_2020,
        '| Friday, April 03, 2020 | 08:30 AM | **Employment Situation** for March 2020 |'),
    _Src(date(2020, 4, 10), CPI, _BLS_2020,
        '| Friday, April 10, 2020 | 08:30 AM | **Consumer Price Index** for March 2020 |'),
    _Src(date(2020, 4, 29), FOMC, _FED_2020,
        '##### April 28-29 Meeting - 2020 ... '
        '[Statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary2020'
        '0429a.htm)'),
    _Src(date(2020, 5, 8), NFP, _BLS_2020,
        '| Friday, May 08, 2020 | 08:30 AM | **Employment Situation** for April 2020 |'),
    _Src(date(2020, 5, 12), CPI, _BLS_2020,
        '| Tuesday, May 12, 2020 | 08:30 AM | **Consumer Price Index** for April 2020 |'),
    _Src(date(2020, 6, 5), NFP, _BLS_2020,
        '| Friday, June 05, 2020 | 08:30 AM | **Employment Situation** for May 2020 |'),
    _Src(date(2020, 6, 10), CPI, _BLS_2020,
        '| Wednesday, June 10, 2020 | 08:30 AM | **Consumer Price Index** for May 2020 |',
        note='COLLISION: same date as FOMC statement release'),
    _Src(date(2020, 6, 10), FOMC, _FED_2020,
        '##### June 9-10 Meeting - 2020 ... '
        '[Statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary2020'
        '0610a.htm)',
        note='COLLISION: same date as CPI release for May 2020 data'),
    _Src(date(2020, 7, 2), NFP, _BLS_2020,
        '| Thursday, July 02, 2020 | 08:30 AM | **Employment Situation** for June 2020 |',
        note='moved earlier due to July 4 Independence Day holiday'),
    _Src(date(2020, 7, 14), CPI, _BLS_2020,
        '| Tuesday, July 14, 2020 | 08:30 AM | **Consumer Price Index** for June 2020 |'),
    _Src(date(2020, 7, 29), FOMC, _FED_2020,
        '##### July 28-29 Meeting - 2020 ... '
        '[Statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary2020'
        '0729a.htm)'),
    _Src(date(2020, 8, 7), NFP, _BLS_2020,
        '| Friday, August 07, 2020 | 08:30 AM | **Employment Situation** for July 2020 |'),
    _Src(date(2020, 8, 12), CPI, _BLS_2020,
        '| Wednesday, August 12, 2020 | 08:30 AM | **Consumer Price Index** for July '
        '2020 |'),
    _Src(date(2020, 9, 4), NFP, _BLS_2020,
        '| Friday, September 04, 2020 | 08:30 AM | **Employment Situation** for August '
        '2020 |'),
    _Src(date(2020, 9, 11), CPI, _BLS_2020,
        '| Friday, September 11, 2020 | 08:30 AM | **Consumer Price Index** for August '
        '2020 |'),
    _Src(date(2020, 9, 16), FOMC, _FED_2020,
        '##### September 15-16 Meeting - 2020 ... '
        '[Statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary2020'
        '0916a.htm)'),
    _Src(date(2020, 10, 2), NFP, _BLS_2020,
        '| Friday, October 02, 2020 | 08:30 AM | **Employment Situation** for September '
        '2020 |'),
    _Src(date(2020, 10, 13), CPI, _BLS_2020,
        '| Tuesday, October 13, 2020 | 08:30 AM | **Consumer Price Index** for September '
        '2020 |'),
    _Src(date(2020, 11, 5), FOMC, _FED_2020,
        '##### November 4-5 Meeting - 2020 ... '
        '[Statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary2020'
        '1105a.htm)'),
    _Src(date(2020, 11, 6), NFP, _BLS_2020,
        '| Friday, November 6, 2020 | 08:30 AM | **Employment Situation** for October '
        '2020 |'),
    _Src(date(2020, 11, 12), CPI, _BLS_2020,
        '| Thursday, November 12, 2020 | 08:30 AM | **Consumer Price Index** for October '
        '2020 |'),
    _Src(date(2020, 12, 4), NFP, _BLS_2020,
        '| Friday, December 4, 2020 | 08:30 AM | **Employment Situation** for November '
        '2020 |'),
    _Src(date(2020, 12, 10), CPI, _BLS_2020,
        '| Thursday, December 10, 2020 | 08:30 AM | **Consumer Price Index** for '
        'November 2020 |'),
    _Src(date(2020, 12, 16), FOMC, _FED_2020,
        '##### December 15-16 Meeting - 2020 ... '
        '[Statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary2020'
        '1216a.htm)'),
    _Src(date(2021, 1, 8), NFP, _BLS_2021,
        '| Friday, January 8, 2021 | 08:30 AM | **Employment Situation** for December '
        '2020 |'),
    _Src(date(2021, 1, 13), CPI, _BLS_2021,
        '| Wednesday, January 13, 2021 | 08:30 AM | **Consumer Price Index** for '
        'December 2020 |'),
    _Src(date(2021, 1, 27), FOMC, _FED_CALENDARS,
        '#### 2021 FOMC Meetings\n\n**January**\n\n26-27\n\n**Statement:**\n\n'
        '[PDF](https://www.federalreserve.gov/monetarypolicy/files/monetary20210127a1.pdf'
        ') | '
        '[HTML](https://www.federalreserve.gov/newsevents/pressreleases/monetary20210127a'
        '.htm)'),
    _Src(date(2021, 2, 5), NFP, _BLS_2021,
        '| Friday, February 5, 2021 | 08:30 AM | **Employment Situation** for January '
        '2021 |'),
    _Src(date(2021, 2, 10), CPI, _BLS_2021,
        '| Wednesday, February 10, 2021 | 08:30 AM | **Consumer Price Index** for '
        'January 2021 |'),
    _Src(date(2021, 3, 5), NFP, _BLS_2021,
        '| Friday, March 5, 2021 | 08:30 AM | **Employment Situation** for February 2021 '
        '|'),
    _Src(date(2021, 3, 10), CPI, _BLS_2021,
        '| Wednesday, March 10, 2021 | 08:30 AM | **Consumer Price Index** for February '
        '2021 |'),
    _Src(date(2021, 3, 17), FOMC, _FED_CALENDARS,
        '**March**\n\n16-17\\* ... **Statement:** ... monetary20210317a.htm'),
    _Src(date(2021, 4, 2), NFP, _BLS_2021,
        '| Friday, April 2, 2021 | 08:30 AM | **Employment Situation** for March 2021 |'),
    _Src(date(2021, 4, 13), CPI, _BLS_2021,
        '| Tuesday, April 13, 2021 | 08:30 AM | **Consumer Price Index** for March 2021 |'),
    _Src(date(2021, 4, 28), FOMC, _FED_CALENDARS,
        '**April**\n\n27-28 ... **Statement:** ... monetary20210428a.htm'),
    _Src(date(2021, 5, 7), NFP, _BLS_2021,
        '| Friday, May 07, 2021 | 08:30 AM | **Employment Situation** for April 2021 |'),
    _Src(date(2021, 5, 12), CPI, _BLS_2021,
        '| Wednesday, May 12, 2021 | 08:30 AM | **Consumer Price Index** for April 2021 |'),
    _Src(date(2021, 6, 4), NFP, _BLS_2021,
        '| Friday, June 04, 2021 | 08:30 AM | **Employment Situation** for May 2021 |'),
    _Src(date(2021, 6, 10), CPI, _BLS_2021,
        '| Thursday, June 10, 2021 | 08:30 AM | **Consumer Price Index** for May 2021 |'),
    _Src(date(2021, 6, 16), FOMC, _FED_CALENDARS,
        '**June**\n\n15-16\\* ... **Statement:** ... monetary20210616a.htm'),
    _Src(date(2021, 7, 2), NFP, _BLS_2021,
        '| Friday, July 2, 2021 | 08:30 AM | **Employment Situation** for June 2021 |'),
    _Src(date(2021, 7, 13), CPI, _BLS_2021,
        '| Tuesday, July 13, 2021 | 08:30 AM | **Consumer Price Index** for June 2021 |'),
    _Src(date(2021, 7, 28), FOMC, _FED_CALENDARS,
        '**July**\n\n27-28 ... **Statement:** ... monetary20210728a.htm'),
    _Src(date(2021, 8, 6), NFP, _BLS_2021,
        '| Friday, August 6, 2021 | 08:30 AM | **Employment Situation** for July 2021 |'),
    _Src(date(2021, 8, 11), CPI, _BLS_2021,
        '| Wednesday, August 11, 2021 | 08:30 AM | **Consumer Price Index** for July '
        '2021 |'),
    _Src(date(2021, 9, 3), NFP, _BLS_2021,
        '| Friday, September 3, 2021 | 08:30 AM | **Employment Situation** for August '
        '2021 |'),
    _Src(date(2021, 9, 14), CPI, _BLS_2021,
        '| Tuesday, September 14, 2021 | 08:30 AM | **Consumer Price Index** for August '
        '2021 |'),
    _Src(date(2021, 9, 22), FOMC, _FED_CALENDARS,
        '**September**\n\n21-22\\* ... **Statement:** ... monetary20210922a.htm'),
    _Src(date(2021, 10, 8), NFP, _BLS_2021,
        '| Friday, October 8, 2021 | 08:30 AM | **Employment Situation** for September '
        '2021 |'),
    _Src(date(2021, 10, 13), CPI, _BLS_2021,
        '| Wednesday, October 13, 2021 | 08:30 AM | **Consumer Price Index** for '
        'September 2021 |'),
    _Src(date(2021, 11, 3), FOMC, _FED_CALENDARS,
        '**November**\n\n2-3 ... **Statement:** ... monetary20211103a.htm'),
    _Src(date(2021, 11, 5), NFP, _BLS_2021,
        '| Friday, November 05, 2021 | 08:30 AM | **Employment Situation** for October '
        '2021 |'),
    _Src(date(2021, 11, 10), CPI, _BLS_2021,
        '| Wednesday, November 10, 2021 | 08:30 AM | **Consumer Price Index** for '
        'October 2021 |'),
    _Src(date(2021, 12, 3), NFP, _BLS_2021,
        '| Friday, December 3, 2021 | 08:30 AM | **Employment Situation** for November '
        '2021 |'),
    _Src(date(2021, 12, 10), CPI, _BLS_2021,
        '| Friday, December 10, 2021 | 08:30 AM | **Consumer Price Index** for November '
        '2021 |'),
    _Src(date(2021, 12, 15), FOMC, _FED_CALENDARS,
        '**December**\n\n14-15\\* ... **Statement:** ... monetary20211215a.htm'),
    _Src(date(2022, 1, 7), NFP, _BLS_2022,
        '| Friday, January 07, 2022 | 08:30 AM | **Employment Situation** for December '
        '2021 |'),
    _Src(date(2022, 1, 12), CPI, _BLS_2022,
        '| Wednesday, January 12, 2022 | 08:30 AM | **Consumer Price Index** for '
        'December 2021 |'),
    _Src(date(2022, 1, 26), FOMC, _FED_CALENDARS,
        '#### 2022 FOMC Meetings\n\n**January**\n\n25-26 ... **Statement:** ... '
        'monetary20220126a.htm'),
    _Src(date(2022, 2, 4), NFP, _BLS_2022,
        '| Friday, February 04, 2022 | 08:30 AM | **Employment Situation** for January '
        '2022 |'),
    _Src(date(2022, 2, 10), CPI, _BLS_2022,
        '| Thursday, February 10, 2022 | 08:30 AM | **Consumer Price Index** for January '
        '2022 |'),
    _Src(date(2022, 3, 4), NFP, _BLS_2022,
        '| Friday, March 4, 2022 | 08:30 AM | **Employment Situation** for February 2022 '
        '|'),
    _Src(date(2022, 3, 10), CPI, _BLS_2022,
        '| Thursday, March 10, 2022 | 08:30 AM | **Consumer Price Index** for February '
        '2022 |'),
    _Src(date(2022, 3, 16), FOMC, _FED_CALENDARS,
        '**March**\n\n15-16\\* ... **Statement:** ... monetary20220316a.htm'),
    _Src(date(2022, 4, 1), NFP, _BLS_2022,
        '| Friday, April 1, 2022 | 08:30 AM | **Employment Situation** for March 2022 |'),
    _Src(date(2022, 4, 12), CPI, _BLS_2022,
        '| Tuesday, April 12, 2022 | 08:30 AM | **Consumer Price Index** for March 2022 |'),
    _Src(date(2022, 5, 4), FOMC, _FED_CALENDARS,
        '**May**\n\n3-4 ... **Statement:** ... monetary20220504a.htm'),
    _Src(date(2022, 5, 6), NFP, _BLS_2022,
        '| Friday, May 06, 2022 | 08:30 AM | **Employment Situation** for April 2022 |'),
    _Src(date(2022, 5, 11), CPI, _BLS_2022,
        '| Wednesday, May 11, 2022 | 08:30 AM | **Consumer Price Index** for April 2022 |'),
    _Src(date(2022, 6, 3), NFP, _BLS_2022,
        '| Friday, June 3, 2022 | 08:30 AM | **Employment Situation** for May 2022 |'),
    _Src(date(2022, 6, 10), CPI, _BLS_2022,
        '| Friday, June 10, 2022 | 08:30 AM | **Consumer Price Index** for May 2022 |'),
    _Src(date(2022, 6, 15), FOMC, _FED_CALENDARS,
        '**June**\n\n14-15\\* ... **Statement:** ... monetary20220615a.htm'),
    _Src(date(2022, 7, 8), NFP, _BLS_2022,
        '| Friday, July 8, 2022 | 08:30 AM | **Employment Situation** for June 2022 |'),
    _Src(date(2022, 7, 13), CPI, _BLS_2022,
        '| Wednesday, July 13, 2022 | 08:30 AM | **Consumer Price Index** for June 2022 |'),
    _Src(date(2022, 7, 27), FOMC, _FED_CALENDARS,
        '**July**\n\n26-27 ... **Statement:** ... monetary20220727a.htm'),
    _Src(date(2022, 8, 5), NFP, _BLS_2022,
        '| Friday, August 05, 2022 | 08:30 AM | **Employment Situation** for July 2022 |'),
    _Src(date(2022, 8, 10), CPI, _BLS_2022,
        '| Wednesday, August 10, 2022 | 08:30 AM | **Consumer Price Index** for July '
        '2022 |'),
    _Src(date(2022, 9, 2), NFP, _BLS_2022,
        '| Friday, September 02, 2022 | 08:30 AM | **Employment Situation** for August '
        '2022 |'),
    _Src(date(2022, 9, 13), CPI, _BLS_2022,
        '| Tuesday, September 13, 2022 | 08:30 AM | **Consumer Price Index** for August '
        '2022 |'),
    _Src(date(2022, 9, 21), FOMC, _FED_CALENDARS,
        '**September**\n\n20-21\\* ... **Statement:** ... monetary20220921a.htm'),
    _Src(date(2022, 10, 7), NFP, _BLS_2022,
        '| Friday, October 07, 2022 | 08:30 AM | **Employment Situation** for September '
        '2022 |'),
    _Src(date(2022, 10, 13), CPI, _BLS_2022,
        '| Thursday, October 13, 2022 | 08:30 AM | **Consumer Price Index** for '
        'September 2022 |'),
    _Src(date(2022, 11, 2), FOMC, _FED_CALENDARS,
        '**November**\n\n1-2 ... **Statement:** ... monetary20221102a.htm'),
    _Src(date(2022, 11, 4), NFP, _BLS_2022,
        '| Friday, November 04, 2022 | 08:30 AM | **Employment Situation** for October '
        '2022 |'),
    _Src(date(2022, 11, 10), CPI, _BLS_2022,
        '| Thursday, November 10, 2022 | 08:30 AM | **Consumer Price Index** for October '
        '2022 |'),
    _Src(date(2022, 12, 2), NFP, _BLS_2022,
        '| Friday, December 02, 2022 | 08:30 AM | **Employment Situation** for November '
        '2022 |'),
    _Src(date(2022, 12, 13), CPI, _BLS_2022,
        '| Tuesday, December 13, 2022 | 08:30 AM | **Consumer Price Index** for November '
        '2022 |'),
    _Src(date(2022, 12, 14), FOMC, _FED_CALENDARS,
        '**December**\n\n13-14\\* ... **Statement:** ... monetary20221214a.htm'),
    _Src(date(2023, 1, 6), NFP, _BLS_2023,
        '| Friday, January 06, 2023 | 08:30 AM | **Employment Situation** for December '
        '2022 |'),
    _Src(date(2023, 1, 12), CPI, _BLS_2023,
        '| Thursday, January 12, 2023 | 08:30 AM | **Consumer Price Index** for December '
        '2022 |'),
    _Src(date(2023, 2, 1), FOMC, _FED_CALENDARS,
        '#### 2023 FOMC Meetings\n\n**Jan/Feb**\n\n31-1 ... **Statement:** ... '
        'monetary20230201a.htm'),
    _Src(date(2023, 2, 3), NFP, _BLS_2023,
        '| Friday, February 03, 2023 | 08:30 AM | **Employment Situation** for January '
        '2023 |'),
    _Src(date(2023, 2, 14), CPI, _BLS_2023,
        '| Tuesday, February 14, 2023 | 08:30 AM | **Consumer Price Index** for January '
        '2023 |'),
    _Src(date(2023, 3, 10), NFP, _BLS_2023,
        '| Friday, March 10, 2023 | 08:30 AM | **Employment Situation** for February '
        '2023 |'),
    _Src(date(2023, 3, 14), CPI, _BLS_2023,
        '| Tuesday, March 14, 2023 | 08:30 AM | **Consumer Price Index** for February '
        '2023 |'),
    _Src(date(2023, 3, 22), FOMC, _FED_CALENDARS,
        '**March**\n\n21-22\\* ... **Statement:** ... monetary20230322a.htm'),
    _Src(date(2023, 4, 7), NFP, _BLS_2023,
        '| Friday, April 07, 2023 | 08:30 AM | **Employment Situation** for March 2023 |'),
    _Src(date(2023, 4, 12), CPI, _BLS_2023,
        '| Wednesday, April 12, 2023 | 08:30 AM | **Consumer Price Index** for March '
        '2023 |'),
    _Src(date(2023, 5, 3), FOMC, _FED_CALENDARS,
        '**May**\n\n2-3 ... **Statement:** ... monetary20230503a.htm'),
    _Src(date(2023, 5, 5), NFP, _BLS_2023,
        '| Friday, May 05, 2023 | 08:30 AM | **Employment Situation** for April 2023 |'),
    _Src(date(2023, 5, 10), CPI, _BLS_2023,
        '| Wednesday, May 10, 2023 | 08:30 AM | **Consumer Price Index** for April 2023 |'),
    _Src(date(2023, 6, 2), NFP, _BLS_2023,
        '| Friday, June 02, 2023 | 08:30 AM | **Employment Situation** for May 2023 |'),
    _Src(date(2023, 6, 13), CPI, _BLS_2023,
        '| Tuesday, June 13, 2023 | 08:30 AM | **Consumer Price Index** for May 2023 |'),
    _Src(date(2023, 6, 14), FOMC, _FED_CALENDARS,
        '**June**\n\n13-14\\* ... **Statement:** ... monetary20230614a.htm'),
    _Src(date(2023, 7, 7), NFP, _BLS_2023,
        '| Friday, July 07, 2023 | 08:30 AM | **Employment Situation** for June 2023 |'),
    _Src(date(2023, 7, 12), CPI, _BLS_2023,
        '| Wednesday, July 12, 2023 | 08:30 AM | **Consumer Price Index** for June 2023 |'),
    _Src(date(2023, 7, 26), FOMC, _FED_CALENDARS,
        '**July**\n\n25-26 ... **Statement:** ... monetary20230726a.htm'),
    _Src(date(2023, 8, 4), NFP, _BLS_2023,
        '| Friday, August 04, 2023 | 08:30 AM | **Employment Situation** for July 2023 |'),
    _Src(date(2023, 8, 10), CPI, _BLS_2023,
        '| Thursday, August 10, 2023 | 08:30 AM | **Consumer Price Index** for July 2023 '
        '|'),
    _Src(date(2023, 9, 1), NFP, _BLS_2023,
        '| Friday, September 01, 2023 | 08:30 AM | **Employment Situation** for August '
        '2023 |'),
    _Src(date(2023, 9, 13), CPI, _BLS_2023,
        '| Wednesday, September 13, 2023 | 08:30 AM | **Consumer Price Index** for '
        'August 2023 |'),
    _Src(date(2023, 9, 20), FOMC, _FED_CALENDARS,
        '**September**\n\n19-20\\* ... **Statement:** ... monetary20230920a.htm'),
    _Src(date(2023, 10, 6), NFP, _BLS_2023,
        '| Friday, October 06, 2023 | 08:30 AM | **Employment Situation** for September '
        '2023 |'),
    _Src(date(2023, 10, 12), CPI, _BLS_2023,
        '| Thursday, October 12, 2023 | 08:30 AM | **Consumer Price Index** for '
        'September 2023 |'),
    _Src(date(2023, 11, 1), FOMC, _FED_CALENDARS,
        '**Oct/Nov**\n\n31-1 ... **Statement:** ... monetary20231101a.htm'),
    _Src(date(2023, 11, 3), NFP, _BLS_2023,
        '| Friday, November 03, 2023 | 08:30 AM | **Employment Situation** for October '
        '2023 |'),
    _Src(date(2023, 11, 14), CPI, _BLS_2023,
        '| Tuesday, November 14, 2023 | 08:30 AM | **Consumer Price Index** for October '
        '2023 |'),
    _Src(date(2023, 12, 8), NFP, _BLS_2023,
        '| Friday, December 08, 2023 | 08:30 AM | **Employment Situation** for November '
        '2023 |'),
    _Src(date(2023, 12, 12), CPI, _BLS_2023,
        '| Tuesday, December 12, 2023 | 08:30 AM | **Consumer Price Index** for November '
        '2023 |'),
    _Src(date(2023, 12, 13), FOMC, _FED_CALENDARS,
        '**December**\n\n12-13\\* ... **Statement:** ... monetary20231213a.htm'),
    _Src(date(2024, 1, 5), NFP, _BLS_2024_01,
        '5<br>**Employment Situation** December 2023<br>08:30 AM',
        note='month-view calendar cell; date is Friday, January 5, 2024'),
    _Src(date(2024, 1, 11), CPI, _BLS_2024_01,
        '11<br>**Consumer Price Index** December 2023<br>08:30 AM<br>**Real Earnings** '
        'December 2023<br>08:30 AM',
        note='month-view calendar cell; date is Thursday, January 11, 2024'),
    _Src(date(2024, 1, 31), FOMC, _FED_CALENDARS,
        '#### 2024 FOMC Meetings\n\n**January**\n\n30-31 ... **Statement:** ... '
        'monetary20240131a.htm'),
    _Src(date(2024, 2, 2), NFP, _BLS_2024_02,
        '2<br>**Employment Situation** January 2024<br>08:30 AM',
        note='month-view calendar cell; date is Friday, February 2, 2024'),
    _Src(date(2024, 2, 13), CPI, _BLS_2024_02,
        '13<br>**Consumer Price Index** January 2024<br>08:30 AM<br>**Real Earnings** '
        'January 2024<br>08:30 AM',
        note='month-view calendar cell; date is Tuesday, February 13, 2024'),
)


def _build_release_table(
    releases: tuple[ReleaseSource, ...],
) -> tuple[dict[date, datetime], dict[date, ReleaseSource], tuple[ReleaseSource, ...]]:
    """(table, sources, dropped). A duplicate date raises unless it is a ruled collision,
    where the earliest release is kept and must be of the ruled kind."""
    table: dict[date, datetime] = {}
    sources: dict[date, ReleaseSource] = {}
    dropped: list[ReleaseSource] = []
    for src in releases:
        day = src.release_date
        if not WINDOW_FIRST <= day <= WINDOW_LAST:
            raise ValueError(f"release date {day} outside {WINDOW_FIRST}..{WINDOW_LAST}")
        if src.kind not in RELEASE_TIME_ET:
            raise ValueError(f"unknown release kind {src.kind!r} on {day}")
        if not src.url or not src.quote:
            raise ValueError(f"release {day} {src.kind} has no source")
        if day not in table:
            table[day] = src.release_et
            sources[day] = src
            continue
        ruled_kind = RULED_COLLISIONS.get(day)
        if ruled_kind is None:
            raise ValueError(f"duplicate release date {day} in the 2019-2024 release table")
        kept, lost = (src, sources[day]) if src.release_et < table[day] else (sources[day], src)
        if kept.kind != ruled_kind or kept.release_et == lost.release_et:
            raise ValueError(f"collision on {day} does not resolve as ruled ({ruled_kind})")
        table[day] = kept.release_et
        sources[day] = kept
        dropped.append(lost)
    unresolved = set(RULED_COLLISIONS) - {s.release_date for s in dropped}
    if unresolved:
        raise ValueError(f"ruled collisions not found in the releases: {sorted(unresolved)}")
    return table, sources, tuple(dropped)


_TABLE, _SOURCES, DROPPED_RELEASES = _build_release_table(_RELEASES)

# A plain dict so ``RELEASE_TABLE_ET | RELEASE_TABLE_2019_2024`` is a plain dict (list 2.1 A1).
RELEASE_TABLE_2019_2024: dict[date, datetime] = _TABLE
SOURCES: MappingProxyType[date, ReleaseSource] = MappingProxyType(_SOURCES)
