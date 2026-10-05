STAGE E.14 "TWO REGISTERED TESTS IN ONE NIGHT: THE BACKWARD NG REPLICATION (C1) AND GAMMA-CONDITIONED S&P LATE-SESSION MOMENTUM (C2): PROBE, FREEZE, BUY, EVALUATE ONCE EACH"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage E.13 ranked what is left to search and drafted two
pre-registrations: C1, a backward replication of E.12's NG near-miss on
2010-2019 NG data never read, and C2, dealer-gamma-conditioned
late-session momentum in S&P futures over 2011-2019 (Baltussen et al.,
JFE 2021). The user chose to run both in one overnight stage (V25), allowed
C1's two computations on the 2019-2024 panel, reopened the S&P exposure
for C2's one test, topped up acct-2 by $60 and pre-approved spending up to
$75 after a logged fresh quote. This session runs the calendar probe,
builds the calendars, freezes both pre-registrations with harness v10,
fetches and checks the GEX file, reproduces C1's threshold, registers
both tests, buys the data, and evaluates each test exactly once. Each
test has its own stop rules, and a stop in one never blocks the other.

Decisions in force: docs/DECISIONS.md V18, V23, V24, V25. The drafts
reports/stage_e13_prereg_ngrepl.md (C1) and
reports/stage_e13_prereg_gexmom.md (C2) rule, with C1's technical annex
reports/stage_e13_ng_replication_draft.md and its rulings C1-C21, and
reports/stage_e13_rulings.md. Where a draft and its annex differ, the
draft rules.

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: two pre-registered evaluations, a purchase and
a harness change in one unattended night. The silent failures to guard
against: any test-window byte read before its freeze and registration,
a parameter fixed after data, a threshold that fails to reproduce E.12
exactly, a calendar date guessed, a GEX row used before it was public,
spend above the approval, and a wrong verdict number. Spend, freezes and
verdicts stay with the lead. Fable reviews the freezes before they are
committed and recomputes both verdicts independently.

Usage: follows CLAUDE.md's context-hygiene rules. The user runs this
unattended overnight. The auto-retry launcher resumes it with "read the
STATE file first", so reports/stage_e14_STATE.md names, after every
task, the task finished, the files and hashes in force, C1's and C2's
status (running, stopped with reason, or done), the ledger total per
account and the next task. Compute: the ThinkPad under the overnight
profile. Expect 6 to 9 hours.

Do not stop to ask. Do not use AskUserQuestion: the user is asleep.
Decide, log the choice under Open choices in the return document, and
continue. The only stops are the ones this prompt and the drafts name, a
decision that cannot be undone and could reasonably go either way, or a
guardrail conflict. A stop in one test is reported and the session
continues with the other.

============================================================
SCOPE
============================================================

This stage does:
- the calendar probe that can drop C1 (Task 1)
- the calendars both tests need, from official pages, no prices (Task 2)
- the GEX file: terms, fetch, timing rule, the GEX < 0 count (Task 3)
- harness v10 and the freezes of both pre-registrations (Task 4)
- C1's M1 fit and the q reproduction (Task 5)
- registration of both tests, then the quote and the purchase (Task 6)
- the store builds and one evaluation per test (Task 7)
- Fable verification of both verdicts (Task 8)

This stage does NOT:
- read, summarize or plot any test-window byte (NG and its five legs
  2010-06..2019-04, ES 2011-05..2019-04, GEX values) before that test's
  freeze and registration, except the counts the drafts allow
- spend above $75.00 in total, or above acct-2's cap of $309.67, or buy
  anything the two drafts do not list
- touch MES's sealed holdouts, holdout-1, holdout-2 or the research
  window
- rerun Gate 0, refit anything on 2019-2024 beyond C1's single M1 fit,
  or test anything on 2019-2024
- run either evaluation more than once, or change a pass bar, window,
  rule or cost after its freeze
- contact any firm or data provider, create any account, log in, or
  touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
CONTEXT TO READ FIRST
============================================================

Read by section, as CLAUDE.md's context-hygiene rules require.

1. CLAUDE.md (the page-fetch order and its terms rule) and
   docs/ORCHESTRATION.md.
2. docs/DECISIONS.md V23 to V25.
3. reports/stage_e13_prereg_ngrepl.md and reports/stage_e13_prereg_gexmom.md
   in full.
4. reports/stage_e13_ng_replication_draft.md: sections 2 to 11 and the
   lead's rulings C1-C21.
5. reports/E.13_RETURN.md sections 3 (Tasks 3 and 4) and 6, and
   reports/stage_e13_rulings.md.
6. reports/E.12_RETURN.md section 3 (Tasks 4 to 6) and section 6.
7. docs/STAGE_E_DESIGN.md (FROZEN): D1 rule 5, D4, D8, D13.
8. The code: data/config.py, data/spend_gate.py, data/pull_step2.py,
   data/step2_store.py, data/stage_e_bars.py, data/holdout.py,
   screening/harness_freeze.py, ml_route_v2/ (gate0.py, gate0_stage.py,
   normalize.py, signals/, phase1/), rules/products.py,
   reports/stage_e2a_costs.md (the MES check rows 14:30 and 15:00).

============================================================
GUARDRAILS
============================================================

- Harness: every Stage E command takes `--harness-sha256
  7fd757f6d7c3990c2d20756c501f68b0541aa89851dcca9236badabd4f4a9bd9` (v9)
  until Task 4 commits v10, then the v10 sha256. Fresh
  PYTHONPYCACHEPREFIX outside the repository.
- Spend (V25). Pre-approved, no further approval needed, if every
  condition holds:
  - only through the frozen purchase path and its gate, after a fresh
    quote-only run in this session, ledgered at $0.00;
  - only the items the drafts list: ES 2011-05..2019-04 (C2); NG, NQ, ZN,
    6E, GC and ZC 2010-06..2019-04, including the June-2010 chunks (C1);
  - acct-2 only (acct-1's $1.61 fits no root), under
    ACCOUNT_2_CAP_USD = 309.67, and the session cap = the fresh quote of
    the items still live plus 3%, never above $75.00;
  - C2's ES is bought first (it is small), then C1's set.
  A fresh quote whose live items exceed $75.00 drops C1's purchase (C2
  goes on) and is reported with the figures. Databento refusing a
  purchase for insufficient balance stops further buys, and the return
  states the top-up needed. A billed amount above its quote by more than
  3% stops further buys.
- Order of events per test, enforced in git and the ledger: probe and
  calendars, then freeze commit, then registration (N written), then
  purchase, then evaluation. The return shows the timestamps.
- Web access (Tasks 1 to 3): read a site's terms of use BEFORE any
  automated fetch from it (E.13's Scrapling deviation). Official
  government and exchange calendar pages, Wayback captures of them, and
  SqueezeMetrics' public CSV page only. A site whose terms forbid
  automated access is not fetched by automation. Fetch order per
  CLAUDE.md. No login, no paid source.
- Holdout status all_ok, 0 unlocks, at start, after the purchase and at
  end. MES's sealed stores are never opened.
- Start and end checks, quoted verbatim in the return: `git status
  --short`, `git log --oneline -3`, the holdout status, `wc -c
  REGISTRATION.md`, the manifest checks, the cluster freezes, the v2
  freeze verify, the ledger line count, sha256 and total per account,
  and `uv run pytest -q -p no:cacheprovider` (expected at start: E.12's
  end state, 6,505 passing; run without PYTHONPYCACHEPREFIX, as E.12
  ruled).

============================================================
TASK 0: STARTUP
============================================================

- Owner: lead. Output: reports/stage_e14_STATE.md and the ETA table.
- Check that ~/.cache/propexp_e12_phase1 exists (names and sizes only).
  If it is missing, C1 stops now (it is the only source of q) and the
  session runs C2 alone.
- Done when: the start checks pass and HEAD is the commit holding this
  prompt or a descendant with a clean tree (the untracked
  DO_NOT_COMMIT page folders from E.12 and E.13 are expected).

============================================================
TASK 1: THE CALENDAR PROBE (GATES C1)
============================================================

- Owner: CalendarProbe-OpusHigh (worker-high on opus); the lead rules.
- Source one year, 2012, of the energy group calendar (holidays, early
  closes, halts) and the EIA NGS release table at evidence grade ("cme"
  or "secondary", as C1's ruling C12 defines), from official pages and
  Wayback captures.
- Rule, fixed now: if more than 2% of 2012's energy trade dates, or more
  than 2 NGS release dates, cannot be sourced at "cme" or "secondary"
  grade, C1 is dropped before any freeze (no N added), and the session
  runs C2 alone.
- Output: reports/stage_e14_probe.md with every date's grade and source.

============================================================
TASK 2: CALENDARS FOR BOTH TESTS (NO PRICES)
============================================================

- Owners: up to three CalendarBuilder workers (worker-high on opus),
  split by group, with the lead merging.
- C2 needs: the CME equity group calendar 2011-05..2019-04 (holidays,
  early closes), shared with C1.
- C1 needs (if not dropped): the energy, equity, rates, FX, metals and
  grains group calendars 2010-06..2019-05; Topstep flatten rows by Rule
  H-1; the release calendar for NG's D8 list (EIA NGS, WPSR, FOMC); the
  regenerated K4 literal tables (annex section 5, C-1 to C-5).
- Each date carries a grade and a source row, in the frozen calendar
  formats. The 2% unsourced-date stops (C1 ruling C12; C2 section 3)
  are checked here, before any price is bought. A stop drops that test
  (no N added if before its registration).
- Output: the calendar files and reports/stage_e14_calendars.md.

============================================================
TASK 3: THE GEX FILE (C2)
============================================================

- Owner: lead (small).
- Read SqueezeMetrics' terms and the CSV page's terms first. If they
  forbid this use, C2 stops (no substitute series).
- Fetch the daily DIX/GEX CSV once: URL, UTC fetch time, sha256, stored
  under the stage's briefs. Record the timing rule (C2 section 2: the
  row of the latest trading day strictly before d, or two days back if
  publication can fall after 14:30 CT on d), with the source of the
  publication-time fact.
- The only read of GEX values before the evaluation: the COUNT of
  eligible dates with GEX < 0 in 2011-05-03..2019-04-30 under the timing
  rule and the Task 2 calendar. No prices, no returns. Under 200: C2
  stops (section 7's power stop).
- Output: reports/stage_e14_gex.md.

============================================================
TASK 4: HARNESS V10 AND THE FREEZES (LEAD, WITH FABLE BEFORE THE COMMIT)
============================================================

- Harness v10 (V10Coder-OpusXHigh, worker-xhigh on opus, in a worktree;
  the lead commits): ACCOUNT_2_CAP_USD = 309.67 (V25), the E.14 session
  caps, an "ext2010" store type and buy plan for C1's six roots
  (2010-06..2019-04, with the June-2010 partial chunks and the fixed
  start 2010-06-07, ruling C5) and an ES store for 2011-05..2019-04,
  both refusing any chunk outside their windows, with tests. Diff against
  v9 shown.
- Freezes: reports/stage_e14_prereg_C1.md and reports/stage_e14_prereg_C2.md,
  the drafts with V25's decisions applied and nothing else changed except
  what Fable's review requires (each change listed). C1's freeze also
  hashes E.12's persisted state (45 .npy files, meta, 2 pickles, the
  build JSON) and makes a read-only copy (ruling C17). C2's freeze
  records the GEX file's sha256 and the timing rule.
- FreezeReviewer-FableXHigh (worker-xhigh on fable) reviews both freezes
  and v10 before the commit: no free parameter, every stop rule present,
  the order of events enforceable, the windows disjoint from everything
  the program has read.
- Commits, in order: "harness v10, E.14 caps and stores", then "E.14
  freezes, C1 and C2". A test dropped earlier is not frozen.

============================================================
TASK 5: C1'S M1 FIT AND THE q REPRODUCTION (LEAD)
============================================================

- Reload E.12's persisted out-of-fold predictions and reproduce E.12's
  NG h60 and hF family B rows (trades, mean, t_B) to 1e-9. Any mismatch
  stops C1.
- Fix q per horizon (ruling C3). Fit M1 once on the full E.12 training
  panel with the frozen code, constants byte-identical. Write M1's
  coefficient hash and both q values to STATE before any 2010-2019 byte
  is bought.
- Output: reports/stage_e14_c1_model.md.

============================================================
TASK 6: REGISTRATION, QUOTE AND PURCHASE (LEAD)
============================================================

- Register the live tests in the append-only ledger before any purchase:
  C1's T1 and T2 (N 471 -> 473), then C2's T1 and T2 (-> 475). If C1 was
  dropped, C2 takes 471 -> 473.
- Fresh quote-only run for the live items, ledgered at $0.00. Then buy
  per the spend guardrail: ES first, then C1's six roots.
- Output: reports/stage_e14_purchase.md: quotes, caps, ledger lines,
  billed against quoted per chunk, the balance left, the holdout status
  after the purchase.

============================================================
TASK 7: STORES AND THE EVALUATIONS (LEAD RUNS THE FROZEN CODE)
============================================================

- Store builds print counts only.
- C1: compute the replication features on NG rows, the applicable-row
  counts per feature without values (ruling C10: any feature live in
  E.12 with 0 applicable rows stops C1 and closes this attempt), then
  the evaluation once behind a run-once marker. Verdict per draft
  section 5, then the descriptive outputs (section 6, ruling C15).
- C2: build the eligible-date table, then run T1 and T2 once behind a
  run-once marker. Verdict per draft section 5, including the T1 versus
  T2 comparison.
- Output: reports/stage_e14_c1_result.md and reports/stage_e14_c2_result.md
  with their JSON, each with the verdict (PASS, FAIL, or STOPPED with
  the rule that fired), every statistic, and its hashes.

============================================================
TASK 8: VERIFICATION (FABLE)
============================================================

- VerdictVerifier-FableXHigh (worker-xhigh on fable): recomputes both
  verdicts independently from the stores and the frozen rules, without
  reading the lead's statistics first: C1's q reproduction, the trade
  count, mean gross, c, t and p per test; C2's eligible-date count, T1
  and T2's trades, mean g, t and p, and the T1 versus T2 comparison. It
  also checks the order of events in git and the ledger.
- Output: reports/stage_e14_review.md (both Fable passes, graded
  BLOCKING, SHOULD FIX or NOTE) and reports/stage_e14_rulings.md. A
  BLOCKING finding on a verdict number is resolved by finding the code
  error, never by rerunning an evaluation with changed rules; if
  unresolved, that verdict is reported as unverified.

============================================================
TASK 9: RETURN AND COMMIT (LEAD)
============================================================

- One final commit "Stage E.14 C1 and C2 evaluations" holding the
  reports, results, ledger registrations, the STATE file and the
  briefs. Bars and raw data stay in the frozen stores. No push.

============================================================
DELEGATION PLAN
============================================================

| Task | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup | lead | opus | xhigh | first | gates the session |
| 1 Probe | CalendarProbe-OpusHigh | opus | high | first, with 3 | sourced dates, gates C1 |
| 2 Calendars | CalendarBuilder-OpusHigh x up to 3 | opus | high | parallel, after 1 | sourced dates by group |
| 3 GEX file | lead | opus | xhigh | parallel with 1 | terms and timing judgment |
| 4 v10 | V10Coder-OpusXHigh | opus | xhigh | parallel with 2 | frozen-file change |
| 4 Freeze review | FreezeReviewer-FableXHigh | fable | xhigh | after 2, 3, v10 | independent check before commit |
| 4 Freezes, commits | lead | opus | xhigh | after review | reserved to the lead |
| 5 M1, q | lead | opus | xhigh | after 4 | reserved to the lead |
| 6 Registration, buy | lead | opus | xhigh | after 5 | spend, reserved to the lead |
| 7 Evaluations | lead | opus | xhigh | after 6 | verdicts, reserved to the lead |
| 8 Verify | VerdictVerifier-FableXHigh | fable | xhigh | after 7 | verdict numbers recomputed |
| 9 Return, commit | lead | opus | xhigh | last | reserved to the lead |

Usage pools: Fable runs only the two checks, at xhigh. Web work stays on
Opus high. No Sonnet or Haiku worker draws a conclusion.

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
WHAT NOT TO DO
============================================================

- No test-window byte read before that test's freeze and registration.
- No spend above $75.00, no item outside the drafts, no acct-1 purchase.
- No second evaluation, and no rule changed after a freeze.
- No Gate 0 rerun, no 2019-2024 test, no MES holdout opened.
- No AskUserQuestion. No key printed. No push. No write to REGISTRATION.md.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.14_RETURN.md. Fixed sections, in order:

1. Verdict summary, at most 300 words: C1's and C2's verdicts (PASS,
   FAIL or STOPPED with the rule) and their decisive numbers, what was
   bought and its cost, the funds left, the v10 and freeze hashes, the
   new N, and what each outcome means per the drafts' section 8.
2. Guardrail evidence: the start, post-purchase and end checks verbatim,
   and the order of events with timestamps per test.
3. Results per task: the probe, the calendars, the GEX file and count,
   v10, the freezes, M1 and q, the purchase, both evaluations.
4. Delegation record: one row per spawn.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation: on a pass, the
   next pre-registered step the draft names; on fails, what is closed,
   and whether anything is left before the AiTrader readout.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

Also write one short dated progress.md entry and one line in
docs/STAGES.md.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
