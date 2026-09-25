STAGE E.2a "STAGE E BUILD, PART 1: FREEZE THE ML ROUTE, THEN BUILD PER-PRODUCT RULES, CALENDARS, RESEARCH-WINDOW BARS, COSTS, VEHICLES AND EPSILON (NO MEMBER RUN)"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage E.1 (commits 848f331, b05c506, 1b54dc1) froze the Stage E
design, null criteria and catalog (manifest reports/stage_e1_freeze.json,
sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c),
bought step 1 (904 files, the research window of every admissible contract
and the mbp-1 sample, reports/stage_e1_purchase.json), and drafted the ML
route (docs/STAGE_E_ML_DESIGN.md, DRAFT). The user accepted the planning
chat's recommendations on that draft on 2026-09-25 (Task 1 lists them).
This session is the first half of the Stage E build. It first freezes the
ML route design, because that design must be frozen before anyone reads a
research-window bar. Then it builds, with known-answer tests, the parts of
design D11 that need only step 1 data: the per-product rules engine
(D11.1), the group calendars (D10, D11.3), the research-window bar builds
(part of D11.4), the cost model (D8, D11.2), the vehicle choice (D2,
D11.10), the funnel re-derivation of epsilon (D3, D11.8) and the two
carried test fixes (D14, D11.11). It also records the source windows of
the catalog's source-overlap members as a logged amendment. It stops
there. Stage E.2b builds the screening runner, the ML pipeline with its
leakage tests, the canaries and the harness freeze manifest, and buys the
older history once the user funds it.

Lead: Opus 5.5, effort xhigh. Ultracode: on.

Why this lead and effort: this is an implementation session. The freeze
content in Task 1 was decided by the user, the lead only applies it, and
an independent Fable worker audits it. The rest is harness building,
which CLAUDE.md routes to opus at xhigh (sim/, rules/ and data/ work).
Ultracode is on because the build has more than four independent
workstreams (the rules engine, six new group calendars plus the equity
fix, the bar builds, the cost model, the funnel re-derivation, the test
fixes, the source-window reading), all of them opus work anyway, so
ultracode's fan-out at the lead's tier loses no routing saving. The user
launches it interactively. The lead at xhigh rather than max keeps
ultracode's fan-out at xhigh, which the routing table sets for this kind
of coding.

Usage: Fable is used by one worker, DeclarationAuditor-FableXHigh,
resumed with SendMessage for three briefs: the ML freeze audit (Task 3),
the source-window amendment audit (Task 11), and the independent
recomputation of the verdict-bearing build numbers (Task 12). No fable
max review. If Fable is unavailable when Task 3 starts, nothing that reads
a research-window bar may run: finish Tasks 2, 5 (the parts that read no
bars) and 10, and mark the rest pending. Never substitute opus for a Fable
check. The compute rules are the overnight profile in CLAUDE.md (added
2026-09-25): at most 14 threads and two heavy jobs at once, the combined
peak memory under 70% of available, the RTX 3050's 4 GB GPU allowed, nice
10, resumable, and nothing heavy in the AiTrader window (about 15:30 to
16:00 PT on weekdays).

Do not stop to ask. Decide, log the choice under Open choices in the
return document, and continue. The only stops are the ones this prompt
names, a decision that cannot be undone and could reasonably go either
way, or a guardrail conflict.

============================================================
SCOPE
============================================================

This stage does:
- apply the user's ML-route decisions and freeze docs/STAGE_E_ML_DESIGN.md
  (Tasks 1, 3, 4)
- record the source windows of the source-overlap members as a separate,
  audited amendment (Tasks 2 and 11)
- build and test the per-product rules engine, the group calendars, the
  research-window bars, the cost model, the vehicle choice and the
  funnel epsilon, and fix the two carried tests (Tasks 5 to 10)
- have every verdict-bearing build number recomputed independently (Task
  12)

This stage does NOT:
- buy anything. The E.1 session cap stays as it is, and no E.2a spend
  constant is created. The older history (2019-05..2025-03) is bought in
  E.2b or later, after the user funds acct-2.
- run, screen or score any catalog member, compute any member's P&L, or
  run the power check (D4). That belongs to the cluster screening
  sessions.
- build the screening runner (D11.6), the ML pipeline or its leakage tests
  (D11.7 and M7), the canaries (D11.9) or the harness freeze manifest.
  Those belong to E.2b.
- fit, tune or train any model.
- edit any file frozen by reports/stage_e1_freeze.json. The source-window
  record is a new amendment file, never an edit to a frozen file.
- touch holdout-1 or holdout-2, live/, ops/, or any TopstepX credential or
  API
- edit docs/NULL_CRITERIA.md or reports/stage_d1f_confirmation_list.md
- write to REGISTRATION.md (it stays 0 bytes)
- push. The session makes exactly the two commits Tasks 4 and 11 name.
  The build code stays uncommitted for the planning chat's review.

============================================================
CONTEXT TO READ FIRST
============================================================

1. CLAUDE.md and docs/ORCHESTRATION.md: roles, routing, worker files,
   worker naming, concurrency, artifacts, checkpoints, the ETA tables,
   the Session cost section, and the overnight profile under Compute
   limits. This prompt does not repeat them. On any conflict CLAUDE.md
   wins, and the conflict is logged.
2. reports/E.1_RETURN.md, in full.
3. docs/STAGE_E_DESIGN.md (FROZEN): D1 (the 31 traded exposures and their
   admissible vehicles), D2, D3, D4, D6 (session tables), D8, D9, D10,
   D11 and D14.
4. docs/NULL_CRITERIA_E.md (FROZEN), especially the source-overlap rule.
5. docs/STAGE_E_ML_DESIGN.md (DRAFT until Task 4), in full.
6. reports/stage_e1_freeze_rulings.md (FA-06 and its list of the members
   under the source-overlap fallback), reports/stage_e1_changes.md.
7. reports/stage_e1_purchase.json (every purchased file, its schema, date
   range and sha256) and reports/stage_e0_quotes.json.
8. The existing MES harness the build generalizes: rules/xfa_rules.py,
   data/cme_calendar.py, data/session.py, data/build_mes_bars.py,
   data/validate.py, data/adapter.py, sim/fill_model.py, funnel/power_gate.py,
   and the Stage D.1f calendar check (reports/stage_d1f_calendar_check.md).
9. reports/stage_e0_topstep_facts.md and .json (commissions F3.6 and F3.7,
   volatility caps, sessions, the price-limit rule).

============================================================
GUARDRAILS
============================================================

CLAUDE.md invariants apply in full. This stage adds:

- Order: the ML freeze commit (Task 4) comes before any process opens a
  purchased price or order-book file for anything beyond E.1's integrity
  fields. Tasks 5 to 9 and 12 start only after it. Tasks 2 and 10, and the
  code-only parts of Tasks 5 to 7 (writing modules and tests on synthetic
  data), may start earlier.
- The freeze holds: `sha256sum` of every file in reports/stage_e1_freeze.json
  matches at start and at end. A mismatch stops the session.
- Research-window data only: every bar, spread and move computed in this
  session comes from trade dates 2025-04-01..2026-06-19 in the step 1
  files. No file for any other date range exists for the new products, and
  none is created.
- What may be computed from research-window data: bars and their
  validation, calendar checks against bars, the D8 cost tables, the D2
  per-contract risk r_c and sizing, and the D3 segment moves E|m_T| for the
  funnel. What may not: any member's signal, trade or P&L, any correlation
  or return statistic beyond those D2, D3 and D8 define, and any chart or
  summary of prices. The return document lists every quantity computed
  from research-window data.
- Spend: none. `git diff` of ledger/databento_spend.jsonl is empty at the
  end.
- Holdout status at start and end: `uv run python -m data.holdout status`.
  Both stay all_ok with unlocks_logged 0.
- MES regression: every existing MES test passes unchanged. The rules
  engine, calendar and bar code keep MES's results bit-identical. A test
  that fails is fixed in the new code, never weakened.
- Compute: the overnight profile. Check available memory before each heavy
  job and write the estimate into the STATE file.
- REGISTRATION.md stays 0 bytes. No TopstepX reference of any kind.

Start and end checks, with output quoted verbatim in the return document:
`git status --short`, `git log --oneline -3`, the holdout status, `wc -c
REGISTRATION.md`, the freeze-manifest check, `uv run pytest -q` (expected
at start: 2 failed, 1010 passed, 1 xfailed, the two known D.1f calendar
tests).

============================================================
TASK 0: STARTUP
============================================================

- Owner: lead.
- Inputs: the context files.
- Output: reports/stage_e2a_STATE.md, and the estimate ETA table in chat
  and in the STATE file, with the build rows sized from a probe (time one
  month of one product's bar build before sizing the rest).
- Done when: the start checks are recorded, HEAD is 1b54dc1 or a
  descendant with a clean tree, and the freeze manifest verifies.
- Failure path: a dirty tree, a manifest mismatch, a holdout status other
  than all_ok, or an unexpected test failure stops the session with a
  named refusal.

============================================================
TASK 1: APPLY THE USER'S ML-ROUTE DECISIONS (LEAD)
============================================================

- Owner: lead.
- Inputs: docs/STAGE_E_ML_DESIGN.md, the decisions below.
- Output: the edited design, reports/stage_e2a_ml_changes.md (every edit
  with old text, new text and the decision that requires it), and a
  docs/DECISIONS.md entry dated 2026-09-25 listing V1 to V9.
- Done when: every decision maps to at least one logged edit or a logged
  "no edit needed", and no edit maps to no decision.
- Failure path: a decision that cannot be applied without a new design
  choice is logged as a question for the user and left unapplied.

The user's decisions (planning chat, 2026-09-25, accepting the planning
chat's recommendations on the E.1 draft):

- V1. M1 accepted: train, tune, normalize and distil only on S_X..2024-02-29,
  never touch March 2024 or holdout-2, test the frozen distilled rules once
  on the research window, holdout-2 stays the final gate. The route buys
  the full step 2 range (2019-05..2025-03) of one contract per exposure,
  holdout-2 sealed on arrival. Funding is pending: the user will top up
  acct-2. No purchase in E.2a.
- V2. M2 accepted: one pooled model per challenger across the 31
  exposures, evidence counted in trade dates.
- V3. M3 accepted: LightGBM plus one small LSTM, 36 configurations in
  total, as listed. The TCN stays dropped.
- V4. M4 accepted: the three horizons, the feature list, the 1.5 x cost
  stress.
- V5. M5 accepted: depth-2 surrogate rules, at most 2 per cluster and 16
  in total, the block-6 pre-test.
- V6. M6 accepted: one trial per tested rule, the route as its own family
  at alpha 0.05 / (K + 1).
- V7. M8 amended: the LSTM trains on this machine's NVIDIA RTX 3050 Laptop
  GPU (4 GB VRAM, found 2026-09-25), not on the Windows PC. The Windows PC
  is dropped from the route. Trees run on the CPU. Both follow the
  overnight profile in CLAUDE.md. Replace M8's Windows PC text and its
  time estimates' GPU assumptions accordingly, and state that E.2b's probe
  re-plans the LSTM's batch size to leave at least 0.5 GB of VRAM free.
- V8. M9 accepted: the route's buy and train sessions run after E.2b,
  beside K2's screening, and the route's test runs once all its rules are
  frozen, before K8.
- V9. Also accepted from the E.1 return: F-1 (31 traded exposures, as
  already written in the frozen D1), F-5 (K2-aucpost-01's 5-minute lag,
  which review R-15 found supported), and FA-06 option: the source windows
  of the source-overlap members may be recorded before any confirmation
  read, as a separate audited amendment that can only remove a
  source-overlap label, never add a member, change a rule, or add a label
  (Tasks 2 and 11).

============================================================
TASK 2: SOURCE WINDOWS (WORKER)
============================================================

- Owner: SourceWindowReader-OpusHigh, worker-high on opus. Starts at Task
  0, parallel with Task 1.
- Inputs: reports/stage_e1_freeze_rulings.md (the FA-06 member list), the
  catalog entries of those members, their cited sources in the E.0
  research logs and reports/stage_e0_source_registry.jsonl.
- Output: reports/stage_e2a_source_windows.md and .json: for each listed
  member and each source it rests on, the source's data sample period
  (first and last date), the quoted passage that states it, the URL or
  DOI, and the retrieval status. A period that cannot be pinned to a
  quoted passage is recorded as "unknown".
- Done when: every member on the list has a row for every source it
  cites.
- Failure path: a blocked source, or a WebSearch budget notice, is logged
  with the time, and the row stays "unknown". The worker never estimates a
  period from memory.

============================================================
TASK 3: ML FREEZE AUDIT (FABLE XHIGH)
============================================================

- Owner: DeclarationAuditor-FableXHigh, worker-xhigh on fable. It wrote
  none of the work it audits.
- Inputs: `git diff 1b54dc1 -- docs/STAGE_E_ML_DESIGN.md`,
  reports/stage_e2a_ml_changes.md, V1 to V9 as quoted in this prompt, and
  the frozen design.
- Output: reports/stage_e2a_declaration_audit.md, Part 1, each finding
  graded BLOCKING, SHOULD FIX or NOTE, with file and line.
- Done when: the auditor has checked that every change maps to a decision
  and every decision is applied, that the frozen ML design leaves no
  choice to be made after training data is seen (grids, selection,
  distillation, pre-test and trial accounting fully specified), that the
  partition never lets a research-window, embargo or holdout-2 date into
  training, tuning, normalization or distillation, and that nothing in it
  contradicts the frozen Stage E design.
- Failure path: if Fable is unavailable, stop as the Usage paragraph says.

============================================================
TASK 4: RULINGS, ML FREEZE AND COMMIT (LEAD)
============================================================

- Owner: lead.
- Inputs: the audit.
- Output: reports/stage_e2a_ml_freeze_rulings.md, a FROZEN header in
  docs/STAGE_E_ML_DESIGN.md ("FROZEN by Stage E.2a on <date>, manifest
  reports/stage_e2a_ml_freeze.json"), the manifest (sha256 of the design,
  the changes log, the audit's Part 1 and the rulings, with HEAD and the
  creation time), and one commit.
- Done when: every BLOCKING and SHOULD FIX finding has a ruling and its
  fix, the manifest verifies by script, and one commit on main holds
  exactly the ML design, the changes log, the audit, the rulings, the
  manifest and docs/DECISIONS.md, with a message naming the manifest
  sha256 and "Stage E ML route freeze", ending with this repository's
  attribution lines.
- Failure path: a BLOCKING finding that cannot be fixed within V1 to V9
  stops the freeze. Then no research-window bar is read in this session,
  and the finding goes to the user.

============================================================
TASK 5: PER-PRODUCT RULES ENGINE (D11.1)
============================================================

- Owner: RulesCoder-OpusXHigh, worker-xhigh on opus (or ultracode's
  fan-out at the lead's tier).
- Inputs: rules/xfa_rules.py, the frozen D9 and D11.1, the Topstep facts
  (F3.6 and F3.7 commissions, volatility caps, sessions, the price-limit
  rule).
- Output: the rules engine generalized per product for the 50K XFA only:
  tick size and tick value per product, lot-equivalent weights (minis 1,
  micros 0.1, SIL 0.2, MBT 1), the 1-lot-equivalent member cap (D9.5),
  per-group flatten times (15:08 CT, grains 13:18 with the 07:45-08:30
  pause, livestock 13:03, early closes minus 15 minutes), the price-limit
  proximity rule (D9.7) with per-product limit tables, the volatility caps
  and the CPI window (D9.11, D9.12), and the per-product commission table
  (D8, with MCL and MNG at the 2026-10-01 rates). 100K, 150K and the Daily
  Loss Limit option stay out of scope. Tests with known answers for every
  product group, and MES's existing tests unchanged.
- Done when: the new tests pass, and every existing rules test passes
  unchanged.
- Failure path: a rule the Topstep facts do not state (for example the
  lot counting of QM, QG and E7, which Topstep has not published) is
  encoded as the frozen design's conservative reading and flagged in the
  return document. It is never guessed silently.

============================================================
TASK 6: GROUP CALENDARS (D10, D11.3)
============================================================

- Owner: CalendarBuilder workers, worker-xhigh on opus, one per group:
  rates, FX, energy, metals, grains, livestock, crypto, and the equity
  group's fix. At most 4 at once.
- Inputs: data/cme_calendar.py (the interface and grading), the D.1f
  CalendarChecker method (reports/stage_d1f_calendar_check.md: cmegroup.com
  through Wayback copies, every quote checked by script as a verbatim
  substring), the frozen D10.
- Output: one calendar module per group with the same interface as
  data/cme_calendar.py, covering every CME trade date 2019-05-01 to
  2026-06-19: holidays, full closures, early halts and early closes, each
  entry citing CME's own published schedule for that group and year and
  graded as data/cme_calendar.py grades entries. Session tables per group,
  including the grain session with its pause and the livestock session,
  and any CME session-hour change in 2019-2026, dated. The crypto calendar
  splits at 2026-05-29 (24/7 trading, weekend trading assigned to the next
  business day). The equity group: fix 2024-07-04 in data/cme_calendar.py
  to the 12:00 CT halt CME's trading-hours capture gives
  (reports/stage_d1f_calendar_check.md), and upgrade the 2019-07-03 and
  2023-07-03 grades to cme, with the citations D.1f found. Each group's
  sources are logged in reports/stage_e2a_calendar_sources.md.
- Done when: each group module passes a step-4b-style validation against
  that group's research-window bars (every weekday with no bars is a
  listed full closure, every early halt matches the observed last minute
  plus one, every listed 2025-2026 entry is observed), and the 2019-2024
  entries, which have no bars on disk yet, are marked "validated against
  CME schedules only, bar check pending the step 2 purchase".
- Failure path: a discrepancy between a cited CME schedule and the bars is
  diagnosed as D.1f's Task 3 did (thin trading is never fixed by a fake
  early close). An entry that cannot be sourced stays graded "inferred"
  and is flagged. MES's holdout-2 count moves from 258 to 259 with the
  2024-07-04 fix. Record that, and do not touch the sealed chunks.

============================================================
TASK 7: RESEARCH-WINDOW BAR BUILDS (PART OF D11.4)
============================================================

- Owner: BarsCoder-OpusXHigh, worker-xhigh on opus.
- Inputs: the step 1 ohlcv-1m files (reports/stage_e1_purchase.json),
  data/build_mes_bars.py and data/validate.py as the template, the group
  calendars from Task 6, the symbology and roll information in the files.
- Output: a generalized bar builder and one research-window bar parquet
  per admissible contract (read-only, with the purchase files' sha256 and
  the calendar module's sha256 stamped in), roll boundaries and roll
  blackout dates per product (monthly-expiry products roll about twelve
  times a year), vendor-degraded dates per product, and a build summary
  per product in reports/stage_e2a_bars.json: bars, trade dates,
  validation failures, drops by cause. The MES builder's output for MES is
  unchanged (a regression test compares it bit for bit).
- Done when: every admissible contract has a validated research-window
  parquet, or a named refusal, and the coverage check of D9 (member-level
  coverage at least 0.95) can be computed from the parquets in E.2b.
- Failure path: a product whose bars fail validation is reported with the
  cause and left unbuilt. It is not patched by hand.

============================================================
TASK 8: COST MODEL (D8, D11.2)
============================================================

- Owner: CostCoder-OpusXHigh, worker-xhigh on opus.
- Inputs: the mbp-1 sample (five dates), the Task 5 commission table, the
  Task 6 session tables and 30-minute CT buckets.
- Output: the calibration code, run once, and a frozen cost table per
  admissible contract in reports/stage_e2a_costs.json and .md: the
  commission, s_b per bucket (the time-weighted mean quoted half-spread in
  ticks over the five dates), the depth term at q_c (from Task 9's sizes,
  so this part runs after Task 9's r_c), the fewer-than-3-dates fallback,
  the event-window rule, and the round-turn cost per bucket. Nothing is
  smoothed or fitted.
- Done when: every admissible contract has a table, a known-answer test on
  a synthetic book passes, and the MES table reproduces the D.1 cost model
  within the documented differences (two days of ticks against five days
  of mbp-1), stated as figures.
- Failure path: a bucket or product the rule cannot calibrate is filled by
  the rule's own fallback and flagged. No extra sample dates are bought.

============================================================
TASK 9: VEHICLE CHOICE (D2, D11.10)
============================================================

- Owner: lead, with VehicleCoder-OpusXHigh (worker-xhigh on opus) for the
  code.
- Inputs: the research-window bars, the cost tables, R* = $360.68, the
  frozen D2 rule, the U7 constraint (M6E and M6A are not candidates until
  Topstep answers).
- Output: reports/stage_e2a_vehicles.json and .md: for every admissible
  contract r_c, q_c, rho_c, the cost per dollar of risk, and for every
  exposure the chosen vehicle, the "undersized" flag, or "no candidate"
  (not traded in Stage E). Frozen by hash in the return document.
- Order inside the task: r_c and q_c come first, from the bars alone, so
  that Task 8 can compute its depth term at q_c. The cost per dollar of
  risk and the vehicle choice follow once Task 8's tables exist.
- Done when: the D2 rule is applied mechanically to every exposure, with
  the arithmetic written out for each.
- Failure path: an exposure with no candidate is recorded as not traded,
  as the frozen D2 says. The lead does not choose a vehicle by judgment.

============================================================
TASK 10: CARRIED TEST FIXES (D14, D11.11)
============================================================

- Owner: TestFixer-SonnetMed, worker-medium on sonnet (mechanical,
  already-decided edits).
- Inputs: tests/test_d1f_calendar_build.py, the frozen D14 table.
- Output: the verbatim test pointed at both extraction files, and the
  end-to-end test skipped when the real confirmation parquet exists, with
  a reason string.
- Done when: the full suite shows 0 failures.
- Failure path: if either edit would change what the test protects, the
  worker stops and reports.

============================================================
TASK 11: SOURCE-WINDOW AMENDMENT (LEAD, THEN FABLE RESUMED, THEN COMMIT)
============================================================

- Owner: lead, then DeclarationAuditor-FableXHigh resumed with SendMessage.
- Inputs: Task 2's output, the frozen NULL_CRITERIA_E source-overlap rule.
- Output: reports/stage_e2a_source_window_amendment.md: for each listed
  member, the label before and after under the frozen rule, applied
  mechanically to the recorded windows. A member keeps its label when any
  of its sources overlaps the confirmation window or is "unknown". Then
  Part 2 of reports/stage_e2a_declaration_audit.md (the auditor checks
  each row against Task 2's quoted passages and the rule), the lead's
  rulings, a docs/DECISIONS.md line, and one commit holding exactly the
  amendment, Task 2's files, the audit, the rulings and DECISIONS.md.
- Done when: the commit exists and no frozen file changed.
- Failure path: a row the auditor cannot confirm keeps its label.

============================================================
TASK 12: INDEPENDENT RECOMPUTATION (FABLE RESUMED)
============================================================

- Owner: DeclarationAuditor-FableXHigh, resumed with SendMessage.
- Inputs: the research-window parquets, the mbp-1 sample, the cost tables,
  the vehicle file, the epsilon file, the frozen D2, D3 and D8.
- Output: Part 3 of reports/stage_e2a_declaration_audit.md: an independent
  recomputation, in the auditor's own code, of r_c, q_c, rho_c and the
  chosen vehicle for every exposure, the translated epsilon for every
  exposure, the cost table for at least four products from the raw mbp-1
  files (one each from rates, energy, grains and crypto), and the funnel
  epsilon for at least three exposures. Each item VERIFIED, VERIFIED WITH
  NOTES or DISCREPANCY.
- Done when: every item has a verdict.
- Failure path: a DISCREPANCY is ruled on by the lead in writing. A
  vehicle or epsilon with an unresolved discrepancy is marked "unverified"
  and E.2b may not freeze it.

============================================================
TASK 13: FUNNEL RE-DERIVATION OF EPSILON (D3, D11.8)
============================================================

- Owner: FunnelRunner-OpusXHigh, worker-xhigh on opus. It runs before Task
  12's epsilon items.
- Inputs: funnel/power_gate.py, the frozen D3 (8,000 careers per cell,
  robust verdict, both payout paths, the 120 grid cells plus D.1e's 100
  extension points), each exposure's segment moves E|m_T| (T = 1, 2, 4, 8)
  measured on the research window at q_c, and its modelled round-turn
  cost.
- Output: reports/stage_e2a_epsilon.json and .md: per traded exposure the
  translated epsilon, the funnel-derived epsilon, the operative minimum,
  and the flag where no cell passes.
- Done when: every traded exposure has its three figures, and the job's
  compute record (threads, peak memory, time) is in the STATE file.
- Failure path: the job is resumable per exposure. An exposure that fails
  is reported, and the others continue.

============================================================
DELEGATION PLAN
============================================================

| Task | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup, probe, ETA | lead | opus | xhigh | first | gates the session |
| 1 ML decisions | lead | opus | xhigh | parallel with 2 and 10 | the user decided, the lead applies |
| 2 Source windows | SourceWindowReader-OpusHigh | opus | high | from the start | literature research runs on opus |
| 3 ML freeze audit | DeclarationAuditor-FableXHigh | fable | xhigh | after 1 | an independent model on a declaration |
| 4 Rulings, freeze, commit | lead | opus | xhigh | after 3 | reserved to the lead |
| 5 Rules engine | RulesCoder-OpusXHigh | opus | xhigh | code from the start, tests after 4 | rules/ work |
| 6 Calendars x8 | CalendarBuilder-<Group>-OpusXHigh | opus | xhigh | at most 4 at once, bar checks after 4 | sourced data work in data/ |
| 7 Bar builds | BarsCoder-OpusXHigh | opus | xhigh | after 4 and each group's calendar | data/ pipeline |
| 8 Cost model | CostCoder-OpusXHigh | opus | xhigh | after 4, depth term after 9's r_c | calibration, frozen |
| 9 Vehicle choice | lead with VehicleCoder-OpusXHigh | opus | xhigh | after 7 and 8 | a frozen mechanical rule |
| 10 Test fixes | TestFixer-SonnetMed | sonnet | medium | any time | mechanical, decided edits |
| 11 Source-window amendment | lead, then DeclarationAuditor-FableXHigh resumed | opus, fable | xhigh | after 2 | a declaration, audited |
| 13 Funnel epsilon | FunnelRunner-OpusXHigh | opus | xhigh | after 9 | heavy compute, overnight profile |
| 12 Recomputation | DeclarationAuditor-FableXHigh resumed | fable | xhigh | after 9 and 13 | verdict-bearing numbers |
| Return document | lead | opus | xhigh | last | reserved to the lead |

At most 4 workers at once. Ultracode's own fan-out, if the lead uses it,
counts toward that limit and stays at the lead's tier (opus xhigh). The
Fable and sonnet workers are spawned through the worker files with the
model passed explicitly.

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

- The ML freeze (Task 3), the source-window amendment (Task 11) and the
  build numbers (Task 12) are checked by DeclarationAuditor-FableXHigh,
  which produced none of them.
- The lead rules on every finding in writing and applies the fixes. It
  never re-runs a check to get a different answer.
- If Fable runs out, the checks stay pending in the STATE file, and no
  vehicle or epsilon is treated as final.

============================================================
WHAT NOT TO DO
============================================================

- No research-window file opened for prices before the ML freeze commit.
- No member signal, trade, P&L or screening statistic computed.
- No purchase, no cap change, no ledger line.
- No edit to any file in reports/stage_e1_freeze.json.
- No MES result changed, and no existing test weakened.
- No model fitted.
- No push, and no commit beyond the two named.
- No write to REGISTRATION.md. No edit to docs/NULL_CRITERIA.md.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.2a_RETURN.md. The planning chat reads this one file to
review the session. Fixed sections, in order:

1. Verdict summary, at most 200 words: what was done and what was not, the
   ML freeze manifest sha256 and both commit hashes, the vehicles and
   epsilon per exposure in one line each or a short table, how many
   exposures are traded, undersized or not traded, and whether E.2b is
   unblocked.
2. Guardrail evidence: the start and end checks verbatim, the freeze
   manifest check, the list of every quantity computed from
   research-window data and the script that computed it, `git status
   --short` and `git diff --stat` at the end, and an empty ledger diff.
3. Results per task: each artifact path, its test count and what each
   test proves, the calendar discrepancies and their diagnoses, the bar
   build summary per product, the cost tables' headline per product, the
   vehicle arithmetic, the epsilon table, the source-window amendment's
   before-and-after labels, and the test fixes.
4. Delegation record: one row per spawn with agent name, worker file,
   model, effort, objective, status and deviations, and how much of the
   work ultracode's fan-out did.
5. Verification: each Fable finding in Parts 1 to 3, the lead's ruling and
   the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. What the next session must do first: the planning chat's commits and
   push, the frozen files and hashes, the funding the user owes for the
   older history, the Topstep answer on M6E and M6A, and any blocker for
   E.2b.
8. Session cost: the final ETA table (one row per task and per spawn,
   actual start and end, time taken, tokens from the transcripts, status),
   the per-model token table, and the ultracode share, per CLAUDE.md.
   Never estimated.

Also write one short dated progress.md entry that points to the return
document, and one line in docs/STAGES.md.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
