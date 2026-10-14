# Brief: VerdictVerifier-FableXHigh (Stage E.21 Step 5)

You are an independent verifier (a different model from the one that wrote the code and ran the
evaluation). Stage E.21 registered four tests (E21-T1..T4; N 528 -> 532) and evaluated each once with
multiday.run evaluate. Your job: recompute EVERY verdict number independently, with your own code,
WITHOUT reading the lead's statistics first.

## Order (binding)
1. Read the rules: docs/prompts/STAGE_E.21.md (F1-F8), reports/stage_e21_prereg.md,
   reports/stage_e21_briefs/lead_spec.md (sections 0-11 and A), reports/stage_e16_briefs/lead_spec.md
   sections 0-3 and 5, base_rules/README.md. You may read multiday/ to learn its OUTPUT FORMAT and file
   names, but write your computation from the spec, not by copying its logic.
2. Compute your own numbers (below) and write them to your private folder BEFORE opening any of
   reports/stage_e21_runs/*result*, *verdict*, *.md or the lead's notes. You may read the run's
   per-root input rows only where the spec says a number is an input (none for T1-T3; T4 takes H2 from
   reports/stage_e17_runs/H2_result.json).
3. Only then open the run's result and verdict files and compare.

## Recompute
- From the real stores (load them with base_rules.store.load_product through the E.17 run manifest
  reports/stage_e17_run_manifest.json and base_rules' calendars, settlement table and costs; these
  loaders are frozen E.16 code): for every one of the 17 roots, the marks MK and PS, the daily returns,
  the EWMA sigma (centre of mass 60, x261, EWMA-mean demeaning, strictly before d, 60-return warm-up),
  the rebalance and reference dates (last 6 trade dates rule, action and reference exclusions, fill
  guard), the T1 and T2 signals, the calendar-defined divisor S_M, holdings n, every fill (rebalance,
  roll legs) and its cost per case, the per-root daily values and the T1 and T2 daily series.
- T3 for NQ and RTY (day -2 = the month's second-to-last trade date, day +3; exclusions; S_u).
- T4 from your T2 and T3 series and H2's E.17 component series (H5's arithmetic: trailing 60 grid dates
  strictly before d, ddof 1, warm-up 60).
- For each test and each cost case: n, mean, sd, t, Newey-West t (lags 21 for T1, T2, T4; 5 for T3),
  p_t, p_nw, p = max; annualized Sharpe (sqrt 252); the circular block bootstrap interval (block 21,
  10,000 draws, numpy default_rng(20261014) fresh per test, percentile 2.5 / 97.5); Holm step-down at
  0.025 over the four base-case p values; PASS iff Holm rejects and Sharpe >= 0.3. Also total gross,
  total costs and costs as a share of gross, and fills by kind.
- Order of events: the registration line in ledger/trial_registrations.jsonl (label E21, ids, freeze
  sha256, time) precedes reports/stage_e21_RUN_ONCE.json's time, which precedes every result file's
  mtime; N = 532; the freeze manifest verifies (multiday.freeze_manifest verify).

## Compare and classify
For every number: run value, your value, absolute difference, status (MATCH within 1e-9 relative or
1e-12 absolute; else DIFFERENT with the cause found). Any difference that changes a verdict, or any
look-ahead, mis-specification or missing cost you find, is BLOCKING. Differences of rounding or
reporting only are NOTE.

## Limits
Compute at nice 10; load one root at a time; check `free -m` first and keep your peak under half the
available memory; at most one heavy job. Never write anything under reports/stage_e21_runs/, never
rerun `multiday.run evaluate`, never edit code, never register or commit, never touch live/, ops/,
ledger/ (read-only), REGISTRATION.md. Read nothing dated after 2024-02-29. Scripts and outputs go in
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/13fe2d4e-086f-4929-8325-9ef707bdf0cf/scratchpad/VerdictVerifier/
except your report.

## Output
reports/stage_e21_review_verdict.md: verdict line (VERIFIED / VERIFIED WITH NOTES / NOT VERIFIED), the
comparison table per test and case, findings (id VV-n | severity | detail | fix), and the checks run.
Return the path, a summary of at most 200 words, and anything you could not check.
