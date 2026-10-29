# Stage E.34 STATE (ZL program: design and frozen protocol; no purchase, no registration)

Prompt docs/prompts/STAGE_E.34.md. Lead: Opus 5.5 (claude-opus-5-5), effort max, session 1 =
61379f35-7e9c-4e83-8aba-8176e52367c9 (started 11:53 PDT 2026-10-29). Times America/Vancouver, from `date`, mtimes
and transcripts. N 838 (r009-E33). Binding: the prompt; E.32b recommendations 4.5 and 6; V43, V50, V51, V55, V56
(and V57 for the stage itself).

## Invariants (every session)
- No Databento call, no quote, no key read; REGISTRATION.md 0 bytes; nothing appended to ledger/trial_registrations.jsonl.
- No feature value, label, return or outcome computed; no training.
- Never open the sealed window 2017-05-01..2020-11-30 (ZM, ZS, ZL, any schema) or anything dated 2024-03-01 on.
- No edits under live/ or ops/; no push; one commit at the end ("Stage E.34 ZL program design and protocol").
- At most 6 workers at once. Reviewers Fable xhigh, model confirmed from transcript message.model.

## Task status

| # | Task | Owner | Model / effort | Status | Start-end (PDT) | Artifact |
|---|---|---|---|---|---|---|
| T0 | Start checks | lead | opus / max | done | 11:54:58-11:55:02 | reports/stage_e34_briefs/checks_start.txt |
| T1 | 0.1 seal check + names-only census | lead | opus / max | done | 11:56-12:03 | reports/stage_e34_briefs/seal/part01_seal_check.md, census34.tsv |
| T2a | 0.2 ledger and record extraction | ExposureExtract-HaikuMed | haiku / medium | done | 12:10-12:15 | reports/stage_e34_briefs/X_extract_records.md |
| T2b | 0.2 code extraction | CodeExtract-HaikuMed | haiku / medium | done | 12:15-12:21 | reports/stage_e34_briefs/X_extract_code.md |
| T2c | 0.2 exposure audit (judgment) | ExposureAuditor-OpusHigh | opus / high | done | 12:22-12:29 | reports/stage_e34_exposure.md |
| T3.1 | M1 F10 on ZL (MBO or MBP-1) | MathReaderM1-OpusHigh | opus / high | done | 12:10-12:21 | reports/stage_e34_briefs/M1_F10_ZL.md |
| T3.2 | M2 F09 into ZL | MathReaderM2-OpusHigh | opus / high | done | 12:10-12:28 | reports/stage_e34_briefs/M2_F09_ZL.md |
| T3.3 | M3 labels and holding band | MathReaderM3-OpusHigh | opus / high | done | 12:10-12:23 | reports/stage_e34_briefs/M3_labels_ZL.md |
| T3.4 | M4 power and N | MathReaderM4-OpusHigh | opus / high | done | 12:10-12:16 | reports/stage_e34_briefs/M4_power_ZL.md |
| T4 | Part F data facts | DataFacts-SonnetHigh | sonnet / high | done | 12:10-12:23 | reports/stage_e34_data_facts.md |
| T5 | Assemble Part M | lead | opus / max | after T3 | | reports/stage_e34_zl_methods.md |
| T6 | MathReviewer (Part M) | MathReviewer-FableXHigh | fable / xhigh | after T5 | | reports/stage_e34_briefs/review/MathReview.md |
| T7 | Part P protocol draft | lead | opus / max | after T2c, T3, T4 | | reports/stage_e34_zl_protocol.md |
| T8 | ProtocolReviewer | ProtocolReviewer-FableXHigh | fable / xhigh | after T7 | | reports/stage_e34_briefs/review/ProtocolReview.md |
| T9 | Fix BLOCKING + SHOULD FIX, freeze (sha256) | lead | opus / max | after T6, T8 | | reports/stage_e34_zl_protocol.sha256 |
| T10 | Return, progress, STAGES, end checks, cost, commit | lead | opus / max | last | | reports/E.34_RETURN.md |

## Log
- 11:53 session start; prompt read in full (249 lines).
- 11:54:58 start checks (checks.sh start): git status 2,152 lines (incl. the new reports/stage_e34_briefs/), head
  93389da; holdout all_ok, unlocks_logged 0 on 6 stores; soy test seal sealed 114/114, unlocks 0, all_ok; guard33
  dry-check 4 of 4 refused (rc 0); REGISTRATION.md 0 bytes; harness 2e908c81 preflight OK; spend ledger 37,290 lines
  sha256 42589d7b; N 838 (r009-E33, 10 registrations; registry sha256 11777e46); amendments 1 line 511ae4c3; .env
  KEY/KEY2 absent, KEY3 non-empty, KEY4 absent (names only).
- 12:00:10-12:00:33 census34.py (names and stat only): 143,390 rows, 0 PROBLEM; 0.1 verdict: the seal covers every ZL,
  ZS, ZM file touching the window; nothing sealed; no guard changed (OC-1: FRED monthly soybean-oil csv and the 16
  roll files stay as E.32 classified them; the protocol refuses them by path).
- about 12:03 (hook estimate at the STATE file's first write) context about 267k tokens: plan a wipe after wave 1
  returns, before Part P.
- 12:10 wave 1 spawned (6 at once): MathReaderM1/M2/M3/M4-OpusHigh (worker-high, opus), DataFacts-SonnetHigh
  (worker-high, sonnet), ExposureExtract-HaikuMed (worker-medium, haiku); briefs reports/stage_e34_briefs/BRIEFS.md.
  Next: CodeExtract-HaikuMed when a slot frees; ExposureAuditor-OpusHigh after both extractions.

- 12:15 ExposureExtract-HaikuMed done (21 rows; X_extract_records.md; 215,067 tokens, 36 tool uses, 303.5 s).
- 12:15 CodeExtract-HaikuMed spawned (worker-medium, haiku).
- 12:16 MathReaderM4-OpusHigh done (M4_power_ZL.md; work/MathReaderM4-OpusHigh/m4_power.py, m4_out.md; 172,680
  tokens, 34 tool uses, 371.8 s). Key: binding 0.2007 -> 0.2037 for B 0..300; K2 stays 1.8 ticks; T_disc 796, T_test
  870 (MBO) or 885 (MBP-1); at 1-2 trades a date a 30-minute rule needs 3.9-5.4 ticks net; Holm never binds; E.32
  D2 (V14 c) decisive: as coded a lone finalist beside null Tier B companions passes with probability about 0;
  amended 0.845 at true SR 0.20. Needs the MathReviewer's check; goes to P9 and the user decisions.
- 12:21 MathReaderM1-OpusHigh done (M1_F10_ZL.md, 513 lines; 227,344 tokens, 61 tool uses, 692.5 s). Recommends owned
  MBP-1 for discovery and MBP-1 for the test (2017-05-21..2020-11-30): USD 23.36 vs 40.96 for MBO both windows;
  8 of 12 F3 features carry over, 2 adapted, 2 dropped (IOFI5, QI3); windows 5/15/30 (60 for lambda). To check in
  session 2: where its per-date counts (median 168,917 events, 19,195 trades) came from (must be recorded logs,
  not a decode); day share assumed 83%; flagged latest 30-min entry 12:42 vs 12:50 CT; rule-9 deviation (curl first).
- 12:21 CodeExtract-HaikuMed done (X_extract_code.md: 64 code rows, 14 E.33 feature ids reading ZL; 203,484 tokens,
  51 tool uses, 373.9 s). Untraced: build_features33.py:156 prior-date ZL load (sent to the auditor).
- 12:22 ExposureAuditor-OpusHigh spawned (worker-high, opus).
- 12:23 MathReaderM3-OpusHigh done (M3_labels_ZL.md, 488 lines; 248,858 tokens, 74 tool uses, 766.9 s). Labels F15, F30,
  F60, T15, T30 (T60 out); dead zone = measured spread + 2f (f 0.880): 1.88 ticks at a 1-tick spread (0.5 slippage
  only in c_f planning); market at 1 s selects, trade-through limits reported; P3.8 re-entry caps 17/8/4 trades a
  date (not 19/9/4): test e80 0.96/1.92, K2 1.92 at 30 min (reconcile with M4's 1.8 in Part P); FOMC window
  [12:58, 13:13] recommended; EIA and EPA days as report groups. Open: rule-5 limit band source; same schema in both
  windows for labels.
- 12:23 DataFacts-SonnetHigh done (reports/stage_e34_data_facts.md; work/DataFacts-SonnetHigh/ guard34.py, opens.log 281
  guarded opens; 223,391 tokens, 55 tool uses, 782.3 s). guard34 dry check refused 9/9 + positive control; ZL MBP-1
  158,046,466 records (158,044,028 on the 816 E.33 dates = E.33's split); median 188,782 a date (p5-p95
  129,857-273,153); trades ~10%, day session 70%; bars 816 dates each, median ZL 906 / ZS 981 / ZM 842; 25 front
  changes (9 back-and-forth); MBO estimate 4.4 GB discovery, 4.9 GB test; 620 GB free. RECONCILE in session 2:
  M1 used median 168,917 and an assumed 83% day share -> recheck M1's minimum-aggregation reasoning with these facts.
- 12:28 MathReaderM2-OpusHigh done (M2_F09_ZL.md; 287,672 tokens, 101 tool uses, 1,070.3 s). Crush residual with ZL
  adjusting USE (+ which-leg-opened feature; break-even share 0.52 within a half-life vs ZM 0.70; cost/sigma 0.085 vs
  0.092); ZS/ZM lead ZL USE on bars (5/15/30-min look-backs, implied-oil gap); CL EXCLUDED (E.12/E.20 60-min lead on
  ZL; no intraday evidence; fallback one disclosed CL feature); HO/RB/RINs EXCLUDED (not owned); VECM/half-life
  prior-date features or report-only; 17 features + rules variant 4 x 3 = 12; M2 judges F09 on bars must be rules
  under V28 (LEAD RULING NEEDED in Part P: option A all-ML vs option B rules for F09).
- 12:29 ExposureAuditor-OpusHigh done (reports/stage_e34_exposure.md; 187,800 tokens, 31 tool uses, 437.7 s). No
  proposed F10/F09 feature was ever tested against a ZL outcome; earlier ZL-labelled outcomes were bar work, all
  null/FAIL; indirect: E.33's crush z and d5 for ZM labels (same series up to scale as the F09 mirror); direct: ZL own
  returns and 60-min cross-market leads (CL NQ ZN 6E GC) on ZL at h60-hF (E.12, E.20) -> proposes excluding both in
  those forms; F30/F60 labels seen only under unrelated bar mechanisms (kept); corrected the records extract (E.33 S1
  also reads ZL; S3/S4 validity flags depend on ZL); build_features33.py:156 cannot load 2020-11-30 or earlier; 10
  firewall rules + 6 proposed exclusions for the lead's ruling; open: no lower bound on ts_event in guard33.
- 12:30 session-1 end holdout status: unlocks_logged 0 on all 6 stores; soy test sealed 114, unlocks 0, all_ok
  (reports/stage_e34_briefs/holdout_session1_end.txt). No worker or shell running.

## Open choices (running list; copied into the return's section 6)
- OC-1 (0.1) FRED PSOILUSDM csv and the 16 roll symbology files not sealed (E.32 section 3, OC-0.4); refused by path in
  P1.2; no worker opens them. Reason in seal/part01_seal_check.md (the 114-file plan is pinned by E.33's freeze:
  reports/stage_e33_pipeline_freeze.sha256 line 62 holds the manifest's sha256 673fde8a).
- OC-2 (routing) Haiku extraction split into two workers (records; code) before the Opus auditor, to keep each to one
  objective; the prompt's "(+ Haiku extraction helpers)".
- OC-3 (lead exposure) The lead read E.33c_RETURN.md sections 1-3.8 (per-set G1 counts, the top-10 list, the null
  comparison) while orienting, as the prompt's read-first list requires; disclosed in the exposure file.

## RESUME HERE [SUPERSEDED by the session-3 block below] (written 12:30 PDT at the end of lead session 1, 61379f35-7e9c-4e83-8aba-8176e52367c9)

Done: T0, T1 (0.1: nothing sealed, no guard changed), T2a-c (0.2), T3.1-T3.4 (M1-M4), T4 (Part F). Every artifact is
on disk (table above). No worker or shell is running.

Session 2, in order:
1. Read docs/prompts/STAGE_E.34.md in full, then this file. Run `uv run python -m data.holdout status` and log
   unlocks_logged (CLAUDE.md). Print the ETA table in chat (memory rule) before the first spawn.
2. Lead reconciliations before writing anything that depends on them (read the artifacts by section):
   a. M1 per-date counts (median 168,917; assumed 83% day share) against DataFacts (median 188,782; 70% day share;
      p5 129,857). First check M1's folder (reports/stage_e34_briefs/work/MathReaderM1-OpusHigh/) for the source of its
      counts: it must not have decoded market data (RULES rule 2). Then redo M1's minimum-aggregation-horizon argument
      with DataFacts' numbers (lead, or a small follow-up worker).
   b. Trade caps: M3's P3.8 re-entry caps 17/8/4 a date against E.32b/M4's 19/9/4 (test e80 0.96/1.92; K2 1.92 vs 1.8
      at 30 minutes). Decide the K2 form (M4 offers a per-configuration form).
   c. Latest 30-minute entry: 12:42 CT (M1's grid) vs 12:50 CT (shared facts).
   d. ts_event lower bound (auditor; DataFacts saw 7 records with ts_event more than a day before ts_recv): a P1.2
      drop-and-count rule.
3. T5: assemble reports/stage_e34_zl_methods.md: a lead front (findings, verdict table, what P takes) + M1-M4 as
   sections (cite E.32's brief, do not repeat it).
4. T6: spawn MathReviewer-FableXHigh (worker-xhigh, model fable) on the methods file and M4's scripts; confirm
   message.model from its transcript under ~/.claude/projects/-home-kiros-li-Documents-GitHub-PropExperiment/<session>/
   subagents/ (memory: the fable alias once ran Sonnet). Opus fresh if Fable is unavailable, and say so.
5. T7 (lead, reserved): reports/stage_e34_zl_protocol.md, P1-P10 modelled on reports/stage_e32_discovery_protocol.md
   (sections: 0 13-87; P1 88-177; P2 178-253; P3 254-366; P4 367-534; P5 535-615; P6 616-682; P7 683-739; P8 740-787;
   P9 788-829; P10 830-865; read by section). Lead rulings needed and to be logged as open choices:
   i.   Model rule for F09 on bars: option A all-ML under V43 (one order-book program; E.32b recs 4.5(b) P4-P5) vs
        option B rules for F09 under V28 + ML for F10 (M2 judges rules); hence the budget and N after the run.
   ii.  The auditor's 6 proposed exclusions (ZL own returns as features; 60-minute cross-market leads on ZL) and its 10
        firewall rules for P1.5; CL excluded (M2); HO, RB, RINs excluded (not owned).
   iii. MBP-1 for discovery and test (M1; USD 23.36 vs 40.96 with MBO; difference 17.60; estimates) and the test span
        (MBP-1 from 2017-05-21 vs 2017-05-01: M4 T_test 870 vs 885; the 15 MDP 2 dates).
   iv.  P9: E.32 D2 (V14 (c)) is decisive (M4: as coded, a lone finalist beside null Tier B companions passes with
        probability about 0; amended 0.845 at true SR 0.20): the protocol states both and makes D2 a user decision
        before registration.
   v.   P10 compute-stop reference: no real-data probe is allowed here (it would compute features); set it from
        E.33c's measured fold times (reports/E.33c_RETURN.md 3.2-3.3, ref_v03.json) scaled by DataFacts' ZL sizes, as
        the protocol's own guess range (V53 item 3).
   vi.  Run-stage data plan: what to buy (ZL MBP-1 test 2017-05..2020-11; definitions for the test window), a quote
        first under user approval and a new account slot DATABENTO_API_KEY4 (absent now; acct-1/2/3 headroom under USD 3).
6. T8: ProtocolReviewer-FableXHigh (worker-xhigh, fable; confirm model). T9: fix every BLOCKING and SHOULD FIX in both
   reviews; freeze the protocol (sha256 into reports/stage_e34_zl_protocol.sha256); do not register.
7. T10: reports/E.34_RETURN.md (the prompt's 8 fixed sections), one progress.md entry, one docs/STAGES.md line, end
   checks (bash reports/stage_e34_briefs/checks.sh end > reports/stage_e34_briefs/checks_end.txt), session cost from
   transcripts (session 61379f35 + later sessions; main .jsonl plus subagents/**/*.jsonl; never estimated), confirm no
   worker or shell running, then one commit "Stage E.34 ZL program design and protocol" with only this stage's files
   (leave raw pages under reports/stage_e34_briefs/work/*/pages/ untracked; logs with sha256 are committed). No push.
   pytest is not required by the prompt (Part 0 changed no guard).

Worker token counts from the completion notices (for orientation only; the cost table must come from transcripts):
ExposureExtract 215,067; CodeExtract 203,484; ExposureAuditor 187,800; M1 227,344; M2 287,672; M3 248,858; M4 172,680;
DataFacts 223,391.

READY FOR WIPE 12:30 PDT

## Session 2 (lead 92545abe-53bf-484b-bbfb-6c6b8a67b381, started 13:51 PDT; pause 12:30-13:51 between sessions, not work)
- 13:51 prompt (249 lines) and this file read in full. 13:52 holdout status: unlocks_logged 0 on all stores, all_ok
  true (reports/stage_e34_briefs/holdout_session2_start.txt). No E.34 worker or shell running; T5-T10 artifacts absent.
- 13:55-14:02 lead reconciliations L.a-L.e written: reports/stage_e34_briefs/L_lead_reconciliations.md (5-minute
  floor stands at the measured 76.2% T day share; caps 17/8/4; K2 per-configuration measured form; latest 30-min entry
  12:42 CT; P1.2 ts_event drop-and-count rule; test span 2017-05-22..2020-11-30, T_test 870 on MBP-1).
- 14:02 order changed to shorten the critical path (OC-4): MathReviewer starts on M1-M4 + L now; T7 (protocol) next;
  T5 (methods front + assembly) during T8. Briefs appended to reports/stage_e34_briefs/BRIEFS.md.
- 14:03 spawned MathReviewer-FableXHigh (worker-xhigh, model fable) and ComputeRef-OpusHigh (worker-high, model opus;
  output reports/stage_e34_briefs/P10_compute_ref.md).
- 14:09 T7 protocol part 1 written (header, 0, P1-P3; 295 lines) at reports/stage_e34_zl_protocol.md.
- 14:09 ComputeRef-OpusHigh done (P10_compute_ref.md; work/ComputeRef-OpusHigh/ref_zl.py, ref_zl.json; 140,819
  tokens, 23 tool uses, 333.9 s; model claude-opus-5-5 confirmed): R_ZL low 3,022 s / central 7,965 s / high 22,651 s;
  3 x central 23,895 s covers the all-high case; LOGIT 0.45-1.0 GB a process. Not verified independently (goes to the
  ProtocolReviewer).
- 14:12 T7 protocol draft v0.1 complete (576 lines; P0-P11; feature tables spliced verbatim from M1 section 7 and M2 (f)
  by sed line ranges). 14:13 two lead fixes (0.3 LT8 on ZL; P9.4 multipliers at N 1038 = 1.633 / 1.539 from
  funnel.multiple_comparisons.expected_max_sharpe: e(838) 3.2045, e(1038) 3.2657, e(1138) 3.2917).
- 14:14 spawned ProtocolReviewer-FableXHigh (worker-xhigh, model fable; output review/ProtocolReview.md).
  MathReviewer-FableXHigh still running.

## Open choices added in session 2 (copy into the return's section 6)
- OC-4 (order) MathReviewer started on M1-M4 + L before the methods file was assembled; T5 runs after T8 (shorter
  critical path). The methods file's front summarises reviewed sections.
- OC-5 (model rule, P2) option A: all 4 sets as ML under V43 (S_crush, S_prop, S_book, S_pool x 5 labels x 10 settings
  = 200; N 1038), not option B (12 F09 rules + 50 F10 ML = 62; N 900). Reason: every configuration is labelled on and
  traded against ZL's own book with the measured fill model and carries ZL book context; E.33 precedent (crush and
  propagation sets as ML under V51). User may choose B before registration (an amendment).
- OC-6 (exposure, P1.5) X rules 1-10 and exclusions E1-E6 adopted as written; CL excluded in every form (M2's fallback
  rCL_15 not taken); HO/RB/RINs excluded; VECM loadings and half-life report-only (P6.5).
- OC-7 (data, P1/P9/P11) route A: MBP-1 in both windows; test trade dates 2017-05-22..2020-11-30 (T_test 870; L.e);
  test definitions bought with the MBP-1, else the run stops before the read (no rule substitute for C.7 or limits).
- OC-8 (P3.6) FOMC window not adopted (E.32 has none; new calendar dependency); EIA WPSR Wednesdays 09:28-10:00 CT a
  report-only stratum; EPA RVO dates dropped (no sourced calendar, M3 searched).
- OC-9 (L.b) caps 17/8/4 replace 19/9/4; K2 per-configuration measured form, computed at the realised T_test.
- OC-10 (P8 G2) 0.50 ZL tick (USD 3.00), half a tick of the traded contract as E.32; the firm-fee reason does not arise.
- OC-11 (P4) L1.7's volumes from bars for all three legs (M2 took ZL's from its book).
- OC-12 (P10.3) compute reference R_ZL 7,965 s central (3,022-22,651 s), stop 3 x R_ZL = 23,895 s; rescaled by the
  frozen formula at the process counts logged before the first fit.
- OC-13 (P9.4) E.32-D2: both forms stated with M4's simulation; recommendation amend; the user decides.
- OC-14 (L.c) latest 30-minute entry 12:42 CT; E.32b's 12:50 CT superseded. OC-15 (L.d) ts_event drop-and-count rule.
- OC-16 (L.a) 5-minute floor; M1's SD criterion read at the 5th-percentile date. OC-17 (P6) FDR: BH q = 0.10, report
  only. OC-18 (P10.3) cut order S_pool, S_crush, S_book, S_prop. OC-19 (P3.6/P9.2) test-window release calendar
  built before the read as E.32 P9. OC-20 (P1.2) E.33's ZS split not allowed (no ZS book feature).

## RESUME HERE (session 3; written 14:16 PDT by lead session 2, 92545abe-53bf-484b-bbfb-6c6b8a67b381)

Done in session 2: L.a-L.e (L_lead_reconciliations.md); P10 reference (P10_compute_ref.md); protocol DRAFT v0.1
(reports/stage_e34_zl_protocol.md, 576 lines, P0-P11); reviewers spawned (both models confirmed claude-fable-5-1 from
transcripts). Rulings OC-4..OC-20 above. Still open: T6/T8 results (see the lines after this block), T9, T5, T10.

Session 3, in order:
1. Read docs/prompts/STAGE_E.34.md in full, then this file. `uv run python -m data.holdout status` (log
   unlocks_logged). Print the ETA table in chat before the first spawn.
2. Read reports/stage_e34_briefs/review/MathReview.md and review/ProtocolReview.md by section (verdict, then each
   BLOCKING and SHOULD FIX item). Fix every BLOCKING and SHOULD FIX:
   - protocol items: edit reports/stage_e34_zl_protocol.md (bump status to DRAFT v0.2 while fixing; log each fix
     with its review item id in a "Fix log" section at the end of the protocol or in review/FixLog.md);
   - Part M items: never edit the worker files M1-M4; put the correction into the methods file's errata (step 3)
     and into L if it is a lead ruling; carry any changed number into the protocol.
   - If any BLOCKING item was fixed, or any fix changes a declared choice or number, spawn FixVerifier-FableXHigh
     (worker-xhigh, model fable; confirm message.model) on the diff plus the fix log, and fix what it returns.
3. T5: write reports/stage_e34_zl_methods.md = a lead front (purpose, sources, a verdict table per topic M1-M4 and
   L.a-L.e, what Part P takes from each, errata from MathReview) followed by the files concatenated unchanged:
   stage_e34_briefs/M1_F10_ZL.md, M2_F09_ZL.md, M3_labels_ZL.md, M4_power_ZL.md, L_lead_reconciliations.md (cat;
   do not re-read them whole). Cite E.32's brief, do not repeat it.
4. T9 freeze: status line FROZEN v1.0 (date, lead, review rounds); write reports/stage_e34_zl_protocol.sha256 with
   sha256sum of the protocol and of every P10.4 file (protocol, methods, data facts, exposure, L, P10_compute_ref,
   E.32 protocol, protocol_v0.3.diff, stage_e33_pipeline_freeze.sha256, review files). Do not register; N 838.
5. T10: reports/E.34_RETURN.md (the prompt's 8 fixed sections; section 6 = OC-1..OC-20 + any new; section 7 =
   E.32b-D2, E.32b-D3, E.32-D2 (recommend amend), the model rule (recommend option A), the test purchase (quote on
   DATABENTO_API_KEY4, about USD 23.36 + definitions), each with a recommendation); one progress.md entry; one
   docs/STAGES.md line; end checks `bash reports/stage_e34_briefs/checks.sh end > reports/stage_e34_briefs/checks_end.txt`;
   session cost from transcripts (sessions 61379f35-7e9c-4e83-8aba-8176e52367c9, 92545abe-53bf-484b-bbfb-6c6b8a67b381
   and session 3: main .jsonl + subagents/*.jsonl; usage summed by message.model; one line per worker spawn; delegate
   to CostTally-SonnetMed (worker-medium, model sonnet) with a small script; never estimate). Final ETA table in chat
   and in the progress entry. Confirm no worker or shell is running, then one commit "Stage E.34 ZL program design and
   protocol" with only this stage's files (git add the reports/stage_e34_* files and folders except raw pages under
   reports/stage_e34_briefs/work/*/pages/; logs with sha256 are committed; also progress.md and docs/STAGES.md). No
   push. pytest not required (Part 0 changed no guard).
- 14:23 MathReviewer-FableXHigh done (review/MathReview.md, 383 lines; scratch work/MathReviewer-FableXHigh/;
  307,898 tokens, 44 tool uses, 1,224.3 s; claude-fable-5-1 confirmed at spawn). Verdict GO WITH FIXES: 2 BLOCKING,
  4 SHOULD FIX, 14 NOTE. All 4 worker scripts open no market data and reproduce byte for byte; independent recompute
  matches every M4 and L number. B1: F10.7 zero rule wrong on a rise-then-fall second (condition on the last change
  being a rise). B2: F10.9 fill attribution wrong if post-fill reductions sit on T records (state differences over
  all records, subtract batch T lots once). SF: L.b "20-cap never binds" false for TB15/TB30 (TB exits early); MBP-1
  bad-book reading differs between M1 (batch) and M3 (F_LAST record) and so between protocol 0.3 and P4's F10
  preamble; M2's rule grid keeps the retired 12:50 CT cap (option B only); M2's bar-bounce SD omits sqrt(2). The M2
  rerun rewrote m2_examples.json (identical content; mtime only). All for session 3's step 2.
- 14:30 ProtocolReviewer-FableXHigh done (review/ProtocolReview.md, 401 lines; scratch work/ProtocolReviewer-FableXHigh/
  recompute_p7.py/.out, ref_zl_rerun.json/.out; 349,705 tokens, 59 tool uses, 1,010.1 s; claude-fable-5-1 confirmed).
  Verdict GO WITH FIXES: 2 BLOCKING, 12 SHOULD FIX, 14 NOTE. B1: ZM ohlcv-1m bars are NOT owned for the test window
  before 2019-05 (seal document: ZM raw chunks only 2019-05..2020-11; ZL and ZS have 44 chunks from 2017-04), so F09
  needs ZM.v.0 ohlcv-1m 2017-05-01..2019-04-30 bought with the test data (P9.1, P11 and the BRIEFS shared fact are
  wrong for ZM; the reviewer drafted the remedy text). B2: two MBP-1 bad-book rules (0.3 line 64 vs P4 line 357);
  use the batch form (E.33's frozen code, reading FA-4). Every threshold, cap, multiplier, count and R_ZL reproduces
  with the frozen functions (G3 0.1746, b_test 0.166967, G4 0.2028, SR80_test 0.1957, e80 0.97/1.94/3.74, 1.633/1.539,
  R_ZL 7,965 s). No leak found. Not rerun: the P9.4 simulation (copy-checked). [unverified]: NOPA's 2017-2020
  release time; MBP-1 F-record semantics.
- 14:30 session-2 end holdout status: unlocks_logged 0 on all 6 entries, all_ok true on all 6
  (reports/stage_e34_briefs/holdout_session2_end.txt); REGISTRATION.md 0 bytes; no worker or shell running.
- Session 3 step 2 therefore has 4 BLOCKING (MathReview B1 F10.7, B2 F10.9; ProtocolReview B1 ZM test bars, B2 bad-book
  rule, the same as a MathReview SHOULD FIX) and 16 SHOULD FIX to fix, then FixVerifier-FableXHigh (required: BLOCKING
  items were found), then freeze. The ZM-bar purchase also goes into the return's data plan and section 7.

READY FOR WIPE 14:30 PDT
- 15:10 PDT Wipe watcher restarted the lead (fresh session).

## Session 3 (lead 4b0394a9-db7b-4958-80d5-d40327048001, started 15:10 PDT; pause 14:30-15:10 between sessions, not work)
- 15:10 prompt (249 lines) and this file read in full. 15:11 holdout status: unlocks_logged 0 on all 6 stores, all_ok
  true on all 6 (reports/stage_e34_briefs/holdout_session3_start.txt). No E.34 worker or shell running; T5, T9, T10
  artifacts absent; protocol still DRAFT v0.1.
- 15:13 both reviews read (verdict, BLOCKING, SHOULD FIX, NOTE). v0.1 snapshot for the fix diff:
  reports/stage_e34_briefs/review/protocol_v0.1.md (sha256 c49b4aef..., identical to the live file at 15:13).
- Next: S3.1 fixes (lead) -> S3.2 FixVerifier-FableXHigh + S3.3 T5 methods file -> S3.4 freeze -> T10.
- 15:26 S3.1 done: protocol DRAFT v0.2 (674 lines): header and sources edits, then 42 exact-once replacements
  (scratchpad apply_v02.py); diff review/protocol_v0.1_to_v0.2.diff (318 lines); fix log review/FixLog.md (4 BLOCKING,
  16 SHOULD FIX, NOTEs acted on); L.f appended to L_lead_reconciliations.md (L.f.1-L.f.5); BRIEFS RULES correction (ZM
  test bars owned only 2019-05..2020-11) and the FixVerifier brief appended. ZM bars added to the test purchase (OC-21);
  estimates from the spend ledger: ZM ohlcv-1m about USD 1.46 (73 settled months, median 0.0608), definitions at most
  about 1.66 (39 months, median 0.0385), test total about USD 26.5.
- 15:28 S3.2 FixVerifier-FableXHigh spawned (worker-xhigh, model fable; output review/FixVerify.md). Next: S3.3 T5
  methods file while it runs.
- 15:29 S3.3 T5 done: reports/stage_e34_zl_methods.md (2,199 lines: lead front with the verdict table and 21 errata,
  then M1-M4 and L concatenated unchanged with sha256 tags; L includes L.f). If L changes again, re-assemble.
- 15:32 T10 return drafted: reports/E.34_RETURN.md (8 sections; summary 298 words); placeholders {{END}}, {{FREEZE}},
  {{FV}}, {{OC_FV}}, {{COST}}, {{M:*}}, {{T:*}} to fill after FixVerify, the freeze, the end checks and CostTally.
- 15:45 FixVerifier-FableXHigh done (review/FixVerify.md, 237 lines; claude-fable-5-1 confirmed; 265,347 tokens, 70 tool
  uses, 1,034 s): PASS WITH FIXES; 4/4 BLOCKING fixed, 15/16 SHOULD FIX fixed + 1 partly (PR-S4); 32/32 recomputations
  match; no new leak; new F1-F4 SHOULD FIX, F5-F11 NOTE.
- 15:47 S3.4 done: F1-F11 applied in the verifier's wording (18 exact-once replacements; v0.2 snapshot
  review/protocol_v0.2.md; diff review/protocol_v0.2_to_v1.0.diff 96 lines); FixLog round 2; methods erratum 22.
  FROZEN v1.0: reports/stage_e34_zl_protocol.md sha256 46556059b09b831794884514ef989a4b1b29909595157bf59daa04883ea0213b;
  reports/stage_e34_zl_protocol.sha256 lists 17 files (sha256sum -c OK; E.32 protocol c4ffb9d7 unchanged). Do not edit
  any of the 17 files from here on. Not registered; N 838. Next: fill the return, progress, STAGES, end checks, cost.
- 15:49 return filled (FixVerify, freeze, OC-28/29, end checks); progress.md entry appended (cost pending); docs/STAGES.md
  E.34 line inserted after E.32b. 15:49:04 end checks: reports/stage_e34_briefs/checks_end.txt (all unchanged: holdout 0
  unlocks on 6 stores; seal 114/114; guard33 4/4 refused; REGISTRATION.md 0; harness OK; ledger 37,290 lines 42589d7b;
  N 838, registry 11777e46; amendments 511ae4c3; KEY4 absent). Next: CostTally-SonnetMed, then fill cost, commit.
- 15:50 CostTally-SonnetMed done (work/cost/: make_cost.py, cost_raw.txt, ret_cost_tokens.md, initial_eta.md; problems=0;
  128,757,530 tokens to 15:50:05; lead 35.8%). 15:53 return section 8 and the progress cost section filled; untracked
  large files and raw pages hashed (untracked_large_files.sha256, untracked_pages.sha256; OC-30). No worker or shell
  running. Last step: one commit "Stage E.34 ZL program design and protocol" (hash in git log); no push.
