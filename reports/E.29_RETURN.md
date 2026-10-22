# Stage E.29 return: combining the ranked contracts in one prop account (simulation study)

Lead: Opus 5.5, effort high, Pro plan (Ultracode off; review by an Opus 5.5 xhigh agent in a fresh context, V46
item 5). Session 488b039c-486e-454d-a9bd-0fba40def8ea. Times PDT. Prompt: docs/prompts/STAGE_E.29.md. Status file:
reports/stage_e29_STATE.md.

## 1. Summary

Can two or three ranked contracts in one 50K prop account lower the per-trade break-even, and at what correlation
does any gain disappear? E.28's economic model was applied unchanged to the combined account's daily P&L. B0 (QM
alone) reproduces E.28 exactly at all five firms, and every threshold was grid-confirmed unchanged.

With only QM carrying an edge, no basket beats QM alone at any firm or rho (0 of 80 cells). Each raises QM's
break-even by 0.08 to 1.39 ticks, since QM gives up trades and the other member pays its own fees. With every
member at the same multiple of its own break-even, 27 of 76 cells beat QM alone, at Topstep, Tradeify and Bulenox.
24 of them contain MGC, whose alone break-even is inflated by payout thresholds a one-lot micro rarely clears; the
basket wins by giving MGC 0.7 sigma a trade or more. QM + ZM, the like-for-like pair, moves no break-even outside
Bulenox. Correlation barely matters: no flag turns off between rho 0 and 0.75, because no gain came from
diversification. A zero-edge contract never helps. E.28's v2 firm order stands; keep the pilot on QM alone.

## 2. Guardrail evidence

Start checks (19:20, reports/stage_e29_briefs/start_checks.txt, script checks.sh), verbatim excerpts:

```
# E.29 checks: start
$ date
Wed Oct 21 19:20:10 PDT 2026
$ git status --short | wc -l (tracked changes: git status --short -uno)
1412
$ git log --oneline -3
84704b4 docs: V46 (user decisions of 2026-10-21, Pro plan) and the Stage E.29 prompt
9402789 docs: Stage E.28b prompt (E.28 continued on the Pro plan)
2615df4 Stage E.26 data move and housekeeping
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m screening.harness_freeze verify --expected 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
preflight OK: 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
$ ledger
36402 ledger/databento_spend.jsonl
034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700
$ ledger total per account (SpendGate.account_spent_usd)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 353.455228 cap 355.38 headroom 1.924772
acct-3: spent 0.000000 cap 125.00 headroom 125.000000
$ uv run python -m screening.trial_registry status (N)
r005-E20S: E20S ['E20S-01', 'E20S-02', 'E20S-03', 'E20S-04', 'E20S-05', 'E20S-06', 'E20S-07', 'E20S-08', 'E20S-09', 'E20S-10', 'E20S-11', 'E20S-12', 'E20S-13', 'E20S-14', 'E20S-15', 'E20S-16', 'E20S-1 [line cut at 200 of 553 characters]
r006-E21: E21 ['E21-T1', 'E21-T2', 'E21-T3', 'E21-T4'] N 528 -> 532 at 2026-10-14T04:12:12-07:00
r007-E22: E22 ['E22-F1'] N 532 -> 533 at 2026-10-16T02:12:01-07:00
r008-E23: E23 ['E23-MEZFh5', 'E23-MEZNh5', 'E23-MEZBh5', 'E23-H6NQh5', 'E23-H6NQh20'] N 533 -> 538 at 2026-10-17T03:33:45-07:00
.env DATABENTO_API_KEY3: absent
```

End checks (reports/stage_e29_briefs/end_checks.txt):

```
# E.29 checks: end
$ date
Thu Oct 22 04:41:27 AM PDT 2026
$ git status --short | wc -l (tracked changes: git status --short -uno)
1437
$ git log --oneline -3
60eb6b6 Stage E.28 methods brief, ranking and pilot
54f07ab docs: V47 (QM research, pilot on hold) and the Stage E.30 prompt (QM volume check)
84704b4 docs: V46 (user decisions of 2026-10-21, Pro plan) and the Stage E.29 prompt
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m screening.harness_freeze verify --expected 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
preflight OK: 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
$ ledger
36402 ledger/databento_spend.jsonl
034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700
$ ledger total per account (SpendGate.account_spent_usd)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 353.455228 cap 355.38 headroom 1.924772
acct-3: spent 0.000000 cap 125.00 headroom 125.000000
$ uv run python -m screening.trial_registry status (N)
r005-E20S: E20S ['E20S-01', 'E20S-02', 'E20S-03', 'E20S-04', 'E20S-05', 'E20S-06', 'E20S-07', 'E20S-08', 'E20S-09', 'E20S-10', 'E20S-11', 'E20S-12', 'E20S-13', 'E20S-14', 'E20S-15', 'E20S-16', 'E20S-1 [line cut at 200 of 553 characters]
r006-E21: E21 ['E21-T1', 'E21-T2', 'E21-T3', 'E21-T4'] N 528 -> 532 at 2026-10-14T04:12:12-07:00
r007-E22: E22 ['E22-F1'] N 532 -> 533 at 2026-10-16T02:12:01-07:00
r008-E23: E23 ['E23-MEZFh5', 'E23-MEZNh5', 'E23-MEZBh5', 'E23-H6NQh5', 'E23-H6NQh20'] N 533 -> 538 at 2026-10-17T03:33:45-07:00
.env DATABENTO_API_KEY3: absent
```

Test suite: `uv run pytest -q -p no:cacheprovider`, the full suite, run detached at nice 10 under a memory watchdog
(reports/stage_e29_briefs/run_suite.sh, output pytest_end.out), 10-22 04:20:58 to 04:41:00. Available memory was
8,235 MB at launch, with a minimum of 3,050 MB:

```
FAILED tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha
1 failed, 8090 passed, 5 skipped, 3 xfailed, 54 warnings in 1194.76s (0:19:54)
```

The one failure is the known one. It pins harness v12 and has failed by design since v13; E.26's end run had the
same line. No repo code outside reports/, docs/ and progress.md changed during E.29. The E.29 tests live outside
tests/ (OC-9): 11 passed (work/basket/test_e29_basket_final.out).

Scope kept: no outcome, holdout, embargo, research-window or E.28 pilot data was read; the only market data read was
owned one-minute bars of CL, ZM, GC and NQ dated 2022-10-01 to 2023-11-01 by file name (CorrMeasurer, holdout status
checked before and after: all_ok true, unlocks_logged 0 both times). No purchase, no Databento call, acct-3
untouched; nothing registered or frozen; N stays 538; REGISTRATION.md 0 bytes; prop_econ/ and every E.28 file
unedited (E.28's model imported read-only, sha256 in the STATE file); nothing under live/ or ops/; no key printed;
no push.

## 3. Results

### 3.1 The model (Z3)

The model was declared in reports/stage_e29_model.md (sha256 f393759f4af712a8...) before any E.29 code or run. In
short: each member of a basket trades T_i of 20 daily round trips (B3 7/7/6, the others 10/10), 1 contract each,
with gross P&L per trade normal(mu_i, sigma_1m,i^2) and E.28's limit-case cost. Members' daily P&L are normal with
mean m_i = T_i (mu_i - c_i) v_i and SD s_i = sqrt(T_i) sigma_i v_i, pairwise correlation rho on {0, 0.25, 0.5, 0.75}.
The account's day is their sum, normal(M, S^2) with S^2 = sum s_i^2 + 2 rho sum_{i<j} s_i s_j, and the combined
intraday path is a Brownian motion, so every rule E.28 mapped acts on the combined account through (M, S) on E.28's
own common random numbers; B0 is E.28's QM pair draw for draw. Position limits: only Topstep's 2-lot first XFA tier
can bind (B3 = QM + ZM + 0.1 MGC = 2.1 lots); primary form no-overlap (P&L-neutral in this model), sensitivity MGC
dropped on those days. Topstep's Tier 1 window is a scheduling constraint for size-1 trades (non-binding). Edge
setting (i): every member at k times its own E.28 break-even; setting (ii): QM at mu_QM, the others at zero edge.

### 3.2 Measured correlations (reference only, not an input)

Owned one-minute bars, front contract (highest-volume outright per trade date, roll dates dropped, early-halt dates
excluded), trade dates 2022-11-01 to 2023-10-31 (reports/stage_e29_briefs/E29_correlations.md). Pearson, 233 to 240
days:

| pair | daily return | daily range (% of price) |
|---|---|---|
| CL-ZM | 0.107 | 0.038 |
| CL-GC | 0.118 | 0.395 |
| CL-NQ | 0.088 | 0.143 |
| ZM-GC | -0.013 | 0.019 |
| ZM-NQ | -0.026 | 0.048 |
| GC-NQ | 0.159 | 0.378 |

On the rho grid: every return correlation sits between 0 and 0.25 (closest to 0 for the ZM pairs and about 0.1 for
CL with ZM, GC or NQ); range correlations reach 0.40 (CL-GC, GC-NQ), between 0.25 and 0.5. These are price
correlations. The model's rho is the correlation of a strategy's daily P&L. For direction-neutral one-minute trading,
P&L correlation follows from shared volatility days (closer to the range correlations, through the P&L variance)
more than from price direction, so the lead takes rho = 0 to 0.25 as the realistic band and 0.5 as a stress value.
This is a judgment, not a measurement.

### 3.3 Tables (Z4)

The full tables (per firm: every basket, rho and edge setting, with reporting-point pass rates, P(any payout),
EV per cycle, cost per attempt and daily SD) are in reports/stage_e29_briefs/E29_tables.md (generated from
E29_cells.json, 228 cells and 7 alone records). The compact version below shows, per firm, the break-even and the
mu10K analogue ("threshold / x10K"), limit case, against B0. "*" marks a cell that beats B0 by the declaration's
section 7 rule. "n/a": setting (i) cannot be run because MNQ's alone break-even at Bulenox is above 12 ticks. Every
threshold was found by bisection and then grid-confirmed (A3_econ.md 2.4): 0 of 470 moved (section 5).

**topstep** (setting (i): k* in units of each member's alone break-even; setting (ii): mu*_QM in ticks)

| basket | setting | B0 | rho 0 | rho 0.25 | rho 0.5 | rho 0.75 |
|---|---|---|---|---|---|---|
| B1 | i | 1.0 / 1.69 | 1.0 / 1.55 | 1.01 / 1.55 | 1.01 / 1.56 | 1.02 / 1.57 |
| B2 | i | 1.0 / 1.69 | 0.6 / 1.18 * | 0.6 / 1.18 * | 0.6 / 1.18 * | 0.61 / 1.17 * |
| B3 | i | 1.0 / 1.69 | 0.77 / 1.3 * | 0.78 / 1.3 * | 0.79 / 1.3 * | 0.8 / 1.3 * |
| B4 | i | 1.0 / 1.69 | 0.98 / 2.04 | 1.0 / 2.02 | 1.01 / 2.02 | 1.03 / 2.01 |
| B1 | ii | 0.32 / 0.54 | 0.79 / 1.23 | 0.8 / 1.23 | 0.8 / 1.24 | 0.8 / 1.25 |
| B2 | ii | 0.32 / 0.54 | 0.49 / 0.98 | 0.5 / 0.98 | 0.5 / 0.98 | 0.5 / 0.97 |
| B3 | ii | 0.32 / 0.54 | 0.94 / 1.6 | 0.96 / 1.59 | 0.97 / 1.59 | 0.98 / 1.6 |
| B4 | ii | 0.32 / 0.54 | 0.45 / 0.92 | 0.45 / 0.91 | 0.46 / 0.91 | 0.46 / 0.91 |

**lucid** (setting (i): k* in units of each member's alone break-even; setting (ii): mu*_QM in ticks)

| basket | setting | B0 | rho 0 | rho 0.25 | rho 0.5 | rho 0.75 |
|---|---|---|---|---|---|---|
| B1 | i | 0.98 / 2.32 | 0.98 / 2.11 | 0.98 / 2.11 | 0.98 / 2.11 | 0.98 / 2.09 |
| B2 | i | 0.98 / 2.32 | 0.96 / 3.01 | 0.96 / 2.95 | 0.96 / 2.91 | 0.96 / 2.88 |
| B3 | i | 0.98 / 2.32 | 0.98 / 2.39 | 0.97 / 2.37 | 0.97 / 2.37 | 0.97 / 2.37 |
| B4 | i | 0.98 / 2.32 | 0.97 / 3.17 | 0.97 / 3.11 | 0.96 / 3.09 | 0.96 / 3.09 |
| B1 | ii | 0.33 / 0.77 | 0.77 / 1.66 | 0.77 / 1.66 | 0.77 / 1.66 | 0.77 / 1.64 |
| B2 | ii | 0.33 / 0.77 | 0.46 / 1.42 | 0.46 / 1.39 | 0.46 / 1.38 | 0.46 / 1.36 |
| B3 | ii | 0.33 / 0.77 | 0.89 / 2.17 | 0.88 / 2.16 | 0.88 / 2.15 | 0.88 / 2.15 |
| B4 | ii | 0.33 / 0.77 | 0.41 / 1.33 | 0.41 / 1.31 | 0.41 / 1.3 | 0.41 / 1.3 |

**tradeify** (setting (i): k* in units of each member's alone break-even; setting (ii): mu*_QM in ticks)

| basket | setting | B0 | rho 0 | rho 0.25 | rho 0.5 | rho 0.75 |
|---|---|---|---|---|---|---|
| B1 | i | 1.0 / 1.73 | 1.0 / 1.54 | 1.0 / 1.54 | 1.0 / 1.54 | 1.0 / 1.54 |
| B2 | i | 1.0 / 1.73 | 0.65 / 1.31 * | 0.65 / 1.31 * | 0.64 / 1.31 * | 0.64 / 1.31 * |
| B3 | i | 1.0 / 1.73 | 0.82 / 1.38 * | 0.82 / 1.38 * | 0.82 / 1.38 * | 0.82 / 1.38 * |
| B4 | i | 1.0 / 1.73 | 0.99 / 2.06 | 0.99 / 2.06 | 0.98 / 2.06 | 0.98 / 2.06 |
| B1 | ii | 0.43 / 0.75 | 1.17 / 1.79 | 1.16 / 1.79 | 1.16 / 1.79 | 1.16 / 1.79 |
| B2 | ii | 0.43 / 0.75 | 0.61 / 1.23 | 0.61 / 1.23 | 0.6 / 1.23 | 0.6 / 1.23 |
| B3 | ii | 0.43 / 0.75 | 1.31 / 2.21 | 1.31 / 2.21 | 1.31 / 2.2 | 1.3 / 2.2 |
| B4 | ii | 0.43 / 0.75 | 0.58 / 1.21 | 0.58 / 1.21 | 0.58 / 1.21 | 0.58 / 1.2 |

**mffu** (setting (i): k* in units of each member's alone break-even; setting (ii): mu*_QM in ticks)

| basket | setting | B0 | rho 0 | rho 0.25 | rho 0.5 | rho 0.75 |
|---|---|---|---|---|---|---|
| B1 | i | 1.0 / 2.56 | 1.0 / 2.29 | 1.0 / 2.24 | 1.0 / 2.17 | 1.0 / 2.13 |
| B2 | i | 1.0 / 2.56 | 0.99 / 3.01 | 0.99 / 3.01 | 0.98 / 3.01 | 0.98 / 3.01 |
| B3 | i | 1.0 / 2.56 | 0.99 / 2.54 | 0.99 / 2.54 | 0.99 / 2.5 | 0.99 / 2.43 |
| B4 | i | 1.0 / 2.56 | 0.99 / 3.13 | 0.99 / 3.13 | 0.99 / 3.13 | 0.99 / 3.12 |
| B1 | ii | 0.35 / 0.9 | 0.85 / 1.93 | 0.85 / 1.9 | 0.85 / 1.84 | 0.85 / 1.8 |
| B2 | ii | 0.35 / 0.9 | 0.54 / 1.63 | 0.53 / 1.63 | 0.53 / 1.63 | 0.53 / 1.63 |
| B3 | ii | 0.35 / 0.9 | 1.0 / 2.57 | 1.0 / 2.56 | 1.0 / 2.52 | 1.0 / 2.45 |
| B4 | ii | 0.35 / 0.9 | 0.51 / 1.6 | 0.51 / 1.6 | 0.51 / 1.6 | 0.51 / 1.6 |

**bulenox** (setting (i): k* in units of each member's alone break-even; setting (ii): mu*_QM in ticks)

| basket | setting | B0 | rho 0 | rho 0.25 | rho 0.5 | rho 0.75 |
|---|---|---|---|---|---|---|
| B1 | i | 1.0 / 1.47 | 1.0 / 1.42 | 0.98 / 1.43 * | 0.95 / 1.44 * | 0.93 / 1.45 * |
| B2 | i | 1.0 / 1.47 | 0.97 / 1.37 * | 0.96 / 1.37 * | 0.96 / 1.37 * | 0.95 / 1.37 * |
| B3 | i | 1.0 / 1.47 | 0.98 / 1.38 * | 0.95 / 1.39 * | 0.93 / 1.4 * | 0.91 / 1.41 * |
| B4 | i | 1.0 / 1.47 | n/a | n/a | n/a | n/a |
| B1 | ii | 0.72 / 1.06 | 1.58 / 2.25 | 1.54 / 2.27 | 1.51 / 2.28 | 1.47 / 2.29 |
| B2 | ii | 0.72 / 1.06 | 1.34 / 1.89 | 1.33 / 1.89 | 1.32 / 1.89 | 1.31 / 1.9 |
| B3 | ii | 0.72 / 1.06 | 2.11 / 2.97 | 2.05 / 2.98 | 1.99 / 3.0 | 1.94 / 3.02 |
| B4 | ii | 0.72 / 1.06 | 1.3 / 1.87 | 1.28 / 1.88 | 1.26 / 1.88 | 1.24 / 1.89 |

Market case (c + 1 tick spread per member), B0 against each firm's best basket (section 6 rule: Topstep B2, Lucid
B4, Tradeify B2, MFFU B2, Bulenox B3). In setting (ii), the basket's mu*_QM is higher than B0's at every firm and
every rho: +0.25 to +0.27 ticks at Topstep, Tradeify and MFFU, +0.12 at Lucid, and +2.09 to +2.26 at Bulenox. In
setting (i), k* is 0.83 at Topstep, 0.84 at Tradeify, 0.95 to 0.99 at Bulenox, 0.99 at Lucid and 1.00 at MFFU,
against B0's 1.00 (E29_tables.md, "Market case").

Topstep B3 position-limit sensitivity (MGC dropped on funded days at the 2-lot XFA tier). Setting (i): k* rises from
0.77-0.80 to 0.93-0.95, and x10K from 1.30 to 1.46-1.55. Setting (ii): mu*_QM falls from 0.94-0.98 to 0.87-0.90,
because dropping a zero-edge member removes its fees. Either way B3 stays worse than B2. No other basket meets a
binding limit at any firm (binding-limit log in E29_tables.md).

The account's daily SD at Topstep (USD, MLL 2,000) is 141 for B0. For the baskets at rho 0 / 0.75: B1 141 / 186,
B2 101 / 113, B3 119 / 167, B4 109 / 136. S / MLL is 0.05 to 0.09 throughout.

### 3.4 Answers

The lead adds one reading that the declaration did not fix and that is not a measurement: each member's per-trade
edge at the threshold, in units of its own sigma_1m (mu / sigma). In E.28's model, a member's alone break-even mixes
its fees with how well a one-lot of it clears each firm's payout rules. So "the same multiple of its own
break-even" can mean very different per-trade quality across members.

(a) Does any basket beat QM alone at realistic rho? Not in any sense that matters, and not in setting (ii).
- Setting (ii) (QM edge only, the others at zero): no basket beats B0 at any firm or any rho (0 of 80 cells).
- Setting (i) (every member at k times its own break-even): 27 of 76 runnable cells beat B0 by the section 7 rule.
  All 27 are at Topstep (B2, B3), Tradeify (B2, B3) or Bulenox (B1 at rho >= 0.25; B2, B3). The Topstep and
  Tradeify gains are large (k* 0.60 to 0.82 against 1.00), but every one of them contains MGC. MGC's alone
  break-even there is 6.37 and 6.34 ticks (about 1.2 sigma per trade). The reason is that a one-lot micro rarely
  clears the USD 150 winning-day threshold the payout rules need, not its fees (1.9 to 2.1 ticks). At k* = 0.60,
  B2 at Topstep therefore assigns MGC 3.82 ticks a trade (0.71 sigma) and QM 0.19 ticks (0.08 sigma). That is an
  artifact of the unit, not a benefit of combining. The basket wins because MGC is given a large edge that the
  combined account can finally collect. At Bulenox, B2 and B3 put MGC at 7.9 to 8.1 ticks (about 1.5 sigma).
- The one basket whose members carry similar per-trade edges at their own break-evens is B1 (QM 0.13 to 0.29
  sigma, ZM 0.18 to 0.34 sigma). It shows no benefit at Topstep, Lucid, Tradeify or MFFU (k* 0.98 to 1.02, against
  B0's 0.98 to 1.00), and a small one at Bulenox only at rho >= 0.25 (k* 0.98, 0.95, 0.93; the 0.98 is 2 steps
  from B0's 1.00, within seed noise, R_review item 9). B1 does lower the mu10K multiplier, by 7 to 17% at those
  four firms (for example Topstep 1.55 to 1.57 against 1.69, Tradeify 1.54 against 1.73, MFFU 2.13 to 2.29 against
  2.56) and by 1 to 3% at Bulenox.
- B4 (QM + MNQ): no benefit anywhere (k* 0.96 to 1.03, x10K higher than B0's at every firm where it runs). At
  Bulenox MNQ has no break-even within 12 ticks.

(b) At what rho does the benefit vanish? It does not vanish on the grid, because it never came from
diversification. The declaration's section 7 table, on the confirmed values (E29_confirmation.md), has no basket
whose flag turns off between rho 0 and 0.75: Topstep and Tradeify B2 and B3 and Bulenox B2 and B3 beat B0 at every
grid rho, Bulenox B1 starts to beat it at 0.25, and the other 50 basket-setting-firm lines never do (B4 at Bulenox
in setting (i) cannot be run). Across rho 0 to 0.75, setting (i) thresholds move by at most 0.05 at Topstep, Lucid, Tradeify
and MFFU. At Bulenox they move by up to 0.07, and they fall as rho rises: B1 goes from 1.00 at rho 0 to 0.93 at
0.75, and in setting (ii) from 1.58 to 1.47 ticks (B3 from 2.11 to 1.94). A higher rho means a higher daily SD, and in this funnel (fixed fees,
capped payouts, a trailing drawdown) extra variance near zero edge pays, as E.19 found. The account's SD is 5 to
9% of the 2,000 loss limit at every rho, so variance reduction from low correlation buys almost nothing at the
break-even. Where the measured price correlations sit (returns 0 to 0.16, ranges up to 0.40), the answer is the
same as at any other grid rho.

(c) Does adding a zero-edge contract ever help? No. In setting (ii), every basket raises QM's break-even at every
firm and rho: by +0.08 ticks (Lucid B4) up to +1.39 ticks (Bulenox B3 at rho 0). The mu10K analogue rises in every
cell too. Why: QM's 20 trades become 10 (or 7), and each zero-edge member pays its own fees on the rest, so QM must
earn the lost trades' edge and the other member's costs on fewer trades. The extra variance does not make up for it
at break-even, not even at Bulenox, where it narrows the gap as rho rises. This is the expected sign. The only
place a zero-edge member's removal "helps" is the Topstep B3 sensitivity: there MGC is dropped and its fees go with
it.

### 3.5 The ranking these results would imply (conditional)

- The firm order of E.28's v2 ranking stands: Topstep QM, MFFU QM, Tradeify QM, Bulenox QM, Lucid QM. At every
  firm, B0 (QM alone) has the lowest QM break-even of any option when only QM has an edge (setting ii). That is the
  only setting a QM-only pilot can speak to.
- Conditional on a second contract having its own measured edge: the case for a basket rests on that edge, not on
  correlation. At Topstep and Tradeify, QM + MGC (B2) would come first if MGC carried an edge near 0.7 sigma per
  trade, an edge no short-hold strategy is known to have. With equal per-trade quality across members, QM + ZM
  (B1) is the only basket worth a look. It changes no break-even except at Bulenox (0.02 to 0.07 lower from rho
  0.25) and lowers the mu10K multiplier by 7 to 17% at the other four firms. QM + MNQ (B4) never helps.
- Implied order of options at the rank-1 firm (Topstep), conditional on edges at each member's own break-even
  multiple: B2 (k* 0.60 to 0.61), B3 (0.77 to 0.80), then B1 and B0 level on break-even (1.00 to 1.02 against
  1.00; B1 has the lower mu10K multiplier, 1.55 to 1.57 against 1.69), then B4 (0.98 to 1.03, but mu10K 2.01 to
  2.04). Under a QM-only edge (setting ii, rho 0): B0 (mu*_QM 0.32), then B4 (0.45), B2 (0.49), B1 (0.79), B3
  (0.94).

## 4. Delegation record

Three worker spawns, all on Opus 5.5 (Fable is not on the Pro plan); at most two ran at once. Times are PDT from
the transcripts and log files; tokens are each transcript's usage sums (input + output + cache read + cache
creation), from reports/stage_e10_briefs/cost.py.

| step | owner | agent file / model / effort | start to end | tokens | status |
|---|---|---|---|---|---|
| Plan, briefs (coder, correlations, review), Z3 declaration | lead | - / Opus 5.5 / high | 10-21 19:19 to 19:26 (declaration mtime 19:24:16) | in lead total | done |
| Measured correlations (reference) | CorrMeasurer-OpusHigh | worker-high / opus / high | 19:25:55 to 19:28:58 | 1,514,154 | done: E29_correlations.md/.json |
| Basket module, runner, tests, tables script | BasketCoder-OpusXHigh | worker-xhigh / opus / xhigh | 19:25:51 to 19:37:04; resumed by SendMessage 21:54:37 to 22:02:15 (last record 22:12:15) | 8,094,423 | partial: cut twice by usage limits. On disk: e29_basket.py, e29_run.py, e29_tables.py, 9 tests passing (21:57), LOG.md C1 to C9 |
| Grid run, first launch (coder) | detached, 6 processes, nice 10 | - | 21:59:32 to 22:21 (killed by reboot at 139 records) | - | resumed below |
| Grid run, restart (OC-12) | lead, one detached command | - | 10-22 02:41 to 02:51:55 (rc 0; 96 run, 139 kept) | - | done: 228 cells + 7 alone, 0 missing |
| Collect, tables, final tests | lead | - | 02:51 to 02:53 | - | done: E29_cells.json, E29_tables.md, 11 passed |
| Independent review (Z5) | BasketReviewer-OpusXHigh | worker-xhigh / opus / xhigh, fresh context | 02:53:26 to 03:13:06 | 8,589,743 | done: R_review.md, GO WITH FIXES |
| Synthesis drafts (answers, compact tables, OC, decisions) | lead | - / Opus 5.5 / high | 02:54 to 03:15 | in lead total | done |
| Grid confirmation of the other 211 records (SHOULD FIX 7) | lead, one detached command, 6 processes (OC-17) | - | 03:13 to 04:19 (rc 0) | - | done: 0 of 470 moved |
| Vanish table (SHOULD FIX 8), return, end checks, suite, commit | lead | - / Opus 5.5 / high | 04:19 to end (section 8) | in lead total | done |

The lead kept the declaration, the reading of the results (sections 3.3 to 3.5), the open choices and the decisions
for itself. The grid restart and the confirmation pass were single mechanical commands. The lead ran them itself
instead of spawning a worker (25k to 35k tokens of setup each), and the coder was still blocked by the usage limit
at the time of the restart.

## 5. Verification

Independent review (Z5): BasketReviewer-OpusXHigh, Opus 5.5 at xhigh in a fresh context (Fable is not on the Pro
plan, OC-2), 02:53 to 03:13 on 10-22, reports/stage_e29_briefs/R_review.md. Verdict GO WITH FIXES: 0 BLOCKING,
2 SHOULD FIX, 10 NOTEs. Both SHOULD FIX items were fixed before this return.

The prompt's checks:
- B0 against E.28 (review item 2): B0 setting (ii), limit and market, recomputed at all five firms. Every value
  equals A3_econ.json exactly (mu*_lim / mu*_mkt / mu10K / cost per attempt): Topstep 0.32 / 1.32 / 0.54 / 50.53,
  Lucid 0.33 / 1.33 / 0.77 / 120.87, Tradeify 0.43 / 1.43 / 0.75 / 95.83, MFFU 0.35 / 1.35 / 0.90 / 153.00,
  Bulenox 0.72 / 1.72 / 1.06 / 175.00. Every evaluation row is bit-equal to the stored cell. Test (a) checks the
  same thing and passes.
- Two random cells under a different seed (item 3): a seeded draw over the 156 computed non-B0 limit cells picked
  Bulenox B3 (ii) at rho 0.25 and 0.75. They were rerun with master seed 20261022 instead of 20261021, so every draw
  was new. mu*_QM moved from 2.05 to 2.04 and from 1.94 to 1.93; mu10K from 2.98 to 2.98 and from 3.02 to 3.01.
  Every change is at most 1 step, against a bar of 3, and no beats flag changed. B0 Bulenox (ii) under the new seed
  reproduces 0.72 / 1.06.
- Rule mapping on the combined account (item 4): pass. The combined law enters E.28's funnel through the same call
  as E.28's pair law, so every mapped rule acts on the combined account.
- Tables against JSON (item 6): 994 numbers in the main tables and 1,494 in the reporting tables, 0 mismatches. All
  160 beats flags were re-derived on integer grid indices: 0 mismatches, 27 yes.
- Tests (item 5): 11 passed (work/basket/test_e29_basket_final.out, 66 s), rerun by the reviewer.

The SHOULD FIX items:
- Item 7, grid confirmation (A3_econ.md 2.4) not run: fixed. The reviewer confirmed 21 cells and 3 alone records.
  The lead confirmed the other 211 records with the reviewer's code (work/confirm/confirm_all.py calls
  review_run._work; same code, seed and draws; 03:13 to 04:19, rc 0, no traceback). Result: 235 of 235 records,
  470 thresholds, 0 moved (stage_e29_briefs/E29_confirmation.md).
- Item 8, no vanish rho produced: fixed. E29_confirmation.md section 7 gives, for each firm, basket and setting, the
  beats flag at each grid rho on confirmed values and the rho where it turns off; section 3.4(b) cites it.

NOTEs carried into the text:
- Item 9: flags that rest on exactly 2 steps (Bulenox B1 (i) at rho 0.25, Bulenox B3 (i) at rho 0) are within
  seed noise; 3.4(a) says so.
- Item 10: Topstep B3 sits at the 2-lot tier on 94 to 96% of funded days near the threshold. The drop-MGC
  sensitivity is in 3.3, and it does not change B3's flag.
- Item 11: Lucid's B0 setting-(i) k* is 0.98 on the k lattice, and Lucid's flags are judged against it.
- Item 12: cell_id omits the mode. The confirmation pass wrote only to work/review/out and work/confirm/out, never
  to work/basket/cells.

Lead checks:
- The 27 yes flags in the vanish table equal the 27 starred cells in 3.3.
- Every number in 3.3 to 3.5 was checked against compact_tables.md, which compact.py generates from
  E29_cells.json. The check corrected four statements in the lead's draft: B1's mu10K drop is 7 to 17% (not 8 to
  17%) at four firms and 1 to 3% (not 1 to 4%) at Bulenox, and two places said "top four firms" where "all firms
  but Bulenox" was meant.

Not checked by anyone: the correlations in 3.2 (reference only, not an input), and the lead's per-trade sigma
reading in 3.4 (OC-14). The reviewer checked MGC's 6.37-tick alone break-even only for consistency with E.28's
model.

## 6. Open choices

- OC-1 E.28b had not finished at launch (no E.28 return or commit; its key-watch shell was still polling). E.29
  went ahead because it is simulation-only and touches no acct-3 or pilot file. E.29's code imports E.28's A3 files
  read-only. During the pause, E.28 was committed (60eb6b6, "Stage E.28 methods brief, ranking and pilot"), and
  the imported files are now tracked with unchanged sha256 (A3_funnel.py 9b0183b5..., A3_models.py f9389bf8...,
  A3_econ.json 6140c7d6...). V47 (QM research, pilot on hold) and the E.30 prompt (54f07ab) also arrived during
  the pause. The prompt binds V20 to V46; V47 is used only in section 7.
- OC-2 Fable is not available on Pro. The independent review was done by BasketReviewer-OpusXHigh in a fresh
  context (V46 item 5), not by Fable.
- OC-3 The correlation window is E.28's standard window, 2022-11-01 to 2023-10-31, rather than everything before
  2024-03-01. This keeps E.28's pilot window untouched.
- OC-4 The position limit form (declaration section 4): only Topstep B3 (2.1 lots) meets a binding limit, the
  2-lot first XFA tier. The primary form is no-overlap scheduling, which leaves P&L unchanged in this model. The
  sensitivity drops MGC on those days.
- OC-5 Members whose E.28 break-even is "> 4" had their alone break-evens recomputed on a 0 to 12 tick grid. The
  coder also extended MNQ's market case at Topstep and Tradeify (coder choice C7).
- OC-6 The best-basket rule is the lowest setting-(i) k* at rho 0.5, with "> 4" and "n/a" counted as infinity
  (coder choice C8). The market case was run at every rho for the best basket (coder choice C6).
- OC-7 The reporting points are k = 1.0, 1.5 and 2.0 in setting (i), and mu_QM = B0's mu*_lim, 0.50 and 1.00 in
  setting (ii).
- OC-8 The trade split is floor(20 / n), with the remainder going to members in basket order. That gives B3 7/7/6.
- OC-9 The E.29 tests live in reports/stage_e29_briefs/work/basket/test_e29_basket.py, outside tests/: the repo
  suite's testpaths is tests, and the tests depend on E.28's untracked files.
- OC-10 The main run skipped grid confirmation (A3_econ.md 2.4); the coder logged every threshold as "bisection,
  unconfirmed" (coder choice C3), because the usage-limit cuts and two reboots took the stage's time. The reviewer
  confirmed a sample, and the lead then confirmed every remaining record in a separate pass (work/confirm/,
  03:13 to 04:19, same code, seed and draws). It moved 0 of 470 thresholds. The labels in E29_cells.json and
  E29_tables.md were left as generated; a dated lead note at the head of E29_tables.md points to
  E29_confirmation.md.
- OC-11 Time. Work was interrupted twice by usage limits (about 19:38 to 21:54, and about 22:05 to 02:40) and by
  two reboots (20:42 and 22:21). The prompt's 23:00 stop fell inside the second pause. At 02:41 on 10-22 the user
  said to continue, so the stage finished on 10-22.
- OC-12 After the second reboot, the lead restarted the resumable grid run itself (one detached command) instead
  of through a worker. It is a mechanical step, and the coder was still blocked by the usage limit.
- OC-13 The realistic rho band (0 to 0.25 for a direction-neutral strategy's daily P&L) is the lead's judgment from
  price correlations. It was not measured.
- OC-14 The per-trade edge in sigma units used in section 3.4 is the lead's interpretation, added after the results.
  It is not in the declaration, and no number in the tables depends on it.
- OC-15 The coder's other choices were accepted as logged in work/basket/LOG.md: C1 evaluations cached by (M, S);
  C2 E.28's operation order; C4 P10K is computed only in limit cells; C5 pass rate = E.28's p_pass_attempt; C9 the
  2-lot tier set by E.19's tier_cap_vec on the previous close.
- OC-16 The declaration's header says it was written "about 19:40 PDT". That was the lead's clock estimate. The
  file mtime (19:24:16) governs, and the text was not changed after its hash. STATE's CorrMeasurer times
  (19:28 to 19:29) were lead entries too; its transcript shows 19:25:55 to 19:28:58. Section 4 uses transcript times.
- OC-17 The prompt's "at most 4 workers at once" was read as agents; at most two ran at once. Compute processes
  followed CLAUDE.md's compute limits (at most half the 20 logical CPUs, nice 10): the confirmation pass used 6
  processes. Its memory peak was not recorded.
- OC-18 The lead did not print the initial ETA table in chat before the first spawn (CLAUDE.md asks for one). The
  final table in section 8 is therefore set against the prompt's own schedule (start 19:19, return by 23:30 on
  10-21) instead.

## 7. Decisions for the user

- D1. Keep the pilot and any first evaluation on QM alone. Recommendation: yes. With a QM-only edge, every basket
  raises QM's break-even at every firm and rho (setting ii, 0 of 80 cells better). A second contract belongs in the
  account only after its own edge is measured, and that is a separate pilot with its own spend.
- D2. If Stage E.30 fails QM (median daily volume below 1,000, V47 item 3), the basket question loses its anchor:
  every E.29 basket holds QM, and QM's sigma and range come from CL (E.28 OC-1). Recommendation: then rerun the E.29
  model with ZM as the anchor (B0' ZM alone, ZM + MGC, ZM + MNQ). This needs a new basket table (the module's BASKETS
  constant, e29_basket.py:77, fixes QM as the first member) and a new declaration. The run is about one hour of
  compute with no data read. Until E.30 reports, do nothing.
- D3. Whether to re-express setting (i) in per-trade sigma units (equal mu / sigma across members) in a later
  stage. Recommendation: not now. It answers a question only a measured second-contract edge can make relevant, and
  section 3.4 already shows the direction: with equal per-trade quality, B1 is the only candidate, and it moves the
  break-even only at Bulenox (by 0.02 to 0.07, from rho 0.25).
- D4. Whether MGC's high alone break-even (6.3 to 8.3 ticks at Topstep, Tradeify and Bulenox) changes E.28's L2 scores
  for micro contracts. Recommendation: no change. E.28 already scores those pairs on that break-even. E.29 only shows
  that the cause is the payout thresholds a one-lot micro cannot clear, not fees.

## 8. Session cost

Tokens come from the transcripts, each message at its final usage, counted by reports/stage_e26_briefs/cost.py over
session 488b039c from 2026-10-22T02:19:00Z (19:19 PDT on 10-21) to 11:41:40Z (04:41:40 PDT on 10-22). Output:
reports/stage_e29_briefs/work/lead/cost_raw.txt. The few calls after that (assembly, progress entry, commit and the
closing reply) are not counted. These are token counts, never estimates; plan-meter percentages are the user's
reading.

Wall clock: 10-21 19:19 to 10-22 04:41 = 9 h 22 min. Two pauses are not work: 19:37 to 21:53 (usage limit, reboot
at 20:42; 2 h 16 min) and 22:18 to 02:41 (usage limit, reboot at 22:21; 4 h 23 min). Work: 19:19 to 19:37,
21:53 to 22:18 and 02:41 to 04:41, 2 h 43 min in total.

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---:|---:|---:|---:|---:|
| claude-opus-5-5 | 526 | 342,679 | 40,635,492 | 1,752,157 | 42,730,854 |

Per spawn:
- CorrMeasurer-OpusHigh: worker-high, opus, high: 1,514,154 (in 34, out 18,754, cache read 1,398,076, cache
  creation 97,290).
- BasketCoder-OpusXHigh: worker-xhigh, opus, xhigh: 8,094,423 (in 92, out 102,245, cache read 7,526,829, cache
  creation 465,257); two parts, both cut by the usage limit.
- BasketReviewer-OpusXHigh: worker-xhigh, opus, xhigh: 8,589,743 (in 108, out 71,931, cache read 8,047,727, cache
  creation 469,977).
- Lead (Opus 5.5, high): 24,532,534 (in 292, out 149,749, cache read 23,662,860, cache creation 719,633).

Delegation share: lead 24,532,534 (57.4%), workers 18,198,320 (42.6%). By model tier, 100% Opus 5.5: Fable is not
on the Pro plan, and no Sonnet or Haiku work was routed. Cache reads are 95.1% of all tokens.

Final ETA table (actuals). No initial estimate table was printed (OC-18). The baseline is the prompt's schedule,
19:19 to the 23:30 return, 4 h 11 min.

| # | Task | Owner | Model | Effort | Start | End | Time | Tokens | Status, deviations |
|---|---|---|---|---|---|---|---|---:|---|
| 1 | Start checks | lead | opus | high | 19:19 | 19:20 | 1 min | lead | done |
| 2 | Plan, three briefs, Z3 declaration | lead | opus | high | 19:20 | 19:26 | 6 min | lead | done; declaration mtime 19:24:16 (OC-16) |
| 3 | Reference correlations | CorrMeasurer-OpusHigh | opus | high | 19:25:55 | 19:28:58 | 3 min | 1,514,154 | done |
| 4 | Basket module and runner, part 1 | BasketCoder-OpusXHigh | opus | xhigh | 19:25:51 | 19:37:04 | 11 min | 8,094,423 (both parts) | cut by the usage limit; no tests, no cells |
| P1 | **usage-limit pause; reboot 20:42** | | | | 19:37 | 21:53 | 2 h 16 min | | excluded |
| 5 | Coder resumed (reduced scope): tests, grid launch | BasketCoder-OpusXHigh | opus | xhigh | 21:54:37 | 22:02:15 | 8 min | (in 4) | cut again; 9 tests pass; grid launched 21:59:32 |
| 6 | Return skeleton; lead waits on the grid | lead | opus | high | 21:53 | 22:18 | 25 min | lead | done |
| P2 | **usage-limit pause; reboot 22:21 killed the grid at 139 records** | | | | 22:18 | 02:41 | 4 h 23 min | | excluded |
| 7 | Grid run restart (OC-12) | lead, detached | | | 02:41 | 02:51:55 | 11 min | lead | rc 0; 96 run, 139 kept |
| 8 | Collect, tables, final tests | lead | opus | high | 02:51 | 02:53 | 2 min | lead | 11 passed |
| 9 | Independent review (Z5) | BasketReviewer-OpusXHigh | opus | xhigh | 02:53:26 | 03:13:06 | 20 min | 8,589,743 | GO WITH FIXES, 0 BLOCKING |
| 10 | Synthesis drafts | lead | opus | high | 02:54 | 03:15 | 21 min | lead | done, alongside 9 |
| 11 | Grid confirmation of 211 records (SHOULD FIX 7) | lead, detached, 6 processes | | | 03:13 | 04:19 | 66 min | lead | rc 0; 0 of 470 moved |
| 12 | Vanish table (SHOULD FIX 8), text checks, return sections | lead | opus | high | 04:19 | 04:30 | 11 min | lead | four statements corrected |
| 13 | Full suite | lead, detached | | | 04:20:58 | 04:41:00 | 20 min | lead | 1 known failure, 8,090 passed |
| 14 | End checks, cost, assembly, progress, STAGES, commit | lead | opus | high | 04:41 | commit | | lead (to 04:41:40) | done |
| | **Cumulative** | | | | 19:19 | 04:41 | work 2 h 43 min (pauses 6 h 39 min excluded) | **42,730,854** (lead 24,532,534; workers 18,198,320) | baseline 4 h 11 min to the 23:30 return; the calendar end moved to 10-22 through the pauses (OC-11) |
