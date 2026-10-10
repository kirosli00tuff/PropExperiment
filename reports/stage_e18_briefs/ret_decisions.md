## 7. Decisions for the user (the lead's recommendation first)

1. **The NG near-miss: accept the closure.** C1b FAILED on its registered bar (section 1). Per the freeze's section 8,
   the NG near-miss is closed, Gate 0's reading stands, nothing more is built on v2's model, and N is 480.
   - Recommended: no further NG variant on the v2 model, horizon or threshold. A different NG hypothesis would be a new
     pre-registration counted from N = 480, and must first pass V31's cost-feasibility gate.
   - What it cannot say: a fail does not separate "never real" from "real only in the 2019-2024 LNG-era regime"
     (section 8). The 2010-2019 sign is not even positive on the per-date mean in either test.
2. **What comes next: wait for the AiTrader readout, as V31 says.** Nothing in E.18 changes that. The data owned
   (2010-2019 stores for 17 roots, 2019-2024 for 27) stay on disk; any reuse needs a new pre-registration.
3. **Freeze-writing lessons, for every future pre-registration.** Recommended as standing rules (the lead can add
   them to docs/ORCHESTRATION.md's stage template if the user agrees):
   - Define each statistic's "mean" explicitly (per trade or per date) in the pass bar. C1's section 5 says "per-date
     mean" while the frozen code's criterion 1 uses the per-trade mean; it did not matter here, but it could at a
     boundary.
   - Dry-run every frozen guard on the frozen reference against the expected data state before registering (E.17's
     F-1; done here, and already a memory rule).
   - When a later stage re-registers an old freeze, re-read every factual sentence of the old text against what has
     happened since (here: "never read" and the harness clause).
4. **Housekeeping (no urgency).** Untracked files from earlier stages remain (the reports/stage_e12 and stage_e13
   evidence pages, .claude/worktrees/). Recommended: commit the evidence pages in a separate "evidence pages" commit or
   add their folders to .gitignore, and remove stale worktrees that hold no unmerged work.
