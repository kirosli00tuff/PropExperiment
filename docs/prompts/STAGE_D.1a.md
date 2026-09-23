STAGE D.1a "HARNESS FIXES: DRIFT BENCHMARK, PASSIVE FILLS, SHARED RUNNER"

Model: Opus 5, high effort.

Reasoning for this tier: this session is three interdependent
infrastructure fixes to a single existing harness, not independent
parallel investigations. The shared runner (Task 3) has to integrate
correctly with both the drift benchmark (Task 1) and the fill model
(Task 2), and getting the interfaces right requires one coherent design
sense across all three rather than three agents converging on
compatible APIs independently. This does not meet the standing bar for
ultracode (genuinely divided, independently-investigable work) the way
Stage D.1's literature search across five non-overlapping families did.
Delegate only clearly mechanical, well-specified sub-pieces once the
design is settled — known-answer test scaffolding, docstrings — to
Sonnet-effort subagents if useful; keep every design decision and every
piece of statistical judgment with the lead. State in the final report
what, if anything, was delegated.

============================================================
CONTEXT — READ BEFORE STARTING ANYTHING
============================================================

Working directory: /home/kiros-li/Documents/GitHub/PropExperiment. Read
README.md, docs/DECISIONS.md, docs/STAGES.md, and the full progress.md
entries for Stage A.1, Stage B-C, and Stage D.1 before touching
anything. Stage D.1's entry (dated 2026-09-18) is the direct source of
every task in this session — it names these three limitations
explicitly, in its "Harness facts this session surfaced" and "What a
future session would need" sections, and this prompt exists to close
them. Do not treat Stage D.1's specific numbers (the 23 trials, the
DSR/PBO figures, the drift estimate of +13.65 ticks/session) as
something to re-derive or second-guess here — this session fixes the
harness, it does not re-run or re-judge D.1's screening results.

One fact from Stage D.1 to hold onto while building: the drift estimate
that exposed the false-positive problem (roughly 13.65 ticks per
session, translating to about $4,000 net on one unconditional long leg
over 276 RTH sessions after costs) came from Stage B's own Task 2 null-
generator calibration work, not from a new calculation. Task 1 below
should reuse that existing calibration rather than re-deriving drift
from scratch, unless you find a specific reason the existing figure is
wrong, in which case say so explicitly and show the discrepancy.

CREDENTIAL, STRATEGY-SCOPE, AND HOLDOUT GUARDRAILS — unchanged, carried
forward from every prior session. No TopstepX reference of any kind.
Nothing under live/ or ops/. Do not design, imply, or hint at any actual
trading edge — this session builds measurement infrastructure, not
strategies. Do not unlock the sealed holdout under any framing; check
`python -m data.holdout status` before, during, and after this session
and confirm `unlocks_logged: 0` in the final report, exactly as Stage
D.1's report did.

SPEND GUARDRAIL: this session should need no new Databento spend — every
fix below operates on data already on disk (the existing 517,197-bar
MES series, the two MES tick days used for the original cost
calibration, Stage D.1's own research-fold results). If a genuine gap
emerges, cap new spend at $10 total, quote-then-log through the
existing gate. Do not use this session to acquire the order-book days,
second instrument, or longer history Stage D.1 flagged as needed for a
future data-driven round — those are explicitly out of scope here; a
data-acquisition decision is the user's to make separately, not this
session's to trigger under cover of "fixing the harness."

TOOLCHAIN: continue uv, ruff, pytest as established.

============================================================
TASK 1 — DRIFT / BUY-AND-HOLD BENCHMARK ALONGSIDE THE ZERO-EDGE NULL
============================================================

The problem, stated precisely: `funnel/power_gate.py`'s existing null is
a zero-edge random trader. Stage D.1 showed this null cannot distinguish
a strategy with real conditional edge from an unconditional long
position that is simply riding the research window's own upward drift —
both can clear the zero-edge bar, for entirely different reasons, and
the gate currently has no way to tell them apart.

Build a second, separate benchmark: a buy-and-hold (or, given the
XFA rules' daily flatten requirement, a "hold long through the RTH
session every day" or equivalent unconditional-long) benchmark computed
on the same train-fold data a candidate is being screened against, not
on the full dataset — the benchmark must be recomputed per fold, not
calculated once globally, since drift is a property of the specific
window being tested and Stage D.1 already showed this program's
research window has real, non-trivial drift baked into it.

Extend the screening interface so that a candidate must clear BOTH
benchmarks to be considered non-trivial: the existing zero-edge null (a
candidate must show real statistical edge, not just non-negative
expectancy) AND this new drift benchmark (a candidate's performance must
exceed what an unconditional long would have captured over the same
train dates, not merely match it). Decide and document explicitly
whether "clearing" the drift benchmark means the candidate's return
distribution must exceed the benchmark's at a stated confidence level,
or whether a simpler dominance check suffices for now — state your
reasoning, since Stage D.1's own reviewer flagged this as a design
decision that needed real statistical care, not a rushed default.

A short-only candidate should be checked against the mirror-image
benchmark (an unconditional short position over the same dates), not
silently exempted from this check just because the drift happens to run
positive in this window.

Write known-answer tests: construct a synthetic series with a known,
injected drift and confirm an unconditional-long strategy correctly
fails to clear the new benchmark (since it IS the benchmark, restated),
and confirm a synthetic series with zero drift and a genuinely
conditional signal correctly is unaffected by the new check. This is
the direct test that Task 1 actually catches what Stage D.1 found by
hand, rather than merely existing in the code without being verified to
work.

============================================================
TASK 2 — PASSIVE / LIMIT ORDER TYPE IN THE FILL MODEL
============================================================

The problem, stated precisely: `sim/fill_model.py` currently only
prices market-order fills, calibrated from two days of MES book data.
Stage D.1's reversal family (the strongest-sourced idea in the whole
session, per its Task 1 literature log) specifically needs passive/limit
fills to be testable at all — a mean-reversion or reversal idea that
requires market-order entries to work is a fundamentally different (and
much more cost-sensitive) claim than one that can rest passively and
wait for the market to come to it.

Add a limit/passive order type to the fill model. State explicitly, in
code and in the final report, what this addition does and does NOT
model: it should represent whether and when a resting limit order at a
given price would have been filled given the historical bar sequence
(e.g., touched-and-through logic on OHLC bars), but it does NOT model
queue position (where in the order book's price-level queue a resting
order would have sat relative to other orders already there), and does
NOT model the possibility that a passive order's mere presence would
have changed the market's subsequent path. Both of these are real
limitations of what's achievable from the OHLCV-plus-two-tick-days data
this project has; state them as caveats a future backtest result must
carry, exactly as the two-day slippage calibration's caveats already
get restated in Task C.3's code and in every session since.

Write known-answer tests: a synthetic bar sequence where a limit order
at a known price should fill (price touches or crosses it) and one
where it should not (price never reaches it), confirmed to the cent
including any modeled adverse-selection assumption you choose to apply
to a passive fill (state whether you apply one, and why or why not).

============================================================
TASK 3 — SHARED SCREENING RUNNER WITH ONE CANONICAL EngineConfig
============================================================

The problem, stated precisely: Stage D.1's B/D partitioning failure
happened in part because different subagents could construct their own
EngineConfig, and the roll_blackout parameter specifically is easy to
omit silently — omitting it doesn't raise an error, it just means a
strategy can hold across a contract splice and trip
`EngineInvariantError` unpredictably, or in the worse case not trip
anything and produce a quietly wrong result. Nothing currently documents
that a strategy runner must supply it.

Build a single shared screening entry point — a function or small module
that any future hypothesis-screening session (a future D.1-style
literature round, and the "Family F, data-native patterns" idea
discussed but explicitly not yet started) is expected to call, rather
than constructing its own EngineConfig by hand. This entry point should
hard-code the canonical configuration this project has settled on
(roll_blackout=roll_blackout_dates(...) included, and any other
settings that should not vary between sessions), and should make it
structurally awkward to bypass — for example, by not exposing a raw
"construct your own EngineConfig and call run_backtest directly" path
as the documented/discoverable one, the way a well-designed API steers
users toward the safe call. Wire both Task 1's drift-benchmark check and
Task 2's new fill-model capability through this same shared entry point,
so a future session gets all three fixes automatically just by using it,
rather than having to remember to opt into each separately.

Document this shared runner clearly enough that a future D.1-style
prompt can simply instruct subagents to "use the shared screening
runner" as a single, unambiguous instruction, rather than needing to
re-explain roll blackout, drift benchmarking, and fill-model choice
separately in every future prompt the way this project's prompts have
had to do so far.

============================================================
TASK 4 — REGRESSION AGAINST STAGE D.1'S OWN RESULTS
============================================================

Once Tasks 1 through 3 are complete, re-run Stage D.1's 23 already-
logged trials (not new hypotheses, the exact same 23) through the new
shared runner, and confirm two things explicitly in the report:

1. The result for every trial that Stage D.1 already correctly
   identified as failing (all 23, since nothing passed) still fails
   under the new harness — this is a sanity check that the new checks
   didn't accidentally change existing behavior in some unrelated way.
2. Specifically confirm that the four unconditional-long trials Stage
   D.1 flagged as drift-driven (A-H1, A-H2, and both A-H4 legs) now
   correctly fail the new drift benchmark from Task 1, not merely the
   zero-edge null — this is the direct proof that Task 1 actually
   closes the gap Stage D.1 found, rather than a plausible-sounding fix
   that was never checked against the exact case that motivated it.

If either check surfaces a surprise (a trial's verdict changes in an
unexpected way, or the drift benchmark doesn't cleanly catch the four
flagged trials), stop and report it clearly rather than quietly
adjusting the new code until the expected answer appears — a benchmark
that has to be tuned to produce the answer you already know is
supposed to come out is not a real check.

============================================================
WHAT NOT TO DO
============================================================

Do not run any new strategy hypotheses this session — Task 4's
regression against Stage D.1's existing 23 trials is the only
backtesting this session does. Do not touch the sealed holdout under
any framing. Do not write to REGISTRATION.md. Do not acquire new data
beyond the $10 spend guardrail's narrow allowance. Do not touch live/,
ops/, or anything TopstepX-shaped. Do not build the "Family F, data-
native patterns" exploratory work discussed but explicitly deferred —
that is a future session's decision, not this one's to start under
cover of harness work.

============================================================
DELIVERABLE
============================================================

A dated progress.md entry: what was built for each of the three tasks
and the design decisions made along the way (especially Task 1's
"what counts as clearing the drift benchmark" decision and Task 2's
adverse-selection modeling decision), the known-answer test results for
each, the full Task 4 regression report including the specific
confirmation that the four drift-driven trials now fail correctly,
holdout-status checks before/during/after, exact spend against the $10
cap, and a short, clear statement of what a future hypothesis-screening
session (literature-based or data-native) needs to know to use the new
shared runner correctly.

END PROMPT
