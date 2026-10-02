"""Auditor: can the D9 coverage check on a K8 leg fail for a reason other than missing bars?
For every member, leg and declared interval, over the member's research-window full-session dates,
compare the minutes screening.stage_e_align._expected_ranges expects (the interval clipped by the
group calendar's session intervals of the date) with the interval's nominal length. Any date on
which the session clips the interval is listed. No bar file is read."""

from __future__ import annotations

import os

os.nice(10)

import sys  # noqa: E402
from collections import Counter  # noqa: E402
from datetime import date  # noqa: E402
from pathlib import Path  # noqa: E402

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))

from data.group_session import load_group_calendar  # noqa: E402
from rules.products import product  # noqa: E402
from screening.stage_e_align import NS_PER_MIN, _expected_ranges, _ns  # noqa: E402
from strategy.members.k8 import flight, oilcad, wkndbtc  # noqa: E402
from strategy.members.k8._calendar import FLIGHT_DATES, OILCAD_DATES, WKNDBTC_DATES  # noqa: E402

RES_FIRST, RES_LAST = date(2025, 4, 1), date(2026, 6, 19)
MEMBERS = ((flight.make_h30(), FLIGHT_DATES), (oilcad.make_6c(), OILCAD_DATES),
           (wkndbtc.make_mnq(), WKNDBTC_DATES))

for member, dates in MEMBERS:
    days = [d for d in dates if RES_FIRST <= d <= RES_LAST]
    for root, intervals in member.trading_windows.items():
        cal = load_group_calendar(product(root).group)
        clipped: Counter = Counter()
        nominal = 0
        for iv in intervals:
            nominal += (_ns(date(2025, 6, 2), iv.end_offset_days, iv.end_ct)
                        - _ns(date(2025, 6, 2), iv.start_offset_days, iv.start_ct)) // NS_PER_MIN
        for d in days:
            ranges = _expected_ranges(cal, d, intervals)
            got = sum((b - a) // NS_PER_MIN for a, b in ranges)
            if got != nominal:
                clipped[(d, got)] += 1
        print(f"[{member.name}] {root}: nominal {nominal} min/date over {len(days)} dates; "
              f"dates where the session clips the interval: {len(clipped)} "
              f"{sorted(clipped)[:6]}")
