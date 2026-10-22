# C3 (lead draft): does the missing mathematics explain the program's failures?

Draft by the lead, 2026-10-21 02:31 PDT, from C1's inventory (reports/stage_e28_briefs/C1_inventory.md sections
2 to 4) and the returns it quotes, with the C2 deep dives' evidence on latency, decay and fees (added 05:18 PDT).

## Answer

No. Costs, statistical power and data granularity were the binding constraints: by C1's tally POWER is named in
seven returns, COST in five and GRAN in three, and the cost gap is the one no estimator closes. The missing mathematics is a consequence of the data decision, not an independent cause. Almost
every method the program never used needs event-time order-book or trade data. The program never had that data
outside two sealed MES days and five cost-calibration dates per contract. On the data it did have, the methods it
used were adequate to show that there was nothing to find at retail cost.

## The evidence, item by item

1. **No return names a missing method as the cause of a failure.** C1 tabulates the binding constraint each
   return names (C1 section 3). COST (a gross edge below the round trip) appears in D.1b, D.1d, E.12, E.17 and E.20.
   POWER appears in D.1, D.1e, E.13, E.14, E.21, E.23 and E.25. GRAN (granularity) appears explicitly in D.1, D.1b
   (C-H4) and E.25. PROP and ACCESS appear in D.1g, E.13, E.15, E.19, E.21 and E.25. In C1's words: "No return names a missing
   mathematical method as the cause of a failure".

2. **The cost gap was an order of magnitude, not a modelling margin.** D.1b: "every statistically robust
   directional pattern is worth about 0.1 tick per trade, against a 2.1-tick round-turn cost" (progress.md:902), and
   "every pattern large enough to pay for costs is statistically indistinguishable from noise" (progress.md:903).
   E.20: "a published effect that is sized gross in history is below the round trip at retail cost in recent data"
   (E.20_RETURN.md:562-564). A better estimator of the same 1-minute-bar signal cannot close a gap of 20 times.

3. **Where more flexible models were used on the same data, they failed as well.** E.12's Gate 0 (ridge and
   LightGBM over 64 features, 27 products, 4.8 years) found no gross edge at 1.5 times cost after Holm: "the answer
   is no. The best pair (NG h60, t 2.51) is not evidence after Holm" (E.12_RETURN.md:683-685). E.20's pooled search
   failed on cost (E.20_RETURN.md:562-564). Non-linear models had their chance on the bar data and found nothing
   that pays the round trip.

4. **Several "never-used" methods reduce, on 1-minute bars, to things the program did test.** On bar closes an
   Ornstein-Uhlenbeck fit is an AR(1) reversal rule. Family C's high-frequency reversals failed on hit rate and cost:
   "all three trials fail on win probability alone (p ≈ 0.36, below the grid's floor of 0.40)" (progress.md:626).
   Hidden Markov regimes stand where the deterministic volatility-regime gates stood (D-H1, the VXN bands, G9; C1
   section 2). Fractional differencing and wavelets re-express the same price series; neither adds information that
   the 64-feature library lacked. These methods would have changed the parametrization, not the information set.

5. **The powered nulls were powered.** D.1f's MES null: "Every one of the 100 members outside C6 has its one-sided
   95% upper bound below ε = 34 net ticks per micro per day with achieved null power of at least 0.997"
   (progress.md:2094). A method cannot find an effect that a powered test bounds below the cost of trading it.

6. **The underpowered nulls are limited by history, not by technique.** E.21: "A Sharpe of 0.5 would need about 25
   years of data to pass" and "Databento's GLBX.MDP3 has nothing before 2010" (E.21_RETURN.md:19-20; :650). E.23:
   "at a true net Sharpe of 0.5, no window the program owns supports a discovery read AND a confirmation read with
   power 0.2 each" (E.23_RETURN.md:678-679). Bayesian shrinkage or a Romano-Wolf step-down would change the bar
   modestly. They do not create the decades of data that slow, low-Sharpe strategies need. The one place better
   statistics would have mattered is the size of the multiple-testing penalty at N = 538, and even there the best
   pre-Holm result (NG h60, t 2.51) is below the program's t > 3.0 bar on its own.

7. **The data decision was deliberate, and it is what kept these methods out.** V22 chose "more history, not finer
   data" (docs/DECISIONS.md:394-395). The ML v2 rules fixed "F13 no tick or order-book data | V2.1: one-minute OHLCV
   only, in every phase" (E.11_RETURN.md:298). The one order-book study planned, D.1g (a queue-position fill model on
   181 purchased MBO days), was closed unrun because TopstepX fills a resting limit only on a trade-through and
   Topstep prohibits exploiting sim queue position (docs/DECISIONS.md:30-46). So the program could not price passive
   execution, which is the one lever that changes the cost arithmetic.

## Where the missing mathematics does matter: the new direction

The methods that were never used matter for what comes next, not for what failed. The cost side is where they
change the arithmetic. A passive order does not pay the spread, but it is filled more often when the price moves
against it (adverse selection), and it waits in a queue. Pricing that trade-off needs the fill-probability and
queue mathematics (Cont-Stoikov-Talreja, queue-reactive models, survival models of execution time), arrival-intensity
models (Hawkes) and, if any signal is found, a quoting policy (Avellaneda-Stoikov and Gueant). None of these can
run on 1-minute bars. All of them can run on the pilot's order-book data.

Three honest limits, all already on the record:
- **Latency.** E.25: "information is priced within one to five seconds on ES, NQ, ZN and CL"
  (E.25_RETURN.md:330), below what a retail system in Vancouver can act on reliably. Directional order-flow
  prediction at sub-second horizons is the territory where published order-book ML works, and it is the territory
  the program cannot reach. Methods that work at retail latency must work at horizons of seconds to a minute, where
  the published predictability is much weaker. The deep dives agree: deep OFI's effective horizon is about two
  price changes, "milliseconds to half a second", and its one retail-style replication failed in a forward test
  because of processing delay (C2_OFI section 13); part of the Hawkes excitation in futures order flow, the fast localized kind
  that market orders produce, acts at about 0.3 ms (C2_Hawkes, after Bacry, Jaisson and Muzy 2016). The one feature with published evidence of keeping most
  of its value at 100 ms is top-of-book queue imbalance, in an execution use on 5-year Treasury notes (C2_OFI,
  Stoikov and Waeber).
- **Fees on a micro.** For MES the deep dive's arithmetic leaves almost nothing even before adverse selection: a
  passive round turn earns 1 tick ($1.25) if the mid is a martingale, against a $1.22 round-turn commission, "$0.03
  per round turn: 0.012 tick per fill" (C2_SDE section 7.1). Adverse selection of 0.05 tick per fill already turns it
  to -$0.095. Fees measured in ticks are therefore a first-order criterion for the contract, which is why Part A
  ranks firm-contract pairs by fees in ticks and not by contract alone.
- **The venue's fill rule.** E.25: "under TopstepX trade-through fills most passive fills are adverse" and
  "trade-through fills leave at most about 0.7 MNQ ticks of passive saving per side" (E.25_RETURN.md:25-26,
  :332). A firm whose simulator fills only on trade-through takes away most of what passive execution could save.
  This is why Part A scores each firm's sim fill rule.

So the methods brief does not say the program failed for lack of sophistication. It says the program was asking
1-minute bars a question they cannot answer at retail cost. The next question, whether a passive 1-lot order at the
back of a real CME queue earns more than its adverse selection plus fees, needs new data and the mathematics in
section C2, and the pilot measures exactly that.
