# Stage E.23 verdict verification (VerdictVerifier-FableXHigh)

Brief: reports/stage_e23_briefs/brief_verdict_verify.md. Written 2026-10-17 (PDT); times below are PDT from file mtimes,
JSON timestamps and git. Scripts and raw outputs beside this file: recompute_file_based.py -> recompute_file_based.json
(343 rows), spot_audit.py -> spot_audit.json, make_tables.py -> tables.md (every table referenced as T1..T7). Nothing
outside reports/stage_e23_briefs/verify/ was written; no marker, result, freeze, registry or input file was touched; no
code of the run was imported (every number below comes from my own implementations reading the written files and, for
the spot audit, the ext2010 parquet stores inside 2010-07-01..2019-04-30 only).

## Verdict

**VERIFIED WITH NOTES.** No BLOCKING finding. Every number that enters the E.23 verdict reproduces from the frozen
inputs and the run's own outputs with my own code: the five trigger-holds' base and stress statistics (n, mean, sd,
Sharpe, raw t, Newey-West t, the OLS alpha on v_T1/v_T2, its Bartlett HAC t, the plain t, p_alpha, R2, betas,
correlations), alpha3 and the in-market fraction, Holm over the five (nothing rejected; smallest p_alpha 0.3095 against
0.01), the survivor rule (no survivor: largest alpha t_NW 0.552, largest base Sharpe 0.207), DSR at N 538 (all far
below 0.95; four values differ from the run only at 2-3e-9 relative, the run's normal-quantile approximation), the CSCV
PBO (0.428571 = 30/70), the W_cf power gate (below 0.2 at every S from 1 to 4), N 533 -> 538 in the registry, and the
marker order (each marker written before its computation; nothing read in confirmation; no written series dated after
2019-04-30). An independent re-simulation of all five books from the ext2010 parquet stores (own marks, chained
returns, EWMA sigma, roll legs, D8 costs, units, capped net position, orders) reproduces the run's daily net series
value for value (max |diff| 0.0 on 9,668 series dates in both cases), and the unit-level checks of brief item 4 hold on
every unit: entry at the first settlement mark after the decision time (d_e = d0 for all 3,846 units; 0 moved), exit
exactly h marks later, size 0.40 / (sigma x notional) with sigma from the returns strictly before entry, D8 base cost
per side and stress = commission + 2 x slippage, and no trigger-day intraday P&L (the entry day carries only the fill
cost). The verdict the lead drew from the run, "no survivor; every discovery survivor would have ended INCONCLUSIVE BY
DESIGN on W_cf", stands. Seven NOTEs in section 4; none changes a number or a verdict.

## 1. What the run says and what I checked

The discovery read (marker 03:33:57, result 03:34:35) evaluated the five registered trigger-holds on W_ext
(2011-07-27..2019-04-30) and found no survivor: every Holm check is false, the smallest p_alpha is 0.3095 (E23-MEZFh5),
the largest alpha HAC t is 0.552 and the largest base Sharpe 0.207, against a per-test bar of t >= 2.0 and Sharpe >= 0.3
and a Holm step-1 threshold of 0.01. The confirmation step (marker 03:35:29.8258, result 03:35:29.8263) had S = 0
survivors, read nothing and wrote an empty verdict table. I recomputed every number entering that verdict from the
written daily series, the frozen trend regressors, the power table, the events files and the registry (section 2), then
re-simulated the five books from the bar stores and checked the brief's unit-level invariants (section 3).

## 2. File-based recomputation (recompute_file_based.json; tables T1-T4, T7)

343 rows compared; 339 agree within 1e-9 relative; 4 differ by 2-3e-9 relative (the DSR values; cause in 2.4).

### 2.1 Statistics per trigger-hold and case (T1)
For all five trigger-holds and both cases: n, mean, sd (ddof 1), net Sharpe (mean/sd x sqrt 252), raw t, Newey-West t
(Bartlett, lags h), the OLS alpha on the same root's v_T1 and v_T2 over the series dates (zero where the trend book has
no value: 2011-07-27/28 for NQ, 2011-07-28 for ZF/ZN/ZB, E.21's zero-when-flat convention, spec 1), its Bartlett HAC t
at lags h, the plain OLS t (n - 3 df), p_plain, p_nw, p_alpha = max, R2, both betas and both correlations: all match
within 1e-9 relative (260 rows). Base-case key numbers (run = mine):

| id | n | Sharpe | raw t | raw NW t | alpha | alpha HAC t | plain t | p_alpha |
|---|---|---|---|---|---|---|---|---|
| E23-MEZFh5 | 1936 | 0.20660 | 0.5727 | 0.6168 | 1.3827e-4 | 0.5518 | 0.4974 | 0.30949 |
| E23-MEZNh5 | 1938 | 0.13784 | 0.3822 | 0.4003 | 1.0430e-4 | 0.3831 | 0.3578 | 0.36028 |
| E23-MEZBh5 | 1938 | 0.01631 | 0.0452 | 0.0460 | 2.8154e-5 | 0.0998 | 0.0969 | 0.46142 |
| E23-H6NQh5 | 1928 | -0.50417 | -1.3945 | -1.4593 | -9.1830e-4 | -1.6059 | -1.6320 | 0.94858 |
| E23-H6NQh20 | 1928 | -0.37247 | -1.0303 | -1.1179 | -4.1729e-4 | -0.7145 | -0.7451 | 0.77184 |

Stress-case rows match the same way (T1). Every series is sorted, distinct, inside 2011-07-27..2019-04-30 and has
n = n_dates. The trend regressors are E.21's: the sum over the 17 per-root files equals the published T1 and T2 base
series on all 3,205 dates (max |diff| 0.0), and the per-root files cite the published results' current sha256s.

### 2.2 Holm, survivor rule, survivors (T2)
Holm step-down at one-sided 0.05 over five on the base p_alpha rejects nothing (smallest p 0.3095 > 0.01); no
trigger-hold has alpha t_NW >= 2.0 or base Sharpe >= 0.3; eligible = ranked = survivors = [] (run and mine). The
survivor rule as coded (Holm AND t_NW >= 2.0 AND Sharpe >= 0.3, cap 4, ties by Sharpe then id) is the prereg's.

### 2.3 Confirmation gate (T4)
From the power table's W_cf n_dates (1170 for ZF/ZN/ZB, 1204 for NQ): E[t] = 0.5 sqrt(n/252) = 1.0774 / 1.0929,
power at b = 2.0 is 0.17810 / 0.18218 (run values match), and at b = max(2.0, z(1 - 0.05/S)) for S = 1..4 it is
0.178/0.182, 0.178/0.182, 0.147/0.150, 0.122/0.125: below 0.2 for every S, so every W_cf row is gated whatever the
survivor count. Every power-table row (expected_t, power_gate, power_holm1 at K 5, inconclusive flag) matches. With
S = 0 nothing was gated or read: confirmation_result.json has survivors [], trigger_holds {}, verdict rows {},
n_trials 538; the outputs contain no W_cf series (the latest date in any written series is 2019-04-30).

### 2.4 DSR at N 538 and CSCV PBO (T3)
DSR: daily Sharpe, population moments, Sharpe variance over the five discovery series 3.189280e-4 (match), E[max SR]
under the null 0.0549058 (match), DSR per trigger-hold 6.91e-5 / 3.08e-4 / 0.0211 / 0.0332 / 0.0089 for NQh5 / NQh20
/ ZN / ZF / ZB. Four of the five differ from the run at 2.0-3.3e-9 relative (NQh5 within 1e-9): the run's helper
(funnel/multiple_comparisons.py, lines 32-60) uses Acklam's rational approximation to the normal quantile
(|err| < 1.15e-9) and math.erf for the cdf, mine uses scipy. The difference is 1e-11 in absolute DSR against a bar of
0.95; it is not a disagreement about the quantity. Every DSR is far below 0.95.
PBO: aligned grid of 1940 union dates (2011-07-27..2019-04-30, zero off a series' own dates), 8 contiguous blocks of
1940 // 8 = 242 dates, 70 symmetric splits, in-sample winner by summed P&L, out-of-sample rank (worse + 0.5)/5, PBO =
share of logits <= 0: 0.428571 = 30/70 (match), winner mean OOS -0.18232 (match), P(winner OOS > 0) 0.471429 (match).
NOTE: the helper's block rule drops the last 1940 - 8 x 242 = 4 dates; with np.array_split (no date dropped) PBO is
0.485714 (34/70). Both are below 0.5; the number is descriptive here (no survivor), and the block convention is the
program's (D.1f), so this is a note, not a finding against the run.

### 2.5 N and the registry
ledger/trial_registrations.jsonl line 9 = r008-E23: test E23, the five ids, n_before 533 (= r007's n_after), n_after
538, the freeze sha256 24dcf4dd...3df5a5, harness dd2bcc60...09e4, time 03:33:45. Both markers and both results carry
that freeze sha256 and the registry's sha256 25c04088...a302, which is the working copy's (HEAD still has 8 lines: the
entry was appended after the freeze commit, as the order requires). N = 538 enters the DSR as n_trials.

### 2.6 Order of operations and the markers
Freeze commit 75874c4 03:33:43 -> registration 03:33:45 -> discovery marker 03:33:57.103 (O_EXCL, mode 0444) ->
discovery result 03:34:35.017 (sha256 c3f71384...590d) -> confirmation marker 03:35:29.8258 (records that discovery
sha256) -> confirmation result 03:35:29.8263. In trigger_hold/run.py the marker is written in run_phase (line 196)
before compute_fn (line 202), after preconditions that only hash files and preflight store metadata (no row read);
evaluate.discovery reads bars only inside read_root, called from compute. Both markers were therefore written before
their computations. Every file in the freeze (108) still matches its recorded sha256.

### 2.7 "Nothing dated after 2019-04-30 read in discovery"
Every computed quantity is bounded: run.py sets ctx.last = 2019-04-30 for discovery (line 157), and marks, returns,
sigma, units, fills and series all come from ctx.window_dates (starts <= d <= ctx.last); the trend regressors are taken
on the series dates only; the W_cf events files hold trigger decision timestamps only (no price), as P2.3 allows. The
written series end 2019-04-30. NOTE (not a finding against any number): the frozen E.21 loader concatenates both
eras (base_rules/context.py store_loader -> store.load_product, which reads every era in the manifest), so the step2
store's rows (2019-05-06..2024-02-29) were loaded into memory by the discovery run even though nothing was computed
from them; the only touches of that frame beyond the window are the boundary-splice contract comparison
(multiday.daily.with_boundary_splice) and the limit-lock rule construction, neither of which yields a value that
enters any statistic. The lead's sentence should read "computed nothing from any bar dated after 2019-04-30"; the lead
decides whether a loader change is wanted for later stages.

### 2.8 Events and the entry rule, from files
Every K2 event's decision time is 07:21 CT (the close of the 07:20 bar; the prereg table says "07:20 CT", a one-minute
labelling difference, not an entry difference) and every H6 event's is 14:30 CT; the settlement bar opens 14:00 CT
(rates) and 15:15 CT (NQ, to 2020-10-25). 0 of 1860 + 137 + 143 + 142 events decide at or after the settlement bar,
so d_e = d0 for every unit (the run counts no "entry moved" unit). Events outside W_ext: 2 / 2 / 2 / 36, equal to the
run's exclusions. The events files' sha256s equal the power table's recorded values.

### 2.9 Power table versus the realized books (NOTE)
The power table (calendar-only by design) counts 1939 (rates) / 1934 (NQ) book dates; the books have 1936 / 1938 /
1938 / 1928 (dates whose settlement bar is missing drop out of the realized mark list). NQ units 1727 / 1711 in the
table against 1729 / 1713 realized (two fewer roll-blackout exit exclusions once the missing marks shift the h-th
mark), non-overlapping 374 vs 373 for h 5. Power at the realized n_dates: 1936 -> 0.2694, 1928 -> 0.2685 (table
0.2699 / 0.2693): no inconclusive flag changes. The "exit across the store boundary" label in the table is "exit: no
h-th mark date" in the run (the discovery context ends 2019-04-30), same two units.

## 3. Spot audit of the books (spot_audit.json; tables T5, T6)

The discovery output holds per-trigger-hold daily series and aggregate counters only, not the per-unit and per-fill
records the brief names, so I rebuilt the books myself (spot_audit.py, run 07:22:25-07:22:35 after the pytest suite
had ended at 05:41:25 and with 10.7 GB available, nice 10, one root at a time, the ext2010 stores only, columns
ts_event/open/close/raw_symbol/trade_date/in_scheduled_closure plus the sidecar metadata; each store's sha256 equals
the discovery marker's preflight record). My implementation follows the frozen definitions (lead_spec sections 1-3,
E.21 sections 1, 2, 7, 8) without importing any project module: calendar trade dates = weekdays minus full closures;
MK = open of the settlement bar (rates 14:00 CT) or, where a scheduled closure begins at the settlement minute (NQ
15:15 CT), the close of bar S - 1; chained daily returns split at each recorded roll; sigma = sqrt(261 x EWMA
variance, com 60, mean removed, 60-return warm-up) of the returns dated strictly before the date; per-contract path with
roll legs closed at the last usable bar before the splice and reopened at the first at or after it; D8 cost per side =
commission/2 + ceil(side_ticks(30-minute CT bucket of the fill bar) x tick value), stress = commission/2 + 2 x the
slippage part; units from the frozen events with the run's exclusion rules (window, roll blackout, early halt, missing
mark or signal bar, no h-th mark); net = clip(sum of active units, -1, 1), orders only where net changes, size
net x 0.40 / sigma / (MK price x tick value).

Results (T5): for all five trigger-holds the unit counts by reason, units (131/137/136/1729/1713), non-overlapping
events (71/77/76/373/95), n_dates, in-market fraction, book counters (opens, closes, flips, openings sized), fills by
kind (incl. 9/15/14/13/31 roll pairs) and total fills (160/184/180/429/289), gross, costs and net all equal the run's;
the base and stress daily series are identical on every date (dates equal, max |diff| 0.0, 0 values differing). No
backstop close, no failed-interval hold, no uncalibrated-bucket fill, no series date added. alpha3 (the descriptive
regression adding the root's one-contract buy-and-hold return, which I recomputed from my per-contract path) matches
the run's alpha, betas, t_plain, t_NW, p_alpha and R2 in both cases within 1e-9 relative.

Spot units (T6; 3 to 4 per trigger-hold: the first unit, the last unit, a unit whose hold spans a roll, and for NQ the
unit entering at the book's first flip):
- Entry at the first settlement mark after the decision time: every spot unit decides at 07:21 CT (K2) or 14:30 CT
  (H6), before 14:00 / 15:15 CT, and enters at MK(d0); across all 3,846 units d_e = d0 and 0 entries moved.
- Exit h marks later: marks between d_e and d_x equal h (5 or 20) for every unit.
- Sizing: e.g. E23-MEZFh5's first unit (2011-07-28): sigma 0.040260 from 260 prior returns, MK 15448 ticks ->
  V $120,687.50, n = 0.40 / (0.040260 x 120687.5) = 8.2324e-5 contracts per $ of capital; the same for ZN (5.3042e-5),
  ZB (3.3324e-5), NQ (5.3790e-4 at V $4,720 on MNQ). The next-mark value equals n x (MK(d_e + 1) - MK(d_e)) x tick
  value for every spot unit with an order (match True), which fixes n and the start of the P&L at MK(d_e).
- Costs per side: ZF 507 c base / 898 c stress (commission 116 c + ceil(0.5001 x 781.25) = 391 c; 898 = 116 + 2 x
  391), ZN 913 / 1695 (131 + 782), ZB 1702 / 3266 (138 + 1564), MNQ 105 / 149 (61 + 44, bucket 15:00-15:30 of the
  15:14 bar): the D8 table's values at the fill minute, and stress = commission + 2 x slippage on every fill
  (stress_eq_comm_plus_2x_slip True). Round trips $10.14 / $18.26 / $34.04 / $2.10 equal the prereg's cost table.
- No trigger-day intraday P&L: on every opening from flat the entry-day value is exactly -n x cost (base and stress):
  ZF -4.1738e-4 / -7.3927e-4 on 2011-07-28, NQ -5.6480e-4 / -8.0148e-4 on 2011-07-27, matching the run. On the two
  flip-day units the entry-day value also carries the outgoing position's mark-to-mark move (-0.0003534 cost part of
  +0.019121 on 2011-08-12), which is the previous unit's P&L to MK(d_e), not the new unit's intraday move; my
  re-simulation reproduces those values exactly.
- Roll-spanning units (one splice inside the hold: ZF/ZN/ZB 2011-08-30..09-07, NQ 2011-09-06..13 and 08-15..09-13)
  and the units entering at the first flips reproduce on d_e, the next mark and d_x in both cases.
- Excluded examples reproduce by reason: K2 exits on 2011-10-07 (early halt), NQ exits on 2011-09-08 (roll
  blackout), and the last events of April 2019 (no h-th mark before 2019-04-30).

## 4. Findings

BLOCKING: none.

NOTE-1 (numbers). Four DSR values differ from the run at 2.0-3.3e-9 relative (section 2.4): the run's helper uses
Acklam's normal-quantile approximation (|err| < 1.15e-9); the quantity is the same and every DSR is below 0.001.
NOTE-2 (data use wording). Discovery computed nothing from any bar dated after 2019-04-30 (ctx.last, section 2.7), but
the shared E.21 loader concatenates both eras, so the step2 store's rows were loaded into memory during the discovery
read. No value from them enters any statistic; the lead's sentence should say "computed nothing from", and the lead
may want the loader bounded by ctx.last in later stages.
NOTE-3 (PBO convention). The program's CSCV helper uses 8 blocks of n // 8 dates and drops the last 4 of 1940 dates;
with equal np.array_split blocks the PBO is 0.4857 instead of 0.4286. Descriptive only here (no survivor); both < 0.5.
NOTE-4 (power table vs realized books). Calendar-only counts differ from the realized books by up to 6 book dates
and 2 units (section 2.9); the gate decisions do not change (power 0.2685-0.2694 at the realized n_dates).
NOTE-5 (missing unit/fill artifacts). The discovery output has no per-unit or per-fill records (the brief's "units and
fills files"); the spot audit had to re-simulate the books. Later stages should write them (E.21 did).
NOTE-6 (labelling). The prereg says K2 decides "at 07:20 CT"; the frozen events carry 07:21 CT (the 07:20 bar's
close). No effect on any unit (settlement is 14:00 CT).
NOTE-7 (registry). ledger/trial_registrations.jsonl line r008 (N 538) is in the working copy, not yet committed; the
markers and results record the working copy's sha256. It should be committed with the stage's results.

Could not do / not done: nothing required by the brief is outstanding. I did not read any bar outside
2010-07-01..2019-04-30 (ext2010 stores only), no W_cf bar, nothing dated 2024-03-01 or later, no holdout or sealed
store; no marker, result, freeze, registry or input was modified; no code of the run was rerun or imported.

Artifacts: reports/stage_e23_briefs/verify/{verdict_verify.md, tables.md, recompute_file_based.py,
recompute_file_based.json, spot_audit.py, spot_audit.json, make_tables.py}. Tables T1-T7 are in tables.md (T7 lists
all 343 file-based rows with run value, my value and the match flag).
