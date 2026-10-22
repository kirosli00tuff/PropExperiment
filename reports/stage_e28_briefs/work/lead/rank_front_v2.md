# Stage E.28 Part A: the blind firm-contract ranking for limit-order strategies

Stage E.28, 2026-10-21 (PDT). Spec frozen and hashed at 02:14 before any lookup: reports/stage_e28_ranking_spec.md,
sha256 89347e972ee14f637f0504035750ed952dc999e4787d92394ff7decd5a499a5f. Lead rulings v1, written at 15:13 before any
ranking output was read: reports/stage_e28_briefs/A3_lead_rulings.json (sha256 82581c92030d4664...). Lead rulings v2,
written at 16:36 after RankingReviewer-FableXHigh and after the v1 top pair was known:
reports/stage_e28_briefs/A3_lead_rulings_v2.json (sha256 f99b6e9f63de7f22...). This file is the v2 (final) ranking;
the v1 table is kept as reports/stage_e28_briefs/A3_ranking_table_v1.md. Nothing was bought for any pair here; Part B
buys the pilot for the top pair's contract only.

## Result

**Top pair: Topstep x QM (NYMEX E-mini crude oil, 500 barrels), S = 2.484.** Next four, none bought: 2. MFFU x QM
(2.427); 3. Tradeify x QM (2.415); 4. Bulenox x QM (2.388); 5. Lucid x QM (2.353). All five are the same contract,
so the one-contract pilot (QM, mbp-1) informs all of them. The baseline MNQ ranks 14th at its best firm (Topstep)
and 15th at Bulenox.

Why QM: a 12.50 USD tick against fees of about 3.4 USD a round trip at Topstep (0.27 tick a round trip); a break-even
gross edge of 0.32 tick per trade in the limit-order case and 1.32 in the market-order case; Layer 1 score 2.40
(C1 2, C2 3, C3 1, C4 3, C5 4, C6 2). Its weaknesses: thin liquidity (C3 = 1), and its price statistics are not
observed but derived from CL under OC-1 (sigma_1m 2.52 ticks = CL's 6.30 x 0.01 / 0.025).

How the top pair changed (v1 to v2). Under v1, Topstep x QG led (S 2.524). RankingReviewer's RR-01 (a conditional
BLOCKING) noted that every C1(b) evidence field for QG (masked C40) was UNKNOWN while the blind scorer rated it
"medium"; the spec says "Unknown counts as high". Ruling v2 RR-01 applies that sentence literally where every field
is UNKNOWN (only C40 qualifies; confirmed by DeltaReviewer-OpusXHigh, R_delta.md), which drops QG's L1 to 1.85, below
the 2.00 gate. The other v2 rulings (RR-03 grain C6 cap, RR-04 Topstep R by size, RR-05 Lucid fee u-rule) reorder
ranks 6 and below and do not move the top pair. All four were written after the v1 top pair was known; RR-01 is the
literal reading of the spec for a candidate with no evidence, and leaving partly evidenced ratings as rated is a choice
(R_delta.md section a).

Robustness: QM pairs hold ranks 1 to 3 in every variant the script reports except two: under the v1 rulings
Topstep x QG leads (Topstep x QM second), and with OC-1 off (no
sibling-derived statistics) QM drops out of the top five and Topstep x ZM leads (S 2.312), followed by MGC pairs.
QM's place therefore rests on the CL-derived statistics; the pilot measures QM directly and is the check on that
assumption. Under C4_no_transfer, C4_conservative and C6_as_rated, Topstep x QM still leads (S 2.409).

Canadian tax (one line, not scored): no CRA page names prop-firm payouts; on CRA's general definitions they would
most likely be business income reported with Guide T4002, and GST/HST registration applies above CAD 30,000 of
taxable supplies in four consecutive quarters; whether payouts from a non-resident firm are taxable supplies is
[unverified] (A2_platforms.md section 8). All five firms accept British Columbia residents (A3_facts.md).

## Reviews

- RankingReviewer-FableXHigh (R_rank.md): independent recomputation exact (0 mismatches over 47 candidates and 126
  pairs; economics stable to the seed). 1 BLOCKING (RR-01, conditional), 3 SHOULD FIX (RR-03, RR-04, RR-05), 9 NOTE.
  All four applied in rulings v2.
- DeltaReviewer-OpusXHigh (R_delta.md, E.28b; Fable was not available on the Pro plan): recomputed the v2 top 10
  with its own script (work/REV_delta/rd_rank_recompute.py); top pair and next four confirmed; each v2 ruling applied
  as written. Not finished by it: a field-by-field v1/v2 diff, the rank-10 tie against the tie rule, E for the 37
  rows with a non-numeric input.

