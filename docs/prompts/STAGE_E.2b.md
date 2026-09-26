STAGE E.2b "STAGE E BUILD, PART 2: SCREENING RUNNER, ML PIPELINE, CANARIES, STEP 2 PURCHASE PATH, HARNESS FREEZE (NO MEMBER RUN, NO PURCHASE)"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage E.2a (commits ba67073, 04c504f, 10454b1) froze the ML
route design (manifest reports/stage_e2a_ml_freeze.json, sha256
077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2),
recorded the source-window amendment, and built the per-product rules
engine, eight group calendars, the research-window bars of 45 contracts,
the frozen cost tables, the vehicle choice (28 traded exposures) and the
funnel epsilon, all verified by Fable with 0 discrepancies
(reports/E.2a_RETURN.md). This session finishes the Stage E build. It
builds the generalized screening runner (D11.6) and cross-product
alignment (D11.5), the ML route's pipeline with every M7 leakage test
(D11.7, docs/STAGE_E_ML_DESIGN.md M3 to M8), the canaries per product and
across products (D11.9), and the step 2 purchase path with holdout-2
sealing per product. It refreshes the free quotes for the step 2 history.
It then freezes the whole harness with a sha256 manifest and commits it,
after an adversarial Fable max review. It stops there. The next sessions,
in order: K2's screening session (research window only, needs no
purchase), then the ML route's purchase and training (needs the user to
fund acct-2), then the other clusters.

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: this is an implementation session, and CLAUDE.md
routes harness, screening and data code to opus at xhigh. The only
judgment is the lead's rulings on the review findings. Ultracode stays off.
E.2a showed its fan-out went to research-style work at large contexts
(the calendar workflow, 41% of that stage's tokens), and this session has
four coding workstreams that the worker files route precisely.

Usage: this session follows the context-hygiene rules added to CLAUDE.md
on 2026-09-26. Read files by section, keep command output short, give each
worker one objective, and use fresh workers for large new briefs. Fable is
used once: HarnessAuditor-FableMax, the single adversarial review this
stage hinges on (Task 7). Every Stage E verdict will rest on this harness
being free of look-ahead and leakage. No number enters a verdict in this
session, so there is no separate Fable xhigh number check. If Fable is
unavailable when Task 7 starts, finish everything else, do not make the
freeze commit, and mark Task 7 and 8 pending. Never substitute opus for
the review. Compute follows the overnight profile in CLAUDE.md, including
the RTX 3050 for the LSTM probe.

Do not stop to ask. Decide, log the choice under Open choices in the
return document, and continue. The only stops are the ones this prompt
names, a decision that cannot be undone and could reasonably go either
way, or a guardrail conflict.

============================================================
SCOPE
============================================================

This stage does:
- build and test the generalized screening runner and cross-product
  alignment (Task 1)
- build and test the ML route's pipeline and every M7 test, on synthetic
  data only, with timed probes on synthetic data of the real size (Task 2)
- extend the leakage canaries to every product group, to cross-product
  members and to the ML route's rule wrapper (Task 3)
- build the step 2 purchase path with holdout-2 sealing per product, fix
  the purchase guard to refuse by CME trade date, and run free quotes
  (Task 4)
- record the MBT holdout-1 rows found in E.2a (Task 5)
- write the harness freeze manifest, have it reviewed, rule on the review,
  and commit the freeze (Tasks 6 to 8)

This stage does NOT:
- buy anything. Quotes only, at $0.00. The step 2 history is bought in the
  ML route's purchase session or a cluster's confirmation session, after
  the user funds acct-2.
- code, run, screen or score any catalog member. Each cluster's screening
  session codes its own members, hashes them, and runs them. This session
  provides the runner and a member template only.
- read any research-window bar for any purpose beyond the known-answer
  regressions named in Task 1 (MES's own bars, and the existing E.2a
  parquets' row counts and hashes).
- fit, tune or train any model on real data. The ML pipeline is tested on
  synthetic data.
- edit any file frozen by reports/stage_e1_freeze.json or
  reports/stage_e2a_ml_freeze.json, or any table E.2a recorded by hash
  (costs, sizes, vehicles, readings, epsilon declaration and addendum,
  source-window amendment, epsilon results).
- touch holdout-1 or holdout-2, live/, ops/, or any TopstepX credential or
  API
- edit docs/NULL_CRITERIA.md or reports/stage_d1f_confirmation_list.md
- write to REGISTRATION.md (it stays 0 bytes)
- push. The session makes exactly the one freeze commit Task 8 names.

============================================================
CONTEXT TO READ FIRST
============================================================

Read by section, as CLAUDE.md's context-hygiene rules require.

1. CLAUDE.md and docs/ORCHESTRATION.md: roles, routing, worker files,
   concurrency, artifacts, checkpoints, the ETA tables, Session cost, the
   overnight profile and context hygiene. This prompt does not repeat
   them. On any conflict CLAUDE.md wins, and the conflict is logged.
2. reports/E.2a_RETURN.md, sections 1, 6 and 7 (the E.2b list: roll
   blackouts per group L-8, vendor-unit ticks for cent-quoted grains and
   livestock, the flatten rules R-F1 and R-F4 in rules/sessions.py, the
   event-window cost under D8's literal reading T12-4, the MBT rows booked
   to 2026-06-22 L-9, the 2026-06-18/19 roll check, L-12 left to K1).
3. docs/STAGE_E_DESIGN.md (FROZEN): D4 (power check), D5 (tiers, the
   screen, Holm), D6 (ports and session table), D8 (costs, event window),
   D9 (the constraint set, the member-level coverage check, the trade-rate
   floor), D11 (items 4 to 7 and 9).
4. docs/NULL_CRITERIA_E.md (FROZEN), for what the runner's outputs must
   support.
5. docs/STAGE_E_ML_DESIGN.md (FROZEN): M1 to M8, especially M7 items 1 to
   9 and the E.2a rulings in brackets.
6. The existing code: screening/runner.py (screen_candidate, line 431),
   tests/test_leakage_canaries.py, tests/test_screening_runner.py,
   tests/test_d1f_runner_hardening.py, sim/engine.py, sim/fill_model.py,
   the E.2a modules (rules/products.py, rules/constraints.py,
   rules/sessions.py, rules/price_limits.py, data/calendars/,
   data/build_bars.py, sim/product_costs.py, screening/vehicles.py,
   funnel/exposure_gate.py), data/pull_universe.py, data/pull_mes.py (its
   holdout-2 sealing path), data/holdout.py, and
   strategy/research/_d1f_freeze.py (the manifest template).

============================================================
GUARDRAILS
============================================================

CLAUDE.md invariants apply in full. This stage adds:

- Both freeze manifests verify at start and at end (reports/stage_e1_freeze.json,
  reports/stage_e2a_ml_freeze.json, with the audit files compared at
  their freeze-commit blobs as their manifests note). A mismatch stops the
  session.
- The E.2a hashed tables verify at start and at end against the hashes in
  reports/E.2a_RETURN.md section 7.
- Spend: quotes only. The quote path uses a new E.2b session id with $0.00
  session and request caps. `git diff` of the ledger shows only $0.00
  quote lines.
- Holdout status at start and end: both all_ok, 0 unlocks.
- Research-window data: only the Task 1 regressions read bars, and only
  MES's research bars and E.2a's recorded row counts and hashes. No new
  product's price is read.
- MES regression: every existing test passes unchanged, and the
  generalized runner reproduces D.1's MES screening results bit for bit on
  the members Task 1 names.
- Compute: the overnight profile. Check memory and free VRAM before each
  heavy job.
- REGISTRATION.md stays 0 bytes. No TopstepX reference of any kind.

Start and end checks, quoted verbatim in the return document: `git status
--short`, `git log --oneline -3`, the holdout status, `wc -c
REGISTRATION.md`, the manifest and table checks, `uv run pytest -q`
(expected at start: 1891 passed, 2 skipped, 1 xfailed).

============================================================
TASK 0: STARTUP
============================================================

- Owner: lead.
- Inputs: the context files.
- Output: reports/stage_e2b_STATE.md, and the estimate ETA table in chat
  and in the STATE file.
- Done when: the start checks are recorded, HEAD is a3c3292 or a
  descendant with a clean tree, and every manifest and table verifies.
- Failure path: any mismatch, a dirty tree, or a holdout status other than
  all_ok stops the session with a named refusal.

============================================================
TASK 1: THE GENERALIZED SCREENING RUNNER (D11.5, D11.6)
============================================================

- Owner: RunnerCoder-OpusXHigh, worker-xhigh on opus.
- Inputs: screening/runner.py, the E.2a modules, the frozen D4, D5, D6,
  D8 and D9, the E.2a return's E.2b list.
- Output:
  - screen_candidate generalized to take a product's rules, calendar,
    cost table, vehicle, q_c and epsilon from the frozen E.2a files, never
    from arguments a session could vary.
  - Cross-product alignment on a shared UTC minute grid: no forward fill
    into a signal, and a member whose leg has no bar at a decision time
    does not trade (D11.5).
  - Member-level coverage check (at least 0.95 in the member's own window,
    D9) and the trade-rate floor (at most 20 entries a day, a 2-minute
    minimum hold, a 10-minute mean hold) applied before any member result
    is written. A failing member is labelled, not dropped.
  - The D4 power check machinery (n_b analytic, and the block-bootstrap
    simulation where they differ by more than 15%) and the D5 screen
    (research-window mean net P&L > 0 and daily t >= 1.0) with the Tier A
    and Tier B assignment, both computed by the runner, never by hand.
  - The E.2a carried items: roll blackouts from each product's group
    calendar (L-8), vendor-unit ticks for cent-quoted grains and livestock,
    the flatten rules of rules/sessions.py (R-F1, R-F4), the event-window
    cost under D8's literal text, the largest s_b and not max(s_b + depth)
    (T12-4), a refusal of MBT's rows booked to trade date 2026-06-22 (L-9),
    and a check of 2026-06-18/19 for an unseen roll.
  - A member template (strategy/stage_e/_template.py) and a per-cluster
    code-freeze helper that hashes a cluster's member modules before its
    screening session runs any of them.
  - Tests with known answers, plus MES regressions: the generalized runner
    reproduces D.1's screening output for three MES trials (one C1, one
    C2, one C4) bit for bit on MES's own research bars.
- Done when: the new tests pass, every existing runner and canary test
  passes unchanged, and the regressions match.
- Failure path: a frozen rule the runner cannot encode without a new
  choice is logged as a question for the user, and the runner refuses
  that case by name rather than guessing.

============================================================
TASK 2: THE ML ROUTE PIPELINE AND M7 TESTS (D11.7)
============================================================

- Owner: MLPipelineCoder-OpusXHigh, worker-xhigh on opus.
- Inputs: docs/STAGE_E_ML_DESIGN.md (FROZEN), M3 to M8 with every E.2a
  ruling in brackets.
- Output:
  - lightgbm and torch added to pyproject.toml and pinned in uv.lock
    (torch with CUDA support for the RTX 3050). Record the versions.
  - The training-window bar store builder. It reads only the training
    window, refuses any row on or after 2024-03-01, and has nothing to
    read yet, since the history is not bought.
  - The feature pipeline (M4) with availability timestamps and the
    validator, the net target with the D8 cost model, the CPCV splitter
    with purge and embargo by trade date (M7.3), the LightGBM and PyTorch
    jobs with fixed seeds, resumable ledgers and the model hash chain
    (M7.6), the surrogate-tree and block-6 pre-test code (M5, including the
    E.2a rulings ML-A01 and ML-A02), and the route manifest writer.
  - Every M7 test with known answers: the feature-timestamp validator and
    its two canaries (M7.1), the perturbation test (M7.2), the fold test
    (M7.3), the window test with a planted research-window bar that must
    make the job refuse (M7.4), the normalization test (M7.5), the hash
    chain (M7.6), and the rule wrapper through the existing canaries
    (M7.7).
  - Timed probes on synthetic data of the real size (about 450,000 rows,
    20 features, 31 products): one LightGBM configuration on one CPCV split
    at 8 threads, and one LSTM configuration for one epoch on the GPU, with
    the batch size planned by the frozen A-1 rule to leave at least 0.5 GB
    of VRAM free. Write the measured times, peak memory and peak VRAM to
    reports/stage_e2b_ml_probes.json, and the projected full-run time per
    challenger.
- Done when: every M7 test passes, the probes are recorded, and nothing in
  the pipeline can read a date the frozen partition forbids.
- Failure path: if torch cannot use the GPU, record why, run the LSTM
  probe on the CPU, and report the projected time. Do not change the
  frozen design's challenger list.

============================================================
TASK 3: CANARIES (D11.9)
============================================================

- Owner: CanaryCoder-OpusXHigh, worker-xhigh on opus. Starts once Task 1's
  runner interface exists.
- Inputs: tests/test_leakage_canaries.py, the Task 1 runner, the Task 2
  rule wrapper.
- Output: canaries run through the generalized runner for one synthetic
  product of every group (planted future bars, planted settlement values,
  a planted bar inside a closure), a cross-product canary (a planted
  future bar in one leg must not change the other leg's decisions), and
  the ML rule wrapper's canary.
- Done when: every canary fails loudly when its leak is planted, and
  passes when it is not.
- Failure path: a canary that cannot be made to fail on a planted leak is
  a BLOCKING finding for the lead, recorded, and the freeze waits for its
  fix.

============================================================
TASK 4: STEP 2 PURCHASE PATH AND QUOTES (NO PURCHASE)
============================================================

- Owner: PurchaseCoder2-OpusXHigh, worker-xhigh on opus.
- Inputs: data/pull_universe.py, data/pull_mes.py (holdout-2 sealing in
  the download call), data/holdout.py, data/config.py, the vehicles file,
  the ML freeze's list of 31 price-path contracts.
- Output:
  - The purchase guard fixed to refuse by CME trade date, not only by
    timestamp, so a request can never deliver bars booked to a holdout
    trade date (the E.2a L-9 finding). A test plants MBT's 2026-06-22
    case.
  - The step 2 path: ohlcv-1m monthly chunks 2019-05..2025-03 for a
    given contract list, oldest first, each holdout-2 chunk (2024-03
    through 2025-03) sealed in the download call after its byte check, one
    sealed store per product, the same unlock log, and a per-cluster mode
    for confirmation purchases. --quote-only issues no billable request.
    Tests prove the sealing order, the refusal of holdout-1 dates, the
    per-account caps on acct-2, and resume.
  - A free quote run, under the E.2b session id with $0.00 caps, for two
    request sets: (a) the ML route's 31 price-path contracts over
    2019-05..2025-03, (b) each cluster's chosen vehicles over the same
    range. Output reports/stage_e2b_step2_quotes.json and .md, with the
    totals per set and per cluster, and the acct-2 top-up the user needs
    for each (acct-2 holds $21.52 by the gate's count).
- Done when: the tests pass and the quotes are recorded.
- Failure path: a quote failure is logged and the set is reported
  incomplete. No cap changes.

============================================================
TASK 5: MBT HOLDOUT-1 ROWS (LEAD)
============================================================

- Owner: lead.
- Inputs: reports/E.2a_RETURN.md section 2, Task 4's guard fix.
- Output: a docs/DECISIONS.md entry dated 2026-09-26: the 1,617 MBT bars
  booked to trade date 2026-06-22 arrived inside the step 1 files because
  the guard checked timestamps, were dropped unread by the bar builder,
  were never written to any parquet, and are now refused by every loader
  and by the purchase guard. Nothing is deleted.
- Done when: the entry exists and a loader test proves the refusal.
- Failure path: none expected.

============================================================
TASK 6: HARNESS FREEZE MANIFEST (LEAD)
============================================================

- Owner: lead, with a small script modelled on
  strategy/research/_d1f_freeze.py.
- Inputs: every harness file Stage E's sessions will run.
- Output: reports/stage_e2b_harness_freeze.json: the sha256 of every file
  in rules/, sim/, screening/, funnel/, data/ (code, calendars), the ML
  route pipeline, strategy/stage_e/_template.py, the E.2a hashed tables,
  both earlier manifests, and pyproject.toml and uv.lock. It also records
  HEAD and the creation time. A preflight function that every later Stage
  E runner calls refuses on any mismatch.
- Done when: the manifest verifies by script, and a test proves the
  preflight refuses a one-byte change to a listed file.
- Failure path: a file that changes between the audit and the commit
  forces a new manifest and a note in the rulings.

============================================================
TASK 7: ADVERSARIAL HARNESS REVIEW (FABLE MAX)
============================================================

- Owner: HarnessAuditor-FableMax, worker-max on fable. It wrote none of
  the code it reviews.
- Inputs: the harness files in the manifest, the frozen designs, the
  tests.
- Output: reports/stage_e2b_harness_review.md, each finding graded
  BLOCKING, SHOULD FIX or NOTE, with file and line.
- The brief, what to hunt:
  - look-ahead in the runner: a signal or cost reading a bar, a
    settlement or a release value before its availability time
  - leakage in the ML pipeline: any path by which a research-window,
    embargo or holdout date, or a statistic computed from one, reaches
    training, tuning, normalization or distillation
  - frozen values a session could change: any input the runner or the
    pipeline takes from an argument, environment variable or file outside
    the manifest
  - canaries that cannot fail, or tests that pass for the wrong reason
  - holdout handling in the step 2 path: the sealing order, trade-date
    refusal, and any way plaintext holdout bytes could persist
  - the D4 power check and the D5 screen computed differently from the
    frozen text
- Done when: every item on the brief has a finding or an explicit "none
  found" with the files read.
- Failure path: if Fable is unavailable, stop before Task 8 as the Usage
  paragraph says.

============================================================
TASK 8: RULINGS AND THE FREEZE COMMIT (LEAD)
============================================================

- Owner: lead.
- Inputs: the review.
- Output: reports/stage_e2b_harness_rulings.md, the fixes, a re-run of the
  full test suite, the final manifest, and one commit.
- Done when: every BLOCKING and SHOULD FIX finding has a ruling and its
  fix, the full suite passes, the manifest verifies, and one commit on main
  holds the harness code, the tests, the manifest, the review, the
  rulings, docs/DECISIONS.md and the quote reports, with a message naming
  the manifest sha256 and "Stage E harness freeze", ending with this
  repository's attribution lines.
- Failure path: a BLOCKING finding that cannot be fixed without changing a
  frozen design stops the freeze, and the finding goes to the user. The
  code stays uncommitted.

============================================================
DELEGATION PLAN
============================================================

| Task | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup, ETA | lead | opus | xhigh | first | gates the session |
| 1 Screening runner | RunnerCoder-OpusXHigh | opus | xhigh | parallel with 2 and 4 | screening/ and sim/ code |
| 2 ML pipeline, M7 tests, probes | MLPipelineCoder-OpusXHigh | opus | xhigh | parallel with 1 and 4 | leakage-critical code |
| 3 Canaries | CanaryCoder-OpusXHigh | opus | xhigh | after 1's interface and 2's wrapper | leakage tests |
| 4 Step 2 path, guard, quotes | PurchaseCoder2-OpusXHigh | opus | xhigh | parallel with 1 and 2 | data/ code that will spend money |
| 5 MBT entry | lead | opus | xhigh | after 4's guard | small, inline |
| 6 Manifest | lead | opus | xhigh | after 1 to 5 | reserved to the lead |
| 7 Harness review | HarnessAuditor-FableMax | fable | max | after 6 | the one adversarial call the stage hinges on |
| 8 Rulings, freeze commit | lead | opus | xhigh | after 7 | reserved to the lead |
| Return document | lead | opus | xhigh | last | reserved to the lead |

At most 4 workers at once. Each worker has one objective and ends when it
is done. A large follow-up gets a fresh worker, not a resumed one.

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

============================================================
VERIFICATION
============================================================

- The harness is reviewed adversarially by HarnessAuditor-FableMax, which
  wrote none of it (Task 7).
- No number enters a verdict in this session. The MES regressions and the
  known-answer tests are deterministic checks against recorded results.
- The lead rules on every finding in writing and applies the fixes. It
  never re-runs the review to get a different answer.
- If Fable runs out, the review stays pending and the freeze is not
  committed.

============================================================
WHAT NOT TO DO
============================================================

- No purchase, no cap change, no ledger line above $0.00.
- No catalog member coded or run.
- No new product's price read. No model fitted on real data.
- No edit to any frozen file or E.2a hashed table.
- No existing test weakened. No MES result changed.
- No push, and no commit beyond the freeze commit.
- No write to REGISTRATION.md. No edit to docs/NULL_CRITERIA.md.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.2b_RETURN.md. The planning chat reads this one file to
review the session. Fixed sections, in order:

1. Verdict summary, at most 200 words: what was built and what was not,
   the harness manifest sha256 and the commit hash, the review's headline,
   the step 2 quotes and the acct-2 top-up needed for the ML route and for
   the first cluster, and whether K2's screening session is unblocked.
2. Guardrail evidence: the start and end checks verbatim, the manifest and
   table checks, the ledger diff, `git status --short` and `git diff
   --stat` at the end, and which bars were read and why.
3. Results per task: each artifact path, its test count and what each test
   proves, the MES regression results, the ML probe times and projected
   run times, the canary results, and the quote tables.
4. Delegation record: one row per spawn with agent name, worker file,
   model, effort, objective, status and deviations.
5. Verification: each review finding, the lead's ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. What the next session must do first: the push the planning chat owes,
   the frozen files and hashes, the funding the user owes, and what K2's
   screening session needs from this harness.
8. Session cost: the final ETA table (one row per task and per spawn,
   actual start and end, time taken, tokens from the transcripts, status)
   and the per-model token table, per CLAUDE.md. Never estimated.

Also write one short dated progress.md entry that points to the return
document, and one line in docs/STAGES.md.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
