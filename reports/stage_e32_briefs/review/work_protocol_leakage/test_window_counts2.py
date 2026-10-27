"""T_test from hist (to 2019-05-31) + program grains (from 2019-06-01) calendars; code only."""
from datetime import date
from data.hist_calendar import load_hist_group_calendar
from data.group_session import load_group_calendar, trade_dates_between
h = load_hist_group_calendar("grains"); g = load_group_calendar("grains")
part1 = trade_dates_between(h, date(2017, 5, 22), date(2019, 5, 31))
part2 = trade_dates_between(g, date(2019, 6, 1), date(2020, 11, 30))
pre = trade_dates_between(h, date(2017, 5, 1), date(2017, 5, 21))
allt = part1 + part2
print("hist part 2017-05-22..2019-05-31:", len(part1), "; grains part 2019-06-01..2020-11-30:", len(part2))
print("2017-05-22..2020-11-30 combined:", len(allt), "; +15 pre =", len(allt) + len(pre), "; T_test = ", len(allt) - 20)
print("burn-in last", allt[19], "first scored", allt[20])
# early halts / late opens in the test window by the two calendars (P1.4 exclusions)
eh = [d for d in allt if (h.holiday(d) if d <= date(2019,5,31) else g.holiday(d)) is not None]
print("holiday-kind trade dates:", len(eh), eh)
