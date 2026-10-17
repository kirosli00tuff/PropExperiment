# Brief: HarnessReviewer-FableXHigh, Stage E.22 Part A, independent review of the v13 change set

Lead: E.22 (Opus 5.5, xhigh). You did not write this code; an Opus worker did. Your job is an independent,
adversarial review BEFORE the lead builds the v13 manifest and before any confirmation-window read.

## Inputs
- The change set: `git diff HEAD -- screening/ data/ tests/` (uncommitted working tree; ignore forward/, microbook/,
  tests/test_forward_*.py, tests/test_microbook_*.py, which belong to Part B), and the builder's report
  reports/stage_e22_harness_change.md.
- What it must do: reports/stage_e22_briefs/brief_harness_v13.md (items N1-N5, R1-R3), the v12 audit
  reports/stage_e22_briefs/partA_harness_audit.md, the lead's rulings reports/stage_e22_briefs/partA_rulings.md, the
  declaration reports/stage_e22_price_paths.json, docs/STAGE_E_DESIGN.md D2 (146-204), D4 (244-296), D5 (298-346),
  docs/NULL_CRITERIA_E.md, and the v5 precedent review reports/stage_e5_harness_review.md.

## Check, at least
1. Silent-failure risks in the price-path mapping (N1): could a mapped leg ever read the vehicle's own store, the wrong
   S_X, the wrong pinned sha, the full-size contract's tick value or cost table, or book on the wrong calendar? Is the
   research window provably untouched by the mapping? Are roll blackouts and the D4 union correct for a mapped leg?
   Does the supply count (confirmation_supply_days) use exactly the same window rule as the run (member_window)?
2. N2: can any set now compute an entry for a mapped vehicle from its own store, or produce a StartRuleConflict with
   K3/K4/K5/K6 files? Is GC's/NQ's V_ref from their own research volumes (D4)?
3. N3: the MES store path, its pinned sha, S = 2020-02-03, the enumerated 3-row ruling (are the rows really
   scheduled-closure prints; does any other mismatch still refuse?), roll metadata.
4. N4/N5: a plain Tier A/B trial without a record must still be refused; untestable/by-design run:false trials enter
   Holm at p = 1 and are not covered; k_holm validated 1..9 and echoed; no path lets K default silently.
5. R1: the marker is written only after every no-row check and before any bar row is read; it refuses if present;
   O_EXCL and 0o444; a STOPPED record after the marker on any exception. R2 dry run writes nothing and runs no engine.
   R3 records registry N without refusing.
6. Tests: do they pin each behaviour (including refusals)? Run `nice -n 10 uv run python -m pytest -q -p
   no:cacheprovider tests/test_stage_e_*.py` and any test importing a changed module; report counts.
7. Manifest scope: will the v13 manifest's file and test patterns pick up anything from forward/, microbook/ or the
   Part B tests (they must not)? Did anything outside the allowed files change (`git status --short`, `git diff --stat`)?
8. Anything that would let a confirmation run differ from "each member exactly as its cluster freeze defines it".

## Boundaries
Read-only on code (do not fix; report). No confirmation-window run or bar read, no manifest build, no commit, no edit
of any tracked file. Your output only: reports/stage_e22_harness_review.md.

## Output
reports/stage_e22_harness_review.md: findings numbered and classed BLOCKING (must fix before v13), SHOULD FIX, NOTE;
each with file:line, the failure scenario, and a suggested fix; plus a list of what you verified and how. Return the
path, the counts by class, and a summary of at most 200 words.
