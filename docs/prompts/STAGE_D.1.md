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

--- TASK 1a — RELEVANCE PRE-FILTER, DO THIS FIRST, PER SOURCE ---

A prior research pass (see the directory in Task 1b below) already
identified the highest-yield source categories and flagged each one's
likely relevance to MES / ES / NQ / CME equity-index-futures work as
HIGH, MEDIUM, or LOW. Use that as your starting prioritization, but
every individual paper, post, or item you actually encounter within a
source still needs its own quick pre-filter before you spend any real
effort on it. The pre-filter is cheap and mandatory:

1. Read the abstract/summary/lede only — title, abstract, and first
   paragraph or equivalent. Do not fetch full text yet.
2. Ask one question: does this item concern MES, ES, NQ, the E-mini/
   Micro E-mini S&P 500 or Nasdaq-100 complex, or CME-listed equity-
   index futures specifically (or, failing that, a liquid futures/
   index-derivatives market close enough in microstructure that the
   mechanism plausibly transfers — e.g. another deep, exchange-traded,
   continuously-quoted index or rates futures market)? A paper that is
   generic multi-asset factor investing, purely equities/cash-market
   microstructure with no futures angle, purely crypto, purely FX, or
   purely commodity-specific (agricultural, energy-specific mechanics)
   with no stated relevance to index futures does NOT pass.
3. If it does not pass: log it in one line (source, title/item, one-
   phrase reason for rejection) and move on immediately. Do not fetch
   full text, do not summarize further, do not spend a subagent turn
   on it beyond this one line. This is the credit-saving mechanism —
   treat it as a hard filter, not a soft preference.
4. If it does pass: proceed to full-text retrieval and the full
   logging requirements below. While reading the full text, flag
   source-quality tells rather than accepting claims at face value:
   speculative language presented as fact (verbs like "could" or
   "may" dressed up as findings), unnamed or vague sourcing ("industry
   experts suggest"), cherry-picked or unrepresentative data windows,
   marketing language for a specific product or vendor, and news
   aggregation rather than primary research. Note any of these
   directly in the Task 1c log entry for that item rather than
   silently discounting the source and moving on, so the final report
   shows what was weighted down and why.

This pre-filter applies to every item from every source, including the
HIGH-relevance sources in Task 1b — a HIGH-relevance source (e.g. an
SSRN eJournal) still contains plenty of individual papers with no
futures angle, and those still get the one-line skip, not full
treatment, just because the container is generally strong.

--- TASK 1b — STARTING SOURCE DIRECTORY ---

Use this directory as your initial source list rather than starting
discovery from zero. Relevance flags below are the prior pass's own
assessment of the SOURCE/container as a whole; Task 1a's per-item
pre-filter still governs what you actually read in full within each
one.

SSRN (relevance: HIGH):
  - "Capital Markets: Market Microstructure eJournal" (curated by
    Stephen Figlewski, NYU Stern) — core microstructure container,
    browse for intraday/order-flow/price-impact papers.
  - "Derivatives eJournal" (also Figlewski) — broader derivatives
    coverage including index futures/options.
  - Adjacent/secondary containers: "Econometric Modeling: Derivatives
    eJournal," "Commodities eJournal," "Global Exchanges eJournal."
  - Named author cluster to search directly and pull citation graphs
    from: Torben G. Andersen (Kellogg/Northwestern), Oleg Bondarenko
    (UIC), Albert S. "Pete" Kyle (Maryland), Anna A. Obizhaeva (New
    Economic School). Anchor/seed paper: SSRN abstract_id=2693810,
    "Intraday Trading Invariance in the E-Mini S&P 500 Futures
    Market" — use this paper's own citations and any paper citing it
    as a fast way to expand the relevant set.
  - Note: SSRN's public rankings/top-author tables are retired: browse
    eJournal pages and author pages directly rather than relying on a
    league-table shortcut.

arXiv (relevance: MEDIUM-HIGH, screen per-paper):
  - q-fin.TR (Trading and Market Microstructure) — primary category.
  - q-fin.ST (Statistical Finance) — secondary.
  - q-fin.CP (Computational Finance) — tertiary/adjacent.
  - Expect a high rejection rate here under Task 1a — much recent
    q-fin.TR futures content is China index futures (CSI 300) or
    crypto perpetuals, which do not pass the pre-filter unless the
    mechanism is explicitly argued to transfer.

Vendor / exchange / regulator desks (relevance: HIGH, native ES/MES/NQ
coverage, actively publishing):
  - CME Group: Quarterly Equity Insights newsletter (ADV/OI/roll
    analytics across ES/NQ/MES/MNQ), CME market-structure articles,
    Equity Index Data pages.
  - Databento: blog and Microstructure Guide glossary, ES/MES worked
    examples.
  - Nasdaq: "The Print" (Phil Mackintosh) and Nasdaq Economic
    Institute / Index Insights — more NDX/US-equities market
    structure than CME-specific, but relevant NQ content exists.
  - CFTC Office of the Chief Economist: White Papers / Research Papers
    using CME regulatory data, several explicitly on the S&P E-mini
    (liquidity, automated trading, futures market landscape).

Practitioner blogs (relevance: MEDIUM, treat as discovery layer, hold
to the pre-filter strictly — most content here is generic systematic/
factor material, not equity-index-futures-specific):
  - Jonathan Kinlay (jonathankinlay.com) — has a dedicated E-mini/HFT
    archive, the most directly relevant of this group.
  - Quantitative Brokers (quantitativebrokers.com/blog) — futures
    execution/microstructure, institutional.
  - Robert Carver (qoppac.blogspot.com, systematicmoney.org) —
    systematic futures generally, mostly daily/medium-frequency, not
    intraday microstructure; low individual-item pass rate expected.
  - Robot Wealth (robotwealth.com) — systematic trading education,
    some index/VIX content; low individual-item pass rate expected.
  - Aggregator to skim for links into the above, not as a primary
    source itself: Quantocracy (quantocracy.com) daily mashup.

LOW-relevance, deprioritize, only dip in if a specific item is
flagged as directly relevant by name from elsewhere: Alpha Architect
(factor/asset-pricing focus), QuantInsti (education-oriented),
generic GitHub "awesome-quant" style lists, Quantpedia's general
screener (useful only if filtered directly to equity-index-futures
instruments).

--- TASK 1c — LOGGING AND CITATION VERIFICATION ---

For every strategy family investigated, whether or not it passed the
Task 1a pre-filter, log it: the source (with URL/citation), the core
mechanism in one or two sentences (for passed items) or the one-phrase
rejection reason (for filtered-out items), the source's own stated cost
assumptions if any (for passed items), and the reason it was or wasn't
carried forward to Task 2.

Citation verification is a separate, mandatory pass, not something to
trust from memory while writing the log. Before any claim from a
source enters the log or later feeds Task 2, confirm it against the
actual fetched text: a claim is only logged as sourced if you can
point to the specific passage in the retrieved full text that supports
it. Do not log a claim you recall from a search snippet, a summary
generated earlier in the session, or general background knowledge as
if it came from the source itself — mark anything you cannot pin to
retrieved text as [unverified] rather than dropping it or silently
upgrading it to a sourced claim. This applies with extra weight to any
numeric result (a win rate, a Sharpe figure, a reported edge) — these
get re-checked against the source's own text before they influence
which hypotheses proceed to Task 2, since a fabricated or misquoted
number here would propagate directly into a formalized hypothesis. This log is not optional and is not just for
the winners — it is the record that lets Task 4's multiple-comparisons
accounting be honest rather than survivorship-biased, and it is also
the evidence that the pre-filter in Task 1a is being applied honestly
rather than used to quietly skip inconvenient sources.

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
chance alone, and apply a stated, named correction rather than a vague
adjustment. Specifically: compute or estimate a Deflated Sharpe Ratio
for each surviving candidate, accounting for the actual number of
trials logged in Task 1/3, not just the trials that happened to pass;
apply the Harvey/Liu/Zhu-style stricter significance hurdle (t > 3.0
rather than the conventional t > 2.0) given the number of
configurations tried; and, where feasible given the existing
data.splits.walk_forward_folds(...) structure, estimate a Probability
of Backtest Overfitting across the fold results from Task 3 rather
than reading a single aggregate figure as decisive. If any of these
cannot be computed exactly with what's available in the repo, say so
explicitly and use the closest available approximation, documenting
the approximation rather than silently substituting a softer,
unnamed heuristic. A candidate that only survives when its individual
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

Guard explicitly against converging on the shortlist too early or too
narrowly. If Task 3 produces more than one candidate clearing the
robust verdict, the shortlist must carry forward multiple genuinely
distinct hypothesis families rather than collapsing toward the single
best-looking number — a strong Deflated Sharpe on one candidate is not
a reason to stop investigating or reporting on the others that also
passed. If subagents investigating different families independently
arrive at similar or overlapping mechanisms, note that convergence
explicitly in the report as a finding in its own right (it may
indicate a genuinely robust effect, or it may indicate the sources
themselves are not independent), rather than treating agreement across
subagents as automatic confirmation.

============================================================
DELEGATION
============================================================

Delegate independent hypothesis families (Task 1 through Task 3, end to
end, for a given family) to Sonnet-effort subagents running in parallel,
since they are genuinely independent investigations. The Task 1a
pre-filter is exactly the kind of mechanical, well-specified work a
Sonnet subagent should handle on its own without escalating to the lead
for judgment calls — a source either names MES/ES/NQ/equity-index
futures or it doesn't, and that determination does not need Opus-level
reasoning. Keep in-house: the multiple-comparisons accounting in Task 4,
the fold-stability judgment in Task 3, any decision about whether a
result is real or an artifact, and the final shortlist and report.

Scale the number of subagents to the actual complexity of the
investigation, not by default habit. As a starting rule: 2-3 subagents
for a narrow, well-bounded set of hypothesis families; 4-6 for a
broader sweep across the source directory in Task 1b; do not exceed 10
subagents in this session without an explicit, logged reason for why
fewer would leave real hypothesis space uncovered. More subagents is
not automatically better — it multiplies token cost and, absent clear
boundaries, multiplies duplicate work, not coverage.

Before dispatching subagents, the lead must partition the hypothesis
space into explicitly non-overlapping regions and assign one region
per subagent, stated in enough detail that two subagents could not
reasonably end up investigating the same underlying mechanism from
different angles (e.g., don't send one subagent after "momentum
strategies" and another after "trend continuation" as if these were
distinct — that is exactly the kind of overlap that wastes a full
subagent's budget re-covering ground another already covered). If, once
subagents report back, two turn out to have converged on overlapping
territory despite this, note that explicitly in the final report as a
partitioning failure, not just as a finding.

State the delegation breakdown in the final report exactly as Stage
B-C's report did — subagent count, each one's assigned non-overlapping
region, and effort tier — auditable after the fact.

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
scraping requirement. Do not skip the one-line logging requirement for
pre-filtered-out items even though they're being rejected quickly — an
unlogged rejection is indistinguishable from a source that was never
checked at all, and Task 4's accounting depends on knowing the true
denominator of everything considered.

============================================================
DELIVERABLE
============================================================

A dated progress.md entry: the full hypothesis log from Task 1 (every
source and item considered, including one-line pre-filter rejections,
carried forward or not, why, and its source citation), the full test
log from Task 3 (every formalized hypothesis, pass or fail), the
multiple-comparisons accounting from Task 4, the ranked shortlist from
Task 5, the delegation breakdown, and a clean statement of what a future
session would need to do to move any shortlisted candidate toward a
real Stage D.2 pre-registration.

END PROMPT
