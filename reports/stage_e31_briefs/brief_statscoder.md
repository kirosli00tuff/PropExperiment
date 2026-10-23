# Brief: StatsCoder-OpusXHigh (worker-xhigh, model opus) - Stage E.31 Part 3, statistics and kill rule

Objective (one): write the stats layer that turns the engine's per-day tables into the spec's statistics, the
kill-rule verdict and the report. Synthetic tests only.
Inputs: reports/stage_e31_pilot_spec.md sections 4 to 8 (binding; sections 1 to 3 are the engine's), the table
interface reports/stage_e31_briefs/work/pilot/TABLES31.md (binding), and E.28's
reports/stage_e28_briefs/work/B_pilot/measure_stats.py (Kaplan-Meier, day-block bootstrap, markdown helpers:
copy what fits into new files; E.28 files are read-only).
Files (new, in reports/stage_e31_briefs/work/pilot/):
- stats31.py: CLI --runs DIR --out-json PATH --out-md PATH [--boot 2000 --seed 31]. Reads every date folder with a
  done marker. Computes, per cell model x session x symbol (buy and sell pooled, and each side): placements, fills,
  fill rate, KM time to fill censored at 60 s (median, P at 1, 10, 60 s), stale share, touch rate; among fills the
  mean and median of markout_h, c_half, E_h = mo_h + c_half, N_h(firm) = E_h - fee per fill for all five firms
  (Topstep 0.264, Lucid 0.280, Bulenox 0.286, MFFU 0.306, Tradeify 0.460 ticks), share of positive E_h, VPO_h,
  at h = 1, 10, 60 s, and the no-drop variants; the splits of spec section 5 (ZS, ZL and joint buckets for L = 1
  and 10 s, session, USDA buckets, imbalance buckets) for every model; the loop's round trips per DAY trade date
  (mean, median, distribution) per model; the implied-liquidity shares. 95% two-sided percentile intervals by a
  day-block bootstrap over trade dates (2,000 replicates, seed 31) for every rate and mean, and for the loop mean.
- The kill rule, exactly spec section 7, on the primary population (ZM.v.0, DAY, model c, both sides pooled):
  K1 lower 95% bound of mean N_10(Topstep) not above 0; K2 fills < 400; K3 mean loop round trips per DAY trade
  date (model c) < 20. Verdict FAIL if any holds, else PASS; print each test's number, bound and result. Beside
  K1 (information only): the bound with 0.528 per fill, and the no-drop bound. Nothing else decides.
- The markdown report: the verdict first, then the three models side by side for the primary population, then
  all cells, splits, the loop, implied liquidity, and exclusion counts from days.parquet.
- tests/test_stats31.py: synthetic tables with known answers: fill rate and KM on a hand case; the bootstrap
  resamples whole dates (a date-clustered case); each of K1, K2, K3 triggers FAIL alone and PASS when none holds;
  fee arithmetic for the five firms; bucket edges of spec section 5 (both ends); missing values go to "missing".
  Run: uv run pytest -q -p no:cacheprovider reports/stage_e31_briefs/work/pilot/tests/test_stats31.py
Boundaries: no DBN file, no Databento call, no network, no API key. Do not edit the spec, TABLES31.md or files of
other workers (pull31*, verify31*, vol_*, and the engine files SimCoder will write: mbo_book*, kalgo*,
measure31*). If the spec is ambiguous for a statistic, stop and report it rather than choose. No commits. Keep
output short (pytest -q).
Return: the paths, a summary of at most 200 words with test counts, and anything unfinished.
