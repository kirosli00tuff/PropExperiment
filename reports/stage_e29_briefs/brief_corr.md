# Brief: CorrMeasurer-OpusHigh (Stage E.29)

You are a worker in Stage E.29 of PropExperiment. Read CLAUDE.md's "Invariants", "Context hygiene" and "Compute
limits" sections first. Times in PDT from `date`. Do not spawn other agents.

## Objective
Measure reference correlations (never a model input) between the front contracts of CL, ZM, GC and NQ from owned
one-minute bars, exactly as reports/stage_e29_model.md section 8 says (read that section).

## Inputs
- Owned bars: data/vendor/databento/GLBX.MDP3/ohlcv-1m/<ROOT>_v_0/ only. Reuse the file guard and the trade-date and
  calendar conventions of E.28's A0 script, reports/stage_e28_briefs/work/A0/A0_stats.py (read its open_store and
  trade-date functions, and A0_contract_stats.md "Data rule" and "Method"). If ZM is not owned, use the owned
  soybean-complex sibling (ZS or ZL) and name it.
- Window: trade dates 2022-11-01 to 2023-10-31. Open only files whose range ends on or before 2023-11-01 (A0's
  rule). Never open a file dated 2024-03-01 or later, any mbp-1 file, anything under data/sealed, data/processed*,
  any holdout, embargo, research-window or MES file. Decide from file names before opening.

## Method
- Front contract per trade date: the highest-volume outright on that date (state the rule you used; drop the
  date of each front change as a roll day).
- Daily return: log(close_t / close_{t-1}) of the same front contract on consecutive trade dates (no return across a
  roll). Daily range: (high - low) / close in percent, Globex day.
- Pairwise Pearson correlations over common trade dates for the six pairs, for returns and for ranges, with the
  number of days; also Spearman for both. Report also the main-session-only (06:30-13:00 America/Vancouver)
  return correlation.
- Run `uv run python -m data.holdout status` (keys only: all_ok and unlocks_logged per entry) immediately before
  your first data read and immediately after your last, and paste both outputs into your output file.

## Output
reports/stage_e29_briefs/E29_correlations.md (method, files opened with their ranges, guards, both holdout checks,
the tables) and E29_correlations.json; script under reports/stage_e29_briefs/work/corr/. nice 10, one process.
Keep printed output short.

## Boundaries
- Facts only: do not interpret against the model's rho grid; the lead does that.
- Do not edit anything outside reports/stage_e29_briefs/work/corr/ and the two output files. No network, no
  Databento, no keys. Do not write under data/.

## Return
The paths, a summary of at most 200 words with the six return and range correlations and day counts, and anything
not done.
