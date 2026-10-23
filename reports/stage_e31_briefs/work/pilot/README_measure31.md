# measure31: the E.31 ZM order-book engine

Written by SimCoder-OpusXHigh (Stage E.31 Part 3). Spec: `reports/stage_e31_pilot_spec.md` v2
(sections 1 to 6 and 8). Output interface: `TABLES31.md` (unchanged). K parameters:
`research/K_algorithm.md`. Lead notes of 2026-10-22 (DONE marker, rows only for included pairs,
USDA files, spec-v2 items 1 to 7) are folded in and marked "lead" below. EngineReviewer
(reports/stage_e31_briefs/R_engine31.md section B), 2026-10-23: B1 (blocking), B5, B8 and B9
applied and marked "review"; lead rulings on B2 and B7 noted where they apply.

## Files

| File | Role |
|---|---|
| `kalgo31.py` | K allocation of one match at one price level (spec 3.1). Pure, no I/O. |
| `mbo_book31.py` | One instrument's book from MBO: priorities, TOP state, snapshots, time axis. |
| `measure31_core.py` | One trade date: placements, fill models a/b/c, markouts, conditions, loop, implied check, table rows. |
| `measure31.py` | CLI: manifest guards, definitions, USDA calendar, symbology and rolls, split step, worker pool, parquet writer. |
| `tests/test_kalgo31.py`, `tests/test_book31.py`, `tests/test_measure31.py` | Synthetic tests only. |
| `tests/synth31.py` | Synthetic MBO/MBP-1 builders and a random ZM-like day for the speed probe. |

## Commands (repo root)

```bash
# tests
uv run pytest -q -p no:cacheprovider reports/stage_e31_briefs/work/pilot/tests/test_kalgo31.py \
  reports/stage_e31_briefs/work/pilot/tests/test_book31.py reports/stage_e31_briefs/work/pilot/tests/test_measure31.py

# the run (detach it: background shells die with the session); resumable per trade date
P=reports/stage_e31_briefs/work/pilot
LOG=$P/runs/measure31.log
setsid nohup nice -n 10 uv run python $P/measure31.py --manifest $P/runs/manifest31.json \
  --out $P/runs/measure31 --workers 4 --write-expected-dates $P/runs/expected31.txt > $LOG 2>&1 &
tail -n 3 $LOG

# after the run, before reading any verdict (review B5): counts only, no market values
uv run python $P/measure31.py --out $P/runs/measure31 --summarize-diag   # -> runs/measure31_diag_summary.json
```

Run with `--workers 4` (lead ruling on review B7: 4 x 0.8 GB stays under half of the available
memory), one heavy job at a time, and outside the AiTrader collector window (about 15:30-16:00 PT
on weekdays). `--summarize-diag` needs only `--out`: it sums every date's `diag.json` per symbol
(book anomalies, events, `events_mid_update`, `events_without_passive_fill`, deferred timers,
skipped implied prints, records before a valid start, markout drops by reason, exclusion reasons)
and gives the ratios `events_mid_update_per_event` and `events_without_passive_fill_per_event`,
to be read next to the (a)/(b) results.

Options: `--workers N` (capped at min(8, cpu_count // 2); default the cap), `--dates FILE` (ISO
dates, one per line; each must be a purchased trade date), `--write-expected-dates FILE` (every
purchased trade date, the file stats31 `--expect-dates` reads; written from the whole manifest
even with `--dates`), `--derived DIR` (default
`/mnt/large-storage/market_data/PropExperiment/derived/e31`), `--chunk-records N`.
Exit codes: 0 done, 1 some dates failed (listed; rerun resumes), 2 refused before measuring.

Steps: manifest guards; definitions (Z4) first, summary in `<out>/definitions31.json` (match
algorithm, tick, contract size, implied fields per outright; a warning if any ZM outright is not
K); the split (each Z1/Z2/Z3 file streamed once into `<derived>/<series>/<YYYY-MM-DD>.npy` plus
`<series>/<month>.split.json`, skipped on restart when the marker's sha256 matches); then one
worker per trade date writes `<out>/<YYYY-MM-DD>/{placements,loop,implied,days}.parquet` and
`diag.json` (counts the tables cannot hold), and the file `DONE` last (lead). A date with `DONE`
is skipped on restart; a folder without it is rewritten.

## Guards

- Manifest: refused when verify31's exit code is 2 or any file has a failed hard check; every
  file's request must end at or before 2024-02-29T22:00:00Z and must not touch a sealed window
  (`data.holdout.request_touches_sealed_window`); Z1 and Z4 must be present.
- Files: sha256 re-checked against the manifest before reading; the DBN metadata end must be at
  or before 2024-02-29T22:00:00Z; every chunk is checked and any record (ts_recv or ts_event) on
  or after 2024-03-01T00:00:00Z stops the run before it is used. `measure_day` repeats the check
  and refuses a trade date on or after 2024-03-01.
- Ticks (lead item 2): each root's tick is the Z4 `min_price_increment`, and tick x
  `unit_of_measure_qty` must equal ZM 10.00, ZS 12.50, ZL 6.00 USD, else the run stops with the
  values. ZM must also be 0.10 x 1e9 (prices are written in USD/short ton). **Finding
  (2026-10-23 probe on the 2024-01 Z4 file): ZM passes; ZS and ZL are encoded in cents (ZS 0.25
  x 5000 = 1250, ZL 0.01 x 60000 = 600), so the check as stated stops the run.** The engine uses
  ZS/ZL ticks only as divisors (d in ticks), which is unit-free, but the conversion rule for the
  check is the lead's decision; the code is left stopping.
- USDA (lead item 7, replacing the brief's refusal): a trade date outside the covered range
  2020-12-01..2024-02-29 is measured with `usda_min` NaN.

## Match-event grouping rule

Per instrument, in file order: consecutive T records with the same time (the spec-2 time axis),
price and aggressor side, together with the F records that follow them at the same time, form
one match event. A T record with a different price, time or side, an F record at another time,
or any book record (A, C, M, R, N) closes the event. For an event at price p with aggressor side
A (seller) the passive side is the bid, for B the ask:
- v = the sum of the event's T sizes;
- F = the sum of the event's F sizes whose side is the passive side and whose price is p (the
  aggressor's own F record, emitted when it rested before, carries the aggressor side and is left
  out);
- the outright volume is Q = min(v, F). Models (a) and (b) use Q (spec 3.1: implied parts are not
  reallocated). An event with F = 0 is counted (`events_without_passive_fill`) and fills nothing.
- Side-N trades are never match events for a virtual order (and never through triggers); their
  F records are absorbed and ignored. They are counted in implied.parquet (`n_n`, `vol_n`).

## Conventions (choices the spec leaves to the code)

Book and time
1. File order is used as is (no re-sort): Databento writes MBO in ts_recv order, and sorting by
   sequence could reorder snapshot priority and T/F groups. Each instrument's records are taken
   in file order.
2. Time axis: ts_event made non-decreasing per instrument (running maximum). Snapshot records
   (F_SNAPSHOT) enter with ts_recv (their generation time), since their ts_event is not an event
   time; inversions are counted over non-snapshot records only (`days.inversions`).
3. Reads only after F_LAST (lead item 1): timers (placement and loop joins, life ends) fire only
   when the instrument's last processed record carried F_LAST; otherwise they wait for the next
   F_LAST record (`timers_deferred_mid_update`). BBO history and mid0 are committed only at
   F_LAST records. Events and the implied check read the book when no book record (A, C, M, R)
   has been applied since the last F_LAST record (T, F and N records change nothing, so the
   second and later levels of a sweep read the same consistent book as the first; review B8).
   Otherwise the event takes no queue fill (`events_mid_update`) and the print is left out of the
   implied check (`implied_trades_mid_update`, to be reported beside the check). The implied check
   reads the book before the M/C records of the same event, as spec 8 says ("just before the
   trade").
4. A timer at time T sees the book after every record stamped at or before T; a trade stamped
   exactly at j is part of the join state; a trade stamped exactly at the life end c finds the
   order gone. The life is the open interval (j, c), c = min(j + 60 s + 50 ms, session end).
5. Book validity (spec 2): valid from an R record (snapshot or channel reset). Records before
   the first R of the date are skipped (counted). A date is excluded for an instrument when no R
   comes at or before its first session open (19:00 CT the evening before): reason
   `no_valid_book_start`. F_MAYBE_BAD_BOOK (and, conservatively, F_TOB or F_MBP) marks the book
   bad until the next R: from that record, resting placements are dropped and not written, no
   placement joins, and history states are invalid (markouts crossing them are dropped). A loop
   already running stops; the loop row is not written when a bad period overlaps the DAY session.
   F_BAD_TS_RECV records stay in the book (snapshots carry it).
6. Book anomalies (cancel or modify of an unknown order, duplicate add, side change) are applied
   as Databento's example does (modify of an unknown order = add) and counted in `diag.json`.
7. `crossed_moments` (days) counts grid joins skipped because the book was crossed, locked or
   had an empty side; joins skipped for a bad or unstarted book are counted in `diag.json`.

TOP (spec 3.1 and lead items 4, 6)
8. TOP on entry (add, or a price-changing modify) when displayed size >= TOP Min and (i) the
   price betters its side's best (or the side is empty), or (ii) it joins the side's current best
   level and that level has had no TOP since it was established. (ii) is applied at the best
   level only, so the TOP order is always at its side's best. A new TOP replaces the old one; if
   the new order cannot be TOP (TOP Max already reached under the old rule) the old one keeps it.
9. TOP is lost on a full cancel, a size increase, a price change that does not better the
   market, or when the lots counted against TOP Max reach it (counted from the TOP order's F
   records). A price change that betters the market keeps TOP and its count. A size increase
   never grants TOP.
10. An event's F records count against TOP Max only after the event's allocation (review B1):
    the TOP room of spec 3.1 step 1 is "TOP Max minus its fills since it rested" before the
    event. F records outside an event (no T before them) count at once (counted in diag.json).
    TOP Max counting (lead item 6): from trade date 2023-10-02 only fills after the order rests
    count; before it, the aggressor's own T quantity (T order_id = the later A record's id) is
    counted too, and an order whose initial aggression already reached TOP Max is not TOP.
11. Snapshots carry no TOP state. At a snapshot's end the first order of each side's best level
    is taken as TOP with 0 lots counted, the best levels are marked as having had a TOP and the
    others as not. This is the conservative reading: a TOP order only ever takes volume ahead of
    the virtual order.
12. The virtual order is never TOP (lead item 4) and never changes TOP state: TOP state is the
    real book's, so an order that re-establishes a level emptied in the real book betters the real
    market and is TOP even when the virtual order rests there (tested).

Fill models
13. (a) K: the queue at p in time priority, the virtual 1-lot inserted by its priority number
    (orders that joined or lost priority after j are behind it); Q allocated by `kalgo31`; the
    FIFO exception counts the virtual order (Q >= D + 1, tested at Q = D, lead item 5); fill when
    the virtual order's allocation >= 1.
14. (b) FIFO, literal and conservative: Q_ahead = the current sizes of the orders that were at p
    ahead of the virtual order at j and still rest at p (an order ahead that increased its size
    stays counted with its new size); fill when Q > Q_ahead. Q is the outright volume, not the
    print volume v of spec 4(b): lead ruling on review B2 (conservative, matches spec 3.1's
    implied rule; logged as an erratum).
15. Through trigger (all models): the first A/B trade strictly through p while the order rests,
    any aggressor side (E.28). A queue fill and a through fill at the same instant: the first in
    file order wins (the queue event at p closes before the next level's T record).
16. mid0 = the last valid mid committed (F_LAST) before the fill event, as the spec's "last valid
    mid at or before t". `c_half` is NaN only when no valid mid existed earlier in the date.

Placements, markouts, conditions
17. Grid (lead item 3): open + 5 min <= g < close - 5 min on the CT clock: DAY 08:35..13:10
    (56 times, 112 placements), OVERNIGHT 19:05..07:35 (151 times). Prices and Q_ahead from the
    book at j = g + 50 ms; an invalid book at j takes no placement on either side.
18. `stale`: the best price on the order's side in the last committed state at or before g differs
    from the price at j (no state at g counts as stale).
19. `touched`: inside (j, c) a trade at or through p (any side, N included) or an opposite best
    quote at or through p (E.28's touch).
20. Markouts: headline dropped when t_f + h reaches the session end, when any committed state over
    [t_f, t_f + h] is invalid (crossed, locked, empty side, bad period), or when no state precedes
    t_f; no-drop variant = the last valid state at or before t_f + h if it is active after t_f
    (session-end drops apply to both). Drop counts by reason are in `diag.json`.
21. ZS/ZL moves: mid(t) = the last valid mbp-1 state at or before t (valid: both sides defined,
    bid < ask, no bad-book flag) from a record inside the fill's session; else missing (NaN).
    d = (mid(t_f) - mid(t_f - L)) / tick for L = 1, 10 s. The series is ZS.v.0 / ZL.v.0 filtered to
    the instrument the symbology maps on the date. Computed for fills only; NaN for unfilled rows.
22. USDA (lead): every row whose report is not NOPA, except dates ending "-NORELEASE"; UNCERTAIN
    and RULE-DERIVED rows as listed; the two "X-OR-Y" rows (FAS weeks of 2023-07-06 and
    2023-11-23) are used with both alternatives; time_et is America/New_York. A release belongs to
    the trade date whose window [D-1 16:00 CT, D 16:00 CT) holds it. `usda_min` = signed minutes
    to the nearest release of the fill's trade date (ties: the earlier release); NaN when none or
    outside the coverage. Rows used: FAS Weekly Export Sales 167, NASS Crop Progress 105, NASS
    Crop Production 39, USDA WASDE 39, NASS Fats & Oils 39, NASS Grain Stocks 13, NASS Crop
    Production Annual 4, NASS Acreage 3, NASS Prospective Plantings 3 (412 rows; 331 trade dates
    with a release). Skipped: NOPA 39, NORELEASE 3, no clock time 0.

Days and exclusions
23. Trade dates: grains-calendar trade dates of the purchased Z1 months (full closures are not
    trade dates). Records are assigned by ts_recv to [D-1 16:00 CT, D 16:00 CT); records falling
    on non-trade dates (weekends, closures) or outside the file's month are dropped in the split
    (counted in the marker).
24. One `days` reason per (date, symbol), first by precedence: calendar (`cme_holiday_or_early_close`,
    `scheduled_late_open`), roll (`roll_day`, `after_roll_day`, `roll_status_unknown`,
    `no_symbol_mapping`), `no_records`, `no_valid_book_start`, `day_gap_gt_60s`. `diag.json` holds
    the per-symbol details.
25. Rolls: the instrument behind ZM.v.0 and ZM.v.1 on trade date D is the symbology interval
    holding UTC date D (a grain trade date's sessions lie inside UTC day D). D is a roll day when it
    differs from the previous trade date's instrument; the next trade date is excluded too. When
    the previous trade date has no mapping (the window's first date) the date is excluded as
    `roll_status_unknown` (conservative).
26. Gap (review B9, spec 2 text): the largest gap between consecutive front-month records inside
    DAY [08:30, 13:20) CT; the open and close are not edges. Fewer than two records inside gives
    the session length (excluded). Above 60 s the date is excluded for both symbols.
    `max_gap_day_s` is reported for each symbol on its own records.
27. Tables hold rows only for included (date, symbol) pairs (lead); excluded pairs appear only in
    `days.parquet`, with `crossed_moments`, `placements_day` and `placements_on` 0.

Loop (spec 6)
28. Joins use the book at the join time (as placements). Decisions only before close - 5 min. A
    cancel is decided at j + 60 s and the replacement joins at c = j + 60.05 s. When the book is
    invalid at a join, the order is not placed and the next decision is at the first later valid
    committed state. Round-trip duration = exit fill time minus the decision time of the round
    trip's first entry order; the next entry is decided at the exit fill. An open position at the
    end is not counted.

Implied check (spec 8)
29. Every T record inside a session [open, close) while the book is started and not bad, read
    only after F_LAST (convention 3), for both symbols. A/B trades: `n_ab`, `vol_ab`; passive-side
    displayed quantity at the price just before the trade = 0: `n_none`, `vol_none`; below the
    trade's size (zero included, literal reading of "less displayed resting quantity than the
    trade's size", so `n_short` >= `n_none`): `n_short`, `vol_short`; side N: `n_n`, `vol_n`.

## Speed and memory

- Synthetic random day (945,811 records, 56,052 events): 0.79 s in the engine, 1.2 M records/s,
  peak RSS 368 MB including the generator.
- Real data, 2026-10-23 01:01-01:02 PDT, structure check only (lead): split of the 2024-01 files:
  Z1 20,404,528 records in 3.7 s (5.5 M records/s, sha256 check included), Z2 5,980,787 in 1.1 s,
  Z3 3,742,569 in 0.7 s; split peak RSS 469 MB; 1.3 GB of split arrays for one month. One trade
  date (2024-01-24) end to end: 849,507 ZM records in 0.87 s (0.97 M records/s), peak RSS 277 MB.
  The scratch output and the probe's split arrays were deleted; no placement or markout value
  was opened.
- Estimate for 700 trade dates on 8 workers: at about 1 M records per date and 1 s each (2 s for
  days twice as busy), about 700 to 1,400 worker-seconds, so 2 to 3 minutes of wall time, plus
  the split at about 6 s per month of the four series (about 4 minutes for 39 months, single
  process). Peak memory per worker about 0.3 GB at 1 M records per date, rising roughly in
  proportion (allow 0.8 GB for the busiest days); the run uses 4 workers (lead), so about 3.2 GB
  at most and roughly twice the wall time above (4 to 6 minutes for the dates). Split arrays on
  disk: about 1.3 GB per month.
