"""t4 decision rows (reports/stage_e20_plan.md section 4; F6 addition 1) on the synthetic 17-vehicle
world: one t4 per (vehicle, trade date) the frozen clock kept, at F_X - 60 min, identifiers copied,
the frozen t1-t3 rows untouched, and build_targets' own rule keeping t4 out of h120."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pattern_search import constants as K
from pattern_search.rows import RowsError, frozen_rows, t4_rows, with_t4
from tests._pattern_search_synth import rows_small, world_small

# The plan's t4 clock (section 4), by vehicle, as CT "HH:MM"
T4_CT = {**{v: "14:08" for v in ("MNQ", "M2K", "ZT", "ZF", "ZN", "TN", "ZB", "UB", "6E", "MCL",
                                 "NG", "MGC")},
         **{v: "12:18" for v in ("ZC", "ZS", "ZL")}, **{v: "12:03" for v in ("HE", "LE")}}
NS_MIN = 60_000_000_000


def _ct(ns: np.ndarray) -> np.ndarray:
    idx = pd.to_datetime(ns, utc=True).tz_convert("America/Chicago")
    return np.asarray(idx.strftime("%H:%M"))


def test_every_vehicle_of_the_universe_has_rows_at_all_four_times() -> None:
    rows = rows_small()
    assert sorted(set(rows["root"])) == sorted(K.VEHICLES)
    assert set(rows["t_index"].unique().tolist()) == {1, 2, 3, 4}


def test_one_t4_row_per_kept_vehicle_date_at_f_minus_60() -> None:
    rows = rows_small()
    t1 = rows.loc[rows["t_index"] == 1]
    t4 = rows.loc[rows["t_index"] == K.T4_INDEX]
    key = ["root", "trade_date"]
    assert not t4.duplicated(key).any()
    assert set(map(tuple, t1[key].astype(str).to_numpy())) == \
        set(map(tuple, t4[key].astype(str).to_numpy()))
    assert (t4["decision_ts_ns"].to_numpy() == t4["flatten_ts_ns"].to_numpy() - 60 * NS_MIN).all()


def test_t4_is_at_the_plans_ct_minute_for_every_group() -> None:
    t4 = rows_small().loc[lambda r: r["t_index"] == K.T4_INDEX]
    got = pd.Series(_ct(t4["decision_ts_ns"].to_numpy()), index=t4.index)
    for v, want in T4_CT.items():
        assert set(got[t4["root"] == v]) == {want}, v


def test_t4_rows_copy_the_identifier_columns_of_their_date() -> None:
    rows = rows_small()
    t1 = rows.loc[rows["t_index"] == 1].set_index(["root", "trade_date"])
    t4 = rows.loc[rows["t_index"] == K.T4_INDEX].set_index(["root", "trade_date"])
    t1 = t1.loc[t4.index]
    for col in ("path_root", "cluster", "group", "flatten_ts_ns"):
        assert (t1[col].to_numpy() == t4[col].to_numpy()).all(), col


def test_t4_is_later_than_t3_and_the_frozen_rows_are_untouched() -> None:
    w = world_small()
    frozen = frozen_rows(w)
    rows = rows_small()
    back = rows.loc[rows["t_index"] < K.T4_INDEX].reset_index(drop=True)
    pd.testing.assert_frame_equal(back, frozen.reset_index(drop=True))
    t3 = rows.loc[rows["t_index"] == 3].set_index(["root", "trade_date"])["decision_ts_ns"]
    t4 = rows.loc[rows["t_index"] == 4].set_index(["root", "trade_date"])["decision_ts_ns"]
    assert (t4.to_numpy() > t3.loc[t4.index].to_numpy()).all()


def test_the_rows_keep_the_frozen_sort_and_dtypes() -> None:
    from ml_route_v2.clock import ROW_COLUMNS

    rows = rows_small()
    assert list(rows.columns) == list(ROW_COLUMNS)
    assert isinstance(rows.index, pd.RangeIndex)
    order = rows.sort_values(["decision_ts_ns", "root"], kind="mergesort").index
    assert (order == rows.index).all()
    assert rows["t_index"].dtype == np.int8
    assert rows["decision_ts_ns"].dtype == np.int64 and rows["flatten_ts_ns"].dtype == np.int64
    assert str(rows["trade_date"].dtype) == "datetime64[ns]"


def test_t4_rows_refuse_rows_that_already_hold_t4() -> None:
    with pytest.raises(RowsError, match="t1-t3"):
        t4_rows(rows_small())


def test_with_t4_on_no_rows_is_empty() -> None:
    from ml_route_v2.clock import ROW_COLUMNS

    empty = frozen_rows(world_small()).iloc[:0]
    out = with_t4(empty)
    assert len(out) == 0 and list(out.columns) == list(ROW_COLUMNS)


def test_targets_keep_t4_out_of_h120_and_exit_h60_at_the_flatten_bar() -> None:
    from ml_route_v2.targets import build_targets

    w = world_small()
    rows = rows_small()
    tg = build_targets(rows, w.bars, releases=w.releases, costs=w.costs)
    t4 = (rows["t_index"] == K.T4_INDEX).to_numpy()
    assert not tg["ok_h120"].to_numpy(bool)[t4].any()
    assert tg["ok_h120"].to_numpy(bool)[~t4].any()
    ok = tg["ok_h60"].to_numpy(bool) & tg["ok_hF"].to_numpy(bool) & t4
    assert ok.sum() > 100
    flat = rows["flatten_ts_ns"].to_numpy(np.int64)
    assert (tg["exit_ts_ns_h60"].to_numpy(np.int64)[ok] == flat[ok]).all()
    assert (tg["exit_ts_ns_hF"].to_numpy(np.int64)[ok] == flat[ok]).all()
    np.testing.assert_array_equal(tg["y_gross_h60"].to_numpy()[ok], tg["y_gross_hF"].to_numpy()[ok])
