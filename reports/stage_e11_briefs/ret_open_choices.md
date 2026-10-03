Every decision the lead made without the user, with the reason. Design choices the user can
override are also in V2.12; this list adds the process choices.

**Design (Task 1 and the rulings).**
1. **The cost gate is read literally** (net edge > k c, so gross > (1+k)c). That is F7's wording. A
   one-line switch to the gross reading is built, and the lead recommends the gross reading
   (review D-05).
2. **The Gate 0 canary "an edge smaller than the cost passes Gate 0, then the cost gate rejects it"**
   cannot hold literally under the proposed 1.5c Gate 0 bar. It is implemented as a binary edge in
   [1.5c, 2.5c), which passes Gate 0 and is rejected by the gate, plus an edge below c, which
   fails both. The pre-cost alternative, under which the sentence holds literally, is open
   (V2.12 item 1).
3. **The model is fit on the gross normalized target**, with the cost gate after it. "The net model"
   is the pipeline of model, gate, sizing and net P&L, selected on net P&L. The reason: the cost is
   known exactly at decision time, and Gate 0 shares the fit.
4. **Ridge without elastic net** (154 columns against about 10^5 rows). The grid is 3 ridge values
   plus 2 LightGBM depths, times 3 values of k and 3 horizons: 45 configurations, at MinBTL's bound
   of about 45.
5. **Decision clock by rule** (t1 = O + 30; t3 the latest with t3 + 120 <= F; t2 the midpoint), and
   h in {60, 120, F}.
6. **tau = 0.10**, derived from IC 0.10 x z 2.5 against the loosest literal hurdle of 2.5c.
7. **The Gate 0 statistics.** Family A is the date-clustered IC t per signal and horizon
   (two-sided). Family B is the top 20% of |r_hat| from ridge at lambda 0.1 under CPCV, per pair.
   Holm runs at 0.05 over A and B together, with a 30-trade floor.
8. **The research window is a screen** (t >= 1.0), because 1.19 years cannot confirm a Sharpe near
   1.5 (F5). Confirmation rests on the nested OOS t >= 3, the DSR and the holdout-2 read (review
   D-02, option (a)).
9. **The selection metric** is the fixed-D (the 50K MLL) daily Sharpe with zeros on no-trade dates.
   It is the mean over folds, and eligibility needs at least 30 trades and a finite score on every
   fold.
10. **The simulator subclasses StageERules** with three stated differences: no one-position rule,
    the lot cap per product, the blackout per product. It adds a cost-only override and a
    combined-MLL audit. The 150K figures come from the payout simulator's re-sizing, a lower bound,
    because the frozen account model encodes 50K only; the 150K tiers are taken as the 50K tiers.
11. **Phase-1 scope is the training window only**, with holdout-2 deferred to phase 2. This departs
    from V1 so that more products fit the budget; it is open.
12. **The sizing rounding band**: one contract up to 2b, D2's band, so that full-size vehicles stay
    tradeable at 50K. The daily risk budget caps it at sigma_target.
13. **Payout policy**: on the first eligible date, request the largest amount that leaves
    D >= 0.5 x MLL. The plain maximum halted accounts after small early payouts. Ruin is read with
    the kill switches off.
14. **The ports are pooled** across products, one feature per port variable, because D6 defines
    each port as one rule ported to every product. G9's 120-date median is kept, along with its
    140-date training warm-up.
15. **The roll-blackout rule**: the product's own roll dates exclude its rows. A signal leg's roll
    date makes only the features reading that leg not applicable. D4's union over 8 leads would
    have dropped a large share of all dates.
16. **The research-window warm-up skips the sealed gap** (training dates, then research dates).
    Proposed and open; research-only warm-up would lose 80 to 140 of 299 dates.
17. **The engine and payout figures come from the nested OOS schedule** (5 paths), not the in-sample
    final refit. Each engine path runs in its own process for memory.

**Process.**
18. **Harness v7 was committed first** (01:37), before any ml_route_v2 test file existed. New tests
    are named test_ml_v2_* so they fall outside the manifest's patterns, and ml_route_v2/ is
    outside the harness directories. So v7 differs from v6 only by data/config.py and its test.
19. **The key-fix test is named test_stage_e_config_keys.py**, so the manifest freezes it together
    with data/config.py.
20. **The suites ran as `uv run pytest -q -p no:cacheprovider`** (nice 10), which keeps .pytest_cache
    out of the tree. That is one flag beyond the prompt's `uv run pytest -q`.
21. **The design reviewer's Part 1 was complete on disk** when the usage limit cut the agent off. It
    was used as written, with no rerun. Only its return message was lost.
22. **FixCoder was resumed after the limit** through SendMessage, with its partial work on disk.
23. **The lead deleted 1.9 GB of synthetic probe frames** (~/.cache/propexp_e11_probe/A_fix3) that
    this session had created. The A and B probe states can no longer resume after the fingerprint
    changes, and are deleted at the end.
24. **C-10 is deferred** (docs/ACCESS.md:9 names the old variable; data/config.py does not strip the
    key). The prompt allows exactly two commits, and data/config.py is frozen in v7. The next
    purchasing session fixes both when it writes its own manifest.
25. **The lead fixed one of its own arithmetic errors before the review**: the research-window power
    at t >= 1.0 is 0.74 and 0.88, not 0.70 and 0.83.
26. **The lead corrected guessed times in the STATE file** at 01:23, using file timestamps.
27. **Mid-stage, a full suite ran with the two in-flux canary files excluded** (6130 passed, 02:40).
    It was an early check, not a gate.
