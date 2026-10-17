## 1. Summary

**Shortlist** (4 triggers, 5 trigger-holds, K = 5):
- K2-monthend-01, long on ZF, ZN and ZB at 5 days (strong: month-end Treasury index-extension demand).
- E20H6-T1, reversal on NQ at 5 and 20 days (hedging pressure reverses; the 20-day evidence is disputed).

**Dropped**, among the other 203 inventoried triggers:
- No owned 2010-2019 data, or too short a store: MES, FX, MBT, VXN and the event calendars; TN, RTY, HE and LE.
- Weak or intraday-only mechanisms.
- Already read: the auction members are E16-H3's long leg; CP1, E16-H1 and E16-H4 are H6 on NQ.
- Always-in-market books: NG before its report, month-end at 20 days.

**Discovery**, W_ext 2011-07-27..2019-04-30, read once, base case. Alpha is over the root's E.21 T1 and T2, NW lags h.

| Trigger-hold | Net Sharpe | Raw t | Alpha t |
|---|---|---|---|
| Month-end ZF, 5 days | 0.21 | 0.62 | 0.55 |
| Month-end ZN, 5 days | 0.14 | 0.40 | 0.38 |
| Month-end ZB, 5 days | 0.02 | 0.05 | 0.10 |
| H6 NQ, 5 days | -0.50 | -1.46 | -1.61 |
| H6 NQ, 20 days | -0.37 | -1.12 | -0.71 |

- Adding the bonds' buy-and-hold return takes the month-end alpha t to 0.12, -0.34 and -0.78: the gain is the bonds' drift.
- Holm's smallest p was 0.309 against 0.01: no survivor.

**Confirmation verdicts:**
- All five NULL (each failed discovery).
- W_cf (2019-05..2024-02) was INCONCLUSIVE BY DESIGN for every row (power 0.18 < 0.2). Nothing was computed on it.
- K8-flight-01 and K1-vxnband-01 are UNCONFIRMABLE ON OWNED DATA.

**Verification:** VerdictVerifier-FableXHigh returned VERIFIED WITH NOTES (no BLOCKING); the books re-simulated exactly.

**N:** 533 -> 538.

**For the user:** close this direction (recommended); keep W_cf and holdout-2 for a stronger prior; buy no data; bound the
multi-day loader next time; E22-F1's settlement source is pending.
