# Stage E.21 verdict verification (VerdictVerifier-FableXHigh, Step 5)

Verifier: Fable 5.1 (claude-fable-5-1), effort xhigh, independent of the code's author (Opus) and
of the lead. Window of work: 2026-10-14 04:15-04:40 PDT. Brief:
reports/stage_e21_briefs/brief_verdict_verify.md. Scripts and outputs (never under reports/):
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/13fe2d4e-086f-4929-8325-9ef707bdf0cf/scratchpad/VerdictVerifier/
(vv_compute.py, vv_stats.py, vv_compare.py, vv_splice_diag.py, vv_tables.py; vv_series.json,
vv_per_root.json, vv_stats.json, vv_compare.json, vv_splice_diag.json; the first pass's non-surviving
outputs kept as *_v1_buggy_restart.json).

## Verdict line

**VERIFIED WITH NOTES.** Every verdict number of all four tests and all three cost cases (152
numbers: n, mean, sd, t, Newey-West t, p_t, p_nw, p, annualized Sharpe, bootstrap interval, Holm,
the Sharpe bar, PASS) matches my independent recomputation within 1e-9 relative; every daily
series matches the run date by date with zero difference (T1, T2, T3, T4, all cases); all 17 roots
match on net contribution, fill count, gross and costs in T1 and T2; T3's 227 units match. The
verdicts stand: **T1 FAIL, T2 FAIL, T3 FAIL, T4 FAIL** (Holm rejects nothing: the smallest p is
T1's 0.0419 against 0.025/4 = 0.00625; T1 and T2 clear the Sharpe bar 0.3 with 0.498 and 0.436,
T3 and T4 do not with 0.146 and 0.117). No look-ahead, mis-specification or missing cost found.
BLOCKING 0, SHOULD FIX 0, NOTE 5 (VV-1 to VV-5).

Per-test status: T1 MATCH (all cases, CI, verdict); T2 MATCH; T3 MATCH; T4 MATCH.

## Base-case numbers (run = verifier)

| Test | n | mean | sd | t | t_NW (lags) | p_t | p_NW | p = max | Sharpe | 95% CI | Holm | Sharpe >= 0.3 | PASS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | 3205 | 3.2871e-4 | 0.0104765 | 1.7763 | 1.7290 (21) | 0.03789 | 0.04191 | 0.04191 | 0.4981 | [-0.0634, 1.0533] | no | yes | FAIL |
| T2 | 3205 | 2.2429e-4 | 0.0081574 | 1.5566 | 1.5246 (21) | 0.05984 | 0.06368 | 0.06368 | 0.4365 | [-0.1092, 0.9818] | no | yes | FAIL |
| T3 | 3319 | 1.0156e-4 | 0.0110445 | 0.5298 | 0.5234 (5) | 0.2982 | 0.3003 | 0.3003 | 0.1460 | [-0.3993, 0.7065] | no | no | FAIL |
| T4 | 3331 | 0.0558588 | 7.58019 | 0.4253 | 0.4303 (21) | 0.3353 | 0.3335 | 0.3353 | 0.1170 | [-0.3688, 0.5998] | no | no | FAIL |

Totals (base): T1 gross 1.13519, costs 0.08168 (7.19% of gross), net 1.05352; T2 gross 0.79731,
costs 0.07847 (9.84%), net 0.71884; T3 gross 0.42792, costs 0.09083 (21.23%), net 0.33708. Fills:
T1 and T2 2121 rebalance-type fills each (my split, T1: 45 entries, 1825 rebalances, 206 flips, 45
exits; T2: 45 / 1393 / 638 / 45) plus 980 roll_out and 980 roll_in each; T3 227 entries, 227 exits.

## Order of events (from file times, git and the ledger, not estimates)

| Event | Time (PDT) | Evidence |
|---|---|---|
| Freeze commit 839efc9 "E.21 freeze" | 04:12:01 | git log; reports/stage_e21_freeze.json sha256 0bb899e5...bb1e |
| Registration r006-E21 (E21; E21-T1..T4; freeze sha 0bb899e5...; harness ece91ae8...; N 528 -> 532) | 04:12:12 | ledger/trial_registrations.jsonl line 7, time_local; ledger sha256 085ed33c...4831 (7 lines) |
| Run-once marker written (O_EXCL), started_local | 04:12:28 | reports/stage_e21_RUN_ONCE.json (mtime 04:12:28.69); its registry sha256 equals the ledger's |
| Results T1..T4_result.json, per_root/*.json, verdict.json, summary.md | 04:14:34-04:14:35 | mtimes; verdict.json written_local 04:14:35, n_trials_at_verdict 532, registration r006-E21 |
| Freeze manifest verify (`multiday.freeze_manifest verify --sha256 0bb899...`) | 04:21 (this check) | "freeze verified: 18 inputs", rc 0 |
| T4's H2 input | - | reports/stage_e17_runs/H2_result.json sha256 a661cebc...2dff equals the pin |
| My numbers written before any result file was opened | 04:26:59 (first pass), 04:32:25 (corrected) | vv_stats_v1_buggy_restart.json; the run's files were first opened at 04:27 by vv_compare.py |

Order holds: commit < registration < marker < every result mtime < this verification. N = 532.

## Findings

| Id | Severity | Detail | Fix |
|---|---|---|---|
| VV-1 | NOTE | The lead's extra item, the 171 "no signal (lookback: missing bar)" root-months. Cause, found on the real bars (vv_splice_diag.json): the stores' roll metadata records TWO roll instants on consecutive weekend days with no usable bar between them (a Saturday and the following Sunday at the session open, 19:00 CT, or 18:00 CT in winter). At the first instant chained_return moves the chain's start to Sunday's first bar; at the second, last_before() is still Friday's last bar, so i_out < start_i and the function returns "missing bar". Every 12-month lookback (and, for T2, every 1- and 3-month lookback) spanning such a pair is undefined, hence runs of about 12 flat months. In-window pairs and failed 12-month lookbacks: ZC 7 pairs (2011-07-02/03, 2013-06-01/02, 2013-06-29/30, 2018-04-21/22, 2018-07-07/08, 2020-06-27/28, 2022-06-25/26), 62 failures; ZL 3 (2013-06-29/30, 2017-07-01/02, 2019-06-29/30), 35; ZS 3 (2014-06-21/22, 2015-02-21/22, 2020-06-27/28), 31; LE 5 (2017-01-21/22, 2020-03-14/15, 2020-05-16/17 in window; two more in 2010 and 2014 before LE's window), 26; HE 2 in window (2018-11-17/18, 2019-06-15/16; 80 more before 2017-07 where the store has no bars), 19. The same pairs produce the run's 17 "return undefined: missing bar" daily returns and its 12 "hold excluded: contract change" plus 1 "missing roll bar (fill guard)" (a position held across the pair: the second instant's old leg is Friday's bar, whose contract is no longer the held one). My own chain, written from the spec, reproduces all 171 T1 and T2 missing signals, the 17 returns and the 13 hold exclusions, so the positions are identical. Classification: (a) the frozen rule applied as specified on a real data feature. The spec (section 1) defines the lookback AS base_rules.h2.chained_return and A1 states that a None return makes the lookback undefined and counted; nothing is chosen from data and no look-ahead arises. Consequence for the reader: grains and livestock carry no T1/T2 position in those months (ZC about 62 of its 152 signal months), a loss of exposure, not a bias. | None in this stage (no rule change after bars are read). For a later stage, a lead decision: have the store builder collapse consecutive roll instants with no bar between them, or let chained_return treat an empty segment as a no-op; either changes positions and needs a new freeze. |
| VV-2 | NOTE | Wording in multiday/README.md coder choice 5 ("the order that opened the hold gets target 0"). Read literally as the entry that opened the non-flat streak, a failed roll would cascade backwards and zero every month before it (my first pass did exactly this and lost ZC, ZL, ZS, HE, LE: 17 fills on ZC instead of 153). The code (book.py; FR-2: "hold exclusions are now keyed by the order's date") zeroes the order IN FORCE at the failed interval, one month, which is the reading that "mirrors base_rules' unit exclusion" and the one I verified against. | Reword the README line to "the order in force at the failed interval"; no code change. |
| VV-3 | NOTE | Fills by kind: the run labels every non-roll fill "rebalance" (2121 in T1 and T2); my split (entry 45, rebalance 1825/1393, flip 206/638, exit 45) sums to the same 2121, and the roll legs match (980 + 980). Reporting only. | None. |
| VV-4 | NOTE | T3 exclusions: the run counts "window end" 2 (NQ and RTY February 2024, whose day +3 falls in March 2024); my code skips those units silently. Traded units agree (NQ 154, RTY 73, 227 in all) and match the prereg's calendar-only counts. Reporting only. | None. |
| VV-5 | NOTE | T1/T2 exclusion conventions differ in how months before a root's window are counted (the run: "no signal (no reference (outside window))" 60 and "(no trade date)" 143; mine: "no eligible rebalance date" for those months). No position is affected (all 17 roots match fill for fill). Reporting only. | None. |

## Checks run

1. Rules read in the brief's order (STAGE_E.21.md F1-F8, the prereg, lead_spec sections 0-11, A, B;
   E.16 lead_spec 0-3 and 5; base_rules/README.md; multiday/README.md for file names and formats).
2. Independent computation (vv_compute.py, written from the spec; only the frozen loaders reused:
   context_from_freeze, load_manifest, load_product, settle_point, action_exclusion,
   reference_exclusion, VehicleCost.fill_costs, ReleaseRules.event/guard): for all 17 roots the marks
   MK and PS, the same-contract chained daily returns, the EWMA sigma (com 60, 261, EWMA-mean
   demeaning, strictly before d, 60-return warm-up), rebalance dates (last 6 trade dates, action
   exclusions, MK and PS present, fill guard at the MK bar's open), references (last 6 of month M-k,
   reference exclusions), lookbacks with the store-boundary virtual splice, signs, the calendar-defined
   S_M (13 from 2011-07, 14 from 2015-12, 15 from 2017-01, 17 from 2018-07), holdings n = w/(S_M V),
   fills with per-case costs, roll legs at every splice with guard moves, hold exclusions, the flat
   months 2019-04 and 2024-02, per-root daily values and the T1/T2 series on the calendar-defined
   dates. T3 on NYSE-closure-free equity days (closures by rule, A12), day -2 and day +3, exclusions,
   S_u, entry/exit fills. T4 from my T2 and T3 and H2's pinned component (trailing 60 grid dates,
   ddof 1, warm-up 60; grid 3391 dates, series 3331). Run at nice 10, one root at a time, peak RSS
   1.27 GB (probe), about 3.5 minutes per pass.
3. Statistics (vv_stats.py, own code): t, Bartlett Newey-West (21/21/5/21), p_t (Student, n-1),
   p_nw (normal), p = max, Sharpe x sqrt(252), circular block bootstrap (block 21, 10,000 draws,
   default_rng(20261014) fresh per test, nanpercentile 2.5/97.5), Holm at 0.025 over the four base p.
   The bootstrap intervals match the run's to 1e-15, so the draw procedure is the same.
4. Comparison (vv_compare.py): 152 numbers, 12 series (4 tests x 3 cases) date by date, totals and
   fills by kind, per-root rows for T1 and T2: all MATCH; tables below.
5. The lead's extra item (vv_splice_diag.py): both chained_return and my chain run on every
   12-month lookback of ZC, ZL, ZS, LE, HE; the breaking splice identified for each failure; VV-1.
6. Order of events, freeze verify, H2 pin, N = 532: the table above.
7. Non-survivor of my own work: my first pass (04:26:59) zeroed the hold's first entry order on a
   failed roll (VV-2's literal reading) and differed from the run on ZC, ZL, ZS, HE, LE only (T1
   t 1.862 vs 1.776; T2 1.717 vs 1.557; T3 and 12 roots already identical). The per-root comparison
   located the cause in my restart logic; after the one-line fix (zero the order in force) every
   number matches. Both passes are kept on disk. The fix was made after the comparison, so the
   final match is a check against the run's reading of coder choice 5, which I judge correct
   (VV-2); T3, T4's arithmetic, the statistics, costs, sigma, signals, dates and 12 of 17 roots
   were matched blind.

Not checked (outside the brief or no time): F8's economics; the DSR descriptive block in
verdict.json (not a verdict input); the limit-lock and high == low diagnostics (14 and 454
flagged, counted only); the per-year tables beyond what identical daily series imply; the stress
and slip150 per-root rows (base rows checked, and the series match in all cases).

## Comparison tables (run vs verifier; MATCH = within 1e-9 relative or 1e-12 absolute)

### T1

| case | number | run | verifier | abs diff | status |
|---|---|---|---|---|---|
| base | n | 3205 | 3205 | 0 | MATCH |
| base | mean | 0.0003287099022 | 0.0003287099022 | 5.421010862e-19 | MATCH |
| base | sd | 0.01047650909 | 0.01047650909 | 6.938893904e-18 | MATCH |
| base | t | 1.776275027 | 1.776275027 | 1.554312234e-15 | MATCH |
| base | t_nw | 1.728975118 | 1.728975118 | 1.554312234e-15 | MATCH |
| base | p_t | 0.03789123702 | 0.03789123702 | 1.249000903e-16 | MATCH |
| base | p_nw | 0.04190677424 | 0.04190677424 | 1.387778781e-16 | MATCH |
| base | p | 0.04190677424 | 0.04190677424 | 1.387778781e-16 | MATCH |
| base | sharpe_annualized | 0.4980769724 | 0.4980769724 | 5.551115123e-16 | MATCH |
| stress | n | 3205 | 3205 | 0 | MATCH |
| stress | mean | 0.0002987260686 | 0.0002987260686 | 4.878909776e-19 | MATCH |
| stress | sd | 0.01047751947 | 0.01047751947 | 6.938893904e-18 | MATCH |
| stress | t | 1.614093408 | 1.614093408 | 1.33226763e-15 | MATCH |
| stress | t_nw | 1.569563014 | 1.569563014 | 1.33226763e-15 | MATCH |
| stress | p_t | 0.05330281896 | 0.05330281896 | 1.387778781e-16 | MATCH |
| stress | p_nw | 0.05825840444 | 0.05825840444 | 1.45716772e-16 | MATCH |
| stress | p | 0.05825840444 | 0.05825840444 | 1.45716772e-16 | MATCH |
| stress | sharpe_annualized | 0.4526003831 | 0.4526003831 | 4.440892099e-16 | MATCH |
| slip150 | n | 3205 | 3205 | 0 | MATCH |
| slip150 | mean | 0.0003194934202 | 0.0003194934202 | 4.33680869e-19 | MATCH |
| slip150 | sd | 0.01047667094 | 0.01047667094 | 6.938893904e-18 | MATCH |
| slip150 | t | 1.726444541 | 1.726444541 | 1.33226763e-15 | MATCH |
| slip150 | t_nw | 1.680054209 | 1.680054209 | 1.110223025e-15 | MATCH |
| slip150 | p_t | 0.04218193213 | 0.04218193213 | 1.110223025e-16 | MATCH |
| slip150 | p_nw | 0.04647338454 | 0.04647338454 | 1.179611964e-16 | MATCH |
| slip150 | p | 0.04647338454 | 0.04647338454 | 1.179611964e-16 | MATCH |
| slip150 | sharpe_annualized | 0.4841042388 | 0.4841042388 | 3.885780586e-16 | MATCH |
| base | ci95_lo | -0.06335873911 | -0.06335873911 | 2.91433544e-16 | MATCH |
| base | ci95_hi | 1.053315692 | 1.053315692 | 6.661338148e-16 | MATCH |
| base | ci_undefined_draws | 0 | 0 | - | MATCH |
| base | holm_rejects | False | False | - | MATCH |
| base | sharpe_at_least_bar | True | True | - | MATCH |
| base | pass | False | False | - | MATCH |
| base | verdict.p | 0.04190677424 | 0.04190677424 | - | MATCH |
| base | verdict.t | 1.776275027 | 1.776275027 | - | MATCH |
| base | verdict.n | 3205 | 3205 | - | MATCH |
| base | verdict.mean | 0.0003287099022 | 0.0003287099022 | - | MATCH |
| base | verdict.sharpe_annualized | 0.4980769724 | 0.4980769724 | - | MATCH |

### T2

| case | number | run | verifier | abs diff | status |
|---|---|---|---|---|---|
| base | n | 3205 | 3205 | 0 | MATCH |
| base | mean | 0.0002242878504 | 0.0002242878504 | 3.794707604e-19 | MATCH |
| base | sd | 0.008157429805 | 0.008157429805 | 5.204170428e-18 | MATCH |
| base | t | 1.556561986 | 1.556561986 | 1.776356839e-15 | MATCH |
| base | t_nw | 1.524565936 | 1.524565936 | 1.110223025e-15 | MATCH |
| base | p_t | 0.05983663977 | 0.05983663977 | 2.081668171e-16 | MATCH |
| base | p_nw | 0.0636836996 | 0.0636836996 | 1.665334537e-16 | MATCH |
| base | p | 0.0636836996 | 0.0636836996 | 1.665334537e-16 | MATCH |
| base | sharpe_annualized | 0.4364682663 | 0.4364682663 | 4.440892099e-16 | MATCH |
| stress | n | 3205 | 3205 | 0 | MATCH |
| stress | mean | 0.0001942792807 | 0.0001942792807 | 3.794707604e-19 | MATCH |
| stress | sd | 0.008158774897 | 0.008158774897 | 6.938893904e-18 | MATCH |
| stress | t | 1.34807965 | 1.34807965 | 1.554312234e-15 | MATCH |
| stress | t_nw | 1.31922454 | 1.31922454 | 1.776356839e-15 | MATCH |
| stress | p_t | 0.08886403138 | 0.08886403138 | 2.359223927e-16 | MATCH |
| stress | p_nw | 0.09354702827 | 0.09354702827 | 2.91433544e-16 | MATCH |
| stress | p | 0.09354702827 | 0.09354702827 | 2.91433544e-16 | MATCH |
| stress | sharpe_annualized | 0.3780087095 | 0.3780087095 | 4.440892099e-16 | MATCH |
| slip150 | n | 3205 | 3205 | 0 | MATCH |
| slip150 | mean | 0.0002154099007 | 0.0002154099007 | 3.523657061e-19 | MATCH |
| slip150 | sd | 0.008157636484 | 0.008157636484 | 5.204170428e-18 | MATCH |
| slip150 | t | 1.49491097 | 1.49491097 | 1.33226763e-15 | MATCH |
| slip150 | t_nw | 1.463865692 | 1.463865692 | 1.33226763e-15 | MATCH |
| slip150 | p_t | 0.06751807923 | 0.06751807923 | 1.526556659e-16 | MATCH |
| slip150 | p_nw | 0.07161532451 | 0.07161532451 | 1.665334537e-16 | MATCH |
| slip150 | p | 0.07161532451 | 0.07161532451 | 1.665334537e-16 | MATCH |
| slip150 | sharpe_annualized | 0.4191809931 | 0.4191809931 | 3.885780586e-16 | MATCH |
| base | ci95_lo | -0.1091520215 | -0.1091520215 | 2.220446049e-16 | MATCH |
| base | ci95_hi | 0.9818119205 | 0.9818119205 | 1.110223025e-16 | MATCH |
| base | ci_undefined_draws | 0 | 0 | - | MATCH |
| base | holm_rejects | False | False | - | MATCH |
| base | sharpe_at_least_bar | True | True | - | MATCH |
| base | pass | False | False | - | MATCH |
| base | verdict.p | 0.0636836996 | 0.0636836996 | - | MATCH |
| base | verdict.t | 1.556561986 | 1.556561986 | - | MATCH |
| base | verdict.n | 3205 | 3205 | - | MATCH |
| base | verdict.mean | 0.0002242878504 | 0.0002242878504 | - | MATCH |
| base | verdict.sharpe_annualized | 0.4364682663 | 0.4364682663 | - | MATCH |

### T3

| case | number | run | verifier | abs diff | status |
|---|---|---|---|---|---|
| base | n | 3319 | 3319 | 0 | MATCH |
| base | mean | 0.0001015619975 | 0.0001015619975 | 6.776263578e-20 | MATCH |
| base | sd | 0.01104449528 | 0.01104449528 | 3.469446952e-18 | MATCH |
| base | t | 0.5297719823 | 0.5297719823 | 2.220446049e-16 | MATCH |
| base | t_nw | 0.5234261225 | 0.5234261225 | 2.220446049e-16 | MATCH |
| base | p_t | 0.2981527393 | 0.2981527393 | 5.551115123e-17 | MATCH |
| base | p_nw | 0.3003388748 | 0.3003388748 | 5.551115123e-17 | MATCH |
| base | p | 0.3003388748 | 0.3003388748 | 5.551115123e-17 | MATCH |
| base | sharpe_annualized | 0.1459774021 | 0.1459774021 | 5.551115123e-17 | MATCH |
| stress | n | 3319 | 3319 | 0 | MATCH |
| stress | mean | 8.862357818e-05 | 8.862357818e-05 | 4.065758147e-20 | MATCH |
| stress | sd | 0.01104481604 | 0.01104481604 | 5.204170428e-18 | MATCH |
| stress | t | 0.4622686274 | 0.4622686274 | 5.551115123e-17 | MATCH |
| stress | t_nw | 0.4568222661 | 0.4568222661 | 5.551115123e-17 | MATCH |
| stress | p_t | 0.3219595022 | 0.3219595022 | 0 | MATCH |
| stress | p_nw | 0.3238994001 | 0.3238994001 | 5.551115123e-17 | MATCH |
| stress | p | 0.3238994001 | 0.3238994001 | 5.551115123e-17 | MATCH |
| stress | sharpe_annualized | 0.1273770142 | 0.1273770142 | 0 | MATCH |
| slip150 | n | 3319 | 3319 | 0 | MATCH |
| slip150 | mean | 9.577054218e-05 | 9.577054218e-05 | 1.355252716e-20 | MATCH |
| slip150 | sd | 0.01104462856 | 0.01104462856 | 3.469446952e-18 | MATCH |
| slip150 | t | 0.4995563198 | 0.4995563198 | 1.110223025e-16 | MATCH |
| slip150 | t_nw | 0.4936153631 | 0.4936153631 | 1.110223025e-16 | MATCH |
| slip150 | p_t | 0.3087103221 | 0.3087103221 | 0 | MATCH |
| slip150 | p_nw | 0.3107889244 | 0.3107889244 | 0 | MATCH |
| slip150 | p | 0.3107889244 | 0.3107889244 | 0 | MATCH |
| slip150 | sharpe_annualized | 0.1376515486 | 0.1376515486 | 2.775557562e-17 | MATCH |
| base | ci95_lo | -0.3992983846 | -0.3992983846 | 1.110223025e-16 | MATCH |
| base | ci95_hi | 0.7064797234 | 0.7064797234 | 0 | MATCH |
| base | ci_undefined_draws | 0 | 0 | - | MATCH |
| base | holm_rejects | False | False | - | MATCH |
| base | sharpe_at_least_bar | False | False | - | MATCH |
| base | pass | False | False | - | MATCH |
| base | verdict.p | 0.3003388748 | 0.3003388748 | - | MATCH |
| base | verdict.t | 0.5297719823 | 0.5297719823 | - | MATCH |
| base | verdict.n | 3319 | 3319 | - | MATCH |
| base | verdict.mean | 0.0001015619975 | 0.0001015619975 | - | MATCH |
| base | verdict.sharpe_annualized | 0.1459774021 | 0.1459774021 | - | MATCH |

### T4

| case | number | run | verifier | abs diff | status |
|---|---|---|---|---|---|
| base | n | 3331 | 3331 | 0 | MATCH |
| base | mean | 0.05585883628 | 0.05585883628 | 2.081668171e-17 | MATCH |
| base | sd | 7.580185682 | 7.580185682 | 0 | MATCH |
| base | t | 0.425303891 | 0.425303891 | 1.110223025e-16 | MATCH |
| base | t_nw | 0.4303493494 | 0.4303493494 | 1.665334537e-16 | MATCH |
| base | p_t | 0.3353213196 | 0.3353213196 | 0 | MATCH |
| base | p_nw | 0.333470767 | 0.333470767 | 5.551115123e-17 | MATCH |
| base | p | 0.3353213196 | 0.3353213196 | 0 | MATCH |
| base | sharpe_annualized | 0.1169801867 | 0.1169801867 | 4.163336342e-17 | MATCH |
| stress | n | 3331 | 3331 | 0 | MATCH |
| stress | mean | 0.02718110761 | 0.02718110761 | 0 | MATCH |
| stress | sd | 3.364317903 | 3.364317903 | 0 | MATCH |
| stress | t | 0.4662914365 | 0.4662914365 | 0 | MATCH |
| stress | t_nw | 0.4788696366 | 0.4788696366 | 0 | MATCH |
| stress | p_t | 0.3205187039 | 0.3205187039 | 0 | MATCH |
| stress | p_nw | 0.3160156864 | 0.3160156864 | 0 | MATCH |
| stress | p | 0.3205187039 | 0.3205187039 | 0 | MATCH |
| stress | sharpe_annualized | 0.1282538449 | 0.1282538449 | 0 | MATCH |
| slip150 | n | 3331 | 3331 | 0 | MATCH |
| slip150 | mean | 0.04342382154 | 0.04342382154 | 0 | MATCH |
| slip150 | sd | 5.587942355 | 5.587942355 | 0 | MATCH |
| slip150 | t | 0.4485010253 | 0.4485010253 | 0 | MATCH |
| slip150 | t_nw | 0.4552774265 | 0.4552774265 | 0 | MATCH |
| slip150 | p_t | 0.3269104136 | 0.3269104136 | 0 | MATCH |
| slip150 | p_nw | 0.324454832 | 0.324454832 | 0 | MATCH |
| slip150 | p | 0.3269104136 | 0.3269104136 | 0 | MATCH |
| slip150 | sharpe_annualized | 0.1233605776 | 0.1233605776 | 0 | MATCH |
| base | ci95_lo | -0.3687664236 | -0.3687664236 | 0 | MATCH |
| base | ci95_hi | 0.5997974097 | 0.5997974097 | 0 | MATCH |
| base | ci_undefined_draws | 0 | 0 | - | MATCH |
| base | holm_rejects | False | False | - | MATCH |
| base | sharpe_at_least_bar | False | False | - | MATCH |
| base | pass | False | False | - | MATCH |
| base | verdict.p | 0.3353213196 | 0.3353213196 | - | MATCH |
| base | verdict.t | 0.425303891 | 0.425303891 | - | MATCH |
| base | verdict.n | 3331 | 3331 | - | MATCH |
| base | verdict.mean | 0.05585883628 | 0.05585883628 | - | MATCH |
| base | verdict.sharpe_annualized | 0.1169801867 | 0.1169801867 | - | MATCH |

### Daily series, date by date

| test/case | run n | verifier n | first (run / verifier) | last | dates differing | max abs diff | sum run | sum verifier |
|---|---|---|---|---|---|---|---|---|
| T1/base | 3205 | 3205 | 2011-07-27 / 2011-07-27 | 2024-02-29 / 2024-02-29 | 0 | 0 | 1.053515237 | 1.053515237 |
| T1/stress | 3205 | 3205 | 2011-07-27 / 2011-07-27 | 2024-02-29 / 2024-02-29 | 0 | 0 | 0.9574170498 | 0.9574170498 |
| T1/slip150 | 3205 | 3205 | 2011-07-27 / 2011-07-27 | 2024-02-29 / 2024-02-29 | 0 | 0 | 1.023976412 | 1.023976412 |
| T2/base | 3205 | 3205 | 2011-07-27 / 2011-07-27 | 2024-02-29 / 2024-02-29 | 0 | 0 | 0.7188425604 | 0.7188425604 |
| T2/stress | 3205 | 3205 | 2011-07-27 / 2011-07-27 | 2024-02-29 / 2024-02-29 | 0 | 0 | 0.6226650948 | 0.6226650948 |
| T2/slip150 | 3205 | 3205 | 2011-07-27 / 2011-07-27 | 2024-02-29 / 2024-02-29 | 0 | 0 | 0.6903887317 | 0.6903887317 |
| T3/base | 3319 | 3319 | 2010-10-28 / 2010-10-28 | 2024-02-29 / 2024-02-29 | 0 | 0 | 0.3370842697 | 0.3370842697 |
| T3/stress | 3319 | 3319 | 2010-10-28 / 2010-10-28 | 2024-02-29 / 2024-02-29 | 0 | 0 | 0.294141656 | 0.294141656 |
| T3/slip150 | 3319 | 3319 | 2010-10-28 / 2010-10-28 | 2024-02-29 / 2024-02-29 | 0 | 0 | 0.3178624295 | 0.3178624295 |
| T4/base | 3331 | 3331 | 2011-01-26 / 2011-01-26 | 2024-02-29 / 2024-02-29 | 0 | 0 | 186.0657837 | 186.0657837 |
| T4/stress | 3331 | 3331 | 2011-01-26 / 2011-01-26 | 2024-02-29 / 2024-02-29 | 0 | 0 | 90.54026946 | 90.54026946 |
| T4/slip150 | 3331 | 3331 | 2011-01-26 / 2011-01-26 | 2024-02-29 / 2024-02-29 | 0 | 0 | 144.6447495 | 144.6447495 |

### Gross, costs and fills by kind

| test/case | run gross | verifier gross | run costs | verifier costs | run share | verifier share |
|---|---|---|---|---|---|---|
| T1/base | 1.135191282 | 1.135191282 | 0.08167604561 | 0.08167604561 | 0.07194914804 | 0.07194914804 |
| T1/stress | 1.135191282 | 1.135191282 | 0.1777742324 | 0.1777742324 | 0.1566028873 | 0.1566028873 |
| T1/slip150 | 1.135191282 | 1.135191282 | 0.1112148703 | 0.1112148703 | 0.09797015887 | 0.09797015887 |
| T2/base | 0.7973083163 | 0.7973083163 | 0.07846575593 | 0.07846575593 | 0.09841331682 | 0.09841331682 |
| T2/stress | 0.7973083163 | 0.7973083163 | 0.1746432216 | 0.1746432216 | 0.2190410133 | 0.2190410133 |
| T2/slip150 | 0.7973083163 | 0.7973083163 | 0.1069195846 | 0.1069195846 | 0.1341006765 | 0.1341006765 |
| T3/base | 0.427917939 | 0.427917939 | 0.09083366927 | 0.09083366927 | 0.2122688978 | 0.2122688978 |
| T3/stress | 0.427917939 | 0.427917939 | 0.133776283 | 0.133776283 | 0.3126213482 | 0.3126213482 |
| T3/slip150 | 0.427917939 | 0.427917939 | 0.1100555095 | 0.1100555095 | 0.257188352 | 0.257188352 |

- T1/fills_by_kind: run {"rebalance": {"fills": 2121, "abs_contracts_per_capital": 0.004784476300964327}, "roll_in": {"fills": 980, "abs_contracts_per_capital": 0.006832929382010042}, "roll_out": {"fills": 980, "abs_contracts_per_capital": 0.006832929382010042}}; verifier {"entry": 45, "roll_out": 980, "roll_in": 980, "rebalance": 1825, "flip": 206, "exit": 45}
- T2/fills_by_kind: run {"rebalance": {"fills": 2121, "abs_contracts_per_capital": 0.008584819324259887}, "roll_in": {"fills": 980, "abs_contracts_per_capital": 0.004644594738277805}, "roll_out": {"fills": 980, "abs_contracts_per_capital": 0.004644594738277805}}; verifier {"entry": 45, "roll_out": 980, "roll_in": 980, "rebalance": 1393, "flip": 638, "exit": 45}
- T3/fills_by_kind: run {"entry": {"fills": 227, "abs_contracts_per_capital": 0.04294261376031261}, "exit": {"fills": 227, "abs_contracts_per_capital": 0.04294261376031261}}; verifier {"entry": 227, "exit": 227}
