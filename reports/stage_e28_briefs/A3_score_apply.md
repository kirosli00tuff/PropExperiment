# A3 score.py: lead rulings applied (ScoreApplier, 2026-10-21)

Script: reports/stage_e28_briefs/work/A3_facts/score.py. Tests: work/A3_facts/test_score.py. Rulings file
A3_lead_rulings.json, sha256 82581c92030d4664... (checked by a new guard, like the spec hash). Run at 16:06 PDT after
A3_econ.json appeared (waited from 15:14; the 45 minute limit passed at 15:59 and I waited 7 more minutes because
EconCoder's grid check was at 119 of 119 pairs).

## Code changes
- `load_rulings()` reads the rulings file and returns mng_gate, D_unknown, E_unknown, jump_transfer, C6_floor; exits
  REFUSED on a missing file or a sha256 mismatch. `variant_params(name, rulings)` builds each variant by flipping one thing.
- OC-A3-1: `apply_variant` sets MNG gate_60_dates to True (flag lead_ruling_OC-A3-1). 5YY and 30Y stay unknown, excluded.
- OC-A3-2: `d_score(room, unknown=1)`: unknown D scores 1 (was 0).
- OC-A3-3: `e_score(..., unknown=1)`: each s() component with unknown mu scores 1 (was: whole E = 0). E still flagged u.
- OC-A3-6: the sibling big-move counts (facts variants.C4_jump_transfer) are applied in the primary and in every variant
  except C4_no_transfer. The old C4_jump_transfer variant is therefore the primary and was removed as a duplicate.
- OC-6/OC-7: `score_layer1(..., c6_floor=2)` raises every C6 below 2 to 2 (C25's 0 included); C6_rated keeps the rating.
- New variants: D_unknown_0, E_unknown_0, C4_no_transfer, C6_as_rated (no floor, C25 = 0). Kept: OC1_off, C4_conservative,
  QV_proxy_only, OC2_published, now layered on the new primary (OC1_off therefore gives E = 1, D = 1 where unknown).
- Added `find_ties` (ties section in the md, `ties` in the json), rulings sha256 in the json, a C6 "(rated x)" marker in
  the md. Spec-hash guard, anchors, weights and the tie rule are unchanged.

## Tests
`uv run python -m pytest -q reports/stage_e28_briefs/work/A3_facts/test_score.py`: 110 passed. Two old tests changed to
the new semantics (d_score(None) = 1, e_score with unknown = componentwise 1, OC1_off pipeline E = 1 and D = 1). New
tests: rulings load and hash guard, one-flip variant parameters, MNG gate (5YY and 30Y stay unknown, input not mutated),
D unknown 1/0, E component unknown 1/0, jump transfer primary vs no-transfer, C6 floor and C6_as_rated (C25), C1 untouched
by the floor, tie report.

## Outputs
A3_ranking_table.json and .md regenerated: COMPLETE, 20 Layer 1 survivors, 126 listed pairs, 71 ranked.
Unresolved u flags: E unknown (no econ mu) for 9 pairs (SIL, SI, MET on the firms listing them), D unknown for the same 9.

