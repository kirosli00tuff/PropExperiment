# F2 non-prop: IBKR own-broker venue (British Columbia resident)

Worker NonProp-SonnetHigh (B11), Stage E.32b. Pages fetched 2026-10-28 23:33 to 23:40 PDT (UTC 2026-10-29T06:33 to 06:40), saved in pages/NONPROP/ with log.tsv. No page carries a date. Full data with quotes: F2_nonprop.json.

## Entities
- Interactive Brokers Canada Inc. (CIRO) serves a BC resident; Interactive Brokers LLC is the US entity (compared only).
- USD futures commission schedule: identical on both pages. Margins for the 47 codes: identical (resident Canada trading US vs resident US trading US). Market data prices: identical; the LLC rows add footnote 31 ("Fee is waived if commissions generated are greater than USD 15.00."), the Canada rows do not carry it. Canada pages add GST/PST "where applicable" on eligible services.

## Commission rule (USD 0.85 execution, plain sum)
Tiered and Fixed both USD 0.85 per contract at <= 1,000 contracts a month (Tiered then 0.65, 0.45, 0.25 above 1,000, 10,000, 20,000). Micros count 1/10 of a contract toward the tier, e-mini FX 1/2. Exchange fee: non-member Tier 1 from the IBKR exchange pages. Regulatory fee: CME 0.011, CBOT/NYMEX/COMEX 0.01. Clearing USD 0.00 (worked examples). Conflict: the tiered ES example prints regulatory USD 0.00 but totals USD 2.24 (= 0.85 + 1.38 + 0.01). Overnight position fee (Tiered only): USD 0.10 per contract per night when the account just meets margin, 0.05 at 2x, 0.00 at 3x; none if flat by the close.

## Per code: all-in USD per contract per side and margin (USD per contract)

| code | family | IBKR exec | exchange | clearing | reg | all-in per side | intraday init | intraday maint | overnight init | overnight maint |
|---|---|---|---|---|---|---|---|---|---|---|
| MCL | crude | 0.85 | 0.6 | 0.00 | 0.01 | 1.46 | 2351.48 | N/A | 2351.48 | 1650.79 |
| QM | crude | 0.85 | 1.2 | 0.00 | 0.01 | 2.06 | 11757.50 | N/A | 11757.50 | 8253.93 |
| CL | crude | 0.85 | 1.5 | 0.00 | 0.01 | 2.36 | 23442.08 | N/A | 23442.08 | 16441.66 |
| MNG | natgas | 0.85 | 0.7 | 0.00 | 0.01 | 1.56 | 553.19 | N/A | 553.19 | 440.166 |
| QG | natgas | 0.85 | 0.5 | 0.00 | 0.01 | 1.36 | 1383.08 | N/A | 1383.08 | 1100.41 |
| NG | natgas | 0.85 | 1.6 | 0.00 | 0.01 | 2.46 | 5531.90 | N/A | 5531.90 | 4401.66 |
| MGC | metals | 0.85 | 0.7 | 0.00 | 0.01 | 1.56 | 3606.35 | N/A | 3606.35 | 3135.96 |
| GC | metals | 0.85 | 1.65 | 0.00 | 0.01 | 2.51 | 36063.50 | N/A | 36063.50 | 31359.56 |
| SIL | metals | 0.85 | not published | 0.00 | n/p | not computable | 10216.35 | N/A | 10216.35 | 8883.78 |
| SI | metals | 0.85 | 1.65 | 0.00 | 0.01 | 2.51 | 51081.74 | N/A | 51081.74 | 44418.91 |
| MHG | metals | 0.85 | 0.7 | 0.00 | 0.01 | 1.56 | 2484.69 | N/A | 2484.69 | 1780.47 |
| HG | metals | 0.85 | 1.65 | 0.00 | 0.01 | 2.51 | 24771.875 | N/A | 24771.875 | 17804.73 |
| M6E | fx | 0.85 | 0.24 | 0.00 | 0.011 | 1.101 | 349.27 | N/A | 349.27 | 303.713 |
| 6E | fx | 0.85 | 1.6 | 0.00 | 0.011 | 2.461 | 3492.70 | N/A | 3492.70 | 3037.13 |
| M6A | fx | 0.85 | 0.24 | 0.00 | 0.011 | 1.101 | 247.801 | N/A | 247.801 | 206.349 |
| 6A | fx | 0.85 | 1.6 | 0.00 | 0.011 | 2.461 | 2478.01 | N/A | 2478.01 | 2063.49 |
| MET | crypto | 0.85 | 0.1 | 0.00 | 0.011 | 0.961 | 108.048 | N/A | 108.048 | 93.9544 |
| ETH | crypto | 0.85 | 6.05 | 0.00 | 0.011 | 6.911 | 54023.76 | N/A | 54023.76 | 46977.18 |
| MBT | crypto | 0.85 | 1.15 | 0.00 | 0.011 | 2.011 | 2802.55 | N/A | 2802.55 | 2423.62 |
| BTC | crypto | 0.85 | 8.25 | 0.00 | 0.011 | 9.111 | 140152.58 | N/A | 140152.58 | 121180.78 |
| M2K | equity | 0.85 | 0.35 | 0.00 | 0.011 | 1.211 | 876.056 | 761.787 | 1251.51 | 1088.27 |
| RTY | equity | 0.85 | 1.38 | 0.00 | 0.011 | 2.241 | 8760.56 | 7617.87 | 12515.08 | 10882.68 |
| MYM | equity | 0.85 | 0.35 | 0.00 | 0.01 | 1.21 | 1269.99 | 1074.22 | 1814.27 | 1534.60 |
| YM | equity | 0.85 | 1.38 | 0.00 | 0.01 | 2.24 | 12699.91 | 10742.18 | 18142.73 | 15345.97 |
| MNQ | equity | 0.85 | 0.35 | 0.00 | 0.011 | 1.211 | 4622.90 | 2963.27 | 6604.14 | 4233.24 |
| NQ | equity | 0.85 | 1.38 | 0.00 | 0.011 | 2.241 | 46228.98 | 29632.71 | 66041.40 | 42332.44 |
| 2YY | rates | 0.85 | 0.3 | 0.00 | 0.01 | 1.16 | 953.416 | N/A | 953.416 | 829.058 |
| 5YY | rates | 0.85 | 0.3 | 0.00 | 0.01 | 1.16 | 3079.38 | N/A | 3079.38 | 2677.72 |
| 10Y | rates | 0.85 | 0.3 | 0.00 | 0.01 | 1.16 | 667.399 | N/A | 667.399 | 549.912 |
| 30Y | rates | 0.85 | 0.3 | 0.00 | 0.01 | 1.16 | 981.618 | N/A | 981.618 | 853.581 |
| ZT | rates | 0.85 | 0.65 | 0.00 | 0.01 | 1.51 | 1379.84 | N/A | 1379.84 | 1199.86 |
| ZF | rates | 0.85 | 0.65 | 0.00 | 0.01 | 1.51 | 1438.82 | N/A | 1438.82 | 1251.15 |
| ZN | rates | 0.85 | 0.8 | 0.00 | 0.01 | 1.66 | 2161.39 | N/A | 2161.39 | 1879.47 |
| ZB | rates | 0.85 | 0.87 | 0.00 | 0.01 | 1.73 | 4283.66 | N/A | 4283.66 | 3724.92 |
| MZC | grains | 0.85 | 0.5 | 0.00 | 0.01 | 1.36 | 196.777 | N/A | 196.777 | 148.284 |
| MZS | grains | 0.85 | 0.5 | 0.00 | 0.01 | 1.36 | 416.013 | N/A | 416.013 | 361.75 |
| MZW | grains | 0.85 | 0.5 | 0.00 | 0.01 | 1.36 | 287.143 | N/A | 287.143 | 249.69 |
| MZL | grains | 0.85 | 0.5 | 0.00 | 0.01 | 1.36 | 478.96 | N/A | 478.96 | 416.487 |
| MZM | grains | 0.85 | 0.5 | 0.00 | 0.01 | 1.36 | 301.244 | N/A | 301.244 | 261.952 |
| XC | grains | 0.85 | 1.06 | 0.00 | 0.01 | 1.92 | 381.054 | N/A | 381.054 | 296.569 |
| XK | grains | 0.85 | 1.06 | 0.00 | 0.01 | 1.92 | 832.025 | N/A | 832.025 | 723.50 |
| XW | grains | 0.85 | 1.06 | 0.00 | 0.01 | 1.92 | 574.287 | N/A | 574.287 | 499.38 |
| ZC | grains | 0.85 | 2.15 | 0.00 | 0.01 | 3.01 | 1905.27 | N/A | 1905.27 | 1482.84 |
| ZS | grains | 0.85 | 2.15 | 0.00 | 0.01 | 3.01 | 4160.13 | N/A | 4160.13 | 3617.50 |
| ZW | grains | 0.85 | 2.15 | 0.00 | 0.01 | 3.01 | 2871.43 | N/A | 2871.43 | 2496.90 |
| ZL | grains | 0.85 | 2.15 | 0.00 | 0.01 | 3.01 | 4661.63 | N/A | 4661.63 | 4053.59 |
| ZM | grains | 0.85 | 2.15 | 0.00 | 0.01 | 3.01 | 2920.50 | N/A | 2920.50 | 2539.57 |

Mapping notes (IBKR symbols differ): 6E/6A are listed as EUR/AUD in the "Forex Futures" row; MBT fee row is "Bitcoin Micro Futures BRR - Micro" (inference); XC/XK/XW are YC/YK/YW; MNG is MHNG on the fee page; NQ excluded (V49), fact only. SIL: no row on the COMEX fee page, so no all-in figure. Margin drift: all 47 codes differ from the 2026-10-03 fetch of the same page (CL overnight initial 19044.60 then, 23442.08 now), so use only the dated 2026-10-28 values. Intraday maintenance is a number only for M2K, MNQ, MYM, RTY, YM, NQ; elsewhere intraday initial equals overnight initial. Margins are not cross-checked against CME clearing margins.

## Market data (non-professional, per month)
- US Securities Snapshot and Futures Value Bundle: USD 10.00 base waived for activity (page: accounts generating at least USD 30 commissions a month per user) + USD 0.01 per snapshot; includes top of book (L1) for CBOT, CME, COMEX, NYMEX.
- US Futures Value Bundle PLUS: USD 5.00; adds depth of book for the same four exchanges; requires the bundle above.
- A la carte: CBOT, CME, COMEX, NYMEX Real-Time (L1) USD 1.55 each (4 x 1.55 = USD 6.20; waived for accounts with at least USD 20 commissions a month); L2 USD 12.10 each. Professional L1+L2 USD 145.00 each.
- Accounts with under USD 500 equity have market data turned off. Futures data needs US futures trading permission.

## Account and permission
- Account minimum USD 0.00, inactivity fee USD 0.00 (ibkrca_minimums.html).
- Futures permission: request in Client Portal (Settings > Account Settings > Trading Experiences & Permissions); subject to regulatory review, next business day for requests by 11:00 ET; may depend on financial profile; futures are held in a margin account; cash accounts get no intraday margin.
- Not found: any published equity, net-worth or experience threshold for futures permission; futures in TFSA/RRSP. The "1-2 business days" figure is a search snippet [unverified]; a Benzinga snippet about a USD 110,000 portfolio-margin minimum is a pointer, not confirmed by any IBKR page.

## Capital ceiling
None recorded in docs/DECISIONS.md as a number (read lines 386-396, 456-464, 520-526, 575-585, 686-694, 728-735). The spec then uses USD 6,000, marked u. Nearby text that is not a ceiling: V32 "The user cannot fund a personal IBKR account yet"; a USD 25K design-study capital for the micro trend book (lines 731-733); E.13 return "Trend and carry at $10K-$100K".

## Not finished or unverified
SIL exchange fee; margin cross-check against CME; futures-permission thresholds; no Scrapling or Firecrawl used; 2 of 30 WebSearches used.
