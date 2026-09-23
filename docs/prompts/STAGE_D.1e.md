STAGE D.1e "DEFINING THE MES NULL: CRITERIA, POWER AND DATA QUOTES"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: three consecutive rounds (D.1, D.1b, D.1d; N = 31) found no MES edge,
but the program cannot yet claim MES is null, because 289 train days are too
few to resolve effects near the cost bar and the passive-fill verdict rests on
a deliberately pessimistic fill rule. The user has decided to stay strictly on
MES until a null is proven to a stated standard. This stage writes that
standard down before any data is bought: what the null covers, the smallest
edge that matters economically, the test that establishes it, how many days
each strategy class needs to reach 80% power, what the extra MES history and
order-book days would cost, how a second holdout is carved from the new
history, and the frozen list of tests Stage D.1f will run on it. It buys
nothing, runs no new hypothesis, and ends with a decision packet for the user.

Lead: Fable 5.1, effort xhigh. Ultracode: off.

Why this lead and effort: nearly all of this stage is statistical design
whose errors would be silent. A null criterion that is too loose, a power
calculation that ignores day-level clustering, or a confirmation list that
leaves room to re-tune parameters would each make D.1f's verdict meaningless
while looking rigorous. That is lead-only judgment at xhigh. The parallel
work is small (one extraction pass, one power-code build, one quote script,
verifiers), so ultracode's fan-out buys nothing here. Max effort is used once,
by a worker, for the adversarial review of the null criteria before they are
hashed, because every later verdict hinges on that document.

Usage: Fable has its own weekly cap shared by the lead and any Fable worker.
This stage spends Fable only on the lead, one worker-max review and one
worker-xhigh verification. Everything else routes to opus, sonnet or haiku.

============================================================
SCOPE
============================================================

This stage does:
- define exactly what "MES is null" means for this program, as a bounded,
  testable statement with a named effect size, test, confidence and power
- compute, from the existing train-window results, the number of trading days
  each strategy class needs to reach that power
- confirm MES data availability on Databento GLBX.MDP3 and obtain cost QUOTES
  (metadata only) for the extended 1-minute history and for MBO order-book days
- declare, before any download, the data-quality rules for the older history
  and the second sealed holdout that will be carved from it
- pre-register the complete, frozen confirmation list Stage D.1f will run,
  including one small new declared family of daily-bar constructions
- hand the user a decision packet: spend options, and the power each buys

This stage does NOT:
- buy, download or read any new market data. Quotes only.
- screen any new hypothesis or add anything to N. Re-running existing trials
  through the shared runner to read their per-trade distributions is allowed
  and is not a new trial (D.1b and D.1d did the same for continuity).
- touch the sealed holdout, REGISTRATION.md, rules/, live/, ops/ or any
  TopstepX credential
- consider any instrument other than MES. The user has ruled MNQ and every
  cross-asset idea out of scope until the MES question is settled.
- make the spend decision. It lays out options; the user chooses.

============================================================
CONTEXT TO READ FIRST
============================================================

1. CLAUDE.md and docs/ORCHESTRATION.md. These are the standing rules for this
   session: roles, routing, worker files, concurrency, artifacts, checkpoints.
   This prompt does not repeat them. If anything here seems to contradict
   CLAUDE.md, CLAUDE.md wins and you log the conflict.
2. README.md, docs/DECISIONS.md, docs/STAGES.md, docs/SCREENING.md.
3. progress.md entries for Stages B–C, D.1, D.1a, D.1b, D.1c and D.1d, in
   full. D.1d's synthesis lists what remains unexamined; this stage turns that
   list into a plan.
4. reports/power_gate.md and reports/power_gate.json, and funnel/power_gate.py.
   The power gate is the program's own model of what edge the Combine and XFA
   actually need. Task 2 derives the economic threshold from it.
5. reports/stage_d1d_accounting.json (every trial's daily net series and
   figures), reports/stage_d1b_family_f_facts.json,
   reports/stage_d1d_family_g_facts.json and its four per-timeframe files,
   reports/stage_d1d_retests.json, reports/stage_d1d_horizon_audit.md.
6. docs/HOLDOUT_MANIFEST.json, data/holdout.py, docs/HOLDOUT_UNLOCK_LOG.md.
   The current holdout starts at trade date 2026-06-22. Understand the sealing
   mechanism; Task 5 designs a second holdout that D.1f will seal with it.
7. ledger/databento_spend.jsonl and the Databento adapter and spend-ledger code
   under data/. Every quote this stage makes goes through that ledger as a
   "quote" event. For scale: one month of MES ohlcv-1m quoted at about $0.11
   in Stage A.1, and shared cumulative spend is about $84.

============================================================
GUARDRAILS (short recap; CLAUDE.md has the full list)
============================================================

- Holdout: `uv run python -m data.holdout status` at start and end, report
  unlocks_logged (must be 0).
- Spend: $0.00. Only Databento metadata endpoints (availability, schemas,
  dataset range, get_cost). No timeseries or batch call of any kind. The
  quote script must fail fast if it would import or call a timeseries
  method. If you are unsure whether an endpoint is billable, do not call it.
- N stays 31. No new screens.
- No commits (the user commits after review).
- Checkpoint to reports/stage_d1e_STATE.md after every task.

============================================================
TASK 0 — STARTUP
============================================================

Holdout status check. `git status` must show a clean tree at b79a31d or
later; if not, log what is dirty and continue without touching it. Create
reports/stage_d1e_STATE.md. Confirm CLAUDE.md and .claude/agents/ loaded
(four worker files: worker-medium, worker-high, worker-xhigh, worker-max).

============================================================
TASK 1 — COVERAGE MAP: WHAT THE NULL IS ABOUT
============================================================

Build reports/stage_d1e_coverage.md: every strategy class the MES null will
speak for, with each member cited by its exact trial or statistic ID. Starting
classification, which you may refine with a logged reason:

- C1 session-clock effects: A-H1, A-H2 buy/sell, A-H3, A-H4 RTH/ETH
- C2 reference levels and breakouts: B-H1..B-H4, RT1–RT4, G2, G3, G5,
  F4.1, F4.2, F4.4
- C3 short-horizon reversal and momentum at market fills: C-H1..C-H3, RT5,
  F1 variance ratios, F3.2, F3.3, G1, G4
- C4 volatility-state conditioning: D-H1..D-H4, RT6, RT7, F2, F5
- C5 calendar and scheduled events: E-H1..E-H4
- C6 passive-execution strategies: C-H4. Its null needs order-book fills and
  belongs to Stage D.1g; this stage defines its criteria and sizes its data.
- C7 daily-bar constructions for intraday entries: new, declared in Task 5 as
  Family H, run in D.1f. D.1d flagged this region as never tested; leaving it
  out would put an asterisk on the verdict.
- Out of scope, named so the verdict never overreaches: multi-day holding
  (excluded by the venue, D.1c), other instruments and cross-asset effects
  (excluded by the user's MES-only decision), order-flow signals needing book
  data beyond C6's fill model.

For each member record: trades per day, per-trade net mean and SD, daily net
SD, lag-1 autocorrelation of the daily net series, and the train window it was
measured on. Pull these from the existing reports; where a figure is missing,
re-run the trial through `screen_candidate` on the 289-day train union to read
it (not a new trial; log each re-run). For event statistics from Families F
and G, use event counts, event-level mean and SD, and events per day.

============================================================
TASK 2 — THE ECONOMIC THRESHOLD ε
============================================================

The null must say "no edge of at least ε", with ε set by the program's own
economics, not by what the data can resolve. Derive it from the power gate:

- For each round-turn frequency in the power gate grid (1, 2 and 4 per day),
  and for the Standard and Consistency payout paths, find the boundary
  between fail and pass cells. Convert each boundary cell (win probability,
  average win / average loss, 2 micros) into net expected ticks per trade.
- ε for a class is the smallest net edge per trade at which the power gate
  passes at that class's typical trade frequency. Interpolate between grid
  cells if needed and say so; if the grid is too coarse to place ε within
  0.25 ticks, extend the grid by re-running `funnel.power_gate` at finer
  points (compute only, no market data) and log the runs.
- Report ε alongside the market-order cost bar (2.11 ticks) and the passive
  bar (0.98 ticks), so the reader sees gross and net side by side.
- If ε turns out so small that no feasible sample can resolve it, say so
  plainly. That is itself a finding, and Task 6 must then state what the
  program CAN claim instead of pretending to a claim it cannot make.

============================================================
TASK 3 — POWER AND SAMPLE SIZE
============================================================

For every member in the coverage map, compute two numbers:

(a) Detection power: trading days needed for 80% power to reject "net edge
    ≤ 0" when the true net edge is ε, at the family-wise 5% level with Holm
    correction across the full D.1f confirmation list (Task 5 fixes the list
    size; use a provisional size, then recompute once the list is frozen).
(b) Null power: trading days needed so that, when the true net edge is 0, the
    one-sided 95% upper confidence bound on net edge falls below ε with 80%
    probability. This is the number that makes a null "definitive".

Method:
- Analytic first: per-trade variance, trades per day, and a variance
  inflation factor for day-level clustering and serial correlation, estimated
  from the daily net series.
- Cross-check by simulation: stationary day-block bootstrap of each member's
  existing daily net series (mean block 5, matching the program's inference
  code), shifted to true edge ε and to 0, resampled at target lengths, 2,000
  replications per length. Report where analytic and simulated figures differ
  by more than 15% and use the simulated figure.
- Report per class: the binding member (the one needing the most days), the
  days needed for (a) and (b), and the days the extended history would supply
  after the Task 4 exclusions and the Task 5 holdout.

Code lives in strategy/research/_d1e_power.py with known-answer tests in
tests/test_d1e_power.py (for example iid normal returns with known variance
must reproduce the textbook sample size to within simulation error, and an
AR(1) daily series must show the expected variance inflation). Output:
reports/stage_d1e_power.json plus a table in the progress entry.

============================================================
TASK 4 — DATA AVAILABILITY, QUALITY RULES AND QUOTES (NO PURCHASE)
============================================================

4a. Availability. From Databento metadata, confirm for GLBX.MDP3: the first
    date MES ohlcv-1m exists, the schemas the current pipeline needs for roll
    handling and validation, and the MBO schema's availability for MES.
    Identify the exact start of the current research data so the extension
    ends the day before it with no overlap and no gap.

4b. Quotes via metadata.get_cost only, each logged to the spend ledger as a
    quote event:
    - MES ohlcv-1m, continuous contract exactly as the pipeline pulls it, from
      first availability to the day before the current research window
    - any auxiliary schema the pipeline needs for that same range
    - MES MBO: per-day cost and billable bytes for a sample of RTH days, then
      totals for 20, 40, 60 and 120 days and for the day count Task 3 says C6
      needs. Days must come from outside both holdouts.
    - Report disk footprint against free space: the main drive has about
      368 GB free, and the LARGE STORAGE drive at /mnt/large-storage has about
      770 GB free. Say which drive each dataset should land on; bulk MBO
      belongs on LARGE STORAGE, and nothing secret is ever written there.

4c. Data-quality rules for the older history, declared now, before any bar is
    seen (write them into Task 6's document):
    - MES listed in May 2019 and its early months traded thinly. Fix an
      objective start rule now, for example the first month whose median RTH
      1-minute volume reaches a stated fraction of the 2025–26 level, measured
      in D.1f on the data itself by that fixed rule. The rule is set here; the
      date it yields is computed later and cannot be changed after the fact.
    - Roll, vendor-degraded-day and calendar handling identical to the current
      pipeline.
    - The cost model stays as calibrated on 2025–26 books. State the known
      bias: early-era spreads were likely wider, so modelled costs understate
      real costs there. That bias favors finding an edge, which makes it
      conservative for a null claim; say so, and say it is not conservative
      for any positive finding, which would need a cost re-check.
    - Regime slices (for example 2020) are reported descriptively only; no
      slice may be chosen or dropped after results are seen.

============================================================
TASK 5 — SECOND HOLDOUT AND THE D.1f CONFIRMATION LIST (LEAD ONLY, HASHED)
============================================================

This is D.1f's pre-registration. Write reports/stage_d1f_confirmation_list.md,
then hash it and make it read-only, exactly as the D.1b and D.1d declarations
were handled.

5a. Second holdout. Choose a contiguous block of the new history to seal
    immediately on download in D.1f, before any read, using data/holdout.py's
    mechanism. Give the exact trade-date bounds and the reasoning (size
    against Task 3's needs, regime coverage, adjacency to the current
    research window). D.1f's confirmation runs on the remaining new history
    only. The existing 289 train days are mined and are never pooled into a
    confirmation figure.

5b. The frozen list:
    - all 31 trials with every parameter frozen at its recorded value; no
      re-tuning, no re-selection of thresholds
    - the ranked near-misses already logged, as event statistics with their
      exact definitions: Family F's list in the D.1b entry (F3.2 buckets,
      F6.1, F3.3, F4.4, F4.1) and Family G's top of the p-ordering in the
      D.1d entry (G2.RTH.30 first)
    - Family H, daily-bar constructions for intraday entries, cap 6 tests,
      each with exact, fully specified definitions and entry/exit rules, for
      example prior-day narrow-range (NR4/NR7) conditioning an opening-range
      entry, prior-day range terciles, inside days, prior-day close location
      in range. Every H test uses only information known before the session
      opens; state the look-ahead check for each.
    - the C6 criteria and data needs, so D.1g inherits them unchanged

5c. Multiplicity and decision rules, fixed now:
    - "Edge exists" claims: Holm across the full list at family-wise 5%, then
      the existing composite verdict (robust gate plus drift benchmark) and
      the DSR/t > 3.0/PBO accounting carried forward from N = 31.
    - "Null" claims, per class: every member's one-sided 95% upper bound on
      net edge is below ε AND the achieved null power (Task 3b) is at least
      80% for that member.
    - Any member meeting neither is "inconclusive". An inconclusive member
      keeps its class out of the null verdict. Nothing is rounded to null.
    - A member that passes confirmation goes to the user as a Stage D.2
      discussion item. It is not registered automatically.

5d. Adversarial review before hashing. Spawn worker-max (model fable) with
    the draft list and the Task 6 draft. Brief: find every way these
    documents let a later stage fudge the result, including re-tuning room,
    a loose ε, undefined edge cases, look-ahead in Family H, holdout leakage,
    and multiplicity gaps. The lead adjudicates each finding in writing,
    amends, then hashes. Record findings and rulings in the progress entry.

============================================================
TASK 6 — docs/NULL_CRITERIA.md (LEAD ONLY, HASHED WITH TASK 5)
============================================================

The standing document every later MES stage is judged against. It contains:
- the null statement template, for example: "For MES intraday strategies in
  classes C1–C5 and C7, executed with market orders at modelled retail cost
  and flat by the XFA cutoff, no member has a net edge of at least ε ticks per
  trade: every member's one-sided 95% upper bound is below ε, with at least
  80% power, on the pre-registered confirmation window." Refine the wording,
  keep every number explicit.
- the C6 variant for Stage D.1g (passive fills, order-book fill model, its own
  ε from the passive bar)
- ε per class from Task 2, with the derivation
- the Task 4c data-quality rules
- the inconclusive rule, and the explicit out-of-scope list from Task 1
- what the program is entitled to say if the null holds, and what it is not
  (for example: not "MES has no edge", only the bounded statement above)

============================================================
TASK 7 — DECISION PACKET FOR THE USER
============================================================

A short section at the end of the progress entry, neutral, numbers first:
- the extended-history quote and the power it achieves per class, including
  which classes still end up underpowered even with all available history
- MBO options (20/40/60/120 days and the C6-needed count) with cost, disk,
  and achieved power
- a minimal option and a complete option, each with its total cost
- the questions the user must answer to proceed (approve which spend, accept
  ε as derived, accept the Family H list)

============================================================
DELEGATION PLAN (the lead executes this plan; it does not do worker tasks)
============================================================

| Task | Owner | Model / effort | Parallel? | Why this tier |
|---|---|---|---|---|
| 0 Startup | lead | fable xhigh | — | trivial, inline |
| 1 Extract per-member figures from reports JSON | worker-medium | sonnet medium | parallel with 2-extract and 4a | complex extraction across several files; no judgment |
| 1 Re-runs for missing figures | worker-high | sonnet high | after 1-extract | runs an existing runner on existing trials |
| 1 Classification and coverage map | lead | — | — | defines the null's scope |
| 2 Tabulate power-gate boundary cells | worker-medium | haiku medium | parallel | pure extraction into a fixed schema |
| 2 Finer power-gate runs, if needed | worker-high | opus high | after tabulation | standard code run |
| 2 Choose ε | lead | — | — | economic judgment |
| 3 Power code and known-answer tests | worker-high | opus high | after 1 | standard coding |
| 3 Independent verification of power numbers | worker-xhigh | fable xhigh | after 3 code | numbers enter the verdict criteria |
| 4a/4b Availability and quote script | worker-xhigh | opus xhigh | parallel with 1 | touches spend: a wrong call costs money |
| 4c Data-quality rules | lead | — | — | pre-registration content |
| 5 Holdout, frozen list, Family H definitions | lead | — | — | pre-registration content |
| 5d Adversarial review of 5 and 6 | worker-max | fable max | once, before hashing | the call every later verdict hinges on |
| 6 NULL_CRITERIA.md | lead | — | — | pre-registration content |
| 7 Decision packet | lead | — | — | synthesis against this prompt |

At most 4 workers at once. Workers write to reports/ and return path plus
summary. Checkpoint after every task.

============================================================
WHAT NOT TO DO
============================================================

- No timeseries or batch data call, no purchase, no download.
- No new hypothesis screened; N stays 31.
- No change to any trial's parameters. The frozen list records them as they
  are.
- No hashing of Task 5 or Task 6 before the Task 5d review is adjudicated,
  and no edit after hashing.
- No choice of ε, holdout bounds, or start rule that depends on how D.1f's
  results might come out.
- No instrument other than MES, in any task.
- No writes to REGISTRATION.md, rules/, live/, ops/; no holdout unlock.
- No commits.

============================================================
DELIVERABLE
============================================================

A dated progress.md entry for Stage D.1e containing: the guardrail evidence;
the delegation record (who did what, on which model, and any deviation from
the plan with its reason); the coverage map summary; ε per class with its
derivation; the power table (days needed for detection and null power per
class, and days the extended history supplies); availability and every quote
with ledger references; the data-quality rules; the second holdout bounds;
the frozen confirmation list's path and sha256; the adversarial review's
findings and rulings; docs/NULL_CRITERIA.md's path and sha256; and the
decision packet. Also one line in docs/STAGES.md for D.1e, and D.1f and D.1g
added as planned stages.

The entry closes with a "Session cost" section, computed at the very end,
after everything else is written:
- Wall-clock time: session start to finish, and time per task from the
  STATE file timestamps. Note any pause (for example a usage-limit wait)
  separately so it is not counted as work.
- Tokens used, per model: read this session's own transcript and its
  subagent transcripts under ~/.claude/projects/<this project>/<session id>/
  (the main .jsonl plus subagents/**/*.jsonl) and sum each assistant
  message's usage fields (input, output, cache read, cache creation) by
  model. Give one table: model, input, output, cache read, cache creation,
  total. Then one line per worker spawn: file, model, effort, tokens.
- Delegation share: the fraction of total tokens spent by the lead versus
  workers, and by model tier.
- State plainly that these are token counts, not plan-credit percentages.
  The session cannot read the /usage meter; the user records the percentage
  before and after.
- If the transcript files cannot be read, say so and give the time figures
  only. Never estimate token counts.

Artifacts: reports/stage_d1e_coverage.md, reports/stage_d1e_power.json,
reports/stage_d1e_quotes.json, reports/stage_d1f_confirmation_list.md
(read-only, hashed), docs/NULL_CRITERIA.md (hashed),
strategy/research/_d1e_power.py, tests/test_d1e_power.py,
reports/stage_d1e_STATE.md.

END PROMPT
