# Stage E.5 Task B2: the step 2 purchase (K4 and K5), seals and bars

Lead, 2026-09-27 PDT. Everything below is read from the frozen tools' own outputs: the quote record
reports/stage_e5_step2_quotes.json (sha256 e5e8b5792be2946ec93521f8b543874f74ec5978f834c1b3087d8d0f53b97e8b), the ledger
ledger/databento_spend.jsonl, the purchase logs reports/stage_e5_briefs/b2_buy_k4.log and b2_buy_k5.log, `python -m
data.pull_step2 --status` (reports/stage_e5_briefs/b2_status.json) and the store summaries reports/step2/bars_<ROOT>.json.

## Quote and caps (Task B1)
- Fresh quote 17:53-18:10, `python -m data.pull_step2 --quote-only --set clusters-legs` under v5 code: 1905 chunks over 28 contracts, 0 failed,
  1905 quote lines at $0.00 under stage-E.5-2026-09-27. K4 (MCL, NG) $11.455464; K5 (MGC, MHG) $9.741104; total $21.196568 (E.2b's figures, unchanged).
- Caps (data/config.py, harness v6 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87, commit ce3cb66): session cap = min($21.196568 x 1.10 =
  $23.316225, acct-2 headroom $125.00 - $103.477194 = $21.522806) = $21.52 (whole cents, never above the headroom); request cap $3.00 (D13; largest chunk $0.1157).
- K4 alone ($11.455464) under the headroom: no stop. After K4 the headroom was $10.067342 >= K5's $9.741104, so K5 was bought.

## Purchase (ledger)
| Cluster | Root | Chunks (kept + sealed) | Quote | Spent (commit + settle) | Window | rc |
|---|---|---|---|---|---|---|
| K4 | MCL | 33 + 13 = 46 (from 2021-06, OC-R) | $4.597656 | $4.597656 + $0 | 18:13-18:32 | 0 |
| K4 | NG | 58 + 13 = 71 | $6.857809 | $6.857809 + $0 | 18:13-18:32 | 0 |
| K5 | MGC | 58 + 13 = 71 | $7.303256 | $7.303256 + $0 | 18:32-18:50 | 0 |
| K5 | MHG | 23 + 13 = 36 (from 2022-04, OC-R) | $2.437848 | $2.437848 + $0 | 18:32-18:50 | 0 |
| | **Total** | **224** | **$21.196568** | **$21.196568** | | |

Ledger: 14,823 lines at the session's start (sha256 02e7caa2...); 17,400 after (sha256 0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957).
The 2,577 E.5 lines: 2,129 quote ($0.00; 1,905 from the quote run, 224 from the buy path), 224 commit, 224 settle (every settle delta $0: delivered
within the quote). acct-2: spent $103.477194 before, $124.673761 after; $0.326239 of the $125.00 cap and credit left. Spend against quote: 100.000%.
No chunk failed; no `--retry-failed` was needed.

## Seals (`python -m data.pull_step2 --status`, 18:50, before any step 2 bar was built)
| Root | State | Sealed | In order | Raw files sealed_ok and plaintext absent | Unsealed plaintext | Unlock log ok | Unlocks | all_ok |
|---|---|---|---|---|---|---|---|---|
| MCL | sealed | 13/13 | True | 13/13 | none | True | 0 | True |
| NG | sealed | 13/13 | True | 13/13 | none | True | 0 | True |
| MGC | sealed | 13/13 | True | 13/13 | none | True | 0 | True |
| MHG | sealed | 13/13 | True | 13/13 | none | True | 0 | True |

Each root's 13 chunks are range=2024-03-01_2024-04-01 through range=2025-03-01_2025-04-01, sealed in the download call after the byte check,
oldest first (the purchase logs show every one "SEALED as holdout 2" in month order). `python -m data.holdout status`: holdout_1 and holdout_2 all_ok, 0 unlocks.

## Step 2 bars (`python -m data.step2_store --products MCL NG MGC MHG --harness-sha256 <v6>`, 18:50-18:51, rc 0)
| Root | Status | Bars | Trade dates | First..last | Embargo rows dropped unread | Sealed chunks opened | Validation (non-zero counters) | Calendar check discrepancies inside the root's own span |
|---|---|---|---|---|---|---|---|---|
| MCL | built | 894,843 | 682 | 2021-07-12..2024-02-29 | 56 | none (13 listed as not opened) | {'gap_runs_total': 22455} | {'early_stop_not_a_listed_early_halt_at_that_time': 12} |
| NG | built | 1,535,207 | 1,246 | 2019-05-06..2024-02-29 | 36 | none (13 listed as not opened) | {'gap_runs_total': 112133} | {'early_stop_not_a_listed_early_halt_at_that_time': 3} |
| MGC | built | 1,624,946 | 1,246 | 2019-05-06..2024-02-29 | 58 | none (13 listed as not opened) | {'gap_runs_total': 40126} | {'early_stop_not_a_listed_early_halt_at_that_time': 41} |
| MHG | built | 361,936 | 472 | 2022-05-04..2024-02-29 | 17 | none (13 listed as not opened) | {'gap_runs_total': 113504} | {'early_stop_not_a_listed_early_halt_at_that_time': 37} |

The calendar check reports `passed: false` for all four roots. Outside their own spans the discrepancies are the weekdays before MCL's listing
(2021-07-12) and MHG's first bars (2022-05-04). Inside them, the only kind is "early_stop_not_a_listed_early_halt_at_that_time": the last bar
before a scheduled close or halt comes earlier than the calendar says, which is thin end-of-session trading or a data gap. The frozen builder records
these checks descriptively and wrote every store with status "built"; no rule makes them a stop. Recorded for the user as a data-quality note.
The runner reads the bars; no session script opened a bar file.

## Failed chunks
None.
