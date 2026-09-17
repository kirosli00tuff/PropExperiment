# Funnel null baseline (Stage B, Task 3)

Generated 2026-09-17T07:39:21.605915+00:00 · seed 20260917 · `uv run python -m funnel.run_null_baseline` · machine-readable: `reports/funnel_null_baseline.json`

This is the zero-edge benchmark: how a trader with no market edge fares in Topstep's Combine → XFA funnel at a fixed sizing (2 micros, 1 round turn/day), computed before any strategy exists. A real strategy has to beat these numbers to show it has edge.

Over 64,000 simulated 12-month (252-trading-day) careers:
- Combine pass rate per attempt: 18.1% (both paths)
- P(first payout within 12 months): 66.3% (Standard) / 41.9% (Consistency)
- Median months to first payout, given a payout: 5.0 (Standard) / 5.9 (Consistency)
- Mean monthly net income: $1 (Standard) / -$28 (Consistency); P(net income > 0): 26.3% / 20.4%
- Right tail (monthly net income p80/p90/p95): $43/$199/$388 (Standard), $2/$128/$292 (Consistency)

Reading: at this sizing, a zero-edge trader roughly breaks even on average on the Standard path and loses money on average on the Consistency path, with a lottery-like right tail. The most favorable null critical values used by the power gate come from the 6-micro (p80, p90) and 7-micro (p95) 1 round-turn/day configurations, not the 2-micro headline sizing shown above. The size ladder was extended to 30 micros after this report was first written; the critical-value table below reflects the extended grid.

## Headline: zero-edge trader, 2 micros, 1 round turn/day, 12 months (252 trading days)

| Metric | Standard path | Consistency path |
|---|---|---|
| Runs | 64,000 | 64,000 |
| Combine pass rate per attempt | 18.1% | 18.1% |
| Combine pass rate per resolved attempt | 19.6% | 19.6% |
| Runs passing ≥1 Combine in 12 months | 91.4% | 91.4% |
| Combine attempts per run (mean) | 12.6 | 12.6 |
| P(first payout within 12 months) | 66.3% | 41.9% |
| Months to first payout, p10 / p50 / p90 (given a payout) | 1.8 / 5.0 / 10.1 | 2.1 / 5.9 / 10.6 |
| Monthly gross payouts, mean | $121 | $92 |
| Monthly fees, mean | $120 | $120 |
| Monthly net income, mean | $1 | -$28 |
| Monthly net income, p10 | -$121 | -$129 |
| Monthly net income, p25 | -$102 | -$113 |
| Monthly net income, p50 | -$76 | -$92 |
| Monthly net income, p75 | $7 | -$23 |
| Monthly net income, p80 | $43 | $2 |
| Monthly net income, p90 | $199 | $128 |
| Monthly net income, p95 | $388 | $292 |
| P(net income > 0) | 26.3% | 20.4% |
| XFAs activated per run (mean) | 2.27 | 2.27 |
| XFA payouts per run (mean) | 1.62 | 0.79 |
| XFA breaches per run (mean) | 2.10 | 1.99 |
| Runs ever reaching 5 live XFAs | 0.0% | 0.1% |

## Correlated blowups across the XFA cluster

Counted on days when ≥2 XFAs were live at the open and at least one breached. 'Independent' is the counterfactual where every account draws its own market.

| Metric | Standard (correlated) | Standard (independent) | Consistency (correlated) | Consistency (independent) |
|---|---|---|---|---|
| Breach days with ≥2 live XFAs | 14,828 | 9,769 | 20,749 | 16,925 |
| …share where ≥2 XFAs breached the same day | 21.9% | 2.5% | 20.4% | 1.8% |
| …share where every live XFA breached | 19.8% | 2.4% | 17.7% | 1.6% |
| Runs with a same-day multi-XFA breach | 5.0% | 0.4% | 6.5% | 0.5% |
| Monthly net income, mean | $1 | -$7 | -$28 | -$26 |
| Monthly net income, p80 | $43 | $47 | $2 | $27 |
| Breach days (≥2 live) with exactly 1 breached | 11,574 | 9,524 | 16,516 | 16,624 |
| Breach days (≥2 live) with exactly 2 breached | 3,144 | 243 | 4,083 | 301 |
| Breach days (≥2 live) with exactly 3 breached | 103 | 2 | 139 | 0 |
| Breach days (≥2 live) with exactly 4 breached | 6 | 0 | 10 | 0 |
| Breach days (≥2 live) with exactly 5 breached | 1 | 0 | 1 | 0 |

"Correlated" means every live account in a run trades against the same market draw each day — all XFAs a trader holds see the identical daily move, because in reality one person trades one market with multiple accounts. "Independent" is a counterfactual where each account instead draws its own market, as if the accounts belonged to unrelated traders.

Counted on days when at least 2 XFAs were live at the open and at least one breached: on the Standard path, 21.9% of those days saw at least 2 XFAs breach together under the correlated draw, versus 2.5% under independent draws; on the Consistency path it's 20.4% versus 1.8%. At the run level, 5.0% of Standard runs (versus 0.4% independent) and 6.5% of Consistency runs (versus 0.5% independent) had a same-day multi-XFA breach.

Caveat: a zero-edge trader rarely holds many XFAs at once — only about 0.03% of Standard runs and 0.1% of Consistency runs ever reach 5 live XFAs — so the full 5-account cluster is sparsely populated under the null, and the correlation effect above is measured only on the days (≥2 live XFAs, at least one breached) where it can occur at all. It will matter more for strategies that manage to keep accounts alive longer and stack more of them; see reports/power_gate.md.

## Sample-size stability

**Standard path:** stable at N = 16,000. Rule: `|m(N)-m(next)| <= tol AND 1.96*SE(N) <= tol for every metric`; rate tolerance ±1 pp, USD tolerance max($10, 2%). Cells are estimate ± 1.96 × Monte Carlo SE.

| N | pass rate/attempt | P(payout ≤12m) | P(multi-breach run) | net mean | net median | net p80 | stable vs next |
|---|---|---|---|---|---|---|---|
| 1,000 | 19.1% ± 0.7% | 69.5% ± 2.9% | 4.5% ± 1.3% | $14 ± $15 | -$68 ± $5 | $64 ± $28 | no |
| 2,000 | 18.4% ± 0.5% | 68.5% ± 2.0% | 4.4% ± 0.9% | $9 ± $11 | -$73 ± $4 | $45 ± $17 | no |
| 4,000 | 18.2% ± 0.3% | 68.0% ± 1.4% | 4.5% ± 0.6% | $3 ± $8 | -$76 ± $2 | $36 ± $9 | no |
| 8,000 | 18.2% ± 0.2% | 66.9% ± 1.0% | 4.9% ± 0.5% | $4 ± $5 | -$76 ± $1 | $39 ± $7 | no |
| 16,000 | 18.1% ± 0.2% | 66.5% ± 0.7% | 4.8% ± 0.3% | $4 ± $4 | -$76 ± $1 | $44 ± $5 | yes |
| 32,000 | 18.1% ± 0.1% | 66.0% ± 0.5% | 4.9% ± 0.2% | $1 ± $3 | -$76 ± $0 | $43 ± $4 | yes |
| 64,000 | 18.1% ± 0.1% | 66.3% ± 0.4% | 5.0% ± 0.2% | $1 ± $2 | -$76 ± $0 | $43 ± $3 | — |

**Consistency path:** stable at N = 16,000. Rule: `|m(N)-m(next)| <= tol AND 1.96*SE(N) <= tol for every metric`; rate tolerance ±1 pp, USD tolerance max($10, 2%). Cells are estimate ± 1.96 × Monte Carlo SE.

| N | pass rate/attempt | P(payout ≤12m) | P(multi-breach run) | net mean | net median | net p80 | stable vs next |
|---|---|---|---|---|---|---|---|
| 1,000 | 19.1% ± 0.7% | 45.5% ± 3.1% | 7.2% ± 1.6% | -$13 ± $15 | -$88 ± $5 | $12 ± $22 | no |
| 2,000 | 18.4% ± 0.5% | 43.4% ± 2.2% | 6.8% ± 1.1% | -$21 ± $10 | -$92 ± $3 | $1 ± $11 | no |
| 4,000 | 18.2% ± 0.3% | 43.0% ± 1.5% | 6.5% ± 0.8% | -$26 ± $7 | -$92 ± $1 | -$1 ± $6 | no |
| 8,000 | 18.2% ± 0.2% | 42.2% ± 1.1% | 6.6% ± 0.5% | -$26 ± $5 | -$92 ± $0 | $1 ± $6 | no |
| 16,000 | 18.1% ± 0.2% | 42.1% ± 0.8% | 6.7% ± 0.4% | -$26 ± $3 | -$92 ± $0 | $3 ± $4 | yes |
| 32,000 | 18.1% ± 0.1% | 41.7% ± 0.5% | 6.4% ± 0.3% | -$28 ± $2 | -$92 ± $0 | $2 ± $3 | yes |
| 64,000 | 18.1% ± 0.1% | 41.9% ± 0.4% | 6.5% ± 0.2% | -$28 ± $2 | -$92 ± $0 | $2 ± $2 | — |

## Sensitivity: size × round turns per day (correlated, 32,000 runs)

| Path | Micros | RT/day | Pass/attempt | P(payout ≤12m) | Net mean | Net p50 | Net p80 | Net p90 | P(net>0) | XFA breaches/run |
|---|---|---|---|---|---|---|---|---|---|---|
| consistency | 1 | 1 | 14.7% | 19.5% | -$61 | -$76 | -$68 | -$30 | 7.0% | 0.50 |
| consistency | 1 | 2 | 12.9% | 17.2% | -$65 | -$76 | -$68 | -$34 | 5.4% | 0.47 |
| consistency | 1 | 4 | 9.2% | 11.2% | -$70 | -$76 | -$68 | -$62 | 3.2% | 0.36 |
| consistency | 2 | 1 | 18.1% | 41.7% | -$28 | -$92 | $2 | $129 | 20.3% | 1.98 |
| consistency | 2 | 2 | 16.7% | 38.3% | -$42 | -$96 | -$11 | $91 | 17.9% | 1.92 |
| consistency | 2 | 4 | 14.0% | 29.8% | -$63 | -$100 | -$38 | $24 | 12.8% | 1.66 |
| consistency | 3 | 1 | 19.5% | 53.5% | $12 | -$92 | $88 | $304 | 29.8% | 3.66 |
| consistency | 3 | 2 | 18.0% | 49.7% | -$18 | -$111 | $59 | $240 | 26.6% | 3.65 |
| consistency | 3 | 4 | 15.2% | 41.1% | -$57 | -$129 | -$2 | $118 | 19.7% | 3.20 |
| consistency | 5 | 1 | 18.4% | 60.8% | $27 | -$107 | $185 | $477 | 33.7% | 6.44 |
| consistency | 5 | 2 | 16.9% | 56.9% | -$23 | -$135 | $120 | $376 | 28.8% | 6.39 |
| consistency | 5 | 4 | 14.5% | 48.3% | -$89 | -$188 | $10 | $215 | 21.2% | 5.72 |
| consistency | 6 | 1 | 17.2% | 60.5% | $5 | -$126 | $178 | $473 | 31.8% | 7.30 |
| consistency | 7 | 1 | 15.6% | 58.6% | -$40 | -$162 | $133 | $424 | 28.8% | 7.92 |
| consistency | 8 | 1 | 14.6% | 56.6% | -$74 | -$191 | $103 | $391 | 26.8% | 8.21 |
| consistency | 10 | 1 | 12.7% | 52.8% | -$145 | -$248 | $31 | $298 | 22.3% | 8.60 |
| consistency | 15 | 1 | 9.8% | 43.6% | -$279 | -$362 | -$112 | $122 | 13.4% | 8.45 |
| consistency | 20 | 1 | 8.3% | 37.9% | -$369 | -$448 | -$203 | -$18 | 9.6% | 8.32 |
| consistency | 30 | 1 | 6.1% | 26.5% | -$509 | -$583 | -$358 | -$203 | 4.2% | 7.35 |
| standard | 1 | 1 | 14.7% | 33.8% | -$53 | -$72 | -$58 | -$11 | 9.1% | 0.58 |
| standard | 1 | 2 | 12.9% | 30.4% | -$60 | -$72 | -$64 | -$29 | 6.9% | 0.54 |
| standard | 1 | 4 | 9.2% | 21.3% | -$67 | -$72 | -$68 | -$52 | 4.0% | 0.40 |
| standard | 2 | 1 | 18.1% | 66.0% | $1 | -$76 | $43 | $199 | 26.4% | 2.10 |
| standard | 2 | 2 | 16.7% | 64.5% | -$18 | -$80 | $20 | $142 | 23.1% | 2.02 |
| standard | 2 | 4 | 14.0% | 55.4% | -$43 | -$88 | -$17 | $66 | 17.1% | 1.73 |
| standard | 3 | 1 | 19.5% | 77.2% | $83 | -$49 | $198 | $459 | 39.7% | 3.79 |
| standard | 3 | 2 | 18.0% | 75.1% | $45 | -$64 | $147 | $361 | 35.9% | 3.75 |
| standard | 3 | 4 | 15.2% | 67.8% | -$8 | -$91 | $59 | $234 | 27.4% | 3.27 |
| standard | 5 | 1 | 18.4% | 79.2% | $177 | -$34 | $401 | $817 | 46.0% | 6.56 |
| standard | 5 | 2 | 16.9% | 76.8% | $105 | -$70 | $300 | $651 | 41.1% | 6.48 |
| standard | 5 | 4 | 14.5% | 70.4% | $9 | -$118 | $157 | $418 | 31.9% | 5.78 |
| standard | 6 | 1 | 17.2% | 76.9% | $170 | -$57 | $420 | $874 | 44.0% | 7.40 |
| standard | 7 | 1 | 15.6% | 73.6% | $132 | -$98 | $392 | $860 | 39.8% | 8.00 |
| standard | 8 | 1 | 14.6% | 71.3% | $101 | -$130 | $361 | $849 | 37.4% | 8.27 |
| standard | 10 | 1 | 12.7% | 66.8% | $30 | -$199 | $290 | $771 | 32.1% | 8.64 |
| standard | 15 | 1 | 9.8% | 56.4% | -$133 | -$330 | $70 | $531 | 22.6% | 8.48 |
| standard | 20 | 1 | 8.3% | 49.8% | -$244 | -$420 | -$82 | $344 | 17.2% | 8.34 |
| standard | 30 | 1 | 6.1% | 35.2% | -$436 | -$559 | -$304 | -$62 | 8.8% | 7.35 |

## Sensitivity: bootstrap mean block length (headline size)

| Path | Mean block (days) | Pass/attempt | P(payout ≤12m) | Net mean | Net p80 | P(multi-breach run) |
|---|---|---|---|---|---|---|
| standard | 1 | 18.3% | 66.8% | $9 | $59 | 5.9% |
| standard | 5 | 18.1% | 66.0% | $1 | $43 | 4.9% |
| standard | 21 | 18.1% | 65.3% | -$1 | $37 | 4.7% |
| consistency | 1 | 18.3% | 40.3% | -$26 | $1 | 6.8% |
| consistency | 5 | 18.1% | 41.7% | -$28 | $2 | 6.4% |
| consistency | 21 | 18.1% | 41.9% | -$30 | $3 | 6.4% |

## Most favorable null (critical values used by the power gate)

| Path | Quantile | Monthly net | at micros | RT/day |
|---|---|---|---|---|
| standard | p80 | $420 | 6 | 1 |
| standard | p90 | $874 | 6 | 1 |
| standard | p95 | $1,423 | 7 | 1 |
| consistency | p80 | $185 | 5 | 1 |
| consistency | p90 | $477 | 5 | 1 |
| consistency | p95 | $829 | 6 | 1 |

## Assumptions and limits

- Null generator: sign-randomized stationary block bootstrap (mean block length 5 trading days) resampled from 310 research-slice RTH sessions (2025-04-01 to 2026-06-12); RTH session move sd is $283.62 per micro, and the historical long drift of +13.65 ticks/session is removed by the sign-randomizing fair coin.
- Sizing: the rule targets a daily RTH sd of about 25% of the $2,000 Maximum Loss Limit (about $500); 2 micros (2 × $283.62 = $567.24 daily sd) is the closest integer-micro fit to that target.
- Horizon: 252 trading days per run, treated as 12 months of 21 trading days each.
- Costs: $1.22 round-turn commission ($0.61/side/micro) — a blocking TODO to reconfirm at checkout — plus a two-day slippage calibration that is a lower bound (excludes latency, adverse selection, and queue position).
- Fees: Standard plan $49/month for the Combine, $149 one-time XFA activation, $14.50/month API fee (per the help center as of 2026-09-16; flagged to reconfirm in Stage A.2); a failed Combine restarts as a new billed month.
- Payouts are gross (no profit split applied); the payout policy is greedy (withdraws the maximum allowed as soon as eligible); one Combine attempt at a time; max 5 XFAs live per trader.
- Not modeled: XFA activation delay, LFA call-up, inactivity rules, the optional Daily Loss Limit plan, and taxes.
- Sample size: the largest ladder rung, N = 64,000 runs; both paths reach Monte Carlo stability at N = 16,000 (per the tolerance rule in the stability tables above).
- Runtime: this baseline took about 1,946 seconds (roughly 32 minutes) to generate, plus 553 seconds (about 9 minutes) for the later size-ladder extension to 6-30 micros — 2,499 seconds (about 42 minutes) in total.
- Rules conflicts flagged in Stage A.1 are still encoded at the stricter reading in every case (e.g. Combine consistency 50% vs. 55%); full list in `rules/xfa_rules.py`.
