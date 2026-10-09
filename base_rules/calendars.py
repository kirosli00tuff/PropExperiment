"""Trade dates, halts, unsourced dates and day sessions per product, 2010-06..2024-02.

Two frozen calendars per group, never edited: the hist calendar
(data/calendars/hist2010/<group>.json
through data.hist_calendar; livestock from Task 3b's file at a path parameter, parsed by the same
frozen parser) for trade dates before 2019-05-01, and the 2019-on group calendar
(data.group_session.load_group_calendar) from 2019-05-01. Every question (is a trade date, early
halt, unsourced, open intervals, the day session's open and close) is answered by the frozen
calendar object of the date's era, with data.group_session's own functions.
"""

from __future__ import annotations

import bisect
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from pathlib import Path
from typing import Any

from base_rules import constants as K
from data.group_session import GroupCalendar, load_group_calendar, session_intervals
from data.hist_calendar import load_hist_group_calendar, parse_hist_calendar


class CalendarError(RuntimeError):
    """A calendar is missing, unpinned where a pin was given, or cannot answer."""


def _minute(t: time) -> int:
    return t.hour * 60 + t.minute


def _day_session_entry(cal: GroupCalendar, product: str, day: date) -> tuple[time, time]:
    """D6's (O, C) for ``product`` on ``day`` with GroupCalendar.day_session_close's key order
    (product, sub-group, "*", a single shared value)."""
    table = cal.spec_for(day).day_session_ct
    if product in table:
        return table[product]
    sub = cal.subgroup_of_product.get(product) or K.SUBGROUP.get(product)
    if sub in table:
        return table[sub]
    if "*" in table:
        return table["*"]
    if len(set(table.values())) == 1:
        return next(iter(table.values()))
    raise CalendarError(f"{cal.group}: no day session for {product} on {day} (keys "
                        f"{sorted(table)})")


@dataclass
class GroupCalendars:
    """One group's two eras: ``hist`` before 2019-05-01, ``frozen`` from it."""

    group: str
    hist: Any  # data.hist_calendar.HistGroupCalendar
    frozen: GroupCalendar
    _dates: list[date] = field(default_factory=list, repr=False)
    _index: dict[date, int] = field(default_factory=dict, repr=False)
    _iv: dict[date, list] = field(default_factory=dict, repr=False)

    def cal_for(self, day: date) -> GroupCalendar:
        return self.hist if day < K.FROZEN_CAL_FIRST else self.frozen

    def is_trade_date(self, day: date) -> bool:
        cal = self.cal_for(day)
        return cal.covers(day) and cal.is_trade_date(day)

    def early_halt(self, day: date) -> time | None:
        return self.cal_for(day).early_halt_ct(day)

    def unsourced(self, day: date) -> bool:
        cal = self.cal_for(day)
        return bool(getattr(cal, "is_unsourced", lambda d: False)(day))

    def trade_dates(self) -> list[date]:
        """Every trade date 2010-06-01..2024-02-29 of the two eras, ascending (cached)."""
        if not self._dates:
            d, out = date(2010, 6, 1), []
            while d <= K.WINDOW_LAST:
                if self.is_trade_date(d):
                    out.append(d)
                d += timedelta(days=1)
            self._dates = out
            self._index = {x: i for i, x in enumerate(out)}
        return self._dates

    def offset(self, day: date, n: int) -> date | None:
        """The trade date ``n`` trade dates after (n > 0) or before (n < 0) ``day``."""
        dates = self.trade_dates()
        i = self._index.get(day)
        if i is None or not 0 <= i + n < len(dates):
            return None
        return dates[i + n]

    def previous(self, day: date) -> date | None:
        dates = self.trade_dates()
        i = bisect.bisect_left(dates, day) - 1
        return dates[i] if i >= 0 else None

    def intervals(self, day: date) -> list[tuple[int, int]]:
        """Trade date ``day``'s open intervals (UTC ns), data.group_session.session_intervals."""
        got = self._iv.get(day)
        if got is None:
            got = self._iv[day] = session_intervals(self.cal_for(day), day)
        return got

    def day_session(self, product: str, day: date) -> tuple[int, int]:
        o, c = _day_session_entry(self.cal_for(day), product, day)
        return _minute(o), _minute(c)

    def open_by_period(self, product: str) -> dict[date, int]:
        """valid_from -> day-session open minute, both eras (for the provisional table)."""
        out: dict[date, int] = {}
        for cal, lo, hi in ((self.hist, date(2010, 6, 1), K.FROZEN_CAL_FIRST - timedelta(1)),
                            (self.frozen, K.FROZEN_CAL_FIRST, K.WINDOW_LAST)):
            for spec in cal.sessions:
                start = max(spec.valid_from, lo)
                if start > hi or (spec.valid_to is not None and spec.valid_to < lo):
                    continue
                out[start] = _minute(_day_session_entry(cal, product, start)[0])
        return out


def load_hist(group: str, *, hist_dir: Path = K.HIST_CALENDAR_DIR,
              livestock_path: Path = K.LIVESTOCK_HIST_PATH,
              expected_sha256: str | None = None) -> Any:
    """The group's 2010-2019 calendar through data.hist_calendar (livestock: its parser on Task
    3b's file, the frozen loader's group list does not hold livestock)."""
    if group == K.LIVESTOCK:
        path = K.repo_path(livestock_path)
        if not path.is_file():
            raise CalendarError(f"{path} does not exist (Task 3b's livestock calendar)")
        raw = path.read_bytes()
        cal = parse_hist_calendar(raw, group, path)
        if expected_sha256 is not None and cal.file_sha256 != expected_sha256:
            raise CalendarError(f"{path.name}: sha256 {cal.file_sha256[:12]}... is not the "
                                f"pinned {expected_sha256[:12]}...")
        return cal
    return load_hist_group_calendar(group, base=K.repo_path(hist_dir),
                                    expected_sha256=expected_sha256)


def load_calendars(groups: tuple[str, ...] | None = None, *,
                   hist_dir: Path = K.HIST_CALENDAR_DIR,
                   livestock_path: Path = K.LIVESTOCK_HIST_PATH,
                   pins: Mapping[str, str] | None = None) -> dict[str, GroupCalendars]:
    """group -> GroupCalendars for ``groups`` (default: every group of the 27 products).
    ``pins``: group -> the hist file's sha256 (the freeze's record)."""
    groups = groups or tuple(sorted(set(K.GROUP_OF.values())))
    out = {}
    for g in groups:
        hist = load_hist(g, hist_dir=hist_dir, livestock_path=livestock_path,
                         expected_sha256=(pins or {}).get(g))
        out[g] = GroupCalendars(g, hist, load_group_calendar(g))
    return out


def both_trade_dates(a: GroupCalendars, b: GroupCalendars) -> list[date]:
    """Dates that are trade dates of both groups (H2's trading days)."""
    other = set(b.trade_dates())
    return [d for d in a.trade_dates() if d in other]


__all__ = ["CalendarError", "GroupCalendars", "both_trade_dates", "load_calendars", "load_hist"]
