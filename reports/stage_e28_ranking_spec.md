# Stage E.28 Part A: ranking specification (frozen before any lookup)

Written by the lead (Opus 5.5, xhigh) at 2026-10-21 02:12 PDT, before any Layer 1 or Layer 2 lookup for this
stage. Its sha256 is logged in reports/stage_e28_STATE.md. Nothing in this file changes after the hash. A
superseded version, if a reviewer's BLOCKING finding forces one, is kept on disk beside it under a new name with
its own hash, and the diff is shown in the return.

What the lead had read before writing it: the stage prompt, docs/DECISIONS.md V42 to V44, the E.26 prompt, and the
verdict summary of reports/E.19_RETURN.md (Topstep funnel economics at zero edge). Nothing about the other four
firms, the platforms' fill rules or any contract's microstructure was read for this stage before the hash.

## 0. Units and candidates

A Layer 1 candidate is one CME Globex product code. Micro, mini and full-size versions of the same underlying are
separate candidates, because they have separate order books, queues and participants.

| Family | Candidates |
|---|---|
| Crude oil | MCL, QM, CL |
| Natural gas | MNG, QG, NG |
| Metals | MGC, GC, SIL, SI, MHG, HG |
| FX | M6E, 6E, M6A, 6A |
| Crypto | MET, ETH (CME Ether), MBT, BTC |
| Equity index | M2K, RTY, MYM, YM, MNQ (the baseline), NQ |
| Rates | the micro Treasury yield futures (2YY, 5YY, 10Y, 30Y) and, as their full-size cousins, ZT, ZF, ZN, ZB |
| Grains | the micro grains (MZC, MZS, MZW, MZL, MZM, or whatever codes CME lists), the mini grains if still listed (XC, XK, XW), and ZC, ZS, ZW, ZL, ZM |

A Layer 2 pair is (firm, candidate) for each Layer 1 survivor at each of Topstep, Lucid, Tradeify, MFFU (My Funded
Futures) and Bulenox where that firm lists the product.

The ranking scores the candidate's suitability for a limit-order (passive) strategy run by an automated retail
system: size 1 contract, latency of tens of milliseconds, no co-location, no exchange fee rebates, at the back of
the visible queue when it joins.

## 1. Data rules for the facts

- Every quantitative fact is reported with its source (file path or URL with fetch time, and a verbatim quote for
  web sources) and its date or window. A fact without a source counts as unknown.
- Owned data may be read only for magnitudes (volume, ranges, 1-minute changes), only from files dated before
  2023-11-01 (the pilot window 2023-11-01..2024-02-29 is kept clean for Part B), and never from any file dated
  2024-03-01 or later. The owned mbp-1 sample dates (2025-2026) are not read.
- The standard magnitude window, where owned 1-minute bars exist, is 2022-11-01..2023-10-31 (12 months).
- The main session for session-split statistics is 06:30-13:00 America/Vancouver (09:30-16:00 New York) on CME
  trade dates; the rest of the Globex day is the overnight session.
- sigma_1m: the standard deviation of 1-minute close-to-close price changes in the main session, in ticks.
- R_d: the median daily high-low range of the front contract over the standard window, in ticks.
- ADV: the median daily volume (all expiries, Globex) over the standard window, in contracts; or the most recent
  12-month average daily volume published by CME or a regulator if no owned bars exist.
- Unknown facts take the conservative default named in each criterion, and the table marks them "u".

## 2. Layer 1: contract feasibility (score 0 to 4 per criterion)

L1 = 0.25 C1 + 0.20 C2 + 0.15 C3 + 0.15 C4 + 0.10 C5 + 0.15 C6.

C1, adverse selection and competition (weight 0.25). Two ratings from the reader's evidence:
- (a) uninformed or retail flow share: high (at least 40% of volume retail or uninformed, or CME or a regulator
  describes the product as predominantly retail), medium, or low (dominated by commercial hedgers, institutions or
  professional traders). Unknown counts as medium.
- (b) professional liquidity-provision intensity at the touch: low (no market-maker program found, few
  high-frequency participants documented, spread usually wider than 1 tick), medium, or high (an exchange
  market-maker or incentive program, documented HFT dominance, or a 1-tick spread with deep queues most of the
  main session). Unknown counts as high.
C1 = 2 + (a: high +1, medium 0, low -1) + (b: low +1, medium 0, high -1), so 0 to 4.

C2, queue mechanics for a back-of-queue order (weight 0.20). Primary number: QV = median displayed size at the best
bid or ask (contracts) divided by median traded volume per minute (contracts per minute), both in the main session,
in minutes. Score: QV <= 0.5 gives 4; <= 2 gives 3; <= 5 gives 2; <= 15 gives 1; > 15 gives 0.
If QV cannot be sourced, the proxy r = 1 / sigma_1m (tick size over the 1-minute SD; a large r means a
tick-constrained book with long queues) is used and marked "proxy": r >= 1.0 gives 1; 0.5 <= r < 1.0 gives 2;
0.1 <= r < 0.5 gives 3; r < 0.1 gives 2 (the tick is small against the noise, so one tick of spread capture is
small). The proxy never scores 4 or 0. If neither is available, C2 = 1.

C3, liquidity and its stability across sessions (weight 0.15). ADV >= 200,000 gives 4; >= 50,000 gives 3;
>= 10,000 gives 2; >= 1,000 gives 1; < 1,000 gives 0. Minus 1 (not below 0) if the sourced median overnight spread
is at least 3 times the main-session median spread. Unknown ADV gives 1.

C4, information events, gaps and limit moves (weight 0.15). Start at 4 and subtract 1 for each that holds, not
below 0:
- two or more scheduled product-specific high-impact releases per week (EIA crude and natural gas inventories,
  USDA reports, and the like; the US macro calendar every product shares does not count);
- weekend-gap exposure from an underlying that trades while Globex is closed (crypto spot);
- a daily price limit or circuit breaker hit on at least one day per year on average over 2019-2024;
- at least 10 days per year on average over 2019-2024 with an absolute daily return above 4 times the daily
  standard deviation of that year.
An item whose fact is unknown is counted as holding (conservative).

C5, volatility per tick (weight 0.10). From sigma_1m in ticks: 1.5 to 6 gives 4; 1 to 1.5 or 6 to 10 gives 3; 0.5 to
1 or 10 to 20 gives 2; 0.25 to 0.5 or 20 to 40 gives 1; else 0. Boundaries go to the higher score. Unknown gives 1.

C6, published microstructure evidence (weight 0.15). 4: a peer-reviewed paper or a documented study on this product
(or its micro, mini or full-size version on the same underlying) showing short-horizon predictability from
order-book variables (order-flow imbalance, queue imbalance, trade signs) or profitable passive liquidity provision
net of costs. 3: such evidence on a close cousin (same asset class on CME Globex). 2: evidence only for futures or
the asset class broadly. 1: nothing found within the reader's search budget. 0: published evidence that such
patterns are absent on this product or arbitraged away.

Layer 1 gate. A candidate survives only if all hold:
- L1 >= 2.00;
- no criterion scores 0;
- it traded on Globex (GLBX.MDP3) on at least 60 trade dates inside 2023-11-01..2024-02-29, so the pilot could be
  bought for it.
Candidates below the gate are listed with their scores but not ranked further.

## 3. Layer 2: firm-contract economics (score 0 to 4 per criterion)

L2 = 0.40 E + 0.10 D + 0.10 R + 0.15 A + 0.10 F + 0.05 P + 0.10 Rel.

Notation: s(x; x0) = 4 * max(0, 1 - x / x0).

The economic model (fixed here; EconCoder implements it on E.19's simulator, prop_econ/, with the rules record
E.26 refreshes for Topstep and per-firm records for the other four):
- The account is the firm's standard 50K plan: the first 50K evaluation plan on its pricing page on the lookup
  date, with its funded stage. If no 50K plan exists, the nearest size below.
- The strategy trades T = 20 round trips per trading day, 1 contract each, independent trades. Gross P&L per trade
  in ticks is normal with mean mu and standard deviation sigma_T = sigma_1m (a one-minute holding scale).
- Cost per round trip in ticks: limit case c_lim = F_rt, the firm's round-trip commission and fees for that product
  divided by the tick value (both legs passive, so no spread is paid; adverse selection is not a cost here, it is
  part of the gross edge mu, which the pilot measures as markouts). Market case c_mkt = F_rt + S_rt, with S_rt the
  sourced median main-session spread in ticks (1 if unknown).
- Daily P&L in USD is normal with mean T (mu - c) v and standard deviation sqrt(T) sigma_T v, with v the tick value.
- 20,000 paths per pair and case, common random numbers across pairs, a fixed seed.
- mu* (break-even): the smallest mu on a 0.01-tick grid from 0 to 4 ticks at which expected net cash per cycle
  (all withdrawals minus all fees, a cycle as E.19 defines it) is at least 0. mu*_lim and mu*_mkt for the two
  cases.
- mu10K: the smallest mu on the same grid at which the probability of reaching USD 10,000 of net cash (withdrawals
  minus fees) within 250 trading days, one account at a time, restarting after each failure, is at least 50%;
  limit case only.
- Cost per attempt: the expected fees paid per evaluation attempt at mu = 0 in the limit case.
- A firm rule the simulator cannot represent is mapped to its most conservative representable form, and the
  mapping is logged.
- If a fee is unknown, the highest fee found for that product class at the other four firms is used and marked "u".
  If a mu exceeds 4 ticks, it is reported as "> 4" and scores 0.

E, economics (weight 0.40): E = 0.60 s(mu*_lim; 2.0) + 0.15 s(mu*_mkt; 3.0) + 0.25 s(mu10K; 3.0).

D, room in the dollar limits (weight 0.10). room = the firm's maximum loss limit (or trailing drawdown) at the 50K
plan in USD divided by (R_d v), the dollar value of one median daily range for 1 contract. room >= 4 gives 4; >= 3
gives 3; >= 2 gives 2; >= 1 gives 1; < 1 gives 0. The table also shows the daily loss limit in ticks and the
position limit, and notes micro-to-mini scaling.

R, product restrictions (weight 0.10). 4: no restriction on the product beyond a firm-wide rule that applies to every
product; 3: restricted around at most 2 scheduled events per week; 2: restricted around a recurring weekly event
central to the product (for example EIA inventories for crude or natural gas); 1: trading hours limited so that at
least 25% of the product's Globex hours are excluded, or restrictions that combine the 2 and 3 cases. Unknown gives 1.

A, automation and order-rate rules (weight 0.15). 4: automated trading through an API explicitly permitted in both
the evaluation and funded stages, and no published order-rate, minimum-hold or scalping rule beyond the platform's
technical rate limit; 3: permitted, with a published rate limit, minimum hold or scalping rule that a 20 round-trip
per day strategy with holds of about a minute meets; 2: permitted only through a named third-party platform or with
case-by-case approval, or a published rule makes the 1-minute-hold strategy borderline; 1: the terms do not say
either way. 0: prohibited, or a rule forbids holds of about a minute (gate: the pair is excluded).

F, the simulated fill rule for resting limit orders (weight 0.10), for the platform the firm's evaluation and funded
accounts run on. 4: documented, and it fills on traded volume at the price after a queue (a queue or trade-volume
model close to the real market); 2: documented, and it fills on a touch (lenient: the firm may review profits that
rest on it, and Lucid-style bans on exploiting sim fills apply); 1: documented and fills only on a trade-through
(passive strategies are filled only adversely), or undocumented after the search budget.

P, platform, API and latency (weight 0.05). Start at 4 and subtract 1 for each that holds, not below 0: no native or
documented API (automation only through a desktop platform's scripts); no native OCO or bracket orders on the API; a
VPS near Chicago is prohibited or unknown; a documented API rate limit below 10 orders per second or unknown.

Rel, reliability and eligibility (weight 0.10). Start at 4 and subtract, not below 0: 1 if operating under 2 years;
1 if documented payout delays, denials or disputes in the 12 months before the lookup date; 1 if two or more
material adverse rule changes in those 12 months; 2 if a regulatory action against the firm itself. The table
also shows the payout track record and speed, actions against close peers, and the Canada-specific payout terms
(not scored). Canadian tax treatment gets one line in the ranking file and is not scored.

Layer 2 gates. A pair is excluded (listed, not ranked) if any holds: the firm does not list the product for its
50K plan; A = 0; the firm does not accept British Columbia residents; the strategy would need to exploit a sim
fill quirk to be profitable (by construction it does not, since mu is measured under the real-market fill model).

## 4. Combination, ties and selection

Pair score S = 0.50 L1 + 0.50 L2, on 0 to 4, computed from unrounded criterion scores.

Order by S, highest first. Two pairs tie if their S values are equal when rounded to 2 decimals. Ties are broken in
this order: lower mu*_lim; then higher L1; then lower cost per attempt; then contract code, then firm name,
alphabetically. Nothing else reorders the table.

The top pair is rank 1. Ranks 2 to 5 are the next four named. Nothing is bought for them. The pilot of Part B buys
data only for the top pair's contract.

MNQ is scored like every other candidate and shown as the baseline. Its rank is reported wherever it falls.

## 5. Blinding

- Readers report facts and the sources behind them. They do not score.
- C1 (a) and (b), C6, R, A, F and the Rel deductions are rated by a scorer who did not read the sources, from fact
  sheets with product codes, firm names and platform names replaced by labels; the lead holds the key.
- The quantitative scores (C2, C3, C5, D, E, P counts and the C4 counts) are computed by a script from the fact
  table.
- RankingReviewer-FableXHigh recomputes every number in the table from the fact files and the script.
