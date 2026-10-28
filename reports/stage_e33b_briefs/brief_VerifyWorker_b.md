# Brief: VerifyWorker-OpusXHigh (Stage E.33b, Part D4; fresh context)

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
- reports/stage_e32_discovery_protocol.md (sha256 c4ffb9d7...; refuse if it differs): P3.3-P3.8, P6.1-P6.2, P7.2,
  P8.
- reports/stage_e33_protocol_readings.md: the lead rulings and the Appendix entries S01-S21 and P01-P14. Where the
  protocol text leaves a choice, the ruling there is the declared reading.

Inputs (read only):
- derived/e33/search/<cid>/fold<k>.npz (OOF probabilities and row keys), fold<k>.model.json, daily.parquet,
  trades.parquet, not_made.parquet, stats.json.
- The label store labels/<label_sha>/ and feature store features/<feat_sha>/ (sigma_ZM(D) in _day/), shas given
  at spawn.
- The selection output from select33 and the StatsCoder's reports/stage_e33_briefs/work/D_stats.json, to compare
  against only after your own numbers are written.

Independence:
- Write your own code under reports/stage_e33_briefs/work/verify/.
- Do not import pipeline/search33.py, pipeline/select33.py, the StatsCoder's code under work/stats/, or any
  pipeline module except pipeline/data33.py and cal33.py for reading files and the calendar.
- G3 names the program's function funnel.multiple_comparisons.deflated_sharpe_ratio, so call it, and also compute
  the DSR from its formula yourself; report both.
- Tolerance: 1e-9 relative, 1e-12 absolute (G7) for floats; integers, flags and memberships exactly.

Output:
- reports/stage_e33_briefs/work/D4_verify.md: per number, your value, the pipeline's, the StatsCoder's, and agree
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
