# Stage E.33 return: ZM directional signal discovery (run the frozen protocol), stopped at Part B by the deadline

Lead: Opus 5.5 (claude-opus-5-5), effort xhigh, Ultracode on; session 86e80bc3-d62a-42e1-b5fd-5c881ccf8b54.
Launched 2026-10-27 14:31 PDT; this return written 2026-10-28 by 08:45 PDT (times America/Vancouver, from `date`,
file mtimes and transcripts). Prompt: docs/prompts/STAGE_E.33.md. Protocol: reports/stage_e32_discovery_protocol.md
FROZEN v1.0, sha256 c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05 (verified at start and end).

## 1. Summary

E.33 did not reach the search. Two usage limits took 14 h 20 min of the 18-hour window (15:27-02:01, the weekly
limit; 03:15-07:01, the 5-hour limit), and the 40 synthetic proof searches alone needed about 5.7 hours. The stage
stopped, as the prompt orders, after whole parts, with no gate rushed.

- N before and after: 538 and 538. No C1 registration was made: registering would have charged N with 300
  configurations that could not run before the 07:00 cut (Open choice 1).
- Configurations run on real outcomes: none. No label or return statistic of the discovery dates was computed.
- Part A: every start gate passed (156/156 hashes, holdout and soy seal intact, guard refuses 4/4, harness v14).
- Part B, built twice: pipeline A (data layer, 59 features, labels, search engine, P8, synthetic proofs, cost model)
  and an independent implementation B of the features and labels. B3 on 20 seeded dates: labels and sigma agree
  exactly; feature disagreements were traced to 5 causes, ruled and fixed; after the rerun 57 of 59 feature columns
  agree on every row and two residual readings (F3_11, F3_9) await a ruling. B4: LT2-LT6 pass; LT1 and LT7 not run at
  their declared scale.
  B5 (iii): the deflated Sharpe example (0.9004) and Benjamini-Hochberg reproduce; the AFML examples only from
  secondary sources. B5 proofs (synthetic, no real outcome): 36 of
  40 seeds ran: the null put nothing in Tier A in 18 of 18 seeds and the plant entered Tier A in 18 of 18 (the planted
  proof passes: it needs 14 of 20; the null proof needs the last 2 null seeds). B6: fees match E.28; fills match E.31's
  engine.
- B7: MathReviewer (Fable) agrees with both implementations on 16 features and 12 labels recomputed by hand and
  reproduces every threshold; PipelineReviewer (Fable) provisional NOT YET (0 BLOCKING, 3 SHOULD FIX).
- Not done: the freeze, C1, C2, D, E. No null comparison on real data, no finalist, no clean negative: the search
  never ran. E.34 is not drafted and nothing is to be bought.
- Next: a continuation stage (decision D1) that finishes the last proof seeds (about 1 hour), closes B7, freezes,
  registers and runs the search (feature store about 31 minutes, labels, 1,800 fits; the proofs' measured pace puts
  the search at about 2-3 hours).

## 2. Guardrail evidence

Start checks (reports/stage_e33_briefs/checks_start.txt, 2026-10-27 14:35:41 PDT; the untracked-path list of `git
status --short` is in the file):

```
$ git status --short | wc -l
2106
$ git log --oneline -3
835f508 Stage E.32 ZM discovery brief and protocol
3a75f3b docs: Stage E.33 hard deadline 09:00 PDT Wed 2026-10-28
864574b docs: Stage E.33 timing (no fixed end; continues across the weekly reset)
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
$ uv run python -m screening.trial_registry status (N)
r008-E23: E23 ['E23-MEZFh5', 'E23-MEZNh5', 'E23-MEZBh5', 'E23-H6NQh5', 'E23-H6NQh20'] N 533 -> 538 at 2026-10-17T03:33:45-07:00
.env DATABENTO_API_KEY: absent
.env DATABENTO_API_KEY2: absent
.env DATABENTO_API_KEY3: non-empty
$ sha256sum reports/stage_e32_discovery_protocol.md
c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05  reports/stage_e32_discovery_protocol.md
```

A1 discovery data (reports/stage_e33_briefs/verify_discovery_hashes.out, 14:35:54-14:36:23 PDT; verifier sha256
c329f443...): `{"files": 156, "ok": 156, "mismatch": 0, "missing": 0, "problems": []}`; the four manifest.json copies
all hash to 09396842c4fd5d742c166e5b6ca1327c5eeebfed9b112952b84d15f254c23261 (manifest_hashes.txt).

A1 guard dry check (reports/stage_e33_briefs/guard_dry_check_start.txt, 2026-10-27 15:06:47 PDT):
```
[sealed test-window path] REFUSED (P1.2 sealed soy test data): .../data/sealed/SOY_test_v1/data/processed_hist/ext2010h/ZL/ohlcv-1m_ZL_v_0_2010-07-01_2019-04-30_ext2010h.parquet.sealed lies under data/sealed/SOY_test_v1
[test-window date 2019-03-05] REFUSED (P1.2 soy test window): date 2019-03-05 lies in the sealed soy test window 2017-05-01..2020-11-30 (ZM, ZS, ZL)
[date 2024-03-01] REFUSED (P1.2 on or after 2024-03-01): date 2024-03-01 is on or after 2024-03-01
[E.31 runs/ path] REFUSED (P1.2 E.31 measured outputs): .../reports/stage_e31_briefs/work/pilot/runs/measure31 lies under reports/stage_e31_briefs/work/pilot/runs/
dry-check: 4 of 4 refused
rc=0
```
A2: no Databento call of any kind was made (no worker had a reason or a brief to; the loaders read local files only).

End checks (reports/stage_e33_briefs/checks_end.txt, 2026-10-28 07:44:37 PDT; guard dry check again 4 of 4 refused,
rc 0, guard_dry_check_end.txt):

```
$ git status --short (tracked)
 M docs/STAGES.md
$ git log --oneline -3
835f508 Stage E.32 ZM discovery brief and protocol
3a75f3b docs: Stage E.33 hard deadline 09:00 PDT Wed 2026-10-28
864574b docs: Stage E.33 timing (no fixed end; continues across the weekly reset)
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
soy test {'state': 'sealed', 'files_sealed': 114, 'files_ok': 114, 'plaintext_in_window_present': [], 'unlocks_logged': 0, 'all_ok': True}
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m screening.harness_freeze verify --expected 2e908c81...
preflight OK: 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1
$ ledger
37290 ledger/databento_spend.jsonl
42589d7bc02696383cbf5d800ceb922491a4dea90fb2c3d3e2f82da36834c9bb
$ uv run python -m screening.trial_registry status (N)
r008-E23: E23 [...] N 533 -> 538 at 2026-10-17T03:33:45-07:00
.env DATABENTO_API_KEY3: non-empty (by name only)
$ sha256sum reports/stage_e32_discovery_protocol.md
c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05
```
N before and after: 538 and 538 (no registration). Spend ledger unchanged (lines and sha256). Frozen pipeline sha256:
none (no freeze in this stage; the proof run manifest pins its executed code, section 3.4). Full pytest (`uv run pytest -q -p no:cacheprovider`, nice 10, started
07:44:50 PDT with 11,740 MB available, the 2 GB rule met): 1 failed, 8,116 passed, 5 skipped, 3 xfailed in 1,147.87 s
(reports/stage_e33_briefs/pytest_end.log); the one failure is tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha,
the known failure that predates E.32 (E.32 D7), identical to E.32's end result.
No worker, job or shell of this stage runs at the end (checked at 07:44 and before the commit).

Session checks: data.holdout unlocks_logged 0 at 14:35 (start), 02:01 and 07:01 PDT (after each usage limit) and at
the end. No TopstepX, ProjectX or broker call; nothing under live/ or ops/ touched; no key read or printed (keys checked
by name only). Large outputs are under /mnt/large-storage/market_data/PropExperiment/derived/e33/ (split/, features/,
labels/, implB/, proofs/, probes/, b3/), never in git.

## 3. Results

### 3.1 Part B code (pipeline A: reports/stage_e33_briefs/work/pipeline/; implementation B: .../work/implB/)
| Module | Author | Tests | Final code |
|---|---|---|---|
| guard33, data33, cal33, split33, check33, g6_33 | DataCoder | 80 | split ZS 248,167,909 and ZL 158,044,028 records, 816/816 dates each, = raw on 3 dates |
| feat33, build_features33 (Coder-A features) | FeatureCoder | 65 | 6873427a6150 |
| lab33, build_labels33 (Coder-A labels, weights, outcomes) | LabelCoder | 42 | ff0181fc391c |
| search33, run_search33 (folds, LOGIT, LGBM, EV rule, simulation, P6.2) | SearchCoder | 45 | search33 a7d30b2a..., run_search33 d44fb7c1... |
| select33 (P8), synth33 (P4.2 generator), run_proofs33 | ProofCoder | 52 | 9b992806..., 5a5ed5b9..., 4a0f4e98... |
| cost33, test_stats_repro33 | StatsCostCoder | 52 | - |
| implB featB, dayB, replayB, calB (Coder-B features) | FeatureCoder2 | 56 | fb69badd4bb9 |
| implB labB, labB_book, labB_cal (Coder-B labels) | LabelCoder2 | 33 | efdde5c74ee1 |
| tests_b3 (agreement), tests_b4 (leakage), synthetic streams | TestCoder | LT2-LT6 pass; xfail D1/D2 pass | - |

Data facts measured on the way (no outcome involved): P1.4 by the rule excludes 52 of the 816 dates (23 roll dates,
23 dates after a roll, 4 holiday or early close, 5 late opens; 49 of the 796 OOF dates); 54 front segments; the
release calendar asserts exactly 39 WASDE, 39 Crop Production, 4 Annual, 13 Grain Stocks, 3 Prospective Plantings, 3
Acreage, 37 NOPA rows plus 2 NOPA rule dates; limit prices exist on all 816 dates; G6 flags 0 of 39 months (largest
gap between the ZM, ZS and ZL medians of ts_recv - ts_event 0.252 ms). Finding: the Z4 definitions carry new high and
low limit prices only on Sundays, so P3.6 rule 5 as written measures the 2% distance to a band up to 5 days old; on the
20 B3 dates it removed every F05 minute of 2021-07-09, 142 minutes of 2022-06-03 and 82 of 2021-04-01 (decision D3).

### 3.2 B3 agreement (reports/stage_e33_briefs/work/B3_agreement.md)
Dates (rule fixed at 14:45 before any computation: default_rng(20261028).choice(796, 20) over the sorted OOF dates):
2021-01-19, 2021-01-25, 2021-03-11, 2021-03-16, 2021-04-01, 2021-05-04, 2021-07-06 (excluded), 2021-07-09, 2021-07-29,
2021-08-16, 2022-06-03, 2022-09-01, 2022-09-29, 2022-12-13 (excluded), 2022-12-22, 2023-01-11, 2023-02-16, 2023-04-10,
2023-08-11, 2024-02-15.
- First run (full_r1, 02:21): labels F05..T30 (5,460 / 5,260 / 4,960 / 4,360 / 5,260 / 4,960 rows): 0 disagreeing cells
  in all 19 compared columns. sigma_ZM, ZS, ZL: 0. Features: 35,473 cells in 34 of 59 columns, every one explained by
  FD1 (early closes), FD2 (late opens), FD3 (OFI terms at the pause junction and at invalid states), FD4 (refills), FD5
  (removals). Rulings R-B3-* (reports/stage_e33_protocol_readings.md): FD1, FD2, FD4, FD5 for Coder-B's literal
  reading (fixed in A); FD3 (a) a new reading both sides implement, (b) and (c) for A (fixed in B); latent label
  readings D1, D2 for B's conservative side (fixed in A; the 20-date labels are unchanged in every column).
- Rerun on the fixed builds (full_r2, 07:02; Coder-A features 6873427a6150, Coder-B fb69badd4bb9, labels A ff0181fc391c):
  labels 0 disagreeing cells in all six labels; sigma_ZM, ZS, ZL equal on all 20 dates; features 57 of 59 columns agree on
  every row. Residual: FD6, F3_11 on 5,385 cells (a single record that is partly fill and partly cancel opens a refill
  window under Coder-B's rule, not Coder-A's; about one refill a day; feat33.py 493-513 against replayB.py 140-154;
  PipelineReview SF3); FD7, F3_9 on 10 cells of 2022-09-01 (a fill naming an order not yet in the book: Coder-A counts the
  order's later cancel as a removal, Coder-B counts the lots as fills). Both await a lead ruling, a fix and a rerun in the
  continuation; B3 is therefore not passed.

### 3.3 B4 leakage tests (reports/stage_e33_briefs/work/B4_leakage.md)
- LT2 (spans), LT3 (fold hygiene and the 21-date embargo against every span and look-back), LT4 (ts_recv clock), LT5 (the
  leak canary is caught and scores absurdly), LT6 (one guard test per refused class): passed.
- Record-level synthetic streams for 30 trade dates through both builders: all 59 feature columns agree.
- LT1 (200 truncation draws, seed 20261027): only a 5-draw timing probe ran (the usage limit cut the run); Coder-A's
  3-time and Coder-B's 9-time self-checks matched exactly on earlier builds. Not passed at the declared scale.
- LT7 (seed-1 null fold models on real feature rows): 50 of 50 decisions and 11 of 11 fills equal on 3 usable draws, on a
  superseded feature build; the full run (run_lt1_lt7.py, about 50 minutes) is left to the continuation.

### 3.4 B5 synthetic proofs and published examples
(iii) reports/stage_e33_briefs/work/pipeline/tests/test_stats_repro33.py: Bailey and Lopez de Prado (2014) pp. 9-10
reproduced to the 4 printed decimals (threshold 0.1132, DSR 0.9004, 0.9505 at N 46 and at N 88) in both
funnel.multiple_comparisons and screening.stage_e_verdict; Benjamini-Hochberg's 15 p-values (BH rejects 4, threshold
0.013; Bonferroni 3; Holm 3); CSCV split counts exact (the paper's printed 12,780 for S = 16 is a misprint of 12,870,
confirmed on the rendered page); AFML's uniqueness toy example and the purged-CV construction reproduced only from
secondary or author-restated sources (the book was not obtained).
(i), (ii) the production proofs (S5 x {F15, T30} x 10 grid points per seed, thresholds at N 838; 02:36 PDT onward,
detached, stopped at a seed boundary at 07:44:02 PDT for the deadline; reports/stage_e33_briefs/work/B5_proofs.md):
36 of 40 seeds ran (null 1-18, planted 101-118), 0 failed configurations in any seed. Null: Tier A empty in 18 of 18; in
every null seed G1 passed 5-10 of the 20 configurations and G2 (0.50 tick net per trade) passed none; best SR_d per seed
from -0.0757 to 0.0602 (median 0.0058); the SD of the 360 null daily Sharpes, each centred on its configuration's mean,
is 0.0425 (df-corrected 0.0437) against the 1/sqrt(796) = 0.0354 reference (P4.2 asks for the report; it is not a
criterion). The null proof fails at 2 or more of 20 non-empty seeds; 0 of 18 so far, so seeds 19 and 20 decide nothing
unless both fill Tier A. Planted: Tier A non-empty in 18 of 18 (pass at 14 of 20: passed); the best planted
configuration's SR_d sits beside the oracle's (mean oracle 0.3435 on the seeds' own series); S5F15L001E entered Tier A
in most seeds and no T30 configuration ever did. Not run: seeds 19, 119, 20, 120 (seed 19 had started when the job
stopped; its started folds carry one interruption each, which P5 allows to rerun once). Every seed ran exactly once, under run-manifest
code hashes and library versions that a resume must match (R-L3). The planted signal: F3_4, beta 0.367 ticks per
minute per unit, calibrated so the P3.5 oracle has a mean daily Sharpe of 0.3498 (se 0.0048) at F15.

### 3.5 B6 cost and fill model
cost33.py: E.28's fees agree with the protocol's P6.4 list and P0.3's f with no difference (Topstep 0.528, Lucid 0.560
or 0.920, Bulenox 0.572, MFFU 0.612, Tradeify 0.920 ticks); on hand-built sequences E.31's own engine and cost33 make
the same fill decisions on 10 orders and per-fill nets agree to 1e-9 for 5 firms at 3 horizons.

### 3.6 Search distribution, selection table, robustness, finalists
Not run (no registration; section 1).

## 4. Delegation record

Every model below is read from the agent's own transcript (message.model), never a self-report (V50 item 5).

| # | Agent (role) | Agent file | Model (transcript) | Effort | Active (PDT) | Tokens | Status |
|---|---|---|---|---|---|---|---|
| 1 | DataCoder-OpusXHigh (guard, loaders, calendar, split, G6) | worker-xhigh | claude-opus-5-5 | xhigh | 10-27 14:46-15:08 | 13,158,272 | done |
| 2 | FeatureCoder-OpusXHigh (Coder-A features) | worker-xhigh | claude-opus-5-5 | xhigh | 14:46-15:27; 02:02-03:15; 07:02-07:05 | 37,931,731 | done (cut twice, resumed) |
| 3 | LabelCoder-OpusXHigh (Coder-A labels) | worker-xhigh | claude-opus-5-5 | xhigh | 14:46-15:06; 15:20-15:25; 02:44-02:47 | 16,739,870 | done |
| 4 | FeatureCoder2-OpusXHigh (Coder-B features) | worker-xhigh | claude-opus-5-5 | xhigh | 14:46-15:27; 02:02-03:15; 07:02-07:04 | 39,432,011 | done (cut twice, resumed) |
| 5 | LabelCoder2-OpusXHigh (Coder-B labels) | worker-xhigh | claude-opus-5-5 | xhigh | 14:46-15:16 | 13,659,953 | done |
| 6 | SearchCoder-OpusXHigh (search engine) | worker-xhigh | claude-opus-5-5 | xhigh | 14:46-15:27; 02:02-02:25 | 31,622,898 | done (cut, resumed; SF1-SF4 fixed) |
| 7 | ProofCoder-OpusXHigh (P8, generator, proof runner) | worker-xhigh | claude-opus-5-5 | xhigh | 15:06-15:27; 02:02-02:36 | 25,938,872 | done (cut, resumed; SF1-SF2 fixed) |
| 8 | StatsCostCoder-OpusXHigh (B5 iii, B6) | worker-xhigh | claude-opus-5-5 | xhigh | 15:08-15:27; 02:02-02:03 | 20,268,814 | done (cut, resumed) |
| 9 | TestCoder-OpusXHigh (B3, B4) | worker-xhigh | claude-opus-5-5 | xhigh | 15:16-15:27; 02:02-03:15; 07:02-07:05 | 74,650,269 | done (cut twice; LT1, LT7 not at scale) |
| 10 | SearchReviewer-OpusXHigh (pre-proof review) | worker-xhigh | claude-opus-5-5 | xhigh | 10-28 02:03-02:16 | 8,681,813 | done |
| 11 | ProofReviewer-FableXHigh (pre-proof review) | worker-xhigh | claude-fable-5-1 | xhigh | 02:18-02:32 | 4,059,346 | done |
| 12 | MathReviewer-FableXHigh (B7) | worker-xhigh | claude-fable-5-1 | xhigh | 02:18-02:42 | 5,182,542 | done |
| 13 | PipelineReviewer-FableXHigh (B7) | worker-xhigh | claude-fable-5-1 | xhigh | 03:08-03:15; 07:02-07:03 | 7,309,863 | provisional NOT YET (cut, resumed for a wrap-up) |
| - | lead, session 86e80bc3 | - | claude-opus-5-5 | xhigh | 14:31-15:27; 02:01-03:15; 07:01-end | 59,837,014 (to 07:45) | - |

Routing: coders on Opus xhigh, reviewers on Fable xhigh (the prompt's table), the extra pre-proof search review on Opus
xhigh in a fresh context. No Sonnet and no Haiku ran; no Fable fallback was needed (every Fable reviewer's transcript
shows claude-fable-5-1). No worker spawned another worker. The `<synthetic>` messages in the transcripts are the
zero-usage usage-limit stubs. Active intervals come from the transcripts' first and last records and the STATE file.

## 5. Verification

| Check | Object | Reviewer (model from transcript) | Result |
|---|---|---|---|
| SearchReview (pre-proof, extra to B7) | search33, run_search33 | SearchReviewer-OpusXHigh (claude-opus-5-5) | 0 BLOCKING, 4 SHOULD FIX (DONE markers without a code hash; infrastructure errors counted as failed fits; collateral kills charged; load-phase kills uncharged), 10 NOTE; all 4 fixed before the proofs (45 tests); probes confirmed the LightGBM stopping metric to 1.6e-10 and probabilities to 2e-16 |
| ProofReview (pre-proof) | select33, synth33, run_proofs33 | ProofReviewer-FableXHigh (claude-fable-5-1) | 0 BLOCKING, 2 SHOULD FIX (failed configurations hidden in the summary; library versions not pinned), 11 NOTE; both fixed before the proofs; P8 matches the protocol argument by argument; no look-ahead in the generator |
| B7 MathReviewer | 10+ features, 10+ labels by hand; B5 arithmetic | MathReviewer-FableXHigh (claude-fable-5-1) | 16 features agree with A and B within G7; 12 labels, 5 exclusion-flag minutes and 6 weights exact with both; SR0 0.113653, G3 0.172422, b_test 0.164882, G4 0.200703, binomials 0.2642 and 0.9133, analytic rates, the oracle reproduced; 0 BLOCKING, 1 SHOULD FIX (= FD3), 6 NOTE |
| B7 PipelineReviewer | B1-B6, code and evidence | PipelineReviewer-FableXHigh (claude-fable-5-1) | provisional NOT YET: 0 BLOCKING, 3 SHOULD FIX (the readings file is a draft; the freeze list must add the program modules; F3_11 mixed fill-plus-cancel record), 10 NOTE; 333 tests run, 0 failures; not reached: the full B3 rerun, LT1/LT7, the last proof seeds |

No number enters a verdict in this stage (nothing was searched); the proof figures are synthetic.

## 6. Open choices

1. No C1 registration. At 02:01 PDT about 6 hours remained and the full budget needed the proofs (measured later at
   about 5.7 hours), B7 and the freeze first; registering would have raised N by 300 for configurations that could not
   run before the 07:00 cut. The conservative choice keeps N at 538 and leaves the registration to a stage that can run
   the budget.
2. B5's production proofs ran detached through the second usage limit and were stopped at a seed boundary for the
   deadline; the remaining seeds run once each in the continuation under the same pinned code and versions (R-L3).
3. Coders ran as Agent-tool workers (resumable for fix briefs); fan-out reviews as single agents, not workflows.
4. B3 dates rule fixed before any computation (R-L5).
5. Compute: at most 2 heavy jobs, at most 10 threads in all; the proofs at the P5 cap of 8 processes; nice 10.
6. The P5 probe runs on a production-size synthetic table, not real outcomes (R-L1).
7. Label values on real dates appear only inside equality checks (R-L2).
8. Proof reruns are keyed to the hashes of the code the proofs execute (R-L3); the planted pass rule is per seed
   (R-L4); the test window is P9's 2017-05-22 (R-L6); LightGBM early stopping uses the declared metric in float64
   (R-L7); Tier B continues from where Tier A stopped (R-L8).
9. B3 rulings R-B3-FD1 to FD5 and D1 to D5 (section 3.2).
10. Two pre-proof reviews were added (SearchReview, ProofReview), beyond the prompt's B7, because a defect found
    after the proofs start forces all 40 to rerun.
11. A `mid_move` column was added to the label table for P6.2's reported-only mid-sign hit rate (never used by P8).
12. 21 DataCoder readings accepted (DG-1..5, DATA-1..6, CAL-1..8, G6-1..2), among them the guard's refusal of every
    date outside 2020-12-01..2024-02-29 and C.7's count of dates T with D < T <= expiry.
13. The B3 residuals FD6 and FD7 and the PipelineReviewer's 3 SHOULD FIX items are left open rather than ruled without
    their code-level diagnosis in the last hour; the readings file stays DRAFT.
14. The proof job was stopped at the first seed boundary after 07:40 (07:44:02) so the work stop at 08:00 held and the
    end checks and suite could run; four seeds remain.

## 7. Decisions for the user (each with a recommendation)

D1. Launch a continuation stage (E.33b) to finish this protocol run: the last proof seeds (about 1 hour, once each,
    same code), the B3 rerun with the F3_11 ruling, LT1 and LT7, the PipelineReviewer's remaining scope and its 3 SHOULD
    FIX items, the readings file final, the freeze, C1 (N 538 -> 838), the feature store (about 31 minutes), the labels,
    the 1,800 fits (about 2-3 hours at the proofs' pace), D1-D5 and E. Recommendation: launch it in a window of at least
    10 hours with usage headroom (two limits cost this stage 14 h 20 min), and keep the frozen protocol unchanged.
D2. E.32's D1 (keep or drop the protocol-added test DSR) is still pending and must be recorded before E.33b's C1.
    Recommendation: keep (E.32's reasoning stands).
D3. Price-limit staleness (section 3.1): rule 5 as written uses a limit band refreshed only on Sundays. Recommendation:
    keep the rule for discovery (it only removes rows, never adds them; the protocol is frozen), have E.33b count the
    affected dates and minutes on all 796, and decide before any test registration whether the test stage should use
    exchange daily limits from another source (a protocol amendment, decided before the test is registered).
D4. The AFML worked examples were reproduced only from secondary sources. Recommendation: accept for E.33b; obtain the
    book only if a reviewer asks.
D5. DATABENTO_API_KEY3 is still non-empty in .env (start check; E.32's D5). Recommendation: remove it.
D6. The one suite failure is E.32's D7 (test_h6 pinned to an old harness hash). Recommendation: as E.32 said, re-pin it
    to the current harness or mark it xfail with the reason, in a small separate change.

## 8. Session cost

Tokens come from this session's transcripts (the lead's .jsonl and all 13 subagent transcripts under
~/.claude/projects/-home-kiros-li-Documents-GitHub-PropExperiment/86e80bc3-d62a-42e1-b5fd-5c881ccf8b54/subagents/), each
assistant message counted once at its final usage, by reports/stage_e33_briefs/work/lead/deleg33.py at 07:45:19 PDT
(output reports/stage_e33_briefs/work/lead/deleg33_final.md); the lead's calls after 07:45 (filling this return, the
progress entry and the commit) are not counted. Token counts, never estimates; plan-meter percentages are the user's
reading.

Wall clock: 2026-10-27 14:31 to 2026-10-28 08:05 PDT, 17 h 34 min. Pauses, not work: USAGE LIMIT 1 (weekly)
15:27-02:01 (10 h 34 min); USAGE LIMIT 2 (5-hour) 03:15-07:01 (3 h 46 min); 14 h 20 min in all. Work: 3 h 14 min
(14:31-15:27, 02:01-03:15, 07:01-08:05). The detached proof job ran 02:36-07:44 (5 h 8 min), through the second pause.

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-opus-5-5 | 2,552 | 2,054,619 | 328,998,084 | 10,866,262 | 341,921,517 |
| claude-fable-5-1 | 2,495 | 242,370 | 15,026,681 | 1,280,205 | 16,551,751 |
| all | 5,047 | 2,296,989 | 344,024,765 | 12,146,467 | 358,473,268 |

Delegation share: lead 59,837,014 (16.7%), workers 298,636,254 (83.3%): Opus workers 282,084,503 (78.7% of all),
Fable workers 16,551,751 (4.6%). Cache reads are 96.0% of all tokens. Per worker spawn (agent file, model, effort,
tokens): section 4. No max effort was used. The largest consumer was the TestCoder (74.7 M), whose context held both
implementations.

Final table (times PDT; tokens by transcript):

| # | Task / agent | Model (effort) | Start-end | Time | Tokens | Status, deviations |
|---|---|---|---|---|---|---|
| 1 | Lead: start checks, A1 hashes, reading, plan | opus (xhigh) | 10-27 14:31-14:37 | 6 min | (lead) | done |
| 2 | Lead: INTERFACE, STATE, 9 briefs, estimate table, readings draft, C1 builder | opus (xhigh) | 14:37-14:56 | 19 min | (lead) | done |
| 3 | DataCoder-OpusXHigh | opus-5-5 (xhigh) | 14:46-15:08 | 22 min | 13,158,272 | done |
| 4 | FeatureCoder-OpusXHigh | opus-5-5 (xhigh) | 14:46-07:05 (active about 1 h 57 min) | about 1 h 57 min | 37,931,731 | done; cut twice |
| 5 | LabelCoder-OpusXHigh | opus-5-5 (xhigh) | 14:46-02:47 (active about 28 min) | about 28 min | 16,739,870 | done |
| 6 | FeatureCoder2-OpusXHigh | opus-5-5 (xhigh) | 14:46-07:04 (active about 1 h 56 min) | about 1 h 56 min | 39,432,011 | done; cut twice |
| 7 | LabelCoder2-OpusXHigh | opus-5-5 (xhigh) | 14:46-15:16 | 30 min | 13,659,953 | done |
| 8 | SearchCoder-OpusXHigh | opus-5-5 (xhigh) | 14:46-02:25 (active about 1 h 4 min) | about 1 h 4 min | 31,622,898 | done; cut once |
| 9 | Lead: A1 guard dry check, wave-2 spawns, readings review | opus (xhigh) | 15:06-15:27 | 21 min | (lead) | done |
| 10 | ProofCoder-OpusXHigh | opus-5-5 (xhigh) | 15:06-02:36 (active about 55 min) | about 55 min | 25,938,872 | done; cut once |
| 11 | StatsCostCoder-OpusXHigh | opus-5-5 (xhigh) | 15:08-02:03 (active about 20 min) | about 20 min | 20,268,814 | done; cut once |
| 12 | TestCoder-OpusXHigh | opus-5-5 (xhigh) | 15:16-07:05 (active about 1 h 27 min) | about 1 h 27 min | 74,650,269 | done; cut twice |
| 13 | USAGE LIMIT 1 (weekly) | - | 15:27-02:01 | 10 h 34 min | - | not work |
| 14 | Lead: resume, estimate table, reviews, B3 rulings, proof launch | opus (xhigh) | 02:01-03:15 | 1 h 14 min | (lead) | done |
| 15 | SearchReviewer-OpusXHigh | opus-5-5 (xhigh) | 02:03-02:16 | 13 min | 8,681,813 | done |
| 16 | ProofReviewer-FableXHigh | fable-5-1 (xhigh) | 02:18-02:32 | 14 min | 4,059,346 | done |
| 17 | MathReviewer-FableXHigh | fable-5-1 (xhigh) | 02:18-02:42 | 24 min | 5,182,542 | done |
| 18 | Production proofs (detached job, 8 processes) | - | 02:36-07:44 | 5 h 8 min | - | 36 of 40 seeds; stopped for the deadline |
| 19 | PipelineReviewer-FableXHigh | fable-5-1 (xhigh) | 03:08-03:15; 07:02-07:03 | about 8 min | 7,309,863 | provisional NOT YET |
| 20 | USAGE LIMIT 2 (5-hour) | - | 03:15-07:01 | 3 h 46 min | - | not work |
| 21 | Lead: wrap-ups, proof stop, end checks, pytest, return, progress, STAGES, commit | opus (xhigh) | 07:01-08:05 | 1 h 4 min | (lead) | done |
| - | Lead session 86e80bc3, whole | opus 5.5 (xhigh) | 14:31-08:05 | - | 59,837,014 (to 07:45) | - |
| total | Stage E.33 | - | 10-27 14:31-10-28 08:05 | work 3 h 14 min (pauses 14 h 20 min) | 358,473,268 (to 07:45) | initial estimate (14:47): return by 07:30 with the full search; revised (02:03): Part B by 06:45, C not run |
