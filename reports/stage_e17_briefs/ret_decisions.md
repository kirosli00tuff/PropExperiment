1. **C1: rerun under a corrected freeze, or close it.**
   - Recommended: a new pre-registration "C1b". It is identical to C1 except that C10 names the legs that are n/a by
     design (MBT; CL is already 0 in E.12) as exempt. Before registering, a frozen dry check should run c10_check on
     the frozen reference against the sentinel frames (Fable F-1).
   - Costs: N + 2 (478 -> 480) and no purchase. The six 2010-2019 stores are bought and the model, q and calendars are
     frozen, so it is one short session.
   - Why: C1 never produced an answer. With the data owned, the only cost is N.
   - The alternative is to close the NG near-miss as unresolved: the freeze contradicted itself and nothing was learned.
2. **The base-rule batch: close it.**
   - All five registered tests fail on the base case: Holm rejects none, DSR is about 0 at N = 478, and the stress
     and 1.5 x slippage cases are worse. Per the common file (section 10), there is no holdout-2 read and no
     meta-labeling design (V28) for any of H1-H5. Holdout-2 stays sealed.
   - H2's positive mean (+0.344, p 0.068, 5 of 6 years positive) is not a pass. Any H2 variant would be a new
     pre-registration counted from N = 478.
   - H1's gross momentum is positive but about a quarter of D8 costs, so it is not a cost-feasible rule at these
     horizons.
   - Recommended: no rerun or variant of H1-H5 on these windows.
3. **What the next search should cost-check first.** H1 and H4 show that 30-minute and next-day horizons at D8 costs
   leave little room: costs are about 4x H1's gross. Recommended: any new hypothesis states its expected gross per
   trade against the D8 cost of its vehicle before pre-registration (a cost-feasibility gate), so a decade of data is
   not bought to learn the cost arithmetic.
4. **Funds.** acct-2 has about $3.14 left against the user's $125 figure; the ledger total for E.17 is $121.855498.
   No further purchase is possible without a top-up. The 10 fallback roots (YM, HG, 6S, 6J, 6A, 6B, 6N, ZM, ZW, 6C)
   would need $92.62 (x 1.03) for their 2010-2019 extension. Recommended: do not buy them for the base-rule batch;
   its verdict is final.
5. **The quote tool's ledger fallback (E.15)** is still unfixed for plans es2011 and ext2010. ext2010h sidesteps it
   with its own session id. Recommended: fix it in the next harness change (use only the current run's lines).
6. **The untracked ..env.swp** at the repo root is an editor swap file of .env and may hold the Databento keys. It was
   not read or committed. Recommended: delete it, or add `*.swp` to .gitignore, before any commit with `git add -A`.
