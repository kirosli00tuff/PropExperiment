# Common brief for MemberCoder-A-OpusXHigh and MemberCoder-B-OpusXHigh (Stage E.4 Part 2, K5, Task 2)

Worker file: worker-xhigh. Model: opus. Effort: xhigh. Written by the Stage E.4 lead, 2026-09-27 05:25 PDT.

## What you implement

The K5 members assigned to you (your own brief), exactly as reports/stage_e4b_member_specs.md states
them. That file is the lead's reading of the frozen catalog entries (reports/stage_e0_catalog_K5.md).
Read section 0 (S0.1-S0.14), your members' sections, section 10 (the E.3 and K4 readings adopted and
K5-L-01..K5-L-12) and section 11 (the release check) in full. Read the catalog only by the line ranges the specs cite. The spec governs. Change no rule, no
parameter, no time and no side. Add nothing a spec does not state: no filter, no stop, no size rule,
no extra guard.

## Read first (by section)

- strategy/stage_e/_template.py (the member contract, the static-check rules and the import allowlist)
  and strategy/stage_e/interface.py. The template's example exits at C-2. That is NOT K5-cp2-01's rule
  (L-07). Copy the template's structure, not its logic.
- screening/stage_e_freeze.py: check_member_source and MemberDecl. Every .py file you add under
  strategy/members/k5/ must pass check_member_source.
- How the engine calls a member: screening/stage_e_engine.py and screening/stage_e_rules.py (call_member,
  account_view, the refusals list at the top of stage_e_rules.py). Find out whether a single-leg member
  is called on minutes where its leg has no bar, and handle both cases.
- Test helpers: tests/_stage_e_canary_kit.py (rules_for, product_bars, ts_at, ...),
  tests/_stage_e_synthetic.py (product_frame, install_member_package) and how tests/test_stage_e_canaries.py
  and tests/test_stage_e_template.py run a member through the real engine on synthetic bars.

## Rules for the code

- One module per member under strategy/members/k5/, from the template. A dataclass taking `root`, with
  `name` = the label "<member id> <ROOT>" (S0.2), `legs`, `trading_windows` (S0.12), and module-level
  zero-argument factories `make_mgc`, `make_mhg` for the exposures the member trades. Every
  constant is a named module constant or comes from the frozen tables (O, C, q_c, vendor tick).
- Imports only from the template's allowlist. No file reads, no mutation of anything imported.
- Prices in integer vendor ticks for every comparison (S0.10).
- Per-trade-date state resets when bar.trade_date changes. Never forward fill a None bar.
- strategy/members/__init__.py and strategy/members/k5/__init__.py exist, empty, created by the lead.
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
  example a Thursday 12:00 ET WPSR or a Wednesday 12:00 ET storage report) moves the decision minutes with it; a date not in the table is not
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
- A report, reports/stage_e4b_coder_<A|B>.md. It gives each file with its sha256, and for each member a
  table: spec field, the code lines that implement it, and the tests that pin it. It also lists your
  implementation choices, anything you did not finish, the pytest command, and its last line verbatim.
- Return to the lead: the report path, a summary of at most 200 words, and any open question.

## K5 additions (Stage E.4 Part 2)

- Pattern, not source of rules: E.3's K2 modules (strategy/members/k2/) and Part 1's audited K4 modules
  (strategy/members/k4/: cp1.py, cp2.py, cp3.py, ovr.py, _port_common.py, _calendar.py, _event_common.py, and
  tests/test_e4_k4_members*.py) show working code against this engine, including R-T2-1 (a bar's open is read through
  `dataclasses.asdict(bar)["open"]`, since the static check bans the name `open`). Copy into k5; never import from k2
  or k4. The rules come only from the K5 specs.
- K5-ovr-01 carries the same rule text as K4-ovr-01 (E.1 F-7) with K5's decision clock: start from k4/ovr.py and
  change only the clock (t = O + 60k while t <= C), the calendar table (METALS_FULL_SESSIONS) and the value floor
  (80% of the possible values: 80 of 100 on MGC, 64 of 80 on MHG; K5-L-06). The auditor diffs the two modules.
- Extra test cases required (the prompt's Task 2): the C10-style guard where a percent return is computed (ovr); D9.7's
  price-limit exit (an engine-forced exit: no duplicate exit, no re-entry that trade date or decision time); a moved and
  a dropped event (a 5-hour-week auction instant moves the decision minutes; a date not in the table is not traded).
- Test file names: tests/test_e4_k5_members_<a|b>*.py (each name starting tests/test_e4_k5_members).
- The harness is frozen (v4, 82ae8536...); do not touch it.
