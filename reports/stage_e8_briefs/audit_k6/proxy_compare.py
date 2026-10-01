"""Auditor's comparison of K6-limitcont-01's settlement proxy with the engine's (item 6, K6-L-06).

Run from the repository root:
    PYTHONPYCACHEPREFIX=<scratch> uv run python reports/stage_e8_briefs/audit_k6/proxy_compare.py

Synthetic livestock bars only. For a set of days (regular; 12:59 missing -> fallback; zero volume
in the window; the early halts 2025-11-28 (12:05) and 2025-12-24 (12:15); bars only after 13:00;
bars after the window present), the engine's screening.stage_e_rules._Settlement is fed every bar
as StageERules.observe feeds it, and the member's LimitCont is fed the same bars through
on_minute with a flat account. Then, for every trade date, the engine's proxy of that date is
compared with the member's settlement(date). Also compares the member's d-1/d-2/d-3 mapping with
the engine's prior_settlement mapping (data.group_session.previous_trade_date) on every livestock
trade date of the range, and the member's settlement_window with rules.price_limits
.settlement_window_ct. Prints counts and differences; writes nothing.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from types import MappingProxyType

from data.group_session import load_group_calendar
from data.group_session import previous_trade_date as cal_prev
from rules import price_limits as pl
from rules.products import PRICE_SCALE, product
from rules.xfa_rules import Phase, Status
from screening.stage_e_rules import _Settlement
from strategy.interface import Bar
from strategy.members.k6 import _calendar as cal_mod
from strategy.members.k6 import limitcont
from strategy.stage_e.interface import MemberAccountView, MinuteView
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
BASE = {"HE": 90.0, "LE": 220.0}
problems: list[str] = []


def ns_at(day: date, hh: int, mm: int) -> int:
    return int(datetime.combine(day, time(hh, mm), tzinfo=CT).astimezone(UTC).timestamp()) * NS


def px(root: str, ticks: int) -> float:
    base = round(Decimal(repr(BASE[root])) / product(root).vendor_tick)
    return (int(base) + ticks) * product(root).vendor_tick_fixed / PRICE_SCALE


def bar(root: str, day: date, hh: int, mm: int, close_ticks: int, volume: int = 10,
        iid: int = 777, halt: time | None = None) -> Bar:
    p = px(root, close_ticks)
    return Bar(ns_at(day, hh, mm), p, p, p, p, volume, iid, f"{root}M5", day, False, False, halt,
               False, False, 0, False)


def minutes(a: tuple[int, int], b: tuple[int, int]):
    t = datetime(2000, 1, 3, *a)
    end = datetime(2000, 1, 3, *b)
    while t < end:
        yield t.hour, t.minute
        t += timedelta(minutes=1)


def day_bars(root: str, day: date, closes: dict[tuple[int, int], int] | None = None,
             skip: set[tuple[int, int]] = frozenset(), volumes: dict | None = None,
             start=(8, 30), end=(13, 5), halt: time | None = None, ids: dict | None = None,
             level: int = 0) -> list[Bar]:
    closes, volumes, ids = closes or {}, volumes or {}, ids or {}
    out = []
    for hh, mm in minutes(start, end):
        if (hh, mm) in skip:
            continue
        out.append(bar(root, day, hh, mm, closes.get((hh, mm), level), volumes.get((hh, mm), 10),
                       ids.get((hh, mm), 777), halt))
    return out


def account(root: str) -> MemberAccountView:
    return MemberAccountView(Phase.XFA, Status.ACTIVE, None, 0, 0, MappingProxyType({root: 0}),
                             MappingProxyType({root: 0}), MappingProxyType({root: None}),
                             MappingProxyType({root: 0}))


def compare(root: str, scenario: str, bars_by_day: dict[date, list[Bar]]) -> None:
    eng = _Settlement(root)
    mem = limitcont.make_he() if root == "HE" else limitcont.make_le()
    all_bars = [b for d in sorted(bars_by_day) for b in bars_by_day[d]]
    for b in all_bars:
        eng.add(b)
        mem.on_minute(MinuteView(b.ts_event_ns, MappingProxyType({root: b})), account(root))
    eng.finalize()
    for d in sorted(bars_by_day):
        e = eng.proxies.get(d)
        m, ids = mem.settlement(d)
        ok = (e is None and m is None) or (e is not None and m is not None and e == m)
        tag = "OK" if ok else "DIFF"
        print(f"  {root} {scenario} {d}: engine={e} member={m} ids={set(ids)} {tag}")
        if not ok:
            problems.append(f"{root} {scenario} {d}")


def main() -> None:
    mon, tue, wed = date(2025, 5, 5), date(2025, 5, 6), date(2025, 5, 7)
    xmas, tg = date(2025, 12, 24), date(2025, 11, 28)  # livestock halts 12:15 and 12:05
    for root in ("HE", "LE"):
        print(f"== {root}")
        compare(root, "regular", {mon: day_bars(root, mon, {(12, 59): 7, (13, 0): 11, (13, 4): 13})})
        compare(root, "fallback(12:59 missing)", {
            mon: day_bars(root, mon, {(12, 58): 3, (13, 0): 11}, skip={(12, 59)})})
        compare(root, "zero volume 12:59", {
            mon: day_bars(root, mon, {(12, 58): 3, (12, 59): 5}, volumes={(12, 59): 0})})
        compare(root, "zero volume 12:59 and 12:58 missing", {
            mon: day_bars(root, mon, {(12, 57): 2, (12, 59): 5}, volumes={(12, 59): 0}, skip={(12, 58)})})
        compare(root, "bars only after 13:00", {mon: day_bars(root, mon, start=(13, 0))})
        compare(root, "halt 12:15 (2025-12-24)", {
            xmas: day_bars(root, xmas, {(12, 13): 2, (12, 14): 9}, end=(12, 15), halt=time(12, 15))})
        compare(root, "halt 12:15, 12:14 missing", {
            xmas: day_bars(root, xmas, {(12, 12): 4, (12, 13): 2}, skip={(12, 14)}, end=(12, 15),
                           halt=time(12, 15))})
        compare(root, "halt 12:05 (2025-11-28)", {
            tg: day_bars(root, tg, {(12, 3): 1, (12, 4): 6}, end=(12, 5), halt=time(12, 5))})
        compare(root, "halt day but bars run to 13:05 (label only)", {
            xmas: day_bars(root, xmas, {(12, 14): 9, (12, 59): 7}, halt=time(12, 15))})
        compare(root, "three days, ids differ on d-2", {
            mon: day_bars(root, mon, {(12, 59): 1}), tue: day_bars(root, tue, {(12, 59): 2}, ids={(12, 59): 778}),
            wed: day_bars(root, wed, {(12, 59): 3})})
        compare(root, "a day with no bar at all between two days", {
            mon: day_bars(root, mon, {(12, 59): 1}), wed: day_bars(root, wed, {(12, 59): 3})})
    # window equality on every livestock trade date
    cal = load_group_calendar("livestock")
    first, last = date(2019, 5, 1), date(2026, 6, 19)
    bad, n, moved = [], 0, 0
    d = first
    while d <= last:
        if d.weekday() < 5 and cal.is_trade_date(d):
            n += 1
            for root in ("HE", "LE"):
                w = pl.settlement_window_ct(root, d)
                m = limitcont.settlement_window(d)
                if (w.start_ct, w.end_ct) != m:
                    bad.append((str(d), root, str(w.start_ct), str(w.end_ct), str(m)))
            if m != limitcont.SETTLEMENT_WINDOW_LIVESTOCK:
                moved += 1
        d += timedelta(days=1)
    print(f"settlement_window == settlement_window_ct on {n} livestock trade dates x 2 roots: "
          f"{'OK' if not bad else 'DIFF'} ({len(bad)} mismatches; {moved} dates moved by a halt) {bad[:5]}")
    if bad:
        problems.append("settlement_window")
    # d-1/d-2/d-3 mapping vs the engine's prior_settlement mapping (previous_trade_date on the calendar)
    bad = []
    d = first + timedelta(days=10)
    while d <= last:
        if d.weekday() < 5 and cal.is_trade_date(d):
            x, chain = d, []
            for _ in range(3):
                x = cal_mod.previous_trade_date(cal_mod.LIVESTOCK_TRADE_DATES, x)
                chain.append(x)
            y, chain2 = d, []
            for _ in range(3):
                y = cal_prev(cal, y)
                chain2.append(y)
            if chain != chain2:
                bad.append((str(d), chain, chain2))
        d += timedelta(days=1)
    print(f"member d-1,d-2,d-3 chain == calendar previous_trade_date chain: "
          f"{'OK' if not bad else 'DIFF'} ({len(bad)} mismatches) {bad[:3]}")
    if bad:
        problems.append("d-k chain")
    print("PROBLEMS:", problems if problems else "none")


if __name__ == "__main__":
    main()
