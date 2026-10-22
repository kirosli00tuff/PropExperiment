### topstep: 50K Trading Combine, Standard Path (USD 49/month)

| code | v USD | F_rt USD | F_rt ticks | sigma_T | mu*_lim | mu*_mkt | mu10K | cost/attempt USD | room | DLL ticks | pos. limit | grid check | sensitivities | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | 5.0000 | 4.22 | 0.844 | 3.09 | 0.91 | 1.91 | 1.67 | 49.6 | 2.90 | - | 5 | ok (56 pts) | ex-API mu*_lim 0.90; fee 4.22: mu*_lim 0.91 | non-monotone cached points |
| 6E | 6.2500 | 4.22 | 0.675 | 3.56 | 0.74 | 1.74 | 1.23 | 49.5 | 2.09 | - | 5 | ok (52 pts) | ex-API mu*_lim 0.73; fee 4.22: mu*_lim 0.74; S_rt 1.200: mu*_mkt 1.94 | non-monotone cached points |
| CL | 10.0000 | 4.02 | 0.402 | 6.30 | 0.45 | 1.45 | 0.82 | 49.6 | 0.82 | - | 3 | ok (48 pts) | ex-API mu*_lim 0.43; fee 4.02: mu*_lim 0.45 | non-monotone cached points |
| GC | 10.0000 | 4.32 | 0.432 | 5.29 | 0.50 | 1.50 | 0.82 | 49.5 | 0.91 | - | 3 | ok (45 pts) | ex-API mu*_lim 0.48; fee 4.32: mu*_lim 0.50 | non-monotone cached points |
| HG | 12.5000 | 4.32 | 0.346 | 3.14 | 0.40 | 1.40 | 0.62 | 49.5 | 1.01 | - | 0 | ok (42 pts) | ex-API mu*_lim 0.39; fee 4.32: mu*_lim 0.40 | position_limit_0; non-monotone cached points |
| M2K | 0.5000 | 1.22 | 2.440 | 10.01 | > 4 | > 4 | > 4 | 168.8 | 11.73 | - | 50 | ok (52 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 | sigma_1m and R_d from sibling RTY (OC-1); non-monotone cached points |
| M6A | 1.0000 | 1.00 | 1.000 | 1.55 | > 4 | > 4 | > 4 | 202.8 | 28.99 | - | 50 | ok (51 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 | sigma_1m and R_d from sibling 6A (OC-1) |
| M6E | 1.2500 | 1.00 | 0.800 | 1.78 | > 4 | > 4 | > 4 | 206.9 | 20.92 | - | 50 | ok (52 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 | sigma_1m and R_d from sibling 6E (OC-1) |
| MBT | 0.5000 | 2.82 | 5.640 | 4.92 | > 4 | > 4 | > 4 | 49.8 | 23.67 | - | 5 | ok (52 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 | non-monotone cached points |
| MCL | 1.0000 | 1.72 | 1.720 | 6.49 | > 4 | > 4 | > 4 | 111.3 | 8.15 | - | 30 | ok (52 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 |  |
| MET | 0.0500 | 0.72 | 14.400 | - | - | - | - | - | - | - | 5 | - |  | not computed |
| MGC | 1.0000 | 1.92 | 1.920 | 5.40 | > 4 | > 4 | > 4 | 99.6 | 9.09 | - | 30 | ok (52 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 |  |
| MHG | 1.2500 | 1.92 | 1.536 | 3.38 | > 4 | > 4 | > 4 | 99.0 | 10.06 | - | 2 | ok (51 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 |  |
| MNG | 1.0000 | 1.92 | 1.920 | 6.28 | > 4 | > 4 | > 4 | 100.0 | 12.66 | - | 50 | ok (52 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 | sigma_1m and R_d from sibling NG (OC-1) |
| MNQ | 0.5000 | 1.22 | 2.440 | 27.83 | 3.26 | > 4 | > 4 | 165.1 | 4.14 | - | 50 | ok (72 pts) | ex-API mu*_lim 3.06; fee 3.70: mu*_lim > 4 | sigma_1m and R_d from sibling NQ (OC-1); non-monotone cached points |
| MYM | 0.5000 | 1.22 | 2.440 | 12.14 | > 4 | > 4 | > 4 | 168.9 | 10.18 | - | 50 | ok (52 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 | sigma_1m and R_d from sibling YM (OC-1); non-monotone cached points |
| NG | 10.0000 | 4.22 | 0.422 | 6.28 | 0.47 | 1.47 | 0.84 | 49.5 | 1.27 | - | 5 | ok (47 pts) | ex-API mu*_lim 0.45; fee 4.22: mu*_lim 0.47 | non-monotone cached points |
| NQ | 5.0000 | 3.78 | 0.756 | 27.83 | 0.44 | 1.44 | 1.83 | 50.0 | 0.41 | - | 5 | ok (61 pts) | ex-API mu*_lim 0.37; fee 3.78: mu*_lim 0.44 |  |
| QG | 12.5000 | 2.02 | 0.162 | 1.26 | 0.19 | 1.19 | 0.49 | 92.0 | 5.06 | - | 5 | ok (42 pts) | ex-API mu*_lim 0.19; fee 3.70: mu*_lim 0.33 | sigma_1m and R_d from sibling NG (OC-1); non-monotone cached points |
| QM | 12.5000 | 3.42 | 0.274 | 2.52 | 0.32 | 1.32 | 0.54 | 50.5 | 1.64 | - | 3 | ok (45 pts) | ex-API mu*_lim 0.32; fee 3.70: mu*_lim 0.35 | sigma_1m and R_d from sibling CL (OC-1); non-monotone cached points |
| RTY | 5.0000 | 3.78 | 0.756 | 10.01 | 0.88 | 1.88 | 1.50 | 49.7 | 1.17 | - | 5 | ok (54 pts) | ex-API mu*_lim 0.85; fee 3.78: mu*_lim 0.88 | non-monotone cached points |
| SI | 25.0000 | 4.32 | 0.173 | - | - | - | - | - | - | - | 0 | - |  | position_limit_0; not computed |
| SIL | 5.0000 | 2.72 | 0.544 | - | - | - | - | - | - | - | 2 | - |  | not computed |
| YM | 5.0000 | 3.78 | 0.756 | 12.14 | 0.86 | 1.86 | 1.57 | 49.7 | 1.02 | - | 5 | ok (55 pts) | ex-API mu*_lim 0.81; fee 3.78: mu*_lim 0.86 | non-monotone cached points |
| ZB | 31.2500 | 2.76 | 0.088 | 1.22 | 0.11 | 1.11 | 0.20 | 57.0 | 1.33 | - | 5 | ok (37 pts) | ex-API mu*_lim 0.11; fee 3.70: mu*_lim 0.14 | non-monotone cached points |
| ZC | 12.5000 | 5.28 | 0.422 | 1.71 | 0.46 | 1.46 | 0.71 | 49.2 | 3.68 | - | 5 | ok (45 pts) | ex-API mu*_lim 0.45; fee 5.28: mu*_lim 0.46; S_rt 1.260: mu*_mkt 1.72 | non-monotone cached points |
| ZF | 7.8125 | 2.32 | 0.297 | 1.68 | 0.37 | 1.37 | 0.88 | 77.4 | 4.06 | - | 5 | ok (47 pts) | ex-API mu*_lim 0.35; fee 3.70: mu*_lim 0.55 | non-monotone cached points |
| ZL | 6.0000 | 5.28 | 0.880 | 5.52 | 0.99 | 1.99 | 1.44 | 49.2 | 2.01 | - | 5 | ok (55 pts) | ex-API mu*_lim 0.97; fee 5.28: mu*_lim 0.99 | non-monotone cached points |
| ZM | 10.0000 | 5.28 | 0.528 | 3.15 | 0.59 | 1.59 | 0.86 | 49.2 | 2.08 | - | 5 | ok (47 pts) | ex-API mu*_lim 0.58; fee 5.28: mu*_lim 0.59 | non-monotone cached points |
| ZN | 15.6250 | 2.62 | 0.168 | 1.28 | 0.19 | 1.19 | 0.40 | 65.6 | 2.75 | - | 5 | ok (41 pts) | ex-API mu*_lim 0.19; fee 3.70: mu*_lim 0.26 | non-monotone cached points |
| ZS | 12.5000 | 5.28 | 0.422 | 3.11 | 0.48 | 1.48 | 0.70 | 49.2 | 1.77 | - | 5 | ok (46 pts) | ex-API mu*_lim 0.47; fee 5.28: mu*_lim 0.48; S_rt 1.118: mu*_mkt 1.60 | non-monotone cached points |
| ZT | 7.8125 | 2.32 | 0.297 | 1.58 | 0.40 | 1.40 | 0.90 | 77.7 | 4.88 | - | 5 | ok (45 pts) | ex-API mu*_lim 0.37; fee 3.70: mu*_lim 0.58 | non-monotone cached points |
| ZW | 12.5000 | 5.28 | 0.422 | 2.72 | 0.48 | 1.48 | 0.69 | 49.2 | 2.06 | - | 5 | ok (46 pts) | ex-API mu*_lim 0.47; fee 5.28: mu*_lim 0.48; S_rt 1.100: mu*_mkt 1.58 | non-monotone cached points |

### lucid: LucidPro 50K (USD 172 one-time, DLL on)

| code | v USD | F_rt USD | F_rt ticks | sigma_T | mu*_lim | mu*_mkt | mu10K | cost/attempt USD | room | DLL ticks | pos. limit | grid check | sensitivities | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | 5.0000 | 4.80 | 0.960 | 3.09 | 0.98 | 1.98 | 2.28 | 120.9 | 2.90 | 240.0 | 4 | ok (60 pts) | fee 6.20: mu*_lim 1.26 |  |
| 6E | 6.2500 | 4.80 | 0.768 | 3.56 | 0.78 | 1.78 | 1.76 | 120.9 | 2.09 | 192.0 | 4 | ok (55 pts) | fee 6.20: mu*_lim 1.00; S_rt 1.200: mu*_mkt 1.98 |  |
| CL | 10.0000 | 4.00 | 0.400 | 6.30 | 0.40 | 1.40 | 0.86 | 120.9 | 0.82 | 120.0 | 4 | ok (45 pts) | fee 5.98: mu*_lim 0.60 |  |
| GC | 10.0000 | 4.60 | 0.460 | 5.29 | 0.46 | 1.46 | 0.93 | 120.9 | 0.91 | 120.0 | 4 | ok (45 pts) | fee 6.20: mu*_lim 0.62 |  |
| HG | 12.5000 | 4.60 | 0.368 | 3.14 | 0.37 | 1.37 | 0.81 | 120.9 | 1.01 | 96.0 | 4 | ok (44 pts) | fee 6.20: mu*_lim 0.50 |  |
| M2K | 0.5000 | 1.00 | 2.000 | 10.01 | 2.36 | 3.36 | > 4 | 120.9 | 11.73 | 2,400.0 | 40 | ok (63 pts) | fee 1.90: mu*_lim > 4 | sigma_1m and R_d from sibling RTY (OC-1) |
| MCL | 1.0000 | 1.00 | 1.000 | 6.49 | 1.17 | 2.17 | > 4 | 120.9 | 8.15 | 1,200.0 | 40 | ok (63 pts) | fee 2.12: mu*_lim 2.29 |  |
| MGC | 1.0000 | 1.60 | 1.600 | 5.40 | 1.78 | 2.78 | > 4 | 120.9 | 9.09 | 1,200.0 | 40 | ok (63 pts) | fee 2.20: mu*_lim 2.38 |  |
| MNQ | 0.5000 | 1.00 | 2.000 | 27.83 | 2.21 | 3.21 | > 4 | 120.9 | 4.14 | 2,400.0 | 40 | ok (62 pts) | fee 1.90: mu*_lim > 4 | sigma_1m and R_d from sibling NQ (OC-1) |
| MYM | 0.5000 | 1.00 | 2.000 | 12.14 | 2.34 | 3.34 | > 4 | 120.9 | 10.18 | 2,400.0 | 40 | ok (62 pts) | fee 1.90: mu*_lim > 4 | sigma_1m and R_d from sibling YM (OC-1) |
| NG | 10.0000 | 4.00 | 0.400 | 6.28 | 0.40 | 1.40 | 0.86 | 120.9 | 1.27 | 120.0 | 4 | ok (45 pts) | fee 6.20: mu*_lim 0.62 |  |
| NQ | 5.0000 | 3.50 | 0.700 | 27.83 | 0.64 | 1.64 | 1.85 | 126.3 | 0.41 | 240.0 | 4 | ok (59 pts) | fee 5.76: mu*_lim 1.09 | non-monotone cached points |
| QG | 12.5000 | 2.60 | 0.208 | 1.26 | 0.22 | 1.22 | 0.74 | 120.9 | 5.06 | 96.0 | 4 | ok (45 pts) | fee 4.00: mu*_lim 0.33 | sigma_1m and R_d from sibling NG (OC-1) |
| QM | 12.5000 | 4.00 | 0.320 | 2.52 | 0.33 | 1.33 | 0.77 | 120.9 | 1.64 | 96.0 | 4 | ok (46 pts) | fee 5.40: mu*_lim 0.44 | sigma_1m and R_d from sibling CL (OC-1) |
| RTY | 5.0000 | 3.50 | 0.700 | 10.01 | 0.70 | 1.70 | 1.66 | 120.9 | 1.17 | 240.0 | 4 | ok (52 pts) | fee 5.76: mu*_lim 1.15 |  |
| SI | 25.0000 | 4.60 | 0.184 | - | - | - | - | - | - | 48.0 | 4 | - |  | not computed |
| SIL | 5.0000 | 3.20 | 0.640 | - | - | - | - | - | - | 240.0 | 40 | - |  | not computed |
| YM | 5.0000 | 3.50 | 0.700 | 12.14 | 0.70 | 1.70 | 1.62 | 120.9 | 1.02 | 240.0 | 4 | ok (51 pts) | fee 5.76: mu*_lim 1.15 |  |
| ZC | 12.5000 | 5.60 | 0.448 | 1.71 | 0.46 | 1.46 | 0.96 | 120.9 | 3.68 | 96.0 | 4 | ok (45 pts) | fee 7.20: mu*_lim 0.58; S_rt 1.260: mu*_mkt 1.72 |  |
| ZL | 6.0000 | 5.60 | 0.933 | 5.52 | 0.94 | 1.94 | 1.87 | 120.9 | 2.01 | 200.0 | 4 | ok (54 pts) | fee 7.20: mu*_lim 1.20 |  |
| ZM | 10.0000 | 5.60 | 0.560 | 3.15 | 0.57 | 1.57 | 1.12 | 120.9 | 2.08 | 120.0 | 4 | ok (49 pts) | fee 9.20: mu*_lim 0.93 |  |
| ZS | 12.5000 | 5.60 | 0.448 | 3.11 | 0.45 | 1.45 | 0.90 | 120.9 | 1.77 | 96.0 | 4 | ok (46 pts) | fee 15.20: mu*_lim 1.22; S_rt 1.118: mu*_mkt 1.57 |  |
| ZW | 12.5000 | 5.60 | 0.448 | 2.72 | 0.45 | 1.45 | 0.90 | 120.9 | 2.06 | 96.0 | 4 | ok (46 pts) | fee 17.20: mu*_lim 1.38; S_rt 1.100: mu*_mkt 1.55 |  |

### tradeify: Growth 50K (USD 145 one-time)

| code | v USD | F_rt USD | F_rt ticks | sigma_T | mu*_lim | mu*_mkt | mu10K | cost/attempt USD | room | DLL ticks | pos. limit | grid check | sensitivities | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | 5.0000 | 6.20 | 1.240 | 3.09 | 1.26 | 2.26 | 1.96 | 95.8 | 2.90 | 250.0 | 4 | ok (56 pts) |  | non-monotone cached points |
| 6E | 6.2500 | 6.20 | 0.992 | 3.56 | 1.00 | 2.00 | 1.61 | 95.8 | 2.09 | 200.0 | 4 | ok (52 pts) | S_rt 1.200: mu*_mkt 2.20 | non-monotone cached points |
| CL | 10.0000 | 5.98 | 0.598 | 6.30 | 0.59 | 1.59 | 0.97 | 95.8 | 0.82 | 125.0 | 4 | ok (46 pts) |  | non-monotone cached points |
| GC | 10.0000 | 6.20 | 0.620 | 5.29 | 0.61 | 1.61 | 1.01 | 95.8 | 0.91 | 125.0 | 4 | ok (50 pts) |  |  |
| HG | 12.5000 | 6.20 | 0.496 | 3.14 | 0.50 | 1.50 | 0.81 | 95.8 | 1.01 | 100.0 | 4 | ok (44 pts) |  |  |
| M2K | 0.5000 | 1.82 | 3.640 | 10.01 | > 4 | > 4 | > 4 | 95.8 | 11.73 | 2,500.0 | 40 | ok (51 pts) |  | sigma_1m and R_d from sibling RTY (OC-1) |
| M6A | 1.0000 | 1.60 | 1.600 | 1.55 | > 4 | > 4 | > 4 | 95.8 | 28.99 | 1,250.0 | 40 | ok (51 pts) |  | sigma_1m and R_d from sibling 6A (OC-1) |
| M6E | 1.2500 | 1.60 | 1.280 | 1.78 | > 4 | > 4 | > 4 | 95.8 | 20.92 | 1,000.0 | 40 | ok (51 pts) |  | sigma_1m and R_d from sibling 6E (OC-1) |
| MCL | 1.0000 | 2.12 | 2.120 | 6.49 | > 4 | > 4 | > 4 | 95.8 | 8.15 | 1,250.0 | 40 | ok (51 pts) |  |  |
| MGC | 1.0000 | 2.12 | 2.120 | 5.40 | > 4 | > 4 | > 4 | 95.8 | 9.09 | 1,250.0 | 40 | ok (51 pts) |  |  |
| MNQ | 0.5000 | 1.82 | 3.640 | 27.83 | 3.86 | > 4 | > 4 | 95.8 | 4.14 | 2,500.0 | 40 | ok (63 pts) |  | sigma_1m and R_d from sibling NQ (OC-1) |
| MYM | 0.5000 | 1.82 | 3.640 | 12.14 | > 4 | > 4 | > 4 | 95.8 | 10.18 | 2,500.0 | 40 | ok (51 pts) |  | sigma_1m and R_d from sibling YM (OC-1) |
| NG | 10.0000 | 6.20 | 0.620 | 6.28 | 0.61 | 1.61 | 1.00 | 95.8 | 1.27 | 125.0 | 4 | ok (45 pts) |  |  |
| NQ | 5.0000 | 5.76 | 1.152 | 27.83 | 1.05 | 2.05 | 2.22 | 98.4 | 0.41 | 250.0 | 4 | ok (71 pts) |  |  |
| QG | 12.5000 | 4.00 | 0.320 | 1.26 | 0.33 | 1.33 | 0.61 | 95.8 | 5.06 | 100.0 | 4 | ok (44 pts) |  | sigma_1m and R_d from sibling NG (OC-1); non-monotone cached points |
| QM | 12.5000 | 5.40 | 0.432 | 2.52 | 0.43 | 1.43 | 0.75 | 95.8 | 1.64 | 100.0 | 4 | ok (43 pts) |  | sigma_1m and R_d from sibling CL (OC-1) |
| RTY | 5.0000 | 5.76 | 1.152 | 10.01 | 1.13 | 2.13 | 1.92 | 95.8 | 1.17 | 250.0 | 4 | ok (57 pts) |  |  |
| SI | 25.0000 | 6.20 | 0.248 | - | - | - | - | - | - | 50.0 | 4 | - |  | not computed |
| YM | 5.0000 | 5.76 | 1.152 | 12.14 | 1.13 | 2.13 | 1.90 | 95.8 | 1.02 | 250.0 | 4 | ok (56 pts) |  |  |
| ZC | 12.5000 | 7.20 | 0.576 | 1.71 | 0.58 | 1.58 | 0.89 | 95.8 | 3.68 | 100.0 | 4 | ok (47 pts) | S_rt 1.260: mu*_mkt 1.84 | non-monotone cached points |
| ZL | 6.0000 | 7.20 | 1.200 | 5.52 | 1.20 | 2.20 | 1.85 | 95.8 | 2.01 | 208.3 | 4 | ok (53 pts) |  |  |
| ZM | 10.0000 | 9.20 | 0.920 | 3.15 | 0.92 | 1.92 | 1.31 | 95.8 | 2.08 | 125.0 | 4 | ok (50 pts) |  |  |
| ZS | 12.5000 | 15.20 | 1.216 | 3.11 | 1.22 | 2.22 | 1.53 | 95.8 | 1.77 | 100.0 | 4 | ok (53 pts) | S_rt 1.118: mu*_mkt 2.33 |  |
| ZW | 12.5000 | 17.20 | 1.376 | 2.72 | 1.38 | 2.38 | 1.69 | 95.8 | 2.06 | 100.0 | 4 | ok (53 pts) | S_rt 1.100: mu*_mkt 2.48 |  |

### mffu: Builder 50K Default (USD 153 one-time)

| code | v USD | F_rt USD | F_rt ticks | sigma_T | mu*_lim | mu*_mkt | mu10K | cost/attempt USD | room | DLL ticks | pos. limit | grid check | sensitivities | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | 5.0000 | 5.04 | 1.008 | 3.09 | 1.03 | 2.03 | 2.39 | 153.0 | 2.90 | 200.0 | 4 | ok (63 pts) |  |  |
| 6E | 6.2500 | 5.12 | 0.819 | 3.56 | 0.83 | 1.83 | 1.92 | 153.0 | 2.09 | 160.0 | 4 | ok (56 pts) | S_rt 1.200: mu*_mkt 2.03 |  |
| CL | 10.0000 | 4.92 | 0.492 | 6.30 | 0.51 | 1.51 | 1.06 | 153.0 | 0.82 | 100.0 | 4 | ok (50 pts) |  |  |
| GC | 10.0000 | 5.12 | 0.512 | 5.29 | 0.53 | 1.53 | 1.10 | 153.0 | 0.91 | 100.0 | 4 | ok (49 pts) |  |  |
| HG | 12.5000 | 5.12 | 0.410 | 3.14 | 0.42 | 1.42 | 0.91 | 153.0 | 1.01 | 80.0 | 4 | ok (47 pts) |  | restricted_now |
| M2K | 0.5000 | 1.90 | 3.800 | 10.01 | > 4 | > 4 | > 4 | 153.0 | 11.73 | 2,000.0 | 40 | ok (51 pts) |  | sigma_1m and R_d from sibling RTY (OC-1) |
| M6A | 1.0000 | 1.44 | 1.440 | 1.55 | 1.64 | 2.64 | > 4 | 153.0 | 28.99 | 1,000.0 | 40 | ok (64 pts) |  | sigma_1m and R_d from sibling 6A (OC-1) |
| M6E | 1.2500 | 1.44 | 1.152 | 1.78 | 1.31 | 2.31 | > 4 | 153.0 | 20.92 | 800.0 | 40 | ok (62 pts) |  | sigma_1m and R_d from sibling 6E (OC-1) |
| MBT | 0.5000 | 3.50 | 7.000 | 4.92 | > 4 | > 4 | > 4 | 153.0 | 23.67 | 2,000.0 | 4 | ok (51 pts) |  |  |
| MCL | 1.0000 | 1.16 | 1.160 | 6.49 | 1.34 | 2.34 | > 4 | 153.0 | 8.15 | 1,000.0 | 40 | ok (62 pts) |  |  |
| MET | 0.0500 | 1.16 | 23.200 | - | - | - | - | - | - | 20,000.0 | 40 | - |  | not computed |
| MGC | 1.0000 | 2.20 | 2.200 | 5.40 | 2.38 | 3.38 | > 4 | 153.0 | 9.09 | 1,000.0 | 5 | ok (63 pts) |  |  |
| MNQ | 0.5000 | 1.90 | 3.800 | 27.83 | > 4 | > 4 | > 4 | 153.0 | 4.14 | 2,000.0 | 40 | ok (51 pts) |  | sigma_1m and R_d from sibling NQ (OC-1) |
| MYM | 0.5000 | 1.90 | 3.800 | 12.14 | > 4 | > 4 | > 4 | 153.0 | 10.18 | 2,000.0 | 40 | ok (51 pts) |  | sigma_1m and R_d from sibling YM (OC-1) |
| NG | 10.0000 | 5.12 | 0.512 | 6.28 | 0.53 | 1.53 | 1.08 | 153.0 | 1.27 | 100.0 | 4 | ok (50 pts) |  | restricted_now |
| NQ | 5.0000 | 4.68 | 0.936 | 27.83 | 0.98 | 1.98 | 2.32 | 153.0 | 0.41 | 200.0 | 4 | ok (71 pts) |  |  |
| QG | 12.5000 | 2.92 | 0.234 | 1.26 | 0.25 | 1.25 | 0.79 | 153.0 | 5.06 | 80.0 | 4 | ok (44 pts) |  | restricted_now; sigma_1m and R_d from sibling NG (OC-1) |
| QM | 12.5000 | 4.32 | 0.346 | 2.52 | 0.35 | 1.35 | 0.90 | 153.0 | 1.64 | 80.0 | 4 | ok (45 pts) |  | sigma_1m and R_d from sibling CL (OC-1) |
| RTY | 5.0000 | 4.68 | 0.936 | 10.01 | 0.96 | 1.96 | 2.12 | 153.0 | 1.17 | 200.0 | 4 | ok (57 pts) |  |  |
| SI | 25.0000 | 5.12 | 0.205 | - | - | - | - | - | - | 40.0 | 4 | - |  | restricted_now; not computed |
| SIL | 5.0000 | 2.84 | 0.568 | - | - | - | - | - | - | 200.0 | 5 | - |  | not computed |
| YM | 5.0000 | 5.76 | 1.152 | 12.14 | 1.18 | 2.18 | 2.31 | 153.0 | 1.02 | 200.0 | 4 | ok (59 pts) |  |  |
| ZC | 12.5000 | 6.12 | 0.490 | 1.71 | 0.50 | 1.50 | 1.04 | 153.0 | 3.68 | 80.0 | 4 | ok (48 pts) | S_rt 1.260: mu*_mkt 1.76 |  |
| ZL | 6.0000 | 6.12 | 1.020 | 5.52 | 1.03 | 2.03 | 2.15 | 153.0 | 2.01 | 166.7 | 4 | ok (60 pts) |  |  |
| ZM | 10.0000 | 6.12 | 0.612 | 3.15 | 0.62 | 1.62 | 1.30 | 153.0 | 2.08 | 100.0 | 4 | ok (49 pts) |  |  |
| ZS | 12.5000 | 6.12 | 0.490 | 3.11 | 0.50 | 1.50 | 0.99 | 153.0 | 1.77 | 80.0 | 4 | ok (46 pts) | S_rt 1.118: mu*_mkt 1.62 |  |
| ZW | 12.5000 | 6.12 | 0.490 | 2.72 | 0.50 | 1.50 | 1.03 | 153.0 | 2.06 | 80.0 | 4 | ok (48 pts) | S_rt 1.100: mu*_mkt 1.60 |  |

### bulenox: Qualification 50K, Option 1 trailing (USD 175 one-time, 30 days)

| code | v USD | F_rt USD | F_rt ticks | sigma_T | mu*_lim | mu*_mkt | mu10K | cost/attempt USD | room | DLL ticks | pos. limit | grid check | sensitivities | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | 5.0000 | 4.72 | 0.944 | 3.09 | 2.17 | 3.17 | 2.75 | 175.0 | 3.62 | - | 7 | ok (67 pts) | ex-API mu*_lim 2.13 | non-monotone cached points |
| 6E | 6.2500 | 4.72 | 0.755 | 3.56 | 1.67 | 2.67 | 2.21 | 175.0 | 2.61 | - | 7 | ok (63 pts) | ex-API mu*_lim 1.62; S_rt 1.200: mu*_mkt 2.87 | non-monotone cached points |
| CL | 10.0000 | 4.52 | 0.452 | 6.30 | 0.76 | 1.76 | 1.44 | 175.0 | 1.02 | - | 7 | ok (55 pts) | ex-API mu*_lim 0.68 |  |
| GC | 10.0000 | 4.62 | 0.462 | 5.29 | 0.82 | 1.82 | 1.43 | 175.0 | 1.13 | - | 7 | ok (54 pts) | ex-API mu*_lim 0.74 |  |
| HG | 12.5000 | 4.62 | 0.370 | 3.14 | 0.74 | 1.74 | 1.13 | 175.0 | 1.26 | - | 7 | ok (52 pts) | ex-API mu*_lim 0.69 | non-monotone cached points |
| M2K | 0.5000 | 1.22 | 2.440 | 10.01 | > 4 | > 4 | > 4 | 175.0 | 14.66 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 | sigma_1m and R_d from sibling RTY (OC-1) |
| M6A | 1.0000 | 1.00 | 1.000 | 1.55 | > 4 | > 4 | > 4 | 175.0 | 36.23 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 | sigma_1m and R_d from sibling 6A (OC-1) |
| M6E | 1.2500 | 1.00 | 0.800 | 1.78 | > 4 | > 4 | > 4 | 175.0 | 26.14 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 | sigma_1m and R_d from sibling 6E (OC-1) |
| MBT | 0.5000 | 5.52 | 11.040 | 4.92 | > 4 | > 4 | > 4 | 175.0 | 29.59 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 |  |
| MCL | 1.0000 | 1.52 | 1.520 | 6.49 | > 4 | > 4 | > 4 | 175.0 | 10.18 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 |  |
| MET | 0.0500 | 0.92 | 18.400 | - | - | - | - | - | - | - | 70 | - |  | not computed |
| MGC | 1.0000 | 1.52 | 1.520 | 5.40 | > 4 | > 4 | > 4 | 175.0 | 11.36 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 |  |
| MNQ | 0.5000 | 1.22 | 2.440 | 27.83 | > 4 | > 4 | > 4 | 175.0 | 5.17 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 | sigma_1m and R_d from sibling NQ (OC-1) |
| MYM | 0.5000 | 1.22 | 2.440 | 12.14 | > 4 | > 4 | > 4 | 175.0 | 12.72 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 | sigma_1m and R_d from sibling YM (OC-1) |
| NG | 10.0000 | 4.52 | 0.452 | 6.28 | 0.76 | 1.76 | 1.44 | 175.0 | 1.58 | - | 7 | ok (55 pts) | ex-API mu*_lim 0.68 |  |
| NQ | 5.0000 | 4.18 | 0.836 | 27.83 | 1.37 | 2.37 | 3.10 | 175.0 | 0.52 | - | 7 | ok (81 pts) | ex-API mu*_lim 1.14 |  |
| QG | 12.5000 | 2.52 | 0.202 | 1.26 | 0.69 | 1.69 | 0.93 | 175.0 | 6.33 | - | 7 | ok (47 pts) | ex-API mu*_lim 0.68 | sigma_1m and R_d from sibling NG (OC-1); non-monotone cached points |
| QM | 12.5000 | 3.92 | 0.314 | 2.52 | 0.72 | 1.72 | 1.06 | 175.0 | 2.05 | - | 7 | ok (50 pts) | ex-API mu*_lim 0.69 | sigma_1m and R_d from sibling CL (OC-1); non-monotone cached points |
| RTY | 5.0000 | 4.18 | 0.836 | 10.01 | 1.59 | 2.59 | 2.76 | 175.0 | 1.47 | - | 7 | ok (72 pts) | ex-API mu*_lim 1.44 |  |
| SI | 25.0000 | 4.62 | 0.185 | - | - | - | - | - | - | - | 7 | - |  | not computed |
| YM | 5.0000 | 4.18 | 0.836 | 12.14 | 1.46 | 2.46 | 2.80 | 175.0 | 1.27 | - | 7 | ok (68 pts) | ex-API mu*_lim 1.30 |  |
| ZL | 6.0000 | 5.72 | 0.953 | 5.52 | 1.78 | 2.78 | 2.50 | 175.0 | 2.51 | - | 7 | ok (65 pts) | ex-API mu*_lim 1.70 | non-monotone cached points |
| ZM | 10.0000 | 5.72 | 0.572 | 3.15 | 1.08 | 2.08 | 1.50 | 175.0 | 2.60 | - | 7 | ok (54 pts) | ex-API mu*_lim 1.04 | non-monotone cached points |
| ZS | 12.5000 | 5.72 | 0.458 | 3.11 | 0.83 | 1.83 | 1.21 | 175.0 | 2.21 | - | 7 | ok (52 pts) | ex-API mu*_lim 0.78; S_rt 1.118: mu*_mkt 1.94 | non-monotone cached points |
| ZW | 12.5000 | 5.72 | 0.458 | 2.72 | 0.85 | 1.85 | 1.21 | 175.0 | 2.58 | - | 7 | ok (51 pts) | ex-API mu*_lim 0.81; S_rt 1.100: mu*_mkt 1.95 | non-monotone cached points |
