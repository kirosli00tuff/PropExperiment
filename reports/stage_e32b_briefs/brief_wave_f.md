# Stage E.32b wave F (session 4): fixes for the Step 4 reviews (lead, Opus 5.5 max, 2026-10-29 08:46 PDT)

B = reports/stage_e32b_briefs (repo root /home/kiros-li/Documents/GitHub/PropExperiment). The spec
reports/stage_e32b_ranking_spec.md is hashed (sha256 09ebe697...8635) and does not change. Prompt Step 4: "Fix every
BLOCKING and SHOULD FIX item before the return." Common rules for every worker below:
- Read files by section (grep, line ranges, short scripts printing only what you need); never load a large JSON or
  report whole. Keep command output short (pytest -q; logs to files, read the tail).
- No outcome is read, no data file (bars, MBO, parquet, data/) is opened, no Databento call, no holdout unlock, no
  TopstepX/ProjectX, nothing under live/ or ops/, no commit, no push, no edits to E.32 or E.33 files. Workers do not
  spawn workers. Times from `date` (PDT).
- Write only the files your section names. Everything else is read-only. If a fix needs a judgment or a change beyond
  your section, stop and report it to the lead instead of deciding.
- Return three things: the report path, a summary of at most 200 words, and anything you could not finish.

## F1 ScoreFixer-OpusHigh (worker-high, opus): RV1 S1, S2, S3, N1, N2

Read: B/REVIEW_ranking.md lines 19-58 (S1-S3, N1-N2); B/work/score/README.md, SCHEMA.md section 4,
s32b_layer2.py (line 43), score32b.py (line 144 tie-break), the score tests; B/work/econ/README.md lines 40-50, 145-155
and 180-190; B/work/rankmd/ (template.md lines 10-20, 55-70, 115-125; make_rankmd.py:145; extra_frags.py:41;
assemble.py); B/score32b_out.json's inputs record (paths and sha256 of the 05:40:30 PDT run).
1. s32b_layer2.py: the tie-break cost per attempt reads `cost_per_attempt_mkt_mu0` (the market case, per the lead's
   session-2 EconSetup ruling and spec 4), and the output carries the limit-case value beside it as
   `cost_per_attempt_lim`. First check that `cost_per_attempt_mkt_mu0` exists in every econ block the scorer reads
   (primary, spread1, E_dir60 and the S_mean file B/econ32b_smean.json); if it is missing anywhere, stop and report.
2. score32b.py: list in `input_checks` every econ block whose search records `confirmed: false` (pair, block, search
   name, recorded value, number of violations). RV1 found bulenox|CL and bulenox|NG (primary and spread1).
3. Tests for 1 and 2 in the existing test files (fixture style); run `uv run pytest -q
   reports/stage_e32b_briefs/work/score/` and report the counts.
4. Copy B/score32b_out.json and .md to B/work/score/score32b_out_run2.json and .md (the 05:40:30 run; leave the run1
   files alone). Rerun score32b.py with exactly the 05:40:30 run's inputs and --rulings file (paths from its inputs
   record; the score run reads work/F5run/F2_attention_listcodes.json per LR-ATT, not the README's F2_attention.json).
   Note: econ32b.json was rewritten at 07:27:59 by econ pass 2's collect (it added the E_dir 30/120/240 blocks for the
   top 15): record the old (0567890e...) and new sha256. Output to B/score32b_out.json and .md; log
   B/work/score/score_run3.log.
5. B/work/fix4/score/diff_score.py: compare run2 and run3 for every pair and every variant: S, L1, L2, every
   criterion, gates, ranks, top 5, top 15, MNQ ranks, survivors, ties. Expected: only the cost fields, input_checks,
   input hashes and generated time differ. If any score, gate or rank differs, stop and report before step 6.
6. reports/stage_e32b_ranking.md, rebuilt the way the RankingWriter built it (work/rankmd: find the commands in the
   folder; template text edits go into template.md so a rebuild keeps them):
   - table 3a's cost column shows the market-case value, labelled as the tie-break cost (market case), with the
     limit-case value beside it or in a note under the table;
   - template lines 62-63 (RV1 S2): replace the false generalisation with: no code with a KNOWN notional loses c = 1
     to a code with an unknown notional in metals, crude, grains or rates; crypto's c is 0 throughout and undetermined
     (ETH, notional unknown only for lack of an F3 close, very probably holds the family's largest notional ADV);
   - line 15 (N2): the econ32b.json hash of the run the file now reports, and the 05:40:30 run's 0567890e named as such;
   - line 121 (N1): D3 mean 3.50 (exact 3.5049); recompute every mean printed in that sentence at 2 decimals and fix any
     other that differs;
   - econ notes (S3): bulenox|CL and bulenox|NG, primary and spread1: the bisection did not confirm, so the recorded
     values are the full-grid thresholds (k_final; mu* 1.76, mu10K 2.44), equal to E.28's; E for both pairs is right;
   - keep every other sentence, including every lead ruling's text, unchanged. Report a unified diff summary (lines
     changed) of the ranking file against its pre-rebuild copy (save that copy as B/work/fix4/score/ranking_pre.md).
7. B/work/econ/README.md: add a dated note under line 184's "none unconfirmed" (true of the regression): the real pass
   1 had two unconfirmed searches (the pairs above). Do not rewrite the line.
8. List (do not change) every stage file that records score32b_out.json's sha256 or reads cost_per_attempt from it
   (grep B, B/work/F5, B/work/F5run, B/work/R2, B/work/scope, reports/stage_e32b_*.md).
Write only: B/work/score/s32b_layer2.py, score32b.py, the score tests, B/work/score/score32b_out_run2.*,
score_run3.log, B/score32b_out.json/.md (by the rerun), B/work/rankmd/ (template and outputs),
reports/stage_e32b_ranking.md, B/work/econ/README.md (the dated note), B/work/fix4/score/. Report:
B/work/fix4/score/score_fix_report.md (each change with file:line, test counts, the diff result, both econ hashes, the
step-8 list).

## F2 R1Fixer-OpusHigh (worker-high, opus): RV2 B1 (text part) and S6, N2

Read: B/REVIEW_recs.md lines 18-50 (B1), 74-78 (S6), 88-91 (N2); B/R1_closed_lines.md and .json (R1-11, R1-15);
B/R2_dossiers.md (errata block at the top; catalog rows for R1-11 and R1-15); B/R2_Q_ratings.md (RTY|F09 and ZL|F09
Q3 reasons); B/RULINGS.md last block (LR-Q3b).
1. Verify RV2's G17 facts read-only against the frozen code and reports, quoting file:line: the G17 definition
   (ml_route_v2/signals/generic.py about line 22); the own-cluster rule (c1_replication/c1b.py about line 53 and
   generic.py's SignalSpec legs); E.12 Gate 0's G17 rows at h60 and h120 (reports/stage_e12_gate0.md about lines
   158-164 and 222); E.20's 36 frozen features (pattern_search/constants.py about line 59;
   reports/stage_e20_search_freeze.json feature_names: read only that key with a script), its decision times (t4 = 14:08
   CT for equity; find t1-t3 if they are stated), horizons and window; which leads were live on RTY/M2K and on ZL. If
   any fact disagrees with RV2, report it and do not write it.
2. B/R1_closed_lines.md and .json, lines R1-11 and R1-15: add the cross-market content: "includes G17: 60-minute log
   returns of the other clusters' lead prices (NQ, ZN, 6E, CL, GC, ZC; E.12 also MES, MBT), never applied on the
   product's own cluster; live on RTY/M2K: ZN, 6E, CL, GC, ZC; live on ZL: NQ, ZN, 6E, CL, GC" (as verified), with the
   file references, tagged "added 2026-10-29 (session 4, RV2 B1/S6)". JSON: add one new field per line; no existing
   value changes; the file must load and its trial counts still sum to 838.
3. B/R2_dossiers.md: extend the errata block at the top with (a) the G17 fact for R1-11 and R1-15, and tag the two
   catalog rows in this file "[corrected s4: see errata]" with the added text; (b) the RTY|F09 Q3 reason "no
   cross-market configuration closed on RTY or M2K" is wrong (60-minute leads from five other asset classes were
   searched on RTY and M2K at h60-hF); LR-Q3b sets Q3 = 1 for C112-C116 and C138-C139, the leg-level reading is the
   sensitivity; (c) RV2 N2: E.29 3.2 measured only the CL, ZM, GC and NQ pairs, none of YM-MNQ, YM-RTY or MNQ-RTY, so
   the pools use the spec's default rho 0.5; fix the wording wherever this file says E.29 measured no correlation
   between the pool members; (d) B/R2_dossiers_for_rating.md is kept exactly as the CombinationScorer rated it.
4. B/R2_Q_ratings.md: prepend a "Lead errata (session 4)" block saying the rater's RTY|F09 and ZL|F09 Q3 lines are
   kept as written, that LR-Q3b replaced the value with 1 for C112-C116 and C138-C139 (reason as in RULINGS.md), and
   that B/R2_combinations.json carries both Q3 and Q3_rater. Change no rating line.
5. Grep and list (do not edit) every other place in the stage's deliverables with the same incomplete statements
   (R1-11/R1-15 described without the cross-market features; "no cross-market configuration" on RTY or M2K; "E.29
   measured no correlation"): reports/stage_e32b_recommendations.md, B/work/R4/draft_sections.md (about 316-319),
   reports/stage_e32b_ranking.md, reports/stage_e32b_holding_scope.md. Give file:line and the exact text.
Write only: B/R1_closed_lines.md/.json, B/R2_dossiers.md, B/R2_Q_ratings.md, B/work/fix4/r1/. Do not edit
R2_combinations*.json, r3 outputs, R2_dossiers_for_rating.md, the recommendations, ranking or scope files,
work/R4/*, STATE or RULINGS. Read-only on strategy/, ml_route_v2/, pattern_search/, c1_replication/ and other stages'
reports. Report: B/work/fix4/r1/r1fix_report.md (each verified fact with its quote, each edit before/after, the
step-5 list).

## F3 RecsAssembler-OpusXHigh (worker-xhigh, opus): the recommendations file after LR-Q3b; RV2 S1-S4, S6

Starts after F2 and the lead's session-4 text. Read: B/work/R4/lead_sections.md (the lead's text, session 4; diff it
against B/work/R4/lead_sections_s3.md to see what changed); B/r3_out.json (primary after LR-Q3a, LR-V31, LR-Q3b),
B/work/R2/r3_out_q3only.json, r3_out_nozlw.json, r3_out_ts150_v2.json, r3_out_q3bleg.json (the leg-level F09
reading, = the session-3 primary), r3_out_v1.json; B/R2_combinations.json (C147 EQ3 F08 topstep, C141 ZL F10 ibkr,
C113 RTY F09, C138, C139, C140); B/F5_holding.json (pairs.<firm|code>.rows.<h>: sigma, e80_test, gross_detect_test,
n_cap, trades_per_year); B/F4_facts_unmasked.json (fees, margins); B/SR80.json; B/work/R4/draft_sections.md (version
2); B/work/fix4/r1/r1fix_report.md (its step-5 list) and the updated B/R1_closed_lines.md (R1-11, R1-15);
B/REVIEW_recs.md lines 51-91 (S1-S6, N1-N2). The assembled file reports/stage_e32b_recommendations.md (936 lines):
read it by section (its headings: grep "^#").
1. B/work/R4/draft_sections.md -> version 3 (copy version 2 to B/work/R4/draft_sections_v2.md first):
   - section 1: the R4 list verbatim from r3_out.json, grouped: program 1 = C140 ZL F10 + C138 ZL F09 (one sealed
     read; F10 first), then C072 MNQ F08, C021 YM F08, C147 EQ3 F08 (pool of YM, MNQ, RTY at Topstep);
   - program 1's fact table: C140 first; C138 with Q3 = 1 (LR-Q3b) and C 2.65;
   - a new program section for C147, in the same format as the others: (a) fact table per member (c_f, sigma_30,
     c_f/sigma, K per member, K_eff 1,305 at rho 0.5 within the class, q 0.158, e80 test per member in ticks =
     q x sigma_30, trades a year, clean test window per member: YM 0 under LR-V31, MNQ and RTY as recorded, the unread
     2024-03..2025-03 and 2026-06-17 onward stretches; Q6 per member; data schema and cost), (b) pre-registration
     outline (one registration, members pooled, F08 at 15-30 minutes, h_c 30; under the decisions in force YM cannot
     enter, so the outline says how the pool is cut to MNQ and RTY), (c) data purchase plan with the quotes to obtain
     (V31: no YM purchase; V51: 2024-03+ needs the user's approval), (d) kill-criteria facts;
   - RTY F09 (version 2's program 2) moves to an appendix "Dropped by LR-Q3b: RTY F09 (C113, C 2.50)", its tables
     kept, with its overlap text corrected from the R1 fix (the "no cross-market configuration on RTY or M2K" and "E.20's
     36 late-session features" passages: say which cross-market leads were live on RTY/M2K, as verified in r1fix_report);
   - the own-broker section becomes C141 ZL F10 at IBKR (C 2.60): fact table from R2_combinations/r3_out (Q1-Q7, c_f,
     Q6 = 3 with its deduction, margin), outline and data, kill-criteria facts; one line: C139 ZL F09 at IBKR is 2.50
     under LR-Q3b;
   - YM's e80 test printed at one decimal is 12.2 (0.193625 x 63.2336 = 12.24; RV2 S1);
   - section 9 (sensitivities): the R4 list and best own-broker of q3only, nozlw, ts150_v2, q3bleg and v1 under the
     current files; ts150_v2 has n_reaching_2 = 5 (its printed "fewer than 3 reach 2.00: False" is a label; RV2 N1).
2. reports/stage_e32b_recommendations.md (copy the current file to B/work/R4/recommendations_s3.md first), rebuilt
   section by section from the current sources:
   - every paragraph of lead_sections.md appears verbatim (sections 4.1, the candidate cases, priors and kill
     criteria, the dropped-RTY note, the F01 note, 5's paragraph, 6, 7). Never edit the lead's text; list any number in
     it that disagrees with the files under "Lead check" (file, field, value), or write "none";
   - section 0, Summary (RV2 S4): rewrite from the current lead text and r3_out.json, at most 300 words: the R4 list in
     order with C and priors, the kill criteria in one line each, the stop rule, the four user decisions; nothing in it
     may contradict the lead text (no "about 1.5% each", no RTY fallback);
   - section 1 (R1): the R1-11 and R1-15 rows with the added cross-market content from the updated R1 file;
   - sections 2-3: correct every passage r1fix_report's step 5 lists for this file; regenerate the R3 tables (top 20,
     gated list 3.1, sensitivities 3.2 with all five runs) from the current r3 outputs;
   - section 4: 4.0 the R4 list and grouping; 4.2 facts for lead decisions: add an item for RV2 B1 with the lead's
     resolution (LR-Q3b, RULINGS.md last block); the ZL program (F10 first), MNQ F08 and YM F08, the new EQ3 F08 pool
     with draft v3's tables, the dropped-RTY note (lead text) with its tables in an appendix, the F01 note;
   - section 5: C141's tables; sections 6 and 7: the lead text; section 8: add patch_v31_q3_lead.py's q3bleg mode,
     r3_out_q3bleg.json and LR-Q3b.
3. Check the rebuilt file by grep and report the counts: "12.3 ticks", "not a small-cap lag", "priors of 1.5-4%",
   "about 1.5% each", "final build only if", "no cross-market configuration", "measured no correlation" must give 0
   (except inside a quote that says it was corrected).
Write only: reports/stage_e32b_recommendations.md, B/work/R4/draft_sections.md and draft_sections_v2.md,
B/work/R4/recommendations_s3.md, B/work/fix4/recs/. Read-only: lead_sections.md, every r3 output and combinations
file, F4, F5, R1 and dossier files, the ranking and scope files, STATE, RULINGS. Report:
B/work/fix4/recs/recs_fix_report.md (changes by section, word counts, the Lead check, the step-3 counts).

## F4 FixVerifier-FableXHigh (worker-xhigh, fable): independent check of every session-4 fix and the E_dir table

Starts after F1, F2, F3 and the lead's L10-L11. You did not produce any of the work below. Read the reviews' items
first (B/REVIEW_ranking.md lines 19-58; B/REVIEW_recs.md lines 18-91), then the fix reports
(B/work/fix4/score/score_fix_report.md, B/work/fix4/r1/r1fix_report.md, B/work/fix4/recs/recs_fix_report.md) and the
STATE rows L10 and L11 (reports/stage_e32b_STATE.md, the "Session 4" section). Use your own scripts in
B/work/fix4/verify/; you may run, but must spot-check, the earlier reviewers' helpers (B/work/rv1/, B/work/rv2/).
1. RV1 S1-S3, N1-N2: the scorer's tie-break reads the market-case field (cost_per_attempt_mkt_mu0) and the limit case
   is kept beside; tests pass (`uv run pytest -q reports/stage_e32b_briefs/work/score/`); run3 against run2
   (B/work/score/score32b_out_run2.json vs B/score32b_out.json): by your own diff only the expected fields differ (no
   S, criterion, gate, rank, top 5, top 15 or variant result); the ranking file's table 3a column and label; the S2
   sentence is true (check the ETH/MBT notional arithmetic from F4); the S3 note (bulenox|CL, bulenox|NG: unconfirmed
   bisection, full-grid thresholds 1.76 / 2.44, equal to E.28's) and the new input_checks entries; the N1 means at 2
   decimals; the N2 hashes.
2. RV2 B1 (text) and S6: the G17 facts against the frozen code (read generic.py, c1b.py, pattern_search/constants.py,
   the E.12 Gate 0 report rows and the E.20 freeze's feature_names yourself); the R1 file edits (JSON loads, trial
   counts sum to 838, no existing value changed); the dossier and R2_Q_ratings errata; R2_dossiers_for_rating.md not
   modified after the rating (mtime before 06:01 PDT).
3. LR-Q3b: B/R2_combinations.json Q3 = 1 with Q3_rater kept for C112-C116 and C138-C139 and no other Q3 change against
   work/R2/R2_combinations_q3bleg.json; r3_out.json and the five sensitivity outputs reproduce from the spec 8 text by
   your own recomputation (Q4-Q7, C, order, R4, best own-broker); q3bleg's R4 equals the session-3 06:49 list in the
   STATE row D3r3b.
4. The lead's session-4 text (B/work/R4/lead_sections.md): every number against the files: C values; the priors'
   arithmetic (0.04 x 0.49, 0.05 x 0.49, the program's about 4%); EQ3's K_eff 1,305 = 3 x 870 / (1 + 2 x 0.5), q 0.158 =
   0.193625 x sqrt(870 / 1,305), member thresholds 10.0 / 23.3 / 8.2 ticks (q x sigma_30 from F5_holding.json); YM 12.2,
   MNQ 28.5; the RTY figures; C139 2.50, C141 2.60, Q6 3, 2.50 vs 2.38; the base rate 1/19 on 17 lines with outcomes;
   the F09.E06 wording against B/R2_dossiers_for_rating.md (about line 1300); the E.12/E.20 coverage sentence.
5. The recommendations file: the lead text appears verbatim; the summary agrees with the lead text and r3_out.json;
   the R4 and sensitivity tables equal the r3 outputs; the EQ3 F08 and C141 fact tables; the RTY appendix's corrected
   overlap text; RV2 S1-S4 and S6 resolved.
6. The scope file (reports/stage_e32b_holding_scope.md): S5's range (minimum of gross_detect_test at 30 over the 15
   pairs, maximum); every cell of the section-4 E_dir table against econ32b.json (15 pairs x E_dir30/60/120/240 x
   mu*_mkt, mu10K_mkt, m*, m10K, cap); the lead's section-4 reading and the summary bullet (m10K lowest at 30 and rising
   with h in 15/15; above cap at 120 for 4 and at 240 for 14; m* lower at 240 than 30 in 8/15; 9 zero cells; no
   unconfirmed E_dir search); no PENDING, PLACEHOLDER or "still running" left.
7. Process: no session-4 script read an outcome or a data file (check what each reads); holdout status before and
   after your work (`uv run python -m data.holdout status`, unlocks_logged 0).
Write only B/REVIEW_fixes.md and B/work/fix4/verify/. Verdict PASS, PASS WITH FIXES or FAIL; findings as BLOCKING,
SHOULD FIX, NOTE, each with file:line, evidence and the fix; a "Checks performed" list and a "Could not check" list.

## F5 CostTabler-SonnetHigh (worker-high, sonnet): the session-cost script for the four lead sessions

Objective: a script that computes this stage's session cost per CLAUDE.md "Session cost", ready for the lead to rerun
at the very end with the final end time. Adapt (do not rewrite from scratch) reports/stage_e26_briefs/cost.py or
reports/stage_e25_briefs/make_cost.py (both use reports/stage_e10_briefs/cost.py's scan, which keeps each message's
final usage; the E.4 script undercounts output). Write B/work/cost/make_cost.py; usage:
`python3 reports/stage_e32b_briefs/work/cost/make_cost.py <to ISO UTC>`; it writes B/work/cost/cost_raw.txt and
B/work/cost/ret_cost_tokens.md.
- Sessions (lead transcripts under ~/.claude/projects/-home-kiros-li-Documents-GitHub-PropExperiment/): 1
  3d79635b-4dfe-4992-b743-c48717efe7fc, 2 7e35d21b-f567-499d-aaa7-6117610c9a16, 3 3860d0d1-cf19-46b3-a4da-6fda65b58c32,
  4 0d036ce2-d1e2-4d45-9a12-484b421ab30e (the current one, still running). For each: the main <id>.jsonl plus
  <id>/subagents/**/*.jsonl. Check whether a session's transcript also holds usage from before the stage (the stage
  launched about 22:15 PDT 2026-10-28 = 05:15 UTC 2026-10-29; reports/stage_e32b_STATE.md's first task rows give the
  exact start) and slice by time if so; say what you found. Memory note: a resumed session's usage stays in the first
  session's .jsonl; check whether any of the four is a resume of another.
- Output tables: (1) tokens per model (input, output, cache read, cache creation, total) for the whole stage; (2) one
  line per worker spawn: role name (the Agent description, e.g. ScoreFixer-OpusHigh; take it from the subagent's meta
  file or its first prompt's "You are <Name>" line), agent file (worker-medium/high/xhigh/max), model from the
  transcript's message.model (state every distinct model seen), first and last timestamp in PDT (America/Vancouver),
  tokens by field and total; (3) per session: lead tokens, worker tokens, wall-clock first-last; (4) delegation share:
  lead vs workers, and by model tier. Times in PDT. Token counts only, never estimated: if a transcript cannot be read,
  say so in the output.
- Test it now with a provisional end time (now) and report the tables' row counts and per-model totals (not the full
  tables) in your summary. Never print or log any key; do not read .env.
Write only B/work/cost/. Read-only on everything else. Report: B/work/cost/README.md (usage, what it reads, findings).

### F3 addendum (lead, 08:58, after F1 and F2 returned)
- R1Fixer's verified corrections to RV2's wording (work/fix4/r1/r1fix_report.md): E.12's extra G17 lead was MBT only
  (g17_mes excluded by rule P-1a, stage_e12_rulings.md:49; MBT's store starts 2024-01-02, live two months of the
  window); E.12 Family B is one ridge per horizon pooled across products. Live leads: RTY/M2K ZN, 6E, CL, GC, ZC; ZL NQ,
  ZN, 6E, CL, GC. E.20 decision times for equity 09:00, 11:00, 13:00 and t4 14:08 CT. Use these, not RV2's text.
- Its step-5 list for the recommendations file is lines 46, 50, 465, 485, 568, 580, 582-583; for draft_sections.md
  lines 187, 207, 304, 316, 318-319. Lead ruling on recommendations:485 / draft:207 ("ZL in other families' closed
  lines: R1-08 CP ports (ZL F01 gated at Q3 0), R1-11, R1-13, R1-15, R1-16"): under LR-Q3b split it into "same family
  for F09 at a neighbouring horizon (LR-Q3b): R1-11, R1-15 (G17 leads NQ, ZN, 6E, CL, GC at h60-hF)" and "other
  families: R1-08 CP ports (ZL F01 gated at Q3 0), R1-13, R1-16; for F10 also R1-11 and R1-15 (no order-book
  features in either library)".
- Score output: the R2 files and recommendations:880 record the 05:40:30 run's hash (70809d50...); the score was rerun
  at 08:51:03 for RV1 S1/S3 (B/score32b_out.json ee74c6a0...; run2 kept as B/work/score/score32b_out_run2.json) with no
  score, gate or rank change (work/fix4/score/score_fix_report.md). Section 8 states both hashes and that R2 took only
  the top-15 list from the score output, identical in both runs.

### F4 addendum (lead, 09:23)
- After F3, the lead changed its own text by work/R4/fix_lead_text_s4.py (6 exact replacements, applied to
  work/R4/lead_sections.md and reports/stage_e32b_recommendations.md; pre-edit copies work/R4/lead_sections_s4a.md and
  work/fix4/recs/recommendations_pre_s4fix.md) and corrected patch_v31_q3_lead.py's docstring (no code change). Check
  those six statements against the files too: E.12's MBT lead; MNQ "read by E.16, E.20, E.21, C1b and E.23" (from
  B/F2_data_access.json or the R2 data fields); the 2024-03..2025-03 (about 273 dates) and 2026-06-17-onward stretches.
- The RecsAssembler's numbers to check: the EQ3 pool cut to MNQ + RTY under LR-V31 (K_eff 1,160, q 0.168) and its
  pooled-power interpolation behind "far below 80% even pooled"; its build scripts are in B/work/fix4/recs/scripts/
  (spot-check them, do not trust them). SR80.json is at B/work/F5/SR80.json.
