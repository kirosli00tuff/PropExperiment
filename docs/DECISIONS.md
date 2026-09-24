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
