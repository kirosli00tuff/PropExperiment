# LabelCoder2 readings (Stage E.33 B2, implementation B of P3)

Worker: LabelCoder2-OpusXHigh. Protocol: reports/stage_e32_discovery_protocol.md (sha256 c4ffb9d7...,
checked at start). Code: reports/stage_e33_briefs/work/implB/labB.py, labB_book.py, labB_cal.py,
build_labB.py (code_sha12 efdde5c74ee1, final build 15:13-15:16 PDT). Each reading is marked in the code as `# READING LB-n`
where it applies. The lead decides each reading before the freeze. "Effect on B3 dates" gives counts
from the 20 built dates (counts only).

## LB-1 Book update and as-of lookup
- Protocol 0.3: "'Book update': the book state after a record that carries F_LAST (the end of one
  event batch). ... 'as of u' means the last book update with ts_recv <= u ... A book update's time
  is the ts_recv of its F_LAST record".
- Readings considered: (a) every F_LAST record of the front, including T, F and N records, which
  leave the book unchanged; (b) only F_LAST records that changed the book.
- Choice: (a). Several updates with the same ts_recv are kept in record order. "As of u" uses
  the last one in that order; a first-touch search (TB) and the rule 5 row check visit each one.
- Why: this is the literal text. It does not change prices.

## LB-2 TB "whole possible span" for the row rules (rule 5 row part, rules 2-3)
- P3.6: "A label span is [t, t + L + h min] (FH) or [t, tau + L] (TB). ... a trade may be entered
  at t only if the possible span [t, t + L + h min] meets them ... A row is kept only if its whole
  possible span lies inside D's day session on one ZM front and meets every rule".
- Readings considered: (a) the realised TB span [t, tau + L]; (b) [t, t + L + h min], the
  possible span the entry paragraph names; (c) the union of every realised span a TB label can
  have, [t, t + h min + 2L], since tau <= t + L + h min and the exit fills at tau + L.
- Choice: (c) for the row rules. The entry rules use [t, t + L + h min], as written.
- Why conservative: (c) contains (a) and (b), so it never keeps a row whose label could need a
  missing exit price. On the minute grid, rules 2 and 3 give the same result for (b) and (c).
- Effect on B3 dates: 0 rows removed by the extra part (span_row and r5_row counts are 0).

## LB-3 Crossed or locked book at t (entry rule and limit test)
- P3.6: "a trade may be entered at t only if ... the ZM book at t has both sides and is not marked
  bad". P3.7: rows need "a valid M_ZM(t)". 0.3: M is "defined only when both sides exist,
  bid_1 < ask_1 and the book is not marked bad". Rule 5's limit test uses M_ZM(t).
- Readings considered: (a) entry needs only both sides and not bad; if the book at t is crossed
  or locked, the limit test is either skipped or failed; (b) entry also needs M_ZM(t) defined.
- Choice: (b). entry_ok requires M_ZM(t) defined (the `mid_t` rule).
- Why conservative: under (a) an entry on a crossed book would depend on whether D has limit
  prices. (b) never trades a book state the protocol calls invalid.
- Effect on B3 dates: 0 minutes (mid_t first-rule count 0). INTERFACE.md 4.2 lists the literal
  rule, so this is a stated difference from INTERFACE.

## LB-4 "Planned exit time" for entries not made
- P3.2: "an entry with no such update before its planned exit time is not made (counted)". P3.8:
  "FH at t + h, TB at tau".
- Readings considered: FH: (a) t + h, the exit decision time, or (b) t + h + L, the exit fill
  time. TB: (a) t + L + h min, the vertical barrier and latest possible tau, or (b) that time
  plus L.
- Choice: (a) for both. "Before" is strict: an update at exactly the planned exit time is too
  late.
- Why conservative: fewer partial-hold trades are made.
- Effect on B3 dates: no entry fallback fired.

## LB-5 Fill time of a normal fill
- P3.2: "A market buy decided at time u fills at ask_1 of the ZM book as of u + L".
- Readings considered: (a) the fill time is u + L; (b) the fill time is the ts_recv of the as-of
  update.
- Choice: (a) for normal fills (s_entry_ns = t + L; s_exit_ns = exit decision + L). A fallback
  fill takes the ts_recv of the fallback update.
- Why: the text times the fill at u + L. P3.8's next decision is "the first grid minute at or
  after the exit fill time", and (a) is never earlier than (b).

## LB-6 Release window edges
- P3.6 rule 3: "no span intersects [R - 2 min, R + 30 min]".
- Choice: closed intervals at both ends. A span ending exactly at R - 2 min, or starting exactly
  at R + 30 min, intersects. With h = 5 the excluded starts are 10:53 to 11:30 (38 minutes).
- Why conservative: more minutes are removed at the edges.

## LB-7 TB row when M_ZM(t + L) is undefined
- P3.4: "m0 = M_ZM(t + L)". The rule 5 row part catches only a missing side or a bad book. A
  crossed or locked book at t + L leaves m0 undefined.
- Choice: no row (`label_undef`, counted). The entry minute stays; the simulation marks it
  TB-not-made (flag 32), following P3.2's TB rule.
- Effect on B3 dates: 0.

## LB-8 TB when sigma_ZM(D) is undefined
- P3.4: "b(t) = kappa x sigma_ZM(D) x sqrt(h)". 0.3 allows sigma to be undefined.
- Choice: no TB entries and no TB rows on D (`tb_sigma`, counted).
- Why conservative: a TB trade cannot be simulated without b.
- Effect on B3 dates: 0. sigma was defined on all 20 dates.

## LB-9 Opposite barriers touched at the same ts_recv
- P3.4: "tau = min(tau_up, tau_dn, t + L + h min)"; "+1 if tau = tau_up".
- Choice: the first update in record order wins. Same-ts_recv cases where a later update touches
  the opposite barrier are counted (`tb_same_time_ties`).
- Effect on B3 dates: 0.

## LB-10 Meaning of flag bits 1 and 2
- INTERFACE.md 4.2: "1 entry fallback fired, 2 exit fallback fired, 4 exit marked at the limit
  price, 8 exit marked at the last valid touch, 16 entry not made ..., 32 TB entry not made".
- Readings considered: (a) bit 1 or 2 is set whenever the needed side was missing or bad at
  u + L, so the fallback rule was invoked; (b) only when a fallback fill happened.
- Choice: (a). An entry not made for lack of a valid update carries 1|16. A marked exit carries
  2|4 or 2|8. A TB entry whose fill update has no mid carries 32, or 1|32 after a fallback fill.
- Why: the INTERFACE invariant ("where row_ok and no fallback fired, s_net equals n_s exactly")
  then holds as flags == 0. Coder-A may read it as (b); B3's flag comparison will show it.

## LB-11 Time of a marked exit
- P3.2: "an exit with none before 13:20:00 is marked at the front's limit price ...".
- Choice: s_exit_ns = 13:20:00 CT for a limit or last-touch mark. A fallback exit fill must come
  strictly before 13:20:00.
- Why: no fill exists. 13:20 is the moment the mark applies, and no later trade follows on D.

## LB-12 Book driver around mbo_book31.Book
- 0.3: "Book: ZM from MBO (mbo_book31.Book, full displayed depth)"; "the book is not marked bad
  (F_MAYBE_BAD_BOOK)". mbo_book31's docstring: "F_MAYBE_BAD_BOOK marks the book bad until the
  next R".
- Choices:
  - Records before the first R are not applied, and updates from them count as invalid ("not
    started"): 1,752 such records on the 20 dates, all before the evening snapshot.
  - F_MAYBE_BAD_BOOK on an R record marks the book bad after the clear. This is conservative;
    E.31's driver clears last.
  - A or M records with side N are skipped and counted.
  - T, F and N records change nothing.
- Effect on B3 dates: 0 bad-flag records, 0 side-N records, 1 clear (the snapshot) per date.

## LB-13 F_TOB / F_MBP on MBO records
- The protocol names only F_MAYBE_BAD_BOOK. E.31's driver also marks the book bad on F_TOB or
  F_MBP.
- Choice: F_TOB and F_MBP do not mark the book bad. They are counted.
- Effect on B3 dates: 0 such records. If any appear on other dates, the lead should rule.

## LB-14 Roll exclusion when the front is unknown
- P1.4: "(i) a ZM roll date ... and the trade date after it (measure31.roll_reasons)".
  roll_reasons also returns 'roll_status_unknown' and 'no_symbol_mapping'.
- Choice: every reason roll_reasons returns excludes the date.
- Why conservative: it removes more dates.
- Effect: over the 816 dates, 52 are excluded (23 roll_day, 21 after_roll_day, 5
  scheduled_late_open, 4 cme_holiday_or_early_close; one date has two reasons); 49 of them are OOF
  dates. No unknown or no-mapping reasons occur. B3 dates excluded: 2021-07-06 (scheduled late
  open) and 2022-12-13 (after roll).

## LB-15 Data finding: the definitions' limit fields are refreshed weekly, not daily
- P3.6 rule 5: "HL and LL are the high and low limit prices of the front's last definition
  record with ts_recv <= 08:30:00 CT on D".
- Implemented literally. Finding: definition records arrive daily at 00:00 UTC, but
  high_limit_price and low_limit_price change only on Sundays. For ZMZ1, ZMN2 and ZMK1 the change
  dates are 2020-12-06, -13, -20, -27, ... (52, 82 and 22 changes over 328, 508 and 142
  records). On the B3 dates the band in use is 1 to 5 days old.
- Effect on B3 dates: on 2021-07-09 (band 5 days old; the 08:35 mid sits at -0.968 of the half
  band below its centre) all 273 F05 minutes are removed. 82 are removed on 2021-04-01 and 142 on
  2022-06-03. In total r5_limit removes 497 F05 minutes on the 20 dates.
- Not changed (a declared rule). For the lead: the rule as written measures distance to a weekly
  band, not to the daily limit that the cited firm rule (M6 4.1) refers to.

## LB-16 sigma_ZM(D) source and details
- Brief: read sigma_zm from derived/e33/implB/features/_day/<D>.json, or compute it per P0.3.
- That folder did not exist at build time (15:07 PDT), so all 20 dates use my own sigma
  ("sigma_source" in _day/<D>.json).
- Details:
  - Minute marks 08:35 to 13:13 (279 marks, 278 intervals).
  - As-of mids from each history date's own front, which chains across rolls.
  - Changes are pooled over the 20 prior trade dates (burn-in dates included) where both ends
    have a valid mid. Population SD in ticks.
  - The replay keeps records with ts_recv <= 13:13:00 CT inclusive. The first build cut at
    13:13:00 minus 1 ns, so it would have missed an update stamped exactly at the mark; that
    build was discarded and rebuilt.
- If FeatureCoder2's file appears, the builder uses it (--sigma auto). A mismatch between the two
  sigmas would change TB labels, so B3 should compare them.

## LB-17 Rule 5 row part: which updates are "in the span"
- P3.6 rule 5: "no span with a book update at which the ZM book lacks a bid or an ask or is
  marked bad".
- Choice: updates with ts_recv in the closed interval [t, span end]. The state as of t (an update
  before t) is covered by the M_ZM(t) requirement. A crossed or locked update inside the span
  does not remove the row, because the text names only a missing side or a bad book.
- Effect on B3 dates: 0.

## LB-18 Weights
- P3.7: "c_m = the number of rows of the same label type and date whose span intersects m by
  more than one second".
- Choices:
  - Intervals m are the clock minutes [08:35 + m, 08:36 + m).
  - "More than one second" is strict (> 1 s in ns), so an FH span covers exactly h intervals.
  - Only row_ok rows enter c_m.
  - u_i = math.fsum(1/c_m) / n_i.
- The sum order may differ from Coder-A's at 1e-16 relative, so B3 should compare w within
  1e-12 rather than bitwise.

## LB-19 Limit-proximity arithmetic
- Choice: an exact integer test in ticks: 50 x (bid + ask) >= 99 HL - LL (high side) or
  <= 101 LL + HL (low side). This is algebraically equal to M >= HL - 0.02c or M <= LL + 0.02c.
- A float implementation can differ only on an exact boundary tie.
- The limit fields of the 20 dates are tick multiples (asserted).

## Differences from INTERFACE.md (reported, protocol governs)
- Output path: brief and INTERFACE both say DERIVED/implB/labels/<LABEL>/<D>.parquet. There is no
  <code_sha12> level; the hash is in labels/manifest.json.
- entry_ok adds M_ZM(t) defined (LB-3).
