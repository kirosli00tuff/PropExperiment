"""Auditor's engine probes for K6 cases the coders' tests may not pin (Stage E.8 Task 3, items
3, 6, 9). Synthetic bars through the real engine via the test kits; prints fills and intents.

    PYTHONPATH=. uv run python reports/stage_e8_briefs/audit_k6/probes.py

1. crushgap: a D9.7 forced exit (ZS close at the upper stop at 10:30) -> the engine closes at
   10:31 (price_limit_exit); the member sends no 13:13 exit and no second entry.
2. wasdepre: the 11:00 bar closes at the upper stop after the release -> the D9.7 exit fills at the
   11:01 open (exempt from the fill guard); the member sends nothing more.
3. limitcont: d = 2025-12-26 (Friday), d-1 = 2025-12-24 (livestock halt 12:15): d-1's proxy is the
   12:14 bar's close at +L (limit-up by the halt window), d-2 = 12-23, d-3 = 12-22 flat -> BUY at
   08:45 on 12-26 through the real engine (whose D9.7 reference is the same proxy).
4. limitcont: the same with d-1's 12:14 bar one tick short of L -> no trade.
5. crushgap on a Monday whose Friday had the 13:14 ZS bar missing -> no trade (K6-L-05), and the
   control with the bar present -> a trade.
"""

from __future__ import annotations

from datetime import date, time

from tests import test_k6_members_crushgap as cg
from tests import test_k6_members_limitcont as lk
from tests import test_k6_members_wasde as wk
from tests.test_k6_members_ports import Day, hm, stop_offsets
from strategy.members.k6 import limitcont


def probe_crushgap_d97() -> None:
    up, _ = stop_offsets("ZS", cg.TUE, 0)  # MON's 13:14 ZS close is the base: the D9.7 reference
    days = cg.legs_days(cg.MON, cg.TUE, opens={"ZM": 10})  # G = +220 units: BUY ZS
    zs_tue = days["ZS"][1]
    days["ZS"][1] = Day(cg.TUE, paths={**zs_tue.paths, hm(10, 30): (0, up, 0, up)})
    res = cg.run_legs(cg.mk(), days)
    print("1 crushgap D9.7:", cg.fills(res))
    print("  intents:", cg.intents(res))
    ok = cg.fills(res) == [(cg.TUE, "08:31", "buy", "strategy"), (cg.TUE, "10:31", "sell", "price_limit_exit")] \
        and [i[1] for i in cg.intents(res)] == ["08:30"]
    print("  ->", "OK" if ok else "UNEXPECTED")


def probe_wasdepre_d97() -> None:
    root = "ZC"
    import rules.price_limits as pl
    from datetime import datetime
    from decimal import Decimal
    from zoneinfo import ZoneInfo
    ct = ZoneInfo("America/Chicago")
    s = Decimal(repr(lk.px(root, 0)))  # PRIOR's proxy: its 12:59 close? grains window is [13:14, 13:15)
    band = pl.limit_band(root, wk.WASDE, datetime.combine(wk.WASDE, time(11, 0), tzinfo=ct), s)
    upper = pl.stop_levels(band, s).upper
    k = 0
    while Decimal(repr(lk.px(root, k))) < upper:
        k += 1
    day = wk.pre_day(wk.WASDE, closes={hm(11, 0): k})  # the release bar jumps to the stop level
    res = lk.run(wk.pre(root), [lk.Day(wk.PRIOR), day], releases=wk.release_at(root, wk.WASDE, 11, 0))
    print("2 wasdepre D9.7 at the release:", lk.fills(res))
    print("  intents:", lk.intents(res))
    f = lk.fills(res)
    ok = f == [(wk.WASDE, "10:30", "buy", "strategy"), (wk.WASDE, "11:01", "sell", "price_limit_exit")] \
        and [i[1] for i in lk.intents(res)] == ["10:29"]
    print("  ->", "OK" if ok else "UNEXPECTED (check: is the D9.7 exit exempt from the 11:00-11:02 fill guard?)")


def probe_limitcont_halt_d1(short: int = 0) -> None:
    root = "LE"
    d3, d2, d1, d = date(2025, 12, 22), date(2025, 12, 23), date(2025, 12, 24), date(2025, 12, 26)
    lim = limitcont.limit_ticks(root, d1)  # 290 in 2025-12
    halt_day = lk.Day(d1, level=lim - short, halt=time(12, 15), end=hm(12, 15))
    days = [lk.Day(d3), lk.Day(d2), halt_day, lk.Day(d, level=lim - short)]
    res = lk.run(lk.m(root), days)
    print(f"{'3' if not short else '4'} limitcont d-1 = 2025-12-24 halt (short {short}):", lk.fills(res))
    print("  intents:", lk.intents(res))
    if not short:
        ok = lk.fills(res) == [(d, "08:45", "buy", "strategy"), (d, "12:59", "sell", "strategy")]
    else:
        ok = lk.fills(res) == [] and lk.intents(res) == []
    print("  ->", "OK" if ok else "UNEXPECTED")


def probe_crushgap_missing_1314() -> None:
    days = cg.legs_days(cg.FRI, cg.MON, opens={"ZM": 10}, prev_ZS={"skip": frozenset({hm(13, 14)})})
    res = cg.run_legs(cg.mk(), days)
    control = cg.run_legs(cg.mk(), cg.legs_days(cg.FRI, cg.MON, opens={"ZM": 10}))
    print("5 crushgap Friday 13:14 ZS bar missing:", cg.fills(res), "| control:", cg.fills(control))
    print("  ->", "OK" if cg.fills(res) == [] and len(cg.fills(control)) == 2 else "UNEXPECTED")


if __name__ == "__main__":
    probe_crushgap_d97()
    probe_wasdepre_d97()
    probe_limitcont_halt_d1(0)
    probe_limitcont_halt_d1(1)
    probe_crushgap_missing_1314()
