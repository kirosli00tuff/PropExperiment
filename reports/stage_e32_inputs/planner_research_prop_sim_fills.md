# Planner research: how prop-firm simulators fill limit orders (2026-10-26)

This is an external web research run from the planning chat. Treat it as
pointers to verify. Firm rules change often, so check every date.

## Firms, platforms and fill rules

- **TopstepX (ProjectX), Topstep's only platform.** The help centre (Order
  types, fills and slippage, 2026-09-16) says the market "has to trade
  *through* your price — not just touch it… Partial fills happen". This
  is trade-through, the rule E.31 used for its gate.
  - The Combine and XFA are simulated, with real payouts. The LFA is
    live by call-up only.
  - The API is not allowed on the LFA: "automated strategies are not
    possible at this time in the Live Funded Account".
- **Rithmic paper trading.** A Rithmic staff post on the Optimus Futures
  forum (2019-01-31) reports fills "when the market trades through your
  price and when the orders ahead of you in the queue… are depleted and
  there is quantity or opposite side order activity at your price
  level". That is an estimated-queue model. The wording is ambiguous on
  whether the two are alternative or joint conditions; confirm with
  Rithmic or the firm. Each account is simulated separately.
  - Used by Bulenox (Rithmic only; bots allowed if user-built), and by
    Tradeify and Lucid on their Rithmic routes.
- **Tradovate sim:** fill rule unpublished. Staff say it "tries to
  mirror" exchange matching; forum users report trade-through-like
  behaviour. Assume trade-through. Used by MFFU and the Tradovate routes
  at Tradeify, Take Profit Trader and Apex.
- **CQG sim:** fill rule unpublished. Lucid's CQG route uses it.
- **Market orders** fill at the top of book in these sims. For one
  contract that is close to live: about half the spread per fill.
- **Exploitation rules:**
  - Topstep bans queue-position farming in SIM, tight brackets, and
    orders outside the best bid or offer (2026-06-10). The last is
    ambiguous for resting limits deeper than the inside quote.
  - MFFU bans duplicate limit orders at one price and tight-bracket
    no-slippage farming.
  - Lucid bans microscalping (more than 50% of profit from holds of 5
    seconds or less).
  - Tradeify gates funded payouts on holds over 10 seconds.
  - Apex bans automation entirely. Take Profit Trader excludes automated
    seconds-scale systems.
  A minutes-scale directional bot is outside all of these thresholds.

## Implication (the planner's arithmetic, ZM, 1-tick spread, per fill against the mid)

- Market order: about -0.5 tick.
- Limit under trade-through (TopstepX, Tradovate assumed): about -0.97
  tick (E.31 model c, gross). About 0.5 tick worse than market per fill.
- Limit under a queue model (Rithmic, if it behaves as described): about
  -0.25 to -0.29 tick (E.31 models a and b, gross). About 0.2 to 0.25
  tick better than market per fill, so about 0.5 tick per round trip.

These are unconditional per-fill figures. A directional strategy also
pays an opportunity cost when a limit order fails to fill on a move in
its favour, and that cost must be measured, not assumed.
