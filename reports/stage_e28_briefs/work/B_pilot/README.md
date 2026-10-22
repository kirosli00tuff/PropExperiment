# Stage E.28 Part B pilot: purchase, verification and measurement code

Written by PilotCoder-OpusXHigh, 2026-10-21 (15:36-16:05 PDT); SpecReviewer fixes RS-01 to RS-13
applied 16:3x-16:43 PDT; finished for the final QM spec by PilotFixer-OpusXHigh, 2026-10-21
(16:54-17:05 PDT, FIXES_E28b.md), and DeltaReviewer's RD-01 to RD-03 applied 17:14-17:22 PDT
(FIXES_E28b.md, "E.28b round 2"). Synthetic tests only: no Databento call of any kind was made
while this was written, and no API key was read.

Frozen spec: `reports/stage_e28_pilot_spec.md` (sha256 `8937740338e81103...`, contract QM),
with `reports/stage_e28_briefs/R_spec.md` (RS-01 to RS-13).

| file | what it does |
|---|---|
| `pilot_common.py` | constants, request guards, sessions and placement grid, day exclusions (shared) |
| `pilot_pull.py` | `--plan`, `--span-search`, `--quote`, `--buy` (spend gate on acct-3) |
| `pilot_stream.py` | streams the DBN file one trade date at a time, reduced to what the spec needs |
| `measure_core.py` | spec section 3: placements, fill rules, touches, markouts |
| `measure_stats.py` | spec section 4: cells, Kaplan-Meier, day-block bootstrap, markdown |
| `measure.py` | the measurement CLI (per-date workers, resumable, then aggregation) |
| `verify.py` | the manifest of the downloaded file(s) and its checks |
| `tests/` | pytest tests on synthetic books and synthetic DBN files (count: FIXES_E28b.md) |

## Parameters (frozen spec section 0, contract QM)

| placeholder | value for this pilot |
|---|---|
| `ROOT` | `QM` (NYMEX E-mini crude oil; Databento `QM.v.0`, energy group calendar) |
| `TICK` | `0.025` (USD per barrel; tick value 12.50 USD) |
| `FEE_SIDE` | `0.1368` tick per side (3.42 USD per round trip / 2 / 12.50), primary |
| `FEE_SIDE_ALT` | `0.296` tick per side (3.70 USD / 12.50), the conservative reading, reported beside |
| `SIMRULE` | `trade_through_only` (Topstep: the market has to trade through the price) |
| `FIRM` | `Topstep` (the `--label` of the report) |
| `B` | acct-3's usable balance in USD: 125.00 unless the portal shows a lower balance at purchase |
| `TARGET` | B - max(3.00, 0.03 x B), rounded down to the cent: 121.25 at B = 125.00 (RS-08) |
| `D` | the first whole trade date, from the span search; never later than 2024-01-12 (RS-07) |
| `APPROVED` | exactly the fresh quote of step 3 (RS-08) |

The request is fixed: GLBX.MDP3, mbp-1, `QM.v.0`, stype_in continuous, on acct-3 only, start
`start_bound(D)` = D-1 16:00 CT in UTC, end exactly `2024-02-29T22:00:00Z` exclusive (16:00 CT,
the end of CME trade date 2024-02-29; no record of trade date 2024-03-01 is bought, RS-01). Every
mode of pilot_pull.py refuses, before any call, a root other than QM (`pilot_common.PILOT_ROOT`,
RD-01) and an end other than exactly `2024-02-29T22:00:00Z` (RD-02); with the start check of
RS-07 this means every bought span holds the whole minimum span. One purchase only: `--buy`
refuses when the ledger already holds a commit on acct-3 for any other request (RD-01). The
minimum span
for QM is [2024-01-12, 2024-02-29T22:00Z), i.e. start `2024-01-11T22:00:00Z` or earlier (frozen
spec section 6, "Corrected after review": QM rolls monthly, so about 8 roll-day exclusions in four
months; 2024-01-18 was the QG value and is not used).

Run every command from the repository root:

```bash
cd /home/kiros-li/Documents/GitHub/PropExperiment
P=reports/stage_e28_briefs/work/B_pilot
uv run python -m data.holdout status          # record unlocks_logged (CLAUDE.md)
uv run pytest -q $P/tests -p no:cacheprovider # this folder's tests only, never the repo suite
```

## 1. Plan (no call of any kind)

```bash
uv run python $P/pilot_pull.py --plan --root QM --first-trade-date 2024-01-12
```

This prints the exact request (start `2024-01-11T22:00:00Z`, end `2024-02-29T22:00:00Z`), the
target file
`/mnt/large-storage/market_data/PropExperiment/data/vendor/databento/GLBX.MDP3/mbp-1/QM_v_0/range=2024-01-11T220000Z_2024-02-29T220000Z.dbn.zst`
(in general `range=<start_bound(D) as YYYY-MM-DDTHHMMSSZ>_2024-02-29T220000Z.dbn.zst`), whether
the request covers the minimum span, the spend target for `--balance-usd`, and acct-3's ledger
position (committed, cap 125.00, headroom). `--start <bound>` can replace `--first-trade-date`.
Any `--end` other than exactly `2024-02-29T22:00:00Z` (later, such as the old `2024-03-01`, or
earlier) is refused, rc 2, and so is any `--root` other than `QM`.

## 2. Span search (free quotes only, never buys)

```bash
uv run python $P/pilot_pull.py --span-search --root QM --balance-usd B \
    --out $P/runs/span_QM.json [--target-usd X] [--first-listed YYYY-MM-DD] [--earliest YYYY-MM-DD]
```

TARGET is computed from `--balance-usd` (default and maximum 125.00) as B - max(3.00, 0.03 x B)
rounded down to the cent; `--target-usd` may only lower it. The search bisects over trade dates
D no later than 2024-01-12 for the earliest D with cost([start_bound(D), 2024-02-29T22:00:00Z))
<= TARGET, making one ledgered quote per step under session `stage-E.28-pilot-span` (cap 0.00;
about 2 + log2(number of trade dates) quotes, around 14). It extends the start backwards only;
the end never moves. If even the minimum span [2024-01-12, 2024-02-29T22:00Z) costs more than
TARGET, the plan is "buy nothing" (exit 1). Without `--first-listed` it makes one free
`symbology.resolve` call to find the root's first listed date. The default lower bound is the
group calendar's coverage start (2019-05-01), because measure.py can only measure covered dates;
`--earliest` moves it. The timeseries and batch namespaces are replaced by raising guards before
the first call. The output gives `first_trade_date`, `start`, `cost_usd`, the next earlier
candidate's cost, `limited_by_lower_bound`, `costs_monotone` and every quote. Exit 0 = plan
found; 1 = infeasible or a quote failed; 2 = refused before any call.

## 3. Quote the chosen request

```bash
uv run python $P/pilot_pull.py --quote --root QM --first-trade-date D --out $P/runs/quote_QM.json
```

This makes one free quote, ledgered on acct-3 under session `stage-E.28-pilot`. The buy uses
this quote, so quote again whenever anything changes. It warns when `D` is later than 2024-01-12
(the buy would refuse). The balance check comes next: the user reads the balance B on the
Databento portal. The rule (RS-08): APPROVED = the fresh quote, exactly; nothing is bought if the
quote exceeds TARGET = B - max(3.00, 0.03 x B) (rounded down to the cent).

## 4. Buy (detached, with an rc line)

```bash
LOG=$P/runs/buy_QM.log
setsid nohup bash -c "nice -n 10 uv run python $P/pilot_pull.py --buy --root QM \
    --first-trade-date D --balance-usd B --approved-usd APPROVED >> $LOG 2>&1; \
    echo \"rc=\$? \$(TZ=America/Vancouver date '+%F %T %Z')\" >> $LOG" > /dev/null 2>&1 &
tail -n 5 $LOG; grep '^rc=' $LOG            # check later; rc=0 done, 1 stopped, 2 refused
```

The buy makes no new quote. After the request refusals of step 1 (QM only, end pinned), and
before reading the ledger, it refuses a start later than `2024-01-11T22:00:00Z` (the minimum
span, RS-07). It then refuses if the ledger already holds a commit on acct-3 for any other
request: one purchase only, no second contract and no second buy (RD-01); rerunning the same
request is the resume below, not a second buy. It authorizes against the session's newest
quote and refuses that quote if it is for another request, failed, is more than
`--max-quote-age-hours` old (default 24), already has a commit after it, exceeds TARGET for
`--balance-usd` (RS-08: nothing is bought), exceeds `--approved-usd`, or is not what
`--approved-usd` approves (the approval is for exactly the fresh quote: quote <= APPROVED <
quote + 0.01). The spend gate then refuses anything past the session cap (`--session-cap-usd`,
default and maximum 125.00) or acct-3's cap (125.00 committed in total). If those pass, the buy
commits, makes one `get_range` call to `<target>.partial`, links it to the target (an existing
file is never replaced), sets the file read-only, runs the record-byte check, settles, and writes
`runs/purchase_QM_<start>_<end>.json` (sha256, bytes, billing) and
`runs/condition_GLBX.MDP3_<start>_<end>.json` (the free condition list; best effort). Billing more
than 3% above the quote is settled pro rata, recorded, and gives rc 1.

Resume. First check `pgrep -f pilot_pull.py`, the last `commit`/`settle` ledger lines for the
request (`grep stage-E.28-pilot ledger/databento_spend.jsonl | tail -3`), the target, and any
`.partial`. Then rerun the identical command:
- target and settle line both present: "already bought", rc 0, nothing is called;
- target present with an open commit (the run died after the download): it is settled without a
  second download;
- open commit with no file (the download was cut short and may have been billed): refused,
  rc 2. The lead decides. To buy again, run `--quote` again and add `--retry-download`; the
  orphan commit still counts against the caps (pessimistic);
- a file with no ledger line, a settle with no file, or another file in the folder that overlaps
  the range: refused, rc 2. Nothing is deleted.

## 5. Verify (detached for a large file)

```bash
DBN=/mnt/large-storage/market_data/PropExperiment/data/vendor/databento/GLBX.MDP3/mbp-1/QM_v_0/range=<start>_2024-02-29T220000Z.dbn.zst
LOG=$P/runs/verify_QM.log
setsid nohup bash -c "nice -n 10 uv run python $P/verify.py --root QM --dbn $DBN \
    --out $P/runs/manifest_QM.json --tick 0.025 --purchase-record $P/runs/purchase_QM_<start>_<end>.json \
    >> $LOG 2>&1; echo \"rc=\$? \$(TZ=America/Vancouver date '+%F %T %Z')\" >> $LOG" > /dev/null 2>&1 &
```

`--purchase-record` is required (RD-03): without it, or with a record that holds no sha256,
nothing is opened (rc 2). Every `--dbn` file gets its own hard check
`sha256_matches_purchase_record`; one purchase is one file, so two or more files cannot all
match and the run exits 1. This writes `manifest_QM.json` and `manifest_QM.md`. Exit codes:
- 0: every check passed;
- 1: a hard check failed: the header is not the pilot request; a record with ts_event at or after
  `2024-02-29T23:00:00Z` (the 17:00 CT open of trade date 2024-03-01; records in
  [22:00Z, 23:00Z), the maintenance hour, are counted as info only, RS-01); instrument ids missing
  from the symbology; ts_recv order; a file's sha256 differs from the purchase record; off-tick
  prices;
- 3: only the data-quality check failed (a MAIN gap above 60 s on some date that is not
  otherwise excluded; measure.py excludes those dates, as spec section 2 says);
- 2: the file was refused unopened, or `--purchase-record` is missing or holds no sha256.

The manifest also gives trade counts by aggressor side (A/B/N) per date (RS-03). It holds no
resumable state: rerun it.

"ACCOUNT_3 SAFE TO WIPE" (RS-09, spec section 6). The lead writes this line to the STATE file only
after verify.py exited 0, or 3 for data-quality findings only. Since RD-03 verify.py cannot run
without the purchase record and a sha256 mismatch is a hard failure (exit 1), so exit 0 or 3
implies the manifest's `sha256_matches_purchase_record` passed for every file. Never after exit 1
or 2.

## 6. Measure (detached)

The command for this pilot (frozen spec section 0):

```bash
DBN=/mnt/large-storage/market_data/PropExperiment/data/vendor/databento/GLBX.MDP3/mbp-1/QM_v_0/range=<start>_2024-02-29T220000Z.dbn.zst
OUT=$P/runs/measure_QM; LOG=$P/runs/measure_QM.log
setsid nohup bash -c "uv run python $P/measure.py --root QM --tick 0.025 --fee-side 0.1368 \
    --fee-side-alt 0.296 --sim-rule trade_through_only --dbn $DBN --out-dir $OUT --workers 2 \
    --label Topstep >> $LOG 2>&1; \
    echo \"rc=\$? \$(TZ=America/Vancouver date '+%F %T %Z')\" >> $LOG" > /dev/null 2>&1 &
```

measure.py sets nice 10 itself.

Phase 1 runs 1 to 4 worker processes (`--workers`, capped at 4, and cut further if the estimated
peak of about 1 GB per worker exceeds 70% of MemAvailable). Each worker streams the file once
and measures only its own trade dates, one at a time, into `$OUT/days/<date>.json`. Each worker
logs its peak RSS. Every rule is computed for every date, so a different `--sim-rule` needs only
`--aggregate-only`. Every purchased trade date is measured; phase 2 applies the exclusions of
spec section 2 and writes `$OUT/results.json` and `$OUT/results.md`: one table per cell (T/I x
MAIN/OVERNIGHT), pooled/buy/sell columns, for the spec rule and `trade_through_only`. Net
markouts and VPO are given at FEE_SIDE 0.1368 and, on their own rows (`... at fee 0.296
tick/side`; JSON keys `mean_net_alt`, `vpo_alt`, `vpo_nodrop_alt` under `"0.296"`), at the
conservative 0.296.

Resume: rerun the identical command. Dates already on disk with the same fingerprint are skipped.
If the parameters, the code version or the input file change, the run is refused (rc 2): use a
new `--out-dir`. Day files are never overwritten. The fees enter phase 2 only (they are not in
the fingerprint), so `--aggregate-only` can re-score the same day files; it rewrites
`results.json` and `results.md` in that `--out-dir`, so copy them first to keep both. Re-score
under another sim rule: `... --sim-rule touch --aggregate-only`. Exit codes: 0 done; 1 a worker
failed (finished dates are kept) or aggregation stopped; 2 refused before work started (a file
outside the pilot range, a wrong header, or a fingerprint mismatch).

End with `uv run python -m data.holdout status` again and record `unlocks_logged`.

## Conventions the code fixes (where the spec leaves a choice)

These are listed in the coder's return to the lead. The spec itself is unchanged.
1. Record order: each segment is stably sorted by ts_recv, then sequence (this is the file
   order). Sequence and ts_event inversions are counted. The time axis is ts_event, made
   non-decreasing by a running maximum, and the adjusted records are counted (spec section 2).
2. Grouping: a record belongs to trade date D when ts_recv is in [D-1 16:00 CT, D 16:00 CT). The
   pre-open hour seeds the book; the trade date itself is the calendar's open time from 17:00 CT.
3. Sessions: MAIN = 06:30-13:00 PT intersected with the group calendar's open intervals.
   OVERNIGHT = the rest of the open time. "Each session" means each contiguous piece: the first
   and last 5 minutes of every piece get no placements (grid g with lo + 5 min <= g < hi - 5 min).
   On a regular QM trade date this gives 76 MAIN grid times (152 placements per type).
4. Price and Q_ahead both come from the book state at j (the last record at or before j). Book
   validity is checked at j only, not at g. The share of placements whose best price on their
   side at g differs from that at j is reported per cell ("stale share", RS-06).
5. Life window (j, c) with c = min(j + 60 s + 50 ms, the end of the session piece) (RS-13; under
   the spec grid the clip never binds): a trade at exactly j is part of the join state; a trade
   at exactly c does not fill.
6. KM: time from j, censored at 60 s, so fills in the 50 ms cancel latency count in the fill rate
   but are censored in the KM curve (counted separately).
7. The touch rate uses the same life window. A trade at or through the price (any aggressor), or
   any defined opposite quote at or through it, counts (crossed and locked states included).
8. Trades with no aggressor ('N') never add to V(t) and never trigger a fill under any rule,
   including the through clause (spec sections 2 and 3, RS-04). Fills are reported by trigger
   (queue or through) and by the trigger trade's aggressor side; per-date trade counts by side
   (A/B/N) are in the day summaries and the manifest (RS-03).
9. Headline markouts are dropped when t_f + h is at or after the end of the fill's session piece,
   or when any book state over [t_f, t_f + h] is crossed, locked or empty; the dropped share is
   reported per cell. Beside them, the no-drop variant takes the mid of the last valid state at
   or before t_f + h, dropping only when no valid state is active at any moment after t_f up to
   t_f + h, or at a session end, which the spec grid never reaches (RS-05); it has its own net
   mean and VPO.
10. Exclusions: every holiday-calendar entry (full closure, early halt or early close), and
    scheduled late opens. A roll day is a trade date whose symbology (or records) shows two
    instruments, or whose first instrument differs from the previous trade date's last one; it
    and the next trade date are excluded (generic: QM's monthly rolls are found the same way).
    The MAIN gap includes the gaps from the piece edges to the first and last record.
11. VPO = 0 where a cell has placements but no fill (NaN with no placements).
12. Bootstrap: one draw matrix shared by every cell, side, rule and fee; percentile intervals; no
    interval for medians.
