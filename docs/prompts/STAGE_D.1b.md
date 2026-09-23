STAGE D.1b "C-H4 AND FAMILY F: NEXT HYPOTHESIS ROUND"

Model: Opus 5, high effort.

Reasoning: this session is one moderately complex thread (Family F, which
needs continuous exploratory-design judgment) plus one small, well-
specified addition (C-H4), not five independently parallelizable
investigations the way Stage D.1's literature sweep was. It does not meet
the standing bar for ultracode. C-H4's implementation is a reasonable
Sonnet-delegation candidate once its spec is restated below — the
mechanism is already fully described in Stage D.1's own literature log,
nothing new needs discovering. Family F's feature enumeration, its
hypothesis cap, and every statistical judgment in this session stay with
the lead, specifically because Family F is exploratory-search work, and
the whole point of the guardrails below is to keep that kind of work from
becoming the unconstrained data-mining session that was explicitly
rejected as too risky a few sessions ago. State in the final report
exactly what was delegated and what stayed in-house.

============================================================
CONTEXT — READ BEFORE STARTING ANYTHING
============================================================

Working directory: /home/kiros-li/Documents/GitHub/PropExperiment. Read
README.md, docs/DECISIONS.md, docs/STAGES.md, docs/SCREENING.md, and the
full progress.md entries for Stage D.1 and Stage D.1a before starting.
docs/SCREENING.md is the contract for this session: every backtest run
in this session, for both C-H4 and any Family F hypothesis, goes through
screen_candidate(label, factory, window) from the shared runner. Do not
construct an EngineConfig by hand and do not call run_backtest directly
for anything that is meant to count as a screening result — the runner
now refuses to build a config without an explicit roll_blackout for
exactly the reason Stage D.1's B/D partitioning failure happened, and
bypassing the documented safe path defeats that fix.

Two facts from Stage D.1a to carry forward without re-deriving:
- Pure clock-seasonality hypotheses cannot clear the drift check
  in-sample by construction — their entire P&L is the average price
  path the benchmark measures against. Don't spend a Family F trial on
  one without an explicit out-of-sample argument for why it's worth
  testing anyway.
- A composite pass now requires both the robust zero-edge verdict AND
  the drift benchmark's two sub-checks (significant excess over the
  unconditional counterpart, and drift-adjusted p/R clearing the robust
  gate). Read a "pass" as meaning both, not either.

CREDENTIAL, STRATEGY-SCOPE, AND HOLDOUT GUARDRAILS — unchanged and
non-negotiable, carried forward from every prior session. No TopstepX
reference of any kind. Nothing under live/ or ops/. Do not unlock the
sealed holdout under any framing; check `python -m data.holdout status`
before, during, and after, and confirm `unlocks_logged: 0` in the final
report.

SPEND GUARDRAIL: cap new Databento spend at $10 total, quote-then-log
through the existing gate, exactly as every prior session. This session
should need no new data — C-H4 and Family F both run on the existing
517,197-bar MES series and the data already used in Stage D.1's research.
Do not use this session to acquire the order-book days, second instrument,
or longer history Stage D.1 and D.1a both flagged as needed for future
work — those remain the user's separate decision, not something to fold
in here.

TOOLCHAIN: uv, ruff, pytest, as established.

============================================================
TASK 1 — C-H4: REVERSAL WITH PASSIVE FILLS
============================================================

This is the trial Stage D.1's Task 1 literature log identified as its
strongest-sourced idea in the reversal family, and the reason it wasn't
run then is exactly the gap Stage D.1a closed: it needs passive/limit
fills to be a meaningful test, since a reversal idea that only works with
market-order entries is a materially different (and much more
cost-sensitive) claim than one that can rest and wait.

Go back to Stage D.1's own logged research for family C
(short_horizon_reversal) and use the mechanism as it was originally
sourced and described there — do not re-derive or reinterpret it from
scratch, and do not go looking for new literature this session; the
sourcing work is already done and logged. Formalize it as a concrete
implementation of strategy/interface.py (INTERFACE_VERSION = 2, using
limit_intent as Stage D.1a built it), with the same pre-specification
discipline every prior hypothesis has used: state what would count as
support and what would count against before running it.

Screen it through screen_candidate on fold 0's train window first, then
across all 8 train folds if it clears the robust verdict there, exactly
as Stage D.1's protocol required for anything promising. Every
PASSIVE_FILL_CAVEATS this result carries (queue position, market impact,
volume-at-level, latency) must be stated plainly in the log entry for
this trial, not left implicit because "the runner attaches them
automatically" — a human reading the log later should not have to go
find the runner's source to know what this result does and doesn't
account for.

This is trial number 24. It counts toward the cumulative N exactly as
every other trial does.

============================================================
TASK 2 — FAMILY F: BOUNDED, DECLARED-IN-ADVANCE DATA-NATIVE EXPLORATION
============================================================

This task exists because of a specific concern raised and agreed on in
an earlier session: letting an agent explore raw price data and "find its
own strategy" is data snooping by another name, with no countable trial
space and nothing external to check a discovered pattern against. The
structure below exists specifically to prevent that failure mode while
still allowing genuine data-native discovery. Every guardrail in this
task is load-bearing — do not skip or loosen one because it seems slow.

--- TASK 2a — DECLARE THE FEATURE SPACE FIRST, BEFORE COMPUTING ANYTHING ---

Before running any exploratory computation on the MES bar data, write
down and log a fixed, enumerated list of the statistical properties you
intend to examine. This list must be complete before Task 2b starts — do
not add an item to it after seeing what an earlier item's result looked
like. A reasonable starting enumeration (adjust as needed, but decide and
log the final list before proceeding, not while proceeding):

- autocorrelation structure of returns at several fixed horizons;
- volatility clustering / regime persistence measures;
- session-conditional distributional properties (RTH vs ETH, by
  time-of-day bucket) that are NOT already covered by families A through
  E's existing screened trials;
- any distributional asymmetry around the daily open, the prior day's
  close, or round-number price levels, stated precisely enough to be
  computed without further judgment calls later;
- volume/range relationships not already tested by family D.

If you believe a property outside this starting list is worth adding,
add it to the declared list now, before computation, and say why. The
list, once computed against, is closed — any additional idea that occurs
to you DURING Task 2b goes into a separate "ideas for a future round"
note in the log, not into this session's feature space.

--- TASK 2b — COMPUTE STYLIZED FACTS ONLY, NO SIGNALS, NO P&L ---

For each declared feature, compute and log the statistical finding
itself: a number, a distribution, a described pattern. This step
produces NO strategy code, NO entries, NO exits, and touches
strategy/interface.py for nothing. If a feature under examination turns
out to closely resemble something a family A-E trial already tested
(check against Stage D.1's logged mechanisms before treating anything as
novel), say so explicitly and do not double-count it as a new discovery.

--- TASK 2c — FORMALIZE A CAPPED NUMBER OF HYPOTHESES ---

From the stylized facts in Task 2b, select at most 6 to formalize as
testable strategy/interface.py implementations, with the same
falsification-condition discipline as every prior family. Six is a hard
ceiling for this session without an explicit, logged justification for
why fewer would leave an obviously strong finding untested — this cap
exists because an EDA pass can generate far more plausible-sounding
candidate ideas per hour than literature search does, and the whole
point of this task's structure is to keep that from turning into
runaway trial generation. If Task 2b's stylized facts suggest more than
6 candidates worth testing, rank them and log the ones NOT selected with
your reasoning, rather than silently dropping them.

--- TASK 2d — SCREEN THROUGH THE SHARED RUNNER, LOG EVERY TRIAL ---

Screen each formalized hypothesis through screen_candidate exactly as
Task 1 does, fold 0 first, full 8-fold spread for anything clearing the
robust verdict. Log every one, pass or fail, with the same rigor as
Stage D.1's per-item logging — this is not optional for the ones that
fail any more than it was in D.1.

============================================================
TASK 3 — CUMULATIVE MULTIPLE-COMPARISONS ACCOUNTING
============================================================

This is not a re-run of Stage D.1's Task 4 in isolation — it is an
update to the SAME accounting, carried forward. The trial count going
into this session's accounting is N = 23 (Stage D.1) + 1 (C-H4) + however
many Family F hypotheses were formalized in Task 2c, not a fresh count
starting from 1. Recompute the Deflated Sharpe Ratio, the Harvey/Liu/Zhu
t-hurdle comparison, and the Probability of Backtest Overfitting
treatment from Stage D.1's Task 4 using this full cumulative N, on the
full cumulative set of trials (all 23 original plus this session's), not
only on this session's new trials in isolation. A candidate that would
look significant judged only against this session's small trial count
but not against the true cumulative count is exactly the false-positive
risk this accounting exists to catch.

If C-H4 or any Family F candidate clears the robust verdict AND the
drift benchmark AND still looks meaningful under the cumulative
accounting, extend it across all 8 train folds and report the
fold-stability spread, exactly as Stage D.1's protocol required for any
survivor.

============================================================
TASK 4 — SHORTLIST UPDATE, NOT A RESET
============================================================

Stage D.1's shortlist was empty. This task updates that same shortlist
with this session's results — it does not start a new one. If nothing
here clears Task 3's cumulative bar either, say so as plainly as Stage
D.1's report did, and do not soften an honest second consecutive null
result into something that sounds more promising than it is. If
something does clear the bar, apply the same anti-premature-convergence
discipline as Stage D.1's Task 5: don't declare a single winner, don't
imply Stage D.2 readiness, and if multiple candidates pass, carry
forward the genuinely distinct ones rather than collapsing to the
best-looking number. That decision, including whether and when to write
to REGISTRATION.md, remains the user's to make in a separate session.

============================================================
DELEGATION
============================================================

C-H4 (Task 1) is a reasonable candidate for a Sonnet-effort subagent to
implement once you've restated its spec from Stage D.1's log — the
mechanism is already sourced and described, this is mechanical
translation into strategy/interface.py plus running it through the
shared runner, not a judgment call. Family F's Task 2a (feature
enumeration) and Task 2c (the cap and what makes the cut) must stay with
the lead — these are exactly the design decisions where a plausible-but-
wrong choice would fail silently, the same category flagged for Tasks 1
and 2 in Stage D.1a. Task 2b's raw computation, once the feature list is
fixed, is delegable. Task 3's cumulative accounting stays with the lead
in full. State the delegation breakdown in the final report.

============================================================
WHAT NOT TO DO
============================================================

Do not compute any Family F feature that wasn't declared in Task 2a
before computation started. Do not formalize more than 6 Family F
hypotheses without an explicit, logged justification. Do not treat this
session's trial count in isolation for Task 3 — the cumulative N from
Stage D.1 is the real denominator. Do not unlock the sealed holdout. Do
not write to REGISTRATION.md. Do not touch live/, ops/, or anything
TopstepX-shaped. Do not build a new EngineConfig by hand anywhere in
this session — use the shared runner exclusively.

============================================================
DELIVERABLE
============================================================

A dated progress.md entry: C-H4's formalization, screening result, and
caveats; Family F's declared feature list (Task 2a) logged before any
computation; the stylized facts found (Task 2b); the up-to-6 formalized
hypotheses and the reasoning for what was and wasn't selected (Task 2c);
every Family F trial's screening result, pass or fail (Task 2d); the
updated cumulative multiple-comparisons accounting against the true N
(Task 3); the updated shortlist, honestly stated whether it's still
empty or not (Task 4); the delegation breakdown; and, if the shortlist
is still empty, a clear statement of whether this program should keep
searching for a strategy or whether two consecutive clean nulls across
28+ trials is itself a signal worth discussing with the user directly.

END PROMPT
