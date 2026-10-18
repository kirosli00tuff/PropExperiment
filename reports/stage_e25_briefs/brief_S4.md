# Stage E.25 S4 brief: ShortlistReviewer-FableXHigh

You are the independent reviewer of Stage E.25's synthesis (prompt docs/prompts/STAGE_E.25.md, section
SYNTHESIS item S4). You did not write any of it. Repo /home/kiros-li/Documents/GitHub/PropExperiment (cd there;
absolute paths). Research only: no market data (nothing under data/processed*, data/sealed, data/raw, no
.parquet/.dbn/.zst), no purchase, no web fetch unless a cited number cannot be checked from the files on disk
(then at most 10 fetches, terms read first, never cmegroup.com or SSRN by automation). No commits. Stage E.24 runs
in parallel: never touch forward/, base_rules/, multiday/, tests/, or run pytest. Do not spawn agents.

## What to check (every item)

1. **Evidence-quality labels.** For every S1 row and every S2 candidate in
   reports/stage_e25_briefs/synthesis.md, check the label (peer-reviewed, working paper, vendor, live record,
   pointer; secondary-only, unverified) against the reader file it cites (reports/stage_e25_briefs/<reader>.md
   and .json) and the quote recorded there. A number with no verbatim quote from fetched full text in a reader
   file is at most [unverified].
2. **Hurdle ratios.** Recompute every gross -> micro-tick conversion and every ratio in S1 and S2 by hand from the
   published figure (bp, price level, tick size) and the D8 round trip in reports/stage_e2a_costs.md (headline
   table; MES uses the Stage D model in sim/costs.py and sim/slippage_calibration.json). Check the brief's hurdle
   table (reports/stage_e25_briefs/brief_shared.md section 2) against the D8 file.
3. **Power.** Re-derive every power figure in S2 independently (do not just rerun
   reports/stage_e25_briefs/s2_power.py; check its method and inputs, then recompute): per-trade or per-day
   dispersion from the published sd, t and n; the event counts on the research window 2025-04-01..2026-06-19
   (monthly 3rd Fridays with holiday shifts and roll-blackout exclusions; quarterly refunding announcements;
   scheduled FOMC statements) from public calendars or the second readers' files (DF1, DF2, DF3); one-sided 5%
   and Holm thresholds.
4. **Overlap claims.** For every S1 "overlap" cell and every S2 "no prior trial duplicated" claim, check against
   reports/stage_e25_briefs/r0_mechanism_index.md and the inventory tables
   reports/stage_e23_briefs/inventory/{K1..K8,CDE,H6}.md (rule text, decision time, hold). A shortlisted candidate
   that duplicates a prior trial is BLOCKING.
5. **Group A and Group B** (user addenda 4 and 5): check the lead's rule and arithmetic against
   reports/stage_e25_briefs/NM1_nearmiss_table.json and NM2_exec_triage.md, and the passive-saving evidence in
   R17_maker_native.md and R18_queue_fill.md.
6. **Re-dig table** (user addendum 1): each SUPPORTS / WEAKENS / OVERTURNS claim against the quote in the reader
   file named.
7. **S3** against the evidence: flag any sentence the reader files do not support.

## Output

reports/stage_e25_briefs/review_S4.md: a verdict line (READY / READY WITH FIXES / BLOCK), then one numbered
finding per issue: severity BLOCKING (a wrong number entering the shortlist, a duplicate trial shortlisted, a
grade that changes a shortlist decision), SHOULD FIX (a wrong number or label outside the shortlist decision, a
missing caveat), or NOTE; location; what is wrong; your recomputed value or the correct text; evidence (file and
line or quote). Also a table of your recomputed ratio and power for every S2 row next to the lead's. Return to
the lead: the path, the verdict, counts by severity, and the BLOCKING items in at most 200 words.
