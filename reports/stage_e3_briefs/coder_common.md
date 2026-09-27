# Common brief for MemberCoder-A-OpusXHigh and MemberCoder-B-OpusXHigh (Stage E.3, Task 2)

Worker file: worker-xhigh. Model: opus. Effort: xhigh. Written by the Stage E.3 lead, 2026-09-27 00:20 PDT.

## What you implement

The K2 members assigned to you (your own brief), exactly as reports/stage_e3_member_specs.md states
them. That file is the lead's reading of the frozen catalog entries (reports/stage_e0_catalog_K2.md).
Read section 0 (S0.1-S0.13), your members' sections, and section 10 (the readings L-01..L-22) in
full. Read the catalog only by the line ranges the specs cite. The spec governs. Change no rule, no
parameter, no time and no side. Add nothing a spec does not state: no filter, no stop, no size rule,
no extra guard.

## Read first (by section)

- strategy/stage_e/_template.py (the member contract, the static-check rules and the import allowlist)
  and strategy/stage_e/interface.py. The template's example exits at C-2. That is NOT K2-cp2-01's rule
  (L-07). Copy the template's structure, not its logic.
- screening/stage_e_freeze.py: check_member_source and MemberDecl. Every .py file you add under
  strategy/members/k2/ must pass check_member_source.
- How the engine calls a member: screening/stage_e_engine.py and screening/stage_e_rules.py (call_member,
  account_view, the refusals list at the top of stage_e_rules.py). Find out whether a single-leg member
  is called on minutes where its leg has no bar, and handle both cases.
- Test helpers: tests/_stage_e_canary_kit.py (rules_for, product_bars, ts_at, ...),
  tests/_stage_e_synthetic.py (product_frame, install_member_package) and how tests/test_stage_e_canaries.py
  and tests/test_stage_e_template.py run a member through the real engine on synthetic bars.

## Rules for the code

- One module per member under strategy/members/k2/, from the template. A dataclass taking `root`, with
  `name` = the label "<member id> <ROOT>" (S0.2), `legs`, `trading_windows` (S0.12), and module-level
  zero-argument factories `make_zt`, `make_zf`, ... for the exposures the member trades. Every
  constant is a named module constant or comes from the frozen tables (O, C, q_c, vendor tick).
- Imports only from the template's allowlist. No file reads, no mutation of anything imported.
- Prices in integer vendor ticks for every comparison (S0.10).
- Per-trade-date state resets when bar.trade_date changes. Never forward fill a None bar.
- strategy/members/__init__.py and strategy/members/k2/__init__.py exist, empty, created by the lead.
  Never create, edit or fill either.

## Tests

Unit tests on synthetic bars that pin each rule's decisions on hand-built cases. Where it matters, run
the member through the real engine (screening.stage_e_engine with StageERules via the canary kit's
rules_for). Cover, per member:
- entry and exit times: the decision minute, the fill bar and the side, checked on the engine's fills;
- the event-window behaviour: a release inside or next to the member's window (a
  ReleaseCalendar built in the test), showing what the engine's D9.5a fill guard does to a fill that
  lands in [release, release + 2 min);
- the flatten: a position still open at F is closed by the engine (for example an early-halt day for a
  port, or a synthetic F);
- a missing bar at a decision time: the entry bar (no trade), a signal bar (no trade), and an exit bar
  (the exit goes on the first later bar);
- for event members, a release that moved: a date whose instant differs from the usual time (for
  example an 11:30 ET auction) moves the decision minutes with it; a date not in the table is not
  traded;
- the member-specific guards in the spec (instrument guard, early halt, zero signal, one entry per day,
  and so on).
Also a table-pin test for your literal table (your brief says which), recomputed from its frozen source
in the test.
Tests use synthetic bars only. Never read a bar file (data/processed*, data/processed_step2, any parquet
of real bars), never run screening.stage_e_runner, and never call write_cluster_freeze on the
repository: it is write-once, and the lead calls it in Task 4. A test that needs a freeze writes it under
tmp_path.

## Running things

- Run pytest WITHOUT PYTHONPYCACHEPREFIX, as the repository's reference command does
  (`uv run pytest -q <files>`; three tests in tests/test_harness_freeze.py fail when that variable is
  set). Run only your own test file plus tests/test_stage_e_freeze.py and tests/test_stage_e_template.py.
  The lead runs the full suite once both coders are done. Use `nice -n 10`.
- Keep output short (`-q`, tail).
- No git commit, no git add, no push.

## When the spec is not enough

If you find a case the spec does not decide and a choice could change a trade, do not choose. Finish
everything the question does not touch, then return with the question stated precisely (file, case,
the options). The lead rules in writing and resumes you. Small implementation choices that cannot change
any trade (names, helper structure) are yours: list them in your report.

## Boundaries

- Touch only your own files (your brief lists them). The other coder works in the same directory in
  parallel: never edit, rename or delete their files, and do not import from their helper modules.
- No edits to any other file of the repository: no harness, no frozen file, no docs, no reports other than
  your own report.
- No Databento, no TopstepX, no web access, no bar data, no live/ or ops/, no REGISTRATION.md.
- Do not spawn workers.

## Output

- Your modules and your test file.
- A report, reports/stage_e3_coder_<A|B>.md. It gives each file with its sha256, and for each member a
  table: spec field, the code lines that implement it, and the tests that pin it. It also lists your
  implementation choices, anything you did not finish, the pytest command, and its last line verbatim.
- Return to the lead: the report path, a summary of at most 200 words, and any open question.
