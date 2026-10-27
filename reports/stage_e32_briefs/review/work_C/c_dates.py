"""MathReviewer C: independent trade-date count for the two E.32/E.33 windows.

Weekdays minus CBOT grain FULL closures, from a holiday list typed by the reviewer from memory
(no CME page fetched, no data read). Prints counts and the list so the lead can compare it with
the program's calendars (which p7_thresholds.py uses).
"""
from __future__ import annotations

from datetime import date, timedelta

TEST = (date(2017, 5, 1), date(2020, 11, 30))
DISC = (date(2020, 12, 1), date(2024, 2, 29))

# Reviewer's typed list of CBOT grain full closures (trade date does not exist).
# Early closes (day after Thanksgiving, Christmas Eve, New Year's Eve) are NOT closures.
CLOSURES = {
    # 2017
    date(2017, 5, 29): "Memorial", date(2017, 7, 4): "July4", date(2017, 9, 4): "Labor",
    date(2017, 11, 23): "Thanksgiving", date(2017, 12, 25): "Christmas",
    # 2018
    date(2018, 1, 1): "NewYear", date(2018, 1, 15): "MLK", date(2018, 2, 19): "Presidents",
    date(2018, 3, 30): "GoodFriday", date(2018, 5, 28): "Memorial", date(2018, 7, 4): "July4",
    date(2018, 9, 3): "Labor", date(2018, 11, 22): "Thanksgiving", date(2018, 12, 25): "Christmas",
    # 2019
    date(2019, 1, 1): "NewYear", date(2019, 1, 21): "MLK", date(2019, 2, 18): "Presidents",
    date(2019, 4, 19): "GoodFriday", date(2019, 5, 27): "Memorial", date(2019, 7, 4): "July4",
    date(2019, 9, 2): "Labor", date(2019, 11, 28): "Thanksgiving", date(2019, 12, 25): "Christmas",
    # 2020
    date(2020, 1, 1): "NewYear", date(2020, 1, 20): "MLK", date(2020, 2, 17): "Presidents",
    date(2020, 4, 10): "GoodFriday", date(2020, 5, 25): "Memorial", date(2020, 7, 3): "July4obs",
    date(2020, 9, 7): "Labor", date(2020, 11, 26): "Thanksgiving", date(2020, 12, 25): "Christmas",
    # 2021
    date(2021, 1, 1): "NewYear", date(2021, 1, 18): "MLK", date(2021, 2, 15): "Presidents",
    date(2021, 4, 2): "GoodFriday", date(2021, 5, 31): "Memorial", date(2021, 7, 5): "July4obs",
    date(2021, 9, 6): "Labor", date(2021, 11, 25): "Thanksgiving", date(2021, 12, 24): "ChristmasObs",
    # 2022 (Jan 1 2022 was a Saturday; CME did not close Fri 2021-12-31 [reviewer memory])
    date(2022, 1, 17): "MLK", date(2022, 2, 21): "Presidents", date(2022, 4, 15): "GoodFriday",
    date(2022, 5, 30): "Memorial", date(2022, 6, 20): "JuneteenthObs", date(2022, 7, 4): "July4",
    date(2022, 9, 5): "Labor", date(2022, 11, 24): "Thanksgiving", date(2022, 12, 26): "ChristmasObs",
    # 2023
    date(2023, 1, 2): "NewYearObs", date(2023, 1, 16): "MLK", date(2023, 2, 20): "Presidents",
    date(2023, 4, 7): "GoodFriday", date(2023, 5, 29): "Memorial", date(2023, 6, 19): "Juneteenth",
    date(2023, 7, 4): "July4", date(2023, 9, 4): "Labor", date(2023, 11, 23): "Thanksgiving",
    date(2023, 12, 25): "Christmas",
    # 2024
    date(2024, 1, 1): "NewYear", date(2024, 1, 15): "MLK", date(2024, 2, 19): "Presidents",
}
# Disputed: 2018-12-05 national day of mourning (G.H.W. Bush). Reviewer's memory: CME closed only
# US equity-index and interest-rate markets; agricultural markets kept regular hours. Counted separately.
DISPUTED = {date(2018, 12, 5): "DayOfMourning(equities/rates only?)"}


def weekdays(first: date, last: date) -> list[date]:
    out, d = [], first
    while d <= last:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def main() -> None:
    for name, (a, b) in (("TEST 2017-05-01..2020-11-30", TEST), ("DISC 2020-12-01..2024-02-29", DISC)):
        wd = weekdays(a, b)
        closed = sorted(d for d in CLOSURES if a <= d <= b)
        disputed = sorted(d for d in DISPUTED if a <= d <= b)
        n = len(wd) - len(closed)
        print(f"{name}: weekdays {len(wd)}, typed closures {len(closed)}, trade dates {n}"
              f" (minus disputed {len(disputed)} -> {n - len(disputed)})")
        per_year: dict[int, int] = {}
        for d in closed:
            per_year[d.year] = per_year.get(d.year, 0) + 1
        print("   closures per year:", per_year)


if __name__ == "__main__":
    main()
