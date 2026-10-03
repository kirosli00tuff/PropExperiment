# Stage E.12 return: ML route v2 frozen, phase 1 bought, Gate 0 run once: FAIL

Lead Opus 5.5 xhigh, 2026-10-03 07:51 to {{END_TIME}} PDT. Prompt docs/prompts/STAGE_E.12.md. Times
are America/Vancouver. One mid-stage question to the user (the held stores, section 3, Task 6); the
user chose harness v9.

## 1. Verdict summary

**Gate 0: FAIL.** No product-horizon pair passes; v2 stops (V2.2b): no phase-2 purchase, no model.
- Best pair NG h60: mean gross 5.57 ticks against c 1.71 (3.25c, bar 1 met), t_B 2.51 (bar 2,
  t >= 3, fails), p 0.0062 against the Holm threshold 0.000183 (rank 1 of 273, not rejected),
  518 trades. NG hF: 7.9c, t 2.33. No pair reaches t >= 3.
- Pooled family B: mean gross -0.72 ticks against 2.26 ticks of cost, t 0.28, 39,997 trades.
  Family A: the smallest p is 0.015 (g07_range hF).
- Fable recomputed all 273 tests independently: agreement to about 1e-13, the same Holm
  decisions, VERIFIED WITH NOTES (no blocking or should-fix finding).

**Phase 1.** The frozen subset rule selected all 28 exposures (the planning guess was 8): 1,543
training-window chunks (2019-05..2024-02) for **$133.723742** (acct-1 $26.797773, acct-2
$106.925969; NG already owned). Billed equalled quoted on every chunk. MBT has no Gate 0 row (D4
start 2024-01-02, all 41 dates lost to warm-up); MES was excluded by the pre-registered P-1a.

**Funds left:** acct-1 $1.61 of headroom, acct-2 $18.07.

**Hashes:** v2 freeze commit 9466f2e, manifest a647cd06...; harness v8 452c4a51... (deccd17); harness
v9 7fd757f6... (4b1e81e, the user's mid-stage decision on 24 held closure bars).

**New program N: 198 + 273 = 471.**

**Phase 2** is not bought (Gate 0 failed). Quotes for the record: holdout-2 for the 28 price paths
$31.98; the 2010 extension {{EXT_TOTAL}}. Top-up needed for both: {{TOPUP}}.

## 2. Guardrail evidence

### Start (07:52 PDT), quoted verbatim (reports/stage_e12_briefs/start_checks.txt)

```
{{START_CHECKS}}
```

Start pytest (07:52-08:13, run with PYTHONPYCACHEPREFIX): `3 failed, 6317 passed, 2 skipped, 2 xfailed`.
The 3 are test_harness_freeze bytecode tests that fail only under PYTHONPYCACHEPREFIX (E.11 saw the
same); rerun without it: `17 passed`. The start state is E.11's 6320 passing.

### After the purchase (11:58 PDT, harness v8), quoted verbatim (reports/stage_e12_briefs/postpurchase_checks.txt)

```
{{POST_CHECKS}}
```

Training-window chunks on disk for the 27 bought roots: 1,543 (26 x 58 + MBT 35); chunks starting
in 2024-03..2025-03 (embargo and holdout-2): **0**; every purchase manifest ends at
range=2024-02-01_2024-03-01.

### End ({{END_TIME}} PDT, harness v9), quoted verbatim (reports/stage_e12_briefs/end_checks.txt)

```
{{END_CHECKS}}
```

End pytest (without PYTHONPYCACHEPREFIX): `{{END_PYTEST}}`.

## 3. Results per task

### Task 0: startup
All start checks passed (above). HEAD 8b93e98 (the prompt commit), clean tree, v7 preflight OK.

### Task 1: V23 applied (design: lead; code: V23Coder, Phase1Coder)
- Design (docs/STAGE_E_ML_V2_DESIGN.md): every V2.12 item marked decided with V23 cited; only item
  18 open. Gross reading the built default (hurdles 1.5c/2c/3c), tau 0.167 with its derivation,
  Gate 0 at 1.5c with family A in the Holm family, the canary semantics rewritten for the gross
  reading; the release-window rule in V2.8 (lead rule P-5: counted with the entry, refused above
  half the tier); the 1.5 x slippage must-survive in the holdout-2 registration; deployment (a);
  the unused research-window Holm slot with V23 cited; the phase-1 test list (P-1 to P-3).
- Code (V23Coder): COST_GATE_READING "gross", C_SIGMA_TAU 0.167, N_PROGRAM_AT_FREEZE 198, the
  release-window rule in the portfolio, selection metric, engine portfolio and both payout
  re-sizing paths, the K9-anncday-01 flag k9_anncday, the Gate 0 canaries under the new defaults
  (noise fails, a planted gross edge passes, 1.0c-1.5c fails, [1.5c, 2.5c) passes; the literal
  reading's case kept with the reading pinned). ml_v2 suite 704 -> 791 passed.
- Real-data entry point (Phase1Coder; not named in the prompt, needed so Gate 0 code was frozen
  before any data): ml_route_v2/phase1 (build, register, run): the frozen store loaders, D4 S_X per
  price path, coverage rule P-1, MES contingency P-1a, the P-2 list, the run-once guard, the
  list-hash check, the v2 freeze check and the harness preflight before every step. 50 tests.
- Lead edits: ACCOUNT_150K's 150K scaling plan and MLL comment, PAYOUT_RESET_DELAY_DATES = 2.
- Final ml_v2 suite before the freeze: `803 passed, 2 xfailed`.

### Task 2: freeze inputs
- 2a CME margins (MarginFetch): live CME refused automated access (HTTP 403 citing its terms); only
  stale Wayback figures for 25 of 34 symbols; 5 vehicles (MNQ, M2K, MYM, MCL, NG) had none. More
  than a few, so the whole ranking used the frozen E|m_1| (V23 item 3's fallback; design V2.1
  step 6). reports/stage_e12_cme_margins.json kept as the record; its figures are unused.
- 2b Topstep 150K (TopstepFacts): MLL $4,500 confirmed; scaling plan from the page image: 3 lots
  below $1,500, 4 from $1,500, 5 above $2,000, 10 above $3,000, 15 above $4,500 (a balance exactly
  on a boundary takes the lower tier); Combine $199/month (Standard) or $229 (No Activation Fee),
  reset the same, activation $149 (Standard); Back2Funded $829; "as few as two days" to pass.
  reports/stage_e12_topstep_150k.md.
- 2c EC-K9 2019-2024 (CalendarBuilder): 240 dates (FOMC 38, NFP 58, GDP 38, ISM 58, inflation
  58), 884 CAL-E12 source rows from the Fed, BLS, BEA and ISM pages, no uncovered span; FOMC, NFP,
  CPI and PPI match the frozen release calendar exactly; the method reproduces the frozen
  research-window rows exactly. Unscheduled FOMC actions and the cancelled 2020-03-18 statement day
  excluded (not known at the entry intent). reports/stage_e12_ec_k9_2019_2024.json/.md.

### Task 3: the v2 freeze
- Fable reviewed the uncommitted freeze (0 blocking, 4 should-fix, 9 notes); all accepted fixes
  were applied before the commit and the manifest rebuilt once (the first was never committed).
- Commit **9466f2e "ML route v2 freeze"** (09:25:53): the design marked FROZEN, the manifest
  reports/stage_e12_ml_v2_freeze.json (91 files: the design, every ml_route_v2 file, the ml_v2 tests
  and fixtures, the cost wall, the margin attempt, the Topstep file, the EC-K9 files and the other
  frozen inputs; sha256 **a647cd06c8f71f9549c0afa1c740bc32bad05e8f83ed57c87642a1586a0cad5b**), the
  Task 1 code and tests, the Task 2 files, the ranking script and the manifest builder.
- Universe table regenerated from cost_wall.json: all 28 rows match (clusters, paths, tick values
  and ticks exactly; the RT_X $ display to the cent).
- Program N read at the freeze: 198 (E.9; E.10 and E.11 added nothing); no machine-readable N
  ledger exists, so it was read from the stage records, cited in the manifest.

### Task 4: harness v8 (KeyCapFix prepared it in a worktree; lead committed)
- ACCOUNT_2_CAP_USD 125.00 -> **249.67** (acct-2 ledger spend 124.673761 + the $125.00 top-up,
  rounded down to the cent); C-10: the key is returned stripped, docs/ACCESS.md names
  DATABENTO_API_KEY1 and DATABENTO_API_KEY2; the E.12 spend block (session cap $137.73 = the fresh
  quote of the subset $133.723742 x 1.03, under the combined headroom $153.403992; request cap
  $3.00); pull_step2 --account, --roots, --training-window (ends at range=2024-02-01_2024-03-01,
  refuses later chunks, required for --buy), quote-only --holdout2-only and --extension-2010.
- v8 sha256 **452c4a51ebfae33f6f18822c9b754634f1ce3ab879b88abe416633c75965a426**; diff against v7:
  data/config.py, data/pull_step2.py, tests/test_e2b_pull_step2.py changed, two test files added.
  No data/config.py name the phase-1 path imports changed (review F-4). Harness tests 241 passed.
  Commit **deccd17** (10:02:53).

### Task 5: quote, rank and buy
- Fresh quote (09:27-09:58, ledgered at $0.00 under stage-E.12-2026-10-03): 1,601 chunks, 0 failed,
  $139.340240 for the 28 price paths' training windows (reports/stage_e12_quotes_phase1.json).
- Ranking (reports/stage_e12_ranking.json, sha256 43f80e90...; lead rule P-4, E|m_1| proxy):

{{RANKING_TABLE}}

- Every pick fitted (3% reserved per pick): the subset is all 28.
- Buy (10:03-11:57): four processes over disjoint roots (acct-1: NQ GC 6E ZL MBT LE HE; acct-2 in
  three groups), each through data.pull_step2 --buy --training-window with the v8 sha256. 1,543
  commits, 1,543 settles, **every settle delta $0.00** (billed = quoted), 0 refusals. Spend:
  acct-1 $26.797773 (now 118.390020 of 120.00), acct-2 $106.925969 (now 231.599730 of 249.67);
  session $133.723742 under its $137.73 cap.

### Task 6: bars, filter and Gate 0
- Stores: 15 built under v8. The v8 builder held 12 roots "for the lead (ruling L-3)": 24 bars
  inside a scheduled closure beyond the close minute, each the last minute before a 15:30, 17:00 or
  08:30 CT reopen on a 2020 quarter- or month-end date (NQ 6, RTY 5, YM 4; 6E 6S 6J 6A 6B 6N 6C 1
  each; LE, HE 1 each). The builder has no path to apply a ruling, so the choice (harness v9, or
  drop the roots under F-3, or wait) was a guardrail conflict and an irreversible either-way
  decision: the lead asked the user, who chose **harness v9: keep and flag**. V9Coder built the
  enumerated ruling path (reports/stage_e12_closure_rulings.json, 24 entries) and proved the frozen
  loader reads such stores; v9 sha256 **7fd757f6d7c3990c2d20756c501f68b0541aa89851dcca9236badabd4f4a9bd9**,
  commit **4b1e81e** (12:05:01); the 12 stores built under v9. All 28 stores exist.
- Build (12:09-12:14, v9 + the freeze manifest): 28 vehicles; MES store refused by the frozen loader
  (TradeDateMismatch, 3 rows labelled 2020-03-30, booked 2020-03-31), so P-1a excluded g17_mes,
  k8_flight_ret and k8_flight_tail: 64 signals; calendar 1,248 trade dates; 68,138 panel rows; D4
  S_X: 2019-05-06 for 25 paths, ZF 2020-10-01, ZT 2021-10-01, MBT 2024-01-02 (41 dates, no row after
  warm-up). Vendor-degraded dates flagged and kept (5 per path).
- c/sigma filter (tau 0.167, volatility only): 81 pairs, **81 admissible, 0 dropped**; ratios
  0.009 to 0.140 (largest ZN h60). reports/stage_e12_c_sigma.json.
- List registered **12:15:25** before any statistic: reports/stage_e12_gate0_list.json sha256
  **53e7ef576feba9959360b52a633b793175bce98d62a839fefa0f41baf19fa8ea**, |A| 192, |B| 81, 273
  entries in ledger/ml_v2_config_ledger.jsonl; the hash written to the STATE file first.
- Gate 0 ran **once**, 12:15:41-12:15:54. Verdict **FAIL**. reports/stage_e12_gate0.json (sha256
  c0af61c2...) and .md (363c5676...). Family B, the eight pairs with the largest t_B:

{{B_TABLE}}

  Eight pairs clear 1.5c (6J hF, HE hF, NG h60/h120/hF, UB h60, ZS hF, ZT hF), all with t_B <= 2.51.
  Pooled B: mean gross -0.717 ticks, cost 2.260, t 0.28, 39,997 trades on 1,067 dates. Family A:
  no test near Holm (smallest p 0.015, g07_range hF, t -2.43); the descriptive rank ICs are in the
  JSON beside each test.
- **New program N = 198 + 273 = 471.**

### Task 7: free quotes for later phases (ledgered at $0.00, nothing bought)

{{LATER_TABLE}}

## 4. Delegation record

{{DELEGATION}}

## 5. Verification

Freeze review (FreezeReviewer-FableXHigh, before the commit; reports/stage_e12_review.md Part 1): 0
BLOCKING, 4 SHOULD FIX, 9 NOTE. Gate 0 verification (Gate0Verifier-FableXHigh; Part 2): VERIFIED
WITH NOTES, 0 BLOCKING, 0 SHOULD FIX, 5 NOTE. Rulings in reports/stage_e12_rulings.md.

| Id | Grade | Finding (short) | Ruling and fix |
|---|---|---|---|
| F-1 | SHOULD FIX | ranking reserved the quote, not quote x 1.03 | fixed before the commit |
| F-2 | SHOULD FIX | phase-1 CLI took operator paths for its checks | canonical paths only (Phase1Coder) |
| F-3 | SHOULD FIX | build --vehicles a free input | vehicles derived from the ranking and the stores |
| F-4 | SHOULD FIX | v8 must not change config names on the phase-1 path | verified from the v8 diff |
| F-5..F-13 | NOTE | counts, fixtures hash, phase-2 code items, freeze.py check, manifest wording, inputs not yet existing, proxy record, reset lower bound, K9 R-12 | applied or noted before the commit |
| N-1 | NOTE | c(p,h) built as the mean of max(long, short), design says "the mean round trip" | documentation; no admissibility change either way; next design edit |
| N-2 | NOTE | CPCV blocks cut on the calendar from 2019-05-06 | V2.9 as written |
| N-3 | NOTE | the verifier saw the lead's headline numbers (STATE grep) before finishing | disclosed; all 273 tests recomputed by its own code, agreement 1e-13 |
| N-4 | NOTE | v9 did change data/step2_store.py, imported on the read path (build side only) | wording corrected in the rulings |
| N-5 | NOTE | MBT's V_ref comes from research-window medians the verifier may not read | noted |

Key numbers, Fable vs lead: admissible 81 | 81; NG h60 mean g 5.56950 | 5.56950, c 1.71288 |
1.71288, t_B 2.51434 | 2.51434, p 0.006201 | 0.006201, 518 | 518 trades, Holm rank 1/273 not
rejected | same; pooled t 0.2807 | 0.2807; three seeded family A tests to 3e-13; 20/20 targets from
the bars exact. Order of events confirmed strictly increasing: freeze 09:25:53 < v8 10:02:53 < first
purchase commit 10:03:54 < v9 12:05:01 < last list registration 12:15:25 < Gate 0 result 12:15:54.

## 6. Open choices (decisions the lead made on its own, with the reason)

{{OPEN_CHOICES}}

## 7. Decisions for the user (Gate 0 FAILED)

**What v2's stop means.** Under the frozen V2.2b, a Gate 0 fail ends ML route v2: no phase-2
purchase (holdout-2, 2010 extension), no V2.6 selection, no model, no holdout-2 registration, no
paper trading. The 273 tests stay in N (471). The bought training stores remain on disk; reusing them
for a new hypothesis would need a new pre-registration that counts N = 471. V2.12 item 18 becomes
moot until there is a model.

1. **Accept the stop (recommended).** Gate 0 asked the cheapest question (is there any gross edge
   at 1.5x cost, t >= 3, after Holm, on 27 products and 64 signals over 4.8 years), and the answer
   is no. The best pair (NG h60, t 2.51) is not evidence after Holm, and choosing NG now would be
   selection on the same data. Do not re-run Gate 0, relax its bar, or buy phase 2.
2. **V22's personal-account path.** It moves a working model from XFAs to a personal account. With
   no model there is nothing to move, and funding a personal micro account now would trade without
   an edge. Recommendation: do not fund it on v2; revisit only if another route produces an edge
   that clears a pre-registered bar.
3. **The AiTrader readout** (the sibling project's Stage C: a one-shot, pre-registered evaluation of
   its news-judgment signal, not started, gated on its collection's Stage B exit). It is a different
   information source from price-based signals, so v2's null does not predict it. Recommendation:
   make it the program's next live question, run when its exit gate is met; keep PropExperiment
   paused rather than open a new price-based search, since 471 trials and 9 screened clusters plus
   v2 have found nothing that survives.
4. **The unspent funds** (acct-1 $1.61, acct-2 $18.07): no use under v2; leave them.
5. **Harness v9** (the user's decision): stays in force; the ruling file is a frozen input. No
   action, recorded for completeness.

## 8. Session cost

{{COST}}
