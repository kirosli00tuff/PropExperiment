The full text is V2.12 of docs/STAGE_E_ML_V2_DESIGN.md. Here each decision comes with the lead's
recommendation first.

1. **The Gate 0 bar, the cost-gate reading and tau (one coupled decision).** Recommended:
   - the gross reading (hurdles 1.5c / 2c / 3c, tau 0.167);
   - Gate 0 at 1.5c on the top-20% confident trades, t >= 3, Holm 0.05 with family A included
     (operative z about 3.57), >= 30 trades.
   Alternatives: the literal F7 reading as built (2.5c / 3c / 4c, tau 0.10), or a pre-cost Gate 0
   with no cost multiple.
2. **The phase-1 subset rule.** Recommended as written: the liquidity tier (median ADV), then
   c / sigma_proxy, then a cluster round-robin, greedy to the budget.
3. **The volatility proxy.** Recommended: the CME maintenance margin (it reads no window of ours).
   Use the frozen E|m_1| only if CME's pages block the fetch.
4. **Phase-1 scope.** Recommended: the training window only (more products for Gate 0), with the
   holdout-2 chunks bought in phase 2 for the traded products. This departs from V1.
5. **The 2010 extension.** Recommended: take the free quote at the freeze, and buy only after a
   Gate 0 pass, with a D4 start-rule amendment. It is the only lever that makes a Sharpe near 1
   detectable (minimum detectable Sharpe 0.80 vs 1.37).
6. **The decision clock.** Recommended as written: three times by rule, holds of 60 min, 120 min
   or to the flatten.
7. **The roll-blackout rule.** Recommended as written: the own roll date excludes rows; a signal
   leg's roll date makes its features not applicable.
8. **The signal library.** Recommended: all 54 families and G1-G19, with the ports pooled. Also
   build the EC-K9 announcement calendar for 2019-2024 from official pages in the freeze session,
   so K9-anncday-01 can enter.
9. **The research-window warm-up.** Recommended: skip the sealed gap.
10. **The grid sizes.** Recommended as written: 3 ridge, 2 LightGBM, 3 k and 3 horizons, 45 in all.
11. **Sizing constants.** Recommended as written: 0.10 x D, 0.25 x D, the daily budget, the 2b band
    and one extra tick per side beyond q_c. Also add the release-window rule: no new entry near a
    release while open lot-equivalents exceed half the tier.
12. **The 150K parameters.** Recommended: the freeze session reads Topstep's 150K MLL (V22 says
    $4,500) and the XFA scaling schedule. Until then every 150K figure is a lower bound.
13. **Kill-switch thresholds.** Recommended as written:
    - KS1: -0.30 x D_open;
    - KS2: 0.50 x MLL, half size;
    - KS2b: 0.25 x MLL, halt;
    - KS3: 5 losing dates;
    - KS4: 3 standard errors over 40 dates;
    - KS5: 2 and 5 minutes.
14. **The success criteria.** Recommended:
    - training window: median-path t >= 3, DSR > 0.95 at N_total, PBO < 0.5, ruin <= 10%
      (breach or the KS2b level), >= 30 trades per product, with the Sharpe reported against the
      band;
    - research window: a screen (mean > 0, t >= 1.0, >= 30 trips);
    - the 1.5 x slippage sensitivity as a must-survive condition in the holdout-2 registration;
    - paper trading: 40 dates, costs within 1.25 x D8.
    Alternatives: keep Sharpe >= 1.5 as a gate; a Holm-level research bar (t >= 2.58); eligibility
    on a majority of splits instead of all.
15. **The payout policy.** Recommended: request at the first eligibility the largest amount that
    leaves D >= 0.5 MLL. Choose Standard or Consistency, and DLL on or off, from the payout
    simulation once real data exist.
16. **Deployment.** Recommended: (a), a frozen ridge model with weights hashed and never retrained
    live. In effect it is a plain linear rule. It replaces the 2026-09-24 "plain rules" decision;
    Topstep's AI clause (D9.9) may need a support answer.
17. **The compute host.** Recommended: the ThinkPad. The full grid takes under 1 hour at 28
    products, and about 2.5 h with the 2010 extension.
18. **The Live Funded risk (F12).** The API is banned on Live Funded, so the bot runs on XFAs only,
    and a call-up ends automated trading on that account. Recommended: plan as V22 does (XFA
    payouts fund a personal account) and decide before the first funded account whether to accept
    a call-up.
19. **The purchase plan and the cap raise.** Recommended:
    - phase 1 spends acct-1's headroom (about $28.41) first, then acct-2's $125;
    - the purchasing session raises ACCOUNT_2_CAP_USD to about $249.67 (V19) in its own manifest,
      and logs a fresh quote before buying;
    - the same session fixes C-10 (docs/ACCESS.md:9 and key.strip() in data/config.py) in that
      manifest.

**What the freeze session needs:**
- the decisions above;
- the CME margin table, or the E|m_1| choice;
- Topstep's 150K MLL, scaling schedule and reset price;
- a fresh phase-1 quote under the subset rule;
- the EC-K9 calendar for 2019-2024 (if item 8 is accepted);
- the design and the ml_route_v2/ build hashed into a v2 freeze manifest;
- the program N read from the ledger;
- a DECISIONS entry for the route's unused research-window Holm slot.
