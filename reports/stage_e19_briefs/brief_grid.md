# Brief: GridCoder-OpusHigh (Stage E.19 Tasks 3-4 support, worker-high on opus)

Objective: write the grid runner and the aggregator for the E.19 funnel model, test them, run the full grid below,
and produce the machine-generated results. The lead owns every modelling choice (reports/stage_e19_briefs/sim_spec.md
section 6 and the lead decisions L-1..L-17 in reports/stage_e19_STATE.md); where this brief is ambiguous, take the
reading closest to its words, flag it in reports/stage_e19_briefs/grid_questions.md, and continue.

Use (read their docstrings and signatures; do not modify them): prop_econ/returns.py (build_shocks; ShockSet),
prop_econ/rules.py (load_rules, apply_readings with allow_unlisted, size_rules), prop_econ/vec.py (simulate_attempts,
simulate_xfas, Policy), prop_econ/assemble.py (fee_terms, draw_cycles / assemble_cycles, run_campaign,
campaign_quantiles). Rules come ONLY from reports/stage_e19_rules.json (status FINAL).

## Fixed settings (all jobs)
n_paths 20,000 attempts and 20,000 XFAs per pool; 20,000 cycles and 20,000 campaign replications per rule set;
attempt and XFA horizon 756 trading days; max_payouts 192; attempt cap 60 per cycle; campaign cap 400 purchases;
targets $5,000 and $10,000 of cumulative user payout cash; campaign slots 1 and 5. Seeds: one base seed 20261019;
the shock seed depends only on (phase, size, tail, direction, products, cost model, mode), so every edge, f, DLL
choice and payout path of a size sees the same shocks (common random numbers); the cycle and campaign index-draw
seeds depend only on (size, tail, direction, products, cost model, mode), so cycles are paired across f and edge.

## Headline grid (tail bootstrap, direction random, cost d8, mode continuous, products all five, payout policy
## "max" (keep_d 0), call-up per the file (discretionary = none), every rule at readings[0])
- size 50K, 100K, 150K; dll off/on (both phases); payout path standard/consistency;
- edge: zero_k1, zero_k3, and net Sharpe S in {0, 0.15, 0.3, 0.5, 0.75, 1.0};
- f in {0.05, 0.10, 0.15, 0.20, 0.25} (policy band) and {0.35, 0.50} (diagnostic; label them so);
- post hoc per rule set: pricing path standard / no_activation_fee; Back2Funded off (headline) / on.
- Campaigns: for the band f only, pricing both, Back2Funded off.

## Sensitivities (dll off, pricing both, Back2Funded off, f in the band, both payout paths, all sizes, unless said)
- tail normal: all eight edges.
- direction long: zero_k1.  cost model wall: zero_k1, zero_k3.
- mode integer, one product at a time (NQ, CL, GC, ZN, 6E): zero_k1 and S 0.5.
- payout policy keep_d 0.5: zero_k1, S 0.5, S 1.0.
- call-up after_n_payouts n = 1 and n = 3 (apply_readings allow_unlisted): zero_k1 and S 0.5.
- UNSOURCED / CONFLICT readings, each alone at its alternative: scaling_boundary "upper" (all sizes),
  global.combine_consistency_inclusive true: zero_k1 and S 0.5 at f 0.10 and 0.25.
- Post hoc on the headline (no new simulation): payout transfer fee $30 per payout (ACH/wire); voluntary close at the
  horizon for 0.9 x min(0.5 x end balance, 5000) on XFAs alive at the horizon; API fee excluded; copy-traded five
  accounts = five times one cycle's cash flows (same draws).

## Wallet accounting (every rule set)
cash out = Combine purchases (P and R payments), activation fees, Back2Funded fees, and the API subscription
$14.50 per started 21-trading-day period of operation (global.api_access_monthly_usd; one per user: per cycle in the
cycle metrics, per elapsed campaign period in campaigns); cash in = profit_split_trader x payout gross. Payout
transfer fee $0 in the headline (Wise/Aeropay). Report every figure with the API fee included, and the cycle mean net
also without it.

## Metrics per rule set (one record)
Attempts: P(pass), mean length, timeout share, attempts per pass. XFAs: P(any payout), mean user cash per XFA, mean
n payouts, mean days to first payout given one, end-reason shares (breach, call-up, payout limit, horizon), share
alive at the horizon, overflow count, mean XFA life. Cycles: mean net and its Monte Carlo SE, P5 / P50 / P95 of net,
P(no payout in the cycle) (= all fees lost), P(cycle reaches an XFA), mean purchases, mean total fees (by type),
expected net per Combine purchase = mean net / mean purchases, mean trading days from cycle start to the first payout
given one, mean cycle length. Per funded XFA: mean user cash - activation fee. Campaigns (slots 1 and 5, both
targets): P50 and P80 of purchases, total fees and elapsed trading days at the first crossing, share not reached.
Derived (aggregator): the break-even net Sharpe per (size, path, dll, pricing) at each f and at the best f, by linear
interpolation of cycle mean net over S in {0 .. 1.0}; "< 0" when the net is already positive at S = 0, "> 1.0" when
still negative at 1.0; the effective net Sharpe of zero_k1 and zero_k3 (from the pooled cost mix actually traded,
report how you computed it); the in-simulation optimum f in the band per (size, path, dll, pricing, edge) with its SE
and the paired SE of the difference to the runner-up (paired cycles share index draws); the same for the diagnostic
f values separately (does the mean keep rising above 0.25?).

## Outputs
- prop_econ/grid.py (job list, one job = one attempt pool + its XFA pools + all post hoc rule sets; CLI
  `python -m prop_econ.grid run --workers N`; resumable: one JSON per job in reports/stage_e19_runs/, skipped when
  present and complete; progress lines to reports/stage_e19_briefs/grid_run.log); prop_econ/report.py (aggregator:
  reports/stage_e19_results.json with every record and the derived quantities, and
  reports/stage_e19_briefs/results_tables.md with compact tables: T1 headline per size x path x dll x pricing at
  zero_k1 and S 0.5 at the best band f; T2 cycle mean net (SE) by f x edge per size and path (dll off, cheaper
  pricing); T3 break-even S; T4 campaigns at the best f for zero_k1, S 0.3, 0.5, 1.0; T5 every sensitivity against
  its headline twin; T6 the optimum f with SEs; T7 diagnostic f). Round dollars to whole dollars, probabilities to 3
  decimals; every table states its configuration.
- tests/test_prop_econ_grid.py: job enumeration counts, seed independence from f/edge/dll/path, resumability,
  break-even interpolation and optimum selection on synthetic records, wallet accounting (API periods, payout fee).
- Run: check `free -g` first; `nice -n 10`; at most 8 worker processes (CLAUDE.md: half the cores, never more than
  8); time a single job first and log the estimate; then the full grid detached
  (`setsid nohup ... > reports/stage_e19_briefs/grid_run.log 2>&1 &`), then the aggregator.

Boundaries: write only prop_econ/grid.py, prop_econ/report.py, tests/test_prop_econ_grid.py, reports/stage_e19_runs/,
reports/stage_e19_results.json, reports/stage_e19_briefs/results_tables.md, grid_run.log, grid_questions.md. Do not
modify other prop_econ modules (report a bug instead, with a failing example), frozen code, or any data. Run only
tests/test_prop_econ_*.py, never the full suite; ruff clean. Do not spawn workers. Do not commit.

Return (three things): the paths; a summary of at most 200 words (job counts, wall time, any failures, the headline
zero-edge and S 0.5 cycle means per size at the best f); anything unfinished and your grid questions.
