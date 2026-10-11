# Stage E.19 funnel model specification (lead, binding; written 2026-10-10 17:25 PDT)

The lead's modelling decisions for Tasks 2 to 4. Coders implement exactly this; anything this spec leaves open is
reported back, not decided by the coder. Rule values come only from the rules JSON (reports/stage_e19_briefs/
rules_schema.md); no Topstep number is hard-coded in prop_econ/ (tests may use their own hand fixtures).

## 1. Shocks (prop_econ/returns.py, ReturnsCoder)

- Price paths NQ, CL, GC, ZN, 6E from the owned E.12 training stores
  data/processed_step2/<root>/ohlcv-1m_<root>_v_0_2019-05-06_2024-02-29_step2.parquet. Assert every bar's trade date
  is within 2019-05-06..2024-02-29. Nothing else is read: no data/sealed, no research window, no holdout, no
  2010-2019 store, no MES store.
- One row per trade date and path: the frozen D6 day session [O_X, C_X) of that root (find it in the repo; it is the
  window D8's "day buckets" cover). Entry = open of the first bar at or after O_X, exit = close of the last bar
  before C_X; H, L = max high, min low over the window. Skip a date when the window is missing bars at either end,
  or when the instrument changes inside the window (roll); count every skip by reason.
- Dollars per full-size contract: r = (C - O), up = (H - O), dn = (L - O), times the full-size multiplier.
- Demean per path: r' = r - mean(r) over that path's kept dates. sigma_full = sd(r') (ddof 1).
  Long position: z_L = r'/sigma_full, w_L = min(dn, r', 0)/sigma_full. Short: z_S = -r'/sigma_full,
  w_S = min(-up, -r', 0)/sigma_full. (The demeaning moves the close only; the min() keeps w <= min(0, z).)
- Vehicles: NQ -> MNQ, CL -> MCL, GC -> MGC, 6E -> M6E (micro = 1/10 of full: sigma_micro = sigma_full/10);
  ZN has no micro. Round-trip cost per contract: D8 day-session mean RT $ (reports/stage_e2a_costs.json via
  sim.product_costs, read-only) for NQ, MNQ, CL, MCL, GC, MGC, ZN, 6E, M6E; the E.10 cost wall RT_X
  (reports/stage_e10_research/cost_wall.json) as the sensitivity set (cost_model "d8" or "wall").
- Bootstrap source (the fat-tail model): per path, consecutive blocks of 5 trade dates; per block the price path is
  drawn uniformly from the allowed set (all five pooled, or one fixed path for the per-product sensitivity) and the
  block start uniformly from that path's kept-date array (a block may span a skipped date; blocks never wrap).
  Per day a direction sign: +1 or -1 with probability 1/2 each (direction mode "random", the headline), or always
  +1 (mode "long", sensitivity); z, w come from the long or short columns accordingly. Seeded numpy
  Generator(PCG64).
- Normal source (the thin-tail comparison): same product sequence and signs as the bootstrap for the same seed; z ~
  N(0, 1) i.i.d.; w = the minimum of a Brownian bridge from 0 to z on unit time with unit variance:
  w = (z - sqrt(z^2 - 2 ln U)) / 2, U ~ Uniform(0, 1].
- Output: prop_econ.types.ShockSet for (n_paths, n_days) and a ProductSpec tuple; a function that writes the
  per-path summary (dates kept, skips by reason, mean r removed, sigma_full, skew, excess kurtosis of z, share of
  |z| > 4, mean and 1st percentile of w) to JSON.

## 2. Daily step (both phases; prop_econ/funnel.py scalar reference and prop_econ/vec.py vectorized)

State: balance B, floor F (the MLL level, in balance units), so D = B - F is the drawdown distance.

1. D_open = B - F (> 0 while alive). Risk target s* = f x D_open (f = the sizing fraction; grid in section 6).
2. Vehicle for the day (product p from the ShockSet): full-size if s* >= sigma_full(p) or p has no micro, else the
   micro. sigma_u, rt_u = that vehicle's sigma and round trip.
3. Contracts n = s*/sigma_u in mode "continuous" (headline) or floor(s*/sigma_u) in mode "integer"
   (product sensitivity); in both modes n >= 1 (a bot trades at least one contract; below that the realised risk
   exceeds f x D, which is the honest end state of a shrinking account). Lot cap: n x (1 if full else 1/10)
   <= cap_minis, where cap_minis = the Combine's max_minis, or the XFA scaling tier read from the balance at the
   prior session's close (start balance on day 1; boundary per scaling_boundary). If above, n is cut to the cap.
4. Edge. Mode "zero": gross drift 0, k round trips a day (k = 1 or 3). Mode "sharpe S" (net, after costs): gross
   drift per contract per day mu = sigma_u x S/sqrt(252) + k x rt_u, so net = n x sigma_u x (z + S/sqrt(252)).
5. Close P&L = n x (sigma_u x z + mu) - n x k x rt_u. Worst P&L = n x sigma_u x w - n x k x rt_u (no drift credit,
   all costs counted).
6. DLL, if active in this phase (Combine dll_usd, or the XFA DLL when chosen): if Worst <= -DLL and DLL < D_open,
   the day ends at P&L = -DLL (flat, not a breach).
7. MLL (real time): if Worst <= -D_open, the account breaches: P&L = -D_open (liquidated at the floor; gap-through
   overshoot ignored, noted as a limitation) and the phase ends.
8. Otherwise P&L = Close P&L. End of day: B += P&L; floor trails per the phase (section 3/4); counters update.

## 3. Combine attempt (run_attempt)

- B = 0 (relative to the start balance), F = -mll_usd. EOD trailing: F = max(F, min(B - mll, mll_floor_max_rel)).
- Consistency (type best_day_max_frac_of_target, frac c): effective target = max(T, best_day / c); type
  best_day_max_frac_of_profit: pass needs B >= T and best_day <= c x B. Best day = the largest daily P&L so far.
- Pass at EOD when B >= target (as above) and days traded >= min_trading_days. Fail at a breach. Timeout at
  attempt_max_days (default 756) = abandoned, counted as a fail (report the share).
- Output per attempt: passed, length in trading days (the day of the pass or breach counts), end reason.

## 4. XFA life (run_xfa)

- B = start_balance (0), F = B - mll_usd. EOD trailing: F = max(F, min(B - mll, mll_floor_lock)) until the first
  payout; after the first payout F = mll_after_first_payout_usd for good (null: keep trailing).
- Payout request at the START of a day, before trading, when the window since the last payout (all days after the
  previous request day; the request day itself never counts when payout_day_counts_toward_next_window is false) is
  eligible:
  Standard: count of window days with P&L >= winning_day_usd >= winning_days, and window net > 0 when
  net_positive_since_last (after the first payout; before it, B > 0 suffices).
  Consistency: window traded days >= traded_days, window net > 0, and the largest window day P&L <=
  best_day_max_frac x window net.
  Amount = floor to the cent of min(cap (cap_usd_dll when the DLL was chosen and dll_doubles_payout_caps),
  frac_of_balance x B, B - keep_d x mll_usd), requested only if >= payout_min_request_usd. Policy keep_d: 0.0
  (headline "max": the largest amount the policy allows, as soon as eligible) or 0.5 (sensitivity: the V2.8 keep-D
  policy). On a request: B -= amount; the user receives profit_split_trader x amount; F is set per the rule above;
  the window restarts.
- Ends: breach; call-up (global.callup: after_n_payouts n -> the XFA ends right after its n-th payout; the
  remaining balance is worth 0 to the bot in the headline); payout_count_limit reached (ends after that payout);
  horizon xfa_max_days (default 756 trading days after activation; the remaining balance is worth 0; report the
  share alive at the horizon).
- Output per XFA: payout days and gross amounts (padded array, max 64; flag overflow), n payouts, total gross,
  first payout day (or -1), end day, end reason, balance at the end.

## 5. Fees, cycles and campaigns (prop_econ/assemble.py; post hoc on pools of attempts and XFAs)

- Pools: attempt outcomes and XFA outcomes are simulated separately (i.i.d. draws, common seeds across f and edge).
  A cycle is assembled by drawing attempts in sequence until a pass (or the attempt cap), then one XFA, then
  Back2Funded XFAs when that policy is on.
- Trading-day clock; billing period = 21 trading days (30 calendar days x 252/365, rounded).
- Subscription fees (pricing path standard or no_activation_fee; P = monthly price, R = reset price, DLL discount
  applied when the DLL is chosen): pay P at the start; a rebill pays P every 21 trading days after the last start or
  reset while the subscription is alive, and adds one reset credit when rebill_adds_reset_credit; a failed attempt
  is followed by a reset next day, which uses a credit if any, else pays R; a reset restarts the rebill clock when
  reset_pushes_rebill. A pass ends the subscription (unused credits are lost) and the activation fee is paid.
  Every P or R payment is one "Combine purchase".
- Back2Funded (policy on/off): an XFA that breaches before its first payout may be reactivated, at most max_per_xfa
  times, at price_usd (less the DLL discount when chosen); it is a fresh XFA drawn from the pool.
- Attempt cap per cycle (stop rule within a cycle): default 60 attempts; a cycle that hits it ends with no XFA.
- Cycle outputs: fees paid and their days, purchases, user payout cash (after the split) and their days,
  net = cash in - fees.
- Campaign: slots in {1, 5} (5 = global.max_active_xfas; each slot runs cycles back to back, so at most 5 XFAs are
  live at once; slots independent, i.e. different products or uncorrelated bots; the copy-traded case, all five
  slots trading the same fills, is reported separately as five times one cycle). For targets $5,000 and $10,000 of
  cumulative user payout cash: per replication, the number of Combine purchases made (across all slots) when the
  target is first reached, the total fees by then (purchases + activations + Back2Funded), and the elapsed trading
  days; "not reached" when a cap of 400 purchases is hit. Report P50 and P80 of each (the K that reaches the target
  with 50% / 80% probability).

## 6. Grid and outputs (Task 3/4 runner, written after the modules pass their tests)

- Sizes 50K, 100K, 150K; payout path standard / consistency; DLL off / on; pricing path standard /
  no_activation_fee (fees only, post hoc).
- Edges: zero (k = 1 and k = 3); net Sharpe S in {0, 0.15, 0.3, 0.5, 0.75, 1.0}.
- Sizing f in {0.05, 0.10, 0.15, 0.20, 0.25}; plus 0.35 and 0.50 labelled "diagnostic, outside the policy band".
- Tail model: bootstrap (headline) and normal. Direction random (headline); long only as a zero-edge sensitivity.
- Cost model d8 (headline) and wall (zero-edge sensitivity). Mode continuous (headline); integer per product.
- Payout policy max (headline) and keep-D 0.5 (sensitivity). Back2Funded off (headline) and on.
- Every UNSOURCED rule: both readings at zero edge and S = 0.5 for every size and path at f in {0.10, 0.25}.
- Paths: 20,000 attempts and 20,000 XFAs per configuration (common random numbers across f and edge for a given
  size, tail and seed); 20,000 campaign replications.
- Per configuration: pass probability and mean attempt length; per-XFA mean user cash, P(any payout), mean time to
  the first payout; per cycle: mean net cash and its Monte Carlo SE, 5th / 50th / 95th percentiles, P(no payout,
  i.e. all fees lost); expected net cash per Combine purchase = E[cycle net] / E[cycle purchases]; per funded XFA:
  E[user cash] - activation fee. Break-even net Sharpe by linear interpolation between grid edges where the cycle
  net changes sign. In-simulation optimum f per rule set and edge, with its SE and the paired SE of its gap to the
  runner-up.
- Compute limits (CLAUDE.md): nice 10, at most 8 worker processes, chunked paths, resumable (one result file per
  configuration, skipped when present), progress to a log file.
