# Orchestration and model tiering

Adopted 2026-09-21. CLAUDE.md holds the operating rules. This file holds the
reasoning behind them, the stage-prompt template, and the thresholds that
would change the setup.

## The setup

- Lead session on Fable. The lead plans, routes, verifies and synthesizes.
- Workers on haiku, sonnet, opus or fable, at effort medium, high, xhigh or
  max, chosen per subtask by the lead. Low effort is not used.
- Haiku does pure extraction; Sonnet at medium does complex extraction
  (2026-09-21 revision): reading, parsing and
  tabulating into a fixed schema. Extraction quality does not depend much on
  model tier, while drawing conclusions from the extracted data does, so
  every interpretive step goes to a higher tier.
- Four generic agent files (.claude/agents/worker-medium, worker-high,
  worker-xhigh, worker-max) pin the effort. The lead passes the model on each Agent call.
  The Agent tool takes a per-call `model` but no per-call `effort`, which is
  why effort lives in the files. Dynamic workflows take both per agent:
  `agent(prompt, { model, effort })`.
- .claude/settings.json caps concurrency at 4 subagents and spawn depth at 2.

## Why

- Anthropic's Fable prompting guide says Fable is more dependable at
  dispatching and sustaining parallel subagents, and recommends explicit
  guidance on when to delegate. That is the lead role here.
- Anthropic reports a Fable-lead plus Sonnet-worker split reaching about 96%
  of Fable-solo quality at about 46% of the cost (BrowseComp, July 2026).
  These are Anthropic's internal numbers, not independently reproduced, and
  some easier workloads showed orchestration overhead with no benefit.
- Multi-agent work pays off on parallel, independent items (literature
  sweeps, per-family audits, per-timeframe computations, per-finding
  verification). It does not pay off on tightly coupled single judgments.
  The DSR/PBO/t-hurdle synthesis is one of those, so it stays with the lead.
- Route by silent-failure risk. A cheap model on a statistical judgment
  produces output that looks right and is wrong. Sonnet gets only work whose
  correctness is checkable by inspection or by a test.

## What the D.1d blowout showed

The first D.1d run spent about 744k tokens in 7 minutes across 6 parallel
agents and hit the weekly limit. That was a fan-out problem more than a
model-tier problem: every subagent pays roughly 25k to 35k tokens of setup,
re-reads its own inputs, and draws from the same shared pool at the same
time. Six Sonnet agents would have hit the same wall, only later. The fixes,
in order of effect: the concurrency cap, doing small tasks inline, passing
file paths instead of long summaries, and only then cheaper tiers.

## Usage notes

- Fable has its own weekly cap, 50% of the plan's weekly usage. The lead is
  always Fable, so every fable worker competes with the lead for that slice.
  This is why reviews and audits run on opus at xhigh and fable workers are
  kept for verdict-number verification and the hinge call. A Fable lead that
  runs out mid-stage continues on Opus; see CLAUDE.md.
- Ultracode is available on Fable and Opus, so a lead that falls back to Opus
  keeps it.
- Check /usage mid-session. If Fable passes about 40% of the weekly bar
  before mid-week, run implementation-heavy stages with an Opus lead and keep
  Fable for synthesis and verification.
- If a sonnet worker fails verification more than occasionally on a class of
  task, move that class to opus in CLAUDE.md's routing table.
- Keep CLAUDE.md stable and short. A stable prompt prefix keeps cache reads
  cheap for a long-running lead.
- Claude Code 2.1.234 and later can continue automatically after a usage
  limit resets. Check it is on in /config.

## Stage-prompt template

Every stage prompt follows this shape. The Delegation plan section is new as
of 2026-09-21 and is mandatory.

    STAGE X.Y "SHORT TITLE"

    Lead: Fable, <effort>. Ultracode: <on/off>.
    One paragraph on why this lead and effort fit this stage, and a separate
    line for any usage consideration.

    SCOPE             what the stage does and does not do
    CONTEXT           files to read first
    GUARDRAILS        holdout, registration, credentials, spend
    TASK 1..n         each with: owner, inputs, output artifact, done-when
    DELEGATION PLAN   table: task, owner (lead, or worker file + model),
                      parallel or serial, why that tier
    WHAT NOT TO DO
    DELIVERABLE       dated progress.md entry and named artifacts, ending
                      with the Session cost section (CLAUDE.md); the lead
                      keeps a per-row and cumulative ETA table throughout

    END PROMPT

Delegation plan block, as it appears in each prompt:

    DELEGATION PLAN (the lead executes this; it does not do worker tasks)
    1. Decompose each task into subtasks with one objective, inputs, output
       path and format, allowed tools, and boundaries.
    2. Route per CLAUDE.md. State model and effort for each subtask before
       spawning.
    3. At most 4 concurrent. Small tasks needing no isolation go inline.
    4. Collect results as files plus short summaries.
    5. Verify every number entering a verdict with an independent fable
       xhigh worker.
    6. Synthesize in the lead against this prompt, and write the synthesis
       to disk before ending.
    7. Unattended run: no pauses to ask. Checkpoint to
       reports/<stage>_STATE.md after each task.
