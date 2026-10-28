# Brief: FeatureCoder-OpusXHigh (Stage E.33 B1, Coder-A: features)

You are a worker (Opus 5.5, xhigh) for the E.33 lead. Do not spawn workers. Do not use AskUserQuestion: decide
conservatively, log it, continue. The user asked for extreme care with the mathematics: a leak or a silent error
makes every later number worthless.

## Objective
Implement every P4 feature exactly as the frozen protocol writes it (C 15, F1 8, F2 11, F3 12, F4 13 = 59) with
P0.3's notation and P4's general rules G1-G7, in an event-loop style (stream each date's records once in ts_recv
order and sample the state at the decision minutes), producing the INTERFACE.md 4.1 tables and day statistics.
You are Coder-A. An independent Coder-B implements the same text separately (vectorised), and the two are compared
on 20 dates within G7's tolerance (1e-9 relative, 1e-12 absolute near 0). Write each definition so its steps can be
audited line by line against the protocol, with the protocol ID in a comment.

## Read first (by section)
- reports/stage_e33_briefs/INTERFACE.md (all; section 2 rules bind you)
- Protocol reports/stage_e32_discovery_protocol.md: 0.3 (all notation: fronts, ticks, book, mid validity, sigma_X,
  windows on the open-time axis, trailing 20-date references, decision grid, book updates, statistics conventions),
  P1.3, P4 (all), P4.1 LT1, LT2 (feature part), LT4, P3.6 rule 3 (F1.3's release-clear minutes, C.8, C.9)
- reports/stage_e32_data_facts.md sections 1, 3.2, 5, 6 (grep -n "^#" for ranges)
- reports/stage_e31_briefs/work/pilot/mbo_book31.py (Book: check whether it keeps per-order add/modify times;
  seasoned depth needs the ts_recv of each order's last add or modify), measure31_core.py CondSeries,
  canary_check31.py TFPairing (aggressor side of trades)
- reports/stage_e33_briefs/briefs/brief_DataCoder.md sections "Deliverables" 2 and 4 (the data33 and cal33 API you
  code against; DataCoder is writing them now in pipeline/; poll for data33.py and cal33.py and
  work/DataCoder_progress.md; until they land, test with hand-built record arrays)

## Deliverables (reports/stage_e33_briefs/work/pipeline/)
1. feat33.py (the feature definitions) and build_features33.py (a resumable per-date builder: DONE marker per date,
   nice 10, at most 3 processes by default, --dates, --cutoff-ns for LT1, output DERIVED/features/<code_sha12>/ with
   a manifest.json listing each code file's sha256). Day-level statistics that later dates need (sigma inputs,
   trailing-reference inputs, 13:15 and 08:35 mids, F1 segment samples, F1.3 OLS samples) may be computed in a first
   pass per date and stored under _day/, then the features in a second pass; your design. _day/<date>.json must carry
   sigma_zm, sigma_zs, sigma_zl (ticks) and the fronts (INTERFACE 4.1); the label builder reads sigma_zm from it.
2. tests/test_feat33.py: for every one of the 59 features at least one hand-built case whose answer is computed by
   hand in the test (comment the arithmetic); plus G1 (a record after t changes nothing), G2 (segments, roll
   chaining of scale references), G3 (invalid -> 0 and the family flag), G4 (exactly the 38 clipped and 21 unclipped
   IDs of P4 G4), G6 (no feature uses ts_recv - ts_event), the open-time axis (07:45-08:30 pause and 13:20-19:00
   close skipped; overnight minutes count), ts_recv ordering (LT4), book-update stepping (F_LAST batches; P0.3).
3. Probe: time the builder on the 3 dates of P5's probe bullet (the median, p90 and maximum ZM message-count dates;
   derive them from record counts of the split store or data facts 3.1, never from any outcome); write per-date
   seconds and peak RSS to reports/stage_e33_briefs/work/probe_features.md.
4. Run the builder on the 20 B3 dates (the "B3 dates rule" in reports/stage_e33_STATE.md, using cal33.oof_dates())
   with all the look-back dates they need. Report only counts (rows written, invalid values per feature); feature
   values are not outcomes, but keep output short.

## Boundaries
No labels, returns, models or P8 (other workers'). Never read reports/stage_e33_briefs/work/implB/. INTERFACE.md
section 2 rules apply.

## Return
Paths, a summary of at most 200 words (probe seconds per date, the 20-date run status, invalid-count highlights),
what is unfinished, and reports/stage_e33_briefs/work/FeatureCoder_readings.md (every protocol detail you had to read
one way, with the protocol line, the readings considered, the choice and why it is the conservative one).
