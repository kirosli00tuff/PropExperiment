# Brief: HarnessReviewer-FableXHigh (worker-xhigh, model fable) - review of harness v12 (Stage E.17 step 8)

Written by the E.17 lead. Independent, adversarial review of a harness change BEFORE any use (no quote, no buy has
used it). You did not write it. Do not spawn workers. Do not commit. Write only your review section.

## One objective

Decide whether the uncommitted v12 working tree of /home/kiros-li/Documents/GitHub/PropExperiment (against HEAD
558a7ce, which holds v11 and C1's result) is exactly the diff the E.16 hand-off step 8 and E.17 amendment A4 allow,
whether it is correct, and whether it is safe to quote and buy with. The caps are still placeholders (0.00); the lead
sets them from the fresh quote after your review and will send you that small delta separately.

## Binding rules

- reports/stage_e16_handoff.md section 1 step 8 (the diff list, "nothing else"; v12 must not change any file
  reports/stage_e16_freeze.json hashes; if it must, Part 2 stops) and step 9 (its own session id; 1,993 chunks).
- docs/prompts/STAGE_E.17.md amendments A1 ($124.00 total, V30 as amended in docs/DECISIONS.md), A3, A4 (the roots
  option restricting the purchase to A3's selection).
- base_rules/hist_plan.py and base_rules/constants.py lines 36-55: the frozen consumer of plan "ext2010h" (file name
  `ohlcv-1m_<ROOT>_v_0_<first>_2019-04-30_ext2010h.parquet` under `<base>/ext2010h/<ROOT>/`, 2010-06-06 <= first <=
  the root's window start, metadata plan "ext2010h", trade_date_range inside the plan window from get_plan).
- reports/stage_e16_windows.json: each root's start month and chunk count (1,993 in total).

## Inputs

- `git diff HEAD -- data tests` plus the new files data/calendars/hist2010/livestock.json and
  tests/test_e17_v12_{pull_hist,hist_calendar,hist_store}.py. The coder's report:
  reports/stage_e17_briefs/v12_report.md (its own claims: verify them). The coder's diff file:
  reports/stage_e17_briefs/v12.diff (sha256 5f68cc84...), applied on main by the lead.
- The provisional v12 manifest reports/stage_e2b_harness_freeze.json (sha256 838201c4bf11b5e407b530c847472894aea8fa24204eabeb014d4077f4d4a56c,
  built by the lead with the caps at 0.00; v11 at HEAD is ba1ce996...).

## Checks (each one PASS or a finding)

1. Scope: the changed files are exactly data/pull_hist.py, data/hist_calendar.py, data/hist_store.py, data/config.py,
   the new livestock calendar (byte copy; sha256 equal to the freeze's record of
   reports/stage_e16_calendars/hist2010_livestock.json), new tests, and tests/test_e14_hist_calendar.py:164 (the coder
   changed "livestock" to "crypto" as the unknown-group example; rule on it). The E.16 freeze verifies
   (`uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected
   5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4`); no file in reports/stage_e14_c1_freeze_inputs.json
   changed other than the harness manifest.
2. Plan ext2010h: by your own script, the chunk list per root equals the windows file (start month through 2019-04,
   end exclusive 2019-05-01), 1,993 in total; check_hist_chunk refuses any other chunk; get_plan("ext2010h") has first
   trade date 2010-07-01 and last 2019-04-30 and satisfies base_rules.hist_plan's checks for every one of the 21 roots
   (including TN, RTY, HE); label E16 and ids E16-H1..E16-H5. es2011 and ext2010 behave exactly as in v10/v11 (chunks,
   keys, session ids, CLI): compare against HEAD.
3. Spend safety: the quote and buy of ext2010h run under their own session id; the buy refuses at the 0.00 cap and
   without E16-H1..H5 registered under label E16; `--roots` restricts the buy to the named roots and is refused for
   es2011/ext2010. Rule on whether a buy of ext2010h WITHOUT `--roots` should be refused (the lead will always pass
   it; the coder made it optional). The lead plans to run up to 4 buy processes at once over DISJOINT `--roots` sets
   under the one session cap (the E.12 precedent): say whether the gate's cap checks stay safe under that
   concurrency, and what margin is needed.
4. The store builder for ext2010h: inputs are exactly the root's own chunks from its purchase manifest; the layout,
   metadata plan and trade_date_range match base_rules.hist_plan; the partial first trade date 2010-07-01 (its
   2010-06-30 17:00-19:00 CT Globex hours lie in the unbought June chunk) is handled without refusing and without
   inventing rows; livestock roots (LE, HE) use the livestock hist calendar. Note any risk for roots whose symbology
   before listing (TN before 2016, RTY before 2017-06, HE before 2017-07) the fake tests cannot exercise.
5. Tests: run tests/test_e17_v12_*.py, tests/test_e14_*.py, tests/test_base_rules_store.py and
   tests/test_base_rules_review.py at nice 10 with -p no:cacheprovider (report counts). Do not run the full suite.
6. The provisional manifest: preflight passes with 838201c4...; entries differ from v11's only for the changed files and
   the added livestock calendar; note that the new tests are not in the manifest's test patterns (the coder's point 1)
   and rule on whether that matters.

## Boundaries

No vendor call, no .env or key read (never open the untracked ..env.swp), no write to ledger/, data/ or any repo file
except your review section, no commit. Read large files by section or by script.

## Output

Append a section "## v12 review (HarnessReviewer-FableXHigh)" to reports/stage_e17_review.md: each check, findings
graded BLOCKING, SHOULD FIX or NOTE with evidence (command and output line). Return the path, a summary of at most
200 words with your verdict (APPROVE, APPROVE WITH FIXES, or BLOCK), and anything you could not finish. Stay available:
the lead will send you the cap values after the fresh quote for a short follow-up check.
