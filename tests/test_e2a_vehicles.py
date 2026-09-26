"""Stage E.2a Task 9: the vehicle rule (D2 read as R1-R12), known answers on synthetic data."""

from __future__ import annotations

import re
from datetime import date, time, timedelta
from decimal import Decimal
from fractions import Fraction

import numpy as np
import pytest

from data.calendars import GROUP_OF_PRODUCT
from data.cme_calendar import Holiday, HolidayKind
from data.config import REPO_ROOT
from data.session import ct_ns
from screening import vehicles as v

MIN = 60 * 1_000_000_000
D1, D2, D3, D4, D5, D6 = (date(2025, 5, 12) + timedelta(days=k) for k in range(6))  # Mon-Sat


# ------------------------------------------------------------------ helpers ----
def _bars(days_minutes: dict[date, list[tuple[time, float, float]]],
          trade_date_of: dict[tuple[date, time], date] | None = None,
          instrument: dict[tuple[date, time], int] | None = None):
    """Synthetic one-minute bars: {calendar day: [(CT start, open, close), ...]}."""
    rows = []
    for day, bars in days_minutes.items():
        for at, o, c in bars:
            td = (trade_date_of or {}).get((day, at), day)
            inst = (instrument or {}).get((day, at), 7)
            rows.append((ct_ns(day, at), np.datetime64(td, "D"), o, c, inst))
    rows.sort(key=lambda r: r[0])
    return (np.array([r[0] for r in rows], dtype=np.int64),
            np.array([r[1] for r in rows], dtype="datetime64[D]"),
            np.array([r[2] for r in rows]), np.array([r[3] for r in rows]),
            np.array([r[4] for r in rows], dtype=np.int64))


def _measure(bars, *, holidays=None, blackout=(), degraded=(), tick="0.25", tv="1.25",
             o=time(8, 30), c=time(15, 0)):
    ts, td, op, cl, inst = bars
    return v.measure_risk(ts, td, op, cl, inst, open_ct=o, close_ct=c, holidays=holidays or {},
                          roll_blackout=blackout, degraded=degraded, tick=Decimal(tick),
                          tick_value_usd=Decimal(tv))


def _full_day(open_px: float, close_px: float) -> list[tuple[time, float, float]]:
    return [(time(8, 30), open_px, open_px + 1), (time(12, 0), 5000.0, 5001.0),
            (time(14, 59), close_px - 1, close_px)]


def _facts(name, rho, cost, adv=1000, q=1, cap=1):
    return v.VehicleFacts(name, q, cap, Fraction(rho), Fraction(cost), adv)


# ------------------------------------------------------------------ R1 / ticks ----
def test_d6_sessions_per_group_and_metals_subgroups():
    assert v.session_of("ZN", "rates")[1:] == (time(7, 20), time(14, 0))
    assert v.session_of("SIL", "metals") == ("silver", time(7, 20), time(12, 25))
    assert v.session_of("MHG", "metals") == ("copper", time(7, 10), time(12, 0))
    assert v.session_of("GC", "metals") == ("gold", time(7, 20), time(12, 30))
    assert v.session_of("LE", "livestock")[1:] == (time(8, 30), time(13, 0))
    assert v.session_of("MBT", "crypto")[1:] == (time(8, 30), time(15, 0))


def test_d6_table_agrees_with_every_group_calendar_module():
    from data.group_session import load_group_calendar
    from screening.vehicles_run import module_session
    for product, group in GROUP_OF_PRODUCT.items():
        if product in ("MES", "ES"):
            continue
        cal = load_group_calendar(group)
        for day in (date(2025, 4, 1), date(2026, 1, 15), date(2026, 6, 18)):
            assert module_session(cal, product, day) == v.session_of(product, group)[1:], product


@pytest.mark.parametrize(("text", "want"), [
    ("0.25", "0.25"), ("1.0", "1.0"), ("1/8 of 1/32 (0.00390625)", "0.00390625"),
    ("1/2 of 1/32 (0.015625)", "0.015625"), ("1/32 (0.03125)", "0.03125"),
    ("0.0025 (USD per bushel; quoted in cents: 1/4 cent)", "0.0025"),
    ("0.0001 (USD per pound; quoted in cents: 0.01 cent)", "0.0001"),
    ("0.00025 (USD per pound)", "0.00025"), ("5.00 (USD per bitcoin)", "5.00"),
    ("0.0000005", "0.0000005")])
def test_parse_tick_size_takes_the_leading_decimal_or_the_checked_rates_fraction(text, want):
    assert v.parse_tick_size(text) == Decimal(want)


@pytest.mark.parametrize("text", ["1/32 (0.0313)", "about a quarter", "", "1/4 cent"])
def test_parse_tick_size_refuses_what_it_cannot_read(text):
    with pytest.raises(v.VehicleRuleError):
        v.parse_tick_size(text)


def test_vendor_tick_is_100x_for_the_six_cent_quoted_products_only():
    assert v.vendor_tick("ZC", Decimal("0.0025")) == Decimal("0.25")
    assert v.vendor_tick("ZL", Decimal("0.0001")) == Decimal("0.01")
    assert v.vendor_tick("HE", Decimal("0.00025")) == Decimal("0.025")
    assert v.vendor_tick("ZM", Decimal("0.10")) == Decimal("0.10")
    assert v.vendor_tick("ZN", Decimal("0.015625")) == Decimal("0.015625")
    assert set(v.VENDOR_PRICE_FACTOR) == {"ZC", "ZW", "ZS", "ZL", "HE", "LE"}


def test_tick_scale_check_refuses_a_tick_100x_too_fine_and_a_tick_too_coarse():
    rng = np.random.default_rng(0)
    prices = 450 + 0.25 * rng.integers(-400, 400, size=5000)  # cents, 1/4-cent grid
    assert v.tick_scale_check(prices, Decimal("0.25"))["passed"]
    fine = v.tick_scale_check(prices, Decimal("0.0025"))  # the E.0 USD tick on cent prices
    assert fine["off_grid_1x"] == 0 and fine["off_grid_2x"] == 0 and not fine["passed"]
    coarse = v.tick_scale_check(prices, Decimal("0.5"))
    assert coarse["off_grid_1x"] > 0 and not coarse["passed"]


def test_to_ticks_refuses_an_off_grid_price():
    assert v.to_ticks(np.array([1.25, 1.5]), Decimal("0.25")).tolist() == [5, 6]
    with pytest.raises(v.VehicleRuleError):
        v.to_ticks(np.array([1.26]), Decimal("0.25"))


# ------------------------------------------------------------------ R2 ----
def test_calendar_exclusion_at_or_before_c_inclusive():
    halt = lambda at: Holiday(D1, "x", HolidayKind.EARLY_HALT, at, "cme", "cme")  # noqa: E731
    assert v.calendar_exclusion(halt(time(13, 30)), time(13, 30)) == "early_halt_at_or_before_C"
    assert v.calendar_exclusion(halt(time(12, 0)), time(13, 30)) == "early_halt_at_or_before_C"
    assert v.calendar_exclusion(halt(time(13, 31)), time(13, 30)) is None
    closure = Holiday(D1, "x", HolidayKind.FULL_CLOSURE, None, "cme", "n/a")
    assert v.calendar_exclusion(closure, time(13, 30)) == "full_closure"
    assert v.calendar_exclusion(None, time(13, 30)) is None


def test_r2_exclusions_roll_blackout_degraded_and_early_close():
    bars = _bars({d: _full_day(5000.0, 5000.0 + (i + 1)) for i, d in enumerate(
        (D1, D2, D3, D4, D5))})
    holidays = {D3: Holiday(D3, "halt at C", HolidayKind.EARLY_HALT, time(15, 0), "cme", "cme"),
                D4: Holiday(D4, "halt after C", HolidayKind.EARLY_HALT, time(15, 1), "cme", "cme"),
                D5: Holiday(D5, "closed", HolidayKind.FULL_CLOSURE, None, "cme", "n/a")}
    m = _measure(bars, holidays=holidays, blackout={D1, D6}, degraded={D2, date(2025, 5, 11)})
    assert m.excluded["roll_blackout"] == (D1,)
    assert m.excluded["vendor_degraded"] == (D2,)
    assert m.excluded["closure_or_early_close_at_or_before_C"] == (D3, D5)
    assert m.used == (D4,)
    assert m.sum_abs_ticks == 16 and m.r_c_usd == Fraction(20)  # 4 points = 16 ticks x $1.25


def test_r2_causes_may_overlap_and_the_date_is_dropped_once():
    bars = _bars({D1: _full_day(10.0, 11.0), D2: _full_day(10.0, 12.0)})
    m = _measure(bars, blackout={D1}, degraded={D1})
    assert m.excluded["roll_blackout"] == (D1,) and m.excluded["vendor_degraded"] == (D1,)
    assert m.used == (D2,) and m.sum_abs_ticks == 8


def test_trade_dates_outside_the_research_window_are_refused():
    bars = _bars({date(2026, 6, 22): _full_day(10.0, 11.0)})
    with pytest.raises(v.VehicleRuleError):
        _measure(bars)


# ------------------------------------------------------------------ R3 ----
def test_r3_exact_bars_on_a_liquid_day():
    bars = _bars({D1: [(time(8, 29), 1.0, 1.0), (time(8, 30), 100.0, 100.25),
                       (time(14, 59), 101.0, 102.5), (time(15, 0), 200.0, 200.0)]})
    m = _measure(bars)
    assert m.used == (D1,) and m.sum_abs_ticks == 10  # |102.5 - 100| / 0.25
    assert m.open_bar_missing == () and m.close_bar_missing == ()


def test_r3_missing_minutes_take_the_nearest_traded_minute_inside_the_window():
    bars = _bars({D1: [(time(8, 29), 1.0, 1.0), (time(8, 33), 100.0, 100.25),
                       (time(14, 55), 101.0, 101.5), (time(15, 0), 200.0, 200.0)],
                  D2: [(time(8, 30), 100.0, 100.0), (time(14, 58), 101.0, 99.0)]})
    m = _measure(bars)
    assert m.used == (D1, D2)
    assert m.sum_abs_ticks == 6 + 4
    assert m.open_bar_missing == (D1,) and m.close_bar_missing == (D1, D2)
    assert m.exact_bar_missing == (D1, D2)


def test_r3_a_single_bar_in_the_window_gives_both_prices():
    bars = _bars({D1: [(time(11, 0), 100.0, 100.75)]})
    m = _measure(bars)
    assert m.used == (D1,) and m.sum_abs_ticks == 3
    assert m.open_bar_missing == (D1,) and m.close_bar_missing == (D1,)


def test_r3_a_date_with_no_bar_in_the_window_is_excluded():
    bars = _bars({D1: [(time(7, 0), 1.0, 1.0), (time(15, 0), 2.0, 2.0)],
                  D2: _full_day(10.0, 11.0)})
    m = _measure(bars)
    assert m.excluded["no_bar_in_window"] == (D1,) and m.used == (D2,)


def test_l10_bars_of_another_trade_date_on_this_calendar_day_are_ignored():
    # a booked-forward holiday session: calendar day D1 traded, booked to trade date D2
    bars = _bars({D1: [(time(8, 30), 50.0, 50.0), (time(14, 59), 60.0, 60.0)],
                  D2: [(time(8, 30), 100.0, 100.0), (time(14, 59), 100.0, 101.0)]},
                 trade_date_of={(D1, time(8, 30)): D2, (D1, time(14, 59)): D2})
    m = _measure(bars)
    assert m.trade_dates == (D2,) and m.used == (D2,) and m.sum_abs_ticks == 4
    assert m.other_trade_date_bars_in_window == 0  # D1 is not a trade date: no window there


def test_l10_foreign_bars_inside_a_trade_dates_window_are_counted_not_used():
    bars = _bars({D1: [(time(8, 30), 50.0, 50.0), (time(9, 0), 100.0, 100.0),
                       (time(14, 59), 100.0, 101.0)]},
                 trade_date_of={(D1, time(8, 30)): D2})
    m = _measure(bars)
    assert m.used == (D1,) and m.sum_abs_ticks == 4 and m.other_trade_date_bars_in_window == 1
    assert m.open_bar_missing == (D1,)


def test_r3_refuses_a_window_spanning_two_instruments():
    bars = _bars({D1: _full_day(10.0, 11.0)}, instrument={(D1, time(14, 59)): 8})
    with pytest.raises(v.VehicleRuleError):
        _measure(bars)


def test_r4_dollars_use_the_vendor_tick_and_the_tick_value_exactly():
    # ZC-like: prices in cents on a 1/4-cent grid, tick value $12.50 per vendor tick
    bars = _bars({D1: [(time(8, 30), 450.25, 450.5), (time(13, 14), 452.0, 452.75)],
                  D2: [(time(8, 30), 452.0, 452.0), (time(13, 14), 451.0, 451.5)]})
    m = _measure(bars, tick="0.25", tv="12.5", c=time(13, 15))
    assert m.sum_abs_ticks == 10 + 2
    assert m.r_c_usd == Fraction(75)  # (10 + 2) x 12.5 / 2
    tv42 = _measure(bars, tick="0.25", tv="4.2", c=time(13, 15))
    assert tv42.r_c_usd == Fraction(Decimal("4.2")) * 6  # exact decimal tick value


# ------------------------------------------------------------------ R5 / R6 ----
@pytest.mark.parametrize(("ratio", "q"), [
    (Fraction(5, 2), 3), (Fraction(3, 2), 2), (Fraction(7, 2), 4), (Fraction(1, 2), 1),
    (Fraction(24999, 10000), 2), (Fraction(25001, 10000), 3), (Fraction(1, 5), 1)])
def test_round_half_up_at_point_five(ratio, q):
    r_c = v.R_STAR_USD / ratio
    assert v.size_contract(r_c, 10)[0] == q


def test_round_half_up_primitive():
    assert [v.round_half_up(Fraction(k, 2)) for k in range(1, 8)] == [1, 1, 2, 2, 3, 3, 4]


@pytest.mark.parametrize(("product", "cap", "source"), [
    ("SIL", 2, "D9.11"), ("MHG", 2, "D9.11"), ("MBT", 1, "D9.5"),
    ("MNQ", 10, "D9.5"), ("M2K", 10, "D9.5"), ("MYM", 10, "D9.5"), ("MCL", 10, "D9.5"),
    ("MGC", 10, "D9.5"), ("MNG", 10, "D9.5"), ("M6B", 10, "D9.5"), ("M6E", 10, "D9.5"),
    ("M6A", 10, "D9.5"), ("NQ", 1, "D9.5"), ("CL", 1, "D9.5"), ("QM", 1, "D9.5"),
    ("QG", 1, "D9.5"), ("E7", 1, "D9.5"), ("GC", 1, "D9.5"), ("RB", 1, "D9.5"),
    ("HO", 1, "D9.5"), ("ZN", 1, "D9.5"), ("6E", 1, "D9.5"), ("ZC", 1, "D9.5"),
    ("SI", 1, "D9.5"), ("HG", 1, "D9.5")])
def test_caps(product, cap, source):
    got = v.cap_for(product)
    assert (got.cap, got.source) == (cap, source)


def test_sil_lot_cap_5_is_not_reachable_and_micro_cap_10_is():
    sil = v.cap_for("SIL")
    assert sil.lot_cap_d9_5 == 5 and sil.cap == 2
    assert v.size_contract(Fraction(1), sil.cap)[0] == 2  # R*/r = 360.68 wants 361
    assert v.size_contract(Fraction(1), v.cap_for("MCL").cap)[0] == 10
    assert v.size_contract(Fraction(1), v.cap_for("NQ").cap)[0] == 1
    assert v.cap_for("SI").vol_cap_50k_d9_11 is None and "Q-1" in v.cap_for("SI").note


def test_every_admissible_contract_has_a_cap_and_every_cap_is_at_least_one():
    for x in v.EXPOSURES:
        for p in x.products:
            assert v.cap_for(p).cap >= 1


def test_size_floor_one_and_rho():
    q, rho = v.size_contract(Fraction(1000), 1)  # R*/r = 0.36 -> max(1, 0) = 1
    assert q == 1 and rho == Fraction(1000) / v.R_STAR_USD
    q, rho = v.size_contract(v.R_STAR_USD / 4, 2)  # wants 4, cap 2
    assert q == 2 and rho == Fraction(1, 2)
    with pytest.raises(v.VehicleRuleError):
        v.size_contract(Fraction(0), 1)


# ------------------------------------------------------------------ R8 ----
def test_one_side_slippage_is_minute_weighted_mean_of_the_two_sides():
    b = [v.BucketSides(8 * 60, 8 * 60 + 30, 1.0, 2.0), v.BucketSides(8 * 60 + 30, 9 * 60, 1.0, 1.0)]
    got = v.one_side_slippage_ticks(b, 8 * 60 + 10, 8 * 60 + 40)
    assert got == Fraction(20 * Fraction(3, 2) + 10 * 1, 30)


def test_one_side_slippage_refuses_gaps_and_overlaps():
    gap = [v.BucketSides(480, 500, 1.0, 1.0), v.BucketSides(501, 540, 1.0, 1.0)]
    with pytest.raises(v.VehicleRuleError):
        v.one_side_slippage_ticks(gap, 480, 540)
    overlap = [v.BucketSides(480, 520, 1.0, 1.0), v.BucketSides(510, 540, 1.0, 1.0)]
    with pytest.raises(v.VehicleRuleError):
        v.one_side_slippage_ticks(overlap, 480, 540)


def test_cost_per_dollar_of_risk():
    got = v.cost_per_dollar_of_risk(Fraction(Decimal("1.72")), Fraction(1, 2), Fraction(10))
    assert got == Fraction(Decimal("0.272"))


# ------------------------------------------------------------------ R7, R9-R11 ----
def test_rho_band_edges_are_inclusive():
    c = v.choose_vehicle("x", [_facts("A", 2, "0.5"), _facts("B", Fraction(20001, 10000), "0.1")])
    assert c.candidates == ("A",) and c.vehicle == "A" and c.status == "chosen"
    c = v.choose_vehicle("x", [_facts("A", Fraction(1, 2), "0.5"),
                               _facts("B", Fraction(4999, 10000), "0.1", q=2, cap=2)])
    assert c.preferred == ("A",) and c.vehicle == "A"


def test_m6e_and_m6a_are_never_candidates():
    c = v.choose_vehicle("EUR", [_facts("6E", 1, "0.9"), _facts("M6E", 1, "0.1"),
                                 _facts("E7", 3, "0.1")])
    assert c.excluded_by_r7 == ("M6E",) and c.candidates == ("6E",) and c.vehicle == "6E"
    c = v.choose_vehicle("AUD", [_facts("6A", 3, "0.1"), _facts("M6A", 1, "0.1")])
    assert c.status == "no candidate: not traded in Stage E" and c.excluded_by_r7 == ("M6A",)


def test_lowest_cost_among_preferred_wins_and_a_cheaper_non_preferred_does_not():
    c = v.choose_vehicle("x", [_facts("A", 1, "0.30"), _facts("B", Fraction(3, 2), "0.20"),
                               _facts("C", Fraction(2, 5), "0.01", q=10, cap=10)])
    assert c.preferred == ("A", "B") and c.vehicle == "B" and c.status == "chosen"


def test_adv_breaks_an_exact_cost_tie():
    c = v.choose_vehicle("x", [_facts("A", 1, "0.25", adv=10), _facts("B", 1, "0.25", adv=20)])
    assert c.vehicle == "B" and "higher ADV" in c.deciding


def test_silver_and_copper_prefer_the_micro_whenever_it_is_a_candidate():
    c = v.choose_vehicle("silver", [_facts("SIL", Fraction(3, 5), "0.9", q=2, cap=2),
                                    _facts("SI", 1, "0.1")])
    assert c.vehicle == "SIL" and c.status == "chosen"
    c = v.choose_vehicle("copper", [_facts("HG", 1, "0.1"),
                                    _facts("MHG", Fraction(7, 10), "0.9", q=2, cap=2)])
    assert c.vehicle == "MHG"
    c = v.choose_vehicle("silver", [_facts("SIL", 3, "0.1"), _facts("SI", 1, "0.9")])
    assert c.vehicle == "SI"  # SIL is not a candidate: the plain rule decides
    c = v.choose_vehicle("gold", [_facts("MGC", 1, "0.9", q=5, cap=10), _facts("GC", 1, "0.1")])
    assert c.vehicle == "GC"  # no preference outside silver and copper


def test_preference_switch_shows_whether_the_silver_sentence_binds():
    facts = [_facts("SIL", Fraction(3, 5), "0.9", q=2, cap=2), _facts("SI", 1, "0.1")]
    assert v.choose_vehicle("silver", facts).vehicle == "SIL"
    assert v.choose_vehicle("silver", facts, apply_preference=False).vehicle == "SI"
    single = v.choose_vehicle("copper", [_facts("MHG", Fraction(3, 5), "0.9", q=2, cap=2),
                                         _facts("HG", 3, "0.1")], apply_preference=False)
    assert single.vehicle == "MHG" and "only preferred candidate" in single.deciding


def test_preferred_micro_below_the_band_beside_a_preferred_contract_goes_to_the_lead():
    c = v.choose_vehicle("silver", [_facts("SIL", Fraction(2, 5), "0.1", q=2, cap=2),
                                    _facts("SI", 1, "0.9")])
    assert c.status == "question" and c.vehicle is None


def test_undersized_takes_the_cheapest_candidate_at_its_cap():
    c = v.choose_vehicle("x", [_facts("A", Fraction(1, 5), "0.3"),
                               _facts("B", Fraction(2, 5), "0.2", q=10, cap=10),
                               _facts("C", 3, "0.01")])
    assert c.status == "undersized" and c.vehicle == "B" and c.candidates == ("A", "B")


def test_no_candidate_when_every_rho_exceeds_two():
    c = v.choose_vehicle("Bond", [_facts("ZB", Fraction(21, 10), "0.01")])
    assert c.status == "no candidate: not traded in Stage E" and c.vehicle is None


# ------------------------------------------------------------------ R12 ----
@pytest.mark.parametrize(("q", "tv", "eps"), [
    (4, "1.00", 21), (1, "12.5", 6), (1, "5.0", 17), (2, "4.2", 10), (10, "0.5", 17),
    (1, "31.25", 2), (3, "1.25", 22)])
def test_translated_epsilon_floors(q, tv, eps):
    assert v.translated_epsilon_ticks(q, Decimal(tv)) == eps


# ------------------------------------------------------------------ D1 table ----
def test_exposure_table_matches_design_d1():
    text = (REPO_ROOT / "docs" / "STAGE_E_DESIGN.md").read_text()
    rows = re.findall(r"^\| (K\d) \| ([^|]+?) \| (\S+) ([\d,]+) \| [^|]+ \| [^|]+ \| [^|]+ \| "
                      r"IN \| ([^|]+?) \|$", text, re.MULTILINE)
    parsed = []
    for cluster, name, top, top_adv, admissible in rows:
        contracts = []
        for part in admissible.split(", "):
            m = re.fullmatch(r"(\S+)(?: \(([\d,]+)\))?", part.strip())
            sym, adv = m.group(1), m.group(2)
            contracts.append((sym, int((adv or top_adv).replace(",", ""))))
        assert contracts[0][0] == top
        parsed.append(v.Exposure(name.strip(), cluster, tuple(contracts)))
    assert tuple(parsed) == v.EXPOSURES
    assert len(v.EXPOSURES) == 31 and sum(len(x.contracts) for x in v.EXPOSURES) == 45
    assert set(v.EXPOSURE_OF_PRODUCT) == set(GROUP_OF_PRODUCT) - {"MES", "ES"}


def test_blackout_dates_helper():
    is_td = lambda d: d.weekday() < 5  # noqa: E731
    got = v.blackout_dates([date(2025, 5, 19)], is_td)  # Monday
    assert got == {date(2025, 5, 19), date(2025, 5, 16), date(2025, 5, 15)}


# ------------------------------------------------------------------ runner helpers ----
def test_bars_vendor_factor_reads_an_explicit_tick_or_the_grid_probe():
    from screening.vehicles_run import bars_vendor_factor
    probe = lambda x10, x100: {"tick": {"tick": "0.0025"},  # noqa: E731
                               "raw_checks": {"grid_scale_probe": {"x1": 0, "x10": x10,
                                                                   "x100": x100}}}
    assert bars_vendor_factor(probe(0, 0))[0] == 100
    assert bars_vendor_factor(probe(5, 9))[0] == 1
    explicit = {"tick": {"tick": "0.0025", "vendor_tick": "0.25"}, "raw_checks": {}}
    assert bars_vendor_factor(explicit) == (100, "bars.json vendor_tick")


def test_degraded_flag_check_separates_window_bars_from_a_flagged_sunday_evening():
    import pandas as pd

    from screening.vehicles_run import degraded_flag_checks
    mon = date(2026, 5, 25)
    rows = [(ct_ns(date(2026, 5, 24), time(17, 0)), mon, True),  # Sunday 22:00 UTC: flagged
            (ct_ns(mon, time(8, 30)), mon, False), (ct_ns(mon, time(14, 59)), mon, False),
            (ct_ns(D2, time(9, 0)), D2, True)]  # D2 on the list, window bar flagged
    frame = pd.DataFrame({"ts_event": [r[0] for r in rows],
                          "trade_date": [str(r[1]) for r in rows],
                          "vendor_degraded_day": [r[2] for r in rows]})
    got = degraded_flag_checks(frame, {D2}, time(8, 30), time(15, 0))
    assert got["window_bars_flag_vs_list_mismatches"] == 0
    assert got["trade_dates_off_list_with_flagged_bars_outside_window"] == ["2026-05-25"]
    bad = degraded_flag_checks(frame, set(), time(8, 30), time(15, 0))
    assert bad["window_bars_flag_vs_list_mismatches"] == 1


def test_phase2_contract_cost_known_answer_and_exposure_arithmetic():
    from types import SimpleNamespace

    from screening.vehicles_choice import contract_cost, exposure_result
    bucket = lambda k, a, b, buy, sell: SimpleNamespace(  # noqa: E731
        key=k, start_min=a, end_min=b, side_ticks={"buy": buy, "sell": sell}, fallback=False)
    model = SimpleNamespace(product="MCL", q_c=4, tick_value_usd=1.0, commission_rt_usd=1.72,
                            buckets=(bucket("07:30", 450, 480, 9.0, 9.0),
                                     bucket("08:00", 480, 510, 1.0, 2.0),
                                     bucket("08:30", 510, 840, 1.0, 1.0)))
    size = {"exposure": "WTI crude", "O_X": "08:00", "C_X": "13:30", "r_c_usd": 100.0,
            "r_c_usd_exact": "100/1", "q_c": 4, "cap_c": 10, "cap_source": "D9.5",
            "rho_c": 400 / 360.68, "rho_c_exact": str(Fraction(400) / v.R_STAR_USD),
            "tick_value_usd": "1.0"}
    row, cpd = contract_cost(size, model)
    slip = Fraction(30 * 3, 2 * 330) + Fraction(300, 330)  # (30 x 1.5 + 300 x 1) / 330
    assert Fraction(row["one_side_slippage_ticks"]) == Fraction(float(slip))
    assert cpd == (Fraction(Decimal("1.72")) + 2 * slip) / 100
    assert [b["bucket"] for b in row["day_session_buckets"]] == ["08:00", "08:30"]
    x = v.Exposure("WTI crude", "K4", (("MCL", 10),))
    got = exposure_result(x, {"MCL": row}, {"MCL": cpd})
    assert got["status"] == "chosen" and got["vehicle"] == "MCL"
    assert got["eps_X_net_ticks"] == 21  # floor(85 / (4 x $1.00))
    with pytest.raises(v.VehicleRuleError):
        contract_cost({**size, "q_c": 3}, model)
