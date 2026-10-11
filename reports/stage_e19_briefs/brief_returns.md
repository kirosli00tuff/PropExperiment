# Brief: ReturnsCoder-OpusHigh (Stage E.19 Task 3 support, worker-high on opus)

Objective: implement prop_econ/returns.py exactly as reports/stage_e19_briefs/sim_spec.md section 1 specifies
(daily day-session returns of NQ, CL, GC, ZN, 6E from the owned E.12 training stores, demeaned and standardized;
the 5-day block bootstrap and the normal comparison source producing prop_econ.types.ShockSet; the product table with
D8 and cost-wall round trips), with tests, and write the per-path summary. This reads return magnitudes only; it is
not an edge test and computes no signal.

Inputs: sim_spec.md section 1; prop_econ/types.py (the lead's interface; do not change it, ask instead); the stores
data/processed_step2/{NQ,CL,GC,ZN,6E}/ohlcv-1m_<root>_v_0_2019-05-06_2024-02-29_step2.parquet; the frozen D6 day
session O_X..C_X per root (find where the repo defines it, e.g. screening/ or sim/ or the D8 cost code; cite the
file and line in your return); D8 costs reports/stage_e2a_costs.json (via sim.product_costs if convenient, read-only);
the E.10 cost wall reports/stage_e10_research/cost_wall.json; multipliers per contract from the repo's vehicle tables.

Data rules: read only those five parquet files and only the columns you need; assert every trade date is within
2019-05-06..2024-02-29; never print rows of a data file and never run head, cat, less or a DataFrame print on one
(print counts, dates ranges and summary statistics only); no other data file, no data/sealed, no holdout, no
research window, no MES store. Memory: one store at a time.

Files to write: prop_econ/returns.py; tests/test_prop_econ_returns.py (synthetic bars: exact r, up, dn, z, w; the
roll and missing-bar skips; demeaned mean exactly 0 per path; w <= min(0, z); bootstrap determinism by seed, 5-day
blocks within one path, the random and long direction modes, the per-product restriction; the normal source's
w <= min(0, z) and its mean and variance; ProductSpec values from the cost files); reports/stage_e19_returns_summary.json
and reports/stage_e19_returns_summary.md (per path: window used, dates kept, skips by reason, mean r removed in $ per
full contract, sigma_full and sigma_micro $, skew, excess kurtosis, share of |z| > 4, mean and 1st percentile of w
long and short, D8 and wall round trips for each vehicle, and cost per unit sigma k x rt/sigma at k = 1 and 3).
Also give a function that builds the shocks for (n_paths, n_days, seed, tail="bootstrap"|"normal",
direction="random"|"long", products=all or one, cost_model="d8"|"wall") and returns (ShockSet).

Boundaries: write only those files. Do not touch prop_econ/types.py or any simulator module (FunnelCoder-OpusXHigh
writes prop_econ/rules.py, funnel.py, vec.py, assemble.py in parallel). No edits to frozen code (ml_route_v2/, rules/,
sim/, screening/, data/). Run only your own tests, never the full suite; ruff clean; nice -n 10. Do not spawn workers.
Do not commit.

Return (three things): the paths; a summary of at most 200 words (the window per root, dates kept, sigma_full per
root, tail statistics, the cost per unit sigma); anything unfinished or any spec question.
