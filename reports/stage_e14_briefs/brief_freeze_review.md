# Brief: FreezeReviewer-FableXHigh (Stage E.14 Task 4: independent review before the freeze commits)

You are an independent, adversarial reviewer. A different model (Opus) wrote everything you review. Your job is
to find what is wrong before it is frozen: once committed, nothing here may change. The user is asleep; do not ask
questions. Read by section (grep, line ranges); never load a large JSON or log whole.

## What you review (paths; the lead's merge of harness v10 is in the main checkout, uncommitted)
1. Test C2 is NOT frozen: it stopped at its power rule before any freeze (reports/stage_e14_gex.md: the terms
   ruling, the single fetch, the lag-1 timing rule, the count 135 < 200, the calendar-free bound 146). Review that
   stop and the terms and timing rulings; the C2 draft is reports/stage_e13_prereg_gexmom.md (section 7's stop).
   v10 still contains the es2011 plan and screening/stage_e14_c2.py as inert code with E14_SESSION_CAP_USD = 0.00:
   check nothing in v10 can buy ES or run C2 tonight.
2. reports/stage_e14_prereg_C1.md (test C1) against its draft reports/stage_e13_prereg_ngrepl.md, the annex
   reports/stage_e13_ng_replication_draft.md (sections 2-11, rulings C1-C21) and V25 (item 1), V26.
3. Harness v10: `git diff HEAD --stat` and `git diff HEAD -- <file>` per file (data/config.py, data/pull_step2.py,
   the hist store and calendar modules, data/stage_e_bars.py, screening/harness_freeze.py,
   screening/stage_e14_c2.py, screening/trial_registry.py, their tests), and reports/stage_e14_v10_notes.md.
4. C1's code: c1_replication/ and reports/stage_e14_c1code_notes.md.
5. The inputs the freezes hash: the calendars reports/stage_e14_cal_*.json (and their copies under
   data/calendars/hist2010/), reports/stage_e14_calendars.md, reports/stage_e14_probe.md, reports/stage_e14_gex.md,
   reports/stage_e14_c1_e12_state_manifest.json.
6. The stage prompt docs/prompts/STAGE_E.14.md (Scope, Guardrails, Tasks 4-7, What not to do).

## Questions to answer (each with file:line evidence)
A. No free parameter: every number, window, threshold, cost, timing rule, exclusion and tie rule each test uses is
   fixed in its freeze or in frozen code, and the code implements exactly the freeze's rule (C2: section 3-5 rule,
   lag, T1/T2, c and the bar, p one-sided at 0.025, n >= 30, the T1 > T2 comparison; C1: q definition, M1 spec,
   feature_cols, the trade rule, gate0._b_test, the pass bar, the C10/C11 guards). Check the C2 statistic code line
   by line against section 5 (t, df, survival function, ddof).
B. Every stop rule present and enforceable in code: C2's 2% unsourced-date stop, the 200-date power stop, the
   terms stop, the spend stops (quote x 1.03 above the headroom; billed > quote x 1.03; insufficient balance);
   C1's probe rule, 2% stop, q-reproduction mismatch stop, C10 stop (closes the attempt), run-once.
C. Order of events enforceable: freeze commit, then registration, then purchase, then evaluation, for each test,
   in git, the trial registry and the spend ledger. Can the ES buy run without C2's registration? Can C2's
   evaluation run twice, or without the registration, or with a different freeze file? Can C1's buy run under
   v10 at all (it must not)?
D. Windows disjoint from everything the program has read: no bar of any root before 2019-05 has been read
   (check the stores, file names under data/, and the new code's window guards); C2 reads ES 2011-05-02..2019-04-30
   only and never MES's sealed stores; C1 reads 2010-06-07..2019-04-30 only; the hist plans refuse any chunk
   outside their windows; nothing in v10 changes behaviour for dates from 2019-05 on.
E. Spend safety: ACCOUNT_2_CAP_USD unchanged at 249.67; the E.14 session cap logic; acct-2 only; only ES buyable.
F. The calendars: does the grading match the rule (reports/stage_e14_briefs/calendar_rules.md)? Spot-check at
   least ten entries per group against the saved pages (grep the quoted text in the saved file). Are the 2%
   checks computed correctly over the right windows? Are unsourced dates excluded by the code, not just listed?
G. C1's code: does q_m1 reproduce with no refit and no write to the ML ledger; is M1 the annex's M1; does the
   replication's calendar context restore every patched name; are the C7 empty frames tested for equality?
H. Anything else that would make a verdict wrong or a guardrail fail.

## Output
reports/stage_e14_review.md, section "Freeze review (Task 4)": each finding with an id (F-01...), grade BLOCKING
(must fix before commit), SHOULD FIX or NOTE, the evidence (file:line, quoted), and the fix you propose. End with
an overall verdict: APPROVE, APPROVE WITH FIXES, or BLOCK. You may run read-only commands and the tests
(`uv run pytest -q -p no:cacheprovider <files>`, tail only, nice 10). Do not edit any file except your review.
Do not read any market data (no data/vendor, data/processed*, data/sealed, no GEX values: the CSV's sha256 is
enough), no .env, no key; no Databento or network call except fetching a saved page's URL again to check a quote.
Return: the path, a summary of at most 200 words with the counts per grade, and anything you could not check.
