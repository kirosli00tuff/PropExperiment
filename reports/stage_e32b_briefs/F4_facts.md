# F4 facts (Stage E.32b, FactTable C1), unmasked

Generated 2026-10-29 01:31 PDT from F4_facts_unmasked.json (READY line: `4a4d1e2965ee6dbc8497c6dc2b08ac74fa51b61df548cd1b2173ecbf4171397c 2026-10-29 01:16:45 PDT`), F4_smean.json, F4_venue_ibkr.json. Facts only; no score. Item ids are the F2 readers' ids (reports/stage_e32b_briefs/F2_*.json). '-' = unknown or not applicable.

## 1. Codes

| code | family | tick | v USD | mult | ADV (E.28) | ADV kind | leader | siblings | settles off sibling | main session PT | listing |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MCL | crude | 0.01 | 1 | 100 | 79142 | v0_front_median | CL | QM CL | yes: CL (CRUDE-9) | 06:30-13:00 | 2021-07-12 |
| QM | crude | 0.025 | 12.5 | 500 | - | unknown | CL | MCL CL | yes: CL (CRUDE-10) | 06:30-13:00 | 2002-06-17 |
| CL | crude | 0.01 | 10 | 1000 | 227772 | v0_front_median | CL | MCL QM | no | 06:30-13:00 | 1983-01-01 |
| MNG | natgas | 0.001 | 1 | 1000 | 13781 | published_all_expiry | NG | QG NG | yes: NG (NATGAS-36) | 06:30-13:00 | 2023-11-06 |
| QG | natgas | 0.005 | 12.5 | 2500 | 3937 | published_all_expiry | NG | MNG NG | yes: NG (NATGAS-35) | 06:30-13:00 | 2002-06-17 |
| NG | natgas | 0.001 | 10 | 10000 | 85334 | v0_front_median | NG | MNG QG | no | 06:30-13:00 | 2006-09-05 |
| MGC | metals | 0.1 | 1 | 10 | 52744 | v0_front_median | GC | GC | no | 06:30-13:00 | 2010-10-04 |
| GC | metals | 0.1 | 10 | 100 | 160118 | v0_front_median | GC | MGC | no | 06:30-13:00 | - |
| SIL | metals | 0.005 | 5 | 1000 | 74000 | published_all_expiry | SI | SI | no | 06:30-13:00 | 2013-06-01 |
| SI | metals | 0.005 | 25 | 5000 | 64000 | published_all_expiry | SI | SIL | no | 06:30-13:00 | - |
| MHG | metals | 0.0005 | 1.25 | 2500 | 4373 | v0_front_median | HG | HG | yes: HG (METALS-8, METALS-9) | 06:30-13:00 | 2022-05-02 |
| HG | metals | 0.0005 | 12.5 | 25000 | 59578.5 | v0_front_median | HG | MHG | no | 06:30-13:00 | - |
| M6E | fx | 0.0001 | 1.25 | 12500 | 23742 | published_all_expiry | 6E | 6E | no | 06:30-13:00 | 2009-03-01 |
| 6E | fx | 5e-05 | 6.25 | 125000 | 176291 | v0_front_median | 6E | M6E | no | 06:30-13:00 | - |
| M6A | fx | 0.0001 | 1 | 10000 | 7384 | published_all_expiry | 6A | 6A | no | 06:30-13:00 | 2009-03-01 |
| 6A | fx | 5e-05 | 5 | 100000 | 82950 | v0_front_median | 6A | M6A | no | 06:30-13:00 | - |
| MET | crypto | 0.5 | 0.05 | 0.1 | 144000 | published_all_expiry | ETH | ETH | no | - | 2021-12-06 |
| ETH | crypto | 0.5 | 25 | 50 | 19000 | published_all_expiry | ETH | MET | no | - | 2021-02-08 |
| MBT | crypto | 5 | 0.5 | 0.1 | 6678 | v0_front_median | BTC | BTC | no | 06:30-13:00 | 2021-05-03 |
| BTC | crypto | 5 | 25 | 5 | - | unknown | BTC | MBT | no | 06:30-13:00 | 2017-12-18 |
| M2K | equity | 0.1 | 0.5 | 5 | 79724 | published_all_expiry | RTY | RTY | no | 06:30-13:00 | 2019-05-06 |
| RTY | equity | 0.1 | 5 | 50 | 181060 | v0_front_median | RTY | M2K | no | 06:30-13:00 | 2017-07-10 |
| MYM | equity | 1 | 0.5 | 0.5 | 114779 | published_all_expiry | YM | YM | no | 06:30-13:00 | 2019-05-06 |
| YM | equity | 1 | 5 | 5 | 163416 | v0_front_median | YM | MYM | no | 06:30-13:00 | - |
| MNQ | equity | 0.25 | 0.5 | 2 | 1.6e+06 | published_all_expiry | NQ | NQ | no | 06:30-13:00 | 2019-05-06 |
| NQ (excluded V49) | equity | 0.25 | 5 | 20 | 618345 | v0_front_median | NQ | MNQ | no | 06:30-13:00 | 1999-06-01 |
| 2YY | rates | 0.001 | 1 | 1000 | 0 | published_all_expiry | 2YY | - | no | - | 2021-08-16 |
| 5YY | rates | 0.001 | 1 | 1000 | 0 | published_all_expiry | 5YY | - | no | - | 2021-08-16 |
| 10Y | rates | 0.001 | 1 | 1000 | 1277 | published_all_expiry | 10Y | - | no | - | 2021-08-16 |
| 30Y | rates | 0.001 | 1 | 1000 | 0 | published_all_expiry | 30Y | - | no | - | 2021-08-16 |
| ZT | rates | 0.00390625 | 7.8125 | 2000 | 472003 | v0_front_median | ZT | - | no | 06:30-13:00 | - |
| ZF | rates | 0.0078125 | 7.8125 | 1000 | 927861 | v0_front_median | ZF | - | no | 06:30-13:00 | - |
| ZN | rates | 0.015625 | 15.625 | 1000 | 1.38581e+06 | v0_front_median | ZN | - | no | 06:30-13:00 | - |
| ZB | rates | 0.03125 | 31.25 | 1000 | 291523 | v0_front_median | ZB | - | no | 06:30-13:00 | 1977-01-01 |
| MZC | grains | 0.005 | 2.5 | 500 | - | unknown | ZC | XC ZC | yes: ZC (GRAINS-8) | 06:30-11:20 | 2025-02-24 |
| MZS | grains | 0.005 | 2.5 | 500 | - | unknown | ZS | XK ZS | yes: ZS (GRAINS-8) | 06:30-11:20 | 2025-02-24 |
| MZW | grains | 0.005 | 2.5 | 500 | - | unknown | ZW | XW ZW | yes: ZW (GRAINS-8) | 06:30-11:20 | 2025-02-24 |
| MZL | grains | 0.0002 | 1.2 | 6000 | - | unknown | ZL | ZL | yes: ZL (GRAINS-8) | 06:30-11:20 | 2025-02-24 |
| MZM | grains | 0.2 | 2 | 10 | - | unknown | ZM | ZM | yes: ZM (GRAINS-8) | 06:30-11:20 | 2025-02-24 |
| XC | grains | 0.00125 | 1.25 | 1000 | 1160 | published_all_expiry | ZC | MZC ZC | no | 06:30-11:20 | 2003-04-07 |
| XK | grains | 0.00125 | 1.25 | 1000 | 1980 | published_all_expiry | ZS | MZS ZS | no | 06:30-11:20 | 2003-04-07 |
| XW | grains | 0.00125 | 1.25 | 1000 | 922 | published_all_expiry | ZW | MZW ZW | no | 06:30-11:20 | 2003-04-07 |
| ZC | grains | 0.0025 | 12.5 | 5000 | 91946 | v0_front_median | ZC | MZC XC | no | 06:30-11:20 | - |
| ZS | grains | 0.0025 | 12.5 | 5000 | 77862 | v0_front_median | ZS | MZS XK | no | 06:30-11:20 | - |
| ZW | grains | 0.0025 | 12.5 | 5000 | 39361.5 | v0_front_median | ZW | MZW XW | no | 06:30-11:20 | - |
| ZL | grains | 0.0001 | 6 | 60000 | 42686 | v0_front_median | ZL | MZL | no | 06:30-11:20 | - |
| ZM | grains | 0.1 | 10 | 100 | 36690 | v0_front_median | ZM | MZM | no | 06:30-11:20 | - |

Newer ADV figures shown beside (not used): QM 4480.5 (median daily volume 2025-10-01..2026-09-30 (program measurement, E.31), CRUDE-24); BTC 12167 (5-day average 2026-01-05..09 (CME Bitcoin futures report), CRYPTO-5); M2K 85000 (2025 to October (FTSE Russell insight page), EQUITY-53); RTY 217000 (2025 to October (FTSE Russell insight page), EQUITY-53).

Leader basis: computed from USD-notional ADV (ADV x multiplier x F3 median close) where every sibling's notional is known; the readers' leader otherwise (QM, BTC/MBT, SI/SIL, ETH/MET, the mini and micro grains, ZL/MZL, ZM/MZM).

## 2. Spread S and touch (LR-S)

| code | S | sourced | clause | items | touch | touch sourced | touch item | note |
|---|---|---|---|---|---|---|---|---|
| MCL | 1 (u) | no | none: S = 1 (u) | CRUDE-1, CRUDE-48 | - | no | - | figures are CL's (no sibling transfer) |
| QM | 1 (u) | no | none: S = 1 (u) | CRUDE-1, CRUDE-48 | - | no | - | figures are CL's (no sibling transfer) |
| CL | 1 | yes | LR-S (ii) | CRUDE-48 | - | no | - | S = 1 tick: hourly AVERAGE spreads over the US day session 09:00-14:30 ET, Q1 2023, most active month: 1.27-1.29 ticks, all < 1.5 (CME whitepaper, ful |
| MNG | 1 (u) | no | none: S = 1 (u) | NATGAS-3 | 3 | yes | NATGAS-6 | time-weighted MEAN 2.414 ticks >= 1.5 |
| QG | 1 | yes | LR-S (ii) | NATGAS-2 | 10 | yes | NATGAS-5 | S = 1 tick: program-measured time-weighted MEAN quoted spread, day session: 1.22 ticks < 1.5 (E.2a) |
| NG | 1 | yes | LR-S (ii) | NATGAS-1 | 5 | yes | NATGAS-4 | S = 1 tick: program-measured time-weighted MEAN quoted spread, day session 08:00-13:30 CT, 5 dates 2025-05..2026-04: 1.25 ticks < 1.5 (E.2a) |
| MGC | 1 (u) | no | none: S = 1 (u) | METALS-1, METALS-49 | - | no | - | figures are GC's (no sibling transfer) |
| GC | 1 | yes | LR-S (ii) | METALS-49, METALS-1 | 4.62 | yes | METALS-3 | S = 1 tick: hourly AVERAGE spreads over ET 08:00-13:00 (US day hours), Q1 2023: 1.31-1.35 ticks, all < 1.5; also (iii) METALS-1 'one tick during almos |
| SIL | 1 (u) | no | none: S = 1 (u) | METALS-2 | - | no | - | figure is SI's (no sibling transfer) |
| SI | 1 | yes | LR-S (iii) | METALS-2 | 6.56 | yes | METALS-4 | S = 1 tick: 'one tick wide most of the hours' (2017-Q1 2018); SI tick 0.005 is the tick in force in the F3 window |
| MHG | 1 (u) | no | none: S = 1 (u) | METALS-50 | - | no | - | figure is HG's (no sibling transfer) |
| HG | 1 | yes | LR-S (ii) | METALS-50 | - | no | - | S = 1 tick: hourly AVERAGE spreads over ET 08:00-13:00 (US day hours), Q1 2023: 1.38-1.45 ticks, all < 1.5 (all-hours average 1.55 is above 1.5; the U |
| M6E | 1 (u) | no | none: S = 1 (u) | FX-5, FX-6 | - | no | - | no published figure; forum pointer only |
| 6E | 1 | yes | LR-S (ii) | FX-1 | - | no | - | S = 1 tick: whole-day time-weighted AVERAGE top-of-book spread about 0.6 pip = 1.2 ticks, June 2021, < 1.5 |
| M6A | 1 (u) | no | none: S = 1 (u) | FX-5 | - | no | - | no published figure |
| 6A | 1 | yes | LR-S (i) | FX-3 | - | no | - | S = 1 tick: whole-day MEDIAN top-of-book spread 0.5 pip = 1 tick, December 2020, after the 2020-11-23 tick change (tick in force in the F3 window) |
| MET | 1 (u) | no | none: S = 1 (u) | CRYPTO-3, CRYPTO-4 | - | no | - | none sourced; forum pointer only |
| ETH | 1 (u) | no | none: S = 1 (u) | CRYPTO-3, CRYPTO-4 | - | no | - | none sourced; forum pointer only |
| MBT | 1 (u) | no | none: S = 1 (u) | CRYPTO-1, CRYPTO-2, CRYPTO-3 | - | no | - | figures are BTC's (no sibling transfer) |
| BTC | 1 (u) | no | none: S = 1 (u) | CRYPTO-1, CRYPTO-2 | - | no | - | AVERAGE spreads 13.64 (Jan 2026) and 4.72 (Apr 2023) ticks, session not stated |
| M2K | 1 (u) | no | none: S = 1 (u) | - | - | no | - | no spread figure found by the reader |
| RTY | 1 (u) | no | none: S = 1 (u) | - | - | no | - | no spread figure found by the reader |
| MYM | 1 (u) | no | none: S = 1 (u) | - | - | no | - | no spread figure found by the reader |
| YM | 1 (u) | no | none: S = 1 (u) | - | - | no | - | no spread figure found by the reader |
| MNQ | 1 (u) | no | none: S = 1 (u) | EQUITY-1, EQUITY-2 | - | no | - | abstract with no figure; snippet pointer |
| NQ | 1 (u) | no | none: S = 1 (u) | EQUITY-1, EQUITY-2 | - | no | - | abstract with no figure; snippet pointer |
| 2YY | 1 (u) | no | none: S = 1 (u) | - | - | no | - | no spread figure found by the reader |
| 5YY | 1 (u) | no | none: S = 1 (u) | - | - | no | - | no spread figure found by the reader |
| 10Y | 1 (u) | no | none: S = 1 (u) | RATES-5 | - | no | - | AVERAGE 1.67 ticks >= 1.5 (RTH 2024) |
| 30Y | 1 (u) | no | none: S = 1 (u) | - | - | no | - | no spread figure found by the reader |
| ZT | 1 (u) | no | none: S = 1 (u) | RATES-1 | - | no | - | 2018 statement predates the 2019 ZT tick change (LR-S names this case) |
| ZF | 1 | yes | LR-S (iii) | RATES-1 | - | no | - | S = 1 tick: spread at the minimum increment > 99% of each trading day, RTH 2018; ZF tick unchanged |
| ZN | 1 | yes | LR-S (iii) | RATES-1, RATES-4 | - | no | - | S = 1 tick: > 99% of each 2018 RTH day at the minimum increment; 94% of observations at one tick in March 2020; ZN tick unchanged |
| ZB | 1 | yes | LR-S (iii) | RATES-1 | - | no | - | S = 1 tick: > 99% of each trading day at the minimum increment, RTH 2018; ZB tick unchanged |
| MZC | 1 (u) | no | none: S = 1 (u) | - | - | no | - | no spread figure found by the reader |
| MZS | 1 (u) | no | none: S = 1 (u) | - | - | no | - | no spread figure found by the reader |
| MZW | 1 (u) | no | none: S = 1 (u) | - | - | no | - | no spread figure found by the reader |
| MZL | 1 (u) | no | none: S = 1 (u) | - | - | no | - | no spread figure found by the reader |
| MZM | 1 (u) | no | none: S = 1 (u) | - | - | no | - | no spread figure found by the reader |
| XC | 1 (u) | no | none: S = 1 (u) | - | - | no | - | no spread figure found by the reader |
| XK | 1 (u) | no | none: S = 1 (u) | - | - | no | - | no spread figure found by the reader |
| XW | 1 (u) | no | none: S = 1 (u) | - | - | no | - | no spread figure found by the reader |
| ZC | 1 | yes | LR-S (ii) | GRAINS-1 | - | no | - | S = 1 tick: MEAN quoted spread, day session (BBO), 2008-01..2010-01: 1.26 ticks < 1.5; tick 0.25 c unchanged |
| ZS | 1 | yes | LR-S (ii) | GRAINS-3, GRAINS-33 | - | no | - | S = 1 tick: MEAN of daily volume-weighted spreads, day session H1 2019: 1.118 ticks; whole-day average about 2020: 1.04 ticks; both < 1.5 |
| ZW | 1 (u) | no | none: S = 1 (u) | GRAINS-2 | - | no | - | only a MEAN pooled over corn, wheat and soybeans (1.1 ticks, 2015-16): a figure computed partly on other codes, sessions as pooled; not a wheat figure |
| ZL | 1 (u) | no | none: S = 1 (u) | GRAINS-35, GRAINS-51 | - | no | - | snippet only (US hours 2.06 ticks, 2022), and >= 1.5 |
| ZM | 1 (u) | no | none: S = 1 (u) | GRAINS-50, GRAINS-51 | - | no | - | no spread figure (E.31 markouts; snippet ranking only) |

## 3. S_mean variant (F4_smean.json)

| code | S_mean | item | window | touch_mean | item |
|---|---|---|---|---|---|
| CL | - | - | - | 8 | CRUDE-49 |
| MNG | 2.414 | NATGAS-3 | 5 dates 2025-05-14..2026-04-15, day session 08:00-13:30 CT | - | - |
| HG | - | - | - | 5.35 | METALS-52 |
| 6E | - | - | - | 23 | FX-2 |
| 6A | - | - | - | 15 | FX-4 |
| BTC | 4.72 | CRYPTO-2 | 2023-04-17..2023-04-21 (front BTCJ3), session not stated | - | - |
| 10Y | 1.67 | RATES-5 | 2024 (H1 per E.28), RTH 07:00-16:00 CT | - | - |
| ZT | - | - | - | 99471 | RATES-2 |
| ZF | - | - | - | 1319 | RATES-2 |
| ZN | - | - | - | 2507 | RATES-2 |
| ZB | - | - | - | 377 | RATES-2 |
| ZC | - | - | - | 375.27 | GRAINS-5 |
| ZS | - | - | - | 26.32 | GRAINS-34 |
| ZW | - | - | - | 43.92 | GRAINS-6 |

Counts: {'spread_changes': 3, 'touch_changes': 11}. Unchanged: 33 codes.

## 4. Firms

| firm | modelled plan | DLL 50K | MLL 50K | MLL type | BC | flat by | overnight | P inputs |
|---|---|---|---|---|---|---|---|---|
| topstep | 50K Trading Combine, Standard Path | none | 2000 | trailing on end-of-day balance, monitored intraday on realized+unrealized P&L; C | yes | 15:10 CT | no | native yes, OCO yes, VPS prohibited, rate 3.33 |
| lucid | LucidPro 50K (evaluation then simulated funded); one-time fee, no rebilling | 1200 | 2000 | end-of-day trailing (evaluation and funded); 50,100 once the account exceeds 52, | yes | 16:45 ET | no | native no, OCO yes, VPS unknown, rate unknown |
| tradeify | Growth 50K (evaluation with EOD trailing drawdown and DLL; simulated funded) | 1250 | 2000 | end-of-day trailing, enforced in real time on net liquidation; evaluation: floor | yes | 16:45 ET | no | native no, OCO yes, VPS prohibited, rate unknown |
| mffu | Builder 50K, Default MLL option ($2,000); evaluation then sim funded (1 per user), live after 5th sim payout | 1000 | 2000 | end-of-day trailing (open equity counted at the end of the day); locks once it r | yes | 16:10 ET | no | native no, OCO yes, VPS unknown, rate unknown |
| bulenox | Qualification Account $50,000, Option 1 (trailing, no scaling) or Option 2 (EOD drawdown, scaling, DLL); then simulated Master Account; Funded at discretion after 3 Master payouts | none | 2500 | Option 1: real-time trailing on highest intraday value incl. unrealized; Option  | yes | 15:59 CT | no | native yes, OCO yes, VPS unknown, rate unknown |

DLL 'none': topstep: optional (USD 1,000 only if added at purchase; not a rule violation); the modelled Standard Path plan has none (E.28 firm model dll None); bulenox: Option 1 (the modelled plan) has none; Option 2 has USD 1,100 soft. The econ firm check reports these as 'unverifiable' (not a mismatch); every number matches E.28's firm models.

Payout changed since E.28: bulenox (F2_firms.json payout_qualification).

## 5. Pairs (listed on the 50K plan)

| firm | listed | codes (fee RT USD) |
|---|---|---|
| topstep | 31 | MCL (1.72), QM (3.42), CL (4.02), MNG (1.92), QG (2.02), NG (4.22), MGC (1.92), GC (4.32), SIL (2.72), MHG (1.92), M6E (1), 6E (4.22), M6A (1), 6A (4.22), MET (0.72), MBT (2.82), M2K (1.22), RTY (3.78), MYM (1.22), YM (3.78), MNQ (1.22), NQ (3.78), ZT (2.32), ZF (2.32), ZN (2.62), ZB (2.76), ZC (5.28), ZS (5.28), ZW (5.28), ZL (5.28), ZM (5.28) |
| lucid | 23 | MCL (2.12 u), QM (5.4 u), CL (5.98 u), QG (4 u), NG (6.2 u), MGC (2.2 u), GC (6.2 u), SIL (2.84 u), SI (6.2 u), HG (6.2 u), 6E (6.2 u), 6A (6.2 u), M2K (1.9 u), RTY (5.76 u), MYM (1.9 u), YM (5.76 u), MNQ (1.9 u), NQ (5.76 u), ZC (7.2 u), ZS (15.2 u), ZW (17.2 u), ZL (7.2 u), ZM (9.2 u) |
| tradeify | 24 | MCL (2.12), QM (5.4), CL (5.98), QG (4), NG (6.2), MGC (2.12), GC (6.2), SI (6.2), HG (6.2), M6E (1.6), 6E (6.2), M6A (1.6), 6A (6.2), M2K (1.82), RTY (5.76), MYM (1.82), YM (5.76), MNQ (1.82), NQ (5.76), ZC (7.2), ZS (15.2), ZW (17.2), ZL (7.2), ZM (9.2) |
| mffu | 23 | MCL (1.16), QM (4.32), CL (4.92), MGC (2.2), GC (5.12), SIL (2.84), M6E (1.44), 6E (5.12), M6A (1.44), 6A (5.04), MET (1.16), MBT (3.5), M2K (1.9), RTY (4.68), MYM (1.9), YM (5.76), MNQ (1.9), NQ (4.68), ZC (6.12), ZS (6.12), ZW (6.12), ZL (6.12), ZM (6.12) |
| bulenox | 25 | MCL (1.52), QM (3.92), CL (4.52), QG (2.52), NG (4.52), MGC (1.52), GC (4.62), SI (4.62), HG (4.62), M6E (1), 6E (4.72), M6A (1), 6A (4.72), MET (0.92), MBT (5.52), M2K (1.22), RTY (4.18), MYM (1.22), YM (4.18), MNQ (1.22), NQ (4.18), ZS (5.72), ZW (5.72), ZL (5.72), ZM (5.72) |

Lucid fees are RR-05 (u): the highest round trip for the product at the other four firms (fee_basis per pair). Topstep news windows: blocked full-size RTY YM NQ GC SI HG; capped micros M2K MYM MNQ MGC MHG SIL (one lot allowed).

## 6. Cross-family program items

The International Incentive Program item (RATES-11, a volume-fee incentive, 2011-12-16 to 2026-01-31) is attached to every code its fee table names: 10Y, 2YY, 30Y, 5YY, 6A, 6E, CL, GC, HG, M2K, M6A, M6E, MGC, MNQ, MYM, NG, NQ, QG, QM, RTY, SI, SIL, XC, XK, XW, YM, ZB, ZC, ZF, ZL, ZM, ZN, ZS, ZT, ZW. Not named: MCL, MNG, MHG, the crypto codes, the micro grains. Every other F2 item is attached to every code it lists (codes.<CODE>.f2_items, by topic).

## 7. Data access (copied from F2_data_access.json primary fields)

| code | MBO start | k USD/month | k kind | owned >= 36 m | all read |
|---|---|---|---|---|---|
| MCL | 2021-07-12 | 2.49 | estimate | yes | yes |
| QM | 2017-05-21 | 0.4907 | estimate | yes | yes |
| CL | 2017-05-21 | 3.4346 | estimate | yes | yes |
| MNG | 2023-11-06 | 0.4903 | estimate | yes | yes |
| QG | 2017-05-21 | 0.1996 | estimate | yes | yes |
| NG | 2017-05-21 | 0.9819 | estimate | yes | yes |
| MGC | 2017-05-21 | 8.8585 | estimate | yes | yes |
| GC | 2017-05-21 | 3.96 | estimate | yes | yes |
| SIL | 2017-05-21 | 2.5461 | estimate | no | no |
| SI | - | 2.2308 | estimate | no | no |
| MHG | 2022-05-02 | 1.0809 | estimate | yes | no |
| HG | 2017-05-21 | 0.9872 | estimate | yes | no |
| M6E | 2017-05-21 | 0.9898 | estimate | yes | yes |
| 6E | 2017-05-21 | 3.3259 | estimate | yes | yes |
| M6A | 2017-05-21 | 0.4106 | estimate | yes | no |
| 6A | 2017-05-21 | 2.5367 | estimate | yes | no |
| MET | 2021-12-06 | 1.5772 | estimate | no | no |
| ETH | 2021-02-08 | - | unknown | no | no |
| MBT | 2021-05-03 | 4.6466 | estimate | no | no |
| BTC | 2017-12-18 | - | unknown | no | no |
| M2K | 2019-05-06 | 5.1622 | estimate | yes | yes |
| RTY | 2017-07-10 | 7.1933 | estimate | yes | yes |
| MYM | 2019-05-06 | 9.6483 | estimate | yes | no |
| YM | 2017-05-21 | 5.8351 | estimate | yes | no |
| MNQ | 2019-05-06 | 51.9707 | estimate | yes | yes |
| NQ | 2017-05-21 | 22.8808 | estimate | yes | yes |
| 2YY | 2021-08-16 | - | unknown | no | yes |
| 5YY | 2021-08-16 | - | unknown | no | yes |
| 10Y | 2021-08-16 | - | unknown | no | yes |
| 30Y | 2021-08-16 | - | unknown | no | yes |
| ZT | 2017-05-21 | 3.8991 | estimate | yes | yes |
| ZF | 2017-05-21 | 4.1433 | estimate | yes | yes |
| ZN | 2017-05-21 | 5.0735 | estimate | yes | yes |
| ZB | 2017-05-21 | 2.3205 | estimate | yes | yes |
| MZC | 2025-02-24 | - | unknown | yes | yes |
| MZS | 2025-02-24 | - | unknown | yes | no |
| MZW | 2025-02-24 | - | unknown | yes | no |
| MZL | 2025-02-24 | - | unknown | yes | no |
| MZM | 2025-02-24 | - | unknown | yes | no |
| XC | 2017-05-21 | - | unknown | yes | yes |
| XK | 2017-05-21 | - | unknown | yes | no |
| XW | 2017-05-21 | - | unknown | yes | no |
| ZC | 2017-05-21 | 0.3621 | estimate | yes | yes |
| ZS | 2017-05-21 | 0.7863 | estimate | yes | no |
| ZW | 2017-05-21 | 0.3694 | estimate | yes | no |
| ZL | 2017-05-21 | 0.4995 | estimate | yes | no |
| ZM | 2017-05-21 | 1.671 | ledger MBO quote | yes | no |

F2_data_access writes o_owned_36m and p_all_read as the D5 o and p scores (0/1); F4 holds the booleans the score script reads (owned = F2 o 0; all read = F2 p 1). The score script's soft cross-check therefore lists 47 'o_owned_36m' differences (format, not value).

## 8. Own-broker venue (F4_venue_ibkr.json)

Venue: IBKR own account, British Columbia resident (Interactive Brokers Canada Inc.). Account minimum USD 0.0; overnight holds allowed; no DLL, MLL or flat-by-close; capital ceiling: none recorded in docs/DECISIONS.md: spec 8.3 uses USD 6,000 (u). SIL exchange fee not published (fee unknown). Per-code fees and margins in the JSON.

## 9. Unknowns the scripts meet

- ADV unknown (L = 1 u): QM, BTC, MZC MZS MZW MZL MZM. ADV 0 (E.28 published YTD 2026 figure): 2YY 5YY 30Y.
- F3 sigma unknown (gate): SIL SI MET ETH 2YY 5YY 10Y 30Y (status unknown in F3_vol.json).
- k unknown: ETH BTC, the micro yields, the micro and mini grains. MBO start unknown: SI.
- Lucid fee for every listed pair: RR-05 (u). IBKR SIL fee unknown.
