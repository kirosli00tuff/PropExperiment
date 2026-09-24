# Stage E null criteria

STATUS: DRAFT (Stage E.0, 2026-09-23, lead). Not frozen, not hashed. It generalizes
docs/NULL_CRITERIA.md (the MES criteria, frozen, sha256
6f69e318c96edf0a58956856c881ec3e1b8c68d89e1c836b3d54cfbf0e3497e2) from one product and seven classes
to eight clusters and their products. docs/NULL_CRITERIA.md is not edited and stays the MES record.
Stage E.1 freezes and hashes this file, after the user's review, together with the per-cluster
confirmation lists; after hashing it does not change, and a later stage that needs different
criteria issues a new version under a new name and says why. Design references (D1 to D15) are to
docs/STAGE_E_DESIGN.md.

Written before any bar, tick or order-book data of any Stage E product existed on this machine.

## 1. The null statement, per cluster

The claim the program is entitled to make if a cluster's confirmation comes out null, and nothing
more:

> For intraday strategies on CME {cluster name} futures in cluster {K#}, tested on the
> pre-registered confirmation windows (trade dates S_X to 2024-02-29 for each exposure X, S_X fixed
> by the start rule in section 4; for a member with legs on several exposures, the intersection of
> their windows): the members executed through the engine with market orders at the per-product
> modelled retail cost (Topstep's published round-turn commission plus the calibrated time-of-day
> half-spread table, docs/STAGE_E_DESIGN.md D8, about {c_X} ticks per round turn on exposure X), at
> the risk-matched size q_X of the exposure's vehicle (D2), every position flat by the product's
> XFA flatten time (D9), limit orders, where any, filled only on trade-through: for every member of
> the cluster, a net edge of at least eps_X on its exposure (section 2: the per-exposure translation
> of $85.00 a day, the smallest edge that funds the Topstep XFA funnel under the Stage B model of the
> 2026 rules and fee schedule at MES's 2-micro risk, or the exposure's own funnel-derived figure if
> smaller) is rejected at one-sided 95% (the upper confidence bound on the member's mean net daily
> P&L is below eps_X), with achieved null power of at least 80%. Per-exposure resolution: {the
> table of section 7}; {label "null by inactivity" where section 6 requires it}; members declared
> inconclusive by design before the run and therefore not covered: {list, or "none"}. Members and
> their definitions: {reports/stage_e1_confirmation_list_K#.md, sha256}; criteria: this file,
> {sha256}.

The statement is made per cluster, never for "CME futures", "commodities", "rates", "FX" or any
asset class as a whole. A cluster with any inconclusive member gets no statement, with one
exception: a member labelled "inconclusive by design" in its hashed confirmation list BEFORE the
run, because the power check (section 5) showed its window cannot reach 80% null power, is named in
the statement as not covered and does not block the others (as C6 was handled for MES).

## 2. Epsilon per exposure

- Translated bar (D3): eps_X^tr = floor($85.00 / (q_X x tick value of the vehicle)) net ticks per
  contract per day of the vehicle; in dollars, eps_X^tr x q_X x tick value per day at size q_X.
- Funnel bar (D3, computed in E.2 before any confirmation read): the Stage B power gate re-run for
  exposure X with its own research-window segment moves and costs at q_X, by the rule of
  docs/NULL_CRITERIA.md 2.2 exactly (floor of the minimum robust-pass net dollars per day, over the
  pre-declared cell set, divided by q_X x tick value).
- Operative eps_X = min(eps_X^tr, eps_X^funnel), fixed in the hashed confirmation list; no
  recomputation after hashing.
- What eps_X does and does not mean: as docs/NULL_CRITERIA.md 2.4. It is the smallest edge that
  would pay in the funnel at the program's headline risk; it is not the cost bar; a member can have a
  real edge below it; the claim is scoped to size q_X.

## 3. The tests

- Unit (the R-1 lesson of D.1e): the member's daily net series in ticks per contract of the vehicle:
  each round trip's net P&L divided by its own contract quantity, summed per window date, zeros on
  window dates without a trip. A multi-leg member's series is its combined net dollars per day at its
  frozen leg sizes, divided by (q_X x tick value) of its primary leg, named in its list entry.
- Estimates: theta_hat = the mean; the one-sided 95% upper bound UCB95 and SE_boot from the program's
  stationary block bootstrap (mean block 5, 10,000 resamples, a fresh generator per member seeded
  20260923 plus the member's ordinal in the hashed list, np.quantile at 0.95).
- Null for a cluster: every member (Tier A and Tier B, D5) has UCB95 < eps_X and achieved null power
  Phi(eps_X / SE_boot - 1.645) >= 0.80.
- Edge (D5): Holm over the cluster's Tier A one-sided p-values at family-wise 0.05 / K (K = clusters
  with a non-empty Tier A); then the runner's composite verdict on the confirmation window; then
  DSR > 0.95 at the cumulative program N, daily t > 3.0 one-sided and CSCV PBO < 0.5 on 8 contiguous
  blocks, pinned to the program's functions. A passing member goes to the user as a discussion item
  for a registered final read; no cluster session registers anything.
- ML members (D15): one trial each, tested exactly like any member with its frozen model (sha256 in
  the list); the 48-configuration research-window grid is reported beside it.
- Source overlap (added 2026-09-24 01:52 PDT, on CatalogWriter-K6's question 9): every member records
  its sources' data windows. A member whose supporting source's sample overlaps its confirmation
  window was chosen partly on evidence from that window, so its confirmation is not fully out of
  sample. Such a member is labelled "source-overlap" in the hashed list; it can support a null
  statement as usual, but an edge on it cannot be claimed, or discussed for a final read, unless the
  sealed holdout read (holdout-2, and holdout-1 once bought) confirms it under a registration.
  E.1 records every member's source windows before hashing; a member whose source window is not
  recorded is treated as source-overlap (ruling on review R-04, 2026-09-24).

## 4. Data-quality rules (fixed now, applied later, never revised)

- Start rule per exposure (D4): V_ref,X = the median of the 14 monthly medians (2025-04..2026-05) of
  the vehicle's day-session one-minute volume over bars present; S_X = the first trade date with
  bars of the earliest month M* such that every month from M* through 2024-02 has a median of at
  least 0.25 V_ref,X; 0.15 and 0.40 descriptive; the earliest possible S_X is the first trade date
  with bars on or after 2019-05-06. Where E.2 declares the full-size contract's bars as a micro's
  price path (D2, D4), the rule runs on the full-size contract.
- Rolls: each product's volume-ranked continuous series; roll boundaries from symbology.resolve,
  never inferred from prices; blackout = the splice trade date and the two sessions before it
  (monthly-expiry products lose about three times as many dates as quarterly ones; the power check
  counts them).
- Vendor-degraded dates from metadata.get_dataset_condition, fetched once and frozen at fetch;
  trials trade through them, event statistics exclude them, as for MES.
- Calendars per product group from CME's published schedules (D10), each entry cited, validated
  against bars on non-holdout dates before any run; flatten per group (D9).
- Cost model per product (D8), calibrated once on the declared sample. It understates costs on the
  older, thinner history: conservative for a null, not for an edge; any member that passes gets a
  period-appropriate cost re-check before it is discussed.
- Year slices are descriptive only; no year, product or regime is dropped, weighted or excluded
  before or after results are seen.

## 5. Power and sample size

Computed in E.2 per member from its research-window daily series by the D.1e method (analytic n_b and
n_a, the block-bootstrap simulation where they differ by more than 15%, the larger figure chosen),
against the days each exposure's confirmation window supplies after exclusions. A member whose n_b
exceeds its supply is labelled "inconclusive by design" in the hashed list before the run. Achieved
null power is then MEASURED at confirmation from each member's own series (section 3); the plan
figures are not the criterion.

## 6. The inconclusive rule and the out-of-scope list

- Inconclusive: any member that neither passes confirmation nor meets both null conditions; one such
  member keeps its cluster out of the null statement (except section 1's pre-declared label). A member
  with zero trips or events, or a zero bootstrap standard error, is inconclusive, not null. A member
  meeting the null with fewer than 30 closed round trips or events on its window is marked "null by
  inactivity", and the cluster statement carries that label in the same sentence. Nothing is rounded
  to null; no member is dropped, moved or re-parametrized after the run.
- Out of scope (no statement speaks for these): holding past the XFA flatten (venue rule); products
  not permitted by Topstep or dropped by D1; the S&P 500 exposure (closed with MES, docs/NULL_CRITERIA.md);
  sizes other than each exposure's q_X; passive execution at better-than-trade-through fills (C6,
  closed by decision, docs/DECISIONS.md); signals needing order-book data; constructions not on the
  frozen lists; the 100K and 150K accounts and the Daily Loss Limit option; other prop firms; social
  media and sentiment signals.

## 7. What the program may say, and what it may not

If a cluster comes out null, the program may say section 1's statement for that cluster, cite this
file's hash and the cluster list's hash, and must carry in the same sentence, per exposure: eps_X in
ticks per contract per day and in dollars at q_X; the vehicle and q_X; the member with the fewest
trades or events and its count; the largest per-trade upper bound found; the "null by inactivity"
label where required; and the members not covered by design.

It may not say "CME futures have no intraday edge", "{asset class} is efficient", "{product} has no
edge", or anything about sizes, products, fill types, horizons, accounts or constructions outside
the lists. If every cluster that had a list comes out null, the program may say exactly: "On the
pre-registered confirmation windows (per exposure, S_X to 2024-02-29), no member of any cluster the
program tested on CME futures (market orders at the per-product modelled cost, risk-matched sizes,
flat by the XFA cutoff) showed a net edge of at least its exposure's eps_X, the smallest edge that
funds the Topstep XFA funnel at MES's 2-micro risk; every member's one-sided 95% upper bound was
below eps_X at >= 80% achieved null power; per cluster and exposure, the resolution was [table]",
and must add that the MES record is separate (docs/NULL_CRITERIA.md), which members were not
covered by design, and that the structural question below eps remains open wherever the power
table says the data cannot resolve it.

## 8. Cross-cluster members (K8)

A member whose legs sit in different clusters is stated under K8 only, never under its legs'
clusters. Its window is the intersection of its legs' windows, its eps is that of its traded
(primary) leg's exposure, and it enters K8's Holm family, not a leg cluster's.
