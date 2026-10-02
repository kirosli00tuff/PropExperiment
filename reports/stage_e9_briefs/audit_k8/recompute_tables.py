"""Auditor's independent recomputation of the K8 literal tables (Task 3 item 5).

Own code, not the generator's: every weekday 2019-05-01..2026-06-19 is classified from EC-CAL and
rules.sessions directly, then compared with strategy/members/k8/_calendar.py; the guard instants are
rebuilt from the frozen release calendar JSON and compared with _releases.GUARD_INSTANTS and with the
engine's ReleaseCalendar.by_root; in_guard is compared with ReleaseCalendar.in_fill_guard on every
instant's edges. Prints counts and differences only.
"""

from __future__ import annotations

import os

os.nice(10)

import json  # noqa: E402
import sys  # noqa: E402
from datetime import UTC, date, datetime, time, timedelta  # noqa: E402
from pathlib import Path  # noqa: E402

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))

from data.group_session import load_group_calendar  # noqa: E402
from rules import sessions  # noqa: E402
from screening.stage_e_rules import load_release_calendar  # noqa: E402
from strategy.members.k8 import _calendar as C  # noqa: E402
from strategy.members.k8 import _releases as R  # noqa: E402

FIRST, LAST = date(2019, 5, 1), date(2026, 6, 19)
RES_FIRST, RES_LAST = date(2025, 4, 1), date(2026, 6, 19)
GROUPS = {"equity": ("MES", "MNQ"), "crypto": ("MBT",), "metals": ("MGC",), "energy": ("MCL",),
          "fx": ("6C",)}
REGULAR_F = time(15, 8)
NS = 1_000_000_000


def all_days() -> list[date]:
    return [FIRST + timedelta(days=n) for n in range((LAST - FIRST).days + 1)]


def recompute_group(group: str, roots: tuple[str, ...]) -> tuple[set[date], list[str]]:
    cal = load_group_calendar(group)
    full: set[date] = set()
    notes: list[str] = []
    for d in all_days():
        if not cal.is_trade_date(d):
            if d.weekday() < 5 and not cal.is_full_closure(d):
                notes.append(f"{d} weekday non-trade-date, not a full closure (booked forward)")
            continue
        if d.weekday() >= 5:
            notes.append(f"{d} WEEKEND is_trade_date True")
        halt = cal.early_halt_ct(d)
        flats = {r: sessions.flatten_time_ct(r, d) for r in roots}
        if len(set(flats.values())) != 1:
            notes.append(f"{d} roots disagree on F: {flats}")
        f = next(iter(flats.values()))
        if halt is None and f == REGULAR_F:
            full.add(d)
        elif (halt is None) != (f == REGULAR_F):
            notes.append(f"{d} halt={halt} F={f} (tests disagree)")
    return full, notes


def in_research(d: date) -> bool:
    return RES_FIRST <= d <= RES_LAST


def main() -> None:
    mine: dict[str, set[date]] = {}
    for g, roots in GROUPS.items():
        full, notes = recompute_group(g, roots)
        mine[g] = full
        theirs = getattr(C, f"{g.upper()}_FULL_SESSIONS")
        only_mine = sorted(full - theirs)
        only_theirs = sorted(theirs - full)
        print(f"[{g}] mine {len(full)} module {len(theirs)} research mine "
              f"{sum(in_research(d) for d in full)} | only_mine {only_mine} only_module {only_theirs}")
        disagree = [n for n in notes if "disagree" in n]
        weekend = [n for n in notes if "WEEKEND" in n]
        booked = [n for n in notes if "booked" in n]
        print(f"   halt/F disagreements {len(disagree)}; weekend trade dates {len(weekend)}; "
              f"booked-forward weekdays {len(booked)}")
        if disagree and len(disagree) <= 40:
            for n in disagree:
                print("   ", n)
    members = {
        "FLIGHT_DATES": mine["equity"] & mine["metals"],
        "OILCAD_DATES": mine["energy"] & mine["fx"],
        "WKNDBTC_DATES": mine["equity"] & mine["crypto"],
    }
    for name, s in members.items():
        theirs = getattr(C, name)
        assert list(theirs) == sorted(theirs), f"{name} not sorted"
        diff = sorted(s ^ set(theirs))
        print(f"[{name}] mine {len(s)} module {len(theirs)} research "
              f"{sum(in_research(d) for d in s)} | symdiff {diff}")
    wk = members["WKNDBTC_DATES"]
    mondays = sorted(d for d in wk if in_research(d) and d.weekday() == 0
                     and d - timedelta(days=3) in wk)
    print(f"[wkndbtc] research Mondays with d and d-3 in WKNDBTC_DATES: {len(mondays)}; "
          f"after 2026-05-29: {[str(d) for d in mondays if d > date(2026, 5, 29)]}")
    res_mondays = [d for d in all_days() if in_research(d) and d.weekday() == 0]
    excluded = [d for d in res_mondays if d not in set(mondays)]
    print(f"[wkndbtc] research Mondays {len(res_mondays)}, excluded {len(excluded)}: "
          f"{[str(d) for d in excluded]}")

    # earlier clusters' frozen tables (read-only imports, test-style)
    earlier = {}
    from strategy.members.k1 import _calendar as K1
    from strategy.members.k3 import _calendar as K3
    from strategy.members.k4 import _calendar as K4
    from strategy.members.k5 import _calendar as K5
    from strategy.members.k7 import _calendar as K7
    earlier["equity"] = {date.fromisoformat(s) for s in K1.EQUITY_FULL_SESSIONS}
    earlier["fx"] = {date.fromisoformat(s) for s in K3.FX_FULL_SESSIONS}
    earlier["energy"] = {date.fromisoformat(s) for s in K4.ENERGY_FULL_SESSIONS}
    earlier["metals"] = {date.fromisoformat(s) for s in K5.METALS_FULL_SESSIONS}
    earlier["crypto"] = {date.fromisoformat(s) for s in K7.CRYPTO_FULL_SESSIONS}
    for g, e in earlier.items():
        lo, hi = min(e), max(e)
        m = {d for d in mine[g] if lo <= d <= hi}
        e_in = {d for d in e if FIRST <= d <= LAST}
        print(f"[earlier {g}] earlier {len(e)} ({lo}..{hi}); only_earlier "
              f"{[str(d) for d in sorted(e_in - m)]}; only_k8 {[str(d) for d in sorted(m - e_in)]}")

    # guard instants from the JSON
    raw = json.loads((REPO / "reports/stage_e2b_release_calendar.json").read_text())
    print(f"[releases] schema {raw.get('schema')} coverage {raw.get('coverage')} rows "
          f"{len(raw['releases'])}")
    rebuilt: dict[str, set[int]] = {r: set() for r in ("MGC", "6C", "MNQ")}
    outside = []
    not_ct_date = []
    for row in raw["releases"]:
        d = date.fromisoformat(row["date"])
        dt = datetime.fromisoformat(row["instant_utc"].replace("Z", "+00:00"))
        secs = int(dt.timestamp())
        local = datetime.fromtimestamp(secs, tz=sessions.CT) if hasattr(sessions, "CT") else None
        for root in rebuilt:
            if root in row["products"]:
                if FIRST <= d <= LAST:
                    rebuilt[root].add(secs)
                else:
                    outside.append((row["id"], root))
        if local is not None and local.date() != d:
            not_ct_date.append(row["id"])
    print(f"[releases] rows naming a K8 root outside the table range: {outside}")
    print(f"[releases] rows whose CT date differs from 'date': {not_ct_date[:10]} "
          f"(count {len(not_ct_date)})")
    cal = load_release_calendar()
    for root, s in rebuilt.items():
        theirs = set(R.GUARD_INSTANTS[root])
        engine = {ns // NS for ns in cal.by_root[root]}
        print(f"[guard {root}] rebuilt {len(s)} module {len(theirs)} engine {len(engine)} | "
              f"module^rebuilt {sorted(theirs ^ s)[:5]} | module^engine {sorted(theirs ^ engine)[:5]}"
              f" | research {sum(RES_FIRST <= datetime.fromtimestamp(x, tz=UTC).date() <= RES_LAST for x in s)}")
        assert tuple(sorted(theirs)) == R.GUARD_INSTANTS[root], f"{root} not sorted/unique"
        # in_guard vs the engine's in_fill_guard at every edge of every instant
        bad = 0
        for inst in sorted(theirs):
            for off in (-120, -60, -1, 0, 1, 59, 60, 61, 119, 120, 121, 180):
                t = inst * NS + off * NS
                if R.in_guard(root, t) != cal.in_fill_guard(root, t):
                    bad += 1
            # sub-second edges
            for t in (inst * NS + 120 * NS - 1, inst * NS - 1):
                if R.in_guard(root, t) != cal.in_fill_guard(root, t):
                    bad += 1
        print(f"[guard {root}] in_guard vs engine.in_fill_guard disagreements at edges: {bad}")
    # R-1b-1 rows present
    ids = {row[1] for row in R.GUARD_ROWS}
    print(f"[R-1b-1] WPSR-2025-12-29 in rows: {'WPSR-2025-12-29' in ids}; WPSR-2026-05-28 in rows: "
          f"{'WPSR-2026-05-28' in ids}")
    # which research-window instants meet a K8 fill minute
    ct = sessions.CT if hasattr(sessions, "CT") else None
    if ct is not None:
        flight_grid = {(8 * 60 + 35) + 5 * k for k in range(77)}
        oilcad_grid = {(8 * 60 + 5) + 5 * k for k in range(65)}
        hits = {"MGC": [], "6C": [], "MNQ": []}
        for root, grid in (("MGC", flight_grid), ("6C", oilcad_grid)):
            for inst in R.GUARD_INSTANTS[root]:
                loc = datetime.fromtimestamp(inst, tz=ct)
                if not in_research(loc.date()):
                    continue
                for m in (0, 1):
                    mod = loc.hour * 60 + loc.minute + m
                    if mod in grid:
                        hits[root].append(f"{loc:%Y-%m-%d %H:%M}+{m}")
        for inst in R.GUARD_INSTANTS["MNQ"]:
            loc = datetime.fromtimestamp(inst, tz=ct)
            if in_research(loc.date()) and (loc.hour, loc.minute) in ((18, 0), (17, 59), (14, 59), (14, 58)):
                hits["MNQ"].append(f"{loc:%Y-%m-%d %H:%M}")
        for root, h in hits.items():
            print(f"[A3 {root}] research instants meeting a fill minute: {len(h)} {h}")


if __name__ == "__main__":
    main()
