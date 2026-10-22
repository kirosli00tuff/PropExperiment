- D1. Keep the pilot and any first evaluation on QM alone. Recommendation: yes. With a QM-only edge, every basket
  raises QM's break-even at every firm and rho (setting ii, 0 of 80 cells better). A second contract belongs in the
  account only after its own edge is measured, and that is a separate pilot with its own spend.
- D2. If Stage E.30 fails QM (median daily volume below 1,000, V47 item 3), the basket question loses its anchor:
  every E.29 basket holds QM, and QM's sigma and range come from CL (E.28 OC-1). Recommendation: then rerun the E.29
  model with ZM as the anchor (B0' ZM alone, ZM + MGC, ZM + MNQ). This needs a new basket table (the module's BASKETS
  constant, e29_basket.py:77, fixes QM as the first member) and a new declaration. The run is about one hour of
  compute with no data read. Until E.30 reports, do nothing.
- D3. Whether to re-express setting (i) in per-trade sigma units (equal mu / sigma across members) in a later
  stage. Recommendation: not now. It answers a question only a measured second-contract edge can make relevant, and
  section 3.4 already shows the direction: with equal per-trade quality, B1 is the only candidate, and it moves the
  break-even only at Bulenox (by 0.02 to 0.07, from rho 0.25).
- D4. Whether MGC's high alone break-even (6.3 to 8.3 ticks at Topstep, Tradeify and Bulenox) changes E.28's L2 scores
  for micro contracts. Recommendation: no change. E.28 already scores those pairs on that break-even. E.29 only shows
  that the cause is the payout thresholds a one-lot micro cannot clear, not fees.
