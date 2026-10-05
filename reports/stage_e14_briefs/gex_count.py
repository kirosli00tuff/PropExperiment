"""Stage E.14 Task 3: the one read of GEX values before C2's evaluation (prereg C2 section 9 step 3).

Counts the eligible trade dates d in 2011-05-03..2019-04-30 whose timing-rule GEX row is negative.
Reads the hist equity calendar (e14_hist_calendar/1) and the GEX CSV's date and gex columns only;
no price, no return, no bar. Prints counts only, never a GEX value.

Eligible here = calendar-eligible: a CME equity trade date (a weekday that is not a full closure),
not an early halt or late open, not unsourced or unverified, with a prior trade date in the
calendar, and with a GEX row dated strictly before d (lag 1: the latest such row). The stop rule
(under 200: C2 stops) applies to this count, as Task 3 defines it ("under the timing rule and the
Task 2 calendar"). The roll blackout needs Databento's symbology (bought data), so it is only
bounded, as a disclosure: ES rolls quarterly, 32 rolls in the window, 3 blackout dates each, at
most 96 dates, subtracted as if every one were a GEX < 0 date. Bar presence cannot be checked
before the purchase.

Usage: python3 gex_count.py <equity calendar json> <DIX.csv> <expected csv sha256>
"""
from __future__ import annotations

import bisect
import csv
import hashlib
import json
import sys
from datetime import date, timedelta

FIRST, LAST = date(2011, 5, 3), date(2019, 4, 30)
LAG = 1
ROLL_BLACKOUT_BOUND = 32 * 3
POWER_STOP = 200


def calendar_days(path: str) -> tuple[list[date], set[date], set[date]]:
    cal = json.load(open(path))
    if cal.get("schema") != "e14_hist_calendar/1" or cal.get("group") != "equity":
        raise SystemExit("not an e14_hist_calendar/1 equity file")
    closed, short, unsourced = set(), set(), set()
    for e in cal["entries"]:
        d = date.fromisoformat(e["day"])
        if e["evidence"] not in ("cme", "secondary"):
            unsourced.add(d)
        if e["kind"] == "full_closure":
            closed.add(d)
        else:
            short.add(d)
    unsourced |= {date.fromisoformat(u["day"]) for u in cal.get("unsourced", [])}
    first = date.fromisoformat(cal["coverage"]["first"])
    last = date.fromisoformat(cal["coverage"]["last"])
    days = (first + timedelta(days=i) for i in range((last - first).days + 1))
    trade = sorted(d for d in days if d.weekday() < 5 and d not in closed)
    return trade, short, unsourced


def gex_signs(path: str, expected: str) -> tuple[list[date], list[bool]]:
    raw = open(path, "rb").read()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise SystemExit("GEX CSV sha256 mismatch")
    rows = list(csv.DictReader(raw.decode().splitlines()))
    days = [date.fromisoformat(r["date"]) for r in rows]
    neg = [float(r["gex"]) < 0 for r in rows]  # the sign only; no value is kept or printed
    if days != sorted(days) or len(set(days)) != len(days):
        raise SystemExit("GEX dates not strictly increasing")
    return days, neg


def main(cal_path: str, csv_path: str, expected: str) -> None:
    trade, short, unsourced = calendar_days(cal_path)
    gdays, gneg = gex_signs(csv_path, expected)
    counts = {"window_trade_dates": 0, "excluded_early_halt_or_late_open": 0,
              "excluded_unsourced": 0, "excluded_no_prior_trade_date": 0,
              "excluded_no_gex_row": 0, "calendar_eligible": 0, "calendar_eligible_gex_negative": 0}
    for i, d in enumerate(trade):
        if not FIRST <= d <= LAST:
            continue
        counts["window_trade_dates"] += 1
        if d in short:
            counts["excluded_early_halt_or_late_open"] += 1
            continue
        if d in unsourced:
            counts["excluded_unsourced"] += 1
            continue
        if i == 0:
            counts["excluded_no_prior_trade_date"] += 1
            continue
        j = bisect.bisect_left(gdays, d) - LAG  # the latest row dated strictly before d
        if j < 0:
            counts["excluded_no_gex_row"] += 1
            continue
        counts["calendar_eligible"] += 1
        counts["calendar_eligible_gex_negative"] += int(gneg[j])
    n = counts["calendar_eligible_gex_negative"]
    counts["share_gex_negative"] = round(n / counts["calendar_eligible"], 4) if counts["calendar_eligible"] else None
    counts["disclosure_after_roll_bound"] = n - ROLL_BLACKOUT_BOUND
    counts["power_stop_fires"] = n < POWER_STOP
    print(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
