# Brief: V9Coder-OpusXHigh (worker-xhigh, opus). Stage E.12: harness v9, the L-3 closure-bar ruling path

Context. Stage E.12 bought ML route v2's phase-1 training-window history. The frozen step 2 store
builder (data/step2_store.py:_build_window, lines ~265-298) holds a root "for the lead before
building (ruling L-3)" when it has bars inside a scheduled closure beyond the close minute, and it
has no code path to apply a lead ruling, so the root gets no store. Held so far: NQ (6 bars:
2020-03-30 Mon 15:29, 2020-03-31 Tue 15:29, 2020-03-31 Tue 16:59 -> trade date 2020-04-01,
2020-04-01 Wed 15:29, 2020-06-30 Tue 15:29, 2020-06-30 Tue 16:59 -> 2020-07-01) and 6A (1 bar:
2020-06-30 Tue 16:59). See reports/step2/bars_NQ.json and bars_6A.json, key "closure_bars".
THE USER DECIDED (2026-10-03): harness v9, keep and flag. The builder reads an enumerated ruling
file that lists exactly the held bars and keeps them, flagged in_scheduled_closure, as L-3's
principle states (E.2a: "Bars inside a scheduled closure are kept and flagged ... not a hard
failure"). No bar value changes, and any deep-closure bar NOT listed still holds.

## WHERE YOU WORK
Only in the git worktree /home/kiros-li/Documents/GitHub/PropExperiment-e12-v9 (detached at
deccd17, harness v8). Never edit the main tree (store builds under v8 run there now). No commits.
Tests from the worktree with the main venv:
  cd /home/kiros-li/Documents/GitHub/PropExperiment-e12-v9 && nice -n 10 \
  /home/kiros-li/Documents/GitHub/PropExperiment/.venv/bin/python -m pytest -q -p no:cacheprovider <files>
(no PYTHONPYCACHEPREFIX: the harness bytecode tests fail under it). No .env exists there; no key.

## Changes
1. data/step2_store.py: a module constant CLOSURE_RULINGS_PATH = REPO_ROOT /
   "reports/stage_e12_closure_rulings.json" (a parameter of run_product / build_step2_product for
   tests, default the constant). Schema:
   {"schema": "closure_rulings/1", "ruling": "...", "entries": [{"root": "NQ", "ct": "2020-03-30 Mon
   15:29", "trade_date": "2020-03-30", "ruling": "keep_and_flag"}, ...]}
   ("ct" exactly as bb._ct_str writes it in the summary's closure_bars). In _build_window, when deep
   closure bars exist: if every deep bar of the root is listed (root, ct, trade_date) with ruling
   keep_and_flag AND every listed entry of the root matches a deep bar, continue to _flag (build);
   the summary gets "closure_ruling": {"path", "sha256", "bars_ruled": n, "entries": [...]}, and the
   parquet metadata the same. A deep bar not listed: held_for_lead as now (naming the unlisted
   bars). A listed entry with no matching bar: refuse (a hard problem naming it). A missing ruling
   file with deep bars present: held as now. Close-minute bars are unchanged.
2. Keep every existing guard. Do not change data/stage_e_bars.py, data/group_session.py,
   data/build_bars.py or any module the v2 phase-1 path imports except data/step2_store.py, and in
   data/step2_store.py keep step2_parquet_path, summary_path and the store layout unchanged.
3. Tests (a new file named so the harness manifest freezes it, e.g. tests/test_e2b_step2_store_v9.py;
   check screening/harness_freeze.py's test patterns): held without a ruling; built with the exact
   ruling, the ruled bars present with in_scheduled_closure True and values unchanged; an extra
   unlisted deep bar keeps the hold; a listed bar that does not exist refuses; the summary records
   the ruling file's sha256.
4. THE LOADER CHECK (most important; do it first): prove with a fixture store built by the v9 path
   under the REAL equity and FX group calendars (data.group_session.load_group_calendar) that
   data.stage_e_bars.load_confirmation_leg (and read_leg) load a store containing a ruled bar at a
   15:29 CT equity-halt minute (2020-03-30) and at a 16:59 CT daily-break minute (2020-06-30, FX and
   equity), with no TradeDateUnbookable / TradeDateMismatch / HoldoutRowRefused, and that the bar's
   trade date is the one the summary shows. If the loader refuses such a bar, STOP and report at
   once (SendMessage is not available to you: write the finding to your report and return).
5. Find how screening/harness_freeze.py's build_manifest lists frozen inputs; if the ruling file
   must be listed explicitly to be hashed, say exactly which edit is needed (and make it if it is a
   one-line list addition in a harness file), so the lead's v9 manifest covers it.

## Return (at most 200 words) + report
Write reports/stage_e12_briefs/v9coder_report.md in the MAIN tree (the only main-tree file you
write): the loader check result first, every change with file:line, `git -C <worktree> diff --stat`,
test summary lines, the exact manifest build/verify commands, and anything open. Return its path, a
summary and open items.
