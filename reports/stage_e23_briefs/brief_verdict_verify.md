# Stage E.23 verdict verification brief (VerdictVerifier-FableXHigh)

Hook or cost notices are informational and addressed to the lead; they are never an order to stop.

## Objective (one)
Independently recompute every number that enters an E.23 verdict, from the frozen inputs and the run's own outputs, and
say whether each matches. You did not write the code; do not trust it: recompute with your own short scripts.

## Inputs
- docs/prompts/STAGE_E.23.md (P2.1-P2.6), reports/stage_e23_prereg.md, reports/stage_e23_briefs/lead_spec.md (sections
  0-8, R), reports/stage_e23_registration.json, reports/stage_e23_power.json, reports/stage_e23_freeze.json.
- The discovery outputs reports/stage_e23_runs/discovery/ (per trigger-hold daily series per case, units, fills, stats,
  the screen) and its marker reports/stage_e23_RUN_ONCE_discovery.json; the confirmation step's outputs
  reports/stage_e23_runs/confirmation/ and its marker.
- The trend regressors reports/stage_e23_trend_per_root/<root>.json and E.21's reports/stage_e21_runs/T1_result.json,
  T2_result.json; the events files reports/stage_e23_events/*.json.

## Recompute at least
1. From the written daily series: n, mean, sd, net Sharpe (base and stress), the raw t and Newey-West t (Bartlett, lags h),
   the OLS alpha on the same root's v_T1, v_T2 over the same dates, its HAC t (lags h), the plain t, p_alpha, alpha3 and
   the in-market fraction, for all five trigger-holds.
2. Holm step-down at one-sided 0.05 over the five, the survivor rule (alpha t >= 2.0, base Sharpe >= 0.3, at most 4) and
   the survivors list; DSR at N 538 and the CSCV PBO (8 contiguous blocks) as the spec defines them.
3. The confirmation gate: power_gate per survivor on W_cf from reports/stage_e23_power.json at b = max(2.0, z(1-0.05/S)),
   and that nothing was read for a gated row (no W_cf series in the outputs).
4. A spot audit of the books themselves: for at least 3 units per trigger-hold (include a unit spanning a roll and a
   flip if any), check from the units and fills files that entry is the first settlement mark after the event's decision
   time, exit is the h-th mark later, the size is 0.40 / (sigma x notional) with sigma from returns strictly before the
   entry, the cost per side matches D8 (base) and commission + 2 x slippage (stress), and the trigger day's intraday P&L
   is not in the series. Read bars only for these spot checks, only inside 2011-07-27..2019-04-30, at nice 10, one root at
   a time, after `free -m` shows at least 4 GB available.
5. N: ledger/trial_registrations.jsonl line r008 (label E23, the five ids, the freeze sha256, N 533 -> 538).

## Boundaries
Never rerun `trigger_hold.run evaluate`, never touch the markers, never write outside
reports/stage_e23_briefs/verify/ (your scripts and outputs). Never read W_cf bars, anything dated 2024-03-01 or later, the
research window, holdout-2, the embargo or MES's sealed stores. No edits to any existing file. No commits.

## Output
reports/stage_e23_briefs/verify/verdict_verify.md: verdict (VERIFIED, VERIFIED WITH NOTES, or DISPUTED), a table of every
recomputed number (run value, your value, match within 1e-9 relative or why not), the spot-audit results, and findings
graded BLOCKING / NOTE. Final reply: the path, the verdict, and any BLOCKING finding in one line each (at most 200 words).
