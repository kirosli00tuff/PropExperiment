# Stage E.21 F8: descriptive economics (not part of any verdict)

Produced by reports/stage_e21_briefs/econ/economics.py from the run's files (reports/stage_e21_runs/, read only), E.13 C2 (reports/stage_e13_trend_carry.md) and reports/stage_e21_proped_rules.json. Numbers: reports/stage_e21_economics.json. Verdicts are unchanged: T1 pass=False, T2 pass=False, T3 pass=False, T4 pass=False.

## 1. Personal account: capital to hold every root at >= 1 contract at full signal

### T1 (sigma_b = 16.6%, S = 17, roots = 17; fractional reconstruction max abs error 2.1e-17)

| tau | k = tau/sigma_b | K_min | binding root | roots rounding to 0 at $10K / $25K / $50K / $100K |
|---|---|---|---|---|
| 15% | 0.902 | $691,077 | LE (LE) | 17 / 11 / 9 / 7 |
| 25% | 1.503 | $414,646 | LE (LE) | 14 / 10 / 8 / 6 |

Supplementary (not the brief's book): with MNG/MZC/MZS/MZL for NG/ZC/ZS/ZL, K_min = $691,077 (15%) and $414,646 (25%), binding LE.

| root | F8 vehicle | sigma$/yr | 15%: at K_min | $10K | $25K | $50K | $100K | 25%: at K_min | $10K | $25K | $50K | $100K |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6E | M6E | 787 | 18.64 | 0.27 | 0.67 | 1.35 | 2.70 | 18.64 | 0.45 | 1.12 | 2.25 | 4.49 |
| CL | MCL | 2,777 | 5.28 | 0.08 | 0.19 | 0.38 | 0.76 | 5.28 | 0.13 | 0.32 | 0.64 | 1.27 |
| GC | MGC | 9,254 | 1.58 | 0.02 | 0.06 | 0.11 | 0.23 | 1.58 | 0.04 | 0.10 | 0.19 | 0.38 |
| HE | HE (FLAG full-size) | 6,586 | 2.23 | 0.03 | 0.08 | 0.16 | 0.32 | 2.23 | 0.05 | 0.13 | 0.27 | 0.54 |
| LE | LE (FLAG full-size) | 14,666 | 1.00 | 0.01 | 0.04 | 0.07 | 0.14 | 1.00 | 0.02 | 0.06 | 0.12 | 0.24 |
| NG | NG (FLAG full-size) | 13,183 | 1.11 | 0.02 | 0.04 | 0.08 | 0.16 | 1.11 | 0.03 | 0.07 | 0.13 | 0.27 |
| NQ | MNQ | 9,743 | 1.51 | 0.02 | 0.05 | 0.11 | 0.22 | 1.51 | 0.04 | 0.09 | 0.18 | 0.36 |
| RTY | M2K | 2,014 | 7.28 | 0.11 | 0.26 | 0.53 | 1.05 | 7.28 | 0.18 | 0.44 | 0.88 | 1.76 |
| TN | MTN | 645 | 22.74 | 0.33 | 0.82 | 1.65 | 3.29 | 22.74 | 0.55 | 1.37 | 2.74 | 5.48 |
| UB | MWN | 1,137 | 12.90 | 0.19 | 0.47 | 0.93 | 1.87 | 12.90 | 0.31 | 0.78 | 1.56 | 3.11 |
| ZB | 30YY | 587 | 24.98 | 0.36 | 0.90 | 1.81 | 3.62 | 24.98 | 0.60 | 1.51 | 3.01 | 6.03 |
| ZC | ZC (FLAG full-size) | 3,817 | 3.84 | 0.06 | 0.14 | 0.28 | 0.56 | 3.84 | 0.09 | 0.23 | 0.46 | 0.93 |
| ZF | 5YY | 752 | 19.50 | 0.28 | 0.71 | 1.41 | 2.82 | 19.50 | 0.47 | 1.18 | 2.35 | 4.70 |
| ZL | ZL (FLAG full-size) | 8,971 | 1.63 | 0.02 | 0.06 | 0.12 | 0.24 | 1.63 | 0.04 | 0.10 | 0.20 | 0.39 |
| ZN | 10YY | 670 | 21.89 | 0.32 | 0.79 | 1.58 | 3.17 | 21.89 | 0.53 | 1.32 | 2.64 | 5.28 |
| ZS | ZS (FLAG full-size) | 7,914 | 1.85 | 0.03 | 0.07 | 0.13 | 0.27 | 1.85 | 0.04 | 0.11 | 0.22 | 0.45 |
| ZT | 2YY | 745 | 19.69 | 0.28 | 0.71 | 1.42 | 2.85 | 19.69 | 0.47 | 1.19 | 2.37 | 4.75 |

Roots rounding to zero contracts (round-half-up of the fractional count above):

- 15%, $10,000: 6E, CL, GC, HE, LE, NG, NQ, RTY, TN, UB, ZB, ZC, ZF, ZL, ZN, ZS, ZT
- 15%, $25,000: CL, GC, HE, LE, NG, NQ, RTY, UB, ZC, ZL, ZS
- 15%, $50,000: CL, GC, HE, LE, NG, NQ, ZC, ZL, ZS
- 15%, $100,000: GC, HE, LE, NG, NQ, ZL, ZS
- 25%, $10,000: 6E, CL, GC, HE, LE, NG, NQ, RTY, UB, ZC, ZF, ZL, ZS, ZT
- 25%, $25,000: CL, GC, HE, LE, NG, NQ, RTY, ZC, ZL, ZS
- 25%, $50,000: GC, HE, LE, NG, NQ, ZC, ZL, ZS
- 25%, $100,000: GC, LE, NG, NQ, ZL, ZS

### T2 (sigma_b = 12.9%, S = 17, roots = 17; fractional reconstruction max abs error 1.0e-17)

| tau | k = tau/sigma_b | K_min | binding root | roots rounding to 0 at $10K / $25K / $50K / $100K |
|---|---|---|---|---|
| 15% | 1.158 | $538,100 | LE (LE) | 17 / 10 / 9 / 7 |
| 25% | 1.931 | $322,860 | LE (LE) | 11 / 9 / 7 / 4 |

Supplementary (not the brief's book): with MNG/MZC/MZS/MZL for NG/ZC/ZS/ZL, K_min = $538,100 (15%) and $322,860 (25%), binding LE.

| root | F8 vehicle | sigma$/yr | 15%: at K_min | $10K | $25K | $50K | $100K | 25%: at K_min | $10K | $25K | $50K | $100K |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6E | M6E | 787 | 18.64 | 0.35 | 0.87 | 1.73 | 3.46 | 18.64 | 0.58 | 1.44 | 2.89 | 5.77 |
| CL | MCL | 2,777 | 5.28 | 0.10 | 0.25 | 0.49 | 0.98 | 5.28 | 0.16 | 0.41 | 0.82 | 1.64 |
| GC | MGC | 9,254 | 1.58 | 0.03 | 0.07 | 0.15 | 0.29 | 1.58 | 0.05 | 0.12 | 0.25 | 0.49 |
| HE | HE (FLAG full-size) | 6,586 | 2.23 | 0.04 | 0.10 | 0.21 | 0.41 | 2.23 | 0.07 | 0.17 | 0.34 | 0.69 |
| LE | LE (FLAG full-size) | 14,666 | 1.00 | 0.02 | 0.05 | 0.09 | 0.19 | 1.00 | 0.03 | 0.08 | 0.15 | 0.31 |
| NG | NG (FLAG full-size) | 13,183 | 1.11 | 0.02 | 0.05 | 0.10 | 0.21 | 1.11 | 0.03 | 0.09 | 0.17 | 0.34 |
| NQ | MNQ | 9,743 | 1.51 | 0.03 | 0.07 | 0.14 | 0.28 | 1.51 | 0.05 | 0.12 | 0.23 | 0.47 |
| RTY | M2K | 2,014 | 7.28 | 0.14 | 0.34 | 0.68 | 1.35 | 7.28 | 0.23 | 0.56 | 1.13 | 2.26 |
| TN | MTN | 645 | 22.74 | 0.42 | 1.06 | 2.11 | 4.23 | 22.74 | 0.70 | 1.76 | 3.52 | 7.04 |
| UB | MWN | 1,137 | 12.90 | 0.24 | 0.60 | 1.20 | 2.40 | 12.90 | 0.40 | 1.00 | 2.00 | 4.00 |
| ZB | 30YY | 587 | 24.98 | 0.46 | 1.16 | 2.32 | 4.64 | 24.98 | 0.77 | 1.93 | 3.87 | 7.74 |
| ZC | ZC (FLAG full-size) | 3,817 | 3.84 | 0.07 | 0.18 | 0.36 | 0.71 | 3.84 | 0.12 | 0.30 | 0.60 | 1.19 |
| ZF | 5YY | 752 | 19.50 | 0.36 | 0.91 | 1.81 | 3.62 | 19.50 | 0.60 | 1.51 | 3.02 | 6.04 |
| ZL | ZL (FLAG full-size) | 8,971 | 1.63 | 0.03 | 0.08 | 0.15 | 0.30 | 1.63 | 0.05 | 0.13 | 0.25 | 0.51 |
| ZN | 10YY | 670 | 21.89 | 0.41 | 1.02 | 2.03 | 4.07 | 21.89 | 0.68 | 1.69 | 3.39 | 6.78 |
| ZS | ZS (FLAG full-size) | 7,914 | 1.85 | 0.03 | 0.09 | 0.17 | 0.34 | 1.85 | 0.06 | 0.14 | 0.29 | 0.57 |
| ZT | 2YY | 745 | 19.69 | 0.37 | 0.91 | 1.83 | 3.66 | 19.69 | 0.61 | 1.52 | 3.05 | 6.10 |

Roots rounding to zero contracts (round-half-up of the fractional count above):

- 15%, $10,000: 6E, CL, GC, HE, LE, NG, NQ, RTY, TN, UB, ZB, ZC, ZF, ZL, ZN, ZS, ZT
- 15%, $25,000: CL, GC, HE, LE, NG, NQ, RTY, ZC, ZL, ZS
- 15%, $50,000: CL, GC, HE, LE, NG, NQ, ZC, ZL, ZS
- 15%, $100,000: GC, HE, LE, NG, NQ, ZL, ZS
- 25%, $10,000: CL, GC, HE, LE, NG, NQ, RTY, UB, ZC, ZL, ZS
- 25%, $25,000: CL, GC, HE, LE, NG, NQ, ZC, ZL, ZS
- 25%, $50,000: GC, HE, LE, NG, NQ, ZL, ZS
- 25%, $100,000: GC, LE, NG, NQ

### T3 (sigma_b = 17.5%, S = 2, roots = 2; fractional reconstruction max abs error 1.4e-17)

| tau | k = tau/sigma_b | K_min | binding root | roots rounding to 0 at $10K / $25K / $50K / $100K |
|---|---|---|---|---|
| 15% | 0.856 | $56,940 | NQ (MNQ) | 1 / 1 / 0 / 0 |
| 25% | 1.426 | $34,164 | NQ (MNQ) | 1 / 0 / 0 / 0 |

Supplementary (not the brief's book): with MNG/MZC/MZS/MZL for NG/ZC/ZS/ZL, K_min = $56,940 (15%) and $34,164 (25%), binding NQ.

| root | F8 vehicle | sigma$/yr | 15%: at K_min | $10K | $25K | $50K | $100K | 25%: at K_min | $10K | $25K | $50K | $100K |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NQ | MNQ | 9,743 | 1.00 | 0.18 | 0.44 | 0.88 | 1.76 | 1.00 | 0.29 | 0.73 | 1.46 | 2.93 |
| RTY | M2K | 2,014 | 4.84 | 0.85 | 2.12 | 4.25 | 8.50 | 4.84 | 1.42 | 3.54 | 7.08 | 14.16 |

Roots rounding to zero contracts (round-half-up of the fractional count above):

- 15%, $10,000: NQ
- 15%, $25,000: NQ
- 15%, $50,000: none
- 15%, $100,000: none
- 25%, $10,000: NQ
- 25%, $25,000: none
- 25%, $50,000: none
- 25%, $100,000: none

### Cross-check against E.13 C3

- C3 chooses which instruments to hold: the N lowest-risk instruments whose one contract is within 1.5x of the target, and floors every held position at 1 contract (max(1, round)). F8 here must hold the 17 fixed roots of the test (2 for T3), including the high-risk full-size LE ($14,666), NG ($13,183), ZL, ZS and the micros MNQ ($9,743) and MGC ($9,254), which C3 never holds even at $100K. So C3 holds 11-23 instruments at $10K-$100K while here T1/T2 need $323K-$691K before LE reaches one contract.
- Per-instrument risk budget: C3 uses tau x IDM(N)/N with rho 0.125 (e.g. $2,692/yr at $100K, 25%, N 23); here it is k x K x 0.40 / S with k from the realized book volatility (T1 at $100K, 25%: 1.503 x 100,000 x 0.40 / 17 = $3,537/yr; T2 $4,544/yr; T3 $28,523/yr per root with S = 2). The orders of magnitude agree for T1/T2; the gap is the fixed universe, not the budget.
- C3 is a separate construction (Carver-style, equal weights over cheap instruments); it is not the tested book, and its $10K-$100K portfolios would not reproduce T1/T2.

## 2. The integer book at its smallest integer size (base case)

| test | scale A (capital $ at unit leverage) | dates | daily mean $ | daily sd $ | 5-day sd $ (blocks) | annual mean $ | annual sd $ | gross $ | costs $ | TE daily $ (annual) | corr with fractional | max micro-equiv |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | 623,305 | 3205 | 212.0 | 6,540 | 14,520 (641) | 53,415 | 103,824 | 729,998 | 50,653 | 505 (8,017) | 0.9970 | 381 |
| T2 | 623,305 | 3205 | 146.2 | 5,099 | 10,958 (641) | 36,845 | 80,951 | 517,166 | 48,559 | 517 (8,203) | 0.9949 | 351 |
| T3 | 48,715 | 3319 | 4.0 | 535 | 1,190 (663) | 1,020 | 8,488 | 17,852 | 4,423 | 34 (537) | 0.9980 | 32 |

No-weekend variant of the same book:

| test | daily sd $ | 5-day sd $ | annual mean $ | dates zeroed | extra weekend fill costs $ |
|---|---|---|---|---|---|
| T1 | 5,797 | 12,824 | -4,881 | 657 | 359,221 |
| T2 | 4,486 | 9,523 | -290 | 657 | 238,131 |
| T3 | 454 | 998 | 420 | 696 | 4,027 |

Per root, largest |contracts| held (F8 vehicles) and nonzero rebalance targets that round to zero:

- T1: 6E M6E max 26, zero 0/150; CL MCL max 13, zero 0/150; GC MGC max 13, zero 0/150; HE HE max 2, zero 0/46; LE LE max 3, zero 0/69; NG NG max 2, zero 14/150; NQ MNQ max 25, zero 0/150; RTY M2K max 14, zero 0/66; TN MTN max 29, zero 0/84; UB MWN max 14, zero 0/150; ZB 30YY max 35, zero 0/150; ZC ZC max 7, zero 0/84; ZF 5YY max 45, zero 0/150; ZL ZL max 6, zero 0/110; ZN 10YY max 33, zero 0/150; ZS ZS max 3, zero 0/117; ZT 2YY max 133, zero 0/150
- T2: 6E M6E max 26, zero 0/150; CL MCL max 13, zero 0/150; GC MGC max 13, zero 0/150; HE HE max 2, zero 17/46; LE LE max 3, zero 4/69; NG NG max 2, zero 54/150; NQ MNQ max 25, zero 0/150; RTY M2K max 13, zero 0/66; TN MTN max 29, zero 0/84; UB MWN max 13, zero 0/150; ZB 30YY max 34, zero 0/150; ZC ZC max 6, zero 1/84; ZF 5YY max 45, zero 0/150; ZL ZL max 6, zero 17/110; ZN 10YY max 33, zero 0/150; ZS ZS max 3, zero 39/117; ZT 2YY max 133, zero 0/150
- T3: NQ MNQ max 32, zero 0/154; RTY M2K max 14, zero 0/73

### T4

T4 is a combination in risk units and has no contract book. Realized volatility of its base daily series: 120.33 risk units per year (3331 dates). Observation for the lead (not interpreted here): the series has 8 days with |value| > 10 (max 299.9; 99th percentile of |value| 3.70); largest days 2016-06-27 -299.9, 2020-09-25 244.8, 2021-07-27 190.5. Without those days the realized volatility is 13.03.

## 3. PropEd plans (automation UNCONFIRMED on every row) and Phidias Premium 50K

Instruments: PropEd's list (Q32) has MNQ, M2K, MGC, MCL, NG, ZC, ZS, ZL, ZT, ZF, ZN, ZB and 6E; it does NOT list M6E, the micro yield futures, MTN, MWN, TN, UB, HE or LE. The list is not plan-specific. Phidias: instrument list UNSOURCED. Daily loss limit is UNSOURCED for every PropEd plan except One Plan ($11,250); Phidias has none.

### T1 (daily sd $6,540, 5-day sd $14,520, max micro-equivalent 381)

| plan | DD type | DD $ | DLL $ | max micros | share days over max | not listed | daily sd / DD | 5-day sd / DD | weekend add-on $ | breach with weekend (trailing / static) | breach no weekend (trailing / static) | 10% scale: m, with wknd tr/st, no wknd tr/st |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Standard Eval - 25k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 1,000 | UNSOURCED | 30 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 6.54 | 14.52 | 16.35 | 100.0% / 84.0% | 99.9% / 84.8% | none |
| Standard Eval - 50k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 2,000 | UNSOURCED | 50 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 3.27 | 7.26 | 26.25 | 100.0% / 81.2% | 99.9% / 81.9% | none |
| Standard Eval - 100k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 4,000 | UNSOURCED | 100 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 1.64 | 3.63 | 42.75 | 100.0% / 76.2% | 99.9% / 77.5% | none |
| Standard Eval - 150k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 6,000 | UNSOURCED | 150 | 93.8% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 1.09 | 2.42 | 54.75 | 98.9% / 70.9% | 98.6% / 72.2% | none |
| Instant Funding - 50k [automation UNCONFIRMED] | EOD ("(eod)"; trailing not stated) | 2,500 | UNSOURCED | 30 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 2.62 | 5.81 | 89.85 | 100.0% / 80.0% | 99.9% / 80.8% | none |
| Instant Funding - 100k [automation UNCONFIRMED] | EOD ("(eod)"; trailing not stated) | 5,000 | UNSOURCED | 60 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 1.31 | 2.90 | 142.35 | 99.7% / 73.3% | 99.2% / 74.9% | none |
| Instant Funding - 150k [automation UNCONFIRMED] | EOD ("(eod)"; trailing not stated) | 7,500 | UNSOURCED | 90 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 0.87 | 1.94 | 194.85 | 97.0% / 66.8% | 96.6% / 68.3% | none |
| TrueRisk Eval - 1.25k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 1,250 | UNSOURCED | 15 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 5.23 | 11.62 | UNSOURCED ("available ... | 100.0% / 83.4% | 99.9% / 84.4% | none |
| TrueRisk Eval - 2.5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 2,500 | UNSOURCED | 30 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 2.62 | 5.81 | UNSOURCED ("available ... | 100.0% / 80.0% | 99.9% / 80.8% | none |
| TrueRisk Eval - 5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 5,000 | UNSOURCED | 60 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 1.31 | 2.90 | UNSOURCED ("available ... | 99.7% / 73.3% | 99.2% / 74.9% | none |
| TrueRisk Eval - 10k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 10,000 | UNSOURCED | 120 | 99.3% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 0.65 | 1.45 | UNSOURCED ("available ... | 92.7% / 59.7% | 91.8% / 60.8% | none |
| TrueRisk - Instant Funded - 2.5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 2,500 | UNSOURCED | 30 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 2.62 | 5.81 | 89.85 | 100.0% / 80.0% | 99.9% / 80.8% | none |
| TrueRisk - Instant Funded - 5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 5,000 | UNSOURCED | 60 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 1.31 | 2.90 | 89.85 | 99.7% / 73.3% | 99.2% / 74.9% | none |
| TrueRisk - Instant Funded - 7.5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 7,500 | UNSOURCED | 90 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 0.87 | 1.94 | 194.85 | 97.0% / 66.8% | 96.6% / 68.3% | none |
| TrueRisk - Instant Funded - 10k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 10,000 | UNSOURCED | 90 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 0.65 | 1.45 | 194.85 | 92.7% / 59.7% | 91.8% / 60.8% | none |
| One Plan - 750k [automation UNCONFIRMED] | trailing EOD, locks at starting balance on... | 37,500 | 11250 | 750 | 0.0% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 0.17 | 0.39 | UNSOURCED | 56.9% / 56.8% | 51.1% / 51.0% | none |
| Nexus X5 Evaluation - 50k [automation UNCONFIRMED] | trailing EOD (Q87) | 2,500 | UNSOURCED | 50 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 2.62 | 5.81 | UNSOURCED | 100.0% / 80.0% | 99.9% / 80.8% | none |
| Phidias Premium 50K (comparison) [semi-automated only] | EOD trailing; on CASH stops trailing at $5... | 2,500 | none | 100 | 99.4% | UNSOURCED (Phidias instrument list not collected) | 2.62 | 5.81 | not needed / none listed | 100.0% / 80.0% | 99.9% / 80.8% | none |

### T2 (daily sd $5,099, 5-day sd $10,958, max micro-equivalent 351)

| plan | DD type | DD $ | DLL $ | max micros | share days over max | not listed | daily sd / DD | 5-day sd / DD | weekend add-on $ | breach with weekend (trailing / static) | breach no weekend (trailing / static) | 10% scale: m, with wknd tr/st, no wknd tr/st |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Standard Eval - 25k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 1,000 | UNSOURCED | 30 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 5.10 | 10.96 | 16.35 | 100.0% / 80.8% | 99.9% / 82.9% | none |
| Standard Eval - 50k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 2,000 | UNSOURCED | 50 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 2.55 | 5.48 | 26.25 | 99.4% / 76.3% | 98.8% / 78.2% | none |
| Standard Eval - 100k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 4,000 | UNSOURCED | 100 | 90.8% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 1.27 | 2.74 | 42.75 | 97.0% / 67.8% | 95.3% / 69.4% | none |
| Standard Eval - 150k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 6,000 | UNSOURCED | 150 | 57.0% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 0.85 | 1.83 | 54.75 | 92.4% / 59.9% | 90.3% / 61.1% | none |
| Instant Funding - 50k [automation UNCONFIRMED] | EOD ("(eod)"; trailing not stated) | 2,500 | UNSOURCED | 30 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 2.04 | 4.38 | 89.85 | 99.2% / 74.2% | 98.6% / 76.1% | none |
| Instant Funding - 100k [automation UNCONFIRMED] | EOD ("(eod)"; trailing not stated) | 5,000 | UNSOURCED | 60 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 1.02 | 2.19 | 142.35 | 95.1% / 64.1% | 93.2% / 65.2% | none |
| Instant Funding - 150k [automation UNCONFIRMED] | EOD ("(eod)"; trailing not stated) | 7,500 | UNSOURCED | 90 | 95.9% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 0.68 | 1.46 | 194.85 | 86.2% / 55.0% | 82.5% / 54.5% | none |
| TrueRisk Eval - 1.25k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 1,250 | UNSOURCED | 15 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 4.08 | 8.77 | UNSOURCED ("available ... | 100.0% / 79.9% | 99.9% / 81.6% | none |
| TrueRisk Eval - 2.5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 2,500 | UNSOURCED | 30 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 2.04 | 4.38 | UNSOURCED ("available ... | 99.2% / 74.2% | 98.6% / 76.1% | none |
| TrueRisk Eval - 5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 5,000 | UNSOURCED | 60 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 1.02 | 2.19 | UNSOURCED ("available ... | 95.1% / 64.1% | 93.2% / 65.2% | none |
| TrueRisk Eval - 10k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 10,000 | UNSOURCED | 120 | 77.0% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 0.51 | 1.10 | UNSOURCED ("available ... | 76.6% / 46.3% | 72.2% / 45.0% | none |
| TrueRisk - Instant Funded - 2.5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 2,500 | UNSOURCED | 30 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 2.04 | 4.38 | 89.85 | 99.2% / 74.2% | 98.6% / 76.1% | none |
| TrueRisk - Instant Funded - 5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 5,000 | UNSOURCED | 60 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 1.02 | 2.19 | 89.85 | 95.1% / 64.1% | 93.2% / 65.2% | none |
| TrueRisk - Instant Funded - 7.5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 7,500 | UNSOURCED | 90 | 95.9% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 0.68 | 1.46 | 194.85 | 86.2% / 55.0% | 82.5% / 54.5% | none |
| TrueRisk - Instant Funded - 10k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 10,000 | UNSOURCED | 90 | 95.9% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 0.51 | 1.10 | 194.85 | 76.6% / 46.3% | 72.2% / 45.0% | none |
| One Plan - 750k [automation UNCONFIRMED] | trailing EOD, locks at starting balance on... | 37,500 | 11250 | 750 | 0.0% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 0.14 | 0.29 | UNSOURCED | 26.2% / 25.9% | 24.2% / 23.8% | none |
| Nexus X5 Evaluation - 50k [automation UNCONFIRMED] | trailing EOD (Q87) | 2,500 | UNSOURCED | 50 | 99.4% | 10YY, 2YY, 30YY, 5YY, HE, LE, M6E, MTN, MWN | 2.04 | 4.38 | UNSOURCED | 99.2% / 74.2% | 98.6% / 76.1% | none |
| Phidias Premium 50K (comparison) [semi-automated only] | EOD trailing; on CASH stops trailing at $5... | 2,500 | none | 100 | 90.8% | UNSOURCED (Phidias instrument list not collected) | 2.04 | 4.38 | not needed / none listed | 99.2% / 74.2% | 98.6% / 76.1% | none |

### T3 (daily sd $535, 5-day sd $1,190, max micro-equivalent 32)

| plan | DD type | DD $ | DLL $ | max micros | share days over max | not listed | daily sd / DD | 5-day sd / DD | weekend add-on $ | breach with weekend (trailing / static) | breach no weekend (trailing / static) | 10% scale: m, with wknd tr/st, no wknd tr/st |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Standard Eval - 25k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 1,000 | UNSOURCED | 30 | 0.2% | - | 0.53 | 1.19 | 16.35 | 55.8% / 42.7% | 48.1% / 37.6% | none |
| Standard Eval - 50k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 2,000 | UNSOURCED | 50 | 0.0% | - | 0.27 | 0.60 | 26.25 | 31.3% / 24.8% | 27.2% / 22.8% | none |
| Standard Eval - 100k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 4,000 | UNSOURCED | 100 | 0.0% | - | 0.13 | 0.30 | 42.75 | 6.7% / 5.2% | 4.3% / 4.1% | none |
| Standard Eval - 150k [automation UNCONFIRMED] | EOD ("(eod)"; whether it trails is not sta... | 6,000 | UNSOURCED | 150 | 0.0% | - | 0.09 | 0.20 | 54.75 | 1.4% / 1.4% | 0.2% / 0.2% | m=1: 1.4% / 1.4%; 0.2% / 0.2% |
| Instant Funding - 50k [automation UNCONFIRMED] | EOD ("(eod)"; trailing not stated) | 2,500 | UNSOURCED | 30 | 0.2% | - | 0.21 | 0.48 | 89.85 | 21.8% / 16.9% | 17.3% / 15.9% | none |
| Instant Funding - 100k [automation UNCONFIRMED] | EOD ("(eod)"; trailing not stated) | 5,000 | UNSOURCED | 60 | 0.0% | - | 0.11 | 0.24 | 142.35 | 2.7% / 2.1% | 1.5% / 1.5% | none |
| Instant Funding - 150k [automation UNCONFIRMED] | EOD ("(eod)"; trailing not stated) | 7,500 | UNSOURCED | 90 | 0.0% | - | 0.07 | 0.16 | 194.85 | 1.2% / 1.2% | 0.0% / 0.0% | m=1: 1.2% / 1.2%; 0.0% / 0.0% |
| TrueRisk Eval - 1.25k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 1,250 | UNSOURCED | 15 | 7.0% | - | 0.43 | 0.95 | UNSOURCED ("available ... | 48.7% / 35.5% | 40.6% / 33.5% | none |
| TrueRisk Eval - 2.5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 2,500 | UNSOURCED | 30 | 0.2% | - | 0.21 | 0.48 | UNSOURCED ("available ... | 21.8% / 16.9% | 17.3% / 15.9% | none |
| TrueRisk Eval - 5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 5,000 | UNSOURCED | 60 | 0.0% | - | 0.11 | 0.24 | UNSOURCED ("available ... | 2.7% / 2.1% | 1.5% / 1.5% | none |
| TrueRisk Eval - 10k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 10,000 | UNSOURCED | 120 | 0.0% | - | 0.05 | 0.12 | UNSOURCED ("available ... | 0.6% / 0.6% | 0.0% / 0.0% | m=1: 0.6% / 0.6%; 0.0% / 0.0% |
| TrueRisk - Instant Funded - 2.5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 2,500 | UNSOURCED | 30 | 0.2% | - | 0.21 | 0.48 | 89.85 | 21.8% / 16.9% | 17.3% / 15.9% | none |
| TrueRisk - Instant Funded - 5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 5,000 | UNSOURCED | 60 | 0.0% | - | 0.11 | 0.24 | 89.85 | 2.7% / 2.1% | 1.5% / 1.5% | none |
| TrueRisk - Instant Funded - 7.5k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 7,500 | UNSOURCED | 90 | 0.0% | - | 0.07 | 0.16 | 194.85 | 1.2% / 1.2% | 0.0% / 0.0% | m=1: 1.2% / 1.2%; 0.0% / 0.0% |
| TrueRisk - Instant Funded - 10k [automation UNCONFIRMED] | CONFLICT: Static (plan page, plan comparis... | 10,000 | UNSOURCED | 90 | 0.0% | - | 0.05 | 0.12 | 194.85 | 0.6% / 0.6% | 0.0% / 0.0% | m=1: 0.6% / 0.6%; 0.0% / 0.0% |
| One Plan - 750k [automation UNCONFIRMED] | trailing EOD, locks at starting balance on... | 37,500 | 11250 | 750 | 0.0% | - | 0.01 | 0.03 | UNSOURCED | 0.0% / 0.0% | 0.0% / 0.0% | m=6: 20.6% / 20.6%; 16.7% / 16.7% |
| Nexus X5 Evaluation - 50k [automation UNCONFIRMED] | trailing EOD (Q87) | 2,500 | UNSOURCED | 50 | 0.0% | - | 0.21 | 0.48 | UNSOURCED | 21.8% / 16.9% | 17.3% / 15.9% | none |
| Phidias Premium 50K (comparison) [semi-automated only] | EOD trailing; on CASH stops trailing at $5... | 2,500 | none | 100 | 0.0% | UNSOURCED (Phidias instrument list not collected) | 0.21 | 0.48 | not needed / none listed | 21.8% / 16.9% | 17.3% / 15.9% | none |

Overnight: Standard, Instant and TrueRisk plans 'yes' (FAQ Q21, terms Q02); One Plan and Nexus X5: general FAQ statement only, plan not named (FLAG). Weekend holds: add-on for Standard/Instant/TrueRisk (TrueRisk Eval price UNSOURCED, 'available at checkout'); One Plan and Nexus X5 weekend terms UNSOURCED; Phidias allows weekends (JSON weekend_allowed true).

## 4. Assumptions and flags

1. F8 is descriptive only; no verdict changes (verdict.json pass flags are copied into the JSON).
2. sigma_b = sd (ddof 1) of the run's base-case daily series x sqrt(252), in capital units (flat days included as zeros, as the run's series has them).
3. Per-contract annual dollar risk sigma$_i = E.13 C2 '$ risk / contract / yr' (2026-10-02 prices and Carver T-22 vols; micro yields from T-30). These are today's levels, not the 2010-2024 levels at which the run's targets were set, so the integer book's actual contract counts differ from the K_min arithmetic (e.g. ZT/2YY: low 2010-2020 rate vol gives large historical targets).
4. S = 17 (T1, T2) and 2 (T3), the tests' maximum divisors (confirmed as the maxima of S_M and S_u in the holdings rows).
5. Root to F8 vehicle mapping: NQ->MNQ, RTY->M2K, GC->MGC, CL->MCL (these are already the E.12 vehicles), 6E->M6E, TN->MTN, UB->MWN (notional ratio 10), ZT->2YY, ZF->5YY, ZN->10YY, ZB->30YY (micro Treasury YIELD futures, $10 DV01; converted by the C2 risk ratio because no notional ratio exists; FLAG: yield futures move with the on-the-run yield, not the cheapest-to-deliver price, and the economic direction is inverted, a long note being a short yield position). NG, ZC, ZS, ZL, HE, LE are full-size, FLAGGED (brief's list; C2 does list MNG, MZC, MZS, MZL, shown only as a supplementary K_min line; HE and LE have no micro in C2).
6. K_min(tau) = max_i sigma$_i x S / (k x 0.40), k = tau / sigma_b; per-root contracts at K are k x K x 0.40 / S / sigma$_i at full signal (|s| = 1); 'rounds to zero' uses round-half-up.
7. Integer book: capital scale A = max_i sigma$_i x S / 0.40 dollars at unit leverage (= k x K_min for both tau). Contracts c(i,M) = round_half_up(A x r_i x target(i,M)) in F8 vehicles, r_i = F8 contracts per E.12 vehicle contract. Per-F8-contract daily P&L = the run's per_contract_daily_dollars / r_i.
8. Holding timing: a fill on date d (at MK(d)) changes the holding from date d+1 on; the P&L of date d belongs to the previous holding. This reproduces the run's base series exactly in capital units (max abs error reported per test), so the timing and cost reading match the run.
9. Costs: rebalance/entry/exit fills pay |delta c| x the fill's base cost per contract; each roll leg pays |c| x that leg's base cost per contract. Cost per F8 contract = the run's E.12 per-contract cost / r_i (FLAG: proportional scaling; real micro costs per unit of notional are higher, so micro-converted roots' costs are understated).
10. No-weekend variant: on each series date whose previous series date lies before a Saturday, the gross P&L is set to zero; that date's own fill costs are kept; per root 2 x |c held| x the root's median base per-contract cost (all of its fills in the test, F8 units) is charged on that date.
11. Breach windows: every run of 21 consecutive series dates (step 1). Equity starts at 0 at the window start; trailing = max drop from the running EOD peak (peak includes the start), static = max drop below the start; breach if the drop >= the drawdown amount, or (where a daily loss limit is sourced, One Plan only) any day's loss > the limit. Both measures are shown for every plan; the plan's own type is in the drawdown column (Standard and Instant say EOD without saying whether it trails; TrueRisk is CONFLICT static vs EOD).
12. Max contracts: micro-equivalents with 1 mini = 10 micros (PropEd Q31); full-size F8 vehicles (NG, ZC, ZS, ZL, HE, LE) count as 10, every micro (including 2YY..30YY, MTN, MWN, M6E) as 1. 'share over' = share of series dates whose held micro-equivalent exceeds the plan's micro cap.
13. 10% scale: integer multiples m of A; the largest m with book daily dollar sd <= 10% of the drawdown. Every root holds >= 1 contract at full signal for m >= 1 by construction (C2 basis); 'none' when m = 1 already exceeds 10%.
14. Tracking error: sd of (integer book - fractional book scaled to the integer book's daily dollar sd); the fractional book is the run's base series.
15. Automation is UNCONFIRMED for every PropEd plan (lead ruling A11); Phidias is semi-automated only. No fee or payout model.

FLAGS: full-size roots NG, ZC, ZS, ZL, HE, LE; micro-yield conversion by risk ratio (ZT, ZF, ZN, ZB); proportional micro cost scaling; C2 risk at 2026 levels; automation UNCONFIRMED (PropEd), semi-automated only (Phidias); PropEd drawdown trailing-or-static unresolved for Standard/Instant (EOD, trailing not stated) and TrueRisk (CONFLICT); daily loss limits UNSOURCED except One Plan; PropEd instrument list not plan-specific; Phidias instrument list and price UNSOURCED.
