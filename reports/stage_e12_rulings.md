# Stage E.12 rulings: the lead on every review finding and worker question

Lead: Opus 5.5, xhigh. Times America/Vancouver, 2026-10-03.

## Part 1: freeze review (FreezeReviewer-FableXHigh, pre-commit; ruled about 09:20)

The review ran on the uncommitted freeze (manifest sha256 45e0faf2...), so every accepted fix was
applied before the freeze commit and the manifest was rebuilt once (the first, uncommitted manifest
was deleted; it was never committed or used).

| Id | Grade | Ruling | Action |
|---|---|---|---|
| F-1 | SHOULD FIX | Accept | rank_phase1.py reserves quote x 1.03 after each pick, so every account's picks with the margin fit its headroom and the session cap (subset total x 1.03) never exceeds the combined headroom. |
| F-2 | SHOULD FIX | Accept | Phase1Coder follow-up 2: the CLI verifies only the canonical manifest, writes only the canonical reports and ledger, and uses the canonical state dir ~/.cache/propexp_e12_phase1; no operator path reaches a check. |
| F-3 | SHOULD FIX | Accept | Phase1Coder follow-up 2: the build derives the vehicles from reports/stage_e12_ranking.json's subset and the step 2 stores that exist; a selected vehicle without a store is dropped by name; no free --vehicles. Design V2.2b "Products" bullet updated. |
| F-4 | SHOULD FIX | Accept | The Task 4 v8 review states, from the diff, that no data/config.py name imported on the phase-1 path changes (REPO_ROOT, DATA_ROOT, PROCESSED_ROOT, STEP2_ROOT, DATASET, VENDOR_ROOT and the rest), and the manifest records it as a constraint. |
| F-5 | NOTE | Accept | Design counts 222/282 -> 225/285 (67 signals). |
| F-6 | NOTE | Accept | tests/ml_v2_fixtures.py added to the manifest. |
| F-7 | NOTE | Accept | Design states that the reset-cost figures and the research-window warm-up are coded at phase 2 under the frozen text; neither touches Gate 0. |
| F-8 | NOTE | Accept | freeze.py entry check uses a subset test (Phase1Coder follow-up 2). |
| F-9 | NOTE | Accept | The manifest's harness entry is a constraint the v8 review verifies; context hashes labelled informational. |
| F-10 | NOTE | Accept | Gate0Verifier reconciles the build fingerprint's store sha256s with the purchase records and the ranking output. |
| F-11 | NOTE | Noted | No action. |
| F-12 | NOTE | Noted | Reset delay 2 is a lower bound; reported beside the payout figures at phase 2. |
| F-13 | NOTE | Accept | Design V2.3 K9 text: R-12 is carried by V2.2's decision-row exclusions. |

## Part 0: worker questions ruled before the review

| Source | Question | Ruling |
|---|---|---|
| MarginFetch | Live CME blocked (HTTP 403 citing its terms); 25/34 stale Wayback figures; 5 vehicles none; CME ToS 8(vi) | The prompt's failure path applies: the WHOLE ranking uses the frozen E|m_1| (V23 item 3), never mixed. The margin file is kept as the record; its figures are unused. Scrapling and Firecrawl were rightly not used against an explicit block. |
| TopstepFacts | 150K tier boundaries unstated | $1,500 opens the 4-lot tier (as XFA_50K encodes the same label); a balance exactly on $2,000, $3,000 or $4,500 takes the lower tier (conservative). |
| TopstepFacts | Reset cost and delay | Delay 2 trade dates (Topstep's stated minimum, a lower bound); cost per new XFA reported at both paths ($348 / $229 at 150K; $198 / $95 at 50K); Back2Funded listed, not modelled. |
| CalendarBuilder Q1 | Unscheduled FOMC actions (2019-10-11, 2020-03-03, 2020-03-15, notation votes) | Excluded: not known at the 17:59 CT entry intent the evening before (member decision_time; catalog R-07). |
| CalendarBuilder Q2 | The cancelled 2020-03-18 statement day | Excluded: cancelled on 2020-03-15, before the entry intent. |
| Phase1Coder | MES never loaded by a Stage E loader | Lead rule P-1a: a refused MES store makes MES unavailable (its signals are coverage exclusions); a refused price-path store stops the run. |
| Phase1Coder | check_grid off on real bars | Accepted: the frozen loader's L-3 booking check replaces the synthetic session-grid check. |
| Phase1Coder | P-2 counts never-applicable covered signals (p = 1 tests) | Kept as frozen: conservative for Holm and N, and the list stays a function of coverage only. |
| V23Coder | P-5 refuses rather than re-sizes | Accepted (the rule says "refused"). |
| V23Coder | Edits outside its file list (targets.py, simulate.py, test_ml_v2_cpcv.py) | Accepted: no other coder owned them; covered by the ml_v2 suite and the freeze review. |
| V23Coder | New strict xfail: ridge extrapolation of a 0.5c edge passes the 1.5c gate on 4 of 2,538 rows | Accepted as a documented expected failure (C-1 again under the gross reading); design V2.7 records it; no rule change. |
| KeyCapFix | credit_left = cap headroom for both accounts | Accepted (V19: the cap was raised to match the funds; V23: acct-1's headroom is its funds). |

## Part 2: mid-stage events and the Gate 0 verification (ruled 2026-10-03, 12:00-12:40)

| Item | Ruling |
|---|---|
| v8 store builder held 12 roots (24 deep closure bars, each the minute before a 15:30, 17:00 or 08:30 CT reopen on a 2020 quarter- or month-end date) | A guardrail conflict (harness beyond v8) plus an irreversible either-way choice (Gate 0 runs once): put to the user (AskUserQuestion, about 10:41). The user chose "Harness v9: keep and flag". Implemented as an enumerated ruling file (24 entries) read by data/step2_store.py; harness v9 7fd757f6... (commit 4b1e81e); the 12 stores built under v9; 15 under v8; NG owned. |
| MES store refused by the frozen loader at the build (TradeDateMismatch, 3 rows) | Pre-registered lead rule P-1a applied as frozen: g17_mes, k8_flight_ret, k8_flight_tail excluded; 64 signals covered. No ruling needed; verified by Gate0Verifier (exactly 3 rows). |
| MBT has no panel row (D4 S_X 2024-01-02, 41 dates, all lost to the 60-date warm-up) | The frozen rules working as written (P-3, V2.4). K7 has no Gate 0 row; MBT's 3 B pairs are absent, not dropped by the filter. Verified. |
| Gate0Verifier N-1: c(p,h) as built is the mean of max(long, short) round trips; V2.2 says "the mean D8 round trip" | Accept as documentation (conservative reading; 0 of 81 admissibility changes either way). The frozen design is not edited in this stage (its hash is in the freeze manifest); the next design edit records the max reading. No rerun. |
| N-2: CPCV blocks cut on the 1,248-date calendar while the first panel row is 2019-11-19 | Noted: V2.9 as written ("from calendars alone"). |
| N-3: the verifier's STATE grep showed the lead's headline numbers before its run finished | Disclosed in the return. All 273 tests were recomputed by its own code and agree to 1e-13. |
| N-4: "no module on the Gate 0 read path changed between v8 and v9" | Corrected wording: data/step2_store.py (imported on the read path) changed on its build side only; the names the phase-1 path imports from it (step2_parquet_path and the summary path) are unchanged. The v9 commit message's sentence is superseded by this ruling. |
| N-5: MBT's V_ref (48.0) comes from research-window medians the verifier may not read | Noted; recorded with the research store's sha256 (E.2a's pinned value). |
| Freeze review's commit-order check | Moved to Gate0Verifier (prompt Task 8 item); confirmed (review Part 2): freeze 09:25:53 < v8 10:02:53 < first purchase commit 10:03:54 < v9 12:05:01 < last list registration 12:15:25 < Gate 0 result 12:15:54 (PDT). |
