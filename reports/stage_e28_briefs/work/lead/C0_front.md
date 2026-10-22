# Stage E.28 methods brief: what the program never used, what it would take, and whether it explains the failures

Stage E.28, 2026-10-21 (PDT). Lead: Opus 5.5 (xhigh). Readers: twelve opus workers at high effort. Review:
MathReviewer-FableXHigh (Part 5). No rule was tested, nothing was registered, no market data was read for this
brief, and N stays 538. This file is assembled by reports/stage_e28_briefs/work/lead/assemble_brief.py from the
files it names, so every section can be traced to its source file.

## Contents

- Part 0. Headline
- Part 1 (C1). Gap inventory: every method the program used, and what it never used
- Part 2 (C2). Deep dives on the methods it never used
  - 2.0 All verdicts in one table
  - 2.1 Stochastic calculus and continuous-time models (Ito, jump-diffusions, Ornstein-Uhlenbeck)
  - 2.2 Point processes: Poisson and Hawkes order arrivals
  - 2.3 Limit-order-book models and the mathematics of fill probability
  - 2.4 Stochastic optimal control, HJB, market making (Avellaneda-Stoikov, Gueant) and execution (Almgren-Chriss)
  - 2.5 Filtering: Kalman, particle filters, hidden Markov regimes
  - 2.6 Random-matrix cleaning, Bayesian shrinkage, information theory
  - 2.7 Fractional differencing, meta-labeling, purged CV, wavelets and spectral methods
  - 2.8 Machine learning on order-book data I: DeepLOB and later deep models
  - 2.9 Machine learning on order-book data II: order-flow imbalance, trees, labels, latency
  - 2.10 Single-contract versus pooled multi-contract models
  - 2.11 How top firms run the research process
- Part 3 (C3). Does the missing mathematics explain the program's failures?
- Part 4 (C4). The recommended method set and a draft design for the order-book ML search under V43
- Part 5. Verification: MathReviewer's findings, the rulings and the fixes

How to read it: Part 0 and Parts 3 and 4 are the lead's synthesis (about 15 pages). Part 2's deep dives are the
evidence. Each deep dive gives, for every method, the core idea, the key equations with every term explained, the
data it needs, what it estimates or decides, a worked example, a pre-registerable hypothesis from the pilot data,
compute needs, and the honest evidence at retail scale and latency. Each ends with a verdict table and an evidence
table of verbatim quotes from fetched full text (claims not verified from full text are marked [unverified]).

## Part 0. Headline

**The program did not fail for lack of mathematics.** Every return names costs, statistical power, data
granularity, prop-firm rules or data access as the binding constraint, and none names a missing method (C1 section 3; Part 3). The program asked
1-minute bars a question they cannot answer at retail cost: the robust patterns were worth about a tenth of a tick
against a round trip of about two ticks. The methods it never used (14 of the 19 listed topics, 5 more only in
part) almost all need event-time order-book data, which it never bought.

**Those methods matter for the new direction, but as measurement, not as alpha.** Eleven independent deep dives
agree that no method here is a source of edge on its own at retail latency. The deep order-book models report
accuracy, not net profit. The control-theory market makers give inventory discipline, not an edge. Hawkes direction
forecasts lose to a naive benchmark out of sample. What the methods do give is the arithmetic of a passive order:
the value of a resting 1-lot is P(fill) x (half-spread - adverse move after the fill) - fee. Fill survival curves,
markouts, arrival intensities, queue imbalance and depth-normalized order-flow imbalance are the tools to measure
and condition that value.

**The real risk is adverse selection at the back of the queue, and fees in ticks.** Every queue model predicts that
a slow order at the back of a FIFO queue on a large-tick contract fills disproportionately on adverse paths. On MES
the fee alone eats almost all of a martingale half-spread (C2_SDE section 7.1). The pilot (Part B of the stage) is
the cheapest test of that risk. The ranking (Part A) chooses the contract and firm where fees are smallest in ticks
and the flow least toxic.

**The recommended design (Part 4)** is plain and phased. Phase 0 is the pilot measurement. Phase 1 is one
contract, with a written and hashed protocol, a five-rung model ladder from a no-model baseline to a small
network, every rung counted into N, purged and embargoed CV by trade date, one test on a research-window purchase
under a registered read, and costs from the measured fill model under both the real-market rule and the firm's
simulated fill rule. Phase 2 is a partially pooled model on two or three matched contracts, tested on an unseen
one, run only after a Phase 1 pass. Phases 0 and 1 fit the laptop. Deep models need a rented GPU or a bigger
machine.
