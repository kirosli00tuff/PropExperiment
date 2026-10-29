# Stage E.32b review briefs (Step 4 and R5; written by the lead 2026-10-29 ~06:55 PDT)

Two independent reviewers, Fable xhigh, read-only, each with its own scope. Common rules: briefs/brief_wave_b.md
"Common rules" (no edits outside your output paths, no market data except RV1's item 5, no web, no git changes, no
agents). You did not produce any of the files you check. Recompute with your own scripts (in your own work folder),
not by rerunning the stage's scripts alone. Label every finding BLOCKING (a wrong number or rule application that
changes a scored value, a rank, an R4 candidate or a stated conclusion; a blinding breach that touches a rating used;
any outcome read), SHOULD FIX (a wrong statement or a rule application that changes no rank, an unclear or unsupported
claim) or NOTE. Each finding: the file and line or field, what is wrong, the evidence (a quote or your recomputation),
and the fix. The frozen spec: reports/stage_e32b_ranking_spec.md (sha256 09ebe697...8635); all lead rulings are in
briefs/RULINGS.md and reports/stage_e32b_STATE.md (sessions 1-3).

## RV1 RankingReviewer-FableXHigh: Step 4 (the ranking)

Inputs: spec sections 0-6; briefs/F3_vol.json/.md and work/F3/ (code, files-opened log, holdout and seal checks);
F4_facts_unmasked.json, F4_corrections.json, F4_facts.md, F4_audit.md (the FactAuditor's audit and re-check);
F4_masked_contracts.json, F4_masked_firms.json, F4_mask_key.json, F4_masks_FINAL*.txt, work/facts/ (mask_patch.py,
mask_patch2_lead.py, leak checks); F4_blind_ratings_masked.json/.md, F4_blind_unmasked.json, work/blind_rater1/;
econ32b.json, econ32b_smean.json, work/econ/ (README, REGRESSION.md, run_real.log); work/F5run/F2_attention_listcodes.json
and F2_attention.json; F2_data_access.json; work/score/ (score32b.py and its modules, lead_variants.json); briefs/
score32b_out.json/.md; reports/stage_e32b_ranking.md.
Checks:
1. Recompute every Layer 1 score (D1 with its horizon bands from F3 and S, D2 a-d, D3, D4 L, J and Sat, D5, D6 with
   the satellite and evidence-cap rules, the gates with their arithmetic lines) and every Layer 2 score (E from the
   econ blocks, R, A, D, Rel, P), S, the ties and the ranks, for all 47 codes and every listed pair; compare with
   score32b_out.json; recompute the top 5 of at least six variants (including RL-KZM, RS-MNQD6, E_dir60, OC1_off).
2. Blinding: the masked sheets against the key; the leak history (audit B1, B2 and the patches, FINAL3); whether any
   rating used was made by a rater exposed to a leak (rater 1 is superseded; rater 2 rated FINAL3); residual
   identifiability; the inter-rater comparison (302/329).
3. Unknown rules: every unknown and its rule (spec 1, 3, 4; SCHEMA.md section 3; LR-SC; LR-DLL).
4. Facts behind the scores on a sample of at least 15 codes and 10 pairs: S and touch under LR-S, settles_off_sibling,
   ADV and notional, fees (RR-05), DLL/MLL, data_access (FT-1 conversion); the LR-S1e HG erratum's "no score effect".
5. F3: the volatility arithmetic (sigma_h, m_h, OC, overnight, R_d, median close, OC-1 factors); the window
   discipline (only the 12 allowed monthly files 2022-11..2023-10; the refusal rules; nothing sealed or spent opened;
   the holdout and E.32 seal checks before and after). You may rerun work/F3's script for at most 3 roots through its
   own allow-list, with `uv run python -m data.holdout status`, soy_test_seal.py status and guard33.py dry-check before
   and after (save the outputs in your folder); nothing else touches market data.
6. Economics: E's formula and grid rule on a sample of pairs; that econ32b.json's inputs match F4 (fees, S, tick
   values, DLL/MLL); the regression against E.28; the S_mean run's inputs.
7. reports/stage_e32b_ranking.md: every number and claim against score32b_out.json.
Output: briefs/REVIEW_ranking.md (verdict line, then findings), helpers in briefs/work/rv1/.

## RV2 RecsReviewer-FableXHigh: R5 (step 3b) and the holding scope (F5)

Inputs: spec sections 7-9; briefs/R1_closed_lines.md/.json (and its sources: reports/stage_e23_briefs/inventory/,
ledger/trial_registrations.jsonl, the frozen member code under strategy/members/ where a closed line's rule matters);
R2_idea_families.md/.json; work/R2/ (groundwork, build_combos.py, merge_q.py, patch_q6p_lead.py,
patch_v31_q3_lead.py, the v1 files); R2_dossiers.md (with the lead errata at its top), R2_dossiers_for_rating.md,
R2_Q_ratings.json/.md, R2_combinations*.json, r3_out.json and work/R2/r3_out_*.json; work/score/r3_score.py;
work/R4/draft_sections.md and work/R4/lead_sections.md, reports/stage_e32b_recommendations.md if it exists;
F5_holding.json/.md, work/F5/ (code, SR80.json), reports/stage_e32b_holding_scope.md; reports/E.29_RETURN.md,
E.31_RETURN.md, E.33c_RETURN.md (sections 1 and 7).
Checks:
1. Closed lines: R1 complete and sourced; for every R4 candidate and the next ten combinations by C, check against the
   frozen member code and the E.23 inventory (not R1's summaries alone) whether it re-tests or closely varies a closed
   configuration (the lead corrected F01 on YM, MYM and RTY at 06:47: LR-Q3a; look for others the same way); the
   LR-R1, LR-V31 and LR-ZLW readings against the decision texts (V31, V38, V45, V50, V51, V56).
2. R3 arithmetic: recompute Q4-Q7 and C for the R4 candidates and the next ten from their inputs (c_f, sigma_hc,
   K_test, K_eff, payout thresholds under LR-Q6p, news windows, data costs, clean test windows) and check those
   inputs against F5, F4 and F2_data_access; the pools' K_eff; the ties; the sensitivities (v1, q3only, nozlw,
   topstep150).
3. Q1-Q3: spot-check at least 15 ratings against the dossiers' evidence rows and the scales (spec 8.3).
4. R4: the realism of each prior (base rates, the arithmetic), the kill criteria, the stop rule's coherence, the
   non-prop paragraph, the decisions for the user; that no outcome was read anywhere (no strategy return computed,
   F3 statistics only, no sealed or spent window opened).
5. F5 and the holding scope: recompute the band rule and the prior verdict for at least 3 top pairs and 2 own-broker
   rows from F3, F4 and SR80.json; check the scope file's statements (the 15-60 minute finding; "hours not
   supported"; overnight; the E_dir placeholder or table).
Output: briefs/REVIEW_recs.md (verdict line, then findings), helpers in briefs/work/rv2/.
