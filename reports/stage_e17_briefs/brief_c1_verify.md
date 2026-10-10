# Brief: VerdictVerifier-FableXHigh (worker-xhigh, model fable) - verify C1's STOPPED verdict (Stage E.17)

Written by the E.17 lead (rewritten at 22:50 after the run stopped). Independent check of the numbers and logic that
produced C1's verdict. Do not spawn workers. Do not commit. Write only under reports/stage_e17_c1_verify/ (create it)
and reports/stage_e17_review.md (append a section).

## What happened (the lead's account; verify it, do not trust it)

C1's single evaluation (c1_replication.evaluate; marker reports/stage_e14_c1_RUN_ONCE.json written 22:47:44; result
reports/stage_e14_c1_result.json, verdict STOPPED, finished 22:48:44, exit 1; log
reports/stage_e17_briefs/c1_evaluate.log) stopped at guard C10: "features live in E.12 apply on no NG row:
['g17_mbt (h60)', 'g17_mbt (hF)']". The lead's rulings C1-R1..R5 are in reports/stage_e17_rulings.md. No T1 or T2
statistic was computed. The lead reads the stop as the freeze's C10 rule applied as written: E.12's reference counts
for g17_mbt on NG rows are 87 (h60) and 84 (hF), and in 2010-2019 MBT is not listed (n/a by design).

## One objective

Decide independently whether the STOPPED verdict is correct, i.e. whether C10 fired on true counts by the freeze's
rule as written, or whether a code or input error caused it. Your verdict: VERIFIED (the stop is the freeze's rule on
correct counts), VERIFIED WITH NOTES, or NOT VERIFIED (a code or input error caused the stop; name it with file:line).

## Binding rules

- reports/stage_e14_prereg_C1.md sections 2 and 3 (MBT "not listed (n/a by design)"; ruling C7's CL and MBT
  sentinel frames; the C10 guard: "The run stops if any feature live in E.12 has 0 applicable rows ... A C10 stop
  therefore CLOSES this registered attempt"), section 9, and the annex reports/stage_e13_ng_replication_draft.md
  where it defines G17 and C10.
- c1_replication/evaluate.py (c10_counts, c10_check, the order: preconditions, marker, world, panel, C11, C10, trades).

## Checks

1. The reference: recompute E.12's applicable-row counts of g17_mbt (and of every g17_* lead) on NG rows from E.12's
   persisted state copy (~/.cache/propexp_e14_c1/e12_state_copy, read-only; manifest
   reports/stage_e14_c1_e12_state_manifest.json) or show where reports/stage_e14_c1_model.json's c10_reference comes
   from, and confirm 87 and 84.
2. The window: show, by your own script, that no MBT bar exists in 2010-06-07..2019-04-30 in what the run gave the
   world (ruling C7's sentinel frame), and that the G17 lead for MBT therefore cannot apply on any NG decision row
   there; confirm the run's applicable counts for g17_mbt are 0 (the result's guards.C10 block) and that every other
   feature with 0 applicable rows in the run also had 0 in the reference (so g17_mbt is the only trigger).
3. Code error or not: read c10_check and c10_counts and the freeze text; state whether the code implements the
   freeze's C10 rule as written, and whether the freeze anywhere exempts a leg that is n/a by design from C10. If
   the code deviates from the freeze, that is NOT VERIFIED with file:line.
4. Order and leakage: the marker was written before any bar was read (log order and file times); the result and log
   print counts only, no price or bar-derived statistic; no T1/T2 statistic, trade or verdict number exists anywhere
   (grep the result for mean, t_B, p_one_sided, trades_sha256).
5. Registration and inputs: ledger/trial_registrations.jsonl holds r001-C1 (C1-T1, C1-T2, freeze sha256
   afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b, N 471 -> 473); the result's inputs block records
   harness ba1ce99672b7e5bbb33f0cfabb89ba618d207d701348da1b1681ecfa7d932292, the store hashes
   reports/stage_e17_c1_store_hashes.json and the calendar hashes reports/stage_e17_c1_calendar_hashes.json, each
   equal to the files on disk.

## Boundaries

No vendor call, no key read, no write to ledger/, data/, the marker, the result or any frozen file; never run
c1_replication.evaluate (it runs once). You may build the world or panel with the frozen code into memory to count
applicability; print counts only, never prices or feature values. Check free memory first (the run peaked at 2.06 GB
RSS) and run at nice 10. Another worker (a coder in its own git worktree) runs at the same time; do not touch
data/pull_hist.py, data/hist_store.py, data/hist_calendar.py or data/config.py.

## Output

reports/stage_e17_c1_verify/ (your script(s) and a JSON of your counts), and a section
"## C1 STOPPED verdict verification (VerdictVerifier-FableXHigh)" appended to reports/stage_e17_review.md with each
check, findings graded BLOCKING, SHOULD FIX or NOTE with evidence. Return the paths, a summary of at most 200 words
with your verdict, and anything you could not finish.
