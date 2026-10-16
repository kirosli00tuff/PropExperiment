# Brief: RegReviewer-FableXHigh, Stage E.22 Part B, independent review of the E22-F1 forward registration

Lead: E.22 (Opus 5.5, xhigh). You review BEFORE the registration is frozen and registered (N 532 -> 533). You did
not write the registration (the lead did) or the code (two Opus workers did).

## Inputs
- The registration draft: reports/stage_e22_prereg_F1.md.
- The prompt's requirement: docs/prompts/STAGE_E.22.md items B1-B5 (lines 93-137) and SCOPE (139-154).
- The lead's spec and rulings: reports/stage_e22_briefs/lead_spec_B.md (S0-S8), the Carver extract
  reports/stage_e22_briefs/carver_sources.md (quoted constants and the November 2021 greedy algorithm).
- The code the registration freezes: forward/core.py, forward/strategy.py, forward/runner.py, forward/ledger.py,
  forward/sources.py, forward/rolls.py, forward/history.py, forward/evaluate.py, forward/report.py,
  forward/config_f1.json, forward/rolls_f1.json (and any costs table file), forward/README.md; tests
  tests/test_forward_*.py. The historical study that set the constants: microbook/ and reports/stage_e22_microbook.md.

## Check, at least
1. Does the text register exactly what B4 asks (rule, universe, rounding method, start-date rule, 36-month horizon,
   the bar p <= 0.05 one-sided on the forward daily net series AND net Sharpe >= 0.3, a 6-monthly look that changes
   nothing, N 532 -> 533)? Anything ambiguous enough to allow a choice after data arrive (forking paths)?
2. Does the code implement the text (the code governs where they differ, so every difference matters): the bar in
   forward/evaluate.py (Newey-West lag 10, Bartlett, one-sided p from the normal, Sharpe x sqrt(252), PASS iff both;
   refusal before 36 months; interim with no t/p), missing-day handling, start and horizon arithmetic, the ledger's
   refusals.
3. Integer arithmetic and sizing in forward/core.py and forward/strategy.py: Carver's formulas and constants as cited
   (scalars, caps, FDM/IDM, vol blend, position formula, the yield micros priced in yield with $10/bp), simple rounding,
   and the greedy optimiser against the November 2021 description (start point, step, stop rule, shadow cost, buffer,
   adjustment factor). Look for off-by-one, sign, unit (dollars vs contracts vs fraction of capital), look-ahead
   (a settle(t) signal must never earn P&L at t) and silent NaN propagation.
4. Constants frozen in config_f1.json: each has a source; FDM and IDM values are what the study computed; nothing is
   left to be decided after the start.
5. Anything in the registration that the prompt forbids (data fetch, purchase, a p-value on historical data, an
   interim look that can stop or change the test).
6. Power statement in section 8: arithmetic correct?
7. Run `nice -n 10 uv run python -m pytest -q -p no:cacheprovider tests/test_forward_*.py`; report counts.

## Boundaries
Read-only. No edits to any file except your output; no data reads from data/; no network; no commit.

## Output
reports/stage_e22_reg_review.md: findings numbered and classed BLOCKING (must fix before the freeze), SHOULD FIX, NOTE;
each with file:line or section, the failure scenario and a suggested fix; plus what you verified and how. Return the
path, the counts by class, and a summary of at most 200 words.
