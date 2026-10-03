STAGE E.13 "WHAT IS LEFT TO SEARCH: VENUES FOR MULTI-DAY HOLDS, NEW INFORMATION SOURCES, A BACKWARD NG REPLICATION DRAFT, AND A RANKED PLAN (RESEARCH AND SCOPING ONLY, NO DATA READ, NO PURCHASE)"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: ML route v2 failed Gate 0 in Stage E.12 (best pair NG h60, t_B
2.51 against a Holm bar near 3.6; the pooled edge negative), so v2 stops
and the program's N is 471. Across Stage E's nine clusters and v2,
price-based intraday signals on 28 futures, held 60 minutes or longer
and flat by 15:08 CT, show no edge after costs. The user wants to keep
searching (V24). This session does no market-data work. It researches
and scopes the three directions still open, then ranks them: (a) venues
that allow multi-day holds with automation, where the best-documented
futures premia (trend and carry) become reachable, including what a
personal micro-futures account needs; (b) information sources the
program has never used for intraday signals; (c) a backward replication
of the NG near-miss on 2010-2019 data, drafted and costed but not run.
The deliverable is a ranked plan with pre-registration drafts for the
top one or two, written so the next stage can freeze and run one.

Decisions in force: docs/DECISIONS.md V22 (income path), V23, V24 (v2
stops, N = 471, the scope of this stage, no re-mining of the 2019-2024
stores, no Gate 0 rerun), and the 2026-09-28 Phidias entry (a swing
account blocked by an automation ban, with a semi-automated question
for Phidias support still open).

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: the session is judgment-heavy research. The
silent failures to guard against: venue rules reported from marketing
pages or stale captures without dates, evidence quoted from memory
instead of a source, a ranking that favors what is easy over what has
evidence, and a replication draft that quietly reuses information from
the 2019-2024 result beyond the single pre-stated hypothesis. Web
research goes to Opus workers (high) per the 2026-09-24 rule. Fable
gives one adversarial review of the ranking.

Usage: follows CLAUDE.md's context-hygiene rules. The user runs this
unattended. The auto-retry launcher resumes it with "read the STATE file
first", so reports/stage_e13_STATE.md names, after every task, the task
finished, the files written and the next task. Expect 3 to 5 hours.

Do not stop to ask. Decide, log the choice under Open choices in the
return document, and continue. The only stops are the ones this prompt
names, a decision that cannot be undone and could reasonably go either
way, or a guardrail conflict. AskUserQuestion is not to be used: the
user is away.

============================================================
SCOPE
============================================================

This stage does:
- research venues for multi-day automated futures trading (Task 1)
- research the trend and carry evidence and size a personal micro
  account (Task 2)
- scope new information sources for intraday signals (Task 3)
- draft and cost a backward NG replication (Task 4)
- rank the candidates and draft pre-registrations for the top one or
  two (Task 5)
- get one adversarial Fable review (Task 6)

This stage does NOT:
- read any bar, quote, cost sample or market-data file of any window,
  or run any screen, model, Gate 0 or statistic on market data
- call Databento for anything but a quote-only run, which the frozen
  path ledgers at $0.00, and only if Task 4 needs a figure E.12 did not
  already quote
- buy anything, raise any cap, or change any frozen file or harness
- contact any firm, open any account, or log in anywhere. Support
  questions are drafted for the user, never sent.
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push. The session makes exactly the one commit Task 7 names.

============================================================
CONTEXT TO READ FIRST
============================================================

Read by section, as CLAUDE.md's context-hygiene rules require.

1. CLAUDE.md (including the page-fetch order and its terms rule) and
   docs/ORCHESTRATION.md.
2. docs/DECISIONS.md: the 2026-09-28 Phidias entry, V19 to V24.
3. reports/E.12_RETURN.md sections 1, 3 (Task 2b and Task 6) and 7.
4. reports/E.10_RETURN.md sections 1 and 3 (the cost wall and the
   design target), and reports/stage_e10_catalog_K9.md's source list.
5. docs/STAGE_E_ML_V2_DESIGN.md V2.0 (economics and power), V2.1 (the
   universe, price paths and costs), V2.3 (the signal library: what the
   program has already used), V2.2b (Gate 0's family B rule).
6. reports/stage_e0_topstep_facts.json and reports/stage_e12_topstep_150k.md.
7. The E.12 quote record for the 2010 extension
   (reports/stage_e12_purchase.md and its JSON), for NG's figure.
8. The research report summary in V22 and the findings F1 to F13 in
   docs/prompts/STAGE_E.11.md.

Reading Stage E return documents for what was tested and what failed is
allowed. Opening any bar file or result table to compute anything new is
not.

============================================================
GUARDRAILS
============================================================

- Every claim about a firm's rules, a broker's terms, a data source's
  cost or a published result carries a source: URL, fetch date, and a
  short quote. A fact with no source is marked UNSOURCED and never
  drives a ranking.
- Fetch order per CLAUDE.md. A site whose terms forbid automated access
  (E.12's CME case) is not fetched by automation: use what a plain
  WebFetch returns, a Wayback capture, or record the gap.
- Prop-firm rules change often. Each firm's entry records the page date
  or "no date shown", and the help-centre article, not the sales page,
  where both exist.
- Literature: prefer peer-reviewed papers and practitioner sources with
  out-of-sample records (index data, fund returns). Record each effect's
  sample period and whether it holds after its publication date.
- No market data of the program's is read. Power and economics are
  computed from published figures and the program's frozen cost wall.
- Start and end checks, quoted verbatim in the return: `git status
  --short`, `git log --oneline -3`, the holdout status, `wc -c
  REGISTRATION.md`, the harness preflight with `--harness-sha256
  7fd757f6d7c3990c2d20756c501f68b0541aa89851dcca9236badabd4f4a9bd9`
  (v9) and a fresh PYTHONPYCACHEPREFIX, the ledger line count and
  sha256 (unchanged unless Task 4 ran a quote, which is then listed).

============================================================
TASK 0: STARTUP
============================================================

- Owner: lead. Output: reports/stage_e13_STATE.md and the ETA table.
- Done when: the start checks pass and HEAD is the commit holding this
  prompt or a descendant with a clean tree (untracked
  reports/stage_e12_briefs/margin_pages/ is expected and stays
  uncommitted, per E.12's open choice 18).

============================================================
TASK 1: VENUES FOR MULTI-DAY AUTOMATED FUTURES TRADING
============================================================

- Owner: VenueResearch-OpusHigh (worker-high on opus).
- Question: where can an automated or semi-automated futures system
  hold positions overnight and for several days?
- Prop firms: every reputable futures prop firm the worker can find
  with a current offer (at least Topstep, Apex, Tradeify, Take Profit
  Trader, Elite Trader Funding, MyFundedFutures, Bulenox, Alpha Futures,
  Lucid, TradeDay, Earn2Trade, FundedNext Futures, Phidias, The Trading
  Pit). For each: overnight and weekend holding (allowed, on which
  plans), the drawdown type (end-of-day or intraday trailing, static),
  automation and API policy in the terms (quoted), the semi-automated
  or copy-trading wording, platforms, lot limits, payout rules, fees,
  whether Canadian residents may join, and any news-trading rule.
- Phidias: re-check the 2026-09-28 entry against the current terms and
  draft the written question for Phidias support (bot generates a
  signal, a human confirms each order) for the user to send.
- Personal account: brokers that accept Canadian residents for US
  futures with an API (at least Interactive Brokers Canada; check
  others the worker finds), micro contract availability, commissions,
  initial and maintenance margins for the micros the program uses
  (from the broker's pages, not CME's), and the account minimums.
- Output: reports/stage_e13_venues.md: one table per venue type, each
  cell sourced, and a short list of venues where a multi-day automated
  system is permitted without ambiguity, permitted only with a human
  in the loop, or not permitted.

============================================================
TASK 2: TREND AND CARRY, EVIDENCE AND SIZING
============================================================

- Owner: TrendCarryResearch-OpusHigh (worker-high on opus).
- Evidence: time-series momentum and trend following (Moskowitz, Ooi
  and Pedersen 2012; Hurst, Ooi and Pedersen's century study; the SG
  Trend Index or similar out-of-sample record), and carry in futures
  (Koijen, Moskowitz, Pedersen and Vrugt 2018). For each: the
  published Sharpe, its sample, its performance after publication and
  since 2010, costs assumed, holding periods, and the number of
  markets it needs.
- Small-account implementation: Robert Carver's published guidance on
  minimum capital and instrument choice for retail accounts (the
  "small account" and micro-futures material), position rounding,
  and the volatility targets he uses.
- Sizing with numbers: for the program's 28 vehicles plus any micros
  the evidence calls for (equity micros, micro treasuries if listed,
  micro FX, micro gold, crude, copper), compute the minimum capital at
  which a diversified trend and carry portfolio holds at least one
  contract per instrument at a sane volatility target (state the
  target and the formula), at three capital levels (for example $25K,
  $50K, $100K): instruments held, expected annual return at the
  published post-2010 Sharpe range, expected monthly income, and the
  worst drawdown to expect. Use published volatilities with sources,
  never the program's bars.
- Prop-firm fit: whether a trend and carry system survives a trailing
  drawdown of the size the Task 1 swing venues use, by the V2.0 style
  arithmetic (ruin against drawdown distance), with stated assumptions.
- Output: reports/stage_e13_trend_carry.md.

============================================================
TASK 3: NEW INFORMATION SOURCES FOR INTRADAY SIGNALS
============================================================

- Owner: InfoSourceResearch-OpusHigh (worker-high on opus).
- Candidates (add others the worker finds with evidence): CFTC
  Commitments of Traders positioning; EIA weekly storage and inventory
  surprises (natural gas, crude) against consensus; weather forecast
  revisions (heating and cooling degree days) for NG and grains; USDA
  report surprises (WASDE, crop progress); implied-volatility indices
  (CBOE VIX, VIX term structure, OVX, GVZ) and their changes;
  economic-surprise indices; options-market positioning.
- For each: what it measures, its release time and the time the data
  is available to a retail system, the free or paid source and its
  cost and terms, its history length, the published evidence for
  intraday or one-day predictability in the program's products (with
  the post-publication record), whether the program has already used
  it (check V2.3's library and the K-cluster catalogs: K2, K4, K6 and
  K9 used some calendars), and whether it fits flat-by-15:08 trading.
- Output: reports/stage_e13_info_sources.md, ending with the two or
  three sources with the best evidence and fit.

============================================================
TASK 4: THE BACKWARD NG REPLICATION, DRAFT AND COST
============================================================

- Owner: ReplicationDesigner-OpusXHigh (worker-xhigh on opus), with the
  lead ruling on every design choice.
- The hypothesis, stated once and fixed: the Gate 0 family B result for
  NG at h60 (and hF, as the second of exactly two tests) reflects an
  edge that also holds on 2010-01-04..2019-05-03 NG data, a period no
  part of the program has read.
- Draft reports/stage_e13_ng_replication_draft.md as a pre-registration:
  the model (the frozen Gate 0 ridge at lambda 0.1, fitted once on the
  E.12 training panel, or an NG-only refit, chosen by a stated rule
  before any 2010-2019 data exists), the features available in
  2010-2019 (which cross-product legs need other roots' history; the
  "not applicable" treatment the design uses for unlisted legs), the
  trade rule (the top-20% threshold fixed from the training window's
  out-of-fold predictions, never from the test data), the cost (D8 at
  the vehicle; NG's vehicle and its sizing on a 50K and a 150K XFA), the
  pass bar (Bonferroni over the two tests, a mean gross of at least
  1.5c, at least 30 trades, the sign fixed), the trial count (N becomes
  473), and what a pass or a fail means.
- Feasibility: what has to be bought (NG alone, or NG plus the legs its
  features read), from E.12's quote record where it covers the item, or
  a quote-only run where it does not. Whether the funds left ($1.61 and
  $18.07) cover the purchase, and what top-up it needs.
- State the prior honestly: the best of 81 correlated tests reaching
  t 2.5 under no edge, computed or bounded, and the NG regime change
  between 2010-2019 and 2019-2024 (shale supply, LNG exports, price
  level and volatility, from published sources).
- Output: the draft, with a one-paragraph recommendation (run, run
  later, or drop) and the reason.

============================================================
TASK 5: RANKING AND PRE-REGISTRATION DRAFTS (LEAD)
============================================================

- Owner: lead.
- Rank every candidate from Tasks 1 to 4 on the same table: the
  evidence (strength and post-publication record), the venue fit
  (Topstep, a swing prop firm, a personal account), the data cost and
  any top-up, the compute and build effort in sessions, the
  statistical power with the data available (t is about Sharpe x
  sqrt(years)), the realistic income range at the user's scale (V22),
  the odds the lead assigns, and the risks (terms, regime, capital).
- Draft pre-registrations for the top one or two in
  reports/stage_e13_prereg_<name>.md: hypothesis, data and windows
  (with a held-out period never read before the test), the rule or
  model with every parameter fixed or bounded, costs, the pass bar,
  the trial count, the power, and what each outcome means. Drafts
  only: nothing frozen, nothing run.
- Include the AiTrader readout as a column in the ranking (its timing
  and what it tests), without reading its repository's results.
- Output: reports/stage_e13_ranking.md.

============================================================
TASK 6: ADVERSARIAL REVIEW (FABLE)
============================================================

- Owner: RankingReviewer-FableXHigh (worker-xhigh on fable), which wrote
  none of the files.
- Checks: every ranking input is sourced; no claim leans on an
  UNSOURCED fact; the evidence is read at its post-publication strength;
  the income arithmetic is correct; the NG draft cannot see its test
  data and its prior is stated honestly; the top pre-registration
  leaves no free parameter; the ranking does not favor ease over
  evidence.
- Output: reports/stage_e13_review.md, findings graded BLOCKING, SHOULD
  FIX or NOTE, and the lead's rulings in reports/stage_e13_rulings.md,
  every BLOCKING and SHOULD FIX fixed.

============================================================
TASK 7: RETURN AND COMMIT (LEAD)
============================================================

- One commit "Stage E.13 research and scoping" holding the reports, the
  drafts, the STATE file and the briefs, with this repository's
  attribution lines. No push.

============================================================
DELEGATION PLAN
============================================================

| Task | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup | lead | opus | xhigh | first | gates the session |
| 1 Venues | VenueResearch-OpusHigh | opus | high | parallel | web research with sources |
| 2 Trend and carry | TrendCarryResearch-OpusHigh | opus | high | parallel | literature plus sizing arithmetic |
| 3 Information sources | InfoSourceResearch-OpusHigh | opus | high | parallel | literature and data-source research |
| 4 NG replication draft | ReplicationDesigner-OpusXHigh | opus | xhigh | parallel | pre-registration design against frozen code |
| 5 Ranking, drafts | lead | opus | xhigh | after 1 to 4 | judgment, reserved to the lead |
| 6 Review | RankingReviewer-FableXHigh | fable | xhigh | after 5 | independent adversarial check |
| 7 Return, commit | lead | opus | xhigh | last | reserved to the lead |

Usage pools: weekly usage is at 65% and Fable at 45%. Fable runs only the
one review at xhigh. Web research stays on Opus high. No Sonnet worker
draws a conclusion; Sonnet or Haiku may extract text from fetched pages.

At most 4 workers at once. Workers write files and return paths.

    DELEGATION PLAN (the lead executes this; it does not do worker tasks)
    1. Decompose each task into subtasks with one objective, inputs, output
       path and format, allowed tools, and boundaries.
    2. Route per CLAUDE.md. State model and effort for each subtask before
       spawning.
    3. At most 4 concurrent. Small tasks needing no isolation go inline.
    4. Collect results as files plus short summaries.
    5. Verify every number entering a ranking with an independent check
       (the Fable review covers it).
    6. Synthesize in the lead against this prompt, and write the synthesis
       to disk before ending.
    7. Unattended run: no pauses to ask. Checkpoint to
       reports/<stage>_STATE.md after each task.

============================================================
VERIFICATION
============================================================

- Every fact in the ranking table traces to a sourced line in a Task 1
  to 4 file.
- The income and sizing arithmetic is recomputed by the reviewer.
- The ledger is unchanged, or changed only by a listed quote at $0.00.
- Holdout status unchanged, REGISTRATION.md 0 bytes.

============================================================
WHAT NOT TO DO
============================================================

- No market data read, no statistic on the program's bars, no purchase.
- No contact with any firm or broker, no account opened, no login.
- No re-mining of the 2019-2024 stores and no Gate 0 rerun (V24).
- No AskUserQuestion. No key printed. No push.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.13_RETURN.md. Fixed sections, in order:

1. Verdict summary, at most 300 words: the ranked plan's top three, the
   recommended next stage with its cost, top-up, odds and income range,
   and what the user must decide.
2. Guardrail evidence: the start and end checks verbatim.
3. Results per task: venues, trend and carry, information sources, the
   NG replication draft, the ranking table.
4. Delegation record: one row per spawn.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the
   reason.
7. Decisions for the user, each with a recommendation: which candidate
   to run next, any purchase or top-up, any support question to send
   (Phidias, others), and whether a personal account enters the plan.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

Also write one short dated progress.md entry and one line in
docs/STAGES.md.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
