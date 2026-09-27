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
