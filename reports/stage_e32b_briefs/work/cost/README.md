# F5 CostTabler: Stage E.32b session-cost script

## Usage
    python3 reports/stage_e32b_briefs/work/cost/make_cost.py <to ISO UTC> [<from ISO UTC>]
Example for an end time of 10:30 PDT: `... make_cost.py 2026-10-29T17:30:00Z`. Default `from` is
2026-10-29T05:00:00Z. Writes `cost_raw.txt` (one line per transcript and model) and `ret_cost_tokens.md`
(tables 1 to 4 plus pauses). Prints a 6-line summary. Run it with `nice -n 10`; it takes a few seconds.

## What it reads
Only `~/.claude/projects/-home-kiros-li-Documents-GitHub-PropExperiment/<id>.jsonl` and
`<id>/subagents/**/agent-*.jsonl` (+ each `.meta.json` for role, agent file, requested model) for the four lead
sessions: 3d79635b (1), 7e35d21b (2), 3860d0d1 (3), 0d036ce2 (4). Fields read: timestamp, type, requestId,
message.id/model/usage. No .env, no keys, no message text (the first-prompt "You are X" fallback is only used when a
meta file is missing; none was needed).

Scan = E.10 scan (per-field max over a message's records, keyed by (message id, requestId)), with rglob as in E.26.
Adapted from reports/stage_e26_briefs/cost.py; the added parts are the four sessions, worker identity from meta,
per-worker/per-session/delegation tables and pause listing. Tables: (1) per model whole stage, (2) one line per
spawn (role, agent file, requested model, models in transcript, first/last PDT, msgs, 4 fields + total), (3) per
session (lead tokens, worker tokens, first-last, idle gaps >= 30 min, gaps between sessions), (4) lead vs workers and
by model tier. Times PDT. Unreadable/missing files are listed under "UNREADABLE OR MISSING" (none at test time).

## Findings
- Session slicing: no pre-stage usage in any of the four transcripts. Session 1's first record is 05:06:09Z
  (22:06:09 PDT), its first user message (the stage prompt) 05:06:40Z, first assistant 05:06:47Z; the STATE file
  gives the stage start as 22:07 PDT (the brief's "about 22:15" is later than every record). Sessions 2 to 4 start
  at their own "continue as lead session N" prompts. So no slice is needed; the default `from` (05:00Z) is just a
  lower bound. Window edges: lead can override `from` if it wants a different start (a judgment, not made here).
- Resumes: none of the four is a `--resume` of another. Every record in each file carries that file's own
  sessionId (only the 4 or 1 non-event lines have none), first user messages are fresh prompts after planned context
  wipes, and no (message id, request id) pair appears in more than one file (0 duplicates across all files). So no
  usage is hidden in an earlier session's file and none is double counted. Caveat: the usual resume rule (usage stays
  in the first .jsonl) applies if the lead later resumes any session with `claude --resume`; then rerun with the
  extended window and recheck.
- Session 3's last timestamped record is 07:28:50 PDT but the file mtime is 08:39; session 4 starts 08:39:23. The
  71-min gap between them is reported as a gap, not classified (pause vs wipe is the lead's call). Two 75-min idle
  gaps inside session 3 (01:55-03:11 and 04:09-05:24 PDT, union of lead and subagent timestamps) are listed as
  candidate pauses, not classified.
- Models seen (message.model): claude-opus-5-5, claude-sonnet-5-5, claude-haiku-5-5, claude-fable-5-1, and
  `<synthetic>` (3 messages, all usage fields 0, in session 3's lead; kept as a zero row). Per CLAUDE.md memory
  (Fable alias fallback), verify any Fable-routed row from this transcript model column: all Fable rows here show
  claude-fable-5-1, none fell back.
- Subagent files: 1 + 18 + 13 + 4 = 36 transcripts, all with meta files; no workflow subdirectories, all names
  resolved from meta (no UNNAMED). Session 4's spawns include running workers, so the counts grow until the end time.
- Messages that straddle the `to` bound are counted from their in-window records only (max usage of those records);
  the effect is at most one message per running transcript.

## Test run (to = 2026-10-29T15:55:28Z, 08:55 PDT)
5 model rows (incl. `<synthetic>`), 36 spawn rows, 4 session rows, 0 problems. Totals: opus 595,069,280; sonnet
38,687,053; fable 19,324,859; haiku 1,170,382; synthetic 0; all 654,251,574 (lead 116,642,490 = 17.8%, workers
537,609,084 = 82.2%). The test output was written to this folder; rerun overwrites it.
