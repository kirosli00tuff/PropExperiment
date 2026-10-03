# Stage E.10 Task 6: the lead's rulings on the Fable review

Lead (Opus 5.5, xhigh), 2026-10-02 23:58 to 2026-10-03 PDT. Review: reports/stage_e10_catalog_review.md
(CatalogReviewer-FableXHigh, 23:31-23:55; BLOCKING 0, SHOULD FIX 8, NOTE 8; all 123 quoted passages
re-verified, none fabricated or misread). Every SHOULD FIX finding is ruled below and applied to the draft
catalog (reports/stage_e10_catalog_K9.md and .json) and to docs/STAGE_E_DESIGN_K9_DRAFT.md. The notes are
ruled too. No Stage E result enters any ruling.

## Outcome

**K9 draft after the review: 1 active member, K9-anncday-01, on 3 exposures (MNQ, M2K, MYM): 3 trials.
Projected program N = 198 + 3 = 201.** Two drafts are withdrawn and kept in full in the catalog's appendices
for the user to reinstate: A, K9-vixback-01 (round 2); B, K9-vixspike-01 (this ruling, R-01).

## SHOULD FIX findings

**R-01 (K9-vixspike-01 against X10): accepted; the member is withdrawn.** The design target fixed the
borderline test before any source was read: a volatility-spike member differs from X10 only if "the condition
reads a volatility level, not the sign of the last move". The member's condition is a one-day change in VIX.
The source itself says "the correlation between daily returns and daily changes in VIX is close to -70%". Its
Table 8 shows next-day returns after large price drops alone that are positive and larger than the member's row
(only less significant, on 5-16 days a year; R-04). So the source's own data do not separate the uncertainty
premium from a reversal of the spike-day fall. Reading "level" to cover a one-day change would relax a
pre-declared test after reading the source, and the lead does not do that. The member moves to Appendix B,
"Withdrawn draft", with its full specification and with R-03, R-04, R-05 and R-09 applied there. The user may
reinstate it at E.11 by widening the borderline test explicitly. If reinstated: the cutoff (R-05), and a
pre-stated descriptive reversal diagnostic (the mean trip P&L on signal days whose vehicle day-session return
was non-negative, reported beside the overall mean; descriptive only, it changes no tier).

**R-02 (K9-anncday-01 against D.1's E-H1 and E.0's K1-predrift-01 exclusion): ruled; the member stays, and
the ruling is written into its exclusion-list check.** Grounds:
1. The frozen design leaves announcement members to each cluster's own literature. D6 lists among the
   families not ported "E calendar and events (each cluster writes its own announcement members from its own
   literature, which is more specific than MES's E-H1)" (docs/STAGE_E_DESIGN.md line 381). K9-anncday-01 comes
   from its own literature (Ai-Bansal-Guo; Savor-Wilson).
2. E-H1's D.1c verdict on MES was a non-resolution (underpowered), not a null. The hypothesis was not rejected,
   so re-testing a related one is not repeating a failed family.
3. The member differs from E-H1 in date set (six release types, including GDP, ISM manufacturing and PPI when
   earlier, against FOMC, CPI and NFP), in hold (the whole announcement day, including the release response,
   against a stop at the release), in exposures (three traded equity indices; MES is not traded in Stage E),
   and in source.
4. E.0's K1-predrift-01 exclusion rested on the E.0 K1 brief, which allowed MES families in K1 only through the
   core ports. That brief does not govern K9. The E.10 prompt scopes the exclusion list to families Stage E
   tested.

The risk is real and goes to the user as a decision (design draft K9-G): cut K9-anncday-01 for consistency with
E.0's K1 exclusion, or keep it (recommended). The Excluded table's pre-announcement row gains E-H1 as a further
reason (its window is E-H1's window).

Correction recorded here (the design target is hashed and not edited): X4's "Members tested" cell lists
K1-predrift-01. It was excluded at E.0 with 0 trials and never screened. Only K2-predrift-01 was tested.
X4's mechanism exclusion is unchanged.

**R-03 (K9R-006 and the source-overlap label): accepted, fix (a).** K9R-006 is removed from the member's
evidence and from the JSON `sources`. Section 5 keeps it as "read in round 2 after selection; monthly
horizon; not used". This supersedes the lead's item-19 ruling, which created a category section 3 does not
have. Applied inside Appendix B, since the member is withdrawn.

**R-04 (Table 8 gloss): accepted.** Reworded to the source's claim: "positive, of comparable or larger size,
statistically insignificant on 5-16 days a year". Moved into the X10 risk paragraph (Appendix B).

**R-05 (the cutoff rule): accepted.** The lead's round-1 choice of 1.0 over 1.5 applied (b)1. The source's
0.5 row (68.0 days a year, 7.87 bps, t 2.28 on 1994-2018; 4.84 bps, t 1.62 on 1986-2018) was not in the
lead's view, and no rule picked 1.0 over 0.5. The applied rule was in effect "the largest cutoff whose count
clears 40", a rarity preference that the design target's reading 3 (prefer the upper end of the band) argues
against. Appendix B states this. If the member is reinstated, the user chooses one cutoff: 0.5 (meets (b)1
with margin, about 62 capped trips, weaker per-trip move) or 1.0 (needs the (b)1 waiver).

**R-06 (the D-entry amendment): accepted.** The round-2 change (reopen entries as intent on the 17:59 CT bar,
filled at 18:00 CT) was made after sources were read, on a non-result ground. It is now a user decision in the
design draft (new section K9-H), with the D9.4 reasoning, the K8-wkndbtc-01 precedent, the transfer cost (the
15:00-18:00 CT part of the source's close-to-close return is not held) and the alternative (the 17:00 CT first
bar, as D-entry was fixed). The rulings' phrase "a frozen constraint and precedent" overstated it. It is a
judgment that extends a precedent set for the Sunday reopen to the weekday reopen after a one-hour halt. The
draft catalog keeps 18:00 pending that decision. Lead recommendation: 18:00. The cost is one hour of a 21-hour
hold, and it keeps every K9 fill away from the reopen minutes that D9.4's conduct rule and the K8 precedent
treat as gapped.

**R-07 ("known in advance" for rescheduled BLS releases): accepted.** The about 8 announcement dates moved
by the October-November 2025 lapse in appropriations are flagged [unverified: date announced before the
entry intent]. These are Employment Situation 2025-11-20, 2025-12-16 and 2026-02-11, and CPI 2025-10-24 and
2025-12-18, plus the PPI dates where they set the inflation date. E.11 fetches BLS's revised-schedule notice
and keeps a date only if its announcement precedes the entry intent (17:59 CT the evening before). Otherwise
the date is dropped. The entry states that E.12's harness uses the date set as known at the entry intent.
Worst case, all 8 are dropped together with R-12's holiday exclusions: about 50 dates before the cap,
about 47 scaled to the 299 screened dates. That is still above the 40-trip margin; the writer's recount in
the catalog governs. No further fetch is run in E.10.

**R-08 (the pre-announcement row): accepted.** "Weak" is replaced by the source's statement: "stable and
significant across all three subperiods ... 6.98 basis point and statistically significant" in 2012-2018
(P-K9C-006-e). The row and design draft K9-G gain two facts for the user's comparison. (i) The variant's
source (HPWZ, sample to May 2018) is not source-overlap, while K9-anncday-01 is. (ii) The source reports that
the post-announcement segment the member adds has small and insignificant returns with large variances
(P-K9C-006-c). The variant stays excluded: it is a hold-window variant of K9-anncday-01 under the no-grids
rule, and its window is D.1's E-H1 window (R-02). It is offered as the alternative literal set. Lead
recommendation: keep the full-day member. It is the full-session form K9 exists to test, and the variant would
re-run E-H1's window on the same research window as MES. The trade-off (the variant's clean label and lower
variance) is stated for the user.

## NOTES

- **R-09:** applied in Appendix B (the "40 of 202" derivation restated).
- **R-10 (provenance times): acknowledged.** The design target's header reads "22:40-23:10 PDT". That was the
  lead's planned slot, written before the file was finished. The file's mtime (22:29:01), the hash
  (22:29:07, reports/stage_e10_briefs/design_target.sha256) and the STATE row (22:24-22:29) place it before
  the readers started (22:32). The header is not edited, because that would break the recorded hash. STATE's
  "written 23:32" for the design draft is corrected to its mtime, 23:24, in the final STATE pass.
- **R-11:** closed. The author manuscript of the JFE version states the same sample (September 1994 to May
  2018). This only matters if Appendix B is reinstated; its label would be "not source-overlap".
- **R-12 (holiday sessions): accepted, and it amends round 2 item 14.** As in K8-wkndbtc-01, an announcement
  date that the program's calendar marks as an early close, early halt or closure for equity-index futures is
  excluded: no trade. Examples: 2025-07-03 (Employment Situation, early close) and 2026-04-03 (Good Friday,
  Employment Situation). Thanksgiving-week and Christmas-week dates are treated the same. The forced flatten
  at F still governs any position open at an unscheduled halt. The writer recounts the date set.
- **R-13:** acknowledged. cost_wall.json is byte-identical (sha256 8ef052dc...); its mtime moved.
- **R-14:** acknowledged. It matters only if Appendix B is reinstated.
- **R-15:** acknowledged. Appendix A's withdrawal stands.
- **R-16:** acknowledged. Appendix B states the mixed-sample ratio as conservative.

## Addendum: the writer's round-3 question Q21 (lead, 2026-10-03 00:08 PDT)

**Q21 (BEA GDP dates moved by the lapse: 2025-12-23, 2026-01-22, 2026-02-20, 2026-04-09): the same rule as
R-07.** E.11 fetches BEA's revised release schedule and keeps each date only if it was announced before the
entry intent (17:59 CT the evening before); otherwise the date is dropped. The writer's recount already covers
the worst case. With every flagged BLS and BEA date dropped: 49 dates before the cap and 47 after, or 46.4 and
44.5 scaled to the 299 screened dates. That is still above the 40-trip margin.
