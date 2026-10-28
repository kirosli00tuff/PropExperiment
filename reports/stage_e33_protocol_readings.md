# Stage E.33 protocol readings (P0.2)

Status: DRAFT, not final (lead, opened 2026-10-27 14:52 PDT; last edit 2026-10-28 07:10 PDT). Open for the continuation: the rulings on B3 residuals FD6 (F3_11 mixed fill-plus-cancel record) and FD7 (F3_9 fill naming an order not yet in the book), and PipelineReview SF1-SF3; the coder readings files not quoted below are accepted as summarised in reports/E.33_RETURN.md section 6 unless a ruling here differs. Finalised and hashed before the B7 pipeline freeze; no reading is
added after C1 (P0.2). A reading added between the freeze and C1 re-takes the freeze list.

Protocol: reports/stage_e32_discovery_protocol.md FROZEN v1.0, sha256
c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05.

Each entry: the protocol line, the readings considered, the one chosen, and why it is the conservative one. Entries
R-L* are the lead's own; entries carried from a coder's readings file keep the coder's ID and record the lead's
decision.

## Lead readings

R-L1. P5 probe: "before the first real-outcome fit, E.33 times the feature builder on 3 dates ... and fold 6 (the
largest training set, 664 dates) of the two slowest grid points (E33-S5F15L100E and E33-S5F15G3050)".
Readings: (a) fit fold 6 of those two configurations on real outcomes; (b) time fold 6 of the same two configurations
on a production-size synthetic table (real OOF dates, real grid G_15, real calendar exclusions, 59 synthetic S5
columns; DERIVED/proofs/seed9000/, not a proof seed). Chosen: (b). Reason: (a) is itself a real-outcome fit made
before the projection is written and, before the C1 registration, a fit of an unregistered configuration; (b)
measures the same code path at the same table size and touches no real outcome. The projection formula of P5 and the
3x stop of P10 are unchanged.

R-L2. Prompt B3 and B7 (MathReviewer) compute label values on real discovery dates before C1. Readings: (a) compute and
report label statistics; (b) compute label values only inside equality comparisons (B3: A versus B; MathReviewer: hand
recomputation versus the code), reporting agreement counts and mismatch locations, never a class share, mean or any
other statistic. Chosen: (b). Reason: least exposure of outcomes before the registration; it is all the checks need.

R-L3. P4.2: proof searches run "exactly once per pipeline hash (4,800 fits); after a logged code fix (0.2) all 40 are
rerun with the same seeds". Readings: (a) rerun all 40 after any change to any pipeline file; (b) rerun all 40 after
any change to a file the proof run executes (synth33, run_proofs33, search33, run_search33, select33, cal33, data33,
guard33, p7_final.py, the program functions it calls, uv.lock), and keep the proof results when a fix touches only
files the proof run never executes (the record-level feature and label builders), because those results are then
byte-identical by construction. Chosen: (b), with a check at the freeze: the sha256 of every file the proof run
executed equals its sha256 in the frozen pipeline list; if any differs, all 40 are rerun with the same seeds and every
run before and after is reported. Reason: the rule exists to stop seed or code shopping; under (b) no seed is ever
rerun alone, no result is dropped, and the equality of the executed code is proved by hash rather than assumed.

R-L4. P4.2 planted pass rule: "The proof passes if at least one S5 configuration at FH15 or TB30 enters Tier A in at
least 14 of the 20 planted seeds (P(at least 14 of 20) = 0.91 at a per-seed power of 0.8 ...)". Readings: (a) per
seed, success = at least one of the 20 configurations enters Tier A; pass if successes >= 14; (b) one fixed
configuration enters Tier A in >= 14 seeds. Chosen: (a), and (b)'s per-configuration counts are reported beside it.
Reason: the protocol's own arithmetic is a binomial over seeds with a per-seed power, which is reading (a); every
configuration in the proof search is an S5 configuration at FH15 or TB30, so (a) is the event "the pipeline finds the
plant in this seed". The null rule uses the same per-seed event (Tier A non-empty), so (a) keeps the two proofs
symmetric.

R-L5. Prompt B3 "20 discovery dates chosen by a fixed seed". Chosen rule (fixed 14:45 PDT, before any feature or label
was computed): OOF = the 796 dates sorted; idx = numpy.random.default_rng(20261028).choice(796, 20, replace=False);
dates = sorted(OOF[idx]); a date excluded by P1.4 may be drawn and is counted.

R-L6. Prompt E: "the 2017-05-01 to 2020-11-30 window" for the E.34 draft. P9 sets 2017-05-22..2020-11-30 (MBO from
2017-05-21) and the planner's launch note confirms P9 governs (E.32 D6). Chosen: P9's window; the 15 dates
2017-05-01..2017-05-19 stay sealed and untested.

## Coder readings (decided by the lead before the freeze)

### B3 rulings (lead, 2026-10-28 02:47 PDT; source reports/stage_e33_briefs/work/B3_agreement.md, run full_r1)

R-B3-FD1/FD2. P0.3 "Window of k minutes ending at t: the last k minutes of time during which X was open, ending at t
(the 07:45-08:30 pause and the 13:20-19:00 close are skipped; overnight minutes count)". On early-close dates the time
after the halt is not open time; on scheduled late-open dates with no overnight session the last open minutes before
08:30 are the previous trade date's day session. Readings: (a) the regular schedule on every date (Coder-A first
build); (b) the actual session of each date (Coder-B). Chosen: (b), the literal text. Fix in Coder-A. F1 level samples
still stop at the segment boundary (G2).

R-B3-FD3a. OFI terms (F2.8-F2.11, F3.1-F3.4) at the first book update after a skipped interval, whose predecessor
state lies in skipped time (the 07:45-08:30 pre-open book; the 13:20-19:00 close). Readings: (a) compute the term from
the pre-open state when both states are two-sided (Coder-A); (b) set it to 0 unless both states are valid books
(Coder-B); (c) make every window holding it invalid (TestCoder's suggestion); (d) the term is not part of any window's
sum and the window stays valid. Chosen: (d). Reason: P0.3 skips the pause, and the term is the net book change over
the pause (pre-open order flow and the opening uncross), so including it carries skipped-time information into the
window; (d) excludes it by the skip rule rather than imputing a value, and keeps the first open minutes, which (c)
would discard on every date for a term the text does not call uncomputable. Both coders change.

R-B3-FD3b. Within open time, an OFI term whose state or predecessor lacks a side or is marked bad. Readings: (a) the
window is not computable and the feature is invalid (G3: 0 and family flag 0; Coder-A); (b) the term is set to 0 and
the window kept (Coder-B). Chosen: (a). Reason: G3 lists "empty book side" among the cases that make a feature
uncomputable; (b) imputes. Fix in Coder-B.

R-B3-FD3c. Crossed or locked but two-sided, not-bad states inside open time. Chosen: the literal e_n formula (Coder-A).
Reason: the formula is defined on any two-sided state; 0.3's validity rule governs mids, not OFI. Fix in Coder-B.

R-B3-FD4. F3.11 "an add at the same price and side within 100 ms (ts_recv) after that price level, while it was the
touch, reached 0 displayed quantity through trades". Readings: (a) the window opens at the book update where an F3.10
sweep set leaves the pre-trade touch at 0 (Coder-A); (b) it opens at the record at which a level that is then the touch
reaches 0 through fills, deeper levels that become the touch during a sweep included, a level emptied by a cancel
excluded (Coder-B). Chosen: (b), the literal text (0.3 does not list F3.11 among the book-update-stepping features).
Fix in Coder-A.

R-B3-FD5. F3.9 "fills are not removals". Readings: (a) unconsumed fill lots of an order carry across event batches and
absorb its later cancels (Coder-A); (b) the fill accumulator clears at every F_LAST, so a cancel in a later batch is a
removal (Coder-B). Chosen: (b), the literal text. Fix in Coder-A.

R-B3-D1. An R record that carries F_MAYBE_BAD_BOOK. Chosen: the book stays bad until the next R (Coder-B; the snapshot
that carries the flag is not trusted). Fix in Coder-A (labels and features). Untriggered on the 20 dates.

R-B3-D2. Entry at a locked or crossed book on a date without limit prices. Chosen: entry_ok requires M_ZM(t) defined
(Coder-B; never enter on a state 0.3 calls invalid). Cannot arise on the discovery dates (limits on all 816). Fix in
Coder-A.

R-B3-D3/D4/D5 (no effect on the data). D3: F_TOB/F_MBP on MBO records mark the book bad (Coder-A, E.31 convention);
0 such records in Z1. D4: records before the first R emit no update (Coder-A) or an invalid one (Coder-B); no as-of
state in 08:35-13:20 differs. D5: sigma_ZM(D) undefined on a non-excluded date stops the label build (Coder-A).

R-L7. LightGBM early stopping (SearchCoder S11; SearchReview accepted it): the weighted multi_logloss of the inner block
is computed in float64 numpy instead of LightGBM's float32 metric, with LightGBM's own early-stopping callback. It is
the declared metric made deterministic; values agree to 1.6e-10 and the stopping iteration is the same.

R-L8. Tier B start point (ProofCoder Q3; ProofReview agreed): "continue the Tier A walk over all 300 configurations
ordered by the same key, gates ignored" is read as continuing from the position where Tier A stopped in the full
ordering. Q9: the proofs' report-only "best configuration" is the first in P8 order among configurations that traded.
(to be filled from reports/stage_e33_briefs/work/*_readings.md and implB/*_readings.md)
