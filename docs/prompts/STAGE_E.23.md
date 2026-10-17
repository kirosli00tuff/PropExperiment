STAGE E.23 "CHANGE THE HOLD, NOT THE RULE: THE PROGRAM'S INTRADAY TRIGGERS HELD FOR 5 AND 20 DAYS, MEASURED AS ALPHA OVER TREND"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: A new pre-registered hypothesis family in the multi-day track
(V40). Some of the program's intraday triggers might be the visible start
of a multi-day move. Each shortlisted trigger keeps its frozen definition
exactly; only the hold changes: entry at the trigger day's settlement,
exit at the settlement 5 or 20 trading days later. Because trend already
pays at multi-day holds (E.21), the measure is the alpha left after
regressing on the same root's trend returns, not raw P&L. Phases: an
inventory and mechanism memo with no outcome read; a frozen, Fable-reviewed
registration with power checks; one discovery read; one confirmation read
of the discovery survivors on owned data never used to select the trigger;
Fable recomputation; the return. Owned data only. No purchase.

Decisions in force: docs/DECISIONS.md V20 to V40. Binding: this prompt,
docs/STAGE_E_DESIGN.md D2, D4, D5, D8, D9, D13 where cited, and V37.

Lead: Opus 5.5, effort xhigh. Ultracode: on (launched interactively).

Why this lead and effort: the stage turns frozen intraday triggers into
multi-day books, where silent errors live in entry timing (re-counting the
trigger day's intraday P&L), overlapping holds, rolls, and the data-use map
that decides which window may confirm which trigger. Fable reviews the
registration before any outcome read and recomputes every verdict number.

Usage and time: the user cleared two five-hour usage windows starting about
02:00 PDT on 2026-10-17. The session may hit a usage limit between them;
reports/stage_e23_STATE.md is updated after every step so that a resume
starts from disk, and every outcome read sits behind a run-once marker so a
resume never repeats one. No outcome read (discovery or confirmation) starts
after 10:30 PDT; by 11:30 PDT the return is written with each phase's
status, finished or not; the session ends by 12:00 PDT.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the choice
under Open choices in the return document, and continue.

============================================================
PHASE 1: INVENTORY, MECHANISMS AND THE DATA-USE MAP (NO OUTCOME READ)
============================================================

P1.1 Inventory. List every intraday trigger the program has frozen: every
Tier A and Tier B member in reports/stage_e_k1..k8_member_freeze.json, the
E.20 H6 rule (reports/stage_e20_h6_freeze.json), and any frozen intraday
rule in the Stage C, D and E.14 to E.18 freezes. For each: id, root(s),
trigger definition (verbatim from the freeze), trigger direction, the
intraday hold it was tested with, every stage that read it and on which
window, and its verdict. Exclude, with the reason: ML models and E.20
search configurations (not frozen plain rules), H2 and H3 (already
multi-day; H2 is E.21 T4), and any rule whose trigger needs data not owned
for both windows below.

P1.2 Mechanism memo. For each inventoried trigger, a one-paragraph stated
reason it should (or should not) predict a move over the following 5 to 20
days, with the direction that reason predicts (continuation or reversal of
the trigger-day move), citing published work where it exists (limit-move
continuation and delayed price discovery, flight-to-safety persistence,
post-FOMC drift, rest-of-day momentum, flow effects, and any others the
readers find). A trigger whose only reason is intraday (a within-day
snap-back, a session-open imbalance) is dropped with that reason. The
direction is fixed here, by the mechanism, never by data.

P1.3 Shortlist: at most 12 triggers, chosen by the strength of the stated
mechanism and the expected trigger count (P2.3), written before any outcome
read. Two holds each (5 and 20 trading days): at most 24 trials.

P1.4 Data-use map. For each shortlisted trigger, from the returns,
freezes and run markers: which owned windows were used to select it
(screen, discovery) and which were used to confirm or test it. Then
declare per trigger:
- the discovery window: owned data, ideally the data the trigger was
  screened on (its intraday outcome is spent there, its multi-day outcome
  is not);
- the confirmation window: owned data that never selected the trigger at
  any stage, at the trigger's own intraday hold or otherwise (candidates:
  the ext2010/ext2010h stores 2010-06..2019-04 for the 17 roots with older
  history; the confirmation window S_X..2024-02-29 where screening used an
  earlier sample). A trigger with no owned confirmation window is
  "unconfirmable on owned data" and is not registered.
State plainly that E.21 read the daily series of 2010-07..2024-02 for the
17 roots, so the aggregate multi-day drift of these windows is known; the
alpha-over-trend measure (P2.2) is what guards against that.

============================================================
PHASE 2: THE FROZEN REGISTRATION (FIXED HERE; DETAILS IN THE FREEZE)
============================================================

P2.1 Book per trigger and hold h in {5, 20}:
- Entry at the settlement price of the trigger day (the session's
  settlement bar as the harness defines it), after the intraday move; the
  trigger day's own intraday P&L is never counted.
- Exit at the settlement h trading days later. Each trigger opens one unit
  in the mechanism's direction; the root's position on a day is the sum of
  active units, capped at +/-1 unit per root.
- Each unit sized to a constant risk: 1 / sigma, sigma the EWMA (centre of
  mass 60) daily return volatility known at entry, as E.21 T1 did.
- Costs at D8 for the root's micro (or the full-size contract where no
  micro exists) on every entry, exit and roll, plus the stress case at 2 x
  slippage. Rolls by the harness's front-contract rule; a hold spanning a
  roll pays the roll.
- Daily marked-to-settlement net returns.

P2.2 The measure. Regress each book's daily net returns on the same root's
E.21 T1 (TSMOM-12) and T2 (1/3/12 blend) daily returns over the same days
(reports/stage_e21_runs/per_root; recompute from the frozen E.21 code if a
series is missing, and state it). The alpha's t statistic uses Newey-West
lags equal to h. A trigger whose raw P&L is positive but whose alpha is
not is a null: it is trend, already known.

P2.3 Power check before any outcome read (D4 spirit). From trigger dates
only (computing a trigger reads intraday bars the screens already read;
forward returns stay unread): the count of non-overlapping events per
window and the power to reach the bar at a true net Sharpe of 0.5. A
trigger-hold with fewer than 30 non-overlapping events in a window, or
power below 0.2, is "inconclusive by design" for that window and is not
read there.

P2.4 Bars.
- Discovery screen: Holm across the registered family at one-sided alpha
  0.05 on the alpha t; survivors also need alpha t >= 2.0 and net Sharpe
  >= 0.3 (base costs). At most 4 survivors go to confirmation (the 4
  largest alpha t; ties by net Sharpe).
- Confirmation, once per survivor: Holm across the survivors at one-sided
  alpha 0.05 on the alpha t; then the composite: alpha t >= 2.0, net
  Sharpe >= 0.3 at base and > 0 at stress, DSR > 0.95 at the program N
  after registration, CSCV PBO < 0.5 on the discovery window.
- No outcome is read on the research window, holdout-2, the March 2024
  embargo, MES's sealed stores or anything dated 2024-03-01 or later.

P2.5 N. Every registered trigger-hold counts (at most 24): N 533 -> 533 +
the registered count, entered in ledger/trial_registrations.jsonl before
the discovery read. State the new N.

P2.6 Order. Inventory, memo, shortlist and data-use map written; freeze
written and hashed (sha256 manifest of the rules, windows, power table,
code); RegReviewer-FableXHigh review (BLOCKING and SHOULD FIX fixed
first); freeze commit; registration; discovery read once behind a run-once
marker; screen; confirmation read once behind a second marker; then
VerdictVerifier-FableXHigh recomputation. A BLOCKING finding on a verdict
is resolved by finding the code error, never by a second read.

============================================================
SCOPE
============================================================

This stage does Phases 1 and 2 and nothing else.

This stage does NOT:
- buy anything, call Databento, or fetch market data from the web
  (literature readers fetch papers and articles only, under V37's
  spacing rule, after reading each site's terms; CME's site is never
  fetched by automation)
- change any frozen member, rule, harness file or earlier freeze (a new
  harness version, if the books need one, is written, Fable-reviewed and
  committed before any outcome read, as E.22 did for v13)
- read holdout-2, the embargo, MES's sealed stores, the research window,
  or anything dated 2024-03-01 or later
- run any outcome read twice, or start one after 10:30 PDT
- fit any ML model
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
CONTEXT TO READ FIRST
============================================================

1. CLAUDE.md and docs/ORCHESTRATION.md.
2. docs/DECISIONS.md V24 to V40.
3. docs/STAGE_E_DESIGN.md D2, D4, D5, D8, D9, D13.
4. reports/E.21_RETURN.md, reports/stage_e21_prereg.md and the E.21 code
   (the trend series and the sizing this stage reuses).
5. reports/E.22_RETURN.md and reports/E.5_RETURN.md (run-once and
   verification precedent).
6. The cluster member freezes K1 to K8, the E.20 H6 freeze and the returns
   that tested them (for P1.1 and P1.4).

============================================================
GUARDRAILS
============================================================

- Harness v13 dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4
  verified at start and end (or the new version, if one is committed).
- Holdout status all_ok, 0 unlocks, at start and end; spend ledger
  unchanged.
- Start and end checks quoted verbatim in the return: `git status
  --short`, `git log --oneline -3`, the holdout status, `wc -c
  REGISTRATION.md`, the freeze verifications, the ledger line count and
  sha256, N, and `uv run pytest -q -p no:cacheprovider` (if free memory
  falls below 2 GB, stop the run and quote the last full run on identical
  code, as E.22 did).
- Compute at nice 10 after a free-memory check; at most 2 heavy workers.
- Before ending, confirm no worker or background shell is still running.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup | lead | opus | xhigh | first | gates the session |
| P1.1 inventory | InventoryReader-OpusHigh x up to 10 (one per cluster K1..K8, one for H6, one for C/D/E.14-E.18) | opus | high | all at once | independent file reads |
| P1.2 mechanisms | MechanismReader-OpusHigh x up to 12 (one per mechanism family, one shared brief) | opus | high | all at once, about 2 per web domain | literature per mechanism |
| P1.3-P1.4 shortlist, data-use map | lead | opus | xhigh | after the readers | reserved judgment |
| P2 books, power, freeze code | BookCoder-OpusXHigh | opus | xhigh | after P1.4 | entry timing, overlap, rolls, regressions |
| Registration review | RegReviewer-FableXHigh | fable | xhigh | after the freeze text | independent check before any read |
| Reads and verdicts | lead | opus | xhigh | serial, behind markers | verdicts reserved to the lead |
| Verification | VerdictVerifier-FableXHigh | fable | xhigh | after the confirmation | every verdict number recomputed |
| Return | lead | opus | xhigh | last | reserved to the lead |

    DELEGATION PLAN (the lead executes this; it does not do worker tasks)
    1. Decompose each task into subtasks with one objective, inputs, output
       path and format, allowed tools, and boundaries.
    2. Route per CLAUDE.md. State model and effort for each subtask before
       spawning.
    3. Run independent workers at once (V37); heavy compute at most 2.
    4. Collect results as files plus short summaries.
    5. Verify every number entering a verdict with an independent fable
       xhigh worker.
    6. Synthesize in the lead against this prompt, and write the synthesis
       to disk before ending.
    7. Unattended run: no pauses to ask. Checkpoint to
       reports/stage_e23_STATE.md after each task.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.23_RETURN.md, one progress.md entry, one docs/STAGES.md
line, and one final commit "Stage E.23 triggers at multi-day holds". No
push. Fixed sections:

1. Summary, at most 300 words: the shortlist and what was dropped and why;
   each trigger-hold's discovery result (alpha t, net Sharpe, raw vs
   alpha); each confirmation verdict (PASS, NULL, INCONCLUSIVE BY DESIGN,
   UNCONFIRMABLE ON OWNED DATA) with its decisive numbers; the new N; what
   the user must decide.
2. Guardrail evidence: start and end checks verbatim; the order of events.
3. Results: the inventory, the mechanism memo, the data-use map, the power
   table, discovery and confirmation tables (base and stress, raw and
   alpha, event counts).
4. Delegation record.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
