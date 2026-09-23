STAGE B–C "FUNNEL SIMULATOR + BACKTEST HARNESS"

Model: Opus 5, ultracode effort.

Reasoning for this tier, stated explicitly because it's a change from the
last two sessions: this prompt is structured as a multi-agent build. You
(the lead Opus agent) own the parts that need real judgment — leakage-
canary design, the sealed-holdout mechanism, the funnel Monte Carlo's
statistical design, and final integration review. Delegate the
mechanical, well-specified pieces to Sonnet-effort subagents through
whatever subagent/Task tooling this CLI exposes: fixture generation for
known-answer tests, boilerplate that consumes the existing bar-flag
columns, docstring and report-writing passes, and repetitive test-case
scaffolding once you've specified the shape. This is exactly the
structure the program's standing rule reserves ultracode for — a single
coherent task does not earn it, a genuinely divided multi-agent build
does. State in your final report which pieces you delegated and to what
effort tier, so the choice is auditable after the fact, not just
asserted.

============================================================
ETA — REQUIRED BEFORE COMMITTING TO THE FULL TASK LIST
============================================================

Before starting Task B.1, run a small probe: build the thinnest possible
version of the event-driven backtest loop (Task C.2 below) against one
month of the existing MES bar data, with no fill model and no rules
engine wired in yet, just raw iteration and intent collection. Time it.
Extrapolate a measured ETA for the full task list below from that probe,
not a guess pulled from general experience with similar work. Log the
probe result and the resulting ETA estimate in progress.md before
proceeding to the rest of the tasks. This matches the program's standing
convention: measured ETAs derived from probes, not asserted ones.

If the measured ETA suggests the full list will not complete overnight,
do not silently cut scope. Follow the priority order stated in the "if
time runs out" section near the end of this prompt, and say explicitly
in the final report what was cut and why, rather than delivering a
partial Task C.4 alongside a skipped Task B.2 with no explanation of the
tradeoff.

============================================================
CONTEXT — READ BEFORE STARTING
============================================================

Working directory: /home/kiros-li/Documents/GitHub/PropExperiment

Read, in order: README.md, docs/DECISIONS.md, docs/STAGES.md, and
progress.md's existing Stage A.1 entry. Stage A.1 delivered a validated
MES bar dataset (517,197 one-minute bars, 2025-04-01 through
2026-09-16), a cost model calibrated from two tick days (sim/costs.py),
and a pure-function XFA rules engine with known-answer tests
(rules/xfa_rules.py). This session builds directly on top of all three.
Do not re-derive or second-guess Stage A.1's outputs; if you find an
actual defect in them while working, fix it with a regression test and
note it clearly in progress.md, following the same pattern the Stage
A.1 session itself used when its own independent review caught two
medium bugs.

One locked convention from Stage A.1 that must carry forward: bars and
any live-lane logic bucket on ts_recv, never ts_event. The Stage A.1
tick cross-check proved these diverge by up to 8 minutes and 6 ticks on
a single sample day. Any code in this session that touches timestamps
must respect this.

CREDENTIAL GUARDRAIL — unchanged from Stage A.1. No TopstepX credential
exists. Nothing in this session touches live/ or ops/, no TopstepX API
reference of any kind.

STRATEGY-SCOPE GUARDRAIL — new for this session, read carefully. This
session builds the strategy interface and, for testing the harness
itself, a null (no-op) reference implementation and a zero-edge random
baseline implementation. It does not design, imply, or hint at any
actual trading edge, signal, or hypothesis. Strategy research is
explicitly Stage D.1, a separate future session by design, decided early
in this project and restated multiple times since — do not let "fit as
much as possible into this session" become a reason to quietly start
that work. If you find yourself writing logic that looks like a real
trading idea rather than a null/random placeholder, stop and flag it in
the report instead of continuing.

SPEND GUARDRAIL — tighter than Stage A.1, because headroom is thinner
now. The shared Databento account ledger stood at $84.01 of $120 after
Stage A.1, leaving $35.99 of shared headroom, and future stages (Stage
A.2 data confirmation, a possible later MNQ pull) will need some of
that. This session's tasks should need little or no new Databento data
— everything runs against the MES bars Stage A.1 already pulled. Cap
any new spend this session at $5.00 total, hard ceiling, quote-then-log
through the existing spend gate exactly as Stage A.1 did, same
shared-ledger check. If nothing in this session actually needs new
data, say so plainly in the report rather than pulling something
speculative just because budget exists.

TOOLCHAIN — continue what Stage A.1 established: uv for dependency
management, ruff for linting, pytest for tests. Do not introduce a
second toolchain for convenience.

============================================================
STAGE B — FUNNEL SIMULATOR (XFA BRANCH ONLY)
============================================================

This closes a deliverable promised in earlier project research and not
yet built: a null benchmark the eventual real strategy must beat,
computed before any strategy exists.

Stage B : Task 1 — Multi-day rules-engine integration tests.
Stage A.1's known-answer tests exercise rules/xfa_rules.py's functions
in isolation, one scenario each. This task chains many simulated
trading days together against the rules engine and confirms state
evolves correctly across sequences a single-scenario test wouldn't
catch: the trailing MLL ratcheting correctly across dozens of days with
mixed wins and losses, the Scaling Plan transitioning correctly as
balance crosses the $0 / $1,500 / $2,000 boundaries in both directions
(balance can fall as well as rise), multiple payouts in sequence each
correctly resetting the MLL and correctly restarting the consistency
window per the payout mechanics Stage A.1 discovered (net-profit-
since-last-payout requirement, request day excluded from the next
window), and the Combine's best-day-raises-target behavior interacting
correctly with an eventual pass once total profit clears the now-larger
target. Write these as tests/test_xfa_rules_sequences.py, separate from
the existing single-scenario known-answer tests rather than mixed into
that file.

Stage B : Task 2 — Null-strategy daily P&L generator.
Build a daily P&L generator that is explicitly zero-edge: a symmetric
random process calibrated to realistic MES daily volatility (derive the
volatility figure from the actual pulled bar data — do not invent a
number). This is not a strategy in the sense the strategy-scope
guardrail above forbids; it's an explicit statistical null, and its
zero-edge property must be a property you can point to in the code and
the tests, not just an assertion in a comment. Write it as
funnel/null_generator.py, with a test confirming its long-run
expectation is genuinely zero within a stated tolerance.

Stage B : Task 3 — Monte Carlo funnel simulator.
Using the null generator from Task 2 and the rules engine from
rules/xfa_rules.py, simulate the full Combine-to-XFA lifecycle
thousands of times (choose a sample size large enough for the output
distributions to be stable — check this explicitly by comparing results
at increasing sample sizes rather than picking a round number and
hoping). Consume sim/costs.py for realistic commission and slippage on
every simulated trade. For each run, model the account progressing from
Combine attempt through pass/fail, through XFA trading, through payout
requests on both the Standard and Consistency paths (run both paths as
separate scenarios, don't conflate them), tracking months-to-first-
payout, monthly payout income, and blowup events. Critically: explicitly
model up to 5 XFA accounts running the same underlying null-generator
draw (correlated, not independent), since a single bad sequence hits
every account's MLL together — this was identified as the key realism
gap in earlier research and must not be simplified away here. Output
the resulting distributions (pass rate, months-to-first-payout, monthly
income by path, correlated-blowup rate across the 5-account cluster) to
reports/funnel_null_baseline.md and a machine-readable
reports/funnel_null_baseline.json.

Stage B : Task 4 — Power gate.
Sweep the funnel simulator from Task 3 across a small grid of assumed
strategy quality — vary win rate, average win/loss ratio, and
trades-per-day across a reasonable range rather than one point each —
and compute, for each grid point, whether the resulting income
distribution beats the null baseline from Task 3 at a stated confidence
level (80% is a reasonable starting point, but state your choice and
reasoning rather than treating it as fixed). The output is a lookup
table or equivalent structured output mapping strategy-quality
combinations to pass/fail against the null, at the chosen confidence
level. This becomes the screening criterion Stage D.1 uses before
spending real research time on a candidate strategy. Write to
reports/power_gate.md plus a structured data file other code can
consume later.

============================================================
STAGE C — BACKTEST HARNESS
============================================================

Stage C : Task 1 — Strategy interface.
Define a minimal, frozen protocol/interface a strategy module must
implement: given a bar (with its Stage A.1 flag columns —
in_flatten_window, in_no_new_positions_window, in_scheduled_closure,
is_roll_session, vendor_degraded_day, and the rest) and current account
state, emit zero or more order intents shaped to fit directly into the
rules/xfa_rules.py gate from Stage A.1 with no translation layer needed
in between. Follow the same frozen-dataclass, refuse-at-construction
shape used for the rules engine's own intent type — consistency of
pattern matters here since this interface is what Stage D.1 will build
against later. Provide exactly two reference implementations, both
explicitly non-strategies per the strategy-scope guardrail: a null
implementation that never emits an intent, and a random baseline that
emits intents from an unconditional coin-flip, purely to exercise the
harness's mechanics end to end. Write to strategy/interface.py,
strategy/null_strategy.py, strategy/random_baseline.py.

Stage C : Task 2 — Event-driven backtest engine.
Replay the Stage A.1 MES bars in strict chronological order (this is
the loop the ETA probe above already built a thin version of — extend
it, don't restart it). Feed each bar to the strategy interface from
Task 1, collect any emitted intents, evaluate them through the rules
engine and the fill model (Task 3), and maintain a complete
account-state ledger across the full run: every intent, every fill,
every rule check, timestamped and reconstructable after the fact. The
engine must respect the flag columns as hard constraints, not advisory
ones — an intent emitted during in_flatten_window or
in_scheduled_closure should be structurally rejected by the engine
itself, not merely flagged. Write to sim/engine.py.

Stage C : Task 3 — Fill model integration.
Wire the engine from Task 2 to sim/costs.py's slippage calibration,
applying the correct time-of-day and size bucket to every fill. State
explicitly, in a code comment and again in the final report, the
caveats Stage A.1 already flagged and that must not be quietly
forgotten here: the calibration rests on two days of book data, and
excludes latency, adverse selection, and queue position. This is not a
reason to skip using it — it's the best available model — but the
engine's output should not be presented anywhere as more realistic than
it is.

Stage C : Task 4 — Leakage suite with planted-future canaries.
This is the standing methodology for every project in this research
program and is not optional. Construct a copy of the bar data with
synthetic signals deliberately injected that are correlated with future
information relative to any point in the backtest — for example, a
marker on bar N that is a near-perfect predictor of bar N+1's return
direction, constructed so that a leaky implementation would show
implausibly strong performance and a correctly point-in-time
implementation would show none. Run the engine from Task 2 against this
planted data using the random baseline from Task 1, and confirm the
harness shows no exploitable performance from the planted signal. If it
does show exploitable performance, that is a real defect in the
engine's point-in-time discipline and must be fixed before anything
else in this session is considered trustworthy — treat a canary catch
as a stop-the-line event, not a minor finding to note and move past.
Write the suite and its results to tests/test_leakage_canaries.py and
reports/leakage_suite.md.

Stage C : Task 5 — Walk-forward split construction.
Partition the 17.5-month MES history into rolling walk-forward
train/test windows. Choose window lengths and step sizes with explicit
reasoning tied to the data actually available, not arbitrary round
numbers. Separate out a final holdout slice that will not be touched by
any training or tuning work — this slice is reserved exclusively for
Stage D.2.

Stage C : Task 6 — Sealed-holdout lockout mechanism.
This must be a structural barrier, not a naming convention or a comment
saying "don't touch this." Design and build an actual mechanism that
makes it mechanically difficult for a future session to read the
holdout slice by accident or convenience: for example, store the
holdout data in a separate path, compute and record a checksum manifest
of it at creation time, and gate any code path that would load it
behind an explicit, logged unlock step that writes a dated entry to a
file specifically for this purpose (e.g., docs/HOLDOUT_UNLOCK_LOG.md)
rather than a silent file read. The exact mechanism is your design
call, but the bar is: a future session working carelessly under time
pressure should still have to do something deliberate and logged to
see this data, not just open() a file that happens to be sitting right
there in the repo tree.

Stage C : Task 7 — Known-answer tests for the engine itself.
Construct a small, fully synthetic, hand-computable price series and a
trivial deterministic strategy (not one of the Task 1 reference
implementations — a third, throwaway one built only for this test, e.g.
"buy on bar 1, sell on bar 10, nothing else"). Hand-compute the
expected P&L including commission and the exact slippage the fill
model should apply, and confirm the engine's output matches to the
cent. This is the engine-level equivalent of Stage A.1's rules-engine
known-answer tests, and it's what makes every later backtest result
trustworthy rather than merely plausible-looking. Write to
tests/test_engine_known_answer.py.

============================================================
IF TIME RUNS OUT OVERNIGHT — PRIORITY ORDER, DO NOT SILENTLY REORDER
============================================================

If the ETA probe or actual progress shows the full list won't complete:
finish Stage B entirely first (it's smaller, and it closes a specific
deliverable promised in prior research). Within Stage C, Tasks 1 through
3 and Task 7 are core and should not be cut. Task 4 (leakage canaries)
must never be cut silently — if you cannot complete it, say so
explicitly and mark every other Stage C output as provisional pending
that suite, since nothing built on top of a backtest engine is
trustworthy until its point-in-time discipline is proven. Tasks 5 and 6
(walk-forward and the sealed holdout) can be the last thing cut if
genuinely necessary, since Stage D.1 and D.2 are separate future
sessions regardless and there's no immediate downstream consumer of the
holdout mechanism yet — but note clearly in progress.md if this
happens, since it directly blocks Stage D.2 later.

============================================================
DELIVERABLE
============================================================

A dated progress.md entry: the probe-derived ETA and how actual time
compared to it, what was delegated to subagents and at what effort tier
versus what you handled directly, full results from Stage B's funnel
and power-gate outputs, full results from Stage C's leakage suite (with
explicit pass/fail, not just "ran"), what was cut if anything and why
per the priority order above, exact new Databento spend against the
$5/$35.99 caps, and a clean list of what Stage D.1 will need from this
session's outputs to get started.

END PROMPT
