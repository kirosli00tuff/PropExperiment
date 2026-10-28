# Brief: StatsReviewer-FableXHigh (Stage E.33b, Part D5)

Objective: an adversarial review of Part D (D1 to D4) and of the honesty of the language used to report it. Find
anything wrong, overstated or missing before the lead writes the return.

Read (by section):
- The frozen protocol reports/stage_e32_discovery_protocol.md (sha256 c4ffb9d7...): P6.2, P7.2, P8, P10.
- docs/prompts/STAGE_E.33.md Part D and Part E.
- reports/stage_e33_protocol_readings.md (lead rulings govern).
- docs/NULL_CRITERIA_E.md.
- The StatsCoder's reports/stage_e33_briefs/work/D_stats.md and D_stats.json, with its code under work/stats/.
- The VerifyWorker's reports/stage_e33_briefs/work/D4_verify.md, with its code under work/verify/.
- The selection output from select33 (path given at spawn).
- The lead's draft sections 3 to 5 of reports/E.33b_RETURN.md, when the lead sends them.

Check:
1. Every gate value and the funnel follow P8 as written and as ruled; the selection decision follows from them.
2. The DSR, SR0, G3 and G4 thresholds are at the registered N (quote trial_registry.current_n() as recorded in
   STATE), with V = 1/(T_disc - 1) and each configuration's own moments.
3. BH, Holm and PBO are reports, never gates, and are computed on the declared sets.
4. D3's null comparison is like for like: the same statistic, the same dates, and the null seeds as run.
5. Branch N: P10 items (i) to (vi) are complete. The minimum detectable edge formula matches P7.2. Any null
   statement meets docs/NULL_CRITERIA_E.md, or says "no statement".
6. Branch T: the finalists file was hashed before any P6.4 or P6.5 number; no near miss is promoted; Part E's
   fields are complete.
7. D4 is independent in fact (no shared code beyond what its brief allows), and every difference it found is
   resolved or reported.
8. Language: no claim beyond the evidence (for example "no edge exists" from a discovery null), no hedging that
   hides a result, and the numbers in the prose match the tables.

Output: reports/stage_e33_briefs/review/StatsReview_b.md with BLOCKING, SHOULD FIX and NOTE items, each with a file
and line and a concrete fix.

Rules: read only, except your own review file. Small scripts to recompute a number are allowed (nice 10, at most 2
processes); print counts, not rows. No test-window data. Every time from `date`, in PDT. Do not end your turn while
a job of your own is running.

Return: the path; the counts by severity; every BLOCKING item, in at most 200 words.
