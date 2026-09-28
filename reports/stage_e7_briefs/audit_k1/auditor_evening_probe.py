"""Stage E.7 Task 3 audit: show that mutants VB-26 (vxnband reads the previous evening's bars) and VW-28
(vwap reads them) are NOT equivalent on realistic bars, although every coder-B test passes them.

Runs the same two scenarios against whatever strategy.members.k1 is on PYTHONPATH: the repository (correct
code) or the scratch mirror with the mutant applied. Synthetic bars only, through the real engine.
"""

from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal

from strategy.members.k1 import vwap, vxnband
from tests.test_k1_members_vxnband import EVENING, Day, fills, hm, run

FRI, HOLIDAY, TUE, WED = date(2025, 5, 23), date(2025, 5, 26), date(2025, 5, 27), date(2025, 5, 28)
label = sys.argv[1] if len(sys.argv) > 1 else "repo"

# vxnband: Friday complete at BASE; Memorial Day halts at 12:00 (incomplete); Tuesday opens with the
# holiday's 17:00 reopen, whose bars carry the holiday's "12:00" label (their CT date is the holiday);
# Tuesday's own day closes +2000 at 14:59 (complete); Wednesday's 08:30 close is +1001.
# Correct code: C_prev(WED) = Tuesday's 162000, w = 1012.5 -> no breach, no trade.
# VB-26: the evening label makes Tuesday incomplete -> C_prev = Friday's 160000, w = 1000 -> sell.
vxnband._VXN = {TUE: Decimal("10.000000"), HOLIDAY: Decimal("10.000000")}
days = [Day(FRI), Day(HOLIDAY, end=hm(12, 0), halt="12:00"),
        Day(TUE, start=EVENING, end=0, halt="12:00"), Day(TUE, closes={hm(14, 59): 2000}),
        Day(WED, start=EVENING, closes={0: 1001})]
res = run(vxnband.make_mnq(), days)
print(f"[{label}] vxnband fills on WED:", [f for f in fills(res) if f[0].startswith("2025-05-28")])

# vwap: a plain full session whose trade date opens the evening before (17:00 CT on CT date d-1) and
# steps up at 09:00. Correct code: buy 09:00 (fill 09:01) and the final exit. VW-28: the evening bars
# break the 08:30 clock run (gap) -> no entry at all.
days = [Day(date(2025, 5, 20)), Day(date(2025, 5, 21), start=EVENING, closes={hm(9, 0): 40})]
res = run(vwap.make_mnq(), days)
print(f"[{label}] vwap fills:", fills(res))
