1. **Budget.** Three planning-chat messages before any quote set the budget at $122.50, then $126.30, then FINAL
   $124.00 (commits 5f9671d, 7447677, 8e5707c). The last one governed (ruling B-1). At about 01:21 the user wrote
   "theres 125 total on the account. use all if needed". A3 rerun at $125.00 selects the same 11 roots, and the
   selection and fallback list were already registered, so nothing changed (B-2).
2. **Order: quote, v11, register, buy.** The hand-off's steps 5-7 and C1's freeze section 11 put the fresh quote first.
   The prompt summary lists "harness v11, fresh quote". The quote ran first under v10, as E.15 did, because v11's caps
   need the fresh total.
3. **E.17's own scripts.** The scripts are copies of E.15's with output paths changed, so no earlier stage's file
   was overwritten:
   - check script (adds the E.14 inputs check and the E.16 freeze verification);
   - freeze verifier;
   - hash-file writer.
   The calendar hash file is byte-identical to E.15's.
4. **The guard was generalized** to both plans and A1's budget. It was dry-run on E.15's failed lines, which it
   refused. The A3 selection script was written before any quote (18:43-18:45) and reads no market data.
5. **v11's test assertions.**
   - tests/test_e14_pull_hist.py:196 also pins E14_EXT2010_SESSION_CAP_USD and failed on v11. The freeze's citation
     list omits it, so it was changed under the freeze's governing words "the test assertions that pin those two
     values" (V11-R1; Fable agreed).
   - test_stage_e_config_v8.py's pinning assertions are lines 64-65, not 62-64 (E.15 item 14). The dropped
     `funds >= cap` (V11-R2) became a value pin.
6. **Commits hold only what they name.** The v11 and v12 commits hold only harness files; the ledger's quote and buy
   lines went into "E.17 C1 evaluated" and the final commit. The commit "E.17 C1 evaluated" uses the prompt's name:
   C1 was evaluated once, and its verdict is STOPPED.
7. **The C1 buy interrupted by the session end.**
   - The first Claude session ended at about 19:38 and its background shell took the buy with it, after 33 settled
     chunks. NG 2013-03 had been committed ($0.075002) without a settle, and it left no file.
   - The identical command resumed at 19:42:33; the tool skips settled chunks.
   - The orphan commit stays in the ledger and is counted as spend (conservative): $57.817332 against the
     $57.742330 quote.
   - Every long job after that ran detached (setsid nohup) with an rc line in its log.
8. **C1 STOPPED, not rerun.** The C10 stop is the freeze's rule applied as written; the freeze says a C10 stop closes
   the attempt, and the prompt forbids a second run (C1-R1, C1-R2). The Fable check after step 7 verified the STOP
   (C1-R5), because no verdict statistic existed to recompute. A6 did not apply (NQ and ZN were bought), so H2 stayed.
9. **v12 in a worktree; the quote before the commit.**
   - The coder worked in an isolated git worktree. The lead applied its diff (sha256 5f68cc84...) on main.
   - The ext2010h quote ran on the uncommitted, Fable-reviewed v12 with the caps at 0.00. Quote-only takes no
     harness sha; E.12's open choice 7 is the precedent. This put the caps into the single v12 commit the prompt
     names.
   - The coder's worktree (.claude/worktrees/agent-a463ba71418f7066b) was removed at the end.
10. **F-1 made `--roots` mandatory for an ext2010h buy** (Fable SHOULD FIX). It is a tightening inside
    data/pull_hist.py, a file v12 changes anyway.
11. **v12's caps.**
    - ACCOUNT_2_CAP_USD = acct-2's spend after C1 + the A3 selection's quote x 1.03, rounded up: 355.38. That is the
      hand-off's formula with the selection's total in place of the 21-root total, as A1 and A3 require.
    - The session cap is $65.82, not the formula's $65.95. That tightening lets 4 concurrent buy processes (each able
      to overshoot by one in-flight chunk, the largest $0.115211) stay within $124.00 (V12-R3; Fable checked: worst
      case $123.99).
12. **Four buy processes over disjoint roots** (E.12's precedent). This cut the base-rule buy to 56 minutes. The C1 buy
    had run serially at about 17 s a chunk.
13. **A3's "budget left" falls by each taken root's quote x 1.03**, not by the bare quote (conservative, consistent
    with the caps).
14. **Step-2 stores in the run manifest.** They were taken from reports/step2/bars_<ROOT>.json, E.12's store
    summaries. The hand-off calls it "E.12's start-rule file", but no file by that name exists. Each sha256 was
    checked on disk.
15. **A pre-marker dry check before the H registration** (lesson from C1). It ran on a scratch manifest at 22:52 and
    again on the real one at 01:31: base_rules' freeze check, context build and store preflight, with no bar read
    and no marker. It is not part of the frozen procedure and changed nothing.
16. **A descriptive look at H1's units** right after H1's run (gross versus cost). H2-H4 were frozen and could not be
    affected. It is reported as descriptive and adds nothing to N.
17. **The H-verification brief carried three run numbers.** After the runs the lead appended "focus points" quoting
    H1's mean and t and H5's per-case sd, to direct Fable's checks to costs and H5's scaling. The prompt asks Fable to
    work "without reading the lead's statistics first". Fable still recomputed every number from the units and stores,
    but this is a departure, and it is recorded here.
18. **Times.** Several STATE entries were first written with estimated times and corrected the same minute from
    `date` and file times (memory rule). The user's 01:21 message was first logged as 00:33 and corrected.
19. **No Firecrawl, web search or other network use** besides Databento's quote, buy and free metadata calls.
20. **The untracked ..env.swp** at the repo root (an editor swap file) was never opened, read, staged or committed
    (section 7).
