# Stage E.2b step 2 quotes (free; $0.00 quote lines only)

Session stage-E.5-2026-09-27, GLBX.MDP3 ohlcv-1m, 2019-05-01..2025-04-01 (end exclusive, 00:00 UTC), 71 monthly chunks; a contract listed later starts at its first priced month (OC-R). Written by `python -m data.pull_step2 --quote-only`; costs, bytes and counts only. Nothing was bought and no cap was changed.

## acct-2 by the gate's own arithmetic

- Spent on acct-2 (sum of `usd` over this repo's acct-2 ledger lines, SpendGate.account_spent_usd): **$103.477194**
- Account cap ACCOUNT_2_CAP_USD: $125.00; cap headroom **$21.522806**
- Credit when opened (U5): $125.00; credit left **$21.522806**
- Session stage-E.5-2026-09-27: session cap $0.00, request cap $0.00 (quotes only)

Reading the tables: a set's top-up buys the whole set against today's credit; a cluster's top-up is that cluster ALONE against today's credit (cluster top-ups do not add up). Lead ruling OC-R: a contract listed after 2019-05 is planned from its first vendor-priceable month (MBT 2021-04, MCL 2021-06, MHG 2022-04); earlier months are not requested and not counted. A failed chunk quote inside a plan carries its cause in the ledger's quote line and is priced at nothing in these totals.

## (a) ML route: the 31 price-path contracts (docs/STAGE_E_ML_DESIGN.md M1)

- 31 contracts, 2178 chunks, 2178 quoted, complete
- **Total quoted $189.31**; with 10% (D13's session-cap rule) $208.24
- acct-2 top-up needed: $167.79 at the quote, $186.72 at quote + 10%; ACCOUNT_2_CAP_USD would have to be at least $292.79 ($311.72 with 10%)

| Cluster | Contracts | Quoted | Top-up at quote | Top-up at quote + 10% | Complete |
|---|---|---:|---:|---:|---|
| K1 | NQ, RTY, YM | $22.53 | $1.01 | $3.26 | yes |
| K2 | ZT, ZF, ZN, TN, ZB, UB | $40.50 | $18.98 | $23.03 | yes |
| K3 | 6E, 6A, 6B, 6C, 6J, 6S, 6N | $49.34 | $27.81 | $32.75 | yes |
| K4 | CL, NG, RB, HO | $25.21 | $3.68 | $6.20 | yes |
| K5 | GC, SI, HG | $22.10 | $0.58 | $2.79 | yes |
| K6 | ZC, ZW, ZS, ZM, ZL, HE, LE | $26.52 | $5.00 | $7.65 | yes |
| K7 | MBT | $3.11 | $0.00 | $0.00 | yes |

| Contract | Cluster | Quoted | 2019-05..2024-02 (kept) | 2024-03..2025-03 (sealed) | Largest chunk | Chunks quoted | Failed chunks |
|---|---|---:|---:|---:|---:|---:|---|
| NQ | K1 | $7.62 | $6.23 | $1.40 | $0.12 | 71/71 | - |
| RTY | K1 | $7.34 | $6.01 | $1.33 | $0.11 | 71/71 | - |
| YM | K1 | $7.57 | $6.20 | $1.37 | $0.12 | 71/71 | - |
| ZT | K2 | $6.01 | $4.85 | $1.16 | $0.11 | 71/71 | - |
| ZF | K2 | $6.98 | $5.72 | $1.26 | $0.11 | 71/71 | - |
| ZN | K2 | $7.23 | $5.92 | $1.31 | $0.11 | 71/71 | - |
| TN | K2 | $6.59 | $5.38 | $1.21 | $0.11 | 71/71 | - |
| ZB | K2 | $6.80 | $5.61 | $1.20 | $0.11 | 71/71 | - |
| UB | K2 | $6.88 | $5.62 | $1.26 | $0.11 | 71/71 | - |
| 6E | K3 | $7.50 | $6.13 | $1.37 | $0.11 | 71/71 | - |
| 6A | K3 | $7.39 | $6.03 | $1.37 | $0.11 | 71/71 | - |
| 6B | K3 | $7.09 | $5.82 | $1.27 | $0.11 | 71/71 | - |
| 6C | K3 | $7.05 | $5.78 | $1.26 | $0.11 | 71/71 | - |
| 6J | K3 | $7.47 | $6.09 | $1.37 | $0.11 | 71/71 | - |
| 6S | K3 | $6.21 | $5.00 | $1.22 | $0.10 | 71/71 | - |
| 6N | K3 | $6.62 | $5.37 | $1.25 | $0.11 | 71/71 | - |
| CL | K4 | $7.57 | $6.20 | $1.38 | $0.12 | 71/71 | - |
| NG | K4 | $6.86 | $5.62 | $1.24 | $0.11 | 71/71 | - |
| RB | K4 | $5.29 | $4.28 | $1.01 | $0.09 | 71/71 | - |
| HO | K4 | $5.49 | $4.44 | $1.05 | $0.09 | 71/71 | - |
| GC | K5 | $7.55 | $6.17 | $1.38 | $0.12 | 71/71 | - |
| SI | K5 | $7.21 | $5.87 | $1.34 | $0.11 | 71/71 | - |
| HG | K5 | $7.34 | $5.99 | $1.35 | $0.11 | 71/71 | - |
| ZC | K6 | $4.67 | $3.88 | $0.79 | $0.08 | 71/71 | - |
| ZW | K6 | $4.53 | $3.71 | $0.82 | $0.07 | 71/71 | - |
| ZS | K6 | $5.11 | $4.18 | $0.92 | $0.08 | 71/71 | - |
| ZM | K6 | $4.39 | $3.57 | $0.83 | $0.07 | 71/71 | - |
| ZL | K6 | $4.88 | $3.97 | $0.91 | $0.08 | 71/71 | - |
| HE | K6 | $1.47 | $1.20 | $0.27 | $0.02 | 71/71 | - |
| LE | K6 | $1.48 | $1.21 | $0.27 | $0.02 | 71/71 | - |
| MBT | K7 | $3.11 | $1.90 | $1.21 | $0.10 | 48/48 | - |

## (b) Each cluster's chosen vehicles (reports/stage_e2a_vehicles.json, status "chosen")

- 22 contracts, 1502 chunks, 1502 quoted, complete
- **Total quoted $128.34**; with 10% (D13's session-cap rule) $141.18
- acct-2 top-up needed: $106.82 at the quote, $119.65 at quote + 10%; ACCOUNT_2_CAP_USD would have to be at least $231.82 ($244.65 with 10%)

| Cluster | Contracts | Quoted | Top-up at quote | Top-up at quote + 10% | Complete |
|---|---|---:|---:|---:|---|
| K1 | MNQ, M2K, MYM | $22.11 | $0.59 | $2.80 | yes |
| K2 | ZN, TN, ZB, UB | $27.51 | $5.99 | $8.74 | yes |
| K3 | 6E, 6A, 6B, 6J, 6S | $35.67 | $14.15 | $17.71 | yes |
| K4 | MCL, NG | $11.46 | $0.00 | $0.00 | yes |
| K5 | MGC, MHG | $9.74 | $0.00 | $0.00 | yes |
| K6 | ZW, ZS, ZM, ZL, HE, LE | $21.86 | $0.33 | $2.52 | yes |
| K7 | (none) | $0.00 | $0.00 | $0.00 | yes |

| Contract | Cluster | Quoted | 2019-05..2024-02 (kept) | 2024-03..2025-03 (sealed) | Largest chunk | Chunks quoted | Failed chunks |
|---|---|---:|---:|---:|---:|---:|---|
| MNQ | K1 | $7.59 | $6.20 | $1.40 | $0.12 | 71/71 | - |
| M2K | K1 | $7.15 | $5.83 | $1.31 | $0.12 | 71/71 | - |
| MYM | K1 | $7.37 | $6.03 | $1.34 | $0.12 | 71/71 | - |
| ZN | K2 | $7.23 | $5.92 | $1.31 | $0.11 | 71/71 | - |
| TN | K2 | $6.59 | $5.38 | $1.21 | $0.11 | 71/71 | - |
| ZB | K2 | $6.80 | $5.61 | $1.20 | $0.11 | 71/71 | - |
| UB | K2 | $6.88 | $5.62 | $1.26 | $0.11 | 71/71 | - |
| 6E | K3 | $7.50 | $6.13 | $1.37 | $0.11 | 71/71 | - |
| 6A | K3 | $7.39 | $6.03 | $1.37 | $0.11 | 71/71 | - |
| 6B | K3 | $7.09 | $5.82 | $1.27 | $0.11 | 71/71 | - |
| 6J | K3 | $7.47 | $6.09 | $1.37 | $0.11 | 71/71 | - |
| 6S | K3 | $6.21 | $5.00 | $1.22 | $0.10 | 71/71 | - |
| MCL | K4 | $4.60 | $3.27 | $1.33 | $0.12 | 46/46 | - |
| NG | K4 | $6.86 | $5.62 | $1.24 | $0.11 | 71/71 | - |
| MGC | K5 | $7.30 | $5.94 | $1.36 | $0.12 | 71/71 | - |
| MHG | K5 | $2.44 | $1.32 | $1.12 | $0.10 | 36/36 | - |
| ZW | K6 | $4.53 | $3.71 | $0.82 | $0.07 | 71/71 | - |
| ZS | K6 | $5.11 | $4.18 | $0.92 | $0.08 | 71/71 | - |
| ZM | K6 | $4.39 | $3.57 | $0.83 | $0.07 | 71/71 | - |
| ZL | K6 | $4.88 | $3.97 | $0.91 | $0.08 | 71/71 | - |
| HE | K6 | $1.47 | $1.20 | $0.27 | $0.02 | 71/71 | - |
| LE | K6 | $1.48 | $1.21 | $0.27 | $0.02 | 71/71 | - |

## (b2) Each cluster's purchase: traded vehicles (chosen or undersized, R10) plus every leg root its members read (frozen catalog; MES excluded; K8 legs only)

- 28 contracts, 1905 chunks, 1905 quoted, complete
- **Total quoted $162.78**; with 10% (D13's session-cap rule) $179.06
- acct-2 top-up needed: $141.26 at the quote, $157.53 at quote + 10%; ACCOUNT_2_CAP_USD would have to be at least $266.26 ($282.53 with 10%)

| Cluster | Contracts | Quoted | Top-up at quote | Top-up at quote + 10% | Complete |
|---|---|---:|---:|---:|---|
| K1 | MNQ, M2K, MYM | $22.11 | $0.59 | $2.80 | yes |
| K2 | ZT, ZF, ZN, TN, ZB, UB | $40.50 | $18.98 | $23.03 | yes |
| K3 | 6E, 6A, 6B, 6C, 6J, 6S, 6N | $49.34 | $27.81 | $32.75 | yes |
| K4 | MCL, NG | $11.46 | $0.00 | $0.00 | yes |
| K5 | MGC, MHG | $9.74 | $0.00 | $0.00 | yes |
| K6 | ZC, ZW, ZS, ZM, ZL, HE, LE | $26.52 | $5.00 | $7.65 | yes |
| K7 | MBT | $3.11 | $0.00 | $0.00 | yes |
| K8 | MGC, 6C, MNQ, MCL, MBT | $29.65 | $8.13 | $11.09 | yes |

| Contract | Cluster | Quoted | 2019-05..2024-02 (kept) | 2024-03..2025-03 (sealed) | Largest chunk | Chunks quoted | Failed chunks |
|---|---|---:|---:|---:|---:|---:|---|
| MNQ | K1 | $7.59 | $6.20 | $1.40 | $0.12 | 71/71 | - |
| M2K | K1 | $7.15 | $5.83 | $1.31 | $0.12 | 71/71 | - |
| MYM | K1 | $7.37 | $6.03 | $1.34 | $0.12 | 71/71 | - |
| ZT | K2 | $6.01 | $4.85 | $1.16 | $0.11 | 71/71 | - |
| ZF | K2 | $6.98 | $5.72 | $1.26 | $0.11 | 71/71 | - |
| ZN | K2 | $7.23 | $5.92 | $1.31 | $0.11 | 71/71 | - |
| TN | K2 | $6.59 | $5.38 | $1.21 | $0.11 | 71/71 | - |
| ZB | K2 | $6.80 | $5.61 | $1.20 | $0.11 | 71/71 | - |
| UB | K2 | $6.88 | $5.62 | $1.26 | $0.11 | 71/71 | - |
| 6E | K3 | $7.50 | $6.13 | $1.37 | $0.11 | 71/71 | - |
| 6A | K3 | $7.39 | $6.03 | $1.37 | $0.11 | 71/71 | - |
| 6B | K3 | $7.09 | $5.82 | $1.27 | $0.11 | 71/71 | - |
| 6C | K3 | $7.05 | $5.78 | $1.26 | $0.11 | 71/71 | - |
| 6J | K3 | $7.47 | $6.09 | $1.37 | $0.11 | 71/71 | - |
| 6S | K3 | $6.21 | $5.00 | $1.22 | $0.10 | 71/71 | - |
| 6N | K3 | $6.62 | $5.37 | $1.25 | $0.11 | 71/71 | - |
| MCL | K4 | $4.60 | $3.27 | $1.33 | $0.12 | 46/46 | - |
| NG | K4 | $6.86 | $5.62 | $1.24 | $0.11 | 71/71 | - |
| MGC | K5 | $7.30 | $5.94 | $1.36 | $0.12 | 71/71 | - |
| MHG | K5 | $2.44 | $1.32 | $1.12 | $0.10 | 36/36 | - |
| ZC | K6 | $4.67 | $3.88 | $0.79 | $0.08 | 71/71 | - |
| ZW | K6 | $4.53 | $3.71 | $0.82 | $0.07 | 71/71 | - |
| ZS | K6 | $5.11 | $4.18 | $0.92 | $0.08 | 71/71 | - |
| ZM | K6 | $4.39 | $3.57 | $0.83 | $0.07 | 71/71 | - |
| ZL | K6 | $4.88 | $3.97 | $0.91 | $0.08 | 71/71 | - |
| HE | K6 | $1.47 | $1.20 | $0.27 | $0.02 | 71/71 | - |
| LE | K6 | $1.48 | $1.21 | $0.27 | $0.02 | 71/71 | - |
| MBT | K7 | $3.11 | $1.90 | $1.21 | $0.10 | 48/48 | - |

