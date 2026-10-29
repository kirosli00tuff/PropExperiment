# E.32b economics: regression against E.28 (A3_econ.json)

Written by econ32b_regress.py at 2026-10-29 00:53:38 PDT (EconSetup-OpusXHigh). Code: work/econ/econ32b*.py on E.28's A3_funnel.py / A3_models.py / A3_run.py (copied unchanged, COPY_MANIFEST.json); inputs: E.28's A3_inputs.json (copied), S = 1 tick for every pair, T = 20, sigma_T = sigma_1m, market case only, grid 0..5.00 ticks at 0.01, bisection then E.28's grid confirmation.

E.28 reports mu10K in the limit case; with S = 1.00 its market twin is mu10K + 1.00 exactly (EV and P10K depend on mu only through d = mu - c, on the same common random numbers). The grid runs to 5.00 so every E.28 value <= 4 has its twin on the grid. A pass is a difference of at most one grid step (0.01).

## Result: PASS

- Pairs compared: 121 (every E.28 pair computed; 11 E.28 pairs not computed there either: bulenox|MET, bulenox|SI, lucid|SI, lucid|SIL, mffu|MET, mffu|SI, mffu|SIL, topstep|MET, topstep|SI, topstep|SIL, tradeify|SI).
- mu*_mkt within one grid step: 121 / 121; identical (or above 4 in both): 121 / 121.
- mu10K_mkt = E.28 mu10K + 1.00 within one grid step: 121 / 121; identical (or above the cap in both): 121 / 121.
- Cost per attempt (E.28's definition): largest absolute difference USD 0.
- EV at the mu*_mkt grid point vs E.28's grid_check f_at_k: largest absolute difference 4.500000002849447e-06 USD over 92 pairs (floating point only: E.28 passed the unrounded d to the day law, this code d rounded to 1e-9 ticks; no threshold moves).
- Thresholds corrected by the grid confirmation: 0; unconfirmed: 0.
- Work: 6462 evaluations, 19590 s summed over jobs; run stats: {"chunks": [{"fingerprint": "27af1bdb86ecd928", "jobs": 31, "ran": 31, "workers": 6, "wall_s": 901.4, "peak_pss_mb": 1879, "min_mem_available_mb": 8589}, {"fingerprint": "27af1bdb86ecd928", "jobs": 30, "ran": 29, "workers": 6, "wall_s": 839.3, "peak_pss_mb": 1932, "min_mem_available_mb": 6223}, {"fingerprint": "27af1bdb86ecd928", "jobs": 30, "ran": 29, "workers": 6, "wall_s": 805.8, "peak_pss_mb": 2006, "min_mem_available_mb": 6380}, {"fingerprint": "27af1bdb86ecd928", "jobs": 30, "ran": 30, "workers": 6, "wall_s": 823.1, "peak_pss_mb": 2032, "min_mem_available_mb": 6426}], "wall_s_total": 3369.6, "peak_pss_mb_max": 2032}.

## Every pair

| pair | E.28 mu*_mkt | new mu*_mkt | E.28 mu10K (lim) | new mu10K_mkt | cost E.28 | cost new | evals |
|---|---|---|---|---|---|---|---|
| bulenox|6A | 3.17 | 3.17 | 2.75 | 3.75 | 175.00 | 175.00 | 63 |
| bulenox|6E | 2.67 | 2.67 | 2.21 | 3.21 | 175.00 | 175.00 | 61 |
| bulenox|CL | 1.76 | 1.76 | 1.44 | 2.44 | 175.00 | 175.00 | 54 |
| bulenox|GC | 1.82 | 1.82 | 1.43 | 2.43 | 175.00 | 175.00 | 55 |
| bulenox|HG | 1.74 | 1.74 | 1.13 | 2.13 | 175.00 | 175.00 | 52 |
| bulenox|M2K | > 4 | above cap | > 4 | above cap | 175.00 | 175.00 | 51 |
| bulenox|M6A | > 4 | above cap | > 4 | above cap | 175.00 | 175.00 | 51 |
| bulenox|M6E | > 4 | above cap | > 4 | above cap | 175.00 | 175.00 | 51 |
| bulenox|MBT | > 4 | above cap | > 4 | above cap | 175.00 | 175.00 | 51 |
| bulenox|MCL | > 4 | above cap | > 4 | above cap | 175.00 | 175.00 | 51 |
| bulenox|MGC | > 4 | above cap | > 4 | above cap | 175.00 | 175.00 | 51 |
| bulenox|MNQ | > 4 | above cap | > 4 | above cap | 175.00 | 175.00 | 51 |
| bulenox|MYM | > 4 | above cap | > 4 | above cap | 175.00 | 175.00 | 51 |
| bulenox|NG | 1.76 | 1.76 | 1.44 | 2.44 | 175.00 | 175.00 | 54 |
| bulenox|NQ | 2.37 | 2.37 | 3.10 | 4.10 | 175.00 | 175.00 | 81 |
| bulenox|QG | 1.69 | 1.69 | 0.93 | 1.93 | 175.00 | 175.00 | 48 |
| bulenox|QM | 1.72 | 1.72 | 1.06 | 2.06 | 175.00 | 175.00 | 51 |
| bulenox|RTY | 2.59 | 2.59 | 2.76 | 3.76 | 175.00 | 175.00 | 68 |
| bulenox|YM | 2.46 | 2.46 | 2.80 | 3.80 | 175.00 | 175.00 | 67 |
| bulenox|ZL | 2.78 | 2.78 | 2.50 | 3.50 | 175.00 | 175.00 | 63 |
| bulenox|ZM | 2.08 | 2.08 | 1.50 | 2.50 | 175.00 | 175.00 | 50 |
| bulenox|ZS | 1.83 | 1.83 | 1.21 | 2.21 | 175.00 | 175.00 | 52 |
| bulenox|ZW | 1.85 | 1.85 | 1.21 | 2.21 | 175.00 | 175.00 | 52 |
| lucid|6A | 1.98 | 1.98 | 2.28 | 3.28 | 120.87 | 120.87 | 64 |
| lucid|6E | 1.78 | 1.78 | 1.76 | 2.76 | 120.87 | 120.87 | 58 |
| lucid|CL | 1.40 | 1.40 | 0.86 | 1.86 | 120.91 | 120.91 | 44 |
| lucid|GC | 1.46 | 1.46 | 0.93 | 1.93 | 120.87 | 120.87 | 48 |
| lucid|HG | 1.37 | 1.37 | 0.81 | 1.81 | 120.87 | 120.87 | 46 |
| lucid|M2K | 3.36 | 3.36 | > 4 | above cap | 120.87 | 120.87 | 66 |
| lucid|MCL | 2.17 | 2.17 | > 4 | above cap | 120.87 | 120.87 | 65 |
| lucid|MGC | 2.78 | 2.78 | > 4 | above cap | 120.87 | 120.87 | 66 |
| lucid|MNQ | 3.21 | 3.21 | > 4 | above cap | 120.87 | 120.87 | 65 |
| lucid|MYM | 3.34 | 3.34 | > 4 | above cap | 120.87 | 120.87 | 65 |
| lucid|NG | 1.40 | 1.40 | 0.86 | 1.86 | 120.91 | 120.91 | 44 |
| lucid|NQ | 1.64 | 1.64 | 1.85 | 2.85 | 126.29 | 126.29 | 64 |
| lucid|QG | 1.22 | 1.22 | 0.74 | 1.74 | 120.87 | 120.87 | 49 |
| lucid|QM | 1.33 | 1.33 | 0.77 | 1.77 | 120.87 | 120.87 | 45 |
| lucid|RTY | 1.70 | 1.70 | 1.66 | 2.66 | 120.88 | 120.88 | 57 |
| lucid|YM | 1.70 | 1.70 | 1.62 | 2.62 | 120.93 | 120.93 | 56 |
| lucid|ZC | 1.46 | 1.46 | 0.96 | 1.96 | 120.87 | 120.87 | 48 |
| lucid|ZL | 1.94 | 1.94 | 1.87 | 2.87 | 120.87 | 120.87 | 57 |
| lucid|ZM | 1.57 | 1.57 | 1.12 | 2.12 | 120.87 | 120.87 | 51 |
| lucid|ZS | 1.45 | 1.45 | 0.90 | 1.90 | 120.87 | 120.87 | 48 |
| lucid|ZW | 1.45 | 1.45 | 0.90 | 1.90 | 120.87 | 120.87 | 48 |
| mffu|6A | 2.03 | 2.03 | 2.39 | 3.39 | 153.00 | 153.00 | 64 |
| mffu|6E | 1.83 | 1.83 | 1.92 | 2.92 | 153.00 | 153.00 | 59 |
| mffu|CL | 1.51 | 1.51 | 1.06 | 2.06 | 153.00 | 153.00 | 49 |
| mffu|GC | 1.53 | 1.53 | 1.10 | 2.10 | 153.00 | 153.00 | 48 |
| mffu|HG | 1.42 | 1.42 | 0.91 | 1.91 | 153.00 | 153.00 | 50 |
| mffu|M2K | > 4 | above cap | > 4 | above cap | 153.00 | 153.00 | 51 |
| mffu|M6A | 2.64 | 2.64 | > 4 | above cap | 153.00 | 153.00 | 65 |
| mffu|M6E | 2.31 | 2.31 | > 4 | above cap | 153.00 | 153.00 | 66 |
| mffu|MBT | > 4 | above cap | > 4 | above cap | 153.00 | 153.00 | 51 |
| mffu|MCL | 2.34 | 2.34 | > 4 | above cap | 153.00 | 153.00 | 64 |
| mffu|MGC | 3.38 | 3.38 | > 4 | above cap | 153.00 | 153.00 | 66 |
| mffu|MNQ | > 4 | above cap | > 4 | above cap | 153.00 | 153.00 | 51 |
| mffu|MYM | > 4 | above cap | > 4 | above cap | 153.00 | 153.00 | 51 |
| mffu|NG | 1.53 | 1.53 | 1.08 | 2.08 | 153.00 | 153.00 | 49 |
| mffu|NQ | 1.98 | 1.98 | 2.32 | 3.32 | 153.00 | 153.00 | 72 |
| mffu|QG | 1.25 | 1.25 | 0.79 | 1.79 | 153.00 | 153.00 | 45 |
| mffu|QM | 1.35 | 1.35 | 0.90 | 1.90 | 153.00 | 153.00 | 46 |
| mffu|RTY | 1.96 | 1.96 | 2.12 | 3.12 | 153.00 | 153.00 | 60 |
| mffu|YM | 2.18 | 2.18 | 2.31 | 3.31 | 153.00 | 153.00 | 62 |
| mffu|ZC | 1.50 | 1.50 | 1.04 | 2.04 | 153.00 | 153.00 | 49 |
| mffu|ZL | 2.03 | 2.03 | 2.15 | 3.15 | 153.00 | 153.00 | 62 |
| mffu|ZM | 1.62 | 1.62 | 1.30 | 2.30 | 153.00 | 153.00 | 51 |
| mffu|ZS | 1.50 | 1.50 | 0.99 | 1.99 | 153.00 | 153.00 | 48 |
| mffu|ZW | 1.50 | 1.50 | 1.03 | 2.03 | 153.00 | 153.00 | 50 |
| topstep|6A | 1.91 | 1.91 | 1.67 | 2.67 | 49.59 | 49.59 | 58 |
| topstep|6E | 1.74 | 1.74 | 1.23 | 2.23 | 49.53 | 49.53 | 53 |
| topstep|CL | 1.45 | 1.45 | 0.82 | 1.82 | 49.59 | 49.59 | 48 |
| topstep|GC | 1.50 | 1.50 | 0.82 | 1.82 | 49.46 | 49.46 | 46 |
| topstep|HG | 1.40 | 1.40 | 0.62 | 1.62 | 49.48 | 49.48 | 42 |
| topstep|M2K | > 4 | above cap | > 4 | above cap | 168.75 | 168.75 | 51 |
| topstep|M6A | > 4 | above cap | > 4 | above cap | 202.81 | 202.81 | 51 |
| topstep|M6E | > 4 | above cap | > 4 | above cap | 206.90 | 206.90 | 51 |
| topstep|MBT | > 4 | above cap | > 4 | above cap | 49.82 | 49.82 | 51 |
| topstep|MCL | > 4 | above cap | > 4 | above cap | 111.33 | 111.33 | 51 |
| topstep|MGC | > 4 | above cap | > 4 | above cap | 99.57 | 99.57 | 51 |
| topstep|MHG | > 4 | above cap | > 4 | above cap | 99.04 | 99.04 | 51 |
| topstep|MNG | > 4 | above cap | > 4 | above cap | 100.01 | 100.01 | 51 |
| topstep|MNQ | > 4 | 4.26 | > 4 | above cap | 165.14 | 165.14 | 66 |
| topstep|MYM | > 4 | above cap | > 4 | above cap | 168.89 | 168.89 | 51 |
| topstep|NG | 1.47 | 1.47 | 0.84 | 1.84 | 49.50 | 49.50 | 47 |
| topstep|NQ | 1.44 | 1.44 | 1.83 | 2.83 | 49.99 | 49.99 | 64 |
| topstep|QG | 1.19 | 1.19 | 0.49 | 1.49 | 92.05 | 92.05 | 45 |
| topstep|QM | 1.32 | 1.32 | 0.54 | 1.54 | 50.53 | 50.53 | 40 |
| topstep|RTY | 1.88 | 1.88 | 1.50 | 2.50 | 49.73 | 49.73 | 51 |
| topstep|YM | 1.86 | 1.86 | 1.57 | 2.57 | 49.71 | 49.71 | 55 |
| topstep|ZB | 1.11 | 1.11 | 0.20 | 1.20 | 56.99 | 56.99 | 37 |
| topstep|ZC | 1.46 | 1.46 | 0.71 | 1.71 | 49.20 | 49.20 | 44 |
| topstep|ZF | 1.37 | 1.37 | 0.88 | 1.88 | 77.40 | 77.40 | 48 |
| topstep|ZL | 1.99 | 1.99 | 1.44 | 2.44 | 49.23 | 49.23 | 52 |
| topstep|ZM | 1.59 | 1.59 | 0.86 | 1.86 | 49.23 | 49.23 | 45 |
| topstep|ZN | 1.19 | 1.19 | 0.40 | 1.40 | 65.57 | 65.57 | 42 |
| topstep|ZS | 1.48 | 1.48 | 0.70 | 1.70 | 49.24 | 49.24 | 43 |
| topstep|ZT | 1.40 | 1.40 | 0.90 | 1.90 | 77.68 | 77.68 | 45 |
| topstep|ZW | 1.48 | 1.48 | 0.69 | 1.69 | 49.23 | 49.23 | 43 |
| tradeify|6A | 2.26 | 2.26 | 1.96 | 2.96 | 95.83 | 95.83 | 57 |
| tradeify|6E | 2.00 | 2.00 | 1.61 | 2.61 | 95.83 | 95.83 | 55 |
| tradeify|CL | 1.59 | 1.59 | 0.97 | 1.97 | 95.84 | 95.84 | 48 |
| tradeify|GC | 1.61 | 1.61 | 1.01 | 2.01 | 95.83 | 95.83 | 49 |
| tradeify|HG | 1.50 | 1.50 | 0.81 | 1.81 | 95.83 | 95.83 | 45 |
| tradeify|M2K | > 4 | above cap | > 4 | above cap | 95.83 | 95.83 | 51 |
| tradeify|M6A | > 4 | above cap | > 4 | above cap | 95.83 | 95.83 | 51 |
| tradeify|M6E | > 4 | above cap | > 4 | above cap | 95.83 | 95.83 | 51 |
| tradeify|MCL | > 4 | above cap | > 4 | above cap | 95.83 | 95.83 | 51 |
| tradeify|MGC | > 4 | above cap | > 4 | above cap | 95.83 | 95.83 | 51 |
| tradeify|MNQ | > 4 | 4.86 | > 4 | above cap | 95.83 | 95.83 | 66 |
| tradeify|MYM | > 4 | above cap | > 4 | above cap | 95.83 | 95.83 | 51 |
| tradeify|NG | 1.61 | 1.61 | 1.00 | 2.00 | 95.83 | 95.83 | 48 |
| tradeify|NQ | 2.05 | 2.05 | 2.22 | 3.22 | 98.37 | 98.37 | 72 |
| tradeify|QG | 1.33 | 1.33 | 0.61 | 1.61 | 95.83 | 95.83 | 44 |
| tradeify|QM | 1.43 | 1.43 | 0.75 | 1.75 | 95.83 | 95.83 | 46 |
| tradeify|RTY | 2.13 | 2.13 | 1.92 | 2.92 | 95.83 | 95.83 | 60 |
| tradeify|YM | 2.13 | 2.13 | 1.90 | 2.90 | 95.83 | 95.83 | 59 |
| tradeify|ZC | 1.58 | 1.58 | 0.89 | 1.89 | 95.83 | 95.83 | 49 |
| tradeify|ZL | 2.20 | 2.20 | 1.85 | 2.85 | 95.83 | 95.83 | 59 |
| tradeify|ZM | 1.92 | 1.92 | 1.31 | 2.31 | 95.83 | 95.83 | 52 |
| tradeify|ZS | 2.22 | 2.22 | 1.53 | 2.53 | 95.83 | 95.83 | 56 |
| tradeify|ZW | 2.38 | 2.38 | 1.69 | 2.69 | 95.83 | 95.83 | 56 |
