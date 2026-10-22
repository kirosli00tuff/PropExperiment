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

**Purchase (Part B).** @@PURCHASE_SUMMARY@@

**Pilot.** @@PILOT_SUMMARY@@

**The user decides:** @@DECIDE_SUMMARY@@

## 2. Guardrail evidence

Start checks, session 1 (02:07-02:13, verbatim file reports/stage_e28_briefs/start_checks.txt): holdout all_ok True,
unlocks_logged 0 (top, holdout_2, MCL, MGC, MHG, NG); `wc -c REGISTRATION.md` = 0; ledger 36402 lines, sha256
034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700; git 0 tracked changes, HEAD 71d667f; N 538.

Start checks, session 2 (verbatim, reports/stage_e28_briefs/start_checks_b.txt, script checks_b.sh):

```
@@INCLUDE reports/stage_e28_briefs/start_checks_b.txt@@
```

End checks (verbatim, reports/stage_e28_briefs/end_checks_b.txt):

```
@@INCLUDE reports/stage_e28_briefs/end_checks_b.txt@@
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
@@EVENTS_TAIL@@

## 3. Results

### Part C: the methods brief

reports/stage_e28_methods_brief.md (1.1 MB, sha256 e8c3fd71a648fcb7...; final at 15:16; not re-read in E.28b).
Contents:

@@INCLUDE_LINES reports/stage_e28_methods_brief.md 10 26@@

C3's answer: costs and data granularity were binding, not missing mathematics (Part 3). C4: Part 4 (phases, trial
counting into N, purged and embargoed CV by trade date, one test on data that never selected it, hardware).

### Part A: the ranking

reports/stage_e28_ranking.md (v2, final; spec sha256 89347e97...). Top 12 of the primary table:

@@INCLUDE_LINES reports/stage_e28_briefs/A3_ranking_table.md 59 72@@

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
- Quote, purchase, manifest: @@PURCHASE_DETAIL@@
- Pilot results: @@PILOT_DETAIL@@

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

@@OPEN_CHOICES@@

## 7. Decisions for the user

@@DECISIONS@@

## 8. Session cost

@@COST@@
