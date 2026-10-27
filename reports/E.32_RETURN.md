# Stage E.32 return: ZM directional signal discovery, the methods brief and the frozen discovery protocol

Lead: Opus 5.5 (claude-opus-5-5), effort xhigh, Ultracode on. Launched 2026-10-26 22:21 PDT; this return written
2026-10-27 (times America/Vancouver, from `date`, file mtimes and transcripts). Prompt: docs/prompts/STAGE_E.32.md.

Frozen protocol: reports/stage_e32_discovery_protocol.md, FROZEN v1.0, sha256 c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05
(also in reports/stage_e32_discovery_protocol.sha256).

## 1. Summary

E.32 designed, and did not run, a ZM directional search. Nothing was trained; no feature, label, return or markout
was computed; N stays 538. The ZM, ZS and ZL window 2017-05-01..2020-11-30 is sealed (114 files, own unlock log,
0 unlocks).

Families (P2): four, each searched with a 15-feature context block, plus all pooled. F1 crush-residual reversion
(C = 11 ZL + 2.2 ZM - ZS); F2 ZS and ZL leading ZM
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

Start checks (reports/stage_e32_briefs/checks_start.txt, 2026-10-26 22:41:26 PDT):

```
$ git status --short | wc -l
1457
$ git log --oneline -3
baf24eb docs: V51 (ZM directional signal program) and the Stage E.32 prompt
a6e5582 docs: V50 (E.31 accepted: passive spread capture closed; acct-3 safe to wipe; reviewer model check)
97ce7f0 Stage E.31 volume check and ZM pilot
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
37290 ledger/databento_spend.jsonl
42589d7bc02696383cbf5d800ceb922491a4dea90fb2c3d3e2f82da36834c9bb
$ uv run python -m screening.trial_registry status (N)
r008-E23: E23 [...] N 533 -> 538 at 2026-10-17T03:33:45-07:00
.env DATABENTO_API_KEY: absent
.env DATABENTO_API_KEY2: absent
.env DATABENTO_API_KEY3: non-empty
```
(The git status list itself, 1,457 untracked lines, is in the start file. Keys were checked by name only.)

Holdout before and after Part 0 (the seal): reports/stage_e32_briefs/seal/holdout_status_before.json and _after.json
are identical; the soy test seal's own status before and after is in soy_status_before.json and soy_status_after.json
(after: all_ok, unlocks 0). Session checks: 02:32 PDT and 07:31 PDT, data.holdout state sealed, unlocks_logged 0.

End checks (reports/stage_e32_briefs/checks_end.txt, 2026-10-27 13:08:23 PDT; the 1,470 untracked paths of `git status --short` are in the file and are omitted here, with the registry lines before r008):

```
$ date
Tue Oct 27 13:08:23 PDT 2026
$ git status --short
$ git status --short | wc -l
1470
$ git log --oneline -3
3a75f3b docs: Stage E.33 hard deadline 09:00 PDT Wed 2026-10-28
864574b docs: Stage E.33 timing (no fixed end; continues across the weekly reset)
aadf4f9 docs: Stage E.35 prompt (passive venue screen outside prop firms)
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ uv run python reports/stage_e32_briefs/seal/soy_test_seal.py status (keys)
soy test {'state': 'sealed', 'files_sealed': 114, 'files_ok': 114, 'plaintext_in_window_present': [], 'unlocks_logged': 0, 'all_ok': True}
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m screening.harness_freeze verify --expected 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
preflight OK: 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
$ ledger
37290 ledger/databento_spend.jsonl
42589d7bc02696383cbf5d800ceb922491a4dea90fb2c3d3e2f82da36834c9bb
$ ledger total per account (SpendGate.account_spent_usd)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 353.455228 cap 355.38 headroom 1.924772
acct-3: spent 122.370573 cap 125.00 headroom 2.629427
$ uv run python -m screening.trial_registry status (N)
r008-E23: E23 ['E23-MEZFh5', 'E23-MEZNh5', 'E23-MEZBh5', 'E23-H6NQh5', 'E23-H6NQh20'] N 533 -> 538 at 2026-10-17T03:33:45-07:00
.env DATABENTO_API_KEY: absent
.env DATABENTO_API_KEY2: absent
.env DATABENTO_API_KEY3: non-empty
```

No tracked file changed during the stage (`git status --short | grep -vc '^??'` = 0 at 12:35 and at the end). N stays 538, the spend ledger is unchanged (37,290 lines, sha256 42589d7b...), REGISTRATION.md is 0 bytes, harness v14 2e908c81... verifies, and no Databento or TopstepX call was made. Session checks: data.holdout unlocks_logged 0 at 02:32, 07:31, 08:39 and 12:35 PDT and at the end. Full pytest (2 GB rule met: 10.2 GB available at launch): 8,116 passed, 1 failed (predates E.32; D7), 5 skipped, 3 xfailed, 1,175.65 s (reports/stage_e32_briefs/pytest_end.log). No worker, workflow or shell is running at the end (checked before the commit).

## 3. Results

### 3.1 Deliverables
| File | Bytes | sha256 |
|---|---|---|
| reports/stage_e32_methods_brief.md | 890,514 | 142f3afc4bc0dc6b8900730dcddf69ca69b907755570025ad51187d7105301a6 |
| reports/stage_e32_test_seal.md | 44,152 | e599a29e2391eae7b169c853953b9dd0d1247bfb8fcd4e43c0f23fc6d443a8af |
| reports/stage_e32_data_facts.md | 51,409 | b4c61cc58c7335d529b1a5fc01faf6e50e33701841b04858adfa4bb8fe5ad6c0 |
| reports/stage_e32_discovery_protocol.md | 78,119 | c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05 |
| reports/stage_e32_discovery_protocol.sha256 | 106 | 2577fc5f950eb58f10b310c9d6c8c4ed137b9cb03aa77373c42eac74b69be62b |
| docs/soy_test/SOY_TEST_MANIFEST.json | 90,482 | 673fde8a98e50397e994f08aeb335d027d7e24a6c1617d7bfadc69b2016c6c88 |
| docs/SOY_TEST_UNLOCK_LOG.md | 68,113 | c4c58c672beda08a476dbd1ac7acb1aace0d836ffe387aa3819ad0a1b69c9da2 |
| tests/test_e32_soy_test_seal.py | 9,371 | 51cb095784c0241bb2927d3b87ff7a3650c2415eaf7f342c2549928f59a0bacc |
| reports/stage_e32_briefs/seal/soy_test_seal.py | 24,912 | 06a34fea5147b40d85990f0ab44d4fbfc27f11dec712530bd564f43a68c42ac4 |
| reports/stage_e32_briefs/protocol/p7_final.py | 7,574 | 3db06f1276bf949529cb8b0d5f3e07c3d155db13fdb819666a7c51377385e828 |
| reports/stage_e32_briefs/protocol/p7_final_budget300.md | 3,159 | 88269842b9b5702288e65ca6c0a8959f6788b4ca9451035eb3eb3540cadb6536 |

Also: this return; one progress.md entry; one docs/STAGES.md line; the reader, review, seal and work files under reports/stage_e32_briefs/ (the raw fetched source pages under pages/ stay on disk, uncommitted, as in E.28 and E.31; their logs are committed). The methods brief is the front, Parts R and M (the reader files as corrected) and Part V (verification).

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
Thirteen reader files (R1, R2, R3a, R3b, R4, R5; M1, M2, M3, M4, M5a, M5b, M6) and the exposure inventory X1, all
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

| # | Agent | Session / run | Agent file | Model (transcript) | Effort | Start PDT | End PDT | Minutes | Tokens |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ValidationMath-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-26 23:03 | 10-26 23:13 | 10 | 10,800,750 |
| 2 | LeadLagMath-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-26 23:03 | 10-26 23:15 | 12 | 14,919,332 |
| 3 | CrushEconomics-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-26 23:03 | 10-26 23:16 | 13 | 14,081,770 |
| 4 | EventStructure-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-26 23:03 | 10-26 23:16 | 13 | 12,607,561 |
| 5 | OrderFlowMath-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-26 23:03 | 10-26 23:15 | 12 | 17,711,143 |
| 6 | FableProbe-FableXHigh | a51871c6 agent | worker-xhigh | claude-fable-5-1 | xhigh | 10-26 23:03 | 10-26 23:03 | 0 | 63,019 |
| 7 | ExposureInventory-SonnetMed | a51871c6 wf_2ed35392-831 | worker-medium | claude-sonnet-5-5 | medium | 10-26 23:03 | 10-26 23:14 | 11 | 16,501,113 |
| 8 | LabelsMath-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-26 23:14 | 10-26 23:15 | 1 | 1,451,306 |
| 9 | ValidationMath-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-27 00:16 | 10-27 00:32 | 16 | 12,877,539 |
| 10 | LeadLagMath-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-27 00:16 | 10-27 00:28 | 12 | 9,060,031 |
| 11 | CrushEconomics-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-27 00:16 | 10-27 00:23 | 7 | 5,292,706 |
| 12 | OrderFlowMath-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-27 00:16 | 10-27 00:29 | 13 | 13,300,400 |
| 13 | X1Verifier-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-27 00:16 | 10-27 00:29 | 13 | 24,233,595 |
| 14 | EventStructure-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-27 00:16 | 10-27 00:30 | 14 | 17,687,636 |
| 15 | LabelsMath-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-27 00:23 | 10-27 00:39 | 16 | 16,865,073 |
| 16 | PowerStability-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-27 00:29 | 10-27 00:44 | 16 | 11,970,110 |
| 17 | DataFacts-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-27 00:29 | 10-27 00:46 | 17 | 13,560,264 |
| 18 | PropStrategyMath-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-27 00:29 | 10-27 00:50 | 21 | 14,633,090 |
| 19 | ModelsMath-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-27 00:30 | 10-27 00:51 | 21 | 14,327,082 |
| 20 | SoyMicrostructure-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-27 00:32 | 10-27 00:49 | 17 | 25,547,321 |
| 21 | AgDesks-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-27 00:39 | 10-27 00:51 | 12 | 14,158,856 |
| 22 | AlphaProcess-OpusHigh | a51871c6 wf_2ed35392-831 | worker-high | claude-opus-5-5 | high | 10-27 00:44 | 10-27 00:51 | 7 | 6,676,053 |
| 23 | MLEvidence-OpusHigh | a51871c6 agent | worker-high | claude-opus-5-5 | high | 10-27 00:46 | 10-27 00:50 | 3 | 3,081,497 |
| 24 | MathReviewerC-FableXHigh | a51871c6 agent | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 00:50 | 10-27 00:51 | 1 | 1,444,111 |
| 25 | MLEvidence-OpusHigh | 900dd54a agent | worker-high | claude-opus-5-5 | high | 10-27 02:33 | 10-27 02:48 | 15 | 13,425,372 |
| 26 | MathReviewerC-FableXHigh | 900dd54a agent | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 02:33 | 10-27 02:51 | 17 | 2,980,789 |
| 27 | PropStrategyMath-OpusHigh | 900dd54a wf_df544c98-716 | worker-high | claude-opus-5-5 | high | 10-27 02:33 | 10-27 02:45 | 11 | 7,888,116 |
| 28 | AgDesks-OpusHigh | 900dd54a wf_df544c98-716 | worker-high | claude-opus-5-5 | high | 10-27 02:34 | 10-27 02:42 | 9 | 7,915,557 |
| 29 | AlphaProcess-OpusHigh | 900dd54a wf_df544c98-716 | worker-high | claude-opus-5-5 | high | 10-27 02:34 | 10-27 02:51 | 18 | 18,736,590 |
| 30 | MathReviewerA-FableXHigh | 900dd54a agent | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 02:34 | 10-27 02:53 | 19 | 2,174,991 |
| 31 | MathReviewerB-FableXHigh | 900dd54a agent | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 02:43 | 10-27 03:03 | 20 | 8,255,017 |
| 32 | MathReviewerD-FableXHigh | 900dd54a agent | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 02:46 | 10-27 03:11 | 24 | 7,412,718 |
| 33 | LeakageReviewer-FableXHigh | 900dd54a wf_3d631049-c34 | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 03:05 | 10-27 03:11 | 6 | 2,932,000 |
| 34 | ArithmeticReviewer-FableXHigh | 900dd54a wf_3d631049-c34 | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 03:05 | 10-27 03:11 | 6 | 1,605,800 |
| 35 | FeasibilityReviewer-FableXHigh | 900dd54a wf_3d631049-c34 | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 03:05 | 10-27 03:11 | 6 | 3,484,948 |
| 36 | DofReviewer-FableXHigh | 900dd54a wf_3d631049-c34 | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 03:05 | 10-27 03:07 | 2 | 1,707,444 |
| 37 | FixApplier-OpusHigh | 900dd54a agent | worker-high | claude-opus-5-5 | high | 10-27 03:11 | 10-27 03:11 | 0 | 220,726 |
| 38 | LeakageReviewer-FableXHigh | 900dd54a wf_30d7118e-f81 | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 07:32 | 10-27 07:53 | 21 | 8,536,712 |
| 39 | FixApplier-OpusHigh | 900dd54a agent | worker-high | claude-opus-5-5 | high | 10-27 07:32 | 10-27 07:38 | 6 | 4,978,898 |
| 40 | DofReviewer-FableXHigh | 900dd54a wf_30d7118e-f81 | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 07:32 | 10-27 07:57 | 24 | 9,806,052 |
| 41 | ArithmeticReviewer-FableXHigh | 900dd54a wf_30d7118e-f81 | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 07:32 | 10-27 07:52 | 19 | 3,907,769 |
| 42 | FeasibilityReviewer-FableXHigh | 900dd54a wf_30d7118e-f81 | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 07:32 | 10-27 07:55 | 22 | 3,088,124 |
| 43 | FixVerifierLeakArith-FableXHigh | 89bc0cd0 wf_6418603c-1ef | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 08:42 | 10-27 08:56 | 14 | 5,415,437 |
| 44 | FixVerifierFeas-FableXHigh | 89bc0cd0 wf_6418603c-1ef | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 08:42 | 10-27 08:52 | 10 | 1,275,543 |
| 45 | FixVerifierDofA-FableXHigh | 89bc0cd0 wf_6418603c-1ef | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 08:42 | 10-27 08:50 | 8 | 2,784,627 |
| 46 | FixVerifierDofB-FableXHigh | 89bc0cd0 wf_6418603c-1ef | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 08:42 | 10-27 08:54 | 12 | 1,528,664 |
| 47 | FixSpotCheckB-FableXHigh | 89bc0cd0 wf_22487789-c6a | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 12:42 | 10-27 12:56 | 14 | 4,445,077 |
| 48 | FixSpotCheckA-FableXHigh | 89bc0cd0 wf_22487789-c6a | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 12:42 | 10-27 12:52 | 10 | 3,770,126 |
| 49 | FinalDiffCheck-FableXHigh | 89bc0cd0 agent | worker-xhigh | claude-fable-5-1 | xhigh | 10-27 12:58 | 10-27 13:06 | 8 | 1,447,590 |
| | all workers | | | | | | | | 422,576,045 |

Lead sessions (Opus 5.5 xhigh, claude-opus-5-5 in every transcript): a51871c6-ae95-4aa9-8b23-0daf24b41dc1 (2026-10-26 22:21 to 2026-10-27 00:51), 900dd54a-de4d-4012-a455-b0efd91bbcf0 (02:32 to 08:02), 89bc0cd0-ddc5-469d-b633-94a1a978350a (08:39 to the end). Rows 1-49 are every worker transcript with usage in the window, re-spawns included (a worker stopped by a usage limit and re-spawned appears twice). Routing: readers and extraction on Opus high (X1 alone on Sonnet medium, before the rule), all reviews and checks on Fable xhigh; nothing ran on Haiku; no worker spawned another worker. Effort is fixed by the agent file (worker-high = high, worker-xhigh = xhigh, worker-medium = medium).

## 5. Verification

Every reviewer ran in a fresh context on a different model from the author (authors: Opus 5.5; reviewers: Fable
5.1), and each model is confirmed from its own transcript (section 4).

| Check | Object | Reviewer(s) | Result |
|---|---|---|---|
| MathReviewer A | M2, R3a arithmetic | MathReviewerA-FableXHigh | 0 BLOCKING, 5 SHOULD FIX, 11 NOTE; 118 M2 and 71 R3a numbers recomputed, all agree |
| MathReviewer B | M1, M3 | MathReviewerB-FableXHigh | 0 / 5 / 14; every worked example recomputed; 127 quote segments found in saved pages |
| MathReviewer C | M5a, M5b, p7_thresholds.py | MathReviewerC-FableXHigh | 1 (C-10: power table used z 2.128 while the bar was DSR at N) / 7 / 8; about 450 closed-form numbers; 905 test dates confirmed |
| MathReviewer D | M4, M6, R5 (b) | MathReviewerD-FableXHigh | 0 / 7 / 12; M6's payout funnel reproduced cell by cell |
| X1 re-verification | X1_exposure.md (a Sonnet worker's) | X1Verifier-OpusHigh | 311 rows: 303 confirmed, 8 corrected, 0 unsourced; 4 missing rows added |
| ProtocolReviewer (4 lenses) | protocol v0.2 | Leakage, Dof, Arithmetic, Feasibility -FableXHigh | 6 BLOCKING, 39 SHOULD FIX, 44 NOTE; 122 numbers reproduced, p7_final.py re-run byte-identical |
| FixVerifier (4 workers) | v0.3 against the 45 items | FixVerifierLeakArith, DofA, DofB, Feas -FableXHigh | 29 CORRECT, 14 PARTIAL, 2 WRONG; 0 new BLOCKING, 17 SHOULD FIX, 25 NOTE |
| FixSpotCheck (2 workers) | the v0.3 to v0.4 diff (37 hunks) | FixSpotCheckA, FixSpotCheckB -FableXHigh | 32 CORRECT, 2 UNTAGGED-OK, 2 PARTIAL, 1 WRONG (one number); 0 BLOCKING, 4 SHOULD FIX, 12 NOTE; 0 findings uncovered |
| FinalDiffCheck | the v0.4 to v0.5 diff (15 hunks) | FinalDiffCheck-FableXHigh | 11 CORRECT, 2 PARTIAL, 2 UNTAGGED-OK, 0 WRONG; 0 BLOCKING, 3 SHOULD FIX, 5 NOTE, all applied with the checker's texts (v0.6); frozen v1.0 |

Rulings: every BLOCKING and SHOULD FIX item at every round was accepted and applied before the freeze; NOTE items of
the re-check rounds (FixVerifier, FixSpotCheck, FinalDiffCheck) were applied too; ProtocolReviewer NOTEs were
applied only where the lead chose (others, such as AR-15's sign, came back through the re-check) and MathReviewer
NOTEs were not (all are listed in the review files). Where a
reviewer left options open, the lead's choice is logged in reports/stage_e32_STATE.md and in section 6. Files:
reports/stage_e32_briefs/review/ (MathReview_A..D.md, ProtocolReview_*.md, fix_log.md) and review/recheck/
(Recheck_W1..W4.md, SpotCheck_A.md, SpotCheck_B.md, FinalDiffCheck.md).

Numbers entering the verdict thresholds: p7_final.py's outputs (N 838, T_disc 796, T_test 870, G3 0.1724, b_test
0.164882, G4 0.2007, drop branch 0.1017 / 0.1373 / 0.1724) were reproduced by ArithmeticReviewer, FixVerifier W1
and FixSpotCheck B independently. No trading verdict number exists in E.32 (nothing was run).

Tests: tests/test_e32_soy_test_seal.py 26 passed (Part 0); the store-test subset before and after the seal (1,840
passed 1 skipped; 1,866 passed 1 skipped); the full suite at 09:01 PDT: 8,116 passed, 1 failed, 5 skipped, 3
xfailed in 1,175.65 s (reports/stage_e32_briefs/pytest_end.log). The one failure,
tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha, predates E.32: it fails
identically at HEAD 3a75f3b in a clean worktree (reports/stage_e32_briefs/h6_single.log; decision D7).

Process gaps (stated, not hidden; methods brief Part V.5): 18 cftc.gov reference fetches before the terms check
(terms allow reference use); M2's 9 failed fetches without the Scrapling fallback; R2's FAS page not retried;
abstract-only sources marked [unverified]; M5b's Lo (2002) copy from a host of unknown authorisation; X1 ran on
Sonnet before the never-Sonnet rule and printed one E.17 pooled daily series to its context; the first session's
workflow journal could not be resumed (byte-identical continuation script); three usage limits and one planned
context wipe (section 8).

## 6. Open choices

Part 0 (seal)
1. Whole files are sealed: stores that span the window boundary are sealed whole; no script reads in-window rows to
   split them.
2. Window rule: raw files by UTC span [2017-04-30T21:00Z, 2020-11-30T22:00Z) (the pre-open hours of 2017-05-01 pull
   in the April 2017 ZS/ZL chunks); stores by inclusive trade dates.
3. The soy seal has its own unlock log and phrase (docs/SOY_TEST_UNLOCK_LOG.md), so a soy unlock never counts as
   holdout 1's.
4. rolls/ symbology JSONs (date to instrument id, no prices) are not sealed; named in the seal document.
5. 206 derived files (95 git-tracked reports, 111 ~/.cache ML caches; seal/derived_unsealed_files.tsv) are not
   sealed: git history keeps the tracked ones readable and both are audit state of registered trials; the guard is
   the protocol's data allowlist (P1.2).
6. The seal stays on 2017-05-01..2020-11-30 although MBO exists only from 2017-05-21: sealing three extra weeks costs
   nothing; the protocol tests 2017-05-22..2020-11-30.
Parts R, M, F (workers)
7. R3 split into R3a (economics) and R3b (microstructure), M5 into M5a (validation) and M5b (power, stability), and
   a follow-up reader R5 (ML evidence and the honest odds): 3 of the prompt's 4 follow-up slots.
8. X1 (the exposure inventory) ran on Sonnet medium before the user's never-Sonnet rule reached the run; it was
   re-verified row by row by X1Verifier-OpusHigh inside the workflow pool (to hold concurrency at 6), and the seal
   document's section 4 was corrected from that verification.
9. The first session's workflow journal could not be resumed in the new session; the three unfinished readers ran
   from a continuation script whose item prompts are byte-identical to the original's.
10. MathReviewer fixes are bracketed notes in the reader files; no reader text was deleted (E.28's practice).
11. The cftc.gov terms check came after 18 reference fetches by R3a, R3b and R4 (the terms allow reference use);
    stated in Part V.5, not hidden.
Part P (protocol)
12. Test bar: the program verdict as coded plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (an
    addition, never a relaxation; dropping it is decision D1 in section 7).
13. Effective test span 2017-05-22..2020-11-30 (890 dates), a 20-date feature burn-in in both windows (T_disc 796,
    T_test 870).
14. The overnight session: no labels or trades in E.33; overnight records enter features only.
15. Four idea families plus a context block; post-USDA drift, the overnight handoff, liquidity regimes, index rolls,
    COT and late-session momentum are not families (power or evidence); their signals survive as exclusions, flags
    or features.
16. Five feature sets (each family with C, and all pooled) x 6 executable labels x 10 grid points = 300.
17. Two model families (regularised logistic primary, LightGBM depth <= 3 secondary); the online wrapper (M4 d
    "maybe") is dropped to keep the grid small and the CV analogue exact.
18. The trade rule is the EV rule with class-conditional training means (no tuned probability threshold).
19. Selection on Topstep market orders, L = 1.0 s; other firms, limit variants and L = 0.3 s are reported for the
    finalists only; a finalist is meant for Topstep (lowest ZM fee, API automation admitted).
20. The program runner's 20-entries-a-date cap is adopted; its 10-minute mean-holding floor is not.
21. Embargo of 21 dates after each evaluation block only (labels end inside their session; features use the past;
    21 covers the 20-date SDs of F1.7 and F4.7, which reach the 13:15 mid of the 21st date back; ProtocolReview
    LE-4, AR-5).
22. The power gate uses the one-standard-error lower bound of the discovery Sharpe against the binding test bar,
    at power 0.5.
23. Tier B (for the program verdict's variance and PBO when Tier A has one member) is the next two configurations
    of the Tier A walk with correlation <= 0.70 to every one taken, gates ignored; failed or constant series are
    skipped (ProtocolReview DO-5, FixVerifier R-W2-1).
24. The model taken to the test is the 6-fold ensemble (no refit, no new hyperparameter).
25. The release calendar is E.31's sourced CSVs (hashed); a NOPA month without a row gets its rule date.
26. Queue-imbalance features use seasoned depth (orders resting at least 1 s), as a spoofing guard (R2).
27. All thresholds use the literal N = trial_registry.current_n() right after E.33's one registration of the 300
    IDs (838 if no other stage registers first), recomputed by p7_final.py at that N (ProtocolReview DO-4, AR-3).
Part P after the ProtocolReviewer (v0.3) and the FixVerifier re-check (v0.4)
28. Entry decisions use only data with ts_recv <= t; the locked-book rule is a row rule; an entry or exit whose side
    is empty at t + L fills at the first later valid book update (the P3.2 fallback), and a TB trade's barrier
    reference is the mid at that fill update (ProtocolReview LE-1, FixVerifier R-W1-2).
29. Definitions (limit prices) are taken as of ts_recv <= 08:30 CT on D; a missing or undefined limit skips the
    limit rule for that date (ProtocolReview LE-2, FE-8; FixVerifier R-W4-8, R-W1-11).
30. The release calendar is parsed by a fixed rule with asserted counts (39 WASDE, 39 Crop Production, 4 Annual, 13
    Grain Stocks, 3 Prospective Plantings, 3 Acreage, 37 NOPA rows plus 2 rule dates); a NOPA month without a row
    gets its rule date (ProtocolReview LE-3, DO-8; FixVerifier R-W1-5). (Replaces 25's wording.)
31. Conservative readings by E.33 go into reports/stage_e33_protocol_readings.md, hashed in the pipeline freeze and
    quoted in the C1 note; none after C1 (ProtocolReview DO-1, FixVerifier R-W2-2).
32. Registry IDs E33-<set><label><grid> (e.g. E33-S5F15L010A) to match trial_registry's pattern; one register call
    (ProtocolReview DO-3, FE-1).
33. Synthetic proofs at a declared subset scale (S5 x {FH15, TB30} x 10 grid points, 20 null and 20 planted seeds,
    4,800 fits) instead of 40 full searches (72,000 fits); the plant is sized at FH15 by the P3.5 oracle with true
    class probabilities (ProtocolReview FE-2, FE-7, DO-21; FixVerifier R-W3-4, lead's choice of FH15).
34. LT7 (simulator causality) runs on the fold models of the seed-1 null proof search, applied to the real streams
    before any real-outcome fit, and again on Tier A and Tier B after the test list is hashed (FixVerifier R-W3-6,
    lead's choice).
35. An interrupted fold is rerun once from the DONE markers; a second interruption fails the configuration
    (FixVerifier R-W3-7, lead's choice over failing at once).
36. Threads: processes x threads <= 8; every long job at nice 10 and resumable (ProtocolReview FE-3, FixVerifier
    R-W4-3, R-W4-4).
37. No package is added after the pipeline freeze; anything needing statsmodels is written in numpy with tests or
    reported as not done; SFI only if time remains (ProtocolReview FE-6).
38. E.33's deadlines are quoted by value from its prompt as amended at 08:16 (search cut 07:00 PDT 2026-10-28, work
    stop 08:00, return 08:45, nothing after 09:00); the prompt's current times govern; the cut unit is a whole
    feature set and the report cut order is declared (ProtocolReview DO-19, FE-11; FixVerifier R-W3-1, R-W4-1).
39. G3 and the protocol-added test DSR use the program's sign "> 0.95"; b_test is the unrounded 0.164882; ranking
    rounds SR_d with Python's round() (FixVerifier R-W1-12, R-W1-4, R-W2-4).
40. The P6.4 (iii) queue-model variant uses a port of E.31's fill logic written by E.33 (F 6.2 classes E.31's code
    as not reusable), reported as not done if not ready; P6.3-P6.5 items are never a stop (FixVerifier FE-6,
    R-W4-2).
41. E.31's measured outputs (pilot/runs/, incl. runs/measure31/) are refused in code; X1_exposure.md, X1_verify.md
    and the Table C appendix are closed to E.33's workers as whole files (ProtocolReview LE-7, FE-5; FixVerifier
    R-W1-8).
Process
42. The fix re-check ran as four split FixVerifier workers (by item and section) instead of one, and the v0.4 diff
    spot-check as two; same model (Fable xhigh) and effort, less context per step.
43. All 25 NOTE items of the re-check were applied with the SHOULD FIX items (the prompt requires only BLOCKING and
    SHOULD FIX).
44. The full pytest ran during the re-check (no code changed after Part 0); its one failure predates E.32 and is not
    fixed here (decision D7).
45. The MathReviewer NOTE items were not applied to the reader files (listed in the review files).
46. The raw fetched source pages under reports/stage_e32_briefs/pages/ (PDF, HTML, text extracts) are not committed
    (E.28 and E.31 precedent; 275 MB); their logs with URL, time and sha256 are.
47. No review round after FinalDiffCheck: every BLOCKING and SHOULD FIX item of every round is applied, the last
    round's replacement texts are the checker's own, and the lead's consistency grep found nothing further.

## 7. Decisions for the user (each with a recommendation)

D1. Keep or drop the protocol-added test DSR (DSR > 0.95 at N with V = 1/(T_test - 1)). Recommendation: keep. It is
    the conservative reading of V43's "DSR at N" and does not depend on how similar the tested candidates are.
    Keeping it: b_test 0.1649, binding selection threshold 0.2007 (t 5.66), 1.22 ticks net per 15-minute trade at 4
    a date. Dropping it: b_test 0.1017 (t > 3 alone), G4 0.1373, binding threshold 0.1724 (G3), about 1.05 ticks at
    the same rate (scaled from P7.2's random-walk line, 1.22 x 0.1724/0.2007; an estimate). Deadline: before E.33's
    C1 registration, as a protocol amendment (a new version hashed before C1, P7.2 restated); after C1 it cannot
    change (P7.2).
D2. Amend V14 (c) for this test so that the program verdict's DSR uses V = 1/(T_test - 1) (ProtocolReview AR-1).
    Recommendation: amend, before the test is registered. As coded, V takes the population variance of the 2-3
    tested Sharpes, so SR0 = 3.2045 x their SD: beside one null companion no true Sharpe passes (SR0 = 1.60 x the
    strong member's), and beside a weaker real one the pass probability falls with the gap (true 0.25 beside 0.15:
    about 0.84; beside 0.10: about 0.09). Amending makes the DSR part of the verdict equal to the protocol-added
    check, whose power P7.2 tabulates; Holm, t > 3 and PBO stay. Amending can only loosen the combined bar to that
    point, so the discovery outcomes cannot steer it further.
D3. Launch E.33 (docs/prompts/STAGE_E.33.md, run the frozen protocol). Recommendation: launch after D1 is recorded,
    on Max, under its prompt's deadlines (search cut 07:00 PDT 2026-10-28, nothing after 09:00). Compute (P5, a
    guess until E.33's probe): ZM book rebuild 9-18 minutes; ZS/ZL re-split about 90 s of decoding and up to 32.5 GB
    of disk; features 1-3 CPU-hours; synthetic proofs 4,800 fits, 0.9-1.4 h of wall time at the balanced probes
    (1.5-9 h at the guesses); the search 1,800 fits, 1-4 h of wall time at <= 8 threads; memory far under the 70%
    rule. Usage: this stage used 545,304,733 tokens over its three lead sessions (section 8); E.33 has more
    code to write and test (split, sampler, labels, simulator, purged CV, guard, P8) and fewer readers, so expect the
    same order (an estimate from this stage's measured total, not a measurement of E.33).
D4. Test-data quote plan (P9). Recommendation: no quote until a funded Databento account exists and E.33 has a
    non-empty Tier A; then one quote for ZM.v.0 MBO, ZS.v.0 and ZL.v.0 MBP-1 and the ZM, ZS and ZL definitions,
    2017-05-21..2020-11-30 (trade dates from 2017-05-22), logged before approval. Scale: E.31 paid 121.65 USD for the
    39 months of 2020-12..2024-02 in these schemas; 43 months at the same rates would be about 134 USD (an estimate
    by proportion; 2017-2019 volumes were lower, so it may cost less). If Tier A is empty, nothing is bought.
D5. DATABENTO_API_KEY3 was still non-empty in .env at the start check (V50 said wipe and remove). Recommendation:
    the user removes it (checked by name only; never printed).
D6. The testable window starts 2017-05-22 (MBO from 2017-05-21): the E.33 prompt's "2017-05-01" is superseded by
    protocol P9. Recommendation: note it in the E.33 prompt or a decision line; the seal keeps covering 2017-05-01
    onward (sealing three extra weeks costs nothing).
D7. tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha fails (1 of 8,125
    in the full suite). Cause: the E.20 H6 test (last changed in 498fd05, 2026-10-11) asserts the preflight refuses
    for a "freeze manifest" reason, but the preflight now stops earlier because the harness freeze is v14
    (2e908c81...) and the test expects ece91ae8e699...; it fails identically at HEAD 3a75f3b in a clean worktree,
    and E.29 and E.31 recorded it as the known by-design failure since harness v13. E.32 did not cause it (no
    tracked file changed). Recommendation: a small separate change that re-pins the test to the current harness or
    marks it xfail with the reason, so the suite is green again and a new failure stands out.
D8. E.33's deadlines are quoted by value in P10 from the prompt as amended at 08:16 and the prompt's current times
    govern. Recommendation: if the E.33 times change again, change only the prompt; the protocol need not change.

## 8. Session cost

Tokens come from the transcripts, each message at its final usage, counted by
reports/stage_e32_briefs/work/lead/cost32.py (reports/stage_e10_briefs/cost.py's scan, recursive over subagents/**,
so workflow agents count) over the three lead sessions a51871c6-ae95-4aa9-8b23-0daf24b41dc1,
900dd54a-de4d-4012-a455-b0efd91bbcf0 and 89bc0cd0-ddc5-469d-b633-94a1a978350a and all their subagents, from
2026-10-27T05:00Z to 20:11:27Z (13:11 PDT); the last calls (filling these tables, the commit and the closing reply)
are not counted. Output: reports/stage_e32_briefs/work/lead/cost_raw.txt; per-agent lines in deleg_all.tsv. Token
counts, never estimates; plan-meter percentages are the user's reading.

Wall clock: 2026-10-26 22:21 to 2026-10-27 13:11 = 14 h 50 min. Pauses, not work: PAUSE 1 (planner) 23:16-00:14
(58 min); USAGE LIMIT 1 00:51-02:32 (1 h 41 min); USAGE LIMIT 2 about 03:12-07:31 (4 h 19 min); the planned context
wipe 08:02-08:39 (37 min); USAGE LIMIT 3 08:57-12:35 (3 h 38 min): 11 h 13 min in all. Work: 3 h 37 min.

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-opus-5-5 | 5,100 | 2,296,520 | 440,697,045 | 7,738,397 | 450,737,062 |
| claude-fable-5-1 | 16,240 | 1,211,290 | 72,087,677 | 4,751,351 | 78,066,558 |
| claude-sonnet-5-5 (X1 only) | 200 | 72,108 | 16,167,864 | 260,941 | 16,501,113 |
| all | 21,540 | 3,579,918 | 528,952,586 | 12,750,689 | 545,304,733 |

Delegation share: lead 122,728,688 (22.5%; sessions 48,849,791 + 43,326,750 + 30,552,147), workers 422,576,045
(77.5%): Opus workers 328,008,374 (60.2% of all), Fable workers 78,066,558 (14.3%), Sonnet 16,501,113 (3.0%, the one
X1 run before the never-Sonnet rule). Cache reads are 97.0% of all tokens. Per worker spawn (agent file, model,
effort, tokens): the worker rows of the final table below and section 4 of the return. No max effort was used; the
cost driver was the 24 Opus reader runs (re-spawns included) with long saved-page contexts, 60% of the total.

Final table (times PDT; 10-27 unless marked; tokens by transcript):

| # | Task / agent | Model (effort) | Start-end | Time | Tokens | Status, deviations |
|---|---|---|---|---|---|---|
| 1 | Lead: read inputs, plan, estimate table, start checks | opus (xhigh) | 10-26 22:21-22:42 | 21 min | (lead) | done |
| 2 | Lead: Part 0 seal (tool, 26 tests, 114 files), store-test subsets | opus (xhigh) | 10-26 22:42-23:01 | 19 min | (lead) | done |
| 3 | ValidationMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-26 23:03-23:13 | 10 min | 10,800,750 | stopped at PAUSE 1, re-spawned (row 14) |
| 4 | LeadLagMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-26 23:03-23:15 | 12 min | 14,919,332 | stopped at PAUSE 1, re-spawned (row 15) |
| 5 | CrushEconomics-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-26 23:03-23:16 | 13 min | 14,081,770 | stopped at PAUSE 1 (partial file kept), re-spawned (row 16) |
| 6 | EventStructure-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-26 23:03-23:16 | 13 min | 12,607,561 | stopped at PAUSE 1, re-spawned (row 19) |
| 7 | OrderFlowMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-26 23:03-23:15 | 12 min | 17,711,143 | stopped at PAUSE 1, re-spawned (row 17) |
| 8 | FableProbe-FableXHigh (worker-xhigh, Agent) | fable-5-1 (xhigh) | 10-26 23:03-23:03 | 0 min | 63,019 | done |
| 9 | ExposureInventory-SonnetMed (worker-medium, wf_2ed35392-831) | sonnet-5-5 (medium) | 10-26 23:03-23:14 | 11 min | 16,501,113 | done on Sonnet (before the never-Sonnet rule); re-verified (row 18) |
| 10 | Lead: seal doc, P1 hash check 156/156, p7_thresholds.py, design notes | opus (xhigh) | 10-26 23:05-23:15 | 10 min | (lead) | done |
| 11 | LabelsMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-26 23:14-23:15 | 1 min | 1,451,306 | stopped at PAUSE 1, re-spawned (row 20) |
| 12 | PAUSE 1 (planner request) | - | 10-26 23:16-10-27 00:14 | 58 min | - | not work |
| 13 | Lead: resume, M6/P6 execution variants, X1 corrections to the seal doc, cftc terms, reviewer briefs | opus (xhigh) | 10-27 00:15-00:51 | 36 min | (lead) | done |
| 14 | ValidationMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:16-00:32 | 16 min | 12,877,539 | done |
| 15 | LeadLagMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:16-00:28 | 12 min | 9,060,031 | done |
| 16 | CrushEconomics-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:16-00:23 | 7 min | 5,292,706 | done |
| 17 | OrderFlowMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:16-00:29 | 13 min | 13,300,400 | done |
| 18 | X1Verifier-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:16-00:29 | 13 min | 24,233,595 | done |
| 19 | EventStructure-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:16-00:30 | 14 min | 17,687,636 | done |
| 20 | LabelsMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:23-00:39 | 16 min | 16,865,073 | done |
| 21 | PowerStability-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:29-00:44 | 16 min | 11,970,110 | done |
| 22 | DataFacts-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:29-00:46 | 17 min | 13,560,264 | done |
| 23 | PropStrategyMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:29-00:50 | 21 min | 14,633,090 | stopped at USAGE LIMIT 1 (partial kept), re-spawned (row 34) |
| 24 | ModelsMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:30-00:51 | 21 min | 14,327,082 | done |
| 25 | SoyMicrostructure-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:32-00:49 | 17 min | 25,547,321 | done |
| 26 | AgDesks-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:39-00:51 | 12 min | 14,158,856 | stopped at USAGE LIMIT 1 (partial kept), re-spawned (row 35) |
| 27 | AlphaProcess-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:44-00:51 | 7 min | 6,676,053 | stopped at USAGE LIMIT 1, re-spawned (row 36) |
| 28 | MLEvidence-OpusHigh (worker-high, Agent) | opus-5-5 (high) | 10-27 00:46-00:50 | 3 min | 3,081,497 | stopped at USAGE LIMIT 1, re-spawned (row 32) |
| 29 | MathReviewerC-FableXHigh (worker-xhigh, Agent) | fable-5-1 (xhigh) | 10-27 00:50-00:51 | 1 min | 1,444,111 | stopped at USAGE LIMIT 1, re-spawned (row 33) |
| 30 | USAGE LIMIT 1 | - | 10-27 00:51-02:32 | 101 min | - | not work |
| 31 | Lead: resume (continuation script), test-bar ruling, p7_final.py, protocol v0.1, brief front | opus (xhigh) | 10-27 02:32-03:12 | 40 min | (lead) | done |
| 32 | MLEvidence-OpusHigh (worker-high, Agent) | opus-5-5 (high) | 10-27 02:33-02:48 | 15 min | 13,425,372 | done |
| 33 | MathReviewerC-FableXHigh (worker-xhigh, Agent) | fable-5-1 (xhigh) | 10-27 02:33-02:51 | 17 min | 2,980,789 | done |
| 34 | PropStrategyMath-OpusHigh (worker-high, wf_df544c98-716) | opus-5-5 (high) | 10-27 02:33-02:45 | 11 min | 7,888,116 | done |
| 35 | AgDesks-OpusHigh (worker-high, wf_df544c98-716) | opus-5-5 (high) | 10-27 02:34-02:42 | 9 min | 7,915,557 | done |
| 36 | AlphaProcess-OpusHigh (worker-high, wf_df544c98-716) | opus-5-5 (high) | 10-27 02:34-02:51 | 18 min | 18,736,590 | done |
| 37 | MathReviewerA-FableXHigh (worker-xhigh, Agent) | fable-5-1 (xhigh) | 10-27 02:34-02:53 | 19 min | 2,174,991 | done |
| 38 | MathReviewerB-FableXHigh (worker-xhigh, Agent) | fable-5-1 (xhigh) | 10-27 02:43-03:03 | 20 min | 8,255,017 | done |
| 39 | MathReviewerD-FableXHigh (worker-xhigh, Agent) | fable-5-1 (xhigh) | 10-27 02:46-03:11 | 24 min | 7,412,718 | done |
| 40 | LeakageReviewer-FableXHigh (worker-xhigh, wf_3d631049-c34) | fable-5-1 (xhigh) | 10-27 03:05-03:11 | 6 min | 2,932,000 | stopped at USAGE LIMIT 2, no output; re-run (row 47) |
| 41 | ArithmeticReviewer-FableXHigh (worker-xhigh, wf_3d631049-c34) | fable-5-1 (xhigh) | 10-27 03:05-03:11 | 6 min | 1,605,800 | stopped at USAGE LIMIT 2, no output; re-run (row 50) |
| 42 | FeasibilityReviewer-FableXHigh (worker-xhigh, wf_3d631049-c34) | fable-5-1 (xhigh) | 10-27 03:05-03:11 | 6 min | 3,484,948 | stopped at USAGE LIMIT 2, no output; re-run (row 51) |
| 43 | DofReviewer-FableXHigh (worker-xhigh, wf_3d631049-c34) | fable-5-1 (xhigh) | 10-27 03:05-03:07 | 2 min | 1,707,444 | stopped at USAGE LIMIT 2, no output; re-run (row 49) |
| 44 | FixApplier-OpusHigh (worker-high, Agent) | opus-5-5 (high) | 10-27 03:11-03:11 | 0 min | 220,726 | stopped at USAGE LIMIT 2, no edit; re-run (row 48) |
| 45 | USAGE LIMIT 2 | - | 10-27 03:12-07:31 | 259 min | - | not work |
| 46 | Lead: protocol v0.2, relaunches, Part V draft, v0.3 (45 items) | opus (xhigh) | 10-27 07:31-08:02 | 31 min | (lead) | done |
| 47 | LeakageReviewer-FableXHigh (worker-xhigh, wf_30d7118e-f81) | fable-5-1 (xhigh) | 10-27 07:32-07:53 | 21 min | 8,536,712 | done |
| 48 | FixApplier-OpusHigh (worker-high, Agent) | opus-5-5 (high) | 10-27 07:32-07:38 | 6 min | 4,978,898 | done |
| 49 | DofReviewer-FableXHigh (worker-xhigh, wf_30d7118e-f81) | fable-5-1 (xhigh) | 10-27 07:32-07:57 | 24 min | 9,806,052 | done |
| 50 | ArithmeticReviewer-FableXHigh (worker-xhigh, wf_30d7118e-f81) | fable-5-1 (xhigh) | 10-27 07:32-07:52 | 19 min | 3,907,769 | done |
| 51 | FeasibilityReviewer-FableXHigh (worker-xhigh, wf_30d7118e-f81) | fable-5-1 (xhigh) | 10-27 07:32-07:55 | 22 min | 3,088,124 | done |
| 52 | PLANNED CONTEXT WIPE | - | 10-27 08:02-08:39 | 37 min | - | not work |
| 53 | Lead: resume checks, re-check plan, estimate table | opus (xhigh) | 10-27 08:39-08:42 | 3 min | (lead) | done |
| 54 | Full pytest (background shell, nice 10) | - | 10-27 08:42-09:01 | 19 min | - | 8,116 passed, 1 known failure |
| 55 | Lead: model checks, deleg32.py, drafts | opus (xhigh) | 10-27 08:42-08:57 | 15 min | (lead) | done |
| 56 | FixVerifierLeakArith-FableXHigh (worker-xhigh, wf_6418603c-1ef) | fable-5-1 (xhigh) | 10-27 08:42-08:56 | 14 min | 5,415,437 | done |
| 57 | FixVerifierFeas-FableXHigh (worker-xhigh, wf_6418603c-1ef) | fable-5-1 (xhigh) | 10-27 08:42-08:52 | 10 min | 1,275,543 | done |
| 58 | FixVerifierDofA-FableXHigh (worker-xhigh, wf_6418603c-1ef) | fable-5-1 (xhigh) | 10-27 08:42-08:50 | 8 min | 2,784,627 | done |
| 59 | FixVerifierDofB-FableXHigh (worker-xhigh, wf_6418603c-1ef) | fable-5-1 (xhigh) | 10-27 08:42-08:54 | 12 min | 1,528,664 | done |
| 60 | USAGE LIMIT 3 | - | 10-27 08:57-12:35 | 218 min | - | not work |
| 61 | Lead: pytest failure investigation (clean worktree at HEAD) | opus (xhigh) | 10-27 12:35-12:38 | 3 min | (lead) | predates E.32 |
| 62 | Lead: re-check rulings, protocol v0.4 | opus (xhigh) | 10-27 12:38-12:42 | 4 min | (lead) | done |
| 63 | Lead: return drafts; spot-check rulings, v0.5 | opus (xhigh) | 10-27 12:42-12:58 | 16 min | (lead) | done |
| 64 | FixSpotCheckB-FableXHigh (worker-xhigh, wf_22487789-c6a) | fable-5-1 (xhigh) | 10-27 12:42-12:56 | 14 min | 4,445,077 | done |
| 65 | FixSpotCheckA-FableXHigh (worker-xhigh, wf_22487789-c6a) | fable-5-1 (xhigh) | 10-27 12:42-12:52 | 10 min | 3,770,126 | done |
| 66 | FinalDiffCheck-FableXHigh (worker-xhigh, Agent) | fable-5-1 (xhigh) | 10-27 12:58-13:06 | 8 min | 1,447,590 | done |
| 67 | Lead: final-check rulings, v0.6, FREEZE v1.0 | opus (xhigh) | 10-27 13:06-13:08 | 2 min | (lead) | done |
| 68 | Lead: brief assembly, end checks, return, progress, STAGES, cost, commit | opus (xhigh) | 10-27 13:08-13:11 | 3 min | (lead) | done |
| - | Lead session a51871c6, whole | opus 5.5 (xhigh) | 10-26 22:21-10-27 00:51 | - | 48,849,791 | - |
| - | Lead session 900dd54a, whole | opus 5.5 (xhigh) | 02:32-08:02 | - | 43,326,750 | - |
| - | Lead session 89bc0cd0, whole | opus 5.5 (xhigh) | 08:39-13:11 | - | 30,552,147 | - |
| total | Stage E.32 | - | 10-26 22:21-10-27 13:11 | work 3 h 37 min (pauses 11 h 13 min) | 545,304,733 | initial estimate (10-26 23:01): done by about 11:20 PDT 10-27; this session's estimate (08:41): 10:40 |
