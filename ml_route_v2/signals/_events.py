"""Event helpers of the member signals (V2.3 "Rule for member variables").

- ``event_rows``: a member variable defined once per event date (a WPSR move, a fix move) enters
  every decision row of the same trade date whose t is at or after the value's availability; an
  event later that day, or no event, is "not applicable" (0 plus applicable 0).
- ``fixed_clock``: a fixed-clock member has no variable; its event enters as minutes to the event
  (applicable while the event is still ahead on that trade date) and minutes since the event
  (applicable once it has happened), from a calendar known in advance. The same-day flag is the
  sum of the two applicability flags. Availability = t (calendar values, as v1 F13-F15).
- ``slot_rows``: a member variable evaluated at several clock slots per date (hourly returns,
  5-minute blocks) enters as its value at the latest slot whose availability is at or before t.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd

from ml_route_v2.signals._core import (
    NS_MIN,
    RowsView,
    SignalContext,
    apply_event,
    empty,
    lookup_days,
    result,
    rows_of,
)


def event_rows(view: RowsView, rows: np.ndarray, ev_days: np.ndarray, ev_value: np.ndarray,
               ev_avail: np.ndarray) -> pd.DataFrame:
    """A signal frame from one value per event date (``ev_days`` sorted unique epoch days)."""
    out = empty(view)
    if len(rows) and len(ev_days):
        pos = lookup_days(view.day[rows], ev_days)
        on = pos >= 0
        p = np.clip(pos, 0, None)
        apply_event(view, rows, ev_value[p], ev_avail[p], on, out)
    return result(view, *out)


def fixed_clock(view: RowsView, rows: np.ndarray, ev_days: np.ndarray, ev_ns: np.ndarray
                ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(minutes to, minutes since) frames of a fixed-clock event; one or more instants per trade
    date (``ev_days`` aligned to ``ev_ns``)."""
    to_v, to_a, to_av = empty(view)
    si_v, si_a, si_av = empty(view)
    ok = ev_ns > 0
    order = np.argsort(ev_ns[ok], kind="mergesort")
    inst, days = ev_ns[ok][order], ev_days[ok][order]
    if len(rows) and len(inst):
        t, d = view.t[rows], view.day[rows]
        nxt = np.searchsorted(inst, t, side="right")
        has_n = nxt < len(inst)
        has_n[has_n] = days[nxt[has_n]] == d[has_n]
        prv = nxt - 1
        has_p = prv >= 0
        has_p[has_p] = days[prv[has_p]] == d[has_p]
        r_n, r_p = rows[has_n], rows[has_p]
        to_v[r_n] = (inst[nxt[has_n]] - t[has_n]) / NS_MIN
        to_a[r_n] = True
        to_av[r_n] = t[has_n]
        si_v[r_p] = (t[has_p] - inst[prv[has_p]]) / NS_MIN
        si_a[r_p] = True
        si_av[r_p] = t[has_p]
    return result(view, to_v, to_a, to_av), result(view, si_v, si_a, si_av)


def cached_pair(ctx: SignalContext, key: str,
                build: Callable[[SignalContext], tuple[pd.DataFrame, pd.DataFrame]]
                ) -> tuple[pd.DataFrame, pd.DataFrame]:
    ck = ("pair", key)
    if ck not in ctx.cache:
        ctx.cache[ck] = build(ctx)
    return ctx.cache[ck]


def slot_rows(view: RowsView, rows: np.ndarray, slot_avail: np.ndarray, slot_value: np.ndarray,
              on: np.ndarray) -> pd.DataFrame:
    """``slot_avail``/``slot_value`` are (len(rows), S) arrays of each row's date's slots, in time
    order; the row takes the latest slot with avail <= t (none: not applicable)."""
    value, app, avail = empty(view)
    if len(rows):
        t = view.t[rows][:, None]
        known = (slot_avail > 0) & (slot_avail <= t)
        any_k = known.any(axis=1) & on
        last = slot_avail.shape[1] - 1 - np.argmax(known[:, ::-1], axis=1)
        sel = rows[any_k]
        k = last[any_k]
        value[sel] = slot_value[any_k, k]
        avail[sel] = slot_avail[any_k, k]
        app[sel] = True
    return result(view, value, app, avail)


def combine(frames: list[pd.DataFrame]) -> pd.DataFrame:
    """One frame from per-vehicle frames whose applicable rows are disjoint (column by column, so
    int64 availability never passes through float)."""
    acc = {c: frames[0][c].to_numpy().copy() for c in ("value", "applicable", "avail_ts_ns")}
    for f in frames[1:]:
        on = f["applicable"].to_numpy() > 0
        for c in acc:
            acc[c][on] = f[c].to_numpy()[on]
    return pd.DataFrame(acc, index=frames[0].index)


def nothing(view: RowsView) -> pd.DataFrame:
    """A frame where nothing applies (no row of the signal's vehicles)."""
    return result(view, *empty(view))


def per_vehicle(ctx: SignalContext, vehicles: tuple[str, ...],
                fn: Callable[[str, np.ndarray], pd.DataFrame]) -> pd.DataFrame:
    """combine(fn(vehicle, rows)) over the vehicles that have rows; bars of a vehicle without
    rows are never read."""
    view = rows_of(ctx)
    frames = []
    for v in vehicles:
        rows = view.where_root((v,))
        if len(rows):
            frames.append(fn(v, rows))
    return combine(frames) if frames else nothing(view)


def vehicle_rows(ctx: SignalContext, vehicles: tuple[str, ...]) -> tuple[RowsView, np.ndarray]:
    view = rows_of(ctx)
    return view, view.where_root(vehicles)


__all__ = ["cached_pair", "combine", "event_rows", "fixed_clock", "nothing", "per_vehicle",
           "slot_rows", "vehicle_rows"]
