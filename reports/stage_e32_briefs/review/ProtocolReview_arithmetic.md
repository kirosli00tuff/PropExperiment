# ProtocolReview (arithmetic lens): reports/stage_e32_discovery_protocol.md DRAFT v0.2

Reviewer: ArithmeticReviewer-FableXHigh (claude-fable-5-1, xhigh), Stage E.32 ProtocolReviewer, lens "arithmetic of
the budget and thresholds". Written 2026-10-27 07:05-08:05 PDT. Object: the 647-line protocol at sha256
34dde904a4cf76d9... (first 16 hex of `sha256sum reports/stage_e32_discovery_protocol.md` at review time). I did not
write the protocol and assumed it wrong until checked. No market data was opened; no web access was used
(work_protocol_arithmetic/log.tsv). Holdout status at start and end: sealed_ok true, unlocks_logged 0.

Method. Every number of P0.4, P1.4, P3.1, P4 (feature counts), P5, P6.1, P7, P8 and P9 was recomputed BEFORE
running p7_final.py, with my own scripts under reports/stage_e32_briefs/review/work_protocol_arithmetic/:
a1_calendar_folds.py (trade dates from the program calendars by my own walk, burn-in, folds, embargo reach, decision
grid, P5 arithmetic; output a1_out.txt), a2_thresholds.py (own closed forms with statistics.NormalDist for E[max SR],
DSR, Mertens se, power, per-trade edge, Bonferroni/BH/BY/Holm, the P4.2 binomials; and the same through the program's
funnel.multiple_comparisons; output a2_out.txt), a3_program_dsr_power.py (Monte Carlo of the test's pass probability
under the program verdict's own DSR variance rule, V14 c; output a3_out.txt). Then p7_final.py was rerun to
p7_final_rerun.md: byte-identical to the committed p7_final_budget300.md.

## Findings table

| ID | Section, line | Severity | Finding (one line) |
|---|---|---|---|
| AR-1 | P7.2 l.554-563, P9 l.621-624, P8 l.594 | BLOCKING | The test power statements (0.993 at s = 0.25; 80% power at 0.1936) describe only the protocol-added DSR at V = 1/(T_test - 1). P9 also requires the program verdict's DSR, whose V (V14 c) is the population variance of the 2-3 tested Sharpes. With any null or weaker companion that variance makes SR0 = 1.51-1.60 x s, above s for every s: P(pass) = 0.000 for a true daily Sharpe 0.25 or 0.30 beside one or two nulls. The stated power is therefore not the power of the P9 bar |
| AR-2 | P6.2 l.490; P8 G5(c) l.586; P8 G4 l.582 | SHOULD FIX | "SR_d = mean/SD (sample SD)" contradicts "as screening/stage_e_verdict.py moments() computes them" (population SD). The two readings differ by a factor 0.999372: 1.26e-4 in SR at G4, larger than the ranking's tie tolerance 1e-4 and 10^5 times G7's agreement tolerance; a configuration at the G4 margin passes under one reading and fails under the other |
| AR-3 | P7.1 l.546 | SHOULD FIX | "the registered N at E.33's start is used in every DSR" reads as 538 (N at the start, before registration) or 838 (after). G3 is 0.1678 (t 4.73) at 538 and 0.1724 (t 4.86) at 838; the test DSR bar 0.1605 against 0.1649. P8 G3 says "after E.33's registration"; P7.1 must say the same |
| AR-4 | P7.2 l.565 | SHOULD FIX | "the test's Holm step 1 at K = 9 z 2.539" holds only for a one-member Tier A. holm_tier_a's step-1 threshold is alpha_K / m = 0.05/(9 m): z 2.773 at m = 2, 2.902 at m = 3. The conclusion (below t > 3.0) stands |
| AR-5 | P6.1 l.482 | SHOULD FIX | "20 = the longest feature look-back in trade dates" is wrong by one date: F1.7's sd_g and F4.7's sd_gap at date D are SDs over gC(D-20..D-1), and gC(D-20) uses the 13:15 close of D-21. The first non-embargoed training date L+21 therefore reads block k's last close through a normaliser. Immaterial in size (one close price inside a scale), but the sentence and LT3's "exceeds every look-back" are false as written |
| AR-6 | P7.2 l.559-563 | NOTE | "is selected and then passes with probability" is P(SR_d >= max(G3, G4)) x P(pass b_test) only: G1, G2, G5 and the 0.70 correlation filter are not in it, and the per-trade column assumes trades on every date while G1 admits 50% of dates (x 1.41 on mu at the floor: 1.22 -> 1.73 ticks at h 15, n 4) |
| AR-7 | P4.2 l.419-423 | NOTE | The 20-run null proof cannot establish "<= 0.05": after 1 non-empty Tier A in 20 the exact 95% upper bound on the rate is 0.216; a true rate of 0.15 passes the proof with probability 0.18, 0.10 with 0.39. The guarantee is the analytic 1.7e-4; say so |
| AR-8 | P4.2 l.424-427 | NOTE | "at least 14 of 20 seeds (P(at least 14 \| 0.8) = 0.91)" tests power >= 0.8, not the "stated power of selection 0.91": at power 0.91 the pass probability is 0.999. The 0.91 in the parenthesis is a coincidence of numbers |
| AR-9 | P6.4 (ii) l.509 | NOTE | "within min(60 s, h/5)": with h in minutes h/5 is 1-12 minutes, so the minimum is 60 s for every horizon; state the intended unit (if h/5 is meant in minutes, write "60 s") |
| AR-10 | P7.2 l.553, 552-558 | NOTE | "kurtosis 6" is raw kurtosis (excess 6, raw 9, gives 0.1762 not 0.1756); add "raw". The SR values are 4-decimal displays: the program's DSR at exactly SR = 0.1724 is 0.94994 (fails), at 0.1725 passes; P8 rightly gates on the function |
| AR-11 | P5 l.444, 470 | NOTE (feasibility lens) | "7 worker processes" x "num_threads at most min(8, cpu//2)" allows 56 threads; the 1-4 h wall estimate (4.0-24.0 CPU-h / 7 = 0.57-3.4 h) holds only with num_threads 1 per process, which is also what CLAUDE.md's cap (8 threads; 14 overnight) permits |
| AR-12 | P10 l.638 | NOTE (feasibility lens) | The E.33 prompt gives two times: 01:00 PDT (line 43, work stops) and 00:00 (C3, line 157-158: the run cutoff after which only whole families finish). P10 cites 01:00 only |
| AR-13 | P6.3 l.497-499; P9 | NOTE | 796 // 8 = 99 dates per block: the last 4 OOF dates are outside the PBO; on the test 870 // 8 = 108, 6 dates outside. The program does this; say it |
| AR-14 | P8 G5 l.584-588 | NOTE | December 2020 holds 2 OOF dates (burn-in ends 2020-12-29), so "each of the 39 months" includes a 2-date month and the first quarter has 40 dates (others 59-65); harmless, state it |
| AR-15 | P8 G3 l.579; P9 l.621-624 | NOTE | G3 and the protocol-added test DSR say ">= 0.95"; the program's _chain_verdict uses "> 0.95". Measure zero, but E.33's two implementations should copy one sign |
| AR-16 | P7.2 l.552-558 | NOTE | G4 is computed from the configuration's own moments but P7.2 reports it for normal moments only; at skew -0.5, raw kurtosis 6 it is 0.2030 (beside G3's 0.1756) |

Counts: BLOCKING 1, SHOULD FIX 4, NOTE 11; 16 findings. Items checked and found sound: 122 (the coverage list below).

## Findings in detail

### AR-1 (BLOCKING). The test's power is stated for a bar that is not P9's bar

Text as written. P7.2 l.554-556: "The test (T_test = 870, P9): daily t > 3.0 is SR 0.1017; the protocol-added DSR
>= 0.95 at N 838 with V = 1/(T_test - 1) is SR 0.1649 (t 4.86); b_test = 0.1649 (2.62 annualised); 80% power needs a
true daily Sharpe of 0.1936." l.562-563: "a configuration whose true daily Sharpe is s in both windows is selected and
then passes with probability 0.03 at s = 0.15, 0.11 at 0.17, 0.42 at 0.20, 0.91 at 0.25." P9 l.621-624: "(1) the
program verdict exactly as coded (... DSR > 0.95 at the list's program N with the population variance of the Tier A
Sharpes if two or more, else of Tier A and Tier B, V14 c; ...) and (2) the protocol-added DSR >= 0.95 at the same N
with V = 1/(T_test - 1). A Tier A configuration passes only if both pass."

What is wrong. The power table is computed at b_test = max(t-bar, protocol DSR bar) = 0.1649 (p7_final.py
`power(s, b_test, t_test)`), i.e. for component (2) alone. Component (1)'s DSR uses, as coded
(screening/stage_e_verdict.py l.216-229, 537-553: `dsr_over = a_series if len(a_series) >= 2 else run_series`,
`variance = statistics.pvariance([moms[k]["sharpe"] ...])`, benchmark `expected_max_sharpe(n_trials, variance)`),
V = the population variance of the 2-3 tested daily Sharpes. That variance is the dispersion of the tested list, not
the null sampling variance 1/(T - 1) that b_test uses. Closed form: with k tested series of which one has true daily
Sharpe s and the rest 0, pvariance ~ s^2 (k - 1)/k^2, so SR0_program = 3.205 x s x sqrt(k - 1)/k = 1.60 s (k = 2) or
1.51 s (k = 3) (3.205 is the E[max] multiplier at N 838: (1 - gamma) z(1 - 1/838) + gamma z(1 - 1/(838 e)) =
0.4228 x 3.0374 + 0.5772 x 3.3270). SR0_program exceeds s for every s, so the real member cannot reach DSR > 0.95
however strong it is. Two real but unequal members behave the same way: k = 2 with (s1, s2) gives
SR0_program = 3.205 |s1 - s2|/2; at (0.25, 0.15) the better one needs 0.216 and passes with about 0.84, at (0.25,
0.10) it needs 0.296 and passes with about 0.09.

Monte Carlo (a3_program_dsr_power.py, 20,000 draws per row, observed Sharpes ~ N(mu, Sigma) with
Sigma_ij = rho (1 + 0.5 mu_i mu_j)/(T - 1), T 870, N 838; a3_out.txt):

| tested list, true daily Sharpes in the test window | rho | P(program DSR) | P(t > 3 and protocol DSR) | P(both) |
|---|---|---|---|---|
| Tier A 3: 0.25, 0.25, 0.25 | 0.0 / 0.5 | 0.961 / 0.995 | 0.993 | 0.961 / 0.990 |
| Tier A 3: 0.25, 0.25, 0.00 | 0.0 / 0.5 | 0.000 / 0.000 | 0.993 | 0.000 |
| Tier A 3: 0.25, 0.00, 0.00 | 0.0 / 0.5 | 0.000 | 0.994 | 0.000 |
| Tier A 3: 0.20, 0.00, 0.00 | 0.0 / 0.5 | 0.000 | 0.848 | 0.000 |
| Tier A 2: 0.25, 0.00 | 0.0 / 0.5 | 0.000 | 0.993 | 0.000 |
| Tier A 1 + Tier B 2 near-duplicates: 0.25, 0.25, 0.25 | 0.9 | 1.000 | 0.994 | 0.994 |
| Tier A 1 + Tier B 2 nulls: 0.25, 0.00, 0.00 | 0.3 | 0.000 | 0.993 | 0.000 |
| Tier A 1 + Tier B 2 nulls: 0.30, 0.00, 0.00 | 0.3 | 0.000 | 1.000 | 0.000 |

So the protocol's "0.91 at s = 0.25" is the power only when every tested series has about the same true Sharpe. In
the cases the search is designed to produce (up to 3 members decorrelated at 0.70, some of them false positives
selected at discovery t about 4.9; or one real member with two Tier B companions that were chosen "whatever their
gates") the pass probability of the P9 bar is 0. The design notes (work/lead/design_notes.md "Program bar" item)
foresaw the opposite direction only ("With 2-3 correlated candidates the V14(c) variance can be tiny"), which the
protocol-added DSR guards; this direction is unguarded. Note also that P8's Tier B rule decides which case applies when
Tier A has one member: near-duplicates (the two next-best by SR_d are typically neighbouring grid points of the same
set and label, correlated above 0.70) give the benign small-variance case; anything else gives the fatal one. The
composition of the test list is thus a lever on the program DSR's V, which a reader of P7.2 cannot see.

Why BLOCKING. Under the brief's letter this could be read as SHOULD FIX (a wrong power statement; no number enters a
verdict). I rate it BLOCKING because the stage prompt requires P8 to carry "the power check for the 43-month test
window", G4 and the planted-signal proof are calibrated against b_test, and the program would spend its one clean
window on a bar whose pass probability for a genuine 0.30-daily-Sharpe candidate is 0 whenever a companion is weaker.
The decision how to resolve it is the user's (V14 c is a user decision), not mine or E.33's.

Proposed fix (text; the choice between (a) and (b) is reserved for the user before the P9 registration). Replace
P7.2 l.554-556 with: "The test (T_test = 870, P9) applies two DSRs. (2), the protocol-added DSR >= 0.95 at N 838 with
V = 1/(T_test - 1), is SR 0.1649 (t 4.86); with t > 3.0 (SR 0.1017) this gives b_test = 0.1649 (2.62 annualised), and
80% power against b_test needs a true daily Sharpe of 0.1936. (1), the program verdict's DSR, uses V = the population
variance of the tested Sharpes (V14 c), which is not known before the read: when the tested series have about equal
true Sharpe it is looser than (2); when one member is real and another null, SR0 = 1.51-1.60 x the real member's
Sharpe and (1) cannot be passed (a3_out.txt). The power figures below are for (2) and are an upper bound on the power
of the P9 bar." Then either (a) the user amends V14 c for this program so that the test's DSR variance is
1/(T_test - 1) (the protocol-added DSR then IS the program DSR and the table is the power), or (b) P8 l.594-596 adds:
"Tier B's two series set the program DSR's V when Tier A has one member; with Tier A of two or three, the members set
it for each other. A member's pass therefore depends on its companions' test Sharpes (P7.2)." and P9 states the same
sentence beside "A Tier A configuration passes only if both pass."

### AR-2 (SHOULD FIX). Sample versus population SD in SR_d and t

Text as written. P6.2 l.490: "daily Sharpe SR_d = mean/SD (sample SD), skewness and raw kurtosis (as
screening/stage_e_verdict.py moments() computes them)". P8 G5(c) l.586: "the daily t of the series without that month
(mean/SD x sqrt(n)) >= 2.5". P8 G4 l.582 uses SR_d.

What is wrong. moments() (stage_e_verdict.py l.178-188) uses `statistics.pstdev` (population SD) and divides the
third and fourth moments by n. "sample SD" (divisor n - 1) and "as moments() computes them" cannot both hold.
SR_sample = SR_pop x sqrt((T - 1)/T) = 0.999372 SR_pop at T 796. At the G4 threshold 0.20070 the two readings differ
by 1.26e-4 (a2_out.txt), above the P8 ranking's tie tolerance 1e-4 and 10^5 times G7's 1e-9 relative tolerance for
E.33's two implementations. A configuration with SR_pop in [0.20070, 0.20083) passes G4 under the population reading
and fails under the sample reading. The t of G5(c) has the same two readings (program: t = mean/(pstdev/sqrt(n)),
funnel.multiple_comparisons.harvey_liu_zhu_verdict), and the P7.2 "t" values (4.86 = 0.1724 sqrt(796)) are on the
population convention. The thresholds of P7.2 (G3, G4) are in population units because deflated_sharpe_ratio and
required_sharpe take the population Sharpe.

Proposed fix. P6.2 l.490: "daily Sharpe SR_d = mean / population SD (statistics.pstdev), skewness and raw kurtosis,
all exactly as screening/stage_e_verdict.py moments() computes them (divisor n throughout); daily
t = SR_d x sqrt(n) (= funnel.multiple_comparisons.harvey_liu_zhu_verdict)". P8 G5(c): "(mean / population SD x
sqrt(n), the moments() convention)". P8 G4: add "b_test is p7_final.py's unrounded value at the registered N (0.16488
at N 838), not the 4-decimal display".

### AR-3 (SHOULD FIX). "The registered N at E.33's start" is two numbers

Text as written. P7.1 l.545-546: "N goes from 538 to 838 if no other stage registers trials first, and the registered
N at E.33's start is used in every DSR."

What is wrong. At E.33's start N is 538 (screening.trial_registry.current_n() = 538 at review time); after the
registration that the same sentence describes it is 838. The two readings give different gates: at N 538, SR0 =
0.1090 and G3 = 0.1678 (t 4.73); at N 838, 0.1137 and 0.1724 (t 4.86); the test DSR bar 0.1605 against 0.1649
(work_protocol_arithmetic/a4_n538_out.txt). P8 G3 l.579-580 says "N = the registered N after E.33's registration",
and p7_final.py uses N_PRIOR + budget. P7.1 contradicts them.

Proposed fix. Replace with: "N goes from 538 to 838 if no other stage registers trials first. The N recorded by
screening.trial_registry.current_n() immediately after E.33's 300 registrations (838 in that case) is the N of every
DSR in P7.2, P8 and P9."

### AR-4 (SHOULD FIX). Holm step-1 z at K = 9 depends on the size of Tier A

Text as written. P7.2 l.565: "the test's Holm step 1 at K = 9 z 2.539".

What is wrong. holm_tier_a (screening/stage_e_stats.py l.317-334) sets alpha_K = 0.05/K and the step-i threshold
alpha_K/(m - i + 1) over the m Tier A p-values; step 1 is 0.05/(9 m). z = 2.539 is m = 1; m = 2 gives alpha 0.00278,
z 2.773; m = 3 gives 0.00185, z 2.902 (own computation). All remain below t > 3.0, so "nothing is lost" (V14 b) holds
and no gate changes; the printed number is right for one case of three.

Proposed fix. "the test's Holm at K = 9 (step 1 alpha 0.05/(9 m) over m Tier A members: z 2.539, 2.773, 2.902 for
m = 1, 2, 3)".

### AR-5 (SHOULD FIX). The embargo is one trade date short of the gap features' reach

Text as written. P6.1 l.481-483: "the embargo, the 20 trade dates immediately after block k's last date (20 = the
longest feature look-back in trade dates: sigma_X, the trailing references, F1.3's 10 dates, F1.7's and F4.7's 20)".
P4.1 LT3: "the embargo (20 dates) exceeds every label's span".

What is wrong. Let L be block k's last date and L+1..L+20 the embargo. The first training date after it, L+21, has
sigma_X, the trailing references and C.5's Vbar over L+1..L+20 (clean) and F1.3's regression over L+11..L+20 (clean).
F1.7's sd_g and F4.7's sd_gap at L+21 are SDs of gC(D') and GAP(D') for D' = L+1..L+20, and gC(L+1) =
C(08:35 on L+1) - C(13:15 on L): the 13:15 close of block k's last date enters a training feature's normaliser. All
other features stay within 20 dates (a1_out.txt; the "window of k minutes" at 08:35 reaches into the overnight
session, which belongs to the same trade date). The spill is one close price inside a scale; it cannot plausibly
move an outcome, but the stated bound is wrong and LT3 would pass a test it should fail if written as "20 exceeds
every look-back".

Proposed fix. Either "the 21 trade dates immediately after block k's last date (21: the gap features F1.7 and F4.7
reach the previous date's close, so their 20-date SD spans 21 dates; every other look-back is at most 20)", with the
training-date counts 642/642/642/642/643/664 (fold 6 has no embargo), or keep 20 and add "(F1.7's and F4.7's SD at
L+21 reads one close of block k; accepted as immaterial)".

### AR-6 to AR-16 (NOTE)

AR-6. P7.2 l.562 says "is selected and then passes"; p7_final labels the column "P(select: SR_d >= max(G3, G4))".
Write "clears the SR threshold max(G3, G4) at discovery and then clears b_test" and add to l.559 "(trades on every
OOF date; at G1's floor of 50% of dates the per-trade edge needed is 1.41 times larger)".

AR-7. P4.2: 300 x P(Z > 4.865) = 1.7e-4 reproduces (the exact one-configuration null rate of DSR >= 0.95 is 6.2e-7).
Twenty runs with "more than 1 non-empty fails" accept a true rate of 0.05 with probability 0.74, 0.10 with 0.39, 0.15
with 0.18, 0.20 with 0.07; the exact-binomial 95% upper bound after 1 of 20 is 0.216. Suggested wording: "The proof
checks that nothing is grossly wrong (a rate above about 0.2 would show); the stated rate rests on the analytic
1.7e-4 and on the DSR gate, not on 20 runs."

AR-8. P4.2: P(X >= 14 | n 20, p 0.8) = 0.913 reproduces; P(X >= 14 | 0.91) = 0.999. The rule tests "power at least
0.8" and would pass a pipeline with power 0.8 nine times in ten; say "the proof's acceptance rule is set at power
0.8, below the stated 0.91, so that a pass is not a coincidence of seeds". The planted size 0.25 x 12.20 / 2 = 1.525
ticks net reproduces ("about 1.5").

AR-9. P6.4 (ii): min(60 s, h/5) = 60 s for h = 5, 15, 30, 60 if h/5 is in minutes (60, 180, 360, 720 s). Either
write "within 60 s" or give h/5 in seconds (1-12 s, which would make the window almost never fill).

AR-10. P7.2 l.553 "kurtosis 6": raw (the program's convention; p7_final passes kurt = 6.0 to deflated_sharpe_ratio).
Add "raw". Add after l.552: "SR values are 4-decimal displays of p7_final.py; the gates apply the functions
(the DSR at exactly SR_d = 0.1724 is 0.94994)".

AR-11 (for the feasibility lens). P5 l.444 and l.470: 7 processes x num_threads up to 8. The CPU-hour arithmetic
(1,080 x 10-60 s = 3.0-18.0; 720 x 5-30 s = 1.0-6.0; total 4.0-24.0 CPU-h; / 7 = 0.57-3.4 h, printed as "about 1-4")
is right; the wall figure needs num_threads 1 per process to stay inside CLAUDE.md's cap.

AR-12 (for the feasibility lens). P10 l.638: add "(runs stop by 00:00 PDT per the prompt's C3; the stage by 01:00)".

AR-13. P6.3: "8 blocks of n_days // 8 dates" = 99 dates, 792 of the 796 OOF dates (the last 4 are outside the PBO
blocks, as the program's blocks() does); on the test 108 x 8 = 864 of 870.

AR-14. P8 G5: the burn-in ends 2020-12-29, so 2020-12 holds OOF dates 12-30 and 12-31 only; the Dec-Feb 2020/21
quarter has 40 OOF dates (others 59-65, a1_out.txt). G5(c)'s leave-one-month-out t for 2020-12 is the full-series t.
State "(December 2020 holds two OOF dates)".

AR-15. P8 G3 and the protocol-added test DSR: ">= 0.95"; stage_e_verdict._chain_verdict: `d_value > DSR_MIN`. Pick
">" to match the program function E.33 is told to call, or state that equality passes.

AR-16. P7.2: G4 at skew -0.5, raw kurtosis 6 is 0.2030 (G3 0.1756); worth one clause since G4 uses own moments.

## Coverage: checked and found sound (122 items)

P0.3 (6): decision-grid counts 273/263/248/218 by enumeration, last span end 13:12:01 <= 13:13:00 for every h; tick
values ZM 10, ZS 12.50, ZL 6 USD; fee 0.528 = 5.28/10 (planner_research_notes.md l.50); L 1.000 s; trade date
[D-1 16:00, D 16:00); sigma_X(D) definition closed under 20 dates.

P0.4 (6): sigma_1m 3.15 (A0_contract_stats.md l.115); sigma_h = 3.15 sqrt(h) -> 7.04/12.20/17.25/24.40; 1.59 =
0.528 + 1.000 + 0.062 (stage_e28_ranking.md l.130 row 6: 0.59/1.59; M3 e.2 l.482-490 decomposition); E.31 gross
edges -0.970/-0.287/-0.252 (E.31_RETURN.md l.190); the 1.59 is used in the protocol only for prose hurdles (P2, P3.1),
never in a label or gate (labels use f = 0.528 and the realised spread).

P1.1, P1.3, P1.4, P1.5 (10): 156 = 4 x 39 files, 24,234,707,848 bytes (F l.352); 816 trade dates = 848 weekdays
- 32 full closures by my own walk over data.calendars.grains and the hist2010 calendar (closure list printed in
a1_out.txt; Juneteenth 2022-06-20 and 2023-06-19 included, 2021-06-18 correctly not); equals F 3.1's measured 816 and
X1 Table C's 816; burn-in = 2020-12-01..2020-12-29, T_disc 796; E.31's exclusion counts 23/20/4/5 and 764 (X1 l.233);
overnight 2 vs 71 contracts a minute (A0 l.115) and 17% (1 - 0.83, READER_BRIEF l.50); X1_verify 311/303/8/0
(l.273); ADV 77,862 vs 36,690 (READER_BRIEF l.50-51).

P2 (10): 49 USDA and 39 NOPA days (R4 l.586, R3a l.632); 24.4/sqrt(24) = 4.98, 2 SE = 10.0 ticks (R4 l.245-248);
10.7-33 ticks (M5b l.441, 586); 3.46 and 4.90 ticks at one trade a date (P7.2 table rows h 30 n 1, h 60 n 1);
(2 x 24.40/1.59)^2 = 942 (R3a l.623); 0.70 = 1.59/4.545/0.5 and A's 0.70/0.47/0.40 (MathReview_A l.143); 0.22 c
per ZM tick and 2.2 = 44/2000 x 100; 2-34 weights (M4 l.362, 728); BCOM 3.5% (R3b l.298); 2 bp (R3b l.343).

P3 (9): 6 label types; the 1-minute hit rate 0.816 = 0.5 + 1.59/(2 x 3.15 x 0.7979) (M3 f.3 l.640, 660; my 0.8163;
also 0.6415 at h 5, 0.5817 at h 15); N_long + N_short = -s(t+L) - s(t+h+L) - 2f < 0 re-derived; TB barrier
b = sigma sqrt(h) with kappa 1 matches M3's +-sigma_h row; entry cap 20 (stage_e_runner.py l.36-37); the grid's last
mark 13:12 - h respects rule 2 with L = 1 s; P3.6 rule 3 window arithmetic; P3.7 weights sum to about the independent
labels (definition only); X_D = 0 on no-trade dates matches the program's series unit.

P4 (8): feature counts C 15 (C.11-C.14 four flags), F1 8, F2 11 (3+3+1+2+2), F3 12 (3+9), F4 13 (5+8); S1 23, S2 26,
S3 27, S4 28, S5 59; F2.7's identity -dC_5/2.2 = (dZS - 11 dZL)/2.2 - dZM re-derived; every look-back other than
F1.7/F4.7 within 20 trade dates (AR-5).

P4.2 (5): 300 x P(Z > 4.865) = 1.72e-4; P(>= 2 of 20 | 0.05) = 0.2642; P(>= 14 of 20 | 0.8) = 0.9133; planted
1.525 ticks; selection power at s 0.25 = 0.914 (AR-7, AR-8 are about what these establish, not the arithmetic).

P5 (12): 414,363,576 records (F l.391, X1 l.233) / 0.76 and 0.39 M/s = 9.1-17.7 min; RSS 125-394 MB (F l.383-384);
re-split (248,167,909 + 158,044,028) x 80 B = 32.50 GB (F l.398-399) and 56 + 35 = 91 s decode; 263 x 796 = 209,348
rows, x 59 x 4 B = 49.4 MB ("under 0.1 GB", "about 50 MB"); 1,800 = 1,080 LOGIT (5 x 6 x 6 x 6) + 720 LGBM
(5 x 6 x 4 x 6); rows per fit (796 - 133 - 20) x 263 = 169,109 ("about 170,000"); CPU-hours 3-18 and 1-6;
min_data_in_leaf 50h/200h = 250..12,000 rows; num_leaves 2^d = 4, 8; grid 6 + 4 = 10 points; run order covers all 300.

P6.1-P6.5 (12): 133 x 4 + 132 x 2 = 796; fold boundaries and embargo windows printed (a1_out.txt); fold 6 has no
embargo (no dates after); no training label overlaps an evaluation label because labels end by 13:13 on their own date;
P6.2's statistics list is computable from the series and trade list; PBO 8 blocks of 99 (program's blocks()); M5a's
null band 0.13-0.83 (M5a l.550); P6.4 fees Topstep 0.528, Lucid 0.560/0.920, Bulenox 0.572, MFFU 0.612, Tradeify
0.920 = M6 l.29-31 and l.457 (USD/10 each); P6.5 bootstrap constants (mean block 5, B 10,000, seed 20260923) =
stage_e_verdict.py l.95-97; reversed walk-forward k = 1..5 well defined; 43 months = 2017-05..2020-11.

P7.1 (3): 5 x 6 x 10 = 300; the ID list has 10 grid labels; 538 + 300 = 838 with current_n() = 538.

P7.2 (24): SR0 0.11365 (own closed form and expected_max_sharpe agree to 1e-5; z(1 - 1/838) = 3.0374,
z(1 - 1/(838 e)) = 3.3270); G3 normal 0.17242 (own DSR and the program's deflated_sharpe_ratio agree; t 4.865;
annualised 2.737); G3 skew -0.5 raw kurt 6 = 0.17556; t-bar 3/sqrt(870) = 0.10171; SR0_test 0.10871; test DSR bar
0.16488 (t 4.863); b_test 0.16488, annualised 2.617; s80 = 0.19363 and P(SR_hat >= b_test | 0.1936) = 0.799; G4
0.20070 with SR - se = 0.16488 exactly, t 5.663, annualised 3.186; G4 0.1373 and selection 0.1724 if the test DSR is
dropped; the 7-row power table (0.028/0.094/0.331/0.560/0.847/0.993/1.000 and 0.480/0.704/0.922/0.977/0.998/1/1); the
joint table (0.002/0.012/0.078/0.195/0.492/0.914/0.997 and products 0.000/0.001/0.026/0.109/0.417/0.908/0.997; the
text's 0.03/0.11/0.42/0.91 are these rounded); the 16-cell per-trade table (0.71/0.50, 1.22/0.87, 1.73, 3.46 at 2 a
date, 3.46 and 4.90 at 1 a date; mu = s sigma_h/sqrt(n) is the correct daily Sharpe of n independent trades a date
under the stated random walk); Bonferroni/Holm 300 z 3.5879; Bonferroni 838 z 3.8475; BY c(300) = 6.2827, z 4.0417;
HLZ 3.0; "G3 stricter than each" (4.865 > 4.042); the fat-tail requirement is correctly the harder one (0.1756 >
0.1724); p7_final.py rerun byte-identical to p7_final_budget300.md; p7_final's T_disc and T_test come from the same
calendars I walked.

P8 (10): G1 796 trades = 1.0 x 796; G2 0.920 - 0.528 = 0.392 and 0.50 - 0.392 = 0.108; G3's V and T match P7.2's
computation; G4's se formula equals the program's DSR denominator / sqrt(T - 1) to 1e-6 at (0.2007; 0, 3) and
(0.2007; -0.5, 6); G5(a) 13 quarters of 40-65 dates; G5(d) terciles from 796 values are well defined; Tier A cap 3 and
the 0.70 rule need no arithmetic; Tier B supplies 2 so that the program's DSR variance and PBO are defined when Tier A
has one member (stage_e_verdict.py l.549-553, l.609-620: fewer than 2 series -> "no edge (dsr undefined)"); the
6-fold ensemble averages probabilities and mu_k, not refits.

P9 and P10 (7): 2017-05-01..2017-05-19 = 15 weekdays, no closures; 2017-05-22..2020-11-30 = 921 weekdays - 31
closures = 890 (my walk; 905 - 15); burn-in 2017-05-22..2017-06-19, T_test 870, first OOF date 2017-06-20; the
program's verdict order Holm -> DSR -> t -> PBO as coded; K = 9 as the list's k_holm (V14 b); "N rises by 300 whatever
the outcome" is the registry's behaviour; the null-report items are computable from P6.2 and P4.2 outputs.

## Program-code consistency (the brief's explicit questions)

1. Raw or excess kurtosis. deflated_sharpe_ratio (funnel/multiple_comparisons.py l.81-113) takes RAW kurtosis
("a normal distribution is 3.0, not 0.0") and uses denominator_sq = 1 - skew SR + 0.25 (kurt - 1) SR^2. moments()
returns raw kurtosis (3.0 at sd = 0). P8 G4's se = sqrt((1 - g3 SR + (g4 - 1)/4 SR^2)/(T - 1)) with "g4 raw
kurtosis" is the same convention: numerically the program's denominator at (0.2007, 0, 3) is 1.010020 and at
(0.2007, -0.5, 6) 1.072707, equal to se x sqrt(T - 1) in both cases. Consistent. P7.2's bare "kurtosis 6" is raw
(AR-10).

2. DSR on the daily series with zeros. The verdict computes moments on the trial's daily series (zeros on window dates
without a trip, series unit "net ticks per contract per day") with n_observations = the series length. p7_final.py
uses T_disc = 796 and T_test = 870 daily values with V = 1/(T - 1) and the DSR's sqrt(T - 1): the same object. P3.8
and P6.2 define X_D with zeros on no-trade and excluded dates, so E.33's series is the program's kind. Consistent.

3. Sample or population SD. The verdict uses population SD, skew and kurtosis (statistics.pstdev, divisor n) and
t = mean/(pstdev/sqrt(n)). P6.2 says "sample SD" and contradicts itself: AR-2.

4. MathReview C-10 (one bar everywhere). Resolved in the protocol's own numbers: every power and per-trade figure in
P2, P3.1, P4.2 and P7.2 uses the one test bar b_test = 0.1649 and the one selection threshold 0.2007 (p7_final.py
report(); p7_thresholds.py's conflicting sections are superseded and not cited by the protocol). The residual is
AR-1: b_test is one of P9's two DSR bars, and the other is not a constant.

5. P7.2 per-trade figures against the stated random walk. With n independent trades a date of mean mu and SD
sigma_h = 3.15 sqrt(h), the daily P&L has mean n mu and SD sigma_h sqrt(n), so SR_d = mu sqrt(n)/sigma_h and
mu = SR_d sigma_h/sqrt(n): every cell reproduces. The assumption "every date" is stated; its interaction with G1's
50% floor is AR-6. The table is for fixed-horizon exits; TB exits have a different per-trade SD (not claimed).

6. Numbers that would change a gate, a power statement or the false-positive rate. Gate: AR-2 (SD convention at the
G4 margin), AR-3 (N 538 vs 838: G3 0.1678 vs 0.1724), AR-5 (embargo 20 vs 21: fold sizes). Power statement: AR-1
(the P9 bar's power is 0 in mixed lists), AR-6, AR-8. False-positive rate: none wrong; AR-7 on what the 20-run proof
can show. The Holm z (AR-4) changes no gate.

## Not checked

- Anything requiring data: sigma_1m's validity on 2020-12..2024-02, the real trade rates and zero-trade-day shares
  behind the per-trade table, E.31's counts of roll and late-open dates (E.33 recounts by rule).
- The leakage, hidden-degree-of-freedom and feasibility lenses beyond the arithmetic they touch (AR-5, AR-11, AR-12
  are handed to those reviewers).
- The content of MathReview_D's 4-5 open items and whether the lead has applied A-D's fixes to the reader files.
- The program's bootstrap p_upper and PBO behaviour on 2-3 correlated test series (a second companion effect on the
  P9 bar: PBO over Tier A series is undefined for one and noisy for two or three); only the DSR component was
  simulated.
- The web was not used; no library or schema fact needed checking against documentation.
