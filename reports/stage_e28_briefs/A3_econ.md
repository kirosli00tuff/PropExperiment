# Stage E.28 A3: firm-contract economics per (firm, candidate) pair (spec section 3)

EconCoder-OpusXHigh, 2026-10-21 (times PDT). Spec: reports/stage_e28_ranking_spec.md, sha256 89347e97...a5f (checked
against the hash in reports/stage_e28_STATE.md), applied literally. Outputs: reports/stage_e28_briefs/A3_econ.json (one
record per pair with every field the brief lists, plus provenance, grid checks and sensitivities) and this file. Code
and per-pair evaluation logs: reports/stage_e28_briefs/work/A3_econ/ (A3_funnel.py model, A3_models.py firm mapping,
A3_inputs.py inputs, A3_run.py driver, A3_gridcheck.py grid confirmation and monotonicity scan, A3_opt2.py Bulenox
Option 2, A3_regress_e19.py and test_A3_econ.py checks, pairs/<firm>__<code>.json full evaluation lists,
gridcheck/<firm>__<code>.json grid curves, A3_log.md). Nothing is scored here.

Data used: the stage's fact files only (A0_contract_stats.json for sigma_1m, R_d and owned ADV; A1_<family>.json for
ticks, tick values, spreads and published ADV; A2_firm_<firm>.json/.md for plans, fees and limits; A2_platforms.json).
No market data file was opened. prop_econ/ was imported read-only (PYTHONDONTWRITEBYTECODE=1); no file under it was
changed. Topstep's rules come from reports/stage_e19_rules.json as refreshed by Stage E.26 Task 4 (234 rules, sha256
01155d26...; reports/stage_e26_STATE.md, done 02:25), as the brief directs; the values the simulator reads are the same
as in E.19's record (pre-E.26 copy, sha256 ebc29f8b...): both load to equal 50K rules and give identical regression
numbers (section 8). The A2 Topstep reader found no contradiction between that record and today's pages
(A2_firm_topstep.md section 8); the gaps it lists (per-product commissions, volatility caps, product list) are taken
from the A2 record.

## 1. Summary

| firm | pairs | computed | mu*_lim <= 4 | mu*_mkt <= 4 | mu10K <= 4 | not computed (sigma unknown) |
|---|---|---|---|---|---|---|
| topstep | 33 | 30 | 21 | 20 | 20 | MET, SI, SIL |
| lucid | 23 | 21 | 21 | 21 | 16 | SI, SIL |
| tradeify | 24 | 23 | 17 | 16 | 16 | SI |
| mffu | 27 | 24 | 20 | 20 | 16 | MET, SI, SIL |
| bulenox | 25 | 23 | 15 | 15 | 15 | MET, SI |

132 (firm, candidate) pairs are listed (each firm's product list from its A2 record, restricted products
included and flagged). 121 are computed. 11 are not (SI, SIL and MET at the firms that list them): sigma_1m is
unknown for them, and section 3 gives no default for it. Every computed pair has mu*_lim, mu*_mkt, mu10K and the cost
per attempt from 20,000 paths on common random numbers (seed 20261021). mu*_mkt = mu*_lim + 1.00 wherever both are
<= 4, because S_rt = 1 tick for every candidate (sourced for CL, GC, SI and the four Treasuries; the spec's default
"u" elsewhere). The lowest mu*_lim values are Topstep ZB 0.11, Topstep ZN and QG 0.19, Lucid QG 0.22 and MFFU QG 0.25
(MFFU QG is listed but restricted now: flagged). MNQ, the baseline, needs mu*_lim 2.21 (Lucid), 3.26 (Topstep), 3.86
(Tradeify) and "> 4" at MFFU and Bulenox; its mu10K is "> 4" at all five firms. Most micro products are "> 4": a
round trip costs 2 to 4 ticks in fees, and at Tradeify and Topstep a one-lot micro day rarely clears the USD 150
winning-day threshold that payouts need (section 8).

Checks. All 363 thresholds (121 pairs x 3) were confirmed on the 0.01-tick grid: no checked grid point below any
threshold has EV >= 0 (or P10K >= 0.5), so no value was corrected. One stored point per pair was recomputed from
scratch, and all 121 match bit for bit. Monotonicity in mu FAILS as a property (EV has a trough below the break-even;
section 8), which is why the grid confirmation was run. The thresholds are unaffected. E.19's published -250 headline
cannot be rerun here, because its bootstrap reads stores dated to 2024-02-29 and the stage's data rule forbids that.
E.19's normal-tail twin of the same job was reproduced exactly instead (56 numbers, maximum difference 0.0). 14 unit
tests pass, including the per-trade layer's daily mean T (mu - c) v and SD sqrt(T) sigma_T v. Nothing is scored.

## 2. Method

### 2.1 Per-trade layer (spec, applied literally)
T = 20 round trips per trading day, 1 contract, independent trades; gross P&L per trade normal with mean mu and SD
sigma_T = sigma_1m (ticks). Cost per round trip c_lim = F_rt / v (limit case) or c_mkt = F_rt / v + S_rt (market case).
Daily P&L in USD is then exactly normal with mean m = T (mu - c) v and SD s = sqrt(T) sigma_T v (test 4 checks both
the formula and the equality in law with the sum of 20 simulated trades). The day's intraday path is E.19's normal
source (prop_econ.returns.normal_shocks): a Brownian bridge from 0 to the close, whose minimum (the worst intraday
P&L, used for drawdown breaches and daily loss limits) is drawn given the close with E.19's formula
w = (x - sqrt(x^2 - 2 ln U)) / 2. Given its endpoint a Brownian motion with drift is a Brownian bridge, so the drift
enters only through the close. The bridge maximum (same formula, mirrored) is drawn only where a rule trails the
intraday high (Bulenox Option 1). Size 1 is forced through E.19's own day step (prop_econ.vec.day_step_vec) with the
sizing fraction f = 1e-12, so n = max(f D / sigma, 1) = 1 contract (test 5 replays this by hand).

### 2.2 The funnel: E.19's simulator where it fits
A cycle is E.19's: Combine/evaluation attempts in sequence (fees, rebills, resets, up to 60 attempts) until a pass,
the activation, then one funded account until its end (breach, payout limit, or the 756-day horizon). Unchanged
prop_econ code: simulate_attempts (Topstep, Lucid, Tradeify, MFFU evaluations, each on a SizeRules carrying its rules),
simulate_xfas (Topstep XFA), day_step_vec, tier_cap_vec, cents_floor_vec, assemble_cycles (fees and cash events), the
FeeTerms rebill/reset/credit logic and the API wallet convention (one API subscription per started billing period of
the cycle). Two thin extensions in A3_funnel.py reuse the day step: simulate_attempts_intraday (the floor trails the
day's high: F_eff = max(F, min(B + H - MLL, lock)), the high taken to come before the low) and simulate_funded (E.19's
XFA loop with general payout rules: winning-day counts with a threshold, traded-day counts, window profit minimums,
a minimum balance, best-day consistency on the window or cumulative, per-payout caps, a buffer, a payout-count limit,
weekly request days and uncounted days after a payout). On Topstep's rules simulate_funded equals simulate_xfas path
for path, on both payout paths and with the DLL option (test 1), and both intraday code paths reduce exactly to E.19's
EOD simulators when the high is removed (test 2).

### 2.3 Common random numbers and seeds
One set of standard draws per phase, (20,000 paths x 756 days): z ~ N(0,1), E1 = -ln U (bridge minimum) and, for
intraday rules only, E2 (bridge maximum); seeds prop_econ.grid.derive_seed(20261021, "e28a3", phase, name). Every pair,
firm and mu uses the same draws; a pair and a mu only shift and scale them. Cycle index draws (20,000 cycles x 60
attempts, 3 funded columns) are seeded "cycle"; campaign draws per (block of 500 replications, round). Draws are
stored as float32 and used in float64.

### 2.4 Thresholds on the 0.01-tick grid
EV(mu) = mean net cash per cycle = all withdrawals (trader's share) minus all fees, the API subscription included
(E.19's net), over 20,000 cycles. mu*_lim and mu*_mkt: the smallest grid mu in [0, 4] with EV >= 0 in the limit and
market case. mu10K: the smallest grid mu with P(net cash >= USD 10,000 within 250 trading days) >= 0.5, limit case.
Search: bisection on the integer index k (mu = 0.01 k), invariant f(lo) < 0 <= f(hi), after f(400) and f(0); "> 4"
when f(400) < 0. The final bracket is the spec's grid check: each record's grid_check stores f(k*) >= 0 and
f(k* - 1) < 0. Because EV depends on mu only through d = mu - c, evaluations are cached by d and shared between cases;
with S_rt = 1 tick for every pair, mu*_mkt = mu*_lim + 1.00 by construction whenever it is <= 4.

Bisection is exact only for a nondecreasing f, and EV is not monotone in mu (section 8), so every computed pair's
thresholds are then confirmed on the grid itself (A3_gridcheck.py, same common random numbers; d = 0.01 j - c_lim on
the lattice j, the market case at j = k_mkt - 100): every j = 0 mod 10 (a 0.10-tick sub-grid) below each threshold
(EV: j from -100 to the market threshold and from 0 to the limit threshold; P10K: 0 to the mu10K threshold; up to
mu = 4 when a threshold is "> 4"), every grid point in the 0.10 ticks below each threshold found, and every grid point
of any sub-grid gap with an end near the threshold (EV >= -max(5 SE, USD 100), or P10K >= 0.40). A threshold is
confirmed when no checked point below it has f >= 0; a point that did would replace the bisection value by the
smallest grid point with f >= 0 (the spec's definition). One stored point per pair is also recomputed from scratch
and must equal the record exactly. Points in a sub-grid gap whose two ends are both far from the threshold are not
evaluated: the check assumes EV and P10K do not swing across the threshold and back inside 0.10 ticks there.

### 2.5 Cost per attempt, mu10K campaign, room
cost_per_attempt_usd: expected evaluation-stage fees (purchase or first month, rebills, resets) per evaluation attempt
at mu = 0, limit case (ratio of means over the 20,000 cycles). Variants in the record: plus the API over the
evaluation stage; all fees including activation and API. The mu10K campaign runs one account at a time: cycles back to
back, the next starting when the previous ends (all attempts failed, or the funded account breached, ended by its
payout limit or reached the horizon); events at elapsed day t <= 250 count, fees before cash on the same day, the API
paid per started period (E.19's api_periods_at); 20,000 replications (test 7 checks it against a plain loop over
E.19's scalar cycle assembly). room = MLL / (R_d v); DLL_ticks = DLL / v; position_limit = contracts of that product
allowed at the 50K evaluation stage (text in position_limit_text).

## 3. The 50K plans mapped onto the funnel

Each firm's standard 50K plan is the first 50K evaluation plan its A2 reader found on the pricing page (spec
section 3). kind: exact = represented as stated; conservative = the simulator cannot represent it or the record is
unclear, and the form harder on the trader is used; ignored = no effect on a 20 round-trip, size-1, 1-minute-hold
strategy; policy = the trader's choice, fixed as stated.

### 3.1 topstep: 50K Trading Combine, Standard Path (USD 49/month)

Fees in the model: start 49.00; rebill 49.00 every 21 trading days (credit True, reset pushes rebill True); reset or re-purchase 49.00; activation 149.00; trader split 90%; API 14.50 per started 21-trading-day period; attempt cap 60; evaluation horizon 756 trading days; drawdown trailing eod in the evaluation.

| rule | firm value (A2 record) | model form | kind |
|---|---|---|---|
| plan | 50K Trading Combine, Standard Path, USD 49/month (A2 1.1) | E.19 headline rules, 50K | exact |
| evaluation | target 3,000; MLL 2,000 EOD trailing, intraday check, locks at start; best day < 55% of profit; min 2 days; no time limit | prop_econ simulate_attempts on the refreshed record | exact |
| fees | 49/month rebill every 30 days (21 trading days), reset 49, a rebill adds a reset credit, a reset pushes the rebill, activation 149 | prop_econ fee_terms(standard, DLL off, Back2Funded off) | exact |
| funded | XFA: start 0, MLL 2,000 EOD, lock 0, floor 0 after the first payout; Standard path 5 days of 150+, net > 0 since last, 50% of balance capped 2,000, min 125, 90/10, payout day not counted | prop_econ simulate_xfas (standard path) | exact |
| DLL | optional 1,000 at purchase (doubles caps) | not chosen (the standard plan's default) | policy |
| Back2Funded | 599, up to 2 before the first payout | off (E.19 headline) | policy |
| LFA call-up | discretionary (0.71% of XFA traders in 2025) | no automatic call-up (E.19 L-rule) | exact |
| API | ProjectX API USD 14.50/month | E.19 wallet: per started 21-day period of the cycle | exact |
| XFA scaling 2/3/5 lots, position caps | volatility caps CL/QM/GC 3, MCL/MGC 30, SI/HG 0 | size 1 always fits except caps of 0 (flagged) | ignored |
| Tier 1 news | minis: no new opens 5 min either side of CPI/FOMC/NFP/PPI | not modelled (R criterion) | ignored |
| commission | per-product table (A2 section 2); conflict: $3.70/lot simulated Combine fee | product table both stages; the 3.70 reading as a sensitivity | conservative |
| XFA inactivity 30 days, max 5 XFAs | - | one account, trades every day | ignored |

### 3.2 lucid: LucidPro 50K (USD 172 one-time, DLL on)

Fees in the model: start 172.00; no rebill; reset or re-purchase 120.00; activation 0.00; trader split 90%; API 0.00 per started 21-trading-day period; attempt cap 60; evaluation horizon 756 trading days; drawdown trailing eod in the evaluation.

| rule | firm value (A2 record) | model form | kind |
|---|---|---|---|
| plan | LucidPro 50K, USD 172 one-time, DLL-on version (A2 1a) | start fee 172, no rebills | exact |
| evaluation | target 3,000; MLL 2,000 EOD trailing, locks at +100 once above 52,100; DLL 1,200 soft; no consistency; min 1 day | simulate_attempts with combine.dll_usd 1,200, floor cap +100 | exact |
| breach test | 'If your account balance reached the MLL' (intraday vs EOD not stated) | intraday worst P&L against the floor (E.19 form) | conservative |
| reset | USD 120 restarts a failed evaluation | reset fee 120 after every failure | policy |
| activation | none | 0 | exact |
| funded | start 50,000, MLL 2,000 EOD, locks at 50,100; buffer 52,100; min profit 500 per cycle; best day <= 40% of cycle profit; 3 days to payout; min 500; max 2,000 then 2,500; 90/10 | extension: traded_days 3, window net >= 500, consistency 0.40 window, buffer 2,100, caps 2,000 / 2,500, min 500, frac 1 | exact |
| funded DLL | 1,200 below 52,100, then 60% of peak EOD profit (soft) | fixed 1,200 throughout | conservative |
| payout count | Payout 5 is the maximum level; then live review pool (discretionary), sim accounts close on going live | funded account ends after the 5th payout; live stage valued at 0 | conservative |
| payout day | not stated | payout day not counted in the next window | conservative |
| inactivity 30 days, 5 funded per household | - | one account, trades every day | ignored |
| microscalping | flag if > 50% of profit from holds <= 5 s | 1-minute holds | ignored |
| API | no Lucid API page; no API fee found | 0 | exact |

### 3.3 tradeify: Growth 50K (USD 145 one-time)

Fees in the model: start 145.00; no rebill; reset or re-purchase 95.00; activation 0.00; trader split 90%; API 0.00 per started 21-trading-day period; attempt cap 60; evaluation horizon 756 trading days; drawdown trailing eod in the evaluation.

| rule | firm value (A2 record) | model form | kind |
|---|---|---|---|
| plan | Growth 50K, USD 145 one-time (A2 1.1-1.2) | start fee 145, no rebills | exact |
| evaluation | target 3,000; MLL 2,000 EOD trailing enforced in real time, no lock; DLL 1,250 soft; no consistency; min 1 day | simulate_attempts, floor cap +inf, combine.dll_usd 1,250 | exact |
| reset | USD 95 | reset fee 95 after every failure | policy |
| activation | none | 0 | exact |
| funded | start 50,000, MLL 2,000 EOD, locks at 50,100 (EOD 52,100 or first request); DLL 1,250; request needs balance >= 53,000 and 5 days > 150 since last payout; caps 1,500 / 2,000 / 2,500 / 3,000; min 500; stay above 50,100; 90/10 | extension: win > 150 x 5, min balance 3,000, caps as stated, buffer 100.01, min 500, lock +100 | exact |
| funded consistency | 35% (Consistency Rule article not fetched: wording unverified) | best day < 35% of the window profit (strict) | conservative |
| live move | may be moved to Live after any payout (discretionary) | no automatic move | exact |
| microscalping | > 50% of trades and profit from holds > 10 s | 1-minute holds meet it | ignored |
| flat 16:45 ET, weekly activity, 15 evaluations a month, 5 funded | - | - | ignored |
| payout day | not stated | payout day not counted in the next window | conservative |
| API | Tradovate API only on live; no API fee found | 0 | exact |

### 3.4 mffu: Builder 50K Default (USD 153 one-time)

Fees in the model: start 153.00; no rebill; reset or re-purchase 153.00; activation 0.00; trader split 80%; API 0.00 per started 21-trading-day period; attempt cap 60; evaluation horizon 756 trading days; drawdown trailing eod in the evaluation.

| rule | firm value (A2 record) | model form | kind |
|---|---|---|---|
| plan | Builder 50K Default, USD 153 one-time (A2 1a) | start fee 153, no rebills | exact |
| evaluation | target 3,000; MLL 2,000 EOD trailing, locks at +100; DLL 1,000 soft pause; no consistency; min 1 day (plan box says min 2) | simulate_attempts, floor cap +100, DLL 1,000, min 2 days | conservative |
| breach test | 'Open equity losses are counted ... at the end of the trading day' | intraday worst P&L (E.19 form, stricter) | conservative |
| reset | no reset price found; a failed account needs a new evaluation | every failure buys a new evaluation at 153 | conservative |
| activation | 0 | 0 | exact |
| funded | start 0, MLL 2,000 EOD, locks at +100; DLL 1,000; buffer 2,100; first payout >= 500 above buffer, later >= 500 since last; >= 2 traded days; best day <= 50% of cycle profit; 500..2,000; 80/20 | extension: traded_days 2, min balance 2,600, window net >= 500 after the first, consistency 0.50 window, buffer 2,100, cap 2,000, min 500 | exact |
| floor after payout | not stated in the Builder guide; older article: MLL resets to $100 | floor fixed at +100 at the first payout | conservative |
| payout count | max 5 sim payouts, then promotion to live (Blue Row Capital) | funded account ends after the 5th payout; live stage valued at 0 | conservative |
| payout day | not stated | not counted in the next window | conservative |
| inactivity 7 days, 1 Builder sim funded | - | one account, trades every day | ignored |
| API | no MFFU API documented; no API fee found | 0 | exact |

### 3.5 bulenox: Qualification 50K, Option 1 trailing (USD 175 one-time, 30 days)

Fees in the model: start 175.00; no rebill; reset or re-purchase 175.00; activation 148.00; trader split 90%; API 100.00 per started 21-trading-day period; attempt cap 60; evaluation horizon 21 trading days; drawdown trailing intraday in the evaluation.

| rule | firm value (A2 record) | model form | kind |
|---|---|---|---|
| plan | Qualification 50K, Option 1 (trailing, listed first), USD 175 one-time, 30 days of access (A2 1.1-1.2) | start fee 175 | exact |
| evaluation | target 3,000; drawdown 2,500 trailing intraday on equity incl. open P&L; locks at +100 (value 52,600); no DLL; no consistency; no minimum days | extension: floor trails the day's high, taken to come before the low (conservative ordering); min 1 day | conservative |
| 30-day access | hard 30-calendar-day clock per purchase; a reset (78) does not extend it | attempt horizon 21 trading days (E.19 30-day conversion); every attempt is a fresh purchase at 175; the 78 reset is not used | conservative |
| activation | 148 one-time per Master account | 148 at the pass | exact |
| pass review | manual review, queue, 7-day activation link | Master starts the next trading day | ignored |
| funded (Master) | drawdown 2,500 intraday trailing, locks at +100; 10 trading days per payout; reserve 2,600 above start; min 1,000; max 1,500 for payouts 1-3; best day <= 40% of total P&L, cumulative; weekly processing (request by Fri, paid Wed; days to Wed not counted) | extension: intraday trailing, traded_days 10, buffer 2,600, min 1,000, caps 1,500, cumulative 0.40, requests at the start of day 0 of each 5-day week, 2 further days not counted | exact |
| split | 100% of the first 10,000 per trader profile, then 90% | 90% throughout | conservative |
| after 3 payouts | transition to a live Funded account at Bulenox's discretion; nothing carries over; declining closes the Master | Master ends after the 3rd payout; live stage valued at 0 | conservative |
| API | third-party API / Trader Composite fee USD 100/month | E.19 wallet: per started 21-day period | exact |
| third-party algorithm review; scalping algorithms banned | - | A criterion | ignored |
| market data | non-professional free; professional 116/month | non-professional | policy |

## 4. Rules not representable as stated, and the conservative forms used

Firm rules (from the tables above):
- Topstep: the $3.70/lot simulated Combine fee conflicts with the per-product table; the table is used, 3.70 as a
  sensitivity.
- Lucid: breach test intraday (not stated); funded DLL fixed at 1,200 (the LucidScale 60%-of-peak DLL after 52,100 is
  not modelled); the funded account ends after payout 5 (live review is discretionary; the live stage is valued at 0);
  commission per side x 2 with exchange/NFA inclusion not stated (the 'u' rule fee as a sensitivity).
- Tradeify: the 35% funded consistency rule's article was not fetched; best day < 35% of the profit since the last
  payout (strict) is used; discretionary live moves are not triggered.
- MFFU: evaluation minimum 2 days (the plan box) rather than 1 (the rules table); intraday breach test although the
  guide counts open losses at the end of the day; no reset price, so every failure buys a new evaluation (153); the
  floor fixed at +100 after the first payout (older article); the account ends after the 5th sim payout (the live
  stage at Blue Row Capital is valued at 0).
- Bulenox: Option 1's intraday trailing drawdown with the day's high taken before its low; the 30-day access window
  as a 21-trading-day attempt horizon with every attempt a fresh 175 purchase (the 78 reset inside the window is not
  used; a trader can always do at least this well, so the form is a lower bound); 90% split throughout (the 100% on
  the first 10,000 per profile is not credited); the Master account ends after the 3rd payout (the discretionary live
  transition carries nothing over and the live terms are not public); weekly processing as requests only on day 0 of
  each 5-day week with the next 2 days not counted.

Model-wide forms (all firms): the payout day is not counted toward the next window where the firm does not say;
payouts are paid at the request (no processing lag) except Bulenox's weekly cycle; balances left at the 756-day
horizon are not credited (E.19's convention); live stages after a discretionary or count-based call-up are valued at 0;
optional DLLs, Back2Funded and paid add-ons are not bought; resets are bought after every failure where the firm sells
one (Topstep with its rebill credits, Lucid 120, Tradeify 95); payouts by a route without a transfer fee.

## 5. Inputs per candidate

Lead decisions applied exactly: OC-1 (sigma_1m and R_d in ticks for a candidate without owned window data from the
owned sibling on the same price, x_ticks(cand) = x_ticks(sibling) x tick(sibling) / tick(cand), units checked; volume
never transfers) and OC-2 (ADV: A0's v_0 median for owned roots, else A1's published figures; both kept; ADV is not an
input of the economics and is passed through). SIL, SI, MET, ETH and the micro yields have no owned data and no A1
value for sigma_1m, so their pairs are not computed (the spec's section 3 gives no default for sigma). S_rt: the A1
readers sourced a one-tick touch for CL (volume statement), GC and SI (CME, all or most hours) and the four Treasury
futures (> 99% of the day at the minimum increment); everything else is the spec's default 1 ("u"). The figures the
readers found for 6E (1.2), ZC (1.26), ZS (1.118) and ZW (1.1) are means, not medians, and enter only a sensitivity.
Tick values agree with A0 wherever A0 has them (v_matches_A0 in the JSON).

| code | tick | v USD | sigma_1m ticks | R_d ticks | source of sigma_1m and R_d | S_rt | ADV owned (A0 v_0) | A1 published ADV fields |
|---|---|---|---|---|---|---|---|---|
| 6A | 5e-05 USD per AUD | 5.0000 | 3.093 | 138.0 | owned A0 window 2022-11-01..2023-10-31 (257 trade dates) | 1 (u) | 82,950 | adv_latest_published, adv_pre_pilot_published |
| 6E | 5e-05 USD per EUR | 6.2500 | 3.558 | 153.0 | owned A0 window 2022-11-01..2023-10-31 (257 trade dates) | 1 (u; mean 1.2) | 176,291 | adv_latest_published, adv_pre_pilot_published |
| CL | 0.01 USD per barrel | 10.0000 | 6.300 | 244.0 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (sourced) | 227,772 | adv_published_latest |
| GC | 0.1 USD per troy ounce | 10.0000 | 5.293 | 220.5 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (sourced) | 160,118 | - |
| HG | 0.0005 USD per pound | 12.5000 | 3.142 | 159.0 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (u) | 59,578 | - |
| M2K | 0.1 index points | 0.5000 | 10.008 | 341.0 | OC-1 sibling RTY: x_ticks(RTY) x tick(RTY) / tick(M2K) = x 1 (A1 ticks 0.1 / 0.1 index points) | 1 (u) | - | adv_nov2022, adv_dec2022, adv_2022_full_year, adv_oct2023, adv_ytd_jan_oct_2023, adv_derived_2022-11_2023-10 |
| M6A | 0.0001 USD per AUD | 1.0000 | 1.547 | 69.0 | OC-1 sibling 6A: x_ticks(6A) x tick(6A) / tick(M6A) = x 0.5 (A1 ticks 5e-05 / 0.0001 USD per AUD) | 1 (u) | - | adv_latest_published, adv_pre_pilot_published |
| M6E | 0.0001 USD per EUR | 1.2500 | 1.779 | 76.5 | OC-1 sibling 6E: x_ticks(6E) x tick(6E) / tick(M6E) = x 0.5 (A1 ticks 5e-05 / 0.0001 USD per EUR) | 1 (u) | - | adv_latest_published, adv_pre_pilot_published |
| MBT | 5.0 USD per bitcoin (index points) | 0.5000 | 4.924 | 169.0 | owned A0 window 2022-11-01..2023-10-31 (257 trade dates) | 1 (u) | 6,678 | adv_latest, adv_2022_11_2023_10 |
| MCL | 0.01 USD per barrel | 1.0000 | 6.491 | 245.5 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (u) | 79,142 | adv_published_latest |
| MET | 0.5 USD per ether (index points) | 0.0500 | - | - | unknown: no owned window data and no OC-1 sibling | 1 (u) | - | adv_latest, adv_2022_11_2023_10 |
| MGC | 0.1 USD per troy ounce | 1.0000 | 5.401 | 220.0 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (u) | 52,744 | adv_window, adv_latest |
| MHG | 0.0005 USD per pound | 1.2500 | 3.383 | 159.0 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (u) | 4,373 | adv_window, adv_latest |
| MNG | 0.001 USD per MMBtu | 1.0000 | 6.280 | 158.0 | OC-1 sibling NG: x_ticks(NG) x tick(NG) / tick(MNG) = x 1 (A1 ticks 0.001 / 0.001 USD per MMBtu) | 1 (u) | - | adv_latest, adv_ytd_2025 |
| MNQ | 0.25 index points | 0.5000 | 27.825 | 967.0 | OC-1 sibling NQ: x_ticks(NQ) x tick(NQ) / tick(MNQ) = x 1 (A1 ticks 0.25 / 0.25 index points) | 1 (u) | - | adv_latest_published, adv_nov2022, adv_dec2022, adv_2022_full_year, adv_oct2023, adv_ytd_jan_oct_2023, adv_derived_2022-11_2023-10 |
| MYM | 1.0 index points | 0.5000 | 12.136 | 393.0 | OC-1 sibling YM: x_ticks(YM) x tick(YM) / tick(MYM) = x 1 (A1 ticks 1.0 / 1.0 index points) | 1 (u) | - | adv_nov2022, adv_dec2022, adv_2022_full_year, adv_oct2023, adv_ytd_jan_oct_2023, adv_derived_2022-11_2023-10 |
| NG | 0.001 USD per MMBtu | 10.0000 | 6.280 | 158.0 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (u) | 85,334 | adv_latest, adv_ytd_2026, adv_2022_11_2023_10 |
| NQ | 0.25 index points | 5.0000 | 27.825 | 967.0 | owned A0 window 2022-11-01..2023-10-31 (249 trade dates) | 1 (u) | 618,345 | adv_nov2022, adv_dec2022, adv_2022_full_year, adv_oct2023, adv_ytd_jan_oct_2023, adv_derived_2022-11_2023-10 |
| QG | 0.005 USD per MMBtu | 12.5000 | 1.256 | 31.6 | OC-1 sibling NG: x_ticks(NG) x tick(NG) / tick(QG) = x 0.2 (A1 ticks 0.001 / 0.005 USD per MMBtu) | 1 (u) | - | adv_latest, adv_ytd_2026, adv_2022_11_2023_10 |
| QM | 0.025 USD per barrel | 12.5000 | 2.520 | 97.6 | OC-1 sibling CL: x_ticks(CL) x tick(CL) / tick(QM) = x 0.4 (A1 ticks 0.01 / 0.025 USD per barrel) | 1 (u) | - | - |
| RTY | 0.1 index points | 5.0000 | 10.008 | 341.0 | owned A0 window 2022-11-01..2023-10-31 (249 trade dates) | 1 (u) | 181,060 | adv_latest_published, adv_nov2022, adv_dec2022, adv_2022_full_year, adv_oct2023, adv_ytd_jan_oct_2023, adv_derived_2022-11_2023-10 |
| SI | 0.005 USD per troy ounce (outright) | 25.0000 | - | - | unknown: no owned window data and no OC-1 sibling | 1 (sourced) | - | adv_latest |
| SIL | 0.005 USD per troy ounce (outright) | 5.0000 | - | - | unknown: no owned window data and no OC-1 sibling | 1 (u) | - | adv_window, adv_latest |
| YM | 1.0 index points | 5.0000 | 12.136 | 393.0 | owned A0 window 2022-11-01..2023-10-31 (249 trade dates) | 1 (u) | 163,416 | adv_nov2022, adv_dec2022, adv_2022_full_year, adv_oct2023, adv_ytd_jan_oct_2023, adv_derived_2022-11_2023-10 |
| ZB | 0.03125 points of par (1/32) | 31.2500 | 1.218 | 48.0 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (sourced) | 291,523 | adv_published_latest, adv_2022_11_2023_10 |
| ZC | 0.25 US cents per bushel | 12.5000 | 1.714 | 43.5 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (u; mean 1.26) | 91,946 | adv_published_latest, adv_2022_11_2023_10 |
| ZF | 0.0078125 points of par (1/4 of 1/32) | 7.8125 | 1.678 | 63.0 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (sourced) | 927,861 | adv_published_latest, adv_2022_11_2023_10 |
| ZL | 0.01 US cents per pound | 6.0000 | 5.517 | 166.0 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (u) | 42,686 | adv_published_latest, adv_2022_11_2023_10 |
| ZM | 0.1 USD per short ton | 10.0000 | 3.152 | 96.0 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (u) | 36,690 | adv_published_latest, adv_2022_11_2023_10 |
| ZN | 0.015625 points of par (1/2 of 1/32) | 15.6250 | 1.277 | 46.5 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (sourced) | 1,385,806 | adv_published_latest, adv_2022_11_2023_10 |
| ZS | 0.25 US cents per bushel | 12.5000 | 3.106 | 90.5 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (u; mean 1.118) | 77,862 | adv_published_latest, adv_2022_11_2023_10 |
| ZT | 0.00390625 points of par (1/8 of 1/32) | 7.8125 | 1.581 | 52.5 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (sourced) | 472,003 | adv_published_latest, adv_2022_11_2023_10 |
| ZW | 0.25 US cents per bushel | 12.5000 | 2.725 | 77.5 | owned A0 window 2022-11-01..2023-10-31 (250 trade dates) | 1 (u; mean 1.1) | 39,362 | adv_published_latest, adv_2022_11_2023_10 |

## 6. Results per pair (limit case unless named; no scores)

Columns: v = tick value; F_rt = the firm's round-trip commission and fees for 1 contract (source and quote in the
JSON); sigma_T = sigma_1m in ticks; mu values in ticks per trade ("> 4" scores 0 under the spec); cost/attempt = section
2.5; room = MLL / (R_d v); pos. limit = contracts of that product at the 50K evaluation stage. Flags: "restricted_now"
(listed with a fee but currently restricted), "position_limit_0" (listed, 0 contracts now), "sigma ... from sibling"
(OC-1), "not computed" (sigma unknown), "non-monotone cached points" (section 8). Every Topstep row also carries the
3.70 fee-conflict flag, every Lucid row the exchange-fee-inclusion flag, and rows with the default spread the "S_rt
default 1 (u)" flag (omitted from the table, kept in the JSON).

### topstep: 50K Trading Combine, Standard Path (USD 49/month)

| code | v USD | F_rt USD | F_rt ticks | sigma_T | mu*_lim | mu*_mkt | mu10K | cost/attempt USD | room | DLL ticks | pos. limit | grid check | sensitivities | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | 5.0000 | 4.22 | 0.844 | 3.09 | 0.91 | 1.91 | 1.67 | 49.6 | 2.90 | - | 5 | ok (56 pts) | ex-API mu*_lim 0.90; fee 4.22: mu*_lim 0.91 | non-monotone cached points |
| 6E | 6.2500 | 4.22 | 0.675 | 3.56 | 0.74 | 1.74 | 1.23 | 49.5 | 2.09 | - | 5 | ok (52 pts) | ex-API mu*_lim 0.73; fee 4.22: mu*_lim 0.74; S_rt 1.200: mu*_mkt 1.94 | non-monotone cached points |
| CL | 10.0000 | 4.02 | 0.402 | 6.30 | 0.45 | 1.45 | 0.82 | 49.6 | 0.82 | - | 3 | ok (48 pts) | ex-API mu*_lim 0.43; fee 4.02: mu*_lim 0.45 | non-monotone cached points |
| GC | 10.0000 | 4.32 | 0.432 | 5.29 | 0.50 | 1.50 | 0.82 | 49.5 | 0.91 | - | 3 | ok (45 pts) | ex-API mu*_lim 0.48; fee 4.32: mu*_lim 0.50 | non-monotone cached points |
| HG | 12.5000 | 4.32 | 0.346 | 3.14 | 0.40 | 1.40 | 0.62 | 49.5 | 1.01 | - | 0 | ok (42 pts) | ex-API mu*_lim 0.39; fee 4.32: mu*_lim 0.40 | position_limit_0; non-monotone cached points |
| M2K | 0.5000 | 1.22 | 2.440 | 10.01 | > 4 | > 4 | > 4 | 168.8 | 11.73 | - | 50 | ok (52 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 | sigma_1m and R_d from sibling RTY (OC-1); non-monotone cached points |
| M6A | 1.0000 | 1.00 | 1.000 | 1.55 | > 4 | > 4 | > 4 | 202.8 | 28.99 | - | 50 | ok (51 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 | sigma_1m and R_d from sibling 6A (OC-1) |
| M6E | 1.2500 | 1.00 | 0.800 | 1.78 | > 4 | > 4 | > 4 | 206.9 | 20.92 | - | 50 | ok (52 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 | sigma_1m and R_d from sibling 6E (OC-1) |
| MBT | 0.5000 | 2.82 | 5.640 | 4.92 | > 4 | > 4 | > 4 | 49.8 | 23.67 | - | 5 | ok (52 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 | non-monotone cached points |
| MCL | 1.0000 | 1.72 | 1.720 | 6.49 | > 4 | > 4 | > 4 | 111.3 | 8.15 | - | 30 | ok (52 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 |  |
| MET | 0.0500 | 0.72 | 14.400 | - | - | - | - | - | - | - | 5 | - |  | not computed |
| MGC | 1.0000 | 1.92 | 1.920 | 5.40 | > 4 | > 4 | > 4 | 99.6 | 9.09 | - | 30 | ok (52 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 |  |
| MHG | 1.2500 | 1.92 | 1.536 | 3.38 | > 4 | > 4 | > 4 | 99.0 | 10.06 | - | 2 | ok (51 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 |  |
| MNG | 1.0000 | 1.92 | 1.920 | 6.28 | > 4 | > 4 | > 4 | 100.0 | 12.66 | - | 50 | ok (52 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 | sigma_1m and R_d from sibling NG (OC-1) |
| MNQ | 0.5000 | 1.22 | 2.440 | 27.83 | 3.26 | > 4 | > 4 | 165.1 | 4.14 | - | 50 | ok (72 pts) | ex-API mu*_lim 3.06; fee 3.70: mu*_lim > 4 | sigma_1m and R_d from sibling NQ (OC-1); non-monotone cached points |
| MYM | 0.5000 | 1.22 | 2.440 | 12.14 | > 4 | > 4 | > 4 | 168.9 | 10.18 | - | 50 | ok (52 pts) | ex-API mu*_lim > 4; fee 3.70: mu*_lim > 4 | sigma_1m and R_d from sibling YM (OC-1); non-monotone cached points |
| NG | 10.0000 | 4.22 | 0.422 | 6.28 | 0.47 | 1.47 | 0.84 | 49.5 | 1.27 | - | 5 | ok (47 pts) | ex-API mu*_lim 0.45; fee 4.22: mu*_lim 0.47 | non-monotone cached points |
| NQ | 5.0000 | 3.78 | 0.756 | 27.83 | 0.44 | 1.44 | 1.83 | 50.0 | 0.41 | - | 5 | ok (61 pts) | ex-API mu*_lim 0.37; fee 3.78: mu*_lim 0.44 |  |
| QG | 12.5000 | 2.02 | 0.162 | 1.26 | 0.19 | 1.19 | 0.49 | 92.0 | 5.06 | - | 5 | ok (42 pts) | ex-API mu*_lim 0.19; fee 3.70: mu*_lim 0.33 | sigma_1m and R_d from sibling NG (OC-1); non-monotone cached points |
| QM | 12.5000 | 3.42 | 0.274 | 2.52 | 0.32 | 1.32 | 0.54 | 50.5 | 1.64 | - | 3 | ok (45 pts) | ex-API mu*_lim 0.32; fee 3.70: mu*_lim 0.35 | sigma_1m and R_d from sibling CL (OC-1); non-monotone cached points |
| RTY | 5.0000 | 3.78 | 0.756 | 10.01 | 0.88 | 1.88 | 1.50 | 49.7 | 1.17 | - | 5 | ok (54 pts) | ex-API mu*_lim 0.85; fee 3.78: mu*_lim 0.88 | non-monotone cached points |
| SI | 25.0000 | 4.32 | 0.173 | - | - | - | - | - | - | - | 0 | - |  | position_limit_0; not computed |
| SIL | 5.0000 | 2.72 | 0.544 | - | - | - | - | - | - | - | 2 | - |  | not computed |
| YM | 5.0000 | 3.78 | 0.756 | 12.14 | 0.86 | 1.86 | 1.57 | 49.7 | 1.02 | - | 5 | ok (55 pts) | ex-API mu*_lim 0.81; fee 3.78: mu*_lim 0.86 | non-monotone cached points |
| ZB | 31.2500 | 2.76 | 0.088 | 1.22 | 0.11 | 1.11 | 0.20 | 57.0 | 1.33 | - | 5 | ok (37 pts) | ex-API mu*_lim 0.11; fee 3.70: mu*_lim 0.14 | non-monotone cached points |
| ZC | 12.5000 | 5.28 | 0.422 | 1.71 | 0.46 | 1.46 | 0.71 | 49.2 | 3.68 | - | 5 | ok (45 pts) | ex-API mu*_lim 0.45; fee 5.28: mu*_lim 0.46; S_rt 1.260: mu*_mkt 1.72 | non-monotone cached points |
| ZF | 7.8125 | 2.32 | 0.297 | 1.68 | 0.37 | 1.37 | 0.88 | 77.4 | 4.06 | - | 5 | ok (47 pts) | ex-API mu*_lim 0.35; fee 3.70: mu*_lim 0.55 | non-monotone cached points |
| ZL | 6.0000 | 5.28 | 0.880 | 5.52 | 0.99 | 1.99 | 1.44 | 49.2 | 2.01 | - | 5 | ok (55 pts) | ex-API mu*_lim 0.97; fee 5.28: mu*_lim 0.99 | non-monotone cached points |
| ZM | 10.0000 | 5.28 | 0.528 | 3.15 | 0.59 | 1.59 | 0.86 | 49.2 | 2.08 | - | 5 | ok (47 pts) | ex-API mu*_lim 0.58; fee 5.28: mu*_lim 0.59 | non-monotone cached points |
| ZN | 15.6250 | 2.62 | 0.168 | 1.28 | 0.19 | 1.19 | 0.40 | 65.6 | 2.75 | - | 5 | ok (41 pts) | ex-API mu*_lim 0.19; fee 3.70: mu*_lim 0.26 | non-monotone cached points |
| ZS | 12.5000 | 5.28 | 0.422 | 3.11 | 0.48 | 1.48 | 0.70 | 49.2 | 1.77 | - | 5 | ok (46 pts) | ex-API mu*_lim 0.47; fee 5.28: mu*_lim 0.48; S_rt 1.118: mu*_mkt 1.60 | non-monotone cached points |
| ZT | 7.8125 | 2.32 | 0.297 | 1.58 | 0.40 | 1.40 | 0.90 | 77.7 | 4.88 | - | 5 | ok (45 pts) | ex-API mu*_lim 0.37; fee 3.70: mu*_lim 0.58 | non-monotone cached points |
| ZW | 12.5000 | 5.28 | 0.422 | 2.72 | 0.48 | 1.48 | 0.69 | 49.2 | 2.06 | - | 5 | ok (46 pts) | ex-API mu*_lim 0.47; fee 5.28: mu*_lim 0.48; S_rt 1.100: mu*_mkt 1.58 | non-monotone cached points |

### lucid: LucidPro 50K (USD 172 one-time, DLL on)

| code | v USD | F_rt USD | F_rt ticks | sigma_T | mu*_lim | mu*_mkt | mu10K | cost/attempt USD | room | DLL ticks | pos. limit | grid check | sensitivities | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | 5.0000 | 4.80 | 0.960 | 3.09 | 0.98 | 1.98 | 2.28 | 120.9 | 2.90 | 240.0 | 4 | ok (60 pts) | fee 6.20: mu*_lim 1.26 |  |
| 6E | 6.2500 | 4.80 | 0.768 | 3.56 | 0.78 | 1.78 | 1.76 | 120.9 | 2.09 | 192.0 | 4 | ok (55 pts) | fee 6.20: mu*_lim 1.00; S_rt 1.200: mu*_mkt 1.98 |  |
| CL | 10.0000 | 4.00 | 0.400 | 6.30 | 0.40 | 1.40 | 0.86 | 120.9 | 0.82 | 120.0 | 4 | ok (45 pts) | fee 5.98: mu*_lim 0.60 |  |
| GC | 10.0000 | 4.60 | 0.460 | 5.29 | 0.46 | 1.46 | 0.93 | 120.9 | 0.91 | 120.0 | 4 | ok (45 pts) | fee 6.20: mu*_lim 0.62 |  |
| HG | 12.5000 | 4.60 | 0.368 | 3.14 | 0.37 | 1.37 | 0.81 | 120.9 | 1.01 | 96.0 | 4 | ok (44 pts) | fee 6.20: mu*_lim 0.50 |  |
| M2K | 0.5000 | 1.00 | 2.000 | 10.01 | 2.36 | 3.36 | > 4 | 120.9 | 11.73 | 2,400.0 | 40 | ok (63 pts) | fee 1.90: mu*_lim > 4 | sigma_1m and R_d from sibling RTY (OC-1) |
| MCL | 1.0000 | 1.00 | 1.000 | 6.49 | 1.17 | 2.17 | > 4 | 120.9 | 8.15 | 1,200.0 | 40 | ok (63 pts) | fee 2.12: mu*_lim 2.29 |  |
| MGC | 1.0000 | 1.60 | 1.600 | 5.40 | 1.78 | 2.78 | > 4 | 120.9 | 9.09 | 1,200.0 | 40 | ok (63 pts) | fee 2.20: mu*_lim 2.38 |  |
| MNQ | 0.5000 | 1.00 | 2.000 | 27.83 | 2.21 | 3.21 | > 4 | 120.9 | 4.14 | 2,400.0 | 40 | ok (62 pts) | fee 1.90: mu*_lim > 4 | sigma_1m and R_d from sibling NQ (OC-1) |
| MYM | 0.5000 | 1.00 | 2.000 | 12.14 | 2.34 | 3.34 | > 4 | 120.9 | 10.18 | 2,400.0 | 40 | ok (62 pts) | fee 1.90: mu*_lim > 4 | sigma_1m and R_d from sibling YM (OC-1) |
| NG | 10.0000 | 4.00 | 0.400 | 6.28 | 0.40 | 1.40 | 0.86 | 120.9 | 1.27 | 120.0 | 4 | ok (45 pts) | fee 6.20: mu*_lim 0.62 |  |
| NQ | 5.0000 | 3.50 | 0.700 | 27.83 | 0.64 | 1.64 | 1.85 | 126.3 | 0.41 | 240.0 | 4 | ok (59 pts) | fee 5.76: mu*_lim 1.09 | non-monotone cached points |
| QG | 12.5000 | 2.60 | 0.208 | 1.26 | 0.22 | 1.22 | 0.74 | 120.9 | 5.06 | 96.0 | 4 | ok (45 pts) | fee 4.00: mu*_lim 0.33 | sigma_1m and R_d from sibling NG (OC-1) |
| QM | 12.5000 | 4.00 | 0.320 | 2.52 | 0.33 | 1.33 | 0.77 | 120.9 | 1.64 | 96.0 | 4 | ok (46 pts) | fee 5.40: mu*_lim 0.44 | sigma_1m and R_d from sibling CL (OC-1) |
| RTY | 5.0000 | 3.50 | 0.700 | 10.01 | 0.70 | 1.70 | 1.66 | 120.9 | 1.17 | 240.0 | 4 | ok (52 pts) | fee 5.76: mu*_lim 1.15 |  |
| SI | 25.0000 | 4.60 | 0.184 | - | - | - | - | - | - | 48.0 | 4 | - |  | not computed |
| SIL | 5.0000 | 3.20 | 0.640 | - | - | - | - | - | - | 240.0 | 40 | - |  | not computed |
| YM | 5.0000 | 3.50 | 0.700 | 12.14 | 0.70 | 1.70 | 1.62 | 120.9 | 1.02 | 240.0 | 4 | ok (51 pts) | fee 5.76: mu*_lim 1.15 |  |
| ZC | 12.5000 | 5.60 | 0.448 | 1.71 | 0.46 | 1.46 | 0.96 | 120.9 | 3.68 | 96.0 | 4 | ok (45 pts) | fee 7.20: mu*_lim 0.58; S_rt 1.260: mu*_mkt 1.72 |  |
| ZL | 6.0000 | 5.60 | 0.933 | 5.52 | 0.94 | 1.94 | 1.87 | 120.9 | 2.01 | 200.0 | 4 | ok (54 pts) | fee 7.20: mu*_lim 1.20 |  |
| ZM | 10.0000 | 5.60 | 0.560 | 3.15 | 0.57 | 1.57 | 1.12 | 120.9 | 2.08 | 120.0 | 4 | ok (49 pts) | fee 9.20: mu*_lim 0.93 |  |
| ZS | 12.5000 | 5.60 | 0.448 | 3.11 | 0.45 | 1.45 | 0.90 | 120.9 | 1.77 | 96.0 | 4 | ok (46 pts) | fee 15.20: mu*_lim 1.22; S_rt 1.118: mu*_mkt 1.57 |  |
| ZW | 12.5000 | 5.60 | 0.448 | 2.72 | 0.45 | 1.45 | 0.90 | 120.9 | 2.06 | 96.0 | 4 | ok (46 pts) | fee 17.20: mu*_lim 1.38; S_rt 1.100: mu*_mkt 1.55 |  |

### tradeify: Growth 50K (USD 145 one-time)

| code | v USD | F_rt USD | F_rt ticks | sigma_T | mu*_lim | mu*_mkt | mu10K | cost/attempt USD | room | DLL ticks | pos. limit | grid check | sensitivities | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | 5.0000 | 6.20 | 1.240 | 3.09 | 1.26 | 2.26 | 1.96 | 95.8 | 2.90 | 250.0 | 4 | ok (56 pts) |  | non-monotone cached points |
| 6E | 6.2500 | 6.20 | 0.992 | 3.56 | 1.00 | 2.00 | 1.61 | 95.8 | 2.09 | 200.0 | 4 | ok (52 pts) | S_rt 1.200: mu*_mkt 2.20 | non-monotone cached points |
| CL | 10.0000 | 5.98 | 0.598 | 6.30 | 0.59 | 1.59 | 0.97 | 95.8 | 0.82 | 125.0 | 4 | ok (46 pts) |  | non-monotone cached points |
| GC | 10.0000 | 6.20 | 0.620 | 5.29 | 0.61 | 1.61 | 1.01 | 95.8 | 0.91 | 125.0 | 4 | ok (50 pts) |  |  |
| HG | 12.5000 | 6.20 | 0.496 | 3.14 | 0.50 | 1.50 | 0.81 | 95.8 | 1.01 | 100.0 | 4 | ok (44 pts) |  |  |
| M2K | 0.5000 | 1.82 | 3.640 | 10.01 | > 4 | > 4 | > 4 | 95.8 | 11.73 | 2,500.0 | 40 | ok (51 pts) |  | sigma_1m and R_d from sibling RTY (OC-1) |
| M6A | 1.0000 | 1.60 | 1.600 | 1.55 | > 4 | > 4 | > 4 | 95.8 | 28.99 | 1,250.0 | 40 | ok (51 pts) |  | sigma_1m and R_d from sibling 6A (OC-1) |
| M6E | 1.2500 | 1.60 | 1.280 | 1.78 | > 4 | > 4 | > 4 | 95.8 | 20.92 | 1,000.0 | 40 | ok (51 pts) |  | sigma_1m and R_d from sibling 6E (OC-1) |
| MCL | 1.0000 | 2.12 | 2.120 | 6.49 | > 4 | > 4 | > 4 | 95.8 | 8.15 | 1,250.0 | 40 | ok (51 pts) |  |  |
| MGC | 1.0000 | 2.12 | 2.120 | 5.40 | > 4 | > 4 | > 4 | 95.8 | 9.09 | 1,250.0 | 40 | ok (51 pts) |  |  |
| MNQ | 0.5000 | 1.82 | 3.640 | 27.83 | 3.86 | > 4 | > 4 | 95.8 | 4.14 | 2,500.0 | 40 | ok (63 pts) |  | sigma_1m and R_d from sibling NQ (OC-1) |
| MYM | 0.5000 | 1.82 | 3.640 | 12.14 | > 4 | > 4 | > 4 | 95.8 | 10.18 | 2,500.0 | 40 | ok (51 pts) |  | sigma_1m and R_d from sibling YM (OC-1) |
| NG | 10.0000 | 6.20 | 0.620 | 6.28 | 0.61 | 1.61 | 1.00 | 95.8 | 1.27 | 125.0 | 4 | ok (45 pts) |  |  |
| NQ | 5.0000 | 5.76 | 1.152 | 27.83 | 1.05 | 2.05 | 2.22 | 98.4 | 0.41 | 250.0 | 4 | ok (71 pts) |  |  |
| QG | 12.5000 | 4.00 | 0.320 | 1.26 | 0.33 | 1.33 | 0.61 | 95.8 | 5.06 | 100.0 | 4 | ok (44 pts) |  | sigma_1m and R_d from sibling NG (OC-1); non-monotone cached points |
| QM | 12.5000 | 5.40 | 0.432 | 2.52 | 0.43 | 1.43 | 0.75 | 95.8 | 1.64 | 100.0 | 4 | ok (43 pts) |  | sigma_1m and R_d from sibling CL (OC-1) |
| RTY | 5.0000 | 5.76 | 1.152 | 10.01 | 1.13 | 2.13 | 1.92 | 95.8 | 1.17 | 250.0 | 4 | ok (57 pts) |  |  |
| SI | 25.0000 | 6.20 | 0.248 | - | - | - | - | - | - | 50.0 | 4 | - |  | not computed |
| YM | 5.0000 | 5.76 | 1.152 | 12.14 | 1.13 | 2.13 | 1.90 | 95.8 | 1.02 | 250.0 | 4 | ok (56 pts) |  |  |
| ZC | 12.5000 | 7.20 | 0.576 | 1.71 | 0.58 | 1.58 | 0.89 | 95.8 | 3.68 | 100.0 | 4 | ok (47 pts) | S_rt 1.260: mu*_mkt 1.84 | non-monotone cached points |
| ZL | 6.0000 | 7.20 | 1.200 | 5.52 | 1.20 | 2.20 | 1.85 | 95.8 | 2.01 | 208.3 | 4 | ok (53 pts) |  |  |
| ZM | 10.0000 | 9.20 | 0.920 | 3.15 | 0.92 | 1.92 | 1.31 | 95.8 | 2.08 | 125.0 | 4 | ok (50 pts) |  |  |
| ZS | 12.5000 | 15.20 | 1.216 | 3.11 | 1.22 | 2.22 | 1.53 | 95.8 | 1.77 | 100.0 | 4 | ok (53 pts) | S_rt 1.118: mu*_mkt 2.33 |  |
| ZW | 12.5000 | 17.20 | 1.376 | 2.72 | 1.38 | 2.38 | 1.69 | 95.8 | 2.06 | 100.0 | 4 | ok (53 pts) | S_rt 1.100: mu*_mkt 2.48 |  |

### mffu: Builder 50K Default (USD 153 one-time)

| code | v USD | F_rt USD | F_rt ticks | sigma_T | mu*_lim | mu*_mkt | mu10K | cost/attempt USD | room | DLL ticks | pos. limit | grid check | sensitivities | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | 5.0000 | 5.04 | 1.008 | 3.09 | 1.03 | 2.03 | 2.39 | 153.0 | 2.90 | 200.0 | 4 | ok (63 pts) |  |  |
| 6E | 6.2500 | 5.12 | 0.819 | 3.56 | 0.83 | 1.83 | 1.92 | 153.0 | 2.09 | 160.0 | 4 | ok (56 pts) | S_rt 1.200: mu*_mkt 2.03 |  |
| CL | 10.0000 | 4.92 | 0.492 | 6.30 | 0.51 | 1.51 | 1.06 | 153.0 | 0.82 | 100.0 | 4 | ok (50 pts) |  |  |
| GC | 10.0000 | 5.12 | 0.512 | 5.29 | 0.53 | 1.53 | 1.10 | 153.0 | 0.91 | 100.0 | 4 | ok (49 pts) |  |  |
| HG | 12.5000 | 5.12 | 0.410 | 3.14 | 0.42 | 1.42 | 0.91 | 153.0 | 1.01 | 80.0 | 4 | ok (47 pts) |  | restricted_now |
| M2K | 0.5000 | 1.90 | 3.800 | 10.01 | > 4 | > 4 | > 4 | 153.0 | 11.73 | 2,000.0 | 40 | ok (51 pts) |  | sigma_1m and R_d from sibling RTY (OC-1) |
| M6A | 1.0000 | 1.44 | 1.440 | 1.55 | 1.64 | 2.64 | > 4 | 153.0 | 28.99 | 1,000.0 | 40 | ok (64 pts) |  | sigma_1m and R_d from sibling 6A (OC-1) |
| M6E | 1.2500 | 1.44 | 1.152 | 1.78 | 1.31 | 2.31 | > 4 | 153.0 | 20.92 | 800.0 | 40 | ok (62 pts) |  | sigma_1m and R_d from sibling 6E (OC-1) |
| MBT | 0.5000 | 3.50 | 7.000 | 4.92 | > 4 | > 4 | > 4 | 153.0 | 23.67 | 2,000.0 | 4 | ok (51 pts) |  |  |
| MCL | 1.0000 | 1.16 | 1.160 | 6.49 | 1.34 | 2.34 | > 4 | 153.0 | 8.15 | 1,000.0 | 40 | ok (62 pts) |  |  |
| MET | 0.0500 | 1.16 | 23.200 | - | - | - | - | - | - | 20,000.0 | 40 | - |  | not computed |
| MGC | 1.0000 | 2.20 | 2.200 | 5.40 | 2.38 | 3.38 | > 4 | 153.0 | 9.09 | 1,000.0 | 5 | ok (63 pts) |  |  |
| MNQ | 0.5000 | 1.90 | 3.800 | 27.83 | > 4 | > 4 | > 4 | 153.0 | 4.14 | 2,000.0 | 40 | ok (51 pts) |  | sigma_1m and R_d from sibling NQ (OC-1) |
| MYM | 0.5000 | 1.90 | 3.800 | 12.14 | > 4 | > 4 | > 4 | 153.0 | 10.18 | 2,000.0 | 40 | ok (51 pts) |  | sigma_1m and R_d from sibling YM (OC-1) |
| NG | 10.0000 | 5.12 | 0.512 | 6.28 | 0.53 | 1.53 | 1.08 | 153.0 | 1.27 | 100.0 | 4 | ok (50 pts) |  | restricted_now |
| NQ | 5.0000 | 4.68 | 0.936 | 27.83 | 0.98 | 1.98 | 2.32 | 153.0 | 0.41 | 200.0 | 4 | ok (71 pts) |  |  |
| QG | 12.5000 | 2.92 | 0.234 | 1.26 | 0.25 | 1.25 | 0.79 | 153.0 | 5.06 | 80.0 | 4 | ok (44 pts) |  | restricted_now; sigma_1m and R_d from sibling NG (OC-1) |
| QM | 12.5000 | 4.32 | 0.346 | 2.52 | 0.35 | 1.35 | 0.90 | 153.0 | 1.64 | 80.0 | 4 | ok (45 pts) |  | sigma_1m and R_d from sibling CL (OC-1) |
| RTY | 5.0000 | 4.68 | 0.936 | 10.01 | 0.96 | 1.96 | 2.12 | 153.0 | 1.17 | 200.0 | 4 | ok (57 pts) |  |  |
| SI | 25.0000 | 5.12 | 0.205 | - | - | - | - | - | - | 40.0 | 4 | - |  | restricted_now; not computed |
| SIL | 5.0000 | 2.84 | 0.568 | - | - | - | - | - | - | 200.0 | 5 | - |  | not computed |
| YM | 5.0000 | 5.76 | 1.152 | 12.14 | 1.18 | 2.18 | 2.31 | 153.0 | 1.02 | 200.0 | 4 | ok (59 pts) |  |  |
| ZC | 12.5000 | 6.12 | 0.490 | 1.71 | 0.50 | 1.50 | 1.04 | 153.0 | 3.68 | 80.0 | 4 | ok (48 pts) | S_rt 1.260: mu*_mkt 1.76 |  |
| ZL | 6.0000 | 6.12 | 1.020 | 5.52 | 1.03 | 2.03 | 2.15 | 153.0 | 2.01 | 166.7 | 4 | ok (60 pts) |  |  |
| ZM | 10.0000 | 6.12 | 0.612 | 3.15 | 0.62 | 1.62 | 1.30 | 153.0 | 2.08 | 100.0 | 4 | ok (49 pts) |  |  |
| ZS | 12.5000 | 6.12 | 0.490 | 3.11 | 0.50 | 1.50 | 0.99 | 153.0 | 1.77 | 80.0 | 4 | ok (46 pts) | S_rt 1.118: mu*_mkt 1.62 |  |
| ZW | 12.5000 | 6.12 | 0.490 | 2.72 | 0.50 | 1.50 | 1.03 | 153.0 | 2.06 | 80.0 | 4 | ok (48 pts) | S_rt 1.100: mu*_mkt 1.60 |  |

### bulenox: Qualification 50K, Option 1 trailing (USD 175 one-time, 30 days)

| code | v USD | F_rt USD | F_rt ticks | sigma_T | mu*_lim | mu*_mkt | mu10K | cost/attempt USD | room | DLL ticks | pos. limit | grid check | sensitivities | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | 5.0000 | 4.72 | 0.944 | 3.09 | 2.17 | 3.17 | 2.75 | 175.0 | 3.62 | - | 7 | ok (67 pts) | ex-API mu*_lim 2.13 | non-monotone cached points |
| 6E | 6.2500 | 4.72 | 0.755 | 3.56 | 1.67 | 2.67 | 2.21 | 175.0 | 2.61 | - | 7 | ok (63 pts) | ex-API mu*_lim 1.62; S_rt 1.200: mu*_mkt 2.87 | non-monotone cached points |
| CL | 10.0000 | 4.52 | 0.452 | 6.30 | 0.76 | 1.76 | 1.44 | 175.0 | 1.02 | - | 7 | ok (55 pts) | ex-API mu*_lim 0.68 |  |
| GC | 10.0000 | 4.62 | 0.462 | 5.29 | 0.82 | 1.82 | 1.43 | 175.0 | 1.13 | - | 7 | ok (54 pts) | ex-API mu*_lim 0.74 |  |
| HG | 12.5000 | 4.62 | 0.370 | 3.14 | 0.74 | 1.74 | 1.13 | 175.0 | 1.26 | - | 7 | ok (52 pts) | ex-API mu*_lim 0.69 | non-monotone cached points |
| M2K | 0.5000 | 1.22 | 2.440 | 10.01 | > 4 | > 4 | > 4 | 175.0 | 14.66 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 | sigma_1m and R_d from sibling RTY (OC-1) |
| M6A | 1.0000 | 1.00 | 1.000 | 1.55 | > 4 | > 4 | > 4 | 175.0 | 36.23 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 | sigma_1m and R_d from sibling 6A (OC-1) |
| M6E | 1.2500 | 1.00 | 0.800 | 1.78 | > 4 | > 4 | > 4 | 175.0 | 26.14 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 | sigma_1m and R_d from sibling 6E (OC-1) |
| MBT | 0.5000 | 5.52 | 11.040 | 4.92 | > 4 | > 4 | > 4 | 175.0 | 29.59 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 |  |
| MCL | 1.0000 | 1.52 | 1.520 | 6.49 | > 4 | > 4 | > 4 | 175.0 | 10.18 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 |  |
| MET | 0.0500 | 0.92 | 18.400 | - | - | - | - | - | - | - | 70 | - |  | not computed |
| MGC | 1.0000 | 1.52 | 1.520 | 5.40 | > 4 | > 4 | > 4 | 175.0 | 11.36 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 |  |
| MNQ | 0.5000 | 1.22 | 2.440 | 27.83 | > 4 | > 4 | > 4 | 175.0 | 5.17 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 | sigma_1m and R_d from sibling NQ (OC-1) |
| MYM | 0.5000 | 1.22 | 2.440 | 12.14 | > 4 | > 4 | > 4 | 175.0 | 12.72 | - | 70 | ok (51 pts) | ex-API mu*_lim > 4 | sigma_1m and R_d from sibling YM (OC-1) |
| NG | 10.0000 | 4.52 | 0.452 | 6.28 | 0.76 | 1.76 | 1.44 | 175.0 | 1.58 | - | 7 | ok (55 pts) | ex-API mu*_lim 0.68 |  |
| NQ | 5.0000 | 4.18 | 0.836 | 27.83 | 1.37 | 2.37 | 3.10 | 175.0 | 0.52 | - | 7 | ok (81 pts) | ex-API mu*_lim 1.14 |  |
| QG | 12.5000 | 2.52 | 0.202 | 1.26 | 0.69 | 1.69 | 0.93 | 175.0 | 6.33 | - | 7 | ok (47 pts) | ex-API mu*_lim 0.68 | sigma_1m and R_d from sibling NG (OC-1); non-monotone cached points |
| QM | 12.5000 | 3.92 | 0.314 | 2.52 | 0.72 | 1.72 | 1.06 | 175.0 | 2.05 | - | 7 | ok (50 pts) | ex-API mu*_lim 0.69 | sigma_1m and R_d from sibling CL (OC-1); non-monotone cached points |
| RTY | 5.0000 | 4.18 | 0.836 | 10.01 | 1.59 | 2.59 | 2.76 | 175.0 | 1.47 | - | 7 | ok (72 pts) | ex-API mu*_lim 1.44 |  |
| SI | 25.0000 | 4.62 | 0.185 | - | - | - | - | - | - | - | 7 | - |  | not computed |
| YM | 5.0000 | 4.18 | 0.836 | 12.14 | 1.46 | 2.46 | 2.80 | 175.0 | 1.27 | - | 7 | ok (68 pts) | ex-API mu*_lim 1.30 |  |
| ZL | 6.0000 | 5.72 | 0.953 | 5.52 | 1.78 | 2.78 | 2.50 | 175.0 | 2.51 | - | 7 | ok (65 pts) | ex-API mu*_lim 1.70 | non-monotone cached points |
| ZM | 10.0000 | 5.72 | 0.572 | 3.15 | 1.08 | 2.08 | 1.50 | 175.0 | 2.60 | - | 7 | ok (54 pts) | ex-API mu*_lim 1.04 | non-monotone cached points |
| ZS | 12.5000 | 5.72 | 0.458 | 3.11 | 0.83 | 1.83 | 1.21 | 175.0 | 2.21 | - | 7 | ok (52 pts) | ex-API mu*_lim 0.78; S_rt 1.118: mu*_mkt 1.94 | non-monotone cached points |
| ZW | 12.5000 | 5.72 | 0.458 | 2.72 | 0.85 | 1.85 | 1.21 | 175.0 | 2.58 | - | 7 | ok (51 pts) | ex-API mu*_lim 0.81; S_rt 1.100: mu*_mkt 1.95 | non-monotone cached points |


## 7. Sensitivities

Ex-API: the same cycles without the API subscription (Topstep 14.50, Bulenox 100 per month). Alt fee: Lucid at the
highest fee for that product at the other four firms (the spec's 'u' rule, since Lucid does not say whether its
per-side commission includes exchange and NFA fees); Topstep at max(3.70, table fee) in both stages (the LFA-costs
page's simulated Combine fee). S_rt mean: the market case at the readers' sourced mean spread instead of 1.

| firm | code | mu*_lim | ex-API mu*_lim | alt fee USD | mu*_lim at alt fee | S_rt mean | mu*_mkt at mean |
|---|---|---|---|---|---|---|---|
| bulenox | 6A | 2.17 | 2.13 | - | - | - | - |
| bulenox | 6E | 1.67 | 1.62 | - | - | 1.200 | 2.87 |
| bulenox | CL | 0.76 | 0.68 | - | - | - | - |
| bulenox | GC | 0.82 | 0.74 | - | - | - | - |
| bulenox | HG | 0.74 | 0.69 | - | - | - | - |
| bulenox | M2K | > 4 | > 4 | - | - | - | - |
| bulenox | M6A | > 4 | > 4 | - | - | - | - |
| bulenox | M6E | > 4 | > 4 | - | - | - | - |
| bulenox | MBT | > 4 | > 4 | - | - | - | - |
| bulenox | MCL | > 4 | > 4 | - | - | - | - |
| bulenox | MGC | > 4 | > 4 | - | - | - | - |
| bulenox | MNQ | > 4 | > 4 | - | - | - | - |
| bulenox | MYM | > 4 | > 4 | - | - | - | - |
| bulenox | NG | 0.76 | 0.68 | - | - | - | - |
| bulenox | NQ | 1.37 | 1.14 | - | - | - | - |
| bulenox | QG | 0.69 | 0.68 | - | - | - | - |
| bulenox | QM | 0.72 | 0.69 | - | - | - | - |
| bulenox | RTY | 1.59 | 1.44 | - | - | - | - |
| bulenox | YM | 1.46 | 1.30 | - | - | - | - |
| bulenox | ZL | 1.78 | 1.70 | - | - | - | - |
| bulenox | ZM | 1.08 | 1.04 | - | - | - | - |
| bulenox | ZS | 0.83 | 0.78 | - | - | 1.118 | 1.94 |
| bulenox | ZW | 0.85 | 0.81 | - | - | 1.100 | 1.95 |
| lucid | 6A | 0.98 | - | 6.20 | 1.26 | - | - |
| lucid | 6E | 0.78 | - | 6.20 | 1.00 | 1.200 | 1.98 |
| lucid | CL | 0.40 | - | 5.98 | 0.60 | - | - |
| lucid | GC | 0.46 | - | 6.20 | 0.62 | - | - |
| lucid | HG | 0.37 | - | 6.20 | 0.50 | - | - |
| lucid | M2K | 2.36 | - | 1.90 | > 4 | - | - |
| lucid | MCL | 1.17 | - | 2.12 | 2.29 | - | - |
| lucid | MGC | 1.78 | - | 2.20 | 2.38 | - | - |
| lucid | MNQ | 2.21 | - | 1.90 | > 4 | - | - |
| lucid | MYM | 2.34 | - | 1.90 | > 4 | - | - |
| lucid | NG | 0.40 | - | 6.20 | 0.62 | - | - |
| lucid | NQ | 0.64 | - | 5.76 | 1.09 | - | - |
| lucid | QG | 0.22 | - | 4.00 | 0.33 | - | - |
| lucid | QM | 0.33 | - | 5.40 | 0.44 | - | - |
| lucid | RTY | 0.70 | - | 5.76 | 1.15 | - | - |
| lucid | YM | 0.70 | - | 5.76 | 1.15 | - | - |
| lucid | ZC | 0.46 | - | 7.20 | 0.58 | 1.260 | 1.72 |
| lucid | ZL | 0.94 | - | 7.20 | 1.20 | - | - |
| lucid | ZM | 0.57 | - | 9.20 | 0.93 | - | - |
| lucid | ZS | 0.45 | - | 15.20 | 1.22 | 1.118 | 1.57 |
| lucid | ZW | 0.45 | - | 17.20 | 1.38 | 1.100 | 1.55 |
| mffu | 6E | 0.83 | - | - | - | 1.200 | 2.03 |
| mffu | ZC | 0.50 | - | - | - | 1.260 | 1.76 |
| mffu | ZS | 0.50 | - | - | - | 1.118 | 1.62 |
| mffu | ZW | 0.50 | - | - | - | 1.100 | 1.60 |
| topstep | 6A | 0.91 | 0.90 | 4.22 | 0.91 | - | - |
| topstep | 6E | 0.74 | 0.73 | 4.22 | 0.74 | 1.200 | 1.94 |
| topstep | CL | 0.45 | 0.43 | 4.02 | 0.45 | - | - |
| topstep | GC | 0.50 | 0.48 | 4.32 | 0.50 | - | - |
| topstep | HG | 0.40 | 0.39 | 4.32 | 0.40 | - | - |
| topstep | M2K | > 4 | > 4 | 3.70 | > 4 | - | - |
| topstep | M6A | > 4 | > 4 | 3.70 | > 4 | - | - |
| topstep | M6E | > 4 | > 4 | 3.70 | > 4 | - | - |
| topstep | MBT | > 4 | > 4 | 3.70 | > 4 | - | - |
| topstep | MCL | > 4 | > 4 | 3.70 | > 4 | - | - |
| topstep | MGC | > 4 | > 4 | 3.70 | > 4 | - | - |
| topstep | MHG | > 4 | > 4 | 3.70 | > 4 | - | - |
| topstep | MNG | > 4 | > 4 | 3.70 | > 4 | - | - |
| topstep | MNQ | 3.26 | 3.06 | 3.70 | > 4 | - | - |
| topstep | MYM | > 4 | > 4 | 3.70 | > 4 | - | - |
| topstep | NG | 0.47 | 0.45 | 4.22 | 0.47 | - | - |
| topstep | NQ | 0.44 | 0.37 | 3.78 | 0.44 | - | - |
| topstep | QG | 0.19 | 0.19 | 3.70 | 0.33 | - | - |
| topstep | QM | 0.32 | 0.32 | 3.70 | 0.35 | - | - |
| topstep | RTY | 0.88 | 0.85 | 3.78 | 0.88 | - | - |
| topstep | YM | 0.86 | 0.81 | 3.78 | 0.86 | - | - |
| topstep | ZB | 0.11 | 0.11 | 3.70 | 0.14 | - | - |
| topstep | ZC | 0.46 | 0.45 | 5.28 | 0.46 | 1.260 | 1.72 |
| topstep | ZF | 0.37 | 0.35 | 3.70 | 0.55 | - | - |
| topstep | ZL | 0.99 | 0.97 | 5.28 | 0.99 | - | - |
| topstep | ZM | 0.59 | 0.58 | 5.28 | 0.59 | - | - |
| topstep | ZN | 0.19 | 0.19 | 3.70 | 0.26 | - | - |
| topstep | ZS | 0.48 | 0.47 | 5.28 | 0.48 | 1.118 | 1.60 |
| topstep | ZT | 0.40 | 0.37 | 3.70 | 0.58 | - | - |
| topstep | ZW | 0.48 | 0.47 | 5.28 | 0.48 | 1.100 | 1.58 |
| tradeify | 6E | 1.00 | - | - | - | 1.200 | 2.20 |
| tradeify | ZC | 0.58 | - | - | - | 1.260 | 1.84 |
| tradeify | ZS | 1.22 | - | - | - | 1.118 | 2.33 |
| tradeify | ZW | 1.38 | - | - | - | 1.100 | 2.48 |

Bulenox Option 2 (EOD drawdown, DLL 1,100) beside the spec's Option 1:

| code | Option 1 mu*_lim / mu*_mkt / mu10K | Option 2 mu*_lim / mu*_mkt / mu10K |
|---|---|---|
| 6A | 2.17 / 3.17 / 2.75 | 2.17 / 3.17 / 2.75 |
| 6E | 1.67 / 2.67 / 2.21 | 1.67 / 2.67 / 2.21 |
| CL | 0.76 / 1.76 / 1.44 | 0.76 / 1.76 / 1.44 |
| GC | 0.82 / 1.82 / 1.43 | 0.82 / 1.82 / 1.43 |
| HG | 0.74 / 1.74 / 1.13 | 0.74 / 1.74 / 1.13 |
| M2K | > 4 / > 4 / > 4 | > 4 / > 4 / > 4 |
| M6A | > 4 / > 4 / > 4 | > 4 / > 4 / > 4 |
| M6E | > 4 / > 4 / > 4 | > 4 / > 4 / > 4 |
| MBT | > 4 / > 4 / > 4 | > 4 / > 4 / > 4 |
| MCL | > 4 / > 4 / > 4 | > 4 / > 4 / > 4 |
| MET | - / - / - | - / - / - |
| MGC | > 4 / > 4 / > 4 | > 4 / > 4 / > 4 |
| MNQ | > 4 / > 4 / > 4 | > 4 / > 4 / > 4 |
| MYM | > 4 / > 4 / > 4 | > 4 / > 4 / > 4 |
| NG | 0.76 / 1.76 / 1.44 | 0.76 / 1.76 / 1.44 |
| NQ | 1.37 / 2.37 / 3.10 | 1.30 / 2.30 / 3.08 |
| QG | 0.69 / 1.69 / 0.93 | 0.69 / 1.69 / 0.93 |
| QM | 0.72 / 1.72 / 1.06 | 0.72 / 1.72 / 1.06 |
| RTY | 1.59 / 2.59 / 2.76 | 1.59 / 2.59 / 2.76 |
| SI | - / - / - | - / - / - |
| YM | 1.46 / 2.46 / 2.80 | 1.46 / 2.46 / 2.80 |
| ZL | 1.78 / 2.78 / 2.50 | 1.78 / 2.78 / 2.50 |
| ZM | 1.08 / 2.08 / 1.50 | 1.08 / 2.08 / 1.50 |
| ZS | 0.83 / 1.83 / 1.21 | 0.83 / 1.83 / 1.21 |
| ZW | 0.85 / 1.85 / 1.21 | 0.85 / 1.85 / 1.21 |

## 8. Tests and checks

Regression against E.19 (A3_regress_e19.py, output A3_regress_e19.json). E.19's published zero-edge best case,
Topstep 50K Standard, -$250 per cycle, is E.19's bootstrap headline (stored record
reports/stage_e19_runs/bootstrap-random-all-d8-continuous__50K__zero_k1__f0.25__dll0__base.json: net -250.35, SE
7.28). It cannot be re-run here: its bootstrap reads the E.12 training stores, which run to 2024-02-29, and the stage's
reader rules forbid reading data dated 2023-11-01 or later. The substitute re-runs E.19's own normal-tail twin of the
same job (same grid code prop_econ.grid.run_task, settings, seeds and rules file; it needs only the published
sigma_full values, and the bootstrap loader is replaced by a function that raises): all 56 stored numbers of the job's
four records reproduced with maximum absolute difference 0.0 (net -179.02, SE 6.69, settings fingerprint
d4644acce4988b94 = E.19's), and the same on the E.26-refreshed record. Test 6 then runs the same twin through this
module's own wrapper (prop_econ pools at E.19's sizing, E.19's index draws, A3's cycle_stats and API wallet) and gets
E.19's stored net and net-ex-API exactly.

Unit tests (test_A3_econ.py, 14 tests, all pass in 4.6 s at 15:15 PDT; output test_A3_econ.out):
1. simulate_funded equals prop_econ simulate_xfas path for path on Topstep rules (standard, consistency, DLL option),
   on E.19 normal shocks at f = 0.25 (every XfaPool field array-equal).
2. Both intraday code paths equal E.19's EOD simulators when the day's high is removed.
3. A hand-computed intraday-trailing path (Bulenox-style): breach on day 3 under intraday trailing, pass on day 4 under
   EOD trailing.
4. Per-trade layer: m = T (mu - c) v and s = sqrt(T) sigma_T v exactly; simulated daily P&L matches both moments within
   4 standard errors, as does the sum of 20 simulated normal trades; bridge minimum <= min(0, close), maximum >=
   max(0, close).
5. Size 1 through E.19's day step: a scalar replay of 50 Topstep attempts gives the same pass/breach days.
6. The E.19 normal twin through A3's cycle wrapper: E.19's stored net (-179.02) and net ex API exactly.
7. The vectorized 250-day campaign equals a plain loop over E.19's scalar cycle assembly (two replication blocks).
8. Chunked pool simulation equals one call; the e2 stream helper equals make_draws' stream.
9. Bridge formulas equal prop_econ.returns.bridge_min to 1e-12; every firm has a mapping table.

Monotonicity scan:

| firm | code | EV per cycle at mu = 0, 0.25, ..., 4 (USD, limit case) | EV nondecreasing | P10K nondecreasing |
|---|---|---|---|---|
| topstep | NQ | -364 -153 53 285 563 985 1,639 2,794 5,323 10,772 21,449 36,303 53,303 70,157 84,773 97,948 109,855 | True | True |
| topstep | MNQ | -13,246 -14,818 -16,780 -19,292 -22,622 -27,161 -33,877 -44,577 -61,614 -61,632 -15,649 -4,098 -1,227 -1 798 1,431 2,005 | False | True |
| lucid | CL | -6,925 -2,140 1,584 5,449 6,513 6,914 7,293 7,711 8,130 8,543 8,895 9,176 9,387 9,524 9,622 9,698 9,763 | True | True |
| tradeify | 6E | -5,750 -5,750 -5,750 -5,750 295 8,068 8,767 8,952 9,110 9,408 9,888 10,470 11,186 12,032 13,585 15,659 18,557 | True | True |
| mffu | GC | -9,180 -8,468 -297 3,307 4,084 4,348 4,657 5,014 5,422 5,821 6,189 6,491 6,702 6,825 6,892 6,929 6,956 | True | True |
| bulenox | NQ | -2,655 -1,995 -1,485 -1,017 -605 -185 224 641 1,048 1,435 1,776 2,085 2,338 2,553 2,727 2,885 2,997 | True | True |
| bulenox | ZS | -15,834 -16,480 -16,376 -4,136 2,754 3,221 3,331 3,355 3,349 3,391 3,423 3,427 3,427 3,427 3,427 3,427 3,427 | False | True |
| tradeify | MCL | -5,750 -5,750 -5,750 -5,750 -5,750 -5,750 -5,750 -5,750 -5,750 -823 -145 -145 -145 -145 -145 -145 -145 | True | True |

Monotonicity of expected net cash in mu: the check FAILS. EV is not nondecreasing in mu. In the 0.25-step
scan above (limit case, 8 pairs) it is nondecreasing for 6 pairs and not for 2. For topstep MNQ, EV falls from
-13,246 at mu = 0 to -61,632 at mu = 2.25, then rises to -1 at 3.25 and crosses 0 at 3.26. For bulenox ZS it falls from
-15,834 at mu = 0 to -16,480 at 0.25 before rising (plus a decrease of a few dollars on its flat positive plateau above
the threshold). P10K is nondecreasing for all 8 pairs. Over the grid check's evaluated lattice points (6,374 points),
48 of 121 pairs show at least one EV decrease between consecutive points. The pair records' own cached points
show non-monotone steps for bulenox 9, lucid 1, topstep 23, tradeify 5 (by firm).

Mechanism: as the net drift d = mu - c rises toward 0 from below, attempts last longer before they breach (up to
E.19's 756-trading-day horizon; a timed-out attempt counts as a failure and is followed by a reset or a new purchase,
E.19's convention). Each long attempt pays more rebills (Topstep, 49 per 21 trading days) or more API periods
(Topstep 14.50, Bulenox 100 per started period). So EV per cycle falls before passes start to pay. The trough lies
entirely at EV < 0.

Consequence for the thresholds: the bisection's monotonicity assumption does not hold, so every threshold was
confirmed on the grid (section 2.4; gridcheck/<firm>__<code>.json). Result: 121 of 121 pairs confirmed on every threshold, 0 corrected; stored point recomputed bit-for-bit in 121 of 121 pairs; 6,374 lattice points in all, 4,713 of them new.

A related rule effect: for micro products at Tradeify (and Topstep's micros at high mu), the evaluation can pass,
but 20 one-lot round trips a day rarely make a day of more than USD 150. That is the firm's winning-day threshold
for a payout (Tradeify: 5 days above 150; Topstep XFA: 5 days of 150+). So no payout ever qualifies. EV then equals
the fees paid (for tradeify M6E, -145 at every mu from 1.5 to 4, SE 0), and the funded balance at the 756-day
horizon is not credited (E.19's convention). These pairs report "> 4".

## 9. Runtimes and memory

All times are PDT, from the logs' own stamps (A3_runtimes.json). Everything ran at nice 10, with at most 4 worker
processes forked from one parent that shares the draws copy-on-write.

| step | when (PDT) | detail |
|---|---|---|
| E.19 regression (A3_regress_e19.py) | first spawn, 10:26 | 2.71 s (E.19 rules) + 2.59 s (E.26 record) |
| time probe | first spawn, before 10:43 | 4 pairs on 2 workers, 1:12.9, max RSS 665 MB |
| main run (A3_run.py run) | 10:43:58-11:00:02 | 128 pairs on 4 workers; worker-seconds 3,954; 1,838 evaluations; slowest pair 94 s; max RSS per worker 686 MB (the first trial hit 7.9 GB before the assembly was chunked, A3_log.md) |
| usage-limit pause, re-spawn | 11:00-15:12 | first spawn cut before writing the outputs; not work time |
| unit tests | 15:15:09-15:15:14 | 14 passed, 4.9 s, max RSS 969 MB |
| grid-check trial | 15:18:03-15:19:27 | 2 pairs on 2 workers |
| grid check + monotone scan | 15:19:39-16:03:19 | 119 pairs on 4 workers (121 with the trial); 4,713 new evaluations; worker-seconds 10,134; max RSS per worker 808 MB; monotone quarter points in the parent, 16:01:23-16:03:19 |
| Bulenox Option 2 | 16:03:25-16:05:37 | 25 pairs on 4 workers (bisection only) |

Memory: system memory in use was 3.0 GB before the grid check and at most 4.5 GB during it (free -m at 15:20, 15:22
and 15:42), so the job's peak stayed under 1.5 GB above baseline. That is within the brief's 3 GB.

## 10. Choices this worker made that the lead may want to revisit, and what is not done

1. Plans. The first-listed standard 50K plan, per the A2 readers: Topstep 50K Trading Combine Standard; LucidPro 50K
   (DLL-on, the listed price); Tradeify Growth 50K; MFFU Builder 50K Default; Bulenox Qualification 50K Option 1
   (trailing). The Bulenox A2 reader left the option to the lead. Option 2 (EOD, DLL 1,100) was computed beside it:
   all thresholds are identical except NQ (mu*_lim 1.30 vs 1.37, mu*_mkt 2.30 vs 2.37, mu10K 3.08 vs 3.10).
2. Pairs not computed. SI, SIL and MET (11 pairs) have no sigma_1m: no owned data, no A1 value, and OC-1 names no
   sibling. C5's "unknown gives 1" is a score default, not a model input. A value from the lead would let them run.
3. Restricted products. Listed-but-restricted or position-limit-0 pairs were computed anyway and flagged (MFFU HG,
   NG, QG, SI; Topstep HG, SI), so the lead can apply the Layer 2 gate.
4. Grid confirmation tolerance. Sub-grid gaps of 0.10 tick whose two ends are both far from the threshold
   (EV < -max(5 SE, USD 100); P10K < 0.40) were not evaluated point by point (section 2.4). A full 0.01 scan below
   every threshold was estimated at about 37,000 evaluations (about 6 h on 4 workers) and was not run.
5. E.19 regression. The published -250 bootstrap headline was cited from its stored record, not re-run (data rule).
   The substitute is E.19's normal-tail twin of the same job.
6. Conservative firm mappings (section 4), notably: MFFU has no reset price, so every failure buys a new evaluation at
   153; Lucid's and MFFU's funded stages end after payout 5, and Bulenox's after payout 3 (live stages valued at 0);
   Bulenox gets 90% throughout and a 21-trading-day attempt horizon; breach tests are intraday where the firm does not
   say.
7. E.19 cycle conventions inherited: a timed-out attempt is a failure followed by a reset; balances at the 756-day
   horizon are not credited. Together these make the EV trough (section 8) and the "> 4" of the low-P&L micros.
8. cost_per_attempt_usd counts evaluation fees only (purchase or first month, rebills, resets) per attempt, ratio of
   means at mu = 0. Variants with the API and with activation are in the JSON.
9. The sourced mean spreads (6E 1.2, ZC 1.26, ZS 1.118, ZW 1.1 ticks) enter only a sensitivity. The spec's S_rt is a
   median, and the median-spread readings are 1 tick or unknown.

Not done: the bootstrap re-run of E.19's headline (data rule); the grid confirmation of the Bulenox Option 2
sensitivity (bisection only); any scoring (by design).
