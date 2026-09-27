"""Auditor recompute of MONTH_END from EC-CAL (prints counts and diffs only)."""
import sys; sys.path.insert(0, ".")
from datetime import date, timedelta
from data.group_session import load_group_calendar
from strategy.members.k2._month_end import MONTH_END, MONTH_END_SOURCE_SHA256
cal = load_group_calendar("rates")
attrs = [a for a in dir(cal) if not a.startswith("_")]
print("calendar attrs", attrs)
start, end = date(2019, 5, 1), date(2026, 6, 19)
# coverage probe
try:
    print("coverage", getattr(cal, "start", None), getattr(cal, "end", None), getattr(cal, "coverage", None))
except Exception as e:
    print("coverage err", e)
tds = [d for d in (start + timedelta(i) for i in range((end - start).days + 1)) if cal.is_trade_date(d)]
print("n trade dates in", start, end, len(tds))
by_month = {}
for d in tds:
    by_month.setdefault((d.year, d.month), []).append(d)
rows = []
for (y, m), ds in sorted(by_month.items()):
    n = ds[-1]
    # N must be the true last trade date of the month: check the month has no later weekday inside coverage
    last_dom = (date(y + (m == 12), (m % 12) + 1, 1) - timedelta(days=1))
    if last_dom > end:
        continue  # month's end outside coverage
    i = tds.index(n)
    rows.append((f"{y:04d}-{m:02d}", tds[i - 1].isoformat(), n.isoformat()))
mine = tuple(rows); theirs = tuple(MONTH_END)
print("recomputed rows", len(mine), "table rows", len(theirs), "equal", mine == theirs)
if mine != theirs:
    sm, st = set(mine), set(theirs)
    print("only mine", sorted(sm - st)[:10]); print("only table", sorted(st - sm)[:10])
halts = [d for d in tds if cal.early_halt_ct(d) is not None]
print("early halts among trade dates", len(halts))
ev = sorted({date.fromisoformat(x) for _, a, b in MONTH_END for x in (a, b)})
print("event dates", len(ev), "early-halt event dates", [d.isoformat() for d in ev if cal.early_halt_ct(d) is not None])
for probe in (date(2019,12,24), date(2025,11,28), date(2021,5,31), date(2020,1,27)):
    print(probe, "trade", cal.is_trade_date(probe), "halt", cal.early_halt_ct(probe))
# is the last trade date of May 2026 really 2026-05-29 (weekday check)
print("2026-05-29 weekday", date(2026,5,29).weekday(), "2026-06-01 trade", cal.is_trade_date(date(2026,6,1)))
