# StatsCostCoder readings (Stage E.33, prompt B5 (iii) and B6)

Worker: StatsCostCoder-OpusXHigh. Written 2026-10-27, 15:09-15:27 PDT. The weekly usage limit cut the run at
about 15:27 PDT; it resumed 2026-10-28 02:02 PDT and finished 02:04 PDT, when the select33 reproduction was
added. Protocol:
reports/stage_e32_discovery_protocol.md (sha256 c4ffb9d7...; checked at start). Every reading below is the
lead's to decide before the freeze. In code, cost33 readings are marked `READING C<n>`. The B5 (iii) readings
(R1-R5) are notes on the reproductions. No code exists for them, because the code under test belongs to other
workers.

Files written:
- reports/stage_e33_briefs/work/pipeline/cost33.py (sha256 505f5252...)
- reports/stage_e33_briefs/work/pipeline/tests/test_cost33.py (23 tests, all pass)
- reports/stage_e33_briefs/work/pipeline/tests/test_stats_repro33.py (29 tests, all pass; sha256 c7c3d649...)
- reports/stage_e33_briefs/pages/StatsCost/ (3 rendered crops) and rows in reports/stage_e33_briefs/pages/LOG.md

No real market data was read. No page was fetched from the web: every source was already saved in E.28 or E.32.
The guard was not needed.

## B5 (iii) reproduction results

| Worked example | Source used | Code under test | Result |
|---|---|---|---|
| DSR numerical example (BLdP 2014, pp. 9-10) | E.32 PDF. Inputs are glyphs that pdftotext drops: read from the rendered pages (StatsCost/dsr2014_p9*, _p10*). Same inputs as text in LdP 2017 slides 41-42 (E.28 C2_AFML) | funnel expected_max_sharpe, deflated_sharpe_ratio; stage_e_verdict dsr, dsr_table | Reproduced to the 4 printed decimals: SR0 0.1132 (0.113172), DSR 0.9004 (0.900397), N=46 0.9505 (0.950502), normal N=88 0.9505 (0.950491) |
| BH 1995 15 p-values (sec. 3.2, p. 295) | E.32 PDF text | _d1f_decisions.benjamini_hochberg; screening holm_tier_a; _d1f holm | Reproduced. BH q=0.05 rejects 4; threshold 4/15 x 0.05 = 0.013 (3 d.p.); Bonferroni 0.05/15 = 0.0033 (4 d.p.) rejects 3. Holm rejects 3: this follows from the paper's counts (see R2) and is not printed in the paper |
| BH/Holm in pipeline/select33.py | E.32 PDF text | select33.bh_holm, reference_thresholds (select33.py sha256 1a7207f8..., mtime 2026-10-27 15:26; absent at the 15:09 and 15:25 polls, present at 02:02 on 10-28) | Reproduced. bh_holm rejects 4 (BH) and 3 (Holm) on the 15 p-values. Each p is fed as t = Phi^-1(1 - p), because select33 takes daily t and uses p = 1 - Phi(t); the round trip holds to rel 1e-9. p = 1.000 is fed as t = None (select33 READING Q7 sets p = 1). The Bonferroni step-1 z gives 0.0033 (4 d.p.). If ProofCoder changes select33 after this hash, rerun the test |
| PBO/CSCV (Bailey, Borwein, LdP, Zhu 2017) | E.32 PDF text; p. 11 crop | funnel probability_of_backtest_overfitting; stage_e_verdict pbo | N=3 rank example reproduced exactly (ranks (1,3,2) and (1,2,3); omega 0.5, logit 0). Split counts 6 (S=4) and 924 (S=12) reproduced by the program. 2,704,156 (S=24) checked on Eq. 2.3 only; the program was not run at S=24. S=16: the paper prints 12,780; Eq. 2.3 and the program give 12,870. NOT REPRODUCED: a misprint in the paper (R4). The program's PBO equals Algorithm 2.3 run literally on 4 random tie-free matrices |
| AFML ch. 4 average uniqueness / sequential bootstrap toy example | AFML not obtained (a paid book). The example comes from a secondary source: the mlfinpy docs (E.32 M3 pages), "toy example from the book". The definition comes from the author's 2017 slides | lab33.uniqueness_weights, interval_set | Reproduced: u = (5/6, 3/4, 1). The 9 published probabilities (3 iterations) match to atol 2e-16, about 16 significant digits. The primary text was not checked (R5) |
| AFML ch. 7 purged/embargoed K-fold | AFML not obtained. The construction comes from the author's restatement: LdP 2018 JPM Solution #8 (E.32 pages) and 2017 slides 34-35 | search33.make_folds, EMBARGO | No numeric worked example exists in the sources. The construction is reproduced: the three overlap conditions plus an embargo of h = 21 dates, applied literally to date-level spans, give search33's training sets for all 6 folds (642, 642, 642, 642, 643, 664). Purging removes nothing. 21 >= 0.01 T (8 dates) |
| moments, t_stat | none of the four sources has a worked example for them | stage_e_verdict | Checked only against Harvey-Liu 2015 eq. (1)-(2), on a hand-computed series. This is not a published reproduction |

## Readings: B5 (iii)

R1. The DSR example's units. The paper's inputs are annualised: SR 2.5 and V[SR_n] = 1/2. The paper computes
SR0 with 1/(2 x 250) and the SR as 2.5/sqrt(250), and its formula uses sqrt(1249) = sqrt(T - 1). The test passes
daily values (SR 2.5/sqrt(250), V 0.5/250, T = 1250), which is the program's "same period basis" docstring.
Nothing else was considered: the paper prints those exact expressions.

R2. Holm in the BH example. The paper prints Bonferroni (3) and Hochberg (3), not Holm. Holm is at least as
powerful as Bonferroni and at most as powerful as Hochberg, so it must reject 3. The test labels this "implied by
the published counts". This is not a printed number.

R3. The PBO count at the median. The paper defines PBO two ways that disagree at the median rank:
- Definition 2.2 (eq. 2.2) uses "rbar_n < N/2".
- Section 3.1 estimates PBO as phi = integral from -infinity to 0 of f(lambda).

In the N = 3 example the IS winner sits at the OOS median (omega 0.5, lambda 0). The program counts lambda <= 0 as
overfit (multiple_comparisons.py, `lg <= 0`); Definition 2.2 would not count that split. The program's choice gives
the higher PBO, the conservative side. The program's rank also differs from the paper's:
- program: omega = (number strictly worse + 0.5)/N;
- paper: rbar/(N + 1).

The two always give the same logit sign without ties, so PBO is identical; the logit magnitudes differ (they are
not reported as a gate). The program also measures performance as block P&L sums, while the paper's example uses
Sharpe; the paper allows any measure, and P6.3 fixes the program's. funnel/ is pinned and was not edited.

R4. The S = 16 misprint. The paper prints "12, 780" combinations twice (pp. 11 and 22). The rendered p. 11
(StatsCost/pbo2017_p11_eq2_3_combinations.png) confirms the PDF says this; it is not an extraction error. Eq. 2.3
gives C(16, 8) = 12,870, and the program agrees with Eq. 2.3. The sigma[f] < 0.0045 bound holds for both.

R5. AFML (paid) was not fetched, so the AFML numbers come from secondary or author-restated sources:
- ch. 4: the mlfinpy documentation's restatement of the book's toy example. The digits match it, but the book
  itself was not seen;
- ch. 7: the author's 2018 JPM paper and 2017 slides give the construction only (no numeric example). The test
  reproduces the construction, not a worked example.

The lead decides whether this counts as "the stated digits" for AFML.

## Readings: B6 (cost33)

C0 (fees; information). E.28's A2 files give ZM round-trip fees of:

| Firm | USD | Ticks |
|---|---|---|
| Topstep | 5.28 | 0.528 |
| Lucid | 5.60 | 0.560 |
| Bulenox | 5.72 | 0.572 |
| MFFU | 6.12 | 0.612 |
| Tradeify | 9.20 | 0.920 |

These agree with A3_firm_products.json (fee_rt_ticks), with A3_econ.json (pairs F_rt_ticks) and with P6.4's list
to 1e-9. P0.3's f = 0.528 equals Topstep's. No differences were found.
- Lucid: the A2 note says "inclusion of exchange/NFA fees not stated". cost33 reports 0.560 as the firm's figure
  and P6.4's alternative 0.920 as `lucid_not_all_in` (the E.28 u-rule; methods brief line 8808). Which one governs
  is the lead's choice.
- E.31's FEE_PER_FILL_TICKS (0.264, 0.280, 0.286, 0.306, 0.460) equal exactly half of these.

C1. A print stamped at the placement time is not a fill. P6.4 (ii) says "at t + L the order rests ... fills only
when a trade prints strictly through". The window is therefore open at t + L. This follows E.31: a timer at T sees
every record stamped at or before T before the order joins, so a record with ts_recv = t + L is known at
placement and came before the order. The alternative (closed at t + L) counts prints that the order could not
have met. The choice is needed for agreement with E.31.

C2. Side-N trades never fill. The protocol says "a trade prints strictly through" and does not name sides. E.31
excludes side-N (implied or opening) trades from every fill (measure31_core: "Side-N trades ... are never match
events"). This is chosen for agreement with E.31 under V50. Including N trades would add fills on implied prints
that a resting outright order may not trade against.

C3. The window and the conversion time. The protocol says "within min(60 s, h/5)". The order rests W =
min(60 s, h/5) at the exchange: window (t + L, t + L + W], closed at its end. W = 60 s for every protocol
horizon. The bot's cancel/convert decision is at c = t + W; it reaches the exchange at c + L = t + L + W, and the
(ii-b) market order fills at the touch as of t + L + W.

Alternatives considered:
- E.31's window, (j, j + 60 s + 50 ms): the cancel latency is added on top of 60 s;
- a window measured from the decision t.

The test test_e31_window_differs_only_by_its_cancel_latency documents a print in E.31's last 50 ms that fills
under E.31 only. This is a difference of window length, not of rule. For E.33 the difference is L itself (the
window would be 61 s under E.31's convention). This should be decided: a longer window raises p_fill.

C4. An exit decision before the timeout (only TB, when the barrier is hit within 60 s). The window ends at the exit
decision: c = min(t + W, exit decision), and the window is (t + L, c + L].
- (ii): no trade.
- (ii-b): converts at c. When c equals the exit decision, entry and exit fill at the same instant, so the net is
  -spread - fee. This is the conservative choice: it charges the cost of the signal.

The alternative is to cancel without trading in (ii-b) too. That reads better as bot behaviour but drops a costly
case.

C5. No touch on the order's side (or a bad book) at t + L. The order is not placed (flag 64); it counts as unfilled
in p_fill, and (ii-b) still converts at c. The alternative is to place it at the first later valid update (a P3.2
analogue). This case is rare, because the P3.6 entry rules need a valid book at t.

C6. The exit for limit variants is the selection variant's exit decision, supplied by the caller: t + h for FH,
and the selection simulation's tau for TB. The basis is P6.4: "variants differ only in execution". cost33 does
not recompute TB barriers from a limit fill. It also does not apply P3.2's TB rule ("if M_ZM is undefined at that
update, the entry is not made"); the caller does.

C7. cost33's entry_leg_net is E.31's N_h = s (mid(t_f + h) - price) - fee/2, from the mid as of t_f + h. E.31's
headline markout also drops a fill when any book state over [t_f, t_f + h] is invalid; cost33 does not apply that
drop. In the agreement tests the books stay valid, so the two agree exactly (to 1e-9).

C8 (information). E.31's engine runs on mbo_book31.time_axis, the running maximum of ts_event; E.33 uses ts_recv
(P0.3). The hand-built agreement tests feed the same explicit times to both, so they check the rules, not the
clock.

## E.31 agreement (B6)

E.31's own engine was run end to end on hand-built MBO streams:
- measure31_core.InstrumentRun.run with one DAY session and one placement grid time;
- per-fill accounting from measure31_core._fill_fields and stats31.edge_arrays, minus
  stats31_core.FEE_PER_FILL_TICKS.

Five cases were run, covering: an at-price print, a side-N print through the price, a print exactly at the join
time, prints after the life, a touch move after placement, and both sides. cost33's limit price, fill decision and
fill time equal E.31's for all 10 orders (6 fills). Its per-fill net equals E.31's for 6 fills x 3 horizons (1, 10,
60 s) x 5 firms, to 1e-9. E.31 code was imported and run, never edited. pilot/runs/, E.31_RETURN.md lines 175-213
and stage_e32_briefs/X1_* were not opened.
