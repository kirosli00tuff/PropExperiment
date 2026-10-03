# Step 2 quotes, session stage-E.12-2026-10-03 (free; $0.00 quote lines only)

Session stage-E.12-2026-10-03, GLBX.MDP3 ohlcv-1m, the 13 holdout-2 chunks 2024-03-01..2025-04-01 (end exclusive) per root; quote only, never bought. Written by `python -m data.pull_step2 --quote-only`; costs, bytes and counts only. Nothing was bought and no cap was changed.

## acct-2 by the gate's own arithmetic

- Spent on acct-2 (sum of `usd` over this repo's acct-2 ledger lines, SpendGate.account_spent_usd): **$231.599730**
- Account cap ACCOUNT_2_CAP_USD: $249.67; cap headroom **$18.070270**
- Credit when opened (U5): $125.00; credit left **$18.070270**
- Session stage-E.12-2026-10-03: session cap $137.73, request cap $3.00 (quotes only)

Reading the tables: a set's top-up buys the whole set against today's credit; a cluster's top-up is that cluster ALONE against today's credit (cluster top-ups do not add up). Lead ruling OC-R: a contract listed after 2019-05 is planned from its first vendor-priceable month (MBT 2021-04, MCL 2021-06, MHG 2022-04); earlier months are not requested and not counted. A failed chunk quote inside a plan carries its cause in the ledger's quote line and is priced at nothing in these totals.

## ml-v2+holdout2-only

- Plan: the 13 holdout-2 chunks 2024-03-01..2025-04-01 (end exclusive) per root; quote only, never bought
- 28 contracts, 364 chunks, 364 quoted, complete
- **Total quoted $31.98**; with 10% (D13's session-cap rule) $35.18
- acct-2 top-up needed: $13.91 at the quote, $17.11 at quote + 10%; ACCOUNT_2_CAP_USD would have to be at least $263.58 ($266.78 with 10%)

| Cluster | Contracts | Quoted | Top-up at quote | Top-up at quote + 10% | Complete |
|---|---|---:|---:|---:|---|
| K1 | NQ, RTY, YM | $4.10 | $0.00 | $0.00 | yes |
| K2 | ZT, ZF, ZN, TN, ZB, UB | $7.39 | $0.00 | $0.00 | yes |
| K3 | 6E, 6A, 6B, 6C, 6J, 6S, 6N | $9.11 | $0.00 | $0.00 | yes |
| K4 | CL, NG | $2.62 | $0.00 | $0.00 | yes |
| K5 | GC, HG | $2.73 | $0.00 | $0.00 | yes |
| K6 | ZC, ZW, ZS, ZM, ZL, HE, LE | $4.81 | $0.00 | $0.00 | yes |
| K7 | MBT | $1.21 | $0.00 | $0.00 | yes |

| Contract | Cluster | Quoted | 2019-05..2024-02 (kept) | 2024-03..2025-03 (sealed) | Largest chunk | Chunks quoted | Failed chunks |
|---|---|---:|---:|---:|---:|---:|---|
| NQ | K1 | $1.40 | $0.00 | $1.40 | $0.12 | 13/13 | - |
| RTY | K1 | $1.33 | $0.00 | $1.33 | $0.11 | 13/13 | - |
| YM | K1 | $1.37 | $0.00 | $1.37 | $0.11 | 13/13 | - |
| ZT | K2 | $1.16 | $0.00 | $1.16 | $0.10 | 13/13 | - |
| ZF | K2 | $1.26 | $0.00 | $1.26 | $0.11 | 13/13 | - |
| ZN | K2 | $1.31 | $0.00 | $1.31 | $0.11 | 13/13 | - |
| TN | K2 | $1.21 | $0.00 | $1.21 | $0.10 | 13/13 | - |
| ZB | K2 | $1.20 | $0.00 | $1.20 | $0.10 | 13/13 | - |
| UB | K2 | $1.26 | $0.00 | $1.26 | $0.10 | 13/13 | - |
| 6E | K3 | $1.37 | $0.00 | $1.37 | $0.11 | 13/13 | - |
| 6A | K3 | $1.37 | $0.00 | $1.37 | $0.11 | 13/13 | - |
| 6B | K3 | $1.27 | $0.00 | $1.27 | $0.11 | 13/13 | - |
| 6C | K3 | $1.26 | $0.00 | $1.26 | $0.10 | 13/13 | - |
| 6J | K3 | $1.37 | $0.00 | $1.37 | $0.11 | 13/13 | - |
| 6S | K3 | $1.22 | $0.00 | $1.22 | $0.10 | 13/13 | - |
| 6N | K3 | $1.25 | $0.00 | $1.25 | $0.11 | 13/13 | - |
| CL | K4 | $1.38 | $0.00 | $1.38 | $0.11 | 13/13 | - |
| NG | K4 | $1.24 | $0.00 | $1.24 | $0.10 | 13/13 | - |
| GC | K5 | $1.38 | $0.00 | $1.38 | $0.12 | 13/13 | - |
| HG | K5 | $1.35 | $0.00 | $1.35 | $0.11 | 13/13 | - |
| ZC | K6 | $0.79 | $0.00 | $0.79 | $0.07 | 13/13 | - |
| ZW | K6 | $0.82 | $0.00 | $0.82 | $0.07 | 13/13 | - |
| ZS | K6 | $0.92 | $0.00 | $0.92 | $0.08 | 13/13 | - |
| ZM | K6 | $0.83 | $0.00 | $0.83 | $0.07 | 13/13 | - |
| ZL | K6 | $0.91 | $0.00 | $0.91 | $0.08 | 13/13 | - |
| HE | K6 | $0.27 | $0.00 | $0.27 | $0.02 | 13/13 | - |
| LE | K6 | $0.27 | $0.00 | $0.27 | $0.02 | 13/13 | - |
| MBT | K7 | $1.21 | $0.00 | $1.21 | $0.10 | 13/13 | - |

## Account positions (each account's gate)

| Account | Spent | Cap | Headroom |
|---|---:|---:|---:|
| acct-1 | $118.390020 | $120.00 | $1.609980 |
| acct-2 | $231.599730 | $249.67 | $18.070270 |

Combined headroom: $19.680250
