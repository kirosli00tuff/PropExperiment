STAGE E.36 "ZL DISCOVERY SEARCH: AMEND, REGISTER, BUILD, RUN, SELECT (NO PURCHASE)"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: the run stage of the ZL program. E.34 froze the discovery
protocol (reports/stage_e34_zl_protocol.md, v1.0). The user accepted
E.34's recommendations (V58):
- ZL's single sealed read goes to this program (E.32b-D2);
- discovery is judged by the power rule, not V31's cost gate (E.32b-D3);
- the test DSR uses V = 1/(T_test - 1) (E.32-D2 amended);
- all 200 configurations run as ML (OC-5 option A).
This stage:
- writes protocol v1.1 (v1.0 plus the P9.4 amendment and the decision
  status lines, nothing else) and hashes it;
- builds the ZL pipeline twice from the protocol text, proves it on
  synthetic data, and freezes it;
- registers all 200 configurations (N 838 -> 1038) before any real
  outcome is read;
- runs the search on owned data, 2020-12-01..2024-02-29;
- applies P8 selection, the statistics and the independent
  recomputation;
- then either writes the null report (K1), or hashes the test list,
  runs K2, and writes the test purchase request for the user.
It buys nothing, quotes nothing and calls no Databento endpoint. The
stage ends at the first point where data credits would be needed.

The user's standing instruction: be extremely careful with the
mathematics and the ML implementation. A false discovery would spend
ZL's one sealed window, and a leak would make every number worthless.
Never sacrifice quality to save usage.

Decisions in force: docs/DECISIONS.md V20 to V58. Binding, in this
order:
- protocol v1.1, once hashed (v1.0 sha256 checked at start; the stage
  refuses to run if v1.0 differs from reports/stage_e34_zl_protocol.sha256);
- this prompt;
- V43, V50, V51, V55, V56, V58;
- docs/prompts/STAGE_E.33.md for the parts this prompt cites (its gates,
  Parts B to E and their rules), read with the protocol's 0.4 mirror
  substitutions.
Where this prompt and the protocol disagree, the protocol wins, except
that this prompt forbids any Databento call.

Read first:
- reports/E.34_RETURN.md (all of it)
- reports/stage_e34_zl_protocol.md (all of it)
- reports/stage_e34_zl_methods.md (the lead front and errata; the rest by
  search)
- reports/stage_e34_data_facts.md
- reports/stage_e34_exposure.md (the firewall rules)
- reports/stage_e34_briefs/P10_compute_ref.md
- reports/stage_e34_briefs/L_lead_reconciliations.md
- docs/prompts/STAGE_E.33.md
- reports/E.33c_RETURN.md and reports/E.33_RETURN.md section 3
- E.33's frozen pipeline: reports/stage_e33_pipeline_freeze.sha256 and
  the code under reports/stage_e33_briefs/work/pipeline/
- reports/stage_e32_test_seal.md

Lead: Opus 5.5, effort max. Ultracode only if the lead judges it
necessary. Routing per V55:
- Reviewers: Fable xhigh, model confirmed from the transcript (V50 item
  5). If Fable is unavailable or the transcript shows another model, use
  Opus 5.5 max in a fresh context and say so. Never Sonnet for a review.
- Extraction and file parsing: Haiku.
- Low-to-mid tasks (counts, manifests, file checks): Sonnet.
- Coding, statistics and everything else: Opus.
- Worker effort from medium to max, set by the task.
- At most 6 workers at once. At most 2 heavy compute jobs at once. Stop
  a job if free memory falls below 2 GB (the ThinkPad has 14 GB).

Time: launched about 17:00 PDT on 2026-10-29, with no fixed end. It
continues across usage-limit pauses and reboots.
- Checkpoint reports/stage_e36_STATE.md after every step and resume from
  it.
- Long jobs are restartable per trade date and per configuration, with
  DONE markers.
- When the lead's context passes about 300k tokens at a quiet point (no
  worker or job running), write RESUME HERE (what is done, what is next,
  the exact continuation command) and "READY FOR WIPE <time>", then
  stop. An hourly watcher restarts a fresh lead.
- A search job may keep running through a wipe only if it is a
  detached, restartable script that writes DONE markers; the fresh lead
  checks it from disk.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the
choice under Open choices in the return, and continue. A choice the
protocol does not cover is decided in the most conservative way and
logged in reports/stage_e36_protocol_readings.md (protocol 0.2). The
protocol is never changed except by the amendment in S2. If it cannot be
run as written, stop that part and report.

============================================================
PART S: START GATES AND THE AMENDMENT
============================================================

S1 Verify, quoted verbatim:
- the sha256 of protocol v1.0 and of every file in
  reports/stage_e34_zl_protocol.sha256 (P10.4);
- the test seal: the holdout status, 114/114 files sealed, and the read
  guard refusing a 2017-05..2020-11 ZL, ZS and ZM file in a dry check;
- harness v14 and E.33's pipeline freeze list;
- the discovery data files (ZL MBP-1, the three roots' ohlcv-1m, the ZL
  definitions, 2020-12..2024-02) against their manifests (P1.1);
- N = 838 and the ledger line counts;
- that no Databento call is possible from this stage's code paths: the
  stage never imports or calls the Databento client. Check
  DATABENTO_API_KEY4 by variable name only, and record "present" or
  "absent". Never print a key.

S2 The amendment, protocol v1.1:
- v1.1 is v1.0 with only these changes:
  (a) P9.4 and P9.3 check (1): at the test, the program DSR uses
      V = 1/(T_test - 1), as V58 item 3 and E.34 P9.4 state. Holm at
      K = 9, the daily t > 3.0, CSCV PBO < 0.5 and check (2) are
      unchanged. The amended check can never fall below check (2);
  (b) the header's status lines record the four decisions as V58
      (E.32b-D2 yes, E.32b-D3 yes for this program, E.32-D2 amended,
      OC-5 option A, as written);
  (c) the version line and date.
- Produce reports/stage_e36_briefs/protocol_v1.1.diff showing nothing
  else changed.
- AmendReviewer (Fable xhigh, confirmed, or Opus max fresh) checks that
  the diff touches only (a) to (c), that P7.2's discovery thresholds are
  unchanged, and that no outcome was read to make it.
- Hash v1.1. Write reports/stage_e36_zl_protocol_v1.1.sha256. From here
  on v1.1 binds.
- Do not change screening/stage_e_verdict.py in this stage. The amended
  check binds the later test stage's verdict call; the test stage
  implements and tests it before the read.

S3 Firewall: apply the 10 rules of reports/stage_e34_exposure.md and
P1.5 to every loader and worker brief. No worker opens an E.31 or E.33
outcome file, markout, OOF prediction or result table for ZL, ZS or ZM.

============================================================
PART B: BUILD THE PIPELINE TWICE, PROVE IT, THEN FREEZE IT
============================================================

As STAGE_E.33.md Part B, with the protocol's P1 to P6 as the text to
implement. Reuse E.33's frozen modules where the protocol says "as
E.32" and the mirror rule leaves the code unchanged (CV, purge and
embargo, model grid, DSR, PBO, BH, Holm). Record every reused file with
its E.33 sha256. New code covers at least:
- the ZL MBP-1 loader and book state, F10 (12 features, P4), including
  F10.7 and F10.9 exactly as written;
- F09c (8 features) and F09p (9 features) with ZL as the adjusting leg,
  and the bar timing rule B;
- the C context block (14 features);
- the ZL labels (FH15, FH30, FH60, TB15, TB30), the executable prices,
  the trade rule, the exclusion rules and the sample weights (P3);
- the realised trade simulation at Topstep, market, L = 1 s (P3.8),
  with ZL's tick (USD 6.00 a tick, 0.01 cents) and Topstep's ZL round
  trip from E.28's fee file;
- the America/Chicago decision grid (LT13).

B1 Coder-A implements from the protocol text.
B2 Coder-B, in a fresh context that never sees Coder-A's code,
   implements the same definitions in a different style.
B3 Agreement on 20 discovery dates chosen by seed 20261029 (feature and
   label values only; no model, no P&L): every value within the stated
   tolerance (protocol G7 where named); each disagreement traced and
   fixed in the wrong implementation; any ambiguity resolved in the most
   conservative way and logged in the readings file.
B4 Every test of P4.1: LT1 to LT13, and DC1 to DC5 as counts. Plus
   STAGE_E.33.md B4 (iv): a deliberately leaked feature must be caught
   and give an absurd CV score. All must pass before any model is fitted
   on a real outcome.
B5 P4.2's synthetic proofs: the null run (the false-positive rate of P8
   at N 1038 at or below the protocol's rate, else stop and report), the
   planted signals in F09c, F09p and F10, and the published worked
   examples for CV, DSR, BH and PBO to the stated digits.
B6 Cost model: re-derive Topstep's ZL net ticks from E.28's fee file;
   test it on hand-built trades with known answers.
B7 Review before the freeze:
   - PipelineReviewer (Fable xhigh, confirmed) reads B1 to B6 with the
     code and evidence, and returns GO or NO GO;
   - MathReviewer (Fable xhigh, confirmed) recomputes 10 feature values
     (at least 4 from F10, from raw MBP-1 records) and 10 labels by hand
     on dates of its own choice, plus the B5 threshold arithmetic.
   Fix every BLOCKING and SHOULD FIX item and re-check. Write the
   readings file and hash it. Freeze the pipeline:
   reports/stage_e36_pipeline_freeze.sha256 (every code file, config,
   the readings file and uv.lock). From here the pipeline does not
   change. A bug found later is fixed only by a logged amendment, with
   every affected configuration re-run and counted.

============================================================
PART C: REGISTER, THEN RUN THE SEARCH
============================================================

C1 Registration, exactly as P7.1:
- one screening.trial_registry.register call for all 200 configurations,
  before any real-outcome fit; IDs as P7.1 with the test name E36;
- each record carries set, label, h, model, hyperparameters, the
  pipeline sha256, the protocol v1.1 sha256 and the readings file
  sha256;
- quote N before (838) and after (1038);
- recompute P7.2 at the registry's N with the functions P7.1 names, and
  pin b_test unrounded;
- write reports/stage_e36_run_marker.md (run-once).

C2 Compute stop: before the first real-outcome fit, log the process
counts. If they differ from P10.3's (8 LOGIT, 2 LGBM), recompute R_ZL
with the frozen formula of P10_compute_ref.md section 3. The stop is
3 x R_ZL of measured search wall time (23,895 s at the reference
counts). Write your own projection from the first measured folds to the
STATE file beside the reference; the reference does not move. If the
stop fires, cut whole sets in P7.1's run order and report; do not
amend.

C3 Run all 200 configurations in P7.1's run order, under P6's CV:
- no early pruning except P10's stop rules;
- raw OOF predictions, labels and trade lists per configuration to disk
  under /mnt/large-storage/market_data/PropExperiment/derived/e36/, with
  a manifest;
- seeds logged; a configuration that errors is counted and recorded as
  failed with its error, as P5's failed-fit rule says;
- no result of any finished configuration is opened before all 200 are
  done.

============================================================
PART D: SELECTION AND STATISTICS
============================================================

As STAGE_E.33.md Part D, with P6 and P8 of the protocol:
D1 P8 on all 200: G1 to G5, the ranking, Tier A (at most 3,
   correlation <= 0.70) and Tier B (2). The BH report at q = 0.10 (never
   a gate). The discovery PBO.
D2 Robustness of any Tier A configuration, without re-selecting: by
   year, by session segment, release days versus other days, roll phase
   and volatility tercile. P6.4's execution variants and Topstep 50K
   prop-account simulation, and P6.5's diagnostics including the VECM
   report, only after the test list is hashed (E1 below).
D3 The distribution of all 200 OOF daily Sharpes beside B5's null and
   SR0 at N 1038.
D4 VerifyWorker (Fable xhigh, confirmed, or Opus max fresh): from the
   saved OOF predictions, labels and trade lists alone, recompute every
   number in the selection table and the Tier A and Tier B decision.
D5 StatsReviewer (Fable xhigh, confirmed) checks D1 to D4 and the
   honesty of the language. Fix BLOCKING and SHOULD FIX items.

============================================================
PART E: K1, K2, AND THE STOP BEFORE CREDITS
============================================================

If Tier A is empty (K1):
- write P10.5's null report, ending with the sentence "No candidate; the
  test window stays sealed; no test data purchase.";
- per E.32b section 6, state that the directional program stops, and
  that a restart needs a new information source the program has not
  used.

If Tier A is not empty:
E1 Write reports/stage_e36_finalists.md as P8's last bullet states (IDs,
   tiers, the 6 fold models of each with sha256, the pipeline sha256
   list, the P9 calendar procedure) and hash it, before any P6.4 or P6.5
   computation. Then run D2's deferred parts.
E2 K2 (P10.2): for each Tier A configuration, e80_test(c) =
   SR80_test(N_reg, T_test) x SD(X_D,c) / nbar_c on its OOF dates, with
   T_test 870. Stop if no Tier A configuration has OOF mean net per
   trade >= e80_test(c). Report the fixed figures beside it.
E3 If K2 passes, write reports/stage_e36_test_purchase_request.md for
   the user, and stop there:
   - the three items of P9.2 (ZL.v.0 MBP-1 from 2017-05-21 to
     2020-11-30; ZL definitions for the same span; ZM.v.0 ohlcv-1m
     2017-05-01..2019-04-30), each with dataset, schema, symbols,
     stype, start and end exactly as a quote call would use them;
   - E.34's estimates (USD 23.36, about 1.66, about 1.46; about 26.5 in
     all, 27.3 at the dearest months), marked as estimates, not quotes;
   - the preconditions: a funded account slot DATABENTO_API_KEY4 in
     .env (the user adds it), a logged quote, and the user's approval
     of the quoted spend;
   - what the test stage then does: the purchase under the seal guard,
     the metadata check of ts_recv, the release calendar build (P9.2),
     the amended verdict code with its tests, and the one read (P9.3).
   Do not quote, buy, download or open any test-window data.

============================================================
SCOPE
============================================================

This stage does NOT:
- call Databento in any way (no quote, no metadata call, no purchase,
  no download), whatever the key status
- open any data dated 2017-05-01 to 2020-11-30 or 2024-03-01 onward,
  or any E.31 or E.33 outcome file (S3)
- change protocol v1.1 after its hash, or the pipeline after its freeze,
  except by a logged amendment with every affected configuration re-run
  and counted
- change screening/stage_e_verdict.py
- trade, connect to any broker or firm, or touch live/, ops/, any
  TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
GUARDRAILS
============================================================

Start and end checks, quoted verbatim:
- `git status --short` and `git log --oneline -3`;
- the holdout status and the test-seal guard dry check (114/114);
- `wc -c REGISTRATION.md`;
- the harness sha;
- the spend ledger line count and sha256 (unchanged at the end);
- N before and after registration (838 -> 1038);
- the protocol v1.0 and v1.1 sha256 and the pipeline freeze sha256;
- DATABENTO_API_KEY4 present or absent, by name only;
- `uv run pytest -q -p no:cacheprovider` at the end, with the 2 GB rule.
  The known failing test
  tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha
  is reported, not fixed.
Commits touch only this stage's files and the trial registrations.
Large outputs go under
/mnt/large-storage/market_data/PropExperiment/derived/e36/ with a
manifest, never into git. Before ending, confirm no worker, job or shell
is still running.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| S1 gates, S2 amendment | lead | opus | max | first | reserved |
| S2 AmendReviewer | fable (confirmed) | fable | xhigh | after the diff | independent check |
| Manifest and hash checks | DataCheck-SonnetMedium | sonnet | medium | parallel with S2 | counts and hashes |
| B1 Coder-A | FeatureCoder-OpusMax | opus | max | parallel with B2 | exact implementation |
| B2 Coder-B | FeatureCoder2-OpusMax | opus | max | parallel with B1, isolated | independent implementation |
| B3-B6 tests, proofs, cost model | TestCoder-OpusXHigh x 2 | opus | xhigh | after B1, B2 | proofs before outcomes |
| DC1-DC5 counts | DataCounts-SonnetHigh | sonnet | high | after B1 | counts only |
| B7 PipelineReviewer, MathReviewer | fable (confirmed) | fable | xhigh | before the freeze | independent check |
| C registration | lead | opus | max | serial | reserved |
| C3 search jobs | lead-run scripts | - | - | at most 2 heavy jobs | compute |
| Log and DONE-marker parsing | LogParse-Haiku | haiku | medium | during C3 | extraction |
| D1-D3 | StatsCoder-OpusMax | opus | max | after C | exact statistics |
| D4 VerifyWorker | fable (confirmed) | fable | xhigh | fresh context | independent recomputation |
| D5 StatsReviewer | fable (confirmed) | fable | xhigh | after D4 | independent check |
| E, return | lead | opus | max | last | reserved |

    DELEGATION PLAN (the lead executes this; it does not do worker tasks)
    1. Decompose each part into subtasks with one objective, inputs, output
       path and format, allowed tools, and boundaries.
    2. Route per CLAUDE.md and V55. State model and effort for each
       subtask before spawning; confirm each reviewer's model from its
       transcript.
    3. Run independent workers at once (V37), at most 6 at a time.
    4. Collect results as files plus short summaries.
    5. Verify with independent workers and reviewers as listed.
    6. Synthesize in the lead against this prompt, and write the synthesis
       to disk before ending.
    7. Unattended run: no pauses to ask. Checkpoint to
       reports/stage_e36_STATE.md after each step.

============================================================
DELIVERABLE
============================================================

Write:
- reports/stage_e34_zl_protocol_v1.1.md (or the protocol file updated in
  place with v1.0 kept as reports/stage_e34_zl_protocol_v1.0.md; the
  lead logs which), the diff and the v1.1 sha256;
- reports/stage_e36_protocol_readings.md (hashed);
- reports/stage_e36_pipeline_freeze.sha256;
- reports/stage_e36_selection.md (the selection table, the
  distribution, the statistics);
- reports/stage_e36_finalists.md and
  reports/stage_e36_test_purchase_request.md, or the null report;
- reports/E.36_RETURN.md;
- one progress.md entry and one docs/STAGES.md line;
- one final commit "Stage E.36 ZL discovery search". Do not push.

The return's fixed sections:
1. Summary, at most 300 words. Cover:
   - N before and after;
   - the configurations run, and any cut;
   - the null comparison;
   - Tier A or the clean negative, with each Tier A configuration's net
     ticks per trade and trades a date at Topstep;
   - K2's result;
   - what the test stage would buy, at what estimated cost, and what
     the user must do first (KEY4, quote approval).
2. Guardrail evidence.
3. Results: S2's diff review, B3 agreement, B4 tests, B5 proofs, the
   search distribution, the selection table, robustness, K1 and K2.
4. Delegation record, with each reviewer's confirmed model.
5. Verification.
6. Open choices.
7. Decisions for the user, each with a recommendation.
8. Session cost, per CLAUDE.md, from the transcripts, never estimated.

The last thing before ending: list every open choice in section 6.

END PROMPT
