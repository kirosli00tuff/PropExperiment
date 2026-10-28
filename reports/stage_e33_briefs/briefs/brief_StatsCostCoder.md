# Brief: StatsCostCoder-OpusXHigh (Stage E.33 B5 (iii) and B6)

You are a worker (Opus 5.5, xhigh) for the E.33 lead. Do not spawn workers. Do not use AskUserQuestion: decide
conservatively, log it, continue.

## Objective 1 (prompt B5 (iii))
Show that the CV, deflated Sharpe, FDR and PBO code the stage uses reproduces published worked examples to the
stated digits: Lopez de Prado (Advances in Financial Machine Learning: the purged and embargoed CV construction and
average uniqueness, ch. 4 and 7), Bailey and Lopez de Prado (2014, "The Deflated Sharpe Ratio": its numerical
example), Benjamini and Hochberg (1995: the 15 p-value example), and the PBO by CSCV (Bailey, Borwein, Lopez de Prado
and Zhu). The code under test is the program's (funnel/multiple_comparisons.py deflated_sharpe_ratio,
expected_max_sharpe, probability_of_backtest_overfitting; screening/stage_e_verdict.py dsr, pbo, moments, t_stat) and
E.33's (pipeline/search33.py folds and embargo; pipeline/lab33.py weights; pipeline/select33.py BH and Holm helpers,
when they exist; poll). Each test quotes the published numbers with their source (paper, section or page) and the
digits matched. Sources: first look in E.32's saved pages and reader files (reports/stage_e32_briefs/pages/,
reports/stage_e32_methods_brief.md sections M5a and M3 by grep); if a worked example is not there, fetch it (WebFetch;
Scrapling fallback per CLAUDE.md), save the raw page under reports/stage_e33_briefs/pages/ with URL, UTC time and
sha256 in reports/stage_e33_briefs/pages/LOG.md, and grep it for the passage. A worked example you cannot obtain is
reported as not reproduced, never reconstructed from memory. Tests: pipeline/tests/test_stats_repro33.py.

## Objective 2 (prompt B6)
pipeline/cost33.py: re-derive ZM's per-firm net-ticks metric from E.28's fee file and the trade-through rule (V50):
- per-firm fee per round trip in ticks (ZM tick 10 USD) for Topstep, Lucid, Bulenox, MFFU, Tradeify from E.28's files
  (reports/stage_e28_briefs/A2_firm_*.json, A3_econ.json, A3_firm_products.json; find the fee fields), checked against
  the protocol's P6.4 list (0.528, 0.560 or 0.920, 0.572, 0.612, 0.920) and P0.3's f; report any difference;
- net ticks of a market round trip (P3.3 executable prices) and of a trade-through limit entry (P6.4 (ii): rests at the
  touch at t + L, fills only when a trade prints strictly through its price within min(60 s, h/5); market exit; the
  (ii-b) conversion at the timeout), per firm;
- tests on hand-built trades with known answers (pipeline/tests/test_cost33.py);
- agreement with E.31's per-fill accounting where the two overlap: E.31's code (reports/stage_e31_briefs/work/pilot/
  measure31_core.py `through` and the fee handling in stats31_core/stats31) applied to the same hand-built sequences
  gives the same fill decisions and the same per-fill net. Read E.31's code only; never open pilot/runs/ and never
  read reports/E.31_RETURN.md lines 175-213 or reports/stage_e32_briefs/X1_* (P1.2).
Also read docs/DECISIONS.md V50 (grep) and the protocol P0.3, P3.2-P3.3, P6.4.

## Boundaries
INTERFACE.md section 2 rules bind you (no real outcomes; no edits to program code; no package installs). Do not
change other workers' modules; if a reproduction fails because of their code, report it with the failing numbers.

## Return
Paths, a summary of at most 200 words (each worked example: reproduced to how many digits, or not), what is
unfinished, and reports/stage_e33_briefs/work/StatsCostCoder_readings.md.
