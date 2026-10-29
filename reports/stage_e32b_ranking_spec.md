# Stage E.32b: ranking specification for directional strategies (frozen before any new lookup or score)

Written by the lead (Opus 5.5, effort max) on 2026-10-28 from 22:31 PDT, before any new fact lookup, volatility run or
score of this stage. Its sha256 is in reports/stage_e32b_ranking_spec.sha256 and reports/stage_e32b_STATE.md. Nothing
here changes after the hash. If a reviewer's BLOCKING finding forces a change, a new version is written beside this
file under a new name with its own hash, the diff is shown in the return, and this version stays on disk.

What the lead had read before writing it: the stage prompt (amended, commit 3a8edf0); docs/DECISIONS.md V37, V38,
V42, V49 to V56; reports/stage_e28_ranking_spec.md and stage_e28_ranking.md; A0_contract_stats.md (method sections);
A3_facts.md (firm table rows); A3_econ.md (sections 1 and 2.1); A3_lead_rulings.json and _v2.json; E.28 READER_RULES.md;
E.29 return section 1; E.31 return sections 1 and 7; E.33c return sections 1, 2, 3.7 (v) and 7; protocol 0.3 P3.8 and
P7.2; the planner research notes for E.31 and E.32; the spend ledger's field names and per-schema quote counts (no
prices read); the owned one-minute bar folder and file names (no file opened). Model and method follow E.28's spec
except where this file says otherwise.

## 0. Units, candidates, families

- A Layer 1 candidate is one CME Globex product code, as in E.28 section 0: the same 47 codes in the same 8 families
  (crude MCL QM CL; natgas MNG QG NG; metals MGC GC SIL SI MHG HG; fx M6E 6E M6A 6A; crypto MET ETH MBT BTC; equity M2K
  RTY MYM YM MNQ NQ; rates 2YY 5YY 10Y 30Y ZT ZF ZN ZB; grains MZC MZS MZW MZL MZM XC XK XW ZC ZS ZW ZL ZM).
- NQ is excluded (V49): listed as "excluded (V49)", never scored, never ranked. It still counts as a family member
  where a family-level share is computed (D2 c).
- MNQ is scored like every other candidate and shown as the baseline, as in E.28.
- No code is added. ES, MES and the program's other owned roots stay outside the universe (open choice).
- Underlying: the commodity, index, rate or currency a code is written on. Codes on the same underlying are siblings
  (for example MCL, QM and CL; MZM and ZM; MBT and BTC; 10Y and ZN are NOT siblings for price transfer, see 2.4).
- Leader of a satellite (D4): the sibling with the largest USD-notional ADV on the same underlying.
- A Layer 2 pair is (firm, candidate) for each Layer 1 survivor at Topstep, Lucid, Tradeify, MFFU and Bulenox where the
  firm lists the product for its standard 50K plan (E.28 A3_firm_products.json, updated only by verified changes).
- The strategy being ranked: a directional one-lot strategy run by an automated retail system, entering and exiting by
  market order (or a limit order priced under the trade-through rule, V50), at most 20 round trips a trading day, holds
  from 5 minutes to the session close, latency of tens of milliseconds to one second, no co-location, no rebates.

## 1. Facts: sources and data rules

- Every quantitative fact carries its source (file path, or URL with UTC and PDT fetch time, sha256 of the saved page and
  a verbatim quote) and its date or window. A fact without a source counts as unknown and takes the rule of its
  criterion (marked "u").
- F1: E.28's sourced facts are reused with their citations where the meaning is unchanged: fees, listing, position
  limits, automation, reliability, platforms, ADV, sessions and limits (A1_*.json, A2_firm_*.json, A2_platforms.json,
  A3_facts.json, A3_firm_products.json). A reader that finds a changed fact records the new value with its source;
  the new value is used and the old one is shown beside it.
- Lucid fees: if Lucid's all-in fee (commission plus exchange and NFA fees) is still not stated by Lucid, E.28's rule
  RR-05 applies: the highest fee for that product at the other four firms, marked u.
- The ADV used is E.28's (A0 v_0 front-contract median over the standard window, or the published all-expiry figure
  for codes without owned bars); a newer figure a reader sources is shown beside it, not substituted.
- Spread: the sourced median main-session bid-ask spread in ticks (S). Where none is sourced, S = 1 (u).
- Evidence rules (E.28 OC-6, RR-03 carried over): a rating at either extreme of a judgment scale (0, or 3 and above on
  D6 and Q2; 2 on D3 s1 or s2) may not rest only on evidence known from an abstract or a search snippet ([unverified]).
  Such a rating is capped at the next level inward (D6 and Q2: at most 2 from above, at least 1 from below; s1, s2: 1).

## 2. F3: volatility at horizons (script; volatility statistics only, never strategy outcomes)

2.1 Files. Only data/vendor/databento/GLBX.MDP3/ohlcv-1m/<ROOT>_v_0/range=YYYY-MM-01_....dbn.zst files whose range
starts on or after 2022-11-01 and ends on or before 2023-11-01 (the 12 monthly files 2022-11 to 2023-10). The script
refuses every other path before opening it (allow-list on the resolved path), refuses any path containing mbo, mbp,
tbbo, holdout, sealed or enc, and logs every open. Never opened: holdout-2, the March 2024 embargo, the research window,
anything dated 2024-03-01 or later, and ZM, ZS, ZL from 2017-05-01 to 2020-11-30 (the E.32 test seal). The lead or the
coder runs `data.holdout status`, `soy_test_seal.py status` and `guard33.py dry-check` before and after the run and
saves the outputs.

2.2 Trade dates, sessions, grid. As E.28 A0 (A0_contract_stats.md, Method): trade date by the 17:00 CT rule; EARLY_HALT
dates of the group calendar excluded; main session = bar start in [06:30, 13:00) America/Vancouver cut to the product's
scheduled session (grains 06:30-11:20 PT); minute grid with the close carried forward; a change is kept only if both
ends carry the same instrument_id (rolls dropped). L_main = the product's main-session length in minutes.

2.3 Statistics per root, in ticks (vendor price / vendor tick, rules/products.py):
- For h in {1, 2, 5, 15, 30, 60, 120, 240} minutes: D_h(t) = close(t + h) - close(t) for every main-session grid
  minute t with t + h inside the same trade date's main session and the same instrument at both ends (overlapping
  starts). sigma_h = SD of D_h (ddof 1); m_h = mean |D_h|; also median |D_h|, p99 |D_h| and the count of pairs.
- OC: last main-session close minus first main-session close per trade date: sigma_OC, m_OC.
- Overnight (reported apart from the intraday rows): close-to-close between consecutive trade dates' main-session
  closes (sigma_cc, m_cc), and main-session close to the next trade date's first main-session close (sigma_on, m_on);
  same instrument at both ends.
- R_d: E.28's definition (full trade-date high minus low of the instrument in the day's last bar): median and p99.
  Also the median main-session high-low range.
- The median main-session close price (price units, for notional value) and L_main.
- Nothing else: no signed or conditional statistic, no autocorrelation, no signal.

2.4 OC-1 transfer (E.28's rule): a code without owned standard-window bars takes its sibling's price statistics in
ticks times (sibling tick size / own tick size), flagged OC1. Transfers only between codes on the same price of the
same underlying (MNQ from NQ, M2K from RTY, MYM from YM, QM from CL, QG and MNG from NG, M6E from 6E, M6A from 6A, BTC
from MBT, the micro and mini grains from their full-size grain). No transfer between yield-quoted and price-quoted
contracts (the micro yields 2YY 5YY 10Y 30Y) and none where no sibling is owned (SI, SIL, MET, ETH): their sigma is
unknown. Volume statistics never transfer.

## 3. Layer 1: directional suitability of a contract (each criterion 0 to 4)

L1 = 0.30 D1 + 0.15 D2 + 0.15 D3 + 0.15 D4 + 0.10 D5 + 0.15 D6. Weights as the prompt gives them; the lead made no
adjustment (they sum to 1 and follow the prompt's emphasis on cost per sigma).

D1, cost in volatility units (0.30). c_RT = S + 0.5 ticks: the firm-independent market-order round trip, one median
spread S (ticks) plus a slippage allowance of 0.5 tick per round trip (0.25 a side; a stated assumption, no measured
source; variants 0 and 1.0). For each h, r_h = c_RT / sigma_h, banded: r_h <= 0.025 gives 4; <= 0.05 gives 3;
<= 0.10 gives 2; <= 0.20 gives 1; > 0.20 gives 0 (boundaries to the higher score). D1 = the mean of the band scores at
h = 30, 60, 120 and 240 minutes (the user's prior band). r_5, r_15 and r_OC are reported, not scored. Reason for the
bands, fixed before any lookup: a sign forecast with correlation rho to the h-minute move earns about
0.8 rho sigma_h gross per trade; published out-of-sample intraday R^2 of about 0.25% to 1.6% (rho 0.05 to 0.13) gives
roughly 0.04 to 0.10 sigma_h. So 4 means a weak signal (rho about 0.03-0.05) clears the cost, 3 needs the better
published values, 2 the best in-sample ones, 1 more than any published intraday result, 0 far more. Unknown sigma: the
contract fails the Layer 1 gate (below), so D1 is not needed.

D2, crowding and attention (0.15). D2 = max(0, 4 - a - b - c - d):
- a = 1 if a published automated-trading or HFT share of volume of at least 50% exists for the product, its leader
  (for a satellite) or, failing those, its CME product group (most specific post-2012 figure); 0 if that figure is below
  50%; 1 if unknown. Rated blind from the sourced figure.
- b = 1 if a CME market-maker, lead market-maker or volume-incentive program for the product's outright futures (for a
  satellite: its leader's) was in force at any time in 2021-2026 (sourced); 0 if a source documents none; 0.5 if
  unknown. Rated blind.
- c = 1 if the product, or for a satellite its leader, has the largest USD-notional ADV in its E.28 family
  (ADV x contract multiplier x F3 median close; NQ included in the comparison); else 0. Script.
- d = research attention, script: for each underlying, the OpenAlex count (meta.count) of works matching
  title_and_abstract.search for the underlying's phrases (section 9.1) AND (intraday OR "intra-day" OR
  "high-frequency" OR "high frequency" OR microstructure), run once with the exact URLs logged. Underlyings are split
  into terciles by count: top tercile d = 1, middle 0.5, bottom 0 (equal counts take the higher tier). If the count
  cannot be obtained for an underlying, d = 0.5 (u). Every code on an underlying shares its d.
Less attention scores higher (V51). For a satellite (D4, Sat by rule i or ii) a, b and c use the leader's facts,
because its direction is set there; variant D2_own uses its own facts.

D3, structural signal sources (0.15). D3 = min(4, s1 + s2 + s3), each sourced, rated blind:
- s1 (0/1/2): 2 = a sourced economic spread relationship (for example the soybean crush, the crack, a cross-asset
  pair) with documented intraday cointegration, mean reversion or lead-lag at horizons of a minute or more; 1 = a
  sourced relationship that is mechanical or arbitrage-tight (calendars, mini/full or micro/full pairs, implied spread
  books) or documented only at daily or longer horizons; 0 = none sourced.
- s2 (0/1/2): 2 = sourced evidence that a scheduled release's price effect on the product or its underlying keeps moving
  the mean (drift or slow adjustment, not volatility alone) for 5 minutes or more after the release; 1 = scheduled
  product-specific or macro releases that move it, absorbed within seconds to a few minutes or with absorption speed not
  documented; 0 = none documented.
- s3 (0/1): 1 = a sourced session structure with a documented handoff effect on the product or its underlying (the
  day-session open after an overnight break or pause, a regional open or close, the settlement window); 0 otherwise.
Unsourced items score 0.

D4, tradability at one contract (0.15). D4 = max(0, 4 - L - J - 2 Sat):
- L (0/1/2), liquidity for market orders without walking the book: 2 if ADV < 1,000, or the sourced median spread is
  above 2 ticks, or the sourced median displayed size at the best bid or ask is below 2 contracts; 1 if
  1,000 <= ADV < 10,000, or the median spread is above 1 and at most 2 ticks, or the median touch size is below 5
  contracts; else 0. Unknown ADV: L = 1 (u). An unsourced spread or touch size does not count.
- J (0/1), jump and limit-move risk: 1 if the one-contract USD value of the p99 daily range R_d (F3) exceeds the
  reference daily loss limit DLL_ref = USD 1,000 (the lowest 50K daily loss limit among the five firms, A3_facts.md);
  else 0. Unknown: 1.
- Sat (0/1), satellite: 1 if (i) a sibling on the same underlying has at least 5 times the candidate's USD-notional ADV,
  or (ii) the candidate is financially settled off a sibling's settlement price (sourced), or (iii) a sourced
  information-share or price-discovery study attributes at least 75% of the candidate's price discovery to another
  market (rated blind). If a larger-size sibling exists and the ADV ratio is unknown, (i) counts as holding.
Scoring a satellite low follows the prompt: its direction is set elsewhere. Variant sat1 uses a deduction of 1.

D5, data access (0.10). D5 = max(0, 4 - h - k - o - p), script from the DataAccess census:
- h: Databento GLBX.MDP3 MBO history for the product starts on or before 2017-06-30: 0; 2017-07-01 to 2020-12-31: 1;
  2021-01-01 or later: 2; unknown: 1.
- k: approximate price of one month of front-contract MBO (published Databento pricing, or the program's ledger quotes
  scaled to a month and labelled as an estimate): at most USD 10: 0; at most USD 50: 1; above USD 50: 2; unknown: 1.
- o: 0 if the program owns one-minute bars or book data for the product or a same-underlying sibling covering at least
  36 months before 2024-03-01 outside every sealed window; else 1.
- p: 1 if every pre-2024-03 window of 36 months or more of the product's underlying has been read by a registered
  bar-based or directional search (the 838 trials) and none is sealed for a future test; else 0; unknown 0.
The census also lists, for each code, the sealed and spent windows with their sources (reported, not scored beyond p).

D6, published directional evidence (0.15), rated blind: 4 = a peer-reviewed paper or documented study on this product or
a same-underlying sibling showing intraday directional predictability at horizons from 5 minutes to the session, out of
sample or net of costs, on data after 2010; 3 = such evidence in sample only, or before 2010, or on a close cousin (same
asset class on CME Globex) after 2010; 2 = evidence only for futures or the asset class broadly (multi-asset studies
that include the class count here), or for another venue of the same underlying; 1 = nothing found within the search
budget; 0 = full-text published evidence that such predictability is absent, insignificant after costs, or arbitraged
away on this product after 2010. Correctly signed contemporaneous order flow does not count, nor does predictability
only at horizons under 5 minutes. A satellite takes its leader's evidence.

Layer 1 gate. A candidate fails Layer 1 (listed with its scores, not ranked) if any holds:
- D4 = 0;
- sigma_60 < 2 x c_RT, shown as the arithmetic "sigma_60 = x ticks vs 2 x (S + 0.5) = y ticks";
- sigma_60 is unknown (no owned bars and no sibling under 2.4).
E.28's other Layer 1 gates (L1 >= 2.00, no criterion at 0, the 60-date pilot gate) are not used: the prompt lists the
gates, and a 0 on D2 or D6 is a legitimate directional fact. L1 < 2.00 is flagged, and variant L1min2 applies E.28's
L1 >= 2.00 gate.

## 4. Layer 2: firm x contract for directional one-lot strategies (each criterion 0 to 4)

L2 = 0.40 E + 0.15 R + 0.15 A + 0.15 D + 0.10 Rel + 0.05 P. E.28's F (sim fill rule) is dropped; the trade-through
rule is assumed everywhere (V50). Notation s(x; x0) = 4 max(0, 1 - x / x0).

E, economics under market orders (0.40). E.28's model (spec section 3; A3_econ.md 2.1; code
reports/stage_e28_briefs/work/A3_econ/), unchanged except: c_mkt = F_rt / v + S_rt with S_rt = the sourced median
spread S (1 tick where none is sourced, as E.28); the grid runs from 0 to max(4, the ceiling of 0.30 sigma_60) ticks at
0.01 (a coarser scan is allowed if every threshold is then confirmed on the 0.01 grid, E.28's grid-check). Outputs per
pair: mu*_mkt and mu10K_mkt (E.28's definitions, market case) in ticks and in sigma_60 units (m* = mu*_mkt / sigma_60,
m10K = mu10K_mkt / sigma_60), and the cost per attempt. E = 0.75 s(m*; 0.20) + 0.25 s(m10K; 0.30). A threshold above the
grid cap scores 0 for its component. Unknown sigma: not reached (Layer 1 gate). E.28's limit case is not used.
Declared variant E_dir60: the same model with T = min(20, floor(L_main / 60)) round trips a day and sigma_T = sigma_60
(a directional 60-minute hold) in place of T = 20 and sigma_T = sigma_1; reported for every pair. E_dir at h = 30,
120 and 240 is computed for the top-15 pairs for F5.

R, product restrictions and news windows (0.15). E.28's scale: 4 = no restriction on the product beyond a firm-wide
rule; 3 = restricted around at most 2 scheduled events a week; 2 = restricted around a recurring weekly event central
to the product (for example EIA inventories for crude or natural gas); 1 = trading hours limited so that at least 25%
of the product's Globex hours are excluded, or restrictions combining the 2 and 3 cases; unknown 1. Applied with the
verified product lists (Topstep's Tier 1 list names specific minis and caps; MFFU's EIA rule covers energy; both
checked against the firm pages). E.28's ruling RR-04 is superseded by the verified list. Rated blind.

A, automation (0.15). E.28's scale with the directional profile: 4 = automated trading through an API explicitly allowed
in evaluation and funded stages, no published order-rate, minimum-hold or scalping rule beyond the platform's
technical limit; 3 = allowed, with a published rate limit, minimum hold or scalping rule that a strategy of at most 20
round trips a day with holds of 5 minutes or more meets; 2 = allowed only through a named third-party platform or by
case-by-case approval, or a published rule makes that strategy borderline; 1 = the terms say neither; 0 = prohibited,
or a rule forbids that strategy (gate). Rated blind.

D, room under the dollar limits (0.15). room_a = DLL_f / (sigma_240 v), with DLL_f the firm's 50K daily loss limit
(where the firm has none, its maximum loss limit); room_b = MLL_f / (R_d v), with MLL_f the maximum loss limit or
trailing drawdown and R_d the median daily range. Each banded: >= 4 gives 4; >= 3: 3; >= 2: 2; >= 1: 1; < 1: 0.
D = the mean of the two. Unknown sigma_240 or R_d: that band scores 1 (E.28 OC-A3-2).

Rel, reliability and eligibility (0.10): E.28's rubric unchanged (4 minus: 1 if operating under 2 years; 1 for
documented payout delays, denials or disputes in the 12 months before the lookup; 1 for two or more material adverse
rule changes in those months; 2 for a regulatory action against the firm itself). Rated blind from the facts.

P, platform and API (0.05): E.28's rubric unchanged (4 minus one for each: no native or documented API; no native
OCO or bracket orders on the API; a VPS near Chicago prohibited or unknown; a documented API rate limit below 10
orders a second, or unknown). Script from the facts.

Layer 2 gates (E.28's, minus the sim-fill item): excluded (listed, not ranked) if the firm does not list the product for
its 50K plan, A = 0, or the firm does not accept British Columbia residents.

## 5. Pair score, ties, variants

- S = 0.50 L1 + 0.50 L2 on 0 to 4, from unrounded criterion scores.
- Order by S, highest first. Two pairs tie if their S are equal at 2 decimals (half-up). Ties are broken by: lower m*;
  then higher L1; then lower cost per attempt; then contract code, then firm name, alphabetically. Nothing else
  reorders the table.
- Reported: the full table for every listed pair (NQ pairs as "excluded (V49)"), the top 15, and the moves against
  E.28's v2 order (rank in E.28, rank here, and the criteria that moved it).
- Declared variants, each flipping one thing against the primary and reported with its top 5 and the MNQ ranks:
  slip0 (slippage 0), slip1 (slippage 1.0 tick), mad (m_h in place of sigma_h in D1 and the gate), D1_all (D1 averaged
  over 5, 15, 30, 60, 120, 240 and OC), E_dir60, OC1_off (no sibling transfer: those codes fail the gate), sat1, D2_own,
  L1min2, spread1 (S = 1 for every code), and one variant for every lead ruling made after this hash that changes the
  top 5.

## 6. Blinding

- Readers report facts and their sources; they do not score.
- FactTable writes masked sheets: product codes, product names that identify a code, firm names and platform names
  replaced by fresh random labels (not E.28's), and the mask key kept by the lead. Facts that reveal an asset class (for
  example "weekly inventory report") stay; E.28 accepted the same.
- BlindScorer (Opus xhigh, fresh context, never shown a source page, the key or E.28's ratings) rates from the masked
  sheets only: D2 a and b, D3 s1 s2 s3, D4 Sat (iii), D6, R, A and the Rel deductions, each with a one-line reason.
- Script (ScoreApplier): D1, D2 c and d, D4 L, J and Sat (i, ii), D5, E, D, P, the gates, L1, L2, S, ties, ranks and
  variants. It refuses to run if this file's sha256 differs from the recorded one.
- RankingReviewer (Fable xhigh, model confirmed from its transcript) recomputes every number from the fact files and
  the script, checks the blinding, the unknown rules, the volatility arithmetic and the F3 window discipline, and
  reviews Step 3b (section 8).

## 7. F5: holding-time scope (script plus lead; facts only, no outcome)

For every Layer 1 survivor (firm-independent rows) and every top-15 pair (firm rows), at h in {1, 2, 5, 15, 30, 60, 120,
240} minutes and OC, with the overnight holds reported in separate rows:
- c_RT = S + 0.5; c_f = c_RT + F_rt,f / v (the firm's round-trip fee in ticks, reported).
- k(h) = c / sigma_h for c_RT and for c_f: the cost-per-sigma curve.
- Gross edge per trade needed: to break even g_be = c_f; to net 1 tick g_1 = c_f + 1. Hit rate needed for a sign
  forecast, p = 0.5 + g / (2 m_h) (empirical m_h), with the normal-approximation p = 0.5 + g / (1.596 sigma_h) beside.
- Trades: n_max(h) = floor(L_main / h), n_cap(h) = min(20, n_max(h)) (the program's entry cap); OC and the overnight
  holds 1 a day; per year x 252.
- Minimum detectable edge at 80% power with the DSR at N = 838 (E.32 protocol P7.2 formulas, recomputed by the script
  from reports/stage_e32_briefs/protocol p7_final.py's definitions, read-only): SR80 = the true daily Sharpe that passes
  with probability 0.80; discovery over 39 months at T = 796 dates (E.33's out-of-fold count; reported both at G3 alone
  and at the binding G3 + G4), test over 43 months at T = 870 (E.32's test count). e80(h) = SR80 sigma_h /
  sqrt(n_cap(h)) ticks a trade, net (independent trades every date, normal moments: a lower bound for fat-tailed
  series). The gross needed for detection is c_f + e80.
- Required gross per sigma at the test: G(h) = c_f / sigma_h + SR80_test / sqrt(n_cap(h)).
- Prop rules per firm by h: DLL_f / (sigma_h v) and MLL_f / (sigma_h v) at one contract; the flat-by-close time against
  the main session's end and the latest start for an h-minute hold; overnight holds (allowed or not, margin, rules);
  news windows (events, products, minutes before and after); scheduled pauses inside or next to the main session (for
  example ZM's 07:45-08:30 CT break).
- Recommended band for a pair: B = {h in {5, 15, 30, 60, 120, 240, OC} : G(h) <= 1.10 min G, DLL_f / (sigma_h v) >= 2,
  and the hold fits before the firm's flat-by-close}. Reported as its shortest and longest member (all members if not
  contiguous) with the reason (where k flattens, where power and the prop rules bind).
- The user's prior ("holds of multiple minutes to hours are best") is judged per pair: it holds if B is non-empty and
  lies within 5 to 240 minutes; partly if B also contains OC; it fails if B is empty or the minimum of G lies at 1-2
  minutes or only at OC or overnight. The scope file says plainly where the facts disagree.
- E.33's cost and trade-count facts may be cited from its return; no new outcome is read.

## 8. Step 3b: build recommendations (rule fixed here, before any combination is built or scored)

8.1 R1 closed lines, listed with sources: the 538 bar-based trials by family (E.23 inventory,
reports/stage_e23_briefs/inventory/ and inventory_compact.txt, and ledger/trial_registrations.jsonl); passive spread
capture (V50); the ZM 5-60 minute directional families of E.33c (V56: crush, cross-asset, order flow, own price path,
pooled); NQ (V49); the intraday closure of V38 with its V45 exceptions.

8.2 R2 combinations. A combination is (product or pool, venue, idea family, holding band). Venues: the five firms and
one own-broker venue (IBKR, non-prop, for the non-prop alternative). Idea families come from the methods briefs (E.28
C2_*.md and C3/C4 drafts, reports/stage_e32_methods_brief.md), the planner research inputs and the readers' D3 and event
facts. Only Layer 1 survivors and their top-15 pairs (plus the own-broker venue for the same products) are combined.
Each dossier states: mechanism and why an edge could exist at retail size; evidence quality; overlap with R1; c_f in
ticks and the hit rate needed at the band's central horizon h_c (the member of B with the lowest G; for the own-broker
venue the F5 formulas with its fee); a Rithmic queue-limit variant only where the route admits it, priced with E.31's
measured trade-through adverse selection as the only measurement; expected trades a year K_year (continuous families:
n_cap(h_c) x 252; event families: events a year x trades per event); power: e80 over the discovery (796 dates) and the
test (870 dates) windows, e80 = SR80 sqrt(T) sigma_hc / sqrt(K) with K = trades in the window; prop fit (DLL against
sigma at h_c, flat-by-close, overnight, news rules, payout reachability at one contract per E.29); data needed (schema,
discovery and test windows, owned, sealed, spent, approximate Databento cost).

8.3 R3 rule. Combination score C = 0.20 Q1 + 0.10 Q2 + 0.10 Q3 + 0.15 Q4 + 0.15 Q5 + 0.15 Q6 + 0.15 Q7, each 0 to 4.
Q1 to Q3 are rated by a CombinationScorer (Opus xhigh, fresh context, not the dossier writer) from the dossiers; Q4 to
Q7 by script.
- Q1 mechanism plausibility: 4 = an identified non-informational or slow-information participant flow at a predictable
  time (hedging demand, index or ETF rebalancing, report digestion with documented drift), with post-2015 evidence that
  the price effect lasts at least the band's shortest member; 3 = identified mechanism, evidence before 2015 or on a
  cousin; 2 = plausible mechanism, no direct evidence at the horizon; 1 = a pattern without a participant story;
  0 = contradicted by full-text evidence or documented as arbitraged away since 2015.
- Q2 evidence quality: 4 = peer-reviewed, out of sample, net of costs, on this product at this horizon; 3 = peer-reviewed
  in sample, or an out-of-sample working paper, on this product, or peer-reviewed out of sample on a close cousin;
  2 = asset-class-wide or other-venue evidence; 1 = practitioner or anecdotal only; 0 = none, or negative evidence.
- Q3 distance from closed lines: 4 = no overlap with R1; 3 = product overlap only; 2 = family overlap only (the family
  was closed on another product, or on this product at non-neighbouring horizons); 1 = same family and product at a
  neighbouring horizon, or a close variant of a closed configuration; 0 = re-tests a closed line (gate: excluded).
- Q4 minimum edge relative to sigma: x = c_f / sigma_hc; <= 0.025: 4; <= 0.05: 3; <= 0.10: 2; <= 0.20: 1; else 0.
- Q5 power: q = SR80_test sqrt(870) / sqrt(K_test), the test's minimum detectable edge in sigma_hc units (K_test = trades
  in a 43-month test; pools use K_eff); <= 0.05: 4; <= 0.10: 3; <= 0.20: 2; <= 0.40: 1; else 0.
- Q6 prop fit: 4 minus: 2 if DLL_f / (sigma_hc v) < 1.5, else 1 if < 3; 1 if the firm's daily payout-qualification
  threshold exceeds sqrt(n/day) sigma_hc v at one contract (payouts rarely reachable, E.29); 1 if the firm's news
  windows stop the family around 2 or more scheduled events a week; floor 0. Gate (excluded): the family's core trades
  are prohibited (a news window covering the event trade for that product, overnight holds needed but prohibited, holds
  past flat-by-close). Own-broker venue: 4 minus 2 if one contract's initial margin exceeds the capital ceiling for an
  own account recorded in docs/DECISIONS.md (if none is recorded: USD 6,000, marked u), minus 1 if sigma_day at one
  contract exceeds 2% of that ceiling.
- Q7 data: 4 minus: 1 if discovery data must be bought at more than USD 50; 1 more if all data needed cost more than
  USD 200; 1 if no clean test window of 36 months or more before 2024-03 exists (sealed, or never read and buyable), 2
  if none of 24 months; floor 0.
- Pools across products sharing a mechanism are allowed: K_eff = K_total / (1 + (m - 1) rho), with rho from E.29
  section 3.2's measured correlations where they exist, else 0.5 within an asset class and 0.3 across classes (E.28's
  effective-sample caveat); a pool's Q6 is its worst member's.
- Ties: C equal at 2 decimals; broken by higher Q1, then lower G(h_c), then product code, venue, family name.
- R4: the build candidates are the top 5 distinct (product or pool, idea family) by their best C, each with its best
  venue and band; those with C < 2.00 are marked weak, and if fewer than 3 reach 2.00 the return says so. Each gets the
  prompt's case, pre-registration outline, data purchase plan with quotes to obtain, kill criteria and an honest prior of
  passing a sealed test (the lead's judgment, with its reasoning and base rates). The best own-broker combination is
  reported as the non-prop alternative. The lead writes a stop rule for the whole directional program.
- R5: the RankingReviewer reviews R1 to R4: arithmetic, closed-line overlaps, realism of the priors, and that no outcome
  was read.

## 9. Fixed lists

9.1 OpenAlex underlying phrases (ORed inside the first search clause): crude oil: "crude oil futures", "WTI futures";
natural gas: "natural gas futures"; gold: "gold futures"; silver: "silver futures"; copper: "copper futures"; euro:
"euro FX futures", "EUR/USD futures", "euro currency futures"; Australian dollar: "Australian dollar futures",
"AUD/USD futures"; bitcoin: "bitcoin futures"; ether: "ether futures", "ethereum futures"; Nasdaq-100: "Nasdaq-100
futures", "Nasdaq 100 futures", "E-mini Nasdaq"; Russell 2000: "Russell 2000 futures", "E-mini Russell"; Dow: "Dow
futures", "E-mini Dow", "DJIA futures"; US Treasuries (all eight rates codes): "Treasury futures", "Treasury note
futures", "Treasury bond futures", "T-note futures", "T-bond futures"; corn: "corn futures"; soybeans: "soybean
futures"; wheat: "wheat futures"; soybean oil: "soybean oil futures"; soybean meal: "soybean meal futures".

9.2 Reference values: DLL_ref USD 1,000; the program's entry cap 20 round trips a day; T_disc 796, T_test 870, N 838;
252 trade dates a year; standard window 2022-11-01 to 2023-10-31.
