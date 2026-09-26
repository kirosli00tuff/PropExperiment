"""Stage E.2a Task 13: the power gate generalized per exposure (funnel/exposure_gate.py,
funnel/exposure_segments.py). Known answers on synthetic inputs, plus the MES regression:
a fast one at 200 runs against funnel.power_gate.evaluate_point itself, and (E2A_SLOW=1) the
8,000-run binding cell against D.1e's stored row and samples."""

from __future__ import annotations

import json
import math
import os
from dataclasses import replace
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytest

from data.research_bars import RESEARCH, RESEARCH_SERIES_PATH, HoldoutLeakError
from funnel import exposure_gate as eg
from funnel.exposure_segments import (
    MES_WINDOW,
    DateRule,
    SessionWindow,
    TickScaleError,
    build_exposure_segment_table,
    load_exposure_bars,
    mean_abs_move_ticks,
    tick_scale_check,
    to_ticks,
    vendor_tick_from_probe,
)
from funnel.null_generator import NullDayGenerator, SegmentTable, build_segment_table
from funnel.power_gate import BASE_SEED

CT = ZoneInfo("America/Chicago")
ROOT = Path(__file__).resolve().parents[1]
RULE = DateRule(date(2025, 4, 1), date(2026, 6, 12), frozenset({RESEARCH}))


# ------------------------------------------------------------- fixtures ----
def _bars(days: dict[str, list[tuple[str, float, float, float, float]]], *,
          instrument: dict[str, list[int]] | None = None, flatten_from: str = "15:10"
          ) -> pd.DataFrame:
    """Minute bars from {trade_date: [(HH:MM CT, open, high, low, close), ...]}."""
    rows = []
    for day, bars in days.items():
        for i, (hhmm, o, h, lo, c) in enumerate(bars):
            local = datetime.fromisoformat(f"{day} {hhmm}").replace(tzinfo=CT)
            rows.append({"ts_event": int(local.timestamp()) * 1_000_000_000, "open": o, "high": h,
                         "low": lo, "close": c, "trade_date": day,
                         "in_flatten_window": hhmm >= flatten_from,
                         "instrument_id": (instrument or {}).get(day, [7] * len(bars))[i]})
    return pd.DataFrame(rows).sort_values("ts_event").reset_index(drop=True)


def _day(start: str, n: int, base: float, step: float, tick: float) -> list[tuple]:
    """n consecutive minutes from ``start``; bar k opens at base + k*step*tick, closes one tick
    higher, spans +-2 ticks."""
    t0 = datetime.fromisoformat(f"2000-01-01 {start}")
    out = []
    for k in range(n):
        o = base + k * step * tick
        out.append(((t0 + timedelta(minutes=k)).strftime("%H:%M"), o, o + 2 * tick, o - 2 * tick,
                    o + tick))
    return out


def _table(moves: list[list[int]], minutes: tuple[int, int] = (510, 911)) -> SegmentTable:
    m = np.array(moves, dtype=np.int64)
    days, t = m.shape
    return SegmentTable(trade_dates=tuple(f"2025-05-{d + 1:02d}" for d in range(days)),
                        segments_per_day=t, move_ticks=m, low_ticks=np.minimum(m, 0) - 1,
                        high_ticks=np.maximum(m, 0) + 1,
                        entry_minute_ct=np.full((days, t), minutes[0], dtype=np.int64),
                        exit_minute_ct=np.full((days, t), minutes[1], dtype=np.int64))


def _flat_book(size_units: int, cents: int, minutes=(510, 911)) -> eg.MinuteCostBook:
    return eg.MinuteCostBook(size_units, {m: cents for m in minutes})


def _critical(robust: float = 50.0) -> eg.CriticalValues:
    return eg.CriticalValues("test", {f"{p}|c{c}": robust for p in ("standard", "consistency")
                                      for c in (80, 90, 95)})


def _ctx(table: SegmentTable, **kw) -> eg.ExposureContext:
    base = dict(exposure="SYN", vehicle="SYN", q=1, lot_weight=1.0, tick_value_usd=12.5,
                tables={table.segments_per_day: table, 1: table}, book=_flat_book(10, 300),
                critical=_critical(), runs=12)
    return eg.ExposureContext(**{**base, **kw})


# ------------------------------------------------------ segment tables ----
def test_segment_table_known_answer_two_segments_cents_quoted() -> None:
    """A ZC-like product quoted in cents (vendor tick 0.25): window [08:30, 13:18), 4 bars a day,
    T = 2 -> bars {0,1} and {2,3}; moves in vendor ticks."""
    tick = 0.25
    bars = _bars({"2025-05-06": _day("08:30", 4, 450.00, 3, tick)}, flatten_from="13:18")
    window = SessionWindow(8 * 60 + 30, 13 * 60 + 18)
    table, report = build_exposure_segment_table(bars, 2, tick=tick, window=window, rule=RULE)
    # opens (ticks): 1800, 1803, 1806, 1809; closes = open + 1
    assert table.move_ticks.tolist() == [[1804 - 1800, 1810 - 1806]]
    assert table.low_ticks.tolist() == [[-2, -2]]
    assert table.high_ticks.tolist() == [[1803 + 2 - 1800, 1809 + 2 - 1806]]
    assert table.entry_minute_ct.tolist() == [[510, 512]]
    assert table.exit_minute_ct.tolist() == [[512, 514]]
    assert report["days_kept"] == 1 and report["tick_scale_check"]["off_grid_share_1x"] == 0.0
    assert mean_abs_move_ticks(table) == 4.0


def test_segment_table_skip_rules() -> None:
    tick = 0.25
    days = {
        "2025-05-06": _day("08:30", 4, 100.0, 1, tick),  # kept
        "2025-05-07": _day("08:31", 4, 100.0, 1, tick),  # first bar not at O
        "2025-05-08": _day("08:30", 1, 100.0, 1, tick),  # fewer bars than T
        "2025-05-09": _day("08:30", 4, 100.0, 1, tick),  # excluded by the date rule
        "2025-05-12": _day("08:30", 4, 100.0, 1, tick),  # a roll splice inside the window
    }
    bars = _bars(days, instrument={"2025-05-12": [1, 1, 2, 2]})
    rule = replace(RULE, exclude=frozenset({"2025-05-09"}))
    table, report = build_exposure_segment_table(bars, 2, tick=tick, window=MES_WINDOW,
                                                 rule=rule, require_single_instrument=True)
    assert table.trade_dates == ("2025-05-06",)
    assert report["skipped_by_cause"] == {"excluded": 1, "no_bar_at_open": 1, "short": 1,
                                          "two_instruments": 1}


def test_flatten_flag_and_end_minute_cut_the_window() -> None:
    tick = 0.25
    bars = _bars({"2025-05-06": _day("08:30", 6, 100.0, 1, tick)}, flatten_from="08:34")
    table, _ = build_exposure_segment_table(bars, 1, tick=tick,
                                            window=SessionWindow(510, 16 * 60), rule=RULE)
    assert table.exit_minute_ct.tolist() == [[514]]  # bars 08:30..08:33 only
    table, _ = build_exposure_segment_table(bars, 1, tick=tick,
                                            window=SessionWindow(510, 512, False), rule=RULE)
    assert table.exit_minute_ct.tolist() == [[512]]  # end minute (C) cuts at 08:32


def test_mes_parameters_reproduce_null_generator_table() -> None:
    rng = np.random.default_rng(5)
    days = {}
    for d in ("2025-05-06", "2025-05-07", "2025-05-08"):
        bars = []
        for hhmm in ["07:00"] + [f"{h:02d}:{m:02d}" for h in range(8, 16) for m in range(60)
                                 if (h, m) >= (8, 30)]:
            o = 5000.0 + 0.25 * int(rng.integers(-40, 40))
            bars.append((hhmm, o, o + 0.25 * int(rng.integers(0, 5)),
                         o - 0.25 * int(rng.integers(0, 5)), o + 0.25 * int(rng.integers(-3, 4))))
        days[d] = [(h, o, max(o, hi, c), min(o, lo, c), c) for h, o, hi, lo, c in bars]
    frame = _bars(days)
    for t in (1, 2, 4, 32):
        ref = build_segment_table(frame, t)
        mine, _ = build_exposure_segment_table(frame, t, tick=0.25, window=MES_WINDOW, rule=RULE)
        for f in ("move_ticks", "low_ticks", "high_ticks", "entry_minute_ct", "exit_minute_ct"):
            assert np.array_equal(getattr(ref, f), getattr(mine, f)), (t, f)
        assert ref.trade_dates == mine.trade_dates


def test_research_only_dates_and_file_names(tmp_path: Path) -> None:
    bars = _bars({"2026-06-22": _day("08:30", 3, 100.0, 1, 0.25)})
    with pytest.raises(HoldoutLeakError):
        build_exposure_segment_table(bars, 1, tick=0.25, window=MES_WINDOW,
                                     rule=replace(RULE, last=date(2026, 6, 30)))
    with pytest.raises(ValueError, match="research-window parquets only"):
        load_exposure_bars(tmp_path / "x_confirmation.parquet", RULE)
    with pytest.raises(ValueError, match="research-window classes"):
        DateRule(date(2019, 5, 1), date(2019, 6, 1), frozenset({"confirmation"}))


def test_load_exposure_bars_reads_date32_and_refuses_holdout(tmp_path: Path) -> None:
    frame = _bars({"2025-05-06": _day("08:30", 3, 100.0, 1, 0.25)})
    frame["trade_date"] = pd.to_datetime(frame["trade_date"]).dt.date
    path = tmp_path / "ohlcv-1m_SYN_v_0_2025-04-01_2026-06-19_research.parquet"
    frame.to_parquet(path)
    out = load_exposure_bars(path, RULE)
    assert out["trade_date"].tolist() == ["2025-05-06"] * 3
    bad = pd.concat([frame, _bars({"2026-06-22": _day("08:30", 1, 100.0, 1, 0.25)})])
    bad["trade_date"] = pd.to_datetime(bad["trade_date"]).dt.date
    bad.to_parquet(path)
    with pytest.raises(HoldoutLeakError):
        load_exposure_bars(path, replace(RULE, last=date(2026, 6, 30)))


# ------------------------------------------------------------------ ticks ----
def test_tick_scale_check_refuses_a_tick_100x_too_fine() -> None:
    prices = 450.0 + 0.25 * np.arange(400)  # cents, quarter-cent grid
    assert tick_scale_check(prices, 0.25)["off_grid_share_2x"] == pytest.approx(0.5)
    with pytest.raises(TickScaleError, match="coarser"):
        tick_scale_check(prices, 0.0025)  # the E.0 USD tick applied to cents
    with pytest.raises(TickScaleError, match="off the"):
        tick_scale_check(prices, 0.5)
    assert to_ticks(np.array([450.25, 450.5]), 0.25).tolist() == [1801, 1802]
    with pytest.raises(TickScaleError):
        to_ticks(np.array([450.1]), 0.25)


def test_vendor_tick_from_probe() -> None:
    assert vendor_tick_from_probe(0.0025, {"x1": 0, "x10": 0, "x100": 0}) == pytest.approx(0.25)
    assert vendor_tick_from_probe(0.25, {"x1": 0, "x10": 900, "x100": 990}) == 0.25
    with pytest.raises(TickScaleError):
        vendor_tick_from_probe(0.25, {"x1": 3, "x10": 900, "x100": 990})


# --------------------------------------------------------- size and money ----
@pytest.mark.parametrize(("lot_weight", "tick_value", "units", "factor"), [
    (0.1, 1.25, 1, 1.0),  # MES: identity
    (1.0, 12.5, 10, 1.0),  # ZC, a mini: $12.50 per tick per contract
    (1.0, 15.625, 10, 1.25),  # ZN
    (0.2, 5.0, 2, 2.0),  # SIL counts as 2 micros
    (0.1, 0.5, 1, 0.4),  # MNQ
])
def test_units_and_money_factor(lot_weight, tick_value, units, factor) -> None:
    assert eg.units_per_contract(lot_weight) == units
    assert eg.money_factor(tick_value, lot_weight) == pytest.approx(factor)
    for q in (1, 2):
        for ticks in (-7, 1, 13):
            size = q * units
            booked = round(size * ticks * eg.money_factor(tick_value, lot_weight) * 125)
            assert booked == round(q * ticks * tick_value * 100)


def test_scaled_generator_uses_the_same_draws() -> None:
    table = _table([[10, -4], [3, 8], [-6, 2]])
    inner = NullDayGenerator(table)
    a = inner.draw(np.random.default_rng(1), 50)
    b = eg.ScaledDayGenerator(inner, 2.5).draw(np.random.default_rng(1), 50)
    assert np.array_equal(a.day_index, b.day_index) and np.array_equal(a.side, b.side)
    assert np.array_equal(b.pnl_ticks, a.pnl_ticks * 2.5)
    assert np.array_equal(b.adverse_ticks, a.adverse_ticks * 2.5)
    assert eg.scaled(inner, 1.0) is inner


# ------------------------------------------------------------------- cost ----
def test_side_cents_and_net_edge_arithmetic() -> None:
    """q = 3, RT commission $2.00, 0.5 tick slippage per side, $5 tick: one side =
    ceil(3 x (100 + 250)) = 1,050 cents; round turn per contract = $7.00 = 1.4 ticks."""
    assert eg.side_cents(3, 2.00, 0.5, 5.0) == 1050
    assert eg.side_cents(1, 1.22, 0.3, 1.25) == math.ceil(61 + 37.5)  # MES-like: 99
    table = _table([[10, -30], [20, 40]])  # E|m_2| = 25 ticks
    ctx = _ctx(table, q=3, lot_weight=0.1, tick_value_usd=5.0, book=_flat_book(3, 1050))
    cell = eg.Cell("standard", 2, 0.6, 1.0)
    f = eg.analytic_fields(ctx, cell)
    assert f["expected_gross_edge_ticks_per_trade_per_contract"] == pytest.approx(25 * 0.2)
    assert f["mean_round_turn_cost_usd_per_contract"] == pytest.approx(7.0)
    assert f["rt_cost_ticks"] == pytest.approx(1.4)
    assert f["net_edge_ticks_per_trade_per_contract"] == pytest.approx(5.0 - 1.4)
    assert f["net_edge_usd_per_day_at_q"] == pytest.approx((25.0 - 7.0) * 3 * 2)


def test_d8_side_cost_fn_averages_buy_and_sell() -> None:
    class Model:
        commission_rt_usd = 5.28
        tick_value_usd = 12.5

        def side_slippage_ticks(self, at, side):
            assert at.hour == 9 and at.minute == 5
            return {"buy": 0.5, "sell": 1.0}[side]

    fn = eg.d8_side_cost_fn(Model(), 1)
    assert fn(9 * 60 + 5) == math.ceil(264 + 0.75 * 1250)
    book = eg.minute_cost_book(10, fn, [545])
    assert book.side_cents(545, 10) == 1202
    with pytest.raises(ValueError, match="wiring"):
        book.side_cents(545, 20)


# --------------------------------------------------------------- eps rule ----
def _row(key: str, net: float, verdict: str) -> dict:
    return {"cell_key": key, "net_edge_usd_per_day_at_q": net, "robust_c80_verdict": verdict}


def test_eps_floor_rule_excludes_marginal() -> None:
    rows = [_row("a", 84.41, "marginal"), _row("b", 87.48087, "pass"), _row("c", 60.0, "fail"),
            _row("d", 120.0, "pass")]
    out = eg.eps_funnel(rows, 2, 1.25)
    assert out["eps_funnel"] == 34 and out["binding_cell"] == "b"
    assert out["counts"] == {"pass": 2, "marginal": 1, "fail": 1, "of_which_early_stopped": 0}
    op = eg.eps_operative(2, 1.25, out)
    assert op == {"eps_translated": 34, "eps_funnel": 34, "eps_operative": 34,
                  "flag_r12_no_passing_cell": False}
    assert eg.eps_operative(1, 12.5, eg.eps_funnel([_row("b", 40.0, "pass")], 1, 12.5)) == {
        "eps_translated": 6, "eps_funnel": 3, "eps_operative": 3,
        "flag_r12_no_passing_cell": False}


def test_no_passing_cell_is_flagged_and_translated_bar_used() -> None:
    out = eg.eps_funnel([_row("a", 90.0, "marginal"), _row("b", 50.0, "fail")], 1, 12.5)
    assert out["eps_funnel"] is None and out["flag"] == "no_passing_cell"
    assert eg.eps_operative(1, 12.5, out) == {"eps_translated": 6, "eps_funnel": None,
                                              "eps_operative": 6,
                                              "flag_r12_no_passing_cell": True}


def test_ascending_shortcut_is_exact_even_when_power_is_not_monotone() -> None:
    """A pass at $10 below a fail at $20: the first pass in ascending order is still the
    minimum over passing cells, because every cheaper cell was evaluated first."""
    cells = [eg.Cell(p, t, 0.5, r) for t, r in ((1, 1.0), (1, 1.5), (2, 1.0), (2, 2.0))
             for p in ("standard", "consistency")]
    net = {1: {1.0: 10.0, 1.5: 30.0}, 2: {1.0: 20.0, 2.0: 5.0}}
    verdicts = {("standard", 2, 2.0): "fail", ("consistency", 2, 2.0): "marginal",
                ("standard", 1, 1.0): "pass", ("consistency", 1, 1.0): "fail",
                ("standard", 2, 1.0): "fail", ("consistency", 2, 1.0): "fail",
                ("standard", 1, 1.5): "pass", ("consistency", 1, 1.5): "pass"}
    rows = {c.key: {**_row(c.key, net[c.segments_per_day][c.win_loss_ratio],
                           verdicts[(c.path, c.segments_per_day, c.win_loss_ratio)]),
                    "segments_per_day": c.segments_per_day} for c in cells}
    out = eg.ascending_shortcut(rows, cells)
    assert out["min_pass_net_usd_per_day_shortcut"] == 10.0 == out["min_pass_net_usd_per_day_full"]
    assert out["cells_evaluated"] == 4 and out["cells_saved"] == 4  # ties evaluated together
    assert out["evaluated_verdicts"] == {"pass": 1, "marginal": 1, "fail": 2}
    groups = eg.ascending_order(cells, {k: v["net_edge_usd_per_day_at_q"] for k, v in rows.items()})
    assert [len(g) for g in groups] == [2, 2, 2, 2]


def test_d3_cell_set_is_220_distinct_cells() -> None:
    cells = eg.d3_cell_set()
    assert len(cells) == 220 and len(eg.grid_cells()) == 120 and len(eg.extension_cells()) == 100
    by_t = {t: sum(1 for c in cells if c.segments_per_day == t) for t in (1, 2, 4, 8, 16, 32)}
    assert by_t == {1: 64, 2: 60, 4: 62, 8: 18, 16: 12, 32: 4}
    assert "consistency|T2|p0.6|R1.0" in {c.key for c in cells}


# ----------------------------------------------------------------- runner ----
def test_run_exposure_resumes_and_refuses_another_configuration(tmp_path: Path) -> None:
    table = _table([[40, -30], [25, 60], [-50, 10], [70, -20]])
    ctx = _ctx(table)
    cells = [eg.Cell("standard", 2, 0.6, 1.0), eg.Cell("consistency", 2, 0.55, 1.5)]
    logs: list[str] = []
    first = eg.run_exposure(ctx, cells[:1], tmp_path, workers=1, log=logs.append)
    assert [r["cell_key"] for r in first] == [cells[0].key]
    logs.clear()
    both = eg.run_exposure(ctx, cells, tmp_path, workers=1, log=logs.append)
    assert [r["cell_key"] for r in both] == [c.key for c in cells]
    assert sum(1 for s in logs if "|T2|" in s) == 1 and cells[1].key in logs[-1]
    lines = (tmp_path / "cells.jsonl").read_text().splitlines()
    assert len(lines) == 2 and json.loads(lines[0]) == first[0]
    assert (tmp_path / "samples" / "standard_T2_p0.6_R1.0.npy").exists()
    with pytest.raises(ValueError, match="another configuration"):
        eg.run_exposure(replace(ctx, q=2, book=_flat_book(20, 300)), cells, tmp_path, workers=1)


def test_run_exposure_ascending_mode_stops_at_first_pass(tmp_path: Path) -> None:
    table = _table([[400, -300], [250, 600], [-500, 100], [700, -200]])
    ctx = _ctx(table, critical=_critical(robust=-1e9))  # every cell passes
    cells = [eg.Cell("standard", 2, 0.6, 1.0), eg.Cell("standard", 2, 0.45, 1.0),
             eg.Cell("standard", 2, 0.55, 1.0)]
    rows = eg.run_exposure(ctx, cells, tmp_path, workers=1, mode="ascending", log=lambda s: None)
    assert [r["cell_key"] for r in rows] == [cells[1].key]  # the lowest net $/day only


def test_workers_do_not_change_results() -> None:
    table = _table([[40, -30], [25, 60], [-50, 10], [70, -20]])
    ctx = _ctx(table, runs=40)
    null = eg.null_samples(ctx, "standard", workers=1)
    assert np.array_equal(null, eg.null_samples(ctx, "standard", workers=2))
    a = eg.evaluate_cell(ctx, eg.Cell("standard", 2, 0.6, 1.0), null, workers=1)
    b = eg.evaluate_cell(ctx, eg.Cell("standard", 2, 0.6, 1.0), null, workers=2)
    assert np.array_equal(a.pop("_net_samples"), b.pop("_net_samples"))
    del a["wall_seconds"], b["wall_seconds"]
    assert a == b
    cfg = eg.FunnelConfig(eg.PayoutPath.STANDARD, ctx.size_units)
    gen = eg.QualityDayGenerator(table, eg.QualityParams(0.6, 1.0))
    fork = eg.run_many_with_book(cfg, gen, 30, BASE_SEED, ctx.book, workers=2, chunk=7)
    server = eg.run_many_with_book(cfg, gen, 30, BASE_SEED, ctx.book, workers=2, chunk=7,
                                   start_method="forkserver")
    assert fork == server


# ----------------------------------------------------------- MES regression ----
needs_mes = pytest.mark.skipif(not RESEARCH_SERIES_PATH.exists(),
                               reason="MES research bars not on disk")


@needs_mes
def test_mes_generalized_path_equals_power_gate_at_small_n() -> None:
    """The generalized path with MES's inputs vs funnel.power_gate.evaluate_point, 200 runs."""
    from funnel import exposure_gate_mes as m
    from funnel import power_gate
    from funnel.null_generator import load_null_generator
    from funnel.simulator import FunnelConfig, monthly_net_usd, run_many
    from rules.xfa_rules import PayoutPath

    tables, _ = m.mes_tables()
    for t in (1, 2):
        assert m.table_regression({t: tables[t]})[str(t)]["equal"]
    ctx = replace(m.mes_context(tables), runs=200)
    baseline = json.loads(m.BASELINE_JSON.read_text())
    gens = {1: load_null_generator(1), 2: load_null_generator(2)}
    cfg = FunnelConfig(PayoutPath.CONSISTENCY, 2)
    null_ref = np.sort(monthly_net_usd(run_many(cfg, gens[1], 200, BASE_SEED + 1, workers=2),
                                       cfg.horizon_days))
    null_mine = eg.null_samples(ctx, "consistency", workers=2)
    assert np.array_equal(null_ref, null_mine)
    cell = eg.Cell("consistency", 2, 0.6, 1.0)
    ref = power_gate.evaluate_point(PayoutPath.CONSISTENCY, cell.params, 2, 2, 200, gens,
                                    baseline, null_ref)
    mine = eg.evaluate_cell(ctx, cell, null_mine, workers=2)
    assert np.array_equal(ref.pop("_net_samples"), mine.pop("_net_samples"))
    cmp = m.compare_row(mine, ref)
    assert cmp["equal"], cmp["mismatches"]
    assert cmp["fields_compared"] == len(ref)


@needs_mes
@pytest.mark.skipif(os.environ.get("E2A_SLOW") != "1", reason="set E2A_SLOW=1 (8,000 runs)")
def test_mes_binding_cell_equals_d1e_stored_row() -> None:
    """D.1e's binding cell at 8,000 runs: every stored field and the sorted samples."""
    from funnel import exposure_gate_mes as m

    tables, _ = m.mes_tables()
    ctx = m.mes_context({1: tables[1], 2: tables[2]})
    cell = eg.Cell("consistency", 2, 0.6, 1.0)
    null = eg.null_samples(ctx, "consistency", workers=8)
    row = eg.evaluate_cell(ctx, cell, null, workers=8)
    stored = m.stored_rows()[cell.key]
    with np.load(m.GATE_SAMPLES) as z:
        assert np.array_equal(row.pop("_net_samples"), z[cell.key])
    cmp = m.compare_row(row, stored)
    assert cmp["equal"], cmp["mismatches"]
    assert row["net_edge_usd_per_day_at_q"] == pytest.approx(87.48087096774192, abs=0)
    assert eg.eps_funnel([row], 2, 1.25)["eps_funnel"] == 34


# ------------------------------------------------ Stage E options (R3, L-10) ----
def test_first_bar_at_or_after_open_and_same_calendar_day() -> None:
    """R3: the first bar at or after O counts when the O minute itself has no bar; L-10: bars of
    another calendar day inside [O, C) (a booked-in holiday session) are not in the window."""
    tick = 0.25
    day = _day("08:31", 4, 100.0, 1, tick)
    bars = _bars({"2025-05-06": day})
    stray = _bars({"2025-05-05": _day("08:40", 2, 90.0, 1, tick)})
    stray["trade_date"] = "2025-05-06"  # booked forward to the next trade date
    frame = pd.concat([stray, bars]).sort_values("ts_event").reset_index(drop=True)
    window = SessionWindow(510, 900, require_bar_at_open=False, same_calendar_day=True)
    table, _ = build_exposure_segment_table(frame, 1, tick=tick, window=window, rule=RULE)
    assert table.entry_minute_ct.tolist() == [[511]] and table.move_ticks.tolist() == [[4]]
    strict = SessionWindow(510, 900)  # MES's rule: no bar at 08:30 -> skipped
    with pytest.raises(ValueError, match="no trade date survives"):
        build_exposure_segment_table(bars, 1, tick=tick, window=strict, rule=RULE)


# ------------------------------------------------------ addendum A-1 ----
def test_max_failures_for_pass_matches_verdict() -> None:
    from funnel.power_gate import verdict

    assert eg.max_failures_for_pass(8000) == 1531
    assert verdict(6469 / 8000, 8000)[0] == "pass" and verdict(6468 / 8000, 8000)[0] != "pass"


def _cell_setup(runs: int = 60):
    table = _table([[40, -30], [25, 60], [-50, 10], [70, -20]])
    ctx = _ctx(table, runs=runs)
    cfg = eg.FunnelConfig(eg.PayoutPath.STANDARD, ctx.size_units)
    gen = eg.QualityDayGenerator(table, eg.QualityParams(0.6, 1.0))
    return ctx, cfg, gen


@pytest.mark.parametrize("workers", [1, 2])
def test_early_stop_runner_prefix_is_the_full_run_prefix(workers: int) -> None:
    ctx, cfg, gen = _cell_setup()
    full = eg.run_many_with_book(cfg, gen, 60, BASE_SEED, ctx.book, workers=1)
    net_full = eg.monthly_net_usd(full, cfg.horizon_days)
    k = float(np.median(net_full))
    same, stopped, f = eg.run_many_early_stop(cfg, gen, 60, BASE_SEED, ctx.book, workers=workers,
                                              critical_value=k, max_failures=60, chunk=7)
    assert not stopped and same == full and f == int(np.sum(~(net_full > k)))
    part, stopped, f = eg.run_many_early_stop(cfg, gen, 60, BASE_SEED, ctx.book, workers=workers,
                                              critical_value=k, max_failures=5, chunk=7)
    n = len(part)
    assert stopped and n % 7 == 0 and part == full[:n]
    assert f == int(np.sum(~(net_full[:n] > k))) > 5
    assert int(np.sum(~(net_full[:n - 7] > k))) <= 5  # it stopped at the first chunk possible


def test_evaluate_cell_early_stop(tmp_path: Path) -> None:
    ctx, _, _ = _cell_setup(runs=40)
    null = eg.null_samples(ctx, "standard", workers=1)
    cell = eg.Cell("standard", 2, 0.6, 1.0)
    full = eg.evaluate_cell(ctx, cell, null, workers=1)
    kept = eg.evaluate_cell(ctx, cell, null, workers=1, early_stop=True)  # every career passes
    assert np.array_equal(full.pop("_net_samples"), kept.pop("_net_samples"))
    assert kept.pop("early_stopped") is False
    del full["wall_seconds"], kept["wall_seconds"]
    assert full == kept
    hard = replace(ctx, critical=_critical(robust=1e9))  # nobody beats $1bn a month
    row = eg.evaluate_cell(hard, cell, null, workers=1, early_stop=True)
    # 40 runs fit in one batch of 50: the prefix is the whole run, so the full row is kept
    assert row["early_stopped"] is False and row["robust_c80_verdict"] == "fail"
    hard80 = replace(hard, runs=600)  # every career fails; stop at the first batch past m
    m = eg.max_failures_for_pass(600)
    expected = math.ceil((m + 1) / eg.EARLY_STOP_CHUNK) * eg.EARLY_STOP_CHUNK
    assert expected < 600
    row = eg.evaluate_cell(hard80, cell, eg.null_samples(hard80, "standard", workers=1),
                           workers=1, early_stop=True)
    assert row["early_stopped"] and row["robust_c80_verdict"] == "fail"
    assert row["early_stop_runs"] == expected and row["early_stop_failures"] == expected
    assert row["verdict_note"] == f"fail (pass impossible after {expected} runs)"
    assert "_net_samples" not in row and row["robust_c80_power"] is None
    rows = eg.run_exposure(hard80, [cell], tmp_path, workers=1, early_stop=True,
                           log=lambda s: None)
    assert rows[0]["early_stopped"] and not (tmp_path / "samples").exists()
