"""M4: calendar arithmetic for effective sample size (no market data read).
Trade-date count = weekdays 2020-12-01..2024-02-29 minus an ASSUMED CBOT grain holiday list
(full-day closures only; the DataFacts worker owns the real calendar)."""
import datetime as dt, math, json
start, end = dt.date(2020,12,1), dt.date(2024,2,29)
hol = ["2020-12-25","2021-01-01","2021-01-18","2021-02-15","2021-04-02","2021-05-31","2021-07-05",
       "2021-09-06","2021-11-25","2021-12-24","2022-01-17","2022-02-21","2022-04-15","2022-05-30",
       "2022-06-20","2022-07-04","2022-09-05","2022-11-24","2022-12-26","2023-01-02","2023-01-16",
       "2023-02-20","2023-04-07","2023-05-29","2023-06-19","2023-07-04","2023-09-04","2023-11-23",
       "2023-12-25","2024-01-01","2024-01-15","2024-02-19"]
hol = {dt.date.fromisoformat(h) for h in hol}
d, wk = start, 0
while d <= end:
    if d.weekday() < 5: wk += 1
    d += dt.timedelta(days=1)
nh = sum(1 for h in hol if start <= h <= end and h.weekday() < 5)
D = wk - nh
day, ovn = 290, 765   # minutes: 08:30-13:20 CT, 19:00-07:45 CT
out = {"weekdays": wk, "holidays_assumed": nh, "trade_dates": D, "rows": []}
for h in [1, 5, 15, 30, 60, 120, 240]:
    nd, no = day // h, ovn // h
    out["rows"].append({"h_min": h, "per_day_session": nd, "per_overnight": no,
                        "day_total": nd*D, "ovn_total": no*D, "both_total": (nd+no)*D})
# minimum |IC| detectable at t=3 with n independent labels: IC = 3/sqrt(n)
for r in out["rows"]:
    r["ic_t3_day"] = round(3/math.sqrt(r["day_total"]), 4) if r["day_total"] else None
    r["ic_t3_both"] = round(3/math.sqrt(r["both_total"]), 4)
print(json.dumps(out, indent=0))
