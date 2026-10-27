"""T_test from the historical grains calendar (code only; no market data)."""
from datetime import date
from data.hist_calendar import load_hist_group_calendar
from data.group_session import trade_dates_between
cal = load_hist_group_calendar("grains")
print("hist coverage", cal.coverage)
a = trade_dates_between(cal, date(2017, 5, 1), date(2020, 11, 30))
b = trade_dates_between(cal, date(2017, 5, 22), date(2020, 11, 30))
print("2017-05-01..2020-11-30:", len(a), "; 2017-05-22..:", len(b), "first", b[0], "burn-in last", b[19], "first scored", b[20], "last", b[-1])
print("T_test = ", len(b) - 20)
hol = [(d, cal.holidays[d].kind.name) for d in b if cal.holiday(d) is not None]
print("holiday trade dates in test window:", len(hol))
