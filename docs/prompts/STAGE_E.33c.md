STAGE E.33c "ZM DISCOVERY SEARCH: AMEND THE COMPUTE LIMIT, FINISH THE 300, SELECT"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: E.33b registered the 300 configurations (r009-E33, N 538 -> 838)
and started the search on real data. The protocol's compute limit (P10's
3x rule) stopped it after 72 of 300 configurations, because the
synthetic probe behind the limit badly under-projected the real fold
times. The user chose option (a) (V53):
- amend the protocol to 0.3, setting only the compute reference from the
  real per-fold wall times already measured (no outcomes), with a 3x stop
  kept;
- hash 0.3, then resume the same registration from its DONE markers;
- finish all 300 configurations, then run P8 selection, Part D
  (statistics, independent recomputation, review) and Part E (finalists
  or a clean negative).
No result of any finished configuration may be opened before all 300 are
done.

Binding, in this order:
- the protocol 0.3 this stage hashes (0.2 plus the V53 amendment and
  nothing else);
- docs/prompts/STAGE_E.33.md (its rules, gates, Parts D and E, and the
  deliverable sections);
- this prompt;
- docs/DECISIONS.md V20 to V53.

Read first:
- reports/E.33b_RETURN.md
- reports/stage_e33_STATE.md (the "E.33b FINAL STATUS" block and its
  continuation command)
- the frozen pipeline list (freeze eb565a37)
- the briefs under reports/stage_e33_briefs/ and reports/stage_e33b_briefs/

Lead: Opus 5.5, effort xhigh. Ultracode OFF: this stage is mostly
compute plus a few named workers. Workers only where Part D needs them:
- StatsCoder: Opus xhigh.
- VerifyWorker: Opus xhigh, fresh context.
- StatsReviewer: Fable xhigh with the model confirmed from its
  transcript, or Opus xhigh in a fresh context if Fable is unavailable.
- A Haiku worker only for pure extraction or counting. Never Sonnet.
The user's rule: never sacrifice quality to save usage. Fewer agents is
not fewer checks: every check in STAGE_E.33.md Parts D and E runs.

Time: launched about 18:15 PDT on 2026-10-28, with no fixed end (V52,
V53). Checkpoint reports/stage_e33_STATE.md under an "E.33c" heading
after every step, and resume from it after any usage limit or reboot.
When the lead's context passes about 300k tokens at a quiet point,
write a full RESUME HERE block, add "READY FOR WIPE <time>", and stop:
the planner restarts a fresh session.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the choice
under Open choices in the return document, and continue.

============================================================
STEPS
============================================================

S1 Start gates, quoted verbatim:
- the protocol 0.2 sha256;
- the freeze eb565a37;
- the registration r009-E33 and N 838;
- the test-seal guard dry check;
- the holdout status;
- the harness;
- that the spend ledger is unchanged;
- that no outcome file of the search has been opened (state how this is
  known).

S2 The amendment:
- write protocol 0.3 as 0.2 plus one changed section, the P5/P10
  compute reference;
- the new reference is projected from the measured per-fold wall times
  in work/logs/search_real.log (wall times only) for the remaining
  configurations and feature sets, with the method written out and a 3x
  stop against it;
- produce a diff that shows nothing else changed;
- record the amendment beside the registration in the ledger, as the
  program does for amendments;
- AmendReviewer (Fable xhigh, model confirmed, or Opus fresh) checks
  that the diff touches only the compute reference and that no outcome
  was read to make it;
- hash 0.3.

S3 Resume: run the continuation command from the E.33b FINAL STATUS
block against the frozen pipeline (it refuses on any pin difference),
from the DONE markers. The 8 cut folds re-run once. Monitor memory (2 GB
rule) and the new 3x stop. If the new stop fires, stop and report; do
not amend again.

S4 Only after all 300 configurations are DONE (0 failed, or failures
counted as P8 says): Part D exactly as STAGE_E.33.md writes it:
- D1 P8 selection on all 300;
- D2 robustness of any passing candidate;
- D3 the full distribution beside B5's null;
- D4 the VerifyWorker's independent recomputation from the raw saved
  predictions;
- D5 StatsReviewer.

S5 Part E: freeze at most 3 finalists and draft the E.34 test
registration, or write the clean negative.

============================================================
DELIVERABLE
============================================================

Write reports/E.33c_RETURN.md in the sections of STAGE_E.33.md. Section 1
covers the whole E.33, E.33b and E.33c run:
- N;
- the null comparison;
- the finalists with net ticks per trade per firm, or the clean negative;
- what E.34 would buy.
Also write one progress.md entry and one docs/STAGES.md line, and make
one final commit "Stage E.33c ZM discovery search (completion)". Do not
push.

The last thing before ending: list every open choice in section 6.

END PROMPT
