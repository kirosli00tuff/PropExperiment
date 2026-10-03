STAGE E.12 "ML ROUTE V2: FREEZE THE DESIGN, BUY PHASE 1 WITH THE FUNDS ON HAND, RUN GATE 0 ONCE, THEN STOP"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage E.11 drafted the ML route v2 design and built its pipeline
on synthetic data (704 tests, every leakage canary caught, the simulator
matching the frozen engine to the cent). The user accepted all 19 of the
lead's V2.12 recommendations (V23) and pre-approved spending the funds
already in the two Databento accounts on phase 1. This session applies
those decisions to the draft, gathers the inputs the freeze needs (CME
margins, Topstep's 150K figures, the EC-K9 calendar for 2019-2024),
freezes v2 with a manifest, raises acct-2's cap, fixes the deferred key
items in harness v8, quotes and buys the phase-1 subset of training-window
history, builds the bars, applies the c/sigma filter, and runs Gate 0
exactly once. Then it stops, whatever Gate 0 says. No model selection, no
research-window read, no holdout read. Gate 0 decides whether v2 earns a
phase-2 purchase.

Decisions in force: docs/DECISIONS.md V18 (minimum trade count), V19
(account keys, the acct-2 cap raise to about $249.67), V20 (ML route v2),
V21 (K9 folded into v2), V22 (income path, more history not finer data,
phase 1 within the funds on hand, Gate 0 first), V23 (the 19 decisions,
the purchase pre-approval, the unused research-window Holm slot).

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: the session freezes a pre-registration, spends
money and reads training data for the first time under v2. The silent
failures to guard against: a freeze that leaves a free parameter open, a
purchase outside the subset rule or above the funds, a chunk at or after
2024-03 downloaded, a Gate 0 run more than once or with a bar changed
after data, and a Gate 0 number that is wrong. Spend, freeze and the Gate
0 verdict stay with the lead. Fable verifies the freeze against V23 and
recomputes the Gate 0 verdict numbers independently.

Usage: follows CLAUDE.md's context-hygiene rules. The user runs this
unattended. The auto-retry launcher resumes it with "read the STATE file
first", so reports/stage_e12_STATE.md names, after every task, the task
finished, the files and hashes in force, the ledger total per account
and the next task. Compute: the ThinkPad under the overnight profile.
Expect 4 to 6 hours.

Do not stop to ask. Decide, log the choice under Open choices in the
return document, and continue. The only stops are the ones this prompt
names, a decision that cannot be undone and could reasonably go either
way, or a guardrail conflict.

============================================================
SCOPE
============================================================

This stage does:
- apply V23 to docs/STAGE_E_ML_V2_DESIGN.md and the ml_route_v2 build
  (Task 1)
- gather the freeze inputs: CME maintenance margins, Topstep's 150K
  figures, the EC-K9 calendar for 2019-2024 (Task 2)
- freeze v2: the design marked FROZEN, a v2 freeze manifest hashing the
  design and the build, the program N read from the ledger (Task 3)
- harness v8: the acct-2 cap raise, the C-10 key fixes, and, if needed, a
  training-window-only option in the step 2 purchase path (Task 4)
- quote, rank and buy the phase-1 subset within the funds on hand (Task 5)
- build and validate the phase-1 bars, apply the c/sigma filter, run Gate
  0 once (Task 6)
- free quotes for everything later phases need (Task 7)
- verification by Fable (Task 8)

This stage does NOT:
- spend beyond acct-1's headroom (about $28.41) plus acct-2's $125 after
  the cap raise, or buy anything outside the phase-1 subset rule
- download any chunk at or after range=2024-03-01, any holdout-2 chunk,
  any research-window bar, or any tick or order-book schema
- read any research-window or holdout bar, or any Stage E screen or
  confirmation result figure
- fit any V2.6 configuration, run the nested CPCV selection, the engine
  paths or the payout simulation on real data. Gate 0's own fixed ridge
  fit (lambda 0.1, V2.2b) is the only fit on real data.
- run Gate 0 more than once, or change any Gate 0 rule after the freeze
  commit
- buy the 2010 extension or any phase-2 item (quotes only)
- touch live/, ops/, any TopstepX credential or the ProjectX API. Topstep
  facts come from Topstep's public help pages only.
- print, copy or log any key. REGISTRATION.md stays 0 bytes.

============================================================
CONTEXT TO READ FIRST
============================================================

Read by section, as CLAUDE.md's context-hygiene rules require.

1. CLAUDE.md and docs/ORCHESTRATION.md (including the page-fetch order).
2. docs/DECISIONS.md V18 to V23.
3. reports/E.11_RETURN.md sections 1, 6 and 7, and reports/stage_e11_rulings.md.
4. docs/STAGE_E_ML_V2_DESIGN.md: V2.1 (universe, price paths, phase-1
   rule), V2.2 (clock, c/sigma filter), V2.2b (Gate 0), V2.3 (signals and
   EC-K9), V2.7 (cost gate), V2.8 (sizing, the release-window rule), V2.9
   (N_total, success criteria), V2.12 (the decisions).
5. reports/stage_e10_catalog_K9.md: K9-anncday-01, EC-K9 (C9) and its
   official sources.
6. docs/STAGE_E_DESIGN.md (FROZEN): D4 (start rule, windows), D8 (costs),
   D13 (purchases).
7. The code: data/config.py, data/spend_gate.py, data/pull_step2.py,
   data/step2_store.py, data/step2_seal.py, data/holdout.py,
   screening/harness_freeze.py, screening/stage_e_start_dates.py,
   ml_route_v2/ (gate0.py, decide.py, panel and pipeline entry points),
   reports/stage_e0_topstep_facts.json, reports/stage_e0_liquidity.json,
   the cost_wall.json E.10 wrote.

============================================================
GUARDRAILS
============================================================

- Every Stage E harness command takes `--harness-sha256
  eee8a8b92a0210b245429135cf08b42f739b9328fa4eb49bf9034e5b387853d4` (v7)
  until Task 4 commits v8, then the v8 sha256. Fresh PYTHONPYCACHEPREFIX
  outside the repository.
- Spend (V23, item 19). The user pre-approved this purchase; no further
  approval is needed if every condition holds:
  - only through the frozen purchase path and its spend gate, never a
    direct client call;
  - only after a fresh quote-only run in this session, logged in the
    ledger at $0.00;
  - acct-1 first, up to its remaining headroom under
    SHARED_ACCOUNT_CAP_USD; then acct-2, up to its remaining headroom
    under ACCOUNT_2_CAP_USD = 249.67;
  - each exposure's purchase sits on one account, and its fresh quote
    fits that account's remaining headroom with a 3% margin;
  - the session caps equal the selected subset's fresh quote total plus
    3%, never above the combined headroom.
  A fresh quote that fits no exposure on either account stops the
  purchase with the figures for the user. A billed amount above its
  quote by more than 3% stops further buys.
- Windows: phase 1 downloads training-window chunks only, ending with
  range=2024-02-01_2024-03-01. No chunk at or after range=2024-03-01. The
  start follows the frozen step 2 path and the design's warm-up needs;
  if they disagree, the design governs, logged.
- Holdout status all_ok, 0 unlocks, at start, after the purchase and at
  end. The research window and holdout-2 are never read.
- Gate 0 runs once, after the freeze commit and the Gate 0 test list's
  registration in the append-only ledger. Any crash mid-run resumes from
  its checkpoint with the same inputs and constants fingerprint; a
  changed input or constant is a stop, never a rerun.
- Web access (Task 2 only): read-only fetches of CME margin pages,
  Topstep's public help pages, and the official release-calendar pages
  EC-K9 names, plus Wayback captures of those pages. No login, no paid
  source, no TopstepX or ProjectX page or API. Fetch order per CLAUDE.md.
- No key printed, copied or logged. REGISTRATION.md stays 0 bytes.

Start and end checks, quoted verbatim in the return: `git status
--short`, `git log --oneline -3`, the holdout status, `wc -c
REGISTRATION.md`, the manifest checks, the cluster freezes, the ledger
line count and sha256, the ledger total per account, `uv run pytest -q
-p no:cacheprovider` (expected at start: E.11's end, 6320 passed).

============================================================
TASK 0: STARTUP
============================================================

- Owner: lead. Output: reports/stage_e12_STATE.md and the ETA table.
- Done when: the start checks pass, HEAD is the commit holding this
  prompt or a descendant with a clean tree, and the preflight accepts v7.

============================================================
TASK 1: APPLY V23 TO THE DRAFT AND THE BUILD
============================================================

- Owner: lead for the design text; V23Coder-OpusXHigh (worker-xhigh on
  opus) for the code.
- Design: each V2.12 item marked decided, with V23 cited. Item 1: the
  gross reading becomes the built default (hurdles 1.5c / 2c / 3c, tau
  0.167), Gate 0 at 1.5c, family A in the Holm family. Item 11: the
  release-window rule written into V2.8. Item 14: the 1.5 x slippage
  sensitivity marked must-survive for the holdout-2 registration. Item
  16: deployment (a). The unused research-window Holm slot recorded in
  V2.9 with V23 cited.
- Code: the gross reading as the default in decide.py and the constants,
  tau 0.167 in the c/sigma filter, the release-window rule in the
  portfolio layer, with tests. The Gate 0 canaries rerun under the new
  defaults: noise fails, a planted gross edge passes, an edge between 1c
  and 1.5c fails Gate 0, and an edge in [1.5c, 2.5c) passes Gate 0 under
  the gross reading.
- Done when: the ml_route_v2 tests and canaries pass under the decided
  defaults, and no V2.12 item stays open except item 18 (Live Funded,
  decided later by the user).

============================================================
TASK 2: FREEZE INPUTS (WORKERS, IN PARALLEL)
============================================================

TASK 2a: CME MAINTENANCE MARGINS
- Owner: MarginFetch-OpusHigh (worker-high on opus).
- Output: reports/stage_e12_cme_margins.json: per vehicle of the 28 (and
  each price-path contract), the front-month maintenance margin in USD,
  the source URL, the fetch time and the method. Wayback captures when the
  live page blocks.
- Failure path: if CME's pages block every route for more than a few
  vehicles, the lead switches the whole ranking to the frozen E|m_1|
  (V23 item 3), logged. Never mix proxies within one ranking.

TASK 2b: TOPSTEP 150K FIGURES
- Owner: TopstepFacts-OpusMedium (worker-medium on opus).
- Output: reports/stage_e12_topstep_150k.md: the 150K MLL, the XFA
  scaling schedule (as text, read from the page or its image), the reset
  price, each with URL, fetch time and quote. Public help pages only.
- The lead updates the 150K parameters in the design and the payout
  simulator's inputs from this file. A figure that differs from V22's
  $4,500 is logged and used.

TASK 2c: THE EC-K9 CALENDAR FOR 2019-2024
- Owner: CalendarBuilder-OpusHigh (worker-high on opus).
- Output: the EC-K9 date set for 2019-05-01..2024-02-29 in the frozen
  calendar format, built from the official pages EC-K9 names, with a
  source row per date (CAL-* format), and a cross-check against the
  research-window rows already frozen (same rule, same sources).
- Done when: every date has a source row, the rule matches EC-K9's text
  exactly, and K9-anncday-01's signal passes its causality test on the
  new calendar. A year that no official source covers is logged, and
  K9-anncday-01 stays excluded for that span rather than guessed.

============================================================
TASK 3: THE V2 FREEZE (LEAD)
============================================================

- Output: docs/STAGE_E_ML_V2_DESIGN.md marked FROZEN with the date and
  V23; reports/stage_e12_ml_v2_freeze.json hashing the design, every
  ml_route_v2/ file, its tests, the constants, the cost wall, the margin
  file, the Topstep file and the EC-K9 calendar; the program N read from
  the ledger and written into the manifest; the universe table
  regenerated from cost_wall.json and checked against the design.
- The Gate 0 test list (families A and B over the phase-1 products, once
  the subset is known) is registered in the append-only ledger before
  Gate 0 computes, as the design requires. The freeze manifest records
  the rule that generates the list; the list itself is hashed at Task 6.
- One commit, "ML route v2 freeze", holding exactly the design, the
  manifest, the Task 1 code and tests, and the Task 2 files.
- Done when: the manifest verifies, and the commit exists before any
  purchase.

============================================================
TASK 4: HARNESS V8 (LEAD OR KeyCapFix-OpusXHigh)
============================================================

- Changes, all to frozen files, in one manifest:
  - ACCOUNT_2_CAP_USD = 249.67 (V19, V23), with the arithmetic shown
    from the ledger (cumulative acct-2 spend plus the $125 top-up);
  - C-10: data/config.py returns the stripped key; docs/ACCESS.md names
    DATABENTO_API_KEY1 and DATABENTO_API_KEY2;
  - the E.12 session caps per the spend guardrail;
  - if the step 2 purchase path cannot limit a purchase to the training
    window, a stated option that ends the plan at range=2024-02-01_2024-03-01
    and refuses any later chunk, with tests.
- Output: the v8 manifest, verified, its diff against v7 shown, and one
  commit "harness v8, acct-2 cap, key strip, training-window purchase"
  with the new sha256. Tests never print a key.
- Done when: v8 verifies and every later command uses its sha256.

============================================================
TASK 5: QUOTE, RANK AND BUY PHASE 1 (LEAD)
============================================================

- Quote: a fresh quote-only run for the training-window chunks of every
  exposure's price path (V2.1's table), ledgered at $0.00. NG's owned
  step 2 store is its price path and costs $0. MCL, MGC and MHG's owned
  stores are not price paths (V2.1).
- Rank: V2.1's rule exactly: the liquidity tier by median ADV
  (reports/stage_e0_liquidity.json), then c / sigma_proxy ascending with
  the Task 2a proxy, then the cluster round-robin, greedy to the budget,
  acct-1 first. Show the full ranking table, each step's remaining
  headroom per account, and every skip with its reason.
- Buy: the selected subset, through the purchase path with v8, chunk by
  chunk with the byte checks. Failed chunks retried once. A chunk still
  failing drops that exposure from phase 1 (logged), and its quote does
  not roll to another exposure unless the rule's next pick fits.
- Output: reports/stage_e12_purchase.md: the quotes, the ranking, the
  subset, the caps, the ledger lines, billed against quoted per chunk,
  the remaining balance per account, and the holdout status after the
  purchase.
- Done when: the subset is bought, no chunk at or after 2024-03 exists
  on disk for any new root, and the ledger reconciles to the cent.

============================================================
TASK 6: BARS, FILTER AND GATE 0 (LEAD RUNS THE FROZEN PIPELINE)
============================================================

- Bars: build and validate the phase-1 bars with the frozen store path;
  the D4 start rule per exposure (S_X); counts per root; vendor-degraded
  dates flagged as the design says.
- c/sigma filter: tau 0.167 on the training window, per (product,
  horizon). Output the admissible pairs and every dropped pair with its
  ratio. The filter reads volatility only.
- Register the Gate 0 test list (|A| = signals x 3 horizons, |B| = the
  admissible pairs) in the append-only ledger, hash it, and record the
  hash in the STATE file before computing.
- Run Gate 0 once: families A and B, CPCV per V2.2b, the pass bar as
  frozen. Output reports/stage_e12_gate0.md and its JSON: every test's
  statistic, p-value and Holm decision; for family B each pair's mean
  gross per trade against c, t_B and trade count; the pooled result;
  the descriptive rank ICs; and the verdict, PASS or FAIL, with the
  pairs that pass.
- The new program N (N_program plus the Gate 0 tests) is written to the
  return.
- Done when: the verdict is on disk with its hashes, and Fable has
  verified it (Task 8).

============================================================
TASK 7: FREE QUOTES FOR LATER PHASES (LEAD)
============================================================

- Quote-only, ledgered at $0.00, nothing bought:
  - phase 2: the training window of the exposures not bought in phase 1;
  - holdout-2 chunks (2024-03..2025-03) for all 28 price paths;
  - the research-window bars of the price-path contracts not already
    owned (the vehicles' research-window bars are owned from E.1);
  - the 2010 extension: full-size price paths 2010-01-04..2019-05-03.
- Output: a table in reports/stage_e12_purchase.md with each item's
  quote, the funds left, and the top-up each later purchase needs.

============================================================
TASK 8: VERIFICATION (FABLE)
============================================================

- FreezeReviewer-FableXHigh (worker-xhigh on fable): checks that the
  frozen design matches V23 item by item, that no free parameter is left
  open except item 18, that the manifest covers everything Gate 0 reads,
  and that the freeze commit precedes the purchase and Gate 0.
- Gate0Verifier-FableXHigh (worker-xhigh on fable): recomputes the Gate
  0 verdict numbers independently from the bars and the frozen rules,
  without reading the lead's statistics first: the admissible pairs, the
  passing pair's (or the best pair's) mean gross, c, t_B, trade count and
  Holm decision, and three family A statistics chosen at random.
  Agreement to the stated tolerance or a written discrepancy.
- Output: reports/stage_e12_review.md, findings graded BLOCKING, SHOULD
  FIX or NOTE, and the lead's rulings in reports/stage_e12_rulings.md.
- A BLOCKING finding on the Gate 0 numbers is resolved by finding the
  error in code, never by rerunning Gate 0 with changed rules. If the
  error cannot be resolved, the verdict is reported as unverified.

============================================================
TASK 9: RETURN AND COMMIT (LEAD)
============================================================

- One commit after the freeze and v8 commits, "Stage E.12 ML route v2
  phase 1 and Gate 0", holding the reports, the Gate 0 outputs and
  ledger registration, the STATE file and the briefs. Bars and raw data
  stay where the frozen store keeps them, never in git.
- No push.

============================================================
DELEGATION PLAN
============================================================

| Task | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup | lead | opus | xhigh | first | gates the session |
| 1 Apply V23 (design) | lead | opus | xhigh | after 0 | pre-registration judgment |
| 1 Apply V23 (code) | V23Coder-OpusXHigh | opus | xhigh | parallel with 2 | frozen-default code and canaries |
| 2a CME margins | MarginFetch-OpusHigh | opus | high | parallel | web data with sources |
| 2b Topstep 150K | TopstepFacts-OpusMedium | opus | medium | parallel | narrow lookup |
| 2c EC-K9 2019-2024 | CalendarBuilder-OpusHigh | opus | high | parallel | sourced calendar, rule-exact |
| 3 Freeze | lead | opus | xhigh | after 1 and 2 | reserved to the lead |
| 4 Harness v8 | lead or KeyCapFix-OpusXHigh | opus | xhigh | after 3 | frozen-file change |
| 5 Quote, rank, buy | lead | opus | xhigh | after 4 | spend, reserved to the lead |
| 6 Bars, filter, Gate 0 | lead | opus | xhigh | after 5 | the verdict, reserved to the lead |
| 7 Free quotes | lead | opus | xhigh | after 5, any time | ledgered quotes |
| 8 Freeze review | FreezeReviewer-FableXHigh | fable | xhigh | after 3 | independent check of the freeze |
| 8 Gate 0 verify | Gate0Verifier-FableXHigh | fable | xhigh | after 6 | verdict numbers verified |
| 9 Return, commit | lead | opus | xhigh | last | reserved to the lead |

Usage pools: Fable runs only the two checks, at xhigh, to keep the Fable
weekly pool for later stages. Web lookups go to Opus (high, medium for
the narrow one), per the 2026-09-24 rule.

At most 4 workers at once. Workers write files and return paths.

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

Compute: heavy steps (bar build, Gate 0's CPCV) run at nice 10 under the
overnight profile, with peak memory under 70% of free memory at launch,
and resumable checkpoints.

============================================================
VERIFICATION
============================================================

- The freeze commit precedes the purchase, and the Gate 0 list hash
  precedes Gate 0's computation. The return shows both orders from git
  and the ledger timestamps.
- The ledger reconciles: quoted against billed per chunk, the totals per
  account, under the caps.
- No chunk at or after 2024-03 on disk for any new root. Holdout status
  unchanged.
- Fable verifies the freeze and recomputes the Gate 0 verdict numbers.

============================================================
WHAT NOT TO DO
============================================================

- No spend beyond the funds on hand, no purchase outside the subset rule,
  no 2010 extension or phase-2 purchase.
- No chunk at or after 2024-03. No research-window or holdout read.
- No V2.6 model selection, no engine paths, no payout simulation on real
  data.
- No second Gate 0 run, and no Gate 0 rule changed after the freeze.
- No key printed. No push. No write to REGISTRATION.md. No TopstepX or
  ProjectX access.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.12_RETURN.md. Fixed sections, in order:

1. Verdict summary, at most 250 words: the Gate 0 verdict (PASS or FAIL)
   and its decisive numbers, the phase-1 subset and what it cost, the
   funds left, the freeze and v8 hashes, the new program N, and the
   top-up phase 2 would need.
2. Guardrail evidence: the start, post-purchase and end checks verbatim.
3. Results per task: V23 applied, the freeze inputs (margins, 150K
   figures, EC-K9 coverage), the freeze, v8, the ranking and purchase,
   the bars, the c/sigma filter, Gate 0 in full, the later-phase quotes.
4. Delegation record: one row per spawn.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user: on a PASS, the phase-2 purchase and its
   top-up, the 2010 extension and the D4 amendment it needs, and the
   modelling stage; on a FAIL, what v2's stop means and the options left
   (V22's personal-account path, the AiTrader readout), each with a
   recommendation.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

Also write one short dated progress.md entry and one line in
docs/STAGES.md.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
