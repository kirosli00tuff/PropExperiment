"""h6_rod.member through the frozen engine, unchanged, on synthetic bars (prereg section 3)."""

from __future__ import annotations

import math
from datetime import date

import pandas as pd
import pytest

from h6_rod import clock, engine, report, signal, stats
from tests._h6_rod_synth import day_frame, no_releases, ts_ns

MON, TUE, WED = date(2022, 3, 14), date(2022, 3, 15), date(2022, 3, 16)
THANKSGIVING, BLACK_FRIDAY = date(2022, 11, 24), date(2022, 11, 25)


def _bars(*day_rows: list[dict]) -> pd.DataFrame:
    rows = [r for rows in day_rows for r in rows]
    return pd.DataFrame(rows).sort_values("ts_event", kind="stable").reset_index(drop=True)


def _run(bars: pd.DataFrame, days: list[date], lead_in: tuple = (),
         blackout: frozenset = frozenset()) -> tuple[engine.EngineRun, signal.Schedule]:
    facts = signal.compute_facts(bars[["ts_event", "close", "instrument_id"]],
                                 sorted({*lead_in, *days}))
    sched = signal.t1_schedule(facts, days[0], days[-1])
    return engine.run_schedule(bars, sched, days, lead_in, blackout, no_releases()), sched


def _fills(run: engine.EngineRun) -> list:
    from screening.stage_e_engine import Fill

    return list(run.result.events(Fill))


def _refusals(run: engine.EngineRun) -> list[str]:
    from screening.stage_e_engine import IntentRecord

    return [e.refusal.reason for e in run.result.events(IntentRecord) if e.refusal is not None]


def _normal_pair(**tue_kw: object) -> pd.DataFrame:
    kw = {"base_ticks": 60_000, "close_ticks": {(14, 29): 60_040, (14, 45): 60_080}}
    kw.update(tue_kw)
    return _bars(day_frame(MON, close_ticks={(14, 59): 60_000}), day_frame(TUE, **kw))


# ------------------------------------------------------------------ entry and exit fills ----
def test_entry_fills_at_the_c30_open_and_exit_at_the_open_after_the_1458_bar() -> None:
    run, sched = _run(_normal_pair(open_ticks={(14, 30): 60_044}), [TUE], lead_in=(MON,))
    entry, exit_ = _fills(run)
    assert sched.entries[TUE].side == "buy"
    assert (entry.fill_ts_ns, entry.price, entry.side) == (ts_ns(TUE, 14, 30), 15011.00, "buy")
    assert entry.decision_ts_ns == ts_ns(TUE, 14, 30)  # decided at the 14:29 bar's close
    assert (exit_.fill_ts_ns, exit_.price, exit_.reason) == (ts_ns(TUE, 14, 59), 15020.00,
                                                             "strategy")
    assert exit_.decision_ts_ns == ts_ns(TUE, 14, 59)  # decided at the 14:58 bar's close
    trade, = stats.trades_from(run.result, run.rules, {})
    assert stats.ticks(trade.gross_cents, run.rules) == 36.0  # (15020.00 - 15011.00) / 0.25
    assert trade.exit_type == "c2_exit" and trade.price_check_ok


def test_a_missing_1458_bar_exits_on_the_next_present_bar() -> None:
    run, _ = _run(_normal_pair(skip=[(14, 58)]), [TUE], lead_in=(MON,))
    exit_ = _fills(run)[-1]
    assert exit_.decision_ts_ns == ts_ns(TUE, 15, 0)  # decided at the 14:59 bar's close
    assert exit_.fill_ts_ns == ts_ns(TUE, 15, 0) and exit_.reason == "strategy"


def test_with_no_bar_from_1458_to_1507_the_engine_flattens_at_f() -> None:
    skip = [(14, m) for m in range(58, 60)] + [(15, m) for m in range(0, 8)]
    run, _ = _run(_normal_pair(skip=skip), [TUE], lead_in=(MON,))
    exit_ = _fills(run)[-1]
    assert exit_.reason == "forced_flatten" and exit_.fill_ts_ns == ts_ns(TUE, 15, 9)
    trade, = stats.trades_from(run.result, run.rules, {TUE: False})
    assert trade.exit_type == "forced_flatten"


def test_a_short_entry_and_the_member_trades_at_most_once_a_day() -> None:
    bars = _bars(day_frame(MON, close_ticks={(14, 59): 60_000}),
                 day_frame(TUE, base_ticks=60_000, close_ticks={(14, 29): 59_960}),
                 day_frame(WED, base_ticks=59_960, close_ticks={(14, 29): 59_900}))
    run, sched = _run(bars, [TUE, WED], lead_in=(MON,))
    trades = stats.trades_from(run.result, run.rules, {})
    assert [t.trade_date for t in trades] == [TUE, WED]
    assert [t.side for t in trades] == ["sell", "sell"]
    assert all(t.n_fills == 2 for t in trades)


# ------------------------------------------------------------------ shortened day ----
def test_a_shortened_day_entry_at_early_close_minus_30_is_refused_by_the_engines_f() -> None:
    # 2022-11-25 halts 12:15 CT; the frozen engine's F that day is 11:45 (Topstep's derived
    # close-by, rules/sessions.py), which is C - 30: the entry decided at 11:45 is refused.
    bars = _bars(day_frame(THANKSGIVING, start=(11, 0), end=(12, 0),
                           close_ticks={(11, 59): 60_000}),
                 day_frame(BLACK_FRIDAY, start=(11, 0), end=(12, 15), base_ticks=60_000,
                           close_ticks={(11, 44): 60_040}))
    run, sched = _run(bars, [BLACK_FRIDAY], lead_in=(THANKSGIVING,))
    assert sched.entries[BLACK_FRIDAY].entry_bar_ns == ts_ns(BLACK_FRIDAY, 11, 44)
    assert sched.entries[BLACK_FRIDAY].exit_from_ns == ts_ns(BLACK_FRIDAY, 12, 13)
    assert _fills(run) == [] and _refusals(run) == ["engine_flatten_window"]
    out = report.entry_outcomes(run.result, sched)
    assert out["counts"] == {"engine_flatten_window": 1}


def test_every_shortened_day_of_the_store_window_has_f_at_c_minus_30() -> None:
    from rules import sessions

    for d in clock.trade_dates(date(2019, 5, 6), date(2024, 2, 29)):
        if clock.is_shortened(d):
            assert sessions.flatten_time_ct("MNQ", d) == clock.shift(clock.close_ct(d), -30), d


# ------------------------------------------------------------------ refusals ----
def test_an_entry_on_a_roll_blackout_date_is_refused_and_counted() -> None:
    run, sched = _run(_normal_pair(), [TUE], lead_in=(MON,), blackout=frozenset({TUE}))
    assert _fills(run) == [] and _refusals(run) == ["engine_roll_blackout"]
    assert report.entry_outcomes(run.result, sched)["not_traded"] == {
        TUE.isoformat(): "engine_roll_blackout"}


def test_without_a_lead_in_the_first_date_has_no_d97_reference_and_is_refused() -> None:
    bars = _normal_pair()
    run0, _ = _run(bars, [TUE], lead_in=())
    assert _refusals(run0) == ["engine_price_limit_reference_unavailable"]
    run1, _ = _run(bars, [TUE], lead_in=(MON,))
    assert _refusals(run1) == [] and len(_fills(run1)) == 2


def test_the_vehicle_blackout_is_the_price_paths_set_as_the_v2_engine_stage_builds_it() -> None:
    nq = frozenset({date(2022, 3, 9), date(2022, 3, 10), date(2022, 3, 11)})
    assert engine.vehicle_blackout(nq) == nq


# ------------------------------------------------------------------ cost to the cent ----
def test_one_round_trip_costs_the_d8_commission_plus_two_bucket_slippages() -> None:
    from screening.stage_e_frozen import leg_inputs

    run, _ = _run(_normal_pair(), [TUE], lead_in=(MON,))
    trade, = stats.trades_from(run.result, run.rules, {})
    costs = leg_inputs("MNQ", traded=True).costs
    bucket = costs.bucket_at(clock.ct_of_ns(ts_ns(TUE, 14, 30)))
    assert bucket.key == "14:30"  # both fills (14:30 and 14:59 opens) lie in the 14:30 bucket
    per_side = math.ceil(round(bucket.side_ticks["buy"] * 50, 6))
    assert trade.commission_cents == costs.commission_rt_cents == 122
    assert trade.slippage_cents == 2 * per_side == 82  # ceil(0.81742 x 50) = 41 a side
    assert trade.cost_cents == 204
    assert stats.ticks(trade.cost_cents, run.rules) == pytest.approx(4.08)


def test_run_tests_keeps_an_engine_invariant_as_that_tests_stop() -> None:
    bars = _normal_pair()
    bad = bars.copy()
    bad.loc[bad.index[5], "open"] = 15000.10  # off the 0.25 grid
    facts = signal.compute_facts(bars[["ts_event", "close", "instrument_id"]], [MON, TUE])
    scheds = {"T1": signal.t1_schedule(facts, TUE, TUE)}
    out = engine.run_tests(bad, scheds, [TUE], (MON,), frozenset(), no_releases())
    assert isinstance(out["T1"], Exception) and "grid" in str(out["T1"])
