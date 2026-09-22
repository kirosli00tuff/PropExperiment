"""The one way Stage D.1d builds a coarser bar: declaration section 1, rules R1-R7.

Two implementations of the same rule live here on purpose:

- ``coarse_bars(frame, tf)`` is the vectorised form the stylized facts use.
- ``CoarseBarBuilder`` is the incremental, bar-by-bar form every D.1d strategy uses
  inside ``on_bar``. It sees only completed 1-minute bars, so it cannot look ahead.

``tests/test_d1d_resample.py`` pins that the two produce identical bars whenever the
1-minute feed runs past each segment's end, which every research trade date does (a
slot-less bar, e.g. 15:00 CT, flushes the builder's pending slot). The one known
divergence, documented by that file's strict ``xfail``: a feed that STOPS inside a slot
leaves the builder's last accumulator unreturned (rule R6 completes a bar only on a later
bar), while ``coarse_bars`` emits it as a short bar. No D.1d result touches that case.

The rules, restated in code terms (session minute 0 = 17:00 CT, the Globex reopen):

- ETH is ``[0, min(930, limit))`` and RTH is ``[930, min(1320, limit))``, where ``limit``
  is the session minute of the no-new-positions time (15:08 CT on a normal day, earlier
  before a CME early close). The early-close time is read from the bar's own
  ``early_halt_ct``, but only for bars on the trade date's own calendar day (session
  minute >= 420, i.e. after 00:00 CT); an evening bar carries the PREVIOUS calendar
  day's halt, which is already over.
- A slot is ``[start + j*tf, start + (j+1)*tf)`` inside its segment and exists only if it
  ends at or before the segment's end. Nothing is truncated or extended.
- A coarse bar is the OHLCV aggregate of the 1-minute bars whose open falls in the slot.
  Missing minutes do not drop it; two instrument ids do.
- A coarse bar completes at the decision time of the 1-minute bar opening in its last
  minute. If that minute is missing, it completes late, on the next bar the strategy
  receives (``completed_late=True``).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, time

import numpy as np
import pandas as pd

from data.session import CME_TZ
from rules.xfa_rules import no_new_positions_time_ct
from strategy.interface import Bar

TIMEFRAMES = (5, 15, 30, 60)
TICK = 0.25
SESSION_OPEN_MINUTE_CT = 17 * 60
DAY_MINUTES = 1440
ETH_START = 0
ETH_NOMINAL_END = 930  # 08:30 CT
RTH_START = 930
RTH_NOMINAL_END = 1320  # 15:00 CT
MIDNIGHT_SESSION_MINUTE = 420  # 00:00 CT: from here on, a bar is on its trade date's own day
SEGMENTS = ("ETH", "RTH")
_SEGMENT_START = {"ETH": ETH_START, "RTH": RTH_START}
_SEGMENT_NOMINAL_END = {"ETH": ETH_NOMINAL_END, "RTH": RTH_NOMINAL_END}


def session_minute(ct_minute_of_day: int) -> int:
    """Minute of the trade date's session, 0 at 17:00 CT."""
    return (ct_minute_of_day - SESSION_OPEN_MINUTE_CT) % DAY_MINUTES


def _time_to_session_minute(at: time) -> int:
    return session_minute(at.hour * 60 + at.minute)


DEFAULT_LIMIT = _time_to_session_minute(no_new_positions_time_ct(None))  # 15:08 CT -> 1328


def limit_minute(bar_session_minute: int, early_halt_ct: time | None) -> int:
    """Session minute of the no-new-positions time that governs this bar's trade date."""
    if early_halt_ct is None or bar_session_minute < MIDNIGHT_SESSION_MINUTE:
        return DEFAULT_LIMIT
    return _time_to_session_minute(no_new_positions_time_ct(early_halt_ct))


def segment_end(segment: str, limit: int) -> int:
    return min(_SEGMENT_NOMINAL_END[segment], limit)


def slot_count(segment: str, tf: int, limit: int) -> int:
    """How many ``tf``-minute slots the segment holds under this limit (0 if none)."""
    return max(0, (segment_end(segment, limit) - _SEGMENT_START[segment]) // tf)


@dataclass(frozen=True, slots=True)
class Slot:
    segment: str
    index: int
    start: int  # session minute
    end: int


def slot_of(bar_session_minute: int, tf: int, limit: int) -> Slot | None:
    """The slot a 1-minute bar belongs to, or None if the minute is in no coarse bar."""
    for segment in SEGMENTS:
        start, end = _SEGMENT_START[segment], segment_end(segment, limit)
        if start <= bar_session_minute < end:
            index = (bar_session_minute - start) // tf
            slot_end = start + (index + 1) * tf
            if slot_end <= end:
                return Slot(segment, index, start + index * tf, slot_end)
            return None
    return None


# ------------------------------------------------------------------ vectorised ----
def _halt_to_limit(halt: str) -> int:
    if not halt:
        return DEFAULT_LIMIT
    return _time_to_session_minute(no_new_positions_time_ct(time.fromisoformat(halt)))


def annotate_session(frame: pd.DataFrame) -> pd.DataFrame:
    """Copy of ``frame`` with ``session_minute`` and ``limit`` columns (rule R2)."""
    out = frame.copy()
    local = pd.to_datetime(out["ts_event"], unit="ns", utc=True).dt.tz_convert(CME_TZ)
    out["session_minute"] = ((local.dt.hour * 60 + local.dt.minute - SESSION_OPEN_MINUTE_CT)
                             % DAY_MINUTES).to_numpy()
    halts = out["early_halt_ct"].fillna("").astype(str)
    limit_by_halt = {h: _halt_to_limit(h) for h in halts.unique()}
    own_day = out["session_minute"].to_numpy() >= MIDNIGHT_SESSION_MINUTE
    out["limit"] = np.where(own_day, halts.map(limit_by_halt).to_numpy(), DEFAULT_LIMIT)
    return out


def _assign_slots(annotated: pd.DataFrame, tf: int) -> pd.DataFrame:
    sm = annotated["session_minute"].to_numpy()
    limit = annotated["limit"].to_numpy()
    eth_end = np.minimum(ETH_NOMINAL_END, limit)
    rth_end = np.minimum(RTH_NOMINAL_END, limit)
    in_eth = sm < eth_end
    in_rth = (sm >= RTH_START) & (sm < rth_end)
    seg_start = np.where(in_eth, ETH_START, RTH_START)
    seg_end = np.where(in_eth, eth_end, rth_end)
    index = (sm - seg_start) // tf
    slot_start = seg_start + index * tf
    slot_end = slot_start + tf
    valid = (in_eth | in_rth) & (slot_end <= seg_end)
    out = annotated.loc[valid].copy()
    out["segment"] = np.where(in_eth[valid], "ETH", "RTH")
    out["slot"] = index[valid]
    out["slot_start"] = slot_start[valid]
    out["slot_end"] = slot_end[valid]
    return out


def coarse_bars(frame: pd.DataFrame, tf: int) -> pd.DataFrame:
    """Rules R1-R5 over a whole frame of 1-minute bars (``ts_event`` order required).

    Columns: trade_date, segment, slot, start, end, open, high, low, close, volume,
    n_minutes, instrument_id. Sorted by trade date, then start.
    """
    if tf not in TIMEFRAMES:
        raise ValueError(f"tf {tf!r} is not one of {TIMEFRAMES}")
    if not frame["ts_event"].is_monotonic_increasing:
        raise ValueError("frame must be in ts_event order")
    slotted = _assign_slots(annotate_session(frame), tf)
    keys = ["trade_date", "segment", "slot"]
    out = slotted.groupby(keys, sort=False).agg(
        start=("slot_start", "first"), end=("slot_end", "first"),
        open=("open", "first"), high=("high", "max"), low=("low", "min"),
        close=("close", "last"), volume=("volume", "sum"), n_minutes=("close", "size"),
        instrument_id=("instrument_id", "first"), n_instruments=("instrument_id", "nunique"),
    ).reset_index()
    out = out[out["n_instruments"] == 1].drop(columns="n_instruments")
    out["trade_date"] = pd.to_datetime(out["trade_date"].astype(str)).dt.date
    return out.sort_values(["trade_date", "start"], kind="stable").reset_index(drop=True)


def missing_minute_share(coarse: pd.DataFrame, tf: int) -> dict[str, float]:
    """Descriptive: the share of coarse bars with at least one missing minute, per segment."""
    out = {}
    for segment in SEGMENTS:
        sub = coarse[coarse["segment"] == segment]
        out[segment] = float((sub["n_minutes"] < tf).mean()) if len(sub) else float("nan")
    return out


# ----------------------------------------------------------------- incremental ----
@dataclass(frozen=True, slots=True)
class CoarseBar:
    trade_date: date
    segment: str
    slot: int
    start: int
    end: int
    open: float
    high: float
    low: float
    close: float
    volume: int
    n_minutes: int
    instrument_id: int
    completed_late: bool

    @property
    def body(self) -> float:
        return self.close - self.open

    @property
    def range(self) -> float:
        return self.high - self.low


def bar_session_minute(bar: Bar) -> int:
    local = bar.open_ts_utc.astimezone(CME_TZ)
    return session_minute(local.hour * 60 + local.minute)


def bar_limit(bar: Bar) -> int:
    return limit_minute(bar_session_minute(bar), bar.early_halt_ct)


@dataclass(frozen=True, slots=True)
class _Accumulator:
    slot: Slot
    bar: CoarseBar
    instrument_ids: frozenset[int]

    def add(self, bar: Bar) -> _Accumulator:
        b = self.bar
        merged = replace(b, high=max(b.high, bar.high), low=min(b.low, bar.low),
                         close=bar.close, volume=b.volume + bar.volume,
                         n_minutes=b.n_minutes + 1)
        return _Accumulator(self.slot, merged, self.instrument_ids | {bar.instrument_id})

    def completed(self, late: bool) -> CoarseBar | None:
        if len(self.instrument_ids) != 1:
            return None  # rule R4: a slot spanning two instrument ids is dropped
        return replace(self.bar, completed_late=late)


def _start(bar: Bar, slot: Slot) -> _Accumulator:
    first = CoarseBar(bar.trade_date, slot.segment, slot.index, slot.start, slot.end,
                      bar.open, bar.high, bar.low, bar.close, bar.volume, 1,
                      bar.instrument_id, completed_late=False)
    return _Accumulator(slot, first, frozenset({bar.instrument_id}))


class CoarseBarBuilder:
    """Rule R6: feed 1-minute bars in order; get each coarse bar back the moment it completes.

    A slot whose last minute is missing completes late, on the next bar pushed, whatever
    slot or trade date that bar belongs to; strategies check ``coarse.trade_date`` before
    acting on one. A slot spanning two instrument ids is never returned.
    """

    def __init__(self, tf: int) -> None:
        if tf not in TIMEFRAMES:
            raise ValueError(f"tf {tf!r} is not one of {TIMEFRAMES}")
        self.tf = tf
        self._pending: _Accumulator | None = None

    def push(self, bar: Bar) -> tuple[CoarseBar, ...]:
        minute = bar_session_minute(bar)
        slot = slot_of(minute, self.tf, limit_minute(minute, bar.early_halt_ct))
        done: list[CoarseBar | None] = []
        pending = self._pending
        if pending is not None and (slot is None or pending.bar.trade_date != bar.trade_date
                                    or pending.slot != slot):
            done.append(pending.completed(late=True))
            pending = None
        if slot is not None:
            pending = _start(bar, slot) if pending is None else pending.add(bar)
            if minute == slot.end - 1:
                done.append(pending.completed(late=False))
                pending = None
        self._pending = pending
        return tuple(b for b in done if b is not None)
