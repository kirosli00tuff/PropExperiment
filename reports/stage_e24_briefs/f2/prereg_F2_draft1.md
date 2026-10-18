# E22-F2: forward-test pre-registration of the E22-F1 trend rule on a US ETF universe at $25,000

STATUS: DRAFT 1 (Stage E.24 lead, Opus 5.5 xhigh, against docs/prompts/STAGE_E.24.md C2 and V42). Written before any
ETF price exists in this program: no ETF price, return, spread or volume has been read by any session. Slots marked
[SLOT] wait on the stage's fact files (reports/stage_e24_briefs/facts/). After the freeze nothing in this file changes;
the registration records its sha256.

## 1. What is registered

One forward test, ID **E22-F2**, of one hypothesis: the E22-F1 trend rule (sections 2-5), run as a paper book on the
daily closes of 11 US ETFs that arrive after the start date (section 7), earns a positive net daily P&L in excess of
cash (section 5). Registering it adds one trial to the program: **N 538 -> 539** (ledger/trial_registrations.jsonl;
`uv run python -m screening.trial_registry register --test E24 --ids E22-F2 --freeze reports/stage_e24_prereg_F2.md
--freeze-sha256 <sha256 of this file> --harness-sha256 <harness in force>`). No historical figure enters the verdict;
no ETF history is read before the start, except the warm-up read of section 7 in the first connection session.

## 2. The rule (frozen code and constants)

- Same rule as E22-F1 (reports/stage_e22_prereg_F1.md section 2), reused through E22-F1's frozen code, unchanged:
  forward/core.py (volatility, EWMAC, forecast combination, sizing, buffer), forward/strategy.py
  (instrument_state: the per-instrument forecast and dollar volatility), forward/ledger.py, and forward/evaluate.py's
  statistics (newey_west, one_sided_p, annualised_sharpe, passes).
- New code for E22-F2 only: forward/etf_bars.py (the bar interface), forward/strategy_f2.py (positions: fractional
  longs, whole-share shorts, leverage cap), forward/runner_f2.py (the paper book), forward/evaluate_f2.py (the verdict
  on E22-F2's ledger with forward/evaluate.py's statistics), forward/config_f2.json (every constant with its source),
  forward/tables_f2.json (per-ETF costs). Data adapter: forward/sources_alpaca.py. The shadow route
  (forward/orders_alpaca.py, forward/shadow_f2.json) is not part of the verdict.
- In words (the code governs where they differ): EWMAC 8/32, 16/64, 32/128, 64/256 on each ETF's back-adjusted
  total-return close series (section 6), each scaled by Carver's published forecast scalar and capped at +-20;
  equal-weight combination x E22-F1's frozen FDM (1.1313802916085167), capped at +-20; positions for a 20% annual
  volatility target on $25,000 of notional capital (fixed, no compounding), equal instrument weights over the live
  instruments, x the IDM (below); volatility exactly as E22-F1 (config vol block: 35-day EWMA of daily price
  differences, 30% weight on the 10-year average, x 16 to annualise); an instrument is live once it has 256 daily
  differences.
- FDM: E22-F1's frozen value. Reason: the four speeds, scalars and caps are the same, and the forecast correlation is
  a property of the rule pooled over 12 futures (2010-07..2024-02); no ETF history is read to re-estimate it.
- IDM: forward.core.idm_for_live on E22-F1's frozen 12 x 12 subsystem-return correlation (config_f1.json idm),
  restricted to the 11 exposures this universe models (MZL, soybean oil, excluded), over the live instruments, cap 2.5,
  negative correlations floored at zero: **2.3293791420997985** when all 11 are live (computed 2026-10-18 from the frozen
  config only). Reason: each ETF carries the same exposure as its E22-F1 micro (section 3); a trend subsystem's return
  is invariant to quoting a bond in price or in yield (the forecast and position flip sign together), so the frozen
  correlations are the declared assumption for the ETF subsystems. Not re-estimated on ETF data, ever.

## 3. Universe

| ETF | Exposure | E22-F1 micro |
|---|---|---|
| QQQ | Nasdaq-100 | MNQ |
| IWM | Russell 2000 | M2K |
| GLD | gold | MGC |
| USO | WTI crude oil | MCL |
| UNG | Henry Hub natural gas | MNG |
| FXE | euro / US dollar | M6E |
| SHY | US Treasuries 1-3 years | 2YY |
| IEF | US Treasuries 7-10 years | 10Y |
| TLT | US Treasuries 20+ years | 30Y |
| CORN | corn futures | MZC |
| SOYB | soybean futures | MZS |

Soybean oil (E22-F1's MZL) is **not modelled**: no US-listed ETF holds soybean oil futures alone (the nearest funds
hold baskets of grains or vegetable oils, a different exposure), so a substitute would change the exposure rather than
represent it. The book has 11 instruments and equal weights of 1/11 when all are live. BIL (SPDR Bloomberg 1-3 Month
T-Bill ETF) is the cash benchmark of section 5; it is read daily and never traded.

## 4. Positions: fractional longs, whole-share shorts, buffer, leverage cap

For each decision date t (data through close(t)), with q the shares held after t's fills:
1. Unrounded target n_i (shares) from forward.core.unrounded_position with multiplier 1 and the dollar volatility per
   share of section 6; average position a_i from forward.core.average_position.
2. Leverage cap on the unrounded targets: G = sum |n_i| x close_i(t); if G > B, every n_i and a_i is multiplied by
   B / G. B = **$50,000**: the overnight (Reg T) buying power of a margin account whose equity is the fixed capital,
   2 x $25,000 [SLOT: Alpaca's Reg T overnight multiplier and any ETF-specific margin rates, facts A7].
3. Carver's buffer (E22-F1's buffer_size 0.10, trade to the edge): with lower = n_i - 0.1 a_i and upper = n_i + 0.1 a_i
   (a_i >= 0), the buffered target is q_i if lower <= q_i <= upper, else the nearer edge. No integer rounding here.
4. Granularity: a non-negative target is rounded half away from zero to [SLOT: Alpaca's fractional increment, facts A5;
   default 0.001 share]; a negative target is rounded toward zero to whole shares (shorts are whole shares only, and
   rounding toward zero never raises gross exposure). A target that changes sign is reached by closing the old side
   and opening the new one.
5. Second cap check: if the result's gross exposure at close(t) exceeds B (possible only when holdings sit at a buffer
   edge), the longs are scaled down by the factor that brings it to B (shorts already whole shares and rounded toward
   zero are left as they are), then step 4's granularity is applied again to the longs.
6. An instrument with no close on t keeps q_i and gets no new target (section 6); a live instrument whose close
   arrives gets a target; a non-live instrument's target is 0.
The orders are the differences between the targets and q, for the next session's close.

## 5. Fills, costs and the P&L in excess of cash

- Orders computed from data through close(t) fill at close(t+1), the next session's official closing price (raw,
  unadjusted), paper only. A pending order expires unfilled if the ETF has no close on the next processed session.
- P&L of a session t (USD), with N_i = q_i x rawclose_i(t-1) the signed notional held into t, r_i(t) the ETF's total
  return over the session (section 6), r_c(t) the same for BIL, L = the sum of the long N_i, K = $25,000, and d the
  calendar days from the previous processed session to t:
  - excess return of each position: sum_i N_i x (r_i(t) - r_c(t));
  - shorts: minus sum over short positions of |N_i| x (r_c(t) + b x d / 360): short-sale proceeds earn nothing, and
    the borrow fee b is charged;
  - leverage: minus max(0, L - K) x s x d / 360: the debit above the capital pays the margin spread s over cash;
  - trading costs of t's fills: per share, half the quoted spread h_i (forward/tables_f2.json), plus on every sale
    (including short sales) the SEC Section 31 fee (rate x proceeds) and the FINRA Trading Activity Fee (per share,
    capped per order); commission 0 [SLOT: facts F1-F3].
  - net_pnl = the sum of the four terms. A flat book earns 0; an unlevered long position earns its total return in
    excess of BIL.
- Constants: h_i [SLOT, declared: 0.01 USD per share for QQQ, IWM, GLD, USO, UNG, SHY, IEF, TLT; 0.03 USD for FXE, CORN,
  SOYB; declared without reading any quote: the first group trades in high volume at the one-cent minimum quote
  increment for prices above $1 (SEC Rule 612), and twice the minimum half-spread is assumed; the second group is
  thinner and is given three times that]; b [SLOT: facts F5; declared default 1.0% a year]; s [SLOT: facts F4; declared
  default 3.0% a year]. All are fixed for the test (not updated when a fee or rate changes) and the verdict uses them
  only.
- Splits and distributions: the shares held change at a split by the split ratio and at a distribution by
  reinvestment at the close, through q_i(t) = q_i(t-1) x rawclose_i(t-1) x (1 + r_i(t)) / rawclose_i(t) before t's fills.
- No live order is placed by this test. Alpaca paper orders (forward/orders_alpaca.py, off by default) are a shadow
  record in a separate ledger and never enter the verdict.

## 6. Data handling

- Source: Alpaca's market data API, daily bars of the 11 ETFs and BIL, feed [SLOT: facts A2/A4], requested with
  adjustment "raw" (rawclose) and "all" (splits and distributions); approved by the user as E22-F2's venue (V42).
  The connection date, the start date and the warm-up file's sha256 are recorded in docs/DECISIONS.md and the STATE file
  of the stage that starts the clock, before the first ledger record is written.
- r_i(t) = allclose_i(t) / allclose_i(prev) - 1, both values from one response, prev the ETF's previous bar in that
  response (so a split or a distribution falls inside the return).
- The signal series is rebuilt deterministically from stored data: the back-adjusted close as of t is
  rawclose_i(t) at t and, going back, divides by (1 + r_i(u)) for each later session u; the latest value equals the raw
  close, so price differences near t are in dollars per share and the dollar volatility per share is the frozen vol
  definition with multiplier 1.
- A session on which an ETF has no bar after the cutoff: no fill for it (its pending order expires), no new order, its
  position carried; its P&L accrues when its data returns (r spans the gap); the day is flagged. The same for BIL: the
  cash terms of the gap accrue when BIL's data returns.
- Every NYSE weekday in the horizon has a ledger record or is declared exchange-closed in the next record (stored
  there); a declaration must match NYSE's published holiday calendar [SLOT: facts F6]. A weekday not declared closed
  with no bar for any instrument is a missing day: P&L 0, flagged, and it COUNTS as a 0 in the evaluation series.
  Declared exchange-closed days are not in the series.
- A connection failure, a rate limit, a timeout or a partial response is never a missing day: no record is written and
  the step is retried (forward.etf_bars.SourceUnavailable).
- A day's bars may be taken from a second approved source only before that day's record is written; the switch is
  logged in docs/DECISIONS.md. A recorded day is never changed.
- The ledger (forward/ledger.py; append-only JSONL with a sha256 chain; every record carries the fingerprint of the
  frozen configuration and of the warm-up history) is the only record of the series. A broken chain, a rewrite or an
  out-of-order date ends the test "abandoned, no verdict".

## 7. Start date, warm-up and horizon

- Start: the date of the first ledger record, the first NYSE session after the user approves the first connection
  session on which the source delivers bars (none is approved at registration; the clock does not run until data
  flows).
- Warm-up: the source's daily bars (raw and all-adjusted) of the 11 ETFs and BIL from 2024-03-01 to the session
  before the start, the same calendar window as E22-F1's warm-up (V42), read once in the first connection session,
  written in forward/etf_bars.py's warm-up format and fingerprinted into every ledger record. An ETF with fewer than 257
  closes is flat until it has 256 daily differences. Expected live on the start date: all 11.
- Horizon: 36 calendar months from the start date. The evaluation series is the net_pnl of every ledger record dated
  in [start, start + 36 months), including the zero days before the first fill and the missing days.

## 8. The bar (the only verdict)

Computed once, at the end of the horizon, by forward/evaluate_f2.py on the series of section 7, in USD, with
forward/evaluate.py's functions:
- one-sided Newey-West t of the mean daily net P&L (Bartlett kernel, lag 10), p from the standard normal: **p <= 0.05**;
  and
- annualised net Sharpe = mean / sd x sqrt(252): **>= 0.3**.
PASS iff both hold; otherwise FAIL. No other test, horizon, sub-period or cost case decides it.
Power (stated before the start): with a true annualised Sharpe S the expected t over 3 years is about S x sqrt(3), and
the power is 1 - Phi(1.645 - S x sqrt(3)): S = 0.3 -> 0.13, S = 0.5 -> 0.22, S = 1.0 -> 0.53. Under iid daily P&L,
p <= 0.05 at 36 months already implies a realised Sharpe of about 0.95, so the Sharpe leg rarely binds. A FAIL at 36
months is weak evidence against a modest edge; a PASS is evidence for one at the registered level.
Expected behaviour, stated so that it is not a surprise (no data read; typical annual volatilities from general
knowledge, unsourced, and nothing in the rule depends on them): the short-bond fund SHY and the currency fund FXE have
low volatility, so their unrounded positions need notionals of several times the capital; the cap of section 4 is
expected to bind on most days, scaling the whole book down proportionally and running it below its 20% target. The
verdict's t and Sharpe do not depend on the book's scale.

## 9. Interim looks and stopping

Every 6 months from the start date, a descriptive look (mean, sd, Sharpe, drawdown, turnover, costs, flagged days,
days the cap bound). No p-value is computed at a look, nothing is changed because of a look, and there is no early
stop for success or failure. The test may end early only "abandoned, no verdict" (sections 2, 6, 7, or the user stops
it). An abandoned E22-F2 stays in N, is reported with its descriptive figures at the stop date and the reason, and is
never restarted under the same ID; a restart of the same rule is a new ID and N + 1.

## 10. Program accounting

E22-F2 is one trial: N 538 -> 539 at registration. It is not part of any Holm family. E22-F1 and E22-F2 run the same
rule on overlapping exposures over the same dates, so their results are correlated: two PASSes are not two independent
confirmations, and each is reported with the program N at that time.

## 11. Freeze record

[SLOT: frozen time, harness, the file list with sha256 in `sha256sum -c` form, also written to
reports/stage_e24_f2_files.sha256.]
