# Stage E.34 frozen discovery protocol: the ZL program (F10 order-book state and F09 soy-complex lead-lag into ZL)

Status: DRAFT v0.2 (2026-10-29, lead Opus 5.5 max, session 3): v0.1 (session 2) with every BLOCKING and SHOULD FIX
item of the two reviews (MathReviewer and ProtocolReviewer, Fable xhigh) fixed, and some NOTEs; each change and its
review item are listed in reports/stage_e34_briefs/review/FixLog.md. For FixVerifier (Fable xhigh).
The frozen version carries its sha256 in reports/stage_e34_zl_protocol.sha256 and in reports/E.34_RETURN.md; any
later edit voids the freeze. NOT REGISTERED. Registration belongs to the run stage, after the user decides:
- E.32b-D2: give ZL's single sealed read to this program;
- E.32b-D3: admit a discovery search judged by the power rule instead of V31's cost gate (P10, K0);
- E.32-D2: the test DSR variance rule (P9.4);
- OC-5, the reading of V43 (ProtocolReview S10): that S_crush and S_prop, built from bar leaders and ZL's book
  context and traded against ZL's book, run as ML under V43 (option A, this text). Otherwise option B (12 F09 rules
  under V28 beside ML for F10, E.32b recs 4.5(b); M2 (f)'s rules variant on the grid of L.c, without M2's 12:50 CT
  cap, MathReview S3) is registered instead, as an amendment, and P7 is recomputed at N_before + 62.

The run stage runs this protocol unchanged on owned data of 2020-12-01..2024-02-29. If the stop rules allow it and
the user has decided the items above, it then reads the sealed window once. Nothing here was chosen by looking at an
outcome: E.34 trained nothing and computed no feature value, label, return or markout (stage scope).

Sources, with the short names used below:
- M1-M4 and L: Part M, reports/stage_e34_zl_methods.md: a lead front (verdicts and errata), then M1 F10 on ZL, M2
  F09 into ZL, M3 labels, M4 power and L the lead's reconciliations, the files reports/stage_e34_briefs/M1_F10_ZL.md,
  M2_F09_ZL.md, M3_labels_ZL.md, M4_power_ZL.md and L_lead_reconciliations.md concatenated unchanged (ProtocolReview
  S3). Where the errata correct a worker file, the errata govern;
- DF34: reports/stage_e34_data_facts.md;
- X: reports/stage_e34_exposure.md;
- the reviews under reports/stage_e34_briefs/review/;
- "E.32 Pn.m (lines a-b)": the frozen E.32 protocol reports/stage_e32_discovery_protocol.md, v1.0, sha256
  c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05, with E.33c's amendment 0.3 where named
  (reports/stage_e33c_briefs/protocol_v0.3.diff);
- E.33's frozen pipeline: reports/stage_e33_pipeline_freeze.sha256, code under reports/stage_e33_briefs/work/pipeline/;
- E.32b recs: reports/stage_e32b_recommendations.md, sections 4.5 and 6;
- docs/DECISIONS.md.

Where this text says "as E.32 Pn.m", the E.32 text applies word for word after the substitutions of 0.4. Where it
states a rule in full, that rule replaces E.32's.

## 0. What binds, change control, notation and the mirror rule

### 0.1 Binding sources
- V43 (docs/DECISIONS.md 788-806), for every configuration: model, features, labels, training window,
  hyperparameters and code frozen and hashed before any outcome read; every configuration searched counts into N;
  purged and embargoed cross-validation on the discovery data; one test on data that never selected the model, with
  the program's bar (Holm, net Sharpe, DSR at N, PBO); costs from the measured fill model, never touched-means-filled;
  no model trades, on paper or live, before it passes.
- V50 item 4 (E.31 read the discovery dates: "Any test of an order-flow signal on these dates is therefore not a
  clean holdout"; a discovery use is disclosed exposure, P1.5).
- V51 item 2 (2024-03-01 onward stays closed), V55 (routing), V56 (ZM's route closed; "Order-book direction is not
  closed for other products"; item 1 keeps ZL's sealed window for a future hypothesis family), V57.
- E.32b recs 4.5 (the ZL fact table, the draft outline, the data plan) and section 6 (the stop rule).
- V14 (b) Holm K = 9 and (c) the DSR variance rule, as coded in screening/stage_e_verdict.py (harness v14,
  2e908c81...), subject to E.32-D2 (P9.4).
- This document.

### 0.2 Change control
As E.32 0.2 (lines 28-45), with "E.33" read as "the run stage". The readings file is
reports/stage_<run>_protocol_readings.md, written by the run stage's lead before the registration and hashed into its
pipeline freeze list. The run stage may fix code so that it does what this text says; it may not change any declared
choice. An amendment is a new protocol version decided by the user and hashed before it runs.

### 0.3 Notation (where it differs from E.32 0.3, lines 46-81)
- Clock, trade date D ([D-1 16:00, D 16:00) CT on ts_recv), day session 08:30:00-13:20:00 and overnight session
  19:00 on D-1 to 07:45 on D: as E.32 0.3. Times are America/Chicago (CT).
- Front: the ZL front on D is the instrument_id mapped to ZL.v.0 for D in the manifest's symbology
  (measure31.instrument_on). ZS and ZM enter only through ohlcv-1m bars of ZS.v.0 and ZM.v.0 (P1.1). No ZS or ZM book
  record and no ZL.v.1 record is read.
- Ticks: ZL 0.01 cents/lb = USD 6.00, read from the definitions (measure31.read_definitions, checked_tick with E.31's
  ZS/ZL USD-check fix); ZS 0.25 cents/bu; ZM 0.10 USD/short ton.
- Book: ZL from MBP-1, the top of book after each event plus action-T trade records with aggressor side. bid_1,
  ask_1, qb_1 and qa_1 are the touch prices and displayed sizes; no deeper level exists in this program. A book
  update is the state after a record carrying F_LAST, of any action (F and R records included, as
  feat33.stream_mbp1), timed at that record's ts_recv; its batch is the records after the previous F_LAST record up
  to and including its own. Bad-book reading for MBP-1, the same for features, labels, exclusions and fills (E.33
  reading FA-4, feat33.stream_mbp1; MathReview S2, ProtocolReview B2): an update is bad iff any record of its batch
  carries F_MAYBE_BAD_BOOK. The mark belongs to that update only (MBP-1 has no R record; E.33's code clears it at
  each F_LAST record), so the book is undefined from a bad update to the next good one. "As of u" is the last
  good-or-bad book update with ts_recv <= u. Mid M_ZL(u) = (bid_1 + ask_1)/2 as of u, defined only when both sides exist,
  bid_1 < ask_1 and the update is not bad. Spread s(u) = ask_1 - bid_1.
- Bars: an ohlcv-1m record of root X stamped m covers [m, m + 1 min) (Databento's convention; the run stage saves
  and hashes the schema page that states it before the registration). Under the other convention (a bar stamped m
  covering [m - 1 min, m)) the rule-B bar would be one minute older, never later, so rule B cannot look ahead under
  either (MathReview N12 b). Rule B: at decision time t the last usable bar of any root is the one stamped t - 1 min. A bar is built from trades by exchange time, and its last trade's ts_recv
  can follow t by its capture latency (DF34: ts_recv - ts_event exceeds 1 s on 354 of 158,046,466 ZL MBP-1 records),
  which lies inside the 1 s order latency L. P4.1 LT8 reports this count for ZL, the one root with both feeds. S(u) and M(u) are the closes of the
  last usable ZS and ZM bars. A root whose last bar with volume > 0 is stamped earlier than t - 2 min is stale at t.
- sigma_X(D) for X in {ZL, ZS, ZM}, "window of k minutes ending at t", "trailing 20-date reference", the decision grid
  G_h(D) and the statistics conventions: as E.32 0.3. sigma_ZL uses ZL book mids; sigma_ZS and sigma_ZM use 1-minute
  bar-close changes, chained across rolls, in ticks of X, over the 1-minute intervals inside 08:35-13:13 whose two end
  marks both have a usable bar under rule B (an interval with a missing bar is skipped, not filled: E.32 0.3's "valid
  mids at both ends" read for bars; ProtocolReview N5).
- Latency L = 1.000 s (selection); L = 0.300 s is reported for the test list only (P6.4).
- Fee f = 0.880 ZL ticks per round trip (Topstep USD 5.28 / USD 6.00; E.32b holding scope 15).

### 0.4 The mirror rule (substitutions applied to every "as E.32" reference)
Traded leg ZM -> ZL; the ZM book (MBO, mbo_book31) -> the ZL book (MBP-1, 0.3); ZM tick 0.10 USD/short ton -> ZL
tick 0.01 cents/lb; f 0.528 -> 0.880; sigma_ZM -> sigma_ZL; M_ZM -> M_ZL; E.33 -> the run stage; E.33's file names ->
the run stage's. F1 (crush) -> F09c and F2 (propagation) -> F09p (P2, P4, with the definitions of P4 replacing
E.32's); F3 (ZM book) -> F10 (P4, replacing E.32 F3); F4 -> not in this program (P2). No look-back, threshold, sign,
clip or weight differs from E.32's text unless units or data force it, and each such change is stated where it is
made, with its reason (X rule 4).
Counts and names in inherited text (ProtocolReview S2): 300 configurations -> 200; S5 -> S_pool, S1 -> S_crush, S2 ->
S_prop, S3 -> S_book, S4 -> none; the 59 S5 feature columns -> the 43 S_pool columns; N 838 -> N_reg (1038 if no other
trial registers first); the binding-threshold z 5.66 -> 5.72 (G4 x sqrt(T_disc) = 0.2028 x sqrt(796)), and any other
E.32 threshold figure -> its value at N_reg from the functions of P7.1; the five MDA blocks C, F1, F2, F3, F4 -> the
four blocks C, F09c, F09p, F10; SFI 59 x 6 = 354 fits -> 43 x 6 = 258; a set's fold counts 216 LOGIT and 144 LGBM ->
180 and 120 (5 labels x 6 or 4 settings x 6 folds); E.32's run order S5, S1, S3, S2, S4 -> S_pool, S_crush, S_book,
S_prop; labels F05, F15, F30, F60, T15, T30 -> F15, F30, F60, T15, T30; P4.2's planted-proof figures 0.91 and 0.914 ->
0.90 and 0.905 (select-and-pass 0.898 and selection 0.905 at a realised daily Sharpe of 0.25 at N 1038; ProtocolReview
recompute_p7.out). The synthetic proofs (P4.2) run at the thresholds of P7.2.

### 0.5 Standard numbers (for thresholds and power only; the run stage never uses them in place of a measurement)
ZL day-session sigma_h 5.52 / 12.05 / 20.37 / 28.10 / 38.21 ticks at h 1 / 5 / 15 / 30 / 60 (E.32b holding scope 15,
owned bars 2022-11-01..2023-10-31); planning round trip c_f 2.38 ticks = spread 1.0 tick (assumed) + 0.5 slippage
(assumed) + f 0.88 (E.32b recs 4.5(a)); entry maxima under the grid and P3.8: 17 / 8 / 4 trades a date at h 15 / 30 /
60 for the FH labels (L.b); the TB labels' count per date is realised and capped at 20 (P3.8).

## P1. Discovery data

### P1.1 Files
- ZL MBP-1: the 39 monthly files of mbp-1/Z3_ZL_v_0/ in the 156-file manifest of E.32 P1.1 (sha256
  09396842c4fd5d742c166e5b6ca1327c5eeebfed9b112952b84d15f254c23261), from range=2020-11-30T220000Z_2020-12-31T220000Z
  to range=2024-01-31T220000Z_2024-02-29T220000Z (DF34 section 6); ZL definitions: the ZL_FUT records of
  definition/Z4_ZM_FUT-ZS_FUT-ZL_FUT/ in the same manifest.
- Bars: the ohlcv-1m files of ZL_v_0, ZS_v_0 and ZM_v_0 from range=2020-12-01_2021-01-01 to
  range=2024-02-01_2024-03-01, 39 per root (DF34 section 4; X rule 1).
- Before reading any record, the run stage re-runs reports/stage_e32_briefs/work/lead/verify_discovery_hashes.py
  (sha256 c329f443...; 156 of 156 must match), then hashes the 117 bar files once, before any read of them (no
  expected list exists before the run stage, so this first hashing is the reference, and the list is part of the
  pipeline freeze; ProtocolReview N12), and stops on any mismatch or missing file.
- E.33's ZL split store (derived/e33/split/ZL: 816 per-date files 2020-12-01.npy..2024-02-29.npy) may be reused as
  data after the run stage checks it against the raw Z3 files on 3 dates (equal record counts per date) and checks
  its DONE counts (X rule 2). E.33's ZS split is not used (no ZS book feature exists here).
- Nothing is bought for discovery (M1 4.4 route A; P11).

### P1.2 Data allowlist, refusals and record drops
- The run stage's data guard is a copy of guard33 with its allowlist changed (X rule 1). It allows only the files
  of P1.1, E.33's ZL split store, the release calendars of P3.6 (sha256-pinned), the program calendars
  (data.calendars.grains, data.cme_calendar, data.hist_calendar) and the run stage's own derived tree. It keeps every
  guard33 refusal: data/sealed/ and the sealed originals (docs/soy_test/SOY_TEST_MANIFEST.json); any ZL, ZS or ZM
  data with a trade date in 2017-05-01..2020-11-30 or on or after 2024-03-01; any record with ts_recv before
  2020-11-30T22:00:00Z; reports/stage_e32_briefs/seal/derived_unsealed_files.tsv and every file it lists;
  reports/stage_e31_briefs/work/pilot/runs/; data/vendor/databento/rolls/*; the FRED soybean-oil csv
  reports/stage_e20_briefs/pages/ZL/fred_PSOILUSDM.csv; every other root's market data (CL, HO and RB included);
  the ML caches ~/.cache/propexp_*. Its dry check runs at least guard33's four probes plus a ZL ohlcv-1m name in
  2020-11 and an E.33 results folder; all must be refused (X rule 1).
- Record drops (L.d), applied on load, before any feature or label, counted by rule and reported (a record that
  meets several rules is counted under each and once in the total, so the overlap of rules 1 and 2 is visible;
  MathReview N5): (1) records flagged F_SNAPSHOT or F_BAD_TS_RECV; (2) records with ts_event before
  2020-11-30T22:00:00Z or with ts_recv - ts_event above 86,400 s; (3) records whose instrument_id is not D's ZL front
  (0.3; DF34 section 5: 83 records on 14 dates; ProtocolReview S5). Dropping reads ts_event; no feature, label,
  exclusion or fill reads it; the G6 clock report and the LT8 count read it for reports only (counts, no outcome;
  ProtocolReview S4). Records outside D's ts_recv window are refused by the guard (E.33's _check_window).
- Outcome files that no run-stage worker and no lead consults while declaring or running (X rule 3): E.31's
  stats31.md and .json and X1's Table C with its appendix; E.33, E.33b and E.33c results (E.33c_RETURN.md sections
  3.4-3.8 and the files they cite, search33 stats.json, P8_select33.json, D_stats.md and .json); the E.22 K6 ZL trip
  files and member rows; E.25 NM1 ZL rows; the E.12 gate0B_ZL rows; the E.20 search outputs; the E.17 units files;
  E.21 per_root/ZL.json. Every run-stage brief carries this list.

### P1.3 Sessions
- The day session is the search: label starts 08:35:00 to 13:12:00 - h; every label ends by 13:13:00 (P3).
- The overnight session carries no label, no trade and no selection. Its records enter features only (windows that
  reach back across 08:30). Reasons: Topstep allows no overnight hold for this account (E.32b recs 4.5(a) prop fit;
  K4), and 23.8% of ZL trade records fall outside the day session (DF34 section 3: 3,812,647 of 16,019,898), at
  wider spreads.

### P1.4 Trade dates
- Universe: the 816 regular grains trade dates 2020-12-01..2024-02-29 (program calendars; DF34 section 1).
- Burn-in: the first 20 dates (features computed for look-backs; no row, trade or daily value). OOF dates: the
  remaining T_disc = 796.
- Excluded from trading (daily value 0, no rows; features still computed for later look-backs): (i) a ZL roll date
  (the ZL front on D differs from the front on the previous trade date) and the trade date after it
  (measure31.roll_reasons applied to ZL); (ii) early-close and scheduled late-open dates (measure31.calendar_reason).
  The run stage counts them by the rule. DF34 section 5 counts 25 ZL front changes on the discovery dates, 9 of them
  back-and-forth flips (for example ZLN1 and ZLK1 alternating 2021-04-05..04-12; ProtocolReview N2); each change is a roll date here.

### P1.5 Prior exposure of the discovery dates, and the firewall
The inventory is X section 1 (reports/stage_e34_exposure.md; its sha256 is a line of P10.4's freeze list). In brief
(X section 5): ZL's discovery dates are not virgin, but no feature of this program was ever tested against a ZL
outcome. Every earlier ZL-labelled outcome on these dates came from a one-minute-bar mechanism unrelated to F09 and
F10, and all were null or FAIL (the E.22 K6 ZL members, E.12 Gate 0 family B, E.17's pooled settlement window, E.20's
pooled search, E.21's trend). The order-book reads (E.31, E.33) used ZL MBP-1 only as an input to ZM labels or as a
split of ZM fills. The strongest exposure is indirect: E.33 searched crush z-scores and the crush change d5 against
ZM labels, series equal up to scale to F09c's, and found a clean negative (Tier A empty). Direct exposure exists for
ZL's own returns and for 60-minute cross-market leads on ZL (E.12, E.20), including the test window's
2019-05..2020-11 bars. E.34's lead read E.33c_RETURN.md sections 1-3.8 while orienting (X row 19); nothing in this
protocol cites them.

The firewall (X section 3, rules 1-10; adopted and restated below, with rules 2, 6 and 7 tightened against X's text;
ProtocolReview N9):
1. The data allowlist of P1.2.
2. E.33's ZL split may be read as data; E.33's labels, search, statistics and selection outputs may not.
3. The outcome files of P1.2 are never consulted.
4. Definitions are E.32's text passed through 0.4. Each change forced by units or data (MBP-1 for F10, bars for the
   leaders) is listed at its feature with its reason. No item's only stated source is an outcome file.
5. The grid is not trimmed by outcome. The labels are E.33's six minus FH05, by band B (cost and sigma, sign-free).
   The model settings are E.33's ten. No set, label, setting or feature is added, dropped, ordered or weighted by
   reference to E.33's or E.31's results. Every grid element carries its source (P2, P4, P5).
6. Minute look-backs only: no lead feature from ZS or ZM into ZL has a look-back under 5 minutes (P4; E.31's ZL
   splits used 1 s and 10 s).
7. No queue-imbalance bucket edge from E.31 (+-0.2, +-0.6) appears anywhere; F10.7 and F10.8 are continuous.
8. Selection is mechanical (P8). Discovery selects; the one sealed read confirms (V43).
9. Loader rule: previous-date loads come only from the run stage's own 816-date list, so 2020-12-01 has no previous
   date; each load passes check_request and check_records. A unit test asks for the previous trade date of
   2020-12-01 and expects a refusal or no date (X section 6).
10. Disclosure: the registration carries X section 1 (or a pointer to it with its sha256) and states that E.34
    computed nothing on ZL.

Choices excluded because of exposure (X section 4, adopted): E1 lead-lag features from ZS or ZM into ZL with
look-backs of seconds; E2 queue-imbalance thresholds or buckets from E.31; E3 a ZL own-price-path set (the E.32 F4
mirror) and ZL's own returns as stand-alone features; E4 60-minute cross-market lead returns (CL, NQ, ZN, 6E, GC) as
ZL features; E5 a once-a-day overnight crush-gap rule; E6 pruning or ranking sets, labels or settings by E.33's
results. ZL's own price enters only inside declared relative-value or scale quantities (the crush and its residual,
the implied-oil gap, C.6), never as a stand-alone return or path feature. A fitted model can recombine those
quantities: in S_prop and S_pool, ZL's own scaled k-minute return is a linear function of gR_k, rS_k and rM_k with
date-varying coefficients (before clipping, -dO_k/(0.01 sigma_ZL sqrt k) = gR_k - b_S (0.25 sigma_ZS/(0.01 sigma_ZL))
rS_k - b_M (0.10 sigma_ZM/(0.01 sigma_ZL)) rM_k), which a LOGIT model can recover approximately and a tree model
partially. E3 therefore removes the stand-alone feature and its direct test history, not the information
(ProtocolReview S12). The disclosure above stands: the earlier ZL own-price trials selected nothing here, and their
reads of the test window's 2019-05..2020-11 bars are named in the seal document (reports/stage_e32_test_seal.md
section 4).

## P2. Idea families

Three idea families and one context block (C). Each family's features enter its own set with C; the pooled set holds
all three (V43; E.32b recs 4.5(b) P4-P5, option A). Sets: S_crush = C + F09c, S_prop = C + F09p, S_book = C + F10,
S_pool = C + F09c + F09p + F10.

### F09c Crush residual with ZL as the adjusting leg (the E.32 F1 mirror)
- Mechanism: the board crush C = 11 O + 2.2 M - S (cents/bu; O ZL in cents/lb, M ZM in USD/short ton, S ZS in
  cents/bu; E.32 F1, MathReview A) is cointegrated within the day session. When ZS or ZM moves, the crush dislocates,
  and part of it may close through ZL within minutes.
- Evidence and reasoning (M2 bottom line 1, (a), (d); (e) for the prior only): expected gross per trade G = s_L x D x (1 - 2^-m) / 0.11
  ZL ticks; ZL must close 52% of a 1-cent dislocation within one half-life to clear 2.38 ticks (35% in two half-lives),
  against ZM's 70% in E.32; cost per sigma 0.085 against ZM's 0.092. No published intraday s_L or half-life exists;
  the one intraday source (Zhou et al.) finds that both ZS and ZM Granger-cause ZL more as ZL's relative volume rises;
  daily evidence puts biofuel shocks first in ZL in the renewable-diesel regime. E.33's negative on ZM rules out "ZM
  adjusts strongly", not "ZL adjusts"; it is weak, mildly negative evidence for F09 on ZL (M2 e).
- Changes against E.32 F1, forced by data or the traded leg: a ZL-dependent regression residual (L1.3) and an origin
  split (L1.5-L1.6) replace ZM-specific items; the overnight items F1.7-F1.8 are dropped (E5). Sources of the two
  additions (ProtocolReview S9): the rolling ZL-dependent residual from M2 (a).2 (never fixed physical weights:
  Janzen and Wang's weekly cash regression; beans decoupled from oil after 2020); the origin split from M2 (a).1-2 and
  (d).4 (in the renewable-diesel regime biofuel shocks start in ZL: Avileis and Swanson). Neither cites an E.31 or
  E.33 result.

### F09p Propagation: ZS and ZM lead ZL at minutes (the E.32 F2 mirror)
- Mechanism: information reaches ZS and ZM first; ZL catches up over minutes through crush arbitrage and hedging.
- Evidence and reasoning (M2 b): seconds-scale lead-lag cannot pay the round trip at a 1 s latency, so look-backs are
  5, 15 and 30 minutes; the useful form is the implied-oil gap (how far ZL lags what the ZS and ZM moves imply
  through the crush) plus each leader's own scaled return.
- Changes against E.32 F2, forced by data: the leaders come from ohlcv-1m bars (no ZS or ZM book is owned for the
  test window; buying one would add a larger test-window purchase than the ZM bars of P11), so no leader OFI feature
  exists; k = 1 is dropped (the bars' bid-ask bounce in the implied-oil gap, over the two bar closes of a k-minute
  change, is about 2.25 ZL ticks: 41% of sigma_1 and 19% of sigma_5; M2 (b).3 as corrected by MathReview S4); k = 30
  is added because it matches band B's h_c (M2 (b).1: holds of 15-60 minutes), the reason F10's OFI_30 and TI_30 are
  added (P4). Neither change cites an E.31 or E.33 result (ProtocolReview S9).

### F10 ZL order flow and book state on MBP-1 (the E.32 F3 mirror)
- Mechanism: persistent buying or selling pressure moves the mid over the next minutes before it is absorbed.
- Evidence and reasoning: as E.32 F3 (lines 209-222). ZL facts (M1, L.a): 8 of E.32's 12 F3 features carry over to
  MBP-1 with their definitions unchanged (windows changed as listed after the P4 F10 table), 2 are adapted (F10.7 seasoned queue imbalance by a 1-second running minimum; F10.9 cancellations
  with fills attributed by price inside the event batch), and 2 need depth beyond level 1 and are dropped (E.32 F3.4,
  F3.8). Minimum aggregation horizon 5 minutes (L.a).
- Why MBP-1 and not MBO (M1 4.2): the MBO-only features are the ones M1's evidence rates lowest; MBO does not reduce
  the discovery dates' exposure, which is of dates, not schemas (V50 item 4); MBP-1 in both windows needs no
  equivalence proof. Cost of the choice: a weaker spoofing guard (an upper bound on seasoned depth) and approximate
  cancellation attribution.

### C Context block (in every set, never searched alone)
As E.32 C (lines 236-240), on ZL (P4).

### Not in this program (with reasons)
- The E.32 F4 mirror (ZL's own price path): E3.
- CL as a leader (M2 c): E.12 and E.20 already used CL's 60-minute return as a lead on ZL, including the test
  window's 2019-05..2020-11 bars (E4), and the literature links energy to vegetable oil only weekly or daily. No CL
  feature of any form enters. HO, RB and RIN series: not owned for either window, or no intraday series exists.
- MBO-only F10 items (E.32 F3.4 integrated OFI, F3.8 three-level queue imbalance): no depth in MBP-1.
- A once-a-day overnight crush-gap rule and F1.7-F1.8: E5.
- VECM loadings and half-lives as features: they enter only as a report-only diagnostic (P6.5; M2 d).
- Option B of E.32b recs 4.5(b) (12 F09 rules under V28 beside ML for F10): not run. Lead ruling (open choice OC-5):
  every configuration of this program is labelled on and traded against ZL's own book with the measured fill model,
  and every set carries ZL's book context, so the program is one order-book program under V43, as E.33 ran its
  crush and propagation sets as ML under V51 ("ML is a core tool, under V43"). The reading is the user's to confirm
  before registration (header; E.34_RETURN section 7; ProtocolReview S10); option B is then an amendment.
- An FOMC exclusion window: not adopted (OC-8). E.32 has none, and it would add a calendar dependency; the 13:00 CT
  statement days stay in, as noise the models cannot predict.
- Labels FH05 and TB60, to-close and 1-minute labels: band B and M3 a.4.

## P3. Labels, horizons and sampling

### P3.1 Horizons and label types (5)
Fixed-horizon executable labels FH15, FH30, FH60 and triple-barrier labels TB15, TB30 (E.32b recs 4.5(b) P3; M3 a.4).
FH05 is outside band B; TB60 is out (M3 a.4).

### P3.2 Executable prices
As E.32 P3.2 (lines 262-276) on the ZL book: a market buy decided at u fills at ask_1 of ZL as of u + L, a sell at
bid_1 as of u + L, one contract, no depth walk; the fallback, entry-not-made, limit-mark and last-touch-mark rules
apply with ZL's front and its limits (P3.6 rule 5); m0 of P3.4 is M_ZL as of the entry fill update. Labels and
fills read the ZL MBP-1 book in both windows, with the same code (MathReview S2).

### P3.3 Fixed-horizon label
    N_long(t)  = bid_1(t + h + L) - ask_1(t + L) - 0.880
    N_short(t) = bid_1(t + L) - ask_1(t + h + L) - 0.880          (ZL ticks)
    y(t) = +1 if N_long(t) > 0; -1 if N_short(t) > 0; 0 otherwise (the run stage asserts that both are never positive).

### P3.4 Triple-barrier label
As E.32 P3.4 (lines 285-297) on ZL: m0 = M_ZL(t + L), b(t) = 1.0 x sigma_ZL(D) x sqrt(h), the first ZL book update in
(t + L, t + L + h min] reaching m0 + b(t) or m0 - b(t) (undefined mids ignored), exits by market order at tau + L,
f = 0.880.

### P3.5 Trade rule
As E.32 P3.5 (lines 298-308), unchanged.

### P3.6 Exclusion rules
As E.32 P3.6 (lines 309-345) on the ZL book and front, with these readings:
1. Open: no span starts before 08:35:00.
2. Close: every span ends by 13:13:00, before the 13:14-13:15 CT settlement window (L.c).
3. Releases: E.32 rule 3 word for word (the seven report types, the two E.31 calendar files with their sha256 and
   parse rule, the NOPA rule dates and the asserted counts) for the discovery dates. For the test window the run
   stage builds the same seven report types for 2017-05-22..2020-11-30 from primary sources, hashes the file and
   asserts its counts before the sealed read (P9.2).
4. Rolls and calendar: P1.4 exclusions.
5. Locked or halted book and price limits: E.32 rule 5 on ZL (the limits HL and LL from the ZL front's last
   definition record with ts_recv <= 08:30:00 CT on D; c = (HL + LL)/2; the 2% band; skip-and-count when no record or
   UNDEF_PRICE).
6. ZS or ZM invalid or stale (0.3): rows are kept; F09 features fall back per P4 G3.
Report-only stratum (selects nothing; after the test list is hashed): EIA Weekly Petroleum Status Report minutes,
09:28-10:00 CT on Wednesdays that are trade dates (holiday shifts not modelled).
The run stage reports how many rows and minutes each rule removes.

### P3.7 Rows and sample weights
As E.32 P3.7 (lines 346-355): every t in G_h(D) on every OOF date that meets P3.6 and has a valid M_ZL(t) (263, 248,
218 grid minutes a date at h 15, 30, 60); weights are the raw average uniqueness at 1-minute resolution.

### P3.8 Realised trade simulation
As E.32 P3.8 (lines 356-366): one position at a time, at most 20 entries a date, the decision uses only records with
ts_recv <= t, the next decision at the first grid minute at or after the exit fill. Under the grid the most FH trades
a date are 17, 8 and 4 at h 15, 30 and 60 (L.b), so the 20-entry cap never binds for FH15, FH30 and FH60; it can bind
for TB15 and TB30, whose trade count per date is realised (a barrier exit frees the account early; MathReview S1,
ProtocolReview N8). The latest entries are 12:57, 12:42 and 12:12 CT (L.c). X_D is the
sum of the net P&L of the trades entered on D, in ZL ticks per contract per day.

## P4. Features (exact definitions)

### General rules
- G1 Point in time: a feature at t uses only ZL book records with ts_recv <= t and bars usable at t under rule B (0.3).
  Trade counts (C.5, TI_k, F10.12's sv_i) count each T record by its own ts_recv <= t, even when its batch's F_LAST
  record arrives after t; book-state features use the last book update with ts_recv <= t; F10.9, F10.10 and F10.11
  work per batch and count a batch once its F_LAST record has ts_recv <= t. Each is known at t (MathReview N12 c).
- G2 Look-backs follow 0.3. Scale references chain across rolls. Every F09 level or difference (L1.1-L1.6, L1.8,
  L2.1-L2.9) uses only the current fronts: a segment is a maximal run of trade dates on which the ZL front (0.3) and
  the instrument_ids carried by the ZS.v.0 and ZM.v.0 bars are all unchanged, and a window or fit sample that would
  cross a segment boundary or a front change of any root it uses makes the feature invalid. An F10 window spanning two
  ZL instrument ids is invalid (M1 section 7). A trade date on which a root's bars carry two instrument_ids is a
  front change of that root (its segment breaks there); the run stage counts such dates per root (DF34 found none for
  ZL; not verified for ZS and ZM, ProtocolReview "not finished").
- G3 Invalid values: an invalid feature takes the value 0, and its family flag (C.11 F09c, C.12 F09p, C.13 F10) is 0
  for that row if any feature of the family is invalid. A stale ZS or ZM root at t (0.3) makes every F09 feature that
  uses it invalid at t.
- G4 Clipping to [-5, 5] after their own normalisation: C.5, L1.1-L1.3, F10.1-F10.3, F10.10-F10.12, L2.1-L2.9; L1.4,
  L1.6 and L1.8 are computed from the clipped L1.1 and then clipped. Not clipped (bounded by construction or the log
  of a positive scale): C.1-C.4, C.6-C.13, C.15, L1.5, L1.7, F10.4-F10.9.
- G5 Model standardisation, G6 clocks and G7 agreement tolerance: as E.32 P4 G5-G7 (lines 383-394; ProtocolReview N1)
  with the ZL book in place of the ZM book. The run stage writes two independent implementations of every feature
  and label (E.33's practice, its B3) and compares them on the discovery dates within G7's tolerance before any
  real-outcome fit (ProtocolReview N10); P10.3's compute reference does not include this work. Under G6 the run stage reports, per month, the distribution of ts_recv - ts_event for the ZL
  MBP-1 feed; bars carry no ts_recv. All book prices in features and labels are mids or executable touch prices;
  leader prices are bar closes (rule B), never last-trade prices of ZL.

### C Context (14 features)
As E.32 C (lines 396-411) on ZL: C.1 tod and C.2 tod^2 on the 08:35-13:13 axis; C.3 min(s_ZL(t), 5) ticks; C.4
log(1 + qb_1 + qa_1) of ZL at t; C.5 log((V_ZL(15) + 1)/(Vbar + 1)), with V_ZL(15) the contracts of ZL T records of all
sides in the 15-minute window ending at t and Vbar their mean at the same minute of day over the 20 prior trade
dates; C.6 log(sigma_ZL(D)); C.7 min(trade dates from D to the expiration of the ZL front, from its last definition
record with ts_recv <= 08:30:00 CT on D, 60)/60 (the test needs the test window's definitions, P11); C.8 the P3.6
rule-3 release flag; C.9 C.8 x 1{t >= 11:30}; C.10 Monday or first trade date after a full closure; C.11-C.13 the
validity flags of F09c, F09p and F10 (G3); C.15 June-August. C.14 (E.32's F4 flag) does not exist here.

### Leader and crush inputs (F09)
O(u) is the ZL mid M_ZL(u) of the book (0.3). S(u) and M(u) are the closes of the last usable ZS and ZM bars (rule
B). V_X(15) in L1.7 is, for each of ZL, ZS and ZM, the sum of its bar volumes over the bars stamped m - 1 min for the
15 minute marks m of the window of 15 minutes ending at t on the open-time axis (0.3), so a window at 08:35-08:49
reaches back across the 07:45-08:30 pause as C.5's does (ProtocolReview N4); one source type for all three legs (a
change from M2 (f), which took ZL's volume from its book).
sigma_X(D) as 0.3. Crush statistics are in cents/bu.

### F09c Crush (8 features; M2 (f), verbatim)
| ID | Definition | Look-back | Normalisation |
|---|---|---|---|
| L1.1 | zC30 = (C(t) - mean_30)/sd_30, C = 11 O + 2.2 M - S; mean and sd over C(t - j min), j = 1..30 | 30 min, in segment | own rolling z; clip |
| L1.2 | zC120: as L1.1 with j = 1..120 | 120 min, in segment | as L1.1 |
| L1.3 | zRL = e_L(t)/sd_e; before D's open, OLS O = a + b_S S + b_M M on the clean 1-minute samples 08:35-13:13 (release marks [R - 2, R + 30] min excluded) of the 10 trade dates before D in the segment (at least 3 dates or invalid); centred fit, a from the means; e_L = (O - a - b_S S - b_M M)/0.01 in ZL ticks; sd_e = fit residual SD in ZL ticks; coefficients fixed for D | 10 dates | sd_e; clip |
| L1.4 | dzC5 = zC30(t) - zC30(t - 5 min) | 35 min | difference of z |
| L1.5 | oL30 = 11 dO_30 / (\|11 dO_30\| + \|2.2 dM_30\| + \|dS_30\|), dX_30 = X(t) - X(t - 30 min) | 30 min | bounded [-1, 1]; invalid if denominator 0 |
| L1.6 | zC30 x (1 - \|oL30\|) (reversion weighted to leader-opened dislocations) | 30 min | product |
| L1.7 | vrelL15 = V_ZL(15)/(V_ZL(15) + V_ZS(15) + V_ZM(15)) | 15 min | share in [0, 1] |
| L1.8 | zC30 x vrelL15 | 30 min | product |

### F09p Propagation (9 features; M2 (f), verbatim)
| ID | Definition | Look-back | Normalisation |
|---|---|---|---|
| L2.1-L2.3 | rS_k = (S(t) - S(t - k))/0.25/(sigma_ZS(D) sqrt(k)), k = 5, 15, 30 | k min | sigma_ZS(D); clip |
| L2.4-L2.6 | rM_k = (M(t) - M(t - k))/0.10/(sigma_ZM(D) sqrt(k)), k = 5, 15, 30 | k min | sigma_ZM(D); clip |
| L2.7-L2.9 | gR_k = [b_S dS_k + b_M dM_k - dO_k]/0.01/(sigma_ZL(D) sqrt(k)), b_S, b_M from L1.3's fit for D (invalid when L1.3 is invalid), k = 5, 15, 30 | k min | sigma_ZL(D); clip |

F09 readings: zC30's mean and SD are population statistics over the 30 one-minute samples C(t - j min), j = 1..30;
the L1.3 fit is the centred lstsq of 0.3 with an intercept, fitted before D opens and fixed for D; dX_k = X(t) -
X(t - k min) on the open-time axis. Not included (M2 (f)): k = 1, the physical-weight gap, the overnight crush gap,
any leader book feature, any CL, HO, RB or RIN feature, ZL's own returns (E3), and VECM features (P6.5).

### F10 ZL order flow and book state (12 features; M1 section 7, verbatim)
Book updates are F_LAST records of any action, F and R included (0.3); F and R records are neither trades nor
removals and enter no T, C or M count (ProtocolReview S8); a batch containing F_MAYBE_BAD_BOOK marks its update bad
(0.3, FA-4); windows of k minutes run on ZL's open-time axis; trailing references as 0.3.
| ID | Definition | Window / parameters | Normalisation | Clip |
|---|---|---|---|---|
| F10.1-F10.3 | OFI_k = sum over consecutive good two-sided ZL book updates in (t - k, t] of e_n = 1{bid_n >= bid_{n-1}} qb_n - 1{bid_n <= bid_{n-1}} qb_{n-1} - 1{ask_n <= ask_{n-1}} qa_n + 1{ask_n >= ask_{n-1}} qa_{n-1}; no term for the first update of an open interval; a pair with a one-sided or bad state contributes 0 and is counted; crossed or locked states allowed | k = 5, 15, 30 min | / Obar_k = trailing 20-date reference mean of abs(OFI_k); invalid if Obar_k = 0 | [-5, 5] |
| F10.4-F10.6 | TI_k = (B_k - S_k)/(B_k + S_k): B_k (S_k) = contracts of T records with side B (A) and ts_recv in (t - k, t]; side N excluded | k = 5, 15, 30 min; invalid if B_k + S_k = 0 | none (bounded) | no |
| F10.7 | QI1s = (qb~ - qa~)/(qb~ + qa~): qb~ = 0 if the most recent change of bid_1 with ts_recv in (t - 1 s, t] was an increase (MathReview B1); else min of qb_1 over the book states with ts_recv in [t_c, t] and the state as of t_c, t_c = max(t - 1.000 s, last change of bid_1); qa~ symmetric (0 if the most recent change of ask_1 in (t - 1 s, t] was a decrease) | seasoning 1.000 s; invalid if qb~ + qa~ = 0 (ProtocolReview S6) | none | no |
| F10.8 | QIbar5 = mean of QI1s at the 300 one-second marks t - 299 s .. t (on the open-time axis; invalid marks skipped) | 5 min; invalid if fewer than 150 valid marks | none | no |
| F10.9 | CR5 = (Ca_5 - Cb_5)/(Ca_5 + Cb_5): Cb_5 = the sum, over the event batches b whose F_LAST record has ts_recv in (t - 5 min, t] and over bid touch prices p, of max(0, D_b(p) - T_b(p)); D_b(p) = the decrease of the bid touch at p summed over every consecutive pair of front records from the state before b to b's F_LAST record, of any action (same price and lower size -> the decrease; touch price fell from p -> the whole previous size at p); T_b(p) = the contracts of b's T records printed at p (fills attributed first; no carry across batches). This is correct whether the post-fill size reduction sits on the T record or on a later C or M record (MathReview B2). A pair with a one-sided state, or inside a bad batch, contributes 0 and is counted. Ca_5 symmetric on the ask | 5 min; invalid if Ca_5 + Cb_5 = 0 | none | no |
| F10.10 | SW15 = (sw_buy_15 - sw_sell_15)/sbar_15: a trade set = T records sharing one ts_event (any side); buy sweep if at the set's batch end ask_1 > the ask_1 as of the record before the set's first T, or the ask side is empty; sell sweep symmetric on the bid | 15 min | sbar_15 = trailing 20-date reference mean of sw_buy_15 + sw_sell_15; invalid if 0 | [-5, 5] |
| F10.11 | RF15 = (rf_bid_15 - rf_ask_15)/rbar_15: a refill on side X = an A record at price p, side X, ts_recv within 100 ms after the batch end of a trade set that emptied touch level p on side X (F10.10 rule), that makes p the touch again | 15 min; refill window 100 ms | rbar_15 = trailing 20-date reference mean of abs(rf_bid_15 - rf_ask_15); invalid if 0 | [-5, 5] |
| F10.12 | lam60 = OLS slope (with intercept) of dM_i (ZL mid change over 1-minute interval i, ticks) on sv_i = B_i - S_i (contracts, side N excluded), over the trade-bearing 1-minute intervals among the 60 ending at t | 60 min; invalid with fewer than 30 intervals | / abs(trailing 20-date reference median of the same slope), so lam60 keeps the slope's sign; invalid if that median is 0 (ProtocolReview N3) | [-5, 5] |

Not added (M1 section 7): order-count features (bid_ct_00, ask_ct_00) and the microprice. Dropped from E.32 F3:
F3.4 IOFI5 and F3.8 QI3 (depth beyond level 1) and F3.1-F3.3's 1-minute window (L.a). Windows changed against E.32
F3, with reasons, none from an outcome (ProtocolReview S7): OFI k = 1, 5, 15 -> 5, 15, 30 and TI k = 5, 15 -> 5, 15,
30 (L.a: the minimum aggregation horizon is 5 minutes at ZL's trade rate; 30 is added to span band B's h_c); the
sweep window 5 -> 15 minutes (SW5 -> SW15; M1 2.3 d: sweeps are rarer than trades); QIbar5 (F10.8), a 5-minute mean
of QI1s, takes QI3's place (M1 2.3 b).

### P4.1 Leakage, pipeline and data tests (before any model is fitted on real outcomes)
- LT1-LT7: as E.32 P4.1 (lines 466-504) with 0.4's substitutions. LT1's input streams are the ZL MBP-1 records, the
  three roots' bars and the ZL definitions; LT1 truncates the book at ts_recv <= t and the bars at rule B.
- LT8 Bar timing: for 200 decision times (seed 20261029) across the OOF dates, recompute every F09 feature after
  deleting every bar stamped t - 1 min or later except the rule-B bar, and then after deleting the rule-B bar too;
  the first must equal production within G7, the second must differ only in features that use the rule-B bar. Count
  report (no outcome): for ZL, whose MBP-1 and bars are both owned, the share of grid minutes at which the last T
  record inside the rule-B bar, by ts_event, has ts_recv > t. The count changes no rule (ProtocolReview N7).
- LT9 Record drops: a unit test with synthetic records for each P1.2 drop rule; the real drop counts by rule.
- LT10 Loader: the previous trade date of 2020-12-01 is refused or does not exist (X rule 9).
- LT11 Fronts: no feature window or fit sample spans two instrument ids of a root it uses; each ZL front change of
  DF34 section 5 is a P1.4 roll date. The run stage reports, per F09 family, the share of OOF dates and of rows on
  which the family flag is 0 by construction (segment starts, stale roots); P10.5 shows it beside the F09 sets'
  results (ProtocolReview N11).
- LT12 F10 hand values (M1 trap 9, M1_F10_ZL.md line 407, and its siblings): synthetic MBP-1 streams with
  hand-computed F10.7 and F10.9, including the rise-then-fall second (bid_1 p -> p + 1 -> p inside the last second,
  old orders resting at p: qb~ = the min over [t - 0.2 s, t], not 0; MathReview B1) and both placements of a
  post-fill size reduction (on the T record; on a later C or M record of the batch), which must give the same
  removal count (MathReview B2).
- LT13 Clock (MathReview N12 a): the grid is built per date in America/Chicago, and the decision-minute count is
  278 - h on every ordinary trade date of both windows, across the CST and CDT changes.
- Data checks before any label (counts only; M1 section 7): DC1 day-session share of ZL events and T records; DC2 per
  batch with a T at the touch, which record carries the post-fill size reduction (the T record or a later C or M
  record; F10.9 is correct in both cases); DC3
  sweeps and refills per 15 minutes on 5 dates; DC4 side-N share at 08:30:00-08:30:05; DC5 the share of seconds in
  which the touch price fell (F10.7's bound is looser there). They are reported and change no declared choice.

### P4.2 Synthetic proofs
As E.32 P4.2 (lines 505-534), with each planted mechanism moved to its mirror family (F1 to F09c, F2 to F09p with
planted leader bars, F3 to F10 on a synthetic MBP-1 stream); the F4 plant is dropped.

## P5. Models (two families) and compute
As E.32 P5 (lines 535-577), unchanged: LOGIT (regularised multinomial logistic regression, primary, 6 settings) and
LGBM (shallow gradient-boosted trees, secondary, 4 settings), the failed-fit rule and the not-used list. The compute
estimate of E.32 (lines 578-615) is replaced by P10.3.

## P6. Validation
As E.32 P6 (lines 616-682) with 0.4's substitutions: P6.1 the 6 blocked folds and the 21-date embargo; P6.2 the
selection metric; P6.3 the discovery PBO (reported, not a gate). Changes:
- P6.4 execution variants (after the test list is hashed; Tier A and Tier B only; they select nothing; M3 g):
  (i) market at L = 1.000 s and 0.300 s; (ii) a trade-through limit at the ZL touch, filled on the first A or B
  print strictly through the limit within (t + L, min(t + 60 s, exit decision) + L], side-N prints never fill;
  (ii-b) (ii) converted to market at the timeout; Topstep fee only. E.32's variant (iii) (E.31's MBO queue logic) is
  not run: MBP-1 has no order queue. For Tier A, E.32 P6.4's prop-account simulator (lines 659-661: the E.19
  simulator and prop_econ) runs on the OOF trade list under Topstep's 50K rules: daily-loss-limit and
  trailing-drawdown breach probabilities per month and expected trade dates to the first payout (ProtocolReview N6).
- P6.5 diagnostics as E.32 P6.5, plus the VECM report (M2 d): for every set, after P8's result is written and hashed,
  whether or not anything passes: the loadings alpha on (ZS cents, ZL ticks, ZM ticks), ZL's adjustment share s_L,
  the weak-exogeneity test alpha_L = 0 and the half-life hl = -ln 2 / ln phi with phi = 1 + beta' alpha, each fitted on
  the 20 trade dates before D (day session, 1-minute bars, release marks excluded, beta normalised on the ZL entry,
  lag order 5). It selects nothing.
- FDR report: Benjamini-Hochberg at q = 0.10 over the 200 configurations' one-sided p-values of the OOF daily t
  (H0: mean daily net <= 0; t_stat() of 0.3). A report, never a gate (E.32 P8 line 744).

## P7. The search budget and the thresholds

### P7.1 Budget
4 sets (S_crush, S_prop, S_book, S_pool) x 5 labels (FH15, FH30, FH60, TB15, TB30) x 10 model settings (E.32 P5) =
200 configurations. Run order (ProtocolReview S1): sets S_pool, S_crush, S_book, S_prop (P10.3's cut order); inside a
set FH15, FH30, FH60, TB15, TB30; inside a label the P5 grid order (6 LOGIT, then 4 LGBM). All 200 count into N at the
registration, whatever runs: N_reg = N_before + 200, which is 1038 if no other trial is registered first. Execution
variants, diagnostics and reports are not configurations. Registration mechanics as E.32 P7.1 (lines 685-701;
ProtocolReview S11), with "E33" read as the run stage's test name and 300 as 200: one
screening.trial_registry.register call for all 200 before any real-outcome fit; registry IDs <test>-<set><label><grid>
with set C (S_crush), P (S_prop), B (S_book), L (S_pool), label F15, F30, F60, T15, T30 and grid as E.32 P7.1 (L001A
.. G3200); the freeze file's fields as E.32 P7.1 (set, label, h, model, hyperparameters, pipeline sha256, protocol
sha256, and once the readings file's sha256); after any stop or restart the one registration is re-used and
re-checked with trial_registry.require_registered. The registration recomputes P7.2 at the registry's N immediately after it, with the functions
named in M4 (p7_final.se_sharpe, p7_final.g4_threshold, p7_thresholds.required_sharpe,
funnel.multiple_comparisons.expected_max_sharpe and deflated_sharpe_ratio), and pins b_test unrounded.

### P7.2 Thresholds at N = 1038 (M4 (g), row B 200; T_disc 796, T_test 870)
| item | value |
|---|---|
| G3: DSR > 0.95, as a daily Sharpe | 0.1746 |
| b_test (unrounded, pinned) | 0.166967 |
| G4 = the binding discovery threshold (SR_d - se >= b_test) | 0.2028 |
| SR80_test (80% power at the test) | 0.1957 |
| SR80 for discovery at the binding threshold | 0.2330 |
| test e80 at the FH grid caps 17 / 8 / 4 (h 15 / 30 / 60), ticks a trade net; not for TB labels (P3.8) | 0.97 / 1.94 / 3.74 (L.b) |
| test e80 at h 30 and 1 / 2 / 4 trades a date | 5.50 / 3.89 / 2.75 |
| daily t bar at the test | 3.0 |
The e80 figures assume independent trades with sigma_h; heavy tails add about 1-3% at kurtosis 6-20 and about 11%
(13% on the binding threshold) at skew -2 and kurtosis 30 (M4 c as recomputed by MathReview N2), and same-day
correlation multiplies them by sqrt(1 + (k - 1) rho), so they are floors (M4 c). For TB configurations the trade
count is realised and the measured K2 form governs (P10.2). SR80 follows E.32's convention, se taken at the bar (the
exact bisection gives 0.1958 against 0.1957; MathReview N1). P10.5 reports the measured version (SR80_test x SD(X_D) /
mean trades a date) beside them.

## P8. Selection rule (mechanical)
As E.32 P8 (lines 740-787) on the 200 configurations, with these values:
- G1 Activity: at least 1.0 trade per OOF date on average (at least 796 trades) and a trade on at least 50% of the
  OOF dates.
- G2 Edge: mean net per trade >= 0.50 ZL tick (USD 3.00; Topstep, market, L = 1 s): half a tick of the traded
  contract, as in E.32. E.32's firm-fee reason does not arise: the program trades at Topstep only (E.32b recs 4.5).
- G3 and G4: as E.32 at N_reg, V = 1/(T_disc - 1), T = T_disc, the configuration's own moments, and b_test of P7.2
  (or its recomputation at N_reg).
- G5: as E.32 (13 quarters, 39 months, the leave-one-month-out t >= 2.5), with the terciles of sigma_ZL(D) (ranks
  1-265, 266-530, 531-796).
- Ranking, Tier A (at most 3, correlation <= 0.70) and Tier B (2, over all 200, gates ignored): as E.32, with the set
  index S_crush 1, S_prop 2, S_book 3, S_pool 4.
- If Tier A is empty: no test list and no purchase (K1).
- The frozen model of a configuration for the test is the ensemble of its 6 fold models, as E.32. Firm: Topstep
  (50K Combine and XFA via the ProjectX API).
- The test list (configuration IDs, tiers, the 6 fold models of each with sha256, the pipeline sha256 list, the P9
  calendar procedure) is written to reports/stage_<run>_finalists.md and hashed before any P6.4 or P6.5 computation.

## P9. The test stage (sketch, registered later)

### P9.1 Data
ZL.v.0 MBP-1 and ZL definitions for trade dates 2017-05-22..2020-11-30, requested from 2017-05-21 (L.e). The ZL and
ZS ohlcv-1m bars inside the sealed soy files (owned: 44 raw monthly chunks each, 2017-04..2020-11,
reports/stage_e32_test_seal.md section 2; docs/soy_test/SOY_TEST_MANIFEST.json). The ZM ohlcv-1m bars for
2019-05..2020-11 inside the sealed files (19 raw monthly chunks) and, for 2017-05-01..2019-04-30, ZM.v.0 ohlcv-1m
bought with the test data (not owned: "no earlier ZM file is owned", seal section 2; ProtocolReview B1), requested
from 2017-05-01 to the start of the owned 2019-05 chunk so that the two abut. Without them ZM would be stale on
2017-05-22..2019-05-03, more than half of the test dates, and the F09 sets would have no like-for-like test; if they
cannot be bought, the run stage stops before the read and reports (P9.2). 890 program trade
dates; the first 20 are burn-in, so T_test = 870. The 15 MDP 2 trade dates 2017-05-01..2017-05-19 stay sealed and
untested (MDP 2: ts_recv equals ts_event and F_BAD_TS_RECV is set on every record). Before the read, from metadata
only, the run stage checks that ts_recv in 2017-2020 is a capture timestamp comparable with the discovery files'.
P1.2's drop rules apply with the test window's first instant, 2017-05-21T21:00:00Z.

### P9.2 Purchase and calendar
- Quote first, under the user's approval, on a new funded account slot DATABENTO_API_KEY4 (absent at E.34's end;
  accounts 1-3 have less than USD 3 of headroom), for three items: ZL.v.0 MBP-1, ZL definitions and ZM.v.0 ohlcv-1m
  2017-05-01..2019-04-30 (P9.1). Estimates, not quotes: USD 23.36 for ZL MBP-1 (census USD 0.5432 a month x 43; E.32b
  recs 4.5(c)); about USD 1.46 for the ZM bars (24 months x USD 0.0608, the median of the 73 settled ZM.v.0 ohlcv-1m
  monthly buys in ledger/databento_spend.jsonl; USD 1.77 at the dearest month, 0.0738); at most about USD 1.66 for
  the definitions (43 months x USD 0.0385, the median settled month of the three-parent ZM/ZS/ZL definition buys, of
  which a ZL-only request is a subset); about USD 26.5 in all. The files land under the soy seal's read guard
  (soy_test_seal.py) and are opened once. If the definitions or the ZM bars cannot be bought, the run stage stops
  before the read and reports (C.7 and P3.6 rule 5 need the definitions; every F09 feature needs ZM); it does not
  substitute a rule.
- The release calendar for 2017-05..2020-11 is built and checked before the read exactly as E.32 P9 (lines 799-806)
  states: same sources and parse rule, hashed and never edited; one USDA WASDE, one NASS Crop Production and one NOPA
  date per calendar month (43 each); the four other report types counted by hand by a second worker from the saved
  pages; any other count stops the read. The builder records each NOPA release's time from the saved pages, and the
  rule-3 window follows the recorded time, 11:00 CT where none is recorded (ProtocolReview N13).

### P9.3 One read and the pass bar
As E.32 P9 (lines 807-815): the frozen pipeline runs once over the test window and computes the Tier A and Tier B
daily series (Topstep, market, L = 1 s). It applies (1) the program verdict as coded in screening/stage_e_verdict.py
(Holm at K = 9 per V14 b; DSR > 0.95 at the registered N with V14 c's variance; daily t > 3.0; CSCV PBO < 0.5), and
(2) DSR > 0.95 at the same N with V = 1/(T_test - 1). A Tier A configuration passes only if both pass; it then reads
"edge candidate, composite pending" (V14 a), never "edge". Holm never binds before the DSR (M4 e: z at most 2.90
against b_test's t of 4.86 or more, unless the bootstrap SE exceeds the iid SE by more than 1.67 x). No re-run: a bug
found after the read voids the test; the window is spent.

### P9.4 E.32-D2: the test DSR variance (a user decision before registration)
As coded, V14 (c) takes the population variance of the tested Sharpes (Tier A if two or more, else Tier A and Tier B).
Beside null companions, no true Sharpe can pass: SR0 is 1.633 x the member's Sharpe with one null at N 1038 and 1.539 x
with two (M4 f). M4's synthetic simulation at N 838 (4,000 replications; N 1138 is 0.00-0.04 lower):

| true Sharpes (finalist first) | as coded: all checks | amended (V = 1/(T_test - 1)): DSR and t |
|---|---|---|
| 0.20 + 2 nulls (Tier A of 1, Tier B null) | 0.000 | 0.845 |
| 0.25 + 2 nulls | 0.000 | 0.995 |
| 0.25 + 0.15 | 0.699 | 0.993 |
| 0.20 + 0.15 | 0.725 | 0.857 |

Amending makes the program DSR equal check (2); it cannot loosen the bar below check (2), and Holm, t and PBO are
unchanged. Every power figure in P7.2 assumes the amendment, or at least two real finalists of similar true Sharpe;
unamended, they are upper bounds. Recommendation in E.34_RETURN section 7: amend for this test.

### P9.5 Regime differences named before any outcome
The oil-share regime (renewable diesel: discovery inside the high-oil-share regime, the test before it), the 2020
COVID liquidity collapse, the 2021-2022 change in federal position limits, and lower volume in 2017-2019 (E.32b recs
4.5(b) P9).

## P10. Stop rules, compute reference, freeze list and the null report

### P10.1 Integrity stops
As E.32 P10 (lines 832-838): stop at once on a hash mismatch (P1.1); a guard refusal or any read of refused data or
outcome files (P1.2); a leakage, data-test or synthetic-proof failure (P4.1, P4.2) that cannot be fixed without
changing a declared choice; a declared choice of P1-P5, P6.1-P6.2, P7 or P8 that cannot be implemented as written; a
measured search wall time above the P10.3 stop; or two out-of-memory failures. No result stops, shortens or extends
the search; every configuration runs to completion, and none is added or dropped. On any stop after outcomes exist,
report what ran; every configuration counts in N.

### P10.2 Program stop rules (E.32b recs 4.5 K0-K4 and section 6)
- K0: if the user keeps V31's cost-feasibility gate in force for discovery searches (E.32b-D3 not admitted), the
  program does not run.
- K1: if Tier A is empty under P8 at N_reg, stop: no test read and no test purchase.
- K2 (L.b): after the test list is hashed and before any purchase, compute for each Tier A configuration c
  e80_test(c) = SR80_test(N_reg, T_test) x SD(X_D,c) / nbar_c on its OOF discovery dates; if no Tier A configuration
  has OOF mean net per trade >= e80_test(c), stop: the test could not detect it. Recompute at the realised T_test
  immediately before the read. With T_test = 870, K2 cannot bind for a configuration that passed G4 (0.2028 >
  0.1957); it can bind only if SR80_test at the realised T_test exceeds 0.2028, roughly T_test below 810 (870 x
  (0.1957/0.2028)^2, about 60 dates lost; MathReview N13). The fixed figures 0.97 / 1.94 / 3.74 ticks (and E.32b's 1.8) are
  reported beside it, not used.
- K3: if the sealed test fails, the ZL program closes and counts toward the stop rule.
- K4: no configuration enters inside a firm's news window or holds past the main session's end: by design (P1.3,
  P3.6 rules 2-3, P3.8; Topstep's news block does not name grains, M3 d.1).
- E.32b section 6: this is the last registered build of the directional program. If it fails its discovery gate or
  its sealed test, the directional program stops, and a restart needs a new information source the program has not
  used, not another product or family on the same bars and books.

### P10.3 Compute reference and stop (reports/stage_e34_briefs/P10_compute_ref.md; the protocol's own guess range)
No real-data probe was allowed in E.34 (it would compute features), and a synthetic-only probe is not used (E.33b D3).
The reference is E.33's measured fold times and build (reports/stage_e33c_briefs/ref_v03.json) scaled to this grid
(sets of 22, 23, 26 and 43 features; 1,200 fold fits; P_L = 8 LOGIT and P_G = 2 LGBM processes):
R_ZL = 7,965 s central (guess range 3,022-22,651 s). The search stops when its measured wall time exceeds
3 x R_ZL = 23,895 s, which covers the all-high case. If memory forces fewer processes, the run stage recomputes R_ZL
with the frozen formula of P10_compute_ref.md section 3 at the process counts it logs before the first real-outcome
fit, and the stop is 3 x that value. The run stage writes its own projection from its first measured folds to its
STATE file beside the reference; the reference does not move. There is no deadline in this protocol; a run-stage
prompt may set feasibility limits, and its cut unit is a whole set in P7.1's run order (S_pool, S_crush, S_book,
S_prop), with the rules of E.32 P10 (lines 839-858) after 0.4's substitutions (180 LOGIT and 120 LGBM fits a set).

### P10.4 Freeze list carried into the registration
The sha256 of: this protocol; reports/stage_e34_zl_methods.md; reports/stage_e34_data_facts.md;
reports/stage_e34_exposure.md; reports/stage_e34_briefs/L_lead_reconciliations.md;
reports/stage_e34_briefs/P10_compute_ref.md; the E.32 protocol (c4ffb9d7...) and E.33c's protocol_v0.3.diff;
reports/stage_e33_pipeline_freeze.sha256; the review files of reports/stage_e34_briefs/review/ (the two reviews, the
fix log, the fix verification and the v0.1 snapshot). They are listed in
reports/stage_e34_zl_protocol.sha256.

### P10.5 The null report
If Tier A is empty: as E.32 P10 (lines 859-865) with 200 configurations: the gate funnel; the 10 best configurations
by SR_d with every P6.2 statistic; the distribution of the 200 OOF daily Sharpes beside the synthetic null and SR0 at
N_reg; the discovery PBO; the minimum detectable net edge per trade at 80% power per horizon, by the formula and
measured (P7.2); per F09 family, the share of OOF dates on which it is invalid by construction (LT11); per family,
whether a null statement under docs/NULL_CRITERIA_E.md is supportable; and the sentence
"No candidate; the test window stays sealed; no test data purchase." N rises by 200 whatever the outcome.

## P11. Run-stage data plan

| use | schema | symbols | dates | status | cost (estimate, not a quote) |
|---|---|---|---|---|---|
| discovery, F10 and labels | mbp-1 | ZL.v.0 front | 2020-12-01..2024-02-29 | owned (E.31); read by E.31 and E.33 (V50 item 4) | 0 |
| discovery, F09 | ohlcv-1m | ZL.v.0, ZS.v.0, ZM.v.0 | 2020-12-01..2024-02-29 | owned, 39 files each | 0 |
| discovery, C.7 and limits | definition | ZL | 2020-12..2024-02 | owned (Z4) | 0 |
| test, F10 and labels | mbp-1 | ZL.v.0 | request 2017-05-21..2020-11-30 | sealed, never bought | USD 23.36 (0.5432 x 43) |
| test, C.7 and limits | definition | ZL | 2017-05-21..2020-11-30 | not owned | at most about USD 1.66 (P9.2); bought with the MBP-1 |
| test, F09 | ohlcv-1m | ZL and ZS 2017-04..2020-11; ZM 2019-05..2020-11 | to 2020-11-30 | owned inside the sealed soy files | 0 |
| test, F09 | ohlcv-1m | ZM.v.0 | 2017-05-01..2019-04-30 | not owned (ProtocolReview B1); bought with the test MBP-1, under the seal guard | about USD 1.46 (P9.2) |
| closed | any | ZL, ZS, ZM | 2024-03-01 onward | V51 item 2 | - |

Not bought: ZL MBO in either window (M1 4.4: route B would cost USD 40.96 in all, USD 17.60 more than route A; the
mixed route C needs an equivalence purchase first). The test purchase happens only after K1 and K2 pass, the user has
decided E.32b-D2, E.32b-D3, E.32-D2 and OC-5, a quote is logged, and the user approves the spend. Estimated test
purchase: about USD 26.5 (23.36 + 1.46 + at most 1.66); the quote decides.
