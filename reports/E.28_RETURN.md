# Stage E.28 return: the methods brief, the firm-contract ranking, and the order-book pilot

Stage E.28 ran in two lead sessions on 2026-10-21 (PDT): session 1 (bc87cf0f-1877-4bba-a4a0-51b0873c3865, Opus 5.5
xhigh, Max plan, ultracode on) from 02:06 until its call failed at 16:43 when the user moved to the Pro plan; session
2, Stage E.28b (c4961140-6cb5-4eeb-8deb-096950337c09, Opus 5.5 high, Pro plan, ultracode off, at most 2 workers), from
16:51, which finished Part B from disk under docs/prompts/STAGE_E.28b.md. Parts C and A were done in session 1 and
were not redone. N stays 538; nothing was tested or registered; REGISTRATION.md is 0 bytes.

## 1. Summary

**Methods brief (Part C).** The program did not fail for lack of mathematics: every return names costs, power, data
granularity, firm rules or data access as the binding constraint, and none names a missing method. 14 of 19 method
families were never used and 5 only in part; almost all need event-time order-book data, which the program never
bought. At retail latency no method is an edge on its own; their value is measurement of a passive order's worth,
P(fill) x (half-spread - adverse move) - fee. The brief (reports/stage_e28_methods_brief.md) recommends a phased
design: Phase 0 the pilot, Phase 1 one contract with a five-rung model ladder counted into N, Phase 2 a pooled model
on 2-3 matched contracts tested on an unseen one.

**Ranking (Part A).** Top pair: **Topstep x QM** (E-mini crude oil), S 2.484. Next four: MFFU x QM 2.427, Tradeify x QM
2.415, Bulenox x QM 2.388, Lucid x QM 2.353. The top pair moved from Topstep x QG after RankingReviewer's RR-01 and the
lead's v2 ruling; QM's place rests on statistics derived from CL (with OC-1 off, QM leaves the top five).

**Purchase (Part B).** Nothing was bought: DATABENTO_API_KEY3 was absent by name from 16:53 through the 20:30 PDT deadline (the delta
review gave GO at 17:22). No Databento call was made; acct-3 keeps its USD 125. The user has since put the pilot on
hold (V47, 21:53-21:57) until a QM volume check (E.30) passes and the spec is revised.

**Pilot.** Not run (no data). The code passes 204 of 204 tests; the exact commands are in section 3.

**The user decides:** how to revise the pilot spec if QM passes E.30 (V47), or which contract replaces QM if it fails; the review
standard; the v2 rulings and the Topstep fee reading (section 7).

## 2. Guardrail evidence

Start checks, session 1 (02:07-02:13, verbatim file reports/stage_e28_briefs/start_checks.txt): holdout all_ok True,
unlocks_logged 0 (top, holdout_2, MCL, MGC, MHG, NG); `wc -c REGISTRATION.md` = 0; ledger 36402 lines, sha256
034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700; git 0 tracked changes, HEAD 71d667f; N 538.

Start checks, session 2 (verbatim, reports/stage_e28_briefs/start_checks_b.txt, script checks_b.sh):

```
# E.28b checks: start
$ date
Wed Oct 21 16:53:07 PDT 2026
$ git status --short | wc -l (tracked changes: git status --short -uno)
1410
$ git log --oneline -3
9402789 docs: Stage E.28b prompt (E.28 continued on the Pro plan)
2615df4 Stage E.26 data move and housekeeping
95df9c6 feat: Stage E.26 ACCOUNT_3 (harness v14), V45, data-move git and test hygiene
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
r005-E20S: E20S ['E20S-01', 'E20S-02', 'E20S-03', 'E20S-04', 'E20S-05', 'E20S-06', 'E20S-07', 'E20S-08', 'E20S-09', 'E20S-10', 'E20S-11', 'E20S-12', 'E20S-13', 'E20S-14', 'E20S-15', 'E20S-16', 'E20S-17', 'E20S-18', 'E20S-19', 'E20S-20', 'E20S-21', 'E20S-22', 'E20S-23', 'E20S-24', 'E20S-25', 'E20S-26', 'E20S-27', 'E20S-28', 'E20S-29', 'E20S-30', 'E20S-31', 'E20S-32', 'E20S-33', 'E20S-34', 'E20S-35', 'E20S-36', 'E20S-37', 'E20S-38', 'E20S-39', 'E20S-40', 'E20S-41', 'E20S-42', 'E20S-43', 'E20S-44', 'E20S-45'] N 483 -> 528 at 2026-10-11T17:43:59-07:00
r006-E21: E21 ['E21-T1', 'E21-T2', 'E21-T3', 'E21-T4'] N 528 -> 532 at 2026-10-14T04:12:12-07:00
r007-E22: E22 ['E22-F1'] N 532 -> 533 at 2026-10-16T02:12:01-07:00
r008-E23: E23 ['E23-MEZFh5', 'E23-MEZNh5', 'E23-MEZBh5', 'E23-H6NQh5', 'E23-H6NQh20'] N 533 -> 538 at 2026-10-17T03:33:45-07:00
$ DATABENTO_API_KEY3 by name (.env and environment)
.env DATABENTO_API_KEY3: absent
env DATABENTO_API_KEY3: empty or unset
```

End checks (verbatim, reports/stage_e28_briefs/end_checks_b.txt):

```
# E.28b checks: end
$ date
Wed Oct 21 22:00:34 PDT 2026
$ git status --short | wc -l (tracked changes: git status --short -uno)
1417
 M docs/STAGES.md
$ git log --oneline -3
54f07ab docs: V47 (QM research, pilot on hold) and the Stage E.30 prompt (QM volume check)
84704b4 docs: V46 (user decisions of 2026-10-21, Pro plan) and the Stage E.29 prompt
9402789 docs: Stage E.28b prompt (E.28 continued on the Pro plan)
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
r005-E20S: E20S ['E20S-01', 'E20S-02', 'E20S-03', 'E20S-04', 'E20S-05', 'E20S-06', 'E20S-07', 'E20S-08', 'E20S-09', 'E20S-10', 'E20S-11', 'E20S-12', 'E20S-13', 'E20S-14', 'E20S-15', 'E20S-16', 'E20S-17', 'E20S-18', 'E20S-19', 'E20S-20', 'E20S-21', 'E20S-22', 'E20S-23', 'E20S-24', 'E20S-25', 'E20S-26', 'E20S-27', 'E20S-28', 'E20S-29', 'E20S-30', 'E20S-31', 'E20S-32', 'E20S-33', 'E20S-34', 'E20S-35', 'E20S-36', 'E20S-37', 'E20S-38', 'E20S-39', 'E20S-40', 'E20S-41', 'E20S-42', 'E20S-43', 'E20S-44', 'E20S-45'] N 483 -> 528 at 2026-10-11T17:43:59-07:00
r006-E21: E21 ['E21-T1', 'E21-T2', 'E21-T3', 'E21-T4'] N 528 -> 532 at 2026-10-14T04:12:12-07:00
r007-E22: E22 ['E22-F1'] N 532 -> 533 at 2026-10-16T02:12:01-07:00
r008-E23: E23 ['E23-MEZFh5', 'E23-MEZNh5', 'E23-MEZBh5', 'E23-H6NQh5', 'E23-H6NQh20'] N 533 -> 538 at 2026-10-17T03:33:45-07:00
$ DATABENTO_API_KEY3 by name (.env and environment)
.env DATABENTO_API_KEY3: absent
env DATABENTO_API_KEY3: empty or unset
$ DATABENTO_API_KEY3 by name via data.config._read_env_file (value never read into output)
KEY3 absent or empty
```

The full untracked-path lists of `git status --short` are in start_checks.txt; they are E.13/E.26 pages and other
stages' scratch, not this stage's. No pytest run of the repo suite (E.28 rule); only the pilot folder's own tests.

Order of events (PDT; details in reports/stage_e28_STATE.md):
- 02:14 ranking spec hashed before any lookup; 02:20 reader queue (C1, 11 C2 deep dives, A0, A1 x8, A2 x6).
- 03:10-05:10, 06:19-10:10, 11:10-15:10 usage-limit pauses (not work time).
- 05:19 brief v1 assembled; 06:05-11:11 MathReviewer G1-G6 (Fable); 10:12-16:08 A3 fact table, blind scorer, economics.
- 15:13 lead rulings v1; 15:16 Part C final (brief v2, sha256 e8c3fd71a648fcb7).
- 15:15 B1/B2 drafted; 15:18-16:00 PilotCoder (code, synthetic tests, no Databento call).
- 16:05 ranking v1 (Topstep QG); 16:08 spec filled for QG; 16:09-16:35 SpecReviewer and RankingReviewer (Fable).
- 16:34 spec fixes RS-01..13; 16:36 lead rulings v2; 16:41 ranking v2 (Topstep QM), spec re-filled for QM, sha256
  8937740338e81103b0a5a3edcf90fab46d1aa62140bcaf7abb309a7fdc87d0ae (frozen; unchanged to the end).
- 16:43 session 1 cut (Pro plan). 16:51 session 2 start; 16:53 start checks; DATABENTO_API_KEY3 absent by name.
- 16:54-17:05 PilotFixer (S1); 17:06-17:14 DeltaReviewer: NO GO (RD-01, RD-02); 17:14-17:20 fixes; 17:20-17:22 re-check: GO.
- 17:15 reports/stage_e28_ranking.md written (v2). Between 17:22 and 17:24 (not timed) a push notification told the user the key is missing; a name-only poll for the key ran until 20:25.
- 19:15 user commit 84704b4 (V46, the E.29 prompt) appeared during the wait; not this stage's file, not staged.
- 20:25 the key watch's planned end; it reported completion (exit 0), but its output file was on /tmp (RAM) and was
  lost in the reboot.
- 20:30 purchase deadline passed with the key absent: nothing bought (S3).
- 20:42 the laptop rebooted (uptime -s 20:42:39). 21:54 session resumed; the user confirmed the key still absent. The
  key watch was not restarted.
- 21:58 user commit 54f07ab (V47: QM research, the pilot on hold, acct-3 kept; the E.30 prompt), seen at the end
  checks; not this stage's file, not staged. Section 7 follows it.
- - 21:54-22:02 S5: V47 read, return section 7 rewritten to follow it, progress entry, STAGES line, end checks (22:00),
  session cost (22:02); then one commit, no push.

## 3. Results

### Part C: the methods brief

reports/stage_e28_methods_brief.md (1.1 MB, sha256 e8c3fd71a648fcb7...; final at 15:16; not re-read in E.28b).
Contents:

- Part 0. Headline
- Part 1 (C1). Gap inventory: every method the program used, and what it never used
- Part 2 (C2). Deep dives on the methods it never used
  - 2.0 All verdicts in one table
  - 2.1 Stochastic calculus and continuous-time models (Ito, jump-diffusions, Ornstein-Uhlenbeck)
  - 2.2 Point processes: Poisson and Hawkes order arrivals
  - 2.3 Limit-order-book models and the mathematics of fill probability
  - 2.4 Stochastic optimal control, HJB, market making (Avellaneda-Stoikov, Gueant) and execution (Almgren-Chriss)
  - 2.5 Filtering: Kalman, particle filters, hidden Markov regimes
  - 2.6 Random-matrix cleaning, Bayesian shrinkage, information theory
  - 2.7 Fractional differencing, meta-labeling, purged CV, wavelets and spectral methods
  - 2.8 Machine learning on order-book data I: DeepLOB and later deep models
  - 2.9 Machine learning on order-book data II: order-flow imbalance, trees, labels, latency
  - 2.10 Single-contract versus pooled multi-contract models
  - 2.11 How top firms run the research process
- Part 3 (C3). Does the missing mathematics explain the program's failures?
- Part 4 (C4). The recommended method set and a draft design for the order-book ML search under V43

C3's answer: costs and data granularity were binding, not missing mathematics (Part 3). C4: Part 4 (phases, trial
counting into N, purged and embargoed CV by trade date, one test on data that never selected it, hardware).

### Part A: the ranking

reports/stage_e28_ranking.md (v2, final; spec sha256 89347e97...). Top 12 of the primary table:

| Rank | Firm | Code | E | D | R | A | F | P | Rel | L2 | L1 | S | mu*_lim | mu*_mkt | mu10K | cost/attempt | room | gates | u |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | topstep | QM | 3.17 | 1 | 4 | 2 | 1 | 2 | 3 | 2.569 | 2.400 | 2.484 | 0.32 | 1.32 | 0.54 | 50.53 | 1.64 | ok |  |
| 2 | mffu | QM | 3.01 | 1 | 4 | 2 | 1 | 1 | 3 | 2.454 | 2.400 | 2.427 | 0.35 | 1.35 | 0.90 | 153.00 | 1.64 | ok |  |
| 3 | tradeify | QM | 2.95 | 1 | 4 | 2 | 1 | 1 | 3 | 2.429 | 2.400 | 2.415 | 0.43 | 1.43 | 0.75 | 95.83 | 1.64 | ok |  |
| 4 | bulenox | QM | 2.44 | 2 | 4 | 2 | 1 | 2 | 3 | 2.375 | 2.400 | 2.388 | 0.72 | 1.72 | 1.06 | 175.00 | 2.05 | ok |  |
| 5 | lucid | QM | 2.89 | 1 | 4 | 2 | 1 | 1 | 2 | 2.306 | 2.400 | 2.353 | 0.44 | 1.44 | 0.88 | 120.87 | 1.64 | ok | fee |
| 6 | topstep | ZM | 2.69 | 2 | 4 | 2 | 1 | 2 | 3 | 2.475 | 2.150 | 2.312 | 0.59 | 1.59 | 0.86 | 49.23 | 2.08 | ok |  |
| 7 | topstep | MGC | 0.00 | 4 | 4 | 2 | 1 | 2 | 3 | 1.600 | 2.950 | 2.275 | > 4 | > 4 | > 4 | 99.57 | 9.09 | ok |  |
| 8 | bulenox | MGC | 0.00 | 4 | 4 | 2 | 1 | 2 | 3 | 1.600 | 2.950 | 2.275 | > 4 | > 4 | > 4 | 175.00 | 11.36 | ok |  |
| 9 | lucid | MGC | 0.31 | 4 | 4 | 2 | 1 | 1 | 2 | 1.573 | 2.950 | 2.262 | 1.78 | 2.78 | > 4 | 120.87 | 9.09 | ok | fee |
| 10 | mffu | ZM | 2.50 | 2 | 4 | 2 | 1 | 1 | 3 | 2.349 | 2.150 | 2.250 | 0.62 | 1.62 | 1.30 | 153.00 | 2.08 | ok |  |
| 11 | mffu | MGC | 0.00 | 4 | 4 | 2 | 1 | 1 | 3 | 1.550 | 2.950 | 2.250 | 2.38 | 3.38 | > 4 | 153.00 | 9.09 | ok |  |
| 12 | tradeify | MGC | 0.00 | 4 | 4 | 2 | 1 | 1 | 3 | 1.550 | 2.950 | 2.250 | > 4 | > 4 | > 4 | 95.83 | 9.09 | ok |  |

Columns: E, D, R, A, F, P, Rel are the Layer 2 criteria; L2, L1 and S the scores; mu*_lim and mu*_mkt the break-even
gross edge per trade in ticks (limit and market cost case); mu10K the edge to reach USD 10K; cost/attempt in USD;
room the limit room (see the ranking spec). The variants, ties and the Lucid fee reading are in the ranking file.

### Part B: the pilot

- Schema decision (B1): mbp-1, the cheapest schema that supports the conservative fill rule, queue times and markouts
  (spec section 1). Minimum span for QM: [2024-01-12, 2024-02-29T22:00:00Z), 26 usable trade dates after holiday and
  roll exclusions (spec section 6, RS-07; DeltaReviewer counts about 29 usable).
- Frozen spec (B2): reports/stage_e28_pilot_spec.md, sha256
  8937740338e81103b0a5a3edcf90fab46d1aa62140bcaf7abb309a7fdc87d0ae. Contract QM (QM.v.0), FIFO, tick 0.025 / 12.50
  USD, FEE_SIDE 0.1368 (and 0.296 conservative), sim rule trade_through_only, latency 50 ms (assumption), request end
  2024-02-29T22:00:00Z. Spend target TARGET = B - max(3.00, 0.03 B), 121.25 USD at B = 125.00.
- Code: reports/stage_e28_briefs/work/B_pilot/ (pilot_pull.py, verify.py, pilot_stream.py, measure_core.py,
  measure_stats.py, measure.py, README.md); 204 of 204 tests pass; fix log FIXES_E28b.md.
- Quote, purchase, manifest: none. No quote was taken either: a quote needs the key, and the spend rule (RS-08) approves exactly a fresh quote
logged just before the buy. The ledger's line count and sha256 are the same at session 1's start, session 2's start
and the end (section 2). The commands below buy the frozen spec, which V47 has put on hold; they apply only if the
user lifts the hold with the spec unchanged. From work/B_pilot/README.md sections 2-4 (P=reports/stage_e28_briefs/
work/B_pilot; B = acct-3's balance, at most 125.00; D = the first trade date the span search returns, no later than
2024-01-12; APPROVED = exactly the fresh quote):

  ```bash
  uv run python $P/pilot_pull.py --span-search --root QM --balance-usd B --out $P/runs/span_QM.json
  uv run python $P/pilot_pull.py --quote --root QM --first-trade-date D --out $P/runs/quote_QM.json
  LOG=$P/runs/buy_QM.log
  setsid nohup bash -c "nice -n 10 uv run python $P/pilot_pull.py --buy --root QM \
      --first-trade-date D --balance-usd B --approved-usd APPROVED >> $LOG 2>&1; \
      echo \"rc=\$? \$(TZ=America/Vancouver date '+%F %T %Z')\" >> $LOG" > /dev/null 2>&1 &
  ```

  Then verify.py (README section 5) with the required --purchase-record. "ACCOUNT_3 SAFE TO WIPE" goes into the STATE
  file with the time only after verify.py exits 0, or 3 for data-quality findings only (RS-09).
- Pilot results: not run (no data). Command (README section 6), DBN being the verified file under
  /mnt/large-storage/market_data/PropExperiment/data/vendor/databento/GLBX.MDP3/mbp-1/QM_v_0/:

  ```bash
  OUT=$P/runs/measure_QM; LOG=$P/runs/measure_QM.log
  setsid nohup bash -c "uv run python $P/measure.py --root QM --tick 0.025 --fee-side 0.1368 \
      --fee-side-alt 0.296 --sim-rule trade_through_only --dbn $DBN --out-dir $OUT --workers 2 \
      --label Topstep >> $LOG 2>&1; \
      echo \"rc=\$? \$(TZ=America/Vancouver date '+%F %T %Z')\" >> $LOG" > /dev/null 2>&1 &
  ```

  measure.py sets nice 10 itself. Its run time on real data is not measured.

## 4. Delegation record

Session 2 (E.28b), lead Opus 5.5 high:

| Agent | Effort file | Model | Task | Start-end (PDT) | Result |
|---|---|---|---|---|---|
| PilotFixer-OpusXHigh | worker-xhigh | opus | S1: RS fixes for QM; round 2: RD-01..03 | 16:54-17:05; 17:14-17:20 | 168 then 204 tests pass; FIXES_E28b.md |
| DeltaReviewer-OpusXHigh | worker-xhigh | opus | S2: delta review (ranking v2, QM parameters, code); one re-check | 17:06-17:14; 17:20-17:22 | NO GO (RD-01, RD-02), then GO; R_delta.md |

Session 1: 60 spawns, listed with tokens in section 8. Roles: MethodsInventory, MethodReader x11, ContractStats,
ContractReader x8, FirmReader x5, PlatformReader (opus high); FactTable-OpusHigh, BlindScorer-OpusXHigh,
EconCoder-OpusXHigh; MathReviewer-FableXHigh x6; BriefFixer-SonnetHigh x6; ScoreApplier and ScoreApplierV2 (sonnet
high); RankingReviewer-FableXHigh, SpecReviewer-FableXHigh; PilotCoder-OpusXHigh. Re-runs after usage-limit cuts
appear as separate spawns.

## 5. Verification

- MathReviewer-FableXHigh G1-G6 (Part C): 3 BLOCKING, 38 SHOULD FIX, 79 NOTE; all BLOCKING and SHOULD FIX applied;
  one verdict changed (HMM gate, use to maybe). Per-group table in the brief's Part 5; reviews R_math_G1..G6.md, fix
  logs R_fix_G1..G6.md.
- RankingReviewer-FableXHigh (Part A, R_rank.md): recomputation exact (0 mismatches, 47 candidates, 126 pairs; seed
  stable). RR-01 BLOCKING (conditional) -> ruling v2 RR-01 (QG's all-UNKNOWN C1(b) = high; QG fails the L1 gate; top
  pair becomes Topstep QM). RR-03, RR-04, RR-05 SHOULD FIX -> rulings v2. RR-02 (Topstep 3.70 USD per lot vs per-product
  fee): per-product fee governs; 0.296 tick per side reported as the conservative reading. 9 NOTEs recorded.
- SpecReviewer-FableXHigh (Part B, R_spec.md, on the QG spec): GO WITH FIXES. RS-01 BLOCKING (request end) -> fixed
  (end 2024-02-29T22:00:00Z; verify cutoff 23:00Z). RS-02 FIFO confirmed. RS-03..RS-08 SHOULD FIX and RS-09..RS-13
  NOTE -> all applied in the spec (16:34) and the code (16:37-16:41 and E.28b S1).
- DeltaReviewer-OpusXHigh (E.28b, R_delta.md; an Opus stand-in for Fable, see OC-B1): v2 ranking recomputed (top pair
  and next four confirmed; only C40 has all C1(b) fields UNKNOWN); every QM parameter row matches its source; section 6
  arithmetic confirmed (610 and 915 fills; 26 days; 121.25). RD-01 BLOCKING (any root; a second buy possible) -> QM
  only in every pilot_pull mode, one purchase on acct-3. RD-02 BLOCKING (end not pinned) -> end must equal
  2024-02-29T22:00:00Z. RD-03 SHOULD FIX (purchase record optional) -> required, sha256 per file. RD-04..RD-09 NOTE
  (wording; 3,202 vs 3,201 placements, no effect; QM rolls estimated from expiry rules). Re-check: GO, 28 new
  adversarial tests pass.
- Limit: the DeltaReviewer is the same model as the authors (Opus 5.5), so errors both share are less likely to be
  caught than under Fable (OC-B1).

## 6. Open choices

Every decision a lead made on its own, with the reason. Session 1 numbers (OC-1 to OC-7, OC-11) are from
reports/stage_e28_STATE.md and the rulings files; OC-8 to OC-10 are not recorded on disk (session 1's transcript uses
"OC-10" only as a group label for the A3 rulings below), so those choices are listed by content.

Session 1 (Parts C, A and B1/B2):
- OC-1: price statistics in ticks for a candidate with no owned window data are derived from an owned sibling on the
  same underlying price (x_ticks(cand) = x_ticks(sibling) x tick(sibling) / tick(cand)); volume never transfers.
  Reason: the same price process; the alternative leaves 10 micros and minis unscored. QM's rank depends on it.
- OC-2: ADV from owned v.0 front-month bars where owned, else the published figure. Reason: one source per
  contract where possible; a variant OC2_published is shown.
- OC-3: firm reliability: no deduction for an undocumented item; an unknown founding date deducts. Reason: absence of
  a record is not evidence of a problem, but an unknown age is a real risk.
- OC-4: the F (fill) criterion rated on the API platform the strategy would use. Reason: that is the fill rule the
  strategy would meet.
- OC-5: no quote, balance check or purchase before Parts A and C were finished. Reason: the prompt's order.
- OC-6: a C6 rating may not rest only on abstract or snippet evidence at either extreme (no 0, no >= 3). Reason:
  unverified evidence cannot exclude or promote a contract.
- OC-7: futures-broad order-book evidence floors C6 at 2 (the spec's level-2 anchor). Reason: the spec's own words.
- OC-A3-1 to OC-A3-11 (rulings v1, A3_lead_rulings.json, written at 15:13 before any ranking output was read):
  MNG passes the 60-date listing gate by the common inference; unknown D and E components score 1 (variants at 0
  shown); FactTable's QV and C4 readings accepted (variants shown); big-move counts transfer to OC-1 siblings
  (primary; no-transfer variant shown); a 0-contract cap at 50K means not listed; the rest accepted as written.
  BlindScorer's alternatives: the primary ratings stand (C07, C15; F04 A = 2).
- OC-11 (rulings v2, A3_lead_rulings_v2.json, 16:36, written after RankingReviewer and after the v1 top pair was
  known): RR-01 applied literally (QG's all-UNKNOWN C1(b) = high; QG fails the L1 gate), RR-03 (abstract-only grain
  C6 capped at 2), RR-04 (Topstep R by size), RR-05 (Lucid fee unknown, u-rule). Reason: each is the literal reading
  of the frozen spec or of the lead's v1 clauses; DeltaReviewer confirms RR-01 is literal and notes that leaving
  partly evidenced ratings as rated is itself a choice. This changed the top pair from Topstep QG to Topstep QM.
- MathReviewer findings: all BLOCKING and SHOULD FIX applied as proposed; NOTEs only where factual with exact text.
  Reason: no basis to overrule a reviewer that re-derived each item.
- Usage-limit handling: the review prompt was amended to write R_math files early; fewer agents at once after the
  cuts; cut agents' complete files reused as they stand (Bulenox reader; MathReviewer G1, G4, G6) and EconCoder
  resumed. Reason: workflow agents cut by a limit lose unsaved work.
- B1/B2: PilotCoder's ambiguity 14 resolved by trade date (request end 2024-02-29T22:00:00Z, no record of trade date
  2024-03-01); its other 14 resolutions accepted. QM's FIFO matching confirmed by the lead from SpecReviewer's saved
  CME sheets (later re-confirmed by DeltaReviewer). Topstep's fee: the per-product 3.42 USD round trip is primary
  (RR-02); 3.70 USD per lot read as per side is reported as the conservative alternative.
- The spec was re-filled for QM after SpecReviewer had reviewed the QG version; QM's parameters were reviewed only by
  E.28b's DeltaReviewer.

Session 2 (E.28b):
- OC-B1: no Fable on the Pro plan; every remaining Fable review became DeltaReviewer-OpusXHigh in a fresh context
  (prompt E.28b). Reason: the prompt; cost: correlated errors with the Opus-written work are less likely to be caught.
- S1 done by one worker (PilotFixer-OpusXHigh) rather than the lead. Reason: test runs and edits across seven modules
  would have filled the lead's small Pro context.
- OC-B2 to OC-B6 (PilotFixer round 1 questions): --root left to the reviewer (it became RD-01 and was fixed); VPO also
  reported at the 0.296 fee (extra conservative output, headline unchanged); verify always run with
  --purchase-record (later made mandatory, RD-03); "fills within 60 s" includes the 50 ms cancel latency as the spec
  says (wording only); RS-13 implemented as a clip, not an assert (identical under the spec grid).
- RD-01 to RD-03 rulings: QM is the only root any pilot_pull mode accepts; one purchase on acct-3; the request end must
  equal 2024-02-29T22:00:00Z; verify.py refuses to run without the purchase record and checks every file's sha256.
  Reason: each closes a path to buying the wrong thing; none changes the frozen spec.
- OC-B7 to OC-B9 (round 2 questions): verify.py and measure.py not pinned to QM (they act on the bought file and its
  record); --quote allowed after a purchase (free; adds a ledger line); any committed acct-3 purchase blocks a second
  (acct-3 is pilot-only, V45). DeltaReviewer rated all three NOTE.
- The key was absent at the start. The lead finished S1 and S2 anyway so the code would be ready, sent the user one
  push notification, and polled for the key by name only (never the value) every 60 s until 20:25.
- reports/stage_e28_ranking.md built from the v2 table verbatim with a new front page (rank_front_v2.md); session 1's
  QG-era front is kept unchanged in work/lead/rank_front.md.
- Session cost from reports/stage_e26_briefs/cost.py (the rglob copy that counts workflow agents); the E.10 script
  misses them.
- No quote was taken while waiting, though a quote is free: a quote needs the key, and the spend rule wants a fresh
  one right before the buy.
- After the reboot the key watch was not restarted (user instruction); the key's absence after 20:30 rests on the
  user's word and on the end check by name.
- V47 (committed 21:58, during S5) was read and section 7 written to follow it: no purchase is recommended, and the
  open items are framed around E.30 and the spec revision V47 asks for.
- Commit scope: this stage's documents and the briefs' notes, tables, scripts, tests and logs; not the raw fetched
  pages under reports/stage_e28_briefs/pages/ (876 MB with duplicates), the CFTC COT downloads under work/A1_*/cot/,
  or raw .html/.xml/.js under work/, as in E.23 and E.25 (whose pages are untracked). They stay on disk.
- cost/per_agent.py changed to print PDT times and a minutes column; session 1's table was regenerated (tokens
  unchanged).
- Session 2's cost was computed just before the commit; the few calls after it (staging, the commit, the closing
  reply) are not in its table.

## 7. Decisions for the user

Already decided by the user in V47 (21:53-21:57): the pilot purchase is on hold; acct-3 is kept, not wiped; no
QM-only purchase until E.30's QM volume check passes and the pilot spec is revised. What remains open:

Pro-fit: runs in a short Pro session (opus high, at most 2 workers). Max-sized: needs Max usage, Fable or a long
session.

1. **The spec revision, if QM passes E.30 (Pro-fit for the drafting and code; the review is Max-sized if Fable).**
   The frozen spec and the code pin QM as the only root, the request end at 2024-02-29T22:00:00Z and one purchase on
   acct-3. Each of V47's changes touches those guards. A synchronized CL top of book is a second contract, which
   every pilot_pull mode now refuses (RD-01). A 2025-2026 sample lies after 2024-03-01, where E.28's prompt forbade
   any read or purchase (research window, holdout-2, embargo), so it needs the user's ruling on those windows as well
   as the separate approval V47 names. A back-of-queue model beside trade-through-only is a new measure path, and the
   kill rule is a new pre-purchase declaration. So the revised spec needs a new freeze, code changes, tests and an
   independent review before any purchase. Recommendation: write it as a new spec file (keep the frozen one and its
   hash as the record) and review it with Fable when available.
2. **If QM fails E.30: which contract replaces it (Pro-fit).** In stage_e28_ranking.md's variants, Topstep x ZM leads
   with OC-1 off, followed by MGC pairs. V47 item 4's research on ZM and MGC feeds this. Recommendation: choose the
   replacement by the ranking with OC-1 off for the excluded contract only, and re-fill a new spec for it.
3. **Review standard for any later purchase (Pro-fit).** Accept an Opus stand-in review in a fresh context (V46
   item 5, while Fable is unavailable) or wait for Fable xhigh. Recommendation: for a bounded pilot-only spend, the Opus
   stand-in is acceptable. Have Fable check the pilot's numbers before any verdict rests on them.
4. **The v2 rulings (Pro-fit).** RR-01, RR-03, RR-04 and RR-05 were written after the v1 top pair was known.
   Recommendation: accept; RR-01 is the spec's literal text for a candidate with no evidence (R_delta.md, section a).
   Alternative: v1, under which Topstep x QG leads.
5. **Topstep's QM fee (Pro-fit).** USD 3.42 per round trip (per-product, primary) or USD 3.70 per lot read as per
   side (conservative, 0.296 tick per side). The measurement reports both; which governs a verdict is the user's
   call. Recommendation: check Topstep's current fee page or ask support before any measurement is read.
6. **Unfinished review items (Max-sized if done by Fable).** R_delta.md lists three items it did not finish: a
   field-by-field v1/v2 diff, the rank-10 tie against the tie rule, and E for the 37 rows with a non-numeric input.
   It confirmed the top five by its own recomputation.
7. **Next steps by size.** Pro-fit: E.30's volume check, the spec revision and its code, E.29's simulation (its
   prompt, line 24, allows it "after E.28b ends without one"). Max-sized: a Fable review of the revised spec, the
   methods brief's Phase 1 (one contract, a five-rung model ladder counted into N, purged and embargoed CV, Fable
   reviews) and Phase 2's pooled model on 2-3 contracts (GPU, more data purchases).

## 8. Session cost

Tokens are from the transcripts, per message at its final usage, by reports/stage_e26_briefs/cost.py (the copy
that also globs workflow agents); never estimated. Session 1: transcript bc87cf0f, window 2026-10-21 01:00-24:00 PDT,
output reports/stage_e28_briefs/cost/cost_session1.txt. Session 2: transcript c4961140 through 22:02 PDT
(cost_session2.txt); the few calls after that (the commit and the closing reply) are not counted.

Wall clock. Session 1: 02:06-16:43 = 14 h 37 min, with usage-limit pauses 03:10-05:10, 06:19-10:10 and 11:10-15:10
(9 h 51 min, not work): work about 4 h 46 min. Session 2: 16:51-22:02; work 16:51-17:25 (34 min) and 21:54-22:02;
the wait for the key (17:25-20:30, a name-only poll, no work), the idle 20:30-20:42 and the reboot outage
20:42-21:54 are not work.

Session 1:

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---:|---:|---:|---:|---:|
| claude-opus-5-5 | 7,628 | 3,552,572 | 699,284,400 | 12,697,818 | 715,542,418 |
| claude-fable-5-1 | 7,418 | 999,352 | 41,026,571 | 3,221,371 | 45,254,712 |
| claude-sonnet-5-5 | 222 | 112,074 | 9,249,346 | 1,418,328 | 10,779,970 |
| all | 15,268 | 4,663,998 | 749,560,317 | 17,337,517 | 771,577,100 |

Session 2:

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---:|---:|---:|---:|---:|
| claude-opus-5-5 | 578 | 280,726 | 49,104,369 | 1,317,906 | 50,703,579 |
| all | 578 | 280,726 | 49,104,369 | 1,317,906 | 50,703,579 |

Both sessions:

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---:|---:|---:|---:|---:|
| claude-opus-5-5 | 8,206 | 3,833,298 | 748,388,769 | 14,015,724 | 766,245,997 |
| claude-fable-5-1 | 7,418 | 999,352 | 41,026,571 | 3,221,371 | 45,254,712 |
| claude-sonnet-5-5 | 222 | 112,074 | 9,249,346 | 1,418,328 | 10,779,970 |
| all | 15,846 | 4,944,724 | 798,664,686 | 18,655,423 | 822,280,679 |

Lead versus workers: lead 99,313,743 (session 1 83,468,827, session 2 15,844,916), 12.1%; workers
722,966,936 (62 spawns: 60 in session 1, 2 in session 2), 87.9%. By tier: Opus 93.2%, Fable
5.5%, Sonnet 1.3%. Cache reads are 97.1% of all tokens.

Per worker spawn, session 2 (cost/per_agent_session2.md):

| Agent | Effort file | Model | Run | First (PDT) | Last (PDT) | Min | Tokens |
|---|---|---|---|---|---|---|---|
| PilotFixer-OpusXHigh | worker-xhigh | claude-opus-5-5 | Agent tool | 16:54 | 17:20 | 27 | 23,722,826 |
| DeltaReviewer-OpusXHigh | worker-xhigh | claude-opus-5-5 | Agent tool | 17:06 | 17:21 | 16 | 11,135,837 |

2 spawns, 34,858,663 tokens. Min is first to last message, so it includes any usage-limit pause the agent spanned.

PilotFixer's and DeltaReviewer's spans include the idle time between their two rounds (17:05-17:14, 17:14-17:20).

Per worker spawn, session 1 (cost/per_agent_session1.md; times PDT; re-runs after usage-limit cuts are separate rows):

| Agent | Effort file | Model | Run | First (PDT) | Last (PDT) | Min | Tokens |
|---|---|---|---|---|---|---|---|
| MethodsInventory-OpusHigh | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 02:20 | 02:30 | 10 | 13,795,423 |
| MethodReader-OpusHigh:DeepLOB | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 02:20 | 02:42 | 22 | 23,906,218 |
| MethodReader-OpusHigh:LOB | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 02:20 | 02:44 | 24 | 24,646,665 |
| MethodReader-OpusHigh:Hawkes | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 02:20 | 02:48 | 28 | 20,773,596 |
| MethodReader-OpusHigh:SDE | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 02:20 | 02:44 | 24 | 18,842,025 |
| MethodReader-OpusHigh:Control | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 02:20 | 02:39 | 19 | 18,615,449 |
| ContractStats-OpusHigh | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 02:30 | 02:41 | 11 | 3,752,211 |
| MethodReader-OpusHigh:OFI | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 02:39 | 02:58 | 19 | 16,804,677 |
| MethodReader-OpusHigh:Pooled | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 02:41 | 02:57 | 16 | 15,027,211 |
| MethodReader-OpusHigh:Filter | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 02:42 | 03:03 | 20 | 14,902,101 |
| MethodReader-OpusHigh:StatsRMT | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 02:44 | 03:10 | 26 | 14,017,814 |
| MethodReader-OpusHigh:AFML | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 02:44 | 03:09 | 25 | 18,546,707 |
| MethodReader-OpusHigh:Firms | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 02:49 | 03:06 | 17 | 17,051,614 |
| ContractReader-OpusHigh:crude | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 02:57 | 03:09 | 13 | 8,935,952 |
| ContractReader-OpusHigh:natgas | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 02:58 | 03:09 | 12 | 5,990,880 |
| ContractReader-OpusHigh:metals | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 03:03 | 03:10 | 7 | 1,794,397 |
| ContractReader-OpusHigh:fx | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 03:06 | 03:10 | 5 | 2,066,482 |
| MethodReader-OpusHigh:StatsRMT | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:11 | 05:17 | 6 | 3,593,700 |
| ContractReader-OpusHigh:crude | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:11 | 05:30 | 19 | 16,989,790 |
| MethodReader-OpusHigh:Firms | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:11 | 05:12 | 1 | 516,471 |
| MethodReader-OpusHigh:AFML | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:11 | 05:12 | 1 | 902,903 |
| ContractReader-OpusHigh:natgas | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:11 | 05:30 | 19 | 18,310,823 |
| ContractReader-OpusHigh:metals | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:11 | 05:45 | 34 | 20,608,214 |
| ContractReader-OpusHigh:fx | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:12 | 05:38 | 26 | 21,080,703 |
| ContractReader-OpusHigh:crypto | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:12 | 05:42 | 30 | 23,308,486 |
| ContractReader-OpusHigh:equity | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:17 | 05:43 | 25 | 22,635,808 |
| ContractReader-OpusHigh:rates | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:30 | 06:11 | 41 | 35,949,333 |
| ContractReader-OpusHigh:grains | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:30 | 06:08 | 37 | 29,271,958 |
| FirmReader-OpusHigh:topstep | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:38 | 05:59 | 21 | 18,921,688 |
| FirmReader-OpusHigh:lucid | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:42 | 06:04 | 22 | 14,624,972 |
| FirmReader-OpusHigh:tradeify | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:43 | 06:10 | 27 | 17,489,540 |
| FirmReader-OpusHigh:mffu | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:45 | 06:01 | 16 | 11,435,575 |
| FirmReader-OpusHigh:bulenox | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 05:59 | 06:19 | 20 | 13,437,402 |
| PlatformReader-OpusHigh | worker-high | claude-opus-5-5 | wf_aafdf932-52a | 06:01 | 06:17 | 15 | 15,585,926 |
| MathReviewer-FableXHigh:G2 | worker-xhigh | claude-fable-5-1 | wf_6a9d64d8-26a | 06:05 | 06:18 | 14 | 4,394,703 |
| MathReviewer-FableXHigh:G5 | worker-xhigh | claude-fable-5-1 | wf_cc674605-c65 | 06:08 | 06:22 | 14 | 1,948,818 |
| MathReviewer-FableXHigh:G3 | worker-xhigh | claude-fable-5-1 | wf_32286c51-7c5 | 06:10 | 06:21 | 11 | 1,682,644 |
| MathReviewer-FableXHigh:G4 | worker-xhigh | claude-fable-5-1 | wf_44c3806b-6c8 | 06:12 | 06:19 | 7 | 719,159 |
| EconCoder-OpusXHigh | worker-xhigh | claude-opus-5-5 | wf_b313fd3e-77a | 10:12 | 11:09 | 57 | 29,910,369 |
| FactTable-OpusHigh | worker-high | claude-opus-5-5 | wf_b313fd3e-77a | 10:12 | 10:36 | 24 | 20,468,921 |
| MathReviewer-FableXHigh:G2 | worker-xhigh | claude-fable-5-1 | wf_6016fd3f-f3f | 10:12 | 10:37 | 25 | 2,574,878 |
| MathReviewer-FableXHigh:G5 | worker-xhigh | claude-fable-5-1 | wf_6016fd3f-f3f | 10:12 | 10:31 | 19 | 3,341,331 |
| MathReviewer-FableXHigh:G3 | worker-xhigh | claude-fable-5-1 | wf_ddfb96f0-bd7 | 10:31 | 11:02 | 31 | 4,221,144 |
| BlindScorer-OpusXHigh | worker-xhigh | claude-opus-5-5 | wf_b313fd3e-77a | 10:36 | 10:54 | 19 | 7,203,034 |
| MathReviewer-FableXHigh:G4 | worker-xhigh | claude-fable-5-1 | wf_53f0af3a-a4e | 10:36 | 11:11 | 34 | 9,773,081 |
| MathReviewer-FableXHigh:G1 | worker-xhigh | claude-fable-5-1 | wf_92dc4ada-5dd | 10:38 | 11:08 | 30 | 4,854,154 |
| MathReviewer-FableXHigh:G6 | worker-xhigh | claude-fable-5-1 | wf_bb7d9819-7ac | 10:42 | 11:09 | 27 | 2,734,189 |
| EconCoder-OpusXHigh | worker-xhigh | claude-opus-5-5 | wf_b313fd3e-77a | 15:12 | 16:07 | 56 | 11,557,057 |
| BlindScorer-OpusXHigh | worker-xhigh | claude-opus-5-5 | wf_b313fd3e-77a | 15:12 | 15:13 | 2 | 1,010,675 |
| BriefFixer-SonnetHigh:G1 | worker-high | claude-sonnet-5-5 | wf_b778c409-c1a | 15:12 | 15:13 | 1 | 949,433 |
| BriefFixer-SonnetHigh:G2 | worker-high | claude-sonnet-5-5 | wf_b778c409-c1a | 15:12 | 15:13 | 1 | 849,821 |
| BriefFixer-SonnetHigh:G4 | worker-high | claude-sonnet-5-5 | wf_b778c409-c1a | 15:12 | 15:14 | 2 | 911,749 |
| BriefFixer-SonnetHigh:G3 | worker-high | claude-sonnet-5-5 | wf_b778c409-c1a | 15:12 | 15:13 | 1 | 511,302 |
| BriefFixer-SonnetHigh:G5 | worker-high | claude-sonnet-5-5 | wf_b778c409-c1a | 15:13 | 15:14 | 1 | 647,878 |
| BriefFixer-SonnetHigh:G6 | worker-high | claude-sonnet-5-5 | wf_b778c409-c1a | 15:13 | 15:15 | 2 | 1,506,667 |
| ScoreApplier-SonnetHigh | worker-high | claude-sonnet-5-5 | wf_6971bb48-723 | 15:13 | 16:06 | 53 | 2,461,132 |
| PilotCoder-OpusXHigh | worker-xhigh | claude-opus-5-5 | Agent tool | 15:18 | 16:43 | 85 | 37,790,821 |
| RankingReviewer-FableXHigh | worker-xhigh | claude-fable-5-1 | wf_cbe3e2d9-acc | 16:09 | 16:35 | 26 | 5,573,128 |
| SpecReviewer-FableXHigh | worker-xhigh | claude-fable-5-1 | wf_cbe3e2d9-acc | 16:09 | 16:32 | 23 | 3,437,483 |
| ScoreApplierV2-SonnetHigh | worker-high | claude-sonnet-5-5 | wf_997b4b50-44f | 16:37 | 16:41 | 4 | 2,941,988 |

60 spawns, 688,108,273 tokens. Min is first to last message, so it includes any usage-limit pause the agent spanned.

### Final ETA table (actuals)

No initial estimate table was found in either session's transcript (searched the lead's replies for an ETA table),
so the actuals stand without one. Worker tokens are in the per-spawn tables above; "lead" rows are in the lead totals.

| # | Task | Owner | Model | Effort | Start | End | Time | Tokens | Status, deviations |
|---|---|---|---|---|---|---|---|---:|---|
| A0 | Start checks | lead | opus | xhigh | 02:07 | 02:13 | 6 min | lead | done |
| A1 | Ranking spec hashed | lead | opus | xhigh | 02:14 | 02:14 | 1 min | lead | done, before any lookup |
| A2 | Readers: C1, C2 x11, A0, A1 x8, A2 x6; brief v1 | 27 workers, lead | opus | high | 02:20 | 05:19 | spans pause 1 | see table | done; cut agents re-run |
| P1 | **usage-limit pause** | | | | 03:10 | 05:10 | 2 h 00 min | | excluded |
| A3 | MathReviewer G1-G6; BriefFixers | 6 Fable + 6 Sonnet | fable, sonnet | xhigh, high | 06:05 | 11:11 | spans pause 2 | see table | done; G1, G4, G6 files reused after cuts |
| P2 | **usage-limit pause** | | | | 06:19 | 10:10 | 3 h 51 min | | excluded |
| A4 | Fact table, blind scorer, economics | FactTable, BlindScorer, EconCoder | opus | high, xhigh | 10:12 | 16:08 | spans pause 3 | see table | done; EconCoder resumed |
| P3 | **usage-limit pause** | | | | 11:10 | 15:10 | 4 h 00 min | | excluded |
| A5 | Rulings v1; Part C final | lead | opus | xhigh | 15:13 | 15:16 | 3 min | lead | done |
| A6 | B1/B2 drafts; pilot code | lead; PilotCoder-OpusXHigh | opus | xhigh | 15:15 | 16:00 | 45 min | see table | done |
| A7 | Ranking v1; spec for QG; two Fable reviews | lead; RankingReviewer, SpecReviewer | opus, fable | xhigh | 16:05 | 16:35 | 30 min | see table | done; RR-01 moved the top pair |
| A8 | Spec fixes; rulings v2; ranking v2; spec for QM | lead; ScoreApplierV2 | opus, sonnet | xhigh, high | 16:34 | 16:41 | 7 min | see table | done; session cut 16:43 |
| B0 | E.28b startup, start checks | lead | opus | high | 16:51 | 16:54 | 3 min | lead | done; key absent |
| B1 | S1 code fixes for QM | PilotFixer-OpusXHigh | opus | xhigh | 16:54 | 17:05 | 11 min | 23,722,826 (both rounds) | done; 168 pass |
| B2 | S2 delta review | DeltaReviewer-OpusXHigh | opus | xhigh | 17:06 | 17:14 | 8 min | 11,135,837 (both rounds) | NO GO (RD-01, RD-02) |
| B3 | RD-01..03 fixes | PilotFixer-OpusXHigh | opus | xhigh | 17:14 | 17:20 | 6 min | (in B1) | done; 204 pass |
| B4 | Re-check | DeltaReviewer-OpusXHigh | opus | xhigh | 17:20 | 17:22 | 2 min | (in B2) | GO |
| B5 | Ranking file; return drafts; session-1 cost | lead | opus | high | 17:15 | 17:25 | 10 min | lead | done |
| P4 | **wait for the key (name-only poll)** | | | | 17:25 | 20:30 | 3 h 05 min | | excluded; key never appeared |
| P5 | **idle, then reboot outage** | | | | 20:30 | 21:54 | 1 h 24 min | | excluded; reboot 20:42 |
| B6 | S3: not run | | | | 20:30 | 20:30 | 0 | | key absent at the deadline |
| B7 | S5: V47 read; return; progress; STAGES; end checks; cost | lead | opus | high | 21:54 | 22:02 | see below | lead | done |
| | **Cumulative** | | | | 02:06 | 22:02 | work: session 1 about 4 h 46 min, session 2 34 min + 21:54-22:02 | **822,280,679** (lead 99,313,743; workers 722,966,936) | no initial estimate on disk |
