STAGE E.26 "HOUSEKEEPING: MARKET DATA TO LARGE STORAGE, THE THIRD DATABENTO ACCOUNT, AND THE DECISION RECORD"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: A housekeeping stage, run first on the user's last Max day
(2026-10-21) beside Stage E.28 (V44). Four tasks:
- Task 1: move the program's market data out of the repo folder onto the
  internal LARGE STORAGE disk (/mnt/large-storage, ext4), with symlinks
  at every old path, full checksum verification, and the holdout seals
  intact. E.28's data purchase waits for this task.
- Task 2: let data/config.py select a third Databento account
  (ACCOUNT_3, key variable DATABENTO_API_KEY3), with tests, without
  changing acct-1 or acct-2.
- Task 3: the decision record: V45 in docs/DECISIONS.md.
- Task 4: refresh the Topstep rules record for its Tier 1 news window.
No outcome read, no market data read beyond checksums, no purchase,
nothing registered, N stays 538. E22-F2 work is skipped today (V44).

Decisions in force: docs/DECISIONS.md V20 to V44. Binding: this prompt.

Lead: Opus 5.5, effort xhigh. Ultracode: on (launched interactively).

Why this lead and effort: moving sealed holdout data and every store a
frozen manifest points at can silently break freezes, seals or harness
checks; the account change touches the spend path. Fable reviews the
move plan before any file moves and the config change before commit.

Usage and time: launched about 02:15 PDT on 2026-10-21. Task 1 first and
as fast as safely possible, because E.28 waits on it for its purchase.
Work may continue until 23:00 PDT; the return by 23:30; nothing running
after 23:45. At most 6 workers at once (E.28 runs beside this session).
Checkpoint reports/stage_e26_STATE.md after every step; resume from it
after any usage limit.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the choice
under Open choices in the return document, and continue.

============================================================
TASK 1: MARKET DATA TO LARGE STORAGE (FIXED HERE)
============================================================

T1.1 Inventory, no file moved: list every data file and directory under
the repo that holds market data (the Databento raw downloads, the
processed stores such as data/processed_step2/ and data/processed_hist/,
the holdout and embargo stores, MES's Stage D store, caches of bars) with
sizes, file counts, and which freeze manifests, harness manifests,
holdout manifests and scripts reference each path. Code under data/
(the Python package: config.py, adapter.py, bars.py and the rest) is NOT
data and never moves. .env, keys and any secret never move.
T1.2 Seal check: confirm on /mnt/large-storage (ext4) that the holdout
seal mechanism works there: create a scratch file, apply the same
permission and ownership scheme the seals use, and confirm the holdout
status tool reads it the way it reads the real seals. If anything
differs, sealed holdout and embargo files stay where they are and only
unsealed stores move.
T1.3 Plan: write reports/stage_e26_move_plan.md: each source path, its
destination under /mnt/large-storage/market_data/PropExperiment/
(mirroring the repo-relative layout), the symlink to leave at the old
path, and the order of operations. MovePlanReviewer-FableXHigh reviews it
before any file moves; BLOCKING and SHOULD FIX fixed first.
T1.4 Before checks, quoted verbatim in the return: the holdout status,
every freeze verification, the harness check (v13 dd2bcc60...), and a
sha256 manifest of every file to be moved.
T1.5 Move: copy (preserving permissions, ownership and timestamps),
verify every copied file's sha256 against the manifest, replace each old
path with a symlink to the new location, then remove nothing else. A
source is deleted only after its copy is verified and its symlink is in
place.
T1.6 After checks, quoted verbatim: the same holdout status, freeze
verifications and harness check, all unchanged; a short read through
each symlink by the existing loaders in test mode (no outcome read).
Then a git status check: the move must not add data to git.
T1.7 Mark the move done in the STATE file with the destination root, so
E.28 can download there. New downloads go straight to
/mnt/large-storage/market_data/PropExperiment/.

============================================================
TASK 2: THE THIRD DATABENTO ACCOUNT
============================================================

Add ACCOUNT_3 to data/config.py mapped to DATABENTO_API_KEY3, selectable
the same way acct-1 and acct-2 are (require_databento_key, the quote
tool and the spend ledger), without changing their behaviour or the
default ACTIVE_ACCOUNT. Tests with fake keys only. The key itself is a
one-time exception the user chose for a temporary account that he will
wipe; it may not be in .env yet. Check its presence by variable NAME
only (empty or non-empty), never read, print, copy or log the value.
ConfigReviewer-FableXHigh reviews the diff; commit with Task 3. Also
commit scripts/set_databento_key3.sh (the planner's hidden-input helper)
if it passes review; never commit .env.

============================================================
TASK 3: V45 IN docs/DECISIONS.md
============================================================

Append V45 recording: the data move as done (the destination root, what
moved, what stayed and why, the before and after checks); ACCOUNT_3 and
DATABENTO_API_KEY3 as a temporary account for the E.28 pilot purchase
only, to be wiped by the user after the download is verified; the E.25
corrections: V34's reason for dropping noise-area momentum ('unsized') is
corrected with the post-publication evidence from reports/E.25_RETURN.md,
and V38's sentence on published intraday effects is amended to name the
three working-paper effects above 1.5 x the D8 round trip (pre-refunding
ZN, pre-FOMC ZN, the ES 3rd-Friday reversal) as exceptions that cannot be
tested with adequate power on owned data, leaving the intraday program's
closure in place.

============================================================
TASK 4: TOPSTEP RULES RECORD
============================================================

Refresh reports/stage_e19_rules.json for Topstep's Tier 1 news window
(reports/E.25_RETURN.md section 7 item 6 and its prop-rules reader), with
the source and date quoted. Do not rerun E.19's simulator here (E.28
reuses it with the refreshed record).

============================================================
SCOPE
============================================================

This stage does NOT:
- read any outcome, holdout, embargo or research-window data (checksums
  and test-mode loader reads through symlinks only)
- buy anything or call Databento for data or quotes
- move code, .env, keys or secrets, or put any secret on LARGE STORAGE
- send anything to the Windows PC
- change any freeze, harness file or frozen member
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.

============================================================
GUARDRAILS
============================================================

- Start and end checks quoted verbatim: `git status --short`, `git log
  --oneline -3`, the holdout status, `wc -c REGISTRATION.md`, the freeze
  verifications, the spend ledger line count and sha256, N, and `uv run
  pytest -q -p no:cacheprovider` at the end (stop it if free memory falls
  below 2 GB and quote the last full run on identical code).
- Commits touch only this stage's files; before committing, `git status`
  shows no file of E.28 staged. Push after the final commit (the planner
  reviews and pushes; do not push yourself).
- Before ending, confirm no worker or background shell is still running.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup | lead | opus | xhigh | first | gates the session |
| T1.1 inventory | DataInventory-OpusHigh | opus | high | first | paths and references |
| T1.2-T1.3 seal check, plan | lead | opus | xhigh | after T1.1 | reserved judgment |
| Move plan review | MovePlanReviewer-FableXHigh | fable | xhigh | before any move | independent check |
| T1.4-T1.7 move | lead | opus | xhigh | serial | sealed data |
| Task 2 code | ConfigCoder-OpusXHigh | opus | xhigh | parallel with Task 1 | spend path |
| Task 2 review | ConfigReviewer-FableXHigh | fable | xhigh | after the diff | independent check |
| Tasks 3, 4 | lead | opus | xhigh | after Tasks 1, 2 | reserved |
| Return | lead | opus | xhigh | last | reserved |

    DELEGATION PLAN (the lead executes this; it does not do worker tasks)
    1. Decompose each task into subtasks with one objective, inputs, output
       path and format, allowed tools, and boundaries.
    2. Route per CLAUDE.md. State model and effort for each subtask before
       spawning.
    3. Run independent workers at once (V37); at most 6 at once today.
    4. Collect results as files plus short summaries.
    5. Verify with an independent fable xhigh worker as listed.
    6. Synthesize in the lead against this prompt, and write the synthesis
       to disk before ending.
    7. Unattended run: no pauses to ask. Checkpoint to
       reports/stage_e26_STATE.md after each task.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.26_RETURN.md, one progress.md entry, one docs/STAGES.md
line, and one final commit "Stage E.26 data move and housekeeping". No
push. Fixed sections:

1. Summary, at most 200 words: what moved and where, what stayed and why,
   the checks before and after, ACCOUNT_3, V45, the Topstep refresh.
2. Guardrail evidence: start and end checks verbatim; order of events.
3. Results: the inventory, the move plan, the checksum manifest summary,
   the before and after checks, the config diff and tests.
4. Delegation record.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
