# Brief: AmendReviewer-FableXHigh (Stage E.33c, S2; adversarial review before the hash)

You review one protocol amendment before it is hashed. You are independent of the lead who wrote it: check, do not
trust. Repo: /home/kiros-li/Documents/GitHub/PropExperiment. Times are PDT (America/Vancouver); take them from `date`.

## What was decided and what the lead wrote
- User decision V53 (docs/DECISIONS.md lines 1094-1111): amend the frozen protocol to "version 0.3" for registration
  r009-E33 only; replace P5/P10's synthetic-probe 3x reference with one projected from the real per-fold wall times
  in reports/stage_e33_briefs/work/logs/search_real.log (timings only, no outcomes); keep a 3x stop; hash 0.3 before
  the search resumes; nothing else in the protocol changes. Stage prompt docs/prompts/STAGE_E.33c.md, step S2.
- Background: reports/E.33b_RETURN.md sections 3.6-3.7 and 7 (D1); reports/stage_e33_STATE.md lines 160-176 (the 0.2
  projection and the stop) and the "# E.33c" section at the end (decisions so far).
- Frozen v1.0: reports/stage_e32_discovery_protocol.md (sha256 c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05).
- Amended: reports/stage_e32_discovery_protocol_v0.3.md; diff reports/stage_e33c_briefs/protocol_v0.3.diff; built by
  reports/stage_e33c_briefs/tools/make_v03.py.
- Method in code: reports/stage_e33c_briefs/tools/project_ref_v03.py; its output reports/stage_e33c_briefs/ref_v03.json.
  Inputs: search_real.log, ledger/trial_registrations.jsonl (r009-E33 ids), work/logs/p5_builder_probe_e33b.log,
  work/logs/p10_stop.json (all under reports/stage_e33_briefs/ unless rooted).
- An independent per-fold extraction (Haiku): reports/stage_e33c_briefs/fold_times/ (csv, summary, parser).

## Checks (write each as CONFIRMED or DIFFERS, with your value and file:line)
1. Scope of the diff. Re-diff v1.0 and v0.3 yourself. Every changed line must belong to (a) the status/version
   paragraph, (b) P5's "Probe and compute stop" bullet, or (c) the P10 stop clause that names the reference. Report
   the hunk count and confirm every other line is byte-identical.
2. No outcome was read to make it.
   (a) The inputs carry wall times only: confirm from the runner's log statements
   (reports/stage_e33_briefs/work/pipeline/run_search33.py) and from the log's line types (grep for formats; do not
   print fold-level content beyond what you need).
   (b) The projection script reads only its four inputs.
   (c) The lead's own tool calls this session: scan the lead transcript
   /home/kiros-li/.claude/projects/-home-kiros-li-Documents-GitHub-PropExperiment/7c6136a3-16c6-44df-891a-efd174837057.jsonl
   with a short script that prints only tool-call INPUTS (never results) that name an outcome file: stats.json,
   daily.parquet, trades.parquet, not_made.parquet, fold*.npz or fold*.model.json under derived/e33/search/. Report
   what you find.
3. Recompute R_0.3 independently from the log with your own code (do not import or run the lead's script for this):
   the 440 measured folds, the 8 cut folds, the 360 S5 cells, rho_LOGIT and rho_LGBM with their cell counts, B, the
   LOGIT and LGBM fold sums, R_0.3, 3 x R_0.3, the 6,774.8 s at the stop and the allowance for the resumed run, and the
   projected remaining part. Agree within 0.1 s, or report DIFFERS.
4. The text alone. Could a reader reproduce R_0.3 from the 0.3 wording without the script? List every gap or ambiguity.
5. Fidelity to V53 and the prompt. The measured wall time keeps its v1.0 definition; the interval from the 0.2 stop to
   the resumed first fold start is treated as a logged pause; P10 stays coherent with P5; nothing else changed.
6. Judgment, on wall times only. Is the method a defensible projection, neither tuned to make the stop inert nor to
   make it fire? Compare 3 x R_0.3, and the resumed run's allowance, with the measured pace (S5 and S1 fold times, the
   0.2 run's wall time net of its pause). Name any assumption you would challenge (for example the linear
   feature-count factor, or using S5 cells for S2-S4), and say whether it changes the verdict.

Mark each finding BLOCKING, SHOULD FIX or NOTE, then give GO or NO GO for hashing version 0.3.

## Boundaries
- OUTCOME SEAL: never open stats.json, daily.parquet, trades.parquet, not_made.parquet, fold*.npz or fold*.model.json
  under /mnt/large-storage/market_data/PropExperiment/derived/e33/search/. You do not need any file there.
- Edit nothing except your review file. No web, no git, no agents. Keep command output short (counts, not rows).
- Do not end your turn while a job of yours is running.

## Output
reports/stage_e33c_briefs/review/AmendReview_c.md: the checks, the findings, the verdict, the time written. Return the
path, the verdict, the finding counts by level, and at most 200 words.
