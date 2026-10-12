## 6. Open choices (every decision the lead made on its own, with the reason)

Part A
1. **The 17 readers were spawned with the Agent tool, all at once, not inside a workflow.** The workflow runtime caps
   concurrent agents at 16; V36 and the prompt say all 17 at once with the same instructions and effort.
2. **Shared sources by assignment, not by a pre-fetch wave.** Baltussen et al. was already on disk (E.13's copy of the
   version of record), so every reader could grep it; each other cross-root source went to one class reader (NQ:
   Baltussen and Rosa; RTY: equity class and the macro calendars; ZN: rates class and the Aalto thesis; CL, ZC, LE:
   their classes). A pre-fetch wave would have added about 45 minutes of serial time.
3. **Feature-cut readings** (product summary 1.3): a table that a frozen rule derives from a calendar existing over
   both windows counts as existing (k1_vwap_dist, k5_ovr_*); partial availability from a window start, the warm-up or
   a session structure whose bars do not exist (rows then "missing", never "not applicable") does not drop a feature;
   undetermined calendars drop (k4_apipre_ret); a table not derivable from the program's calendars drops
   (k4_eiamom_r3's NYSE list); one pooled release column cannot be made product-specific, so g13-g15 drop as a group.
4. **RTY's fomc_r1 rejected** under rule (c): its published size is for SPY's 15:30-16:00 ET hold in 1993-2013, not for
   the t4-to-F hold on Russell; the plan review (PR-7) asked the written rule to state this refinement, which it now does.
5. **Excluded v2 families not re-admitted at t4** (K5-fomc-01, K6-wasdepost-01, k2_fomc_msince's reach): not in the
   frozen library's code, and F6 allows no added features; no reader proposed them with a published size.

Part B (H6)
6. **The H6 code was written by H6Coder-OpusXHigh, not by the lead.** The prompt's Step 2 says the lead writes the
   code; CLAUDE.md says the lead does not write bulk code. The lead wrote the text, ruled on every stop item and read
   the code paths the verdict rests on.
7. **T2's warm-up, the literal reading:** only eligible dates among the 60 trade dates before 2020-06-01 feed the first
   verdict thresholds; fewer than 60 means no threshold (59 were eligible, so T2 started a date late).
8. **T3, the literal reading of "previous trade date's GEX":** the row dated the equity calendar's previous trade
   date; after a futures-only holiday session there is no row, so no T3 trade (about 7 to 8 dates a year).
9. **GEX copy:** E.14's download reused (the NQ reader's reading of the terms), no new retrieval; rows on or after
   2024-03-01 cut at load.
10. **A sign count of GEX < 0 rows (148) was made before the freeze**, after T3's status was fixed, for the power
    record; disclosed in the prereg header and section 6 (review H6R-2).
11. **Registry names without hyphens** (the frozen registry's regex): E20H6-T1..T3 for E20-H6-T1..T3, E20S-01..45 for
    E20-S01..S45, E20B1-T1 for E20-B1.
12. **ENGINE_LEAD_IN_DATES = 1:** each engine run starts one trade date before its window with no entry, so the first
    window date has the D9.7 reference like every other date.
13. **The rulings file stays appendable:** the H6 freeze hashes a snapshot (reports/stage_e20_briefs/h6_rulings_at_freeze.md),
    because Steps 4, 5 and 9 append to reports/stage_e20_rulings.md.
14. **The first H6Reviewer stopped on the session usage limit** (11:21, no output); it was re-spawned fresh after the
    reset (15:12) rather than resumed, since it had written nothing.
15. **H6 evaluate ran detached** (setsid nohup), because a run-once evaluation that died with the session would leave
    the marker and no permitted rerun.

Part C (plan and search)
16. **E.12's recorded S_X** (ZF 2020-10-01, ZT 2021-10-01, the others 2019-05-06) instead of rerunning D4's rule, which
    reads research-window store bytes (F2 forbids them).
17. **MES is never loaded** (its features are cut by F6's leg rule; phase1_world would read its store by default).
18. **Four decision times allow four entries per product per date** (the v2 cap of 3 followed from three decision
    times and is read by no frozen module).
19. **rod_absratio's median is per vehicle and per t_index** (|r_ROD| grows with the time since the prior close).
20. **Composition, no v2 amendment:** pattern_search composes the frozen functions (the frozen run_pipeline cannot
    take t4 rows or skip Gate 0).
21. **Above-4.0 Sharpe fails the screen** (review PR-3, reading (a)); a clean leakage audit cannot convert it.
22. **B1 uses the fixed-D score_split construction** (review PR-5), the one behind the screen's record; the engine's
    path-dependent mechanics are excluded and named.
23. **The ruin probability is computed only after a passed screen** (review PR-6; no real-data engine path exists).
24. **The seven backward rulings of plan 10.1** (metals map and livestock calendar; LE 08:00-era t1 rows excluded;
    grains R-B1 exit; the daily cost fallback for release types without 2010-2019 rows; WPSR 2012-11-01 excluded;
    unsourced livestock dates excluded; frozen reopening labels).
25. **SearchCoder started before the PR-1 swap table existed** (16:21), building the parts already fixed; no fit before
    the reviewer's recheck and the Step 6 dry check.
26. **An independent SearchReviewer-FableXHigh** was added before the 45 registrations (CLAUDE.md: a Fable check of
    harness code a verdict rests on); the prompt names no code review for pattern_search.

Process
27. **Raw third-party pages stay uncommitted** (reports/stage_e20_briefs/pages/ and shared/ raw files;
    DO_NOT_COMMIT.txt), as E.13 and E.14 did; the fetch logs and notes are committed.
28. **A five-agent read-only code-map workflow** (opus high) mapped ml_route_v2 before the plan was written.
29. **check --world before the registration** (review SC-1): the real world was loaded once through the frozen loaders
    before the registry line, with no row, feature or fit, so a loader failure could be fixed without a post-registration
    change (F9 requires registration before any fit).
30. **The grid assertion on real bars was removed** (rulings section 7): the lead had added it at PR-4; the first real
    check --world refused on 7 NQ closure bars; the frozen V2.2b text replaces it with the L-3 booking check on real
    bars, and E.12 kept and counted closure bars (30 here). The first search manifest (66436234...) was deleted unregistered.
31. **Criterion 6's reading**: per-product round trips per path on the nested record, flagged when the median over the 5
    paths is below 30 (the median path, as criterion 2); the other readings are reported (rulings section 5).
32. **No commit before the search registration**: the prompt asks for commits only at the H6 and B1 freezes and at the
    end; the search registration carries the freeze manifest's sha256, and the end commit holds the manifest.
33. **The screen numbers got an independent Fable check** (CLAUDE.md), although the prompt's verifiers cover H6 and B1
    only; its first spawn stopped on the usage limit and it was re-spawned fresh at 20:12.
34. **The rulings and reviews are not in the search freeze manifest** (only the plan, code, tests and inputs), so the
    rulings file could take later sections; the plan pins the swap table by sha256 in its text.
35. **The cost table counts the workflow agents' transcripts** (subagents/workflows/), which reports/stage_e10_briefs/cost.py
    does not glob; reports/stage_e20_briefs/make_cost.py reuses cost.py's scan on all of them.
