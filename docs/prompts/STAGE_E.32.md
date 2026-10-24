STAGE E.32 "ZM DIRECTIONAL SIGNAL DISCOVERY: THE METHODS BRIEF AND THE FROZEN DISCOVERY PROTOCOL"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: E.31 closed passive spread capture (V50). The user's thesis: any
capturable directional edge is most likely in a lesser-known product such
as ZM, on an unpublished idea the program finds itself, with ML as a core
tool. This stage is the first part of that program, discovery design:
- a deep methods brief (Parts R and M), on the model of E.28 Part C but
  aimed at short-horizon DIRECTIONAL signals in the soybean complex, and
  at how professional firms actually build, test and retire such
  strategies;
- a frozen discovery protocol (Part P): the labels, horizons, feature
  families, model families, cross-validation, search budget and selection
  rule that the next stage (E.33) will run, unchanged, on the owned ZM
  data.
Nothing is trained, no outcome is computed, and N stays 538. The only data
access allowed is format and size inspection of the owned files (Part F).
The one-shot test window, 2017-05 to 2020-11, is sealed by this stage
before any other work.

Decisions in force: docs/DECISIONS.md V20 to V51. Binding: this prompt,
V43 (ML as the strategy under pre-registration), V50 (trade-through
pricing, reviewer model check), V37.

Read first:
- reports/E.31_RETURN.md
- reports/stage_e31_pilot_spec.md
- reports/stage_e28_methods_brief.md (sections 1 and 4 and the verdict
  table; the rest by search, never the whole 1 MB at once)
- reports/stage_e28_ranking.md
- reports/E.29_RETURN.md section 1
- reports/stage_e31_inputs/planner_research_notes.md
- the E.23 inventory (reports/stage_e23_briefs/inventory/, K6.md for
  agriculture), so every idea is checked against the 538 trials

Lead: Opus 5.5, effort xhigh, Ultracode on (launched interactively on the
Max plan).
- Readers are Opus high, at most 6 at once.
- Reviews are Fable xhigh. Each reviewer's model is confirmed from its
  transcript (V50 item 5). If Fable is unavailable, or the transcript
  shows another model, use Opus 5.5 xhigh in a fresh context and say so.
  Never Sonnet.

Time: launch after the user moves to Max. Checkpoint
reports/stage_e32_STATE.md after every step, and resume from it after
any usage limit or reboot. The return is due within one working day of
launch.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the choice
under Open choices in the return document, and continue.

============================================================
PART 0: SEAL THE TEST WINDOW (FIRST, BEFORE ANY READING)
============================================================

The one-shot test for this hypothesis family is ZM, ZS and ZL data from
2017-05-01 to 2020-11-30. Write reports/stage_e32_test_seal.md to state:
- No stage may buy, download or open ZM, ZS or ZL data of any schema
  dated in that window, until a registered test stage reads it once.
- That covers the program's own one-minute bars too: list every owned
  ZM, ZS and ZL file that touches the window, with path and sha256, and
  apply the program's seal mechanism or an equivalent read-refusal guard.
  Show the holdout status before and after.
- Earlier stages' reads of ZM, ZS or ZL bars in that window: list them
  from the E.23 inventory and the ledgers. Name the exposure honestly. It
  was bar-level trend and seasonal work, not order-book features.
- 2024-03 onward stays closed (program embargo, and V48 gives no
  approval).

============================================================
PART R: HOW PROFESSIONALS BUILD SHORT-HORIZON DIRECTIONAL STRATEGIES
============================================================

Readers, each with one objective, an output file under
reports/stage_e32_briefs/, a source log and the E.28 reader rules
(reports/stage_e28_briefs/READER_RULES.md):

- R1 Alpha research process at proprietary trading firms and systematic
  funds:
  - how ideas are generated, screened, ranked and killed;
  - research-to-production pipelines;
  - how the multiple-testing problem is handled in practice (false
    discovery control, hold-out discipline, paper trading, staged
    capital);
  - signal decay and capacity;
  - how desks decide a small edge is worth running.
  Sources: practitioner books and talks (Lopez de Prado, Chan, Narang,
  Kissell, Isichenko "Quantitative Portfolio Management", Grinold-Kahn),
  firm engineering blogs, interviews, conference talks. Practitioner
  sources are labelled as such.
- R2 Commodity and agricultural trading desks:
  - how merchants (ADM, Bunge, Cargill-type), ag-focused prop shops and
    CTAs trade the soybean complex at short horizons;
  - what information they use: the board crush, basis, export and
    processing data, weather, South American crops, fund positioning
    (COT), USDA reports;
  - which edges they describe as structural.
- R3 Soybean complex economics relevant to minutes-to-hours horizons:
  - crush margin dynamics and the oil/meal share;
  - ZS, ZM and ZL cointegration;
  - spread trading and its mean reversion speed;
  - roll and delivery effects;
  - seasonality of liquidity;
  - the K algorithm and implied crush liquidity (what an aggressor sees
    versus what the feed shows).
- R4 Event structure:
  - USDA releases (WASDE, Crop Progress, Export Sales, NOPA crush, Grain
    Stocks, Acreage), their timing relative to the day session;
  - price discovery after them: drift or reversal, horizons, sizes;
  - daily limits and limit-expansion days;
  - weather-driven overnight gaps;
  - published evidence quantified per event type.

============================================================
PART M: THE MATHEMATICS AND ML FOR DIRECTIONAL SIGNALS
============================================================

Extend E.28's brief. Do not repeat it: cite its sections, and add only
what directional, minutes-scale prediction needs. Each topic gives:
- the equations;
- a worked example on ZM-sized numbers (tick 10 USD, a typical sigma);
- the data it needs;
- its leakage traps;
- a verdict (use, maybe, skip) with the reason.

- M1 Order-flow measures at aggregation horizons from 1 second to 30
  minutes:
  - multi-level OFI (Cont, Kukanov, Stoikov; Xu, Gould, Howison; Kolm,
    Turiel, Westray);
  - trade-sign imbalance and its long memory;
  - Kyle's lambda;
  - the microprice (Stoikov);
  - cancellation and replenishment rates;
  - detection of large orders being worked and icebergs from MBO;
  - VPIN, with its critiques.
- M2 Lead-lag and cross-asset structure for asynchronous data:
  - the Hayashi-Yoshida estimator, lead-lag via the Hoffmann, Rosenbaum
    and Yoshida contrast;
  - error-correction and OU models of the crush spread;
  - half-life estimation;
  - how to trade a dislocation in one leg.
- M3 Labels and sampling:
  - clock, event, volume and dollar bars;
  - fixed-horizon versus triple-barrier labels;
  - meta-labeling;
  - sample weights for overlapping labels (uniqueness);
  - the minimum predictable move set by costs: ZM's market-order
    break-even, about 1.6 ticks at Topstep (E.28), and the trade-through
    fill rule (V50).
- M4 Model families and their fit to about 39 months of one contract:
  - regularised linear and logistic models;
  - gradient-boosted trees;
  - small sequence models (DeepLOB-style CNN-LSTM, TCN, transformers),
    with the honest data-size verdict from E.28;
  - online and regime-switching models;
  - the compute each needs on the ThinkPad.
- M5 Validation and overfitting control:
  - purged and embargoed K-fold;
  - combinatorial purged CV;
  - walk-forward;
  - deflated Sharpe at the search's N;
  - PBO;
  - false discovery rate (Benjamini-Hochberg) versus Holm for a large
    search;
  - feature importance done safely (MDA and SFI on purged folds);
  - stability across months and regimes;
  - power analysis: the number of trades needed to detect the minimum
    edge at the test window's length.
- M6 From prediction to a prop-firm strategy:
  - converting a probability or forecast into entries, exits and holding
    time;
  - market versus limit execution under the trade-through rule;
  - the effect of each firm's daily loss limit, trailing drawdown,
    consistency and payout rules on which signals are usable (E.19's
    simulator, E.28's model, E.29's finding on micro payout thresholds);
  - news windows and position limits for ZM at each firm.

============================================================
PART F: DATA FACTS (FORMAT AND SIZE ONLY)
============================================================

From the owned files under /mnt/large-storage (E.31's 2020-12 to 2024-02
purchase) and the manifests, record:
- schemas, fields, timestamps (ts_event versus ts_recv) and their
  resolution;
- instrument ids across rolls;
- message counts per day;
- disk and memory needs for book reconstruction and features over 39
  months;
- the time to rebuild one day of MBO;
- E.31's existing book and markout code that can be reused.
No price, return, markout or feature value is computed or looked at.
Counts, sizes and schemas only.

============================================================
PART P: THE FROZEN DISCOVERY PROTOCOL (FOR E.33)
============================================================

Write reports/stage_e32_discovery_protocol.md, review it, and freeze it
with sha256 before the return. It fixes, before any outcome exists:

P1 Discovery data:
- the owned 2020-12 to 2024-02 ZM MBO and ZS and ZL MBP-1 files, as
  hashed;
- the day session as primary, the overnight session separate.
State E.31's prior exposure on these dates (passive markouts, including
splits by queue imbalance at entry), and how the protocol keeps it from
steering the choice of features.

P2 The idea families to search (at most 6), each with:
- its mechanism;
- the evidence or reasoning;
- its overlap with the 538 trials and E.31.
Candidates the lead weighs, among others:
- crush-spread dislocation and reversion;
- ZS and ZL leading ZM;
- minutes-scale order flow and worked orders;
- post-USDA drift or reversal;
- the overnight-to-day handoff;
- liquidity-state regimes.

P3 Labels and horizons:
- a fixed short list, for example 1, 5, 15 and 60 minutes, and a
  triple-barrier variant;
- the cost-aware target (net of the ZM market-order break-even and the
  trade-through penalty);
- event-time sampling rules.

P4 Features: per family, a fixed list of definitions with their exact
formulas, look-back windows and normalisations. Point-in-time only, with
leakage tests.

P5 Models: at most 3 families. For each:
- a hyperparameter grid that is fixed and finite;
- the compute estimate.

P6 Validation:
- purged and embargoed CV, with folds, purge and embargo widths fixed;
- the metric (net expected ticks per trade under each firm's fees and
  the trade-through rule, plus hit rate and turnover);
- stability requirements across months.

P7 The search budget: the exact number of configurations, family x
features x label x horizon x model x grid. Every one is counted into N
(V43) when E.33 runs it. The deflated-Sharpe and FDR thresholds at that
N are computed here.

P8 The selection rule: how at most 3 candidates are chosen for the
one-shot test, with:
- minimum edge after costs;
- minimum trade count;
- stability;
- no single month dominating;
- the power check for the 43-month test window.

P9 The test stage, as a sketch to register later:
- the 2017-05 to 2020-11 purchase (quote only, after a funded account
  exists);
- one read;
- the pass bar.

P10 Stop rules for E.33: what ends the search early, and what is reported
if nothing passes.

Review: ProtocolReviewer (Fable xhigh, model confirmed) checks P1 to P10
for:
- leakage;
- hidden degrees of freedom;
- the arithmetic of the budget and thresholds;
- feasibility on the ThinkPad.
A second reviewer, MathReviewer, checks Part M's equations and worked
examples, as E.28 did. Fix every BLOCKING and SHOULD FIX item before the
freeze.

============================================================
SCOPE
============================================================

This stage does NOT:
- train any model, compute any feature value, label, return, markout or
  outcome, or look at any price series
- open, buy or download any data dated 2017-05-01 to 2020-11-30, or
  2024-03-01 onward
- call Databento at all (there is no funded account; quotes come later)
- register anything; N stays 538
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

Source rules: as E.28. Read each site's terms before any automated
fetch. Never fetch CME's site or archived copies by automation. Blogs,
forums and videos are pointers only.

============================================================
GUARDRAILS
============================================================

Start and end checks, quoted verbatim:
- `git status --short` and `git log --oneline -3`;
- the holdout status, before and after Part 0;
- `wc -c REGISTRATION.md`;
- harness v14 2e908c81...;
- the spend ledger line count and sha256, and N;
- `uv run pytest -q -p no:cacheprovider` at the end, with the 2 GB
  memory rule, if Part 0 adds a guard.
Commits touch only this stage's files. Before ending, confirm no worker
or shell is still running.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup, Part 0 seal | lead | opus | xhigh | first | sealing is reserved |
| R1-R4 readers | SourceReader-OpusHigh x 4 (+ up to 4 follow-ups) | opus | high | at once | independent topics |
| M1-M6 readers | MathReader-OpusHigh x 6 | opus | high | at once, after Part 0 | independent topics |
| Part F | DataFacts-OpusHigh | opus | high | parallel | counts only |
| Brief synthesis | lead | opus | xhigh | after the readers | reserved |
| MathReviewer | fable (confirmed) | fable | xhigh | after the brief | independent check |
| Part P protocol | lead | opus | xhigh | after the brief | reserved |
| ProtocolReviewer | fable (confirmed) | fable | xhigh | before the freeze | independent check |
| Return | lead | opus | xhigh | last | reserved |

    DELEGATION PLAN (the lead executes this; it does not do worker tasks)
    1. Decompose each part into subtasks with one objective, inputs, output
       path and format, allowed tools, and boundaries.
    2. Route per CLAUDE.md. State model and effort for each subtask before
       spawning, and confirm each reviewer's model from its transcript.
    3. Run independent workers at once (V37), at most 6 at a time.
    4. Collect results as files plus short summaries.
    5. Verify with independent reviewers as listed.
    6. Synthesize in the lead against this prompt, and write the synthesis
       to disk before ending.
    7. Unattended run: no pauses to ask. Checkpoint to
       reports/stage_e32_STATE.md after each step.

============================================================
DELIVERABLE
============================================================

Write:
- reports/stage_e32_methods_brief.md (Parts R and M, with a one-page
  front);
- reports/stage_e32_test_seal.md;
- reports/stage_e32_data_facts.md;
- reports/stage_e32_discovery_protocol.md (frozen, with sha256);
- reports/E.32_RETURN.md;
- one progress.md entry;
- one docs/STAGES.md line;
- one final commit "Stage E.32 ZM discovery brief and protocol". Do not
  push.

The return's fixed sections:
1. Summary, at most 300 words. Cover:
   - the families chosen and why;
   - the search budget and N after E.33;
   - the minimum edge per trade the search must find;
   - the power of the 43-month test;
   - the honest odds.
2. Guardrail evidence.
3. Results.
4. Delegation record, with each reviewer's confirmed model.
5. Verification.
6. Open choices.
7. Decisions for the user, each with a recommendation. Include E.33's
   compute and usage estimate, and the test-data quote plan.
8. Session cost, per CLAUDE.md, never estimated.

The last thing before ending: list every open choice in section 6.

END PROMPT
