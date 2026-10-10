# Brief: DiffReviewer-FableXHigh (Stage E.18 Step 2)

You are an independent, adversarial reviewer (worker-xhigh on Fable). Work in
/home/kiros-li/Documents/GitHub/PropExperiment. All times PDT from `date`. Follow CLAUDE.md's context-hygiene rules:
read files by section (grep, line ranges), keep command output short, never load a large JSON or log whole.

## Objective (one)

Decide whether C1b's text and code, as written by the lead, hold THE ONE FIX of docs/prompts/STAGE_E.18.md and
nothing else, and whether any second contradiction of C1's kind remains, BEFORE C1b is frozen and registered.

## Inputs

- The prompt: docs/prompts/STAGE_E.18.md (THE ONE FIX lines 42-71; STEP 2 lines 137-142). Decision V31:
  docs/DECISIONS.md lines 562-577.
- C1's freeze: reports/stage_e14_prereg_C1.md (sha256 afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b).
- C1b's text: reports/stage_e18_prereg_C1b.md; its generator reports/stage_e18_briefs/make_c1b_text.py (15 exact
  replacements + section 13); the lead's diff and leg table: reports/stage_e18_c1b_diff.md.
- C1b's code: c1_replication/c1b.py and tests/test_c1b.py (new); the frozen C1 code it wraps:
  c1_replication/evaluate.py (c10_check at 376-384, its call at 514-523, preconditions, run), constants.py, world.py,
  q_m1.py (c10_reference 237-247), guards.py.
- The features: ml_route_v2/signals/ (generic.py `_lead` around 339-357; ports.py; k4.py; _daily.py; _events if any),
  ml_route_v2/constants.py (CLUSTER_LEADS, clusters), reports/stage_e12_gate0_list.json (covered signals).
- E.12's reference counts (training panel, NOT the test window): reports/stage_e14_c1_model.json key c10_reference.
- Fable's E.17 C1 findings: reports/stage_e17_review.md lines 199-330 (F-1, N-1..N-4).
- Listing evidence: reports/stage_e18_briefs/pages/LOG.md and the two saved pages beside it.
- Harness: v10 is commit dc93e9b; v12 is HEAD's reports/stage_e2b_harness_freeze.json
  (ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32). Files whose manifest entry changed v10 -> v12:
  data/config.py, data/hist_calendar.py, data/hist_store.py, data/pull_hist.py, data/calendars/hist2010/livestock.json
  (added), and four test files.

## Checks (report each as PASS / FAIL with file:line evidence)

1. Scope of the text diff. Every changed line of C1b against C1's freeze belongs to item 1 (ids C1b-T1/T2, the new
   registration N 478 -> 480, C1's closed attempt cited), item 2 (C10's exemption clause) or item 3 (every other
   feature keeps C10), or is bookkeeping item 1 forces. Judge in particular the lead's three consequential edits:
   section 2 "Never read before the test" (now false for C1's sentence after Stage E.17), section 9 (C1b's steps,
   no purchase), section 11 (harness v12 instead of C1's "differs from v10 only in data/config.py"). Confirm every
   other line is byte-identical (run the diff yourself). Flag anything that changes M1, q, calendars, windows, trade
   rule, costs, pass bar or any parameter.
2. The exempt list follows from listing dates and section 2 alone, never from a test-window count. Verify the two
   quotes by grep in the saved pages. Verify in code that CL is never applicable on NG rows (own-cluster exclusion)
   and that g17_mbt reads MBT bars only (never BTC). Say whether including g17_cl (a no-op, reference 0) matches V31
   and the prompt, and whether the text describes CL's status accurately.
3. No other leg or input can hit the same contradiction. For EVERY one of the 30 signals with a non-zero E.12
   reference on NG rows (both horizons), identify from code every input it reads (own NG path, another root's bars,
   release tables, calendars, session tables) and decide whether that input exists on the test window's dates by
   design. Check every leg's listing state in 2010-06-07..2019-04-30 (NQ, ZN, 6E, GC, ZC, CL, MBT; MES gets no
   feature). Long-established CME contracts may be marked [unverified] for launch date; flag any real doubt. Also
   look for any other design-time contradiction in C1b's text of the kind that stopped C1 (a frozen rule that the
   frozen inputs or C1b's own design make impossible to satisfy), including the guards C11 and C12, the clock check,
   the q / model / payload hash checks, the store hash file and the registry check under C1b's ids.
4. The code does exactly clause 2. c1b.c10_check equals C1's rule minus the exempt signals; the profile swaps the
   right evaluate attributes, every evaluate function that uses them reads them at call time (module globals),
   nothing else on the run path reads C1's ids, marker or freeze in a way that diverges, the originals are restored
   on exit and on exception, the marker path is C1b's, the registry check needs C1b's ids under C1b's freeze sha256.
   Confirm no C1 file changed: `git diff --quiet HEAD -- c1_replication tests/test_c1_evaluate.py tests/_c1_fixtures.py
   tests/_c1_state.py` and `git status --short c1_replication tests` (only c1b.py and test_c1b.py new).
5. Harness v12 against the evaluation path. Confirm that v12's changes to data/pull_hist.py, data/hist_store.py,
   data/hist_calendar.py and data/config.py change nothing that c1_replication.evaluate calls for plan "ext2010"
   (data.hist_bars.load_hist_leg -> data.pull_hist.get_plan("ext2010"), hist_parquet_path, parse_hist_calendar; for
   example compare get_plan("ext2010") built from dc93e9b's data/pull_hist.py against HEAD's, using `git show` into
   your scratch dir).
6. Tests. Run `uv run pytest -q -p no:cacheprovider tests/test_c1b.py tests/test_c1_evaluate.py tests/test_c1_world.py`
   (synthetic data, about 30 s) with PYTHONPYCACHEPREFIX set to a fresh dir under
   /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/a6f2d97b-f5fc-4d95-a054-c5010e1ff6d0/scratchpad/
   and `nice -n 10`. Say whether the tests cover clause 2 (exempt never stops, every other signal still stops, C1's
   rule unchanged) and what they miss.

## Output

Write reports/stage_e18_review.md (create it) with one section, "## C1b diff review (DiffReviewer-FableXHigh)":
the start and end time, a verdict (APPROVE, APPROVE WITH FIXES or BLOCK), the six checks, then findings, each
labelled BLOCKING, SHOULD FIX or NOTE, each with file:line evidence and a concrete fix. Scratch scripts go in
reports/stage_e18_diff_review/. Return: the path, a summary of at most 200 words, and anything you could not finish.

## Boundaries

- Never read a 2010-2019 bar or any value from the ext2010 stores (HIST_ROOT/ext2010/...): no load, no head, cat,
  less or parquet read of them. Do not open reports/stage_e14_c1_result.json (the exempt list must be judged without
  its counts) or reports/stage_e17_runs/* (base-rule results).
- Do not run c1_replication.c1b, c1_replication.evaluate or q_m1 on real inputs. Synthetic tests only.
- Write nothing outside reports/stage_e18_review.md and reports/stage_e18_diff_review/. No edits to C1b's files (the
  lead fixes findings), no ledger or trial-registry write, no git commit, no network except, optionally, at most six
  page fetches to check a leg's listing date (save raw under reports/stage_e18_briefs/pages/ with URL, UTC time and
  sha256 appended to its LOG.md; WebFetch first, then `scrapling extract get <url> <file>`). A web-search cost or
  budget notice is informational: if a search is refused for budget, stop searching, log it with the time, go on.
- No holdout, live/, ops/, TopstepX or Databento access. Do not spawn other agents.
