STAGE E.16 "BASE-RULE BATCH, PART A: BUILD AND FREEZE FIVE FORCED-FLOW TESTS ON A 2010-2024 WINDOW (SETTLEMENT-WINDOW MOMENTUM, MONTH-END REBALANCING PAIR, TREASURY AUCTION CYCLE, NEXT-DAY REVERSAL, AND THEIR COMBINATION); NO DATABENTO, NO DATA READ, NO REGISTRATION"

Revision 2026-10-08 (before launch, V29): Databento is unavailable (acct-2
locked). This session does everything that needs no Databento: sources,
overlap audit, simulator and runners, calendars, the freeze with a
2010-2024 window and its power. Registration, the purchase and the five
runs move to the next stage (E.17), together with C1.

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: The user's research run of 2026-10-07 (how quant firms build
systems, which base strategies survive) concluded that the most durable
edges a small futures trader can reach come from forced, predictable,
price-insensitive flows, and named five hypotheses the program has not
tested in this form. The user decided (V28) not to put a deep network or
reinforcement learning on top of anything yet: ML enters only as a
pre-registered meta-labeling layer on a base rule that has already
passed. This session pre-registers the five base rules with every
parameter fixed, audits their overlap with Stage E's catalogs, builds a
small multi-day simulator, and freezes everything with Fable's review,
on a 2010-2024 window that gives each test real power. It reads no bar
of any market data, calls no Databento endpoint, registers nothing and
runs no test: Databento's acct-2 is locked (V29), and the 2010-2019
history for most products is not yet bought. Stage E.17 will finish C1,
buy the 2010 extension, register the five tests and run each once under
this freeze. Holdout-2 stays sealed for the final confirmation of
anything that passes.

Decisions in force: docs/DECISIONS.md V18, V22, V24 to V29.

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: five pre-registrations and new simulator code
in one unattended night. The silent failures to guard against: a
parameter left free, a settlement time guessed, a multi-day P&L more
generous than the frozen engine's fills and costs, a window or splice
rule that leaks into holdout-2 or cannot be decided before data, and any
market-data byte read. The freeze stays with the lead. Fable reviews it
before the commit.

Usage: follows CLAUDE.md's context-hygiene rules. The user runs this
unattended overnight. The auto-retry launcher resumes it with "read the
STATE file first", so reports/stage_e16_STATE.md names, after every
task, the task finished, the files and hashes in force, each test's
status and the next task. Compute: the ThinkPad under the overnight
profile. Expect 4 to 6 hours.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the
choice under Open choices in the return document, and continue. The only
stops are the ones this prompt names, a decision that cannot be undone
and could reasonably go either way, or a guardrail conflict. A stop in
one test is reported, and the session continues with the others.

============================================================
THE FIVE HYPOTHESES (FIXED HERE; THE FREEZE MAY ONLY TIGHTEN THEM)
============================================================

Common definitions:
- S_p is product p's daily settlement minute in CT, from Task 1's sourced
  table. The lead's prior, to be verified, not used unverified: equity
  index 15:00; Treasuries 14:00; FX 14:00; energy 13:30; gold 12:30;
  copper 12:00; grains 13:15; livestock 13:00; bitcoin 15:00. A product
  whose S_p cannot be sourced at "secondary" grade or better is excluded
  from H1 and H4, counted, with no substitute.
- Prices are bar opens and closes from the owned one-minute stores, using
  the frozen engine's clock: a decision at a bar's close fills at a later
  bar's open. Every entry and exit pays the frozen D8 cost of the
  vehicle (Stage E's cost tables, the bucket of the fill minute, size
  one), plus one extra tick per side beyond q_c, as v2 ruled (V2.8).
- Risk scaling: each position is sized to equal risk using the trailing
  20-trade-date standard deviation of that test's own per-trade gross
  return for that product, computed strictly before the trade date. The
  first 20 eligible dates of each product are warm-up and not traded.
- Exclusions per product: roll-blackout dates, CME early-close and halt
  dates, and dates where a required bar is missing, all from the frozen
  calendars. Each exclusion is counted.
- Universe: the 27 price paths of E.12 (MBT excluded: too short). Each
  product's window starts at the later of 2010-06-07 and its first
  priced month in E.12's 2010-extension quote record
  (reports/stage_e12_quotes_ext2010.json; RTY and TN, for example, start
  years later), plus its warm-up.

H1, settlement-window intraday momentum, pooled. For each product p and
eligible date d: signal = sign of (price at S_p - 30 min on d minus the
settlement-minute price at S_p on the prior eligible date). Enter in the
signal's direction at the open of the bar at S_p - 30 on d; exit at the
open of the bar at S_p on d (both inside Topstep's 15:08 CT flatten).
Zero signal, no trade. Test statistic: the daily pooled net P&L, an
equal-risk average across products traded that date.

H2, month-end rebalancing pair (Harvey, Mazzoleni and Melone). Equity leg
NQ (vehicle MNQ), bond leg ZN. On the fifth-last trading day of each
month, at the settlement minute, compute month-to-date returns of NQ and
ZN from the prior month's last settlement. If NQ outperformed ZN: short
NQ and long ZN; else long NQ and short ZN. Legs are volatility-matched by
the risk rule. Exit both legs at the settlement minute of the month's
last trading day. Multi-day: IBKR venue only. Test statistic: per-month
net P&L of the pair.

H3, Treasury auction cycle (Lou, Yan and Zhang). Tenor map: 2-year to
ZT, 5-year to ZF, 10-year to ZN, 30-year to ZB, from the frozen EC-AUC
calendar (FiscalData, announcement strictly before the auction). For each
auction: short the tenor's contract at the settlement minute three
trading days before the auction date, cover at the auction date's
settlement minute, and go long at that same minute, exiting at the
settlement minute five trading days after the auction date. Multi-day:
IBKR venue only. Test statistic: per-auction net P&L of the two legs
combined. Auctions whose windows overlap the same tenor's next auction
keep the earlier and drop the later, counted.

H4, next-day reversal of the settlement-window move. For each product p
and eligible date d whose prior eligible date had an H1 window move m (the
gross move from S_p - 30 to S_p on that date): trade opposite to sign(m),
entering at the open of the bar at the day-session open O_p + 1 minute on
d, exiting at the open of the bar at S_p - 31 on d (so H4 never overlaps
H1's window). Intraday: both venues. Test statistic: the daily pooled net
P&L, as H1.

H5, the combination. The equal-risk daily combination of H1 to H4's net
daily P&L series (H2 and H3 marked to settlement daily while open, from
the same bars), each series scaled by its own trailing 60-date standard
deviation, computed strictly before the date. Test statistic: the daily
combined net P&L.

Windows (fixed):
- Test window for every test: trade dates 2010-06-07..2024-02-29 (per
  product from its start above), from the ext2010 stores for
  2010-06..2019-04 (to be bought in E.17) and the E.12 phase-1 stores
  from 2019-05. The freeze writes the splice rule (the store boundary,
  roll handling across it, and that no date is double-counted).
- Fallback, fixed now: if E.17 cannot buy the extension for a product,
  that product's window is 2019-05-06..2024-02-29, recorded per product
  at E.17's registration, before any test bar is read. A test whose
  products all fall back runs on the short window with its lower power
  stated.
- Never read: holdout-2 (2024-03..2025-03), MES's sealed stores, anything
  from 2026-06-21. The research window 2025-04..2026-06 is NOT part of any
  test (Stage E's screens used it); after all verdicts are written, the
  same frozen code may report descriptive research-window figures, marked
  descriptive, adding nothing to N.

Pass bar (each test; fixed):
1. Net mean P&L per unit (date, month or auction) above zero, with a
   one-sided p rejected by Holm at family-wise 0.05 across the five tests
   (t-statistics on the per-unit series; H1, H4 and H5 daily, H2 monthly,
   H3 per auction).
2. At least 30 units.
3. Year stability: net P&L positive in at least two thirds of the
   calendar years that hold at least 10 units.
The deflated Sharpe ratio at the program's full N is reported beside
each, as is the 1.5 x slippage case. A pass is evidence, not a deployment
verdict: the next step for a pass is a holdout-2 registered read and,
only then, a meta-labeling design (V28).

Trial count: N rises by 5 at E.17's registration, whatever the outcomes.
This stage registers nothing.

Priors (from the research report, decayed): net Sharpe H1 0.3-0.8, H2
0.4-0.9, H3 0.3-0.7, H4 0.2-0.6, H5 0.8-1.5. The freeze states each
test's power at those values, for the full 2010-2024 window and for the
short fallback window.

============================================================
SCOPE
============================================================

This stage does:
- source the settlement minutes for 2010-2024 (Task 1)
- audit overlap with every Stage D and E catalog member (Task 2)
- build and test the multi-day simulator and the five test runners, on
  synthetic data only, with a runtime probe at full 2010-2024 scale
  (Task 3)
- the calendars the window needs that do not yet exist: the livestock
  group calendar 2010-2019 and the EC-AUC Treasury auction calendar
  2010-2019 from FiscalData, both in the frozen formats (Task 3b)
- freeze the five pre-registrations with Fable's review (Task 4)
- write the E.17 hand-off: the exact purchase list (the 21 extension
  roots not in C1's set, from E.12's quote record), the order of events,
  and the guard against the quote tool's stale-ledger fallback that E.15
  found (Task 5)

This stage does NOT:
- call Databento for anything, buy anything, or read any bar of any
  market data, including the owned stores (the runners touch synthetic
  data only)
- register any test or run any test
- read holdout-2, MES's sealed stores, or any bar from 2026-06-21
- tune, add or drop any parameter after the freeze, or run any test twice
- fit any ML model, deep network or RL policy (V28)
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
CONTEXT TO READ FIRST
============================================================

1. CLAUDE.md (the page-fetch order and its terms rule) and
   docs/ORCHESTRATION.md.
2. docs/DECISIONS.md V22 to V28.
3. reports/E.12_RETURN.md sections 3 and 6 (the stores, the closure-bar
   ruling, the panel builder), reports/E.14_RETURN.md and, if present,
   reports/E.15_RETURN.md.
4. reports/stage_e0_catalog.md: CP1 (all clusters), K2-aucpre-01,
   K2-aucpost-01, K2-monthend-01, X-04, and the K3 and K1 members; the
   K1-K9 catalogs for the overlap audit; the Stage D family declarations.
5. docs/STAGE_E_DESIGN.md (FROZEN): D4, D6, D8, D9.
6. The code: screening/stage_e_engine.py (fills, costs, clock),
   data/stage_e_bars.py and data/step2_store.py (the stores),
   data/hist_store.py (the ext2010 stores), ml_route_v2/phase1 (the
   loaders), screening/trial_registry.py, rules/sessions.py,
   rules/products.py, the frozen calendars and EC-AUC.

============================================================
GUARDRAILS
============================================================

- Harness: v10
  fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b,
  verified at start. No harness file changes in this stage (C1's freeze
  allows only a cap change in the next harness). New code lives in a new package base_rules/ outside
  the harness directories, frozen by this stage's own manifest. Fresh
  PYTHONPYCACHEPREFIX outside the repository.
- No market-data bar is read at all in this stage. Store metadata
  (file names, sizes, manifests, quote records) may be read.
- Web access (Tasks 1 and 3b only; FiscalData is a public API whose
  terms allow access): read a site's terms before any automated
  fetch. CME's own site forbids automated access (E.12): do not fetch it
  or archived copies of it. Use other sources that allow access
  (published papers, exchange rulebook excerpts quoted by permitted
  sources, broker contract pages whose terms allow it), each graded and
  cited. No login, no paid source.
- The multi-day simulator is never more generous than the frozen engine:
  the same fill rule, the same D8 costs and the extra tick.
- Holdout status all_ok, 0 unlocks, at start and end. The ledger is
  unchanged.
- Start and end checks, quoted verbatim in the return: `git status
  --short`, `git log --oneline -3`, the holdout status, `wc -c
  REGISTRATION.md`, the manifest checks, the cluster freezes, the v2
  freeze verify, the ledger line count, sha256 and total per account,
  and `uv run pytest -q -p no:cacheprovider` (without
  PYTHONPYCACHEPREFIX).
- Before ending, confirm no worker or background shell is still running.

============================================================
TASKS
============================================================

TASK 0: STARTUP (lead). Start checks; the STATE file; the ETA table. HEAD
is the commit holding this prompt or a descendant with a clean tree
(apart from the expected DO_NOT_COMMIT page folders and
.claude/worktrees/).

TASK 1: SETTLEMENT MINUTES (SettlementSource-OpusHigh, worker-high on
opus). For each of the 27 products, the daily settlement minute in CT for
2010-2024, every change in that period with its date, a grade and a
cited source. Output reports/stage_e16_settlement.md and .json.

TASK 2: OVERLAP AUDIT (OverlapAudit-OpusHigh, worker-high on opus; the
lead rules). Compare each of H1 to H5 against every Stage D and E member:
same signal, same window, same products. Report each near match (for
example CP1's first-half-hour signal into the last 30 minutes; K2's
intraday auction and month-end slices) and how H1 to H5 differ. Rule: a
hypothesis identical to a tested member (same signal, window and
products) is dropped before registration; a related one is kept and the
relation is written into its freeze. Output reports/stage_e16_overlap.md.

TASK 3B: CALENDARS (CalendarBuilder-OpusHigh, worker-high on opus). The
livestock group calendar 2010-06..2019-05 (holidays, early closes,
halts) in E.14's calendar format and grading, and the EC-AUC auction
calendar 2010-2019 from FiscalData with E.0's announcement rule, both
with their 2% unsourced-date checks. E.14's six group calendars
(energy, equity, rates, FX, metals, grains) for 2010-2019 are reused as
frozen. Output the calendar files and reports/stage_e16_calendars.md.

TASK 3: BUILD (BaseRulesCoder-OpusXHigh, worker-xhigh on opus, in a
worktree; the lead merges). base_rules/: the multi-day position
simulator (entries and exits at bar opens per the engine's clock, D8
costs plus the extra tick, daily marks at settlement), the five test
runners reading the frozen stores, the statistics (per-unit t, Holm,
year stability, DSR at N, the 1.5 x slippage case), a run-once marker per
test, and tests: a hand-computed multi-day trade to the cent, a
single-day trade that matches the frozen engine fill for fill, causality
tests for every signal and for the risk scaling, a planted-edge synthetic
test each runner must detect, and a pure-noise test each must reject.
The store loader for the 2010-2024 splice is built and tested on
synthetic stores of the same layout as the ext2010 and E.12 stores.
Synthetic data only. A runtime probe at the full 2010-2024 scale (27
products, about 3,500 dates) reports wall time and peak memory.

TASK 4: FREEZE (lead, with FreezeReviewer-FableXHigh, worker-xhigh on
fable, before the commit). reports/stage_e16_prereg_H1.md to _H5.md, the
text above with Task 1's settlement table, Task 2's relations, each
test's power, and nothing loosened. A manifest
reports/stage_e16_freeze.json hashing the prereg files, base_rules/, its
tests and every input table, including the splice rule, the fallback
rule and the power table. The reviewer checks: no free parameter, no
look-ahead, the simulator no more generous than the engine, the windows
clear of holdout-2, the splice and fallback rules decidable before any
bar is read, the pass bars as stated. Findings graded BLOCKING, SHOULD
FIX or NOTE in reports/stage_e16_review.md; the lead's rulings in
reports/stage_e16_rulings.md; every BLOCKING and SHOULD FIX fixed before
the commit. One commit "E.16 base-rule freeze".

TASK 5: E.17 HAND-OFF (lead). reports/stage_e16_handoff.md: the exact
order E.17 must follow (verify both freezes, C1's then this one; the
fresh quote with the lead-side guard that sums the fresh total from the
run's own new ledger lines and never trusts the tool's JSON or uses
--retry-failed; the cap change as the only harness diff; C1's
registration and purchase; this batch's registration; the purchase of
the remaining extension roots; the store builds; C1's evaluation; the
five runs; Fable's recomputation), the purchase list with E.12's quoted
cost per root, the funds each step needs, and the commands.

TASK 6: RETURN AND COMMIT (lead). One final commit "Stage E.16 Part A:
base-rule batch frozen" holding the reports, the calendars, base_rules/,
its tests, the STATE file and the briefs. No push.

============================================================
DELEGATION PLAN
============================================================

| Task | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup | lead | opus | xhigh | first | gates the session |
| 1 Settlement minutes | SettlementSource-OpusHigh | opus | high | parallel | sourced facts with terms checks |
| 2 Overlap audit | OverlapAudit-OpusHigh | opus | high | parallel | catalog reading, lead rules |
| 3 Build | BaseRulesCoder-OpusXHigh | opus | xhigh | parallel | simulator must match the engine |
| 3b Calendars | CalendarBuilder-OpusHigh | opus | high | parallel | sourced dates, rule-exact |
| 4 Freeze review | FreezeReviewer-FableXHigh | fable | xhigh | after 1 to 3b | independent check before commit |
| 4 Freeze, commit | lead | opus | xhigh | after review | reserved to the lead |
| 5 Hand-off | lead | opus | xhigh | after 4 | reserved to the lead |
| 6 Return, commit | lead | opus | xhigh | last | reserved to the lead |

Usage pools: weekly usage reset on 2026-10-07; Fable runs only the
freeze review at xhigh. Web work stays on Opus high. No Sonnet or Haiku worker
draws a conclusion.

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

Compute: heavy steps at nice 10 under the overnight profile, peak memory
under 70% of free memory at launch, resumable checkpoints.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.16_RETURN.md. Fixed sections, in order:

1. Verdict summary, at most 300 words: what was frozen (or dropped by the
   overlap audit), each test's power on the full and fallback windows,
   the freeze hash, the E.17 purchase list and its cost, and what E.17
   must do.
2. Guardrail evidence: the start and end checks verbatim, and a
   statement that no bar was read and no vendor was called.
3. Results per task: the settlement table, the overlap rulings, the
   calendars, the build and its tests, the runtime probe, the freeze,
   the hand-off.
4. Delegation record: one row per spawn.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

Also write one short dated progress.md entry and one line in
docs/STAGES.md.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
