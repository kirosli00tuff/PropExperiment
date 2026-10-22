"""DeltaReviewer: QM trade dates, static exclusions and MAIN grid counts with the repo calendar
(no market data read), plus the section 6 arithmetic recomputed."""
import math
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "B_pilot"))
import pilot_common as pc  # noqa: E402

cal = pc.calendar_for("QM")
print("group", pc.GROUP_OF_PRODUCT["QM"], "coverage", cal.coverage)


def count(first, last):
    trade, usable, excl, grids = [], [], {}, {}
    d = first
    while d <= last:
        plan = pc.build_day_plan(cal, d)
        if plan.is_trade_date:
            trade.append(d)
            r = pc.static_exclusions(plan, plan.open_lo or 0, plan.open_hi or 0)
            g = sum(1 for k in range(len(plan.grid_ns))
                    if plan.pieces[int(plan.grid_piece[k])].label == pc.MAIN)
            grids[g] = grids.get(g, 0) + 1
            (excl.__setitem__(d, r) if r else usable.append(d))
        d += timedelta(days=1)
    return trade, usable, excl, grids


for a, b in ((date(2023, 11, 1), date(2024, 2, 29)), (date(2024, 1, 12), date(2024, 2, 29))):
    t, u, e, g = count(a, b)
    print(f"{a}..{b}: trade dates {len(t)}, static excl {[(str(k), v) for k, v in e.items()]}, "
          f"usable before rolls {len(u)}, MAIN grid counts {g}")
    if a.month == 11:
        for n in (26, 28, 30, 32):
            print(f"  last {n} usable start {u[-n]}")
# section 6 arithmetic
s60 = 6.30 * 0.01 / 0.025
s10 = s60 / math.sqrt(6)
n10 = 1.5 * (1.96 * s10 / 0.10) ** 2
n60 = 1.5 * (1.96 * s60 / 0.20) ** 2
nfr = 3 * (1.96 * 0.5 / 0.03) ** 2
fpd = 152 * 0.3
print(f"sigma60 {s60:.4f} sigma10 {s10:.4f} n10 {n10:.2f} n60 {n60:.2f} n_fillrate {nfr:.1f}")
print(f"days: fillrate {nfr/152:.3f} n10 {n10/fpd:.3f} n60 {n60/fpd:.3f}; at p=0.1 n60 {n60/(152*0.1):.2f}")
m = max(math.ceil(nfr / 152), math.ceil(n10 / fpd), math.ceil(n60 / fpd))
print(f"min days {m}, x1.15 = {m*1.15:.2f} -> {math.ceil(m*1.15)}")
print("margin_target(125)", pc.margin_target(125.0), "start_bound(2024-01-12)",
      pc.start_bound(date(2024, 1, 12)))
