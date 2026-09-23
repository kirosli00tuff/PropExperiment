STAGE D.1f "CONFIRMATION RUN: BUY, SEAL, BUILD, TEST THE FROZEN LIST"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: the D.1f build session built and froze the whole confirmation
harness (reports/stage_d1f_harness_freeze.json, 129 files, sha256
ba5b34d5239737cc493c360b38753573aa133963e73abf8639ba3532a4cf847a,
committed as d384bfe, which is the runner's git anchor). This session does
steps 2 to 8 of the frozen confirmation list's order of operations
(reports/stage_d1f_confirmation_list.md 1.5): buy the MES 1-minute history
for 2019-05..2025-03 ($7.59 quoted), seal the 13 holdout-2 chunks as they
arrive, build the confirmation parquet, validate the calendar, compute the
start date S by the frozen rule, run the continuity check, run the 58 Tier A
tests and 43 Tier B statistics, and apply the frozen decision rules. The
result is either a member that passes confirmation (a D.2 discussion item
for the user, never an automatic registration) or a per-class MES null
statement in exactly the wording docs/NULL_CRITERIA.md allows, or an
honest "inconclusive". Every rule, threshold and test was fixed before this
data existed. Nothing is chosen here; everything is executed.

Lead: Opus 5.5, effort max. Ultracode: off.

Why this lead and effort: this is the session whose output is a verdict.
Every rule is frozen, but applying them still takes judgment at the edges:
reading a step-4b discrepancy correctly, deciding whether a stop condition
has been met, making sure a class statement says exactly what the criteria
permit and nothing more. A subtle error here gets written into the program's
record as a finding. CLAUDE.md reserves opus max for exactly that. The
parallel parts are small (a few verification workers), so ultracode's
fan-out buys nothing.

Usage: Fable's shared allowance already hit its limit once this week, in
the build session. Fable is used here only for the independent
verification of verdict-bearing numbers (Task 7), at xhigh, and nothing
else. If Fable is unavailable when Task 7 starts, finish everything else,
mark the verification pending in the STATE file and the entry, and label
every class statement "pending independent verification". Never substitute
opus for the Fable check.

============================================================
SCOPE
============================================================

This session does:
- steps 2 to 8 of the list's order of operations, in order, once
- the independent verification of the verdict-bearing numbers
- the progress entry, with every class statement worded as
  docs/NULL_CRITERIA.md section 7 allows

This session does NOT:
- change any file in the freeze manifest, except the single sanctioned path
  in Task 3 (a step-4b calendar correction), handled exactly as described
  there
- re-run, revisit or reinterpret anything after step 8 completes. The list
  forbids it. A defect found after step 8 is reported, and the affected
  statement is withheld; it is never fixed and re-run in this session.
- buy anything beyond the ohlcv-1m history. The order-book data is Stage
  D.1g's decision, and the $10 caps in data/config.py are set so it cannot
  fit.
- register anything. REGISTRATION.md stays 0 bytes. A passing member goes to
  the user as a D.2 discussion item.
- touch holdout-1, rules/, live/, ops/ or any TopstepX credential
- run any trial, statistic or H module on the holdout-2 dates, the embargo
  dates or holdout-1. The loaders refuse; do not work around a refusal.

============================================================
CONTEXT TO READ FIRST
============================================================

1. CLAUDE.md, in full: roles, routing, compute limits, ETA tables, Session
   cost, unattended runs. This prompt restates only what is specific to
   this stage.
2. reports/stage_d1f_confirmation_list.md and docs/NULL_CRITERIA.md, in
   full. Both are read-only and FROZEN. They are the rules of this session.
3. progress.md's Stage D.1f (build) entry, especially "What the run session
   must do first (checklist)" and "Open choices the lead made on its own".
   The build lead's rulings stand; do not re-decide them.
4. progress.md's Stage D.1e entry: ε = 34 net ticks per micro per day, the
   power table, the holdout-2 bounds, and the decision packet.
5. The runner's code paths, as needed: data/pull_mes.py (--d1f-pull),
   data/build_mes_bars.py (--confirmation), data/holdout.py,
   strategy/research/_d1f_confirmation.py and its sibling _d1f_* modules.

============================================================
GUARDRAILS (short recap; CLAUDE.md has the full list)
============================================================

- `uv run python -m data.holdout status` at the start, after sealing, and
  at the end. Report both holdouts. Holdout-1 must stay all_ok with
  unlocks_logged 0 throughout; holdout-2 must go from not_yet_sealed to
  sealed, all_ok, 0 unlocks.
- Every Python command runs with `OPENBLAS_NUM_THREADS=1`, at `nice -n 10`.
- Spend: only the ohlcv-1m history through `data.pull_mes --d1f-pull`,
  which refuses any request or session total over $10.00. Before the pull,
  confirm the spend ledger at
  /mnt/large-storage/Archive/GitHub/MLCryptoEngine/data/vendor/spend_ledger.jsonl
  is readable; if the large drive is not mounted, stop and report, never
  edit the path.
- Compute limits per CLAUDE.md: at most half the cores, one heavy job at a
  time, memory checked before launching, resumable scripts, and nothing
  heavy between 15:15 and 16:15 PT on a weekday (the AiTrader collector).
  Slower is fine; a crash is not.
- No commits, except the Task 3 calendar correction path if it is needed.

============================================================
TASK 0 — STARTUP
============================================================

- Holdout status for both holdouts.
- Confirm HEAD is d384bfe or a descendant with no change to any manifest
  file, and that `sha256sum reports/stage_d1f_harness_freeze.json` returns
  ba5b34d5239737cc493c360b38753573aa133963e73abf8639ba3532a4cf847a.
- Run the preflight:
  `OPENBLAS_NUM_THREADS=1 nice -n 10 uv run python -m
  strategy.research._d1f_confirmation --step preflight --manifest-sha256
  ba5b34d5239737cc493c360b38753573aa133963e73abf8639ba3532a4cf847a`.
  Expected refusals at this point, and only these: the confirmation build
  summary is missing, and holdout-2 is not yet sealed. Any other refusal
  (a hash mismatch, the git anchor) means stop and report.
- Check free disk space on the main drive and free memory.
- Write the estimate ETA table (CLAUDE.md) and print it in chat.

============================================================
TASK 1 — PURCHASE AND SEAL (list steps 2 and 3)
============================================================

`OPENBLAS_NUM_THREADS=1 nice -n 10 uv run python -m data.pull_mes --d1f-pull`.
It quotes, gates, buys the 71 monthly chunks oldest first, and seals each of
the 13 holdout-2 chunks (2024-03 through 2025-03) on arrival, before the next
request. Fetch the dataset condition and symbology once and freeze them, as
the puller does.

- Record the holdout-2 trade-date count from the calendar at sealing (build
  choice 2.1), never from the sealed bytes.
- Decode failure on any holdout-2 chunk: the plaintext stays at its target.
  Do not seal it, do not read it, and do not delete it without a logged
  decision. The conservative decision is to stop the stage here, write the
  state, and report; take it unless the failure is plainly a truncated
  .partial left by an interrupted fetch, which the next fetch removes.
- Any request refused by the cap, any quote above $7.59 by more than a few
  cents, or any unexpected billable size: stop and report, do not raise the
  cap.
- After the pull, holdout status must show holdout-2 sealed, 13 chunks,
  all_ok, plaintext absent. Log the ledger lines added and the actual cost.

============================================================
TASK 2 — BUILD THE CONFIRMATION PARQUET (list step 4)
============================================================

`OPENBLAS_NUM_THREADS=1 nice -n 10 uv run python -m data.build_mes_bars
--confirmation`. It reads only the 58 unsealed chunks, stamps the raw
symbol mapped on each bar's date, drops trade dates after 2024-02-29,
validates, runs step 4b, and writes the parquet read-only with the manifest
sha256 stamped in.

- Exit code 0: go to Task 4.
- Exit code 7 (stop for a lead decision): read the build summary. If the
  cause is a raw-symbol drop from 2019-05-06 on, stop the stage and report;
  that is not a calendar matter. If the cause is a step-4b discrepancy, go
  to Task 3.

============================================================
TASK 3 — STEP-4B CALENDAR CORRECTION (ONLY IF TASK 2 REQUIRES IT)
============================================================

The list (1.5, step 4b) sanctions exactly one change to a frozen file
before step 5: correcting data/cme_calendar.py so that every weekday with
no bars is a listed full closure, every early halt matches the observed last
minute plus one, and every listed 2019-2024 entry is observed.

- Diagnose each discrepancy against the observed bars AND a cited source.
  Two causes are expected and are not calendar errors: thin 2019 trading
  (a normal day whose last bar is early because nothing traded) and the
  pre-2021-06-28 session (a 15:15-15:30 CT pause and a 16:15 CT close, which
  the frozen session.py treats as a 16:00 halt). A calendar entry is changed
  only when a cited CME or exchange source supports the change. Thin trading
  is never "fixed" by adding a fake early close.
- If a discrepancy is real and sourced: edit only the 2019-2024 block of
  data/cme_calendar.py, with the citation, keeping the 2025-2026 block
  byte-identical. Re-run `uv run python -m strategy.research._d1f_freeze` to
  write a new manifest, commit exactly data/cme_calendar.py and the new
  manifest in one commit whose message names the old and new manifest
  sha256 and lists each corrected date, then re-run Task 2. Use the new
  sha256 for every later runner call.
- If a discrepancy cannot be resolved with a cited source, stop the stage
  and report it with the evidence. Do not change a frozen file on inference
  alone.
- Once Task 4 starts, the calendar is immutable.

============================================================
TASK 4 — THE LIST RUN (list steps 5 to 8)
============================================================

`OPENBLAS_NUM_THREADS=1 nice -n 10 uv run python -m
strategy.research._d1f_confirmation --step all --manifest-sha256 <sha>`.

It runs, in order and once each:
- step 5, the start rule: S from docs/NULL_CRITERIA.md 4.1, with every
  monthly median and the 0.15 and 0.40 sensitivities logged. If no month
  qualifies, the stage stops with that finding.
- step 6, the continuity check: all 31 trials reproduce
  stage_d1d_accounting.json on the train union to the cent, trip counts
  equal, daily Sharpe to 1e-6. Any failure stops the run.
- step 7, the list: 58 Tier A tests and 43 Tier B statistics on the
  confirmation window S..2024-02-29, the per-member statistics, bootstrap
  UCBs and achieved null power, Holm over the 58, the composite screening
  verdict, and the cumulative accounting at N = 58 (DSR, t > 3.0, PBO), with
  N = 101 and 186 reported descriptively.
- step 8, the decision rules of the list's section 3: per member, pass,
  null or inconclusive; per class, null only if every member is null; C6
  inconclusive by design (its verdict belongs to D.1g).

This is the heavy compute. Before launching, estimate memory and time from
a small probe (one Tier A member through step 7's per-member path), keep
the job at half the cores, and make sure it resumes from its written state.
If the machine goes down mid-step, resume; do not restart a finished step.

Nothing in steps 5 to 8 is revisited after step 8 completes.

============================================================
TASK 5 — READ THE RESULT (LEAD, AFTER STEP 8)
============================================================

From the runner's output JSONs only (not from memory of intermediate
logs):
- The start date S, its monthly medians, and the confirmation-window day
  count against the D.1e power table's needs per class.
- Every Tier A member: n, mean net edge per micro per day, UCB95, achieved
  null power, one-sided p, its Holm-adjusted outcome, and its label.
- Any member that passed "edge exists": its full record, including the
  composite verdict, DSR, t and PBO, and the period-appropriate cost caveat
  from docs/NULL_CRITERIA.md 4 (early-era spreads were wider, so a positive
  finding needs a cost re-check before it can go to D.2 discussion).
- Per class: null, inconclusive (naming the blocking members), or containing
  a passing member.
- Tier B anomalies, per the one-sided rule.
- Year-by-year slices, descriptive only.
- The descriptive resolution per class (the smallest per-trade edge the
  window could rule out), beside every null statement.

============================================================
TASK 6 — CLASS STATEMENTS (LEAD)
============================================================

Write each class's statement in exactly the form docs/NULL_CRITERIA.md
section 7 permits, with every number explicit: the class, the window
S..2024-02-29, market orders at modelled retail cost, 2 micros, flat by
the XFA cutoff, ε = 34 net ticks per micro per day, both hashes, the
per-trade resolution, the least-active member, and a "null by inactivity"
label where it applies. Never write "MES has no edge", "intraday MES has no
edge" or "MES is efficient". If every class C1-C5 and C7 is null, use the
one aggregate sentence the criteria allow, with C6 pending D.1g. If any
class is inconclusive, say which members blocked it and why.

============================================================
TASK 7 — INDEPENDENT VERIFICATION (FABLE XHIGH)
============================================================

One worker, worker-xhigh on fable, named NumberVerifier-FableXHigh. It must
not import the runner's decision or member modules. From the runner's
output JSONs and the per-member daily series, it re-computes independently:
- UCB95 and achieved null power for the binding member of every class (per
  the D.1e power table) and for any member within 10% of ε
- the Holm ordering and cut-off over the 58 Tier A p-values
- the full record of any member labelled "edge exists"
- the start rule's S from the logged monthly medians
- each class label from the member labels

It writes reports/stage_d1f_run_verification.md with VERIFIED, VERIFIED
WITH NOTES, or DISCREPANCY for each item. The lead includes it in the
entry. A DISCREPANCY on a verdict-bearing number means the affected
statement is withheld and reported as "unverified: discrepancy found",
never corrected and re-run in this session.

============================================================
DELEGATION PLAN (the lead executes this; it does not do worker tasks)
============================================================

| Task | Owner | Model / effort | Parallel? | Why this tier |
|---|---|---|---|---|
| 0 Startup, preflight | lead | opus max | — | checks that gate the whole run |
| 1 Pull and seal | lead runs the frozen command | — | serial | irreversible: the lead watches it directly |
| 2 Build | lead runs the frozen command | — | serial | its exit code decides the next task |
| 3 Calendar correction, if needed | lead, with one CalendarChecker-OpusXHigh worker for source lookups | opus xhigh | serial | touches a frozen file; the lead rules |
| 4 List run | lead runs the frozen command | — | serial, background | heavy compute under the limits |
| 4 Probe and monitoring | lead | — | — | small, inline |
| 5 Read the result | lead | opus max | — | the judgment this session exists for |
| 5 Tabulate the member records from the JSONs | ResultTabulator-SonnetMed | sonnet medium | parallel with 7 | complex extraction, no conclusions |
| 6 Class statements | lead | opus max | — | wording is constrained by the criteria |
| 7 Independent verification | NumberVerifier-FableXHigh | fable xhigh | parallel with 5's tabulation | a second model checks verdict numbers |
| 8 Entry, STAGES.md, Session cost | lead | opus max | — | — |

At most 4 workers at once. Workers write files and return paths.

============================================================
WHAT NOT TO DO
============================================================

- No change to any manifest file except the Task 3 path, and no commit
  except that one.
- No re-run, re-tuning or reinterpretation after step 8.
- No purchase beyond the ohlcv-1m history; no cap change.
- No read of holdout-2, embargo-2 or holdout-1 bars, and no workaround of
  any loader refusal.
- No registration; REGISTRATION.md stays 0 bytes.
- No wording beyond what docs/NULL_CRITERIA.md section 7 permits.
- No heavy computation in the AiTrader collector window.

============================================================
DELIVERABLE
============================================================

A dated progress.md entry for Stage D.1f (run), containing:
- guardrail evidence for both holdouts at start, after sealing and at end
- the purchase: ledger lines, actual cost, holdout-2 sealing record and its
  calendar trade-date count
- the build: exit code, drops per month, step-4b result, and any Task 3
  correction with old and new manifest sha256 and the commit hash
- S, the monthly medians and sensitivities, and the confirmation day count
- the continuity result
- the Tier A table (all 58), Tier B anomalies, Holm result, cumulative
  accounting at N = 58 with N = 101 and 186 descriptive
- every class statement, worded per the criteria, with its descriptive
  resolution
- the D.2 discussion items, if any, with the cost re-check caveat
- Task 7's verification table
- the open choices the lead made on its own, with reasons
- the Session cost section and the final ETA table, per CLAUDE.md

Also one line in docs/STAGES.md recording the run and its headline.

END PROMPT
