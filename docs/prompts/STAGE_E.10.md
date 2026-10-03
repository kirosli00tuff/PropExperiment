STAGE E.10 "LOW-FREQUENCY FULL-SESSION HOLDS: LITERATURE RESEARCH AND A DRAFT K9 CATALOG BUILT AROUND THE COST WALL (NO MARKET DATA READ, NO PURCHASE)"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage E screened 198 trials across all eight clusters (E.3 to
E.9). One reached confirmation (K4-ngpre-01) and failed it. Every other
Tier A pass was economically tiny or rested on one or two days. The
pattern across the returns: most trials lost roughly their own round-trip
cost, so for intraday rules under retail costs the moves the rules caught
were smaller than what it costs to trade them. This session researches one
targeted family the program has not tried: low-frequency, full-session
holds. A member trades rarely (at most about two entries a week per
product), only when a pre-stated rare condition holds, holds for hours up
to the whole session the Topstep rules allow (from the 17:00 CT Globex
open of the trade date to the 15:08 CT flatten), and aims for a move
several times its round-trip cost. A rule may run on several products,
one trial per product, to reach enough trading days. The session searches
the literature, writes a draft catalog for a new cluster K9 from published
evidence only, drafts the design amendment K9 needs, and has an
independent Fable worker review it adversarially. It reads no market data
and buys nothing. The user decides the open design points, and a later
session (E.11) applies the decisions and freezes the catalog, the E.1
pattern.

Decisions in force: docs/DECISIONS.md V17 as amended by V19 (this research
run comes before the ML route), and V18 (any new screen states a minimum
trade count before any data is read).

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: the work is literature research, mechanism
judgment and catalog writing. CLAUDE.md routes research readers to opus
at high (Sonnet failed E.0's research checks) and reserves design
judgment for the lead. The silent failure to guard against is a catalog
that looks new but repeats a family Stage E already tested, or that was
tuned, knowingly or not, to Stage E's research-window results. An
independent Fable review checks both. Ultracode stays off: at most four
readers at once, routed through the worker files.

Usage: follows CLAUDE.md's context-hygiene rules, including the research
rules: readers write pages to disk and grep them, and only quoted lines
enter context. Use CLAUDE.md's page-fetch fallback (WebFetch, then
Scrapling `get`, then `fetch`, `stealthy-fetch` only where a site's terms
allow automated access). Firecrawl is not used. For scholarly search, use
the Semantic Scholar API with the key in .env under
SEMANTIC_SCHOLAR_API_KEY (send it as the x-api-key header, never print or
log it) and OpenAlex with the polite-pool email in .env under
OPENALEX_EMAIL (sent as the mailto parameter). If either variable is
missing, continue without it, slower, and log it. Fable is used by one
worker, CatalogReviewer-FableXHigh (Task 5). Compute: the ThinkPad. E.0
(eight clusters) was far larger. Expect about 3 hours.

Do not stop to ask. Decide, log the choice under Open choices in the return
document, and continue. The only stops are the ones this prompt names, a
decision that cannot be undone and could reasonably go either way, or a
guardrail conflict.

============================================================
SCOPE
============================================================

This stage does:
- write the K9 design target and the exclusion list of families Stage E
  already tested (Task 1)
- search the literature for low-frequency, multi-hour, intraday-bounded
  effects in futures (Tasks 2 and 3)
- write a draft K9 catalog of fully specified members from published
  evidence only (Task 4)
- draft the design amendment K9 needs (Task 4)
- have the catalog reviewed adversarially by Fable (Task 5)
- write the return, with every open design point listed for the user
  (Task 6)

This stage does NOT:
- read any bar, quote, cost sample or market data file, in any window, or
  open any Stage E screen or confirmation record for its numbers. The
  frozen cost tables (reports/stage_e2a_costs.json and the D8 text) and
  the E.0 to E.9 return documents' prose may be read, for costs and for
  the list of families already tested.
- choose any parameter from Stage E results. Every literal in a member
  comes from its source or from a stated design rule fixed in Task 1.
- buy anything, call Databento, or edit data/config.py
- freeze anything, write any member code, or edit any frozen file,
  manifest, docs/STAGE_E_DESIGN.md (the amendment is drafted in a separate
  file), docs/NULL_CRITERIA.md or docs/NULL_CRITERIA_E.md
- touch the ML route, holdout-1 or holdout-2, live/, ops/, or any
  TopstepX credential or API
- write to REGISTRATION.md (it stays 0 bytes)
- push. The session makes exactly one commit (Task 6).

============================================================
CONTEXT TO READ FIRST
============================================================

Read by section, as CLAUDE.md's context-hygiene rules require.

1. CLAUDE.md (the research rules, the page-fetch fallback, the WebSearch
   budget) and docs/ORCHESTRATION.md.
2. docs/DECISIONS.md V13 to V19.
3. reports/stage_e0_catalog.md, the member index of every cluster, and
   the section 1 headings of reports/stage_e0_catalog_K1.md to K8.md: the
   families already tested. Read the headings and one-line mechanisms
   only.
4. docs/STAGE_E_DESIGN.md (FROZEN): D1 (the traded exposures), D2 and the
   E.2a vehicle table (q_c per exposure), D3 and reports/stage_e2a_epsilon.md
   (eps per exposure), D5 (the screen and the tiers), D6 (each product's
   session row O, C, F), D8 (costs) and D9 (the constraint set).
5. reports/stage_e2a_costs.json (the frozen round-trip cost per contract,
   by product and by 30-minute bucket) and reports/stage_e2a_vehicles.md.
6. reports/stage_e0_topstep_facts.json: the flatten time, the lot limits,
   the payout rules (Standard: 5 winning days of $150 or more. Consistency:
   no single day above 40% of total profit).
7. The E.0 research logs (reports/stage_e0_research_K*.md), headings only,
   to avoid re-reading sources E.0 already logged.

============================================================
GUARDRAILS
============================================================

CLAUDE.md invariants apply in full. This stage adds:

- No market data of any kind, no Stage E result figures. A worker that
  needs a number it cannot source from the literature or the frozen cost
  and rules tables stops and reports it.
- Every member's evidence is quoted verbatim from its source with a
  passage ID, as in E.0. A member without a quoted mechanism is not
  written.
- Every web page used as evidence is saved raw under
  reports/stage_e10_research/ with its URL, UTC fetch time and sha256 in
  the log.
- No key printed, copied or logged. REGISTRATION.md stays 0 bytes. No
  TopstepX reference of any kind.
- Holdout status at start and end: all_ok, 0 unlocks. The ledger is
  unchanged.

Start and end checks, quoted verbatim in the return: `git status
--short`, `git log --oneline -3`, the holdout status, `wc -c
REGISTRATION.md`, the ledger total.

============================================================
TASK 0: STARTUP
============================================================

- Owner: lead.
- Output: reports/stage_e10_STATE.md and the estimate ETA table. The
  STATE file names, after every task, the task finished and the next
  task (the auto-retry launcher resumes from it).
- Done when: the start checks pass and HEAD is the commit holding this
  prompt or a descendant with a clean tree. Note whether
  SEMANTIC_SCHOLAR_API_KEY and OPENALEX_EMAIL exist (names only).

============================================================
TASK 1: DESIGN TARGET AND EXCLUSIONS (LEAD)
============================================================

- Owner: lead.
- Output: reports/stage_e10_design_target.md:
  (a) The cost wall per exposure: from the frozen cost table, the
  round-trip cost in ticks per contract of each traded exposure's vehicle,
  its eps_X, and the minimum gross move per trade a member must target:
  M_X = 3 x round-trip cost, and the per-trade size needed to reach eps_X
  per trade date at the member's stated frequency (the C11 arithmetic of
  the earlier catalogs). Both are design rules, fixed here before any
  source is read.
  (b) The shape every K9 member must have: at most about two entries a
  week per product, one position at a time, entry and exit inside one
  trade date, hold of at least two hours, flat by F = 15:08 CT, market
  orders, size q_c (D2), every D9 constraint.
  (c) The exclusion list: every family Stage E already tested, by
  mechanism, from the catalogs' headings (the three core ports, the event
  members by release, the fixes, overreaction reversal, month-end, roll
  and expiry, cross-market leads). A K9 member must differ in mechanism,
  not only in parameters or frequency.
  (d) The proposed screen for K9, for the user to decide: D5 (mean > 0 and
  daily t >= 1.0) plus a minimum trade count per trial in the research
  window (V18), proposed at 30 trips, with the arithmetic for 299
  research dates.
- Done when: every number traces to a frozen table or a stated rule.

============================================================
TASK 2: SEARCH PLAN (LEAD)
============================================================

- Owner: lead.
- Output: reports/stage_e10_search_plan.md: the topics, each with its
  query strings for Semantic Scholar, OpenAlex and the web, and the reader
  that owns it. Topics to cover at least: regime-conditioned session drift
  (after volatility spikes, after large prior-day moves, after range
  compression), overnight-to-day continuation or reversal over full
  sessions, calendar effects with full-session holds that Stage E did not
  test (pre-holiday, day-of-week, turn-of-week), commodity-specific
  supply or inventory regimes, term-structure or basis signals read from
  the futures curve, and conditional time-series momentum at the daily
  scale applied inside one session. Each topic's link to the cost wall is
  stated: why its move could be large relative to cost.
- Done when: every topic has an owner and queries.

============================================================
TASK 3: LITERATURE READERS (WORKERS)
============================================================

- Owners: up to four readers in parallel, LitReader-<topic>-OpusHigh,
  worker-high on opus, one topic group each.
- Inputs: the search plan, the exclusion list, the design target.
- Output: one log per reader, reports/stage_e10_research_<topic>.md: each
  source with its bibliographic record, its sample window, the market and
  frequency studied, the verbatim passages (with IDs) stating the effect,
  its size and its costs if given, any conflicting evidence, and the
  reader's note on whether it fits the K9 shape and clears the cost wall.
  Search summaries are never logged as retrieved text (E.0's failure).
- Done when: each topic has been searched to saturation or its budget,
  and each candidate mechanism has at least one full-text or abstract
  quote.
- Failure path: a reader that hits the WebSearch budget notice stops and
  logs it with the time (CLAUDE.md).

============================================================
TASK 4: THE DRAFT CATALOG AND DESIGN AMENDMENT (LEAD)
============================================================

- Owner: lead. Catalog writing may go to CatalogWriter-OpusXHigh
  (worker-xhigh on opus) from the lead's rulings.
- Output:
  (a) reports/stage_e10_catalog_K9.md and .json, in the E.0 catalog
  format: per member the mechanism with quoted evidence, the traded
  exposures (only those E.2a admits), the exact rule (rare condition,
  decision time, entry, exit, hold, flatten, size), every literal with its
  source, the expected frequency from calendar arithmetic (no price data),
  the target move against M_X, the source windows and the source-overlap
  label (NULL_CRITERIA_E section 3), the Topstep checks, and the trial
  count. A trial budget: at most 40 trials in total, so that program N
  (198 now) and the DSR hurdle stay bounded.
  (b) docs/STAGE_E_DESIGN_K9_DRAFT.md: the amendment K9 needs, as
  proposals for the user: K9 as its own Holm family, which raises the
  maximum K from 9 to 10 (V14 (b)). The minimum trade count (Task 1 (d)).
  The trial budget. How K9's confirmation and holdout-2 purchases would
  work per exposure (the step 2 path, with no quote run in this session).
- Done when: every member is fully specified with no open literal, or its
  open point is listed for the user.

============================================================
TASK 5: ADVERSARIAL REVIEW (FABLE XHIGH)
============================================================

- Owner: CatalogReviewer-FableXHigh, worker-xhigh on fable. It wrote none
  of the catalog.
- Output: reports/stage_e10_catalog_review.md, findings graded BLOCKING,
  SHOULD FIX or NOTE.
- Done when: the reviewer has checked, for every member:
  - that the quoted passages exist in the saved sources and say what the
    entry claims
  - that the mechanism differs from every family on the exclusion list
  - that no literal could have come from Stage E's results rather than
    its source
  - the frequency and cost-wall arithmetic
  - the K9 shape (hold, flatten, frequency, D9)
  - the source-overlap label and the trial count
- Failure path: if Fable is unavailable, stop before Task 6 and mark the
  catalog unreviewed.

============================================================
TASK 6: RULINGS, RETURN AND COMMIT (LEAD)
============================================================

- Owner: lead.
- Output: reports/stage_e10_catalog_rulings.md (a ruling on every
  BLOCKING and SHOULD FIX finding, applied to the draft), the return
  document, and one commit holding exactly this stage's research logs,
  saved sources, design target, search plan, draft catalog, design draft,
  review and rulings, with the message "Stage E.10 K9 research and draft
  catalog" and this repository's attribution lines.
- Done when: the commit exists.

============================================================
DELEGATION PLAN
============================================================

| Task | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup, ETA | lead | opus | xhigh | first | gates the session |
| 1 Design target, exclusions | lead | opus | xhigh | after 0 | design rules fixed before any source, reserved to the lead |
| 2 Search plan | lead | opus | xhigh | after 1 | scope judgment |
| 3 Literature readers | LitReader-<topic>-OpusHigh (up to 4) | opus | high | parallel | research readers run on opus (CLAUDE.md, E.0 lesson) |
| 4 Catalog, design draft | lead, with CatalogWriter-OpusXHigh | opus | xhigh | after 3 | mechanism judgment and exact rule text |
| 5 Adversarial review | CatalogReviewer-FableXHigh | fable | xhigh | after 4 | an independent model checks novelty, evidence and data hygiene |
| 6 Rulings, return, commit | lead | opus | xhigh | last | reserved to the lead |

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

============================================================
VERIFICATION
============================================================

- Every quoted passage is checked against its saved source by the Fable
  reviewer, which wrote none of the catalog.
- Every member is checked for novelty against the exclusion list and for
  data hygiene (no literal from Stage E's results).
- The lead rules on every finding in writing.

============================================================
WHAT NOT TO DO
============================================================

- No market data, no Stage E result figures, no Databento call.
- No member re-using a tested family with new parameters.
- No literal without a source or a Task 1 design rule.
- No freeze, no code, no edit to frozen files. The design amendment stays
  a draft for the user.
- No search summary logged as retrieved text.
- No push, no write to REGISTRATION.md, no key printed.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.10_RETURN.md. The planning chat reads this one file.
Fixed sections, in order:

1. Verdict summary, at most 250 words: the members found, by mechanism,
   the trials per exposure, the total against the 40-trial budget, how
   each clears the cost wall on paper, and the decisions the user owes.
2. Guardrail evidence: the start and end checks verbatim.
3. Results per task: the design target, the exclusion list, the search
   coverage (sources found, read, used), the catalog summary table, the
   design draft.
4. Delegation record: one row per spawn.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation: K9 as its own Holm
   family with maximum K = 10, the minimum trade count, the trial budget,
   any member to cut, and what E.11 (freeze) and E.12 (code and screen)
   will need.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

Also write one short dated progress.md entry and one line in
docs/STAGES.md.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
