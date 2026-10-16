# E22-F1: forward-test pre-registration of the micro trend book at $25,000

STATUS: FROZEN 2026-10-16T02:11:20-07:00 by the Stage E.22 lead (Opus 5.5, xhigh), before registration, against
docs/prompts/STAGE_E.22.md B4. Draft 1 (2026-10-16 ~01:05 PDT) is preserved verbatim at
reports/stage_e22_briefs/prereg_F1_draft_0105.md (sha256 904c194d46d8d201e05a984bea43500a686078f63496a6fcf4927482c50bfc6d);
revised ~01:32 (sections 4, 6) and ~01:52-01:56 PDT after RegReviewer-FableXHigh (reports/stage_e22_reg_review.md:
B1, B2, S1-S8, N1, N3, N8; recheck section 4: 19/20 resolved, N2 by agreement, NEW-1 and NEW-2 fixed). After this
freeze nothing in this file changes; the registration records its sha256.

## 1. What is registered

One forward test, ID **E22-F1**, of one hypothesis: the micro trend book defined in sections 2-6,
run as a paper book on daily settlement prices that arrive after the start date (section 7), earns a
positive net daily P&L. Registering it adds one trial to the program: **N 532 -> 533**
(ledger/trial_registrations.jsonl; `uv run python -m screening.trial_registry register --test E22F1
--ids E22-F1 --freeze reports/stage_e22_prereg_F1.md --freeze-sha256 <sha256 of this file>
--harness-sha256 <harness in force>`). No historical figure enters the verdict. The Part B study
(reports/stage_e22_microbook.md) re-uses data E.21 already read (2010-07..2024-02) and is not
evidence of edge; it sets the constants of section 2 and describes the book's behaviour.

## 2. The rule (frozen code and constants)

- Code: forward/__init__.py, forward/core.py (volatility, EWMAC, forecast combination, sizing,
  rounding; also the greedy optimiser, which E22-F1 does not use), forward/strategy.py
  (target_positions), forward/history.py, forward/runner.py, forward/ledger.py, forward/sources.py,
  forward/rolls.py, forward/evaluate.py, forward/report.py.
- Constants and tables: forward/config_f1.json (every constant with its source; rounding_method
  "simple"), forward/tables_f1.json (the runner's per-instrument multipliers and per-side costs; it
  must equal config_f1.json's instruments.* multiplier and cost_per_side_usd, pinned by
  tests/test_forward_tables_pin.py), forward/rolls_f1.json (roll rules; see section 7 for its
  pre-clock check).
- The file list with sha256 is section 11. Any change to a listed file after the freeze (except the
  pre-clock roll correction of section 7) is a new registration with a new ID (and N + 1); E22-F1
  then ends "abandoned, no verdict".
- In words (the code governs where they differ): EWMAC 8/32, 16/64, 32/128, 64/256 on each
  instrument's back-adjusted daily settlement series, each scaled by Carver's published forecast
  scalar and capped at +-20; equal-weight combination x the frozen FDM (1.1314), capped at +-20;
  positions for a 20% annual volatility target on $25,000 of notional capital (fixed, no
  compounding), equal instrument weights over the live instruments, x the IDM computed from the
  frozen correlation matrix (config_f1.json idm) over the live instruments (2.3518 when all 12 are
  live); Carver's published formulas and constants as cited in config_f1.json and
  reports/stage_e22_briefs/carver_sources.md.

## 3. Universe

The 12 micros of reports/stage_e22_briefs/lead_spec_B.md S1: MNQ, M2K, MGC, MCL, MNG, M6E, 2YY, 10Y,
30Y, MZC, MZS, MZL, each on its own settlement price in the forward test (the micro's own contract;
the full-size paths were used only in the historical study). The yield micros (2YY, 10Y, 30Y) trade
their own yield-quoted contracts; their forecasts run on their own settlement series (yields in
percent), not on a proxy. Not in the book: SIL, MHG, M6A, M6B, MCD, MJY, MZW, MZM, MES.

## 4. Rounding method

**Simple rounding: Carver's rounded-and-buffered baseline** (the unrounded position of section 2
rounded to whole contracts, with his position buffer of 10% of the average absolute position:
trade only when the rounded target leaves the buffer, and then to the buffer's edge), as
implemented in forward/core.py (buffered_round) and selected in forward/config_f1.json.

History of this choice (kept visible on purpose). Draft 1 (01:05 PDT, before the study ran; preserved,
see the status line) chose Carver's greedy minimum-tracking-error dynamic optimisation (November 2021
version). The historical design study then showed, at $25,000, net Sharpe 0.47 unrounded, 0.41 simple
(daily correlation with unrounded 0.95) and 0.29 greedy (with the 0.5 correlation shrink of ruling R-B6;
0.20 without it; correlation 0.75), the greedy holding most live instruments at zero on most days
(reports/stage_e22_microbook.md sections 4, 7, 11). The lead changed the method to simple rounding
(ruling R-B7, ~01:32 PDT), before the freeze and before any forward data exist. The change uses only
historical data that the forward test never reads, so the forward evidence stays independent. Rulings
R-B6 and R-B7 are recorded in lead_spec_B.md S8 (labelled there B-R6 and B-R7: the same rulings) and will
be listed as open choices in
reports/E.22_RETURN.md.

## 5. Fills and costs

- Orders computed from data through settlement(t) fill at settlement(t+1) (the next settlement),
  paper only. Integer contracts.
- Costs per contract per side: forward/tables_f1.json (base case; MNQ, M2K, MGC, MCL from the frozen
  D8 tables; the other eight a declared D8 extension, commission plus one tick, flagged UNSOURCED where
  so marked); the verdict uses the base case only. Rolls: two fills per contract held.
- No live order is placed by this test. Live trading by the user is outside E22-F1 and does not
  change it.

## 6. Data handling

- Source: the daily settlement source the user approves. Its name, terms, the approval date, the start
  date and the warm-up file's sha256 are recorded in docs/DECISIONS.md and in the E.22 STATE file
  (reports/stage_e22_STATE.md) before the first ledger record is written.
- A day on which the source delivers no settlement for an instrument: no fill for it (a pending order
  expires unfilled, never filled later at another price) and no new order for it; its position is
  carried, and its P&L accrues from its last mark when its data returns; the day is flagged.
- Every weekday in the horizon has a ledger record or is declared exchange-closed in the next record
  (stored there); a declaration must match the exchange's published holiday calendar. A weekday that is
  not declared closed and has no settlement for any instrument is a missing day: P&L 0, flagged, and it
  COUNTS as a 0 in the evaluation series (this can only lower the Sharpe). Declared exchange-closed days
  are not in the series (forward/README.md open choices 2, 6, 7).
- A day's settlements may be taken from a second approved source only before that day's record is
  written; the switch is logged in docs/DECISIONS.md. A recorded day is never changed.
- The ledger (forward/ledger.py; append-only JSONL with a sha256 chain; every record carries the
  fingerprint of the frozen configuration and the warm-up history) is the only record of the series. A
  broken chain, a rewrite or an out-of-order date ends the test "abandoned, no verdict".

## 7. Start date, warm-up, rolls and horizon

- Start: the date of the first ledger record, which is the first trade date, after the user approves a
  daily data source, on which the approved source delivers settlements (none is approved at
  registration; the clock does not run until data flows).
- Warm-up: the approved source's own back history of daily settlements of each of the 12 micros (no
  splice with the owned stores), at least 260 trade dates before the start where the source has them,
  in the runner's history format (forward/history.py), passed to the runner and fingerprinted into
  every ledger record. An instrument with fewer than 257 prior settlements is flat until it has 256
  daily differences (config warmup_diffs). Expected live on the start date: all 12, if the source
  delivers that history; the count is recorded with the start date (section 6).
- Rolls: forward/rolls_f1.json may be corrected against the exchange's published roll schedule
  BEFORE the first ledger record; the correction and the new sha256 are logged in docs/DECISIONS.md and
  the STATE file, and this is not a new registration. From the first ledger record on, the file is
  frozen (it is in every record's fingerprint). E22-F1 ends "abandoned, no verdict" when a non-zero
  position's reference contract is past its roll anchor date (forward.rolls.expiry_guard) and the roll
  has not executed, whichever flag the runner sets (`missing:I` on or after the anchor, or
  `roll_overdue:I`); the condition is checked from each record's positions[I].contract, positions[I].qty
  and its date against rolls_f1.json.
- Horizon: 36 calendar months from the start date. The evaluation series is the net_pnl of every
  ledger record dated in [start, start + 36 months), including the zero days before the first fill and
  the missing days. forward.evaluate and forward.report are run WITHOUT --clock-start; a run with
  --clock-start is not the registered evaluation.

## 8. The bar (the only verdict)

Computed once, at the end of the horizon, by forward/evaluate.py on the series of section 7, in USD:
- one-sided Newey-West t of the mean daily net P&L (Bartlett kernel, lag 10), p from the standard
  normal: **p <= 0.05**; and
- annualised net Sharpe = mean / sd x sqrt(252): **>= 0.3**.
PASS iff both hold; otherwise FAIL. No other test, horizon, sub-period or cost case decides it.
Power (stated before the start): with a true annualised Sharpe S the expected t over 3 years is about
S x sqrt(3), and the power is 1 - Phi(1.645 - S x sqrt(3)): S = 0.3 -> 0.13, S = 0.5 -> 0.22,
S = 1.0 -> 0.53. Under iid daily P&L, p <= 0.05 at 36 months already implies a realised Sharpe of
about 0.95, so the Sharpe >= 0.3 leg rarely binds; in practice the bar is the p-value. A FAIL at 36
months is weak evidence against a modest edge; a PASS is evidence for one at the registered level.

## 9. Interim looks and stopping

Every 6 months from the start date, forward/report.py produces a descriptive look (mean, sd, Sharpe,
drawdown, turnover, costs, flagged days). No p-value is computed at a look, nothing is changed because
of a look, and there is no early stop for success or failure. The test may end early only
"abandoned, no verdict" (sections 2, 6, 7, or the user stops it). An abandoned E22-F1 stays in N, is
reported in the program record with its descriptive figures at the stop date and the reason, and is
never restarted under the same ID; a restart of the same rule is a new ID and N + 1.

## 10. Program accounting

E22-F1 is one trial: N 532 -> 533 at registration. It is not part of any Holm family. Its result,
when it exists, is reported with the program N at that time.

## 11. Freeze record

- Frozen 2026-10-16T02:11:20-07:00. Harness at registration: v13 dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4
  (commit e40ca85). The registration entry id and time are recorded in reports/stage_e22_STATE.md and the return.
- The frozen file set (section 2 and the supporting files) is listed below in `sha256sum -c` form; the same list is
  reports/stage_e22_f1_files.sha256 (sha256 bb3bf3b3c6df28ac203905b53317b1835d447d6b2bba2ec88be929dd2a0fb8af).
  Check with `sha256sum -c reports/stage_e22_f1_files.sha256`. forward/rolls_f1.json may change only by the
  pre-clock roll correction of section 7 (logged in docs/DECISIONS.md with its new sha256).

```
3a226dead048f1f9b9c0058ac463c18fa112ca537b7f7fbc49cd6a4843756d6b  forward/README.md
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  forward/__init__.py
b6903541f70d157f4a67e0303981afb0d70710655d37317e043ee8d69e653c43  forward/config_f1.json
e5e9cdb0d9e9b63fec05f5f691577b77b57cb29b56b65bc865710fbb3359a916  forward/core.py
5632c385e63d3969284e1a1573ad1c319d76bf8aacbf7a087b152d630f269ba2  forward/evaluate.py
afef3948721e66388cb370b1c9c43361d9043c41eb332c95f15871b9219a7c11  forward/history.py
4c71e2c0d619c942a4dce1d7443240e38277179508a82d9eab49841dfb737450  forward/ledger.py
fdf2655dc1aaa51998d991c27e56744ba3800f1adcd21e0e49e258e17ba5d6c5  forward/report.py
ba7205fb434e5287f9469d70bc7ed81d5ae8283ee9d07ea9cbdbe9f1d5332f52  forward/rolls.py
17b56c48efbb59ace9ab8438ed031614dadc9335e1df1d533be2ceba54a5c5a6  forward/rolls_f1.json
a994c38e0cf420db274b2f2c40c7c84de74530ca4c71aed71d36a781a3ab75c3  forward/runner.py
d1484cef9bb19620d486acd8738104afbdff1d36a96731e43e7828a182123a0d  forward/sources.py
a6247af0cf8f3482a506f196c5969aea2f554735bab6e687ca044e424f191604  forward/strategy.py
78e9d54274595579f8e269828434de2996a45b6271cc89f3e5174e15dff36ff4  forward/tables_f1.json
79bfb71e0b0e8372a05bd820c1624a772f48c8304039134c77cea08c28bc8c1a  tests/test_forward_core_rounding.py
4fc0c779952420f83d5ffa171798b6d5d7879c3067918cd565c3b7c2c18e75e7  tests/test_forward_core_signals.py
528c9d1c9c896ab73ebcb3d6d6acaeaeb99f9a934901d79b11732bc40615dd12  tests/test_forward_core_strategy.py
78d0df033ca528d56f919cf9d977ca1e53eb7bc38c5511d21c7c634ff7d84894  tests/test_forward_runner_evaluate.py
36c93b6931e595ce6b4d4ad82862619a8f80d974cecfcdc7b2ca45af47e09775  tests/test_forward_runner_ledger.py
fc722472e71afee208b826e6a74e97d1e644f6fc13c3e162e81de1d0f95e3d32  tests/test_forward_runner_report.py
1ea11c8ff9dd902061c71ae05466f5e47480940acd6c49f777a83f36d73422d8  tests/test_forward_runner_rolls.py
0d7c732dabababa84420d19407e565840307399417c279315ee411d8fe804ceb  tests/test_forward_runner_sources.py
c8cc2dbaec9f0d64e512a7f7c652b3647484e92cf2066a19fe4ad397c6fddada  tests/test_forward_runner_step.py
2a2d4b0f7c4a9558625976ba048c5e0aa7c5616182dfbe1023648ab59677ff31  tests/test_forward_tables_pin.py
7d6ca68e28131d09c4091b7a583db3b5b5dc57bfd6d0cfe3d938f2bfc419cdae  reports/stage_e22_briefs/lead_spec_B.md
b93149fa8a9e2e5e240db5f159bd8e19da167f57056f14caaa23726d5e36a69d  reports/stage_e22_briefs/carver_sources.md
904c194d46d8d201e05a984bea43500a686078f63496a6fcf4927482c50bfc6d  reports/stage_e22_briefs/prereg_F1_draft_0105.md
786b2ffa7d588985f1cdd6bd79f65d2d9e28e74e305430dbb97173dd64206198  reports/stage_e22_microbook.json
fa081c0564ad95e2cf6bdda62335911f37b5165e1db4941314305b31cb473ab3  reports/stage_e22_microbook.md
ecd9aa18990306f0f092308feab66b8badf425549d9ccd63fb26ed5f0c44b7f4  reports/stage_e22_reg_review.md
```
