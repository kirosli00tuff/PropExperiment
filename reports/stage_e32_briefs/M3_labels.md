# E.32 Part M3: labels and sampling for a minutes-scale directional ZM search, net of costs

Worker: LabelsMath-OpusHigh (Opus 5.5, effort high), 2026-10-27 00:23-PDT start. Brief: the E.32 lead's spawn message,
reports/stage_e32_briefs/READER_BRIEF.md and reports/stage_e28_briefs/READER_RULES.md. Evidence pages and log:
reports/stage_e32_briefs/pages/M3_labels/ (log.tsv). Arithmetic: reports/stage_e32_briefs/work/M3_labels/M3_calc.py,
output M3_calc.out (every number in this file that is not hand-computed below comes from that script; it reads no
market data). Status: all seven topics (a-g), the per-horizon table (f.3) and both planner pointers written; finished
2026-10-27 00:40 PDT. Nothing was trained and no feature, label, return or markout was computed from data. N stays 538.

What this file adds to E.28. E.28 2.7 (methods brief lines 6941-8259) already defines the triple-barrier method
(section 2), meta-labeling (section 3), uniqueness weights and the sequential bootstrap (section 4) and purged CV
(sections 5-6); E.28 2.9 section 8 (lines 10142-10219) defines taker and maker labels for MES. I cite those as
"E.28 2.7 s2" and so on and do not restate them. New here: bar types and the CUSUM event filter on ZM's two sessions
(a); volatility-scaled barriers and first-passage arithmetic that shows what a +-4-6 tick barrier really measures
(b); meta-labeling for a directional primary rule (c); a 15-minute uniqueness example and time-decay weights (d);
the decomposition of the 1.59-tick break-even and the executable-versus-mid label bias (e); the per-horizon
break-even hit rates and their detectability over 39 months (f); and sampling exclusions on the CBOT grain grid (g).

Standing assumptions (used in every worked example, restated where used):
- A1 (random-walk scaling): ZM mid changes are uncorrelated across minutes with constant variance, so
  sigma_h = sigma_1m x sqrt(h), sigma_1m = 3.15 ticks (A0 Table 1: main-session minutes only, last-trade closes
  carried forward, roll minutes dropped; 18% of minutes have zero change). This is false in detail: intraday
  volatility is U-shaped and release minutes are far noisier, and sigma_1m from trade prices carries bid-ask bounce
  (Roll: a 1-tick spread adds up to s^2/2 = 0.5 tick^2 to a variance of 3.15^2 = 9.92 tick^2, about 5%). Check of A1:
  the expected range of a Brownian path over the 290-minute day session is sqrt(8/pi) x sigma x sqrt(T) =
  1.5958 x 3.15 x 17.029 = 85.6 ticks, against A0's median daily range of 96 ticks for the whole trade date
  (overnight included). Same order; A1 is usable for sizing, not for inference.
- A2 (cost): BE = 1.59 ticks per round trip, E.28's mu*_mkt for Topstep x ZM (section e quotes and decomposes it).
- A3 (sessions, CT): overnight 19:00-07:45, day 08:30-13:20 (290 minutes), settlement window 13:14-13:15 (R4_events.md
  section 1.1, from CBOT filings that R4 saved; section g).

---

## (a) Clock, tick, volume and dollar bars; event-time sampling with the CUSUM filter

### a.1 Core idea

A bar is one row of the training table. Clock bars sample every fixed minute; tick, volume and dollar bars sample
after a fixed number of trades, contracts or dollars, so busy periods get more rows and quiet ones fewer. An event
filter (the symmetric CUSUM) goes one step further and creates a row only when the cumulative price move since the
last event passes a threshold, so the model is asked to forecast only after something has happened.

### a.2 Equations

- Clock bars: bar k closes at t_k = t_0 + k x Delta, Delta = 1 minute.
- Tick, volume, dollar bars (definitions as in mlfinpy, `mlfinpy_FinancialDataStructure.rst.txt` lines 18-20:
  "Tick bars, are sampled after a fixed number of ticks have taken place", "Volume bars, are sampled after a fixed
  number of contracts (volume) has been traded", "Dollar bars, are sampled after a fixed monetary amount has been
  traded"). With trades j = 1, 2, ... since the last bar close, sizes v_j and prices p_j, bar k closes at the first
  trade J where sum_{j<=J} 1 >= theta_N (tick), sum_{j<=J} v_j >= theta_V (volume), or
  sum_{j<=J} p_j x m x v_j >= theta_D (dollar; m = 100 short tons for ZM, p in USD per short ton).
- Volume imbalance bars (mlfinpy restating AFML ch. 2, lines 197-221): tick rule b_t = b_{t-1} if Delta p_t = 0,
  else sign(Delta p_t); theta_T = sum_{t=1}^{T} b_t v_t; a bar closes when |theta_T| >= E_0[T] x |2 v^+ - E_0[v_t]|,
  with E_0[T] and the expected signed volume both EWMAs of earlier bars. (The rst text omits the absolute value on
  the right side; AFML's version has it [unverified: book not fetched].)
- Symmetric CUSUM filter (implementation `mlfinpy_src_filters.py` lines 76-86; the docs call it "the Symmetric
  Dynamic/Fixed CUSUM Filter", line 18). With y_t the price change (log return in the code; ticks below) and
  E_{t-1}[y_t] = 0:
      S+_t = max(0, S+_{t-1} + y_t),   S-_t = min(0, S-_{t-1} + y_t),
      event at t if S-_t < -H (then S-_t := 0) or else if S+_t > H (then S+_t := 0).
  Only the side that fired is reset (lines 81-86). H can be a series (a dynamic threshold, line 66), for example
  H_t = kappa x sigma_hat_t computed from trailing data.
- Event-spacing bound (my statement, standard first-passage result): for a driftless random walk with per-minute sd
  sigma, one CUSUM side alone is a random walk reflected at 0, whose mean time to pass H is H^2 / sigma^2. Two sides
  race, so the mean spacing between events is below H^2 / sigma^2.

### a.3 Worked example on the standard ZM numbers

Volume bars at 1/50 of ADV (the size Easley, Lopez de Prado and O'Hara used on the E-mini: "if we sample every 1/50
of the average daily volume", `easley_lopezdeprado_ohara_2012_volume_clock.txt` lines 854-855).
1. Bar size: theta_V = 36,690 / 50 = 733.8 contracts.
2. Day session: 36,690 x 0.83 = 30,452.7 contracts in 290 minutes, so 30,452.7 / 733.8 = 41.5 bars a day, one per
   290 / 41.5 = 7.0 minutes on average. Using A0's mean main-session volume of 109.2 contracts a minute instead:
   733.8 / 109.2 = 6.7 minutes per bar.
3. Overnight: 36,690 x 0.17 = 6,237.3 contracts, so 6,237.3 / 733.8 = 8.5 bars a night. At A0's overnight mean of
   8.5 contracts a minute a bar takes 733.8 / 8.5 = 86 minutes; at the overnight median of 2 a minute, 367 minutes.
4. Check: 41.5 + 8.5 = 50.0 bars a trade date, which is 36,690 / 733.8 = 50.0 by construction.
Reading: a volume clock gives ZM about 42 day rows and 8 overnight rows a day, against 290 and 765 one-minute rows.
It removes most of the overnight sample automatically, which is the right direction for a thin overnight book, but
at this bar size a 5-minute label is shorter than one bar.

Dollar bars. For a single futures contract with a fixed multiplier and no corporate actions, dollar bars differ from
volume bars only by the price level. The source's two arguments for dollar bars are price appreciation over long
periods and "corporate actions" on shares (`lopezdeprado_2018_10reasons_jpm.txt` lines 216-233); the second does not
apply to ZM and the first only rescales the bar rate by the price ratio over 39 months.

CUSUM toy (in ticks, H = 6; M3_calc.out section "symmetric CUSUM toy"). Changes y = (+2, +1, -1, +3, +1, -2, -3,
-2, +1, -2, 0, +4):
- t1: S+ = 2, S- = 0. t2: S+ = 3. t3: S+ = 2, S- = -1. t4: S+ = 5, S- = min(0, -1 + 3) = 0. t5: S+ = 6 (not > 6).
- t6: S+ = 4, S- = -2. t7: S+ = 1, S- = -5. t8: S+ = max(0, 1 - 2) = 0, S- = -7 < -6: event, S- := 0.
- t9: S+ = 1. t10: S+ = 0, S- = -2. t11: unchanged. t12: S+ = 4, S- = 0. One event, at t8.
Check: S+ touched exactly 6 at t5 and did not fire, because the test is strict (> H, code line 85); the declared
rule must say "strictly greater", or a tie-handling difference changes the event set.
Rate on ZM (A1): H = 6 ticks gives a spacing below 6^2 / 3.15^2 = 36 / 9.9225 = 3.63 minutes; H = 10 gives below
10.08 minutes; H = 15 below 22.7 minutes. A threshold near sigma_h of the label horizon makes events roughly as
frequent as non-overlapping labels.

### a.4 Data it needs

Trades from ZM MBO (action = trade or fill messages, with size, price and aggressor side; ts_recv for causal
ordering), aggregated to bars inside each session. ZS and ZL MBP-1 carry trades too and give the same bars for
context. Volume clocks need nothing beyond the trade prints; CUSUM can run on a 1-second or 1-minute mid grid built
from the book.

### a.5 Leakage and look-ahead traps

1. Bar size from full-sample ADV (36,690 is a 2022-11..2023-10 median). Test: compute theta_V from a trailing window
   only, rebuild bars on data truncated at a date D, and assert that every bar closing before D is identical to the
   full-run bars.
2. A label starting inside the bar that produced the features. Test: assert t_{i,0} > bar close time (strictly
   later message) for every row; shift features by one more bar and check no metric jumps.
3. Bars or CUSUM sums carried across the 13:20 close, the 07:45 pause, a roll (instrument_id change) or a halt.
   Test: reset S+, S- and partial bars at every session boundary and instrument change; count bars spanning a boundary
   (must be 0).
4. A dynamic CUSUM threshold H_t that uses same-minute or future volatility. Test: H_t computed from data at or
   before t - 1 minute; recompute with a one-minute extra lag and require identical events except where the
   threshold moves.
5. Prints that are not outright trades. E.31 found 9.1% of aggressor prints carry no aggressor side and 5.5% found no
   displayed quantity at their price (implied liquidity; reports/E.31_RETURN.md section 3.5). Test: tabulate prints
   by side flag and by whether a resting order existed; run bars with and without the unflagged prints.

### a.6 Compute (ThinkPad, 39 months)

One pass over the trade messages per date. E.31's pass over the same 816 ZM MBO trade dates (book rebuild plus
markouts) took 384 s on 4 workers; bars and CUSUM are lighter. Minutes in total; memory per date well under 1 GB.

### a.7 Verdict for a minutes-scale directional ZM search under V43

- Clock bars (1 minute) as the feature and label grid: USE. Horizons, the prop account's daily rules and the
  release calendar are all in clock time; purging and embargo are simplest on a clock grid.
- CUSUM (or another declared event filter) to choose label start times: USE as one declared sampling variant per
  family; each threshold kappa counts as a configuration in N.
- Volume bars: MAYBE, only as a declared robustness variant (one configuration). Their stated advantages are
  statistical ("a partial recovery of Normality and the IID assumption", `easley_lopezdeprado_ohara_2012_volume_clock.txt`
  lines 293-297), not predictive; the only controlled test found (a 2026 crypto study, evidence table) reports "No
  systematic relationship between statistical quality and predictability", and a comment on Ane and Geman (2000)
  reports that returns conditioned on trades or volume "are not Gaussian". Activity measures (volume in the last
  N minutes) carry the same information as features.
- Dollar bars: SKIP (no corporate actions; a price-level rescaling of volume bars).
- Imbalance and run bars: SKIP as a sampling scheme; their statistic (signed volume) belongs in M1's feature set.

### a.8 Evidence table

| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| Time bars oversample quiet periods | Lopez de Prado 2018, JPM (academic/practitioner) | "time bars oversample information during low-activity periods and undersample information during high-activity periods" | lopezdeprado_2018_10reasons_jpm.txt lines 200-202 |
| Volume clock as a subordinated process | same | "We can avoid the two problems described earlier by forming bars as a subordinated process of trading activity" | same, lines 208-209 |
| Dollar-bar rationale includes corporate actions | same | "the number of outstanding shares often changes multiple times over the course of a security's life, as a result of corporate actions" | same, lines 229-231 |
| Volume time gives partial normality | Easley, Lopez de Prado, O'Hara 2012 (academic; third-party PDF copy of the May 2012 version) | "this time transformation removes most intra-session seasonal effects; second, it allows a partial recovery of Normality and the IID assumption" | easley_lopezdeprado_ohara_2012_volume_clock.txt lines 293-295 |
| Their bar size: 1/50 of ADV on the E-mini | same | "The blue line is the equivalent if we sample every 1/50 of the average daily volume" | same, lines 854-855 |
| Volume-conditioned returns are still not normal | Murphy and Izzeldin 2005 (academic working paper) | "returns conditioned by recentered volume or the number of transactions are not normally distributed" | murphy_izzeldin_2005_comment_ane_geman.txt lines 324-325 |
| Bar statistics do not predict forecast quality | Fayyaz et al. 2026, arXiv 2608.26158 (academic preprint; BTCUSDT perpetual, 3-day labels) | "No systematic relationship between statistical quality and predictability. We do not find that any single statistical criterion predicts classifier AUC" | arxiv_2608.26158_info_bars_crypto.txt lines 2304 and 2315-2316 (two-column extraction interleaves the words; also line 2755: "out-of-sample AUC is near-chance (0.50-0.60)") |
| Same study: near-chance AUC for every bar type | same | "All AUC values lie in 0.48-0.60 (near-chance)" (en dash in original) | same, line 2283 (Table V note at line 2127) |
| CUSUM is symmetric and resets on firing | mlfinpy source (practitioner code implementing AFML) | "if s_neg < -thresh: s_neg = 0 ... elif s_pos > thresh: s_pos = 0" | mlfinpy_src_filters.py lines 81-86 |
| CUSUM avoids repeated triggers near a level | mlfinpy docs | "multiple events are not triggered by raw_time_series hovering around a threshold level" | mlfinpy_Filtering.rst.txt line 29 |
| Volume clock helps Normality per the mlfinpy authors | mlfinpy docs (secondary) | "tick, volume, and dollar bars all exhibit a distribution significantly closer to normal - versus standard time bars" | mlfinpy_FinancialDataStructure.rst.txt lines 150-151 |

Stopping rule: the bar-type topic has four full texts read (LdP 2018, Easley et al. 2012, Murphy-Izzeldin 2005,
Fayyaz et al. 2026); Ane and Geman (2000) itself is paywalled (JF 55(5), known from the search snippet and the
comment only [unverified]); arXiv API queries for "dollar bars", "volume bars" and "volume clock" in q-fin surfaced
only 2608.26158.

---

## (b) Fixed-horizon versus triple-barrier labels with volatility-scaled barriers; labels to the session close

### b.1 Core idea

A fixed-horizon label scores the trade at t + h whatever happened in between; a triple-barrier label scores it at
the first of a profit target, a stop, or t + h (E.28 2.7 s2 has the definition and a toy path). The barrier width
decides which horizon the label really measures: for a random walk the expected time to reach +-a is a^2/sigma^2,
so a fixed-tick barrier is a fixed-time label in disguise, and only a barrier that scales with sigma x sqrt(h) keeps
the label tied to the declared horizon h. A label "to the session close" is a fixed-horizon label whose horizon
shrinks with the entry time.

### b.2 Equations

Notation: tick size delta = 0.10 USD per short ton, so prices below are in ticks; A_t, B_t, M_t are best ask, best
bid and mid; L is the order latency; f = 0.528 ticks the round-trip fee; s = side (+1 long, -1 short).

- Fixed horizon, executable (extends E.28 2.9 s8.2 to both sides and to latency):
      R^exec_{t,h}(s=+1) = B_{t+L+h} - A_{t+L} - f,   R^exec_{t,h}(s=-1) = B_{t+L} - A_{t+L+h} - f.
  Mid-to-mid: R^mid_{t,h} = M_{t+h} - M_t. Label y = sign or value of R (section f adds the dead zone).
- Fixed-horizon definition in the source (`lopezdeprado_2018_10reasons_jpm.txt` lines 327-345): y_i = -1 if
  r < -tau, 0 if |r| <= tau, 1 if r > tau, with r_{t_{i,0}, t_{i,0}+h} = p_{t_{i,0}+h} / p_{t_{i,0}} - 1. The source's
  objection: "the same threshold tau is applied regardless of the observed volatility" (lines 346-347).
- Volatility-scaled barriers (my parameterisation of the AFML idea that barriers are "a dynamic function of
  estimated volatility", lines 356-357): for event i with entry price P_i (the executable entry), declared horizon h
  and multiplier kappa,
      a_i = kappa x sigma_hat_i x sqrt(h),
  with sigma_hat_i a per-minute sd estimated from data strictly before t_i (for example an EWMA of 1-minute mid
  changes over the previous 60 day-session minutes; one declared choice). Upper barrier P_i + a_i, lower P_i - a_i,
  vertical t_i + h. Barrier tests are on the executable exit price (the bid for a long, the ask for a short).
[MathReview B-13 (lead: accepted): under this definition an upper-barrier hit for a long means bid_exit >= ask_entry + k, so the k ticks are already net of the spread, and charging BE = 1.59 (which contains the 1-tick spread) on top as in b.3, c.2 and f.2 (original lines 214-216, 295-297, 642) double-counts the spread by 1.0 tick. The protocol must state which applies: either (i) barriers on the mid, cost BE = 1.59: p* = 0.699/0.659/0.6325 (as written), or (ii) barriers on executable prices, cost c_x = 0.59 (fee + residual): p* = (k + 0.59)/(2k) = 0.574/0.559/0.549 at k = 4/5/6 and 0.5121 at k = 24.40; every mixed reading errs conservative, so no verdict changes.]
- First-passage facts for a driftless Brownian path with per-minute sd sigma and symmetric barriers +-a (standard
  results; my statements, not from the fetched sources):
      P(up first) = 1/2;   E[tau] = a^2 / sigma^2 (minutes);
      P(no barrier by h) = (4/pi) x sum_{n>=0} (-1)^n / (2n+1) x exp( -(2n+1)^2 pi^2 sigma^2 h / (8 a^2) ).
  With a = kappa x sigma x sqrt(h) the last expression depends on kappa only: 0.3708 at kappa = 1 and 0.9090 at
  kappa = 2 (M3_calc.out). So at kappa = 1 about 37% of labels end on the vertical barrier and at kappa = 2 about 91%,
  at which point the triple-barrier label is almost a fixed-horizon label.
- Labels to the close: for an entry at minute u of the day session (u in [0, 290)), h(u) = T_close - u. With A1,
  sigma_{h(u)} = sigma_1m x sqrt(290 - u). Averaged over a uniform entry time, E[sqrt(290 - u)] = (2/3) sqrt(290), so
  the typical to-close label has sd (2/3) x 3.15 x 17.029 = 35.76 ticks, the same as a fixed 128.9-minute label
  ((2/3)^2 x 290 = 128.9).

### b.3 Worked example on the standard ZM numbers

1. The planner's +-4 to 6 tick triple barrier (planner pointer 1). With sigma = 3.15 ticks a minute:
   - E[tau] = 4^2 / 9.9225 = 1.61 min; 5^2 / 9.9225 = 2.52 min; 6^2 / 9.9225 = 3.63 min.
   - 95% of paths have hit a barrier by 4.23 min (k = 4), 6.61 min (k = 5) and 9.52 min (k = 6) (M3_calc.out,
     bisection on the series above).
   - So a +-5-tick label with a 60-minute vertical barrier is in practice a 2-to-7-minute label; the vertical
     barrier almost never binds. It cannot stand in for the 15-240-minute horizons in the same label set.
   - Break-even hit rate with exits at the barriers and cost BE = 1.59: win k - 1.59, loss -(k + 1.59), so
     p* = (k + 1.59) / (2k): k = 4: 5.59 / 8 = 0.699; k = 5: 6.59 / 10 = 0.659; k = 6: 7.59 / 12 = 0.6325. Check
     (k = 5): 0.659 x 3.41 - 0.341 x 6.59 = 2.247 - 2.247 = 0.000.
2. Volatility-scaled barrier for h = 60 min, kappa = 1: a = 1 x 3.15 x sqrt(60) = 3.15 x 7.746 = 24.40 ticks.
   p* = 1/2 + 1.59 / (2 x 24.40) = 0.5 + 0.0326 = 0.5326; 37% of such labels end at the vertical barrier.
3. Fixed-horizon label at 15 minutes: sigma_15 = 3.15 x 3.873 = 12.20 ticks; the executable label differs from
   the mid label by the spread paid (section e), here about 1 tick, which is 1 / 12.20 = 0.082 sigma.
4. To-close label, entry 08:30: h = 290, sigma = 3.15 x 17.029 = 53.64 ticks; entry 13:00: h = 20,
   sigma = 3.15 x 4.472 = 14.09 ticks. The same model output means 3.8 times less risk at 13:00; the label must be
   scaled by sigma_{h(u)} (or the model trained per entry-time bucket), or late-session rows dominate the loss less
   than their count suggests and early-session rows dominate the P&L.
Check: 53.64 / 14.09 = 3.807 = sqrt(290 / 20) = sqrt(14.5) = 3.808.

### b.4 Data it needs

ZM MBO rebuilt to the best bid and ask (executable labels need both sides at entry and exit, at the event
resolution of the barrier, plus the book depth for section e); ZS and ZL MBP-1 are not labelled (context only).
sigma_hat from 1-minute mids of the same book. Session and roll calendars (section g).

### b.5 Leakage and look-ahead traps

1. sigma_hat_i including the label window or the current minute. Test: compute sigma_hat with an extra one-minute
   lag; barriers and labels must change only through the lag, and no feature importance may sit on sigma_hat alone.
2. Ties: a bar where both barriers are inside the bar's high-low range (1-minute bars cannot tell which came first).
   Test: build labels from event-time book updates, not from 1-minute OHLC; count ties under OHLC (report them).
3. Barrier hits measured on mid or last trade while the trade exits at the bid or ask. Test: recompute every label
   with executable prices; report the share of labels whose class changes.
4. To-close labels that end at the 13:14-13:15 settlement VWAP or at 13:20 when the exit price used is the
   settlement price (not tradeable at that price by a market order). Test: the exit is an executable price at a
   declared minute; assert no label uses a settlement field.
5. Barrier multipliers or horizons tuned on the discovery data and reported as one configuration. Test: the
   declared grid in the protocol equals the grid run; N counts each (kappa, h) pair.

### b.6 Compute

Barrier first-passage per event is a forward scan: O(events x book updates in the window). At one label start per
minute over 816 day sessions there are 816 x 290 = 236,640 starts; a 60-minute window holds on the order of 10^3 to
10^4 book updates, so 10^8 to 10^9 comparisons per (kappa, h) pair. Vectorised per date, minutes on the laptop;
run per date in parallel (at most 8 processes, nice 10).

### b.7 Verdict

- Fixed-horizon executable labels at the declared horizons: USE (the primary target; they map one-to-one to a trade
  that holds h minutes).
- Triple barrier with kappa x sigma_hat x sqrt(h) barriers: MAYBE, one declared kappa (for example 1) per horizon
  as a secondary target, counted in N. Its advantage is the realism of the exit, not prediction (E.28 2.7 s2.8 found
  no head-to-head test against fixed horizons, and none was found here).
- Fixed +-4-6 tick barriers: SKIP as a multi-horizon label. They measure a 2-7-minute move and need a 63-70% hit
  rate; if kept, they belong to the 1-5-minute family only.
- To the close: USE as one label, with the exit at a declared executable minute before the settlement window
  (section g), and the target scaled by sigma_{h(u)}.

### b.8 Evidence table

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Fixed-horizon threshold ignores volatility | Lopez de Prado 2018 (JPM) | "the same threshold 𝜏 is applied regardless of the observed volatility" | lopezdeprado_2018_10reasons_jpm.txt lines 346-347 |
| Barriers scale with volatility | same | "which are a dynamic function of estimated volatility (whether realized or implied)" | same, lines 356-357 |
| Vertical barrier can be activity-based | same | "The third barrier is defined in terms of number of bars elapsed since the position was taken (an activity-based, not fixed-time expiration limit)" | same, lines 358-360 |
| Implementations label on close prices | mlfinpy source | "cum_returns = (closing_prices / close[loc] - 1) * events_.at[loc, \"side\"]  # Path returns" | mlfinpy_src_labeling.py line 72 |
| First-passage formulas | standard Brownian-motion results | [no fetched source; my statement, checked numerically in M3_calc.py] | - |

---

## (c) Meta-labeling, and when it helps

### c.1 Core idea

A fixed primary rule picks the side (for a directional search: follow the post-release move, fade a crush-residual
gap, follow a CUSUM break); a secondary classifier, trained on the primary's own past events, decides act or pass
and possibly the size. E.28 2.7 s3 gives the definitions, the precision-to-P&L link and the evidence, and finds no
independent cost-inclusive test. What is new here is the directional version: the meta-label is the net executable
outcome of the primary's trade, and the break-even precision is the section (f) hit rate.

### c.2 Equations

- Primary side s_i in {-1, +1} at event time t_i (a declared rule; no fitted parameters, or parameters frozen before
  E.33).
- Meta-label z_i = 1[ R^exec_{t_i,h}(s_i) > 0 ], with R^exec from b.2 (net of fee and spread, after latency).
  mlfinpy's version, for comparison, multiplies the close-price return by the side and sets "bin" to 0 when
  "ret <= 0" (`mlfinpy_src_labeling.py` lines 332-340): gross of costs and on last-trade prices.
- Secondary model p_i = P(z_i = 1 | X_i), act if p_i > c. With symmetric barriers +-k and cost BE, the expected net
  per accepted trade is pi(c)(k - BE) - (1 - pi(c))(k + BE), positive iff precision pi(c) > (k + BE) / (2k)
  (the same p* as b.3; E.28 2.7 s3.2 derives the general form b / (a + b)).
- Trade count: report the number of accepted trades n_acc directly (recall alone does not fix it). The standard
  error on precision is sqrt(pi(1 - pi) / n_eff,acc), with n_eff,acc the uniqueness-adjusted count (section d).

### c.3 Worked example on the standard ZM numbers

Primary rule: "follow the direction of a CUSUM event (H = 12 ticks) for 15 minutes". Under A1 the rule has no edge,
so its raw precision is 0.50.
1. Barrier at kappa = 1 for h = 15: k = 12.20 ticks. Break-even precision p* = (12.20 + 1.59) / 24.40 = 13.79 / 24.40
   = 0.5652.
2. Events: the one-sided mean spacing H^2 / sigma^2 = 144 / 9.9225 = 14.5 minutes bounds the spacing from above, so
   there are at least about 290 / 14.5 = 20 day-session events a day, about 816 x 20 = 16,320 over the discovery
   window (a lower-end count: two sides racing make events more frequent, and the 15-minute labels then overlap).
3. Suppose the secondary model accepts 20% of events, 3,264, at precision 0.58. Net per trade:
   0.58 x (12.20 - 1.59) - 0.42 x (12.20 + 1.59) = 0.58 x 10.61 - 0.42 x 13.79 = 6.154 - 5.792 = +0.362 ticks.
4. Is 0.58 distinguishable from p* = 0.5652? se = sqrt(0.58 x 0.42 / 3,264) = sqrt(0.2436 / 3,264) =
   sqrt(7.463e-5) = 0.00864; (0.58 - 0.5652) / 0.00864 = 1.71. Not at t > 3, before any multiple-testing deflation.
   To reach t = 3 at the same margin needs n = 0.2436 x (3 / 0.0148)^2 = 0.2436 x 41,088 = 10,009 accepted trades,
   more than half of all events.
Check: 3,264 x 0.362 = 1,182 ticks of total edge over 39 months, about 1.45 ticks per trading day; the per-trade sd is
2 x 12.20 x sqrt(0.58 x 0.42) = 24.40 x 0.4936 = 12.04 ticks, so the per-trade Sharpe is 0.362 / 12.04 = 0.030.

### c.4 Data it needs

The primary's event list (from ZM MBO and, for cross-market rules, ZS/ZL MBP-1), executable labels (b.2), and
features known at t_i. The secondary's training set is the primary's events only, so its sample is small: plan the
size from the primary's event rate before the run.

### c.5 Leakage and look-ahead traps

1. Primary parameters tuned on the same data as the secondary. Test: freeze the primary in the protocol; the run
   log shows no fit step for it.
2. The secondary's threshold c chosen on the test fold. Test: c fixed in the protocol or chosen inside the
   training folds only; record the c grid in N.
3. Meta-labels gross of costs or on mid prices (mlfinpy default). Test: assert the label function takes the side,
   fee, latency and bid/ask arrays; a unit test with a one-tick move must return z = 0 for a long.
4. Overlapping primary events counted as independent in the precision test. Test: report n_eff (section d) beside
   n_acc, and use a day-block bootstrap.

### c.6 Compute

Small: a few thousand to tens of thousands of rows; a shallow GBM fit in seconds (E.28 2.7 s3.7 measured 5.6 s for
10^6 rows x 30 features x 200 trees on 8 threads).

### c.7 Verdict

MAYBE. It is the right architecture when a family has an economically signed primary rule (post-USDA, crush gap,
open gap), because it keeps the side out of the search and spends the model only on act/pass. It does not create
an edge where the primary has none on any subset, and the arithmetic above shows the binding problem is the count
of accepted trades: precision gains of a few points over p* are not testable at t > 3 with tens of thousands of
events at most. Each threshold c counts in N.

### c.8 Evidence table

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Purpose of the secondary model | Lopez de Prado 2018 (via E.28 2.7 s3) | "The goal of the secondary model is to predict the accuracy of the primary model's prediction" | lopezdeprado_2018_10reasons_jpm.txt lines 387-388 (E.28 2.7 s3.1 cites 389-391 for the same sentence; the copy here shows 387-388) |
| mlfinpy meta-labels are gross close-price returns times side | mlfinpy source | "out_df[\"ret\"] = out_df[\"ret\"] * events_[\"side\"]  # meta-labeling" and "out_df.loc[out_df[\"ret\"] <= 0, \"bin\"] = 0" | mlfinpy_src_labeling.py lines 333 and 340 |
| No new independent cost-inclusive test found | search 2026-10-27: one WebSearch ("meta-labeling futures out-of-sample transaction costs...") and one Crossref query; results were theses, vendor posts and unrelated papers | (null result) | work/M3_labels/M3_crossref_meta.json |

---

## (d) Sample weights for overlapping labels: average uniqueness, sequential bootstrap, time decay

### d.1 Core idea

A 15-minute label started every minute shares 14 of its 15 one-minute returns with its neighbour, so 15 rows carry
roughly one row of label information. Average uniqueness measures this per label; weights proportional to it (times
attributed return, optionally times a time-decay factor) stop the model from counting the same move 15 times; the
sequential bootstrap draws bagging samples that overlap less. E.28 2.7 s4 gives the uniqueness and return-attribution
equations and a 6-bar toy; this section adds the minute-sampled ZM case, a closed form for the effective count, time
decay, and the compute limit of the sequential bootstrap.

### d.2 Equations

- From E.28 2.7 s4.2 (AFML ch. 4 via the JPM summary): 1_{t,i} = 1 if label i uses return bar t; c_t = sum_i 1_{t,i};
  u_bar_i = (sum_t 1_{t,i} / c_t) / (sum_t 1_{t,i}). mlfinpy's statement of concurrency: labels "are concurrent at t
  if they are a function of at least one common return at r_{t-1,t}" (`mlfinpy_Sampling.rst.txt` lines 29-30).
- Effective count, closed form when every span has the same length h (my derivation):
      sum_i u_bar_i = (1/h) sum_i sum_t 1_{t,i} / c_t = (1/h) sum_t (sum_i 1_{t,i}) / c_t = (1/h) x #{t : c_t > 0}.
  So n_eff = (bars covered by at least one label) / h: for minute-sampled labels it equals the number of
  non-overlapping horizons, whatever the sampling step.
- Time decay (AFML 4.7 as implemented, `mlfinpy_src_attribution.py` lines 116-170): let x_i = cumulative average
  uniqueness up to label i in time order and X = x_last. Weights d_i = max(0, a + b x_i) with d_last = 1 and
      b = (1 - C) / X if C >= 0,   b = 1 / ((C + 1) X) if C < 0,   a = 1 - b X.
  The docstring: "``decay`` = 1 means there is no time decay" and "``decay`` < 0 means that the oldes portion c of
  the observations receive zero weight" (lines 136 and 140; "oldes" sic).
- Sequential bootstrap: at each draw, every candidate's probability is proportional to its average uniqueness
  computed together with the labels already drawn (mlfinpy docs lines 141-156; E.28 2.7 s4.2).

### d.3 Worked example: 15-minute labels sampled every minute in one ZM day session

Setup: 290 one-minute return bars (j = 1..290); a label started at minute t0 uses bars t0+1..t0+15 and must end by
the close, so t0 = 0..275: 276 labels.
1. Concurrency: c_j = min(j, 15, 291 - j) (it rises 1, 2, ..., 15 over the first 15 bars, stays at 15, and falls at
   the end). Maximum 15 (M3_calc.out: "max c 15").
2. Interior label (t0 = 100): every bar has c = 15, so u_bar = (15 x 1/15) / 15 = 1/15 = 0.0667.
3. First label (t0 = 0): bars j = 1..15 have c_j = j, so u_bar = (1/15)(1 + 1/2 + ... + 1/15) = H_15 / 15 =
   3.3182 / 15 = 0.2212. The last label is the mirror image: 0.2212. The second is 0.1590, the third 0.1301.
4. n_eff = sum u_bar = 290 / 15 = 19.33 (closed form above; the script's direct sum gives 19.3333). Mean u_bar =
   19.33 / 276 = 0.0700.
5. Over the 816 trade dates of the discovery window (E.31's count before exclusions): 276 x 816 = 225,216 labels,
   n_eff = 19.333 x 816 = 15,776.
Check: n_eff equals the 19.33 non-overlapping 15-minute windows in 290 minutes, as the closed form says; and 0.0700 is
just above 1/15 = 0.0667 because the edge labels are more unique.
Consequence: sampling every minute multiplies rows by 15 but not information about the label; every standard error
and the power calculation must use about 15,800 (or fewer, after exclusions), not 225,216.

Time decay on four labels with u_bar = (0.5, 0.5, 1, 1), so x = (0.5, 1.0, 2.0, 3.0), X = 3:
- C = 0.5: b = 0.5 / 3 = 0.1667, a = 1 - 0.5 = 0.5; d = (0.5833, 0.6667, 0.8333, 1.0).
- C = -0.25: b = 1 / (0.75 x 3) = 0.4444, a = 1 - 1.3333 = -0.3333; d = (max(0, -0.1111), 0.1111, 0.5556, 1.0) =
  (0, 0.1111, 0.5556, 1.0): the oldest 25% of cumulative uniqueness (x <= 0.75) gets zero weight.
Check: both rows end at 1.0, and the C = 0.5 row starts at a + b x_1 = 0.5 + 0.0833 = 0.5833, above C because x_1 > 0.

### d.4 Data it needs

Only label spans (from b) on the 1-minute grid and 1-minute mid returns (for return attribution).

### d.5 Leakage and look-ahead traps

1. Weights computed on the whole sample, including test folds (uniqueness at a fold boundary depends on labels in
   the next fold). Test: compute weights inside each training fold after purging; compare with full-sample weights
   at the boundary rows.
2. Return-attribution weights |sum r / c| use the label's own return, which is the target. As training weights that is
   allowed (AFML), but they must never enter features or model selection metrics. Test: the evaluation metric is
   unweighted or uniqueness-weighted only; assert no attribution weight in the scorer.
3. Time-decay weights tuned on test results (C chosen after looking). Test: C fixed in the protocol; each C counts
   in N.
4. Reporting t-statistics with the raw row count. Test: every reported test lists n_eff beside n.

### d.6 Compute

Uniqueness: O(labels x span) = 225,216 x 15 = 3.4 x 10^6 operations per horizon; trivial. The sequential bootstrap as
implemented in mlfinpy recomputes uniqueness for every candidate at every draw: about I^2 x h operations for I draws
from I labels, here 225,216^2 x 15 = 7.6 x 10^11, which is not feasible in Python on the laptop. Run it per trade
date (276 labels: 276^2 x 15 = 1.14 x 10^6 per date, 9.3 x 10^8 over 816 dates, minutes) or replace it by a
day-block bootstrap, which removes the cross-day overlap by construction because labels end at the close.

### d.7 Verdict

- n_eff and HAC or day-block inference: USE (mandatory).
- Uniqueness weights in training: USE as the single declared weighting (cheap; no comparison, so no extra N).
- Time decay: SKIP for discovery (39 months is short; a decay choice is one more configuration with no prior reason
  for a value); revisit only if the lead declares a regime-adaptive variant.
- Sequential bootstrap: SKIP; the day-block bootstrap covers the same need at a fraction of the compute.

### d.8 Evidence table

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Concurrency definition | mlfinpy docs (secondary, citing AFML) | "We say that labels :math:`y_i` and :math:`y_j` are concurrent at :math:`t` if they are a function of at least one common return at :math:`r_{t-1,t}`" | mlfinpy_Sampling.rst.txt lines 29-30 |
| Sequential bootstrap aim | same | "The key idea behind Sequential Bootstrapping is to select samples in such a way that on each iteration we maximize average uniqueness of selected subsamples." | same, lines 77-78 |
| Sequential bootstrap raises uniqueness | Lopez de Prado 2018 (via E.28 2.7 s4) | "can significantly increase the average uniqueness of samples" | lopezdeprado_2018_10reasons_jpm.txt line 490 |
| Time-decay rule | mlfinpy source (AFML 4.7) | "``decay`` = 1 means there is no time decay" ... "``decay`` < 0 means that the oldes portion c of the observations receive zero weight" | mlfinpy_src_attribution.py lines 136-140 |
| Time-decay formula | same | "slope = (1 - decay) / decay_w.iloc[-1]" ... "slope = 1 / ((decay + 1) * decay_w.iloc[-1])" ... "const = 1 - slope * decay_w.iloc[-1]" | same, lines 164-167 |

---

## (e) The minimum predictable move set by costs; executable-price versus mid-to-mid labels

### e.1 Core idea

A directional forecast pays three things per round trip: the fee, the spread it crosses (or, for a passive order,
the adverse selection of being filled), and any slippage and latency drift. Its gross expected move must exceed their
sum. The label must be built on the prices the trade would actually get, or the model learns a target that is
systematically about one tick too optimistic per round trip.

### e.2 The 1.6-tick break-even: the exact row and its decomposition

Exact row (reports/stage_e28_ranking.md line 130, Layer 2 table; header at line 123):

    | Rank | Firm | Code | E | D | R | A | F | P | Rel | L2 | L1 | S | mu*_lim | mu*_mkt | mu10K | cost/attempt | room | gates | u |
    | 6 | topstep | ZM | 2.69 | 2 | 4 | 2 | 1 | 2 | 3 | 2.475 | 2.150 | 2.312 | 0.59 | 1.59 | 0.86 | 49.23 | 2.08 | ok |  |

What mu*_mkt is (reports/stage_e28_ranking_spec.md lines 114-124): the strategy trades "T = 20 round trips per
trading day, 1 contract each", gross P&L per trade is normal with mean mu and "standard deviation sigma_T = sigma_1m
(a one-minute holding scale)"; "Market case c_mkt = F_rt + S_rt, with S_rt the sourced median main-session spread in
ticks (1 if unknown)"; and mu* is "the smallest mu on a 0.01-tick grid from 0 to 4 ticks at which expected net cash
per cycle (all withdrawals minus all fees, a cycle as E.19 defines it) is at least 0".

The Topstep x ZM inputs (reports/stage_e28_briefs/A3_econ.json, record for topstep ZM): F_rt_usd = 5.28,
F_rt_ticks = 0.528, S_rt_ticks = 1.0 with S_rt_status "u" and note "default 1 (u): no sourced median", sigma_T =
3.1522, c_lim_ticks = 0.528, c_mkt_ticks = 1.528, mu_star_mkt = 1.59, cost_per_attempt_usd = 49.23, MLL_usd = 2000,
plan "50K Trading Combine, Standard Path (USD 49/month)", api_monthly_usd = 14.5.

Decomposition of 1.59 ticks per round trip:

| Component | Ticks | Basis |
|---|---|---|
| Fees (commission + NFA + exchange) | 0.528 | 5.28 USD / 10 USD per tick; Topstep page read by E.28 (F_rt_source quote "$5.28") |
| Spread crossing (half a spread at entry, half at exit) | 1.000 | E.28's default S_rt = 1 tick, NOT a sourced or measured ZM spread ("u") |
| Slippage beyond the touch, latency drift | 0 | not in E.28's model |
| Prop-account economics (evaluation and API fees, MLL failures and resets, payout rules) at T = 20, sigma_T = 3.15 | 0.062 | residual: 1.59 - 1.528; part of mu*, not a trading cost; also absorbs the 0.01-tick grid |
| Total (mu*_mkt) | 1.59 | |

Check: c_mkt = 0.528 + 1.000 = 1.528; mu*_lim - c_lim = 0.59 - 0.528 = 0.062, the same residual, as it should be since
both cases share the account economics.

Three caveats the protocol must carry:
1. The spread term is a default. ZM's quoted spread is usually one tick in the day session (E.31's model (a) and (b)
   fills captured +0.34 to +0.36 ticks of half-spread, below the 0.5 a 1-tick market allows; my inference only, not
   a spread measurement), but the mean spread
   paid by a market order, wider at the open, after releases and overnight, is not on disk as a sourced number. E.33
   should measure it from MBO on discovery data as part of the cost model (a cost input, not a signal).
2. Slippage is zero in the 1.59. For a 1-lot, the touch usually holds at least one contract, but E.31 found that
   "5.5% of aggressor prints (3.6% of their volume) found no displayed resting quantity at their price" and "11.8%
   (26.0% of volume) found less than their size" (reports/E.31_RETURN.md section 3.5): depth-conditioned fills
   matter in exactly the minutes a directional signal is likely to fire.
3. mu*_mkt was solved at sigma_T = sigma_1m and 20 trades a day. A 60-minute strategy can hold at most
   floor(290 / 60) = 4 non-overlapping day trades and has per-trade sd 24.4 ticks, so its account economics
   (MLL breach rate, days to payout) differ and the residual 0.062 is not transferable. Rerunning E.28's model at
   (T, sigma_T) = (floor(290/h), sigma_h) per horizon is a lead decision; I did not run it (the brief forbids new
   computation from data, and the model is E.28's code).

### e.3 Passive entries under V50, and E.31's measured adverse selection

V50 (docs/DECISIONS.md, 2026-10-23): "Limit orders stay allowed as an execution method for a directional signal.
They are not a source of edge in themselves. Any later stage prices its fills under the trade-through rule unless a
firm documents otherwise." Under that rule E.31 measured, for a resting 1-lot at the ZM touch (front month, day
session, 85,568 placements): fill rate 0.515, half-spread captured -0.425 ticks, 10 s markout vs mid -0.545, gross
10 s edge -0.970 [-0.988, -0.950], and -1.234 net of Topstep's fee per fill (E.31_RETURN.md section 3.5).

What this means for a directional entry (my arithmetic on those numbers, not a new statistic):
- A market buy pays half the spread, 0.5 tick at a 1-tick market, relative to the mid at entry.
- A trade-through passive buy that fills sits 0.425 tick worse than the mid at the fill (the half-spread captured is
  negative because the fill only happens after the level trades through), a saving of only 0.5 - 0.425 = 0.075
  tick over the market order; then, unconditionally, the mid moves another 0.545 tick against it within 10 s, and
  48.5% of the orders do not fill.
- For a directional signal the selection is worse than unconditional: the orders that fill are those where price
  moved through the limit, i.e., against the forecast, and the missed fills are the ones where the forecast was right
  at once. A passive entry therefore cannot be costed with the unconditional E.31 number; it must be simulated per
  signal under the trade-through rule, and the comparison "market versus passive entry" is one more configuration.
- Base case for E.33: market-order entry and exit, executable labels (e.4). Passive entry: a declared variant.

### e.4 Equations: executable versus mid labels, latency and depth

Long trade decided at t, sent at t, arriving at t + L, held h minutes (prices in ticks):
    R^exec = B_{t+L+h} - A_{t+L} - f - slip(q, book_{t+L}) - slip(q, book_{t+L+h}),
    R^mid  = M_{t+h} - M_t.
With A = M + s/2 and B = M - s/2 (s the quoted spread):
    R^exec - R^mid = (M_{t+L+h} - M_{t+h}) - (M_{t+L} - M_t) - (s_{t+L} + s_{t+L+h}) / 2 - f - slip terms.
- Spread bias: E[(s_entry + s_exit)/2] = 1 tick when both spreads are 1 tick; it is deterministic in sign, so a
  model trained on R^mid with a zero threshold labels as "up" every case with 0 < R^mid <= 1.528, all of which lose
  after costs.
- Latency term: (M_{t+L} - M_t) has, under A1, sd sigma_1m x sqrt(L / 60 s): L = 0.3 s gives 3.15 x sqrt(0.005) =
  0.223 tick; L = 1.0 s gives 3.15 x sqrt(1/60) = 0.407 tick (M3_calc.out). Its mean is zero for a signal that
  accrues linearly over h (the fraction lost is L / h: 1 s / 60 s = 1.7% of the edge at h = 1 min, 0.11% at 15 min),
  but it is negative and possibly large for front-loaded signals (sweep and refill, the first minutes after a
  release), where most of the predicted move happens in the first seconds.
- Last-trade labels (mlfinpy's `close`): with a 1-tick spread, last-trade changes carry bid-ask bounce with
  Cov(DeltaP_t, DeltaP_{t-1}) = -s^2/4 = -0.25 tick^2 (Roll's model, standard result [no fetched source]). A feature
  that knows whether the last print hit the bid or the ask then "predicts" the next last-trade change through bounce
  alone, an edge that disappears in R^exec.
- Depth: slip(q, book) = (VWAP of walking q contracts into the opposite side) - touch price; zero for q = 1 unless
  the touch is empty or implied liquidity is not displayed (E.31's 5.5%).

### e.5 Worked example on the standard ZM numbers

A 15-minute long signal forecasting +2.0 ticks of mid move (0.164 sigma_15; 2.0 / 12.20 = 0.164):
1. Mid-label view: +2.0 > 0, labelled "up", counted as a win.
2. Executable view: 2.0 - 1.0 (spread, 1-tick both ends) - 0.528 (fee) = +0.472 ticks gross of account economics;
   minus the 0.062 residual = +0.41 ticks. Against the E.28 break-even it is 2.0 - 1.59 = +0.41. Same answer.
3. With L = 1 s on a front-loaded signal that realises half its move in the first second (an illustrative
   assumption, not a measurement): the entry is 1.0 tick later, so 2.0 - 1.0 - 1.59 = -0.59 ticks: a winner on mid
   labels, a loser on executable ones.
4. A +1.2-tick forecast is "up" on mid labels and 1.2 - 1.59 = -0.39 net: every such row is a mislabelled loss.
   Under A1 the share of 15-minute mid moves between 0 and +1.528 ticks is Phi(1.528 / 12.20) - 0.5 =
   Phi(0.1252) - 0.5 = 0.5498 - 0.5 = 0.0498, about 5% of all rows (10% counting both signs).
Check: Phi(0.1252) from the series Phi(x) = 0.5 + x/sqrt(2 pi) - x^3/(6 sqrt(2 pi)) = 0.5 + 0.04995 - 0.00013 =
0.5498.

### e.6 Data it needs

ZM MBO: best bid and ask, the full visible depth for slippage, and order-level arrival times for latency (ts_recv).
ZS and ZL MBP-1 give only the touch; they are features, not traded, so their slippage does not enter.

### e.7 Leakage and look-ahead traps

1. Entry at the decision-time price (A_t instead of A_{t+L}). Test: rerun labels with L = 0, 0.3 s and 1.0 s; any
   family whose result needs L = 0 is a latency artefact.
2. Mid or last-trade labels in training with executable labels only in the final P&L (or the reverse). Test: one label
   function used everywhere; a unit test on a synthetic book with a 1-tick spread and no mid move must return
   -(1 + 0.528) for a round trip.
3. Spread and depth measured on the full sample and fed back as a per-row cost (the cost model learns from the
   label window). Test: the cost per row uses only the book at t + L and t + L + h, never averages that include
   the test fold.
4. Bounce-driven features (last-print side, last-trade change) scoring well on last-trade labels. Test: compare each
   feature's univariate hit rate on last-trade and on executable labels; drop or flag any feature whose edge vanishes.

### e.8 Compute

Executable labels need the book at two instants per label: a lookup into the per-date rebuilt book, 236,640 starts x
2 lookups per horizon. Depth walking for q = 1 is a touch check. Minutes in total.

### e.9 Verdict

USE executable labels (market entry and exit, latency L as a declared parameter with at least two values, depth
from MBO) as the only training and evaluation target. Use mid labels only as a diagnostic, never for selection.
Record the 1.59 as E.28's model value with its three caveats; E.33 should replace the default 1-tick spread by the
measured mean spread a 1-lot market order pays (a cost input).

### e.10 Evidence table

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| ZM Topstep break-even 1.59 (market), 0.59 (limit) | E.28 ranking (program record) | "\| 6 \| topstep \| ZM \| 2.69 \| ... \| 0.59 \| 1.59 \| 0.86 \| 49.23 \| 2.08 \| ok \|  \|" | reports/stage_e28_ranking.md line 130 |
| c_mkt = fee + spread, spread 1 if unknown | E.28 ranking spec | "Market case c_mkt = F_rt + S_rt, with S_rt the sourced median main-session spread in ticks (1 if unknown)" | reports/stage_e28_ranking_spec.md lines 118-119 |
| ZM spread was the default | E.28 econ record | "S_rt_note": "default 1 (u): no sourced median" | reports/stage_e28_briefs/A3_econ.json (topstep ZM record) |
| Fee 5.28 USD | E.28 econ record citing the Topstep page | "quote": "$5.28" ... "commission+NFA+exchange; per side = RT/2" | same (F_rt_source) |
| Mid-to-mid labels are not tradable | Lucchese, Pakkanen, Veraart 2024 (academic) | "we focus on mid-to-mid returns, which are not tradable in practice. When considering specific trading applications, one should thus define the return labels appropriately, for example, working with ask-to-bid returns." | lucchese2024_predictability.txt lines 1342-1343 |
| Mid price is not a transaction price | Zhang, Zohren, Roberts 2019 (DeepLOB, academic) | "Although no order can transact exactly at the mid-price" | deeplob_zhang2019.txt line 242 |
| Trade-through passive fills lose about 1 tick in 10 s | E.31 (program measurement) | "10 s edge E_10, mean \| -0.287 [-0.303, -0.273] \| -0.252 [-0.267, -0.239] \| -0.970 [-0.988, -0.950]" | reports/E.31_RETURN.md section 3.5 |
| Limit orders allowed only as execution | V50 (user decision) | "Limit orders stay allowed as an execution method for a directional signal. They are not a source of edge in themselves." | docs/DECISIONS.md (V50 item 2) |
| Implied or undisplayed liquidity | E.31 | "5.5% of aggressor prints (3.6% of their volume) found no displayed resting quantity at their price" | reports/E.31_RETURN.md section 3.5 |
| Latency of 300-1,000 ms | planner claim; no primary source | vendor and blog pages (copier and auto-trader vendors, 5-50 ms claims) are pointers only, not evidence | [unverified] |

---

## (f) The cost-aware target: dead-zone classification, regression net of cost, the expected-value threshold

### f.1 Core idea

The target must already contain the cost, so the model is never rewarded for predicting moves too small to trade.
Three equivalent ways: (1) a three-class label whose middle class is "no trade pays", (2) a regression on the net
executable return, traded only when the forecast exceeds zero, (3) a probability of "up" traded only when the implied
expected value clears the cost. Whatever the form, the per-trade net edge required is the same 1.59 ticks at every
horizon; what changes with h is how small that is relative to the noise, and how many independent trades there are
to prove it.

### f.2 Equations

- Executable three-class label (my construction from b.2/e.4; L and h fixed):
      N_long = B_{t+L+h} - A_{t+L} - c_x,   N_short = B_{t+L} - A_{t+L+h} - c_x,   c_x = f + account residual,
      y = +1 if N_long > 0;  -1 if N_short > 0;  0 otherwise.
  The two cannot both be positive: N_long + N_short = -(s_{t+L} + s_{t+L+h}) - 2 c_x < 0. So the dead zone is not a
  tuned threshold tau: it is the spread plus costs, about |M_{t+L+h} - M_{t+L}| <= 1.59 ticks at 1-tick spreads.
  (Contrast the fixed-tau labels of the source, "0 if |r| <= tau", lopezdeprado_2018_10reasons_jpm.txt lines 327-334,
  and DeepLOB's threshold alpha on smoothed mid changes, deeplob_zhang2019.txt lines 280-283.)
- Regression net of cost: target N_long (or the signed net return for the side chosen); trade long if
  E_hat[M_{t+L+h} - M_{t+L} | X] > BE, short if < -BE. The decision rule is "forecast mid move beyond +-BE".
- Classifier with probability q = P(M_{t+h} > M_t | X) and symmetric magnitudes (A1: the size of the move is
  independent of its sign and of X): expected net of a long = (2q - 1) E|DeltaM_h| - BE, so act iff
      q > q* = 1/2 + BE / (2 E|DeltaM_h|),   E|DeltaM_h| = sigma_h x sqrt(2/pi) = 0.7979 sigma_h.
  For a classifier whose hits are on larger moves than its misses the needed q is lower, and vice versa; the
  calibration of q and of the magnitudes is part of the test, not an assumption to keep.
- Symmetric barriers +-k with all exits on a barrier: q* = (k + BE) / (2k) = 1/2 + BE / (2k).
- Per-trade Sharpe at hit rate p with +-k barriers: SR_trade = ((2p - 1) k - BE) / (2k sqrt(p(1 - p))).
- Detectability over the discovery window (my addition): with n non-overlapping day-session trades,
  n = 816 x floor(290 / h), the sd of an observed hit rate near 0.5 is 0.5 / sqrt(n); a classifier sitting exactly at
  q* shows a t-statistic (q* - 0.5) / (0.5 / sqrt(n)) against "no skill", and needs q* + 3 x 0.5 / sqrt(n) to show
  net skill above break-even at t = 3 (ignoring the deflation that N adds).
[MathReview B-27 (lead: accepted): q* + 3 x 0.5/sqrt(n) is the observed hit rate at which the realised t equals 3, not the true hit rate at which a t = 3 test has a stated power; at 80% power it is q* + (3 + 0.8416) x 0.5/sqrt(n): h = 60: 0.5745 (not 0.5671); h = 120: 0.5764; h = 15: 0.5971. Relabel the f.3 table's last column (original line 656) "observed hit rate giving t = 3" or add the power column, and read reading item 2 (original lines 671-675) the same way; the 60-120 min band is the same either way.]

### f.3 Worked example: the per-horizon table (A1, BE = 1.59 ticks)

Row h = 15 by hand: sigma_15 = 3.15 x sqrt(15) = 3.15 x 3.8730 = 12.200 ticks; E|DeltaM| = 12.200 x 0.79788 = 9.734;
q* = 0.5 + 1.59 / (2 x 9.734) = 0.5 + 1.59 / 19.468 = 0.5 + 0.0817 = 0.5817; BE / sigma_15 = 1.59 / 12.200 = 0.1303;
barriers at +-sigma_15: q* = 0.5 + 1.59 / 24.40 = 0.5652; n = 816 x floor(290/15) = 816 x 19 = 15,504;
se = 0.5 / 124.5 = 0.00402; t at q* = 0.0817 / 0.00402 = 20.3.

| Horizon h (min) | sigma_h (ticks) | E\|DeltaM_h\| (ticks) | Net edge needed, BE/sigma_h (sd units) | q* fixed horizon, sign classifier | q* fixed horizon at c_mkt = 1.528 | q* barriers +-sigma_h (37% end at vertical) | q* barriers +-2 sigma_h (91% end at vertical) | Non-overlapping day trades in 816 dates | t of a classifier exactly at q* | q needed for net skill at t = 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 3.150 | 2.513 | 0.505 | 0.816 | 0.804 | 0.752 | 0.626 | 236,640 | 307.7 | 0.819 |
| 5 | 7.044 | 5.620 | 0.226 | 0.642 | 0.636 | 0.613 | 0.556 | 47,328 | 61.6 | 0.648 |
| 15 | 12.200 | 9.734 | 0.130 | 0.582 | 0.579 | 0.565 | 0.533 | 15,504 | 20.3 | 0.594 |
| 30 | 17.253 | 13.766 | 0.092 | 0.558 | 0.556 | 0.546 | 0.523 | 7,344 | 9.9 | 0.575 |
| 60 | 24.400 | 19.468 | 0.065 | 0.541 | 0.539 | 0.533 | 0.516 | 3,264 | 4.7 | 0.567 |
| 120 | 34.507 | 27.532 | 0.046 | 0.529 | 0.528 | 0.523 | 0.512 | 1,632 | 2.3 | 0.566 |
| 240 | 48.800 | 38.936 | 0.033 | 0.520 | 0.520 | 0.516 | 0.508 | 816 | 1.2 | 0.573 |
| to close, entry 08:30 (h = 290) | 53.643 | 42.801 | 0.030 | 0.519 | 0.518 | 0.515 | 0.507 | 816 | 1.1 | 0.571 |
| to close, uniform entry (equivalent h = 128.9) | 35.762 | 28.534 | 0.044 | 0.528 | 0.527 | 0.522 | 0.511 | (one per day) | - | - |

Reading the table:
1. The edge required per trade is 1.59 ticks at every horizon. In sd units it falls from 0.51 at 1 minute to 0.03 at
   the close, so the hit rate needed falls from 82% to 52%.
2. The sample to prove it falls faster. A classifier exactly at break-even is invisible (t = 1.1-1.2) at 240 minutes
   and to the close, and only at 60-120 minutes do "needs to be right 54-57% of the time" and "can be shown at t = 3"
   meet. The hit rate needed for a t = 3 demonstration of net skill is lowest, about 0.566-0.567, at 60-120 minutes,
   and rises on both sides (0.594 at 15 minutes, 0.573 at 240), before any multiple-testing deflation and with every
   day-session window traded. A model that trades a subset has fewer trades and needs more.
3. Under A1 a +-5-tick barrier needs q* = 0.659 (b.3); a 5-minute fixed-horizon classifier needs 0.642. They are the
   same short-horizon regime.
4. The dead zone is small at minutes horizons: P(|DeltaM_h| <= 1.59) under A1 is 2 Phi(1.59 / sigma_h) - 1 =
   0.179 at 5 minutes (1.59 / 7.044 = 0.2257; Phi = 0.5893), 0.104 at 15 and 0.052 at 60 (M3_calc.out). Most rows are
   +1 or -1; the dead zone mainly removes the cases where a mid label would be wrong after costs.
5. Per-trade Sharpe at 2 points above break-even with +-5 barriers: p = 0.68, mean (2 x 0.68 - 1) x 5 - 1.59 = 1.80
   - 1.59 = 0.21 ticks, sd 2 x 5 x sqrt(0.68 x 0.32) = 10 x 0.4665 = 4.665 ticks, SR_trade = 0.045 (M3_calc.out).
Check (row 60): 3.15 x 7.746 = 24.40; x 0.79788 = 19.47; 1.59 / 38.94 = 0.0408; q* = 0.5408; n = 816 x 4 = 3,264,
sqrt = 57.13, se = 0.00875, t = 0.0408 / 0.00875 = 4.66; q for t = 3 = 0.5408 + 0.0263 = 0.5671. Matches the table.
Relation to M1 (M1_order_flow.md section 1): M1 states the same 1.59-tick hurdle as an out-of-sample R-squared for a
normal regression forecast (0.0267 at 15 minutes, trading every bar). This table states it as a sign hit rate with
magnitudes independent of the sign. The two rest on different forecast models and are not converted into each other
here; both fall as 1/h (R-squared) or 1/sqrt(h) (excess hit rate) under A1.

Limits of the table: A1 understates noise around the open and releases (where signals fire) and treats ZM overnight
as if it had the day's sigma; the trade count uses all 816 dates before exclusions (E.31 kept 764 day-session dates
after its roll and holiday exclusions, which lowers every n by 6%); and BE's own caveats (e.2) apply.

### f.4 Data it needs

As e.6. The table itself needs only the brief's standard numbers.

### f.5 Leakage and look-ahead traps

1. The dead-zone width or q-threshold set from the test-fold cost or class balance. Test: thresholds from the
   protocol (BE, L) only; assert no data-derived threshold.
2. Class rebalancing (up-sampling the minority class, as in the meta-labeling evidence E.28 2.7 s3.8 cites) that
   changes the base rate the threshold assumes. Test: evaluate at the natural class frequencies of the test fold.
3. Choosing the horizon after seeing which one works and reporting it as one trial. Test: every horizon in the
   declared set is run and reported, and N counts all of them.
4. Calibration: q from a GBM is not a probability until calibrated within the training folds. Test: reliability curve
   on purged validation folds; the q > q* rule uses calibrated q.
5. Smoothed labels that contain the past. DeepLOB's second label, l_t = (m+(t) - m-(t)) / m-(t), with m-(t) "the mean
   of the previous k mid-prices" (deeplob_zhang2019.txt lines 251-253, the paper's eqs. 2 and 4), is partly known at t: any feature built from
   the last k mids predicts it without forecasting anything. Test: regress the label on the trailing k-mid mean
   alone; a non-zero out-of-sample fit flags the leak. Use only labels built from prices strictly after t + L.

### f.6 Compute

Negligible beyond the labels themselves.

### f.7 Verdict

USE the executable three-class label (dead zone = spread + costs) as the classification target and the net
executable return as the regression target, with the EV rule q > q*(h) or |forecast| > BE. Report hit rate, mean net
ticks per trade and n_eff for each horizon. Given the detectability column, the 60- and 120-minute horizons are where a
modest classifier could be both profitable and provable; the 1- and 5-minute labels need
hit rates (64-82%) that no published order-book model at those horizons reports (E.28 2.9 s8.3 found the same for
MES), and the 240-minute and to-close labels can be profitable but are not provable on 39 months at break-even.

### f.8 Evidence table

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Fixed-threshold three-class label | Lopez de Prado 2018 (JPM) | "where 𝜏 is a pre-defined constant threshold" | lopezdeprado_2018_10reasons_jpm.txt line 334 |
| Threshold labels on mid changes | Zhang, Zohren, Roberts 2019 (DeepLOB) | "The labels are then decided based on a threshold (α) for the percentage change (lt ). If lt > α or lt < −α, we define it as up (+1) or down (−1). For anything else, we consider it as stationary (0)." | deeplob_zhang2019.txt lines 280-283 (left column) |
| Noisy labels cost trades | same | "signals are not consistent here leading to many redundant trading actions thus incurring larger transaction costs" | same, lines 294-295 (left column) |
| q*, detectability, Sharpe link | my derivations under A1 and A2 | - | work/M3_labels/M3_calc.py, M3_calc.out |

---

## (g) Event-time sampling rules that avoid release windows, rolls, and the open and close

### g.1 Core idea

A label start (and every minute a label spans) must sit in a market state the strategy could trade in and that the
family is about. Scheduled releases, the 08:30 open after the pre-open, the 13:14-13:15 settlement window, rolls and
limit locks each produce price moves of a different kind; unless a family is about one of them, labels that touch
them mix regimes and inflate both apparent skill and apparent noise. The windows must come from published calendars
fixed in advance, never from the data.

### g.2 The CBOT grain grid and what is (and is not) an auction

- Sessions (CT), unchanged across both the discovery window and the sealed test window: overnight Sun-Fri 19:00-07:45,
  day Mon-Fri 08:30-13:20, settlement window 13:14-13:15 (R4_events.md section 1.1, from CBOT Submission 15-204 and
  the 2013-03-13 filing that R4 saved). The 2015 filing: the extension lets TAS trade "until 1:15 p.m./CT" and
  "would allow TAS liquidity providers to hedge or trade as needed after 1:15 p.m./CT and not impact or influence the
  1:14-1:15 p.m. CT settlement window" (R4_cftc_cbot_2015_hours_1320.txt lines 88-90).
- Pre-open: a CBOT filing for grain weekly options (options on the same futures) lists "CME Globex Pre-Open: Sunday:
  4:00 p.m. - 7:00 p.m. CT, Monday - Thursday: 4:45 p.m. - 7:00 p.m. CT and Monday - Friday: 8:00 a.m. - 8:30 a.m. CT"
  (R4_cftc_cbot_sub25-045.txt lines 141-147; en dashes in the original). That the futures pre-open has the same
  times is my inference from the shared Globex hours in the same table [unverified for the futures themselves].
- So the "open auction" is the Globex pre-open ending in the 08:30 opening (and the 19:00 opening overnight); its
  matching mechanics (indicative opening price, uncross) come from CME Globex documentation, which this stage may not
  fetch [unverified]. There is no closing auction: the "close" is a one-minute settlement VWAP window (R4 1.1:
  "VWAP of all trades ... in the settlement minute", from the 2012 change), and Globex keeps trading to 13:20.

### g.3 The rules (a declared set for the lead to adopt or change; each alternative counts in N if compared)

Let W be the set of excluded minutes. A label i with start t_i and span [t_i, t_i + L + h] is kept only if its
whole span lies inside one session of one instrument_id and does not intersect W, unless the family's own event is
the excluded window (then the family declares its own start rule, e.g. "enter at release + 5 minutes").

1. Open: W includes 08:30:00-08:30:00 + D_open (D_open = 5 minutes as a default) and 19:00:00-19:00:00 + D_open.
   Label starts in 08:00-08:30 (pre-open, no executable book) are impossible by construction (no ask and bid to
   trade). Families about the overnight gap at the open (planner family 4) start at 08:30 + D_open by declaration.
2. Close: labels must end by 13:13:00 (one minute before the settlement window); the "to close" label exits at an
   executable price at 13:13:00. A variant ending at 13:19 (after settlement, still trading) is one more
   configuration. Overnight labels end by 07:44.
3. Releases (11:00 CT on WASDE, Crop Production, Grain Stocks, Prospective Plantings, Acreage days; NOPA 11:00 CT;
   R4_events.md section 1.2): W includes [release - 2 minutes, release + D_rel], D_rel = 30 minutes as a default for
   non-event families. Evidence on disk: E.31's passive fills "0-5 minutes after a USDA release" averaged -8.98 ticks
   (68 fills; reports/E.31_RETURN.md section 3.5); Huang (2022) has about 75% of the hour's corn move done by 10
   minutes and Joseph and Garcia (2016) report variance above control for 30-40 minutes on soybeans (as tabulated in
   R4_events.md section 2.1). The planner's "first 1-2 minutes" is shorter than any of these windows (planner
   pointer 2). Event families use release + 5 to 15 minutes as their start (R4 2.4).
4. Overnight releases and closed-market news: Thursday export sales at 07:30 CT fall in the overnight session,
   15 minutes before the pause; Crop Progress at 15:00 CT (if ET is right) falls while closed and is absorbed at
   19:00 (R4 1.2). W includes 07:28-07:44 on Thursdays for overnight labels; day labels are unaffected except
   through the open (rule 1).
5. Rolls: no span crosses an instrument_id change in ZM.v.0; exclude the roll date and the next trade date (E.31's
   precedent: "23 roll days, 20 days after a roll" excluded; E.31_RETURN.md section 3.5). ZS and ZL features are
   read from their own front contracts; a feature roll inside the lookback is flagged and the row dropped.
6. Daily limits: exclude any span during which the ZM book has no bid or no ask (limit-locked or halted); R4 section 3
   covers the limit rule. Count such minutes and report them.
7. Holidays and early closes: use the repo's grain calendar; drop early-close dates entirely (E.31 dropped 4 holidays
   or early closes and 5 late opens).
8. Overnight as a separate stratum: report overnight labels separately and do not pool them with day labels in
   selection (A0: median overnight volume 2 contracts a minute against 71 in the day session).

### g.4 Worked example on the standard ZM numbers: how many 15-minute label starts survive on a WASDE day

Day session 290 minutes; 15-minute labels need t_i + 15 <= the end of the allowed day, and L is ignored here.
1. Allowed span for label minutes: 08:35 to 13:13 = 278 minutes (open exclusion 5, close cut-off 7 minutes before
   13:20: 290 - 5 - 7 = 278).
2. Release window on a WASDE day: 10:58 to 11:30 = 32 minutes in W.
3. Start minutes on an ordinary day: 278 - 15 + 1 = 264 starts (t_i from 08:35 to 13:13 - 15 = 12:58).
4. On a WASDE day a start t is excluded if [t, t + 15] meets [10:58, 11:30]: t from 10:43 to 11:30, 48 minutes
   (10:43 + 15 = 10:58 touches the window; 11:30 is its last minute). Kept: 264 - 48 = 216 starts.
5. n_eff on the WASDE day: two clean blocks, 08:35-10:58 (143 minutes) and 11:30-13:13 (103 minutes), so
   n_eff = (143 + 103) / 15 = 16.4 non-overlapping windows (section d's closed form, with each block's covered
   bars), against 278 / 15 = 18.5 on an ordinary day.
Check: 216 / 264 = 0.818 of starts and 16.4 / 18.5 = 0.886 of effective information survive; about 15 such release
days a year (R4 2.4) cost 15 x (18.53 - 16.40) = 32 effective 15-minute windows a year, under 0.7% of the year's
roughly 250 x 18.5 = 4,625 (32 / 4,625 = 0.69%).

### g.5 Data it needs

A release calendar (dates and minutes) built from the publishers' schedules, the repo grain calendar (sessions,
holidays, early closes), ZM.v.0 instrument_id changes from the definitions schema, and the rebuilt book for the
no-bid/no-ask test.

### g.6 Leakage and look-ahead traps

1. Exclusion windows detected from the data (volatility spikes, volume bursts) instead of the published calendar.
   That makes W depend on the outcome. Test: W is a function of the calendar file and timestamps only; rebuild W
   without loading any price and assert equality.
2. Release dates known only after the fact (rescheduled or cancelled releases, e.g. shutdown years). Test: the
   calendar records the scheduled date as known on the day before; any change is logged with its announcement date.
3. Roll detection from the volume crossover inside the label window (Databento's v.0 is volume-ranked). Test: roll
   dates from the definitions or a fixed calendar rule; compare to v.0's instrument_id switches and report mismatches.
4. Asymmetric exclusions that keep winners (for example dropping only days with a large adverse move). Test: every
   exclusion rule is a declared function of calendar fields; count kept and dropped labels per rule.

### g.7 Compute

Negligible: interval arithmetic on a few hundred calendar windows.

### g.8 Verdict

USE all eight rules, with D_open, the close cut-off and D_rel declared once in the protocol (alternatives counted in
N). The sampling of label starts inside the allowed windows: every minute (with n_eff reporting) as the default, and a
CUSUM event filter (section a) as one declared variant per family.

### g.9 Evidence table

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Settlement window 13:14-13:15 CT, trading to 13:20 | CBOT 2015 filing (exchange, CFTC-hosted, saved by R4) | "not impact or influence the 1:14-1:15 p.m. CT settlement window" | R4_events pages: R4_cftc_cbot_2015_hours_1320.txt line 90 |
| Day session 08:30-13:20 | same | "Monday – Friday, 8:30 a.m. – 1:20 p.m. CT" (new hours column) | same, line 78 |
| Grain pre-open times | CBOT Submission 25-045 (grain weekly options, exchange, CFTC-hosted, saved by R4) | "CME Globex Pre-Open: Sunday: 4:00 p.m. – 7:00 p.m. CT Monday – Thursday: 4:45 p.m. – 7:00 p.m. CT and Monday – Friday: 8:00 a.m. – 8:30 a.m. CT" | R4_events pages: R4_cftc_cbot_sub25-045.txt lines 141-144 |
| Release times and stacking | R4_events.md (E.32 worker, sourced there) | "WASDE ... 12:00 p.m. ET \| 11:00 \| day session" | reports/stage_e32_briefs/R4_events.md section 1.2 |
| Post-release passive fills | E.31 (program measurement) | "fills 0-5 minutes after a USDA release -8.98 (68 fills)" | reports/E.31_RETURN.md section 3.5 |
| E.31's exclusion precedent | E.31 | "Exclusions, front month: 52 of 816 dates (23 roll days, 20 days after a roll, 4 holidays or early closes, 5 late opens)" | reports/E.31_RETURN.md section 3.5 |
| Futures pre-open equals options pre-open; opening-match mechanics | - | - | [unverified]; CME documentation not fetched (stage CME rule) |
| CFTC pages were not fetched by M3 | cftc.gov robots.txt | "User-agent: ClaudeBot / Disallow: /" and "Content-Signal: search=yes,ai-train=no,use=reference" | log.tsv (terms decision, 2026-10-27 00:29 PDT) |

---

## Planner pointers owned by M3 (reports/stage_e32_inputs/planner_research_soy_complex.md lines 110-111 and 123-124)

| Pointer (verbatim) | Status | What the evidence and arithmetic show |
|---|---|---|
| "Labels at 5, 15, 30, 60, 120 and 240 minutes and to the session close, net of 1.6 ticks, plus a triple-barrier label at about +-4-6 ticks." | PARTLY VERIFIED | The 1.6 ticks is E.28's mu*_mkt = 1.59 for Topstep x ZM (ranking line 130), but it is a model value: 0.528 fee + 1.0 default (unsourced) spread + 0.062 account economics, zero slippage, solved at a 1-minute holding scale (e.2). The horizon set is workable; per f.3, the hit rate needed to show net skill at t = 3 is lowest (about 0.566) at 60-120 minutes and higher on both sides (0.594 at 15, 0.648 at 5, 0.573 at 240 minutes); at 240 minutes and to the close a classifier exactly at break-even (about 52%) gives t = 1.1-1.2 on 39 months. The +-4-6 tick triple barrier does not belong with these horizons: under A1 its mean exit time is 1.6-3.6 minutes (95% by 4.2-9.5 minutes) and it needs a 63-70% hit rate (b.3); barriers should scale as kappa x sigma_hat x sqrt(h). "Net of 1.6 ticks" must mean executable labels (buy at the ask, sell at the bid, after latency), not mid labels minus a constant, because the spread part varies by minute. |
| "Market-order execution with depth-conditioned slippage and 300-1,000 ms latency, excluding the first 1-2 minutes after releases." | PARTLY VERIFIED | Market orders as the base case agree with V50 (limit orders are execution only, priced by trade-through; E.31's trade-through fills lose 0.970 ticks gross in 10 s), e.3. Depth-conditioned slippage is supported by E.31's implied-liquidity finding (5.5% of aggressor prints met no displayed quantity) and is computable from ZM MBO (not from ZS/ZL MBP-1), e.4. The 300-1,000 ms latency is UNVERIFIED: no primary source states a TopstepX or ProjectX latency; vendor and blog pages claim 5-50 ms and are pointers only; the program's own note is "tens of milliseconds" network latency to Aurora (E.28 READER_RULES, not a measurement). As a conservative stress range it costs little at minutes horizons (sd 0.22-0.41 ticks; under 2% of a linear 1-minute edge) but matters for front-loaded signals; declare L in {0.3, 1.0} s. The "first 1-2 minutes after releases" exclusion is shorter than the evidence on disk: E.31's 0-5-minute post-USDA bucket averaged -8.98 ticks per passive fill and the literature R4 tabulates has 75% of the move by 10 minutes and elevated variance for 30-60 minutes; g.3 proposes [release - 2, release + 30] for non-event families. |

## Compute summary (ThinkPad, 39 months)

All label, weight and exclusion work is a few passes over the rebuilt ZM book: minutes per horizon, under 1 GB per
trade date, parallel by date (at most 8 processes, nice 10). The only infeasible item is mlfinpy's sequential
bootstrap on 225,216 labels (about 7.6 x 10^11 operations); per-date sequential bootstrap or a day-block bootstrap
replaces it (d.6). No GPU is needed.

## Verdicts in one table

| Topic | Verdict | Reason |
|---|---|---|
| 1-minute clock grid for features and labels | USE | horizons, account rules and calendars are clock-based; simplest purging |
| CUSUM event filter for label starts | USE (one declared threshold per family, in N) | conditions on "something happened"; cheap |
| Volume bars | MAYBE (one robustness variant) | statistical gains only; no evidence of predictive gain |
| Dollar, imbalance and run bars | SKIP | no corporate actions; imbalance belongs in features |
| Fixed-horizon executable labels | USE (primary target) | maps one-to-one to the trade |
| Triple barrier at kappa x sigma_hat x sqrt(h) | MAYBE (one kappa, in N) | exit realism; no evidence of predictive gain |
| Fixed +-4-6 tick barriers | SKIP for the multi-horizon set | a 2-7-minute label needing 63-70% hits |
| To-close label | USE, exit 13:13, scaled by sigma_{h(u)} | needs the shortest hit rate (52%) but least provable |
| Meta-labeling | MAYBE (for signed primary rules) | sound architecture, sample-size bound; no independent cost-inclusive evidence |
| Uniqueness weights, n_eff, day-block inference | USE | 15-minute labels sampled each minute carry 1/15 of their row count |
| Time decay, sequential bootstrap | SKIP | an extra configuration without a prior; compute |
| Executable labels with latency and depth | USE (only training and selection target) | mid labels are about 1 tick a round trip too optimistic |
| Dead-zone three-class label and EV threshold | USE | dead zone = spread + costs, not a tuned tau |
| Exclusion rules g.3 (1-8) | USE | calendar-based; declared once |

## Stopping rule, null results and gaps

- Bar types (a): 4 full texts; last discovery queries (arXiv API for "dollar bars", "volume bars", "volume clock" in
  q-fin; one WebSearch) surfaced nothing beyond those. Ane and Geman (2000) itself not read (paywalled) [unverified].
- Triple barrier versus fixed horizon (b): no head-to-head, cost-inclusive out-of-sample comparison found (as in E.28
  2.7 s2.8); arXiv q-fin "triple barrier" query returned two papers (2404.01866, 2411.12753), both using the label
  without a fixed-horizon control (abstract only for 2404.01866 [unverified beyond the abstract]).
- Meta-labeling (c): no new independent evidence (one WebSearch, one Crossref query, 2026-10-27); E.28's null result
  stands.
- Sample weights (d): no independent evidence that uniqueness weighting improves out-of-sample results (as in E.28
  2.7 s4.8); the effective-count argument is standard and needs none.
- Costs (e): the ZM market-order spread a 1-lot actually pays is not on disk as a sourced number (E.28 used a default);
  Topstep's simulated market-order fill rule (does a market order walk the book, or fill at the touch regardless of
  depth?) was not looked up here [unverified]; it decides whether depth-conditioned slippage applies at all at the
  firm. TopstepX latency: no primary source (5-50 ms vendor claims are pointers only).
- Sessions (g): cftc.gov was not fetched by this worker because its robots.txt disallows ClaudeBot and anthropic-ai
  (logged). Other E.32 workers did fetch CFTC filings; the lead may want to review that against the terms rule.
  Futures pre-open times and the opening-match mechanics are [unverified] (options filing only; CME docs not fetched).
- WebSearch calls used: 4 of 80. No budget notice was seen.
- Every number here assumes A1 (random-walk scaling of sigma_1m = 3.15) and A2 (BE = 1.59); none was computed from
  market data.
