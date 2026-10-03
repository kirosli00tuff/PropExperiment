"""ml_route_v2.targets: hand-computed gross moves, D8 round trips and normalized targets (V2.5).

A tiny synthetic world: MNQ (NQ price path) on 26 trade dates, random-walk bars on the real
equity calendar, the frozen D8 cost table (screening.stage_e_frozen.leg_inputs), and a release
calendar planted to hit the D9.5a guard and the D8 event window.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from types import MappingProxyType

import numpy as np
import pandas as pd
import pytest

from ml_route_v2.clock import decision_rows, trade_dates_of
from ml_route_v2.constants import HORIZONS
from ml_route_v2.signals.synthetic_bars import session_bars
from ml_route_v2.targets import build_targets, frozen_costs, sigma_d

NS_MIN = 60_000_000_000
FIRST, LAST = date(2023, 1, 3), date(2023, 2, 8)
PU = 4.0  # MNQ ticks per NQ index point: 1 / (vendor factor 1 x tick 0.25)


def _releases(instants: list[int]):  # noqa: ANN202 - ReleaseCalendar
    from screening.stage_e_rules import ReleaseCalendar

    rel = tuple(sorted(instants))
    return ReleaseCalendar(MappingProxyType({"MNQ": rel, "NQ": rel}), (), FIRST, LAST, "0" * 64,
                           "test")


@pytest.fixture(scope="module")
def world() -> tuple[pd.DataFrame, pd.DataFrame]:
    bars = session_bars("NQ", FIRST, LAST, seed=11)
    rows = decision_rows(("MNQ",), {"MNQ": trade_dates_of(bars)})
    return bars, rows


def _open_at(bars: pd.DataFrame, ns: int) -> float:
    hit = bars.loc[bars["ts_event"] == ns, "open"]
    assert len(hit) == 1
    return float(hit.iloc[0])


def _side(ns: int, side: str, event: bool) -> float:
    from screening.stage_e_frozen import leg_inputs

    pc = leg_inputs("MNQ", traded=True).costs
    return pc.side_slippage_ticks(datetime.fromtimestamp(ns / 1e9, UTC), side, event)


def _commission() -> float:
    from screening.stage_e_frozen import leg_inputs

    li = leg_inputs("MNQ", traded=True)
    return li.costs.commission_rt_cents / float(li.tick_value_cents)


def _sigma_by_hand(bars: pd.DataFrame, day: pd.Timestamp) -> float:
    ct = pd.to_datetime(bars["ts_event"], utc=True).dt.tz_convert("America/Chicago")
    hm = ct.dt.strftime("%H:%M")
    td = pd.to_datetime(bars["trade_date"])
    moves = []
    for d in sorted(td[td < day].unique())[::-1]:  # complete dates only (an early halt is not)
        o = bars.loc[(td == d) & (hm == "08:30") & (ct.dt.date == pd.Timestamp(d).date()), "open"]
        c = bars.loc[(td == d) & (hm == "14:59") & (ct.dt.date == pd.Timestamp(d).date()),
                     "close"]
        if len(o) and len(c):
            moves.append(abs(float(c.iloc[0]) - float(o.iloc[0])) * PU)
        if len(moves) == 20:
            break
    assert len(moves) == 20
    return float(np.mean(moves))


def test_hand_computed_row(world: tuple) -> None:
    bars, rows = world
    tg = build_targets(rows, {"NQ": bars}, releases=_releases([]), costs=frozen_costs(("MNQ",)))
    i = len(rows) - 2  # t2 of the last date (sigma has 20 prior dates)
    t = int(rows["decision_ts_ns"].iloc[i])
    f = int(rows["flatten_ts_ns"].iloc[i])
    entry = _open_at(bars, t)
    sig = _sigma_by_hand(bars, rows["trade_date"].iloc[i])
    assert tg["sigma_d"].iloc[i] == pytest.approx(sig)
    assert tg["entry_price"].iloc[i] == entry
    for h, x in (("h60", t + 60 * NS_MIN), ("h120", t + 120 * NS_MIN), ("hF", f)):
        y = (_open_at(bars, x) - entry) * PU
        assert tg[f"y_gross_{h}"].iloc[i] == pytest.approx(y)
        assert tg[f"cost_long_{h}"].iloc[i] == pytest.approx(
            _commission() + _side(t, "buy", False) + _side(x, "sell", False))
        assert tg[f"cost_short_{h}"].iloc[i] == pytest.approx(
            _commission() + _side(t, "sell", False) + _side(x, "buy", False))
        assert tg[f"y_norm_{h}"].iloc[i] == pytest.approx(y / sig)
        assert tg[f"exit_ts_ns_{h}"].iloc[i] == x
        assert bool(tg[f"ok_{h}"].iloc[i])


def test_entry_in_the_fill_guard_is_deferred(world: tuple) -> None:
    bars, rows = world
    i = len(rows) - 3
    t = int(rows["decision_ts_ns"].iloc[i])
    tg = build_targets(rows, {"NQ": bars}, releases=_releases([t - NS_MIN]),
                       costs=frozen_costs(("MNQ",)))
    entry_ns = t + NS_MIN  # the first bar at or after release + 2 min
    assert tg["entry_ts_ns"].iloc[i] == entry_ns
    assert tg["entry_price"].iloc[i] == _open_at(bars, entry_ns)
    x = t + 60 * NS_MIN
    assert tg["y_gross_h60"].iloc[i] == pytest.approx((_open_at(bars, x)
                                                       - _open_at(bars, entry_ns)) * PU)
    # the deferred entry is still in the event window: the event side applies
    assert tg["cost_long_h60"].iloc[i] == pytest.approx(
        _commission() + _side(entry_ns, "buy", True) + _side(x, "sell", False))


def test_exit_in_the_event_window_and_in_the_guard(world: tuple) -> None:
    bars, rows = world
    i = len(rows) - 1  # t3
    t = int(rows["decision_ts_ns"].iloc[i])
    x = t + 60 * NS_MIN
    rel = [x - 10 * NS_MIN, t + 120 * NS_MIN]  # h60 exit 10 min after a release; h120 guarded
    tg = build_targets(rows, {"NQ": bars}, releases=_releases(rel), costs=frozen_costs(("MNQ",)))
    assert tg["cost_short_h60"].iloc[i] == pytest.approx(
        _commission() + _side(t, "sell", False) + _side(x, "buy", True))
    deferred = t + 122 * NS_MIN
    assert tg["exit_ts_ns_h120"].iloc[i] == deferred
    assert tg["y_gross_h120"].iloc[i] == pytest.approx((_open_at(bars, deferred)
                                                        - _open_at(bars, t)) * PU)


def test_horizon_beyond_flatten_and_missing_bars(world: tuple) -> None:
    bars, rows = world
    i = len(rows) - 2
    short = rows.copy()
    short.loc[short.index[i], "flatten_ts_ns"] = int(short["decision_ts_ns"].iloc[i]) \
        + 90 * NS_MIN
    tg = build_targets(short, {"NQ": bars}, releases=_releases([]), costs=frozen_costs(("MNQ",)))
    assert bool(tg["ok_h60"].iloc[i]) and not bool(tg["ok_h120"].iloc[i])
    assert np.isnan(tg["y_gross_h120"].iloc[i]) and tg["exit_ts_ns_h120"].iloc[i] == -1
    t = int(rows["decision_ts_ns"].iloc[i])
    holed = bars[bars["ts_event"] != t + 60 * NS_MIN]
    tg2 = build_targets(rows, {"NQ": holed}, releases=_releases([]), costs=frozen_costs(("MNQ",)))
    assert not bool(tg2["ok_h60"].iloc[i]) and np.isnan(tg2["y_gross_h60"].iloc[i])
    assert bool(tg2["ok_hF"].iloc[i])


def test_layout_warm_up_and_determinism(world: tuple) -> None:
    bars, rows = world
    a = build_targets(rows, {"NQ": bars}, releases=_releases([]), costs=frozen_costs(("MNQ",)))
    b = build_targets(rows, {"NQ": bars}, releases=_releases([]), costs=frozen_costs(("MNQ",)))
    pd.testing.assert_frame_equal(a, b)
    want = ["entry_price", "entry_ts_ns", "sigma_d"]
    for h in HORIZONS:
        want += [f"y_gross_{h}", f"cost_long_{h}", f"cost_short_{h}", f"exit_ts_ns_{h}",
                 f"y_norm_{h}", f"ok_{h}"]
    assert list(a.columns) == want
    first20 = rows["trade_date"].isin(sorted(rows["trade_date"].unique())[:20]).to_numpy()
    assert a.loc[first20, "sigma_d"].isna().all() and not a.loc[first20, "ok_h60"].any()
    assert a.loc[~first20, "ok_hF"].all()
    pd.testing.assert_series_equal(a["sigma_d"], sigma_d(rows, {"NQ": bars}))


def test_missing_cost_input_raises(world: tuple) -> None:
    from ml_route_v2.targets import TargetInputMissing

    bars, rows = world
    with pytest.raises(TargetInputMissing):
        build_targets(rows, {"NQ": bars}, releases=_releases([]), costs={})


def test_cost_missing_rows_are_counted_per_root_and_horizon() -> None:
    """Code review C-05: a row whose gross move is formed but whose fill minute has no
    calibrated cost bucket (a cost NaN) is counted per (root, horizon); a row without a gross
    move, or with both costs, is not."""
    from ml_route_v2.targets import cost_missing_counts

    nan = float("nan")
    frame = pd.DataFrame({"root": ["MNQ", "MNQ", "MGC", "MGC", "MGC"]})
    for h in HORIZONS:
        frame[f"y_gross_{h}"] = [1.0, 2.0, nan, 3.0, 4.0]
        frame[f"cost_long_{h}"] = [nan, 1.0, nan, 1.0, nan]
        frame[f"cost_short_{h}"] = [1.0, nan, nan, 1.0, 1.0]
    frame.loc[0, "cost_long_h60"] = 1.0  # MNQ's first row has both costs at h60 only
    got = cost_missing_counts(frame)
    assert got == {"cost_missing_MNQ_h60": 1, "cost_missing_MGC_h60": 1,
                   "cost_missing_MGC_h120": 1, "cost_missing_MNQ_h120": 2,
                   "cost_missing_MGC_hF": 1, "cost_missing_MNQ_hF": 2}
    full = frame.assign(**{f"cost_{s}_{h}": 1.0 for s in ("long", "short") for h in HORIZONS})
    assert cost_missing_counts(full) == {}
