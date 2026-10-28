# Brief: FeatureCoder2-OpusXHigh (Stage E.33 B2, Coder-B: independent features)

You are a worker (Opus 5.5, xhigh) for the E.33 lead. Do not spawn workers. Do not use AskUserQuestion: decide
conservatively, log it, continue.

## Independence (the point of your task)
You write the INDEPENDENT second implementation of the protocol's features (prompt B2). You work from the protocol
text alone. You never read anything under reports/stage_e33_briefs/work/pipeline/ except guard33.py and data33.py
(the read guard and the raw-record loader), and you never read the other coders' briefs or readings files. Your
results are compared with Coder-A's on 20 dates within G7's tolerance (1e-9 relative, 1e-12 absolute near 0); each
disagreement is traced to a cause and fixed in the implementation that is wrong, so write your code so each step can
be audited against the protocol line, with the protocol ID in a comment.

## Objective
Implement every P4 feature (59) from the protocol text in a vectorised style: for example, replay the ZM front's
book once per date into arrays of book-update states (ts_recv, the first 5 levels' prices and quantities, seasoned
quantities, best-level removals) and trade records, then compute the minute features with searchsorted, cumulative
sums and window arithmetic. Produce the INTERFACE.md 4.1 tables under
/mnt/large-storage/market_data/PropExperiment/derived/e33/implB/features/ and _day/<date>.json with sigma_zm,
sigma_zs, sigma_zl (LabelCoder2 reads sigma_zm from it).

Write your own calendar helpers: the trade dates from the program calendar (data.calendars / measure31.grains, P1.4),
the fronts with measure31.instrument_on as P0.3 names, segments (P4 G2), and the release calendar parse of P3.6 rule
3 (for C.8, C.9 and F1.3). Do not import cal33.

## Read first (by section)
- reports/stage_e33_briefs/INTERFACE.md (all; section 2 rules bind you)
- Protocol reports/stage_e32_discovery_protocol.md: 0.3, P1.3, P1.4, P3.6 rule 3, P4 (all), P4.1 LT1, LT4
- reports/stage_e32_data_facts.md sections 1, 3.2, 6
- reports/stage_e31_briefs/work/pilot/mbo_book31.py (P0.3 names Book for the ZM book; you may use it for the replay;
  implement seasoned depth, OFI, sweeps, refills, removals and everything else yourself), measure31.py
  (instrument_on, day_bounds, grains, calendar_reason, read_definitions, checked_tick)
- pipeline/data33.py and pipeline/guard33.py only, when they land (DataCoder is writing them now; poll for the
  files). Their API: data33.load_zm(D, cutoff_ns=None) (E.31 Z1 per-day MBO records, all ZM instruments),
  data33.load_mbp1(root, D, cutoff_ns=None) (ZS or ZL MBP-1 with all fields), data33.definitions(cutoff_ns=None).
  Until they land, write and unit-test your logic on hand-built arrays.

## Deliverables (reports/stage_e33_briefs/work/implB/)
1. featB.py plus a builder with --dates and a cutoff option; implB/tests/test_featB.py with your own hand-built
   known-answer cases (at least one per feature), the G4 clip list and G3 invalid handling.
2. Outputs for the 20 B3 dates (the "B3 dates rule" in reports/stage_e33_STATE.md, applied to your own OOF list) with
   every look-back date they need; nice 10, at most 3 processes, `free -m` first (stop below 2 GB available).
3. A timing note in implB/timing_featB.md.

## Return
Paths, a summary of at most 200 words, what is unfinished, and implB/FeatureCoder2_readings.md (each protocol detail
you had to read one way: the line, the readings, your choice, why it is the conservative one).
