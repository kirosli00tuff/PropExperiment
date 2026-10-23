VERDICT: NO GO (one BLOCKING item, model (a) only; the gate (c), K1-K3 and the stats layer are clean; fix item 1, re-run the tests, then GO)

# Stage E.31 Part 4, pass 2: EngineReviewer-FableXHigh review of the engine and stats code

Reviewer: Fable 5.1 (xhigh), 2026-10-23, 00:59 to 01:30 PDT. Review only: no Databento call, no purchased file or measure31
output opened (the engine was run on synthetic data only), no edit except this file, no commit. Spec sha256 recomputed =
31d33e68736b3c13ae46afcd0bf8d28411bbb3d96864802a6193cf5f33b9f61a. Holdout `unlocks_logged` 0, `all_ok` true (start and end);
REGISTRATION.md 0 bytes. pull31, pilot31_common, verify31, canary_check31 were not reviewed (FixCoder's).

## A. What I checked and found sound (evidence)

1. Tests: `pytest -q -p no:cacheprovider .../tests` = 313 passed (17 s); engine + stats subset 141 passed.
2. K allocator (kalgo31.py). Hand recomputation, two cases: [30,10,20,5,1], Q=60, TOP=A: TOP 30, Q1=30, FIFO ceil(12)=12 (B 10,
   C 2), pro rata 18 over W=24 (C 13, D 3, V 0), leveling 2 lots to V only participant at 0 -> V 1, residual 1 to C: total
   [30,10,16,3,1]; and [4,2,2,1], Q=7: FIFO 3, PR 4 over W=6 -> [0,1,1,0], leveling lots to order 1 then V -> [4,1,1,1].
   Both equal the tests. E3/E4 (CME): [0,0,7,0,3,37] and leveling orders 2,1,4 as printed. Independent reference written from
   spec 3.1 steps 0-7 vs `ka.allocate`: 60,000 random cases (n<=9, TOP/room random, 8,628 FIFO-exception cases), 0 differences,
   sum<=Q and allocation<=quantity always. Virtual never TOP, FIFO exception on D+1 (Q=D runs K), ceil split (Q=5 -> 2/3),
   post-FIFO denominator, leveling (larger, then earlier): all as spec v2.
3. Book (mbo_book31.py): A/C/M/R match Databento's own book example (research/pages/data/db_ex_lob): C removes `size`
   lots, M decrease keeps priority, increase or price change goes to the back, unknown M = add; Databento's ES order
   life-cycle sample (db_ex_order_actions) shows F then, ~58 us later, M/C: the engine's "group closes at the first book
   record" design fits it. Snapshots R then A with F_SNAPSHOT, end at F_LAST. TOP Max counting switch at trade date 2023-10-02
   (`day < 2023-10-02`) tested both ways.
4. Fill models: (c) strictly through, A/B only, never on a touch; the order joins at j with `prio = book.seq` (behind every
   resting order), Q_ahead tuple fixed at j; `t < o.end` bounds every fill; a trade stamped j is in the join state; life
   (j, j+60.05 s); (a)/(b) also fill on a through trade. Synthetic probes confirm the invariants (model (b) fills >= model (c)).
5. Look-ahead: mid0 = last mid committed at an F_LAST before the fill event; history entries are stamped with the F_LAST
   record's time and looked up with `searchsorted(right)`, so no state later than t_f enters mid0, c, or a condition; ZS/ZL
   `mid_at` is at or before the time asked; imbalance and queue are read at j; USDA release times are fixed calendar data.
6. Markouts: E_h = markout + c = s(mid(t_f+h) - p)/tick algebraically; headline drop over [k_f, k_h]; no-drop = last valid
   state in [k_f, k_h]. With the 5-minute edge exclusion no DAY or OVERNIGHT placement can reach the session end within 60 s,
   so the session-end drop (README 20) never fires and cannot differ between the variants.
7. Grid: DAY 56 times (08:35..13:10), 112 placements; OVERNIGHT 151 (19:05..07:35); CST/CDT tested; grains calendar (`data.group_session`, listed during
   the review): the early halts (2020-12-24, 2021-11-26, 2022-11-25, 2023-11-24) and the scheduled late opens (2021-07-06,
   2022-07-05, 2023-07-05, 2023-12-26, 2024-01-02 and the day-after-Thanksgiving dates) are excluded by `calendar_reason`;
   full closures are not trade dates.
8. Loop: decisions before close - 5 min; cancel decided at j+60 s, replacement joins at j+60.05 s; entry alternates, starts
   with a buy at the first grid time; exit decided at t_f and joins +50 ms; open position not counted; rows only for measured dates.
9. Stats: kill rule recomputed independently on 40 synthetic dates with decoy cells (other model, ZM.v.1, OVERNIGHT, extreme
   edges): N_10 point and 95% bounds equal to 6 decimals for both variants (default_rng(31).integers(0,n,(2000,n)), ratio of
   sums per replicate, fee 0.264), K2 count equal. Code reads: K1 fails if EITHER lower bound is not above 0, K2 counts fills
   before any drop, K3 is the mean of loop rows (measured DAY dates), fragile = PASS whose 0.528 bound (either variant) is not
   above 0, 0.528 never decides. Completeness gate refuses on a missing or an unexpected done folder before reading a table.
   Spec section 5's "headline and gate use the dropping version" is superseded by v2 section 7 (lead's erratum); the code follows 7.
10. Cut-off: manifest request end <= 2024-02-29T22:00Z, metadata end, per-chunk ts_recv/ts_event guard (definitions included),
    `measure_day` guard, sealed-window check; nothing reads on or after 2024-03-01.
11. Speed and memory (synthetic only): 756,191 records in 0.65 s engine time (1.17 M records/s), peak RSS 317 MB with the
    generator; README figures reproduced. Split arrays about 51 GB for 39 months; /mnt/large-storage has 757 GB free.

## B. Items

### BLOCKING

1. [BLOCKING, model (a) only] TOP state is read AFTER the event's own fills were counted against TOP Max.
   measure31_core.py:556 calls `book.on_fill(oid, sz)` at each F record; `close_event` runs later (at the next non-T/F record)
   and `_k_allocation` (402-413) reads `book.top_at` (mbo_book31.py:281-289). `on_fill` (270-279) has by then added the event's
   own lots to `top_count`, so TOP room = 100 - count - own fills instead of spec 3.1 step 1's "100 minus its fills since it rested"
   (before the event), and if the event itself reaches TOP Max the order is dropped as TOP before the allocation. The TOP
   step is wrong whenever count_before + own fill + Q > 100 (about count_before + 2 x Q > 100 when the TOP order takes the event). Probe (synthetic, `run()` of the test file): snapshot bid 349.9 = o1 150
   (snapshot TOP, count 0), o2 20; a 70-lot seller fills o1 for 70. Spec allocation `ka.allocate([150,20,1],70,top=0,top_room=100)`
   = [70,0,0] (V gets nothing); the engine's allocation uses room 30 = [66,3,1] and the model (a) virtual order FILLS. The
   bias is optimistic (more (a) fills) and hits large events and TOP orders near 100 lots. The gate (c), (b), K1-K3 are not affected.
   Fix: defer `book.on_fill` for F records that belong to an open group until after `close_event` (keep the (oid, size) pairs
   in the group list, apply them right after the allocation, also in `drain`), keep immediate application for orphan F records.
   Add two tests: the 70-vs-150 case above (virtual gets 0) and count 95 + a 6-lot event (TOP takes 5 and is lost afterwards).

### ADVISORY

2. [ADVISORY, lead ruling] Convention 14 deviates from spec 4(b): the spec fills (b) when the event "volume v exceeds Q_ahead"
   (v = sum of the print sizes, spec 3); the code uses Q = min(v, F) (measure31_core.py:379, 397). Conservative (an implied part
   of a print cannot fill the virtual order), documented in the README. Confirm it is intended; the implied check
   (share of prints with F < v) shows how big the difference is.
3. [ADVISORY] Event key is (ts_event, price, aggressor side) (measure31_core.py:501-504, 538-544), not the aggressor order id,
   so two aggressors printing at the same nanosecond, price and side with no book record between them merge into one event with
   Q = sum (a larger Q is optimistic for (a) and (b)). Spec 3 literally says "share its ts_event and price", so this is within the
   spec; adding the T order_id to the key when it is non-zero is a one-line tightening that matches "per aggressor".
4. [ADVISORY, model (a) caveats to print with the results] (i) TOP rule (ii) is applied at the best level only (mbo_book31.py:194,
   README 8); spec 3.1 says "a level that has had no TOP order". (ii) Snapshot TOP = first order of each best level (README 11).
   Both keep a TOP order ahead of the virtual order more often, i.e. conservative. (iii) Spec-literal D+1 test: at Q = D (a level the
   print cleared completely) the virtual order can take a lot from a real order, i.e. optimistic. Net direction not known; say so.
5. [ADVISORY, before reading any verdict] Nothing aggregates `diag.json` (book anomalies cancel_unknown_order,
   modify_unknown_order_as_add, add_duplicate_id; events, events_without_passive_fill, events_mid_update,
   timers_deferred_mid_update, implied_trades_mid_update, records_before_valid_start, markout drops by reason, bad-book flags).
   A wrong T/F/C ordering assumption on the real feed would show only there. Sum them over all dates and print the ratios
   (events_mid_update / events, events_without_passive_fill / events) next to the (a)/(b) results; large values disable queue fills quietly.
   Same idea for canary_check31 (structure only, no prices): the share of T records whose predecessor in the instrument's
   records carries F_LAST, and whether a C or M with the F's order_id follows each F.
6. [ADVISORY] Placement price and queue come from the book at j = g + 50 ms (spec 4 and E.28, measure31_core.py:322-338), while
   the decision time is g; this is spec-literal, `stale` reports how often the best price at g differs. Read the stale share
   beside the fill rates; no code change.
7. [ADVISORY, compute limits] 8 workers x up to 0.8 GB (README) = 6.4 GB against 8 to 9.5 GB available during the review (`free -m`);
   CLAUDE.md allows half of the available memory. Run with `--workers 4` or measure the busiest date first; README_measure31 has no
   note on the 15:30-16:00 PT collector window (spec 9 requires it); only one heavy job at a time.
8. [ADVISORY] The implied check skips prints that follow a record without F_LAST (second and later levels of a sweep,
   `implied_trades_mid_update`) and reads a book that is not yet reduced by the M/C of the previous fill (Databento's sample shows
   the M/C about 58 us after the F), so shares (i) and (ii) are biased slightly low. Report the skipped count with the check.
9. [ADVISORY] Gap rule counts the session open and close as edges (measure31_core.py:732-736); spec 2 says "between ZM front-month
   records inside the DAY session", so a quiet last minute excludes a date the spec would keep. The number of such dates is in
   `days.max_gap_day_s`; read it before the verdict (K2/K3 depend on the date count).
10. [ADVISORY] The bootstrap pool is every done folder (stats31.py:588-593), including dates excluded for ZM.v.0 (roll, gap,
    early close); empty blocks add a little width only. The K3 mean itself uses measured dates. State the pool size in the return.
11. [ADVISORY, low] ZS/ZL conditions do not apply the F_LAST rule (CondSeries, measure31_core.py:645-671); they decide nothing.
    An MBP-1 price scale check (median ZS mid / tick should be near 5,000 ticks if both are in cents) would catch a unit mismatch
    in `d`; the lead's cents rule only checks the tick x contract-size product.

## C. Not verified

- Anything that depends on the real feed: T/F/C record order and F_LAST placement (item 5), roll-time snapshots, how often
  multi-level sweeps and two-aggressor timestamps occur. Only the real files (canary) can show these.
- Wall-clock of the full run on real data (README estimate 2 to 3 minutes plus 4 minutes of splitting; synthetic rate reproduced).
- pull31, pilot31_common, verify31 and canary_check31 (out of scope).
