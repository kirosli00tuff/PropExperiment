# Stage E.2a Task 9, phase 2: the vehicle per exposure

Generated 2026-09-25 02:43 PDT by screening/vehicles_choice.py (VehicleCoder-OpusXHigh). Rule: docs/STAGE_E_DESIGN.md D2 read as R1-R12 of reports/stage_e2a_vehicle_rule_readings.md. Full data: reports/stage_e2a_vehicles.json. Nothing here is chosen by judgment: each result follows from R7-R12 and the numbers shown; a case the readings do not settle is listed as a question.

Inputs: r_c, q_c, rho_c from reports/stage_e2a_vehicle_sizes.json (phase 1; re-derived from the parquets with the current code: 0 differences); costs from the frozen D8 table reports/stage_e2a_costs.json (sha256 f4360bb77272d0335485a9e01c0f6fc6ab99c47d52e640d95f9cd0397296df14). reports/stage_e2a_vehicle_sizes.json lists reports/stage_e2a_costs.json with sha256 02b3838bdc510c56483646bf12a012a5927f4dab7fb350cee21a2bea9fc38b74: the provisional table, read in phase 1 only to cross-check the vendor price factor (q_c does not depend on costs). Phase 2 uses only the frozen table, sha256 f4360bb77272d0335485a9e01c0f6fc6ab99c47d52e640d95f9cd0397296df14.

Lead answers applied: Q-1 accepted (02:42 PDT): SI and HG keep the D9.5 cap of 1; D9.11's 0 is discretionary and R5 lists only SIL and MHG; Q-2 accepted (02:42 PDT): vendor-degraded trade dates as BarsCoder lists them.

R8: cost per dollar of risk = (commission_c + 2 x one-side slippage_c) / r_c, the one-side slippage being the minute-weighted mean over the day session [O_X, C_X) of D8's per-side cost at q_c, (buy side + sell side) / 2 per 30-minute bucket (s_b plus the mean of the two sides' depth terms). R9: candidates rho_c <= 2.0 less R7 (M6E, M6A); preferred rho_c >= 0.5; lowest R8 cost among the preferred; an exact tie to the higher D1 ADV; SIL (MHG) is the vehicle whenever it is a candidate. R10: candidates but none preferred: the cheapest candidate at its cap, 'undersized'. R11: no candidate: not traded in Stage E. R12: eps_X = floor($85.00 / (q_c x tick value)).

## Result per exposure

| Exposure | Cluster | Admissible | Candidates | Preferred | Status | Vehicle | q_c | eps_X (net ticks) |
|---|---|---|---|---|---|---|---|---|
| Nasdaq-100 | K1 | MNQ, NQ | MNQ | MNQ | chosen | MNQ | 1 | 170 |
| Russell 2000 | K1 | RTY, M2K | M2K | M2K | chosen | M2K | 3 | 56 |
| Dow | K1 | MYM, YM | MYM | MYM | chosen | MYM | 3 | 56 |
| 2-year | K2 | ZT | ZT | none | undersized | ZT | 1 | 10 |
| 5-year | K2 | ZF | ZF | none | undersized | ZF | 1 | 10 |
| 10-year | K2 | ZN | ZN | ZN | chosen | ZN | 1 | 5 |
| Ultra 10-year | K2 | TN | TN | TN | chosen | TN | 1 | 5 |
| Bond | K2 | ZB | ZB | ZB | chosen | ZB | 1 | 2 |
| Ultra bond | K2 | UB | UB | UB | chosen | UB | 1 | 2 |
| EUR | K3 | 6E, M6E, E7 | 6E, E7 | 6E | chosen | 6E | 1 | 13 |
| AUD | K3 | 6A, M6A | 6A | 6A | chosen | 6A | 1 | 17 |
| GBP | K3 | 6B, M6B | 6B, M6B | 6B, M6B | chosen | 6B | 1 | 13 |
| CAD | K3 | 6C | 6C | none | undersized | 6C | 1 | 17 |
| JPY | K3 | 6J | 6J | 6J | chosen | 6J | 1 | 13 |
| CHF | K3 | 6S | 6S | 6S | chosen | 6S | 1 | 13 |
| NZD | K3 | 6N | 6N | none | undersized | 6N | 1 | 17 |
| WTI crude | K4 | CL, MCL, QM | MCL, QM | MCL, QM | chosen | MCL | 4 | 21 |
| Henry Hub gas | K4 | NG, MNG, QG | NG, MNG, QG | NG, MNG | chosen | NG | 1 | 8 |
| RBOB | K4 | RB | none | none | no candidate: not traded in Stage E | - | - | - |
| ULSD | K4 | HO | none | none | no candidate: not traded in Stage E | - | - | - |
| gold | K5 | MGC, GC | MGC | MGC | chosen | MGC | 1 | 85 |
| silver | K5 | SIL, SI | none | none | no candidate: not traded in Stage E | - | - | - |
| copper | K5 | HG, MHG | MHG | MHG | chosen | MHG | 2 | 34 |
| corn | K6 | ZC | ZC | none | undersized | ZC | 1 | 6 |
| wheat | K6 | ZW | ZW | ZW | chosen | ZW | 1 | 6 |
| soybeans | K6 | ZS | ZS | ZS | chosen | ZS | 1 | 6 |
| soybean meal | K6 | ZM | ZM | ZM | chosen | ZM | 1 | 8 |
| soybean oil | K6 | ZL | ZL | ZL | chosen | ZL | 1 | 14 |
| lean hogs | K6 | HE | HE | HE | chosen | HE | 1 | 8 |
| live cattle | K6 | LE | LE | LE | chosen | LE | 1 | 8 |
| bitcoin | K7 | MBT | MBT | none | undersized | MBT | 1 | 170 |

Counts: chosen 22; undersized 6; no candidate: not traded in Stage E 3.

## Per contract (r_c, q_c, rho_c from phase 1; costs at q_c)

| Contract | Exposure | r_c (USD) | q_c | rho_c | Commission RT (USD) | One-side (ticks) | One-side (USD) | Round turn (USD) | Cost per $ of risk | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| MNQ | Nasdaq-100 | 363.46 | 1 | 1.0077 | 1.22 | 0.8394 | 0.4197 | 2.0594 | 0.005666 |  |
| NQ | Nasdaq-100 | 3613.08 | 1 | 10.0174 | 3.78 | 1.1772 | 5.8861 | 15.5522 | 0.004304 |  |
| RTY | Russell 2000 | 1060.72 | 1 | 2.9409 | 3.78 | 0.8016 | 4.0079 | 11.7959 | 0.011121 |  |
| M2K | Russell 2000 | 106.13 | 3 | 0.8828 | 1.22 | 0.7570 | 0.3785 | 1.9770 | 0.018627 |  |
| MYM | Dow | 131.15 | 3 | 1.0908 | 1.22 | 0.7713 | 0.3856 | 1.9913 | 0.015183 |  |
| YM | Dow | 1312.27 | 1 | 3.6383 | 3.78 | 1.0337 | 5.1684 | 14.1169 | 0.010758 |  |
| ZT | 2-year | 112.68 | 1 | 0.3124 | 2.32 | 0.5021 | 3.9229 | 10.1659 | 0.090219 |  |
| ZF | 5-year | 135.54 | 1 | 0.3758 | 2.32 | 0.5005 | 3.9101 | 10.1401 | 0.074810 |  |
| ZN | 10-year | 204.93 | 1 | 0.5682 | 2.62 | 0.5001 | 7.8134 | 18.2468 | 0.089040 |  |
| TN | Ultra 10-year | 259.94 | 1 | 0.7207 | 2.62 | 0.5032 | 7.8619 | 18.3439 | 0.070569 |  |
| ZB | Bond | 402.10 | 1 | 1.1148 | 2.76 | 0.5005 | 15.6407 | 34.0413 | 0.084659 |  |
| UB | Ultra bond | 501.42 | 1 | 1.3902 | 2.92 | 0.5024 | 15.7008 | 34.3216 | 0.068449 |  |
| 6E | EUR | 319.45 | 1 | 0.8857 | 4.22 | 0.6293 | 3.9332 | 12.0864 | 0.037834 |  |
| M6E | EUR | 32.03 | 10 | 0.8882 | 1.00 | 0.5608 | 0.7010 | 2.4020 | 0.074982 | R7 |
| E7 | EUR | 160.73 | 1 | 0.4456 | 2.72 | 0.6371 | 3.9816 | 10.6833 | 0.066467 |  |
| 6A | AUD | 183.65 | 1 | 0.5092 | 4.22 | 0.6739 | 3.3697 | 10.9594 | 0.059675 |  |
| M6A | AUD | 18.42 | 10 | 0.5106 | 1.00 | 0.5854 | 0.5854 | 2.1708 | 0.117872 | R7 |
| 6B | GBP | 186.22 | 1 | 0.5163 | 4.22 | 0.6194 | 3.8711 | 11.9622 | 0.064237 |  |
| M6B | GBP | 18.71 | 10 | 0.5188 | 1.00 | 0.8733 | 0.5458 | 2.0916 | 0.111770 |  |
| 6C | CAD | 120.29 | 1 | 0.3335 | 4.22 | 0.5918 | 2.9590 | 10.1381 | 0.084280 |  |
| 6J | JPY | 204.82 | 1 | 0.5679 | 4.22 | 0.6066 | 3.7914 | 11.8028 | 0.057625 |  |
| 6S | CHF | 410.75 | 1 | 1.1388 | 4.22 | 0.9860 | 6.1622 | 16.5444 | 0.040278 |  |
| 6N | NZD | 156.48 | 1 | 0.4339 | 4.22 | 0.7041 | 3.5205 | 11.2609 | 0.071962 |  |
| CL | WTI crude | 918.79 | 1 | 2.5474 | 4.02 | 0.6630 | 6.6303 | 17.2806 | 0.018808 |  |
| MCL | WTI crude | 91.57 | 4 | 1.0155 | 1.72 | 0.7235 | 0.7235 | 3.1670 | 0.034585 |  |
| QM | WTI crude | 457.22 | 1 | 1.2677 | 3.42 | 0.6628 | 8.2851 | 19.9903 | 0.043721 |  |
| NG | Henry Hub gas | 639.31 | 1 | 1.7725 | 4.22 | 0.6250 | 6.2501 | 16.7202 | 0.026154 |  |
| MNG | Henry Hub gas | 65.31 | 6 | 1.0864 | 1.92 | 1.7148 | 1.7148 | 5.3496 | 0.081912 |  |
| QG | Henry Hub gas | 159.16 | 1 | 0.4413 | 2.02 | 0.6099 | 7.6238 | 17.2677 | 0.108492 |  |
| RB | RBOB | 1012.79 | 1 | 2.8080 | 4.02 | 2.2788 | 9.5708 | 23.1615 | 0.022869 |  |
| HO | ULSD | 1441.40 | 1 | 3.9963 | 4.02 | 4.4349 | 18.6266 | 41.2731 | 0.028634 |  |
| MGC | gold | 258.59 | 1 | 0.7170 | 1.92 | 1.0780 | 1.0780 | 4.0760 | 0.015762 |  |
| GC | gold | 2586.97 | 1 | 7.1725 | 4.32 | 1.9521 | 19.5211 | 43.3623 | 0.016762 |  |
| SIL | silver | 931.05 | 1 | 2.5814 | 2.72 | 1.1163 | 5.5816 | 13.8832 | 0.014911 |  |
| SI | silver | 4653.97 | 1 | 12.9033 | 4.32 | 1.6821 | 42.0526 | 88.4252 | 0.019000 |  |
| HG | copper | 1101.29 | 1 | 3.0534 | 4.32 | 1.1172 | 13.9648 | 32.2496 | 0.029283 |  |
| MHG | copper | 110.22 | 2 | 0.6112 | 1.92 | 1.0755 | 1.3444 | 4.6089 | 0.041817 |  |
| ZC | corn | 158.16 | 1 | 0.4385 | 5.28 | 0.5015 | 6.2684 | 17.8169 | 0.112648 |  |
| ZW | wheat | 234.75 | 1 | 0.6508 | 5.28 | 0.5286 | 6.6071 | 18.4941 | 0.078783 |  |
| ZS | soybeans | 304.39 | 1 | 0.8439 | 5.28 | 0.5229 | 6.5365 | 18.3529 | 0.060294 |  |
| ZM | soybean meal | 212.64 | 1 | 0.5895 | 5.28 | 0.5399 | 5.3991 | 16.0782 | 0.075613 |  |
| ZL | soybean oil | 304.83 | 1 | 0.8452 | 5.28 | 0.6461 | 3.8768 | 13.0335 | 0.042757 |  |
| HE | lean hogs | 322.96 | 1 | 0.8954 | 5.22 | 0.6690 | 6.6895 | 18.5991 | 0.057589 |  |
| LE | live cattle | 707.16 | 1 | 1.9606 | 5.22 | 0.9356 | 9.3563 | 23.9325 | 0.033843 |  |
| MBT | bitcoin | 120.61 | 1 | 0.3344 | 2.82 | 1.6030 | 0.8015 | 4.4230 | 0.036671 |  |

## Arithmetic per exposure

### Nasdaq-100 (K1): chosen: MNQ

- MNQ (ADV 2,363,465): r_c = $363.4614; R*/r_c = 360.68 / 363.4614 = 0.9923, round-half-up 1; q_c = min(cap 10 (D9.5), max(1, 1)) = 1; rho_c = 1 x 363.4614 / 360.68 = 1.0077: 0.5 <= rho_c <= 2.0: candidate, preferred
- MNQ cost: (commission $1.22 + 2 x one-side $0.419719 [0.839437 ticks x $0.5]) / r_c $363.4614 = $2.059437 / $363.4614 = 0.00566618 per dollar of risk
- NQ (ADV 593,595): r_c = $3613.0769; R*/r_c = 360.68 / 3613.0769 = 0.0998, round-half-up 0; q_c = min(cap 1 (D9.5), max(1, 0)) = 1; rho_c = 1 x 3613.0769 / 360.68 = 10.0174: rho_c > 2.0: not a candidate
- NQ cost: (commission $3.78 + 2 x one-side $5.886088 [1.177218 ticks x $5.0]) / r_c $3613.0769 = $15.552175 / $3613.0769 = 0.00430441 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['MNQ']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['MNQ']
- Decides: the only preferred candidate: MNQ (cost per dollar of risk 0.00566618)
- eps_X = floor(85.00 / (1 x $0.5)) = floor(170.0000) = 170 net ticks per contract per day (R12)

### Russell 2000 (K1): chosen: M2K

- RTY (ADV 209,871): r_c = $1060.7168; R*/r_c = 360.68 / 1060.7168 = 0.3400, round-half-up 0; q_c = min(cap 1 (D9.5), max(1, 0)) = 1; rho_c = 1 x 1060.7168 / 360.68 = 2.9409: rho_c > 2.0: not a candidate
- RTY cost: (commission $3.78 + 2 x one-side $4.007939 [0.801588 ticks x $5.0]) / r_c $1060.7168 = $11.795878 / $1060.7168 = 0.01112067 per dollar of risk
- M2K (ADV 115,832): r_c = $106.1346; R*/r_c = 360.68 / 106.1346 = 3.3983, round-half-up 3; q_c = min(cap 10 (D9.5), max(1, 3)) = 3; rho_c = 3 x 106.1346 / 360.68 = 0.8828: 0.5 <= rho_c <= 2.0: candidate, preferred
- M2K cost: (commission $1.22 + 2 x one-side $0.378497 [0.756995 ticks x $0.5]) / r_c $106.1346 = $1.976995 / $106.1346 = 0.01862724 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['M2K']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['M2K']
- Decides: the only preferred candidate: M2K (cost per dollar of risk 0.01862724)
- eps_X = floor(85.00 / (3 x $0.5)) = floor(56.6667) = 56 net ticks per contract per day (R12)

### Dow (K1): chosen: MYM

- MYM (ADV 152,686): r_c = $131.1486; R*/r_c = 360.68 / 131.1486 = 2.7502, round-half-up 3; q_c = min(cap 10 (D9.5), max(1, 3)) = 3; rho_c = 3 x 131.1486 / 360.68 = 1.0908: 0.5 <= rho_c <= 2.0: candidate, preferred
- MYM cost: (commission $1.22 + 2 x one-side $0.385631 [0.771262 ticks x $0.5]) / r_c $131.1486 = $1.991262 / $131.1486 = 0.01518325 per dollar of risk
- YM (ADV 108,142): r_c = $1312.2727; R*/r_c = 360.68 / 1312.2727 = 0.2749, round-half-up 0; q_c = min(cap 1 (D9.5), max(1, 0)) = 1; rho_c = 1 x 1312.2727 / 360.68 = 3.6383: rho_c > 2.0: not a candidate
- YM cost: (commission $3.78 + 2 x one-side $5.168428 [1.033686 ticks x $5.0]) / r_c $1312.2727 = $14.116856 / $1312.2727 = 0.01075756 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['MYM']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['MYM']
- Decides: the only preferred candidate: MYM (cost per dollar of risk 0.01518325)
- eps_X = floor(85.00 / (3 x $0.5)) = floor(56.6667) = 56 net ticks per contract per day (R12)

### 2-year (K2): undersized: ZT

- ZT (ADV 1,325,938): r_c = $112.6803; R*/r_c = 360.68 / 112.6803 = 3.2009, round-half-up 3; q_c = min(cap 1 (D9.5), max(1, 3)) = 1; rho_c = 1 x 112.6803 / 360.68 = 0.3124: rho_c < 0.5: candidate, not preferred
- ZT cost: (commission $2.32 + 2 x one-side $3.922950 [0.502138 ticks x $7.8125]) / r_c $112.6803 = $10.165900 / $112.6803 = 0.09021897 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['ZT']; excluded by R7: none
- Preferred (rho_c >= 0.5): none
- Decides: R10: no candidate has rho_c >= 0.5; the only candidate: ZT (cost per dollar of risk 0.09021897)
- eps_X = floor(85.00 / (1 x $7.8125)) = floor(10.8800) = 10 net ticks per contract per day (R12)
- R10: undersized, traded at the cap; its funnel-derived epsilon then governs (D2, D3)

### 5-year (K2): undersized: ZF

- ZF (ADV 1,941,530): r_c = $135.5441; R*/r_c = 360.68 / 135.5441 = 2.6610, round-half-up 3; q_c = min(cap 1 (D9.5), max(1, 3)) = 1; rho_c = 1 x 135.5441 / 360.68 = 0.3758: rho_c < 0.5: candidate, not preferred
- ZF cost: (commission $2.32 + 2 x one-side $3.910051 [0.500487 ticks x $7.8125]) / r_c $135.5441 = $10.140102 / $135.5441 = 0.07481033 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['ZF']; excluded by R7: none
- Preferred (rho_c >= 0.5): none
- Decides: R10: no candidate has rho_c >= 0.5; the only candidate: ZF (cost per dollar of risk 0.07481033)
- eps_X = floor(85.00 / (1 x $7.8125)) = floor(10.8800) = 10 net ticks per contract per day (R12)
- R10: undersized, traded at the cap; its funnel-derived epsilon then governs (D2, D3)

### 10-year (K2): chosen: ZN

- ZN (ADV 2,589,058): r_c = $204.9279; R*/r_c = 360.68 / 204.9279 = 1.7600, round-half-up 2; q_c = min(cap 1 (D9.5), max(1, 2)) = 1; rho_c = 1 x 204.9279 / 360.68 = 0.5682: 0.5 <= rho_c <= 2.0: candidate, preferred
- ZN cost: (commission $2.62 + 2 x one-side $7.813399 [0.500058 ticks x $15.625]) / r_c $204.9279 = $18.246797 / $204.9279 = 0.08904009 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['ZN']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['ZN']
- Decides: the only preferred candidate: ZN (cost per dollar of risk 0.08904009)
- eps_X = floor(85.00 / (1 x $15.625)) = floor(5.4400) = 5 net ticks per contract per day (R12)

### Ultra 10-year (K2): chosen: TN

- TN (ADV 819,357): r_c = $259.9432; R*/r_c = 360.68 / 259.9432 = 1.3875, round-half-up 1; q_c = min(cap 1 (D9.5), max(1, 1)) = 1; rho_c = 1 x 259.9432 / 360.68 = 0.7207: 0.5 <= rho_c <= 2.0: candidate, preferred
- TN cost: (commission $2.62 + 2 x one-side $7.861940 [0.503164 ticks x $15.625]) / r_c $259.9432 = $18.343880 / $259.9432 = 0.07056881 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['TN']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['TN']
- Decides: the only preferred candidate: TN (cost per dollar of risk 0.07056881)
- eps_X = floor(85.00 / (1 x $15.625)) = floor(5.4400) = 5 net ticks per contract per day (R12)

### Bond (K2): chosen: ZB

- ZB (ADV 609,604): r_c = $402.0979; R*/r_c = 360.68 / 402.0979 = 0.8970, round-half-up 1; q_c = min(cap 1 (D9.5), max(1, 1)) = 1; rho_c = 1 x 402.0979 / 360.68 = 1.1148: 0.5 <= rho_c <= 2.0: candidate, preferred
- ZB cost: (commission $2.76 + 2 x one-side $15.640659 [0.500501 ticks x $31.25]) / r_c $402.0979 = $34.041318 / $402.0979 = 0.08465928 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['ZB']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['ZB']
- Decides: the only preferred candidate: ZB (cost per dollar of risk 0.08465928)
- eps_X = floor(85.00 / (1 x $31.25)) = floor(2.7200) = 2 net ticks per contract per day (R12)

### Ultra bond (K2): chosen: UB

- UB (ADV 505,131): r_c = $501.4205; R*/r_c = 360.68 / 501.4205 = 0.7193, round-half-up 1; q_c = min(cap 1 (D9.5), max(1, 1)) = 1; rho_c = 1 x 501.4205 / 360.68 = 1.3902: 0.5 <= rho_c <= 2.0: candidate, preferred
- UB cost: (commission $2.92 + 2 x one-side $15.700819 [0.502426 ticks x $31.25]) / r_c $501.4205 = $34.321639 / $501.4205 = 0.06844882 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['UB']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['UB']
- Decides: the only preferred candidate: UB (cost per dollar of risk 0.06844882)
- eps_X = floor(85.00 / (1 x $31.25)) = floor(2.7200) = 2 net ticks per contract per day (R12)

### EUR (K3): chosen: 6E

- 6E (ADV 216,466): r_c = $319.4539; R*/r_c = 360.68 / 319.4539 = 1.1291, round-half-up 1; q_c = min(cap 1 (D9.5), max(1, 1)) = 1; rho_c = 1 x 319.4539 / 360.68 = 0.8857: 0.5 <= rho_c <= 2.0: candidate, preferred
- 6E cost: (commission $4.22 + 2 x one-side $3.933184 [0.629309 ticks x $6.25]) / r_c $319.4539 = $12.086367 / $319.4539 = 0.03783446 per dollar of risk
- M6E (ADV 24,552): r_c = $32.0350; R*/r_c = 360.68 / 32.0350 = 11.2589, round-half-up 11; q_c = min(cap 10 (D9.5), max(1, 11)) = 10; rho_c = 10 x 32.0350 / 360.68 = 0.8882: R7 (U7): not a candidate
- M6E cost: (commission $1.00 + 2 x one-side $0.701023 [0.560818 ticks x $1.25]) / r_c $32.0350 = $2.402045 / $32.0350 = 0.07498194 per dollar of risk
- E7 (ADV 4,018): r_c = $160.7295; R*/r_c = 360.68 / 160.7295 = 2.2440, round-half-up 2; q_c = min(cap 1 (D9.5), max(1, 2)) = 1; rho_c = 1 x 160.7295 / 360.68 = 0.4456: rho_c < 0.5: candidate, not preferred
- E7 cost: (commission $2.72 + 2 x one-side $3.981629 [0.637061 ticks x $6.25]) / r_c $160.7295 = $10.683257 / $160.7295 = 0.06646730 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['6E', 'E7']; excluded by R7: ['M6E']
- Preferred (rho_c >= 0.5): ['6E']
- Decides: the only preferred candidate: 6E (cost per dollar of risk 0.03783446)
- eps_X = floor(85.00 / (1 x $6.25)) = floor(13.6000) = 13 net ticks per contract per day (R12)

### AUD (K3): chosen: 6A

- 6A (ADV 119,206): r_c = $183.6519; R*/r_c = 360.68 / 183.6519 = 1.9639, round-half-up 2; q_c = min(cap 1 (D9.5), max(1, 2)) = 1; rho_c = 1 x 183.6519 / 360.68 = 0.5092: 0.5 <= rho_c <= 2.0: candidate, preferred
- 6A cost: (commission $4.22 + 2 x one-side $3.369677 [0.673935 ticks x $5.0]) / r_c $183.6519 = $10.959353 / $183.6519 = 0.05967461 per dollar of risk
- M6A (ADV 7,765): r_c = $18.4164; R*/r_c = 360.68 / 18.4164 = 19.5847, round-half-up 20; q_c = min(cap 10 (D9.5), max(1, 20)) = 10; rho_c = 10 x 18.4164 / 360.68 = 0.5106: R7 (U7): not a candidate
- M6A cost: (commission $1.00 + 2 x one-side $0.585391 [0.585391 ticks x $1.0]) / r_c $18.4164 = $2.170781 / $18.4164 = 0.11787229 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['6A']; excluded by R7: ['M6A']
- Preferred (rho_c >= 0.5): ['6A']
- Decides: the only preferred candidate: 6A (cost per dollar of risk 0.05967461)
- eps_X = floor(85.00 / (1 x $5.0)) = floor(17.0000) = 17 net ticks per contract per day (R12)

### GBP (K3): chosen: 6B

- 6B (ADV 103,657): r_c = $186.2201; R*/r_c = 360.68 / 186.2201 = 1.9368, round-half-up 2; q_c = min(cap 1 (D9.5), max(1, 2)) = 1; rho_c = 1 x 186.2201 / 360.68 = 0.5163: 0.5 <= rho_c <= 2.0: candidate, preferred
- 6B cost: (commission $4.22 + 2 x one-side $3.871100 [0.619376 ticks x $6.25]) / r_c $186.2201 = $11.962201 / $186.2201 = 0.06423688 per dollar of risk
- M6B (ADV 4,290): r_c = $18.7137; R*/r_c = 360.68 / 18.7137 = 19.2735, round-half-up 19; q_c = min(cap 10 (D9.5), max(1, 19)) = 10; rho_c = 10 x 18.7137 / 360.68 = 0.5188: 0.5 <= rho_c <= 2.0: candidate, preferred
- M6B cost: (commission $1.00 + 2 x one-side $0.545821 [0.873313 ticks x $0.625]) / r_c $18.7137 = $2.091642 / $18.7137 = 0.11177039 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['6B', 'M6B']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['6B', 'M6B']
- Decides: lowest cost per dollar of risk: 6B 0.06423688 < M6B 0.11177039
- eps_X = floor(85.00 / (1 x $6.25)) = floor(13.6000) = 13 net ticks per contract per day (R12)

### CAD (K3): undersized: 6C

- 6C (ADV 81,946): r_c = $120.2901; R*/r_c = 360.68 / 120.2901 = 2.9984, round-half-up 3; q_c = min(cap 1 (D9.5), max(1, 3)) = 1; rho_c = 1 x 120.2901 / 360.68 = 0.3335: rho_c < 0.5: candidate, not preferred
- 6C cost: (commission $4.22 + 2 x one-side $2.959031 [0.591806 ticks x $5.0]) / r_c $120.2901 = $10.138063 / $120.2901 = 0.08428011 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['6C']; excluded by R7: none
- Preferred (rho_c >= 0.5): none
- Decides: R10: no candidate has rho_c >= 0.5; the only candidate: 6C (cost per dollar of risk 0.08428011)
- eps_X = floor(85.00 / (1 x $5.0)) = floor(17.0000) = 17 net ticks per contract per day (R12)
- R10: undersized, traded at the cap; its funnel-derived epsilon then governs (D2, D3)

### JPY (K3): chosen: 6J

- 6J (ADV 180,897): r_c = $204.8208; R*/r_c = 360.68 / 204.8208 = 1.7610, round-half-up 2; q_c = min(cap 1 (D9.5), max(1, 2)) = 1; rho_c = 1 x 204.8208 / 360.68 = 0.5679: 0.5 <= rho_c <= 2.0: candidate, preferred
- 6J cost: (commission $4.22 + 2 x one-side $3.791421 [0.606627 ticks x $6.25]) / r_c $204.8208 = $11.802841 / $204.8208 = 0.05762520 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['6J']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['6J']
- Decides: the only preferred candidate: 6J (cost per dollar of risk 0.05762520)
- eps_X = floor(85.00 / (1 x $6.25)) = floor(13.6000) = 13 net ticks per contract per day (R12)

### CHF (K3): chosen: 6S

- 6S (ADV 30,520): r_c = $410.7509; R*/r_c = 360.68 / 410.7509 = 0.8781, round-half-up 1; q_c = min(cap 1 (D9.5), max(1, 1)) = 1; rho_c = 1 x 410.7509 / 360.68 = 1.1388: 0.5 <= rho_c <= 2.0: candidate, preferred
- 6S cost: (commission $4.22 + 2 x one-side $6.162201 [0.985952 ticks x $6.25]) / r_c $410.7509 = $16.544402 / $410.7509 = 0.04027844 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['6S']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['6S']
- Decides: the only preferred candidate: 6S (cost per dollar of risk 0.04027844)
- eps_X = floor(85.00 / (1 x $6.25)) = floor(13.6000) = 13 net ticks per contract per day (R12)

### NZD (K3): undersized: 6N

- 6N (ADV 40,801): r_c = $156.4846; R*/r_c = 360.68 / 156.4846 = 2.3049, round-half-up 2; q_c = min(cap 1 (D9.5), max(1, 2)) = 1; rho_c = 1 x 156.4846 / 360.68 = 0.4339: rho_c < 0.5: candidate, not preferred
- 6N cost: (commission $4.22 + 2 x one-side $3.520466 [0.704093 ticks x $5.0]) / r_c $156.4846 = $11.260931 / $156.4846 = 0.07196189 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['6N']; excluded by R7: none
- Preferred (rho_c >= 0.5): none
- Decides: R10: no candidate has rho_c >= 0.5; the only candidate: 6N (cost per dollar of risk 0.07196189)
- eps_X = floor(85.00 / (1 x $5.0)) = floor(17.0000) = 17 net ticks per contract per day (R12)
- R10: undersized, traded at the cap; its funnel-derived epsilon then governs (D2, D3)

### WTI crude (K4): chosen: MCL

- CL (ADV 1,079,857): r_c = $918.7891; R*/r_c = 360.68 / 918.7891 = 0.3926, round-half-up 0; q_c = min(cap 1 (D9.5), max(1, 0)) = 1; rho_c = 1 x 918.7891 / 360.68 = 2.5474: rho_c > 2.0: not a candidate
- CL cost: (commission $4.02 + 2 x one-side $6.630279 [0.663028 ticks x $10.0]) / r_c $918.7891 = $17.280559 / $918.7891 = 0.01880797 per dollar of risk
- MCL (ADV 252,100): r_c = $91.5698; R*/r_c = 360.68 / 91.5698 = 3.9389, round-half-up 4; q_c = min(cap 10 (D9.5), max(1, 4)) = 4; rho_c = 4 x 91.5698 / 360.68 = 1.0155: 0.5 <= rho_c <= 2.0: candidate, preferred
- MCL cost: (commission $1.72 + 2 x one-side $0.723475 [0.723475 ticks x $1.0]) / r_c $91.5698 = $3.166950 / $91.5698 = 0.03458511 per dollar of risk
- QM (ADV 9,446): r_c = $457.2190; R*/r_c = 360.68 / 457.2190 = 0.7889, round-half-up 1; q_c = min(cap 1 (D9.5), max(1, 1)) = 1; rho_c = 1 x 457.2190 / 360.68 = 1.2677: 0.5 <= rho_c <= 2.0: candidate, preferred
- QM cost: (commission $3.42 + 2 x one-side $8.285139 [0.662811 ticks x $12.5]) / r_c $457.2190 = $19.990278 / $457.2190 = 0.04372145 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['MCL', 'QM']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['MCL', 'QM']
- Decides: lowest cost per dollar of risk: MCL 0.03458511 < QM 0.04372145
- eps_X = floor(85.00 / (4 x $1.0)) = floor(21.2500) = 21 net ticks per contract per day (R12)

### Henry Hub gas (K4): chosen: NG

- NG (ADV 521,792): r_c = $639.3050; R*/r_c = 360.68 / 639.3050 = 0.5642, round-half-up 1; q_c = min(cap 1 (D9.5), max(1, 1)) = 1; rho_c = 1 x 639.3050 / 360.68 = 1.7725: 0.5 <= rho_c <= 2.0: candidate, preferred
- NG cost: (commission $4.22 + 2 x one-side $6.250116 [0.625012 ticks x $10.0]) / r_c $639.3050 = $16.720232 / $639.3050 = 0.02615376 per dollar of risk
- MNG (ADV 14,942): r_c = $65.3092; R*/r_c = 360.68 / 65.3092 = 5.5227, round-half-up 6; q_c = min(cap 10 (D9.5), max(1, 6)) = 6; rho_c = 6 x 65.3092 / 360.68 = 1.0864: 0.5 <= rho_c <= 2.0: candidate, preferred
- MNG cost: (commission $1.92 + 2 x one-side $1.714797 [1.714797 ticks x $1.0]) / r_c $65.3092 = $5.349595 / $65.3092 = 0.08191186 per dollar of risk
- QG (ADV 4,060): r_c = $159.1603; R*/r_c = 360.68 / 159.1603 = 2.2661, round-half-up 2; q_c = min(cap 1 (D9.5), max(1, 2)) = 1; rho_c = 1 x 159.1603 / 360.68 = 0.4413: rho_c < 0.5: candidate, not preferred
- QG cost: (commission $2.02 + 2 x one-side $7.623844 [0.609908 ticks x $12.5]) / r_c $159.1603 = $17.267688 / $159.1603 = 0.10849243 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['NG', 'MNG', 'QG']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['NG', 'MNG']
- Decides: lowest cost per dollar of risk: NG 0.02615376 < MNG 0.08191186
- eps_X = floor(85.00 / (1 x $10.0)) = floor(8.5000) = 8 net ticks per contract per day (R12)

### RBOB (K4): no candidate: not traded in Stage E

- RB (ADV 206,850): r_c = $1012.7925; R*/r_c = 360.68 / 1012.7925 = 0.3561, round-half-up 0; q_c = min(cap 1 (D9.5), max(1, 0)) = 1; rho_c = 1 x 1012.7925 / 360.68 = 2.8080: rho_c > 2.0: not a candidate
- RB cost: (commission $4.02 + 2 x one-side $9.570754 [2.278751 ticks x $4.2]) / r_c $1012.7925 = $23.161507 / $1012.7925 = 0.02286896 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): none; excluded by R7: none
- Preferred (rho_c >= 0.5): none
- Decides: no admissible contract has rho_c <= 2.0 after R7

### ULSD (K4): no candidate: not traded in Stage E

- HO (ADV 187,479): r_c = $1441.3968; R*/r_c = 360.68 / 1441.3968 = 0.2502, round-half-up 0; q_c = min(cap 1 (D9.5), max(1, 0)) = 1; rho_c = 1 x 1441.3968 / 360.68 = 3.9963: rho_c > 2.0: not a candidate
- HO cost: (commission $4.02 + 2 x one-side $18.626569 [4.434897 ticks x $4.2]) / r_c $1441.3968 = $41.273138 / $1441.3968 = 0.02863413 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): none; excluded by R7: none
- Preferred (rho_c >= 0.5): none
- Decides: no admissible contract has rho_c <= 2.0 after R7

### gold (K5): chosen: MGC

- MGC (ADV 429,702): r_c = $258.5897; R*/r_c = 360.68 / 258.5897 = 1.3948, round-half-up 1; q_c = min(cap 10 (D9.5), max(1, 1)) = 1; rho_c = 1 x 258.5897 / 360.68 = 0.7170: 0.5 <= rho_c <= 2.0: candidate, preferred
- MGC cost: (commission $1.92 + 2 x one-side $1.077978 [1.077978 ticks x $1.0]) / r_c $258.5897 = $4.075956 / $258.5897 = 0.01576225 per dollar of risk
- GC (ADV 212,764): r_c = $2586.9655; R*/r_c = 360.68 / 2586.9655 = 0.1394, round-half-up 0; q_c = min(cap 1 (D9.5), max(1, 0)) = 1; rho_c = 1 x 2586.9655 / 360.68 = 7.1725: rho_c > 2.0: not a candidate
- GC cost: (commission $4.32 + 2 x one-side $19.521125 [1.952113 ticks x $10.0]) / r_c $2586.9655 = $43.362251 / $2586.9655 = 0.01676182 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['MGC']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['MGC']
- Decides: the only preferred candidate: MGC (cost per dollar of risk 0.01576225)
- eps_X = floor(85.00 / (1 x $1.0)) = floor(85.0000) = 85 net ticks per contract per day (R12)

### silver (K5): no candidate: not traded in Stage E

- SIL (ADV 134,882): r_c = $931.0517; R*/r_c = 360.68 / 931.0517 = 0.3874, round-half-up 0; q_c = min(cap 2 (D9.11), max(1, 0)) = 1; rho_c = 1 x 931.0517 / 360.68 = 2.5814: rho_c > 2.0: not a candidate
- SIL cost: (commission $2.72 + 2 x one-side $5.581591 [1.116318 ticks x $5.0]) / r_c $931.0517 = $13.883183 / $931.0517 = 0.01491129 per dollar of risk
- SI (ADV 83,587): r_c = $4653.9655; R*/r_c = 360.68 / 4653.9655 = 0.0775, round-half-up 0; q_c = min(cap 1 (D9.5), max(1, 0)) = 1; rho_c = 1 x 4653.9655 / 360.68 = 12.9033: rho_c > 2.0: not a candidate
- SI cost: (commission $4.32 + 2 x one-side $42.052621 [1.682105 ticks x $25.0]) / r_c $4653.9655 = $88.425242 / $4653.9655 = 0.01899998 per dollar of risk
- R9 (D9.11) SIL sentence: without it the rule gives no candidate: not traded in Stage E; the sentence does not bind
- Candidates (rho_c <= 2.0, less R7): none; excluded by R7: none
- Preferred (rho_c >= 0.5): none
- Decides: no admissible contract has rho_c <= 2.0 after R7

### copper (K5): chosen: MHG

- HG (ADV 77,679): r_c = $1101.2931; R*/r_c = 360.68 / 1101.2931 = 0.3275, round-half-up 0; q_c = min(cap 1 (D9.5), max(1, 0)) = 1; rho_c = 1 x 1101.2931 / 360.68 = 3.0534: rho_c > 2.0: not a candidate
- HG cost: (commission $4.32 + 2 x one-side $13.964791 [1.117183 ticks x $12.5]) / r_c $1101.2931 = $32.249582 / $1101.2931 = 0.02928338 per dollar of risk
- MHG (ADV 21,803): r_c = $110.2155; R*/r_c = 360.68 / 110.2155 = 3.2725, round-half-up 3; q_c = min(cap 2 (D9.11), max(1, 3)) = 2; rho_c = 2 x 110.2155 / 360.68 = 0.6112: 0.5 <= rho_c <= 2.0: candidate, preferred
- MHG cost: (commission $1.92 + 2 x one-side $1.344426 [1.075541 ticks x $1.25]) / r_c $110.2155 = $4.608852 / $110.2155 = 0.04181673 per dollar of risk
- R9 (D9.11) MHG sentence: without it the rule gives chosen MHG; the sentence does not bind
- Candidates (rho_c <= 2.0, less R7): ['MHG']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['MHG']
- Decides: R9 (D9.11): MHG is a candidate (rho 0.6112), so it is the vehicle
- eps_X = floor(85.00 / (2 x $1.25)) = floor(34.0000) = 34 net ticks per contract per day (R12)

### corn (K6): undersized: ZC

- ZC (ADV 505,663): r_c = $158.1642; R*/r_c = 360.68 / 158.1642 = 2.2804, round-half-up 2; q_c = min(cap 1 (D9.5), max(1, 2)) = 1; rho_c = 1 x 158.1642 / 360.68 = 0.4385: rho_c < 0.5: candidate, not preferred
- ZC cost: (commission $5.28 + 2 x one-side $6.268447 [0.501476 ticks x $12.5]) / r_c $158.1642 = $17.816893 / $158.1642 = 0.11264807 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['ZC']; excluded by R7: none
- Preferred (rho_c >= 0.5): none
- Decides: R10: no candidate has rho_c >= 0.5; the only candidate: ZC (cost per dollar of risk 0.11264807)
- eps_X = floor(85.00 / (1 x $12.5)) = floor(6.8000) = 6 net ticks per contract per day (R12)
- R10: undersized, traded at the cap; its funnel-derived epsilon then governs (D2, D3)

### wheat (K6): chosen: ZW

- ZW (ADV 180,405): r_c = $234.7473; R*/r_c = 360.68 / 234.7473 = 1.5365, round-half-up 2; q_c = min(cap 1 (D9.5), max(1, 2)) = 1; rho_c = 1 x 234.7473 / 360.68 = 0.6508: 0.5 <= rho_c <= 2.0: candidate, preferred
- ZW cost: (commission $5.28 + 2 x one-side $6.607072 [0.528566 ticks x $12.5]) / r_c $234.7473 = $18.494144 / $234.7473 = 0.07878321 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['ZW']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['ZW']
- Decides: the only preferred candidate: ZW (cost per dollar of risk 0.07878321)
- eps_X = floor(85.00 / (1 x $12.5)) = floor(6.8000) = 6 net ticks per contract per day (R12)

### soybeans (K6): chosen: ZS

- ZS (ADV 302,997): r_c = $304.3907; R*/r_c = 360.68 / 304.3907 = 1.1849, round-half-up 1; q_c = min(cap 1 (D9.5), max(1, 1)) = 1; rho_c = 1 x 304.3907 / 360.68 = 0.8439: 0.5 <= rho_c <= 2.0: candidate, preferred
- ZS cost: (commission $5.28 + 2 x one-side $6.536460 [0.522917 ticks x $12.5]) / r_c $304.3907 = $18.352920 / $304.3907 = 0.06029396 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['ZS']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['ZS']
- Decides: the only preferred candidate: ZS (cost per dollar of risk 0.06029396)
- eps_X = floor(85.00 / (1 x $12.5)) = floor(6.8000) = 6 net ticks per contract per day (R12)

### soybean meal (K6): chosen: ZM

- ZM (ADV 181,637): r_c = $212.6374; R*/r_c = 360.68 / 212.6374 = 1.6962, round-half-up 2; q_c = min(cap 1 (D9.5), max(1, 2)) = 1; rho_c = 1 x 212.6374 / 360.68 = 0.5895: 0.5 <= rho_c <= 2.0: candidate, preferred
- ZM cost: (commission $5.28 + 2 x one-side $5.399096 [0.539910 ticks x $10.0]) / r_c $212.6374 = $16.078192 / $212.6374 = 0.07561320 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['ZM']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['ZM']
- Decides: the only preferred candidate: ZM (cost per dollar of risk 0.07561320)
- eps_X = floor(85.00 / (1 x $10.0)) = floor(8.5000) = 8 net ticks per contract per day (R12)

### soybean oil (K6): chosen: ZL

- ZL (ADV 232,819): r_c = $304.8298; R*/r_c = 360.68 / 304.8298 = 1.1832, round-half-up 1; q_c = min(cap 1 (D9.5), max(1, 1)) = 1; rho_c = 1 x 304.8298 / 360.68 = 0.8452: 0.5 <= rho_c <= 2.0: candidate, preferred
- ZL cost: (commission $5.28 + 2 x one-side $3.876757 [0.646126 ticks x $6.0]) / r_c $304.8298 = $13.033515 / $304.8298 = 0.04275670 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['ZL']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['ZL']
- Decides: the only preferred candidate: ZL (cost per dollar of risk 0.04275670)
- eps_X = floor(85.00 / (1 x $6.0)) = floor(14.1667) = 14 net ticks per contract per day (R12)

### lean hogs (K6): chosen: HE

- HE (ADV 67,267): r_c = $322.9630; R*/r_c = 360.68 / 322.9630 = 1.1168, round-half-up 1; q_c = min(cap 1 (D9.5), max(1, 1)) = 1; rho_c = 1 x 322.9630 / 360.68 = 0.8954: 0.5 <= rho_c <= 2.0: candidate, preferred
- HE cost: (commission $5.22 + 2 x one-side $6.689544 [0.668954 ticks x $10.0]) / r_c $322.9630 = $18.599087 / $322.9630 = 0.05758892 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['HE']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['HE']
- Decides: the only preferred candidate: HE (cost per dollar of risk 0.05758892)
- eps_X = floor(85.00 / (1 x $10.0)) = floor(8.5000) = 8 net ticks per contract per day (R12)

### live cattle (K6): chosen: LE

- LE (ADV 68,652): r_c = $707.1591; R*/r_c = 360.68 / 707.1591 = 0.5100, round-half-up 1; q_c = min(cap 1 (D9.5), max(1, 1)) = 1; rho_c = 1 x 707.1591 / 360.68 = 1.9606: 0.5 <= rho_c <= 2.0: candidate, preferred
- LE cost: (commission $5.22 + 2 x one-side $9.356252 [0.935625 ticks x $10.0]) / r_c $707.1591 = $23.932503 / $707.1591 = 0.03384317 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['LE']; excluded by R7: none
- Preferred (rho_c >= 0.5): ['LE']
- Decides: the only preferred candidate: LE (cost per dollar of risk 0.03384317)
- eps_X = floor(85.00 / (1 x $10.0)) = floor(8.5000) = 8 net ticks per contract per day (R12)

### bitcoin (K7): undersized: MBT

- MBT (ADV 69,615): r_c = $120.6135; R*/r_c = 360.68 / 120.6135 = 2.9904, round-half-up 3; q_c = min(cap 1 (D9.5), max(1, 3)) = 1; rho_c = 1 x 120.6135 / 360.68 = 0.3344: rho_c < 0.5: candidate, not preferred
- MBT cost: (commission $2.82 + 2 x one-side $0.801498 [1.602996 ticks x $0.5]) / r_c $120.6135 = $4.422996 / $120.6135 = 0.03667083 per dollar of risk
- Candidates (rho_c <= 2.0, less R7): ['MBT']; excluded by R7: none
- Preferred (rho_c >= 0.5): none
- Decides: R10: no candidate has rho_c >= 0.5; the only candidate: MBT (cost per dollar of risk 0.03667083)
- eps_X = floor(85.00 / (1 x $0.5)) = floor(170.0000) = 170 net ticks per contract per day (R12)
- R10: undersized, traded at the cap; its funnel-derived epsilon then governs (D2, D3)

## Questions for the lead

- None: R1-R12 settle every exposure (no cost tie, no SIL/MHG corner case).

## Input and code sha256

Calendar modules changed since phase 1 (current hashes below): ['data/calendars/equity.py'].

- reports/stage_e2a_costs.json: f4360bb77272d0335485a9e01c0f6fc6ab99c47d52e640d95f9cd0397296df14
- reports/stage_e2a_vehicle_sizes.json: 280d7e9df1953069448ca1762588477146a5d3c35bc53d3e9e2df50272c47325
- reports/stage_e2a_vehicle_rule_readings.md: 8c3c29dd6531782b6b98d75192071977b8caebd37c48de6cab0afd1642d6b458
- reports/stage_e0_liquidity.json: 28d2fdac51be883a0fc0d05e9a9ee4a0233276d3a37f49e08fd9804b0ebeb78c
- reports/stage_e2a_bars.json: cf5e49e13cbe9a47dbf57343e632da957541f3ececcf9abb2e16a4df0651b0f4
- docs/STAGE_E_DESIGN.md: 615bb1e14f9072b12f6a5c6206b463fc7828989ad0a9c8e463ebb301ea55103a
- data/processed/MNQ/ohlcv-1m_MNQ_v_0_2025-04-01_2026-06-19_research.parquet: 9506eace6dae2e8193947db083451766d0ed168bcfe86f1ece2d25ee845fe315
- data/processed/NQ/ohlcv-1m_NQ_v_0_2025-04-01_2026-06-19_research.parquet: 5284f91e7ada8da99438975f53f8a190626c508e6ab8042a7f8c6cd140df4d6e
- data/processed/RTY/ohlcv-1m_RTY_v_0_2025-04-01_2026-06-19_research.parquet: 45d340b8853595cb4c97dc11abffa4191bc2b44a0260c94adb28904fd7a9a693
- data/processed/M2K/ohlcv-1m_M2K_v_0_2025-04-01_2026-06-19_research.parquet: fb08ff51bb7c5e85208bdf567e6d09a7dec654c9c6ab47f427b5118c3852f7dc
- data/processed/MYM/ohlcv-1m_MYM_v_0_2025-04-01_2026-06-19_research.parquet: 061e816d27b3a5e824abda357f21be6a6aded672558ea4ce3aeb3660d9fd09d8
- data/processed/YM/ohlcv-1m_YM_v_0_2025-04-01_2026-06-19_research.parquet: 71d4f33718d5ab5ff609d4fcddfdff087413f757dbae887473111466d52f0c0f
- data/processed/ZT/ohlcv-1m_ZT_v_0_2025-04-01_2026-06-19_research.parquet: 729a661b70e50e0254eb6366b90da48e526b079b4ded34c3c8752080f9d04b08
- data/processed/ZF/ohlcv-1m_ZF_v_0_2025-04-01_2026-06-19_research.parquet: 12f7aba9b57d49c93370e27529677224d715559e94d5001e8a4c9b5471111d10
- data/processed/ZN/ohlcv-1m_ZN_v_0_2025-04-01_2026-06-19_research.parquet: f4a403f8641c593daac8b8ea42674233c90574181fac3a001d26c4c31e487ee0
- data/processed/TN/ohlcv-1m_TN_v_0_2025-04-01_2026-06-19_research.parquet: 3d7e1affa41ab8fb3e4a2704fcf583ff75c8d1745e40fc503a9e723191a0a2df
- data/processed/ZB/ohlcv-1m_ZB_v_0_2025-04-01_2026-06-19_research.parquet: bc437fe4d7fefbd60f2f84a2d2e9b04ef0eae2672f049f62a0adb55f0dc920c0
- data/processed/UB/ohlcv-1m_UB_v_0_2025-04-01_2026-06-19_research.parquet: 98c384f0d0f165be4b74917b8a16f6e6ba0e1bc642516fbf7383444da9a12369
- data/processed/6E/ohlcv-1m_6E_v_0_2025-04-01_2026-06-19_research.parquet: 32738b639684cc382cc06597bb39ea9c4c7d5df0925bc40977c1e6ebc53bc8d5
- data/processed/M6E/ohlcv-1m_M6E_v_0_2025-04-01_2026-06-19_research.parquet: c1cd01a3741a5097bfdf9cbf2d250f3c0a1201bf1c7b2e86a8ddee3dac71efbb
- data/processed/E7/ohlcv-1m_E7_v_0_2025-04-01_2026-06-19_research.parquet: 3c44af807c4be19346c9a6cea8f00eb75f9f234e28e327d914e4b0c33327f138
- data/processed/6A/ohlcv-1m_6A_v_0_2025-04-01_2026-06-19_research.parquet: 41d579724f2e04bb5a6183fde996fe76bb05b78e44cb6cdb49f631a1caa8133b
- data/processed/M6A/ohlcv-1m_M6A_v_0_2025-04-01_2026-06-19_research.parquet: 1edea024a19420cc10a73e03a2ccc0f962b122797d2a4120c21f683512dd86a1
- data/processed/6B/ohlcv-1m_6B_v_0_2025-04-01_2026-06-19_research.parquet: ec0af6afb9541f6ab8ebefe116add156416290ee4faf76a7c962dc261b428fa8
- data/processed/M6B/ohlcv-1m_M6B_v_0_2025-04-01_2026-06-19_research.parquet: 3b1cacc19d3727e111f16709ce30eefada71ed4a701c36ca1d254679c6503633
- data/processed/6C/ohlcv-1m_6C_v_0_2025-04-01_2026-06-19_research.parquet: 5c39143960d544c11b4fb9790e64450e98faee60cb07fe8d7e2ee4eccca52eb8
- data/processed/6J/ohlcv-1m_6J_v_0_2025-04-01_2026-06-19_research.parquet: bf8f6a218c01e05cbad48488d0d3c3e71e7076afacd2c9f12914a2f87142bbb2
- data/processed/6S/ohlcv-1m_6S_v_0_2025-04-01_2026-06-19_research.parquet: 579bce49a102928240088400b4ba4d6398fe5974ef7b5dab43326a2ba1fbf27c
- data/processed/6N/ohlcv-1m_6N_v_0_2025-04-01_2026-06-19_research.parquet: d6497c80be6ef65c5d58b29152fffd6fe6dcdc4fe1ad927a0449e226810dc6e8
- data/processed/CL/ohlcv-1m_CL_v_0_2025-04-01_2026-06-19_research.parquet: 589b824c8a622b1fb583c36a0226d845bd427dd2a00f2b0c659f66cbb9a08c4b
- data/processed/MCL/ohlcv-1m_MCL_v_0_2025-04-01_2026-06-19_research.parquet: 6be9bb5ba95ab66515c8a4739bfcbc82894f8602619ff97ab8ee9799d2e2cd69
- data/processed/QM/ohlcv-1m_QM_v_0_2025-04-01_2026-06-19_research.parquet: c1ded239a5a836ddf545b429b2a8b1bd20e3ac00afeddae8b756f3b52a77508c
- data/processed/NG/ohlcv-1m_NG_v_0_2025-04-01_2026-06-19_research.parquet: 41f1f1c8e00dbef5b5065544371cd2af25878dc1316e099781145b00c60e9648
- data/processed/MNG/ohlcv-1m_MNG_v_0_2025-04-01_2026-06-19_research.parquet: ef4b32d857d2c721ff65aaa31d03d377439b5fde0ffc1e5224f2ff8e74760767
- data/processed/QG/ohlcv-1m_QG_v_0_2025-04-01_2026-06-19_research.parquet: 5d67ced9f2e7705c9d7856df4872469d46b4dd322ff8b14859db18f585657ce0
- data/processed/RB/ohlcv-1m_RB_v_0_2025-04-01_2026-06-19_research.parquet: e086852ec627240b7b44d177a7e5b1637681e886aab214f1f333031446c90be7
- data/processed/HO/ohlcv-1m_HO_v_0_2025-04-01_2026-06-19_research.parquet: a5cde179158087720c1d1f3cb210fe66934b3adadddc3d33d923023a095b6781
- data/processed/MGC/ohlcv-1m_MGC_v_0_2025-04-01_2026-06-19_research.parquet: f6bcdd63c9bfc99b1b5a358fc549fe795796209dc5f8374e752906ca75852dd2
- data/processed/GC/ohlcv-1m_GC_v_0_2025-04-01_2026-06-19_research.parquet: fa8c47a0eb2bed8860caaac7831ce9d374dddd06b0269c494c5c7602d08f9c65
- data/processed/SIL/ohlcv-1m_SIL_v_0_2025-04-01_2026-06-19_research.parquet: b1e4b093f972c9ad698f757c5f36f29a9f4e05708338869878f1de539ade6d61
- data/processed/SI/ohlcv-1m_SI_v_0_2025-04-01_2026-06-19_research.parquet: 340679454cf50829ca631ca9e51ae8eb744cbe01f285f4bff1b8153c42b42d8b
- data/processed/HG/ohlcv-1m_HG_v_0_2025-04-01_2026-06-19_research.parquet: ebce30184089590ef65c800e0a45c354def557b867447c23fa995d995a6179e9
- data/processed/MHG/ohlcv-1m_MHG_v_0_2025-04-01_2026-06-19_research.parquet: 4c3deb8ecd7c2b322f42b7eefc836d99e71ec8014be4fa1d254952e10543b2f8
- data/processed/ZC/ohlcv-1m_ZC_v_0_2025-04-01_2026-06-19_research.parquet: 37106ebc79d7d331d1f7d8847ca329eacb95b828ca5386af3d2b39a556e0e410
- data/processed/ZW/ohlcv-1m_ZW_v_0_2025-04-01_2026-06-19_research.parquet: a9c459d94f4dacdadbb5d5ec75be31cc0c76edecfd7f1d53f45476cf84b9c55a
- data/processed/ZS/ohlcv-1m_ZS_v_0_2025-04-01_2026-06-19_research.parquet: 4d159a37b36f6d354a55b685fdb1cc4310cefda246e4df8dab798c7e8e0464c8
- data/processed/ZM/ohlcv-1m_ZM_v_0_2025-04-01_2026-06-19_research.parquet: 74d0b79665c9dd34b1e691fcc81adbb0669be89380dca911229e78640a9cb486
- data/processed/ZL/ohlcv-1m_ZL_v_0_2025-04-01_2026-06-19_research.parquet: 4a33fdc073176e521a564d00c474be1755b761863eb3344cba154baa99340641
- data/processed/HE/ohlcv-1m_HE_v_0_2025-04-01_2026-06-19_research.parquet: 7188ac519e199e6cdbe0a7bb50b5a462e16d9922a3c548c2b58d7c604f17cce6
- data/processed/LE/ohlcv-1m_LE_v_0_2025-04-01_2026-06-19_research.parquet: 883b34eb75e2d79b3d6e56daf1e3dba18d89b3fd97b301a68e9e09a86255cd91
- data/processed/MBT/ohlcv-1m_MBT_v_0_2025-04-01_2026-06-19_research.parquet: 78ef1710165fd3a184d84d5e544526c85b6608355178b2b62ec60550d479cf14
- data/cme_calendar.py: 61218c13635ca73558fcf6ff73884e7cd6f09d5f5f5ceb0d7d7abd28ad968c89
- data/calendars/equity.py: 3315e81225400add3ba2cc949117c090db0806d495879382d5f3ad02b59e041c
- data/calendars/__init__.py: a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a
- data/calendars/rates.py: 449c152977d21dc84721871d970960845bc3e21e603361f5d59e71841ef4df23
- data/calendars/fx.py: 07bdf8c6e4363d5626e655841dbb4ffa65458cd66d5b273a069ed4e47eb746b6
- data/calendars/energy.py: ef90ef8d19df6e2d87cfeb57a224d49a5ba95c66e22cf27bee67b4741f052806
- data/calendars/metals.py: 8224189e04e349ab13047b10181ed41ceb5d61567fb681726545b0a03cad58d1
- data/calendars/grains.py: a685731be437412fa8dcb9120f0f37392112d6b4d41a781db393351a38f7806f
- data/calendars/livestock.py: 57727e68c448153ed018d0c0d0f03107db56d93e26da190e6d356f34e743c501
- data/calendars/crypto.py: 683807b74d5fb888dcdbcb61ec816adc436a7edec4da28576ebc267a07d97227
- screening/vehicles.py: 3864247b60c180c4a8799a6e223bf6f64613f073a922de9768924503b4738466
- screening/vehicles_run.py: 378228a1b7d0c3211c13824395d053d3c1eb3e2db478d5cf69758e76e457db26
- screening/vehicles_md.py: 09fe65adff795882b732573f2424e3e4b0809ed9535a769a1ecba4b5ecbc7f20
- screening/vehicles_choice.py: 65d0f6b24acfebaa5e0125066eee7d568a482e2048618a4b97ec0ce44f2bd855
- screening/vehicles_choice_md.py: c680c556c375d68a242d9c4742e92ed2fc907a384ea900733bfed69472260868
- sim/product_costs.py: 2a640c7ca7a7d83a03cb1975f6a99729462c32336c403835c1b9798203018f51
