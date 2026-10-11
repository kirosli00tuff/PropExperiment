# Stage E.20 rulings (lead)

All times PDT. One section per review or verification, in the order they happened.

## 1. Lead rulings on the H6 build's stop items (h6_build.md section 1; ruled 11:10-11:12)

- S1 (registry names): the frozen registry (screening/trial_registry.py lines 48-49) allows no hyphen
  in a label. The prompt's E20-H6-T1..T3 are registered as label E20H6, ids E20H6-T1, E20H6-T2,
  E20H6-T3 (the E16 pattern). Prereg section 8 and h6_rod/constants.py changed together.
- S2 (shortened days): the frozen engine's flatten on an early-close date is the early close minus
  Topstep's 30-minute lead in 2019-2025 (rules/sessions.py TOPSTEP_EARLY_CLOSE_LEAD), so F = C-30 and
  every shortened-day entry is refused by the engine. The prereg text (section 3, 7a) was corrected
  to say so; the code already followed the engine.
- S3 (engine lead-in): ENGINE_LEAD_IN_DATES = 1. Each engine run begins one equity trade date before
  its window, with no entry on it, so the first window date has the D9.7 prior-settlement reference
  like every other date. The text was silent; this reading makes every eligible date tradeable alike.
- T3_REGISTERED = True (the NQ reader's GEX ruling, accepted); GEX_CSV_SHA256 = E.14's copy.
- Two tests in tests/test_h6_rod_run.py that pinned the "as shipped" refusals were updated to the
  ruled state (the ruled names accepted, a hyphenated label refused; the CLI refuses a wrong freeze
  sha256 and no longer for T3_REGISTERED).

## 2. Rulings on the H6 review (reports/stage_e20_review_h6.md: APPROVE WITH FIXES; 0 BLOCKING, 3 SHOULD FIX, 7 NOTE; review file 15:29, returned 15:30; rulings 15:31-15:33)

The first H6Reviewer spawn (11:12) stopped at 11:21 on the session usage limit with no output; the
review was re-spawned fresh at 15:12 after the limit reset (pause 11:21-15:10).

| Finding | Severity | Ruling | Fix |
|---|---|---|---|
| H6R-1 post-marker exceptions leave the marker and no result | SHOULD FIX | accepted | h6_rod/run.py: a catch-all after the marker writes every test STOPPED with the traceback, then the result file; a test injects a RuntimeError after the marker (H6Coder follow-up) |
| H6R-2 header says GEX values unread; section 6 has a sign count | SHOULD FIX | accepted | header amended; section 6 records who (lead), when (10:56:48 PDT), what was read (date and gex columns, sign only) and the count's inputs |
| H6R-3 section 7a omits two of the NQ reader's differences | SHOULD FIX | accepted | 7a adds the prior close after an early-close day, the roll difference, and shortened days in T2's median |
| H6R-4 day after a futures-only holiday has no GEX row | NOTE | accepted (text) | section 3 names the case and its approximate count |
| H6R-5 T2 warm-up reading is literal | NOTE | no change | the literal reading stands (F2 allows only the 60 trade dates) |
| H6R-6 registry names differ from the prompt's | NOTE | no change | the mapping is stated in prereg section 8 and will be in the return and progress entry |
| H6R-7 manifest need not list the tests | NOTE | accepted | the lead's manifest builder lists tests/test_h6_rod_*.py and tests/_h6_rod_synth.py |
| H6R-8 two wording points | NOTE | accepted (first point) | section 1 now separates the paper's window (C-30 to C) from the traded window; the T2 attribution stays as F5 words it, corrected in 7a |
| H6R-9 member.trading_windows unused | NOTE | accepted | comment added (H6Coder follow-up) |
| H6R-10 weak CLI refusal test | NOTE | accepted | the test also asserts "freeze manifest" in stderr (H6Coder follow-up) |

Fixes applied and checked by the lead at 15:33: H6R-1, H6R-9, H6R-10 in h6_rod/run.py, member.py and tests/test_h6_rod_run.py (h6_build.md section 7); the text fixes in the prereg; `uv run pytest -q -p no:cacheprovider tests/test_h6_rod*.py`: 85 passed; ruff clean. No BLOCKING finding; no re-review needed: the lead read the H6R-1 change (run.py evaluate, the post-marker try block), the member.py comment, the new and changed tests, and wrote the text fixes.
