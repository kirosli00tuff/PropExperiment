# Stage E.1 Task 4: the lead's rulings on the freeze audit

Audit: reports/stage_e1_freeze_audit.md, Part 1 (FreezeAuditor-FableXHigh, Fable 5.1 at xhigh). Verdict
**READY WITH FIXES**: 0 BLOCKING, 7 SHOULD FIX (FA-01 to FA-07), 9 NOTE (FA-08 to FA-16). The auditor's
independent recount from reports/stage_e0_catalog.json: 53 active members, 158 confirmation trials
(93 port + 65 new), projected cumulative N = 216, matching every figure the lead wrote.

Rulings by the lead (Opus 5.5, max), 2026-09-24, written at 18:15 PDT. The audit was not re-run. Every fix is
an exact-string edit, applied to the cluster file and to the assembled copy alike where a catalog entry
changes. No fix changes a member's rule, parameter, threshold or window.

| # | Grade | Finding (short) | Ruling | Where applied |
|---|---|---|---|---|
| FA-01 | SHOULD FIX | K8's trial-table row for K8-ml-01 unstruck | **Fixed** (U6): struck, 0 trials (E.0: 1) | reports/stage_e0_catalog_K8.md; reports/stage_e0_catalog.md section K8 |
| FA-02 | SHOULD FIX | K5-preauc-01 "Data needed" names platinum vehicles | **Fixed** (U2): "gold and silver ~~and platinum~~ [U2: platinum OUT]" | K5 file and assembled K5 |
| FA-03 | SHOULD FIX | K5-ovr-01 "Data needed: all four admitted vehicles" | **Fixed** (U2): "all ~~four~~ three [U2]" | K5 file and assembled K5 |
| FA-04 | SHOULD FIX | assembled copy's K5 to K8 sections lack E.0's R-10 ruling line | **Fixed** (copy fix, no decision: E.0 ruling R-10 carried): the four ruling lines inserted in the assembled copy at the cluster files' positions, so the two frozen copies agree | reports/stage_e0_catalog.md sections K5, K6, K7, K8 |
| FA-05 | SHOULD FIX | D13's "largest request about $2.7" is false | **Fixed** (factual correction, rule unchanged): bracketed note with E.0's quotes ($4.14, $3.41), the cap not raised, and the split handling | docs/STAGE_E_DESIGN.md D13 caps |
| FA-06 | SHOULD FIX | the criteria say E.1 records source windows; E.1 did not | **Option (b).** Recording 34-odd members' windows now would edit members beyond U1 to U9, which this stage may not do. Bracketed note added: not done; by the rule every member without a recorded window is source-overlap as frozen; whether windows may be recorded later (from the research logs, before the cluster's screening session reads any bar) is the user's decision. Members this may cover are listed below | docs/NULL_CRITERIA_E.md section 3 |
| FA-07 | SHOULD FIX | the lead's count note sat inside U2's decision text | **Fixed**: moved out of U2 as its own "Lead's count note" line | docs/DECISIONS.md |
| FA-08 | NOTE | F-1 right; pull_universe.py docstring says "30 traded exposures" | **Acted on**: docstring reads 31 (Task 5 commit). F-1 goes first in the return document | data/pull_universe.py |
| FA-09 | NOTE | re-summed cents: $57.28 and K5 $8.99 included coverage quotes; step 2 low end $164.71 | **Acted on**: D13 note reads $57.00, $102.95, $164.71-189.31, $267.66-292.26, K5 $8.95. The fresh Task 6 quote governs | docs/STAGE_E_DESIGN.md D13 |
| FA-10 | NOTE | seven cluster headers still count "+ 1 ML member" | Left: the banners supersede header totals "where they differ" | — |
| FA-11 | NOTE | descriptive platinum residuals in K5 | Left: bind nothing under the K5 banner | — |
| FA-12 | NOTE | changes-log JSON table omits four bookkeeping fields; K4 gas row mislabelled | **Acted on**: four rows added, gas row relabelled "R-06 carried" | reports/stage_e1_changes.md |
| FA-13 | NOTE | D12's strike covered still-valid sentences | **Acted on**: only the order sentence is superseded; the rest of the paragraph stands | docs/STAGE_E_DESIGN.md D12 |
| FA-14 | NOTE | K4-ovr-01 and K5-ovr-01 equivalent, not verbatim (R-24) | Recorded: **equivalent, not verbatim** (same signal, reference construction, cuts, entry, exit and 59-minute hold; they differ only in convention names and decision clocks). No member edit | — |
| FA-15 | NOTE | declared forward references | Recorded: docs/STAGE_E_ML_DESIGN.md (Task 9) and data/config.py's account registry (Task 5 commit) post-date this manifest and are not frozen by it; docs/DECISIONS.md forward-references reports/stage_e1_freeze.json | — |
| FA-16 | NOTE | F-5 and F-6 correctly left | Recorded | — |

## FA-06: the members the source-overlap fallback may cover

Active members already labelled source-overlap (16, reports/stage_e0_catalog.json): K1-cp2-01, K1-vxnband-01,
K1-vwap-01, K2-aucpre-01, K2-aucpost-01, K2-fomcpost-01, K4-apipre-01, K4-eiafade-01, K4-eiamom-01, K4-ovr-01,
K5-fomc-01, K5-ovr-01, K6-wasdepre-01, K7-expiry-01, K7-montrend-01, K8-wkndbtc-01.

Active members not labelled (37). Each is source-overlap under the frozen rule unless its entry records a
source window that does not overlap its confirmation window; the auditor's heuristic found window text in only
about 20 of the 64 entries, so roughly 34 active members fall under the fallback: K1-cp1-01, K1-cp3-01,
K2-cp1-01, K2-cp2-01, K2-cp3-01, K2-predrift-01, K2-monthend-01, K3-cp1-01, K3-cp2-01, K3-cp3-01, K3-ldnrev-01,
K3-ldnmom-01, K3-mehedge-01, K3-ecbfix-01, K3-tkypre-01, K3-tkypost-01, K4-cp1-01, K4-cp2-01, K4-cp3-01,
K4-ngpre-01, K5-cp1-01, K5-cp2-01, K5-cp3-01, K5-preauc-01, K5-pmfix-01, K6-cp1-01, K6-cp2-01, K6-cp3-01,
K6-crushgap-01, K6-limitcont-01, K6-wasdepost-01, K7-cp1-01, K7-cp2-01, K7-cp3-01, K7-rev2h-01, K8-flight-01,
K8-oilcad-01. The consequence: a null statement is unaffected; an edge on such a member cannot be claimed or
discussed for a final read without a registered holdout read. For the user.

## Other checks at the freeze

- R-24 (F-7, FA-14): equivalent rule texts, recorded above.
- F-2 is resolved by FA-05's note. F-3 is FA-06. F-1 stands as written (31 traded exposures after U2).
- No BLOCKING finding exists, so the freeze proceeds.
