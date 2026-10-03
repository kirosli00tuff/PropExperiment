# Brief: ReviewFixCoder-OpusXHigh, the code-review fixes (Part 2)

You are ReviewFixCoder-OpusXHigh in Stage E.11 of the PropExperiment repo
(/home/kiros-li/Documents/GitHub/PropExperiment). Read CLAUDE.md first (invariants, context hygiene,
compute limits). Synthetic data only. Apply the code fixes the lead ruled on the code review.

Read:
- reports/stage_e11_rulings.md, Part 2 (the table);
- reports/stage_e11_review.md, Part 2, findings C-01 to C-12 (each has file:line, the failing
  scenario and a suggested fix): `awk 'NR>=565 && NR<=700' reports/stage_e11_review.md`;
- reports/stage_e11_interfaces.md section 0 (the rules);
- the code you change, by grep and line ranges.

## Fixes (each with a test unless marked "label")
- C-01 constants fingerprint across all resumable state; hash partial keywords; a test flipping
  COST_GATE_READING with monkeypatch must raise the mismatch error.
- C-02 risk_unknown skip, counted; keep the raise for a pair absent from the table; a test with a
  vehicle planted in two blocks only.
- C-03 an empty-schedule path row with empty_schedule True.
- C-04 per-split sigma and loss on each split's candidates in _nested_schedule; join_risk prefers
  row-level values; PortfolioMember and _pack follow. Test: a schedule row's sizing uses its own
  split's table, not the all-blocks table. The final model's research-window schedule keeps the
  all-blocks table.
- C-05 cost-bucket drop counts in Panel.counts.
- C-06 exit_ts <= 0 counts as missing.
- C-07 the ridge fit under one BLAS thread (threadpoolctl if importable in this environment; check
  with `uv run python -c "import threadpoolctl"`; never add a dependency to pyproject/uv.lock). If it
  is not importable, record the thread count in the unit record and document it.
- C-09 the tier read at the prior session's close, before the payout debit.
- C-11 labels "kill switches off" on the engine record and the combined-MLL audit (report keys and
  docstrings). Label only.
- C-12 a shifted-origin variance in normalize.py; the existing normalizer tests still pass.
  Add one test with a feature of mean 1e6 and sd 1.

## Then
Run all ml_route_v2 tests: `nice -n 10 uv run pytest -q tests/test_ml_v2_*.py`, output to
reports/stage_e11_briefs/reviewfix_pytest.out, tail only. All pass, with only the C-1 strict xfail.

## Boundaries
- Edit only ml_route_v2/ files, tests/test_ml_v2_*.py and tests/ml_v2_fixtures.py.
- constants.py: additions only.
- Do not edit data/config.py or docs/ACCESS.md (C-10 is deferred), the design, the interfaces,
  the review or the rulings.
- Never touch the harness directories, data files, .env or result reports.
- No full suite, no agents, no commits, no network.

## Return
The files changed; the test result line; where each fix lives and its test names; anything not
done as ruled, with why; a summary of at most 200 words.
