# Stage E.31 return: volume check, then a ZM order-book pilot on the temporary account

Lead: Opus 5.5 (claude-opus-5-5), xhigh. Prompt: docs/prompts/STAGE_E.31.md. Run 2026-10-22 07:47 PDT to 2026-10-23
{{END_TIME}} PDT, with three usage-limit pauses and one laptop reboot (section 8). The prompt's 23:00/23:30 times were
applied to 2026-10-23 on the user's instruction after the reboot. Times are America/Vancouver. Nothing is registered;
N stays 538; REGISTRATION.md is 0 bytes; nothing was pushed.

## 1. Summary

- **Volume verdicts (Part 1).** Over the last 12 full months (2025-10-01 to 2026-09-30, 260 weekdays), QM's median daily
  volume is **4,480.5** contracts, above the 1,000 kill line, so QM does not fail: the frozen E.28 QM pilot is not
  closed and stays on hold (V47, V48). ZM's median is **78,281.5** (own-universe 79,512.0), above the 5,000 line, so
  ZM passes and Part 4 went ahead. An independent recomputation matched all 442 quantities.
- **acct-3.** Spent **122.370573 USD** of the 125.00 cap by this repo's ledger: Part 1 0.725022 and the pilot
  121.645551 (156 requests, each settled at its quote). Left **2.629427 USD** (the ledger figure; the Databento portal
  governs). **"ACCOUNT_3 SAFE TO WIPE"** was written to reports/stage_e31_STATE.md at {{SAFE_TIME}} after the last
  purchase was verified (verify31 exit 3, data-quality findings only, all on the definitions files).
- **Pilot verdict (Part 5): ZM FAILS, on K1.** Under the gate model (c), trade-through only, the front month's DAY
  session gives a mean 10 s edge net of Topstep's fee per fill of **-1.234 ticks**, 95% day-block interval
  [-1.252, -1.214], identical under the dropping and the no-drop markout variants (no markout was dropped). It fails
  at zero fee too (gross -0.970 [-0.988, -0.950]) and at the full round-trip fee per fill (-1.516 bound), so the result
  does not depend on the fee reading. K2 (44,045 fills, need 400) and K3 (111.6 round trips a DAY date, need 20) clear.
  Models (a) K-algorithm and (b) FIFO, which decide nothing, are negative too, before fees: gross 10 s edge -0.287 and
  -0.252 ticks. Every firm, horizon, session, month and split is negative.
- **Data bought.** 39 whole months, 2020-12 to 2024-02 (the most that fit TARGET 122.27): ZM MBO (ZM.v.0, ZM.v.1), ZS
  and ZL MBP-1 (front), and the definitions; 156 files, 24.2 GB under /mnt/large-storage/market_data/PropExperiment/,
  sha256 manifests beside them. Nothing dated on or after 2024-03-01. 816 trade dates measured; 764 DAY dates usable for
  the front month.
- **Deviation the user should know.** Every worker spawned as "Fable xhigh" ran on **claude-sonnet-5-5** at xhigh
  according to its transcript; the probe's "FABLE OK" was a self-report. The reviews and verifications were therefore
  Sonnet 5.5 xhigh in fresh contexts, not Fable (Max branch) and not Opus (Pro branch, V46 item 5). The verdict numbers
  were then checked again by an Opus 5.5 xhigh fresh-context worker: {{OPUSV_SHORT}}. A true Fable check remains pending.

## 2. Guardrail evidence

{{GUARD}}
Other guardrails:
- Sealed holdout: `unlocks_logged` 0 and `all_ok` true in all six stores at the start (07:47), at each resume (00:57,
  05:51) and at the end. No holdout, embargo, research-window or sealed file was read.
- Keys: checked by name only (checks.sh greps for the line); no key was read into any log, print or file.
- Spend: every Databento call went through SpendGate on acct-3 with this stage's session ids
  (stage-E.31-2026-10-22-volume, -pilot-span, -pilot); a fresh logged quote came before each purchase; the pilot-only
  guard (data.config.PILOT_ONLY_ACCOUNTS) and every file under data/ are unchanged.
- No ZM, ZS or ZL record dated on or after 2024-03-01 was quoted, bought or read: every request ends at or before
  2024-02-29T22:00:00Z, and verify31 checks ts_recv and ts_event of every record against the request bounds.
- No TopstepX call, no credential, no edit under live/ or ops/. Ledger: 36,402 lines at the start, 37,290 at the end.
- Full test suite: {{PYTEST}}

## 3. Results

### 3.1 Part 1: volume check

Request frozen before any quote: reports/stage_e31_volume_request.md (sha256 09d83f43...; the text says "about 08:20",
its mtime is 07:56, before the 07:58 quote: a lead clock slip). Quote 0.72502180934 USD (V2 bound 1.00), bought 07:58,
settled at the quote. Results: reports/stage_e31_volume.md and work/pilot/runs/vol_measures.json.

| Root | Window median (primary universe) | Own universe | Kill line | Verdict |
|---|---|---|---|---|
| QM | 4,480.5 | 4,480.5 | 1,000 | not FAIL (E.28 QM pilot stays open, on hold) |
| ZM | 78,281.5 | 79,512.0 | 5,000 | PASS |

Per-quarter medians, 10th percentiles and front-month shares are in reports/stage_e31_volume.md. ZM's Q3 front-month
share is low (about 0.08) because the earliest-delivery rule picks the expiring August/September contract; it decides
nothing.

### 3.2 Part 2: the spec

reports/stage_e31_pilot_spec.md, v1 frozen 2026-10-22 13:02:19 (sha256 9143d2b6...), v2 frozen 13:21:47 (sha256
31d33e68736b3c13ae46afcd0bf8d28411bbb3d96864802a6193cf5f33b9f61a) after the spec review, before any ZM purchase. v2
made K1 clear under both markout variants, added the canary tranche, the retry rule and the grid boundary (56 DAY grid
times, 112 placements a day), and settled the K-algorithm reading. One erratum (OC-5). Research behind it:
research/K_algorithm.md (CME product sheets 2023-06 and 2024-02: ZM K, TOP 100%/min 1/max 100, 40% FIFO, 60% pro rata,
pro-rata minimum 1, leveling, no LMM; 8 CME examples used as tests), research/data_facts.md (Databento snapshots and
record semantics, ZM limits reset 2023-11-01), research/usda_releases.csv and usda_releases_ext.csv (2020-12 to 2024-02).

### 3.3 Part 3: code

Beside E.28's, in reports/stage_e31_briefs/work/pilot/: pilot31_common.py, pull31.py, verify31.py, canary_check31.py
(purchase and checks); mbo_book31.py, kalgo31.py, measure31_core.py, measure31.py (the engine); stats31*.py (statistics
and kill rule); README31.md, README_measure31.md, TABLES31.md. 328 synthetic tests in its tests/ folder pass (no
Databento call), including CME's K-algorithm examples E1-E7 and E9 and hand-built full K sequences.

### 3.4 Part 4: reviews and purchase

- Spec review (pass 1, reports/stage_e31_briefs/R_spec31.md): GO, no BLOCKING, 16 advisory; items 1-9, 11 and 12
  adopted before any purchase.
- Engine review (pass 2, R_engine31.md): NO GO on one BLOCKING item (model (a) read a TOP order's room after the
  event's own fills); fixed, with tests.
- One re-check of both (R_recheck31.md): "A: GO; B: GO".
- Window: k = 39 months, 2020-12 to 2024-02; the 156 free span quotes sum to 121.645551 against TARGET 122.27 (2020-11
  would make 124.340118). Canary first (2024-01 and 2024-02, 6.107772 USD, 13:24-13:48 on 2026-10-22), structure checked
  (every weekday snapshot present, all outrights K, ticks 10.00/12.50/6.00 USD with ZS and ZL quoted in cents, trade and
  fill records consistent with implied trades), then the other 148 requests (06:30-12:31 on 2026-10-23, fresh quote
  121.645551 approved exactly). verify31 over all 156 files: exit 3, all findings on the definitions files (35 months
  delivered 3.7% under the quoted bytes, OC-8; 8 months list combos partway through); every MBO and MBP-1 file matched
  its quote byte for byte and passed every check.

### 3.5 Part 5: the measurement

Run 2026-10-23 12:35:57-12:46:12 (816 of 816 trade dates, 384 s, 4 workers, nice 10); statistics only after every
date was done (the stats layer refuses otherwise). Outputs: work/pilot/runs/stats31.md and stats31.json (the full
tables), runs/measure31_diag_summary.json, and the per-date tables under runs/measure31/ (50 MB, kept on disk, not
committed). Exclusions, front month: 52 of 816 dates (23 roll days, 20 days after a roll, 4 holidays or early closes,
5 late opens); no DAY gap above 60 s; consistency checks all 0.

Primary population (ZM.v.0, DAY session, buy and sell pooled; ticks; 95% day-block intervals):

| Statistic | (a) K | (b) FIFO, back of queue | (c) trade-through (gate) |
|---|---|---|---|
| placements | 85,568 | 85,568 | 85,568 |
| fills (rate) | 60,216 (0.704) | 61,078 (0.714) | 44,045 (0.515) |
| half-spread captured, mean | +0.341 | +0.359 | -0.425 |
| 10 s markout vs mid, mean | -0.629 | -0.611 | -0.545 |
| 10 s edge E_10, mean | -0.287 [-0.303, -0.273] | -0.252 [-0.267, -0.239] | -0.970 [-0.988, -0.950] |
| 10 s edge net of Topstep's fee per fill | -0.551 | -0.516 | **-1.234 [-1.252, -1.214]** |
| 60 s edge E_60, mean | -0.290 | -0.253 | -0.979 |
| loop round trips per DAY date, mean | 207.7 | 215.1 | 111.6 [109.6, 113.5] |

Kill rule (spec v2 section 7), model (c): K1 holds (FAIL): lower bound -1.2524 under both variants; information only,
at 0.528 per fill: -1.5164. K2 clear: 44,045 fills. K3 clear: 111.568 over 764 dates. **Verdict: FAIL.**

Reported beside, deciding nothing (gross 10 s edge, model (c)): overnight front month -0.997 (fill rate 0.132);
second month (ZM.v.1) DAY -1.186; model (a) from 2023-11-01 alone, front DAY -0.281. All five firms' nets are negative
for every model and horizon (Tradeify's 0.460 fee per fill makes it the worst). Conditioning, model (c), front DAY,
10 s edge: fills after a ZS move against the order in the prior 1 s average -1.100, after a ZS move with it -0.652;
fills 0-5 minutes after a USDA release -8.98 (68 fills); no imbalance, ZS, ZL or USDA bucket is positive for any
model. Implied liquidity, front DAY: 5.5% of aggressor prints (3.6% of their volume) found no displayed resting
quantity at their price, 11.8% (26.0% of volume) found less than their size, and 9.1% of prints carry no aggressor side.

What this means. A resting one-lot at the ZM touch loses on average about a quarter of a tick per fill before fees
even when it fills at its queue turn (models a and b), because the mid moves through it more often than not; under
Topstep's simulator rule (fill only on a trade through the price) every fill comes after the level has gone, so the
fill sits about half a tick behind the mid and keeps losing, about one tick in all. Fees make it worse at every firm.
The pilot measures fills and markouts, not a strategy, but no strategy that rests one lot at the ZM touch under these
rules starts from a positive edge.

## 4. Delegation record

{{DELEGATION}}

## 5. Verification

- Part 1 volume numbers: VolumeVerifier (launched as Fable xhigh, ran on Sonnet 5.5 xhigh) recomputed them from the
  frozen request before opening the producer's files: CONFIRMED, 442 of 442 quantities and 64 of 64 quarter rows
  (work/verify_vol/VERIFY_volume.md).
- Spec, kill rule, window arithmetic and purchase code: SpecReviewer (Sonnet 5.5 xhigh in fact): GO, 16 advisory; it
  matched all 156 span quotes with the ledger and recomputed every month bound (R_spec31.md).
- Engine and stats: EngineReviewer (Sonnet 5.5 xhigh in fact): NO GO on one model (a) item, fixed; the K allocator
  matched an independent reference over 60,000 random cases; no look-ahead (R_engine31.md). ReCheck (Sonnet 5.5 xhigh in
  fact): A GO, B GO (R_recheck31.md).
- Verdict numbers: PilotVerifier (Sonnet 5.5 xhigh in fact) recomputed K1 (both variants), K2, K3 from the tables with
  its own code, rebuilt model (c) from the raw MBO on 9 dates (all 1,008 placements and 534 fills matched to the
  nanosecond), and found the producer's numbers CONFIRMED (work/verify_pilot/VERIFY_pilot.md).
- Verdict numbers again, Pro branch: OpusVerifier (Opus 5.5 xhigh, fresh context): {{OPUSV_LONG}}
- Pending: a check by Fable itself, once a session can confirm from its transcript that it runs on claude-fable-*.

{{OC}}

## 7. Decisions for the user

1. Accept the ZM verdict and stop pursuing passive spread capture at the touch in ZM at these five firms.
   Recommendation: yes. All three fill models are negative before fees, at every horizon, session, month and split,
   and the gate fails at zero fee, so neither the fee reading nor the fill model changes the answer.
2. QM. It passed the volume check (median 4,480.5), so the E.28 QM pilot is not closed. Recommendation: keep it on
   hold and do not buy it. Under the trade-through rule a fill comes after the level is gone, which cost ZM about a
   tick per fill; QM's quotes go stale faster (one QM tick is 2.5 CL ticks, V47), so the same mechanism is unlikely to
   be kinder to it. The decision is yours: V47's conditions (a 2025-2026 sample, CL top of book) still stand.
3. The passive-capture line as a whole (E.28's methods brief, Phase 0). Recommendation: treat the trade-through rule
   as the binding constraint for any passive one-lot at a prop firm's simulator, and test any further contract (V49's
   ZL follow-up included) first with the cheap check this stage shows to be decisive: the gross 10 s edge under model
   (c) from top-of-book data alone.
4. V49's ZL follow-up. The ZL MBP-1 data are on disk (2020-12 to 2024-02, front month), so it costs no data. It needs
   a trade-through measurement on MBP-1 (E.28's measure_core does that for one contract) and its own declaration.
   Recommendation: run it only if decision 3 is accepted as the test, and expect the same mechanism.
5. E.29's D2 (re-run the basket model around ZM). Recommendation: do not run it: ZM has no positive passive edge to
   anchor a basket.
6. acct-3. It is safe to wipe (2.63 USD left by the ledger; please confirm the portal balance), then remove
   DATABENTO_API_KEY3 from .env (V46 item 4).
7. The bought data (24.2 GB of ZM MBO with ZS and ZL top of book, 2020-12 to 2024-02) can serve later order-flow work
   (the methods brief's Phase 1), which would need its own pre-registration. Recommendation: keep them.
8. Reviewer routing. The "fable" alias ran on Sonnet 5.5 in this session. Recommendation: decide whether this
   stage's Sonnet reviews plus the Opus fresh-context check are acceptable for a FAIL verdict with this margin, or
   whether a Fable check is required when Fable is available; and add a transcript check of the model to the probe
   (memory note fable-alias-falls-back-to-sonnet).

## 8. Session cost

{{COST}}
