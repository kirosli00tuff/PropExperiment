"""Stage E.8 K6-crushgap-01 of MemberCoder-A (reports/stage_e8_member_specs.md section 4;
readings K6-L-03, K6-L-04, K6-L-05, K6-L-10; S0.1, S0.8, S0.9, S0.12).

Synthetic bars only, built with tests/test_k6_members_ports.py's kit (one frame per leg: ZS
traded, ZM and ZL signal legs) and run through the real Stage E engine, plus direct calls where
the calendar never produces the case. No bar file is read. The GRAIN_TRADE_DATES and
GRAIN_FULL_SESSIONS tables are coder B's (strategy/members/k6/_calendar.py, pinned by
tests/test_k6_members_tables.py); this file checks the members of them it relies on.

Prices at the base: ZS 1050.00 cents/bu (4200 ticks of 0.25), ZM 300.0 USD/short ton (3000 ticks
of 0.10), ZL 50.00 cents/lb (5000 ticks of 0.01). GPM = 0.022 x 300 + 11 x 0.50 - 10.50 =
1.60 USD/bu = 16000 units of 0.0001; a gap of a, b, c ticks on ZM, ZL, ZS moves G by
22 a + 11 b - 25 c units, and the filter is 200 units (0.02 USD/bu).
"""

from __future__ import annotations

import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, time, timedelta
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType
from typing import Any

import pytest

from data.group_session import load_group_calendar, previous_trade_date
from rules.products import product
from rules.xfa_rules import Phase, Status
from screening.stage_e_engine import EngineResult, Fill, IntentRecord, run_engine
from screening.stage_e_freeze import (
    MemberDecl,
    check_cluster_sources,
    check_member_source,
    load_cluster_freeze,
    verify_cluster_code,
    write_cluster_freeze,
)
from strategy.interface import Bar
from strategy.members.k6 import crushgap
from strategy.members.k6._calendar import GRAIN_FULL_SESSIONS, GRAIN_TRADE_DATES
from strategy.members.k6.crushgap import FILTER_UNITS, CrushGap, gpm_units_per_tick
from strategy.stage_e.interface import (
    LegSpec,
    MemberAccountView,
    MinuteView,
    StageEMember,
    TradingInterval,
    leg_market_intent,
)
from tests._stage_e_canary_kit import rules_for
from tests.test_k6_members_ports import (
    BASE_PRICE,
    FRI,
    FRI_MD,
    HALT_TG,
    HALT_XMAS,
    K6_DIR,
    MON,
    MON_TG,
    REPO,
    TUE,
    TUE_MD,
    TUE_XMAS,
    WED,
    WED_TG,
    Day,
    Ticks,
    bar_at,
    base_ticks,
    ct,
    fills,
    frame,
    hm,
    intents,
    ns_at,
    trade,
    with_references,
)

LEGS = ("ZS", "ZM", "ZL")
TICK_1314, BAR_0830 = hm(13, 14), hm(8, 30)


def mk() -> CrushGap:
    return crushgap.make_zs()


Gaps = Mapping[str, int]  # root -> ticks


def legs_days(prev: date, day: date, closes: Gaps | None = None, opens: Gaps | None = None,
              **per_leg: Mapping[str, Any]) -> dict[str, list[Day]]:
    """Per leg: a full day ``prev`` whose 13:14 close is base + closes[r] ticks and a full day
    ``day`` whose 08:30 open is base + opens[r] ticks (the rest flat at the base).
    ``per_leg[r]`` adds keyword arguments to leg r's ``day`` (skip, ids, ...); ``prev_<r>`` to
    its ``prev``."""
    closes, opens = closes or {}, opens or {}
    out: dict[str, list[Day]] = {}
    for r in LEGS:
        c, o = closes.get(r, 0), opens.get(r, 0)
        prev_kw = dict(per_leg.get(f"prev_{r}", {}))
        day_kw = dict(per_leg.get(r, {}))
        prev_paths: dict[int, Ticks] = {TICK_1314: (0, max(c, 0), min(c, 0), c)}
        day_paths: dict[int, Ticks] = {BAR_0830: (o, max(o, 0), min(o, 0), 0)}
        prev_paths.update(prev_kw.pop("paths", {}))
        day_paths.update(day_kw.pop("paths", {}))
        out[r] = [Day(prev, paths=prev_paths, **prev_kw), Day(day, paths=day_paths, **day_kw)]
    return out


def run_legs(member: Any, days: Mapping[str, Sequence[Day]], window: Sequence[date] | None = None
             ) -> EngineResult:
    dates = sorted({d.trade_date for d in days["ZS"]}) if window is None else list(window)
    frames = {r: frame(with_references(days[r], "grains"), r) for r in LEGS}
    return run_engine(frames, member, member.legs, rules_for(member.legs, dates))


def fill_roots(res: EngineResult) -> set[str]:
    return {f.root for f in res.events(Fill)}


def intent_roots(res: EngineResult) -> set[str | None]:
    return {r.root for r in res.events(IntentRecord)}


def g_units(gaps: Gaps) -> int:
    """22 a + 11 b - 25 c for open-minus-close gaps a (ZM), b (ZL), c (ZS) in ticks."""
    return sum(gpm_units_per_tick(r) * gaps.get(r, 0) for r in LEGS)


def gap_case(gaps: Gaps, prev: date = MON, day: date = TUE, **kw: Any) -> EngineResult:
    return run_legs(mk(), legs_days(prev, day, opens=gaps, **kw))


TRADE_BUY = trade(TUE, "08:31", "13:14", "buy")
TRADE_SELL = trade(TUE, "08:31", "13:14", "sell")


# ------------------------------------------------------------- declaration and windows ----
def test_crushgap_passes_the_freeze_static_check() -> None:
    rel = "strategy/members/k6/crushgap.py"
    assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K6") == []


def test_crushgap_declaration_is_zs_traded_zm_zl_signal() -> None:
    member = mk()
    assert isinstance(member, StageEMember)
    assert member.name == "K6-crushgap-01 ZS" and crushgap.MEMBER_ID == "K6-crushgap-01"
    assert member.legs == (LegSpec("ZS", True), LegSpec("ZM", False), LegSpec("ZL", False))
    assert sorted(n for n in vars(crushgap) if n.startswith("make_")) == ["make_zs"]
    assert mk() is not mk()
    with pytest.raises(ValueError, match="trades ZS only"):
        CrushGap("ZM")


def test_crushgap_trading_windows_are_the_s0_12_intervals() -> None:
    w = mk().trading_windows
    assert list(w) == ["ZS", "ZM", "ZL"]
    assert w["ZS"] == (TradingInterval(time(8, 30), time(13, 15)),)
    for r in ("ZM", "ZL"):
        assert w[r] == (TradingInterval(time(8, 30), time(8, 31)),
                        TradingInterval(time(13, 14), time(13, 15)))


def test_crushgap_declaration_freezes_and_verifies_under_tmp_path(tmp_path: Path) -> None:
    members_dir = tmp_path / "strategy" / "members"
    (members_dir / "k6").mkdir(parents=True)
    (members_dir / "__init__.py").write_bytes(b"")
    (members_dir / "k6" / "__init__.py").write_bytes(b"")
    for name in ("crushgap.py", "_port_common.py", "_calendar.py"):
        shutil.copyfile(K6_DIR / name, members_dir / "k6" / name)
    check_cluster_sources("K6", tmp_path)
    decl = MemberDecl("K6-crushgap-01 ZS", 22, "strategy.members.k6.crushgap", "make_zs",
                      (LegSpec("ZS", True), LegSpec("ZM", False), LegSpec("ZL", False)))
    write_cluster_freeze("K6", [decl], tmp_path)
    freeze = load_cluster_freeze("K6", tmp_path)
    verify_cluster_code(freeze)
    assert freeze.member("K6-crushgap-01 ZS").ordinal == 22


# -------------------------------------------------------------------- the GPM (K6-L-03) ----
def test_gpm_units_are_derived_from_rules_products_and_the_weights() -> None:
    assert {r: gpm_units_per_tick(r) for r in LEGS} == {"ZS": -25, "ZM": 22, "ZL": 11}
    assert FILTER_UNITS == 200
    weights = {"ZM": Decimal("0.022"), "ZL": Decimal("11"), "ZS": Decimal("-1")}
    assert weights == crushgap.GPM_WEIGHTS
    unit_and_filter = (Decimal("0.0001"), Decimal("0.02"))
    assert unit_and_filter == (crushgap.GPM_UNIT_USD_PER_BU, crushgap.FILTER_USD_PER_BU)
    # the identity: weight x tick / factor in 0.0001 USD/bu, from the frozen product table
    for r, w in (("ZM", Decimal("0.022")), ("ZL", Decimal("11")), ("ZS", Decimal("-1"))):
        p = product(r)
        assert w * p.vendor_tick / p.vendor_price_factor * 10_000 == gpm_units_per_tick(r)
    assert (product("ZM").vendor_price_factor, product("ZL").vendor_price_factor,
            product("ZS").vendor_price_factor) == (1, 100, 100)


def test_a_weighted_tick_off_the_unit_grid_is_refused() -> None:
    # K6-L-03: the coefficients must be exact integers of 0.0001 USD/bu, never rounded
    assert crushgap._exact_units(Decimal("0.0022"), "x") == 22
    with pytest.raises(ValueError, match="not an integer number"):
        crushgap._exact_units(Decimal("0.00015"), "x")


def test_gpm_hand_computed_in_usd_per_bushel() -> None:
    # vendor prices: ZM 300.0 USD/st, ZL 50.00 cents/lb, ZS 1050.00 cents/bu
    assert (BASE_PRICE["ZM"], BASE_PRICE["ZL"], BASE_PRICE["ZS"]) == (300.0, 50.0, 1050.0)
    usd = Decimal("0.022") * Decimal("300.0") + 11 * Decimal("0.50") - Decimal("10.50")
    assert usd == Decimal("1.60")
    ticks = {r: base_ticks(r) for r in LEGS}
    assert ticks == {"ZS": 4200, "ZM": 3000, "ZL": 5000}
    assert sum(gpm_units_per_tick(r) * ticks[r] for r in LEGS) == 16_000  # 1.60 x 10^4
    # a realistic case: ZM 290.3, ZL 52.17 cents, ZS 1012.25 cents
    t = {"ZM": 2903, "ZL": 5217, "ZS": 4049}
    usd = Decimal("0.022") * Decimal("290.3") + 11 * Decimal("0.5217") - Decimal("10.1225")
    assert usd == Decimal("2.0028")
    assert sum(gpm_units_per_tick(r) * t[r] for r in LEGS) == usd * 10_000 == 20_028


def test_the_filter_exactly_at_plus_and_minus_002_trades() -> None:
    assert g_units({"ZS": -8}) == 200 and g_units({"ZS": 8}) == -200
    assert fills(gap_case({"ZS": -8})) == TRADE_BUY  # G = +0.02: buy ZS
    assert fills(gap_case({"ZS": 8})) == TRADE_SELL  # G = -0.02: sell ZS


def test_one_unit_inside_the_filter_is_no_trade() -> None:
    inside_up, inside_down = {"ZM": 17, "ZS": 7}, {"ZM": -17, "ZS": -7}
    assert (g_units(inside_up), g_units(inside_down)) == (199, -199)
    assert intents(gap_case(inside_up)) == [] and intents(gap_case(inside_down)) == []
    assert intents(gap_case({"ZS": 7})) == [] and intents(gap_case({})) == []


@pytest.mark.parametrize(("gaps", "units", "side"), [
    ({"ZM": 10, "ZL": 5, "ZS": 3}, 200, "buy"), ({"ZM": 10, "ZL": 4, "ZS": 3}, 189, None),
    ({"ZM": 9, "ZL": 5, "ZS": 3}, 178, None), ({"ZM": 10, "ZL": 5, "ZS": 4}, 175, None),
    ({"ZM": -10, "ZL": -5, "ZS": -3}, -200, "sell"), ({"ZM": 10}, 220, "buy"),
    ({"ZM": 9}, 198, None), ({"ZL": 19}, 209, "buy"), ({"ZL": 18}, 198, None),
    ({"ZM": -10}, -220, "sell"), ({"ZL": -19}, -209, "sell"), ({"ZS": -9}, 225, "buy"),
])
def test_every_leg_enters_g_with_its_coefficient(gaps: Gaps, units: int, side: str | None
                                                 ) -> None:
    assert g_units(gaps) == units
    res = gap_case(gaps)
    expected = {"buy": TRADE_BUY, "sell": TRADE_SELL, None: []}[side]
    assert fills(res) == expected


def test_g_is_open_of_d_minus_close_of_d_minus_1() -> None:
    # d-1 closes ZS 8 ticks up, d opens ZS at the base: c = -8, G = +200, a buy
    days = legs_days(MON, TUE, closes={"ZS": 8})
    assert fills(run_legs(mk(), days)) == TRADE_BUY
    # the 08:30 CLOSE is not read: d opens at the d-1 close, then the 08:30 bar closes 8 down
    days = legs_days(MON, TUE, closes={"ZS": 8}, opens={"ZS": 8},
                     ZS={"paths": {BAR_0830: (8, 8, -8, -8)}})
    assert intents(run_legs(mk(), days)) == []
    # the d-1 OPEN of 13:14 is not read either (its close is)
    days = legs_days(MON, TUE, prev_ZS={"paths": {TICK_1314: (-8, 0, -8, 0)}})
    assert intents(run_legs(mk(), days)) == []


# ---------------------------------------------------------- the engine view of the legs ----
def test_engine_fills_only_zs_at_0831_and_holds_no_zm_or_zl_position() -> None:
    res = gap_case({"ZM": 10, "ZL": 5, "ZS": 3})
    assert fills(res) == TRADE_BUY
    assert fill_roots(res) == {"ZS"} and intent_roots(res) == {"ZS"}
    assert [f.position_after for f in res.events(Fill)] == [1, 0]
    assert all(f.qty == 1 for f in res.events(Fill))


@dataclass
class GuardlessProbe:
    """TEST ONLY: the member, plus a buy on the 08:30 ZS bar of ``day`` whenever the member
    stays silent there, to show what the engine does with an open when a signal leg has no bar
    (D11.5)."""

    inner: CrushGap
    day: date

    def __post_init__(self) -> None:
        self.name, self.legs = self.inner.name, self.inner.legs
        self.trading_windows = self.inner.trading_windows

    def on_minute(self, view: MinuteView, account: MemberAccountView) -> Any:
        out = self.inner.on_minute(view, account)
        bar = view.bar("ZS")
        if out or bar is None or bar.trade_date != self.day or ct(
                bar.ts_event_ns).time() != time(8, 30):
            return out
        return (leg_market_intent(view, "ZS", "buy", 1),)


@pytest.mark.parametrize("leg", ("ZM", "ZL"))
def test_engine_refuses_the_open_when_a_signal_leg_lacks_the_0830_bar_d11_5(leg: str) -> None:
    days = legs_days(MON, TUE, opens={"ZS": -8}, **{leg: {"skip": frozenset({BAR_0830})}})
    # the member itself sends nothing (its guard) ...
    assert intents(run_legs(mk(), days)) == []
    # ... and an open sent anyway is refused by the engine
    res = run_legs(GuardlessProbe(mk(), TUE), days)
    assert intents(res) == [(TUE, "08:30", False, "engine_leg_missing_bar")]
    assert fills(res) == []
    # with the bar present the probe adds nothing to the member's own trade
    assert fills(run_legs(GuardlessProbe(mk(), TUE), legs_days(MON, TUE, opens={"ZS": -8}))
                 ) == TRADE_BUY


# ------------------------------------------------------------------- d-1 (K6-L-04) ----
def test_a_monday_reads_the_friday() -> None:
    assert previous_trade_date(load_group_calendar("grains"), MON) == FRI
    assert fills(gap_case({"ZS": -8}, FRI, MON)) == trade(MON, "08:31", "13:14")


def test_the_tuesday_after_memorial_day_reads_the_friday() -> None:
    assert crushgap.previous_trade_date(GRAIN_TRADE_DATES, TUE_MD) == FRI_MD
    assert fills(gap_case({"ZS": 8}, FRI_MD, TUE_MD)) == trade(TUE_MD, "08:31", "13:14", "sell")


def test_d_minus_1_is_the_calendar_date_not_the_last_date_with_bars() -> None:
    # WED and TUE both full; TUE has no bars at all: WED's d-1 is TUE, so MON's closes are not
    # read and there is no trade on WED
    days = legs_days(MON, WED, opens={"ZS": -8})
    assert intents(run_legs(mk(), days, window=[MON, WED])) == []


def test_an_early_halt_d_minus_1_gives_no_trade_on_the_next_date() -> None:
    # 2025-11-28 (late open, halt 12:05) is d-1 of 2025-12-01: it has no 13:14 bars. The 11-26
    # closes would give G = +200 (the most-recent-complete reading would trade)
    assert crushgap.previous_trade_date(GRAIN_TRADE_DATES, MON_TG) == HALT_TG
    days = legs_days(WED_TG, MON_TG, opens={"ZS": -8})
    halt = Day(HALT_TG, no_evening=True, halt="12:05", end=hm(12, 5))
    days = {r: [days[r][0], halt, days[r][1]] for r in LEGS}
    assert intents(run_legs(mk(), days)) == []
    # control: with 11-28's 13:14 bars present (a synthetic full day), 12-01 trades
    full = {r: [days[r][0], Day(HALT_TG, no_evening=True), days[r][2]] for r in LEGS}
    assert fills(run_legs(mk(), full)) == trade(MON_TG, "08:31", "13:14")


# ------------------------------------------------------------- the guard (K6-L-05) ----
@pytest.mark.parametrize("leg", LEGS)
def test_a_missing_1314_bar_of_d_minus_1_on_any_leg_is_no_trade(leg: str) -> None:
    days = legs_days(MON, TUE, opens={"ZS": -8}, **{f"prev_{leg}": {"skip": frozenset(
        {TICK_1314})}})
    assert intents(run_legs(mk(), days)) == []


@pytest.mark.parametrize("leg", LEGS)
def test_a_missing_0830_bar_of_d_on_any_leg_is_no_trade(leg: str) -> None:
    days = legs_days(MON, TUE, opens={"ZS": -8}, **{leg: {"skip": frozenset({BAR_0830})}})
    res = run_legs(mk(), days)
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("leg", LEGS)
def test_an_instrument_change_on_any_leg_is_no_trade(leg: str) -> None:
    # the leg's 13:14 bar of d-1 and 08:30 bar of d carry different ids: no trade
    days = legs_days(MON, TUE, opens={"ZS": -8}, **{f"prev_{leg}": {"ids": {TICK_1314: 776}}})
    assert intents(run_legs(mk(), days)) == []
    days = legs_days(MON, TUE, opens={"ZS": -8}, **{leg: {"ids": {BAR_0830: 778}}})
    assert intents(run_legs(mk(), days)) == []


def test_different_ids_across_legs_are_accepted() -> None:
    # each leg has its own contract (months may differ): only a change within a leg matters
    days = legs_days(MON, TUE, opens={"ZS": -8}, prev_ZM={"instrument_id": 1},
                     ZM={"instrument_id": 1}, prev_ZL={"instrument_id": 2},
                     ZL={"instrument_id": 2})
    assert fills(run_legs(mk(), days)) == TRADE_BUY


# -------------------------------------------------------- exclusions, entry and exit ----
def test_d_not_in_grain_full_sessions_is_no_trade() -> None:
    assert HALT_XMAS not in GRAIN_FULL_SESSIONS and TUE_XMAS in GRAIN_FULL_SESSIONS
    assert HALT_TG not in GRAIN_FULL_SESSIONS
    assert {MON, TUE, WED, FRI, WED_TG, MON_TG} <= GRAIN_FULL_SESSIONS
    # 12-24 (halt 12:05): with bars to the regular close and G = +200, still no intent
    days = legs_days(TUE_XMAS, HALT_XMAS, opens={"ZS": -8},
                     **{r: {"halt": "12:05"} for r in LEGS})
    assert intents(run_legs(mk(), days)) == []


def test_d_in_full_sessions_with_a_late_open_trades() -> None:
    # a grain late open (no evening session) is not an early close (S0.8): 2026-01-02 is a
    # full session and reads 2025-12-31
    late = date(2026, 1, 2)
    assert late in GRAIN_FULL_SESSIONS
    prev = crushgap.previous_trade_date(GRAIN_TRADE_DATES, late)
    assert prev == date(2025, 12, 31) and prev in GRAIN_FULL_SESSIONS
    days = legs_days(prev, late, opens={"ZS": -8}, **{r: {"no_evening": True} for r in LEGS})
    assert fills(run_legs(mk(), days)) == trade(late, "08:31", "13:14")


def test_the_entry_is_the_0830_zs_bar_only() -> None:
    # ZS has no 08:30 bar; its 08:31 bar opens 8 ticks down (G would be +200 there)
    days = legs_days(MON, TUE, opens={"ZS": -8}, ZS={"skip": frozenset({BAR_0830}),
                                                     "paths": {hm(8, 31): (-8, 0, -8, 0)}})
    assert intents(run_legs(mk(), days)) == []


def test_missing_1313_zs_bar_sends_the_exit_on_1314() -> None:
    days = legs_days(MON, TUE, opens={"ZS": -8}, ZS={"skip": frozenset({hm(13, 13)})})
    res = run_legs(mk(), days)
    assert fills(res) == trade(TUE, "08:31", "13:15")
    assert [i[1] for i in intents(res)] == ["08:30", "13:14"]


def test_no_exit_before_1313_and_exit_needs_a_zs_bar() -> None:
    # ZM and ZL bars at 13:13 do not carry the exit: only the ZS bar does
    days = legs_days(MON, TUE, opens={"ZS": -8}, ZS={"skip": frozenset({hm(13, 13)})},
                     ZM={"paths": {}}, ZL={"paths": {}})
    res = run_legs(mk(), days)
    assert [i[1] for i in intents(res)] == ["08:30", "13:14"]
    assert [i[1] for i in intents(gap_case({"ZS": -8}))] == ["08:30", "13:13"]


def test_one_trade_per_trade_date_on_consecutive_days() -> None:
    days = legs_days(MON, TUE, opens={"ZS": -8})
    wed = {r: Day(WED, paths={BAR_0830: (8, 8, 0, 0)} if r == "ZS" else {}) for r in LEGS}
    days = {r: [*days[r], wed[r]] for r in LEGS}
    res = run_legs(mk(), days)
    # WED's d-1 is TUE (13:14 closes at the base); ZS opens +8 on WED: G = -200, a sell
    assert fills(res) == TRADE_BUY + trade(WED, "08:31", "13:14", "sell")


def test_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    days = legs_days(MON, TUE, opens={"ZS": -8}, ZS={"flatten_from": hm(12, 0)})
    res = run_legs(mk(), days)
    assert fills(res) == trade(TUE, "08:31", "12:01", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["08:30"]


# ------------------------------------------------------------------- direct calls ----
def view3(ts: int, bars: Mapping[str, Bar | None]) -> MinuteView:
    return MinuteView(ts, MappingProxyType({r: bars.get(r) for r in LEGS}))


def account3(position: int = 0, pending: int = 0) -> MemberAccountView:
    return MemberAccountView(Phase.XFA, Status.ACTIVE, None, 0, 0,
                             MappingProxyType({"ZS": position}), MappingProxyType({"ZS": pending}),
                             MappingProxyType({"ZS": None}), MappingProxyType({"ZS": 0}))


def prime(member: CrushGap, prev: date = MON, ct_day: date | None = None,
          zs_close: int = 8) -> None:
    """Feed the three 13:14 bars of ``prev`` (on CT date ``ct_day``, default prev)."""
    on = prev if ct_day is None else ct_day
    bars = {r: bar_at(r, on, TICK_1314, (0, max(zs_close, 0), 0, zs_close) if r == "ZS"
                      else (0, 0, 0, 0), trade_day=prev) for r in LEGS}
    assert member.on_minute(view3(ns_at(on, TICK_1314), bars), account3()) == ()


def opening(day: date = TUE) -> MinuteView:
    return view3(ns_at(day, BAR_0830), {r: bar_at(r, day, BAR_0830) for r in LEGS})


def test_direct_one_entry_per_trade_date_and_none_while_pending() -> None:
    member = mk()
    prime(member)
    (intent,) = member.on_minute(opening(), account3())  # ZS closed +8, opens 0: G = +200
    assert (intent.root, intent.side, intent.quantity) == ("ZS", "buy", 1)
    assert member.on_minute(opening(), account3()) == ()
    member = mk()
    prime(member)
    assert member.on_minute(opening(), account3(0, 1)) == ()


def test_direct_the_1314_bar_must_be_on_its_trade_dates_ct_date() -> None:
    member = mk()
    prime(member, MON, ct_day=MON - timedelta(days=1))  # a 13:14 bar of CT date d-2
    assert member.on_minute(opening(), account3()) == ()


def test_direct_signal_leg_closes_are_recorded_without_a_zs_bar() -> None:
    member = mk()
    ts = ns_at(MON, TICK_1314)
    zs = {"ZS": bar_at("ZS", MON, TICK_1314, (0, 8, 0, 8))}
    others = {r: bar_at(r, MON, TICK_1314) for r in ("ZM", "ZL")}
    assert member.on_minute(view3(ts, others), account3()) == ()  # no ZS bar at this minute
    assert member.on_minute(view3(ts, zs), account3()) == ()
    (intent,) = member.on_minute(opening(), account3())
    assert intent.side == "buy"


def test_direct_no_intent_on_a_signal_leg_ever() -> None:
    member = mk()
    prime(member)
    out = list(member.on_minute(opening(), account3()))
    later = view3(ns_at(TUE, hm(13, 13)), {r: bar_at(r, TUE, hm(13, 13)) for r in LEGS})
    out += member.on_minute(later, account3(1))
    assert [(i.root, i.side) for i in out] == [("ZS", "buy"), ("ZS", "sell")]


def test_direct_the_entry_bar_is_the_0830_bar_of_ct_date_d() -> None:
    # an 08:30 bar set of CT date d-1 carrying trade date d (never produced) is not the entry
    member = mk()
    prime(member)
    stray = view3(ns_at(MON, BAR_0830),
                  {r: bar_at(r, MON, BAR_0830, trade_day=TUE) for r in LEGS})
    assert member.on_minute(stray, account3()) == ()
    (intent,) = member.on_minute(opening(), account3())
    assert intent.side == "buy"
