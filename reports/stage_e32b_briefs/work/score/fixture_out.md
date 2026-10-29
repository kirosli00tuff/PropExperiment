# score32b output (2026-10-29 08:56:10 PDT)

spec sha256 09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635

## Layer 1

| code | status | D1 | D2 | D3 | D4 | D5 | D6 | L1 | gate | arithmetic |
|---|---|---|---|---|---|---|---|---|---|---|
| CL | owned | 3.50 | 0.50 | 4.00 | 3.00 | 4.00 | 3.00 | 3.02 | pass | sigma_60 = 44.00 ticks vs 2 x (1 + 0.5) = 3.00 ticks |
| MCL | owned | 3.50 | 0.50 | 3.00 | 2.00 | 2.00 | 3.00 | 2.52 | pass | sigma_60 = 44.00 ticks vs 2 x (1 + 0.5) = 3.00 ticks |
| MNQ | OC1 | 4.00 | 0.00 | 4.00 | 2.00 | 2.00 | 4.00 | 2.90 | pass | sigma_60 = 160.00 ticks vs 2 x (1 + 0.5) = 3.00 ticks |
| MYM | OC1 | 3.75 | 2.50 | 3.00 | 2.00 | 3.00 | 3.00 | 3.00 | pass | sigma_60 = 60.00 ticks vs 2 x (1 + 0.5) = 3.00 ticks |
| MZM | OC1 | 0.00 | 2.50 | 3.00 | 1.00 | 0.00 | 2.00 | 1.27 | FAIL: sigma_60 = 2.90 ticks vs 2 x (1 + 0.5) = 3.00 ticks | sigma_60 = 2.90 ticks vs 2 x (1 + 0.5) = 3.00 ticks |
| NQ | excluded (V49) |  |  |  |  |  |  |  | not ranked |  |
| QM | OC1 | 2.00 | 0.50 | 2.00 | 0.00 | 3.00 | 3.00 | 1.73 | FAIL: D4 = 0 | sigma_60 = 17.60 ticks vs 2 x (1 + 0.5) = 3.00 ticks |
| SI | unknown | - | 2.50 | 2.00 | 3.00 | 1.00 | 1.00 | - | FAIL: sigma_60 unknown (no owned bars and no sibling under 2.4) | sigma_60 unknown (no owned bars and no sibling under 2.4) |
| SIL | unknown | - | 2.50 | 0.00 | 0.00 | 1.00 | 1.00 | - | FAIL: sigma_60 unknown (no owned bars and no sibling under 2.4); D4 = 0 | sigma_60 unknown (no owned bars and no sibling under 2.4) |
| YM | owned | 3.75 | 2.50 | 3.00 | 3.00 | 3.00 | 3.00 | 3.15 | pass | sigma_60 = 60.00 ticks vs 2 x (1 + 0.5) = 3.00 ticks |
| ZM | owned | 0.25 | 2.50 | 3.00 | 2.00 | 1.00 | 2.00 | 1.60 | pass | sigma_60 = 5.80 ticks vs 2 x (1.5 + 0.5) = 4.00 ticks |

## Pairs

| rank | firm | code | S | S 2dp | L1 | L2 | E | R | A | D | Rel | P | m* | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | bulenox | MNQ | 3.308 | 3.310 | 2.900 | 3.715 | 3.288 | 4.000 | 4.000 | 4.000 | 4.000 | 4.000 | 0.035 | ranked |
| 2 | topstep | MNQ | 3.103 | 3.100 | 2.900 | 3.306 | 3.390 | 3.000 | 3.000 | 4.000 | 3.000 | 3.000 | 0.030 | ranked |
| 3 | bulenox | YM | 3.086 | 3.090 | 3.150 | 3.021 | 2.678 | 4.000 | 4.000 | 1.000 | 4.000 | 4.000 | 0.065 | ranked |
| 4 | bulenox | MYM | 3.081 | 3.080 | 3.000 | 3.162 | 1.906 | 4.000 | 4.000 | 4.000 | 4.000 | 4.000 | 0.103 | ranked |
| 5 | lucid | YM | 2.990 | 2.990 | 3.150 | 2.831 | 2.577 | 4.000 | 4.000 | 2.000 | 3.000 | 0.000 | 0.070 | ranked |
| 6 | bulenox | MCL | 2.917 | 2.920 | 2.525 | 3.309 | 2.272 | 4.000 | 4.000 | 4.000 | 4.000 | 4.000 | 0.085 | ranked |
| 7 | lucid | MYM | 2.911 | 2.910 | 3.000 | 2.822 | 1.804 | 4.000 | 4.000 | 4.000 | 3.000 | 0.000 | 0.108 | ranked |
| 8 | lucid | CL | 2.893 | 2.890 | 3.025 | 2.762 | 2.780 | 4.000 | 4.000 | 1.000 | 3.000 | 0.000 | 0.060 | ranked |
| 9 | topstep | YM | 2.881 | 2.880 | 3.150 | 2.612 | 2.780 | 3.000 | 3.000 | 1.000 | 3.000 | 3.000 | 0.060 | ranked |
| 10 | topstep | MYM | 2.876 | 2.880 | 3.000 | 2.753 | 2.007 | 3.000 | 3.000 | 4.000 | 3.000 | 3.000 | 0.098 | ranked |
| 11 | bulenox | CL | 2.839 | 2.840 | 3.025 | 2.653 | 2.882 | 1.000 | 4.000 | 1.000 | 4.000 | 4.000 | 0.055 | ranked |
| 12 | topstep | CL | 2.822 | 2.820 | 3.025 | 2.618 | 2.983 | 3.000 | 3.000 | 0.500 | 3.000 | 3.000 | 0.050 | ranked |
| 13 | lucid | MCL | 2.747 | 2.750 | 2.525 | 2.968 | 2.170 | 4.000 | 4.000 | 4.000 | 3.000 | 0.000 | 0.090 | ranked |
| 14 | topstep | MCL | 2.712 | 2.710 | 2.525 | 2.899 | 2.373 | 3.000 | 3.000 | 4.000 | 3.000 | 3.000 | 0.080 | ranked |
| 15 | lucid | ZM | 1.812 | 1.810 | 1.600 | 2.025 | 0.000 | 4.000 | 4.000 | 3.500 | 3.000 | 0.000 | 0.260 | ranked |
| 16 | topstep | ZM | 1.738 | 1.740 | 1.600 | 1.875 | 0.000 | 3.000 | 3.000 | 3.500 | 3.000 | 3.000 | 0.250 | ranked |
| - | lucid | MNQ | 2.837 | 2.840 | 2.900 | 2.775 | 3.187 | 4.000 | 0.000 | 4.000 | 3.000 | 0.000 | 0.040 | Layer 2 gate: A = 0 |
| - | bulenox | MZM | 1.837 | 1.840 | 1.275 | 2.400 | 0.000 | 4.000 | 4.000 | 4.000 | 4.000 | 4.000 | inf | Layer 1 gate: Layer 1: sigma_60 = 2.90 ticks vs 2 x (1 + 0.5) = 3.00 ticks |
| - | lucid | MZM | 1.688 | 1.690 | 1.275 | 2.100 | 0.000 | 4.000 | 4.000 | 4.000 | 3.000 | 0.000 | inf | Layer 1 gate: Layer 1: sigma_60 = 2.90 ticks vs 2 x (1 + 0.5) = 3.00 ticks |
| - | topstep | MZM | 1.613 | 1.610 | 1.275 | 1.950 | 0.000 | 3.000 | 3.000 | 4.000 | 3.000 | 3.000 | inf | Layer 1 gate: Layer 1: sigma_60 = 2.90 ticks vs 2 x (1 + 0.5) = 3.00 ticks |
| - | bulenox | NQ | - | - | - | - | - | - | - | - | - | - | - | excluded (V49): excluded (V49) |
| - | lucid | NQ | - | - | - | - | - | - | - | - | - | - | - | excluded (V49): excluded (V49) |
| - | topstep | NQ | - | - | - | - | - | - | - | - | - | - | - | excluded (V49): excluded (V49) |
| - | bulenox | QM | 2.204 | 2.200 | 1.725 | 2.683 | 1.458 | 4.000 | 4.000 | 2.000 | 4.000 | 4.000 | 0.125 | Layer 1 gate: Layer 1: D4 = 0 |
| - | lucid | QM | 2.071 | 2.070 | 1.725 | 2.418 | 1.357 | 4.000 | 4.000 | 2.500 | 3.000 | 0.000 | 0.130 | Layer 1 gate: Layer 1: D4 = 0; not listed for the 50K plan |
| - | topstep | QM | 1.962 | 1.960 | 1.725 | 2.199 | 1.560 | 3.000 | 3.000 | 1.500 | 3.000 | 3.000 | 0.120 | Layer 1 gate: Layer 1: D4 = 0 |
| - | bulenox | SI | - | - | - | - | - | 4.000 | 4.000 | 1.000 | 4.000 | 4.000 | - | Layer 1 gate: Layer 1: sigma_60 unknown (no owned bars and no sibling under 2.4) |
| - | lucid | SI | - | - | - | - | - | 4.000 | 4.000 | 1.000 | 3.000 | 0.000 | - | Layer 1 gate: Layer 1: sigma_60 unknown (no owned bars and no sibling under 2.4) |
| - | topstep | SI | - | - | - | - | - | 3.000 | 3.000 | 1.000 | 3.000 | 3.000 | - | Layer 1 gate: Layer 1: sigma_60 unknown (no owned bars and no sibling under 2.4) |
| - | bulenox | SIL | - | - | - | - | - | 4.000 | 4.000 | 1.000 | 4.000 | 4.000 | - | Layer 1 gate: Layer 1: sigma_60 unknown (no owned bars and no sibling under 2.4); D4 = 0 |
| - | lucid | SIL | - | - | - | - | - | 4.000 | 4.000 | 1.000 | 3.000 | 0.000 | - | Layer 1 gate: Layer 1: sigma_60 unknown (no owned bars and no sibling under 2.4); D4 = 0 |
| - | topstep | SIL | - | - | - | - | - | 3.000 | 3.000 | 1.000 | 3.000 | 3.000 | - | Layer 1 gate: Layer 1: sigma_60 unknown (no owned bars and no sibling under 2.4); D4 = 0 |
| - | bulenox | ZM | 2.000 | 2.000 | 1.600 | 2.400 | 0.000 | 4.000 | 4.000 | 4.000 | 4.000 | 4.000 | 0.255 | Layer 2 gate: 50K listing unknown |

## Ties

- S 2.88: ['topstep|YM', 'topstep|MYM'] [{'higher': 'topstep|YM', 'lower': 'topstep|MYM', 'decided_by': 'm*'}]

## Variants (top 5, MNQ ranks)

- slip0 (declared): 1 bulenox MNQ 3.308, 2 bulenox YM 3.123, 3 bulenox MYM 3.119, 4 topstep MNQ 3.103, 5 lucid YM 3.028; MNQ {'bulenox': 1, 'lucid': 'Layer 2 gate', 'topstep': 4}; same top 5: False
- slip1 (declared): 1 bulenox MNQ 3.308, 2 topstep MNQ 3.103, 3 bulenox YM 3.048, 4 bulenox MYM 3.044, 5 lucid YM 2.953; MNQ {'bulenox': 1, 'lucid': 'Layer 2 gate', 'topstep': 2}; same top 5: True
- mad (declared): 1 bulenox MNQ 3.308, 2 topstep MNQ 3.103, 3 bulenox YM 3.048, 4 bulenox MYM 3.044, 5 lucid YM 2.953; MNQ {'bulenox': 1, 'lucid': 'Layer 2 gate', 'topstep': 2}; same top 5: True
- D1_all (declared): 1 bulenox MNQ 3.286, 2 topstep MNQ 3.082, 3 bulenox YM 3.037, 4 bulenox MYM 3.033, 5 lucid YM 2.942; MNQ {'bulenox': 1, 'lucid': 'Layer 2 gate', 'topstep': 2}; same top 5: True
- E_dir60 (declared): 1 bulenox MNQ 3.379, 2 bulenox MYM 3.291, 3 bulenox YM 3.218, 4 topstep MNQ 3.164, 5 lucid YM 3.133; MNQ {'bulenox': 1, 'lucid': 'Layer 2 gate', 'topstep': 4}; same top 5: False
- OC1_off (declared): 1 bulenox YM 3.086, 2 lucid YM 2.990, 3 bulenox MCL 2.917, 4 lucid CL 2.893, 5 topstep YM 2.881; MNQ {'bulenox': 'Layer 1 gate', 'lucid': 'Layer 1 gate', 'topstep': 'Layer 1 gate'}; same top 5: False
- sat1 (declared): 1 bulenox MNQ 3.383, 2 topstep MNQ 3.178, 3 bulenox MYM 3.156, 4 bulenox YM 3.086, 5 lucid YM 2.990; MNQ {'bulenox': 1, 'lucid': 'Layer 2 gate', 'topstep': 2}; same top 5: False
- D2_own (declared): 1 bulenox MNQ 3.458, 2 topstep MNQ 3.253, 3 bulenox MYM 3.194, 4 bulenox YM 3.086, 5 bulenox MCL 3.067; MNQ {'bulenox': 1, 'lucid': 'Layer 2 gate', 'topstep': 2}; same top 5: False
- L1min2 (declared): 1 bulenox MNQ 3.308, 2 topstep MNQ 3.103, 3 bulenox YM 3.086, 4 bulenox MYM 3.081, 5 lucid YM 2.990; MNQ {'bulenox': 1, 'lucid': 'Layer 2 gate', 'topstep': 2}; same top 5: True
- spread1 (declared): 1 bulenox MNQ 3.308, 2 topstep MNQ 3.103, 3 bulenox YM 3.086, 4 bulenox MYM 3.081, 5 lucid YM 2.990; MNQ {'bulenox': 1, 'lucid': 'Layer 2 gate', 'topstep': 2}; same top 5: True
- RL-SYN-CL-spread2 (lead ruling): 1 bulenox MNQ 3.308, 2 topstep MNQ 3.103, 3 bulenox YM 3.086, 4 bulenox MYM 3.081, 5 lucid YM 2.990; MNQ {'bulenox': 1, 'lucid': 'Layer 2 gate', 'topstep': 2}; same top 5: True

## Moves against E.28 v2

| firm | code | E.28 rank | rank here | moved by |
|---|---|---|---|---|
| bulenox | MNQ | 15 | 1 | E, A, D, R, L1, P, F (dropped), Rel |
| topstep | MNQ | 14 | 2 | E, D, A, L1, F (dropped), P, R |
| bulenox | YM | 55 | 3 | L1, E, A, R, P, F (dropped), Rel, D |
| bulenox | MYM | 23 | 4 | E, L1, A, D, R, P, F (dropped), Rel |
| lucid | YM | 25 | 5 | L1, A, D, R, E, Rel, F (dropped), P |
| bulenox | MCL | 51 | 6 | E, A, D, R, L1, P, F (dropped), Rel |
| lucid | MYM | 40 | 7 | E, L1, A, D, R, Rel, F (dropped), P |
| lucid | CL | not ranked: Layer 1 gate | 8 | L1, A, R, D, Rel, F (dropped), E, P |
| topstep | YM | 34 | 9 | L1, E, A, R, F (dropped), P, D |
| topstep | MYM | 21 | 10 | E, L1, D, A, F (dropped), P, R |
| bulenox | CL | not ranked: Layer 1 gate | 11 | L1, A, E, R, P, F (dropped), Rel, D |
| topstep | CL | not ranked: Layer 1 gate | 12 | L1, A, F (dropped), D, P, R, E |
| lucid | MCL | 27 | 13 | E, A, D, R, L1, Rel, F (dropped), P |
| topstep | MCL | 50 | 14 | E, D, L1, A, F (dropped), P, R |
| lucid | ZM | 13 | 15 | E, L1, D, A, R, Rel, F (dropped), P |
| topstep | ZM | 6 | 16 | E, L1, D, A, F (dropped), P, R |
| topstep | QM | 1 | Layer 1 gate | L1, E, A, D, F (dropped), P, R |
| mffu | QM | 2 | not in F4 pairs |  |
| tradeify | QM | 3 | not in F4 pairs |  |
| bulenox | QM | 4 | Layer 1 gate | L1, E, A, R, P, F (dropped), D, Rel |
| lucid | QM | 5 | Layer 1 gate | L1, E, A, D, R, Rel, F (dropped), P |
| topstep | MGC | 7 | not in F4 pairs |  |
| bulenox | MGC | 8 | not in F4 pairs |  |
| lucid | MGC | 9 | not in F4 pairs |  |
| mffu | ZM | 10 | not in F4 pairs |  |
| mffu | MGC | 11 | not in F4 pairs |  |
| tradeify | MGC | 12 | not in F4 pairs |  |
| tradeify | ZM | 16 | not in F4 pairs |  |
| topstep | ZL | 17 | not in F4 pairs |  |
| tradeify | MNQ | 18 | not in F4 pairs |  |
| mffu | MNQ | 19 | not in F4 pairs |  |
| topstep | M2K | 20 | not in F4 pairs |  |
| bulenox | M2K | 22 | not in F4 pairs |  |
| lucid | RTY | 24 | not in F4 pairs |  |
| bulenox | ZM | 26 | Layer 2 gate | E, L1, D, A, R, P, F (dropped), Rel |
| mffu | MCL | 28 | not in F4 pairs |  |
| tradeify | M2K | 29 | not in F4 pairs |  |
| tradeify | MYM | 30 | not in F4 pairs |  |
| mffu | M2K | 31 | not in F4 pairs |  |
| mffu | MYM | 32 | not in F4 pairs |  |
| topstep | NQ | 33 | excluded (V49) |  |
| topstep | RTY | 35 | not in F4 pairs |  |
| lucid | MNQ | 36 | Layer 2 gate | E, A, D, R, L1, Rel, F (dropped), P |
| mffu | ZL | 37 | not in F4 pairs |  |
| lucid | ZL | 38 | not in F4 pairs |  |
| mffu | RTY | 39 | not in F4 pairs |  |
| lucid | M2K | 41 | not in F4 pairs |  |
| tradeify | ZL | 42 | not in F4 pairs |  |
| tradeify | RTY | 43 | not in F4 pairs |  |
| tradeify | YM | 44 | not in F4 pairs |  |
| lucid | NQ | 45 | excluded (V49) |  |
| topstep | MNG | 46 | not in F4 pairs |  |
| mffu | M6E | 47 | not in F4 pairs |  |
| mffu | YM | 48 | not in F4 pairs |  |
| topstep | MHG | 49 | not in F4 pairs |  |
| mffu | NQ | 52 | not in F4 pairs |  |
| tradeify | MCL | 53 | not in F4 pairs |  |
| tradeify | NQ | 54 | not in F4 pairs |  |
| topstep | SIL | 56 | Layer 1 gate |  |
| bulenox | RTY | 57 | not in F4 pairs |  |
| mffu | SIL | 58 | not in F4 pairs |  |
| bulenox | ZL | 59 | not in F4 pairs |  |
| bulenox | M6E | 60 | not in F4 pairs |  |
| topstep | M6E | 61 | not in F4 pairs |  |
| bulenox | NQ | 62 | excluded (V49) |  |
| tradeify | M6E | 63 | not in F4 pairs |  |
| lucid | SIL | 64 | Layer 1 gate |  |
| topstep | MBT | 65 | not in F4 pairs |  |
| bulenox | MBT | 66 | not in F4 pairs |  |
| mffu | MBT | 67 | not in F4 pairs |  |

## For the lead

- leader: leader from F4 (notional ADV not computable for every sibling) [MZM, ZM]
- D2 c (ZM): provisional, notional ADV unknown for MZM in family grains (ADV, multiplier or F3 median close unknown); compared among known codes only [MZM, ZM]
- D2 c (SI): provisional, notional ADV unknown for SI, SIL in family metals (ADV, multiplier or F3 median close unknown); compared among known codes only [SI, SIL]
- Rel (bulenox) rel_payout: unknown -> no deduction (spec names no default; E.28 practice) [bulenox|CL, bulenox|MCL, bulenox|MNQ, bulenox|MYM, bulenox|MZM, bulenox|QM, bulenox|SI, bulenox|SIL, bulenox|YM, bulenox|ZM]
- gate: listed_50k unknown -> excluded (script choice; spec gates on 'does not list') [bulenox|ZM]

## Input checks

- partial universe (allowed by flag): 36 spec codes absent
