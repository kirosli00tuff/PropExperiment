"""Trigger events -> units (lead_spec sections 1 and 2).

- Entry mark date d_e: d0 when tau is STRICTLY before the open of the settlement bar S_i(d0)
  (the settlement table's minute S on d0, the instant MK fills at); otherwise (tau at or after
  it, or d0 without a settlement minute) the next mark date of the root after d0.
- d_e must be an eligible action date (multiday.signals.action_why, E.21 T3's entry rule:
  base_rules' action exclusion incl. roll blackout and early halt, listed, MK and PS present,
  the MK bar outside every guard window); else the unit is excluded, counted "entry: <why>".
- Exit mark date d_x: the h-th mark date of the root after d_e. Coder choice (conservative,
  "Questions for the lead" Q1): d_x must also be an eligible action date (T3's exit rule),
  else the unit is excluded, counted "exit: <why>".
- Window membership: a unit belongs to the window holding both d_e and d_x; a unit whose d_e or
  d_x falls outside the window (a window edge, the store boundary, no h-th mark) is excluded,
  counted by reason. Direction u = side x m.

Mark existence and eligibility come from a ``MarkSource``: ``BarMarks`` (the loaded bars: the
run) or ``CalendarMarks`` (the calendars and the settlement table alone: the power table). No
source reads a price.
"""

from __future__ import annotations

import bisect
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, time
from typing import Protocol

from base_rules.common import RunContext
from base_rules.store import ProductBars
from data.session import ct_ns
from multiday.daily import Mark, era_of
from multiday.signals import BarOracle, CalendarOracle, action_why
from trigger_hold import constants as K
from trigger_hold.types import TriggerEvent


@dataclass(frozen=True)
class Window:
    name: str
    first: date
    last: date

    def holds(self, d: date) -> bool:
        return self.first <= d <= self.last


@dataclass(frozen=True, order=True)
class Unit:
    d_e: date
    d_x: date
    u: int
    trigger_id: str
    root: str
    d0: date
    h: int


class MarkSource(Protocol):
    root: str

    def mark_days(self) -> Sequence[date]: ...

    def settle_open_ns(self, d: date) -> int | None: ...

    def action_why(self, d: date) -> str | None: ...


def _settle_open_ns(ctx: RunContext, root: str, d: date) -> int | None:
    """The open instant of the settlement bar S_i(d) (ns UTC; None: no settlement minute)."""
    s = ctx.settlement.settle_minute(root, d)
    if s is None:
        return None
    return ct_ns(d, time(int(s) // 60, int(s) % 60))


class BarMarks:
    """Mark dates and eligibility from the loaded bars (existence only; no price is read)."""

    def __init__(self, ctx: RunContext, bars: ProductBars, root: str, marks: Sequence[Mark]):
        self.ctx, self.root = ctx, root
        self._days = [m.day for m in marks]
        self._oracle = BarOracle(ctx, bars, root, marks)

    def mark_days(self) -> Sequence[date]:
        return self._days

    def settle_open_ns(self, d: date) -> int | None:
        return _settle_open_ns(self.ctx, self.root, d)

    def action_why(self, d: date) -> str | None:
        return action_why(self.ctx, self._oracle, self.root, d)


class CalendarMarks:
    """Calendar-only: a mark exists on a listed window trade date whose settlement minute lies
    inside the session (multiday.signals.CalendarOracle); the roll blackout from the stores'
    metadata."""

    def __init__(self, ctx: RunContext, root: str, blackout: frozenset[date]):
        self.ctx, self.root = ctx, root
        self._oracle = CalendarOracle(ctx, root, blackout)
        self._days = [d for d in ctx.window_dates(root) if self._oracle.has_mark(d)]

    def mark_days(self) -> Sequence[date]:
        return self._days

    def settle_open_ns(self, d: date) -> int | None:
        return _settle_open_ns(self.ctx, self.root, d)

    def action_why(self, d: date) -> str | None:
        return action_why(self.ctx, self._oracle, self.root, d)


def entry_mark_date(src: MarkSource, e: TriggerEvent) -> date | None:
    """d_e of section 2 (None: no mark date after d0)."""
    days = src.mark_days()
    s_open = src.settle_open_ns(e.d0)
    if s_open is not None and e.tau_ns < s_open:
        return e.d0
    k = bisect.bisect_right(days, e.d0)
    return days[k] if k < len(days) else None


def window_for(src: MarkSource, name: str, s_x: date | None = None) -> Window:
    """W_ext: max(2011-07-27, the root's first mark date) .. 2019-04-30; W_cf: max(2019-05-06,
    S_X) .. 2024-02-29 (section 1)."""
    days = src.mark_days()
    if name == K.W_EXT:
        first = max([K.W_EXT_FIRST, *days[:1]])
        return Window(name, first, K.W_EXT_LAST)
    if name == K.W_CF:
        return Window(name, max([K.W_CF_FIRST, *([s_x] if s_x else [])]), K.W_CF_LAST)
    raise ValueError(f"unknown window {name!r}")


def build_units(src: MarkSource, events: Sequence[TriggerEvent], window: Window, *, m: int,
                h: int) -> tuple[list[Unit], Counter]:
    """Section 2: the window's units of one trigger-hold and the exclusions by reason."""
    if m not in K.DIRECTIONS:
        raise ValueError(f"m must be +1 or -1, got {m!r}")
    if h < 1:
        raise ValueError(f"h must be a positive number of mark dates, got {h!r}")
    days = list(src.mark_days())
    index = {d: k for k, d in enumerate(days)}
    out: list[Unit] = []
    c: Counter = Counter()
    for e in sorted(events):
        c["events"] += 1
        if not window.holds(e.d0):
            c["excluded: event outside the window"] += 1
            continue
        d_e = entry_mark_date(src, e)
        if d_e is None:
            c["excluded: no mark date after d0"] += 1
            continue
        if d_e != e.d0:
            c["entry moved to the next mark date (tau at or after S)"] += 1
        if not window.holds(d_e):
            c["excluded: entry outside the window (window edge)"] += 1
            continue
        why = src.action_why(d_e)
        if why is not None:
            c[f"excluded: entry: {why}"] += 1
            continue
        k = index[d_e] + h  # d_e is a mark date (action_why requires MK)
        if k >= len(days):
            c["excluded: exit: no h-th mark date"] += 1
            continue
        d_x = days[k]
        if era_of(d_x) != era_of(d_e):
            c["excluded: exit across the store boundary"] += 1
            continue
        if not window.holds(d_x):
            c["excluded: exit outside the window (window edge)"] += 1
            continue
        why = src.action_why(d_x)
        if why is not None:
            c[f"excluded: exit: {why}"] += 1
            continue
        out.append(Unit(d_e, d_x, e.side * m, e.trigger_id, src.root, e.d0, h))
        c["units"] += 1
    return out, c


def series_days(src: MarkSource, window: Window) -> list[date]:
    """The root's mark dates inside the window (section 1)."""
    return [d for d in src.mark_days() if window.holds(d)]


def book_days(src: MarkSource, window: Window, units: Sequence[Unit]) -> list[date]:
    """A book's series dates (section 5 addition (a), lead 2026-10-17): the root's mark dates
    inside the window from its FIRST unit's entry mark date on; none without a unit. Used for
    the power table's n_dates and for the statistics."""
    if not units:
        return []
    first = min(u.d_e for u in units)
    return [d for d in series_days(src, window) if d >= first]


def in_market_fraction(units: Sequence[Unit], days: Sequence[date]) -> float | None:
    """Section 5 addition (c): the share of ``days`` with net(i, d) != 0, net(i, d) = clip(sum
    of u over the units with d_e < d <= d_x) (section 3); from units only (no price, no sigma)."""
    if not days:
        return None
    hits = 0
    for d in days:
        total = sum(u.u for u in units if u.d_e < d <= u.d_x)
        hits += max(-1, min(1, total)) != 0
    return hits / len(days)


__all__ = ["BarMarks", "CalendarMarks", "MarkSource", "Unit", "Window", "book_days",
           "build_units", "entry_mark_date", "in_market_fraction", "series_days", "window_for"]
