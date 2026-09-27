"""Cross-product windows and the member-level coverage check (Stage E.2b Task 1; D4, D9, D11.5).

- The shared UTC minute grid and the no-forward-fill rule live in the engine
  (screening.stage_e_engine.iter_minutes, and the refusal "engine_leg_missing_bar"): a leg without a
  bar at a minute is absent from that minute, and a member opens no exposure unless every leg it
  reads has a bar there.
- ``member_window``: a member's window dates are the trade dates every leg has bars on (the
  intersection), less the union of every leg's roll-blackout dates (D4: "a trade date is excluded
  if it is a roll-blackout date of ANY leg the member reads"; NULL_CRITERIA_E 4 and D11.4 read the
  blackout as dates removed, so a single-leg member loses its own blackout dates the same way,
  reading RR-5), less, on the research window, the dates of rule UR-1 below.
- Rule UR-1 (unseen roll, E.2a's carried item): the research-window symbology ends before
  2026-06-21 00:00 UTC, so a splice booked to trade date 2026-06-22 or 2026-06-23 (which would make
  2026-06-18 and/or 2026-06-19 roll-blackout dates) cannot be seen. For several products the
  front contract on 2026-06-19 still had a roll due (NG, MNG, QG July contracts expire 2026-06-26;
  grains and metals roll before first notice at the end of June; MBT's June contract expires
  2026-06-26), and a volume-ranked series can also flip back just after a roll. Whether a roll
  happened cannot be decided without data this machine does not have, so 2026-06-18 and
  2026-06-19 are excluded from every Stage E product's research window as possible roll-blackout
  dates (a question for the user: a per-product refinement from contract calendars).
- ``leg_coverage``: D9's member-level coverage: bars present over minutes expected, where the
  expected minutes are the member's declared intervals for the leg (strategy.stage_e.interface
  .TradingInterval) intersected with the group calendar's open intervals of each window date;
  a member passes when every leg it reads has coverage >= 0.95.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from types import MappingProxyType
from zoneinfo import ZoneInfo

import numpy as np

from data.group_session import load_group_calendar, session_intervals
from data.stage_e_bars import RESEARCH, LegFrame
from rules.products import product
from strategy.stage_e.interface import TradingInterval

CT = ZoneInfo("America/Chicago")
NS_PER_MIN = 60 * 1_000_000_000
COVERAGE_MIN = 0.95  # D9
UNSEEN_ROLL_DATES = (date(2026, 6, 18), date(2026, 6, 19))  # rule UR-1
UNSEEN_ROLL_RULE = "UR-1"


@dataclass(frozen=True)
class MemberWindow:
    store: str
    dates: tuple[date, ...]  # the window dates, ascending
    excluded: Mapping[str, tuple[date, ...]]  # cause -> dates removed
    blackout_union: frozenset[date]


def member_window(legs: Mapping[str, LegFrame], store: str) -> MemberWindow:
    """D4's window for the legs' frames (all from one store)."""
    if not legs:
        raise ValueError("a member has at least one leg")
    stores = {leg.store for leg in legs.values()}
    if stores != {store}:
        raise ValueError(f"legs come from stores {sorted(stores)}, not {store!r}")
    days = [set(leg.trade_dates) for leg in legs.values()]
    union = set().union(*days)
    common = set.intersection(*days)
    blackout = frozenset().union(*(leg.roll_blackout for leg in legs.values()))
    excluded: dict[str, tuple[date, ...]] = {
        "not_every_leg_trades": tuple(sorted(union - common)),
        "roll_blackout_any_leg": tuple(sorted(common & blackout)),
    }
    kept = common - blackout
    if store == RESEARCH:
        ur = {d for d in UNSEEN_ROLL_DATES if d in kept}
        excluded[f"unseen_roll_{UNSEEN_ROLL_RULE}"] = tuple(sorted(ur))
        kept -= ur
    return MemberWindow(store, tuple(sorted(kept)), MappingProxyType(excluded), blackout)


def _ns(day: date, offset: int, at: object) -> int:
    local = datetime.combine(day + timedelta(days=offset), at, tzinfo=CT)  # type: ignore[arg-type]
    return int(local.timestamp()) * 1_000_000_000


@dataclass(frozen=True)
class Coverage:
    root: str
    present: int
    expected: int

    @property
    def ratio(self) -> float:
        return self.present / self.expected if self.expected else 0.0

    @property
    def passes(self) -> bool:
        return self.expected > 0 and self.ratio >= COVERAGE_MIN


def _expected_ranges(cal: object, day: date, intervals: Sequence[TradingInterval]
                     ) -> list[tuple[int, int]]:
    opened = session_intervals(cal, day)  # type: ignore[arg-type]
    out: list[tuple[int, int]] = []
    for iv in intervals:
        lo = _ns(day, iv.start_offset_days, iv.start_ct)
        hi = _ns(day, iv.end_offset_days, iv.end_ct)
        if hi <= lo:
            raise ValueError(f"trading interval {iv} is empty or reversed")
        for s, e in opened:
            a, b = max(lo, s), min(hi, e)
            if b > a:
                out.append((a, b))
    return out


def leg_coverage(leg: LegFrame, dates: Sequence[date], intervals: Sequence[TradingInterval]
                 ) -> Coverage:
    """Present bars over expected minutes, summed over ``dates`` (D9)."""
    if not intervals:
        raise ValueError(f"{leg.root}: the member declares no trading interval for this leg")
    cal = load_group_calendar(product(leg.root).group)
    ts = np.sort(leg.frame["ts_event"].to_numpy(dtype="int64"))
    present = expected = 0
    for day in dates:
        for a, b in _expected_ranges(cal, day, intervals):
            a_min = -(-a // NS_PER_MIN) * NS_PER_MIN  # first whole minute at or after a
            n = max(0, (b - a_min + NS_PER_MIN - 1) // NS_PER_MIN)
            expected += n
            present += int(np.searchsorted(ts, b, side="left") - np.searchsorted(ts, a_min,
                                                                                side="left"))
    return Coverage(leg.root, present, expected)


def member_coverage(legs: Mapping[str, LegFrame], dates: Sequence[date],
                    windows: Mapping[str, Sequence[TradingInterval]]) -> dict[str, Coverage]:
    missing = [r for r in legs if r not in windows]
    if missing:
        raise ValueError(f"the member declares no trading window for legs {missing}")
    return {r: leg_coverage(leg, dates, windows[r]) for r, leg in legs.items()}


__all__ = [
    "COVERAGE_MIN", "UNSEEN_ROLL_DATES", "UNSEEN_ROLL_RULE", "Coverage", "MemberWindow",
    "leg_coverage", "member_coverage", "member_window",
]
