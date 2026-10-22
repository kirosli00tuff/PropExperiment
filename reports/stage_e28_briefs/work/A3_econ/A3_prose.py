"""Fixed prose of A3_econ.md (composed by A3_write_md.py). Numbers in SUMMARY and RUNTIME come from the run."""

HEAD = """# Stage E.28 A3: firm-contract economics per (firm, candidate) pair (spec section 3)

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
from the A2 record."""

METHOD = """## 2. Method

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
allowed at the 50K evaluation stage (text in position_limit_text)."""

MAPPING_INTRO = """Each firm's standard 50K plan is the first 50K evaluation plan its A2 reader found on the pricing page (spec
section 3). kind: exact = represented as stated; conservative = the simulator cannot represent it or the record is
unclear, and the form harder on the trader is used; ignored = no effect on a 20 round-trip, size-1, 1-minute-hold
strategy; policy = the trader's choice, fixed as stated."""

CONSERVATIVE = """## 4. Rules not representable as stated, and the conservative forms used

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
one (Topstep with its rebill credits, Lucid 120, Tradeify 95); payouts by a route without a transfer fee."""

INPUTS = """Lead decisions applied exactly: OC-1 (sigma_1m and R_d in ticks for a candidate without owned window data from the
owned sibling on the same price, x_ticks(cand) = x_ticks(sibling) x tick(sibling) / tick(cand), units checked; volume
never transfers) and OC-2 (ADV: A0's v_0 median for owned roots, else A1's published figures; both kept; ADV is not an
input of the economics and is passed through). SIL, SI, MET, ETH and the micro yields have no owned data and no A1
value for sigma_1m, so their pairs are not computed (the spec's section 3 gives no default for sigma). S_rt: the A1
readers sourced a one-tick touch for CL (volume statement), GC and SI (CME, all or most hours) and the four Treasury
futures (> 99% of the day at the minimum increment); everything else is the spec's default 1 ("u"). The figures the
readers found for 6E (1.2), ZC (1.26), ZS (1.118) and ZW (1.1) are means, not medians, and enter only a sensitivity.
Tick values agree with A0 wherever A0 has them (v_matches_A0 in the JSON)."""

RESULTS_INTRO = """Columns: v = tick value; F_rt = the firm's round-trip commission and fees for 1 contract (source and quote in the
JSON); sigma_T = sigma_1m in ticks; mu values in ticks per trade ("> 4" scores 0 under the spec); cost/attempt = section
2.5; room = MLL / (R_d v); pos. limit = contracts of that product at the 50K evaluation stage. Flags: "restricted_now"
(listed with a fee but currently restricted), "position_limit_0" (listed, 0 contracts now), "sigma ... from sibling"
(OC-1), "not computed" (sigma unknown), "non-monotone cached points" (section 8). Every Topstep row also carries the
3.70 fee-conflict flag, every Lucid row the exchange-fee-inclusion flag, and rows with the default spread the "S_rt
default 1 (u)" flag (omitted from the table, kept in the JSON)."""

SENS = """Ex-API: the same cycles without the API subscription (Topstep 14.50, Bulenox 100 per month). Alt fee: Lucid at the
highest fee for that product at the other four firms (the spec's 'u' rule, since Lucid does not say whether its
per-side commission includes exchange and NFA fees); Topstep at max(3.70, table fee) in both stages (the LFA-costs
page's simulated Combine fee). S_rt mean: the market case at the readers' sourced mean spread instead of 1."""

TESTS = """Regression against E.19 (A3_regress_e19.py, output A3_regress_e19.json). E.19's published zero-edge best case,
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
9. Bridge formulas equal prop_econ.returns.bridge_min to 1e-12; every firm has a mapping table."""

MONOTONE = """Monotonicity of expected net cash in mu: the check FAILS. EV is not nondecreasing in mu. In the 0.25-step
scan above (limit case, 8 pairs) it is nondecreasing for 6 pairs and not for 2. For topstep MNQ, EV falls from
-13,246 at mu = 0 to -61,632 at mu = 2.25, then rises to -1 at 3.25 and crosses 0 at 3.26. For bulenox ZS it falls from
-15,834 at mu = 0 to -16,480 at 0.25 before rising (plus a decrease of a few dollars on its flat positive plateau above
the threshold). P10K is nondecreasing for all 8 pairs. Over the grid check's evaluated lattice points ({NPTS} points),
{NDROP} of 121 pairs show at least one EV decrease between consecutive points. The pair records' own cached points
show non-monotone steps for {VIOL} (by firm).

Mechanism: as the net drift d = mu - c rises toward 0 from below, attempts last longer before they breach (up to
E.19's 756-trading-day horizon; a timed-out attempt counts as a failure and is followed by a reset or a new purchase,
E.19's convention). Each long attempt pays more rebills (Topstep, 49 per 21 trading days) or more API periods
(Topstep 14.50, Bulenox 100 per started period). So EV per cycle falls before passes start to pay. The trough lies
entirely at EV < 0.

Consequence for the thresholds: the bisection's monotonicity assumption does not hold, so every threshold was
confirmed on the grid (section 2.4; gridcheck/<firm>__<code>.json). Result: {GRID}.

A related rule effect: for micro products at Tradeify (and Topstep's micros at high mu), the evaluation can pass,
but 20 one-lot round trips a day rarely make a day of more than USD 150. That is the firm's winning-day threshold
for a payout (Tradeify: 5 days above 150; Topstep XFA: 5 days of 150+). So no payout ever qualifies. EV then equals
the fees paid (for tradeify M6E, -145 at every mu from 1.5 to 4, SE 0), and the funded balance at the 756-day
horizon is not credited (E.19's convention). These pairs report "> 4"."""


RUNTIME = """## 9. Runtimes and memory

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
and 15:42), so the job's peak stayed under 1.5 GB above baseline. That is within the brief's 3 GB."""

CHOICES = """## 10. Choices this worker made that the lead may want to revisit, and what is not done

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
sensitivity (bisection only); any scoring (by design)."""

SUMMARY = """132 (firm, candidate) pairs are listed (each firm's product list from its A2 record, restricted products
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
tests pass, including the per-trade layer's daily mean T (mu - c) v and SD sqrt(T) sigma_T v. Nothing is scored."""

PROSE = {"head": HEAD, "summary": SUMMARY, "method": METHOD, "mapping_intro": MAPPING_INTRO,
         "conservative": CONSERVATIVE, "inputs": INPUTS, "results_intro": RESULTS_INTRO, "sens": SENS,
         "tests": TESTS, "monotone": MONOTONE, "runtime": RUNTIME, "choices": CHOICES}
