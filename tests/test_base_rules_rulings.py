"""The lead's rulings of 2026-10-09: R-B1 (the settlement minute at a scheduled closure), R-B2 (an
uncalibrated D8 bucket), R-B3 (no data condition raises during a run; input problems are found
before the marker), R-B4 (the fixed registry label). Synthetic data only."""

from __future__ import annotations

import json
import math
from collections import Counter
from datetime import UTC, date, datetime
from fractions import Fraction

import pytest

from base_rules import constants as K
from base_rules.common import entry_point, load_or_exclude, settle_point
from base_rules.costs import vehicle_cost
from base_rules.counts import entry_why, settle_ok
from base_rules.h2 import _leg
from base_rules.intraday import candidate, product_units
from base_rules.sim import simulate
from base_rules.store import StoreRefused
from data.config import REPO_ROOT
from tests._base_rules_fixtures import (
    calendars,
    context,
    hist_payload,
    make_bars,
    ns,
    settlement,
)

D0, D1, D2 = date(2016, 3, 7), date(2016, 3, 8), date(2016, 3, 9)


def _seg(a: int, start: str, b: int, end: str) -> dict:
    return {"start_offset_days": a, "start_ct": start, "end_offset_days": b, "end_ct": end}


HALT_1515 = [_seg(-1, "17:00", 0, "15:15"), _seg(0, "15:30", 0, "16:15")]
HALT_2010 = [_seg(-1, "15:30", -1, "16:30"), _seg(-1, "17:00", 0, "15:15")]
GRAINS_1315 = [_seg(-1, "18:00", 0, "07:15"), _seg(0, "09:30", 0, "13:15")]


def _st(**minutes: tuple[str, str]):  # noqa: ANN202
    settle = {p: [{"from": str(K.PROMPT_FIRST), "to": str(K.WINDOW_LAST), "minute_ct": s,
                   "grade": "primary", "lead_grade": "primary"}] for p, (s, _o) in minutes.items()}
    opens = {p: [{"from": str(K.PROMPT_FIRST), "to": str(K.WINDOW_LAST), "minute_ct": o}]
             for p, (_s, o) in minutes.items()}
    return settlement(overrides=settle, opens=opens)


def _equity_ctx(segments, bars):  # noqa: ANN001, ANN202
    cals = calendars(("equity", "rates"), {"equity": hist_payload("equity", segments=segments)})
    return context(cals, bars, st=_st(NQ=("15:15", "08:30")),
                   starts={p: date(2016, 1, 1) for p in K.PRODUCTS})


def _nq_rows() -> list[tuple]:
    rows = []
    for k, d in enumerate((D0, D1, D2)):
        base = 1000 + 10 * k
        rows += [(d, 14 * 60 + 44, base, base + 5, "A"), (d, 14 * 60 + 45, base + 5, base + 6, "A"),
                 (d, 15 * 60 + 14, base + 6, base + 9, "A"),
                 (d, 15 * 60 + 15, 99999, 99999, "A", False),  # the closure-flagged print
                 (d, 15 * 60 + 30, base + 7, base + 8, "A")]
    return rows


# ------------------------------------------------------------------ R-B1 ----
def test_h1_exit_at_an_equity_1515_closure_is_the_close_of_bar_s_minus_1() -> None:
    bars = make_bars("NQ", _nq_rows())
    ctx = _equity_ctx(HALT_1515, {"NQ": bars})
    assert ctx.closure_at("NQ", D1, 15 * 60 + 15) and not ctx.closure_at("NQ", D1, 15 * 60)
    assert ctx.reopen_ns("NQ", D1, 15 * 60 + 15) == ns(D1, 15 * 60 + 30)
    why, cand = candidate("H1", ctx, bars, "NQ", D1)
    assert why is None
    direction, p_in, p_out, info = cand
    assert p_out == (bars.bar(D1, 15 * 60 + 14), True) and info["exit_at_close"]
    assert p_in == (bars.bar(D1, 14 * 60 + 45), False)
    res = simulate(bars, vehicle_cost("NQ"), ctx.releases, [(p_in, direction), (p_out, 0)])
    assert [f.price_ticks for f in res.fills] == [1015, 1019]  # never the 99999 closure print
    assert res.fills[1].at_close and res.fills[1].ts_ns == ns(D1, 15 * 60 + 14)
    assert res.gross_cents == direction * 4 * 50


def test_h4_reference_move_uses_h1_s_exit_price_under_the_closure() -> None:
    bars = make_bars("NQ", _nq_rows() + [(D2, 8 * 60 + 31, 1030, 1030, "A")])
    ctx = _equity_ctx(HALT_1515, {"NQ": bars})
    why, cand = candidate("H4", ctx, bars, "NQ", D2)
    assert why is None
    # m on D1 = close of 15:14 (1019) - open of 14:45 (1015) > 0: H4 goes short
    assert cand[0] == -1 and cand[3]["ref_exit_at_close"]


def test_h2_entry_after_the_halt_exit_and_marks_at_the_close_and_no_entry_bar() -> None:
    nq = make_bars("NQ", _nq_rows())
    zn = make_bars("ZN", [(d, m, 500 + k, 500 + k, "Z") for k, d in enumerate((D0, D1, D2))
                          for m in (13 * 60 + 59, 14 * 60, 15 * 60 + 15)])
    ctx = _equity_ctx(HALT_1515, {"NQ": nq, "ZN": zn})
    why, leg = _leg(ctx, nq, "NQ", D0, D1, D2, 15 * 60 + 15)
    assert why is None
    assert leg["p_in"] == (nq.bar(D1, 15 * 60 + 30), False)  # the first bar after the halt
    assert leg["p_out"] == (nq.bar(D2, 15 * 60 + 14), True)
    assert leg["marks"] == [(nq.bar(D1, 15 * 60 + 14), True), (nq.bar(D2, 15 * 60 + 14), True)]
    why, zleg = _leg(ctx, zn, "ZN", D0, D1, D2, 15 * 60 + 15)
    assert why is None and zleg["p_in"] == (zn.bar(D1, 15 * 60 + 15), False)
    res = simulate(nq, vehicle_cost("NQ"), ctx.releases, [(leg["p_in"], 1), (leg["p_out"], 0)],
                   leg["marks"])
    assert res.gross_cents == (1029 - 1017) * 50  # entry 15:30 open D1, exit 15:14 close D2
    assert res.daily["base"][D1] == -res.fills[0].costs["base"]  # D1's mark precedes the entry
    early = _equity_ctx(HALT_2010, {"NQ": nq, "ZN": zn})  # after 15:15 the session is D+1's
    assert _leg(early, nq, "NQ", D0, D1, D2, 15 * 60 + 15)[0] == "no entry bar"
    assert entry_point(early, nq, "NQ", D1, 15 * 60 + 15) == (None, "no entry bar")


def test_a_grains_session_close_at_s_exits_at_the_close_of_s_minus_1() -> None:
    cals = calendars(("grains",), {"grains": hist_payload(
        "grains", segments=GRAINS_1315, day_session={p: ("09:30", "13:15") for p in
                                                     ("ZC", "ZW", "ZS", "ZM", "ZL")})})
    rows = [(d, m, 700 + k, 701 + k, "C") for k, d in enumerate((D0, D1))
            for m in (12 * 60 + 44, 12 * 60 + 45, 13 * 60 + 14)]
    bars = make_bars("ZC", rows)
    ctx = context(cals, {"ZC": bars}, st=_st(ZC=("13:15", "09:30")),
                  starts={p: date(2016, 1, 1) for p in K.PRODUCTS})
    assert ctx.closure_at("ZC", D1, 13 * 60 + 15)
    assert settle_point(ctx, bars, "ZC", D1) == (bars.bar(D1, 13 * 60 + 14), True)
    why, cand = candidate("H1", ctx, bars, "ZC", D1)
    assert why is None and cand[2][1]
    assert settle_ok(ctx, "ZC", D1)  # the calendar-only counts follow R-B1 too
    assert entry_why(ctx, "ZC", D1, 13 * 60 + 15) == "no entry bar"


def test_inside_an_open_interval_nothing_changes() -> None:
    bars = make_bars("ZN", [(D1, 14 * 60, 1, 1, "Z")])
    ctx = context(calendars(("rates",)), {"ZN": bars})
    assert not ctx.closure_at("ZN", D1, 14 * 60)
    assert settle_point(ctx, bars, "ZN", D1) == (0, False)


# ------------------------------------------------------------------ R-B2 ----
def test_an_uncalibrated_bucket_pays_the_largest_per_side_slippage() -> None:
    raw = json.loads((REPO_ROOT / "reports" / "stage_e2a_costs.json").read_text())["products"]
    le = raw["LE"]
    worst = max(float(b["side_ticks"]["buy"]) for b in le["buckets"])
    tv = Fraction(str(le["tick_value_usd"])) * 100
    comm = int(Fraction(str(le["commission_rt_usd"])) * 100) // 2
    ts = ns(date(2015, 3, 3), 8 * 60 + 1)  # LE's O_p 08:00: H4 enters at 08:01
    costs, uncal = vehicle_cost("LE").fill_costs(ts, "buy", False)
    assert uncal
    assert costs["base"] == comm + math.ceil(round(worst * float(tv), 6))
    assert costs["stress"] == costs["base"] + tv
    assert costs["slip150"] == comm + math.ceil(round(worst * 1.5 * float(tv), 6))
    ok_costs, ok_uncal = vehicle_cost("LE").fill_costs(ns(date(2015, 3, 3), 9 * 60), "buy", False)
    assert not ok_uncal and ok_costs["base"] <= costs["base"]


def test_a_unit_with_an_uncalibrated_fill_is_kept_and_counted() -> None:
    cals = calendars(("livestock",), {"livestock": hist_payload("livestock")})
    rows = []
    for k, d in enumerate((D0, D1)):
        rows += [(d, m, 900 + k * 3 + j, 900 + k * 3 + j, "L")
                 for j, m in enumerate((8 * 60 + 1, 12 * 60 + 29, 12 * 60 + 30, 13 * 60))]
    bars = make_bars("LE", rows)
    ctx = context(cals, {"LE": bars}, st=_st(LE=("13:00", "08:00")),
                  starts={p: date(2016, 1, 1) for p in K.PRODUCTS})
    c: Counter = Counter()
    units = product_units("H4", ctx, "LE", bars, c, set())
    assert len(units) == 1 and c["uncalibrated bucket"] == 1 and units[0].sim.uncalibrated


# ------------------------------------------------------------------ R-B3 ----
def test_a_contract_change_on_a_tradeable_date_is_excluded_not_raised() -> None:
    rows = [(d, m, 1000, 1000 + (d == D1) * 4, "A" if d == D0 else "B")
            for d in (D0, D1) for m in (14 * 60 + 44, 14 * 60 + 45, 15 * 60 + 14)]
    bars = make_bars("NQ", rows)
    ctx = _equity_ctx(HALT_1515, {"NQ": bars})
    assert candidate("H1", ctx, bars, "NQ", D1) == ("contract change", None)


def test_a_store_refused_after_its_rows_are_read_excludes_the_product() -> None:
    def load(p: str):  # noqa: ANN202
        raise StoreRefused("a row booked to 2024-03-01")

    ctx = context(calendars(("rates",)), {})
    ctx.load_bars = load
    c: Counter = Counter()
    notes: dict = {}
    assert load_or_exclude(ctx, "ZN", c, notes) is None
    assert c["store refused"] == 1 and "2024-03-01" in notes["store_refused"]["ZN"]


# ------------------------------------------------------------------ R-B4 ----
def test_the_registry_label_is_fixed() -> None:
    assert K.REGISTRY_TEST == "E16"
    assert dict(K.TEST_IDS) == {t: f"E16-{t}" for t in K.TESTS}


def test_a_unit_that_does_not_end_flat_is_a_code_error_and_raises() -> None:
    splice = int(datetime(2016, 3, 9, tzinfo=UTC).timestamp()) * 10**9
    bars = make_bars("NQ", _nq_rows(), splices=[(splice, D2)])
    with pytest.raises(ValueError):
        simulate(bars, vehicle_cost("NQ"), _equity_ctx(HALT_1515, {"NQ": bars}).releases,
                 [((0, True), 1)])


def test_h2_counts_entries_after_the_closure() -> None:  # F-09
    from base_rules.h2 import run_h2
    from tests._base_rules_fixtures import trade_dates

    probe = _equity_ctx(HALT_1515, {})
    days = trade_dates(probe.cal("NQ"), date(2016, 1, 4), date(2016, 6, 30))
    nq = make_bars("NQ", [(d, m, 1000 + k, 1000 + k, "A") for k, d in enumerate(days)
                          for m in (15 * 60 + 14, 15 * 60 + 30)])
    zn = make_bars("ZN", [(d, m, 500 + k % 7, 500 + k % 7, "Z") for k, d in enumerate(days)
                          for m in (13 * 60 + 59, 14 * 60, 15 * 60 + 15)])
    out = run_h2(_equity_ctx(HALT_1515, {"NQ": nq, "ZN": zn}))
    assert out.counters["eligible"] >= 4
    assert out.counters["entry after closure"] == out.counters["eligible"]
