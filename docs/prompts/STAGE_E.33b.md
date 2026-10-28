STAGE E.33b "ZM DISCOVERY SEARCH: FINISH THE FROZEN PROTOCOL RUN"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: E.33 (2d5a2ba) built the ZM discovery pipeline twice and proved
most of it, but two usage limits stopped it before the search. N is 538
and no real outcome was computed. This stage finishes exactly what E.33's
return (section 7 D1) lists, under the same frozen E.32 protocol and the
same rules. It runs nothing new and changes nothing frozen:
- the last synthetic proof seeds;
- the B3 rerun with the F3_11 ruling;
- LT1 and LT7 at their declared scale;
- the PipelineReviewer's remaining scope and its 3 SHOULD FIX items;
- the readings file and the pipeline freeze;
- C1 registration (N 538 -> 838);
- the feature store, labels and all 1,800 fits;
- Parts D and E.

Binding, in this order:
- the frozen protocol reports/stage_e32_discovery_protocol.md (sha256
  checked at start; refuse if it differs);
- docs/prompts/STAGE_E.33.md (all its rules, gates and deliverable
  sections, except its times);
- this prompt;
- docs/DECISIONS.md V20 to the latest entry.

Read first:
- reports/E.33_RETURN.md (all of it)
- reports/stage_e33_STATE.md (its RESUME HERE block and the numbered
  steps (1) to (8))
- the briefs under reports/stage_e33_briefs/briefs/

Workers from E.33 are gone. Start fresh ones from those briefs, and check
disk and DONE markers before redoing anything.

Lead: Opus 5.5, effort xhigh, Ultracode on (Max).
- Coders: Opus xhigh.
- Reviews: Fable xhigh, each model confirmed from its transcript. If
  Fable is unavailable or the transcript shows another model, use Opus
  5.5 xhigh in a fresh context and say so. Never Sonnet.
- At most 6 workers. At most 2 heavy compute jobs.
- The user's rule: never sacrifice quality to save usage. A usage-limit
  pause is fine; a skipped or rushed check is not.

Pre-registration decisions that must be on file before C1 (the planner
records them as a V-entry):
- E.32 D1: keep or drop the protocol-added test DSR (recommended: keep).
- E.33 D3: keep price-limit rule 5 for discovery as written
  (recommended), and count the affected dates and minutes on all 796
  dates.
If no V-entry records E.32 D1 when the lead reaches C1, stop before C1 and
report. Do not register.

Time: the window is set by the planner at launch. Allow at least 10
hours. Checkpoint reports/stage_e33_STATE.md (continue the same file,
with an "E.33b" heading) after every step. Resume from it after any usage
limit or reboot. If the window ends before C2 completes, stop after whole
parts, as E.33's rules require.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the choice
under Open choices in the return document, and continue.

SCOPE: as in STAGE_E.33.md. No Databento call. No test-window read
(2017-05-01 to 2020-11-30), and nothing dated 2024-03-01 or later. No
change to the frozen protocol, and no change to the pipeline after its
freeze except by a logged amendment with every affected configuration
re-run and counted. No live/, ops/, TopstepX or ProjectX. No key is
printed or logged. REGISTRATION.md stays 0 bytes. No push.

DELIVERABLE:
- reports/E.33b_RETURN.md, with the sections of STAGE_E.33.md (section 1
  covers the whole E.33 + E.33b run);
- one progress.md entry;
- one docs/STAGES.md line;
- one final commit "Stage E.33b ZM discovery search (continuation)". Do
  not push.
The last thing before ending: list every open choice in section 6.

END PROMPT
