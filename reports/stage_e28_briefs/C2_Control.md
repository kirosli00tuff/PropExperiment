# C2 Control: stochastic optimal control, HJB, market making and execution

Stage E.28 methods brief, deep-dive section C2. Worker: C2_Control (Opus 5.5). Written 2026-10-21 from
02:30 PDT. Pages: reports/stage_e28_briefs/pages/C2_Control/ (log.tsv lists every fetch). Scripts and
their outputs: reports/stage_e28_briefs/work/C2_Control/ (C2_examples.py, C2_examples_out.txt,
C2_threshold.py, C2_threshold_out.txt). No market data was read. Every number in a worked example is
either an assumption (labelled "assumed") or arithmetic on one; none is a measurement of MES or ES.

Conventions used throughout
- Prices in ticks, time in seconds, unless stated. MES tick = 0.25 index points = USD 1.25 (CME page,
  cme_mes_specs_wayback.txt: "The Micro E-mini S&P 500 futures contract is $5 x the S&P 500 Index and has
  a minimum tick of 0.25 index points"). Round-turn costs are the program's own table
  (rules/products.py line 154: MES 122 cents, line 153: ES 378 cents; source named there as Topstep's
  commission table). I did not re-verify those costs in this section.
- s = mid (or reference) price; x = cash; q = signed inventory in contracts; t = time; T = horizon;
  delta^b = s - p^b (distance of my bid below mid), delta^a = p^a - s (distance of my ask above mid);
  lambda(delta) = Poisson rate at which a resting order at distance delta gets filled; gamma = risk
  aversion; sigma = volatility of the mid in ticks per sqrt(second).
- "[unverified]" marks a claim I could not confirm from fetched full text, with the reason.

Bottom line up front (details and sources in the sections): these models are inventory-risk policies
built on an assumed exogenous fill process. Where the fill process is independent of future prices (the
A-S and GLFT assumption), the spread is free money and the control only trades mean for variance. On
real large-tick books, fills are correlated with adverse price moves, queue position decides whether a
fill happens at all, and the tick grid collapses the continuous optimal quote onto two or three discrete
choices. For a 1-lot MES trader at tens of milliseconds, the published evidence and the fee arithmetic
(MES round-turn cost is 97.6% of one tick) say the models give no edge by themselves. Their usable
content for this program is (a) a clean language for pre-registering a passive policy, (b) the
fill-intensity and markout measurements the pilot will make, and (c) one testable profitability
criterion (Gao and Wang 2020) that the pilot can evaluate directly.

---

## 1. Dynamic programming and the Hamilton-Jacobi-Bellman (HJB) equation

### 1.1 Core idea in plain words
You control something over time (here: where to put your bid and ask) and are scored at the end (here:
utility of final wealth). Dynamic programming says: the best you can do from today equals the best
single small step you can take now, followed by playing optimally from wherever that step leaves you.
Write that statement for an infinitesimal step and you get a partial differential equation for the
"value function" V (the best achievable expected score from each state). That equation is the HJB
equation. Solving it gives V; the control that attains the maximum inside the equation is the optimal
policy, as a function of the state (a feedback rule).

### 1.2 Derivation summary (the market-making case)
State Z_t = (t, x, s, q). Controls (delta^b_t, delta^a_t). Assumptions (those of Avellaneda and Stoikov
2008, and of Gueant, Lehalle and Fernandez-Tapia 2013):
- A1. The mid follows an arithmetic Brownian motion, dS = sigma dW (A-S eq. 2.1).
- A2. My bid is hit by a counting process N^b with intensity lambda^b(delta^b); my ask is lifted by
  N^a with intensity lambda^a(delta^a); both decreasing in the distance; each fill is one unit; the
  counting processes are independent of W (GLFT state this explicitly: "the point processes
  (independent of (Wt )t )", gueant_lehalle_ft_2013.txt line 181).
- A3. Two fills in the same dt have probability O(dt^2); quotes can be changed continuously at no cost.
- A4. Objective: maximize E[U(X_T + q_T S_T)], with U(w) = -exp(-gamma w) (CARA).

Value function: V(t, x, s, q) = sup over admissible quote processes of E_t[ U(X_T + q_T S_T) ].

Bellman principle over [t, t+dt]: V(t, z) = sup_{delta} E[ V(t+dt, Z_{t+dt}) ].
Expand the right-hand side over dt, using three possible events:
- No fill (probability about 1 - (lambda^b + lambda^a) dt): only s moves. By Ito's lemma,
  E[V(t+dt, x, s+dS, q)] = V + (dV/dt + (1/2) sigma^2 d2V/ds2) dt + o(dt).
- Bid filled (probability lambda^b(delta^b) dt): I buy one unit at s - delta^b, so x -> x - s + delta^b
  and q -> q + 1. Change in V: V(t, x - s + delta^b, s, q+1) - V(t, x, s, q).
- Ask filled (probability lambda^a(delta^a) dt): x -> x + s + delta^a, q -> q - 1.
Subtract V from both sides, divide by dt and let dt -> 0:

  dV/dt + (1/2) sigma^2 d2V/ds2
    + max_{delta^b} lambda^b(delta^b) [ V(t, x - s + delta^b, s, q+1) - V(t, x, s, q) ]
    + max_{delta^a} lambda^a(delta^a) [ V(t, x + s + delta^a, s, q-1) - V(t, x, s, q) ] = 0,
  with terminal condition V(T, x, s, q) = -exp(-gamma (x + q s)).

This is exactly the equation printed by A-S (avellaneda_stoikov_2008.txt lines 296-310: "the function u
solves the following Hamilton-Jacobi-Bellman equation ... u(s, x, q, T ) = - exp(-gamma(x + qs))", Greek transliterated).
Each bracket is "rate of an event times the value jump it causes": that is the generic HJB term for a
controlled jump process. Rigor (existence, the "verification theorem" that a smooth solution of the HJB
really is the value function) is what GLFT added for the bounded-inventory version ("we provide in the
case of our model with inventory limits a verification theorem that was absent from the original
paper", gueant_lehalle_ft_2013.txt lines 120-121).

### 1.3 The one-line first-order condition behind every formula below
With CARA utility the value function factors as V = -exp(-gamma (x + theta(t, s, q))) (the A-S
"ansatz", eq. 3.2). Substituting, each max term becomes, with p := the inventory-dependent "reservation
offset" (for the bid, p = theta(q) - theta(q+1) + s, measured from the mid):

  max over delta of  lambda(delta) * [1 - exp(-gamma (delta - p))] / gamma.

For an exponential fill rate lambda(delta) = A exp(-k delta), set the derivative to zero:
  -k e^{-k delta} [1 - e^{-gamma(delta - p)}] + e^{-k delta} gamma e^{-gamma(delta - p)} = 0
  => e^{-gamma(delta - p)} = k / (k + gamma)
  => delta* = p + (1/gamma) ln(1 + gamma/k).
So the optimal distance = (inventory-driven reservation offset) + (a constant "liquidity" half-spread
(1/gamma) ln(1 + gamma/k), which tends to 1/k as gamma -> 0). This is A-S eq. (3.6) specialised to the
exponential rate (there, ln(1 - gamma lambda/lambda') with lambda/lambda' = -1/k gives ln(1 + gamma/k)).
The risk-neutral case (gamma -> 0, the Cartea-Jaimungal "Model B") gives delta* = p + 1/k
(gueant_2017_optimal_mm.txt lines 462-465, which give for xi = 0 the condition p = delta*(p) + Lambda(delta*)/Lambda'(delta*) [rendered from the PDF layout],
and Lambda/Lambda' = -1/k for the exponential).

### 1.4 Data, outputs, compute
- Data: none by itself; it is a solution method. The data needs come from the parameters of each model
  (sections 3 to 9).
- Decides: a feedback policy (quote distances as a function of time-to-horizon and inventory).
- Compute: for these models the HJB reduces to a small system of ordinary differential equations in t,
  one per inventory level (GLFT Proposition 1; Gueant 2017 eq. 3.9). With |q| <= Q that is 2Q+1
  equations: Q = 50 is 101 equations, solvable in milliseconds on the laptop. Only the high-dimensional
  order-book versions (section 8.4) need heavy numerics.

### 1.5 Testable hypothesis, evidence, verdict
Not a hypothesis-bearing method by itself. Verdict at the end (section 11).

---

## 2. Ho and Stoll (1981): the monopolistic dealer under transaction and return uncertainty

Source status: the original (Journal of Financial Economics 9(1), 47-73) was not retrievable (no open
copy found; a search on 2026-10-21 returned only citations). Everything below comes from two secondary
descriptions with full text on disk: Avellaneda and Stoikov's introduction, and the review section of
arXiv 1512.08866 (multiple_dealers_2015_review.txt). The original's equations are [unverified].

### 2.1 Core idea
A single dealer posts a bid and an ask around a "true" price he takes as given. Buyers and sellers
arrive as Poisson processes whose rates fall as his fees (half-spreads) rise. He holds an inventory
whose value is risky, and chooses the fees to maximize expected utility of terminal wealth over many
periods. The result: the spread compensates for the risk of carrying inventory, and the quotes shift
with the inventory he holds. A-S describe it: "In their model, the authors specify a 'true' price for
the asset, and derive optimal bid and ask quotes around this price, to account for the effect of the
inventory" (avellaneda_stoikov_2008.txt lines 39-41).

### 2.2 Key equations (as reported by the secondary source)
From multiple_dealers_2015_review.txt lines 149-200:
- Order flow: dq^a = 1{a market buy arrives} Q lambda^a dt, dq^b = 1{a market sale arrives} Q lambda^b dt
  (Q = order size; lambda^a, lambda^b = arrival intensities, which "depend on the dealer's selling fee
  and buying fee", and the review says Ho and Stoll assume "a linear demand relation", lines 79-80).
- Quotes: p^b = p - b and p^a = p + a, with p the dealer's view of the true price and a, b the fees.
- Accounts: dF = r F dt - (p - b) dq^b + (p + a) dq^a (cash); dI = r_I I dt + p dq^b - p dq^a + I dZ_I
  (inventory, with return noise dZ_I); dY = r_Y Y dt + Y dZ_Y (base wealth).
- Objective: maximize E_t[U(W_T)], W_T = F_T + I_T + Y_T.
The solution method is the same dynamic programming argument as section 1.2; A-S say "This type of
optimal dealer problem was first studied by Ho and Stoll [6]. One of the key steps in their analysis is
to use the dynamic programming principle" (avellaneda_stoikov_2008.txt lines 296-298).

### 2.3 Data needs and what it decides
Needs the arrival rates as a function of the fee, a return variance, and a utility. A monopolist dealer
sets the price of immediacy; a retail participant in a CME central limit order book does not, so the
model's decision variable (the fee level) does not exist for us in that form. One-contract mbp-10/mbo
data would let one estimate "arrival rate versus distance from mid" (section 9), which is the modern
replacement for the linear demand curve.

### 2.4 Worked example, hypothesis, compute
No separate example: its modern form is A-S (section 3). No separate hypothesis. Compute: trivial.

### 2.5 Evidence at retail scale
Historical foundation only. A-S cite an empirical inventory effect in AMEX options quotes (Ho and Macris)
"This inventory effect was found to be significant in an empirical study of AMEX Options by Ho and
Macris [5]" (lines 41-43); that is evidence that dealers skew quotes with inventory, not that skewing
earns money for a small participant. No out-of-sample or retail evidence found.

---

## 3. Avellaneda and Stoikov (2008): reservation price and optimal spread

File: avellaneda_stoikov_2008.txt (the October 2006 draft hosted on Stoikov's Cornell page; the
published version is Quantitative Finance 8(3), 217-224, 2008, as cited in guilbaud_pham_2013.txt
references). Equation numbers below are the draft's.

### 3.1 Core idea in plain words
Two steps. First, ask: "given that I already hold q contracts and dislike risk, what is one more contract
worth to me?" That subjective value is the reservation (indifference) price r; it sits below the mid when
you are long (you want to sell) and above it when short. Second, place your bid and ask around r, at a
distance that trades off "closer quotes fill more often" against "closer quotes earn less per fill". The
paper's own summary: "First, the dealer computes a personal indifference valuation for the stock, given
his current inventory. Second, he calibrates his bid and ask quotes to the limit order book, by
considering the probability with which his quotes will be executed as a function of their distance from
the mid-price" (lines 64-68).

### 3.2 Key equations
Model: dS = sigma dW (2.1); fills at Poisson rate lambda(delta), derived as lambda(delta) = A exp(-k delta)
(2.11) from a power-law market-order size density f(x) ~ x^(-1-alpha) and a log impact Delta p ~ ln Q,
with A = Lambda/alpha and k = alpha K, where Lambda is the frequency of market orders and K the
impact-scale constant (lines 260-277: "where A = Lambda/alpha and k = alpha K", Greek transliterated).

Frozen-inventory value (no trading): v(x, s, q, t) = -exp(-gamma x) exp(-gamma q s)
exp(gamma^2 q^2 sigma^2 (T - t)/2) (2.3). The reservation bid r^b solves v(x - r^b, s, q+1, t) = v(x, s,
q, t) (2.4); the reservation ask solves v(x + r^a, s, q-1, t) = v(x, s, q, t) (2.5). Solving with (2.3):

  r^a = s + (1 - 2q) gamma sigma^2 (T - t)/2,   r^b = s + (-1 - 2q) gamma sigma^2 (T - t)/2   (2.6, 2.7)
  reservation price r(s, q, t) = s - q gamma sigma^2 (T - t).

Terms: gamma (1/price unit) = CARA risk aversion; sigma^2 (T - t) = variance of the mid over the
remaining horizon; q gamma sigma^2 (T-t) = the price concession that makes holding q more units
acceptable.

With trading, the HJB of section 1.2 holds; the ansatz u = -exp(-gamma x) exp(-gamma theta(s, q, t))
(3.2) gives the theta-equation (3.3), and the optimal distances (3.6)-(3.7). Expanding theta to second
order in q and linearising the arrival term (3.10)-(3.16) gives theta^1 = s and theta^2 =
(1/2) sigma^2 gamma (T - t), hence the famous approximate solution (lines 432-442):

  r(s, t) = s - q gamma sigma^2 (T - t)                                         (3.17)
  delta^a + delta^b = gamma sigma^2 (T - t) + (2/gamma) ln(1 + gamma/k)          (3.18)

quoted symmetrically around r. Note what is absent: A, the overall fill frequency, does not enter the
approximate quotes; and the spread does not depend on q ("The bid-ask spread in (3.13) is independent
of the inventory. This follows from our assumption of exponential arrival rates", lines 408-409).

### 3.3 Data needs; is one contract's 4-12 months enough?
Parameters: sigma (from mid changes), A and k (fill rate versus distance), gamma (chosen, not
estimated), T (chosen). For one CME contract: sigma is easy from any schema. A and k need, for each
distance delta, how often a resting order at that distance would have been filled. tbbo gives every
trade with the BBO just before it ("provides every trade event alongside the BBO immediately before the
effect of each trade", databento_tbbo.txt), enough for the A-S/hftbacktest "did a trade reach my price"
proxy. mbp-10 adds the visible queue ahead at each of ten levels ("every order book event across the top
ten price levels", databento_mbp10.txt), needed for a queue-aware fill estimate. mbo gives exact queue
position ("assigns a unique ID to every order in the book, to exactly track this queue position",
databento_queue_position.txt). Four months of MES gives tens of thousands of trades per day [unverified:
volume not measured here], ample for A and k; the binding constraint is not the sample but the model's
fit to a one-tick book (section 8).

### 3.4 What it decides
A feedback rule: bid = r - spread/2, ask = r + spread/2, as functions of (q, T - t). It estimates nothing
about future prices: the mid has zero drift by assumption ("our agent has no opinion on the drift or any
autocorrelation structure for the stock", lines 91-93).

### 3.5 Worked examples (C2_examples.py, output in C2_examples_out.txt)
(a) Reproducing the paper. Parameters from lines 463-464: s = 100, T = 1, sigma = 2, gamma = 0.1, k = 1.5.
At t = 0, q = 0:
  gamma sigma^2 (T - t) = 0.1 x 4 x 1 = 0.400
  (2/gamma) ln(1 + gamma/k) = 20 x ln(1.0667) = 20 x 0.06454 = 1.2908
  spread = 1.6908; bid = 99.1546, ask = 100.8454.
With q = +1: r = 100 - 1 x 0.1 x 4 x 1 = 99.60, so bid 98.7546, ask 100.4454 (the ask moves toward the
mid to shed the long). The paper's Table 1 lists "Spread 1.29" for gamma = 0.1, and 1.33 and 1.15 for
gamma = 0.01 and 0.5; those match the constant term alone: 200 ln(1 + 0.01/1.5) = 1.329 and
4 ln(1 + 0.5/1.5) = 1.151. So the tabulated "spread" is the horizon-independent part; the
gamma sigma^2 (T-t) part adds 0.4 at t = 0 and shrinks to 0 at T. (My reading of the table; the paper
does not say so explicitly.)

(b) MES-like units (all assumed, not measured): sigma = 1.0 tick/sqrt(s), k = 1.5 per tick,
gamma = 0.01 per tick, T - t = 600 s.
  inventory term gamma sigma^2 (T - t) = 0.01 x 1 x 600 = 6.0 ticks
  constant term (2/gamma) ln(1 + gamma/k) = 200 x ln(1.00667) = 1.329 ticks
  spread = 7.33 ticks; with q = +1, r - s = -6.0 ticks and delta^a = -2.34 ticks (a negative distance:
  the "limit" ask would sit 2.3 ticks below the mid, i.e., cross the market).
The approximation (3.17)-(3.18) is therefore unusable at realistic horizons for a futures contract: a
single contract moves the reservation price six ticks. GLFT show the cause (the expansion in q is poor
away from T) and fix it with inventory bounds; section 4.5 recomputes this case with their exact
solution and gets sensible quotes.

### 3.6 Turning the pilot into a pre-registerable test
A-S makes no claim of predictive edge; its money comes from assumption A2 (fills independent of the next
price move). The pilot can test that assumption directly.
- Hypothesis H-AS0 (assumption check, not a strategy): for a simulated 1-lot passive order resting at
  the best bid or ask, the mean mid-price markout after fill, signed in my favour, is zero at 1, 10 and
  60 s (A-S assumption) against the alternative that it is negative (adverse selection).
- Statistic: mean markout m_h = (1/n) sum_i side_i x (mid_{t_i + h} - fill price_i), in ticks, with a
  t-statistic clustered by day (or Newey-West over the fill sequence), one per horizon.
- Sample: under a random-walk mid the per-fill markout s.d. at horizon h is about sigma sqrt(h). With
  sigma = 1 tick/sqrt(s) (assumed) the 10 s s.d. is 3.2 ticks; detecting a mean of -0.25 tick at t = 3
  needs n = (3 x 3.2 / 0.25)^2 = 1,475, about 1,450 fills (1,440 with the unrounded s.d. 3.162). Four months should provide that [unverified until the
  pilot counts fills].
- Trial count: this selects no rule, so I would not count it in N; that is the lead's decision. If it
  is counted, it is 3 configurations (three horizons) or 1 if a single primary horizon is declared.
- A strategy-level hypothesis (H-AS1: inventory-skewed quoting at touch versus symmetric quoting) is in
  section 4.6, because on a one-tick book only the GLFT bounded-inventory version gives usable quotes.

### 3.7 Compute
The closed form is a few floating-point operations per quote update: microseconds on the laptop. The
calibration is a pass over the trades (section 9). No GPU. No need for a bigger machine.

### 3.8 Evidence: does it work at retail scale and latency?
- The paper itself tests only on simulated data in which A2 holds by construction, and even there the
  inventory policy earns less on average than the symmetric benchmark: Table 1 (gamma = 0.1),
  "Inventory 1.29 62.94 5.89" versus "Symmetric 1.29 67.21 13.43" (profit, s.d. of profit); for
  gamma = 0.5, 33.92 versus 66.20 (lines 528-560). The paper: "the inventory strategy obtains a P&L
  profile with a much smaller variance" (lines 525-526). So the method's product is variance reduction.
- Falces Marin, Diaz Pardo de Vera and Lopez Gonzalo (2022, PLOS ONE), backtest on 30 days of BTC-USD
  L2 data: the Avellaneda-Stoikov model with genetically tuned parameters (AS-Gen) had a negative daily
  Sharpe ratio on 28 of 30 test days, mean -0.24 (my count from their Table 2, falces_marin_2022_plosone.txt
  lines ~1196-1232: "Mean -0.43 -0.36 -0.24 -0.11 -0.13" for FOIC, LIIC, AS-Gen, Alpha-AS 1, Alpha-AS 2).
  Even the RL-improved variants had negative mean daily Sharpe. Crypto, not CME; but it is a
  cost-inclusive out-of-sample test of the method and it is negative.
- Gueant (2017) on applicability: "Models a la Avellaneda-Stoikov can hardly be applied to most stock
  markets for at least two reasons: (i) the discrete nature of prices (especially in the case of stocks
  with a large tick size), and (ii) the fact that the very nature of the limit order books, which are
  queuing systems with priorities and volumes, is not taken into account" (gueant_2017_optimal_mm.txt
  lines 169-171). MES and ES are large-tick books; the same objection applies.
- hftbacktest (open-source practitioner documentation) runs the GLFT closed form, the A-S family's
  descendant, on Binance futures with a maker rebate: "Improved, but even when accounting for rebates,
  it can only achieve breakeven at best" and "it's evident that profits are generated through rebates"
  (hftbacktest_glft_tutorial.txt lines 577, 623). CME offers a retail account no maker rebate; the
  program pays a commission on both sides.

---

## 4. Gueant, Lehalle and Fernandez-Tapia (2013): inventory limits and closed-form approximations

File: gueant_lehalle_ft_2013.txt (arXiv 1105.3115v5, July 2012 draft; published in Mathematics and
Financial Economics 7(4), 2013 [venue from my knowledge, not from the fetched text: unverified]).

### 4.1 Core idea
Same market as A-S, plus a hard inventory limit: at q = +Q the market maker stops bidding, at q = -Q he
stops offering ("we add a bound Q to the inventory ... will never set a bid quote", lines 216-222). With
that bound and exponential fill rates the HJB becomes a finite linear ODE system, solved exactly by a
matrix exponential, and as T grows the quotes converge to time-independent values with a simple closed
form. The paper shows the quotes are "almost independent of t, as soon as t is far from the terminal
time T. This observation is at odds with the approximations proposed in Avellaneda and Stoikov [3]"
(lines 391-394).

### 4.2 Key equations
Change of variables (Proposition 1, lines 300-313): u(t, x, q, s) = -exp(-gamma (x + q s)) v_q(t)^(-gamma/k),
where v = (v_{-Q}, ..., v_Q) solves the linear system
  dv_q/dt = alpha q^2 v_q - eta (v_{q-1} + v_{q+1})   (|q| < Q; one neighbour only at q = +/-Q),
  v_q(T) = 1,   alpha = (k/2) gamma sigma^2,   eta = A (1 + gamma/k)^(-(1 + k/gamma)).
In matrix form v(t) = exp(-M (T - t)) 1, with M tridiagonal: diagonal alpha q^2, off-diagonals -eta
(lines 320-353). Optimal quotes (Theorem 1, lines 360-381):
  delta^b*(t, q) = (1/k) ln( v_q(t) / v_{q+1}(t) ) + (1/gamma) ln(1 + gamma/k),   q != Q
  delta^a*(t, q) = (1/k) ln( v_q(t) / v_{q-1}(t) ) + (1/gamma) ln(1 + gamma/k),   q != -Q
Terms: alpha measures inventory risk per unit time (variance sigma^2 times risk aversion, scaled by k);
eta measures how much fill opportunity there is (A, discounted by the risk-adjusted liquidity factor).
The ratio v_q/v_{q+1} is the inventory skew; the last term is the constant from section 1.3.

Closed-form asymptotic approximation (the display at lines 612-630): replacing the
discrete eigenvector by a Gaussian exp(-(1/2) sqrt(alpha/eta) q^2),
  delta^b*(q) ~ (1/gamma) ln(1 + gamma/k) + ((2q + 1)/2) sqrt( (sigma^2 gamma / (2 k A)) (1 + gamma/k)^(1 + k/gamma) )
  delta^a*(q) ~ (1/gamma) ln(1 + gamma/k) - ((2q - 1)/2) sqrt( same )
  spread psi*  ~ (2/gamma) ln(1 + gamma/k) + sqrt( (sigma^2 gamma / (2 k A)) (1 + gamma/k)^(1 + k/gamma) ).
hftbacktest writes the same thing as c1 = (1/gamma) ln(1 + gamma/k) (per unit size) and c2 = the square
root, so that half-spread = c1 + sigma c2/2 and skew = sigma c2 per unit of inventory
(hftbacktest_glft_tutorial.txt lines 67-75). Unlike A-S, the inventory skew now scales with
sigma / sqrt(A k), so a liquid market (large A) means small skews, which is the economically right sign.

### 4.3 Data needs
As A-S: sigma, A, k from data; gamma and Q chosen. GLFT add the practical caveat: "A and k have to depend
at least on the actual market bid-ask spread" (lines 1281-1283). On MES the spread is one tick almost
always [unverified here; the pilot will measure], so conditioning on spread mostly means conditioning on
the rare wide-spread moments. One contract's tbbo is enough for the trade-through proxy; mbp-10 or mbo
for queue-aware fills.

### 4.4 What it decides
Exact optimal quotes for each inventory level within [-Q, Q] and each time to horizon; plus the
stationary closed form for long horizons.

### 4.5 Worked examples (C2_examples.py)
(a) The paper's Figure 1 parameters (lines 434-435): sigma = 0.3 tick/sqrt(s), A = 0.9 /s, k = 0.3 /tick,
gamma = 0.01 /tick, T = 600 s; I assumed Q = 10 (the caption lines I read do not state Q).
  alpha = (0.3/2) x 0.01 x 0.09 = 0.000135;  eta = 0.9 x (1 + 0.0333)^(-(1 + 30)) = 0.9 x 0.3619 = 0.3257
  c1 = 100 x ln(1.0333) = 3.279 ticks;  root term (sigma included) = sqrt(0.09 x 0.01 / (2 x 0.3 x 0.9)
  x 1.0333^31) = sqrt(0.001667 x 2.764) = 0.068 tick
  q = 0: exact delta^b = delta^a = 3.324 ticks; approximation 3.279 + 0.5 x 0.068 = 3.313 ticks
  (C2_examples_out.txt). q = 5: exact (3.848, 2.840) versus
  approximation (3.652, 2.974). With Q = 10 the exact q = 5 quotes differ from the approximation by 0.2 and 0.13 tick; the
  difference comes from the inventory bound (Q = 20 gives 3.654/2.972, equal to the approximation to 3 d.p.).
  The approximation is the Q -> infinity limit. Gueant (2017) makes the matching remark for the bounded case
  ("the closed-form approximations are satisfactory for small values of the inventory",
  gueant_2017_optimal_mm.txt line 2331).
(b) MES-like (assumed sigma = 1.0 tick/sqrt(s), A = 0.5 /s, k = 1.5 /tick, gamma = 0.01, T = 600 s).
  alpha = 0.75 x 0.01 x 1 = 0.0075;  eta = 0.5 x (1.00667)^(-151) = 0.1833.
  Q = 1 (a 1-lot trader): flat, delta^b = delta^a = 0.905 tick; long one, delta^a = 0.424 tick and no bid.
  Q = 3: flat 0.746; q = +1: (0.920, 0.583); q = +2: (1.171, 0.409).
  Compare A-S section 3.5(b), which put the ask 2.3 ticks through the mid for q = +1: the bound fixes it.
(c) The tick grid. On a one-tick-wide book the only passive distances are 0.5, 1.5, 2.5 ... ticks from
the mid (you cannot improve inside a one-tick spread). Rounding as GLFT do in their backtest ("we
decided to round the optimal quotes to the nearest tick", lines 1272-1273): 0.905 -> 0.5 (|0.905 - 0.5| =
0.405 < |1.5 - 0.905| = 0.595), and 0.424 -> 0.5. So for a 1-lot trader the exact optimal control
becomes: join the best bid and best ask when flat; when long one, offer at the best ask only; when short
one, bid at the best bid only. That is a position cap, nothing more. The quote moves one tick behind the
touch only when delta* exceeds 1.0 tick: with A = 0.5, k = 1.5, sigma = 1.0 the exact bounded solution needs gamma >= 0.13 (Q = 1) to 0.19 (Q = 3) per tick;
with sigma = 0.5, gamma >= 0.79 to 0.95; with A = 0.1, gamma >= 0.022 to 0.035 (REV_G4_control_check_out.txt).
(The large-Q approximation gives 0.31, 1.78 and 0.052.) So the whole continuous (gamma, Q) family maps onto a handful of discrete
policies: {touch, one tick behind} on the entry side, times Q in {1, 2, 3, ...}.

### 4.6 Pre-registerable hypothesis from the pilot
- H-GLFT1: a 1-lot discrete GLFT policy (join the touch on both sides when |q| < Q; quote only the
  unwinding side at |q| = Q; flatten at session end) has positive mean daily net P&L on the contract,
  where fills come from a queue-aware replay of the pilot's mbp-10 or mbo data (an order joins at the
  back of the visible queue and fills only after the queue ahead is consumed by trades; cancellations
  ahead advance it pro rata, or exactly with mbo).
- Statistic: mean daily net P&L (after the program's round-turn cost per completed round trip),
  day-level t-statistic (days are close to independent after the flat-at-close rule); report also the
  per-fill 1/10/60 s markouts so the P&L can be decomposed into spread captured, adverse selection and
  fees.
- Sample: about 80 RTH days in four months. For a day-level t > 3 with 80 days the daily Sharpe must be
  at least 3/sqrt(80) = 0.335, i.e. an annualized Sharpe near 0.335 x sqrt(252) = 5.3. Only an edge that
  large is detectable from the pilot window; a smaller real edge would need a longer purchase. Fees set
  the bar: per fill, MES earns half a tick (USD 0.625) minus half the round-turn cost (USD 0.61) = USD
  0.015 = 0.012 tick before any adverse selection; ES earns USD 6.25 - 1.89 = USD 4.36 = 0.349 tick
  (C2_examples_out.txt section 5). Any adverse markout larger than 0.012 tick makes MES passive making
  a loser; ES has thirty times the margin in tick terms.
- Trial count: Q in {1, 2, 3} times entry side {touch, one tick behind} = 6 configurations if all are
  declared; 1 if the lead declares a single policy (Q = 1, touch) ex ante. Gamma adds nothing beyond
  the policies it maps to, provided the declaration lists the discrete policies rather than gamma
  values.
- Limitations to declare: a replay cannot show the trader's own effect on others' behaviour, and the
  queue model is an assumption; the test is of the policy under that fill model.

### 4.7 Compute
Exact solution: one (2Q+1) x (2Q+1) matrix exponential per time step, microseconds for Q <= 50. The
replay is the cost: one pass over each day's events. Laptop CPU is sufficient; memory is the limit when
loading a whole day of mbo at once, so stream by day (CLAUDE.md compute rules). No GPU use.

### 4.8 Evidence
- The paper's only real-data test is one day of one stock with optimistic fills: "we considered the
  case of the French stock France Telecom on March 15th 2012", "we assumed that our orders were entirely
  filled when a trade occurred at or above the ask price quoted by the agent", and "We, voluntarily, do
  not give full details about the algorithm based on the model" (lines 1291-1297 and footnote 11). That
  is an illustration, not an out-of-sample test.
- The independence assumption (A2) is stated outright (line 181) and is exactly what fails at the top
  of a large-tick queue (section 6.8, section 8.5).
- hftbacktest's GLFT implementation: breakeven at best even with a 0.005% maker rebate (lines 281, 577).
- The paper says gamma is not estimated but picked: "we decided in our backtests to assign gamma an
  arbitrary value for which the inventory stayed between -10 and 10" (lines 1287-1289). A free
  parameter tuned on the test day is a selection that must be counted.

---

## 5. Gueant (2016), The Financial Mathematics of Market Liquidity (book), with Gueant (2017)

Source status: the book is not open. I have its table of contents (gueant_2016_routledge.txt, line 39)
and the author's 2017 paper "Optimal market making" (arXiv 1605.01862, gueant_2017_optimal_mm.txt), which
generalises the book's market-making chapter. Statements about the book's text beyond its contents
list are [unverified].

### 5.1 Core idea and contents
The book builds one framework, starting from Almgren-Chriss execution and ending with market making.
Contents (Routledge page): Part II "OPTIMAL LIQUIDATION The Almgren-Chriss Framework ... A Generalized
Almgren-Chriss Model in Continuous Time The Model in Discrete Time ... Optimal Liquidation with Different
Benchmarks ... Target Close Orders POV Orders VWAP Orders", Part III (block trades, option hedging with
execution costs, share buy-backs), and Part IV "MARKET MAKING Market Making: From Avellaneda-Stoikov to
Gueant-Lehalle, and Beyond ... Market Making on Stock Markets". The 2017 paper does three useful things:
(i) it allows general intensity functions Lambda(delta), not only exponential; (ii) it shows the
CARA objective (Model A) and the risk-neutral objective with a running inventory penalty used by
Cartea and Jaimungal (Model B) lead to the same family of ODEs; (iii) it gives closed-form
approximations for both, and multi-asset versions.

### 5.2 Key equations (Gueant 2017)
Model A: maximize E[-exp(-gamma (X_T + q_T S_T - l(|q_T|)))]. Model B: maximize
E[X_T + q_T S_T - l(|q_T|) - (1/2) gamma sigma^2 integral_0^T q_t^2 dt] (lines 310-322); l is a
terminal liquidation penalty. Both reduce to (eq. 3.9, lines 428-436)
  0 = d theta/dt(t, q) - (1/2) gamma sigma^2 q^2 + 1{q<Q} H^b_xi( (theta(t,q) - theta(t,q+Delta))/Delta )
      + 1{q>-Q} H^a_xi( (theta(t,q) - theta(t,q-Delta))/Delta ),   theta(T, q) = -l(|q|)
(the sign convention in the PDF has the time derivative with a minus sign and the H terms with minus
signs; I rewrote it with the same content), where H_xi(p) = sup_delta Lambda(delta)(1 - exp(-xi Delta
(delta - p)))/xi, xi = gamma for Model A and xi = 0 (limit) for Model B (lines 406-424). The optimal
quote solves the first-order condition of section 1.3 with Lambda general (lines 453-465). Delta is the
order size.

### 5.3 Data, decisions, compute
Same as section 4, with the advantage that Lambda can be estimated non-parametrically (one rate per
tick distance, section 9) and plugged in directly; no exponential-shape assumption is needed. Compute:
(2Q+1) nonlinear ODEs, solved by explicit Euler backward from T in milliseconds.

### 5.4 Worked example
For Model B with an exponential Lambda the quote is delta* = 1/k + (theta(q) - theta(q+1)): with
k = 1.5 /tick that is 0.667 tick plus the inventory term, which on a one-tick book again rounds to the
touch when flat (0.667 is closer to 0.5 than to 1.5). Same discrete collapse as section 4.5(c).

### 5.5 Hypothesis and trial count
None separate from H-GLFT1; Model A versus Model B is a choice of objective, and on a one-tick book both
map to the same few discrete policies. If the lead declares Model B with a non-parametric Lambda, it
adds no configuration beyond the discrete policy list.

### 5.6 Evidence
Gueant's own statement of the limits (section 3.8 quote, lines 169-171) applies. The 2017 paper's
numerical examples are corporate-bond and CDS-index market making with assumed parameters (lines
2222-2430: "the case of two credit (or CDS) indices"); no out-of-sample P&L test. The book is a
reference text; no evidence of retail profitability found or expected.

---

## 6. Cartea, Jaimungal and Penalva (2015): market making with adverse selection and alpha signals

Source status: the book (Algorithmic and High-Frequency Trading, Cambridge University Press 2015) is not
open. I have its contents list (cjp_2015_frontmatter.txt) and two open papers by the same authors that
carry the same models with full equations and data: Cartea, Jaimungal and Ricci, "Buy low, sell high"
(SIAM J. Financial Mathematics 2014; the Oxford copy fetched is titled "Algorithmic trading, stochastic
control, and mutually-exciting processes", DOI 10.1137/130911196: cartea_jaimungal_ricci_2018_siamrev.txt),
and Cartea, Donnelly and Jaimungal, "Enhancing trading strategies with order book signals" (Applied
Mathematical Finance 25(1), 2018: cartea_donnelly_jaimungal_2018_obsignals.txt). The book's chapter 10
equations are [unverified]; its contents are: "10 Market Making ... 10.2.2 Market Making At-The-Touch
... 10.3 Utility Maximising Market Maker ... 10.4 Market Making with Adverse Selection 10.4.1 Impact of
Market Orders on Midprice 10.4.2 Short-Term-Alpha and Adverse Selection" (frontmatter lines 386-397),
and chapter 12 uses order-flow information (lines 573-575).

### 6.1 Core idea in plain words
A-S and GLFT assume the mid does not care who just traded. Cartea and Jaimungal drop that: some market
orders are "influential" and push the short-term drift of the mid (the "short-term alpha") in their
direction. A passive order that is filled by an influential order is, on average, filled just before the
price moves against it: that is adverse selection. The optimal policy therefore (a) widens or withdraws
the quote on the side that is about to be picked off, (b) leans into the predicted move on the other
side, and (c) still controls inventory. Their stated finding, from simulation: "HF traders who do not
include predictors of short-term-alpha in their strategies are driven out of the market because they
are adversely selected by better informed traders and because they are not able to profit from
directional strategies" (cartea_jaimungal_ricci lines 11-13). In other words, in their own framework the
inventory control alone is not a business; the signal is.

### 6.2 Key equations
(a) Cartea, Jaimungal, Ricci. Mid: dS_t = (upsilon + alpha_t) dt + sigma dW_t (eq. 1, line 242), upsilon
set to 0. Short-term alpha (Assumption 4, eq. 4, lines 595-600):
  d alpha_t = -zeta alpha_t dt + sigma_alpha dB_t + eps^+ dM^+_t - eps^- dM^-_t
zeta = mean-reversion speed of the alpha; sigma_alpha = its diffusion; M^+ and M^- count influential buy
and sell market orders; eps^+/- = random jump sizes in the drift. Fill probability given an arriving
market order: h(delta; kappa) = e^(-kappa delta) (exponential class, lines 446-449), with kappa itself
random (the book's shape changes). Objective: maximize expected terminal wealth with a running inventory
penalty phi integral q^2 dt and a terminal liquidation penalty (Model B of section 5.2). The optimal
half-spreads expand as (eq. 11, line 729)
  delta^{+/-*}_t = delta_0^{+/-} + alpha_t delta_alpha^{+/-} + eps delta_eps^{+/-} + phi delta_phi^{+/-} + o(.)
so the quote = a base half-spread + a correction proportional to the current alpha + a correction for
the expected impact of the next influential order + an inventory correction. "if short-term-alpha is
positive, the HFT's sell halfspread is increased to avoid being picked off, and at the same time the
buy halfspread decreases" (lines 779-782).

(b) Cartea, Donnelly, Jaimungal, at-the-touch version (the one that fits a one-tick futures book).
Volume imbalance (eq. 1, lines 168-171): rho_t = (V^b_t - V^a_t)/(V^b_t + V^a_t) in [-1, 1], with V^b,
V^a the volumes at the best bid and ask. It is cut into n_Z buckets; the state J = (imbalance bucket,
spread in ticks). Controls gamma^+/- in {0, 1}: post (1) or do not post (0) a one-lot order at the best
ask/bid. Cash: dX_t = gamma^+ (S_{t-} + Delta_{t-}/2) dM^+_t - gamma^- (S_{t-} - Delta_{t-}/2) dM^-_t
(Delta = spread). Value function (eq. 8, line 829):
  H(t, x, q, S, J) = sup E[ X_T + q_T (S_T - l(q_T, Delta_T)) - phi integral_t^T q_u^2 du ].
The HJB reduces to an ODE system h(t, q, J), and the optimal control is a comparison (eq. 13a, lines
967-975): post at the ask iff
  Delta/2 - eps^+(J) + Sigma_1^+(t, q, J) > Sigma_0^+(t, q, J)  and q is not at the limit,
where Delta/2 is the half-spread earned on a fill, eps^+(J) is the expected adverse mid move after a buy
market order arrives in state J ("the immediate costs incurred due to adverse selection after having an
LO filled", lines 949-951), and the Sigma terms are the continuation values with and without the fill.
This is the single most useful formula in the section for this program: whether to post is "half-spread
versus expected post-fill markout in the current book state", plus an inventory term.

### 6.3 Data needs; is one contract enough?
Needs, per imbalance bucket J: market-order arrival rates, the probability a market order fills my
order (queue), and eps(J) = mean mid change after the order (exactly the pilot's conditional markouts).
rho_t needs the best-level volumes, which tbbo gives only at trade times (BBO "immediately before the
effect of each trade") and mbp-10/mbp-1 give continuously. One contract, four months of mbp-10, is
enough to estimate a 3- or 5-bucket table of eps(J) and fill rates; CDJ calibrated on six months and
tested on the next six, per stock (abstract, lines 26-29).

### 6.4 What it decides
When to post and when to step away, conditioned on the book state and inventory; and in the CJR version
how far from the touch to post.

### 6.5 Worked example (myopic version of eq. 13a; numbers assumed except fees)
Drop the continuation terms (a myopic agent with zero inventory). Post at the ask iff
half-spread - fee per side - eps^+(J) > 0. On MES, half-spread = 0.5 tick = USD 0.625, fee per side
= USD 0.61 (program table), so the condition is eps^+(J) < 0.012 tick. Suppose (assumed) the pilot
finds, for a passive ask filled by a buy market order, 10 s markouts of -0.40, -0.15 and +0.05 tick in
imbalance buckets "bid-heavy", "neutral", "ask-heavy" (negative = price rose after I sold). Then MES
posts only in the "ask-heavy" bucket, earning 0.05 + 0.012 = 0.062 tick = USD 0.078 per fill there. On ES
the threshold is 0.349 tick, so ES would post in "neutral" (0.349 - 0.15 = 0.199 tick = USD 2.49 per
fill) and "ask-heavy" (0.399 tick), and step away when the book is bid-heavy. The numbers show the
mechanism: the signal's value is the markout difference across buckets, and the fee sets how much of
it is left.

### 6.6 Pre-registerable hypotheses from the pilot
- H-CJ1 (signal exists): for simulated 1-lot passive fills, the mean 10 s markout differs between the
  extreme imbalance buckets in the direction CDJ report. Statistic: difference of bucket means, t
  clustered by day. Sample: if a third of fills fall in each extreme bucket and the per-fill s.d. is 3.2
  ticks (assumed), a 0.25-tick difference at t = 3 needs about 2 x (3 x 3.2 / 0.25)^2 = 2,950 fills per
  bucket. This is a measurement; whether it counts in N is the lead's decision (I would count it as 1
  if the bucket edges and horizon are declared in advance).
- H-CJ2 (gated policy pays): the policy "post at the touch on a side only when the imbalance bucket
  predicts a non-adverse markout; position cap Q = 1; flat at session end" has positive mean daily net
  P&L under the queue-aware replay. Statistic and sample as H-GLFT1 (section 4.6), but gating removes
  fills, so the day count needed rises roughly as 1/(fraction of time posted).
- Trial count: n_Z in {3, 5} times a gate threshold in {0, small positive} = 4 configurations, times
  horizons if more than one is used to define the gate. The bucket edges must be declared before
  computing, or each edge choice is another configuration.

### 6.7 Compute
CDJ's ODE system has (2Q+1) x n_Z x n_Delta states: Q = 1, n_Z = 5, n_Delta = 2 gives 30; Q = 50 gives
1,010; solved by backward Euler in well under a second. CJR's expansion is closed-form given parameters.
Estimating eps(J) is a pass over the fills. Laptop only.

### 6.8 Evidence (the strongest in this section, and it cuts both ways)
- Naive market making loses: CDJ's "zero-intelligence" strategy (always post both sides) has negative
  annualized Sharpe ratios for all eleven Nasdaq stocks and all inventory limits in Table 2 (for example
  "INTC -20.97 -26.15 ..." and "ORCL -20.24 -28.23 ...", lines 1560-1562), "indicating the failure to
  make positive profits through roundtrip trades when always posting LOs on both sides of the LOB" (lines
  1538-1539). This is out-of-sample (July to December 2014). It is the cleanest published evidence that
  the inventory-control part alone, on large-tick books, does not earn money.
- With the imbalance signal, out-of-sample Sharpe ratios become large under "always filled at the touch"
  (Table 4, n_Z = 3: e.g. ORCL 11.65 to 34.25 across phi; Table 5, n_Z = 5: 11.75 to 33.29), but the authors themselves flag the bias: "So
  far the strategy assumes that the agent's LOs are always at the front of the queue. This assumption is
  unrealistic and introduces a bias in the profitability" (lines 1622-1624). With a back-of-queue fill
  probability (Table 7) the Sharpe ratios fall to roughly -5 to +12, and ARCC is negative at every phi
  ("ARCC -4.43 -3.79 -4.75 -5.02 -2.28 -3.34 -4.40 -3.18", line 1706).
- Further assumptions that favour the strategy: zero latency ("we assume that the agent has zero latency
  - market changes are followed by immediate repositioning of LO's. In reality, for an agent with
  colocated servers, a latency on the order of 10ms is not unrealistic", lines 818-820), no own effect on
  the book (lines 796-805), and no fees: a search of the fetched text for "commission", "transaction
  cost" and "exchange fee" returns 0 hits. Eight phi values per stock were reported; picking the best
  phi is a selection over 8 configurations per stock.
- CJR's evidence is simulation only ("We test our model using simulations", lines 187 and 1166), with the
  parameters chosen by the authors (lines 1000-1012).
- Retail relevance: the edge in these papers comes from processing order flow faster than others and
  repositioning before being picked off. CDJ's own latency remark (10 ms for a colocated agent) is below
  the program's tens of milliseconds from Vancouver to Aurora. Baron, Brogaard and Kirilenko find on the
  E-mini that "revenue is concentrated among a small number of HFT firms who achieve greater investment
  performance through liquidity-taking activity and higher speed" (baron_brogaard_kirilenko_2014_cftc.txt
  lines 14-15), and that "Small traders experience a much larger loss of -$3.49" per contract over one
  minute when trading with aggressive HFTs (lines 1452-1454). The direction of flow is from slow to fast.

---

## 7. Almgren and Chriss (2000): optimal execution, mean-variance, the sinh trajectory

File: almgren_chriss_2000.txt (December 2000 version, published in Journal of Risk 3(2), 2000/01; the
venue is from my knowledge, not the fetched text [unverified]).

### 7.1 Core idea
You must sell X units by time T. Selling fast costs more (temporary impact: your own selling pushes the
price you get down); selling slowly leaves you exposed to price risk for longer. Choose the schedule that
minimises expected cost plus lambda times its variance. With linear impact the answer is a smooth
schedule that decays like sinh, front-loaded when you are risk averse, a straight line (TWAP) when you
are risk neutral.

### 7.2 Key equations (discrete time, N intervals of length tau = T/N)
Price: S_k = S_{k-1} + sigma tau^(1/2) xi_k - tau g(n_k/tau), with n_k the units sold in interval k and
x_k the units still held. Price received: S~_k = S_{k-1} - h(n_k/tau) (eq. 2). Linear impact:
g(v) = gamma v (permanent, eq. 6) and h(n_k/tau) = eps sgn(n_k) + (eta/tau) n_k (temporary, eq. 7);
eps = fixed cost per unit (half-spread plus fees), eta = temporary impact per unit of trading rate,
gamma = permanent impact per unit sold. Expected shortfall and variance (eqs. 4, 5, 8):
  E(x) = (1/2) gamma X^2 + eps sum|n_k| + (eta~/tau) sum n_k^2,   eta~ = eta - (1/2) gamma tau
  V(x) = sigma^2 sum tau x_k^2.
Minimise U = E + lambda V. Setting dU/dx_j = 0 gives the difference equation
(x_{j-1} - 2 x_j + x_{j+1})/tau^2 = kappa~^2 x_j with kappa~^2 = lambda sigma^2 / eta~ (eq. 16), solved by
  x_j = sinh(kappa (T - t_j)) / sinh(kappa T) * X                    (eq. 17)
  n_j = [2 sinh(kappa tau/2) / sinh(kappa T)] cosh(kappa (T - t_{j-1/2})) X   (eq. 18)
with (2/tau^2)(cosh(kappa tau) - 1) = kappa~^2, and for small tau kappa ~ sqrt(lambda sigma^2 / eta) (eq. 19).
The "half-life" theta = 1/kappa is "the amount of time it takes to deplete the portfolio by a factor of
e" (lines 683-684). Derivation: a quadratic in x minimised by its first-order conditions (lines 589-608),
the discrete analogue of the Euler-Lagrange equation x'' = kappa^2 x.

### 7.3 Data needs
sigma (any schema); eta and eps from the cost of trading at different speeds, which needs trades and
the book (mbp-10 shows how many contracts sit at each level, so the cost of sweeping n contracts is
directly readable); gamma (permanent impact) from price changes after metaorders, which a single
trader's public data cannot identify well. For a 1-lot trader the inputs are moot (section 7.5).

### 7.4 What it decides
The execution schedule for a given order size and horizon, and the cost-risk frontier.

### 7.5 Worked example (ticks, seconds; parameters assumed; C2_examples_out.txt section 8)
(a) Half-lives: with sigma = 1 tick/sqrt(s), eta = 0.05 tick per (contract/s), lambda = 0.1 per
tick-contract: kappa = sqrt(0.1 x 1 / 0.05) = 1.414 /s, theta = 0.71 s: sell almost at once. With
lambda = 1e-4: kappa = 0.0447 /s, theta = 22.4 s. With eta = 5: theta = 224 s.
(b) Schedule: X = 20 contracts, T = 60 s, N = 6, lambda = 1e-3, eta = 5:
kappa~^2 = 1e-3 x 1 / 5 = 2e-4; cosh(kappa x 10) = 1 + 2e-4 x 100/2 = 1.01 -> kappa = 0.01413 /s;
holdings 20.0, 16.09, 12.50, 9.16, 6.01, 2.97, 0.00; trades 3.91, 3.59, 3.34, 3.15, 3.03, 2.97: mildly
front-loaded, close to TWAP because kappa T = 0.85 < 1.
(c) The retail case: X = 1 contract. There is nothing to split; the only decision is "cross now (pay
the half-spread plus fee) or rest a limit order (risk non-execution and adverse selection)". That
decision is the limit-versus-market-order problem of Guilbaud and Pham (section 8.1), not A-C.

### 7.6 Hypothesis from the pilot
None that bears on edge. The pilot can measure the A-C inputs for later use (the visible depth at each
level gives the sweep cost; 1/10/60 s markouts of aggressive trades give a permanent-impact proxy), but
for one lot the schedule is trivial. Trial count: 0. If the lead wants an unwind rule inside H-GLFT1
(at the inventory cap, cross immediately versus rest at the touch for up to t seconds), each declared
alternative adds 1 configuration.

### 7.7 Compute
Closed form. Microseconds. Laptop.

### 7.8 Evidence
A-C is a cost-minimisation model; it promises lower implementation shortfall, not alpha. Its own
footnote limits it: monotone selling "can cease to be true if there is drift or serial correlation in
the price movements" (line 649, footnote 11). Lehalle and Neuman (2019) describe the field's later turn:
"The inclusion of signals (i.e. short term predictors of price dynamics) in optimal trading is a recent
development" (lehalle_neuman_2019_signals.txt abstract). I did not fetch an empirical post-publication
test of A-C on futures (the Almgren et al. 2005 impact-estimation paper URL returned a 404; logged).
For a 1-lot MES trader, impact relative to the visible depth is negligible [unverified: depth not
measured here; the pilot will show it].

---

## 8. Discrete-tick adaptations for a futures book with a fixed tick

Why this section matters: MES and ES are "large-tick" books in the sense of Huang, Lehalle and Rosenbaum
("A large tick asset is defined as an asset whose bid-ask spread is almost always equal to one tick",
huang_lehalle_rosenbaum_2015_qr.txt line 96; they add that index futures are among such assets, lines
240-241) [the MES spread distribution itself is unverified here; the pilot measures it]. On such a book
the continuous models' main output, a distance delta, has only a few feasible values, and the main
determinant of fills is queue position, which the continuous models ignore.

### 8.1 Guilbaud and Pham (2013): limit and market orders with a spread in ticks
File: guilbaud_pham_2013.txt (arXiv 1106.5040). Core idea: the spread is a Markov chain on multiples of
the tick, changing at the jumps of a "tick-time clock"; the agent can post at the best quote or one tick
better (to get priority), and can also cross with a market order; fills are Cox processes whose
intensities depend on the spread and the chosen quote (abstract, lines 18-31). The problem is a mixed
regular/impulse control, reduced to "a system of simple equations involving only the inventory and
spread variables" under mean-variance or exponential utility (lines 33-37). Calibration: execution
intensities are counts over time-in-state, lambda^b_i(q^b) = N^b_T / T^b_T (eq. 2.9, lines 491-500),
with a queue-aware proxy that counts a fill at the best bid only if the sell volume traded exceeds
"V0 + V^b" (my size plus the queue ahead, lines 576-580). Evidence: real data were used only for
calibration (one day, SOGN.PA, lines 513-515); the performance tests are simulated, and the authors say
so: "the annualized value of the NIR (obtained by simple extrapolation) is 47, but this simulated data
backtest must be completed by a backtest on real data" (lines 1162-1165). A net information ratio of 47
on simulated data is a warning about what these models produce when their assumptions hold by
construction.

### 8.2 Gao and Wang (2020): large-tick market making with latency, and a profitability criterion
File: gao_wang_2020_latency.txt (arXiv 1806.05849v3, Quantitative Finance 20(9), 2020 per the RePEc
listing in my search results). Model: spread fixed at one tick, mid a compound Poisson process jumping
+/- 1 tick at rate lambda (eq. 2.1, lines 187-197); a resting ask is filled either (2a) when the price
jumps through it, "among the last in the queue to get filled just as the market moves higher", which
"serves the role of 'adverse selection'", or (2b) by "small or 'uninformed' buy market order flow" at
rate lambda^+ without the mid moving (lines 270-295). Orders arrive at the exchange after a latency.
Result (lines 568-575): the expected profit of a filled at-the-touch ask is
  E[profit | fill] = lambda^+/(lambda^+ + lambda/2) x 0.5 + (lambda/2)/(lambda^+ + lambda/2) x (-0.5)
                   = lambda^+/(lambda^+ + lambda/2) - 0.5   ticks,
and "Value of an order = (spread capture - adverse selection cost) x fill probability" (line 581). If
lambda^+ <= lambda/2 on both sides, "the market maker can not make a positive profit regardless of how
many times the market maker quotes" (Theorem 4.3 (1), lines 690-697). Latency perturbs the quote and
lowers the order value (Theorem 4.1 (b), lines 584-587).

Worked example with fees (C2_gaowang.py, C2_gaowang_out.txt). With a per-side fee f in ticks the
condition becomes lambda^+/(lambda^+ + lambda/2) > 0.5 + f, i.e. the share of fills that are "benign"
(filled without the price trading through) must exceed 0.5 + f.
- MES: f = 0.61/1.25 = 0.488 tick, so the benign share must exceed 0.988, i.e. lambda^+ > 82.3 x (lambda/2):
  fewer than 1.2% of fills may be trade-through fills. At a benign share of 0.80 the expected net per
  fill is 0.80 x 0.5 - 0.20 x 0.5 - 0.488 = -0.188 tick = -USD 0.235.
- ES: f = 1.89/12.50 = 0.151 tick, threshold 0.651; at 0.70 the net is +0.049 tick = +USD 0.61 per fill,
  at 0.80 it is +0.149 tick = +USD 1.86.
Pilot hypothesis H-GW1: on the contract, the share of simulated 1-lot touch fills that are benign (the
level was not cleared and the mid did not move against the order within the fill event) exceeds
0.5 + f. Statistic: the benign share with a day-clustered standard error; one-sided t > 3 against 0.5 + f.
Sample: under independent fills, showing 0.70 > 0.651 at t = 3 needs about 9 x 0.7 x 0.3 / 0.049^2 = 794
fills; showing 0.995 > 0.988 for MES needs about 914; clustering will raise both. Trial count: 1 per
contract tested (2 if both MES and ES are evaluated from separate purchases). This is the most direct,
cheapest test in the section, and it uses exactly the pilot's fill classification. It ignores drift
after the fill; the 10 and 60 s markouts cover that.

### 8.3 Queue position: Moallemi and Yuan
File: moallemi_yuan_queue_value.txt (Columbia working paper, revision June 2017). "for some large
tick-size stocks, we find that queue value can be of the same order of magnitude as the bid-ask spread.
This suggests that accurate valuation of queue position is a necessary and important ingredient in
considering optimal execution or market-making strategies for such assets" (lines 29-32), and "adverse
selection costs are increasing with queue position" (line 24). A retail order arriving tens of
milliseconds after a level forms joins at the back; if queue value is of the order of the spread, the
back of the queue is where the spread is given away. The pilot's queue-time and fill-rate measurements
by queue position (exact with mbo, estimated with mbp-10) test this on the contract.

### 8.4 Order-book state models: queue-reactive (Huang, Lehalle, Rosenbaum 2015) and
### Abergel, Hure, Pham (2020)
Queue-reactive model: between changes of the reference price, the book is a Markov queueing system whose
insertion, cancellation and market-order intensities depend on the current queue sizes; intensities
are estimated by maximum likelihood from the event times ("it is easy to estimate lambda^L_i(n),
lambda^C_i(n) and lambda^M_i(n) by the maximum likelihood method", lines 331-333; for a Poisson rate in
state n this is count in state n divided by time in state n). Useful as the fill simulator behind
H-GLFT1 and H-CJ2. Abergel, Hure and Pham solve market making in a FIFO book whose event intensities
depend on the book state, by MDP dynamic programming with quantization ("We use a control
randomization method combined with quantization method to compute the optimal strategies", abstract),
but "Several computational tests are performed on simulated data" only (abstract). These are the right
models for a one-tick futures book; none of the fetched papers shows them earning money out of sample.

### 8.5 Summary for a one-tick book
- Feasible quotes: touch, one tick behind, two behind. Continuous optima are rounded (GLFT section 7).
- Fills: decided by queue position and by whether the level is swept (Gao-Wang case 2a). The continuous
  models' lambda(delta) = A e^(-k delta) has, on a one-tick book, only one point inside the touch region
  and should be replaced by a fill model conditioned on queue position and book state.
- The decision that remains is binary per side: post or not (CDJ), plus an inventory cap.
- Compute: queue-reactive calibration on one contract is a single pass over mbo/mbp-10 events per day;
  the Abergel-Hure-Pham numerics (quantization with many grid points over book states) are the only
  piece where a bigger machine might help, and only if the lead wants a full book-state policy, which
  this section does not recommend.

---

## 9. Calibration of fill intensities from data

### 9.1 Core idea
Every model above needs "how often does a resting order at a given place get filled". There are four
ways to estimate it, in increasing realism and data need.
1. From market-order statistics (A-S section 2.5): lambda(delta) = Lambda P(Delta p > delta), the rate of
   market orders times the probability that an order moves the price past delta. With power-law sizes
   and log impact this gives A e^(-k delta) with A = Lambda/alpha, k = alpha K (eq. 2.11, lines 260-277).
2. Trade-through counting (hftbacktest; GLFT backtest): at each decision step, record how deep trades
   reached relative to the mid; the rate at which trades reach distance delta estimates lambda(delta);
   fit log lambda = log A - k delta by regression ("Calibrate A and k using linear regression, since by
   taking the logarithm of both sides of lambda, it becomes log lambda = -k delta + log A",
   hftbacktest_glft_tutorial.txt line 198). Queue ignored: "only market trades that cross our quote will
   be counted as executed" (line 135). This undercounts fills at the touch (a trade at my price can fill
   me without crossing) and overstates their quality (only sweeping trades, the adverse ones, count).
   The same documentation flags a units bug in its own example ("The trading intensity ... is
   incorrectly in half-tick units instead of tick units", line 136), a reminder to unit-test calibration
   code.
3. Counts over time-in-state with a queue proxy (Guilbaud-Pham eq. 2.9-2.11; CDJ eq. 17): lambda_hat =
   (number of qualifying executions in state) / (time spent in state), where an execution qualifies only
   if traded volume at the level exceeds my size plus the visible queue ahead. CDJ's version, the share
   of market orders "large enough to fill the entire first price queue", is a back-of-queue lower bound
   (cartea_donnelly_jaimungal lines 1622-1640 and 1685-1690).
4. Exact queue tracking with order IDs (mbo): follow a hypothetical order placed at the back of the
   queue, advance it when orders ahead are filled or cancelled, and record whether and when it fills
   (Databento's example uses "the MBO schema ("L3" data), which assigns a unique ID to every order in the
   book, to exactly track this queue position" and also shows how to "use the MBP-10 schema ("L2" data)
   to estimate queue position", databento_queue_position.txt). With mbp-10 the position must be inferred
   from aggregate size changes (cancellations ahead versus behind are not identified, so an assumption
   such as pro-rata cancellation is needed).

### 9.2 Key equations and the statistics of the estimate
For a Poisson rate, the maximum-likelihood estimator in a state is lambda_hat = N/T (count over exposure
time), with standard error sqrt(N)/T; the delta method gives se(log lambda_hat) = 1/sqrt(N), so a
weighted regression of log lambda_hat on delta uses weights N. Queue-reactive MLE is the same estimator
per (queue size, event type) cell.

### 9.3 Worked example (toy counts, not data; C2_examples_out.txt section 6)
Exposure T = 3,600 s; trades reaching 0.5, 1.5, 2.5, 3.5 ticks from mid: N = 1,800, 400, 90, 20.
lambda_hat = 0.500, 0.111, 0.025, 0.0056 per s (standard errors 0.0118, 0.0056, 0.0026, 0.0012).
log lambda_hat = -0.693, -2.197, -3.689, -5.193: each tick costs about 1.5 in log rate. Weighted least
squares: k = 1.501 per tick (s.e. 0.036), A = e^0.0568 = 1.06 per s. Interpretation: at the touch
(0.5 tick) about one qualifying trade every 2 s; one tick further back, one every 9 s. On a one-tick book
the A-S/GLFT formulas then say delta* ~ 1/k = 0.67 tick for small gamma, which rounds to the touch.

### 9.4 Data needs; one contract, 4-12 months
Approach 2 needs only trades and the BBO (tbbo). Approaches 3 and 4 need depth (mbp-10) or order IDs
(mbo). Rates vary through the day and with the spread (GLFT, lines 1281-1283), so estimates should be
per time-of-day bucket and per spread state; four months gives about 80 RTH days, enough for a
time-of-day profile [unverified until counted]. Twelve months would allow a stability test across
regimes.

### 9.5 Pre-registerable hypotheses
- H-CAL1 (stability): fill rates at the touch estimated on the first half of the pilot window predict
  the second half's within a declared tolerance (for example, the ratio of realised to predicted fills
  per time-of-day bucket has a mean within 1 +/- 0.2). Statistic: the realised/predicted ratio with a
  day-clustered interval. This selects no trading rule; I would not count it in N (lead's decision).
- H-CAL2 (shape): the exponential form fits the per-level rates (likelihood-ratio test of free per-level
  rates against A e^(-k delta)). Model validation only; 0 configurations.

### 9.6 Compute
One pass over the events per day; streaming by day keeps memory small. Laptop CPU. The exact mbo queue
tracker is a per-event loop; in plain Python it may be slow over months of a busy contract [unverified:
not timed here]; a numba or compiled loop, or processing days in parallel within the CLAUDE.md CPU
limit, solves that without new hardware.

### 9.7 Evidence
Calibration methods are standard and not in dispute. The evidence problem is that the most common
practitioner method (trade-through counting) ignores the queue, which is exactly where the profit and the
adverse selection live on a large-tick book (sections 8.2 and 8.3).

---

## 10. Do these models give a retail 1-lot trader an edge, or only an inventory-risk policy?

An inventory-risk policy, not an edge. The reasons, with sources:
1. No price forecast. A-S, GLFT and Gueant assume a driftless mid and fills independent of it (A-S
   lines 91-93; GLFT line 181). Under those assumptions every passive fill earns the half-spread on
   average, so any quoting rule makes money; the control only moves risk around. A-S's own table shows
   the inventory policy earning less than the symmetric one (62.94 against 67.21) with far lower
   variance (5.89 against 13.43).
2. The edge in this literature comes from the signal, and the signal needs speed. Cartea, Jaimungal and
   Ricci: market makers without short-term-alpha predictors are "driven out of the market". CDJ: the
   zero-intelligence policy has negative out-of-sample Sharpe ratios on all eleven stocks; the
   imbalance-gated policy is positive under front-of-queue, zero-latency, no-fee assumptions, and falls
   to roughly -5 to +12 with a back-of-queue fill model (Table 7).
3. Speed and queue position. Gao and Wang: latency "impacts negatively the performance of market makers"
   and profit needs uninformed fills to outnumber trade-through fills; Moallemi and Yuan: queue value
   can be as large as the spread; Baron, Brogaard and Kirilenko (E-mini): revenue goes to the fastest
   firms, and small traders lose USD 3.49 per contract at one minute against aggressive HFTs.
4. Fees on MES. Round-turn cost USD 1.22 against a USD 1.25 tick: a passive round trip that captures the
   full spread nets USD 0.03. By the Gao-Wang arithmetic, 98.8% of fills would have to be benign. ES is
   less hopeless (threshold 65.1% benign), but ES has the longest queues.
5. Published real-data tests are thin and mostly negative: GLFT one day with optimistic fills; Guilbaud
   and Pham simulated (NIR 47, "must be completed by a backtest on real data"); A-S-tuned on 30 days of
   BTC-USD negative on 28 of 30 days; hftbacktest GLFT breakeven only with exchange rebates.
What survives for the program: (a) the at-the-touch "post or not" decision of CDJ, whose inputs are the
pilot's conditional markouts; (b) the Gao-Wang benign-fill criterion, a one-number go/no-go test per
contract; (c) GLFT's discrete policy as the default inventory cap for any passive rule the program
tests; (d) the calibration estimators of section 9 for the fill simulator. None of these is evidence of
an edge; each is a way to find out cheaply whether one exists.

---

## 11. Verdicts (use / maybe / skip, for this program)

| Method | Verdict | Reason |
|---|---|---|
| Dynamic programming / HJB | use (as a tool) | The language for writing any passive policy as a pre-declared feedback rule; tiny ODE systems, laptop-scale. Not a source of edge. |
| Ho and Stoll (1981) | skip | Historical foundation; monopolist-dealer setting does not fit a CLOB participant; original not retrieved. |
| Avellaneda and Stoikov (2008) | skip as a strategy; use as background | The approximate quotes misbehave at futures horizons (section 3.5b: 6-tick skew for one contract); no edge mechanism; negative cost-inclusive test (Falces Marin 2022). |
| GLFT (2013) | maybe (as the inventory cap inside another rule) | Exact bounded-inventory quotes; on a one-tick book they reduce to "touch, cap at Q" (section 4.5c). H-GLFT1 tests whether that policy alone pays; prior evidence says it will not. |
| Gueant (2016 book, 2017 paper) | use as reference | Best single treatment; general intensities allow a non-parametric fill curve; no extra configurations. |
| Cartea, Jaimungal, Penalva (2015) and CDJ (2018) | maybe, leaning use for the measurement | The only family with an edge mechanism (book-imbalance gating against adverse selection). The pilot's conditional markouts are its inputs (H-CJ1); a gated policy (H-CJ2) is testable, but the published gains shrink with realistic fills and assume zero latency and no fees. |
| Almgren and Chriss (2000) | skip for a 1-lot trader | Nothing to schedule for one contract; relevant only if position sizes grow. |
| Discrete-tick models (Guilbaud-Pham, Gao-Wang, queue-reactive, Abergel-Hure-Pham) | use Gao-Wang criterion; maybe queue-reactive as simulator; skip the high-dimensional MDPs | Gao-Wang gives a cheap, decisive go/no-go (H-GW1); queue-reactive estimation gives a fill simulator; full book-state MDPs are simulation-only in the fetched evidence. |
| Fill-intensity calibration | use | Needed for every passive test; prefer queue-aware estimators (mbo exact, mbp-10 inferred) over trade-through counting. |

---

## 12. Pilot hypotheses proposed by this section (for the lead; nothing here is declared)

All use the pilot's simulated 1-lot passive orders on one contract (fill rates, queue times, 1/10/60 s
markouts). "Configurations" is my count if the lead adopts the hypothesis as written; whether a
measurement-only hypothesis enters N is the lead's decision.

| ID | Hypothesis | Statistic | Sample needed (assumptions in the cited section) | Configurations |
|---|---|---|---|---|
| H-AS0 | Mean signed markout of touch fills is 0 (A-S assumption) vs negative | mean markout per horizon, day-clustered t | ~1,450 fills to detect -0.25 tick at t = 3 if s.d. = 3.2 ticks (3.6) | 0 (measurement) or 1-3 |
| H-GW1 | Benign-fill share > 0.5 + fee per side (MES 0.988, ES 0.651) | proportion, day-clustered one-sided t > 3 | ~800 fills (ES, true share 0.70 vs 0.651) or ~900 (MES, 0.995 vs 0.988) (8.2) | 1 per contract |
| H-CJ1 | 10 s markout differs between extreme imbalance buckets | difference of bucket means | ~2,950 fills per bucket for 0.25 tick (6.6) | 1 if edges and horizon declared |
| H-CJ2 | Imbalance-gated touch posting, Q = 1, flat at close, has mean daily net P&L > 0 | day-level t | daily Sharpe >= 0.335 detectable in 80 days (annualized ~5.3) | 4 (n_Z in {3,5} x 2 gates) |
| H-GLFT1 | Discrete GLFT policy (touch, cap Q) has mean daily net P&L > 0 | day-level t | as H-CJ2 (4.6) | 6 (Q in {1,2,3} x {touch, one behind}) or 1 |
| H-CAL1 | Touch fill rates are stable between halves of the window | realised/predicted ratio | 80 days split 40/40 (9.5) | 0 (validation) |
| H-CAL2 | Exponential fill-rate shape fits | likelihood-ratio test | per-level counts (9.5) | 0 (validation) |

Ordering suggestion (for the lead to accept or not): H-GW1 first, because it is cheap, uses only the
fill classification, and on MES its threshold (98.8% benign) can reject passive market making outright.
If it fails, the touch variant of H-GLFT1 cannot pass (same fills). H-CJ2 can still pass if the gated
buckets' benign share clears 0.5 + f; H-GW1 computed per imbalance bucket is its precondition.

---

## 13. Compute needs and cost

| Piece | Laptop (20 CPUs, 14 GB, RTX 3050 4 GB) | Bigger machine needed? |
|---|---|---|
| A-S / GLFT closed forms, GLFT matrix exponential (Q <= 50) | microseconds to milliseconds | no |
| Gueant 2017 / CDJ ODE systems (up to ~1,000 states) | well under a second | no |
| Fill-intensity calibration, markouts, queue-reactive MLE | one pass over each day's events, streamed by day | no, if streamed; memory is the limit |
| Queue-aware replay for H-GLFT1 / H-CJ2 (a handful of configurations) | one replay per configuration, hours at most for 4 months in compiled code [unverified: not timed] | no |
| Abergel-Hure-Pham style high-dimensional MDP | possible but slow | maybe; not recommended |
| GPU | not used by any method in this section | no |

Cloud prices (lambda_pricing.txt, fetched 2026-10-21, on-demand, "plus applicable sales tax"): 1x NVIDIA
A10 instance "24 GB 30 226 GiB 1.3 TiB SSD $1.29" per GPU-hour (30 vCPUs, 226 GiB RAM); 1x "NVIDIA A6000
48 GB 14 100 GiB 512 GiB SSD $1.09"; 1x "NVIDIA Quadro RTX 6000 24 GB 14 46 GiB 512 GiB SSD $0.69".
The only reason to rent would be RAM (loading many months of mbo at once): 10 hours on the 226 GiB A10
instance costs 10 x 1.29 = USD 12.90 before tax. Streaming by day on the laptop makes even that
unnecessary. RunPod's page (runpod_pricing.html) was saved but its prices did not extract cleanly by grep
and are not used.

---

## 14. References (fetched full text unless marked)

1. Avellaneda, M. and Stoikov, S. (2008). High-frequency trading in a limit order book. Quantitative
   Finance 8(3), 217-224. Draft of 5 Oct 2006 from https://people.orie.cornell.edu/sfs33/LimitOrderBook.pdf
   (avellaneda_stoikov_2008.pdf/.txt).
2. Gueant, O., Lehalle, C.-A. and Fernandez-Tapia, J. (2013). Dealing with the inventory risk: a solution
   to the market making problem. arXiv 1105.3115v5 (gueant_lehalle_ft_2013.pdf/.txt). Journal venue
   [unverified from fetched text].
3. Gueant, O. (2017). Optimal market making. arXiv 1605.01862v5 (gueant_2017_optimal_mm.pdf/.txt).
4. Gueant, O. (2016). The Financial Mathematics of Market Liquidity: From Optimal Execution to Market
   Making. Chapman and Hall/CRC. Contents only, Routledge page (gueant_2016_routledge.html/.txt); book
   text [unverified].
5. Cartea, A., Jaimungal, S. and Penalva, J. (2015). Algorithmic and High-Frequency Trading. Cambridge
   University Press. Front matter and index only (cjp_2015_frontmatter.pdf/.txt, cjp_2015_index.pdf/.txt);
   chapter text [unverified].
6. Cartea, A., Jaimungal, S. and Ricci, J. (2014). Buy low, sell high: a high frequency trading
   perspective. SIAM J. Financial Mathematics 5(1), DOI 10.1137/130911196; Oxford ORA copy titled
   "Algorithmic trading, stochastic control, and mutually-exciting processes"
   (cartea_jaimungal_ricci_2018_siamrev.pdf/.txt).
7. Cartea, A., Donnelly, R. and Jaimungal, S. (2018). Enhancing trading strategies with order book
   signals. Applied Mathematical Finance 25(1), 1-35. Oxford ORA copy
   (cartea_donnelly_jaimungal_2018_obsignals.pdf/.txt).
8. Almgren, R. and Chriss, N. (2000). Optimal execution of portfolio transactions. December 2000 version
   (almgren_chriss_2000.pdf/.txt, smallake.kr mirror). Journal of Risk 3(2) [venue unverified from text].
9. Ho, T. and Stoll, H. R. (1981). Optimal dealer pricing under transactions and return uncertainty.
   Journal of Financial Economics 9(1), 47-73. NOT fetched; described via refs 1 and 10 [unverified].
10. Ching, W.-K., Gu, J.-W., Yang, Q.-Q. and Siu, T.-K. (2015). On optimal pricing model for multiple
    dealers in a competitive market. arXiv 1512.08866v1; used only for its description of Ho-Stoll (multiple_dealers_2015_review.pdf/.txt).
11. Guilbaud, F. and Pham, H. (2013). Optimal high-frequency trading with limit and market orders.
    Quantitative Finance (as cited by Gueant 2017); arXiv 1106.5040 (guilbaud_pham_2013.pdf/.txt).
12. Gao, X. and Wang, Y. (2020). Optimal market making in the presence of latency. Quantitative Finance
    20(9), 1495-1512; arXiv 1806.05849v3 (gao_wang_2020_latency.pdf/.txt).
13. Moallemi, C. C. and Yuan, K. (2017). A model for queue position valuation in a limit order book.
    Working paper, revision June 2017, Columbia GSB copy (moallemi_yuan_queue_value.pdf/.txt).
14. Huang, W., Lehalle, C.-A. and Rosenbaum, M. (2015). Simulating and analyzing order book data: the
    queue-reactive model. JASA 110(509); arXiv 1312.0563v2 (huang_lehalle_rosenbaum_2015_qr.pdf/.txt).
15. Abergel, F., Hure, C. and Pham, H. (2020). Algorithmic trading in a microstructural limit order book
    model. arXiv 1705.01446v3 (abergel_hure_pham_2020.pdf/.txt).
16. Lehalle, C.-A. and Neuman, E. (2019). Incorporating signals into optimal trading. arXiv 1704.00847v3
    (lehalle_neuman_2019_signals.pdf/.txt).
17. Falces Marin, J., Diaz Pardo de Vera, D. and Lopez Gonzalo, E. (2022). A reinforcement learning
    approach to improve the performance of the Avellaneda-Stoikov market-making algorithm. PLOS ONE
    17(12), e0277042 (falces_marin_2022_plosone.pdf/.txt).
18. Baron, M., Brogaard, J. and Kirilenko, A. (2014). Risk and return in high frequency trading. CFTC OCE
    draft (baron_brogaard_kirilenko_2014_cftc.pdf/.txt); published with Hagstromer in JFQA 54(3), 2019
    [published version not fetched].
19. hftbacktest documentation: "Gueant-Lehalle-Fernandez-Tapia Market Making Model and Grid Trading" and
    "Impact of Order Latency" (hftbacktest_glft_tutorial.html/.txt, hftbacktest_latency_tutorial.html/.txt).
    Open-source practitioner documentation; the latency page yielded no quotable conclusion and is not
    cited for a claim.
20. Databento documentation: MBP-10, MBO, TBBO schema pages and "Queue position of an order" example
    (databento_mbp10, databento_mbo, databento_tbbo, databento_queue_position .html/.txt).
21. CME Group, Micro E-mini S&P 500 contract specifications, via Wayback 2025 (cme_mes_specs_wayback.html/.txt).
22. Lambda, GPU cloud pricing page (lambda_pricing.html/.txt), fetched 2026-10-21.
23. Spooner, T., Fearnley, J., Savani, R. and Koukorinis, A. (2018). Market making via reinforcement learning. arXiv 1804.04216
    (spooner_2018_rl_mm.pdf/.txt). Fetched; not used for any claim.
24. Program file rules/products.py (MES and ES tick values and round-turn costs), repository source, not
    re-verified here.

---

## 15. Evidence table

Saved files are under reports/stage_e28_briefs/pages/C2_Control/. Quotes are verbatim from the .txt
extraction (PDF line breaks and hyphenation joined; Greek letters as extracted).

| Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|
| A-S quotes come from indifference value plus fill-probability calibration | Avellaneda-Stoikov 2008 | "First, the dealer computes a personal indifference valuation for the stock, given his current inventory. Second, he calibrates his bid and ask quotes to the limit order book" | avellaneda_stoikov_2008.txt l.64-67 |
| A-S assume no view on drift | A-S 2008 | "our agent has no opinion on the drift or any autocorrelation structure for the stock" | avellaneda_stoikov_2008.txt l.91-93 |
| HJB derived by dynamic programming, following Ho-Stoll | A-S 2008 | "This type of optimal dealer problem was first studied by Ho and Stoll [6]. One of the key steps in their analysis is to use the dynamic programming principle to show that the function u solves the following Hamilton-Jacobi-Bellman equation" | avellaneda_stoikov_2008.txt l.296-298 |
| Exponential intensity from power-law sizes and log impact | A-S 2008 | "where A = Λ/α and k = αK" | avellaneda_stoikov_2008.txt l.277 |
| Spread independent of inventory under exponential rates | A-S 2008 | "The bid-ask spread in (3.13) is independent of the inventory. This follows from our assumption of exponential arrival rates." | avellaneda_stoikov_2008.txt l.408-409 |
| Inventory policy lowers variance, not mean | A-S 2008 | "the inventory strategy obtains a P&L profile with a much smaller variance"; Table 1 "Inventory 1.29 62.94 5.89" / "Symmetric 1.29 67.21 13.43" | avellaneda_stoikov_2008.txt l.525-530 |
| Ho-Stoll: true price exogenous, quotes around it for inventory | A-S 2008 (secondary) | "In their model, the authors specify a 'true' price for the asset, and derive optimal bid and ask quotes around this price, to account for the effect of the inventory." | avellaneda_stoikov_2008.txt l.39-41 |
| Ho-Stoll: linear demand for dealer services | Ching et al. 2015 (secondary) | "assuming a linear demand relation for dealer sales and purchases" | multiple_dealers_2015_review.txt l.79-80 |
| GLFT add an inventory bound | GLFT 2013 | "we add a bound Q to the inventory that a market maker is authorized to have" | gueant_lehalle_ft_2013.txt l.217-218 |
| Fills independent of price in GLFT | GLFT 2013 | "the point processes (independent of (Wt )t ) giving the number of shares the market maker respectively bought and sold" | gueant_lehalle_ft_2013.txt l.181-182 |
| A-S expansion is poor away from T | GLFT 2013 | "the optimal quotes are almost independent of t, as soon as t is far from the terminal time T. This observation is at odds with the approximations proposed in Avellaneda and Stoikov" | gueant_lehalle_ft_2013.txt l.391-394 |
| A and k depend on the spread | GLFT 2013 | "it is well known by practitioners that A and k have to depend at least on the actual market bid-ask spread" | gueant_lehalle_ft_2013.txt l.1281-1283 |
| GLFT round to tick | GLFT 2013 | "we decided to round the optimal quotes to the nearest tick" | gueant_lehalle_ft_2013.txt l.1272-1273 |
| GLFT gamma is chosen, not estimated | GLFT 2013 | "we decided in our backtests to assign γ an arbitrary value for which the inventory stayed between -10 and 10" | gueant_lehalle_ft_2013.txt l.1287-1289 |
| GLFT real-data test is one day with optimistic fills | GLFT 2013 | "we assumed that our orders were entirely filled when a trade occurred at or above the ask price quoted by the agent" ... "France Telecom on March 15th 2012" | gueant_lehalle_ft_2013.txt l.1291-1295 |
| A-S-type models hardly apply to large-tick queue books | Gueant 2017 | "Models à la Avellaneda-Stoikov can hardly be applied to most stock markets for at least two reasons: (i) the discrete nature of prices (especially in the case of stocks with a large tick size), and (ii) the fact that the very nature of the limit order books, which are queuing systems with priorities and volumes, is not taken into account." | gueant_2017_optimal_mm.txt l.169-171 |
| Cartea-Jaimungal objective is Model B (running penalty) | Gueant 2017 | "holding an inventory is penalized over the time interval [0, T ]. This is typically what is done by Cartea, Jaimungal and their coauthors" | gueant_2017_optimal_mm.txt l.315-316 |
| Closed forms fine near q = 0 | Gueant 2017 | "the closed-form approximations are satisfactory for small values of the inven-[tory]" | gueant_2017_optimal_mm.txt l.2331 |
| Gueant book contents include A-S to GLFT chapter | Routledge page | "IV: MARKET MAKING Market Making: From Avellaneda-Stoikov to Guéant-Lehalle, and Beyond" | gueant_2016_routledge.txt l.39 |
| CJP book has an adverse-selection chapter | CJP front matter | "10.4 Market Making with Adverse Selection" / "10.4.2 Short-Term-Alpha and Adverse Selection" | cjp_2015_frontmatter.txt l.393-395 |
| Market makers without alpha are driven out | Cartea-Jaimungal-Ricci | "HF traders who do not include predictors of short-term-alpha in their strategies are driven out of the market because they are adversely selected by better informed traders" | cartea_jaimungal_ricci_2018_siamrev.txt l.11-13 |
| CJR alpha dynamics | CJR | "dαt = −ζ αt dt + σα dBt + + dM t − − dM t" (jump terms ε± garbled in extraction) | cartea_jaimungal_ricci_2018_siamrev.txt l.597 |
| CJR evidence is simulation | CJR | "We test our model using simulations where we assume different types of HFTs" | cartea_jaimungal_ricci_2018_siamrev.txt l.187 |
| CDJ imbalance definition | CDJ 2018 | "ρt = (Vtb − Vta)/(Vtb + Vta) ∈ [−1, 1]" (layout joined) | cartea_donnelly_jaimungal_2018_obsignals.txt l.168-171 |
| CDJ out-of-sample design | CDJ 2018 | "We use in-sample-data (January to June 2014) to calibrate the model to eleven equities traded in the Nasdaq exchange, and use out-of-sample data (July to December 2014) to test the performance of the strategy." | cartea_donnelly_jaimungal_2018_obsignals.txt l.27-29 |
| Naive two-sided posting loses | CDJ 2018 | "indicating the failure to make positive profits through roundtrip trades when always posting LOs on both sides of the LOB" | cartea_donnelly_jaimungal_2018_obsignals.txt l.1538-1539 |
| Front-of-queue assumption biases results | CDJ 2018 | "So far the strategy assumes that the agent's LOs are always at the front of the queue. This assumption is unrealistic and introduces a bias in the profitability of the trading strategy." | cartea_donnelly_jaimungal_2018_obsignals.txt l.1622-1624 |
| With back-of-queue fills, some stocks negative | CDJ 2018 Table 7 | "ARCC -4.43 -3.79 -4.75 -5.02 -2.28 -3.34 -4.40 -3.18" | cartea_donnelly_jaimungal_2018_obsignals.txt l.1706 |
| CDJ assume zero latency | CDJ 2018 | "we assume that the agent has zero latency – market changes are followed by immediate repositioning of LO's. In reality, for an agent with colocated servers, a latency on the order of 10ms is not unrealistic." | cartea_donnelly_jaimungal_2018_obsignals.txt l.818-820 |
| A-C sinh trajectory and half-life | Almgren-Chriss 2000 | "The value θ is exactly the amount of time it takes to deplete the portfolio by a factor of e." | almgren_chriss_2000.txt l.683-684 |
| A-C monotonicity can fail with drift | Almgren-Chriss 2000 | "This can cease to be true if there is drift or serial correlation in the price movements." | almgren_chriss_2000.txt l.649 |
| Signals in execution are recent | Lehalle-Neuman | "The inclusion of signals (i.e. short term predictors of price dynamics) in optimal trading is a recent development" | lehalle_neuman_2019_signals.txt abstract |
| Guilbaud-Pham: spread in ticks, priority by one tick | Guilbaud-Pham | "The bid-ask spread of the LOB is modelled by a Markov chain with finite values, multiple of the tick size" | guilbaud_pham_2013.txt l.20-21 |
| Guilbaud-Pham: simulated NIR must be checked on real data | Guilbaud-Pham | "the annualized value of the NIR (obtained by simple extrapolation) is 47, but this simulated data backtest must be completed by a backtest on real data" | guilbaud_pham_2013.txt l.1162-1165 |
| Gao-Wang: per-fill value decomposition | Gao-Wang 2020 | "Value of an order = (spread capture − adverse selection cost) × fill probability." | gao_wang_2020_latency.txt l.581 |
| Gao-Wang: no profit if uninformed fills too rare | Gao-Wang 2020 | "then the market maker can not make a positive profit regardless of how many times the market maker quotes" | gao_wang_2020_latency.txt l.695-697 |
| Gao-Wang: latency hurts | Gao-Wang 2020 | "latency can be an additional source of risk and latency impacts negatively the performance of market makers" | gao_wang_2020_latency.txt l.18-19 |
| Queue value comparable to spread | Moallemi-Yuan | "for some large tick-size stocks, we find that queue value can be of the same order of magnitude as the bid-ask spread" | moallemi_yuan_queue_value.txt l.29-30 |
| Large-tick definition; index futures included | Huang-Lehalle-Rosenbaum | "A large tick asset is defined as an asset whose bid-ask spread is almost always equal to one tick"; "index futures (among which large tick assets are quite numerous" | huang_lehalle_rosenbaum_2015_qr.txt l.96, 240-241 |
| Queue-reactive intensities by MLE | HLR 2015 | "it is easy to estimate λLi (n), λCi (n) and λMi (n) by the maximum likelihood method" (layout joined) | huang_lehalle_rosenbaum_2015_qr.txt l.331-333 |
| High-dimensional LOB MDP tested on simulation only | Abergel-Hure-Pham | "Several computational tests are performed on simulated data to illustrate the efficiency of the computed optimal strategy." | abergel_hure_pham_2020.txt abstract |
| A-S tuned model negative on BTC-USD | Falces Marin 2022 Table 2 | "Mean -0.43 -0.36 -0.24 -0.11 -0.13" (FOIC, LIIC, AS-Gen, Alpha-AS 1, Alpha-AS 2; daily Sharpe) | falces_marin_2022_plosone.txt l.1230 |
| E-mini HFT revenue concentrated in fast, liquidity-taking firms | Baron-Brogaard-Kirilenko 2014 | "revenue is concentrated among a small number of HFT firms who achieve greater investment performance through liquidity-taking activity and higher speed" | baron_brogaard_kirilenko_2014_cftc.txt l.14-15 |
| Small traders lose per contract at 1 minute | BBK 2014 | "Small traders experience a much larger loss of -$3.49" | baron_brogaard_kirilenko_2014_cftc.txt l.1452-1453 |
| Practitioner GLFT breaks even only with rebates | hftbacktest docs | "Improved, but even when accounting for rebates, it can only achieve breakeven at best." / "it's evident that profits are generated through rebates" | hftbacktest_glft_tutorial.txt l.577, 623 |
| Trade-through calibration ignores queue | hftbacktest docs | "only market trades that cross our quote will be counted as executed" | hftbacktest_glft_tutorial.txt l.135 |
| mbp-10 content | Databento docs | "MBP-10 (market by price) provides every order book event across the top ten price levels, keyed by price." | databento_mbp10.txt |
| mbo content | Databento docs | "Market by order (MBO) provides every order book event across every price level, keyed by its order ID." | databento_mbo.txt |
| tbbo content | Databento docs | "BBO on trade (TBBO) provides every trade event alongside the BBO immediately before the effect of each trade." | databento_tbbo.txt |
| Exact queue position needs mbo | Databento example | "We will use the MBO schema ("L3" data), which assigns a unique ID to every order in the book, to exactly track this queue position." | databento_queue_position.txt |
| MES tick | CME (Wayback) | "has a minimum tick of 0.25 index points" | cme_mes_specs_wayback.txt l.44 |
| Cloud price | Lambda pricing | "NVIDIA A10 24 GB 30 226 GiB 1.3 TiB SSD $1.29" | lambda_pricing.txt l.8 |

---

## 16. What I could not do, failures and caveats

- Ho and Stoll (1981) original not retrieved (no open copy; one WebSearch and one secondary search).
  Its content here is secondary and marked [unverified].
- Gueant (2016) and Cartea-Jaimungal-Penalva (2015) books: only contents pages; equations taken from
  the authors' open papers instead.
- Almgren et al. (2005) impact-estimation paper: the NYU URL returned an HTML 404 (logged, file
  deleted); no empirical post-publication test of Almgren-Chriss on futures was fetched.
- First Almgren-Chriss URL (upenn) also returned a 404 page; the smallake.kr mirror worked.
- RunPod pricing page saved but not parsed; only Lambda prices are used.
- hftbacktest's latency tutorial page carried no quotable conclusion in its text (figures only); not
  used for a claim.
- No market data read. Every MES/ES number other than tick size and the program's round-turn costs is
  an assumption (sigma, A, k, gamma, markout s.d., fill counts). The pilot replaces them.
- Equation numbers: A-S numbers are those of the 2006 draft; the published 2008 numbering may differ.
- WebSearch calls used: 12 of the 60 budget. No budget notice was received.
- Times: work ran 2026-10-21 from 02:21 PDT (log.tsv has per-file UTC and PDT times).

## Corrections after review (Stage E.28, MathReviewer G4)

- MG4-01: section 4.5(c) gamma thresholds replaced by the exact bounded values (0.13 to 0.19; 0.79 to 0.95; 0.022 to 0.035), approximation values kept in brackets. The script C2_threshold.py (sigma applied twice) was not edited here; see R_fix_G4.md.
- MG4-02: the q = 5 drift is now attributed to the Q = 10 inventory bound (Q = 20 matches the approximation); approximation called the Q -> infinity limit; the Gueant 2017 quote is attached to the bounded case only.
- MG4-03: ORCL row corrected to Table 4 (11.65 to 34.25) with the Table 5 range (11.75 to 33.29) labelled separately.
- MG4-04: the H-GW1-first ordering argument now holds for the touch variant of H-GLFT1 only; H-CJ2 can still pass on gated buckets.
- MG4-05: sample for H-AS0 stated as about 1,450 fills (1,440 with s.d. 3.162), in 3.6 and in the hypothesis table.
- MG4-06: H-GW1 sample stated as ~800 (ES) or ~900 (MES), with the two margins.
- MG4-07: "(Greek transliterated)" added to the two transliterated quotes (A-S lines 260-277 and the HJB quote); "(layout joined)" added to the HLR queue-reactive quote. The other listed quotes already carry the extraction caveat.
- MG4-09: "Proposition 3 and" removed; the citation is now the display lines 612-630 only.
- Not applied (style NOTE): MG4-08.

Lead note (Stage E.28, after MathReviewer G4): the helper script work/C2_Control/C2_threshold.py still contains the
sigma-twice error that MG4-01 found; the text above is corrected and the script's printed threshold is superseded.
