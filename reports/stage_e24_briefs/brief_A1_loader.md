# Brief A1: LoaderCoder-OpusXHigh (worker-xhigh, opus). Stage E.24 Part A (V41 loader fix)

Objective: make a multi-day read load each store only up to the read window's last bar (no later bar ever in memory),
and make multi-day books write per-unit and per-fill files as E.21 did, without changing the behaviour of any frozen
member, freeze or earlier stage's code path.

Inputs: docs/prompts/STAGE_E.24.md Part A; docs/DECISIONS.md V41 (lines 745-761); reports/E.23_RETURN.md section 7
item 5 (lines 688-692); reports/stage_e23_briefs/verify/verdict_verify.md NOTE-2 and NOTE-5 (lines 184-196);
base_rules/context.py, base_rules/store.py, multiday/*, trigger_hold/*; how E.21 wrote per-unit/per-fill files
(multiday/ run or book code and reports/stage_e21_* outputs); E.23's recorded discovery result
reports/stage_e23_runs/discovery/discovery_result.json.

Steps:
1. Pin inventory FIRST, written to reports/stage_e24_briefs/loader/pins.md: for every file you may touch, whether it is
   pinned by: the harness manifest (reports/stage_e2b_harness_freeze.json "files"); the E.16 guardrail line
   `git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md` (must stay exit 0);
   reports/stage_e20_h6_freeze.json; reports/stage_e1_freeze.json; reports/stage_e21_freeze.json and the files its
   spec/prereg pin; reports/stage_e23_freeze.json (config, spec, prereg entries) and any code sha256 they list; cluster
   freezes; the E22-F1 list reports/stage_e22_f1_files.sha256. If the fix needs a pinned file changed, STOP Part A,
   change nothing, and report which file and why (the lead logs it).
2. Design the smallest change in unpinned files (base_rules/context.py only if unpinned, else multiday/ or a new
   module). The bound must be enforced in code (stores are read with a filter or truncation at the window's last bar
   BEFORE rows reach memory where the store format allows, e.g. a pyarrow filter or row-group pruning; if only
   post-load truncation is possible, say so plainly) and asserted (a check that no loaded row is dated after the bound).
3. Per-unit and per-fill files for multi-day books, in E.21's format, written by the book code for future reads.
4. Tests (new files, TDD): the bound (a synthetic store with rows after the bound: never returned, never loaded where
   the format allows), the files written, and equality of results with and without the change on synthetic data.
5. Proofs, all quoted in your report: (a) the E.21 and E.23 test suites unchanged and passing
   (tests/test_multiday_*.py, tests/test_trigger_hold_*.py, tests/test_base_rules_*.py; `uv run pytest -q
   -p no:cacheprovider <files>`); (b) a replay of E.23's discovery books in a scratch directory under
   /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/c2dca792-060d-4694-91ef-4a6f3f808f1d/scratchpad/
   loader_replay/ in test mode, with no marker written and no file under reports/ or ledger/ written, every number
   compared with discovery_result.json (exact or to the last float bit; list every mismatch), plus the max loaded date per
   store showing nothing after 2019-04-30 was loaded. This replay re-reads E.23's own already-read window only.

Boundaries: never read W_cf (2019-05..2024-02) bars, holdout-2, the embargo, the research window, MES sealed stores or
anything dated 2024-03-01 or later; the replay touches only the ext2010 stores of E.23's discovery roots. Never write
markers, results, freezes, registrations or ledgers; never rerun trigger_hold/run.py's real phases. Do not touch
forward/, live/, ops/, sim/, rules/, screening/, data/holdout.py, pyproject.toml or uv.lock (harness v13 pins
pyproject.toml and uv.lock). Compute: check `free -m` first; run the replay at nice 10 only when at least 4 GB is
available and reports/stage_e24_briefs/pytest_start.out ends with an "rc" or "KILLED" line (the start suite is
running until then; wait for it with a one-off check every few minutes, never a pgrep -f loop on your own command
line). Other workers are writing forward/*_ibkr.py, forward/*_alpaca.py and forward/*_f2.py at the same time: do not
touch them. No commits.

Output: the code change and tests; reports/stage_e24_briefs/loader/loader_report.md (diff summary with file list and
sha256 before/after, pins.md result, proofs verbatim, what you could not do); replay output in the scratch dir plus
reports/stage_e24_briefs/loader/replay_compare.json (number of values compared, mismatches, max loaded date per store).
Return: the report path, a summary of at most 200 words, and anything unfinished.
