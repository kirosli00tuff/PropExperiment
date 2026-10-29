STAGE E.34 "ZL PROGRAM: DESIGN AND FROZEN PROTOCOL (NO PURCHASE, NO REGISTRATION)"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: E.32b's only recommended build is one ZL program at Topstep:
- two families in one registration: F10, order-book state at 5 minutes
  and longer; and F09, soy-complex lead-lag and relative value into ZL;
- discovery on 2020-12..2024-02, then the single read of ZL's sealed
  window 2017-05..2020-11;
- prior about 4%; the last build under E.32b's stop rule.
The user asked to run work that needs no Databento key now. This stage
does the design half, modelled on E.32, specialised to ZL and building on
E.32's methods brief and E.33's frozen, proven pipeline:
- a ZL methods addendum;
- data facts from the owned files;
- the exposure audit of the discovery dates;
- a frozen discovery protocol for a later run stage.
It buys nothing, registers nothing, trains nothing and reads no outcome.
N stays 838.

Decisions in force: docs/DECISIONS.md V20 to V57. Binding, in order:
- this prompt;
- E.32b's recommendations, section 4.5 (the ZL fact table, the draft
  pre-registration outline, the data plan) and section 6 (the stop
  rule);
- V43, V50, V51, V55, V56.
The user's decisions D2 and D3 of E.32b are still open:
- D2: give ZL's single sealed read to this program;
- D3: admit a discovery search judged by the power rule instead of
  V31's cost gate.
So this stage freezes the protocol but does not register it. Registration
belongs to the run stage, after the user decides D2 and D3.

Read first:
- reports/E.32b_RETURN.md
- reports/stage_e32b_recommendations.md (sections 0, 4.1-4.5, 6, 7)
- reports/stage_e32b_holding_scope.md (the ZL rows)
- reports/stage_e32_discovery_protocol.md (the model for every section,
  by search, not whole)
- reports/stage_e32_methods_brief.md (the front; the rest by search)
- reports/E.33c_RETURN.md
- reports/E.33_RETURN.md section 3
- reports/stage_e32_test_seal.md
- reports/stage_e32b_briefs/F2_grains.md (ZL facts)

Lead: Opus 5.5, effort max. Ultracode only if the lead judges it
necessary. Routing per V55:
- Reviewers: Fable xhigh, model confirmed from the transcript; Opus
  fresh if Fable is unavailable.
- Extraction and file parsing: Haiku.
- Low-to-mid tasks: Sonnet.
- Everything else: Opus.
- At most 6 workers at once.
Never sacrifice quality to save usage.

Time: launched about 12:00 PDT on 2026-10-29, with no fixed end.
Checkpoint reports/stage_e34_STATE.md after every step and resume from it.
When the lead's context passes about 300k tokens at a quiet point, write
RESUME HERE and "READY FOR WIPE <time>", then stop.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the choice
under Open choices in the return document, and continue.

============================================================
PART 0: SEAL AND EXPOSURE (FIRST)
============================================================

0.1 Confirm the E.32 test seal covers every ZL, ZS and ZM file from
2017-05-01 to 2020-11-30 (all schemas, owned bars included), with the
guard dry check and the holdout status. Seal any ZL file that
touches the window but is not yet covered.

0.2 Exposure audit of the discovery dates 2020-12..2024-02 for ZL, from
the ledgers, E.31's and E.33's code and the E.23 inventory. List every
earlier read of ZL data and what was computed, for example:
- E.31's passive markouts on ZL MBP-1;
- E.33's ZL-based features (the crush residual, ZS and ZL propagation)
  with ZM labels;
- the bar-level trials on ZL.
State plainly which proposed features or labels were already looked at
in any form. State how the protocol keeps that exposure from steering
its choices, or which choices are excluded because of it.

============================================================
PART M: ZL METHODS ADDENDUM
============================================================

Extend E.32's brief, citing it and not repeating it. Each topic gives its
equations, a worked ZL example (tick 6 USD, a typical sigma from
E.32b's F3), its data needs, its leakage traps and a verdict:

- M1 F10 on ZL: which of E.32's F3 order-book features carry over to
  ZL, which need MBO and which work from MBP-1, and the minimum
  aggregation horizon given ZL's message rate. Decide whether discovery
  needs ZL MBO (a purchase in the run stage) or can use the owned ZL
  MBP-1 front month. Give the reasons and the cost difference (E.32b
  4.5(c)).
- M2 F09 into ZL:
  - the crush residual with ZL as the adjusting leg (E.33 tested ZM as
    the adjusting leg);
  - ZS and ZM leading ZL;
  - the biofuel and energy linkages (CL, HO, RB) as candidate leaders,
    only if the data is owned or free;
  - whether ZL, not ZM, is the leg that adjusts, with the half-life
    method.
  E.33's negative on ZM constrains what is plausible here; say how.
- M3 Labels and holding band from E.32b's F5 (Topstep ZL band 15-60
  minutes): the label set, cost-aware targets, and the trade-through and
  market execution variants of E.32 M6.
- M4 Power and N: the minimum detectable net edge at the discovery and
  test windows' lengths, at N 838 plus this program's budget, against
  E.32b's 1.8-tick test detectable edge (K2).

============================================================
PART F: DATA FACTS (COUNTS, SIZES, SCHEMAS ONLY)
============================================================

From the owned ZL MBP-1 (E.31) and the ZS, ZM and ZL bars, record:
- schemas, fields and timestamps;
- message counts per day;
- roll handling;
- disk and memory needs;
- what E.33's pipeline can reuse.
No price, return, feature value or label is computed or looked at.

============================================================
PART P: THE FROZEN PROTOCOL (FOR THE RUN STAGE)
============================================================

Write reports/stage_e34_zl_protocol.md, sections P1 to P10 as in E.32:
- data and windows, and the exposure handling from 0.2;
- the families (F10 and F09 only, unless the lead rules a family out on
  power or exposure, with the reason);
- labels, horizons and features (exact formulas);
- models (at most 2 families, with finite grids);
- validation (purged and embargoed);
- the search budget (exact count, the N after the run, the DSR and FDR
  thresholds);
- the selection rule;
- the test registration sketch (one read, the pass bar with Holm);
- stop rules, including E.32b's K0 to K4;
- the compute-stop reference, set from a real-data timing probe or the
  protocol's own guess range, never a synthetic-only probe (E.33b D3).
Include the run-stage data plan:
- what to buy, if anything, for discovery and for the test, with
  E.32b's cost estimates;
- a quote taken first, under the user's approval and a new account
  slot (DATABENTO_API_KEY4).

Review:
- ProtocolReviewer (Fable xhigh, confirmed) checks P1-P10 for leakage,
  exposure handling, hidden degrees of freedom, the budget and threshold
  arithmetic, and feasibility;
- MathReviewer (Fable xhigh, confirmed) checks Part M.
Fix every BLOCKING and SHOULD FIX item, then freeze the protocol with a
sha256. Do not register.

============================================================
SCOPE
============================================================

This stage does NOT:
- buy, quote or call Databento (no key is needed or used)
- register anything or append to ledger/trial_registrations.jsonl; N
  stays 838
- train, or compute any feature value, label, return or outcome
- read any sealed window, the embargo, or any data from 2024-03-01 on
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
GUARDRAILS
============================================================

Start and end checks, quoted verbatim:
- `git status --short` and `git log --oneline -3`;
- the holdout status and the test-seal guard dry check;
- `wc -c REGISTRATION.md`;
- the harness sha;
- the spend ledger line count and sha256;
- N (838);
- pytest at the end with the 2 GB rule, if Part 0 changed a guard.
Commits touch only this stage's files. Before ending, confirm no worker
or shell is still running.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0.1 seal check | lead | opus | max | first | sealing is reserved |
| 0.2 exposure audit | ExposureAuditor-OpusHigh (+ Haiku extraction helpers) | opus / haiku | high / medium | parallel | judgment over extracted facts |
| M1-M4 | MathReader-OpusHigh x 4 | opus | high | parallel | independent topics |
| Part F | DataFacts-SonnetHigh | sonnet | high | parallel | counts only |
| Part P | lead | opus | max | after M, F, 0.2 | reserved |
| MathReviewer, ProtocolReviewer | fable (confirmed) | fable | xhigh | before the freeze | independent check |
| Return | lead | opus | max | last | reserved |

    DELEGATION PLAN (the lead executes this; it does not do worker tasks)
    1. Decompose each part into subtasks with one objective, inputs, output
       path and format, allowed tools, and boundaries.
    2. Route per CLAUDE.md and V55. State model and effort for each
       subtask before spawning; confirm each reviewer's model from its
       transcript.
    3. Run independent workers at once (V37), at most 6 at a time.
    4. Collect results as files plus short summaries.
    5. Verify with the independent reviewers as listed.
    6. Synthesize in the lead against this prompt, and write the synthesis
       to disk before ending.
    7. Unattended run: no pauses to ask. Checkpoint to
       reports/stage_e34_STATE.md after each step.

============================================================
DELIVERABLE
============================================================

Write:
- reports/stage_e34_zl_methods.md;
- reports/stage_e34_exposure.md;
- reports/stage_e34_data_facts.md;
- reports/stage_e34_zl_protocol.md (frozen, with sha256);
- reports/E.34_RETURN.md;
- one progress.md entry;
- one docs/STAGES.md line;
- one final commit "Stage E.34 ZL program design and protocol". Do not
  push.

The return's fixed sections:
1. Summary, at most 300 words. Cover:
   - the exposure verdict;
   - MBO or MBP-1 for discovery;
   - the families and the search budget;
   - the minimum edge and power;
   - the honest prior after design;
   - what the run stage buys, and its estimated cost.
2. Guardrail evidence.
3. Results.
4. Delegation record, with each reviewer's confirmed model.
5. Verification.
6. Open choices.
7. Decisions for the user, each with a recommendation, including D2 and
   D3 of E.32b restated with this stage's facts.
8. Session cost, never estimated.

The last thing before ending: list every open choice in section 6.

END PROMPT
