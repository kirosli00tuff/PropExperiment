"""Auditor scenarios through the real engine (synthetic bars via the test fixtures). Prints fills only."""
import sys; sys.path.insert(0, ".")
from datetime import date
import tests.test_e3_k2_members as A
import tests.test_e3_k2_members_events as B
from strategy.members.k2 import cp2, cp3, monthend, aucpre, predrift
from strategy.members.k2._releases import TREASURY_AUCTIONS
hm, Day, run, fills, intents = A.hm, A.Day, A.run, A.fills, A.intents
TUE, WED, MON = A.TUE, A.WED, A.MON
# 1. CP2: a 4-tick close at 07:34 is a RANGE bar (widens OR_high), not an entry; at 07:35 it is an entry
d = Day(TUE, paths={**A.CP2_OR, hm(7, 34): (0, 6, 0, 6), hm(8, 0): (0, 6, 0, 6)})
print("cp2 07:34 break:", intents(run(cp2.make_zn(), [d])), fills(run(cp2.make_zn(), [d])))
d = Day(TUE, paths={**A.CP2_OR, hm(7, 35): (0, 6, 0, 6)})
print("cp2 07:35 break:", fills(run(cp2.make_zn(), [d])))
# 2. CP2: a 4-tick break during the range window on a later bar (07:30) then re-test at 08:00 -> OR_high moved to B+6 so 08:00 B+6 close no entry
d = Day(TUE, paths={**A.CP2_OR, hm(7, 33): (0, 6, 0, 6), hm(8, 0): (0, 6, 0, 6), hm(8, 5): (0, 10, 0, 10)})
print("cp2 range widened, 08:05 B+10 entry:", fills(run(cp2.make_zn(), [d])))
# 3. CP3: a bar after 14:00 (14:30) with a different instrument_id, and an evening bar with another id, do not make MON incomplete
mon = Day(MON, A.BUY_08, ids={hm(14, 30): 778}, evening_id=776)
print("cp3 post-14:00 and evening id ignored:", fills(run(cp3.make_zn(), [mon, Day(TUE)])))
# 4. CP3: a different id at 13:59 (an RTH bar) makes MON incomplete
mon = Day(MON, A.BUY_08, ids={hm(13, 59): 778})
print("cp3 13:59 id differs -> incomplete:", fills(run(cp3.make_zn(), [mon, Day(TUE)])))
# 5. CP3: halt label only on the evening bars of TUE (i.e. MON's CT date halt) must not exclude TUE
mon = Day(MON, A.BUY_08); tue = Day(TUE, evening_halt="12:15")
print("cp3 evening halt label ignored:", fills(run(cp3.make_zn(), [mon, tue])))
# 6. monthend Nov 2019: N-1 = 11-28 (halt 12:15), N = 11-29 (halt 12:15): both dropped, 11-27 not traded
days = [Day(date(2019, 11, 27)), Day(date(2019, 11, 28), halt="12:15", end=hm(12, 15)),
        Day(date(2019, 11, 29), halt="12:15", end=hm(12, 15), evening_halt="12:15"), Day(date(2019, 12, 2), evening_halt="12:15")]
print("monthend Nov 2019:", fills(run(monthend.make_zn(), days)), intents(run(monthend.make_zn(), days)))
# 7. aucpre ZN on a standard-time 10Y date (DST off): fills at 09:00 and 11:59 CT
std = [d for d, t, ta in TREASURY_AUCTIONS if t == "10Y" and d.startswith("2025-12")]
day = date.fromisoformat(std[0])
print("aucpre ZN", day, B.trips(B.run(aucpre.make_zn(), B.bars("ZN", [day]), [day])))
# 8. predrift: 08:30 bar present with a different id than 08:49 but the same as ... (guard) -> covered; here: the signal uses the 08:30 OPEN, not its close
up = B.drift_paths(B.D_ISM, B.B, B.B + 9, B.B + 9, B.B + 3)  # open 08:30 = B, close 08:49 = B+3 -> +3 buy; close-close would be -6
print("predrift open-based:", B.trips(B.run(predrift.make_zn(), B.predrift_bars("ZN", B.D_ISM, up), [B.D_ISM])))
# 9. CP2 two consecutive days: a position must not carry the count across days (state reset) and hold ends at F on a synthetic early F
d1 = Day(TUE, paths={**A.CP2_OR, hm(13, 0): (0, 6, 0, 6)}, flatten_from=hm(13, 30))
print("cp2 synthetic F at 13:30:", fills(run(cp2.make_zn(), [d1, Day(WED, paths={**A.CP2_OR, hm(8, 0): (0, 6, 0, 6)})])))
