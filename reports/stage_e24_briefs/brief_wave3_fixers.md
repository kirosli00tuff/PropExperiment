# Briefs: Stage E.24 wave 3 fixers (worker-xhigh, opus), 2026-10-18 from about 11:56 PDT

Common: read reports/stage_e24_briefs/review_rulings.md (the lead's rulings) and your review file; fix every item
ruled for you, test first (a failing test, then the fix); run `uv run --frozen pytest -q -p no:cacheprovider
tests/test_forward_*.py tests/test_mdio_*.py`; `sha256sum -c --quiet reports/stage_e22_f1_files.sha256` at the end; no
network, no market data, no .env; never edit pyproject.toml, uv.lock, reports/stage_e24_prereg_F2.md (the lead's) or
any file outside your scope; another fixer works in parallel on the other scopes. No commits. Append "Wave 3 fixes
(<role>, <PDT times>)" to your report file: each item, file:line, the test, sha256 before/after. Latest stop 13:30 PDT.
Return: items fixed, items not fixed with the reason, test counts (<= 200 words).

## F2Fixer2-OpusXHigh
Scope: forward/runner_f2.py, strategy_f2.py, evaluate_f2.py, daily_f2.py, config_f2.json, tables_f2.json,
tests/test_forward_f2_*.py. Review: reports/stage_e24_briefs/f2/reg_review.md (C4b B1, B2, S1-S8, NOTEs). The text of
reports/stage_e24_prereg_F2.md sections 4-6 and 8 was revised at 11:50-11:55 PDT for those rulings: implement it
exactly (step 2 with C held fixed; step 5 scaling longs and shorts; r and the share update from the recorded close and
the session's actions, prev_close_mismatch flag at 1e-6 relative; late-action key with the amount or the source's id;
q_ex x k x amount; the cash-term wording of an ETF without a bar; the suspect-split guard; delisting after 10
sessions; SGOV replacing BIL after 10 sessions). For corporate actions over a span (prev, t] the runner calls the
source's corporate_actions(start, end, symbols) (AlpacaFixer guarantees any span); do not edit sources_alpaca.py.
Report: reports/stage_e24_briefs/f2/f2book_report.md (update the prereg-to-code mapping table too).

## AlpacaFixer-OpusXHigh
Scope: forward/etf_bars.py, forward/sources_alpaca.py, forward/orders_alpaca.py, forward/shadow_f2.json,
tests/test_forward_alpaca_*.py, tests/test_forward_etf_bars.py. Review: reports/stage_e24_briefs/alpaca/
adapter_review.md (C4a S1-S3, NOTEs). S1: corporate_actions(start, end, symbols) must return every action with
ex_date in the span however long (process_date padding, pagination) and fetch_day must deliver t's raw close even
when the symbol's previous bar is outside the request window; S2; S3; fix the stale "all" docstrings. Keep
DayFetch's fields (runner_f2 reads applied and flags). Report: reports/stage_e24_briefs/alpaca/alpaca_report.md.

## IBKRFixer-OpusXHigh
Scope: forward/ibkr_gateway.py, forward/sources_ibkr.py, forward/orders_ibkr.py, forward/daily_f1.py,
forward/shadow_f1.json, tests/_forward_ibkr_mock.py, tests/test_forward_ibkr_*.py. Review: reports/stage_e24_briefs/
ibkr/adapter_review.md (B5 B1, S1-S5, NOTEs) with the lead's rulings on S3 and S4 in review_rulings.md. Report:
reports/stage_e24_briefs/ibkr/ibkr_report.md.
