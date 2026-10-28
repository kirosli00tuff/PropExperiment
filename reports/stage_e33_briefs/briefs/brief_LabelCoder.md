# Brief: LabelCoder-OpusXHigh (Stage E.33 B1, Coder-A: labels, sampling, weights, trade outcomes)

You are a worker (Opus 5.5, xhigh) for the E.33 lead. Do not spawn workers. Do not use AskUserQuestion: decide
conservatively, log it, continue. The user asked for extreme care with the mathematics.

## Objective
Implement P3 exactly: executable prices with latency and the fallback (P3.2), fixed-horizon labels (P3.3),
triple-barrier labels (P3.4), the exclusion rules with their split into entry rules and row rules (P3.6), rows and
uniqueness weights (P3.7), and the per-minute, per-side simulated trade outcome fields the simulator needs (P3.8's
per-trade inputs), in INTERFACE.md 4.2's schema, on the ZM front's book replayed with mbo_book31.Book and stepped
through book updates (records carrying F_LAST; P0.3). Event-loop style. You are Coder-A; Coder-B implements the same
text independently and the two are compared on 20 dates: labels and classes must be exactly equal (G7). Do the price
arithmetic in integer ticks and subtract f = 0.528 once, so equal inputs give bit-equal nets.

## Read first (by section)
- reports/stage_e33_briefs/INTERFACE.md (all; section 2 rules bind you, especially rule 1: no statistic of label
  values on real data)
- Protocol reports/stage_e32_discovery_protocol.md: 0.3, P1.4, P3 (all), P4.1 LT2, LT4, LT7 (LT7 recomputes an entry
  fill from streams truncated at the production fill time: expose a function that computes one side's entry fill
  from given records and a cutoff)
- reports/stage_e31_briefs/work/pilot/mbo_book31.py; measure31_core.py History and InstrumentRun.commit (as-of top of
  book at F_LAST boundaries; lift the logic, do not import placements or fill models)
- reports/stage_e33_briefs/briefs/brief_DataCoder.md "Deliverables" 2 and 4 (data33 and cal33 API; DataCoder is
  writing them now; poll work/DataCoder_progress.md; until they land, test with hand-built record arrays)
- sigma_ZM(D) for the TB width comes from DERIVED/features/<sha>/_day/<date>.json (INTERFACE 4.1): take it as an
  argument; tests pass it directly.

## Points the protocol fixes that are easy to get wrong
- Entry rules (known at t) versus the locked-book row rule (looks into the span): P3.6 first paragraph. The
  simulation never conditions an entry on the row rule; it uses the P3.2 fallback.
- A row needs its whole possible span [t, t + L + h min] inside D's day session on one ZM front, clear of
  [R - 2 min, R + 30 min] for every release R, starting at or after 08:35:00 and ending by 13:13:00, D not excluded
  (P1.4), no book update in the span with an empty side or a bad book, not within 2% of a price limit at t
  (HL - 0.02c, LL + 0.02c; skip the limit part when cal33.limits(D) is None), and a valid M_ZM(t).
- P3.2 fallback per side; the entry not made, the limit mark and the last-touch mark; TB m0 at the entry fill update
  (per side); the TB barrier ignores updates where M_ZM is undefined; assert one update cannot hit both barriers.
- P3.7 weights: one-minute intervals; c_m counts the rows of the same label type and date whose span intersects m by
  more than one second (FH: h intervals; TB: the realised [t, tau + L]); u_i = mean of 1/c_m over the intervals that
  span_i intersects by more than one second; raw u_i, no renormalisation; per date.
- Per-side outcome fields for every entry_ok minute (INTERFACE 4.2), with the invariant s_net == n_s exactly where
  row_ok and no fallback fired. The sequential account logic (one position, 20 entries, next decision after the
  exit) belongs to the SearchCoder.

## Deliverables (reports/stage_e33_briefs/work/pipeline/)
1. lab33.py and build_labels33.py (resumable per (label, date), DONE markers, --dates, at most 3 processes, nice 10,
   output DERIVED/labels/<code_sha12>/<LABEL>/ with a manifest of code sha256s, per-date _excl json with the rows
   and minutes removed per rule).
2. tests/test_lab33.py with hand-built books (answers computed by hand in the test) for: executable prices with L;
   entry and exit fallback; entry not made; limit mark; last-touch mark; FH classes incl. the dead zone (N_long +
   N_short < 0); TB up, down and vertical; barrier ignoring undefined mids; each P3.6 rule with one case that
   removes a row and one that keeps it; entry_ok versus row_ok; the release-window parse inputs (via cal33 or a stub);
   weights on a hand example; the s_net == n_s invariant; ts_recv ordering (LT4).
3. You may run the builder on at most 3 real dates for timing and schema, printing only row and exclusion COUNTS.
   Write per-date seconds to reports/stage_e33_briefs/work/probe_labels.md. The full build waits for the
   registration (the lead launches it).

## Boundaries
No features, models or P8. Never read reports/stage_e33_briefs/work/implB/. INTERFACE.md section 2 rules apply.

## Return
Paths, a summary of at most 200 words, what is unfinished, and reports/stage_e33_briefs/work/LabelCoder_readings.md.
