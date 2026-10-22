# Stage E.28 Part A: ranking review (RankingReviewer-FableXHigh)

Reviewer: Fable 5.1, xhigh. Started 2026-10-21 16:09 PDT. Spec reports/stage_e28_ranking_spec.md sha256
89347e972ee14f637f0504035750ed952dc999e4787d92394ff7decd5a499a5f (verified by sha256sum at start). Lead rulings
reports/stage_e28_briefs/A3_lead_rulings.json. Work folder: reports/stage_e28_briefs/work/REV_rank/ (own scripts only;
score.py is not imported). All sections complete (finished 16:35 PDT).

Severity: BLOCKING = wrong number or rule that changes the top pair, the order of the top five, the purchase or the
measurement's validity. SHOULD FIX = misleading or wrong but not decision-changing. NOTE = everything else.

## Findings table

Counts: BLOCKING 1 (a lead decision to re-affirm, not a computational error), SHOULD FIX 3, NOTE 9.

| ID | Severity | Where | Finding | Effect on top pair / top five |
|---|---|---|---|---|
| RR-01 | **BLOCKING** (conditional: stands only if the lead re-affirms the C40 C1(b) reading with the consequence known) | A3_blind_ratings.json C40 (QG) C1b = medium; A3_masked_contracts.json C40 C1b_evidence; A3_lead_rulings.json BlindScorer_alternatives | Every C1(b) field the natural-gas reader supplied for QG is literally "UNKNOWN. Searched: ..." (matching algorithm, market-maker or incentive programmes, HFT/automated share, spread, depth, touch queue). The spec says "Unknown counts as high". The blind scorer rated medium on the ground that a failed one-query programme search is the spec's "no market-maker program found" marker, and flagged "C1b alt high ... under the spec default C1b = high". The lead's ruling "C1(b) partial evidence stays as rated" was written at 15:13 PDT "before any ranking output was read", so without knowing that this one field decides the top pair. Under the spec's literal default C1(QG) = 1, L1 = 1.850 < 2.00 and QG fails the Layer 1 gate (variant `C1b_unknown_counts_high`: 15 survivors; 1 topstep QM 2.359, 2 mffu QM 2.302, 3 tradeify QM 2.290, 4 lucid QM 2.266, 5 bulenox QM 2.263). QM and MNG survive the same reading (L1 2.15 and 2.20). QG is the only contract in the top ten whose survival rests on it. | Changes the top pair (topstep QM), the top contract (QM) and the purchase under the spec-literal reading. The scorer's reading is defensible; the lead must re-affirm it knowingly or the ranking changes. |
| RR-02 | NOTE | A3_econ.json topstep pairs, flag "fee conflict"; Task 4 | Topstep's LFA-costs page says "In the Trading Combine, a $3.70/lot simulated fee is charged"; the commissions page gives QG 2.02 and says its fees apply in the Combine, XFA and LFA. Decision (4.2): 2.02 governs both stages; 3.70 is a stale flat figure, per round turn if anything. Under 3.70 RT the order of the top five is unchanged (QG 2.4756 vs QM 2.4740); only the unsupported per-side reading (7.40) moves the top pair to tradeify QG (same contract). | None under the supported readings; the rank 1-2 margin falls to 0.0016 under 3.70 RT. |
| RR-03 | SHOULD FIX | A3_blind_ratings.json C6 = 3 for 13 grain codes; A1_grains.md line 296 "abstract only [unverified]"; OC-6 | OC-6's symmetric clause: all 13 grain C6 = 3 ratings (MZC, MZS, MZW, MZL, MZM, XC, XK, XW, ZC, ZS, ZW, ZL, ZM) rest only on Volkenand, Filler, Odening (2018), known from an OpenAlex abstract; no other qualifying positive item exists on any grain sheet. They must be capped at 2. The 5 equity C6 = 3 ratings rest on Dixon (2017) full text (1,139 lines saved) and stand. | Top five unchanged. Ranks 8-20 change: topstep ZM 8 -> 10 (2.312), bulenox QM 9 -> 8, bulenox QG 10 -> 9, mffu ZM 11 -> 13, lucid ZM 12 -> 16; MNQ baseline ranks become topstep 28, lucid 33, tradeify 21, mffu 22, bulenox 18. |
| RR-04 | SHOULD FIX | A3_blind_ratings.json F03.R vs F03.R_by_size and reasons; score.py r_for() | The scorer's F03 (Topstep) `R` dict gives equity_index 3 and metals 3, but its `R_by_size` gives micro 4 / non-micro 3 and its reason says micros are "capped (3 at 50K ...)" in the news window, "a cap a 1-contract strategy never reaches (4)"; the flag names 3 for micros as the alternative "literal reading". score.py reads the class dict, so topstep MNQ, M2K, MYM, MGC and MHG carry R = 3 against the scorer's stated primary. Under R = 4: topstep MGC 2.225 -> 2.275 (rank 19 -> 13), topstep MNQ 2.125 -> 2.175 (33 -> 21), M2K and MYM 2.100 -> 2.150 (42/43 -> 27/28), MHG 1.950 -> 2.000 (56 -> 53). The lead decides which of the scorer's two readings is primary (the spec's text "restricted around at most 2 scheduled events per week" supports 3; the scorer's reasons support 4) and the table should say which. | Top five unchanged. The MNQ baseline rank the return reports changes (topstep MNQ 33 -> 21). |
| RR-05 | SHOULD FIX (lead decision) | A3_firm_products.json lucid pairs fee_rt_usd; pages/A2_lucid/sup_products_commissions.html.txt; A3_econ lucid flag "exchange/NFA inclusion not stated" | Lucid's table is headed "Commission (Per Side)" ("the commission rates per contract, so you know exactly what you can trade and what it costs") and never mentions exchange or NFA fees. FactTable marked the doubled figure (QG 2.60, QM 4.00) "sourced"; the spec's 'u' rule ("if a fee is unknown, the highest fee found for that product class at the other four firms") would give QG 4.00 and QM 5.40. Re-run (rr_econ_lucidalt.json): lucid QG 0.33 / 1.33 / 0.85, lucid QM 0.44 / 1.44 / 0.88. Variant `lucid_fee_u_rule`: lucid QG S 2.424 -> 2.386, rank 5 -> 6; tradeify QM (2.415) becomes rank 5; lucid QM 7 -> 9. | Changes the fifth of the next four if the lead reads the fee as unknown; top pair and ranks 1-4 unchanged. The table should carry the reading explicitly (u or sourced). |
| RR-06 | NOTE | A3_facts.json QM.C4.releases_2plus_per_week (flag "ambiguous"); OC-A3-5 | The crude reader counts 1 scheduled release a week (EIA WPSR) "2 if API is counted" (API weekly, Tuesday 16:30 ET, "impact weak"). Read as not holding (lead accepted). If counted, every QM pair loses 0.075 and topstep QM falls from 2 to 4 (published C4_conservative; my variant agrees). | Order of the top five changes under the conservative reading; top pair unchanged. |
| RR-07 | NOTE | A3_blind_ratings.json F03 Rel; A2_firm_topstep.md line 274 | McCrudden v. Topstepfunded LLC (filed 2026-04-09) is open; the complaint was not read and its subject is known from press and a snippet only, so the 0 deduction for documented payout disputes follows the rules. If treated as documented, Topstep Rel = 2 and ranks 2 and 3 swap (tradeify QG 2.452 above topstep QM 2.434); top pair 2.474 unchanged. | Ranks 2-3 only, under a reading the rules do not admit. |
| RR-08 | NOTE | A3_econ S_rt default 1 (u) for QG and QM | No sourced median spread for QG or QM; both default to 1 tick. Raising both to 2 or 3 ticks lowers all QG and QM pairs together and leaves their order unchanged (rr_spread_sens.txt). Only a QG spread two or more of its own ticks wider than QM's would put QM first. | None under equal treatment. |
| RR-09 | NOTE | ranks 4-5 | mffu QM 2.427 vs lucid QG 2.424: 0.003 apart; any 0.005 change in either L2 swaps them. | Ranks 4-5 fragile. |
| RR-10 | NOTE | A3_firm_products.json mffu QG listed_50k "no" (currently restricted) | mffu QG is excluded by the listing gate (restriction of 2026-02-07, described as temporary). EconCoder computed it anyway: mu*_lim 0.25 at F_rt 2.92, which would score about S 2.49, rank 2. | If MFFU lifts the restriction before the purchase, rank 2 changes; the top contract does not. |
| RR-11 | NOTE | A3_econ.json seed | Seed changed 20261021 -> 20261022 for the top six pairs and topstep MNQ: all 21 thresholds identical (0.00 tick); cost per attempt moves <= 0.09 USD. | None. |
| RR-12 | NOTE | A3_ranking_table.md "u" column | The spec says the table marks facts that took the unknown default "u"; the ranking table's u column omits the S_rt = 1 default (every pair except CL, GC, SI and the four Treasuries) and the fee-inclusion doubt at Lucid; both are flagged only in A3_econ. | Presentation only. |
| RR-13 | NOTE | A3_facts.json M2K, MYM ADV ("ADV_standard_window_not_latest") vs MNQ (2025 figure) | Within one family the ADV source window differs (nothing later than 2023-10 was found for M2K and MYM; a 2025 CME figure was used for MNQ). Consistent with the spec's fallback; no score changes (both stay C3 = 3). | None. |

## Task 1: independent recomputation of the primary table

Script: reports/stage_e28_briefs/work/REV_rank/rr_score.py (written from the spec text; score.py not imported; same
four fact files plus A3_mask_key.json). Output: work/REV_rank/rr_primary.json (my table), rr_variants.json (my
sensitivity variants), rr_score.out (console).

Result: **0 mismatches** against A3_ranking_table.json (variant `primary`): every C1..C6, L1 and gate verdict for all 47
candidates; every E, D, R, A, F, P, Rel, L2, S and rank for all 126 listed pairs (71 ranked, 20 Layer 1 survivors).
Tolerance 1e-9 on the unrounded scores. The tie rule (S rounded half-up to 2 decimals, then lower mu*_lim, higher L1,
lower cost per attempt, contract code, firm name) reproduces the published order, including the three places where
a lower unrounded S sits above a higher one (topstep ZM 2.387 above bulenox QM 2.388 at rank 8/9; mffu ZL 2.153 below
lucid ZL 2.147 at 22/23; mffu MCL 2.135 below tradeify ZL 2.126 at 31/32), which the spec's rounding-then-tie-break
rule requires.

Hand check of the top pair (all numbers from the fact files, not from score.py): QG C1 = 2 (medium, medium), C2 = 2
(proxy r = 1/1.2561 = 0.796, in [0.5, 1)), C3 = 1 (ADV 3,937 in [1,000, 10,000)), C4 = 3 (one item holds: limit-hit
count unknown; EIA storage is 1 release/week, no weekend gap, big moves 0.42/yr from NG under OC-A3-6), C5 = 3
(sigma_1m 1.2561 in [1, 1.5)), C6 = 2; L1 = 0.50 + 0.40 + 0.15 + 0.45 + 0.30 + 0.30 = 2.100. Topstep QG: E = 0.60 x
4(1 - 0.19/2) + 0.15 x 4(1 - 1.19/3) + 0.25 x 4(1 - 0.49/3) = 2.172 + 0.362 + 0.837 = 3.371; D = 4 (room = 2000 /
(31.6 x 12.5) = 5.06); R 4, A 2, F 1, P 2, Rel 3; L2 = 1.348 + 0.4 + 0.4 + 0.3 + 0.1 + 0.1 + 0.3 = 2.948; S = 2.524.

Margins that matter for the top five: rank 1 to 2, 0.040; 2 to 3, 0.032; 3 to 4, 0.025; 4 to 5, 0.003 (mffu QM 2.427
vs lucid QG 2.424: any 0.005 shift in either L2 flips them); 5 to 6, 0.009 (tradeify QM 2.415). QG's Layer 1 margin
over the gate is 0.10 (L1 2.100 vs 2.00), one C1 step (0.25) wide of failing.

## Task 2: lead rulings applied as written; OC-6 symmetric clause on C6 >= 3

### 2.1 Each ruling against score.py and my recomputation

| Ruling | As written | Applied in score.py / table | Verdict |
|---|---|---|---|
| OC-A3-1 (MNG gate) | MNG passes the 60-date gate; any other unknown gate stays excluded | MNG gate forced True with flag; 5YY and 30Y stay "unknown (not shown)" and excluded | exact |
| OC-A3-2 (D unknown) | D with unknown R_d scores 1; variant D_unknown_0 kept | d_score(None) = 1; 9 pairs (SI, SIL, MET) flagged u; variant present | exact |
| OC-A3-3 (E unknown) | each s() component with unknown mu scores 1, so E = 1; variant E_unknown_0 | e_score componentwise 1; same 9 pairs E = 1.00 flagged u; variant present | exact |
| OC-A3-4, -5, -7, -8, -9, -10, -11 | accepted as FactTable wrote them | QV primary where formed (CL, GC, ZF, ZN, ZB, ZC, ZS, ZW), proxy elsewhere; C4 "ambiguous" items read as not holding in the primary, C4_conservative variant shown; 0-contract 50K caps read as not listed (topstep SI, HG, PL absent from the listed pairs) | exact |
| OC-A3-6 (jump transfer) | sibling big-move counts PRIMARY; no-transfer shown as a variant | facts.variants.C4_jump_transfer merged into every variant except C4_no_transfer; 11 OC-1 codes get the sibling count (QM, MNG, QG, M6E, M6A, BTC, M2K, MYM, MNQ, MZ*, XC, XK, XW get False where the sibling rate < 10/yr) | exact |
| OC-6 (unverified evidence) | no C6 = 0 or C6 >= 3 may rest only on abstract/snippet evidence; C25 (NQ) 0 replaced by the OC-7 floor; reviewer checks every C6 >= 3 | NQ C6 = 2 (rated 0) in the table; the C6 >= 3 check was NOT done by score.py (it has no notion of evidence quality); see 2.2 | applied to C25 only; the symmetric half is this review |
| OC-7 (class floor) | every C6 rated 1 becomes 2; C6 = 0 only on full-text negative evidence (none) | c6_floor = 2 raises 23 contracts rated 1 and C25's 0; C6_as_rated variant kept | exact |
| BlindScorer_alternatives | primary ratings stand for C07, C15, F04 (A = 2); C1(b) partial evidence stays as rated | C07 (MNQ) C6 = 3 not 0; C15 (ZN) C6 1 -> 2 by the floor, not 0; F04 (bulenox) A = 2; every C1b = medium kept | exact, but see RR-01: for C40 (QG) this ruling is the single hinge of the top pair |

Checks on the floor's own evidence (OC-7): the "X39 OFI studies ... significant at the one-second horizon" line is
Takahashi 2025 (arXiv 2508.06788v2), saved full text pages/C2_OFI/emini_ofi_2025.txt (790 lines; the sentence is in
the abstract, line 22, and the conclusion, line 709). Dixon 2017 is saved full text pages/C2_DeepLOB/dixon_rnn_seq2017.txt
(1,139 lines; the quoted sentence at lines 24 and 1023). The level-2 floor therefore rests on verified full text, and
OC-6 does not constrain level 2 in any case.

### 2.2 OC-6 symmetric clause: every C6 >= 3 and the evidence it rests on

19 contracts are rated C6 = 3 (none 4). Two evidence bases:

(a) Dixon (2017), RNN price-flip classification on ES level II, COUSIN for the equity index candidates RTY, MNQ, MYM,
YM, M2K. Full text saved (above). The rating does not rest on an abstract or snippet. **Stands.** (The negative cousin
items the scorer weighed, Rodas 2026 on NQ, are abstract-only, so they could not have set a 0 either.)

(b) Volkenand, Filler, Odening (2018), Agricultural Finance Review, order imbalance in CME grains, for ALL 14 grain
candidates rated 3: MZM, XK, ZM, MZL, ZC, ZS, ZL, MZC, ZW, XW, MZS, MZW, XC (and the reader's sheet for every grain code).
A1_grains.md line 296: "abstract only [unverified]: openalex_10_1108_afr_10_2017_0099.json"; A1_grains.json carries the
item as "positive (lagged order imbalance predicts returns for some contracts) [abstract only]". The blind scorer's own
reason for each of these says "[abstract only]" and flags "without the abstract-only item: 1" (which the OC-7 floor
makes 2). No other qualifying positive item exists on any grain sheet (Hu et al. is gross-only; de Boer is liquidity
spillovers; Arzandeh-Frank is an information share, "not a trading test"). **Under OC-6 as written, every grain C6 = 3
must be capped at 2.** (My script's set of "C6 >= 3 whose scorer reason contains 'abstract only'" is {M2K, MZC, MZL, MZM,
MZS, MZW, XC, XK, XW, YM, ZC, ZL, ZM, ZS, ZW}: M2K and YM enter that set only because their reasons mention the Rodas
abstract as a NEGATIVE item; their positive item is Dixon full text, so they are not capped. The cap applies to the 13
grain codes.)

Ranking with the 13 grain C6 capped at 2 (L1 of every grain candidate -0.15, S -0.075; variant
`OC6_cap_abstract_only_C6` in rr_variants.json; the two equity codes in the set shift nothing in the top 20 either way):
top five unchanged (topstep QG 2.524, topstep QM 2.484, tradeify QG 2.452, mffu QM 2.427, lucid QG 2.424); ranks 6-7
unchanged (tradeify QM, lucid QM); bulenox QM moves 9 -> 8, bulenox QG 10 -> 9, topstep ZM 8 -> 10 (S 2.312), mffu ZM
11 -> 13, lucid ZM 12 -> 16, topstep ZL 18 -> ~22. 20 Layer 1 survivors still (the lowest grain survivor, ZL/ZM at
2.300, becomes 2.150; XC 2.400 -> 2.250; XK 2.550 -> 2.400). MNQ baseline ranks: topstep 28, lucid 33, tradeify 21,
mffu 22, bulenox 18.

Conclusion for Task 2: the rulings are applied exactly as written; the one open item is the symmetric OC-6 cap on the
13 grain C6 = 3 ratings, which changes ranks 8 to 20 but not the top pair or the next four (finding RR-03).

## Task 3: economics re-derivation (fee in ticks, sigma_T, daily mean and SD) and seed stability

### 3.1 Hand re-derivation from the sources (work/REV_rank/rr_task3_hand.txt)

Fees read from the saved pages, tick values from the A1 rulebook quotes, sigma_1m and R_d from A0_contract_stats.json
(sibling root, scaled by the tick ratio under OC-1). Daily mean = T (mu - c) v, daily SD = sqrt(T) sigma_T v, T = 20.

| pair | F_rt USD (page) | v | c_lim = F/v ticks | sibling sigma_1m (ticks) x ratio | sigma_T ticks | SD/day USD | mean/day at mu*_lim USD | mean/day at mu = 0 | R_d ticks | matches A3_econ |
|---|---|---|---|---|---|---|---|---|---|---|
| topstep QG | 2.02 (ts_8284213 "E-mini Natural Gas (QG) $2.02") | 12.50 | 0.1616 | NG 6.2803 x 0.2 | 1.2561 | 70.22 | +7.10 (mu 0.19) | -40.40 | 31.60 | yes |
| topstep QM | 3.42 ("E-mini Crude Oil (QM) $3.42") | 12.50 | 0.2736 | CL 6.2998 x 0.4 | 2.5199 | 140.87 | +11.60 (0.32) | -68.40 | 97.60 | yes |
| tradeify QG | 4.00 (tf_wf_comm L11; "includes Exchange fees, NFA fees, Clearing fees, and Commissions") | 12.50 | 0.3200 | NG x 0.2 | 1.2561 | 70.22 | +2.50 (0.33) | -80.00 | 31.60 | yes |
| mffu QM | 4.32 (mffu_art_9735811 "E-mini Crude Oil QM ... 0.025 $12.50 $4.32", Total Cost Round Trip) | 12.50 | 0.3456 | CL x 0.4 | 2.5199 | 140.87 | +1.10 (0.35) | -86.40 | 97.60 | yes |
| lucid QG | 2.60 (sup_products_commissions: QG 1.30 under "Commission (Per Side)", x 2) | 12.50 | 0.2080 | NG x 0.2 | 1.2561 | 70.22 | +3.00 (0.22) | -52.00 | 31.60 | yes (see RR-05 on inclusion) |
| tradeify QM | 5.40 (tf_wf_comm L11) | 12.50 | 0.4320 | CL x 0.4 | 2.5199 | 140.87 | -0.50 (0.43) | -108.00 | 97.60 | yes |
| topstep MNQ (baseline) | 1.22 ("Micro E-mini NASDAQ 100 (MNQ) $1.22") | 0.50 | 2.4400 | NQ 27.8254 x 1 | 27.8254 | 62.22 | +8.20 (3.26) | -24.40 | 967.0 | yes |
| topstep ZM (rank 8) | 5.28 ("Soybean Meal (ZM) $5.28") | 10.00 | 0.5280 | ZM own 3.1522 | 3.1522 | 140.97 | +12.40 (0.59) | -105.60 | 96.00 | yes |

Every F_rt_ticks, sigma_T, c_lim, c_mkt (= c_lim + 1) and R_d in A3_econ.json agrees with these to the printed
precision. Tick values: QG 0.005 USD/MMBtu x 2,500 MMBtu = 12.50 (NYMEX rulebook ch. 402 quote in the facts); QM 0.025
x 500 bbl = 12.50; MNQ 0.25 x 2 = 0.50. The tick-ratio scaling (NG 0.001 -> QG 0.005 is x0.2; CL 0.01 -> QM 0.025 is
x0.4; NQ -> MNQ x1) is right. Note that the tradeify QM break-even sits one grid step below its own cost (0.43 < 0.432):
expected net cash per cycle is non-negative at a slightly negative per-trade drift because the trader's downside is
capped at the evaluation fees while payouts accrue on the winning paths; it is a property of the E.19 funnel, not an
arithmetic slip.

### 3.2 Seed stability (EconCoder's code re-run with BASE_SEED 20261022 instead of 20261021)

Driver: work/REV_rank/rr_econ_rerun.py (imports A3_funnel/A3_models/A3_run unchanged; sets F.BASE_SEED before the
draws are built; nice 10; 2 processes; 500-520 MB RSS each; 134 s and 175 s). Outputs rr_econ_seedA.json,
rr_econ_seedB.json, logs rr_econ_seed*.log.

| pair | mu*_lim (new / published) | mu*_mkt | mu10K | cost per attempt USD | EV at mu = 0 USD |
|---|---|---|---|---|---|
| topstep QG | 0.19 / 0.19 | 1.19 / 1.19 | 0.49 / 0.49 | 92.09 / 92.05 | -7,571 / -7,566 |
| topstep QM | 0.32 / 0.32 | 1.32 / 1.32 | 0.54 / 0.54 | 50.57 / 50.53 | -4,222 / -4,218 |
| tradeify QG | 0.33 / 0.33 | 1.33 / 1.33 | 0.61 / 0.61 | 95.83 / 95.83 | -5,750 / -5,750 |
| mffu QM | 0.35 / 0.35 | 1.35 / 1.35 | 0.90 / 0.90 | 153.00 / 153.00 | -9,180 / -9,180 |
| lucid QG | 0.22 / 0.22 | 1.22 / 1.22 | 0.74 / 0.74 | 120.87 / 120.87 | -7,252 / -7,252 |
| tradeify QM | 0.43 / 0.43 | 1.43 / 1.43 | 0.75 / 0.75 | 95.83 / 95.83 | -5,750 / -5,750 |
| topstep MNQ | 3.26 / 3.26 | > 4 / > 4 | > 4 / > 4 | 165.05 / 165.14 | -13,242 / -13,246 |

All 21 thresholds are identical under the new seed (difference 0.00 tick, inside the +-0.02 tick tolerance). The
draws did change (EV at mu = 0 and the Topstep cost per attempt move by a few USD); the one-time-fee firms' values are
deterministic at mu = 0 (60 attempts x fee). The thresholds therefore do not depend on the seed at the 0.01-tick grid,
and the E scores of the top six are stable (variant `econ_seed_20261022` in rr_variants.json reproduces the primary top
ten exactly).

## Task 4: Topstep QG fee conflict (3.70 USD per lot simulated Combine fee vs 2.02 USD round trip)

### 4.1 What the two saved pages say

pages/A2_topstep/ts_8284229.html.txt ("What are the costs in the Live Funded Account?", dateModified 2026-10-19,
fetched 2026-10-21 05:41 PDT, sha256 8bf4f0b7...): under "2. Round-Turn Costs": "Round-turn costs are deducted directly
from your brokerage account balance. In the Trading Combine®, a $3.70/lot simulated fee is charged to emulate these
real-world costs. Commissions & Fees: $0.72–$2.04 (go to brokerages) Exchange Fees: $2.46–$4.30 (set by exchange, vary
by instrument) Examples (round turn): E-mini S&P 500 (ES): $3.80 E-mini NASDAQ 100 (NQ): $3.80 Crude Oil (CL): $1.54
Gold (GC): $4.24 Full breakdown by platform and product: TopstepX™ Commissions and Fees".

pages/A2_topstep/ts_8284213.html.txt ("TopstepX™ — Commissions and Fees", dateModified 2026-09-30, fetched 05:42 PDT,
sha256 64de4659...): "These fees apply when trading the Trading Combine, Express Funded Account, and Live Funded
Account. Commissions and fees are automatically deducted from each trade, and you'll see a breakdown in the TopstepX
platform and from your Dashboard!" ... "Round-Turn (RT) cost: charged when you complete both sides of a trade. Each side
(Buy or Sell) incurs half the total" ... product table: "E-mini Natural Gas (QG) $2.02", "E-mini Crude Oil (QM) $3.42",
"Micro E-mini NASDAQ 100 (MNQ) $1.22", "Soybean Meal (ZM) $5.28"; the ES example decomposes 3.78 = 2.76 exchange + 0.02
NFA + 1.00 commission.

### 4.2 Decision: which fee applies to a QG round trip

The per-product table (QG 2.02 USD per round trip) applies in both the Trading Combine and the Express Funded Account.
Reasons: (1) the commissions page says so in terms ("apply when trading the Trading Combine, Express Funded Account, and
Live Funded Account") and describes the mechanism (deducted per trade, shown in TopstepX); (2) it is the product-specific
page and the LFA page itself defers to it ("Full breakdown by platform and product"); (3) the LFA page's "$3.70/lot" is
a single flat figure that is inconsistent with that page's own examples (ES 3.80, CL 1.54, GC 4.24) and with the
product table (CL 4.02, GC 4.32, ES 3.78); it matches the legacy flat sim fee at ES level and reads as a stale sentence
on a page about live-account costs, not as a per-product rule; (4) a flat per-lot fee cannot describe QG when the firm
publishes QG at 2.02 on the page it points to. On the unit: the sentence sits under "Round-Turn Costs", so "$3.70/lot"
reads as per round turn per contract; a per-side reading (7.40 per round trip) has no support in the text and is kept
only as a stress case. EconCoder's primary (2.02) is therefore the right reading; the 3.70 alternative is a sensitivity,
which is how A3_econ treats it ("conservative" row in its mapping table, alt_fee sensitivity per pair).

### 4.3 Economics under the alternatives (EconCoder's code, original seed 20261021; rr_econ_altfee.json)

| pair | F_rt USD | c_lim ticks | mu*_lim | mu*_mkt | mu10K | cost/attempt USD | E | L2 | S | rank |
|---|---|---|---|---|---|---|---|---|---|---|
| topstep QG primary | 2.02 | 0.1616 | 0.19 | 1.19 | 0.49 | 92.05 | 3.371 | 2.948 | 2.524 | 1 |
| topstep QG at 3.70 RT | 3.70 | 0.2960 | 0.33 | 1.33 | 0.63 | 49.84 | 3.128 | 2.851 | 2.4756 | 1 |
| topstep QM primary | 3.42 | 0.2736 | 0.32 | 1.32 | 0.54 | 50.53 | 3.172 | 2.569 | 2.484 | 2 |
| topstep QM at 3.70 RT | 3.70 | 0.2960 | 0.35 | 1.35 | 0.57 | 49.88 | 3.120 | 2.548 | 2.4740 | 2 |
| topstep QG at 7.40 RT (per-side stress) | 7.40 | 0.5920 | 0.62 | 1.62 | 0.92 | 49.00 | 2.625 | 2.650 | 2.375 | 8 |
| topstep QM at 7.40 RT (per-side stress) | 7.40 | 0.5920 | 0.64 | 1.64 | 0.86 | 49.02 | 2.606 | 2.342 | 2.371 | 9 |

EconCoder's own alt_fee sensitivity gives the same mu*_lim (0.33 and 0.35); it did not report mu*_mkt or mu10K under
the alternative, which this re-run supplies. All other Topstep pairs have table fees above 3.70 (ZM 5.28) or are already
"> 4" (the micros), so max(3.70, table) changes nothing else in the top ten.

Ranking under 3.70 RT applied to every Topstep pair (variant `topstep_fee_3.70_RT`): 1 topstep QG 2.4756, 2 topstep QM
2.4740, 3 tradeify QG 2.4519, 4 mffu QM 2.4270, 5 lucid QG 2.4241, 6 tradeify QM 2.4146. **Top pair, top contract and
the next four are unchanged.** The margin between ranks 1 and 2 shrinks from 0.040 to 0.0016 (rounded 2.48 vs 2.47);
even at equal rounding the tie rule (lower mu*_lim, 0.33 vs 0.35) keeps QG first.

Ranking under the per-side stress (7.40 RT; variant `topstep_fee_3.70_per_side`): 1 tradeify QG 2.452, 2 mffu QM 2.427,
3 lucid QG 2.424, 4 tradeify QM 2.415, 5 lucid QM 2.391; topstep QG falls to 8 and topstep QM to 9. The top PAIR would
change (to tradeify QG) but the top CONTRACT (QG) would not, so the purchase would be the same. This reading is not
supported by the page text.

## Task 5: other errors that could change the top pair or the order of the top five

Checked and found correct (no finding): the spec hash and the rulings hash guards; the weights and anchors in score.py
against the spec text; the tie rule and half-up rounding; the 60-date gate for QG (listing inferred, consistent with
QG's published ADV of 8,000 to 11,000 a day in 2023); the Layer 2 listing gate (mffu QG excluded as "currently
restricted", OC-A3-9); BC eligibility (all five firms True); P items (Topstep: VPS prohibited and 3.3 orders/s API
limit, so P = 2; Bulenox 2; the other three 1); Rel deductions against the A2 evidence (Lucid under 2 years: waitlist
page 2025-02-20, footer "@2024-2026", so the -1 is right; Tradeify operating since the 2022-12-05 Wayback capture, the
"2024" launch is an interview pointer and not evidence, so no deduction; Topstep -1 for two adverse changes); the ADV
sources (QG 3,937 is the CME YTD Jan-Sep 2026 figure, cme_ADV_report_CMEG_202610snap.txt line 613, so C3 = 1 under the
spec's "most recent 12-month published" fallback, and the nearest 12-month figures, 4,502 YTD Jan-Oct 2025 and 4,618
YTD Jan-Sep 2025, give the same score); the QG C4 items (EIA storage once a week, no weekend-traded Henry Hub
instrument, limit-hit count unknown and counted as holding, big moves transferred from NG at 0.42/yr).

Sensitivities that would reorder the top five but rest on a judgment the lead has already made or on evidence the rules
do not admit (reported as NOTE unless stated):

- RR-01 (C1(b) for QG): see the findings table. The decisive one.
- QM's second weekly release (API inventory report, Tuesday 16:30 ET): the crude reader gives "1 ... 2 if API is
  counted", impact "weak"; FactTable read it as not holding (flag "ambiguous"); the lead accepted (OC-A3-5). If counted,
  every QM pair loses 0.075 of S and topstep QM falls from 2 to 4 (the published C4_conservative variant; my script
  agrees: topstep QG 2.524, tradeify QG 2.452, lucid QG 2.424, topstep QM 2.409, topstep ZM 2.387).
- Topstep Rel: McCrudden v. Topstepfunded LLC (M.D. Fla. 3:26-cv-00816, filed 2026-04-09) is open; its subject is known
  only from secondary press and a search snippet (the complaint was not read), so the scorer's 0 for "documented payout
  disputes" follows the rules. If the lead treated it as a documented dispute, Topstep Rel = 2 and the order becomes
  topstep QG 2.474, tradeify QG 2.452, topstep QM 2.434, mffu QM 2.427, lucid QG 2.424 (ranks 2 and 3 swap; top pair
  unchanged). Variant `topstep_Rel2_lawsuit_as_dispute`.
- Lucid Rel: if Lucid were found to have operated for 2 years (it has not: Feb 2025), lucid QG would move to rank 3
  (2.474). Variant `lucid_Rel3`. Tradeify Rel: an under-2-years deduction would drop tradeify QG to rank 5 (2.402).
  Variant `tradeify_Rel2`. Neither is supported by the evidence.
- Spread default S_rt = 1 tick (u) for QG and QM alike: no sourced median for either. Moving both to 2 or 3 ticks
  lowers every QG and QM pair together and leaves their order unchanged (work/REV_rank/rr_spread_sens.txt: at 3 ticks
  topstep QG 2.452, topstep QM 2.417, tradeify QG 2.385, mffu QM 2.361, lucid QG 2.353). Only a QG spread wider than
  QM's by two or more of its own ticks while QM stays at 1 would put QM first; nothing sourced says either way.
- mffu QM (2.427) versus lucid QG (2.424): a 0.003 margin. Any 0.005 change in either pair's L2 swaps ranks 4 and 5
  (for example the Lucid fee question, RR-05).
- mffu QG is listed but "currently restricted" (since 2026-02-07, described as temporary) and therefore excluded. Its
  economics were computed anyway (EconCoder: mu*_lim 0.25 at F_rt 2.92). If MFFU lifts the restriction before the
  purchase, mffu QG would score about S 2.49 and take rank 2; the top pair's contract (QG) would not change.
- Topstep R for micro equity index and metals (RR-04): changes ranks 13 to 56 only.

## Recomputed top 10 (own script, primary rules; identical to the published table)

| Rank | Firm | Code | S | L1 | L2 | E | mu*_lim | mu*_mkt | mu10K | cost/attempt USD |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | topstep | QG | 2.5241 | 2.100 | 2.9483 | 3.371 | 0.19 | 1.19 | 0.49 | 92.05 |
| 2 | topstep | QM | 2.4844 | 2.400 | 2.5688 | 3.172 | 0.32 | 1.32 | 0.54 | 50.53 |
| 3 | tradeify | QG | 2.4519 | 2.100 | 2.8039 | 3.135 | 0.33 | 1.33 | 0.61 | 95.83 |
| 4 | mffu | QM | 2.4270 | 2.400 | 2.4540 | 3.010 | 0.35 | 1.35 | 0.90 | 153.00 |
| 5 | lucid | QG | 2.4241 | 2.100 | 2.7481 | 3.245 | 0.22 | 1.22 | 0.74 | 120.87 |
| 6 | tradeify | QM | 2.4146 | 2.400 | 2.4292 | 2.948 | 0.43 | 1.43 | 0.75 | 95.83 |
| 7 | lucid | QM | 2.3913 | 2.400 | 2.3825 | 3.081 | 0.33 | 1.33 | 0.77 | 120.87 |
| 8 | topstep | ZM | 2.3875 | 2.300 | 2.4749 | 2.687 | 0.59 | 1.59 | 0.86 | 49.23 |
| 9 | bulenox | QM | 2.3877 | 2.400 | 2.3755 | 2.439 | 0.72 | 1.72 | 1.06 | 175.00 |
| 10 | bulenox | QG | 2.3551 | 2.100 | 2.6101 | 2.524 | 0.69 | 1.69 | 0.93 | 175.00 |

MNQ baseline: topstep 33, lucid 41, tradeify 24, mffu 25, bulenox 21 (as published; under RR-03 and RR-04 together
topstep MNQ would be about rank 20).

Top five by reviewer variant (rr_variants.json): primary, OC6 grain cap, Topstep R-by-size, seed 20261022, Topstep fee
3.70 RT: topstep QG, topstep QM, tradeify QG, mffu QM, lucid QG in every case. Lucid fee 'u' rule: ..., mffu QM,
tradeify QM (lucid QG 6th). C4 conservative: topstep QG, tradeify QG, lucid QG, topstep QM, topstep ZM. Topstep Rel 2:
topstep QG, tradeify QG, topstep QM, mffu QM, lucid QG. C1(b) unknown counts high: topstep QM, mffu QM, tradeify QM,
lucid QM, bulenox QM (QG excluded). Topstep fee per side (7.40): tradeify QG, mffu QM, lucid QG, tradeify QM, lucid QM.

## Verdict

The published primary table is arithmetically right: an independent script written from the spec text reproduces every
criterion score, L1, L2, S, gate verdict and rank for all 47 candidates and 126 pairs with zero mismatches; every fee in
ticks, sigma_T, R_d, daily mean and SD for the top six pairs and the MNQ baseline re-derives from the saved pages and
A0_contract_stats.json; and the economics are stable to the seed (21 thresholds identical). The lead rulings are
applied as written.

The published top pair (topstep QG) and the next four (topstep QM, tradeify QG, mffu QM, lucid QG) **stand** under the
primary rules, under the OC-6 cap that the rulings asked this review to apply (13 grain C6 = 3 -> 2; RR-03, which
reorders ranks 8 to 20 and should be applied), under the Topstep R-by-size correction (RR-04, ranks 13 to 56), and under
the Topstep 3.70 USD fee alternative (RR-02; the top five keep their order, the rank 1-2 margin shrinks to 0.0016).

They do **not** stand unconditionally. Two lead decisions carry the ranking:

1. RR-01 (BLOCKING unless re-affirmed): the top pair's Layer 1 survival rests on one blind-scorer reading, C1(b) =
   medium for QG, made from reader fields that are all marked UNKNOWN. The spec's own default for unknown is high, under
   which QG fails the gate, no QG pair is ranked, and the top pair is topstep QM (the purchase would be QM data). The
   lead accepted the scorer's reading before any ranking output was read. The lead must either re-affirm "C1(b) partial
   evidence stays as rated" for C40 knowing that it alone decides the contract bought, with the reasoning recorded
   (a one-query negative programme search as the spec's "no market-maker program found" marker), or apply the spec's
   default and re-issue the table with QM first.
2. RR-05 (SHOULD FIX): whether Lucid's "Commission (Per Side)" figures are the all-in fee. Read as unknown under the
   spec's 'u' rule, lucid QG drops from rank 5 to 6 and tradeify QM enters the next four. Ranks 1 to 4 are unaffected.

Everything else that could reorder the top five (RR-06 API report, RR-07 lawsuit, RR-09 the 0.003 margin at ranks 4-5,
RR-10 the MFFU QG restriction) is a judgment the lead has already made within the rules or a fact the rules do not
admit, and none of them moves the top contract away from QG. The one scenario in which the top contract changes is
RR-01.

Review finished 2026-10-21 16:35 PDT. Files: this report; work/REV_rank/rr_score.py, rr_primary.json, rr_variants.json,
rr_score.out, rr_task3_hand.txt, rr_spread_sens.txt, rr_econ_rerun.py, rr_econ_seedA.json, rr_econ_seedB.json,
rr_econ_altfee.json, rr_econ_lucidalt.json and their .log files. Nothing under A3_*, score.py, prop_econ/ or the pages
was edited; no API, broker or Databento call was made; no key was read.
