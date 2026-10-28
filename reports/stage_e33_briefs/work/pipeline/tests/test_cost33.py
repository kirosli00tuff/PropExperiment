"""Tests for cost33 (Stage E.33 StatsCostCoder, prompt B6). Hand-built books and trades only; E.28's fee files;
E.31's pilot code (measure31_core, mbo_book31, kalgo31, stats31_core, stats31) imported as is, never edited.

Run: uv run pytest -q reports/stage_e33_briefs/work/pipeline/tests/test_cost33.py
"""
from __future__ import annotations

import math
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
REPO = PIPE.parents[3]
PILOT = REPO / "reports" / "stage_e31_briefs" / "work" / "pilot"
for _p in (str(REPO), str(PIPE), str(PILOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cost33 as c  # noqa: E402
import kalgo31 as ka  # noqa: E402
import mbo_book31 as mb  # noqa: E402
import measure31_core as mc  # noqa: E402
import stats31 as s31  # noqa: E402
import stats31_core as s31c  # noqa: E402

NS = c.NS
T0 = 1_000 * NS  # decision time t in the hand-built cases
SESSION_END = 5_000 * NS
FEE = 0.528
E31_NAME = {"topstep": "Topstep", "lucid": "Lucid", "bulenox": "Bulenox", "mffu": "MFFU", "tradeify": "Tradeify"}


# ------------------------------------------------------------------------------------------- fees --
def test_e28_fees_match_protocol_p64_and_p03():
    fees = c.load_firm_fees()
    rep = c.fee_report(fees)
    assert rep["differences"] == [] and rep["p03_difference"] == []
    got = {f.firm: f.fee_rt_ticks for f in fees}
    for firm, want in {"topstep": 0.528, "lucid": 0.560, "bulenox": 0.572, "mffu": 0.612,
                       "tradeify": 0.920}.items():
        assert got[firm] == pytest.approx(want, abs=1e-12)
    usd = {f.firm: f.fee_rt_usd for f in fees}
    assert usd == {"topstep": 5.28, "lucid": 5.60, "bulenox": 5.72, "mffu": 6.12, "tradeify": 9.20}
    assert c.fee_variants(fees)["lucid_not_all_in"] == pytest.approx(0.920)


def test_fee_report_flags_a_difference():
    fees = c.load_firm_fees()
    bad = [c.FirmFee(f.firm, f.fee_rt_usd, f.fee_rt_ticks + (0.01 if f.firm == "mffu" else 0.0), f.source,
                     f.quote, f.note, f.a3_products_ticks, f.a3_econ_ticks, f.protocol_ticks) for f in fees]
    diffs = c.fee_report(bad)["differences"]
    assert any(d.startswith("mffu: E.28 A2") for d in diffs)
    assert any("A3_firm_products" in d for d in diffs)


def test_per_fill_fee_equals_e31_fee_per_fill():
    """E.31 stats31_core: FEE_PER_FILL_TICKS = RT / 2 / 10; cost33 per fill = fee_rt_ticks / 2."""
    for f in c.load_firm_fees():
        name = E31_NAME[f.firm]
        assert s31c.FEES_RT_USD[name] == pytest.approx(f.fee_rt_usd, abs=1e-12)
        assert s31c.FEE_PER_FILL_TICKS[name] == pytest.approx(f.per_fill_ticks, abs=1e-12)


def test_firm_nets_subtract_each_round_trip_fee():
    nets = c.firm_nets(8.0, c.fee_variants(c.load_firm_fees()))
    assert nets == pytest.approx({"topstep": 7.472, "lucid": 7.44, "bulenox": 7.428, "mffu": 7.388,
                                  "tradeify": 7.08, "lucid_not_all_in": 7.08})


# ----------------------------------------------------------------------------- (i) market round trip --
def _touch_basic() -> c.Touch:
    """Valid book throughout: the touch before t, before t + L, before t + 300 s and before t + h + L."""
    return c.Touch.of(
        [T0 - 10 * NS, T0 + NS // 2, T0 + 30 * NS, T0 + 200 * NS, T0 + 300 * NS + NS // 2],
        [4000, 4001, 4004, 4007, 4010],
        [4001, 4002, 4005, 4008, 4011])


def test_market_round_trip_p33_long_short_and_identity():
    tch = _touch_basic()
    lo = c.market_round_trip(tch, T0, T0 + 300 * NS, c.LONG, FEE, session_end=SESSION_END)
    sh = c.market_round_trip(tch, T0, T0 + 300 * NS, c.SHORT, FEE, session_end=SESSION_END)
    # N_long = bid_1(t + h + L) - ask_1(t + L) - f = 4010 - 4002 - 0.528
    assert (lo.entry_px, lo.exit_px, lo.flags) == (4002, 4010, 0)
    assert lo.net == pytest.approx(7.472) and lo.gross == 8.0
    # N_short = bid_1(t + L) - ask_1(t + h + L) - f = 4001 - 4011 - 0.528
    assert (sh.entry_px, sh.exit_px) == (4001, 4011) and sh.net == pytest.approx(-10.528)
    # P3.3 (M3 f.2): N_long + N_short = -s(t + L) - s(t + h + L) - 2 f
    assert lo.net + sh.net == pytest.approx(-1 - 1 - 2 * FEE)
    assert lo.entry_ns == T0 + NS and lo.exit_ns == T0 + 301 * NS


def test_market_round_trip_fast_latency_variant():
    lo = c.market_round_trip(_touch_basic(), T0, T0 + 300 * NS, c.LONG, FEE, latency=c.L_FAST_NS,
                             session_end=SESSION_END)
    assert (lo.entry_px, lo.exit_px) == (4001, 4007) and lo.net == pytest.approx(6 - FEE)


def test_market_entry_fallback_and_not_made():
    tch = c.Touch.of([T0 - 10 * NS, T0 + NS // 2, T0 + 5 * NS, T0 + 300 * NS + NS // 2],
                     [4000, 4001, 4003, 4010], [4001, c.NO_PX, 4004, 4011])
    lo = c.market_round_trip(tch, T0, T0 + 300 * NS, c.LONG, FEE, session_end=SESSION_END)
    assert lo.flags == c.FLAG_ENTRY_FALLBACK and (lo.entry_px, lo.entry_ns) == (4004, T0 + 5 * NS)
    sh = c.market_round_trip(tch, T0, T0 + 300 * NS, c.SHORT, FEE, session_end=SESSION_END)
    assert sh.flags == 0 and sh.entry_px == 4001  # the bid side exists at t + L
    bad = c.Touch.of([T0 - 10 * NS, T0 + NS // 2, T0 + 300 * NS], [4000, 4001, 4002], [4001, 4002, 4003],
                     bad=[False, True, False])  # bad from t + L until exactly the planned exit
    assert c.market_round_trip(bad, T0, T0 + 300 * NS, c.LONG, FEE, session_end=SESSION_END) == c.NOT_MADE


def test_market_exit_fallback_limit_mark_and_last_touch():
    tch = c.Touch.of([T0 - 10 * NS, T0 + 300 * NS + NS // 2, T0 + 320 * NS],
                     [4000, c.NO_PX, 4006], [4001, 4012, 4007])
    lo = c.market_round_trip(tch, T0, T0 + 300 * NS, c.LONG, FEE, session_end=SESSION_END)
    assert lo.flags == c.FLAG_EXIT_FALLBACK and (lo.exit_px, lo.exit_ns) == (4006, T0 + 320 * NS)
    end = T0 + 310 * NS  # the session ends before the bid returns
    lim = c.market_round_trip(tch, T0, T0 + 300 * NS, c.LONG, FEE, session_end=end,
                              limit_px={c.LONG: 3900, c.SHORT: 4100})
    assert lim.flags == c.FLAG_EXIT_FALLBACK | c.FLAG_EXIT_LIMIT and lim.exit_px == 3900 and lim.exit_ns == end
    last = c.market_round_trip(tch, T0, T0 + 300 * NS, c.LONG, FEE, session_end=end)
    assert last.flags == c.FLAG_EXIT_FALLBACK | c.FLAG_EXIT_LAST_TOUCH and last.exit_px == 4000
    assert last.net == pytest.approx(4000 - 4001 - FEE)


# -------------------------------------------------------------------- (ii) trade-through limit entry --
def _trades_basic() -> c.Trades:
    return c.Trades.of(
        [T0 + NS // 2, T0 + NS, T0 + 5 * NS, T0 + 10 * NS, T0 + 20 * NS, T0 + 61 * NS + NS // 2],
        [4000, 4000, 4001, 4000, 4000, 4003],
        ["A", "A", "A", "N", "B", "B"])


def test_limit_window_is_min_60s_h_over_5():
    assert [c.limit_window_ns(h) for h in (5, 15, 30, 60)] == [60 * NS] * 4
    assert c.limit_window_ns(1) == 12 * NS
    with pytest.raises(ValueError):
        c.limit_window_ns(0)


def test_limit_long_fills_only_strictly_through_after_placement_by_a_or_b():
    out = c.limit_entry_through(_touch_basic(), _trades_basic(), T0, T0 + 300 * NS, c.LONG, FEE, 5,
                                session_end=SESSION_END)
    # rests at bid_1(t + L) = 4001; 4000 at t + 0.5 s is before placement, 4000 at exactly t + L is not a fill
    # (C1), 4001 at t + 5 s is at the price, 4000 'N' at t + 10 s is side N (C2); 4000 'B' at t + 20 s fills
    assert out.placed and out.filled and out.limit_px == 4001 and out.fill_ns == T0 + 20 * NS
    assert out.exit_px == 4010 and out.net == pytest.approx(4010 - 4001 - FEE)
    assert out.market.net == pytest.approx(7.472) and out.net_iib == out.net and out.converted is None


def test_limit_short_unfilled_window_closes_then_iib_converts_at_timeout():
    out = c.limit_entry_through(_touch_basic(), _trades_basic(), T0, T0 + 300 * NS, c.SHORT, FEE, 5,
                                session_end=SESSION_END)
    # rests at ask_1(t + L) = 4002; the only print above it (4003 at t + 61.5 s) is after t + L + 60 s
    assert out.placed and not out.filled and out.limit_px == 4002 and math.isnan(out.net)
    conv = out.converted
    # (ii-b): market sell as of t + L + 60 s at bid 4004, exit buy as of t + h + L at ask 4011
    assert conv.made and conv.flags & c.FLAG_CONVERTED and (conv.entry_px, conv.exit_px) == (4004, 4011)
    assert out.net_iib == pytest.approx(4004 - 4011 - FEE)
    assert out.market.net == pytest.approx(-10.528)


def test_limit_window_end_is_inclusive_at_t_plus_l_plus_w():
    tr = c.Trades.of([T0 + 61 * NS, T0 + 61 * NS + 1], [4003, 4003], ["B", "B"])
    out = c.limit_entry_through(_touch_basic(), tr, T0, T0 + 300 * NS, c.SHORT, FEE, 5, session_end=SESSION_END)
    assert out.filled and out.fill_ns == T0 + 61 * NS
    late = c.Trades.of([T0 + 61 * NS + 1], [4003], ["B"])
    assert not c.limit_entry_through(_touch_basic(), late, T0, T0 + 300 * NS, c.SHORT, FEE, 5,
                                     session_end=SESSION_END).filled


def test_limit_exit_decision_before_timeout_cuts_window_and_iib_is_zero_length():
    """READING C4 (a TB barrier inside the first minute): the window ends at the exit decision + L."""
    tr = c.Trades.of([T0 + 40 * NS], [4000], ["A"])
    out = c.limit_entry_through(_touch_basic(), tr, T0, T0 + 30 * NS, c.LONG, FEE, 15, session_end=SESSION_END)
    assert not out.filled
    conv = out.converted  # entry and exit both as of t + 31 s: ask 4005, bid 4004
    assert (conv.entry_px, conv.exit_px) == (4005, 4004) and out.net_iib == pytest.approx(-1 - FEE)


def test_limit_not_placed_without_own_touch():
    tch = c.Touch.of([T0 - 10 * NS, T0 + NS // 2, T0 + 30 * NS, T0 + 300 * NS + NS // 2],
                     [4000, c.NO_PX, 4004, 4010], [4001, 4002, 4005, 4011])
    out = c.limit_entry_through(tch, _trades_basic(), T0, T0 + 300 * NS, c.LONG, FEE, 5, session_end=SESSION_END)
    assert not out.placed and not out.filled and out.flags == c.FLAG_LIMIT_NOT_PLACED
    assert out.converted.made and out.converted.entry_px == 4005


def test_limit_summary_fields():
    tch, tr = _touch_basic(), _trades_basic()
    outs = [c.limit_entry_through(tch, tr, T0, T0 + 300 * NS, s, FEE, 5, session_end=SESSION_END)
            for s in (c.LONG, c.SHORT)]
    sm = c.limit_summary(outs)
    assert (sm["n_signals"], sm["n_fills"], sm["p_fill"]) == (2, 1, 0.5)
    assert sm["mean_net_fill"] == pytest.approx(9 - FEE)
    assert sm["mean_net_mkt_nofill"] == pytest.approx(-10.528)
    assert sm["opportunity_cost"] == pytest.approx(0.5 * -10.528)
    assert sm["mean_net_iib"] == pytest.approx(((9 - FEE) + (-7 - FEE)) / 2)


def test_round_trip_net_decomposes_into_entry_and_exit_fills():
    tch, tr = _touch_basic(), _trades_basic()
    out = c.limit_entry_through(tch, tr, T0, T0 + 300 * NS, c.LONG, FEE, 5, session_end=SESSION_END)
    entry = c.entry_leg_net(tch, c.LONG, out.limit_px, out.fill_ns, out.exit_ns - out.fill_ns, FEE)
    exit_ = c.exit_leg_net(tch, c.LONG, out.exit_px, out.exit_ns, FEE)
    assert entry + exit_ == pytest.approx(out.net, abs=1e-12)


def test_bad_inputs_raise():
    with pytest.raises(ValueError):
        c.Touch.of([2, 1], [1, 1], [2, 2])
    with pytest.raises(ValueError):
        c.Trades.of([2, 1], [1, 1], ["A", "A"])
    with pytest.raises(ValueError):
        c.through_fill(_trades_basic(), 4000, 0, 0, 1)
    with pytest.raises(ValueError):
        c.limit_summary([])


# ------------------------------------------------------------------- agreement with E.31's pilot code --
TICK_1E9 = 100_000_000  # ZM 0.10 in mbo_book31's 1e-9 fixed point
E31_SESSION = mc.Session(mc.DAY, 0, 900 * NS)  # one placement: g = 300 s, j = 300.05 s, end = 360.1 s


def _e31_records(states, trades) -> dict[str, np.ndarray]:
    """Hand-built MBO: a clear at 1 s, then per touch state one batch (adds of the new touch orders, cancels
    of the old, F_LAST on the batch's last record), and each trade as one T record with F_LAST."""
    rows = [(NS, mb.ACT_CLEAR, mb.SIDE_NONE_CODE, mb.UNDEF_PRICE, 0, 0, mb.F_LAST)]
    oid, cur = 100, {}
    for tau, bid, ask in states:
        batch = []
        for code, px in ((mb.SIDE_BID_CODE, bid), (mb.SIDE_ASK_CODE, ask)):
            if code in cur and cur[code][0] == px:
                continue
            oid += 1
            batch.append((tau, mb.ACT_ADD, code, px * TICK_1E9, 5, oid, 0))
            if code in cur:
                batch.append((tau, mb.ACT_CANCEL, code, cur[code][0] * TICK_1E9, 5, cur[code][1], 0))
            cur[code] = (px, oid)
        last = list(batch[-1])
        last[6] = mb.F_LAST
        rows += batch[:-1] + [tuple(last)]
    rows += [(tau, mb.ACT_TRADE, ord(side), px * TICK_1E9, 1, 0, mb.F_LAST) for tau, px, side in trades]
    rows.sort(key=lambda r: r[0])  # stable; a case never puts a state batch and a trade at one time
    cols = list(zip(*rows, strict=True))
    keys = ("t", "action", "side", "price", "size", "order_id", "flags")
    return {k: np.asarray(v, dtype=np.int64) for k, v in zip(keys, cols, strict=True)}


# (states (time, bid, ask), trades (time, price, aggressor side)); times in ns
E31_CASES = {
    "through_after_at_price_and_side_n": (
        [(2 * NS, 4000, 4001), (326 * NS, 4001, 4002), (335 * NS, 4003, 4004), (385 * NS, 3998, 3999)],
        [(310 * NS, 4000, "A"), (320 * NS, 3999, "N"), (325 * NS, 3999, "A"), (340 * NS, 4003, "B")]),
    "print_at_join_time_is_not_a_fill": (
        [(2 * NS, 4000, 4001), (351 * NS, 4002, 4003)],
        [(300_050_000_000, 3999, "A"), (300_050_000_000 + 1, 4000, "A"), (350 * NS, 3998, "B"),
         (355 * NS, 4002, "A")]),
    "prints_only_after_the_life": (
        [(2 * NS, 4000, 4001)],
        [(361 * NS, 3999, "A"), (362 * NS, 4002, "B")]),
    "touch_moves_order_price_stays": (
        [(2 * NS, 4000, 4001), (305 * NS, 4001, 4002), (345 * NS, 3997, 3998)],
        [(320 * NS, 4000, "B"), (330 * NS, 3999, "A"), (331 * NS, 4002, "B"), (340 * NS, 4001, "B")]),
    "at_price_only": (
        [(2 * NS, 4000, 4001)],
        [(310 * NS, 4000, "A"), (320 * NS, 4001, "B")]),
}


def _run_e31(states, trades):
    run = mc.InstrumentRun((E31_SESSION,), ka.ZM_K, False)
    run.run(_e31_records(states, trades))
    assert len(run.placements) == 2  # one grid time, a buy and a sell
    return run


def _e31_net_per_fill(run, pl, v) -> dict[int, dict[str, float]]:
    """E.31's own accounting: _fill_fields (markouts, c_half), stats31.edge_arrays (E_h = markout_h + c_half),
    N_h(firm) = E_h - FEE_PER_FILL_TICKS[firm] (stats31 horizon_block)."""
    hist = mc.History.of(run)
    lv = mc.last_valid_index(hist.valid)
    inv_cum = np.concatenate(([0], np.cumsum(~hist.valid)))
    job = mc.DayJob(day=date(2023, 1, 3), symbols=())
    row = mc._fill_fields(job, v, pl, hist, inv_cum, lv, {}, TICK_1E9, {})
    p = {k: np.asarray([row[k]], dtype=np.float64) for k in row if k.startswith(("mo_", "c_half"))}
    edges = s31.edge_arrays(p)["drop"]
    return {h: {firm: float(edges[h][0]) - fee for firm, fee in s31c.FEE_PER_FILL_TICKS.items()}
            for h in s31c.HORIZONS_S}


@pytest.mark.parametrize("case", sorted(E31_CASES))
def test_fill_decisions_and_per_fill_net_agree_with_e31(case):
    states, trades = E31_CASES[case]
    run = _run_e31(states, trades)
    tch = c.Touch.of(*zip(*states, strict=True))
    tr = c.Trades.of(*zip(*trades, strict=True))
    fees = {E31_NAME[f.firm]: f.fee_rt_ticks for f in c.load_firm_fees()}
    n_fills = 0
    for pl in run.placements:
        v = pl.orders["c"]
        side = c.LONG if pl.s > 0 else c.SHORT
        k = tch.asof(pl.j)
        assert pl.price == (tch.bid[k] if side == c.LONG else tch.ask[k]) * TICK_1E9  # the touch at placement
        # E.31's life is open at both ends, (j, end); cost33's window is closed at its end: end - 1 ns
        ours = c.through_fill(tr, pl.price // TICK_1E9, side, pl.j, pl.end - 1)
        assert ours == v.t_fill, (case, side, ours, v.t_fill)
        if v.t_fill is None:
            continue
        n_fills += 1
        assert v.trigger == mc.THROUGH
        e31 = _e31_net_per_fill(run, pl, v)
        for h in s31c.HORIZONS_S:
            for firm, fee_rt in fees.items():
                ours_net = c.entry_leg_net(tch, side, pl.price // TICK_1E9, v.t_fill, h * NS, fee_rt)
                assert ours_net == pytest.approx(e31[h][firm], abs=1e-9), (case, side, h, firm)
    expected = {"through_after_at_price_and_side_n": 2, "print_at_join_time_is_not_a_fill": 2,
                "prints_only_after_the_life": 0, "touch_moves_order_price_stays": 2, "at_price_only": 0}
    assert n_fills == expected[case]


def test_e31_window_differs_only_by_its_cancel_latency():
    """E.31's life is (j, j + 60 s + 50 ms); P6.4 (ii)'s window is (t + L, t + L + 60 s]. A print in the last
    50 ms fills under E.31's rule only: a documented difference of window length, not of the fill rule."""
    states, trades = [(2 * NS, 4000, 4001)], [(360_080_000_000, 3999, "A")]
    run = _run_e31(states, trades)
    buy = next(pl for pl in run.placements if pl.s > 0)
    assert buy.orders["c"].t_fill == 360_080_000_000
    tr = c.Trades.of(*zip(*trades, strict=True))
    t = buy.j - c.L_NS  # the P6.4 decision whose order rests at E.31's join time
    out = c.limit_entry_through(c.Touch.of(*zip(*states, strict=True)), tr, t, t + 300 * NS, c.LONG, FEE, 5,
                                session_end=900 * NS)
    assert out.placed and out.limit_px == 4000 and not out.filled
