# RV1 review of Step 4 (the ranking), Stage E.32b

RankingReviewer-FableXHigh (claude-fable-5-1), 2026-10-29 06:58-07:25 PDT. Read-only on every stage file; helpers and
outputs in reports/stage_e32b_briefs/work/rv1/ (recompute.py, check_rankmd.py, recomp_*.json, variants_*.txt,
f3copy/, guard_before.txt, guard_after.txt, f3_rerun.log). Spec checked: reports/stage_e32b_ranking_spec.md sha256
09ebe697...8635 (matches). Inputs as the 05:40:30 PDT score run recorded them (F3 9ba14d56, F4 4a4d1e29, blind aeae3296,
econ 0567890e, attention 7ae497c0, data_access 4bad06bd, lead_variants 6d32a1fd): every sha256 re-hashed and equal.

**Verdict: PASS with 3 SHOULD FIX and 13 NOTE; no BLOCKING.** Every Layer 1 score, gate, Layer 2 score, S, tie, rank and
all 28 variants' top 5 and MNQ ranks were recomputed from the spec text with an independent script (exact fractions) and
match score32b_out.json exactly; the blind ratings used are rater 2's on the FINAL3 sheets; the F3 statistics reproduce
byte-for-byte on three reran roots inside the window discipline; econ32b.json's inputs match F3 and F4 for every pair;
reports/stage_e32b_ranking.md matches the score run in every table cell but one rounding of a descriptive mean.

## BLOCKING

None.

## SHOULD FIX

- **S1. Tie-break cost per attempt uses the limit-case value, against the lead's ruling.** reports/stage_e32b_STATE.md
  (session 3, EconSetup flags ruled): "cost per attempt in the tie-break = the market-case value (spec 4 says E.28's
  definitions, market case; the limit-case value is reported beside)". The econ block field `cost_per_attempt` is, per
  work/econ/README.md item 1, "E.28's definition (d = -F_rt / v)", the limit case; the market-case value is
  `cost_per_attempt_mkt_mu0`. work/score/s32b_layer2.py line 43 reads `block.get("cost_per_attempt")`, and every ranked
  pair's `cost_per_attempt` in score32b_out.json equals the econ limit-case field (103/103). Evidence: topstep|YM
  49.706 (limit) vs 49.029 (market); topstep|M6A 202.80 vs 98.82. Rank effect: none. The only two ties the cost level
  decides (tradeify|M6A over topstep|M6A at ranks 94/95; tradeify|M6E over topstep|M6E at 101/102) keep their order
  under either field (95.83 < 98.82 and 95.83 < 98.35). Also affected: the "cost/attempt USD" column of
  stage_e32b_ranking.md table 3a (shows the limit-case numbers, e.g. Topstep YM 49.71, Topstep MNQ 165). Fix: read
  `cost_per_attempt_mkt_mu0` in the scorer (or amend the ruling to the limit case) and relabel the 3a column.
- **S2. stage_e32b_ranking.md section 1 ("Unknown rules applied") states a false generalisation:** "no code with an
  unknown notional can hold its family's largest notional ADV, so the provisional values stand". In crypto, ETH's
  notional is unknown only because F3 has no ETH close (spec 2.4); from F4, ETH ADV 19,000 x multiplier 50 = 950,000
  ETH per day against MBT 6,678 x 0.1 = 668 BTC per day, so ETH's USD notional exceeds MBT's unless one ETH is worth
  less than 1/1,422 of one BTC. ETH very probably holds the family's largest notional ADV. No rank effect: every crypto
  code has D2 c = 0 in the run (MBT and BTC because their facts_of BTC has an unknown notional), and ETH and MET fail the
  Layer 1 gate (sigma unknown). The sentence is right where c = 1 was given with a provisional flag (GC: SI 64,000 x
  5,000 oz is about a quarter of GC's 160,118 x 100 oz x price; CL against QM; ZC/ZS/ZW/ZL/ZM against micros with
  unknown ADV; ZN against the micro yields). Fix: say that no code with a KNOWN notional loses c = 1 to an unknown one
  in metals, crude, grains or rates, and that crypto's c is 0 throughout and undetermined (ETH likely largest).
- **S3. Two econ pairs' thresholds come from a failed bisection, and nothing downstream surfaces it.** econ32b.json
  pairs bulenox|CL and bulenox|NG, blocks primary and spread1: `search.mu_star_mkt.k_bisection: null, confirmed:
  false, violations: [176, 177, 178, ...], n_checked: 1339` and the same for mu10K (violations from 244). By
  work/econ/econ32b_core.py `confirm()` lines 152-157, the recorded value is then the smallest grid k with f >= 0 after a
  dense fill (k_final), so mu* = 1.76 and mu10K = 2.44 are the full-grid thresholds (f(1.75) = -80.1 < 0, f(1.76) =
  +94.3; f(2.43) < 0, f(2.44) > 0) and equal E.28's values for these pairs (REGRESSION.md: bulenox|CL 1.76 / 1.44 + 1).
  E for both pairs (3.285, 3.269; ranks 27, 28) is therefore right. But the scorer's validation (SCHEMA.md 4) does not
  look at `confirmed`, run_real.log only prints the values, README line 184 says "none unconfirmed" (of the regression),
  and the ranking report does not mention it. Fix: state the two corrected searches in the econ notes and the report,
  and have score32b.py list `confirmed: false` blocks in `input_checks`.

## NOTE

- N1. stage_e32b_ranking.md section 4: "The ranked-pair means are ... D3 3.51"; the mean of D3 over the 103 ranked
  pairs is 3.5049 (3.50). The gains/losses column itself matches at 3 decimals for all 15 rows (the writer used the
  exact mean there); only the printed summary is off by a rounding.
- N2. stage_e32b_ranking.md line 15 prints econ32b.json's hash as "05678907..."; the file's sha256 begins 0567890e5a.
- N3. moves_vs_e28 `moved_by` lists mix two effects: each criterion's entry is (new weight x new score - E.28 weight x
  E.28 score)/2, so R (weight 0.10 -> 0.15) and D (0.10 -> 0.15) appear as movers when their values did not change: 168
  of the 216 R and D entries in `moved_by` are pure re-weighting (value unchanged). The contributions sum exactly to
  S_here - S_e28 (108/108 rows) and section 5's text states the definition, but the column heading "moved up by" reads
  as criterion movement. Consider a "(reweight)" tag or a separate column.
- N4. score32b_out.json `input_checks` holds 47 findings "data access X.o_owned_36m: F4 False != F2_data_access 1": a
  boolean (F4) against a 0/1 score (F2) with no conversion. All 47 are consistent under FT-1 (o_owned_36m = (F2 o == 0),
  p_all_read = (F2 p == 1)); re-derived for all 47 codes, 0 real disagreements. The report says so (section 1).
- N5. HG: the frozen F4 and the score run's Layer 1 record carry `S_sourced: true`; LR-S1e makes it 1 (u)
  (F4_corrections.json). Verified no score effect: S = 1 either way, so c_RT, the gate threshold, D4 L's spread test
  (1 is not above 1) and econ S_rt (1.0 for all three HG pairs; only `S_rt_status` would change) are identical;
  spread1 is a no-op for every code.
- N6. Residual identifiability of the masked sheets is at the product level by design: the kept underlying words
  (rater 2's reasons mention "Dow" 117 times, gold 21, silver 22, copper 14, Treasury 19, soybean 16, corn 6, wheat 5,
  WTI 3), exchange names, filing numbers and program dates (F4_audit.md N5) let a reader name most contracts; the label
  hides the code, not the product (spec 6 and the lead's ruling accept this, as E.28 did). No universe code, no firm
  name and no platform name appears in rater 2's 819 reasons (word-boundary grep, 0 hits for all 47 codes and the 5
  firms).
- N7. Rater 1 was exposed to the B1 leak: its helpers work/blind_rater1/helpers/firm.py (01:51) and pairsum.py (01:52)
  read F4_masked_firms.json of the FINAL set (Lucid plan names). Its ratings enter nothing but the inter-rater
  comparison; recomputed: 302/329 exact (D2a, D2b, s1, s3, sat_iii 47/47; s2 44/47 (MCL, QM, CL 1 vs 2); D6 23/47: 17
  at 4 vs 3 (GC M2K MGC MNG MNQ MYM NG NQ QG RTY SI SIL YM ZB ZF ZN ZT), 5 at 0 vs 2 (6E CL HG ZL ZW), ZM 0 vs 3, MZM 2
  vs 3), matching the report's section 7 lists.
- N8. Rater 2 rated FINAL3: F4_masks_FINAL3.txt 03:28:21 (contracts 580dae9d = file, firms 24e2a3d2 = file, key
  c017866f = file); the three sheets' mtimes 03:19:13, 03:27:00 and 03:27:20 precede the launch (~03:28:30 per STATE) and
  rater 2's first helper output (work/blind2/d2a.txt 03:29:58); F4_blind_unmasked.json's inputs are rater 2's file
  (ce1bf831) and the FINAL3 key. The 9-second margin between FINAL3 and the launch is thin but the file times settle it.
- N9. Evidence cap (spec 1): checked every extreme rating (D6 >= 3 or 0, s1 or s2 = 2) of all 47 codes against the
  `verified` field of each cited item in F4_masked_contracts.json (through the key): none rests only on abstract or
  snippet items; the two D6 = 4 (BTC, MBT) each cite four full-text items. The rater's "unverified: none" stands.
- N10. Sat (i) for SIL, SI and ETH: the script computes the notional ratio from ADV x multiplier when the siblings share
  a price (the close cancels), so SIL/SI (4.32x) and MET/ETH (66x) are decided without a close; my first pass (both
  unknown -> holds) differed for SIL only, and the script's reading is the right one. All three fail the gate anyway.
- N11. The spec 5 tie rule puts 15 adjacent pairs below a pair with a lower unrounded S (30 ranks move, all inside
  2-decimal ties, e.g. lucid|MYM 2.8663 at 17 over bulenox|MNQ 2.8690 at 18 by m*). By design; the report says so.
- N12. F3 sanity: sigma_60 / (sigma_1 sqrt 60) is 0.81-0.99 for the 22 owned roots (ZN 0.81, ZB 0.83; the rest 0.87+),
  consistent with mild 1-minute mean reversion; L_main 390 (06:30-13:00 PT), 290 for grains (06:30-11:20 PT).
- N13. E_dir60 top 5: rank 3 tradeify|MNQ S 3.04605 sits above rank 4 tradeify|YM 3.04639 (both 3.05, m* decides); the
  report's variant table shows "3.046" for both without saying which rule ordered them. Harmless.

## Check 1. Recomputation (work/rv1/recompute.py, Fractions from the JSON text)

- Primary: 46 scored codes (NQ excluded) and 235 pairs. D1 (bands at 30/60/120/240), D2 a-d (d terciles: 18 underlyings,
  6/6/6; top crude 169, Treasuries 91, gold 57, bitcoin 36, Nasdaq 31, natgas 29), D3 (with caps), D4 L/J/Sat (i, ii,
  iii), D5 h/k/o/p, D6 (satellite by i/ii takes the leader's), the gate strings, L1; E from the econ blocks, R, A, D
  (room_a with the MLL where DLL is "none", LR-DLL), Rel, P, L2, S, S_rounded, the 21 tie groups and all 103 ranks:
  0 mismatches (the only differences are the 5 NQ pairs, which the run leaves unscored, and N10). Survivors 35 and
  L1_below_2 (M6E, MZC, MZL, MZM, MZS, MZW, QG, QM) equal. MNQ ranks 2/3/8/12/18 equal.
- Variants: all 10 declared (slip0, slip1, mad, D1_all, E_dir60, OC1_off, sat1, D2_own, L1min2, spread1) and all 18
  lead/rater variants (RL-SMEAN, RL-KZM, RL-PBRIEF, RL-TRECENT, RS-D6SPAN, RS-D6THRESH, RS-D6CRYPTO, RS-D2BIIP,
  RS-MNQD6, RS-OWNONLY, RS-EQS2, RS-MFFUR, RS-CRYPTOR, RS-ATOP2, RS-A3P, RS-ATRAD1, RS-RELTOP0, RS-RELTRAD1), applying
  each ruling's patches myself: top 5 (pairs, order, S), MNQ ranks, n_ranked and survivors all equal the run's
  (work/rv1/variants_declared.txt, variants_lead.txt, variants_lead2.txt).
- moves_vs_e28: 116 rows = pairs ranked in either run; rank_e28 and S_e28 equal A3_ranking_table.json (variant
  primary) for all; rank_here equal; contributions follow the stated definition and sum to the S change (108/108);
  the 10 pairs ranked in neither run are the ones the report names. E.28's top five (QM at five firms) fail here on
  D4 = 0 (L 1 (u), J 1: 227.81 ticks x 12.5 = 2,847.6 USD, Sat 1 by rules i and ii).

## Check 2. Blinding

Masked sheets equal FINAL3 by hash; rater 2 rated FINAL3 (N8); rater 1 superseded and exposed (N7); no rating used
comes from an exposed rater. Leak history read: FINAL (B1 Lucid plan names in 4 items of V-PCDG, FactAuditor) ->
mask_patch.py (20 + 22 substitutions, S2 IIP quotes, S3 sizes/ticks) -> FINAL2 (B2 "MyFunded Futures" one-space
spelling) -> mask_patch2_lead.py (8 exact replacements) -> FINAL3; leak_v2_out_final3.txt 0 unjustified of 138 hits;
leak_audit_out3.txt substring mode: labels sheet == key, 47/5/235 one-to-one, no E.28 label overlap. Residual
identifiability: N6. Evidence caps: N9. Inter-rater: N7 (302/329 confirmed).

## Check 3. Unknown rules (spec 1, 3, 4; SCHEMA.md 3; LR-SC; LR-DLL)

Every "u" in the run re-derived and matched to its spec clause: S = 1 (u) 33 codes (46 scored - 13 sourced; HG's is
sourced in F4, N5); Sat (iii) unknown -> 0 for 18; D5 k price unknown -> 1 for 14; Sat (i) larger sibling with unknown
ratio -> holds for 8 codes (11 entries: MZC, MZS, MZW carry two); D4 J unknown -> 1 for 8 (all sigma-unknown); D4 L ADV
unknown -> 1 for 7; D2 a unknown -> 1 for MET, ETH, MBT, BTC (rater unknown, rule 1); D5 h unknown -> 1 for SI; D2 b
unknown (MZC, MZS, MZW, MZL, MZM) not reached (their facts_of is the leader); D room bands 1 (u) for 40 pairs, all on
gate-failed codes; pairs: P rate limit unknown -> deduction 184 (77 ranked), VPS unknown 138 (57 ranked), Rel payout
unknown -> 0 (lead) 77 ranked; R and A unknown: none. LR-DLL: Topstep and Bulenox DLL "none" -> MLL in room_a (checked
bulenox|YM 2500 / (166.2 x 5) = 3.008). LR-SC readings 6 and 7: no code has a known sigma_60 with another D1 horizon
unknown; spread1 takes the spread1 econ block (identical to primary since S = 1 everywhere). D2 c provisional for 34
codes: see S2.

## Check 4. Facts behind the scores (sample)

- ADV, tick_size, tick_value, multiplier for 20 codes (MCL CL NG MNG QG GC MGC HG 6E 6A MBT RTY YM MNQ ZN ZC ZS ZL ZM
  XC) against reports/stage_e28_briefs/A3_facts.json: all equal (grain ticks: A1 cents -> F4 USD, correct).
- Fees for 12 pairs: topstep|YM 3.78, topstep|MNQ 1.22, topstep|RTY 3.78, tradeify|MNQ 1.82, tradeify|YM 5.76 equal
  A2_firm_*.json fee_rt; bulenox|YM 4.18, bulenox|RTY 4.18, bulenox|ZL 5.72, mffu|YM 5.76, mffu|MNQ 1.90 equal the A2
  rate-table quotes; Lucid RR-05: lucid|MYM 1.90 = max(1.22, 1.82, 1.90, 1.22), lucid|SIL 2.84 = max(2.72, 2.84) (below
  Lucid's own 3.20 commission, FactAuditor S4, left as ruled; SIL fails the gate).
- DLL/MLL/BC for the 5 firms against F2_firms.json: Topstep DLL optional -> "none", MLL 2000; Lucid 1200/2000;
  Tradeify 1250/2000; MFFU 1000/2000; Bulenox option 1 null -> "none", MLL 2500; BC true for all five.
- Data access (FT-1): all 47 codes' mbo_start, k_usd_month, o_owned_36m = (F2 o == 0), p_all_read = (F2 p == 1) equal.
- Spread S under LR-S: the 13 sourced values (CL, QG, NG, GC, SI, HG, 6E, 6A, ZF, ZN, ZB, ZC, ZS) carry a clause (i),
  (ii) or (iii) and a figure that satisfies it as stated (6A median 1 (i); means below 1.5 (ii) for CL 1.27-1.29, QG
  1.22, NG 1.25, GC 1.31-1.35, 6E 1.2, ZC 1.26, ZS 1.04-1.12; one-tick statements (iii) for SI, ZF, ZN, ZB); HG's (ii)
  is the erratum (N5). Touch: 5 sourced medians (MNG 3, QG 10, NG 5, GC 4.62, SI 6.56); GC 4.62 and MNG 3 are the only
  two below 5 and set L = 1 for those codes (FT-2 accepted; RL-TRECENT identical top 5). settles_off_sibling: 10 true
  with a settlement item each (MCL, QM -> CL; MNG, QG -> NG; MHG -> HG; MZC, MZS, MZW, MZL, MZM -> their full-size
  grain). Notional: YM 163,416 x 5 x 33,825 = 27.6 B vs MYM 1.94 B (14.2x); NQ/MNQ 3.86x (MNQ not a satellite).

## Check 5. F3

- Arithmetic (work/F3/f3_core.py read against spec 2.3): D_h over main-session grid minutes with t + h in the same
  trade date's main session and the same instrument_id at both ends; sigma = SD ddof 1, m = mean |D|, median and p99 of
  |D|, counts; OC = last minus first main close per date, same instrument; cc and on between consecutive sample dates
  (LR-F3); R_d = full trade-date high minus low of the last bar's instrument, median and p99; main-range median;
  median_close = median of each day's last main close x price factor; OC-1 = sibling statistics x (sibling tick / own
  tick), counts and close unscaled. All 17 OC1 factors equal sibling_tick / own_tick; the scaled statistics of QM (0.4),
  XC (2.0), MZC (0.5) and M6E (0.5) reproduce exactly from their sources.
- Rerun (allowed, 3 roots): guard checks before (07:10:41) and after (07:10:54), both all_ok True, unlocks_logged 0
  (top, holdout_2, MCL, MGC, MHG, NG), soy test seal sealed 114/114, guard33 dry-check 4 of 4 refused (work/rv1/
  guard_before.txt, guard_after.txt). f3_vol.py (byte-identical copy except the REPO path line; f3_guard.py and
  f3_core.py identical by sha256) run for MCL, 6E, ZC into work/rv1/f3copy/: 36 opens, 0 refusals, 186 MB peak; the
  three parts equal work/F3/parts/*.json and F3_vol.json in every field (0 differences; n_dates 250/257/250, L_main
  390/390/290, early halts excluded 8/2/1).
- Window discipline: work/F3/opens.log 264 OPEN lines (22 owned roots x 12 months: 252 in the run plus the 12-file ZC
  time probe), 0 REFUSED, every path one of the 12 allowed months 2022-11..2023-10, no forbidden token; the resolved
  paths (under /mnt/large-storage/..., a symlink target) are what the guard checks. Refusal dry test on my copy
  (check() only, nothing opened): the March 2024 embargo month, the months before and after the window, root ES, the
  ZM 2019 seal window, an mbo path and a holdout path all refused; an in-window MCL path allowed; opened = [].
  work/F3/holdout_before.txt and holdout_after.txt (23:13:18 and 23:14:50) show the same all-OK status around the run.

## Check 6. Economics

- E = 0.75 s(m*; 0.20) + 0.25 s(m10K; 0.30) with above-cap components 0: recomputed for all 103 ranked pairs, equal.
- econ32b.json inputs against F3 and F4 for all 112 computed pairs and all 3 blocks: sigma_1, sigma_60, L_main, F_rt
  (= F4 fee_rt_usd), v (= tick_value_usd), S_rt (sourced S or 1 (u)), grid cap = max(4, ceil(0.30 sigma_60)) on every
  block, T = 20 and sigma_T = sigma_1 (primary, spread1), T = min(20, floor(L_main / 60)) and sigma_T = sigma_60
  (E_dir60), c_mkt = F_rt / v + S_rt, m* = mu* / sigma_60, m10K = mu10K / sigma_60, value = k x 0.01, f(k) >= 0 and
  f(k - 1) < 0: 0 mismatches apart from S3; 86 above-cap components. not_computed 123 = 109 unlisted + 9 sigma unknown
  + 5 V49; every listed pair with F3 owned or OC1 has blocks; no unlisted or NQ pair computed. firm_check: MLL match
  for all five; DLL match for Lucid, Tradeify, MFFU, "unverifiable" (none) for Topstep and Bulenox (LR-DLL).
- Regression against E.28 (REGRESSION.md, read): 121/121 mu*_mkt identical, mu10K_mkt = E.28 mu10K + 1.00, cost per
  attempt 0 difference, EV at the threshold within 4.5e-6 USD.
- S_mean run (econ32b_smean.json): bulenox|HG, lucid|HG, tradeify|HG with S_rt 1.55 and topstep|MNG with 2.414, all
  confirmed, F4 copy f9bbef68; RL-SMEAN patches exactly these four primary blocks plus 15 F4 spread/touch values
  (HG 1.55, MNG 2.414, BTC 4.72, 10Y 1.67; touch 6A 15, 6E 23, CL 8, HG 5.35, ZB 377, ZC 375.27, ZF 1319, ZN 2507,
  ZS 26.32, ZT 99471, ZW 43.92).

## Check 7. reports/stage_e32b_ranking.md against score32b_out.json (work/rv1/check_rankmd.py)

Every cell of tables 2a (47 rows), 2b (47), 2c (47), 3a (103), 3c (132), 4 (15), 5 (116), 6 (28) and the section 7
sat1 table (QM, QG, MGC ranks from my sat1 recomputation) compared at the printed precision: 1 mismatch (N1). Prose
claims checked and right: 35 pass / 11 fail (8 sigma unknown, 3 D4 = 0: QG, QM, XW); 126 listed, 103 ranked; 21 tie
groups, 19 by m*, 2 by cost (M6A, M6E); 13 sourced S; the unknown-rule counts; P 77/57 and Rel 77 on ranked pairs; D2 c
provisional 34; 28 variants, YM in every top 5 and first in 23, the five exceptions, MNQ out of the top 5 in OC1_off and
RS-MNQD6 (MNQ ranks 13/15/21/31/45); 3c's 72/31/9/9/6/5; section 5's 54/49/8 (5 QM, 3 SIL)/5 and the 10 unlisted rows;
section 7: QM J 2,848 USD and L1 1.80; ZM L1 2.725, Topstep rank 24 S 2.794 E 2.66 m* 0.071, others 41-60 with E
2.24-2.57, E.28 rank 6, +0.29 from L1; MGC L1 2.55, best MFFU 58 S 2.570, E 1.85-1.88 / 0-0.42; ZL ranks 15 and 21-38,
bands 2/3/3/4; MYM 14/17/31/36/70; M2K 20/29/59/65/76; MCL 48-90; MNG 85; MBT 92-96; M6A 94-98; M6E 100-103; MHG 99;
HG 49/51/66; the "next products" table's 19 best ranks; the inter-rater lists (N7); BTC listed at no firm.

## Not checked, or checked only in part

- F3 was reran for 3 of 22 owned roots (the brief's cap); the other 19 are covered by the code reading and the OC1
  arithmetic, not by a rerun.
- The econ model itself (E.28's funnel, 20,000 paths) was not re-simulated; its inputs, outputs, grid rule, sign change
  at the thresholds and the E.28 regression were checked.
- Blind ratings were not re-rated; I checked their unknown rules, evidence caps, timing, leak exposure and the
  inter-rater comparison, not the rater's judgments.
- Spread and touch items were checked against F4's recorded clauses and notes and the FactAuditor's re-extraction, not
  by re-opening every source page.
- Econ pass 2 (E_dir 30/120/240) was running during this review; its blocks were not read and are outside step 4.
- Holdout status at the end of this review (07:21:40 PDT): all_ok True, unlocks_logged 0.
