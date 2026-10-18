# Briefs: Stage E.24 wave 2 fixers (worker-xhigh, opus). Resumed 2026-10-18 11:17 PDT after a reboot.

Common: the earlier coder is gone; read its report and the current code by section; TDD (a failing test first);
run `uv run --frozen pytest -q -p no:cacheprovider <your tests> tests/test_forward_*.py tests/test_mdio_*.py`; check
`sha256sum -c --quiet reports/stage_e22_f1_files.sha256` at the end; no network, no market data, no .env; never edit
pyproject.toml, uv.lock, reports/stage_e24_prereg_F2.md or files outside your scope; no commits. Append a section
"Wave 2 fixes (<role>, <PDT times>)" to the report named below: each fix with file:line, the test that proves it, and
sha256 before/after of every file you changed. Return: what you fixed, test counts, anything not done (<= 150 words).

## LoaderFixer-OpusXHigh (scope: mdio/, tests/test_mdio_*.py; report reports/stage_e24_briefs/loader/loader_report.md)
Fix the two SHOULD FIX findings of reports/stage_e24_briefs/loader/loader_review.md: (1) mdio/bounded.py:144
_keep_mask drops rows with a null trade_date silently where the frozen path refuses: refuse (raise) exactly as the
frozen path does; (2) read_root_books (mdio trigger_books.py:40-47) does not call check_bounded: make the bound
mandatory on that path. Address NOTEs only if cheap and safe; list the rest. Also re-run the E.21/E.23/base_rules
suites (tests/test_multiday_*.py tests/test_trigger_hold_*.py tests/test_base_rules_*.py) and the E.16 guardrail
`git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md`. Do not re-run the
data replay unless a fix changes the read path's numbers (then: scratch dir, test mode, E.23's ext2010 discovery
stores only, nothing after 2019-04-30, nice 10).

## F2Fixer-OpusXHigh (scope: forward/runner_f2.py, strategy_f2.py, evaluate_f2.py, daily_f2.py, config_f2.json,
## tables_f2.json, tests/test_forward_f2_*.py; report reports/stage_e24_briefs/f2/f2book_report.md)
Implement the lead's rulings on Q21-Q23 of f2book_report.md against reports/stage_e24_prereg_F2.md section 6 (the
late corporate-action bullet was revised at 11:20 PDT; re-read it): Q23: each record's ca_applied stores every action
counted when the session was recorded WITH its type, ex_date and amount or ratio (forward/sources_alpaca.py's
DayFetch.applied already carries CorporateAction objects; do not edit sources_alpaca.py), and corrected_rows computes
a session's corrected return from ALL its actions (recorded and late) with the section 6 formula
k x (rawclose(t) + D) / rawclose(prev) - 1; Q21: a late BIL action of either kind (distribution or split) books
-L_ex x dr_c with dr_c = corrected minus recorded BIL return of that session; Q22 accepted as implemented (mixed feeds
-> abandoned, no verdict). Tests: a late BIL split (dr_c from the split), a late distribution on a session whose
recorded r already contained a split (exact corrected return), and the earlier Q15/Q16/Q17 tests still green. Mark
Q21-Q23 RULED in the report.
