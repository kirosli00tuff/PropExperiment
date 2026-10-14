## 5. Verification (each Fable finding, the ruling and the fix)

### 5.1 FreezeReviewer-FableXHigh (reports/stage_e21_review_freeze.md)

The review ran before registration, 03:51-04:02 PDT, and returned APPROVE WITH FIXES (0 BLOCKING,
2 SHOULD FIX, 6 NOTE). The recheck, 04:07-04:10, returned APPROVE with one further NOTE (FR-9). The
rulings are in lead_spec section B.

| Id | Severity | Finding | Ruling and fix |
|---|---|---|---|
| FR-1 | SHOULD FIX | The forced close at an era's last mark was untested. It was the only path keeping the "book ends with a position" invariant from raising after the marker. | Fixed. Tests were added at both era ends (2019-04, 2024-02). The end-of-book check became a non-fatal, counted backstop forced close. The run counted 0 backstops. |
| FR-2 | SHOULD FIX | The "missing roll bar" and "missing roll bar (fill guard)" hold exclusions were untested. | Fixed: two synthetic tests. The run counted 1 "missing roll bar (fill guard)" in T1. |
| FR-3 | NOTE | Bar existence at later dates steers rebalance dates and T3 eligibility. This is a data-presence effect, not a price effect. | Declared in the prereg. Reported separately from calendar reasons. |
| FR-4 | NOTE | T4's trailing-sd scaling runs over mostly-zero H2 and early-T2 values, which inflates x/sigma on those dates. | No change, because the prompt prescribes H5's method. After the run, this effect dominates T4's series (section 7, item 3; open choice 28). |
| FR-5 | NOTE | Capital units versus risk units, and "scaled to the hold", do not change the verdict. | Declared in the prereg. |
| FR-6 | NOTE | Sigma skips returns across a missing previous mark. | Counted in the exclusions: 1,343 across the 17 roots. |
| FR-7 | NOTE | multiday/README.md and screening/trial_registry.py were not pinned. | Both added to the freeze. |
| FR-8 | NOTE | The pre-marker order and the O_EXCL marker were confirmed. | None. |
| FR-9 | NOTE (recheck) | A backstop close on a mark dated 2019-05-01..05-05, whose era is None, would raise KeyError after the marker. | Hardened before the freeze: the marks on each side of an era change are precomputed. Test added. |

### 5.2 VerdictVerifier-FableXHigh (reports/stage_e21_review_verdict.md)

The verifier worked 04:15-04:35 PDT and returned VERIFIED WITH NOTES (0 BLOCKING, 0 SHOULD FIX,
5 NOTE).
- **Its own code first:** it built its own series from the real stores with its own code, before
  opening the run's statistics.
- **Statistics:** all 152 verdict numbers matched within 1e-9 (n, mean, sd, t, t_NW, p_t, p_NW, p,
  Sharpe, bootstrap CI, Holm, Sharpe bar and PASS, for every cost case).
- **Series and units:** all 12 daily series (4 tests x 3 cost cases) matched date by date with zero
  difference. All 17 roots matched in T1 and T2 on net, fills, gross and costs, and T3's 227 units
  matched.
- **Order of events:** confirmed, as were N = 532, the freeze and the H2 pin.

| Id | Severity | Finding | Ruling |
|---|---|---|---|
| VV-1 | NOTE | The 171 "no signal (lookback: missing bar)" root-months, concentrated in ZC, ZL, ZS, LE and HE, come from the stores' roll metadata. It records two roll instants on consecutive weekend days (Saturday, then Sunday's session open) with no bar between them. At the second instant, base_rules.h2.chained_return finds i_out < start_i and returns "missing bar". The verifier reproduces all 171, the 17 undefined returns and the 13 hold exclusions. Positions are identical; there is no look-ahead. | Accepted as classification (a): the frozen rule applied as specified to a real store feature. It thins those five roots for about 1-5 years each and does not bias the verdicts. Any future test chaining across these stores should treat consecutive recorded rolls with no bar between them as one splice, defined before data. |
| VV-2 | NOTE | The wording of multiday/README.md coder choice 5 can be misread as cascading backwards. The code zeroes only the order in force at the failed interval, which is the verified reading. The verifier's first pass misread it, and both passes are kept. | No change to the frozen README; noted here. |
| VV-3 | NOTE | Fills by kind: the run labels every non-roll fill "rebalance". The verifier's entry/flip/exit split sums to the same 2,121. | Reporting only. |
| VV-4 | NOTE | The two T3 "window end" units (February 2024) are counted by the run and skipped silently by the verifier. Traded units agree. | Reporting only. |
| VV-5 | NOTE | The two counts label pre-window months differently. No position is affected. | Reporting only. |

Not checked by the verifier: the F8 economics, the DSR block, the limit-lock and high == low
diagnostics, and the stress and 1.5 x per-root rows. F8 is descriptive. EconWorker-OpusHigh
reconstructed each test's base series from the per-root files (maximum absolute error 2e-17), which
cross-checks the per-root files the economics uses.
