# LabelCoder (Coder-A labels) readings, Stage E.33

Author: LabelCoder-OpusXHigh, 2026-10-27 (PDT). Code: reports/stage_e33_briefs/work/pipeline/lab33.py (each
reading is marked `# READING <id>` there unless it says otherwise). Protocol = reports/stage_e32_discovery_protocol.md
(sha256 c4ffb9d7...). The lead decides each before the freeze; Coder-B (implB) may have chosen differently on any
row marked "G7 risk", so the lead should harmonise those before the 20-date comparison.

| ID | Protocol text (quoted) | Readings considered | Choice | Why (conservative) | G7 risk |
|---|---|---|---|---|---|
| TB-SPAN | P3.6: "A label span is [t, t + L + h min] (FH) or [t, tau + L] (TB) ... a trade may be entered at t only if the possible span [t, t + L + h min] meets them"; rule 5 row part: "no span with a book update at which the ZM book lacks a bid or an ask or is marked bad" | (a) realised TB span [t, tau + L]; (b) possible span [t, t + L + h]; (c) their union [t, max(t + L + h, tau + L)]; (d) the whole possible TB span [t, t + 2L + h] | (c) for the locked-book row rule. Rules 1-3 use [t, t + L + h] for both types (on the minute grid (b), (c), (d) give identical rule 1-3 results: shown in the code comment and by hand, the release-window edges and 08:35/13:13 bounds are whole minutes and L = 1 s) | tau + L can exceed t + L + h by up to L (tau <= t + L + h); (b) alone could leave the TB exit price at tau + L undefined, (a) alone ignores the declared possible span. The union removes every row either reading removes | yes (a row with a bad update in (t + L + h, tau + L] or in (tau + L, t + L + h]) |
| R5-CROSSED | (superseded 2026-10-28 by lead ruling D2, below) | - | - | - | - |
| LOCKED-LITERAL | rule 5 heading "Locked or halted book"; text: "lacks a bid or an ask or is marked bad" | (a) literal text; (b) also remove spans with a crossed or locked quote (bid_1 >= ask_1, both sides present) | (a) | "Locked" here is the futures sense (limit-locked: one side empty), which the text already covers; (b) adds a rule the protocol does not state. Labels stay defined under (a) because rows need M_ZM(t) defined and TB barriers ignore undefined mids. A consequence: P3.3's claim "both cannot be positive" needs s >= 0; lab33 raises LabelError if both N are ever positive (never on the probe dates) | low |
| TB-M0 | P3.4: "m0 = M_ZM(t + L)" | (a) row removed when M_ZM(t + L) is undefined; (b) use the last defined mid | (a), counted as `tb_m0` in _excl (attributed to r5_locked_span instead when a bad update in the span exists) | no label without its defined anchor; mirrors P3.2's "entry is not made" for the trade | low |
| ENTRY-WINDOW | P3.2: "an entry with no such update before its planned exit time is not made" | FH: exit decision t + h, or exit fill t + h + L; TB: the vertical barrier t + L + h, or tau (circular: tau needs m0 from the fill) | FH: t + h; TB: t + L + h; strictly before | P3.8 names the exit times "FH at t + h, TB at tau"; for TB the latest tau is t + L + h. Strict "before" admits fewer fallback entries | yes (fallback fills in [t + h, t + h + L) for FH) |
| ENTRY-FLAGS | INTERFACE 4.2: "1 entry fallback fired ... 16 entry not made (no valid update before the planned exit)" | flags 16 alone, or 1 + 16 | 1 + 16 when the fallback was needed and found nothing; 32 with 1 when a fallback fill had M_ZM undefined; 32 alone when the as-of t + L fill had M_ZM undefined | bit 1 records that the needed side was empty or the book bad at t + L, which is true in that case | flags only (no label effect) |
| EXIT-MARK-TIME | P3.2: "an exit with none before 13:20:00 is marked at the front's limit price ... or ... the last valid touch" | s_exit_ns = 13:20:00 CT, or -1, or the planned exit time | 13:20:00 CT on D | the position cannot be closed before the end of the window; the SearchCoder's "next decision at or after the exit fill time" then ends the date's trading | flags/time only |
| FILL-TIME | LT7: "the production fill time (t + L, or the fallback fill update of P3.2)" | entry/exit fill time = u + L, or the ts_recv of the as-of update | u + L when no fallback; the fallback update's ts_recv otherwise | LT7's own wording | no (not a label) |
| TB-TIE | P3.4: "tau = min(tau_up, tau_dn, t + L + h min) ... y = +1 if tau = tau_up" | (a) by update order (first barrier-hitting update in the ts_recv-ordered sequence); (b) by time, +1 first when two different updates with the same ts_recv hit opposite barriers | (a) | "first ZM book update" is an order statement; a mid move of 2b inside one ts_recv tick is the only case where they differ | very low |
| TB-EXACT | P3.4: "M_ZM(u) >= m0 + b(t)" | float m0 + b, or the exact form | exact: (S_u - S_0) >= 2b in float64 with S = bid_1 + ask_1 integer ticks (doubling and int->float are exact), b = 1.0 * sigma * math.sqrt(h) | equals the real-number comparison; float m0 + b can round at a tie | very low |
| TB-SIGMA | P3.4: b(t) = kappa sigma_ZM(D) sqrt(h); "For b(t) > 0 ..." | skip TB on D, or stop | LabelError (stop) when sigma_ZM(D) is null, non-finite or <= 0 on a date that is not excluded | a TB label without a width cannot exist; a silent skip would hide a feature-layer gap | no |
| W-SUM | P3.7: "u_i = the mean of 1/c_m over the intervals m that span_i intersects by more than one second" | np.mean, sequential sum, fsum | math.fsum(1/c_m) / n (correctly rounded, order-free); overlap measured as min(end, m_end) - max(start, m_start) > 1 s strictly; intervals are absolute UTC minutes (CT minute marks coincide) | bit-reproducible across implementations that agree on c_m | weights only (tolerance) |
| BOOK-BAD-FLAGS | 0.3: "the book is not marked bad (F_MAYBE_BAD_BOOK)" | F_MAYBE_BAD_BOOK only; also F_TOB / F_MBP as E.31 does | as E.31 (README_measure31 convention 5) | zero F_TOB / F_MBP records in Z1 (stage_e32_data_facts.md 1.5), so no effect | none |
| BOOK-UPDATE | 0.3: "'Book update': the book state after a record that carries F_LAST ... A book update's time is the ts_recv of its F_LAST record" | (not ambiguous) E.31's InstrumentRun also commits at a bad-flag record without F_LAST | literal: updates only at F_LAST records; a bad mark becomes visible at the next F_LAST record; every update kept (no de-duplication), several per ts_recv allowed; records before the first R skipped; T/F/N leave the book unchanged | protocol definition (FixVerifier R-W2-6) | low |
| REPLAY-END | P3.2 exit fallback "before 13:20:00" | replay to 16:00 or to 13:20 | the builder replays the front's records with ts_recv < 13:20:00 CT (data33.load_zm cutoff 13:20:00 - 1 ns) | no label or fill looks at or after 13:20:00 | none |
| GRID-R1R2 | P3.6 rules 1-2 | - | implemented and counted, but on G_h(D) they never fire (t >= 08:35; t + L + h <= 13:12:01; TB tau + L <= 13:12:02) | - | none |
| LIMIT-ORDER | P3.6 rule 5 limits | - | DayInputs raises if HL <= LL or if UNDEF/0 limits are passed instead of None | a malformed limit pair stops the build rather than mis-excluding | none |
| MIDMOVE-EXCL | Lead follow-up 2026-10-27: "`mid_move` ... for every grid minute i; ... NaN when either mid is undefined" (P6.2 reported-only; never used by P8) | (a) NaN on P1.4-excluded dates (no book replayed there before); (b) filled on every grid minute of every date | (b): the builder now replays the book on excluded dates too; flags stay false there. If E.31's Z1 store has no records for an excluded date, mid_move stays NaN and `book_missing` is set in the result line (a non-excluded date without records still stops the build) | the lead's text says every grid minute; the column is not a flag. Value = (S(t+L+h) - S(t+L)) / 2 exactly, S = bid_1 + ask_1 integer ticks, mids as of ts_recv <= each instant, TB with the vertical h | none for labels (a reported column) |

## Finding for the lead (data, not a reading; counts and book states only)

- 2021-07-01 (OOF, not excluded): rule 5's limit part removes all minutes of every label (F15: 263 of 263). The
  ZM front ZMZ1 (794459) traded at bid 385.6 / ask 385.7 at 08:35 CT, above the high limit 384.9 of its last
  definition with ts_recv <= 08:30 CT (HL 384.9, LL 324.9). The Z4 definitions of 794459 at 2021-06-30 00:00Z,
  2021-07-01 00:00Z and 2021-07-02 00:00Z all carry 384.9 / 324.9, so the 07-01 record did not move its band
  after the 2021-06-30 USDA Acreage / Grain Stocks session. The mechanical rule (P3.6 rule 5, FixSpotCheck S-A-9)
  is implemented as written; whether Databento's definition limits lag the exchange's daily limits on other dates
  (it would remove whole days after large moves, and the P3.2 limit mark would use the stale band) is a question
  for the lead. Not counted across the universe: the brief caps real-data runs at 3 dates.

## Lead rulings after B3 (2026-10-28 PDT), applied in code sha12 ff0181fc391c

B3: all six labels agreed exactly with Coder-B on the 20 dates. Two latent readings that B3 did not trigger were
ruled for Coder-B's side and lab33 changed to match:

- D1 (replaces part of BOOK-BAD-FLAGS / BOOK-UPDATE): an R record that carries F_MAYBE_BAD_BOOK clears the book first
  and then marks it bad; the book stays bad until the next R, and a book update at that state is bad. lab33
  `_drive_book` now applies the bad mark after the record's action (for every record other than R the order makes
  no difference, the mark being sticky until an R). Test: test_d1_r_record_with_bad_flag_leaves_book_bad_until_next_r.
- D2 (replaces R5-CROSSED): entry_ok requires M_ZM(t) defined (both sides, bid_1 < ask_1, not bad) on every date,
  with or without limit prices; a crossed or locked book at t fails `r5_book_at_t` (also counted in
  `book_crossed_or_locked_at_t`), the limit part is evaluated only where M_ZM(t) is defined, and the row rule
  `p37_mid_t` can no longer fire. Test: test_d2_entry_needs_defined_mid_on_a_date_without_limits (and the updated
  test_rule5_book_at_t_and_crossed_reading).
- D5: TB-SIGMA kept (LabelError stop when sigma_ZM(D) is undefined on a date that is not excluded).

Rebuild of the 20 B3 dates (02:46:42-02:47:12 PDT, 2 processes, nice 10, free 6.7 GB available, peak RSS 0.4 GB,
sigma from DERIVED/features/c22b0a50f4cd/_day): DERIVED/labels/ff0181fc391c/. Every column of all 120 (label, date)
files is equal to the B3 build 17934b7b23b1 (equality check only); 30,260 grid rows, 23,443 entry_ok = rows kept;
LT2 violations 0; crossed or locked at t 0; fallback/mark flags 0.

Effect on the TestCoder's pipeline/tests_b4/test_lt4_labels_handbuilt.py: test_latent_d1_bad_flag_on_clear and
test_latent_d2_locked_at_t_no_limits now XPASS; test_d1_behaviour_documented (line 232) and
test_d2_behaviour_documented (line 256) now FAIL because they assert the old Coder-A behaviour. That file belongs to
the TestCoder; not edited here.
