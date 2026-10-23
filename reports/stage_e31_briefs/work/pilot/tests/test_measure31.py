"""measure31_core and measure31 on synthetic records only (no real data file exists or is opened).

Fill models on small scenarios (queue fill, through fill, no fill on a touch, the 60 s + 50 ms
life), markouts / half spread / drops, session clocks in CST and CDT, calendar, roll and gap
exclusions, the loop state machine, ZS/ZL conditions, the table columns of TABLES31.md, the
split step and the manifest / USDA guards."""

import json
import math
import re
import sys
from datetime import date, time
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import mbo_book31 as mb  # noqa: E402
import measure31 as m31  # noqa: E402
import measure31_core as core  # noqa: E402
import synth31 as sy  # noqa: E402
from synth31 import ct  # noqa: E402

TABLES_MD = HERE.parent / "TABLES31.md"
SNAP_T = sy.ct(18, 0, day=date(2024, 1, 9))  # 00:00 UTC on 2024-01-10
P = sy.p


def base_book() -> list[tuple]:
    """Snapshot: bids 349.9 (o1 5, o2 3), 349.8 (o5 10); asks 350.0 (o10 4), 350.1 (o11 6)."""
    return sy.snapshot(SNAP_T, [(349.9, 5, 1), (349.9, 3, 2), (349.8, 10, 5)],
                       [(350.0, 4, 10), (350.1, 6, 11)])


def short_session() -> tuple[core.Session, ...]:
    return (core.Session(core.DAY, ct(8, 30), ct(8, 50)),)  # grid 08:35 and 08:40 (< 08:45)


def run(rows: list[tuple], sessions=None, loop=False, kparams=None) -> core.InstrumentRun:
    sessions = sessions or short_session()
    rec = sy.mbo(rows)
    rec["t"], rec["inversions"] = mb.time_axis(rec["ts_event"], rec["ts_recv"], rec["flags"])
    r = core.InstrumentRun(sessions, kparams or core.ka.ZM_K, False,
                           loop_session=sessions[-1] if loop else None)
    r.run(rec)
    return r


def first(r: core.InstrumentRun, s: int) -> core.Placement:
    return next(pl for pl in r.placements if pl.s == s)


def trade(t, aggr, price, size, fills=(), oid=900, last=True):
    """T then one F per (order id, lots) on the passive side; no book change. ``last``: the
    final record carries F_LAST (no C/M records follow in the same event)."""
    rest = "B" if aggr == "A" else "A"
    rows = [(t, "T", aggr, price, size, oid, 0), *[(t, "F", rest, price, n, o, 0)
                                                    for o, n in fills]]
    if last:
        rows[-1] = (*rows[-1][:6], mb.F_LAST)
    return rows


J = ct(8, 35, 0.05)


# ------------------------------------------------------------------ fill models ----
def test_queue_fill_model_b_and_k_model_a_scenario():
    rows = base_book()
    # 08:35:10: a seller takes 8 at 349.9 (o1 5, o2 3): Q = 8 = Q_ahead -> (b) no fill;
    # (a): o1 is the snapshot TOP and takes 5; Q1 = 3 -> FIFO 2 (o2), pro rata 1 over
    # [0, 1, V 1] -> 0, 0; leveling 1 lot: o2 before V (same size, earlier) -> V gets 0
    rows += trade(ct(8, 35, 10), "A", 349.9, 8, [(1, 5), (2, 3)], last=False)
    rows += [(ct(8, 35, 10), "C", "B", 349.9, 5, 1, 0), (ct(8, 35, 10), "C", "B", 349.9, 3, 2)]
    # the real 349.9 level is now empty: o3 re-establishes it, betters the real market (best
    # 349.8) and is TOP (the virtual order never changes TOP state); o4 joins behind
    rows += [(ct(8, 35, 15), "A", "B", 349.9, 2, 3), (ct(8, 35, 16), "A", "B", 349.9, 5, 4)]
    # 08:35:20: a seller takes 3 (o3 2, o4 1). (b): Q_ahead = 0 < 3 -> fill. (a): queue
    # [V 1, o3 2 (TOP), o4 5]: TOP takes 2, Q1 = 1 -> FIFO 1 -> V (earlier than o4)
    rows += trade(ct(8, 35, 20), "A", 349.9, 3, [(3, 2), (4, 1)], last=False)
    rows += [(ct(8, 35, 20), "C", "B", 349.9, 2, 3, 0), (ct(8, 35, 20), "M", "B", 349.9, 4, 4)]
    r = run(rows)
    buy = first(r, 1)
    assert buy.price == P(349.9) and buy.j == J
    assert buy.orders["b"].t_fill == ct(8, 35, 20) and buy.orders["b"].trigger == "queue"
    assert buy.orders["a"].t_fill == ct(8, 35, 20) and buy.orders["a"].trigger == "queue"
    assert buy.orders["c"].t_fill is None
    assert buy.orders["b"].mid0 == pytest.approx(P(349.95))
    assert r.book.top[mb.BID] == 0  # o3 left


def test_k_model_a_top_takes_a_one_lot_event_behind_the_virtual():
    rows = base_book()
    rows += trade(ct(8, 35, 10), "A", 349.9, 8, [(1, 5), (2, 3)], last=False)
    rows += [(ct(8, 35, 10), "C", "B", 349.9, 5, 1, 0), (ct(8, 35, 10), "C", "B", 349.9, 3, 2)]
    rows += [(ct(8, 35, 15), "A", "B", 349.9, 2, 3)]  # o3 TOP (see the scenario above)
    rows += trade(ct(8, 35, 20), "A", 349.9, 1, [(3, 1)], last=False)
    rows += [(ct(8, 35, 20), "M", "B", 349.9, 1, 3)]
    buy = first(run(rows), 1)
    assert buy.orders["a"].t_fill is None  # TOP o3 takes the 1 lot
    assert buy.orders["b"].t_fill == ct(8, 35, 20)


def test_model_b_counts_cancels_ahead_but_k_needs_its_allocation():
    rows = base_book()
    rows += [(ct(8, 35, 5), "C", "B", 349.9, 5, 1)]  # o1 cancels: Q_ahead 3 (o2)
    rows += trade(ct(8, 35, 10), "A", 349.9, 2, [(2, 2)])
    rows += [(ct(8, 35, 10), "M", "B", 349.9, 1, 2)]
    r = run(rows)
    buy = first(r, 1)
    assert buy.orders["b"].t_fill is None  # 2 does not exceed 3
    # (a): no TOP (cancelled), Q = 2: FIFO 1 -> o2, pro rata 1 over [2, 1]: 0, 0; leveling:
    # o2 (2) first -> V gets 0
    assert buy.orders["a"].t_fill is None


def test_through_fill_every_model_and_c_half_negative():
    rows = base_book()
    rows += trade(ct(8, 35, 30), "A", 349.8, 3, [(5, 3)])
    r = run(rows)
    buy = first(r, 1)
    for m in core.MODELS:
        assert buy.orders[m].t_fill == ct(8, 35, 30) and buy.orders[m].trigger == "through"
    sell = first(r, -1)
    assert all(sell.orders[m].t_fill is None for m in core.MODELS)


def test_sell_side_through_on_a_buyer_above():
    rows = base_book() + trade(ct(8, 35, 40), "B", 350.1, 2, [(11, 2)])
    sell = first(run(rows), -1)
    assert sell.price == P(350.0)
    assert {sell.orders[m].trigger for m in core.MODELS} == {"through"}


def test_no_fill_on_a_touch_or_a_trade_at_the_price_under_c():
    rows = base_book()
    rows += [(ct(8, 35, 5), "A", "A", 349.9, 1, 20)]  # an ask moves to the buy's price
    rows += trade(ct(8, 35, 6), "A", 349.9, 1, [(1, 1)])  # a trade at p, not through
    r = run(rows)
    assert first(r, 1).orders["c"].t_fill is None


def test_side_n_trades_never_fill():
    rows = base_book() + trade(ct(8, 35, 30), "N", 349.7, 3)
    r = run(rows)
    assert all(first(r, 1).orders[m].t_fill is None for m in core.MODELS)
    assert r.implied[core.DAY][6:] == [1, 3]


@pytest.mark.parametrize(("offset_ns", "filled"), [
    (0, False),  # stamped at j: part of the join state
    (1, True),
    (60 * core.NS, True),  # the cancel is decided at j + 60 s ...
    (60 * core.NS + 50 * core.MS - 1, True),  # ... and takes effect 50 ms later
    (60 * core.NS + 50 * core.MS, False),  # at j + 60.05 s the order is gone
])
def test_life_window_cancel_at_60s_plus_50ms(offset_ns, filled):
    rows = base_book() + trade(J + offset_ns, "A", 349.8, 1, [(5, 1)])
    buy = first(run(rows), 1)
    assert (buy.orders["c"].t_fill is not None) is filled


def test_invalid_book_at_join_takes_no_placement():
    rows = base_book() + [(ct(8, 34), "A", "A", 349.9, 1, 30)]  # locked from 08:34
    r = run(rows)
    assert [pl.g for pl in r.placements] == []
    assert r.diag["crossed_moments"] == 2


def test_bad_book_flag_drops_resting_and_later_placements():
    rows = base_book() + [(ct(8, 35, 30), "N", "N", 0.0, 0, 0, mb.F_MAYBE_BAD_BOOK | mb.F_LAST)]
    r = run(rows)
    assert [pl.dropped for pl in r.placements] == [True, True]
    assert r.diag["joins_invalid_bad_or_unstarted"] == 1


# ------------------------------------------------------------------ markouts ----
def hist(states):
    t, b, a, v = zip(*states, strict=True)
    return core.History(np.array(t, dtype=np.int64), np.array([P(x) for x in b]),
                        np.array([P(x) for x in a]), np.array(v, dtype=bool))


def test_markouts_half_spread_and_drops():
    t0 = ct(9, 0)
    h = hist([(t0 - 5, 349.9, 350.0, True), (t0, 349.8, 350.0, True),
              (t0 + 5 * core.NS, 350.0, 350.2, True), (t0 + 30 * core.NS, 350.0, 350.0, False),
              (t0 + 40 * core.NS, 350.2, 350.4, True)])
    inv = np.concatenate(([0], np.cumsum(~h.valid)))
    lv = core.last_valid_index(h.valid)
    drops = {}
    mid0 = P(349.95)
    head, nodrop = core.markouts(h, inv, lv, t0, 1, mid0, t0 + 3600 * core.NS, P(0.1), drops)
    # h=1: state at t0 (mid 349.9) -> -0.5; h=10: mid 350.1 -> +1.5; h=60: crosses the locked
    # state at +30 s -> dropped; the no-drop variant takes the last valid state (mid 350.3)
    assert head[:2] == [pytest.approx(-0.5), pytest.approx(1.5)] and math.isnan(head[2])
    assert nodrop == [pytest.approx(-0.5), pytest.approx(1.5), pytest.approx(3.5)]
    assert drops == {"invalid_book": 1}
    head, nodrop = core.markouts(h, inv, lv, t0, -1, mid0, t0 + 10 * core.NS, P(0.1), drops)
    assert head[0] == pytest.approx(0.5) and math.isnan(head[1]) and math.isnan(nodrop[2])
    assert drops["session_end"] == 2


def test_measure_day_fill_columns_markouts_and_c_half():
    rows = base_book() + heartbeat()
    rows += trade(ct(8, 35, 30), "A", 349.8, 3, [(5, 3)])  # through fill of the 08:35 buy
    rows += [(ct(8, 35, 30), "C", "B", 349.8, 3, 5)]
    rows.sort(key=lambda r: r[0])
    out = core.measure_day(sy.job(), sy.mbo(rows), None, None)
    pl = out["placements"]
    k = next(i for i in range(len(pl["model"])) if pl["model"][i] == "c" and pl["filled"][i])
    assert pl["g_ns"][k] == ct(8, 35) and pl["side"][k] == 1 and pl["trigger"][k] == "through"
    assert pl["wait_s"][k] == pytest.approx(29.95)
    assert pl["c_half"][k] == pytest.approx(0.5)  # mid0 349.95 above the 349.9 buy
    assert pl["mid0"][k] == pytest.approx(349.95)
    assert pl["mo_1"][k] == pytest.approx(0.0)  # mid unchanged at 349.95 (E_1 = 0.5)
    assert pl["touched"][k] is True and pl["stale"][k] is False
    assert math.isnan(pl["zs_d1"][k]) and math.isnan(pl["usda_min"][k])
    unfilled = [i for i in range(len(pl["model"])) if not pl["filled"][i]]
    assert all(pl["wait_s"][i] == pytest.approx(60.05) and pl["t_fill_ns"][i] == -1
               and pl["trigger"][i] == "" for i in unfilled)


# ------------------------------------------------------------------ sessions ----
def test_session_clocks_cst_and_cdt_and_grid_counts():
    on, day = core.regular_sessions(date(2024, 1, 8))  # Monday in CST
    assert on.lo == 1_704_675_600 * core.NS  # Sunday 2024-01-07 19:00 CST = 01:00Z on 01-08
    assert day.lo == 1_704_724_200 * core.NS  # 08:30 CST = 14:30Z
    # spec v2: open + 5 min <= g < close - 5 min -> DAY 08:35 .. 13:10 CT
    assert len(day.grid()) == 56 and day.grid()[0] == day.lo + 300 * core.NS
    assert day.grid()[-1] == day.hi - 600 * core.NS
    assert len(on.grid()) == 151  # 19:05 .. 07:35 CT
    on_s, day_s = core.regular_sessions(date(2023, 7, 12))  # Wednesday in CDT
    assert on_s.lo == 1_689_120_000 * core.NS  # 2023-07-11 19:00 CDT = 00:00Z
    assert day_s.lo == 1_689_168_600 * core.NS  # 08:30 CDT = 13:30Z
    assert len(day_s.grid()) == 56


def test_sessions_agree_with_the_grains_calendar():
    from data.group_session import session_intervals

    cal = m31.grains()
    for d in (date(2024, 1, 8), date(2023, 7, 12), date(2023, 3, 13), date(2023, 11, 6)):
        assert [(s.lo, s.hi) for s in core.regular_sessions(d)] == session_intervals(cal, d)


# ------------------------------------------------------------------ exclusions ----
def heartbeat(lo=None, hi=None, step_s=20, iid=sy.IID):
    lo = ct(8, 30) if lo is None else lo
    hi = ct(13, 20) if hi is None else hi
    return [(t, "N", "N", 0.0, 0, 0, mb.F_LAST, iid) for t in range(lo, hi, step_s * core.NS)]


def test_gap_exclusion_and_counts():
    rows = base_book() + [r for r in heartbeat() if not ct(10, 0) < r[0] < ct(10, 2)]
    out = core.measure_day(sy.job(), sy.mbo(rows), None, None)
    d = out["days"]
    assert d["included"] == [False] and d["reason"] == ["day_gap_gt_60s"]
    assert d["max_gap_day_s"][0] == pytest.approx(120.0)  # 10:00:00 to 10:02:00
    assert out["placements"]["model"] == [] and out["loop"]["model"] == []


def test_included_day_counts_and_loop_rows():
    rows = base_book() + heartbeat()
    out = core.measure_day(sy.job(), sy.mbo(rows), None, None)
    d = out["days"]
    assert d["included"] == [True] and d["reason"] == [""]
    assert d["placements_day"] == [112] and d["placements_on"] == [302]
    assert len(out["placements"]["model"]) == 3 * (112 + 302)
    assert out["loop"]["model"] == ["a", "b", "c"] and out["loop"]["round_trips"] == [0, 0, 0]
    assert sorted(set(out["implied"]["session"])) == ["DAY", "OVERNIGHT"]


def test_no_valid_start_and_no_records():
    rows = [r for r in base_book() if r[1] != "R"] + heartbeat()
    out = core.measure_day(sy.job(), sy.mbo(rows), None, None)
    assert out["days"]["reason"] == ["no_valid_book_start"]
    empty = core.measure_day(sy.job(), sy.mbo([]), None, None)
    assert empty["days"]["reason"] == ["no_records"]


def test_calendar_and_static_reasons_win():
    rows = base_book() + heartbeat()
    syms = (core.SymbolJob("ZM.v.0", sy.IID, "ZMH4", "roll_day"),)
    out = core.measure_day(sy.job(symbols=syms), sy.mbo(rows), None, None)
    assert out["days"]["reason"] == ["roll_day"]
    out = core.measure_day(sy.job(calendar_reason="scheduled_late_open"), sy.mbo(rows), None, None)
    assert out["days"]["reason"] == ["scheduled_late_open"]


def test_calendar_reason_on_holiday_late_open_and_regular_days():
    cal = m31.grains()
    assert m31.calendar_reason(cal, date(2023, 11, 24)) == m31.REASON_HOLIDAY  # 12:05 close
    assert m31.calendar_reason(cal, date(2024, 1, 2)) == m31.REASON_LATE_OPEN
    assert m31.calendar_reason(cal, date(2024, 1, 10)) == ""
    days = m31.month_trade_dates(cal, ["2024-01"])
    assert date(2024, 1, 15) not in days and date(2024, 1, 2) in days and len(days) == 21


def test_roll_reasons_day_after_and_unknown():
    cal = m31.grains()
    maps = {"ZM.v.0": [(date(2023, 12, 29), date(2024, 1, 10), 1),
                       (date(2024, 1, 10), date(2024, 2, 1), 2)]}
    days = m31.month_trade_dates(cal, ["2024-01"])
    rr = m31.roll_reasons(maps, "ZM.v.0", days, cal)
    assert rr[date(2024, 1, 10)] == "roll_day" and rr[date(2024, 1, 11)] == "after_roll_day"
    assert date(2024, 1, 9) not in rr and date(2024, 1, 2) not in rr
    assert m31.roll_reasons({"ZM.v.0": [(date(2024, 1, 2), date(2024, 2, 1), 1)]},
                            "ZM.v.0", [date(2024, 1, 2)], cal) == {date(2024, 1, 2):
                                                                   "roll_status_unknown"}
    assert m31.instrument_on(maps, "ZM.v.0", date(2024, 1, 9)) == 1


def test_measure_day_refuses_march_2024():
    with pytest.raises(core.MeasureRefused):
        core.measure_day(sy.job(day=date(2024, 3, 1)), sy.mbo([]), None, None)
    late = sy.mbo([(core.CUTOFF_NS, "N", "N", 0.0, 0, 0)])
    with pytest.raises(core.MeasureRefused):
        core.measure_day(sy.job(), late, None, None)


# ------------------------------------------------------------------ loop ----
def test_loop_state_machine_under_model_c():
    rows = base_book()
    rows += trade(ct(8, 35, 10), "A", 349.8, 1, [(5, 1)])  # entry buy filled (through)
    rows += trade(ct(8, 35, 20), "B", 350.1, 1, [(11, 1)])  # exit sell at 350.0 filled
    sess = (core.Session(core.DAY, ct(8, 30), ct(8, 50)),)
    r = run(rows, sessions=sess, loop=True)
    lp = next(x for x in r.loops if x.model == "c")
    # buy entry, exit, then sell entries decided at 08:35:20 + k x 60.05 s while the decision
    # is before 08:45:00 (k = 0..9): 12 orders, one round trip of 20 s
    assert (lp.round_trips, lp.entries_filled, lp.orders_placed) == (1, 1, 12)
    assert lp.durations == [20 * core.NS] and lp.entry_side == -1 and lp.done


def test_loop_waits_for_a_valid_book():
    rows = base_book()
    rows += [(ct(8, 34), "A", "A", 349.9, 1, 30)]  # locked at the first loop join
    rows += [(ct(8, 36), "C", "A", 349.9, 1, 30)]  # valid again: decided at 08:36:00
    sess = (core.Session(core.DAY, ct(8, 30), ct(8, 42)),)  # decisions before 08:37:00
    lp = next(x for x in run(rows, sessions=sess, loop=True).loops if x.model == "c")
    assert lp.join_invalid == 1 and lp.orders_placed == 1


# ------------------------------------------------------------------ conditions ----
def test_zs_zl_condition_moves_and_missing():
    lo = ct(8, 30)
    zs = sy.mbp([(lo + 1 * core.NS, 1200.00, 1200.25), (ct(9, 0, 0.5), 1200.25, 1200.50),
                 (ct(9, 0, 5), 1200.25, 1200.25)])
    rec = {**zs, "t": zs["ts_event"].astype(np.int64)}
    series = core.CondSeries.of(rec, P(0.25))
    tf = ct(9, 0, 9)
    assert series.move(tf, 1, lo) == pytest.approx(0.0)  # locked at 09:00:05 -> last valid
    assert series.move(tf, 10, lo) == pytest.approx(1.0)  # 1200.375 - 1200.125 = 1 tick
    assert math.isnan(series.move(lo + 500 * core.MS, 1, lo))  # nothing before t_f - L
    assert math.isnan(series.mid_at(lo + 2 * core.NS, lo + 5 * core.NS))  # before the session


def test_usda_minutes_nearest_and_ties():
    t = ct(11, 0)
    assert core.usda_minutes(t, ()) != core.usda_minutes(t, ())  # NaN
    assert core.usda_minutes(t, (ct(11, 2), ct(10, 30))) == pytest.approx(-2.0)
    assert core.usda_minutes(t, (ct(10, 58), ct(11, 2))) == pytest.approx(2.0)  # tie: earlier


def test_usda_files_rules_and_coverage():
    usda, counts = m31.load_usda()
    assert counts["skipped_nopa"] > 0 and counts["skipped_norelease"] == 3
    assert counts["uncertain_or_rows"] == 2
    assert date(2023, 7, 6) in usda and date(2023, 7, 7) in usda
    cov = m31.usda_coverage()
    assert cov[0] == (date(2022, 11, 1), date(2024, 2, 29))
    assert any(a == date(2020, 12, 1) for a, _ in cov)
    wasde = m31.release_trade_date(m31.datetime(2023, 1, 12, 17, 0, tzinfo=m31.UTC))
    assert wasde == date(2023, 1, 12)
    assert ct(11, 0, day=date(2023, 1, 12)) in usda[date(2023, 1, 12)]  # 12:00 ET = 11:00 CT
    late = m31.release_trade_date(m31.datetime(2023, 1, 3, 22, 0, tzinfo=m31.UTC))
    assert late == date(2023, 1, 4)  # 16:00 CT and later belongs to the next trade date


def test_plan_days_and_usda_nan_outside_coverage(tmp_path):
    cal = m31.grains()
    files = [m31.SourceFile("Z1", "2024-01", Path("x"), "s", "a", "b")]
    stray = tmp_path / "d.txt"
    stray.write_text("2023-12-01\n")
    with pytest.raises(m31.Refused):
        m31.plan_days(files, cal, stray)
    expected, wanted = m31.plan_days(files, cal, None)
    assert expected == wanted and len(expected) == 21
    assert m31._covered(date(2024, 1, 10), [(date(2020, 12, 1), date(2024, 2, 29))])
    assert not m31._covered(date(2020, 11, 30), [(date(2020, 12, 1), date(2024, 2, 29))])


# ------------------------------------------------------------------ tables ----
def _tables_md_columns() -> dict[str, list[str]]:
    text = TABLES_MD.read_text(encoding="utf-8")
    out = {}
    for name, body in re.findall(r"## (\w+)\.parquet[^\n]*\n(.*?)(?=\n## |\Z)", text, re.S):
        flat = " ".join(body.split("\nThe ")[0].split())  # drop the trailing note
        while "(" in flat:
            flat = re.sub(r"\([^()]*\)", "", flat)
        cols = []
        for seg in flat.split("|"):
            cols += [c.strip() for c in seg.split(",") if c.strip()]
        out[name] = cols
    return out


def test_table_columns_match_tables31_md_exactly():
    md = _tables_md_columns()
    assert md["placements"] == list(core.PLACEMENT_COLUMNS)
    assert md["loop"] == list(core.LOOP_COLUMNS)
    assert md["implied"] == list(core.IMPLIED_COLUMNS)
    assert md["days"] == list(core.DAYS_COLUMNS)
    for table, cols in core.TABLE_COLUMNS.items():
        for c in cols:
            assert c in core.COLUMN_TYPES[table] or c in core.COLUMN_TYPES["*"]


def test_written_tables_parquet_types_and_done_last(tmp_path):
    import pyarrow.parquet as pq

    rows = base_book() + heartbeat() + trade(ct(8, 35, 30), "A", 349.8, 3, [(5, 3)])
    rows.sort(key=lambda r: r[0])
    out = core.measure_day(sy.job(), sy.mbo(rows), None, None)
    folder = tmp_path / "2024-01-10"
    m31.write_day_tables(folder, out, {"seconds": 0})
    names = sorted(p.name for p in folder.iterdir())
    assert names == ["DONE", "days.parquet", "diag.json", "implied.parquet", "loop.parquet",
                     "placements.parquet"]
    assert (folder / "DONE").stat().st_mtime_ns >= (folder / "days.parquet").stat().st_mtime_ns
    tab = pq.read_table(folder / "placements.parquet")
    assert tab.column_names == list(core.PLACEMENT_COLUMNS)
    assert str(tab.schema.field("trade_date").type) == "date32[day]"
    assert str(tab.schema.field("side").type) == "int8"
    assert str(pq.read_table(folder / "loop.parquet").schema.field("round_trips").type) == "int32"
    assert json.loads((folder / "diag.json").read_text())["trade_date"] == "2024-01-10"


def test_random_day_invariants():
    rec = sy.random_day(30_000, seed=3)
    rows_t = rec["ts_event"]
    assert np.all(np.diff(rows_t.astype(np.int64)) >= 0)
    out = core.measure_day(sy.job(), rec, None, None)
    pl = out["placements"]
    n = len(pl["model"])
    assert n > 0 and out["days"]["included"] == [True]
    filled = np.array(pl["filled"])
    t_f, j = np.array(pl["t_fill_ns"]), np.array(pl["j_ns"])
    assert np.all(t_f[filled] > j[filled])
    assert np.all(np.array(pl["wait_s"]) <= 60.05 + 1e-9)
    model = np.array(pl["model"])
    trig = np.array(pl["trigger"])
    assert set(trig[filled & (model == "c")]) <= {"through"}
    assert np.count_nonzero(filled & (model == "b")) >= np.count_nonzero(filled & (model == "c"))
    assert all(np.count_nonzero(model == m) == n // 3 for m in core.MODELS)
    assert np.all(np.isfinite(np.array(pl["c_half"])[filled]))


# ------------------------------------------------------------------ split and manifest ----
class FakeStore:
    def __init__(self, chunks, start, end, mappings=None):
        self._chunks = chunks
        self.metadata = type("Meta", (), {"start": start, "end": end,
                                          "mappings": mappings or {}})()

    def to_ndarray(self, count):  # noqa: ARG002
        yield from self._chunks


def _raw_mbo(times):
    import databento_dbn as dbn

    arr = np.zeros(len(times), dtype=dbn.MBOMsg._dtypes)
    arr["ts_recv"] = times
    arr["ts_event"] = times
    arr["action"] = b"A"
    arr["side"] = b"B"
    arr["instrument_id"] = sy.IID
    return arr


def test_split_file_per_trade_date_and_marker(tmp_path):
    cal = m31.grains()
    t1 = ct(9, 0, day=date(2024, 1, 10))
    t0 = ct(17, 0, day=date(2024, 1, 9))  # after 16:00 CT: trade date 01-10
    t2 = ct(9, 0, day=date(2024, 1, 11))
    sat = ct(9, 0, day=date(2024, 1, 13))
    store = FakeStore([_raw_mbo([t0, t1]), _raw_mbo([t2, sat])], ct(16, 0, day=date(2023, 12, 31)),
                      ct(16, 0, day=date(2024, 1, 31)),
                      {"ZM.v.0": [{"start_date": "2024-01-01", "end_date": "2024-02-01",
                                   "symbol": str(sy.IID)}]})
    sf = m31.SourceFile("Z1", "2024-01", tmp_path / "x.dbn.zst", "abc", "s", "e")
    res = m31.split_file(sf, tmp_path, cal, store=store)
    assert res["dates"] == {"2024-01-10": 2, "2024-01-11": 1}
    assert res["counts"]["outside_trade_dates"] == 1
    arr = np.load(tmp_path / "Z1" / "2024-01-10.npy")
    assert arr.dtype == m31.MBO_COMPACT and arr["action"].tolist() == [ord("A")] * 2
    again = m31.split_file(sf, tmp_path, cal, store=None)  # marker: skipped, no store needed
    assert again["dates"] == res["dates"]
    maps = m31.merge_mappings([res])
    assert m31.instrument_on(maps, "ZM.v.0", date(2024, 1, 10)) == sy.IID


def test_split_stops_on_a_march_record(tmp_path):
    store = FakeStore([_raw_mbo([core.CUTOFF_NS])], 0, core.CUTOFF_NS)
    sf = m31.SourceFile("Z1", "2024-02", tmp_path / "x", "abc", "s", "e")
    with pytest.raises(m31.Refused):
        m31.split_file(sf, tmp_path, m31.grains(), store=store)


def _manifest(tmp_path, **over):
    f = {"series": "Z1", "month": "2024-02", "path": str(tmp_path / "f"), "sha256": "x",
         "request": {"start": "2024-01-31T22:00:00Z", "end": "2024-02-29T22:00:00Z"},
         "checks": []}
    g = {**f, "series": "Z4"}
    data = {"exit_code": 0, "files": [{**f, **over}, g]}
    path = tmp_path / "manifest31.json"
    path.write_text(json.dumps(data))
    return path


def test_manifest_guards(tmp_path):
    assert len(m31.load_manifest(_manifest(tmp_path))) == 2
    with pytest.raises(m31.Refused):
        m31.load_manifest(_manifest(tmp_path, request={"start": "2024-02-01T00:00:00Z",
                                                       "end": "2024-03-01T00:00:00Z"}))
    with pytest.raises(m31.Refused):
        m31.load_manifest(_manifest(tmp_path, checks=[{"name": "x", "severity": "hard",
                                                       "passed": False}]))
    path = _manifest(tmp_path)
    data = json.loads(path.read_text())
    path.write_text(json.dumps({**data, "exit_code": 2}))
    with pytest.raises(m31.Refused):
        m31.load_manifest(path)


def test_definition_rows_and_ticks():
    import databento_dbn as dbn

    arr = np.zeros(3, dtype=dbn.InstrumentDefMsg._dtypes)
    for k, (iid, raw, cls, algo, tick, size) in enumerate([
            (1, b"ZMH4", b"F", b"K", 100_000_000, 100), (2, b"ZSH4", b"F", b"K", 2_500_000, 5000),
            (3, b"ZMH4-ZMK4", b"S", b"K", 100_000_000, 100)]):
        arr[k]["instrument_id"] = iid
        arr[k]["raw_symbol"] = raw
        arr[k]["instrument_class"] = cls
        arr[k]["match_algorithm"] = algo
        arr[k]["min_price_increment"] = tick
        arr[k]["unit_of_measure_qty"] = size * 1_000_000_000
    defs = m31.definition_rows(arr)
    assert sorted(defs) == [1, 2] and defs[1]["match_algorithm"] == "K"
    summary = m31.definitions_summary(defs)
    assert summary["zm_outrights_all_K"] and summary["ticks_1e9"]["ZS"] == 2_500_000
    assert m31.checked_tick(defs, "ZM") == 100_000_000  # 0.10 x 100 = 10.00 USD
    assert m31.checked_tick(defs, "ZS") == 2_500_000  # 0.0025 x 5000 = 12.50 USD
    with pytest.raises(m31.Refused):
        m31.checked_tick(defs, "ZL")  # no ZL outright
    cents = {9: {**defs[2], "min_price_increment": 250_000_000}}  # 0.25 (cents) x 5000
    assert m31.checked_tick(cents, "ZS") == 250_000_000  # lead ruling 2026-10-23: cents accepted
    wrong = {9: {**defs[2], "min_price_increment": 500_000_000}}  # 0.50 x 5000: neither unit fits
    with pytest.raises(m31.Refused, match="expected 12.50 USD"):
        m31.checked_tick(wrong, "ZS")


def test_max_workers_cap():
    assert 1 <= m31.max_workers(None) <= 8
    assert m31.max_workers(100) == m31.max_workers(None)
    assert m31.max_workers(1) == 1


def test_time_constants():
    assert m31._utc_ns("2024-03-01T00:00:00Z") == core.CUTOFF_NS
    assert m31._utc_ns("2024-02-29T22:00:00Z") == m31.CUTOFF_END_NS
    assert core.ct_ns(date(2024, 2, 29), time(16, 0)) == m31.CUTOFF_END_NS


# ------------------------------------------------------------------ lead items ----
def test_join_waits_for_f_last_and_never_reads_mid_update():
    rows = base_book()
    rows += [(ct(8, 35, 0.0), "C", "B", 349.9, 5, 1, 0)]  # an event without F_LAST yet ...
    rows += [(ct(8, 35, 0.1), "A", "B", 349.9, 2, 4)]  # ... ends here (F_LAST)
    rows += [(ct(8, 35, 0.2), "N", "N", 0.0, 0, 0)]
    r = run(rows)
    buy = first(r, 1)
    assert r.diag["timers_deferred_mid_update"] == 1
    assert buy.orders["b"].ahead == (2, 4)  # the join saw the book after the F_LAST record


def test_event_after_a_mid_update_record_takes_no_queue_fill():
    rows = base_book()
    rows += [(ct(8, 35, 5), "C", "B", 349.9, 5, 1), (ct(8, 35, 6), "C", "B", 349.9, 3, 2, 0)]
    rows += trade(ct(8, 35, 7), "A", 349.9, 1, [(9, 1)])
    r = run(rows)
    assert r.diag["events_mid_update"] == 1
    assert first(r, 1).orders["b"].t_fill is None


def test_top_max_counting_rule_switch_in_the_engine():
    # an aggressor sells 5 into the 349.9 bids, then rests 2 at 349.9 as a new best ask
    rows = base_book()
    rows += trade(ct(8, 34, 10), "A", 349.9, 5, [(1, 5)], oid=50, last=False)
    rows += [(ct(8, 34, 10), "C", "B", 349.9, 5, 1, 0), (ct(8, 34, 10), "C", "B", 349.9, 3, 2, 0)]
    rows += [(ct(8, 34, 10), "A", "A", 349.9, 2, 50)]
    params = core.ka.KParams(top_max=4)
    new = core.InstrumentRun(short_session(), params, False)
    old = core.InstrumentRun(short_session(), params, True)
    for r in (new, old):
        rec = sy.mbo(rows)
        rec["t"], _ = mb.time_axis(rec["ts_event"], rec["ts_recv"], rec["flags"])
        r.run(rec)
    assert new.book.top[mb.ASK] == 50  # from 2023-10-02: only fills after resting count
    # before: the 5 aggressed lots reach TOP Max 4, so no new TOP is granted and the resting
    # snapshot TOP offer o10 (350.0) keeps it (only a new TOP order takes TOP away)
    assert old.book.top[mb.ASK] == 10
    assert core.DayJob(date(2023, 9, 29), ()).count_initial_aggressed
    assert not core.DayJob(date(2023, 10, 2), ()).count_initial_aggressed


def test_virtual_order_is_never_top_even_on_a_level_without_top():
    rows = base_book()  # snapshot TOP o1 at 349.9; the 349.8 level (o5) has had no TOP
    rows += [(ct(8, 34), "C", "B", 349.9, 5, 1, 0), (ct(8, 34), "C", "B", 349.9, 3, 2)]
    # 08:35:00.05: the virtual buy joins 349.8 behind o5; a 1-lot event there: no TOP, so the
    # FIFO lot goes to o5 (it would go to V if V were TOP)
    rows += trade(ct(8, 35, 10), "A", 349.8, 1, [(5, 1)], last=False)
    rows += [(ct(8, 35, 10), "M", "B", 349.8, 9, 5)]
    rows += [(ct(8, 35, 20), "A", "B", 349.8, 2, 6)]  # o6 joins: TOP by rule (ii), not V
    r = run(rows)
    buy = first(r, 1)
    assert buy.price == P(349.8) and buy.orders["a"].t_fill is None
    assert r.book.top[mb.BID] == 6


# ------------------------------------------------- review items (R_engine31 B) ----
def _top_book(bid_sizes):
    return sy.snapshot(SNAP_T, [(349.9, n, oid) for oid, n in bid_sizes], [(350.0, 4, 10)])


def test_b1_top_room_is_read_before_the_events_own_fills():
    # snapshot TOP o1 150 (0 counted), o2 20, V behind; a 70-lot seller fills o1 for 70:
    # spec allocate([150, 20, 1], 70, top=0, room=100) = [70, 0, 0] -> V gets nothing
    assert core.ka.allocate([150, 20, 1], 70, top=0, top_room=100) == [70, 0, 0]
    rows = _top_book([(1, 150), (2, 20)])
    rows += trade(ct(8, 35, 10), "A", 349.9, 70, [(1, 70)], last=False)
    rows += [(ct(8, 35, 10), "M", "B", 349.9, 80, 1)]
    r = run(rows)
    assert first(r, 1).orders["a"].t_fill is None  # room 30 (the old bug) would fill V
    assert r.book.top[mb.BID] == 1 and r.book.top_count[mb.BID] == 70


def test_b1_count_95_and_a_6_lot_event_top_takes_5_then_is_lost():
    rows = _top_book([(1, 200)])
    rows += trade(ct(8, 34, 10), "A", 349.9, 95, [(1, 95)], last=False)  # before V joins
    rows += [(ct(8, 34, 10), "M", "B", 349.9, 105, 1)]
    # V joins behind o1 (TOP, 95 counted, room 5); a 6-lot seller: TOP takes 5, Q1 = 1 -> FIFO
    # -> o1 (earlier) -> V gets 0. Counting the 6 first (room -1, TOP gone) would give V the
    # leveling lot.
    assert core.ka.allocate([105, 1], 6, top=0, top_room=5) == [6, 0]
    assert core.ka.allocate([105, 1], 6)[1] == 1
    rows += trade(ct(8, 35, 10), "A", 349.9, 6, [(1, 6)], last=False)
    rows += [(ct(8, 35, 10), "M", "B", 349.9, 99, 1)]
    r = run(rows)
    assert first(r, 1).orders["a"].t_fill is None
    assert r.book.top[mb.BID] == 0 and r.book.top_count[mb.BID] == 101  # lost after the event
    assert ids_at(r.book, 349.9)[0] == 1  # it keeps its timestamp


def ids_at(book, price):
    return [oid for oid, _, _ in book.queue(mb.BID, P(price))]


def test_b8_second_level_of_a_sweep_reads_the_unchanged_book():
    rows = base_book() + [(ct(8, 34), "C", "A", 350.0, 4, 10)]  # best ask 350.1
    rows += [(ct(8, 35, 5), "C", "B", 349.9, 5, 1)]  # Q_ahead of V at 349.9: o2 3
    rows += [(ct(8, 35, 6), "A", "B", 349.9, 4, 8), (ct(8, 35, 7), "A", "B", 350.0, 1, 7)]
    # one seller sweeps 350.0 (o7 1) and 349.9 (o2 3, o8 2); the C/M records come last
    rows += trade(ct(8, 35, 10), "A", 350.0, 1, [(7, 1)], last=False)
    rows += trade(ct(8, 35, 10), "A", 349.9, 5, [(2, 3), (8, 2)], last=False)
    rows += [(ct(8, 35, 10), "C", "B", 350.0, 1, 7, 0),
             (ct(8, 35, 10), "C", "B", 349.9, 3, 2, 0), (ct(8, 35, 10), "M", "B", 349.9, 2, 8)]
    r = run(rows)
    buy = first(r, 1)
    assert buy.price == P(349.9)
    assert buy.orders["b"].t_fill == ct(8, 35, 10) and buy.orders["b"].trigger == "queue"
    assert "events_mid_update" not in r.diag and "implied_trades_mid_update" not in r.diag
    assert r.implied[core.DAY][:2] == [2, 6]


def test_b9_gap_counts_records_only_not_the_session_edges():
    sess = core.Session(core.DAY, ct(8, 30), ct(13, 20))
    t = np.array([ct(8, 32), ct(8, 32, 30), ct(13, 0)], dtype=np.int64)  # a quiet end
    assert core.max_gap_s(t, sess) == pytest.approx(16_050.0)  # 08:32:30 to 13:00
    t = np.array([ct(8, 32), ct(8, 33)], dtype=np.int64)
    assert core.max_gap_s(t, sess) == pytest.approx(60.0)  # 8:30 open and 13:20 close ignored
    assert core.max_gap_s(np.array([ct(9, 0)], dtype=np.int64), sess) == pytest.approx(17_400.0)
    rows = base_book() + [r for r in heartbeat() if r[0] < ct(13, 18)]  # silent last 2 minutes
    out = core.measure_day(sy.job(), sy.mbo(rows), None, None)
    assert out["days"]["included"] == [True]


def test_b5_summarize_diag_sums_counts_per_symbol(tmp_path):
    out = tmp_path / "measure31"
    for day, events, mid in (("2024-01-10", 10, 1), ("2024-01-11", 30, 0)):
        folder = out / day
        folder.mkdir(parents=True)
        (folder / "diag.json").write_text(json.dumps({
            "trade_date": day, "zm_records": 100, "seconds": 0.5,
            "symbols": {"ZM.v.0": {"reason": "", "run": {"events": events,
                                                          "events_mid_update": mid},
                                   "book": {"cancel_unknown_order": 2},
                                   "markout_drops": {"invalid_book": 1},
                                   "placements_dropped_bad_book": 0},
                        "ZM.v.1": {"reason": "roll_day"}}}))
    (out / "2024-01-12").mkdir()
    summary = m31.summarize_diag(out)
    front = summary["per_symbol"]["ZM.v.0"]
    assert front["dates"] == 2 and front["run"]["events"] == 40
    assert front["book"]["cancel_unknown_order"] == 4
    assert front["ratios"]["events_mid_update_per_event"] == pytest.approx(0.025)
    assert summary["per_symbol"]["ZM.v.1"]["reasons"] == {"roll_day": 2}
    assert summary["folders_without_diag"] == ["2024-01-12"]
    assert (tmp_path / "measure31_diag_summary.json").is_file()
    assert m31.main(["--out", str(out), "--summarize-diag"]) == 0
