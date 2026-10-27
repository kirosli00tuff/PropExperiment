STAGE E.33 "ZM DIRECTIONAL SIGNAL DISCOVERY: RUN THE FROZEN PROTOCOL"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Part 2 of the ZM directional program (V51). Stage E.32 froze the
discovery protocol (reports/stage_e32_discovery_protocol.md). This stage
runs it unchanged on the owned discovery data: ZM MBO plus ZS and ZL MBP-1,
2020-12 to 2024-02. The user's instruction is to be extremely careful with
the mathematics and the ML implementation. A false discovery here would
cost the one clean test window, and a leak would make every number
worthless. So the stage builds everything twice where it matters, proves
the pipeline on synthetic data with known answers before it touches real
outcomes, registers every configuration before it runs, and has each step
checked by an independent reviewer. It returns at most 3 frozen finalists
for the one-shot test (a later stage), or a clean negative.

Decisions in force: docs/DECISIONS.md V20 to V51 and any V-entry E.32
adds. Binding, in this order: the frozen protocol (its sha256 is checked
at start, and the stage refuses to run if it differs), this prompt, V43,
V50, V37.

Read first:
- reports/E.32_RETURN.md (all of it)
- reports/stage_e32_discovery_protocol.md (all of it)
- reports/stage_e32_test_seal.md
- reports/stage_e32_data_facts.md
- reports/stage_e32_methods_brief.md (the front, then sections by search)
- reports/E.31_RETURN.md
- E.31's verified MBO book and K-algorithm code under
  reports/stage_e31_briefs/work/pilot/

Lead: Opus 5.5, effort xhigh, Ultracode on (launched interactively on
Max).
- Coders: Opus xhigh.
- Reviewers: Fable xhigh, each model confirmed from its transcript (V50
  item 5). If Fable is unavailable or the transcript shows another
  model, use Opus 5.5 xhigh in a fresh context and say so. Never Sonnet.
- At most 6 workers at once. At most 2 heavy compute jobs at once. Stop
  a job if free memory falls below 2 GB (the ThinkPad has 14 GB).

Time: launched after E.32's return is reviewed, on 2026-10-27. There is
no fixed end time: work continues until the stage is complete, across
usage-limit pauses and the weekly reset at 02:00 PDT on 2026-10-28 (user,
2026-10-27 08:12). Do not cut scope for time; quality comes first.
Checkpoint reports/stage_e33_STATE.md after every step, and resume from it
after any usage limit or reboot. Long jobs are restartable per trade date,
with a DONE marker per date.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the choice
under Open choices in the return document, and continue. A choice the
protocol does not cover is decided in the most conservative way and
logged. The protocol is never changed. If it cannot be run as written,
stop that part and report.

============================================================
PART A: START GATES
============================================================

A1 Verify all of these, quoted verbatim:
- the protocol's sha256;
- the test seal: the holdout status, and that the read-refusal guard
  rejects a test-window file in a dry check;
- harness v14 (or the version E.32 recorded);
- the hashes of the discovery data files against their manifests.
A2 No Databento call of any kind in this stage, even if a key is
present.

============================================================
PART B: BUILD THE PIPELINE TWICE, PROVE IT, THEN FREEZE IT
============================================================

B1 Feature and label code (Coder-A): implement every feature, label,
sample weight and sampling rule exactly as the protocol writes it, with:
- point-in-time computation only;
- ts_recv/ts_event handling exactly as the data facts state;
- rolls and session boundaries handled explicitly.

B2 An independent second implementation (Coder-B, fresh context, who
never sees Coder-A's code). From the protocol text alone, it implements
the same definitions in a different style (for example event loop
versus vectorised).

B3 Agreement on 20 discovery dates chosen by a fixed seed (feature and
label values only; no model and no P&L):
- every feature and label agrees within a stated tolerance;
- each disagreement is traced to a cause and fixed in the wrong
  implementation;
- if the protocol text was ambiguous, the most conservative reading is
  chosen and logged.

B4 Leakage tests, which must pass before any model is fitted:
- (i) a future-shift test: features recomputed with all inputs after
  time t removed must equal the originals;
- (ii) a label-boundary test: no feature window overlaps its own label
  window;
- (iii) purge and embargo widths checked against the longest label
  horizon;
- (iv) a test that a deliberately leaked feature (the label itself,
  lagged by minus one step) is caught by these tests and gives an
  absurd CV score.

B5 Synthetic proofs (no real outcomes):
- (i) Null: run the full search pipeline on synthetic order flow with
  no signal, built with the same tick size, volatility and event rates
  as the data facts. Report the distribution of the best configuration's
  CV metric, and the false-positive rate of the selection rule P8 at the
  search's N. It must be at or below the protocol's stated rate; if not,
  stop and report.
- (ii) Planted signal: plant one known signal of the protocol's minimum
  size in one feature family, and show the pipeline finds it with the
  stated power.
- (iii) The CV, deflated Sharpe, FDR and PBO code reproduces published
  worked examples (Lopez de Prado, Bailey and Lopez de Prado, Benjamini
  and Hochberg) to the stated digits.

B6 Cost and fill model:
- re-derive ZM's per-firm net-ticks metric from E.28's fee file and the
  trade-through rule (V50);
- test it on hand-built trades with known answers;
- it must match E.31's per-fill accounting where the two overlap.

B7 Review:
- PipelineReviewer (fable xhigh, model confirmed) reads B1 to B6, with
  the code and the evidence, and returns GO or NO GO;
- MathReviewer recomputes 10 feature values and 10 labels by hand from
  raw MBO messages on dates of its own choice, plus the B5 threshold
  arithmetic.
Fix every BLOCKING and SHOULD FIX item and re-check. Then freeze the
pipeline: a sha256 list of every code file, config and environment lock
(uv.lock). From here on the pipeline does not change. A bug found later
is fixed only by a logged amendment, with every affected configuration
re-run and counted.

============================================================
PART C: REGISTER, THEN RUN THE SEARCH
============================================================

C1 Before any real-outcome fit:
- write every configuration in the protocol's search budget (P7) to
  ledger/trial_registrations.jsonl, with its id, family, feature set,
  label, horizon, model, hyperparameters, the pipeline sha256 and the
  protocol sha256;
- N rises by exactly the budget. Quote N before and after.
- write reports/stage_e33_run_marker.md (run-once).

C2 Run the full budget on the discovery data under the protocol's CV:
- keep every result, with no early pruning except the protocol's stop
  rules (P10);
- write raw out-of-fold predictions per configuration to disk, so every
  later number can be recomputed;
- log the seeds;
- a configuration that errors is counted, and recorded as failed with
  the error.

C3 Monitor memory and time. Order the runs by family, so that a cut
still leaves complete families. If a usage limit or reboot interrupts
the search, resume it from the per-configuration DONE markers. Every
registered configuration is run.

============================================================
PART D: SELECTION AND STATISTICS
============================================================

D1 Apply the selection rule P8 exactly:
- net expected ticks per trade after costs for each firm under the
  trade-through rule;
- trade counts;
- the deflated Sharpe at the full N;
- FDR (and Holm, for reference);
- PBO via CSCV;
- stability across months and sessions;
- no single month dominating.

D2 Robustness of each candidate that passes D1, without re-selecting:
- the result by year, by session, around USDA days versus other days,
  by roll phase and by volatility regime;
- the result with the K-algorithm and FIFO fill models, for reference.

D3 Report the whole distribution, not only the winners: a histogram of
the metric across all configurations, beside B5's null distribution.

D4 Independent recomputation (VerifyWorker, opus xhigh, fresh context):
from the saved raw predictions and labels alone, recompute every number
in the finalists' rows and the selection decision.

D5 StatsReviewer (fable xhigh, model confirmed) checks D1 to D4 and the
honesty of the language. BLOCKING and SHOULD FIX items are fixed.

============================================================
PART E: FREEZE THE FINALISTS FOR THE ONE-SHOT TEST
============================================================

If at least one candidate passes, then for each of at most 3 finalists
freeze:
- the trained model, or its exact retraining recipe on all discovery
  data;
- the decision rule (probability or forecast to entries, exits, holding
  time, sizing at one contract);
- the execution (market, or limit priced under the trade-through rule);
- the firm and plan it is meant for;
- the expected net ticks per trade and the trade rate.
Hash everything into reports/stage_e33_finalists.md.

Then draft the test registration for a later stage, E.34. It sets:
- the 2017-05-01 to 2020-11-30 window;
- the exact files to buy (ZM MBO and ZS and ZL MBP-1, or less if the
  finalists need less);
- one read;
- the pass bar from P9, with Holm across the finalists;
- the power at the 43-month window;
- the cost plan: a quote from the new Databento account, to be taken by
  E.34, not here.

If nothing passes, write the clean negative: what was searched, the
null comparison, and the program's next options. No finalist is
promoted on a near miss.

============================================================
SCOPE
============================================================

This stage does NOT:
- open, buy, download or quote any data dated 2017-05-01 to
  2020-11-30, or 2024-03-01 onward
- call Databento, whatever the key status
- change the frozen protocol, or the pipeline after its freeze, except
  by a logged amendment with every affected configuration re-run and
  counted
- trade, connect to any broker or firm, or touch live/, ops/, any
  TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
GUARDRAILS
============================================================

Start and end checks, quoted verbatim:
- `git status --short` and `git log --oneline -3`;
- the holdout status;
- the test-seal guard dry check;
- `wc -c REGISTRATION.md`;
- the harness;
- the spend ledger line count and sha256 (unchanged);
- N before and after registration;
- the protocol sha256 and the frozen pipeline sha256;
- `uv run pytest -q -p no:cacheprovider` at the end, with the 2 GB
  rule.
Commits touch only this stage's files, plus the trial registrations. Large
outputs (predictions, features) go under
/mnt/large-storage/market_data/PropExperiment/derived/e33/ with a manifest,
never into git. Before ending, confirm no worker, job or shell is still
running.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| A gates | lead | opus | xhigh | first | reserved |
| B1 Coder-A | FeatureCoder-OpusXHigh | opus | xhigh | parallel with B2 | exact implementation |
| B2 Coder-B | FeatureCoder2-OpusXHigh | opus | xhigh | parallel with B1, isolated | independent implementation |
| B3-B6 tests, synthetic proofs, cost model | TestCoder-OpusXHigh x 2 | opus | xhigh | after B1, B2 | proofs before outcomes |
| B7 PipelineReviewer, MathReviewer | fable (confirmed) | fable | xhigh | before the freeze | independent check |
| C registration | lead | opus | xhigh | serial | reserved |
| C2 search jobs | lead-run scripts | - | - | at most 2 heavy jobs | compute |
| D1-D3 | StatsCoder-OpusXHigh | opus | xhigh | after C | exact statistics |
| D4 VerifyWorker | opus | opus | xhigh | fresh context | independent recomputation |
| D5 StatsReviewer | fable (confirmed) | fable | xhigh | after D4 | independent check |
| E, return | lead | opus | xhigh | last | reserved |

    DELEGATION PLAN (the lead executes this; it does not do worker tasks)
    1. Decompose each part into subtasks with one objective, inputs, output
       path and format, allowed tools, and boundaries.
    2. Route per CLAUDE.md. State model and effort for each subtask before
       spawning, and confirm each reviewer's model from its transcript.
    3. Run independent workers at once (V37), at most 6 at a time.
    4. Collect results as files plus short summaries.
    5. Verify with independent workers and reviewers as listed.
    6. Synthesize in the lead against this prompt, and write the synthesis
       to disk before ending.
    7. Unattended run: no pauses to ask. Checkpoint to
       reports/stage_e33_STATE.md after each step.

============================================================
DELIVERABLE
============================================================

Write reports/E.33_RETURN.md, one progress.md entry, one docs/STAGES.md
line, and one final commit "Stage E.33 ZM discovery search". Do not push.

Fixed sections:
1. Summary, at most 300 words. Cover:
   - N before and after;
   - the configurations run;
   - the null comparison;
   - the finalists or the clean negative;
   - each finalist's net ticks per trade and trade rate per firm;
   - what E.34 would buy and test.
2. Guardrail evidence.
3. Results: B3 agreement, B4 leakage tests, B5 synthetic proofs, the
   search distribution, the selection table, robustness and the
   finalists.
4. Delegation record, with each reviewer's confirmed model.
5. Verification.
6. Open choices.
7. Decisions for the user, each with a recommendation.
8. Session cost, per CLAUDE.md, never estimated.

The last thing before ending: list every open choice in section 6.

END PROMPT
