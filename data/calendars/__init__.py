"""Per-group CME calendars for Stage E (design D10, D11.3), written in Stage E.2a.

Each group module (rates, fx, energy, metals, grains, livestock, crypto) has the interface of
``data.cme_calendar`` (the equity group, which stays where it is): ``HOLIDAYS`` (date ->
``data.cme_calendar.Holiday``), ``CALENDAR_COVERAGE``, ``assert_calendar_coverage``, verbatim
source citations per entry, and a ``SESSIONS`` tuple of ``SessionSpec`` (below) giving the
group's Globex session structure with every dated CME session-hour change in 2019-2026.

This file holds only the shared session type and the product-to-group map. It holds no
calendar entries.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time

GROUPS = ("equity", "rates", "fx", "energy", "metals", "grains", "livestock", "crypto")

# The 45 admissible contracts of design D1 (after U2), plus the MES/ES leg (equity).
GROUP_OF_PRODUCT: dict[str, str] = {
    **{p: "equity" for p in ("MNQ", "NQ", "RTY", "M2K", "MYM", "YM", "MES", "ES")},
    **{p: "rates" for p in ("ZT", "ZF", "ZN", "TN", "ZB", "UB")},
    **{p: "fx" for p in ("6E", "M6E", "E7", "6A", "M6A", "6B", "M6B", "6C", "6J", "6S", "6N")},
    **{p: "energy" for p in ("CL", "MCL", "QM", "NG", "MNG", "QG", "RB", "HO")},
    **{p: "metals" for p in ("GC", "MGC", "SI", "SIL", "HG", "MHG")},
    **{p: "grains" for p in ("ZC", "ZW", "ZS", "ZM", "ZL")},
    **{p: "livestock" for p in ("HE", "LE")},
    **{p: "crypto" for p in ("MBT",)},
}


@dataclass(frozen=True)
class Segment:
    """One continuous trading segment of a trade date, in CT wall-clock time.

    ``start_offset_days`` / ``end_offset_days`` are relative to the trade date: -1 means the
    prior calendar day (for example the 17:00 CT evening open), 0 the trade date itself.
    """

    start_offset_days: int
    start_ct: time
    end_offset_days: int
    end_ct: time


@dataclass(frozen=True)
class SessionSpec:
    """The regular (non-holiday) Globex session of a group over a span of trade dates.

    ``valid_from`` and ``valid_to`` are trade dates, both inclusive (``valid_to`` None = open).
    ``segments`` are in time order. ``day_session_ct`` is design D6's (O, C) for the group
    as confirmed against CME's published settlement procedures (or the group's own sub-table
    where D6 splits a group, e.g. gold / silver / copper). ``source`` is a citation key into
    the module's source table. ``note`` records anything a reader needs (for example the
    crypto weekend rule from 2026-05-29).
    """

    valid_from: date
    valid_to: date | None
    segments: tuple[Segment, ...]
    day_session_ct: dict[str, tuple[time, time]]
    source: str
    note: str = ""
