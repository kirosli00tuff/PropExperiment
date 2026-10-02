"""Stage E.9 K8-oilcad-01 of MemberCoder-B (reports/stage_e9_member_specs.md section 2; readings
K8-L-04..K8-L-11; S0.4, S0.6, S0.7, S0.9, S0.10, S0.12). This file also holds the small K8 kit that
tests/test_k8_members_wkndbtc.py imports (synthetic Bars, direct calls, engine frames).

Synthetic bars only; no bar file is read. Direct calls feed views minute by minute (both legs'
keys always present, a None for a missing bar); engine tests run the real Stage E engine on
synthetic two-leg frames (as tests/test_stage_e_alignment.py).

The reference set STANDARD (20 dates): MCL closes at the 66 signal clocks 07:59, 08:04, ...,
13:24, base B = 6000 ticks (60.00). Each date starts at B and holds `zeros` flat steps (r = 0),
then `plus` steps B -> B+1 (r = +1/6000) and `minus` steps B -> B-1 (r = -1/6000), each followed
by a return to B under a NEW instrument_id (that return's r is undefined, S0.9). Totals: 125
plus, 125 minus, 751 zeros, n = 1001, mean 0, so the sample variance is 250 u^2 / 1000 = u^2 / 4
with u = 1/6000: s(d) = u / 2 exactly (statistics.stdev rounds the exact square root). A trade
day step of +1 from B gives r = u and z = 2.0 exactly; +1 from B+1 gives z = 1.99967 under
ddof 1 and 2.00067 under ddof 0 (pstdev); +2 from B gives z ~ 4.
"""

from __future__ import annotations

import statistics
from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from types import MappingProxyType
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from data.stage_e_bars import RESEARCH, LegFrame
from rules import sessions
from rules.products import PRICE_SCALE, product
from rules.xfa_rules import Phase, Status
from screening.stage_e_align import member_window
from screening.stage_e_engine import EngineResult, Fill, IntentRecord, run_engine
from screening.stage_e_freeze import check_member_source
from screening.stage_e_frozen import leg_inputs, load_frozen_tables
from screening.stage_e_rules import StageERules
from strategy.interface import Bar
from strategy.members.k8 import oilcad
from strategy.members.k8._calendar import OILCAD_DATES, previous_dates
from strategy.members.k8._releases import in_guard
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    StageEMember,
    TradingInterval,
)
from tests._stage_e_canary_kit import NO_RELEASES

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
REPO = Path(__file__).resolve().parents[1]
K8_DIR = REPO / "strategy" / "members" / "k8"


# ============================================================== the K8 kit (shared) ====
def hm(hh: int, mm: int) -> int:
    return hh * 60 + mm


def clock(minute: int) -> str:
    return f"{minute // 60:02d}:{minute % 60:02d}"


def ns_at(day: date, minute: int) -> int:
    """UTC ns of CT clock ``minute`` (0..1439) on CT calendar date ``day``."""
    local = datetime.combine(day, time(minute // 60, minute % 60), tzinfo=CT)
    return int(local.astimezone(UTC).timestamp()) * NS


def ct(ns: int) -> datetime:
    return datetime.fromtimestamp(ns // NS, tz=UTC).astimezone(CT)


def price(root: str, ticks: int) -> float:
    """``ticks`` vendor ticks of ``root`` as the engine's float."""
    return ticks * product(root).vendor_tick_fixed / PRICE_SCALE


RootBar = tuple[str, Bar]


def mk_bar(root: str, ct_day: date, minute: int, ticks: int, *, trade_day: date | None = None,
           iid: int = 777) -> RootBar:
    """A flat bar (o = h = l = c) of ``root`` opening at CT ``minute`` of CT date ``ct_day``,
    carrying ``trade_day`` (default: the CT date)."""
    p = price(root, ticks)
    return root, Bar(ns_at(ct_day, minute), p, p, p, p, 10, iid, f"{root}U5",
                     ct_day if trade_day is None else trade_day, False, False, None, False,
                     False, 0, False)


def account(roots: Iterable[str], position: int = 0, pending: int = 0, root: str | None = None
            ) -> MemberAccountView:
    """An XFA account snapshot: ``position`` and ``pending`` on ``root`` (default: the first)."""
    roots = tuple(roots)
    held = roots[0] if root is None else root
    return MemberAccountView(
        Phase.XFA, Status.ACTIVE, None, 0, 0,
        MappingProxyType({r: position if r == held else 0 for r in roots}),
        MappingProxyType({r: pending if r == held else 0 for r in roots}),
        MappingProxyType({r: None for r in roots}), MappingProxyType({r: 0 for r in roots}))


Intent = tuple[date, str, str, str, int]  # (CT date, CT hh:mm of the view, root, side, qty)
AccountFn = Callable[[int], MemberAccountView]


def drive(member: Any, bars: Sequence[RootBar], acct: AccountFn | None = None) -> list[Intent]:
    """Direct calls, one per minute holding any bar, in time order; every leg's key is present
    (None: no bar). ``acct(ts_ns)`` gives the account per view (default: flat)."""
    roots = tuple(leg.root for leg in member.legs)
    traded = tuple(leg.root for leg in member.legs if leg.traded)
    by_ts: dict[int, dict[str, Bar]] = {}
    for root, b in bars:
        assert root in roots and root not in by_ts.get(b.ts_event_ns, {})
        by_ts.setdefault(b.ts_event_ns, {})[root] = b
    flat = account(traded)
    out: list[Intent] = []
    for ts in sorted(by_ts):
        view = MinuteView(ts, MappingProxyType({r: by_ts[ts].get(r) for r in roots}))
        for item in member.on_minute(view, flat if acct is None else acct(ts)):
            assert isinstance(item, LegIntent), item
            at = ct(ts)
            out.append((at.date(), f"{at:%H:%M}", item.root, item.side, item.quantity))
    return out


def frame_of(root: str, bars: Sequence[RootBar], flatten_at: frozenset[int] = frozenset()
             ) -> pd.DataFrame:
    """The engine frame of ``root``'s bars; session flags from rules/sessions.py, plus a bar
    flatten flag on the bars opening at ``flatten_at`` (UTC ns; an engine closure)."""
    rows = []
    for r, b in bars:
        if r != root:
            continue
        state = sessions.session_state(root, ct(b.ts_event_ns).astimezone(UTC))
        forced = b.ts_event_ns in flatten_at
        rows.append({
            "ts_event": b.ts_event_ns, "open": b.close, "high": b.close, "low": b.close,
            "close": b.close, "volume": 10, "instrument_id": b.instrument_id,
            "raw_symbol": b.raw_symbol, "trade_date": b.trade_date.isoformat(),
            "in_flatten_window": bool(state.must_be_flat) or forced,
            "in_no_new_positions_window": bool(not state.can_open),
            "early_halt_ct": "", "in_scheduled_closure": False, "is_roll_session": False,
            "gap_before_minutes": 0, "vendor_degraded_day": False})
    out = pd.DataFrame(rows).sort_values("ts_event", ignore_index=True)
    assert out["ts_event"].is_unique
    return out


def rules_of(member: Any, window: Iterable[date], blackout: Iterable[date] = ()) -> StageERules:
    """The real Stage E rules: ``blackout`` is the union of the legs' roll blackouts (D4)."""
    return StageERules({leg.root: leg_inputs(leg.root, traded=leg.traded) for leg in member.legs},
                       frozenset(window), frozenset(blackout), NO_RELEASES)


def engine(member: Any, bars: Sequence[RootBar], rules: StageERules,
           flatten_at: frozenset[int] = frozenset()) -> EngineResult:
    frames = {leg.root: frame_of(leg.root, bars, flatten_at) for leg in member.legs}
    return run_engine(frames, member, member.legs, rules)


def leg_frame(root: str, bars: Sequence[RootBar], blackout: Iterable[date] = ()) -> LegFrame:
    """A research-store LegFrame as the runner builds it (D4's inputs)."""
    f = frame_of(root, bars)
    days = tuple(sorted({date.fromisoformat(d) for d in f["trade_date"]}))
    return LegFrame(root, RESEARCH, f"{root}.parquet", "0" * 64, f, days, (), frozenset(blackout))


def runner_rules(member: Any, bars: Sequence[RootBar], blackouts: Mapping[str, Iterable[date]]
                 ) -> tuple[StageERules, Any]:
    """The rules the runner would build: member_window over the legs' frames (common dates less
    the union of every leg's roll blackouts), the union as the rules' blackout."""
    frames = {leg.root: leg_frame(leg.root, bars, blackouts.get(leg.root, ()))
              for leg in member.legs}
    mw = member_window(frames, RESEARCH)
    return (StageERules({leg.root: leg_inputs(leg.root, traded=leg.traded)
                         for leg in member.legs},
                        frozenset(mw.dates), mw.blackout_union, NO_RELEASES), mw)


Filled = tuple[date, str, str, str, str]  # (trade date, CT hh:mm of the fill bar, root, side, why)


def fills(res: EngineResult) -> list[Filled]:
    return [(ct(f.fill_ts_ns).date(), f"{ct(f.fill_ts_ns):%H:%M}", f.root, f.side, f.reason)
            for f in res.events(Fill)]


def intent_roots(res: EngineResult) -> set[str | None]:
    return {r.root for r in res.events(IntentRecord)}


def refusals(res: EngineResult) -> list[str]:
    return [r.refusal.reason for r in res.events(IntentRecord) if r.refusal is not None]


# ========================================================== the oilcad scenarios ====
B_MCL = 6000  # 60.00 USD/bbl in 0.01 ticks
B_CAD = 14000  # 0.70000 USD/CAD in 0.00005 ticks
POINTS = tuple(hm(7, 59) + 5 * j for j in range(66))  # the MCL signal bars 07:59 .. 13:24
DECISIONS = tuple(hm(8, 5) + 5 * j for j in range(65))  # T: 08:05 .. 13:25
U = 1 / 6000
Spec = tuple[int, int, int]  # (plus, minus, zeros) of one reference date
STANDARD: tuple[Spec, ...] = ((7, 7, 37),) * 5 + ((6, 6, 38),) * 11 + ((6, 6, 37),) * 4
WPSR_DAY = date(2025, 7, 9)  # WPSR 10:30 ET = 09:30 CT (1b A3)
FOMC_DAY = date(2025, 7, 30)  # FOMC 14:00 ET = 13:00 CT (also a WPSR day)
HOLIDAY_WPSR_DAY = date(2025, 9, 4)  # WPSR 11:00 CT (holiday week)
DROPPED_WPSR_DAY = date(2026, 5, 28)  # WPSR 11:00 CT, E.4-dropped, kept by R-1b-1
PLAIN_DAY = date(2025, 7, 8)  # no 6C row in the day's grid
DAY = PLAIN_DAY


def ref_path(spec: Spec, base: int = B_MCL) -> list[tuple[int, int]]:
    """(close ticks, instrument_id) at the signal points of one reference date (module doc)."""
    plus, minus, zeros = spec
    iid = 1
    pts = [(base, iid)] * (1 + zeros)
    for step in (1,) * plus + (-1,) * minus:
        pts.append((base + step, iid))
        iid += 1
        pts.append((base, iid))
    pts = pts[:-1]  # the last return to B adds no value
    assert len(pts) <= len(POINTS)
    return pts


def ref_values(specs: Sequence[Spec], base: int = B_MCL) -> list[float]:
    """The r values the reference dates give, computed independently of the member."""
    out: list[float] = []
    for plus, minus, zeros in specs:
        up, down = (base + 1 - base) / base, (base - 1 - base) / base
        out += [0.0] * zeros + [up] * plus + [down] * minus
    return out


def ref_bars(dates: Sequence[date], specs: Sequence[Spec]) -> list[RootBar]:
    assert len(dates) == len(specs)
    return [mk_bar("MCL", d, POINTS[j], ticks, iid=iid)
            for d, spec in zip(dates, specs, strict=True)
            for j, (ticks, iid) in enumerate(ref_path(spec))]


def refs_of(day: date) -> tuple[date, ...]:
    refs = previous_dates(OILCAD_DATES, day, 20)
    assert len(refs) == 20
    return refs


def trade_bars(day: date, steps: Mapping[str, int] | None = None, *, base: int = B_MCL,
               mcl_skip: Iterable[int] = (), mcl_ids: Mapping[int, int] | None = None,
               mcl_extra: Sequence[tuple[int, int]] = (), cad_skip: Iterable[int] = (),
               cad_from: int = hm(7, 55), cad_to: int = hm(13, 50)) -> list[RootBar]:
    """Trade date ``day``: MCL at the signal points, flat at ``base`` except ``steps``
    {decision "HH:MM": ticks} (the step lands on that decision's t - 1 point, so r_t =
    step / level at t - 6); ``mcl_extra`` adds (minute, ticks) bars; 6C every minute
    [cad_from, cad_to] at B_CAD less ``cad_skip``."""
    steps, mcl_ids = steps or {}, mcl_ids or {}
    assert all(hm(*map(int, t.split(":"))) in DECISIONS for t in steps), steps
    skip, cskip = set(mcl_skip), set(cad_skip)
    level, out = base, []
    for j, minute in enumerate(POINTS):
        if j:
            level += steps.get(clock(DECISIONS[j - 1]), 0)
        if minute not in skip:
            out.append(mk_bar("MCL", day, minute, level, iid=mcl_ids.get(minute, 777)))
    out += [mk_bar("MCL", day, m, ticks, iid=mcl_ids.get(m, 777)) for m, ticks in mcl_extra]
    out += [mk_bar("6C", day, m, B_CAD) for m in range(cad_from, cad_to + 1) if m not in cskip]
    return out


def oil_bars(day: date, steps: Mapping[str, int] | None = None, *,
             specs: Sequence[Spec] = STANDARD, **kw: Any) -> list[RootBar]:
    """The 20 reference dates of ``day`` (STANDARD) and the trade date; the run starts on the
    oldest reference date (the warm-up is met exactly)."""
    return ref_bars(refs_of(day), specs) + trade_bars(day, steps, **kw)


def entries(day: date, steps: Mapping[str, int] | None = None, *,
            acct: AccountFn | None = None, **kw: Any) -> list[tuple[str, str]]:
    """(CT hh:mm of the view, side) of every intent on the trade date (direct calls)."""
    out = drive(oilcad.make_6c(), oil_bars(day, steps, **kw), acct)
    assert all(i[0] == day and i[2] == "6C" and i[4] == 1 for i in out), out
    return [(i[1], i[3]) for i in out]


def mk() -> oilcad.OilCad:
    return oilcad.make_6c()


# ------------------------------------------------------------------- the kit's facts ----
def test_standard_reference_set_gives_s_exactly_u_over_2() -> None:
    values = ref_values(STANDARD)
    assert len(values) == 1001
    assert statistics.stdev(values) == U / 2
    assert U / (U / 2) == 2.0
    assert statistics.pstdev(values) < U / 2  # ddof 0 is smaller: z under it is larger


def test_scenario_dates_are_calendar_facts() -> None:
    oil = set(OILCAD_DATES)
    for d in (WPSR_DAY, FOMC_DAY, HOLIDAY_WPSR_DAY, DROPPED_WPSR_DAY, PLAIN_DAY):
        assert d in oil
    assert in_guard("6C", ns_at(WPSR_DAY, hm(9, 30)))
    assert not in_guard("6C", ns_at(WPSR_DAY, hm(9, 35)))
    assert in_guard("6C", ns_at(FOMC_DAY, hm(13, 0)))
    assert in_guard("6C", ns_at(HOLIDAY_WPSR_DAY, hm(11, 0)))
    assert in_guard("6C", ns_at(DROPPED_WPSR_DAY, hm(11, 0)))
    assert not any(in_guard("6C", ns_at(PLAIN_DAY, t)) for t in DECISIONS)
    # 2025-06-19 and 2025-07-04 are not OILCAD dates; WPSR_DAY's 20 reference dates skip them
    assert date(2025, 6, 19) not in oil and date(2025, 7, 4) not in oil
    assert refs_of(WPSR_DAY)[0] == date(2025, 6, 9) and refs_of(WPSR_DAY)[-1] == PLAIN_DAY


# --------------------------------------------------------------- declaration and freeze ----
def test_factory_name_legs_size_and_protocol() -> None:
    m = mk()
    assert isinstance(m, StageEMember)
    assert m.name == "K8-oilcad-01 6C"
    assert m.legs == (LegSpec("6C", True), LegSpec("MCL", False))
    assert load_frozen_tables().vehicles["6C"].q_c == 1
    assert m._q == load_frozen_tables().vehicles["6C"].q_c
    with pytest.raises(ValueError):
        oilcad.OilCad("MCL")


def test_trading_windows_are_s0_12() -> None:
    assert mk().trading_windows == {
        "6C": (TradingInterval(time(8, 4), time(13, 41)),),
        "MCL": (TradingInterval(time(7, 59), time(13, 25)),),
    }


@pytest.mark.parametrize("name", ["oilcad.py"])
def test_member_file_passes_the_freeze_static_check(name: str) -> None:
    rel = f"strategy/members/k8/{name}"
    assert check_member_source(rel, (REPO / rel).read_text(), "K8") == []


# ----------------------------------------------------------------- the decision clock ----
def test_decision_clock_is_08_05_to_13_25_every_5_minutes() -> None:
    t = oilcad.DECISION_TIMES_CT
    assert len(t) == 65
    assert t[0] == time(8, 5) and t[-1] == time(13, 25)
    assert [hm(x.hour, x.minute) for x in t] == list(DECISIONS)


def test_first_and_last_decisions_trade() -> None:
    assert entries(DAY, {"08:05": 2, "13:25": 2}) == [("08:04", "buy"), ("13:24", "buy")]


def test_no_decision_at_08_00() -> None:
    """A big MCL move 07:54 -> 07:59 with a 6C bar at 07:59: 08:00 is not a decision time."""
    assert entries(DAY, mcl_extra=[(hm(7, 54), B_MCL - 3)]) == []


def test_no_decision_at_13_30() -> None:
    """A big MCL move 13:24 -> 13:29 with a 6C bar at 13:29: 13:30 is not a decision time."""
    assert entries(DAY, mcl_extra=[(hm(13, 29), B_MCL + 3)]) == []


def test_r_t_reads_the_mcl_bars_at_t_minus_1_and_t_minus_6() -> None:
    """t = 08:05: closes of 07:59 (B) and 08:04 (B + 2): a buy. Decoy bars 08:00..08:03 at
    B + 6 (a sell if 08:00 were t - 5) and 07:58 at B + 6 (a sell against 08:04 if it were
    t - 7) are never read."""
    decoys = [(m, B_MCL + 6) for m in (hm(7, 58), *range(hm(8, 0), hm(8, 4)))]
    assert entries(DAY, {"08:05": 2}, mcl_extra=decoys) == [("08:04", "buy")]


def test_the_entry_is_on_the_6c_bar_at_t_minus_1() -> None:
    """A big move at t = 09:05 is acted on at the 09:04 view only."""
    assert entries(DAY, {"09:05": 2}) == [("09:04", "buy")]


# ------------------------------------------------------------------------ the arithmetic ----
def test_block_return_requires_a_positive_denominator() -> None:
    assert oilcad.block_return(5, 0) is None
    assert oilcad.block_return(5, -1) is None
    assert oilcad.block_return(6001, 6000) == 1 / 6000
    assert oilcad.block_return(5999, 6000) == -1 / 6000


def test_a_zero_mcl_close_at_t_minus_6_leaves_r_t_undefined() -> None:
    """The 07:59 close is 0 (c6 of t = 08:05, the c1 of no block): no entry at 08:05 despite
    the move; 08:10 still trades."""
    bars = oil_bars(DAY, {"08:05": 2, "08:10": 2})
    bars = [rb for rb in bars if not (rb[0] == "MCL" and rb[1].trade_date == DAY
                                      and ct(rb[1].ts_event_ns).time() == time(7, 59))]
    bars.append(mk_bar("MCL", DAY, hm(7, 59), 0))
    out = drive(mk(), sorted(bars, key=lambda rb: rb[1].ts_event_ns))
    assert [(i[1], i[3]) for i in out] == [("08:09", "buy")]


def test_scale_is_the_sample_standard_deviation_ddof_1() -> None:
    """Hand-computed: 500 x +0.25, 500 x -0.25 and one 0: ddof 1 gives exactly 0.25 (ss 62.5 over
    1000), ddof 0 gives 0.24988; r = 0.49985 is z = 1.9994 under ddof 1 (no trade) and 2.0004
    under ddof 0 (a trade)."""
    values = [0.25] * 500 + [-0.25] * 500 + [0.0]
    s = oilcad.scale(values)
    assert s == 0.25
    assert not oilcad.passes_threshold(0.49985, s)
    assert abs(0.49985 / statistics.pstdev(values)) >= 2.0  # ddof 0 would flip it


def test_scale_refuses_fewer_than_1000_values_and_a_zero_deviation() -> None:
    assert oilcad.scale([0.25, -0.25] * 499 + [0.0]) is None  # n = 999
    assert oilcad.scale([0.25, -0.25] * 500) == pytest.approx(0.2501250, rel=1e-6)  # n = 1000
    assert oilcad.scale([0.0] * 1300) is None  # s = 0


def test_threshold_is_inclusive_at_exactly_2() -> None:
    assert oilcad.passes_threshold(0.5, 0.25)  # z = 2.0 exactly
    assert oilcad.passes_threshold(-0.5, 0.25)
    below = 0.49999999999999994  # the float just below 0.5
    assert 0.5 - below > 0
    assert not oilcad.passes_threshold(below, 0.25)
    assert not oilcad.passes_threshold(-below, 0.25)


def test_z_exactly_2_trades_end_to_end() -> None:
    """STANDARD: s = u/2; a +1 step from B is r = u, z = 2.0 exactly: a buy; -1 a sell."""
    assert entries(DAY, {"10:05": 1}) == [("10:04", "buy")]
    assert entries(DAY, {"10:05": -1}) == [("10:04", "sell")]


def test_ddof_1_end_to_end_just_below_2_does_not_trade() -> None:
    """On base B + 1 a +1 step is r = 1/6001: z = 1.99967 with ddof 1 (no trade); ddof 0 would
    give 2.00067 (a trade)."""
    values = ref_values(STANDARD)
    r = (B_MCL + 2 - (B_MCL + 1)) / (B_MCL + 1)
    assert abs(r / statistics.stdev(values)) < 2.0 <= abs(r / statistics.pstdev(values))
    assert entries(DAY, {"10:05": 1}, base=B_MCL + 1) == []
    assert entries(DAY, {"10:05": 2}, base=B_MCL + 1) == [("10:04", "buy")]  # control


def test_n_1000_trades_and_n_999_does_not() -> None:
    n1000 = STANDARD[:-1] + ((6, 6, 36),)  # one zero fewer: n = 1000
    n999 = STANDARD[:-1] + ((6, 6, 35),)  # n = 999
    assert len(ref_values(n1000)) == 1000 and len(ref_values(n999)) == 999
    assert entries(DAY, {"10:05": 2}, specs=n1000) == [("10:04", "buy")]
    assert entries(DAY, {"10:05": 2}, specs=n999) == []


def test_zero_scale_is_no_trade_on_d() -> None:
    flat = ((0, 0, 65),) * 20
    assert entries(DAY, {"10:05": 50}, specs=flat) == []


def test_sign_buys_on_z_above_zero_and_sells_below() -> None:
    assert entries(DAY, {"09:05": 2, "10:05": -2}) == [("09:04", "buy"), ("10:04", "sell")]


def test_small_moves_do_not_trade() -> None:
    assert entries(DAY, {"09:05": 0}) == []
    assert entries(DAY, {"09:05": 1}, base=B_MCL + 50) == []


# ------------------------------------------------------- reference dates and warm-up ----
def test_reference_dates_are_the_20_previous_oilcad_dates() -> None:
    """WPSR_DAY's references skip 2025-06-19 and 2025-07-04 (not OILCAD dates). Wild MCL values
    on those two weekdays and on the date before the oldest reference (2025-06-09) must not
    enter s(d): with them, z = 2.0 exactly would fall below 2."""
    day = date(2025, 7, 10)  # a non-WPSR day whose references contain both holidays
    refs = refs_of(day)
    assert date(2025, 6, 19) not in refs and date(2025, 7, 4) not in refs
    assert refs[0] == date(2025, 6, 10) and refs[-1] == WPSR_DAY
    oldest = previous_dates(OILCAD_DATES, refs[0], 1)[0]
    wild = ((16, 16, 0),)  # 32 values of |r| = u > s: they would raise s
    bars = (ref_bars((oldest,), wild) + ref_bars(refs[:10], STANDARD[:10])
            + ref_bars((date(2025, 6, 19),), wild) + ref_bars(refs[10:], STANDARD[10:])
            + ref_bars((date(2025, 7, 4),), wild) + trade_bars(day, {"10:05": 1}))
    bars = sorted(bars, key=lambda rb: rb[1].ts_event_ns)
    out = drive(mk(), bars)
    assert [(i[0], i[1], i[3]) for i in out] == [(day, "10:04", "buy")]


def test_warm_up_20th_eligible_date_no_trade_21st_trades() -> None:
    """The run starts on S[0]. S[0]..S[18] each give 55 values; S[19] and S[20] carry a big
    move. On S[19] the references start one date before the run (warm-up: no trade, though
    n = 1045 and z ~ 7); on S[20] they are S[0]..S[19]: a trade."""
    start = OILCAD_DATES.index(date(2025, 8, 4))
    s = OILCAD_DATES[start:start + 21]
    warm = ((5, 5, 45),) * 19
    assert len(ref_values(warm)) == 1045
    bars = (ref_bars(s[:19], warm) + trade_bars(s[19], {"10:05": 3})
            + trade_bars(s[20], {"10:05": 10}))
    bars = sorted(bars, key=lambda rb: rb[1].ts_event_ns)
    out = drive(mk(), bars)
    assert [(i[0], i[1], i[3]) for i in out] == [(s[20], "10:04", "buy")]


def test_too_few_reference_dates_at_the_table_start_no_trade() -> None:
    day = OILCAD_DATES[19]  # only 19 OILCAD dates before it
    assert len(previous_dates(OILCAD_DATES, day, 20)) == 19
    rich = ((5, 5, 45),) * 19  # n = 1045, s > 0: only the reference count blocks the trade
    bars = ref_bars(OILCAD_DATES[:19], rich) + trade_bars(day, {"10:05": 50})
    assert drive(mk(), sorted(bars, key=lambda rb: rb[1].ts_event_ns)) == []


def test_a_date_outside_oilcad_dates_never_trades() -> None:
    """2025-07-04 (not an OILCAD date) with synthetic bars and a big move: no trade."""
    day = date(2025, 7, 4)
    refs = previous_dates(OILCAD_DATES, day, 20)
    bars = ref_bars(refs, STANDARD) + trade_bars(day, {"10:05": 5})
    assert drive(mk(), bars) == []


# ------------------------------------------------- the instrument guard, missing bars ----
def test_mcl_roll_inside_a_block_no_entry_at_t_later_decisions_proceed() -> None:
    """08:59 carries id 777 and 09:04 id 778: r_09:05 undefined (no entry at 09:05, though
    the move is big); 09:04 and 09:09 both 778: r_09:10 defined, a buy."""
    ids = {m: 778 for m in POINTS if m >= hm(9, 4)}
    assert entries(DAY, {"09:05": 2, "09:10": 2}, mcl_ids=ids) == [("09:09", "buy")]
    assert entries(DAY, {"09:05": 2, "09:10": 2}) == [("09:04", "buy"), ("09:09", "buy")]


def test_missing_6c_entry_bar_blocks_that_t_only() -> None:
    assert entries(DAY, {"09:05": 2, "09:10": 2}, cad_skip=[hm(9, 4)]) == [("09:09", "buy")]


def test_missing_mcl_bar_at_t_minus_1_blocks_t_and_the_next_block() -> None:
    """09:04 missing: r_09:05 (09:04 is c1) and r_09:10 (09:04 is c6) undefined."""
    out = entries(DAY, {"09:05": 2, "09:10": 2, "09:15": 2}, mcl_skip=[hm(9, 4)])
    assert out == [("09:14", "buy")]


def test_mcl_bar_arriving_late_is_never_used() -> None:
    """MCL has no bar at 09:04 and a bar one minute later (09:05) at the 09:04 level: never a
    forward fill or a late substitute, so no entry at 09:05 or 09:10."""
    late = [(hm(9, 5), B_MCL + 2)]
    out = entries(DAY, {"09:05": 2, "09:10": 2}, mcl_skip=[hm(9, 4)], mcl_extra=late)
    assert out == []


def test_missing_mcl_bar_at_t_minus_6_blocks_t() -> None:
    assert entries(DAY, {"09:05": 2}, mcl_skip=[hm(8, 59)]) == []


def test_a_previous_dates_t_minus_6_bar_is_never_used() -> None:
    """d's 08:59 MCL bar is missing; the previous date's 08:59 bar carries d's instrument_id and
    a level 10 ticks below: r_09:05 stays undefined (no stale value), so no entry at 09:05.
    Control: d's own 08:59 bar at that level is read (a sell at 09:00, a buy at 09:05).
    References (5, 5, 45) x 20, n ~ 1100."""
    rich = ((5, 5, 45),) * 20
    refs = refs_of(DAY)

    def scenario(own: bool) -> list[tuple[str, str]]:
        bars = [rb for rb in ref_bars(refs, rich) if not (
            rb[1].trade_date == refs[-1] and ct(rb[1].ts_event_ns).time() == time(8, 59))]
        bars.append(mk_bar("MCL", refs[-1], hm(8, 59), B_MCL - 10))
        bars += trade_bars(DAY, mcl_skip=[] if own else [hm(8, 59)],
                           mcl_extra=[(hm(8, 59), B_MCL - 10)] if own else [])
        if own:
            bars = [rb for rb in bars if not (
                rb[1].trade_date == DAY and rb[0] == "MCL" and rb[1].close == price("MCL", B_MCL)
                and ct(rb[1].ts_event_ns).time() == time(8, 59))]
        out = drive(mk(), sorted(bars, key=lambda rb: rb[1].ts_event_ns))
        return [(i[1], i[3]) for i in out]

    assert scenario(own=False) == []
    assert scenario(own=True) == [("08:59", "sell"), ("09:04", "buy")]  # r_09:00 < 0, r_09:05 > 0


def test_bars_are_identified_by_ct_date_not_trade_date_alone() -> None:
    """K7-L-01: a 6C bar opening 09:04 on CT date d + 1 but carrying trade_date d is not the 6C
    bar at 09:04 of d: d's references are complete and d + 1's MCL block is a big move, yet no
    entry."""
    day = DAY
    nxt = OILCAD_DATES[OILCAD_DATES.index(day) + 1]
    bars = oil_bars(day, cad_to=hm(9, 0)) + [
        rb for rb in trade_bars(nxt, {"09:05": 2}) if rb[0] == "MCL"]
    wrong = mk_bar("6C", nxt, hm(9, 4), B_CAD, trade_day=day)
    out = drive(mk(), sorted([*bars, wrong], key=lambda rb: rb[1].ts_event_ns))
    assert out == []
    right = mk_bar("6C", day, hm(9, 4), B_CAD)  # control: the same move on d itself trades
    bars_d = oil_bars(day, {"09:05": 2}, cad_to=hm(9, 0))
    out = drive(mk(), sorted([*bars_d, right], key=lambda rb: rb[1].ts_event_ns))
    assert [(i[0], i[1], i[3]) for i in out] == [(day, "09:04", "buy")]


def test_an_mcl_bar_is_read_on_its_own_ct_date_only() -> None:
    """S0.4: d's 09:04 MCL bar is missing; an MCL bar opening 09:04 on CT date d + 1 but
    labelled trade_date d (with a big move over d's 08:59) is not d's bar at 09:04, so it closes
    no block, and the 6C bar of d + 1 at 09:04 gets no entry."""
    day = DAY
    nxt = OILCAD_DATES[OILCAD_DATES.index(day) + 1]
    wrong = mk_bar("MCL", nxt, hm(9, 4), B_MCL + 10, trade_day=day)
    cad = [mk_bar("6C", nxt, m, B_CAD) for m in range(hm(9, 0), hm(9, 10))]
    bars = oil_bars(day, mcl_skip=[hm(9, 4)], cad_to=hm(9, 0)) + [wrong, *cad]
    assert drive(mk(), sorted(bars, key=lambda rb: rb[1].ts_event_ns)) == []


# ----------------------------------------------------------------------- the C6 skip ----
def test_c6_skips_09_30_on_a_standard_wpsr_date_and_not_09_35() -> None:
    assert entries(WPSR_DAY, {"09:30": 2, "09:35": 2}) == [("09:34", "buy")]


def test_09_30_on_a_non_wpsr_date_is_not_skipped() -> None:
    assert entries(PLAIN_DAY, {"09:30": 2}) == [("09:29", "buy")]


def test_c6_skips_13_00_on_an_fomc_date() -> None:
    assert entries(FOMC_DAY, {"13:00": 2, "13:05": 2}) == [("13:04", "buy")]


def test_c6_skips_11_00_on_holiday_week_wpsr_dates_including_the_e4_dropped_row() -> None:
    assert entries(HOLIDAY_WPSR_DAY, {"11:00": 2, "11:05": 2}) == [("11:04", "buy")]
    assert entries(DROPPED_WPSR_DAY, {"11:00": 2}) == []  # R-1b-1


def test_c6_tests_the_fill_minute_t_on_the_6c_root(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, int]] = []

    def spy(root: str, t_ns: int) -> bool:
        calls.append((root, t_ns))
        return False

    monkeypatch.setattr(oilcad, "in_guard", spy)
    assert entries(DAY, {"09:05": 2}) == [("09:04", "buy")]
    assert calls == [("6C", ns_at(DAY, hm(9, 5)))]


def test_a_skipped_decision_leaves_later_decisions_alone(monkeypatch: pytest.MonkeyPatch
                                                         ) -> None:
    monkeypatch.setattr(oilcad, "in_guard", lambda root, t_ns: True)
    assert entries(DAY, {"09:05": 2, "09:10": 2}) == []
    monkeypatch.setattr(oilcad, "in_guard",
                        lambda root, t_ns: t_ns == ns_at(DAY, hm(9, 5)))
    assert entries(DAY, {"09:05": 2, "09:10": 2}) == [("09:09", "buy")]


# ------------------------------------------------------------- flat-only and the exit ----
def _acct_from(ts_from: int, position: int = 0, pending: int = 0) -> AccountFn:
    held, flat = account(("6C",), position, pending), account(("6C",))
    return lambda ts: held if ts >= ts_from else flat


@pytest.mark.parametrize("position,pending", [(1, 0), (-1, 0), (0, 1), (0, -1)])
def test_no_entry_while_a_position_or_a_pending_order_exists(position: int, pending: int
                                                            ) -> None:
    acct = _acct_from(ns_at(DAY, hm(9, 4)), position=0, pending=pending)
    if position:  # a position seen first at 09:04 (T_e = 09:04): no entry, and no exit yet
        acct = _acct_from(ns_at(DAY, hm(9, 4)), position=position)
    out = entries(DAY, {"09:05": 2}, acct=acct, cad_to=hm(9, 10))
    assert out == []


def test_exit_on_the_first_6c_bar_at_t_e_plus_14_resent_while_not_pending() -> None:
    """T_e = 09:05 (the account first shows +1 there): no exit before 09:19; an exit intent on
    09:19 and, refused (still not pending), again on 09:20; pending at 09:21: nothing."""
    pend_from = ns_at(DAY, hm(9, 21))
    held, pend = account(("6C",), 1), account(("6C",), 1, -1)
    flat = account(("6C",))

    def acct(ts: int) -> MemberAccountView:
        if ts < ns_at(DAY, hm(9, 5)):
            return flat
        return pend if ts >= pend_from else held

    out = drive(mk(), trade_bars(DAY, cad_to=hm(9, 25)), acct)
    assert [(i[1], i[3], i[4]) for i in out] == [("09:19", "sell", 1), ("09:20", "sell", 1)]


def test_exit_of_a_short_buys_the_whole_position() -> None:
    acct = _acct_from(ns_at(DAY, hm(9, 5)), position=-1)
    out = drive(mk(), trade_bars(DAY, cad_to=hm(9, 19)), acct)
    assert [(i[1], i[3], i[4]) for i in out] == [("09:19", "buy", 1)]


def test_every_exit_closes_the_whole_position() -> None:
    acct = _acct_from(ns_at(DAY, hm(9, 5)), position=2)
    out = drive(mk(), trade_bars(DAY, cad_to=hm(9, 19)), acct)
    assert [(i[1], i[3], i[4]) for i in out] == [("09:19", "sell", 2)]


def test_missing_exit_bar_goes_on_the_first_later_present_bar() -> None:
    acct = _acct_from(ns_at(DAY, hm(9, 5)), position=1)
    out = drive(mk(), trade_bars(DAY, cad_skip=[hm(9, 19), hm(9, 20)], cad_to=hm(9, 21)), acct)
    assert [(i[1], i[3]) for i in out] == [("09:21", "sell")]


# ---------------------------------------------------------------------- engine level ----
def run_day(steps: Mapping[str, int], *, flatten_at: Iterable[int] = (),
            rules: StageERules | None = None, **kw: Any) -> EngineResult:
    m = mk()
    bars = oil_bars(DAY, steps, **kw)
    rules = rules_of(m, [DAY]) if rules is None else rules
    return engine(m, bars, rules, frozenset(ns_at(DAY, x) for x in flatten_at))


def test_engine_fills_6c_at_t_and_exits_at_t_e_plus_15_with_no_mcl_position() -> None:
    res = run_day({"09:05": 2})
    assert fills(res) == [(DAY, "09:05", "6C", "buy", "strategy"),
                          (DAY, "09:20", "6C", "sell", "strategy")]
    assert intent_roots(res) == {"6C"}
    assert [f.qty for f in res.events(Fill)] == [1, 1]


def test_engine_sell_side() -> None:
    assert fills(run_day({"09:05": -2})) == [(DAY, "09:05", "6C", "sell", "strategy"),
                                             (DAY, "09:20", "6C", "buy", "strategy")]


def test_engine_t_e_is_the_actual_fill_when_the_6c_bar_at_t_is_missing() -> None:
    res = run_day({"09:05": 2}, cad_skip=[hm(9, 5)])
    assert fills(res) == [(DAY, "09:06", "6C", "buy", "strategy"),
                          (DAY, "09:21", "6C", "sell", "strategy")]


def test_engine_missing_exit_bar_exits_on_the_first_later_bar() -> None:
    res = run_day({"09:05": 2}, cad_skip=[hm(9, 19)])
    assert fills(res) == [(DAY, "09:05", "6C", "buy", "strategy"),
                          (DAY, "09:21", "6C", "sell", "strategy")]


def test_engine_spacing_exit_view_blocks_t_e_plus_15_next_entry_t_e_plus_20() -> None:
    """Big moves at 09:05, 09:20 (= t_e + 15, decided on the exit's 09:19 view: no entry) and
    09:25 (= t_e + 20: an entry)."""
    res = run_day({"09:05": 2, "09:20": 2, "09:25": 2})
    assert fills(res) == [(DAY, "09:05", "6C", "buy", "strategy"),
                          (DAY, "09:20", "6C", "sell", "strategy"),
                          (DAY, "09:25", "6C", "buy", "strategy"),
                          (DAY, "09:40", "6C", "sell", "strategy")]


def test_engine_late_fill_holds_the_position_through_the_next_decision() -> None:
    """6C bars 09:05..09:08 missing: the 09:05 entry fills at 09:09 (T_e = 09:09), so the 09:10
    decision (its 09:09 view) sees a position: no entry; the exit fills at 09:24."""
    res = run_day({"09:05": 2, "09:10": 2}, cad_skip=list(range(hm(9, 5), hm(9, 9))))
    assert fills(res) == [(DAY, "09:09", "6C", "buy", "strategy"),
                          (DAY, "09:24", "6C", "sell", "strategy")]


def test_engine_closure_leaves_the_account_flat_and_later_decisions_apply() -> None:
    """A bar flatten flag on the 09:10 6C bar: the engine closes at 09:11; the member sends no
    exit; the 09:20 decision enters again and exits at 09:35."""
    res = run_day({"09:05": 2, "09:20": 2}, flatten_at=[hm(9, 10)])
    assert fills(res) == [(DAY, "09:05", "6C", "buy", "strategy"),
                          (DAY, "09:11", "6C", "sell", "forced_flatten"),
                          (DAY, "09:20", "6C", "buy", "strategy"),
                          (DAY, "09:35", "6C", "sell", "strategy")]


def test_engine_nothing_after_the_13_40_fill() -> None:
    res = run_day({"13:25": 2}, mcl_extra=[(hm(13, 29), B_MCL + 10)], cad_to=hm(14, 30))
    assert fills(res) == [(DAY, "13:25", "6C", "buy", "strategy"),
                          (DAY, "13:40", "6C", "sell", "strategy")]
    assert max(r.decision_ts_ns for r in res.events(IntentRecord)) <= ns_at(DAY, hm(13, 40))


def test_engine_refuses_on_a_signal_leg_roll_blackout_date_only() -> None:
    """V16(a) end to end: an MCL roll blackout on the trade date (6C clean). With the rules the
    runner builds (member_window: the union removes the date) the open is refused as outside
    the window; with the date kept in the window and the union as blackout, by name
    engine_roll_blackout; with no blackout it fills."""
    m = mk()
    bars = oil_bars(DAY, {"09:05": 2})
    rules, mw = runner_rules(m, bars, {"MCL": [DAY]})
    assert DAY not in mw.dates and DAY in mw.blackout_union
    assert DAY in mw.excluded["roll_blackout_any_leg"]
    res = engine(m, bars, rules)
    assert fills(res) == [] and refusals(res) == ["engine_not_a_window_date"]
    res = engine(mk(), bars, rules_of(m, [DAY], blackout=mw.blackout_union))
    assert fills(res) == [] and refusals(res) == ["engine_roll_blackout"]
    clean, mw2 = runner_rules(m, bars, {})
    assert DAY in mw2.dates
    assert fills(engine(mk(), bars, clean))[0] == (DAY, "09:05", "6C", "buy", "strategy")


def test_engine_a_6c_roll_blackout_also_refuses() -> None:
    m = mk()
    bars = oil_bars(DAY, {"09:05": 2})
    rules, mw = runner_rules(m, bars, {"6C": [DAY]})
    assert DAY not in mw.dates
    assert fills(engine(m, bars, rules)) == []


def test_reference_dates_include_roll_blackout_dates() -> None:
    """K8-L-04: a reference date that is a roll-blackout date still gives its values (the bars
    are delivered; only opens are refused there): with one blackout reference date, z = 2.0
    still trades."""
    m = mk()
    bars = oil_bars(DAY, {"10:05": 1})
    rules = rules_of(m, [DAY, *refs_of(DAY)], blackout=[refs_of(DAY)[3]])
    assert fills(engine(m, bars, rules))[0] == (DAY, "10:05", "6C", "buy", "strategy")


def test_shift_helper_moves_a_clock_time() -> None:
    assert oilcad.shift(time(8, 5), -6) == time(7, 59)
    assert oilcad.shift(time(13, 25), 16) == time(13, 41)
    assert timedelta(minutes=oilcad.EXIT_AFTER_FILL_MIN) == timedelta(minutes=14)
