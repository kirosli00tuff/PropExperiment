"""Known-answer tests for the Stage E rules engine per product ($50K XFA; design D9, D11.1).

Covers rules/products.py (ticks, vendor units, commissions, lot weights, caps), rules/constraints.py
(member cap, volatility caps, CPI window), rules/sessions.py (flatten times per group and date,
grain pause, livestock close, Topstep holiday schedule) and rules/price_limits.py (limit tables,
stop levels, the D9.7 entry and exit, the R-08 locked-market fill, the settlement proxy). Every
product group (equity, rates, FX, energy, metals, grains, livestock, crypto) has a known answer.
rules/xfa_rules.py is not touched; its own tests run unchanged.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from data.calendars import GROUP_OF_PRODUCT, GROUPS
from data.cme_calendar import Holiday, HolidayKind
from rules import constraints as C
from rules import price_limits as PL
from rules import products as P
from rules import sessions as S
from rules import xfa_rules as X

CT = ZoneInfo("America/Chicago")
UTC = ZoneInfo("UTC")
REPO = Path(__file__).resolve().parents[1]
D = Decimal


def ct(y: int, m: int, d: int, h: int = 0, mi: int = 0, s: int = 0) -> datetime:
    return datetime(y, m, d, h, mi, s, tzinfo=CT)


def _cal(**by_group: dict[date, Holiday]) -> dict[str, dict[date, Holiday]]:
    """Synthetic group calendars: every group empty unless given."""
    return {g: dict(by_group.get(g, {})) for g in GROUPS}


NO_LATE = {g: {} for g in GROUPS}


def _closure(day: date) -> Holiday:
    return Holiday(day, "synthetic closure", HolidayKind.FULL_CLOSURE, None, "cme", "n/a")


def _halt(day: date, at: time) -> Holiday:
    return Holiday(day, "synthetic early close", HolidayKind.EARLY_HALT, at, "cme", "cme")


# ================================================================ products ====
def test_product_table_is_the_45_admissible_contracts_plus_the_leg() -> None:
    assert len(P.ADMISSIBLE) == 45
    assert set(P.ADMISSIBLE) == set(GROUP_OF_PRODUCT) - {"ES", "MES"}
    assert {r for r, p in P.PRODUCTS.items() if not p.admissible} == {"ES", "MES"}
    for root, p in P.PRODUCTS.items():
        assert p.group == GROUP_OF_PRODUCT[root]
        assert p.tick_size * p.multiplier_usd == p.tick_value_usd, root


def _e0_tick(text: str) -> Decimal:
    """Numeric part of an E.0 tick_size string (the lead's late note: the number comes first,
    or sits in parentheses after a fraction)."""
    lead = re.match(r"^\s*(\d+(?:\.\d+)?)(?=\s|$)", text)
    if lead:
        return D(lead.group(1))
    return D(re.search(r"\((\d+(?:\.\d+)?)\)", text).group(1))


def test_ticks_equal_the_e0_liquidity_census() -> None:
    rows = json.loads((REPO / "reports/stage_e0_liquidity.json").read_text())["products"]
    seen = set()
    for row in rows:
        root = row["symbol"]
        if root not in P.PRODUCTS:
            continue  # NKD, 6M, MET, PL: OUT (D1)
        seen.add(root)
        assert P.PRODUCTS[root].tick_size == _e0_tick(str(row["tick_size"])), root
        assert P.PRODUCTS[root].tick_value_usd == D(str(row["tick_value_usd"])), root
    assert seen == set(P.PRODUCTS) - {"MES"}  # MES is not in the census: checked below


def test_mes_row_repeats_the_mes_engine_constants() -> None:
    mes = P.PRODUCTS["MES"]
    assert mes.tick_size == D(str(X.MES_TICK_SIZE))
    assert mes.tick_value_usd * 100 == X.MES_TICK_VALUE_CENTS
    assert mes.lot_weight_tenths * X.MICROS_PER_MINI == P.TENTHS_PER_LOT


def test_commissions_are_topstep_f37_plus_the_f36_increase() -> None:
    facts = json.loads((REPO / "reports/stage_e0_topstep_facts.json").read_text())["facts"]
    quote = next(f["quote"] for f in facts if f["id"] == "F3.7")
    f37 = {m.group(1): int(D(m.group(2)) * 100)
           for m in re.finditer(r"([0-9A-Z]+) \$(\d+\.\d{2})", quote)}
    for root, p in P.PRODUCTS.items():
        bump = 20 if root in ("MCL", "MNG") else 0  # F3.6: +$0.10 per side from 2026-10-01
        assert p.commission_rt_cents == f37[root] + bump, root
    assert P.PRODUCTS["MCL"].commission_rt_cents == 172
    assert P.PRODUCTS["MNG"].commission_rt_cents == 192
    assert P.commission_usd("MNQ", 3) == D("3.66")
    assert P.commission_usd("ZC", 1) == D("5.28")


def test_vendor_price_factor_matches_the_bar_builds_grid_probe() -> None:
    path = REPO / "reports/stage_e2a_bars.json"
    if not path.exists():
        pytest.skip("reports/stage_e2a_bars.json not present")
    bars = json.loads(path.read_text())["products"]
    cents = {r for r, p in P.PRODUCTS.items() if p.vendor_price_factor == 100}
    assert cents == {"ZC", "ZW", "ZS", "ZL", "HE", "LE"}
    for root in P.ADMISSIBLE:
        probe = bars[root]["raw_checks"]["grid_scale_probe"]
        if root in cents:
            assert probe["x100"] == 0, root  # every vendor price on the 100 x E.0 tick grid
        else:
            assert probe["x1"] == 0 and probe["x10"] > 0, root  # on the E.0 grid, not 10 x


@pytest.mark.parametrize(
    ("root", "p0", "p1", "ticks", "contracts", "usd"),
    [
        ("NQ", "20000.00", "20001.00", 4, 1, "20.00"),  # equity
        ("MNQ", "20000.00", "19999.25", -3, 2, "-3.00"),
        ("ZN", "111.0", "111.015625", 1, 1, "15.625"),  # rates
        ("ZT", "104.0", "104.01171875", 3, 2, "46.875"),
        ("6J", "0.0065", "0.0065005", 1, 1, "6.25"),  # FX
        ("M6B", "1.2700", "1.2701", 1, 1, "0.625"),
        ("CL", "65.00", "65.10", 10, 1, "100.00"),  # energy
        ("MNG", "3.000", "3.005", 5, 6, "30.00"),
        ("GC", "2400.0", "2400.3", 3, 1, "30.00"),  # metals
        ("SIL", "30.000", "30.010", 2, 1, "10.00"),
        ("ZC", "450.25", "451.00", 3, 1, "37.50"),  # grains, vendor cents
        ("ZL", "50.00", "50.05", 5, 1, "30.00"),
        ("ZM", "300.0", "300.5", 5, 1, "50.00"),  # grains, vendor USD per short ton
        ("HE", "90.000", "90.100", 4, 1, "40.00"),  # livestock, vendor cents
        ("LE", "220.025", "220.050", 1, 1, "10.00"),
        ("MBT", "60000", "60025", 5, 1, "2.50"),  # crypto
    ],
)
def test_tick_value_arithmetic_in_vendor_units(root, p0, p1, ticks, contracts, usd) -> None:
    assert P.ticks_between(root, p0, p1) == ticks
    assert P.pnl_usd(root, ticks, contracts) == D(usd)


def test_off_grid_price_and_bool_are_refused() -> None:
    with pytest.raises(ValueError):
        P.price_to_ticks("ZC", "450.10")  # ZC's vendor tick is 0.25 cent
    with pytest.raises(ValueError):
        P.price_to_ticks("ZC", "4.5025")  # a USD price is not on the cent grid either
    with pytest.raises(TypeError):
        P.to_decimal(True)
    assert P.from_fixed(450_250_000_000) == D("450.25")
    assert P.price_to_ticks("ZC", P.from_fixed(450_250_000_000)) == 1801


# ======================================================= lots and the cap ====
def test_lot_weights_d96_and_the_unpublished_readings() -> None:
    w = {r: P.PRODUCTS[r].lot_weight_tenths for r in P.PRODUCTS}
    assert w["NQ"] == w["ZN"] == w["6E"] == w["CL"] == w["GC"] == w["ZC"] == w["LE"] == 10
    assert w["MNQ"] == w["MCL"] == w["MGC"] == w["MHG"] == w["MNG"] == 1
    assert w["SIL"] == 2 and w["MBT"] == 10
    assert w["QM"] == w["QG"] == w["E7"] == 10  # not published: D9.6 "minis 1" (flagged)
    assert w["M6E"] == w["M6A"] == w["M6B"] == 1  # not published: D9.6 "micros 0.1" (flagged)


def test_member_cap_is_floor_one_lot_then_the_volatility_cap() -> None:
    caps = {r: P.member_cap_contracts(r) for r in P.ADMISSIBLE}
    assert caps["MNQ"] == caps["M2K"] == caps["MYM"] == caps["M6E"] == caps["MNG"] == 10
    assert caps["NQ"] == caps["ZB"] == caps["6E"] == caps["QM"] == caps["ZC"] == caps["MBT"] == 1
    assert caps["SIL"] == 2 and caps["MHG"] == 2  # D9.11 binds below floor(1 / weight)
    assert caps["MCL"] == 10 and caps["MGC"] == 10  # D9.11's 10 equals the D9.5 cap
    assert caps["SI"] == 1 and caps["HG"] == 1  # 0 only at Topstep's discretion: flag
    path = REPO / "reports/stage_e2a_vehicle_sizes.json"
    if path.exists():
        rows = json.loads(path.read_text())
        rows = rows.get("contracts") or rows.get("rows") or rows
        for root in P.ADMISSIBLE:
            if isinstance(rows.get(root), dict) and "cap_c" in rows[root]:
                assert rows[root]["cap_c"] == caps[root], root


def test_volatility_caps_are_the_50k_figures() -> None:
    assert P.VOLATILITY_CAP_50K == {"SIL": 2, "MHG": 2, "MCL": 10, "MGC": 10, "CL": 1,
                                    "QM": 1, "RB": 1, "HO": 1, "GC": 1}
    assert {"SI", "HG"} == P.MAY_BE_SUSPENDED
    assert C.check_member_size({"SIL": 3}).reason == "member_product_cap_exceeded"
    assert C.check_member_size({"MHG": -3}).reason == "member_product_cap_exceeded"
    assert C.check_member_size({"CL": 2}).reason == "member_product_cap_exceeded"


@pytest.mark.parametrize(
    ("positions", "reason"),
    [
        ({"MNQ": 10}, None),
        ({"MNQ": 11}, "member_product_cap_exceeded"),
        ({"MNQ": 5, "M2K": -5}, None),  # 1.0 lot, signs do not net
        ({"MNQ": 6, "M2K": 5}, "member_lot_equivalent_cap_exceeded"),
        ({"NQ": 1, "MNQ": 1}, "member_lot_equivalent_cap_exceeded"),
        ({"SIL": 2, "MGC": 6}, None),  # 0.4 + 0.6
        ({"SIL": 2, "MGC": 7}, "member_lot_equivalent_cap_exceeded"),
        ({"ZN": 1}, None),
        ({"ZN": 1, "ZF": -1}, "member_lot_equivalent_cap_exceeded"),
        ({"MBT": 1}, None),
        ({"MBT": 2}, "member_product_cap_exceeded"),
    ],
)
def test_member_size_check(positions, reason) -> None:
    got = C.check_member_size(positions)
    assert (got.reason if got else None) == reason


# ================================================================ CPI (D9.12) ==
CPI = datetime(2025, 7, 15, 12, 30, tzinfo=UTC)  # 07:30 CT


@pytest.mark.parametrize(
    ("root", "offset_s", "qty", "reason"),
    [
        ("NQ", -300, 1, "cpi_window_no_opening"),  # CPI - 5 min: inside, skipped for the day
        ("NQ", 300, 1, "cpi_window_no_opening"),  # CPI + 5 min: inside
        ("NQ", -301, 1, None),
        ("NQ", 301, 1, None),
        ("GC", 0, 1, "cpi_window_no_opening"),
        ("RTY", 60, 1, "cpi_window_no_opening"),
        ("MNQ", 0, 3, None),  # micros: at most 3 at the $50K size
        ("MNQ", 0, 4, "cpi_window_micro_limit"),
        ("SIL", 0, 3, None),
        ("MHG", 120, 4, "cpi_window_micro_limit"),
        ("CL", 0, 1, None),  # not a CPI-restricted product
        ("NQ", 0, 0, None),  # a closing fill is not an opening transaction
    ],
)
def test_cpi_window(root, offset_s, qty, reason) -> None:
    got = C.check_cpi_opening(root, CPI + timedelta(seconds=offset_s), qty, [CPI])
    assert (got.reason if got else None) == reason


def test_cpi_window_refuses_naive_timestamps() -> None:
    with pytest.raises(ValueError):
        C.check_cpi_opening("NQ", datetime(2025, 7, 15, 7, 30), 1, [CPI])


# ========================================================= flatten (D9.1) ====
REGULAR = _cal()
WED = date(2021, 3, 10)  # no Topstep schedule year, no calendar entry in the synthetic maps


@pytest.mark.parametrize(
    ("root", "f"),
    [("NQ", time(15, 8)), ("ZN", time(15, 8)), ("6E", time(15, 8)), ("CL", time(15, 8)),
     ("GC", time(15, 8)), ("MBT", time(15, 8)), ("ZC", time(13, 18)), ("LE", time(13, 3))],
)
def test_regular_flatten_time_per_group(root, f) -> None:
    assert S.flatten_time_ct(root, WED, REGULAR) == f
    t = datetime.combine(WED, f, tzinfo=CT)
    assert S.session_state(root, t - timedelta(minutes=1), REGULAR, NO_LATE).can_open
    state = S.session_state(root, t, REGULAR, NO_LATE)
    assert not state.can_open and state.must_be_flat


@pytest.mark.parametrize(
    ("root", "group", "halt", "f"),
    [("NQ", "equity", time(12, 15), time(12, 0)), ("ZN", "rates", time(12, 15), time(12, 0)),
     ("6E", "fx", time(12, 0), time(11, 45)), ("CL", "energy", time(13, 30), time(13, 15)),
     ("GC", "metals", time(13, 45), time(13, 30)), ("ZC", "grains", time(12, 5), time(11, 50)),
     ("LE", "livestock", time(12, 5), time(11, 50)), ("MBT", "crypto", time(12, 0), time(11, 45)),
     ("NQ", "equity", time(15, 15), time(15, 0))],
)
def test_early_close_flatten_is_the_close_minus_15(root, group, halt, f) -> None:
    cal = _cal(**{group: {WED: _halt(WED, halt)}})
    assert S.flatten_time_ct(root, WED, cal) == f
    at_f = datetime.combine(WED, f, tzinfo=CT)
    assert S.required_flatten(root, 2, at_f, cal, NO_LATE).side == "sell"
    before = at_f - timedelta(minutes=1)
    assert S.required_flatten(root, 2, before, cal, NO_LATE) is None


@pytest.mark.parametrize(
    ("root", "group"), [("NQ", "equity"), ("ZC", "grains"), ("LE", "livestock"), ("6E", "fx")])
def test_full_closure_has_no_trading(root, group) -> None:
    cal = _cal(**{group: {WED: _closure(WED)}})
    rule = S.day_rule(root, WED, cal)
    assert rule.closed and rule.flatten_ct is None
    for h in (3, 9, 12):
        assert S.session_state(root, ct(2021, 3, 10, h), cal, NO_LATE).must_be_flat
    if group != "livestock":  # the evening session of a closed trade date does not open
        evening = ct(2021, 3, 9, 20) if group != "grains" else ct(2021, 3, 9, 19, 30)
        assert S.session_state(root, evening, cal, NO_LATE).must_be_flat
        assert S.session_state(root, ct(2021, 3, 10, 20), cal, NO_LATE).can_open  # next date


def test_grain_pause_and_overnight_session() -> None:
    def st(h: int, mi: int) -> S.SessionState:
        return S.session_state("ZS", ct(2021, 3, 10, h, mi), REGULAR, NO_LATE)

    assert st(7, 42).can_open  # overnight session, before the pause exit
    assert st(7, 43).must_be_flat  # no grain position into the 07:45 pause
    assert st(8, 29).must_be_flat
    assert st(8, 30).can_open
    assert st(13, 17).can_open and st(13, 18).must_be_flat
    assert st(18, 59).must_be_flat and st(19, 0).can_open  # evening reopen 19:00 CT
    pos = S.required_flatten("ZS", -1, ct(2021, 3, 10, 7, 43), REGULAR, NO_LATE)
    assert pos is not None and pos.side == "buy" and "pause" in pos.reason


def test_livestock_close_and_no_evening_session() -> None:
    def st(h: int, mi: int) -> S.SessionState:
        return S.session_state("HE", ct(2021, 3, 10, h, mi), REGULAR, NO_LATE)

    assert st(8, 29).must_be_flat and st(8, 30).can_open
    assert st(13, 2).can_open and st(13, 3).must_be_flat
    assert st(17, 30).must_be_flat and st(23, 0).must_be_flat


def test_weekend_is_flat_from_friday_f_to_sunday_reopen() -> None:
    assert S.session_state("NQ", ct(2021, 3, 12, 15, 7), REGULAR, NO_LATE).can_open  # Friday
    assert S.session_state("NQ", ct(2021, 3, 12, 17, 30), REGULAR, NO_LATE).must_be_flat
    assert S.session_state("NQ", ct(2021, 3, 13, 12), REGULAR, NO_LATE).must_be_flat
    assert S.session_state("NQ", ct(2021, 3, 14, 16, 59), REGULAR, NO_LATE).must_be_flat
    assert S.session_state("NQ", ct(2021, 3, 14, 17, 0), REGULAR, NO_LATE).can_open


# ---- Topstep's published holiday schedule against CME's hours (brief item 6b), real calendars
@pytest.mark.parametrize(
    ("root", "day", "f"),
    [
        ("6E", date(2025, 1, 20), time(11, 30)),  # FX trades to 16:00 on MLK; Topstep 2025: 11:30
        ("NQ", date(2025, 1, 20), time(11, 30)),  # CME halt 12:00 - 15 = 11:45; Topstep 11:30
        ("6E", date(2026, 1, 19), time(11, 45)),  # Topstep 2026: 11:45
        ("NQ", date(2025, 7, 3), time(11, 45)),  # not listed by Topstep: 2025 rule, 12:15 - 30
        ("CL", date(2025, 11, 28), time(11, 45)),  # CME 13:45 close; Topstep 11:45 is earlier
        ("ZN", date(2026, 4, 3), time(8, 0)),  # Good Friday 2026: Topstep 08:00
        ("ZN", date(2025, 6, 11), time(15, 8)),  # an ordinary Wednesday
    ],
)
def test_holiday_flatten_is_the_earlier_of_topstep_and_cme(root, day, f) -> None:
    assert S.flatten_time_ct(root, day) == f


def test_topstep_markets_closed_days_and_cme_grain_closures() -> None:
    assert S.day_rule("6E", date(2025, 4, 18)).closed  # Good Friday 2025
    assert S.day_rule("ZC", date(2025, 1, 20)).closed  # MLK: grains closed by CME
    assert S.day_rule("LE", date(2025, 12, 25)).closed


def test_grain_scheduled_late_open_after_a_closure() -> None:
    # Thanksgiving 2025: no overnight grain session into 2025-11-28 (lead ruling L-6)
    assert S.session_state("ZC", ct(2025, 11, 27, 19, 30)).must_be_flat
    assert S.session_state("ZC", ct(2025, 11, 28, 8, 29)).must_be_flat
    assert S.session_state("ZC", ct(2025, 11, 28, 8, 30)).can_open
    assert S.flatten_time_ct("ZC", date(2025, 11, 28)) == time(11, 45)  # Topstep 11:45


def test_every_research_window_weekday_has_a_rule_for_every_product() -> None:
    day = date(2025, 4, 1)
    while day <= date(2026, 6, 19):
        if day.weekday() < 5:
            for root in P.ADMISSIBLE:
                rule = S.day_rule(root, day)
                assert rule.closed or rule.flatten_ct <= S.REGULAR_FLATTEN_CT[rule.group]
        day += timedelta(days=1)


# =========================================================== price limits ====
def test_limit_table_equals_the_report_json() -> None:
    data = json.loads((REPO / "reports/stage_e2a_price_limits.json").read_text())["products"]
    assert set(data) == set(PL.LIMITS)
    for root, periods in PL.LIMITS.items():
        rows = data[root]["periods"]
        assert len(rows) == len(periods), root
        for per, row in zip(periods, rows, strict=True):
            assert (per.start.isoformat(), per.end.isoformat(), per.status) == (
                row["from"], row["to"], row["status"]), root
            if per.kind is PL.LimitKind.HARD_DAILY:
                assert (str(per.amount) if per.amount is not None else None) == row["value"]
            elif per.kind is PL.LimitKind.EQUITY_BANDS:
                assert per.eth_pct == row["eth_pct"]
                assert per.rth_7pct_until.strftime("%H:%M") == row["rth_7pct_until"]
            else:
                assert (str(per.dcb_value) if per.dcb_value is not None else None) == row["variant"]


def test_limit_table_covers_the_research_window_without_pending() -> None:
    assert set(PL.LIMITS) == set(P.PRODUCTS)
    for root, periods in PL.LIMITS.items():
        for a, b in zip(periods, periods[1:], strict=False):
            assert b.start == a.end + timedelta(days=1), root  # contiguous, no overlap
        day = date(2025, 4, 1)
        while day <= date(2026, 6, 19):
            assert PL.limit_period(root, day).status in ("sourced", "bracketed", "carried")
            day += timedelta(days=7)


def test_hard_limits_exist_only_for_grains_livestock_and_equity() -> None:
    hard = {"ZC", "ZW", "ZS", "ZM", "ZL", "HE", "LE",
            "NQ", "MNQ", "RTY", "M2K", "YM", "MYM", "ES", "MES"}
    assert hard == PL.HARD_LIMIT_PRODUCTS


def test_grain_limits_reset_on_the_first_trade_dates_of_may_and_november() -> None:
    assert PL.limit_period("ZC", date(2025, 4, 30)).amount == D("0.30")
    assert PL.limit_period("ZC", date(2025, 5, 1)).amount == D("0.35")
    assert PL.limit_period("ZC", date(2025, 10, 31)).amount == D("0.35")
    assert PL.limit_period("ZC", date(2025, 11, 3)).amount == D("0.30")
    assert PL.limit_period("ZS", date(2026, 5, 1)).amount == D("0.85")
    assert PL.limit_period("LE", date(2025, 6, 2)).amount == D("0.0725")  # June reset
    assert PL.limit_period("HE", date(2025, 9, 2)).amount == D("0.0475")  # September reset


def test_pending_period_raises_only_under_the_alternative_dcb_reading() -> None:
    alt = PL.DcbReading.VARIANT_AS_LIMIT
    with pytest.raises(PL.LimitPending):
        PL.limit_period("ZN", date(2019, 6, 3))
    with pytest.raises(PL.LimitPending):
        PL.limit_band("ZN", date(2019, 6, 3), ct(2019, 6, 3, 9), "125.0", alt)
    band = PL.limit_band("ZN", date(2019, 6, 3), ct(2019, 6, 3, 9), "125.0")  # default
    assert band.up is None and band.down is None


def test_percentage_limit_stop_levels_topstep_es_example() -> None:
    # Topstep's own example: ES settlement 2,814.00 in May 2020 (5% overnight, 7% down in RTH)
    s = "2814.00"
    eth = PL.stop_levels(PL.limit_band("MES", date(2020, 5, 14), ct(2020, 5, 13, 20), s), s)
    assert eth.upper == D("2898.4200") and eth.lower == D("2729.5800")  # "2,898" / "2,730"
    rth = PL.stop_levels(PL.limit_band("MES", date(2020, 5, 14), ct(2020, 5, 14, 9), s), s)
    assert rth.upper is None and rth.lower == D("2673.3000")  # "2,673"


def test_equity_bands_by_time_of_day_in_the_research_window() -> None:
    s, day = D("20000"), date(2025, 6, 11)
    def band(h: int, mi: int = 0) -> PL.Band:
        return PL.limit_band("NQ", day, ct(2025, 6, 11, h, mi), s)
    assert (band(2).up, band(2).down) == (D("0.07"), D("0.07"))  # overnight: 7% up and down
    assert (band(8, 30).up, band(8, 30).down) == (None, D("0.07"))
    assert (band(14, 25).up, band(14, 25).down) == (None, D("0.20"))
    assert (band(15, 0).up, band(15, 0).down) == (D("0.07"), D("0.07"))
    levels = PL.stop_levels(band(2), s)
    assert (levels.upper, levels.lower) == (D("21000.00"), D("19000.00"))


def test_price_unit_limit_stop_levels_grains_and_livestock() -> None:
    # ZC on 2025-06-02: limit $0.35 = 35 cents in vendor units; S = 440.00 cents
    band = PL.limit_band("ZC", date(2025, 6, 2), ct(2025, 6, 2, 9), "440.00")
    assert band.up == band.down == D(35) / D(440)
    lv = PL.stop_levels(band, "440.00")
    assert lv.upper == D("466.20") and lv.lower == D("413.80")  # 440 +/- (35 - 8.80)
    up, down = PL.limit_prices(band, "440.00")
    assert (up, down) == (D("475.00"), D("405.00"))
    # LE on 2025-06-02: $0.0725 = 7.25 cents; S = 220.00 cents
    le = PL.stop_levels(PL.limit_band("LE", date(2025, 6, 2), ct(2025, 6, 2, 9), "220"), "220")
    assert le.upper == D("222.8500") and le.lower == D("217.1500")
    # ZM is quoted in USD per short ton (factor 1): $20 on S = 300.0
    zm = PL.stop_levels(PL.limit_band("ZM", date(2025, 6, 2), ct(2025, 6, 2, 9), "300"), "300")
    assert zm.upper == D("314.00") and zm.lower == D("286.00")


def test_entry_refused_and_exit_forced_beyond_a_stop_level() -> None:
    day, t, s = date(2025, 6, 2), ct(2025, 6, 2, 10), "440.00"
    assert PL.check_price_limit_entry("ZC", day, t, s, "466.00") is None
    refusal = PL.check_price_limit_entry("ZC", day, t, s, "466.25")
    assert refusal is not None and refusal.reason == "price_limit_zone_no_entry"
    assert PL.check_price_limit_entry("ZC", day, t, s, "413.75") is not None
    assert PL.check_price_limit_entry("ZC", day, t, s, "413.80") is not None  # touching counts
    assert PL.check_price_limit_entry("ZC", day, t, s, "466.20") is not None  # on both sides
    assert PL.required_price_limit_exit("ZC", day, t, 1, s, "440.00") is None
    ex = PL.required_price_limit_exit("ZC", day, t, 1, s, "413.00")
    assert ex is not None and ex.side == "sell" and ex.quantity == 1
    assert ex.fill == "next_bar_open" and ex.fill_guard_exempt and ex.cost == "event_window"
    assert PL.required_price_limit_exit("ZC", day, t, 0, s, "413.00") is None


DCB_ROOTS = ("ZT", "ZF", "ZN", "TN", "ZB", "UB", "6E", "M6E", "E7", "6A", "M6A", "6B", "M6B",
             "6C", "6J", "6S", "6N", "CL", "MCL", "QM", "NG", "MNG", "QG", "RB", "HO", "GC", "MGC",
             "SI", "SIL", "HG", "MHG", "MBT")


def test_default_dcb_reading_is_no_lock_limit_ruling_l13() -> None:
    assert PL.DCB_READING_DEFAULT is PL.DcbReading.NO_LOCK_LIMIT
    assert {r for r, ps in PL.LIMITS.items() if ps[0].kind is PL.LimitKind.DCB_ONLY} == set(
        DCB_ROOTS)
    day, t = date(2025, 6, 2), ct(2025, 6, 2, 10)
    for root in DCB_ROOTS:
        band = PL.limit_band(root, day, t, "100")
        assert band.up is None and band.down is None, root
        levels = PL.stop_levels(band, "100")
        assert levels.upper is None and levels.lower is None
        assert PL.limit_prices(band, "100") == (None, None)
        # no entry refusal and no forced exit, however far the price has moved
        assert PL.check_price_limit_entry(root, day, t, "100", "150") is None
        assert PL.required_price_limit_exit(root, day, t, 1, "100", "50") is None
    # ZT, ZF, ZN: tradable at the settlement under the default reading
    for root in ("ZT", "ZF", "ZN"):
        assert PL.check_price_limit_entry(root, day, t, "111.0", "111.0") is None


def test_default_leaves_the_hard_limit_products_unchanged() -> None:
    day, t = date(2025, 6, 2), ct(2025, 6, 2, 10)
    for reading in PL.DcbReading:
        zc = PL.stop_levels(PL.limit_band("ZC", day, t, "440.00", reading), "440.00")
        assert (zc.upper, zc.lower) == (D("466.20"), D("413.80"))
        nq = PL.stop_levels(PL.limit_band("NQ", day, ct(2025, 6, 11, 2), "20000", reading),
                            "20000")
        assert (nq.upper, nq.lower) == (D("21000.00"), D("19000.00"))
        assert PL.check_price_limit_entry("LE", day, t, "220", "222.85", reading) is not None


def test_dcb_products_under_the_alternative_reading() -> None:
    alt = PL.DcbReading.VARIANT_AS_LIMIT
    day, t = date(2025, 6, 2), ct(2025, 6, 2, 10)
    # CL (energy): variant 10% of the prior settlement
    cl = PL.limit_band("CL", day, t, "65.00", alt)
    assert cl.up == D("0.10") and cl.kind is PL.LimitKind.DCB_ONLY
    lv = PL.stop_levels(cl, "65.00")
    assert (lv.upper, lv.lower) == (D("70.2000"), D("59.8000"))
    assert PL.limit_prices(cl, "65.00") == (D("71.5000"), D("58.5000"))
    ex = PL.required_price_limit_exit("CL", day, t, -2, "65.00", "70.20", alt)
    assert ex is not None and ex.side == "buy" and ex.quantity == 2
    # 6E (FX) 4%, GC (metals) 10%, MBT (crypto) 10%
    assert PL.limit_band("6E", day, t, "1.10", alt).up == D("0.04")
    assert PL.limit_band("GC", day, t, "3300", alt).up == D("0.10")
    assert PL.limit_band("MBT", day, t, "100000", alt).up == D("0.10")
    # ZN (rates): 2.00 points on 111.0 is 1.8% < 2%: no tradable band under this reading
    zn = PL.stop_levels(PL.limit_band("ZN", day, t, "111.0", alt), "111.0")
    assert zn.upper < D("111.0") < zn.lower
    assert PL.check_price_limit_entry("ZN", day, t, "111.0", "111.0", alt) is not None
    # UB: 8 points on 115 is 6.96%, a band of +/- 4.96%
    ub = PL.stop_levels(PL.limit_band("UB", day, t, "115", alt), "115")
    assert (ub.upper, ub.lower) == (D("120.70"), D("109.30"))


def test_locked_market_exit_waits_for_a_bar_trading_through_the_limit() -> None:
    up, lim = D("475.00"), D("405.00")  # ZC limit prices around S = 440.00 cents
    locked = PL.Bar(lim, lim, lim, lim)
    through = PL.Bar(lim, D("406.50"), lim, D("406.00"))
    fill = PL.locked_exit_fill("sell", up, lim, [locked, locked, through])
    assert (fill.index, fill.price, fill.flagged, fill.bars_waited) == (2, lim, True, 2)
    # not locked at all: fills at the first bar's open, no flag
    free = PL.Bar(D("410.00"), D("411.00"), D("409.00"), D("410.50"))
    assert PL.locked_exit_fill("sell", up, lim, [free]) == PL.LockedFill(0, D("410.00"), False, 0)
    # still locked at the end of the bars given: no fill yet, flagged
    assert PL.locked_exit_fill("sell", up, lim, [locked, locked]) == PL.LockedFill(
        None, None, True, 2)
    # a short exits (buys) against limit-up
    lu = PL.Bar(up, up, up, up)
    back = PL.Bar(up, up, D("474.00"), D("474.25"))
    assert PL.locked_exit_fill("buy", up, lim, [lu, back]).index == 1
    # a buy is not blocked by a limit-down lock; a side with no limit cannot lock
    assert PL.locked_exit_fill("buy", up, lim, [locked]).index == 0
    assert PL.locked_exit_fill("sell", None, None, [locked]).index == 0
    # equity RTH has no upside limit: a short's buy exit never waits on a lock
    band = PL.limit_band("NQ", date(2025, 6, 11), ct(2025, 6, 11, 10), "20000")
    lim_up, lim_down = PL.limit_prices(band, "20000")
    assert lim_up is None and lim_down == D("18600.00")
    top = PL.Bar(D("20100"), D("20100"), D("20100"), D("20100"))
    assert PL.locked_exit_fill("buy", lim_up, lim_down, [top]).index == 0
    # tolerance for a proxy settlement off CME's by a tick
    near = PL.Bar(D("405.25"), D("405.25"), D("405.25"), D("405.25"))
    assert PL.locked_exit_fill("sell", up, lim, [near]).index == 0
    assert PL.locked_exit_fill("sell", up, lim, [near, through], tolerance="0.25").index == 1


# ---- settlement windows and the proxy
@pytest.mark.parametrize(
    ("root", "start", "end"),
    [("NQ", time(14, 59, 30), time(15, 0)), ("ZN", time(13, 59, 30), time(14, 0)),
     ("6E", time(13, 59, 30), time(14, 0)), ("CL", time(13, 28), time(13, 30)),
     ("GC", time(12, 29), time(12, 30)), ("SI", time(12, 24), time(12, 25)),
     ("HG", time(11, 59), time(12, 0)), ("ZC", time(13, 14), time(13, 15)),
     ("LE", time(12, 59, 30), time(13, 0)), ("MBT", time(14, 59), time(15, 0))],
)
def test_regular_settlement_windows(root, start, end) -> None:
    w = PL.settlement_window_ct(root, WED, REGULAR)
    assert (w.start_ct, w.end_ct) == (start, end)


def test_settlement_window_ends_at_d6_c_for_every_product() -> None:
    import importlib

    for root, p in P.PRODUCTS.items():
        mod = importlib.import_module(f"data.calendars.{p.group}")
        spec = mod.SESSIONS[-1]
        key = root if root in spec.day_session_ct else (
            p.subgroup if p.subgroup in spec.day_session_ct else p.group)
        c = spec.day_session_ct[key][1]
        assert PL.settlement_window_ct(root, WED, REGULAR).end_ct == c, root


def test_early_settlement_and_early_halt_windows() -> None:
    w = PL.settlement_window_ct("ZN", date(2025, 12, 24))  # rates EARLY_SETTLEMENT_CT 12:00
    assert (w.start_ct, w.end_ct) == (time(11, 59, 30), time(12, 0))
    cal = _cal(grains={WED: _halt(WED, time(12, 5))})
    w = PL.settlement_window_ct("ZC", WED, cal)
    assert (w.start_ct, w.end_ct) == (time(12, 4), time(12, 5))
    with pytest.raises(ValueError):
        PL.settlement_window_ct("ZC", WED, _cal(grains={WED: _closure(WED)}))
    lo, hi = PL.settlement_window_utc("ZC", date(2025, 6, 2))
    assert (lo, hi) == (datetime(2025, 6, 2, 18, 14, tzinfo=UTC),
                        datetime(2025, 6, 2, 18, 15, tzinfo=UTC))


def test_settlement_proxy_is_the_volume_weighted_close() -> None:
    lo, hi = datetime(2025, 6, 2, 18, 28, tzinfo=UTC), datetime(2025, 6, 2, 18, 30, tzinfo=UTC)
    bars = [PL.BarPrint(datetime(2025, 6, 2, 18, 27, tzinfo=UTC), "64.00", 500),
            PL.BarPrint(datetime(2025, 6, 2, 18, 28, tzinfo=UTC), "65.00", 100),
            PL.BarPrint(datetime(2025, 6, 2, 18, 29, tzinfo=UTC), "65.30", 200),
            PL.BarPrint(datetime(2025, 6, 2, 18, 30, tzinfo=UTC), "70.00", 900)]
    got = PL.settlement_proxy(bars, lo, hi)
    assert got == PL.SettlementProxy(D("65.20"), "vwap_close", 2)
    # a 30-second window takes the bar of its minute
    got = PL.settlement_proxy(bars, lo + timedelta(seconds=90), hi)
    assert got.value == D("65.30") and got.bars_used == 1
    # no volume in the window: last close before the window end (flagged method)
    quiet = [PL.BarPrint(datetime(2025, 6, 2, 18, 27, tzinfo=UTC), "64.00", 500),
             PL.BarPrint(datetime(2025, 6, 2, 18, 28, tzinfo=UTC), "64.50", 0)]
    got = PL.settlement_proxy(quiet, lo, hi)
    assert got == PL.SettlementProxy(D("64.50"), "last_close_before_window_end", 0)
    assert PL.settlement_proxy([], lo, hi) is None


# ============================================================ MES neutrality ==
def test_mes_engine_constants_unchanged() -> None:
    assert time(15, 10) == X.FLATTEN_TIME_CT
    assert timedelta(minutes=2) == X.NO_NEW_POSITIONS_LEAD
    assert timedelta(minutes=15) == X.HOLIDAY_FLATTEN_LEAD
    assert X.flatten_time_ct(time(12, 0)) == time(11, 45)
    assert X.max_position_micros(X.Phase.XFA, 0) == 20
