# Brief: FeatureCoder-OpusXHigh (Stage E.33b, Coder-A: the FD7 fix and the 20-date rebuild)

You are a worker (Opus 5.5, xhigh) for the E.33b lead, in a fresh context. You take over Coder-A's feature code from
Stage E.33 (that worker is gone). Do not spawn workers; do not use AskUserQuestion; decide conservatively, log, continue.

Read first (by section, never whole large files): your E.33 brief reports/stage_e33_briefs/briefs/brief_FeatureCoder.md
(its independence rule binds you: never read anything under reports/stage_e33_briefs/work/implB/), INTERFACE.md
(section 2 rules), work/FeatureCoder_readings.md, work/B3_agreement.md (the FD7 bullet and table row),
reports/stage_e33_protocol_readings.md entries R-B3-FD5 and R-B3-FD7, protocol P4 F3.9 and F3.11.

## Objective
1. Apply ruling R-B3-FD7 in pipeline/feat33.py: fill lots of an F record are attributed by order id within the event
   batch whether or not the order is in the book when the F record arrives (drop the `if oid in orders` gate on F
   records); keep the per-batch clear at F_LAST (R-B3-FD5) and change nothing else. FD6 is ruled for your side as it
   stands (a record opens the F3.11 refill window only when its whole reduction is fill lots and the level is then
   empty): do not change it, but add a test that pins it if none exists.
2. Hand-built tests in pipeline/tests/test_feat33.py: an F record for a not-yet-booked order, then its A and C in the
   same batch (the C is a fill, not a removal); the same lots in a later batch (a removal). Run the feature tests
   (`uv run pytest -q -p no:cacheprovider <test files>`, nice 10) and report counts.
3. Rebuild the 20 B3 dates with every look-back date they need (the B3 dates rule R-L5; about 328 pass-1 dates) on the
   new code, to a new code_sha12 store under DERIVED/features/. Processes: 1 while `pgrep -f run_proofs33` finds the
   proof job, up to 4 when it does not (the builder resumes from DONE markers, so you may restart it with more
   processes when the proofs end); `free -m` first, stop below 2 GB available; nice 10.
Do not touch any other file, lab33, the search, the proofs or implB. If anything else looks wrong, report it; do not fix.

## Return
The new feat33 sha256 and code_sha12, the store path, test counts, rebuild wall time and process counts, a summary of
at most 200 words, and anything unfinished. Append a dated note to work/FeatureCoder_readings.md.
