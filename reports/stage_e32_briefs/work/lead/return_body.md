# Stage E.32 return: ZM directional signal discovery, the methods brief and the frozen discovery protocol

Lead: Opus 5.5 (claude-opus-5-5), effort xhigh, Ultracode on. Launched 2026-10-26 22:21 PDT; this return written
2026-10-27 (times America/Vancouver, from `date`, file mtimes and transcripts). Prompt: docs/prompts/STAGE_E.32.md.

Frozen protocol: reports/stage_e32_discovery_protocol.md, FROZEN v1.0, sha256 {{FREEZE_SHA}}
(also in reports/stage_e32_discovery_protocol.sha256).

## 1. Summary

E.32 designed, and did not run, a ZM directional search. Nothing was trained; no feature, label, return or markout
was computed; N stays 538. The ZM, ZS and ZL window 2017-05-01..2020-11-30 is sealed (114 files, own unlock log,
0 unlocks).

Families (P2): four, each searched with a 15-feature context block, plus all pooled. F1 crush-residual reversion
(C = 11 ZL + 2.2 ZM - ZS, the one minutes-scale cross-asset structure in the literature); F2 ZS and ZL leading ZM
at 1-15 minutes; F3 ZM order flow and book state from MBO; F4 ZM's own path (momentum, reversal, burst aftermath,
gap). USDA drift, NOPA days, the overnight handoff and liquidity regimes fail on power (about 40-49 events in 39
months) and survive as exclusions, flags and context features.

Budget: 5 feature sets x 6 executable labels (5, 15, 30, 60 minutes; triple barrier at 15 and 30) x 10 grid points
(6 regularised logistic, 4 shallow LightGBM) = 300 configurations. N after E.33 = 838.

Minimum edge: G2 needs 0.50 tick net per trade (Topstep market orders); the binding gate needs a discovery daily
Sharpe of 0.2007 (t 5.66), about 1.22 ticks net per 15-minute trade at 4 trades a day, or 0.50 per 5-minute trade
at 8.

Test power: ZM MBO starts 2017-05-21, so the test is 2017-05-22..2020-11-30, 870 dates after burn-in. Its bar
(daily Sharpe 0.1649) has 80% power at a true 0.1936; a configuration with a true 0.25 in both windows is selected
and passes with probability 0.91 (0.42 at 0.20). Under the program verdict as coded these are upper bounds
(decision D2).

Honest odds: about 5% that E.33 produces a finalist and about 3% (range 1-6%) that this route ends with a passing
candidate. No published study shows net out-of-sample directional predictability at these horizons in a
commodity future.

## 2. Guardrail evidence

{{GUARDRAILS}}

## 3. Results

### 3.1 Deliverables
{{DELIVERABLES}}

### 3.2 Part 0: the test seal (reports/stage_e32_test_seal.md)
- 114 files sealed (117.6 MB) at 22:54:51-22:55:11 PDT on 2026-10-26: 107 raw ohlcv-1m chunks (ZS and ZL
  2017-04..2020-11, ZM 2019-05..2020-11), the step2 ZM/ZS/ZL stores, the ext2010h ZS/ZL stores and the E.22
  microbook caches. Sealed store data/sealed/SOY_test_v1 (large storage); manifest docs/soy_test/SOY_TEST_MANIFEST.json;
  own unlock log docs/SOY_TEST_UNLOCK_LOG.md and phrase; tool reports/stage_e32_briefs/seal/soy_test_seal.py with
  tests/test_e32_soy_test_seal.py (26 tests). data.holdout status identical before and after
  (reports/stage_e32_briefs/seal/holdout_status_{before,after}.json).
- Earlier exposure (seal document section 4, from X1 as re-verified by X1Verifier): bar-level trend, seasonal and
  ML work on 1-minute bars (E.12, E.14, E.17, E.20, E.21, E.22, E.25), never order-book features. 206 derived
  files (95 git-tracked reports, 111 ~/.cache ML caches) are listed with sha256 and not sealed; the protocol's data
  allowlist refuses them.
- 2024-03 onward stays closed.

### 3.3 Part F: data facts (reports/stage_e32_data_facts.md)
156 owned files (ZM MBO, ZS and ZL MBP-1, definitions; 2020-12..2024-02), 1,107,120,522 records, 24.23 GB
compressed, 72.59 GB decompressed; all hashes match the manifest (156 of 156). ts_recv - ts_event is 0.1-10 ms for
about 96% of records, and ts_recv < ts_event for 0.14-0.16%. 816 trade dates in every file. Volume-ranked symbols
flip near rolls (ZM.v.0 24 runs), so the protocol pins the front mapping. Book rebuild 0.39-0.76 M records/s per
process (9-18 minutes for 39 months of ZM). Missing code that E.33 must write: a ZS/ZL split keeping sizes and
trades, the event-time sampler, the label builder, purged CV and the soy-seal read guard. Databento's GLBX.MDP3
page (saved by Part F) shows ZM MBO starts 2017-05-21; before that only MBP-10 and ts_recv = ts_event.

### 3.4 Parts R and M: the methods brief (reports/stage_e32_methods_brief.md)
Twelve reader files (R1, R2, R3a, R3b, R4, R5; M1, M2, M3, M4, M5a, M5b, M6) and the exposure inventory X1, all
corrected by the MathReviewer rulings (bracketed notes; nothing deleted). The front's findings:
1. The published evidence is thin and mostly negative at horizons that can pay ZM's costs: CBOT meal's
   first-half-hour momentum is null over 1982-2020 (Baltussen et al., slope -0.95, t -1.58); order-flow
   predictability fades within about 30 minutes; no commodity-futures study shows net out-of-sample predictability
   at 1-240 minutes (R4, R5, M1).
2. Costs: a market round trip costs about one spread plus the fee (Topstep 0.528 ticks); E.28's break-even 1.59
   ticks is a cycle-EV threshold; limit entries are not cheaper once E.31's adverse markout counts (trade-through
   +0.79 tick, queue model +0.03-0.07); labels must be executable (mid labels are about 1 tick a round trip
   optimistic) (M3, M6).
3. Statistics: at N 838 the deflated Sharpe on 796 discovery dates needs a daily Sharpe of 0.172 (t 4.86); a
   15-minute forecast traded 4 times a day needs an out-of-sample rho of about 0.13 for 1.2 ticks net (M5a, M5b,
   R5).
4. Structure: the board crush is cointegrated in most day sessions, but ZM must close about 70% of a 1-cent
   dislocation to pay costs and is not the default adjusting leg; seconds-scale lead-lag cannot pay at retail
   latency; order flow is a conditioner; event and once-a-day families fail on power (M2, R3a, M1, R4).
5. Methods: regularised logistic first, shallow trees second, no deep order-book models; purged, embargoed,
   session-aligned folds; DSR at the literal N; PBO reported, not gated; stability and power gates (M4, M5a, M5b).
6. Practice (R1, R2): ideas screened for sense, prediction, consistency and additivity; a small declared number of
   variants; trial ledgers; merchants' hedging flows are private and untimed; HFT edge in soybeans is spread capture
   (closed by V50).
7. Regimes: the discovery and test windows straddle the renewable-diesel change in the oil share, the 2020
   liquidity collapse and the 2021-2022 position-limit change (R3a, R3b).

### 3.5 Part P: the frozen protocol (reports/stage_e32_discovery_protocol.md, v1.0)
- P1: the 156 hashed files (manifest 09396842...); day session 08:35-13:13 CT searched; overnight records enter
  features only; roll dates, the date after a roll, early closes and late opens excluded; a data allowlist with a
  guard test per refused path; E.31's prior exposure named and firewalled (no E.31 statistic sets a sign,
  threshold, look-back or weight; E.31 outputs refused to E.33's code and closed to its workers).
- P2: families F1-F4 and the context block C, with mechanisms, evidence and overlap with the 538 trials and E.31.
- P3: 6 executable labels, net of the 0.528-tick fee and the spread (dead zone = spread + costs); the EV trade rule
  with class-conditional training means; exclusion rules (open, close, USDA/NOPA releases -2..+30 min with a parse
  rule and asserted counts, rolls, locked books, price limits); uniqueness weights; one position at a time, at most
  20 entries a date; the P3.2 fallback fills.
- P4: 59 features with exact formulas (C 15, F1 8, F2 11, F3 12, F4 13), point-in-time on the ts_recv clock; LT1-LT7
  leakage and pipeline tests; synthetic proofs (20 null and 20 planted subset searches, 4,800 fits; pass and fail
  rules declared).
- P5: LOGIT (6 grid points) and LGBM (4), pinned libraries and seeds, thread cap 8, failed and interrupted fits
  defined, compute estimate and a probe-based 3x stop.
- P6: 6 blocked folds of the 796 OOF dates with a 21-date embargo; the selection metric on Topstep market orders
  at L = 1 s; PBO reported; execution variants per firm (market, trade-through limit, queue-model limit) and
  diagnostics after the test list is hashed, never selecting.
- P7: 300 configurations under one registration (IDs E33-<set><label><grid>), N 838, thresholds at that N.
- P8: gates G1 activity, G2 0.50 tick net, G3 DSR, G4 power, G5 stability; a total-order ranking; Tier A at most 3
  with pairwise correlation <= 0.70; Tier B 2 for the test verdict's variance; the 6-fold ensemble frozen.
- P9: the test sketch (2017-05-22..2020-11-30; quote only after a funded account; one read; the program verdict
  plus the protocol-added DSR; a reserved user decision on V14 c).
- P10: integrity and feasibility stops only; deadlines and the cut order; the null report.

### 3.6 Thresholds (P7.2, p7_final.py, N 838)
| Quantity | Value |
|---|---|
| T_disc / T_test | 796 / 870 trade dates (20-date burn-in each) |
| SR0 = E[max SR] at discovery | 0.1137 daily |
| G3: DSR > 0.95 at discovery | SR_d >= 0.1724 (t 4.86) |
| Test bar b_test (protocol-added DSR at V = 1/(T_test - 1)) | 0.1649 daily (unrounded 0.164882; t 4.86) |
| Test t > 3.0 alone | 0.1017 daily |
| G4 (binding): SR_d - se >= b_test | SR_d >= 0.2007 (t 5.66) |
| Net per trade at the binding threshold | 0.71 ticks at 5 min x 4 a date (0.50 at 8); 1.22 at 15 min x 4 (0.87 at 8); 1.73 at 30 min x 4; 3.46 at 60 min x 2 |
| Test 80% power | true daily Sharpe 0.1936 over 870 dates |
| Select-and-pass probability | 0.03 at true 0.15, 0.11 at 0.17, 0.42 at 0.20, 0.91 at 0.25 |
| If the added test DSR is dropped (D1) | b_test 0.1017, G4 0.1373, binding threshold 0.1724 (G3) |

## 4. Delegation record

Every model below is read from the agent's own transcript (message.model), never a self-report (V50 item 5). One
worker ran on Sonnet (X1, before the user's 23:15 never-Sonnet rule reached the run); its output was re-verified on
Opus. All Fable reviewers ran on claude-fable-5-1; no Fable fallback was needed.

{{DELEGATION}}

## 5. Verification

{{VERIFICATION}}

## 6. Open choices

{{OPEN_CHOICES}}

## 7. Decisions for the user (each with a recommendation)

{{DECISIONS}}

## 8. Session cost

{{COST}}
