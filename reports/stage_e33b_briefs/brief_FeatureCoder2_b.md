# Brief: FeatureCoder2-OpusXHigh (Stage E.33b, Coder-B: the FD6 and N10 fixes and the 20-date rebuild)

You are a worker (Opus 5.5, xhigh) for the E.33b lead, in a fresh context. You take over Coder-B's independent
feature implementation from Stage E.33 (that worker is gone). Do not spawn workers; do not use AskUserQuestion.

Independence binds you: read your E.33 brief reports/stage_e33_briefs/briefs/brief_FeatureCoder2.md first and keep
its rule (never read anything under reports/stage_e33_briefs/work/pipeline/ except guard33.py and data33.py; never
read the other coders' briefs or readings files). Also read INTERFACE.md (section 2 rules), implB/FeatureCoder2_readings.md,
and protocol 0.3, P4 F3.9 and F3.11.

## The lead's rulings you implement (reports/stage_e33_protocol_readings.md, 2026-10-28 09:12 PDT)
- R-B3-FD6 (F3.11): a single record opens the 100 ms refill window only if its WHOLE reduction is fill lots of its
  event batch and the level, while the touch, is then at 0 displayed quantity. A record that removes fill lots and a
  voluntary remainder at once (an order partly filled and the rest cancelled or modified away in one record) does not
  open a window; its non-fill remainder still counts as a removal for F3.9. Today implB/replayB.py `reduce` opens the
  window when any part is fill lots.
- R-B3-N10 (= R-B3-D1): for an R record that carries F_MAYBE_BAD_BOOK (or F_TOB/F_MBP), clear the book first and then
  mark it bad, so the book stays bad until the next R. Today replayB.py marks before the clear and the clear resets it.
Change nothing else.

## Objective
1. Apply both in implB (replayB.py and any caller), with hand-built tests in implB/tests/ (a mixed fill-plus-cancel
   record at the touch: no refill window, remainder counted as a removal; an all-fill emptying record: window opens;
   an R with the flag: the book is bad after it). Run implB/tests, nice 10, and report counts.
2. Rebuild your 20 B3 dates (rule R-L5 applied to your own OOF list) with their look-back dates on the new code to a
   new code-hash store under DERIVED/implB/features/. Processes: 1 while `pgrep -f run_proofs33` finds the proof
   job, up to 4 when it does not; `free -m` first, stop below 2 GB available; nice 10.

## Return
New sha256 of each changed file and your code hash, the store path, test counts, rebuild wall time, a summary of at
most 200 words, anything unfinished. Append a dated note to implB/FeatureCoder2_readings.md.
