"""ArithmeticReviewer (E.32 ProtocolReview, arithmetic lens): independent trade-date counts, burn-in,
fold sizes, embargo reach, decision-grid counts and the P5 compute arithmetic. No market data is read:
only the program's calendar code (data.calendars.grains, data.hist_calendar) is imported.

    uv run python reports/stage_e32_briefs/review/work_protocol_arithmetic/a1_calendar_folds.py
"""
from __future__ import annotations

import sys
from collections import Counter
from datetime import date, time, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from data.calendars import grains  # noqa: E402
from data.cme_calendar import HolidayKind  # noqa: E402
from data.hist_calendar import load_hist_group_calendar  # noqa: E402

HIST = load_hist_group_calendar("grains")


def full_closures(first: date, last: date) -> dict[date, str]:
    """My own walk over both calendars (hist2010 before the grains file's coverage, grains after)."""
    out: dict[date, str] = {}
    for day, hol in HIST.holidays.items():
        if hol.kind is HolidayKind.FULL_CLOSURE and first <= day <= last:
            out[day] = f"hist:{hol.name}"
    for day, hol in grains.HOLIDAYS.items():
        if hol.kind is HolidayKind.FULL_CLOSURE and first <= day <= last:
            out[day] = f"grains:{hol.name}"
    return out


def weekdays(first: date, last: date) -> list[date]:
    days, day = [], first
    while day <= last:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


def trade_dates(first: date, last: date) -> list[date]:
    closed = full_closures(first, last)
    return [d for d in weekdays(first, last) if d not in closed]


def section(title: str) -> None:
    print(f"\n== {title}")


# ---------------------------------------------------------------- 1. windows ----
section("calendar coverage")
print("hist coverage", HIST.coverage, "grains coverage", grains.CALENDAR_COVERAGE)
overlap_first, overlap_last = grains.CALENDAR_COVERAGE[0], HIST.coverage[1]
h_over = {d for d, h in HIST.holidays.items() if h.kind is HolidayKind.FULL_CLOSURE
          and overlap_first <= d <= overlap_last}
g_over = {d for d, h in grains.HOLIDAYS.items() if h.kind is HolidayKind.FULL_CLOSURE
          and overlap_first <= d <= overlap_last}
print("overlap month", overlap_first, overlap_last, "hist closures", sorted(h_over),
      "grains closures", sorted(g_over), "agree", h_over == g_over)

windows = {
    "discovery 2020-12-01..2024-02-29": (date(2020, 12, 1), date(2024, 2, 29)),
    "test (seal) 2017-05-01..2020-11-30": (date(2017, 5, 1), date(2020, 11, 30)),
    "test (MBO) 2017-05-22..2020-11-30": (date(2017, 5, 22), date(2020, 11, 30)),
    "sealed-untested 2017-05-01..2017-05-19": (date(2017, 5, 1), date(2017, 5, 19)),
}
dates: dict[str, list[date]] = {}
for name, (a, b) in windows.items():
    section(name)
    wd = weekdays(a, b)
    cl = full_closures(a, b)
    td = trade_dates(a, b)
    dates[name] = td
    print(f"weekdays {len(wd)}  full closures {len(cl)}  trade dates {len(td)}")
    print("closures:", ", ".join(f"{d} ({why.split(':')[0]})" for d, why in sorted(cl.items())))

disc = dates["discovery 2020-12-01..2024-02-29"]
test = dates["test (MBO) 2017-05-22..2020-11-30"]

# ---------------------------------------------------------------- 2. burn-in ----
section("burn-in (first 20 trade dates)")
for name, td in (("discovery", disc), ("test", test)):
    burn, oof = td[:20], td[20:]
    print(f"{name}: burn-in {burn[0]}..{burn[-1]}, first OOF {oof[0]}, last OOF {oof[-1]}, T = {len(oof)}")
oof = disc[20:]
months = Counter((d.year, d.month) for d in oof)
print("OOF dates in 2020-12:", months[(2020, 12)], "; months with OOF dates:", len(months))
q_of = lambda d: (d.year + (1 if d.month == 12 else 0), {12: 1, 1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 3, 7: 3,
                                                          8: 3, 9: 4, 10: 4, 11: 4}[d.month])
quarters = Counter(q_of(d) for d in oof)
print("calendar quarters (Dec-Feb, ...):", len(quarters), "; dates per quarter min/max",
      min(quarters.values()), max(quarters.values()))
jja = sum(1 for d in oof if d.month in (6, 7, 8))
print("OOF dates in Jun-Aug (C.15 = 1):", jja)

# ---------------------------------------------------------------- 3. folds ----
section("P6.1 folds on the 796 OOF dates")
sizes = [133, 133, 133, 133, 132, 132]
print("sum of block sizes", sum(sizes), "== T_disc", sum(sizes) == len(oof))
pos, blocks = 0, []
for k, n in enumerate(sizes, 1):
    blk = oof[pos:pos + n]
    pos += n
    blocks.append(blk)
    after = oof[pos:pos + 20]
    emb = f"{after[0]}..{after[-1]}" if after else "none (last block)"
    train = len(oof) - n - len(after)
    print(f"fold {k}: {blk[0]}..{blk[-1]} ({n} dates); embargo {emb}; training dates {train}; "
          f"rows at 263/date {train * 263:,}")
# Longest look-back check: which features reach beyond 20 trade dates?
print("gap features F1.7/F4.7 at date D use the 13:15 close of D-1; their sd over the 20 dates before D "
      "therefore reaches D-21 -> first clean training date after block k is L+22, not L+21")

# ---------------------------------------------------------------- 4. decision grid ----
section("decision grid G_h: minute marks 08:35:00 .. 13:12:00 - h")
for h in (5, 15, 30, 60):
    start = 8 * 60 + 35
    last = 13 * 60 + 12 - h
    n = last - start + 1
    end_last = last + h  # minutes; + L = 1 s
    print(f"h={h}: {n} marks, last mark {end_last // 60 - h:02d}:{(last % 60):02d}, "
          f"last span end {end_last // 60:02d}:{end_last % 60:02d}:01 <= 13:13:00 "
          f"{end_last * 60 + 1 <= 13 * 3600 + 13 * 60}; max non-overlapping trades {n // h}")

# ---------------------------------------------------------------- 5. P5 arithmetic ----
section("P5 compute arithmetic")
recs = 414_363_576
print(f"ZM.v.0 book rebuild: {recs / 0.76e6 / 60:.1f} to {recs / 0.39e6 / 60:.1f} min in one process")
print(f"ZS+ZL re-split at 80 B/record: {(248_167_909 + 158_044_028) * 80 / 1e9:.2f} GB; decode 56 + 35 s = 91 s")
rows = 263 * 796
print(f"rows per horizon at 263/date: {rows:,}; S5 59 features float32: {rows * 59 * 4 / 1e6:.1f} MB; "
      f"h=5 at 273/date: {273 * 796:,} rows, {273 * 796 * 59 * 4 / 1e6:.1f} MB")
fits = 300 * 6
logit, lgbm = 5 * 6 * 6 * 6, 5 * 6 * 4 * 6
print(f"fits {fits} = LOGIT {logit} + LGBM {lgbm}; CPU-hours LOGIT {logit * 10 / 3600:.1f}-{logit * 60 / 3600:.1f}, "
      f"LGBM {lgbm * 5 / 3600:.1f}-{lgbm * 30 / 3600:.1f}; total {(logit * 10 + lgbm * 5) / 3600:.1f}-"
      f"{(logit * 60 + lgbm * 30) / 3600:.1f}; / 7 processes = {(logit * 10 + lgbm * 5) / 3600 / 7:.2f}-"
      f"{(logit * 60 + lgbm * 30) / 3600 / 7:.2f} h wall")
print("LGBM min_data_in_leaf {50h, 200h}:", {h: (50 * h, 200 * h) for h in (5, 15, 30, 60)})
print("PBO blocks: 796 // 8 =", 796 // 8, "dates/block, dates used", 8 * (796 // 8), "; test 870 // 8 =",
      870 // 8, "used", 8 * (870 // 8))
print("sessions: day 08:30-13:20 =", 13 * 60 + 20 - 8 * 60 - 30, "min; label window 08:35-13:13 =",
      13 * 60 + 13 - 8 * 60 - 35, "min")
