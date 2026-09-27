"""Synthetic inputs for the ML route's tests and probes. No market data is read.

- ``synthetic_bars``: random-walk one-minute bars on a product's real group calendar and D6/D9
  session times, from O_X - ``pre_minutes`` to F_X + 2 minutes of every trade date, in the step 2
  store's schema (data/build_bars.py research schema).
- ``write_step2_store``: writes such frames as a step 2 store tree
  (<root>/<ROOT>/ohlcv-1m_<ROOT>_v_0_2019-05-06_2024-02-29_step2.parquet, metadata store=step2).
- ``synthetic_inputs``: a RouteInputs with the real frozen products and D8 costs, and a synthetic
  release calendar and S_X table passed in explicitly.
- ``synthetic_matrix``: a feature matrix and target of a given size for the timed probes.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from ml_route.constants import TRAIN_LAST
from ml_route.inputs import (
    EventCalendar,
    RouteInputs,
    day_times,
    load_products,
    load_vehicle_costs,
)
from ml_route.store import META_KEY, step2_file_name

NS_MIN = 60_000_000_000


def synthetic_bars(root: str, group: str, first: date, last: date, seed: int,
                   tick: float = 0.25, start_price: float = 4000.0, pre_minutes: int = 150,
                   ) -> pd.DataFrame:
    """Random-walk bars on every trade date of ``root``'s group calendar in [first, last]."""
    from data.group_session import trade_dates_between
    from ml_route.inputs import _group_calendar

    rng = np.random.default_rng(seed)
    rows: list[pd.DataFrame] = []
    price = start_price
    for day in trade_dates_between(_group_calendar(group), first, last):
        dt = day_times(root, group, day)
        if dt is None:
            continue
        start = dt.open_ns - pre_minutes * NS_MIN
        ts = np.arange(start, dt.flatten_ns + 3 * NS_MIN, NS_MIN, dtype=np.int64)
        steps = rng.integers(-3, 4, size=len(ts)) * tick
        closes = price + np.cumsum(steps)
        opens = np.concatenate([[price], closes[:-1]])
        price = float(closes[-1])
        wig = rng.integers(0, 3, size=len(ts)) * tick
        rows.append(pd.DataFrame({
            "ts_event": ts, "open": opens, "high": np.maximum(opens, closes) + wig,
            "low": np.minimum(opens, closes) - wig, "close": closes,
            "volume": rng.integers(1, 400, size=len(ts)).astype(np.uint64),
            "instrument_id": np.full(len(ts), 1, dtype=np.uint32),
            "raw_symbol": root + "Z9", "in_flatten_window": ts >= dt.flatten_ns,
            "in_no_new_positions_window": ts >= dt.flatten_ns, "early_halt_ct": "",
            "in_scheduled_closure": False, "trade_date": day.isoformat(),
            "is_roll_session": False, "gap_before_minutes": 0, "vendor_degraded_day": False}))
    return pd.concat(rows, ignore_index=True)


def write_step2_store(store_root: Path, frames: Mapping[str, pd.DataFrame],
                      blackout: Mapping[str, Iterable[date]] | None = None) -> dict[str, Path]:
    out = {}
    for root, frame in frames.items():
        path = Path(store_root) / root / step2_file_name(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        meta = {"store": "step2", "stage": "synthetic (ml_route.synthetic)",
                "roll_blackout_dates": sorted(d.isoformat()
                                              for d in (blackout or {}).get(root, ())),
                "trade_date_range": [str(frame["trade_date"].min()),
                                     str(frame["trade_date"].max())]}
        table = pa.Table.from_pandas(frame, preserve_index=False)
        table = table.replace_schema_metadata({**(table.schema.metadata or {}),
                                               META_KEY: json.dumps(meta).encode()})
        pq.write_table(table, path)
        out[root] = path
    return out


def synthetic_events(roots: Iterable[str], first: date, last: date, seed: int
                     ) -> EventCalendar:
    """A release at 07:30 CT on a few weekdays a month for every product; CPI on the 12th-ish."""
    rng = np.random.default_rng(seed)
    days = pd.bdate_range(first, last)
    picks = days[rng.random(len(days)) < 0.15]
    at = pd.Timedelta(hours=7, minutes=30)
    rel = (pd.DatetimeIndex(picks).tz_localize("America/Chicago") + at
           ).tz_convert("UTC").as_unit("ns").asi8.astype(np.int64)
    cpi_days = days[(days.day >= 10) & (days.day <= 12)][::3]
    cpi = (pd.DatetimeIndex(cpi_days).tz_localize("America/Chicago") + at
           ).tz_convert("UTC").as_unit("ns").asi8.astype(np.int64)
    rel = np.sort(rel)
    return EventCalendar({r: rel for r in roots}, np.sort(cpi), "synthetic", "0" * 64)


def synthetic_inputs(s_x: Mapping[str, date], events: EventCalendar) -> RouteInputs:
    products = load_products()
    return RouteInputs(products, load_vehicle_costs(products), events, dict(s_x),
                       {"synthetic": "true"})


def synthetic_matrix(n_rows: int, n_features: int, n_products: int, seed: int,
                     n_dates: int = 1200) -> dict[str, np.ndarray]:
    """Random features and a weakly predictable target of the real shapes (for probes)."""
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n_rows, n_features)).astype(np.float32)
    y = (0.05 * X[:, 0] + rng.standard_normal(n_rows)).astype(np.float32)
    product = rng.integers(0, n_products, size=n_rows)
    day = np.sort(rng.integers(0, n_dates, size=n_rows))
    return {"X": X, "y": y, "product": product, "day": day,
            "cost": np.full(n_rows, 0.05, dtype=np.float32)}


def last_train_date() -> date:
    return TRAIN_LAST


def bars_from_frame(root: str, frame: pd.DataFrame):  # noqa: ANN201 - ml_route.features.Bars
    """A store-schema frame as the pipeline's in-memory Bars."""
    from ml_route.features import Bars

    return Bars(root, frame["ts_event"].to_numpy(np.int64), frame["open"].to_numpy(np.float64),
                frame["high"].to_numpy(np.float64), frame["low"].to_numpy(np.float64),
                frame["close"].to_numpy(np.float64), frame["volume"].to_numpy(np.float64),
                frame["instrument_id"].to_numpy(np.int64),
                pd.to_datetime(frame["trade_date"]).to_numpy().astype("datetime64[D]"))
