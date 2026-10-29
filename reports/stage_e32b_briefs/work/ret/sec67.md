## 6. Open choices

Every choice the prompt left open, as decided and logged (full text and times: reports/stage_e32b_briefs/RULINGS.md
and the STATE file). Lead rulings made after the hash carry a declared variant, kept in the results when it changes
the top 5 (OC-14).

Sessions 1-2:
- OC-1 N = 838: the SCOPE line "N stays 538" is a V51 carry-over (V53 item 2, V56 item 1).
- OC-2 Universe = E.28's 47 codes; ES, MES and the other owned roots not added.
- OC-3 Databento MBO availability and prices from one DataAccess worker (V37 shared source), not from each reader.
- OC-4 Primary E is E.28's model (T 20, sigma_T = sigma_1); E_dir60 a declared variant, E_dir 30/120/240 reported.
- OC-5 Slippage allowance 0.5 tick a round trip (an assumption); variants slip0, slip1.
- OC-6 sigma_h is the SD of h-minute changes (the "typical absolute move" read as the RMS move); variant mad.
- OC-7 E.28's L1 >= 2.00 and no-zero gates not used; variant L1min2.
- OC-8 A satellite's D2 uses its leader's facts and D4 deducts 2: a deliberate double penalty; variants D2_own, sat1.
- OC-9 D2 d (research attention) by OpenAlex count terciles.
- OC-10 An own-broker venue (IBKR) in R2/R3 only, for the non-prop alternative.
- OC-11, OC-15, OC-16 Planned context wipes when the lead passed about 300k tokens: after session 1 (22:34), session 2
  (00:56) and session 3 (07:25); each resumed from the STATE file's RESUME HERE block.
- OC-12 The R2 dossiers by a DossierWriter worker, the Q1-Q3 ratings by a fresh CombinationScorer, R4 by the lead.
- OC-13 The program's own earlier measurements (RETURN files) admitted as file-path sources, labelled with windows.
- OC-14 Lead rulings after the hash each carry a declared variant, reported when it changes the top 5 (spec 5).

Session 4:
- OC-17 LR-Q3b's leg-level reading made reproducible as the sensitivity q3bleg (patch_v31_q3_lead.py mode;
  work/R2/r3_out_q3bleg.json reproduces the session-3 list).
- OC-18 RV1 S1 fixed in the scorer (the market-case tie-break, as ruled in session 2), not by amending the ruling.
- OC-19 ZL F09's P(edge) lowered from 0.07 to 0.05 for the G17 null on ZL; the ZL program's prior stays about 4%.
- OC-20 The EQ3 F08 pool's prior under 1% (about 1.5% at most with V31 narrowed and 2024-03+ data approved); its
  K_eff 1,305 uses the spec's rho 0.5 within a class and is likely optimistic for index futures at the open.
- OC-21 R2_dossiers_for_rating.md stays as rated; corrections go to errata (R2_dossiers.md, R2_Q_ratings.md) and to
  the R1 file; recommendations line "ZL in other families' closed lines" split under LR-Q3b (LR-OF).
- OC-22 The base rate is shown both ways: 4% over the 23 closed lines and 1/19 (about 5%) over the 17 with a
  registered outcome (RV2 N5).
- OC-23 Section 2 quotes git status --short by its line count and this stage's lines (the full listing is in the two
  checks files).
- OC-24 The session-4 wipe gap (07:28:40-08:40:31) and the usage-limit pause (01:56-03:10) are shown apart from work
  time; the lead's wait while econ pass 1 ran (04:09-05:24) is stage compute and counted.

Lead rulings (one line each; RULINGS.md has the text):
- Facts and volatility: LR-F3 (VolCoder's choices where spec 2 is silent); LR-S (spread qualification; RL-SMEAN);
  LR-D0 (21-day month scaling of quotes); LR-D1 (k ratio 0.9195, ES proxy; RL-KZM kept, it reorders the top 5); LR-D2
  (p per the spec text; RL-PBRIEF); LR-D3 (registrations are reads only for the windows their searches ran on);
  FT-1 to FT-11 (FactTable items); LR-S1e (HG's S = 1 kept; sourced -> u an erratum with no effect); LR-ATT (the score
  run reads a format-only copy of the attention file).
- Scoring: HoldingCoder's 12 and ScoreCoder's 14 readings (LR-SC; crude and natgas one asset class); LR-E1 (econ pass 1
  on every computable listed pair, 8 workers); LR-B1 (names-free blind brief); LR-DLL (no DLL on the modelled Topstep
  and Bulenox plans: the MLL is used); audit decisions (B1, B2, S2, S3 patched without relabelling; S4 left);
  rater 2's primary ratings used throughout, its alternatives run as RS-* sensitivities; rater 1 superseded; RS-MNQD6,
  RS-OWNONLY, RS-EQS2 added once MNQ was shown not to be a satellite; QM's exclusion by the double penalty is the
  intended OC-8 reading; no ZL S = 2.06 variant (cannot reach the top 5); LR-RV1S1.
- Holding scope: LR-F5-IBKR (own-broker band B = {h : G <= 1.10 min G}); LR-Q6d (own-broker daily risk and the USD
  6,000 (u) ceiling); news windows not band conditions; soft DLLs treated as hard; E_dir zeros a model property.
- Recommendations: LR-R1 (V38 closes the tested configurations; its umbrella sentence an evidence finding); LR-R2a-c
  (combinations, bands, energy class); LR-Q6p (lowest payout path per firm; ts150_v2 sensitivity); the
  CombinationScorer's flags (ZL F01 gated; MNQ F12 only without R1-14 H6 T3; V39 not read as closing USDA/NOPA drift);
  LR-Q3a (F01 on YM, MYM, RTY re-tests closed configurations: Q3 0); LR-V31 (read literally: no clean test window for
  YM or MYM; q3only sensitivity, D1); LR-ZLW (ZL keeps its sealed window; nozlw sensitivity, D2); LR-Q3b (F09 on RTY
  and ZL: Q3 1, family level; q3bleg sensitivity); LR-OF; the lead's own R4 text corrected twice (07:07:40 after the
  RecsDrafter's fact check; session 4 after RV2).

## 7. Decisions for the user (each with a recommendation)

- D1 V31's scope for YM (no variant on E.16's windows, no purchase of the fallback roots). Recommendation: keep it. The
  Dow's best family (F01) is closed and its next one (F08) has a prior of about 1.5%; narrowing V31 would make YM F08
  the top candidate (C 2.85) without raising that prior.
- D2 The ZL sealed window's single read (2017-05..2020-11, V56 item 1). Recommendation: assign it to the ZL program
  (F10 + F09 in one registration, made before any further ZL read) if a prior of about 4% is acceptable; otherwise
  stop the directional program now.
- D3 V31's cost-feasibility gate for discovery searches. Recommendation: state explicitly that a V51-style discovery
  search is admitted without a published expected gross and is judged instead by the power rule (K2); keeping the gate
  stops every primary candidate before any purchase.
- D4 Data from 2024-03 onward (V51). Recommendation: keep it closed unless the ZL program passes; it would only enable
  the weaker MNQ F08 and EQ3 F08 candidates (and RTY F09, now outside the R4), at a power of about 0.05 on the 13 unread
  months.
- D5 The next stage. Recommendation: if D2 and D3 are accepted, one pre-registration stage for the ZL program on the
  E.32 protocol's model, with a Databento quote for the ZL order-book data logged before any purchase (the census rate
  gives about USD 19 for the discovery window and USD 41 with the test window; a quote, not a price); if either is
  declined, apply the stop rule and close the directional program.
