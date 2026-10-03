"""ml_route_v2.clock: the V2.2 decision clock and DecisionRows (synthetic dates only)."""

from __future__ import annotations

from datetime import date, time

import numpy as np
import pandas as pd
import pytest

from ml_route_v2.clock import (
    ROW_COLUMNS,
    ClockError,
    decision_rows,
    decision_times_ct,
    decision_times_from,
    exclude_union,
    minutes_after_midnight_ct,
    session_group,
)
from ml_route_v2.constants import DECISION_TIMES_CT, UNIVERSE


@pytest.mark.parametrize("group", sorted(DECISION_TIMES_CT))
def test_rule_reproduces_the_pinned_table(group: str) -> None:
    assert decision_times_ct(group) == DECISION_TIMES_CT[group]


def test_whole_table_pinned() -> None:
    assert {g: decision_times_ct(g) for g in DECISION_TIMES_CT} == dict(DECISION_TIMES_CT)


def test_rule_on_explicit_sessions() -> None:
    assert decision_times_from(time(7, 20), time(15, 8)) == (time(7, 50), time(10, 20),
                                                             time(12, 50))
    assert decision_times_from(time(8, 30), time(13, 3)) == (time(9, 0), time(10, 0),
                                                             time(11, 0))
    with pytest.raises(ClockError):
        decision_times_from(time(8, 30), time(11, 30))  # fewer than three times


def test_every_vehicle_has_a_session_group() -> None:
    groups = {session_group(v) for v in UNIVERSE}
    assert groups == set(DECISION_TIMES_CT)
    assert session_group("MGC") == "gold" and session_group("MHG") == "copper"


def _ct_times(frame: pd.DataFrame) -> list[time]:
    mins = minutes_after_midnight_ct(frame["decision_ts_ns"].to_numpy())
    return [time(int(m) // 60, int(m) % 60) for m in mins]


def test_rows_schema_sort_and_times() -> None:
    day = date(2023, 6, 6)
    roots = tuple(UNIVERSE)
    rows = decision_rows(roots, {r: [day] for r in roots})
    assert tuple(rows.columns) == ROW_COLUMNS
    assert len(rows) == 3 * len(roots)
    assert rows["t_index"].dtype == np.int8
    assert rows["decision_ts_ns"].dtype == np.int64
    assert str(rows["trade_date"].dtype) == "datetime64[ns]"
    key = list(zip(rows["decision_ts_ns"], rows["root"], strict=True))
    assert key == sorted(key)
    for root in roots:
        sub = rows[rows["root"] == root].sort_values("t_index")
        assert _ct_times(sub) == list(DECISION_TIMES_CT[session_group(root)])
        assert set(sub["path_root"]) == {UNIVERSE[root][1]}
        assert set(sub["cluster"]) == {UNIVERSE[root][0]}


def test_dst_keeps_the_ct_clock() -> None:
    rows = decision_rows(("ZN",), {"ZN": [date(2023, 1, 10), date(2023, 7, 11)]})
    assert _ct_times(rows[rows["trade_date"] == "2023-01-10"]) == \
        _ct_times(rows[rows["trade_date"] == "2023-07-11"])


def test_early_halt_and_early_close_dates_are_excluded() -> None:
    # 2023-07-03: equity early halt; 2022-01-17: a Topstep close-by date (F 11:30) on FX that is
    # not an early halt of the group calendar (reading TC-1); 2023-07-05: a regular date.
    rows = decision_rows(("MNQ", "6E"), {"MNQ": [date(2023, 7, 3), date(2023, 7, 5)],
                                         "6E": [date(2022, 1, 17), date(2023, 7, 5)]})
    days = {(r, str(d.date())) for r, d in zip(rows["root"], rows["trade_date"], strict=True)}
    assert days == {("MNQ", "2023-07-05"), ("6E", "2023-07-05")}


def test_weekend_is_not_a_trade_date() -> None:
    assert decision_rows(("ZC",), {"ZC": [date(2023, 6, 10)]}).empty


def test_exclude_map_drops_dates() -> None:
    days = [date(2023, 6, 5), date(2023, 6, 6)]
    rows = decision_rows(("ZN", "ZB"), {"ZN": days, "ZB": days},
                         exclude={"ZN": frozenset({date(2023, 6, 5)})})
    assert len(rows[rows["root"] == "ZN"]) == 3 and len(rows[rows["root"] == "ZB"]) == 6


def test_exclude_union_adds_the_legs() -> None:
    out = exclude_union({"ZS": frozenset({date(2023, 1, 3)}), "ZM": frozenset({date(2023, 1, 4)})},
                        {"ZS": ("ZM", "ZL"), "ZC": ()})
    assert out == {"ZS": frozenset({date(2023, 1, 3), date(2023, 1, 4)}), "ZC": frozenset()}


def test_flatten_is_after_every_horizon() -> None:
    roots = tuple(UNIVERSE)
    rows = decision_rows(roots, {r: [date(2023, 6, 6)] for r in roots})
    t3 = rows[rows["t_index"] == 3]
    assert ((t3["flatten_ts_ns"] - t3["decision_ts_ns"]) >= 120 * 60_000_000_000).all()


def test_unknown_root_raises() -> None:
    with pytest.raises(ClockError):
        decision_rows(("ES",), {"ES": [date(2023, 6, 6)]})


def test_deterministic() -> None:
    days = {"MBT": [date(2022, 3, 1), date(2022, 3, 2)]}
    pd.testing.assert_frame_equal(decision_rows(("MBT",), days), decision_rows(("MBT",), days))
