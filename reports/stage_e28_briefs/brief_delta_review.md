# Brief: DeltaReviewer-OpusXHigh (Stage E.28b, step S2)

You are an independent, adversarial reviewer in a fresh context. Repo: /home/kiros-li/Documents/GitHub/PropExperiment.
You did not write any of the work below. Judge it only from the files named here; do not trust any summary inside them
without checking it against the source it cites. Times are PDT (America/Vancouver).

Background, in one paragraph: Stage E.28 ranked firm-contract pairs for limit-order strategies (Part A) and froze a
pilot measurement spec (Part B) before a Databento purchase of ONE contract in ONE schema (mbp-1). A first Fable review
(R_rank.md) changed the ranking (lead rulings v2): the top pair moved from Topstep QG to Topstep QM, and the spec was
re-filled for QM. A second Fable review (R_spec.md, RS-01..RS-15) reviewed the QG version of the spec and the pilot code;
its fixes were applied afterwards. Nobody has reviewed the v2 ranking, the QM parameters or the code after the fixes.
That delta is your job.

## Objective

Return GO or NO GO for the purchase, with every BLOCKING item. A BLOCKING item is one that would make the purchase buy
the wrong thing (wrong contract, schema, dates, account or amount), break a guardrail (data dated on or after the
CME trade date 2024-03-01; research window, holdout or embargo), or make the frozen measurement flatter the result or
fail to run as the spec says. Everything else is SHOULD FIX or NOTE.

## Three checks

(a) The v2 ranking against R_rank and the v2 rulings.
- Inputs: reports/stage_e28_ranking_spec.md (the frozen criteria, sha256 89347e97...; check the hash),
  stage_e28_briefs/R_rank.md (findings table and Verdict), A3_lead_rulings.json (v1), A3_lead_rulings_v2.json (v2),
  A3_ranking_table.md/.json (v2, primary), A3_ranking_table_v1.md/.json, A3_score_apply_v2.md,
  work/A3_facts/score.py, A3_blind_ratings.json, A3_facts.json, A3_firm_products.json, A3_econ.json,
  work/REV_rank/rr_econ_lucidalt.json, A3_masked_contracts.json (C1(b) evidence fields; C40 is QG, mask key in
  A3_mask_key.json).
- Check: each v2 ruling (RR-01, RR-03, RR-04, RR-05) is applied exactly as written and nothing else changed; recompute the
  top 10 of the v2 primary table yourself (your own script under stage_e28_briefs/work/REV_delta/); confirm the top pair
  (Topstep QM) and the next 4; check RR-01's claim that only C40 has every C1(b) field UNKNOWN; say whether any v2 ruling
  departs from the frozen spec's text. The rulings were written after the v1 top pair was known: say whether each is the
  literal reading of the spec or a choice.

(b) The QM parameters in the frozen spec reports/stage_e28_pilot_spec.md (sha256 8937740338e81103...; check the hash; do
NOT edit it).
- Section 0, each row against its source: tick 0.025 USD/bbl and 12.50 USD; FIFO (F) for QM (saved .xls snapshots in
  stage_e28_briefs/pages/REV_spec/globex_product_reference_sheet_2023*.xls and 2024*.xls; the lead's reader
  work/lead/lead_xls_rows.py; find the QM rows yourself); FEE_SIDE 0.1368 = 3.42 / 2 / 12.50 (Topstep's QM fee in
  A3_firm_products.json and stage_e28_briefs/A2_firm_topstep.md and its saved pages under pages/); sigma_1m 2.520 from
  CL's 6.30 ticks in A0_contract_stats.md/.json under the sibling rule (x_ticks(QM) = x_ticks(CL) x 0.01 / 0.025);
  SIMRULE trade_through_only (docs/DECISIONS.md lines 30-46); request end 2024-02-29T22:00:00Z.
- Section 6 arithmetic: recompute n_10, n_60, days, the 15% raise, RS-07's 22/26-day correction, and the QM claim
  "first trade date no later than 2024-01-12" (QM rolls monthly; count trade dates, holidays/early closes and roll-day
  exclusions with the repo's CME calendar; see how R_spec did it in work/REV_spec/REV_spec_calendar_count.py). Check the
  spend target formula (RS-08) and that 121.25 at B = 125.00 follows.

(c) The code against R_spec and the spec.
- Inputs: stage_e28_briefs/R_spec.md (RS-01..RS-15, section 6 Verdict), the code in
  stage_e28_briefs/work/B_pilot/ (pilot_common.py, pilot_pull.py, verify.py, pilot_stream.py, measure_core.py,
  measure_stats.py, measure.py, README.md, tests/), the fixer's report work/B_pilot/FIXES_E28b.md and the test logs
  it names under work/B_pilot/runs/.
- Check each RS item is fixed in the code as the spec now says (not as the QG spec said): request end and verify
  cutoff (RS-01), A/B-only through clause (RS-04), side counts (RS-03), no-drop markouts (RS-05), stale share (RS-06),
  minimum span for QM in the buy step (RS-07), the margin rule (RS-08), SAFE TO WIPE precondition (RS-09), and the
  rest. Check pilot_pull.py's refusals (acct-3 only, dataset GLBX.MDP3, schema mbp-1, symbol QM.v.0, stype continuous,
  end bound, sealed windows) and that no path can buy for a second contract or schema. Re-run both suites yourself
  (commands in FIXES_E28b.md), quietly, logs to work/REV_delta/, and read only the tails. Add adversarial tests of your
  own under work/REV_delta/ for anything you suspect.

## Boundaries

- NO Databento call of any kind (no quote, balance, metadata or download). Never read, print or log any .env value or
  key; do not open .env.
- Write only under reports/stage_e28_briefs/work/REV_delta/ and your output file. Do not edit the spec, the code, the
  ranking files, the ledger, docs/, data/, live/ or ops/. No commits. Do not run the repo-wide pytest suite.
- Read files by section (grep, line ranges, short scripts that print only the fields you need). Never load
  reports/stage_e28_methods_brief.md (1 MB). Run anything heavy with nice -n 10.
- Do not spawn other agents.

## Output

reports/stage_e28_briefs/R_delta.md: a findings table (ID RD-NN, severity BLOCKING / SHOULD FIX / NOTE, file:line,
finding, required fix), then sections (a), (b), (c) with your recomputations, then a Verdict line "GO" or "NO GO" with
the BLOCKING list. Return: the path, a summary of at most 200 words with the verdict, and anything you could not finish.
