"""Stage E.9 K8-flight-01 of MemberCoder-A, part 1: declaration, block clock, r_k, Q(d), the
trigger, warm-up and reference dates (reports/stage_e9_member_specs.md section 1, S0.1-S0.12;
readings K8-L-02, K8-L-04, K8-L-05, K8-L-09, K8-L-10, K4-L-09). Exits, C6 and missing bars are in
tests/test_k8_members_flight_exits.py; engine-level tests in tests/test_k8_members_flight_engine.py.
Both import this file's kit.

Synthetic bars only, fed straight to on_minute (no bar file is read). MES closes are integer
ticks of 0.25 around B = 20000 (5000.00); MGC sits at 30000 ticks of 0.10 (3000.0). The kit feeds
one view per block bar (08:29, 08:34, ..., 14:54): a path of closes p_0..p_j gives
r_k = (p_k - p_{k-1}) / p_{k-1}, k = 1..j. A "dip" of x ticks at k (p_k = B - x, the rest B) gives
r_k = -x/B, r_{k+1} = x/(B - x) and r = 0 elsewhere. The reference kit puts dips of 1..10 ticks on
the first ten reference dates, so the negative values are -10/B < ... < -1/B and
Q(d) = -(11 - m)/B: m = 6 at n = 1,200 (-5/B), 7 at 1,201 (-4/B), 8 at 1,540 (-3/B).
"""

from __future__ import annotations

import shutil
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, date, datetime, time
from fractions import Fraction
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pytest

from rules.products import product
from rules.xfa_rules import Phase, Status
from screening.stage_e_freeze import (
    MemberDecl,
    check_cluster_sources,
    check_member_source,
    load_cluster_freeze,
    verify_cluster_code,
    write_cluster_freeze,
)
from screening.stage_e_frozen import load_frozen_tables
from strategy.interface import Bar
from strategy.members.k8 import _releases as rel
from strategy.members.k8 import flight
from strategy.members.k8._calendar import FLIGHT_DATES
from strategy.members.k8.flight import (
    FlightToGold,
    block_return,
    compare,
    decision_times,
    reference_dates,
    threshold,
    triggers,
)
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    StageEMember,
    TradingInterval,
)

REPO = Path(__file__).resolve().parents[1]
K8_DIR = REPO / "strategy" / "members" / "k8"
CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
B = 20000  # MES base close in ticks of 0.25
G = 30000  # MGC price in ticks of 0.10
MES_ID, MGC_ID = 4242, 777
# the block bars: 08:29 (start of k = 1), then the bar at t_k - 1 = 08:34 + 5(k - 1), k = 1..77
BLOCK_BARS: tuple[int, ...] = (8 * 60 + 29, *(8 * 60 + 34 + 5 * j for j in range(77)))
DAY = date(2025, 6, 17)  # a Tuesday in FLIGHT_DATES, no MGC release on the grid
FOMC = date(2025, 6, 18)  # an FOMC date: MGC guarded at [13:00, 13:02) CT
DIPS = tuple(range(1, 11))  # dips of 1..10 ticks on the first ten reference dates

Out = dict[int, list]  # minute of day -> the member's non-empty outputs at that view


def hm(h: int, m: int) -> int:
    return h * 60 + m


def end_bar(k: int) -> int:
    """The minute of day of the bar at t_k - 1."""
    return BLOCK_BARS[k]


def ns_at(day: date, minute: int) -> int:
    local = datetime.combine(day, time(*divmod(minute, 60)), tzinfo=CT)
    return int(local.astimezone(UTC).timestamp()) * NS


def bar(root: str, day: date, minute: int, close: int, iid: int,
        trade_date: date | None = None) -> Bar:
    """A flat bar (open = high = low = close) of ``root`` at ``minute`` of CT date ``day``."""
    px = float(close * product(root).vendor_tick)
    return Bar(ns_at(day, minute), px, px, px, px, 1, iid, f"{root}U5",
               day if trade_date is None else trade_date, False, False, None, False, False, 0,
               False)


def mes(day: date, minute: int, close: int = B, iid: int = MES_ID, **kw: Any) -> Bar:
    return bar("MES", day, minute, close, iid, **kw)


def mgc(day: date, minute: int, iid: int = MGC_ID, **kw: Any) -> Bar:
    return bar("MGC", day, minute, G, iid, **kw)


def account(position: int = 0, pending: int = 0) -> MemberAccountView:
    return MemberAccountView(Phase.XFA, Status.ACTIVE, None, 0, 0, {"MGC": position},
                             {"MGC": pending}, {"MGC": None}, {"MGC": 0})


def call(member: FlightToGold, day: date, minute: int, *, mes_bar: Bar | None = None,
         mgc_bar: Bar | None = None, position: int = 0, pending: int = 0) -> list:
    view = MinuteView(ns_at(day, minute), {"MGC": mgc_bar, "MES": mes_bar})
    return list(member.on_minute(view, account(position, pending)))


def dip_path(dips: Mapping[int, int] | None = None, n_values: int = 77) -> list[int]:
    """Closes p_0..p_n of the block bars: B everywhere, B - x at index k for each dip (k, x)."""
    path = [B] * (n_values + 1)
    for k, x in (dips or {}).items():
        path[k] = B - x
    return path


def feed(member: FlightToGold, day: date, path: Sequence[int], *, mes_skip: Iterable[int] = (),
         mgc_skip: Iterable[int] = (), ids: Mapping[int, int] | None = None,
         mgc_trade_date: date | None = None) -> Out:
    """One view per block bar (index i of ``path``) with the MES bar (unless skipped) and the
    MGC bar (unless skipped), a flat account; the outputs by minute."""
    out: Out = {}
    mes_skip, mgc_skip, ids = set(mes_skip), set(mgc_skip), ids or {}
    for i, close in enumerate(path):
        minute = BLOCK_BARS[i]
        m = None if i in mes_skip else mes(day, minute, close, ids.get(i, MES_ID))
        g = None if i in mgc_skip else mgc(day, minute, trade_date=mgc_trade_date)
        got = call(member, day, minute, mes_bar=m, mgc_bar=g)
        if got:
            out[minute] = got
    return out


def prepare(member: FlightToGold, day: date, values: int | Sequence[int] = 77,
            dips: Sequence[int] = DIPS) -> tuple[date, ...]:
    """Feed the 20 reference dates of ``day`` (the first one is the first bar of the run): date i
    gives values[i] defined r values, with a dip of dips[i] ticks at k = 10 when i < len(dips)."""
    refs = reference_dates(day)
    assert len(refs) == 20
    counts = [values] * len(refs) if isinstance(values, int) else list(values)
    for i, ref in enumerate(refs):
        dip = {10: dips[i]} if i < len(dips) and dips[i] else {}
        assert not feed(member, ref, dip_path(dip, counts[i]))  # warm-up: never a trade
    return refs


def entries(out: Out) -> list[tuple[int, str, str, int]]:
    """(minute, root, side, quantity) of every intent."""
    return [(m, i.root, i.side, i.quantity) for m, got in sorted(out.items()) for i in got
            if isinstance(i, LegIntent)]


def buy_at(minute: int) -> list[tuple[int, str, str, int]]:
    return [(minute, "MGC", "buy", 1)]


def ready(day: date = DAY, **kw: Any) -> FlightToGold:
    member = flight.make_h30()
    prepare(member, day, **kw)
    return member


# ------------------------------------------------------------- declaration and windows ----
@pytest.mark.parametrize("name", ["flight.py", "_calendar.py", "_releases.py"])
def test_the_files_pass_the_freeze_static_check(name: str) -> None:
    rel = f"strategy/members/k8/{name}"
    assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K8") == []


def test_declarations_names_legs_and_factories() -> None:
    h30, heod = flight.make_h30(), flight.make_heod()
    assert isinstance(h30, StageEMember) and isinstance(heod, StageEMember)
    assert (h30.name, heod.name) == ("K8-flight-01 H30 MGC", "K8-flight-01 HEOD MGC")
    for m in (h30, heod):
        assert m.legs == (LegSpec("MGC", True), LegSpec("MES", False))
    assert flight.make_h30() is not flight.make_h30()
    assert sorted(n for n in vars(flight) if n.startswith("make_")) == ["make_h30", "make_heod"]
    with pytest.raises(ValueError, match="variant"):
        FlightToGold("H60")


def test_trading_windows_are_the_s0_12_intervals() -> None:
    for m in (flight.make_h30(), flight.make_heod()):
        assert m.trading_windows == {"MGC": (TradingInterval(time(8, 34), time(15, 6)),),
                                     "MES": (TradingInterval(time(8, 29), time(14, 55)),)}


def test_the_entry_size_is_the_frozen_q_c() -> None:
    q_c = load_frozen_tables().vehicles["MGC"].q_c
    assert q_c == 1
    member = ready()
    assert entries(feed(member, DAY, dip_path({3: 5}))) == [(end_bar(3), "MGC", "buy", q_c)]


def test_the_declarations_freeze_and_verify_under_tmp_path(tmp_path: Path) -> None:
    members_dir = tmp_path / "strategy" / "members"
    (members_dir / "k8").mkdir(parents=True)
    (members_dir / "__init__.py").write_bytes(b"")
    (members_dir / "k8" / "__init__.py").write_bytes(b"")
    for name in ("flight.py", "_calendar.py", "_releases.py"):
        shutil.copyfile(K8_DIR / name, members_dir / "k8" / name)
    check_cluster_sources("K8", tmp_path)
    legs = (LegSpec("MGC", True), LegSpec("MES", False))
    decls = [MemberDecl("K8-flight-01 H30 MGC", 1, "strategy.members.k8.flight", "make_h30", legs),
             MemberDecl("K8-flight-01 HEOD MGC", 2, "strategy.members.k8.flight", "make_heod",
                        legs)]
    write_cluster_freeze("K8", decls, tmp_path)
    freeze = load_cluster_freeze("K8", tmp_path)
    verify_cluster_code(freeze)
    assert freeze.member("K8-flight-01 HEOD MGC").ordinal == 2


# ---------------------------------------------------------------------- block clock ----
def test_decision_times_are_0835_to_1455_every_5_minutes() -> None:
    times = decision_times()
    assert len(times) == 77 and times[0] == time(8, 35) and times[-1] == time(14, 55)
    assert all(hm(t.hour, t.minute) - hm(s.hour, s.minute) == 5
               for s, t in zip(times, times[1:], strict=False))
    assert time(15, 0) not in times


def test_k1_reads_the_0829_and_0834_bars() -> None:
    member = ready()
    assert entries(feed(member, DAY, dip_path({1: 5}))) == buy_at(hm(8, 34))
    member = ready()  # the 08:29 bar missing: r_1 undefined, no trigger at 08:35
    assert entries(feed(member, DAY, dip_path({1: 5}), mes_skip={0})) == []


def test_a_bar_at_0830_is_not_the_start_bar_of_k1() -> None:
    member = ready()
    call(member, DAY, hm(8, 30), mes_bar=mes(DAY, hm(8, 30), B))  # 08:29 missing
    out = call(member, DAY, hm(8, 34), mes_bar=mes(DAY, hm(8, 34), B - 5),
               mgc_bar=mgc(DAY, hm(8, 34)))
    assert out == []
    member = ready()  # control: the same dip after an 08:29 bar triggers
    call(member, DAY, hm(8, 29), mes_bar=mes(DAY, hm(8, 29), B))
    out = call(member, DAY, hm(8, 34), mes_bar=mes(DAY, hm(8, 34), B - 5),
               mgc_bar=mgc(DAY, hm(8, 34)))
    assert [(i.root, i.side) for i in out] == [("MGC", "buy")]


def test_the_last_block_ends_at_1455_and_there_is_no_block_at_1500() -> None:
    member = ready()
    assert entries(feed(member, DAY, dip_path({77: 5}))) == buy_at(hm(14, 54))
    member = ready()
    feed(member, DAY, dip_path())
    out = call(member, DAY, hm(14, 59), mes_bar=mes(DAY, hm(14, 59), B - 50),
               mgc_bar=mgc(DAY, hm(14, 59)))
    assert out == []  # 14:54 -> 14:59 would be a block ending 15:00: none


def test_every_block_k_triggers_at_its_own_bar() -> None:
    for k in (2, 30, 54, 76):
        member = ready()
        assert entries(feed(member, DAY, dip_path({k: 5}))) == buy_at(end_bar(k)), k


# ------------------------------------------------------------------- r_k (exact) ----
def test_block_return_is_the_tick_ratio_and_needs_c6_positive() -> None:
    assert block_return(20000, 19990) == (-10, 20000)
    assert Fraction(*block_return(20000, 19990)) == Fraction(-1, 2000)
    assert block_return(0, 5) is None and block_return(-4, 5) is None
    assert block_return(1, 5) == (4, 1)


def test_compare_and_trigger_are_exact_beyond_float() -> None:
    near, q = (-(10**17) - 1, 10**17), (-1, 1)  # equal as floats, not as rationals
    assert float(near[0]) / near[1] == float(q[0]) / q[1]
    assert compare(near, q) == -1 and compare(q, near) == 1 and compare(q, (-2, 2)) == 0
    assert triggers(near, q)
    assert not triggers((-(10**17) + 1, 10**17), q)
    for a, b in (((-3, 7), (-2, 5)), ((1, 3), (2, 6)), ((-5, 20000), (-10, 40000))):
        fa, fb = Fraction(*a), Fraction(*b)
        assert compare(a, b) == (fa > fb) - (fa < fb)


def test_r_equal_to_q_in_another_form_triggers() -> None:
    """Q(d) = -3/B (n = 1,540); r_k = -6/(2B) on d is the same rational: the trigger fires."""
    member = ready()
    path = [B] * 2 + [2 * B] + [2 * B - 6] * 75  # r_2 = +1, r_3 = -6/2B, then 0
    assert entries(feed(member, DAY, path)) == buy_at(end_bar(3))


def test_an_mes_roll_inside_a_block_is_no_trigger_and_later_blocks_trigger() -> None:
    member = ready()
    ids = {i: MES_ID + 1 for i in range(3, 78)}  # the id changes between the bars of block 3
    assert entries(feed(member, DAY, dip_path({3: 5}), ids=ids)) == []
    member = ready()
    assert entries(feed(member, DAY, dip_path({3: 5, 6: 5}), ids=ids)) == buy_at(end_bar(6))


def test_instrument_ids_are_compared_within_mes_only() -> None:
    member = ready()  # the MGC bar carries another id than MES: irrelevant
    assert MGC_ID != MES_ID
    assert entries(feed(member, DAY, dip_path({3: 5}))) == buy_at(end_bar(3))


def test_a_bar_whose_trade_date_is_not_its_ct_date_is_not_a_block_bar() -> None:
    """K8-L-02: bars on CT date DAY stamped with trade date 2025-06-18 (whose reference set the
    kit also fills) are no block bars of either date."""
    nxt = FLIGHT_DATES[FLIGHT_DATES.index(DAY) + 1]
    member = ready()
    call(member, DAY, hm(8, 29), mes_bar=mes(DAY, hm(8, 29), B, trade_date=nxt))
    out = call(member, DAY, hm(8, 34), mes_bar=mes(DAY, hm(8, 34), B - 5, trade_date=nxt),
               mgc_bar=mgc(DAY, hm(8, 34), trade_date=nxt))
    assert out == []
    member = ready()  # control: the same bars stamped DAY trigger
    call(member, DAY, hm(8, 29), mes_bar=mes(DAY, hm(8, 29), B))
    out = call(member, DAY, hm(8, 34), mes_bar=mes(DAY, hm(8, 34), B - 5),
               mgc_bar=mgc(DAY, hm(8, 34)))
    assert [(i.root, i.side) for i in out] == [("MGC", "buy")]


# ----------------------------------------------------------------------- Q(d) ----
def _vals(*xs: int, zeros: int = 0) -> list[tuple[int, int]]:
    return [(-x, B) for x in xs] + [(0, B)] * zeros


def test_threshold_m_and_the_value_floor() -> None:
    assert threshold(_vals(*DIPS, zeros=1189)) is None  # n = 1,199
    assert threshold(_vals(*DIPS, zeros=1190)) == (-5, B)  # n = 1,200: m = 6
    assert threshold(_vals(*DIPS, zeros=1191)) == (-4, B)  # n = 1,201: m = 7
    assert threshold(_vals(*DIPS, zeros=1390)) == (-4, B)  # n = 1,400: m = 7
    assert threshold(_vals(*DIPS, zeros=1391)) == (-3, B)  # n = 1,401: m = 8
    assert threshold(_vals(*DIPS, zeros=1530)) == (-3, B)  # n = 1,540: m = 8


def test_threshold_counts_duplicates() -> None:
    values = _vals(10, 10, 9, 8, 7, 6, 5, 4, 3, 2, zeros=1530)  # n = 1,540, m = 8
    assert threshold(values) == (-4, B)
    assert threshold(list(reversed(values))) == (-4, B)


@pytest.mark.parametrize(("n", "m"), [(1200, 6), (1201, 7), (1400, 7), (1401, 8), (1540, 8)])
def test_m_is_ceil_of_n_over_200(n: int, m: int) -> None:
    ladder = [(-(n - i), B) for i in range(n)]  # all distinct: the m-th smallest is -(n - m + 1)
    assert threshold(ladder) == (-(n - m + 1), B)


def test_member_n_1199_is_no_trade_and_n_1200_trades() -> None:
    member = ready(values=[59] + [60] * 19)
    assert entries(feed(member, DAY, dip_path({3: 50}))) == []
    member = ready(values=60)  # n = 1,200: Q = -5/B
    assert entries(feed(member, DAY, dip_path({3: 5}))) == buy_at(end_bar(3))
    member = ready(values=60)
    assert entries(feed(member, DAY, dip_path({3: 4}))) == []


def test_member_m_at_1201_and_1540() -> None:
    member = ready(values=[61] + [60] * 19)  # n = 1,201: m = 7, Q = -4/B
    assert entries(feed(member, DAY, dip_path({3: 4}))) == buy_at(end_bar(3))
    member = ready(values=[61] + [60] * 19)
    assert entries(feed(member, DAY, dip_path({3: 3}))) == []
    member = ready(values=77)  # n = 1,540: m = 8, Q = -3/B
    assert entries(feed(member, DAY, dip_path({3: 3}))) == buy_at(end_bar(3))
    member = ready(values=77)
    assert entries(feed(member, DAY, dip_path({3: 2}))) == []


def test_member_counts_duplicate_reference_values() -> None:
    dips = (10, 10, 9, 8, 7, 6, 5, 4, 3, 2)  # n = 1,540, m = 8: Q = -4/B (not -3/B)
    member = ready(dips=dips)
    assert entries(feed(member, DAY, dip_path({3: 4}))) == buy_at(end_bar(3))
    member = ready(dips=dips)
    assert entries(feed(member, DAY, dip_path({3: 3}))) == []


def _undefined_first_reference() -> FlightToGold:
    """The first reference date carries a -50/B dip but a new MES id on every bar (no defined
    r_k); dates 2..10 carry the dips 2..10."""
    member = flight.make_h30()
    for i, ref in enumerate(reference_dates(DAY)):
        dip = {10: 50 if i == 0 else DIPS[i]} if i < len(DIPS) else {}
        ids = {j: MES_ID + j for j in range(78)} if i == 0 else None
        feed(member, ref, dip_path(dip), ids=ids)
    return member


def test_undefined_reference_computations_are_not_values() -> None:
    """n = 19 x 77 = 1,463, m = 8: Q = -3/B from the dips -10..-2; counting the undefined -50/B
    would give -4/B."""
    assert entries(feed(_undefined_first_reference(), DAY, dip_path({3: 3}))) == buy_at(end_bar(3))
    assert entries(feed(_undefined_first_reference(), DAY, dip_path({3: 2}))) == []


# ---------------------------------------------------------------------- trigger ----
def test_trigger_needs_r_negative_even_at_or_below_q() -> None:
    member = ready(dips=())  # every reference value 0: Q = 0
    assert entries(feed(member, DAY, dip_path())) == []  # r = 0 <= Q, not < 0
    member = ready(dips=())
    assert entries(feed(member, DAY, dip_path({3: 1}))) == buy_at(end_bar(3))


def _positive_q() -> FlightToGold:
    member = flight.make_h30()
    for ref in reference_dates(DAY):  # every reference value 1/(B + k - 1) > 0: Q = 1/(B + 69)
        feed(member, ref, [B + j for j in range(78)])
    return member


def test_a_positive_q_never_triggers_a_non_negative_r() -> None:
    assert entries(feed(_positive_q(), DAY, dip_path())) == []  # every r = 0 <= Q
    small = [B + 100] * 3 + [B + 101] * 75  # r_3 = 1/(B + 100) <= Q, r = 0 elsewhere
    assert entries(feed(_positive_q(), DAY, small)) == []
    assert entries(feed(_positive_q(), DAY, dip_path({3: 1}))) == buy_at(end_bar(3))


# ------------------------------------------------------------- warm-up, references ----
def test_warm_up_the_20th_date_does_not_trade_and_the_21st_does() -> None:
    refs = reference_dates(DAY)
    member = flight.make_h30()  # the run's first bar is on refs[1]: refs[1..19] and DAY
    for i, ref in enumerate(refs[1:], start=1):
        dip = {10: DIPS[i]} if i < len(DIPS) else {}
        out = feed(member, ref, dip_path({**dip, 3: 50} if ref == refs[-1] else dip))
        assert entries(out) == [], ref  # eligible dates 1..19 of the run: warm-up
    out = feed(member, DAY, dip_path({3: 50}))
    assert entries(out) == []  # DAY is the 20th eligible date of this run: still warm-up
    after = FLIGHT_DATES[FLIGHT_DATES.index(DAY) + 1]
    assert entries(feed(member, after, dip_path({3: 50}))) == buy_at(end_bar(3))  # the 21st


def test_the_21st_date_trades_when_the_run_starts_on_the_first_reference() -> None:
    member = ready()
    assert entries(feed(member, DAY, dip_path({3: 5}))) == buy_at(end_bar(3))


def test_fewer_than_20_reference_dates_at_the_tables_start_is_no_trade() -> None:
    """The run starts on FLIGHT_DATES[0] (2019-05-01): the 20th date has 19 reference dates
    (n = 1,463, all after the first bar) and does not trade; the 21st does."""
    member = flight.make_h30()
    for i, ref in enumerate(FLIGHT_DATES[:19]):
        dip = {10: DIPS[i]} if i < len(DIPS) else {}
        assert entries(feed(member, ref, dip_path(dip))) == [], ref
    twentieth, twenty_first = FLIGHT_DATES[19], FLIGHT_DATES[20]
    assert len(reference_dates(twentieth)) == 19
    assert entries(feed(member, twentieth, dip_path({3: 50}))) == []
    assert entries(feed(member, twenty_first, dip_path({3: 50}))) == buy_at(end_bar(3))


def test_ticks_round_a_near_grid_float_to_the_nearest_tick() -> None:
    """The engine accepts prices within 1e-6 of the tick grid; r_k reads them as the nearest
    integer tick (4997.499999999999 is 19,990 ticks of 0.25, not 19,989)."""
    tick = product("MES").vendor_tick
    assert flight.to_ticks(4997.5 - 1e-12, tick) == 19990
    assert flight.to_ticks(4997.5 + 1e-12, tick) == 19990
    assert flight.to_ticks(4997.5, tick) == 19990


def test_reference_dates_are_the_20_flight_dates_before_d() -> None:
    d = date(2025, 12, 1)
    refs = reference_dates(d)
    assert len(refs) == 20 and refs[-1] == date(2025, 11, 26)
    assert date(2025, 11, 28) not in refs and date(2025, 11, 27) not in refs
    assert all(r in FLIGHT_DATES for r in refs)


def test_a_non_full_date_is_skipped_as_a_reference_and_as_d() -> None:
    """2025-11-28 (early halt) is not in FLIGHT_DATES: its values never enter Q(2025-12-01)
    (a -50/B dip there would move Q from -3/B to -4/B) and it never trades itself, although its
    reference set (the same 20 dates as 2025-12-01's) would give Q = -3/B."""
    d, halt = date(2025, 12, 1), date(2025, 11, 28)
    member = flight.make_h30()
    prepare(member, d)
    assert entries(feed(member, halt, dip_path({3: 50, 20: 3}))) == []
    assert entries(feed(member, d, dip_path({3: 3}))) == buy_at(end_bar(3))


def test_values_of_d_itself_never_enter_q_of_d(monkeypatch: pytest.MonkeyPatch) -> None:
    """Q(d) is fixed before d's 08:30: a -60/B value at k = 1 on d (its trigger skipped by a
    guard at 08:35) would move Q from -3/B to -4/B if it counted; x = 3 at k = 3 still enters."""
    monkeypatch.setitem(rel.GUARD_INSTANTS, "MGC", (ns_at(DAY, hm(8, 35)) // NS,))
    member = ready()
    assert entries(feed(member, DAY, dip_path({1: 60, 3: 3}))) == buy_at(end_bar(3))
    after = FLIGHT_DATES[FLIGHT_DATES.index(DAY) + 1]
    member = ready()
    feed(member, DAY, dip_path({1: 60}))  # DAY's values are filed for later dates
    # Q(after): refs[1..19] of DAY (dips 2..10) and DAY (-60/B): m = 8 -> -4/B
    assert entries(feed(member, after, dip_path({3: 4}))) == buy_at(end_bar(3))
