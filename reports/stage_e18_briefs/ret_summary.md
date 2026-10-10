## 1. Verdict summary

**C1b: FAIL.** Neither registered test passes its bar (freeze section 5; each meets only n >= 30):

| Test | Trades / dates | Mean gross (ticks) | 1.5c bar | t_B | one-sided p |
|---|---|---|---|---|---|
| C1b-T1, NG h60 | 814 / 557 | +0.585 per trade (-0.914 per date) | 2.562 | -0.83 | 0.80 |
| C1b-T2, NG hF | 627 / 386 | -0.113 per trade | 2.649 | -0.41 | 0.66 |

VerdictVerifier-FableXHigh recomputed every number independently (66 items, 0 unequal at 1e-9): VERIFIED WITH
NOTES, no BLOCKING finding. The verdict holds whether criterion 1 reads the
per-trade or the per-date mean.

**N = 480** (r003-C1b, N 478 -> 480, 12:17:48 PDT).

**The one fix held.** C10 exempted only g17_mbt (MBT unlisted until 2021) and g17_cl (NG's own cluster lead,
reference 0). Every other feature live in E.12 applied, so the run did not stop. The exempt list follows from
listing dates and section 2 alone, not from the C10 counts E.17's stopped run printed. Before the freeze, Fable
approved the diff (one SHOULD FIX, fixed), and the dry check passed on E.12's frozen reference.

**Meaning (freeze section 8, Fail):** the NG near-miss is closed. Gate 0's reading stands, nothing more is built on
v2's model, and N is 480. E.12's 2019-2024 h60 row (5.57 ticks, t_B 2.51) did not recur in 2010-2019. A fail cannot
separate "never real" from "real only in the 2019-2024 LNG-era regime".

