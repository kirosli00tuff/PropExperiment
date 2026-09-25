# Stage E.2a Task 11: the lead's rulings on the source-window amendment audit

Audit: reports/stage_e2a_declaration_audit.md, Part 2 (DeclarationAuditor-FableXHigh, Claude Fable 5.1 at
xhigh), on reports/stage_e2a_source_window_amendment.md, sha256
9fe401c1c156ebba38162256bf151d9888dec00e42cd24026d348d039e64f13d. Verdict: all six removals CONFIRMED;
0 BLOCKING, 0 SHOULD FIX, 7 NOTE. The auditor's own classification of all 145 rows and its recomputation of
all 37 labels equal the amendment's; the six removed members' frozen entries cite no source Task 2 missed;
the 16 already-labelled members are untouched; all 32 files of reports/stage_e1_freeze.json match.

Rulings by the lead (Opus 5.5, xhigh), 2026-09-25, about 06:45 PDT. The audit was not re-run.

| # | Grade | Note (short) | Ruling |
|---|---|---|---|
| SW-A01 | NOTE | the brief's hash 95a040bb... predates a one-phrase header time fix; the audited version is 9fe401c1... | Recorded. 9fe401c1... is the amendment committed with this file. |
| SW-A02 | NOTE | K8-006's row omits its daily 1986-2015 sample | Recorded; no effect (both samples end before 2019-05-06). K8-oilcad-01's removal stands. |
| SW-A03 | NOTE | K7-025's window is read from table captions | Recorded; no effect (K7-rev2h-01 keeps its label on other sources). |
| SW-A04 | NOTE | the "no data sample" reading decides K3-mehedge-01 | **Upheld.** The frozen rule concerns a source's sample: "a member whose supporting source's sample overlaps its confirmation window was chosen partly on evidence from that window". R-K3-014 is a product and calendar document with no data sample (verified by the auditor on its text), so it cannot have supplied evidence from the confirmation window. K3-mehedge-01's other sources (K3-001, 2004-04-28..2012-12-31; K3-002, 2006-01-02..2016-06-30) end before 2019-05-06. The label is removed. |
| SW-A05 | NOTE | "port of D.1 family" tags are classifications, not sources | Recorded; the amendment treats them so. |
| SW-A06 | NOTE | three removed entries already stated their windows | Recorded; consistent with E.1's audit heuristic (about 20 of 64 entries had window text). |
| SW-A07 | NOTE | the auditor's first verbatim pass showed 69/71 from key handling; 71/71 stands | Recorded. |

## Result

Labels removed (source-overlap -> not source-overlap), confirmed: **K2-predrift-01, K3-ldnmom-01,
K3-mehedge-01, K4-ngpre-01, K8-flight-01, K8-oilcad-01.** The other 31 of the 37 fallback members, and the 16
members labelled in the frozen catalog, stay source-overlap. For a removed member, an edge found at its
cluster's confirmation read may be claimed or discussed under the frozen criteria without the extra
holdout condition that the source-overlap label imposes; a null statement is unaffected either way.
