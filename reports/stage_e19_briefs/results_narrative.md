# Stage E.19 results: what the Topstep Combine-to-XFA funnel is worth to the user, in cash

Lead synthesis (Opus 5.5 xhigh), 2026-10-10, written against docs/prompts/STAGE_E.19.md. Numbers come from
reports/stage_e19_results.json (prop_econ/report.py: 780 grid jobs, 4,464 records, settings fingerprint
d4644acce4988b94; 20,000 attempts, 20,000 XFAs, 20,000 cycles and 20,000 campaign replications per configuration).
The model is reports/stage_e19_briefs/sim_spec.md with the lead decisions L-1..L-20 (reports/stage_e19_STATE.md); the
rules are reports/stage_e19_rules.json (Topstep help centre and terms, fetched 2026-10-10). Fable review:
reports/stage_e19_review_rules.md (rules, terms) and reports/stage_e19_review.md (model, recomputation); rulings in
reports/stage_e19_rulings.md. This is an economics model, not an edge test: N stays 480.

## 1. The answer

**At zero edge the funnel is negative expected value for the user, at every account size, payout path, pricing path,
DLL choice and sizing, under every sensitivity run.** The best zero-edge case is 50K, Standard payout path, Standard
pricing, DLL off, f = 0.25: **-$250 per cycle (SE $7 given the simulated pools, about $9 with the pools' own
sampling error, ER-1)**, i.e. -$31 per Combine purchase; 100K -$1,063, 150K -$2,696.
Without the $14.50/month API fee the 50K figure is -$94. Thin (normal) tails flatter it to -$179; a long-only bot
makes it worse (-$294). Inside the policy band (f <= 0.25) all 1,500 zero-edge records are negative (EconReviewer, ER-4). Outside it, the
only zero-edge cells that come out positive are at f = 0.50 with the DLL (+$27 per cycle at 50K Standard, +$34 with
Back2Funded), and the reviewer's independent shocks give +$2.5 (SE 10) and -$16 (SE 15) there, so their sign is not
established (ER-14): at best, sizing that breaches fast (the account-stacking pattern Topstep prohibits) lifts the
zero-edge funnel to about break-even. Without the API fee one product-specific
case is also slightly positive (integer MNQ contracts on 50K Consistency, +$21 to +$67). What the sign depends on:
at a net Sharpe of exactly 0 (a gross edge that just covers trading costs) 50K is about break-even at f = 0.25 (-$8
Standard, +$3 Consistency), so at 50K the loss comes from trading costs and the API fee; at 100K (-$559 / -$509) and
150K (-$1,672 / -$1,500) the funnel loses even then.

A "cycle" is one Combine subscription from purchase, through every reset until a pass (cap 60 attempts), to the end of
the funded XFA it produces; cash out = Combine purchases (monthly price, rebills, paid resets), the activation fee and
the API subscription; cash in = 90% of the XFA payouts.

Why zero edge loses: (1) zero gross edge is a negative net edge: the D8 round trip costs a net Sharpe of about -0.5 at
one round trip a day and -1.5 at three (T3's effective-Sharpe table); (2) the Combine pass probability is low (0.175
at 50K, 0.13 at 100K and 150K, at f = 0.25) and every month in the Combine is billed; (3) the XFA's value is capped
by the loss Topstep absorbs: a zero-edge funded 50K XFA pays the user $447 on average (Standard path) and a 150K one
$926, less the $149 activation fee, while getting one costs 8 (50K) to 16 (150K) Combine purchases.

**Break-even edge** (net annual Sharpe after costs at which the cycle mean crosses zero, best band f, DLL off,
Standard pricing): 50K Standard path 0.02, Consistency path below 0 (+$3 at a net Sharpe of exactly 0); 100K 0.52 /
0.34; 150K 0.86 / 0.54. In gross terms add the cost drag: about +0.5 at one round trip a day. A bot therefore needs a
real gross edge of roughly a Sharpe of 0.5 (50K) to 1.0-1.4 (150K) just to break even on the funnel.

**Best size and path:** 50K. At a net Sharpe of 0.5: Consistency path +$391 (f 0.20; DLL off), +$477 with the DLL
(f 0.25), and +$692 / +$906 with Back2Funded reactivations on; Standard path +$278. 100K at 0.5 is positive on the
Consistency path (+$263) and on the Standard path only with Back2Funded (+$117); 150K is negative on the Standard path
even at a net Sharpe of 0.5 (-$697; -$461 with Back2Funded). The No Activation
Fee pricing path is worse everywhere except a few DLL-on 150K cells.

**Cash targets** (five accounts at most, five independent slots, best band f, DLL off, Back2Funded off, API fee in):
to withdraw $5,000 at zero edge (50K Standard) takes 112 Combine purchases and $7,918 of fees with 50% probability
(164 and $11,499 with 80%), about 570 trading days; $10,000 takes 202 / 276 purchases and $14,366 / $19,390. At a
net Sharpe of 0.5 (50K Standard): $5,000 in 51 / 76 purchases, $4,052 / $5,934 of fees, 255 / 383 trading days;
$10,000 in 86 / 121 purchases, $6,900 / $9,530. At 1.0: $5,000 in 36 / 53 purchases, $3,036 / $4,409. So even with a
good edge, roughly 60-80 cents of fees go out for every dollar withdrawn on the way to the first $5,000.

**Risk of losing every fee paid** (a cycle with no payout at all): 0.48 (50K Standard) to 0.74 (Consistency) at zero
edge; 0.36 / 0.54 at a net Sharpe of 0.5. The Consistency path pays more on average but more cycles pay nothing.

**Terms:** Topstep allows bots on the Combine and XFA through the TopstepX / ProjectX API (not on a Live Funded
Account), forbids a VPS (the bot must run on the user's own machine), forbids cross-account hedging and trading the
full position size into scheduled news, and names "account stacking" and "excessive purchases of Trading Combines or
Resets" as prohibited; it publishes no threshold. Expected cash rises with aggressive sizing (the band optimum is f 0.25 in
176 of 192 cases, and 0.35 / 0.50 beat 0.25 at zero edge): the structure rewards exactly what the terms forbid.

## 2. Model in brief (Tasks 2 and 3)

- Rules: 214 sourced rules for 50K / 100K / 150K (reports/stage_e19_rules.md), 7 UNSOURCED and 3 CONFLICT, each run at
  every reading that can be simulated. Combine: monthly price $49 / $99 / $199 (Standard pricing; $95 / $149 / $229
  No Activation Fee), resets at the same price, rebill every 30 days with a reset credit, profit target $3,000 /
  $6,000 / $9,000, end-of-day trailing MLL $2,000 / $3,000 / $4,500 locking at the start balance, best day < 55% of
  total profit, at least 2 days. XFA: $149 activation (Standard pricing), trailing MLL locking at $0 and set to $0 after
  the first payout, scaling plan by balance, Standard path (5 winning days of $150+) or Consistency path (3 days,
  best day <= 40%), payouts up to 50% of the balance capped at $2,000 / $3,000 / $5,000 (Standard) and $3,000 / $4,000
  / $6,000 (Consistency), doubled with the DLL, 90/10 split, $125 minimum, Back2Funded $599 / $699 / $829 before the
  first payout, at most 5 XFAs, discretionary Live Funded call-up (no API on a Live account).
- Returns (reports/stage_e19_returns_summary.md): day-session holds of NQ, CL, GC, ZN, 6E from the owned E.12 training
  stores (2019-05-06..2024-02-29; 1,203 to 1,222 dates each), demeaned per path, a random direction each day, 5-day
  block bootstrap pooled over the five paths (fat tails: excess kurtosis 1.9 to 5.6, 0.08% to 0.66% of days beyond 4
  sigma; worst intraday excursion from the 1-minute bars), against a normal model with a Brownian-bridge intraday
  minimum. Vehicles: the micro when the day's risk is below one full contract's sigma (MNQ, MCL, MGC, M6E; ZN has no
  micro). Costs: the D8 day-session round trip, at 1 or 3 round trips a day; D8 cost per unit of daily sigma 0.005
  (NQ) to 0.051 (M6E), so zero gross edge is a net Sharpe of about -0.5 (1 round trip) or -1.5 (3).
- Sizing: daily risk f x D (D = distance to the trailing MLL) in fractional contracts, at least one contract, cut to
  the lot limit or scaling tier; f in 0.05..0.25 (policy band) plus 0.35 and 0.50 as diagnostics. Edges: zero gross
  drift, or a constant drift giving a net Sharpe of 0, 0.15, 0.3, 0.5, 0.75 or 1.0 after costs.
- Wallet: payouts are requested at the first eligible morning, at the largest amount the policy allows (keep-D 0.5 as
  a sensitivity); the API subscription ($14.50 per 21 trading days) is a cash-out; transfer fees $0 (Wise).

## 3. Sizing: every grid point and the in-simulation optimum

The table below and T2 (appendix) give the cycle mean net at every f and edge; T6 gives the in-simulation optimum f
per rule set and edge, with its SE and the paired SE of its gap to the runner-up. All SEs in this report condition on the simulated 20,000-path pools; the
pools' own sampling error multiplies them by about 1.3 (50K) to 2.5 (150K) at zero edge (ER-1), which changes no sign,
ranking or break-even. The optimum sits at the top of the policy band (f 0.25) in 176 of 192 rule-set-edge cases; the 16 exceptions are all on the Consistency path at a net Sharpe of
0.5 to 1.0 (best f 0.15 or 0.20). On the Standard path the mean keeps rising past the band (f 0.50 beats 0.25 in every Standard-path cell): fees are
priced by time and the downside is capped, so faster resolution pays. On the Consistency path the optimum is interior
once the edge is positive (f 0.15 to 0.35; ER-5). It is an in-simulation optimum: the gaps to f 0.20 are many SEs wide at zero edge
($166 to $2,066), but at a net Sharpe of 0.5 on 50K Consistency the best two f differ by $7 (SE 10), within noise.
Small f is ruinous on the larger accounts because a slow Combine is billed every month for years (150K at f 0.05:
-$52,841 per cycle: 248 purchases over a mean cycle of 5,464 trading days, a cycle no one would run to the end): the subscription price, not the trading, dominates.

## 4. Sensitivities (T5, appendix)

- Tail model: normal tails make zero edge less negative by $34 to $230 per cycle (50K -179 vs -250); at a net
  Sharpe of 0.5 or 1.0 the difference is mixed and mostly within 2 SEs. Fat tails do not flip any sign.
- Direction long only (index skew kept): $31 to $325 worse at zero edge.
- Cost wall (E.10's worst-bucket round trip): $36 to $975 worse at zero edge (largest at 150K, 3 round trips).
- Integer contracts on a single product: much worse for 6E, CL and GC (the micros cost 0.023 to 0.051 per unit of
  sigma per round trip, and rounding down cuts the risk below f x D, slowing the Combine); NQ (MNQ) is close to the
  pooled headline; ZN mixed. On 50K, NQ and ZN trade one contract at every band f (ER-12), so their results do not
  depend on f. Product and vehicle choice matter as much as sizing.
- Payout policy keep-D 0.5 (leave at least half the MLL in the account after a payout): better whenever there is an
  edge (50K Standard, net Sharpe 0.5: +$487 vs +$278; 150K Standard at 1.0: +$1,690 vs +$303); neutral at zero edge.
- Live Funded call-up right after the 1st payout: -$132 to -$1,048 per cycle; after the 3rd: -$12 to -$281.
- UNSOURCED scaling-plan boundary and the CONFLICT Combine-consistency boundary: no effect (0 in every cell).
- Post hoc: ACH or wire at $30 per payout costs $10 to $42 per cycle; the voluntary-close payout at the horizon adds
  at most $16 (few XFAs live that long); the API fee is $109 to $311 per cycle (at its $29 list price, double that);
  five copy-traded accounts multiply both the gains and the losses by about five (50K, net Sharpe 0.5: +$1,826;
  zero edge: -$628), but copied accounts breach together, which Topstep lists as a Responsible Trading Program
  trigger, so that figure is not repeatable.

## 5. Churn and the terms (reviewer finding RR-1, rule L-19)

Every configuration's Combine purchase rate is 0.79 to 1.90 per 21 Combine-phase trading days per account, so all
are "low" under L-19 (<= 2.0); a five-slot campaign buys 2.86 to 8.73 Combines per 21 trading days in its first year.
The label is partly definitional (ER-2): every 21-day rebill is a purchase and reset credits pay most resets, so the
rate has a floor near 0.8 to 1.0. Counting credit-paid resets too, the per-account rate stays at or below 2.0 inside
the band, and a five-account campaign makes about 4 to 5 purchases or resets per 21 trading days.
Topstep publishes no "excessive" threshold, so L-19 is the lead's reading, not Topstep's. The binding terms are
qualitative: sizing that repeatedly hits the MLL and moves on to the next account (account stacking), many Combines
or Resets in a short time, losing many XFAs quickly (the Slowdown path), several accounts hitting the MLL on one day
(the Responsible Trading Program), opposite positions across accounts, full position size into scheduled releases,
and a VPS. The cash rewards point toward f above the band; the terms point the other way.

## 6. Limitations

- One sizing fraction serves both phases; a faster Combine (larger f in the Combine than in the XFA) was not
  modelled and might cut the subscription drag; it is also the direction the account-stacking clause polices.
- Daily P&L is one day-session hold per day; real strategies trade fewer days and hold for less time, which raises
  the cost per unit of risk (the zero-edge cost drag here is a lower bound).
- Slots are independent; copy-trading or correlated products widen the distribution and trip the RTP rule.
- Discretionary rules (call-up, churn thresholds, payout reviews) are not modelled as random events; payouts are
  never denied in the headline (the forfeiture column in T8 shows the loss if they were).
- Prices exclude sales tax; the API is billed by a third party; a CAD bank adds Wise's conversion fee.
- Each cycle ends when its XFA ends; an XFA alive after 756 trading days is valued at 0 (a few at most).
