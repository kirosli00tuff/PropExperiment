# BlindScorer brief (Stage E.32b, step 3; written by the lead 2026-10-29)

You rate qualitative criteria for a ranking of futures contracts and of firm-contract pairs, from two masked fact
sheets. Contracts, firms, plans and platforms carry random labels. Your ratings feed a script that applies the weights;
you never see the weights, the other criteria, the label key, or anyone's earlier ratings.

## Files: these three only

- This brief: reports/stage_e32b_briefs/brief_blind.md
- reports/stage_e32b_briefs/F4_masked_contracts.json
- reports/stage_e32b_briefs/F4_masked_firms.json

Open no other file: no directory listing, no grep of the repository, no web access, no other brief, no spec, no
earlier stage's file. Read each JSON by section with short scripts that print only what you need (for example one
contract's items at a time); never print a whole file. Each sheet starts with a "format" field: read it first. If you
believe you recognize a real contract or firm behind a label, do not use that belief: rate only from the sheet's facts.

## The strategy being rated

A directional one-lot strategy run by an automated retail system, entering and exiting by market order (or a limit
order priced under the trade-through rule), at most 20 round trips a trading day, holds from 5 minutes to the session
close, latency of tens of milliseconds to one second, no co-location, no rebates.

## Evidence rule (applies to D3 s1, s2 and D6)

A rating at either extreme of a scale (D6: 0, 3 or 4; D3 s1 or s2: 2) may not rest only on evidence known from an
abstract or a search snippet (verified level "abstract" or "snippet [unverified]"). How to report it: if the value you
would give at an extreme rests only on such items, check what the full-text items alone support. If that value is at
least as far out as the capped value (D6: 2 from above, 1 from below; s1, s2: 1), report the full-text value with
"unverified": false and say so in the reason. Otherwise report your value with "unverified": true; the script then
caps it (D6 at most 2 from above and at least 1 from below; s1, s2 at most 1).

## Per contract (every label in F4_masked_contracts.json)

Rate each contract on its own facts. Some contracts have siblings or leaders; the script handles those links, not you.

- D2a (0 or 1): 1 if a published automated-trading or HFT share of volume of at least 50% exists for the contract
  ("applies_to": "this contract") or, failing that, for its product group (the most specific post-2012 figure); 0 if
  that figure is below 50%. If no such figure is given: unknown (value 1).
- D2b (0, 0.5 or 1): 1 if a market-maker, lead market-maker or volume-incentive program for the contract's outright
  futures was in force at any time in 2021-2026 (sourced); 0 if a source documents none; unknown 0.5.
- s1 (0, 1 or 2), structural spread relationships: 2 = a sourced economic spread relationship (for example the soybean
  crush, the crack, a cross-asset pair) with documented intraday cointegration, mean reversion or lead-lag at horizons
  of a minute or more; 1 = a sourced relationship that is mechanical or arbitrage-tight (calendars, mini/full or
  micro/full pairs, implied spread books) or documented only at daily or longer horizons; 0 = none sourced.
- s2 (0, 1 or 2), scheduled information events: 2 = sourced evidence that a scheduled release's price effect on the
  product or its underlying keeps moving the mean (drift or slow adjustment, not volatility alone) for 5 minutes or
  more after the release; 1 = scheduled product-specific or macro releases that move it, absorbed within seconds to a
  few minutes or with absorption speed not documented; 0 = none documented.
- s3 (0 or 1), session structure: 1 = a sourced session structure with a documented handoff effect on the product or
  its underlying (the day-session open after an overnight break or pause, a regional open or close, the settlement
  window); 0 otherwise. Unsourced items score 0 on s1, s2 and s3.
- sat_iii (0 or 1): 1 if a sourced information-share or price-discovery study attributes at least 75% of the
  contract's price discovery to another market; 0 otherwise (also 0 when no study is given).
- D6 (0 to 4), published directional evidence: 4 = a peer-reviewed paper or documented study on this contract or a
  same-underlying sibling showing intraday directional predictability at horizons from 5 minutes to the session, out
  of sample or net of costs, on data after 2010; 3 = such evidence in sample only, or before 2010, or on a close cousin
  (same asset class on CME Globex) after 2010; 2 = evidence only for futures or the asset class broadly (multi-asset
  studies that include the class count here), or for another venue of the same underlying; 1 = nothing found within
  the search budget; 0 = full-text published evidence that such predictability is absent, insignificant after costs,
  or arbitraged away on this contract after 2010. Correctly signed contemporaneous order flow does not count, nor does
  predictability only at horizons under 5 minutes. Use each item's "applies_to", period, sample and cost fields.

## Per pair (every "<firm label>|<contract label>" in F4_masked_firms.json)

Rate the firm's standard 50K plan as the sheet marks it (evaluation and funded stages). Where a rule binds only some
plans or stages, say in the reason how you treated it.

- R (1 to 4), product restrictions and news windows: 4 = no restriction on the product beyond a firm-wide rule;
  3 = restricted around at most 2 scheduled events a week; 2 = restricted around a recurring weekly event central to
  the product (for example a weekly inventory report for an energy contract); 1 = trading hours limited so that at
  least 25% of the product's exchange hours are excluded, or restrictions combining the 2 and 3 cases; unknown 1.
  Apply the restrictions exactly as the pair's facts state them.
- A (0 to 4), automation, for the strategy above: 4 = automated trading through an API explicitly allowed in
  evaluation and funded stages, no published order-rate, minimum-hold or scalping rule beyond the platform's technical
  limit; 3 = allowed, with a published rate limit, minimum hold or scalping rule that a strategy of at most 20 round
  trips a day with holds of 5 minutes or more meets; 2 = allowed only through a named third-party platform or by
  case-by-case approval, or a published rule makes that strategy borderline; 1 = the terms say neither (also unknown);
  0 = prohibited, or a rule forbids that strategy (a gate: say exactly which fact forbids it).

## Per firm (every firm label)

Deductions, each from the firm's facts and dates (the sheet gives each firm's lookup date):
- rel_age (0 or 1): 1 if the firm has operated for under 2 years at the lookup date.
- rel_payout (0 or 1): 1 for documented payout delays, denials or disputes in the 12 months before the lookup.
- rel_rules (0 or 1): 1 for two or more material adverse rule changes in those 12 months.
- rel_regulatory (0 or 2): 2 for a regulatory action against the firm itself.
- Unknown: 0 (no deduction), with unknown true.

## Output

1. reports/stage_e32b_briefs/F4_blind_ratings_masked.json:

       {"rater": "BlindScorer-OpusXHigh", "generated_pdt": "YYYY-MM-DD HH:MM PDT",
        "codes": {"<contract label>": {"D2a": R, "D2b": R, "s1": R, "s2": R, "s3": R, "sat_iii": R, "D6": R}},
        "pairs": {"<firm label>|<contract label>": {"R": R, "A": R}},
        "firms": {"<firm label>": {"rel_age": R, "rel_payout": R, "rel_rules": R, "rel_regulatory": R}}}

   with R = {"value": <number on the scale>, "unknown": true|false, "reason": "<one line; cite the masked item ids in
   brackets>"} plus "unverified": true where the evidence rule above says so. Every contract label, every pair label
   and every firm label in the sheets gets every rating. An unknown rating still carries the value its unknown rule
   gives.
2. reports/stage_e32b_briefs/F4_blind_ratings_masked.md: one table per section (label, ratings, short reasons), and a
   section "Flags for the lead": each rating that sits on a scale boundary, rests on conflicting facts, or is a gate
   (A = 0), with the alternative value and why.

Write the JSON incrementally (contracts first, then pairs, then firms) so a cut run can continue from it. Times in PDT
from `TZ=America/Vancouver date`.
