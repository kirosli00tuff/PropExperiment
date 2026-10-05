STAGE E.14 "C1 AND C2 TOGETHER: PROBE, CALENDARS AND FREEZES FOR BOTH; C2 BOUGHT AND EVALUATED ONCE WITH THE FUNDS ON HAND; C1 FROZEN AND READY, AWAITING FUNDS"

Revision 2026-10-05 (before launch, V26): the acct-2 top-up did not go
through. No cap raise, spend limited to acct-2's current headroom
($18.07), C2's ES only. C1 is built, frozen and taken through its q
reproduction, then stops before registration and purchase.

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage E.13 ranked what is left to search and drafted two
pre-registrations: C1, a backward replication of E.12's NG near-miss on
2010-2019 NG data never read, and C2, dealer-gamma-conditioned
late-session momentum in S&P futures over 2011-2019 (Baltussen et al.,
JFE 2021). The user chose to run both together (V25), allowed C1's two
computations on the 2019-2024 panel, and reopened the S&P exposure for
C2's one test. The acct-2 top-up failed (V26), so this session works with
the funds on hand: it runs the calendar probe, builds the calendars,
freezes both pre-registrations with harness v10, fetches and checks the
GEX file, reproduces C1's threshold and fits M1, then registers C2 only,
buys C2's ES data within acct-2's $18.07 of headroom, and evaluates C2
exactly once. C1 ends frozen and ready, with its registration, purchase
and evaluation left to a later session once funds are in place. Each
test has its own stop rules, and a stop in one never blocks the other.

Decisions in force: docs/DECISIONS.md V18, V23, V24, V25, V26. The drafts
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
status (running, stopped with reason, frozen awaiting funds, or done),
the ledger total per account and the next task. Compute: the ThinkPad
under the overnight profile. Expect 5 to 8 hours.

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
- C1's M1 fit and the q reproduction, then C1 stops, frozen (Task 5)
- registration of C2, then the quote and C2's purchase (Task 6)
- C2's store build and its one evaluation (Task 7)
- Fable verification of C2's verdict and of C1's q reproduction (Task 8)
- a free quote for C1's set, so the user knows the top-up (Task 6)

This stage does NOT:
- read, summarize or plot any test-window byte (NG and its five legs
  2010-06..2019-04, ES 2011-05..2019-04, GEX values) before that test's
  freeze and registration, except the counts the drafts allow
- spend above acct-2's current headroom ($18.07 under the unchanged
  cap of $249.67), buy anything but C2's ES, or raise any cap
- register, buy or evaluate C1 (it stops frozen after Task 5)
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
- Spend (V26). Pre-approved, no further approval needed, if every
  condition holds:
  - only through the frozen purchase path and its gate, after a fresh
    quote-only run in this session, ledgered at $0.00;
  - only C2's ES 2011-05..2019-04;
  - acct-2 only (acct-1's $1.61 fits no root), under the unchanged
    ACCOUNT_2_CAP_USD = 249.67, and the session cap = the fresh ES quote
    plus 3%, never above acct-2's remaining headroom ($18.07).
  A fresh ES quote whose 3% margin exceeds the headroom stops C2 before
  its registration, and the return states the shortfall. Databento
  refusing a purchase for insufficient balance stops the buy and is
  reported. A billed amount above its quote by more than 3% is a stop.
- C1's set (NG, NQ, ZN, 6E, GC, ZC 2010-06..2019-04, with the June-2010
  chunks) is quoted only, ledgered at $0.00, never bought here.
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
  the lead commits): ACCOUNT_2_CAP_USD unchanged at 249.67 (V26; the
  raise waits for the user's top-up and a later harness), the E.14
  session caps for C2's ES only, an "ext2010" store type and buy plan for C1's six roots
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
  freezes, C1 and C2". A test dropped earlier is not frozen. C1's freeze
  records that its registration (N 473 -> 475), purchase and evaluation
  happen in a later session, under this freeze, with v10 or a later
  harness that changes only the acct-2 cap and session caps.

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
- Then C1 stops with status FROZEN, AWAITING FUNDS. It is not
  registered, so N does not change for it tonight.
- Output: reports/stage_e14_c1_model.md, including exactly what the later
  session must do (register, quote fresh, buy, build, evaluate once) and
  the hashes it must verify first (the freeze, M1, q, the E.12 state copy).

============================================================
TASK 6: REGISTRATION, QUOTE AND PURCHASE (LEAD)
============================================================

- Fresh quote-only runs, ledgered at $0.00: C2's ES, and C1's full set
  (for the user's top-up figure).
- If the ES quote fits the spend guardrail: register C2's T1 and T2 in
  the append-only ledger (N 471 -> 473), then buy ES.
- Output: reports/stage_e14_purchase.md: both quotes, the caps, ledger
  lines, billed against quoted per chunk, the balance left, the top-up C1
  needs (its quote plus 3% minus the headroom left after C2), and the
  holdout status after the purchase.

============================================================
TASK 7: STORES AND THE EVALUATIONS (LEAD RUNS THE FROZEN CODE)
============================================================

- Store builds print counts only.
- C1 is not evaluated in this stage.
- C2: build the eligible-date table, then run T1 and T2 once behind a
  run-once marker. Verdict per draft section 5, including the T1 versus
  T2 comparison.
- Output: reports/stage_e14_c2_result.md with its JSON: the verdict (PASS, FAIL, or STOPPED with
  the rule that fired), every statistic, and its hashes.

============================================================
TASK 8: VERIFICATION (FABLE)
============================================================

- VerdictVerifier-FableXHigh (worker-xhigh on fable): recomputes both
  C2's verdict independently from the store and the frozen rules,
  without reading the lead's statistics first: the eligible-date count,
  T1 and T2's trades, mean g, t and p, and the T1 versus T2 comparison.
  It also re-runs C1's q reproduction and M1 coefficient hash from the
  frozen state. It
  also checks the order of events in git and the ledger.
- Output: reports/stage_e14_review.md (both Fable passes, graded
  BLOCKING, SHOULD FIX or NOTE) and reports/stage_e14_rulings.md. A
  BLOCKING finding on a verdict number is resolved by finding the code
  error, never by rerunning an evaluation with changed rules; if
  unresolved, that verdict is reported as unverified.

============================================================
TASK 9: RETURN AND COMMIT (LEAD)
============================================================

- One final commit "Stage E.14 C1 frozen, C2 evaluated" holding the
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
| 6 Quotes, C2 registration, buy | lead | opus | xhigh | after 5 | spend, reserved to the lead |
| 7 C2 evaluation | lead | opus | xhigh | after 6 | verdict, reserved to the lead |
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
- No spend beyond C2's ES within $18.07, no cap raise, no acct-1
  purchase, no C1 registration, purchase or evaluation.
- No second evaluation, and no rule changed after a freeze.
- No Gate 0 rerun, no 2019-2024 test, no MES holdout opened.
- No AskUserQuestion. No key printed. No push. No write to REGISTRATION.md.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.14_RETURN.md. Fixed sections, in order:

1. Verdict summary, at most 300 words: C2's verdict (PASS, FAIL or
   STOPPED with the rule) and its decisive numbers; C1's status (FROZEN,
   AWAITING FUNDS, or dropped with the rule) and its q reproduction;
   what was bought and its cost, the funds left, the top-up C1 needs, the
   v10 and freeze hashes, the new N, and what C2's outcome means per its
   draft's section 8.
2. Guardrail evidence: the start, post-purchase and end checks verbatim,
   and the order of events with timestamps per test.
3. Results per task: the probe, the calendars, the GEX file and count,
   v10, the freezes, M1 and q, the quotes and purchase, C2's evaluation.
4. Delegation record: one row per spawn.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation: C2's next step
   per its outcome; C1's top-up and the session that completes it; and
   whether anything else is left before the AiTrader readout.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

Also write one short dated progress.md entry and one line in
docs/STAGES.md.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
