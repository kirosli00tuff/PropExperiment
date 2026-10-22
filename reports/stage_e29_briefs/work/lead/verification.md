Independent review (Z5): BasketReviewer-OpusXHigh, Opus 5.5 at xhigh in a fresh context (Fable is not on the Pro
plan, OC-2), 02:53 to 03:13 on 10-22, reports/stage_e29_briefs/R_review.md. Verdict GO WITH FIXES: 0 BLOCKING,
2 SHOULD FIX, 10 NOTEs. Both SHOULD FIX items were fixed before this return.

The prompt's checks:
- B0 against E.28 (review item 2): B0 setting (ii), limit and market, recomputed at all five firms. Every value
  equals A3_econ.json exactly (mu*_lim / mu*_mkt / mu10K / cost per attempt): Topstep 0.32 / 1.32 / 0.54 / 50.53,
  Lucid 0.33 / 1.33 / 0.77 / 120.87, Tradeify 0.43 / 1.43 / 0.75 / 95.83, MFFU 0.35 / 1.35 / 0.90 / 153.00,
  Bulenox 0.72 / 1.72 / 1.06 / 175.00. Every evaluation row is bit-equal to the stored cell. Test (a) checks the
  same thing and passes.
- Two random cells under a different seed (item 3): a seeded draw over the 156 computed non-B0 limit cells picked
  Bulenox B3 (ii) at rho 0.25 and 0.75. They were rerun with master seed 20261022 instead of 20261021, so every draw
  was new. mu*_QM moved from 2.05 to 2.04 and from 1.94 to 1.93; mu10K from 2.98 to 2.98 and from 3.02 to 3.01.
  Every change is at most 1 step, against a bar of 3, and no beats flag changed. B0 Bulenox (ii) under the new seed
  reproduces 0.72 / 1.06.
- Rule mapping on the combined account (item 4): pass. The combined law enters E.28's funnel through the same call
  as E.28's pair law, so every mapped rule acts on the combined account.
- Tables against JSON (item 6): 994 numbers in the main tables and 1,494 in the reporting tables, 0 mismatches. All
  160 beats flags were re-derived on integer grid indices: 0 mismatches, 27 yes.
- Tests (item 5): 11 passed (work/basket/test_e29_basket_final.out, 66 s), rerun by the reviewer.

The SHOULD FIX items:
- Item 7, grid confirmation (A3_econ.md 2.4) not run: fixed. The reviewer confirmed 21 cells and 3 alone records.
  The lead confirmed the other 211 records with the reviewer's code (work/confirm/confirm_all.py calls
  review_run._work; same code, seed and draws; 03:13 to 04:19, rc 0, no traceback). Result: 235 of 235 records,
  470 thresholds, 0 moved (stage_e29_briefs/E29_confirmation.md).
- Item 8, no vanish rho produced: fixed. E29_confirmation.md section 7 gives, for each firm, basket and setting, the
  beats flag at each grid rho on confirmed values and the rho where it turns off; section 3.4(b) cites it.

NOTEs carried into the text:
- Item 9: flags that rest on exactly 2 steps (Bulenox B1 (i) at rho 0.25, Bulenox B3 (i) at rho 0) are within
  seed noise; 3.4(a) says so.
- Item 10: Topstep B3 sits at the 2-lot tier on 94 to 96% of funded days near the threshold. The drop-MGC
  sensitivity is in 3.3, and it does not change B3's flag.
- Item 11: Lucid's B0 setting-(i) k* is 0.98 on the k lattice, and Lucid's flags are judged against it.
- Item 12: cell_id omits the mode. The confirmation pass wrote only to work/review/out and work/confirm/out, never
  to work/basket/cells.

Lead checks:
- The 27 yes flags in the vanish table equal the 27 starred cells in 3.3.
- Every number in 3.3 to 3.5 was checked against compact_tables.md, which compact.py generates from
  E29_cells.json. The check corrected four statements in the lead's draft: B1's mu10K drop is 7 to 17% (not 8 to
  17%) at four firms and 1 to 3% (not 1 to 4%) at Bulenox, and two places said "top four firms" where "all firms
  but Bulenox" was meant.

Not checked by anyone: the correlations in 3.2 (reference only, not an input), and the lead's per-trade sigma
reading in 3.4 (OC-14). The reviewer checked MGC's 6.37-tick alone break-even only for consistency with E.28's
model.
