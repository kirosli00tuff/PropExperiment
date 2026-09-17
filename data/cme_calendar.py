"""CME Globex holiday calendar for equity index futures (MES/ES), 2025-2026.

Closes the gap documented in MLCryptoEngine's session calendar, which had no
holiday handling. Compiled 2026-09-16 from CME Group's own publications, NOT
from the NYSE calendar — CME differs: most US holidays keep equity futures
trading on Globex with an early 12:00 CT halt, Good Friday 2026 had an
abbreviated session for the jobs report, and the day before/after some
holidays closes at 12:15 CT.

Evidence grades per entry (``evidence``):
- ``cme``: the day's status (closure / no settlement / early equity
  settlement) is stated by a CME-direct source: the holiday settlement-times
  PDFs at cmegroup.com/tools-information/holiday-calendar/files/{2025,2026}/,
  CME press release 2024-12-30 (Day of Mourning), clearing notice 25-012,
  and the 2026 Good Friday clearing advisory. cmegroup.com blocks automated
  fetches, so these were read through Wayback Machine copies.
- ``secondary``: the exact halt/close clock time comes from broker schedules
  (AMP Futures, CrossTrade, DiscountTrading) quoting CME; CME's own Globex
  hours table was not retrievable. Topstep's holiday article (2026-09-01)
  independently implies the same 12:00 / 12:15 CT times for Nov 26-27 and
  Dec 24 2026 (its flatten times are 15 minutes earlier).
- ``inferred``: 12:15 CT close inferred from CME's 12:00 CT equity
  settlement on that date, consistent with brokers.

Every entry inside the pulled bar window (2025-04-01..2026-09-16) is
additionally checked EMPIRICALLY against the MES 1-minute bars by
``data.validate`` (last traded minute before the halt, no bars inside the
closure); results are in reports/bar_validation.md. Unconfirmed items are
listed there too — notably the Good Friday 2026 close time (08:15 CT per AMP,
~09:15 CT per another secondary source).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from enum import Enum

EARLY_HALT_NOON = time(12, 0)
EARLY_CLOSE_1215 = time(12, 15)


class HolidayKind(Enum):
    FULL_CLOSURE = "full_closure"  # no Globex session for this calendar day
    EARLY_HALT = "early_halt"  # trading stops at halt_ct; normal 17:00 CT reopen


@dataclass(frozen=True)
class Holiday:
    day: date
    name: str
    kind: HolidayKind
    halt_ct: time | None
    evidence: str  # "cme" status; time grade noted in ``time_evidence``
    time_evidence: str  # "cme" | "empirical" | "secondary" | "inferred" | "n/a"


def _closure(day: date, name: str) -> Holiday:
    return Holiday(day, name, HolidayKind.FULL_CLOSURE, None, "cme", "n/a")


def _halt(day: date, name: str, at: time, time_evidence: str) -> Holiday:
    return Holiday(day, name, HolidayKind.EARLY_HALT, at, "cme", time_evidence)


_ENTRIES: tuple[Holiday, ...] = (
    # ---- 2025
    _closure(date(2025, 1, 1), "New Year's Day"),
    _halt(date(2025, 1, 9), "National Day of Mourning (Carter)", time(8, 30), "cme"),
    _halt(date(2025, 1, 20), "Martin Luther King Jr. Day", EARLY_HALT_NOON, "secondary"),
    _halt(date(2025, 2, 17), "Presidents Day", EARLY_HALT_NOON, "secondary"),
    _closure(date(2025, 4, 18), "Good Friday"),
    _halt(date(2025, 5, 26), "Memorial Day", EARLY_HALT_NOON, "secondary"),
    _halt(date(2025, 6, 19), "Juneteenth", EARLY_HALT_NOON, "secondary"),
    _halt(date(2025, 7, 3), "Day before Independence Day", EARLY_CLOSE_1215, "inferred"),
    # Corrected 2026-09-16 from the bars: CME publishes "no settlement" for
    # 2025-07-04, which research first read as a full closure. MES 1-minute
    # bars show Globex trading Thu 17:00 CT -> Fri 11:59 CT (1,140 bars), i.e.
    # an early 12:00 CT halt with the trade date combined, like other holidays.
    _halt(date(2025, 7, 4), "Independence Day", EARLY_HALT_NOON, "empirical"),
    _halt(date(2025, 9, 1), "Labor Day", EARLY_HALT_NOON, "secondary"),
    _halt(date(2025, 11, 27), "Thanksgiving", EARLY_HALT_NOON, "secondary"),
    _halt(date(2025, 11, 28), "Day after Thanksgiving", EARLY_CLOSE_1215, "inferred"),
    _halt(date(2025, 12, 24), "Christmas Eve", EARLY_CLOSE_1215, "inferred"),
    _closure(date(2025, 12, 25), "Christmas Day"),
    # ---- 2026
    _closure(date(2026, 1, 1), "New Year's Day"),
    _halt(date(2026, 1, 19), "Martin Luther King Jr. Day", EARLY_HALT_NOON, "secondary"),
    _halt(date(2026, 2, 16), "Presidents Day", EARLY_HALT_NOON, "secondary"),
    # CME 2026 Good Friday clearing advisory: "Equities are open for an
    # abbreviated session on April 3rd, but will not be settled". Close time
    # not published CME-direct: 08:15 CT per AMP Futures (checked in bars).
    # 08:15 CT per AMP Futures; ~09:15 per another secondary source. The bars
    # settle it: last traded minute 08:14 CT, next bar Sunday 17:00 CT.
    _halt(date(2026, 4, 3), "Good Friday (abbreviated, jobs report)", time(8, 15), "empirical"),
    _halt(date(2026, 5, 25), "Memorial Day", EARLY_HALT_NOON, "secondary"),
    _halt(date(2026, 6, 19), "Juneteenth", EARLY_HALT_NOON, "secondary"),
    _halt(date(2026, 7, 3), "Independence Day (observed)", EARLY_HALT_NOON, "secondary"),
    _halt(date(2026, 9, 7), "Labor Day", EARLY_HALT_NOON, "secondary"),
    _halt(date(2026, 11, 26), "Thanksgiving", EARLY_HALT_NOON, "secondary"),
    _halt(date(2026, 11, 27), "Day after Thanksgiving", EARLY_CLOSE_1215, "inferred"),
    _halt(date(2026, 12, 24), "Christmas Eve", EARLY_CLOSE_1215, "inferred"),
    _closure(date(2026, 12, 25), "Christmas Day"),
)

HOLIDAYS: dict[date, Holiday] = {h.day: h for h in _ENTRIES}
CALENDAR_COVERAGE = (date(2025, 1, 1), date(2026, 12, 31))
