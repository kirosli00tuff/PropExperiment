# FeatureCoder2 (implementation B) readings

Worker: FeatureCoder2-OpusXHigh, Stage E.33 B2, 2026-10-27. Protocol: reports/stage_e32_discovery_protocol.md
(cited by line). Each reading is marked in code with `# READING <id>` or named in a docstring. "Conservative" here
means: no information after t, no imputation of a missing input (the feature is invalid instead), and the literal
protocol text where it is explicit. The lead decides each before the freeze; nothing here changes a declared choice.

## Clock and windows

**B-OPEN-1 (open-axis junction point).** Line 63: "the last k minutes of time during which X was open, ending at t
(the 07:45-08:30 pause and the 13:20-19:00 close are skipped; overnight minutes count). Sample points inside a window
are the minute marks t - j minutes, j = 1..k, on that open-time axis." Readings: the open-axis point shared by 07:45
and 08:30 is sampled (a) as of 07:45:00, the end of the overnight interval, or (b) as of 08:30:00, the open instant
of the day interval. Measured (counts only, 328 dates built for the B3 run): the as-of book at 08:30:00 is invalid
(pre-open, locked or crossed) on 328 of 328 dates for ZM, 328 for ZS and 327 for ZL; at 07:45:00 and 08:35:00 it is
valid. Under (b) every window that reaches back across 08:30 is therefore invalid on every date (first code run:
F1.2 rows 0-115, F1.1 and F1.6 rows 0-25, F1.4 rows 0-30, F4.10-F4.12 rows 0-10, one row each of F2.2, F2.3, F2.5,
F2.6, F2.7, F4.2-F4.5), so C.11 would be 0 for the first 116 minutes of every day. That contradicts P1.3 line 131
("Its records enter features only (windows that reach back across 08:30 ...)"). Choice (a): marks of the axis are
lo_0, then for each interval lo_k + 1 min, ..., hi_k, so the junction point is 07:45:00 (likewise 13:20 for
13:20/19:00 and the halt time for an early close) and no record of the skipped pause enters any sample. Why: (a) is
the reading under which the pause is actually skipped (its records never enter a sample or a window, B-WIN-1) and
P1.3's windows across 08:30 exist; it uses older information than (b), never newer. Marks before 08:35 are 08:34, ...,
08:31, 07:45, 07:44, ...

**B-WIN-1 (what a window sum covers).** Line 63 (same). Readings: a k-minute window sum covers records with ts_recv
in (a) the wall-clock interval (wall(t - k), t] including the pause, or (b) open time only, open-axis position in
(P(t) - k, P(t)]. Choice (b): records stamped inside the 07:45-08:30 pause or after a close are not in any window
(volume, OFI, removals, sweeps, refills, trade counts). An OFI term e_n of the first update after 08:30 is taken
against the last update before it (possibly a pause update). Why conservative: the protocol says the pause is
skipped; no closed-time record enters a window.

**B-EARLY-1 (decision times after an early halt).** Features are computed on every date (P1.4), including early
closes (12:05 halt) where grid times 12:06..13:12 lie in closed time. Choice: P(t) for a closed t is the position of
the close, so the window ending at t is the last k open minutes before the halt; M(t) itself is as of the wall time
t. The trailing references and sigma use the wall-clock marks 08:35-13:13 of every date (see B-SIG-1), so on early
closes they include post-halt marks (stale states). Why: literal "the last k minutes of time during which X was
open, ending at t" and "minute marks 08:35-13:13".

**B-LATE-1 (scheduled late opens).** On a scheduled late open (no overnight session; 8 dates in the universe, e.g.
2021-07-06), the 120-minute look-back from 08:35 reaches the previous trade date's day session. Choice: the open-time
axis runs across trade dates (literal line 63), the previous trade date's records are loaded and replayed with D's
records as one stream (D's fronts), and F1 samples on the previous date count only if that date is in D's segment
(G2). Other families take the previous date's values (scale and non-F1 quantities are not segment-bound by G2).

**B-EARLYIDX (C.9, F4.13 thresholds).** C.9 "1{t >= 11:30}" is i >= 175; F4.13 "1{t >= 12:15}" is i >= 220.

## Book, trades and record-level events (F3)

**B-BOOKBAD (ZM validity).** Line 58: M defined "only when both sides exist, bid_1 < ask_1 and the book is not marked
bad (F_MAYBE_BAD_BOOK)". Choice: E.31's book semantics (mbo_book31 docstring): a record with F_MAYBE_BAD_BOOK (or
F_TOB/F_MBP, as E.31) marks the ZM book bad until the next R; records before the first R are skipped (book not
started, invalid). Why: P0.3 names mbo_book31.Book; this is E.31's own rule.

**B-MBP-BAD (ZS/ZL validity).** MBP-1 has one R record per file series, so "bad until the next R" would void weeks.
Choice: an MBP-1 book update (the state after an F_LAST record) is bad if any record of its event carries
F_MAYBE_BAD_BOOK (E.31's CondSeries flags the record itself; I widen it to the whole event). A side is missing when
its price is UNDEF_PRICE or INT64_MIN; a defined price with size 0 counts as present. Why conservative: the event
that carries the flag is never used; the rest of the day is not voided on a flag that MBP-1 never clears.

**B-SEAS-1 (seasoned depth, F3.7-F3.8).** Line 437: "the displayed quantity at a price level counting only orders
whose last add or modify (by ts_recv) is at least 1.000 s before t." Readings: levels m = 1..3 are (a) the levels of
the displayed book or (b) the levels of the seasoned-only book. Choice (a): the price levels of the full displayed
book, quantities counted over seasoned orders only (a level can have seasoned quantity 0). "Modify" is any M record,
including a size decrease that keeps priority (it resets the order's time); a partial cancel does not. Snapshot adds
carry the snapshot's ts_recv. The state is the one after the last F_LAST record with ts_recv <= t; seasoned means
last add/modify ts_recv <= t - 1.000 s. Invalid (G3) when the ZM book at t is not valid or the denominator is 0.
Why conservative: (a) is the literal "at a price level"; resetting on every modify counts fewer orders as seasoned.

**B-FILL-1 (fills are not removals, F3.9).** Line 446: "contracts removed ... by cancels, size-reducing modifies
(the reduction) and modifies to another price (the full size), in the 5-minute window; fills are not removals".
Databento MBO marks fills with F records and reduces the resting order with a later C or M (E.31 data_facts a2). A
counts-only probe on 2022-02-15 (front 689369): all 17,115 C/M records that followed an F record of the same order
were in the same event (same F_LAST batch) and had the same ts_event. Choice: within an event, F sizes accumulate per
order id; a C/M reduction of that order consumes the accumulated fill first, and only the remainder is a removal;
the accumulator is cleared at each F_LAST. Why conservative: only quantity provably not filled is a removal.

**B-REM-1 (touch removals, F3.9).** "the price level that was the best ask (Ca) or best bid (Cb) just before the
record". Choice: record-level best price of the order's side just before the record (mid-event states allowed, since
the line says "just before the record", not "as of a book update"). Counted: C (the cancelled lots, capped at the
order size), M with a size decrease at the same price (the decrease), M to another price, an M that changes side or
sets size <= 0 (the full old size). Time = the record's ts_recv.

**B-SW-1 (sweeps, F3.10).** Line 447: "a buy sweep is a set of trade records sharing one ts_event that leaves the
best ask level's displayed quantity at 0 (sell sweep: the best bid)". Choices: a run is a maximal sequence of
consecutive front records with one ts_event value; the best bid and ask prices are taken just before the run's
first T record; at every F_LAST record inside the run (an event end, so the check is causal and identical under the
LT1 truncation) the run is a buy sweep if that ask price level has displayed quantity 0, and a sell sweep if that
bid level has 0 (each at most once per run). Time = the ts_recv of that F_LAST record. No condition on the aggressor
side code (the line defines the sweep by its effect on the level). Why: evaluating only at event ends never reads a
half-applied event; the run definition is the literal "sharing one ts_event".

**B-REFILL-1 (refills, F3.11).** Line 448: "a refill is an add at the same price and side within 100 ms (ts_recv)
after that price level, while it was the touch, reached 0 displayed quantity through trades". Choices: a depletion
is a C/M reduction with a fill part (B-FILL-1) on the best level of its side that leaves the level at 0; every later
A record (not an M) with the same side and price and ts_recv - t_depletion <= 100 ms is one refill (each add counts;
the latest depletion of that level is used); a book clear forgets depletions. Time = the add's ts_recv; bid refill =
an add on the bid side. Why: "a refill is an add" counts adds; A records are the only literal adds.

**B-OFI-1 (OFI terms, F2.8-F2.11, F3.1-F3.4): replaced by the lead's ruling FD3 (2026-10-28).** My first version
set a term to 0 unless both states were valid books (P0.3 validity, so crossed or locked states gave 0 terms) and
let the first update after the pause enter the sum. Implemented now (code fb69badd4bb9, dayB.ofi_terms,
ofi_included, OfiWindows; tests test_ofi_terms_known_answer, test_fd3a_*, test_fd3b_*, test_fd3c_* in
tests/test_replayB.py and test_f2_8_fd3b_*, test_f3_1_f3_4_fd3b_* in tests/test_featB.py), in every OFI feature and every level:
- FD3 (a): the term of the first book update after a skipped interval (the 07:45-08:30 pause, the 13:20-19:00 close,
  an early halt; also the stream's first update, which has no predecessor) never enters a window's sum, whatever its
  predecessor; the window sums its remaining terms and stays valid. Rule in code: an update's term is included only
  if the update lies in open time and its predecessor lies in the same open interval.
- FD3 (b): an included term whose state or predecessor lacks a side or is marked bad cannot be computed; a window
  holding such a term makes the OFI invalid (G3: 0 and the family flag 0); no 0 term is imputed. Marked bad: ZM
  started and not bad (B-BOOKBAD), ZS/ZL the event flag (B-MBP-BAD).
- FD3 (c): crossed or locked but two-sided, not-bad states use the literal e_n formula.

**B-OFI-2 (FD3 (b) at levels 2-5, F3.4).** For the level-m OFI, "lacks a side" is read as "has no level m on that
side": a term whose state or predecessor has fewer than m displayed levels on either side cannot be computed, so
the window's OFI^(m)_5 is invalid and F3.4 (which sums m = 1..5) is invalid. Why: the e_n of level m needs the
level-m price and quantity of both sides; using 0 for a missing level would impute a term, which FD3 (b) forbids.

**B-OFI-REF (references of OFI features).** Obar_S_k, Obar_ZM_k (F2.8-F2.11, F3.1-F3.3): the mean of |OFI_k| over
the marks 08:35-13:13 of the 20 previous dates where that window's OFI is computable (FD3 (b)); undefined if none.
Why: an invalid window has no OFI value to average.

**B-VOL-1 (volume and trade counts).** V_ZM counts every ZM T record (aggressor sides A, B and N: "ZM contracts
traded"); TI (F3.5-F3.6) and lam60's signed volume use sides B and A only (side N excluded, line 444). V_ZS and V_ZL
count MBP-1 T records only; the MBP-1 F records (undocumented in MBP-1, data facts 3.2) are not counted.

**B-LAM-1 / B-LAM-2 (lam60, F3.12).** Line 449: "over those of the 60 one-minute intervals ending at t that contain
trades". Choices: an interval contains trades when it has at least one ZM T record of any side (literal "trades");
intervals whose end mids are not both valid are dropped; the slope is the lstsq coefficient on [1, x - mean(x)];
fewer than 30 intervals or rank < 2 (all x equal) is invalid. The reference median is over the valid slopes at the
20 x 279 marks; a median of 0 or no valid slope is invalid.

**B-RP-1 (F4.6).** "Hi and Lo the max and min of M_ZM over [08:30, t] on D". Choice: the valid mid as of 08:30:00
and every valid book update with ts_recv in (08:30, t]. Why: the closed interval starts at 08:30:00, whose state is
the one as of 08:30:00.

## Missing inputs and history

**B-MISS-1 (a sample point without a valid mid).** The protocol states the valid-mids rule only for sigma and F1.3.
Choice: every other window feature that uses sample points (F1.1, F1.2, F1.4, F2.1-F2.7, F4.1-F4.5, F4.10, F4.11,
F4.12) is invalid if any sample point it uses has no valid mid (or, for F1, lies outside D's segment). Why
conservative: no imputation and no shortened window.

**B-C34 (C.3, C.4).** G3 lists "empty book side". Choice: C.3 and C.4 are invalid (0) when the ZM book at t is not
valid (empty side, locked or crossed, bad). C has no flag, so only the value is set to 0.

**B-SIG-1 (sigma_X).** "the SD of 1-minute mid changes ... over all 1-minute intervals inside 08:35-13:13 of the 20
trade dates before D". Choices: wall-clock intervals between consecutive marks 08:35..13:13 of each of the 20
previous universe dates, with valid mids at both ends; null (undefined) when D has fewer than 20 universe dates
before it (the burn-in dates: data before 2020-12-01 is sealed) or no valid interval. sigma <= 0 makes C.6 and every
feature divided by it invalid.

**B-REF-1 (trailing references).** Over the 279 marks 08:35-13:13 of the 20 previous universe dates; undefined (the
feature invalid) with fewer than 20 dates. Vbar (C.5) is the mean of the 20 values at the same minute. Obar_S/L are
undefined if ZS or ZL had no front on any of the 20 dates. **B-DBAR-1:** Dbar_m uses the marks where the ZM book is
valid, a missing level counting 0.

**B-C7.** Line 405: "min(trade dates from D to the expiration of the ZM front ..., 60)/60". Readings: count of trade
dates x with (a) D < x <= E, (b) D <= x <= E, (c) D <= x < E, where E is the trade date holding the expiration
instant ([E-1 16:00 CT, E 16:00 CT)). Choice (a), a difference E - D in trade dates (0 when D = E). Invalid when no
definition of the front has ts_recv <= 08:30 CT on D (and <= the cutoff) or the expiration is undefined.

**B-C10.** Line 408: "1 if D is a Monday or the first trade date after a full closure". Choice: D is a Monday, or a
calendar day strictly between the previous grains trade date and D is a full closure (data.group_session holidays,
kind FULL_CLOSURE); e.g. 2022-01-18 and the Friday after Thanksgiving are 1.

**B-SEG-1 (segments, G2).** Fronts from measure31.instrument_on over the discovery manifest's per-file symbology
headers (ZM.v.0 from Z1, ZS.v.0 from Z2, ZL.v.0 from Z3). A date with an unknown front starts its own segment. 54
segments over the 816 dates.

**B-F13-REL / B-F13-DATES (F1.3).** "1-minute samples (08:35-13:13, minutes clear of P3.6 rule 3) of the 10 trade
dates before D inside the current segment; at least 3 such dates or invalid". Choices: samples are the 279 marks of
each date with all three mids valid; a mark u is excluded when R - 2 min <= u <= R + 30 min (closed) for a release R
on that date; the dates are those among the 10 universe dates before D that lie in D's segment and contribute at
least one sample; at least 3 such dates; rank < 3 (collinear regressors) or residual SD 0 is invalid. e(t) needs
valid mids of all three at t. Natural-unit fit: y = M_ZM (USD/ton), regressors M_ZS (c/bu) and M_ZL (c/lb) centred,
with an intercept; a = mean(y) - b_S mean(M_ZS) - b_L mean(M_ZL); sd = sqrt(SSR/n).

**B-GAP-1 (F1.7, F4.7).** F4.7 line 456: "sd_gap = the SD of the same quantity over the 20 trade dates before D on
which the ZM front was the same at both times (at least 10, or invalid)". Readings: (a) of the 20 trade dates before
D, those that qualify (>= 10 needed); (b) the 20 most recent qualifying dates, searching further back. Choice (a),
matching "(at least 10, or invalid)". D's own GAP is invalid when the ZM front on the previous trade date differs.
F1.7 likewise: D' and its previous trade date must both lie in D's segment, and D's previous trade date too; gaps
use each date's own fronts (equal inside a segment). The first universe date's previous trade date (2020-11-30) is
sealed, so its gap is undefined.

**B-F15 (F1.5).** vrel15 is invalid when any of the three fronts is unknown (its volume cannot be counted) or the
denominator is 0. F1.5 needs no segment check (G2 restricts only the crush and its residual).

**B-F49 (F4.9).** "0 at 08:35": the value at i = 0 is 0; it is still invalid when M(t), M(08:35) or sigma_ZM is
undefined.

**B-LT1-1 (builder cutoff).** P4.1 LT1: "recompute every feature from ALL input streams ... truncated at
ts_recv <= t". The builder truncates every stream of the target date (ZM MBO, ZS/ZL MBP-1, definitions, and the
previous date's records on a late open) and reuses history day raws built without a cutoff only when the history
date's whole ts_recv window ends at or before the cutoff (asserted), since such a raw contains no record after t. The
lead may prefer literal recomputation of the history too; the result is identical by construction. Fix on
2026-10-28 (code fb69badd4bb9): the truncated target raw is cached under lt1/<cutoff>/dayraw/<code_sha12>/ (it was
lt1/<cutoff>/dayraw/, so a raw from older code could be reused at the same cutoff; found when a self-check failed
on a stale raw).

## What the readings do on the 20 B3 dates (features only; code 345ba20d4f97, unchanged at fb69badd4bb9)

After FD3 (code fb69badd4bb9, built 2026-10-28) no OFI window of the 20 B3 dates holds an uncomputable term, so
F2.8-F2.11 and F3.1-F3.4 are valid on every row; the invalid-row counts below are unchanged.

Invalid rows (G3) over 20 dates x 273 rows: F1.3 546 (2 dates with fewer than 3 segment dates among the previous 10:
2022-12-13 has 1, 2023-02-16 has 0), F1.7 and F1.8 1,638 (6 dates: 2021-07-06, 2021-07-09, 2022-12-13, 2022-12-22,
2023-01-11, 2023-02-16; the segment holds fewer than 10 qualifying gaps among the previous 20 dates, e.g. 2023-01-11
has 10 segment dates but its oldest one's previous trade date lies outside the segment, so 9 gaps under B-GAP-1),
F3.7 73 (scattered minutes where both seasoned touch quantities are 0). Every other feature is valid on every row.
C.11 is therefore 0 on all rows of those 6 dates. Under reading (b) of B-OPEN-1 (first code version) F1.2 alone was
invalid on rows 0-115 of every date.

Independent checks run on real data (book states and features only): a plain-dict ZM book (no mbo_book31) and
wall-clock window sums agree with the day raws on 2022-09-01 and 2024-02-15 (ZM mid at the 279 marks 279/279;
rZ_k numerators for k = 1, 5, 15, 30, 60, V_ZM(15), B_5 and ZS OFI_1 at rows 60-278, 219/219 each). A truncation
self-check in the form of LT1 (every stream of the target date cut at ts_recv <= t, the row at t recomputed) gave
59/59 equal features at 9 times on 6 dates (2023-04-10 i 0, 7, 131, 272; 2021-07-06 i 0, 150; 2021-01-19 i 3;
2022-12-22 i 272; 2024-02-15 i 61).

## Deviations from INTERFACE.md (none in schema)

None found. Column names, order, dtypes and the _day JSON keys follow INTERFACE 4.1; _day JSON also carries the
fronts and n_hist.

## E.33b, 2026-10-28 09:13-10:01 PDT (FeatureCoder2-OpusXHigh, Coder-B continued): lead rulings R-B3-FD6, R-B3-N10, R-L11

Rulings from reports/stage_e33_protocol_readings.md (09:12 PDT) and the lead's message (R-L11, 09:52 PDT by the lead's
clock; received 09:43 PDT by `date` here). Nothing else changed. Code 0485beafebbb (was fb69badd4bb9); changed files
replayB.py (sha256 5910d217000ab92b6452b0263808121374422b5abe445f47849343dbda036c1e) and dayB.py
(87a57970fb219fa720ef57abd38f3d601a805ef041b3aeebf8fa62699379189c); calB.py, featB.py, build_featB.py unchanged.

- **R-B3-FD6 replaces the depletion rule of B-REFILL-1 (F3.11).** A C/M record opens the 100 ms refill window only if
  its whole reduction is fill lots of its event batch (fill > 0 and remainder 0) and it leaves the touch level at 0.
  A record that removes fill lots and a voluntary remainder at once (partial fill, rest cancelled or modified away)
  opens no window; its remainder is still a touch removal (F3.9, unchanged). Code: replayB.replay_zm `reduce`,
  `# READING R-B3-FD6`. Effect on the 20 B3 dates (whole streams, counts only): refill events 80,521 -> 80,305 (216
  dropped; the new set is a subset of the old on each date); removals, sweeps and book states identical.
- **R-B3-N10 (= R-B3-D1) replaces the order in B-BOOKBAD.** An R record with F_MAYBE_BAD_BOOK (or F_TOB/F_MBP) clears
  the book, then marks it bad, so it stays bad until the next R (before: the mark preceded the clear and the clear
  reset it). Code: replayB.replay_zm R branch, `# READING R-B3-N10`. Effect: none on the 20 dates (0 records with
  those flags).
- **R-L11 replaces B-RP-1's "every valid book update" (F4.6).** Hi and Lo run over the as-of function M(u),
  u in [08:30, t]: the state as of 08:30:00 and, for each distinct ts_recv in (08:30, t], the state after the last
  book update with that ts_recv, if valid (valid-mid rule unchanged). Code: dayB._range, `# READING R-L11`. Effect on
  the 20 dates (counts only): 58,115 updates in (08:30, 13:13] share their ts_recv with the next update (all valid;
  155 with a different mid from the next), none of which set a new running Hi or Lo at any mark, so F4.6 is
  unchanged on all 20 dates (and rp_hi/rp_lo on all 328 day raws).

Tests (hand-built, synthetic; tests/test_replayB.py): test_fd6_fill_plus_voluntary_remainder_opens_no_refill_window
(C and M-to-another-price cases), test_fd6_all_fill_emptying_record_opens_refill_window,
test_n10_flagged_r_record_leaves_the_book_bad_until_the_next_r (F_MAYBE_BAD_BOOK, F_TOB, F_MBP),
test_rl11_range_uses_only_the_last_update_of_each_ts_recv. Run against the HEAD (fb69badd4bb9) files: 6 fail as
intended (all but the all-fill case, which both versions pass). implB/tests at 0485beafebbb: 96 passed (test_featB
37, test_labB 33, test_replayB 26).

Store: DERIVED/implB/features/0485beafebbb/ (20 parquets, 20 _day JSON, manifest.json), day raws
DERIVED/implB/dayraw/0485beafebbb/ (328). Against fb69badd4bb9 (exact, NaN == NaN): only F3_11 differs (5,385 of
5,460 rows; rbar_15 changes on every date); every other column and every _day JSON identical; day raws differ only
in rfb15 (129 of 328 dates) and rfa15 (131). Superseded and left on disk: DERIVED/implB/dayraw/1570ccd23c76/ (263
raws of the FD6+N10 code before R-L11, no features; stopped 09:43 PDT).
