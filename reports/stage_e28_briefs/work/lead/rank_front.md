# Stage E.28 Part A: the blind firm-contract ranking for limit-order strategies

Stage E.28, 2026-10-21 (PDT). Spec frozen and hashed at 02:14 before any lookup: reports/stage_e28_ranking_spec.md,
sha256 89347e972ee14f637f0504035750ed952dc999e4787d92394ff7decd5a499a5f. Lead rulings on the reading choices the spec
left open, written at 15:13 before any ranking output was read: reports/stage_e28_briefs/A3_lead_rulings.json, sha256
82581c92030d46643036383fe66f2755ffbf6f889f71782b39ccc3c7328fcc4e. Nothing was bought for any pair here; Part B buys
the pilot for the top pair's contract only.

## Result

**Top pair: Topstep x QG (NYMEX E-mini Henry Hub natural gas), S = 2.524.** Next four, none bought: 2. Topstep x QM
(E-mini crude oil, 2.484); 3. Tradeify x QG (2.452); 4. MFFU x QM (2.427); 5. Lucid x QG (2.424). The baseline MNQ
ranks 21st at its best firm (Bulenox) and 33rd at Topstep; its economics score E is 0 at every firm (break-even
gross edge above 2 ticks per trade in the limit case).

Why QG: its tick is large in dollars (12.50 USD) against fees of about 2 USD a round trip, so fees are about 0.16
tick per round trip; its one-minute volatility is about 1.26 ticks; and its loss limits leave about five median daily
ranges of room for one contract. Its weaknesses are thin liquidity (C3 = 1: a published ADV near 4,000 contracts a
day in 2026, about 11,000 in 2023) and a tick-constrained book (C2 = 2 by the proxy). Micro contracts score badly on
economics: their fees run to 2 to 4 ticks a round trip, so a 1-lot passive strategy needs a gross edge above 4
ticks per trade at most firms (A3_econ.md).

Robustness: QG is first in 7 of the 9 variants the scoring script reports. Without the big-move transfer to sibling
contracts (variant C4_no_transfer) Topstep x QM leads; with OC-1 off (no sibling-derived statistics at all) Topstep
x ZM leads. See the variant list at the end of the table section.

Canadian tax (one line, not scored): no CRA page names prop-firm payouts; on CRA's general definitions they would
most likely be business income reported with Guide T4002, and GST/HST registration applies above CAD 30,000 of
taxable supplies in four consecutive quarters; whether payouts from a non-resident firm are taxable supplies is
[unverified] (A2_platforms.md section 8). All five firms accept British Columbia residents (A3_facts.md).

## How the ranking was built

- Layer 1 facts: eight contract-family readers (A1_*.md/.json), the owned-bar statistics (A0_contract_stats.*), the
  fact table (A3_facts.json/.md, 47 candidates). Layer 2 facts: five firm readers and a platform reader
  (A2_firm_*.md/.json, A2_platforms.*), the firm-product matrix (A3_firm_products.json, 126 listed 50K pairs).
- Economics: E.19's funnel simulator (prop_econ/) with each firm's standard 50K plan mapped onto it, 20,000 paths per
  pair and case, every threshold confirmed on the 0.01-tick grid (A3_econ.md).
- Blinding: the qualitative criteria (C1, C6, R, A, F, Rel) were rated by a scorer that saw only masked sheets
  (A3_blind_ratings.*); the quantitative criteria come from the script (work/A3_facts/score.py, which refuses to run
  if the spec's hash differs).
- Verification: RankingReviewer-FableXHigh recomputed the table independently (reports/stage_e28_briefs/R_rank.md;
  section "Review" below).
