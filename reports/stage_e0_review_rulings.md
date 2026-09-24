# Stage E.0 Task 8: the lead's rulings on the independent review

Review: reports/stage_e0_review.md (CatalogAuditor-FableXHigh, Fable 5.1 at xhigh; 02:27 to 06:18 PDT with the
02:35 to 06:10 usage-limit pause excluded). Verdict: **READY WITH FIXES**. Findings: 0 BLOCKING, 10 SHOULD FIX,
18 NOTE. Passage re-read: 46 rows, 42 MATCH, 0 MISREAD, 4 UNVERIFIABLE.

Rulings by the lead (Opus 5.5, max), 2026-09-24 06:19 to 06:22 PDT. Every catalog change is a bracketed
"[Lead ruling on the Task 6 review ...]" note inside the entry it changes, in the cluster catalog and in the
assembled copy alike (reports/stage_e0_catalog.md), so the original text stays visible. The review was not
re-run. No BLOCKING finding exists, so no member is excluded for an unresolved BLOCKING finding.

| # | Grade | Finding (short) | Ruling | Where applied |
|---|---|---|---|---|
| R-01 | SHOULD FIX | The ML member's Tier A membership was defined two ways (D5 "plus the ML member"; D15.10 "failing the screen puts it in Tier B") | **Fixed.** One reading, D15.10's: the ML member takes the same screen as every member, on its nested outer-fold estimate, and joins Tier A only if it passes | docs/STAGE_E_DESIGN.md D5 |
| R-02 | SHOULD FIX | CP1 described as "the family null on MES", but MES's confirmation tested the reversal-signed F3.3 statistics | **Fixed (wording; no rule change).** Corrected in D6 and in every cp1 entry: MES confirmed the reversal-signed form (s = -1) as null; the momentum form ported here, the literature's form, was negative on MES's mined window and is untested on MES's confirmation. The port is kept: it is chosen on the literature's form, not on MES's result | D6; K1-K7 cp1 entries |
| R-03 | SHOULD FIX | CP1 on livestock is the (b) form | **Fixed (wording).** D6 now states that on a product with no overnight session the trade date's first bar is the day open, so the same rule text yields the first-30-minute signal; HE and LE are kept (2 trials) | D6; K6-cp1-01 |
| R-04 | SHOULD FIX | "Source-overlap" applied to one member; at least twelve trials qualify | **Fixed.** Label and source window added to 15 entries (K1-vxnband, K1-vwap, K1-cp2 on the Nasdaq-100, K2-aucpre, K2-aucpost, K2-fomcpost, K4-ovr, K5-ovr, K5-fomc, K6-wasdepre, K7-expiry, K7-montrend, and, windows unrecorded, K4-eiamom, K4-eiafade, K4-apipre). New rule: E.1 records every member's source windows before hashing, and a member without a recorded window is treated as source-overlap | catalog entries; docs/NULL_CRITERIA_E.md section 3; catalog JSON |
| R-05 | SHOULD FIX | K3-ldnrev-01's 15-minute signal window is not the source's | **Fixed.** Signal = the 10-minute pre-fix move (close of the bar at T_L-1 minus close of the bar at T_L-11), as NBER w23327 footnote 9 measures it; the T_L+5 entry stays as a stated judgment | K3-ldnrev-01 |
| R-06 | SHOULD FIX | K4-ngrev-01's chain contradicts its own source ("efficiently impound") | **Excluded** (1 trial). A member whose own source argues against its central step spends a Holm trial on a mechanism the evidence already rejects | K4-ngrev-01; K4 trial table; catalog JSON (K4 20 trials) |
| R-07 | SHOULD FIX | K4-cp2-01's buffer table used vehicle ticks | **Fixed.** 4 ticks of the exposure's most active contract: crude 0.04 and natural gas 0.004 on every vehicle of the exposure | K4-cp2-01 |
| R-08 | SHOULD FIX | Locked-limit exits simulated as fills | **Fixed.** Harness rule in D9.7: when the bars show a lock on the exit's side, no exit (D9.7, forced flatten or any other) fills until a later bar trades through; the trip is flagged and the count is reported per member. E.2 builds it before any bar is read | docs/STAGE_E_DESIGN.md D9.7 |
| R-09 | SHOULD FIX | Six ML members left the vehicle to "the lead decides" after D2's figures | **Fixed.** Fallback orders declared now, by the D1 ADV order (data-free): K1 Nasdaq-100, Russell 2000, Dow; K3 EUR, JPY, AUD, GBP, CAD, NZD, CHF; K4 crude, natural gas, RBOB, ULSD; K6 ZC, ZS, ZL, ZM, ZW, LE, HE; K8 6C only; K7 MBT only; K5 gold, silver, copper (the 01:47 ruling, text aligned); K2 ZN, ZF (already declared). No admitted exposure means no ML member | K1, K3, K4, K5, K6, K8 ML entries |
| R-10 | SHOULD FIX | K6's D9.7 "release residual" text predates the 01:52 exemption | **Fixed.** Marked superseded in K6 C13 and K6-wasdepre-01 | K6 |

NOTEs, acknowledged (no ruling required by the prompt; actions where one was taken):
- R-11 K6-ml-01's first decision cannot trade: noted in the entry (D15.3's row rule drops it).
- R-12 D3 had no rule when no funnel cell passes: **added** (translated bar used, exposure flagged).
- R-13 The D1 input change was legitimate and changed no verdict: recorded.
- R-14 Registry and provenance hygiene: recorded in the progress entry (in-place edits, DOI and author errors).
- R-15 K2-aucpost-01's 5-minute lag rests on a passage the log did not quote: carried to E.1's review.
- R-16 K4-ovr-01's crude figure is the 2020-04-20 episode: covered by its source-overlap label (R-04).
- R-17 The lead's narrowings and exclusions are not result-driven: recorded.
- R-18, R-19 D5 and D2 to D4 argued adversarially: carried to the user's decisions before E.1.
- R-20 The ML protocol and entries: no leak found beyond R-01 and R-09; counting one trial judged defensible with the grid reported.
- R-21, R-22 Topstep and look-ahead items checked and clean.
- R-23 Ports against D6 and the MES modules: consistent after R-02, R-03, R-07.
- R-24 Duplicates across clusters: K4-ovr-01 and K5-ovr-01 must carry one rule text; E.1 checks it before hashing (noted in both entries).
- R-25 Nothing in the catalog required price data.
- R-26 NULL_CRITERIA_E's two new rules: kept; the user decides them (D7).
- R-27 K7 regime and window: covered by the D10 regime note.
- R-28 Small text items: carried to E.1's hashing pass.

Post-review catalog: **61 active members, 170 confirmation trials, projected cumulative N = 58 + 170 = 228**
(reports/stage_e0_catalog.json, patched 06:21 PDT; the assembled markdown carries a post-review header note).
The catalog and design remain DRAFTS for the user's review; nothing is frozen, hashed or registered.
