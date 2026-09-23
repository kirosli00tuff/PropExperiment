"""Stage D.1f step 7: the frozen list's members and their daily series (list 2.1 to 2.3, 3.1,
3.2(ii)). Used by ``_d1f_confirmation``; the decision rules are in ``_d1f_decisions``.

TIER A TRIALS (A1, A3): the 31 of ``strategy.research._d1d_accounting.ALL_TRIALS`` (imported,
never retyped) with E-H1 and E-H2 swapped for the confirmation factories of the 5.7 amendment,
verbatim, then the six Family H trials of ``h_daily_bar.H_TRIALS``. The swap is keyed on the
factory object, not on a label. Classes come from the label prefixes of list 2.3.

A TRIAL'S DAILY SERIES (3.1, R-1): d_t = sum over the trips that close on window date t of
trip_pnl_usd / (1.25 x trip_micros), 0 on a date without a closed trip. ``daily_n_trips``
partitions ``trip_pnls_usd`` in ledger order.

STATISTICS (A2, 2.2): Tier A = the 21 ids of the A2 table with s FROM THE TABLE (checked
against the sign of the recorded implied edge); Tier B = the 43 ids of 2.2, s = the sign of the
recorded implied edge in the facts files ``_d1e_event_series`` reads. Per event
v = s x e - 2.11; d_t = sum of v on each of the statistic's own post-exclusion dates.

A TIER A STATISTIC'S COMPOSITE (3.2(ii), R-10): the gate call on its events (p = share of
v > 0, ties neither side; R = mean positive v / mean |negative v|; T =
nearest_segments_per_day(events per own date); standard path, robust), exactly as
``screening.runner._gate`` does for trips, plus both drift sub-checks as
``screening.drift`` applies them to trips. Each event is a ``TripDrift`` with, in cents per
micro, gross = s x e x 125, cost = 2.11 x 125 and drift = s x (window-mean move over the
event's forward interval) x 125; ``drift_significance`` and the adjusted-p/R gate then run
unchanged. The drift path is built on the statistic's own post-exclusion date set (the dates
being screened; roll blackout and vendor-degraded dates excluded), a reading of "window-mean".

LEAD RULING (e): the drift charge of an interval across a daily halt or weekend (F4.4 only)
sums the drift path's per-minute mean changes over every clock-minute bar the interval
covers, halt minutes contributing 0. The interval starts at the crossing bar's open. For the
first covered bar the change is close - open, for a bar following one of the same trade date
it is close - previous close, and for the first bar after the halt it is close - open (the
halt gap is not charged). A trade date with no bar in the statistic's set (an excluded date
the scan steps over) contributes 0 in the same way. Each change is the path's mean over the
days that have both prices. ``forward_mean_moves_ticks`` refuses such events, so this module
implements the ruling; events on one trade date go through the wrapper unchanged.
"""

from __future__ import annotations

import dataclasses
import json
from collections.abc import Callable, Mapping, Sequence
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from screening.drift import DriftPath, TripDrift, build_drift_path, drift_significance
from screening.runner import _gate, _p_and_r
from strategy.research._d1d_accounting import ALL_TRIALS
from strategy.research._d1e_event_series import F_FACTS_PATH, G_FACTS_PATH
from strategy.research._d1f_decisions import STAT_COST_TICKS, Member
from strategy.research._d1f_statistics import StatisticEvents, forward_mean_moves_ticks
from strategy.research.e_calendar_event._release_table_2019_2024 import RELEASE_TABLE_2019_2024
from strategy.research.e_calendar_event.h1_scheduled_macro_drift import (
    RELEASE_TABLE_ET,
    H1ScheduledMacroDrift,
)
from strategy.research.e_calendar_event.h2_post_release_momentum import H2PostReleaseMomentum
from strategy.research.h_daily_bar import H_TRIALS

TICK_VALUE_USD = 1.25
CENTS_PER_TICK = 125.0

# The two confirmation factories, verbatim as the 5.7 amendment writes them (list 2.1 A1).
CONFIRMATION_FACTORIES: dict[object, Callable[[], object]] = {
    H1ScheduledMacroDrift:
        lambda: H1ScheduledMacroDrift(release_table=RELEASE_TABLE_ET | RELEASE_TABLE_2019_2024),
    H2PostReleaseMomentum:
        lambda: H2PostReleaseMomentum(release_table=RELEASE_TABLE_ET | RELEASE_TABLE_2019_2024),
}

# Class by label prefix (list 2.3); longest prefix first so C-H4 is C6, not C3.
_TRIAL_CLASS_PREFIXES = (
    ("C-H4", "C6"), ("A-H", "C1"), ("B-H", "C2"), ("RT1 ", "C2"), ("RT2 ", "C2"),
    ("RT3 ", "C2"), ("RT4 ", "C2"), ("C-H", "C3"), ("RT5 ", "C3"), ("D-H", "C4"),
    ("RT6 ", "C4"), ("RT7 ", "C4"), ("E-H", "C5"),
)
TRIAL_CLASS_COUNTS = {"C1": 6, "C2": 10, "C3": 4, "C4": 6, "C5": 4, "C6": 1, "C7": 6}

# List 2.1 A2: (id in the facts file, class, s), s from the table.
TIER_A_STATISTICS: tuple[tuple[str, str, int], ...] = (
    ("F3_2_bucket07_bucket08", "C3", -1), ("F6_1_overnight_range_position", "C2", 1),
    ("F3_3_opening_30min_to_close_momentum", "C3", -1), ("F3_2_bucket08_bucket09", "C3", -1),
    ("F3_3_overnight_to_close_momentum", "C3", -1),
    ("F4_4_round_number_multiples_of_100", "C2", -1), ("F3_2_bucket01_bucket02", "C3", 1),
    ("F3_2_bucket10_bucket11", "C3", 1), ("F4_1_rth_open_crossing", "C2", -1),
    ("F3_2_bucket02_bucket03", "C3", 1), ("F3_2_bucket05_bucket06", "C3", 1),
    ("F3_2_bucket04_bucket05", "C3", 1), ("F3_2_bucket06_bucket07", "C3", -1),
    ("F3_2_bucket12_bucket13", "C3", 1), ("G2.RTH.30", "C2", 1), ("G1.RTH.5", "C3", 1),
    ("G2.ETH.30", "C2", -1), ("G2.ETH.5", "C2", -1), ("G5.RTH.15", "C2", -1),
    ("G5.RTH.30", "C2", 1), ("G3.RTH.15", "C2", -1),
)
# List 2.2, spelled out as the list spells it (checked against "the 64 minus Tier A").
TIER_B_STATISTICS: tuple[str, ...] = (
    *(f"F1_1_h{h}_{seg}" for seg in ("RTH", "ETH") for h in (1, 5, 15, 30, 60)),
    "F2_4_15min_vol_tercile_bottom", "F2_4_15min_vol_tercile_top",
    "F3_2_bucket03_bucket04", "F3_2_bucket09_bucket10", "F3_2_bucket11_bucket12",
    "F4_2_prior_rth_close_crossing", "F4_4_round_number_multiples_of_50",
    "F5_1_relvol_tercile_bottom", "F5_1_relvol_tercile_top", "F5_2_efficiency_tercile_bottom",
    "F5_2_efficiency_tercile_top", "F5_3_range_volume_residual",
    "G1.ETH.5", "G2.RTH.5", "G3.RTH.5", "G4.RTH.5", "G5.RTH.5", "G1.ETH.15", "G2.ETH.15",
    "G1.RTH.15", "G2.RTH.15", "G4.RTH.15", "G1.ETH.30", "G1.RTH.30", "G3.RTH.30", "G4.RTH.30",
    "G1.ETH.60", "G2.ETH.60", "G1.RTH.60", "G2.RTH.60", "G3.RTH.60", "G4.RTH.60", "G5.RTH.60",
)
_STAT_CLASS_PREFIXES = (("F1_1", "C3"), ("F2_4", "C4"), ("F3_", "C3"), ("F4_", "C2"),
                        ("F5_", "C4"), ("F6_1", "C2"), ("G1.", "C3"), ("G4.", "C3"),
                        ("G2.", "C2"), ("G3.", "C2"), ("G5.", "C2"))


def trial_class(label: str) -> str:
    for prefix, klass in _TRIAL_CLASS_PREFIXES:
        if label.startswith(prefix):
            return klass
    raise ValueError(f"no class for trial label {label!r}")


def statistic_class(stat_id: str) -> str:
    for prefix, klass in _STAT_CLASS_PREFIXES:
        if stat_id.startswith(prefix):
            return klass
    raise ValueError(f"no class for statistic {stat_id!r}")


def tier_a_trials() -> tuple[tuple[str, Callable[[], object], str], ...]:
    """(label, confirmation factory, class) for the 37 Tier A trials, in list order."""
    swapped = [f for _, f in ALL_TRIALS if f in CONFIRMATION_FACTORIES]
    if len(swapped) != len(CONFIRMATION_FACTORIES) or len(ALL_TRIALS) != 31:
        raise AssertionError("ALL_TRIALS no longer holds the 31 trials with E-H1 and E-H2 once")
    out = [(label, CONFIRMATION_FACTORIES.get(f, f), trial_class(label)) for label, f in ALL_TRIALS]
    out += [(label, f, "C7") for label, f in H_TRIALS]
    counts = {k: sum(1 for *_, c in out if c == k) for k in TRIAL_CLASS_COUNTS}
    if counts != TRIAL_CLASS_COUNTS:
        raise AssertionError(f"trial classes {counts} != list 2.3 {TRIAL_CLASS_COUNTS}")
    return tuple(out)


def continuity_trials() -> tuple[tuple[str, Callable[[], object], str], ...]:
    """The 31 no-argument factories, then E-H1 and E-H2 under their confirmation factories
    (list 1.4, 2.1 A1 NEW-1: both factories must reproduce the train union to the cent)."""
    base = [(label, f, "default") for label, f in ALL_TRIALS]
    base += [(label, CONFIRMATION_FACTORIES[f], "confirmation_factory")
             for label, f in ALL_TRIALS if f in CONFIRMATION_FACTORIES]
    return tuple(base)


# ------------------------------------------------------------------- trials ----
def per_micro_daily(trip_pnls_usd: Sequence[float], trip_micros: Sequence[int],
                    daily_n_trips: Sequence[int]) -> np.ndarray:
    """3.1: per window date, the sum of the per-micro net ticks of the trips that closed that
    date (each trip over $1.25 x its OWN micros); ``daily_n_trips`` partitions the trips."""
    if len(trip_pnls_usd) != len(trip_micros):
        raise AssertionError(f"{len(trip_pnls_usd)} trip P&Ls but {len(trip_micros)} sizes")
    if any(q < 1 for q in trip_micros):
        raise AssertionError("a closed trip reports fewer than 1 micro")
    if sum(daily_n_trips) != len(trip_pnls_usd) or any(n < 0 for n in daily_n_trips):
        raise AssertionError(f"daily trip counts sum to {sum(daily_n_trips)}, but the run "
                             f"holds {len(trip_pnls_usd)} trips")
    ticks = [p / (TICK_VALUE_USD * q) for p, q in zip(trip_pnls_usd, trip_micros, strict=True)]
    out, cut = np.zeros(len(daily_n_trips)), 0
    for i, n in enumerate(daily_n_trips):
        out[i] = float(sum(ticks[cut:cut + n]))
        cut += n
    return out


def trial_member(label: str, klass: str, report: Mapping, window_dates: Sequence[date],
                 extra: Mapping | None = None) -> Member:
    """A Tier A trial member from a ScreeningReport's ``to_dict()``."""
    if int(report["n_dates"]) != len(window_dates):
        raise AssertionError(f"{label}: report covers {report['n_dates']} dates, window "
                             f"{len(window_dates)}")
    daily = per_micro_daily(report["trip_pnls_usd"], report["trip_micros"],
                            report["daily_n_trips"])
    summary = {k: v for k, v in report.items()
               if k not in ("trip_pnls_usd", "daily_n_trips", "trip_micros", "daily_net_usd")}
    return Member(label, "A", "trial", klass, tuple(window_dates), daily,
                  np.asarray(report["daily_n_trips"], dtype=np.int64), report["verdict"],
                  None, {"screening": summary, **(extra or {})})


# --------------------------------------------------------------- statistics ----
def recorded_edges(f_facts: Path = F_FACTS_PATH, g_facts: Path = G_FACTS_PATH
                   ) -> dict[str, float]:
    """Recorded implied edges of the 64 directional statistics (the EDA facts files)."""
    out: dict[str, float] = {}
    for path in (f_facts, g_facts):
        for row in json.loads(Path(path).read_text())["tested_statistics"]:
            if row.get("directional"):
                out[row["id"]] = row["implied_edge_ticks"]
    return out


def statistic_directions(edges: Mapping[str, float]) -> dict[str, tuple[str, str, int]]:
    """id -> (tier, class, s). Tier A's s from the table, checked against the recorded sign;
    Tier B's s = sign of the recorded edge. Refuses a zero or missing edge."""
    ids_a = [sid for sid, _, _ in TIER_A_STATISTICS]
    if len(set(ids_a)) != 21 or len(set(TIER_B_STATISTICS)) != 43 or len(edges) != 64:
        raise AssertionError("the list needs 21 Tier A and 43 Tier B of 64 statistics")
    if set(edges) - set(ids_a) != set(TIER_B_STATISTICS):
        raise AssertionError("Tier B is not the 64 directional statistics minus Tier A")
    def sign(sid: str) -> int:
        edge = edges.get(sid)
        if edge is None or not np.isfinite(edge) or edge == 0:
            raise AssertionError(f"{sid}: recorded implied edge {edge!r} has no sign")
        return int(np.sign(edge))

    out = {}
    for sid, klass, s in TIER_A_STATISTICS:
        if klass != statistic_class(sid) or s != sign(sid):
            raise AssertionError(f"{sid}: table class/s disagree with the rule/recorded edge")
        out[sid] = ("A", klass, s)
    for sid in TIER_B_STATISTICS:
        out[sid] = ("B", statistic_class(sid), sign(sid))
    return out


def _daily_sums(values: np.ndarray, event_dates: Sequence[date], dates: Sequence[date]
                ) -> tuple[np.ndarray, np.ndarray]:
    index = {d: i for i, d in enumerate(dates)}
    sums, counts = np.zeros(len(dates)), np.zeros(len(dates), dtype=np.int64)
    for d, v in zip(event_dates, values, strict=True):
        sums[index[d]] += v
        counts[index[d]] += 1
    return sums, counts


def _subset(ev: StatisticEvents, mask: np.ndarray) -> StatisticEvents:
    pick = np.flatnonzero(mask)
    return dataclasses.replace(
        ev, values=ev.values[pick], trade_dates=tuple(ev.trade_dates[i] for i in pick),
        start_bar_ts_ns=ev.start_bar_ts_ns[pick],
        start_price=tuple(ev.start_price[i] for i in pick), end_bar_ts_ns=ev.end_bar_ts_ns[pick],
        end_price=tuple(ev.end_price[i] for i in pick),
        end_trade_dates=tuple(ev.end_trade_dates[i] for i in pick))


def halt_crossing_move_ticks(start_ts: int, end_ts: int, path: DriftPath,
                             bar_ts: np.ndarray, bar_days: np.ndarray) -> float:
    """Lead ruling (e) for one interval (start at a bar's OPEN, end at a bar's CLOSE): the sum
    of the path's per-minute mean changes over every bar the interval covers, 0 across a halt.
    ``bar_ts`` / ``bar_days``: the statistic's bars in ts order, the ones the path holds."""
    first, last = int(np.searchsorted(bar_ts, start_ts)), int(np.searchsorted(bar_ts, end_ts))
    if (first >= len(bar_ts) or last >= len(bar_ts) or bar_ts[first] != start_ts
            or bar_ts[last] != end_ts or last < first):
        raise ValueError("interval points are not bars of the statistic's bar set")
    total = 0.0
    for row in range(first, last + 1):
        _, minute = path.locator[int(bar_ts[row])]
        same_day = row > first and bar_days[row] == bar_days[row - 1]
        if same_day:
            _, previous = path.locator[int(bar_ts[row - 1])]
            total += path.mean_move_ticks((previous, "close"), (minute, "close"))
        else:  # the first covered bar, or the first bar after a halt: its own open to close
            total += path.mean_move_ticks((minute, "open"), (minute, "close"))
    return total


def forward_moves_ticks(ev: StatisticEvents, path: DriftPath, stat_bars: pd.DataFrame
                        ) -> np.ndarray:
    """Per event, the window-mean move over its forward interval: the wrapper's
    ``forward_mean_moves_ticks`` on one trade date, lead ruling (e) across a halt."""
    out = np.empty(len(ev.values))
    crossing = ev.crosses_trade_date if len(ev.values) else np.zeros(0, dtype=bool)
    if (~crossing).any():
        out[~crossing] = forward_mean_moves_ticks(_subset(ev, ~crossing), path)
    if crossing.any():
        if any(p != "open" for p, c in zip(ev.start_price, crossing, strict=True) if c) or any(
                p != "close" for p, c in zip(ev.end_price, crossing, strict=True) if c):
            raise ValueError(f"{ev.stat_id}: a halt-crossing interval must run open -> close")
        bar_ts = stat_bars["ts_event"].to_numpy(np.int64)
        bar_days = stat_bars["trade_date"].astype(str).to_numpy()
        for i in np.flatnonzero(crossing):
            out[i] = halt_crossing_move_ticks(int(ev.start_bar_ts_ns[i]),
                                              int(ev.end_bar_ts_ns[i]), path, bar_ts, bar_days)
    return out


def statistic_composite(ev: StatisticEvents, s: int, dates: Sequence[date],
                        stat_bars: pd.DataFrame, gate_json: Path) -> dict:
    """3.2(ii) for a statistic: the robust gate on its events plus both drift sub-checks."""
    v = s * ev.values - STAT_COST_TICKS
    n_per_day = len(v) / len(dates)
    p, r = _p_and_r([float(x) for x in v])
    zero_edge = _gate(p, r, n_per_day, gate_json)
    path = build_drift_path(stat_bars, frozenset())
    moves = forward_moves_ticks(ev, path, stat_bars)
    trips = tuple(TripDrift(d, float(s * e * CENTS_PER_TICK), STAT_COST_TICKS * CENTS_PER_TICK,
                            float(s * m * CENTS_PER_TICK))
                  for d, e, m in zip(ev.trade_dates, ev.values, moves, strict=True))
    significance = drift_significance(trips, tuple(dates))
    adj_p, adj_r = _p_and_r([t.adjusted_net_cents / 100.0 for t in trips])
    adjusted = _gate(adj_p, adj_r, n_per_day, gate_json)
    drift_ok = significance.passes and adjusted.robust == "pass"
    verdict = "pass" if zero_edge.robust == "pass" and drift_ok else "fail"
    return {"verdict": verdict, "zero_edge": dataclasses.asdict(zero_edge),
            "drift_adjusted": dataclasses.asdict(adjusted),
            "drift": {**dataclasses.asdict(significance),
                      "excess_lower_bounds_usd_per_micro": {
                          f"c{round(c * 100)}": b
                          for c, b in significance.excess_lower_bounds_usd.items()}},
            "drift_verdict": "pass" if drift_ok else "fail",
            "n_halt_crossing_events": int(ev.crosses_trade_date.sum()) if len(v) else 0,
            "drift_path_dates": "the statistic's own post-exclusion dates",
            "units": "drift figures in USD per micro (ticks x $1.25)"}


def statistic_member(ev: StatisticEvents, tier: str, klass: str, s: int,
                     dates: Sequence[date], composite: dict | None = None) -> Member:
    """A statistic member on its own post-exclusion dates (3.1)."""
    v = s * ev.values - STAT_COST_TICKS
    daily, counts = _daily_sums(v, ev.trade_dates, dates)
    extra = {"family": ev.family, "description": ev.description, "n_events": int(len(v)),
             "confirmation_estimate": ev.estimate, "confirmation_n": ev.n,
             "confirmation_implied_edge_ticks": ev.implied_edge_ticks,
             "gross_mean_s_times_e_per_event": float(np.mean(s * ev.values)) if len(v) else None,
             "extra": dict(ev.extra)}
    if composite is not None:
        extra["composite_detail"] = composite
    return Member(ev.stat_id, tier, "statistic", klass, tuple(dates), daily, counts,
                  None if composite is None else composite["verdict"], s, extra)
