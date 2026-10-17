
Trials not in the table: cp1-01 6S, cp1-01 6N, cp2-01 6N (listed not run, tier excluded; records
present with status excluded_before_screening, label coverage_below_0.95; not covered); cp2-01 6S
and cp3-01 6N (listed run, Tier B; records excluded_before_screening on the confirmation-window
coverage check, no series; classed inconclusive, blocking).

Coverage pattern of the 6S and 6N records (expected / present / ratio): cp1 6S 38528 / 35485 /
0.9210 and cp1 6N 38528 / 35323 / 0.9168 (listed excluded); cp2 6S 552583 / 516011 / 0.9338 and
cp2 6N 552583 / 510913 / 0.9246 (6N listed excluded, 6S listed run); cp3 6S 473295 / 449710 / 0.9502
(run, passes) and cp3 6N 473295 / 444013 / 0.9381 (listed run, excluded); ldnrev 6S 76148 / 73967 /
0.9714 (run). The ratios are taken from the records; no store was read.

## Notes (none bears on a figure)

- **N0-a.** The marker's not_run is [] and members 30: the runner was given no not-run declaration
  for K3 (R-E22-A9's only declaration is K8-wkndbtc-01) and processed all 30 members; the three
  listed-excluded trials were excluded by its coverage check and the verdict ignores their records,
  as the brief's item 0 allows ("a not-run record, if any, carries exactly the declared label").
- **N4-a (classification of cp2-01 6S and cp3-01 6N).** The verdict classes the two run trials
  without a series as inconclusive and blocking, so K3 gets no statement. This follows the written
  criteria: NULL_CRITERIA_E 6 makes any member that neither passes nor meets both null conditions
  inconclusive (zero trips included), and section 1's only exception is the "inconclusive by design"
  label declared in the hashed list before the run; L-E5-5 covers trials listed not run, which these
  were not. Both were listed run: true with "power sufficient" from the research window. Whether a
  confirmation-window coverage exclusion (the harness's data-quality rule, not a P&L outcome) should
  form a not-covered class of its own is a lead decision that was not taken before the run; this
  report does not take it.
- **N4-b (resolution table).** The per-exposure table names the two blocking trials nowhere: 6N
  reads fewest_trips null, largest null, not_covered [cp1-01 6N, cp2-01 6N], as if 6N had no run
  trial, although cp3-01 6N was run and returned inconclusive; 6S lists cp1-01 6S only. They appear
  in statement.blocking. A reader of the resolution table alone would not see them.
- **N4-c (the word "covered").** statement.covered (27) is the code's "run and not by design" set
  and includes the two inconclusive trials; in NULL_CRITERIA_E 1's sense ("members ... not covered")
  nothing is covered because no statement is made. No statement text is affected.
- **N3.** The PBO blocks use 8 x 148 = 1184 of the 1191 union dates (D.1b's `_blocks`); the last 7
  dates enter no block. Frozen definition, not a discrepancy.
- **N3-b.** E[max SR] differs at 3.7e-10 relative between funnel's `_norm_ppf` (rational
  approximation) and statistics.NormalDist.inv_cdf; within the brief's 1e-9.

## Not checked

- No bar store was read (brief): the series-to-trips link is verified exactly; trips-to-bars, the
  coverage ratios, the start rule and the roll blackouts are taken from the records.
- The event-window membership of the 207 cp2/cp3 fills was inferred by matching their cents to the
  table's event_window_side_ticks, not checked against the release calendar (sha 839f2437...).
- The 11:30 CT flatten on the 14 dates is reported as the harness applied it (close_reason and CT
  close minute in the trip files); the rule itself was not re-derived.
- registry_current_n = 533 is the verdict's own check (program_n_check.equal true); the registry was
  not re-read.
- p_upper's definition is D.1f's frozen one-sided p, accepted as given.
- screening/stage_e_verdict.py was not run (brief).

## Files

- This report: reports/stage_e22_verify_k3.md
- Code and figures: reports/stage_e22_briefs/verify_k3/verify_k3.py, figures.json; extra_checks.py,
  extra_checks.json; event_cost_check.py, event_cost_check.json; table_trials.md.
