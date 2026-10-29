# Brief: VerifyWorker-FableXHigh (Stage E.33c, Part D4; fresh context)

Objective: recompute independently, from the saved raw out-of-fold predictions and the label store alone, every
number that enters the E.33 selection decision and the selection decision itself. Then compare your numbers with
the pipeline's and with the StatsCoder's.

Scope (the lead names the branch at spawn):
- Branch T (Tier A not empty): every number in the Tier A and Tier B rows, and the Tier A / Tier B membership.
- Branch N (Tier A empty): the G1-G5 funnel for all 300 configurations, every P6.2 statistic of the 10 best by
  SR_d, and every configuration within 10% of any gate threshold. The decision to check is that no configuration
  passes G1-G5.
- In both branches: a full re-simulation from the predictions (P3.5 decision rule, P3.8 simulation) for every
  configuration in the rows above. For the rest of the 300, recompute the gate values from daily.parquet and
  trades.parquet, and check on 3 dates per configuration that trades.parquet follows from the predictions and labels.

Read first (by section):
- reports/stage_e32_discovery_protocol_v0.3.md (protocol 0.3, sha256 a2a2856f...; refuse if it differs): P3.3-P3.8, P6.1-P6.2, P7.2,
  P8.
- reports/stage_e33_protocol_readings.md: the lead rulings and the Appendix entries S01-S21 and P01-P14. Where the
  protocol text leaves a choice, the ruling there is the declared reading.

Inputs (read only):
- derived/e33/search/<cid>/fold<k>.npz (OOF probabilities and row keys), fold<k>.model.json, daily.parquet,
  trades.parquet, not_made.parquet, stats.json.
- The label store labels/<label_sha>/ and feature store features/<feat_sha>/ (sigma_ZM(D) in _day/), shas given
  at spawn.
- The selection output from select33 and the StatsCoder's reports/stage_e33c_briefs/work/D_stats.json, to compare
  against only after your own numbers are written.

Independence:
- Write your own code under reports/stage_e33c_briefs/work/verify/.
- Do not import pipeline/search33.py, pipeline/select33.py, the StatsCoder's code under reports/stage_e33c_briefs/work/stats/, or any
  pipeline module except pipeline/data33.py and cal33.py for reading files and the calendar.
- G3 names the program's function funnel.multiple_comparisons.deflated_sharpe_ratio, so call it, and also compute
  the DSR from its formula yourself; report both.
- Tolerance: 1e-9 relative, 1e-12 absolute (G7) for floats; integers, flags and memberships exactly.

Output:
- reports/stage_e33c_briefs/work/D4_verify.md: per number, your value, the pipeline's, the StatsCoder's, and agree
  or differ.
- A verdict line: the selection decision CONFIRMED or NOT CONFIRMED, with each difference located (file, config,
  date).

Rules:
- Real outcomes may be read (C1 registration on file).
- Never edit the search root, the stores or any frozen file.
- No test-window data and nothing dated 2024-03-01 or later. No Databento call; no live/ or ops/.
- Run at nice 10, at most 4 processes. Check `free -m` first, and stop a job if free memory falls below 2 GB.
- Scripts print counts, not rows. Every time from `date`, in PDT.
- Do not end your turn while a job of your own is running.

Return: the path; a summary of at most 200 words with the verdict and every difference; anything not finished.

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
- Model: Fable at xhigh (V55: independent verifiers on Fable). Fresh context.
- Outputs (E.33c paths): reports/stage_e33c_briefs/work/D4_verify.md; your code under
  reports/stage_e33c_briefs/work/verify/ (not work/stats/, which is the StatsCoder's and which you must not read
  before your own numbers are written); large outputs under derived/e33/verify_c/.
- Compare with the selection output as soon as your own numbers are written. The StatsCoder's D_stats.json may not
  exist yet when you finish: if it is absent, write "StatsCoder comparison pending" in D4_verify.md and return; the
  lead will send a short follow-up.
