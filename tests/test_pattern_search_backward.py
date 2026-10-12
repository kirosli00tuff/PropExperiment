"""The 2010-2019 swap context and the lead's rulings (reports/stage_e20_plan.md section 10.1), and a
reduced Step 6 dry check. Calendars, release files and synthetic sentinel bars only."""

from __future__ import annotations

from datetime import date, datetime
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from pattern_search import backward as B
from pattern_search import constants as K
from pattern_search import dry_check as D

CT = "America/Chicago"
NS_MIN = 60_000_000_000


@pytest.fixture(scope="module")
def tables():  # noqa: ANN201
    return B.backward_tables()


@pytest.fixture(scope="module")
def rules():  # noqa: ANN201
    return B.backward_release_rules()


def _ct_hhmm(ns: np.ndarray) -> list[str]:
    idx = pd.DatetimeIndex(pd.to_datetime(np.asarray(ns, dtype=np.int64), utc=True))
    return list(idx.tz_convert(CT).strftime("%H:%M"))


# ------------------------------------------------------------------ tables ----
def test_every_derived_table_equals_the_frozen_one_on_the_overlap(tables) -> None:
    assert all(tables.record["overlap"].values()), tables.record["overlap"]
    d = tables.record["derived_hist"]
    assert (d["equity_full"], d["auctions"], d["month_end_rows"], d["wpsr"], d["ngs"],
            d["energy_full"], d["metals_full"]) == (2247, 447, 108, 469, 470, 2250, 2250)
    assert d["wpsr_untimed"] == ["2012-11-01"] and tables.record["h1_rows"] == 95


def test_the_tables_are_hist_rows_before_may_2019_then_the_frozen_rows(tables) -> None:
    from strategy.members.k2._releases import TREASURY_AUCTIONS

    hist = [r for r in tables.auctions if r[0] < "2019-05-01"]
    assert tuple(tables.auctions[len(hist):]) == tuple(TREASURY_AUCTIONS)
    assert min(r[0] for r in hist) == "2010-01-13"
    assert all(d < date(2019, 5, 1) or d >= date(2019, 5, 1) for d in tables.month_end_dates)
    assert date(2010, 6, 30) in tables.month_end_dates


def test_the_metals_calendar_carries_the_frozen_sub_group_map(tables) -> None:
    from data.group_session import load_group_calendar

    assert dict(tables.calendars["metals"].subgroup_of_product) == dict(
        load_group_calendar("metals").subgroup_of_product)
    assert set(tables.calendars) == set(B.HIST_GROUPS)


# ------------------------------------------------------------------ the context ----
def test_the_context_swaps_every_attribute_and_restores_it(tables) -> None:
    before = B.originals()
    with B.backward_context(tables) as values:
        now = B.originals()
        assert all(now[k] is values[k] for k in B.PATCHES)
        assert B.is_active()
    after = B.originals()
    assert all(after[k] is before[k] for k in B.PATCHES) and not B.is_active()


def test_the_context_restores_on_an_exception_and_refuses_nesting(tables) -> None:
    before = B.originals()
    with pytest.raises(RuntimeError, match="boom"), B.backward_context(tables):
        raise RuntimeError("boom")
    assert all(B.originals()[k] is before[k] for k in B.PATCHES)
    with B.backward_context(tables), pytest.raises(B.BackwardError, match="no nesting"), \
            B.backward_context(tables):
        pass


def test_inside_the_context_the_frozen_clock_forms_2010_2019_rows_for_every_group(tables) -> None:
    from ml_route_v2.clock import decision_rows, session_group

    days = {"MGC": [date(2011, 3, 1)], "ZC": [date(2011, 3, 1)], "LE": [date(2015, 3, 3)],
            "ZN": [date(2011, 3, 1)], "MNQ": [date(2011, 3, 1)], "HE": [date(2018, 3, 6)]}
    with B.backward_context(tables):
        assert session_group("MGC") == "gold"
        rows = decision_rows(tuple(days), days)
    got = {v: _ct_hhmm(rows.loc[rows["root"] == v].sort_values("t_index")["decision_ts_ns"])
           for v in days}
    assert got["MGC"] == ["07:50", "10:20", "12:50"] and got["ZN"] == got["MGC"]
    assert got["ZC"] == ["10:00", "10:30", "11:00"]  # O_X 09:30 before 2013-04-08
    assert got["LE"] == ["08:30", "09:30", "11:00"]  # the 08:00 era
    assert got["MNQ"] == ["09:00", "11:00", "13:00"] and got["HE"] == ["09:00", "10:00", "11:00"]


def test_inside_the_context_the_member_tables_are_the_hist_ones(tables) -> None:
    from strategy.members.k2._releases import TREASURY_AUCTIONS
    from strategy.members.k4 import eiafade, ngpre

    with B.backward_context(tables):
        from strategy.members.k2 import _releases

        assert _releases.TREASURY_AUCTIONS[0][0] == "2010-01-13"
        assert eiafade.make_mcl().wpsr[0][0] == "2010-06-03"
        assert ngpre.make_ng().ngs[0][0] == "2010-06-03"
    assert TREASURY_AUCTIONS[0][0] == "2019-05-08"
    assert eiafade.make_mcl().wpsr[0][0] == "2019-05-01"


# ------------------------------------------------------------------ S11 and ruling 4 ----
def test_the_release_rules_hold_hist_rows_and_the_fallback_minutes(rules) -> None:
    assert set(rules.hist_types) == {"FOMC", "NGS", "WPSR", "TREASURY_AUCTION"}
    fb = rules.record["fallback_ct_minutes"]
    assert fb["MNQ"] == [450, 540] and fb["ZN"] == [450, 540] and fb["ZT"] == [450]
    assert 660 in fb["ZC"] and fb["LE"] == [660] and "NG" not in fb
    assert rules.calendar.covers([date(2010, 7, 1), date(2019, 4, 30)])


def test_fallback_costs_change_nothing_without_fallback_minutes_and_price_hits_at_the_event_cost(
        tables, rules) -> None:
    from ml_route_v2.signals._core import release_times
    from ml_route_v2.targets import _cost_parts, build_targets, frozen_costs

    with B.backward_context(tables):
        w = D.sentinel_world(date(2011, 6, 1), date(2011, 6, 30), rules.calendar)
        w = D.SentinelWorld(("ZN",), {"ZN": w.bars["ZN"]}, {"ZN": frozenset()}, rules.calendar,
                            frozen_costs(("ZN",)))
        rows = D.b1_rows(w)
        tg = build_targets(rows, w.bars, releases=rules.calendar, costs=w.costs)
        none = SimpleNamespace(fallback={}, _roots=lambda p: (p, p))
        same = B.apply_fallback_costs(rows, tg, rules.calendar, w.costs, none)
        for h in ("h60", "h120", "hF"):
            np.testing.assert_allclose(same[f"cost_long_{h}"], tg[f"cost_long_{h}"], equal_nan=True)
        t1 = (rows["t_index"] == 1).to_numpy()
        assert set(_ct_hhmm(rows.loc[t1, "decision_ts_ns"])) == {"07:50"}  # in [07:30, 08:00)
        hit = SimpleNamespace(fallback={"ZN": (7 * 60 + 30,)}, _roots=lambda p: (p, p))
        got = B.apply_fallback_costs(rows, tg, rules.calendar, w.costs, hit)
        pc, comm = _cost_parts(w.costs["ZN"], "ZN")
        i = int(np.flatnonzero(t1 & tg["ok_h60"].to_numpy(bool))[0])
        e = pd.Timestamp(int(tg["entry_ts_ns"].iloc[i]), tz="UTC").tz_convert(CT).to_pydatetime()
        x = pd.Timestamp(int(tg["exit_ts_ns_h60"].iloc[i]), tz="UTC").tz_convert(CT).to_pydatetime()
        rel = release_times(rules.calendar, "ZN")
        assert len(rel) > 0
        want = comm + pc.side_slippage_ticks(e, "buy", True) + pc.side_slippage_ticks(
            x, "sell", False)
        assert got["cost_long_h60"].iloc[i] == pytest.approx(want)
        assert got["cost_long_h60"].iloc[i] >= tg["cost_long_h60"].iloc[i]


# ------------------------------------------------------------------ rulings 2, 3, 5, 6, 7 ----
def test_ruling_2_excludes_le_t1_in_the_08_00_era_and_the_frozen_check_needs_it(tables, rules
                                                                                ) -> None:
    from ml_route_v2.signals import CausalityError, compute_signals
    from ml_route_v2.targets import frozen_costs

    with B.backward_context(tables):
        bars = D.sentinel_bars(("LE",), date(2015, 2, 2), date(2015, 3, 31))
        w = D.SentinelWorld(("LE",), bars, {"LE": frozenset()}, rules.calendar,
                            frozen_costs(("LE",)))
        rows = D.b1_rows(w)
        kept, dropped = D.apply_ruling2(w, rows)
        assert len(dropped) and set(dropped["t_index"]) == {1}
        assert set(_ct_hhmm(dropped["decision_ts_ns"])) == {"08:30"}
        with pytest.raises(CausalityError, match="g05_gap"):  # an LE-only world: own-path
            compute_signals(D._ctx(w, rows), D.PORTS_G5)
        compute_signals(D._ctx(w, kept), D.PORTS_G5)


def test_ruling_3_session_end_exit_matches_a_hand_computation(tables, rules) -> None:
    """PR-17: ZC on 2014-03-04 (close 13:15, F_X 13:18 has no bar): the hF and t4-h60 exits fill
    at the close of the 13:14 bar, priced in its bucket; exit_ts is 13:15 CT."""
    from ml_route_v2.signals._core import per_unit
    from ml_route_v2.targets import _cost_parts, build_targets, frozen_costs

    day = date(2014, 3, 4)
    with B.backward_context(tables):
        bars = D.sentinel_bars(("ZC",), date(2014, 1, 6), date(2014, 3, 7))
        w = D.SentinelWorld(("ZC",), bars, {"ZC": frozenset()}, rules.calendar,
                            frozen_costs(("ZC",)))
        rows = D.b1_rows(w)
        tg = build_targets(rows, bars, releases=rules.calendar, costs=w.costs)
        out, counts = B.session_end_exits(rows, tg, bars, w.costs, rules.calendar)
    on = (pd.to_datetime(rows["trade_date"]).dt.date == day).to_numpy()
    i4 = int(np.flatnonzero(on & (rows["t_index"] == K.T4_INDEX).to_numpy())[0])
    assert not tg["ok_hF"].iloc[i4] and not tg["ok_h60"].iloc[i4]  # the frozen targets: no F bar
    f = bars["ZC"]
    ts = f["ts_event"].to_numpy(np.int64)
    bar1314 = int(pd.Timestamp(datetime(2014, 3, 4, 13, 14)).tz_localize(CT)
                  .tz_convert("UTC").value)
    j = int(np.flatnonzero(ts == bar1314)[0])
    assert ts[j + 1] > bar1314 + NS_MIN or str(f["trade_date"].iloc[j + 1]) != "2014-03-04"
    entry = float(tg["entry_price"].iloc[i4])
    t4 = int(rows["decision_ts_ns"].iloc[i4])
    assert entry == float(f["open"].iloc[int(np.flatnonzero(ts == t4)[0])])
    y = (float(f["close"].iloc[j]) - entry) * per_unit("ZC")
    pc, comm = _cost_parts(w.costs["ZC"], "ZC")
    e_ct = pd.Timestamp(t4, tz="UTC").tz_convert(CT).to_pydatetime()
    x_ct = pd.Timestamp(bar1314, tz="UTC").tz_convert(CT).to_pydatetime()
    want_long = comm + pc.side_slippage_ticks(e_ct, "buy", False) + pc.side_slippage_ticks(
        x_ct, "sell", False)
    want_short = comm + pc.side_slippage_ticks(e_ct, "sell", False) + pc.side_slippage_ticks(
        x_ct, "buy", False)
    for h in ("hF", "h60"):
        assert out[f"ok_{h}"].iloc[i4]
        assert out[f"y_gross_{h}"].iloc[i4] == pytest.approx(y)
        assert out[f"exit_ts_ns_{h}"].iloc[i4] == bar1314 + NS_MIN
        assert out[f"cost_long_{h}"].iloc[i4] == pytest.approx(want_long)
        assert out[f"cost_short_{h}"].iloc[i4] == pytest.approx(want_short)
        assert out[f"y_norm_{h}"].iloc[i4] == pytest.approx(y / out["sigma_d"].iloc[i4])
    i1 = int(np.flatnonzero(on & (rows["t_index"] == 1).to_numpy())[0])
    assert out["ok_hF"].iloc[i1] and not np.isfinite(tg["y_gross_hF"].iloc[i1])
    assert out["exit_ts_ns_h60"].iloc[i1] == tg["exit_ts_ns_h60"].iloc[i1]  # t1 h60 untouched
    assert counts["hF"] >= 4 and counts["h60_t4"] >= 1


def test_ruling_3_leaves_dates_whose_f_bar_exists_untouched(tables, rules) -> None:
    from ml_route_v2.targets import build_targets, frozen_costs

    with B.backward_context(tables):
        bars = D.sentinel_bars(("ZC",), date(2016, 3, 1), date(2016, 3, 31))
        w = D.SentinelWorld(("ZC",), bars, {"ZC": frozenset()}, rules.calendar,
                            frozen_costs(("ZC",)))
        rows = D.b1_rows(w)
        tg = build_targets(rows, bars, releases=rules.calendar, costs=w.costs)
        out, counts = B.session_end_exits(rows, tg, bars, w.costs, rules.calendar)
    assert counts == {"hF": 0, "h60_t4": 0}
    pd.testing.assert_frame_equal(out, tg)


def test_rulings_5_and_6_exclusions(tables) -> None:
    assert B.unsourced_release_exclusions() == {"MCL": frozenset({date(2012, 11, 1)})}
    cal = B.unsourced_calendar_exclusions(tables.calendars)
    assert len(cal["LE"]) == 14 and len(cal["HE"]) == 4
    assert all(not cal[v] for v in K.VEHICLES if v not in ("LE", "HE"))
    ex = B.b1_exclusions(tables.calendars)
    assert date(2012, 11, 1) in ex["MCL"] and len(ex["LE"]) == 14


def test_ruling_7_records_the_frozen_tenor_labels(tables) -> None:
    rec = B.reopening_record(tables)
    assert rec["rows_in_window_by_tenor"] == {"2Y": 97, "5Y": 107, "10Y": 106, "30Y": 106}


# ------------------------------------------------------------------ the dry check ----
def test_the_declared_row_losses_and_ruling_2_counts_are_reproduced(tables, rules) -> None:
    got = D.row_loss_check(tables, rules.calendar, roots=("NQ", "ZN", "ZC", "LE", "CL"))
    assert all(r["reproduced"] for r in got.values()), {p: r["dates_all_rows_lost"]
                                                        for p, r in got.items()}
    assert got["LE"]["ruling2_excluded"] == {1: 296}
    assert all(not got[p]["ruling2_excluded"] for p in ("NQ", "ZN", "ZC", "CL"))
    assert 590 <= got["ZC"]["dates_all_rows_lost_with_sigma_g9_warmup"] <= 640


def test_every_kept_feature_computes_and_removing_a_leg_stops_the_build(tables, rules) -> None:
    res = D.feature_check(tables, rules.calendar, windows=(D.WINDOWS[2],))
    assert res["failures"] == [], res["failures"]
    legs = D.leg_check(tables, rules.calendar)
    assert set(legs) == set(K.PATH_ROOTS)
    assert all(r["stops"] and r["names_the_leg"] for r in legs.values())


def test_the_fallback_reach_table(tables, rules) -> None:
    fb = D.fallback_table(tables, rules)["summary"]
    assert fb["MNQ"]["entry_share"] == pytest.approx(0.25)  # t1 09:00 in ISM's [09:00, 09:30)
    assert fb["ZT"]["entry_share"] == pytest.approx(0.25)  # t1 07:50 in NFP's [07:30, 08:00)
    assert fb["ZC"]["entry_share"] == pytest.approx(0.25) and fb["ZC"]["exit_share"] > 0
    assert fb["NG"]["entries_affected"] == 0 and fb["MCL"]["entries_affected"] == 0
