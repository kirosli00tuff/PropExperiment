"""Auditor's independent recomputation of the K6 literal tables (Stage E.8 Task 3, item 5).

Run from the repository root:
    PYTHONPYCACHEPREFIX=<scratch> uv run python reports/stage_e8_briefs/audit_k6/recompute_tables.py

Recomputes, from the frozen sources and without the generator:
- GRAIN_TRADE_DATES / LIVESTOCK_TRADE_DATES: every weekday d in 2019-05-01..2026-06-19 with
  load_group_calendar(group).is_trade_date(d);
- GRAIN_FULL_SESSIONS / LIVESTOCK_FULL_SESSIONS: trade dates with early_halt_ct None AND
  rules.sessions.flatten_time_ct(root, d) == the regular F for EVERY root of the group (K3-L-11);
- LIVESTOCK_EARLY_HALT_CT: every livestock trade date with an early halt;
- WASDE_DATES: every row of reports/stage_e2b_release_calendar.json with release WASDE at 12:00
  America/New_York whose CT date lies in the range;
- LIMIT_PERIODS: every HARD_DAILY period of rules.price_limits.LIMITS for HE and LE intersecting
  the range, with ticks = amount x vendor_price_factor / vendor_tick, checked against
  limit_period(root, d) on every livestock trade date;
- DROPPED_LIMIT_DATES: the livestock trade dates 2026-06-01..2026-06-18 for LE.
Prints counts and every difference. Writes nothing.
"""

from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from data.group_session import load_group_calendar
from rules import price_limits as pl
from rules import sessions
from rules.products import product
from strategy.members.k6 import _calendar as cal_mod
from strategy.members.k6 import _limits as lim_mod
from strategy.members.k6 import _wasde as wasde_mod

FIRST, LAST = date(2019, 5, 1), date(2026, 6, 19)
RESEARCH = (date(2025, 4, 1), date(2026, 6, 19))
ROOTS = {"grains": ("ZC", "ZW", "ZS", "ZM", "ZL"), "livestock": ("HE", "LE")}
REGULAR_F = {"grains": time(13, 18), "livestock": time(13, 3)}
CT = ZoneInfo("America/Chicago")
problems: list[str] = []


def days(a: date, b: date):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)


def diff(name: str, mine, theirs) -> None:
    mine, theirs = set(mine), set(theirs)
    only_mine, only_theirs = sorted(mine - theirs), sorted(theirs - mine)
    status = "OK" if not only_mine and not only_theirs else "DIFF"
    print(f"{name}: recomputed {len(mine)}, module {len(theirs)}: {status}")
    if only_mine:
        print("   only in recomputation:", [str(x) for x in only_mine][:20])
    if only_theirs:
        print("   only in module:", [str(x) for x in only_theirs][:20])
    if status != "OK":
        problems.append(name)


def group_tables(group: str):
    cal = load_group_calendar(group)
    trade, full, halts, disagree = [], set(), {}, []
    for d in days(FIRST, LAST):
        if d.weekday() >= 5 or not cal.is_trade_date(d):
            continue
        trade.append(d)
        halt = cal.early_halt_ct(d)
        flats = {r: sessions.flatten_time_ct(r, d) for r in ROOTS[group]}
        if len(set(flats.values())) != 1:
            problems.append(f"{group} {d}: F differs across roots {flats}")
        f = flats[ROOTS[group][0]]
        if halt is not None:
            halts[d] = halt
        no_halt, regular = halt is None, f == REGULAR_F[group]
        if no_halt and regular:
            full.add(d)
        if no_halt != regular:
            disagree.append((d, halt, f))
    return trade, full, halts, disagree


def main() -> None:
    for group, (tt, ft, ht) in (("grains", ("GRAIN_TRADE_DATES", "GRAIN_FULL_SESSIONS", None)),
                                ("livestock", ("LIVESTOCK_TRADE_DATES", "LIVESTOCK_FULL_SESSIONS",
                                               "LIVESTOCK_EARLY_HALT_CT"))):
        trade, full, halts, disagree = group_tables(group)
        mod_trade = getattr(cal_mod, tt)
        assert list(mod_trade) == sorted(mod_trade), f"{tt} not sorted"
        diff(tt, trade, mod_trade)
        diff(ft, full, getattr(cal_mod, ft))
        print(f"   {group}: early-halt vs F disagreements: "
              f"{[(str(d), str(h), str(f)) for d, h, f in disagree]}")
        removed_research = sorted(d for d in trade if d not in full and RESEARCH[0] <= d <= RESEARCH[1])
        print(f"   {group}: research-window dates removed from full sessions: "
              f"{[str(d) for d in removed_research]}")
        if ht:
            mod_h = getattr(cal_mod, ht)
            diff(ht + " (dates)", halts, mod_h)
            bad = [(str(d), str(h), str(mod_h.get(d))) for d, h in halts.items() if mod_h.get(d) != h]
            print(f"   {ht} time mismatches: {bad}")
            if bad:
                problems.append(ht + " times")
        if group == "grains":
            late = sorted(d for d in cal.scheduled_late_opens if RESEARCH[0] <= d <= RESEARCH[1]) \
                if (cal := load_group_calendar(group)) else []
            print(f"   grains: research-window scheduled late opens {[str(d) for d in late]}; "
                  f"in full sessions: {[d in full for d in late]}")
    # previous_trade_date equals the calendar's for every date in the range (both groups)
    from data.group_session import previous_trade_date as cal_prev
    for group, tt in (("grains", "GRAIN_TRADE_DATES"), ("livestock", "LIVESTOCK_TRADE_DATES")):
        cal = load_group_calendar(group)
        table = getattr(cal_mod, tt)
        bad = []
        for d in days(FIRST + timedelta(days=14), LAST):
            a = cal_mod.previous_trade_date(table, d)
            b = cal_prev(cal, d)
            if a != b:
                bad.append((str(d), str(a), str(b)))
        print(f"previous_trade_date({tt}) vs data.group_session.previous_trade_date: "
              f"{'OK' if not bad else 'DIFF'} ({len(bad)} mismatches) {bad[:5]}")
        if bad:
            problems.append("previous_trade_date " + group)

    # WASDE
    raw = json.load(open("reports/stage_e2b_release_calendar.json", encoding="utf-8"))
    kept, other, all_wasde = [], [], 0
    for r in raw["releases"]:
        if r["release"] != "WASDE":
            continue
        all_wasde += 1
        local = datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00")).astimezone(CT)
        d = local.date()
        if not FIRST <= d <= LAST:
            continue
        if r["time_local"] == "12:00" and r["tz"] == "America/New_York":
            kept.append(d)
        else:
            other.append((r["id"], r["time_local"], r["tz"]))
    print(f"WASDE rows in file: {all_wasde}; in range at 12:00 ET: {len(kept)}; other times: {other}")
    diff("WASDE_DATES", kept, wasde_mod.WASDE_DATES)
    research = sorted(d for d in kept if RESEARCH[0] <= d <= RESEARCH[1])
    print(f"   research-window WASDE dates ({len(research)}): {[str(d) for d in research]}")
    print(f"   DROPPED_WASDE: {wasde_mod.DROPPED_WASDE}")
    for d in (date(2025, 10, 9), date(2025, 11, 10)):
        print(f"   {d} in WASDE_DATES: {d in wasde_mod.WASDE_DATES}")

    # limits
    for root in ("HE", "LE"):
        p_root = product(root)
        rows = []
        for p in pl.LIMITS[root]:
            if p.end < FIRST or p.start > LAST:
                continue
            if p.kind is not pl.LimitKind.HARD_DAILY:
                problems.append(f"{root} period {p.start} not HARD_DAILY")
            rows.append((p.start, p.end, str(p.amount), p.status))
        mod_rows = lim_mod.LIMIT_PERIODS[root]
        same = [(a, b, c) for a, b, c, _ in rows] == list(mod_rows)
        print(f"LIMIT_PERIODS[{root}]: recomputed {len(rows)} periods, module {len(mod_rows)}: "
              f"{'OK' if same else 'DIFF'}")
        if not same:
            problems.append(f"LIMIT_PERIODS {root}")
            print("   recomputed:", rows)
            print("   module:", mod_rows)
        print("   statuses:", [(str(a), str(b), c, s) for a, b, c, s in rows if s != "sourced"])
        # ticks on every livestock trade date
        from strategy.members.k6.limitcont import limit_ticks
        cal = load_group_calendar("livestock")
        bad = []
        ticks_seen = set()
        for d in days(FIRST, LAST):
            if d.weekday() >= 5 or not cal.is_trade_date(d):
                continue
            per = pl.limit_period(root, d)
            expect = per.amount * p_root.vendor_price_factor / p_root.vendor_tick
            got = limit_ticks(root, d)
            ticks_seen.add((str(per.amount), got))
            if Decimal(got) != expect or expect != expect.to_integral_value():
                bad.append((str(d), str(expect), got))
        print(f"   limit_ticks == limit_period x factor / tick on every livestock trade date: "
              f"{'OK' if not bad else 'DIFF'} {bad[:5]}; amounts->ticks {sorted(ticks_seen)}")
        if bad:
            problems.append(f"limit_ticks {root}")
    # dropped LE dates
    cal = load_group_calendar("livestock")
    june = [d for d in days(date(2026, 6, 1), date(2026, 6, 18)) if d.weekday() < 5 and cal.is_trade_date(d)]
    diff("DROPPED_LIMIT_DATES[LE]", june, lim_mod.DROPPED_LIMIT_DATES["LE"])
    print(f"   DROPPED_LIMIT_DATES[HE]: {lim_mod.DROPPED_LIMIT_DATES['HE']}")
    for d in june:
        per = pl.limit_period("LE", d)
        if (str(per.amount), per.status) != ("0.0725", "bracketed"):
            problems.append(f"LE {d} period {per.amount} {per.status}")
    w = pl.SETTLEMENT_WINDOW_CT["livestock"]
    print(f"SETTLEMENT_WINDOW_LIVESTOCK module {lim_mod.SETTLEMENT_WINDOW_LIVESTOCK} vs engine "
          f"({w.start_ct}, {w.end_ct}): {'OK' if (w.start_ct, w.end_ct) == lim_mod.SETTLEMENT_WINDOW_LIVESTOCK else 'DIFF'}")
    # source hashes recorded by the modules
    import hashlib
    for mod in (cal_mod, wasde_mod, lim_mod):
        for rel, sha in mod.SOURCE_SHA256:
            now = hashlib.sha256(open(rel, "rb").read()).hexdigest()
            print(f"   {mod.__name__.split('.')[-1]} source {rel}: {'OK' if now == sha else 'CHANGED'}")
            if now != sha:
                problems.append(f"source hash {rel}")
    print("PROBLEMS:", problems if problems else "none")


if __name__ == "__main__":
    main()
