# Stage E.33c return: ZM discovery search (completion): no candidate

Lead: Opus 5.5 (claude-opus-5-5) in three sessions separated by two planned context wipes:
7c6136a3-16c6-44df-891a-efd174837057 (18:05-18:39 PDT; effort xhigh at launch, max from 18:10 under V55),
fec9a0d1-0594-4d0f-bee3-e7a05a38398a (19:54-21:22, max) and 7ea5755f-a4a7-4902-a9d3-8df2c289a807 (from 21:31, max;
the closing steps). Times are America/Vancouver, from `date`, log stamps, file mtimes and transcripts.
Binding, in order: protocol 0.3 (reports/stage_e32_discovery_protocol_v0.3.md, sha256
a2a2856f49723f97319a4db2819ba4d1b5c4b8a1dc86a596e7c48110dbb48246 = FROZEN v1.0 c4ffb9d7 plus the V53 amendment of
the P5/P10 compute reference only); docs/prompts/STAGE_E.33.md; docs/prompts/STAGE_E.33c.md; docs/DECISIONS.md
V20-V55.

## 1. Summary (E.33, E.33b and E.33c together)

The frozen ZM discovery search ran all 300 registered configurations and selected nothing: a clean negative.

- N: 538 before, 838 after (r009-E33, 300 configurations, 2026-10-28 14:23 PDT). E.33c registered nothing; its
  amendment (protocol 0.3, V53) kept the registration.
- What ran: 5 feature sets x 6 labels x 10 model settings on 796 out-of-fold ZM dates (2020-12-30 to 2024-02-29);
  all 1,800 fold fits, 0 failed. Part B (two implementations, leakage tests, 40 synthetic proofs) passed in
  E.33 and E.33b. E.33b's run stopped after 72 configurations at a compute limit set from a synthetic probe;
  protocol 0.3 re-set only that reference from measured fold times, and the other 228 finished in 2.0 hours, at
  0.39 of the new stop.
- Selection (P8, frozen code, recomputed three more times): 61 configurations trade often enough (G1), and all 61
  lose more than 1.0 tick a trade after costs; 8 others average at least 0.5 tick, on at most 55 trades each; none
  passes the significance or power gates (largest DSR 0.0248 against 0.95, largest daily t 1.35; BH and Holm
  reject nothing). Tier A is empty.
- Null comparison: the best daily Sharpe (0.0478; binding threshold 0.2007) lies inside the synthetic null's
  per-seed maxima over only 20 configurations (-0.076 to 0.060); no real configuration exceeds the null's largest
  value. PBO 0.14 (reported).
- Finalists: none, so no per-firm net ticks or trade rates. At every firm's fee the median configuration loses 2.2
  to 2.6 ticks a trade.
- E.34: nothing to buy or test; the 2017-05 to 2020-11 test window stays sealed.
- Checks: the VerifyWorker (Fable) re-simulated all 300 from the raw predictions and confirmed the decision; the
  StatsReviewer (Fable) found 0 BLOCKING items and 4 SHOULD FIX (wording), all fixed.

## 2. Guardrail evidence

Start (S1, 18:10-18:16; reports/stage_e33c_briefs/checks_start.txt, freeze_verify_start.txt, atime_census_start.txt):
the protocol file reports/stage_e32_discovery_protocol.md has sha256 c4ffb9d7 (it calls itself FROZEN v1.0; the
prompt's "protocol 0.2", open choice 1); the freeze file reports/stage_e33_pipeline_freeze.sha256 has sha256
eb565a37, and `freeze33.py verify --remeasure` found 0 differences on 227 files and 4,125 derived inputs (rc 0,
18:13:01-18:14:21); registration r009-E33 is the last registry line, N 838, require_registered(300 ids, test E33)
ok; the test-seal guard dry check (guard33.py dry-check) refused 4 of 4 forbidden reads; data.holdout status all_ok
with unlocks_logged 0 on all 6 stores; soy test seal 114/114; REGISTRATION.md 0 bytes; harness 2e908c81 preflight
OK; spend ledger ledger/databento_spend.jsonl 37,290 lines, sha256 42589d7b (as at E.33b's end). No outcome file
of the search had been opened (open choice 2: what the log and markers hold, a scan of the tool-call inputs of
every transcript since the first fit, and a stat-only atime census, with the relatime limit stated).

Amendment and resume (18:34-18:36): protocol 0.3 hashed at 18:34:30 (sha256 a2a2856f; .sha256 file beside it);
amendment line a001-E33 appended to ledger/trial_amendments.jsonl (file sha256 511ae4c3); N 838 unchanged; freeze
verify --remeasure 0 differences on 227 files and 4,125 derived inputs (18:34:53-18:36:04); the resumed runner
re-checked the registration (300) at launch and refused no marker.

Search end (20:37-20:38; reports/stage_e33c_briefs/search_end.txt): runner "finished: 300/300 configs DONE (0
failed: []); not done: []", wrapper rc=0; 300 of 300 configuration DONE markers, status ok 300; fold markers DONE
1,800, FAILED 0; no stop file; the watcher's lowest MemAvailable 6,311 MB; registry current_n 838. Outcomes were
first opened after these checks, at the selection (20:38:50).

End (lead session 3, 21:35-21:37; reports/stage_e33c_briefs/checks_end.txt, freeze_verify_end.txt): `git log
--oneline -3` head 88d4eb8 (no commit before the final one); `git status --short` 2,154 lines against 2,148 at the
start, the 6 new lines all this stage's (the STATE file; the return, protocol 0.3 and its .sha256,
ledger/trial_amendments.jsonl and the resumed search log), none dropped; data.holdout status all_ok with
unlocks_logged 0 on all 6 stores; soy test seal sealed 114/114, unlocks 0; REGISTRATION.md 0 bytes; harness 2e908c81
preflight OK; spend ledger 37,290 lines, sha256 42589d7b (unchanged); N 838, last registry line r009-E33 (538 -> 838,
14:23:13), require_registered(300 ids, test E33) ok; protocol v1.0 c4ffb9d7 and 0.3 a2a2856f; freeze file eb565a37,
and `freeze33.py verify --remeasure` found 0 differences on 227 files and 4,125 derived inputs (rc 0,
21:35:23-21:36:38); the guard dry check refused 4 of 4 (rc 0, read through PIPESTATUS);
ledger/trial_amendments.jsonl 1 line, sha256 511ae4c3; search_real.log sha256 63c0a802 (unchanged). The holdout
status also ran at the end of sessions 1 and 2 and at session 3's start and end (holdout_session*.txt; open choice
27): unlocks_logged 0 each time. Full suite (`nice -n 10 uv run pytest -q -p no:cacheprovider`, no
PYTHONPYCACHEPREFIX, 21:02:01-21:21:28, started with 10,945 MB available, lowest 4,037 MB, the 2 GB guard never
fired; pytest_end.txt, pytest_memguard.txt): 1 failed, 8,116 passed, 5 skipped, 3 xfailed, 54 warnings. The one
failure, tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha, fails by
design since harness v13 (the same counts as at E.33b's end). No worker, job or shell of this stage was running at
the end (checked before the commit).

Scope: no Databento call (the spend ledger is unchanged); no read of the test window (2017-05-01 to 2020-11-30) or
of anything dated 2024-03-01 or later; the protocol changed only by the logged, reviewed and hashed 0.3 amendment
(V53), with no configuration added or dropped; no pipeline file changed after the freeze; nothing under live/ or
ops/, no TopstepX or ProjectX; no key printed or logged; REGISTRATION.md 0 bytes; no push. Large outputs stay under
/mnt/large-storage/market_data/PropExperiment/derived/e33/ (search/, features/2b30cb0e953b, labels/b15c4ca10d68),
not in git.

## 3. Results

### 3.1 Part B (unchanged since E.33b; reports/E.33b_RETURN.md sections 3.1-3.3)
- B3: 0 disagreeing cells between the two implementations on all 59 features, 6 labels and sigma on the 20 seeded
  dates (run full_r3).
- B4: LT1 at 200 draws under both priors, LT2 on the R-L10 span (46,886 rows, 0 violations), LT3-LT6 and LT7
  (3,620 of 3,620 decisions equal) pass.
- B5: null proof Tier A empty in 20 of 20 seeds; planted proof Tier A non-empty in 20 of 20; 0 failed fits.

### 3.2 The amendment (protocol 0.3; S2)
Protocol 0.3 is v1.0 plus one changed part, the P5/P10 compute reference (diff reports/stage_e33c_briefs/
protocol_v0.3.diff: 3 hunks, the status line, one P5 bullet, one P10 clause). The reference was set from the
measured per-fold wall times in reports/stage_e33_briefs/work/logs/search_real.log (sha256 63c0a802; times only):
R_0.3 = B + sum over the LOGIT folds of t_f / 8 + sum over the LGBM folds of t_f / 2 = 976.43 + 9,522.7 + 1,515.8 =
12,014.9 s, with t_f measured for the 440 finished folds and projected for the rest from S5's cell times scaled by
the measured S1/S5 ratio (LOGIT 0.492659, LGBM 0.707670) and the feature count; 3 x R_0.3 = 36,044.7 s. Method
script reports/stage_e33c_briefs/tools/project_ref_v03.py, output ref_v03.json; a Haiku extraction of the same log
matched fold for fold. AmendReviewer (Fable, confirmed): GO, 0 BLOCKING, 0 SHOULD FIX, 9 NOTE.

### 3.3 What ran
- All 300 configurations finished with status ok, 0 failed: 72 in the first run (14:29:04-16:08:11, stopped by
  v1.0's limit) and 228 in the resumed run (first fold start 18:36:15.199, finished 20:37:27.786, no pause). 1,800
  of 1,800 fold fits are done; the 8 folds cut at 16:08 re-ran once and finished.
- Measured under 0.3's P5: 6,774.8 s (first run: build 2,387.0 + fits 4,387.8) + 7,272.6 s (resumed) = 14,047.4 s
  (3.90 hours) = 1.17 x R_0.3 and 0.390 of the 3x stop. The resumed part took 0.98 of its projection (7,437.3 s).
- The interval 16:08:11-18:36:15 (8,884.2 s) is a logged pause under 0.3 (open choice 7).

### 3.4 Selection (D1, P8 on all 300)
The frozen select33.py (sha256 9b992806, as in the freeze list) ran at 20:38:50-20:38:54 on all 300 at N 838:
reports/stage_e33c_briefs/select/P8_select33.json (sha256 ee506884263d712e), stdout P8_select33.out. The
StatsCoder's own gate code, written from P8 and the readings, agrees with it on every number
(reports/stage_e33c_briefs/work/D_stats.md, section 0).

| gate (P8; Topstep, market, L = 1 s) | alone | in order |
|---|---|---|
| G1 activity: at least 796 trades and a trade on at least 398 dates | 61 | 61 |
| G2 edge: mean net per trade at least 0.50 tick | 8 | 0 |
| G3 significance: DSR > 0.95 at N 838 | 0 | 0 |
| G4 power: SR_d - se >= b_test 0.164882 | 0 | 0 |
| G5 stability | 0 | 0 |

- The 61 G1 passers (by set S5 23, S4 16, S3 12, S2 10, S1 0; by label T30 34, F60 20, T15 5, F30 2) all lose
  money per trade: the best mean net per trade among them is -1.098 ticks, and the best of them by SR_d is
  E33-S3F60L001A at -0.0522.
- The 8 G2 passers traded 8 to 55 times in 796 dates (on 2 to 47 dates) and all fail G1.
- G3: the largest DSR is 0.0248 (E33-S2F30G2200); 78 configurations never traded (constant series; DSR undefined,
  so G3 fails). G4: the largest SR_d - se is 0.0305. G5: no configuration meets part (a), (b) or (c); 10 have a
  positive total net, and in each one month carries more than 25% of it.
- Reports, never gates: BH (q 0.05) and Holm (0.05) over the 300 one-sided p reject 0 (smallest p 0.0888, daily t
  1.348; the largest t of the 300). Per firm, the mean net per trade is a fee shift on the same fills (the P6.4
  execution variants are not computed): the median over the 222 configurations that traded runs from -2.207 ticks
  (Topstep 0.528) to -2.599 (Tradeify 0.920, and Lucid if its 5.60 USD is not all-in); at 0.920, 6 configurations
  stay at or above 0.50, none with more than 55 trades.
- Tier A: empty. Tier B (reading continue): E33-S2F30G2200, E33-S1F15G3200; it has no use without a test list.

The 10 best by SR_d (P10 item ii; P8 order; every P6.2 statistic in D_stats.md, section "P10 (ii)"):

| rank | config | SR_d | daily t | DSR | trades | dates with a trade | mean net per trade (Topstep) | gates passed |
|---|---|---|---|---|---|---|---|---|
| 1 | E33-S2F30G2200 | 0.0478 | 1.348 | 0.0248 | 55 | 47 | 4.399 | G2 |
| 2 | E33-S1F15G3200 | 0.0473 | 1.335 | 0.0000 | 8 | 2 | 8.472 | G2 |
| 3 | E33-S2F30L001A | 0.0452 | 1.274 | 0.0053 | 13 | 10 | 7.472 | G2 |
| 4 | E33-S5F15G2050 | 0.0426 | 1.201 | 0.0000 | 39 | 4 | 2.062 | G2 |
| 5 | E33-S5F15G3050 | 0.0225 | 0.636 | 0.0017 | 36 | 7 | 0.611 | G2 |
| 6 | E33-S3F30L001A | 0.0140 | 0.394 | 0.0015 | 14 | 12 | 1.401 | G2 |
| 7 | E33-S2F30L100A | 0.0084 | 0.236 | 0.0011 | 30 | 22 | 0.939 | G2 |
| 8 | E33-S2F30L100E | 0.0067 | 0.188 | 0.0009 | 26 | 18 | 0.818 | G2 |
| 9 | E33-S1T15G2200 | 0.0053 | 0.150 | 0.0012 | 66 | 45 | 0.214 | none |
| 10 | E33-S2F30L010A | 0.0017 | 0.048 | 0.0007 | 29 | 21 | 0.196 | none |

None of the ten trades more than 66 times in 796 dates; their positive means rest on a few dozen trades, and the
binding threshold is 0.2007.

### 3.5 The search distribution beside the null (D3)
Figure reports/stage_e33c_briefs/work/stats/fig/D3_sharpe_hist.png. The null is B5's: 20 null seeds x 20
configurations (S5 x {F15, T30} x 10 grid points), 400 series on the same 796 dates and the same statistic.

| series | n | mean | SD | q05 | median | q95 | max |
|---|---|---|---|---|---|---|---|
| real, all 300 | 300 | -0.0840 | 0.0839 | -0.2603 | -0.0706 | 0.0000 | 0.0478 |
| real, configurations that traded | 222 | -0.1135 | 0.0786 | -0.2651 | -0.0977 | -0.0093 | 0.0478 |
| null, per configuration | 400 | -0.1194 | 0.0937 | -0.2809 | -0.0988 | 0.0000 | 0.0602 |
| null, per-seed maximum over 20 configurations | 20 | -0.0014 | | -0.0586 | 0.0058 | 0.0514 | 0.0602 |

- No real configuration reaches SR0 = 0.1137 (E[max SR] at N 838), G3's 0.1724 or the binding 0.2007. 10 have
  SR_d > 0; none exceeds the null's largest per-configuration value, 0.0602. The real best, 0.0478, lies inside the
  range of the null's per-seed maxima (-0.0757 to 0.0602), which are maxima over 20 configurations, not 300.
- Both distributions sit below zero, as costs predict (every trade pays the spread and the 0.528-tick fee). The
  real search has more no-trade configurations (78 of 300 against 31 of 400), which pulls its mean toward 0.
- Strictly like for like (the null's own design, S5 x {F15, T30} x 10 grid points, 20 configurations): the real
  subset's best SR_d is 0.0426 (E33-S5F15G2050), and 2 of the 20 null per-seed maxima exceed it (rank 3 of 21).
- An expected null maximum over 300, built from the null's per-configuration spread as if the 300 were independent
  with zero true edge, is 0.1230 (SD 0.0425; 0.1262 with the df-corrected SD 0.0436, the figure's line; report
  only). The same construction overstates B5's own per-seed maxima by 0.031, so it is an upper-side figure.

### 3.6 Robustness (D2)
No configuration passes D1, so D2 has no candidate. The P6.4 execution variants and P6.5 diagnostics run only after
a test list is hashed (P8); there is none, so none was computed (open choice 19). STAGE_E.33.md D1 also asks for
stability across months and sessions: the month part is G5 (b) and (c) in section 3.4; the split by session is a
P6.5 item and was not computed, for the same reason.

### 3.7 Finalists and the P10 null report
Tier A is empty: no finalist, no test list, no purchase. P10's null report (sources: work/D_stats.md, D_stats.json):
- (i) The gate funnel: section 3.4 (alone 61 / 8 / 0 / 0 / 0; in order 61 / 0 / 0 / 0 / 0; 0 failed).
- (ii) The 10 best configurations by SR_d: section 3.4's table; every P6.2 statistic in D_stats.md.
- (iii) The distribution of the 300 OOF daily Sharpes beside the synthetic null and SR0 at N 838 (0.1137): section
  3.5.
- (iv) The discovery PBO (CSCV, 8 blocks of 99 dates, 70 splits, all 300 series): 0.1429 (10 of 70), at the low end
  of M5a e's null band 0.13-0.83 (reported, not a gate). The in-sample winner's out-of-sample net averages -57.18
  ticks: the low PBO says the in-sample ranking persists out of sample, not that the winners make money.
- (v) The minimum detectable net edge per trade at 80% power on the 796 OOF dates: a true daily Sharpe of 0.2309 at
  the binding threshold (0.2025 at G3 alone). With P7.2's normal-moment random-walk formula (e80 = 0.2309 x 3.15
  sqrt(h) / sqrt(n); a lower-side figure for heavy-tailed series, which the measured figures below cover) that is 0.81 ticks a trade at 5-minute holds and 4 trades a date, 1.41 at 15 minutes, 1.99 at 30 minutes,
  and 3.98 at 60 minutes and 2 a date (TB labels at their vertical h). Measured on each configuration's own daily
  series, the median among the G1 passers is 1.57 (T15), 1.95 (T30), 4.33 (F60) and 4.37 (F30) ticks a trade. Every
  G1 passer's realised mean net is below -1.0.
- (vi) A null statement per family in the sense of docs/NULL_CRITERIA_E.md: "no statement" for all five sets (S1
  F1 crush, S2 F2 cross-asset, S3 F3 order flow, S4 F4 own price path, S5 pooled). Reasons, quoted from the
  criteria file in D_stats.md: the configurations are not members of a hashed confirmation list (ZM's cluster K6
  list has 27 members, none from E.33); the 796 dates are search dates, not a pre-registered confirmation read; every
  set uses order-book inputs ("signals needing order-book data" are out of that file's scope); no UCB95 is computed.
- (vii) No candidate; the test window stays sealed; no test data purchase.

### 3.8 Part E: the clean negative
- What was searched: 300 pre-registered configurations (r009-E33), that is 5 feature sets (crush residual,
  cross-asset propagation from ZS and ZL, ZM order flow and book state, ZM's own price path, and all four pooled,
  each with the context block) x 6 labels (fixed horizons of 5, 15, 30 and 60 minutes; triple barrier at 15 and 30)
  x 10 model settings (6 regularised multinomial logits, 4 shallow LightGBM). Data: the owned ZM MBO and ZS and ZL
  MBP-1 on 796 out-of-fold dates, 2020-12-30 to 2024-02-29, in 6 blocked folds with a 21-date embargo; Topstep
  market orders at 1 s latency and a 0.528-tick fee, under the trade-through rule's market variant.
- The null comparison: section 3.5. The real search looks like the synthetic null: its best daily Sharpe (0.0478)
  is inside the null's per-seed maxima over 20 configurations, every multiple-comparison check rejects nothing
  (largest t 1.348, largest DSR 0.0248), and the 61 configurations that meet G1 (at least one trade a date on
  average, on at least half the dates) lose more than 1.0 tick a trade after costs (the best -1.098).
- No near miss is promoted: the best configuration is a quarter of the binding Sharpe (0.0478 against 0.2007) on
  55 trades, and no configuration passes two gates.
- What this does and does not show: no configuration passes the gates. A configuration with a true daily Sharpe of
  0.2309 would have cleared the binding threshold (G3 and G4) with probability 0.8 (section 3.7 v), so an edge of
  that size in one of these configurations would most likely have been found; smaller edges could be missed, and
  G1, G2 and G5 apply as well. It is not evidence that no ZM edge exists, and it is not a null statement in the
  program's sense (item vi). The program's next options are in section 7.

## 4. Delegation record

| Agent (description) | Agent file | Model (confirmed from transcript) | Effort | Start-end (PDT) | Status |
|---|---|---|---|---|---|
| FoldTimes-HaikuMed | worker-medium | haiku = claude-haiku-5-5 | medium | 18:17:42-18:18:33 | done: 448 rows (440 done, 8 cut), equal to the lead's parse fold for fold |
| AmendReviewer-FableXHigh | worker-xhigh | fable = claude-fable-5-1 | xhigh | 18:22:52-18:34:08 | GO, 0 BLOCKING, 0 SHOULD FIX, 9 NOTE |
| StatsCoder-OpusXHigh | worker-xhigh | opus = claude-opus-5-5 (147 assistant records) | xhigh | 20:39:48-20:57:50 | done: D1, D3, P10 (i)-(vi); its own gate code equals select33 on every number; 28 tests pass |
| VerifyWorker-FableXHigh | worker-xhigh | fable = claude-fable-5-1 (85 assistant records) | xhigh | 20:39:56-20:59:46 | CONFIRMED: 300 of 300 re-simulated row for row; 3 non-gate convention differences |
| StatsReviewer-FableXHigh | worker-xhigh | fable = claude-fable-5-1 (76 assistant records) | xhigh | 21:01:33-21:15:38 | 0 BLOCKING, 4 SHOULD FIX (fixed), 8 NOTE |

The lead (opus, max) ran S1, the 0.3 method, the hash, the ledger line, the watcher, the search, the step-5
checks, select33, Part E and this return. No worker spawned another.

## 5. Verification

- 0.3 amendment: AmendReviewer recomputed every number of R_0.3 identically and found the diff limited to the
  compute reference (review/AmendReview_c.md).
- D4 (VerifyWorker, Fable, fresh context; reports/stage_e33c_briefs/work/D4_verify.md): the selection decision is
  CONFIRMED. It re-simulated all 300 configurations from fold<k>.npz and the label store with its own code (P3.5,
  P3.8): every trade (162,189), daily value and not-made record equals the pipeline's; the funnel, the ranking, Tier
  A (empty) and Tier B equal P8_select33.json and D_stats.json; its own bisection gives b_test 0.16488165417, equal
  to the pipeline's. Three differences, none in a gate: (1) DSR and se are None for the 78 no-trade series in the
  pipeline and D_stats, where the program's function returns 0.00068 (G3 fails either way); (2) its own-formula DSR
  differs from the program's function by 6e-9 to 9e-9 relative on 14 configurations (two inverse-normal
  implementations; the program's function, which G3 names, agrees at 1e-9); (3) on 8 configurations with one
  undefined leave-one-month-out t, the pipeline reports the minimum over the 38 defined months and the verifier
  reports None (G5 (c) fails in all three). Independence: it read select33's stdout headline before computing and
  says so; it compared the JSON only after its own numbers were written. Its D_stats comparison (20:53) read an
  earlier write of D_stats.json (sha256 fac9aea9; file time 20:50); the final file (cdaa33b8, 20:57:27) was checked
  in D5: equal on every gate-relevant number (review/StatsReview_c.md, check (a)).
- D5 (StatsReviewer, Fable, fresh context; reports/stage_e33c_briefs/review/StatsReview_c.md): 0 BLOCKING, 4 SHOULD
  FIX, 8 NOTE. Its own third recomputation agrees (DSR to 1.4e-10, gate flags, funnel, BH and Holm 0 of 300, s80
  0.2309, e80 0.81 / 1.41 / 1.99 / 3.98); the P10 (v) formula reproduces P7.2's per-trade line; D3 is like for like;
  D4's code imports only cal33 and the program's DSR function. The 4 SHOULD FIX items were wording in this return's
  section 3 (an overclaim about what the discovery data hold, "at least 1.1 ticks" for a best of -1.098, an
  ambiguous gate count, and the strictly like-for-like S5 x {F15, T30} comparison): all fixed. NOTEs 1-5 and 7 fixed
  here; NOTE 6 concerns a phrase in D_stats.md that this return does not quote; NOTE 8 needs no change.

## 6. Open choices

1. Naming: the protocol file says FROZEN v1.0; the prompt's "0.2" is v1.0 (E.33b's "protocol 0.2" was its section
   0.2). The amended file is called 0.3, as V53 does; its header gives the lineage and keeps v1.0's provenance.
2. S1's "no outcome opened" evidence: the code (what the log and markers hold), a scan of the tool-call inputs of
   every transcript since the first fit, and a stat-only atime census, with the relatime limit stated.
3. checks.sh printed tail's rc for the start guard dry check (the guard itself printed "4 of 4 refused"); fixed to
   PIPESTATUS for the end run.
4. Routing of the fold-time table: Haiku extracted it (V55), the lead's method script parsed the log itself (the
   declaration reads the primary source), and the Haiku CSV served as an equality check (equal fold for fold).
5. The R_0.3 method: P5's measured definition kept, only the reference replaced; rejected (i) v1.0's formula with
   the real fold-6 times, (ii) a reference for the resumed run alone, (iii) S5's cell times unscaled for S2-S4,
   (iv) no feature-count factor (STATE decisions log 18:27).
6. The status paragraph changed (version line); v0.3 line 10 ("E.33 runs this protocol unchanged") is left as is
   (AmendReview NOTE 7) to keep the diff to the compute reference.
7. The interval from the v1.0 stop to the resumed first fold start (8,884.2 s) is a logged pause, written into 0.3.
8. Ledger: the registry refuses amendments, so the amendment is a line in a separate append-only file,
   ledger/trial_amendments.jsonl, written once after the review and the hash (the prompt lists the ledger record
   before the review).
9. The build part stays 2,387.0 s as v1.0's watcher and p10_stop.json applied it, not the PostStop review's exact
   2,387.7 s (AmendReview NOTE 8; 0.7 s).
10. The resumed run logged to a new file (search_real_c.log), so the 0.3 input (search_real.log) stays unchanged
    (sha256 63c0a802 at the end).
11. Memory: the frozen runner stops submissions below 2,048 MB; the watcher would stop the job if MemAvailable
    stayed below 2,048 MB for 60 s (it never did; lowest 6,311 MB).
12. AmendReview NOTEs 1-9 accepted without a text change (none affects R_0.3).
13. The first lead stopped for a context wipe at 18:38, during the search, as the prompt directs; a fresh lead
    resumed at 19:55 from the STATE file.
14. Routing under V55 rather than the prompt's text: the lead at max effort (prompt: xhigh); the VerifyWorker and
    the StatsReviewer on Fable xhigh, models confirmed from the transcripts (the prompt had the VerifyWorker on
    Opus xhigh); Haiku for one pure extraction; no Sonnet worker was needed.
15. The step-5 script's registry import failed (its own folder was sys.path[0]); the registry check was rerun from
    the repo root (rc 0) and appended to search_end.txt.
16. D3's null: the E.33c brief corrected E.33b's "300 x 20 null-seed Sharpes" (B5 is 20 seeds x 20
    configurations); the comparison is per configuration, the per-seed maxima are labelled as maxima over 20, and
    the strictly like-for-like S5 x {F15, T30} line was added at D5's request.
17. The VerifyWorker was told only the branch, not the funnel. It read select33's stdout headline before computing
    (its brief's addendum named the file) and disclosed it; it compared the JSON only after its own numbers were
    written, and it re-simulated all 300 configurations (more than its branch-N scope).
18. D4's comparison read an earlier write of D_stats.json (fac9aea9); D5 checked the final file (cdaa33b8): equal
    on every gate-relevant number.
19. D2 and the P6.4/P6.5 items (the split by session included) were not computed: no configuration passes D1, and
    P8 runs them only after a hashed test list. The per-firm figures in D1 are a fee shift on the selection
    variant's fills.
20. For P10 (vi), a family is a feature set (P10 calls a whole feature set the "family"); the answer is "no
    statement" for all five.
21. The expected null maximum over 300 (0.1230; 0.1262 df-corrected) is a report with a known upward bias (its n =
    20 check overstates by 0.031); no decision uses it.
22. B5_proofs.md line 41's "368 non-constant null series" is 369 (368 counts configurations with at least 2
    non-constant seeds; its 0.0434 reproduces either way). The E.33 file is left as frozen evidence; the correction
    is recorded in D_stats.md and here.
23. The full test suite ran during D5 (the review ran only small scripts; pytest collects only tests/, so no Part D
    file can change its result), started with at least 8 GB available under a 2 GB guard.
24. The selection output (P8_select33.json, 505 KB) and D_stats.json (618 KB) are committed under
    reports/stage_e33c_briefs/ as the selection record; the per-configuration tables and the verifier's
    re-simulation outputs stay under derived/e33/ (stats_c/, verify_c/).
25. D5 NOTE 6 (D_stats.md line 45's "all four" means all four G5 parts) is left in the StatsCoder's file; this
    return states the G5 parts directly.
26. The lead stopped a second time for a context wipe (about 312k tokens at 21:18, after D5 and its fixes), as the
    prompt directs. A third session (7ea5755f, from 21:31) ran the closing steps from the STATE file's RESUME HERE
    block: the end checks, sections 1, 2 (End), 6 and 8, the progress entry, the STAGES line and the commit.
27. Holdout status at lead-session starts: session 2 did not run it at its start (19:55; a lead miss). The gap is
    covered by session 1's end check (18:38, holdout_session1_end.txt) and the VerifyWorker's end check (about
    20:57); both show unlocks_logged 0. Session 2 ran it at its end (21:22) and session 3 at its start (21:32:51)
    and end; unlocks_logged 0 on all 6 stores each time. Session 3's end status ran before the commit (its file is
    committed) and once more after it (reported in the chat).
28. Section 1 had 307 words of body against STAGE_E.33.md's cap of 300; session 3 trimmed it to 290 with no number
    changed ("recomputed twice more" became "three more times", counting the StatsReviewer's own recomputation,
    section 5).
29. The full suite was not rerun in session 3. It ran at the end of session 2 (21:02-21:21), and session 3 changed
    only Markdown and text outputs (no code, test or data file), so its result stands.
30. Session cost: cost.py per lead session over that session's own transcript and subagents. Session 3's lead is
    counted to a stated cutoff, so the commit and the last checks after it are not counted (as in E.33b). The final
    table appears in section 8 and in the progress entry, as in E.33b; no estimate table is written to any file.
31. The commit includes reports/stage_e33_briefs/work/logs/search_real_c.log (239 KB, the resumed search's log),
    because search_real.log is tracked. Large outputs stay under derived/e33/. The untracked files of earlier
    stages (most of `git status --short`'s 2,154 lines) are left alone.

## 7. Decisions for the user (each with a recommendation)

1. Accept the clean negative. Then: no E.34 test registration, the 2017-05-01 to 2020-11-30 window stays sealed, and
   no Databento purchase. N stays 838. Recommendation: accept. All 300 registered configurations ran; the decision
   was recomputed from the raw predictions by a second model; no configuration is near a gate.
2. The program's next step. The options:
   - (a) the planned Stage E sequence in docs/STAGES.md (E.3b onward: K2's confirmation session, then one screening
     and one confirmation session per remaining cluster);
   - (b) a new pre-registered directional search on the same ZM discovery dates with other families or horizons.
     Its trials add to N (thresholds rise from SR0 0.1137 at N 838), and the dates are no longer a fresh sample;
   - (c) a second order-flow search on the owned MBO (V50 item 4). E.33's F3 set already covered ZM order flow and
     book state at 5 to 60 minutes and found nothing, and the same N cost applies.
   Recommendation: (a). The minimum edges this search could detect were roughly 1.5 to 4.4 ticks a trade at the
   trade rates seen. The 61 configurations that met G1 lost more than 1.0 tick a trade after costs (the best
   -1.098), and the synthetic null also sits below zero from costs alone. Minute-scale direction on these inputs is far from
   paying for the spread and fee. A further search of the same kind would mostly raise N.
3. E.32 D2 (whether to amend V14 (c) for a test's DSR variance; V52 item 4) has no test to apply to now.
   Recommendation: leave it open, attached to any future test registration, rather than decide it in the abstract.

## 8. Session cost

Computed at 21:43:15 PDT (the cutoff) from the transcripts of the three lead sessions and their subagents (main
.jsonl and subagents/*.jsonl of 7c6136a3, fec9a0d1 and 7ea5755f, 2026-10-28 18:05-21:43 PDT) with
reports/stage_e10_briefs/cost.py (outputs and the three-session sum: reports/stage_e33c_briefs/cost_e33c.txt). These
are token counts, not plan-credit percentages; the commit and the last checks after 21:43:15 are not counted.

Wall clock: 18:05-21:43 PDT, 3 h 38 min. Lead wipe 1 (18:39-19:54, 1 h 15 min) was planned lead downtime while the
search ran, so the stage's work continued and it is counted. Lead wipe 2 (21:22-21:31, 9 min) had nothing running:
a pause, not counted. Usage-limit pauses: none. Work time: 3 h 29 min.

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,936 | 196,238 | 8,651,688 | 632,695 | 9,482,557 |
| claude-haiku-5-5 | 16 | 11,026 | 495,776 | 94,321 | 601,139 |
| claude-opus-5-5 | 580 | 429,682 | 54,153,951 | 1,056,327 | 55,640,540 |
| all | 2,532 | 636,946 | 63,301,415 | 1,783,343 | 65,724,236 |

Worker spawns:
- FoldTimes-HaikuMed: worker-medium, haiku (claude-haiku-5-5), medium, 601,139 tokens
- AmendReviewer-FableXHigh: worker-xhigh, fable (claude-fable-5-1), xhigh, 1,214,370
- StatsCoder-OpusXHigh: worker-xhigh, opus (claude-opus-5-5), xhigh, 13,270,018
- VerifyWorker-FableXHigh: worker-xhigh, fable (claude-fable-5-1), xhigh, 4,849,271
- StatsReviewer-FableXHigh: worker-xhigh, fable (claude-fable-5-1), xhigh, 3,418,916

Lead sessions (opus, claude-opus-5-5, max effort from 18:10): 7c6136a3 16,501,417; fec9a0d1 19,156,706; 7ea5755f
6,712,399 (to the cutoff).

Delegation share: lead 42,370,522 (64.5%), workers 23,353,714 (35.5%). By model: Opus 55,640,540 (84.7%), Fable
9,482,557 (14.4%), Haiku 601,139 (0.9%). Cache reads are 96.3% of all tokens. The lead at max effort used 42.4M
tokens over 3 h 29 min of work that was mostly compute and review; E.33b's xhigh lead used 76.8M over 5 h 30 min of
build work, so the two are not like for like.

Final table (times PDT, from STATE, logs and transcripts; tokens from the transcripts):

| # | Task / agent | Model (effort) | Start-end | Time | Tokens | Status, deviations |
|---|---|---|---|---|---|---|
| 1 | Lead session 1: prompt, V53-V55, routing, plan | opus (xhigh; max from 18:10) | 18:05-18:10 | 5 min | (lead) | done |
| 2 | c1 S1 start gates | lead, opus (max) | 18:10:31-18:16 | 6 min | (lead) | done: all pass; no outcome opened |
| 3 | c2a FoldTimes-HaikuMed | haiku-5-5 (medium) | 18:17:42-18:18:33 | 1 min | 601,139 | done: 448 rows, equal to the lead's parse |
| 4 | c2b 0.3 text, method script, R_0.3, diff | lead, opus (max) | 18:19-18:27 | 8 min | (lead) | done |
| 5 | c2c AmendReviewer-FableXHigh | fable-5-1 (xhigh) | 18:22:52-18:34:08 | 11 min | 1,214,370 | GO: 0 BLOCKING, 0 SHOULD FIX, 9 NOTE |
| 6 | c2d 0.3 stop watcher | lead, opus (max) | 18:30-18:32 | 2 min | (lead) | done |
| 7 | c2e hash 0.3, ledger line, freeze verify | lead, opus (max) | 18:34-18:36 | 2 min | (lead) | done; 0 differences |
| 8 | c3 resumed search (lead-run, detached) | - | 18:36:14-20:37:27 | 2 h 01 min | - | 300/300, 0 failed; 0.39 of the 3x stop |
| 9 | Lead wipe 1 (planned; the search ran) | - | 18:39-19:54 | 1 h 15 min | - | lead downtime, counted (open choice 13) |
| 10 | Lead session 2: resume, checks, Part D briefs, end-of-search tool | opus (max) | 19:54-20:37 | 43 min | (lead) | done |
| 11 | c4 step-5 end-of-search checks | lead, opus (max) | 20:38:15-20:38:26 | under 1 min | (lead) | done: 300/300 DONE, 0 failed; seal lifted |
| 12 | c5 select33, P8 (frozen script, lead-run) | - | 20:38:50-20:38:54 | 4 s | - | Tier A empty; branch N |
| 13 | c6 StatsCoder-OpusXHigh | opus-5-5 (xhigh) | 20:39:48-20:57:50 | 18 min | 13,270,018 | done: D1, D3, P10 (i)-(vi); 28 tests pass |
| 14 | c7 VerifyWorker-FableXHigh | fable-5-1 (xhigh) | 20:39:56-20:59:46 | 20 min | 4,849,271 | CONFIRMED; read a stdout headline first (disclosed) |
| 15 | Lead: return draft (interleaved) | opus (max) | 20:41-21:20 | - | (lead) | done |
| 16 | c8 StatsReviewer-FableXHigh | fable-5-1 (xhigh) | 21:01:33-21:15:38 | 14 min | 3,418,916 | 0 BLOCKING, 4 SHOULD FIX (fixed), 8 NOTE |
| 17 | c8b D5 fixes in the return | lead, opus (max) | 21:16-21:18 | 2 min | (lead) | done |
| 18 | Full pytest suite | - | 21:02:01-21:21:28 | 19 min | - | 1 known failure (h6, v13), as at E.33b's end |
| 19 | Lead wipe 2 (planned; nothing ran) | - | 21:22-21:31 | 9 min | - | pause, not counted |
| 20 | Lead session 3: end checks, return sections 1, 2, 6 and 8, progress, STAGES, cost | opus (max) | 21:31-21:43 (cutoff) | 12 min | (lead) | done; commit and end status after the cutoff |
| all | Stage E.33c | lead (3 sessions) + 5 workers | 18:05-21:43 | 3 h 38 min (3 h 29 min excluding wipe 2) | 65,724,236 (lead 42,370,522; workers 23,353,714) | initial estimates: 18:17 table "finish about 01:30", 20:03 table "about 01:25", 21:33 table (session 3) "about 22:27"; actual: closing steps done 21:43, commit right after |
