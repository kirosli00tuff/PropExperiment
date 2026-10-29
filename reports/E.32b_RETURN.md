# Stage E.32b return: directional rerank of the firm-contract pairs; one ZL build candidate

Prompt docs/prompts/STAGE_E.32b.md (sha256 2416a1fa...). Spec reports/stage_e32b_ranking_spec.md (31,068 bytes,
sha256 09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635), hashed at 22:32:14 PDT on 2026-10-28 before
any new lookup or score; unchanged since (re-hashed at each session start and by both reviewers). Deliverables:
reports/stage_e32b_ranking.md, reports/stage_e32b_holding_scope.md, reports/stage_e32b_recommendations.md (the main
output), this file. STATE reports/stage_e32b_STATE.md; rulings and open choices reports/stage_e32b_briefs/RULINGS.md.
Four lead sessions (Opus 5.5, max effort), split by three planned context wipes and one usage-limit pause. All times
PDT (America/Vancouver).

## 1. Summary

E.32b reranked the firm-contract pairs for directional one-lot strategies under a new two-layer spec (hashed
09ebe697...), with blind ratings of a masked fact table, E.28's economics rerun for market orders, and Fable reviews.
No outcome was read; N stays 838.

Top 10 pairs (S): Bulenox YM 3.113, Topstep MNQ 3.096, Tradeify MNQ 3.087, Tradeify YM 3.081, Topstep YM 3.055, MFFU
YM 3.026, Bulenox RTY 3.017, MFFU MNQ 3.014, Topstep RTY 3.009, Tradeify RTY 2.994. YM is in the top 5 of all 28
variants.

Holding: every top-15 pair's band is 15-30 minutes, except MFFU MYM (30-60) and Topstep ZL (15-60); cost and power per
trade are best at 30 minutes in every pair, and so is the edge needed to reach USD 10,000 in 250 days. The prior holds
for minutes, not hours: no band reaches 120 minutes, and no prop firm allows overnight holds.

Landing: ZL ranks 15 (Topstep), the only top-15 product with a clean (sealed) test window; ZM 24, its directional
route closed (E.33c); QM fails Layer 1 (D4 = 0, a satellite of CL); MGC 58 (crowded, D2 = 0); MNQ 2 (not a
satellite), MYM 14, M2K 20, the other micros 48-100 or unlisted.

Next products after ZM: the Dow, Nasdaq-100 and Russell index futures, then soybean oil and natural gas.

Builds (prior of passing a sealed test): one ZL program at Topstep, F10 order-book state plus F09 soy-complex
lead-lag on the single sealed read 2017-05..2020-11, about 4%; MNQ F08, YM F08 and the EQ3 F08 pool under 1% (YM 1.5%
only if V31 were narrowed). Kill: V31's cost gate kept (not run), the discovery gate fails, net edge below the test's
1.8-tick detectable edge, or the sealed test fails. Stop rule: at most one more registered build.

## 2. Guardrail evidence

Start checks (22:22:50 PDT 2026-10-28) and end checks (09:43:24 PDT 2026-10-29) by reports/stage_e32b_briefs/checks.sh,
quoted verbatim from checks_start.txt and checks_end.txt, except that each `git status --short` listing is replaced by
its counts plus every tracked change and every line naming E.32b (OC-23; the full listings are in the two files). Keys
are checked by name only; no key value was read, printed or logged.

Start:

```
# E.32b checks: start
$ date
Wed Oct 28 22:22:50 PDT 2026
$ git status --short
[2148 lines: 2148 untracked, 0 tracked changes; quoted below: every tracked change and every line naming E.32b (1)]
?? reports/stage_e32b_briefs/
$ git status --short | wc -l
2148
$ git log --oneline -3
3a8edf0 docs: Stage E.32b adds build recommendations (step 3b) as its main output
3efe70b docs: V56 (ZM clean negative accepted) and Stage E.32b updated with the holding-time scope
2661261 Stage E.33c ZM discovery search (completion)
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ uv run python reports/stage_e32_briefs/seal/soy_test_seal.py status (keys)  [the E.32 test seal]
soy test {'state': 'sealed', 'files_sealed': 114, 'files_ok': 114, 'plaintext_in_window_present': [], 'unlocks_logged': 0, 'all_ok': True}
$ guard33.py dry-check  [E.33 test-seal read guard: must refuse every forbidden read]
dry-check: 4 of 4 refused
rc=0
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
$ trial registry: current_n and last entry (N)
current_n 838 | registrations 10 | last r009-E33 538 -> 838 2026-10-28T14:23:13-07:00
$ sha256sum ledger/trial_registrations.jsonl
11777e468fa6f2db9e7d7da16bd57681a985b9370c8e6058f8dd6ae8bd75f24c
.env DATABENTO_API_KEY: absent
.env DATABENTO_API_KEY2: absent
.env DATABENTO_API_KEY3: non-empty
$ ls reports | grep -c stage_e32b
1
```

End:

```
# E.32b checks: end
$ date
Thu Oct 29 09:43:24 PDT 2026
$ git status --short
[2156 lines: 2155 untracked, 1 tracked changes; quoted below: every tracked change and every line naming E.32b (9)]
 M docs/STAGES.md
?? reports/E.32b_RETURN.md
?? reports/stage_e32b_STATE.md
?? reports/stage_e32b_briefs/
?? reports/stage_e32b_holding_scope.md
?? reports/stage_e32b_ranking.md
?? reports/stage_e32b_ranking_spec.md
?? reports/stage_e32b_ranking_spec.sha256
?? reports/stage_e32b_recommendations.md
$ git status --short | wc -l
2156
$ git log --oneline -3
3a8edf0 docs: Stage E.32b adds build recommendations (step 3b) as its main output
3efe70b docs: V56 (ZM clean negative accepted) and Stage E.32b updated with the holding-time scope
2661261 Stage E.33c ZM discovery search (completion)
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ uv run python reports/stage_e32_briefs/seal/soy_test_seal.py status (keys)  [the E.32 test seal]
soy test {'state': 'sealed', 'files_sealed': 114, 'files_ok': 114, 'plaintext_in_window_present': [], 'unlocks_logged': 0, 'all_ok': True}
$ guard33.py dry-check  [E.33 test-seal read guard: must refuse every forbidden read]
dry-check: 4 of 4 refused
rc=0
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
$ trial registry: current_n and last entry (N)
current_n 838 | registrations 10 | last r009-E33 538 -> 838 2026-10-28T14:23:13-07:00
$ sha256sum ledger/trial_registrations.jsonl
11777e468fa6f2db9e7d7da16bd57681a985b9370c8e6058f8dd6ae8bd75f24c
.env DATABENTO_API_KEY: absent
.env DATABENTO_API_KEY2: absent
.env DATABENTO_API_KEY3: non-empty
$ ls reports | grep -c stage_e32b
7
```

Also at the end (09:43:30): `uv run python -m data.holdout status` printed "unlocks_logged": 0 in all 6 of its entries;
the no-process check `ps -eo args | grep -E 'econ32b|run_real|f5_holding|score32b|r3_score' | grep -vc grep` printed 0;
no worker was running (all 38 spawns had reported complete). Reading: no unlock anywhere (holdout; the E.32 soy test
seal, 114 of 114 files sealed; the E.33 guard refusing 4 of 4 forbidden reads); REGISTRATION.md 0 bytes; the harness
freeze 2e908c81 preflight OK at both ends; the spend ledger unchanged (37,290 lines, 42589d7b; no Databento call); N
838 unchanged (trial registry 11777e46 at both ends); no tracked file changed but docs/STAGES.md (this stage's line;
progress.md is written after these checks); the untracked entries grew by exactly this stage's 7 report files
(2,148 to 2,155): no tracked E.32 or E.33 file changed and no new file appeared outside this stage's paths. No TopstepX, ProjectX or broker call; nothing under live/ or
ops/ touched; nothing pushed.

## 3. Results

### 3.1 Spec, facts and volatility statistics

- Spec: two layers as the prompt sets them (weights unchanged; spec section 1), E.28's F dropped, the trade-through
  rule assumed everywhere, S = 0.5 L1 + 0.5 L2, E.28's unknown rules unless the spec says otherwise, the R3 rule for the
  combinations (spec 8) hashed with it.
- F1/F2 facts: eight family readers (crude, natgas, metals, grains, rates, equity, FX, crypto; Opus high), FirmRules
  (Opus high), DataAccess (Sonnet high) and AttentionCounter (Haiku) under one shared reader brief (terms read first,
  never CME's site by automation, pointers labelled). S qualifies at 1 tick for 13 codes (CL NG QG GC HG SI ZC ZS ZF ZN ZB 6E 6A: means, time-weighted means
  or hourly means all below 1.5 ticks, or one-tick statements), and every other code takes S = 1 (u) (LR-S); a sourced
  touch exists for 5 (NG 5, QG 10, MNG 3, GC 4.62, SI 6.56 contracts).
- F3 (VolCoder): 47 codes, 22 from owned one-minute bars, 17 by OC-1 sibling transfer, 8 with sigma unknown (SI, SIL,
  MET, ETH; 2YY, 5YY, 10Y, 30Y, yield-quoted), all in E.28's standard window 2022-11-01..2023-10-31, day session; the
  holdout status and the E.32 test-seal guard were checked before and after, and the RankingReviewer reran three roots
  (MCL, 6E, ZC) byte for byte (opens.log: only the 12 window months, 0 refusals).
- F4 (FactTable): 47 codes, 5 firms, 235 pairs (126 listed on a modelled 50K plan, 109 not); masked sheets FINAL3 after
  the FactAuditor's two blinding failures (B1 Lucid plan names, B2 the MFFU name) were patched without relabelling;
  blind ratings by a fresh rater on FINAL3 (329 contract, 470 pair, 20 firm ratings); the first rater, cut by the usage
  limit and possibly exposed to B1, is kept only for inter-rater agreement (302/329 exact; D6 23/47).

### 3.2 The ranking (reports/stage_e32b_ranking.md)

- Layer 1: 35 of 47 codes survive; 11 fail (8 on unknown sigma_60, 3 on D4 = 0: QG, QM, XW); none fails sigma_60 <
  2 x c_RT; 8 survivors have L1 < 2.00 (flagged, not gated); NQ is excluded (V49).
- Layer 2 and S: 103 of the 126 listed pairs are ranked. Top 10: 1 Bulenox YM 3.113, 2 Topstep MNQ 3.096, 3 Tradeify
  MNQ 3.087, 4 Tradeify YM 3.081, 5 Topstep YM 3.055, 6 MFFU YM 3.026, 7 Bulenox RTY 3.017, 8 MFFU MNQ 3.014, 9 Topstep
  RTY 3.009, 10 Tradeify RTY 2.994. The top 15 hold only YM, MNQ, RTY, MYM and ZL (Topstep ZL 15). MNQ, the baseline,
  ranks 2 at Topstep, 3 at Tradeify, 8 at MFFU, 12 at Lucid and 18 at Bulenox; its top-5 places rest on its D6 = 3
  (with the rater's alternative 0, RS-MNQD6, its best rank is 13).
- Variants (28 runs): the top-5 products are always within {YM, MNQ, RTY}; YM is in every top 5 and first in 23 (the
  exceptions put Topstep MNQ first: slip1, mad, D1_all, RL-KZM, RS-RELTOP0). RL-KZM (LR-D1's k ratio) is the only
  lead-ruling variant that changes the top 5 (order only) and is kept (spec 5).
- Against E.28: E.28's v2 top five (QM at all five firms) fail Layer 1 here (D4 = 0). ZM falls from 6th (Topstep) to
  24th: its limit is volatility against cost (r_60 = 0.067, band 2; m* 0.071-0.093 sigma_60, E 2.24-2.66 against
  3.27-3.59 for the equity pairs). ZL: rank 15 at Topstep (S 2.901), 21-38 elsewhere. MGC: rank 58 (MFFU), D2 0 from
  GC's crowding facts and D4 2 (a satellite: GC has 30.4x its notional ADV). The micros: MNQ is not a satellite (NQ/MNQ
  notional ratio 3.86 < 5); MYM (14-70) and M2K (20-76) are satellites (Sat 1) with their leaders' D2; MCL 48-90; MNG
  85; MBT, M6A, M6E and MHG rank 92-103 with E = 0 (a threshold above the grid cap; MFFU M6E 0.35); the micro grains, XC and XK pass
  Layer 1 but are listed on no firm's 50K plan.
- The next products after ZM, by underlying with micros under their leaders: the Dow (YM 1, MYM 14), the Nasdaq-100
  (MNQ 2), the Russell 2000 (RTY 7, M2K 20), soybean oil (ZL 15), natural gas (NG 19, MNG 85).
- Session 4 (RV1 S1, S3): the tie-break cost now reads the market case, as ruled; the score was rerun at 08:51:03 with
  no score, gate or rank change, table 3a shows both cost cases, and 8 econ searches whose bisection did not confirm
  (Bulenox CL and NG, primary and spread1, mu* and mu10K) are listed: their values are the full-grid thresholds, equal
  to E.28's.

### 3.3 Holding scope (reports/stage_e32b_holding_scope.md)

- Every top-15 pair has its minimum G (cost per sigma plus the power term, under the 20-trade entry cap) at 30
  minutes. Band B is 15-30 minutes for 13 pairs, 30-60 for MFFU MYM and 15-60 for Topstep ZL; no band contains 5, 120 or
  240 minutes or the open-to-close hold. Cost per sigma falls about as sqrt(h) with no flattening point, so the band is
  set by the entry cap and the power term, which bind past 60 minutes (G(120) is 1.13-1.56 times the minimum, G(240)
  1.50-2.53).
- E.28's economics by horizon (E_dir, econ pass 2 ended 07:27:58): the edge needed to reach USD 10,000 within 250 days
  is lowest at 30 minutes and rises with the hold in all 15 pairs (above the grid cap at 120 minutes for 4 pairs and at
  240 for 14). The break-even edge falls to zero at long holds in 9 cells, a property of the model's payout structure,
  not an edge.
- Prop rules: the daily loss limit never binds inside B (it excludes holds from 120 minutes up, or the open-to-close
  hold, on 6 of the 15 pairs, all already outside B); no prop firm allows overnight holds (evaluation, funded or
  weekend); news windows are listed per firm, not used as band edges.
- Own broker (IBKR, no prop rules): 20 of the 35 Layer 1 survivors hold the prior, 1 partly (ZF), 14 fail (their minimum G
  lies at the close-to-close hold, or their band is empty); the five top-15 codes hold, MYM's band reaching 120 minutes.
- The user's prior (multiple minutes to hours) holds at its short end and fails for hours: the facts support 15-60
  minute holds. At 30 minutes, detecting an edge at the test with 80% power needs a gross of 4.2-13.2 ticks a trade
  (cost plus the minimum detectable edge).

### 3.4 Build recommendations (reports/stage_e32b_recommendations.md)

- R1: 23 closed lines, 838 trials (the ledger ladder r001-r009); LR-R1 reads V38 as closing the tested configurations
  on the 17 roots, with its umbrella sentence an evidence finding.
- R2: 185 combinations from 49 dossiers (product x firm x family x F5 band: Topstep 35, Tradeify 29, MFFU 43, Bulenox
  15, Lucid 14, IBKR 49; 42 pools), rated Q1-Q3 by a fresh CombinationScorer on a names-free dossier copy.
- R3 (hashed rule, spec 8): 26 combinations excluded (Q3 = 0: re-tests of closed configurations; F01 on MNQ, ZL and
  the pools by the rater, F01 on YM, MYM and RTY by LR-Q3a), 159 eligible.
- R4 (primary, after LR-Q3a, LR-V31 and LR-Q3b):

| # | Combination | Venue | Band (h_c) | C | Prior of passing a sealed test | Runs only if |
|---|---|---|---|---|---|---|
| 1-2 | C140 ZL F10 order-book state + C138 ZL F09 soy-complex lead-lag, one registration | Topstep | 15-60 (30) | 2.75, 2.65 | about 4% (F10 about 2%, F09 about 2.5%) | D2 and D3 |
| 3 | C072 MNQ F08 overnight-to-day handoff | Topstep | 15-30 (30) | 2.55 | under 1% | D4 |
| 4 | C021 YM F08 handoff | Topstep | 15-30 (30) | 2.55 | about 1.5%, only if V31 were narrowed | D1 |
| 5 | C147 EQ3 F08 pool (YM, MNQ, RTY) | Topstep | 15-30 (30) | 2.55 | under 1% | D1 and D4 |

  Kill criteria (each program): K0 its "runs only if" condition fails: not run; K1 the pre-registered discovery gate
  fails: stop, no test read; K2 the best configuration's net edge per trade is below the test's minimum detectable
  edge (ZL 1.8 ticks at 30 minutes; YM 12.2, MNQ 28.5; the pool 0.16 sigma per member): stop; K3 the sealed test fails:
  the program closes; K4 entries inside news windows or holds past the main session are excluded by design.
- Sensitivities: the narrow V31 reading puts YM F08 first (2.85); without the ZL window the list is MNQ F08, YM F08, EQ3
  F08, RTY F08 and RTY F09; Topstep's Standard Path ($150 a day) lowers MNQ F08 to 2.40; the leg-level F09 reading
  (LR-Q3b's sensitivity) gives the session-3 list (ZL F09 and F10 2.75, RTY F09 2.60, MNQ F08, YM F08).
- Non-prop alternative: C141 ZL F10 at IBKR (C 2.60 against 2.75 at Topstep); not favoured now (margin, daily risk
  against the USD 6,000 (u) ceiling, and V32).
- Stop rule: run at most one more registered build, the ZL program; if it fails its discovery gate or its sealed test,
  the directional program stops; MNQ F08, YM F08, the EQ3 pool and RTY F09 are not fallbacks; stop before any purchase
  when the best remaining prior is below 2% or its K0 fails; a restart needs a new information source.

## 4. Delegation record

Lead: Opus 5.5 (claude-opus-5-5) at max effort in all four sessions (3d79635b, 7e35d21b, 3860d0d1, 0d036ce2). Workers
use the generic agent files (subagent_type worker-medium/high/xhigh/max, model passed per call); each model below is
the one in the worker's own transcript (message.model), not its self-report. The routing followed V55 (readers Opus
high or Sonnet, extraction Haiku, the blind scorer Opus xhigh, reviewers Fable xhigh) with at most 6 workers at once.
Token counts per spawn are in section 8.

| Session | Worker (role) | Agent file | Model (transcript) | First-last (PDT) | Status |
|---|---|---|---|---|---|
| 1 | FableProbe-FableMed | worker-medium | claude-fable-5-1 | 22:22 | done: Fable available |
| 2 | CrudeReader, NatgasReader, MetalsReader, GrainsReader, RatesReader, EquityReader -OpusHigh | worker-high | claude-opus-5-5 | 22:48-23:09 | done (F2) |
| 2 | FXReader-OpusHigh, CryptoReader-OpusHigh | worker-high | claude-opus-5-5 | 23:03-23:21 | done (F2) |
| 2 | FirmRules-OpusHigh | worker-high | claude-opus-5-5 | 23:07-23:34 | done (firm facts) |
| 2 | DataAccess-SonnetHigh | worker-high | claude-sonnet-5-5 | 23:16-23:33 | done (D5 facts, Databento MBO) |
| 2 | AttentionCounter-HaikuMed | worker-medium | claude-haiku-5-5 | 23:18-23:19 | done (OpenAlex counts) |
| 2 | VolCoder-OpusXHigh | worker-xhigh | claude-opus-5-5 | 23:05-23:16 | done (F3) |
| 2 | ScoreCoder-OpusXHigh | worker-xhigh | claude-opus-5-5 | 23:09-23:38 | done (score32b.py, r3_score.py) |
| 2 | EconSetup-OpusXHigh | worker-xhigh | claude-opus-5-5 | 23:09-00:54 | done (econ code, E.28 regression) |
| 2 | HoldingCoder-OpusXHigh | worker-xhigh | claude-opus-5-5 | 23:19-23:32 | done (F5 code, SR80) |
| 2 | ClosedLines-SonnetHigh, NonProp-SonnetHigh | worker-high | claude-sonnet-5-5 | 23:21-23:41 | done (R1 inventory; IBKR facts) |
| 2 | IdeaFamilies-OpusHigh | worker-high | claude-opus-5-5 | 23:28-23:40 | done (family catalog) |
| 3 | FactTable-OpusHigh (resumed twice) | worker-high | claude-opus-5-5 | 01:05-03:21 | done (F4, masks FINAL3) |
| 3 | BlindScorer-OpusXHigh (rater 1) | worker-xhigh | claude-opus-5-5 | 01:35-01:53 | cut by the usage limit; superseded, inter-rater only |
| 3 | FactAuditor-FableXHigh (resumed once) | worker-xhigh | claude-fable-5-1 | 01:35-03:26 | done: B1, then B2 (blinding), values PASS |
| 3 | BlindScorer2-OpusXHigh (rater 2) | worker-xhigh | claude-opus-5-5 | 03:28-03:54 | done (all blind ratings) |
| 3 | VariantBuilder-SonnetHigh (resumed twice) | worker-high | claude-sonnet-5-5 | 03:31-05:40 | done (lead_variants.json) |
| 3 | F5Runner-OpusXHigh | worker-xhigh | claude-opus-5-5 | 03:57-04:06 | done (provisional Layer 1, IBKR venue) |
| 3 | DossierWriter-OpusXHigh | worker-xhigh | claude-opus-5-5 | 05:27-05:59 | done (R2) |
| 3 | RankingWriter-OpusHigh, ScopeWriter-OpusHigh (each resumed) | worker-high | claude-opus-5-5 | 05:27-05:43 | done (ranking, scope files) |
| 3 | CombinationScorer-OpusXHigh | worker-xhigh | claude-opus-5-5 | 06:01-06:19 | done (Q1-Q3, names-free) |
| 3 | RecsDrafter-OpusXHigh (resumed twice) | worker-xhigh | claude-opus-5-5 | 06:21-07:06 | done (R4 facts, assembly) |
| 3 | RankingReviewer-FableXHigh (RV1) | worker-xhigh | claude-fable-5-1 | 06:58-07:25 | done: PASS, 0 / 3 / 13 |
| 3 | RecsReviewer-FableXHigh (RV2) | worker-xhigh | claude-fable-5-1 | 06:58-07:18 | done: PASS WITH ONE RULING NEEDED, 1 / 6 / 7 |
| 4 | ScoreFixer-OpusHigh (resumed once) | worker-high | claude-opus-5-5 | 08:47-08:57 | done (RV1 S1-S3, N1-N2) |
| 4 | R1Fixer-OpusHigh | worker-high | claude-opus-5-5 | 08:47-08:56 | done (RV2 B1 text, S6, N2) |
| 4 | CostTabler-SonnetHigh | worker-high | claude-sonnet-5-5 | 08:54-08:56 | done (cost script) |
| 4 | DelegationTabler-HaikuMed | worker-medium | claude-haiku-5-5 | 08:54-09:01 | done (STATE rows) |
| 4 | RecsAssembler-OpusXHigh | worker-xhigh | claude-opus-5-5 | 08:57-09:22 | done (recommendations file) |
| 4 | FixVerifier-FableXHigh | worker-xhigh | claude-fable-5-1 | 09:23-09:41 | done: PASS, 0 / 0 / 7 |

Reviewers' models, confirmed from their transcripts: FactAuditor claude-fable-5-1 (3 of 3 messages at 01:38), RV1 and
RV2 claude-fable-5-1 (4 of 4 and 3 of 3 at 06:58), FixVerifier claude-fable-5-1 (09:23); the cost script found no
other model in any Fable transcript (records marked <synthetic> are the usage-limit cuts). Detached scripts: econ
pass 1 (01:17:08-05:24:12, 224 jobs on 8 workers), econ S_mean (03:53:14-04:04:51), econ pass 2 (E_dir 30/120/240,
05:26:15-07:27:59); the score, F5, scope and r3 runs were run by the lead.

## 5. Verification

Every number entering a verdict was checked by a Fable worker that did not produce it (each model confirmed from its
transcript: claude-fable-5-1).
- FactAuditor-FableXHigh (F4, 01:35-03:26): every value that feeds a score PASS (0 wrong values across 47 codes, 5
  firms, 235 pairs, S_mean, IBKR and cross-family checks); blinding FAILED twice (B1: Lucid plan names in four items;
  B2: the MFFU name in one quote), both patched before rater 2 rated the FINAL3 sheets; S1-S4 handled (the HG
  erratum, the IIP lines, sizes and ticks removed from items, SIL left as ruled).
- RankingReviewer-FableXHigh (RV1, Step 4, 06:58-07:25): PASS; 0 BLOCKING, 3 SHOULD FIX, 13 NOTE. It recomputed every
  Layer 1 and Layer 2 score, gate, S, tie and rank (46 scored codes, 103 ranked pairs) and all 28 variants' top 5 and
  MNQ ranks with exact fractions; reran F3 on MCL, 6E and ZC byte for byte inside the window discipline (guards OK
  before and after, unlocks 0); confirmed the blinding (rater 2 rated FINAL3; no code, firm or platform name in its 819
  reasons) and the unknown rules; matched econ inputs to F3 and F4 for 112 pairs x 3 blocks.
- RecsReviewer-FableXHigh (RV2, R5 and F5, 06:58-07:20): PASS WITH ONE RULING NEEDED; 1 BLOCKING, 6 SHOULD FIX, 7
  NOTE. It recomputed R3 for 185 combinations in five runs (Q4-Q7, C, order, R4, own broker) and F5 for 8 rows,
  checked the closed-line overlaps against the frozen code, and found no outcome read. B1 (the F09 candidates' Q3
  rested on an incomplete closed-line fact) was ruled as LR-Q3b (family level), which drops RTY F09 from the R4 and
  adds the EQ3 F08 pool.
- Session-4 fixes: RV1 S1-S3 and N1-N2 by ScoreFixer (score rerun 08:51:03 with no score, gate or rank change; 178
  tests pass); RV2 B1 (text) and S6 by R1Fixer, which also corrected three of RV2's own statements against the code (no
  MES lead in E.12, MBT live for two months, Family B a pooled ridge); RV2 S1-S3 and S5 by the lead; S4 by the
  RecsAssembler; RV2 N1, N2, N5 and N6 addressed in the text.
- FixVerifier-FableXHigh (09:23-09:41): PASS; 0 BLOCKING, 0 SHOULD FIX, 7 NOTE. With its own scripts it reproduced
  the run-2/run-3 identity, all six r3 runs from the spec 8.3 text, the LR-Q3b patch's scope (exactly C112-C116 and
  C138-C139), the EQ3 arithmetic, every number in the lead's session-4 text, all 75 cells of the E_dir table and the
  six claims of its reading, the G17 facts against the frozen code, and 105 lead lines verbatim. The lead then applied
  six of its NOTE fixes (wording, timestamps, attribution: the reviewer's proposed text; not re-reviewed).
- Inter-rater agreement: 302/329 exact (91.8%); D6 23/47 (rater 2 reads samples spanning 2010 as not "on data after
  2010").
- Not verified: the full texts behind the evidence rows were not re-fetched by RV2 (no web access); the drafter's
  published-effect translations (F10.E01 R2 to 0.058 sigma; F01.E02 to 15.5%) are arithmetic under stated
  assumptions; the econ32b.json read by the 05:40:30 run (0567890e) is not on disk, so its blocks are inferred
  unchanged from the identical scores; p7_final.py's power was not rerun for the pooled 273-date case (the "far below
  80%" statement rests on an interpolation from recorded values).

## 6. Open choices

Every choice the prompt left open, as decided and logged (full text and times: reports/stage_e32b_briefs/RULINGS.md
and the STATE file). Lead rulings made after the hash carry a declared variant, kept in the results when it changes
the top 5 (OC-14).

Sessions 1-2:
- OC-1 N = 838: the SCOPE line "N stays 538" is a V51 carry-over (V53 item 2, V56 item 1).
- OC-2 Universe = E.28's 47 codes; ES, MES and the other owned roots not added.
- OC-3 Databento MBO availability and prices from one DataAccess worker (V37 shared source), not from each reader.
- OC-4 Primary E is E.28's model (T 20, sigma_T = sigma_1); E_dir60 a declared variant, E_dir 30/120/240 reported.
- OC-5 Slippage allowance 0.5 tick a round trip (an assumption); variants slip0, slip1.
- OC-6 sigma_h is the SD of h-minute changes (the "typical absolute move" read as the RMS move); variant mad.
- OC-7 E.28's L1 >= 2.00 and no-zero gates not used; variant L1min2.
- OC-8 A satellite's D2 uses its leader's facts and D4 deducts 2: a deliberate double penalty; variants D2_own, sat1.
- OC-9 D2 d (research attention) by OpenAlex count terciles.
- OC-10 An own-broker venue (IBKR) in R2/R3 only, for the non-prop alternative.
- OC-11, OC-15, OC-16 Planned context wipes when the lead passed about 300k tokens: after session 1 (22:34), session 2
  (00:56) and session 3 (07:25); each resumed from the STATE file's RESUME HERE block.
- OC-12 The R2 dossiers by a DossierWriter worker, the Q1-Q3 ratings by a fresh CombinationScorer, R4 by the lead.
- OC-13 The program's own earlier measurements (RETURN files) admitted as file-path sources, labelled with windows.
- OC-14 Lead rulings after the hash each carry a declared variant, reported when it changes the top 5 (spec 5).

Session 4:
- OC-17 LR-Q3b's leg-level reading made reproducible as the sensitivity q3bleg (patch_v31_q3_lead.py mode;
  work/R2/r3_out_q3bleg.json reproduces the session-3 list).
- OC-18 RV1 S1 fixed in the scorer (the market-case tie-break, as ruled in session 2), not by amending the ruling.
- OC-19 ZL F09's P(edge) lowered from 0.07 to 0.05 for the G17 null on ZL; the ZL program's prior stays about 4%.
- OC-20 The EQ3 F08 pool's prior under 1% (about 1.5% at most with V31 narrowed and 2024-03+ data approved); its
  K_eff 1,305 uses the spec's rho 0.5 within a class and is likely optimistic for index futures at the open.
- OC-21 R2_dossiers_for_rating.md stays as rated; corrections go to errata (R2_dossiers.md, R2_Q_ratings.md) and to
  the R1 file; recommendations line "ZL in other families' closed lines" split under LR-Q3b (LR-OF).
- OC-22 The base rate is shown both ways: 4% over the 23 closed lines and 1/19 (about 5%) over the 17 with a
  registered outcome (RV2 N5).
- OC-23 Section 2 quotes git status --short by its line count and this stage's lines (the full listing is in the two
  checks files).
- OC-24 The session-4 wipe gap (07:28:40-08:40:31) and the usage-limit pause (01:56-03:10) are shown apart from work
  time; the lead's wait while econ pass 1 ran (04:09-05:24) is stage compute and counted.
- OC-25 The commit leaves the raw fetched web pages untracked (reports/stage_e32b_briefs/pages/, 584 files, 135 MB, and
  three raw HTML pages under work/CRYPTO and work/GRAINS), as E.28 and E.32 did; the reader logs that record each
  page's URL, fetch time and sha256 are committed.

Lead rulings (one line each; RULINGS.md has the text):
- Facts and volatility: LR-F3 (VolCoder's choices where spec 2 is silent); LR-S (spread qualification; RL-SMEAN);
  LR-D0 (21-day month scaling of quotes); LR-D1 (k ratio 0.9195, ES proxy; RL-KZM kept, it reorders the top 5); LR-D2
  (p per the spec text; RL-PBRIEF); LR-D3 (registrations are reads only for the windows their searches ran on);
  FT-1 to FT-11 (FactTable items); LR-S1e (HG's S = 1 kept; sourced -> u an erratum with no effect); LR-ATT (the score
  run reads a format-only copy of the attention file).
- Scoring: HoldingCoder's 12 and ScoreCoder's 14 readings (LR-SC; crude and natgas one asset class); LR-E1 (econ pass 1
  on every computable listed pair, 8 workers); LR-B1 (names-free blind brief); LR-DLL (no DLL on the modelled Topstep
  and Bulenox plans: the MLL is used); audit decisions (B1, B2, S2, S3 patched without relabelling; S4 left);
  rater 2's primary ratings used throughout, its alternatives run as RS-* sensitivities; rater 1 superseded; RS-MNQD6,
  RS-OWNONLY, RS-EQS2 added once MNQ was shown not to be a satellite; QM's exclusion by the double penalty is the
  intended OC-8 reading; no ZL S = 2.06 variant (cannot reach the top 5); LR-RV1S1.
- Holding scope: LR-F5-IBKR (own-broker band B = {h : G <= 1.10 min G}); LR-Q6d (own-broker daily risk and the USD
  6,000 (u) ceiling); news windows not band conditions; soft DLLs treated as hard; E_dir zeros a model property.
- Recommendations: LR-R1 (V38 closes the tested configurations; its umbrella sentence an evidence finding); LR-R2a-c
  (combinations, bands, energy class); LR-Q6p (lowest payout path per firm; ts150_v2 sensitivity); the
  CombinationScorer's flags (ZL F01 gated; MNQ F12 only without R1-14 H6 T3; V39 not read as closing USDA/NOPA drift);
  LR-Q3a (F01 on YM, MYM, RTY re-tests closed configurations: Q3 0); LR-V31 (read literally: no clean test window for
  YM or MYM; q3only sensitivity, D1); LR-ZLW (ZL keeps its sealed window; nozlw sensitivity, D2); LR-Q3b (F09 on RTY
  and ZL: Q3 1, family level; q3bleg sensitivity); LR-OF; the lead's own R4 text corrected twice (07:07:40 after the
  RecsDrafter's fact check; session 4 after RV2).

## 7. Decisions for the user (each with a recommendation)

- D1 V31's scope for YM (no variant on E.16's windows, no purchase of the fallback roots). Recommendation: keep it. The
  Dow's best family (F01) is closed and its next one (F08) has a prior of about 1.5%; narrowing V31 would make YM F08
  the top candidate (C 2.85) without raising that prior.
- D2 The ZL sealed window's single read (2017-05..2020-11, V56 item 1). Recommendation: assign it to the ZL program
  (F10 + F09 in one registration, made before any further ZL read) if a prior of about 4% is acceptable; otherwise
  stop the directional program now.
- D3 V31's cost-feasibility gate for discovery searches. Recommendation: state explicitly that a V51-style discovery
  search is admitted without a published expected gross and is judged instead by the power rule (K2); keeping the gate
  stops every primary candidate before any purchase.
- D4 Data from 2024-03 onward (V51). Recommendation: keep it closed unless the ZL program passes; it would only enable
  the weaker MNQ F08 and EQ3 F08 candidates (and RTY F09, now outside the R4), at a power of about 0.05 on the 13 unread
  months.
- D5 The next stage. Recommendation: if D2 and D3 are accepted, one pre-registration stage for the ZL program on the
  E.32 protocol's model, with a Databento quote for the ZL order-book data logged before any purchase (the census rate
  gives about USD 19 for the discovery window and USD 41 with the test window; a quote, not a price); if either is
  declined, apply the stop rule and close the directional program.

## 8. Session cost

Computed at 09:44:52 PDT 2026-10-29 (the cutoff) from the transcripts of the four lead sessions and their subagents
(main .jsonl and subagents/**/*.jsonl of 3d79635b, 7e35d21b, 3860d0d1 and 0d036ce2) with
reports/stage_e32b_briefs/work/cost/make_cost.py (adapted from E.25/E.26; it keeps each message's final usage, as
reports/stage_e10_briefs/cost.py does; output work/cost/ret_cost_tokens.md and cost_raw.txt). No session is a resume
of another and none holds usage from before the stage. These are token counts, not plan-credit percentages; the
commit and the checks after 09:44:52 are not counted.

Wall clock: 22:06:09 (2026-10-28) to 09:44:52, 11 h 39 min. Not counted as work: the usage-limit pause (01:55:44-03:11:01,
1 h 15 min; the local econ run kept going) and three planned context wipes with nothing running (22:35:17-22:40:26,
5 min; 00:56:14-00:56:45; 07:28:50-08:39:23, 1 h 11 min). Counted: the lead's wait while econ pass 1 ran (04:09-05:24,
stage compute). Work time: 9 h 07 min. Per session (first to last record): 1 0 h 29 min; 2 2 h 16 min; 3 6 h 32 min
(5 h 17 min without the pause); 4 1 h 05 min to the cutoff.

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 3,382 | 385,969 | 21,663,145 | 1,851,038 | 23,903,534 |
| claude-haiku-5-5 | 58 | 79,231 | 3,743,478 | 319,077 | 4,141,844 |
| claude-opus-5-5 | 5,844 | 3,645,088 | 627,519,667 | 11,011,541 | 642,182,140 |
| claude-sonnet-5-5 | 526 | 238,462 | 37,525,195 | 1,241,992 | 39,006,175 |
| all | 9,810 | 4,348,750 | 690,451,485 | 14,423,648 | 709,233,693 |

(Three records marked <synthetic>, with zero usage, are the usage-limit cuts.)

Worker spawns (agent file, model from the transcript, effort, tokens):
- Session 1: FableProbe-FableMed: worker-medium, claude-fable-5-1, medium, 65,309
- Session 2: CrudeReader-OpusHigh: worker-high, claude-opus-5-5, high, 32,162,972; NatgasReader-OpusHigh: same, 28,090,644;
  MetalsReader-OpusHigh: same, 22,423,835; GrainsReader-OpusHigh: same, 31,237,627; RatesReader-OpusHigh: same,
  23,549,545; EquityReader-OpusHigh: same, 22,171,338; FXReader-OpusHigh: same, 21,236,586; CryptoReader-OpusHigh:
  same, 21,612,823; FirmRules-OpusHigh: same, 27,291,824; IdeaFamilies-OpusHigh: same, 10,643,052; VolCoder-OpusXHigh:
  worker-xhigh, claude-opus-5-5, xhigh, 5,038,247; ScoreCoder-OpusXHigh: same, 14,892,068; EconSetup-OpusXHigh: same,
  28,798,889; HoldingCoder-OpusXHigh: same, 7,374,669; DataAccess-SonnetHigh: worker-high, claude-sonnet-5-5, high,
  14,815,324; ClosedLines-SonnetHigh: same, 8,793,559; NonProp-SonnetHigh: same, 10,188,926; AttentionCounter-HaikuMed:
  worker-medium, claude-haiku-5-5, medium, 672,961
- Session 3: FactTable-OpusHigh: worker-high, claude-opus-5-5, high, 39,400,501; RankingWriter-OpusHigh: same,
  13,086,414; ScopeWriter-OpusHigh: same, 6,819,605; BlindScorer-OpusXHigh: worker-xhigh, claude-opus-5-5, xhigh,
  15,031,894; BlindScorer2-OpusXHigh: same, 12,026,958; F5Runner-OpusXHigh: same, 7,640,619; DossierWriter-OpusXHigh:
  same, 29,440,132; CombinationScorer-OpusXHigh: same, 4,504,982; RecsDrafter-OpusXHigh: same, 38,031,774;
  VariantBuilder-SonnetHigh: worker-high, claude-sonnet-5-5, high, 4,185,724; FactAuditor-FableXHigh: worker-xhigh,
  claude-fable-5-1, xhigh, 5,783,847; RankingReviewer-FableXHigh: same, 8,010,050; RecsReviewer-FableXHigh: same,
  5,465,653
- Session 4: ScoreFixer-OpusHigh: worker-high, claude-opus-5-5, high, 8,892,840; R1Fixer-OpusHigh: same, 8,951,432;
  RecsAssembler-OpusXHigh: worker-xhigh, claude-opus-5-5, xhigh, 27,063,610; CostTabler-SonnetHigh: worker-high,
  claude-sonnet-5-5, high, 1,022,642; DelegationTabler-HaikuMed: worker-medium, claude-haiku-5-5, medium, 3,468,883;
  FixVerifier-FableXHigh: worker-xhigh, claude-fable-5-1, xhigh, 4,578,675

Lead sessions (claude-opus-5-5, max effort): 3d79635b 13,097,805; 7e35d21b 19,115,950; 3860d0d1 74,510,690; 0d036ce2
28,042,815 (to the cutoff).

Delegation share: lead 134,767,260 (19.0%), workers 574,466,433 (81.0%). By model: Opus 642,182,140 (90.5%; lead
134,767,260, workers 507,414,880), Sonnet 39,006,175 (5.5%), Fable 23,903,534 (3.4%), Haiku 4,141,844 (0.6%). Cache
reads are 97.4% of all tokens. By session: 1 13,163,114; 2 350,110,839 (the eight research readers alone 202,485,370);
3 263,938,843; 4 82,020,897.

The final table (one row per task, spawn and pause, against the initial estimate) is in this stage's progress.md
entry, as CLAUDE.md asks.

