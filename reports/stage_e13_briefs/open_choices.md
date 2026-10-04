# Stage E.13 open choices (working list for the return's section 6)

1. Task 1 split into three workers (PropVenues1, PropVenues2, BrokerVenues) instead of one: 14 firms plus brokers is
   too long for one context (CLAUDE.md: several short workers over one long one). The lead merged the parts.
2. The prompt's "reports/stage_e12_purchase.md and its JSON" do not exist. The 2010-extension quote record is
   reports/stage_e12_quotes_ext2010.md/.json, which was used.
3. No Databento quote run. E.12's record prices NG and every leg Task 4 needs, so the ledger is unchanged. The
   June-2010 partial chunks are not in that record; the next stage quotes them (CLAUDE.md requires a fresh quote
   before any spend anyway).
4. Task 2 tabulated ruin over a grid of drawdown sizes, so it did not wait for Task 1. The lead mapped the grid to
   the swing venues in the ranking.
5. Task 2 added a $10K capital level to the prompt's three examples, for V22's small personal account.
6. The lead appended an Elite Trader Funding question (section 4) to reports/stage_e13_phidias_question.md, from
   PropVenues1's suggested asks.
7. Lead error: the InfoSource brief gave docs/ for the K1-K8 catalogs, which are in reports/. The worker found
   them; no effect on the result.
8. Task 4 brief: the provisional rulings L4-1 to L4-7 (M1 first with a stated fallback rule, the threshold from
   persisted out-of-fold predictions, the window, the pass bar, the order of events).
9. Task 4 rulings on C1-C21: all accepted except C5 (a fixed start of 2010-06-07 for every root, with no volume
   read) and C6 (end 2019-04-30, with no May-2019 splice). C19 (funding) is left to the user.
10. Raw pages were saved under reports/stage_e13_briefs/pages/<Role>/ (CLAUDE.md: the stage's briefs folder).
    Pages from sites whose terms forbid automated access are listed in each folder's DO_NOT_COMMIT.txt, kept on
    disk and not committed, as E.12 did with CME's pages.
11. Deviation fetches (Fable R-11 count): two workers used Scrapling on sites whose terms forbid automated access
    before reading those terms: PropVenues1 (help.tradeify.co, elitetraderfunding.com) and PropVenues2
    (lucidtrading.com). BrokerVenues (NinjaTrader: no terms page, robots allows all) and InfoSource (Insper) were
    compliant. The lead's brief to the reviewer had said three; the correct count is two. Ruling: a fact stands on a
    compliant corroborating copy; otherwise it is marked "deviation fetch" (P1-19, P1-21, P1-37, Lucid's TOU). No
    classification rests on those alone. InfoSource's Firecrawl-before-Scrapling fetch of the Baltussen PDF is
    recorded in INF's lead note.
12. The C1 pre-registration rules over its annex where they differ. Its power figures are noted as about 3%
    optimistic for the ruled window.
13. AiTrader readout facts come from its plan documents only (docs/STAGES.md, its git log), not from its results.
14. E.12's persisted Gate 0 state in ~/.cache/propexp_e12_phase1 was not hashed in this stage, to avoid opening
    result files (names and sizes only). The next stage's freeze hashes and copies it (ruling C17).
15. The ranking rule was fixed in section 1 before the candidates were scored: odds first; the tie-breaks are
    published evidence, then test independence, then fit; ease never decides.
16. The ranking's odds for C2-C5 are the lead's judgment, with ranges. C1's come from the Task 4 annex.
17. C2's bar applies 1.5c at the test era's costs, a conservative choice because costs were a larger share of the
    move at 2011-2019 index levels.
18. C2's GEX timing rule (the latest row strictly before d, or two days back if publication can fall after 14:30
    CT) and its 200-date minimum-power stop.
19. Correction before the review: ranking section 5 first applied test independence ahead of evidence,
    contradicting section 1. The lead corrected the order to follow section 1 (C2 first, C1 second) rather than
    change the rule.
20. STATE times were corrected from the output files' modification times. The final table uses transcript times.
