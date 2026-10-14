# Brief: FreezeReviewer-FableXHigh (Stage E.21 Step 3)

You are an independent, adversarial reviewer (a different model from the one that wrote the work). The
stage's lead is Opus; the code was written by MultidayCoder-OpusXHigh. Nothing has been registered and
no bar of any real store has been read. Your review is BLOCKING for registration.

## Objective
Find every way the E.21 freeze could produce a wrong verdict, before it is registered: a published rule
mis-specified, look-ahead, wrong chaining across contract rolls, omitted costs, wrong dates, wrong
statistics, or a run discipline gap.

## Read (by section; grep and line ranges, never whole large files)
- docs/prompts/STAGE_E.21.md (FIXED DESIGN F1-F8, SCOPE): binding first.
- reports/stage_e21_prereg.md and reports/stage_e21_briefs/lead_spec.md (including section A, the
  literature amendments): the lead's frozen declarations.
- reports/stage_e21_briefs/spec_trend.md, spec_tom.md, spec_post2010.md: the Step 1 literature checks
  (verbatim quotes from the primary sources).
- reports/stage_e16_briefs/lead_spec.md sections 0-3 and 5; base_rules/README.md (conventions reused).
- multiday/ (all modules), tests/test_multiday_*.py, reports/stage_e21_briefs/multiday_build.md and
  calendar_counts.md.

## Check at least
1. Spec vs prompt vs papers: TSMOM-12 lookback and sign, the EWMA estimator (centre of mass 60,
   annualization, demeaning, strictly-before timing, warm-up), the 0.40 target, the equal-weight average,
   the 1/3/12 blend, the month-end rebalance day, the turn-of-month days -2..+3, T4's equal-risk
   combination as H5 (trailing 60 grid dates strictly before d, warm-up), H2 used exactly as frozen.
2. Look-ahead: sigma, every signal, every reference date, the divisor S_M and S_u, eligibility of
   rebalance and entry dates (no use of the fill bar's own prices or any later bar), the store boundary.
3. Chaining: daily returns and lookbacks across splices and across the 2019-04-30 / 2019-05-06 store
   boundary; no return ever taken across two contracts; roll legs at the right bars; P&L per contract
   versus base_rules.sim.
4. Costs: every fill (rebalance, entry, exit, each roll leg) pays per side; the event window, fill guard,
   R-B2 uncalibrated buckets; |delta n| x cost in capital units; stress and 1.5 x cases.
5. Series and statistics: series dates (calendar-defined, zeros on flat days), t, Newey-West (lags 21 /
   5), p = max rule, Holm step-down at 0.025, Sharpe annualization sqrt(252), the bootstrap (circular
   blocks of 21, 10,000 draws, seed 20261014), the PASS rule.
6. Run discipline: the marker reports/stage_e21_RUN_ONCE.json is written with O_EXCL before any bar row
   is read; every pre-marker refusal (freeze file changed, unregistered, wrong freeze sha256, output
   exists, store sha256); nothing dated after 2024-02-29 can be read; holdout, embargo, research and MES
   stores refused; no edit of any frozen file (base_rules/, screening/, data/, earlier freezes).
7. Tests: do they test what they claim (a planted future bar must not move a position; roll costs
   charged; chaining; dates)? Name any claim no test covers.

## Allowed
Read code, spec and tests; run `nice -n 10 uv run python -m pytest -q -p no:cacheprovider
tests/test_multiday_*.py`; write throwaway scripts and synthetic data in your private folder
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/13fe2d4e-086f-4929-8325-9ef707bdf0cf/scratchpad/FreezeReviewer/.

## Not allowed
Reading any row of a real store (no `evaluate`, no bar read from data/), editing multiday/, tests/ or any
report other than your output, registering, committing, touching live/, ops/, ledger/, REGISTRATION.md.

## Output
reports/stage_e21_review_freeze.md: a verdict line (APPROVE / APPROVE WITH FIXES / BLOCK), then one row
per finding: id FR-n | severity (BLOCKING = would make a verdict number wrong or break the run
discipline; SHOULD FIX = could plausibly mislead or is untested; NOTE) | file:line | the concrete failure
scenario | the proposed fix. Then the list of checks you ran and what they showed. Return the path, a
summary of at most 200 words, and anything you could not check.
