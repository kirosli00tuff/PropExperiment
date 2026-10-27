"""Trade-date counts from the program grains calendar (code only; no market data)."""
from datetime import date
from data.group_session import load_group_calendar, trade_dates_between
cal = load_group_calendar("grains")
print("coverage", cal.coverage)
disc = trade_dates_between(cal, date(2020, 12, 1), date(2024, 2, 29))
print("discovery dates", len(disc), "first", disc[0], "burn-in last", disc[19], "first OOF", disc[20], "last", disc[-1])
# six blocks of 796
oof = disc[20:]
sizes = [133, 133, 133, 133, 132, 132]
i = 0
for k, s in enumerate(sizes, 1):
    blk = oof[i:i + s]
    print(f"block {k}: {blk[0]} .. {blk[-1]} ({len(blk)})")
    i += s
# 20-date embargo after each block: dates
i = 0
for k, s in enumerate(sizes, 1):
    end = i + s
    emb = oof[end:end + 20]
    print(f"embargo after block {k}: {emb[0] if emb else None} .. {emb[-1] if emb else None} ({len(emb)})")
    i = end
test_all = trade_dates_between(cal, date(2017, 5, 1), date(2020, 11, 30))
test = trade_dates_between(cal, date(2017, 5, 22), date(2020, 11, 30))
print("test 2017-05-01.. dates", len(test_all), "; from 2017-05-22:", len(test), "first", test[0], "burn-in last", test[19], "first scored", test[20])
pre = trade_dates_between(cal, date(2017, 5, 1), date(2017, 5, 21))
print("dates 2017-05-01..05-21:", len(pre), pre[0], pre[-1])
# holidays in the discovery range that are full closures vs early halts
hol = [(d, cal.holidays[d].kind.name) for d in disc if cal.holiday(d) is not None]
print("holidays on trade dates in discovery:", len(hol), hol[:12])
print("scheduled late opens in discovery:", [d for d in disc if d in cal.scheduled_late_opens][:10])
print("late_opens in discovery:", [d for d in disc if d in cal.late_opens][:10])
# calendar quarters Dec-Feb etc over OOF dates
import collections
def q(d):
    m = d.month
    y = d.year if m != 12 else d.year + 1
    return (y, {12:1,1:1,2:1,3:2,4:2,5:2,6:3,7:3,8:3,9:4,10:4,11:4}[m])
qc = collections.Counter(q(d) for d in oof)
print("OOF quarters:", len(qc), sorted(qc.items()))
mc = collections.Counter((d.year, d.month) for d in oof)
print("OOF months:", len(mc), "first", min(mc), "last", max(mc), "min dates", min(mc.values()))
