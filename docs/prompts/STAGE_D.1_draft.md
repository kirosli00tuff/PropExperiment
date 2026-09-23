STAGE D.1 "STRATEGY RESEARCH AND HYPOTHESIS SCREENING"

Model: Opus 5, ultracode effort.

Reasoning: this session genuinely divides into parallel, independent
hypothesis investigations (different strategy families researched and
screened by different subagents) synthesized by a lead who owns
statistical rigor, the multiple-comparisons guardrail, and the final
honest accounting of what was tried and what worked. Matches the
standing rule for ultracode exactly as Stage B-C did. State in the final
report which hypotheses were delegated to which effort tier.

============================================================
SCOPE — READ THIS BEFORE ANYTHING ELSE
============================================================

This session does two things and two things only: investigate candidate
trading strategies, and screen them against the existing harness on
train-fold data. It does NOT build new backtest infrastructure, does NOT
touch live/ or ops/, does NOT touch TopstepX in any way, and above all
does NOT unlock the sealed holdout under any circumstance.
REGISTRATION.md stays empty unless and until a specific candidate is
ready for Stage D.2, and that decision is the user's to make in a
future session, not this one's to trigger.

Working directory: /home/kiros-li/Documents/GitHub/PropExperiment. Read
README.md, docs/DECISIONS.md, docs/STAGES.md, and the full progress.md
entries for Stage A.1 and Stage B-C before starting anything. In
particular, understand and do not rebuild:

- strategy/interface.py (INTERFACE_VERSION = 1) — the contract every
  candidate must implement: on_bar(bar, account) -> Sequence[OrderIntent].
- sim/engine.py and sim/fill_model.py — the harness.
  sim.engine.run_backtest(bars, strategy, EngineConfig(...), table) is
  how a candidate gets tested. The cost caveats from Stage C (two-day
  slippage calibration, no latency/adverse-selection/queue-position
  modeling) still apply to every result this session produces.
- funnel/power_gate.py — screen(path, win_probability, win_loss_ratio,
  segments_per_day) against reports/power_gate.json. This is the
  pass/fail bar before a hypothesis earns more than a cursory look.
  Practical thresholds already established: R >= 1.5 with p >= 0.55, or
  R = 2.0 with p >= 0.50, at roughly 1 round turn/day. Use the robust
  verdict, not the matched one, when deciding whether something is worth
  carrying forward — the matched null was already shown to overstate
  apparent edge.
- data/splits.py — 8 walk-forward folds, 311 research trade dates,
  non-overlapping test windows. Fit and tune on train folds. Report
  out-of-sample results from test folds. Never touch the holdout.
- data/holdout.py and docs/HOLDOUT_MANIFEST.json — the seal. Any code
  path that would call an unlock function is out of scope for this
  session, full stop, regardless of how promising a candidate looks. If
  you find yourself reasoning about whether a peek would be justified,
  that reasoning itself is the signal to stop and flag it in the report
  instead.

CREDENTIAL AND STRATEGY-SCOPE GUARDRAILS carried forward unchanged: no
TopstepX reference of any kind; nothing under live/ or ops/.

SPEND GUARDRAIL: this session should need no new Databento spend,
everything runs on data already pulled. If a genuine gap emerges (a
specific hypothesis needs a data series not already on disk, e.g. a
different instrument for a cross-asset idea), cap any new spend at $10
total, quote-then-log through the existing gate exactly as prior
sessions did, and the gate already refuses anything overlapping the
sealed holdout window automatically.

============================================================
TASK 1 — LITERATURE AND COMMUNITY INVESTIGATION
============================================================

This task requires actually scraping and reading full source material,
not summarizing search-result snippets. Search-engine snippets are a
starting point for finding sources, not a substitute for reading them.
Use whatever web-scraping and article-fetching tools are available in
this environment to retrieve full text wherever a source allows it, and
say plainly in the log when a source could not be fully retrieved
(paywall, scrape blocked, etc.) rather than substituting a snippet
summary and presenting it as if the full text were read.

SSRN specifically: search SSRN directly for empirical or methodological
papers on intraday and short-horizon systematic strategies in liquid
equity-index futures or closely comparable instruments. Retrieve and
read full abstracts at minimum, and full papers wherever accessible,
rather than relying on a third-party summary of an SSRN paper found
elsewhere. Prioritize papers with actual measured results (win rates,
Sharpe figures, holding periods, cost assumptions) over purely
theoretical pieces, and note each paper's cost/slippage assumptions
explicitly when extracting a result — a paper's edge is only as
credible as its cost model, exactly as this program's own cost-model
discipline requires of its own backtests.

Beyond SSRN, use web search and article scraping across the broader
literature and practitioner/community sources (quant research blogs,
exchange or vendor research notes, relevant academic working papers
outside SSRN) for the same subject matter. Areas worth covering, not
exhaustive: opening-range and time-of-day effects, volatility/regime-
based entries, mean-reversion around VWAP or similar reference prices,
momentum/trend continuation on short horizons, order-flow or volume-
based signals achievable from OHLCV-only data (the dataset on disk has
no order-book depth beyond what Stage A.1's two tick days already used
for cost calibration), and any documented failure modes specific to MES
or CME equity-index futures that would rule a family out before
spending backtest time on it.

Note on scope, to avoid confusion with a previously shelved idea: this
task is literature and research retrieval, not live sentiment or
social-media data collection. A separate social-media web-scraping
capability was discussed and deliberately shelved in an earlier session
specifically because it risked starting strategy work outside proper
staging — that decision stands and is unaffected by this task. If any
avenue in this task's research turns up a reason to seriously consider
social or sentiment data as a signal source, note it in the log as a
candidate for a future, separate, properly-scoped evaluation. Do not
attempt to build or test a sentiment-based hypothesis in this session.

One directly relevant prior result from this research program to weigh
seriously: ORBExperiment (a different instrument, QQQ, not futures)
found that measured slippage on the traded population ran 11.27x the
slippage carried into the original cost assumption, which was enough to
erase the strategy's apparent edge entirely. That is direct evidence in
this program's own history that a strategy can look profitable on
optimistic costs and fail on realistic ones. Treat every candidate's
apparent edge, including any edge reported in a scraped paper, as
provisional until it survives the actual fill model in
sim/fill_model.py, not a hand-waved cost assumption from the source
material.

For every strategy family investigated, whether or not it proceeds to
Task 2, log it: the source (with URL/citation), the core mechanism in
one or two sentences, the source's own stated cost assumptions if any,
and the reason it was or wasn't carried forward to backtesting. This
log is not optional and is not just for the winners — it is the record
that lets Task 4's multiple-comparisons accounting be honest rather than
survivorship-biased.

============================================================
TASK 2 — HYPOTHESIS FORMALIZATION
============================================================

For each strategy family carried forward from Task 1, write it as a
concrete, testable implementation of strategy/interface.py before
running anything. State explicitly, before backtesting, what result
would count as support and what would count against — this is the
pre-specification discipline the program's methodology requires, applied
at hypothesis level even though the formal REGISTRATION.md gate is
reserved for an eventual Stage D.2 candidate, not for this exploratory
stage. A hypothesis with no stated falsification condition is not ready
for Task 3.

============================================================
TASK 3 — SCREENING AGAINST TRAIN FOLDS ONLY
============================================================

Run each formalized hypothesis through sim.engine.run_backtest against
train-fold data only, using data.splits.walk_forward_folds(...). For
each, measure the actual win probability, win/loss ratio, and
trades/day the hypothesis produces, then run those measured figures
through funnel.power_gate.screen(...) to get a real verdict rather than
a guessed grid-point lookup. Record every hypothesis tested here in the
same log from Task 1, pass or fail, not just the ones that clear the
gate.

For anything that passes the robust verdict, extend the test across all
8 train folds (not just one), and report the spread across folds, not
just an aggregate. A hypothesis that looks strong on one fold and falls
apart on others is a strong candidate for overfitting to that fold's
specific regime, and that instability is itself a finding worth
recording, not a result to average away.

Run uv run pytest tests/test_leakage_canaries.py after any change to how
a strategy consumes bar data, before trusting any of its backtest
numbers. A failure here is a stop-the-line event exactly as it was in
Stage C.

============================================================
TASK 4 — MULTIPLE-COMPARISONS ACCOUNTING
============================================================

This is the task that keeps Task 3's results honest. Report the total
count of hypotheses formalized and tested in Task 2/3, not just the ones
that passed. State plainly what testing many hypotheses against the same
train folds does to the odds that at least one clears the power gate by
chance alone, and apply a stated correction or at minimum a stated
adjustment to how much confidence the report places in any single
passing result. A candidate that only survives when its individual
p-value or robust-verdict margin is read in isolation, without
accounting for how many other candidates were tried against the same
data, is not ready to be called promising.

============================================================
TASK 5 — RANKED SHORTLIST, NOT A SINGLE WINNER
============================================================

Produce a ranked shortlist of candidates that cleared Task 3's robust
verdict and Task 4's accounting, with each candidate's measured
p/R/trades-per-day, its fold-stability spread, and an honest note on
what would need to be true in the held-out period for it to actually
work live. Do not declare a single winner or imply readiness for Stage
D.2 — that decision, including whether and when to write a real
pre-registration into REGISTRATION.md, is explicitly the user's to make
in a separate future session, informed by this shortlist, not concluded
by this one.

============================================================
DELEGATION
============================================================

Delegate independent hypothesis families (Task 1 through Task 3, end to
end, for a given family) to Sonnet-effort subagents running in parallel,
since they are genuinely independent investigations. Keep in-house: the
multiple-comparisons accounting in Task 4, the fold-stability judgment
in Task 3, any decision about whether a result is real or an artifact,
and the final shortlist and report. State the delegation breakdown in
the final report exactly as Stage B-C's report did, auditable after the
fact.

============================================================
WHAT NOT TO DO
============================================================

Do not unlock or attempt to unlock the sealed holdout, under any
framing, even a hypothetical "just to check" framing. Do not write to
REGISTRATION.md. Do not build new backtest infrastructure, extend
sim/engine.py's core mechanics, or duplicate what Stage C already
delivered — if a hypothesis needs a capability the harness doesn't have,
note that as a limitation in the report rather than building around it
silently. Do not touch live/, ops/, or anything TopstepX-shaped. Do not
build or test any social-media/sentiment-based signal — that remains
shelved from an earlier session, unaffected by this prompt's literature-
scraping requirement.

============================================================
DELIVERABLE
============================================================

A dated progress.md entry: the full hypothesis log from Task 1 (every
family considered, carried forward or not, why, and its source
citation), the full test log from Task 3 (every formalized hypothesis,
pass or fail), the multiple-comparisons accounting from Task 4, the
ranked shortlist from Task 5, the delegation breakdown, and a clean
statement of what a future session would need to do to move any
shortlisted candidate toward a real Stage D.2 pre-registration.

END PROMPT
