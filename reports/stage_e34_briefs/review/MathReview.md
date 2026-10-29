# E.34 Part M review (MathReviewer-FableXHigh, Fable 5.1, xhigh)

Written 2026-10-29 14:05-14:24 PDT (times from `TZ=America/Vancouver date`). Inputs: M1_F10_ZL.md, M2_F09_ZL.md, M3_labels_ZL.md, M4_power_ZL.md,
L_lead_reconciliations.md; the four workers' scripts and outputs; the frozen E.32 functions m4_power.py imports;
reports/stage_e34_data_facts.md (counts only, lines 100-146); reports/stage_e34_exposure.md section 6; the E.32
protocol and methods brief at the cited lines only. Scratch: work/MathReviewer-FableXHigh/ (indep_m4_L.py and .out,
cite_check.py and .out, the four reruns).

What was run. Each script was grepped for file reads before running (m1: math and statistics only; m2: writes its
own JSON only; m3: numpy, os.nice; m4: imports p7_thresholds, p7_final and funnel.multiple_comparisons, whose only
file read is data/calendars/hist2010/grains.json through data.hist_calendar, a holiday calendar). All four reran at
nice 10 (rc 0) and reproduced the saved outputs byte for byte: m1_examples.out identical, m2_examples.json
identical, M3_calc.out identical, m4_out.md identical (195 lines, 0 diff lines). I then recomputed the M4 and L
numbers with my own implementation of e(N), DSR, the bisections and the e80 formula (indep_m4_L.py, no frozen
imports): every printed digit agrees. No market data was opened; no price, return, feature or label was computed;
no earlier-stage ZL statistic was read; nothing outside review/ and work/MathReviewer-FableXHigh/ was written.

## Verdict: GO WITH FIXES

The arithmetic is right. Every number that would enter the protocol from M4 and L (T_disc 796, T_test 870 and 885,
the threshold rows at N 838..1138, SR80_test 0.1936/0.1957, e80 at caps 19/9/4 and 17/8/4, Holm z, the D2
multipliers and simulation, the L.a rates, the L.b caps and e80, the L.e span) recomputes. M3's caps 17/8/4, dead
zone, barrier widths, trade-through identities and the M6 table recompute; M2's break-even shares (0.5236, 0.3491,
0.2618) and cost per sigma (0.0847, 0.0922) recompute; M1's per-bucket SDs and R2 hurdles recompute. The two
blocking items are feature definitions in M1's F10 list that would be frozen as written and are wrong on a
subset of book states (F10.7) or under one unverified data property (F10.9); each has a one-clause fix. The
verdicts (MBP-1 both windows, 5-minute minimum; CL out, leaders from bars, ZL-dependent crush residual; labels F15
F30 F60 T15 T30 with dead zone and caps; power, K2 and D2; L.a-L.e) follow from their evidence, with the
qualifications below.

## BLOCKING

**B1. M1_F10_ZL.md:153 and :467 (F10.7 seasoned-depth proxy): the zero rule "qb~(t) = 0 if bid_1 rose in
(t - 1 s, t]" is wrong on a rise-then-fall second, so the proxy is not an upper bound on seasoned depth there.**
Counterexample: at t - 1 s bid_1 = p with old orders resting at p; at t - 0.5 s a new order improves the touch to
p + 1; at t - 0.2 s it is cancelled and bid_1 returns to p. At t the orders at p have last add or modify before
t - 1 s, so the exact seasoned depth S_b(t) > 0, but the rule gives qb~ = 0 and QI1s = -1 whenever qa~ > 0. The
proof sketch at :155-158 ("if bid_1 rose inside the last second, every order at bid_1(t) was added or modified
within it") is false on that path: the orders at p sat at level 2 while p + 1 existed. Exact fix (keeps the proof
and makes the rule exact in more cases): replace the condition by "the most recent change of bid_1 with ts_recv in
(t - 1 s, t] was an increase" (ask: "was a decrease"). Then: last change a rise to p at t_c > t - 1 s means no
order rested at p before t_c, so S_b(t) = 0 exactly; last change a fall (or no change) keeps the min rule over
[t_c, t], which remains an upper bound. Add the rise-then-fall path to trap 9's synthetic test (M1 :407-409), with
hand value qb~ = min over [t - 0.2 s, t], not 0.

**B2. M1_F10_ZL.md:169-180 and :469 (F10.9 touch cancellations): the fill attribution is only correct if CME's
post-fill size reductions arrive on C or M records; the claim at :178 that "the definition counts correctly in
either case" is false.** If the reduction sits on the T record itself (the branch M1 marks [unverified] at
:177-178 and :499-500), the C/M records in that batch carry only genuine cancels, and subtracting the batch's
traded lots F_b from them removes real cancels: a batch with T 12 at p (bid_sz 20 -> 8 on the T record) and then
a 3-lot cancel at p (8 -> 5) gives r_j = 3, F_b = 12, counted removal 0 instead of 3. On the informative batches
(those with trades at the touch) CR5 would then be biased toward 0. Exact fix, correct in both branches: take the
state difference over every consecutive record pair of the front (A, C, M, T and any other action, not only C and
M), so the batch's total touch decrease at p = fills + removals whichever record carries the fill, and subtract the
batch's T lots at p once; a pair whose either state is one-sided or bad contributes 0 and is counted (the OFI FD3 b
rule at :147-148, not stated for CR5). Keep M1's run-stage check (2) (:485-487) as a report, not as the thing the
definition depends on. Alternative: run check (2) before the freeze (counts only) and freeze the matching form; the
robust form above avoids that dependency.

## SHOULD FIX

**S1. L_lead_reconciliations.md:55-56: "The 20-entry hard cap of E.32 P3.8 stays as written (it never binds at
h >= 15)" is true for FH labels only.** M3 a.3 (:55-56) gives the T label's mean hold as 0.706-0.774 h, about 11
minutes for T15 and 21-23 for T30, and M3 d.2 (:271) says n_max^T depends on the realised tau "(bounded by 20)".
With a 12-minute T15 cycle (hold plus the next grid minute) 277 / 12 is about 23 > 20, so the cap can bind on a
T15 date with early barrier exits, and on a volatile T30 date. Fix: "it never binds for F15, F30, F60 (maxima 17,
8, 4); it can bind for T15 and T30, whose trade count per date is realised, not fixed". The L.b e80 table is for
FH labels; say so.

**S2. The MBP-1 bad-book reading differs between M1 and M3, and L does not pick one.** M1 :402 and :456 (feat33
READING FA-4): "a batch containing F_MAYBE_BAD_BOOK marks the book bad" (confirmed at feat33.py:561-562: "the
update is marked bad if any record of its batch (since the previous F_LAST record) carries F_MAYBE_BAD_BOOK").
M3 :230-231 and :445-446 (P3.0): "an update is bad iff its F_LAST record carries F_MAYBE_BAD_BOOK". Only 476
records carry the flag (DF34 :108), so the effect is small, but features and labels would disagree on which
updates are bad. Fix: L declares FA-4 (any record in the batch) for both features and labels, and states the
persistence rule for MBP-1, which has no R record (M3 :229-230): bad for that update only, or until the next
two-sided good batch. Related: M3 c.4 (:228-236) still argues from "the ZL MBO test that F10 needs"; M1 4.4 and
L.e settle on MBP-1 in both windows, which collapses M3's parity options to (a) without the MBO purchase. L should
say so in one line (label source = ZL MBP-1 in both windows; parity by identical code).

**S3. M2_F09_ZL.md:540-541 (rule variant): "Decision grid: minute marks 08:35..(13:12 - h) CT, further capped by
Topstep's latest entry (h 30: 10:50 PT = 12:50 CT)" conflicts with L.c.** L.c retires the 12:50 figure (the
grid's 13:12 - h already ends h 30 at 12:42). Applied as written to every h, a 12:50 cap would cut the h 15 starts
12:51-12:57 (7 of 263) for no reason. Fix: delete "further capped by Topstep's latest entry ..."; the grid alone
governs (latest 12:57 / 12:42 / 12:12 CT).

**S4. M2_F09_ZL.md:225-227 and :514 (bar bounce in the implied-oil gap): the SD is computed for one endpoint;
a k-minute return of each leg has two bar closes, so the gap's bounce SD is sqrt(2) x 1.594 = 2.254 ZL ticks**,
19% of sigma_5, 11% of sigma_15, 8% of sigma_30 and 41% of sigma_1 (not 13 / 8 / 6 / 29%). The verdict stands
(k = 1 dropped; k >= 5 kept) but "second-order" at k = 5 is weaker than stated; with ZL's price from its BBO mid
the ZL term drops and the figure is sqrt(2) x 1.513 = 2.14 ticks. Fix the four percentages and the sentence at
:230-231.

## NOTE

N1. M4 :41-43 (equation 7) and p7_final.py:104: SR80 = bar + z80 se(bar, T) uses se at the bar rather than at
SR80 itself. The exact value (bisection on s - z80 se(s, T) = b) is 0.1937 against 0.1936 at N 838, 0.1958
against 0.1957 at N 1038: a 0.05% difference, immaterial. Recorded so the protocol can say "E.32 convention".

N2. M4 :168-169: "+2 to 4% at kurtosis 6 to 20" overstates. Recomputed from M4's own moment table: binding
threshold +2.6% (skew -0.5, k 6), +1.3% (k 10), +3.1% (k 20); SR80_test +2.2 / +1.1 / +2.6%. "+11% at skew -2 /
kurtosis 30" is +11.1% on SR80_test and +13.1% on the binding threshold. Say "+1 to 3%".

N3. M1 :207-208 (worked TI example): TI5 = 0.20 with iid SE 1/sqrt(275) = 0.0603 is 3.3 standard errors, not
"two". The long-memory reading (about one SD at 0.184) is right.

N4. M1 :73-74: "3 to 6 times lower than ZM's at 5 minutes in E.32 (0.0120 top decile)". Recomputed: 0.0120 /
0.00321 = 3.7, / 0.00169 = 7.1, / 0.00091 = 13 on the c_f column; 2.0 / 2.3 / 2.0 on the c_f + e80_test column.
Neither range is "3 to 6". (The ZM figure is verified at E.32 brief :3663, h 5 row, c_f 1.59.)

N5. Two data-facts files disagree on ZL's ts_recv - ts_event tail: E.32 data facts :101 gives ">= 1 s: 1 (in
[1 s, 60 s))" for the Z3 ZL file; DF34 :107 gives "> 1 s: 354 records; > 1 day: 7 (not cross-tabulated against
the flags)". M1 trap 1 (:370-371) quotes the former, L.d (:77-78) the latter. The 230,475 negative count agrees
in both. The likely reconciliation is that the 354 and 7 lie among the 848 F_SNAPSHOT / F_BAD_TS_RECV records,
which E.32's table may have excluded; L.d's rule is drop-and-count either way, so no protocol number changes, but
the lead should have DataFacts cross-tabulate the 354 against the flags so L.d's rule 2 second clause is known
to be redundant or not.

N6. M1 :44 (bottom line 3) states "Databento derives CME MBP-1 from MBO" flatly; section 2.1 (:103) correctly
marks the GLBX-specific step as an inference from the general schema page. Carry the caveat into the bottom line.

N7. M1 :387-388: at 08:35 on the open-time axis a 30-minute window reaches back to 07:20 and a 15-minute window
to 07:35, not "07:15-07:45". Immaterial.

N8. M3 :393-394 and M3_calc.py:100-102: the release-day n_eff uses 143 + 101 = 244 covered minutes; counting
one-minute intervals the two blocks are [08:35, 10:57] = 142 and [11:31, 13:12] = 101, so 243 and n_eff 16.2 /
8.1 / 4.05 instead of 16.27 / 8.13 / 4.07. Immaterial.

N9. Propagation of L.b and L.c into the illustrative figures that still use E.32b's e80 at caps 19/9/4 and the
12:50 entry: M1 :35-36 and :64-68 (g = c_f + e80_test 3.28 / 4.19 / 6.08 become 3.34 / 4.30 / 6.08 at caps 17/8/4),
M2 :110-112 (4.19 -> 4.30 ticks; 0.461 -> 0.473 c/bu), M3 :19 and :205 (alpha rows). None enters the protocol;
L.b's "reported beside it for continuity" covers them, but a one-line pointer in each M file would stop a reader
pasting 1.81.

N10. Citation line drift (every quote verified by grep; only the line numbers move): M4 :71 "protocol line 777"
for "stay sealed and untested" is line 795; M4 :21 "lines 518, 520, 521" are 517, 519, 520; M3 :104 "line 285"
is 283-284 (wrapped); M2 :375 "lines 821-822 and 880-882": the first quote is at 880 only, the second at 893;
M2 :390-391 Rechner "lines 278, 356" are 283 and 362; M2 :306 farmdoc 2023 "165-167" is 171; M3 :351 Avileis
"line 395" is 408. Fix the numbers or cite with "near".

N11. RULES 3 wording: M2 :284 "with no pass" (E.12/E.20 G17 leads on ZL) and :179 "null on 2019-05..2024-02 in
E.22" are non-numeric closed-trial statuses taken from E.32b recs and R1 closed lines, not copied statistics; I
read them as within rule 3. If the lead wants zero outcome words on ZL trials, phrase them as "closed (R1-11,
R1-15, R1-08)".

N12. Traps to add (none is a hole in what is listed; each is a test the protocol should name):
(a) DST: the 08:35-13:13 CT grid and the 16:00 CT trade-date boundary move by one hour in UTC between CST and CDT
    (L.d itself uses 22:00Z for 2020-11-30 and 21:00Z for 2017-05-21). Test: the grid is built per date in
    America/Chicago; the decision-minute count equals 278 - h on every ordinary date in both windows.
(b) The ohlcv-1m bar-stamp convention (M2 :244-246, [unverified]) gates M2's rule B (:483-485). Make DataFacts'
    confirmation a precondition of the freeze, not a run-stage check; a wrong convention is a one-minute look-ahead
    on every F09 feature.
(c) TI_k and C.5 count T records with ts_recv <= t even when the batch's F_LAST is after t, while book-state
    features use the batch end. Both are "known at t"; state it so the two conventions are not read as a leak.
(d) MBP-1 bad-book persistence (S2 above).

N13. L.b's K2 logic, checked: the measured form (mean(X_D)/nbar >= SR80_test SD(X_D)/nbar) is the inequality
SR_d >= SR80_test, and G4 gives SR_d >= 0.2007 > 0.1936, so K2 cannot bind at T_test 870. It binds only when
SR80_test(realised T) exceeds 0.2007; with SR80 roughly proportional to 1/sqrt(T) that needs T_test below about
870 x (0.1936 / 0.2007)^2 = 810, about 60 dates lost. Worth stating as the trigger.

N14. M4 :252-262 shows 9 of the script's 12 D2 cases; the omitted rows (0.30 + 2 nulls; 0.20 alone; 0.25 alone)
are in m4_out.md and change nothing. M4 :268 "sqrt(2) x 0.034 = 0.048": recomputed sqrt(se(0.25)^2 + se(0.15)^2)
= 0.0485.

## Check 2: equations (units, signs, causality, agreement with the E.32 text)

- M4 eq. 1-9 (:31-50) match funnel/multiple_comparisons.py:63-115, p7_final.py:41-56 and p7_thresholds.py:69-81,
  and the E.32 brief :7259-7262 (BLdP eq. (1) and (2)) and :8223 (Mertens). The e80 derivation is right: with n
  independent trades a date of mean mu and SD sigma_h, daily SR = mu sqrt(n)/sigma_h, so mu = SR sigma_h/sqrt(n);
  with trades on a fraction p of dates the daily variance is about p n' sigma_h^2, so n = p n' (inactive dates
  included) as :45-47 says. The equicorrelation factor 1 + (k - 1) rho_w on the daily variance is right. The
  kurtosis-of-a-sparse-series claim (3/p, :126) is exact for a zero-mean normal mixed with zeros.
- M3 a.2 (:32-39) is protocol P3.3-P3.4 (:279-291) with ZM -> ZL and f 0.528 -> 0.880 = 5.28/6.00; the identity
  N_long + N_short = -s(t+L) - s(t+h+L) - 2f (:88) holds; b.2's dead-zone equivalence (:108) holds; q* = 0.5 +
  d/(2 E|Z| sigma_h) with E|Z| = 0.7979 is the right break-even sign hit rate; the first-passage series (:44) is the
  standard two-sided-barrier formula; p* = 0.5 + c/(2b) is the barrier-exit break-even; the M6 identities (:185-186)
  verified algebraically (V_M - V_L = OC - p s); the limit-band integer form (:371-372) is exact
  (mid >= 0.99 HL - 0.01 LL <=> 100(bid + ask) >= 198 HL - 2 LL); n_max^F = floor((277 - h)/(h + 1)) + 1 follows
  from P3.8 (:363, verified) and the 0.3 grid (:68; 273/263/248/218 = p7_final.DECISION_MINUTES; lab33
  LAST_GRID_OFFSET = 277, line 51). Units: ZL tick 0.01 c/lb x 60,000 lb = USD 6.00; barriers in USD at :47-48.
- M2: C = 11 O + 2.2 M - S is protocol F1 (:413-414; 11 lb oil, 44 lb meal, 2.2 = 44/2000 x 100); the tick
  conversions (0.11 / 0.22 / 0.25 c/bu per tick), hedge ratios and contract-size arithmetic are right; zRL mirrors
  F1.3 (:418) with ZL dependent; g_k mirrors F2.7 (:430) with the identity (dS - 2.2 dM)/11 - dO = -dC/11 and the
  sign convention g > 0 -> buy ZL (crush narrowed) right; s_i = beta_i alpha_i / beta'alpha sums to 1 and ZL's
  per-cent move alpha_L/(-beta'alpha) = -s_L/0.11 is consistent (1.292 x 0.11 = 0.142); hl = -ln 2 / ln phi. ZS's
  3.11 ticks per minute is the E.32 brief :1382 figure. Causality: OLS from the 10 prior dates, scales from the 20
  prior dates, bars after close (rule B), all before t.
- M1: e_n is protocol F2.8 (:433); the R2 hurdle R2 = (g/(sigma_h k))^2 is the E.32 brief :3655-3663 form; the
  long-memory variance 1 + 2 sum (1 - l/n) C0 l^-gamma is right; F10.7's step (ii) is right (fills do not unseason;
  a seasoned order's size at u >= its size at t), step (i) is wrong (B1); F10.9 (B2); F10.10's batch-end reading
  is sound for MBP-1; F10.11-F10.12 match F3.11-F3.12 (:446, :450, 30 intervals). Every feature reads ts_recv <= t;
  no feature reads (t, t + L].
- L: all arithmetic recomputed (table below); L.d uses ts_event for dropping only; L.e's 15 dates are the weekdays
  2017-05-01..19 (no closure).

## Check 3: leakage and look-ahead traps (coverage of the ones the brief names)

| trap | where listed, with a test |
|---|---|
| roll days and ZL.v.0 flips | M1 trap 3 (:377-383; instrument_id constant inside every window; roll date + next excluded); M3 e.2 rule 4 (:357-363), e.4 trap 4; M2 (b)5(iv) |
| 07:45-08:30 pause and the uncross | M1 trap 4 (:384-392; axis skips the pause, no OFI term bridges it, side-N count of the 08:30 batch as a run-stage check, one frozen choice for SW/RF); M3 a.4 (:74-75, outside every label) |
| settlement | M3 e.2 rule 2 (:319-323; spans end 13:13); M1 trap 5; L.c |
| ts_event | M1 trap 1 (:369-373; ts_recv clock, +50 ms shift test, future-scramble); L.d drop-and-count rule; N5 |
| a bar that closes after t | M2 (b)5(i) (:249-251; rule B, +1-minute shift test); N12(b): confirm the stamp convention before the freeze |
| cross-market bar stamps | M2 (b)5(ii) (:252-254); (iii) same-minute news; staleness limit (:483-486) |

Also listed with tests: latency (M1 trap 2, M3 c.5.1), trailing references (M1 6), non-book records (M1 7), side N
(M1 8), the seasoned proxy (M1 9; add the B1 path), fill attribution (M1 10; B2), releases (M1 11, M3 rule 3),
implied liquidity (M1 12), sigma(D) from D (M3 a.6.1), barriers on bars (a.6.2), mid labels (a.6.3), post-hoc label
or kappa (a.6.4), prior exposure (a.6.5), data-derived dead zone (b.5.1), spread at t (b.5.2), class reweighting
(b.5.3), fills at placement (c.5.2), side-N fills (c.5.3), variant subsets (c.5.4), post-hoc W (c.5.5), decisions
after t (d.5.1), overlapping holds (d.5.2), changed re-entry (d.5.3), windows from data (e.4.1), unscheduled events
(e.4.2), rescheduled releases (e.4.3), roll from volume (e.4.4), stale limit bands (e.4.5), M2 (a)5 (i)-(v) and
(b)5 (iii)-(vi). Missing or to sharpen: N12 (a) DST, (b) bar-stamp precondition, (c) partial-batch T counts,
(d) MBP-1 bad-book persistence (S2).

## Check 4: verdicts against their evidence

- M1 (a) carry 8 / adapt 2 / drop 2: follows from the schema pages (verified quotes). (b) 5-minute minimum: follows
  from the stated criterion; with DF34's measured 76.2% day share the quietest date gives 0.104 (L.a), so the
  criterion is met at the 5th-percentile date, a lead choice L.a states. (c) MBP-1 in both windows: follows; the
  exposure-of-dates argument is V50 item 4 (verified at E.32b recs :596); the "derived from MBO" step is an
  inference (N6). (d) traps: complete subject to B1, B2 and N12. No statement rests on an earlier ZL outcome.
- M2 (a) USE the ZL-dependent crush residual with the origin split: follows. (b) leaders from bars: follows and is
  decisive on the shared facts (no ZS or ZM book for the test window is owned or priced). (c) CL excluded: follows
  (G17 exposure of the test bars, no intraday evidence found after three queries, same family at a neighbouring
  horizon); N11 on wording. (d) report-only VECM diagnostic: follows; the optional early kill is correctly flagged as
  a selection step. (e) "weak, mildly negative evidence": a reading, not an overclaim; the 2.5% prior is left to the
  lead. (f) the model rule is reserved; S3 fix.
- M3 (a) F15 F30 F60 T15 T30: follows; T60 out is a judgment with four stated reasons and an explicit "admissible
  on every timing rule". (b) dead zone = spreads + 2f with no slippage term: consistent with E.32 B-13 (verified at
  brief :5429) and P3.2 (:263, no depth walk). (c) market execution at L = 1 s, variants (ii)/(ii-b) report-only:
  follows; the M6 table is stylised and says so. (d) caps 17/8/4: follows from P3.8 and the grid; L.b adopts.
  (e) exclusions: FOMC and the limit-band source are correctly left to the lead; EIA/EPA as strata is the causal
  choice. (f) weights: follows P3.7.
- M4: reproduction verified independently; "N barely matters" (+1.5% over B 0..300) right; "trade rate and
  dependence matter" right; K2 analysis right and L.b adopts the measured form (N13); Holm never binds (z 2.902
  against t 4.86) right; D2 right, with the model difference against P7.2 correctly explained. The E.33 e80 figures
  (:159-165) are ZM aggregates from a RETURN summary, within RULES 3.
- L.a-L.e: arithmetic right; S1 wording; S2 one declaration missing; L.e consistent with M1 4.3 and M4 (a).

## Check 5: citations (79 greps; cite_check.out)

66 of 79 quotes sit at the cited line; the other 13 are present but wrapped across lines or drifted (listed in N10);
none is missing or misquoted. Explicit sample:

| cited | found | result |
|---|---|---|
| M1: Databento MBP-1 "provides every order book event that updates the top price level" (pages/schemas_mbp-1.md L6) | L6 | verbatim |
| M1: MBP-1 side "sell aggressor in a trade" (L21) | L21 | verbatim |
| M1: "are simply derived from MBO data" (schemas_whats-a-schema.md L77); "losslessly on the client side" (L79) | L77, L79 | verbatim |
| M1: GLBX "such as MBP-1 and Trades" (L42); "normalized into one" (L57); "modify the orders" (L62); "normal for order books to be locked or crossed" (L104); "publishing the merged top-of-book" (L113); MDP 2 "set to the same value as" (L299); "MBP-10" (L315) | same lines | verbatim |
| M1: GLBX implied trades "normalized with side set to None" (L70-71) | L70-71, split by a markdown link | verbatim |
| M1: E.32 brief CRS :3821, CKS :3810 and :3812, XGH :3814, Lillo-Farmer :3905, Patzelt :3911, Volkenand :4350, Jin :4351 | same lines | verbatim |
| M1: ZM top-decile R2 0.0120 (brief :3663) | :3663, h 5 row | verbatim |
| M1/M2: V50 "not a clean holdout" (E.32b recs :595-596) | :596 | verbatim |
| M2: Janzen and Wang "has broken down" (brief :1500); Huth and Abergel (:4693); Boero (:5071); Adrangi (:1796); Liu and Sono (:1798); Avileis and Swanson (:1802, wrapped) | same | verbatim |
| M2: farmdoc 2013 "7.55 pounds of soybean oil per gallon" (cited L51) and "priced biodiesel based on the cost of soybean oil" (L89-94) | L52, L95 | verbatim, 1-3 lines off |
| M2: farmdoc 2023 "lagged in the second half of 2021" (cited L165-167) | L171 | verbatim, 4 lines off |
| M2: Kristoufek "even at high frequencies" (L38-39), "transmitted into rapeseed oil prices" (L80-81) | L39, L82 | verbatim |
| M2: Zhou "the more soybean will Granger cause soyoil" (cited 821-822, 880); "even more significantly Granger cause" (881-882) | 880; 893 | verbatim, second 12 lines off |
| M2: Rechner and Poitras "-0.035 (-1.70)" (L278), "-0.08935 (-2.95)" (L356) | L283, L362 | verbatim, 5-6 lines off |
| M2: seal "for the window was ever bought or read" (test_seal.md :117-119) | :117 | verbatim |
| M3: EIA "standard release time and day of the week will be at 10:30"; FBN "4.50"; Fastmarkets "limit down during the overnight session" (pages/*.txt) | present | verbatim |
| M3: Avileis "by 3pm" (cited L395) | L408 | verbatim, 13 lines off |
| M3: brief :1965, :2325, :8814, :5495, :5429; protocol :363 (re-entry), "not a tuned threshold" (cited :285) | same; :283-284 | verbatim |
| M3: holding scope :921 (1.6135), :929 (0.573), :944 (10:50); recs :614 (five labels); DECISIONS :1040 (V50 trade-through), :1037 (V49) | same | verbatim |
| M4: protocol :721 (0.164882), :719 (Holm z), :731 ("1.60 x"), "stay sealed and untested" (cited :777) | same; :795 | verbatim, last 18 lines off |
| M4: recs :512 (N 838 row), :517/:519/:520 (N 938/1038/1138), :507 (V52), :552 (K2 1.8), :487 ("stays open until a test is registered"); holding scope :915, :944; E.33c_RETURN :194-195 (0.2309), :212 (embargo); E.32_RETURN :436 (D2) | same | verbatim |

## Recomputation table (quoted | recomputed | match)

M4_power_ZL.md
| item | quoted | recomputed (indep_m4_L.py unless stated) | match |
|---|---|---|---|
| weekdays disc / test MBO / test MBP-1 | 848 / 921 / 936 | 848 / 921 / 936 | yes |
| CBOT trade dates | 816 / 890 / 905 | frozen trade_dates rerun 816 / 890 / 905; DF34 816; 905 - 890 = 15 weekdays 2017-05-01..19 | yes |
| T_disc / T_test MBO / MBP-1 | 796 / 870 / 885 | 816-20 / 890-20 / 905-20 | yes |
| N 838: e(N), SR0, G3 (t), b_test, G4 (t), SR80_test, SR80 disc G3, SR80 disc binding | 3.2045, 0.1137, 0.1724 (4.86), 0.164882, 0.2007 (5.66), 0.1936, 0.2025, 0.2309 | 3.2045, 0.1137, 0.1724, 0.164882, 0.2007, 0.1936, 0.2025, 0.2309 | yes |
| N 1038 row | 0.1746 / 0.166967 / 0.2028 / 0.1957 / 0.2330 | same | yes |
| N 1138 row | 0.1755 / 0.167853 / 0.2037 / 0.1966 / 0.2338 | same | yes |
| MBP-1 N 838 | 0.163470 / 0.1993 / 0.1920 / 0.2294 | same | yes |
| 40-date burn-in | 0.2031 / 0.1959 (+1.2%) | 0.2031 / 0.1959; ratios 1.012 / 1.012 | yes |
| moments (sel / SR80_test) | 0.2059/0.1979; 0.2033/0.1956; 0.2070/0.1985; 0.2270/0.2151 | same | yes |
| tail effect | "+2 to 4%", "+11%" | +1.3 to +3.1% (binding), +1.1 to +2.6% (SR80_test); +13.1% / +11.1% | no (N2) |
| e80 N 838 caps 19/9/4 | 0.90 / 1.81 / 3.70 | 0.905 / 1.813 / 3.699 | yes |
| e80 h30 n 1 / 2 / 4 | 5.44 / 3.85 / 2.72 | 5.440 / 3.847 / 2.720 | yes |
| e80 B 200 cells (from rounded SR80_test) | 0.91, 1.83, 3.74; 5.50 / 3.89 / 2.75 | 0.915, 1.833, 3.739; 5.499 / 3.889 / 2.750 | yes |
| gross and sigma shares | 6.2-7.8 ticks; 0.22-0.28 sigma_30 | 6.23 / 7.82; 0.222 / 0.278 | yes |
| K2 1.8 by budget | 1.81, 1.82, 1.83, 1.84; MBP-1 1.80, 1.83 | 1.813, 1.820, 1.828, 1.842; 1.798, 1.826 | yes |
| K2 item 1 ratio; item 2 | 1.037; n > 5.2; 1.39 at n 8 | 1.0367; 5.159; 1.394 | yes |
| Holm K 9 | 2.539 / 2.773 / 2.902; f > 1.67 | 2.539 / 2.773 / 2.902; 1.675 | yes |
| D2 multipliers N 838 | 1.602 / 1.511 | e/2 = 1.602; e sqrt2/3 = 1.511 | yes |
| D2 simulation (seed 20261029, 4000 reps; 20261030, 2000) | table :252-262 | m4_out.md rerun identical | yes |
| gap SD | sqrt2 x 0.034 = 0.048 | 0.0485 | yes |
| kurtosis 3/p | 6 at p 0.5 | 6 | yes |

L_lead_reconciliations.md
| item | quoted | recomputed | match |
|---|---|---|---|
| L.a T a minute / n in 5 min / iid SD (quiet, p5, median) | 18.39 / 91.9 / 0.104; 32.46 / 162.3 / 0.078; 50.47 / 252.3 / 0.063 | same | yes |
| L.a book events a second; F_LAST share | 6.8; 188,782 x 0.899 = 169,700 | 6.82; share 0.8989, 169,688 | yes |
| L.a source counts | 188,737 / 168,917 / 19,195 / 6,998 (E.32 DF); 188,782 / 19,206 / 12,352 / 76.2% / 70.3% (DF34) | DF34 :127, :137-146 verified; E.32 DF :238-262 as cited by M1 | yes |
| L.b caps | 17 / 8 / 4 (E.32b 19 / 9 / 4) | floor((277-h)/(h+1))+1 = 17 / 8 / 4; min(20, 290//h) = 19 / 9 / 4 | yes |
| L.b e80 N 838; N 1038 | 0.96 / 1.92 / 3.70; 0.97 / 1.94 / 3.74 | 0.956 / 1.923 / 3.699; 0.967 / 1.944 / 3.739 | yes |
| L.b "never binds at h >= 15" | stated | true for F labels only | no (S1) |
| L.c latest entries | 12:57 / 12:42 / 12:12 CT | 13:12 - h | yes |
| L.d counts | 230,475 (0.146%); 354; 7; 848 / 848 | DF34 :106-108 | yes |
| L.e | 890 / 870; 905 / 885; 15 sealed dates | same | yes |

M3_labels_ZL.md
| item | quoted | recomputed | match |
|---|---|---|---|
| starts a date | 263 / 248 / 218 | 278 - h | yes |
| n_max^F; same-minute alternative; E.32b cap | 17 / 8 / 4; 18 / 9 / 4; 19 / 9 / 4 | same | yes |
| e80 at n_max | 0.956 / 1.923 / 3.699 | same | yes |
| dead-zone table (d/sigma, P(dead), q*) h 30 at 1.88 | 0.0669, 0.0533, 0.5419 | 0.0669, 0.0533, 0.5419; whole table by rerun | yes |
| c_f rows reproduce E.32b p_be norm | 0.573 / 0.553 / 0.539 | 0.5732 / 0.5531 / 0.5390; holding scope :929 | yes |
| barriers b; USD; b/sigma_h | 21.38 / 30.23 / 42.76; 128 / 181 / 257; 1.050 / 1.076 / 1.119 | same | yes |
| P(vertical) series; sim; E[min(tau,h)]/h | 0.371; 0.415 / 0.439 / 0.475; 0.426 / 0.447 / 0.484; 0.706-0.774 | rerun identical; k=1 series 0.3708 by hand | yes |
| p* barrier exits | 0.544 / 0.531 / 0.522 | 0.5 + 1.88/(2b) | yes |
| latency SD | 0.713 / 0.390 | 5.52 sqrt(1/60), sqrt(0.3/60) | yes |
| M6 table and identity | V_M - V_L = 0.445 = OC - p s | 0.515 - 0.070 = 1.238 - 0.793 = 0.445; rerun identical | yes |
| FOMC starts; share | 15; about 0.2% | 15; 26 x 15 / 209,348 = 0.19% | yes |
| EIA | 63 of 248; about 5% | h + 33 = 63; 63/248/5 = 5.1% | yes |
| limit band example | 63.30 / 56.70; 330 ticks; 8.6 / 11.7 / 16.2 sigma; 350; 290 | same | yes |
| release-day rows and n_eff | 48 / 63 / 93 excluded; 215 / 185 / 125; 16.27 / 8.13 / 4.07 | same; 243 vs 244 minutes (N8) | yes |
| rows and n_eff over 796 | 209,348 / 197,408 / 173,528; 14,699 / 7,350 / 3,675 | same | yes |
| 15:10 - 13:13 | 117 min | 117 | yes |
| T60 cost in N | 1038 -> 1078; 900 -> 910 | 838+200+40; 838+62+10 | yes |

M2_F09_ZL.md
| item | quoted | recomputed | match |
|---|---|---|---|
| ticks per crush cent; USD; per ZS tick; per ZM tick; b_S; b_M | 9.09; 54.55; 2.273; -2.000; 0.0909; -0.200 | same | yes |
| contract arithmetic | 5,454.5 bu; 1.091 ZS; 120.0 t = 1.200 ZM; 9.82; 10.8 | same | yes |
| C example | 196 | 660 + 836 - 1300 | yes |
| s_L* table | 0.5236 (1.047 ... 0.0873) | same (json) | yes |
| gross at s_L 1, D 1 | 4.545 / 6.818 / 7.955 | same | yes |
| ZM comparison | 0.70; 0.350 c vs 0.262 c; 25% cheaper | 0.6996; 0.3498 / 0.2618; 0.748 | yes |
| half-life table | 0.405 ... 1.646 | same | yes |
| K2 edge | 0.461 c/bu; D needed 0.92/0.61/0.53; 1.84/1.23/1.05; 3.69/2.46/2.11 | 4.19 x 0.11 = 0.4609; same | yes (N9) |
| VECM illustration | -0.0387; 0.9613; 17.56; 0.517 / 0.142 / 0.341; -1.292 | same | yes |
| hl from phi | 6.58 / 13.51 / 22.76 / 68.97 | same | yes |
| (b) example | 0.446; 0.262; 2.165; 0.0771; 1,516; 1.9 a date | same | yes |
| ZS sigma_15 implied | 12.045; 3.011 c; 27.4; 1.34 | same (3.11 from brief :1382) | yes |
| bounce SD and shares | 1.594; 13 / 8 / 6 / 29% | two endpoints: 2.254; 19 / 11 / 8 / 41% | no (S4) |
| cost per sigma | ZM 0.092; ZL 0.085 | 0.0922; 0.0847 | yes |
| spread 2.06 | c_f 3.44; s_L* 0.757 | same | yes |
| (c) feedstock | 0.000755 USD/gal per tick; 13.2 ticks per 1 c/gal | 7.55e-4; 13.25 | yes |
| (e) illustration | 0.022; 0.109; 9% | 0.02/0.92; 0.10/0.92; 1.087 | yes |
| (f) counts | 12 rules; 100 ML | 4 x 3; 2 x 5 x 10 | yes |

M1_F10_ZL.md
| item | quoted | recomputed | match |
|---|---|---|---|
| k_all, k_top, z90 | 0.7979, 2.0627, 1.6449 | same | yes |
| R2 table | 0.0214/0.00321/0.00609; 0.0113/0.00169/0.00523; 0.0061/0.00091/0.00595 | same | yes |
| c_f / sigma_30 | 0.085 | 0.0847 | yes |
| R2_pred at rho 0.05 / 0.1 / 0.2 | 0.0016 / 0.0065 / 0.026 | same | yes |
| "3 to 6 times lower" | stated | 3.7 / 7.1 / 13 (c_f column); 2.0 / 2.3 / 2.0 (c_f + e80) | no (N4) |
| rate tables at 0.70 / 0.83 / 1.00 | :258-260 | rerun identical | yes |
| long-memory SD table | :277-281 | rerun identical | yes |
| OFI example | 60; 2.0 ticks = USD 12; 0.2 tick at rho 0.1 | same | yes |
| TI example | 0.20; SE 0.060; "two iid standard errors" | 0.0603; 3.3 SEs | no (N3) |
| proxy example; lambda | 8, 0, 1.0; 1.25 | same | yes |
| side N share; records per event | 10.04%; 1.113 | 1,608,719 / 16,019,898; 158,046,466 / 142,061,153 | yes |
| costs | 23.36 / 40.96 / 17.60 / 21.48 / 1.88 | same | yes |
| 5-minute book updates | about 2,400 | 8 x 300 | yes |
| pause reach | 07:15-07:45 | 07:20 (30 min), 07:35 (15 min) | no (N7) |

## Not finished or not verified

- No market data was opened, so nothing here confirms the ZL spread, touch depth, day-session share per date, the
  bar-stamp convention or the T-record fill-reduction branch (B2); those are DataFacts or run-stage counts, as the
  M files say.
- The trade-date counts 816 / 890 / 905 rest on the frozen trade_dates and the grains holiday calendars; I checked
  the weekday counts and the cross-checks (DF34's 816, E.32 P9's 890), not the calendars' holiday lists.
- The E.32b recs figures quoted by the M files (option A/B counts, the USD cost estimates, the 2.5% prior, the
  0.4995 census price) were checked as citations where listed above, not re-derived.
- Pages were read by grep only; no web fetch was needed (every cited page was on disk).

