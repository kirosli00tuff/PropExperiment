# Stage E.32 discovery protocol for E.33: ZM directional signal search (Part P)

Status: FROZEN v1.0 (2026-10-27, lead Opus 5.5 xhigh; DRAFT v0.6 after the ProtocolReviewer, FixVerifier,
FixSpotCheck and FinalDiffCheck rounds, plus one consistency edit in P10). The frozen version carries its sha256 in
reports/stage_e32_discovery_protocol.sha256 and in reports/E.32_RETURN.md; any later edit voids the freeze.

E.33 runs this protocol unchanged on the owned ZM, ZS and ZL data of 2020-12-01..2024-02-29. Nothing in it was
chosen by looking at an outcome: E.32 trained nothing and computed no feature value, label, return or markout
(stage scope). Sources: the methods brief reports/stage_e32_methods_brief.md and its reader files under
reports/stage_e32_briefs/ (cited as M1..M6, R1..R5, F = reports/stage_e32_data_facts.md, X1), the MathReviewer
files under reports/stage_e32_briefs/review/, the program's code, and docs/DECISIONS.md.

## 0. What binds, change control and notation

### 0.1 Binding sources
- V43 (docs/DECISIONS.md 788-809): model, features, labels, training window, hyperparameters and code frozen and
  hashed before any outcome; every configuration searched counts into N; purged and embargoed CV on discovery;
  one test on data that never selected the model, with the program's bar (Holm, net Sharpe, DSR at N, PBO); costs
  from the measured fill model, never touched-means-filled.
- V50: passive fills priced under the trade-through rule unless a firm documents otherwise; E.31 read the discovery
  dates (item 4).
- V51: discovery = owned 2020-12..2024-02; test = sealed 2017-05-01..2020-11-30 (reports/stage_e32_test_seal.md);
  2024-03 onward closed.
- V14 (b) Holm K = 9 and (c) the DSR variance rule, as coded in screening/stage_e_verdict.py (harness v14,
  2e908c81...).
- This document.

### 0.2 Change control
- E.33 may fix code so that the code does what this text says. Every fix is logged with the line of this text it
  restores, and the frozen pipeline hash is re-taken before the first real outcome.
- E.33 may not change any declared choice (data, sessions, exclusions, labels, features, normalisations, models,
  grids, folds, metric, gates, ranking, budget). If a declared choice cannot be implemented as written (a library
  lacks the option, compute exceeds the P10 limit), E.33 stops that part and reports; configurations already run
  stay counted in N. An amendment is a new protocol version decided by the user and hashed before it runs.
- A detail this text does not settle and that can affect an outcome is decided by E.33 in the most conservative
  way and logged (E.33 prompt). Every such reading is written by E.33's lead, before the C1 registration, into
  reports/stage_e33_protocol_readings.md (per entry: the protocol line, the readings considered, the one chosen and
  why it is the conservative one), and before the B7 freeze (a reading added between the freeze and C1 re-takes the
  freeze list, first bullet); that file's sha256 is a line of the B7 pipeline freeze list, is quoted in
  reports/stage_e33_run_marker.md (the prompt's C1) and is carried in the freeze file of P7.1 (FixSpotCheck S-A-3,
  S-A-4). No reading is made after C1: a question that arises later is answered by that file, and if
  it is not answered there, that part of E.33 stops and reports (second bullet; ProtocolReview DO-1, FixVerifier
  R-W2-2, R-W2-7). P8 is coded and unit-tested on synthetic series before the first real-outcome fit. Details that
  cannot affect an outcome (file layout, names, logging) are E.33's.

### 0.3 Notation
- Times are America/Chicago (CT). A record is known at time u iff its ts_recv <= u. All ordering, look-backs,
  "as of" lookups, label starts and label ends use ts_recv, never ts_event (MathReview C-3). The decision clock
  is the ts_recv clock.
- Trade date D: E.31's convention (measure31.day_bounds), the ts_recv window [D-1 16:00, D 16:00). Day session of
  D: 08:30:00-13:20:00 on D. Overnight session: 19:00 on D-1 to 07:45 on D.
- Fronts: ZM front on D = the instrument_id mapped to ZM.v.0 for UTC date D in the manifests' symbology
  (measure31.instrument_on); ZS front = ZS.v.0; ZL front = ZL.v.0. ZM.v.1 records are never used.
- Ticks: ZM 0.10 USD/short ton = 10 USD; ZS 0.25 cents/bu = 12.50 USD; ZL 0.01 cents/lb = 6 USD. Tick sizes are
  read from the definitions (measure31.read_definitions, checked_tick, with E.31's known ZS/ZL USD-check fix).
- Book: ZM from MBO (mbo_book31.Book, full displayed depth); ZS and ZL from MBP-1 (top of book and trades). bid_m,
  ask_m, qb_m, qa_m: price and displayed quantity of level m (m = 1 is the touch). Mid M_X(u) = (bid_1 + ask_1)/2 as
  of u, defined only when both sides exist, bid_1 < ask_1 and the book is not marked bad (F_MAYBE_BAD_BOOK); spread
  s_X(u) = ask_1 - bid_1.
- sigma_X(D): the SD of 1-minute mid changes of X over all 1-minute intervals inside 08:35-13:13 of the 20 trade
  dates before D (burn-in dates included as history), with valid mids at both ends, chained across rolls (a scale,
  not a level). Constant within D. In ticks of X.
- "Window of k minutes ending at t": the last k minutes of time during which X was open, ending at t (the
  07:45-08:30 pause and the 13:20-19:00 close are skipped; overnight minutes count). Sample points inside a window
  are the minute marks t - j minutes, j = 1..k, on that open-time axis.
- "Trailing 20-date reference" of a statistic: its mean (or median where stated) over the minute marks 08:35-13:13
  of the 20 trade dates before D (burn-in dates included as history).
- Decision grid G_h(D) for label horizon h: t in {08:35:00, 08:36:00, ..., 13:12:00 - h} on D (273, 263, 248, 218
  minutes for h = 5, 15, 30, 60).
- "Book update": the book state after a record that carries F_LAST (the end of one event batch). First-touch
  tests (P3.4), locked-book checks (P3.6 rule 5) and OFI sums (F2.8-F2.11, F3.1-F3.4) step through book updates;
  "as of u" means the last book update with ts_recv <= u (ProtocolReview DO-9). A book update's time is the ts_recv
  of its F_LAST record (FixVerifier R-W2-6).
- Statistics conventions (ProtocolReview DO-12, FE-9, FE-10): every SD in a feature, a normaliser or a fit is the
  population SD (ddof 0); a weighted mean and SD are m = sum w x / sum w and sqrt(sum w (x - m)^2 / sum w); an OLS
  fit is numpy.linalg.lstsq on centred regressors with an intercept, and its residual SD is sqrt(SSR / n).
  Statistics of daily series (mean, SD, Sharpe, skewness, raw kurtosis, t) are those of
  screening/stage_e_verdict.py moments() and t_stat() (population SD; Sharpe = mean / pstdev).
- Latency L = 1.000 s (selection); L = 0.300 s is reported for the test list only (P6.4).
- Fee f = 0.528 ticks per round trip (Topstep, 5.28 USD; reports/stage_e31_inputs/planner_research_notes.md).

### 0.4 Standard numbers (for thresholds and power only; E.33 never uses them in place of a measurement)
ZM sigma_1m 3.15 ticks (E.28 A0, 2022-11..2023-10); sigma_h = 3.15 sqrt(h) under a random-walk assumption; E.28's
market-order break-even 1.59 ticks a round trip (reports/stage_e28_ranking.md line 130: 0.528 fee + 1.000 default
spread + 0.062 account economics; M3 e.2); E.31's gross 10 s edges per passive fill: -0.970 (trade-through),
-0.287 (K), -0.252 (FIFO) (reports/E.31_RETURN.md 185-193).

## P1. Discovery data

### P1.1 Files
- The 156 files of one manifest, sha256 09396842c4fd5d742c166e5b6ca1327c5eeebfed9b112952b84d15f254c23261
  (identical manifest.json in each directory), 24,234,707,848 bytes, under data/vendor/databento/GLBX.MDP3/:
  mbo/Z1_ZM_v_0-ZM_v_1/ (ZM MBO), mbp-1/Z2_ZS_v_0/ (ZS MBP-1), mbp-1/Z3_ZL_v_0/ (ZL MBP-1),
  definition/Z4_ZM_FUT-ZS_FUT-ZL_FUT/ (definitions); 39 monthly files each (F, lines 1-35).
- Before reading any record, E.33 re-runs reports/stage_e32_briefs/work/lead/verify_discovery_hashes.py (sha256
  c329f443d83487c5239855459f1adebe124c63235711d281507f365e579713ab; E.32's run at 23:11 on 2026-10-26: 156 of 156
  match) and stops on any mismatch.
- E.31's per-day split store for ZM (/mnt/large-storage/market_data/PropExperiment/derived/e31/, F 4.3) may be reused
  after E.33 checks it against the raw files on 3 dates (equal record counts per date). ZS and ZL need a new split
  that keeps sizes, side, action, trade price and trade size (F 6.3 item 3).

### P1.2 Data allowlist and refusals (market data and measured outcomes; ProtocolReview FE-5, LE-7)
The list governs market data and measured outcomes; the program's code, docs, prompts, this protocol, E.32's reports
(reports/E.32_RETURN.md, reports/stage_e32_*.md) and the E.32 briefs are readable, except, for E.33's workers,
the section and the files named in the third bullet (FixSpotCheck S-A-6). Where the E.33 prompt's reading list and
this section differ, this section applies (FixVerifier
R-W4-6).
- Market data E.33 may read: (a) the 156 files; (b) the program calendars (data.calendars.grains,
  data.cme_calendar, data.hist_calendar); (c) the release calendar of P3.6; (d) E.31's code under
  reports/stage_e31_briefs/work/pilot/ as a library (mbo_book31, measure31, measure31_core, canary_check31,
  stats31_core, and kalgo31, with measure31_core's fill logic as the reference for E.33's P6.4 (iii) port only:
  F 6.1-6.2; FixVerifier FE-6).
- Refused (the data guard refuses these paths and dates in code, F 6.3 item 8, with a test for each):
  data/sealed/SOY_test_v1 and any ZM, ZS or ZL data dated 2017-05-01..2020-11-30 (seal manifest
  docs/soy_test/SOY_TEST_MANIFEST.json); anything dated on or after 2024-03-01; any file listed in
  reports/stage_e32_briefs/seal/derived_unsealed_files.tsv; any other root's market data; E.31's measured outputs
  (reports/stage_e31_briefs/work/pilot/runs/, which holds the measure31 output folder runs/measure31/ and every
  stats31.md and stats31.json; FixVerifier R-W1-8).
- Not opened by E.33's workers (coders and reviewers), because they reproduce E.31's discovery-date statistics:
  reports/E.31_RETURN.md section 3.5 (lines 175-213 are never read, by grep or otherwise; a grep hit inside them
  is discarded; the rest of the file is read by grep), the whole files reports/stage_e32_briefs/X1_exposure.md and
  reports/stage_e32_briefs/X1_verify.md, and every file under reports/stage_e32_briefs/work/X1_exposure/ (the
  Table C appendix and the X1_part* extraction files). The aggregate E.31 figures quoted in this protocol (P1.3,
  P1.5) and in the reader files M2, M3, M6, R3b and R4 are not closed: they are the figures the declared choices
  cite (FixSpotCheck S-A-1, S-A-7). The E.33 lead may read them: every choice is
  frozen and P8 is mechanical.

### P1.3 Sessions
- The day session is the search: label starts 08:35:00 to 13:12:00 - h; every label ends by 13:13:00 (P3).
- The overnight session carries no label, no trade and no selection in E.33. Its records enter features only
  (windows that reach back across 08:30, the overnight changes F1.7 and F4.7). Reasons: median overnight ZM volume
  about 2 contracts a minute against 71 in the day (M3, from A0) and 17% of volume (READER_BRIEF table), wider
  spreads, and an overnight search would add configurations to N without the power to pass (M5b c). A later stage
  may register one.

### P1.4 Trade dates
- Universe: the 816 regular grains trade dates 2020-12-01..2024-02-29 (program calendars; MathReview C confirmed).
- Burn-in: the first 20 of these dates. Features are computed on them to fill look-backs, but they carry no row, no
  trade and no daily value. OOF dates: the remaining T_disc = 796.
- Excluded from trading (daily value 0, no rows; features still computed for later look-backs): (i) a ZM roll date
  (the ZM front on D differs from the front on the previous trade date) and the trade date after it
  (measure31.roll_reasons); (ii) early-close and scheduled late-open dates (measure31.calendar_reason). E.33 counts
  them by the rule; E.31's counts (23 roll dates, 20 dates after a roll, 4 holiday or early close, 5 late opens;
  X1 Table C) are not copied.

### P1.5 Prior exposure of the discovery dates, and the firewall
What earlier stages computed on 2020-12..2024-02 (X1 Tables B and C, verified and corrected in
reports/stage_e32_briefs/X1_verify.md: 311 rows checked, 303 confirmed, 8 corrected, 0 unsourced):
- E.31 (passive markouts; V50 item 4): 1-lot passive fills at the ZM touch under three fill models, markouts at 1,
  10 and 60 s, by session, front versus second month, side and firm; splits by the ZS and ZL mid move over the
  prior 1 s and 10 s (model (c) fills after a ZS move against the order in the prior 1 s averaged -1.100 ticks,
  -0.652 after a move with it); by USDA window (0-5 minutes after a release: -8.98 ticks over 68 fills); by queue
  imbalance at entry; implied-liquidity shares (5.5% of aggressor prints found no displayed quantity at their
  price); feasible round trips. No split by calendar month, hour, weekday, volatility state or expiry (X1 C1).
- Bar-level trials (1-minute bars) that read ZS, ZM or ZL on these dates: E.22's confirmation of K6 members on
  W_cf 2019-05-06..2024-02-29 (CP1 late-session momentum, CP2 breakout, CP3 prior-close location at 08:30, the
  overnight crush gap, WASDE pre-drift; all null); E.12 Gate 0 (ML route v2, 273 tests, FAIL); E.17 H1/H4/H5
  (settlement-window momentum and reversal, pooled, FAIL); E.20's 45-configuration ML search with late-session
  features (ridge and LightGBM depth 2, h60/h120/hF, FAIL); E.21 T1/T2 multi-day trend (FAIL) (X1 B1-B6).
What could steer E.33: E.31's seconds-scale ZS/ZL move splits (toward cross-asset lead features), its queue-
imbalance split (toward book-imbalance features), its USDA split (toward release windows); the bar trials' nulls
(away from late-session, open-location and crush-gap rules).
The firewall:
1. Every feature in P4 comes from the literature as read by the M1-M4 readers and is declared here before E.33
   reads any outcome. No E.31 statistic sets a sign, threshold, look-back or weight. The shortest look-back is 1
   minute; E.31's splits are at 1 s and 10 s.
2. Queue imbalance (F3.7, F3.8) is in because the order-flow literature names it (M1 a, d: Cont, Kukanov and
   Stoikov; Stoikov's microprice), defined the standard way on seasoned depth (P4; R2's spoofing guard). It would
   be in had E.31 never run.
3. The release exclusion (P3.6) is set from R4 and M3 evidence (Huang; Joseph and Garcia; Anderson, McKenzie and
   Noyes 2024 via R2: soybeans still reacting 30 minutes after WASDE), wider than E.31's 0-5 minute split.
4. Discovery results select; they do not confirm. Inference rests on the one-shot test on the sealed window, which
   E.31 never read (V50 item 4, V51). The bar trials' reads of 2019-05..2020-11 are bar-level and named in the seal
   document (reports/stage_e32_test_seal.md section 4).
5. E.33's workers do not open E.31's outputs (P1.2), and the selection rule (P8) is mechanical: no person or model
   chooses among configurations after seeing outcomes.

## P2. Idea families

Four idea families (F1-F4) and one context block (C). Each family's features enter its own feature set with C; the
pooled set holds all four (the ML route, V51 item 1). Feature sets searched: S1 = C+F1, S2 = C+F2, S3 = C+F3,
S4 = C+F4, S5 = C+F1+F2+F3+F4.

### F1 Crush-residual reversion (the board crush, ZM leg)
- Mechanism: the board crush C = 11 ZL + 2.2 ZM - ZS (cents/bu; M2 bottom line, R3a 1; MathReview A confirmed) is
  cointegrated within the day session. When ZS or ZL moves, the crush dislocates, and part of the dislocation closes
  through ZM within minutes, faster when ZM's share of volume is high.
- Evidence and reasoning: Zhou, Bagnarosa, Gohin, Pennings and Debie (J. Commodity Markets 2023): 180 of 243 day
  sessions cointegrated at 1-minute sampling (229 at 2-minute), 52 overnight; leadership depends on relative volume
  (R3a 3). Against: the prior is that ZM is not the default adjusting leg (Adrangi, daily; Rechner and Poitras,
  meal leg -0.019; R3a 6); no intraday half-life is published (R3a 5); ZM must close about 70% of a 1-cent
  dislocation to clear 1.59 ticks within one half-life (M2 bottom line 1; MathReview A confirmed 0.70, 0.47, 0.40);
  the oil share differs between windows (renewable diesel: discovery inside the high-oil-share regime, the test
  before it; R3a 2, 9), so levels are normalised by causal rolling statistics, never fixed cents.
- Overlap: K6-crushgap-01 (overnight change in the crush gap, ZS traded 08:31-13:14; E.8 t -2.708; E.22 null on
  2019-05..2024-02; X1 B1) is a once-a-day bar rule; F1.7-F1.8 revisit its signal as a decaying minutes-scale
  feature on ZM. E.31's ZS/ZL 1 s and 10 s splits concern seconds and passive fills, not crush levels.

### F2 Cross-asset propagation (ZS and ZL lead ZM at minutes)
- Mechanism: information enters the more liquid ZS (median v_0 ADV 77,862 against ZM's 36,690; READER_BRIEF) and ZL
  first; ZM catches up over minutes through arbitrage and hedging flow.
- Evidence and reasoning: seconds-scale lead-lag cannot pay 1.59 ticks at 300-1,000 ms latency (M2 b: a 3-sigma ZS
  impulse is needed to break even), so F2 uses minute look-backs only. The only positive forward order-flow finding
  in M1's sources is cross-asset and lagged (M1 table 10). De Boer et al. put spillovers within 30 s (R3b e,
  abstract only), which argues the effect may be too fast: F2 tests whether a minutes residue exists.
- Overlap: no registered trial used minutes-scale ZS/ZL-to-ZM lead features (X1 B). E.31's 1 s and 10 s ZS/ZL move
  splits are the nearest exposure (P1.5).

### F3 ZM order flow and book state (MBO)
- Mechanism: persistent buying or selling pressure (order-flow imbalance, aggressor imbalance, touch cancellations,
  sweeps, refills of a hidden order) moves the mid over the next minutes, before the pressure is absorbed.
- Evidence and reasoning: forward predictability of OFI is real but decays within about 30 minutes, and its
  out-of-sample R2 is small or negative at 1 minute (M1 a: Cont, Cucuringu and Zhang Table 8; Chordia, Roll and
  Subrahmanyam: "In no more than thirty minutes, order imbalances lose their predictive ability"). For grains,
  lagged order imbalance predicts returns for some contracts (Volkenand, Filler and Odening 2018, abstract) and OFI
  predicts Dalian soybean meal over short horizons (Jin et al. 2023, abstract) (M1 table 11). M1's verdicts:
  features and conditioners in one frozen model, not standalone rules; drift-burst aftermath is the one event
  mechanism with a grain measurement (ZC b = -0.20). Iceberg impact is transient (M1 7). R2: a CFTC soybean-complex
  spoofing case, hence seasoned depth.
- Overlap: no registered trial used order-book features on ZM (the 538 are bar-level; X1 B). E.31's queue-imbalance
  split of passive markouts is the nearest exposure (P1.5).

### F4 ZM own price path: intraday momentum and reversal, burst aftermath, session handoff
- Mechanism: short-horizon continuation or reversal of ZM's own moves; reversal after non-news bursts (liquidity
  shocks); absorption of the overnight move after the 08:30 open; position-in-range and late-session effects.
- Evidence and reasoning: CBOT soybean meal shows no first-half-hour momentum over 1982-2020 (Baltussen et al.,
  slope -0.95, t -1.58, OOS R2 negative; R4 5.3), and its overnight-plus-first-half-hour slope is negative and
  insignificant; Dalian meal shows overnight continuation (t 2.60 and 2.96, a different market; R4 4.2); drift-burst
  reversal in ZC at 5 minutes (M1 9). Prior: weak. F4 is kept because the published nulls are at daily slots rather
  than minutes and the pooled set needs ZM's own state.
- Overlap: K6-cp1-01 (late-session momentum port, 12:44 decision, about 29 minutes), K6-cp2-01 (breakout),
  K6-cp3-01 (prior-close location at 08:30), E16-H1/H4 (settlement-window momentum and reversal), E.20's
  late-session ML features: all bar-level, all null or FAIL (X1 B1, B3, B4). F4.7-F4.8 and F4.13 share those
  mechanisms at minutes scale; the overlap is disclosed and the configurations count in N like any other.

### C Context block (liquidity and calendar state; in every set, never searched alone)
Time of day, spread, depth, volume rate, volatility level, days to expiry, release-day and post-release flags,
Monday, growing season, validity flags (P4). Liquidity-state regimes have no directional mechanism of their own
(M1: Kyle's lambda and VPIN as conditioners); they enter as conditioners the models may interact with.

### Candidates dropped (with reasons)
- Post-USDA drift or reversal as a family: about 49 major 11:00 USDA days and 39 NOPA days in 39 months; with a
  per-event 60-minute noise of 24.4 ticks the minimum detectable mean effect is about 10 ticks for 24 big events
  (R4 2.4), 10.7-33 ticks in M5b c; an event family that trades on a few dates a month cannot reach the daily
  Sharpe of the test bar (P7). Kept as exclusions (P3.6) and flags (C.8, C.9).
- The overnight-to-day handoff as a once-a-day family: one decision a day needs 3.46 ticks net per trade at a
  30-minute hold to reach the selection threshold (P7.2), against null bar trials on the same mechanism
  (K6-crushgap-01, K6-cp3-01). Kept as features F1.7, F1.8, F4.7, F4.8.
- Seconds-scale lead-lag (M2 b); deep LOB models (M4 c: 2-34 weights per independent label); VPIN as a signal (M1
  8); index-roll front-running (R3b c: BCOM weight about 3.5%; R2: about 2 bp on outrights); COT timing (R2: no
  weekly forecasting power for meal); NOPA-day and biofuel-day event rules (R3a 8.2: about 39 events against about
  942 needed); late-session momentum as a family (R4 5.4).

## P3. Labels, horizons and sampling

### P3.1 Horizons and label types (6)
Fixed-horizon executable labels FH05, FH15, FH30, FH60 (h = 5, 15, 30, 60 minutes) and triple-barrier executable
labels TB15, TB30 (vertical barrier at h = 15, 30 minutes). 1-minute, 120-minute-plus and to-close horizons are not
searched: a 1-minute label needs a hit rate of 0.816 (M3 f.3), and one trade a date needs 3.46 ticks net at a
30-minute hold and 4.90 at 60 minutes to reach the selection threshold (P7.2).

### P3.2 Executable prices
- A market buy decided at time u fills at ask_1 of the ZM book as of u + L; a market sell at bid_1 as of u + L. One
  contract; no depth walk (the touch always shows at least one lot when the level exists; M6 E1).
- Fallback (trade simulation only; ProtocolReview LE-1): if the needed side is empty, or the book is marked bad, at
  u + L, the order fills at the first later book update at which that side exists and the book is not marked bad;
  an entry with no such update before its planned exit time is not made (counted); an exit with none before
  13:20:00 is marked at the front's limit price on the side that blocked it (the low limit for a long's exit, the
  high limit for a short's exit, per P3.6 rule 5's definitions) and flagged; if D has no limit prices (rule 5's skip
  case), the exit is marked at the last valid touch on that side before it emptied or the book was marked bad, and
  flagged (FixSpotCheck S-A-8) (FixVerifier
  R-W1-7). For a TB trade, m0 of P3.4 is M_ZM as of the entry fill update (equal to M_ZM(t + L) when no fallback
  fired); if M_ZM is undefined at that update, the entry is not made and is counted with the entries not made
  (FixVerifier R-W1-2). E.33 reports the counts of fallback fills, entries not made and limit marks per
  configuration.

### P3.3 Fixed-horizon label
For decision time t and horizon h:
    N_long(t)  = bid_1(t + h + L) - ask_1(t + L) - f
    N_short(t) = bid_1(t + L) - ask_1(t + h + L) - f        (ticks; f = 0.528)
    y(t) = +1 if N_long(t) > 0;  -1 if N_short(t) > 0;  0 otherwise.
Both cannot be positive: N_long + N_short = -s(t + L) - s(t + h + L) - 2f < 0 (M3 f.2). The dead zone is the spread
plus costs, not a tuned threshold.

### P3.4 Triple-barrier label
For decision time t and vertical horizon h in {15, 30}: m0 = M_ZM(t + L); half-width b(t) = kappa x sigma_ZM(D) x
sqrt(h) ticks with kappa = 1.0 (one value; M3 b.7); tau_up = the first ZM book update u in (t + L, t + L + h min]
with M_ZM(u) >= m0 + b(t); tau_dn = the first with M_ZM(u) <= m0 - b(t); tau = min(tau_up, tau_dn, t + L + h min).
    N_long^TB(t)  = bid_1(tau + L) - ask_1(t + L) - f
    N_short^TB(t) = bid_1(t + L) - ask_1(tau + L) - f
    y^TB(t) = +1 if tau = tau_up; -1 if tau = tau_dn; 0 if neither barrier is reached by t + L + h min.
For b(t) > 0 one update cannot reach both barriers; E.33 asserts it. The barrier test steps through book updates
(0.3) and ignores updates at which M_ZM is undefined (an empty side or a bad book never triggers a barrier;
ProtocolReview LE-6). Barrier exits are market orders triggered by
the simulated mid; no resting stop or take-profit exists (this keeps clear of Topstep's ban on "Placing orders at
prices outside the current best bid or offer", M6 5.3; disconnect protection is a matter for a later live stage).

### P3.5 Trade rule (identical for every configuration)
A fitted model returns calibrated class probabilities p_k(x), k in {-1, 0, +1}. From the fold's training rows, with
the weights of P3.7, mu_long_k = the weighted mean of N_long over training rows with y = k, and mu_short_k likewise
(N^TB for TB labels). Then
    EV_long(x) = sum_k p_k(x) mu_long_k,     EV_short(x) = sum_k p_k(x) mu_short_k.
At a decision time t at which the simulated account is flat and the entry rules of P3.6 hold at t (P3.6, first
paragraph; FixVerifier R-W1-6):
enter long if EV_long > max(EV_short, 0); short if EV_short > max(EV_long, 0); otherwise no trade (an exact tie
means no trade). Assumption, stated: within a class the net return does not depend on x (the class-conditional
means carry the magnitudes); the realised P&L of P6 measures how far this holds.

### P3.6 Exclusion rules
A label span is [t, t + L + h min] (FH) or [t, tau + L] (TB). Rules 1-4, 6 and the limit-proximity part of rule 5
are known at t (clock, calendar and the book at t) and govern both rows and entries: a trade may be entered at t
only if the possible span [t, t + L + h min] meets them and the ZM book at t has both sides and is not marked bad.
The locked-book part of rule 5 looks into the span, so it is a row rule only (a label needs defined exit prices);
the trade simulation never conditions an entry on it and uses the P3.2 fallback instead (ProtocolReview LE-1). A
row is kept only if its whole possible span lies inside D's day session on one ZM front and meets every rule:
1. Open: no span starts before 08:35:00 (M3 g.3 rule 1).
2. Close: every span ends by 13:13:00, one minute before the 13:14-13:15 settlement window (M3 g.3 rule 2).
3. Releases: no span intersects [R - 2 min, R + 30 min] for any release R at 11:00 CT (12:00 ET) of USDA WASDE, NASS
   Crop Production (monthly and annual), NASS Grain Stocks, NASS Prospective Plantings, NASS Acreage or NOPA Monthly
   Crush. Calendar: reports/stage_e31_briefs/research/usda_releases.csv (sha256 0743c0e27ac963d2d47a691a8b644f10
   208cb64b8f629a09ac788d829ad45119) and usda_releases_ext.csv (sha256 55df3b14f4565f607294e313c0b8fc26f3652df1d4de
   02a732861b47ba9feb88), E.31's sourced calendar, read as reference data: usda_releases_ext.csv covers 2020-12..
   2022-10 and usda_releases.csv covers 2022-11..2024-02. Parse rule (ProtocolReview LE-3, DO-8): skip lines that
   start with "#"; columns date, time_et, report, source_url, evidence; skip rows whose date is not a valid
   YYYY-MM-DD (the "-NORELEASE" rows and the two NOPA placeholders "2022-11-MISSING" and "2022-12-MISSING"); keep
   rows with time_et "12:00" and report exactly one of "USDA WASDE", "NASS Crop Production", "NASS Crop Production
   Annual", "NASS Grain Stocks", "NASS Prospective Plantings", "NASS Acreage", "NOPA Monthly Crush (not USDA)",
   whatever the evidence grade; R = 11:00:00 CT on that date. A calendar month with no valid NOPA row (exactly
   2022-11 and 2022-12 in these files) gets its rule date: the 15th, or the next trade date if the 15th is not one,
   at 11:00 CT. E.33 asserts, before any label, 39 USDA WASDE, 39 NASS Crop Production, 4 NASS Crop Production
   Annual, 13 NASS Grain Stocks, 3 NASS Prospective Plantings, 3 NASS Acreage and 37 NOPA counting rows plus 2 NOPA
   rule dates, prints them, and stops on any other count (FixVerifier LE-3, R-W1-5). Export Sales (07:30 CT), Crop
   Progress (15:00 CT) and Fats & Oils (14:00 CT) fall outside the day session and need no window.
4. Rolls and calendar: P1.4 exclusions (no row and no trade on those dates).
5. Locked or halted book, and price limits: (row rule) no span with a book update at which the ZM book lacks a bid
   or an ask or is marked bad (ProtocolReview LE-6); (row and entry rule) no span that starts while M_ZM(t) >= HL -
   0.02 c or M_ZM(t) <= LL + 0.02 c, where HL and LL are the high and low limit prices of the front's last
   definition record with ts_recv <= 08:30:00 CT on D (a single as-of pass over the Z4 files in ts_recv order,
   state carried across files and dates; ProtocolReview LE-2, FE-8; FixSpotCheck S-A-9) and c = (HL + LL)/2
   (Topstep and MFFU forbid trading within 2% of a price limit; M6 4.1). If no such
   record exists, or either limit field of it is UNDEF_PRICE (mbo_book31.UNDEF_PRICE, 2^63 - 1) or 0, the
   limit-proximity part is skipped for D and the date is counted (FixVerifier R-W4-8, R-W1-11).
6. ZS or ZL invalid: rows are kept; the features that need them fall back per P4 G3.
E.33 reports how many rows and minutes each rule removes.

### P3.7 Rows and sample weights
- Rows: every t in G_h(D) on every OOF date that meets P3.6 and has a valid M_ZM(t). Overlapping labels are kept.
- Weights: average uniqueness at 1-minute resolution (Lopez de Prado, AFML ch. 4; M3 d): for the one-minute
  interval m, c_m = the number of rows of the same label type and date whose span intersects m by more than one
  second (so an FH span of h minutes plus L covers h intervals; ProtocolReview DO-15; for TB the realised span
  [t, tau + L]); u_i = the mean of 1/c_m over the intervals m that span_i intersects by more than one second (the
  same intervals that count span_i in c_m; FixVerifier DO-15). Weights are computed per date over
  all rows of that date (labels never cross dates, so no weight depends on another fold). The raw u_i are the sample
  weights (they sum to about the number of independent labels; no renormalisation).

### P3.8 Realised trade simulation (OOF evaluation and the test)
- One position at a time and at most 20 entries per trade date (the program's entry cap, screening/
  stage_e_runner.py 31-39). That runner's 2-minute minimum hold and 10-minute mean-holding floor are bar-runner
  rules and are not adopted: the firms' hold-time rules are 5-10 s (M6 5.3; ProtocolReview DO-10).
- When flat at t in G_h(D), the entry rules of P3.6 hold at t, and fewer than 20 entries have been made on D, apply
  P3.5. The decision uses only records with ts_recv <= t. A trade entered at t exits per its label type (FH at
  t + h, TB at tau) with the executable prices of P3.3-P3.4 (with the P3.2 fallback) and the variant's fee. After the
  exit fill the account is flat; the next decision is the first grid minute at or after the exit fill time.
- Daily value X_D = the sum of the net P&L of the trades entered on D (ticks per contract per day, the program's
  unit); X_D = 0 on OOF dates with no trade, including excluded dates. Burn-in dates are not in the series.

## P4. Features (exact definitions)

### General rules
- G1 Point in time: a feature at t uses only records with ts_recv <= t.
- G2 Look-backs follow 0.3. Scale references (sigma_X, trailing means and medians of |OFI|, depth, sweeps, refills,
  volume, lambda) chain across rolls. Level quantities of F1 (the crush and its residual) use only data inside the
  current segment: a segment is a maximal run of trade dates on which the three fronts (ZM, ZS, ZL) are unchanged; a
  look-back that would cross a segment boundary makes the feature invalid. ZS has no October or December contract,
  so in autumn the crush mixes contract months (M2 bottom line 4); the rolling statistics of F1 absorb the month
  spread, and segments break at any front change.
- G3 Invalid values: a feature that cannot be computed (insufficient history, empty book side, zero denominator,
  invalid segment) takes the value 0, and its family flag (C.11-C.14) is 0 for that row if any feature of the family
  is invalid.
- G4 Clipping (ProtocolReview DO-11): clipped to [-5, 5] after their own normalisation (38): C.5, F1.1-F1.4,
  F1.6-F1.8, F2.1-F2.11, F3.1-F3.4, F3.10-F3.12, F4.1-F4.5, F4.7-F4.13. Not clipped (21): C.1-C.4, C.6-C.15, F1.5,
  F3.5-F3.9, F4.6 (bounded by construction or a log of a positive scale).
- G5 Model standardisation: for LOGIT, features are centred and scaled by the training fold's weighted mean and SD,
  and the evaluation fold uses the training fold's values; a training SD of 0 makes the feature 0 in that fold.
  LGBM uses the clipped features unscaled.
- G6 Clocks: ZS and ZL are read as of t on the same ts_recv clock as ZM (same GLBX capture); E.33 reports the median
  ts_recv - ts_event of each feed as a data check. No feature uses that difference. A placebo on one stream cannot
  reveal an offset between the ZM MBO feed and the ZS/ZL MBP-1 feeds (MathReview A-2), so E.33 also reports, per
  month, the distribution of ts_recv - ts_event for ZM, ZS and ZL side by side; a difference in medians above 100 ms
  in any month is reported as a data finding (the features' 1-minute grid makes sub-second offsets immaterial, and no
  rule changes because of it). All prices in features and labels are mids or executable touch prices, never
  last-trade prices (no bid-ask bounce; MathReview A-3).
- G7 Agreement tolerance for E.33's two implementations (its B3): features equal within 1e-9 relative (1e-12
  absolute near 0); labels and classes exactly equal (prices are integer ticks).

### C Context (15 features)
| ID | Definition |
|---|---|
| C.1 | tod = (t - 08:35)/(13:13 - 08:35) in minutes, in [0, 1] |
| C.2 | tod^2 |
| C.3 | min(s_ZM(t), 5) in ticks |
| C.4 | log(1 + qb_1 + qa_1) of ZM at t (displayed touch depth, contracts) |
| C.5 | log((V_ZM(15) + 1)/(Vbar + 1)); V_ZM(15) = ZM contracts traded in the 15-minute window ending at t; Vbar = the mean of V_ZM(15) at the same minute of day over the 20 trade dates before D |
| C.6 | log(sigma_ZM(D)) |
| C.7 | min(trade dates from D to the expiration of the ZM front, from its last definition record with ts_recv <= 08:30:00 CT on D, 60)/60 |
| C.8 | 1 if D carries an 11:00 release of P3.6 rule 3, else 0 |
| C.9 | C.8 x 1{t >= 11:30} |
| C.10 | 1 if D is a Monday or the first trade date after a full closure, else 0 |
| C.11-C.14 | validity flags v1-v4 of F1-F4 (G3) |
| C.15 | 1 if D falls in June, July or August, else 0 |

### F1 Crush (8 features)
Crush in cents per bushel: C(u) = 11 M_ZL(u) + 2.2 M_ZM(u) - M_ZS(u), with M_ZL in cents/lb, M_ZM in USD/short ton,
M_ZS in cents/bu (11 lb of oil and 44 lb of meal per 60 lb bushel; 2.2 = 44/2000 x 100). One ZM tick is 0.22 cents
of crush (MathReview A confirmed). Sample points per 0.3.
| ID | Definition |
|---|---|
| F1.1 | zC30 = (C(t) - mean_30)/sd_30, mean_30 and sd_30 over C(t - j min), j = 1..30, inside the segment |
| F1.2 | zC120: the same with j = 1..120 |
| F1.3 | zR = e(t)/sd_e. Before D's open: OLS on the 1-minute samples (08:35-13:13, minutes clear of P3.6 rule 3) of the 10 trade dates before D inside the current segment, M_ZM = a + b_S M_ZS + b_L M_ZL + eps in natural units (a is the natural-scale intercept recovered from the means, a = mean M_ZM - b_S mean M_ZS - b_L mean M_ZL, after the centred fit of 0.3; FixVerifier R-W3-13); at least 3 such dates or invalid. e(t) = (M_ZM(t) - a - b_S M_ZS(t) - b_L M_ZL(t))/0.10 in ZM ticks; sd_e = the fit's residual SD in ZM ticks. Coefficients fixed for D |
| F1.4 | dzC5 = zC30(t) - zC30(t - 5 min) |
| F1.5 | vrel15 = V_ZM(15)/(V_ZM(15) + V_ZS(15) + V_ZL(15)), contracts traded in the 15-minute window ending at t (ZM trades from MBO, ZS and ZL trades from MBP-1 trade records) |
| F1.6 | zC30 x vrel15 |
| F1.7 | gC(D) = (C(08:35:00 on D) - C(13:15:00 on the previous trade date))/sd_g, sd_g = the SD of the same quantity over the 20 trade dates before D inside the segment (at least 10, or invalid); constant within D |
| F1.8 | gC(D) x exp(-(t - 08:35)/30 min) |

### F2 Cross-asset propagation (11 features)
| ID | Definition |
|---|---|
| F2.1-F2.3 | rS_k = (M_ZS(t) - M_ZS(t - k min))/(sigma_ZS(D) sqrt(k)), k = 1, 5, 15 (ZS ticks) |
| F2.4-F2.6 | rL_k: the same for ZL, k = 1, 5, 15 |
| F2.7 | d5 = [ (dZS_5 - 11 dZL_5)/2.2 - dZM_5 ]/0.10/(sigma_ZM(D) sqrt(5)), dX_5 = M_X(t) - M_X(t - 5 min) in natural units (cents/bu, cents/lb, USD/short ton): the 5-minute move of the implied meal value minus ZM's, in ZM ticks, scaled (it equals -dC_5/2.2 in USD/ton before scaling) |
| F2.8-F2.9 | OFI_S_k/Obar_S_k, k = 1, 5: ZS best-level OFI (Cont, Kukanov and Stoikov 2014) summed over the MBP-1 updates in the window, e_n = 1{Pb_n >= Pb_{n-1}} qb_n - 1{Pb_n <= Pb_{n-1}} qb_{n-1} - 1{Pa_n <= Pa_{n-1}} qa_n + 1{Pa_n >= Pa_{n-1}} qa_{n-1}; Obar_S_k = the trailing 20-date reference mean of |OFI_S_k| |
| F2.10-F2.11 | the same for ZL, k = 1, 5 |

### F3 ZM order flow and book state (12 features)
Seasoned depth at t: the displayed quantity at a price level counting only orders whose last add or modify (by
ts_recv) is at least 1.000 s before t.
| ID | Definition |
|---|---|
| F3.1-F3.3 | OFI_ZM_k/Obar_ZM_k, k = 1, 5, 15: as F2.8 on the ZM top of book from MBO |
| F3.4 | IOFI5 = sum_{m=1..5} OFI^(m)_5 / sum_{m=1..5} Dbar_m: OFI^(m) is the level-m OFI (Xu, Gould and Howison 2018: the e_n of F2.8 on level-m prices and quantities) over the 5-minute window; Dbar_m = the trailing 20-date reference mean of (qb_m + qa_m)/2. Equal weights (no estimated PCA weights) |
| F3.5-F3.6 | TI_k = (B_k - S_k)/(B_k + S_k), k = 5, 15: aggressor-buy and aggressor-sell contracts from ZM MBO trade records (Databento's aggressor side A/B; side N excluded); invalid if B_k + S_k = 0 |
| F3.7 | QI1 = (qb_1 - qa_1)/(qb_1 + qa_1) on seasoned depth at t; invalid if the denominator is 0 |
| F3.8 | QI3 = (sum_{m<=3} qb_m - sum_{m<=3} qa_m)/(sum_{m<=3} qb_m + sum_{m<=3} qa_m) on seasoned depth at t |
| F3.9 | CR5 = (Ca_5 - Cb_5)/(Ca_5 + Cb_5): contracts removed from the price level that was the best ask (Ca) or best bid (Cb) just before the record, by cancels, size-reducing modifies (the reduction) and modifies to another price (the full size), in the 5-minute window; fills are not removals (ProtocolReview DO-16); invalid if the denominator is 0 |
| F3.10 | SW5 = (sweeps_buy_5 - sweeps_sell_5)/sbar_5: a buy sweep is a set of trade records sharing one ts_event that leaves the best ask level's displayed quantity at 0 (sell sweep: the best bid); sbar_5 = the trailing 20-date reference mean of sweeps_buy_5 + sweeps_sell_5; invalid if sbar_5 = 0 |
| F3.11 | RF15 = (refill_bid_15 - refill_ask_15)/rbar_15: a refill is an add at the same price and side within 100 ms (ts_recv) after that price level, while it was the touch, reached 0 displayed quantity through trades; rbar_15 = the trailing 20-date reference mean of |refill_bid_15 - refill_ask_15|; invalid if rbar_15 = 0 |
| F3.12 | lam60 = the OLS slope (with an intercept; 0.3) of dM_ZM (ticks) on signed volume (B - S, contracts) over those of the 60 one-minute intervals ending at t that contain trades, divided by the trailing 20-date reference median of the same slope; invalid with fewer than 30 such intervals (ProtocolReview DO-13) |

### F4 ZM own price path (13 features)
| ID | Definition |
|---|---|
| F4.1-F4.5 | rZ_k = (M_ZM(t) - M_ZM(t - k min))/(sigma_ZM(D) sqrt(k)), k = 1, 5, 15, 30, 60 |
| F4.6 | RP = (M_ZM(t) - Lo)/(Hi - Lo), Hi and Lo the max and min of M_ZM over [08:30, t] on D; 0.5 if Hi = Lo |
| F4.7 | GAP(D) = (M_ZM(08:35:00 on D) - M_ZM(13:15:00 on the previous trade date))/sd_gap, sd_gap = the SD of the same quantity over the 20 trade dates before D on which the ZM front was the same at both times (at least 10, or invalid); constant within D |
| F4.8 | GAP(D) x exp(-(t - 08:35)/30 min) |
| F4.9 | rOpen = (M_ZM(t) - M_ZM(08:35:00))/(sigma_ZM(D) sqrt(max(1, minutes from 08:35 to t))); 0 at 08:35 |
| F4.10 | RV15 = SD of the 15 one-minute mid changes ending at t / sigma_ZM(D) |
| F4.11 | DB = B* if |B*| >= 3, else 0: B(e) = (M_ZM(e) - M_ZM(e - 2 min))/(sigma_ZM(D) sqrt 2) for window ends e = t, t - 1 min, ..., t - 13 min, and B* the B(e) with the largest |B(e)| (latest e on ties). Fixed-length windows defined by their end: no local-extremum timing (M1 9's look-ahead trap) |
| F4.12 | DB x exp(-(t - e*)/5 min), e* the window end chosen in F4.11 |
| F4.13 | LATE = rOpen x 1{t >= 12:15} |

Feature counts: C 15, F1 8, F2 11, F3 12, F4 13; S1 23, S2 26, S3 27, S4 28, S5 59.

### P4.1 Leakage and pipeline tests (before any model is fitted on real outcomes; LT7 is repeated after the test list is hashed)
- LT1 Truncation (E.33 B4 i): for 200 decision times drawn with seed 20261027 across the OOF dates, recompute every
  feature from ALL input streams (ZM MBO, ZS and ZL MBP-1, and the definitions) truncated at ts_recv <= t; every
  feature equals the production value within G7's tolerance. Any mismatch stops E.33 until fixed.
- LT2 Span (E.33 B4 ii): for every row the span lies in [08:35, 13:13] on D, on one ZM front, clear of P3.6; no
  feature window reaches past t. Violations must be 0.
- LT3 Fold hygiene (E.33 B4 iii): unit tests that no training row's date lies in the evaluation fold or its embargo,
  that the scaler, the calibrator and the mu_k use training rows only, that early stopping uses the inner block
  only, that LightGBM's feature bins come from the inner-training rows only (the inner-validation set is built with
  reference= the inner-training Dataset; ProtocolReview DO-17, FixVerifier R-W3-12), and that each row's weight
  depends only on rows of its own
  date; the embargo (21 dates) exceeds every label's span and every feature look-back.
- LT4 Clock: unit test that label starts, label ends and feature cut-offs are built from ts_recv only, with records
  that have ts_recv < ts_event (0.14-0.16%, F 1.4) kept in ts_recv order.
- LT5 Leak canary (E.33 B4 iv): a deliberately leaked feature (the label shifted by one step) must be caught by
  LT1-LT2 and must give an absurd CV score; then it is removed. Run on synthetic data or as a pure unit test.
- LT6 Data guard: tests that the guard refuses every path and date class of P1.2's Refused list (FixVerifier
  R-W1-8).
- LT7 Simulator causality (ProtocolReview LE-5; FixVerifier LE-5, R-W1-3, R-W3-6, R-W3-14): before the first
  real-outcome fit, the fold models of the P4.2 null search of seed 1 (its 20 configurations, S5 x {FH15, TB30} x
  the 10 grid points; trained on synthetic rows, so no real outcome enters) are applied to the real streams at the 200
  times of LT1 restricted to each configuration's grid G_h(D): the entry decision (side or no trade) recomputed
  from all streams truncated at t equals the production decision, and the entry fill recomputed from streams
  truncated at the production fill time (t + L, or the fallback fill update of P3.2) equals the production fill.
  At each time t the fold model is the one whose OOF block holds t's date, as in production. LT7 is repeated on
  the Tier A and Tier B fold models after the test list is hashed. A mismatch at the first run stops E.33 until the
  code is fixed under 0.2 (the pipeline hash re-taken before the first real-outcome fit). A mismatch at the second
  run is a bug found after the pipeline freeze: E.33 stops the test list, reports the mismatch, and follows its
  prompt's B7 rule, a logged pipeline amendment (the fix is logged in the STATE file with the protocol line it
  restores, as in 0.2's first bullet; it is not a protocol amendment under 0.2). The fixed pipeline is hashed; the
  P3.8 simulation, and any fit the fix touches, is re-run for all 300 configurations; the affected set is every
  configuration whose OOF daily series differs from its registered series at G7's tolerance. The affected
  configurations are registered in one register call under test "E33A" as E33A-<set><label><grid>, with a new
  freeze file of the P7.1 form listing those IDs and the amended pipeline sha256, so N rises by their number
  (P7.1); p7_final.py recomputes the thresholds at that N; P8 is re-run on the 300 series with each affected
  configuration's registered series replaced by its E33A series (the superseded series is reported, never
  selectable); the test list is re-hashed and P6.4 and P6.5 are re-run on it (FixSpotCheck S-B-1, lead's choice;
  FinalDiffCheck F-2).

### P4.2 Synthetic proofs (E.33 B5; synthetic data only; declared scale, ProtocolReview FE-2, FE-7, DO-21)
Forty full 300-configuration searches would be 72,000 fits, about 40 times the search, and cannot fit E.33's day.
The proofs therefore run at this declared scale:
- Feature and label code: a record-level synthetic MBO and MBP-1 stream for 30 trade dates (tick sizes, spreads,
  volatility and event rates of the data facts) through the production feature and label builders, with known
  answers checked by hand-built cases (E.33 B3-B4).
- Search proofs: the subset S5 x {FH15, TB30} x the 10 grid points (20 configurations, 120 fits a search), run from
  synthetic minute rows on the real decision grid G_h(D), the 796 OOF dates and the P3.6 exclusion calendar (the 20
  burn-in dates as history; mids, touch prices, labels and the 59 S5 feature columns generated to match the data
  facts' rates) through the P6.1 folds and embargo, models, the EV rule, the simulation, G1-G5 with the production
  thresholds and the Tier A walk (FixVerifier FE-2, R-W3-3). The thresholds are those at the expected N 838; if the
  registered N differs, the proofs are not rerun and E.33's return says at which N they ran (FixVerifier R-W3-15).
  Seeds 1-20 for null searches and 101-120 for planted searches, each run exactly once per pipeline hash (4,800
  fits); after a logged code fix (0.2) all 40 are rerun with the same seeds, every run before and after the fix is
  reported, and no seed is added, replaced or rerun on its own (FixVerifier R-W3-5).
- Null: no feature carries signal. Stated false-positive rate of P8: P(Tier A non-empty | no signal) <= 0.05 per
  search. The proof fails if Tier A is non-empty in 2 or more of the 20 null searches (P(at least 2 of 20) = 0.26 at
  a true rate of 0.05). For the full 300-configuration search the analytic rate is far below 0.05: under independent
  configurations and normal days, 300 x P(Z > 5.66) is about 2e-6 at the binding threshold (and 300 x P(Z > 4.86),
  about 2e-4, at G3 alone). E.33 also reports the SD of the 400 null daily Sharpes (20 configurations x 20 seeds,
  each centred on its configuration's mean) against 1/sqrt(796) = 0.0354 (FixVerifier R-W3-9).
- Planted: one F3 feature carries a signal whose size is set so that the oracle strategy (the P3.5 rule applied
  with the generator's true class probabilities, with the P3.8 costs and the dead zone) has a daily Sharpe of 0.35
  net under the selection variant at FH15 on the synthetic series; the same plant serves the TB30 configurations
  (FixVerifier FE-7, R-W3-4). E.33 reports the realised OOF Sharpe of the best planted configuration per seed
  beside the oracle. The proof passes if at least one S5 configuration at FH15 or TB30 enters Tier A in at least 14
  of the 20 planted seeds (P(at least 14 of 20) = 0.91 at a per-seed power of 0.8; P7.2's joint select-and-pass
  probability is 0.91 at a realised daily Sharpe of 0.25, and selection alone 0.914 (the P7.2 table); FixVerifier
  R-W3-10, FixSpotCheck S-B-4).

## P5. Models (two families) and compute

### LOGIT: regularised multinomial logistic regression (primary; M4 a)
- Objective: minimise C x sum_i w_i l_i(beta) + (1 - rho)/2 ||beta||_2^2 + rho ||beta||_1 over the standardised
  features (intercepts unpenalised); l_i is the multinomial log-loss of y_i in {-1, 0, +1}; w_i the P3.7 weights.
- Grid: C in {0.01, 0.1, 1.0} x rho in {0 (L2), 0.5 (elastic net)}: 6 points.
- Implementation: scikit-learn LogisticRegression (version pinned in uv.lock; 1.9.1 on 2026-10-27), solver saga,
  max_iter 2000, tol 1e-4, multinomial loss, sample_weight = w, random_state 20261027. Non-convergence is logged
  and the fit is used as is.
- Calibration: none beyond the model.

### LGBM: shallow gradient-boosted trees (secondary; M4 b)
- LightGBM 4.7.0 (pinned): objective multiclass (3 classes), boosting gbdt, learning_rate 0.05, up to 500 iterations
  with early stopping after 50 rounds without improvement in the weighted multi_logloss of the inner validation
  block, feature_fraction 0.8, bagging_fraction 0.8, bagging_freq 1, lambda_l2 1.0, min_gain_to_split 0, max_bin 255,
  seed 20261027 (all derived seeds from it), deterministic true, force_row_wise true, sample weights w. Threads
  (ProtocolReview FE-3; CLAUDE.md: at most half the cores, never more than 8): processes x threads <= 8 at any time
  (LOGIT fits one thread each, up to 8 processes; LGBM 2 processes x 4 threads or 1 x 8); with deterministic true the
  result does not depend on the thread count.
- Grid: max_depth d in {2, 3} with num_leaves = 2^d, x min_data_in_leaf in {50 h, 200 h} rows (about 50 or 200
  independent labels at horizon h; the vertical barrier's h for TB): 4 points.
- No monotone constraints (M4 b: no minutes-ahead ZM sign is economically fixed for these features).
- Inner validation block: the latest 15% of the fold's training dates by date (rounded up to whole dates); the
  booster is trained on the other training dates and kept at its best iteration (not refit).
- Calibration: a multinomial logistic regression (C = 1e4, lbfgs, max_iter 1000, tol 1e-6; ProtocolReview FE-9;
  non-convergence logged and the fit used as is, FixVerifier R-W4-7) of y on the booster's three raw scores, fitted
  on the inner validation block with weights w; its probabilities feed
  P3.5. LightGBM's feature bins are built from the inner-training rows only (DO-17).
- The mu_k of P3.5 come from all the fold's training rows (inner-train and inner-validation).

### Failed fits (ProtocolReview DO-22)
A configuration with any fold whose fit raises an error, or yields probabilities that are not finite, is failed: it
has no OOF series, fails G1, is recorded with the error, and stays in N. A fold interrupted before it writes its
result (a killed process, an out-of-memory kill, a reboot, a usage-limit pause) is not failed: it is rerun once
from the DONE markers with identical settings (E.33 prompt C3); a second interruption of the same fold fails the
configuration. Every out-of-memory kill counts toward P10's two-failure stop (FixVerifier R-W3-7).

### Not used
Online or regime-switching wrappers (M4 d "maybe": dropped to keep the grid small and the CV analogue exact; the
regime break is met by causal normalisations and reported by the reversed walk-forward diagnostic of P6.5);
sequence models (M4 c skip); monotone constraints; feature selection of any kind (M5b a: importance never steers a
choice inside the same data).

### Compute estimate (ThinkPad: 20 logical CPUs, 14 GB RAM; CLAUDE.md compute rules)
- Book rebuild of ZM.v.0 over 816 dates: 414,363,576 records at 0.39-0.76 M records/s per process, 9-18 minutes in
  one process (F 4.4); peak RSS 125-394 MB per process.
- ZS and ZL re-split keeping all MBP-1 fields: about 90 s of decoding; 32.5 GB of disk at 80 bytes a record if all
  fields are kept (F 4.4; less if fields are dropped).
- Features: about 263 rows a date x 796 dates = 209,000 rows per horizon, 59 features (S5), float32: under 0.1 GB per
  horizon. The feature builder's event loop is the cost: a guess of 1-3 CPU-hours over the 39 months, to be
  replaced by a timed probe on 3 dates.
- Fits: 300 configurations x 6 folds = 1,800 fits on about 170,000 rows each. Guesses: LOGIT (saga) 10-60 s a fit
  (1,080 fits: 3-18 CPU-hours); LGBM 5-30 s a fit (720 fits: 1-6 CPU-hours). With up to 8 single-thread LOGIT
  processes (OMP_NUM_THREADS = OPENBLAS_NUM_THREADS = MKL_NUM_THREADS = 1) or 2 x 4-thread LGBM processes at nice
  10, about 1-4 hours of wall time (FixVerifier R-W4-3). The FeasibilityReviewer's synthetic probes gave 2.4-3.5 s a
  LOGIT fit in a balanced class regime and 1.9-65.6 s when 99% of rows are class 0, and 8-13 s an LGBM fit.
- Synthetic search proofs (P4.2): 4,800 fits (2,880 LOGIT, 1,920 LGBM) on production-size tables, 2.67 times the
  search's 1,800 fits: 11-64 CPU-hours at the guesses above (1.5-9 hours of wall time at 7 single-thread processes,
  a rough figure under the thread rule above; FixSpotCheck S-B-5), 6-10 CPU-hours at the FeasibilityReviewer's
  balanced probes (0.9-1.4 hours). They run before the pipeline freeze,
  their measured wall time is reported, and it counts against E.33's deadlines (P10; FixVerifier FE-2, R-W3-2).
- Probe and compute stop (ProtocolReview FE-4, DO-18; FixVerifier FE-4, DO-18): before the first real-outcome fit,
  E.33 times the feature builder on 3 dates (the median, p90 and maximum ZM message-count dates of F 5) and fold 6
  (the largest training set, 664 dates) of the two slowest grid points (E33-S5F15L100E and E33-S5F15G3050). The
  projected wall time of the search is 796 x the mean per-date builder seconds / P_b + 1,080 x the L100E fold
  seconds / P_L + 720 x the G3050 fold seconds / P_G, where P_b, P_L and P_G are the process counts the thread cap
  of this section allows for the builder, LOGIT and LGBM. E.33 writes that projected wall time, with the probe
  times and this formula, to its STATE file before the first real-outcome fit; the written value is the reference
  for P10's 3x stop. The measured wall time compared with it is the sum of the feature build's wall time (from its
  first to its last DONE marker, whenever it was built) and the 1,800 fits' wall time (from the first real-outcome
  fit to the last DONE marker), each net of the pauses the STATE file logs (usage-limit waits, reboots), the same
  two parts as the projection (FixSpotCheck S-B-3, FinalDiffCheck F-7).
- Every long job (the split, the feature build, the P4.2 proofs, the 1,800 fits, P6.4 and P6.5) runs at nice 10,
  writes a DONE marker per trade date or per configuration and fold, and skips finished pieces on restart (E.33
  prompt C3; FixVerifier R-W4-4).
- No package is added after the pipeline freeze (uv.lock is hashed): statsmodels is not installed, so anything that
  would need it is written in numpy with tests before the freeze or reported as not done (ProtocolReview FE-6).
- Memory: about 50 MB of features per horizon; several processes stay far under the 70%-of-available rule.
- Run order (so that a cut leaves whole feature sets; E.33 prompt C3): S5, S1, S3, S2, S4; inside a set, FH15, FH30,
  FH05, FH60, TB15, TB30; inside a label, the P7.1 grid order. Unrun configurations stay registered and count in N.

## P6. Validation

### P6.1 Folds
- The 796 OOF dates, in order, are cut into K = 6 contiguous blocks of 133, 133, 133, 133, 132, 132 dates.
- For evaluation fold k: training dates = all other blocks' dates minus the embargo, the 21 trade dates immediately
  after block k's last date. 21 covers the longest feature look-back: F1.7's and F4.7's 20-date SDs reach the 13:15
  mid of the 21st date back (ProtocolReview LE-4, AR-5). Training dates per fold: 642, 642, 642, 642, 643, 664. No
  date before block k is removed: labels end inside their own session (P3.6 rule 2), so no training label overlaps
  an evaluation label, and features use only the past.
- Each evaluation row gets the prediction of its fold's model. The OOF series of a configuration is the P3.8
  simulation on the 796 dates, each date using its fold's model.

### P6.2 Metric (the selection variant)
Topstep market orders, L = 1.000 s, f = 0.528. Per configuration: the daily series X_D (796 values); mean,
population SD, daily Sharpe SR_d = mean / population SD, skewness, raw kurtosis and t, exactly as
screening/stage_e_verdict.py moments() and t_stat() compute them (ProtocolReview DO-6, AR-2); trade count, trades per date, mean net per trade, hit rate (share of trades with net > 0), share of dates
with a trade; per-fold, per-quarter and per-month sums; means within volatility terciles (P8 G5 d). Reported for
every configuration but never used by P8 (R5 E item 9, R1 7.1 A8): the Pearson correlation rho over all OOF rows
between the chosen side's EV and the realised net of that side; the hit rate of the realised sign of the mid move over
[t + L, t + L + h] given the chosen side; the mean realised net in the top decile of max(EV_long, EV_short).

### P6.3 Discovery PBO (reported, not a gate)
CSCV PBO over the 300 OOF series with the program's function (screening.stage_e_verdict.pbo: 8 blocks of n_days // 8
dates), reported with M5a e's null band (about 0.13-0.83 for a null search on 39 months).

### P6.4 Execution variants (after the test list is hashed; Tier A and Tier B only; they select nothing)
Every variant is evaluated on one common signal set: the decision times and sides that the selection variant's
simulation (P3.8) produced, so variants differ only in execution (MathReview D-11). Variants use the ts_recv clock
(0.3), the roll and exclusion rules of P3.6, and the latency L of the row. Per firm and route (M6 5.3), each with
that firm's fee per round trip in ticks: Topstep 0.528, Lucid 0.560 (0.920 if the 5.60 USD is not all-in), Bulenox
0.572, MFFU 0.612, Tradeify 0.920:
- (i) Market entry and market exit, and the same at L = 0.300 s.
- (ii) Trade-through limit entry: at t + L the order rests at the touch (bid_1 for a long, ask_1 for a short); it
  fills only when a trade prints strictly through its price (below a buy, above a sell) within min(60 s, h/5);
  market exit as in (i). Routes: Topstep (documented), MFFU, Tradeify Tradovate and WealthCharts, Lucid CQG (assumed
  trade-through under V50, labelled). Reported: p_fill, E[N | fill], E[N_mkt | no fill] (the market-entry net of
  the unfilled signals), the opportunity cost (1 - p_fill) E[N_mkt | no fill], and variant (ii-b), conversion to a
  market order at the timeout.
- (iii) Queue-model limit entry for Rithmic routes (Bulenox, Lucid Rithmic, Tradeify Rithmic): fills simulated with
  E.31's model (a) K-algorithm and (b) FIFO back of queue (kalgo31 as is, and a port of E.31's queue state machine,
  measure31_core's VOrder, Placement and fill logic, to the signal times, written and tested by E.33; reported as
  not done if it is not ready by the P10 cut; F 6.2, FixVerifier FE-6), under the alternative reading of Rithmic's
  rule; under the joint reading (ii) applies (M6 E3).
- For Tier A, per firm: the program's prop-account simulator (the E.19 simulator and prop_econ that M6 3 names) on
  the OOF trade list under the firm's 50K rules: probability of a daily-loss-limit hit and of a trailing-drawdown
  breach per month, and expected trade dates to the first payout.

### P6.5 Diagnostics (after the test list is hashed; Tier A and Tier B only; they select nothing)
- Reversed walk-forward: for k = 1..5, train on blocks k+1..6 only (embargo as P6.1) and evaluate block k: a
  rehearsal of the backward test (M5a c).
- Results by year, by release day versus other days, by roll phase (days to expiry terciles) and by volatility
  tercile (E.33 prompt D2).
- Clustered MDA on the folds with the five blocks C, F1, F2, F3, F4 as the clusters, permuting whole trade dates
  (MathReview C-15), 5 repeats (seeds 1-5), with one noise canary block (M5b a). SFI (one refit per feature and fold:
  up to 59 x 6 = 354 fits per configuration) only if time remains (P10 cut order).
- The VECM loadings of the crush (Johansen) on the discovery dates, for F1's mechanism (M2 e, with MathReview A-4's
  general form); statsmodels is not installed, so E.33 writes it with tests or reports it as not done.
- Day-block bootstrap intervals of the mean net per date (mean block 5 dates, B 10,000, seed 20260923).
- An ancillary non-return test of the mechanism (R1 7.1 A3): the share of the configuration's trades on which the
  mid moved in the chosen direction over the first minute after entry, against 0.5.
- A decay profile (R1 A10): the mean realised mid move in the chosen direction at 1, 5, 15, 30 and 60 minutes after
  entry, whatever the configuration's own horizon.
- Robustness (R1 A11): the mean net per trade and the daily t after dropping the 0.1% of trades with the largest
  absolute net.
- Calibration of the top bucket (R5 E item 7): realised mean net by decile of max(EV_long, EV_short) on the OOF rows,
  against the predicted EV.

## P7. The search budget and the thresholds

### P7.1 Budget
5 feature sets x 6 label types x (6 LOGIT + 4 LGBM grid points) = 300 configurations. Registry ID (the
trial registry's pattern [A-Z][A-Za-z0-9]{0,15}-[A-Za-z0-9]{1,16}; ProtocolReview FE-1, DO-3):
E33-<set><label><grid>, set S1..S5; label F05, F15, F30, F60, T15, T30; grid, in the P7.1 order: L001A (C 0.01,
L2), L001E (C 0.01, elastic net), L010A, L010E, L100A, L100E (C 0.1 and 1.0), G2050, G2200, G3050, G3200 (LGBM depth
2 or 3, min_data_in_leaf 50h or 200h). Example: E33-S5F15L010A. E.33 registers all 300 in one
screening.trial_registry.register call (test "E33", freeze = the hashed configuration file) before any
real-outcome fit. The freeze file holds, per ID, the set, label, h, model, hyperparameters, pipeline sha256 and
protocol sha256 (the prompt's C1 fields; the registry line carries none), and, once for the file, the sha256 of
reports/stage_e33_protocol_readings.md (0.2; FinalDiffCheck F-5). The registry refuses a second
registration under E33, so after any stop or restart E.33 re-uses the one registration and re-checks it with
trial_registry.require_registered(the 300 IDs, test="E33") (FixVerifier R-W4-5). The N of every DSR, threshold and
test in P7.2, P8 and P9 is trial_registry.current_n() immediately after E.33's last registration: the E33
registration (838 if no other stage registers first; ProtocolReview DO-4, AR-3), or the E33A registration of
P4.1 LT7 when one is made (838 plus the E33A count; FinalDiffCheck F-1). Nothing
else in E.33 is a configuration: P6.4 variants and P6.5 diagnostics run after the test list is hashed and select
nothing; the synthetic proofs read no real outcome.

### P7.2 Thresholds at N = 838 (reports/stage_e32_briefs/protocol/p7_final_budget300.md, from p7_final.py; literal
N; normal moments unless stated)
- Discovery (T_disc = 796): SR0 = E[max SR] = 0.1137 daily; G3 (DSR > 0.95, V = 1/(T_disc - 1)) needs SR_d >=
  0.1724 (t 4.86; 2.74 annualised); 0.1756 at skew -0.5 and kurtosis 6.
- The test (T_test = 870, P9): daily t > 3.0 is SR 0.1017; the protocol-added DSR > 0.95 at N 838 with
  V = 1/(T_test - 1) is SR 0.1649 (t 4.86); b_test = 0.1649 (2.62 annualised); 80% power needs a true daily Sharpe
  of 0.1936.
- G4 (power gate) needs SR_d - se(SR_d) >= b_test: SR_d >= 0.2007 (t 5.66; 3.19 annualised). Binding selection
  threshold: 0.2007.
- Per trade (random-walk sigma_h; independent trades every date): 0.71 ticks net at 5-minute holds and 4 trades a
  date (0.50 at 8); 1.22 at 15 minutes and 4 a date (0.87 at 8); 1.73 at 30 minutes and 4 a date; 3.46 at 60 minutes
  and 2 a date.
- Selection and test together (P7.2 table): a configuration whose true daily Sharpe is s in both windows is
  selected and then passes with probability 0.03 at s = 0.15, 0.11 at 0.17, 0.42 at 0.20, 0.91 at 0.25.
- Reference thresholds over the 300 (one-sided 0.05): Bonferroni or Holm step 1 z 3.588; BH rank 1 the same; BY rank
  1 z 4.042 (c(300) = 6.283); Bonferroni at N 838 z 3.847; the test's Holm (holm_tier_a at K = 9 over m tested
  candidates, alpha 0.05/(9m)) z 2.539, 2.773, 2.902 for m = 1, 2, 3 (ProtocolReview AR-4); HLZ t > 3.0. None is a
  gate: G3 (t about 4.86) is stricter at discovery than each of them, and t > 3.0 is stricter at the test than Holm.
- b_test is pinned at p7_final.py's unrounded value at the registered N (0.164882 at N 838, T_test 870; displayed
  0.1649), and G4 compares against that value (FixVerifier AR-2, R-W1-4). The user may drop the protocol-added test
  DSR only by a decision recorded before E.33's C1 registration, as an amendment under 0.2: a new protocol version
  hashed before C1, whose P7.2 states b_test = 0.1017, G4 = 0.1373 and the binding selection threshold 0.1724 (G3)
  (FixVerifier DO-2, R-W2-2). After the E33 registration b_test changes only with an E33A registration (P4.1
  LT7), when p7_final.py recomputes every threshold at the new N before P8 is re-run (ProtocolReview DO-2;
  FinalDiffCheck F-1). If the registered N differs from 838 at the E33 registration, p7_final.py recomputes every
  threshold at that N before any real-outcome fit.
- The test-power figures above (and P4.2's) assume the test's DSR checks use V = 1/(T_test - 1). The program verdict
  as coded (V14 c) takes V = the population variance of the 2-3 tested Sharpes, so its SR0 = 3.2045 x the population
  SD of those Sharpes (the E[max] multiplier at N 838): with one null companion SR0 = 1.60 x the strong member's
  Sharpe (two nulls: 1.51 x), and no true Sharpe passes; with a weaker but real companion SR0 = 3.2045 x half the
  gap between them (two members), so a true 0.25 beside a true 0.15 needs 0.217 and passes with about 0.83, and
  beside 0.10 it needs 0.297 and passes with about 0.09 (FixSpotCheck S-B-6) (ProtocolReview AR-1, its a3_out.txt;
  FixVerifier AR-1,
  R-W1-1). Under V14 (c) as coded these powers are upper bounds that depend on the list's composition; amending
  V14 (c) as P9 reserves makes the DSR part of check (1) identical to check (2), so it can only loosen the combined
  bar, and only to the bar whose power is tabulated. P9 reserves the remedy to the user.

## P8. Selection rule (mechanical)

Inputs: the 300 OOF series and statistics of P6.2. Every configuration is evaluated on every gate, and E.33 reports
the funnel (the count passing each gate alone and in order G1..G5). G1-G5, the ranking and the walks below are the
whole selection rule: the per-firm nets, FDR, PBO and session or robustness splits that E.33's prompt (D1-D2) asks
for are reports, never gates (ProtocolReview DO-20). A failed configuration (P5) fails G1.
- G1 Activity: at least 1.0 trade per OOF date on average (at least 796 trades) and a trade on at least 50% of the
  OOF dates.
- G2 Edge: mean net per trade >= 0.50 tick (Topstep, market, L = 1 s). The margin also covers the highest firm fee
  (Tradeify 0.920: a 0.392-tick shift leaves at least 0.108).
- G3 Significance: DSR > 0.95 (the program's sign; FixVerifier R-W1-12) with the program's function
  (funnel.multiple_comparisons.deflated_sharpe_ratio) at N = the registered N of P7.1 (after E.33's last
  registration; FinalDiffCheck F-1),
  V = 1/(T_disc - 1), T = T_disc, and the configuration's own skewness and raw kurtosis (moments(), 0.3;
  FixVerifier R-W3-8, R-W2-3). A DSR that cannot be computed fails G3.
- G4 Power: SR_d - se(SR_d) >= b_test, with se(SR_d) = sqrt((1 - g3 SR_d + (g4 - 1)/4 SR_d^2)/(T_disc - 1)) from the
  configuration's moments (g3 skewness, g4 raw kurtosis) and b_test = the unrounded value P7.2 pins in the protocol
  version whose sha256 E.33 verified at A1, recomputed by p7_final.py only if N differs from 838 (FixVerifier DO-2).
- G5 Stability (M5b b): (a) mean daily net > 0 in at least 9 of the 13 calendar quarters (Dec-Feb, Mar-May,
  Jun-Aug, Sep-Nov; the first without the burn-in dates); (b) total net > 0 and no calendar month's net above 25% of
  the total; (c) for each of the 39 months, the daily t of the series without that month (mean/SD x sqrt(n), the
  population SD of t_stat(); 0.3; FixVerifier R-W3-11) >= 2.5;
  (d) mean daily net > 0 within each tercile of sigma_ZM(D): the 796 OOF dates sorted by sigma_ZM(D) ascending (ties
  by date), ranks 1-265, 266-530 and 531-796 (ProtocolReview DO-14; sigma_ZM(D) is known before D opens).
- Ranking of the configurations that pass G1-G5 (a total order; ProtocolReview DO-7): SR_d rounded to 4 decimals
  with Python's round() (half to even; FixVerifier R-W2-4), descending; then fewer trades per date; then LOGIT
  before LGBM; then the lower set index; then the shorter horizon
  (FH before TB at equal h); then the earlier grid point in the P7.1 order.
- Tier A (the finalists, at most 3): walk the ranking; take a configuration if its OOF daily series has Pearson
  correlation <= 0.70 with every configuration already taken; stop at 3.
- Tier B (2 configurations, run on the test window only to supply the program verdict's DSR variance and PBO when
  Tier A has one member; never finalists; ProtocolReview DO-5): continue the Tier A walk over all 300
  configurations ordered by the same key, gates ignored, taking the next two whose OOF daily series has correlation
  <= 0.70 with every configuration already taken (Tier A and Tier B). A configuration with no OOF series (failed,
  P5) or a constant OOF series (no trade) is skipped. If fewer than two qualify, Tier B is filled by the
  highest-ranked remaining configurations with a defined series, and E.33 reports their correlations (FixVerifier
  DO-5, R-W2-1). Near-duplicates are excluded because they would make the verdict's variance collapse (DO-5's
  simulation: a true daily Sharpe of 0.12 would pass the program's DSR 93% of the time at rho 0.98 between the
  series, 43% at rho 0.70; FixVerifier R-W2-5).
- If Tier A is empty: no test list and no purchase; P10's null report.
- The frozen model of a configuration for the test is the 6-model ensemble of its folds: calibrated class
  probabilities averaged over the 6 fold models, and the mu_k averaged over the 6 training folds; nothing is refit.
  Decision rule P3.5, exits P3.3-P3.4, one contract, market entry and exit, firm Topstep (50K Combine and XFA via the
  ProjectX API: the lowest ZM fee, automation admitted; M6 4.1, 5.3); other firms are reported (P6.4).
- The test list (configuration IDs, tiers, the 6 fold models of each with sha256, the pipeline sha256 list, the
  P9 calendar procedure) is written to reports/stage_e33_finalists.md and hashed before any P6.4 or P6.5
  computation.

## P9. The test stage (sketch, to be registered by the user later)

- Data: ZM.v.0 MBO, ZS.v.0 and ZL.v.0 MBP-1, and ZM, ZS and ZL definitions for trade dates 2017-05-22..2020-11-30,
  requested from 2017-05-21. Databento's GLBX.MDP3 page (saved at reports/stage_e32_briefs/pages/F_data_facts/
  F_db_glbx-mdp3.html.txt, fetched 2026-10-27 00:31 PDT): "On 2017-05-21, CME introduced full granularity for every
  order event (MBOFD). Data prior to this date is based on the MDP 2, level-aggregated FIX protocol", for which "the
  MBO schema is not available" and "The ts_recv field on all MDP 2 data is set to the same value as ts_event". The
  15 trade dates 2017-05-01..2017-05-19 stay sealed and untested. 890 program trade dates; the first 20 are burn-in,
  so T_test = 870. Whether ts_recv in 2017-2020 is a capture timestamp comparable with the discovery files' is a
  data check the test stage makes from the metadata before the read (the pipeline orders by ts_recv either way).
- Purchase: a quote only after a funded Databento account exists and the user approves a fresh quote (V51 item 4;
  no Databento call in E.32 or E.33). The files land under the soy seal's read guard and are opened once.
- Release calendar for 2017-05..2020-11: built before the read by the P3.6 rule from the same public sources (USDA
  OCE WASDE release-date pages, NASS calendar list views, NOPA reporting-date PDFs), parse rule included, hashed,
  never edited after; the test stage asserts one USDA WASDE, one NASS Crop Production and one NOPA date (row or rule
  date) per calendar month of the window, 43 each, and, for the four other P3.6 rule-3 report types, the counts a
  worker other than the calendar builder derives by hand from the saved source pages (FinalDiffCheck F-6), recorded
  and hashed with the calendar before the read; it stops on any other count
  (FixVerifier LE-3, FixSpotCheck S-B-7).
- One read: the frozen pipeline (P8's hashes) runs once over the test window, computes the Tier A and Tier B daily
  series (Topstep, market, L = 1 s) and applies (1) the program verdict exactly as coded (screening/stage_e_verdict.py:
  Holm at K = 9 per V14 b; DSR > 0.95 at the list's program N (= the N of P7.1: 838, or 838 plus the E33A count;
  FinalDiffCheck F-1;
  unless trials were registered after E.33, in which case the registry's N at the test registration, recorded
  beside it; FixVerifier R-W1-9) with
  the population variance of the Tier A Sharpes if two or more, else of Tier A and Tier B, V14 c; daily t > 3.0;
  CSCV PBO < 0.5) and (2) the protocol-added DSR > 0.95 (the program's sign; FixVerifier R-W1-12) at the same N
  with V = 1/(T_test - 1). A Tier A configuration passes only if both pass; it then reads "edge
  candidate, composite pending" (V14 a), never "edge". Execution variants and the prop simulator are reported per
  firm.
- Reserved decision for the user, before the test is registered (ProtocolReview AR-1): whether to amend V14 (c) for
  this test so that the program verdict's DSR uses V = 1/(T_test - 1), the same V as the protocol-added check. As
  coded, V14 (c) takes the population variance of the 2-3 tested Sharpes, which makes a real edge fail with near
  certainty beside a null companion and with a probability that rises with the gap between the members' true
  Sharpes (P7.2; FixVerifier R-W1-1). Amending can only loosen the combined bar, and only to the point where its
  DSR part equals check (2), whose power P7.2 tabulates (Holm, t and PBO unchanged); the discovery outcomes cannot
  steer it further (FixVerifier R-W1-10). E.32 does not amend a user
  decision; it states the consequence.
- No re-run: a bug found after the read voids the test; the window is spent.
- Regime differences named before any outcome: the oil-share regime (R3a 2), the 2020 COVID liquidity collapse
  (R3b d), the 2021-2022 change in federal position limits (R3b c), lower volume in 2017-2019.

## P10. Stop rules and the null report

Early stops are for integrity and feasibility only. No result stops, shortens or extends the search: every
configuration runs to completion even after one passes, and none is added or dropped.
- Stop at once on: a hash mismatch (P1.1); a guard refusal or any read of refused market data or outcomes (P1.2); a
  leakage or synthetic-proof failure (P4.1, P4.2) that cannot be fixed without changing a declared choice; a
  declared choice of P1-P5, P6.1-P6.2, P7 or P8 that cannot be implemented as written (0.2; a P6.3-P6.5 item that
  cannot be implemented is reported as not done and is not a stop; FixVerifier R-W4-2); a measured wall time of the
  search above 3 times the projected wall time written to the STATE file before the first real-outcome fit (P5;
  FixVerifier DO-18), or two out-of-memory failures.
- E.33's deadlines (its prompt as last amended before E.33 starts; at this writing, user 2026-10-27 08:16: if the
  full budget cannot finish by 07:00 PDT on 2026-10-28, whole families are finished (C3); work stops at 08:00; the
  return is written by 08:45; nothing runs after 09:00; these times are feasibility limits, not declared choices,
  so the prompt's current times govern and an amendment of them does not amend this protocol; FixVerifier DO-19,
  R-W3-1, R-W4-1). The cut unit is a whole feature set in the P5 order (S5, S1, S3, S2, S4), which is the "family"
  of the prompt's C3 (ProtocolReview DO-19): a set is started only if its projected wall time, 216 x the mean
  measured wall seconds of the LOGIT fits finished so far in this run / P_L + 144 x the same for the LGBM fits /
  P_G (the P5 probe seconds in place of a mean that does not exist yet; P_L and P_G the process counts in use),
  written to the STATE file with the clock time before the decision, ends by 07:00 (FinalDiffCheck F-3); a started
  set runs to completion; a set still running at 08:00 is stopped, and all its configurations are excluded from P8
  as a set and recorded as not evaluated (the finished ones' series stay on disk and the return lists them as run
  but not evaluated, the rest as unrun; FinalDiffCheck F-4), so P8 sees whole sets only (FixSpotCheck S-B-2,
  lead's choice). Unrun and not-evaluated configurations stay registered and count in N, and P8 runs on the whole
  sets that ran, with the registered N. A features-only store (P4 features at every minute mark; no
  label, no return) may be built as soon as B3 passes and before the pipeline freeze, keyed by the sha256 of the
  feature code that built it, and is rebuilt if the frozen feature code differs; labels, fits and simulations wait
  for the freeze and the C1 registration (FixVerifier FE-11). When time is short, reports are cut
  in this order (first cut first): the VECM diagnostic, SFI, clustered MDA, the P6.4 (iii) queue variants, the prop
  simulator, Tier B's variants, the rest of P6.5 (ProtocolReview FE-11). G1-G5 and the test list are never cut.
- On any stop after outcomes exist: report what ran; every configuration run stays in N.
- If Tier A is empty, E.33 reports: (i) the gate funnel; (ii) the 10 best configurations by SR_d with every P6.2
  statistic; (iii) the distribution of the 300 OOF daily Sharpes beside the synthetic null distribution and SR0 at
  N; (iv) the discovery PBO; (v) the minimum detectable net edge per trade at 80% power on the OOF dates per horizon;
  (vi) per family, whether a null statement in the sense of docs/NULL_CRITERIA_E.md is supportable, or "no
  statement"; (vii) the sentence "No candidate; the test window stays sealed; no test data purchase." N rises by 300
  (plus any E33A re-runs, P4.1 LT7) whatever the outcome.
