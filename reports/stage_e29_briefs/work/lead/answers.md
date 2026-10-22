The full tables (per firm: every basket, rho and edge setting, with reporting-point pass rates, P(any payout),
EV per cycle, cost per attempt and daily SD) are in reports/stage_e29_briefs/E29_tables.md (generated from
E29_cells.json, 228 cells and 7 alone records). The compact version below shows, per firm, the break-even and the
mu10K analogue ("threshold / x10K"), limit case, against B0. "*" marks a cell that beats B0 by the declaration's
section 7 rule. "n/a": setting (i) cannot be run because MNQ's alone break-even at Bulenox is above 12 ticks. Every
threshold was found by bisection and then grid-confirmed (A3_econ.md 2.4): 0 of 470 moved (section 5).

@@COMPACT@@

Market case (c + 1 tick spread per member), B0 against each firm's best basket (section 6 rule: Topstep B2, Lucid
B4, Tradeify B2, MFFU B2, Bulenox B3). In setting (ii), the basket's mu*_QM is higher than B0's at every firm and
every rho: +0.25 to +0.27 ticks at Topstep, Tradeify and MFFU, +0.12 at Lucid, and +2.09 to +2.26 at Bulenox. In
setting (i), k* is 0.83 at Topstep, 0.84 at Tradeify, 0.95 to 0.99 at Bulenox, 0.99 at Lucid and 1.00 at MFFU,
against B0's 1.00 (E29_tables.md, "Market case").

Topstep B3 position-limit sensitivity (MGC dropped on funded days at the 2-lot XFA tier). Setting (i): k* rises from
0.77-0.80 to 0.93-0.95, and x10K from 1.30 to 1.46-1.55. Setting (ii): mu*_QM falls from 0.94-0.98 to 0.87-0.90,
because dropping a zero-edge member removes its fees. Either way B3 stays worse than B2. No other basket meets a
binding limit at any firm (binding-limit log in E29_tables.md).

The account's daily SD at Topstep (USD, MLL 2,000) is 141 for B0. For the baskets at rho 0 / 0.75: B1 141 / 186,
B2 101 / 113, B3 119 / 167, B4 109 / 136. S / MLL is 0.05 to 0.09 throughout.

### 3.4 Answers

The lead adds one reading that the declaration did not fix and that is not a measurement: each member's per-trade
edge at the threshold, in units of its own sigma_1m (mu / sigma). In E.28's model, a member's alone break-even mixes
its fees with how well a one-lot of it clears each firm's payout rules. So "the same multiple of its own
break-even" can mean very different per-trade quality across members.

(a) Does any basket beat QM alone at realistic rho? Not in any sense that matters, and not in setting (ii).
- Setting (ii) (QM edge only, the others at zero): no basket beats B0 at any firm or any rho (0 of 80 cells).
- Setting (i) (every member at k times its own break-even): 27 of 76 runnable cells beat B0 by the section 7 rule.
  All 27 are at Topstep (B2, B3), Tradeify (B2, B3) or Bulenox (B1 at rho >= 0.25; B2, B3). The Topstep and
  Tradeify gains are large (k* 0.60 to 0.82 against 1.00), but every one of them contains MGC. MGC's alone
  break-even there is 6.37 and 6.34 ticks (about 1.2 sigma per trade). The reason is that a one-lot micro rarely
  clears the USD 150 winning-day threshold the payout rules need, not its fees (1.9 to 2.1 ticks). At k* = 0.60,
  B2 at Topstep therefore assigns MGC 3.82 ticks a trade (0.71 sigma) and QM 0.19 ticks (0.08 sigma). That is an
  artifact of the unit, not a benefit of combining. The basket wins because MGC is given a large edge that the
  combined account can finally collect. At Bulenox, B2 and B3 put MGC at 7.9 to 8.1 ticks (about 1.5 sigma).
- The one basket whose members carry similar per-trade edges at their own break-evens is B1 (QM 0.13 to 0.29
  sigma, ZM 0.18 to 0.34 sigma). It shows no benefit at Topstep, Lucid, Tradeify or MFFU (k* 0.98 to 1.02, against
  B0's 0.98 to 1.00), and a small one at Bulenox only at rho >= 0.25 (k* 0.98, 0.95, 0.93; the 0.98 is 2 steps
  from B0's 1.00, within seed noise, R_review item 9). B1 does lower the mu10K multiplier, by 7 to 17% at those
  four firms (for example Topstep 1.55 to 1.57 against 1.69, Tradeify 1.54 against 1.73, MFFU 2.13 to 2.29 against
  2.56) and by 1 to 3% at Bulenox.
- B4 (QM + MNQ): no benefit anywhere (k* 0.96 to 1.03, x10K higher than B0's at every firm where it runs). At
  Bulenox MNQ has no break-even within 12 ticks.

(b) At what rho does the benefit vanish? It does not vanish on the grid, because it never came from
diversification. The declaration's section 7 table, on the confirmed values (E29_confirmation.md), has no basket
whose flag turns off between rho 0 and 0.75: Topstep and Tradeify B2 and B3 and Bulenox B2 and B3 beat B0 at every
grid rho, Bulenox B1 starts to beat it at 0.25, and the other 50 basket-setting-firm lines never do (B4 at Bulenox
in setting (i) cannot be run). Across rho 0 to 0.75, setting (i) thresholds move by at most 0.05 at Topstep, Lucid, Tradeify
and MFFU. At Bulenox they move by up to 0.07, and they fall as rho rises: B1 goes from 1.00 at rho 0 to 0.93 at
0.75, and in setting (ii) from 1.58 to 1.47 ticks (B3 from 2.11 to 1.94). A higher rho means a higher daily SD, and in this funnel (fixed fees,
capped payouts, a trailing drawdown) extra variance near zero edge pays, as E.19 found. The account's SD is 5 to
9% of the 2,000 loss limit at every rho, so variance reduction from low correlation buys almost nothing at the
break-even. Where the measured price correlations sit (returns 0 to 0.16, ranges up to 0.40), the answer is the
same as at any other grid rho.

(c) Does adding a zero-edge contract ever help? No. In setting (ii), every basket raises QM's break-even at every
firm and rho: by +0.08 ticks (Lucid B4) up to +1.39 ticks (Bulenox B3 at rho 0). The mu10K analogue rises in every
cell too. Why: QM's 20 trades become 10 (or 7), and each zero-edge member pays its own fees on the rest, so QM must
earn the lost trades' edge and the other member's costs on fewer trades. The extra variance does not make up for it
at break-even, not even at Bulenox, where it narrows the gap as rho rises. This is the expected sign. The only
place a zero-edge member's removal "helps" is the Topstep B3 sensitivity: there MGC is dropped and its fees go with
it.

### 3.5 The ranking these results would imply (conditional on an edge no one has measured)

- The firm order of E.28's v2 ranking stands: Topstep QM, MFFU QM, Tradeify QM, Bulenox QM, Lucid QM. At every
  firm, B0 (QM alone) has the lowest QM break-even of any option when only QM has an edge (setting ii). That is the
  only setting a QM-only pilot can speak to.
- Conditional on a second contract having its own measured edge: the case for a basket rests on that edge, not on
  correlation. At Topstep and Tradeify, QM + MGC (B2) would come first if MGC carried an edge near 0.7 sigma per
  trade, an edge no short-hold strategy is known to have. With equal per-trade quality across members, QM + ZM
  (B1) is the only basket worth a look. It changes no break-even except at Bulenox (0.02 to 0.07 lower from rho
  0.25) and lowers the mu10K multiplier by 7 to 17% at the other four firms. QM + MNQ (B4) never helps.
- Implied order of options at the rank-1 firm (Topstep), conditional on edges at each member's own break-even
  multiple: B2 (k* 0.60 to 0.61), B3 (0.77 to 0.80), then B1 and B0 level on break-even (1.00 to 1.02 against
  1.00; B1 has the lower mu10K multiplier, 1.55 to 1.57 against 1.69), then B4 (0.98 to 1.03, but mu10K 2.01 to
  2.04). Under a QM-only edge (setting ii, rho 0): B0 (mu*_QM 0.32), then B4 (0.45), B2 (0.49), B1 (0.79), B3
  (0.94).
