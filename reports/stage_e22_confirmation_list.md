# Stage E.22 Part A confirmation lists (hashed before any confirmation read)

STATUS: FROZEN at the commit "E.22 confirmation lists". Written by the E.22 lead against docs/prompts/STAGE_E.22.md
Part A, before any bar of any confirmation window was read by any run. After the commit nothing in this file or its
JSONs changes. The machine-read lists are the four JSONs below (they govern where this file differs); each is read by
screening/stage_e_verdict.py and named to the runner's run-once marker.

## 0. Provenance and rules

- Harness: dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4 (reports/stage_e2b_harness_freeze.json, v13).
- Holm K = 5 (R-E22-A10: clusters with a non-empty Tier A: K3, K4, K5, K6, K8; V14 (b)'s K = 9 shown descriptively in the return).
- Program N for DSR = 533 (R-E22-A11: 532 + E22-F1, registered in this stage).
- Price paths declared before any read: reports/stage_e22_price_paths.json (MGC on GC bars, MNQ on NQ bars, each with the
  micro's costs, tick value and q_c; R-E22-A4, R-E22-A5). Rulings: reports/stage_e22_briefs/partA_rulings.md.
- Bootstrap: stationary, mean block 5.0, B = 10,000, a fresh generator per trial seeded 20260923 + list ordinal, np.quantile 0.95.
- One confirmation run per cluster, behind its run-once marker (reports/stage_e22_K*_RUN_ONCE.json).

| Cluster | List JSON | sha256 | Cluster freeze sha256 | Trials (run / listed) |
|---|---|---|---|---|
| K5 | reports/stage_e22_k5_confirmation_list.json | d2a230f3f46c7c0b651f3356fc129ff813dc5a365e54c20057df8d250a222212 | 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 | 8 / 11 |
| K3 | reports/stage_e22_k3_confirmation_list.json | 43456def5b4f627e384eb42de3a84c8c1f0ee5b9c3be403eda6a7d9a21f1e2b4 | c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 | 27 / 30 |
| K6 | reports/stage_e22_k6_confirmation_list.json | ebb3d034ed001498b3c87e8f1e47616e839dddde04868c11e95aa4153aa39e39 | a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 | 27 / 27 |
| K8 | reports/stage_e22_k8_confirmation_list.json | 28ad6f63630681dbb1baeb14d0384f5fbfd6c794c160d32d9380166d3d039ca5 | 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 | 3 / 4 |

## K5

Windows (D4):

| Root (as keyed) | S_X | Window | Price path |
|---|---|---|---|
| MGC | 2019-05-06 | 2019-05-06..2024-02-29 | GC |
| MHG | 2022-06-01 | 2022-06-01..2024-02-29 | - |

| Ord | Trial | Vehicle | Legs | q_c | eps_X ticks ($/day) | Tier | Run | Labels | Seed | Power (supply, n_b, label) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K5-cp1-01 MGC | MGC | MGC | 1 | 71 ($71.00) | B | yes | source-overlap | 20260924 | 1174, 9, power sufficient |
| 2 | K5-cp1-01 MHG | MHG | MHG | 2 | 27 ($67.50) | excluded | no | coverage_below_0.95, source-overlap | 20260925 | not run |
| 3 | K5-cp2-01 MGC | MGC | MGC | 1 | 71 ($71.00) | B | yes | source-overlap | 20260926 | 1174, 44, power sufficient |
| 4 | K5-cp2-01 MHG | MHG | MHG | 2 | 27 ($67.50) | excluded | no | coverage_below_0.95, source-overlap | 20260927 | not run |
| 5 | K5-cp3-01 MGC | MGC | MGC | 1 | 71 ($71.00) | B | yes | source-overlap | 20260928 | 1174, 62, power sufficient |
| 6 | K5-cp3-01 MHG | MHG | MHG | 2 | 27 ($67.50) | B | yes | source-overlap | 20260929 | 425, 52, power sufficient |
| 7 | K5-preauc-01 MGC | MGC | MGC | 1 | 71 ($71.00) | B | yes | source-overlap | 20260930 | 1174, 6, power sufficient |
| 8 | K5-pmfix-01 MGC | MGC | MGC | 1 | 71 ($71.00) | excluded | no | mean_holding_below_10min, source-overlap | 20260931 | 1174, 11, power sufficient |
| 9 | K5-fomc-01 MGC | MGC | MGC | 1 | 71 ($71.00) | A | yes | source-overlap | 20260932 | 1174, 1, power sufficient |
| 10 | K5-ovr-01 MGC | MGC | MGC | 1 | 71 ($71.00) | B | yes | source-overlap | 20260933 | 1174, 29, power sufficient |
| 11 | K5-ovr-01 MHG | MHG | MHG | 2 | 27 ($67.50) | B | yes | source-overlap | 20260934 | 425, 18, power sufficient |

Notes (descriptive, not verdict labels):
- K5-cp1-01 MGC: price path declared before any read (reports/stage_e22_price_paths.json): MGC on GC bars with MGC's costs, tick value and q_c
- K5-cp2-01 MGC: price path declared before any read (reports/stage_e22_price_paths.json): MGC on GC bars with MGC's costs, tick value and q_c
- K5-cp3-01 MGC: price path declared before any read (reports/stage_e22_price_paths.json): MGC on GC bars with MGC's costs, tick value and q_c
- K5-preauc-01 MGC: price path declared before any read (reports/stage_e22_price_paths.json): MGC on GC bars with MGC's costs, tick value and q_c
- K5-pmfix-01 MGC: price path declared before any read (reports/stage_e22_price_paths.json): MGC on GC bars with MGC's costs, tick value and q_c
- K5-fomc-01 MGC: price path declared before any read (reports/stage_e22_price_paths.json): MGC on GC bars with MGC's costs, tick value and q_c
- K5-ovr-01 MGC: price path declared before any read (reports/stage_e22_price_paths.json): MGC on GC bars with MGC's costs, tick value and q_c

## K3

Windows (D4):

| Root (as keyed) | S_X | Window | Price path |
|---|---|---|---|
| 6A | 2019-05-06 | 2019-05-06..2024-02-29 | - |
| 6B | 2019-05-06 | 2019-05-06..2024-02-29 | - |
| 6C | 2019-05-06 | 2019-05-06..2024-02-29 | - |
| 6E | 2019-05-06 | 2019-05-06..2024-02-29 | - |
| 6J | 2019-05-06 | 2019-05-06..2024-02-29 | - |
| 6N | 2019-05-06 | 2019-05-06..2024-02-29 | - |
| 6S | 2019-05-06 | 2019-05-06..2024-02-29 | - |

| Ord | Trial | Vehicle | Legs | q_c | eps_X ticks ($/day) | Tier | Run | Labels | Seed | Power (supply, n_b, label) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K3-cp1-01 6E | 6E | 6E | 1 | 12 ($75.00) | B | yes | source-overlap | 20260924 | 1191, 16, power sufficient |
| 2 | K3-cp1-01 6A | 6A | 6A | 1 | 11 ($55.00) | B | yes | source-overlap | 20260925 | 1191, 6, power sufficient |
| 3 | K3-cp1-01 6B | 6B | 6B | 1 | 8 ($50.00) | B | yes | source-overlap | 20260926 | 1191, 9, power sufficient |
| 4 | K3-cp1-01 6C | 6C | 6C | 1 | 9 ($45.00) | B | yes | source-overlap | 20260927 | 1191, 4, power sufficient |
| 5 | K3-cp1-01 6J | 6J | 6J | 1 | 10 ($62.50) | B | yes | source-overlap | 20260928 | 1191, 7, power sufficient |
| 6 | K3-cp1-01 6S | 6S | 6S | 1 | 13 ($81.25) | excluded | no | coverage_below_0.95, source-overlap | 20260929 | not run |
| 7 | K3-cp1-01 6N | 6N | 6N | 1 | 10 ($50.00) | excluded | no | coverage_below_0.95, source-overlap | 20260930 | not run |
| 8 | K3-cp2-01 6E | 6E | 6E | 1 | 12 ($75.00) | B | yes | source-overlap | 20260931 | 1191, 33, power sufficient |
| 9 | K3-cp2-01 6A | 6A | 6A | 1 | 11 ($55.00) | B | yes | source-overlap | 20260932 | 1191, 32, power sufficient |
| 10 | K3-cp2-01 6B | 6B | 6B | 1 | 8 ($50.00) | B | yes | source-overlap | 20260933 | 1191, 36, power sufficient |
| 11 | K3-cp2-01 6C | 6C | 6C | 1 | 9 ($45.00) | B | yes | source-overlap | 20260934 | 1191, 22, power sufficient |
| 12 | K3-cp2-01 6J | 6J | 6J | 1 | 10 ($62.50) | B | yes | source-overlap | 20260935 | 1191, 30, power sufficient |
| 13 | K3-cp2-01 6S | 6S | 6S | 1 | 13 ($81.25) | B | yes | source-overlap | 20260936 | 1191, 95, power sufficient |
| 14 | K3-cp2-01 6N | 6N | 6N | 1 | 10 ($50.00) | excluded | no | coverage_below_0.95, source-overlap | 20260937 | not run |
| 15 | K3-cp3-01 6E | 6E | 6E | 1 | 12 ($75.00) | B | yes | source-overlap | 20260938 | 1191, 83, power sufficient |
| 16 | K3-cp3-01 6A | 6A | 6A | 1 | 11 ($55.00) | B | yes | source-overlap | 20260939 | 1191, 92, power sufficient |
| 17 | K3-cp3-01 6B | 6B | 6B | 1 | 8 ($50.00) | B | yes | source-overlap | 20260940 | 1191, 67, power sufficient |
| 18 | K3-cp3-01 6C | 6C | 6C | 1 | 9 ($45.00) | B | yes | source-overlap | 20260941 | 1191, 40, power sufficient |
| 19 | K3-cp3-01 6J | 6J | 6J | 1 | 10 ($62.50) | B | yes | source-overlap | 20260942 | 1191, 77, power sufficient |
| 20 | K3-cp3-01 6S | 6S | 6S | 1 | 13 ($81.25) | B | yes | source-overlap | 20260943 | 1191, 179, power sufficient |
| 21 | K3-cp3-01 6N | 6N | 6N | 1 | 10 ($50.00) | B | yes | source-overlap | 20260944 | 1191, 71, power sufficient |
| 22 | K3-ldnrev-01 6E | 6E | 6E | 1 | 12 ($75.00) | A | yes | source-overlap | 20260945 | 1191, 1, power sufficient |
| 23 | K3-ldnrev-01 6J | 6J | 6J | 1 | 10 ($62.50) | B | yes | source-overlap | 20260946 | 1191, 1, power sufficient |
| 24 | K3-ldnrev-01 6S | 6S | 6S | 1 | 13 ($81.25) | B | yes | source-overlap | 20260947 | 1191, 1, power sufficient |
| 25 | K3-ldnmom-01 6E | 6E | 6E | 1 | 12 ($75.00) | B | yes | - | 20260948 | 1191, 9, power sufficient |
| 26 | K3-ldnmom-01 6J | 6J | 6J | 1 | 10 ($62.50) | B | yes | - | 20260949 | 1191, 10, power sufficient |
| 27 | K3-mehedge-01 6J | 6J | 6J | 1 | 10 ($62.50) | B | yes | - | 20260950 | 1191, 1, power sufficient |
| 28 | K3-ecbfix-01 6E | 6E | 6E | 1 | 12 ($75.00) | B | yes | source-overlap | 20260951 | 1191, 394, power sufficient |
| 29 | K3-tkypre-01 6J | 6J | 6J | 1 | 10 ($62.50) | B | yes | source-overlap | 20260952 | 1191, 5, power sufficient |
| 30 | K3-tkypost-01 6J | 6J | 6J | 1 | 10 ($62.50) | B | yes | source-overlap | 20260953 | 1191, 46, power sufficient |

Notes (descriptive, not verdict labels):
- K3-cp1-01 6E: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp1-01 6A: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp1-01 6B: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp1-01 6C: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp1-01 6J: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp1-01 6S: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp1-01 6N: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp2-01 6E: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp2-01 6A: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp2-01 6B: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp2-01 6C: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp2-01 6J: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp2-01 6S: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp2-01 6N: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp3-01 6E: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp3-01 6A: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp3-01 6B: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp3-01 6C: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp3-01 6J: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp3-01 6S: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-cp3-01 6N: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-ldnrev-01 6E: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-ldnrev-01 6J: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-ldnrev-01 6S: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-ldnmom-01 6E: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-ldnmom-01 6J: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-mehedge-01 6J: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-ecbfix-01 6E: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-tkypre-01 6J: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen
- K3-tkypost-01 6J: K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen

## K6

Windows (D4):

| Root (as keyed) | S_X | Window | Price path |
|---|---|---|---|
| HE | 2019-05-06 | 2019-05-06..2024-02-29 | - |
| LE | 2019-05-06 | 2019-05-06..2024-02-29 | - |
| ZC | 2019-05-06 | 2019-05-06..2024-02-29 | - |
| ZL | 2019-05-06 | 2019-05-06..2024-02-29 | - |
| ZM | 2019-05-06 | 2019-05-06..2024-02-29 | - |
| ZS | 2019-05-06 | 2019-05-06..2024-02-29 | - |
| ZW | 2019-05-06 | 2019-05-06..2024-02-29 | - |

| Ord | Trial | Vehicle | Legs | q_c | eps_X ticks ($/day) | Tier | Run | Labels | Seed | Power (supply, n_b, label) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K6-cp1-01 ZC | ZC | ZC | 1 | 4 ($50.00) | B | yes | source-overlap | 20260924 | 1130, 5, power sufficient |
| 2 | K6-cp1-01 ZW | ZW | ZW | 1 | 4 ($50.00) | B | yes | source-overlap | 20260925 | 1129, 11, power sufficient |
| 3 | K6-cp1-01 ZS | ZS | ZS | 1 | 5 ($62.50) | B | yes | source-overlap | 20260926 | 1136, 15, power sufficient |
| 4 | K6-cp1-01 ZM | ZM | ZM | 1 | 5 ($50.00) | B | yes | source-overlap | 20260927 | 1106, 8, power sufficient |
| 5 | K6-cp1-01 ZL | ZL | ZL | 1 | 11 ($66.00) | B | yes | source-overlap | 20260928 | 1129, 14, power sufficient |
| 6 | K6-cp1-01 HE | HE | HE | 1 | 7 ($70.00) | B | yes | source-overlap | 20260929 | 1104, 7, power sufficient |
| 7 | K6-cp1-01 LE | LE | LE | 1 | 8 ($80.00) | B | yes | source-overlap | 20260930 | 1109, 28, power sufficient |
| 8 | K6-cp2-01 ZC | ZC | ZC | 1 | 4 ($50.00) | B | yes | source-overlap | 20260931 | 1130, 23, power sufficient |
| 9 | K6-cp2-01 ZW | ZW | ZW | 1 | 4 ($50.00) | B | yes | source-overlap | 20260932 | 1129, 64, power sufficient |
| 10 | K6-cp2-01 ZS | ZS | ZS | 1 | 5 ($62.50) | B | yes | source-overlap | 20260933 | 1136, 73, power sufficient |
| 11 | K6-cp2-01 ZM | ZM | ZM | 1 | 5 ($50.00) | B | yes | source-overlap | 20260934 | 1106, 67, power sufficient |
| 12 | K6-cp2-01 ZL | ZL | ZL | 1 | 11 ($66.00) | B | yes | source-overlap | 20260935 | 1129, 60, power sufficient |
| 13 | K6-cp2-01 HE | HE | HE | 1 | 7 ($70.00) | B | yes | source-overlap | 20260936 | 1104, 50, power sufficient |
| 14 | K6-cp2-01 LE | LE | LE | 1 | 8 ($80.00) | B | yes | source-overlap | 20260937 | 1109, 191, power sufficient |
| 15 | K6-cp3-01 ZC | ZC | ZC | 1 | 4 ($50.00) | B | yes | source-overlap | 20260938 | 1130, 37, power sufficient |
| 16 | K6-cp3-01 ZW | ZW | ZW | 1 | 4 ($50.00) | B | yes | source-overlap | 20260939 | 1129, 69, power sufficient |
| 17 | K6-cp3-01 ZS | ZS | ZS | 1 | 5 ($62.50) | B | yes | source-overlap | 20260940 | 1136, 108, power sufficient |
| 18 | K6-cp3-01 ZM | ZM | ZM | 1 | 5 ($50.00) | B | yes | source-overlap | 20260941 | 1106, 60, power sufficient |
| 19 | K6-cp3-01 ZL | ZL | ZL | 1 | 11 ($66.00) | B | yes | source-overlap | 20260942 | 1129, 92, power sufficient |
| 20 | K6-cp3-01 HE | HE | HE | 1 | 7 ($70.00) | B | yes | source-overlap | 20260943 | 1104, 70, power sufficient |
| 21 | K6-cp3-01 LE | LE | LE | 1 | 8 ($80.00) | B | yes | source-overlap | 20260944 | 1109, 157, power sufficient |
| 22 | K6-crushgap-01 ZS | ZS | ZS ZM ZL | 1 | 5 ($62.50) | B | yes | source-overlap | 20260945 | 1028, 97, power sufficient |
| 23 | K6-limitcont-01 HE | HE | HE | 1 | 7 ($70.00) | A | yes | source-overlap | 20260946 | 1104, 2, power sufficient |
| 24 | K6-limitcont-01 LE | LE | LE | 1 | 8 ($80.00) | B | yes | source-overlap | 20260947 | power check undefined |
| 25 | K6-wasdepre-01 ZC | ZC | ZC | 1 | 4 ($50.00) | B | yes | source-overlap | 20260948 | 1130, 14, power sufficient |
| 26 | K6-wasdepre-01 ZS | ZS | ZS | 1 | 5 ($62.50) | B | yes | source-overlap | 20260949 | 1136, 23, power sufficient |
| 27 | K6-wasdepost-01 ZC | ZC | ZC | 1 | 4 ($50.00) | B | yes | source-overlap | 20260950 | 1130, 6, power sufficient |

Notes (descriptive, not verdict labels):
- K6-cp2-01 ZC: tick history not source-verified for the research window (K6-L-16 13(a))
- K6-cp2-01 ZW: tick history not source-verified for the research window (K6-L-16 13(a))
- K6-cp2-01 ZS: tick history not source-verified for the research window (K6-L-16 13(a))
- K6-cp2-01 ZM: tick history not source-verified for the research window (K6-L-16 13(a))
- K6-cp2-01 ZL: tick history not source-verified for the research window (K6-L-16 13(a))
- K6-cp2-01 HE: tick history not source-verified for the research window (K6-L-16 13(a))
- K6-cp2-01 LE: tick history not source-verified for the research window (K6-L-16 13(a))
- K6-limitcont-01 HE: Tier A on a single trip (research t 1.002 = sqrt(273/272))
- K6-limitcont-01 HE: limits are the frozen initial limits; expanded limits not encoded (K6-L-07)
- K6-limitcont-01 HE: settlements by the D9.7 proxy (one bar's close); official settlements not tested (R-T3-2)
- K6-limitcont-01 LE: limits are the frozen initial limits; expanded limits not encoded (K6-L-07)
- K6-limitcont-01 LE: settlements by the D9.7 proxy; limit table partly contradicted by CME (R-1b-2)

## K8

Windows (D4):

| Root (as keyed) | S_X | Window | Price path |
|---|---|---|---|
| 6C | 2019-05-06 | 2019-05-06..2024-02-29 | - |
| MBT | 2024-01-02 | 2024-01-02..2024-02-29 | - |
| MCL | 2021-07-12 | 2021-07-12..2024-02-29 | - |
| MES | 2020-02-03 | 2020-02-03..2024-02-29 | - |
| MGC | 2019-05-06 | 2019-05-06..2024-02-29 | GC |
| MNQ | 2019-05-06 | 2019-05-06..2024-02-29 | NQ |

| Ord | Trial | Vehicle | Legs | q_c | eps_X ticks ($/day) | Tier | Run | Labels | Seed | Power (supply, n_b, label) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K8-flight-01 H30 MGC | MGC | MGC MES | 1 | 71 ($71.00) | B | yes | - | 20260924 | 944, 7, power sufficient |
| 2 | K8-flight-01 HEOD MGC | MGC | MGC MES | 1 | 71 ($71.00) | A | yes | - | 20260925 | 944, 22, power sufficient |
| 3 | K8-oilcad-01 6C | 6C | 6C MCL | 1 | 9 ($45.00) | B | yes | - | 20260926 | 569, 15, power sufficient |
| 4 | K8-wkndbtc-01 MNQ | MNQ | MNQ MBT | 1 | 170 ($85.00) | A | no | source-overlap, inconclusive by design | 20260927 | 34, 43, inconclusive by design |

Notes (descriptive, not verdict labels):
- K8-flight-01 H30 MGC: price path declared before any read (reports/stage_e22_price_paths.json): MGC on GC bars with MGC's costs, tick value and q_c
- K8-flight-01 HEOD MGC: price path declared before any read (reports/stage_e22_price_paths.json): MGC on GC bars with MGC's costs, tick value and q_c
- K8-wkndbtc-01 MNQ: confirmation window wholly in the weekend-closure regime (E.9 (b))
- K8-wkndbtc-01 MNQ: not run (inconclusive by design): D4 power check fails: the MBT-limited confirmation window (MBT S_X 2024-01-02, reports/stage_e_start_rule_K8.json) supplies 34 days against n_b 43 (reports/stage_e22_power_k8); U8's substitute for a short-history micro, CME full-size BTC bars for the MBT signal path, is not owned and is not bought (prompt A2; lead rulings R-E22-A6, R-E22-A9). Under the strict reading of A2 (no NQ path for MNQ) the trial is also untestable on owned data (missing MNQ); not run either way.
- K8-wkndbtc-01 MNQ: price path declared before any read (reports/stage_e22_price_paths.json): MNQ on NQ bars with MNQ's costs, tick value and q_c

## Tests and decision rules (fixed now; identical in every JSON's `rules`)

- **null.** NULL_CRITERIA_E 3: UCB95 < eps_X and Phi(eps_X / SE_boot - 1.645) >= 0.80; zero trips or SE_boot = 0 inconclusive; < 30 closed trips 'null by inactivity'; a trial labelled 'inconclusive by design' or 'untestable on owned data' is not covered; OC-H-excluded trials are listed, not run, not covered (L-E5-5).
- **edge_chain.** D5 with V14 and the E.22 rulings: Holm over the Tier A one-sided p at 0.05 / K, K = 5 (R-E22-A10), a Tier A trial with no record at p = 1 (R-E22-A13); composite verdict pending, not built unless the rest passes (V14 a); DSR > 0.95 at program N = 533 (R-E22-A11) with the Sharpe variance over Tier A, or over every run trial of the cluster when fewer than two Tier A series exist (V14 c); daily t > 3.0 one-sided; CSCV PBO < 0.5 on 8 contiguous blocks over Tier A, or over every run trial when fewer than two Tier A series exist (L-E5-3), aligned on the union of the run trials' window dates, zeros off each trial's dates.
- **wording.** A trial passing Holm, DSR, t and PBO reads 'edge candidate, composite pending', never 'edge'; a source-overlap trial adds 'no edge claim without a registered holdout read'.
- **code.** screening/stage_e_verdict.py under the harness sha256 above; one confirmation run per cluster, behind a run-once marker.

## Hashing record

Each JSON was written first (sha256 above); this file embeds those hashes and is hashed second; all hashes go into the
commit message "E.22 confirmation lists". Each cluster's confirmation run happens only after that commit, once.
