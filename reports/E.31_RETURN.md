# Stage E.31 return: volume check, then a ZM order-book pilot on the temporary account

Lead: Opus 5.5 (claude-opus-5-5), xhigh. Prompt: docs/prompts/STAGE_E.31.md. Run 2026-10-22 07:47 PDT to 2026-10-23
about 13:50 PDT, with three usage-limit pauses and one laptop reboot (section 8). The prompt's 23:00/23:30 times were
applied to 2026-10-23 on the user's instruction after the reboot. Times are America/Vancouver. Nothing is registered;
N stays 538; REGISTRATION.md is 0 bytes; nothing was pushed.

## 1. Summary

- **Volume verdicts (Part 1).** Over the last 12 full months (2025-10-01 to 2026-09-30, 260 weekdays), QM's median daily
  volume is **4,480.5** contracts, above the 1,000 kill line, so QM does not fail: the frozen E.28 QM pilot is not
  closed and stays on hold (V47, V48). ZM's median is **78,281.5** (own-universe 79,512.0), above the 5,000 line, so
  ZM passes and Part 4 went ahead. An independent recomputation matched all 442 quantities.
- **acct-3.** Spent **122.370573 USD** of the 125.00 cap by this repo's ledger: Part 1 0.725022 and the pilot
  121.645551 (156 requests, each settled at its quote). Left **2.629427 USD** (the ledger figure; the Databento portal
  governs). **"ACCOUNT_3 SAFE TO WIPE"** was written to reports/stage_e31_STATE.md at 2026-10-23 12:35:57 PDT after the last
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
  were then checked again by an Opus 5.5 xhigh fresh-context worker: CONFIRMED (K1 under both variants, K2, K3 and the FAIL verdict; model (c) rebuilt from the raw MBO on 4 more dates matched exactly). A true Fable check remains pending.

## 2. Guardrail evidence

Start checks (2026-10-22 07:47, reports/stage_e31_briefs/start_checks.txt, script checks.sh), verbatim, with the 1,434
untracked `??` lines and the older trial-registry rows left out (they are in the file):

```
# E.31 checks: start
$ date
Thu Oct 22 07:48:26 PDT 2026
$ git status --short
$ git status --short | wc -l
1434
$ git log --oneline -3
403fd7c docs: V48 (keys, ZM pilot replaces QM) and the Stage E.31 prompt
d485f34 Stage E.29 basket simulation
60eb6b6 Stage E.28 methods brief, ranking and pilot
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
36402 ledger/databento_spend.jsonl
034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700
$ ledger total per account (SpendGate.account_spent_usd)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 353.455228 cap 355.38 headroom 1.924772
acct-3: spent 0.000000 cap 125.00 headroom 125.000000
$ uv run python -m screening.trial_registry status (N)
r008-E23: E23 ['E23-MEZFh5', 'E23-MEZNh5', 'E23-MEZBh5', 'E23-H6NQh5', 'E23-H6NQh20'] N 533 -> 538 at 2026-10-17T03:33:45-07:00
.env DATABENTO_API_KEY: absent
.env DATABENTO_API_KEY2: absent
.env DATABENTO_API_KEY3: non-empty
```

End checks (2026-10-23, reports/stage_e31_briefs/end_checks.txt), verbatim, same omissions:

```
# E.31 checks: end
$ date
Fri Oct 23 13:14:40 PDT 2026
$ git status --short
 M ledger/databento_spend.jsonl
$ git status --short | wc -l
1439
$ git log --oneline -3
c8f189e docs: V49 (NQ dropped from the passive candidates; ZL follow-up)
403fd7c docs: V48 (keys, ZM pilot replaces QM) and the Stage E.31 prompt
d485f34 Stage E.29 basket simulation
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
- Full test suite: `uv run pytest -q -p no:cacheprovider` (10-23 13:14-13:34, 2 GB watchdog never fired): 8090 passed, 1 failed, 5 skipped, 3 xfailed in 1196 s. The failure is tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha, the known by-design failure since harness v13 (E.22), the same single failure as E.26 and E.29; no E.31 file touches it. The pilot folder's own tests: 328 passed (work/lead/pytest_full.log).

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

The lead (Opus 5.5 xhigh) kept the decomposition, the Part 1 request, the spec and its v2 rulings, every lead ruling
(OC list), the purchases' approvals, the verdict reading and this synthesis. Workers (worker-* agent files; times,
tokens and status in section 8's final table). Briefs are in reports/stage_e31_briefs/brief_*.md.

| Agent (role) | Model asked / ran | Brief | Artifacts |
|---|---|---|---|
| FableProbe-FableMed (availability probe) | fable / sonnet 5.5 | inline | none |
| VolumeCoder-OpusHigh (Part 1 measures) | opus / opus | brief_volume.md | work/pilot/vol_measure.py, tests, stage_e31_volume.md |
| VolumeVerifier (Part 1 check) | fable / sonnet 5.5 | brief_volverify.md | work/verify_vol/VERIFY_volume.md |
| KResearch-OpusHigh (K algorithm) | opus / opus | brief_kresearch.md | research/K_algorithm.md, K_fetch_log.md, pages/K/ |
| DataResearch-OpusHigh (Databento, USDA, limits, specs) | opus / opus | brief_dataresearch.md | research/data_facts.md, usda_releases.csv |
| UsdaExt-OpusHigh (USDA 2020-12..2022-10) | opus / opus | brief_usdaext.md | research/usda_releases_ext.csv |
| PullCoder-OpusXHigh (purchase, verify) | opus / opus | brief_pullcoder.md | pilot31_common.py, pull31.py, verify31.py, README31.md |
| StatsCoder-OpusXHigh (statistics, kill rule) | opus / opus | brief_statscoder.md | stats31*.py, tests |
| SimCoder-OpusXHigh (engine) | opus / opus | brief_simcoder.md | mbo_book31.py, kalgo31.py, measure31*.py, README_measure31.md |
| FixCoder-OpusXHigh (pass-1 fixes, canary check) | opus / opus | brief_fixcoder.md | pull31 retry and lock, verify31 checks, canary_check31.py |
| SpecReviewer (pass 1) | fable / sonnet 5.5 | brief_specreview.md | R_spec31.md |
| EngineReviewer (pass 2) | fable / sonnet 5.5 | brief_enginereview.md | R_engine31.md |
| ReCheck (both passes) | fable / sonnet 5.5 | brief_recheck.md | R_recheck31.md |
| PilotVerifier (verdict numbers) | fable / sonnet 5.5 | brief_pilotverify.md | work/verify_pilot/VERIFY_pilot.md |
| OpusVerifier-OpusXHigh (verdict numbers, Pro branch) | opus / opus | brief_opusverify.md | work/verify_pilot_opus/VERIFY_pilot_opus.md |

At most 4 workers ran at once. Workers cut by usage limits were resumed from their transcripts (SendMessage), never
restarted; a second copy of this session (tmux claude-retry-*, 10-23 01:07, closed by the planner) made one edit, which
the lead reviewed and superseded (OC-6).


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
- Verdict numbers again, Pro branch: OpusVerifier (Opus 5.5 xhigh, fresh context): CONFIRMED. K1 mean -1.23389 over 44,045 fills; with the producer's 816-date pool it reproduces the bound [-1.25241, -1.21419] exactly ([-1.25296, -1.21500] on the 764 included dates alone; the spec does not fix the pool, effect under 0.001 tick); K2 44,045; K3 111.568 over 764 dates, none below 20; the 0.528 bounds match. It rebuilt the book from the raw Z1 files on 2020-12-14, 2021-01-25, 2022-01-24 and 2023-01-24: all 448 placements and 225 fills match, E_10 and mid0 included, and the loop counts match; it reproduced the producer's bad-book flag counts on all 764 dates and found every flagged record before that date's first clear. Models (a) and (b), overnight, the second month and the conditions were not checked (work/verify_pilot_opus/VERIFY_pilot_opus.md).
- Pending: a check by Fable itself, once a session can confirm from its transcript that it runs on claude-fable-*.

## 6. Open choices

Every choice the lead made where the prompt left room, in the order made. "Lead" is the E.31 lead (Opus 5.5 xhigh).

- OC-1 Reviewers. One tiny probe (FableProbe, 07:49 on 2026-10-22) answered "FABLE OK Fable 5.1", so the lead took the
  prompt's Max branch and spawned every review and verification with model "fable" at xhigh. The transcripts show all six
  ran on claude-sonnet-5-5 (found at the end with the cost script): the alias fell back silently and the probe's answer was
  a self-report. So the reviews were Sonnet 5.5 xhigh in fresh contexts, neither Fable nor the Pro branch's Opus 5.5
  xhigh. The lead then ran the Pro branch's check of the verdict numbers (OpusVerifier, Opus 5.5 xhigh, fresh context);
  a check by Fable itself stays pending. Ultracode is a session setting the lead cannot switch; at most 4 workers ran
  at once.
- OC-2 Part 1 purchase path. Routed through a new pilot-path script (work/pilot/vol_pull.py) that uses SpendGate directly on
  acct-3, as E.28's pilot_pull.py does. data.config.PILOT_ONLY_ACCOUNTS and every file under data/ are unchanged, so no guard
  change needed review.
- OC-3 Volume day universe. Monday-to-Friday UTC dates with a QM or ZM outright bar; a root with no bar counts 0 (it can only
  lower a median). Each root's own universe is shown beside; both gave the same verdicts.
- OC-4 Review in two passes. SpecReviewer (spec, kill rule, window arithmetic, purchase and verify code) gave the purchase GO;
  the engine and stats code got their own Fable review before the measurement; one re-check covered the fixes of both. Reason:
  the purchase depends only on the first, and a single review after all the code would have pushed the download past the
  measurement's time.
- OC-5 Spec v2 erratum. Section 5 still says "the headline and the gate use the dropping version"; v2 section 7 (K1 must clear
  under both the dropping and the no-drop variant) governs the gate. Kept as an erratum so the frozen v2 hash stands.
- OC-6 Tick check. Databento quotes ZS and ZL in US cents (0.25 x 5,000 = 1,250; 0.01 x 60,000 = 600), so the check as first
  written stopped the run. measure31.checked_tick accepts USD or cents for ZS and ZL; ticks are used as found (the engine only
  divides by them). A second copy of this session (tmux claude-retry-*, 01:07 on 2026-10-23, closed by the planner, bought
  nothing) had edited the same line to multiply by a cents factor; the lead's version superseded it deliberately.
- OC-7 Model (b)'s volume. The engine uses Q, the outright volume filled against displayed resting orders, where spec 4(b)
  says v (all prints at the price). Q is conservative and matches spec 3.1's implied-liquidity rule; model (b) decides nothing.
- OC-8 Z4 delivery below the quote. The canary's definition files came 3.7% under the quoted billable bytes, settled at the
  quote. For the definition schema only, that is a quality finding, not hard; Z1-Z3 keep the hard equality (they matched
  exactly). The outrights' match algorithm and ticks are checked directly by canary_check31.
- Fee reading (spec v2 section 7). K1 charges half of Topstep's 5.28 USD round trip per fill (0.264 tick): a passive round trip
  is two fills and Topstep states "Each side (Buy or Sell) incurs half the total". The prompt's literal "less the Topstep fee
  in ticks" can be read as 0.528; that bound is reported beside, and a PASS that fails at 0.528 is labelled "PASS, fragile
  (fee reading)".
- K1 under both markout variants (SpecReviewer item 2), the canary tranche (item 3), one retry within acct-3's cap (item 4),
  verify31 hard checks (item 5), the grid boundary 08:35..13:10 CT, 56 DAY grid times (item 11): adopted before any purchase.
- Window. k = 39 months (2020-12..2024-02) is the rule's result: the most whole months whose fresh quotes fit TARGET 122.27
  (sum 121.645551; 2020-11 would make 124.340118). Month requests run 16:00 CT to 16:00 CT so each holds whole trade dates and
  every weekday 00:00 UTC snapshot.
- Front and second month are Databento volume ranks ZM.v.0 and ZM.v.1, not necessarily the two nearest expiries.
- K-algorithm gaps (spec 3.1): pro-rata denominator after the FIFO step; the TOP order takes part in later steps; split ceil;
  TOP modification rule S4's text; TOP Max counting changes on 2023-10-02; parameters sourced for 2023-06..2024-02 and assumed
  for earlier months, so model (a) is also reported from 2023-11-01 alone; the virtual order is never TOP; the FIFO exception
  is tested with the virtual order included.
- USDA calendar. WASDE, NASS and FAS rows from research/usda_releases.csv and usda_releases_ext.csv; 88 FAS rows are
  rule-derived or uncertain; NOPA is not USDA and is not used; three 2022 FAS outage weeks are skipped.
- StatsCoder's 7 conventions (stats31: done-marker names, split statistics among fills, fills in the 50 ms cancel latency
  count, one shared bootstrap matrix, placements not filtered by days.included, implied cases (i) and (ii) separate, K1 with no
  interval counts as FAIL) and SimCoder's 29 conventions (README_measure31.md, Conventions): accepted by the lead and reviewed
  by EngineReviewer.
- Times. The Part 1 request file says "about 08:20 PDT"; its mtime is 07:56 (before the 07:58 quote): a lead clock estimate,
  corrected in STATE, the frozen file left as is.
- V49 (planner commit c8f189e, 2026-10-23 01:03) makes a ZL trade-through measurement a follow-up; it is not in E.31's scope
  (decisions in force V20-V48).


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

Tokens come from the transcripts, each message at its final usage, counted by reports/stage_e10_briefs/cost.py over
session f6ca509c-6908-4e0b-a24a-4a4214833a47 (lead and its subagents) from 2026-10-22T14:40Z to 2026-10-23T22:00Z;
run at 13:40 PDT on 10-23, so the last calls (assembly, progress entry, commit, closing reply) are not counted. Output:
reports/stage_e31_briefs/work/lead/cost_raw.txt. Token counts, never estimates; plan-meter percentages are the user's
reading.

Wall clock: 2026-10-22 07:47 to 2026-10-23 about 13:50 = 30 h 03 min. Pauses, not work: 10-22 08:50 to 12:41 (usage
limit, 3 h 51 min); 10-22 13:29 to 10-23 00:57 (usage limit from 13:29, laptop reboot about 15:33; 11 h 28 min); 10-23
01:28 to 05:51 (usage limit, 4 h 23 min). Work: 07:47-08:50, 12:41-13:29, 00:57-01:28, 05:51-13:50, 10 h 21 min in
total, of which 6 h 01 min (06:30-12:31) was the detached download, with the lead idle.

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-opus-5-5 | 1,696 | 1,165,795 | 161,556,852 | 6,324,515 | 169,048,858 |
| claude-sonnet-5-5 (every "fable" launch) | 480 | 454,636 | 41,628,834 | 1,372,217 | 43,456,167 |
| all | 2,176 | 1,620,431 | 203,185,686 | 7,696,732 | 212,505,025 |

Delegation share: lead 61,989,915 (29.2%), workers 150,515,110 (70.8%): Opus workers 107,058,943 (50.4% of all),
Sonnet workers 43,456,167 (20.4%). No Fable token was spent.

Final table (times PDT; 10-22 unless marked; tokens by transcript):

| # | Task / agent | Model (effort) | Start-end | Time | Tokens | Status, deviations |
|---|---|---|---|---|---|---|
| 0 | Lead: start checks, inputs, Part 1 request, plan | opus 5.5 (xhigh) | 07:47-08:02 | 15 min | (lead) | done |
| 1 | FableProbe-FableMed (worker-medium) | asked fable, ran sonnet 5.5 (medium) | 07:49 | 3 s | 62,348 | answered "FABLE OK": a self-report |
| 2 | Part 1 quote and buy (lead, vol_pull.py) | - | 07:58-08:00 | 2 min | - | 0.725022 USD |
| 3 | VolumeCoder-OpusHigh | opus (high) | 08:02-08:07 | 5 min | 1,556,141 | done |
| 4 | KResearch-OpusHigh | opus (high) | 08:02-08:25 | 23 min | 9,412,005 | done |
| 5 | DataResearch-OpusHigh | opus (high) | 08:02-08:38 | 36 min | 21,636,041 | done |
| 6 | VolumeVerifier (worker-xhigh) | asked fable, ran sonnet 5.5 (xhigh) | 08:07-08:13 | 6 min | 3,067,916 | CONFIRMED |
| 7 | Lead: spec draft, section 3.1 | opus (xhigh) | 08:05-08:28 | 23 min | (lead) | done |
| 8 | PullCoder-OpusXHigh | opus (xhigh) | 08:10-08:35 | 25 min | 9,185,925 | done |
| 9 | StatsCoder-OpusXHigh | opus (xhigh) | 08:29-08:42, 12:43-12:52, 13:22-13:29, 10-23 01:00-01:02 | about 35 min | 6,080,305 | done; cut twice by limits |
| 10 | Span search (lead, detached) | - | 08:34-08:49, 12:43-13:00 | 32 min | - | first run cut by the lead's own timeout |
| - | PAUSE 1 (usage limit) | - | 08:50-12:41 | 3 h 51 min | - | not work |
| 11 | SimCoder-OpusXHigh | opus (xhigh) | 12:45-13:28, 10-23 01:00-01:07, 05:53-05:59 | about 56 min | 23,921,786 | done; cut once |
| 12 | UsdaExt-OpusHigh | opus (high) | 12:45-13:14 | 29 min | 10,022,511 | done |
| 13 | SpecReviewer (worker-xhigh) | asked fable, ran sonnet 5.5 (xhigh) | 13:03-13:20 | 17 min | 10,244,818 | GO, 16 advisory |
| 14 | Lead: spec v2, canary quote and buy | opus (xhigh) | 13:20-13:48 | 28 min | (lead) | 6.107772 USD |
| 15 | FixCoder-OpusXHigh | opus (xhigh) | 13:25-13:29, 10-23 01:00-01:28, 05:53-05:57 | about 36 min | 18,182,550 | done; cut twice |
| - | PAUSE 2 (usage limit, reboot about 15:33) | - | 13:29-10-23 00:57 | 11 h 28 min | - | not work |
| 16 | EngineReviewer (worker-xhigh) | asked fable, ran sonnet 5.5 (xhigh) | 10-23 01:09-01:27 | 18 min | 11,534,387 | NO GO, 1 blocking (fixed) |
| - | PAUSE 3 (usage limit) | - | 10-23 01:28-05:51 | 4 h 23 min | - | not work |
| 17 | ReCheck (worker-xhigh) | asked fable, ran sonnet 5.5 (xhigh) | 10-23 06:00-06:11 | 11 min | 9,632,677 | A GO, B GO |
| 18 | Full quote and buy (detached) | - | 10-23 06:11-12:31 | 6 h 20 min | - | 121.645551 USD, 156 settled |
| 19 | verify31, SAFE TO WIPE, measurement, stats (lead) | - | 10-23 12:33-12:51 | 18 min | - | verify rc 3; 816 dates; FAIL |
| 20 | PilotVerifier (worker-xhigh) | asked fable, ran sonnet 5.5 (xhigh) | 10-23 12:51-13:14 | 23 min | 8,914,021 | CONFIRMED |
| 21 | Full pytest (detached) | - | 10-23 13:14-13:34 | 20 min | - | 8090 passed, 1 known failure |
| 22 | OpusVerifier-OpusXHigh | opus (xhigh) | 10-23 13:16-13:40 | 24 min | 7,061,679 | CONFIRMED |
| 23 | Lead: return, progress, STAGES, commit | opus (xhigh) | 10-23 13:41-13:50 | 9 min | (lead) | done |
| - | Lead, whole stage | opus 5.5 (xhigh) | - | - | 61,989,915 | - |
| total | Stage E.31 | - | 10-22 07:47-10-23 13:50 | work 10 h 21 min (pauses 19 h 42 min) | 212,505,025 | initial estimate: done by 22:50 on 10-22 (15 h 03 min) |

Did xhigh on the lead pay? It is the prompt's setting. The cost driver was cache reads (95.6% of all tokens), from long
worker contexts resumed across pauses (SimCoder 23.9M, DataResearch 21.6M, FixCoder 18.2M).

