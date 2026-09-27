"""Stage E leakage canaries (design D11.9; Stage E.2b Task 3), run through the generalized Stage E
engine (screening.stage_e_engine.run_engine with screening.stage_e_rules.StageERules and
product_bar_iterator) on synthetic bars of one traded vehicle per group: equity MNQ, rates ZN,
FX 6E, energy MCL, metals MGC, grains ZC, livestock LE, crypto MBT.

A failure here is a STOP-THE-LINE event: no Stage E number is trustworthy until it passes.
Every canary is paired with a deliberately broken engine, member or rule set (the positive
controls in tests/_stage_e_canary_kit.py) that it must flag: a canary that cannot fail on a
planted leak proves nothing.

Per group:
(1) planted future bars: the jump canary (sim/leakage_canaries.py's recipe and thresholds: the real
    engine captures nothing from a jump planted inside the bar the member acts on; a same-bar-fill
    engine and a peek-next-bar engine capture it; the latency control must be captured), and the
    perturbation canary (an honest member's views and every ledger event up to a cutoff are
    unchanged when every later bar is replaced; a member that reads the next bar is caught);
(2) planted values before their availability: a trade date's settlement (D9.7 reads the PRIOR
    date's; a same-day-settlement rule set is caught; DCB-only products consult none, ruling
    L-13), a scheduled release (its event window and fill guard never reach a fill before its
    instant; an off-by-one lookup is caught) and the hindsight field vendor_degraded_day (masked;
    an unmasked run is caught);
(3) a planted bar inside a scheduled closure: an intent decided on it is refused by name, flagged
    or not (the flag and rules/sessions.py both refuse it); a closure-blind rule set is caught.
Cross-product: a planted future in one leg changes no decision on the other leg (a leg-peeking
engine, a misaligned leg, a backward-filled leg and a member reading the leg's frame are caught),
and the tripwire. The ML rule wrapper's canary through the Stage E engine is at the end.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from functools import cache
from types import MappingProxyType

import numpy as np
import pandas as pd
import pytest

from data.group_session import load_group_calendar, previous_trade_date
from rules import price_limits as pl
from screening.stage_e_engine import Fill, IntentRecord, run_engine
from screening.stage_e_frozen import FrozenInputError
from screening.stage_e_rules import product_bar_iterator
from sim import leakage_canaries as lc
from strategy.interface import NS_PER_BAR, NS_PER_S
from strategy.stage_e.interface import LegSpec
from tests._stage_e_canary_kit import (
    CLOSURE_CT,
    CT,
    DAYS,
    GROUP_PRODUCTS,
    JUMP_TICKS,
    NS_MIN,
    CanaryReader,
    ClosureBlindRules,
    ClosureTrader,
    FramePeekingMember,
    HindsightReader,
    LookaheadReleaseCalendar,
    LookaheadViewRules,
    ReactiveMember,
    SameBarFillRun,
    SameDaySettlementRules,
    ScriptMember,
    SettlementSpyRules,
    TripwireRules,
    TripwireSpy,
    ViewSpy,
    closure_booking,
    closure_trades,
    flatten_ct,
    from_ticks,
    gap_before,
    group_bars,
    jump_score,
    ledger_after,
    ledger_until,
    lookahead_bars,
    mark_minutes,
    plant_bar,
    plant_future,
    plant_jumps,
    plant_one_bar,
    product_bars,
    release_calendar,
    rules_for,
    run_with,
    session_end_ts,
    settlement_proxies,
    shift_leg,
    to_ticks,
    tripwire_violations,
    ts_at,
    views_until,
)

GROUPS = tuple(GROUP_PRODUCTS)
HARD_LIMIT = frozenset(g for g, r in GROUP_PRODUCTS.items() if r in pl.HARD_LIMIT_PRODUCTS)
D0, D1, D2, D3 = DAYS[:4]


def _one_leg(group: str) -> tuple[str, tuple[LegSpec, ...]]:
    root = GROUP_PRODUCTS[group]
    return root, (LegSpec(root, True),)


def _refusals(result, day: date | None = None) -> list[str]:
    out = []
    for e in result.events(IntentRecord):
        if e.refusal is None:
            continue
        if day is None or _day_of(e.decision_ts_ns - NS_PER_BAR) == day:
            out.append(e.refusal.reason)
    return out


def _day_of(ts: int) -> date:
    return datetime.fromtimestamp(ts / NS_PER_S, tz=UTC).astimezone(CT).date()


# ============================================================ planting itself ====
@pytest.mark.parametrize("group", GROUPS)
def test_planted_jumps_stay_on_the_vendor_grid_and_never_mutate_the_input(group: str) -> None:
    root, _ = _one_leg(group)
    frame = group_bars(group)
    before = frame.copy()
    planted = plant_jumps(frame, root, 11, mark_minutes(root))
    assert frame.equals(before)
    assert len(planted.leak_markers) >= 13 * len(DAYS)  # every marked minute of every date
    list(product_bar_iterator(root)(planted.frame))  # vendor grid and OHLC checks pass
    ts = frame["ts_event"].to_numpy(np.int64)
    c0, c1 = to_ticks(root, frame["close"]), to_ticks(root, planted.frame["close"])
    o0, o1 = to_ticks(root, frame["open"]), to_ticks(root, planted.frame["open"])
    for marked, d in list(planted.leak_markers.items())[:10]:
        i = int(np.flatnonzero(ts == marked)[0])
        assert o1[i] == o0[i] and c1[i] - c0[i] == d * JUMP_TICKS  # the jump is INSIDE bar i
        assert o1[i + 1] - o0[i + 1] == d * JUMP_TICKS  # and carried to the next open
        assert int(ts[i]) - NS_MIN in planted.latency_markers


@pytest.mark.parametrize("group", GROUPS)
def test_planted_future_changes_only_bars_after_the_cutoff(group: str) -> None:
    root, _ = _one_leg(group)
    frame = group_bars(group)
    cutoff = ts_at(D2, 10, 1)
    planted = plant_future(frame, root, cutoff)
    early = frame["ts_event"] <= cutoff
    assert planted[early].equals(frame[early])
    assert not planted.loc[~early, "close"].equals(frame.loc[~early, "close"])
    list(product_bar_iterator(root)(planted))


# ================================================ (1a) planted future: jump canary ====
@cache
def _jump_run(group: str, markers_kind: str, mutant: str | None) -> dict:
    root, legs = _one_leg(group)
    planted = plant_jumps(group_bars(group), root, 11, mark_minutes(root))
    markers = planted.leak_markers if markers_kind == "leak" else planted.latency_markers
    frames = {root: planted.frame}
    member = CanaryReader(root, markers)
    if mutant == "peek_next_bar":
        rules = rules_for(legs, cls=LookaheadViewRules, lookahead=lookahead_bars(frames, [root]))
    else:
        rules = rules_for(legs)
    run_cls = SameBarFillRun if mutant == "same_bar_fill" else None
    result = run_with(frames, member, legs, rules, run_cls) if run_cls else \
        run_engine(frames, member, legs, rules)
    return jump_score(result, root, rules, markers)


@pytest.mark.parametrize("group", GROUPS)
def test_real_engine_shows_no_edge_from_a_jump_planted_inside_the_decision_bar(group) -> None:
    s = _jump_run(group, "leak", None)
    assert lc.leak_canary_passes(s, JUMP_TICKS), s
    assert s["trades"] >= 150 and abs(s["mean_captured_ticks"]) < JUMP_TICKS / 4


@pytest.mark.parametrize("mutant", ["same_bar_fill", "peek_next_bar"])
@pytest.mark.parametrize("group", GROUPS)
def test_the_jump_canary_catches_a_leaky_engine(group: str, mutant: str) -> None:
    s = _jump_run(group, "leak", mutant)
    assert not lc.leak_canary_passes(s, JUMP_TICKS), s  # the canary FAILS on this engine
    assert lc.edge_detected(s, JUMP_TICKS) and s["hit_rate"] > 0.9, s


@pytest.mark.parametrize("group", GROUPS)
def test_latency_control_is_captured_by_the_real_engine(group: str) -> None:
    """A marker one bar BEFORE the jump is legitimate information: a correct engine must capture
    it, which rules out an engine that passes only because it fills too late."""
    s = _jump_run(group, "latency", None)
    assert lc.edge_detected(s, JUMP_TICKS), s


# ======================================== (1b) planted future: perturbation canary ====
def _cutoffs() -> tuple[int, ...]:
    return ts_at(D2, 10, 1), ts_at(DAYS[4], 12, 7)


def _perturbation(group: str, member_of, cutoff: int, days=DAYS[:6]) -> tuple:
    root, legs = _one_leg(group)
    clean = product_bars(root, days, 5)
    planted = plant_future(clean, root, cutoff)
    rules = rules_for(legs, days)
    spies = (ViewSpy(member_of(clean)), ViewSpy(member_of(planted)))
    runs = tuple(run_engine({root: f}, spy, legs, rules) for f, spy in zip(
        (clean, planted), spies, strict=True))
    return runs, spies


@pytest.mark.parametrize("group", GROUPS)
def test_an_honest_member_is_unaffected_by_planted_future_bars(group: str) -> None:
    root, _ = _one_leg(group)
    for cutoff in _cutoffs():
        (rc, rp), (sc, sp) = _perturbation(group, lambda f: ReactiveMember(root), cutoff)
        assert views_until(sc, cutoff) == views_until(sp, cutoff)
        assert ledger_until(rc, cutoff) == ledger_until(rp, cutoff)
        assert sum(isinstance(e, Fill) for e in ledger_until(rc, cutoff)) >= 10
        # the plant is not inert: once visible, it changes what the member does
        assert ledger_after(rc, cutoff) != ledger_after(rp, cutoff)


@pytest.mark.parametrize("group", GROUPS)
def test_a_member_that_peeks_at_the_next_bar_is_caught(group: str) -> None:
    root, _ = _one_leg(group)
    for cutoff in _cutoffs():
        (rc, rp), (sc, sp) = _perturbation(
            group, lambda f: FramePeekingMember(root, root, f), cutoff)
        assert views_until(sc, cutoff) == views_until(sp, cutoff)  # the engine hands the same
        assert ledger_until(rc, cutoff - NS_MIN) == ledger_until(rp, cutoff - NS_MIN)
        assert ledger_until(rc, cutoff) != ledger_until(rp, cutoff)  # the canary FAILS: caught


# ============================================ (2) settlement before its availability ====
def _settlement_world(group: str) -> dict:
    """D0..D2; the member trades on D1 and D2 at 10:00 and 11:00 CT (flat 10 minutes later),
    never near the settlement window. The planted value: D1's settlement-window bar moved far
    enough that D2's prices sit beyond D9.7's lower stop level of the planted settlement."""
    root, legs = _one_leg(group)
    days = DAYS[:3]
    clean = product_bars(root, days, 7)
    lo, hi = pl.settlement_window_utc(root, D1)
    start = int(lo.timestamp()) * NS_PER_S // NS_MIN * NS_MIN
    end = int(hi.timestamp()) * NS_PER_S
    ts = clean["ts_event"].to_numpy(np.int64)
    window = (ts >= start) & (ts < end)
    assert window.any(), (group, "the frame must hold D1's settlement window")
    price = float(clean.loc[window, "close"].iloc[-1])
    if GROUP_PRODUCTS[group] in pl.HARD_LIMIT_PRODUCTS:
        band = pl.limit_band(root, D2, lo, price)
        lower = pl.stop_levels(band, price).lower
        offset = int(np.ceil(1.25 * float(to_ticks(root, [price])[0]
                                          - to_ticks(root, [float(lower)])[0])))
    else:
        offset = 200
    planted = clean.copy()
    for col in ("open", "high", "low", "close"):
        moved = to_ticks(root, clean.loc[window, col]) + offset
        planted.loc[window, col] = from_ticks(root, moved)
    orders = {}
    for day in (D1, D2):
        for hh in (10, 11):
            orders[ts_at(day, hh, 0)] = [(root, "buy", 1)]
            orders[ts_at(day, hh, 10)] = [(root, "flat", 0)]
    return {"root": root, "legs": legs, "days": days, "clean": clean, "planted": planted,
            "orders": orders, "window_start": int(ts[window][0])}


@pytest.mark.parametrize("group", GROUPS)
def test_a_planted_settlement_is_not_read_before_its_trade_date_ends(group: str) -> None:
    w = _settlement_world(group)
    root, legs = w["root"], w["legs"]
    spies = [rules_for(legs, w["days"], cls=SettlementSpyRules) for _ in range(2)]
    rc, rp = (run_engine({root: f}, ScriptMember(w["orders"]), legs, r)
              for f, r in zip((w["clean"], w["planted"]), spies, strict=True))
    first_d2 = int(w["planted"].loc[w["planted"]["trade_date"] == D2.isoformat(),
                                    "ts_event"].iloc[0])
    # nothing on D0 or D1 (before or after D1's settlement window) sees the planted value
    assert ledger_until(rc, first_d2 - NS_MIN) == ledger_until(rp, first_d2 - NS_MIN)
    if group not in HARD_LIMIT:  # D9.7 does not apply (DCB only, ruling L-13): nothing is read
        assert spies[0].calls == [] and spies[1].calls == []
        assert rc.ledger == rp.ledger
        return
    clean_proxy = settlement_proxies(w["clean"], root)
    planted_proxy = settlement_proxies(w["planted"], root)
    assert planted_proxy[D1] != clean_proxy[D1]
    for _, day, value in spies[1].calls:  # every value consulted is the PRIOR date's
        assert value == {D1: planted_proxy[D0], D2: planted_proxy[D1]}.get(day), day
    # the plant is not inert: on D2 it is available and D9.7 refuses the entries
    assert "price_limit_zone_no_entry" in _refusals(rp, D2)
    assert "price_limit_zone_no_entry" not in _refusals(rc, D2)


@pytest.mark.parametrize("group", sorted(HARD_LIMIT))
def test_a_same_day_settlement_rule_set_is_caught(group: str) -> None:
    w = _settlement_world(group)
    root, legs = w["root"], w["legs"]
    hindsight = {(root, d): v for d, v in settlement_proxies(w["planted"], root).items()}
    real = run_engine({root: w["planted"]}, ScriptMember(w["orders"]), legs,
                      rules_for(legs, w["days"]))
    leaky = run_engine({root: w["planted"]}, ScriptMember(w["orders"]), legs,
                       rules_for(legs, w["days"], cls=SameDaySettlementRules,
                                 hindsight_proxies=hindsight))
    cut = w["window_start"] - NS_MIN
    assert ledger_until(real, cut) != ledger_until(leaky, cut)  # caught before the window
    assert "price_limit_zone_no_entry" in _refusals(leaky, D1)


# ============================================== (2) release before its instant ====
def _release_world(group: str) -> dict:
    root, legs = _one_leg(group)
    frame = product_bars(root, DAYS[:2], 9)
    release = ts_at(D1, 10, 0)
    orders = {ts_at(D1, 9, 40): [(root, "buy", 1)], ts_at(D1, 9, 50): [(root, "flat", 0)],
              ts_at(D1, 9, 54): [(root, "sell", 1)], ts_at(D1, 9, 57): [(root, "flat", 0)],
              ts_at(D1, 9, 59): [(root, "buy", 1)],  # would fill at the release's own open
              ts_at(D1, 10, 10): [(root, "flat", 0)],
              ts_at(D1, 10, 45): [(root, "buy", 1)], ts_at(D1, 10, 50): [(root, "flat", 0)]}
    return {"root": root, "legs": legs, "frame": frame, "release": release, "orders": orders}


def _release_run(w: dict, calendar) -> object:
    rules = rules_for(w["legs"], DAYS[:2], releases=calendar)
    return run_engine({w["root"]: w["frame"]}, ScriptMember(w["orders"]), w["legs"], rules)


def _fills_before(result, ts: int) -> list:
    return [f for f in result.events(Fill) if f.fill_ts_ns < ts]


@pytest.mark.parametrize("group", GROUPS)
def test_a_release_never_reaches_a_fill_before_its_instant(group: str) -> None:
    w = _release_world(group)
    clean = _release_run(w, release_calendar(w["root"], []))
    planted = _release_run(w, release_calendar(w["root"], [w["release"]]))
    before = _fills_before(clean, w["release"])
    assert len(before) == 4 and before == _fills_before(planted, w["release"])
    assert not any(f.event_window for f in before)
    # the plant is not inert: from its instant the guard defers and the event cost applies
    during = [f for f in planted.events(Fill)
              if w["release"] <= f.fill_ts_ns < w["release"] + 30 * NS_MIN]
    assert during and all(f.event_window for f in during)
    assert planted.counters.get("fill_guard_deferral", 0) >= 1
    assert min(f.fill_ts_ns for f in during) >= w["release"] + 2 * NS_MIN
    late = w["release"] + 30 * NS_MIN  # after the window the costs are the clean run's again

    def key(f: Fill) -> tuple:
        return (f.fill_ts_ns, f.side, f.qty, f.price, f.commission_cents, f.slippage_cents,
                f.event_window)

    assert [key(f) for f in planted.events(Fill) if f.fill_ts_ns >= late] == \
        [key(f) for f in clean.events(Fill) if f.fill_ts_ns >= late]


@pytest.mark.parametrize("group", GROUPS)
def test_an_off_by_one_release_lookup_is_caught(group: str) -> None:
    w = _release_world(group)
    clean = _release_run(w, release_calendar(w["root"], []))
    leaky = _release_run(w, release_calendar(w["root"], [w["release"]],
                                             cls=LookaheadReleaseCalendar))
    assert _fills_before(clean, w["release"]) != _fills_before(leaky, w["release"])


# ============================================== (2) hindsight field before its time ====
def _degraded(frame: pd.DataFrame, day: date) -> pd.DataFrame:
    out = frame.copy()
    out.loc[out["trade_date"] == day.isoformat(), "vendor_degraded_day"] = True
    return out


@pytest.mark.parametrize("group", GROUPS)
def test_a_hindsight_flag_never_reaches_the_member(group: str) -> None:
    root, legs = _one_leg(group)
    clean = product_bars(root, DAYS[:3], 3)
    planted = _degraded(clean, D1)
    member = HindsightReader(root)
    res = run_engine({root: planted}, member, legs, rules_for(legs, DAYS[:3]))
    assert member.flags_seen and not any(member.flags_seen)
    assert not res.events(Fill)
    base = run_engine({root: clean}, HindsightReader(root), legs, rules_for(legs, DAYS[:3]))
    assert res.ledger == base.ledger


@pytest.mark.parametrize("group", GROUPS)
def test_an_engine_that_does_not_mask_the_hindsight_flag_is_caught(group: str) -> None:
    root, legs = _one_leg(group)
    planted = _degraded(product_bars(root, DAYS[:3], 3), D1)
    member = HindsightReader(root)
    res = run_engine({root: planted}, member, legs,
                     rules_for(legs, DAYS[:3], mask_hindsight_fields=False))
    assert any(member.flags_seen) and res.events(Fill)  # the canary FAILS: caught


# ================================================= (3) a bar inside a closure ====
def _closure_world(group: str, *, flagged: bool, session_flags: bool = True) -> dict:
    root, legs = _one_leg(group)
    days = DAYS[:4]
    frame = product_bars(root, days, 13)
    at = CLOSURE_CT[group]
    ts = ts_at(D1, at.hour, at.minute)
    in_closure, _, label = closure_booking(root, ts)
    assert in_closure and label is not None, (group, "the planted minute must be a closure")
    price = int(to_ticks(root, frame["close"])[-1]) + 30
    planted = plant_bar(frame, root, ts, label, price, closure_flag=flagged,
                        session_flags=session_flags)
    return {"root": root, "legs": legs, "days": days, "frame": planted, "ts": ts,
            "label": label}


@pytest.mark.parametrize("group", GROUPS)
def test_an_intent_on_a_flagged_closure_bar_is_refused_by_name(group: str) -> None:
    w = _closure_world(group, flagged=True)
    root, legs = w["root"], w["legs"]
    res = run_engine({root: w["frame"]}, ClosureTrader(root, frozenset([w["ts"]])), legs,
                     rules_for(legs, w["days"]))
    (record,) = [e for e in res.events(IntentRecord) if e.decision_ts_ns == w["ts"] + NS_PER_BAR]
    assert not record.accepted and record.refusal.reason == "engine_scheduled_closure"
    assert res.counters["engine_scheduled_closure"] == 1
    assert closure_trades(res, frozenset([w["ts"]])) == []


@pytest.mark.parametrize("group", GROUPS)
def test_an_unflagged_closure_bar_is_still_refused_by_the_session_rules(group: str) -> None:
    """A builder that flagged nothing: rules/sessions.py's own state refuses the intent."""
    w = _closure_world(group, flagged=False, session_flags=False)
    root, legs = w["root"], w["legs"]
    res = run_engine({root: w["frame"]}, ClosureTrader(root, frozenset([w["ts"]])), legs,
                     rules_for(legs, w["days"]))
    (record,) = [e for e in res.events(IntentRecord) if e.decision_ts_ns == w["ts"] + NS_PER_BAR]
    assert not record.accepted and record.refusal.reason == "engine_flatten_window"
    assert closure_trades(res, frozenset([w["ts"]])) == []


@pytest.mark.parametrize("group", GROUPS)
def test_a_closure_blind_rule_set_is_caught(group: str) -> None:
    w = _closure_world(group, flagged=True)
    root, legs = w["root"], w["legs"]
    res = run_engine({root: w["frame"]}, ClosureTrader(root, frozenset([w["ts"]])), legs,
                     rules_for(legs, w["days"], cls=ClosureBlindRules))
    assert closure_trades(res, frozenset([w["ts"]]))  # the canary FAILS: caught


GAP_SCENARIOS = ("member_exit_pending", "forced_flatten_pending", "mll_on_the_closure_bar")
# One early-close trade date per group (rules/sessions.py: Topstep's close-by or 30 minutes before
# the CME early close) whose calendar session ends at the early close.
EARLY_CLOSE = {"equity": date(2025, 7, 3), "rates": date(2025, 5, 26), "fx": date(2025, 7, 4),
               "energy": date(2025, 7, 4), "metals": date(2025, 7, 4),
               "grains": date(2025, 11, 28), "livestock": date(2025, 11, 28),
               "crypto": date(2025, 7, 4)}
FINDING_C1 = (
    "RUNNER FINDING C-1 (reported to the lead, not fixed here): on an early-close date the D8 cost "
    "table has a bucket at the closure minute, so an order pending when a closure bar is the "
    "leg's next bar (a member exit or the forced flatten), or the MLL check on that bar, fills "
    "AT the closure print; the engine has no closure check at the fill (fill_pending_at_open, "
    "try_passive, check_mll). Remove this marker once the engine refuses or flags such a fill.")


class CanaryPrecondition(RuntimeError):
    """A canary's setup is not what it claims (raised instead of AssertionError so that the
    strict xfail below can only be satisfied by its own final assertion)."""


def _require(ok: bool, what: object) -> None:
    if not ok:
        raise CanaryPrecondition(repr(what))


def _gap_world(group: str, scenario: str, day_kind: str) -> dict:
    """A vendor gap from just before F to the session's close minute, where a closure bar (lead
    ruling L-3: booked to the session it closes) is the leg's next bar while the member holds a
    position (entered at F - 30 min): with a member exit pending, with the forced flatten
    pending, or with nothing pending and a closure print beyond the MLL."""
    root, legs = _one_leg(group)
    if day_kind == "regular":
        day, days = D1, DAYS[:3]
    else:
        day = EARLY_CLOSE[group]
        prior = previous_trade_date(load_group_calendar(group), day)
        _require(prior is not None and flatten_ct(root, day) < flatten_ct(root, prior),
                 (group, day, prior))
        days = (prior, day)
    frame = product_bars(root, days, 17)
    f = flatten_ct(root, day)
    entry = ts_at(day, f.hour, f.minute) - 30 * NS_MIN
    last = ts_at(day, f.hour, f.minute) - (NS_MIN if scenario == "forced_flatten_pending"
                                           else 3 * NS_MIN)
    try:
        end = session_end_ts(root, day)
    except AssertionError as exc:
        raise CanaryPrecondition(f"{group} {day}: no open interval holds F - 1 min") from exc
    in_closure, boundary, label = closure_booking(root, end)
    _require(in_closure and boundary and label == day, (group, in_closure, boundary, label))
    ts = frame["ts_event"].to_numpy(np.int64)
    on_day = (frame["trade_date"] == day.isoformat()).to_numpy()
    gapped = frame[~(on_day & (ts > last))].reset_index(drop=True)
    entry_ticks = int(to_ticks(root, gapped.loc[gapped["ts_event"] == entry, "open"])[0])
    tv = rules_for(legs, days).tick_value(root)
    if scenario == "mll_on_the_closure_bar":
        price = entry_ticks - int(np.ceil(200_000 / float(tv))) - 50  # the XFA MLL is $2,000
    else:
        price = entry_ticks + 10
    planted = plant_bar(gapped, root, end, label, price, closure_flag=True)
    orders = {entry - NS_MIN: [(root, "buy", 1)]}
    if scenario == "member_exit_pending":
        orders[last] = [(root, "flat", 0)]
    return {"root": root, "legs": legs, "days": days, "frame": planted, "ts": end,
            "orders": orders}


def _gap_run(w: dict):
    root, legs = w["root"], w["legs"]
    res = run_engine({root: w["frame"]}, ScriptMember(w["orders"]), legs,
                     rules_for(legs, w["days"]))
    _require(any(f.reason == "strategy" and f.position_after == 1 for f in res.events(Fill)),
             "the member holds a position into the gap")
    return res


@pytest.mark.parametrize("scenario", GAP_SCENARIOS)
@pytest.mark.parametrize("group", GROUPS)
def test_a_closure_bar_after_a_vendor_gap_on_a_regular_date_is_never_traded(
        group: str, scenario: str) -> None:
    """Lead ruling OC-T: the engine never trades or marks a closure print; the pending exit, the
    pending forced flatten or the open position fills at the close of the last tradable bar
    before it, flagged and counted by name ("fill_at_prior_close_closure_gap"), never through an
    accidental CostLookupError (finding C-2)."""
    w = _gap_world(group, scenario, "regular")
    try:
        res = _gap_run(w)
    except FrozenInputError as exc:
        pytest.fail(f"accidental refusal instead of the named one: {exc}")
    assert closure_trades(res, frozenset([w["ts"]])) == []
    assert res.counters.get("fill_at_prior_close_closure_gap") == 1


@pytest.mark.parametrize("scenario", GAP_SCENARIOS)
@pytest.mark.parametrize("group", GROUPS)
def test_a_closure_bar_after_a_vendor_gap_on_an_early_close_date_is_never_traded(
        group: str, scenario: str) -> None:
    w = _gap_world(group, scenario, "early_close")
    assert closure_trades(_gap_run(w), frozenset([w["ts"]])) == []


# ======================================================= cross-product canaries ====
# MNQ (equity) traded, ZN (rates) read as a signal leg: two group calendars on one UTC grid.
TRADED, SIGNAL = "MNQ", "ZN"
CROSS_LEGS = {"signal": (LegSpec(TRADED, True), LegSpec(SIGNAL, False)),
              "both_traded": (LegSpec(TRADED, True), LegSpec(SIGNAL, True))}


@cache
def _cross_planted():
    """A common shock: a jump inside the same marked minute of both legs, same direction; the
    markers sit on the SIGNAL leg's jumped bars."""
    marks = mark_minutes(TRADED)
    zn = plant_jumps(group_bars("rates"), SIGNAL, 23, marks)
    mnq = plant_jumps(group_bars("equity"), TRADED, 0, marks, directions=zn.leak_markers)
    assert set(mnq.leak_markers) == set(zn.leak_markers) and len(zn.leak_markers) >= 250
    return mnq, zn


@cache
def _cross_jump(kind: str) -> tuple[dict, dict]:
    """The reader acts on the signal leg's marked bar; a marker travels with the bar's content
    (a re-stamped or copied bar carries it), and trips are scored against the jumps' minutes."""
    mnq, zn = _cross_planted()
    legs = CROSS_LEGS["signal"]
    markers = zn.latency_markers if kind == "latency" else zn.leak_markers
    reader_markers = dict(markers)
    frames = {TRADED: mnq.frame, SIGNAL: zn.frame}
    if kind == "misaligned_leg":  # the signal leg's bars stamped at their close minute - 1
        frames[SIGNAL] = shift_leg(zn.frame, -1)
        reader_markers = {t - NS_MIN: d for t, d in markers.items()}
    elif kind in ("backfilled_leg", "gapped_leg", "view_backfill"):
        frames[SIGNAL] = gap_before(zn.frame, sorted(markers), backfill=kind == "backfilled_leg")
        if kind == "backfilled_leg":
            reader_markers.update({t - NS_MIN: d for t, d in markers.items()})
    if kind == "peek_signal_leg":
        rules = rules_for(legs, cls=LookaheadViewRules,
                          lookahead=lookahead_bars(frames, [SIGNAL]))
    elif kind == "view_backfill":
        rules = rules_for(legs, cls=LookaheadViewRules, only_if_missing=True,
                          lookahead=lookahead_bars(frames, [SIGNAL]))
    else:
        rules = rules_for(legs)
    member = CanaryReader(TRADED, MappingProxyType(reader_markers), marker_root=SIGNAL)
    res = run_engine(frames, member, legs, rules)
    return jump_score(res, TRADED, rules, markers), dict(res.counters)


@pytest.mark.parametrize("kind", ["real", "gapped_leg"])
def test_a_jump_planted_in_the_signal_leg_gives_the_traded_leg_no_edge(kind: str) -> None:
    s, _ = _cross_jump(kind)
    assert lc.leak_canary_passes(s, JUMP_TICKS), s
    assert s["trades"] >= 200


@pytest.mark.parametrize("kind", ["peek_signal_leg", "misaligned_leg", "backfilled_leg"])
def test_the_cross_product_jump_canary_catches_a_leaking_signal_leg(kind: str) -> None:
    s, _ = _cross_jump(kind)
    assert not lc.leak_canary_passes(s, JUMP_TICKS), s  # the canary FAILS: caught
    assert lc.edge_detected(s, JUMP_TICKS), s


def test_cross_product_latency_control_is_captured() -> None:
    s, _ = _cross_jump("latency")
    assert lc.edge_detected(s, JUMP_TICKS), s


def test_a_view_level_backward_fill_is_neutralized_by_the_missing_bar_rule() -> None:
    """Defense in depth (D11.5): a member shown the signal leg's NEXT bar where the leg has none
    wants to open, and the engine refuses every such opening (engine_leg_missing_bar)."""
    s, counters = _cross_jump("view_backfill")
    _, zn = _cross_planted()
    assert counters.get("engine_leg_missing_bar", 0) >= 0.9 * len(zn.leak_markers)
    assert lc.leak_canary_passes(s, JUMP_TICKS) or s["trades"] < 100, s


def _cross_perturbation(member_of, legs, plant: str, cutoff: int) -> tuple:
    days = DAYS[:6]
    mnq = product_bars(TRADED, days, 5)
    zn = product_bars(SIGNAL, days, 6)
    zn_planted = (plant_future(zn, SIGNAL, cutoff) if plant == "future"
                  else plant_one_bar(zn, SIGNAL, cutoff + NS_MIN))
    rules = rules_for(legs, days)
    spies = (ViewSpy(member_of(zn)), ViewSpy(member_of(zn_planted)))
    runs = tuple(run_engine({TRADED: mnq, SIGNAL: z}, spy, legs, rules)
                 for z, spy in zip((zn, zn_planted), spies, strict=True))
    return runs, spies


@pytest.mark.parametrize("plant", ["future", "one_bar"])
@pytest.mark.parametrize("legs_kind", sorted(CROSS_LEGS))
def test_a_planted_future_in_one_leg_changes_no_decision_on_the_other(legs_kind: str,
                                                                      plant: str) -> None:
    for cutoff in _cutoffs():
        (rc, rp), (sc, sp) = _cross_perturbation(
            lambda z: ReactiveMember(TRADED, signal=SIGNAL), CROSS_LEGS[legs_kind], plant,
            cutoff)
        assert views_until(sc, cutoff) == views_until(sp, cutoff)
        assert ledger_until(rc, cutoff) == ledger_until(rp, cutoff)
        assert sum(isinstance(e, Fill) for e in ledger_until(rc, cutoff)) >= 10
        assert all(f.root == TRADED for f in rc.events(Fill))
        # the plant is not inert: once due, the member is handed it (one bar) or trades on it
        if plant == "one_bar":
            assert [v for v in sc.seen if v[0] > cutoff] != [v for v in sp.seen if v[0] > cutoff]
        else:
            assert ledger_after(rc, cutoff) != ledger_after(rp, cutoff)


def test_a_member_that_reads_the_other_legs_next_bar_is_caught() -> None:
    for cutoff in _cutoffs():
        (rc, rp), _ = _cross_perturbation(
            lambda z: FramePeekingMember(TRADED, SIGNAL, z), CROSS_LEGS["signal"], "future",
            cutoff)
        assert ledger_until(rc, cutoff - NS_MIN) == ledger_until(rp, cutoff - NS_MIN)
        assert ledger_until(rc, cutoff) != ledger_until(rp, cutoff)  # the canary FAILS: caught


# ================================================================ the tripwire ====
@pytest.mark.parametrize("case", [*GROUPS, "cross_product"])
def test_the_engine_never_pulls_a_bar_before_the_minute_it_decides(case: str) -> None:
    frames, legs = _tripwire_case(case)
    rules = rules_for(legs, DAYS[:3], cls=TripwireRules)
    spy = TripwireSpy(rules)
    run_engine(frames, spy, legs, rules)
    assert len(spy.calls) >= 300 and tripwire_violations(spy, frames) == []


@pytest.mark.parametrize("case", ["equity", "cross_product"])
def test_the_tripwire_catches_a_feed_that_reads_ahead(case: str) -> None:
    frames, legs = _tripwire_case(case)
    rules = rules_for(legs, DAYS[:3], cls=TripwireRules, eager=True)
    spy = TripwireSpy(rules)
    run_engine(frames, spy, legs, rules)
    assert tripwire_violations(spy, frames)  # the canary FAILS: caught


def _tripwire_case(case: str) -> tuple[dict, tuple]:
    if case == "cross_product":
        zn = product_bars(SIGNAL, DAYS[:3], 2)
        zn = zn[zn.index % 7 != 3]  # the signal leg misses some minutes
        return ({TRADED: product_bars(TRADED, DAYS[:3], 1), SIGNAL: zn.reset_index(drop=True)},
                CROSS_LEGS["signal"])
    root, legs = _one_leg(case)
    return {root: product_bars(root, DAYS[:3], 1)}, legs


# ============================================ the ML rule wrapper's canary (M7.7) ====
# A K1 route rule through ml_route.stage_e_adapter's single-exposure path (lead ruling OC-P) on
# the Stage E engine: the M2K exposure trades M2K and reads its price path RTY and the cluster's
# F16 lead NQ as signal legs. The wrapper needs about 140 trade dates of history before its
# first complete feature row, so the synthetic span is 2019-05-06..2019-12-04. Cutoff A sits 2
# minutes before the 11:00 CT decision time of the 145th date, cutoff B on it.
ML_FIRST, ML_LAST = date(2019, 5, 6), date(2019, 12, 4)
ML_CONDITIONS = (("F1_ret5", ">", 0.0), ("F16_lead_ret30", "<=", 5.0))


@cache
def _ml_world() -> dict:
    from zoneinfo import ZoneInfo

    from ml_route.inputs import RouteInputs, event_calendar_from_release, load_products
    from ml_route.stage_e_adapter import exposure_plans
    from ml_route.surrogate import Leaf, rule_json
    from ml_route.synthetic import synthetic_bars, synthetic_inputs
    from screening.stage_e_rules import release_calendar_from_dict

    nq = synthetic_bars("NQ", "equity", ML_FIRST, ML_LAST, 21, 0.25, 8000.0)
    rty = synthetic_bars("RTY", "equity", ML_FIRST, ML_LAST, 22, 0.1, 1500.0)
    days = sorted(date.fromisoformat(d) for d in nq["trade_date"].unique())
    chicago = ZoneInfo("America/Chicago")
    releases = [{"id": f"r{i}", "products": ["NQ", "MNQ", "RTY", "M2K"], "cpi": False,
                 "source": "canary", "instant_utc": datetime.combine(
                     d, datetime.min.time().replace(hour=10, minute=29), tzinfo=chicago)
                 .astimezone(UTC).isoformat()} for i, d in enumerate(days[130:])]
    calendar = release_calendar_from_dict(
        {"schema": "stage_e_release_calendar/1", "releases": releases,
         "coverage": {"first": "2019-05-01", "last": "2020-01-31"}}, "c" * 64, "ml canary")
    products = load_products()
    events = event_calendar_from_release(calendar, {r: products[r] for r in ("NQ", "RTY")})
    base = synthetic_inputs({"NQ": ML_FIRST, "RTY": ML_FIRST}, events)
    inputs = RouteInputs(base.products, base.costs, events, base.s_x)
    rule = rule_json("K1", "lgbm", "h30", Leaf(0, 1, ML_CONDITIONS, 0.1), 1, 0.05,
                     ["MNQ", "M2K"], "MNQ", {"model_sha256": "m" * 64}, {})
    (plan,) = [p for p in exposure_plans(rule, inputs.products) if p.vehicle == "M2K"]
    assert plan.legs == (LegSpec("M2K", True), LegSpec("RTY", False), LegSpec("NQ", False))
    cut_a, cut_b = ts_at(days[144], 10, 58), ts_at(days[144], 11, 0)
    for frame in (nq, rty):
        assert (frame["ts_event"] == cut_a).sum() == 1 and (frame["ts_event"] == cut_b).sum() == 1
    frames = {"clean": {"RTY": rty, "NQ": nq},
              "own_path": {"RTY": plant_future(rty, "RTY", cut_a), "NQ": nq},
              "lead": {"RTY": rty, "NQ": plant_future(nq, "NQ", cut_a)},
              "lead_b": {"RTY": rty, "NQ": plant_future(nq, "NQ", cut_b)}}
    for f in frames.values():
        f["M2K"] = f["RTY"].assign(raw_symbol="M2KZ9", instrument_id=np.uint32(3))
    return {"days": days, "calendar": calendar, "inputs": inputs, "events": events,
            "rule": rule, "plan": plan, "cut_a": cut_a, "cut_b": cut_b, "frames": frames}


@cache
def _ml_run(data: str, early_lead: bool = False, peek_steps: int = 0, lead_shift: int = 0):
    """One engine run of the M2K exposure. DELIBERATELY BROKEN variants, positive controls only:
    ``peek_steps`` (the engine hands the price-path and lead legs a later bar) and ``lead_shift``
    (the lead's bars stamped that many minutes EARLY: a misaligned cross-product feed)."""
    from ml_route.stage_e_adapter import build_exposure_member
    from screening.stage_e_frozen import leg_inputs
    from screening.stage_e_rules import StageERules
    from tests._stage_e_canary_kit import EarlyLeadMember, MLSpy

    w = _ml_world()
    plan, inputs, days = w["plan"], w["inputs"], w["days"]
    frames = dict(w["frames"][data])
    if lead_shift:
        frames["NQ"] = shift_leg(frames["NQ"], -lead_shift)
    member = build_exposure_member(w["rule"], plan, inputs.products, inputs.costs, w["events"],
                                   {"NQ": days, "RTY": days}, {})
    spy = MLSpy(member)
    runner = EarlyLeadMember(spy, "NQ", frames["NQ"]) if early_lead else spy
    tables = {leg.root: leg_inputs(leg.root, traded=leg.traded) for leg in plan.legs}
    if peek_steps:
        rules = LookaheadViewRules(tables, frozenset(days), frozenset(), w["calendar"],
                                   lookahead=lookahead_bars(frames, ["RTY", "NQ"]),
                                   steps=peek_steps)
    else:
        rules = StageERules(tables, frozenset(days), frozenset(), w["calendar"])
    result = run_engine({leg.root: frames[leg.root] for leg in plan.legs}, runner, plan.legs,
                        rules)
    return spy, result


@pytest.mark.parametrize("planted", ["own_path", "lead"])
def test_the_ml_wrapper_is_unaffected_by_planted_future_bars(planted: str) -> None:
    cut = _ml_world()["cut_a"]
    clean_spy, clean = _ml_run("clean")
    spy, res = _ml_run(planted)
    features, decisions = clean_spy.emitted_until(cut)
    assert sum(row is not None for _, _, row in features) >= 40
    assert sum(d.fired for _, d in decisions) >= 10
    assert spy.emitted_until(cut) == (features, decisions)
    assert ledger_until(res, cut) == ledger_until(clean, cut)
    assert sum(isinstance(e, Fill) for e in ledger_until(clean, cut)) >= 10
    # the plant is not inert: the next decision's features (11:00 CT) read it
    assert spy.emitted_after(cut)[0] != clean_spy.emitted_after(cut)[0]


def test_the_ml_wrapper_ignores_lead_bars_handed_over_early() -> None:
    """M7.7's cross-product check through the Stage E engine: every lead bar, the planted future
    included, is handed to the wrapper before the run; every decision, feature row and ledger
    event equals the normal per-minute handover's."""
    normal_spy, normal = _ml_run("lead")
    early_spy, early = _ml_run("lead", early_lead=True)
    assert early_spy.features == normal_spy.features
    assert early_spy.decisions == normal_spy.decisions
    assert early.ledger == normal.ledger


def test_the_ml_lead_stays_aligned_even_without_the_wrappers_lead_filter(monkeypatch) -> None:
    """Defense in depth: with the wrapper's lead filter switched off AND every lead bar handed
    over early, ml_route.rows' as-of read of F16 (the latest lead bar closing <= t) and the
    lead's Daily (earlier dates only) still keep every feature row equal. So removing the filter
    is not a leak by itself, and it cannot serve as this canary's positive control (the
    misaligned lead below is the one)."""
    from ml_route import rule_wrapper

    normal_spy, _ = _ml_run("lead")  # computed (or cached) BEFORE the filter is switched off
    original = rule_wrapper._History.bars

    def unfiltered(self, root, closed_by_ns=None):
        return original(self, root, None)

    monkeypatch.setattr(rule_wrapper._History, "bars", unfiltered)
    open_spy, _ = _ml_run.__wrapped__("lead", early_lead=True)  # never cached
    assert open_spy.features == normal_spy.features


def test_the_ml_canary_catches_a_misaligned_lead() -> None:
    """The lead's bars stamped 2 minutes early: the 11:00 CT decision (cutoff B, on the decision
    minute itself) then reads the planted 11:01 lead bar."""
    cut = _ml_world()["cut_b"]
    assert _ml_run("lead_b")[0].emitted_until(cut) == _ml_run("clean")[0].emitted_until(cut)
    clean_spy, _ = _ml_run("clean", lead_shift=2)
    planted_spy, _ = _ml_run("lead_b", lead_shift=2)
    assert planted_spy.emitted_until(cut)[0] != clean_spy.emitted_until(cut)[0]  # caught


def test_the_ml_canary_catches_an_engine_that_hands_the_wrapper_a_later_bar() -> None:
    """A two-bar peek (the wrapper reads only bars closed before its decision bar, so a one-bar
    peek gives it nothing new): the features emitted by cutoff A then read the planted future."""
    cut = _ml_world()["cut_a"]
    clean_spy, _ = _ml_run("clean", peek_steps=2)
    planted_spy, _ = _ml_run("own_path", peek_steps=2)
    assert planted_spy.emitted_until(cut)[0] != clean_spy.emitted_until(cut)[0]  # caught
