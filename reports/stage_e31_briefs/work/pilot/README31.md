# Stage E.31 Part 3: ZM pilot purchase and verification code

Written by PullCoder-OpusXHigh, 2026-10-22 (from 08:15 PDT). Synthetic tests only: no Databento
call of any kind was made while this was written, no API key was read, and nothing under
`data/` was edited. Spec: `reports/stage_e31_pilot_spec.md` sections 0, 1, 2, 9 and 10.
Adapted from E.28's `reports/stage_e28_briefs/work/B_pilot/` (pilot_pull.py, pilot_common.py,
verify.py, README sections 2-5), which stay unchanged.

| file | what it does |
|---|---|
| `pilot31_common.py` | constants, the four series, month bounds, request guards, TARGET, ledger checks |
| `pull31.py` | `--plan`, `--span-search`, `--quote`, `--buy`, `--retry-download` (SpendGate / RequestCappedGate on acct-3) |
| `verify31.py` | per-file checks of every purchased file; `runs/manifest31.json` and `manifest.json` beside the data |
| `canary_check31.py` | the canary's structure check (spec v2 section 9): `runs/canary31.json`, `runs/canary31.md` |
| `tests/test_pull31.py` | fake Databento client, tmp ledger and folders, synthetic DBN files |
| `tests/test_canary31.py` | canary_check31.py on synthetic Z1, Z2, Z3 and Z4 files |

Pass-1 fixes (FixCoder-OpusXHigh, 2026-10-23, SpecReviewer pass 1 items 4, 5 and 12 and the
spec v2 section 9 canary): `--retry-download`, the buy lock, verify31's record-byte, billable,
snapshot and last-session checks, and canary_check31.py. Sections 4, 4b, 5 and 6 below.

`vol_pull.py` and `vol_measure.py` in this folder are Part 1's and are not used here. SimCoder's
book, matching and measurement files (`mbo_book*`, `kalgo*`, `measure31*`) are not part of this.

## The requests (spec sections 0 and 1)

Four series, GLBX.MDP3, one request per series per month, so 4k requests for k months:

| series | schema | symbols | stype_in | folder under `VENDOR_ROOT/GLBX.MDP3/<schema>/` |
|---|---|---|---|---|
| Z1 | mbo | ZM.v.0, ZM.v.1 | continuous | `Z1_ZM_v_0-ZM_v_1` |
| Z2 | mbp-1 | ZS.v.0 | continuous | `Z2_ZS_v_0` |
| Z3 | mbp-1 | ZL.v.0 | continuous | `Z3_ZL_v_0` |
| Z4 | definition | ZM.FUT, ZS.FUT, ZL.FUT | parent | `Z4_ZM_FUT-ZS_FUT-ZL_FUT` |

The file name is `range=<start>_<end>.dbn.zst` with colon-free bounds, for example
`VENDOR_ROOT/GLBX.MDP3/mbo/Z1_ZM_v_0-ZM_v_1/range=2024-01-31T220000Z_2024-02-29T220000Z.dbn.zst`.
`VENDOR_ROOT` is `data.config.VENDOR_ROOT` (`data/vendor/databento`, a symlink to
`/mnt/large-storage/market_data/PropExperiment/data/vendor/databento`).

Month m's request runs from 16:00 America/Chicago on the last calendar day of the month before m
to 16:00 America/Chicago on m's last calendar day, in UTC: 21:00Z under CDT, 22:00Z under CST
(for example 2023-10: `2023-09-30T21:00:00Z`..`2023-10-31T21:00:00Z`; 2023-11:
`2023-10-31T21:00:00Z`..`2023-11-30T22:00:00Z`). The last month is 2024-02, whose end is exactly
`2024-02-29T22:00:00Z`. The earliest month is 2019-06, because the grains calendar covers trade
dates from 2019-05-01, so k <= 57.

Every mode refuses, before the key is read and before any vendor call (exit 2): an account other
than acct-3; a request that is not exactly one of the four series (another dataset, root,
schema, symbol set or order, or stype); a window other than the month rule's (including any end
other than the month's 16:00 CT bound); a month after 2024-02 or before 2019-06; any overlap with
the embargo and holdout 2, the research window, holdout 1 or a sealed range; a minute the grains
calendar books to a holdout trade date (`data.trade_date_guard`). The allowed roots are the
literal set {ZM, ZS, ZL}, independent of the series table.

TARGET = (125.00 - acct-3's committed USD outside this pilot's two sessions) - 2.00, rounded
down to the cent and never above the spec's 122.27. With today's ledger (Part 1 committed
0.72502180934 under `stage-E.31-2026-10-22-volume`) it is 122.27.

## Run from the repo root

```bash
cd /home/kiros-li/Documents/GitHub/PropExperiment
P=reports/stage_e31_briefs/work/pilot
uv run python -m data.holdout status          # record unlocks_logged (CLAUDE.md)
uv run pytest -q -p no:cacheprovider $P/tests/test_pull31.py $P/tests/test_canary31.py   # never the repo suite
```

Operations (SpecReviewer pass 1 item 12). Run `--buy`, `--retry-download`, `verify31.py` and
`canary_check31.py` with nothing heavy running beside them, outside the AiTrader collector window
(about 15:30-16:00 PT on weekdays; verify31 decodes every record at nice 10), detached with
`setsid nohup` and an `rc=` line in the log, as in sections 4 to 6. `--buy` and
`--retry-download` hold `runs/.buy31.lock` (flock) for the whole run: a second one is refused at
once (exit 2) before the ledger is read, and the refusal names the holder (pid, mode, start).
The lock file is never deleted; a dead holder's lock is released by the kernel.

Exit codes of `pull31.py`: 0 done; 1 stopped after vendor calls began, or the plan says buy
nothing; 2 refused before any vendor call (nothing called, the key not read).

### 1. Plan (no call of any kind)

```bash
uv run python $P/pull31.py --plan --months K [--out $P/runs/plan31.json]
```

This prints the 4K requests in buy order, each target file, TARGET with its derivation, acct-3's
ledger position (committed, cap 125.00, headroom) and any acct-3 commit that would make `--buy`
refuse. K must be 1..57.

### 2. Span search (free quotes only, never buys)

```bash
uv run python $P/pull31.py --span-search
```

The search makes free ledgered quotes under session `stage-E.31-2026-10-22-pilot-span` (cap
0.00), covering the 4 requests of each month from 2024-02 backwards. It stops at the first month
whose addition makes the cumulative sum exceed TARGET, and k is the number of months before that
one. If every month down to 2019-06 fits, then k = 57 and `limited_by_lower_bound` is true. The
search writes `runs/span31.json` with every quote (request, USD, billable bytes, ledger time),
each month's sum and running total, k, the months, `first_month_over_target` and `buy`. If k >= 2
it also writes the free condition list for those months, `runs/condition31_<first>_<last>.json`
(best effort). The client's `timeseries` and `batch` are raising guards. Exit 0: k >= 2. Exit 1:
k < 2 (buy nothing), or a quote failed, in which case `complete` is false and k is null.

### 3. Quote the chosen K

```bash
uv run python $P/pull31.py --quote --months K
```

This makes fresh free quotes of all 4K requests under session `stage-E.31-2026-10-22-pilot`.
They go to `runs/quote31.json` with each quote's ledger time and the sum (`sum_usd`), together
with `complete` and `within_target`. `timeseries` and `batch` are guarded. Exit 0 means every
quote succeeded and sum <= TARGET. Exit 1 means a quote failed or sum > TARGET, and then `--buy`
will refuse. The command warns when K differs from span31.json's k, and when acct-3 holds a
commit that `--buy` would refuse. APPROVED is the quoted sum: the buy needs
sum <= APPROVED < sum + 0.01.

### 4. Buy (detached, with an rc line)

```bash
LOG=$P/runs/buy31.log
setsid nohup bash -c "nice -n 10 uv run python $P/pull31.py --buy --months K \
    --approved-usd APPROVED >> $LOG 2>&1; \
    echo \"rc=\$? \$(TZ=America/Vancouver date '+%F %T %Z')\" >> $LOG" > /dev/null 2>&1 &
tail -n 5 $LOG; grep '^rc=' $LOG            # check later; rc=0 done, 1 stopped, 2 refused
```

Before the key is read, the buy refuses (exit 2) on any of these:
- the request guards above;
- `runs/quote31.json` missing, incomplete, for another K or another set of requests, or from
  another session or account;
- any of its quotes failed, is more than 24 h old, or has no identical quote line in the ledger
  (same time, request, USD and billable bytes);
- its sum > TARGET, or the sum and `--approved-usd` X break sum <= X < sum + 0.01;
- acct-3's ledger holds a commit for any request other than Part 1's volume request (session
  `stage-E.31-2026-10-22-volume`) and this plan's requests in the pilot session;
- a resume state on the list below that the buy refuses.

The session cap is TARGET, and the SpendGate account cap is 125.00 on acct-3.

Order: Z1 latest month first, then the earlier Z1 months, then Z2, Z3 and Z4 in the same month
order. Each request goes through these steps:
1. A fresh ledgered re-quote. If it is more than 1% above the request's quote31 value, the run
   stops with exit 1 and nothing is committed.
2. `authorize` through `data.pull_mes.RequestCappedGate`, with a request cap of quote31 x 1.01,
   the session cap and the acct-3 cap. A refusal is ledgered and the run stops (exit 1).
3. `commit` the re-quote.
4. One `timeseries.get_range` to `<target>.partial`, then a link to the target (never replaced),
   then the file is set read-only (`data.pull_universe.download`).
5. The record-byte check (`data.adapter.delivered_record_bytes`).
6. `settle`. Delivery above the billable bytes is settled pro rata. More than 3% above stops the
   remaining buys (exit 1).
7. `runs/purchase31_<series>_<month>.json`, holding the bytes, sha256, quote31 value, quote,
   settle and position.

After the last request, the free condition list is fetched if it is not on disk (best effort).

Resume. First check `pgrep -f pull31.py`, the last ledger lines of the session
(`grep '"stage-E.31-2026-10-22-pilot"' ledger/databento_spend.jsonl | tail -3`), the target folders
and any `.partial`. Then rerun the identical command. For each request:
- the file exists and its last ledger line is a settle: skipped. A missing purchase record is
  rebuilt from the ledger (no call). If every request is settled, the run exits 0 without reading
  the key or quote31.json;
- the file exists with an open commit (the run died after the download): settled without a
  second download;
- an open commit with no file (the download was cut short and may have been billed): refused,
  exit 2, naming the recovery (section 4b). Everything else in `--buy` keeps refusing it;
- a request retried by `--retry-download` resumes from its retry-session lines: settled with a
  file, skipped; an open retry commit with a file, settled in the retry session without a new
  download; an open retry commit with no file (a second failure), refused, exit 2;
- a stray `.partial`, a file with no ledger line, a settle with no file, or another file in the
  folder that overlaps the range: refused, exit 2.

Nothing is deleted except a run's own `.partial` when its download fails. If quote31.json is more
than 24 h old on a resume, run `--quote --months K` again: it re-quotes all 4K requests, including
the settled ones (free), and APPROVED is the new sum. Real spend is still bounded by the session
cap TARGET.

### 4b. Retry one failed download (lead only; spec v2 section 9, item 4)

When a download fails after its commit (`--buy` stopped with exit 1, then refuses the request's
open commit with exit 2):

```bash
LOG=$P/runs/retry31.log
setsid nohup bash -c "nice -n 10 uv run python $P/pull31.py --retry-download --series Z1 \
    --month 2024-02 >> $LOG 2>&1; \
    echo \"rc=\$? \$(TZ=America/Vancouver date '+%F %T %Z')\" >> $LOG" > /dev/null 2>&1 &
```

It is allowed only when that request has an open commit in the pilot session, no target file,
no `.partial`, no overlapping file in its folder, and no earlier retry commit (at most one retry
per request), and when acct-3 holds no commit outside the pilot's requests. Otherwise it is
refused (exit 2) before the key is read. The failed commit stays in the ledger, open and counted
as spent. Steps:
1. A fresh ledgered quote, in session `stage-E.31-2026-10-22-pilot-retry`.
2. Refused (exit 1, nothing committed) when the quote is more than 1% above the failed commit's.
3. `authorize` with the retry session's cap, 125.00 - acct-3 committed so far (every acct-3
   line, the failed commit included), the request cap (the failed commit's quote x 1.01) and
   the acct-3 cap 125.00. A refusal is ledgered (exit 1).
4. commit, download (`.partial`, link, read-only), record-byte check, settle (the 3% rule as in
   `--buy`), and `runs/purchase31_<series>_<month>.json` with `session_id` = the retry session
   and `retry_of_commit` = the failed commit.
5. A failed retry download stops (exit 1): a second failure. The purchases stop and the return
   reports the gap; a second `--retry-download` of the same request is refused, and `--buy`
   refuses the request (exit 2).

After a successful retry, rerun the `--buy` command (with a fresh `--quote` if quote31.json is
more than 24 h old) for the rest. The retry session is one of the pilot's sessions for TARGET,
so a retry does not lower TARGET: it is paid from the 2.00 USD margin, and acct-3's 125.00 cap
bounds the total.

### 5. Verify (detached for large files)

```bash
LOG=$P/runs/verify31.log
setsid nohup bash -c "nice -n 10 uv run python $P/verify31.py --months K >> $LOG 2>&1; \
    echo \"rc=\$? \$(TZ=America/Vancouver date '+%F %T %Z')\" >> $LOG" > /dev/null 2>&1 &
```

`--no-side-manifests` writes `runs/manifest31.json` only (nothing beside the data under
`data/`), for a read-only check run.

The script verifies every request of the K-month plan that has a purchase record. A planned
request with no record is a hard failure unless `--allow-missing` is given, which reports it as
info, for a partial buy. Records are streamed in chunks (`--chunk-records`, default 1,000,000)
at nice 10. It writes `runs/manifest31.json` and copies it as `manifest.json` into every series
folder that holds a verified file. Per file the manifest gives the bytes, the sha256, the header
(dataset, schema, stype_in and stype_out, symbols, partial, not_found, start, end, mappings), the
record counts by rtype, by instrument_id and by both, and the ts_event and ts_recv minimum and
maximum.

Checks and exit codes (0 every check passed; 3 data-quality findings only, listed in the
manifest; 2 a hard failure, or nothing could be verified):
- hard:
  - the purchase record is this request at this target;
  - the file exists;
  - bytes and sha256 equal the purchase record;
  - the metadata is the request: dataset, schema, stype_in, symbols, start and end; every symbol
    has a mapping and `not_found` is empty;
  - the file holds at least one record;
  - no record with ts_event or ts_recv at or after the request end;
  - no record at or after `2024-03-01T00:00:00Z`;
  - every planned request was purchased (without `--allow-missing`);
  - `record_bytes_match_purchase_record` (item 5): the decoded record bytes == records x the
    DBN v3 record size (mbo 56, mbp-1 80, definition 520) == the records' own length fields x 4
    == the purchase record's `settled.delivered_record_bytes`, and the file is DBN v3;
  - `delivered_bytes_equal_quoted_billable` when delivered < the quote's `billable_bytes`;
- quality:
  - the file is read-only;
  - `partial` is empty; for a parent request (Z4), CME combo children (names with ":", such as
    `ZM:BF K5-N5-Q5`) that are listed partway through the window are listed as info;
  - no record whose ts_recv is before the request start. Databento selects records by ts_recv,
    so a ts_event before the start with ts_recv inside (a snapshot's resting orders, an older
    definition) is expected and counted as info (`ts_event_before_request_start_counted`);
  - only the schema's record type (mbo 160, mbp-1 1, definition 19);
  - every record's instrument_id is in the mappings;
  - ts_recv is non-decreasing in file order;
  - `delivered_bytes_equal_quoted_billable` when delivered > billable (any difference is listed
    with its sign; below is hard, above is quality);
  - Z1 `z1_weekday_midnight_snapshot_per_mapped_instrument`: every UTC weekday 00:00Z inside the
    request has an R record flagged F_SNAPSHOT (ts_recv within 60 s after the midnight) for each
    instrument the metadata maps on that UTC date (start_date inclusive, end_date exclusive);
    the missing cells are listed;
  - Z1, Z2, Z3 `ts_event_max_reaches_last_day_session`: ts_event max >= the end of the DAY
    session of the month's last grains trade date (13:20 CT unless an early halt;
    data.calendars.grains through data.group_session) less 60 s;
- info: ts_event inversions in file order (counted; spec section 2).

measure31.py refuses a manifest with any failed hard check, so a file delivered below its
billable bytes stops the measurement until the lead rules on it.

### 6. Canary check (structure only; spec v2 section 9)

```bash
LOG=$P/runs/canary31.log
setsid nohup bash -c "nice -n 10 uv run python $P/canary_check31.py >> $LOG 2>&1; \
    echo \"rc=\$? \$(TZ=America/Vancouver date '+%F %T %Z')\" >> $LOG" > /dev/null 2>&1 &
```

Default months 2024-01 and 2024-02 (`--month YYYY-MM`, repeatable). It reads the purchased files
and writes `runs/canary31.json` (full tables) and `runs/canary31.md`. Exit 0: the structure holds;
3: findings (listed in both); 2: refused, nothing opened (a month outside the plan, a missing
file). It never reads a price field of an MBO or MBP-1 record and computes no fill, markout,
spread statistic or price summary. Per month:
- Z4: the ZM, ZS and ZL outrights' (instrument_class F) match_algorithm, min_price_increment,
  min_price_increment_amount and unit_of_measure_qty. Findings: a match algorithm other than K;
  ZM's tick not 0.10; more than one tick for a root; tick x the contract size (100, 5,000,
  60,000) neither 10.00, 12.50, 6.00 (prices in USD) nor 1000, 1250, 600 (prices in US cents);
  a stated contract quantity that disagrees. min_price_increment_amount is a note only (the real
  files give 1.0, 1.0, 0.06; the engine uses min_price_increment x unit_of_measure_qty).
- Z1: the v.0/v.1 mapping per UTC date (instrument_id and raw symbol from Z4); the snapshot
  table (weekday midnight x mapped instrument: the clear, its A records, F_LAST); T and F counts;
  per instrument in file order, each T opens a group that the F records right after it join
  (any other action closes it). Findings: a missing snapshot cell, a T with no F, F sizes
  summing above their T's size, F records that follow no T. Info only: T runs (consecutive T
  records and the F records right after them; F sum equal, twice, below or above the run's T
  sum), to read the per-T findings against.
- Z2, Z3: records per grains trade date (in session; before the session they are booked to),
  by data.group_session.assign_trade_dates. Finding: a trade date with no in-session record.

"ACCOUNT_3 SAFE TO WIPE" (spec section 9) is the lead's line in the STATE file. The lead writes it
only after the last purchase is verified: verify31.py exit 0, or exit 3 with findings only and no
`--allow-missing`. It is never written after exit 1 or 2.

## Conventions the code fixes (where the brief or spec leaves a choice)

- TARGET is the brief's ledger rule, capped at the spec's fixed 122.27, so the lower of the two
  applies if the ledger ever disagrees.
- The span search quotes all 4 requests of a month, even after the cumulative sum has already
  passed TARGET partway through that month. It records them and then stops.
- The re-quote, not the quote31 value, is what gets committed and settled. The 1% tolerance and
  the request cap compare the re-quote with its quote31 value.
- Delivery 0-3% above the billable bytes is settled pro rata and the run continues. Above 3% it
  is settled pro rata and the run stops (as in E.28 and data.pull_hist).
- The condition list's date range is the first request's UTC start date to 2024-02-29, so no date
  on or after 2024-03-01 is asked for.
- In verify31.py, a record before the request start is a quality finding, because MBO snapshots
  and definitions may carry an older ts_event and this is no leakage risk. A record at or after
  the end is a hard failure.
- Retry: the retry session's cap is the brief's 125.00 - acct-3 committed so far, read when the
  retry starts. An earlier retry of another request is in both that sum and the retry session's
  own spend, so it is counted twice, which only tightens the cap. The retry's request cap is the
  failed commit's quote x 1.01 (the buy's 1% rule, against the failed commit).
- A rebuilt purchase record takes `delivered_record_bytes` from its settle note (the wording
  `settle_download` writes), so verify31's byte check applies to it too.
- Snapshot window 60 s after 00:00Z (the docs give ts_recv = the generation time, 00:00:00Z;
  research/data_facts.md a1) and last-session tolerance 60 s are this code's choices.
