STAGE D.1d "MULTI-TIMEFRAME AUDIT AND BOUNDED COARSER-BAR SWEEP"

Model: Opus 5, ultracode effort.

Reasoning: unlike D.1c, this session has a genuinely parallelizable core. Task 1
(auditing 24 existing trials against their source's stated horizon) is
mechanical extraction, delegable. Task 3's computation splits cleanly into
four independent workstreams, one per timeframe (5, 15, 30, 60-minute bars),
each computing its own declared stylized facts and re-tests with no
dependency on the others. That is the standing bar for ultracode: real,
non-overlapping parallel investigation, not synthesis dressed up as parallel
work. Task 2's declaration and Task 5's synthesis stay lead-only for the
same reason D.1c's Task 3 did: a subtly slanted declaration or a slanted
synthesis would functionally pre-decide the result.

============================================================
SCOPE
============================================================

Every trial run in D.1 and D.1b used 1-minute bars for both signal
construction and entry timing, regardless of what horizon each literature
source actually specified. This session checks whether that forced
resolution understated or misrepresented what the sources claim, and
separately runs a bounded, declared sweep of new stylized facts at coarser
intraday resolutions. It does not touch the XFA flatten constraint decided
in D.1c: every bar and every position stays inside one trade date, same as
before. It requires no new data purchase. All work resamples the 1-minute
GLBX.MDP3 bars already on disk into 5, 15, 30, and 60-minute bars,
respecting the RTH/ETH session boundaries and the daily halt.

Read progress.md's Stage D.1, D.1a, D.1b, and D.1c entries before starting,
plus docs/SCREENING.md and reports/stage_d1b_family_f_declaration.md, which
is the template for how Task 2 below must be written.

CREDENTIAL AND HOLDOUT GUARDRAILS — unchanged. No TopstepX API or
credential reference. Check `python -m data.holdout status` at start and
end, confirm `unlocks_logged: 0`.

SPEND GUARDRAIL: this session needs $0.00 in Databento spend. Every bar
used here already exists on disk as 1-minute OHLCV. If a data request
seems needed, stop — that means the task has drifted toward D.1e's scope
(the order-book fill model), which is a separate, costed stage.

============================================================
TASK 1 — HORIZON-RESOLUTION AUDIT OF THE 24 EXISTING TRIALS
============================================================

Delegable, mechanical. For each of the 24 trials across families A through
E plus C-H4, compare the signal-construction and entry-timing resolution
the harness actually used against the horizon the trial's cited source
specifies (use D.1's untruncated `all_results.json`, not the truncated
table in progress.md). Produce a table: trial ID, source's stated horizon,
what the trial tested it at, and whether that is a faithful test or a
resolution mismatch. Flag every trial where the source's natural horizon is
5 minutes or coarser and the trial forced finer-grained entries or signal
windows in a way that could plausibly understate the claimed effect. Do not
judge whether the effect is real — only whether it was tested at the right
resolution. This list is the exact and only scope of Task 3's re-tests; do
not add trials to it after Task 2 is written.

============================================================
TASK 2 — DECLARE THE COARSER-TIMEFRAME FEATURE SPACE (LEAD ONLY, BEFORE
ANY COMPUTATION)
============================================================

Write this declaration to `reports/stage_d1d_timeframe_declaration.md` and
hash it before any computation code exists, exactly as Family F's
declaration was handled in D.1b. It must fix, in advance:

- The four timeframes: 5, 15, 30, 60-minute bars, built from the existing
  1-minute data. State the resampling rule precisely, including what
  happens to a bar that would span the 15:10 CT flatten or the daily halt
  (truncate or drop it; do not extend a bar past a session boundary).
- The exact re-tests carried over from Task 1's flagged list — one entry
  per flagged trial, restating each at its source's actual specified
  horizon.
- A capped list of new stylized facts to compute at each of the four
  timeframes, in the same style as Family F's F1 through F6 (bar-to-bar
  momentum and reversion, range-breakout continuation, opening-range
  breakout, VWAP-deviation reversion, or others as this session judges
  relevant to a coarser resolution). State the cap on how many of these may
  be formalized into trials: no more than 8 across all four timeframes
  combined, matching the order of magnitude of Family F's cap.
- The selection rule for formalizing a stylized fact into a trial:
  directional, statistically significant after correction, stable across
  sub-blocks, and its implied edge clears the same per-trade cost bar used
  throughout this program (about 2.11 ticks at market, 0.98 passive). Note
  explicitly that this bar does not change with the timeframe — fewer round
  trips per day at 60 minutes changes statistical power, not the cost
  hurdle per trade.
- The inference method: reuse D.1b's stationary day-block bootstrap and
  Benjamini-Hochberg correction, applied within this session's own trial
  count, not mixed into D.1b's Family F numbers.

If nothing in the capped list survives the selection rule, zero hypotheses
are formalized, exactly as Family F allowed for and used.

============================================================
TASK 3 — EXECUTE, ONE WORKSTREAM PER TIMEFRAME (PARALLEL)
============================================================

Four independent subagents, one per timeframe (5, 15, 30, 60-minute), each
working only from Task 2's declaration file. Each computes its assigned
stylized facts, runs its assigned re-tests from Task 1's list at that
timeframe if any apply, and screens anything that survives Task 2's
selection rule through the existing `screen_candidate()` runner, honoring
`roll_blackout`, the EOD trailing MLL, and the flatten. Each subagent
writes its full result set to disk, not just survivors, so the lead is
working from artifacts rather than summaries.

============================================================
TASK 4 — EXTEND THE CUMULATIVE ACCOUNTING
============================================================

Delegable, mechanical. Extend `strategy/research/_d1b_accounting.py` (or a
new `_d1d_accounting.py` that continues from it) to N = 24 plus however
many trials Task 3 actually ran (re-tests plus any newly formalized
coarser-timeframe hypotheses). Recompute Deflated Sharpe Ratio, the
Harvey/Liu/Zhu t-hurdle, and PBO cumulatively, the same way D.1b extended
D.1's accounting. Re-verify the prior 24 trials still reproduce to the cent
as a continuity check, the same discipline D.1b applied to D.1's 23.

============================================================
TASK 5 — SYNTHESIS (LEAD ONLY, NO DELEGATION)
============================================================

Does anything from Task 1's re-tests or Task 2's declared sweep clear the
bar. State this plainly regardless of the answer. If the shortlist is
still empty, say so with the same rigor D.1b's close used, and give an
honest read on what this adds to the "should the program keep searching"
question: whether the resolution-mismatch hypothesis was worth checking,
and what if anything remains unexamined after this session besides the
order-book question already scoped for D.1e.

============================================================
WHAT NOT TO DO
============================================================

No Databento spend of any kind. No new data purchase. No writes to
REGISTRATION.md. No holdout unlock. Do not write Task 2's declaration
after seeing any Task 3 result, and do not add hypotheses to the declared
list after it is hashed. Do not exceed the 8-hypothesis cap. Do not let
any bar or position span the daily halt or cross a trade date. Do not
touch `rules/xfa_rules.py` or anything under `live/` or `ops/`.

============================================================
DELIVERABLE
============================================================

A dated progress.md entry: Task 1's audit table with every trial's
resolution-match verdict; Task 2's declaration file path and hash, written
before computation; Task 3's full results from all four timeframes,
survivors and non-survivors; Task 4's updated N and the recomputed
DSR/PBO/t-hurdle table; Task 5's synthesis and an updated shortlist, or an
explicit statement that it remains empty.

END PROMPT
