STAGE A.1 "OFFLINE DATA + RULES ENGINE BUILD"

Model: Opus 5, high effort.

Reasoning for this tier: this session touches financial rule logic (the
trailing Maximum Loss Limit, the consistency-percentage math, the
Scaling Plan thresholds) and a live spend gate drawing against a
shared, already-partially-spent Databento budget. A defect in either
one has a real consequence later — a rules-engine bug could let a
backtest pass a strategy that would actually blow a live account, and
a spend-gate bug could overrun a budget shared with three other
closed research projects. That combination earns high effort. It does
not earn ultracode: this is one coherent unit of work for a single
agent, not a task structured as multiple independent agents
cross-checking or dividing labor (that pattern is reserved for
program-audit-style work). Ultracode here would spend budget without
buying anything the task actually needs.

============================================================
CONTEXT AND GUARDRAILS — READ BEFORE STARTING ANY TASK
============================================================

Working directory: /home/kiros-li/Documents/GitHub/PropExperiment

Before touching any task below, read, in this order:
  1. README.md — states the project in one paragraph: an automated
     futures trading bot targeting the Topstep Combine and Express
     Funded Account (XFA) via the TopstepX / ProjectX Gateway API, MES
     as the primary instrument, Databento GLBX.MDP3 as the backtest
     data source.
  2. docs/DECISIONS.md — the locked decisions for this project. Do not
     propose alternatives to anything recorded there without flagging
     the conflict explicitly in your final report rather than silently
     picking a different approach. In particular: the venue is Topstep
     via TopstepX/ProjectX, the current phase is XFA-only (the Live
     Funded Account is a call-up exit event, not something to model or
     solve for), instrument ranking is MES first, and the execution
     and rules-engine design deliberately borrows the shape of two
     existing repos rather than being built from a blank file.
  3. docs/STAGES.md — the full stage plan. This session is Stage A.1
     specifically: the offline half of Stage A, meaning everything
     that can be built and tested with zero TopstepX credentials.
     Stage A.2, the live TopstepX access and cost census, is a
     separate future session gated on the user purchasing a Trading
     Combine subscription and an API Access subscription tomorrow
     morning. Do not attempt to collapse A.2 into this session even if
     it feels efficient to do so — the credential boundary is
     deliberate, not accidental, and is restated below as a hard
     guardrail.

CREDENTIAL GUARDRAIL — ABSOLUTE, NOT A SUGGESTION.
No TopstepX API key exists yet for this project. Do not write any code
anywhere in the repository that imports, references, stubs, mocks, or
otherwise assumes a TopstepX credential is available. Do not create a
placeholder key, a "TODO: insert key here" pattern, or a config file
shaped to receive one. Nothing under live/ or ops/ should be touched
at all this session — those directories are for the live lane, which
cannot exist without the credential this project does not have.
Everything produced tonight lives under data/, rules/, sim/, tests/,
and reports/.

SPEND GUARDRAIL — READ CAREFULLY, THIS PROTECTS SHARED BUDGET.
A working Databento API key already exists for this account, shared
across MLCryptoEngine and now PropExperiment. Read it from wherever
the existing .env pattern in MLCryptoEngine stores it — do not
hardcode any key value into source code, ever, in any file, even
temporarily. MLCryptoEngine's own spend ledger currently shows $82.12
spent against a self-imposed $120 cap that spans every project on this
Databento account, not just MLCryptoEngine. That means this session is
drawing against a budget that is already 68% consumed by prior,
unrelated work.

The rule for tonight: cap all NEW spend originating from this session
at $15.00 total, and treat that as a hard ceiling, not a target to
approach. Before any single Databento request — every single one, no
exceptions for requests you are confident are cheap — call the free
cost-estimate endpoint first and log the quoted cost. If a planned
request's quoted cost would push this session's cumulative new spend
past $15, or would push the shared ledger's running total past $120,
do not make the request. Instead, write the exact quoted cost, the
exact request parameters that produced that quote, and the reason you
stopped into docs/ACCESS.md, and move on to whatever other tasks
remain that don't require that data. A partially-completed data pull
with an honest, itemized note about why it stopped short is a correct
outcome. A pull that quietly exceeds budget because the quote step was
skipped is not.

Every Databento request this session must be logged to an append-only
ledger file under ledger/, following the same structural pattern
MLCryptoEngine already uses for its own ledger (read that file for the
exact shape before inventing a new one — do not design a new ledger
schema from scratch when a working one already exists one directory
tree over). The ledger entry should include, at minimum: timestamp,
the exact request parameters, the quoted cost, the actual cost once
known, and a running cumulative total for this session.

============================================================
TASK 1 — PORT THE DATABENTO ADAPTER (READ-ONLY ACROSS THE
MLCryptoEngine BOUNDARY)
============================================================

MLCryptoEngine is a closed repository. Do not open it for editing
under any circumstances this session — not to fix something you
notice is wrong, not to leave a comment, nothing. The only permitted
interaction with MLCryptoEngine this session is reading its code and
its existing data files to inform what you build in PropExperiment.

What to read and port:
  - The data/databento module inside MLCryptoEngine: this includes the
    GLBX.MDP3 adapter itself, the roll-boundary resolution logic (how
    it decides when to switch from one quarterly contract to the
    next), the CME session calendar (which encodes trading hours, the
    daily halt window, and DST transitions), and the validation
    harness that checks incoming data is ordered on ts_recv.
  - The spend-gate and ledger pattern referenced in the guardrails
    section above.

Port these into PropExperiment/data/, adapted specifically for MES
rather than left generic for arbitrary symbols, since MES is this
project's locked primary instrument per docs/DECISIONS.md.

While porting, fix a known, previously-documented gap: MLCryptoEngine's
existing session calendar has no CME holiday calendar — it handles
regular trading hours and the daily halt but not full-day market
closures (e.g. Christmas, Thanksgiving, Independence Day observed).
Add one. Do not guess at the holiday list from memory or assume a
generic US market holiday calendar applies unmodified — CME holiday
observance has its own quirks (some holidays are early-close only, not
full closures; some differ from equity market holidays). Confirm the
holiday calendar against an authoritative CME source rather than
assuming NYSE's calendar transfers directly.

============================================================
TASK 2 — PULL MES OHLCV-1M HISTORY FROM DATABENTO
============================================================

Through the spend gate ported in Task 1, and respecting the spend
guardrail above without exception, quote and then pull ohlcv-1m bars
for MES as a continuous contract. Given the $15 cap, prioritize the
most recent 12 to 18 months of history over reaching further back —
recency matters more here because Stage D backtesting will weight
recent market regimes more heavily than distant ones regardless, so
there is limited value in spending scarce budget on a decade of
history when a fraction of that money buys the window that will
actually get used first.

Store the raw DBN files immutably: once written, a file should never
be silently overwritten by a subsequent run. If the adapter detects an
attempt to write over an existing file, it should refuse and surface
that refusal clearly rather than quietly proceeding — this mirrors the
existing rule in MLCryptoEngine's own data-handling code and exists to
prevent a bug in a later run from silently corrupting or replacing
data that took real money to acquire.

Build a continuous contract series across the quarterly roll cycle
(March, June, September, December — the H, M, U, Z contract months for
equity index futures). Use the roll-boundary logic ported in Task 1
rather than inventing a new roll rule. On top of the continuous
series, mark two things explicitly as metadata or flags on the bar
data, not as separate undocumented side files: the 3:10 PM CT daily
flatten boundary (the point after which Topstep rules require all
positions closed), and the daily 4:00–5:00 PM CT halt window
mentioned in prior research (verify the exact halt window against
what the ported session calendar encodes rather than assuming the
figure from memory is precisely right).

============================================================
TASK 3 — VALIDATE THE PULLED BARS
============================================================

Run integrity checks against the newly pulled MES bar data:
  - Timestamps strictly monotonic increasing, no duplicates.
  - No duplicate bars by timestamp.
  - Volume fields non-negative.
  - Any gap in the expected bar sequence (accounting for session
    boundaries and the holiday calendar from Task 1) gets flagged
    explicitly in the output — do not silently forward-fill or
    interpolate a gap. A flagged gap is honest data; a silently filled
    one is a fabricated data point wearing real data's clothes.

Separately, as an internal consistency cross-check, compare the new
1-minute bars against the two existing MES tick-level days already
sitting on disk in MLCryptoEngine/data/vendor/databento (dated
2026-07-15 and 2026-07-31, mbp-10 and trades schemas) for whichever of
those two dates falls inside the newly pulled history window. This is
a read-only comparison against MLCryptoEngine's existing files — do
not copy those files into PropExperiment, read them in place. Confirm
that aggregating the tick data up to 1-minute bars produces results
consistent with the ohlcv-1m bars pulled directly, within a reasonable
tolerance you should state explicitly rather than leave implicit.

Write a clear, dated findings report to reports/bar_validation.md
covering what was checked, what passed, what (if anything) failed or
was flagged, and the exact tolerance used in the tick-to-bar
cross-check.

============================================================
TASK 4 — BUILD THE COST MODEL FROM EXISTING TICK DATA
============================================================

Using the same two existing MES tick days already on disk in
MLCryptoEngine (read-only, do not re-purchase this data — it is
already paid for and sitting there), build a slippage model calibrated
by time of day. Specifically: construct a table or function mapping
session minute (or a reasonable minute-bucket) to expected slippage in
ticks for a market order, and build this separately for at least three
windows that behave differently — the open, the midday lull, and the
close — since liquidity and spread behavior genuinely differ across
these windows and a single flat slippage number would misrepresent all
three.

On top of the slippage model, apply the official MES round-turn
commission figure of $1.22, sourced from the Topstep commissions page
as recorded in prior project research. Cite that source and the date
it was recorded directly in a code comment next to where the figure is
used, and add an explicit flag or TODO noting that this figure needs
reconfirmation at Topstep checkout before Stage A.2, since Topstep has
changed commission and fee figures multiple times during 2026 and a
stale number here would silently corrupt every downstream backtest
cost calculation.

Write this as sim/costs.py.

============================================================
TASK 5 — BUILD THE XFA RULES ENGINE AS PURE, TESTABLE FUNCTIONS
============================================================

Build rules/xfa_rules.py. Every function in this module should be pure
(no I/O, no network calls, no reading from a live account) so that it
can be exercised entirely in Task 6's known-answer tests with no
TopstepX connection of any kind. This module encodes the following
rules, each of which should be its own clearly separated, independently
testable piece of logic rather than one large tangled function:

  - Trailing end-of-day Maximum Loss Limit (MLL). This has two
    genuinely distinct parts and they must not be collapsed into one
    check: (a) the floor itself trails the end-of-day closing balance
    and only ever ratchets upward, never downward, updating once per
    trading day at the close; and (b) completely separately, a
    real-time breach check runs continuously through the session
    against unrealized-plus-realized equity, meaning an intrabar move
    can trigger a breach even on a day where the closing-balance floor
    itself never moves. Treat these as two functions or two clearly
    labeled code paths, not one.

  - Combine rules for the 50K size: a $3,000 profit target, a rule
    that the single best trading day cannot exceed 50% of that target
    (and critically, breaching this does not fail the account — it
    raises the profit target instead, so the trader continues and
    passes once total profit is large enough relative to the
    now-larger target), and a $2,000 Maximum Loss Limit.

  - XFA Standard payout path: eligibility requires 5 winning days of
    $150 or more net P&L (days need not be consecutive), a per-request
    payout cap of $2,000 on the 50K size, and a ceiling of 50% of
    current account balance per request regardless of the dollar cap.

  - XFA Consistency payout path: eligibility requires only 3 trading
    days, but the largest single day's profit must be at or below 40%
    of total net profit across the window; the per-request cap on the
    50K size is $3,000, higher than Standard's cap, reflecting the
    tradeoff between fewer required days and a stricter shape
    requirement.

  - The XFA Scaling Plan: maximum position size starts at 2 lots (mini
    contracts) at a $0 account balance, increases to 3 lots at a
    $1,500 balance, and increases again to 5 lots at a $2,000 balance.
    Since this project trades MES micros rather than mini ES, multiply
    every lot figure here by 10 to get the correct micro-contract
    equivalent, and make that 10x relationship an explicit, named
    constant in the code rather than a magic number that has to be
    rediscovered later.

  - The 3:10 PM CT auto-flatten. Model this as a hard,
    non-overridable rule: at this point in the session, any open
    position gets force-closed regardless of what the strategy layer
    wants to do. This should not be something the strategy module can
    request an exception to.

  - The post-payout MLL reset. This is a genuinely dangerous mechanic
    worth modeling with real care rather than glossing over: the
    moment a payout is processed, the account's Maximum Loss Limit
    resets to $0, meaning the account has zero drawdown buffer
    immediately after every withdrawal. Model this explicitly as its
    own state transition, not as an incidental side effect buried
    inside the payout-request function.

For the overall shape of this module, follow two existing patterns in
the repository rather than inventing new conventions from nothing.
Read HFExperiment/src/hfexperiment/intents.py and
HFExperiment/src/hfexperiment/gate.py for the frozen-dataclass
Intent-plus-pure-check-function shape, where a malformed input refuses
at construction time before it ever reaches the gate, and the gate
itself is a pure function that returns either None (proceed) or a
Refusal carrying a named reason and the exact arithmetic that
triggered it, checked in a fixed, deterministic order. Separately,
read AiTrader/risk/risk_gate.hpp for the deny-only, final-authority
gate shape, where the gate can only ever refuse based on immutable
hard limits and can never be made more permissive by anything upstream
of it. Adapt both shapes to Topstep's specific rules as encoded above
— do not copy either file's equity-specific or generic-market-specific
field names (things like is_fractionable or SMART routing belong to
HFExperiment's equity context, not to this futures context).

============================================================
TASK 6 — KNOWN-ANSWER TESTS FOR EVERY RULE IN TASK 5
============================================================

For each rule encoded in Task 5, construct at least one planted test
scenario with a hand-computed expected answer, and write these as
tests/test_xfa_rules.py. At minimum, include:

  - A planted intraday scenario where an intrabar wick breaches the
    MLL on unrealized-plus-realized equity, but the account's closing
    balance for that same day never actually breaches the
    end-of-day trailing floor. The expected result is a caught
    breach — this is specifically testing that the two-part MLL logic
    from Task 5 is not collapsed into a single end-of-day-only check
    that would miss this.

  - A day where net profit exceeds 50% of the current profit target.
    The expected result is that the profit target increases and the
    account continues trading — explicitly assert that the account is
    NOT marked as failed, since a naive implementation might
    incorrectly treat any rule-percentage breach as a failure.

  - A Consistency-path scenario at exactly 40.00% largest-day
    concentration (expected: passes) and a second scenario at 40.01%
    (expected: fails). This boundary pair matters because an
    off-by-one or a strict-versus-inclusive comparison error here
    would silently misjudge every real account sitting near this
    threshold.

  - A payout request for an amount exceeding 50% of current account
    balance, even when that amount is below the dollar cap for the
    account size and path. Expected result: refused, with a named
    reason distinguishing this from a dollar-cap refusal.

  - A post-payout scenario: process a payout, confirm the MLL resets
    to $0 as modeled in Task 5, then apply a losing trade immediately
    afterward and confirm the breach is correctly caught given the
    freshly-reset floor. This is the scenario most likely to reveal a
    subtle bug, since it requires the payout logic and the MLL logic
    to interact correctly across a state transition rather than being
    tested purely in isolation from each other.

============================================================
WHAT NOT TO DO THIS SESSION — STATE THESE EXPLICITLY IN THE FINAL
REPORT RATHER THAN SIMPLY OMITTING THEM SILENTLY
============================================================

  - Anything that touches a TopstepX API key, a Practice account, or a
    retrieveBars call of any kind. No credentials exist yet for this
    project.
  - Anything under live/ or ops/, including any form of kill-switch or
    watchdog code. That is live-lane work and is entirely blocked on
    the credential that does not exist this session.
  - Drafting the written questions intended for Topstep support. Hold
    these until the account actually exists and the current, exact
    Combine pricing and path options are confirmed at checkout —
    drafting questions now risks asking about numbers that Topstep may
    have already changed since the last time they were recorded in
    this project's research.
  - Any funnel-level Monte Carlo simulation or Combine-pass-probability
    modeling. This class of work depends on having an actual strategy
    to feed statistics from, and no strategy exists yet — that is
    explicitly Stage D.1's job, a separate future session by design,
    not something to front-run here even partially.

============================================================
DELIVERABLE
============================================================

A clear, dated entry in progress.md summarizing: what actually ran
this session, what was explicitly skipped and why (referencing the
"what not to do" list above by name rather than leaving gaps
unexplained), the exact new Databento spend incurred this session
measured against both the $15 session cap and the $120 shared account
cap, and a clean, short, actionable list of exactly what is needed
from the user tomorrow morning — specifically: creating a TopstepX
account, choosing a Combine path (Standard versus No Activation Fee),
and subscribing to API Access — before Stage A.2 can begin.

END PROMPT
