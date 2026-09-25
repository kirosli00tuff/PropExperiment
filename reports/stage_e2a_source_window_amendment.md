# Stage E.2a Task 11: source-window amendment (source-overlap labels)

Written by the Stage E.2a lead (Opus 5.5, xhigh) on 2026-09-25 at about 06:15 PDT, before any confirmation read of any
Stage E member (no confirmation-window data exists on this machine for any new product). Authority: the user's decision V9
(docs/DECISIONS.md, 2026-09-25): "the source windows of the source-overlap members may be recorded before any confirmation
read, as a separate audited amendment that can only remove a source-overlap label, never add a member, change a rule, or add a
label". This file is that amendment. It edits no frozen file: reports/stage_e0_catalog*.md and .json and
docs/NULL_CRITERIA_E.md stay as frozen by reports/stage_e1_freeze.json; a member's label is read from the frozen catalog and
then from this amendment.

Input: reports/stage_e2a_source_windows.json (Task 2, SourceWindowReader-OpusHigh), sha256 f2442dcc07566216e29b8190efc098369524497573aeb3c06d4e3b97bb50d7f9: 37 members, 75 sources,
145 (member, source) rows, each with a quoted passage checked verbatim by script, or "unknown".

## The rule, and how it is applied

Frozen rule (docs/NULL_CRITERIA_E.md section 3): "A member whose supporting source's sample overlaps its confirmation window
was chosen partly on evidence from that window ... Such a member is labelled 'source-overlap' ... a member whose source window
is not recorded is treated as source-overlap." The stage prompt (Task 11): "A member keeps its label when any of its sources
overlaps the confirmation window or is 'unknown'." Applied mechanically, with these readings (all in the direction that
keeps labels):

- Confirmation window: [2019-05-06, 2024-02-29], the widest it can be (the earliest possible S_X to the frozen end;
  each member's own S_X is not known until its cluster's step 2 purchase, and a later S_X can only shrink the window).
- A source's window runs from the first day of its first period to the last day of its last period at the passage's own
  granularity ("2019" ends 2019-12-31; "2020-05" ends 2020-05-31). Overlap iff the window and the confirmation window share a day.
- "Any of its sources": every source the entry cites, supporting or other (the prompt's words; the frozen rule's
  "supporting source" is the narrower reading, reported beside it for information, not adopted).
- A source recorded "unknown" keeps the label. The one window quoted only from another source's description of the
  paper (K3-025, "secondary_passage") is treated as unknown.
- A product or calendar document with no data sample (window_applicable false: K6-048, K6-050, R-K3-014, the ECB page)
  has no sample to overlap; it neither keeps nor removes a label.
- A member loses the label only if every source is "no overlap" or "no data sample".

## Result

**Labels removed: 6 of 37**: K2-predrift-01, K3-ldnmom-01, K3-mehedge-01, K4-ngpre-01, K8-flight-01, K8-oilcad-01. The other 31 keep "source-overlap". No member is added, no rule changes, no label is added.

For information only (not adopted): the narrower supporting-only reading would remove 8: K2-predrift-01, K3-ldnmom-01, K3-ldnrev-01, K3-mehedge-01, K4-ngpre-01, K5-pmfix-01, K8-flight-01, K8-oilcad-01.

| Member | Before | After (governing) | Supporting-only reading | Sources: classification [window] |
|---|---|---|---|---|
| K1-cp1-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1-A10 (supporting): overlaps [1974-12..2020-05]; D1-A28 (supporting): no overlap [1993..2013]; D1-A10 (other): overlaps [1974-12..2020-05]; R-K1-067 (other): no overlap [2006..2011]; R-Rosa2022 (other): unknown; K3-040 (other): unknown |
| K1-cp3-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1f-Crabel1990 (supporting): unknown; D1-B4 (supporting): no overlap [1983-03-30..2011-01-26]; D1-D11 (supporting): unknown; K1-002 (other): overlaps [2011-01-03..2021-12-31] |
| K2-cp1-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1-A10 (supporting): overlaps [1974-12..2020-05]; D1-A28 (supporting): no overlap [1993..2013] |
| K2-cp2-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1-B5 (supporting): overlaps [2021-12..2025-08]; D1-B2 (supporting): no overlap [2014..2016]; D1-B3 (supporting): no overlap [2010-05-03..2010-05-06] |
| K2-cp3-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1f-Crabel1990 (supporting): unknown; D1-B4 (supporting): no overlap [1983-03-30..2011-01-26]; D1-D11 (supporting): unknown |
| K2-monthend-01 | source-overlap (fallback) | **source-overlap** | source-overlap | K2-021 (supporting): no overlap [1990-01..2018]; K2-003 (supporting): overlaps [2016-01..2025-12]; K2-005 (other): no overlap [2009-03..2011-06] |
| K2-predrift-01 | source-overlap (fallback) | **not source-overlap** | not source-overlap | K2-007 (supporting): no overlap [2008-01-01..2014-03-31] |
| K3-cp1-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1-A10 (supporting): overlaps [1974-12..2020-05]; D1-A28 (supporting): no overlap [1993..2013]; K3-010 (other): overlaps [2012..2024] |
| K3-cp2-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1-B5 (supporting): overlaps [2021-12..2025-08]; D1-B2 (supporting): no overlap [2014..2016]; D1-B3 (supporting): no overlap [2010-05-03..2010-05-06] |
| K3-cp3-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1f-Crabel1990 (supporting): unknown; D1-B4 (supporting): no overlap [1983-03-30..2011-01-26]; D1-D11 (supporting): unknown |
| K3-ecbfix-01 | source-overlap (fallback) | **source-overlap** | source-overlap | K3-016 (supporting): no overlap [1999-01..2018-12]; K3-023 (supporting): no overlap [1997-01..2007-06]; K3-024 (supporting): no overlap [1993-01..2005-08]; K3-025 (supporting): unknown (secondary passage only) [1977..1991]; K3-004 (supporting): no overlap [2002..2013]; K3-hdr-ECB (other): no data sample (cannot overlap) |
| K3-ldnmom-01 | source-overlap (fallback) | **not source-overlap** | not source-overlap | K3-017 (supporting): no overlap [1996-02..2013-12]; K3-002 (supporting): no overlap [2006-01-02..2016-06-30]; K3-021 (supporting): no overlap [2008-01..2014-03]; K3-019 (other): no overlap [2010-10-28..2017-06-14]; K3-004 (other): no overlap [2002..2013]; K3-018 (other): no overlap [2010-01-01..2013-12-31] |
| K3-ldnrev-01 | source-overlap (fallback) | **source-overlap** | not source-overlap | K3-002 (supporting): no overlap [2006-01-02..2016-06-30]; K3-003 (supporting): no overlap [2004..2013]; K3-018 (supporting): no overlap [2010-01-01..2013-12-31]; K3-001 (supporting): no overlap [2004-04-28..2012-12-31]; K3-019 (other): no overlap [2010-10-28..2017-06-14]; K3-020 (other): overlaps [2015-02-15..2023-12-31]; K3-016 (other): no overlap [1999-01..2018-12]; K3-017 (other): no overlap [1996-02..2013-12] |
| K3-mehedge-01 | source-overlap (fallback) | **not source-overlap** | not source-overlap | K3-001 (supporting): no overlap [2004-04-28..2012-12-31]; R-K3-014 (other): no data sample (cannot overlap); K3-002 (other): no overlap [2006-01-02..2016-06-30] |
| K3-tkypost-01 | source-overlap (fallback) | **source-overlap** | source-overlap | K3-016 (supporting): no overlap [1999-01..2018-12]; K3-005 (supporting): overlaps [2018..2020]; K3-022 (other): no overlap [1999-01..2013-12] |
| K3-tkypre-01 | source-overlap (fallback) | **source-overlap** | source-overlap | K3-022 (supporting): no overlap [1999-01..2013-12]; K3-005 (supporting): overlaps [2018..2020]; K3-016 (other): no overlap [1999-01..2018-12] |
| K4-cp1-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1-A10 (supporting): overlaps [1974-12..2020-05]; D1-A28 (supporting): no overlap [1993..2013]; K4-037 (other): no overlap [2006..2018]; K5-028 (other): overlaps [2009-01-01..2020-03-31] |
| K4-cp2-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1-B5 (supporting): overlaps [2021-12..2025-08]; D1-B2 (supporting): no overlap [2014..2016]; D1-B3 (supporting): no overlap [2010-05-03..2010-05-06]; D1-B4 (other): no overlap [1983-03-30..2011-01-26]; D1-B2 (other): no overlap [2014..2016]; K4-050 (other): overlaps [2010..2026] |
| K4-cp3-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1f-Crabel1990 (supporting): unknown; D1-B4 (supporting): no overlap [1983-03-30..2011-01-26]; D1-D11 (supporting): unknown; K5-028 (other): overlaps [2009-01-01..2020-03-31] |
| K4-ngpre-01 | source-overlap (fallback) | **not source-overlap** | not source-overlap | K4-001 (supporting): no overlap [2003-03..2018-12] |
| K5-cp1-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1-A10 (supporting): overlaps [1974-12..2020-05]; D1-A28 (supporting): no overlap [1993..2013]; K5-028 (other): overlaps [2009-01-01..2020-03-31]; R-Rosa2022 (other): unknown |
| K5-cp2-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1-B5 (supporting): overlaps [2021-12..2025-08]; D1-B2 (supporting): no overlap [2014..2016]; D1-B3 (supporting): no overlap [2010-05-03..2010-05-06]; K5-008 (other): overlaps [2020-01..2021-09] |
| K5-cp3-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1f-Crabel1990 (supporting): unknown; D1-B4 (supporting): no overlap [1983-03-30..2011-01-26]; D1-D11 (supporting): unknown; K5-028 (other): overlaps [2009-01-01..2020-03-31] |
| K5-pmfix-01 | source-overlap (fallback) | **source-overlap** | not source-overlap | K5-001 (supporting): no overlap [2007-01-01..2012-12-31]; K5-012 (supporting): no overlap [2012-02-14..2015-04-30]; K5-006 (supporting): no overlap [2008-01-01..2018-06-27]; K5-013 (other): unknown |
| K5-preauc-01 | source-overlap (fallback) | **source-overlap** | source-overlap | K5-002 (supporting): unknown; K5-019 (other): no overlap [2006-11-24..2012-12-31]; K5-020 (other): no overlap [2008-01..2016-04]; K5-012 (other): no overlap [2012-02-14..2015-04-30] |
| K6-cp1-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1-A10 (supporting): overlaps [1974-12..2020-05]; D1-A28 (supporting): no overlap [1993..2013]; R-Rosa2022 (other): unknown; R-K6-032 (other): overlaps [2010-01..2021-11] |
| K6-cp2-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1-B5 (supporting): overlaps [2021-12..2025-08]; D1-B2 (supporting): no overlap [2014..2016]; D1-B3 (supporting): no overlap [2010-05-03..2010-05-06] |
| K6-cp3-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1f-Crabel1990 (supporting): unknown; D1-B4 (supporting): no overlap [1983-03-30..2011-01-26]; D1-D11 (supporting): unknown |
| K6-crushgap-01 | source-overlap (fallback) | **source-overlap** | source-overlap | K6-001 (supporting): no overlap [1978-02-01..1991-07-31]; K6-026 (supporting): no overlap [2015..2015]; K6-008 (supporting): no overlap [1985-01..1995-02]; K6-044 (supporting): unknown; K6-050 (other): no data sample (cannot overlap) |
| K6-limitcont-01 | source-overlap (fallback) | **source-overlap** | source-overlap | K6-002 (supporting): no overlap [1991-01-07..2016-05-23]; K6-003 (supporting): unknown; K6-035 (other): overlaps [2014..2019]; K6-048 (other): no data sample (cannot overlap); K6-018 (other): no overlap [1985..2018]; K6-023 (other): no overlap [2011..2015] |
| K6-wasdepost-01 | source-overlap (fallback) | **source-overlap** | source-overlap | K6-037 (supporting): no overlap [1999..2017]; K6-028 (supporting): overlaps [2013..2020]; K6-011 (other): overlaps [2009..2019]; K6-015 (other): no overlap [2009-07..2012-05]; K6-014 (other): no overlap [2010-06..2014-05] |
| K7-cp1-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1-A10 (supporting): overlaps [1974-12..2020-05]; D1-A28 (supporting): no overlap [1993..2013]; K7-011 (other): overlaps [2013-01-01..2020-12-31]; K7-018 (other): overlaps [2013-03-03..2020-05-31] |
| K7-cp2-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1-B5 (supporting): overlaps [2021-12..2025-08]; D1-B2 (supporting): no overlap [2014..2016]; D1-B3 (supporting): no overlap [2010-05-03..2010-05-06]; K7-022 (other): overlaps [2012..2022]; K4-050 (other): overlaps [2010..2026] |
| K7-cp3-01 | source-overlap (fallback) | **source-overlap** | source-overlap | D1f-Crabel1990 (supporting): unknown; D1-B4 (supporting): no overlap [1983-03-30..2011-01-26]; D1-D11 (supporting): unknown; K7-040 (other): overlaps [2015-10-08..2024-10-15]; K7-041 (other): overlaps [2018-01..2025-06] |
| K7-rev2h-01 | source-overlap (fallback) | **source-overlap** | source-overlap | K7-012 (supporting): no overlap [2015-03-01..2018-06-27]; K7-002 (supporting): overlaps [2019-04-01..2020-01-31]; K7-025 (supporting): no overlap [2024-03-05..2024-09-06]; K7-042 (other): overlaps [2018..2025]; K7-018 (other): overlaps [2013-03-03..2020-05-31]; K7-011 (other): overlaps [2013-01-01..2020-12-31]; K7-022 (other): overlaps [2012..2022] |
| K8-flight-01 | source-overlap (fallback) | **not source-overlap** | not source-overlap | K8-003 (supporting): no overlap [2007..2018] |
| K8-oilcad-01 | source-overlap (fallback) | **not source-overlap** | not source-overlap | K8-006 (supporting): no overlap [2005-01-03..2009-12-31]; K8-001 (supporting): no overlap [2003-10..2017-10] |

## Notes

- The 16 members already labelled source-overlap in the frozen catalog are outside V9's fallback list (reports/stage_e1_freeze_rulings.md,
  FA-06) and are unchanged.
- Holdout-2 is not the confirmation window, so a source whose sample covers holdout-2 dates does not bear on this label; one
  such source is K7-025 (2024-03-05..2024-09-06, cited by K7-rev2h-01, which keeps its label on other sources). Recorded for
  the user, since holdout-2 is the program's final gate.
- The CP3 port chain rests on Crabel (1990) and D.1 D11, whose samples are unknown (a book not fetched from unauthorised hosts;
  a blog with no data sample): every CP3 member keeps its label.
- Independent check: Part 2 of reports/stage_e2a_declaration_audit.md (DeclarationAuditor-FableXHigh) checks every row
  against Task 2's quoted passages and this rule; a row it cannot confirm keeps its label (the lead's rulings file,
  reports/stage_e2a_source_window_rulings.md).
