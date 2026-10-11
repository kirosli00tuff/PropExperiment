"""H6's signal and its three schedules (prereg sections 1-3), pure functions of the bars and the
frozen equity calendar. Nothing here runs the engine or reads a file.

- ``compute_facts``: per trade date d, the bar ending at C-30 (P(C-30), opening at C-31), the bar
  ending at the previous equity trade date's C (P(prior C), opening at that date's C-1), their
  instrument_ids, r_ROD = P(C-30) / P(prior C) - 1, and eligibility with the prereg's reason codes
  in the order the text lists them (the first that applies is recorded): missing_signal_bar,
  missing_prior_bar, instrument_change, zero_signal. A bar is found by its open instant only
  (CP1: its CT date and clock); nothing is forward filled.
- T1: every eligible date of the window, side sign(r_ROD).
- T2 (section 2's warm-up rule and section 3): for d, the median of |r_ROD| over the 60 most recent
  eligible dates e with lookback_first <= e < d; fewer than 60 such dates: no threshold and no
  trade ("t2_warmup"); d is a T2 date iff |r_ROD(d)| > that median, strictly.
- T3 (section 3): d is a T3 date iff the GEX value of the row dated the previous equity trade date
  of d is < 0, strictly; no row for that date: no trade ("gex_missing").
Only eligible dates are T2 or T3 candidates; an ineligible date keeps its eligibility reason.
"""

from __future__ import annotations

import bisect
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, time
from typing import Any

import numpy as np
import pandas as pd

from h6_rod import clock
from h6_rod import constants as K


@dataclass(frozen=True)
class DateFacts:
    day: date
    close_ct: time  # C(d)
    shortened: bool
    prior_day: date | None
    signal_close: float | None  # P(C-30)
    signal_iid: int | None
    prior_close: float | None  # P(prior C)
    prior_iid: int | None
    r_rod: float | None  # None unless both bars exist with one instrument_id
    reason: str | None  # None: eligible

    @property
    def eligible(self) -> bool:
        return self.reason is None

    @property
    def side(self) -> str | None:
        if not self.eligible or self.r_rod is None:
            return None
        return "buy" if self.r_rod > 0 else "sell"


@dataclass(frozen=True)
class Entry:
    """One scheduled entry: the member's market intent on the bar opening at ``entry_bar_ns``."""

    side: str
    entry_bar_ns: int  # the bar at C-31 (the intent at its close fills at the C-30 open)
    exit_from_ns: int  # the exit is due on the first present bar opening at or after C-2
    r_rod: float


@dataclass(frozen=True)
class Schedule:
    """One test on one window: the entries, and every other window date's reason."""

    test: str
    window: tuple[date, date]
    entries: Mapping[date, Entry]
    excluded: Mapping[date, str]
    thresholds: Mapping[date, float] = field(default_factory=dict)  # T2 only, descriptive

    def reason_counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for reason in self.excluded.values():
            out[reason] = out.get(reason, 0) + 1
        return dict(sorted(out.items()))


def _bar_lookup(bars: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ts = bars["ts_event"].to_numpy(np.int64)
    if len(ts) > 1 and not bool(np.all(ts[1:] > ts[:-1])):
        raise ValueError("bars are not strictly increasing in ts_event")
    return ts, bars["close"].to_numpy(np.float64), bars["instrument_id"].to_numpy(np.int64)


def _find(ts: np.ndarray, target: int) -> int | None:
    i = int(np.searchsorted(ts, target))
    return i if i < len(ts) and int(ts[i]) == target else None


def eligibility_reason(signal: tuple[float, int] | None, prior: tuple[float, int] | None
                       ) -> str | None:
    """Section 3's conditions in the text's order; None when eligible."""
    if signal is None:
        return K.REASON_MISSING_SIGNAL_BAR
    if prior is None:
        return K.REASON_MISSING_PRIOR_BAR
    if signal[1] != prior[1]:
        return K.REASON_INSTRUMENT_CHANGE
    if signal[0] == prior[0]:  # r_ROD = 0 exactly (equal prices; x / x == 1.0 in IEEE)
        return K.REASON_ZERO_SIGNAL
    return None


def compute_facts(bars: pd.DataFrame, days: Sequence[date], calendar: Any = None
                  ) -> dict[date, DateFacts]:
    """Per trade date of ``days``: the two signal bars, r_ROD and eligibility (module docstring).
    ``bars``: ts_event (UTC ns, bar open), close, instrument_id, sorted by ts_event."""
    ts, close, iid = _bar_lookup(bars)
    out: dict[date, DateFacts] = {}
    for day in days:
        prior_day = clock.previous_trade_date(day, calendar)
        i = _find(ts, clock.signal_bar_ns(day, calendar))
        j = None if prior_day is None else _find(ts, clock.prior_bar_ns(prior_day, calendar))
        signal = None if i is None else (float(close[i]), int(iid[i]))
        prior = None if j is None else (float(close[j]), int(iid[j]))
        reason = eligibility_reason(signal, prior)
        r = None
        if signal is not None and prior is not None and signal[1] == prior[1]:
            r = signal[0] / prior[0] - 1.0
        out[day] = DateFacts(
            day=day, close_ct=clock.close_ct(day, calendar),
            shortened=clock.is_shortened(day, calendar), prior_day=prior_day,
            signal_close=None if signal is None else signal[0],
            signal_iid=None if signal is None else signal[1],
            prior_close=None if prior is None else prior[0],
            prior_iid=None if prior is None else prior[1], r_rod=r, reason=reason)
    return out


def _entry(f: DateFacts, calendar: Any) -> Entry:
    assert f.side is not None and f.r_rod is not None
    return Entry(f.side, clock.signal_bar_ns(f.day, calendar),
                 clock.exit_from_ns(f.day, calendar), f.r_rod)


def _window_days(facts: Mapping[date, DateFacts], first: date, last: date) -> list[date]:
    return sorted(d for d in facts if first <= d <= last)


def t1_schedule(facts: Mapping[date, DateFacts], first: date, last: date, calendar: Any = None
                ) -> Schedule:
    entries, excluded = {}, {}
    for d in _window_days(facts, first, last):
        f = facts[d]
        if f.eligible:
            entries[d] = _entry(f, calendar)
        else:
            excluded[d] = str(f.reason)
    return Schedule("T1", (first, last), entries, excluded)


def t2_thresholds(facts: Mapping[date, DateFacts], days: Sequence[date], lookback_first: date
                  ) -> dict[date, float | None]:
    """Per day of ``days``: the median of |r_ROD| over the 60 most recent eligible dates in
    [lookback_first, d), or None when fewer than 60 lie there."""
    pool = sorted(d for d, f in facts.items() if f.eligible and d >= lookback_first)
    absr = [abs(float(facts[d].r_rod)) for d in pool]  # type: ignore[arg-type]
    out: dict[date, float | None] = {}
    for d in days:
        i = bisect.bisect_left(pool, d)  # pool[:i] are the eligible dates before d
        if i < K.T2_LOOKBACK_ELIGIBLE:
            out[d] = None
            continue
        out[d] = float(np.median(np.asarray(absr[i - K.T2_LOOKBACK_ELIGIBLE:i])))
    return out


def t2_schedule(facts: Mapping[date, DateFacts], first: date, last: date, lookback_first: date,
                calendar: Any = None) -> Schedule:
    days = _window_days(facts, first, last)
    med = t2_thresholds(facts, days, lookback_first)
    entries, excluded, thresholds = {}, {}, {}
    for d in days:
        f = facts[d]
        if not f.eligible:
            excluded[d] = str(f.reason)
            continue
        m = med[d]
        if m is None:
            excluded[d] = K.REASON_T2_WARMUP
            continue
        thresholds[d] = m
        if abs(float(f.r_rod)) > m:  # type: ignore[arg-type]
            entries[d] = _entry(f, calendar)
        else:
            excluded[d] = K.REASON_T2_NOT_ABOVE
    return Schedule("T2", (first, last), entries, excluded, thresholds)


def t3_schedule(facts: Mapping[date, DateFacts], first: date, last: date,
                gex: Mapping[date, float], calendar: Any = None) -> Schedule:
    entries, excluded = {}, {}
    for d in _window_days(facts, first, last):
        f = facts[d]
        if not f.eligible:
            excluded[d] = str(f.reason)
            continue
        value = None if f.prior_day is None else gex.get(f.prior_day)
        if value is None:
            excluded[d] = K.REASON_GEX_MISSING
        elif value < 0:
            entries[d] = _entry(f, calendar)
        else:
            excluded[d] = K.REASON_GEX_NOT_NEGATIVE
    return Schedule("T3", (first, last), entries, excluded)


def schedules(facts: Mapping[date, DateFacts], tests: Sequence[str], first: date, last: date,
              t2_lookback_first: date, gex: Mapping[date, float] | None = None,
              calendar: Any = None) -> dict[str, Schedule]:
    """Every registered test's schedule on one window."""
    out: dict[str, Schedule] = {}
    for test in tests:
        if test == "T1":
            out[test] = t1_schedule(facts, first, last, calendar)
        elif test == "T2":
            out[test] = t2_schedule(facts, first, last, t2_lookback_first, calendar)
        elif test == "T3":
            if gex is None:
                raise ValueError("T3 is registered but no GEX rows were given")
            out[test] = t3_schedule(facts, first, last, gex, calendar)
        else:
            raise ValueError(f"unknown test {test!r}")
    return out


def eligibility_counts(facts: Mapping[date, DateFacts], first: date, last: date) -> dict[str, int]:
    out = {"trade_dates": 0, "eligible": 0, **{r: 0 for r in K.ELIGIBILITY_REASONS}}
    for d in _window_days(facts, first, last):
        out["trade_dates"] += 1
        f = facts[d]
        out["eligible" if f.eligible else str(f.reason)] += 1
    return out


__all__ = ["DateFacts", "Entry", "Schedule", "compute_facts", "eligibility_counts",
           "eligibility_reason", "schedules", "t1_schedule", "t2_schedule", "t2_thresholds",
           "t3_schedule"]
