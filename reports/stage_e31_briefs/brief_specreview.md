# Brief: SpecReviewer-FableXHigh (worker-xhigh, model fable) - Stage E.31 Part 4, pass 1 (before any ZM purchase)

Objective (one): an independent, adversarial review of the frozen ZM pilot spec, its kill rule, its window
arithmetic and the purchase/verify code, returning GO or NO GO for the purchase.
Read first, against each other:
- docs/prompts/STAGE_E.31.md (the stage prompt; Parts 2 and 4 bind the spec) and docs/DECISIONS.md V48 (lines 980-1007).
- reports/stage_e31_pilot_spec.md (frozen v1; check its sha256 against reports/stage_e31_STATE.md).
- E.28's frozen spec reports/stage_e28_pilot_spec.md (the rules reused "where they apply").
- research: reports/stage_e31_briefs/research/K_algorithm.md, data_facts.md, usda_releases.csv (sources, quotes).
- the window arithmetic: reports/stage_e31_briefs/work/pilot/runs/span31.json and span31.log (free quotes, k).
- code: reports/stage_e31_briefs/work/pilot/pilot31_common.py, pull31.py, verify31.py, README31.md,
  tests/test_pull31.py; and data/spend_gate.py, data/pull_mes.py (RequestCappedGate), data/pull_universe.py
  (download), data/config.py (acct-3, PILOT_ONLY_ACCOUNTS) as used by them.
Check at least: (1) every Part 2 requirement of the prompt is in the spec, and nothing contradicts it (data, window,
sessions, order, three models, markouts and conditioning, fees, kill rule, implied check); (2) the kill rule is fully
determined before data (population, statistic, interval, thresholds, which model decides, the fee-per-fill reading
and whether it is defensible against the prompt's "less the Topstep fee in ticks"); (3) the K-algorithm section
against the research quotes; (4) the window arithmetic: TARGET = 125.00 - Part 1 settled - 2.00 rounded down, the
month bounds (DST), k = the most months whose total fits, k >= 2, all four series on the same months, a WASDE day and
a limit-reset month included; (5) the purchase code can only buy what the spec allows: acct-3 only, the four series,
the months, end <= 2024-02-29T22:00:00Z, nothing on or after 2024-03-01, fresh quote before each buy, sum <= TARGET,
SpendGate commit/settle, no key printed or logged, the pilot-only guard untouched; resume and failure paths cannot
double-buy or overspend; (6) verify31.py checks sizes, record counts, sha256 and date range; (7) anything that would
make the purchased data unable to answer the kill rule (e.g. MBO snapshots, continuous rolls, implied liquidity).
Run the pull tests (uv run pytest -q -p no:cacheprovider reports/stage_e31_briefs/work/pilot/tests/test_pull31.py) and
`uv run python reports/stage_e31_briefs/work/pilot/pull31.py --plan --months K` with K from span31.json (no vendor call).
Output: reports/stage_e31_briefs/R_spec31.md: verdict GO or NO GO on the first line; then numbered items, each marked
BLOCKING (must be fixed before any purchase) or ADVISORY, with file:line and the fix you propose.
Boundaries: review only. No Databento call of any kind (no quote: the --plan mode makes none), no API key, no edits to
any file except your output, no commits. The engine and stats code (mbo_book31, kalgo31, measure31*, stats31*) are out
of scope for this pass (they get their own review). Keep command output short.
Return: the path, the verdict, a summary of at most 200 words, and anything unfinished.
