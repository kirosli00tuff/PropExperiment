# E22-F1: forward-test pre-registration of the micro trend book at $25,000

STATUS: DRAFT (not frozen). Drafted by the Stage E.22 lead (Opus 5.5, xhigh) 2026-10-16 ~01:05 PDT,
against docs/prompts/STAGE_E.22.md B4, BEFORE any Part B study figure existed (the rounding method in
section 4 was fixed in this draft before the study ran). Reviewed by RegReviewer-FableXHigh before it is
frozen; the frozen version replaces this status line with the freeze record (section 11).

## 1. What is registered

One forward test, ID **E22-F1**, of one hypothesis: the micro trend book defined in sections 2-6,
run as a paper book on daily settlement prices that arrive after the start date (section 7), earns a
positive net daily P&L. Registering it adds one trial to the program: **N 532 -> 533**
(ledger/trial_registrations.jsonl, `screening.trial_registry register --test E22F1 --ids E22-F1`).
No historical figure enters the verdict. The Part B study (reports/stage_e22_microbook.md) re-uses data
E.21 already read (2010-07..2024-02) and is not evidence of edge; it only sets the constants of
section 3 and describes the book's behaviour.

## 2. The rule (frozen code and constants)

- Code: forward/core.py (volatility, EWMAC, forecast combination, sizing, rounding, the greedy
  optimiser), forward/strategy.py (target_positions), forward/runner.py, forward/ledger.py,
  forward/sources.py, forward/rolls.py, forward/evaluate.py, forward/report.py.
- Constants: forward/config_f1.json (every constant with its source), forward/rolls_f1.json (roll
  rules), and the per-side cost table of section 5.
- The file list with sha256 is section 11. Any change to any listed file after the freeze is a new
  registration with a new ID (and N + 1); E22-F1 then ends "abandoned, no verdict".
- In words (the code governs where they differ): EWMAC 8/32, 16/64, 32/128, 64/256 on each
  instrument's back-adjusted daily settlement series, each scaled by Carver's published forecast
  scalar and capped at +-20; equal-weight combination x the frozen FDM, capped at +-20; positions for
  a 20% annual volatility target on $25,000 of notional capital (fixed, no compounding), equal
  instrument weights over the live instruments, x the frozen IDM; Carver's published formulas and
  constants as cited in config_f1.json and reports/stage_e22_briefs/carver_sources.md.

## 3. Universe

The 12 micros of reports/stage_e22_briefs/lead_spec_B.md S1: MNQ, M2K, MGC, MCL, MNG, M6E, 2YY, 10Y,
30Y, MZC, MZS, MZL, each on its own settlement price in the forward test (the micro's own contract;
the full-size paths were used only in the historical study). The yield micros (2YY, 10Y, 30Y) trade
their own yield-quoted contracts; their forecasts run on their own settlement series (yields), not on
a proxy. Not in the book: SIL, MHG, M6A, M6B, MCD, MJY, MZW, MZM, MES. An instrument with no
settlement on a day is handled by section 6.

## 4. Rounding method

**Carver's greedy minimum-tracking-error dynamic optimisation, November 2021 version**, as
implemented in forward/core.py from reports/stage_e22_briefs/carver_sources.md (shadow cost,
tracking-error buffer and covariance estimate as configured in config_f1.json). Chosen in this
draft before the study ran, because it is the method Carver publishes for accounts too small for
simple rounding (his own 45-instrument test at $50K: "the optimised version is still better than the
rounded (SR improvement around 0.1)", E.13 T-20).

## 5. Fills and costs

- Orders computed from data through settlement(t) fill at settlement(t+1) (the next settlement),
  paper only. Integer contracts.
- Costs per contract per side: the D8-based table frozen in config_f1.json (base case); the
  verdict uses the base case only. Rolls: by forward/rolls_f1.json, two fills per contract held.
- No live order is placed by this test. Live trading by the user is outside E22-F1 and does not
  change it.

## 6. Data handling

- Source: the daily settlement source the user approves (section 7). Its name, terms and the
  approval date are recorded in docs/DECISIONS.md and in the ledger's first record.
- A day on which the source delivers no settlement for an instrument: no fill and no new order for
  that instrument; its position is carried and marked at its last settlement; the day is flagged.
  A day with no settlement for any instrument is a no-trade day and is not in the series.
- The ledger (forward/ledger.py; append-only JSONL with a sha256 chain) is the only record of the
  series. A broken chain, a rewrite or an out-of-order date ends the test "abandoned, no verdict".
- Prices are never back-filled from a second source after the fact, except under a written lead
  ruling logged in the ledger before the affected date's evaluation, and never after a look.

## 7. Start date and horizon

- Start: the first trade date after the user approves a daily data source (none is approved at
  registration; the clock does not run until data flows). Warm-up: the EWMAC and volatility
  estimates need history; the history used for warm-up (the source's own back history, or the
  owned stores up to 2024-02-29 spliced to the source) is declared in the start record; P&L counts
  only from the first fill after the start date.
- Horizon: 36 calendar months from the start date; the evaluation uses every trade date in
  [start, start + 36 months).

## 8. The bar (the only verdict)

Computed once, at the end of the horizon, by forward/evaluate.py on the forward daily net P&L series
in USD:
- one-sided Newey-West t of the mean daily net P&L (Bartlett kernel, lag 10), p from the standard
  normal: **p <= 0.05**; and
- annualised net Sharpe = mean / sd x sqrt(252): **>= 0.3**.
PASS iff both hold; otherwise FAIL. No other test, horizon, sub-period or cost case decides it.
Power (stated before the start): with a true annualised Sharpe S the expected t over 3 years is about
S x sqrt(3); at S = 0.5 that is 0.87, so p <= 0.05 is reached with probability of roughly 0.2; at S =
1.0 about 0.6. A FAIL at 36 months is therefore weak evidence against a modest edge; a PASS is
strong evidence for one.

## 9. Interim looks

Every 6 months from the start date, forward/report.py produces a descriptive look (mean, sd, Sharpe,
drawdown, turnover, costs, flagged days). No p-value is computed at a look, nothing is changed
because of a look, and there is no early stop for success or failure. The test may end early only
"abandoned, no verdict" (section 6, or the user stops it), and an abandoned E22-F1 is never
restarted under the same ID.

## 10. Program accounting

E22-F1 is one trial: N 532 -> 533 at registration. It is not part of any Holm family. Its result,
when it exists, is reported with the program N at that time.

## 11. Freeze record

(Filled at the freeze: the sha256 of every file in section 2, the harness sha256 at registration,
the registration time and entry id.)
