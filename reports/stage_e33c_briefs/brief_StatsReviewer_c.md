# Brief: StatsReviewer-FableXHigh (Stage E.33c, Part D5)

Objective: an adversarial review of Part D (D1 to D4) and of the honesty of the language used to report it. Find
anything wrong, overstated or missing before the lead writes the return.

Read (by section):
- The frozen protocol reports/stage_e32_discovery_protocol_v0.3.md (protocol 0.3, sha256 a2a2856f...; refuse if it differs): P6.2, P7.2, P8, P10.
- docs/prompts/STAGE_E.33.md Part D and Part E.
- reports/stage_e33_protocol_readings.md (lead rulings govern).
- docs/NULL_CRITERIA_E.md.
- The StatsCoder's reports/stage_e33c_briefs/work/D_stats.md and D_stats.json, with its code under reports/stage_e33c_briefs/work/stats/.
- The VerifyWorker's reports/stage_e33c_briefs/work/D4_verify.md, with its code under reports/stage_e33c_briefs/work/verify/.
- The selection output from select33 (path given at spawn).
- The lead's draft sections 3 to 5 of reports/E.33c_RETURN.md, when the lead sends them.

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

Output: reports/stage_e33c_briefs/review/StatsReview_c.md with BLOCKING, SHOULD FIX and NOTE items, each with a file
and line and a concrete fix.

Rules: read only, except your own review file. Small scripts to recompute a number are allowed (nice 10, at most 2
processes); print counts, not rows. No test-window data. Every time from `date`, in PDT. Do not end your turn while
a job of your own is running.

Return: the path; the counts by severity; every BLOCKING item, in at most 200 words.

## E.33c addendum (lead, 2026-10-28 PDT; governs where it differs from the text above)
- Binding protocol: 0.3 = reports/stage_e32_discovery_protocol_v0.3.md, sha256
  a2a2856f49723f97319a4db2819ba4d1b5c4b8a1dc86a596e7c48110dbb48246 (check it; refuse if it differs). It is v1.0
  (c4ffb9d7) plus one amendment of the P5/P10 compute reference only (reports/stage_e33c_briefs/protocol_v0.3.diff);
  P3, P6, P7, P8, P10's null report and every threshold read exactly as in v1.0. The readings file
  reports/stage_e33_protocol_readings.md (FINAL) cites v1.0; its rulings govern 0.3 unchanged.
- N = 838: trial_registry.current_n() after the E33 registration r009-E33 (no E33A registration exists).
- The search is finished: 300 configuration DONE markers (counts and failures in
  reports/stage_e33c_briefs/search_end.txt). The outcome seal is lifted for Part D. Search root
  /mnt/large-storage/market_data/PropExperiment/derived/e33 (search/<cid>/); feature store features/2b30cb0e953b
  (sigma_zm in _day/); label store labels/b15c4ca10d68; schemas in reports/stage_e33_briefs/INTERFACE.md 4.1-4.3.
- The selection: reports/stage_e33c_briefs/select/P8_select33.json, written by the frozen select33.py (sha256
  9b9928066a35..., freeze list reports/stage_e33_pipeline_freeze.sha256 eb565a37) on all 300 at N 838, Tier B
  reading "continue" (readings R-L8); its stdout is P8_select33.out beside it.
- The branch (N: Tier A empty; T: Tier A not empty) is named in the spawn message.
- Python: run with `uv run python` from the repo root at nice 10, with PYTHONPYCACHEPREFIX set to a folder under
  your own scratch path, so no __pycache__ lands in the frozen pipeline folder.
- Times from `date`, in PDT. Do not end your turn while a job of your own runs.
- Model: Fable at xhigh, fresh context. Output: reports/stage_e33c_briefs/review/StatsReview_c.md.
- Read the StatsCoder's reports/stage_e33c_briefs/work/D_stats.md, D_stats.json and work/stats/; the VerifyWorker's
  reports/stage_e33c_briefs/work/D4_verify.md and work/verify/; the selection output above; and the lead's draft
  sections 3-5 of reports/E.33c_RETURN.md when the lead sends them.
- D3 check: B5's null is 20 seeds x 20 configurations (400 series; per-seed maxima over 20, not 300).
