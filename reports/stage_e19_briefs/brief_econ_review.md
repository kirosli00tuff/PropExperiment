# Brief: EconReviewer-FableXHigh (Stage E.19 Task 5b, worker-xhigh on fable)

Objective: independently check the E.19 funnel model and recompute its headline numbers. You did not write it;
assume it may be wrong. Grade findings BLOCKING (changes a headline number, the zero-edge sign, the break-even edge,
the best account size or path, or a recommendation), SHOULD FIX, or NOTE.

Inputs: the lead's model reports/stage_e19_briefs/sim_spec.md and decisions L-1..L-17 (and later) in
reports/stage_e19_STATE.md; the rules reports/stage_e19_rules.json (FINAL; reviewed separately by RulesReviewer for
quotes, so take its values as given, but check the code uses them as the spec says); the code prop_econ/returns.py,
rules.py, funnel.py, vec.py, assemble.py, grid.py, report.py and tests/test_prop_econ_*.py; the returns summary
reports/stage_e19_returns_summary.json; the stores data/processed_step2/{NQ,CL,GC,ZN,6E}/*.parquet (read only the
columns you need; never print rows; no head/cat/less on a data file; no other data file, no data/sealed).

Phase A, blind (do this first, and write reports/stage_e19_verify/recompute.json with a timestamp BEFORE you open
reports/stage_e19_results.json, reports/stage_e19_briefs/results_tables.md or anything under reports/stage_e19_runs/):
1. Returns: rebuild the per-path day-session table from the stores with your own code (window from
   screening/vehicles.py D6_SESSIONS; same keep rule as the summary states); check the demeaned close has mean 0 per
   path, sigma_full matches the summary, the w <= min(0, z) property, and the D8 round trips per vehicle against
   reports/stage_e2a_costs.json.
2. Your own simulator, written from sim_spec.md sections 2 to 5 and the FINAL rules, without importing
   prop_econ.funnel, vec, assemble, grid or report (numpy; you may reuse your own returns table and your own
   bootstrap). Recompute, for 50K, 100K and 150K, payout paths standard and consistency, DLL off, pricing standard,
   API fee included, payout policy max, edges zero (k = 1) and net Sharpe 0.5, f in {0.05, 0.10, 0.15, 0.20, 0.25}:
   P(pass), mean user cash per XFA, P(any payout per XFA), cycle mean net with its SE, P(no payout per cycle), mean
   purchases per cycle, net per purchase. At least 10,000 paths each. Record seeds and code paths.
3. Hand paths: build at least four short deterministic paths by hand (a pass then a payout; a fail, rebill and reset
   with a credit; a floor lock then the floor at 0 after a payout; a Consistency refusal) and check prop_econ's
   scalar reference returns your hand values to the cent.
Phase B, compare: open the lead's results; compare each recomputed number with the grid's, within 3 combined Monte
Carlo SEs (state the SEs); explain every difference beyond that. Then review the code against the spec and the rules:
the daily step (vehicle choice, n >= 1, lot cap and tier timing, DLL, intraday breach, trailing and locks, the floor
after the first payout), the payout eligibility and amounts on both paths, the fee accounting (rebills, credits,
resets, activation, Back2Funded, API periods, the split), the campaign counting and the 5-XFA cap, common random
numbers, the break-even interpolation and the optimum's SE. Check the zero-edge case really has zero gross drift
(demeaned, random direction) and that the edges are net of costs.

Output: reports/stage_e19_review.md (findings table: id ER-n, grade, area, finding, evidence, suggested fix; then
sections for Phase A, the comparison table, and the code review) and reports/stage_e19_verify/ (your code, logs,
recompute.json). Write nothing else. Compute: nice -n 10, at most 4 processes, check free memory first, one heavy
computation at a time. Do not modify prop_econ/, tests or any reviewed file. Do not spawn workers. Do not commit.

Return (three things): the path; a summary of at most 200 words (counts by grade, each BLOCKING finding in one line,
whether the headline numbers reproduce); anything unfinished.
