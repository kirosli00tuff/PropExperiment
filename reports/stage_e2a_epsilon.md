# Stage E.2a Task 13: epsilon per traded exposure (funnel re-derivation)

Generated 2026-09-26T14:19:11.167212+00:00 by `funnel.exposure_gate_run`; declaration `reports/stage_e2a_epsilon_declaration.md` (sha256 ccdb8ec53f9015d4...). Machine-readable: `reports/stage_e2a_epsilon.json`; per-cell rows: `reports/stage_e2a_funnel/<VEHICLE>/cells.jsonl`. Written progressively: 'pending' and 'running' mean the pass has not finished.

Operative eps = min(translated, funnel). B1 evaluates, in ascending net $/day, the cells below eps_translated x q_c x tick value and stops at the first robust pass; B2 continues above the bar for the reported funnel figure only.

Early stop (addendum A-1, sha256 e6253be2...): a failing cell stops once more than 1,531 of its 8,000 careers have failed (a robust pass is then impossible); it is recorded as 'fail (pass impossible after n runs)'. Every passing cell runs in full. Cells evaluated before the restart at 06:37 PDT (ZT, ZF all; ZN, TN 53 each) ran in full.

| # | Cluster | Exposure | Vehicle | q_c | Status | eps translated | bar $/day | B1 | B1 cells | early-stopped | eps operative | eps funnel | B2 | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K2 | 2-year | ZT | 1 | undersized | 10 | 78.12 | pass consistency|T2|p0.55|R2.0 ($45.55) | 212/220 | 0 | 5 | 5 | not needed (B1 found a pass below the bar) | undersized |
| 2 | K2 | 5-year | ZF | 1 | undersized | 10 | 78.12 | pass consistency|T2|p0.6|R1.5 ($50.57) | 206/218 | 0 | 6 | 6 | not needed (B1 found a pass below the bar) | undersized |
| 3 | K2 | 10-year | ZN | 1 | chosen | 5 | 78.12 | pass consistency|T1|p0.58|R1.5 ($57.04) | 194/208 | 140 | 3 | 3 | not needed (B1 found a pass below the bar) | none |
| 4 | K2 | Ultra 10-year | TN | 1 | chosen | 5 | 78.12 | pass consistency|T2|p0.65|R1.0 ($65.34) | 168/194 | 114 | 4 | 4 | not needed (B1 found a pass below the bar) | none |
| 5 | K2 | Bond | ZB | 1 | chosen | 2 | 62.50 | none below the bar | 144/144 | 159 | 2 | 2 | pass consistency|T1|p0.65|R1.0 ($86.55) | none |
| 6 | K2 | Ultra bond | UB | 1 | chosen | 2 | 62.50 | none below the bar | 126/126 | 143 | 2 | 2 | pass consistency|T2|p0.62|R1.0 ($92.63) | none |
| 7 | K4 | WTI crude | MCL | 4 | chosen | 21 | 84.00 | none below the bar | 118/118 | 137 | 21 | 24 | pass consistency|T1|p0.65|R1.0 ($97.27) | none |
| 8 | K4 | Henry Hub gas | NG | 1 | chosen | 8 | 80.00 | none below the bar | 81/81 | 94 | 8 | 11 | pass consistency|T8|p0.575|R1.0 ($115.77) | none |
| 9 | K5 | gold | MGC | 1 | chosen | 85 | 85.00 | pass consistency|T4|p0.66|R0.75 ($71.43) | 102/140 | 75 | 71 | 71 | not needed (B1 found a pass below the bar) | none |
| 10 | K5 | copper | MHG | 2 | chosen | 34 | 85.00 | pass consistency|T2|p0.65|R1.0 ($69.67) | 176/198 | 149 | 27 | 27 | not needed (B1 found a pass below the bar) | none |
| 11 | K3 | EUR | 6E | 1 | chosen | 13 | 81.25 | pass consistency|T2|p0.62|R1.0 ($80.09) | 136/138 | 135 | 12 | 12 | not needed (B1 found a pass below the bar) | none |
| 12 | K3 | AUD | 6A | 1 | chosen | 17 | 85.00 | pass consistency|T2|p0.55|R1.5 ($56.14) | 182/206 | 181 | 11 | 11 | not needed (B1 found a pass below the bar) | none |
| 13 | K3 | GBP | 6B | 1 | chosen | 13 | 81.25 | pass consistency|T2|p0.55|R1.5 ($52.46) | 176/208 | 175 | 8 | 8 | not needed (B1 found a pass below the bar) | none |
| 14 | K3 | CAD | 6C | 1 | undersized | 17 | 85.00 | pass consistency|T1|p0.55|R2.0 ($45.29) | 206/218 | 205 | 9 | 9 | not needed (B1 found a pass below the bar) | undersized |
| 15 | K3 | JPY | 6J | 1 | chosen | 13 | 81.25 | pass consistency|T1|p0.54|R1.75 ($63.17) | 186/204 | 185 | 10 | 10 | not needed (B1 found a pass below the bar) | none |
| 16 | K3 | CHF | 6S | 1 | chosen | 13 | 81.25 | none below the bar | 126/126 | 135 | 13 | 15 | pass consistency|T4|p0.68|R0.75 ($94.55) | none |
| 17 | K3 | NZD | 6N | 1 | undersized | 17 | 85.00 | pass consistency|T1|p0.7|R1.0 ($51.41) | 198/214 | 197 | 10 | 10 | not needed (B1 found a pass below the bar) | undersized |
| 18 | K6 | corn | ZC | 1 | undersized | 6 | 75.00 | pass consistency|T2|p0.6|R1.5 ($52.62) | 208/216 | 207 | 4 | 4 | not needed (B1 found a pass below the bar) | undersized |
| 19 | K6 | wheat | ZW | 1 | chosen | 6 | 75.00 | pass consistency|T4|p0.55|R1.5 ($61.31) | 174/196 | 173 | 4 | 4 | not needed (B1 found a pass below the bar) | none |
| 20 | K6 | soybeans | ZS | 1 | chosen | 6 | 75.00 | pass consistency|T1|p0.65|R1.0 ($72.85) | 154/158 | 153 | 5 | 5 | not needed (B1 found a pass below the bar) | none |
| 21 | K6 | soybean meal | ZM | 1 | chosen | 8 | 80.00 | pass consistency|T1|p0.57|R1.5 ($57.56) | 174/202 | 173 | 5 | 5 | not needed (B1 found a pass below the bar) | none |
| 22 | K6 | soybean oil | ZL | 1 | chosen | 14 | 84.00 | pass consistency|T4|p0.68|R0.75 ($69.38) | 136/156 | 135 | 11 | 11 | not needed (B1 found a pass below the bar) | none |
| 23 | K6 | lean hogs | HE | 1 | chosen | 8 | 80.00 | pass consistency|T2|p0.62|R1.0 ($70.79) | 142/152 | 141 | 7 | 7 | not needed (B1 found a pass below the bar) | none |
| 24 | K6 | live cattle | LE | 1 | chosen | 8 | 80.00 | none below the bar | 90/90 | 103 | 8 | 11 | pass consistency|T1|p0.6|R1.0 ($118.14) | none |
| 25 | K7 | bitcoin | MBT | 1 | undersized | 170 | 85.00 | pass consistency|T2|p0.52|R1.75 ($45.37) | 196/216 | 195 | 90 | 90 | not needed (B1 found a pass below the bar) | undersized |
| 26 | K1 | Nasdaq-100 | MNQ | 1 | chosen | 170 | 85.00 | none below the bar | 78/78 | 83 | 170 | 186 | pass consistency|T16|p0.55|R1.0 ($93.04) | none |
| 27 | K1 | Russell 2000 | M2K | 3 | chosen | 56 | 84.00 | pass consistency|T2|p0.6|R1.0 ($75.27) | 103/115 | 102 | 50 | 50 | not needed (B1 found a pass below the bar) | none |
| 28 | K1 | Dow | MYM | 3 | chosen | 56 | 84.00 | none below the bar | 85/85 | 86 | 56 | 60 | pass consistency|T4|p0.58|R1.0 ($90.71) | none |

## E|m_T| (vendor ticks per contract) and round-turn cost (ticks)

| Vehicle | T=1 | T=2 | T=4 | T=8 | T=16 | T=32 | RT cost T=1 | E|m_1| x tv = r_c | days used | short days (max over T) |
|---|---|---|---|---|---|---|---|---|---|---|
| ZT | 14.42 | 9.17 | 6.21 | 4.32 | 2.99 | 2.16 | 1.300 | True (112.68) | 286 | 0 |
| ZF | 17.35 | 11.11 | 7.74 | 5.39 | 3.75 | 2.66 | 1.299 | True (135.54) | 286 | 0 |
| ZN | 13.12 | 8.48 | 5.95 | 4.12 | 2.88 | 2.06 | 1.169 | True (204.93) | 286 | 0 |
| TN | 16.64 | 10.88 | 7.51 | 5.21 | 3.61 | 2.57 | 1.174 | True (259.94) | 286 | 0 |
| ZB | 12.87 | 8.55 | 5.94 | 4.08 | 2.88 | 2.05 | 1.091 | True (402.10) | 286 | 0 |
| UB | 16.05 | 10.76 | 7.48 | 5.21 | 3.66 | 2.58 | 1.099 | True (501.42) | 286 | 0 |
| MCL | 91.57 | 61.75 | 45.03 | 33.78 | 23.03 | 16.22 | 3.152 | True (91.57) | 258 | 0 |
| NG | 63.93 | 43.55 | 30.34 | 20.76 | 14.64 | 10.54 | 1.652 | True (639.31) | 259 | 0 |
| MGC | 258.59 | 176.38 | 122.44 | 87.79 | 62.02 | 44.58 | 4.170 | True (258.59) | 290 | 0 |
| MHG | 88.17 | 59.15 | 41.41 | 29.59 | 20.69 | 14.66 | 3.820 | True (110.22) | 290 | 0 |
| 6E | 51.11 | 34.80 | 24.16 | 17.22 | 11.98 | 8.46 | 1.950 | True (319.45) | 293 | 0 |
| 6A | 36.73 | 25.54 | 18.51 | 12.96 | 8.92 | 6.31 | 2.198 | True (183.65) | 293 | 0 |
| 6B | 29.80 | 19.94 | 13.96 | 9.96 | 7.04 | 4.99 | 1.914 | True (186.22) | 293 | 0 |
| 6C | 24.06 | 16.63 | 12.07 | 8.30 | 5.71 | 4.19 | 2.000 | True (120.29) | 293 | 0 |
| 6J | 32.77 | 21.65 | 14.54 | 10.27 | 7.12 | 5.04 | 1.907 | True (204.82) | 293 | 0 |
| 6S | 65.72 | 43.50 | 29.39 | 21.19 | 14.89 | 10.49 | 2.627 | True (410.75) | 293 | 0 |
| 6N | 31.30 | 21.85 | 15.42 | 11.39 | 7.75 | 5.40 | 2.238 | True (156.48) | 293 | 0 |
| ZC | 12.65 | 8.65 | 5.75 | 4.07 | 2.88 | 2.02 | 1.429 | True (158.16) | 271 | 0 |
| ZW | 18.78 | 13.45 | 8.85 | 6.27 | 4.39 | 3.10 | 1.487 | True (234.75) | 277 | 0 |
| ZS | 24.35 | 16.77 | 11.39 | 7.93 | 5.62 | 3.97 | 1.478 | True (304.39) | 279 | 0 |
| ZM | 21.26 | 15.06 | 10.32 | 7.10 | 4.98 | 3.55 | 1.623 | True (212.64) | 273 | 0 |
| ZL | 50.80 | 33.63 | 23.11 | 16.62 | 11.57 | 8.14 | 2.198 | True (304.83) | 282 | 0 |
| HE | 32.30 | 22.48 | 15.64 | 10.80 | 7.63 | 5.26 | 1.838 | True (322.96) | 270 | 0 |
| LE | 70.72 | 46.53 | 31.88 | 21.83 | 15.27 | 10.71 | 2.329 | True (707.16) | 264 | 0 |
| MBT | 241.23 | 167.68 | 112.00 | 79.51 | 55.38 | 39.46 | 9.260 | True (120.61) | 260 | 0 |
| MNQ | 726.92 | 490.28 | 338.57 | 227.45 | 157.66 | 111.82 | 4.300 | True (363.46) | 285 | 0 |
| M2K | 212.27 | 145.90 | 96.85 | 66.57 | 47.19 | 33.20 | 4.220 | True (106.13) | 286 | 0 |
| MYM | 262.30 | 177.32 | 119.91 | 83.28 | 58.60 | 41.77 | 4.307 | True (131.15) | 286 | 0 |

## Addendum A-1 validations (before any early stop was used)

All passed: **True** (310.6 s, 12 workers, forkserver, batches of 50 careers, pass needs at most 1531 failures of 8,000). Exposure ZT; detail in `reports/stage_e2a_funnel/a1_validation.json` (a first run with batches of 250 also passed: `a1_validation_chunk250.json`).

1. Batched = full run, bit for bit, at every batch boundary:

| Cell | recomputed full run is the stored run | boundaries | all prefixes equal |
|---|---|---|---|
| consistency|T1|p0.55|R2.0 | True | 160 | True |
| consistency|T1|p0.55|R1.5 | True | 160 | True |
| standard|T2|p0.5|R1.0 | True | 160 | True |

2. Early stop on stored failing cells:

| Cell | stored power | stopped after n | failures | stored failures of 8,000 | not pass | prefix count | prefix sub-multiset of stored samples |
|---|---|---|---|---|---|---|---|
| consistency|T1|p0.55|R2.0 | 0.72675 | 5650 | 1540 | 2186 | True | True | True |
| consistency|T4|p0.6|R1.5 | 0.64425 | 4350 | 1545 | 2846 | True | True | True |
| standard|T1|p0.45|R1.5 | 0.00075 | 1550 | 1550 | 7994 | True | True | True |
| consistency|T2|p0.45|R2.0 | 0.060125 | 1650 | 1562 | 7519 | True | True | True |
| standard|T4|p0.5|R1.5 | 0.000125 | 1550 | 1550 | 7999 | True | True | True |
| consistency|T8|p0.425|R2.0 | 0.0 | 1550 | 1550 | 8000 | True | True | True |
| standard|T16|p0.45|R1.5 | 0.0 | 1550 | 1550 | 8000 | True | True | True |

3. ZT binding cell consistency|T2|p0.55|R2.0 through the new path: 61 stored fields, differences none, samples equal True, early_stopped False (the one added field: early_stopped).


## Compute

```
{
 "threads": 12,
 "parallel_exposures": 2,
 "workers_per_exposure": 6,
 "start_method": "forkserver",
 "nice": 10,
 "drive_started_utc": "2026-09-26T10:20:52.485513+00:00",
 "phases": {
  "B1": {
   "wall_seconds": 11725.8,
   "state": "done"
  },
  "B2": {
   "wall_seconds": 2572.6,
   "state": "done"
  }
 },
 "failures": {},
 "peak_estimate_gb": 3.0,
 "free_gb_at_launch": {
  "available_gb": 9.34,
  "total_gb": 14.76
 },
 "early_stop_a1": true,
 "drives": [
  {
   "started_utc": "2026-09-25T13:36:16.231625+00:00",
   "phases": [
    "B1",
    "B2"
   ],
   "parallel": 2,
   "workers": 6,
   "early_stop_a1": true,
   "free_gb_at_launch": {
    "available_gb": 9.9,
    "total_gb": 14.76
   }
  },
  {
   "started_utc": "2026-09-26T00:10:45.282787+00:00",
   "phases": [
    "B1",
    "B2"
   ],
   "parallel": 2,
   "workers": 6,
   "early_stop_a1": false,
   "free_gb_at_launch": {
    "available_gb": 11.21,
    "total_gb": 14.76
   }
  },
  {
   "started_utc": "2026-09-26T00:42:21.677089+00:00",
   "phases": [
    "B1",
    "B2"
   ],
   "parallel": 2,
   "workers": 6,
   "early_stop_a1": true,
   "free_gb_at_launch": {
    "available_gb": 8.9,
    "total_gb": 14.76
   }
  },
  {
   "started_utc": "2026-09-26T01:05:19.102943+00:00",
   "phases": [
    "B1",
    "B2"
   ],
   "parallel": 2,
   "workers": 6,
   "early_stop_a1": true,
   "free_gb_at_launch": {
    "available_gb": 8.59,
    "total_gb": 14.76
   }
  },
  {
   "started_utc": "2026-09-26T10:20:52.485513+00:00",
   "phases": [
    "B1",
    "B2"
   ],
   "parallel": 2,
   "workers": 6,
   "early_stop_a1": true,
   "free_gb_at_launch": {
    "available_gb": 9.34,
    "total_gb": 14.76
   }
  }
 ],
 "peak_memory": {
  "peak_pss_mb": 1166.7
 }
}
```

Per exposure: cell seconds summed and wall time per phase are in the JSON (`cell_seconds_sum`, `B1.wall_seconds_this_run`, `B2...`).
