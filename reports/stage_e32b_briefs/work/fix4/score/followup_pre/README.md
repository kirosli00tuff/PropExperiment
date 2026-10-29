# Stage E.32b scoring scripts (ScoreCoder, 2026-10-28)

Spec: reports/stage_e32b_ranking_spec.md, sha256 09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635.
Both scripts refuse to run on any other hash. Inputs and fields: SCHEMA.md. Nothing here has been run on real facts.

## Run

    # tests (159, synthetic only)
    uv run pytest -q reports/stage_e32b_briefs/work/score/
    # dry run on the synthetic fixture -> fixture_out.json, fixture_out.md, fixture/*.json
    uv run python reports/stage_e32b_briefs/work/score/dry_run.py
    # wave C, once the real files exist (B = reports/stage_e32b_briefs)
    uv run python reports/stage_e32b_briefs/work/score/score32b.py --f3 B/F3_vol.json \
        --f4 B/F4_facts_unmasked.json --blind B/F4_blind_unmasked.json --econ B/econ32b.json \
        --attention B/F2_attention.json --data-access B/F2_data_access.json [--rulings <rulings.json>] \
        --out <out.json> --md <out.md>
    uv run python reports/stage_e32b_briefs/work/score/r3_score.py --combos <combinations.json> --out <out.json>

Exit code 2 with "REFUSED: ..." on a spec-hash mismatch or a contract break (missing code, missing econ block for a
rankable pair, bad value). Soft findings go to `input_checks`; cases the spec does not settle go to `for_lead`.
E.28's v2 order is read from reports/stage_e28_briefs/A3_ranking_table.json (read-only; `--no-e28` skips it).
The run takes about a second; no flock needed.

## Files

| file | content |
|---|---|
| s32b_common.py | spec hash check, exact numbers (Fraction from decimal text), band helpers, half-up rounding, Params and the declared variants, blind-rating unknown rules and spec 1 evidence caps, patches |
| s32b_layer1.py | spec 3: D1 to D6, the gate, L1 |
| s32b_layer2.py | spec 4: E, R, A, D, Rel, P, the Layer 2 gates, L2, S |
| score32b.py | validation, spec 5 ranking, ties, top 15, variants, the lead-ruling hook, moves against E.28, JSON and md output, CLI |
| r3_score.py | spec 8.3: Q4 to Q7, K_eff, C, ties, R4 |
| make_fixture.py, dry_run.py | the synthetic fixture and the dry run |
| conftest.py, test_*.py | tests |

## Spec clause per function

| spec | function |
|---|---|
| 3 D1 bands, r_5 r_15 r_OC | s32b_layer1.d1_band, d1_score, Layer1.row (r for all horizons) |
| 3 gate, arithmetic string | s32b_layer1.sigma_gate; D4 = 0 and the D1 unknown-sigma reason in Layer1.row |
| 3 D2 a b (blind), satellite uses leader | s32b_common.blind_rated; Layer1.row (facts_of = leader for Sat i or ii) |
| 3 D2 c | Layer1.notional, Layer1.family_c (NQ included) |
| 3 D2 d terciles | s32b_layer1.attention_count, attention_tiers, code_attention |
| 3 D3 | Layer1.row with s32b_common.cap_s12 |
| 3 D4 L, J, Sat (i) (ii) (iii) | s32b_layer1.l_score, j_score; Layer1.adv_ratio, larger_size, sat, leader |
| 3 D5 h k o p | s32b_layer1.d5_h, d5_k, d5_o, d5_p |
| 3 D6, satellite takes leader's evidence | Layer1.row with s32b_common.cap_extreme_0_4 |
| 3 L1, L1 < 2.00 flag, L1min2 | s32b_layer1.W_L1, below_l1_min |
| 4 E | s32b_layer2.e_score |
| 4 R, A (blind), A = 0 gate | s32b_layer2.pair_row |
| 4 D | s32b_layer2.d_score, room_band |
| 4 Rel, P | s32b_layer2.rel_score, p_score |
| 4 Layer 2 gates, L2, 5 S | s32b_layer2.pair_row |
| 5 ties and order | score32b.rank_key, find_ties, s32b_common.round2 |
| 5 variants | s32b_common.DECLARED_VARIANTS, Params; score32b.run_all, variant_summary |
| 5 lead-ruling variants | score32b.run_all (rulings), s32b_common.apply_patches, params_from |
| 5 moves against E.28 v2 | score32b.moves_vs_e28 |
| 6 refuse on hash | s32b_common.check_spec, check_doc_hash |
| 8.3 Q4, Q5, Q6, Q7 | r3_score.q4_score, q5_score, q6_prop, q6_own, q7_score |
| 8.3 pools | r3_score.pool_rho, k_eff; combo_row (worst member Q6) |
| 8.3 C, ties, R4 | r3_score.combo_row, rank_key, find_ties, r4_select |

## Interpretation points for the lead (each is one place in the code)

1. Sat (i) "at least 5 times": implemented as written (ratio = 5 holds), `SAT_RATIO` with `>=` in Layer1.sat. This
   is the one script threshold where the written inequality sends the boundary to the lower score. A ratio of
   exactly 5 is unlikely with real ADVs. Changing `>=` to `>` would apply "boundary to the higher score" instead.
2. D2 d "equal counts take the higher tier": the top tier (d = 1, the larger deduction), as written. When the number
   of underlyings with a count is not a multiple of 3: top if k < n/3, middle if k < 2n/3 (upper tiers take the
   extra places).
3. D6 "a satellite takes its leader's evidence": satellites by rule (i) or (ii), as D2 defines them ("its direction
   is set there"); rule (iii) does not switch D6 to the leader. D2_own leaves D6 unchanged.
4. D2 c with an unknown notional (no F3 median close: expected for SI, SIL, MET, ETH and the micro yields): a code
   borrows a same-price sibling's close; otherwise c is computed among codes with a known notional, marked
   provisional and listed for the lead (metals, crypto and rates families). A ruling patch of F3 median_close can
   settle it.
5. Sat (i) when both the ADV ratio and the relative contract size are unknown (non-same-price siblings without
   closes, for example a micro yield and its Treasury future): counted as holding (lead). These codes fail the gate
   on unknown sigma anyway.
6. A D1 horizon other than 60 with unknown sigma while sigma_60 is known: the gate fails, under D1's "Unknown sigma:
   the contract fails the Layer 1 gate" (lead).
7. spread1 sets S = 1 for c_RT, the gate and D4 L's spread test (1 is never above 1), and takes E from the spread1
   econ block. E_dir60 and spread1 take m* and cost per attempt for the tie chain from their own econ block.
8. OC1_off: OC1 codes get no transferred statistic at all (gate fails; J becomes 1 (u)); only the gate affects ranks.
9. Unknown ADV: L = 1 (u), but a sourced wide spread or thin touch can still make L = 2.
10. Unknown 50K listing or BC acceptance: excluded (gate). Unknown DLL or MLL: that D band 1. Unknown Rel deduction:
    0 (E.28 practice). Unknown P items: deduction (E.28 rubric). Unsourced Sat (ii): does not count.
11. The leader is computed from USD-notional ADV; F4's `leader` is used only when that is not computable, and a
    disagreement uses the computed leader (lead note).
12. r3: a pool's Q4 and G(h_c) are its worst member's (the spec names the worst member only for Q6); a pool is
    excluded if any member's core trades are prohibited; unknown Q6 and Q7 inputs deduct; the default asset class
    is the E.28 family (crude and natgas count as different classes unless the file sets `asset_class`); R4 is
    computed over all venues as written, and `R4_prop_only` is reported beside it.
13. The BlindScorer must rate NQ's D2 a, D2 b and D6 (MNQ is NQ's satellite) although NQ is never scored.
14. docs/DECISIONS.md records no own-account capital ceiling (grep, 2026-10-28), so r3 uses USD 6,000 (u) unless the
    combinations file supplies one.
