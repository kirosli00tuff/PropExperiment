1. **Built a real-data entry point (ml_route_v2/phase1) and froze it before any data.** The prompt
   assumed the pipeline could run Gate 0 on real bars; it ran on synthetic worlds only. Writing the
   loader after the purchase would have meant code written after data.
2. **Lead rules fixed before any spawn (P-1 to P-6)**: coverage (a signal whose leg is not owned is
   no feature), the Gate 0 list (A = every computed signal x 3, dead tests kept and counted: the
   conservative choice for Holm and N), S_X by D4's frozen rule (it reads research-store volume only,
   never a price), the subset rule's application (pass 1 = exactly the seven cluster-best, the
   literal reading; acct-1 first; 3% reserved per pick), the release-window rule counting the entry
   (it refuses every case the plain wording refuses and keeps D9.5's purpose), N_program 198 read
   from the stage records (no machine-readable N ledger exists).
3. **MES contingency P-1a**, added before the freeze because no Stage E loader had read MES's
   confirmation store. It fired: MES was refused (3 mislabelled rows), and 3 signals left the panel.
4. **The whole ranking on E|m_1|.** Live CME refused automated access, citing its terms, and 5
   vehicles had no 2026 figure anywhere; the prompt's failure path. The margin file is kept as the
   record only (its figures are unused; CME's terms argue against using even archived copies).
5. **150K tier boundaries** at exactly $2,000, $3,000 and $4,500 take the lower tier (the page is
   silent; conservative); $1,500 opens the 4-lot tier as XFA_50K encodes the same label. **Reset
   delay 2 trade dates** (Topstep's stated minimum; a lower bound); reset cost reported at both
   paths; Back2Funded not modelled.
6. **EC-K9**: unscheduled FOMC actions and the cancelled 2020-03-18 statement day excluded (not
   known at the member's entry intent, catalog R-07).
7. **Freeze review before the freeze commit**, so its fixes could not be a Gate 0 rule change after
   the commit; the first manifest (never committed) was deleted and rebuilt once. The review's
   commit-order item went to Gate0Verifier.
8. **v8 prepared in a git worktree in parallel** with the freeze, and the fresh quote run (which
   needs no harness preflight) before the v8 commit, so the session cap could be written into v8 as
   the prompt asks. Commit order kept: freeze, then v8, then the purchase.
9. **The freeze commit also holds** reports/stage_e12_briefs/rank_phase1.py (hashed by the manifest)
   and build_v2_freeze.py (the manifest's builder).
10. **Tests run without PYTHONPYCACHEPREFIX** (three harness bytecode tests fail under it, as in
    E.11). The end suite's 6 failures were all the real-ledger guard, tripped by the Task 7 quote run
    appending to the ledger during the suite; those files were rerun after the quotes finished.
11. **The purchase in four parallel processes** over disjoint roots (E.5's 9.6 s per chunk x 1,543
    chunks would have taken about 4 h serially); each process's quote, authorize and commit go
    through the gate; the caps could not be crossed (planned $133.72 against a $137.73 session cap).
12. **The subset is all 28** because the frozen rule found every exposure fitted the funds (about $6
    per full-size root); no phase-2 training-window item remains.
13. **The held stores went to the user** (AskUserQuestion), not decided by the lead: applying L-3
    needed a harness change beyond v8 (a guardrail) and dropping the roots would have been
    irreversible for the single Gate 0 run. The ruling file was written from the builder's own held
    summaries (24 bars, exactly), after every root had been attempted.
14. **Stores built as purchases completed** (build_ready_stores.py), 15 under v8 and 12 under v9;
    the phase-1 build reads both (their summaries carry their own harness sha256).
15. **Destructive git commands avoided**: a second worktree was added for v9 instead of resetting
    the first (the hook refused the reset). Both worktrees (../PropExperiment-e12-v8, -v9) are left
    for the user to remove (`git worktree remove`); nothing in them is needed.
16. **STATE times before 08:53 were lead guesses**, corrected from file times and transcripts.
17. **A context-hygiene slip**: one directory listing printed about 400 file names into the lead's
    context; no data rows were read.
