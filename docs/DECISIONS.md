# Locked decisions

- Venue: Topstep via TopstepX/ProjectX API. Rationale: only futures prop
  firm with native REST/WebSocket API; Tradovate blocks API on prop
  accounts; Apex bans automation outright.
- Scope: XFA only, current phase. LFA is a call-up exit event, modeled as
  terminal in the funnel simulator, not solved for.
- Instrument ranking: MES > MNQ > MGC > MCL, on cost-to-range and data
  quality. Micros required for $2,000 trailing MLL granularity (10:1
  ratio, 50-micro cap on 50K).
- Data: Databento GLBX.MDP3 for all backtest history. TopstepX
  retrieveBars for live/streaming and cross-checks only (shallow history
  on expired contracts, gateway limitation).
- Execution/rules-engine design borrows the shape of two existing repos:
  HFExperiment's intent/gate pattern (frozen Intent dataclass, pure
  check_order function, named refusals in fixed order) and AiTrader's
  RiskGate/kill-switch pattern (final-authority deny-only gate, JSON
  kill-request file, manual resume required). Adapted to Topstep's rules,
  not left generic.
- No sandbox exists on TopstepX. All early testing runs on a Practice
  account against live endpoints.
- Orchestration (2026-09-21): stage sessions run a Fable lead that plans,
  routes, verifies and synthesizes, with workers on haiku (pure extraction
  only), sonnet, opus or fable at medium, high, xhigh or max effort. No low
  effort. Concurrency capped at 4. Rules in
  CLAUDE.md, rationale and the stage-prompt template in docs/ORCHESTRATION.md.
- Model tiers revised (2026-09-22): Opus 5.5 is the default lead and handles
  all high-level work; Fable is used only for independent and adversarial
  verification, audits and reviews. See CLAUDE.md.
- C6 closed, Stage D.1g not run (2026-09-23, the user's decision in the
  planning chat; recorded by the Stage E.0 lead). C6, passive execution
  (C-H4's resting limit orders), is closed as non-deployable on the XFA, and
  Stage D.1g (a queue-position fill model on 181 purchased MBO days) will not
  run. Reasons, each with its Topstep source (fetched 2026-09-23 20:17 PDT,
  reports/stage_e0_topstep_facts.md):
  (1) TopstepX fills a limit order only when the market trades through it:
  "the market has to trade through your price - not just touch it" and "if
  the market doesn't trade through your price, you don't get filled"
  (help.topstep.com/en/articles/8765442). That is the fill model D.1f already
  applied to C-H4: UCB95 -177.18 net ticks per micro per day (mean -186.63)
  over 90,418 round trips, trade dates 2020-02-03 to 2024-02-29
  (reports/stage_d1f_tier_a.json; progress.md, Stage D.1f run).
  (2) Any edge from fills better than trade-through would come from queue
  position in the simulator, which Topstep prohibits: "Making hundreds of
  rapid trades to take advantage of preferential queue position in SIM",
  behaviour it describes as "usually hundreds or thousands of trades per day,
  with average durations measured in seconds, not minutes"
  (help.topstep.com/en/articles/10305426, updated June 10, 2026).
  This is a scope decision, not a null under docs/NULL_CRITERIA.md. C6 was
  never tested at queue-position fills, no C6 null statement exists, and none
  may be made; C-H4 keeps its D.1f label "null under the pessimistic fill
  model", a lower bound. N stays 58 (D.1g's queue-model C-H4 would have been
  trial 59), and the N_C6 = 181 MBO dates are not bought. From Stage E on,
  every limit order is modelled at trade-through fills, and a member whose
  edge needs better fills is excluded at design.
- Stage E design decisions (2026-09-24, the user's decisions in the planning
  chat after reviewing Stage E.0; applied and recorded by the Stage E.1 lead;
  every edit in reports/stage_e1_changes.md; frozen by Stage E.1's manifest,
  reports/stage_e1_freeze.json):
  U1. D1 as the rule gives it: NKD (ADV 7,969, coverage 0.621), 6M (coverage
  0.903) and MET (coverage 0.947) are OUT; they may serve only as signal legs,
  under D9's member-level coverage check.
  U2. Platinum (PL) is OUT. Topstep's volatility cap for PL on the 50K is 0
  contracts and PL has no micro, so the bot cannot trade it. It is removed as
  a traded exposure everywhere and may not serve as a signal leg.
  U3. Cluster order: K2, then K4, K5, K3, K6, K7; then K1 only if the user
  decides after K7 that it is needed; K8 last. K1's members stay in the
  frozen catalog so that a later K1 session is pre-registered.
  U4. Staged purchase: step 1 in E.1 is the research window of every
  admissible contract of the traded exposures plus the mbp-1 sample on the
  five fixed dates, no tbbo. Step 2 is design option (b): each cluster's
  2019-05..2025-03 history of its chosen vehicles is bought just before that
  cluster's confirmation session, its holdout-2 chunks sealed on arrival. The
  ML route's data needs are decided separately and may pull some step 2
  purchases forward.
  U5. Databento account: acct-2 ($125.00 credit, used only by this repo)
  carries all new spend; acct-1 (shared with the archived MLCryptoEngine,
  $91.59 spent) is closed to new spend by this program.
  U6. Design section D15 is superseded by a separate Stage E ML route
  (docs/STAGE_E_ML_DESIGN.md, a draft for the user's review). The eight
  K#-ml-01 entries are excluded: superseded by the Stage E ML route. ML is a
  strategy-discovery tool: its findings become plain rules that are
  pre-registered and tested like any other member; no model is deployed or
  makes live decisions.
  U7. M6E and M6A stay non-candidates for D2 until Topstep answers the user's
  support email (drafted 2026-09-24). If Topstep clears them before a
  cluster's screening session, a vehicle amendment may be written before that
  session reads any research-window bar, logged here.
  U8. Accepted as drafted: D2 (risk target, band, 1-lot cap), D3
  (min(translated, funnel-derived), with the no-passing-cell rule), D4
  (holdout-1 not bought for new products; full-size bars as a price path only
  if the power check fails and the user agrees), D5 (alpha split, t >= 1.0
  screen), D6 (the three ports), D7 ("inconclusive by design" and
  "source-overlap"), D8 (mbp-1 only, five dates), D9, D10, D11, D14, and every
  member's parameters as E.0's rulings left them.
  U9. E.0's small text items (review R-28) fixed where they change no rule
  (K5's trial counts beside the ruling's 2 for K5-preauc-01; K2's stale CP2
  notes).
  Lead's count note (Stage E.1 F-1, for the user, not part of U2): D1's table
  has 31 traded exposures after U2; E.0's "31" before U2 was a miscount of 32
  IN rows, and the stage prompt's "30" repeats it.
  Result: 53 active members, 158 confirmation trials, projected cumulative
  N = 58 + 158 = 216 (E.0: 61, 170, 228).
- Stage E ML route decisions (2026-09-25, the user's decisions in the planning
  chat, accepting the planning chat's recommendations on the Stage E.1 draft
  of docs/STAGE_E_ML_DESIGN.md; applied and recorded by the Stage E.2a lead;
  every edit in reports/stage_e2a_ml_changes.md; frozen by Stage E.2a's
  manifest, reports/stage_e2a_ml_freeze.json):
  V1. M1 accepted: train, tune, normalize and distil only on
  S_X..2024-02-29, never touch March 2024 or holdout-2, test the frozen
  distilled rules once on the research window, holdout-2 stays the final
  gate. The route buys the full step 2 range (2019-05..2025-03) of one
  contract per exposure, holdout-2 sealed on arrival. Funding is pending: the
  user will top up acct-2. No purchase in E.2a.
  V2. M2 accepted: one pooled model per challenger across the 31 exposures,
  evidence counted in trade dates.
  V3. M3 accepted: LightGBM plus one small LSTM, 36 configurations in total,
  as listed. The TCN stays dropped.
  V4. M4 accepted: the three horizons, the feature list, the 1.5 x cost
  stress.
  V5. M5 accepted: depth-2 surrogate rules, at most 2 per cluster and 16 in
  total, the block-6 pre-test.
  V6. M6 accepted: one trial per tested rule, the route as its own family at
  alpha 0.05 / (K + 1).
  V7. M8 amended: the LSTM trains on this machine's NVIDIA RTX 3050 Laptop
  GPU (4 GB VRAM, found 2026-09-25), not on the Windows PC. The Windows PC is
  dropped from the route. Trees run on the CPU. Both follow the overnight
  profile in CLAUDE.md. Replace M8's Windows PC text and its time estimates'
  GPU assumptions accordingly, and state that E.2b's probe re-plans the
  LSTM's batch size to leave at least 0.5 GB of VRAM free.
  V8. M9 accepted: the route's buy and train sessions run after E.2b, beside
  K2's screening, and the route's test runs once all its rules are frozen,
  before K8.
  V9. Also accepted from the E.1 return: F-1 (31 traded exposures, as already
  written in the frozen D1), F-5 (K2-aucpost-01's 5-minute lag, which review
  R-15 found supported), and FA-06 option: the source windows of the
  source-overlap members may be recorded before any confirmation read, as a
  separate audited amendment that can only remove a source-overlap label,
  never add a member, change a rule, or add a label (Stage E.2a Tasks 2 and
  11).
  Lead's notes (Stage E.2a, for the user, not part of V1 to V9): V1 sets no
  cap for the route's purchase (still the user's); V8 puts the route's buy
  session after E.2b while the E.2a prompt says E.2b or later buys the older
  history; V7 sets no compute budget. See reports/stage_e2a_ml_changes.md,
  Q-1 to Q-3.
  V6's effect on frozen D5 (Stage E.2a freeze ruling on audit ML-A14): D5's
  K counts every family with a non-empty tested set, the ML route included
  once it has a tested rule; when the route tests a rule every family, each
  cluster's Tier A included, tests at 0.05 / (K + 1), and D5's "at most 8"
  reads "at most 9". Recorded here; docs/STAGE_E_DESIGN.md is not edited.
  Freeze rulings (Stage E.2a Task 4, reports/stage_e2a_ml_freeze_rulings.md):
  the audit's 2 blocking and 14 should-fix findings were fixed within V1 to
  V9 by bracketed notes in docs/STAGE_E_ML_DESIGN.md; new wording for the
  user: the selection metric (ML-A01), the per-side candidate threshold
  (ML-A02), the LSTM's 4-dimension product embedding (ML-A12), the
  one-trade-date embargo kept (ML-A13), the primary leg (ML-A15), the
  calendar-based block cut (ML-A03) and the 31 price-path contracts (ML-A07).
- Source-window amendment (2026-09-25, Stage E.2a Task 11, under the user's
  decision V9): the sample windows of the sources behind the 37 members that
  carried the source-overlap label by fallback were recorded
  (reports/stage_e2a_source_windows.json) and the frozen rule applied to
  them mechanically (reports/stage_e2a_source_window_amendment.md). Six
  labels are removed: K2-predrift-01, K3-ldnmom-01, K3-mehedge-01,
  K4-ngpre-01, K8-flight-01, K8-oilcad-01; the other 31 keep it. Audited
  independently (reports/stage_e2a_declaration_audit.md, Part 2: all six
  confirmed); rulings in reports/stage_e2a_source_window_rulings.md. No
  member, rule or label was added and no frozen file was edited.
- Windows PC as an optional compute machine (2026-09-26, the user's decision
  V10, recorded in Stage E.2b): ML training and backtests (screening and
  confirmation runs) may run on the user's Windows PC when it is available
  (Ryzen 5, 32 GB RAM, RTX 2060 Super 8 GB, 2 TB SSD, as the user gave them;
  measured in E.2c), sent from the ThinkPad over SSH with results pulled
  back and checked by hash. The ThinkPad stays the default and every job
  also runs on it unchanged; it keeps the Claude sessions, purchases,
  sealing, reviews and commits. This supersedes V7's sentence dropping the
  PC and nothing else in M8. M8's compute text gains the PC: the ThinkPad
  and its RTX 3050 stay the default; when the PC runs the LSTM, the frozen
  A-1 rule plans its batch size against the RTX 2060 Super's 8 GB, and one
  machine and one batch size are recorded for the whole LSTM grid before its
  first fit. Every job records which machine ran it. Never sent to the PC:
  sealed chunks, plaintext holdout-1, holdout-2 or embargo bars, the
  Databento key or any secret, the ledger. M7.4 is kept by separate data
  roots (the training job's root holds only the training-window store). No
  statistical choice in the frozen ML design changes, and
  docs/STAGE_E_ML_DESIGN.md is not edited. Amendment:
  reports/stage_e2b_v10_amendment.md (audited in Stage E.2b Task 7); setup
  guide: docs/WINDOWS_SETUP.md; the PC is connected and verified in E.2c.
- MBT's holdout-1 rows inside the step 1 files (2026-09-26, recorded in
  Stage E.2b Task 9, E.2a ruling L-9): CME books MBT's trading from
  Thursday 2026-06-18 16:02 CT to Saturday 2026-06-20 18:59 CT (Juneteenth
  and the 24/7 weekend) to trade date 2026-06-22, holdout-1's first trade
  date. The 1,617 MBT bars in that span arrived inside the step 1 purchase
  files because the purchase guard checked timestamps (the files end
  2026-06-21 00:00 UTC), not CME trade dates. The E.2a bar builder decoded
  them with the rest of the file and dropped them unread; they were never
  written to any parquet and no quantity uses them. Nothing is deleted: the
  raw step 1 files stay as bought, and raw vendor files never leave the
  ThinkPad (V10-4). They are now refused by trade date everywhere: the
  Stage E bar loader (tests/test_stage_e_loader.py::
  test_mbt_rows_booked_to_holdout1_trade_date_2026_06_22_are_refused_ruling_L9),
  the purchase guard, which now books every minute of a request to its CME
  trade date before any vendor call (data/trade_date_guard.py; tests/
  test_e2b_trade_date_guard.py::
  test_mbt_request_ending_2026_06_21_is_booked_partly_to_holdout1_and_refused),
  and the Windows backend's send-side data rules (compute/, tests/
  test_compute_datarules.py).

- 2026-09-26 (user, planning chat): V11. The ML route's feature F17
  (docs/STAGE_E_ML_DESIGN.md M4: sigma_X,d over its own median) uses a
  20-trade-date median in place of the frozen 120. Reason (E.2b return,
  decision 7): holdout-2 is sealed and ends the day before the research
  window starts, so a 120-date median leaves about 160 of the research
  window's roughly 300 dates without route rows, and a route rule would be
  tested on about half the window. With 20 dates the warm-up is about 40
  dates. Nothing else in the frozen ML design changes. Status: decided,
  not yet applied. The ML route's first session applies it before any fit,
  as a logged amendment to the frozen design and the harness manifest
  (ml_route/constants.py F17_MEDIAN_DATES), audited by Fable, with a new
  harness manifest sha256.
- 2026-09-26 (user, planning chat): V12. ML route compute. The user prefers
  the Windows PC (RTX 2060 Super 8 GB, 32 GB RAM) for ML training once
  E.2c has connected and verified it. The user allocates 8 to 10 hours of
  overnight time per run: every ML training session either finishes inside
  that window or stops cleanly at a checkpoint (the resumable per
  configuration and fold ledgers of M7 and V10) and resumes in the next
  window with no work lost or repeated. Each session estimates its run
  time from the E.2b and E.2c probes before starting and plans the work
  into windows. The ThinkPad remains the fallback machine.
- 2026-09-27 (planning chat, on the user's go-ahead for the E.4 prompt): V13. Harness fix and cluster order.
  (a) Stage E.4 fixes harness bug C-1 (E.3 return, section 7: under
  `python -m` the runner loads twice and start-date refusals escape) and
  adds a per-trial trip list to the runner's output. Nothing else in the
  harness changes. The change is proven numerically inert by a replay of
  K2's 44 frozen trials, reviewed by Fable, and frozen as harness manifest
  v4. K2's tiers stand as E.3 computed them. Later purchase sessions that
  edit data/config.py write the version after v4.
  (b) The cluster order stays U3 (K2, K4, K5, K3, K6, K7, then K1 if
  needed, K8 last). The order has no statistical effect (each cluster has
  its own Holm family), so the user may move K3 up at any point without
  an amendment.
  (c) At the user's request (2026-09-27), Stage E.4 runs K4, K5 and K3 one
  after another in one unattended session across three usage windows, each
  cluster with its own specs, Fable audit, freeze commit, run and return.
- 2026-09-27 (user, planning chat): V14. Before any Stage E confirmation
  read. (a) OC-Q: the composite verdict for an exposure X is D.1f's
  procedure (the robust zero-edge gate plus both drift sub-checks) run with
  X's own research-window bars, X's frozen D8 cost table, X's vehicle at
  q_c and eps_X in place of MES's. It is built, Fable-reviewed and frozen
  only if a trial passes Holm, DSR, daily t > 3.0 and PBO. Until then such
  a trial reads "edge candidate, composite pending", never "edge".
  (b) Holm K = 9 (the maximum) for every Holm run until every cluster and
  the ML route have been screened. The edge chain's t > 3.0 is stricter
  than 0.05 / 9, so nothing is lost.
  (c) Planning chat ruling, open to the user before E.5's first list hash:
  where a cluster's Tier A has one member, DSR's Sharpe variance is taken
  over all of the cluster's confirmation-window daily Sharpes (Tier A and
  Tier B), since a one-member variance is undefined.
  (d) The user approved the step 2 purchases for K4 (MCL, NG, $11.46
  quoted) and K5 (MGC, MHG, $9.74 quoted) on acct-2. K3's confirmation
  ($49.34, needs a top-up) is deferred.
- 2026-09-27 (user, planning chat): V15. Cluster order after E.5. K6, K7
  and K1 are screened together in Stage E.6, in that order. K1 is screened
  now instead of "only if needed" (U3). K8, the cross-market cluster, runs
  alone in its own session afterwards, because its members differ in kind
  from the single-product clusters.
  Amended by the user, 2026-09-27 21:18: one cluster per session. E.6
  screens K7 alone (before the 2026-09-30 weekly reset), E.7 screens K1
  (swapped forward by the user, 2026-09-28, to fit the weekly limit), and
  E.8 screens K6 after the reset. K8 follows on its own.
- 2026-09-28 (user, planning chat): Phidias Propfirm researched as a
  candidate venue with overnight holding, updating the D.1c constraint
  audit finding that no researched firm permitted it. Result: real but
  blocked, not adopted.
  - Phidias's Premium tier is a genuine swing account: no same-day
    flatten, positions held overnight and over weekends, EOD trailing
    drawdown as the sole loss mechanism. Platform is Rithmic (also
    Tradovate, DeepCharts); Rithmic itself supports algo execution
    generally, but that is infrastructure capability, not Phidias policy.
  - Phidias's Terms of Use ("Prohibition of automated trading and High
    frequency trading") ban robots and fully automated algorithms
    outright, with one exception: "semi-automated software, provided the
    User actively monitors and manually adjusts all operations." The TOU
    gives no technical definition of "semi-automated," no mention of
    alert/confirmation systems (Telegram or otherwise), and no worked
    example of compliant vs. non-compliant software.
  - Candidate design floated by the user if semi-automation reads
    permissively enough: the strategy generates a signal, a Telegram bot
    pushes it to the user, the user taps to confirm, and only that
    human action triggers order submission (e.g. via the Rithmic
    connection, one order at a time, no unattended loop). This is
    UNCONFIRMED against Phidias's actual reading of their own terms.
    Before any build time goes into it: (a) ask Phidias support in
    writing whether a bot-generates / human-confirms-via-Telegram flow
    qualifies as semi-automated, and get the answer in writing; (b)
    do not build the Telegram bot, or any execution path, until that
    answer is in hand. A firm can revoke a funded account retroactively
    for a terms violation, so this is a compliance question first and an
    engineering question second.
  - No dedicated API product, sandbox, or demo API is documented on
    Phidias's side (checked 2026-09-28: rules page, swing-allowed page,
    accounts/platforms page, TOU). Automation, if permitted at all, rides
    on whichever retail platform (Rithmic/Tradovate/DeepCharts) the human
    is clicking in.
  - Venue decision unchanged: TopstepX/ProjectX stays the primary venue
    (`docs/DECISIONS.md`, top entry). Phidias is recorded as researched,
    not selected. Revisit only after the written compliance answer, and
    only as an addition, not a replacement, since Phidias's evaluation
    and split structure differ from TopstepX's and would need its own
    scope decision.
- 2026-09-28 (user, planning chat): V16. K8 cross-market rules, decided
  before any K8 bar is read. (a) Roll days: the frozen design rule stands.
  A trade date is dropped if it is a roll-blackout date of any leg the
  member reads, signal legs included (D4's union). The K8 catalog wording
  that signal-leg rolls are "not excluded" yields to D4. (b) A signal leg
  on a root with no D6 session record reads its micro twin: ES reads MES
  (so an S&P leg starts 2020-02-03, D4) and BTC reads MBT. No purchase and
  no harness change. A leg on NKD, MET or 6M is refused by name. (c) Crude
  signal legs read MCL (S_X 2021-07-12). Full-size CL bars are declared as
  the price path only if D4's power check fails and the user agrees then
  (U8). Each ruling is checked against the K8 member texts before the K8
  prompt is written.
- 2026-09-28 (user, planning chat): V17. Order of work after Stage E's
  screening. First E.8 (K6), then K8 alone, then the ML route (its
  purchase uses acct-1's remaining room first, then a top-up of acct-2).
  Only after those: a narrow research run on low-frequency, full-session
  holds (rare-condition entries, large per-trade targets, several products
  to reach enough trading days), and after that, if a base rule shows an
  edge, a test of an LLM as a bounded per-trade filter (take, skip or half
  size) against the base rule, on post-cutoff data or live paper trading.
  The LLM filter would revisit the "deployed bot runs plain rules"
  decision and needs Topstep's answer on its AI clause first.
- 2026-10-01 (planning chat, for the user): V18. Lesson from E.8, for
  future designs only. D5's screen (mean > 0 and daily t >= 1.0) passes a
  series with a single positive trade automatically, since one positive
  day among n gives t = sqrt(n / (n - 1)), just above 1.0, whatever its
  size (K6-limitcont-01 HE, Tier A on one trip). D5 stays frozen for the
  clusters already screened and for K8. The ML route's own screen and any
  later research run must state a minimum trade count before a pass
  counts, set before any data is read. K6's confirmation is not planned:
  its only Tier A trial rests on one trade.
- 2026-10-02 (user, planning chat): V19. Amends V17's order. The narrow
  research run on low-frequency, full-session holds (V17's fourth step)
  runs before the ML route, so the user has time to settle the ML route's
  compute host. Stage E.10 researches and drafts a K9 catalog from
  published evidence only (no market data, no Stage E figures), E.11
  freezes it after the user's decisions, and E.12 codes and screens it.
  The ML route follows. acct-2 was topped up to a $125 balance by the user
  on 2026-10-02. ACCOUNT_2_CAP_USD (cumulative) is raised to match by the
  next purchasing session, about $249.67, and .env now holds the keys as
  DATABENTO_API_KEY1 and DATABENTO_API_KEY2, which data/config.py must be
  taught to select by account before any purchase (it reads only
  DATABENTO_API_KEY today, so every Databento call is refused until then).
- 2026-10-02 (user, planning chat): V20. ML route v2, a quant-style
  model, replaces running the frozen ML route as designed. After K9
  (E.10 to E.12), a design session writes and freezes "ML route v2"
  before any training data is bought. It follows a quant trader's
  workflow, with the program's own technology: signal research (candidate
  signals), signal construction and normalization, alpha combination into
  one score per product per session, a transaction-cost model with a
  turnover penalty, risk-scaled position sizing inside the lot limit and
  the trailing drawdown, portfolio construction across products under the
  Topstep constraints (flat by 15:08 CT), walk-forward testing with nested
  model selection, a minimum trade count (V18), holdout-2 as the final
  gate, then paper trading before any account. Candidate signals include
  every K1 to K8 family and every K9 family as features, all of them, not
  only those that looked promising: choosing signals by their Stage E
  research-window results would select on the test data. The model
  chooses and weights signals on the training window only. Open for the
  user at the design session: deploying a frozen model (weights fixed and
  hashed, never retrained live) in place of the "deployed bot runs plain
  rules" decision of 2026-09-24, and the compute host. The training window
  overlaps the 2019-2024 data already read for K4's and K5's
  confirmations (MCL, NG, MGC, MHG), which the design records.
- 2026-10-03 (user, planning chat): V21. After E.10. K9 is not frozen or
  screened on its own: its one surviving member, K9-anncday-01 (the
  macro announcement-day premium), is folded into ML route v2 as a
  candidate signal. E.10's design target showed that no low-frequency
  rule can reach eps alone, so any edge is a component edge, which is
  what v2 combines. E.10's design inputs carry forward to v2: the cost
  wall, K = 10 as the proposed maximum Holm K (K9 dropped, the ML route
  kept), and a minimum trade count of 30. The two withdrawn VIX members
  stay withdrawn. Earlier stages' session-cost figures are not re-run
  with E.10's corrected script. Stage E.11 drafts the v2 design and
  builds its pipeline on synthetic data, with no market data, purchase
  or training, as one long build session.
- 2026-10-03 (user, planning chat): V22. Income path and data plan,
  after the quant-integration research report. The report puts a
  realistic net Sharpe at 0.8 to 1.8, about $1.5K to $3.5K a month across
  5 x 150K XFAs. $10K a month on Topstep alone needs a net Sharpe near
  3.4 ($95 a day per account at about $450 of daily risk, 10% of the
  $4,500 MLL), so the user does not plan around it. Path: first earn five
  figures from XFA payouts, or enough to fund a small personal micro
  futures account, then move the same models to personal accounts, where
  income grows with capital and no MLL applies. Data: more history, not
  finer data (no tick or order-book purchases; holds run 60 minutes or
  longer). The first purchase spends only the funds already in the two
  Databento accounts (acct-1 about $28 usable, acct-2 $125 after the cap
  raise to about $249.67): the v2 freeze session quotes a priority subset
  of the 2019-2024 one-minute history (most liquid products, lowest cost
  relative to volatility) that fits that budget. Gate 0, the pre-cost
  component audit, runs on that subset first. The rest of the 28 products
  and a free quote for full-size contracts back to 2010 come later, and
  only if Gate 0 finds a gross edge. The report's findings go into the v2
  freeze (Gate 0, ridge primary with shallow LightGBM as challenger,
  nested CPCV with embargo, PBO, DSR at the full trial count, t >= 3,
  holds of 60 minutes or more at 1 to 3 decision times, cost gate
  k in {1.5, 2, 3}, drawdown-distance sizing, payout-mechanics
  simulation, kill switches, and the Live Funded Account API ban).
- 2026-10-03 (user, planning chat): V23. After E.11. The user accepts
  all 19 of the lead's V2.12 recommendations in
  docs/STAGE_E_ML_V2_DESIGN.md: (1) the gross cost-gate reading
  (hurdles 1.5c / 2c / 3c, tau 0.167) and Gate 0 at a gross mean of
  1.5c on the top-20% confident trades, t >= 3, Holm 0.05 with family A
  in the Holm family, at least 30 trades; (2) the phase-1 subset rule as
  written; (3) the CME maintenance margin as the volatility proxy, the
  frozen E|m_1| only if CME's pages block the fetch; (4) phase 1 covers
  the training window only, the holdout-2 chunks deferred to phase 2;
  (5) a free quote for the 2010 extension at the freeze, bought only
  after a Gate 0 pass and with a D4 start-rule amendment; (6, 7) the
  decision clock, the horizons and the roll-blackout rule as written;
  (8) the signal library as written, plus the EC-K9 calendar for
  2019-2024 built from official pages in the freeze session so
  K9-anncday-01 enters; (9) the research-window warm-up skips the sealed
  gap; (10) the grids as written, 45 configurations; (11) the sizing
  constants as written plus the release-window rule (no new entry with
  a fill in [release - 5 min, release + 30 min) while open
  lot-equivalents exceed half the tier); (12) the 150K MLL, scaling
  schedule and reset price read from Topstep's public pages at the
  freeze; (13) the kill-switch thresholds as written; (14) the success
  criteria as written, with the 1.5 x slippage sensitivity a
  must-survive condition in the holdout-2 registration; (15) the payout
  policy as written; (16) deployment (a): a frozen model, weights fixed
  and hashed, never retrained live, replacing the "deployed bot runs
  plain rules" decision of 2026-09-24; (17) the ThinkPad as the compute
  host; (18) whether to accept a Live Funded call-up is decided before
  the first funded account; (19) the purchase: the user pre-approves
  spending the funds already in the two Databento accounts (acct-1's
  headroom, about $28.41, first, then acct-2's $125 after
  ACCOUNT_2_CAP_USD rises to $249.67) on the phase-1 subset in Stage
  E.12, after a fresh quote logged in that session, with no further
  approval. No spend beyond those funds. The ML route's slot in the
  research-window Holm family stays unused: v2's research-window read is
  a screen (t >= 1.0), and confirmation rests on the nested
  out-of-sample t >= 3, the DSR at N_total and the holdout-2 read. Stage
  E.12 freezes v2, buys phase 1, runs Gate 0 once, and stops.
- 2026-10-03 (user, planning chat): V24. After E.12. Gate 0 failed
  (best pair NG h60, t_B 2.51 against the Holm bar near 3.6; pooled
  family B mean gross -0.72 ticks against 2.26 ticks of cost; Fable
  verified all 273 tests). Under the frozen V2.2b, ML route v2 stops: no
  phase-2 purchase, no V2.6 model, no holdout-2 registration. Program N
  is 471. Harness v9 (7fd757f6..., the keep-and-flag ruling path for 24
  closure bars, chosen at the session's mid-stage question) stays in
  force. The phase-1 stores stay on disk; any reuse needs a new
  pre-registration that counts N = 471. Funds left: acct-1 $1.61,
  acct-2 $18.07, with no spend approved beyond V23. The user chooses to
  keep searching rather than pause. Stage E.13 is a research and
  scoping stage with no market-data read and no purchase: (a) venues
  that allow multi-day holds with automation (prop firms, including
  Phidias's semi-automated reading in the 2026-09-28 entry, and a
  personal micro-futures account for a Canadian resident), with the
  trend and carry evidence and the capital it needs; (b) new information
  sources for intraday signals (positioning, storage and weather
  surprises, implied volatility); (c) a draft pre-registration for a
  backward NG replication on 2010-2019 data, with its feasibility and
  quoted cost; (d) a ranking of these against each other, with
  pre-registration drafts for the top one or two. Re-running Gate 0,
  relaxing its bar, or re-mining the 2019-2024 stores is ruled out.
- 2026-10-04 (user, planning chat): V25. After E.13. The user runs C1
  (the backward NG replication) and C2 (dealer-gamma-conditioned S&P
  late-session momentum) together in one overnight stage, E.14, per the
  drafts reports/stage_e13_prereg_ngrepl.md and
  reports/stage_e13_prereg_gexmom.md. Decisions: (1) V24's question for
  C1 is answered yes: reloading E.12's persisted out-of-fold predictions
  to reproduce q, and one full-panel fit of the frozen ridge M1 on the
  E.12 training panel, are allowed; neither reruns Gate 0 or tests
  anything on 2019-2024. (2) The S&P exposure is reopened for C2's one
  registered test only: ES 2011-05..2019-04 bars are read, MES is the
  vehicle, and MES's sealed holdouts stay sealed. SqueezeMetrics' free
  GEX CSV is accepted, subject to its terms check; C2 stops if the terms
  forbid this use. (3) Funding: the user tops up acct-2 by $60, so
  ACCOUNT_2_CAP_USD rises from $249.67 to $309.67 in E.14's harness v10,
  and pre-approves spending up to $75.00 in total in E.14, after a fresh
  quote logged in that session, with no further approval. (4) The
  calendar probe (one year of the energy calendar and the NGS table at
  evidence grade) runs first inside E.14 and can drop C1 by its stated
  rule. N goes 471 -> 473 (C1) -> 475 (C2) at registration, whatever the
  outcomes. A pass in either is evidence, not a deployment verdict.
- 2026-10-05 (user, planning chat): V26. Amends V25 before E.14
  launched. The acct-2 top-up did not go through. ACCOUNT_2_CAP_USD
  stays $249.67; the raise to $309.67 waits for a successful top-up and
  a later harness change. E.14 works with the funds on hand: both
  pre-registrations are built and frozen; C1 goes through its q
  reproduction and M1 fit and then stops, frozen and unregistered,
  awaiting funds; C2 is registered (N 471 -> 473), its ES 2011-05..2019-04
  bought within acct-2's $18.07 of headroom (pre-approved after a fresh
  logged quote, with the 3% margin), and evaluated once. C1's set is
  quoted only. V25's $75 approval lapses with the top-up.
- 2026-10-07 (user, planning chat): V27. After E.14. C2 stopped at its
  power rule (135 eligible negative-GEX dates against the floor of 200)
  before its freeze; nothing was read or bought for it, N is unchanged,
  and it stays stopped with no rerun planned. C1 is frozen and ready
  (freeze afc5c10f..., commit 1680982). The user has topped up acct-2 to
  fund C1. Stage E.15 completes C1 per its freeze: harness v11 raises
  ACCOUNT_2_CAP_USD from $249.67 to $291.08 (the minimum E.14's quote
  needs), and the user pre-approves spending the fresh ext2010 quote
  x 1.03 on acct-2, never above $60.00, after a logged quote, with no
  further approval. C1 is registered (N 471 -> 473) before the purchase
  and evaluated once.
- 2026-10-07 (user, planning chat): V28. After the user's research run on
  how quant firms build systems and which base strategies survive. No
  deep network, reinforcement learning or other ML layer goes onto a rule
  set that has not passed a pre-registered test: ML combines and filters
  real signals, it does not find them, and Gate 0 already found no gross
  edge for ridge and LightGBM on the 64-feature library. ML re-enters
  only as a pre-registered meta-labeling layer (a small classifier
  deciding whether and how large to take a passing base rule's trades),
  after that rule passes and after a holdout-2 registered read. Stage
  E.16 pre-registers five forced-flow base rules from the report (H1
  settlement-window intraday momentum pooled; H2 the month-end NQ versus
  ZN rebalancing pair; H3 the Treasury auction cycle; H4 the next-day
  reversal of the settlement-window move; H5 their equal-risk
  combination), every parameter fixed, on data already owned, with no
  purchase, holdout-2 sealed, N rising by 5, and Holm at 0.05 across the
  five. H2 and H3 hold overnight, so their venue is a personal account
  (IBKR), not Topstep.
- 2026-10-08 (user, planning chat): V29. After E.15 stopped twice on
  Databento's acct-2 lock ("locked for security reasons"; the user
  suspects an incident on Databento's side). C1 stays frozen and
  unregistered; N stays 471. The quote tool reported E.14's old quote as
  complete when every call failed (a stale-ledger fallback); until a
  harness change fixes it, every quote is checked by summing the run's
  own new ledger lines. The user runs what needs no Databento: Stage
  E.16 becomes Part A, which sources settlement minutes, audits overlap,
  builds the multi-day simulator and runners on synthetic data, builds
  the missing 2010-2019 calendars (livestock, EC-AUC), and freezes H1 to
  H5 on a 2010-06-07..2024-02-29 window (with a per-product fallback to
  2019-05-06 if a product's extension cannot be bought), reading no bar,
  calling no vendor, registering nothing. Stage E.17, once Databento
  works and funds are in place, completes C1, buys the remaining 21
  extension roots (about $160 per E.12's quote), registers H1 to H5
  (N +5), and runs each once.
- 2026-10-09 (user, planning chat): V30. After E.16 Part A. The user has
  about $100 in Databento acct-2 (funded with help from friends) and
  chooses to buy what that covers, then proceed. Stage E.17 follows the
  E.16 hand-off with amendments: total spend at most $97.00; C1 first;
  then the other 21 extension roots in a priority order fixed before any
  quote (ZT, ZF, ZB to complete H3, then E.12's frozen phase-1 ranking,
  greedy within the budget left); roots not funded run on the fallback
  window 2019-05-06..2024-02-29, listed at registration before any
  purchase; H2 is dropped (N + 4) if C1's NQ and ZN purchase does not
  complete. The E.16 lead's recommendations are accepted: H2's NQ entry
  at the 15:30 reopen before 2020-10, HE from 2017-07, LE 2010-2014 out
  of H1 and H4, equity H1 trades past 15:08 kept for 2010-2020 with a
  descriptive table without them. If acct-2 is still locked at the fresh
  quote, E.17 stops before any registration.
- 2026-10-09 (user, planning chat): V30 amended before any quote. The
  user confirmed acct-2's Databento balance at exactly $130.23 (a first
  figure of $126.25 was a typo). At the user's choice, E.17's amendment
  A1 changes from $97.00 to $124.00 in total billed spend, with A3's
  greedy selection using each root's fresh quote x 1.03 against $124.00
  minus Part 1's billed amount. Nothing else changes.
- 2026-10-10 (user, planning chat): V31. After E.17. C1 stopped at its
  guard C10 (g17_mbt, a bitcoin leg that did not trade in 2010-2019,
  applied on 0 NG rows); no statistic exists; the attempt is closed.
  The user chooses a re-registration, C1b, identical to C1 except that
  C10 exempts legs with no listed contract in the test window (MBT; CL),
  which section 2 already treats as not applicable; N 478 -> 480; no
  purchase (the data was bought in E.17). The base-rule batch H1 to H5
  is closed: all five failed (H1's gross is about a quarter of its D8
  cost; H2 positive at p 0.068, not a pass); no rerun or variant on these
  windows, no purchase of the 10 fallback roots, no holdout-2 read. New
  program rule (cost-feasibility gate): every future hypothesis states,
  before any data purchase or pre-registration, its expected gross per
  trade from published evidence against the D8 round-trip cost of its
  vehicle, and is dropped if the expected gross does not clear the
  cost by its pass multiple. After C1b, the program waits for the
  AiTrader readout.
- 2026-10-10 (user, planning chat): V32. After E.18. C1b failed (NG h60
  t_B -0.83, hF -0.41; Fable verified); the NG near-miss is closed; N is
  480. The user cannot fund a personal IBKR account yet and plans to
  build that capital from Topstep XFA payouts. Before any Combine is
  bought, Stage E.19 models the Combine-to-XFA funnel's cash value to
  the user from Topstep's current, sourced rules and fees: expected net
  cash, its distribution and the chance of losing all fees, at zero edge
  and at small edges, with fat-tailed daily returns from the owned
  2019-2024 training stores (return magnitudes only, demeaned) and D8
  costs, for 50K, 100K and 150K, both payout paths and a grid of sizing.
  No purchase, no edge test, N unchanged, and every modelled practice
  checked against Topstep's terms. The program otherwise waits for the
  AiTrader readout.
- 2026-10-10 (user, planning chat): V33. After E.19 (commit 647af55).
  E.19's verdict is accepted: at zero edge the Topstep funnel loses money
  for the user at every size, path and sizing within the terms (best case
  50K, -$250 per cycle); break-even net Sharpe about 0 at 50K, 0.34 to
  0.52 at 100K, 0.54 to 0.86 at 150K. Fable reproduced the headline.
  1. No Combine is bought until a strategy passes a registered test and
     its follow-up reads with a net Sharpe of about 0.5 or more. Then:
     50K, Consistency path, DLL at purchase, Back2Funded, keep-D payouts,
     and a hard fee budget of $1,000 fixed before the first purchase and
     never raised after losses (E.19 return, section 7).
  2. Hyperliquid: the user reports BC residents are not restricted. It is
     parked for a later personal-capital phase. Its base taker round trip
     (0.090% of notional) costs more per notional than CME index futures
     (D8: MNQ about 0.4 bp, NQ about 0.3 bp), so it is not a cost fix.
  3. AiTrader is an options strategy (user). It cannot trade at Topstep
     and stays a separate track; a positive readout and replay test would
     point to a small defined-risk options account, not to an XFA.
  4. H2 (month-end NQ/ZN, multi-day, t 1.52, n 56) is noted as a
     personal-account candidate only; it is not pursued now.
  5. Stage E.20: an ML pattern search. It runs the ML route's frozen net
     pipeline (STAGE_E_ML_V2_DESIGN V2.3 to V2.9: ridge and shallow
     LightGBM, cost gate, 50K sizing, nested CPCV), which never ran
     because Gate 0 stopped v2, on the E.12 training stores
     (2019-05-06..2024-02-29) of the 17 roots with owned 2010-2019
     history. Its 45 configurations are registered before any fit, as
     V2.9's trial count requires (N 480 -> 525). If the nested
     out-of-sample record clears E.20's screen, the one final model is
     frozen, as C1's M1 was (V2.10 (a)), registered as one test (N 526)
     and evaluated once, backward, on the owned 2010-2019 stores: nine
     years of data no part of the search reads, in place of the 1.2-year
     research window as the first confirmation. The user chooses this
     search; it narrows V28, which barred ML layered on the unpassed base
     rules. Shallow models only: no DNN or RL. The research window and
     holdout-2 stay unread; a pass leads to a forward research-window
     read and then holdout-2, each in its own stage. No purchase, no
     Databento call.
- 2026-10-10 (user, planning chat): V34. Amends V33 item 5 before E.20
  runs, after the planning chat's literature run
  (reports/stage_e20_briefs/literature_planning_2026-10-10.md). E.20 is
  not run tonight. It runs with Ultracode on, launched interactively.
  1. Part A: one research agent per root (17, opus high, 4 at a time)
     checks that root's published intraday evidence since 2015, audits
     its feature availability over 2010-2019 and 2019-2024, and proposes
     at most two literature-sourced features.
  2. Part B: H6, rest-of-day to last-half-hour momentum (Baltussen, Da,
     Lammers and Martens, JFE 2021), the only published effect whose
     numbers clear the cost gate (about 2.7 bp gross per trade on the
     equity portfolio against MNQ's 0.4 bp), tested directly on NQ at MNQ
     cost on 2020-06..2024-02, after the paper's sample: T1 always, T2
     above the trailing 60-date median of |r_ROD| (Rosa 2022), and T3 on
     negative prior-day GEX only if its source is cleared under its terms.
     Registered and evaluated once before the search reads data. The
     program's CP1 port tested the overnight-plus-first-half-hour form;
     the rest-of-day form was never screened (E.13 section 2.7).
  3. Part C: the V33 search, with a decision time t4 = F_X - 60 min, the
     r_ROD features, and Part A's accepted features. Market orders only:
     the literature finds passive fills mostly adverse.
  4. Dropped from the shortlist: the overnight drift (decayed since 2021,
     overnight hold), closing-auction distortions (overnight), and
     pre-announcement drift and noise-area momentum (unsized; the latter
     close to the failed opening-range family).
- 2026-10-10 (user, planning chat): V35. The subagent concurrency cap is
  raised from 4 to 8 (.claude/settings.json, CLAUDE.md, ORCHESTRATION.md),
  and the web-search budget from 1,000 to 1,500 a session. Compute-heavy
  workers (model fits, store builds) stay at most 2 at once, after a
  free-memory check (the ThinkPad has 14 GB). E.20's Part A readers run 8
  at a time; V34 item 1's "4 at a time" is superseded.
- 2026-10-10 (user, planning chat): V36. E.20's 17 Part A readers run all
  at once, each with unchanged instructions and effort. The settings cap
  is raised to 17 (the cap is not enforced under ultracode, so the
  prompt's number governs); the default working limit stays 8, and
  compute-heavy workers stay at most 2. Supersedes V35's "8 at a time"
  for Part A.
- 2026-10-10 (user, planning chat): V37. Standing rule: run as many
  workers in parallel as possible whenever it costs nothing in per-worker
  depth (same instructions, model and effort as alone), the items are
  independent, memory is safe (compute-heavy workers bounded by RAM, at
  most 2 at once on the ThinkPad unless a measured peak allows more), and
  usage allows. Settings cap raised to 20. Stage prompts state the
  parallel count per step. Supersedes the default working limit of 8 in
  V35 and V36.
- 2026-10-10 (user, planning chat): V37 refined. Parallel readers start
  from one shared brief, a source serving several workers is read once by
  an assigned worker and cited by the rest, and fetches to one site are
  spaced (about 2 workers per domain at once); a throttled or blocked
  fetch is logged, never reported as missing evidence. E.20 updated.
- 2026-10-14 (user, planning chat): V38. After E.20 (commit 2237731;
  H6 T1-T3 FAIL, the search screen FAIL, N 528). The intraday program on
  Topstep is closed: nothing in 528 trials passed, and no published
  post-2015 intraday effect on the 17 roots exceeds 1.5 x the D8 round
  trip (E.20 Part A, 157 evidence rows). No Combine is bought (V33 item
  1). Multi-day holds were barely tested: H2 and H3 only (H4 was an
  intraday fade, not a multi-day hold). Stage E.21 tests the published
  multi-day effects with the longest records (12-month TSMOM, the
  1/3/12-month trend blend, equity turn-of-month, and a combined book with
  H2) on owned 2010-2024 data, no purchase, N 528 -> 532, in a five-hour
  session the user cleared. Carry needs second-contract prices, which are
  not owned. Main venue for a multi-day strategy (user): PropEd Capital,
  the only firm found whose terms allow automated strategies with
  overnight holds (weekend holds need an add-on; plan-level permission to
  be confirmed in writing before any purchase); E.21 sources its rules.
  Phidias Premium (semi-automated only) and a personal IBKR micro account
  are the comparisons. AiTrader (options) stays a separate track; its
  readout is due 2026-10-23.
- 2026-10-16 (user, planning chat): V39. After E.21 (commit 90e41b0;
  T1 TSMOM-12 net Sharpe 0.50 [-0.06, 1.05], T2 0.44, T3 0.15, T4 0.12,
  all FAIL on Holm; N 532). Trend is recorded as consistent with the
  published evidence, not established by this program's bar; no further
  trend variant on 2010-2024. PropEd does not grant automation publicly
  and cannot hold the trend book; no purchase. Automation is no longer
  the user's priority; manual or semi-automated execution is acceptable.
  Closed as directions: prediction markets (user), crypto (every prior
  crypto line closed negative across the user's projects), commodity
  event drift as a standalone stage (planning research: geopolitical news
  is priced fast, OPEC drift has decayed; at most an overlay on trend).
  Small caps: marginal per the planning research; a narrow long-only
  stage (insider clusters, low-turnover issuance/value, index-deletion
  rebound) needs Norgate Platinum (USD 630/yr) and the user's approval;
  not run now. An ML overlay on trend is not built (published gains
  vanish at 2-3 bp of cost). The user's goal of about $10K by year end
  from prop payouts is not reachable with any tested strategy (E.19:
  even at a net Sharpe of 0.5, $10K takes 86-121 Combine purchases);
  no Combine is bought before a strategy passes. The user delegated
  tonight's choices to the planner for a session ending 08:00 PDT:
  Stage E.22 confirms the five unconfirmed Tier A members as frozen on
  owned data (with full-size price paths where D4's power check fails,
  the U8 condition met by this delegation) and designs the micro trend
  book with a frozen forward registration (E22-F1, N 532 -> 533) and a
  paper runner; no purchase, no data fetch. The AiTrader readout
  (2026-10-23) remains the next decision point.
- 2026-10-17 (user, planning chat): V40. E.22 window: E.22 stopped at
  02:41 PDT on 2026-10-16 at a usage limit before any confirmation read;
  the user paused it and approved a new window that night (no
  confirmation read after 02:00 PDT on 2026-10-17, return by 03:00),
  replacing the prompt's 06:30/07:30 times and nothing else. After E.22
  (commit 7547638, pushed): K5-fomc-01 MGC NULL, K3-ldnrev-01 6E NULL,
  K6-limitcont-01 HE NULL by inactivity, K8-flight-01 HEOD MGC NULL,
  K8-wkndbtc-01 inconclusive by design; no Holm rejection. Stage E's
  intraday clusters are closed (E.22 return item 3 accepted); no holdout
  read. The micro trend book design study (not evidence of edge): net
  Sharpe at $25K 0.41 simple-rounded, realized maximum drawdown 63.5%,
  IBKR margin above capital on about 5% of days; the book is not traded
  live at $25K at a 20% target. E22-F1 is registered (N 533) and waits on
  the user's choice of a daily settlement source; nothing is bought.
  The four pre-E.22 freezes that pinned harness v12 stay as recorded.
  Stage E.23 (user): change the hold, not the rule. The program's frozen
  intraday triggers, each unchanged, are tested at 5- and 20-day holds
  entered at the trigger day's settlement, as a new pre-registered
  family in the multi-day track. The measure is alpha over the same
  root's E.21 trend returns, so trend is not counted twice. At most 12
  triggers and 24 trials (N 533 to at most 557), discovery on data the
  trigger was screened on, confirmation once on owned data that never
  selected it; owned data only, no purchase; two five-hour usage windows
  from about 02:00 PDT on 2026-10-17, no outcome read after 10:30 PDT.
- 2026-10-17 (user, planning chat): V41. After E.23 (commit ef2902d,
  pushed; 5 trigger-holds registered, N 533 -> 538; discovery on W_ext
  2011-07..2019-04 read once, largest alpha t 0.55, Holm smallest p
  0.31, no survivor; confirmation read nothing; VerdictVerifier VERIFIED
  WITH NOTES). "The program's intraday triggers at multi-day holds" is
  closed as a direction; no variant (other roots, other holds, the
  opposite H6 direction) is tested on these windows. W_cf
  (2019-05..2024-02, trigger-conditional multi-day outcomes unread) and
  holdout-2 are kept for a hypothesis with a stronger prior; at a true
  net Sharpe of 0.5 no owned window gives a confirmation power above
  about 0.25. No data is bought for this line. The user approves the
  multi-day loader fix (E.23 VerdictVerifier NOTE-2, NOTE-5): stores are
  loaded only up to the read window's last bar, so no read holds later
  bars in memory, and multi-day books write per-unit and per-fill files
  as E.21 did; the change touches base_rules/context.py or multiday/,
  no frozen member, and is built, Fable-reviewed and tested in its own
  stage before the next multi-day read.
- 2026-10-18 (user, planning chat): V42. Forward-test venues. Alpaca has
  no futures (staff, 2026-02), so E22-F1 cannot run there. The user
  accepts IB Gateway: E22-F1 runs on IBKR paper as its daily price
  source (delayed paper data is enough for a once-a-day book), with
  optional IBKR paper orders as a shadow record; its registered verdict
  stays the paper book of its freeze. If IBKR's daily close is not the
  official settlement, the choice between a pre-clock amendment (a new
  registration, N + 1) and a second settlement source returns to the
  user. The user also approves a second forward test on Alpaca paper:
  E22-F2, the same trend rule on US ETFs (fractional longs, no rounding
  problem), a new registration (N 538 -> 539). Warm-up read approved
  (user): E22-F1's first connection session reads daily prices of its
  12 micros from 2024-03-01 to the start date; this spends holdout-2 for
  MGC, MCL and MNG and the research window for the 12 micros, for
  trend-type and multi-day hypotheses only. Intraday registered reads of
  the research window stay possible. ETF prices were never sealed. Stage
  E.24 builds the plumbing (V41 loader fix, IBKR and Alpaca adapters on
  mocks, E22-F2 freeze and registration, warm-up declarations, user
  checklist; no broker connection, no market data read). Stage E.25, in
  parallel, is a research-only pass for a prop-compatible intraday edge
  in sources the earlier passes did not cover (0DTE and dealer gamma,
  order flow, news-driven moves, live audited records, prop firms'
  outcome data, practitioner work, communities as pointers only); no
  data read, N unchanged by E.25. No connector for Reddit, X or YouTube
  exists in the registry; those sites are reached only through search
  results and pages whose terms allow it.
- 2026-10-18 (user, planning chat): V43. V28 amended for order-book
  strategies. The user approves that a machine-learning model may itself
  be the traded strategy, not only a filter on a passing rule, for
  order-book and limit-order strategies, where the patterns may not
  reduce to plain rules. Conditions, all binding: the model, its
  features, labels, training data window, hyperparameters and code are
  frozen and hashed before any outcome read, as E.20's pipeline was;
  every configuration searched counts into N; validation uses purged
  and embargoed cross-validation on the discovery data; the frozen model
  is then tested once on data that never selected it (a separately
  purchased period or the research window under a registered read),
  with the program's bar (Holm, net Sharpe, DSR at N, PBO); costs use the
  measured fill and adverse-selection model from the tick-data pilot,
  never touched-means-filled; and no model trades, on paper or live,
  before it passes. V28 stands unchanged for every other line (no ML
  layer on an untested rule set elsewhere; meta-labeling only after a
  base rule passes). Also recorded (user, 2026-10-18): no paper trading
  for now and no 24/7 gateway on the laptop (E22-F1, E22-F1b, E22-F2 and
  any C1 forward record parked, unregistered, N 538); a Databento pilot
  cap of USD 100 for order-book data (the user reports about USD 120 on
  the account); the later order-book search should use machine learning,
  likely on a more powerful machine.
- 2026-10-21 (user, planning chat): V44. The user's last Max day. After
  E.24 (commit 8da6bec: the loader fix in mdio/, both broker adapters on
  mocks, IBKR's daily close is the last trade, not reliably the
  settlement; E22-F2 not frozen) and E.25 (commit 715ae8e: five
  candidates clear the hurdle on published numbers, none confirmable on
  owned data with power; limit orders rescue no earlier rule; the
  re-dig supports nearly every closure). Accepted. The direction is now
  limit-order and order-book strategies at automation-friendly prop
  firms. Selection method: a blind two-layer ranking of firm-contract
  pairs (Layer 1, contract feasibility: market structure, competition,
  book mechanics, published microstructure evidence, with a gate; Layer
  2, the economics per firm and contract: fees in ticks, limits in
  ticks and daily ranges, position limits, product restrictions,
  automation and order-rate rules, each platform's simulated fill rule,
  latency, firm reliability and eligibility for British Columbia
  residents), criteria fixed before any lookup. Spend rule (user):
  pilot data for ONE contract (the top pair's) and ONE schema only; the
  measurement spec is frozen before the download with a conservative
  fill rule (back of the visible queue, never a fill on a touch alone);
  the purchase comes last in the day's order. Account (user): a new,
  temporary Databento account, ACCOUNT_3 with key variable
  DATABENTO_API_KEY3; the user chose, as a one-time exception for this
  throwaway account, to give the key to the planner rather than enter it
  himself, and will wipe the account once the download is verified; all
  of its funds go to the one contract and schema, the span extended
  backwards from 2023-11..2024-02, never into 2024-03 or later; acct-1
  and acct-2 are not spent. Data move (user): market data moves out of
  the repo folder to /mnt/large-storage/market_data/PropExperiment/ with
  symlinks at the old paths (Stage E.26). E22-F2's code fixes are
  skipped. Stage E.28 also writes a methods brief (the user's priority):
  a gap inventory of the program's methods and deep dives on the
  mathematics and machine learning it never used, with a draft design
  for the ML search under V43. N stays 538.
- 2026-10-21 (Stage E.26, recording V44's instructions and E.25's
  corrections): V45. Five records.
  1. Data move (V44), done in E.26 on 2026-10-21 05:15-05:18 PDT:
     data/sealed, data/processed_hist, data/processed_step2 and
     data/vendor/databento (4,579 files, 9,693,260,747 bytes) now live
     under /mnt/large-storage/market_data/PropExperiment/ (ext4, not
     encrypted, fstab nofail), with absolute symlinks at the old paths.
     Every file's sha256, mode, owner and mtime were checked at the
     destination, read from disk, before the swap (manifest sha256
     778ec621...). Stayed in the repo: data/processed (a link there
     changes ml_route.store's research-root refusal and fails a harness
     test; the fix would be a harness change), data/vendor/release_pages
     (web pages and the scripts the D.1f preflight scans) and
     data/vendor/index_history (11 tracked files), so data/ and
     data/vendor stay real directories. The before and after checks were
     identical: the holdout status byte for byte (unlocks 0), harness v13,
     every freeze verification, the E.20 store sha256 block (34 stores),
     base_rules' row-free preflight over 44 stores, and the data-path test
     subset (285 passed). .gitignore lists the three top-level links
     without a trailing slash; two holdout tests now scan through the
     links and fail on a dangling one. Records written from now on may
     carry /mnt paths (a new seal records original_relpath None). Any
     session that reads data first checks `mountpoint -q
     /mnt/large-storage`. New downloads go straight to the destination
     root. No secret goes on that drive.
  2. ACCOUNT_3 (V44): data/config.py registers acct-3 (ACCOUNT_3_ID, key
     variable DATABENTO_API_KEY3, cap USD 125.00, the credit a new
     Databento account opens with (U5), an upper bound only; no external
     ledger), selectable the way acct-1 and acct-2 are
     (require_databento_key, SpendGate and its ledger lines, the quote
     tool); acct-1, acct-2, their caps and ACTIVE_ACCOUNT (acct-2) are
     unchanged. It is a temporary account for the E.28 order-book pilot
     purchase only (one contract, one schema, 2023-11..2024-02 extended
     backwards, never 2024-03 or later): PILOT_ONLY_ACCOUNTS makes
     data/pull_step2.py refuse a step-2 buy on it before any key is read,
     and data/pull_hist.py already refuses it. A pilot script passes
     account="acct-3" to both SpendGate and require_databento_key, with
     its own session id and caps; its spend bound is V44's "all of its
     funds" (the balance at purchase less a few dollars of margin, under
     the USD 125.00 account cap), which supersedes V43's USD 100 pilot
     cap for this account. The user wipes the account after E.28
     writes "ACCOUNT_3 SAFE TO WIPE". The key was given to the planner as
     a one-time exception the user chose for this throwaway account; it
     is checked by variable name only and never printed, copied or
     logged. Adding the account changes harness members (data/config.py,
     data/pull_step2.py and two frozen tests that pinned a two-account
     registry), so the Stage E harness is now v14, sha256
     2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1,
     whose manifest differs from v13 (dd2bcc60...) only in those four
     entries; every Stage E entry point takes the v14 sha from now on.
     trigger_hold/events.py keeps its v13 pin (a member of the E.23
     freeze), so E.23's runners refuse until the user decides.
     The E.26 lead made this call against its prompt's no-harness-change
     scope, because Task 2 cannot be done otherwise (E.26 return, open
     choice 1).
  3. V34 corrected (E.25 R10, DF1): V34's reason for dropping
     noise-area momentum (Zarattini, Aziz and Barbon, "Beat the Market",
     WP 2024, v2025-09) was "unsized"; the authors' FAQ sizes it ($0.09 a
     share net per trade at a $247 average SPY price, about 3.6 bp;
     futures Sharpe S&P 1.32, Nasdaq 1.23, cost unstated). The drop stands
     on the post-publication evidence instead: no independent S&P test
     after publication (2024-05) is distinguishable from zero and the
     latest are negative (Brusco ES, the paper's rule: -0.61 bp a trade
     net, Sharpe -0.07; Paz SPY out of sample: Sharpe 0.39, t 0.54;
     Delgado 2025-09..2026-08: Sharpe -0.46); the one positive Nasdaq
     test is a pointer (VigorTas NQ after publication, t 1.37 over 585
     days).
  4. V38 amended (E.25 RD2, DF2, DF3, RD4): V38's sentence "no published
     post-2015 intraday effect on the 17 roots exceeds 1.5 x the D8 round
     trip" now reads: no published post-2015 intraday effect on the 17
     roots exceeds 1.5 x the D8 round trip, except three working-paper
     effects whose samples run past 2015, none with a significant
     post-2015 estimate: the pre-refunding-announcement ZN gain (Wang and
     Zhao 2025, cash, +12.62 bp, t 3.32), the pre-FOMC ZN drift (Pan and
     Peng 2026, futures, +7.26 bp, t 2.82, 2004-01..2025-06) and the ES
     3rd-Friday reversal (Baltussen, Terstegge and Whelan, -12.89 bp, t
     -2.40, 2003-2021; 2015-23 not significant alone). Each gives 3 to 15
     events in the research window (power 0.11 to 0.22 at the published
     sizes), so none can be tested with adequate power on owned data. The
     closure of the intraday program (V38) stays in place.
  5. Topstep rules record (E.25 return section 7 item 6):
     reports/stage_e19_rules.json now carries Topstep's Tier 1 news
     window from the help pages fetched 2026-10-21 02:20 PDT (page
     13613539, dateModified 2026-10-20: minis blocked and micros capped
     to 3/6/9 on 50K/100K/150K Combines, by balance on XFAs, 5 minutes
     either side of CPI, FOMC, NFP and PPI; existing positions may be
     held, so R040's "flatten not required" stands with a new source).
     E.19's simulator was not rerun. N stays 538.
- 2026-10-21 (user, planning chat, 11:04 and 16:49-19:20 PDT): V46.
  1. Harness v14 (2e908c81...) kept (E.26 return section 7 item 1).
  2. V45 item 2 confirmed: the pilot's spend bound on acct-3 is all of
     its funds under the USD 125 cap, superseding V43's USD 100 for this
     account only.
  3. No mount check added for /mnt/large-storage (internal SSD; the user
     judged the risk low). The holdout status still fails closed on a
     dangling link (E.26).
  4. E.26 decisions 2 (trigger_hold's v13 pin), 4 (data/processed stays)
     and 7 (/mnt/... paths in new records) stay open for the user. Item 6
     stands as the user said on 2026-10-20: he wipes acct-3 after
     "ACCOUNT_3 SAFE TO WIPE", then removes DATABENTO_API_KEY3 from .env.
  5. Pro plan from about 16:45: E.28 continues as E.28b (fresh session,
     opus high, Ultracode off, at most 2 workers). Fable needs usage
     credits on Pro, so E.28b's remaining review is an Opus 5.5 xhigh
     reviewer in a fresh context that sees only the files it checks. This
     substitution holds only while Fable is unavailable; on Max, Fable
     xhigh reviews return.
  6. Stage E.29 (prompt docs/prompts/STAGE_E.29.md): a simulation-only
     study of combining the ranked contracts in one prop account, launched
     after E.28b's purchase is verified. No outcome read, nothing
     registered, N stays 538. A cross-market lead-lag test (K8 style, CL
     order flow leading QM) waits for the QM pilot's fill results.
