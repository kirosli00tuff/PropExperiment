"""Test C1's world (c1_replication.world) on SYNTHETIC calendars and frozen synthetic bars.

Ruling C7: CL and MBT carry no bar for any NG row. A frame with NO row cannot be used: the frozen
G17 code indexes the lead's first bar and raises (shown below), so each gets one sentinel bar
after the window. C7's equality test: the NG-row columns of the panel equal those of a context
with synthetic CL bars on every session (CL is NG's own cluster lead, never applicable on NG rows).
Also: the legs are loaded one at a time, NG's excluded dates join its own blackout, refusals.
"""

from __future__ import annotations

import dataclasses
from datetime import date
from types import MappingProxyType

import numpy as np
import pandas as pd
import pytest

from c1_replication.constants import E12_GATE0_LIST, STORE_ROOTS
from c1_replication.context import hist_tables
from c1_replication.evaluate import load_calendars
from c1_replication.world import (
    C7_SENTINEL_DAY,
    WorldError,
    build_world,
    replication_panel,
    sentinel_frame,
)
from tests._c1_fixtures import synthetic_leg, vol_ticks_table, write_inputs

FIRST, LAST_BARS = date(2010, 6, 7), date(2011, 9, 30)
SIGNALS = tuple(__import__("json").loads(E12_GATE0_LIST.read_text())["covered_signals"])
_CACHE: dict = {}


@pytest.fixture(scope="module")
def cal(tmp_path_factory):
    vol_ticks_table()
    from ml_route_v2.synthetic import default_vol_ticks

    _CACHE["cl_vol"] = float(default_vol_ticks("CL"))
    inp = write_inputs(tmp_path_factory.mktemp("c1_world"))
    yield load_calendars(inp.hashes, FIRST, date(2019, 4, 30))
    _CACHE.clear()


def _load(root):
    key = ("leg", root)
    if key not in _CACHE:
        _CACHE[key] = synthetic_leg(root, FIRST, LAST_BARS, seed=11)
    return _CACHE[key]


def test_a_frame_with_no_row_breaks_the_frozen_g17_code():
    from ml_route_v2.phase1.world import compact_bars
    from ml_route_v2.signals import SignalContext
    from ml_route_v2.signals.generic import _lead

    empty = compact_bars(pd.DataFrame({
        "ts_event": np.zeros(0, np.int64), "open": [], "high": [], "low": [], "close": [],
        "volume": np.zeros(0, np.uint32), "instrument_id": np.zeros(0, np.uint32),
        "trade_date": np.zeros(0, object)}))
    t = np.int64(pd.Timestamp("2011-03-03 15:30", tz="UTC").value)
    rows = pd.DataFrame({"root": ["NG"], "path_root": ["NG"], "cluster": ["K4"],
                         "group": ["energy"], "trade_date": [pd.Timestamp("2011-03-03")],
                         "t_index": np.array([1], np.int8),
                         "decision_ts_ns": np.array([t], np.int64),
                         "flatten_ts_ns": np.array([t + 10**12], np.int64)})
    ctx = SignalContext(rows, {"CL": empty}, None, pd.Series([1.0]))
    with pytest.raises(IndexError):
        _lead("CL", ctx)
    ctx2 = SignalContext(rows, {"CL": sentinel_frame()}, None, pd.Series([1.0]))
    out = _lead("CL", ctx2)
    assert out["applicable"].tolist() == [0.0] and out["value"].tolist() == [0.0]


def test_c7_ng_rows_equal_those_with_synthetic_cl_bars(cal):
    from ml_route_v2.phase1.world import compact_bars
    from ml_route_v2.synthetic import _root_bars

    with hist_tables(cal["tables"]):
        world = build_world(_load, cal["releases"].calendar, ())
        cl = _root_bars("CL", FIRST, LAST_BARS, seed=12, vol_ticks=_CACHE["cl_vol"], plants=[],
                        vehicles=("NG",), compact=False)
        with_cl = dataclasses.replace(world, bars=MappingProxyType(
            {**world.bars, "CL": compact_bars(cl)}))
        a = replication_panel(world, SIGNALS)
        b = replication_panel(with_cl, SIGNALS)
    assert len(cl) > 100_000 and len(world.bars["CL"]) == 1
    assert world.bars["CL"]["trade_date"].astype(str).tolist() == [C7_SENTINEL_DAY.isoformat()]
    pd.testing.assert_frame_equal(a.frame, b.frame)
    assert a.feature_cols == b.feature_cols
    assert (a.frame["app_g17_cl"] == 0).all() and (a.frame["app_g17_mbt"] == 0).all()
    assert (a.frame["app_g17_nq"] == 1).any()


def test_world_fields_and_excluded_dates(cal):
    excl = (date(2011, 6, 15), date(2011, 6, 16))
    loaded = []

    def load(root):
        loaded.append(root)
        return _load(root)

    with hist_tables(cal["tables"]):
        w = build_world(load, cal["releases"].calendar, excl)
    assert loaded == list(STORE_ROOTS)
    assert w.vehicles == ("NG",) and set(w.bars) == {*STORE_ROOTS, "CL", "MBT"}
    assert set(excl) <= w.blackout["NG"] and not set(excl) & set(w.calendar)
    assert w.blackout["NQ"] == frozenset(_load("NQ").roll_blackout)
    assert w.calendar[0] == FIRST and w.calendar[-1] == date(2019, 4, 30)
    assert list(w.bars["NG"].columns) == ["ts_event", "open", "high", "low", "close", "volume",
                                          "instrument_id", "trade_date"]
    assert w.roots["NG"]["flagged_bars"] == {"in_scheduled_closure": 0, "vendor_degraded_day": 0}


def test_build_world_refusals(cal):
    with hist_tables(cal["tables"]):
        with pytest.raises(WorldError, match="returned"):
            build_world(lambda r: _load("NG"), cal["releases"].calendar, ())
        late = dataclasses.replace(_load("ZN"), trade_dates=(*_load("ZN").trade_dates,
                                                             date(2019, 5, 2)))
        with pytest.raises(WorldError, match="leave the window"):
            build_world(lambda r: late if r == "ZN" else _load(r), cal["releases"].calendar, ())
