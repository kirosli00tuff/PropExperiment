"""HarnessReviewer (E.5 A3): independent recomputation of Rule H-1 and the day_rule effects.

Loads the v4 rules/sessions.py from git HEAD as a separate module and compares it with the
working-tree v5 module. Read-only on the repository.
"""
from __future__ import annotations

import subprocess
import sys
import types
from collections import Counter
from datetime import date, datetime, time, timedelta

REPO = "/home/kiros-li/Documents/GitHub/PropExperiment"
sys.path.insert(0, REPO)

from data.calendars import GROUPS  # noqa: E402
from data.cme_calendar import HOLIDAYS as EQ  # noqa: E402
from data.cme_calendar import HolidayKind  # noqa: E402
from rules import sessions as S  # noqa: E402

src = subprocess.check_output(["git", "-C", REPO, "show", "HEAD:rules/sessions.py"]).decode()
v4 = types.ModuleType("sessions_v4")
v4.__file__ = REPO + "/rules/sessions_v4_scratch.py"
sys.modules["sessions_v4"] = v4
exec(compile(src, "sessions_v4", "exec"), v4.__dict__)

ROOT = {"equity": "NQ", "rates": "ZN", "fx": "6E", "energy": "CL", "metals": "GC",
        "crypto": "MBT", "grains": "ZC", "livestock": "LE"}
assert set(ROOT) == set(GROUPS), (set(ROOT), set(GROUPS))
DERIVED = "topstep_derived_e5_equity_calendar"


def minus(t: time, d: timedelta) -> time:
    return (datetime.combine(date(2000, 1, 3), t) - d).time()


def rule(first: date, last: date, lead) -> dict[date, time | None]:
    out = {}
    for d, h in EQ.items():
        if not (first <= d <= last) or d.weekday() >= 5:
            continue
        lead_y = lead[d.year] if isinstance(lead, dict) else lead
        out[d] = None if h.kind is HolidayKind.FULL_CLOSURE else minus(h.halt_ct, lead_y)
    return out


def fmt(t) -> str:
    return "closed" if t is None else f"{t:%H:%M}"


def st(r) -> str:
    return "closed" if r.closed else f"{r.flatten_ct:%H:%M}"


print("=== (a) Rule H-1 on 2024-2026 vs the published rows ===")
pub = {d: r.close_by_ct for d, r in S.TOPSTEP_HOLIDAYS.items() if r.source != DERIVED}
r_pub = rule(date(2024, 1, 1), date(2026, 12, 31),
             {2024: timedelta(minutes=30), 2025: timedelta(minutes=30), 2026: timedelta(minutes=15)})
print("published rows:", len(pub), "| rule dates 2024-2026:", len(r_pub),
      "| in domain and matching:", sum(1 for d in pub if d in r_pub and r_pub[d] == pub[d]))
for d in sorted(set(pub) | set(r_pub)):
    a, b = r_pub.get(d, "n/a"), pub.get(d, "n/a")
    if a == "n/a" or b == "n/a" or a != b:
        print("  DIFF", d, EQ[d].name if d in EQ else "(no equity entry)",
              "| rule", a if a == "n/a" else fmt(a), "| published", b if b == "n/a" else fmt(b))
v4rows = {d: (r.close_by_ct, r.source) for d, r in v4.TOPSTEP_HOLIDAYS.items()}
v5from2024 = {d: (r.close_by_ct, r.source) for d, r in S.TOPSTEP_HOLIDAYS.items()
              if d >= date(2024, 1, 1)}
print("v4 table == v5 table from 2024-01-01:", v4rows == v5from2024, len(v4rows), len(v5from2024))
print("v4 lead table:", {y: int(l.total_seconds() // 60) for y, l in v4.TOPSTEP_EARLY_CLOSE_LEAD.items()})
print("v5 lead table:", {y: int(l.total_seconds() // 60) for y, l in S.TOPSTEP_EARLY_CLOSE_LEAD.items()})
print("v4 SCHEDULE_YEARS:", sorted(v4.TOPSTEP_SCHEDULE_YEARS), "v5:", sorted(S.TOPSTEP_SCHEDULE_YEARS),
      "v5 DERIVED_YEARS:", sorted(S.TOPSTEP_DERIVED_YEARS))

print("=== (b) Rule H-1 on 2019-05-01..2023-12-31 vs the derived rows ===")
der = {d: r.close_by_ct for d, r in S.TOPSTEP_HOLIDAYS.items() if r.source == DERIVED}
r_der = rule(date(2019, 5, 1), date(2023, 12, 31), timedelta(minutes=30))
uns = [d for d, _ in S.TOPSTEP_UNSETTLED_DATES]
print("derived rows:", len(der), "| rule dates:", len(r_der), "| unsettled:", [str(d) for d in uns])
print("rows in span, weekdays:", all(date(2019, 5, 1) <= d <= date(2023, 12, 31) and d.weekday() < 5 for d in der))
print("rule minus unsettled == derived rows:", {d: v for d, v in r_der.items() if d not in set(uns)} == der)
print("derived dates not in rule:", [str(d) for d in der if d not in r_der])
print("value mismatches:", [(str(d), fmt(der[d]), fmt(r_der[d])) for d in der if d in r_der and der[d] != r_der[d]])
print("unsettled subset of rule dates:", set(uns) <= set(r_der),
      "| rule dates neither row nor unsettled:", [str(d) for d in r_der if d not in der and d not in set(uns)])
print("--- every equity entry 2019-05-01..2023-12-31 (weekends included) ---")
for d in sorted(EQ):
    if date(2019, 5, 1) <= d <= date(2023, 12, 31):
        h = EQ[d]
        tag = "ROW" if d in der else ("UNSETTLED" if d in set(uns) else "NONE")
        print(f"  {d} wd{d.weekday()} {h.kind.name[:4]} {fmt(h.halt_ct):6} ev={h.evidence}/{h.time_evidence:9} {tag:9} {h.name}")
print("published-date names 2024-2026:", sorted({EQ[d].name for d in pub if d in EQ}))
print("equity entries before 2019-05-01:", [(str(d), EQ[d].name, fmt(EQ[d].halt_ct)) for d in sorted(EQ) if d < date(2019, 5, 1)])


def weekdays(a: date, b: date):
    d = a
    while d <= b:
        if d.weekday() < 5:
            yield d
        d += timedelta(days=1)


print("=== (c) day_rule v4 vs v5 ===")
n_after = diff_after = 0
for d in weekdays(date(2024, 1, 1), date(2027, 12, 31)):
    for g, root in ROOT.items():
        n_after += 1
        a, b = v4.day_rule(root, d), S.day_rule(root, d)
        if (a.closed, a.flatten_ct, a.reasons) != (b.closed, b.flatten_ct, b.reasons):
            diff_after += 1
print("2024-01-01..2027-12-31: results", n_after, "| differences (closed, F, reasons):", diff_after)
changed = []
for d in weekdays(date(2019, 5, 1), date(2023, 12, 31)):
    for g, root in ROOT.items():
        a, b = v4.day_rule(root, d), S.day_rule(root, d)
        if (a.closed, a.flatten_ct) != (b.closed, b.flatten_ct):
            changed.append((g, d, st(a), st(b)))
print("2019-05-01..2023-12-31: changed (group, date):", len(changed), "| dates:", len({d for _, d, _, _ in changed}))
print("per group:", dict(Counter(g for g, *_ in changed)))
print("moved later:", [c for c in changed if c[2] != "closed" and c[3] != "closed" and c[3] > c[2]]
      + [c for c in changed if c[2] == "closed" and c[3] != "closed"])
non_eq = sorted({d for _, d, _, _ in changed if d not in EQ})
print("changed dates not in the equity calendar:", [str(d) for d in non_eq])
for c in changed:
    if c[1] in non_eq:
        print("   ", c)
pre = [(g, str(d), st(v4.day_rule(root, d)), st(S.day_rule(root, d)))
       for d in weekdays(date(2019, 1, 1), date(2019, 4, 30)) for g, root in ROOT.items()
       if (v4.day_rule(root, d).closed, v4.day_rule(root, d).flatten_ct)
       != (S.day_rule(root, d).closed, S.day_rule(root, d).flatten_ct)]
print("2019-01-01..2019-04-30 changes (the 2019 lead applies to the whole year):", len(pre))
for p in pre:
    print("   ", p)

print("=== (d) the audit's 15 FX dates (6E) ===")
FX = [date(2019, 7, 3), date(2022, 1, 17), date(2022, 2, 21), date(2022, 5, 30), date(2022, 7, 4),
      date(2022, 9, 5), date(2022, 11, 24), date(2023, 1, 16), date(2023, 2, 20), date(2023, 5, 29),
      date(2023, 6, 19), date(2023, 7, 3), date(2023, 7, 4), date(2023, 9, 4), date(2023, 11, 23)]
hol = S.default_holidays()
for d in FX:
    a, b = v4.day_rule("6E", d), S.day_rule("6E", d)
    print(f"  {d} fx-cal={'yes' if d in hol['fx'] else 'no ':3} v4 {st(a)} -> v5 {st(b)} :: {b.reasons}")
others_fx = sorted(d for g, d, _, _ in changed if g == "fx" and d not in FX)
print("other FX dates changed, not in the audit's 15:", [(str(d), st(v4.day_rule('6E', d)), st(S.day_rule('6E', d))) for d in others_fx])

for g, root in (("energy", "CL"), ("metals", "GC")):
    print(f"=== (e) {g} ({root}): every calendar entry 2019-05..2023-12 and every derived-row date ===")
    dates = sorted(set(d for d in hol[g] if date(2019, 5, 1) <= d <= date(2023, 12, 31)) | set(der) | set(uns))
    for d in dates:
        if d.weekday() >= 5:
            continue
        h = hol[g].get(d)
        a, b = v4.day_rule(root, d), S.day_rule(root, d)
        row = fmt(S.TOPSTEP_HOLIDAYS[d].close_by_ct) if d in S.TOPSTEP_HOLIDAYS else ("UNSETTLED" if d in set(uns) else "-")
        cal = f"{h.kind.name[:4]} {fmt(h.halt_ct)}" if h else "NO ENTRY   "
        flag = "" if st(a) == st(b) else "  <- changed"
        print(f"  {d} cal={cal:12} row={row:9} v4 {st(a):6} v5 {st(b):6}{flag} :: {h.name if h else EQ[d].name + ' (equity)'}")
