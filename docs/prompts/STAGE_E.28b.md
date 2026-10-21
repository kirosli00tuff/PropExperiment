STAGE E.28b "E.28 CONTINUED ON THE PRO PLAN: PILOT CODE FIXES, DELTA REVIEW, PURCHASE, RETURN"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage E.28 stopped at 16:43 PDT on 2026-10-21. The user moved to
the Pro plan, and the old lead's call failed. Its context (about 536k tokens)
is too costly to carry on Pro, so this fresh session finishes E.28 from disk.
Parts A and C are DONE; do not redo or re-review them. Part B is left:
finish the pilot code fixes, run one independent delta review, then the
purchase (last, and only if allowed), the download check, and the return.

Binding: docs/prompts/STAGE_E.28.md (all its rules, scope and guardrails
still hold, unless this prompt changes them), docs/DECISIONS.md V20 to V45,
reports/stage_e28_STATE.md.

Lead: Opus 5.5, effort high. Ultracode: off. At most 2 workers at once.

Why these changes (planner, V44 last-Max-day plan, Pro since about 16:45):
- Fable is not available on Pro without usage credits. Each Fable review
  left in E.28 becomes an Opus 5.5 xhigh reviewer in a fresh context. It gets
  only the files it checks, never the lead's reasoning. Name it
  DeltaReviewer-OpusXHigh. Record this as an open choice and as a decision
  for the user.
- Pro usage windows are small. Keep turns short, read files in parts, and
  never load the 1 MB methods brief.

Times: unchanged. The purchase starts by 20:30 PDT at the latest. Work
stops at 23:00, the return is written by 23:30, and nothing runs after
23:45. After a usage limit, resume from the STATE file. If the limit lasts
past 20:30, buy nothing today and write that down.

Do not stop to ask, and do not use AskUserQuestion. Checkpoint the STATE
file after every step.

============================================================
STEPS
============================================================

S0 Startup. Read the last 40 lines of reports/stage_e28_STATE.md. Then
read:
- reports/stage_e28_pilot_spec.md (QM, sha256 8937740338e81103...)
- reports/stage_e28_briefs/R_spec.md (RS-01..13)
- reports/stage_e28_briefs/R_rank.md
- reports/stage_e28_briefs/A3_lead_rulings_v2.json
- reports/stage_e28_briefs/A3_ranking_table.md (head only)
- reports/stage_e28_briefs/work/B_pilot/README.md
Run E.28's start checks, quoted: the holdout status, `wc -c
REGISTRATION.md`, harness v14 2e908c81..., the spend ledger line count and
sha256, and N. Check that DATABENTO_API_KEY3 is present by NAME only
(empty or non-empty). Never read, print, copy or log its value.

S1 Code fixes. PilotCoder-OpusXHigh was cut at 16:43 while applying
RS-01..13 to work/B_pilot/ (its files changed between 16:37 and 16:41).
Diff the code against R_spec, finish whatever is missing, and make sure
the code matches the final QM spec (not the QG one). Then run both pilot
test suites. Use one worker (opus xhigh), or do it in the lead if only a
little is left. Still no Databento call.

S2 Delta review (DeltaReviewer-OpusXHigh, fresh context, one agent). It
checks three things:
(a) the v2 ranking against R_rank and the v2 rulings;
(b) the QM parameters in the spec;
(c) the code against R_spec and the spec.
It returns GO or NO GO, with any BLOCKING items. Fix every BLOCKING item
and re-check once. A NO GO that still stands means no purchase.

S3 Purchase. Do this only if all four hold:
- S2 returned GO;
- DATABENTO_API_KEY3 is non-empty;
- it is before 20:30;
- the spend gate passes.
Follow STAGE_E.28 Part B exactly:
- one contract (QM) and one schema (mbp-1);
- only account="acct-3", with E.28's own session id;
- a logged fresh quote first;
- the spend bound is all of acct-3's funds under its $125 cap (V45 item 2,
  confirmed by the user at 11:04 today);
- the data extends backwards and never reaches 2024-03-01 (request end
  2024-02-29T22:00:00Z);
- the download goes to /mnt/large-storage/market_data/PropExperiment/.
Then verify it against the manifest and write the line "ACCOUNT_3 SAFE TO
WIPE" with the time into the STATE file. If any condition fails, buy
nothing and record why.

S4 Measurement. Run the frozen-spec pilot measurement only if time and
usage remain (stop by 23:00). Otherwise leave it for a later stage, and
write down the exact command to run it.

S5 Return. Write reports/E.28_RETURN.md in the fixed sections of
STAGE_E.28, plus:
- reports/stage_e28_methods_brief.md and stage_e28_ranking.md, if not
  final yet;
- one progress.md entry;
- one docs/STAGES.md line;
- one final commit "Stage E.28 methods brief, ranking and pilot".
Do not push. The session cost section covers both sessions; it is never
estimated. As the last step, list every open choice in section 6.

END PROMPT
