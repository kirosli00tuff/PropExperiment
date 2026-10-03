# Step 2 quotes, session stage-E.12-2026-10-03 (free; $0.00 quote lines only)

Session stage-E.12-2026-10-03, GLBX.MDP3 ohlcv-1m, 2019-05-01..2024-03-01 (end exclusive, 00:00 UTC): the training window, through range=2024-02-01_2024-03-01; a contract listed later starts at its first priced month (OC-R). Written by `python -m data.pull_step2 --quote-only`; costs, bytes and counts only. Nothing was bought and no cap was changed.

## acct-2 by the gate's own arithmetic

- Spent on acct-2 (sum of `usd` over this repo's acct-2 ledger lines, SpendGate.account_spent_usd): **$124.673761**
- Account cap ACCOUNT_2_CAP_USD: $249.67; cap headroom **$124.996239**
- Credit when opened (U5): $125.00; credit left **$124.996239**
- Session stage-E.12-2026-10-03: session cap $0.00, request cap $3.00 (quotes only)

Reading the tables: a set's top-up buys the whole set against today's credit; a cluster's top-up is that cluster ALONE against today's credit (cluster top-ups do not add up). Lead ruling OC-R: a contract listed after 2019-05 is planned from its first vendor-priceable month (MBT 2021-04, MCL 2021-06, MHG 2022-04); earlier months are not requested and not counted. A failed chunk quote inside a plan carries its cause in the ledger's quote line and is priced at nothing in these totals.

## ml-v2+training-window

- Plan: 2019-05-01..2024-03-01 (end exclusive, 00:00 UTC): the training window, through range=2024-02-01_2024-03-01; a contract listed later starts at its first priced month (OC-R)
- 28 contracts, 1601 chunks, 1601 quoted, complete
- **Total quoted $139.34**; with 10% (D13's session-cap rule) $153.27
- acct-2 top-up needed: $14.34 at the quote, $28.28 at quote + 10%; ACCOUNT_2_CAP_USD would have to be at least $264.01 ($277.95 with 10%)

| Cluster | Contracts | Quoted | Top-up at quote | Top-up at quote + 10% | Complete |
|---|---|---:|---:|---:|---|
| K1 | NQ, RTY, YM | $18.43 | $0.00 | $0.00 | yes |
| K2 | ZT, ZF, ZN, TN, ZB, UB | $33.11 | $0.00 | $0.00 | yes |
| K3 | 6E, 6A, 6B, 6C, 6J, 6S, 6N | $40.22 | $0.00 | $0.00 | yes |
| K4 | CL, NG | $11.81 | $0.00 | $0.00 | yes |
| K5 | GC, HG | $12.16 | $0.00 | $0.00 | yes |
| K6 | ZC, ZW, ZS, ZM, ZL, HE, LE | $21.72 | $0.00 | $0.00 | yes |
| K7 | MBT | $1.90 | $0.00 | $0.00 | yes |

| Contract | Cluster | Quoted | 2019-05..2024-02 (kept) | 2024-03..2025-03 (sealed) | Largest chunk | Chunks quoted | Failed chunks |
|---|---|---:|---:|---:|---:|---:|---|
| NQ | K1 | $6.23 | $6.23 | $0.00 | $0.12 | 58/58 | - |
| RTY | K1 | $6.01 | $6.01 | $0.00 | $0.11 | 58/58 | - |
| YM | K1 | $6.20 | $6.20 | $0.00 | $0.12 | 58/58 | - |
| ZT | K2 | $4.85 | $4.85 | $0.00 | $0.11 | 58/58 | - |
| ZF | K2 | $5.72 | $5.72 | $0.00 | $0.11 | 58/58 | - |
| ZN | K2 | $5.92 | $5.92 | $0.00 | $0.11 | 58/58 | - |
| TN | K2 | $5.38 | $5.38 | $0.00 | $0.11 | 58/58 | - |
| ZB | K2 | $5.61 | $5.61 | $0.00 | $0.11 | 58/58 | - |
| UB | K2 | $5.62 | $5.62 | $0.00 | $0.11 | 58/58 | - |
| 6E | K3 | $6.13 | $6.13 | $0.00 | $0.11 | 58/58 | - |
| 6A | K3 | $6.03 | $6.03 | $0.00 | $0.11 | 58/58 | - |
| 6B | K3 | $5.82 | $5.82 | $0.00 | $0.11 | 58/58 | - |
| 6C | K3 | $5.78 | $5.78 | $0.00 | $0.11 | 58/58 | - |
| 6J | K3 | $6.09 | $6.09 | $0.00 | $0.11 | 58/58 | - |
| 6S | K3 | $5.00 | $5.00 | $0.00 | $0.10 | 58/58 | - |
| 6N | K3 | $5.37 | $5.37 | $0.00 | $0.11 | 58/58 | - |
| CL | K4 | $6.20 | $6.20 | $0.00 | $0.12 | 58/58 | - |
| NG | K4 | $5.62 | $5.62 | $0.00 | $0.11 | 58/58 | - |
| GC | K5 | $6.17 | $6.17 | $0.00 | $0.12 | 58/58 | - |
| HG | K5 | $5.99 | $5.99 | $0.00 | $0.11 | 58/58 | - |
| ZC | K6 | $3.88 | $3.88 | $0.00 | $0.08 | 58/58 | - |
| ZW | K6 | $3.71 | $3.71 | $0.00 | $0.07 | 58/58 | - |
| ZS | K6 | $4.18 | $4.18 | $0.00 | $0.08 | 58/58 | - |
| ZM | K6 | $3.57 | $3.57 | $0.00 | $0.07 | 58/58 | - |
| ZL | K6 | $3.97 | $3.97 | $0.00 | $0.08 | 58/58 | - |
| HE | K6 | $1.20 | $1.20 | $0.00 | $0.02 | 58/58 | - |
| LE | K6 | $1.21 | $1.21 | $0.00 | $0.02 | 58/58 | - |
| MBT | K7 | $1.90 | $1.90 | $0.00 | $0.08 | 35/35 | - |

## Account positions (each account's gate)

| Account | Spent | Cap | Headroom |
|---|---:|---:|---:|
| acct-1 | $91.592247 | $120.00 | $28.407753 |
| acct-2 | $124.673761 | $249.67 | $124.996239 |

Combined headroom: $153.403992
