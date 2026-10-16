# forward/: E22-F1 forward rule core and paper runner

Stage E.22, Part B (B5); spec: reports/stage_e22_briefs/lead_spec_B.md S7.

Ownership:
- MicroBookCoder: `core.py`, `strategy.py`, `config_f1.json` (the rule core and its frozen constants).
- ForwardRunnerCoder: `runner.py`, `ledger.py`, `sources.py`, `rolls.py`, `rolls_f1.json`,
  `history.py`, `evaluate.py`, `report.py`, this README; tests `tests/test_forward_runner_*.py`.

Nothing here makes a network call, uses a vendor client or reads a key. Prices are entered by
hand (CSV) or by a source the lead adds. cmegroup.com is never fetched.

## Daily procedure (operator)

1. After the settlement, append the day's rows to the settlement CSV (format below).
   On and after an instrument's roll date, until the roll executes, enter BOTH the held and the
   next contract.
2. Run the day:
   `uv run python -m forward.runner --ledger L.jsonl --csv S.csv --tables T.json --config forward/config_f1.json --date YYYY-MM-DD`
   If weekdays were skipped because the exchange was closed, add `--closed YYYY-MM-DD ...`.
   Any other skipped weekday is refused: run it (missing data is recorded, flagged).
3. Check the chain: `uv run python -m forward.ledger L.jsonl` (exit code 1 on any break).
4. Every 6 months (look k = 1..6):
   `uv run python -m forward.report --ledger L.jsonl --look k --capital C --out look_k.md`.
5. After 36 months: `uv run python -m forward.evaluate --ledger L.jsonl` (the frozen bar).
   Before that it refuses; `--interim` gives descriptive figures only (no t, no p).

Before the clock starts, print the declared roll dates and check them against the exchange's
published roll calendar (by hand; never by automation on cmegroup.com):

```python
from datetime import date
from forward.rolls import load_rolls, roll_schedule
for spec in load_rolls().values():
    for row in roll_schedule(spec, date(2026, 11, 1), date(2027, 12, 31)):
        print(row)
```

## Inputs

Settlement CSV (`forward.sources.CsvSettlementSource`), one row per contract per trade date:

```
# comments allowed
trade_date,instrument,contract_id,settlement
2026-11-02,MNQ,MNQZ26,21034.25
```

contract_id = root + month code + 2-digit year (`MNQZ26`, `10YH27`). Duplicates, non-finite
prices, malformed ids and instruments outside the universe stop the run. A date with no rows is a
missing day.

Tables JSON (`--tables`, frozen by the lead; not written here):
`{"multipliers": {inst: USD per 1.0 of the quoted price per contract}, "cost_per_side": {inst: USD per contract per side}}`.
The multiplier must match the units the CSV is entered in (for example MNQ 2.0 per index point;
a micro yield contract quoted in yield percent is $10 per bp = 1000.0 per 1.00).

Warm-up (optional `--warmup`): JSONL of `HistoryRow.to_json()` rows dated before the first ledger
date. They are passed to the strategy, never traded, and fingerprinted into every record.

## Strategy interface

`forward.strategy.target_positions(history, prev_positions, config) -> {instrument: int}` is
looked up at call time (`importlib`), never at import.

- `history`: tuple of `forward.history.HistoryRow`, oldest first, ending with the decision date
  t: warm-up rows, then one row per ledger date. A row has `date`, `prices`
  (instrument -> contract_id -> settlement, read-only) and `reference` (instrument -> the contract
  held after that day's rolls). A missing day is a row with empty prices.
- Helpers: `reference_series` (held contract's own price, for sizing), `back_adjusted_series`
  (additive back-adjustment at each reference switch, for signals) and `instrument_frame`
  (both as a pandas DataFrame with columns contract, price, adjusted).
- `prev_positions`: every instrument's contracts after day t's fills and rolls.
- `config`: a deep copy of the strategy config (config_f1.json).
- Return an int for every instrument with data on t. Values for instruments without data are
  ignored. Unknown instruments, missing entries, floats, bools and strings are refused, and
  nothing is written for that date.

## Ledger

`ledger.py`: append-only JSONL, one canonical-JSON record per trade date: `schema, date,
config_sha256, declared_closed, missing_day, prices, fills, rolls, expired_orders, costs,
pnl_by_instrument, gross_pnl, net_pnl, positions, orders, flags, prev_record_sha256,
record_sha256`. `record_sha256` = sha256 of the canonical JSON of the record without itself.
Rewrites, backwards dates, blank or truncated lines and broken links are refused; `verify()`
re-hashes the chain.

Flags: `missing_day`, `missing:I`, `order_expired:I`, `roll_deferred:I`, `roll_overdue:I`,
`contract_ahead:I`.

## E22-F1 bar (evaluate.py, frozen constants)

Window [clock_start, clock_start + 36 months); daily net P&L in USD; one-sided Newey-West t of
the mean (lag 10, Bartlett weights 1 - l/11, autocovariances with divisor T around the mean,
se = sqrt(LRV / T)); p = 1 - Phi(t); annualised net Sharpe = mean / sd(ddof 1) x sqrt(252).
PASS iff p <= 0.05 and Sharpe >= 0.3.

## Declared roll rules (rolls_f1.json; every row to be checked before the clock starts)

| Inst | Cycle (AMP, E.13 F46) | Roll date | Anchor source |
|---|---|---|---|
| MNQ, M2K | H M U Z | 6 business days before the 3rd Friday of the contract month | ES parent (Wayback, E.14); micro UNSOURCED |
| M6E | H M U Z | 7 business days before the 3rd Wednesday | 6E parent (Wayback); micro UNSOURCED |
| MGC | G J M Q V Z | 10 business days before the 1st of the contract month | GC parent termination; FND UNSOURCED |
| MCL | all months | 10 business days before the 25th of the month before | CL parent (Wayback); MCL UNSOURCED |
| MNG | all months | 10 business days before the 1st of the contract month | NG parent (Wayback); MNG UNSOURCED |
| 2YY, 10Y, 30Y | H M U Z | 5 business days before the 1st of the contract month | UNSOURCED |
| MZC | H K N U Z | 10 business days before the 1st of the contract month | ZC parent termination; FND UNSOURCED |
| MZS | F H K N Q U X | as MZC | UNSOURCED (ZC structure assumed) |
| MZL | F H K N Q U V Z | as MZC | UNSOURCED (ZC structure assumed) |

## Open choices taken (the conservative option, numbered)

1. Source shape: per instrument a map contract_id -> settlement (several contracts allowed),
   because a roll needs both legs' settlements on one date. The brief's single
   `(contract_id, price)` form is accepted and normalised.
2. An order is valid for the next processed date only. If that settlement is missing (the
   instrument or the whole day), the order expires unfilled (`order_expired`); it is never filled
   later at another price. The strategy decides again on the next day with data.
3. Steps run in the brief's order: fill, then roll. An order filled on a roll date fills in the
   old contract and the whole position then rolls (more cost than netting into the new contract).
4. A roll executes only on a date where both contracts settled; otherwise it is deferred
   (`roll_deferred`), and from the held contract's anchor date on it is `roll_overdue`. A flat
   instrument's reference contract switches under the same condition, at zero cost (needed for
   the back-adjusted series).
5. An instrument "has data" only when its reference contract settled; a settlement for another
   contract alone counts as missing.
6. A missing whole day writes a record (P&L 0, `missing_day`) and counts as a 0 in the
   evaluation series, which lowers the Sharpe rather than raising it. P&L of a missing instrument
   accrues when its data returns, from its last mark. The strategy is not called on a missing day.
7. Weekends are refused; every weekday between two records needs its own record or a
   declaration as exchange-closed in the next call (stored in that record). No exchange holiday
   calendar is modelled.
8. Integer contracts only: floats (even 2.0), bools and strings are refused; numpy integers are
   accepted.
9. Re-running a recorded date recomputes it from the previous record; an identical result
   returns the stored record, any difference raises `LedgerConflictError`, and nothing is written.
   A recorded day cannot be corrected; a correction would be a lead decision and a new ledger.
10. Every record carries a fingerprint of the multipliers, costs, roll specs, strategy config
    and warm-up rows; a runner with another configuration refuses to extend the ledger.
11. Evaluation: clock start = the first ledger date unless declared (records before a declared
    start are refused, not dropped); the horizon is complete only when a record dated on or
    after clock_start + 36 months exists; that record and later ones are outside the window; a
    zero-variance series fails the bar.
12. Interim evaluation returns neither t nor p (p could be read off t).
13. A 6-monthly look is refused until its period has closed in the ledger; it reports the
    period and the cumulative span, labels Sharpe as descriptive, and states that it changes
    nothing.
14. Roll rules count weekdays only; each roll is placed well before the parent's termination or
    first notice, or before the contract month when that is unsourced. A holiday inside the
    count moves the roll one exchange day later than the declared n.
15. Roll cost: two fills per contract (2 x |qty| x cost per side), as S3.7 states.
16. Contract-id roots 10Y and 30Y follow spec S1's names; AMP prints 10YY and 30YY. The root is a
    label the operator enters prices against.

## Not done here (for the lead)

- The tables JSON (multipliers in the CSV's quote units, D8 costs per side) is not written; the
  lead freezes it.
- The warm-up history (the EWMAs and vol need years of data before the first decision) has no
  source yet; the runner accepts one and fingerprints it.
- `forward.strategy` did not exist when this was written; the runner's tests use stub target
  functions only.
- The roll table above must be checked against the exchange's published schedule before the
  clock starts.
