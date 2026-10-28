# DataCoder readings (Stage E.33, pipeline A data layer)

Each entry: the protocol or brief line, the readings considered, the choice, why it is the
conservative one. Code marks: `# READING <id>` or the id in the docstring. The lead decides each
before the freeze.

## Guard (guard33.py)

**DG-1 Record-level date bounds.** P1.2: "any ZM, ZS or ZL data dated 2017-05-01..2020-11-30
... anything dated on or after 2024-03-01". Readings: (a) bound records by ts_recv only; (b) bound
by ts_recv and ts_event on both sides. Choice: ts_recv must lie in [2020-11-30T22:00Z,
2024-03-01T00:00Z) (the seal manifest's window_utc ends at 2020-11-30T22:00Z = 16:00 CT, the start of
trade date 2020-12-01's window); ts_event must be < 2024-03-01T00:00Z (as E.31's guard_chunk). The
lower bound does not use ts_event, because the 1,157 Z1 snapshot records whose ts_event precedes
2020-12-01 (E.32 data facts 1.5) carry the resting order's original entry time, while their ts_recv
is the owned capture time; refusing them would delete resting orders from the first book. Why
conservative: the seal is defined on the same UTC window, so no sealed instant is admitted;
ts_event adds the stricter test on the upper side.

**DG-2 Dates outside the discovery span.** P1.2 refuses the test window and dates on or after
2024-03-01. Readings: (a) allow other dates before 2017-05-01; (b) refuse every trade date
outside 2020-12-01..2024-02-29. Choice (b): `check_date` refuses a date before 2020-12-01 even
outside the test window ("outside the discovery span"). Why: no allowed file holds such a date, so
(b) refuses nothing E.33 may read and closes any path to other data.

**DG-3 Allowlist.** Brief deliverable 1 names the 156 files, E.31's derived/e31/Z1 store and the
E.33 DERIVED tree. Choice: `check_path` is a strict allowlist: those, plus the four identical
manifest.json copies and their four folders (metadata), plus the two P3.6 release calendars
(P1.2 (c); `check_reference` also pins their protocol sha256). E.31's derived/e31/Z2 and Z3
stores are refused although they come from the discovery files (the brief does not list them;
E.33 has its own ZS/ZL split). Code under reports/ is not market data and is not read through
the guard (imports of the E.31 library, the program calendars).

**DG-4 Dates read from names.** Brief: "by any date span readable from a file name". Choice:
every component of both spellings of the path (folders too) is parsed: Databento
`range=<start>_<end>` stamps as UTC instants, end exclusive, compared with the seal's UTC window
(so the first discovery file, range=2020-11-30T220000Z_..., passes: its start equals the window's
end); `<date>_<date>` spans end inclusive; single YYYY-MM-DD tokens as trade dates (check_date);
YYYY-MM tokens as whole calendar months. Why conservative: a folder named for a sealed date, or a
month token, is refused too.

**DG-5 derived_unsealed_files.tsv.** P1.2: "any file listed in ...". Choice: refuse a listed
path in either spelling (relative entries are taken from the repo root) and also any folder that
holds a listed file (a directory read would reach it).

## Loaders (data33.py) and split (split33.py)

**DATA-1 Ordering (P0.3, LT4).** Brief: "If files are not in ts_recv order, the loader returns a
stable ts_recv sort and says so." Measured: 0 ts_recv decreases in file order on the 3 check
dates in Z1, Z2 and Z3 (feed level and per instrument), 0 in each of the 39 Z4 files and across
their concatenation, 0 in the whole Z2/Z3 split (split33 stops on any decrease) and 0 over the
whole Z1 series (check33 e31-all: 39 files, all 816 dates). Choice: every loader still counts decreases
on each array it returns; if any appear it returns a stable ts_recv sort and logs the count in
`data33.ORDER_LOG`. Records with ts_recv < ts_event keep their ts_recv position.

**DATA-2 Month-file boundaries in the split.** P0.3 window [D-1 16:00 CT, D 16:00 CT). The
monthly files end at 22:00 UTC, which is 17:00 CDT in summer, so the 16:00-17:00 CDT hour of the
last calendar day belongs to the next month's first trade date. E.31's split_file keeps only
trade dates of the file's month and would drop such records. Choice: split33 takes them from both
files. Measured: no ZS or ZL date drew records from two files (0 DONE markers with two source
months), so the choice changed nothing. For ZM, check33 e31-all found E.31's store equal to an
independent raw count on all 816 dates, so E.31's boundary rule dropped no ZM record either.

**DATA-3 Records outside trade-date windows** (weekend and full-closure windows) are counted and
not stored: ZS 1,373, ZL 2,438 records (split_manifest.json last_run).

**DATA-4 Field types.** action and side are stored as uint8 ASCII codes (as E.31's
MBO_COMPACT and mbo_book31.ACT_* / SIDE_*), ts_recv and ts_event as int64; every other MBP-1
field keeps its source type; the length byte is dropped. Prices stay int64 1e-9 units.

**DATA-5 Definitions.** Brief: "all Z4 definition records in ts_recv order". Choice:
`definitions()` returns all 1,810,372 records (outrights and spreads) by default;
`outright_only=True` returns the 70,131 ZM/ZS/ZL outright-future records (instrument_class F, 148
ids). Kept fields: data33.DEF_FIELDS (source types; expiration/activation uint64 with
UNDEF_TIMESTAMP kept). The cache (DERIVED/split/Z4) is built once from the 39 raw files.

**DATA-6 Loader integrity checks.** load_zm and load_mbp1 refuse an array whose record count
differs from its marker (E.31 month marker, E.33 DONE marker) or whose ts_recv falls outside D's
window. load_zm also checks each E.31 month marker's sha256 against the discovery manifest.

## Calendar (cal33.py)

**CAL-1 expiry_trade_dates (C.7).** C.7: "trade dates from D to the expiration of the ZM front".
Readings: count (a) T with D < T <= E, (b) D <= T <= E, (c) D <= T < E, E = the CT calendar date of
the front's `expiration` (last definition with ts_recv <= 08:30 CT on D). Choice (a): 0 on the
expiration date, 1 the trade date before. Grains calendar (covers to 2026-06-19) counts dates
after 2024-02-29 (calendar data, not market data). Range over the 816 dates: 10..122; never
undefined. Why: none of the readings leaks; (a) is the usual days-to-expiry count, and the
choice only shifts C.7 by 1/60.

**CAL-2 Exclusion reasons.** P1.4: roll date, trade date after it, early close, scheduled late
open. Choice: `excluded(D)` returns every reason that applies (2 dates carry both roll and
after-roll; 2022-11-25 carries after-roll and early close); counts by reason count a date under
each reason, and the distinct count is given. The excluded set equals measure31.roll_reasons'
(cross-checked in code). calendar_reason gives holiday/early close precedence over late open
(2021-11-26 is both; counted as early close).

**CAL-3 Roll test on 2020-12-01.** roll_reasons compares with the previous grains trade date,
2020-11-30, whose ZM.v.0 mapping comes from the first discovery file's header (its request
starts 2020-11-30T22:00Z, so the mapping interval starts on UTC date 2020-11-30). That is
symbology metadata of an allowed file, not test-window market data. Result: no roll on
2020-12-01 (a burn-in date, so no row or trade depends on it).

**CAL-4 Releases.** Choice: `releases(D)` returns the unique instants (several reports share
11:00 CT). The NOPA rule months are computed over the 39 discovery months and asserted to be
exactly 2022-11 and 2022-12; rule dates 2022-11-15 and 2022-12-15 (both trade dates). One kept
row falls on a non-trade date: 2022-04-15 (Good Friday); it touches no trade date's day session.
The report name is matched exactly (no whitespace stripping), time_et exactly "12:00".

**CAL-5 limits as-of.** P3.6 rule 5: "a single as-of pass over the Z4 files in ts_recv order,
state carried across files and dates". Choice: the as-of lookup runs on the ts_recv-ordered
concatenation of all 39 files filtered to the front's instrument_id (identical to the single pass,
since one instrument's state depends only on its own records); ts_recv ties resolve to the later
record in file order. Result: None on 0 of 816 dates.

**CAL-6 monday_or_after_closure (C.10).** "the first trade date after a full closure": a
weekday full closure lies strictly between the previous grains trade date and D. 173 of 816.

**CAL-7 segment_id (G2).** Segments are numbered from 0 at 2020-12-01 over the 816 dates
(burn-in included); a front change during a non-trading gap starts the new segment on the next
trade date. 54 segments.

**CAL-8 ct_ns.** zoneinfo with fold 0 at an ambiguous wall time (the fall-back hour); no session
time of the protocol falls in that hour.

## G6 report (g6_33.py)

**G6-1 Records used.** P4 G6: "the distribution of ts_recv - ts_event for ZM, ZS and ZL". Choice:
records flagged F_SNAPSHOT or F_BAD_TS_RECV are left out (their ts_recv is the snapshot
generation time, or flagged inaccurate; E.32 data facts 1.4 also uses non-snapshot records).

**G6-2 ZM column.** Choice: the ZM column uses every Z1 record (both ZM ids, the feed); a ZM
front-only median is shown beside it, and a month is flagged if either version's medians differ
from ZS or ZL (or each other) by more than 100 ms.

## Differences from INTERFACE.md or the protocol

None found. One addition: modules beyond the three named (check33.py, split33.py, g6_33.py) are
mine and hold the store checks, the split runner and the G6 report.
