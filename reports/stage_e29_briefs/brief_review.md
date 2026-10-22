# Brief: BasketReviewer-OpusXHigh (Stage E.29, independent review)

You review work you did not write, in a fresh context. Read only the files named here (and the code they import).
Read CLAUDE.md's "Context hygiene" and "Compute limits" sections first. Times in PDT from `date`. Do not spawn
agents. Do not edit any file except your own outputs.

## Files you check
- The binding declaration: reports/stage_e29_model.md (sha256 must be f393759f4af712a889646a7a4cdb2c45f2f3b8496a6403be56467de7eb0d8164; check it).
- The code: reports/stage_e29_briefs/work/basket/ (e29_basket.py, e29_run.py, test_e29_basket.py, LOG.md and the
  table script), which imports E.28's model read-only from reports/stage_e28_briefs/work/A3_econ/ and prop_econ/.
- The results: reports/stage_e29_briefs/E29_cells.json and E29_tables.md.
- The reference: reports/stage_e28_briefs/A3_econ.json ("pairs" records with code "QM") and
  reports/stage_e28_briefs/A3_econ.md sections 2 to 4 (E.28's model and the five firms' rule mappings).

## Tasks (Z5 of the stage prompt)
1. B0 against E.28. Recompute B0 (QM alone) at all five firms with the E.29 code and compare with E.28's records:
   mu*_lim, mu*_mkt, mu10K, cost per attempt. They must match exactly. Any mismatch is BLOCKING.
2. Two random cells with a different seed. Choose two non-B0 cells at random (state the RNG and seed you used to pick
   them; at least one with rho > 0), re-run each with a different master seed (for example 20261022) and the same
   search, and compare the break-even and mu10K analogue with E29_cells.json. Report the differences in grid steps.
   A difference of more than about 3 grid steps (0.03 in k or ticks), or a sign change in the "beats B0" flag, is
   at least SHOULD FIX and needs an explanation.
3. The rule mapping on the combined account. Check that every firm rule E.28 mapped (A3_econ.md section 3 and 4)
   acts on the combined daily P&L as the declaration's section 3 and 4 says: combined M and S formula (including
   rho), the intraday min (and max for Bulenox) on the combined path, daily loss limits, trailing drawdowns,
   consistency, payout rules, fees and API; and that the position limits and the Topstep news window are applied
   and logged as declared (Topstep B3 at the 2-lot XFA tier: primary form and the drop-MGC sensitivity). Check the T
   split, the edge settings (i) and (ii) (including the extended alone break-evens of section 5) and the market case
   and best-basket rule of section 6.
4. Spot-check the tables against the JSON (at least 10 numbers) and the "beats B0" flags against section 7's rule.
5. Run the E.29 test file and report the counts.

Compute: nice 10, at most 4 processes, threads 1 each, check `free -m` first. Keep printed output short.

## Output
reports/stage_e29_briefs/R_review.md: a verdict line (GO, GO WITH FIXES, NO GO), then numbered items marked
BLOCKING, SHOULD FIX or NOTE, each with the evidence (file:line or the command and its output tail). Scripts under
reports/stage_e29_briefs/work/review/. Return the path, the verdict, the items in at most 200 words, and anything
you could not check.
