# Stage E.34 return: ZL program design and frozen protocol (no purchase, no registration)

Prompt docs/prompts/STAGE_E.34.md. Lead Opus 5.5 (claude-opus-5-5), effort max, in three sessions with planned
context wipes: 61379f35-7e9c-4e83-8aba-8176e52367c9 (11:53-12:30 PDT), 92545abe-53bf-484b-bbfb-6c6b8a67b381
(13:51-14:30), 4b0394a9-db7b-4958-80d5-d40327048001 (15:10-end), 2026-10-29. Times are America/Vancouver, from `date`,
file mtimes and transcripts. Checkpoints: reports/stage_e34_STATE.md. N stays 838; nothing was bought, quoted,
registered or trained, and no feature value, label, return or outcome was computed.

## 1. Summary

Exposure. ZL's discovery dates (2020-12..2024-02) are not virgin, but no F10 or F09 feature of this program was ever
tested against a ZL outcome. Earlier ZL-labelled outcomes on these dates came from unrelated one-minute-bar
mechanisms, all null or FAIL. The strongest exposure is indirect (E.33's crush z-scores against ZM labels, a clean
negative). Direct exposure (ZL's own returns, 60-minute cross-market leads) is excluded (E1-E6) behind a 10-rule
firewall.

Data. MBP-1 in both windows, no MBO: the owned ZL MBP-1 serves discovery; the test needs ZL MBP-1 (USD 23.36 against
USD 40.96 for MBO in both windows). Minimum aggregation horizon 5 minutes.

Families and budget. F10 (12 book features) and F09 (8 crush and 9 propagation features from one-minute bars), each
with 14 context features: 4 sets x 5 labels (FH15, FH30, FH60, TB15, TB30) x 10 model settings = 200 configurations,
all ML under V43 (user to confirm). N rises from 838 to 1038 at registration.

Power. At N 1038 and 870 test dates, 80% power needs a daily net Sharpe of 0.196: per trade 0.97 / 1.94 / 3.74 ZL
ticks net at the FH caps of 17 / 8 / 4 trades a date, and 3.89-5.50 ticks at one or two trades a date at h 30.
Discovery's binding threshold is a daily Sharpe of 0.203; Holm never binds. With E.32's DSR rule as coded, a lone
finalist beside null companions cannot pass (probability about 0); amended, 0.85 at a true 0.20.

Prior. About 3-4%: E.32b's 4%, essentially unchanged (no outcome was read), and only if E.32-D2 is amended; near 0
otherwise.

Purchase. Discovery buys nothing. The test buys ZL MBP-1, ZL definitions and the ZM bars of 2017-05..2019-04 (not
owned): about USD 26.5, after K1 and K2 pass and a quote on DATABENTO_API_KEY4 is approved.

## 2. Guardrail evidence

Start checks (reports/stage_e34_briefs/checks_start.txt, 11:54:58 PDT; the git status listing of 2,152 lines is in
the file), quoted verbatim:

    $ git status --short | wc -l
    2152
    $ git log --oneline -3
    93389da docs: V57 (stale Stage E sequence line superseded) and the Stage E.34 prompt (ZL program design)
    fe15e06 Stage E.32b directional rerank
    3a8edf0 docs: Stage E.32b adds build recommendations (step 3b) as its main output
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
    $ trial registry: current_n and last entry (N)
    current_n 838 | registrations 10 | last r009-E33 538 -> 838 2026-10-28T14:23:13-07:00

Holdout status at every session start and end (unlocks_logged 0 and all_ok true on all six stores each time):
reports/stage_e34_briefs/holdout_session{2_start,2_end,3_start}.txt and holdout_session1_end.txt.

End checks (reports/stage_e34_briefs/checks_end.txt), quoted verbatim:

    # E.34 checks: end
    $ date
    Thu Oct 29 15:49:04 PDT 2026
    $ git status --short | wc -l
    2161
    $ git log --oneline -3
    93389da docs: V57 (stale Stage E sequence line superseded) and the Stage E.34 prompt (ZL program design)
    fe15e06 Stage E.32b directional rerank
    3a8edf0 docs: Stage E.32b adds build recommendations (step 3b) as its main output
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
    $ trial registry: current_n and last entry (N)
    current_n 838 | registrations 10 | last r009-E33 538 -> 838 2026-10-28T14:23:13-07:00
    $ sha256sum ledger/trial_registrations.jsonl
    11777e468fa6f2db9e7d7da16bd57681a985b9370c8e6058f8dd6ae8bd75f24c
    $ ledger/trial_amendments.jsonl
    1
    511ae4c377c45969259b8a8e02c6114990eb7eb47b407ac0893cc063832c7b40
    7

pytest: not run. The prompt asks for it only if Part 0 changed a guard, and Part 0 changed none (3.1).

## 3. Results

### 3.1 Part 0: seal and exposure
- 0.1 (lead; reports/stage_e34_briefs/seal/part01_seal_check.md, census34.tsv): a names-and-stat census of 143,390 rows
  (0 PROBLEM rows) shows the E.32 test seal covers every ZL, ZS and ZM file touching 2017-05-01..2020-11-30 in every
  schema; nothing new was sealed and no guard changed. The FRED soybean-oil csv and the 16 roll symbology files stay as
  E.32 classified them; the protocol refuses them by path (OC-1).
- 0.2 (reports/stage_e34_exposure.md; ExposureAuditor-OpusHigh over two Haiku extractions: 21 ledger and record rows,
  64 code rows): no proposed F10 or F09 feature was tested against a ZL outcome; every earlier ZL-labelled outcome was
  bar work, null or FAIL; E.33's S1 and S3/S4 validity flags read ZL; build_features33.py:156 cannot load 2020-11-30 or
  earlier. The protocol adopts the auditor's 10 firewall rules and 6 exclusions (P1.5; OC-6).

### 3.2 Part M: ZL methods addendum (reports/stage_e34_zl_methods.md)
A lead front (verdict table, what Part P takes, 21 errata) and the five files M1-M4 and L unchanged. M1: MBP-1 in
both windows; 8 of E.32's 12 F3 features carry over, 2 adapted, 2 dropped; 5-minute floor (L.a). M2: the crush
residual with ZL as the adjusting leg and ZS/ZM leading ZL on bars are USE; CL excluded (E.12/E.20 60-minute leads on
ZL; no intraday evidence); HO, RB and RINs not owned for either window; VECM report-only; ZL must close 52% of a
dislocation within one half-life (ZM 0.70). M3: labels FH15, FH30, FH60, TB15, TB30 with cost-aware executable
targets; market execution selects; trade-through limits reported. M4: the thresholds at N 838..1138 for both test
spans; the D2 simulation. L.a-L.f: the lead's reconciliations and post-review rulings.

### 3.3 Part F: data facts (reports/stage_e34_data_facts.md; counts only)
ZL MBP-1: 158,046,466 records on the discovery files (158,044,028 on the 816 trade dates, equal to E.33's split);
median 188,782 records a date (5th-95th percentile 129,857-273,153); 76.2% of T records in the day session; 25 ZL
front changes (9 back-and-forth). Bars: 816 dates per root, median 906 (ZL), 981 (ZS), 842 (ZM) bars a date.
guard34's dry check refused 9 of 9 probes plus a positive control; 281 guarded opens logged. E.33's split store,
calendars and guard can be reused; labels need a new ZL MBP-1 book module.

### 3.4 Part P: the frozen protocol (reports/stage_e34_zl_protocol.md, FROZEN v1.0)
sha256 46556059b09b831794884514ef989a4b1b29909595157bf59daa04883ea0213b (frozen 15:47 PDT) (reports/stage_e34_zl_protocol.sha256 lists it with the P10.4 files). Sections 0 and P1-P11:
discovery on owned data of 2020-12-01..2024-02-29 (796 OOF dates after a 20-date burn-in); F09c, F09p and F10 with
exact formulas (43 features in the pooled set); 2 model families (6 LOGIT, 4 LGBM settings); E.32's 6 blocked folds
with a 21-date embargo; 200 configurations, N_reg 1038; G3 0.1746, G4 0.2028, b_test 0.166967 pinned; mechanical
selection (Tier A at most 3); the test sketch (one read of 2017-05-22..2020-11-30, Holm K 9, DSR at N, daily t > 3.0,
PBO < 0.5, and DSR with V = 1/(T_test - 1)); stop rules K0-K4 and E.32b section 6; the compute stop 3 x R_ZL = 23,895 s
(R_ZL 7,965 s central, guess range 3,022-22,651 s, from E.33's measured folds); the run-stage data plan (P11).

## 4. Delegation record

| Agent (description) | Agent file | Model (confirmed from transcript) | Effort | PDT | Status | Artifact |
|---|---|---|---|---|---|---|
| ExposureExtract-HaikuMed | worker-medium | claude-haiku-5-5 | medium | 12:10-12:15 | done | stage_e34_briefs/X_extract_records.md |
| CodeExtract-HaikuMed | worker-medium | claude-haiku-5-5 | medium | 12:15-12:21 | done | stage_e34_briefs/X_extract_code.md |
| ExposureAuditor-OpusHigh | worker-high | claude-opus-5-5 | high | 12:22-12:29 | done | stage_e34_exposure.md |
| MathReaderM1-OpusHigh | worker-high | claude-opus-5-5 | high | 12:10-12:21 | done | stage_e34_briefs/M1_F10_ZL.md |
| MathReaderM2-OpusHigh | worker-high | claude-opus-5-5 | high | 12:10-12:28 | done | stage_e34_briefs/M2_F09_ZL.md |
| MathReaderM3-OpusHigh | worker-high | claude-opus-5-5 | high | 12:10-12:23 | done | stage_e34_briefs/M3_labels_ZL.md |
| MathReaderM4-OpusHigh | worker-high | claude-opus-5-5 | high | 12:10-12:16 | done | stage_e34_briefs/M4_power_ZL.md |
| DataFacts-SonnetHigh | worker-high | claude-sonnet-5-5 | high | 12:10-12:23 | done | stage_e34_data_facts.md |
| MathReviewer-FableXHigh | worker-xhigh | claude-fable-5-1 | xhigh | 14:03-14:23 | done | review/MathReview.md |
| ComputeRef-OpusHigh | worker-high | claude-opus-5-5 | high | 14:03-14:09 | done | stage_e34_briefs/P10_compute_ref.md |
| ProtocolReviewer-FableXHigh | worker-xhigh | claude-fable-5-1 | xhigh | 14:14-14:30 | done | review/ProtocolReview.md |
| FixVerifier-FableXHigh | worker-xhigh | claude-fable-5-1 | xhigh | 15:28-15:45 | done | review/FixVerify.md |
| CostTally-SonnetMed | worker-medium | claude-sonnet-5-5 | medium | 15:49-15:50 | done | stage_e34_briefs/work/cost/ |

Lead-reserved work (not delegated): 0.1 seal check, the lead reconciliations L.a-L.f, every protocol declaration
(P0-P11), the fixes and the freeze, the methods front and errata, this return. Tokens per spawn: section 8.

## 5. Verification
- MathReviewer-FableXHigh (Part M): GO WITH FIXES, 2 BLOCKING, 4 SHOULD FIX, 14 NOTE; all four worker scripts reran byte
  for byte; an independent implementation reproduced every M4 and L number.
- ProtocolReviewer-FableXHigh (P0-P11 of v0.1): GO WITH FIXES, 2 BLOCKING, 12 SHOULD FIX, 14 NOTE; every threshold,
  cap, multiplier, count and R_ZL reproduced with the frozen functions (ref_zl.py rerun gave identical JSON); no leak
  found.
- The lead fixed all 4 BLOCKING (MathReview S2 equals ProtocolReview B2) and 16 SHOULD FIX items and 25 NOTEs in
  v0.2 (review/FixLog.md; diff review/protocol_v0.1_to_v0.2.diff).
- FixVerifier-FableXHigh (the v0.1 to v0.2 diff): PASS WITH FIXES (review/FixVerify.md). The stored diff
  reproduces byte for byte; all 4 BLOCKING items fixed; 15 of 16 SHOULD FIX fixed and 1 partly (PR-S4, closed by its
  F3); all 32 recomputations match (z 5.72; the K2 trigger 810, exact with the frozen functions; 2.254 ticks, 40.8%,
  18.7%; 43 / 258 / 180 / 120; 0.8978 / 0.9050 at N 1038; the ledger figures); the new F10.7 and F10.9 rules are point
  in time and correct on the MathReviewer's two counterexamples and nine more hand cases; no new leak. Its 4 new SHOULD
  FIX and 7 NOTE items were applied in its own wording in v1.0 (FixLog round 2; review/protocol_v0.2_to_v1.0.diff).
- Not independently verified: NOPA's 2017-2020 release time (the protocol makes the builder record it); MBP-1
  F-record semantics (the protocol follows E.33's frozen code); the ZS and ZM bars' instrument ids on roll dates (a
  declared G2 rule and a run-stage count).

## 6. Open choices
- OC-1 (0.1) FRED PSOILUSDM csv and the 16 roll symbology files not sealed (E.32 OC-0.4); refused by path in P1.2.
- OC-2 (routing) Haiku extraction split into two workers (records; code) before the Opus auditor.
- OC-3 (lead exposure) the lead read E.33c_RETURN.md sections 1-3.8 while orienting (the prompt's read-first list);
  disclosed in the exposure file; nothing in the protocol cites them.
- OC-4 (order) MathReviewer started on M1-M4 and L before the methods file existed; the methods file was assembled
  after the reviews.
- OC-5 (P2) option A, all 4 sets as ML under V43 (200 configurations, N 1038), not option B (62, N 900); a user
  decision before registration.
- OC-6 (P1.5) X rules 1-10 and exclusions E1-E6 adopted; CL excluded in every form; HO, RB, RINs excluded; VECM
  report-only.
- OC-7 (data) MBP-1 in both windows; test trade dates 2017-05-22..2020-11-30 (T_test 870); test definitions bought,
  else stop before the read.
- OC-8 (P3.6) no FOMC window; EIA WPSR Wednesdays 09:28-10:00 CT a report-only stratum; EPA RVO dates dropped.
- OC-9 (L.b) caps 17 / 8 / 4 replace 19 / 9 / 4; K2 in the per-configuration measured form.
- OC-10 (P8 G2) 0.50 ZL tick (USD 3.00), half a tick of the traded contract.
- OC-11 (P4) L1.7's volumes from bars for all three legs.
- OC-12 (P10.3) R_ZL 7,965 s central (3,022-22,651 s); stop 3 x R_ZL = 23,895 s, rescaled at the logged process counts.
- OC-13 (P9.4) E.32-D2: both forms stated; recommendation amend; the user decides.
- OC-14 (L.c) latest 30-minute entry 12:42 CT. OC-15 (L.d) ts_event drop-and-count rule. OC-16 (L.a) 5-minute floor.
- OC-17 (P6) FDR: BH q = 0.10, report only. OC-18 (P10.3) cut order S_pool, S_crush, S_book, S_prop, now also the run
  order (P7.1). OC-19 (P3.6, P9.2) test-window release calendar built before the read. OC-20 (P1.2) E.33's ZS split
  not used.
- OC-21 (P9.1, P9.2, P11; ProtocolReview B1) ZM.v.0 ohlcv-1m 2017-05-01..2019-04-30 added to the test purchase (not
  owned); if it cannot be bought, the run stage stops before the read rather than test the F09 sets on stale ZM.
- OC-22 (0.3; L.f.2) one bad-book reading, E.33's FA-4, for features, labels, exclusions and fills; M3's F_LAST-only
  form superseded; book updates are F_LAST records of any action.
- OC-23 (F10.7, F10.9) the MathReviewer's exact fixes adopted (most recent touch change; record-pair decreases minus
  the batch's T lots), with LT12 hand tests.
- OC-24 (NOTEs) 25 NOTEs acted on in the protocol, among them: two independent implementations required (G7), the
  Tier A prop simulator kept (P6.4), lam60 normalised by the absolute median. MathReview N3, N4, N6-N11, N14 go to the
  methods errata only; ProtocolReview N14 needs no change.
- OC-25 (P9.2) the ZM-bar and definition estimates come from medians of settled monthly buys in the spend ledger (USD
  0.0608 for ZM ohlcv-1m, 73 months; USD 0.0385 for the three-parent definitions, 39 months), not quotes.
- OC-26 (summary) the honest prior after design is put at about 3-4% (E.32b's 4%; no outcome read), conditional on
  amending E.32-D2.
- OC-27 (method) the v0.2 fixes were applied as 42 exact-once scripted replacements plus two edits; worker files M1-M4
  were not edited (errata govern); L received section L.f.
- OC-28 (freeze) FixVerify's F1-F11 applied verbatim in v1.0 without a third review round: every new sentence is the
  verifier's replacement text, applied by exact-once matching (review/protocol_v0.2_to_v1.0.diff, 96 lines).
- OC-29 (F8) T_b(p) is side-matched (A or N on the bid, B or N on the ask), restoring M1 2.3 c's aggressor rule that
  M1's section 7 table and v0.1 had dropped.
- OC-30 (commit) seal/census34.tsv (28 MB, names and stat only) and work/DataFacts-SonnetHigh/manifest_facts.json (5.6 MB,
  counts) stay untracked, as E.32's seal folder kept only small files; their sha256 are committed in
  reports/stage_e34_briefs/untracked_large_files.sha256. Raw pages under work/*/pages/ stay untracked (E.28, E.32,
  E.32b practice); their sha256 are in reports/stage_e34_briefs/untracked_pages.sha256.

## 7. Decisions for the user (each with a recommendation)
1. E.32b-D2, give ZL's single sealed read to this program. This stage's facts: the read can detect only a daily net
   Sharpe of about 0.20 (0.97-3.74 ticks a trade); the test needs about USD 26.5 of data; the F09 sets need ZM bars that
   are not owned. Recommendation: yes, together with item 3; without item 3 the read would be spent on a test that a
   lone finalist cannot pass.
2. E.32b-D3, admit a discovery search judged by the power rule instead of V31's cost gate. Discovery costs no data (all
   owned) and about 2.2 hours of compute centrally (stop at 6.6 hours); K1 and K2 stop before any purchase if nothing
   detectable survives. Recommendation: admit it for this program only.
3. E.32-D2, the test DSR variance rule. As coded, a lone Tier A finalist beside null Tier B companions passes with
   probability about 0; amended (V = 1/(T_test - 1)), 0.845 at a true daily Sharpe of 0.20, and the bar cannot fall
   below check (2). Recommendation: amend for this test.
4. OC-5, the V43 reading (model rule). Option A runs all 200 configurations as ML (N 1038); option B registers 12 F09
   rules beside 50 F10 ML configurations (N 900). Recommendation: option A (every configuration is labelled and traded
   on ZL's own book with the measured fill model).
5. The test purchase, only after K1 and K2 pass: create a funded slot DATABENTO_API_KEY4 (accounts 1-3 have under USD 3
   of headroom each) and approve a quote for ZL MBP-1 2017-05-21..2020-11-30, ZL definitions and ZM ohlcv-1m
   2017-05-01..2019-04-30 (estimates USD 23.36 + about 1.66 + about 1.46, about USD 26.5; 27.3 at the dearest months). Recommendation: approve
   the quote step when the run stage reaches it, not before.

## 8. Session cost (from the transcripts; never estimated)

Counted by reports/stage_e34_briefs/work/cost/make_cost.py (E.32b's script with the three E.34 sessions; summary line
`models=4 spawns=13 sessions=3 problems=0 grand_total=128,757,530`) from message.usage in the three lead transcripts and
the 13 subagent transcripts, 2026-10-29T18:50:00Z to 22:50:05Z (15:50:05 PDT). Lead messages after the cutoff (these
tables and the commit) are not counted; CostTally's own count stops at the cutoff.

| Model | Messages | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|---|
| claude-opus-5-5 | 523 | 1,080 | 778,566 | 94,012,384 | 2,177,830 | 96,969,860 |
| claude-fable-5-1 | 71 | 2,194 | 260,904 | 10,388,121 | 1,154,411 | 11,805,630 |
| claude-haiku-5-5 | 86 | 172 | 122,945 | 10,913,137 | 403,808 | 11,440,062 |
| claude-sonnet-5-5 | 58 | 118 | 78,022 | 8,166,627 | 297,211 | 8,541,978 |
| all | 738 | 3,564 | 1,240,437 | 123,480,269 | 4,033,260 | 128,757,530 |

Per spawn (agent file, model from the transcript, effort, tokens): ExposureExtract-HaikuMed worker-medium haiku medium
4,844,358; CodeExtract-HaikuMed worker-medium haiku medium 6,595,704; ExposureAuditor-OpusHigh worker-high opus high
4,256,519; MathReaderM1-OpusHigh worker-high opus high 9,494,922; MathReaderM2-OpusHigh 18,315,086; MathReaderM3-OpusHigh
12,312,165; MathReaderM4-OpusHigh 3,975,091 (all worker-high opus high); DataFacts-SonnetHigh worker-high sonnet high
8,327,840; MathReviewer-FableXHigh worker-xhigh fable xhigh 3,276,958; ComputeRef-OpusHigh worker-high opus high
2,488,911; ProtocolReviewer-FableXHigh worker-xhigh fable xhigh 4,734,364; FixVerifier-FableXHigh worker-xhigh fable
xhigh 3,794,308; CostTally-SonnetMed worker-medium sonnet medium 214,138 (to the cutoff).

Lead: session 1 18,845,495; session 2 14,448,452; session 3 12,833,219 (to the cutoff); 46,127,166 in all (35.8%).
Workers: 82,630,364 (64.2%). By model tier: Opus 75.3%, Fable 9.2%, Haiku 8.9%, Sonnet 6.6%. Wall-clock 11:53-15:55
PDT, 4 h 02 min; work 2 h 01 min (sessions of 37, 39 and 45 minutes); the planned wipes 12:30-13:51 (1 h 21 min) and
14:30-15:10 (40 min) are pauses, not work.

The final per-task table is in the progress.md entry's Session cost section.
