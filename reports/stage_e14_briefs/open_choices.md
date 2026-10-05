# Stage E.14 open choices (running list; the return's section 6 is built from it)

1. Calendar work started in parallel with the probe, not after it (the delegation table's "parallel, after 1"):
   the equity calendar is needed by C2 whatever the probe finds, and the C1-only groups (rates, FX, grains,
   energy, metals) and the release calendars were started at the same time so the night fits. If the probe
   drops C1, that work is wasted tokens only; no freeze, registration or N depends on it.
2. The probe worker builds the release calendars (NGS, WPSR, FOMC 2010-06..2019-05) after its probe, only if the
   probe's rule does not fire; the equity builder continues with rates, FX and grains from the same CME
   documents. Three calendar builders in total, as the prompt allows; the probe is its own worker.
3. GEX terms: SqueezeMetrics' terms bar "systematically retrieve data ... to create or compile ... a collection,
   compilation, database, or directory without written permission"; robots.txt is 404; the free DIX page offers
   the CSV through its own download button. Ruled: one download of the offered file for one registered test is
   not systematic retrieval; the terms do not forbid this use. The CSV and the Wayback copies stay uncommitted
   (DO_NOT_COMMIT.txt), hashed in the freeze, so the program does not redistribute it.
4. GEX timing: lag 1 (the latest row dated strictly before d). Sources, SqueezeMetrics' CSV page only: the
   server's Last-Modified (16:57 CT on the row's own date) and Wayback captures at 17:20-18:55 CT that already
   hold the same day's row (2020, 2025, 2026). Disclosed: 2011-2019 publication practice is not observable; the
   window's rows are unchanged since 2020-11-29 (hash comparison only, no value read).
5. Revision check: the window's GEX rows were compared across seven captures by sha256 of the rows, without
   reading or printing any value. Not a read of GEX values under the prompt's rule.
6. GEX count: computed on the calendar and GEX only, as Task 3 defines it; the roll blackout (needs bought
   symbology) is bounded as a disclosure (at most 96 dates), not used for the stop.
7. Hist stores (v10): bars inside a scheduled closure beyond the close minute are kept and flagged
   automatically (v9's keep-and-flag principle), fixed in code before any data exists, so no mid-stage hold.
8. Trial registry: a new append-only ledger, ledger/trial_registrations.jsonl (screening/trial_registry.py,
   baseline N = 471), because the only append-only trial ledger, ledger/ml_v2_config_ledger.jsonl, admits only
   ML v2 kinds through frozen code. The ES buy and the C2 run refuse without the registration (order of events
   enforced in code).
9. C2's cost: c = 0.976 + 0.5191 + 0.5428 = 2.0379 ticks (the table's printed values), bar 1.5c = 3.05685; the
   draft's "2.038" and "3.057" are its rounded display of the same sum.
10. C1's code lives in a new top-level package c1_replication/ (outside the harness directories and the v2
    freeze), hashed in C1's freeze, so neither harness v10 nor ml_route_v2/ changes for it.
11. The ES store holds trade dates 2011-05-02..2019-04-30: the first test date 2011-05-03 needs 2011-05-02's
    close. The test window itself is unchanged.
12. C1's E.12 state copy: ~/.cache/propexp_e14_c1/e12_state_copy (read-only), manifest
    reports/stage_e14_c1_e12_state_manifest.json (51 files, including gate0_run.json and gate0_DONE.json, which
    C17's list did not name; hashed too).
13. C2 stopped on its power rule at the Task 3 count (135 < 200; calendar-free bound 146), before its freeze
    and registration: not frozen, not registered, nothing bought. E14_SESSION_CAP_USD was set to 10.41 from the
    fresh ES quote (01:33) and reset to 0.00 (01:34) so v10 authorizes no spend. The es2011 plan, the ES store
    type and screening/stage_e14_c2.py stay in v10 as tested, inert code, in case the user decides to run C2
    under a new decision; nothing in v10 can buy ES while the cap is 0.00 and C2 is unregistered.
14. C1's registration N: with C2 unregistered, C1's later registration takes N from 471 to 473 (+2 on whatever N
    is then), not 473 -> 475 as the prompt anticipated when C2 was to register first.
15. The probe's NGS grade: an EIA release schedule (Wayback) is an "official" record of each release date, as
    calendar_rules.md defines; on that reading 0 of 52 2012 NGS dates are unsourced. On the stricter reading (an
    EIA record of each week's actual release) 1 is (2012-12-28), still within the rule's 2. Only a reading that
    requires each report's own "Released" line (27 weeks lack a capture) would fire, and the rule does not
    define the grade that way. Ruled: the rule does not fire; C1 continues.
16. Deviation (FreezeReviewer F-08): the GEX timing evidence and the revision check used seven Wayback captures of
    SqueezeMetrics' CSV; the prompt's source list names "SqueezeMetrics' public CSV page" and Wayback captures of
    official calendar pages, not Wayback captures of the CSV. Read-only, last-row dates and row hashes only; no
    verdict rests on them (C2 stopped on its count, which uses the fresh file alone).
17. Loader rulings in v10 before its commit (data/hist_calendar.py): a Friday-to-Monday session handover is
    contiguous in trade dates (the weekend is closed onto the earlier row); one day may hold one early halt and
    one late open (grains' day after Thanksgiving, as data/calendars/grains.py holds it). The builders' files
    were not edited.
18. C1 code rulings (C1Coder D-6, D-7, D-8): C7 as one sentinel bar per empty root dated 2019-05-31 (after the
    window); C12 excludes an NG date unsourced in any of the six groups or holding an unsourced release; Rule H-1
    literal (Sandy and 2018-12-05 get Topstep rows). Release rows with no instant are accepted only when listed
    as unsourced by id (WPSR 2012-11-01).
19. The E.14 session cap was set from a quote run before the v10 manifest, as E.12 did (the cap lives in frozen
    config); the quote is the prompt's "fresh quote-only run in this session". The C1 quote ran in the same window.
20. The lead wrote small code itself rather than spawn a worker for each (CLAUDE.md: small tasks inline): the GEX
    count script, the C1 freeze-input script, the two hist-calendar loader fixes with their tests, and the config
    comment. Each is covered by the Fable reviews; the loader fixes are in the v10 manifest.
21. C1Coder was resumed by SendMessage for one small follow-up (release rows with no instant), as CLAUDE.md allows
    for a small brief.
22. The FreezeReviewer reviewed C2's stop (terms, timing, count) instead of a C2 freeze, which does not exist.
    C2's freeze work file stays in reports/stage_e14_briefs/freeze_C2_work.md as a record only; it is not a freeze.
23. Commit messages: commit 2 reads "E.14 freezes, C1 and C2: C1 frozen; C2 stopped before its freeze" and the
    final commit "Stage E.14 C1 frozen, C2 stopped (not evaluated)" instead of the prompt's "... C2 evaluated",
    which would be false.
24. The return quotes the start and end checks verbatim except the 364 untracked E.12/E.13 DO_NOT_COMMIT page
    lines of `git status --short`, collapsed into one counted line; the full outputs are committed
    (reports/stage_e14_briefs/start_checks.txt, end_checks.txt).
25. The two coder worktrees (.claude/worktrees/agent-a94b80ceda0f5c25b, agent-a87e3dc1a4f58c0e5, branches with
    commits e577d55, 1169b71, 5c4a1cd) are left in place, uncommitted to main's history beyond the merged files;
    the user may delete them.
26. Times: the STATE file's task times were corrected from the transcripts where the lead's clock notes drifted
    (the C2 stop 01:34, not 01:42; the final GEX rerun 02:29; the freeze review 03:06-03:26).
27. The saved evidence pages (reports/stage_e14_briefs/pages/, 113 MB, about 1,800 third-party files) stay on disk,
    uncommitted, as in E.12 and E.13; the committed fetch logs, terms checks and calendar source tables hold every
    URL, fetch time and sha256 (pages/DO_NOT_COMMIT.txt).
