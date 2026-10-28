# Brief: LabelCoder2-OpusXHigh (Stage E.33 B2, Coder-B: independent labels, sampling, weights)

You are a worker (Opus 5.5, xhigh) for the E.33 lead. Do not spawn workers. Do not use AskUserQuestion: decide
conservatively, log it, continue.

## Independence (the point of your task)
You write the INDEPENDENT second implementation of the protocol's labels, sampling rule, exclusions, weights and
per-side trade outcomes (prompt B2). You work from the protocol text alone. You never read anything under
reports/stage_e33_briefs/work/pipeline/ except guard33.py and data33.py (the read guard and the raw-record loader),
and you never read the other coders' briefs or readings files. Your tables are compared with Coder-A's on 20 dates:
labels, classes and every flag must be exactly equal, nets exactly equal (G7). Do price arithmetic in integer ticks
and subtract f = 0.528 once.

## No outcomes
INTERFACE.md section 2 rule 1 binds you: on real data you never compute, print or save any statistic of label
values, nets, class shares or returns. You may print row counts, exclusion counts and timings. The comparison with
Coder-A is run by another worker.

## Objective
Implement P3 (P3.2 executable prices with L and the fallback, P3.3 FH, P3.4 TB, P3.6 entry rules versus row rules,
P3.7 rows and uniqueness weights, the per-minute per-side simulated outcome fields) in a vectorised style: for
example, one array of ZM front book-update states per date (ts_recv of the F_LAST record, bid_1, ask_1, validity)
with searchsorted for t + L and t + h + L, a vectorised first-passage search for the TB barriers, and interval
counting for the weights. Write the INTERFACE.md 4.2 tables under
/mnt/large-storage/market_data/PropExperiment/derived/e33/implB/labels/<LABEL>/ for the 20 B3 dates (the "B3 dates
rule" in reports/stage_e33_STATE.md, applied to your own OOF list).

Write your own exclusion calendar: P1.4 (roll date and the date after; early closes and late opens; measure31's
roll_reasons and calendar_reason are named by the protocol), P3.6 rule 3 (the release files, the parse rule and the
asserted counts), rule 5 (limit prices of the front's last definition with ts_recv <= 08:30 CT on D, as-of pass over
the definitions in ts_recv order). Do not import cal33. sigma_ZM(D) for the TB width: read sigma_zm from
derived/e33/implB/features/_day/<date>.json (FeatureCoder2 writes it); if it is not there when you need it, compute it
yourself from P0.3 and say so in your return.

## Read first (by section)
- reports/stage_e33_briefs/INTERFACE.md (all)
- Protocol reports/stage_e32_discovery_protocol.md: 0.3, P1.4, P3 (all), P4.1 LT2, LT4
- reports/stage_e31_briefs/work/pilot/mbo_book31.py (Book; P0.3 names it), measure31.py (day_bounds, instrument_on,
  roll_reasons, calendar_reason, grains, read_definitions)
- pipeline/data33.py and pipeline/guard33.py only, when they land (API: data33.load_zm(D, cutoff_ns=None),
  data33.load_mbp1(root, D, cutoff_ns=None), data33.definitions(cutoff_ns=None)). Until then use hand-built arrays.

## Deliverables (reports/stage_e33_briefs/work/implB/)
1. labB.py plus a builder with --dates; implB/tests/test_labB.py with your own hand-built cases (exec prices with L,
   fallbacks, entry not made, limit and last-touch marks, FH dead zone, TB up/down/vertical, each P3.6 rule, weights).
2. The 20-date outputs (nice 10, at most 3 processes, `free -m` first, stop below 2 GB available).
3. A timing note implB/timing_labB.md.

## Return
Paths, a summary of at most 200 words, what is unfinished, and implB/LabelCoder2_readings.md.
