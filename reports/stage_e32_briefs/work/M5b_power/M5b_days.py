"""M5b: calendar arithmetic only (no market data). Weekdays minus a TYPED list of assumed CBOT grain full closures."""
import datetime as dt
def weekdays(a, b):
    d, n = a, 0
    while d <= b:
        n += d.weekday() < 5; d += dt.timedelta(1)
    return n
D = dt.date
test_hol = [D(2017,5,29),D(2017,7,4),D(2017,9,4),D(2017,11,23),D(2017,12,25),
 D(2018,1,1),D(2018,1,15),D(2018,2,19),D(2018,3,30),D(2018,5,28),D(2018,7,4),D(2018,9,3),D(2018,11,22),D(2018,12,5),D(2018,12,25),
 D(2019,1,1),D(2019,1,21),D(2019,2,18),D(2019,4,19),D(2019,5,27),D(2019,7,4),D(2019,9,2),D(2019,11,28),D(2019,12,25),
 D(2020,1,1),D(2020,1,20),D(2020,2,17),D(2020,4,10),D(2020,5,25),D(2020,7,3),D(2020,9,7),D(2020,11,26)]
disc_hol = [D(2020,12,25),
 D(2021,1,1),D(2021,1,18),D(2021,2,15),D(2021,4,2),D(2021,5,31),D(2021,7,5),D(2021,9,6),D(2021,11,25),D(2021,12,24),
 D(2022,1,17),D(2022,2,21),D(2022,4,15),D(2022,5,30),D(2022,6,20),D(2022,7,4),D(2022,9,5),D(2022,11,24),D(2022,12,26),
 D(2023,1,2),D(2023,1,16),D(2023,2,20),D(2023,4,7),D(2023,5,29),D(2023,6,19),D(2023,7,4),D(2023,9,4),D(2023,11,23),D(2023,12,25),
 D(2024,1,1),D(2024,1,15),D(2024,2,19)]
for name, a, b, hol in [("test", D(2017,5,1), D(2020,11,30), test_hol), ("discovery", D(2020,12,1), D(2024,2,29), disc_hol)]:
    assert all(h.weekday() < 5 and a <= h <= b for h in hol), name
    w = weekdays(a, b)
    print(f"{name}: weekdays {w}, assumed closures {len(hol)}, trade dates {w-len(hol)}")
