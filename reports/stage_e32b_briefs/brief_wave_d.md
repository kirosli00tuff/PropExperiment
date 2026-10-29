# Stage E.32b wave-D briefs (step 3b: R2 dossiers, combinations, R3 ratings)

Written by the lead (session 3, Opus 5.5 max) on 2026-10-29 from about 01:15 PDT. Common rules and the shared data
contract of briefs/brief_wave_b.md apply unchanged. The frozen spec reports/stage_e32b_ranking_spec.md (sha256
09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635) section 8 is the contract; never edit it.

Lead rulings for step 3b (decided 01:12-01:15, before any combination was built):
- LR-R1 (V38 scope). V38 closes the intraday program as it was tested: the configurations of the 528 bar-based trials
  (family x product x horizon, R1-01..R1-18 in briefs/R1_closed_lines.md) on the 17 roots. Its umbrella sentence, as
  amended by V45 item 4 (three working-paper effects, none testable with adequate power on owned data), is an evidence
  finding (R1-19), not a ban on new families: V50 and V51 opened this directional program after it. A closed
  configuration stays closed at every venue, the own broker included: the tested signals failed out of sample, not only
  on cost. The ZM 5-60 minute directional families of E.33c (V56) are closed lines on ZM; on other products they are
  family overlap. NQ is excluded (V49); passive spread capture is closed (V50).
- LR-R2a (combination set). Combinations are built for the top-15 pairs (each a Layer 1 survivor at a firm), each
  with every idea family that applies to the code's underlying, plus the own-broker venue (ibkr) for every code in the
  top 15, plus pools (below). Survivors outside the top 15 get no combination.
- LR-R2b (band). A combination's band is its pair's F5 band B (F5_holding.json; ibkr: LR-F5-IBKR) and h_c is the
  member of B with the lowest G (spec 8.2). No other band is used. Where a family's documented horizon lies outside B,
  the dossier says so (Q1 reflects it). A pair with an empty B gets no combination (reported).
- LR-R2c (asset class). Crude and natgas members carry asset_class "energy" (one class, rho 0.5 within, unless E.29
  section 3.2 measured a correlation); other members keep their E.28 family.
- LR-Q6d: sigma_day_ticks = F3's overnight close-to-close sigma (sigma_cc), with sigma_OC beside.

## D1 DossierWriter-OpusXHigh (worker-xhigh, opus): R2 dossiers and the combinations file (two phases)

Read first: spec section 8 (all) and 9.2; work/score/SCHEMA.md section 7 (the combinations file r3_score.py reads);
work/F5/SCHEMA.md (F5_holding.json fields); briefs/R2_idea_families.md and .json (12 families F01-F12, 122 evidence
rows with verified levels and R1 overlaps); briefs/R1_closed_lines.md and .json (23 closed lines, 838 trials).
Evidence comes from those files and the F2 files at their recorded verified levels: no new web lookups. Facts only:
no outcome of any strategy is computed or read.

Phase 1 (groundwork, venue-independent; starts when the lead sends the Layer 1 survivors list). For each survivor's
underlying and each family F01-F12:
- applies (true/false, with the sourced fact that decides it: an event family needs the scheduled event, a
  cross-market family a documented relationship, an order-book family order-book data);
- where it applies: the mechanism; the participant flow and why an edge could exist at retail size (one contract,
  tens of milliseconds to a second, no co-location); the family's documented horizon and timing (release times in PT
  against the main session; events a year from the sourced calendars; trades per event, 1 unless the family defines
  more); the evidence rows (R2 row ids: study, product relation, horizon, data period, in or out of sample, net of
  costs, finding, verified level); the R1 overlap under LR-R1 (line ids, products, horizons, with the quote that
  closes each line);
- the data needed: schema (ohlcv-1m for bar families; mbp-1, tbbo or MBO for book families), a 39-month discovery
  and a 43-month test window (spec 9.2), what is owned, sealed or spent (briefs/F2_data_access.json census), the clean
  test window in months before 2024-03 (sealed for this purpose, or never read and buyable), the approximate Databento
  cost (the census estimates x months, labelled estimates) and the quotes to obtain;
- pool candidates: survivor products that share a mechanism, with E.29 section 3.2's measured rho where it exists
  (reports/E.29_RETURN.md).
Inputs beyond the above: briefs/F2_<family>.json (structural, event and session facts), F2_shared_baltussen.json,
F2_data_access.json, F4_facts_unmasked.json and F4_facts.md (sessions, pauses), reports/E.33c_RETURN.md sections 1 and
7 (cost and trade-count facts only), reports/E.31_RETURN.md sections 1 and 7 (the measured trade-through adverse
selection), reports/E.29_RETURN.md section 1 (payout reachability), the planner notes
(reports/stage_e31_inputs/planner_research_notes.md, reports/stage_e32_inputs/planner_research_soy_complex.md) and
reports/stage_e32_methods_brief.md (890 KB: grep by section only).
Output: work/R2/groundwork.json and work/R2/groundwork.md.

Phase 2 (after the lead's score run; the lead sends the top 15 and the final briefs/F5_holding.json):
- Build the combinations of LR-R2a with LR-R2b's band and h_c, pools included (a pool at a venue needs every member
  listed there; a pool's band is the intersection of its members' bands, h_c its member of lowest worst-member G; an
  empty intersection: no pool combination).
- A script, work/R2/build_combos.py, computes the numbers from F5_holding.json, F4 and the groundwork: c_f in ticks;
  the gross edge per trade needed at h_c to break even and to net 1 tick, and the hit rates p = 0.5 + g / (2 m_hc)
  (normal approximation beside); K_year (continuous families n_cap(h_c) x 252; event families events a year x trades
  per event); trades in the discovery (796 dates) and test (870 dates) windows; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)
  for discovery (SR80 disc G3+G4, binding, and G3 alone) and test (SR80 0.1936, work/F5/SR80.json); the prop fit
  (DLL / (sigma_hc v), flat-by-close against the band, overnight rules, the firm's news windows: events a week that
  stop the family and whether a window covers the event trade, payout threshold against sqrt(n/day) sigma_hc v at one
  contract per E.29); the gate flags; the data costs; and, only where the venue's route admits queue-position limit
  orders (platform facts), a queue-limit variant c_lim priced with E.31's measured trade-through adverse selection as
  the only measurement (reported beside, never scored).
- Write briefs/R2_combinations_unrated.json exactly as SCHEMA.md section 7 with Q1-Q3 absent, and
  work/R2/merge_q.py, which merges the CombinationScorer's ratings (briefs/R2_Q_ratings.json, keyed by combination
  id) into briefs/R2_combinations.json and refuses on a missing or out-of-scale rating.
- Write briefs/R2_dossiers.md (one dossier per product or pool and family, everything spec 8.2 lists, with a venue
  table by combination id) and briefs/R2_dossiers_for_rating.md: the same dossiers with ONLY what Q1-Q3 need
  (mechanism, participant flow, evidence rows with verified levels, horizons, periods and sample, the R1 overlap with
  quotes, the band and its shortest member, per combination id). No cost, fee, power, prop-fit, data-cost or venue
  numbers in that file.

Boundaries: write only work/R2/ and briefs/R2_combinations_unrated.json, R2_dossiers.md, R2_dossiers_for_rating.md
(and R2_combinations.json through merge_q.py when the lead runs it). Never edit F2/F3/F4/F5 files, the scripts in
work/score, work/econ or work/F5, or the spec. No web access, no market data, no outcome.
Return (each phase): paths; at most 200 words (counts of underlyings x families applied, combinations, pools,
exclusions with reasons); anything unfinished.

## D2 CombinationScorer-OpusXHigh (worker-xhigh, opus, fresh; not the DossierWriter)

Read ONLY this section and briefs/R2_dossiers_for_rating.md. Do not open the other dossier file, the combinations
files, the ranking, F5 or any score: Q4-Q7 are computed by a script, and you rate Q1-Q3 without them.
Rate every combination id, each with a one-line reason citing the dossier's evidence row ids:
- Q1 mechanism plausibility (0-4): 4 = an identified non-informational or slow-information participant flow at a
  predictable time (hedging demand, index or ETF rebalancing, report digestion with documented drift), with post-2015
  evidence that the price effect lasts at least the band's shortest member; 3 = identified mechanism, evidence before
  2015 or on a cousin; 2 = plausible mechanism, no direct evidence at the horizon; 1 = a pattern without a participant
  story; 0 = contradicted by full-text evidence or documented as arbitraged away since 2015.
- Q2 evidence quality (0-4): 4 = peer-reviewed, out of sample, net of costs, on this product at this horizon;
  3 = peer-reviewed in sample, or an out-of-sample working paper, on this product, or peer-reviewed out of sample on a
  close cousin; 2 = asset-class-wide or other-venue evidence; 1 = practitioner or anecdotal only; 0 = none, or
  negative evidence.
- Q3 distance from closed lines (0-4): 4 = no overlap with R1; 3 = product overlap only; 2 = family overlap only (the
  family was closed on another product, or on this product at non-neighbouring horizons); 1 = same family and product
  at a neighbouring horizon, or a close variant of a closed configuration; 0 = re-tests a closed line (gate: the
  combination is excluded; name the closed line).
- Evidence rule: a Q2 of 0, 3 or 4 may not rest only on abstract or snippet evidence. If it would, report the value
  the full-text rows alone support when that is at least as far out as the cap (2 from above, 1 from below), with
  "unverified": false; otherwise report your value with "unverified": true (the script caps it).
Output: briefs/R2_Q_ratings.json {"rater": "CombinationScorer-OpusXHigh", "generated_pdt", "ratings": {"<id>":
{"Q1": R, "Q2": R, "Q3": R}}} with R = {"value", "unknown", "reason"} (+ "unverified"), and briefs/R2_Q_ratings.md
(tables and "Flags for the lead": boundary calls, conflicting facts, every Q3 = 0 with its closed line).

## D1 note (lead, 04:10): phases 1 and 2 run as ONE task, after the score run

The DossierWriter starts only when the lead sends the top 15 (from briefs/score32b_out.json) and the final
briefs/F5_holding.json. Do phase 1 only for the underlyings of the top-15 codes (plus pools among them), then phase 2.
All lead rulings are listed in briefs/RULINGS.md.

## D3 RankingWriter-OpusXHigh (worker-xhigh, opus): draft of reports/stage_e32b_ranking.md

Objective: write the stage's ranking file (prompt step 3; spec sections 3-6) from the score output. Facts and arithmetic
from the files only; where a reading needs judgment, write it plainly and mark it "[lead to confirm]".
Inputs: briefs/score32b_out.json and .md (the score run: primary, declared variants, lead-ruling variants RL-*,
rater sensitivities RS-*), F3_vol.md, F4_facts.md, F4_blind_unmasked.json and F4_blind_ratings_masked.md (the rater's
flags), econ32b.json and econ32b_smean.json, briefs/RULINGS.md, reports/stage_e28_ranking.md and
reports/stage_e28_briefs/A3_ranking_table.json (E.28's v2 order), the spec (sections 3-6).
Sections:
1. How to read (S = 0.5 L1 + 0.5 L2; gates; unknown rules; what the blind rater rated and what the script computed).
2. Layer 1, all 47 codes: D1-D6 with D1's band per horizon, L1, L1 < 2.00 flags, the gate result with the spec's
   arithmetic line ("sigma_60 = x ticks vs 2 x (S + 0.5) = y ticks") for every code, D4's L, J and Sat with the rule
   that set Sat; NQ "excluded (V49)".
3. Layer 2 and the full pair table: every listed pair (E with m* and m10K in ticks and sigma_60 units, R, A, D, Rel,
   P, L2, S, rank); excluded pairs (unlisted, A = 0, BC) listed with the reason; NQ pairs "excluded (V49)".
4. The top 15, with each pair's main drivers.
5. Moves against E.28's v2 order: rank in E.28, rank here, and the criteria that moved it (up and down).
6. Variants: every declared variant (slip0, slip1, mad, D1_all, E_dir60, OC1_off, sat1, D2_own, L1min2, spread1),
   every RL-* ruling variant and every RS-* sensitivity, each with its top 5, the MNQ ranks and whether the top 5 is
   the primary's; say which rulings change the top 5 (those are kept in the return).
7. Readings: where S = 1 (u) understates a sourced average (LR-S requires it; list each code and the average);
   where ZM, ZL, QM, MGC and the micros landed and why; the next products after ZM by this ranking; inter-rater
   agreement (rater 1 vs rater 2: 302/329 exact; D6 23/47) and what it means for D6; the HG erratum (LR-S1e).
Output: reports/stage_e32b_ranking.md. Tables may be generated by a script you write in work/rankmd/. Never edit any
input. Return: path; at most 150 words; every "[lead to confirm]" item in one line.

## D4 ScopeWriter-OpusXHigh (worker-xhigh, opus): draft of reports/stage_e32b_holding_scope.md

Objective: write the holding-time scope file (prompt step F5; spec section 7) from the F5 outputs. Facts only, no
outcome; where a reading needs judgment, mark it "[lead to confirm]".
Inputs: briefs/F5_holding.json and .md (survivors' firm-independent rows, top-15 pairs' firm rows, IBKR rows),
work/F5/README.md (interpretations), briefs/F4_facts.md (firm rules: DLL, MLL, flat-by-close, overnight, news windows,
pauses), briefs/F2_firms.md, reports/E.33c_RETURN.md sections 1 and 7 (cost and trade-count facts only), econ32b.json
E_dir blocks when present (E_dir 30/120/240 for the top 15 come from a background run; leave a marked placeholder
table if they are not there yet), briefs/RULINGS.md.
Content: per survivor the cost-per-sigma curve k(h) for h = 1 minute to OC (overnight rows apart), the hit rate and
gross edge needed to break even and to net 1 tick, trades per day and year, e80 over discovery (G3 and G3+G4) and
test; per top-15 pair the same with c_f (each firm's fee in ticks), the prop-rule limits by horizon (DLL and MLL
against sigma_h, flat-by-close and the latest start, news windows, pauses such as ZM's 07:45-08:30 CT break), the
recommended band B with its reason (where k flattens, where power and the prop rules bind) and the verdict on the
user's prior (holds / partly / fails, spec 7); the overnight hold (which firms allow it, margin, rules) beside the
intraday rows; the IBKR rows; a closing section that tests the user's prior across all pairs and says plainly where
the facts disagree.
Output: reports/stage_e32b_holding_scope.md (script-built tables in work/scope/ allowed). Never edit any input.
Return: path; at most 150 words; every "[lead to confirm]" item in one line.

## D5 RecsDrafter-OpusXHigh (worker-xhigh, opus): mechanical sections of R4 (after r3_score.py)

Objective: draft the parts of reports/stage_e32b_recommendations.md that follow from the files; the lead writes the
judgment parts (each case paragraph, the kill criteria, the priors with base rates, the non-prop recommendation and
the stop rule). Facts only; no outcome; no Databento call.
Inputs: briefs/r3_out.json and .md (r3_score.py on briefs/R2_combinations.json: C, Q1-Q7, ranks, R4 selection over
all venues and over prop venues only), briefs/R2_dossiers.md, work/R2/groundwork.json, briefs/R2_combinations.json,
briefs/F5_holding.md, briefs/F2_data_access.json and .md (owned, sealed, spent windows; MBO start; cost estimates),
the program's pre-registration structure (reports/stage_e32_briefs/ protocol files: grep the section headers first),
reports/E.33c_RETURN.md sections 1 and 7, reports/E.31_RETURN.md sections 1 and 7, reports/E.29_RETURN.md section 1,
briefs/RULINGS.md, spec section 8.
For each R4 build candidate (the top 5 distinct (product or pool, family) by best C, per spec 8.3; mark C < 2.00 as
weak) write:
(a) a fact table: best venue and band, C and Q1-Q7 with reasons, c_f, h_c, hit rates needed, K_year, K_disc, K_test,
    e80 discovery and test, the prop fit, the closed-line overlap;
(b) a pre-registration outline in the program's structure: families, labels or horizons, features, models (V43 ML
    rules where they apply), discovery and test windows, the trial count it adds to N (838 now) and the DSR hurdle at
    the new N, the selection rule, the sealed one-shot test;
(c) a data purchase plan: schema, symbols, date ranges for discovery and test, what is owned, sealed or spent, the
    approximate cost from the census (labelled estimates) and the exact Databento quote requests to obtain later
    (dataset, schema, symbols, start, end), with V51's data rule that 2024-03 onward stays closed unless the user
    approves it;
(d) candidate kill-criteria facts the lead can choose from (the power numbers, minimum detectable edges, prop-limit
    breaches by horizon).
Also: the best own-broker (ibkr) combination with the same table and plan.
Output: work/R4/draft_sections.md. Return: path; at most 150 words; anything that needs a lead decision.
