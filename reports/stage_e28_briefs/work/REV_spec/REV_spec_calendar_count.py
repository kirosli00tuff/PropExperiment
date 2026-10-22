"""Count QG trade dates in 2023-11-01..2024-02-29 with the repo's group calendar and the pilot's
static exclusions (no market data read). Also the last-25 and last-26 trade-date starts."""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path("reports/stage_e28_briefs/work/B_pilot").resolve()))
import pilot_common as pc  # noqa: E402

root = sys.argv[1] if len(sys.argv) > 1 else "QG"
cal = pc.calendar_for(root)
print("group of", root, "=", pc.GROUP_OF_PRODUCT[root], "coverage", cal.coverage)
first, last = date(2023, 11, 1), date(2024, 2, 29)
days = [first + timedelta(n) for n in range((last - first).days + 1)]
trade, usable, excl = [], [], {}
for d in days:
    plan = pc.build_day_plan(cal, d)
    if not plan.is_trade_date:
        continue
    trade.append(d)
    reasons = pc.static_exclusions(plan, plan.open_lo or 0, plan.open_hi or 0)
    if reasons:
        excl[d] = reasons
    else:
        usable.append(d)
    if d >= date(2024, 1, 20):
        main = plan.main_pieces()
        g_main = sum(1 for k in range(len(plan.grid_ns)) if plan.pieces[int(plan.grid_piece[k])].label == pc.MAIN)
        print(f"{d} trade_date main_pieces={[(pc.local_iso(p.lo)[11:16], pc.local_iso(p.hi)[11:16]) for p in main]} "
              f"main_grid={g_main} pieces={len(plan.pieces)} excl={reasons}")
print("trade dates in window:", len(trade))
print("statically excluded (holiday/early close/late open):", {str(k): v for k, v in excl.items()})
print("usable before roll/gap exclusions:", len(usable))
for n in (25, 26, 30):
    print(f"last {n} usable trade dates start at {usable[-n]}; last {n} trade dates start at {trade[-n]}")
# a regular day's MAIN grid count
plan = pc.build_day_plan(cal, date(2023, 11, 14))
g_main = sum(1 for k in range(len(plan.grid_ns)) if plan.pieces[int(plan.grid_piece[k])].label == pc.MAIN)
g_all = len(plan.grid_ns)
print("2023-11-14: MAIN grid times", g_main, "all grid times", g_all, "pieces", [(p.label, pc.local_iso(p.lo)[11:16], pc.local_iso(p.hi)[11:16]) for p in plan.pieces])
