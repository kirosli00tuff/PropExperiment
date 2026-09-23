# PropExperiment: session instructions

Read at every session start. This file holds the rules. Rationale, evidence
and the stage-prompt template live in docs/ORCHESTRATION.md.

## Orientation

- Scope, venue, instrument: README.md and docs/DECISIONS.md. XFA only, MES,
  TopstepX, Databento GLBX.MDP3.
- Stage history and results: docs/STAGES.md, and progress.md (one dated entry
  per stage).
- Screening contract: docs/SCREENING.md. Every candidate goes through
  `screening.screen_candidate` with `roll_blackout` set.

## Invariants (every session)

- Sealed holdout: run `uv run python -m data.holdout status` at start and end
  and report `unlocks_logged`. Never unlock outside a registered Stage D.2.
- REGISTRATION.md stays 0 bytes unless the user runs a real pre-registration.
- No TopstepX API calls, no credentials, no edits under live/ or ops/ unless
  the stage prompt says so.
- Databento spend only with a quote logged first and explicit approval in the
  stage prompt.
- The cumulative trial count N carries forward. Every screened hypothesis adds
  to it.
- No commits unless the stage prompt asks for one.

## Roles

The session reading this file is the LEAD. Default lead model: Opus (Opus 5.5,
the `opus` alias). The lead
plans, delegates, verifies and synthesizes. It does not write bulk code, parse
logs or run long jobs itself.

The lead keeps these for itself and never delegates them:
- decomposing the stage into subtasks and routing each one
- pre-registration declarations (feature spaces, selection rules, caps),
  written and hashed before any computation
- judgments on multiple-comparisons results (DSR, PBO, t > 3.0) and the final
  synthesis, written against the original stage prompt, never against a
  worker's paraphrase of it
- any decision the stage prompt reserves for the lead

## Model and effort routing

Route by decision complexity and silent-failure risk, not by task label.
Worker models: haiku, sonnet, opus, fable. Worker efforts: medium, high,
xhigh, max. No low effort.

| Work | Model | Effort |
|---|---|---|
| Pure extraction: reading, parsing and tabulating files, logs, JSON and runner output into a fixed schema; citation metadata; file inventories. No interpretation of any kind | haiku | medium |
| Complex extraction: joining several sources, semi-structured or messy inputs, pulling fields that need light reading comprehension (for example matching trial code to its cited source). Still no conclusions | sonnet | medium |
| Mechanical: running an already-written script, applying an already-decided edit, test boilerplate, simple scripted transforms | sonnet | medium, or high when the step has several parts |
| Standard coding: strategy modules to spec, harness or runner changes, debugging, test design | opus | high; xhigh when touching sim/, rules/, screening/ or data/holdout |
| High-level work: hard reasoning, statistical design the lead hands off, research synthesis, drafting that needs judgment | opus | xhigh, or max for the hardest single pieces |
| Independent or adversarial work: verification of any number entering a verdict (DSR, PBO, t-stat, P&L, trial count), leakage and look-ahead audits, adversarial review of a finding or a declaration, independent review of statistical code | fable | xhigh |
| The single adversarial call a stage hinges on, or a disputed verification | fable | max |

Why this split (2026-09-22): Opus 5.5 matches or beats Fable 5.1 on most
benchmarks at lower cost, so Opus is the default for the lead and for all
high-level work. Fable is kept for independent and adversarial checks
because a check by a different model than the one that wrote the work
catches errors both Opus passes would share. Fable also has its own weekly
cap (50% of the plan's weekly usage), so nothing else routes to it. Revisit
when a new Fable model ships.

Max effort on Opus (2026-09-22): Opus 5.5 at max costs well under Fable 5.1
at max, so max is no longer rare. Use opus max for judgment-heavy work
where a subtle error is expensive: pre-registration drafting, statistical
design, synthesis of mixed results, and the lead itself on stages whose
prompt says so. Keep xhigh for coding and routine high-level work, where
max mostly adds tokens (Opus 5.5 writes noticeably more per task at max).
The Session cost section shows whether max paid for itself; adjust from
those numbers.

- State model and effort for every subtask in the plan before spawning.
- Promote on failure: when a worker's output fails verification, rerun that
  subtask one tier up (haiku, then sonnet, then opus at a higher effort). Never demote judgment
  work to save usage.
- Haiku extracts and never interprets: the moment a result needs a
  conclusion drawn from it, that step belongs to a higher tier. Haiku output
  carries row counts and source references so the consumer checks it.
- Sonnet makes no design or statistical decisions. When a mechanical task
  turns out to need judgment, the worker stops and reports back.

## Spawning at a chosen model and effort

- Agent tool: effort is fixed by the agent file, the model is set per call.
  Use the four generic workers in .claude/agents/ and always pass `model`:
  `worker-medium` (effort medium), `worker-high` (effort high),
  `worker-xhigh` (effort xhigh), `worker-max` (effort max). Example:
  subagent_type `worker-xhigh`, model `opus`. Defaults when `model` is
  omitted: worker-medium haiku, worker-high sonnet, worker-xhigh opus,
  worker-max fable. Do not rely on the defaults.
- Dynamic workflows: set both per agent, for example
  `agent(prompt, { model: 'opus', effort: 'high' })`. Use workflows to fan out
  independent items: per-family audits, per-timeframe sweeps, per-finding
  verifiers.
- When a model rejects an effort level, drop one level and log the change.
- The Agent call's description is the agent's name in the CLI and in the
  delegation record. It is `<Role>-<Model><Effort>`: a CamelCase role that
  says what the agent does, then the model and the effort suffix (Med, High,
  XHigh, Max), for example `DataFetcher-HaikuMed`, `PowerCoder-OpusHigh`,
  `NumberVerifier-FableXHigh`, `AdvAuditor-FableMax`. The worker-* files stay
  the subagent_type; the role name is the description, so the user reads the
  routing off the screen (user instruction, 2026-09-22).

## Delegation budget

- At most 4 subagents at once (enforced in .claude/settings.json). Inside a
  workflow, run parallel `agent()` calls in batches of at most 4.
- Workers do not spawn further workers unless the stage prompt says so.
- Scale to the task: a lookup needs 1 agent, a comparison 2 to 4, a parallel
  stage one agent per independent workstream. Each spawn costs roughly 25k to
  35k tokens of setup, so small tasks that need no isolation get done inline.
- Every brief gives one objective, input file paths, an output path and
  format, allowed tools and sources, and explicit boundaries: what not to
  touch, and what belongs to other workers.

## Artifacts, not summaries

- Workers write full results to reports/ or the stage scratch path and return
  three things: the path, a summary of at most 200 words, and anything they
  could not finish.
- Workers return failures and non-survivors, not only winners.
- The lead reads the artifact files for anything entering the synthesis.

## Verification

- Every number entering a verdict (DSR, PBO, t-stat, P&L, trial count) gets an
  independent check at fable xhigh by a worker that did not produce it. The
  work being checked is normally opus-written, so the fable check is a second
  model's view, which reduces correlated errors. The same applies to
  adversarial reviews of declarations and harness code.
- Every citation used carries a verbatim quote from fetched full text, or is
  marked [unverified].

## ETA tables (two, for the operator)

- Estimate table, after planning and before the first spawn, printed in full
  in the chat reply: one row per task and per agent spawn, with owner (lead
  or agent name), model, effort, parallel or serial, the ETA for that row,
  and a cumulative ETA that accounts for which rows run in parallel. Base
  ETAs on measured probes where possible (a timed small run, or the duration
  of the same kind of work in an earlier stage's STATE file) and say which
  rows are guesses. This table is for the chat; it is not written into any
  markdown file.
- Checkpoints: after every task, update the task-status list in
  reports/<stage>_STATE.md (done, running, next, artifact paths, times).
  Print a revised estimate table in chat when the user asks or when the
  cumulative ETA moves by more than 30 minutes.
- Final table, at the very end, printed in full in chat and written into the
  progress entry as part of the Session cost section. It is the only ETA
  table that goes into any markdown file. One row per task and per agent
  spawn: agent name, model, effort, actual start and end, time taken, tokens
  from the transcripts, status and deviations; a closing cumulative row for
  the whole stage (total work time, total tokens, split lead versus workers)
  set against the initial estimate, with pauses and outages shown as their
  own rows and excluded from the work total (user instruction, 2026-09-22).

## Session cost (closing section of every progress entry)

Computed at the very end, after everything else is written:
- Wall-clock time: total, and per task from the STATE file timestamps. Show
  any pause, such as a usage-limit wait, separately so it is not counted as
  work.
- Tokens per model: sum each assistant message's usage fields (input,
  output, cache read, cache creation) by model across this session's own
  transcript and its subagent transcripts under
  ~/.claude/projects/<this project>/<session id>/ (the main .jsonl plus
  subagents/**/*.jsonl). One table: model, input, output, cache read, cache
  creation, total.
- One line per worker spawn: agent file, model, effort, tokens.
- Delegation share: the fraction of tokens spent by the lead versus workers,
  and by model tier.
- These are token counts, not plan-credit percentages. The session cannot
  read the /usage meter; the user records it before and after. If the
  transcripts cannot be read, say so and report time only. Never estimate
  token counts.

## Compute limits (stability over speed)

The ThinkPad has 14 GB of RAM, a recorded out-of-memory incident, and D.1e
pushed it to 90% CPU before a session died with the machine. A slower run
beats a throttled or crashed one (user instruction, 2026-09-23).
- Parallel compute jobs: at most half the cores (use `os.cpu_count() // 2`,
  never more than 8), and at most one heavy computation at a time across
  the lead and all workers.
- Run long computations at low priority (`nice -n 10`, or `os.nice(10)` at
  the top of the script).
- Before launching anything expected to take more than a few minutes, check
  available memory and estimate the job's peak; if the estimate exceeds half
  of what is available, run it in chunks.
- Long computations are resumable: they write progress to disk as they go
  and skip finished pieces on restart.
- Keep heavy runs out of the AiTrader collector window (it runs about
  15:30 to 16:00 PT on weekdays under news-collect.timer) and never kill or
  starve that service.

## Long and unattended runs

- The user is not watching. Do not stop to ask whether to continue. Run the
  stage to the end.
- After each task, append status to reports/<stage>_STATE.md: task done,
  artifact paths, next step. On resume, read that file first and skip
  finished tasks.
- Usage-limit interruption: the user resumes with
  `claude --resume <session-id>`. Finished work is on disk.
- If Fable usage runs out mid-stage, Fable-routed verification and review stay
  pending in the STATE file rather than being downgraded to opus; the lead
  finishes everything else and lists what is pending in the entry.
