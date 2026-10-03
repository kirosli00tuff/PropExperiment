"""V2.5 targets: gross h-forward moves in vehicle ticks, D8 round trips, normalized targets.

docs/STAGE_E_ML_V2_DESIGN.md V2.4 (sigma_X,d) and V2.5; contract reports/stage_e11_interfaces.md
section 4. For a decision row at t (decision_ts_ns) of vehicle X with flatten F_X:
- entry: the open of the bar opening at t; a fill time in the vehicle's D9.5a guard
  [release, release + 2 min) is deferred to the first bar at or after release + 2 min (again while
  that bar is guarded), as the engine's admit_fill defers a strategy order (screening/
  stage_e_rules.py:375); a deferred entry with less than D9.3's 2 minutes before F_X is skipped
  (missing), as is an entry in D9.12's CPI window [CPI - 5, CPI + 5] min on a vehicle of
  rules.constraints.CPI_NO_OPEN (none of the v2 vehicles is; kept for parity);
- exit, h in {h60, h120}: the open of the bar opening at t + h, which exists only if t + h <= F_X;
  a guarded exit fill is deferred as above (v1 ml_route/rows.py deferred_exit, OC-M) and a
  deferral reaching F_X is superseded by the forced flatten; hF: the open of the bar opening at
  F_X, the engine's forced flatten fill (exempt from the guard, RR-3);
- y_gross_<h> = (open(exit) - open(entry)) x vehicle ticks per vendor unit; absent bars: NaN;
- cost_long_<h> = commission_rt / tick value + buy side at the entry minute + sell side at the
  exit minute; cost_short_<h> = commission + sell side at entry + buy side at exit; a side is
  screening.stage_e_frozen.ProductCosts.side_slippage_ticks at that CT minute, with D8's event
  window [release, release + 30 min) (largest half-spread plus the bucket's depth term, T12-4);
  a minute no calibrated bucket covers: NaN;
- y_norm_<h> = y_gross / sigma_X,d (v1 ML-A06, signals._daily); ok_<h>: every one of y_gross,
  both costs and sigma_X,d present (sigma > 0).
- ``cost_missing_counts``: per (root, horizon), the rows whose gross move is formed but whose
  fill minute has no calibrated cost bucket (a cost NaN), which ok_<h> drops from training and
  scoring; panel.build_panel puts them in Panel.counts (code review C-05).
Columns: entry_price (vendor units of the price path), entry_ts_ns (addition), sigma_d, then per
horizon y_gross, cost_long, cost_short, exit_ts_ns, y_norm, ok.
"""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import suppress
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from ml_route_v2.clock import minutes_after_midnight_ct
from ml_route_v2.constants import HORIZON_MINUTES, HORIZONS, UNIVERSE
from ml_route_v2.signals._core import (
    NS_MIN,
    BarArrays,
    bar_arrays,
    cpi_times,
    path_of,
    per_unit,
    release_times,
)
from ml_route_v2.signals._daily import build_daily
from rules.constraints import CPI_HALF_WINDOW
from screening.stage_e_engine import EVENT_WINDOW_NS, FILL_GUARD_NS, MIN_HOLD_NS

CT = ZoneInfo("America/Chicago")
CPI_HALF_WINDOW_NS = int(CPI_HALF_WINDOW.total_seconds()) * 1_000_000_000  # D9.12
_COST_REFERENCE_DAY = (2021, 1, 4)  # any date: a bucket depends on the CT minute only
MINUTES_PER_DAY = 1440


class TargetInputMissing(RuntimeError):
    """A target input (a vehicle's bars or cost model) is not available."""


def frozen_costs(vehicles: tuple[str, ...] | None = None) -> dict[str, Any]:
    """The frozen D8 leg inputs (screening.stage_e_frozen.leg_inputs) of the vehicles."""
    from screening.stage_e_frozen import leg_inputs

    return {v: leg_inputs(v, traded=True) for v in (vehicles or tuple(UNIVERSE))}


def _arrays(bars: Mapping[str, pd.DataFrame], path: str, memo: dict) -> BarArrays:
    if path not in memo:
        if path not in bars:
            raise TargetInputMissing(f"no bars for {path}")
        memo[path] = bar_arrays(path, bars[path])
    return memo[path]


def _row_days(rows: pd.DataFrame) -> np.ndarray:
    return rows["trade_date"].to_numpy().astype("datetime64[D]").astype(np.int64)


def sigma_d(rows: pd.DataFrame, bars: Mapping[str, pd.DataFrame], *,
            _memo: dict | None = None) -> pd.Series:
    """sigma_X,d in vehicle ticks aligned to rows (v1 ML-A06; signals._daily.build_daily)."""
    memo = {} if _memo is None else _memo
    out = np.full(len(rows), np.nan)
    days = _row_days(rows)
    root = rows["root"].to_numpy(object)
    for v in pd.unique(root):
        sel = np.flatnonzero(root == v)
        dl = build_daily(str(v), _arrays(bars, path_of(str(v)), memo))
        pos = dl.pos(days[sel])
        out[sel] = np.where(pos >= 0, dl.sigma[np.clip(pos, 0, None)], np.nan)
    return pd.Series(out, index=rows.index, name="sigma_d")


def _cost_parts(cost: Any, vehicle: str) -> tuple[Any, float]:
    """(ProductCosts, commission round trip in ticks) from a LegInputs or a ProductCosts."""
    from rules.products import product

    pc = getattr(cost, "costs", None)
    if pc is not None:
        return pc, float(pc.commission_rt_cents) / float(cost.tick_value_cents)
    if hasattr(cost, "side_slippage_ticks"):
        tv_cents = float(product(vehicle).tick_value_usd) * 100.0
        return cost, float(cost.commission_rt_cents) / tv_cents
    raise TargetInputMissing(f"{vehicle}: the cost input has no D8 cost model")


def minute_table(pc: Any) -> np.ndarray:
    """side ticks per CT minute: shape (1440, 2 event flags, 2 sides buy/sell); NaN uncovered."""
    from screening.stage_e_frozen import CostLookupError

    out = np.full((MINUTES_PER_DAY, 2, 2), np.nan)
    y, m, d = _COST_REFERENCE_DAY
    for minute in range(MINUTES_PER_DAY):
        when = datetime(y, m, d, minute // 60, minute % 60, tzinfo=CT)
        for ev in (0, 1):
            for s, side in enumerate(("buy", "sell")):
                with suppress(CostLookupError):  # no calibrated bucket: NaN stays
                    out[minute, ev, s] = pc.side_slippage_ticks(when, side, bool(ev))
    return out


def _in_window(when: np.ndarray, rel: np.ndarray, width: int) -> np.ndarray:
    """True where the latest release at or before ``when`` is less than ``width`` ns earlier."""
    if len(rel) == 0:
        return np.zeros(len(when), dtype=bool)
    k = np.searchsorted(rel, when, side="right") - 1
    ok = k >= 0
    out = np.zeros(len(when), dtype=bool)
    out[ok] = when[ok] < rel[k[ok]] + width
    return out


def _defer(b: BarArrays, rel: np.ndarray, when: np.ndarray, flatten: np.ndarray, *,
           to_flatten: bool) -> tuple[np.ndarray, np.ndarray]:
    """(fill time, bar index) of fills at ``when`` after the D9.5a deferral. A deferral reaching
    F_X ends at the flatten bar (``to_flatten``, an exit) or is refused (index -2, an entry)."""
    fill = when.copy()
    idx = b.at(when)
    for r in np.flatnonzero(_in_window(when, rel, FILL_GUARD_NS)):
        at = int(when[r])
        while True:
            k = int(np.searchsorted(rel, at, side="right")) - 1
            if k < 0 or at >= int(rel[k]) + FILL_GUARD_NS:
                break
            j = int(np.searchsorted(b.ts, int(rel[k]) + FILL_GUARD_NS, side="left"))
            if j >= len(b.ts) or int(b.ts[j]) >= int(flatten[r]):
                at = -1
                break
            at = int(b.ts[j])
        if at < 0:
            if to_flatten:
                fill[r], idx[r] = flatten[r], int(b.at(np.array([flatten[r]]))[0])
            else:
                fill[r], idx[r] = -1, -2
            continue
        fill[r], idx[r] = at, int(b.at(np.array([at]))[0])
    return fill, idx


def _side_ticks(table: np.ndarray, when: np.ndarray, event: np.ndarray, side: int
                ) -> np.ndarray:
    out = np.full(len(when), np.nan)
    ok = when > 0
    if ok.any():
        minute = minutes_after_midnight_ct(when[ok])
        out[ok] = table[minute, event[ok].astype(int), side]
    return out


def _vehicle_targets(v: str, b: BarArrays, t: np.ndarray, flat: np.ndarray, days: np.ndarray,
                     rel: np.ndarray, cpi: np.ndarray, cost: Any) -> dict[str, np.ndarray]:
    from rules.constraints import CPI_NO_OPEN

    pu = per_unit(v)
    pc, comm = _cost_parts(cost, v)
    table = minute_table(pc)
    entry_ns, i_e = _defer(b, rel, t, flat, to_flatten=False)
    ok_e = (i_e >= 0) & b.on_day(np.where(i_e >= 0, i_e, -1), days)
    ok_e &= (flat - entry_ns) >= MIN_HOLD_NS
    if v in CPI_NO_OPEN:
        ok_e &= ~_in_window(entry_ns + CPI_HALF_WINDOW_NS, cpi, 2 * CPI_HALF_WINDOW_NS + 1)
    entry_open = np.where(ok_e, b.open[np.clip(i_e, 0, None)], np.nan)
    ev_e = _in_window(entry_ns, rel, EVENT_WINDOW_NS)
    out: dict[str, np.ndarray] = {"entry_price": entry_open,
                                  "entry_ts_ns": np.where(ok_e, entry_ns, -1)}
    for h in HORIZONS:
        mins = HORIZON_MINUTES[h]
        if mins is None:
            x_ns, i_x = flat.copy(), b.at(flat)
            exists = np.ones(len(t), dtype=bool)
        else:
            nominal = t + mins * NS_MIN
            exists = nominal <= flat
            x_ns, i_x = _defer(b, rel, np.where(exists, nominal, t), flat, to_flatten=True)
        ok = ok_e & exists & (i_x >= 0) & b.on_day(np.where(i_x >= 0, i_x, -1), days)
        ok &= (x_ns - entry_ns) >= MIN_HOLD_NS
        y = np.where(ok, (b.open[np.clip(i_x, 0, None)] - entry_open) * pu, np.nan)
        ev_x = _in_window(x_ns, rel, EVENT_WINDOW_NS)
        e_ns = np.where(ok, entry_ns, -1)
        xx = np.where(ok, x_ns, -1)
        out[f"y_gross_{h}"] = y
        out[f"cost_long_{h}"] = comm + _side_ticks(table, e_ns, ev_e, 0) + \
            _side_ticks(table, xx, ev_x, 1)
        out[f"cost_short_{h}"] = comm + _side_ticks(table, e_ns, ev_e, 1) + \
            _side_ticks(table, xx, ev_x, 0)
        out[f"exit_ts_ns_{h}"] = xx.astype(np.int64)
    return out


def build_targets(rows: pd.DataFrame, bars: Mapping[str, pd.DataFrame], *, releases: Any,
                  costs: Mapping[str, Any]) -> pd.DataFrame:
    """The targets frame aligned to rows (module docstring)."""
    memo: dict = {}
    n = len(rows)
    sig = sigma_d(rows, bars, _memo=memo).to_numpy()
    cols: dict[str, np.ndarray] = {"entry_price": np.full(n, np.nan),
                                   "entry_ts_ns": np.full(n, -1, np.int64), "sigma_d": sig}
    for h in HORIZONS:
        for stem in ("y_gross", "cost_long", "cost_short"):
            cols[f"{stem}_{h}"] = np.full(n, np.nan)
        cols[f"exit_ts_ns_{h}"] = np.full(n, -1, np.int64)
    days = _row_days(rows)
    root = rows["root"].to_numpy(object)
    t_all = rows["decision_ts_ns"].to_numpy(np.int64)
    f_all = rows["flatten_ts_ns"].to_numpy(np.int64)
    cpi = cpi_times(releases)
    for v in pd.unique(root):
        v = str(v)
        if v not in costs:
            raise TargetInputMissing(f"no D8 cost input for {v}")
        sel = np.flatnonzero(root == v)
        part = _vehicle_targets(v, _arrays(bars, path_of(v), memo), t_all[sel], f_all[sel],
                                days[sel], release_times(releases, v), cpi, costs[v])
        for k, arr in part.items():
            cols[k][sel] = arr
    good_sigma = np.isfinite(sig) & (sig > 0)
    for h in HORIZONS:
        y = cols[f"y_gross_{h}"]
        cols[f"y_norm_{h}"] = np.where(good_sigma, y / np.where(good_sigma, sig, 1.0), np.nan)
        cols[f"ok_{h}"] = (np.isfinite(y) & np.isfinite(cols[f"cost_long_{h}"])
                           & np.isfinite(cols[f"cost_short_{h}"]) & good_sigma)
    order = ["entry_price", "entry_ts_ns", "sigma_d"]
    for h in HORIZONS:
        order += [f"y_gross_{h}", f"cost_long_{h}", f"cost_short_{h}", f"exit_ts_ns_{h}",
                  f"y_norm_{h}", f"ok_{h}"]
    return pd.DataFrame({k: cols[k] for k in order}, index=rows.index)


def cost_missing_counts(frame: pd.DataFrame) -> dict[str, int]:
    """``cost_missing_<root>_<h>``: rows with a finite y_gross_<h> and a NaN cost_long_<h> or
    cost_short_<h> (no calibrated cost bucket at a fill minute; C-05). Nonzero pairs only."""
    root = frame["root"].to_numpy(object)
    out: dict[str, int] = {}
    for h in HORIZONS:
        lost = (np.isfinite(frame[f"y_gross_{h}"].to_numpy(np.float64))
                & ~(np.isfinite(frame[f"cost_long_{h}"].to_numpy(np.float64))
                    & np.isfinite(frame[f"cost_short_{h}"].to_numpy(np.float64))))
        for r in sorted(map(str, pd.unique(root[lost]))):
            out[f"cost_missing_{r}_{h}"] = int((lost & (root == r)).sum())
    return out


__all__ = ["TargetInputMissing", "build_targets", "cost_missing_counts", "frozen_costs",
           "minute_table", "sigma_d"]
